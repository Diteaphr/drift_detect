"""
base_model.py
=============
Unified abstract interface for all prediction models in the Concept Drift
system.  Every concrete model must inherit from ``BaseModel`` and implement
every abstract method so that the rest of the pipeline can treat all models
interchangeably.
"""

from __future__ import annotations

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np


class BaseModel(ABC):
    """Abstract base class that defines the contract for all prediction models.

    Methods
    -------
    fit(X, y)
        Batch training on an entire dataset (used for initial warm-up).
    predict(X)
        Batch prediction on multiple instances.
    learn_one(x, y)
        Online / incremental update with a single instance — the key method
        for streaming concept-drift scenarios.
    predict_one(x)
        Predict the label for a single instance.
    save(path)
        Persist the model to disk.
    load(path)
        Restore the model from disk.
    """

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    @abstractmethod
    def fit(self, X: Any, y: Any) -> "BaseModel":
        """Train (or re-train) the model on a full batch of data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        y : array-like of shape (n_samples,)

        Returns
        -------
        self
        """
        ...

    @abstractmethod
    def predict(self, X: Any) -> np.ndarray:
        """Return predictions for a batch of instances.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)

        Returns
        -------
        np.ndarray of shape (n_samples,)
        """
        ...

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    @abstractmethod
    def learn_one(self, x: Dict[str, float], y: Any) -> "BaseModel":
        """Update the model with a single observation.

        This is the core method for handling concept drift in a streaming
        setting.  For natively-online models (River) this is a direct call;
        for batch models (XGBoost, PyTorch) this triggers a buffered or
        single-step update.

        Parameters
        ----------
        x : dict
            Feature-name → value mapping for one sample.
        y : int or float
            The true label / target.

        Returns
        -------
        self
        """
        ...

    @abstractmethod
    def predict_one(self, x: Dict[str, float]) -> Any:
        """Predict the label for a single instance.

        Parameters
        ----------
        x : dict
            Feature-name → value mapping for one sample.

        Returns
        -------
        Predicted label (int, float, or similar).
        """
        ...

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        """Serialize the entire model object to *path* using pickle.

        Subclasses may override this to use framework-specific serialization
        (e.g. ``torch.save``, ``xgb.Booster.save_model``).
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "BaseModel":
        """Deserialize a model from *path*.

        Subclasses may override for framework-specific loading.
        """
        with open(path, "rb") as f:
            model = pickle.load(f)
        if not isinstance(model, cls):
            raise TypeError(
                f"Loaded object is {type(model).__name__}, expected {cls.__name__}"
            )
        return model

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _to_dict(x) -> Dict[str, float]:
        """Convert a single sample (numpy array, list, or dict) to a dict
        keyed by feature index.  River models expect ``dict`` inputs.
        """
        if isinstance(x, dict):
            return x
        if isinstance(x, np.ndarray):
            x = x.flatten()
        return {f"f{i}": float(v) for i, v in enumerate(x)}

    @staticmethod
    def _to_numpy(X) -> np.ndarray:
        """Ensure *X* is a 2-D numpy array.  Handles list-of-dicts coming from
        a streaming source as well as plain lists / arrays.
        """
        if isinstance(X, np.ndarray):
            return X if X.ndim == 2 else X.reshape(1, -1)
        if isinstance(X, list) and len(X) > 0 and isinstance(X[0], dict):
            keys = sorted(X[0].keys())
            return np.array([[d[k] for k in keys] for d in X])
        return np.atleast_2d(np.array(X, dtype=np.float32))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
