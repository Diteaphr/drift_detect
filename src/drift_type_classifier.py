"""
Drift type classifier (Type-LDD inspired): when drift is not recurring,
classify as Sudden vs Gradual using gap-based error features and
prototypical-style classification (nearest prototype in feature space).

Reference: Type-LDD (Yu et al., IEEE TKDE 2024) — error features as gaps
between consecutive window mean errors; type identification via
prototype-based classification.
"""

import numpy as np
from typing import Optional, Tuple

from .config import DriftType


# ---------------------------------------------------------------------------
# Type-LDD style feature extraction: gap-based error features G
# ---------------------------------------------------------------------------

def build_gap_features(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
    n_windows: int = 5,
    context_len: int = 80,
) -> np.ndarray:
    """
    Build error features G as in Type-LDD: mean error per sub-window,
    then gaps between consecutive window means.

    G_j = ê_{j+1} - ê_j, where ê_j = mean(errors in window j).
    So G captures how the error level changes across windows (sudden = one
    big gap; gradual = smaller, spread gaps).

    Paper: "The difference between the average error rates of the two
    windows is formulated as: gap_j = ê_{j+1} - ê_j"
    """
    n = len(prediction_errors)
    half = context_len // 2
    start = max(0, drift_timestamp - half)
    end = min(n, drift_timestamp + half)
    window_errors = prediction_errors[start:end]
    if len(window_errors) < n_windows:
        # Pad or use full available length
        window_errors = np.pad(
            window_errors,
            (0, max(0, n_windows - len(window_errors))),
            mode="edge",
        )
    # Split into n_windows (equal-length) sub-windows
    sub_len = len(window_errors) // n_windows
    if sub_len < 1:
        sub_len = 1
    means = []
    for j in range(n_windows):
        beg = j * sub_len
        fin = min((j + 1) * sub_len, len(window_errors))
        if beg < fin:
            means.append(np.mean(window_errors[beg:fin]))
        else:
            means.append(means[-1] if means else 0.0)
    means = np.array(means, dtype=np.float64)
    # Gaps: G_j = ê_{j+1} - ê_j
    gaps = np.diff(means)
    return gaps


# ---------------------------------------------------------------------------
# Synthetic data for prototype learning (Type-LDD pre-training idea)
# ---------------------------------------------------------------------------

