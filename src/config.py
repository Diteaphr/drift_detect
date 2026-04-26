"""Shared config and types for the concept drift pipeline."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


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
            ``"rf"``      — Adaptive Random Forest (River ARF, self-adaptive)
            ``"xgb"``     — XGBoost (buffer-based incremental)
            ``"gru"``     — GRU (PyTorch sliding-window online)
            ``"ht"``      — Plain Hoeffding Tree (River, no internal drift
                            handling — for ECPF-style external frameworks)

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
    selected_detectors: Optional[list] = None  # To specify which atom detectors to include
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
    meta_detector_type: str = "dynamic_weighted"  # "two_stage", "dynamic_weighted", "statistical_fusion"
    # Model
    model_type: str = "ht"
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    # Evaluation
    eval_window: int = 200
    # --- Enhanced Concept Profiling Framework (ECPF), Anderson et al. (TKDE) ---
    use_ecpf: bool = True
    # Signal mode:
    # - "oracle_60": warning at true drift T, confirm drift after 60 samples.
    # - "meta_retro_60": when detector fires at T, use previous 60 as warning buffer.
    # - "detector": warning/drift from standalone ECPF detector (src/ecpf_detector.py).
    ecpf_signal_mode: str = "oracle_60"
    ecpf_oracle_true_drift_times: Optional[List[int]] = None
    ecpf_warning_length: int = 60
    ecpf_similarity_margin: float = 0.95  # m
    ecpf_fade_points: int = 15  # f
    ecpf_fade_enabled: bool = True
    ecpf_model_check_freq: int = 1
    # Standalone detector used when ecpf_signal_mode == "detector".
    ecpf_detector_type: str = "ddm"
    ecpf_detector_min_instances: int = 30
    ecpf_ddm_warning_level: float = 2.0
    ecpf_ddm_drift_level: float = 3.0
    # Hard cap on ECPF expert snapshots in the model pool.
    ecpf_max_pool_size: int = 10
    # Detector params requested from paper's setup (stored for parity with experiments;
    # oracle_60 does not consume them directly yet).
    detector_delta: float = 0.05
    detector_epsilon: float = 0.01
    detector_alpha: float = 0.8
    detector_delta_w: float = 0.1
