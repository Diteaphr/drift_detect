"""Task-type abstraction: one place that knows whether a stream is classification
or regression, and what "prediction error" means for it.

Motivation
----------
Every drift detector in this project consumes a scalar error signal, and the
contract ``detectors/meta/base.py`` documents for it ("1.0 for misclassification,
0.0 for correct") is a *classification* contract.  Three things have to change
together when the target stops being a binary label:

1. **The loss.**  A 0-1 loss on a continuous target is ~always 1.0 (exact float
   equality never holds), which carries no information.  An absolute residual is
   informative but unbounded, and ADWIN/SEED/SeqDrift2 assume a bounded signal
   while DDM/RDDM/HDDM_W/EDDM assume a Bernoulli one.
2. **The uncertainty scalar.**  ``mi_like`` / ``predictive_entropy`` /
   ``vote_disagreement`` all need a probability simplex.  Only ``variance_eu``
   (cross-model variance) has a regression analogue.
3. **ECPF conceptual equivalence.**  The paper's error-bitset XOR has no
   meaning without a notion of "wrong".

Rather than sprinkle ``if regression:`` through the pipeline, callers ask a
:class:`TaskSpec` for the right behaviour.

Detector compatibility
----------------------
Under regression the binomial-bound detectors are not merely inaccurate, they are
invalid: DDM's ``sqrt(p*(1-p)/n)`` needs ``p`` to be a Bernoulli rate.  Use
:func:`incompatible_detectors` to reject them loudly instead of silently
producing numbers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Sequence

import numpy as np

from .preprocessing import zero_one_loss


class TaskType(str, Enum):
    BINARY = "binary"
    MULTICLASS = "multiclass"
    REGRESSION = "regression"


#: Detectors whose statistics assume a Bernoulli (0/1) error stream.
BINOMIAL_DETECTORS = frozenset({"ddm", "rddm", "hddm_w", "eddm", "ecdd", "stepd"})

#: Detectors that accept any bounded real-valued stream.
REAL_VALUED_DETECTORS = frozenset({"adwin", "hddm_a", "page_hinkley", "kswin", "seed", "seqdrift2"})


def incompatible_detectors(task_type: "TaskType", names: Sequence[str]) -> List[str]:
    """Names in *names* that cannot validly consume this task's error stream."""
    if task_type is not TaskType.REGRESSION:
        return []
    return [n for n in names if n in BINOMIAL_DETECTORS]


class ErrorNormalizer:
    """Map an unbounded non-negative residual stream into [0, 1] online.

    Follows the recipe River uses for ``ARFRegressor``: assume the monitored
    deviation is roughly normal and treat ``mean ± 3*sigma`` as its support, so
    a stable concept sits near 0.5 and a rising error climbs toward 1.0.  Mean
    and variance are tracked with Welford's algorithm (numerically stable, O(1)).

    Bounding matters for more than tidiness: SEED and SeqDrift2 multiply their
    Hoeffding/Bernstein bounds by a ``value_range`` that defaults to 1.0, and
    ADWIN's guarantees assume a bounded input.
    """

    __slots__ = ("_n", "_mean", "_m2", "warmup")

    def __init__(self, warmup: int = 30) -> None:
        self._n = 0
        self._mean = 0.0
        self._m2 = 0.0
        self.warmup = int(warmup)

    def reset(self) -> None:
        """Forget the running statistics (prescription 3: re-baseline per era)."""
        self._n = 0
        self._mean = 0.0
        self._m2 = 0.0

    def update(self, value: float) -> float:
        """Observe *value*, then return its normalized position in [0, 1]."""
        v = float(value)
        self._n += 1
        delta = v - self._mean
        self._mean += delta / self._n
        self._m2 += delta * (v - self._mean)
        return self.transform(v)

    def transform(self, value: float) -> float:
        """Normalize without updating the running statistics."""
        if self._n < self.warmup:
            # Not enough evidence to place the value yet; 0.5 is the neutral
            # position and keeps the early stream from looking like a drift.
            return 0.5
        sigma = math.sqrt(self._m2 / self._n) if self._n > 1 else 0.0
        if sigma <= 0.0:
            return 0.5
        lo = self._mean - 3.0 * sigma
        z = (float(value) - lo) / (6.0 * sigma)
        return min(1.0, max(0.0, z))

    def frozen(self) -> "FrozenNormalizer":
        """Read-only view whose ``update`` transforms without advancing the stats.

        Lets several consumers of the same per-instance value share one scale
        while the running mean/variance move exactly once per instance. Without
        it, a warning signal and a drift signal derived from the same quantity
        would be normalized against different denominators.
        """
        return FrozenNormalizer(self)

    @property
    def mean(self) -> float:
        return self._mean

    @property
    def std(self) -> float:
        return math.sqrt(self._m2 / self._n) if self._n > 1 else 0.0

    @property
    def n(self) -> int:
        return self._n


