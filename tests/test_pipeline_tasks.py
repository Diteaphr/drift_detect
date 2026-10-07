"""End-to-end tests that the pipeline actually runs each task type.

The unit tests in test_task.py cover the abstraction in isolation; these drive
``ConceptDriftPipeline.run_stream`` so a wiring mistake (wrong backend chosen,
error signal left on the classification branch, ECPF never told the task) is
caught rather than only showing up as a strange number in an experiment.

Streams are kept small so the file stays fast; they are not meant to produce
meaningful detection quality.
"""

import numpy as np
import pytest

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline
from src.task import TaskType

N = 900
WARM = 150
DRIFT_AT = 500


def _features(n=N, seed=0):
    return np.random.default_rng(seed).uniform(0.0, 10.0, size=(n, 3))


def _score(X, before: bool):
    return (2.0 * X[:, 0] + X[:, 1]) if before else (-1.0 * X[:, 1] + 2.5 * X[:, 2])


def _classification_stream(k: int, seed=0):
    X = _features(seed=seed)
    s = np.where(np.arange(len(X)) < DRIFT_AT, _score(X, True), _score(X, False))
    cuts = np.quantile(s, np.linspace(0, 1, k + 1)[1:-1])
    return X, np.digitize(s, cuts).astype(int)


def _regression_stream(seed=0):
    X = _features(seed=seed)
    rng = np.random.default_rng(seed + 1)
    y = np.where(np.arange(len(X)) < DRIFT_AT, _score(X, True), _score(X, False))
    return X, y + rng.normal(0.0, 0.5, size=len(X))


def _run(X, y, **cfg_kwargs):
    cfg = PipelineConfig(use_ecpf=True, ecpf_signal_mode="dual_adwin", **cfg_kwargs)
    pipe = ConceptDriftPipeline(cfg)
    preds = [yp for _, _, yp, _, _ in pipe.run_stream(X, y, warm_start_samples=WARM)]
    return pipe, preds


# ---------------------------------------------------------------------------
# Task binding
# ---------------------------------------------------------------------------
def test_binary_stream_binds_to_binary_and_keeps_the_classifier():
    X, y = _classification_stream(2)
    pipe, preds = _run(X, y, model_type="ht")
    assert pipe.task.task_type is TaskType.BINARY
    assert pipe._resolved_model_type == "ht"
    assert len(preds) == N - WARM


def test_three_class_stream_binds_to_multiclass_and_predicts_every_class():
    X, y = _classification_stream(3)
    pipe, preds = _run(X, y, model_type="ht")
    assert pipe.task.task_type is TaskType.MULTICLASS
    assert pipe.task.n_classes == 3
    # A binary-only backend would silently cap itself at two labels; 'ht' must not.
    assert len(set(int(round(p)) for p in preds)) >= 3


def test_regression_stream_binds_to_regression_and_swaps_in_a_regressor():
    X, y = _regression_stream()
    pipe, preds = _run(X, y, model_type="ht")  # a classifier: must be replaced
    assert pipe.task.task_type is TaskType.REGRESSION
    assert pipe._resolved_model_type == "htr"
    # Continuous predictions, not a handful of class labels.
    assert len(set(np.round(preds, 6))) > N / 10


def test_regression_error_signal_stays_inside_the_unit_interval():
    """ADWIN/SEED/SeqDrift2 assume a bounded stream; an unbounded residual breaks them."""
    X, y = _regression_stream()
    pipe, _ = _run(X, y, model_type="htr")
    errs = pipe.buffer.get_errors()
    assert errs.size > 0
    assert errs.min() >= 0.0 and errs.max() <= 1.0
    # ...and it must not be pinned at a constant, which would read as "no drift ever".
    assert len(np.unique(np.round(errs, 6))) > 50


def test_classification_error_signal_is_still_exactly_zero_one():
    X, y = _classification_stream(3)
    pipe, _ = _run(X, y, model_type="ht")
    assert set(np.unique(pipe.buffer.get_errors())) <= {0.0, 1.0}


# ---------------------------------------------------------------------------
# Loud failures instead of silent wrongness
# ---------------------------------------------------------------------------
def test_regressor_on_a_classification_stream_raises():
    X, y = _classification_stream(3)
    with pytest.raises(ValueError, match="regressor"):
        _run(X, y, model_type="htr")


