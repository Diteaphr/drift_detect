"""
Main concept drift pipeline: data stream → preprocessing → meta-drift detector
→ optional RCD-style recurring test **or** ECPF model pool (mutually exclusive)
→ drift type classifier → model pool & incremental adaptation.

Supports two model backends:
  - Original sklearn-based PredictionModel ("linear" / "nonlinear")
  - Advanced BaseModel-based models via BaseModelAdapter ("elastic" / "rf" / "xgb" / "gru")

When ``PipelineConfig.use_ecpf`` is True, the Enhanced Concept Profiling Framework
(Anderson et al., TKDE) manages classifier reuse with paper defaults
(``m=0.95``, ``f=15``, synthetic oracle buffer length 60).
"""

import logging
from pathlib import Path
from collections import deque

import numpy as np
import pandas as pd
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from .config import DriftDetection, DriftType, PipelineConfig
from .preprocessing import StreamBuffer, zero_one_loss
from .task import (
    REAL_VALUED_DETECTORS,
    ErrorNormalizer,
    TaskSpec,
    TaskType,
    incompatible_detectors,
    resolve_task,
)
from detectors import (
    ConceptMemory,
    detect_recurring_drift,
)
from .ecpf import ECPFMetaLearner, _deep_clone, load_drift_times_file, load_drift_intervals_file
from .ecpf_detector import ECPFWarningDriftDetector, ECPFZoneDetector
from .uq_warning_detector import UQWarningDetector
from detectors.meta_ecpf.adwin_family import ECPFAdwinFamilyDetector
from detectors.meta_ecpf.signal_routing import extract_signal, normalize_signal_name
from .drift_type_classifier_dtc_rf import classify_drift_type
from .model_pool import ModelPool
from .prediction_model import PredictionModel, needs_class_declaration
from .model_adapter import (
    DEFAULT_MODEL_BY_TASK,
    BaseModelAdapter,
    is_advanced_model_type,
    is_regression_model_type,
)
from .models import ElasticNetModel
from .tracing import StageTracer, NullTracer

try:
    import river  # noqa: F401

    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False

from detectors.meta import TwoStageVotingDetector, DynamicWeightedVotingDetector, StatisticalFusionDetector
from detectors.meta_ecpf.dynamic_weighted import DynamicWeightedVotingECPFDetector
from detectors.meta_ecpf.gddm import ECPFGDDMDetector
from detectors.meta_ecpf.hcdt import HCDTECPFDetector
from detectors.meta_ecpf.hierarchical_parallel import HierarchicalParallelECPFDetector
from detectors.meta.indicators import KSDistributionIndicator, ErrorRateTrendIndicator, UncertaintyProxyIndicator

logger = logging.getLogger(__name__)


ECPF_ADWIN_FAMILY_SIGNAL_MODES = {
    "detector",
    "dual_adwin",
    "dual_seed",
    "dual_seqdrift2",
    "hybrid_adwin_family",
    *ECPFAdwinFamilyDetector.COMBOS.keys(),
}


