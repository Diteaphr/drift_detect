"""
hoeffding_forest.py
===================
Hoeffding Forest — a manually-built ensemble of **plain** Hoeffding Tree
classifiers from the River library.

Unlike ``ARFClassifier`` (which embeds ADWIN drift detectors inside each
tree and silently swaps subtrees), this model is a *passive* ensemble:

*   Each member is a vanilla ``HoeffdingTreeClassifier`` (no internal drift
    handling).
*   **Online Bagging** with ``Poisson(λ)`` replication provides ensemble
    diversity (standard ARF technique, Oza & Russell 2001).
*   **Random Feature Subspace**: each tree sees a random subset of features
    at each split (controlled via ``max_features``).
*   Exposes ``predict_proba_matrix(x)`` so that external modules (e.g.
    ``UQExtractor``) can compute per-tree probability vectors for
    uncertainty quantification.

This design gives ECPF full external control over the model lifecycle
(save / restore / fade / merge) without any internal drift signal
interfering.
"""

from __future__ import annotations

import math
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from river import tree

from .base_model import BaseModel


class HoeffdingForestModel(BaseModel):
    """Ensemble of plain Hoeffding Trees with online bagging — River.

    Parameters
    ----------
    n_trees : int
        Number of trees in the forest.
    max_features : str or float or int or None
        Feature subsampling strategy per tree.  ``"sqrt"`` uses
        ``ceil(sqrt(n_features))`` features at each split.
    lambda_poisson : float
        Poisson λ for online bagging.  Each ``learn_one`` call passes
        the sample to each tree ``k ~ Poisson(λ)`` times.  Higher λ
        increases diversity at the cost of more computation.
    grace_period : int
        Number of instances a leaf must observe between split-attempts
        (forwarded to each ``HoeffdingTreeClassifier``).
    max_depth : int or None
        Maximum tree depth (``None`` = unlimited).
    split_criterion : str
        One of ``"info_gain"``, ``"gini"``, ``"hellinger"``.
    delta : float
        Allowable error in the Hoeffding-bound split decision.
    tau : float
        Tie-breaking threshold.
    leaf_prediction : str
        ``"mc"`` (majority class), ``"nb"`` (naive Bayes), or ``"nba"``
        (naive Bayes adaptive).
    nb_threshold : int
        Minimum samples before NB prediction kicks in.
    max_size : float
        Maximum tree size in MB.
    seed : int or None
        Base random seed.  Each tree uses ``seed + tree_index``.
    """

    def __init__(
        self,
        n_trees: int = 10,
        max_features: Union[str, float, int, None] = "sqrt",
        lambda_poisson: float = 6.0,
        grace_period: int = 200,
        max_depth: Optional[int] = None,
        split_criterion: str = "info_gain",
        delta: float = 1e-7,
        tau: float = 0.05,
        leaf_prediction: str = "nba",
        nb_threshold: int = 0,
        max_size: float = 100.0,
        seed: Optional[int] = 42,
    ) -> None:
        self.n_trees = int(n_trees)
        self.max_features = max_features
        self.lambda_poisson = float(lambda_poisson)
        self.seed = seed

        # Store HT kwargs for cloning / fresh model creation
        # NOTE: River's HoeffdingTreeClassifier does NOT accept max_features.
        # We implement random feature subspace masking manually in learn_one.
        self._ht_kwargs = dict(
            grace_period=grace_period,
            max_depth=max_depth,
            split_criterion=split_criterion,
            delta=delta,
            tau=tau,
            leaf_prediction=leaf_prediction,
            nb_threshold=nb_threshold,
            max_size=max_size,
        )

        # Build the ensemble
        self.trees: List[tree.HoeffdingTreeClassifier] = []
        self._rngs: List[np.random.Generator] = []
        # Per-tree feature masks are lazily initialised on first learn_one
        # (we need to know the feature names first).
        self._feature_masks: List[Optional[List[str]]] = []
        for i in range(self.n_trees):
            t = tree.HoeffdingTreeClassifier(
                **self._ht_kwargs,
            )
            self.trees.append(t)
            rng_seed = (seed + i * 1000) if seed is not None else None
            self._rngs.append(np.random.default_rng(rng_seed))
            self._feature_masks.append(None)  # will be set on first learn_one

    def _resolve_n_subfeatures(self, n_features: int) -> int:
        """Compute how many features each tree should see."""
        if self.max_features is None:
            return n_features
        if isinstance(self.max_features, str):
            if self.max_features == "sqrt":
                return max(1, math.ceil(math.sqrt(n_features)))
            elif self.max_features == "log2":
                return max(1, math.ceil(math.log2(n_features)))
            else:
                return n_features
        if isinstance(self.max_features, float):
            return max(1, int(self.max_features * n_features))
        if isinstance(self.max_features, int):
            return min(self.max_features, n_features)
        return n_features

    def _init_feature_masks(self, feature_names: List[str]) -> None:
        """Assign each tree a fixed random subset of feature names."""
        n = self._resolve_n_subfeatures(len(feature_names))
        for i in range(self.n_trees):
            if self._feature_masks[i] is None:
                chosen = self._rngs[i].choice(
                    feature_names, size=n, replace=False
                ).tolist()
                self._feature_masks[i] = sorted(chosen)

    # ------------------------------------------------------------------
    # Per-tree probability access (key API for UQ)
    # ------------------------------------------------------------------
    def predict_proba_matrix(self, x: Any) -> List[Dict[Any, float]]:
        """Return per-tree class probability dicts for one sample.

        Parameters
        ----------
        x : dict or array-like
            Single sample.

        Returns
        -------
        List of length ``n_trees``, each element is a ``{class: prob}``
        dict as returned by ``HoeffdingTreeClassifier.predict_proba_one``.

        Note: for prediction, all features are used (no masking).  The
        random subspace only affects training to create diversity.
        """
        x_dict = self._to_dict(x)
        matrix: List[Dict[Any, float]] = []
        for t in self.trees:
            proba = t.predict_proba_one(x_dict)
            matrix.append(proba if proba else {})
        return matrix

    def predict_proba_one(self, x: Any) -> Dict[Any, float]:
        """Ensemble-averaged class probability dict for one sample."""
        matrix = self.predict_proba_matrix(x)
        return self._average_proba(matrix)

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "HoeffdingForestModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        for xi, yi in zip(X, y):
            x_dict = self._to_dict(xi)
            self._learn_one_internal(x_dict, yi)
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        preds = []
        for xi in X:
            preds.append(self.predict_one(xi))
        return np.array(preds)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Any, y: Any) -> "HoeffdingForestModel":
        x_dict = self._to_dict(x)
        self._learn_one_internal(x_dict, y)
        return self

    def predict_one(self, x: Any) -> Any:
        """Majority vote prediction across all trees."""
        x_dict = self._to_dict(x)
        votes: Dict[Any, int] = {}
        for t in self.trees:
            pred = t.predict_one(x_dict)
            if pred is None:
                pred = 0
            votes[pred] = votes.get(pred, 0) + 1
        if not votes:
            return 0
        return max(votes, key=votes.get)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _learn_one_internal(self, x_dict: Dict[str, float], y: Any) -> None:
        """Online bagging + random feature subspace.

        Each tree receives the sample ``k ~ Poisson(λ)`` times, with only
        its assigned subset of features visible during training.
        """
        # Lazy init: assign each tree a random feature subset
        if self._feature_masks[0] is None and x_dict:
            all_features = sorted(x_dict.keys())
            self._init_feature_masks(all_features)

        for i, t in enumerate(self.trees):
            k = int(self._rngs[i].poisson(self.lambda_poisson))
            if k == 0:
                continue
            # Apply feature mask: only pass the assigned features
            mask = self._feature_masks[i]
            if mask is not None and len(mask) < len(x_dict):
                masked_x = {f: x_dict[f] for f in mask if f in x_dict}
            else:
                masked_x = x_dict
            for _ in range(k):
                t.learn_one(masked_x, y)

    @staticmethod
    def _average_proba(matrix: List[Dict[Any, float]]) -> Dict[Any, float]:
        """Average class probability dicts from multiple trees."""
        if not matrix:
            return {}
        n = len(matrix)
        merged: Dict[Any, float] = {}
        for proba in matrix:
            for cls, prob in proba.items():
                merged[cls] = merged.get(cls, 0.0) + prob
        return {cls: val / n for cls, val in merged.items()}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "HoeffdingForestModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"HoeffdingForestModel(n_trees={self.n_trees}, "
            f"max_features={self.max_features!r}, "
            f"lambda_poisson={self.lambda_poisson}, "
            f"seed={self.seed})"
        )
