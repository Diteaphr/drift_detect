"""
Synthetic stream generators for drift type classification.
One drift per stream; labels: sudden, gradual, incremental.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StreamSample:
    """Single generated stream with metadata."""
    stream_id: int
    X: np.ndarray          # (stream_length, n_features)
    y: np.ndarray          # (stream_length,) class labels
    t_drift: int           # true drift timestamp
    drift_type: str        # "sudden" | "gradual" | "incremental"


def _sample_drift_position(
    stream_length: int,
    position_range: Tuple[float, float],
    rng: np.random.Generator,
) -> int:
    low, high = position_range
    frac = rng.uniform(low, high)
    return int(frac * stream_length)


# ---------------------------------------------------------------------------
# Sudden drift: distribution changes abruptly at t_drift
# ---------------------------------------------------------------------------

def generate_sudden_streams(
    n_streams: int,
    stream_length: int,
    n_features: int,
    n_classes: int = 2,
    drift_position_range: Tuple[float, float] = (0.4, 0.6),
    random_seed: Optional[int] = 42,
) -> List[StreamSample]:
    """
    Binary/multiclass streams with abrupt concept change at t_drift.
    Before: one set of class means; after: different means (rotating hyperplane style).
    """
    rng = np.random.default_rng(random_seed)
    samples = []
    for sid in range(n_streams):
        t_drift = _sample_drift_position(stream_length, drift_position_range, rng)
        # Class means: pre-drift and post-drift different
        mean_pre = rng.standard_normal((n_classes, n_features)) * 2
        mean_post = rng.standard_normal((n_classes, n_features)) * 2
        X = np.zeros((stream_length, n_features))
        y = np.zeros(stream_length, dtype=np.int64)
        for t in range(stream_length):
            if t < t_drift:
                c = rng.integers(0, n_classes)
                X[t] = mean_pre[c] + rng.standard_normal(n_features) * 0.5
                y[t] = c
            else:
                c = rng.integers(0, n_classes)
                X[t] = mean_post[c] + rng.standard_normal(n_features) * 0.5
                y[t] = c
        samples.append(StreamSample(
            stream_id=sid,
            X=X.astype(np.float64),
            y=y,
            t_drift=t_drift,
            drift_type="sudden",
        ))
    return samples


# ---------------------------------------------------------------------------
# Gradual drift: mixture of old/new over a transition window
# ---------------------------------------------------------------------------

def generate_gradual_streams(
    n_streams: int,
    stream_length: int,
    n_features: int,
    n_classes: int = 2,
    drift_position_range: Tuple[float, float] = (0.4, 0.6),
    gradual_window_size: int = 200,
    random_seed: Optional[int] = 42,
) -> List[StreamSample]:
    """
    Transition window [t_drift - w/2, t_drift + w/2]: sample from old with prob (1-alpha),
    from new with prob alpha, where alpha goes 0 -> 1 across the window.
    """
    rng = np.random.default_rng(random_seed)
    samples = []
    w = min(gradual_window_size, stream_length // 3)
    for sid in range(n_streams):
        t_drift = _sample_drift_position(stream_length, drift_position_range, rng)
        t_start = max(0, t_drift - w // 2)
        t_end = min(stream_length, t_drift + w // 2)
        mean_pre = rng.standard_normal((n_classes, n_features)) * 2
        mean_post = rng.standard_normal((n_classes, n_features)) * 2
        X = np.zeros((stream_length, n_features))
        y = np.zeros(stream_length, dtype=np.int64)
        for t in range(stream_length):
            if t < t_start:
                c = rng.integers(0, n_classes)
                X[t] = mean_pre[c] + rng.standard_normal(n_features) * 0.5
                y[t] = c
            elif t >= t_end:
                c = rng.integers(0, n_classes)
                X[t] = mean_post[c] + rng.standard_normal(n_features) * 0.5
                y[t] = c
            else:
                alpha = (t - t_start) / max(1, t_end - t_start)
                if rng.random() < alpha:
                    c = rng.integers(0, n_classes)
                    X[t] = mean_post[c] + rng.standard_normal(n_features) * 0.5
                else:
                    c = rng.integers(0, n_classes)
                    X[t] = mean_pre[c] + rng.standard_normal(n_features) * 0.5
                y[t] = c
        samples.append(StreamSample(
            stream_id=sid,
            X=X.astype(np.float64),
            y=y,
            t_drift=t_drift,
            drift_type="gradual",
        ))
    return samples


# ---------------------------------------------------------------------------
# Incremental drift: many small steps over a long window
# ---------------------------------------------------------------------------

def generate_incremental_streams(
    n_streams: int,
    stream_length: int,
    n_features: int,
    n_classes: int = 2,
    drift_position_range: Tuple[float, float] = (0.4, 0.6),
    incremental_window_size: int = 400,
    random_seed: Optional[int] = 42,
) -> List[StreamSample]:
    """
    Concept changes smoothly: at each time t, means interpolate from pre to post
    over a long window (linear interpolation of parameters).
    """
    rng = np.random.default_rng(random_seed)
    samples = []
    w = min(incremental_window_size, stream_length // 2)
    for sid in range(n_streams):
        t_drift = _sample_drift_position(stream_length, drift_position_range, rng)
        t_start = max(0, t_drift - w // 2)
        t_end = min(stream_length, t_drift + w // 2)
        mean_pre = rng.standard_normal((n_classes, n_features)) * 2
        mean_post = rng.standard_normal((n_classes, n_features)) * 2
        X = np.zeros((stream_length, n_features))
        y = np.zeros(stream_length, dtype=np.int64)
        for t in range(stream_length):
            if t < t_start:
                beta = 0.0
            elif t >= t_end:
                beta = 1.0
            else:
                beta = (t - t_start) / max(1, t_end - t_start)
            mean_t = (1 - beta) * mean_pre + beta * mean_post
            c = rng.integers(0, n_classes)
            X[t] = mean_t[c] + rng.standard_normal(n_features) * 0.5
            y[t] = c
        samples.append(StreamSample(
            stream_id=sid,
            X=X.astype(np.float64),
            y=y,
            t_drift=t_drift,
            drift_type="incremental",
        ))
    return samples


# ---------------------------------------------------------------------------
# Unified API
# ---------------------------------------------------------------------------

DRIFT_TYPES = ("sudden", "gradual", "incremental")


def generate_all_streams(
    n_streams: int = 300,
    streams_per_class: int = 100,
    stream_length: int = 2000,
    n_features: int = 10,
    n_classes: int = 2,
    drift_position_range: Tuple[float, float] = (0.4, 0.6),
    gradual_window_size: int = 200,
    incremental_window_size: int = 400,
    random_seed: Optional[int] = 42,
) -> List[StreamSample]:
    """Generate n_streams total with streams_per_class per drift type."""
    assert n_streams == streams_per_class * 3
    rng = np.random.default_rng(random_seed)
    all_samples = []
    for i, drift_type in enumerate(DRIFT_TYPES):
        if drift_type == "sudden":
            lst = generate_sudden_streams(
                streams_per_class, stream_length, n_features, n_classes,
                drift_position_range, random_seed=rng.integers(0, 2**31),
            )
        elif drift_type == "gradual":
            lst = generate_gradual_streams(
                streams_per_class, stream_length, n_features, n_classes,
                drift_position_range, gradual_window_size,
                random_seed=rng.integers(0, 2**31),
            )
        else:
            lst = generate_incremental_streams(
                streams_per_class, stream_length, n_features, n_classes,
                drift_position_range, incremental_window_size,
                random_seed=rng.integers(0, 2**31),
            )
        for s in lst:
            s.stream_id = len(all_samples)
            all_samples.append(s)
    return all_samples
