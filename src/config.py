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
            ``"linear"`` -- SGDClassifier
            ``"nonlinear"`` -- GaussianNB

        Advanced (BaseModel-based, via model_adapter):
            ``"elastic"`` -- ElasticNet (River online logistic regression)
            ``"rf"``      -- Adaptive Random Forest (River ARF, self-adaptive)
            ``"xgb"``     -- XGBoost (buffer-based incremental)
            ``"gru"``     -- GRU (PyTorch sliding-window online)
            ``"ht"``      -- Plain Hoeffding Tree (River, no internal drift
                              handling; for ECPF-style external frameworks)

    model_kwargs : dict
        Extra keyword arguments forwarded to the model constructor.
        Only used for advanced model types.
    """

    # Preprocessing
    preprocess_window: int = 20

    # Meta/Unified detector settings
    meta_ks_window_size: int = 100
    atom_min_samples: int = 30
    atom_kwargs: Dict[str, Any] = field(default_factory=dict)
    selected_detectors: Optional[List[str]] = None

    # Recurring (RCD-style statistical test; Goncalves & Barros 2013)
    recurring_stat_alpha: float = 0.01  # recurring if p-value > alpha (paper best: s = 0.01)
    recurring_k_neighbors: int = 5
    recurring_max_buffer_size: int = 400
    recurring_n_permutations: int = 199
    recurring_use_post_alert_fifo: bool = True
    recurring_fifo_min_samples: int = 100
    recurring_window_before: int = 50
    recurring_window_after: int = 10
    recurring_random_seed: int = 42
    recurrence_threshold: Optional[float] = None
    concept_memory_add_if_new: bool = True

    # Batch / adaptation
    update_batch_size: int = 100

    # Meta detector
    # Supported values: "two_stage", "dynamic_weighted",
    # "dynamic_weighted_ecpf", "statistical_fusion".
    meta_detector_type: str = "dynamic_weighted"
    meta_dwm_beta: float = 0.8
    meta_dwm_reward: float = 1.05
    meta_dwm_threshold: float = 0.5
    meta_proxy_policy: str = "any"  # "any" or "all"

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
    # - "uq_warning": UQ-only warning + error-based ADWIN confirmation.
    # - "dual_adwin": warning/drift from ADWIN detectors on configured signals.
    # - "dual_seed": warning/drift from SEED-style detectors on configured signals.
    # - "dual_seqdrift2": warning/drift from SeqDrift2-style detectors on configured signals.
    # - "hybrid_adwin_family": warning/drift from ecpf_adwin_family_combo.
    # - "<warning>_warning_<drift>_drift": explicit ADWIN/SEED/SeqDrift2 combo.
    # - "meta_ecpf_dwm": persistent UQ/KSWIN warning + ADWIN/HDDM-W confirmation.
    # - "meta_ecpf_hier_parallel": hierarchical hypothesis ECPF detector
    #   (low-cost detection layer + zero-one validation layer).
    # - "meta_ecpf_hcdt": HCDT two-layer ECPF detector
    #   (HDDM detection layer + RDDM validation layer).
    # - "meta_ecpf_gddm": GDDM-style group rank detector over tree error/UQ streams.
    ecpf_signal_mode: str = "oracle_60"
    ecpf_oracle_true_drift_times: Optional[List[int]] = None
    ecpf_warning_length: int = 60
    ecpf_similarity_margin: float = 0.95  # m
    ecpf_fade_points: int = 15  # f
    ecpf_fade_enabled: bool = True
    ecpf_model_check_freq: int = 1
    ecpf_max_pool_size: int = 10

    # Standalone detector used when ecpf_signal_mode == "detector".
    ecpf_detector_type: str = "ddm"
    ecpf_detector_min_instances: int = 30
    ecpf_ddm_warning_level: float = 2.0
    ecpf_ddm_drift_level: float = 3.0

    # Detector params requested from paper setup; oracle_60 does not consume
    # them directly, but detector-based modes do.
    detector_delta: float = 0.05
    detector_epsilon: float = 0.01
    detector_alpha: float = 0.8
    detector_delta_w: float = 0.1

    # ADWIN/SEED/SeqDrift2 family routing
    ecpf_adwin_family_combo: str = "seed_warning_adwin_drift"
    ecpf_warning_detector: Optional[str] = None
    ecpf_drift_detector: Optional[str] = None
    ecpf_warning_signal: str = "error"
    ecpf_drift_signal: str = "error"
    ecpf_uq_num_classes: Optional[int] = None
    ecpf_warning_value_range: float = 1.0
    ecpf_drift_value_range: float = 1.0

    # --- UQ Warning Layer (Hoeffding Forest uncertainty-based early warning) ---
    # UQ scalar extraction mode: "mi_like" | "vote_disagreement" | "predictive_entropy"
    ecpf_uq_mode: str = "mi_like"
    ecpf_uq_delta: float = 0.01
    ecpf_uq_grace_period: int = 50
    ecpf_uq_smoothing_alpha: float = 0.1
    ecpf_uq_warning_timeout: int = 1000

    # --- ECPF-DWM two-stage detector ---
    ecpf_dwm_warning_persistence: int = 2
    ecpf_dwm_warning_persistence_window: int = 120
    ecpf_dwm_kswin_alpha: float = 0.005
    ecpf_dwm_kswin_window_size: int = 100
    ecpf_dwm_kswin_stat_size: int = 30
    ecpf_dwm_confirm_threshold: float = 0.5

    # --- ECPF hierarchical hypothesis detector ---
    ecpf_hier_fast_candidate_threshold: float = 0.5
    ecpf_hier_gradual_candidate_threshold: float = 0.5
    ecpf_hier_proxy_policy: str = "any"  # "any" or "all"
    ecpf_hier_validation_hist_size: int = 250
    ecpf_hier_validation_new_size: int = 60
    ecpf_hier_validation_min_new_size: int = 30
    ecpf_hier_validation_gap_threshold: float = 0.02

    # --- ECPF-HCDT two-layer detector ---
    # Detection layer opens the ECPF warning buffer. Validation layer confirms
    # drift or cancels false positives. Core detector implementations live in
    # detectors/core/unified.py; this config only selects how meta_ecpf/hcdt.py
    # wires them together.
    ecpf_hcdt_detection_layer: str = "hddm_a"
    ecpf_hcdt_detection_min_samples: int = 30
    ecpf_hcdt_detection_delta: float = 0.005
    ecpf_hcdt_detection_lambda: float = 0.98
    ecpf_hcdt_detection_threshold: float = 0.07
    ecpf_hcdt_validation_layer: str = "rddm"
    ecpf_hcdt_validation_min_samples: int = 30
    ecpf_hcdt_rddm_warning_level: float = 1.75
    ecpf_hcdt_rddm_drift_level: float = 2.5
    ecpf_hcdt_rddm_max_warning_length: int = 400
    ecpf_hcdt_min_confirmation_age: int = 45
    ecpf_hcdt_warning_timeout: int = 1000
    ecpf_hcdt_cooldown: int = 1500

    # --- ECPF-GDDM group detector ---
    ecpf_gddm_reference_window: int = 160
    ecpf_gddm_test_window: int = 60
    ecpf_gddm_min_updates: int = 2000
    ecpf_gddm_error_rate_window: int = 30
    ecpf_gddm_warning_alpha: float = 0.10
    ecpf_gddm_drift_alpha: float = 0.01
    ecpf_gddm_n_permutations: int = 19
    ecpf_gddm_threshold_update_interval: int = 250
    ecpf_gddm_warning_persistence: int = 2
    ecpf_gddm_gradual_persistence: int = 3
    ecpf_gddm_min_confirmation_age: int = 60
    ecpf_gddm_sudden_jump_ratio: float = 1.35
    ecpf_gddm_include_uq: bool = True
    ecpf_gddm_cooldown: int = 2000
