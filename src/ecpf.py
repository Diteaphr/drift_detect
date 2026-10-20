"""
Enhanced Concept Profiling Framework (ECPF), Anderson et al. (TKDE).

Reference: paper Algorithm 1 / MOA ``ECPF.java`` (rand079/CPF).
Default hyperparameters match the paper's experiments: similarity m = 0.95,
fade points f = 15, model-check frequency = 1.

The pipeline can drive drift timing in two ways:

* ``oracle_60`` — synthetic protocol from the paper: enter WARNING at each
  *true* drift index ``T`` (user-supplied), accumulate exactly ``warning_length``
  instances (default 60), then run the ECPF drift handler on that buffer.
* ``meta_retro_60`` — when the meta-detector fires drift at ``T``, use the last
  ``warning_length`` ``(x, y)`` tuples ending at ``T`` as the warning buffer
  (approximates a fixed-length warning period without a separate warning signal).

Task awareness
--------------
The paper defines conceptual equivalence over an *error bitset*, which presumes
a notion of "wrong".  :class:`ECPFMetaLearner` therefore accepts an optional
:class:`~src.task.TaskSpec`; see :meth:`ECPFMetaLearner._pair_agreement` for the
two similarity metrics and :meth:`ECPFMetaLearner._profile_on_buffer` for the
"higher is better" score that replaces accuracy under regression.  Passing no
TaskSpec keeps the original classification behaviour byte for byte.

Optional extensions (off by default; defaults reproduce the paper exactly):

* ``swap_policy="hoeffding"`` (ARCUS / ARF-style reliability) — the shadow
  learner replaces the leader only when its accuracy advantage since the last
  drift exceeds a Hoeffding bound, instead of on a one-instance lead.
* ``fade_policy="reuse_value"`` (AiRStream-style memory valuation) — a stored
  expert earns fade points by the errors it saved when reused (reused copy vs.
  fresh learner over the first ``reuse_value_window`` post-drift instances),
  instead of +f merely for being the leader.
* Memory-aware variants of ``reuse_value`` (same gains, different costs or
  eviction order; slot sizes are measured with ``deep_sizeof`` in KB):

  - ``density``: evict by fade score per KB (non-positive scores first).
  - ``rent``: idle cost per drift = ``fade_lambda * kb / mean_kb``.
  - ``entry``: one-off fee ``fade_lambda * kb / mean_kb`` the first time a
    slot is stored, then the fixed ``reuse_idle_cost``.
  - ``freq``: evict by ``(reuses + 1) / (age + 2) * max(score, 0) / kb``.
  - ``decay``: idle scores shrink by ``decay_gamma`` each drift before the
    idle cost, so old credit fades.
  - ``subst``: reuse value is measured against the better of the fresh
    learner and the second-best stored expert (what is lost without it).

  ``memory_budget_factor > 0`` adds a pool cap in KB: total stored size
  <= factor x the current leader's size. ``pool_trace`` records the pool
  timeline, evictions, regret against recently evicted experts and the time
  spent in pool operations (observability only, no decision effect).
"""

from __future__ import annotations

import ast
import copy
import logging
import math
import pickle
import sys
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .task import TaskSpec

logger = logging.getLogger(__name__)


# deepcopy/pickle recurse once per tree level; deep River trees (e.g. a
# Hoeffding Forest on electricity) exceed Python's default limit of 1000.
_CLONE_RECURSION_LIMIT = 20_000

FADE_POLICIES = ("ecpf", "reuse_value", "density", "rent", "entry", "freq", "decay", "subst")
# Policies whose decisions read slot sizes.
_MEMORY_POLICIES = ("density", "rent", "entry", "freq")


def _deep_clone(obj: Any) -> Any:
    """Clone sklearn PredictionModel or River BaseModel via pickle when needed."""
    old_limit = sys.getrecursionlimit()
    if old_limit < _CLONE_RECURSION_LIMIT:
        sys.setrecursionlimit(_CLONE_RECURSION_LIMIT)
    try:
        try:
            return copy.deepcopy(obj)
        except Exception:
            return pickle.loads(pickle.dumps(obj))
    finally:
        sys.setrecursionlimit(old_limit)


def _label(value: float) -> int:
    """Round a model output (or a target) to the integer class label.

    Both prediction backends return a hard class label as a float, so this is a
    lossless cast; it exists so that label *comparison* and :func:`_wrong` use
    one and the same rounding rule.
    """
    return int(round(float(value)))


def _wrong(pred: float, y: float) -> bool:
    return _label(pred) != _label(y)


def _residual_similarity(res_i: np.ndarray, res_j: np.ndarray) -> float:
    """Behavioural similarity of two regression experts, in [0, 1].

    Parameters
    ----------
    res_i, res_j : np.ndarray
        *Signed* residual vectors ``y - y_hat`` over the same warning buffer.

    Returns
    -------
    float
        ``(r + 1) / 2`` where ``r`` is the Pearson correlation of the two
        residual vectors, so that 1.0 means "these two experts make the same
        mistake on the same instance in the same direction" and 0.5 means
        "uncorrelated".  The [0, 1] range is what makes the value comparable
        with ``similarity_margin`` at all.

    Notes
    -----
    Signed residuals are used, not absolute ones.  Two experts that are wrong by
    the same magnitude but in opposite directions represent genuinely different
    concepts (one over-predicts, one under-predicts); ``|r|`` on absolute
    residuals would score that pair 1.0 and merge them away, which is exactly the
    K > 2 failure mode this module is being fixed for, transplanted to regression.

    Zero variance makes Pearson undefined.  Identical residual vectors (both
    experts behaving the same, including the degenerate "both perfect" case) are
    reported as 1.0; any other constant vector returns the neutral 0.5, which
    sits below every sane ``similarity_margin`` and therefore never merges.
    Refusing to merge on undefined evidence is the safe direction: a redundant
    expert costs memory, a wrongly merged one destroys a recoverable concept.
    """
    if res_i.size == 0 or res_j.size == 0:
        return 0.5
    if np.allclose(res_i, res_j):
        return 1.0
    std_i = float(np.std(res_i))
    std_j = float(np.std(res_j))
    if std_i <= 0.0 or std_j <= 0.0:
        return 0.5
    cov = float(np.mean((res_i - res_i.mean()) * (res_j - res_j.mean())))
    r = cov / (std_i * std_j)
    if not np.isfinite(r):
        return 0.5
    r = min(1.0, max(-1.0, r))
    return (r + 1.0) / 2.0


