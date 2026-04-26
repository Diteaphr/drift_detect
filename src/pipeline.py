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
from .preprocessing import StreamBuffer
from detectors import (
    ConceptMemory,
    detect_recurring_drift,
)
from .ecpf import ECPFMetaLearner, load_drift_times_file
from .ecpf_detector import ECPFWarningDriftDetector
from .drift_type_classifier_dtc_rf import classify_drift_type
from .model_pool import ModelPool
from .prediction_model import PredictionModel
from .model_adapter import BaseModelAdapter, is_advanced_model_type

try:
    import river  # noqa: F401

    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False

from detectors.meta import TwoStageVotingDetector, DynamicWeightedVotingDetector, StatisticalFusionDetector
from detectors.meta.indicators import KSDistributionIndicator, ErrorRateTrendIndicator, UncertaintyProxyIndicator

logger = logging.getLogger(__name__)


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

        if self.config.meta_detector_type == "two_stage":
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

        # --- Model backend selection ---
        self._use_advanced = is_advanced_model_type(self.config.model_type)

        if self._use_advanced:
            self.prediction_model: Union[PredictionModel, BaseModelAdapter] = (
                BaseModelAdapter(
                    model_type=self.config.model_type,
                    model_kwargs=self.config.model_kwargs,
                )
            )
        else:
            self.prediction_model = PredictionModel(model_type=self.config.model_type)

        # ECPF (Enhanced Concept Profiling Framework)
        self._ecpf: Optional[ECPFMetaLearner] = None
        if self.config.use_ecpf:
            self._ecpf = ECPFMetaLearner(
                similarity_margin=self.config.ecpf_similarity_margin,
                fade_points=self.config.ecpf_fade_points,
                model_check_freq=self.config.ecpf_model_check_freq,
                fade_enabled=self.config.ecpf_fade_enabled,
                max_pool_size=self.config.ecpf_max_pool_size,
                use_advanced=self._use_advanced,
                model_type=self.config.model_type,
                model_kwargs=self.config.model_kwargs,
            )
        self._ecpf_warning_active = False
        self._ecpf_warning_start_idx: Optional[int] = None
        self._ecpf_buffer: List[Tuple[np.ndarray, float]] = []
        self._ecpf_oracle_started: set = set()
        self._ecpf_ring: deque = deque(maxlen=5000)
        self._ecpf_detector: Optional[ECPFWarningDriftDetector] = None
        if self.config.use_ecpf and self.config.ecpf_signal_mode == "detector":
            self._ecpf_detector = ECPFWarningDriftDetector(
                min_num_instances=self.config.ecpf_detector_min_instances,
                delta=self.config.detector_delta,
                delta_w=self.config.detector_delta_w,
            )

        # Post-alert FIFO for RCD-like recurring test (collect after drift alarm)
        self._collecting_post_alert_fifo: bool = False
        self._post_alert_fifo_x: Optional[deque] = None
        self._post_alert_fifo_err: Optional[deque] = None
        self._pending_drift: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Warm start
    # ------------------------------------------------------------------
    def warm_start(self, X: np.ndarray, y: np.ndarray) -> None:
        """Initial fit of the prediction model on first batch."""
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
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
                self.buffer.append(y_true, y_pred, index, x=x_flat)
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

        self.buffer.append(y_true, y_pred, index, x=x_flat)
        errors = self.buffer.get_errors()
        err = float(np.abs(y_true - y_pred))

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
            elif self.config.ecpf_signal_mode == "detector" and self._ecpf_detector is not None:
                err01 = 1.0 if int(round(float(y_pred))) != int(round(float(y_true))) else 0.0
                is_warning, is_drift = self._ecpf_detector.update(err01)

                if is_warning and not self._ecpf_warning_active:
                    self._ecpf_warning_active = True
                    self._ecpf_warning_start_idx = int(index)
                    self._ecpf_buffer = []
                    logger.info("ECPF detector: warning started at t=%d", index)

                if self._ecpf_warning_active:
                    self._ecpf_buffer.append(
                        (np.asarray(x_.ravel(), dtype=np.float64).copy(), float(y_true))
                    )

                if is_drift and self._ecpf_warning_active and self._ecpf_buffer:
                    self._handle_ecpf_drift(
                        self._ecpf_buffer[:],
                        int(self._ecpf_warning_start_idx if self._ecpf_warning_start_idx is not None else index),
                            "ecpf_detector_adwin_dual",
                        new_detections,
                            {
                                "ecpf_protocol": "detector_warning_drift",
                                "detector_type": "adwin_dual",
                                **self._ecpf_detector.stats,
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
                self._ecpf.on_stream_instance(self.prediction_model, x_, y_true, y_pred_leader=y_pred)
            elif not self._use_advanced:
                self._batch_X.append(x_flat)
                self._batch_y.append(y_true)
                if len(self._batch_y) >= self.config.update_batch_size:
                    self._incremental_adapt()
                    self._batch_X.clear()
                    self._batch_y.clear()
            return y_pred, [], False

        # ---- Update Meta-Detector (oracle ECPF ignores meta drift; uses ground-truth schedule) ----
        if self.config.use_ecpf and self.config.ecpf_signal_mode in {"oracle_60", "detector"}:
            is_drift, drift_time, sub_detector_stats = False, index, {}
        else:
            is_drift, drift_time, sub_detector_stats = self.meta_detector.update_and_detect(
                x=x_flat,
                y_true=y_true,
                y_pred=y_pred,
                err=err,
                t=index,
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
            self._ecpf.on_stream_instance(self.prediction_model, x_, y_true, y_pred_leader=y_pred)
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
        merged_details.update(self._ecpf.on_drift(self.prediction_model, buffer))
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
            self.prediction_model = PredictionModel(model_type=self.config.model_type)
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
            self.prediction_model = PredictionModel(model_type=self.config.model_type)
            self._warm = False

    def _reset_model(self) -> None:
        """Full model reset (used when no pool model is found for recurring drift)."""
        if self._use_advanced:
            self.prediction_model.reset_model()
        else:
            self.prediction_model = PredictionModel(model_type=self.config.model_type)
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
