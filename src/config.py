"""Shared config and types for the concept drift pipeline."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class DriftType(str, Enum):
    NONE = "none"
    SUDDEN = "sudden"
    GRADUAL = "gradual"
    INCREMENTAL = "incremental"
    RECURRING = "recurring"


@dataclass
class DriftDetection:
    """Single drift detection event."""
    timestamp: int
    drift_type: DriftType
    detector_source: str  # e.g., "unified" (or naming the detector that fired)
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
    # Meta/Unified detector settings
    meta_ks_window_size: int = 100
    atom_min_samples: int = 30
    atom_kwargs: Dict[str, Any] = field(default_factory=dict)  # For future extensibility of atom detectors
    # Recurring (RCD-style statistical test; Gonçalves & Barros 2013)
    recurring_stat_alpha: float = 0.01  # recurring if p-value > alpha (paper best: s = 0.01)
    recurring_k_neighbors: int = 5
    recurring_max_buffer_size: int = 400
    recurring_n_permutations: int = 199
    # Paper-like: FIFO of instances after drift alert (cap = recurring_max_buffer_size).
    recurring_use_post_alert_fifo: bool = True
    recurring_fifo_min_samples: int = 100  # run test once this many post-alert points collected (or cap hit)
    # Legacy slice around alert (used if recurring_use_post_alert_fifo is False, or for X_stream eval fallback)
    recurring_window_before: int = 50
    recurring_window_after: int = 10
    recurring_random_seed: int = 42
    # If set, overrides recurring_stat_alpha for each detect_recurring_drift call only.
    recurrence_threshold: Optional[float] = None
    concept_memory_add_if_new: bool = True
    # Batch / adaptation
    update_batch_size: int = 100
    # Meta Detector
    meta_detector_type: str = "two_stage"  # "two_stage", "dynamic_weighted", "statistical_fusion"
    # Model
    model_type: str = "linear"
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    # Evaluation
    eval_window: int = 200
