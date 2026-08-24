"""
Regression drift validation plots for g00 (Friedman-style regression).

Outputs (in this folder):
- regression_y_violin_g00.png: segmented y distribution (violin) per drift segment
- regression_y_box_g00.png: segmented y distribution (boxplot) per drift segment
- regression_y_rolling_mean_std_g00.png: rolling mean + rolling std band over time

The plots are meant to be a quick, *direct* look at how the generated target y changes
over time, which is especially relevant for concept drift in y|x (e.g. coefficient drift).
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

WINDOW = 2000

PROFILES = ("sudden", "gradual", "incremental")
G_TAG = "g00"


def load_drift_intervals(path: Path) -> list[list[int]]:
    if not path.is_file():
        return []
    return ast.literal_eval(path.read_text(encoding="utf-8").strip())


def segments_from_intervals(intervals: list[list[int]], n: int) -> list[tuple[int, int, str]]:
    """
    Convert drift intervals [[s,e], ...] to contiguous segments:
    [0, s1), [s1, e1+1), [e1+1, s2), [s2, e2+1), ..., [last_end+1, n)
    """
    cleaned: list[tuple[int, int]] = []
    for pair in intervals:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            continue
        s, e = int(pair[0]), int(pair[1])
        if s > e:
            s, e = e, s
        s = max(0, s)
        e = min(n - 1, e)
        if s <= e:
            cleaned.append((s, e))
    cleaned.sort(key=lambda t: t[0])

    segs: list[tuple[int, int, str]] = []
    cur = 0
    for i, (s, e) in enumerate(cleaned):
        if cur < s:
            segs.append((cur, s, f"stable_{len(segs)}"))
        segs.append((s, e + 1, f"drift_{i}"))
        cur = e + 1
    if cur < n:
        segs.append((cur, n, f"stable_{len(segs)}"))
    return segs


def plot_segment_violin(y: np.ndarray, segs: list[tuple[int, int, str]], title: str, out_path: Path) -> None:
    data = []
    labels = []
    for s, e, name in segs:
        if e - s <= 1:
            continue
        data.append(y[s:e])
        labels.append(f"{name}\n[{s},{e})")

    fig, ax = plt.subplots(figsize=(max(10, 1.8 * len(data)), 5))
    parts = ax.violinplot(data, showmeans=True, showextrema=True, widths=0.9)
    for pc in parts.get("bodies", []):
        pc.set_alpha(0.7)
        pc.set_facecolor("#4C78A8")

    ax.set_title(title)
    ax.set_ylabel("y")
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


def plot_segment_box(y: np.ndarray, segs: list[tuple[int, int, str]], title: str, out_path: Path) -> None:
    data = []
    labels = []
    for s, e, name in segs:
        if e - s <= 1:
            continue
        data.append(y[s:e])
        labels.append(f"{name}\n[{s},{e})")

    fig, ax = plt.subplots(figsize=(max(10, 1.8 * len(data)), 5))
    ax.boxplot(
        data,
        showfliers=False,
        patch_artist=True,
        boxprops=dict(facecolor="#72B7B2", alpha=0.75),
        medianprops=dict(color="#222222", linewidth=1.2),
        whiskerprops=dict(color="#555555"),
        capprops=dict(color="#555555"),
    )
    ax.set_title(title)
    ax.set_ylabel("y")
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


def plot_rolling_mean_std(y: np.ndarray, intervals: list[list[int]], title: str, out_path: Path) -> None:
    s = pd.Series(y)
    mu = s.rolling(WINDOW, min_periods=1).mean()
    sd = s.rolling(WINDOW, min_periods=1).std().fillna(0.0)

    x = np.arange(len(y))
    fig, ax = plt.subplots(figsize=(14, 5.8))
    ax.plot(x, mu.to_numpy(), color="#1f77b4", linewidth=1.2, label=f"rolling mean (w={WINDOW})")
    ax.fill_between(
        x,
        (mu - sd).to_numpy(),
        (mu + sd).to_numpy(),
        color="#1f77b4",
        alpha=0.18,
        label="±1 rolling std",
    )

    for pair in intervals:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            continue
        ds, de = int(pair[0]), int(pair[1])
        if ds > de:
            ds, de = de, ds
        center = (ds + de) // 2
        ax.axvline(center, color="red", linestyle="--", linewidth=1.1, alpha=0.85)
        ax.axvline(ds, color="darkgreen", linestyle="--", linewidth=0.9, alpha=0.7)
        ax.axvline(de, color="navy", linestyle="--", linewidth=0.9, alpha=0.7)

    ax.set_title(title)
    ax.set_xlabel("Sample index")
    ax.set_ylabel("y (rolling statistics)")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best", fontsize=9)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


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

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for profile in PROFILES:
        csv_path = (
            BASE_DIR
            / f"{profile}_drift"
            / tier
            / f"recurring_{profile}_friedman_100k_{G_TAG}.csv"
        )
        dt_path = (
            BASE_DIR
            / f"{profile}_drift"
            / tier
            / f"recurring_{profile}_friedman_100k_{G_TAG}_drift_times.txt"
        )

        df = pd.read_csv(csv_path)
        if "y" not in df.columns:
            raise ValueError(f"{csv_path} 缺少 y 欄位")
        y = df["y"].to_numpy(dtype=float)
        intervals = load_drift_intervals(dt_path)
        segs = segments_from_intervals(intervals, len(df))

        plot_segment_violin(
            y,
            segs,
            title=f"Regression ({profile}) {tier} {G_TAG} — y distribution by segment",
            out_path=OUT_DIR / f"regression_{profile}_y_violin_{tier}_{G_TAG}.png",
        )
        plot_segment_box(
            y,
            segs,
            title=f"Regression ({profile}) {tier} {G_TAG} — y distribution by segment (box)",
            out_path=OUT_DIR / f"regression_{profile}_y_box_{tier}_{G_TAG}.png",
        )
        plot_rolling_mean_std(
            y,
            intervals,
            title=f"Regression ({profile}) {tier} {G_TAG} — rolling mean/std of y (w={WINDOW})",
            out_path=OUT_DIR / f"regression_{profile}_y_rolling_mean_std_{tier}_{G_TAG}.png",
        )

        print(f"已輸出 {profile}：{G_TAG}")


if __name__ == "__main__":
    main()

