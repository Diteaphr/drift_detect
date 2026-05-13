"""
Run the full concept drift pipeline: syntetic stream → detectors → model adaptation → evaluation.
"""

import argparse
import ast
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline
from tests.evaluation import evaluate_detectors, evaluate_drift_type_classifier, prediction_metrics


def load_dataset(csv_path: str, drift_times_path: str):
    """Load dataset and ground truth drift times."""
    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    X = df.drop(columns=['y']).values
    y = df['y'].values

    print(f"Loading ground truth drift times from {drift_times_path}...")
    with open(drift_times_path, 'r') as f:
        content = f.read().strip()
        # Parse the nested list format [[start, end], [start, end]]
        drift_intervals = ast.literal_eval(content)
        # Keep midpoint timestamps for precision/recall/F1 (legacy behavior).
        drift_times = [int((interval[0] + interval[1]) / 2) for interval in drift_intervals]

    return X, y, drift_times, drift_intervals


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run concept drift pipeline on a CSV dataset.",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to input CSV (must contain y column).",
    )
    parser.add_argument(
        "--drift-times",
        type=str,
        default=None,
        help="Path to drift times txt file in [[start,end], ...] format.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/sudden_drift",
        help="Directory that contains dataset csv and drift_times txt.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="recurring_sudden_sea100k_g00",
        help="Dataset basename (without extension).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print("=== Concept Drift Pipeline Demo (Real Dataset) ===\n")

    # 1) Load the stream
    if (args.csv is None) ^ (args.drift_times is None):
        print("Error: --csv and --drift-times must be provided together.")
        return

    if args.csv and args.drift_times:
        csv_path = Path(args.csv)
        drift_times_path = Path(args.drift_times)
    else:
        data_dir = Path(args.data_dir)
        dataset_name = args.dataset
        csv_path = data_dir / f"{dataset_name}.csv"
        drift_times_path = data_dir / f"{dataset_name}_drift_times.txt"

    if not csv_path.exists() or not drift_times_path.exists():
        print(f"Error: Could not find {csv_path} or {drift_times_path}")
        return

    X_true, y_true, drift_at_all, drift_intervals = load_dataset(str(csv_path), str(drift_times_path))
    n_samples = len(y_true)
    print(f"Dataset loaded: {n_samples} samples. Ground truth drifts at: {drift_at_all}")
    
    # We don't have separate ground truths for sudden vs gradual in this generic loader
    # but we can pass all of them to sudden for evaluation purposes if we assume they are sudden
    drift_at_sudden = drift_at_all
    drift_at_gradual = []

    # 2) Initialize and run Pipeline
    config = PipelineConfig(
        sudden_window_size=50,
        gradual_window_size=100,
        update_batch_size=1500,
        recurrence_threshold=0.15,
        model_type="linear" # Switch back to linear since SEA is linearly separable
    )
    pipeline = ConceptDriftPipeline(config=config)
    
    print("\nRunning stream through the pipeline...")
    # Warm start the pipeline slightly
    pipeline.warm_start(X_true[:50], y_true[:50])
    
    y_pred = np.zeros(n_samples)
    y_pred[:50] = np.nan
    
    for i in range(50, n_samples):
        y_p, dets, _ = pipeline.step(X_true[i], y_true[i], index=i)
        y_pred[i] = y_p
        # 移除這個每次印出的迴圈，以避免洗頻，但保留進度追蹤
        # for d in dets:
        #     print(f"  [!] Pipeline Alert -> Drift at t={d.timestamp}: {d.drift_type.value} (triggered by: {d.detector_source})")

    for d in pipeline.detections:
        print(f"  [!] Pipeline Alert -> Drift at t={d.timestamp}: {d.drift_type.value} (triggered by: {d.detector_source})")

    # 3) Offline evaluation: drift detectors
    print("\n--- Drift detector evaluation ---")
    detections = pipeline.detections
    # Tolerance increased slightly because Gradual drift spans from 4500 to 5500
    eval_det = evaluate_detectors(
        detections,
        ground_truth_drift_times=drift_at_all,
        ground_truth_drift_intervals=drift_intervals,
        tolerance=300,
    )

    print(f"Detections: {eval_det['n_detections']}")
    print(f"By type: {eval_det['by_type']}")
    if eval_det.get("precision") is not None:
        print(f"Precision: {eval_det['precision']:.3f}, Recall: {eval_det['recall']:.3f}, F1: {eval_det['f1']:.3f}")
    if eval_det.get("correct_detection") is not None:
        cd = eval_det["correct_detection"]
        score = cd["score"]
        score_text = f"{score:.1f}%" if not math.isnan(score) else "nan"
        print(
            f"Correct detection: TP={cd['tp']}, FP={cd['fp']}, N={cd['n']}, "
            f"score={score_text} ((TP-FP)/N×100)"
        )

    # 4) Offline evaluation: drift type classifier (sudden vs gradual)
    print("\n--- Drift type classifier evaluation ---")
    eval_clf = evaluate_drift_type_classifier(
        detections,
        ground_truth_sudden=drift_at_sudden,
        ground_truth_gradual=drift_at_gradual,
        tolerance=500, # Large tolerance to map to the 1000-width Gradual zone
    )
    print(f"Classified (non-recurring): {eval_clf['n_classified']} (sudden: {eval_clf['n_sudden']}, gradual: {eval_clf['n_gradual']})")
    if eval_clf.get("accuracy_vs_gt") is not None:
        print(f"Accuracy vs ground truth: {eval_clf['accuracy_vs_gt']:.3f}")

    # 5) Prediction quality
    print("\n--- Prediction metrics ---")
    m = prediction_metrics(y_true, y_pred, window=100)
    print(f"MAE (over stream): {m['mae']:.4f}")
    if m["rolling_mae"]:
        print(f"Rolling MAE (last window): {m['rolling_mae'][-1]:.4f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
