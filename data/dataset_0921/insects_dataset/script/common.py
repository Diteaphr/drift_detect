"""Shared helpers for insects_dataset (real Insects streams with known drift points)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
RAW_DIR = ROOT / "_raw"

# Folder / file keys aligned with Souza et al. 2020 Table 2 (balanced only).
# Paper lists stream positions used as sample indices for drift_times.
CHANGE_POINTS: dict[str, list[int]] = {
    "incremental_balanced": [],
    "abrupt_balanced": [14352, 19500, 33240, 38682, 39510],
    "incremental_gradual_balanced": [14028],
    "incremental_abrupt_reoccurring_balanced": [26568, 53364],
    "incremental_reoccurring_balanced": [26568, 53364],
}

PAPER_NAME: dict[str, str] = {
    "incremental_balanced": "Incremental (bal.)",
    "abrupt_balanced": "Abrupt (bal.)",
    "incremental_gradual_balanced": "Incremental-gradual (bal.)",
    "incremental_abrupt_reoccurring_balanced": "Incremental-abrupt-reoccurring (bal.)",
    "incremental_reoccurring_balanced": "Incremental-reoccurring (bal.)",
}

# Temperature / drift-mode notes from the paper (balanced variants).
TEMPERATURE_DESC: dict[str, str] = {
    "incremental_balanced": (
        "溫度由 20°C 平滑遞增至 40°C，特徵呈現連續且緩慢的遞增型飄移；"
        "貫穿整條數據串流，無離散 change point。"
    ),
    "abrupt_balanced": (
        "包含 5 個突發切換點，將數據分為 6 個穩定的溫度概念區間（A–F）。"
    ),
    "incremental_gradual_balanced": (
        "由 37°C 遞減至 35°C 後進入漸進過渡期，35°C 與 23°C 兩種概念交替出現，"
        "過渡點在第 14,028 筆，最後完全轉為 23°C 並平滑升至 27°C。"
    ),
    "incremental_abrupt_reoccurring_balanced": (
        "包含 3 個 20°C→40°C 的遞增升溫週期，週期之間在第 26,568 與 53,364 筆"
        "發生斷崖式突發跳躍跌回 20°C。"
    ),
    "incremental_reoccurring_balanced": (
        "包含 3 個連續升降溫週期（20°C→40°C→20°C→40°C），"
        "在第 26,568 與 53,364 筆為平滑轉折點，無突發斷層。"
    ),
}

GDRIVE_IDS: dict[str, str] = {
    "incremental_balanced": "1tKQ2KL4m-ACHCVKUDLFPrM4cyhioiOpu",
    "abrupt_balanced": "1WQoIuuVgiuXfzv4kvao6XuLQG37V923O",
    "incremental_gradual_balanced": "1fepYkDxwMbuoRUaG_fsymSzkuapS4vJp",
    "incremental_abrupt_reoccurring_balanced": "1-J5WIBN8_F_tomdcrOaiLCxk9nzxtFsf",
    "incremental_reoccurring_balanced": "1mSKTSsxzYMjdV005AJqrcMGajuu7dUfW",
}


def ensure_layout() -> None:
    task = ROOT / "multi_classification"
    (task / "drift_plots").mkdir(parents=True, exist_ok=True)
    for name in GDRIVE_IDS:
        (task / name).mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def points_to_intervals(points: list[int], n_samples: int) -> list[list[int]]:
    """Map discrete change points to [[t, t], ...] clipped to stream length."""
    out: list[list[int]] = []
    for p in points:
        t = int(p)
        if t < 0 or t >= n_samples:
            continue
        out.append([t, t])
    return out


def write_drift_times(path: Path, intervals: list[list[int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(repr(intervals), encoding="utf-8")


def write_meta(path: Path, payload: dict[str, Any]) -> None:
    payload = {**payload, "prepared_date": str(date.today())}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def to_x_columns(df: pd.DataFrame) -> pd.DataFrame:
    feats = [c for c in df.columns if c != "y"]
    out = df[feats + ["y"]].copy()
    return out.rename(columns={c: f"x{i}" for i, c in enumerate(feats)})


def adaptive_window(n: int, default: int = 500) -> int:
    if n < 100:
        return max(5, n // 10)
    return max(50, min(default, n // 20))


def plot_y_with_drifts(
    df: pd.DataFrame,
    intervals: list[list[int]],
    out_png: Path,
    *,
    title: str,
) -> None:
    y = df["y"].to_numpy()
    n = len(y)
    w = adaptive_window(n)
    classes = sorted(pd.unique(df["y"]))
    fig, ax = plt.subplots(figsize=(12, 3.6))
    for c in classes:
        ind = (y == c).astype(float)
        roll = np.convolve(ind, np.ones(w) / w, mode="valid")
        ax.plot(np.arange(len(roll)), roll, linewidth=0.9, label=f"class {c}")
    for s, e in intervals:
        ax.axvspan(s, e, color="coral", alpha=0.25)
        ax.axvline(s, color="coral", linestyle="--", linewidth=0.9, alpha=0.9)
    ax.set_ylabel(f"rolling class proportion (w={w})")
    ax.set_xlabel("t")
    ax.set_title(title)
    ax.set_xlim(0, n)
    ax.set_ylim(-0.02, 1.02)
    ax.legend(loc="upper right", fontsize=8, ncol=min(3, len(classes)))
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=120)
    plt.close(fig)
