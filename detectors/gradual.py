"""
Gradual drift detector: detects slow trend in prediction errors (e.g. Page-Hinkley / CUSUM).
"""

import numpy as np
from typing import Optional, Tuple


class GradualDriftDetector:
    """
    Page-Hinkley style detector: cumulative sum of (error - running_mean) with drift.
    Triggers when the cumulative deviation exceeds a threshold.
    """

    def __init__(
        self,
        window_size: int = 100,
        delta: float = 0.01,
        lambda_: float = 0.99,
        threshold: float = 50.0,
        min_samples: int = 30,
    ):
        self.window_size = window_size
        self.delta = delta
        self.lambda_ = lambda_
        self.threshold = threshold
        self.min_samples = min_samples
        self._errors: list[float] = []
        self._m: float = 0.0  # running mean (exponential)
        self._ph: float = 0.0  # Page-Hinkley statistic
        self._min_ph: float = 0.0

    def update(self, error: float) -> None:
        self._errors.append(error)
        if len(self._errors) > self.window_size:
            self._errors.pop(0)
        # Exponential moving average for reference level
        self._m = self.lambda_ * self._m + (1 - self.lambda_) * error
        # Cumulative deviation
        self._ph = self._ph + (error - self._m - self.delta)
        self._min_ph = min(self._min_ph, self._ph)

    def detect(self) -> Tuple[bool, Optional[int]]:
        """
        Returns (drift_detected, drift_timestamp).
        """
        if len(self._errors) < self.min_samples:
            return False, None
        # Drift when PH - min_PH exceeds threshold
        if self._ph - self._min_ph >= self.threshold:
            return True, len(self._errors) - 1
        return False, None

    def get_errors(self) -> np.ndarray:
        return np.array(self._errors, dtype=np.float64)

    def reset(self) -> None:
        self._errors.clear()
        self._m = 0.0
        self._ph = 0.0
        self._min_ph = 0.0
