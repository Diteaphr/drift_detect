"""Shared I/O / plotting for injected_real_dataset."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import ROOT_DIR


def deterministic_seed(*parts: Any, master: int = 42) -> int:
    key = ":".join(str(p) for p in (master, *parts))
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def g_tag(g_id: int) -> str:
    return f"g{g_id:02d}"


def out_dir(task: str, abruptness: str, method: str) -> Path:
    return ROOT_DIR / task / abruptness / method


def plots_dir(task: str) -> Path:
    return ROOT_DIR / task / "drift_plots"


def ensure_layout(task: str, abruptness: str, method: str) -> None:
    out_dir(task, abruptness, method).mkdir(parents=True, exist_ok=True)
    plots_dir(task).mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_drift_times(path: Path, intervals: list[list[int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(repr(intervals), encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # kept_orig_idx can be long; still useful for exact replot — keep it
    payload = {**payload, "prepared_date": str(date.today())}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def adaptive_window(n: int, default: int = 500) -> int:
    if n < 100:
        return max(5, n // 10)
    return max(50, min(default, n // 20))


def rolling_mean(y: np.ndarray, w: int) -> np.ndarray:
    """Causal rolling mean: average of previous up-to-w samples ending at t."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    out = np.empty(n, dtype=float)
    y0 = np.where(np.isfinite(y), y, 0.0)
    valid = np.isfinite(y).astype(float)
    csum = np.cumsum(y0)
    ccnt = np.cumsum(valid)
    for t in range(n):
        s = max(0, t - w + 1)
        total = csum[t] - (csum[s - 1] if s > 0 else 0.0)
        cnt = ccnt[t] - (ccnt[s - 1] if s > 0 else 0.0)
        out[t] = total / cnt if cnt > 0 else np.nan
    return out


def align_y_to_baseline(
    y_drift: np.ndarray,
    n_baseline: int,
    kept_orig_idx: Sequence[int] | None,
) -> np.ndarray:
    """Place drifted labels onto baseline (shuffle) index; drops → NaN."""
    if kept_orig_idx is None or len(kept_orig_idx) != len(y_drift):
        # no drops / same length: assume 1:1
        if len(y_drift) == n_baseline:
            return np.asarray(y_drift, dtype=float)
        aligned = np.full(n_baseline, np.nan, dtype=float)
        m = min(len(y_drift), n_baseline)
        aligned[:m] = y_drift[:m]
        return aligned
    aligned = np.full(n_baseline, np.nan, dtype=float)
    idx = np.asarray(kept_orig_idx, dtype=int)
    aligned[idx] = np.asarray(y_drift, dtype=float)
    return aligned


def _mark_intervals(ax, intervals: list[list[int]]) -> None:
    for s, e in intervals:
        ax.axvspan(s, max(e, s), color="coral", alpha=0.25)
        ax.axvline(s, color="coral", linestyle="--", linewidth=0.9, alpha=0.9)
        if e > s:
            ax.axvline(e, color="coral", linestyle=":", linewidth=0.9, alpha=0.9)


def _class_label(c: float) -> str:
    return f"class {int(c)}" if float(c).is_integer() else f"class {c:g}"


def _class_proportion(y: np.ndarray, cls: float, w: int) -> np.ndarray:
    """Causal rolling P(y=cls); dropped rows (NaN) are excluded, not counted as 0."""
    ind = np.where(np.isfinite(y), (y == cls).astype(float), np.nan)
    return rolling_mean(ind, w)


