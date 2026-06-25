"""
RF-based adaptive window estimator for Correct Detection Score evaluation.

Usage
-----
### Offline training (one-time):

    from src.metrics.generate_window_labels import build_training_data
    from src.metrics.adaptive_window import AdaptiveWindowEstimator

    # Collect detection timestamps per dataset first (run your pipeline once)
    detection_results = {
        "data/sudden_drift/recurring_sudden_sea100k_g00.csv": [3500, 22000, ...],
        ...
    }
    X, y, meta = build_training_data("data/", detection_results)
    estimator = AdaptiveWindowEstimator()
    estimator.fit(X, y)
    estimator.save("models/adaptive_window_rf.pkl")

### Inference (per evaluation):

    from src.metrics.adaptive_window import AdaptiveWindowEstimator, WindowFeatures
    from src.metrics import build_perturbation_intervals, compute_correct_detection

    estimator = AdaptiveWindowEstimator.load("models/adaptive_window_rf.pkl")

    wf = WindowFeatures.from_csv("data/sudden_drift/my_stream.csv", drift_intervals)
    ext = estimator.predict_extension(wf.to_array())
    pert = build_perturbation_intervals(drift_intervals, extension=ext)
    result = compute_correct_detection(detection_timestamps, pert)
"""

from __future__ import annotations

import ast
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np

from src.metrics.generate_window_labels import (
    _infer_drift_type,
    _DRIFT_TYPE_CODE,
    extract_interval_features,
    extract_stream_features,
)

# Feature names (in order) — for documentation and feature-importance inspection.
FEATURE_NAMES = [
    "drift_type_code",
    "interval_width_mean",
    "interval_width_std",
    "n_drifts",
    "avg_inter_drift_gap",
    "drift_density",
    # Stream features (only when use_stream_features=True)
    "pre_drift_var_mean",
    "pre_drift_var_std",
    "feature_count",
    "label_entropy",
]

# Default extension if the estimator has no model yet.
_FALLBACK_EXTENSION = 1000


@dataclass
class WindowFeatures:
    """Intermediate container so callers can build features incrementally."""

    drift_type_code: int
    interval_width_mean: float
    interval_width_std: float
    n_drifts: int
    avg_inter_drift_gap: float
    drift_density: float
    # Optional stream features (set to None when not computed)
    pre_drift_var_mean: Optional[float] = None
    pre_drift_var_std: Optional[float] = None
    feature_count: Optional[int] = None
    label_entropy: Optional[float] = None

    # ── convenience constructors ──────────────────────────────────────────────

    @classmethod
    def from_intervals(
        cls,
        drift_intervals: List[Tuple[int, int]],
        stream_length: int,
        drift_type_code: int,
    ) -> "WindowFeatures":
        """Build from drift intervals only (no CSV needed)."""
        arr = extract_interval_features(drift_intervals, stream_length, drift_type_code)
        return cls(
            drift_type_code=int(arr[0]),
            interval_width_mean=float(arr[1]),
            interval_width_std=float(arr[2]),
            n_drifts=int(arr[3]),
            avg_inter_drift_gap=float(arr[4]),
            drift_density=float(arr[5]),
        )

    @classmethod
    def from_csv(
        cls,
        csv_path: str | Path,
        drift_intervals: List[Tuple[int, int]],
        pre_window: int = 500,
    ) -> "WindowFeatures":
        """Build full feature set including stream statistics."""
        csv_path = Path(csv_path)
        drift_type_code = _infer_drift_type(csv_path)
        stream_length = sum(1 for _ in csv_path.open()) - 1
        int_arr = extract_interval_features(drift_intervals, stream_length, drift_type_code)
        stream_arr = extract_stream_features(csv_path, drift_intervals, pre_window)
        return cls(
            drift_type_code=int(int_arr[0]),
            interval_width_mean=float(int_arr[1]),
            interval_width_std=float(int_arr[2]),
            n_drifts=int(int_arr[3]),
            avg_inter_drift_gap=float(int_arr[4]),
            drift_density=float(int_arr[5]),
            pre_drift_var_mean=float(stream_arr[0]),
            pre_drift_var_std=float(stream_arr[1]),
            feature_count=int(stream_arr[2]),
            label_entropy=float(stream_arr[3]),
        )

    @classmethod
    def from_drift_type_and_intervals(
        cls,
        drift_type: str,
        drift_intervals: List[Tuple[int, int]],
        stream_length: int,
    ) -> "WindowFeatures":
        """Convenience: pass drift type as string (e.g. 'sudden')."""
        code = _DRIFT_TYPE_CODE.get(drift_type.lower(), -1)
        return cls.from_intervals(drift_intervals, stream_length, code)

    # ── array conversion ──────────────────────────────────────────────────────

    def to_array(self) -> np.ndarray:
        """Convert to a 1-D float array for RF prediction.

        Uses 6-feature vector when stream features are absent, 10-feature vector
        when all fields are populated.  The estimator must have been trained on
        the same feature set.
        """
        base = [
            float(self.drift_type_code),
            self.interval_width_mean,
            self.interval_width_std,
            float(self.n_drifts),
            self.avg_inter_drift_gap,
            self.drift_density,
        ]
        if self.pre_drift_var_mean is not None:
            base += [
                self.pre_drift_var_mean,
                self.pre_drift_var_std if self.pre_drift_var_std is not None else 0.0,
                float(self.feature_count) if self.feature_count is not None else 0.0,
                self.label_entropy if self.label_entropy is not None else 0.0,
            ]
        return np.array(base, dtype=float)


