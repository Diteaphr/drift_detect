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
            ``"hf"``      -- Hoeffding Forest (per-tree predict_proba_matrix
                              for UQ-based warning)

        Multi-class capable: only ``"rf"``, ``"ht"``, ``"hf"``. ``"elastic"`` is
        binary-only and now raises rather than silently capping its accuracy;
        ``"linear"``/``"nonlinear"`` learn their class set from data; ``"xgb"``
        and ``"gru"`` switch to a multi-class head when K > 2.

        Regression (continuous target):
            ``"sgdr"``    -- sklearn SGDRegressor
            ``"htr"``     -- River HoeffdingTreeRegressor
            ``"arfr"``    -- River ARFRegressor (self-adaptive)
            ``"hfr"``     -- Hoeffding Forest Regressor; exposes
                              predict_per_model() for ensemble-variance UQ

        An unrecognised value still falls through to GaussianNB, which is the
        historical behaviour -- a typo'd regressor name therefore trains a
        classifier on a continuous target and dies in ``fit``.

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

    # --- Task type (classification vs regression) ---
    # ``None`` auto-detects from the target array via ``src/task.py``: an integral
    # target with at most ``task_max_classes`` distinct values is classification,
    # anything else is regression. Declare it explicitly only to override that
    # inference (e.g. to model an integer-valued rating as a continuous quantity);
    # a declaration that contradicts the data raises rather than guessing.
    task_type: Optional[str] = None  # "binary" | "multiclass" | "regression"
    n_classes: Optional[int] = None
    task_max_classes: int = 50
    # Warm-up before the regression error normalizer trusts its own mean/sigma.
    error_normalizer_warmup: int = 30

    # Model
    model_type: str = "ht"
    model_kwargs: Dict[str, Any] = field(default_factory=dict)

    # Evaluation
    eval_window: int = 200

    # --- Stage tracing (observer-only; off by default) ---
    # When enabled, the pipeline records intermediate per-stage outputs via
    # src/tracing.py for interpretability analysis. Has no effect on decisions.
    trace_enabled: bool = False
    trace_window: int = 300  # ± samples around each event kept in the stage-1 signal trace

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
    # Regression uses a different similarity statistic, so the paper's m does not
    # transfer: classification measures an agreement RATE over predicted labels,
    # regression measures Pearson correlation of residual vectors mapped to
    # (r + 1) / 2. Reusing 0.95 there would mean r >= 0.90, and two experts scored
    # against the same targets are routinely correlated above that -- everything
    # would merge. Calibrated to 0.80 as a non-degenerate starting point; this is
    # a hyperparameter to tune, not a constant carried over from the paper.
    ecpf_similarity_margin_regression: float = 0.80
    # Conceptual-equivalence definition, for the ablation of this project's
    # modification. "auto" = predicted-label agreement (ours; provably equal to
    # the paper at K=2). "error_bitset" = the published ECPF/CPF definition
    # (wrong-bit XOR; (wrong, wrong) counts as agreement even across different
    # wrong classes). Invalid for regression.
    ecpf_similarity_mode: str = "auto"
    ecpf_fade_points: int = 15  # f
    ecpf_fade_enabled: bool = True
    ecpf_model_check_freq: int = 1
    ecpf_max_pool_size: int = 10

    # --- Post-confirmation echo suppression (ADWIN-family / detector modes) ---
    # After a confirmed drift the pipeline swaps the leader model, but the
    # warning/drift ADWINs keep their windows: they still hold the OLD model's
    # error stream, so the NEW model's different error level reads as a second
    # change a few hundred to ~1500 steps later. Measured on multi-class streams:
    # every true drift was followed by 1-2 such echoes (median gap 1120 steps),
    # which the interval-based CD score counts as false positives.
    #   ecpf_detector_reset_on_drift  reset both detectors after confirmation,
    #                                 so they re-baseline on the new model.
    #   ecpf_detector_cooldown        ignore drift confirmations for N steps
    #                                 after one fires (0 = off).
    # Both default OFF so every existing (binary) run is byte-identical.
    ecpf_detector_reset_on_drift: bool = False
    ecpf_detector_cooldown: int = 0
    # Minimum warning age (ADWIN-family modes). On one signal the warning and
    # drift ADWINs often fire on the SAME step for a sharp change, so the reuse
    # decision is made on a 1-instance warning buffer (measured: 42-57% of hits
    # on both multi-class and regression streams). With k > 0 a confirmation
    # whose buffer holds fewer than k instances is held until it does; the
    # scored timestamp (warning start) does not move. 0 = off, byte-identical.
    ecpf_min_warning_age: int = 0
    # Prescription 3 (regression). The online residual normalizer is a global
    # Welford mean/sd that never resets; when the residual scale changes across
    # concepts it keeps catching up for tens of thousands of steps, turning a
    # flat raw residual into a slow ramp the two-sided ADWIN cuts (fixed-scale
    # counterfactual on Joe sudden: forest FP 21 -> 10). With this on, the
    # normalizer re-baselines together with the detectors at every ECPF
    # confirmation (the duel credit is then neutral, 0.5, for the normalizer's
    # 30-instance warm-up). Classification never uses the normalizer, so binary
    # runs are byte-identical either way; default off.
    ecpf_normalizer_reset_on_drift: bool = False
    # Frozen-reference detector input (regression). The two-sided ADWIN reads
    # the adaptive leader's own improvement (learning curve, duel swaps, a bad
    # reuse being re-learnt) as drift. With this on, the detectors are fed the
    # residual of a FROZEN copy of the model installed at the last confirmation
    # (own normalizer, reset at every freeze); the leader keeps learning as
    # usual and still supplies predictions, accuracy, duel credit and buffer
    # scoring. warmup=0: freeze the just-installed clone and keep it until the
    # next confirmation (no warm-up, no switch). warmup=k>0 (secondary arm):
    # re-freeze from the adapted leader k steps after each confirmation, with
    # a switch reset (detectors, open warning, buffer, reference normalizer);
    # the previous reference then shadow-runs 500 steps for diagnostics only.
    # Classification (E2, docs/ECPF_E1E2_預註冊.md): the detectors read the frozen
    # copy's 0/1 loss. Default-off runs are byte-identical.
    ecpf_reference_signal: bool = False
    ecpf_reference_warmup: int = 0

    # E1 (docs/ECPF_E1E2_預註冊.md): MOA ADWINChangeDetector semantics on both ADWIN
    # arms -- a cut counts only if the error estimate rose; a suppressed cut keeps
    # its post-cut window. river's ADWIN is two-sided, MOA's wrapper has been
    # increase-only since 2017. Default OFF; binary runs unchanged.
    ecpf_adwin_one_sided: bool = False

    # --- Direction gate on drift confirmations (ADWIN-family modes) ---
    # ADWIN is two-sided: it fires on error DROPS as readily as rises. In ECPF
    # the error stream between drifts falls by design (duel leader swaps, the
    # post-adaptation learning curve), so a two-sided confirmation reports the
    # system's own improvement as drift. Per-detection classification on four
    # multi-class streams: 11 echo + 14 orphan FPs vs 12 true hits, separated
    # cleanly by direction (surviving hits at diff >= +0.128, FPs <= +0.078;
    # `margin` 0.05 sits in that gap). The baseline is the mean error over the
    # `older` samples BEFORE THE CURRENT WARNING OPENED (snapshotted then), and
    # `recent` is the trailing window at confirmation. The anchor is essential:
    # a sliding baseline climbs along with a slow gradual transition and the
    # v1 variant suppressed every detection on wide-transition streams. On
    # suppression the drift detector is reset so the ongoing slow decline
    # re-baselines instead of refiring.
    # Known blind spot: a drift buried inside a falling-error phase (e.g. right
    # after warm-start) is suppressed too. Default OFF; binary runs unchanged.
    ecpf_drift_direction_gate: bool = False
    ecpf_gate_recent: int = 300
    ecpf_gate_older: int = 1500
    ecpf_gate_margin: float = 0.05

    # Close a warning that has stayed open longer than this many steps without
    # a confirmation (0 = off). Measured failure it prevents: a warning opened
    # at t=4743 stayed open 11,168 steps; the confirmation triggered by a REAL
    # drift at t=15718 was stamped with the stale warning time (scored as a
    # false positive) and the warning buffer spanning two concepts was used for
    # model reuse selection. The uq_warning mode has an equivalent timeout;
    # the ADWIN-family modes lacked one.
    ecpf_detector_warning_timeout: int = 0

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
    # UQ scalar extraction mode:
    # "mi_like" | "vote_disagreement" | "predictive_entropy" | "variance_eu"
    ecpf_uq_mode: str = "mi_like"
    # Divide the UQ scalar by its theoretical maximum (log2(K) for the entropy
    # modes, 1 - 1/K for vote/variance) so one threshold transfers across class
    # counts. Off by default: a no-op for the entropy modes at K=2, but it would
    # rescale ``vote_disagreement`` and ``variance_eu`` and therefore change
    # existing binary results. Turn it on for multi-class comparability.
    #
    # Applies to the paths that feed a UQ scalar straight into a detector --
    # ``uq_warning`` (src/uq_warning_detector.py) and ``meta_ecpf_gddm``. The
    # ADWIN-family modes do NOT need it: detectors/meta_ecpf/signal_routing.py
    # already rescales by the same denominators before the value leaves it, so
    # enabling this there would divide twice.
    ecpf_uq_normalize_scale: bool = False
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
