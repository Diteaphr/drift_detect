"""
uq_extractor.py
===============
Uncertainty Quantification (UQ) scalar extraction from a Hoeffding Forest's
per-tree probability matrix.

ADWIN (and most change-detection algorithms) consume a **one-dimensional
scalar stream**.  A forest of M trees produces an M × K probability matrix
per sample; we need a principled reduction to a single scalar ``u_t``.

Three extraction modes are provided:

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

Why ``mi_like`` is the primary choice:
*   It isolates epistemic uncertainty (inter-tree disagreement) from
    aleatoric noise, making it a cleaner signal for drift detection.
*   ``predictive_entropy`` mixes both sources and can stay high even in
    a stable but inherently noisy concept, leading to false warnings.
*   ``vote_disagreement`` is coarser (hard votes lose probability
    information) and less sensitive to subtle distribution shifts.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List


def _entropy(proba: Dict[Any, float]) -> float:
    """Shannon entropy of a probability dict.  Returns 0 for empty/degenerate."""
    h = 0.0
    for p in proba.values():
        if p > 0.0:
            h -= p * math.log2(p)
    return h


def _unify_classes(matrix: List[Dict[Any, float]]) -> List[Dict[Any, float]]:
    """Ensure all dicts in *matrix* share the same class keys (fill missing with 0)."""
    all_classes: set = set()
    for proba in matrix:
        all_classes.update(proba.keys())
    unified: List[Dict[Any, float]] = []
    for proba in matrix:
        d = {c: proba.get(c, 0.0) for c in all_classes}
        unified.append(d)
    return unified


class UQExtractor:
    """Extract a single UQ scalar from a forest's per-tree probability matrix.

    Parameters
    ----------
    mode : str
        One of ``"mi_like"``, ``"vote_disagreement"``, ``"predictive_entropy"``.
    """

    MODES = {"mi_like", "vote_disagreement", "predictive_entropy"}

    def __init__(self, mode: str = "mi_like") -> None:
        if mode not in self.MODES:
            raise ValueError(
                f"Unknown UQ mode {mode!r}.  Choose from {sorted(self.MODES)}"
            )
        self.mode = mode

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
            Non-negative UQ scalar ``u_t``.
        """
        if not proba_matrix:
            return 0.0

        # Filter out empty dicts (trees that haven't seen any data yet)
        valid = [p for p in proba_matrix if p]
        if not valid:
            return 0.0

        valid = _unify_classes(valid)

        if self.mode == "mi_like":
            return self._mi_like(valid)
        elif self.mode == "vote_disagreement":
            return self._vote_disagreement(valid)
        elif self.mode == "predictive_entropy":
            return self._predictive_entropy(valid)
        return 0.0  # unreachable

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
