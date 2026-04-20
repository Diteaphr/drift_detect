from typing import Tuple, Dict, Any, List
import numpy as np

from .base import BaseMetaDetector
from detectors.unified import UnifiedDriftDetector
from detectors.meta.indicators import BaseIndicator, KSDistributionIndicator

class DynamicWeightedVotingDetector(BaseMetaDetector):
    """
    基於多重代理訊號一致性的動態加權飄移偵測器 (DWM-Variant)。
    使用 Unsupervised Indicators 的結果作為「代理標準答案」來懲罰或獎勵 Atom Detectors。
    """

    def __init__(self, config=None, custom_indicators: List[BaseIndicator] = None):
        self.config = config
        
        ks_window_size = config.meta_ks_window_size if config else 100
        atom_min_samples = config.atom_min_samples if config else 30
        atom_kwargs = config.atom_kwargs if config else {}
        
        self.drift_detector = UnifiedDriftDetector(min_samples=atom_min_samples, atom_kwargs=atom_kwargs)
        
        # 模組化第一步：將指標提取器抽象為 List，方便未來擴充 (Uncertainty, Disentanglement)
        if custom_indicators is not None:
            self.indicators = custom_indicators
        else:
            # 預設行為：只使用 KS Distribution Indicator
            self.indicators = [KSDistributionIndicator(window_size=ks_window_size)]

        
        # 定義權重調整參數
        self.beta = 0.6         # 懲罰降權係數 (預測與 KS Test 不合)
        self.reward = 1.1      # 獎勵升權係數 (預測與 KS Test 一致且正確報警)
        self.threshold = 0.25    # 觸發 Global Drift 的加權門檻 (調降至 0.3 讓被冷落的演算法也能發揮作用)
        self.min_weight = 0.1
        self.max_weight = 1.0   # 權重上限
        
        self.weights = {
            "hddm_w": 1.0, "eddm": 1.0, "ddm": 1.0, 
            "hddm_a": 1.0, "page_hinkley": 1.0, "adwin": 1.0
        }
        self.weight_history_log = {k: [] for k in self.weights}

        # Gating Strategy 參數
        from collections import deque
        self.stride = 50
        self.err_window = deque(maxlen=100)
        self.error_buffer = []  # 用來暫存要餵給 Atom Detectors 的 error
        self.last_proxy_warning = False
        self.last_indicator_stats = {}

    def _map_detector_names(self, drift_details: Dict[str, bool]) -> Dict[str, bool]:
        mapping = {
            "HDDM-W": "hddm_w", "EDDM": "eddm", "DDM": "ddm",
            "HDDM-A": "hddm_a", "PageHinkley": "page_hinkley", "ADWIN": "adwin"
        }
        return {mapping.get(k, k.lower()): v for k, v in drift_details.items()}

    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int
    ) -> Tuple[bool, int, Dict[str, Any]]:
        
        # 1. 取得「代理標準答案」(收集所有 Indicators 的狀態：KS, Uncertainty, Disentanglement 等)
        any_proxy_warning = False
        all_indicator_stats = {}
        for idx, indicator in enumerate(self.indicators):
            indicator.update(x, y_true, y_pred, err)
            flag, stats = indicator.detect()
            if flag:
                any_proxy_warning = True
            all_indicator_stats[f"indicator_{idx}"] = {"warning": flag, "stats": stats}
        
        # 1.5 讓 Atom Detectors 動態調整敏感度 (備戰狀態 vs 和平狀態)
        if any_proxy_warning:
            # KS響了，逼迫所有人戴上放大鏡
            # 刻意調高 DDM 的容忍度 (從 2.0 提升到 3.5)，因為模型表現太好導致它太容易大驚小怪
            self.drift_detector.ddm.drift_level = 4.5
            self.drift_detector.page_hinkley.threshold = 5.0
            self.drift_detector.adwin.delta = 0.8
        else:
            # 恢復理智 (預設值)
            self.drift_detector.ddm.drift_level = 5.5 # 和平時更嚴苛
            self.drift_detector.page_hinkley.threshold = 15.0
            self.drift_detector.adwin.delta = 0.01

        # 2. 獲取 Atom Detectors 的投票結果
        self.drift_detector.update(err)
        raw_drifts = self.drift_detector.detect()
        mapped_drifts = self._map_detector_names(raw_drifts)
        
        # 3. 寬鬆版 DWM 權重調整 (做法 C)
        # 只有在「有人舉手」的敏感時刻才檢討權重，平時不隨便扣分
        if any(mapped_drifts.values()): 
            for name, predicted_drift in mapped_drifts.items():
                if predicted_drift == True:
                    if any_proxy_warning == False:
                        # 亂報警 (預測有，但訊號沒變)：懲罰
                        self.weights[name] = max(self.weights[name] * self.beta, self.min_weight)
                    else:
                        # 準確報警 (預測有，且任一代理訊號也變了)：獎勵
                        self.weights[name] = min(self.weights[name] * self.reward, self.max_weight)
                else:
                    # 當下沒舉手的人：
                    if any_proxy_warning == True:
                        # 漏報：稍微扣點分警告就好 (懲罰係數 0.9)
                        self.weights[name] = max(self.weights[name] * 0.9, self.min_weight)
                    else:
                        # 安全過關：緩慢恢復
                        self.weights[name] = min(self.weights[name] * 1.05, self.max_weight)
        else:
            # 大家都沒舉手，權重緩慢回血
            for name in self.weights:
                self.weights[name] = min(self.weights[name] * 1.01, self.max_weight)

        # 4. 計算加權總分，決定最終是否觸發 Global Drift
        total_weight = sum(self.weights.values())
        drift_weight_sum = sum(self.weights[name] for name, is_voting in mapped_drifts.items() if is_voting)
        
        current_score = drift_weight_sum / total_weight if total_weight > 0 else 0.0
        global_drift = current_score >= self.threshold

        sub_detector_stats = {
            "proxy_indicators": {
                "any_warning": any_proxy_warning,
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
            print(f"\n{'='*50}")
            print(f"🚨 [Dynamic DWM] Global Drift Detected at step t={t}!")
            print("📊 Current Atom Detector Weights Before Reset:")
            for det_name, weight in self.weights.items():
                print(f"   - {det_name:<15}: {weight:.4f}")
            print(f"📈 Score Ratio: {current_score:.4f} (Threshold: {self.threshold})")
            print(f"{'='*50}\n")
            self._reset_weights()

        # 紀錄當下時間點的權重
        for k in self.weights:
            self.weight_history_log[k].append(self.weights[k])

        return global_drift, t, sub_detector_stats

    def _reset_weights(self):
        for k in self.weights:
            self.weights[k] = self.max_weight

    def reset(self) -> None:
        self.drift_detector.reset()
        for idx in self.indicators:
            idx.reset()
        self._reset_weights()
        # 移除 `self.weight_history_log = ...` 避免在偵測到 drift 重置時，把前面紀錄的歷史圖表洗掉

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