@dataclass
class _SlotStats:
    """Lifetime score tracking for a stored expert (paper / MOA).

    ``n_correct`` is a *count* of correct predictions under classification and a
    sum of ``1 - normalized residual`` credits under regression, so it stays a
    "higher is better" quantity in both regimes but is only an accuracy numerator
    in the first.  It is typed ``float`` for that reason; the classification path
    only ever adds ``int``, so it stays an exact integer there.
    """

    n_inst: int = 0
    n_correct: float = 0


class ECPFMetaLearner:
    """
    ECPF model pool + duel between reused copy and new learner.

    Works with either ``PredictionModel`` (sklearn path) or ``BaseModelAdapter``
    (River / RF path). Archives are **frozen** snapshots; only ``current_idx``
    expert and ``new_model`` receive stream updates in IN_CONTROL.

    Parameters
    ----------
    similarity_margin : float, default 0.95
        Merge threshold on the pairwise similarity accumulated across drifts.
        The paper's 0.95 was calibrated for an *agreement rate* (a fraction of
        instances).  Under regression the accumulated quantity is a Pearson
        correlation remapped to [0, 1] — same range, different distribution:
        0.95 there means ``r >= 0.90``, and residual vectors of two experts
        drawn from the same pool are routinely correlated well above that
        simply because they see the same targets.  Recalibrate before trusting
        merge counts on a regression stream; do not read 0.95 as "the paper's
        value" once ``task`` is a regression spec.
    task : TaskSpec, optional
        Error semantics for the stream.  ``None`` (the default) means "the
        classification behaviour this class has always had" and is what every
        binary experiment in this repository runs with; the classification code
        path is unconditional and does not read this attribute except to decide
        whether the stream is a regression one.

    Notes
    -----
    Under regression the ``curr_correct`` / ``new_correct`` duel counters and
    every ``acc_*`` diagnostic stop being accuracies — see
    :meth:`_instance_credit` and :meth:`_profile_on_buffer`.
    """

    def __init__(
        self,
        *,
        similarity_margin: float = 0.95,
        fade_points: int = 15,
        model_check_freq: int = 1,
        fade_enabled: bool = True,
        max_pool_size: int = 10,
        use_advanced: bool = False,
        model_type: str = "linear",
        model_kwargs: Optional[Dict[str, Any]] = None,
        task: Optional[TaskSpec] = None,
        similarity_mode: str = "auto",
        swap_policy: str = "strict",
        swap_delta: float = 0.05,
        fade_policy: str = "ecpf",
        reuse_value_window: int = 500,
        reuse_idle_cost: float = 1.0,
        fade_lambda: float = 1.0,
        decay_gamma: float = 0.8,
        memory_budget_factor: float = 0.0,
        pool_trace: bool = False,
        ghost_archive_size: int = 20,
    ) -> None:
        self.task = task
        # Cached once: every hot-loop branch below asks only this question, and
        # a missing TaskSpec must be indistinguishable from a classification one.
        self._is_regression: bool = task is not None and task.is_regression
        # Ablation switch for the conceptual-equivalence definition.
        #   "auto" / "label_agreement": signatures are predicted labels, so a
        #       pair agrees when both predicted the SAME class (this repo's
        #       modification; provably identical to the paper at K = 2).
        #   "error_bitset": signatures are wrong-bits, reproducing the
        #       published ECPF/CPF definition where (wrong, wrong) counts as
        #       agreement even if the two experts chose different wrong classes.
        # Exists so the modification can be ablated against the original on
        # K > 2 streams rather than asserted.
        if similarity_mode not in ("auto", "label_agreement", "error_bitset"):
            raise ValueError(
                "similarity_mode must be 'auto', 'label_agreement' or "
                "'error_bitset', got %r" % (similarity_mode,)
            )
        if similarity_mode == "error_bitset" and self._is_regression:
            raise ValueError(
                "similarity_mode='error_bitset' is undefined for regression: "
                "there is no wrong-bit without a discrete label."
            )
        self.similarity_mode = similarity_mode
        self._use_bitset = similarity_mode == "error_bitset"
        if swap_policy not in ("strict", "hoeffding"):
            raise ValueError(f"unknown swap_policy: {swap_policy!r}")
        if fade_policy not in FADE_POLICIES:
            raise ValueError(f"unknown fade_policy: {fade_policy!r}")
        self.swap_policy = swap_policy
        self.swap_delta = float(swap_delta)
        self.fade_policy = fade_policy
        self.reuse_value_window = max(1, int(reuse_value_window))
        self.reuse_idle_cost = float(reuse_idle_cost)
        self.fade_lambda = float(fade_lambda)
        self.decay_gamma = float(decay_gamma)
        self.memory_budget_factor = float(memory_budget_factor)
        self.pool_trace = bool(pool_trace)
        # Sizes are only measured when a decision or the trace needs them, so
        # the default configuration does no extra work.
        self._track_sizes = (
            fade_policy in _MEMORY_POLICIES or self.memory_budget_factor > 0 or self.pool_trace
        )
        self.similarity_margin = float(similarity_margin)
        self.fade_points = int(fade_points)
        self.model_check_freq = int(model_check_freq)
        self.fade_enabled = bool(fade_enabled)
        self.max_pool_size = max(1, int(max_pool_size))
        self.use_advanced = bool(use_advanced)
        self.model_type = model_type
        self.model_kwargs = dict(model_kwargs or {})

        # Collection: None = removed slot
        self.slots: List[Optional[Any]] = []
        self.slot_stats: List[_SlotStats] = []
        # cumulative (seen, agreed) for conceptual equivalence (paper §3.1).
        # ``_pair_agreed`` holds an integer instance count under classification
        # and a similarity-weighted pseudo-count under regression, so that the
        # ``agreed / seen`` ratio consumed by ``_merge_models`` keeps meaning
        # "average similarity over every warning buffer seen so far".
        self._pair_seen: Dict[Tuple[int, int], int] = {}
        self._pair_agreed: Dict[Tuple[int, int], float] = {}
        self.fade_scores: Dict[int, int] = {}

        self.current_idx: int = 0
        self.new_model: Optional[Any] = None

        self.curr_correct = 0
        self.new_correct = 0
        self.total_inst = 0

        self.num_drifts = 0
        self.model_reuses = 0
        self.model_merges = 0
        self.leader_swaps = 0  # stage-4: lifetime count of post-drift duel leader swaps

        # Ablation bookkeeping (observability only, no decision effect):
        # which (kept, removed) pairs each on_drift merged, and the drift era
        # whose data each slot currently represents (era k = the stretch
        # between confirmed drift k and k+1; era 0 = warm start to first
        # drift). A harness can map eras to ground-truth concepts and count
        # cross-concept merges.
        self.last_merge_pairs: List[Tuple[int, int]] = []
        self.slot_eras: Dict[int, int] = {}

        # Reuse-value bookkeeping (fade_policy="reuse_value"). ``_reuse_source``
        # is the stored slot whose copy became leader at the last drift; the
        # leader/shadow roles flip on every swap, so track which one is the
        # reused copy to attribute per-instance correctness.
        self._reuse_source: Optional[int] = None
        self._leader_is_reused = True
        self._rv_reused_correct = 0
        self._rv_fresh_correct = 0
        self._rv_n = 0
        self.reuse_value_log: List[Dict[str, Any]] = []
        # ``subst``: copy of the second-best stored expert, run beside the
        # fresh learner over the reuse-value window.
        self._rv_alt: Optional[Any] = None
        self._rv_alt_correct = 0
        self._rv_has_alt = False

        # Memory / lifetime bookkeeping per slot.
        self.slot_kb: Dict[int, float] = {}
        self._slot_birth: Dict[int, int] = {}
        self._slot_reuses: Dict[int, int] = {}
        self._slot_rv_sum: Dict[int, float] = {}
        self._entry_paid: set = set()

        # Pool trace (pool_trace=True). ``clock`` is the stream index, set by
        # the pipeline every step.
        self.clock: int = 0
        self.pool_timeline: List[Tuple[int, int, float]] = []
        self.eviction_log: List[Dict[str, Any]] = []
        self.regret_log: List[Dict[str, Any]] = []
        self._ghosts: deque = deque(maxlen=max(1, int(ghost_archive_size)))
        self.pool_time_s = 0.0
        self.sizing_time_s = 0.0
        self.trace_time_s = 0.0

    # ------------------------------------------------------------------
    # Memory bookkeeping
    # ------------------------------------------------------------------
    def _measure_slot(self, idx: int) -> None:
        """Size of the stored expert's model in KB.

        Only the estimator is measured: a frozen ``BaseModelAdapter`` also
        carries a copy of the live adapter's ``data_buffer`` (recent samples,
        ~1 MB at the default 1000 rows), which reuse never reads and which is
        the same for every slot, so counting it would hide the size
        differences the memory-aware policies act on.
        """
        if not self._track_sizes or self.slots[idx] is None:
            return
        from .metrics.run_cost import deep_sizeof

        t0 = time.perf_counter()
        slot = self.slots[idx]
        model = slot.get_model() if hasattr(slot, "get_model") else slot
        self.slot_kb[idx] = deep_sizeof(model) / 1024.0
        self.sizing_time_s += time.perf_counter() - t0

    def _alive(self) -> List[int]:
        return [i for i, s in enumerate(self.slots) if s is not None]

    def pool_kb(self) -> float:
        return float(sum(self.slot_kb.get(i, 0.0) for i in self._alive()))

    def _mean_kb(self) -> float:
        alive = self._alive()
        if not alive:
            return 1.0
        m = sum(self.slot_kb.get(i, 0.0) for i in alive) / len(alive)
        return m if m > 0 else 1.0

    def _record_timeline(self) -> None:
        if self.pool_trace:
            self.pool_timeline.append((int(self.clock), len(self._alive()), round(self.pool_kb(), 3)))

    def _evict(self, idx: int, reason: str) -> None:
        """Remove a slot (fade, cap or memory budget) and log it."""
        if self.pool_trace:
            self.eviction_log.append({
                "t": int(self.clock),
                "drift": int(self.num_drifts),
                "slot": int(idx),
                "reason": reason,
                "score": float(self.fade_scores.get(idx, 0)),
                "kb": round(float(self.slot_kb.get(idx, 0.0)), 3),
                "age_drifts": int(self.num_drifts - self._slot_birth.get(idx, 0)),
                "reuses": int(self._slot_reuses.get(idx, 0)),
                "rv_sum": float(self._slot_rv_sum.get(idx, 0.0)),
                "era": int(self.slot_eras.get(idx, -1)),
            })
            self._ghosts.append((int(idx), int(self.slot_eras.get(idx, -1)), self.slots[idx]))
        self._remove_slot(idx)
        self.fade_scores.pop(idx, None)

    def _eviction_key(self, idx: int) -> Tuple[float, ...]:
        """Lower key = evicted first (cap and memory budget)."""
        score = float(self.fade_scores.get(idx, 0))
        if self.fade_policy in ("density", "freq"):
            kb = max(self.slot_kb.get(idx, 0.0), 1e-6)
            if score <= 0:
                return (0.0, score)
            if self.fade_policy == "density":
                return (1.0, score / kb)
            age = self.num_drifts - self._slot_birth.get(idx, 0)
            p_reuse = (self._slot_reuses.get(idx, 0) + 1) / (age + 2)
            return (1.0, p_reuse * score / kb)
        return (score,)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def bootstrap_first_expert(self, prediction_model: Any) -> None:
        """Call after initial warm-start: archive the first working model."""
        self.slots = [_deep_clone(prediction_model)]
        self.slot_stats = [_SlotStats()]
        self.fade_scores = {0: self.fade_points}
        self.slot_eras = {0: 0}
        self.slot_kb = {}
        self._slot_birth = {0: self.num_drifts}
        self._slot_reuses = {}
        self._slot_rv_sum = {}
        self._entry_paid = set()
        self._measure_slot(0)
        self._record_timeline()
        self.current_idx = 0
        self.new_model = None
        self.curr_correct = 0
        self.new_correct = 0
        self.total_inst = 0

    def _predict_one(self, model: Any, x: np.ndarray) -> float:
        x = np.asarray(x, dtype=np.float64).ravel()
        if self.use_advanced:
            return float(model.predict_one(x.reshape(1, -1)))
        return float(model.predict(x.reshape(1, -1))[0])

    def _train_one(self, model: Any, x: np.ndarray, y: float) -> None:
        x = np.asarray(x, dtype=np.float64).ravel()
        if self.use_advanced:
            model.learn_one(x.reshape(1, -1), y)
            return
        model.fine_tune(x.reshape(1, -1), np.array([y], dtype=float))

    def _fit_on_buffer(self, model: Any, buffer: List[Tuple[np.ndarray, float]]) -> None:
        if not buffer:
            return
        X = np.stack([np.asarray(a, dtype=np.float64).ravel() for a, _ in buffer], axis=0)
        y = np.array([float(b) for _, b in buffer], dtype=float)
        if self.use_advanced:
            model.fit(X, y)
        else:
            model.fit(X, y)

    def leader_predict(self, prediction_model: Any, x: np.ndarray) -> float:
        """Predict with the current leading expert (must match ``prediction_model`` state)."""
        return self._predict_one(prediction_model, x)

    # ------------------------------------------------------------------
    # Task-dependent scoring
    # ------------------------------------------------------------------
    def _instance_credit(self, pred: float, y_true: float) -> float:
        """Per-instance "higher is better" credit for the duel counters.

        Classification returns the literal ``int`` 1 or 0, so ``curr_correct``
        and ``new_correct`` stay exact integer hit counts and every existing
        consumer (``tracing.py`` casts them with ``int()``) is unaffected.

        Regression returns ``1 - normalized_residual`` in [0, 1], which is a
        *negated normalized error*, not an accuracy: 1.0 is a perfect fit and
        0.5 is the neutral position of :class:`~src.task.ErrorNormalizer` before
        it has enough evidence to place a residual.  ``_compare_classifiers``
        only needs the ordering, and this preserves it.

        The normalizer is read with ``transform``, never ``update``: the running
        mean/variance belongs to the pipeline's on-stream error channel, and
        letting off-stream evaluations of archived experts feed into it would
        move the detector's own input distribution.
        """
        if self._is_regression:
            resid = self.task.raw_residual(y_true, pred)
            return 1.0 - self.task.normalizer.transform(resid)
        return 0 if _wrong(pred, y_true) else 1

    def _profile_on_buffer(
        self,
        model: Any,
        buffer: List[Tuple[np.ndarray, float]],
    ) -> Tuple[np.ndarray, float]:
        """Behavioural signature and buffer score of one expert.

        Returns
        -------
        signature : np.ndarray
            Classification: the predicted **class labels**, one per buffer slot.
            Regression: the **signed residuals** ``y - y_hat``.  This is the
            vector :meth:`_pair_agreement` compares between two experts.
        score : float
            Classification: accuracy on the buffer, computed as
            ``correct / len(buffer)`` — the exact expression used before this
            method existed, so the reported floats are unchanged bit for bit.
            Regression: ``1 - mean(normalized residual)``, i.e. **not** an
            accuracy, only an ordering-compatible goodness in [0, 1].

        Notes
        -----
        The signature is the whole point of the refactor.  ECPF's published
        similarity is a *wrong-bitset* XOR, and XOR scores (wrong, wrong) as
        agreement.  With K = 2 that is harmless, because "both wrong" on a
        two-valued label forces both experts onto the same other label, so
        error-agreement and prediction-agreement are the same event.  With
        K > 2 the two decouple: two experts wrong in different directions are
        counted as conceptually equivalent, ``agreed / seen`` is inflated, and
        ``_merge_models`` deletes concepts that behave differently.  The failure
        peaks on a post-drift buffer, where accuracy is low and the "both wrong"
        cell holds most of the mass.
        """
        n = len(buffer)
        if self._is_regression:
            resid = np.zeros(n, dtype=np.float64)
            err_sum = 0.0
            for t, (xv, yv) in enumerate(buffer):
                pred = self._predict_one(model, xv)
                resid[t] = float(yv) - pred
                err_sum += self.task.normalizer.transform(abs(resid[t]))
            return resid, (1.0 - err_sum / n) if n else 0.0

        labels = np.zeros(n, dtype=np.int64)
        correct = 0
        for t, (xv, yv) in enumerate(buffer):
            pred = self._predict_one(model, xv)
            if self._use_bitset:
                # Ablation arm: the signature is the WRONG-BIT, so the equality
                # count downstream reproduces the paper's XOR semantics exactly
                # -- (wrong, wrong) agrees regardless of which wrong class.
                labels[t] = 1 if _wrong(pred, yv) else 0
            else:
                labels[t] = _label(pred)
            if not _wrong(pred, yv):
                correct += 1
        return labels, (correct / n if n else 0.0)

    def _pair_agreement(self, sig_i: np.ndarray, sig_j: np.ndarray) -> float:
        """Similarity mass contributed by one warning buffer to a pair of experts.

        The return value is on the same scale as ``len(buffer)`` so that
        ``_pair_agreed / _pair_seen`` stays a per-instance similarity in [0, 1]
        and ``_merge_models`` needs no change.

        Classification counts instances where the two experts predicted the
        **same label**.  On binary data this equals the previous
        ``len(buffer) - xor(wrong_i, wrong_j).sum()`` for every buffer: fix an
        instance with label ``y`` and predictions ``p_i, p_j`` drawn from the
        same two-element label set, then ``(p_i != y) == (p_j != y)`` holds iff
        both are ``y`` or both are the other label — that is, iff
        ``p_i == p_j``.  Both prediction backends are classifiers that only ever
        emit a label seen in training, so the two-element premise holds for every
        binary dataset in ``data/`` and the published numbers are untouched.

        Regression converts a correlation-based similarity into the same
        per-buffer mass by weighting it with the buffer length.
        """
        if self._is_regression:
            return _residual_similarity(sig_i, sig_j) * float(sig_i.size)
        return int(np.count_nonzero(sig_i == sig_j))

    def on_stream_instance(
        self,
        prediction_model: Any,
        x: np.ndarray,
        y_true: float,
        y_pred_leader: Optional[float] = None,
    ) -> None:
        """
        IN_CONTROL training: update leader and ``new_model`` if present; duel counters.
        ``prediction_model`` must be the active leader object (same reference as pipeline).

        ``curr_correct`` / ``new_correct`` accumulate :meth:`_instance_credit`,
        which is a hit count under classification and a sum of
        ``1 - normalized residual`` under regression — higher is better in both,
        an accuracy numerator only in the first.
        """
        if y_pred_leader is None:
            y_pred = self._predict_one(prediction_model, x)
        else:
            y_pred = float(y_pred_leader)
        leader_credit = self._instance_credit(y_pred, y_true)
        if self.new_model is not None:
            ny = self._predict_one(self.new_model, x)
            shadow_credit = self._instance_credit(ny, y_true)
            self.new_correct += shadow_credit
            if self._rv_n < self.reuse_value_window:
                reused, fresh = (
                    (leader_credit, shadow_credit)
                    if self._leader_is_reused
                    else (shadow_credit, leader_credit)
                )
                self._rv_reused_correct += reused
                self._rv_fresh_correct += fresh
                if self._rv_alt is not None:
                    self._rv_alt_correct += self._instance_credit(
                        self._predict_one(self._rv_alt, x), y_true
                    )
                    self._train_one(self._rv_alt, x, y_true)
                self._rv_n += 1
                if self._rv_n >= self.reuse_value_window:
                    self._rv_alt = None
        self.curr_correct += leader_credit
        self.total_inst += 1

        if self.total_inst % self.model_check_freq == 0:
            self._compare_classifiers(prediction_model)

        self._train_one(prediction_model, x, y_true)
        if self.new_model is not None:
            self._train_one(self.new_model, x, y_true)

    def _shadow_wins(self) -> bool:
        """Whether the shadow learner should replace the leader now.

        ``strict`` (paper): any lead in correct count since the last drift.
        ``hoeffding``: the mean of the paired per-instance difference
        d_t = 1[shadow ok] - 1[leader ok] (range R = 2) must exceed the
        Hoeffding bound eps = sqrt(R^2 ln(1/delta) / (2n)), i.e. the shadow is
        better with confidence 1 - delta rather than by chance.
        """
        if self.swap_policy == "strict":
            return self.curr_correct < self.new_correct
        n = self.total_inst
        if n <= 0:
            return False
        lead = (self.new_correct - self.curr_correct) / n
        eps = math.sqrt(2.0 * math.log(1.0 / self.swap_delta) / n)
        return lead > eps

    def _compare_classifiers(self, prediction_model: Any) -> None:
        """Swap leader if shadow ``new_model`` wins under ``swap_policy``."""
        if self.new_model is None:
            return
        if self._shadow_wins():
            self.curr_correct, self.new_correct = self.new_correct, self.curr_correct
            if self.use_advanced:
                tmp = prediction_model.get_model()
                prediction_model.set_model(self.new_model.get_model())
                self.new_model.set_model(tmp)
            else:
                m_a = prediction_model.get_model()
                sc_a = copy.deepcopy(prediction_model.scaler)
                fit_a = prediction_model._scaler_fitted
                m_b = self.new_model.get_model()
                sc_b = copy.deepcopy(self.new_model.scaler)
                fit_b = self.new_model._scaler_fitted
                prediction_model.set_model(m_b)
                prediction_model.scaler = sc_b
                prediction_model._scaler_fitted = fit_b
                self.new_model.set_model(m_a)
                self.new_model.scaler = sc_a
                self.new_model._scaler_fitted = fit_a
            self.slots[self.current_idx] = _deep_clone(prediction_model)
            self.slot_eras[self.current_idx] = self.num_drifts  # mid-era re-freeze
            self._measure_slot(self.current_idx)
            self._record_timeline()
            self.leader_swaps += 1
            self._leader_is_reused = not self._leader_is_reused
            logger.info("ECPF: swapped leader in favour of shadow learner")

    def on_drift(
        self,
        prediction_model: Any,
        buffer: List[Tuple[np.ndarray, float]],
    ) -> Dict[str, Any]:
        """
        Run ECPF steps 8–14 (paper): save leader, pick reuse, train new on buffer,
        merge by similarity, fade, clear counters.

        The ``acc_*`` entries of the returned dict are accuracies only under
        classification; under regression they are ``1 - mean(normalized
        residual)`` (see :meth:`_profile_on_buffer`) and must not be reported as
        accuracies.
        """
        t_start = time.perf_counter()
        trace_before = self.trace_time_s
        self.num_drifts += 1
        details: Dict[str, Any] = {"buffer_len": len(buffer)}
        details.update(self._settle_reuse_value())

        # Freeze current leader into its slot before buffer comparisons
        self.slots[self.current_idx] = _deep_clone(prediction_model)
        # The frozen slot represents the era that just ended.
        self.slot_eras[self.current_idx] = self.num_drifts - 1
        self._measure_slot(self.current_idx)

        # Update lifetime stats for current leader slot (MOA getNextModel start)
        st = self.slot_stats[self.current_idx]
        st.n_inst += self.total_inst
        st.n_correct += self.curr_correct

        # Behavioural signatures on the buffer for each alive slot
        alive = [i for i, m in enumerate(self.slots) if m is not None]
        if not alive:
            self.bootstrap_first_expert(prediction_model)
            alive = [0]

        signatures: Dict[int, np.ndarray] = {}
        acc_on_buffer: Dict[int, float] = {}
        for i in alive:
            sig, score = self._profile_on_buffer(self.slots[i], buffer)
            signatures[i] = sig
            acc_on_buffer[i] = score

        # Pairwise similarity update (paper §3.1)
        for a in range(len(alive)):
            for b in range(a + 1, len(alive)):
                i, j = alive[a], alive[b]
                key = (min(i, j), max(i, j))
                agreed = self._pair_agreement(signatures[i], signatures[j])
                self._pair_seen[key] = self._pair_seen.get(key, 0) + len(buffer)
                self._pair_agreed[key] = self._pair_agreed.get(key, 0) + agreed

        # Merge similar slots (may remove indices)
        self.last_merge_pairs = []
        removed = self._merge_models(alive)
        details["merged"] = removed

        if self.slots[self.current_idx] is None:
            survivors = [i for i, m in enumerate(self.slots) if m is not None]
            self.current_idx = survivors[0] if survivors else 0

        # Recompute survivors and buffer score after merges
        alive = [i for i, m in enumerate(self.slots) if m is not None]
        acc_on_buffer = {}
        for i in alive:
            acc_on_buffer[i] = self._profile_on_buffer(self.slots[i], buffer)[1]

        # Fresh learner trained on full warning buffer
        self.new_model = self._fresh_model()
        self._fit_on_buffer(self.new_model, buffer)

        # Best existing expert on buffer (reuse candidate)
        if not alive:
            best_i = self.current_idx
        else:
            best_i = max(alive, key=lambda idx: acc_on_buffer.get(idx, 0.0))

        # Score diagnostics on the warning buffer (accuracies under
        # classification, 1 - mean normalized residual under regression).
        acc_best = float(acc_on_buffer.get(best_i, 0.0))
        acc_current = float(acc_on_buffer.get(self.current_idx, 0.0))
        acc_new = float(self._profile_on_buffer(self.new_model, buffer)[1])

        # Regret diagnostic: would a recently evicted expert have beaten the
        # best one still stored on this buffer?
        if self.pool_trace and self._ghosts:
            t_trace = time.perf_counter()
            ghost_scores = [
                (self._profile_on_buffer(model, buffer)[1], slot, era)
                for slot, era, model in self._ghosts
            ]
            g_score, g_slot, g_era = max(ghost_scores, key=lambda r: r[0])
            self.regret_log.append({
                "t": int(self.clock),
                "drift": int(self.num_drifts),
                "best_alive_score": acc_best,
                "best_ghost_score": float(g_score),
                "ghost_slot": int(g_slot),
                "ghost_era": int(g_era),
                "regret": float(g_score) > acc_best,
                "gap": float(g_score) - acc_best,
            })
            self.trace_time_s += time.perf_counter() - t_trace

        # ``subst``: the alternative to this reuse is the next-best stored
        # expert (or the fresh learner, whichever does better).
        self._rv_alt = None
        self._rv_alt_correct = 0
        self._rv_has_alt = False
        if self.fade_policy == "subst":
            others = [i for i in alive if i != best_i]
            if others:
                second = max(others, key=lambda idx: acc_on_buffer.get(idx, 0.0))
                self._rv_alt = _deep_clone(self.slots[second])
                self._rv_has_alt = True

        # Copy of best → new slot becomes active (MOA addModel(copy of best))
        clone_best = _deep_clone(self.slots[best_i])
        self.slots.append(clone_best)
        new_idx = len(self.slots) - 1
        self.slot_stats.append(_SlotStats())
        self.fade_scores.setdefault(new_idx, 0)
        # The clone becomes the leader for the era that starts now.
        self.slot_eras[new_idx] = self.num_drifts
        self._slot_birth[new_idx] = self.num_drifts
        if best_i in self.slot_kb:
            self.slot_kb[new_idx] = self.slot_kb[best_i]
        self.current_idx = new_idx

        # Install leader weights into pipeline model = copy of best
        self._copy_model_into(prediction_model, clone_best)

        # Start measuring what this reuse is worth against the fresh learner.
        self._reuse_source = best_i
        self._leader_is_reused = True
        self._rv_reused_correct = 0
        self._rv_fresh_correct = 0
        self._rv_n = 0

        if self.fade_enabled:
            self._fade_models()
        self._enforce_pool_cap()
        self._enforce_memory_budget()
        self._record_timeline()

        self.curr_correct = 0
        self.new_correct = 0
        self.total_inst = 0
        self.model_reuses += 1
        self.pool_time_s += (time.perf_counter() - t_start) - (self.trace_time_s - trace_before)

        details["collection_size"] = sum(1 for s in self.slots if s is not None)
        details["current_idx"] = self.current_idx
        details["best_idx"] = best_i
        details["acc_current_on_warning"] = acc_current
        details["acc_best_on_warning"] = acc_best
        details["acc_new_on_warning"] = acc_new
        details["winner_initial"] = "reused_copy"
        # Per-expert score on the warning buffer (stage-3 interpretability).
        details["acc_on_buffer"] = {int(i): float(v) for i, v in acc_on_buffer.items()}
        if self.task is not None:
            # Only emitted for task-aware callers, so the dict a legacy binary
            # run produces keeps exactly the keys it always had.
            details["similarity_metric"] = (
                "residual_pearson" if self._is_regression
                else ("error_bitset" if self._use_bitset else "label_agreement")
            )
            details["merge_pairs"] = list(self.last_merge_pairs)
            details["slot_eras"] = {int(k): int(v) for k, v in self.slot_eras.items()}
            details["score_semantics"] = (
                "1_minus_mean_normalized_residual" if self._is_regression else "accuracy"
            )
        return details

    def _settle_reuse_value(self) -> Dict[str, Any]:
        """Close the previous reuse episode and credit its source slot.

        value = errors the reused copy avoided vs. the fresh learner over the
        first ``reuse_value_window`` instances after the last drift. Under
        ``fade_policy="reuse_value"`` it is added to the source's fade score
        (negative when reuse did worse than starting fresh).
        """
        src = self._reuse_source
        if src is None or self._rv_n == 0:
            return {}
        baseline = self._rv_fresh_correct
        has_alt = self._rv_has_alt
        if has_alt:
            baseline = max(baseline, self._rv_alt_correct)
        value = self._rv_reused_correct - baseline
        record = {
            "reuse_value": float(value) if self._is_regression else int(value),
            "reuse_value_source": int(src),
            "reuse_value_n": int(self._rv_n),
        }
        log = dict(record, drift=self.num_drifts)
        if self.pool_trace:
            log.update(
                t=int(self.clock),
                reused_correct=float(self._rv_reused_correct),
                fresh_correct=float(self._rv_fresh_correct),
                alt_correct=float(self._rv_alt_correct) if has_alt else None,
                leader_is_reused_at_end=bool(self._leader_is_reused),
            )
        self.reuse_value_log.append(log)
        if (
            self.fade_policy != "ecpf"
            and src < len(self.slots)
            and self.slots[src] is not None
        ):
            self.fade_scores[src] = self.fade_scores.get(src, 0) + value
            self._slot_reuses[src] = self._slot_reuses.get(src, 0) + 1
            self._slot_rv_sum[src] = self._slot_rv_sum.get(src, 0.0) + float(value)
        self._reuse_source = None
        self._rv_alt = None
        self._rv_alt_correct = 0
        self._rv_has_alt = False
        return record

    def _fresh_model(self) -> Any:
        """Build the shadow ("new") learner that duels the reused expert.

        The class set is *declared* rather than left to be inferred, because this
        model is created at a drift and immediately fit on the warning buffer --
        a buffer that is whatever the detector handed over and can be a single
        instance long.  sklearn commits ``classes_`` on that first fit and can
        never widen it, so an inferred set means: ``SGDClassifier.fit`` raises
        "number of classes has to be greater than one" on a single-label buffer,
        while ``GaussianNB`` survives but can only ever emit that one label and
        drops every other sample from then on.  Either way the damage escapes
        this object, because ``_compare_classifiers`` can install the crippled
        estimator into the pipeline's leader via ``set_model``.

        ``needs_class_declaration`` returns False for the ``{0, 1}`` label sets of
        the published binary streams, so those keep constructing exactly the
        wrapper they always did.
        """
        if self.use_advanced:
            from .model_adapter import BaseModelAdapter

            return BaseModelAdapter(
                model_type=self.model_type,
                model_kwargs=self.model_kwargs,
            )
        from .prediction_model import PredictionModel, needs_class_declaration

        classes = None
        if self.task is not None and self.task.is_classification:
            if needs_class_declaration(self.task.classes):
                classes = self.task.classes
        return PredictionModel(model_type=self.model_type, classes=classes)

    def _copy_model_into(self, target: Any, source: Any) -> None:
        if self.use_advanced:
            target.set_model(_deep_clone(source.get_model()))
            return
        target.set_model(copy.deepcopy(source.get_model()))
        target.scaler = copy.deepcopy(source.scaler)
        target._scaler_fitted = source._scaler_fitted

    def _merge_models(self, alive: List[int]) -> List[int]:
        """Remove redundant experts when pairwise similarity ≥ m (paper).

        The similarity is ``_pair_agreed / _pair_seen``, a per-instance average
        over every warning buffer the pair has been scored on.  Its *meaning*
        depends on the task (label-agreement rate vs. remapped Pearson
        correlation of residuals) but its range does not, so the threshold test
        is shared.  Note that ``similarity_margin=0.95`` is the paper's value for
        an agreement rate and is not a calibrated threshold for a correlation.

        The loser of a merge is the expert with the lower lifetime score; under
        regression ``_SlotStats.n_correct / n_inst`` is a mean
        ``1 - normalized residual``, not an accuracy.
        """
        removed: List[int] = []
        alive = [i for i in alive if self.slots[i] is not None]
        for a in range(len(alive)):
            for b in range(a + 1, len(alive)):
                i, j = alive[a], alive[b]
                if self.slots[i] is None or self.slots[j] is None:
                    continue
                key = (min(i, j), max(i, j))
                seen = self._pair_seen.get(key, 0)
                if seen <= 0:
                    continue
                agreed = self._pair_agreed.get(key, 0)
                if agreed / seen < self.similarity_margin:
                    continue
                ai = self.slot_stats[i]
                aj = self.slot_stats[j]
                acc_i = ai.n_correct / max(1, ai.n_inst)
                acc_j = aj.n_correct / max(1, aj.n_inst)
                lose, keep = (j, i) if acc_i >= acc_j else (i, j)
                if self.pool_trace:
                    self.eviction_log.append({
                        "t": int(self.clock),
                        "drift": int(self.num_drifts),
                        "slot": int(lose),
                        "reason": "merge",
                        "kept": int(keep),
                        "kb": round(float(self.slot_kb.get(lose, 0.0)), 3),
                        "era": int(self.slot_eras.get(lose, -1)),
                    })
                self._remove_slot(lose)
                removed.append(lose)
                self.last_merge_pairs.append((int(keep), int(lose)))
                self.model_merges += 1
                if self.fade_enabled:
                    self.fade_scores[keep] = self.fade_scores.get(keep, 0) + self.fade_scores.get(
                        lose, 0
                    )
                    self.fade_scores.pop(lose, None)
        return removed

    def _remove_slot(self, idx: int) -> None:
        self.slots[idx] = None
        self.slot_kb.pop(idx, None)
        if idx < len(self.slot_stats):
            self.slot_stats[idx] = _SlotStats()
        keys = [k for k in self._pair_seen if idx in k]
        for k in keys:
            self._pair_seen.pop(k, None)
            self._pair_agreed.pop(k, None)

    def _fade_models(self) -> None:
        """Fade stored experts; at 0 remove.

        ``ecpf`` (MOA): current gains f; others lose 1.
        ``reuse_value``: current is only topped up to a grace of f (so a new
        leader is not evicted before it can prove itself); others lose
        ``reuse_idle_cost``. Gains come from ``_settle_reuse_value`` instead.
        The memory-aware policies (module docstring) share the reuse_value
        gains and leader grace and differ in the idle cost.
        """
        mean_kb = self._mean_kb() if self._track_sizes else 1.0
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                continue
            if i == self.current_idx:
                if self.fade_policy != "ecpf":
                    self.fade_scores[i] = max(self.fade_scores.get(i, 0), self.fade_points)
                else:
                    self.fade_scores[i] = self.fade_scores.get(i, 0) + self.fade_points
            else:
                fs = self.fade_scores.get(i, 0)
                if self.fade_policy == "ecpf":
                    cost = 1
                elif self.fade_policy == "rent":
                    cost = self.fade_lambda * self.slot_kb.get(i, mean_kb) / mean_kb
                else:
                    cost = self.reuse_idle_cost
                if self.fade_policy == "decay":
                    fs = self.decay_gamma * fs
                if self.fade_policy == "entry" and i not in self._entry_paid:
                    fs -= self.fade_lambda * self.slot_kb.get(i, mean_kb) / mean_kb
                    self._entry_paid.add(i)
                fs -= cost
                if fs <= 0:
                    self.fade_scores[i] = fs
                    self._evict(i, "fade")
                else:
                    self.fade_scores[i] = fs

    def _enforce_pool_cap(self) -> None:
        """Keep at most ``max_pool_size`` alive snapshots, excluding current leader."""
        while sum(1 for s in self.slots if s is not None) > self.max_pool_size:
            candidates = [
                (self._eviction_key(i), i)
                for i, slot in enumerate(self.slots)
                if slot is not None and i != self.current_idx
            ]
            if not candidates:
                break
            _, rm_idx = min(candidates)
            self._evict(rm_idx, "cap")

    def _enforce_memory_budget(self) -> None:
        """Keep stored KB <= ``memory_budget_factor`` x the leader's KB."""
        if self.memory_budget_factor <= 0:
            return
        budget = self.memory_budget_factor * self.slot_kb.get(self.current_idx, 0.0)
        while self.pool_kb() > budget:
            candidates = [
                (self._eviction_key(i), i)
                for i in self._alive()
                if i != self.current_idx
            ]
            if not candidates:
                break
            _, rm_idx = min(candidates)
            self._evict(rm_idx, "budget")

    def pool_trace_dict(self) -> Dict[str, Any]:
        """Everything the pool trace recorded, JSON-serialisable."""
        return {
            "fade_policy": self.fade_policy,
            "fade_lambda": self.fade_lambda,
            "decay_gamma": self.decay_gamma,
            "memory_budget_factor": self.memory_budget_factor,
            "max_pool_size": self.max_pool_size,
            "reuse_value_window": self.reuse_value_window,
            "num_drifts": int(self.num_drifts),
            "model_reuses": int(self.model_reuses),
            "model_merges": int(self.model_merges),
            "leader_swaps": int(self.leader_swaps),
            "pool_time_s": round(self.pool_time_s, 4),
            "sizing_time_s": round(self.sizing_time_s, 4),
            "trace_time_s": round(self.trace_time_s, 4),
            "timeline": [list(r) for r in self.pool_timeline],
            "evictions": self.eviction_log,
            "regret": self.regret_log,
            "reuse_values": self.reuse_value_log,
        }

    def ghost_models(self) -> List[Any]:
        """Evicted experts kept only for the regret diagnostic."""
        return [m for _, _, m in self._ghosts]


