"""Visualize standalone calibration results."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "outputs" / "calibration_standalone_run.log"
CSV_PATH = ROOT / "outputs" / "calibration_standalone" / "calibration_standalone_summary.csv"
OUT_DIR = ROOT / "outputs" / "calibration_standalone"

COLORS = {"adwin": "#4C72B0", "seqdrift2": "#DD8452"}
PARAM_COLORS = {"warning": "#E64B35", "confirm": "#3182BD"}


# ---------------------------------------------------------------------------
# Parse log
# ---------------------------------------------------------------------------

def parse_calib_log(log_path: Path) -> pd.DataFrame:
    pattern = re.compile(
        r"\[calib\]\s+(\w+)\s+\|\s+([\w.]+\.csv)\s+\|\s+delta=([\d.]+)\s+"
        r"N_fire=\s*(\d+)\s+N_actual=\s*(\d+)"
    )
    rows = []
    for line in log_path.read_text().splitlines():
        m = pattern.search(line)
        if m:
            rows.append({
                "detector": m.group(1),
                "stream": m.group(2),
                "delta": float(m.group(3)),
                "N_fire": int(m.group(4)),
                "N_actual": int(m.group(5)),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Plot 1: calibration curves
# ---------------------------------------------------------------------------

def plot_calibration_curves(df: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    detectors = df["detector"].unique()
    fig, axes = plt.subplots(1, len(detectors), figsize=(13, 5), sharey=False)
    if len(detectors) == 1:
        axes = [axes]

    for ax, det in zip(axes, detectors):
        color = COLORS.get(det, "steelblue")
        sub = df[df["detector"] == det]

        # per-stream lines (thin, transparent)
        for stream, grp in sub.groupby("stream"):
            grp_s = grp.sort_values("delta")
            ax.plot(grp_s["delta"], grp_s["N_fire"],
                    color=color, alpha=0.25, linewidth=1.2)

        # mean N_fire across streams per delta
        mean_fires = sub.groupby("delta")["N_fire"].mean()
        ax.plot(mean_fires.index, mean_fires.values,
                color=color, linewidth=2.5, label="mean N_fire", zorder=5)

        # mean N_actual line
        mean_actual = sub["N_actual"].mean()
        ax.axhline(mean_actual, color="black", linestyle="--",
                   linewidth=1.5, label=f"mean N_actual ({mean_actual:.1f})")

        # mark warning and confirm params
        row = summary[summary["detector"] == det].iloc[0]
        for ptype, col in [("warning", "warning_param"), ("confirm", "confirm_param")]:
            p = float(row[col])
            n = float(mean_fires.get(p, mean_fires.iloc[0]))
            ax.axvline(p, color=PARAM_COLORS[ptype], linestyle=":",
                       linewidth=2, alpha=0.8)
            ax.scatter([p], [n], color=PARAM_COLORS[ptype], s=90, zorder=6,
                       label=f"{ptype}_param={p}")

        ax.set_title(f"{det}", fontsize=13, fontweight="bold")
        ax.set_xlabel("delta", fontsize=11)
        ax.set_ylabel("N_fires", fontsize=11)
        ax.legend(fontsize=8.5)
        ax.grid(True, alpha=0.3)

        # x-axis: show all grid values
        deltas = sorted(sub["delta"].unique())
        ax.set_xticks(deltas)
        ax.set_xticklabels([str(d) for d in deltas], rotation=45, fontsize=8)

    fig.suptitle("Calibration Sweep: N_fires vs delta\n(thin lines = individual streams, bold = mean)",
                 fontsize=12)
    plt.tight_layout()
    out = out_dir / "calibration_curves.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Plot 2: metrics comparison bar chart
# ---------------------------------------------------------------------------

def plot_metrics_comparison(summary: pd.DataFrame, out_dir: Path) -> None:
    metrics = [
        ("warn_count_score", "conf_count_score", "Count Score\n(1 − |N_fire−N_actual|/N_actual)", False),
        ("warn_CD%",         "conf_CD%",          "CD%\n(Correct Detection %)",                   False),
        ("warn_avg_delay",   "conf_avg_delay",     "Avg Detection Delay\n(samples, lower = better)", True),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13, 5))

    x = np.arange(len(summary))
    width = 0.35
    detectors = summary["detector"].tolist()
    bar_colors = [COLORS.get(d, "gray") for d in detectors]

    for ax, (warn_col, conf_col, ylabel, invert) in zip(axes, metrics):
        warn_vals = pd.to_numeric(summary[warn_col], errors="coerce").fillna(0).tolist()
        conf_vals = pd.to_numeric(summary[conf_col], errors="coerce").fillna(0).tolist()

        b1 = ax.bar(x - width/2, warn_vals, width, label="warning param",
                    color=[PARAM_COLORS["warning"]] * len(x), alpha=0.85, edgecolor="white")
        b2 = ax.bar(x + width/2, conf_vals, width, label="confirm param",
                    color=[PARAM_COLORS["confirm"]] * len(x), alpha=0.85, edgecolor="white")

        # hatch by detector
        hatches = ["", "//"]
        for bars, hatch in zip([b1, b2], hatches):
            for bar in bars:
                bar.set_hatch(hatch)

        ax.set_xticks(x)
        ax.set_xticklabels(detectors, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(ylabel.split("\n")[0], fontsize=11, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(True, axis="y", alpha=0.3)

        # value labels on bars
        for bar in list(b1) + list(b2):
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h + max(h * 0.02, 0.005),
                        f"{h:.1f}", ha="center", va="bottom", fontsize=8.5)

    # legend patches for detector colours
    patches = [mpatches.Patch(color=COLORS[d], label=d) for d in COLORS if d in detectors]
    fig.legend(handles=patches, loc="lower center", ncol=2,
               fontsize=10, title="Detector", bbox_to_anchor=(0.5, -0.04))

    fig.suptitle("Evaluation Metrics: adwin vs seqdrift2\n(warning param vs confirm param, g05–g09)",
                 fontsize=12)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out = out_dir / "metrics_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = parse_calib_log(LOG_PATH)
    summary = pd.read_csv(CSV_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    plot_calibration_curves(df, summary, OUT_DIR)
    plot_metrics_comparison(summary, OUT_DIR)
    print("Done.")
