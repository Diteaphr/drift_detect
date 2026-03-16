"""
Main concept drift pipeline: data stream → preprocessing → sudden/gradual detectors
→ recurring detector → drift type classifier → model pool & incremental adaptation.

Supports two model backends:
  - Original sklearn-based PredictionModel ("linear" / "nonlinear")
  - Advanced BaseModel-based models via BaseModelAdapter ("elastic" / "rf" / "xgb" / "gru")
"""

import logging
import numpy as np
from typing import Iterator, List, Optional, Tuple, Union

from .config import DriftDetection, DriftType, PipelineConfig
from .preprocessing import StreamBuffer, compute_prediction_errors, smooth_errors
from detectors import (
    SuddenDriftDetector,
    GradualDriftDetector,
    DistributionModule,
    ConceptMemory,
    detect_recurring_drift,
)
from .drift_type_classifier import classify_drift_type
from .model_pool import ModelPool
from .prediction_model import PredictionModel
from .model_adapter import BaseModelAdapter, is_advanced_model_type

try:
    from river import datasets
    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False

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
        self.sudden_detector = SuddenDriftDetector(
            window_size=self.config.sudden_window_size,
            min_samples=30,
            ensemble_strategy="majority",
        )
        self.gradual_detector = GradualDriftDetector(ensemble_strategy="majority")
        self.distribution_detector = DistributionModule(window_size=100)
        self.concept_memory = ConceptMemory(recurrence_threshold=self.config.recurrence_threshold)
        self.model_pool = ModelPool(in_memory=True)
        self.detections: List[DriftDetection] = []
        self._step = 0
        self._lock_out = 0
        self._lock_out_duration = 500
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

        x_ = np.asarray(x)
        if x_.ndim == 0:
            x_ = x_.reshape(1)
        if x_.ndim == 1:
            x_ = x_.reshape(1, -1)

        # ---- Not yet warmed up ----
        if not self._warm:
            if self._use_advanced:
                # River / XGBoost / GRU models can predict_one even with zero
                # training data (they return a safe default).  So we predict
                # FIRST, then learn_one — true test-then-train from sample 1.
                # The lock-out period shields detectors from the initial noise.
                y_pred = float(self.prediction_model.predict_one(x_))
                self.prediction_model.learn_one(x_.ravel(), y_true)
                from .models.base_model import BaseModel
                self.prediction_model.data_buffer.append(
                    (BaseModel._to_dict(x_.ravel()), y_true, index)
                )
                self.buffer.append(y_true, y_pred, index)
                self._cold_start_count = getattr(self, '_cold_start_count', 0) + 1
                if self._cold_start_count >= self.config.update_batch_size:
                    self._warm = True
                    self._cold_start_count = 0
                return y_pred, [], False
            else:
                self._batch_X.append(x_.ravel())
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

        self.buffer.append(y_true, y_pred, index)
        errors = self.buffer.get_errors()
        err = float(np.abs(y_true - y_pred))

        # ---- Online update for advanced models (true streaming) ----
        if self._use_advanced:
            self.prediction_model.learn_one(x_.ravel(), y_true)
            # Also track in adapter's rolling buffer for post-drift retraining
            from .models.base_model import BaseModel
            self.prediction_model.data_buffer.append(
                (BaseModel._to_dict(x_.ravel()), y_true, index)
            )

        # ---- Lock-out period: update model but skip detectors ----
        if self._lock_out > 0:
            if not self._use_advanced:
                self._batch_X.append(x_.ravel())
                self._batch_y.append(y_true)
                if len(self._batch_y) >= self.config.update_batch_size:
                    self._incremental_adapt()
                    self._batch_X.clear()
                    self._batch_y.clear()
            return y_pred, [], False

        # ---- Update detectors ----
        self.distribution_detector.update(x_)
        data_drift_warning = self.distribution_detector.detect()

        self.sudden_detector.update(err)
        self.gradual_detector.update(err)

        new_detections: List[DriftDetection] = []
        drift_occurred = False

        if data_drift_warning:
            if hasattr(self.sudden_detector, "ensemble_strategy"):
                self.sudden_detector.ensemble_strategy = "any"
            if hasattr(self.gradual_detector, "ensemble_strategy"):
                self.gradual_detector.ensemble_strategy = "any"
        else:
            if hasattr(self.sudden_detector, "ensemble_strategy"):
                self.sudden_detector.ensemble_strategy = "majority"
            if hasattr(self.gradual_detector, "ensemble_strategy"):
                self.gradual_detector.ensemble_strategy = "majority"

        sudden_result = self.sudden_detector.detect()
        if isinstance(sudden_result, tuple):
            sudden, sudden_details = sudden_result
        else:
            sudden, sudden_details = sudden_result, {}

        if sudden:
            sudden_details["data_drift_warning"] = data_drift_warning
            sudden_details["strategy"] = getattr(self.sudden_detector, "ensemble_strategy", "unknown")
            drift_occurred = True
            self._handle_drift(errors, index, 0, "sudden", new_detections, sudden_details)
            self._lock_out = self._lock_out_duration
            return y_pred, new_detections, True

        gradual_result = self.gradual_detector.detect()
        if isinstance(gradual_result, tuple):
            gradual, gradual_details = gradual_result
        else:
            gradual, gradual_details = gradual_result, {}

        if gradual:
            gradual_details["data_drift_warning"] = data_drift_warning
            gradual_details["strategy"] = getattr(self.gradual_detector, "ensemble_strategy", "unknown")
            drift_occurred = True
            self._handle_drift(errors, index, 0, "gradual", new_detections, gradual_details)
            self._lock_out = self._lock_out_duration
            return y_pred, new_detections, True

        # ---- No drift: incremental adaptation ----
        if not self._use_advanced:
            self._batch_X.append(x_.ravel())
            self._batch_y.append(y_true)
            if len(self._batch_y) >= self.config.update_batch_size:
                self._incremental_adapt()
                self._batch_X.clear()
                self._batch_y.clear()

        return y_pred, new_detections, False

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
    ) -> None:
        if detector_details is None:
            detector_details = {}
        drift_alert_timestamp = current_index
        errors_flat = self.buffer.get_errors()
        err_idx = len(errors_flat) - 1

        # --- Recurring drift check ---
        recurring = detect_recurring_drift(
            errors_flat,
            err_idx,
            self.concept_memory,
            add_if_new=self.config.concept_memory_add_if_new,
            recurrence_threshold=self.config.recurrence_threshold,
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
            # --- Classify as sudden or gradual ---
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
            else:
                self._handle_gradual_reset(drift_alert_timestamp)

        # Reset detectors
        self.sudden_detector.reset()
        self.gradual_detector.reset()
        self.distribution_detector.reset()

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
        sudden_window_size=50,
        gradual_window_size=100,
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