class FrozenNormalizer:
    """Non-advancing view of an :class:`ErrorNormalizer` (see ``ErrorNormalizer.frozen``)."""

    __slots__ = ("_inner",)

    def __init__(self, inner: ErrorNormalizer) -> None:
        self._inner = inner

    def update(self, value: float) -> float:
        return self._inner.transform(value)

    def transform(self, value: float) -> float:
        return self._inner.transform(value)


@dataclass
class TaskSpec:
    """What kind of stream this is, and the error semantics that follow from it.

    ``loss`` is stateful for regression (the normalizer adapts online), so a
    TaskSpec belongs to one pipeline run and must not be shared across runs.
    """

    task_type: TaskType
    n_classes: Optional[int] = None
    classes: Optional[np.ndarray] = None
    normalizer: ErrorNormalizer = field(default_factory=ErrorNormalizer)

    # ------------------------------------------------------------------
    @property
    def is_classification(self) -> bool:
        return self.task_type in (TaskType.BINARY, TaskType.MULTICLASS)

    @property
    def is_regression(self) -> bool:
        return self.task_type is TaskType.REGRESSION

    # ------------------------------------------------------------------
    def loss(self, y_true: Any, y_pred: Any) -> float:
        """Per-instance error in [0, 1], honouring the detector contract.

        Classification: the 0-1 loss, bit-identical to what the binary pipeline
        produced.  Regression: the absolute residual, normalized online.
        """
        if self.is_classification:
            return zero_one_loss(y_true, y_pred)
        return self.normalizer.update(abs(float(y_true) - float(y_pred)))

    def raw_residual(self, y_true: Any, y_pred: Any) -> float:
        """Unnormalized error — for reporting and for regression similarity."""
        if self.is_classification:
            return zero_one_loss(y_true, y_pred)
        return abs(float(y_true) - float(y_pred))

    # ------------------------------------------------------------------
    def describe(self) -> str:
        if self.is_regression:
            return "regression (continuous target)"
        return "%s (K=%s)" % (self.task_type.value, self.n_classes)


# ----------------------------------------------------------------------
# Auto-detection
# ----------------------------------------------------------------------
def infer_task(
    y: np.ndarray,
    *,
    max_classes: int = 50,
) -> TaskSpec:
    """Infer the task type from a target array.

    A target is treated as regression when it is non-integral, or when it takes
    on more distinct values than any plausible label set (*max_classes*).  A
    binary target stored as floats (0.0/1.0) is still classification — only the
    cardinality and integrality matter, not the dtype.
    """
    arr = np.asarray(y).ravel()
    if arr.size == 0:
        raise ValueError("cannot infer a task type from an empty target array")

    # Non-numeric targets (string labels) are categorical by construction.
    if arr.dtype.kind in ("U", "S", "O"):
        uniq = np.unique(arr)
        return TaskSpec(
            task_type=TaskType.BINARY if len(uniq) == 2 else TaskType.MULTICLASS,
            n_classes=int(len(uniq)),
            classes=uniq,
        )

    finite = arr[np.isfinite(arr.astype(np.float64))]
    if finite.size == 0:
        raise ValueError("target array contains no finite values")

    integral = bool(np.all(np.equal(np.mod(finite, 1.0), 0.0)))
    uniq = np.unique(finite)

    if not integral or len(uniq) > max_classes:
        return TaskSpec(task_type=TaskType.REGRESSION)

    return TaskSpec(
        task_type=TaskType.BINARY if len(uniq) == 2 else TaskType.MULTICLASS,
        n_classes=int(len(uniq)),
        classes=uniq.astype(int),
    )


def resolve_task(
    y: np.ndarray,
    *,
    declared: Optional[TaskType] = None,
    n_classes: Optional[int] = None,
) -> TaskSpec:
    """Infer the task, but let an explicit config declaration win.

    Raises when the declaration contradicts the data — a silently mis-declared
    task is exactly the failure mode this module exists to prevent.
    """
    spec = infer_task(y)
    if declared is None:
        if n_classes is not None and spec.is_classification:
            spec.n_classes = int(n_classes)
        return spec

    declared = TaskType(declared)
    if declared is not spec.task_type:
        if declared is TaskType.REGRESSION and spec.is_classification:
            # Legitimate: an integer-valued target the user wants modelled
            # as a continuous quantity (counts, ratings).
            return TaskSpec(task_type=TaskType.REGRESSION)
        raise ValueError(
            "task_type=%r was declared but the target looks like %s; "
            "refusing to guess. Fix the data or the config."
            % (declared.value, spec.describe())
        )
    if n_classes is not None and spec.is_classification:
        spec.n_classes = int(n_classes)
    return spec
