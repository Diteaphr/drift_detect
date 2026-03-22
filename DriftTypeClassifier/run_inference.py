#!/usr/bin/env python3
"""Example: load model + support set, run inference on a synthetic stream with alerts."""

import sys
from pathlib import Path
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.generators import generate_sudden_streams
from src.inference import predict_drift_types_with_prototypes
from src.models import build_protonet
from src.dataset_builder import build_dataset_from_streams, CLASS_TO_IDX


def main():
    root = Path(__file__).resolve().parent
    ckpt = torch.load(root / "checkpoints" / "best.pt", map_location="cpu")
    config = ckpt.get("config", {})

    data = np.load(root / "data" / "dataset.npz")
    X_all = data["X"]
    y_all = data["y"]
    train_idx = data["train_idx"]
    # Use a small support set from training data (one K_shot per class)
    X_train = X_all[train_idx]
    y_train = y_all[train_idx]
    support_idx = []
    for c in range(3):
        idx = np.where(y_train == c)[0][:5]
        support_idx.extend(idx.tolist())
    support_X = X_train[support_idx]
    support_y = y_train[support_idx]

    model = build_protonet(
        seq_len=support_X.shape[1],
        input_dim=1,
        d_model=config.get("d_model", 64),
        n_heads=config.get("n_heads", 4),
        n_layers=config.get("n_layers", 3),
        dim_feedforward=config.get("dim_feedforward", 128),
        dropout=0.0,
        embed_dim=config.get("embed_dim", 64),
        n_way=3,
    )
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    # Create one sudden stream and use its true drift as alert
    streams = generate_sudden_streams(2, 2000, 10, random_seed=999)
    s = streams[0]
    alert_timestamps = [s.t_drift]

    pred_labels, probs, features = predict_drift_types_with_prototypes(
        s.X, s.y, alert_timestamps, model, support_X, support_y, config,
    )
    print("Alert at", alert_timestamps[0], "-> predicted:", pred_labels[0], "true: sudden")
    print("Probabilities:", probs[0])


if __name__ == "__main__":
    main()