class ConceptDriftPipeline:
    """
    Full pipeline: consume (X, y) stream, maintain prediction model, run detectors,
    output detections and optionally adapt the model.

    When ``config.model_type`` is one of ``"elastic"``, ``"rf"``, ``"xgb"``,
    ``"gru"``, the pipeline uses ``BaseModelAdapter`` which provides true
    single-sample streaming (``learn_one`` / ``predict_one``) and
    ModelManager-style post-drift retraining.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.buffer = StreamBuffer(max_len=3000)

        # 準備多重代理訊號 (Multi-Indicators) 給支援的 Meta-detectors
        # 這裡組合了資料分布、短期錯誤率趨勢、以及模型不確定性 的多個代理指標
        my_indicators = [
            KSDistributionIndicator(window_size=self.config.meta_ks_window_size),
            ErrorRateTrendIndicator(short_window=50, long_window=250, threshold=0.15),
            UncertaintyProxyIndicator(window_size=100, variance_threshold=0.25)
        ]

        if self.config.ecpf_signal_mode == "meta_ecpf_dwm":
            self.meta_detector = DynamicWeightedVotingECPFDetector(
                self.config,
                uq_mode=self.config.ecpf_uq_mode or "mi_like",
                selected_detectors=self.config.selected_detectors
            )
        elif self.config.ecpf_signal_mode == "meta_ecpf_hcdt":
            self.meta_detector = HCDTECPFDetector(self.config)
        elif self.config.ecpf_signal_mode == "meta_ecpf_gddm":
            self.meta_detector = ECPFGDDMDetector(
                self.config,
                uq_mode=self.config.ecpf_uq_mode or "mi_like",
            )
        elif self.config.ecpf_signal_mode == "meta_ecpf_hier_parallel":
            self.meta_detector = HierarchicalParallelECPFDetector(
                self.config,
                uq_mode=self.config.ecpf_uq_mode or "mi_like",
                selected_detectors=self.config.selected_detectors,
            )
        elif self.config.meta_detector_type == "two_stage":
            self.meta_detector = TwoStageVotingDetector(
                self.config, 
                custom_indicators=my_indicators,
                selected_detectors=self.config.selected_detectors
            )
        elif self.config.meta_detector_type == "dynamic_weighted":
            self.meta_detector = DynamicWeightedVotingDetector(
                self.config, 
                custom_indicators=my_indicators,
                selected_detectors=self.config.selected_detectors
            )
        elif self.config.meta_detector_type == "dynamic_weighted_ecpf":
            self.meta_detector = DynamicWeightedVotingECPFDetector(
                self.config, 
                custom_indicators=my_indicators,
                selected_detectors=self.config.selected_detectors
            )
        elif self.config.meta_detector_type == "statistical_fusion":
            self.meta_detector = StatisticalFusionDetector(
                self.config,
                custom_indicators=my_indicators,
                selected_detectors=self.config.selected_detectors
            )
        else:
            raise ValueError(f"Unknown meta_detector_type: {self.config.meta_detector_type}")

        self.concept_memory = ConceptMemory(
            significance=self.config.recurring_stat_alpha,
            k_neighbors=self.config.recurring_k_neighbors,
            max_buffer_size=self.config.recurring_max_buffer_size,
            n_permutations=self.config.recurring_n_permutations,
            window_before=self.config.recurring_window_before,
            window_after=self.config.recurring_window_after,
            random_seed=self.config.recurring_random_seed,
        )
        self.model_pool = ModelPool(in_memory=True)
        self.detections: List[DriftDetection] = []
        self._step = 0
        self._lock_out = 0
        self._lock_out_duration = 100
        self._batch_X: List[np.ndarray] = []
        self._batch_y: List[float] = []
        self._warm = False
        self._concept_counter = 0

        # --- Task type ---
        # Defaults to binary so a pipeline driven instance-by-instance (without
        # run_stream) behaves exactly as before: TaskSpec.loss for a classification
        # task IS zero_one_loss. run_stream calls _bind_task() to replace this with
        # the type actually inferred from the target array.
        self.task: TaskSpec = TaskSpec(task_type=TaskType.BINARY, n_classes=2)
        self._task_bound = False
        self._task_provisional = False
        self._resolved_model_type = self.config.model_type
        # Separate from the task's error normalizer: the ensemble-variance UQ
        # signal lives on a different scale than the residual.
        self._uq_normalizer = ErrorNormalizer(warmup=self.config.error_normalizer_warmup)

        # --- Model backend selection ---
        self._use_advanced = is_advanced_model_type(self._resolved_model_type)
        self.prediction_model: Union[PredictionModel, BaseModelAdapter] = (
            self._build_prediction_model()
        )

        # ECPF (Enhanced Concept Profiling Framework)
        self._ecpf: Optional[ECPFMetaLearner] = self._build_ecpf()
        self._ecpf_warning_active = False
        self._ecpf_warning_start_idx: Optional[int] = None
        self._ecpf_buffer: List[Tuple[np.ndarray, float]] = []
        self._ecpf_oracle_started: set = set()
        self._ecpf_ring: deque = deque(maxlen=5000)
        self._ecpf_cooldown_left = 0   # steps left in the post-confirmation cooldown
        self._ecpf_pending_confirm = False  # drift arm fired, buffer still < ecpf_min_warning_age
        # Frozen-reference detector input (see config.ecpf_reference_signal).
        self._ref_model = None              # frozen copy the detectors are fed with
        self._ref_norm = ErrorNormalizer()  # the reference's own normalizer
        self._ref_frozen_at = None          # index at which the current reference was frozen
        self._ref_switch_due = None         # secondary arm: index at which to re-freeze
        self._ref_shadow = None             # previous reference, shadow-run after a switch
        self._ref_shadow_until = None
        # Rolling drift-signal history for the direction gate; only fed when the
        # gate is enabled, so disabled runs are untouched.
        self._gate_hist: deque = deque(
            maxlen=int(self.config.ecpf_gate_recent) + int(self.config.ecpf_gate_older)
        )
        # Pre-warning error baseline for the direction gate (v2). Snapshotted at
        # the moment a warning OPENS: that history is pre-deterioration by
        # construction. A sliding baseline (gate v1) climbed along with slow
        # gradual transitions and, combined with the re-baseline on suppression,
        # suppressed EVERY detection on wide-transition streams (validated:
        # rbf gradual/low went from 7 events to 0).
        self._gate_baseline: Optional[float] = None
        self._ecpf_detector: Optional[ECPFAdwinFamilyDetector] = None
        if (self.config.use_ecpf and self.config.ecpf_signal_mode in ECPF_ADWIN_FAMILY_SIGNAL_MODES
                and self.config.ecpf_zone_detector):
            # E9: the official-ECPF single detector replaces the dual ADWIN.
            self._ecpf_detector = ECPFZoneDetector(self.config.ecpf_zone_detector)
        elif self.config.use_ecpf and self.config.ecpf_signal_mode in ECPF_ADWIN_FAMILY_SIGNAL_MODES:
            warning_detector, drift_detector = self._resolve_ecpf_adwin_family_detectors()
            if warning_detector == "adwin" and drift_detector == "adwin":
                self._ecpf_detector = ECPFWarningDriftDetector(
                    min_num_instances=self.config.ecpf_detector_min_instances,
                    delta=self.config.detector_delta,
                    delta_w=self.config.detector_delta_w,
                    one_sided=self.config.ecpf_adwin_one_sided,
                )
            else:
                self._ecpf_detector = ECPFAdwinFamilyDetector(
                    warning_detector_type=warning_detector,
                    drift_detector_type=drift_detector,
                    min_num_instances=self.config.ecpf_detector_min_instances,
                    delta=self.config.detector_delta,
                    delta_w=self.config.detector_delta_w,
                    random_seed=self.config.recurring_random_seed,
                    warning_value_range=self.config.ecpf_warning_value_range,
                    drift_value_range=self.config.ecpf_drift_value_range,
                    one_sided=self.config.ecpf_adwin_one_sided,
                )
        # E10b: E1's detector on the leader's own error, next to the reference detectors.
        self._ecpf_guard: Optional[ECPFWarningDriftDetector] = None
        if self._ecpf_detector is not None and self.config.ecpf_leader_guard:
            self._ecpf_guard = ECPFWarningDriftDetector(
                min_num_instances=self.config.ecpf_detector_min_instances,
                delta=self.config.detector_delta,
                delta_w=self.config.detector_delta_w,
                one_sided=True,
            )

        # UQ Warning Layer: UQ-only warning + error-based drift confirmation
        self._uq_warning_detector: Optional[UQWarningDetector] = None
        self._uq_drift_detector: Optional[ECPFWarningDriftDetector] = None
        if self.config.use_ecpf and self.config.ecpf_signal_mode == "uq_warning":
            self._uq_warning_detector = UQWarningDetector(
                uq_mode=self.config.ecpf_uq_mode,
                delta=self.config.ecpf_uq_delta,
                grace_period=self.config.ecpf_uq_grace_period,
                smoothing_alpha=self.config.ecpf_uq_smoothing_alpha,
                num_classes=self.config.ecpf_uq_num_classes or self.config.n_classes,
                normalize_scale=self.config.ecpf_uq_normalize_scale,
            )
            # Second layer: error-based ADWIN for drift confirmation only
            self._uq_drift_detector = ECPFWarningDriftDetector(
                min_num_instances=self.config.ecpf_detector_min_instances,
                delta=self.config.detector_delta,
                delta_w=self.config.detector_delta_w,
            )
            self._uq_warning_timeout = self.config.ecpf_uq_warning_timeout

        # Post-alert FIFO for RCD-like recurring test (collect after drift alarm)
        self._collecting_post_alert_fifo: bool = False
        self._post_alert_fifo_x: Optional[deque] = None
        self._post_alert_fifo_err: Optional[deque] = None
        self._pending_drift: Optional[Dict[str, Any]] = None

        # Observer-only stage tracer (no effect on decisions; off by default).
        self.tracer = (
            StageTracer(self.config.trace_window)
            if getattr(self.config, "trace_enabled", False)
            else NullTracer()
        )
        self._trace_index: int = 0

    def _resolve_ecpf_adwin_family_combo(self) -> str:
        mode = self.config.ecpf_signal_mode
        if mode == "detector":
            return "dual_adwin"
        if mode in {"dual_adwin", "dual_seed", "dual_seqdrift2"}:
            return mode
        if mode == "hybrid_adwin_family":
            return self.config.ecpf_adwin_family_combo
        if mode in ECPFAdwinFamilyDetector.COMBOS:
            return mode
        raise ValueError(f"Unknown ECPF ADWIN-family signal mode: {mode}")

    def _resolve_ecpf_adwin_family_detectors(self) -> Tuple[str, str]:
        if self.config.ecpf_warning_detector or self.config.ecpf_drift_detector:
            warning_detector = (self.config.ecpf_warning_detector or "adwin").lower()
            drift_detector = (self.config.ecpf_drift_detector or "adwin").lower()
            for detector_type in (warning_detector, drift_detector):
                if detector_type not in {"adwin", "seed", "seqdrift2"}:
                    raise ValueError(
                        f"Unknown ECPF detector type {detector_type!r}; "
                        "choose from adwin, seed, seqdrift2"
                    )
            return warning_detector, drift_detector
        return ECPFAdwinFamilyDetector.COMBOS[self._resolve_ecpf_adwin_family_combo()]

    # ------------------------------------------------------------------
    # UQ signal plumbing
    # ------------------------------------------------------------------
    def _uq_num_classes(self) -> Optional[int]:
        """Denominator for UQ rescaling: explicit config wins, else the resolved K."""
        if self.config.ecpf_uq_num_classes is not None:
            return self.config.ecpf_uq_num_classes
        return self.task.n_classes

    def _uq_inputs(self, x_: np.ndarray) -> Tuple[Optional[list], Optional[list]]:
        """``(proba_matrix, pred_matrix)`` -- only one is ever populated.

        Classification reduces a per-tree probability matrix; regression reduces
        per-member point predictions. Asking a regression backend for
        ``predict_proba_matrix`` returns ``[]``, which routes to a UQ scalar
        pinned at 0.0 -- indistinguishable from "no drift ever" -- so the two
        paths are kept strictly separate.
        """
        if self.task.is_regression:
            if hasattr(self.prediction_model, "predict_per_model"):
                try:
                    return None, self.prediction_model.predict_per_model(x_)
                except Exception:
                    return None, None
            return None, None
        if hasattr(self.prediction_model, "predict_proba_matrix"):
            try:
                return self.prediction_model.predict_proba_matrix(x_), None
            except Exception:
                return None, None
        return None, None

    def _direction_gate_passes(self) -> bool:
        """True if the pending confirmation looks like a DETERIORATION.

        v2: compares the mean of the last ``ecpf_gate_recent`` drift-signal
        values against the **pre-warning baseline** snapshotted when the current
        warning opened. Anchoring matters: a sliding baseline climbs along with
        a slow gradual transition (both windows ride the same ramp, the diff
        never clears the margin) and the re-baseline on suppression then wipes
        the accumulation ADWIN needs -- v1 suppressed every detection on
        wide-transition streams. The pre-warning anchor is below the ramp for a
        genuine drift and above the slide for an improvement-driven false
        positive. With no baseline (too little pre-warning history) detections
        are never blocked.
        """
        if self._gate_baseline is None:
            return True
        r = int(self.config.ecpf_gate_recent)
        h = self._gate_hist
        if len(h) < max(100, r // 3):
            return True
        vals = list(h)[-r:]
        recent = sum(vals) / len(vals)
        return (recent - self._gate_baseline) > float(self.config.ecpf_gate_margin)

    def _uq_normalizer_pair(self):
        """Hand the live normalizer to the first consumer, a frozen view to the rest."""
        if not self.task.is_regression:
            return None, None
        if normalize_signal_name(self.config.ecpf_warning_signal) == "uq_variance":
            return self._uq_normalizer, self._uq_normalizer.frozen()
        return None, self._uq_normalizer

    # ------------------------------------------------------------------
    # Task binding
    # ------------------------------------------------------------------
    def declarable_classes(self) -> Optional[np.ndarray]:
        """The full label set to declare on every sklearn wrapper, or ``None``.

        ``TaskSpec.classes`` is resolved from the *whole* target array before
        anything is fit, so declaring it is the only way to stop sklearn locking
        ``classes_`` to whichever labels a particular batch happened to contain
        -- a batch that can be a single instance long (an ECPF warning buffer).

        ``None`` (and therefore no behavioural change) whenever the task is not
        yet bound, is regression, or is the pinned ``{0, 1}`` binary path.
        """
        if not self._task_bound or not self.task.is_classification:
            return None
        classes = self.task.classes
        return classes if needs_class_declaration(classes) else None

    def _build_prediction_model(self) -> Union[PredictionModel, BaseModelAdapter]:
        if self._use_advanced:
            return BaseModelAdapter(
                model_type=self._resolved_model_type,
                model_kwargs=self.config.model_kwargs,
            )
        return PredictionModel(
            model_type=self._resolved_model_type,
            classes=self.declarable_classes(),
        )

    def _build_ecpf(self) -> Optional[ECPFMetaLearner]:
        if not self.config.use_ecpf:
            return None
        margin = (
            self.config.ecpf_similarity_margin_regression
            if self.task.is_regression
            else self.config.ecpf_similarity_margin
        )
        return ECPFMetaLearner(
            similarity_margin=margin,
            fade_points=self.config.ecpf_fade_points,
            model_check_freq=self.config.ecpf_model_check_freq,
            fade_enabled=self.config.ecpf_fade_enabled,
            max_pool_size=self.config.ecpf_max_pool_size,
            use_advanced=self._use_advanced,
            model_type=self._resolved_model_type,
            model_kwargs=self.config.model_kwargs,
            # None keeps ECPF in its legacy classification mode, which is what
            # every binary run wants and what tests/test_ecpf.py asserts.
            task=self.task if self._task_bound else None,
            similarity_mode=self.config.ecpf_similarity_mode,
        )

    def _bind_task(self, y: np.ndarray, *, authoritative: bool = True) -> TaskSpec:
        """Infer the task from the target array and reconfigure accordingly.

        Called before anything is fit, so rebuilding the model and the ECPF pool
        here discards nothing. Three things can change: the backend (a classifier
        cannot model a continuous target), the ECPF similarity statistic and its
        margin, and which detectors are legal.

        Two entry points reach this. :meth:`run_stream` holds the whole target
        array and binds *authoritatively*. :meth:`warm_start` holds only the
        warm-up batch, so it binds *provisionally*: enough to pick the right
        backend and loss, but that batch can easily be missing one of the K
        classes, and sklearn commits its ``classes_`` on first fit with no way to
        widen it later. An authoritative bind therefore overrides a provisional
        one; two provisional binds do not stack.

        Binding here rather than only in ``run_stream`` matters: ``warm_start`` +
        ``step`` is a public entry point (the repo's own ``test_integration.py``
        uses it), and without this the whole task layer silently no-ops there --
        a regression stream would be scored with the classification loss.
        """
        if self._task_bound and not (authoritative and self._task_provisional):
            return self.task

        self.task = resolve_task(
            y,
            declared=self.config.task_type,
            n_classes=self.config.n_classes,
        )
        self.task.normalizer.warmup = int(self.config.error_normalizer_warmup)
        self._task_bound = True
        self._task_provisional = not authoritative

        # A binomial detector on a continuous error stream is not merely
        # imprecise, it is invalid: DDM's sqrt(p*(1-p)/n) needs a Bernoulli rate.
        selected = list(self.config.selected_detectors or [])
        bad = incompatible_detectors(self.task.task_type, selected)
        if bad:
            raise ValueError(
                "detectors %s assume a Bernoulli (0/1) error stream and cannot be "
                "used on a %s task. Choose from %s."
                % (sorted(bad), self.task.describe(), sorted(REAL_VALUED_DETECTORS))
            )

        if self.task.is_regression:
            mode = self.config.ecpf_signal_mode
            if mode == "uq_warning":
                raise ValueError(
                    "ecpf_signal_mode='uq_warning' reduces a per-tree probability "
                    "matrix, which a continuous target does not have. Use "
                    "'detector' / an ADWIN-family mode with "
                    "ecpf_warning_signal='uq_variance' and model_type='hfr'."
                )
            if mode in {"meta_ecpf_dwm", "meta_ecpf_gddm", "meta_ecpf_hier_parallel"}:
                logger.warning(
                    "signal_mode=%r derives some of its proxies from a probability "
                    "matrix; on a regression stream those degrade to their "
                    "error-based fallbacks only.", mode,
                )

        wanted = self._resolved_model_type
        if self.task.is_regression and not is_regression_model_type(wanted):
            fallback = DEFAULT_MODEL_BY_TASK["regression"]
            logger.warning(
                "model_type=%r predicts class labels but the target is continuous; "
                "falling back to %r. Set model_type explicitly to silence this.",
                wanted, fallback,
            )
            self._resolved_model_type = fallback
        elif self.task.is_classification and is_regression_model_type(wanted):
            raise ValueError(
                "model_type=%r is a regressor but the target is %s."
                % (wanted, self.task.describe())
            )

        if self.config.ecpf_signal_mode == "uq_warning" and not hasattr(
            self.prediction_model, "predict_proba_matrix"
        ):
            # Pre-existing failure mode: this mode calls predict_proba_matrix
            # unguarded, so a non-forest backend died with a bare AttributeError
            # deep in the stream loop (on binary too). Name the requirement here.
            raise ValueError(
                "ecpf_signal_mode='uq_warning' reduces a per-tree probability "
                "matrix, which model_type=%r does not expose. Use a forest "
                "backend, i.e. model_type='hf'." % self._resolved_model_type
            )

        if self._resolved_model_type == "elastic":
            # The per-sample guard inside ElasticNetModel cannot fire until the
            # third distinct label arrives, which may be thousands of instances
            # in. Fail at config time instead.
            ElasticNetModel.assert_task_supported(self.task)

        self._use_advanced = is_advanced_model_type(self._resolved_model_type)
        self.prediction_model = self._build_prediction_model()
        self._ecpf = self._build_ecpf()
        logger.info(
            "task bound: %s; model_type=%r", self.task.describe(), self._resolved_model_type
        )
        return self.task

    # ------------------------------------------------------------------
    # Warm start
    # ------------------------------------------------------------------
    def warm_start(self, X: np.ndarray, y: np.ndarray) -> None:
        """Initial fit of the prediction model on first batch.

        Binds the task provisionally from this batch when nothing has bound it
        yet, so the ``warm_start`` + ``step`` entry point gets the same backend
        selection, loss and detector validation that ``run_stream`` gets.
        ``run_stream`` binds authoritatively before calling this, so it wins.
        """
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self._bind_task(y, authoritative=False)
        self.prediction_model.fit(X, y)
        self._warm = True
        if self.config.use_ecpf and self._ecpf is not None:
            self._ecpf.bootstrap_first_expert(self.prediction_model)

    # ------------------------------------------------------------------
    # Per-sample step
    # ------------------------------------------------------------------
    def step(
        self,
        x: np.ndarray,
        y_true: float,
        index: Optional[int] = None,
    ) -> Tuple[float, List[DriftDetection], bool]:
        """
        Process one sample. Returns (y_pred, new_detections_this_step, drift_occurred).
        """
        if index is None:
            index = self._step
        self._step += 1
        self._trace_index = index

        if self._lock_out > 0:
            self._lock_out -= 1

        if isinstance(x, np.ndarray):
            x_ = x
        else:
            x_ = np.asarray(x)
            
        if x_.ndim == 0:
            x_ = x_.reshape(1)
        elif x_.ndim == 1:
            x_ = x_.reshape(1, -1)

        x_flat = x_.ravel()

        # ---- Not yet warmed up ----
        if not self._warm:
            if self._use_advanced:
                # River / XGBoost / GRU models can predict_one even with zero
                # training data (they return a safe default).  So we predict
                # FIRST, then learn_one — true test-then-train from sample 1.
                # The lock-out period shields detectors from the initial noise.
                y_pred = float(self.prediction_model.predict_one(x_))
                self.prediction_model.learn_one(x_flat, y_true)
                from .models.base_model import BaseModel
                self.prediction_model.data_buffer.append(
                    (BaseModel._to_dict(x_flat), y_true, index)
                )
                # Cold-start samples are real stream samples, so they must feed the
                # regression normalizer too -- otherwise it enters the warmed-up
                # phase having seen nothing.
                self.buffer.append(
                    y_true, y_pred, index, x=x_flat, err=self.task.loss(y_true, y_pred)
                )
                self._cold_start_count = getattr(self, '_cold_start_count', 0) + 1
                if self._cold_start_count >= self.config.update_batch_size:
                    self._warm = True
                    self._cold_start_count = 0
                    if self.config.use_ecpf and self._ecpf is not None:
                        self._ecpf.bootstrap_first_expert(self.prediction_model)
                return y_pred, [], False
            else:
                self._batch_X.append(x_flat)
                self._batch_y.append(y_true)
                if len(self._batch_y) >= self.config.update_batch_size:
                    X_b = np.array(self._batch_X)
                    y_b = np.array(self._batch_y)
                    self.warm_start(X_b, y_b)
                    self._batch_X.clear()
                    self._batch_y.clear()
                return 0.0, [], False

        # ---- Predict ----
        if self._use_advanced:
            y_pred = float(self.prediction_model.predict_one(x_))
        else:
            y_pred = float(self.prediction_model.predict(x_)[0])

        # Classification: exactly zero_one_loss, as before. Regression: the
        # absolute residual normalized online into [0,1] so the bounded-signal
        # detectors (ADWIN/SEED/SeqDrift2) stay valid. Computed once and handed
        # to the buffer -- the regression loss advances an online normalizer, so
        # a second call here would move its statistics twice per instance.
        err = self.task.loss(y_true, y_pred)
        self.buffer.append(y_true, y_pred, index, x=x_flat, err=err)
        errors = self.buffer.get_errors()

        # Frozen reference: the ADWIN-family detectors read a frozen copy's
        # residual instead of the learner's. Nothing else reads ref_* -- the
        # ADWIN-family branch swaps its input, the tracer logs it, that is all.
        ref_extra = None
        det_pred = y_pred   # classification's "error" signal is recomputed from this
        if self.config.ecpf_reference_signal:
            if self._ref_model is None:
                self._freeze_reference(index)   # end of warm-up: first reference
            switch_info = None
            if self._ref_switch_due is not None and index >= self._ref_switch_due:
                switch_info = self._switch_reference(index)
            elif (self.config.ecpf_reference_max_age > 0 and not self._ecpf_warning_active
                  and index - self._ref_frozen_at >= self.config.ecpf_reference_max_age):
                # E10a: an old reference stops feeling drifts the leader feels -- refresh it.
                switch_info = {**self._switch_reference(index), "ref_refresh": 1}
            det_pred = self._model_predict(self._ref_model, x_)
            ref_raw = self._ref_loss(y_true, det_pred)
            ref_err = self._ref_norm.update(ref_raw) if self.task.is_regression else ref_raw
            ref_extra = {"ref_err": ref_err, "ref_raw": ref_raw,
                         "ref_age": int(index) - int(self._ref_frozen_at)}
            if self._ref_shadow is not None:
                if index <= self._ref_shadow_until:
                    ref_extra["shadow_raw"] = self._ref_loss(y_true, self._model_predict(self._ref_shadow, x_))
                else:
                    self._ref_shadow = None
            if switch_info:
                ref_extra.update(switch_info)

        new_detections: List[DriftDetection] = []
        ecf_warn = bool(self.config.use_ecpf and self._ecpf_warning_active)

        # ---- ECPF: ring + oracle warning window (paper: warning at true drift, drift after L steps) ----
        if self.config.use_ecpf and self._ecpf is not None:
            self._ecpf_ring.append(
                (
                    np.asarray(x_.ravel(), dtype=np.float64).copy(),
                    float(y_true),
                    int(index),
                )
            )
            if self.config.ecpf_signal_mode == "oracle_60":
                oset = frozenset(self.config.ecpf_oracle_true_drift_times or [])
                if (
                    not self._ecpf_warning_active
                    and index in oset
                    and index not in self._ecpf_oracle_started
                ):
                    self._ecpf_warning_active = True
                    self._ecpf_warning_start_idx = index
                    self._ecpf_buffer = []
                    self._ecpf_oracle_started.add(index)
                    logger.info("ECPF oracle: warning started at t=%d", index)
                if self._ecpf_warning_active:
                    self._ecpf_buffer.append(
                        (np.asarray(x_.ravel(), dtype=np.float64).copy(), float(y_true))
                    )
                    L = self.config.ecpf_warning_length
                    if len(self._ecpf_buffer) >= L:
                        self._handle_ecpf_drift(
                            self._ecpf_buffer[:L],
                            int(self._ecpf_warning_start_idx if self._ecpf_warning_start_idx is not None else index),
                            "ecpf_oracle_60",
                            new_detections,
                            {"ecpf_protocol": f"oracle_warning_then_drift_after_{L}_instances"},
                        )
                        self._ecpf_warning_active = False
                        self._ecpf_warning_start_idx = None
                        self.meta_detector.reset()
                        self._batch_X.clear()
                        self._batch_y.clear()
                        self.buffer = StreamBuffer(
                            max_len=self.buffer.max_len if hasattr(self.buffer, "max_len") else 3000
                        )
                        return y_pred, new_detections, True
                    return y_pred, [], False
            elif self.config.ecpf_signal_mode in ECPF_ADWIN_FAMILY_SIGNAL_MODES and self._ecpf_detector is not None:
                proba_matrix, pred_matrix = self._uq_inputs(x_)
                # The "error" signal the detectors consume: the frozen reference's
                # residual when enabled, otherwise the learner's own (unchanged).
                det_err = ref_extra["ref_err"] if ref_extra is not None else err
                # The unbounded regression UQ variance must be normalized against
                # one scale shared by both signals, and the running statistics must
                # advance exactly once per instance -- hence live-then-frozen.
                warn_norm, drift_norm = self._uq_normalizer_pair()
                warning_value = extract_signal(
                    self.config.ecpf_warning_signal,
                    y_true=y_true,
                    y_pred=det_pred,
                    err=det_err,
                    proba_matrix=proba_matrix,
                    num_classes=self._uq_num_classes(),
                    is_regression=self.task.is_regression,
                    pred_matrix=pred_matrix,
                    uq_normalizer=warn_norm,
                )
                drift_value = extract_signal(
                    self.config.ecpf_drift_signal,
                    y_true=y_true,
                    y_pred=det_pred,
                    err=det_err,
                    proba_matrix=proba_matrix,
                    num_classes=self._uq_num_classes(),
                    is_regression=self.task.is_regression,
                    pred_matrix=pred_matrix,
                    uq_normalizer=drift_norm,
                )
                is_warning, is_drift = self._ecpf_detector.update_values(
                    warning_value,
                    drift_value,
                )
                if self._ecpf_guard is not None:
                    # E10b: the leader's own error (never the reference's), one-sided;
                    # either detector pair may open the warning or confirm.
                    guard_value = extract_signal(
                        "error", y_true=y_true, y_pred=y_pred, err=err, proba_matrix=None,
                        is_regression=self.task.is_regression,
                    )
                    guard_w, guard_d = self._ecpf_guard.update_values(guard_value, guard_value)
                    is_warning, is_drift = is_warning or guard_w, is_drift or guard_d
                    if ref_extra is not None:
                        ref_extra["guard_drift"] = int(guard_d)
                # Echo suppression: a confirmation inside the cooldown window is
                # the new leader's settling-in error being read as a second
                # change. The detector still updates (its window keeps filling);
                # only the confirmation is ignored.
                if is_drift and self._ecpf_cooldown_left > 0:
                    is_drift = False
                if self._ecpf_cooldown_left > 0:
                    self._ecpf_cooldown_left -= 1
                # Direction gate: ADWIN is two-sided, but in ECPF the error
                # stream between drifts falls by design (leader swaps, the
                # learning curve), so improvement-direction confirmations are
                # the system reporting its own progress as drift. Accept only
                # deterioration; on suppression re-baseline the drift arm so
                # the ongoing decline does not immediately refire.
                if self.config.ecpf_drift_direction_gate:
                    self._gate_hist.append(float(drift_value))
                    if is_drift and not self._direction_gate_passes():
                        is_drift = False
                        self._ecpf_detector.reset_drift()
                self.tracer.log_signal(
                    index, y_true, y_pred, err,
                    warning_value, drift_value, is_warning, is_drift,
                    extra=ref_extra,
                )

                # Warning timeout: an unconfirmed warning that stays open for
                # thousands of steps poisons everything downstream -- a later
                # confirmation (even of a REAL drift) is stamped with the stale
                # warning time, and the buffer spanning two concepts is used
                # for model reuse selection. Close it and re-baseline the
                # warning arm; a genuine change will reopen it immediately.
                if (
                    self._ecpf_warning_active
                    and self.config.ecpf_detector_warning_timeout > 0
                    and self._ecpf_warning_start_idx is not None
                    and index - self._ecpf_warning_start_idx
                    > self.config.ecpf_detector_warning_timeout
                ):
                    logger.info(
                        "ECPF detector: warning from t=%d timed out at t=%d",
                        self._ecpf_warning_start_idx, index,
                    )
                    self._ecpf_warning_active = False
                    self._ecpf_warning_start_idx = None
                    self._ecpf_buffer = []
                    self._ecpf_pending_confirm = False
                    # Deliberately KEEP self._gate_baseline. Clearing it here made
                    # the timeout degrade the gate's anchor back into a sliding
                    # baseline on wide gradual transitions: each re-opened warning
                    # re-snapshotted mid-ramp and the gate then suppressed every
                    # confirmation (validated: rbf gradual/low 3 TPs -> 0). The
                    # baseline lives from the first warning after a confirmation
                    # until the next confirmation.
                    self._ecpf_detector.reset_warning()

                if is_warning and not self._ecpf_warning_active:
                    self._ecpf_warning_active = True
                    self._ecpf_warning_start_idx = int(index)
                    self._ecpf_buffer = []
                    if self.config.ecpf_drift_direction_gate and self._gate_baseline is None:
                        # Anchor the gate's baseline to the error level before the
                        # FIRST warning since the last confirmation -- everything
                        # from here on may already be drifting. Warnings re-opened
                        # after a timeout keep the original anchor (see the
                        # timeout block); a fresh anchor is taken only after a
                        # confirmation clears it.
                        tail = list(self._gate_hist)[-int(self.config.ecpf_gate_older):]
                        if len(tail) >= 300:
                            self._gate_baseline = sum(tail) / len(tail)
                    logger.info(
                        "ECPF detector: warning started at t=%d (%s)",
                        index,
                        self._ecpf_detector.combo_name,
                    )

                if (
                    self._ecpf_warning_active
                    and getattr(self._ecpf_detector, "zone", False)
                    and not is_warning
                    and not is_drift
                ):
                    # Official ECPF (E9): leaving the detector's warning zone without a
                    # drift ends the warning and drops its buffer.
                    self._ecpf_warning_active = False
                    self._ecpf_warning_start_idx = None
                    self._ecpf_buffer = []
                    self._ecpf_pending_confirm = False

                if self._ecpf_warning_active:
                    self._ecpf_buffer.append(
                        (np.asarray(x_.ravel(), dtype=np.float64).copy(), float(y_true))
                    )

                # Minimum warning age: hold the confirmation until the warning
                # buffer has k instances, otherwise the reuse decision is made
                # on a 1-instance buffer whenever both arms fire on the same
                # step. The scored timestamp (warning start) does not move.
                k = int(self.config.ecpf_min_warning_age)
                if k > 0 and self._ecpf_warning_active:
                    if is_drift and len(self._ecpf_buffer) < k:
                        self._ecpf_pending_confirm = True
                        is_drift = False
                    elif self._ecpf_pending_confirm and len(self._ecpf_buffer) >= k:
                        is_drift = True
                if is_drift and self._ecpf_warning_active and self._ecpf_buffer:
                    self._ecpf_pending_confirm = False
                    self._handle_ecpf_drift(
                        self._ecpf_buffer[:],
                        int(self._ecpf_warning_start_idx if self._ecpf_warning_start_idx is not None else index),
                        f"ecpf_detector_{self._ecpf_detector.combo_name}",
                        new_detections,
                        {
                            "ecpf_protocol": "detector_warning_drift",
                            "warning_signal": self.config.ecpf_warning_signal,
                            "drift_signal": self.config.ecpf_drift_signal,
                            **self._ecpf_detector.stats,
                        },
                    )
                    self._ecpf_warning_active = False
                    self._ecpf_warning_start_idx = None
                    self._ecpf_buffer = []
                    self._gate_baseline = None
                    self.meta_detector.reset()
                    if self._ecpf_guard is not None:
                        # E10b: the leader just changed and the reference is re-frozen below,
                        # so both detector pairs restart, whichever one confirmed.
                        self._ecpf_guard.reset()
                        self._ecpf_detector.reset()
                    # Prescription 3: re-baseline the residual normalizer on the
                    # new era together with the detectors (see config).
                    if self.config.ecpf_normalizer_reset_on_drift and self.task.is_regression:
                        self.task.normalizer.reset()
                    if self.config.ecpf_reference_signal:
                        # k=0: the just-installed clone becomes the reference right
                        # now; k>0 additionally schedules a re-freeze from the
                        # adapted leader (secondary arm).
                        self._freeze_reference(index)
                        self._ref_switch_due = (
                            int(index) + int(self.config.ecpf_reference_warmup)
                            if self.config.ecpf_reference_warmup > 0 else None
                        )
                    # Optional echo suppression (both default off; see config).
                    if self.config.ecpf_detector_reset_on_drift:
                        # Drop the windows that still describe the OLD leader's
                        # error stream so the detectors re-baseline on the new one.
                        self._ecpf_detector.reset()
                    if self.config.ecpf_detector_cooldown > 0:
                        self._ecpf_cooldown_left = int(self.config.ecpf_detector_cooldown)
                    self._batch_X.clear()
                    self._batch_y.clear()
                    self.buffer = StreamBuffer(
                        max_len=self.buffer.max_len if hasattr(self.buffer, "max_len") else 3000
                    )
                    return y_pred, new_detections, True

                if self._ecpf_warning_active:
                    return y_pred, [], False
            elif self.config.ecpf_signal_mode in {"meta_ecpf_dwm", "meta_ecpf_hcdt", "meta_ecpf_gddm", "meta_ecpf_hier_parallel"} and self.meta_detector is not None:
                # Update meta detector continuously
                proba_matrix = None
                if hasattr(self.prediction_model, 'predict_proba_matrix'):
                    try:
                        proba_matrix = self.prediction_model.predict_proba_matrix(x_)
                    except Exception:
                        pass
                
                is_drift, drift_time, sub_stats = self.meta_detector.update_and_detect(
                    x=x_flat,
                    y_true=y_true,
                    y_pred=y_pred,
                    err=err,
                    t=index,
                    proba_matrix=proba_matrix,
                )

                proxy_stats = sub_stats.get("proxy_indicators", {})
                uq_warning = proxy_stats.get("any_warning", False)
                detector_warning_active = proxy_stats.get("warning_active", self._ecpf_warning_active)
                false_positive = proxy_stats.get("false_positive", False)

                # Warning
                if uq_warning and not self._ecpf_warning_active:
                    self._ecpf_warning_active = True
                    self._ecpf_warning_start_idx = int(index)
                    self._ecpf_buffer = []

                if self._ecpf_warning_active:
                    self._ecpf_buffer.append(
                        (np.asarray(x_.ravel(), dtype=np.float64).copy(), float(y_true))
                    )

                if (
                    self.config.ecpf_signal_mode == "meta_ecpf_hcdt"
                    and self._ecpf_warning_active
                    and false_positive
                    and not is_drift
                ):
                    self._ecpf_warning_active = False
                    self._ecpf_warning_start_idx = None
                    self._ecpf_buffer = []
                    return y_pred, [], False

                if (
                    self.config.ecpf_signal_mode == "meta_ecpf_hcdt"
                    and self._ecpf_warning_active
                    and not detector_warning_active
                    and not is_drift
                ):
                    self._ecpf_warning_active = False
                    self._ecpf_warning_start_idx = None
                    self._ecpf_buffer = []
                    return y_pred, [], False

                # Drift confirmation
                if is_drift and self._ecpf_warning_active and self._ecpf_buffer:
                    detector_source = self.config.ecpf_signal_mode
                    protocol = (
                        "hcdt_detection_warning_then_rddm_validation"
                        if detector_source == "meta_ecpf_hcdt"
                        else "dwm_proxy_warning_then_voting_drift"
                    )
                    uq_proxy_stats = self._extract_uq_proxy_stats(sub_stats)
                    self._handle_ecpf_drift(
                        self._ecpf_buffer[:],
                        int(self._ecpf_warning_start_idx if self._ecpf_warning_start_idx is not None else index),
                        detector_source,
                        new_detections,
                        {
                            "ecpf_protocol": protocol,
                            "uq_mode": self.config.ecpf_uq_mode,
                            **sub_stats.get("meta_info", {}),
                            **uq_proxy_stats,
                        },
                    )
                    self._ecpf_warning_active = False
                    self._ecpf_warning_start_idx = None
                    self._ecpf_buffer = []
                    self.meta_detector.reset()
                    self._batch_X.clear()
                    self._batch_y.clear()
                    self.buffer = StreamBuffer(
                        max_len=self.buffer.max_len if hasattr(self.buffer, "max_len") else 3000
                    )
                    return y_pred, new_detections, True

                if self._ecpf_warning_active:
                    return y_pred, [], False


            elif self.config.ecpf_signal_mode == "uq_warning" and self._uq_warning_detector is not None:
                # --- Dual-layer: UQ warning (layer 1) + error-based drift (layer 2) ---

                # Layer 1: UQ-based early warning from forest ensemble disagreement
                proba_matrix = self.prediction_model.predict_proba_matrix(x_)
                uq_warning = self._uq_warning_detector.update(proba_matrix)

                # Layer 2: error-based ADWIN for drift confirmation only
                err01 = 1.0 if int(round(float(y_pred))) != int(round(float(y_true))) else 0.0
                _err_warning, is_drift = self._uq_drift_detector.update(err01)

                # --- UQ-only warning trigger ---
                # Only UQ-ADWIN can start buffer collection. Error ADWIN is kept
                # solely as the drift confirmation layer, so event buffers are
                # attributable to UQ warnings.
                if uq_warning and not self._ecpf_warning_active:
                    self._ecpf_warning_active = True
                    self._ecpf_warning_start_idx = int(index)
                    self._ecpf_buffer = []
                    logger.info(
                        "ECPF UQ warning: started at t=%d (src=uq, uq_smoothed=%.4f, mode=%s)",
                        index,
                        self._uq_warning_detector.last_uq_smoothed,
                        self._uq_warning_detector.uq_mode,
                    )

                # --- Warning timeout: cancel false alarm ---
                if self._ecpf_warning_active and self._ecpf_warning_start_idx is not None:
                    warning_age = index - self._ecpf_warning_start_idx
                    if warning_age >= self._uq_warning_timeout:
                        logger.info(
                            "ECPF UQ warning: TIMEOUT at t=%d (age=%d > %d), "
                            "cancelling false alarm, discarding %d buffer samples",
                            index, warning_age, self._uq_warning_timeout,
                            len(self._ecpf_buffer),
                        )
                        self._ecpf_warning_active = False
                        self._ecpf_warning_start_idx = None
                        self._ecpf_buffer = []
                        # Reset UQ detector so it re-adapts to current concept
                        self._uq_warning_detector.reset()
                        # Do NOT reset error-based detector (it may be tracking a real change)

                # Collect buffer while warning is active
                if self._ecpf_warning_active:
                    self._ecpf_buffer.append(
                        (np.asarray(x_.ravel(), dtype=np.float64).copy(), float(y_true))
                    )

                # --- Drift confirmation ---
                if is_drift and self._ecpf_warning_active and self._ecpf_buffer:
                    self._handle_ecpf_drift(
                        self._ecpf_buffer[:],
                        int(self._ecpf_warning_start_idx if self._ecpf_warning_start_idx is not None else index),
                        "ecpf_uq_warning",
                        new_detections,
                        {
                            "ecpf_protocol": "uq_warning_then_error_drift",
                            "uq_mode": self.config.ecpf_uq_mode,
                            **self._uq_warning_detector.stats,
                            **self._uq_drift_detector.stats,
                        },
                    )
                    self._ecpf_warning_active = False
                    self._ecpf_warning_start_idx = None
                    self._ecpf_buffer = []
                    self._uq_warning_detector.reset()
                    self._uq_drift_detector.reset()
                    self.meta_detector.reset()
                    self._batch_X.clear()
                    self._batch_y.clear()
                    self.buffer = StreamBuffer(
                        max_len=self.buffer.max_len if hasattr(self.buffer, "max_len") else 3000
                    )
                    return y_pred, new_detections, True

                if self._ecpf_warning_active:
                    return y_pred, [], False

        # ---- Online update for advanced models (true streaming) ----
        if self._use_advanced and not ecf_warn:
            from .models.base_model import BaseModel
            self.prediction_model.data_buffer.append(
                (BaseModel._to_dict(x_flat), y_true, index)
            )
            if not (self.config.use_ecpf and self._ecpf):
                self.prediction_model.learn_one(x_flat, y_true)

        # ---- Post-alert FIFO: collect samples after drift alarm (RCD-like) ----
        if not self.config.use_ecpf and self._collecting_post_alert_fifo and self._post_alert_fifo_err is not None:
            self._post_alert_fifo_err.append(err)
            self._post_alert_fifo_x.append(x_flat.astype(np.float64).copy())
            n_fifo = len(self._post_alert_fifo_err)
            cap = self.config.recurring_max_buffer_size
            need = self.config.recurring_fifo_min_samples
            if n_fifo >= need or n_fifo >= cap:
                self._finalize_post_alert_drift(new_detections)
            elif self._lock_out == 0 and n_fifo >= self.concept_memory.k_neighbors + 1:
                # Lockout ended before min samples: finalize with what we have
                self._finalize_post_alert_drift(new_detections)
            elif self._lock_out == 0 and n_fifo > 0:
                self._finalize_post_alert_drift(new_detections)
            if new_detections:
                return y_pred, new_detections, True

        # ---- Lock-out period: update model but skip detectors ----
        if self._lock_out > 0:
            if self.config.use_ecpf and self._ecpf:
                _pre_swaps = self._ecpf.leader_swaps
                self._ecpf.on_stream_instance(self.prediction_model, x_, y_true, y_pred_leader=y_pred)
                self.tracer.log_duel(
                    index, self._ecpf.curr_correct, self._ecpf.new_correct,
                    self._ecpf.total_inst,
                    swapped=self._ecpf.leader_swaps > _pre_swaps,
                    current_idx=self._ecpf.current_idx,
                    has_shadow=self._ecpf.new_model is not None,
                )
            elif not self._use_advanced:
                self._batch_X.append(x_flat)
                self._batch_y.append(y_true)
                if len(self._batch_y) >= self.config.update_batch_size:
                    self._incremental_adapt()
                    self._batch_X.clear()
                    self._batch_y.clear()
            return y_pred, [], False

        # ---- Update Meta-Detector (oracle ECPF ignores meta drift; uses ground-truth schedule) ----
        proba_matrix = None
        if hasattr(self.prediction_model, 'predict_proba_matrix'):
            try:
                proba_matrix = self.prediction_model.predict_proba_matrix(x_)
            except Exception:
                pass

        if self.config.use_ecpf and self.config.ecpf_signal_mode in {
            "oracle_60",
            *ECPF_ADWIN_FAMILY_SIGNAL_MODES,
            "meta_ecpf_dwm",
            "meta_ecpf_hcdt",
        }:
            is_drift, drift_time, sub_detector_stats = False, index, {}
        else:
            is_drift, drift_time, sub_detector_stats = self.meta_detector.update_and_detect(
                x=x_flat,
                y_true=y_true,
                y_pred=y_pred,
                err=err,
                t=index, proba_matrix=proba_matrix,
            )

        if is_drift and self.config.use_ecpf and self.config.ecpf_signal_mode == "meta_retro_60":
            buf = self._ecpf_tail_buffer(self.config.ecpf_warning_length)
            L = self.config.ecpf_warning_length
            if len(buf) >= L:
                self._handle_ecpf_drift(
                    buf,
                    drift_time,
                    "ecpf_meta_retro_60",
                    new_detections,
                    sub_detector_stats,
                )
            else:
                logger.warning(
                    "ECPF meta_retro: only %d samples in ring (need %d); skipping ECPF update",
                    len(buf),
                    L,
                )
            self.meta_detector.reset()
            self._batch_X.clear()
            self._batch_y.clear()
            self.buffer = StreamBuffer(
                max_len=self.buffer.max_len if hasattr(self.buffer, "max_len") else 3000
            )
            self._lock_out = self._lock_out_duration
            return y_pred, new_detections, True

        if is_drift and not self.config.use_ecpf:
            if self.config.recurring_use_post_alert_fifo:
                self._start_post_alert_fifo_collection(
                    drift_time, "meta_detector", sub_detector_stats, x_flat, err
                )
                self._lock_out = self._lock_out_duration
            else:
                self._handle_drift(errors, drift_time, 0, "meta_detector", new_detections, sub_detector_stats)
                self._lock_out = self._lock_out_duration
            return y_pred, new_detections, True

        # ---- No drift: incremental adaptation (ECPF trains leader + shadow each step) ----
        if self.config.use_ecpf and self._ecpf:
            _pre_swaps = self._ecpf.leader_swaps
            self._ecpf.on_stream_instance(self.prediction_model, x_, y_true, y_pred_leader=y_pred)
            self.tracer.log_duel(
                index, self._ecpf.curr_correct, self._ecpf.new_correct,
                self._ecpf.total_inst,
                swapped=self._ecpf.leader_swaps > _pre_swaps,
                current_idx=self._ecpf.current_idx,
                has_shadow=self._ecpf.new_model is not None,
            )
        elif not self._use_advanced:
            self._batch_X.append(x_flat)
            self._batch_y.append(y_true)
            if len(self._batch_y) >= self.config.update_batch_size:
                self._incremental_adapt()
                self._batch_X.clear()
                self._batch_y.clear()

        return y_pred, new_detections, False

    # ------------------------------------------------------------------
    # ECPF drift handling
    # ------------------------------------------------------------------
    def _ecpf_tail_buffer(self, n: int) -> List[Tuple[np.ndarray, float]]:
        """Last ``n`` (x, y) tuples from the ring buffer for meta-retro mode."""
        items = list(self._ecpf_ring)
        if len(items) <= n:
            return [(np.asarray(a, dtype=np.float64), float(b)) for a, b, _ in items]
        return [(np.asarray(a, dtype=np.float64), float(b)) for a, b, _ in items[-n:]]

    @staticmethod
    def _extract_uq_proxy_stats(sub_stats: Dict[str, Any]) -> Dict[str, Any]:
        proxy_stats = sub_stats.get("proxy_indicators", {})
        details = proxy_stats.get("details", {}) if isinstance(proxy_stats, dict) else {}
        if not isinstance(details, dict):
            return {}
        uq_entry = details.get("UQWarningIndicator", {})
        if not isinstance(uq_entry, dict):
            return {}
        stats = uq_entry.get("stats", {})
        return dict(stats) if isinstance(stats, dict) else {}

    # ------------------------------------------------------------------
    # Frozen reference: detector input decoupled from the adaptive learner
    # ------------------------------------------------------------------
    def _model_predict(self, model: Any, x_: np.ndarray) -> float:
        if self._use_advanced:
            return float(model.predict_one(x_))
        return float(model.predict(x_)[0])

    def _ref_loss(self, y_true: float, pred: float) -> float:
        """Raw loss of a reference prediction: |residual|, or 0/1 for classification."""
        if self.task.is_regression:
            return abs(float(y_true) - pred)
        return 1.0 if int(round(pred)) != int(round(float(y_true))) else 0.0

    def _freeze_reference(self, index: int) -> None:
        """Freeze a copy of the current leader as the detectors' reference."""
        self._ref_model = _deep_clone(self.prediction_model)
        self._ref_norm.reset()
        self._ref_frozen_at = int(index)

    def _switch_reference(self, index: int) -> dict:
        """Secondary arm: re-freeze from the adapted leader (a switch reset).

        The detectors' input steps down here, so both arms restart, an open
        warning is closed and its buffer dropped; the previous reference
        shadow-runs 500 steps so both can be compared on the same data.
        """
        age = (
            int(index) - int(self._ecpf_warning_start_idx)
            if self._ecpf_warning_active and self._ecpf_warning_start_idx is not None
            else -1
        )
        self._ref_shadow, self._ref_shadow_until = self._ref_model, int(index) + 500
        self._freeze_reference(index)
        self._ref_switch_due = None
        self._ecpf_detector.reset()
        self._ecpf_warning_active = False
        self._ecpf_warning_start_idx = None
        self._ecpf_buffer = []
        self._ecpf_pending_confirm = False
        return {"ref_switch": 1, "switch_warning_age": age}

    def _handle_ecpf_drift(
        self,
        buffer: List[Tuple[np.ndarray, float]],
        drift_ts: int,
        source: str,
        out_detections: List[DriftDetection],
        detector_details: dict,
    ) -> None:
        if self._ecpf is None:
            return
        merged_details = dict(detector_details or {})
        ecpf_details = self._ecpf.on_drift(self.prediction_model, buffer)
        merged_details.update(ecpf_details)
        self.tracer.on_event(
            warning_t=drift_ts,
            confirmation_t=self._trace_index,
            source=source,
            stage2=dict(detector_details or {}),
            stage3=ecpf_details,
        )
        out_detections.append(
            DriftDetection(
                timestamp=drift_ts,
                drift_type=DriftType.SUDDEN,
                detector_source=source,
                raw_drift=True,
                details=merged_details,
            )
        )
        self.detections.append(out_detections[-1])

    # ------------------------------------------------------------------
    # Post-alert FIFO (RCD-like sample collection)
    # ------------------------------------------------------------------
    def _start_post_alert_fifo_collection(
        self,
        alert_index: int,
        detector_source: str,
        detector_details: dict,
        x: np.ndarray,
        err: float,
    ) -> None:
        cap = self.config.recurring_max_buffer_size
        self._post_alert_fifo_x = deque(maxlen=cap)
        self._post_alert_fifo_err = deque(maxlen=cap)
        self._post_alert_fifo_x.append(np.asarray(x, dtype=np.float64).ravel().copy())
        self._post_alert_fifo_err.append(float(err))
        self._collecting_post_alert_fifo = True
        self._pending_drift = {
            "alert_index": int(alert_index),
            "source": detector_source,
            "details": dict(detector_details),
        }
        logger.info(
            "Drift alarm at t=%d (%s); collecting post-alert FIFO (min=%d, cap=%d)",
            alert_index,
            detector_source,
            self.config.recurring_fifo_min_samples,
            cap,
        )

    def _finalize_post_alert_drift(self, out_detections: List[DriftDetection]) -> None:
        if not self._collecting_post_alert_fifo or self._pending_drift is None:
            return
        if not self._post_alert_fifo_x or not self._post_alert_fifo_err:
            self._collecting_post_alert_fifo = False
            self._post_alert_fifo_x = None
            self._post_alert_fifo_err = None
            self._pending_drift = None
            return

        Xw = np.stack(list(self._post_alert_fifo_x), axis=0)
        ew = np.array(list(self._post_alert_fifo_err), dtype=np.float64)
        pending = self._pending_drift
        self._collecting_post_alert_fifo = False
        self._post_alert_fifo_x = None
        self._post_alert_fifo_err = None
        self._pending_drift = None

        errors_flat = self.buffer.get_errors()
        self._handle_drift(
            errors_flat,
            pending["alert_index"],
            0,
            pending["source"],
            out_detections,
            pending["details"],
            post_alert_X=Xw,
            post_alert_errors=ew,
        )
        self._lock_out = 0

    # ------------------------------------------------------------------
    # Drift handling
    # ------------------------------------------------------------------
    def _handle_drift(
        self,
        errors: np.ndarray,
        current_index: int,
        detector_ts: int,
        detector_source: str,
        out_detections: List[DriftDetection],
        detector_details: dict = None,
        post_alert_X: Optional[np.ndarray] = None,
        post_alert_errors: Optional[np.ndarray] = None,
    ) -> None:
        if detector_details is None:
            detector_details = {}
        drift_alert_timestamp = current_index
        errors_flat = self.buffer.get_errors()
        err_idx = len(errors_flat) - 1

        # --- Recurring drift check (RCD-style kNN mixing) ---
        if post_alert_errors is not None or post_alert_X is not None:
            recurring = detect_recurring_drift(
                errors_flat,
                drift_alert_timestamp,
                self.concept_memory,
                add_if_new=self.config.concept_memory_add_if_new,
                recurrence_threshold=self.config.recurrence_threshold,
                post_alert_X=post_alert_X,
                post_alert_errors=post_alert_errors,
            )
        else:
            X_window = self.buffer.get_feature_window(
                err_idx,
                self.concept_memory.window_before,
                self.concept_memory.window_after,
            )
            recurring = detect_recurring_drift(
                errors_flat,
                err_idx,
                self.concept_memory,
                add_if_new=self.config.concept_memory_add_if_new,
                recurrence_threshold=self.config.recurrence_threshold,
                X_window=X_window,
            )

        if recurring:
            out_detections.append(DriftDetection(
                timestamp=drift_alert_timestamp,
                drift_type=DriftType.RECURRING,
                detector_source=detector_source,
                raw_drift=True,
                details=detector_details
            ))
            self.detections.append(out_detections[-1])

            # Try to retrieve a previously saved model for this concept
            retrieved_model = self._try_retrieve_recurring_model()
            if retrieved_model is not None:
                if self._use_advanced:
                    self.prediction_model.set_model(retrieved_model)
                    self._warm = True
                else:
                    self.prediction_model.set_model(retrieved_model)
                    self._warm = True
                logger.info(
                    "Recurring drift at t=%d — restored model from pool",
                    drift_alert_timestamp,
                )
            else:
                self._reset_model()
                logger.info(
                    "Recurring drift at t=%d — no matching model in pool, resetting",
                    drift_alert_timestamp,
                )
        else:
            # --- Classify as sudden / gradual / incremental ---
            classified = classify_drift_type(errors_flat, err_idx)
            out_detections.append(DriftDetection(
                timestamp=drift_alert_timestamp,
                drift_type=classified,
                detector_source=detector_source,
                raw_drift=True,
                details=detector_details
            ))
            self.detections.append(out_detections[-1])

            # Save current model before resetting
            concept_id = f"concept_{self._concept_counter}"
            self._concept_counter += 1

            if self._use_advanced:
                self.model_pool.save(concept_id, self.prediction_model.get_model())
            else:
                self.model_pool.save(concept_id, self.prediction_model.get_model())

            # --- Apply drift-type-specific strategy ---
            if classified == DriftType.SUDDEN:
                self._handle_sudden_reset(drift_alert_timestamp)
            elif classified == DriftType.GRADUAL:
                self._handle_gradual_reset(drift_alert_timestamp)
            else:
                # Incremental: keep continuity and adapt conservatively (same handler as gradual for now)
                self._handle_gradual_reset(drift_alert_timestamp)

        # Reset detectors
        self.meta_detector.reset()

        self._batch_X.clear()
        self._batch_y.clear()

        self.buffer = StreamBuffer(
            max_len=self.buffer.max_len if hasattr(self.buffer, 'max_len') else 3000
        )

    def _handle_sudden_reset(self, timestamp: int) -> None:
        """Sudden drift: hard reset — create fresh model.

        For advanced models, replay post-drift samples via learn_one so the
        new model immediately starts adapting to the new concept.  The model
        stays warm (_warm=True) because BaseModel.predict_one always works,
        even with zero training — it returns a safe default.  The lock-out
        period (500 steps) shields detectors from the initial noise.
        """
        if self._use_advanced:
            adapter: BaseModelAdapter = self.prediction_model
            post_drift = [
                (x, y) for x, y, idx in adapter.data_buffer if idx >= timestamp
            ]
            adapter.reset_model()
            if post_drift:
                for x_dict, y_val in post_drift:
                    adapter.get_model().learn_one(x_dict, y_val)
                logger.info(
                    "Sudden drift at t=%d — replayed %d post-drift samples via learn_one",
                    timestamp, len(post_drift),
                )
            else:
                logger.info(
                    "Sudden drift at t=%d — fresh model, will learn_one from next sample",
                    timestamp,
                )
            # Advanced models can predict from sample 0 — stay warm.
            # Set _cold_start_count so detectors remain gated until
            # update_batch_size samples have been processed.
            self._warm = False
            self._cold_start_count = 0
        else:
            # Rebuild through the factory, not a bare PredictionModel(...): a
            # hand-rolled wrapper here would silently drop the declared class set
            # and put a K > 2 stream back on the arrival-order failure.
            self.prediction_model = self._build_prediction_model()
            self._warm = False

    def _handle_gradual_reset(self, timestamp: int) -> None:
        """Gradual drift: for advanced models, keep the model (learn_one adapts).
        For original models, reset like sudden (same as original behaviour).
        """
        if self._use_advanced:
            logger.info(
                "Gradual drift at t=%d — model continues adapting via learn_one",
                timestamp,
            )
        else:
            self.prediction_model = self._build_prediction_model()
            self._warm = False

    def _reset_model(self) -> None:
        """Full model reset (used when no pool model is found for recurring drift)."""
        if self._use_advanced:
            self.prediction_model.reset_model()
        else:
            self.prediction_model = self._build_prediction_model()
        self._warm = False

    def _try_retrieve_recurring_model(self):
        """Attempt to retrieve the most recently saved model from the pool.

        A more sophisticated approach would match concept signatures to model
        IDs; for now we retrieve the most recent one as a reasonable heuristic.
        """
        ids = self.model_pool.list_ids()
        if not ids:
            return None
        latest_id = ids[-1]
        return self.model_pool.retrieve(latest_id)

    # ------------------------------------------------------------------
    # Incremental adaptation (original models only)
    # ------------------------------------------------------------------
    def _incremental_adapt(self) -> None:
        if len(self._batch_X) < 2:
            return
        X_b = np.array(self._batch_X)
        y_b = np.array(self._batch_y)
        self.prediction_model.fine_tune(X_b, y_b)

    # ------------------------------------------------------------------
    # Full stream runner
    # ------------------------------------------------------------------
    def run_stream(
        self,
        X: np.ndarray,
        y: np.ndarray,
        warm_start_samples: Optional[int] = None,
    ) -> Iterator[Tuple[int, float, float, List[DriftDetection], bool]]:
        """
        Run pipeline over arrays X, y. Yields (index, y_true, y_pred, detections, drift_occurred).
        """
        X, y = np.asarray(X), np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        # Resolve classification vs regression from the whole target array before
        # anything is fit; this may swap the backend and the ECPF similarity rule.
        self._bind_task(y)
        n = len(y)
        if warm_start_samples and warm_start_samples > 0:
            self.warm_start(X[:warm_start_samples], y[:warm_start_samples])
            start = warm_start_samples
        else:
            start = 0
        for i in range(start, n):
            y_pred, dets, drift = self.step(X[i], y[i], index=i)
            yield i, float(y[i]), y_pred, dets, drift


