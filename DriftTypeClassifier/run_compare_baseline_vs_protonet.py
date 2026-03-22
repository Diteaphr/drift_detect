#!/usr/bin/env python3
"""
Compare baseline (RandomForest / MLP) vs FAN ProtoNet.
Ablation: exact vs noisy alerts, gap-only vs gap+extra.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.dataset_builder import build_and_save
from src.baseline import train_baseline_rf, train_baseline_mlp, evaluate_baseline
from src.evaluate import run_evaluate, evaluate
from src.models import build_protonet
import torch


def main():
    root = Path(__file__).resolve().parent
    config = {
        "n_streams": 300,
        "streams_per_class": 100,
        "stream_length": 2000,
        "n_features": 10,
        "pre_window": 150,
        "post_window": 150,
        "n_subwindows": 15,
        "use_extra_features": False,
        "alert_noise_radius": 20,
        "train_ratio": 0.7,
        "val_ratio": 0.15,
        "test_ratio": 0.15,
        "random_seed": 42,
    }

    print("Building dataset (noisy alerts, gap-only)...")
    build_and_save(root / "data", config)
    data = np.load(root / "data" / "dataset.npz")
    X = data["X"]
    y = data["y"]
    train_idx = data["train_idx"]
    test_idx = data["test_idx"]
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    print("\n--- Baseline: RandomForest ---")
    rf = train_baseline_rf(X_train, y_train)
    metrics_rf = evaluate_baseline(rf, X_test, y_test)
    print(f"  Accuracy: {metrics_rf['accuracy']:.4f}  Macro F1: {metrics_rf['macro_f1']:.4f}")

    print("\n--- Baseline: MLP ---")
    mlp = train_baseline_mlp(X_train, y_train)
    metrics_mlp = evaluate_baseline(mlp, X_test, y_test)
    print(f"  Accuracy: {metrics_mlp['accuracy']:.4f}  Macro F1: {metrics_mlp['macro_f1']:.4f}")

    print("\n--- FAN ProtoNet (run train.py first, then evaluate) ---")
    ckpt_path = root / "checkpoints" / "best.pt"
    if ckpt_path.exists():
        metrics_pn = run_evaluate(ckpt_path, root / "data")
        print(f"  Accuracy: {metrics_pn['accuracy']:.4f}  Macro F1: {metrics_pn['macro_f1']:.4f}")
    else:
        print("  No checkpoint found. Run: python -m src.train")

    print("\nDone.")


if __name__ == "__main__":
    main()
