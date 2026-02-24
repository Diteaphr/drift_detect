"""
Offline evaluation: evaluate drift detectors and drift type classifier
using stored detections and (optionally) ground-truth drift labels.
"""

import numpy as np
from typing import List, Optional, Tuple

from config import DriftDetection, DriftType


def evaluate_detectors(
    detections: List[DriftDetection],
    ground_truth_drift_times: Optional[List[int]] = None,
    tolerance: int = 30,
) -> dict:
    """
    Evaluate drift detector outputs.
    If ground_truth_drift_times is given, compute precision/recall around those times.
    """
    out = {
        "n_detections": len(detections),
        "by_type": {},
        "precision": None,
        "recall": None,
        "f1": None,
    }
    for dt in DriftType:
        if dt == DriftType.NONE:
            continue
        count = sum(1 for d in detections if d.drift_type == dt)
        out["by_type"][dt.value] = count

    if not ground_truth_drift_times:
        return out

    # Match detections to nearest ground truth within tolerance
    detected_gt = set()
    for d in detections:
        for gt in ground_truth_drift_times:
            if abs(d.timestamp - gt) <= tolerance:
                detected_gt.add(gt)
                break
    n_gt = len(ground_truth_drift_times)
    n_det = len(detections)
    tp = len(detected_gt)
    if n_det > 0:
        out["precision"] = tp / n_det
    else:
        out["precision"] = 0.0
    if n_gt > 0:
        out["recall"] = tp / n_gt
    else:
        out["recall"] = 1.0
    p, r = out["precision"], out["recall"]
    if p + r > 0:
        out["f1"] = 2 * p * r / (p + r)
    else:
        out["f1"] = 0.0
    return out


def evaluate_drift_type_classifier(
    detections: List[DriftDetection],
    ground_truth_sudden: Optional[List[int]] = None,
    ground_truth_gradual: Optional[List[int]] = None,
    tolerance: int = 30,
) -> dict:
    """
    Evaluate how well we classified drift type (sudden vs gradual).
    Only considers detections that are not recurring (i.e. we classified them).
    """
    non_recurring = [d for d in detections if d.drift_type in (DriftType.SUDDEN, DriftType.GRADUAL)]
    out = {
        "n_classified": len(non_recurring),
        "n_sudden": sum(1 for d in non_recurring if d.drift_type == DriftType.SUDDEN),
        "n_gradual": sum(1 for d in non_recurring if d.drift_type == DriftType.GRADUAL),
        "accuracy_vs_gt": None,
    }
    if not ground_truth_sudden:
        ground_truth_sudden = []
    if not ground_truth_gradual:
        ground_truth_gradual = []

    def match_gt(timestamp: int) -> Optional[str]:
        for gt in ground_truth_sudden:
            if abs(timestamp - gt) <= tolerance:
                return "sudden"
        for gt in ground_truth_gradual:
            if abs(timestamp - gt) <= tolerance:
                return "gradual"
        return None

    correct = 0
    for d in non_recurring:
        gt_type = match_gt(d.timestamp)
        if gt_type and d.drift_type.value == gt_type:
            correct += 1
    if non_recurring:
        out["accuracy_vs_gt"] = correct / len(non_recurring)
    return out


def prediction_metrics(y_true: np.ndarray, y_pred: np.ndarray, window: int = 200) -> dict:
    """Compute MAE and optionally rolling MAE over the stream."""
    mask = np.isfinite(y_pred)
    if not np.any(mask):
        return {"mae": np.nan, "rolling_mae": []}
    y_t = np.asarray(y_true)[mask]
    y_p = np.asarray(y_pred)[mask]
    mae = float(np.mean(np.abs(y_t - y_p)))
    rolling = []
    for i in range(window, len(y_p) + 1):
        rolling.append(float(np.mean(np.abs(y_t[i - window : i] - y_p[i - window : i]))))
    return {"mae": mae, "rolling_mae": rolling}
