#!/usr/bin/env python3
"""
Evaluate Type-LDD drift-type classifier on all streams under data/.

Uses the **ECPF pipeline** (detector → ECPF model pool → Type-LDD classifier).
ECPF does NOT use the RCD recurring-drift label; model reuse is handled inside
ECPF via similarity in the model pool.

Type-classifier metrics are computed **only on matched detections**:
  abs(detection_time - gt_drift_midpoint) <= tolerance

Outputs:
  - per-file progress
  - per-type accuracy (matched only)
  - overall accuracy (matched only)
  - 3×3 confusion matrix (matched only)

Usage:
  python3 scripts/eval_type_ldd_all_streams.py
  python3 scripts/eval_type_ldd_all_streams.py --ecpf-signal-mode dual_adwin --model-type ht
  python3 scripts/eval_type_ldd_all_streams.py --max-steps 20000
"""

from __future__ import annotations

import argparse
import ast
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import DriftDetection, DriftType, PipelineConfig  # noqa: E402
from src.pipeline import ConceptDriftPipeline  # noqa: E402

TYPE_DIRS: Dict[str, str] = {
    "sudden": "sudden_drift",
    "gradual": "gradual_drift",
    "incremental": "incremental_drift",
}

TYPE_TO_INT = {"sudden": 0, "gradual": 1, "incremental": 2}
INT_TO_TYPE = {0: "sudden", 1: "gradual", 2: "incremental"}

DRIFT_TYPE_TO_INT = {
    DriftType.SUDDEN: 0,
    DriftType.GRADUAL: 1,
    DriftType.INCREMENTAL: 2,
}


def load_stream(csv_path: Path, drift_times_path: Path):
    df = pd.read_csv(csv_path)
    X = df.drop(columns=["y"]).values
    y = df["y"].values
    drift_intervals = ast.literal_eval(drift_times_path.read_text().strip())
    drift_midpoints = [int((s + e) / 2) for s, e in drift_intervals]
    return X, y, drift_midpoints, drift_intervals


def discover_streams(data_dir: Path) -> List[Tuple[str, Path, Path]]:
    streams = []
    for true_type, subdir_name in TYPE_DIRS.items():
        subdir = data_dir / subdir_name
        if not subdir.is_dir():
            continue
        for csv_path in sorted(subdir.glob("*.csv")):
            if csv_path.name.endswith("_drift_times.csv"):
                continue
            dt_path = csv_path.with_name(csv_path.stem + "_drift_times.txt")
            if dt_path.exists():
                streams.append((true_type, csv_path, dt_path))
    return streams


def build_ecpf_config(
    *,
    ecpf_signal_mode: str,
    model_type: str,
    detector_delta: float,
) -> PipelineConfig:
    """Match the ECPF setup used in detector calibration experiments."""
    return PipelineConfig(
        use_ecpf=True,
        model_type=model_type,
        ecpf_signal_mode=ecpf_signal_mode,
        ecpf_oracle_true_drift_times=None,
        detector_delta=detector_delta,
        detector_delta_w=detector_delta * 2.0,
        ecpf_detector_min_instances=30,
        ecpf_uq_mode="mi_like",
        update_batch_size=500,
        recurrence_threshold=0.15,
    )


def run_pipeline_on_stream(
    X: np.ndarray,
    y: np.ndarray,
    config: PipelineConfig,
    *,
    max_steps: int = 0,
    warmup: int = 200,
) -> List[DriftDetection]:
    pipeline = ConceptDriftPipeline(config=config)
    n = len(y)
    if max_steps > 0:
        n = min(n, max_steps)

    pipeline.warm_start(X[:warmup], y[:warmup])
    for i in range(warmup, n):
        pipeline.step(X[i], y[i], index=i)
    return list(pipeline.detections)


