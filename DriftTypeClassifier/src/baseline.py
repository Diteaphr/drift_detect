"""
Baseline classifiers: RandomForest or MLP on handcrafted (flattened gap + optional extra) features.
"""

import numpy as np
from typing import Optional, Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import f1_score

from .dataset_builder import IDX_TO_CLASS


def train_baseline_rf(
    X_train: np.ndarray,
    y_train: np.ndarray,
    **kwargs: Any,
) -> RandomForestClassifier:
    clf = RandomForestClassifier(n_estimators=100, random_state=42, **kwargs)
    clf.fit(X_train, y_train)
    return clf


def train_baseline_mlp(
    X_train: np.ndarray,
    y_train: np.ndarray,
    hidden_layer_sizes: tuple = (64, 32),
    **kwargs: Any,
) -> MLPClassifier:
    clf = MLPClassifier(
        hidden_layer_sizes=hidden_layer_sizes,
        max_iter=200,
        random_state=42,
        **kwargs,
    )
    clf.fit(X_train, y_train)
    return clf


def evaluate_baseline(
    clf: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> Dict[str, Any]:
    y_pred = clf.predict(X_test)
    acc = float(np.mean(y_pred == y_test))
    p, r, f1, _ = __import__("sklearn.metrics", fromlist=["precision_recall_fscore_support"]).precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0,
    )
    cm = __import__("sklearn.metrics", fromlist=["confusion_matrix"]).confusion_matrix(y_test, y_pred)
    return {
        "accuracy": acc,
        "macro_precision": float(p),
        "macro_recall": float(r),
        "macro_f1": float(f1),
        "confusion_matrix": cm.tolist(),
    }
