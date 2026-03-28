"""
3-class drift type classifier adapter using DriftTypeClassifier assets.

This module intentionally does NOT use `src/drift_type_classifier.py`.
It loads feature extraction from `DriftTypeClassifier/src/feature_extraction.py`,
trains a RandomForest on `DriftTypeClassifier/data/dataset.npz` train split,
and predicts one of: sudden / gradual / incremental.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from .config import DriftType

IDX_TO_DRIFT_TYPE = {
    0: DriftType.SUDDEN,
    1: DriftType.GRADUAL,
    2: DriftType.INCREMENTAL,
}


class DriftTypeClassifierDTCRF:
    """RF classifier trained on DriftTypeClassifier's prepared dataset."""

    def __init__(
        self,
        dtc_root: Optional[Path] = None,
        n_estimators: int = 300,
        random_state: int = 42,
    ):
        repo_root = Path(__file__).resolve().parent.parent
        self.dtc_root = dtc_root or (repo_root / "DriftTypeClassifier")
        self.n_estimators = int(n_estimators)
        self.random_state = int(random_state)

        self._clf: Optional[RandomForestClassifier] = None
        self._feat_dim: Optional[int] = None
        self._extract_features = None
        self._feature_cfg: Dict[str, Any] = {
            "pre_window": 150,
            "post_window": 150,
            "n_subwindows": 15,
            "use_extra_features": False,
        }

    def _load_feature_extractor(self):
        if self._extract_features is not None:
            return self._extract_features
        feat_path = self.dtc_root / "src" / "feature_extraction.py"
        if not feat_path.exists():
            raise FileNotFoundError(f"Feature extraction file not found: {feat_path}")
        spec = importlib.util.spec_from_file_location("dtc_feature_extraction", feat_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load module from: {feat_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._extract_features = module.extract_features
        return self._extract_features

    def fit(self) -> "DriftTypeClassifierDTCRF":
        npz_path = self.dtc_root / "data" / "dataset.npz"
        if not npz_path.exists():
            raise FileNotFoundError(
                f"Expected dataset at {npz_path}. Build DriftTypeClassifier/data first."
            )
        data = np.load(npz_path, allow_pickle=False)
        X = data["X"]
        y = data["y"]
        train_idx = data["train_idx"] if "train_idx" in data else np.arange(len(y))
        X_train = X[train_idx]
        y_train = y[train_idx]
        self._feat_dim = int(X_train.shape[1])
        self._clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
        )
        self._clf.fit(X_train, y_train)
        return self

    def _ensure_fitted(self) -> None:
        if self._clf is None:
            self.fit()

    def _align_feat_dim(self, feat: np.ndarray) -> np.ndarray:
        x = np.asarray(feat, dtype=np.float32).ravel()
        if self._feat_dim is None:
            return x
        if len(x) == self._feat_dim:
            return x
        out = np.zeros(self._feat_dim, dtype=np.float32)
        n = min(self._feat_dim, len(x))
        out[:n] = x[:n]
        return out

    def predict(
        self,
        prediction_errors: np.ndarray,
        drift_timestamp: int,
    ) -> DriftType:
        self._ensure_fitted()
        extract_features = self._load_feature_extractor()
        feat, _ = extract_features(
            np.asarray(prediction_errors, dtype=np.float64),
            int(drift_timestamp),
            self._feature_cfg["pre_window"],
            self._feature_cfg["post_window"],
            self._feature_cfg["n_subwindows"],
            self._feature_cfg["use_extra_features"],
        )
        x = self._align_feat_dim(feat).reshape(1, -1)
        pred_idx = int(self._clf.predict(x)[0])
        return IDX_TO_DRIFT_TYPE.get(pred_idx, DriftType.SUDDEN)


_classifier: Optional[DriftTypeClassifierDTCRF] = None


def classify_drift_type(
    prediction_errors: np.ndarray,
    drift_timestamp: int,
) -> DriftType:
    """Public API for pipeline: return sudden/gradual/incremental."""
    global _classifier
    if _classifier is None:
        _classifier = DriftTypeClassifierDTCRF().fit()
    return _classifier.predict(prediction_errors, drift_timestamp)