def _plot_per_class_dual(
    y_base: np.ndarray,
    y_drift_aligned: np.ndarray,
    intervals: list[list[int]],
    out_png: Path,
    *,
    title: str,
    window: int,
) -> None:
    """One panel per class: grey = no drift, blue = with drift (rolling P(y=c))."""
    classes = sorted(
        {
            *np.unique(y_base[np.isfinite(y_base)]).tolist(),
            *np.unique(y_drift_aligned[np.isfinite(y_drift_aligned)]).tolist(),
        }
    )
    t = np.arange(len(y_base))
    fig, axes = plt.subplots(
        len(classes),
        1,
        figsize=(12, 1.45 * len(classes) + 1.6),
        sharex=True,
        squeeze=False,
    )
    axes = axes[:, 0]

    for i, (ax, c) in enumerate(zip(axes, classes)):
        p_base = _class_proportion(y_base, c, window)
        p_drift = _class_proportion(y_drift_aligned, c, window)
        # thicker grey underneath so perfect overlap still reads as two lines
        ax.plot(t, p_base, color="0.6", linewidth=2.0, alpha=0.9, label="no drift")
        ax.plot(t, p_drift, color="steelblue", linewidth=0.9, label="with drift")
        _mark_intervals(ax, intervals)

        stacked = np.concatenate([p_base, p_drift])
        vmax = np.nanmax(stacked) if np.any(np.isfinite(stacked)) else 1.0
        # per-panel scale so rare classes stay readable
        ax.set_ylim(0.0, max(0.05, float(vmax) * 1.2))
        ax.set_ylabel(_class_label(c), fontsize=9)
        ax.tick_params(labelsize=8)
        ax.set_xlim(0, max(len(y_base) - 1, 1))
        if i == 0:
            ax.legend(loc="upper right", fontsize=8, ncol=2)

    axes[-1].set_xlabel("t (shuffle / baseline index)")
    fig.suptitle(f"{title}  —  causal rolling class proportion (prev w={window})", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=120)
    plt.close(fig)


def plot_stream(
    df: pd.DataFrame,
    intervals: list[list[int]],
    out_png: Path,
    *,
    task: str,
    title: str,
    df_baseline: pd.DataFrame | None = None,
    kept_orig_idx: Sequence[int] | None = None,
    intervals_input: list[list[int]] | None = None,
) -> None:
    """Dual-line plot aligned on baseline (shuffle) index with a shared window."""
    y = df["y"].to_numpy(dtype=float)
    n = len(y)
    dual = df_baseline is not None and "y" in df_baseline.columns

    if dual and task == "multi_classification":
        yb = df_baseline["y"].to_numpy(dtype=float)
        w = adaptive_window(len(yb))
        _plot_per_class_dual(
            yb,
            align_y_to_baseline(y, len(yb), kept_orig_idx),
            intervals_input if intervals_input is not None else intervals,
            out_png,
            title=title,
            window=w,
        )
        return

    fig, ax = plt.subplots(figsize=(12, 3.4))

    if dual:
        yb = df_baseline["y"].to_numpy(dtype=float)
        n_base = len(yb)
        w = adaptive_window(n_base)  # shared window
        y_aligned = align_y_to_baseline(y, n_base, kept_orig_idx)
        roll_b = rolling_mean(yb, w)
        roll_d = rolling_mean(y_aligned, w)
        t = np.arange(len(roll_b))
        ax.plot(t, roll_b, color="0.55", linewidth=0.9, label="no drift", alpha=0.9)
        ax.plot(t, roll_d, color="steelblue", linewidth=0.9, label="with drift")
        ax.set_ylabel(f"causal rolling mean label (prev w={w})")
        mark = intervals_input if intervals_input is not None else intervals
        xlim_n = n_base
    elif task == "multi_classification":
        w = adaptive_window(n)
        classes = sorted(pd.unique(df["y"]))
        show = classes if len(classes) <= 8 else classes[:8]
        for c in show:
            ind = (df["y"].to_numpy() == c).astype(float)
            roll = rolling_mean(ind, w)
            ax.plot(np.arange(len(roll)), roll, linewidth=0.9, label=f"class {c}")
        ax.set_ylabel(f"causal rolling class proportion (prev w={w})")
        ax.set_ylim(-0.02, 1.02)
        mark = intervals
        xlim_n = n
    else:
        w = adaptive_window(n)
        roll = rolling_mean(y, w)
        ax.plot(np.arange(len(roll)), roll, color="steelblue", linewidth=0.9, label="with drift")
        ax.set_ylabel(f"causal rolling mean label (prev w={w})")
        mark = intervals
        xlim_n = n

    _mark_intervals(ax, mark)

    ax.set_title(title)
    ax.set_xlabel("t (shuffle / baseline index)" if dual else "t")
    ax.set_xlim(0, max(xlim_n - 1, 1))
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=120)
    plt.close(fig)
