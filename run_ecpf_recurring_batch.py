"""
Run ECPF across recurring_sud_sea100k_g00 ... g09 and summarize results.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import PipelineConfig
from src.pipeline import load_recurring_stream_pair, ConceptDriftPipeline


def run_one(
    csv_path: Path,
    warm_start: int,
    max_steps: int,
    signal_mode: str,
    uq_mode: str,
    model_type: str,
    detector_delta: float,
    detector_delta_w: float,
    detector_min_instances: int,
) -> tuple[dict, list[dict]]:
    X, y, drift_times = load_recurring_stream_pair(str(csv_path))
    if max_steps > 0:
        n = min(max_steps, len(y))
        X = X[:n]
        y = y[:n]
        drift_times = [t for t in drift_times if t < n]

    cfg = PipelineConfig(
        use_ecpf=True,
        model_type=model_type,
        ecpf_signal_mode=signal_mode,
        ecpf_oracle_true_drift_times=drift_times if signal_mode == "oracle_60" else None,
        ecpf_uq_mode=uq_mode,
        ecpf_warning_length=60,
        ecpf_max_pool_size=10,
        detector_delta=detector_delta,
        detector_delta_w=detector_delta_w,
        ecpf_detector_min_instances=detector_min_instances,
    )
    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[:warm_start], y[:warm_start])

    y_pred = np.full(len(y), np.nan, dtype=float)
    drift_events = 0
    event_rows: list[dict] = []
    for i in range(warm_start, len(y)):
        yp, dets, drift = pipe.step(X[i], y[i], index=i)
        y_pred[i] = yp
        if drift:
            drift_events += len(dets)
            for d in dets:
                event_rows.append(
                    {
                        "file": csv_path.name,
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
                )

    valid = ~np.isnan(y_pred)
    acc = float(np.mean((y_pred[valid] == y[valid]).astype(np.float64))) if np.any(valid) else 0.0
    alive = sum(1 for s in pipe._ecpf.slots if s is not None) if pipe._ecpf is not None else 0
    summary = {
        "file": csv_path.name,
        "samples": int(len(y)),
        "groundtruth_drift_count": int(len(drift_times)),
        "groundtruth_drift_times": " ".join(str(t) for t in drift_times),
        "detected_drift_events": int(drift_events),
        "pool_alive_snapshots": int(alive),
        "prequential_accuracy": float(acc),
        "model_type": model_type,
    }
    return summary, event_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch run ECPF on recurring g00..g09.")
    parser.add_argument("--data-dir", default="data/recurring_drift", help="Directory containing recurring CSV files.")
    parser.add_argument("--warm-start", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument(
        "--signal-mode",
        choices=["oracle_60", "detector", "meta_ecpf_dwm", "meta_ecpf_hier_parallel"],
        default="detector",
    )
    parser.add_argument(
        "--uq-mode",
        choices=["mi_like", "vote_disagreement", "predictive_entropy"],
        default="mi_like",
        help="UQ proxy mode used by meta_ecpf_dwm.",
    )
    parser.add_argument("--detector-delta", type=float, default=0.05)
    parser.add_argument("--detector-delta-w", type=float, default=0.1)
    parser.add_argument("--detector-min-instances", type=int, default=30)
    parser.add_argument(
        "--model-type",
        choices=["ht", "hf"],
        default=None,
        help="Streaming model backend. Defaults to hf for UQ/meta modes, otherwise ht.",
    )
    parser.add_argument("--out-csv", default="outputs/ecpf_batch_summary.csv")
    parser.add_argument("--events-csv", default="outputs/ecpf_batch_events.csv")
    parser.add_argument("--print-events", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    rows = []
    all_events: list[dict] = []
    model_type = args.model_type or (
        "hf" if args.signal_mode in {"meta_ecpf_dwm", "meta_ecpf_hier_parallel", "uq_warning"} else "ht"
    )
    for i in range(10):
        name = f"recurring_sud_sea100k_g{i:02d}.csv"
        csv_path = data_dir / name
        if not csv_path.exists():
            print(f"[skip] missing {csv_path}")
            continue
        row, events = run_one(
            csv_path=csv_path,
            warm_start=args.warm_start,
            max_steps=args.max_steps,
            signal_mode=args.signal_mode,
            uq_mode=args.uq_mode,
            model_type=model_type,
            detector_delta=args.detector_delta,
            detector_delta_w=args.detector_delta_w,
            detector_min_instances=args.detector_min_instances,
        )
        rows.append(row)
        all_events.extend(events)
        print(
            f"{row['file']}: gt={row['groundtruth_drift_count']} "
            f"detected={row['detected_drift_events']} "
            f"pool={row['pool_alive_snapshots']} acc={row['prequential_accuracy']:.4f}"
        )
        if args.print_events:
            for e in events:
                print(
                    f"[event] file={e['file']} t={e['timestamp']} src={e['source']} "
                    f"buf={e['buffer_len']} pool={e['pool_size']} "
                    f"acc(cur/best/new)=({e['acc_current_on_warning']},"
                    f"{e['acc_best_on_warning']},{e['acc_new_on_warning']})"
                )

    if not rows:
        print("No files were processed.")
        return

    df = pd.DataFrame(rows)
    out = Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    out_events = Path(args.events_csv)
    out_events.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_events).to_csv(out_events, index=False)

    print("\nBatch complete")
    print(f"files: {len(df)}")
    print(f"mean accuracy: {df['prequential_accuracy'].mean():.4f}")
    print(f"mean detected drifts: {df['detected_drift_events'].mean():.2f}")
    print(f"summary csv: {out}")
    print(f"events csv: {out_events}")


if __name__ == "__main__":
    main()
