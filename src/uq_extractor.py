"""
uq_extractor.py
===============
Uncertainty Quantification (UQ) scalar extraction from a Hoeffding Forest's
per-tree probability matrix.

ADWIN (and most change-detection algorithms) consume a **one-dimensional
scalar stream**.  A forest of M trees produces an M × K probability matrix
per sample; we need a principled reduction to a single scalar ``u_t``.

Four extraction modes are provided:

Primary — ``mi_like`` (MI-like disagreement / epistemic uncertainty)
    u_t = H(p̄_t) − (1/M) Σ H(p_{t,m})
    where p̄_t is the ensemble-averaged probability and H(·) is Shannon
    entropy.  This captures *only* the ensemble disagreement (epistemic
    uncertainty) and ignores aleatoric noise.  Under a stable concept the
    trees agree → u_t ≈ 0.  When a concept drift occurs, trees adapt at
    different rates → disagreement rises → u_t spikes.

Baseline 1 — ``vote_disagreement``
    u_t = 1 − max_c (1/M) Σ 1[argmax p_{t,m} = c]
    Fraction of trees that disagree with the majority hard vote.

Baseline 2 — ``predictive_entropy``
    u_t = H(p̄_t)
    Total predictive uncertainty (aleatoric + epistemic).

Baseline 3 -- ``variance_eu``
    u_t = sum_k Var_m(p_{t,m,k})
    Cross-tree probability variance summed over classes. This is a direct
    ensemble-variance epistemic uncertainty scalar; it does not rely on any
    tree-internal variance estimate.

Why ``mi_like`` is the primary choice:
*   It isolates epistemic uncertainty (inter-tree disagreement) from
    aleatoric noise, making it a cleaner signal for drift detection.
*   ``predictive_entropy`` mixes both sources and can stay high even in
    a stable but inherently noisy concept, leading to false warnings.
*   ``vote_disagreement`` is coarser (hard votes lose probability
    information) and less sensitive to subtle distribution shifts.

Scale and the number of classes K
---------------------------------
Every mode's range grows with K, so a threshold tuned on a binary stream does
**not** transfer to a K-class stream.  The theoretical maxima are:

======================  ==================  ============  ============
mode                    maximum             K=2           K=5
======================  ==================  ============  ============
``mi_like``             ``log2(K)``         1.0           2.3219
``predictive_entropy``  ``log2(K)``         1.0           2.3219
``vote_disagreement``   ``1 - 1/K``         0.5           0.8
``variance_eu``         ``1 - 1/K``         0.5           0.8
======================  ==================  ============  ============

Derivation of the ``variance_eu`` bound (the only non-obvious one).  With
``M`` members and population variance, the statistic is

    u = Σ_k Var_m(p_{m,k}) = (1/M) Σ_m ‖p_m − p̄‖²

i.e. the mean squared distance from the ensemble centroid.  Holding the other
members fixed, this is a convex function of any single ``p_m`` (its Hessian is
``2(1/M − 1/M²) I ⪰ 0``), so the maximum over the product of probability
simplices is attained at a *vertex* of each simplex — every member must be a
one-hot vector.  Let ``n_k`` members vote one-hot for class ``k`` and
``f_k = n_k/M``.  Then ``Var_k = f_k(1 − f_k)`` exactly, and

    u = Σ_k f_k(1 − f_k) = 1 − Σ_k f_k²  ≤  1 − 1/K,

with equality when the members split evenly across all K classes (reachable
exactly when K divides M).  So ``variance_eu`` and ``vote_disagreement``
happen to share the same bound.  :func:`theoretical_max` returns these values
and ``UQExtractor(normalize_scale=True)`` divides by them.

``normalize_scale`` defaults to **False** and must stay that way: at K=2 the
entropy modes divide by ``log2(2) = 1`` (a no-op), but ``vote_disagreement``
and ``variance_eu`` would divide by ``0.5`` and therefore *double*, changing
every published binary result.  The trade-off is deliberate — legacy binary
fidelity by default, K-comparable [0, 1] scalars on request.

Regression
----------
Only ``variance_eu`` survives the move to a continuous target: ``mi_like``,
``predictive_entropy`` and ``vote_disagreement`` are all defined over a
probability simplex, and a point-prediction ensemble has no simplex (no
classes to put mass on, no argmax to vote with).  Cross-member variance, by
contrast, is defined for any vector space.  Use :meth:`UQExtractor.extract_regression`;
note its output is **unbounded**, so the caller must push it through
``src.task.ErrorNormalizer`` before handing it to ADWIN/SEED/SeqDrift2.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence


def _entropy(proba: Dict[Any, float]) -> float:
    """Shannon entropy of a probability dict.  Returns 0 for empty/degenerate."""
    h = 0.0
    for p in proba.values():
        if p > 0.0:
            h -= p * math.log2(p)
    return h


def _normalize_proba(proba: Dict[Any, float]) -> Dict[Any, float]:
    """Clamp negative mass and normalize a probability dict."""
    cleaned = {c: max(0.0, float(p)) for c, p in proba.items()}
    total = sum(cleaned.values())
    if total <= 0.0:
        return cleaned
    return {c: p / total for c, p in cleaned.items()}


def _unify_classes(
    matrix: List[Dict[Any, float]],
    *,
    num_classes: Optional[int] = None,
    normalize: bool = True,
) -> List[Dict[Any, float]]:
    """Ensure all dicts in *matrix* share the same class keys (fill missing with 0)."""
    all_classes: set = set()
    for proba in matrix:
        all_classes.update(proba.keys())
    if num_classes is not None:
        all_classes.update(range(int(num_classes)))
    unified: List[Dict[Any, float]] = []
    for proba in matrix:
        d = {c: proba.get(c, 0.0) for c in all_classes}
        if normalize:
            d = _normalize_proba(d)
        unified.append(d)
    return unified


def theoretical_max(mode: str, num_classes: int) -> float:
    """Largest value *mode* can attain on a K-class probability simplex.

    See the module docstring for the derivation of the ``variance_eu`` /
    ``vote_disagreement`` bound (``1 - 1/K``); the entropy-based modes are
    bounded by ``log2(K)`` because ``H(p) <= log2(K)`` and ``mi_like`` is
    ``H(p̄)`` minus a non-negative term.

    Returns ``0.0`` for ``K < 2``, where every mode is identically zero and no
    meaningful rescaling exists — callers must treat that as "do not divide".
    """
    k = int(num_classes)
    if k < 2:
        return 0.0
    if mode in ("mi_like", "predictive_entropy"):
        return math.log2(k)
    if mode in ("vote_disagreement", "variance_eu"):
        return 1.0 - 1.0 / k
    raise ValueError(f"Unknown UQ mode {mode!r}")


class UQExtractor:
    """Extract a single UQ scalar from a forest's per-tree probability matrix.

    Parameters
    ----------
    mode : str
        One of ``"mi_like"``, ``"vote_disagreement"``,
        ``"predictive_entropy"``, ``"variance_eu"``.
    num_classes : int, optional
        Size of the label set.  Used to pad per-tree dicts with the classes a
        tree has not seen yet, and — when *normalize_scale* is on — to pin the
        rescaling denominator so it does not wobble as new classes appear in
        the stream.  Strongly recommended whenever *normalize_scale* is True.
    normalize_probabilities : bool
        Renormalize each tree's dict to sum to 1 before reducing.
    normalize_scale : bool
        Divide the result by :func:`theoretical_max`, mapping ``u_t`` into
        [0, 1] for any K so one threshold transfers across label-set sizes.

        **Defaults to False, and that default is load-bearing.**  At K=2 the
        entropy modes divide by ``log2(2) = 1`` (harmless), but
        ``vote_disagreement`` and ``variance_eu`` divide by ``1 - 1/2 = 0.5``
        and therefore come out *doubled*.  Flipping this default would silently
        change every binary experiment already published from this repo.  The
        trade-off: leave it off to reproduce legacy binary numbers, turn it on
        when you need thresholds that are comparable across K.
    """

    MODES = {"mi_like", "vote_disagreement", "predictive_entropy", "variance_eu"}

    #: Modes with a regression analogue (see :meth:`extract_regression`).
    REGRESSION_MODES = {"variance_eu"}

    def __init__(
        self,
        mode: str = "mi_like",
        *,
        num_classes: Optional[int] = None,
        normalize_probabilities: bool = True,
        normalize_scale: bool = False,
    ) -> None:
        if mode not in self.MODES:
            raise ValueError(
                f"Unknown UQ mode {mode!r}.  Choose from {sorted(self.MODES)}"
            )
        self.mode = mode
        self.num_classes = int(num_classes) if num_classes is not None else None
        self.normalize_probabilities = bool(normalize_probabilities)
        self.normalize_scale = bool(normalize_scale)

    # ------------------------------------------------------------------
    @classmethod
    def supports_regression(cls, mode: str) -> bool:
        """Whether *mode* has a continuous-target analogue.

        Lets a caller reject a regression run configured with an
        simplex-only mode instead of silently substituting another one.
        """
        return mode in cls.REGRESSION_MODES

    def _effective_k(self, unified: List[Dict[Any, float]]) -> int:
        """Class count to use as the rescaling denominator.

        Takes the larger of the declared ``num_classes`` and the number of keys
        actually present.  The declared value keeps the denominator constant
        over time (a wobbling denominator would make the scaled stream look
        like drift); the observed count is the safety net that guarantees the
        scaled value never exceeds 1.0 if the declaration was too small.
        """
        observed = len(unified[0]) if unified else 0
        if self.num_classes is None:
            return observed
        return max(self.num_classes, observed)

    def extract(self, proba_matrix: List[Dict[Any, float]]) -> float:
        """Compute UQ scalar from per-tree probability dicts.

        Parameters
        ----------
        proba_matrix : list of dict
            Length-M list where each element is ``{class: probability}``
            from one tree's ``predict_proba_one``.

        Returns
        -------
        float
            Non-negative UQ scalar ``u_t``.  Raw (mode- and K-dependent range)
            unless ``normalize_scale`` was set, in which case it lies in
            [0, 1].
        """
        if not proba_matrix:
            return 0.0

        # Filter out empty dicts (trees that haven't seen any data yet)
        valid = [p for p in proba_matrix if p]
        if not valid:
            return 0.0

        valid = _unify_classes(
            valid,
            num_classes=self.num_classes,
            normalize=self.normalize_probabilities,
        )

        if self.mode == "mi_like":
            value = self._mi_like(valid)
        elif self.mode == "vote_disagreement":
            value = self._vote_disagreement(valid)
        elif self.mode == "predictive_entropy":
            value = self._predictive_entropy(valid)
        elif self.mode == "variance_eu":
            value = self._variance_eu(valid)
        else:  # pragma: no cover - guarded by the constructor
            return 0.0

        if not self.normalize_scale:
            # Legacy path: byte-for-byte the pre-existing behaviour.
            return value

        denom = theoretical_max(self.mode, self._effective_k(valid))
        if denom <= 0.0:
            # K < 2: every mode is identically zero here, so there is nothing
            # to rescale and dividing would be 0/0.
            return value
        # Clamped because the [0, 1] range is this flag's whole contract, and
        # one degenerate input can breach it: if a member's dict is all zeros,
        # `_normalize_proba` leaves it unnormalized (its `total <= 0` guard), so
        # p̄ sums to less than 1 and H(p̄) can exceed log2(K) — measured up to
        # 1.06x on a sub-normalized 2-class p̄.  The unscaled path deliberately
        # keeps that legacy quirk untouched; only this opt-in path clamps.
        return min(1.0, max(0.0, value / denom))

    # ------------------------------------------------------------------
    # Scalar extraction implementations
    # ------------------------------------------------------------------
    @staticmethod
    def _mi_like(matrix: List[Dict[Any, float]]) -> float:
        """MI-like disagreement: H(p̄) − (1/M) Σ H(p_m)."""
        m = len(matrix)
        all_classes = sorted(matrix[0].keys())

        # Ensemble average p̄
        p_bar: Dict[Any, float] = {}
        for c in all_classes:
            p_bar[c] = sum(d.get(c, 0.0) for d in matrix) / m

        h_bar = _entropy(p_bar)
        avg_h = sum(_entropy(d) for d in matrix) / m
        # MI is always >= 0 by Jensen's inequality; clamp for float safety
        return max(0.0, h_bar - avg_h)

    @staticmethod
    def _vote_disagreement(matrix: List[Dict[Any, float]]) -> float:
        """1 − max_c (fraction of trees voting for class c)."""
        m = len(matrix)
        vote_counts: Dict[Any, int] = {}
        for d in matrix:
            if not d:
                continue
            winner = max(d, key=d.get)
            vote_counts[winner] = vote_counts.get(winner, 0) + 1
        if not vote_counts:
            return 0.0
        max_frac = max(vote_counts.values()) / m
        return 1.0 - max_frac

    @staticmethod
    def _predictive_entropy(matrix: List[Dict[Any, float]]) -> float:
        """H(p̄) — entropy of the ensemble-averaged probability."""
        m = len(matrix)
        all_classes = sorted(matrix[0].keys())

        p_bar: Dict[Any, float] = {}
        for c in all_classes:
            p_bar[c] = sum(d.get(c, 0.0) for d in matrix) / m
        return _entropy(p_bar)

    @staticmethod
    def _variance_eu(matrix: List[Dict[Any, float]]) -> float:
        """Cross-tree probability variance summed over classes."""
        m = len(matrix)
        if m <= 1:
            return 0.0
        all_classes = sorted(matrix[0].keys())
        total = 0.0
        for c in all_classes:
            values = [float(d.get(c, 0.0)) for d in matrix]
            mean = sum(values) / m
            total += sum((v - mean) ** 2 for v in values) / m
        return max(0.0, total)

    # ------------------------------------------------------------------
    # Regression
    # ------------------------------------------------------------------
    def extract_regression(self, preds: Sequence[float]) -> float:
        """Cross-member variance of an ensemble's **point** predictions.

        This is the ``variance_eu`` analogue for a continuous target, fed by
        ``HoeffdingForestRegressorModel.predict_per_model`` (a list of floats,
        one per member) rather than by a probability matrix.

        Why only this mode transfers
        ----------------------------
        ``mi_like``, ``predictive_entropy`` and ``vote_disagreement`` are all
        functionals of a probability simplex: entropy needs a normalized mass
        vector over a finite label set, and the hard vote needs an ``argmax``
        over classes.  A regression ensemble emits one real number per member —
        there is no simplex, no label set and no argmax, so those three have no
        analogue that is anything more than an arbitrary re-definition.
        Cross-member variance, in contrast, only needs a vector space, and it
        keeps exactly the epistemic reading it has in the classification case:
        members that were trained on the same concept agree, and members that
        adapted to a drift at different rates spread apart.

        This is a **separate method** rather than an overload of
        :meth:`extract` because the input type differs (``Sequence[float]``
        vs ``List[Dict[class, prob]]``); dispatching on the runtime shape of
        the argument would hide configuration errors that should be loud.

        Parameters
        ----------
        preds : sequence of float
            One point prediction per ensemble member.

        Returns
        -------
        float
            Population variance across members, ``>= 0``.  **Unbounded** — it
            is in the squared units of the target, so unlike the classification
            modes there is no theoretical maximum to divide by and
            ``normalize_scale`` does not apply.  The caller MUST map it into
            [0, 1] with ``src.task.ErrorNormalizer`` before feeding
            ADWIN / SEED / SeqDrift2, whose bounds assume a bounded stream.
        """
        # Non-finite members (an untrained tree, an overflowed extrapolation)
        # would poison the mean; drop them rather than return NaN and silently
        # corrupt the detector's window.
        values = [float(p) for p in preds if math.isfinite(float(p))]
        m = len(values)
        if m <= 1:
            return 0.0
        mean = sum(values) / m
        return max(0.0, sum((v - mean) ** 2 for v in values) / m)
