"""
Trial: run pipeline on a small subset of labeled datasets, collect detection
timestamps, train AdaptiveWindowEstimator, and compare fixed vs adaptive extension.

Usage:
    python scripts/trial_adaptive_window.py
"""

from __future__ import annotations

import ast
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline, load_drift_intervals_file
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

# ── dataset selection ─────────────────────────────────────────────────────────
TRIAL_DATASETS = [
    "data/sudden_drift/recurring_sudden_sea100k_g00.csv",
    "data/sudden_drift/recurring_sudden_sea100k_g01.csv",
    "data/gradual_drift/recurring_gradual_sea100k_g00.csv",
    "data/gradual_drift/recurring_gradual_sea100k_g01.csv",
    "data/incremental_drift/incremental_hyperplane_100k_g00.csv",
    "data/incremental_drift/incremental_hyperplane_100k_g01.csv",
    "data/recurring_drift/recurring_sud_sea100k_g00.csv",
    "data/recurring_drift/recurring_sud_sea100k_g01.csv",
]

ROOT = Path(__file__).resolve().parents[1]


def _load_drift_intervals(txt_path: Path):
    raw = txt_path.read_text().strip()
    return [(int(a), int(b)) for a, b in ast.literal_eval(raw)]


def run_one(csv_path: Path, warm_start: int = 200) -> list[int]:
    """Run pipeline on one CSV with a real (non-oracle) meta-detector.

    Uses DynamicWeightedVoting without ECPF so the detector fires with
    realistic latency after the true drift — this is the scenario where
    the extension actually matters.
    """
    df = pd.read_csv(csv_path)
    X = df.drop(columns=["y"]).values.astype(float)
    y = df["y"].values.astype(float)

    cfg = PipelineConfig(
        use_ecpf=False,
        model_type="ht",
        meta_detector_type="dynamic_weighted",
    )
    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[:warm_start], y[:warm_start])

    for i in range(warm_start, len(y)):
        pipe.step(X[i], y[i], index=i)

    return [d.timestamp for d in pipe.detections]


def score_extension(det_ts: list[int], intervals, ext: int) -> float:
    pert = build_perturbation_intervals(intervals, extension=ext)
    r = compute_correct_detection(det_ts, pert)
    return r.score_percent if r.score_percent is not None else 0.0


# ─────────────────────────────────────────────────────────────────────────────

def main():
    detection_results: dict[str, list[int]] = {}
    interval_map: dict[str, list] = {}

    print("=" * 60)
    print("Phase 1: Run pipeline on each dataset")
    print("=" * 60)

    for rel in TRIAL_DATASETS:
        csv_path = ROOT / rel
        if not csv_path.exists():
            print(f"  SKIP (not found): {rel}")
            continue

        txt_path = csv_path.with_name(csv_path.stem + "_drift_times.txt")
        intervals = _load_drift_intervals(txt_path)

        print(f"\n  {csv_path.name}  ({len(intervals)} drifts)")
        t0 = time.time()
        det_ts = run_one(csv_path)
        elapsed = time.time() - t0
        print(f"    detections: {det_ts}")
        print(f"    elapsed:    {elapsed:.1f}s")

        score_fixed = score_extension(det_ts, intervals, ext=1000)
        print(f"    score@ext=1000: {score_fixed:.1f}%")

        detection_results[str(csv_path)] = det_ts
        interval_map[str(csv_path)] = intervals

    print("\n" + "=" * 60)
    print("Phase 2: Find optimal extension per dataset (sweep)")
    print("=" * 60)

    opt_map: dict[str, int] = {}
    for csv_str, det_ts in detection_results.items():
        intervals = interval_map[csv_str]
        opt = find_optimal_extension(det_ts, intervals)
        opt_map[csv_str] = opt
        name = Path(csv_str).name
        score_opt = score_extension(det_ts, intervals, ext=opt)
        score_fixed = score_extension(det_ts, intervals, ext=1000)
        print(f"  {name}: optimal_ext={opt}  score@1000={score_fixed:.1f}%  score@opt={score_opt:.1f}%")

    print("\n" + "=" * 60)
    print("Phase 3: Build training data + fit RF")
    print("=" * 60)

    X, y, meta = build_training_data(
        str(ROOT / "data"),
        detection_results=detection_results,
        use_stream_features=True,
    )
    print(f"  Training samples: {len(X)}")
    print(f"  Features: {X.shape[1]}")
    print(f"  Labels (optimal ext): {y.tolist()}")

    estimator = AdaptiveWindowEstimator(n_estimators=100, random_state=42)
    if len(X) >= 3:
        mae = estimator.cross_val_mae(X, y)
        print(f"  LOO CV MAE: {mae:.0f} samples")
    estimator.fit(X, y)

    # Save model
    model_path = ROOT / "models" / "adaptive_window_rf.pkl"
    model_path.parent.mkdir(exist_ok=True)
    estimator.save(model_path)
    print(f"  Model saved → {model_path}")

    print("\n" + "=" * 60)
    print("Phase 4: Compare fixed=1000 vs RF-adaptive per dataset")
    print("=" * 60)

    rows = []
    for csv_str, det_ts in detection_results.items():
        intervals = interval_map[csv_str]
        wf = WindowFeatures.from_csv(csv_str, intervals)
        pred_ext = estimator.predict_extension(wf)
        score_fixed = score_extension(det_ts, intervals, ext=1000)
        score_adaptive = score_extension(det_ts, intervals, ext=pred_ext)
        score_oracle = score_extension(det_ts, intervals, ext=opt_map[csv_str])
        name = Path(csv_str).name
        rows.append({
            "dataset": name,
            "predicted_ext": pred_ext,
            "optimal_ext": opt_map[csv_str],
            "score@fixed": round(score_fixed, 1),
            "score@adaptive": round(score_adaptive, 1),
            "score@oracle": round(score_oracle, 1),
        })
        print(
            f"  {name}\n"
            f"    ext: fixed=1000  predicted={pred_ext}  optimal={opt_map[csv_str]}\n"
            f"    score: fixed={score_fixed:.1f}%  adaptive={score_adaptive:.1f}%  oracle={score_oracle:.1f}%"
        )

    # Summary table
    df_res = pd.DataFrame(rows)
    print("\n--- Summary ---")
    print(df_res.to_string(index=False))

    avg_fixed = df_res["score@fixed"].mean()
    avg_adaptive = df_res["score@adaptive"].mean()
    avg_oracle = df_res["score@oracle"].mean()
    print(f"\nAverage score:  fixed={avg_fixed:.1f}%  adaptive={avg_adaptive:.1f}%  oracle={avg_oracle:.1f}%")

    # Feature importances
    fi = estimator.feature_importances()
    if fi is not None:
        feat_names = [
            "drift_type", "width_mean", "width_std", "n_drifts",
            "inter_gap", "density", "pre_var_mean", "pre_var_std",
            "feat_count", "label_entropy",
        ][:len(fi)]
        print("\nRF Feature importances:")
        for name, imp in sorted(zip(feat_names, fi), key=lambda x: -x[1]):
            print(f"  {name:20s}: {imp:.3f}")


if __name__ == "__main__":
    main()
