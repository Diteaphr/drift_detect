import logging
from typing import Tuple, Dict, Any, List, Optional
import numpy as np

from .base import BaseMetaDetector
from detectors.core.unified import DEFAULT_ATOM_DETECTORS, UnifiedDriftDetector
from detectors.meta.indicators import BaseIndicator, KSDistributionIndicator


logger = logging.getLogger(__name__)


class DynamicWeightedVotingDetector(BaseMetaDetector):
    """
    基於多重代理訊號一致性的動態加權飄移偵測器 (DWM-Variant)。
    Proxy indicators are treated as a noisy gate, not ground truth.
    """

    def __init__(
        self,
        config=None,
        custom_indicators: Optional[List[BaseIndicator]] = None,
        selected_detectors: Optional[List[str]] = None,
        proxy_policy: Optional[str] = None,
    ):
        self.config = config
        
        ks_window_size = config.meta_ks_window_size if config else 100
        atom_min_samples = config.atom_min_samples if config else 30
        atom_kwargs = config.atom_kwargs if config else {}
        
        self.drift_detector = UnifiedDriftDetector(
            min_samples=atom_min_samples, 
            atom_kwargs=atom_kwargs,
            selected_detectors=selected_detectors
        )
        
        # 模組化第一步：將指標提取器抽象為 List，方便未來擴充 (Uncertainty, Disentanglement)
        if custom_indicators is not None:
            self.indicators = custom_indicators
        else:
            # 預設行為：只使用 KS Distribution Indicator
            self.indicators = [KSDistributionIndicator(window_size=ks_window_size)]

        
        # 定義權重調整參數。Proxy signals are noisy, so updates are intentionally mild.
        self.beta = config.meta_dwm_beta if config and hasattr(config, "meta_dwm_beta") else 0.8
        self.reward = config.meta_dwm_reward if config and hasattr(config, "meta_dwm_reward") else 1.05
        self.threshold = config.meta_dwm_threshold if config and hasattr(config, "meta_dwm_threshold") else 0.5
        self.min_weight = 0.1
        self.max_weight = 1.0   # 權重上限
        self.proxy_policy = proxy_policy or (
            config.meta_proxy_policy if config and hasattr(config, "meta_proxy_policy") else "any"
        )
        
        # 根據 selected_detectors 初始化 weights
        detector_names = selected_detectors if selected_detectors is not None else DEFAULT_ATOM_DETECTORS
        self.weights = {name.lower(): 1.0 for name in detector_names}
        self.weight_history_log = {k: [] for k in self.weights}

        # Gating Strategy 參數 (部分移除不用的)
        self.last_proxy_warning = False
        self.last_indicator_stats = {}
        self.first_proxy_warning_t = None
        self.proxy_warning_active = False
        self.confirmation_window = (
            config.ecpf_uq_warning_timeout
            if config and hasattr(config, "ecpf_uq_warning_timeout")
            else 1000
        )
        self.min_confirmation_age = (
            config.ecpf_warning_length
            if config and hasattr(config, "ecpf_warning_length")
            else 60
        )
        self.cooldown_duration = max(self.min_confirmation_age, 200)
        self.cooldown_until: Optional[int] = None
        self.proxy_join_window = self.confirmation_window
        self._proxy_last_seen: List[Optional[int]] = [None for _ in self.indicators]

    def _proxy_warning(self, flags: List[bool], t: Optional[int] = None) -> bool:
        if self.proxy_policy == "all":
            if not flags:
                return False
            if t is None:
                return all(flags)
            if len(self._proxy_last_seen) != len(flags):
                self._proxy_last_seen = [None for _ in flags]
            for idx, flag in enumerate(flags):
                if flag:
                    self._proxy_last_seen[idx] = t
            if any(ts is None for ts in self._proxy_last_seen):
                return False
            return (max(self._proxy_last_seen) - min(self._proxy_last_seen)) <= self.proxy_join_window
        return any(flags)

    def _update_indicators(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        **kwargs,
    ) -> Tuple[List[bool], Dict[str, Any]]:
        flags = []
        stats_by_indicator = {}
        for indicator in self.indicators:
            indicator.update(x, y_true, y_pred, err, **kwargs)
            flag, stats = indicator.detect()
            flags.append(bool(flag))
            name = getattr(indicator, "name", indicator.__class__.__name__)
            stats_by_indicator[name] = {"warning": bool(flag), "stats": stats}
        return flags, stats_by_indicator

    def _set_atom_sensitivity(self, proxy_warning: bool) -> None:
        profile = "dwm_sensitive" if proxy_warning else "dwm_normal"
        self.drift_detector.set_sensitivity(profile)

    def _update_weights(self, detector_votes: Dict[str, bool], proxy_warning: bool) -> None:
        for name in detector_votes:
            if name not in self.weights:
                continue
            # Proxy signals are not ground truth.  Until we have labels for
            # detector correctness, do not punish or reward atom detectors
            # based on UQ/ErrorTrend agreement.  Keep weights stable, with a
            # tiny recovery for any historical decay.
            self.weights[name] = min(self.weights[name] * 1.01, self.max_weight)

    def _score_votes(self, detector_votes: Dict[str, bool]) -> float:
        total_weight = sum(self.weights.values())
        drift_weight_sum = sum(
            self.weights[name] for name, is_voting in detector_votes.items()
            if is_voting and name in self.weights
        )
        return drift_weight_sum / total_weight if total_weight > 0 else 0.0

    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int, **kwargs
    ) -> Tuple[bool, int, Dict[str, Any]]:
        
        # 1. 取得 proxy indicator 狀態。這些訊號只做 noisy confirmation，不當作 ground truth。
        proxy_flags, all_indicator_stats = self._update_indicators(x, y_true, y_pred, err, **kwargs)
        in_cooldown = self.cooldown_until is not None and t < self.cooldown_until
        proxy_warning_event = False if in_cooldown else self._proxy_warning(proxy_flags, t=t)
            
        if proxy_warning_event and not self.proxy_warning_active:
            self.first_proxy_warning_t = t
            self.proxy_warning_active = True

        warning_age = None
        if self.proxy_warning_active and self.first_proxy_warning_t is not None:
            warning_age = t - self.first_proxy_warning_t
            if warning_age > self.confirmation_window:
                self.proxy_warning_active = False
                self.first_proxy_warning_t = None
                warning_age = None
        
        # 1.5 讓 Atom Detectors 動態調整敏感度 (備戰狀態 vs 和平狀態)
        self._set_atom_sensitivity(self.proxy_warning_active)

        # 2. 獲取 Atom Detectors 的投票結果
        self.drift_detector.update(err)
        raw_drifts = self.drift_detector.detect()
        
        # 3. 寬鬆版 DWM 權重調整 (做法 C)
        self._update_weights(raw_drifts, self.proxy_warning_active)

        # 4. 計算加權總分，決定最終是否觸發 Global Drift
        current_score = self._score_votes(raw_drifts)
        min_age_met = warning_age is not None and warning_age >= self.min_confirmation_age
        global_drift = (
            self.proxy_warning_active
            and min_age_met
            and current_score >= self.threshold
        )

        sub_detector_stats = {
            "proxy_indicators": {
                # Historical name used by the pipeline. This is the proxy
                # event that starts the ECPF warning buffer; atom votes can
                # confirm later while proxy_warning_active remains true.
                "any_warning": proxy_warning_event,
                "confirmed_warning": proxy_warning_event,
                "warning_active": self.proxy_warning_active,
                "warning_age": warning_age,
                "min_confirmation_age": self.min_confirmation_age,
                "cooldown_until": self.cooldown_until,
                "in_cooldown": in_cooldown,
                "raw_any_warning": any(proxy_flags),
                "policy": self.proxy_policy,
                "first_warning_t": self.first_proxy_warning_t,
                "details": all_indicator_stats
            },
            "ensemble_results": raw_drifts,
            "dynamic_weights": self.weights.copy(),
            "meta_info": {
                "score_ratio": current_score,
                "strategy_used": "dynamic_weighted_dwm"
            }
        }
        
        # 5. Global Drift 發生後，印出當下的權重狀態並重置所有權重
        if global_drift:
            logger.info(
                "Dynamic DWM global drift detected at t=%d; score_ratio=%.4f "
                "(threshold=%.4f); weights=%s",
                t,
                current_score,
                self.threshold,
                {name: round(weight, 4) for name, weight in self.weights.items()},
            )
            self.proxy_warning_active = False
            self.first_proxy_warning_t = None
            self.cooldown_until = t + self.cooldown_duration
            self._proxy_last_seen = [None for _ in self.indicators]
            self._reset_weights()

        # 紀錄當下時間點的權重
        for k in self.weights:
            self.weight_history_log[k].append(self.weights[k])

        return global_drift, t, sub_detector_stats

    def _reset_weights(self):
        for k in self.weights:
            self.weights[k] = self.max_weight

    def reset(self) -> None:
        self.first_proxy_warning_t = None
        self.proxy_warning_active = False
        self.cooldown_until = None
        self._proxy_last_seen = [None for _ in self.indicators]
        self.drift_detector.reset()
        for idx in self.indicators:
            idx.reset()
        self._reset_weights()
        # 移除 `self.weight_history_log = ...` 避免在偵測到 drift 重置時，把前面紀錄的歷史圖表洗掉

    def notify_drift(self, **kwargs) -> None:
        """
        Called by the pipeline when a drift has been confirmed.

        Keep the learned DWM weights, but clear transient detector/indicator
        state.  Without this, atom detectors that keep an internal drift flag
        can fire again on the next sample and make ECPF create many
        one-sample warning buffers.
        """
        try:
            for k in self.weights:
                self.weights[k] = max(self.min_weight, min(self.max_weight, self.weights[k] * 0.97))
            self.first_proxy_warning_t = None
            self.proxy_warning_active = False
            self._proxy_last_seen = [None for _ in self.indicators]
            self.drift_detector.reset()
            for indicator in self.indicators:
                indicator.reset()
        except Exception:
            # fail-safe: do nothing
            pass

    def plot_weight_history(self, title: str = "Atom Detectors Weight History", 
                            true_drift_intervals: List[Tuple[int, int]] = None, 
                            save_path: str = None):
        """
        繪製 0 - n 步驟內各 Atom Detector 權重變化的歷史折線圖，
        並可用紅色區塊標示真實 Drift 的發生區間 (true_drift_intervals=[(start, end), ...])。
        這裡改用 Plotly 繪製，支援互動且更清楚檢視重疊的線條。
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            print("Plotly is not installed. Please run: pip install plotly")
            return

        if not hasattr(self, 'weight_history_log') or not list(self.weight_history_log.values())[0]:
            print("No weight history to plot.")
            return

        fig = go.Figure()
        steps = list(range(len(list(self.weight_history_log.values())[0])))
        
        # 繪製六個 Atom Detector 的權重折線
        for det_name, history in self.weight_history_log.items():
            fig.add_trace(go.Scatter(
                x=steps, 
                y=history, 
                mode='lines', 
                name=det_name, 
                opacity=0.8,
                line=dict(width=2)
            ))
            
        # 標示真實 Drift 的區間
        if true_drift_intervals:
            for i, (start, end) in enumerate(true_drift_intervals):
                fig.add_vrect(
                    x0=start, x1=end, 
                    fillcolor="red", 
                    opacity=0.2, 
                    layer="below", 
                    line_width=0,
                )
                
        fig.update_layout(
            title=title,
            xaxis_title="Time Step (t)",
            yaxis_title="Weight",
            yaxis=dict(range=[-0.05, 1.1]),
            hovermode="x unified",
            template="plotly_white"
        )
        
        if save_path:
            # 如果存成 HTML，保有互動性
            if not save_path.endswith('.html'):
                save_path = save_path.rsplit('.', 1)[0] + '.html'
            fig.write_html(save_path)
            print(f"✅ Weight history plot saved as interactive HTML to {save_path}")
        else:
            fig.show()
