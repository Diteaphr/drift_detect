"""
Sudden drift detector: detects abrupt change in prediction error distribution
by comparing two adjacent windows (reference vs current).
"""

import numpy as np
from typing import Optional, Tuple


class SuddenDriftDetector:
    """
    Detects sudden drift when the recent window of errors differs significantly
    from the reference window (e.g. mean shift or variance change).
    """

    def __init__(
        self,
        window_size: int = 50,
        threshold: float = 2.0,
        min_samples: int = 20,
    ):
        self.window_size = window_size
        self.threshold = threshold  # effect size or z-score threshold
        self.min_samples = min_samples
        self._buffer: list[float] = []

    def update(self, error: float) -> None:
        self._buffer.append(error)
        if len(self._buffer) > 2 * self.window_size:
            self._buffer.pop(0)

    def detect(self) -> Tuple[bool, Optional[int]]:
        """
        Returns (drift_detected, drift_timestamp).
        drift_timestamp is the index of the current (latest) sample when drift is detected.
        """
        n = len(self._buffer)
        if n < 2 * self.min_samples or n < self.window_size * 2:
            return False, None

        ref = np.array(self._buffer[-2 * self.window_size : -self.window_size], dtype=np.float64)
        cur = np.array(self._buffer[-self.window_size :], dtype=np.float64)

        if len(ref) < self.min_samples or len(cur) < self.min_samples:
            return False, None

        m_ref, m_cur = np.mean(ref), np.mean(cur)
        s_ref = np.std(ref)
        s_cur = np.std(cur)
        pooled_std = np.sqrt((s_ref**2 + s_cur**2) / 2) + 1e-10
        effect = abs(m_cur - m_ref) / pooled_std

        if effect >= self.threshold:
            return True, n - 1  # drift at current position
        return False, None

    def get_errors(self) -> np.ndarray:
        return np.array(self._buffer, dtype=np.float64)

    def reset(self) -> None:
        self._buffer.clear()
