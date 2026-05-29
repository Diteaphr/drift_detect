"""
Offline utility: sweep extension values to find the optimal detection window
for each labeled dataset and produce (features, labels) for RF training.

Typical usage (one-time, offline):

    from src.metrics.generate_window_labels import build_training_data
    X, y, meta = build_training_data("data/")
    # X: np.ndarray (n_events, n_features)
    # y: np.ndarray (n_events,)  — optimal extension in samples
    # meta: list of dicts with dataset path / drift index info
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from src.metrics.correct_detection import (
    build_perturbation_intervals,
    compute_correct_detection,
)

# ── extension sweep parameters ────────────────────────────────────────────────
_SWEEP_MIN = 100
_SWEEP_MAX = 3000
_SWEEP_STEP = 100
_TARGET_RECALL_FRAC = 0.95  # accept extension that achieves ≥ 95% of max score


def _load_drift_intervals(txt_path: Path) -> List[Tuple[int, int]]:
    raw = txt_path.read_text().strip()
    parsed = ast.literal_eval(raw)
    return [(int(a), int(b)) for a, b in parsed]


def find_optimal_extension(
    detection_timestamps: Sequence[int],
    drift_intervals: List[Tuple[int, int]],
    sweep_min: int = _SWEEP_MIN,
    sweep_max: int = _SWEEP_MAX,
    sweep_step: int = _SWEEP_STEP,
    target_frac: float = _TARGET_RECALL_FRAC,
) -> int:
    """Return the smallest extension (samples) that achieves target_frac of the
    maximum correct-detection score across a sweep of extension values.

    If no detections are provided, returns sweep_max as a conservative fallback.
    """
    if not detection_timestamps:
        return sweep_max

    extensions = list(range(sweep_min, sweep_max + sweep_step, sweep_step))
    scores: List[float] = []
    for ext in extensions:
        pert = build_perturbation_intervals(drift_intervals, extension=ext)
        result = compute_correct_detection(list(detection_timestamps), pert)
        scores.append(result.score_percent if result.score_percent is not None else 0.0)

    max_score = max(scores)
    if max_score == 0.0:
        return sweep_max  # detector never fires correctly → use large window

    threshold = target_frac * max_score
    for ext, sc in zip(extensions, scores):
        if sc >= threshold:
            return ext
    return extensions[-1]


# ── per-event feature extraction (no pipeline needed) ─────────────────────────

_DRIFT_TYPE_CODE = {"sudden": 0, "gradual": 1, "incremental": 2, "recurring": 3}


def _infer_drift_type(path: Path) -> int:
    """Infer drift type from directory name or file name."""
    name = str(path).lower()
    for key, code in _DRIFT_TYPE_CODE.items():
        if key in name:
            return code
    return -1  # unknown


def extract_interval_features(
    drift_intervals: List[Tuple[int, int]],
    stream_length: int,
    drift_type_code: int,
) -> np.ndarray:
    """
    Extract a feature vector from drift intervals (no CSV read required).

    Features (6):
        0  drift_type_code         — 0=sudden, 1=gradual, 2=incremental, 3=recurring
        1  interval_width_mean     — mean width of drift intervals
        2  interval_width_std      — std of interval widths (0 if single drift)
        3  n_drifts                — number of ground-truth drift events
        4  avg_inter_drift_gap     — mean samples between consecutive drift starts
        5  drift_density           — total drift-interval samples / stream_length
    """
    widths = np.array([e - s for s, e in drift_intervals], dtype=float)
    width_mean = float(widths.mean()) if len(widths) > 0 else 0.0
    width_std = float(widths.std()) if len(widths) > 1 else 0.0
    n = len(drift_intervals)

    starts = [s for s, _ in drift_intervals]
    if n > 1:
        gaps = [starts[i + 1] - starts[i] for i in range(n - 1)]
        avg_gap = float(np.mean(gaps))
    else:
        avg_gap = float(stream_length)

    total_drift_samples = float(widths.sum())
    density = total_drift_samples / stream_length if stream_length > 0 else 0.0

    return np.array(
        [drift_type_code, width_mean, width_std, n, avg_gap, density],
        dtype=float,
    )


def extract_stream_features(
    csv_path: Path,
    drift_intervals: List[Tuple[int, int]],
    pre_window: int = 500,
) -> np.ndarray:
    """
    Extract features that require reading the raw CSV stream.

    Additional features (4):
        6  pre_drift_var_mean      — mean feature variance in window before each drift
        7  pre_drift_var_std       — std of those per-drift variances
        8  feature_count           — number of feature columns
        9  label_entropy           — entropy of class distribution (whole stream)

    Returns a 4-element array to be concatenated with extract_interval_features().
    """
    import pandas as pd

    df = pd.read_csv(csv_path)
    feature_cols = [c for c in df.columns if c != "y"]
    n_features = len(feature_cols)
    X = df[feature_cols].values.astype(float)
    y = df["y"].values if "y" in df.columns else np.zeros(len(df))

    # Per-drift pre-drift variance
    pre_vars: List[float] = []
    for s, _ in drift_intervals:
        lo = max(0, s - pre_window)
        window = X[lo:s]
        if len(window) > 1:
            pre_vars.append(float(np.var(window, axis=0).mean()))
        else:
            pre_vars.append(0.0)

    pre_var_mean = float(np.mean(pre_vars)) if pre_vars else 0.0
    pre_var_std = float(np.std(pre_vars)) if len(pre_vars) > 1 else 0.0

    # Label entropy
    classes, counts = np.unique(y, return_counts=True)
    probs = counts / counts.sum()
    entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))

    return np.array([pre_var_mean, pre_var_std, n_features, entropy], dtype=float)


# ── dataset discovery and label generation ────────────────────────────────────


def _find_dataset_pairs(data_dir: Path) -> List[Tuple[Path, Path]]:
    """Return (csv_path, drift_times_path) pairs under data_dir."""
    pairs = []
    for txt in sorted(data_dir.rglob("*_drift_times.txt")):
        csv = txt.with_name(txt.name.replace("_drift_times.txt", ".csv"))
        if csv.exists():
            pairs.append((csv, txt))
    return pairs


def build_training_data(
    data_dir: str | Path,
    detection_results: Optional[Dict[str, List[int]]] = None,
    use_stream_features: bool = True,
    pre_window: int = 500,
) -> Tuple[np.ndarray, np.ndarray, List[dict]]:
    """
    Build (X, y, meta) for RF training.

    Parameters
    ----------
    data_dir : path to the data/ folder.
    detection_results : optional mapping of csv_path (str) → list of detection
        timestamps.  If omitted, labels cannot be generated and a ValueError
        is raised.  Pass an empty list for a dataset to skip it.
    use_stream_features : if True, also extract per-CSV stream statistics
        (requires reading each CSV; slower but richer features).
    pre_window : number of samples before each drift used for variance stats.

    Returns
    -------
    X : (n_events, n_features) float array.
    y : (n_events,) int array of optimal extension values.
    meta : list of dicts {'csv': str, 'drift_index': int, 'drift_interval': ...}
    """
    if detection_results is None:
        raise ValueError(
            "detection_results must be provided. "
            "Run your detector on labeled streams first and collect timestamps."
        )

    data_dir = Path(data_dir)
    pairs = _find_dataset_pairs(data_dir)
    if not pairs:
        raise FileNotFoundError(f"No dataset pairs found under {data_dir}")

    X_rows: List[np.ndarray] = []
    y_vals: List[int] = []
    meta: List[dict] = []

    for csv_path, txt_path in pairs:
        key = str(csv_path)
        if key not in detection_results:
            continue
        det_ts = detection_results[key]
        if det_ts is None:
            continue

        intervals = _load_drift_intervals(txt_path)
        drift_type_code = _infer_drift_type(csv_path)
        stream_length = sum(1 for _ in csv_path.open()) - 1  # subtract header

        interval_feats = extract_interval_features(intervals, stream_length, drift_type_code)

        if use_stream_features:
            stream_feats = extract_stream_features(csv_path, intervals, pre_window)
            feats = np.concatenate([interval_feats, stream_feats])
        else:
            feats = interval_feats

        # One label per dataset (not per drift event), representing the global
        # optimal extension for this stream's detections.
        opt_ext = find_optimal_extension(det_ts, intervals)

        X_rows.append(feats)
        y_vals.append(opt_ext)
        meta.append(
            {
                "csv": key,
                "drift_type": drift_type_code,
                "n_intervals": len(intervals),
                "optimal_extension": opt_ext,
            }
        )

    if not X_rows:
        raise ValueError("No matching detection results found for any dataset.")

    return np.array(X_rows), np.array(y_vals, dtype=int), meta


def save_training_data(
    X: np.ndarray,
    y: np.ndarray,
    meta: List[dict],
    out_path: str | Path,
) -> None:
    """Save training data as a .npz + .json pair."""
    out_path = Path(out_path)
    np.savez(out_path.with_suffix(".npz"), X=X, y=y)
    with open(out_path.with_suffix(".json"), "w") as f:
        json.dump(meta, f, indent=2)


def load_training_data(
    npz_path: str | Path,
) -> Tuple[np.ndarray, np.ndarray, List[dict]]:
    """Load previously saved training data."""
    npz_path = Path(npz_path)
    data = np.load(npz_path.with_suffix(".npz"))
    with open(npz_path.with_suffix(".json")) as f:
        meta = json.load(f)
    return data["X"], data["y"], meta
