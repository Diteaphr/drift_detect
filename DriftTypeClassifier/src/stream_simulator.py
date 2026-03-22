"""
Simulate online classifier over a stream to produce prediction errors.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

try:
    from sklearn.linear_model import SGDClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class StreamSimResult:
    """Result of running online classifier on a stream."""
    predictions: np.ndarray   # (stream_length,)
    errors: np.ndarray        # (stream_length,) 0/1
    confidences: Optional[np.ndarray] = None


def run_online_classifier(
    X: np.ndarray,
    y: np.ndarray,
    warm_start: int = 50,
    random_state: int = 42,
) -> StreamSimResult:
    """
    At each t: predict, compute error e_t = 1 if wrong else 0, then update with (X_t, y_t).
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("sklearn required for stream_simulator")
    X = np.asarray(X)
    y = np.asarray(y).ravel()
    n = len(y)
    predictions = np.full(n, -1, dtype=np.int64)
    errors = np.zeros(n, dtype=np.float64)
    confidences = np.zeros(n, dtype=np.float64)

    scaler = StandardScaler()
    classes = np.unique(y)
    # max_iter high enough so initial warm_start fit converges (avoids hundreds of ConvergenceWarnings)
    model = SGDClassifier(max_iter=500, warm_start=True, random_state=random_state, tol=1e-3)

    # Warm start
    X_warm = X[:warm_start]
    y_warm = y[:warm_start]
    X_s = scaler.fit_transform(X_warm)
    model.fit(X_s, y_warm)
    predictions[:warm_start] = model.predict(X_s)
    for i in range(warm_start):
        errors[i] = 1.0 if predictions[i] != y[i] else 0.0
    if hasattr(model, "predict_proba"):
        confidences[:warm_start] = np.max(model.predict_proba(X_s), axis=1)

    for t in range(warm_start, n):
        x_t = X[t : t + 1]
        x_s = scaler.transform(x_t)
        pred = model.predict(x_s)[0]
        predictions[t] = pred
        errors[t] = 1.0 if pred != y[t] else 0.0
        if hasattr(model, "predict_proba"):
            confidences[t] = float(np.max(model.predict_proba(x_s)))
        else:
            confidences[t] = 1.0 if pred == y[t] else 0.0
        model.partial_fit(x_s, y[t : t + 1], classes=classes)

    return StreamSimResult(
        predictions=predictions,
        errors=errors,
        confidences=confidences,
    )
