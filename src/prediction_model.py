"""
Prediction model wrapper: supports linear (retrain) and nonlinear (fine-tune)
for incremental adaptation from the model pool.
"""

import numpy as np
from typing import Optional, Any
from sklearn.preprocessing import StandardScaler


def _make_linear_model():
    try:
        from sklearn.linear_model import SGDClassifier
        return SGDClassifier(max_iter=500, warm_start=True, random_state=42, tol=1e-3, loss='log_loss')
    except ImportError:
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression()


def _make_nonlinear_model():
    try:
        from sklearn.naive_bayes import GaussianNB
        # Gaussian Naive Bayes supports partial_fit and can model non-linear boundaries probabilistically.
        return GaussianNB()
    except ImportError:
        return _make_linear_model()


class PredictionModel:
    """
    Wrapper around a classifier. Supports:
    - predict(X)
    - predict_proba(X)
    - retrain (linear): fit from scratch on new data
    - fine_tune (nonlinear): partial_fit / additional fit on new data
    """

    def __init__(self, model_type: str = "linear"):
        self.model_type = model_type.lower()
        self.scaler = StandardScaler()
        self._scaler_fitted = False
        if self.model_type == "linear":
            self._model = _make_linear_model()
        else:
            self._model = _make_nonlinear_model()

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if self._scaler_fitted:
            X = self.scaler.transform(X)
        return self._model.predict(X).ravel()

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns probability estimates for classification. Useful for future Uncertainty Module."""
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if self._scaler_fitted:
            X = self.scaler.transform(X)
        if hasattr(self._model, "predict_proba"):
            return self._model.predict_proba(X)
        else:
            # Fallback if model doesn't support probability
            preds = self._model.predict(X)
            probs = np.zeros((len(preds), 2))
            for i, p in enumerate(preds):
                probs[i, int(p)] = 1.0
            return probs

    def fit(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        X = self.scaler.fit_transform(X)
        self._scaler_fitted = True
        self._model.fit(X, y)
        return self

    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if not self._scaler_fitted:
            X = self.scaler.fit_transform(X)
            self._scaler_fitted = True
        else:
            # Incrementally update scaler
            self.scaler.partial_fit(X)
            X = self.scaler.transform(X)

        if hasattr(self._model, "partial_fit"):
            # For classification, we need to provide all possible classes in the first call
            # Assuming binary classification (0, 1) for river's concept drift datasets
            classes = np.array([0, 1])
            try:
                self._model.partial_fit(X, y, classes=classes)
            except TypeError:
                self._model.partial_fit(X, y) # non-classifier fallback
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
