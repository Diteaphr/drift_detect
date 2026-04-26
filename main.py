"""
Run the full concept drift pipeline: syntetic stream → detectors → model adaptation → evaluation.
"""

import numpy as np
import pandas as pd
import ast
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline
from tests.evaluation import (
    correct_detection_from_detections,
    evaluate_detectors,
    evaluate_drift_type_classifier,
    prediction_metrics,
)


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
        # For evaluation, we typically use the midpoint or start of the drift interval
        drift_times = [int((interval[0] + interval[1]) / 2) for interval in drift_intervals]

    return X, y, drift_times, drift_intervals

def main():
    print("=== Concept Drift Pipeline Demo (Real Dataset) ===\n")

    # 1) Load the stream
    data_dir = Path("data/sudden_drift")
    dataset_name = "recurring_sudden_sea100k_g03"
    
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
        meta_ks_window_size=100,
        atom_min_samples=30,
        update_batch_size=1500,
        recurrence_threshold=0.15,
        model_type="rf", # 改用 Random Forest 來捕捉更細微的分佈變化
        meta_detector_type="dynamic_weighted",  # 可以選擇 dynamic_weighted, two_stage, statistical_fusion
        atom_kwargs={ "adwin": { "delta": 0.002 } } # kwargs for ADWIN
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
        source = d.detector_source
        
        # 解析 meta 機制的策略
        dets_info = ""
        if source == "meta_detector" and d.details:
            
            strategy = d.details.get("meta_info", {}).get("strategy_used", "?").upper()
            
            # 取得哪幾個內部演算法投下贊成票
            ensemble_res = d.details.get("ensemble_results", {})
            acting_voters = [det for det, triggered in ensemble_res.items() if triggered]
            votes_str = ", ".join(acting_voters) if acting_voters else "None"
            
            # --- 取得多重代理訊號狀態 (Multi-Indicators) ---
            proxy_info = d.details.get("proxy_indicators", {})
            any_warn = "YES" if proxy_info.get("any_warning") else "NO"
            
            # 解析個別指標狀態 (對應 pipeline 中注入的 0, 1, 2 順序)
            indicator_details = proxy_info.get("details", {})
            ks_warn = "ON" if indicator_details.get("indicator_0", {}).get("warning") else "OFF"
            err_warn = "ON" if indicator_details.get("indicator_1", {}).get("warning") else "OFF"
            uncert_warn = "ON" if indicator_details.get("indicator_2", {}).get("warning") else "OFF"
            
            indicators_str = f"KS:{ks_warn}, ErrTrend:{err_warn}, Uncert:{uncert_warn}"
            
            dets_info = f" | Strategy: {strategy} | ProxyAlarm: {any_warn} ({indicators_str}) | Voters: [{votes_str}]"
            
        print(f"  [!] Meta Alert -> at t={d.timestamp}{dets_info}")

    # 3) Offline evaluation: drift detectors
    print("\n--- Drift detector evaluation ---")
    detections = pipeline.detections
    # Tolerance increased slightly because Gradual drift spans from 4500 to 5500
    eval_det = evaluate_detectors(detections, ground_truth_drift_times=drift_at_all, tolerance=300)

    print(f"Detections: {eval_det['n_detections']}")
    print(f"By type: {eval_det['by_type']}")
    if eval_det.get("precision") is not None:
        print(f"Precision: {eval_det['precision']:.3f}, Recall: {eval_det['recall']:.3f}, F1: {eval_det['f1']:.3f}")

    cd = correct_detection_from_detections(detections, drift_intervals)
    score_str = f"{cd.score_percent:.1f}%" if cd.score_percent is not None else "n/a"
    print(
        f"Correct detection: TP={cd.tp}, FP={cd.fp}, N={cd.n_intervals}, "
        f"score={score_str} ((TP-FP)/N×100, floored at 0%)"
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

    # 6) Plot weight history
    print("\n--- Plotting Meta Detector Weight History ---")
    if hasattr(pipeline.meta_detector, 'plot_weight_history'):
        pipeline.meta_detector.plot_weight_history(
            title="Atom Detectors Weight Variation Over 100k Steps",
            true_drift_intervals=drift_intervals,
            save_path="dynamic_weights_history_plot.html"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
