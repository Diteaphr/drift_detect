"""
random_forest.py
================
Model B — Adaptive Random Forest (ARF) classifier from the River library.

ARF is specifically designed for concept-drift scenarios.  It maintains an
ensemble of Hoeffding Trees and uses drift detectors (ADWIN by default) to
replace poorly-performing trees automatically.  Like all River models it
supports ``learn_one`` natively.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
from river import forest

from .base_model import BaseModel


class RandomForestModel(BaseModel):
    """Adaptive Random Forest (ARF) classifier — River.

    Parameters
    ----------
    n_models : int
        Number of trees in the forest.
    max_features : str or float
        Maximum fraction / strategy for feature subsampling per tree.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        n_models: int = 10,
        max_features: str = "sqrt",
        seed: int | None = 42,
    ) -> None:
        self.model = forest.ARFClassifier(
            n_models=n_models,
            max_features=max_features,
            seed=seed,
        )
        self._n_models = n_models
        self._max_features = max_features
        self._seed = seed

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "RandomForestModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        for xi, yi in zip(X, y):
            x_dict = self._to_dict(xi)
            self.model.learn_one(x_dict, yi)
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        preds = []
        for xi in X:
            x_dict = self._to_dict(xi)
            pred = self.model.predict_one(x_dict)
            preds.append(pred if pred is not None else 0)
        return np.array(preds)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "RandomForestModel":
        x = self._to_dict(x)
        self.model.learn_one(x, y)
        return self

    def predict_one(self, x: Dict[str, float]) -> Any:
        x = self._to_dict(x)
        pred = self.model.predict_one(x)
        return pred if pred is not None else 0

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "RandomForestModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"RandomForestModel(n_models={self._n_models}, "
            f"max_features={self._max_features!r}, seed={self._seed})"
        )
