"""
hoeffding_tree.py
=================
Plain Hoeffding Tree classifier from the River library.

Unlike ``HoeffdingAdaptiveTreeClassifier`` (which embeds ADWIN drift detectors
inside each split and silently swaps subtrees) and unlike ``ARFClassifier``
(an ensemble of adaptive trees), this model is a *vanilla* incremental
decision tree:

*   Grows split-by-split using the Hoeffding bound on a fixed information
    criterion (no internal drift signal).
*   Never resets, prunes, or swaps subtrees on its own.
*   Behaves like a passive online learner — ideal for evaluating *external*
    drift-handling architectures (e.g. ECPF, where a separate stable / reactive
    learner pair must drive concept switching).
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from river import tree

from .base_model import BaseModel


class HoeffdingTreeModel(BaseModel):
    """Plain (non-adaptive) Hoeffding Tree classifier — River.

    The learner only grows the tree from streaming samples; it does **not**
    perform any concept-drift detection or self-replacement.  Pair it with an
    external framework (ECPF, two-learner ensembles, etc.) to handle drift.

    Parameters
    ----------
    grace_period : int
        Number of instances a leaf must observe between split-attempts.
    max_depth : int or None
        Maximum tree depth (``None`` = unlimited).
    split_criterion : str
        One of ``"info_gain"``, ``"gini"``, ``"hellinger"``.
    delta : float
        Allowable error in the Hoeffding-bound split decision (1 - confidence).
    tau : float
        Threshold for tie-breaking between candidate split attributes.
    leaf_prediction : str
        Leaf prediction strategy: ``"mc"`` (majority class), ``"nb"``
        (naive Bayes), or ``"nba"`` (naive Bayes adaptive — default).
    nb_threshold : int
        Minimum samples a leaf must observe before naive-Bayes prediction
        kicks in (only relevant when ``leaf_prediction`` != ``"mc"``).
    nominal_attributes : list of str or None
        Names of nominal (categorical) features.  ``None`` = treat all as
        numeric, which is what we want for the SEA-style streams used here.
    max_size : float
        Maximum tree size in MB (River caps memory usage).
    """

    def __init__(
        self,
        grace_period: int = 200,
        max_depth: Optional[int] = None,
        split_criterion: str = "info_gain",
        delta: float = 1e-7,
        tau: float = 0.05,
        leaf_prediction: str = "nba",
        nb_threshold: int = 0,
        nominal_attributes: Optional[List[str]] = None,
        max_size: float = 100.0,
    ) -> None:
        self._init_kwargs = dict(
            grace_period=grace_period,
            max_depth=max_depth,
            split_criterion=split_criterion,
            delta=delta,
            tau=tau,
            leaf_prediction=leaf_prediction,
            nb_threshold=nb_threshold,
            nominal_attributes=nominal_attributes,
            max_size=max_size,
        )
        self.model = tree.HoeffdingTreeClassifier(**self._init_kwargs)

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "HoeffdingTreeModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        for xi, yi in zip(X, y):
            x_dict = self._to_dict(xi)
            self.model.learn_one(x_dict, yi)
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        preds = []
        for xi in X:
            x_dict = self._to_dict(xi)
            pred = self.model.predict_one(x_dict)
            preds.append(pred if pred is not None else 0)
        return np.array(preds)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "HoeffdingTreeModel":
        x = self._to_dict(x)
        self.model.learn_one(x, y)
        return self

    def predict_one(self, x: Dict[str, float]) -> Any:
        x = self._to_dict(x)
        pred = self.model.predict_one(x)
        return pred if pred is not None else 0

    def predict_proba_one(self, x: Dict[str, float]) -> Dict[Any, float]:
        """Class-probability dict for one sample (handy for ECPF voting)."""
        x = self._to_dict(x)
        return self.model.predict_proba_one(x) or {}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "HoeffdingTreeModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"HoeffdingTreeModel(grace_period={self._init_kwargs['grace_period']}, "
            f"max_depth={self._init_kwargs['max_depth']}, "
            f"split_criterion={self._init_kwargs['split_criterion']!r}, "
            f"leaf_prediction={self._init_kwargs['leaf_prediction']!r})"
        )
