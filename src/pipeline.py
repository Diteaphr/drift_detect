"""
Main concept drift pipeline: data stream → preprocessing → sudden/gradual detectors
→ recurring detector → drift type classifier → model pool & incremental adaptation.
"""

import numpy as np
from typing import Iterator, List, Optional, Tuple

from .config import DriftDetection, DriftType, PipelineConfig
from .preprocessing import StreamBuffer, compute_prediction_errors, smooth_errors
from detectors import (
    SuddenDriftDetector,
    GradualDriftDetector,
    ConceptMemory,
    detect_recurring_drift,
)
from .drift_type_classifier import classify_drift_type
from .model_pool import ModelPool
from .prediction_model import PredictionModel


class ConceptDriftPipeline:
    """
    Full pipeline: consume (X, y) stream, maintain prediction model, run detectors,
    output detections and optionally adapt the model.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.buffer = StreamBuffer(max_len=3000)
        self.sudden_detector = SuddenDriftDetector(
            window_size=self.config.sudden_window_size,
            min_samples=20,
            ensemble_strategy="majority",
        )
        self.gradual_detector = GradualDriftDetector(ensemble_strategy="majority")
        self.concept_memory = ConceptMemory(recurrence_threshold=self.config.recurrence_threshold)
        self.model_pool = ModelPool(in_memory=True)
        self.prediction_model = PredictionModel(model_type=self.config.model_type)
        self.detections: List[DriftDetection] = []
        self._step = 0
        self._batch_X: List[np.ndarray] = []
        self._batch_y: List[float] = []
        self._warm = False

    def warm_start(self, X: np.ndarray, y: np.ndarray) -> None:
        """Initial fit of the prediction model on first batch."""
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self.prediction_model.fit(X, y)
        self._warm = True

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

        x_ = np.asarray(x)
        if x_.ndim == 0:
            x_ = x_.reshape(1)
        if x_.ndim == 1:
            x_ = x_.reshape(1, -1)
        y_pred = float(self.prediction_model.predict(x_)[0])
        if not self._warm:
            self._batch_X.append(x_.ravel())
            self._batch_y.append(y_true)
            if len(self._batch_y) >= self.config.update_batch_size:
                X_b = np.array(self._batch_X)
                y_b = np.array(self._batch_y)
                self.warm_start(X_b, y_b)
                self._batch_X.clear()
                self._batch_y.clear()
            self.buffer.append(y_true, y_pred, index)
            return y_pred, [], False

        self.buffer.append(y_true, y_pred, index)
        errors = self.buffer.get_errors()
        err = float(np.abs(y_true - y_pred))

        self.sudden_detector.update(err)
        self.gradual_detector.update(err)

        new_detections: List[DriftDetection] = []
        drift_occurred = False

        sudden_result = self.sudden_detector.detect()
        sudden = sudden_result[0] if isinstance(sudden_result, tuple) else sudden_result
        if sudden:
            drift_occurred = True
            self._handle_drift(errors, index, 0, "sudden", new_detections)
            return y_pred, new_detections, True

        gradual_result = self.gradual_detector.detect()
        gradual = gradual_result[0] if isinstance(gradual_result, tuple) else gradual_result
        if gradual:
            drift_occurred = True
            self._handle_drift(errors, index, 0, "gradual", new_detections)
            return y_pred, new_detections, True

        # No drift: maybe incremental adaptation when batch size reached
        self._batch_X.append(x_.ravel())
        self._batch_y.append(y_true)
        if len(self._batch_y) >= self.config.update_batch_size:
            self._incremental_adapt()
            self._batch_X.clear()
            self._batch_y.clear()

        return y_pred, new_detections, False

    def _handle_drift(
        self,
        errors: np.ndarray,
        current_index: int,
        detector_ts: int,
        detector_source: str,
        out_detections: List[DriftDetection],
    ) -> None:
        # Drift is at current stream position (we just detected it here)
        drift_alert_timestamp = current_index
        errors_flat = self.buffer.get_errors()
        # Index into error array for signature: use end of buffer (most recent)
        err_idx = len(errors_flat) - 1

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
            ))
            self.detections.append(out_detections[-1])
            # Option: retrieve model from pool for this concept (simplified: skip here)
        else:
            classified = classify_drift_type(errors_flat, err_idx)
            out_detections.append(DriftDetection(
                timestamp=drift_alert_timestamp,
                drift_type=classified,
                detector_source=detector_source,
                raw_drift=True,
            ))
            self.detections.append(out_detections[-1])
            # Save current model to pool for possible retrieval on recurring drift
            self.model_pool.save(f"concept_{drift_alert_timestamp}", self.prediction_model.get_model())

        # Reset detectors so next drift is a fresh detection
        self.sudden_detector.reset()
        self.gradual_detector.reset()

    def _incremental_adapt(self) -> None:
        if len(self._batch_X) < 2:
            return
        X_b = np.array(self._batch_X)
        y_b = np.array(self._batch_y)
        if self.config.model_type == "linear":
            self.prediction_model.retrain(X_b, y_b)
        else:
            self.prediction_model.fine_tune(X_b, y_b)

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
    n_samples: int = 800,
    drift_at: Optional[List[int]] = None,
    seed: int = 42,
) -> Tuple[ConceptDriftPipeline, np.ndarray, np.ndarray]:
    """
    Generate synthetic stream with concept drift and run full pipeline.
    Returns (pipeline, y_true, y_pred array for evaluation).
    """
    np.random.seed(seed)
    if drift_at is None:
        drift_at = [200, 400, 600]
    t = np.linspace(0, 4 * np.pi, n_samples)
    # Base concept + drifts (mean shift)
    y = np.sin(t) + 0.1 * np.random.randn(n_samples)
    for i, pos in enumerate(drift_at):
        if pos < n_samples:
            y[pos:] += 0.5 * (i + 1)
    X = t.reshape(-1, 1)

    config = PipelineConfig(
        sudden_window_size=40,
        gradual_window_size=80,
        update_batch_size=50,
        recurrence_threshold=0.6,
    )
    pipeline = ConceptDriftPipeline(config=config)
    pipeline.warm_start(X[:80], y[:80])

    y_pred = np.zeros(n_samples)
    y_pred[:80] = np.nan
    for i in range(80, n_samples):
        y_p, dets, _ = pipeline.step(X[i], y[i], index=i)
        y_pred[i] = y_p
        for d in dets:
            print(f"  Drift at t={d.timestamp}: {d.drift_type.value} (source: {d.detector_source})")

    return pipeline, y, y_pred
