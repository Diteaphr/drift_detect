"""Shared helpers: seeds, I/O, drift plans, validation, plots."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np

from config import (
    GRADUAL_WIDTH,
    INCR_ANNOTATION_WIDTH,
    MASTER_SEED,
    MIN_SEGMENT_LEN,
    N_DRIFTS_MAX,
    N_DRIFTS_MIN,
    ROOT_DIR,
    SUDDEN_WIDTH,
)


def deterministic_seed(*parts: Any, master: int = MASTER_SEED) -> int:
    """Stable uint32 seed from master + parts."""
    key = ":".join(str(p) for p in (master, *parts))
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def g_tag(g_id: int) -> str:
    return f"g{g_id:02d}"


def task_dir(task: str) -> Path:
    return ROOT_DIR / task


def drift_dir(task: str, drift_type: str) -> Path:
    return task_dir(task) / drift_type


def plots_dir(task: str) -> Path:
    return task_dir(task) / "drift_plots"


def ensure_dirs(task: str) -> None:
    for d in ("sudden", "gradual", "incremental", "recurring", "drift_plots"):
        (task_dir(task) / d).mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, xs: Sequence, ys: Sequence, n_features: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [f"x{i}" for i in range(n_features)] + ["y"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for x, yi in zip(xs, ys):
            if isinstance(x, dict):
                row = [x[i] for i in range(n_features)]
            else:
                row = [x[i] for i in range(n_features)]
            # classification labels as int when whole; regression keep float
            if isinstance(yi, (float, np.floating)) and float(yi).is_integer():
                y_out: Any = int(yi)
            elif isinstance(yi, (int, np.integer)):
                y_out = int(yi)
            else:
                y_out = float(yi)
            w.writerow(row + [y_out])


def write_drift_times(path: Path, intervals: list[list[int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(repr(intervals), encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def drift_intervals_for_positions(
    drift_positions: list[int],
    width: int,
    n_samples: int,
) -> list[list[int]]:
    half = width // 2
    out: list[list[int]] = []
    for p in drift_positions:
        s = max(0, int(p) - half)
        e = min(n_samples - 1, int(p) + half)
        out.append([s, e])
    return out


def _max_offset_for_width(width: int) -> int:
    return max(1, int(174 * width))


def _random_n_drifts(rng: np.random.Generator, n_samples: int) -> int:
    lo, hi = N_DRIFTS_MIN, N_DRIFTS_MAX
    # Smoke / short streams: fewer drifts
    if n_samples < 20_000:
        lo, hi = 2, max(2, min(4, n_samples // 400))
    return int(rng.integers(lo, hi + 1))


def _random_partition(
    rng: np.random.Generator,
    n: int,
    k: int,
    min_len: int,
) -> list[int]:
    if n < k * min_len:
        # Fallback: shrink min_len for smoke tests
        min_len = max(1, n // (k * 2))
        if n < k * min_len:
            min_len = 1
    remaining = n - k * min_len
    if remaining < 0:
        raise ValueError(f"Cannot partition n={n} into k={k}")
    extras = rng.multinomial(remaining, [1.0 / k] * k)
    return [min_len + int(x) for x in extras]


def _random_local_drift_position(
    rng: np.random.Generator,
    seg_len: int,
    width_ref: int,
) -> int:
    if seg_len <= 2:
        return max(0, seg_len // 2)
    margin = _max_offset_for_width(width_ref)
    hi = min(seg_len - 1, margin + 1)
    if hi < 1:
        return 1
    return int(rng.integers(1, hi + 1))


def build_segment_plan(
    n_samples: int,
    rng: np.random.Generator,
    width_ref: int = SUDDEN_WIDTH,
    n_drifts: int | None = None,
) -> dict:
    if n_drifts is None:
        n_drifts = _random_n_drifts(rng, n_samples)
    min_len = MIN_SEGMENT_LEN
    if n_samples < 20_000:
        min_len = max(MIN_SEGMENT_LEN, width_ref // 2 + 2)
    lengths = _random_partition(rng, n_samples, n_drifts, min_len)
    local_positions: list[int] = []
    drift_positions: list[int] = []
    offset = 0
    for seg_len in lengths:
        lp = _random_local_drift_position(rng, seg_len, width_ref)
        local_positions.append(lp)
        drift_positions.append(offset + lp)
        offset += seg_len
    return {
        "lengths": lengths,
        "local_positions": local_positions,
        "drift_positions": drift_positions,
        "n_drifts": n_drifts,
    }


def choose_recurring_mode(task: str, g_id: int, master: int = MASTER_SEED) -> str:
    rng = np.random.default_rng(deterministic_seed(task, "recurring_mode", g_id, master=master))
    return str(rng.choice(["sudden", "gradual", "incremental"]))


def width_for_mode(mode: str) -> int:
    if mode == "sudden":
        return SUDDEN_WIDTH
    if mode in {"gradual", "incremental"}:
        return GRADUAL_WIDTH if mode == "gradual" else INCR_ANNOTATION_WIDTH
    raise ValueError(mode)


def extract_from_chunks(chunks: list[tuple], n_samples: int) -> tuple[list, list]:
    xs: list = []
    ys: list = []
    for dataset, chunk_len in chunks:
        for x, y in dataset.take(chunk_len):
            xs.append(x)
            ys.append(y)
            if len(xs) >= n_samples:
                return xs[:n_samples], ys[:n_samples]
    return xs, ys


def validate_dataset(
    csv_path: Path,
    drift_path: Path,
    *,
    n_samples: int,
    max_transition_width: int | None,
) -> None:
    import pandas as pd

    df = pd.read_csv(csv_path)
    if "y" not in df.columns:
        raise AssertionError(f"missing y: {csv_path}")
    if len(df) != n_samples:
        raise AssertionError(f"row count {len(df)} != {n_samples}: {csv_path}")
    feats = df.drop(columns=["y"])
    if feats.shape[1] < 1:
        raise AssertionError(f"no features: {csv_path}")
    if not np.isfinite(feats.to_numpy(dtype=float)).all():
        raise AssertionError(f"non-finite features: {csv_path}")

    intervals = ast.literal_eval(drift_path.read_text(encoding="utf-8").strip())
    if not isinstance(intervals, list) or not intervals:
        raise AssertionError(f"bad drift intervals: {drift_path}")
    for pair in intervals:
        if len(pair) != 2:
            raise AssertionError(f"interval not pair: {pair}")
        s, e = int(pair[0]), int(pair[1])
        if not (0 <= s <= e < n_samples):
            raise AssertionError(f"interval out of range: {pair} n={n_samples}")
        if max_transition_width is not None:
            span = e - s + 1
            if span > max_transition_width:
                raise AssertionError(
                    f"transition span {span} > cap {max_transition_width}: {drift_path}"
                )


def annotate_fixed_windows(
    n_samples: int,
    centers: Sequence[int],
    width: int,
) -> list[list[int]]:
    return drift_intervals_for_positions(list(centers), width, n_samples)


def incremental_monitor_windows(
    seed: int,
    n_samples: int,
    width: int = INCR_ANNOTATION_WIDTH,
    n_windows: int | None = None,
) -> list[list[int]]:
    """Place non-overlapping monitor windows of length <= width along the stream."""
    rng = np.random.default_rng(seed + 31)
    if n_windows is None:
        n_windows = 3 if n_samples < 20_000 else int(rng.integers(4, 8))
    w = min(width, max(2, n_samples // (n_windows * 3)))
    intervals: list[list[int]] = []
    # keep margins between windows
    usable = n_samples - n_windows * w
    if usable < n_windows + 1:
        # pack from start
        t = max(1, n_samples // (n_windows + 1))
        for i in range(n_windows):
            s = min(n_samples - w, t * (i + 1))
            e = min(n_samples - 1, s + w - 1)
            intervals.append([s, e])
        return intervals
    gaps = rng.multinomial(usable, [1.0 / (n_windows + 1)] * (n_windows + 1))
    t = int(gaps[0])
    for i in range(n_windows):
        s = t
        e = min(n_samples - 1, s + w - 1)
        intervals.append([s, e])
        t = e + 1 + int(gaps[i + 1])
        if t >= n_samples:
            break
    return intervals


def plot_stream_overview(
    csv_path: Path,
    drift_path: Path,
    out_png: Path,
    *,
    title: str,
    task: str,
    window: int = 500,
    y_baseline: Sequence | None = None,
) -> None:
    import pandas as pd

    df = pd.read_csv(csv_path)
    intervals = ast.literal_eval(drift_path.read_text(encoding="utf-8").strip())
    y = df["y"].to_numpy(dtype=float)
    n = len(y)
    window = max(10, min(window, n // 5 or 10))

    fig, ax = plt.subplots(figsize=(12, 3.2))
    if y_baseline is not None:
        yb = np.asarray(y_baseline, dtype=float)
        # shared window based on max length so curves are comparable
        window = max(10, min(window, max(n, len(yb)) // 5 or 10))
        kernel = np.ones(window) / window
        roll_b = np.convolve(yb, kernel, mode="valid")
        ax.plot(
            np.arange(len(roll_b)),
            roll_b,
            color="0.55",
            linewidth=0.9,
            label="no drift",
            alpha=0.9,
        )
    else:
        kernel = np.ones(window) / window

    roll = np.convolve(y, kernel, mode="valid")
    if task == "regression":
        ax.plot(np.arange(len(roll)), roll, color="darkgreen", linewidth=0.9, label="with drift")
        ax.set_ylabel(f"rolling mean y (w={window})")
    else:
        ax.plot(np.arange(len(roll)), roll, color="steelblue", linewidth=0.9, label="with drift")
        ax.set_ylabel(f"rolling mean label (w={window})")

    for s, e in intervals:
        ax.axvspan(s, e, color="coral", alpha=0.25)
        ax.axvline(s, color="coral", linestyle="--", linewidth=0.8, alpha=0.9)

    ax.set_title(title)
    ax.set_xlabel("t")
    ax.set_xlim(0, n)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=120)
    plt.close(fig)


def save_recurring_manifest(task: str, rows: Iterable[dict]) -> Path:
    path = drift_dir(task, "recurring") / "manifest.json"
    write_json(path, {"task": task, "runs": list(rows)})
    return path
