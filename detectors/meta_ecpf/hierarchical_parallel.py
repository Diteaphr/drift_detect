from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from detectors.meta.indicators import BaseIndicator, ErrorRateTrendIndicator
from .dynamic_weighted import DynamicWeightedVotingECPFDetector
from .indicators import UQWarningIndicator


class HierarchicalParallelECPFDetector(DynamicWeightedVotingECPFDetector):
    """
    Experimental ECPF detector that keeps the original DWM implementation
    available while testing a hierarchical-parallel state machine:

    1. UQ + ErrorTrend open the warning buffer.
    2. Atom detectors continue watching the error stream while warning is active.
    3. Gradual-path atom votes confirm drift.
    4. ECPF compares experts on the collected warning buffer.
    5. Drift handling resets transient state and enters cooldown.
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
        indicators = custom_indicators or [
            UQWarningIndicator(
                uq_mode=uq_mode,
                delta=uq_delta,
                grace_period=uq_grace_period,
                smoothing_alpha=uq_smoothing_alpha,
            ),
            ErrorRateTrendIndicator(short_window=50, long_window=250, threshold=0.05),
        ]
        super().__init__(
            config=config,
            uq_mode=uq_mode,
            selected_detectors=selected_detectors,
            custom_indicators=indicators,
        )
        self.fast_path_detectors = {"adwin", "ddm"}
        self.gradual_path_detectors = {"hddm_a", "page_hinkley"}
        self.gradual_confirm_threshold = 0.5

    def _path_score(self, detector_votes: Dict[str, bool], detector_names: set) -> float:
        names = [name for name in detector_names if name in self.weights]
        total_weight = sum(self.weights[name] for name in names)
        if total_weight <= 0:
            return 0.0
        drift_weight = sum(
            self.weights[name]
            for name in names
            if detector_votes.get(name, False)
        )
        return drift_weight / total_weight

    def _reset_warning_state(self) -> None:
        self.proxy_warning_active = False
        self.first_proxy_warning_t = None
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
        proxy_warning_event = bool(proxy_flags) and all(proxy_flags) and not in_cooldown
        if proxy_warning_event and not self.proxy_warning_active:
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
        atom_votes = self.drift_detector.detect()
        self._update_weights(atom_votes, self.proxy_warning_active)

        all_score = self._score_votes(atom_votes)
        fast_score = self._path_score(atom_votes, self.fast_path_detectors)
        gradual_score = self._path_score(atom_votes, self.gradual_path_detectors)
        min_age_met = warning_age is not None and warning_age >= self.min_confirmation_age
        global_drift = (
            self.proxy_warning_active
            and min_age_met
            and gradual_score >= self.gradual_confirm_threshold
        )

        sub_detector_stats = {
            "proxy_indicators": {
                "any_warning": proxy_warning_event,
                "confirmed_warning": proxy_warning_event,
                "warning_active": self.proxy_warning_active,
                "warning_age": warning_age,
                "min_confirmation_age": self.min_confirmation_age,
                "cooldown_until": self.cooldown_until,
                "in_cooldown": in_cooldown,
                "raw_any_warning": any(proxy_flags),
                "policy": "all",
                "first_warning_t": self.first_proxy_warning_t,
                "details": indicator_stats,
            },
            "ensemble_results": atom_votes,
            "dynamic_weights": self.weights.copy(),
            "meta_info": {
                "score_ratio": all_score,
                "fast_path_score": fast_score,
                "gradual_path_score": gradual_score,
                "gradual_confirm_threshold": self.gradual_confirm_threshold,
                "strategy_used": "hierarchical_parallel_ecpf_dwm",
            },
        }

        if global_drift:
            print(f"\n{'='*50}")
            print(f"[Hierarchical ECPF-DWM] Drift Confirmed at step t={t}!")
            print(f"Fast path score: {fast_score:.4f}")
            print(
                f"Gradual path score: {gradual_score:.4f} "
                f"(Threshold: {self.gradual_confirm_threshold})"
            )
            print(f"{'='*50}\n")
            self._reset_warning_state()
            self.cooldown_until = t + self.cooldown_duration

        for k in self.weights:
            self.weight_history_log[k].append(self.weights[k])

        return global_drift, t, sub_detector_stats
