"""
Run ECPF on one recurring-drift CSV file.

Example:
  python run_ecpf_recurring.py \
    --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
    --warm-start 200
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.config import PipelineConfig
from src.pipeline import load_recurring_stream_pair, ConceptDriftPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ECPF on one recurring CSV stream.")
    parser.add_argument("--csv", required=True, help="Path to recurring CSV file.")
    parser.add_argument(
        "--drift-times",
        default=None,
        help="Optional drift times txt path. If omitted, *_drift_times.txt is inferred.",
    )
    parser.add_argument("--warm-start", type=int, default=200, help="Warm-start sample count.")
    parser.add_argument(
        "--signal-mode",
        choices=["oracle_60", "detector", "meta_ecpf_dwm", "meta_ecpf_hier_parallel"],
        default="oracle_60",
        help="ECPF warning/drift signal source.",
    )
    parser.add_argument(
        "--uq-mode",
        choices=["mi_like", "vote_disagreement", "predictive_entropy"],
        default="mi_like",
        help="UQ proxy mode used by meta_ecpf_dwm.",
    )
    parser.add_argument(
        "--detector-type",
        choices=["adwin_dual"],
        default="adwin_dual",
        help="Standalone detector type when --signal-mode detector.",
    )
    parser.add_argument("--detector-delta", type=float, default=0.05, help="Detector delta.")
    parser.add_argument("--detector-delta-w", type=float, default=0.1, help="Detector warning delta.")
    parser.add_argument("--detector-min-instances", type=int, default=30, help="Detector warmup instances.")
    parser.add_argument("--plot-path", default="outputs/ecpf_timeline.png", help="Output PNG path.")
    parser.add_argument("--events-csv", default="outputs/ecpf_events.csv", help="Output event CSV path.")
    parser.add_argument(
        "--max-steps",
        type=int,
        default=0,
        help="If >0, run only first N rows (debug).",
    )
    parser.add_argument(
        "--model-type",
        choices=["ht", "hf"],
        default=None,
        help="Streaming model backend. Defaults to hf for UQ/meta modes, otherwise ht.",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    X, y, drift_times = load_recurring_stream_pair(str(csv_path), args.drift_times)
    if args.max_steps > 0:
        n = min(args.max_steps, len(y))
        X = X[:n]
        y = y[:n]
        drift_times = [t for t in drift_times if t < n]

    if len(y) <= args.warm_start:
        raise ValueError(
            f"warm-start ({args.warm_start}) must be < dataset size ({len(y)})."
        )

    model_type = args.model_type or (
        "hf" if args.signal_mode in {"meta_ecpf_dwm", "meta_ecpf_hier_parallel", "uq_warning"} else "ht"
    )

    cfg = PipelineConfig(
        use_ecpf=True,
        model_type=model_type,
        ecpf_signal_mode=args.signal_mode,
        ecpf_oracle_true_drift_times=drift_times if args.signal_mode == "oracle_60" else None,
        ecpf_uq_mode=args.uq_mode,
        ecpf_warning_length=60,
        ecpf_max_pool_size=10,
        ecpf_detector_type=args.detector_type,
        detector_delta=args.detector_delta,
        detector_delta_w=args.detector_delta_w,
        ecpf_detector_min_instances=args.detector_min_instances,
    )

    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[: args.warm_start], y[: args.warm_start])

    y_pred = np.full(len(y), np.nan, dtype=float)
    drift_events = 0
    event_rows = []
    pool_alive_series = np.zeros(len(y), dtype=int)
    for i in range(args.warm_start, len(y)):
        yp, dets, drift = pipe.step(X[i], y[i], index=i)
        y_pred[i] = yp
        if pipe._ecpf is not None:
            pool_alive_series[i] = sum(1 for s in pipe._ecpf.slots if s is not None)
        if drift:
            drift_events += len(dets)
            for d in dets:
                row = {
                    "timestamp": int(d.timestamp),
                    "source": d.detector_source,
                    "drift_type": d.drift_type.value,
                    "ecpf_protocol": d.details.get("ecpf_protocol"),
                    "uq_mode": d.details.get("uq_mode"),
                    "uq_raw": d.details.get("uq_raw"),
                    "uq_smoothed": d.details.get("uq_smoothed"),
                    "buffer_len": d.details.get("buffer_len"),
                    "pool_size": d.details.get("collection_size"),
                    "best_idx": d.details.get("best_idx"),
                    "acc_current_on_warning": d.details.get("acc_current_on_warning"),
                    "acc_best_on_warning": d.details.get("acc_best_on_warning"),
                    "acc_new_on_warning": d.details.get("acc_new_on_warning"),
                }
                event_rows.append(row)
                print(
                    f"[event] t={row['timestamp']} src={row['source']} "
                    f"buf={row['buffer_len']} pool={row['pool_size']} "
                    f"acc(cur/best/new)=({row['acc_current_on_warning']},"
                    f"{row['acc_best_on_warning']},{row['acc_new_on_warning']})"
                )

    valid = ~np.isnan(y_pred)
    acc = float(np.mean((y_pred[valid] == y[valid]).astype(np.float64))) if np.any(valid) else 0.0
    alive = 0
    if pipe._ecpf is not None:
        alive = sum(1 for s in pipe._ecpf.slots if s is not None)

    print("Run complete")
    print(f"csv: {csv_path}")
    print(f"samples: {len(y)}")
    print(f"model type: {model_type}")
    if args.signal_mode == "oracle_60":
        print(f"oracle drift starts loaded: {len(drift_times)}")
    if args.signal_mode in {"meta_ecpf_dwm", "meta_ecpf_hier_parallel"}:
        print(f"uq mode: {args.uq_mode}")
    print(f"detected drift events: {drift_events}")
    print(f"pool alive snapshots: {alive}")
    print(f"prequential accuracy (post-warm-start): {acc:.4f}")
    if args.signal_mode == "detector":
        print(f"signal mode: detector ({args.detector_type})")

    # Persist event log
    out_events = Path(args.events_csv)
    out_events.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(event_rows).to_csv(out_events, index=False)
    print(f"events csv: {out_events}")

    # Visualization
    out_plot = Path(args.plot_path)
    out_plot.parent.mkdir(parents=True, exist_ok=True)
    roll = pd.Series((y_pred == y).astype(float))
    roll[~valid] = np.nan
    roll_acc = roll.rolling(window=500, min_periods=50).mean().to_numpy()

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    axes[0].plot(roll_acc, label="Rolling accuracy (window=500)", color="tab:blue")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_ylim(0.0, 1.0)
    for r in event_rows:
        axes[0].axvline(r["timestamp"], color="tab:red", alpha=0.4, linestyle="--")
    axes[0].legend(loc="lower right")
    axes[0].set_title("ECPF timeline")

    axes[1].plot(pool_alive_series, color="tab:green", label="Alive pool snapshots")
    axes[1].set_ylabel("Pool size")
    axes[1].set_xlabel("Time index")
    axes[1].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(out_plot, dpi=150)
    plt.close(fig)
    print(f"plot: {out_plot}")


if __name__ == "__main__":
    main()
