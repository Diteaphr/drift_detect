"""Shared config and types for the concept drift pipeline."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


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


@dataclass
class PipelineConfig:
    """Config for the full pipeline."""
    # Preprocessing
    preprocess_window: int = 20
    # Sudden detector
    sudden_window_size: int = 50
    sudden_threshold: float = 2.0  # e.g. z-score or effect size threshold
    # Gradual detector
    gradual_window_size: int = 100
    gradual_delta: float = 0.01
    gradual_lambda: float = 0.99  # Page-Hinkley
    # Recurring
    recurrence_threshold: float = 0.5
    concept_memory_add_if_new: bool = True
    # Batch / adaptation
    update_batch_size: int = 100
    # Model
    model_type: str = "linear"  # "linear" | "nonlinear"
    # Evaluation
    eval_window: int = 200
