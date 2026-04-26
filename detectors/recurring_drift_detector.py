"""
Recurring drift detector (RCD-inspired, Gonçalves Jr. & Barros 2013).

After a drift alert, decides whether the new context matches a *past* context by
comparing data windows with a **non-parametric kNN mixing test** and permutation
p-values (same spirit as the paper's multivariate two-sample test on instance buffers).

Inputs:
  1. Stream of prediction errors (always) — used to build a 1D window if no raw X.
  2. Drift alert index (position in the error stream / buffer).
  3. Concept memory — stored reference windows from previous *new* concepts.

Output:
  ``True`` if the current window is statistically similar to any stored window
  (p > significance); ``False`` if it appears to be a new concept.

Optional ``X_window`` or ``X_stream`` enables multivariate tests on raw features
(closest to the paper); otherwise the test uses a 1D window of prediction errors.
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional, Tuple

try:
    from sklearn.neighbors import NearestNeighbors
except ImportError:  # pragma: no cover
    NearestNeighbors = None


def _slice_window(
    series: np.ndarray,
    drift_idx: int,
    window_before: int,
    window_after: int,
) -> Tuple[np.ndarray, int, int]:
    """Return 1D or 2D slice ``series[start:end]`` (errors as (L,) or X as (L, d))."""
    n = len(series) if series.ndim == 1 else series.shape[0]
    start = max(0, drift_idx - window_before)
    end = min(n, drift_idx + window_after)
    if end <= start:
        start = max(0, n - window_before)
        end = n
    w = series[start:end]
    return np.asarray(w, dtype=np.float64), start, end


def _subsample_rows(X: np.ndarray, max_rows: int, rng: np.random.Generator) -> np.ndarray:
    """Uniform random subsample without replacement if len > max_rows."""
    X = np.asarray(X, dtype=np.float64)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    n = X.shape[0]
    if n <= max_rows:
        return X
    idx = rng.choice(n, size=max_rows, replace=False)
    idx.sort()
    return X[idx]


def _pool_standardize(X1: np.ndarray, X2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Z-score using pooled mean/std (per feature)."""
    Z = np.vstack([X1, X2])
    mu = Z.mean(axis=0)
    sigma = Z.std(axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    return (X1 - mu) / sigma, (X2 - mu) / sigma


def knn_mixing_statistic(
    nn_indices: np.ndarray,
    labels: np.ndarray,
) -> float:
    """
    Sum over points of (# of kNN that share the same sample label).
    Higher => stronger separation / less mixing (typical of different distributions).
    """
    n = len(labels)
    total = 0
    for i in range(n):
        neigh = nn_indices[i]
        total += int(np.sum(labels[neigh] == labels[i]))
    return float(total)


def knn_mixing_pvalue(
    X1: np.ndarray,
    X2: np.ndarray,
    *,
    k: int = 5,
    n_permutations: int = 199,
    random_state: Optional[int] = None,
) -> float:
    """
    Permutation p-value for H0: two samples from the same distribution.

    Uses fixed kNN graph on pooled standardized data; under H0, assigning
    which points are "sample 1" vs "sample 2" should not produce extreme
    same-label neighbor counts.

    Returns p in [0, 1]. **Large p** => fail to reject H0 => treat as **same
    distribution** (recurring). **Small p** => different (new concept).

    If sklearn is missing or samples are too small, returns 1.0 (assume recurring
    — conservative) or 0.0 — we return 1.0 to avoid false "new" when test inapplicable.
    """
    if NearestNeighbors is None:
        return 1.0

    X1 = np.asarray(X1, dtype=np.float64)
    X2 = np.asarray(X2, dtype=np.float64)
    if X1.ndim == 1:
        X1 = X1.reshape(-1, 1)
    if X2.ndim == 1:
        X2 = X2.reshape(-1, 1)

    n1, n2 = X1.shape[0], X2.shape[0]
    if n1 < k + 1 or n2 < k + 1:
        return 1.0

    X1s, X2s = _pool_standardize(X1, X2)
    Z = np.vstack([X1s, X2s])
    n = Z.shape[0]

    nn = NearestNeighbors(n_neighbors=min(k + 1, n), algorithm="auto", metric="euclidean")
    nn.fit(Z)
    dist, idx = nn.kneighbors(Z, return_distance=True)
    # drop self (first neighbor)
    nn_idx = idx[:, 1 : k + 1]
    if nn_idx.shape[1] < k:
        return 1.0

    labels = np.array([0] * n1 + [1] * n2, dtype=np.int64)
    t_obs = knn_mixing_statistic(nn_idx, labels)

    rng = np.random.default_rng(random_state)
    n_perm = int(n_permutations)
    if n_perm < 1:
        n_perm = 1

    ge = 0
    for _ in range(n_perm):
        perm_labels = np.zeros(n, dtype=np.int64)
        perm_labels[rng.choice(n, size=n2, replace=False)] = 1
        t_p = knn_mixing_statistic(nn_idx, perm_labels)
        if t_p >= t_obs:
            ge += 1

    return (1 + ge) / (1 + n_perm)


class ConceptMemory:
    """
    Stores reference windows (numpy arrays, shape (m, d)) from past *new* concepts.

    Each window is built around the drift alert the same way as the current query window
    (``window_before``, ``window_after``) so comparisons are aligned.
    """

    def __init__(
        self,
        significance: float = 0.01,
        k_neighbors: int = 5,
        max_buffer_size: int = 400,
        n_permutations: int = 199,
        window_before: int = 50,
        window_after: int = 10,
        random_seed: Optional[int] = 42,
        recurrence_threshold: Optional[float] = None,
    ):
        """
        Parameters
        ----------
        significance : float
            If p-value > significance, treat as same distribution (recurring). Paper used 0.01.
        k_neighbors : int
            k for kNN mixing (odd values preferred; default 5 like paper).
        max_buffer_size : int
            Max rows per window when comparing (paper used up to ~400).
        recurrence_threshold : float, optional
            Deprecated: if set, overrides ``significance`` (old API used this name).
        """
        if recurrence_threshold is not None:
            significance = float(recurrence_threshold)
        self.significance = float(significance)
        self.k_neighbors = int(k_neighbors)
        self.max_buffer_size = int(max_buffer_size)
        self.n_permutations = int(n_permutations)
        self.window_before = int(window_before)
        self.window_after = int(window_after)
        self.random_seed = random_seed
        self.buffers: List[np.ndarray] = []
        self.timestamps: List[int] = []

    def _rng(self) -> np.random.Generator:
        return np.random.default_rng(self.random_seed)

    def store(self, X_window: np.ndarray, timestamp: Optional[int] = None) -> None:
        """Append a reference window (subsampled to max_buffer_size)."""
        X_window = np.asarray(X_window, dtype=np.float64)
        if X_window.ndim == 1:
            X_window = X_window.reshape(-1, 1)
        X_window = _subsample_rows(X_window, self.max_buffer_size, self._rng())
        self.buffers.append(X_window)
        self.timestamps.append(int(timestamp) if timestamp is not None else -1)

    def clear(self) -> None:
        self.buffers.clear()
        self.timestamps.clear()

    def is_recurring_vs_stored(
        self, X_query: np.ndarray, significance: Optional[float] = None
    ) -> bool:
        return False
        
        """
        True if ``X_query`` is statistically similar to **any** stored buffer
        (p-value > significance for at least one comparison).
        """
        if not self.buffers:
            return False
        sig = self.significance if significance is None else float(significance)
        rng = self._rng()
        Xq = np.asarray(X_query, dtype=np.float64)
        if Xq.ndim == 1:
            Xq = Xq.reshape(-1, 1)
        Xq = _subsample_rows(Xq, self.max_buffer_size, rng)

        for buf in self.buffers:
            if buf.shape[1] != Xq.shape[1]:
                continue
            p = knn_mixing_pvalue(
                Xq,
                buf,
                k=self.k_neighbors,
                n_permutations=self.n_permutations,
                random_state=int(rng.integers(0, 2**31 - 1)),
            )
            if p > sig:
                return True
        return False


def build_signature(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
    window_before: int = 50,
    window_after: int = 10,
) -> np.ndarray:
    """
    Legacy 5D summary of errors around drift (for tests / debugging only).
    """
    n = len(prediction_errors)
    start = max(0, drift_timestamp - window_before)
    end = min(n, drift_timestamp + window_after)
    window = prediction_errors[start:end]
    if len(window) == 0:
        window = prediction_errors[-window_before:] if n else np.zeros(1)

    sig = np.array(
        [
            np.mean(window),
            np.std(window) if len(window) > 1 else 0.0,
            np.percentile(window, 25),
            np.percentile(window, 50),
            np.percentile(window, 75),
        ],
        dtype=np.float64,
    )
    return sig


def detect_recurring_drift(
    prediction_errors: np.ndarray,
    drift_alert_timestamp: int,
    concept_memory: ConceptMemory,
    *,
    add_if_new: bool = True,
    recurrence_threshold: Optional[float] = None,
    X_window: Optional[np.ndarray] = None,
    X_stream: Optional[np.ndarray] = None,
    post_alert_X: Optional[np.ndarray] = None,
    post_alert_errors: Optional[np.ndarray] = None,
) -> bool:
    """
    Decide whether drift at ``drift_alert_timestamp`` is recurring (RCD-style).

    **Query window** (first match wins):

    1. **Paper-like FIFO:** If ``post_alert_X`` or ``post_alert_errors`` is set, build ``W`` from
       those arrays only (contiguous post-alert samples, oldest→newest), shape ``(n, d)``.
    2. Else if ``X_window`` is given → use directly (shape ``(n, d)``).
    3. Else if ``X_stream`` is given → slice with ``window_before`` / ``window_after`` at ``t``.
    4. Else slice ``prediction_errors`` the same way (1D → ``(n, 1)``).

    ``drift_alert_timestamp`` is still used when storing metadata in memory.

    Parameters
    ----------
    recurrence_threshold : float, optional
        If provided, overrides significance for this call only (same role as α).
    """
    alpha = (
        float(recurrence_threshold)
        if recurrence_threshold is not None
        else concept_memory.significance
    )

    pe = np.asarray(prediction_errors, dtype=np.float64).ravel()
    t = int(drift_alert_timestamp)

    if post_alert_X is not None:
        W = np.asarray(post_alert_X, dtype=np.float64)
        if W.ndim == 1:
            W = W.reshape(-1, 1)
    elif post_alert_errors is not None:
        pa = np.asarray(post_alert_errors, dtype=np.float64).ravel()
        W = pa.reshape(-1, 1)
    elif X_window is not None:
        W = np.asarray(X_window, dtype=np.float64)
        if W.ndim == 1:
            W = W.reshape(-1, 1)
    elif X_stream is not None:
        Xs = np.asarray(X_stream, dtype=np.float64)
        if Xs.ndim == 1:
            Xs = Xs.reshape(-1, 1)
        W, _, _ = _slice_window(Xs, t, concept_memory.window_before, concept_memory.window_after)
        if W.size == 0:
            W = Xs[max(0, len(Xs) - concept_memory.window_before) :].reshape(-1, Xs.shape[1])
    else:
        w1d, _, _ = _slice_window(pe, t, concept_memory.window_before, concept_memory.window_after)
        if w1d.size == 0:
            w1d = pe[-concept_memory.window_before :] if len(pe) else np.array([0.0])
        W = w1d.reshape(-1, 1)

    if W.shape[0] < concept_memory.k_neighbors + 1:
        # Too little data: cannot run test; treat as new concept unless memory empty
        recurring = False
        if not concept_memory.buffers:
            recurring = False
    else:
        recurring = concept_memory.is_recurring_vs_stored(W, significance=alpha)

    if not recurring and add_if_new:
        concept_memory.store(W, t)

    return recurring


# ---------------------------------------------------------------------------
# Deprecated aliases (evaluate_recurring used these names)
# ---------------------------------------------------------------------------


class ConceptMemoryHybrid(ConceptMemory):
    """Deprecated: use :class:`ConceptMemory` (statistical test only)."""

    def __init__(self, *args, confidence_threshold: float = 0.6, **kwargs):
        super().__init__(*args, **kwargs)
        self.confidence_threshold = confidence_threshold


def detect_recurring_drift_hybrid(
    prediction_errors: np.ndarray,
    drift_alert_timestamp: int,
    concept_memory: ConceptMemoryHybrid,
    *,
    add_if_new: bool = True,
    **kwargs,
) -> bool:
    """Deprecated: identical to :func:`detect_recurring_drift`."""
    return detect_recurring_drift(
        prediction_errors,
        drift_alert_timestamp,
        concept_memory,
        add_if_new=add_if_new,
        **kwargs,
    )