def run_pipeline_demo(
    n_samples: int = 10_000,
    drift_at: Optional[List[int]] = None,
    seed: int = 42,
    use_river: bool = True,
) -> Tuple["ConceptDriftPipeline", np.ndarray, np.ndarray]:
    """
    Generate synthetic stream with concept drift and run full pipeline.

    Returns (pipeline, y_true, y_pred array for evaluation).
    """
    np.random.seed(seed)

    if use_river and RIVER_AVAILABLE:
        from river.datasets import synth

        s0 = synth.SEA(seed=seed, variant=0)
        s1 = synth.SEA(seed=seed+1, variant=2)
        s2 = synth.SEA(seed=seed+2, variant=3)
        s3 = synth.SEA(seed=seed+3, variant=1)
        s4 = synth.SEA(seed=seed+4, variant=0)

        if drift_at is None:
            drift_at = [2000, 4000, 6000, 8000]

        streams = [s0, s1, s2, s3, s4]

        X_list = []
        y_list = []

        current_stream = 0
        stream_iter = iter(streams[0])

        for i in range(n_samples):
            if current_stream < len(drift_at) and i == drift_at[current_stream]:
                current_stream += 1
                stream_iter = iter(streams[current_stream])

            x, y = next(stream_iter)
            if current_stream % 2 == 1:
                y = 1 - y
            X_list.append(list(x.values()))
            y_list.append(y)

        X = np.array(X_list)
        y = np.array(y_list, dtype=float)
    else:
        if drift_at is None:
            drift_at = [200, 400, 600]

        t = np.linspace(0, 4 * np.pi, n_samples)
        y = np.sin(t) + 0.1 * np.random.randn(n_samples)
        for i, pos in enumerate(drift_at):
            if pos < n_samples:
                y[pos:] += 0.5 * (i + 1)
        X = t.reshape(-1, 1)

    config = PipelineConfig(
        meta_ks_window_size=100,
        atom_min_samples=30,
        update_batch_size=250,
        recurrence_threshold=0.15,
    )
    pipeline = ConceptDriftPipeline(config=config)
    pipeline.warm_start(X[:50], y[:50])

    y_pred = np.zeros(n_samples)
    y_pred[:50] = np.nan
    for i in range(50, n_samples):
        y_p, dets, _ = pipeline.step(X[i], y[i], index=i)
        y_pred[i] = y_p
        for d in dets:
            print(f"  Drift at t={d.timestamp}: {d.drift_type.value} (source: {d.detector_source})")

    return pipeline, y, y_pred


