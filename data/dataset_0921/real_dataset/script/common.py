"""Shared paths and helpers for real_dataset preparation."""

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

# Cap long streams so CSV stays under GitHub's ~100MB single-file limit.
MAX_STREAM_ROWS = 100_000


def ensure_layout() -> None:
    for task, names in {
        "binary": ["ai4i2020", "electricity", "airlines"],
        "multi_classification": ["gas_sensor_drift", "covertype"],
        "regression": ["metro_interstate_traffic", "bike_sharing"],
    }.items():
        (ROOT / task / "drift_plots").mkdir(parents=True, exist_ok=True)
        for name in names:
            (ROOT / task / name).mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def cap_stream_rows(df: pd.DataFrame, max_n: int = MAX_STREAM_ROWS) -> tuple[pd.DataFrame, int | None]:
    """Keep the first max_n rows (preserve stream order). Returns (df, original_n or None)."""
    n = len(df)
    if n <= max_n:
        return df.reset_index(drop=True), None
    return df.iloc[:max_n].reset_index(drop=True), n


def to_x_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename feature columns to x0..xK (y must already be present)."""
    assert "y" in df.columns
    feats = [c for c in df.columns if c != "y"]
    out = df[feats + ["y"]].copy()
    rename = {c: f"x{i}" for i, c in enumerate(feats)}
    return out.rename(columns=rename)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_meta(path: Path, payload: dict[str, Any]) -> None:
    payload = {**payload, "prepared_date": str(date.today())}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_df(df: pd.DataFrame, task: str, name: str) -> None:
    if "y" not in df.columns:
        raise AssertionError(f"{name}: missing y")
    if df.shape[0] < 1 or df.shape[1] < 2:
        raise AssertionError(f"{name}: empty or no features")
    if df.isna().any().any():
        raise AssertionError(f"{name}: contains NaN")
    y = df["y"]
    if task == "binary":
        nuniq = y.nunique()
        if nuniq != 2:
            raise AssertionError(f"{name}: binary y has {nuniq} unique values")
    elif task == "multi_classification":
        if not np.issubdtype(y.dtype, np.integer) and not set(y.unique()).issubset(set(range(-1, 1000))):
            # allow int-like floats
            if not np.allclose(y.to_numpy(), np.round(y.to_numpy())):
                raise AssertionError(f"{name}: multi y not integer-like")
    elif task == "regression":
        if y.nunique() <= 5:
            raise AssertionError(f"{name}: regression y looks discrete ({y.nunique()} unique)")


def adaptive_window(n: int, default: int = 500) -> int:
    if n < 100:
        return max(5, n // 10)
    return max(50, min(default, n // 20))


def causal_rolling_mean(y: np.ndarray, w: int) -> np.ndarray:
    """Mean of the previous up-to-w samples ending at t (no lookahead)."""
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


def plot_y(df: pd.DataFrame, out_png: Path, *, task: str, title: str) -> None:
    y = df["y"].to_numpy(dtype=float)
    n = len(y)
    w = adaptive_window(n)
    fig, ax = plt.subplots(figsize=(12, 3.4))

    if task == "multi_classification":
        classes = sorted(pd.unique(df["y"]))
        # limit legend clutter
        show = classes if len(classes) <= 8 else classes[:8]
        for c in show:
            ind = (df["y"].to_numpy() == c).astype(float)
            roll = causal_rolling_mean(ind, w)
            ax.plot(np.arange(len(roll)), roll, linewidth=0.9, label=f"class {c}")
        ax.set_ylabel(f"causal rolling class proportion (prev w={w})")
        ax.legend(loc="upper right", fontsize=8, ncol=min(4, len(show)))
        ax.set_ylim(-0.02, 1.02)
    else:
        roll = causal_rolling_mean(y, w)
        color = "darkgreen" if task == "regression" else "steelblue"
        ax.plot(np.arange(len(roll)), roll, color=color, linewidth=0.8)
        ylab = (
            f"causal rolling mean y (prev w={w})"
            if task == "regression"
            else f"causal rolling mean label (prev w={w})"
        )
        ax.set_ylabel(ylab)

    ax.set_title(title)
    ax.set_xlabel("t")
    ax.set_xlim(0, max(n - 1, 1))
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=120)
    plt.close(fig)


def rolling_download(url: str, dest: Path, timeout: int = 120) -> Path:
    """Download url to dest if missing."""
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "drift_detect/real_dataset"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    return dest
