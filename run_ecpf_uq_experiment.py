"""
Run ECPF UQ Warning Layer experiments.

Compares five settings across recurring-drift datasets (g00..g09):

    A. Baseline:    ECPF + HT  + error-based detector
    B. UQ Direct:   ECPF + HF  + error-based detector (forest but no UQ warning)
    C. UQ Warning:  ECPF + HF  + UQ warning (MI-like) + error drift confirmation
    D1. Ablation:   ECPF + HF  + UQ warning (vote_disagreement)
    D2. Ablation:   ECPF + HF  + UQ warning (predictive_entropy)

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
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    X, y, drift_times = load_recurring_stream_pair(str(csv_path))
    if max_steps > 0:
        n = min(max_steps, len(y))
        X, y = X[:n], y[:n]
        drift_times = [t for t in drift_times if t < n]

    cfg_kwargs: Dict[str, Any] = dict(
        use_ecpf=True,
        model_type=model_type,
        ecpf_signal_mode=signal_mode,
        ecpf_oracle_true_drift_times=None,
        ecpf_warning_length=60,
        ecpf_max_pool_size=10,
        detector_delta=detector_delta,
        detector_delta_w=detector_delta_w,
        ecpf_detector_min_instances=detector_min_instances,
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
                    "uq_mode": det_details.get("uq_mode"),
                    "uq_raw": det_details.get("uq_raw"),
                    "uq_smoothed": det_details.get("uq_smoothed"),
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