def load_recurring_stream_pair(
    csv_path: str,
    drift_times_path: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, List[int]]:
    """
    Load recurring stream CSV and matching drift times.

    Expected CSV columns: feature columns + ``y``.
    If ``drift_times_path`` is omitted, it is inferred by replacing ``.csv`` with
    ``_drift_times.txt``.
    """
    cp = Path(csv_path)
    if drift_times_path is None:
        drift_times_path = str(cp.with_name(cp.stem + "_drift_times.txt"))

    df = pd.read_csv(cp)
    if "y" not in df.columns:
        raise ValueError(f"CSV must contain 'y' column: {csv_path}")
    y = df["y"].to_numpy(dtype=float)
    X = df.drop(columns=["y"]).to_numpy(dtype=np.float64)
    drift_times = load_drift_times_file(drift_times_path)
    return X, y, drift_times


def run_ecpf_on_recurring_csv(
    csv_path: str,
    *,
    drift_times_path: Optional[str] = None,
    warm_start_samples: int = 200,
    config: Optional[PipelineConfig] = None,
) -> Tuple[ConceptDriftPipeline, np.ndarray, np.ndarray]:
    """
    Convenience runner for ``data/recurring_drift/*.csv`` with ECPF oracle mode.

    Uses matched ``*_drift_times.txt`` by default and sets oracle drift starts at T.
    """
    X, y, drift_times = load_recurring_stream_pair(csv_path, drift_times_path)
    cfg = config or PipelineConfig()
    cfg.use_ecpf = True
    cfg.model_type = "ht"
    cfg.ecpf_signal_mode = "oracle_60"
    cfg.ecpf_oracle_true_drift_times = drift_times
    cfg.ecpf_warning_length = 60
    cfg.ecpf_max_pool_size = 10

    pipeline = ConceptDriftPipeline(cfg)
    pipeline.warm_start(X[:warm_start_samples], y[:warm_start_samples])

    y_pred = np.full(len(y), np.nan, dtype=float)
    for i in range(warm_start_samples, len(y)):
        yp, _, _ = pipeline.step(X[i], y[i], index=i)
        y_pred[i] = yp
    return pipeline, y, y_pred
