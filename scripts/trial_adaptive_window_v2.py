"""
V2: Adaptive window experiment with `dual_adwin` ECPF mode and more data.

Key differences from V1:
- Detector: ECPF with signal_mode="dual_adwin"
- Captures BOTH warning-start timestamps and drift-confirmation timestamps
- TP scoring uses warning timestamps (per user requirement)
- Uses 5 datasets per type (4 types × 5 = 20 datasets) for more robust RF
- Output written to outputs/adaptive_window_report_v2/ (does not overwrite V1)

Usage:
    python scripts/trial_adaptive_window_v2.py
"""

from __future__ import annotations

import ast
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline
from src.metrics import (
    build_perturbation_intervals,
    compute_correct_detection,
    AdaptiveWindowEstimator,
    WindowFeatures,
)
from src.metrics.generate_window_labels import (
    build_training_data,
    find_optimal_extension,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "adaptive_window_report_v2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 5 datasets per type × 4 types = 20 datasets
TRIAL_DATASETS = [
    *(f"data/sudden_drift/recurring_sudden_sea100k_g0{i}.csv" for i in range(5)),
    *(f"data/gradual_drift/recurring_gradual_sea100k_g0{i}.csv" for i in range(5)),
    *(f"data/incremental_drift/incremental_hyperplane_100k_g0{i}.csv" for i in range(5)),
    *(f"data/recurring_drift/recurring_sud_sea100k_g0{i}.csv" for i in range(5)),
]


def _load_intervals(csv_path: Path):
    txt = csv_path.with_name(csv_path.stem + "_drift_times.txt")
    return [(int(a), int(b)) for a, b in ast.literal_eval(txt.read_text().strip())]


def run_one(csv_path: Path, warm_start: int = 200):
    """Run pipeline with dual_adwin, return (y, y_pred, warnings, drift_confirms).

    - warnings : list of warning-start timestamps (used for TP scoring)
    - drift_confirms : list of drift-confirmation timestamps (visualization only)
    """
    df = pd.read_csv(csv_path)
    X = df.drop(columns=["y"]).values.astype(float)
    y = df["y"].values.astype(float)

    cfg = PipelineConfig(
        use_ecpf=True,
        model_type="ht",
        ecpf_signal_mode="dual_adwin",
        ecpf_warning_signal="error",
        ecpf_drift_signal="error",
        ecpf_warning_detector="adwin",
        ecpf_drift_detector="adwin",
        ecpf_max_pool_size=10,
    )
    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[:warm_start], y[:warm_start])

    y_pred = np.full(len(y), np.nan)
    drift_confirms: list[int] = []
    prev_n_detections = 0

    for i in range(warm_start, len(y)):
        yp, _, _ = pipe.step(X[i], y[i], index=i)
        y_pred[i] = yp

        # Drift confirmation: new entry in pipe.detections at step i
        if len(pipe.detections) > prev_n_detections:
            drift_confirms.append(int(i))
            prev_n_detections = len(pipe.detections)

    # In ECPF dual_adwin, each DriftDetection.timestamp = warning_start_idx
    # so warnings[i] pairs 1-to-1 with drift_confirms[i].
    warnings = [int(d.timestamp) for d in pipe.detections]
    return y, y_pred, warnings, drift_confirms


