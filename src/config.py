"""Shared config and types for the concept drift pipeline."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class DriftType(str, Enum):
    NONE = "none"
    SUDDEN = "sudden"
    GRADUAL = "gradual"
    RECURRING = "recurring"


@dataclass
class DriftDetection:
    """Single drift detection event."""
    timestamp: int
    drift_type: DriftType
    detector_source: str  # "sudden" | "gradual" (which detector fired first)
    raw_drift: bool = True  # True if sudden/gradual fired; False if only recurring/classifier
    details: dict = field(default_factory=dict)

@dataclass
class PipelineConfig:
    """Config for the full pipeline.

    model_type : str
        Which prediction model to use.

        Original (sklearn-based):
            ``"linear"`` — SGDClassifier
            ``"nonlinear"`` — GaussianNB

        Advanced (BaseModel-based, via model_adapter):
            ``"elastic"`` — ElasticNet (River online logistic regression)
            ``"rf"``      — Adaptive Random Forest (River ARF)
            ``"xgb"``     — XGBoost (buffer-based incremental)
            ``"gru"``     — GRU (PyTorch sliding-window online)

    model_kwargs : dict
        Extra keyword arguments forwarded to the model constructor.
        Only used for advanced model types.
    """
    # Preprocessing
    preprocess_window: int = 20
    # Sudden detector
    sudden_window_size: int = 50
    sudden_threshold: float = 2.0
    # Gradual detector
    gradual_window_size: int = 100
    gradual_delta: float = 0.01
    gradual_lambda: float = 0.99
    # Recurring
    recurrence_threshold: float = 0.2
    concept_memory_add_if_new: bool = True
    # Batch / adaptation
    update_batch_size: int = 100
    # Model
    model_type: str = "linear"
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    # Evaluation
    eval_window: int = 200
