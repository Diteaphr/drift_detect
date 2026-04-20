"""
model_adapter.py
================
Adapter that wraps a ``BaseModel`` (from the IM concept-drift model library)
so it can be used seamlessly inside ``ConceptDriftPipeline`` in place of the
original ``PredictionModel``.

The pipeline expects these methods:
    predict(X)  fit(X, y)  partial_fit(X, y)  fine_tune(X, y)
    retrain(X, y)  get_model()  set_model(model)

``BaseModel`` provides:
    predict(X)  fit(X, y)  learn_one(x, y)  predict_one(x)  save()  load()

This adapter bridges the gap.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any, Dict, Optional, Tuple, Type

import numpy as np

from .models.base_model import BaseModel
from .models import (
    ElasticNetModel,
    RandomForestModel,
    XGBoostModel,
    GRUModel,
    HoeffdingTreeModel,
)

logger = logging.getLogger(__name__)

_MODEL_REGISTRY: Dict[str, Tuple[Type[BaseModel], Dict[str, Any]]] = {
    "elastic": (ElasticNetModel, {}),
    "rf":      (RandomForestModel, {"n_models": 10, "seed": 42}),
    "xgb":     (XGBoostModel, {"buffer_size": 50, "num_boost_round": 50}),
    "gru":     (GRUModel, {"input_size": 4, "hidden_size": 32, "window_size": 10}),
    # Plain Hoeffding Tree (no internal drift handling) — for ECPF-style
    # external concept-management experiments.
    "ht":      (HoeffdingTreeModel, {"grace_period": 200, "leaf_prediction": "nba"}),
}

ADVANCED_MODEL_TYPES = set(_MODEL_REGISTRY.keys())


def is_advanced_model_type(model_type: str) -> bool:
    """Return True if *model_type* refers to one of the BaseModel models."""
    return model_type in ADVANCED_MODEL_TYPES


def create_base_model(model_type: str, model_kwargs: Optional[Dict[str, Any]] = None) -> BaseModel:
    """Instantiate a BaseModel from a registry key (e.g. 'rf', 'xgb')."""
    if model_type not in _MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model_type={model_type!r}. "
            f"Choose from {list(_MODEL_REGISTRY.keys())}"
        )
    cls, defaults = _MODEL_REGISTRY[model_type]
    merged = {**defaults, **(model_kwargs or {})}
    return cls(**merged)


class BaseModelAdapter:
    """Wrap a ``BaseModel`` to present the same interface as ``PredictionModel``.

    Key behaviour differences vs. the original ``PredictionModel``:

    *   ``partial_fit`` / ``fine_tune`` call ``learn_one`` per sample
        (true single-sample streaming) instead of sklearn's ``partial_fit``.
    *   ``predict`` converts numpy to dict internally, then back.
    *   No scaler — BaseModel implementations handle normalisation themselves
        (e.g. ``ElasticNetModel`` uses River's ``StandardScaler``).

    Parameters
    ----------
    model_type : str
        One of ``'elastic'``, ``'rf'``, ``'xgb'``, ``'gru'``.
    model_kwargs : dict, optional
        Extra kwargs forwarded to the model constructor.
    buffer_maxlen : int
        Rolling buffer size for post-drift retraining data.
    """

    def __init__(
        self,
        model_type: str = "rf",
        model_kwargs: Optional[Dict[str, Any]] = None,
        buffer_maxlen: int = 1000,
    ) -> None:
        self.model_type = model_type
        self._model_kwargs = model_kwargs or {}
        self._base_model: BaseModel = create_base_model(model_type, model_kwargs)
        self.buffer_maxlen = buffer_maxlen
        self.data_buffer: deque[Tuple[Dict[str, float], Any, int]] = deque(
            maxlen=buffer_maxlen,
        )
        self._samples_seen: int = 0

    # ------------------------------------------------------------------
    # PredictionModel-compatible interface
    # ------------------------------------------------------------------
    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        return self._base_model.predict(X)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseModelAdapter":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self._base_model.fit(X, y)
        return self

    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> "BaseModelAdapter":
        """True streaming update: calls ``learn_one`` for every sample."""
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        for i in range(len(y)):
            x_dict = BaseModel._to_dict(X[i])
            self._base_model.learn_one(x_dict, y[i])
        return self

    def fine_tune(self, X: np.ndarray, y: np.ndarray) -> "BaseModelAdapter":
        return self.partial_fit(X, y)

    def retrain(self, X: np.ndarray, y: np.ndarray) -> "BaseModelAdapter":
        return self.fit(X, y)

    # ------------------------------------------------------------------
    # Streaming interface (used by the enhanced pipeline)
    # ------------------------------------------------------------------
    def predict_one(self, x: np.ndarray) -> Any:
        x_dict = BaseModel._to_dict(x)
        return self._base_model.predict_one(x_dict)

    def learn_one(self, x: np.ndarray, y: Any) -> None:
        x_dict = BaseModel._to_dict(x)
        self._base_model.learn_one(x_dict, y)

    def update(self, x: np.ndarray, y: Any) -> Any:
        """Test-then-train on a single sample. Also stores to rolling buffer."""
        pred = self.predict_one(x)
        self.learn_one(x, y)
        self.data_buffer.append((BaseModel._to_dict(x), y, self._samples_seen))
        self._samples_seen += 1
        return pred

    # ------------------------------------------------------------------
    # Model pool / persistence helpers
    # ------------------------------------------------------------------
    def get_model(self) -> BaseModel:
        return self._base_model

    def set_model(self, model: BaseModel) -> None:
        self._base_model = model

    def create_fresh_model(self) -> BaseModel:
        """Create a new instance of the same model type (for post-drift reset)."""
        return create_base_model(self.model_type, self._model_kwargs)

    def reset_model(self) -> None:
        """Replace the internal model with a fresh instance."""
        self._base_model = self.create_fresh_model()

    def retrain_from_buffer(self, timestamp: int) -> None:
        """Hard retrain: filter buffer for samples after *timestamp*, then fit."""
        post_drift = [(x, y) for x, y, idx in self.data_buffer if idx >= timestamp]
        if not post_drift:
            logger.warning(
                "No post-drift data for retraining (timestamp=%d)", timestamp
            )
            return
        X_np = BaseModel._to_numpy([x for x, _ in post_drift])
        y_np = np.array([y for _, y in post_drift])
        fresh = self.create_fresh_model()
        fresh.fit(X_np, y_np)
        self._base_model = fresh
        logger.info(
            "Retrained %s on %d post-drift samples (t>=%d)",
            self.model_type, len(post_drift), timestamp,
        )

    def __repr__(self) -> str:
        return (
            f"BaseModelAdapter(type={self.model_type!r}, "
            f"model={self._base_model!r}, "
            f"seen={self._samples_seen})"
        )
