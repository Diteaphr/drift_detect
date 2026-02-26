"""
Prediction model wrapper: supports linear (retrain) and nonlinear (fine-tune)
for incremental adaptation from the model pool.
"""

import numpy as np
from typing import Optional, Any


def _make_linear_model():
    try:
        from sklearn.linear_model import SGDRegressor
        return SGDRegressor(max_iter=500, warm_start=True, random_state=42, tol=1e-3)
    except ImportError:
        from sklearn.linear_model import LinearRegression
        return LinearRegression()


def _make_nonlinear_model():
    try:
        from sklearn.neural_network import MLPRegressor
        return MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=1, warm_start=True, random_state=42)
    except ImportError:
        return _make_linear_model()


class PredictionModel:
    """
    Wrapper around a regressor. Supports:
    - predict(X)
    - retrain (linear): fit from scratch on new data
    - fine_tune (nonlinear): partial_fit / additional fit on new data
    """

    def __init__(self, model_type: str = "linear"):
        self.model_type = model_type.lower()
        if self.model_type == "linear":
            self._model = _make_linear_model()
        else:
            self._model = _make_nonlinear_model()

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        return self._model.predict(X).ravel()

    def fit(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self._model.fit(X, y)
        return self

    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if hasattr(self._model, "partial_fit"):
            self._model.partial_fit(X, y)
        else:
            self._model.fit(X, y)
        return self

    def retrain(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        """Full retrain (for linear): fit from scratch."""
        return self.fit(X, y)

    def fine_tune(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        """Incremental update (for nonlinear): partial_fit."""
        return self.partial_fit(X, y)

    def get_model(self) -> Any:
        return self._model

    def set_model(self, model: Any) -> None:
        self._model = model
