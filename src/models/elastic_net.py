"""
elastic_net.py
==============
Model A — Logistic Regression with L1+L2 (Elastic Net) regularization,
built on top of River's online ``LogisticRegression``.

River's ``LogisticRegression`` natively supports ``learn_one`` so this is the
simplest wrapper: every public method delegates almost directly to River.

**Elastic Net implementation note:**
River >=0.21 does not support setting both ``l1`` and ``l2`` simultaneously on
``LogisticRegression``.  We work around this by:

*   Letting River handle the L2 (Ridge) penalty natively — this is applied
    inside the SGD gradient step.
*   Applying the L1 (Lasso) penalty ourselves via a **proximal
    soft-thresholding** step after each ``learn_one`` update.  This is the
    standard Elastic Net / proximal-gradient algorithm used by scikit-learn and
    other frameworks.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
from river import linear_model, optim, preprocessing

from .base_model import BaseModel


class ElasticNetModel(BaseModel):
    """Online Logistic Regression with Elastic-Net regularization.

    The L2 term is delegated to River's built-in SGD, while the L1 term is
    applied as a proximal soft-thresholding step after each weight update.

    Parameters
    ----------
    l1 : float
        L1 (Lasso) regularization strength.  Applied via a manual proximal
        step after every ``learn_one`` call.
    l2 : float
        L2 (Ridge) regularization strength.  Handled natively by River.
    learning_rate : float
        Step size for the SGD optimizer.
    """

    def __init__(
        self,
        l1: float = 0.01,
        l2: float = 0.01,
        learning_rate: float = 0.01,
    ) -> None:
        self.model = linear_model.LogisticRegression(
            optimizer=optim.SGD(lr=learning_rate),
            l2=l2,
            l1=0.0,
        )
        self.scaler = preprocessing.StandardScaler()
        self._l1 = l1
        self._l2 = l2
        self._lr = learning_rate

    # ------------------------------------------------------------------
    # L1 proximal step (Elastic Net)
    # ------------------------------------------------------------------
    def _apply_l1_proximal(self) -> None:
        """Apply soft-thresholding to the model weights for L1 regularization.

        For each weight w_i, the proximal update is::

            w_i ← sign(w_i) * max(|w_i| - λ₁ * lr, 0)
        """
        if self._l1 <= 0:
            return
        threshold = self._l1 * self._lr
        weights = self.model._weights
        for feature, w in list(weights.items()):
            shrunk = float(np.sign(w) * max(abs(w) - threshold, 0.0))
            if shrunk == 0.0:
                del weights[feature]
            else:
                weights[feature] = shrunk

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "ElasticNetModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        for xi, yi in zip(X, y):
            x_dict = self._to_dict(xi)
            self.scaler.learn_one(x_dict)
            x_dict = self.scaler.transform_one(x_dict)
            self.model.learn_one(x_dict, yi)
            self._apply_l1_proximal()
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        preds = []
        for xi in X:
            x_dict = self._to_dict(xi)
            x_dict = self.scaler.transform_one(x_dict)
            proba = self.model.predict_proba_one(x_dict)
            if proba:
                preds.append(max(proba, key=proba.get))
            else:
                preds.append(0)
        return np.array(preds)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "ElasticNetModel":
        x = self._to_dict(x)
        self.scaler.learn_one(x)
        x = self.scaler.transform_one(x)
        self.model.learn_one(x, y)
        self._apply_l1_proximal()
        return self

    def predict_one(self, x: Dict[str, float]) -> Any:
        x = self._to_dict(x)
        x = self.scaler.transform_one(x)
        proba = self.model.predict_proba_one(x)
        if proba:
            return max(proba, key=proba.get)
        return 0

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "ElasticNetModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"ElasticNetModel(l1={self._l1}, l2={self._l2}, lr={self._lr})"
        )
