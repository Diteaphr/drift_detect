"""Unit tests for the task-type abstraction in ``src/task.py``.

Two properties matter most here: that a binary stream is still routed to the
exact 0-1 loss the pipeline used before (so published binary results hold), and
that a continuous target is never silently mistaken for a 1200-class
classification problem — which is what the pipeline did before this module.
"""

import numpy as np

from src.preprocessing import zero_one_loss
from src.task import (
    BINOMIAL_DETECTORS,
    ErrorNormalizer,
    TaskSpec,
    TaskType,
    incompatible_detectors,
    infer_task,
    resolve_task,
)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------
def test_binary_int_labels_detected_as_binary():
    spec = infer_task(np.array([0, 1, 1, 0, 1]))
    assert spec.task_type is TaskType.BINARY
    assert spec.n_classes == 2
    assert spec.is_classification and not spec.is_regression


def test_binary_labels_stored_as_floats_are_still_classification():
    """dtype must not decide the task — cardinality and integrality do."""
    spec = infer_task(np.array([0.0, 1.0, 1.0, 0.0]))
    assert spec.task_type is TaskType.BINARY


def test_three_distinct_int_labels_detected_as_multiclass():
    spec = infer_task(np.array([0, 1, 2, 2, 1, 0]))
    assert spec.task_type is TaskType.MULTICLASS
    assert spec.n_classes == 3


def test_continuous_target_detected_as_regression():
    rng = np.random.default_rng(0)
    spec = infer_task(rng.normal(size=500))
    assert spec.task_type is TaskType.REGRESSION
    assert spec.is_regression and not spec.is_classification


def test_many_distinct_integers_are_regression_not_a_huge_class_set():
    """Before src/task.py the pipeline treated 1200 distinct targets as 1200 classes."""
    spec = infer_task(np.arange(500))
    assert spec.task_type is TaskType.REGRESSION


def test_string_labels_are_classification():
    spec = infer_task(np.array(["cat", "dog", "fox", "cat"]))
    assert spec.task_type is TaskType.MULTICLASS
    assert spec.n_classes == 3


def test_empty_target_is_rejected():
    try:
        infer_task(np.array([]))
    except ValueError:
        return
    raise AssertionError("expected ValueError on an empty target array")


# ---------------------------------------------------------------------------
# Declaration vs inference
# ---------------------------------------------------------------------------
def test_declaring_regression_over_integer_target_is_allowed():
    """Counts/ratings are a legitimate continuous modelling choice."""
    spec = resolve_task(np.array([1, 2, 3, 4, 5]), declared=TaskType.REGRESSION)
    assert spec.is_regression


def test_declaring_classification_over_continuous_target_raises():
    rng = np.random.default_rng(1)
    try:
        resolve_task(rng.normal(size=200), declared=TaskType.MULTICLASS)
    except ValueError as exc:
        assert "refusing to guess" in str(exc)
        return
    raise AssertionError("expected ValueError on a contradicted declaration")


# ---------------------------------------------------------------------------
# Loss semantics
# ---------------------------------------------------------------------------
def test_classification_loss_is_exactly_the_zero_one_loss():
    spec = infer_task(np.array([0, 1]))
    for y in range(4):
        for p in range(4):
            assert spec.loss(y, p) == zero_one_loss(y, p)


def test_regression_loss_is_bounded_in_unit_interval():
    rng = np.random.default_rng(2)
    spec = TaskSpec(task_type=TaskType.REGRESSION)
    vals = [spec.loss(a, b) for a, b in rng.normal(size=(400, 2)) * 10]
    assert all(0.0 <= v <= 1.0 for v in vals)


def test_regression_loss_rises_when_the_residual_grows():
    """A drift that inflates the residual must push the normalized signal up."""
    rng = np.random.default_rng(3)
    spec = TaskSpec(task_type=TaskType.REGRESSION)
    calm = [spec.loss(0.0, rng.normal(0, 1)) for _ in range(300)]
    shifted = [spec.loss(0.0, rng.normal(0, 1) + 8.0) for _ in range(60)]
    assert np.mean(shifted) > np.mean(calm)


def test_raw_residual_keeps_the_magnitude():
    spec = TaskSpec(task_type=TaskType.REGRESSION)
    assert spec.raw_residual(10.0, 4.0) == 6.0


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------
def test_normalizer_is_neutral_before_warmup():
    norm = ErrorNormalizer(warmup=30)
    assert norm.update(123.0) == 0.5


def test_normalizer_tracks_mean_and_std():
    rng = np.random.default_rng(4)
    xs = rng.normal(5.0, 2.0, size=5000)
    norm = ErrorNormalizer(warmup=10)
    for x in xs:
        norm.update(x)
    assert abs(norm.mean - float(np.mean(xs))) < 1e-9
    assert abs(norm.std - float(np.std(xs))) < 1e-9


# ---------------------------------------------------------------------------
# Detector compatibility
# ---------------------------------------------------------------------------
def test_binomial_detectors_are_rejected_for_regression():
    bad = incompatible_detectors(TaskType.REGRESSION, ["adwin", "ddm", "hddm_w", "page_hinkley"])
    assert set(bad) == {"ddm", "hddm_w"}
    assert set(bad) <= BINOMIAL_DETECTORS


def test_no_detector_is_rejected_for_classification():
    names = ["adwin", "ddm", "hddm_w", "rddm", "page_hinkley"]
    assert incompatible_detectors(TaskType.BINARY, names) == []
    assert incompatible_detectors(TaskType.MULTICLASS, names) == []
