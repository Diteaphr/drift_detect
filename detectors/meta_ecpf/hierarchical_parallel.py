from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from detectors.meta.indicators import BaseIndicator, ErrorRateTrendIndicator
from .dynamic_weighted import DynamicWeightedVotingECPFDetector
from .indicators import UQWarningIndicator


class ZeroOneLossValidator:
    """Cheap validation layer over pre-warning vs post-warning 0/1 losses."""

    def __init__(
        self,
        hist_size: int = 250,
        new_size: int = 60,
        gap_threshold: float = 0.02,
        min_new_size: int = 30,
    ) -> None:
        self.hist_errors: deque[float] = deque(maxlen=int(hist_size))
        self.new_errors: deque[float] = deque(maxlen=int(new_size))
        self.gap_threshold = float(gap_threshold)
        self.min_new_size = int(min_new_size)
        self.active = False

    def update_baseline(self, err: float) -> None:
        if not self.active:
            self.hist_errors.append(float(err))

    def start_validation(self) -> None:
        self.active = True
        self.new_errors.clear()

    def update_validation(self, err: float) -> None:
        if self.active:
            self.new_errors.append(float(err))

    def validate(self) -> Tuple[bool, Dict[str, Any]]:
        if len(self.hist_errors) == 0 or len(self.new_errors) < self.min_new_size:
            return False, {
                "validation_gap": None,
                "hist_error": None,
                "new_error": None,
                "validation_threshold": self.gap_threshold,
                "validation_hist_n": len(self.hist_errors),
                "validation_new_n": len(self.new_errors),
            }

        hist_error = float(np.mean(self.hist_errors))
        new_error = float(np.mean(self.new_errors))
        gap = new_error - hist_error
        return gap > self.gap_threshold, {
            "validation_gap": gap,
            "hist_error": hist_error,
            "new_error": new_error,
            "validation_threshold": self.gap_threshold,
            "validation_hist_n": len(self.hist_errors),
            "validation_new_n": len(self.new_errors),
        }

    def reset(self) -> None:
        self.active = False
        self.new_errors.clear()


