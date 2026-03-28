"""Preprocessing and stream buffer for the data stream (y, ŷ) → prediction errors."""

import numpy as np
from typing import List, Optional


def compute_prediction_errors(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Compute prediction errors (e.g. absolute or squared). Returns 1D array."""
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    return np.abs(y_true - y_pred)


def smooth_errors(errors: np.ndarray, window: int = 5) -> np.ndarray:
    """Optional smoothing (moving average) over errors. window=1 means no smoothing."""
    if window <= 1 or len(errors) < window:
        return np.asarray(errors, dtype=np.float64)
    kernel = np.ones(window) / window
    return np.convolve(errors, kernel, mode="same").astype(np.float64)


class StreamBuffer:
    """
    Buffer that maintains a sliding window of (y_true, y_pred, errors, indices)
    for use by drift detectors (reservoir-style).
    """

    def __init__(self, max_len: int = 2000):
        self.max_len = max_len
        self._y_true: list[float] = []
        self._y_pred: list[float] = []
        self._errors: list[float] = []
        self._indices: list[int] = []  # global timestamps
        self._xs: List[Optional[np.ndarray]] = []  # feature vectors, aligned with errors

    def append(
        self,
        y_true: float,
        y_pred: float,
        index: int,
        x: Optional[np.ndarray] = None,
    ) -> None:
        err = float(np.abs(y_true - y_pred))
        self._y_true.append(y_true)
        self._y_pred.append(y_pred)
        self._errors.append(err)
        self._indices.append(index)
        if x is not None:
            xv = np.asarray(x, dtype=np.float64).ravel()
            self._xs.append(xv.copy())
        else:
            self._xs.append(None)
        if len(self._errors) > self.max_len:
            self._y_true.pop(0)
            self._y_pred.pop(0)
            self._errors.pop(0)
            self._indices.pop(0)
            self._xs.pop(0)

    def get_errors(self, last_n: Optional[int] = None) -> np.ndarray:
        if last_n is None:
            return np.array(self._errors, dtype=np.float64)
        return np.array(self._errors[-last_n:], dtype=np.float64)

    def get_indices(self, last_n: Optional[int] = None) -> list[int]:
        if last_n is None:
            return list(self._indices)
        return self._indices[-last_n:]

    def length(self) -> int:
        return len(self._errors)

    def last_index(self) -> int:
        return self._indices[-1] if self._indices else -1

    def get_feature_window(
        self,
        drift_idx: int,
        window_before: int,
        window_after: int,
    ) -> Optional[np.ndarray]:
        """
        Rows of x aligned with ``get_errors()`` indices [start, end) around ``drift_idx``.
        Same slicing rule as the recurring detector's error window. Returns None if any
        row is missing ``x`` (caller should fall back to error-only test).
        """
        n = len(self._errors)
        start = max(0, drift_idx - window_before)
        end = min(n, drift_idx + window_after)
        if end <= start:
            start = max(0, n - window_before)
            end = n
        rows: List[np.ndarray] = []
        for i in range(start, end):
            if i >= len(self._xs):
                return None
            xi = self._xs[i]
            if xi is None:
                return None
            rows.append(np.asarray(xi, dtype=np.float64).ravel())
        if not rows:
            return None
        return np.stack(rows, axis=0)
