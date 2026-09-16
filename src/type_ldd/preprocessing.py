"""
Load Type-LDD CSV streams into gap feature matrices (3-way only).

Faithful to Type-LDD-main/preprocessing.py, except we skip the `normal` class.
Labels: 0=abrupt/sudden, 1=gradual, 2=incremental.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

LABEL_ABRUPT = 0
LABEL_GRADUAL = 1
LABEL_INCREMENTAL = 2

CLASS_DIRS = {
    LABEL_ABRUPT: "abrupt",
    LABEL_GRADUAL: "gradual",
    LABEL_INCREMENTAL: "incremental",
}


def _relative_gaps_from_accuracy(acc: np.ndarray) -> np.ndarray:
    """gap_t = (acc[t+1] - acc[t]) / acc[t]  (Type-LDD preprocessing)."""
    acc = np.asarray(acc, dtype=np.float64).ravel()
    if len(acc) < 2:
        return np.zeros(0, dtype=np.float64)
    prev = acc[:-1]
    nxt = acc[1:]
    with np.errstate(divide="ignore", invalid="ignore"):
        gaps = (nxt - prev) / prev
    gaps = np.nan_to_num(gaps, nan=0.0, posinf=0.0, neginf=0.0)
    return gaps


def _drift_location_index(drift_col: np.ndarray) -> int:
    """First index where next-row drift flag is 1 (matches their shift(-1) logic)."""
    shifted = np.concatenate([drift_col[1:], [0]])
    hits = np.where(shifted == 1)[0]
    return int(hits[0]) if len(hits) else 0


def _load_one_class(
    class_dir: Path,
    label: int,
    feature_length: int,
    sample_num: int,
) -> pd.DataFrame:
    if not class_dir.is_dir():
        raise FileNotFoundError(f"Missing Type-LDD class directory: {class_dir}")

    rows = []
    files = sorted(p for p in class_dir.iterdir() if p.suffix.lower() == ".csv")
    if not files:
        raise FileNotFoundError(f"No CSV files in {class_dir}")

    for path in files:
        if len(rows) >= sample_num:
            break
        df = pd.read_csv(path)
        # Columns: index, accuracy, [drift_flag]
        if df.shape[1] < 2:
            continue
        acc = df.iloc[:, 1].to_numpy(dtype=np.float64)
        if df.shape[1] >= 3:
            loc = _drift_location_index(df.iloc[:, 2].to_numpy(dtype=np.float64))
        else:
            loc = 0
        gaps = _relative_gaps_from_accuracy(acc)
        if len(gaps) < feature_length:
            pad = np.zeros(feature_length - len(gaps), dtype=np.float64)
            gaps = np.concatenate([gaps, pad])
        else:
            gaps = gaps[:feature_length]
        row = {f"feature_{i}": float(gaps[i]) for i in range(feature_length)}
        row["label"] = label
        row["location"] = loc
        rows.append(row)

    if len(rows) < sample_num:
        # Match upstream behavior: use whatever is available if short.
        pass
    return pd.DataFrame(rows)


def load_drift_data_3way(
    data_dir: Path,
    data_vector_length: int = 50,
    data_sample_num: int = 4800,
) -> pd.DataFrame:
    """
    Load abrupt/gradual/incremental only (no normal).

    Returns a DataFrame with columns feature_0..feature_{L-1}, label, location.
    """
    data_dir = Path(data_dir)
    frames = []
    for label, sub in CLASS_DIRS.items():
        frame = _load_one_class(
            data_dir / sub,
            label=label,
            feature_length=data_vector_length,
            sample_num=data_sample_num,
        )
        frames.append(frame.iloc[:data_sample_num].copy())
    all_df = pd.concat(frames, ignore_index=True)
    return all_df


def dataframe_to_arrays(
    df: pd.DataFrame,
    data_vector_length: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = df.iloc[:, :data_vector_length].to_numpy(dtype=np.float64)
    y = df["label"].to_numpy(dtype=np.int64)
    loc = df["location"].to_numpy(dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    return x, y, loc


def train_test_split_arrays(
    x: np.ndarray,
    y: np.ndarray,
    loc: np.ndarray,
    train_ratio: float = 0.8,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y))
    rng.shuffle(idx)
    x, y, loc = x[idx], y[idx], loc[idx]
    n_train = int(len(y) * train_ratio)
    return (
        x[:n_train],
        y[:n_train],
        loc[:n_train],
        x[n_train:],
        y[n_train:],
        loc[n_train:],
    )
