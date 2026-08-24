"""
讀取 g00 的 RandomRBF 多類別 CSV，以 pandas rolling(500) 計算各類別比例，
並繪製 rolling 比例曲線 + 漂移事件／起迄標示。
輸出至本目錄（drift_validation_plots）：
- sudden / gradual：rolling 類別比例圖
- incremental：以 drift_intervals 分段，計算每段各類別特徵平均（重心），PCA→2D 後畫重心軌跡（帶方向箭頭）
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = Path(__file__).resolve().parent
WINDOW = 2000
N_CLASSES = 4

# 若無 drift_times 檔時使用的範例漂移索引（僅備援）
FALLBACK_DRIFT_CENTERS = (30_000, 60_000)


def load_drift_intervals(drift_times_path: Path) -> list[list[int]]:
    if not drift_times_path.is_file():
        return []
    text = drift_times_path.read_text(encoding="utf-8").strip()
    return ast.literal_eval(text)


def plot_rolling_proportions(
    csv_path: Path,
    drift_intervals: list[list[int]],
    title: str,
    out_path: Path,
) -> None:
    df = pd.read_csv(csv_path)
    if "y" not in df.columns:
        raise ValueError("CSV 需包含 y 欄位")

    idx = pd.Series(df.index, name="sample_index")
    for k in range(N_CLASSES):
        df[f"p{k}"] = (df["y"] == k).astype(float).rolling(WINDOW, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    for k in range(N_CLASSES):
        ax.plot(idx, df[f"p{k}"], color=colors[k], linewidth=0.9, label=f"Class {k}")

    ax.set_xlabel("Sample index")
    ax.set_ylabel("Rolling proportion (0–1)")
    ax.set_title(title)
    ax.set_ylim(0.0, 1.0)
    ax.margins(x=0)
    ax.grid(True, linestyle=":", alpha=0.6)

    for pair in drift_intervals:
        if len(pair) != 2:
            continue
        s, e = int(pair[0]), int(pair[1])
        if s > e:
            s, e = e, s
        center = (s + e) // 2
        ax.axvline(center, color="red", linestyle="--", linewidth=1.1, alpha=0.85, zorder=2)
        ax.axvline(s, color="darkgreen", linestyle="--", linewidth=0.9, alpha=0.7, zorder=2)
        ax.axvline(e, color="navy", linestyle="--", linewidth=0.9, alpha=0.7, zorder=2)

    if not drift_intervals:
        for x in FALLBACK_DRIFT_CENTERS:
            ax.axvline(x, color="red", linestyle="--", linewidth=1.1, alpha=0.85, zorder=2)

    class_handles = [
        mlines.Line2D([], [], color=colors[k], linewidth=1.5, label=f"Class {k} proportion")
        for k in range(N_CLASSES)
    ]
    drift_handles = [
        mlines.Line2D([], [], color="red", linestyle="--", linewidth=1.2, label="Drift Event (interval center)"),
        mlines.Line2D([], [], color="darkgreen", linestyle="--", linewidth=1.0, label="Drift start (interval begin)"),
        mlines.Line2D([], [], color="navy", linestyle="--", linewidth=1.0, label="Drift end (interval end)"),
    ]
    leg1 = ax.legend(handles=class_handles, loc="upper left", title="Class rolling p", fontsize=9)
    ax.add_artist(leg1)
    ax.legend(handles=drift_handles, loc="upper right", title="Drift markers", fontsize=9)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _pca_2d(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """回傳 (coords_2d, mean, components_2xD)。以 SVD 實作，避免額外依賴。"""
    if points.ndim != 2:
        raise ValueError("points 必須是 2D array")
    mu = points.mean(axis=0, keepdims=True)
    x = points - mu
    # X = U S Vt；主成分方向在 Vt
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    comps = vt[:2]  # (2, D)
    coords = x @ comps.T  # (N, 2)
    return coords, mu.ravel(), comps


def plot_incremental_centroid_trajectories_pca2d(
    csv_path: Path,
    drift_intervals: list[list[int]],
    title: str,
    out_path: Path,
) -> None:
    df = pd.read_csv(csv_path)
    if "y" not in df.columns:
        raise ValueError("CSV 需包含 y 欄位")

    feat_cols = [c for c in df.columns if c.startswith("x")]
    if not feat_cols:
        raise ValueError("CSV 需包含 x0..xN 特徵欄位")

    # 依 drift_intervals 切分；確保依起點排序且合法
    intervals = []
    for pair in drift_intervals:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            continue
        s, e = int(pair[0]), int(pair[1])
        if s > e:
            s, e = e, s
        s = max(0, s)
        e = min(len(df) - 1, e)
        if s <= e:
            intervals.append((s, e))
    intervals.sort(key=lambda x: x[0])

    if not intervals:
        raise ValueError("incremental 需要 drift_intervals 才能分段畫重心軌跡")

    # 計算每段、每類別的重心（特徵平均）
    centroids = np.full((len(intervals), N_CLASSES, len(feat_cols)), np.nan, dtype=float)
    counts = np.zeros((len(intervals), N_CLASSES), dtype=int)

    for t, (s, e) in enumerate(intervals):
        seg = df.iloc[s : e + 1]
        for k in range(N_CLASSES):
            sub = seg.loc[seg["y"] == k, feat_cols]
            counts[t, k] = int(len(sub))
            if len(sub) > 0:
                centroids[t, k] = sub.mean(axis=0).to_numpy(dtype=float)

    # 對所有有效重心做 PCA→2D
    flat = centroids.reshape(-1, centroids.shape[-1])
    valid_mask = np.isfinite(flat).all(axis=1)
    valid_points = flat[valid_mask]
    if len(valid_points) < 2:
        raise ValueError("有效重心點不足，無法做 PCA")

    coords2d, _, _ = _pca_2d(valid_points)

    # 回填到 (T, K, 2)
    coords_full = np.full((len(intervals) * N_CLASSES, 2), np.nan, dtype=float)
    coords_full[valid_mask] = coords2d
    coords_full = coords_full.reshape(len(intervals), N_CLASSES, 2)

    # 畫軌跡
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for k in range(N_CLASSES):
        pts = coords_full[:, k, :]
        ok = np.isfinite(pts).all(axis=1)
        if ok.sum() == 0:
            continue
        xs = pts[ok, 0]
        ys = pts[ok, 1]
        ax.plot(xs, ys, color=colors[k], linewidth=1.2, alpha=0.85)
        ax.scatter(xs, ys, color=colors[k], s=26, alpha=0.95, label=f"Class {k}")

        # 方向箭頭（相鄰段）
        if len(xs) >= 2:
            dx = np.diff(xs)
            dy = np.diff(ys)
            ax.quiver(
                xs[:-1],
                ys[:-1],
                dx,
                dy,
                angles="xy",
                scale_units="xy",
                scale=1,
                width=0.004,
                color=colors[k],
                alpha=0.75,
                zorder=3,
            )

        # 標註時間段 index（只標註有效點）
        seg_ids = np.arange(len(intervals))[ok]
        for sid, x, y in zip(seg_ids, xs, ys):
            ax.annotate(
                str(int(sid)),
                (x, y),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
                color=colors[k],
                alpha=0.9,
            )

    ax.set_title(title)
    ax.set_xlabel("PCA component 1")
    ax.set_ylabel("PCA component 2")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.axhline(0, color="black", linewidth=0.6, alpha=0.35)
    ax.axvline(0, color="black", linewidth=0.6, alpha=0.35)
    ax.legend(loc="best", title="Class", fontsize=9)

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

    jobs = [
        (
            "sudden",
            BASE_DIR / "sudden_drift" / tier / "recurring_sudden_rbf4_100k_g00.csv",
            BASE_DIR / "sudden_drift" / tier / "recurring_sudden_rbf4_100k_g00_drift_times.txt",
            OUT_DIR / f"rbf_rolling_proportions_sudden_{tier}_g00.png",
        ),
        (
            "gradual",
            BASE_DIR / "gradual_drift" / tier / "recurring_gradual_rbf4_100k_g00.csv",
            BASE_DIR / "gradual_drift" / tier / "recurring_gradual_rbf4_100k_g00_drift_times.txt",
            OUT_DIR / f"rbf_rolling_proportions_gradual_{tier}_g00.png",
        ),
        (
            "incremental",
            BASE_DIR / "incremental_drift" / tier / "recurring_incremental_rbf4_100k_g00.csv",
            BASE_DIR
            / "incremental_drift"
            / tier
            / "recurring_incremental_rbf4_100k_g00_drift_times.txt",
            OUT_DIR / f"rbf_rolling_proportions_incremental_{tier}_g00.png",
        ),
    ]

    for name, csv_p, dt_p, out_p in jobs:
        intervals = load_drift_intervals(dt_p)
        title = (
            f"RandomRBF ({name}) g00 — per-class rolling proportion (window={WINDOW})\n"
            f"Drift intervals: {len(intervals)}"
        )
        plot_rolling_proportions(csv_p, intervals, title, out_p)
        print(f"已儲存: {out_p}")

    # incremental：分段重心→PCA→軌跡
    inc_csv = BASE_DIR / "incremental_drift" / tier / "recurring_incremental_rbf4_100k_g00.csv"
    inc_dt = (
        BASE_DIR / "incremental_drift" / tier / "recurring_incremental_rbf4_100k_g00_drift_times.txt"
    )
    inc_out = OUT_DIR / f"rbf_incremental_centroid_pca_trajectories_{tier}_g00.png"
    inc_intervals = load_drift_intervals(inc_dt)
    inc_title = (
        "RandomRBF (incremental) g00 — per-class centroid trajectories (segment=drift_intervals)\n"
        "Centroids projected to 2D with PCA; arrows show temporal direction"
    )
    plot_incremental_centroid_trajectories_pca2d(inc_csv, inc_intervals, inc_title, inc_out)
    print(f"已儲存: {inc_out}")


if __name__ == "__main__":
    main()