class AdaptiveWindowEstimator:
    """
    Wraps a RandomForestRegressor to predict the optimal detection window
    (extension in samples) for `build_perturbation_intervals`.

    The RF is trained offline once; the predict_extension() call is O(1) at
    evaluation time.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        random_state: int = 42,
        fallback_extension: int = _FALLBACK_EXTENSION,
    ) -> None:
        self._fallback = fallback_extension
        self._n_estimators = n_estimators
        self._random_state = random_state
        self._model = None  # lazy init on fit()

    # ── training ──────────────────────────────────────────────────────────────

    def fit(self, X: np.ndarray, y: np.ndarray) -> "AdaptiveWindowEstimator":
        """Train the RF on (X=features, y=optimal_extension)."""
        from sklearn.ensemble import RandomForestRegressor

        self._model = RandomForestRegressor(
            n_estimators=self._n_estimators,
            random_state=self._random_state,
        )
        self._model.fit(X, y)
        return self

    # ── inference ─────────────────────────────────────────────────────────────

    def predict_extension(
        self,
        features: np.ndarray | WindowFeatures,
        clip_min: int = 100,
        clip_max: int = 3000,
    ) -> int:
        """Predict the optimal extension (in samples) for a given feature vector.

        Parameters
        ----------
        features : 1-D np.ndarray or a WindowFeatures instance.
        clip_min, clip_max : clamp the prediction to a sensible range.

        Returns the fallback value (default 1000) if the estimator has not been
        trained yet.
        """
        if self._model is None:
            return self._fallback

        if isinstance(features, WindowFeatures):
            features = features.to_array()

        arr = np.asarray(features, dtype=float).reshape(1, -1)
        raw = float(self._model.predict(arr)[0])
        return int(np.clip(round(raw / 100) * 100, clip_min, clip_max))

    def feature_importances(self) -> Optional[np.ndarray]:
        """Return RF feature importances (None if not yet trained)."""
        if self._model is None:
            return None
        return self._model.feature_importances_

    # ── persistence ───────────────────────────────────────────────────────────

    def save(self, path: str | Path) -> None:
        """Pickle the estimator to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str | Path) -> "AdaptiveWindowEstimator":
        """Load a previously saved estimator."""
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Loaded object is {type(obj)}, expected AdaptiveWindowEstimator")
        return obj

    # ── leave-one-out CV helper ───────────────────────────────────────────────

    def cross_val_mae(self, X: np.ndarray, y: np.ndarray) -> float:
        """Leave-one-out MAE — use to check RF quality before deploying."""
        from sklearn.model_selection import cross_val_score
        from sklearn.ensemble import RandomForestRegressor

        rf = RandomForestRegressor(
            n_estimators=self._n_estimators,
            random_state=self._random_state,
        )
        scores = cross_val_score(rf, X, y, cv=min(len(y), 5), scoring="neg_mean_absolute_error")
        return float(-scores.mean())
