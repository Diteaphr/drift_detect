"""
Run the full concept drift pipeline: synthetic stream → detectors → model adaptation → evaluation.
"""

import numpy as np
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline, run_pipeline_demo
from tests.evaluation import evaluate_detectors, evaluate_drift_type_classifier, prediction_metrics


def main():
    print("=== Concept Drift Pipeline Demo ===\n")

    # 1) Run pipeline on synthetic stream with known drift points
    n_samples = 10000  # Larger sample size for multiple drifts
    # Ground truth drift points
    drift_at = [2000, 4000, 6000, 8000]  
    
    # Try to use river dataset, fallback to manual if not available
    use_river_dataset = True
    print(f"Running pipeline on synthetic stream ({n_samples} samples) with river ConceptDrift dataset...")
    pipeline, y_true, y_pred = run_pipeline_demo(n_samples=n_samples, drift_at=drift_at, seed=42, use_river=use_river_dataset)

    # 2) Offline evaluation: drift detectors
    print("\n--- Drift detector evaluation ---")
    detections = pipeline.detections
    eval_det = evaluate_detectors(detections, ground_truth_drift_times=drift_at, tolerance=300) # Give room to detect
    print(f"Detections: {eval_det['n_detections']}")
    print(f"By type: {eval_det['by_type']}")
    if eval_det.get("precision") is not None:
        print(f"Precision: {eval_det['precision']:.3f}, Recall: {eval_det['recall']:.3f}, F1: {eval_det['f1']:.3f}")

    # 3) Offline evaluation: drift type classifier (sudden vs gradual)
    print("\n--- Drift type classifier evaluation ---")
    eval_clf = evaluate_drift_type_classifier(
        detections,
        ground_truth_sudden=drift_at[:1],
        ground_truth_gradual=drift_at[1:],
        tolerance=60,
    )
    print(f"Classified (non-recurring): {eval_clf['n_classified']} (sudden: {eval_clf['n_sudden']}, gradual: {eval_clf['n_gradual']})")
    if eval_clf.get("accuracy_vs_gt") is not None:
        print(f"Accuracy vs ground truth: {eval_clf['accuracy_vs_gt']:.3f}")

    # 4) Prediction quality
    print("\n--- Prediction metrics ---")
    m = prediction_metrics(y_true, y_pred, window=100)
    print(f"MAE (over stream): {m['mae']:.4f}")
    if m["rolling_mae"]:
        print(f"Rolling MAE (last window): {m['rolling_mae'][-1]:.4f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
