from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from river import drift

from detectors.core.unified import UnifiedDriftDetector
from detectors.meta.dynamic_weighted import DynamicWeightedVotingDetector
from detectors.meta.indicators import BaseIndicator
from .indicators import UQWarningIndicator


class KSWINFeatureIndicator(BaseIndicator):
    """KSWIN proxy over each feature dimension.

    KSWIN is a scalar detector, so this wrapper lazily creates one detector per
    flattened feature and raises a warning if any dimension shifts.
    """

    name = "KSWINFeatureIndicator"

    def __init__(
        self,
        *,
        alpha: float = 0.005,
        window_size: int = 100,
        stat_size: int = 30,
        seed: Optional[int] = 42,
    ) -> None:
        self.alpha = float(alpha)
        self.window_size = int(window_size)
        self.stat_size = int(stat_size)
        self.seed = seed
        self.detectors: List[drift.KSWIN] = []
        self.last_warning = False
        self.last_warning_dims: List[int] = []

    def _make_detector(self, offset: int = 0) -> drift.KSWIN:
        seed = None if self.seed is None else int(self.seed) + offset
        return drift.KSWIN(
            alpha=self.alpha,
            window_size=self.window_size,
            stat_size=self.stat_size,
            seed=seed,
        )

    def update(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        **kwargs,
    ) -> None:
        values = np.asarray(x, dtype=np.float64).ravel()
        while len(self.detectors) < len(values):
            self.detectors.append(self._make_detector(len(self.detectors)))

        warning_dims: List[int] = []
        for idx, value in enumerate(values):
            det = self.detectors[idx]
            det.update(float(value))
            if bool(det.drift_detected):
                warning_dims.append(idx)

        self.last_warning_dims = warning_dims
        self.last_warning = bool(warning_dims)

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        return self.last_warning, {
            "kswin_warning_dims": self.last_warning_dims,
            "kswin_n_warning_dims": len(self.last_warning_dims),
            "kswin_alpha": self.alpha,
            "kswin_window_size": self.window_size,
            "kswin_stat_size": self.stat_size,
        }

    def reset(self) -> None:
        self.detectors = [self._make_detector(i) for i in range(len(self.detectors))]
        self.last_warning = False
        self.last_warning_dims = []