def main():
    print(f"V2 trial: dual_adwin on {len(TRIAL_DATASETS)} datasets")
    print(f"Output dir: {OUT_DIR}")
    print("=" * 60)

    all_results = []
    detection_results = {}  # warning timestamps per dataset
    interval_map = {}
    extra_info = {}  # drift_confirms, y_pred path, etc.

    for rel in TRIAL_DATASETS:
        csv_path = ROOT / rel
        if not csv_path.exists():
            print(f"  SKIP (not found): {rel}")
            continue

        intervals = _load_intervals(csv_path)
        print(f"\n  {csv_path.name}  ({len(intervals)} drifts)")
        t0 = time.time()
        y, y_pred, warnings, drift_confirms = run_one(csv_path)
        elapsed = time.time() - t0
        print(f"    warnings        : {warnings}")
        print(f"    drift confirms  : {drift_confirms}")
        print(f"    elapsed         : {elapsed:.1f}s")

        # TP scoring uses WARNING timestamps
        pert = build_perturbation_intervals(intervals, extension=1000)
        cd = compute_correct_detection(warnings, pert)
        score_str = f"{cd.score_percent:.1f}%" if cd.score_percent is not None else "n/a"
        print(f"    score@ext=1000  : {score_str} (TP={cd.tp} FP={cd.fp} N={cd.n_intervals})")

        # Save y_pred for chart regeneration
        ypred_path = OUT_DIR / "ypred_cache" / f"{csv_path.stem}.npz"
        ypred_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(ypred_path, y=y, y_pred=y_pred)

        detection_results[str(csv_path)] = warnings
        interval_map[str(csv_path)] = intervals
        extra_info[str(csv_path)] = {
            "warnings": warnings,
            "drift_confirms": drift_confirms,
            "ypred_cache": str(ypred_path),
            "elapsed": elapsed,
        }
        all_results.append({
            "dataset": csv_path.name,
            "n_intervals": len(intervals),
            "n_warnings": len(warnings),
            "n_drift_confirms": len(drift_confirms),
            "score_fixed1000": cd.score_percent or 0.0,
        })

    print("\n" + "=" * 60)
    print("Phase 2: Find optimal extension per dataset")
    print("=" * 60)
    opt_map = {}
    for csv_str, warnings in detection_results.items():
        intervals = interval_map[csv_str]
        opt = find_optimal_extension(warnings, intervals)
        opt_map[csv_str] = opt
        print(f"  {Path(csv_str).name}: optimal_ext={opt}")

    print("\n" + "=" * 60)
    print("Phase 3: Build training data + fit RF")
    print("=" * 60)
    X_train, y_train, meta = build_training_data(
        str(ROOT / "data"),
        detection_results=detection_results,
        use_stream_features=True,
    )
    print(f"  Training samples: {len(X_train)}")
    print(f"  Features: {X_train.shape[1]}")
    print(f"  Labels (optimal ext): {y_train.tolist()}")

    estimator = AdaptiveWindowEstimator(n_estimators=100, random_state=42)
    if len(X_train) >= 3:
        mae = estimator.cross_val_mae(X_train, y_train)
        print(f"  LOO CV MAE: {mae:.0f} samples")
    estimator.fit(X_train, y_train)

    model_path = ROOT / "models" / "adaptive_window_rf_v2.pkl"
    model_path.parent.mkdir(exist_ok=True)
    estimator.save(model_path)
    print(f"  Model saved → {model_path}")

    print("\n" + "=" * 60)
    print("Phase 4: Compare fixed vs adaptive per dataset")
    print("=" * 60)
    comparison = []
    for csv_str, warnings in detection_results.items():
        intervals = interval_map[csv_str]
        wf = WindowFeatures.from_csv(csv_str, intervals)
        pred_ext = estimator.predict_extension(wf)
        score_fixed = (compute_correct_detection(
            warnings, build_perturbation_intervals(intervals, extension=1000)
        ).score_percent or 0.0)
        score_adapt = (compute_correct_detection(
            warnings, build_perturbation_intervals(intervals, extension=pred_ext)
        ).score_percent or 0.0)
        score_oracle = (compute_correct_detection(
            warnings, build_perturbation_intervals(intervals, extension=opt_map[csv_str])
        ).score_percent or 0.0)
        comparison.append({
            "dataset": Path(csv_str).name,
            "predicted_ext": pred_ext,
            "optimal_ext": opt_map[csv_str],
            "score_fixed": round(score_fixed, 1),
            "score_adaptive": round(score_adapt, 1),
            "score_oracle": round(score_oracle, 1),
        })

    df_cmp = pd.DataFrame(comparison)
    print(df_cmp.to_string(index=False))

    # Save state for chart-generation step
    state = {
        "detection_results": detection_results,
        "interval_map": {k: v for k, v in interval_map.items()},
        "opt_map": opt_map,
        "comparison": comparison,
        "extra_info": extra_info,
        "feature_importances": estimator.feature_importances().tolist(),
        "loo_mae": mae if len(X_train) >= 3 else None,
    }

    # Pickle-safe: convert tuples to lists
    def _clean(o):
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_clean(x) for x in o]
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        return o

    (OUT_DIR / "experiment_state.json").write_text(json.dumps(_clean(state), indent=2))
    print(f"\nState saved → {OUT_DIR / 'experiment_state.json'}")


if __name__ == "__main__":
    main()
