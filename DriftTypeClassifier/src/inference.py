"""
Inference: given stream (X, y) and alert timestamps, predict drift type per alert.
"""

import numpy as np
import torch
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .stream_simulator import run_online_classifier
from .feature_extraction import extract_features
from .models import build_protonet
from .dataset_builder import CLASS_TO_IDX, IDX_TO_CLASS


def predict_drift_types_for_alerts(
    X: np.ndarray,
    y: np.ndarray,
    alert_timestamps: List[int],
    model: torch.nn.Module,
    support_X: np.ndarray,
    support_y: np.ndarray,
    config: Dict[str, Any],
    base_classifier_warm_start: int = 50,
    device: Optional[torch.device] = None,
) -> Tuple[List[str], np.ndarray, np.ndarray]:
    """
    High-level API: given stream (X, y) and alert timestamps, return predicted drift types,
    class probabilities, and extracted features. Uses provided support set for ProtoNet.
    """
    return predict_drift_types_with_prototypes(
        X, y, alert_timestamps, model, support_X, support_y, config, device,
    )


def predict_drift_types_with_prototypes(
    X: np.ndarray,
    y: np.ndarray,
    alert_timestamps: List[int],
    model: torch.nn.Module,
    support_X: np.ndarray,
    support_y: np.ndarray,
    config: Dict[str, Any],
    device: Optional[torch.device] = None,
) -> Tuple[List[str], np.ndarray, np.ndarray]:
    """
    Same as above but use provided support set to compute prototypes, then classify each alert.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()

    sim = run_online_classifier(X, y, warm_start=config.get("warm_start", 50))
    pre_window = config.get("pre_window", 150)
    post_window = config.get("post_window", 150)
    n_subwindows = config.get("n_subwindows", 15)
    use_extra = config.get("use_extra_features", False)

    features_list = []
    for t_alert in alert_timestamps:
        feat, _ = extract_features(sim.errors, t_alert, pre_window, post_window, n_subwindows, use_extra)
        features_list.append(feat)
    seq_len = max(len(f) for f in features_list)
    X_alerts = np.zeros((len(features_list), seq_len), dtype=np.float32)
    for i, f in enumerate(features_list):
        X_alerts[i, : len(f)] = f

    support_X_t = torch.from_numpy(support_X).float().to(device)
    support_y_t = torch.from_numpy(support_y).long().to(device)
    query_X_t = torch.from_numpy(X_alerts).float().to(device)
    if support_X_t.dim() == 2:
        support_X_t = support_X_t.unsqueeze(-1)
    if query_X_t.dim() == 2:
        query_X_t = query_X_t.unsqueeze(-1)

    with torch.no_grad():
        logits = model(support_X_t, support_y_t, query_X_t)
        probs = torch.softmax(logits, dim=-1).cpu().numpy()
        pred_idx = logits.argmax(dim=-1).cpu().numpy()

    pred_labels = [IDX_TO_CLASS.get(int(i), "sudden") for i in pred_idx]
    return pred_labels, probs, X_alerts
