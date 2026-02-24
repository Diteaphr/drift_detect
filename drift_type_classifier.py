"""
Drift type classifier: when drift is not recurring, classify as Sudden vs Gradual
using simple features on the error stream around the drift time.
"""

import numpy as np
from config import DriftType


def _features(errors: np.ndarray, drift_idx: int, window: int = 40) -> np.ndarray:
    """Extract features: before-window mean/std, after-window mean/std, slope, jump size."""
    n = len(errors)
    w = min(window, n // 4)
    before_start = max(0, drift_idx - w)
    before = errors[before_start:drift_idx]
    after_end = min(n, drift_idx + w)
    after = errors[drift_idx:after_end]
    if len(before) < 2:
        before = errors[:drift_idx] if drift_idx else np.array([errors[0]])
    if len(after) < 2:
        after = errors[drift_idx:] if drift_idx < n else np.array([errors[-1]])
    mean_b = np.mean(before)
    mean_a = np.mean(after)
    std_b = np.std(before) + 1e-10
    std_a = np.std(after) + 1e-10
    jump = abs(mean_a - mean_b)
    slope = (mean_a - mean_b) / (len(after) + 1e-10)  # gradual tends to smaller slope over window
    # Sudden: big jump, possibly large std change. Gradual: smaller jump, more spread.
    return np.array([jump, slope, std_a / std_b, jump / (std_b + 1e-10)], dtype=np.float64)


def classify_drift_type(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
    *,
    sudden_jump_ratio: float = 1.5,
) -> DriftType:
    """
    Classify drift as SUDDEN or GRADUAL using heuristics on the error window.
    sudden_jump_ratio: if normalized jump is above this, prefer Sudden.
    """
    feats = _features(prediction_errors, drift_timestamp)
    jump, slope, std_ratio, norm_jump = feats[0], feats[1], feats[2], feats[3]
    # Heuristic: sudden = large immediate jump; gradual = smaller jump, more variance
    if norm_jump >= sudden_jump_ratio or (jump > 0.5 and std_ratio > 1.2):
        return DriftType.SUDDEN
    return DriftType.GRADUAL
