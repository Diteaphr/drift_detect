"""
Small multiples / facets for RandomRBFDrift (incremental) g00.

Goal
----
Make concept drift visible by comparing class-colored point clouds across time segments
in a *fixed* 2D projection (PCA fit once, then applied to all segments), with *fixed*
axis limits across subplots.

Default behavior
----------------
- Dataset: incremental_drift/recurring_incremental_rbf4_100k_g00.csv
- Segments: 4 equal chunks (0–25k, 25k–50k, 50k–75k, 75k–100k)
- Sampling: take 1 point every STRIDE (default 100) within each segment
- Output: drift_validation_plots/rbf_incremental_small_multiples_pca_g00.png

Optional
--------
You can segment by the provided drift_intervals (from *_drift_times.txt) by setting
USE_DRIFT_INTERVALS = True.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = Path(__file__).resolve().parent

N_CLASSES = 4
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

G_TAG = "g00"

# Sampling
STRIDE = 20  # every 100 points -> ~1,000 points total across 4 segments

# Segmentation mode
USE_DRIFT_INTERVALS = False
N_EQUAL_SEGMENTS = 4  # used when USE_DRIFT_INTERVALS=False

# Plot config
POINT_SIZE = 8
ALPHA = 0.65
FIG_H = 4.4
FIG_W_PER_PANEL = 4.6
AXIS_PAD_FRAC = 0.05

def load_drift_intervals(path: Path) -> list[list[int]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8").strip()
    return ast.literal_eval(text)


def _pca_fit_svd(x: np.ndarray, n_components: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (mu, comps) where:
    - mu is (D,)
    - comps is (n_components, D)
    """
    mu = x.mean(axis=0)
    xc = x - mu
    _, _, vt = np.linalg.svd(xc, full_matrices=False)
    comps = vt[:n_components]
    return mu, comps


def _pca_transform(x: np.ndarray, mu: np.ndarray, comps: np.ndarray) -> np.ndarray:
    return (x - mu) @ comps.T


def _equal_segments(n_samples: int, n_segments: int) -> list[tuple[int, int]]:
    edges = np.linspace(0, n_samples, n_segments + 1, dtype=int)
    segs: list[tuple[int, int]] = []
    for i in range(n_segments):
        s = int(edges[i])
        e = int(edges[i + 1])
        segs.append((s, e))
    return segs


def _segments_from_drift_intervals(
    intervals: list[list[int]], n_samples: int
) -> list[tuple[int, int]]:
    # Treat each drift interval as a segment; sort by start.
    segs: list[tuple[int, int]] = []
    for pair in intervals:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            continue
        s, e = int(pair[0]), int(pair[1])
        if s > e:
            s, e = e, s
        s = max(0, s)
        e = min(n_samples, e + 1)  # convert to slicing end-exclusive
        if s < e:
            segs.append((s, e))
    segs.sort(key=lambda t: t[0])
    return segs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sensitivity",
        default="medium",
        choices=("low", "medium", "high"),
        help="Sensitivity tier subdirectory (default: medium)",
    )
    args = parser.parse_args()
    tier = args.sensitivity

    csv_path = (
        BASE_DIR / "incremental_drift" / tier / f"recurring_incremental_rbf4_100k_{G_TAG}.csv"
    )
    drift_times_path = (
        BASE_DIR
        / "incremental_drift"
        / tier
        / f"recurring_incremental_rbf4_100k_{G_TAG}_drift_times.txt"
    )
    out_path = OUT_DIR / f"rbf_incremental_small_multiples_pca_{tier}_{G_TAG}.png"

    df = pd.read_csv(csv_path)
    if "y" not in df.columns:
        raise ValueError("CSV 需包含 y 欄位")

    feat_cols = [c for c in df.columns if c.startswith("x")]
    if not feat_cols:
        raise ValueError("CSV 需包含 x0..xN 特徵欄位")

    n_samples = len(df)

    if USE_DRIFT_INTERVALS:
        intervals = load_drift_intervals(drift_times_path)
        segments = _segments_from_drift_intervals(intervals, n_samples)
        if not segments:
            raise ValueError("找不到 drift_intervals，無法切段")
    else:
        segments = _equal_segments(n_samples, N_EQUAL_SEGMENTS)

    # Build a sampled dataframe across *all* segments for PCA fit + axis limits.
    parts = [df.iloc[s:e:STRIDE] for (s, e) in segments]
    df_s = pd.concat(parts, axis=0, ignore_index=True)

    x_all = df_s[feat_cols].to_numpy(dtype=float)
    mu, comps = _pca_fit_svd(x_all, n_components=2)
    z_all = _pca_transform(x_all, mu, comps)

    # Fixed axis limits across panels
    x_min, x_max = float(z_all[:, 0].min()), float(z_all[:, 0].max())
    y_min, y_max = float(z_all[:, 1].min()), float(z_all[:, 1].max())
    pad_x = AXIS_PAD_FRAC * (x_max - x_min + 1e-9)
    pad_y = AXIS_PAD_FRAC * (y_max - y_min + 1e-9)

    # Plot
    n_panels = len(segments)
    fig, axes = plt.subplots(
        1,
        n_panels,
        figsize=(FIG_W_PER_PANEL * n_panels, FIG_H),
        sharex=True,
        sharey=True,
    )
    if n_panels == 1:
        axes = [axes]

    for i, (s, e) in enumerate(segments):
        ax = axes[i]
        seg = df.iloc[s:e:STRIDE]
        x = seg[feat_cols].to_numpy(dtype=float)
        z = _pca_transform(x, mu, comps)
        y = seg["y"].to_numpy(dtype=int)

        for k in range(N_CLASSES):
            m = y == k
            ax.scatter(
                z[m, 0],
                z[m, 1],
                s=POINT_SIZE,
                alpha=ALPHA,
                c=COLORS[k],
                label=f"Class {k}",
                linewidths=0,
            )

        ax.set_title(f"{s//1000}k–{e//1000}k (n≈{len(seg)})", fontsize=10)
        ax.set_xlim(x_min - pad_x, x_max + pad_x)
        ax.set_ylim(y_min - pad_y, y_max + pad_y)
        ax.grid(True, linestyle=":", alpha=0.4)

        if i == 0:
            ax.set_ylabel("PCA component 2")
        ax.set_xlabel("PCA component 1")

    # One legend for the whole figure
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles[:N_CLASSES], labels[:N_CLASSES], loc="upper center", ncol=N_CLASSES, frameon=False)

    mode = "drift_intervals" if USE_DRIFT_INTERVALS else f"{N_EQUAL_SEGMENTS} equal segments"
    fig.suptitle(
        f"RandomRBFDrift incremental g00 — Small Multiples (PCA 2D, stride={STRIDE}, {mode})",
        y=1.05,
    )
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print(f"已儲存: {out_path}")


if __name__ == "__main__":
    main()