def load_drift_times_file(path: str) -> List[int]:
    """Load drift times from txt (ints, space-separated, or list-of-pairs)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return []
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, list):
            out: List[int] = []
            for item in obj:
                if isinstance(item, (list, tuple)) and item:
                    out.append(int(item[0]))
                else:
                    out.append(int(item))
            return out
    except Exception:
        pass
    lines = text.replace(",", " ").replace("[", " ").replace("]", " ").split()
    return [int(x) for x in lines if x.lstrip("-").isdigit()]


def load_drift_intervals_file(path: str) -> List[Tuple[int, int]]:
    """Load drift intervals from txt; returns a list of (start, end) pairs.

    Supports two formats:
    - List-of-pairs: ``[[s1, e1], [s2, e2], ...]``
    - Single integers / list of ints: each is treated as a zero-width interval (t, t).
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return []
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, list):
            out: List[Tuple[int, int]] = []
            for item in obj:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    out.append((int(item[0]), int(item[1])))
                elif isinstance(item, (list, tuple)) and len(item) == 1:
                    t = int(item[0])
                    out.append((t, t))
                else:
                    t = int(item)
                    out.append((t, t))
            return out
    except Exception:
        pass
    lines = text.replace(",", " ").replace("[", " ").replace("]", " ").split()
    return [(int(x), int(x)) for x in lines if x.lstrip("-").isdigit()]
