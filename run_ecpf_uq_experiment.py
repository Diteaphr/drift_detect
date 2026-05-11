"""
Run ECPF UQ Warning Layer experiments.

Compares five settings across recurring-drift datasets (g00..g09):

    A. Baseline:    ECPF + HT  + error-based detector
    B. UQ Direct:   ECPF + HF  + error-based detector (forest but no UQ warning)
    C. UQ Warning:  ECPF + HF  + UQ warning (MI-like) + error drift confirmation
    D1. Ablation:   ECPF + HF  + UQ warning (vote_disagreement)
    D2. Ablation:   ECPF + HF  + UQ warning (predictive_entropy)
    E. Meta ECPF:   ECPF + HF  + UQ warning (MI-like) + DWM Meta Detector

Evaluation metrics:
    - prequential accuracy
    - drift detection delay (vs ground-truth)
    - false warning rate
    - reuse precision
    - average collection size
    - runtime (seconds)

Usage:
    python run_ecpf_uq_experiment.py
    python run_ecpf_uq_experiment.py --max-steps 5000 --print-events
    python3 run_ecpf_uq_experiment.py --max-steps 2000 --print-events

"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.config import PipelineConfig
from src.pipeline import load_recurring_stream_pair, ConceptDriftPipeline
from detectors.meta_ecpf.adwin_family import ECPFAdwinFamilyDetector
from detectors.meta_ecpf.signal_routing import SIGNAL_CHOICES


# ──────────────────────────────────────────────────────────────────────
# Experiment settings
# ──────────────────────────────────────────────────────────────────────
SETTINGS: Dict[str, Dict[str, Any]] = {
    "A_baseline_ht_error": {
        "model_type": "ht",
        "signal_mode": "detector",
        "uq_mode": None,
        "label": "ECPF+HT+error",
    },
    "H_dual_seed": {
        "model_type": "ht",
        "signal_mode": "dual_seed",
        "uq_mode": None,
        "label": "ECPF+HT+dual-SEED",
    },
    "I_dual_seqdrift2": {
        "model_type": "ht",
        "signal_mode": "dual_seqdrift2",
        "uq_mode": None,
        "label": "ECPF+HT+dual-SeqDrift2",
    },
    "J_seed_warning_adwin_drift": {
        "model_type": "ht",
        "signal_mode": "seed_warning_adwin_drift",
        "uq_mode": None,
        "label": "ECPF+HT+SEEDwarn+ADWINdrift",
    },
    "K_adwin_warning_seed_drift": {
        "model_type": "ht",
        "signal_mode": "adwin_warning_seed_drift",
        "uq_mode": None,
        "label": "ECPF+HT+ADWINwarn+SEEDdrift",
    },
    "L_seqdrift2_warning_adwin_drift": {
        "model_type": "ht",
        "signal_mode": "seqdrift2_warning_adwin_drift",
        "uq_mode": None,
        "label": "ECPF+HT+SeqDrift2warn+ADWINdrift",
    },
    "M_adwin_warning_seqdrift2_drift": {
        "model_type": "ht",
        "signal_mode": "adwin_warning_seqdrift2_drift",
        "uq_mode": None,
        "label": "ECPF+HT+ADWINwarn+SeqDrift2drift",
    },
    "E_meta_ecpf_dwm": {
        "model_type": "hf",
        "signal_mode": "meta_ecpf_dwm",
        "uq_mode": "mi_like",
        "label": "ECPF+HF+UQ(MI)+DWM",
    },
    "F_hier_parallel": {
        "model_type": "hf",
        "signal_mode": "meta_ecpf_hier_parallel",
        "uq_mode": "mi_like",
        "label": "ECPF+HF+UQ(MI)+HierParallel",
    },
    "G_meta_ecpf_gddm": {
        "model_type": "hf",
        "signal_mode": "meta_ecpf_gddm",
        "uq_mode": "mi_like",
        "label": "ECPF+HF+GDDM",
    },
    "H_meta_ecpf_hcdt": {
        "model_type": "ht",
        "signal_mode": "meta_ecpf_hcdt",
        "uq_mode": None,
        "label": "ECPF+HT+HCDT",
    },

    "B_hf_error_direct": {
        "model_type": "hf",
        "signal_mode": "detector",
        "uq_mode": None,
        "label": "ECPF+HF+error",
    },
    "C_hf_uq_mi_like": {
        "model_type": "hf",
        "signal_mode": "uq_warning",
        "uq_mode": "mi_like",
        "label": "ECPF+HF+UQ(MI)",
    },
    "D1_hf_uq_vote_dis": {
        "model_type": "hf",
        "signal_mode": "uq_warning",
        "uq_mode": "vote_disagreement",
        "label": "ECPF+HF+UQ(vote)",
    },
    "D2_hf_uq_pred_ent": {
        "model_type": "hf",
        "signal_mode": "uq_warning",
        "uq_mode": "predictive_entropy",
        "label": "ECPF+HF+UQ(entropy)",
    },
}


# ──────────────────────────────────────────────────────────────────────
# Metric computation helpers
# ──────────────────────────────────────────────────────────────────────
def _detection_delay(
    ground_truth_times: List[int],
    detected_times: List[int],
    tolerance: int = 500,
) -> float:
    """Mean delay from ground-truth drift to nearest detected drift.

    Each ground-truth drift is matched to the earliest detection within
    ``[T, T + tolerance]``.  Unmatched ground-truths contribute ``tolerance``
    to the mean.
    """
    if not ground_truth_times:
        return 0.0
    delays: List[int] = []
    for gt in ground_truth_times:
        best = tolerance
        for dt in detected_times:
            if gt <= dt <= gt + tolerance:
                best = min(best, dt - gt)
        delays.append(best)
    return float(np.mean(delays)) if delays else 0.0


def _false_warning_rate(
    detected_times: List[int],
    ground_truth_times: List[int],
    tolerance: int = 500,
) -> float:
    """Fraction of detected drifts that are NOT within ``tolerance`` of any
    ground-truth drift."""
    if not detected_times:
        return 0.0
    false_count = 0
    for dt in detected_times:
        matched = any(abs(dt - gt) <= tolerance for gt in ground_truth_times)
        if not matched:
            false_count += 1
    return false_count / len(detected_times)


# ──────────────────────────────────────────────────────────────────────
# Single run
# ──────────────────────────────────────────────────────────────────────
def run_one(
    csv_path: Path,
    warm_start: int,
    max_steps: int,
    model_type: str,
    signal_mode: str,
    uq_mode: Optional[str],
    detector_delta: float,
    detector_delta_w: float,
    detector_min_instances: int,
    adwin_family_combo: str,
    warning_detector: Optional[str],
    drift_detector: Optional[str],
    warning_signal: str,
    drift_signal: str,
    uq_num_classes: Optional[int],
    warning_value_range: float,
    drift_value_range: float,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    X, y, drift_times = load_recurring_stream_pair(str(csv_path))
    if max_steps > 0:
        n = min(max_steps, len(y))
        X, y = X[:n], y[:n]
        drift_times = [t for t in drift_times if t < n]

    effective_model_type = (
        "hf"
        if model_type == "ht" and (warning_signal != "error" or drift_signal != "error")
        else model_type
    )

    cfg_kwargs: Dict[str, Any] = dict(
        use_ecpf=True,
        model_type=effective_model_type,
        ecpf_signal_mode=signal_mode,
        ecpf_oracle_true_drift_times=None,
        ecpf_warning_length=60,
        ecpf_max_pool_size=10,
        detector_delta=detector_delta,
        detector_delta_w=detector_delta_w,
        ecpf_detector_min_instances=detector_min_instances,
        ecpf_adwin_family_combo=adwin_family_combo,
        ecpf_warning_detector=warning_detector,
        ecpf_drift_detector=drift_detector,
        ecpf_warning_signal=warning_signal,
        ecpf_drift_signal=drift_signal,
        ecpf_uq_num_classes=uq_num_classes,
        ecpf_warning_value_range=warning_value_range,
        ecpf_drift_value_range=drift_value_range,
    )
    if uq_mode is not None:
        cfg_kwargs["ecpf_uq_mode"] = uq_mode
    cfg = PipelineConfig(**cfg_kwargs)
    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[:warm_start], y[:warm_start])

    y_pred = np.full(len(y), np.nan, dtype=float)
    event_rows: List[Dict[str, Any]] = []
    pool_sizes: List[int] = []
    reuse_wins = 0
    reuse_total = 0

    t_start = time.perf_counter()
    for i in range(warm_start, len(y)):
        yp, dets, drift = pipe.step(X[i], y[i], index=i)
        y_pred[i] = yp
        if pipe._ecpf is not None:
            pool_sizes.append(sum(1 for s in pipe._ecpf.slots if s is not None))
        if drift:
            for d in dets:
                det_details = d.details or {}
                row = {
                    "file": csv_path.name,
                    "timestamp": int(d.timestamp),
                    "source": d.detector_source,
                    "drift_type": d.drift_type.value,
                    "ecpf_protocol": det_details.get("ecpf_protocol"),
                    "detector_type": det_details.get("detector_type"),
                    "warning_detector": det_details.get("warning_detector"),
                    "drift_detector": det_details.get("drift_detector"),
                    "warning_signal": det_details.get("warning_signal"),
                    "drift_signal": det_details.get("drift_signal"),
                    "uq_mode": det_details.get("uq_mode"),
                    "uq_raw": det_details.get("uq_raw"),
                    "uq_smoothed": det_details.get("uq_smoothed"),
                    "gddm_U": det_details.get("gddm_U"),
                    "gddm_G_warning": det_details.get("gddm_G_warning"),
                    "gddm_G_drift": det_details.get("gddm_G_drift"),
                    "gddm_drift_type": det_details.get("gddm_drift_type"),
                    "candidate_drift": det_details.get("candidate_drift"),
                    "candidate_source": det_details.get("active_candidate_source")
                    or det_details.get("candidate_source"),
                    "fast_path_score": det_details.get("fast_path_score"),
                    "gradual_path_score": det_details.get("gradual_path_score"),
                    "validation_passed": det_details.get("validation_passed"),
                    "validation_gap": det_details.get("validation_gap"),
                    "hist_error": det_details.get("hist_error"),
                    "new_error": det_details.get("new_error"),
                    "warning_start_t": det_details.get("warning_start_t"),
                    "confirmation_t": det_details.get("confirmation_t"),
                    "warning_age": det_details.get("warning_age"),
                    "buffer_len": det_details.get("buffer_len"),
                    "pool_size": det_details.get("collection_size"),
                    "best_idx": det_details.get("best_idx"),
                    "acc_current_on_warning": det_details.get("acc_current_on_warning"),
                    "acc_best_on_warning": det_details.get("acc_best_on_warning"),
                    "acc_new_on_warning": det_details.get("acc_new_on_warning"),
                }
                event_rows.append(row)
                # Reuse precision: did the reused model beat the new model?
                acc_best = det_details.get("acc_best_on_warning", 0.0)
                acc_new = det_details.get("acc_new_on_warning", 0.0)
                if acc_best is not None and acc_new is not None:
                    reuse_total += 1
                    if acc_best >= acc_new:
                        reuse_wins += 1
    elapsed = time.perf_counter() - t_start

    # Metrics
    valid = ~np.isnan(y_pred)
    acc = float(np.mean((y_pred[valid] == y[valid]).astype(float))) if np.any(valid) else 0.0
    detected_times = [r["timestamp"] for r in event_rows]
    delay = _detection_delay(drift_times, detected_times)
    false_warn = _false_warning_rate(detected_times, drift_times)
    reuse_prec = (reuse_wins / reuse_total) if reuse_total > 0 else float("nan")
    avg_pool = float(np.mean(pool_sizes)) if pool_sizes else 0.0

    summary = {
        "file": csv_path.name,
        "samples": int(len(y)),
        "gt_drift_count": len(drift_times),
        "detected_drifts": len(event_rows),
        "prequential_accuracy": acc,
        "detection_delay": delay,
        "false_warning_rate": false_warn,
        "reuse_precision": reuse_prec,
        "avg_collection_size": avg_pool,
        "runtime_s": elapsed,
    }
    return summary, event_rows


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run ECPF UQ Warning Layer experiments."
    )
    parser.add_argument("--data-dir", default="data/recurring_drift")
    parser.add_argument("--warm-start", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument("--detector-delta", type=float, default=0.05)
    parser.add_argument("--detector-delta-w", type=float, default=0.1)
    parser.add_argument("--detector-min-instances", type=int, default=30)
    parser.add_argument("--warning-detector", choices=["adwin", "seed", "seqdrift2"], default=None)
    parser.add_argument("--drift-detector", choices=["adwin", "seed", "seqdrift2"], default=None)
    parser.add_argument("--warning-signal", choices=sorted(SIGNAL_CHOICES), default="error")
    parser.add_argument("--drift-signal", choices=sorted(SIGNAL_CHOICES), default="error")
    parser.add_argument("--uq-num-classes", type=int, default=None)
    parser.add_argument("--warning-value-range", type=float, default=1.0)
    parser.add_argument("--drift-value-range", type=float, default=1.0)
    parser.add_argument(
        "--adwin-family-combo",
        choices=sorted(ECPFAdwinFamilyDetector.COMBOS.keys()),
        default="seed_warning_adwin_drift",
        help="Warning/drift combo used by hybrid_adwin_family settings.",
    )
    parser.add_argument("--out-dir", default="outputs")
    parser.add_argument("--print-events", action="store_true")
    parser.add_argument(
        "--settings",
        nargs="*",
        default=None,
        help="Run specific settings only (e.g. A_baseline_ht_error C_hf_uq_mi_like)",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = args.settings or list(SETTINGS.keys())
    all_rows: List[Dict[str, Any]] = []
    all_events: List[Dict[str, Any]] = []

    for setting_key in selected:
        if setting_key not in SETTINGS:
            print(f"[skip] unknown setting: {setting_key}")
            continue
        s = SETTINGS[setting_key]
        print(f"\n{'=' * 60}")
        print(f"Setting: {setting_key}  ({s['label']})")
        print(f"{'=' * 60}")

        for gi in range(10):
            name = f"recurring_sud_sea100k_g{gi:02d}.csv"
            csv_path = data_dir / name
            if not csv_path.exists():
                print(f"  [skip] missing {csv_path}")
                continue

            summary, events = run_one(
                csv_path=csv_path,
                warm_start=args.warm_start,
                max_steps=args.max_steps,
                model_type=s["model_type"],
                signal_mode=s["signal_mode"],
                uq_mode=s["uq_mode"],
                detector_delta=args.detector_delta,
                detector_delta_w=args.detector_delta_w,
                detector_min_instances=args.detector_min_instances,
                adwin_family_combo=args.adwin_family_combo,
                warning_detector=args.warning_detector,
                drift_detector=args.drift_detector,
                warning_signal=args.warning_signal,
                drift_signal=args.drift_signal,
                uq_num_classes=args.uq_num_classes,
                warning_value_range=args.warning_value_range,
                drift_value_range=args.drift_value_range,
            )
            summary["setting"] = setting_key
            summary["label"] = s["label"]
            all_rows.append(summary)

            for e in events:
                e["setting"] = setting_key
            all_events.extend(events)

            print(
                f"  {name}: acc={summary['prequential_accuracy']:.4f}  "
                f"delay={summary['detection_delay']:.0f}  "
                f"false_warn={summary['false_warning_rate']:.2f}  "
                f"reuse_prec={summary['reuse_precision']:.2f}  "
                f"pool={summary['avg_collection_size']:.1f}  "
                f"time={summary['runtime_s']:.1f}s"
            )
            if args.print_events:
                for e in events:
                    print(
                        f"    [event] t={e['timestamp']} src={e['source']} "
                        f"buf={e['buffer_len']} pool={e['pool_size']}"
                    )

    if not all_rows:
        print("No files were processed.")
        return

    # Save detailed results
    df = pd.DataFrame(all_rows)
    df.to_csv(out_dir / "ecpf_uq_comparison.csv", index=False)

    # Summary per setting
    summary_cols = [
        "prequential_accuracy",
        "detection_delay",
        "false_warning_rate",
        "reuse_precision",
        "avg_collection_size",
        "runtime_s",
    ]
    agg = df.groupby("setting")[summary_cols].mean().reset_index()
    agg.to_csv(out_dir / "ecpf_uq_summary.csv", index=False)

    # Events
    pd.DataFrame(all_events).to_csv(out_dir / "ecpf_uq_events.csv", index=False)

    # Print summary table
    print(f"\n{'=' * 80}")
    print("SUMMARY (mean across g00..g09)")
    print(f"{'=' * 80}")
    for _, row in agg.iterrows():
        label = SETTINGS.get(row["setting"], {}).get("label", row["setting"])
        print(
            f"  {label:30s}  acc={row['prequential_accuracy']:.4f}  "
            f"delay={row['detection_delay']:.0f}  "
            f"false_warn={row['false_warning_rate']:.2f}  "
            f"reuse_prec={row['reuse_precision']:.2f}  "
            f"pool={row['avg_collection_size']:.1f}  "
            f"time={row['runtime_s']:.1f}s"
        )
    print(f"\nResults saved to {out_dir}")


if __name__ == "__main__":
    main()
