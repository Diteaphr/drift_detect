"""
Visualize per-stream drift detection on evaluation streams (g05-g09).

For each stream × detector:
  - smoothed error rate
  - ground-truth drift intervals (grey shading)
  - warning_param detections  (red  vertical lines)
  - confirm_param detections  (blue vertical lines)

Layout: 2 rows (adwin / seqdrift2) × 5 columns (g05–g09)
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.calibrate_standalone_detectors import (
    DETECTORS, EVAL_SUFFIXES, HF_KWARGS, WARM_START,
    _stream_paths, _load_stream, _run_detector,
)
from src.models.hoeffding_forest import HoeffdingForestModel

OUT_DIR = ROOT / "outputs" / "calibration_standalone"

# Calibrated params from experiment
PARAMS = {
    "adwin":     {"warning": 0.05,  "confirm": 0.02},
    "seqdrift2": {"warning": 0.25,  "confirm": 0.20},
}

COLORS = {"warning": "#E64B35", "confirm": "#3182BD"}
SMOOTH_WINDOW = 500   # samples for moving-average error rate


def _smooth(errors: np.ndarray, w: int) -> np.ndarray:
    kernel = np.ones(w) / w
    return np.convolve(errors, kernel, mode="same")


def _build_error_stream(X, y):
    """Run hf model → return (errors array starting at WARM_START, absolute indices)."""
    model = HoeffdingForestModel(**HF_KWARGS)
    errors = []
    for i in range(len(y)):
        x_dict = {f"f{j}": float(v) for j, v in enumerate(X[i])}
        y_true = int(y[i])
        if i < WARM_START:
            model.learn_one(x_dict, y_true)
            continue
        y_pred = model.predict_one(x_dict)
        err = 1.0 if (y_pred is None or int(y_pred) != y_true) else 0.0
        model.learn_one(x_dict, y_true)
        errors.append(err)
    return np.array(errors)


def main():
    eval_paths = _stream_paths(EVAL_SUFFIXES)
    spec_map = {s.name: s for s in DETECTORS}

    n_streams = len(eval_paths)
    n_detectors = len(DETECTORS)
    fig, axes = plt.subplots(
        n_detectors, n_streams,
        figsize=(4.5 * n_streams, 3.5 * n_detectors),
        sharey=False,
    )

    for col, (csv_path, txt_path) in enumerate(eval_paths):
        print(f"Processing {csv_path.name}...", flush=True)
        X, y, drift_starts, drift_intervals = _load_stream(csv_path, txt_path)
        errors = _build_error_stream(X, y)
        smoothed = _smooth(errors, SMOOTH_WINDOW)
        t = np.arange(WARM_START, WARM_START + len(errors))  # absolute sample index

        for row, spec in enumerate(DETECTORS):
            ax = axes[row][col]
            params = PARAMS[spec.name]

            # error rate (smoothed)
            ax.plot(t, smoothed, color="grey", linewidth=0.8, alpha=0.6, label="error rate")

            # ground truth drift intervals (shading)
            for s, e in drift_intervals:
                ax.axvspan(s, e, color="lightgreen", alpha=0.35,
                           label="drift interval" if s == drift_intervals[0][0] else "")

            # detections at warning and confirm param
            for ptype, color in COLORS.items():
                delta = params[ptype]
                fires = _run_detector(X, y, delta, spec)
                for ft in fires:
                    ax.axvline(ft, color=color, linewidth=1.0,
                               alpha=0.75, linestyle="-")
                # invisible scatter for legend
                ax.scatter([], [], color=color, marker="|", s=100,
                           label=f"{ptype} (δ={delta})")

            # formatting
            stream_label = csv_path.stem.replace("recurring_sud_sea100k_", "")
            if row == 0:
                ax.set_title(stream_label, fontsize=10, fontweight="bold")
            if col == 0:
                ax.set_ylabel(spec.name, fontsize=10, fontweight="bold")
            ax.set_xlabel("sample index", fontsize=8)
            ax.tick_params(labelsize=7)
            ax.set_xlim(t[0], t[-1])
            ax.set_ylim(-0.02, max(smoothed) * 1.8)

            if row == 0 and col == 0:
                ax.legend(fontsize=7, loc="upper right")

    # shared legend at bottom
    legend_handles = [
        mpatches.Patch(color="lightgreen", alpha=0.6, label="ground truth drift"),
        plt.Line2D([0], [0], color=COLORS["warning"], linewidth=1.5,
                   label=f"warning param detections"),
        plt.Line2D([0], [0], color=COLORS["confirm"], linewidth=1.5,
                   label=f"confirm param detections"),
        plt.Line2D([0], [0], color="grey", linewidth=1.2, alpha=0.6,
                   label=f"smoothed error rate (w={SMOOTH_WINDOW})"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=4,
               fontsize=9, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle(
        "Drift Detection Timeline — Evaluation Streams g05–g09\n"
        "adwin (top) vs seqdrift2 (bottom)  |  red=warning param  blue=confirm param",
        fontsize=11,
    )
    plt.tight_layout(rect=[0, 0.04, 1, 0.97])

    out = OUT_DIR / "detection_timeline.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
