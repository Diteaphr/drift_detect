"""
Integration test: compare all model backends on the same drift stream.
Generates a per-model performance visualization for the 4 advanced models.

Usage:
    python test_integration.py
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import PipelineConfig, DriftType
from src.pipeline import ConceptDriftPipeline
from generate_drift_dataset import create_complex_drift_stream
from tests.evaluation import evaluate_detectors, prediction_metrics


DRIFT_AT = [2500, 5000, 8000]
N_SAMPLES = 10_000
WARM_START = 50

MODEL_CONFIGS = [
    # (display_name, model_type, model_kwargs)
    ("Linear (SGD)",       "linear",    {}),
    ("Nonlinear (GNB)",    "nonlinear", {}),
    ("Elastic Net",        "elastic",   {}),
    ("Random Forest (ARF)","rf",        {"n_models": 10, "seed": 42}),
    ("XGBoost",            "xgb",       {"buffer_size": 50, "num_boost_round": 20}),
    ("GRU",                "gru",       {"input_size": 3, "hidden_size": 32, "window_size": 10}),
]

ADVANCED_CONFIGS = [c for c in MODEL_CONFIGS if c[1] in ("elastic", "rf", "xgb", "gru")]


def run_one(name, model_type, model_kwargs, X, y):
    config = PipelineConfig(
        model_type=model_type,
        model_kwargs=model_kwargs,
        sudden_window_size=50,
        gradual_window_size=100,
        update_batch_size=1500,
        recurrence_threshold=0.15,
    )
    pipeline = ConceptDriftPipeline(config=config)
    pipeline.warm_start(X[:WARM_START], y[:WARM_START])

    y_pred = np.full(N_SAMPLES, np.nan)
    t0 = time.perf_counter()
    for i in range(WARM_START, N_SAMPLES):
        yp, _, _ = pipeline.step(X[i], y[i], index=i)
        y_pred[i] = yp
    elapsed = time.perf_counter() - t0

    ev = evaluate_detectors(pipeline.detections, ground_truth_drift_times=DRIFT_AT, tolerance=300)
    m = prediction_metrics(y, y_pred, window=100)

    detections_summary = []
    for d in pipeline.detections:
        detections_summary.append(f"t={d.timestamp} ({d.drift_type.value})")

    return {
        "name": name,
        "model_type": model_type,
        "y_pred": y_pred,
        "detections_raw": pipeline.detections,
        "detections": len(pipeline.detections),
        "det_list": detections_summary,
        "precision": ev.get("precision", 0),
        "recall": ev.get("recall", 0),
        "f1": ev.get("f1", 0),
        "mae": m["mae"],
        "elapsed": elapsed,
    }


def plot_advanced_models(results, y_true, rolling_window=100):
    """Generate a 4-subplot figure showing each advanced model's real-time performance."""

    advanced = [r for r in results if r.get("model_type") in ("elastic", "rf", "xgb", "gru")]
    if not advanced:
        return

    colors = {
        "elastic": "#2196F3",
        "rf":      "#4CAF50",
        "xgb":     "#FF9800",
        "gru":     "#9C27B0",
    }
    drift_styles = {
        DriftType.SUDDEN:    {"color": "#E53935", "marker": "v", "label": "Sudden"},
        DriftType.GRADUAL:   {"color": "#FB8C00", "marker": "s", "label": "Gradual"},
        DriftType.RECURRING: {"color": "#43A047", "marker": "D", "label": "Recurring"},
    }

    fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True)
    fig.suptitle("Advanced Models — Real-time Performance During Concept Drift",
                 fontsize=15, fontweight="bold", y=0.98)

    for ax, r in zip(axes, advanced):
        mtype = r["model_type"]
        name = r["name"]
        y_pred = r["y_pred"]
        clr = colors[mtype]

        # --- Rolling accuracy ---
        correct = np.full(N_SAMPLES, np.nan)
        for i in range(N_SAMPLES):
            if not np.isnan(y_pred[i]):
                correct[i] = 1.0 if y_pred[i] == y_true[i] else 0.0

        rolling_acc = np.full(N_SAMPLES, np.nan)
        for i in range(rolling_window, N_SAMPLES):
            window = correct[i - rolling_window : i]
            valid = window[~np.isnan(window)]
            if len(valid) > 0:
                rolling_acc[i] = np.mean(valid)

        ax.plot(rolling_acc, color=clr, linewidth=1.2, alpha=0.9,
                label=f"Rolling Accuracy (w={rolling_window})")

        # --- Ground truth drift lines ---
        ax.axvline(x=2500, color="#E53935", linestyle="--", linewidth=0.9, alpha=0.7)
        ax.axvspan(4500, 5500, color="#FB8C00", alpha=0.08)
        ax.axvline(x=5000, color="#FB8C00", linestyle="--", linewidth=0.9, alpha=0.7)
        ax.axvline(x=8000, color="#43A047", linestyle="--", linewidth=0.9, alpha=0.7)

        # --- Detection markers ---
        plotted_types = set()
        for d in r["detections_raw"]:
            dt = d.drift_type
            style = drift_styles.get(dt, {"color": "gray", "marker": "o", "label": dt.value})
            lbl = f"Detected: {style['label']}" if dt not in plotted_types else None
            plotted_types.add(dt)
            acc_at = rolling_acc[d.timestamp] if d.timestamp < len(rolling_acc) and not np.isnan(rolling_acc[d.timestamp]) else 0.5
            ax.plot(d.timestamp, acc_at, marker=style["marker"], color=style["color"],
                    markersize=10, markeredgecolor="black", markeredgewidth=0.8,
                    zorder=5, label=lbl)

        # --- Rolling MAE (secondary y-axis) ---
        ax2 = ax.twinx()
        errors = np.full(N_SAMPLES, np.nan)
        for i in range(N_SAMPLES):
            if not np.isnan(y_pred[i]):
                errors[i] = abs(y_true[i] - y_pred[i])

        rolling_mae = np.full(N_SAMPLES, np.nan)
        for i in range(rolling_window, N_SAMPLES):
            window = errors[i - rolling_window : i]
            valid = window[~np.isnan(window)]
            if len(valid) > 0:
                rolling_mae[i] = np.mean(valid)

        ax2.fill_between(range(N_SAMPLES), rolling_mae, alpha=0.12, color=clr)
        ax2.plot(rolling_mae, color=clr, linewidth=0.6, alpha=0.4, linestyle=":")
        ax2.set_ylim(0, 0.7)
        ax2.set_ylabel("Rolling MAE", fontsize=9, color=clr, alpha=0.6)
        ax2.tick_params(axis="y", labelsize=8, colors=clr)

        # --- Formatting ---
        ax.set_ylim(0.2, 1.05)
        ax.set_ylabel("Accuracy", fontsize=10)
        ax.set_title(f"{name}    (MAE={r['mae']:.4f},  Detections={r['detections']},  Time={r['elapsed']:.1f}s)",
                     fontsize=11, loc="left", pad=6)
        ax.legend(loc="lower left", fontsize=8, framealpha=0.8)
        ax.grid(True, alpha=0.2)

    axes[-1].set_xlabel("Sample Index", fontsize=11)

    # --- Shared legend for ground truth ---
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = [
        Line2D([0], [0], color="#E53935", linestyle="--", linewidth=1, label="Ground Truth: Sudden (t=2500)"),
        Patch(facecolor="#FB8C00", alpha=0.15, label="Ground Truth: Gradual Zone (t=4500~5500)"),
        Line2D([0], [0], color="#43A047", linestyle="--", linewidth=1, label="Ground Truth: Recurring (t=8000)"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=3, fontsize=9,
              framealpha=0.9, bbox_to_anchor=(0.5, 0.005))

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    out_path = "advanced_models_performance.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nVisualization saved: {out_path}")


