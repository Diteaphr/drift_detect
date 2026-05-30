"""
Run all ADWIN-family detector/signal combinations on recurring g00..g09.

Grid size:
    warning_detector: adwin | seed | seqdrift2
    drift_detector:   adwin | seed | seqdrift2
    warning_signal:   error | uq_mi | uq_vote | uq_entropy | uq_variance
    drift_signal:     error | uq_mi | uq_vote | uq_entropy | uq_variance

Total: 3 * 3 * 5 * 5 = 225 experiment combinations.
"""

from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path
import time
from typing import Any, Dict, List

import pandas as pd

from run_ecpf_recurring_batch import run_one


DETECTORS = ("adwin", "seed", "seqdrift2")
SIGNALS = ("error", "uq_mi", "uq_vote", "uq_entropy", "uq_variance")


def _model_type_for_signals(warning_signal: str, drift_signal: str) -> str:
    if warning_signal != "error" or drift_signal != "error":
        return "hf"
    return "ht"


def _run_combo(
    *,
    data_dir: Path,
    warm_start: int,
    max_steps: int,
    warning_detector: str,
    drift_detector: str,
    warning_signal: str,
    drift_signal: str,
    detector_delta: float,
    detector_delta_w: float,
    detector_min_instances: int,
    uq_num_classes: int | None,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    model_type = _model_type_for_signals(warning_signal, drift_signal)
    combo_start = time.perf_counter()

    for gi in range(10):
        csv_path = data_dir / f"recurring_sud_sea100k_g{gi:02d}.csv"
        if not csv_path.exists():
            continue

        file_start = time.perf_counter()
        summary, _events = run_one(
            csv_path=csv_path,
            warm_start=warm_start,
            max_steps=max_steps,
            signal_mode="hybrid_adwin_family",
            uq_mode="mi_like",
            model_type=model_type,
            detector_delta=detector_delta,
            detector_delta_w=detector_delta_w,
            detector_min_instances=detector_min_instances,
            adwin_family_combo="dual_adwin",
            warning_detector=warning_detector,
            drift_detector=drift_detector,
            warning_signal=warning_signal,
            drift_signal=drift_signal,
            uq_num_classes=uq_num_classes,
            warning_value_range=1.0,
            drift_value_range=1.0,
        )
        runtime_s = time.perf_counter() - file_start
        summary.update(
            {
                "warning_detector": warning_detector,
                "drift_detector": drift_detector,
                "warning_signal": warning_signal,
                "drift_signal": drift_signal,
                "model_type": model_type,
                "runtime_s": runtime_s,
            }
        )
        rows.append(summary)

    combo_runtime = time.perf_counter() - combo_start
    for row in rows:
        row["combo_runtime_s"] = combo_runtime
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run 225 ECPF ADWIN-family detector/signal combinations."
    )
    parser.add_argument("--data-dir", default="data/recurring_drift")
    parser.add_argument("--warm-start", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=20000)
    parser.add_argument("--detector-delta", type=float, default=0.05)
    parser.add_argument("--detector-delta-w", type=float, default=0.1)
    parser.add_argument("--detector-min-instances", type=int, default=30)
    parser.add_argument("--uq-num-classes", type=int, default=2)
    parser.add_argument(
        "--summary-csv",
        default="outputs/ecpf_recurring_grid_20k_summary.csv",
    )
    parser.add_argument(
        "--details-csv",
        default="outputs/ecpf_recurring_grid_20k_details.csv",
    )
    parser.add_argument(
        "--limit-combos",
        type=int,
        default=0,
        help="Debug helper. If >0, run only the first N combinations.",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    all_detail_rows: List[Dict[str, Any]] = []
    combo_rows: List[Dict[str, Any]] = []

    combos = list(product(DETECTORS, DETECTORS, SIGNALS, SIGNALS))
    if args.limit_combos > 0:
        combos = combos[: args.limit_combos]

    for idx, (warning_detector, drift_detector, warning_signal, drift_signal) in enumerate(
        combos,
        start=1,
    ):
        print(
            f"[{idx:03d}/{len(combos):03d}] "
            f"warn={warning_detector}/{warning_signal} "
            f"drift={drift_detector}/{drift_signal}"
        )
        detail_rows = _run_combo(
            data_dir=data_dir,
            warm_start=args.warm_start,
            max_steps=args.max_steps,
            warning_detector=warning_detector,
            drift_detector=drift_detector,
            warning_signal=warning_signal,
            drift_signal=drift_signal,
            detector_delta=args.detector_delta,
            detector_delta_w=args.detector_delta_w,
            detector_min_instances=args.detector_min_instances,
            uq_num_classes=args.uq_num_classes,
        )
        if not detail_rows:
            continue
        all_detail_rows.extend(detail_rows)
        df_combo = pd.DataFrame(detail_rows)
        combo_rows.append(
            {
                "warning_detector": warning_detector,
                "drift_detector": drift_detector,
                "warning_signal": warning_signal,
                "drift_signal": drift_signal,
                "model_type": df_combo["model_type"].iloc[0],
                "files": int(len(df_combo)),
                "mean_accuracy": float(df_combo["prequential_accuracy"].mean()),
                "mean_detected_drifts": float(df_combo["detected_drift_events"].mean()),
                "mean_time_s": float(df_combo["runtime_s"].mean()),
                "total_time_s": float(df_combo["runtime_s"].sum()),
            }
        )

    if not combo_rows:
        print("No experiments were processed.")
        return

    summary_df = pd.DataFrame(combo_rows).sort_values(
        ["mean_accuracy", "mean_detected_drifts"],
        ascending=[False, True],
    )
    details_df = pd.DataFrame(all_detail_rows)

    summary_path = Path(args.summary_csv)
    details_path = Path(args.details_csv)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    details_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(summary_path, index=False)
    details_df.to_csv(details_path, index=False)

    print("\nGrid complete")
    print(f"combinations: {len(summary_df)}")
    print(f"summary csv: {summary_path}")
    print(f"details csv: {details_path}")
    print("\nTop 20 by mean accuracy:")
    print(
        summary_df[
            [
                "warning_detector",
                "drift_detector",
                "warning_signal",
                "drift_signal",
                "mean_accuracy",
                "mean_detected_drifts",
                "mean_time_s",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
