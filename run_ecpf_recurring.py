"""
Run ECPF on one recurring-drift CSV file.

Example:
  python run_ecpf_recurring.py \
    --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
    --warm-start 200

--warning-detector adwin|seed|seqdrift2
--drift-detector adwin|seed|seqdrift2
--warning-signal error|uq_mi|uq_vote|uq_entropy|uq_variance
--drift-signal error|uq_mi|uq_vote|uq_entropy|uq_variance

"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.config import PipelineConfig
from src.pipeline import load_recurring_stream_pair, load_drift_intervals_file, ConceptDriftPipeline
from src.metrics import build_perturbation_intervals, compute_correct_detection
from detectors.meta_ecpf.adwin_family import ECPFAdwinFamilyDetector
from detectors.meta_ecpf.signal_routing import SIGNAL_CHOICES


ADWIN_FAMILY_SIGNAL_MODES = [
    "detector",
    "dual_seed",
    "dual_seqdrift2",
    "hybrid_adwin_family",
    *ECPFAdwinFamilyDetector.COMBOS.keys(),
]


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
        choices=["oracle_60", *ADWIN_FAMILY_SIGNAL_MODES, "meta_ecpf_dwm", "meta_ecpf_hcdt", "meta_ecpf_hier_parallel", "meta_ecpf_gddm"],
        default="oracle_60",
        help="ECPF warning/drift signal source.",
    )
    parser.add_argument(
        "--uq-mode",
        choices=["mi_like", "vote_disagreement", "predictive_entropy", "variance_eu"],
        default="mi_like",
        help="UQ proxy mode used by meta_ecpf_dwm.",
    )
    parser.add_argument(
        "--detector-type",
        choices=["adwin_dual"],
        default="adwin_dual",
        help="Standalone detector type when --signal-mode detector.",
    )
    parser.add_argument(
        "--adwin-family-combo",
        choices=sorted(ECPFAdwinFamilyDetector.COMBOS.keys()),
        default="seed_warning_adwin_drift",
        help="Warning/drift combo used when --signal-mode hybrid_adwin_family.",
    )
    parser.add_argument("--detector-delta", type=float, default=0.05, help="Detector delta.")
    parser.add_argument("--detector-delta-w", type=float, default=0.1, help="Detector warning delta.")
    parser.add_argument("--detector-min-instances", type=int, default=30, help="Detector warmup instances.")
    parser.add_argument("--warning-detector", choices=["adwin", "seed", "seqdrift2"], default=None)
    parser.add_argument("--drift-detector", choices=["adwin", "seed", "seqdrift2"], default=None)
    parser.add_argument("--warning-signal", choices=sorted(SIGNAL_CHOICES), default="error")
    parser.add_argument("--drift-signal", choices=sorted(SIGNAL_CHOICES), default="error")
    parser.add_argument("--uq-num-classes", type=int, default=None)
    parser.add_argument("--warning-value-range", type=float, default=1.0)
    parser.add_argument("--drift-value-range", type=float, default=1.0)
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
        "hf"
        if (
            args.signal_mode in {"meta_ecpf_dwm", "meta_ecpf_hcdt", "meta_ecpf_hier_parallel", "meta_ecpf_gddm", "uq_warning"}
            or args.warning_signal != "error"
            or args.drift_signal != "error"
        )
        else "ht"
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
        ecpf_adwin_family_combo=args.adwin_family_combo,
        ecpf_warning_detector=args.warning_detector,
        ecpf_drift_detector=args.drift_detector,
        ecpf_warning_signal=args.warning_signal,
        ecpf_drift_signal=args.drift_signal,
        ecpf_uq_num_classes=args.uq_num_classes,
        ecpf_warning_value_range=args.warning_value_range,
        ecpf_drift_value_range=args.drift_value_range,
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
                    "detector_type": d.details.get("detector_type"),
                    "warning_detector": d.details.get("warning_detector"),
                    "drift_detector": d.details.get("drift_detector"),
                    "warning_signal": d.details.get("warning_signal"),
                    "drift_signal": d.details.get("drift_signal"),
                    "uq_mode": d.details.get("uq_mode"),
                    "uq_raw": d.details.get("uq_raw"),
                    "uq_smoothed": d.details.get("uq_smoothed"),
                    "gddm_U": d.details.get("gddm_U"),
                    "gddm_G_warning": d.details.get("gddm_G_warning"),
                    "gddm_G_drift": d.details.get("gddm_G_drift"),
                    "gddm_drift_type": d.details.get("gddm_drift_type"),
                    "candidate_drift": d.details.get("candidate_drift"),
                    "candidate_source": d.details.get("active_candidate_source")
                    or d.details.get("candidate_source"),
                    "fast_path_score": d.details.get("fast_path_score"),
                    "gradual_path_score": d.details.get("gradual_path_score"),
                    "validation_passed": d.details.get("validation_passed"),
                    "validation_gap": d.details.get("validation_gap"),
                    "hist_error": d.details.get("hist_error"),
                    "new_error": d.details.get("new_error"),
                    "warning_start_t": d.details.get("warning_start_t"),
                    "confirmation_t": d.details.get("confirmation_t"),
                    "warning_age": d.details.get("warning_age"),
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
    if args.signal_mode in {"meta_ecpf_dwm", "meta_ecpf_hcdt", "meta_ecpf_hier_parallel", "meta_ecpf_gddm"}:
        print(f"uq mode: {args.uq_mode}")
    print(f"detected drift events: {drift_events}")
    print(f"pool alive snapshots: {alive}")
    print(f"prequential accuracy (post-warm-start): {acc:.4f}")
    if args.signal_mode in ADWIN_FAMILY_SIGNAL_MODES:
        combo = args.adwin_family_combo if args.signal_mode == "hybrid_adwin_family" else args.signal_mode
        print(f"signal mode: {args.signal_mode} ({combo})")
        print(
            f"routing: warning={args.warning_detector or 'mode-default'}/{args.warning_signal} "
            f"drift={args.drift_detector or 'mode-default'}/{args.drift_signal}"
        )

    # --- Correct Detection score ---
    _dt_path = args.drift_times or str(csv_path.with_name(csv_path.stem + "_drift_times.txt"))
    try:
        _intervals = load_drift_intervals_file(_dt_path)
        _perturbation = build_perturbation_intervals(_intervals, extension=1000)
        _det_ts = [d.timestamp for d in pipe.detections]
        _cd = compute_correct_detection(_det_ts, _perturbation)
        _score_str = f"{_cd.score_percent:.1f}%" if _cd.score_percent is not None else "n/a"
        print(
            f"correct detection (perturbation=drift_interval+1000): "
            f"TP={_cd.tp}, FP={_cd.fp}, N={_cd.n_intervals}, score={_score_str} "
            f"((TP-FP)/N×100, floored at 0%)"
        )
    except FileNotFoundError:
        print("correct detection: drift intervals file not found, skipping")

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
