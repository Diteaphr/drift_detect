from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

import numpy as np

from src.uq_extractor import UQExtractor


class ECPFGDDMDetector:
    """GDDM-style group drift detector for the ECPF warning controller.

    The original GDDM consumes a vector of per-stream error rates and compares
    the recent vector distribution with a historical reference distribution
    using rank-based Mann-Whitney style statistics.  This implementation keeps
    that shape for ECPF: per-tree prequential error rates are the primary
    streams, and ensemble uncertainty scalars can be appended as auxiliary
    streams when a Hoeffding Forest probability matrix is available.
    """

    def __init__(self, config=None, uq_mode: str = "mi_like") -> None:
        self.reference_window = int(
            getattr(config, "ecpf_gddm_reference_window", 160)
        )
        self.test_window = int(getattr(config, "ecpf_gddm_test_window", 60))
        self.min_updates = int(getattr(config, "ecpf_gddm_min_updates", 500))
        self.error_rate_window = int(
            getattr(config, "ecpf_gddm_error_rate_window", 30)
        )
        self.warning_alpha = float(getattr(config, "ecpf_gddm_warning_alpha", 0.10))
        self.drift_alpha = float(getattr(config, "ecpf_gddm_drift_alpha", 0.01))
        self.n_permutations = int(getattr(config, "ecpf_gddm_n_permutations", 49))
        self.threshold_update_interval = int(
            getattr(config, "ecpf_gddm_threshold_update_interval", 10)
        )
        self.warning_persistence = int(
            getattr(config, "ecpf_gddm_warning_persistence", 2)
        )
        self.gradual_persistence = int(
            getattr(config, "ecpf_gddm_gradual_persistence", 3)
        )
        self.min_confirmation_age = int(
            getattr(config, "ecpf_gddm_min_confirmation_age", 10)
        )
        self.sudden_jump_ratio = float(
            getattr(config, "ecpf_gddm_sudden_jump_ratio", 1.35)
        )
        self.include_uq = bool(getattr(config, "ecpf_gddm_include_uq", True))
        self.cooldown_duration = int(
            getattr(config, "ecpf_gddm_cooldown", max(self.test_window, 120))
        )
        seed = getattr(config, "recurring_random_seed", 42)
        self.rng = np.random.default_rng(seed)
        self.uq_mode = uq_mode
        self._uq_extractors = {
            "mi_like": UQExtractor("mi_like"),
            "vote_disagreement": UQExtractor("vote_disagreement"),
            "predictive_entropy": UQExtractor("predictive_entropy"),
            "variance_eu": UQExtractor("variance_eu"),
        }
        if uq_mode not in self._uq_extractors:
            self._uq_extractors[uq_mode] = UQExtractor("mi_like")

        self.signal_history: Deque[np.ndarray] = deque(
            maxlen=self.reference_window + self.test_window
        )
        self._tree_error_windows: List[Deque[float]] = []
        self._last_threshold_key: Optional[Tuple[int, int]] = None
        self._last_warning_threshold: Optional[float] = None
        self._last_drift_threshold: Optional[float] = None
        self._last_u: Optional[float] = None
        self._warning_active = False
        self._first_warning_t: Optional[int] = None
        self._warning_run = 0
        self._above_drift_run = 0
        self._cooldown_until: Optional[int] = None
        self.n_updates = 0
        self.n_warnings = 0
        self.n_drifts = 0

    def reset(self) -> None:
        self.signal_history.clear()
        self._tree_error_windows = []
        self._last_threshold_key = None
        self._last_warning_threshold = None
        self._last_drift_threshold = None
        self._last_u = None
        self._warning_active = False
        self._first_warning_t = None
        self._warning_run = 0
        self._above_drift_run = 0
        self._cooldown_until = None
        self.n_updates = 0

    def notify_drift(self, **kwargs) -> None:
        cooldown_until = self._cooldown_until
        self.reset()
        self._cooldown_until = cooldown_until

    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int,
        **kwargs,
    ) -> Tuple[bool, int, Dict[str, Any]]:
        proba_matrix = kwargs.get("proba_matrix")
        signal = self._build_signal_vector(proba_matrix, y_true, y_pred, err)
        if self.signal_history and self.signal_history[-1].shape[0] != signal.shape[0]:
            self.signal_history.clear()
            self._last_threshold_key = None
            self._last_warning_threshold = None
            self._last_drift_threshold = None
            self._last_u = None
        self.signal_history.append(signal)
        self.n_updates += 1

        in_cooldown = self._cooldown_until is not None and t < self._cooldown_until
        ready = len(self.signal_history) >= self.reference_window + self.test_window
        u_stat = 0.0
        warning_threshold = None
        drift_threshold = None
        is_warning_level = False
        is_drift_level = False
        delta_u = 0.0

        past_initialization = self.n_updates >= self.min_updates

        if ready:
            reference, recent = self._current_windows()
            u_stat = self._group_statistic(reference, recent)
            warning_threshold, drift_threshold = self._thresholds(reference, recent)
            if past_initialization and warning_threshold is not None:
                is_warning_level = u_stat > warning_threshold
            if past_initialization and drift_threshold is not None:
                is_drift_level = u_stat > drift_threshold
            if self._last_u is not None:
                delta_u = u_stat - self._last_u

        if in_cooldown:
            is_warning_level = False
            is_drift_level = False

        self._warning_run = self._warning_run + 1 if is_warning_level else 0
        self._above_drift_run = self._above_drift_run + 1 if is_drift_level else 0

        warning_event = (
            not self._warning_active
            and self._warning_run >= self.warning_persistence
        )
        if warning_event:
            self._warning_active = True
            self._first_warning_t = int(t)
            self.n_warnings += 1

        sudden_jump = False
        if is_drift_level and drift_threshold is not None and self._last_u is not None:
            previous = max(self._last_u or 0.0, drift_threshold * 0.25, 1e-12)
            sudden_jump = (u_stat / previous) >= self.sudden_jump_ratio or delta_u > drift_threshold

        gradual_confirm = (
            self._warning_active
            and self._above_drift_run >= self.gradual_persistence
        )
        sudden_confirm = is_drift_level and sudden_jump
        drift_confirmed = bool(sudden_confirm or gradual_confirm)
        drift_type = "sudden" if sudden_confirm else "gradual" if gradual_confirm else "unknown"

        warning_age = None
        if self._warning_active and self._first_warning_t is not None:
            warning_age = int(t) - self._first_warning_t

        min_age_met = (
            warning_age is not None
            and warning_age >= self.min_confirmation_age
        )
        sudden_confirm = bool(sudden_confirm and min_age_met)
        gradual_confirm = bool(gradual_confirm and min_age_met)
        drift_confirmed = bool(sudden_confirm or gradual_confirm)
        drift_type = "sudden" if sudden_confirm else "gradual" if gradual_confirm else "unknown"

        if ready:
            self._last_u = float(u_stat)

        stats = {
            "proxy_indicators": {
                "any_warning": warning_event or (drift_confirmed and not self._warning_active),
                "confirmed_warning": self._warning_active,
                "warning_active": self._warning_active,
                "warning_age": warning_age,
                "cooldown_until": self._cooldown_until,
                "in_cooldown": in_cooldown,
                "raw_any_warning": is_warning_level,
                "policy": "gddm_rank_group",
                "first_warning_t": self._first_warning_t,
                "persistence_count": self._warning_run,
                "persistence_required": self.warning_persistence,
                "details": {
                    "GDDMStatistic": {
                        "warning": is_warning_level,
                        "stats": {
                            "gddm_U": float(u_stat),
                            "gddm_G_warning": (
                                None if warning_threshold is None else float(warning_threshold)
                            ),
                            "gddm_G_drift": (
                                None if drift_threshold is None else float(drift_threshold)
                            ),
                            "gddm_delta_U": float(delta_u),
                            "gddm_signal_dim": int(signal.shape[0]),
                            "gddm_ready": bool(ready),
                            "gddm_min_updates": int(self.min_updates),
                            "gddm_updates": int(self.n_updates),
                        },
                    }
                },
            },
            "ensemble_results": {"gddm_warning": is_warning_level, "gddm_drift": is_drift_level},
            "dynamic_weights": {},
            "meta_info": {
                "score_ratio": (
                    0.0
                    if drift_threshold in (None, 0)
                    else float(u_stat / drift_threshold)
                ),
                "strategy_used": "ecpf_gddm_rank_permutation",
                "drift_type": drift_type,
                "sudden_jump": bool(sudden_jump),
                "above_drift_run": int(self._above_drift_run),
                "gradual_persistence": int(self.gradual_persistence),
                "min_confirmation_age": int(self.min_confirmation_age),
            },
            "gddm_U": float(u_stat),
            "gddm_G_warning": None if warning_threshold is None else float(warning_threshold),
            "gddm_G_drift": None if drift_threshold is None else float(drift_threshold),
            "gddm_delta_U": float(delta_u),
            "gddm_drift_type": drift_type,
        }

        if drift_confirmed:
            self.n_drifts += 1
            self._warning_active = False
            self._first_warning_t = None
            self._warning_run = 0
            self._above_drift_run = 0
            self._cooldown_until = int(t) + self.cooldown_duration

        return drift_confirmed, int(t), stats

    def _build_signal_vector(
        self,
        proba_matrix: Optional[List[Dict[Any, float]]],
        y_true: float,
        y_pred: float,
        err: float,
    ) -> np.ndarray:
        values: List[float] = []
        if proba_matrix:
            while len(self._tree_error_windows) < len(proba_matrix):
                self._tree_error_windows.append(deque(maxlen=self.error_rate_window))
            y_norm = int(round(float(y_true)))
            for idx, proba in enumerate(proba_matrix):
                if proba:
                    pred = max(proba, key=proba.get)
                    tree_err = 1.0 if int(round(float(pred))) != y_norm else 0.0
                else:
                    tree_err = float(err)
                self._tree_error_windows[idx].append(tree_err)
                values.append(float(np.mean(self._tree_error_windows[idx])))

            if self.include_uq:
                values.append(float(self._uq_extractors[self.uq_mode].extract(proba_matrix)))
                values.append(float(self._uq_extractors["vote_disagreement"].extract(proba_matrix)))
                values.append(float(self._uq_extractors["predictive_entropy"].extract(proba_matrix)))
                values.append(self._margin_from_matrix(proba_matrix))

        if not values:
            values = [float(err), 1.0 if int(round(float(y_pred))) != int(round(float(y_true))) else 0.0]

        clean = np.asarray(values, dtype=np.float64)
        clean[~np.isfinite(clean)] = 0.0
        return clean

    @staticmethod
    def _margin_from_matrix(proba_matrix: List[Dict[Any, float]]) -> float:
        totals: Dict[Any, float] = {}
        count = 0
        for proba in proba_matrix:
            if not proba:
                continue
            count += 1
            for cls, prob in proba.items():
                totals[cls] = totals.get(cls, 0.0) + float(prob)
        if count == 0 or not totals:
            return 0.0
        averaged = sorted((v / count for v in totals.values()), reverse=True)
        if len(averaged) == 1:
            return float(averaged[0])
        return float(averaged[0] - averaged[1])

    def _current_windows(self) -> Tuple[np.ndarray, np.ndarray]:
        data = np.vstack(list(self.signal_history))
        reference = data[: self.reference_window]
        recent = data[self.reference_window :]
        return reference, recent

    def _thresholds(
        self,
        reference: np.ndarray,
        recent: np.ndarray,
    ) -> Tuple[Optional[float], Optional[float]]:
        key = (self.n_updates // max(1, self.threshold_update_interval), recent.shape[1])
        if (
            self._last_threshold_key == key
            and self._last_warning_threshold is not None
            and self._last_drift_threshold is not None
        ):
            return self._last_warning_threshold, self._last_drift_threshold

        perm_stats = self._permutation_statistics(reference, recent)
        if len(perm_stats) == 0:
            return None, None
        self._last_warning_threshold = float(
            np.quantile(perm_stats, 1.0 - self.warning_alpha)
        )
        self._last_drift_threshold = float(
            np.quantile(perm_stats, 1.0 - self.drift_alpha)
        )
        self._last_threshold_key = key
        return self._last_warning_threshold, self._last_drift_threshold

    def _permutation_statistics(self, reference: np.ndarray, recent: np.ndarray) -> np.ndarray:
        combined = np.vstack([reference, recent])
        n_ref = reference.shape[0]
        n_total = combined.shape[0]
        stats = np.zeros(self.n_permutations, dtype=np.float64)
        for i in range(self.n_permutations):
            perm = self.rng.permutation(n_total)
            ref_idx = perm[:n_ref]
            recent_idx = perm[n_ref:]
            stats[i] = self._group_statistic(combined[ref_idx], combined[recent_idx])
        return stats

    @classmethod
    def _group_statistic(cls, reference: np.ndarray, recent: np.ndarray) -> float:
        n_ref = reference.shape[0]
        n_recent = recent.shape[0]
        if n_ref == 0 or n_recent == 0:
            return 0.0
        combined = np.vstack([reference, recent])
        recent_mask = np.zeros(n_ref + n_recent, dtype=bool)
        recent_mask[n_ref:] = True
        mean_u = n_ref * n_recent / 2.0
        var_u = n_ref * n_recent * (n_ref + n_recent + 1) / 12.0
        if var_u <= 0:
            return 0.0

        total = 0.0
        for dim in range(combined.shape[1]):
            ranks = cls._average_ranks(combined[:, dim])
            rank_sum_recent = float(np.sum(ranks[recent_mask]))
            u_value = rank_sum_recent - n_recent * (n_recent + 1) / 2.0
            z = (u_value - mean_u) / np.sqrt(var_u)
            total += z * z
        return float(total)

    @staticmethod
    def _average_ranks(values: np.ndarray) -> np.ndarray:
        order = np.argsort(values, kind="mergesort")
        ranks = np.empty(len(values), dtype=np.float64)
        sorted_values = values[order]
        start = 0
        while start < len(values):
            end = start + 1
            while end < len(values) and sorted_values[end] == sorted_values[start]:
                end += 1
            avg_rank = (start + 1 + end) / 2.0
            ranks[order[start:end]] = avg_rank
            start = end
        return ranks