class HierarchicalParallelECPFDetector(DynamicWeightedVotingECPFDetector):
    """
    Experimental hierarchical multiple-hypothesis ECPF trigger.

    1. Optional proxy signals or low-cost atom detectors open the warning buffer.
    2. The detection layer only proposes candidate drift.
    3. The validation layer compares recent 0/1 loss against baseline loss.
    4. ECPF handles drift only after validation passes.
    """

    def __init__(
        self,
        config=None,
        uq_mode: str = "mi_like",
        selected_detectors: Optional[List[str]] = None,
        custom_indicators: Optional[List[BaseIndicator]] = None,
    ):
        if selected_detectors is None:
            selected_detectors = ["hddm_w"]
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
        self.proxy_policy = (
            getattr(config, "ecpf_hier_proxy_policy", "any")
            if config is not None
            else "any"
        )
        self.fast_path_detectors = {"adwin", "ddm"}
        self.gradual_path_detectors = {"hddm_w", "hddm_a", "page_hinkley", "eddm"}
        self.fast_candidate_threshold = float(
            getattr(config, "ecpf_hier_fast_candidate_threshold", 0.5)
            if config is not None
            else 0.5
        )
        self.gradual_candidate_threshold = float(
            getattr(config, "ecpf_hier_gradual_candidate_threshold", 0.5)
            if config is not None
            else 0.5
        )
        self.validator = ZeroOneLossValidator(
            hist_size=(
                getattr(config, "ecpf_hier_validation_hist_size", 250)
                if config is not None
                else 250
            ),
            new_size=(
                getattr(config, "ecpf_hier_validation_new_size", 60)
                if config is not None
                else 60
            ),
            gap_threshold=(
                getattr(config, "ecpf_hier_validation_gap_threshold", 0.02)
                if config is not None
                else 0.02
            ),
            min_new_size=(
                getattr(config, "ecpf_hier_validation_min_new_size", 30)
                if config is not None
                else 30
            ),
        )
        self._candidate_seen = False
        self._candidate_source: Optional[str] = None
        self._candidate_t: Optional[int] = None

    def _path_score(self, detector_votes: Dict[str, bool], detector_names: set) -> float:
        names = [name for name in detector_names if name in detector_votes]
        if not names:
            return 0.0
        return sum(bool(detector_votes.get(name, False)) for name in names) / len(names)

    def _candidate_source_from_scores(
        self,
        atom_votes: Dict[str, bool],
        fast_score: float,
        gradual_score: float,
    ) -> Tuple[bool, Optional[str]]:
        sources = []
        if fast_score >= self.fast_candidate_threshold:
            sources.append("fast_path")
        if gradual_score >= self.gradual_candidate_threshold:
            sources.append("gradual_path")
        if not sources:
            active_atoms = [name for name, vote in atom_votes.items() if vote]
            if active_atoms:
                sources.append(",".join(active_atoms))
        return bool(sources), "+".join(sources) if sources else None

    def _zero_one_loss(self, y_true: float, y_pred: float, err: float) -> float:
        try:
            return float(int(round(float(y_pred))) != int(round(float(y_true))))
        except Exception:
            return 1.0 if float(err) > 0.5 else 0.0

    def _reset_warning_state(self) -> None:
        self.proxy_warning_active = False
        self.first_proxy_warning_t = None
        self._proxy_last_seen = [None for _ in self.indicators]
        self._candidate_seen = False
        self._candidate_source = None
        self._candidate_t = None

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
        err01 = self._zero_one_loss(y_true, y_pred, err)
        in_cooldown = self.cooldown_until is not None and t < self.cooldown_until

        self._set_atom_sensitivity(self.proxy_warning_active)
        self.drift_detector.update(err01)
        atom_votes = self.drift_detector.detect()

        all_score = self._path_score(atom_votes, set(atom_votes))
        fast_score = self._path_score(atom_votes, self.fast_path_detectors)
        gradual_score = self._path_score(atom_votes, self.gradual_path_detectors)
        candidate_drift, current_candidate_source = self._candidate_source_from_scores(
            atom_votes, fast_score, gradual_score
        )
        if candidate_drift and not in_cooldown:
            self._candidate_seen = True
            self._candidate_source = current_candidate_source
            self._candidate_t = t

        raw_proxy_warning = self._proxy_warning(proxy_flags, t=t)
        proxy_warning_event = raw_proxy_warning and not in_cooldown
        warning_event = (
            not self.proxy_warning_active
            and not in_cooldown
            and (proxy_warning_event or candidate_drift)
        )
        if warning_event:
            self.proxy_warning_active = True
            self.first_proxy_warning_t = t
            if candidate_drift and self._candidate_t is None:
                self._candidate_seen = True
                self._candidate_source = current_candidate_source
                self._candidate_t = t
            self.validator.start_validation()

        warning_age = None
        if self.proxy_warning_active and self.first_proxy_warning_t is not None:
            warning_age = t - self.first_proxy_warning_t
            if warning_age > self.confirmation_window:
                self._reset_warning_state()
                self.validator.reset()
                warning_age = None

        if self.proxy_warning_active:
            self.validator.update_validation(err01)
        else:
            self.validator.update_baseline(err01)

        validation_passed = False
        validation_stats: Dict[str, Any] = {
            "validation_gap": None,
            "hist_error": None,
            "new_error": None,
            "validation_threshold": self.validator.gap_threshold,
            "validation_hist_n": len(self.validator.hist_errors),
            "validation_new_n": len(self.validator.new_errors),
        }
        min_age_met = warning_age is not None and warning_age >= self.min_confirmation_age
        if self.proxy_warning_active and min_age_met and self._candidate_seen:
            validation_passed, validation_stats = self.validator.validate()

        global_drift = (
            self.proxy_warning_active
            and min_age_met
            and self._candidate_seen
            and validation_passed
        )

        sub_detector_stats = {
            "proxy_indicators": {
                "any_warning": warning_event,
                "confirmed_warning": warning_event,
                "warning_active": self.proxy_warning_active,
                "warning_age": warning_age,
                "min_confirmation_age": self.min_confirmation_age,
                "cooldown_until": self.cooldown_until,
                "in_cooldown": in_cooldown,
                "raw_any_warning": any(proxy_flags),
                "raw_proxy_warning": raw_proxy_warning,
                "policy": self.proxy_policy,
                "first_warning_t": self.first_proxy_warning_t,
                "details": indicator_stats,
            },
            "ensemble_results": atom_votes,
            "dynamic_weights": self.weights.copy(),
            "meta_info": {
                "score_ratio": all_score,
                "candidate_drift": candidate_drift,
                "candidate_seen": self._candidate_seen,
                "candidate_source": current_candidate_source,
                "active_candidate_source": self._candidate_source,
                "candidate_t": self._candidate_t,
                "fast_path_score": fast_score,
                "gradual_path_score": gradual_score,
                "fast_candidate_threshold": self.fast_candidate_threshold,
                "gradual_candidate_threshold": self.gradual_candidate_threshold,
                "validation_passed": validation_passed,
                **validation_stats,
                "warning_start_t": self.first_proxy_warning_t,
                "confirmation_t": t if global_drift else None,
                "strategy_used": "hierarchical_hypothesis_ecpf",
            },
        }

        if global_drift:
            print(f"\n{'='*50}")
            print(f"[Hierarchical Hypothesis ECPF] Drift confirmed at step t={t}!")
            print(f"Candidate source: {self._candidate_source}")
            print(
                f"Validation gap: {validation_stats.get('validation_gap')} "
                f"(threshold: {self.validator.gap_threshold:.4f})"
            )
            print(f"{'='*50}\n")
            self._reset_warning_state()
            self.validator.reset()
            self.drift_detector.reset()
            self.cooldown_until = t + self.cooldown_duration

        for k in self.weights:
            self.weight_history_log[k].append(self.weights[k])

        return global_drift, t, sub_detector_stats

    def reset(self) -> None:
        super().reset()
        self.validator.reset()
        self._candidate_seen = False
        self._candidate_source = None
        self._candidate_t = None

    def notify_drift(self, **kwargs) -> None:
        super().notify_drift(**kwargs)
        self.validator.reset()
        self._candidate_seen = False
        self._candidate_source = None
        self._candidate_t = None
