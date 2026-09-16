"""
Drift type classifier adapter using the trained Type-LDD (FAN ProtoNet) checkpoint.

This keeps the same public API expected by `src/pipeline.py`:
    classify_drift_type(prediction_errors, drift_timestamp) -> DriftType

Where:
- `prediction_errors` is the 1D error history from `StreamBuffer`:
    err[t] = |y_true[t] - y_pred[t]|
- `drift_timestamp` is the index in that error array at which we raised the alert.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from .config import DriftType
from .type_ldd.infer import load_classifier
from .type_ldd.infer import TypeLDDClassifier


_classifier: Optional[TypeLDDClassifier] = None


def _ensure_classifier() -> TypeLDDClassifier:
    global _classifier
    if _classifier is None:
        _classifier = load_classifier()  # defaults to checkpoints/type_ldd
    return _classifier


def classify_drift_type(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
) -> DriftType:
    """Pipeline-facing API: errors -> Type-LDD 50-d gaps -> sudden/gradual/incremental."""
    clf = _ensure_classifier()
    return clf.predict_errors(prediction_errors, drift_timestamp=int(drift_timestamp))