def match_typed_detections(
    detections: List[DriftDetection],
    true_type_int: int,
    drift_midpoints: List[int],
    tolerance: int,
) -> Tuple[List[int], List[int], int, int, int]:
    """
    Return (y_true, y_pred) for **matched** typed detections only.

    Also returns:
      n_typed_detections, n_matched, n_unmatched
    """
    typed = [
        d for d in detections
        if d.drift_type in (DriftType.SUDDEN, DriftType.GRADUAL, DriftType.INCREMENTAL)
    ]

    y_true: List[int] = []
    y_pred: List[int] = []
    matched_gt: set[int] = set()
    n_matched = 0
    n_unmatched = 0

    for d in typed:
        pred_int = DRIFT_TYPE_TO_INT.get(d.drift_type, 0)
        hit = False
        for idx, gt in enumerate(drift_midpoints):
            if idx not in matched_gt and abs(d.timestamp - gt) <= tolerance:
                matched_gt.add(idx)
                hit = True
                n_matched += 1
                y_true.append(true_type_int)
                y_pred.append(pred_int)
                break
        if not hit:
            n_unmatched += 1

    return y_true, y_pred, len(typed), n_matched, n_unmatched


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, default="data")
    ap.add_argument("--max-steps", type=int, default=0, help="0 = full stream")
    ap.add_argument("--tolerance", type=int, default=500)
    ap.add_argument("--warmup", type=int, default=200)
    ap.add_argument(
        "--ecpf-signal-mode",
        type=str,
        default="dual_adwin",
        help="ECPF detector mode (same as calibrate_and_evaluate_detectors.py).",
    )
    ap.add_argument("--model-type", type=str, default="hf")
    ap.add_argument("--detector-delta", type=float, default=0.05)
    args = ap.parse_args()

    config = build_ecpf_config(
        ecpf_signal_mode=args.ecpf_signal_mode,
        model_type=args.model_type,
        detector_delta=args.detector_delta,
    )

    data_dir = Path(args.data_dir)
    streams = discover_streams(data_dir)
    print(f"Found {len(streams)} streams")
    print(
        f"ECPF mode: signal={args.ecpf_signal_mode} model={args.model_type} "
        f"delta={args.detector_delta} tolerance={args.tolerance}\n"
    )

    all_yt: List[int] = []
    all_yp: List[int] = []
    per_type_yt: Dict[str, List[int]] = {t: [] for t in TYPE_DIRS}
    per_type_yp: Dict[str, List[int]] = {t: [] for t in TYPE_DIRS}
    total_typed = 0
    total_matched = 0
    total_unmatched = 0
    total_gt_drifts = 0

    for i, (true_type, csv_path, dt_path) in enumerate(streams):
        print(f"[{i+1}/{len(streams)}] {csv_path.name}  (gt={true_type})", end="", flush=True)
        t0 = time.time()
        X, y, drift_midpoints, _ = load_stream(csv_path, dt_path)
        total_gt_drifts += len(drift_midpoints)
        detections = run_pipeline_on_stream(
            X, y, config, max_steps=args.max_steps, warmup=args.warmup,
        )
        yt, yp, n_typed, n_matched, n_unmatched = match_typed_detections(
            detections, TYPE_TO_INT[true_type], drift_midpoints, args.tolerance,
        )
        elapsed = time.time() - t0

        total_typed += n_typed
        total_matched += n_matched
        total_unmatched += n_unmatched

        if yt:
            acc = float(np.mean(np.array(yt) == np.array(yp)))
            acc_str = f"{acc:.3f}"
        else:
            acc_str = "n/a"

        print(
            f"  alerts={n_typed}  matched={n_matched}  unmatched={n_unmatched}  "
            f"gt={len(drift_midpoints)}  type_acc={acc_str}  ({elapsed:.1f}s)"
        )

        all_yt.extend(yt)
        all_yp.extend(yp)
        per_type_yt[true_type].extend(yt)
        per_type_yp[true_type].extend(yp)

    print("\n" + "=" * 60)
    print("TYPE CLASSIFIER (matched detections only)")
    print("=" * 60)
    print(f"  total_gt_drifts     = {total_gt_drifts}")
    print(f"  total_typed_alerts  = {total_typed}")
    print(f"  total_matched       = {total_matched}")
    print(f"  total_unmatched     = {total_unmatched}")

    for t in TYPE_DIRS:
        yt = np.array(per_type_yt[t])
        yp = np.array(per_type_yp[t])
        if len(yt):
            print(f"  {t:13s}  n={len(yt):4d}  accuracy={float(np.mean(yt == yp)):.4f}")
        else:
            print(f"  {t:13s}  n=   0  (no matched alerts)")

    if all_yt:
        yt_all = np.array(all_yt)
        yp_all = np.array(all_yp)
        print(f"\n  {'OVERALL':13s}  n={len(yt_all):4d}  accuracy={float(np.mean(yt_all == yp_all)):.4f}")

        cm = np.zeros((3, 3), dtype=int)
        for a, b in zip(all_yt, all_yp):
            cm[int(a), int(b)] += 1
        print("\nConfusion matrix (rows=GT, cols=Pred):")
        print(f"{'':>15s}  {'sudden':>8s}  {'gradual':>8s}  {'increm.':>8s}")
        for r in range(3):
            print(f"  {INT_TO_TYPE[r]:>13s}  {cm[r,0]:8d}  {cm[r,1]:8d}  {cm[r,2]:8d}")
    else:
        print("\n  No matched typed alerts — cannot compute accuracy or confusion matrix.")
        print("  (Detector may be missing drifts or alerts are outside tolerance.)")
    print()


if __name__ == "__main__":
    main()
