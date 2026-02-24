"""
Recurring drift detector for concept drift pipeline.

Inputs:  (1) Streamline prediction error, (2) Drift alert timestamp, (3) Concept Memory
Output:  Recurring drift or not (bool)

Used after sudden/gradual detectors to decide if the current drift matches a past concept.
"""

import numpy as np
from typing import Optional


def build_signature(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
    window_before: int = 50,
    window_after: int = 10,
) -> np.ndarray:
    """
    Build a fixed-size signature from prediction errors around the drift time.

    Uses a window of errors around drift_timestamp and summarizes with simple stats.
    You can replace this with richer features (e.g. histogram, autocorrelation).
    """
    n = len(prediction_errors)
    start = max(0, drift_timestamp - window_before)
    end = min(n, drift_timestamp + window_after)
    window = prediction_errors[start:end]
    if len(window) == 0:
        window = prediction_errors[-window_before:] if n else np.zeros(1)

    # Simple statistical signature: mean, std, quartiles
    sig = np.array([
        np.mean(window),
        np.std(window) if len(window) > 1 else 0.0,
        np.percentile(window, 25),
        np.percentile(window, 50),
        np.percentile(window, 75),
    ], dtype=np.float64)
    return sig


class ConceptMemory:
    """
    Stores signatures of past drift "concepts" and supports similarity query.
    """

    def __init__(self, recurrence_threshold: float = 0.5):
        self.signatures: list[np.ndarray] = []
        self.timestamps: list[int] = []
        self.recurrence_threshold = recurrence_threshold  # max distance to consider "recurring"

    def store(self, signature: np.ndarray, timestamp: Optional[int] = None) -> None:
        self.signatures.append(np.asarray(signature, dtype=np.float64))
        self.timestamps.append(timestamp if timestamp is not None else -1)

    def _distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Euclidean distance between two signatures (normalize if needed)."""
        return float(np.linalg.norm(a - b))

    def find_nearest(self, signature: np.ndarray):
        """Returns (min_distance, index) or (float('inf'), -1) if memory is empty."""
        signature = np.asarray(signature, dtype=np.float64)
        if not self.signatures:
            return float("inf"), -1
        distances = [self._distance(signature, s) for s in self.signatures]
        idx = int(np.argmin(distances))
        return distances[idx], idx

    def is_recurring(self, signature: np.ndarray) -> bool:
        """True if the signature is close enough to any stored concept."""
        min_dist, _ = self.find_nearest(signature)
        return min_dist <= self.recurrence_threshold


def detect_recurring_drift(
    prediction_errors: np.ndarray,
    drift_alert_timestamp: int,
    concept_memory: ConceptMemory,
    *,
    add_if_new: bool = True,
    recurrence_threshold: Optional[float] = None,
) -> bool:
    """
    Main entry: decide if the drift at drift_alert_timestamp is recurring.

    Inputs:
        prediction_errors: 1D array of prediction errors (streamline or window).
        drift_alert_timestamp: index / time when sudden/gradual detector fired.
        concept_memory: store of past drift signatures.

    Output:
        True if recurring, False if new.

    If add_if_new is True, stores the current signature when drift is not recurring
    so future similar drifts can be classified as recurring.
    """
    if recurrence_threshold is not None:
        concept_memory.recurrence_threshold = recurrence_threshold

    signature = build_signature(prediction_errors, drift_alert_timestamp)
    recurring = concept_memory.is_recurring(signature)

    if not recurring and add_if_new:
        concept_memory.store(signature, drift_alert_timestamp)

    return recurring