def _generate_synthetic_sudden(
    n_samples: int = 200,
    stream_len: int = 80,
    n_windows: int = 5,
    low: float = 0.2,
    high: float = 0.8,
    noise: float = 0.05,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Generate error streams with sudden drift (step change)."""
    rng = np.random.default_rng(seed)
    G_list = []
    for _ in range(n_samples):
        drift_at = stream_len // 2
        err = np.zeros(stream_len)
        err[:drift_at] = low + rng.normal(0, noise, drift_at)
        err[drift_at:] = high + rng.normal(0, noise, stream_len - drift_at)
        g = _gaps_from_stream(err, n_windows)
        G_list.append(g)
    return np.array(G_list)


def _generate_synthetic_gradual(
    n_samples: int = 200,
    stream_len: int = 80,
    n_windows: int = 5,
    low: float = 0.2,
    high: float = 0.8,
    noise: float = 0.05,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Generate error streams with gradual drift (linear ramp)."""
    rng = np.random.default_rng(seed)
    G_list = []
    for _ in range(n_samples):
        ramp = np.linspace(low, high, stream_len) + rng.normal(0, noise, stream_len)
        g = _gaps_from_stream(ramp, n_windows)
        G_list.append(g)
    return np.array(G_list)


def _gaps_from_stream(stream: np.ndarray, n_windows: int) -> np.ndarray:
    """Compute gap vector G from a single error stream."""
    sub_len = len(stream) // n_windows
    means = []
    for j in range(n_windows):
        beg = j * sub_len
        fin = (j + 1) * sub_len if j < n_windows - 1 else len(stream)
        if beg < fin:
            means.append(np.mean(stream[beg:fin]))
    means = np.array(means, dtype=np.float64)
    return np.diff(means)


# ---------------------------------------------------------------------------
# Prototypical-style classifier (Type-LDD drift-type identifier idea)
# ---------------------------------------------------------------------------

class DriftTypeClassifier:
    """
    Type-LDD inspired drift-type identifier: gap features G + nearest
    prototype (Euclidean). Prototypes are computed from synthetic
    (sudden/gradual) streams; no learned embedding for a minimal implementation.
    """

    def __init__(
        self,
        n_windows: int = 5,
        context_len: int = 80,
        n_synthetic_per_class: int = 200,
        random_state: Optional[int] = 42,
    ):
        self.n_windows = n_windows
        self.context_len = context_len
        self.n_synthetic_per_class = n_synthetic_per_class
        self.random_state = random_state
        self._prototype_sudden: Optional[np.ndarray] = None
        self._prototype_gradual: Optional[np.ndarray] = None
        self._fitted = False

    def fit(self) -> "DriftTypeClassifier":
        """Build prototypes from synthetic gap features (pre-training style)."""
        G_sudden = _generate_synthetic_sudden(
            n_samples=self.n_synthetic_per_class,
            stream_len=self.context_len,
            n_windows=self.n_windows,
            seed=self.random_state,
        )
        G_gradual = _generate_synthetic_gradual(
            n_samples=self.n_synthetic_per_class,
            stream_len=self.context_len,
            n_windows=self.n_windows,
            seed=(self.random_state + 1) if self.random_state is not None else None,
        )
        self._prototype_sudden = np.mean(G_sudden, axis=0).astype(np.float64)
        self._prototype_gradual = np.mean(G_gradual, axis=0).astype(np.float64)
        self._fitted = True
        return self

    def _ensure_fitted(self) -> None:
        if not self._fitted:
            self.fit()

    def predict(self, G: np.ndarray) -> DriftType:
        """Classify by nearest prototype (Euclidean distance)."""
        self._ensure_fitted()
        G = np.asarray(G, dtype=np.float64).ravel()
        # Match length to prototypes (in case of different n_windows)
        p_s = self._prototype_sudden
        p_g = self._prototype_gradual
        d_s = float(np.linalg.norm(G[: len(p_s)] - p_s)) if len(G) >= len(p_s) else float("inf")
        d_g = float(np.linalg.norm(G[: len(p_g)] - p_g)) if len(G) >= len(p_g) else float("inf")
        return DriftType.SUDDEN if d_s <= d_g else DriftType.GRADUAL


# Singleton classifier (fit once on first use)
_classifier: Optional[DriftTypeClassifier] = None


def _get_classifier(
    n_windows: int = 5,
    context_len: int = 80,
) -> DriftTypeClassifier:
    global _classifier
    if _classifier is None:
        _classifier = DriftTypeClassifier(
            n_windows=n_windows,
            context_len=context_len,
        ).fit()
    return _classifier


# ---------------------------------------------------------------------------
# Public API (drop-in replacement for previous rule-based classifier)
# ---------------------------------------------------------------------------

def classify_drift_type(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
    *,
    n_windows: int = 5,
    context_len: int = 80,
    use_type_ldd_style: bool = True,
) -> DriftType:
    """
    Classify drift as SUDDEN or GRADUAL.

    When use_type_ldd_style is True (default): use Type-LDD inspired
    gap-based features G and prototypical-style nearest prototype.
    """
    if use_type_ldd_style:
        G = build_gap_features(
            prediction_errors,
            drift_timestamp,
            n_windows=n_windows,
            context_len=context_len,
        )
        clf = _get_classifier(n_windows=n_windows, context_len=context_len)
        return clf.predict(G)
    # Fallback: simple rule-based (original behavior)
    return _classify_drift_type_rule_based(prediction_errors, drift_timestamp)


def _classify_drift_type_rule_based(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
    *,
    sudden_jump_ratio: float = 1.5,
) -> DriftType:
    """Original heuristic classifier (kept as fallback)."""
    n = len(prediction_errors)
    w = min(40, n // 4)
    before_start = max(0, drift_timestamp - w)
    before = prediction_errors[before_start:drift_timestamp]
    after_end = min(n, drift_timestamp + w)
    after = prediction_errors[drift_timestamp:after_end]
    if len(before) < 2:
        before = prediction_errors[:drift_timestamp] if drift_timestamp else np.array([prediction_errors[0]])
    if len(after) < 2:
        after = prediction_errors[drift_timestamp:] if drift_timestamp < n else np.array([prediction_errors[-1]])
    mean_b = np.mean(before)
    mean_a = np.mean(after)
    std_b = np.std(before) + 1e-10
    std_a = np.std(after) + 1e-10
    jump = abs(mean_a - mean_b)
    std_ratio = std_a / std_b
    norm_jump = jump / (std_b + 1e-10)
    if norm_jump >= sudden_jump_ratio or (jump > 0.5 and std_ratio > 1.2):
        return DriftType.SUDDEN
    return DriftType.GRADUAL
