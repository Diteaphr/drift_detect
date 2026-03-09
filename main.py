"""
Run the full concept drift pipeline: synthetic stream → detectors → model adaptation → evaluation.
"""

import numpy as np
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline
from tests.evaluation import evaluate_detectors, evaluate_drift_type_classifier, prediction_metrics
from generate_drift_dataset import create_complex_drift_stream

def main():
    print("=== Concept Drift Pipeline Demo (Complex Dataset) ===\n")

    # 1) Generate the complex stream with multiple drift types
    n_samples = 10000
    print(f"Generating synthetic stream ({n_samples} samples) with Agrawal Sudden, Gradual, and Recurring drifts...")
    X_true, y_true, df_meta = create_complex_drift_stream(n_samples=n_samples, seed=42)
    
    # Ground truth drift points based on our generator setup
    # Sudden at 2500, Gradual center at 5000, Recurring Sudden at 8000
    drift_at_all = [2500, 5000, 8000]
    drift_at_sudden = [2500, 8000]
    drift_at_gradual = [5000]

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
    eval_det = evaluate_detectors(detections, ground_truth_drift_times=drift_at_all, tolerance=300)

    print(f"Detections: {eval_det['n_detections']}")
    print(f"By type: {eval_det['by_type']}")
    if eval_det.get("precision") is not None:
        print(f"Precision: {eval_det['precision']:.3f}, Recall: {eval_det['recall']:.3f}, F1: {eval_det['f1']:.3f}")

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