class DynamicWeightedVotingECPFDetector(DynamicWeightedVotingDetector):
    """
    ECPF-specific DWM variant with explicit two-stage semantics.

    Stage 1 opens an ECPF warning buffer only after persistent UQ/KSWIN proxy
    warnings. Stage 2 confirms drift with a small weighted ensemble containing
    only ADWIN and HDDM-W over the error stream.
    """
    def __init__(
        self,
        config=None,
        uq_mode: str = "mi_like",
        selected_detectors: Optional[List[str]] = None,
        custom_indicators: Optional[List[BaseIndicator]] = None,
    ):
        uq_delta = config.ecpf_uq_delta if config is not None else 0.01
        uq_grace_period = config.ecpf_uq_grace_period if config is not None else 50
        uq_smoothing_alpha = config.ecpf_uq_smoothing_alpha if config is not None else 0.1
        kswin_alpha = config.ecpf_dwm_kswin_alpha if config is not None else 0.005
        kswin_window_size = config.ecpf_dwm_kswin_window_size if config is not None else 100
        kswin_stat_size = config.ecpf_dwm_kswin_stat_size if config is not None else 30
        kswin_seed = config.recurring_random_seed if config is not None else 42
        indicators = custom_indicators or [
            UQWarningIndicator(
                uq_mode=uq_mode,
                delta=uq_delta,
                grace_period=uq_grace_period,
                smoothing_alpha=uq_smoothing_alpha,
            ),
            KSWINFeatureIndicator(
                alpha=kswin_alpha,
                window_size=kswin_window_size,
                stat_size=kswin_stat_size,
                seed=kswin_seed,
            ),
        ]
        super().__init__(
            config=config,
            custom_indicators=indicators,
            selected_detectors=selected_detectors or ["adwin", "hddm_w"],
            proxy_policy="any",
        )

        atom_min_samples = config.atom_min_samples if config else 30
        atom_kwargs = config.atom_kwargs if config else {}
        confirmation_detectors = selected_detectors or ["adwin", "hddm_w"]
        self.drift_detector = UnifiedDriftDetector(
            min_samples=atom_min_samples,
            atom_kwargs=atom_kwargs,
            selected_detectors=confirmation_detectors,
        )
        self.weights = {name.lower(): 1.0 for name in confirmation_detectors}
        self.weight_history_log = {k: [] for k in self.weights}

        self.threshold = (
            config.ecpf_dwm_confirm_threshold
            if config is not None and hasattr(config, "ecpf_dwm_confirm_threshold")
            else 0.5
        )
        self.warning_persistence = (
            config.ecpf_dwm_warning_persistence
            if config is not None and hasattr(config, "ecpf_dwm_warning_persistence")
            else 2
        )
        self.warning_persistence_window = (
            config.ecpf_dwm_warning_persistence_window
            if config is not None and hasattr(config, "ecpf_dwm_warning_persistence_window")
            else 120
        )
        self._stage1_events: deque[int] = deque()

    def _persistent_stage1_warning(self, proxy_flags: List[bool], t: int) -> bool:
        if any(proxy_flags):
            self._stage1_events.append(int(t))
        while (
            self._stage1_events
            and t - self._stage1_events[0] > self.warning_persistence_window
        ):
            self._stage1_events.popleft()
        return len(self._stage1_events) >= self.warning_persistence

    def _reset_warning_state(self) -> None:
        self.proxy_warning_active = False
        self.first_proxy_warning_t = None
        self._stage1_events.clear()
        self._proxy_last_seen = [None for _ in self.indicators]

    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int,
        **kwargs,
    ) -> Tuple[bool, int, Dict[str, Any]]:
        proxy_flags, indicator_stats = self._update_indicators(
            x, y_true, y_pred, err, **kwargs
        )
        in_cooldown = self.cooldown_until is not None and t < self.cooldown_until
        persistent_warning = (
            False if in_cooldown else self._persistent_stage1_warning(proxy_flags, t)
        )
        proxy_warning_event = persistent_warning and not self.proxy_warning_active

        if proxy_warning_event:
            self.proxy_warning_active = True
            self.first_proxy_warning_t = t

        warning_age = None
        if self.proxy_warning_active and self.first_proxy_warning_t is not None:
            warning_age = t - self.first_proxy_warning_t
            if warning_age > self.confirmation_window:
                self._reset_warning_state()
                warning_age = None

        self._set_atom_sensitivity(self.proxy_warning_active)
        self.drift_detector.update(err)
        confirmation_votes = self.drift_detector.detect()
        self._update_weights(confirmation_votes, self.proxy_warning_active)

        score = self._score_votes(confirmation_votes)
        min_age_met = warning_age is not None and warning_age >= self.min_confirmation_age
        global_drift = (
            self.proxy_warning_active
            and min_age_met
            and score >= self.threshold
        )

        sub_detector_stats = {
            "proxy_indicators": {
                "any_warning": proxy_warning_event,
                "confirmed_warning": persistent_warning,
                "warning_active": self.proxy_warning_active,
                "warning_age": warning_age,
                "min_confirmation_age": self.min_confirmation_age,
                "cooldown_until": self.cooldown_until,
                "in_cooldown": in_cooldown,
                "raw_any_warning": any(proxy_flags),
                "policy": "persistent_any",
                "persistence_count": len(self._stage1_events),
                "persistence_required": self.warning_persistence,
                "persistence_window": self.warning_persistence_window,
                "first_warning_t": self.first_proxy_warning_t,
                "details": indicator_stats,
            },
            "ensemble_results": confirmation_votes,
            "dynamic_weights": self.weights.copy(),
            "meta_info": {
                "score_ratio": score,
                "confirm_threshold": self.threshold,
                "strategy_used": "persistent_uq_kswin_then_adwin_hddmw",
            },
        }

        if global_drift:
            print(f"\n{'='*50}")
            print(f"[Persistent ECPF-DWM] Drift confirmed at step t={t}!")
            print(f"Stage-2 score: {score:.4f} (threshold: {self.threshold:.4f})")
            print(f"{'='*50}\n")
            self._reset_warning_state()
            self.cooldown_until = t + self.cooldown_duration

        for k in self.weights:
            self.weight_history_log[k].append(self.weights[k])

        return global_drift, t, sub_detector_stats

    def reset(self) -> None:
        self._reset_warning_state()
        self.cooldown_until = None
        self.drift_detector.reset()
        for indicator in self.indicators:
            indicator.reset()
        self._reset_weights()

    def notify_drift(self, **kwargs) -> None:
        try:
            for k in self.weights:
                self.weights[k] = max(self.min_weight, min(self.max_weight, self.weights[k] * 0.97))
            self._reset_warning_state()
            self.drift_detector.reset()
            for indicator in self.indicators:
                indicator.reset()
        except Exception:
            pass