def main():
    print("=" * 70)
    print("  Integration Test — All Model Backends on Same Drift Stream")
    print("=" * 70)

    print(f"\nGenerating stream: {N_SAMPLES} samples, drift at {DRIFT_AT} ...")
    X, y, _ = create_complex_drift_stream(n_samples=N_SAMPLES, seed=42)
    print(f"Features: {X.shape[1]}, Classes: {len(np.unique(y))}\n")

    results = []
    for name, mtype, mkwargs in MODEL_CONFIGS:
        print(f"Running [{name}] ...", end=" ", flush=True)
        try:
            r = run_one(name, mtype, mkwargs, X, y)
            results.append(r)
            print(f"done ({r['elapsed']:.1f}s)")
        except Exception as e:
            print(f"FAILED: {e}")
            results.append({"name": name, "error": str(e)})

    # --- Report ---
    print("\n" + "=" * 70)
    print(f"  {'Model':<22} {'MAE':>7} {'Dets':>5} {'Prec':>6} {'Rec':>6} {'F1':>6} {'Time':>7}")
    print("-" * 70)
    for r in results:
        if "error" in r:
            print(f"  {r['name']:<22} {'ERROR':>7}")
            continue
        print(
            f"  {r['name']:<22} "
            f"{r['mae']:>7.4f} "
            f"{r['detections']:>5} "
            f"{r['precision']:>6.3f} "
            f"{r['recall']:>6.3f} "
            f"{r['f1']:>6.3f} "
            f"{r['elapsed']:>6.1f}s"
        )
    print("=" * 70)

    print("\nDetection details:")
    for r in results:
        if "error" in r:
            continue
        if r["det_list"]:
            print(f"  [{r['name']}]: {', '.join(r['det_list'])}")
        else:
            print(f"  [{r['name']}]: (no detections)")

    # --- Plot advanced models ---
    plot_advanced_models(results, y)

    print("\nDone.")


if __name__ == "__main__":
    main()
