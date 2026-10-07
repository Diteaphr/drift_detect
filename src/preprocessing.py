"""Preprocessing and stream buffer for the data stream (y, ŷ) → prediction errors."""

import numpy as np
from typing import List, Optional


def zero_one_loss(y_true: float, y_pred: float) -> float:
    """Per-instance 0-1 loss: 1.0 on a misclassification, 0.0 when correct.

    This is the contract the detectors document for their ``err`` argument
    (``detectors/meta/base.py``: "1.0 for misclassification, 0.0 for correct")
    and it matches the definition the ECPF signal router already applies in
    ``detectors/meta_ecpf/signal_routing.py``.

    The previous formulation ``abs(y_true - y_pred)`` coincides with this one
    only when the labels are exactly {0, 1}: it treats class indices as
    *ordinal*, so with K > 2 a 0-vs-3 confusion scores 3.0 instead of 1.0.
    That magnitude reaches ADWIN, HDDM_A and Page-Hinkley unmodified in
    ``detectors/core/unified.py`` (only the binomial detectors are spared,
    because they re-threshold at ``> 0.5``), silently rescaling their bounds.
    The same holds for a {-1, +1} or {1, 2} binary encoding, where every
    mistake would score 2.0.
    """
    return 0.0 if int(round(float(y_true))) == int(round(float(y_pred))) else 1.0


def compute_prediction_errors(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Vectorised :func:`zero_one_loss` over aligned label arrays. Returns 1D array."""
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    return (np.rint(y_true) != np.rint(y_pred)).astype(np.float64)


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
        err: Optional[float] = None,
    ) -> None:
        """Store one (y_true, y_pred) pair and its error.

        *err* should be supplied by the caller so the per-instance error is
        computed exactly **once** per sample. That matters beyond tidiness: under
        a regression task the loss is stateful (it advances an online normalizer),
        so recomputing it here would move the running statistics twice per
        instance and skew every normalized value. Falls back to the 0-1 loss when
        omitted, which is what a classification caller would have produced anyway.
        """
        err = zero_one_loss(y_true, y_pred) if err is None else float(err)
        self._y_true.append(y_true)
        self._y_pred.append(y_pred)
        self._errors.append(err)
        self._indices.append(index)
        if x is not None:
            if isinstance(x, np.ndarray):
                xv = x
            else:
                xv = np.asarray(x, dtype=np.float64)
            if xv.ndim != 1:
                xv = xv.ravel()
            self._xs.append(xv.copy() if not isinstance(x, np.ndarray) or xv.base is not None else xv)
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