def test_binary_only_backend_rejects_a_multiclass_stream():
    """'elastic' used to complete silently, capped at two labels (measured acc 0.640)."""
    X, y = _classification_stream(3)
    with pytest.raises(ValueError):
        _run(X, y, model_type="elastic")


def test_binomial_detector_on_a_regression_stream_raises():
    X, y = _regression_stream()
    with pytest.raises(ValueError, match="Bernoulli"):
        _run(X, y, model_type="htr", selected_detectors=["adwin", "ddm"])


def test_uq_warning_mode_is_rejected_for_regression():
    """It reduces a probability matrix, which a continuous target has no analogue of."""
    X, y = _regression_stream()
    cfg = PipelineConfig(use_ecpf=True, ecpf_signal_mode="uq_warning", model_type="htr")
    pipe = ConceptDriftPipeline(cfg)
    with pytest.raises(ValueError, match="probability matrix"):
        list(pipe.run_stream(X, y, warm_start_samples=WARM))


def test_probability_based_uq_signal_is_rejected_for_regression():
    X, y = _regression_stream()
    with pytest.raises(ValueError, match="no regression analogue"):
        _run(X, y, model_type="hfr", ecpf_warning_signal="uq_mi")


# ---------------------------------------------------------------------------
# Regression UQ path
# ---------------------------------------------------------------------------
def test_regression_variance_uq_signal_is_live():
    """hfr exposes predict_per_model; the variance must vary, not sit at a constant."""
    X, y = _regression_stream()
    pipe, _ = _run(X, y, model_type="hfr", ecpf_warning_signal="uq_variance")
    assert pipe.task.is_regression
    assert pipe._uq_normalizer.n > 0
    assert pipe._uq_normalizer.std > 0.0


# ---------------------------------------------------------------------------
# The warm_start + step entry point must bind the task too
# ---------------------------------------------------------------------------
def _run_via_step(X, y, **cfg_kwargs):
    """Drive the pipeline the way test_integration.py does, bypassing run_stream."""
    cfg = PipelineConfig(use_ecpf=True, ecpf_signal_mode="dual_adwin", **cfg_kwargs)
    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[:WARM], y[:WARM])
    preds = [pipe.step(X[i], y[i], index=i)[0] for i in range(WARM, len(y))]
    return pipe, preds


def test_step_entry_point_binds_the_task_for_multiclass():
    """warm_start+step is public; without binding there, the task layer no-ops."""
    X, y = _classification_stream(3)
    pipe, preds = _run_via_step(X, y, model_type="linear")
    assert pipe.task.task_type is TaskType.MULTICLASS
    assert len(set(int(round(p)) for p in preds)) >= 3


def test_step_entry_point_binds_the_task_for_regression():
    """Otherwise a continuous target would be scored with the classification loss."""
    X, y = _regression_stream()
    pipe, _ = _run_via_step(X, y, model_type="ht")
    assert pipe.task.task_type is TaskType.REGRESSION
    assert pipe._resolved_model_type == "htr"
    errs = pipe.buffer.get_errors()
    assert len(np.unique(np.round(errs, 6))) > 50


def test_run_stream_overrides_a_provisional_warm_start_binding():
    """The warm-up batch can miss a class; the full target array must win."""
    X, y = _classification_stream(3)
    cfg = PipelineConfig(use_ecpf=True, ecpf_signal_mode="dual_adwin", model_type="ht")
    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[:WARM], y[:WARM])
    assert pipe._task_provisional
    list(pipe.run_stream(X, y, warm_start_samples=WARM))
    assert not pipe._task_provisional
    assert pipe.task.n_classes == 3


def test_uq_warning_mode_rejects_a_backend_without_a_probability_matrix():
    X, y = _classification_stream(2)
    cfg = PipelineConfig(use_ecpf=True, ecpf_signal_mode="uq_warning", model_type="linear")
    pipe = ConceptDriftPipeline(cfg)
    with pytest.raises(ValueError, match="does not expose"):
        list(pipe.run_stream(X, y, warm_start_samples=WARM))


def test_ecpf_receives_the_same_task_object_the_pipeline_scores_with():
    """ECPF only transforms; if it held a different spec its scores would sit at 0.5."""
    X, y = _regression_stream()
    pipe, _ = _run(X, y, model_type="htr")
    assert pipe._ecpf is not None
    assert pipe._ecpf.task is pipe.task
