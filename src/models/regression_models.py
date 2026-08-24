"""
regression_models.py
====================
Continuous-target counterparts of the classification learners in this package.

Three learners, mirroring the classification side one-for-one:

======================================  ==========================================
Classification                          Regression
======================================  ==========================================
``HoeffdingTreeModel``                  :class:`HoeffdingTreeRegressorModel`
``RandomForestModel`` (ARFClassifier)   :class:`AdaptiveRandomForestRegressorModel`
``HoeffdingForestModel``                :class:`HoeffdingForestRegressorModel`
======================================  ==========================================

Why a separate module rather than a ``task_type`` switch inside the existing
classes: River's regressors are different classes with different constructor
arguments (no ``split_criterion``, no ``nb_threshold``, a ``leaf_model``
instead) and a different prediction contract (a scalar, not a probability
dict).  Branching inside the classification wrappers would have put a
regression code path inside the objects that produced the published binary
results; keeping them in a new module leaves those objects byte-for-byte
untouched.

Uncertainty quantification
--------------------------
Of the four UQ modes used in this project (``predictive_entropy``, ``mi_like``,
``vote_disagreement``, ``variance_eu``) only **ensemble variance** survives the
move to a continuous target — the other three need a probability simplex, which
does not exist here.  :class:`HoeffdingForestRegressorModel` therefore exposes
``predict_per_model(x) -> List[float]``, the regression analogue of
``HoeffdingForestModel.predict_proba_matrix``: the spread of those point
predictions *is* the epistemic uncertainty signal.

``AdaptiveRandomForestRegressorModel`` deliberately does not expose
``predict_per_model``, exactly as ``RandomForestModel`` does not expose
``predict_proba_matrix``: ARF swaps its own members when its internal ADWIN
fires, so member-to-member spread is contaminated by the ensemble's own drift
handling and is not a clean epistemic signal.

Verified against river 0.21.2 (``river.tree.HoeffdingTreeRegressor``,
``river.forest.ARFRegressor``).
"""

from __future__ import annotations

import math
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from river import forest, tree

from .base_model import BaseModel


def _as_float(value: Any, default: float = 0.0) -> float:
    """Coerce a River prediction to a plain float.

    River returns ``0.0`` from an untrained ``HoeffdingTreeRegressor`` but
    ``None`` from some other estimators; normalising here keeps every caller
    (and every ``np.array`` built from these) on a numeric dtype.
    """
    if value is None:
        return default
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


class HoeffdingTreeRegressorModel(BaseModel):
    """Plain (non-adaptive) Hoeffding Tree regressor — River.

    The regression twin of ``HoeffdingTreeModel``: it grows split-by-split from
    the stream and never resets, prunes, or swaps subtrees on its own, so an
    *external* drift-handling architecture (ECPF) owns the whole model
    lifecycle and no internal drift signal interferes with the experiment.

    Parameters
    ----------
    grace_period : int
        Number of instances a leaf must observe between split-attempts.
    max_depth : int or None
        Maximum tree depth (``None`` = unlimited).
    delta : float
        Allowable error in the Hoeffding-bound split decision (1 - confidence).
    tau : float
        Threshold for tie-breaking between candidate split attributes.
    leaf_prediction : str
        ``"mean"``, ``"model"`` (the leaf's linear model), or ``"adaptive"``
        (River's default — picks whichever of the two has been more accurate
        at that leaf).  There is no ``"nba"`` here: the classification split
        criteria and naive-Bayes leaves have no regression counterpart.
    leaf_model : river estimator or None
        Regressor used at the leaves when ``leaf_prediction`` is not
        ``"mean"``.  ``None`` = River's default (``LinearRegression``).
    model_selector_decay : float
        Fading factor for the ``"adaptive"`` leaf-model comparison.
    min_samples_split : int
        Minimum observations required before a split is attempted.
    nominal_attributes : list of str or None
        Names of nominal (categorical) features.  ``None`` = all numeric.
    max_size : float
        Maximum tree size in MB (River's memory cap).
    """

    def __init__(
        self,
        grace_period: int = 200,
        max_depth: Optional[int] = None,
        delta: float = 1e-7,
        tau: float = 0.05,
        leaf_prediction: str = "adaptive",
        leaf_model: Any = None,
        model_selector_decay: float = 0.95,
        min_samples_split: int = 5,
        nominal_attributes: Optional[List[str]] = None,
        max_size: float = 500.0,
    ) -> None:
        self._init_kwargs = dict(
            grace_period=grace_period,
            max_depth=max_depth,
            delta=delta,
            tau=tau,
            leaf_prediction=leaf_prediction,
            leaf_model=leaf_model,
            model_selector_decay=model_selector_decay,
            min_samples_split=min_samples_split,
            nominal_attributes=nominal_attributes,
            max_size=max_size,
        )
        self.model = tree.HoeffdingTreeRegressor(**self._init_kwargs)

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "HoeffdingTreeRegressorModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        for xi, yi in zip(X, y):
            x_dict = self._to_dict(xi)
            self.model.learn_one(x_dict, float(yi))
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        preds = [
            _as_float(self.model.predict_one(self._to_dict(xi))) for xi in X
        ]
        return np.asarray(preds, dtype=float)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "HoeffdingTreeRegressorModel":
        x = self._to_dict(x)
        self.model.learn_one(x, float(y))
        return self

    def predict_one(self, x: Dict[str, float]) -> float:
        x = self._to_dict(x)
        return _as_float(self.model.predict_one(x))

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "HoeffdingTreeRegressorModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"HoeffdingTreeRegressorModel("
            f"grace_period={self._init_kwargs['grace_period']}, "
            f"max_depth={self._init_kwargs['max_depth']}, "
            f"leaf_prediction={self._init_kwargs['leaf_prediction']!r})"
        )


class AdaptiveRandomForestRegressorModel(BaseModel):
    """Adaptive Random Forest regressor (ARF-Reg) — River.

    The regression twin of ``RandomForestModel``.  Like its classifier sibling
    it is *self*-adaptive: every member carries an internal drift detector and
    is replaced when that detector fires.  It is the natural strong baseline
    for a regression stream, and the natural control against ECPF's external
    concept management.

    Parameters
    ----------
    n_models : int
        Number of trees in the forest.
    max_features : str or float or int
        Feature subsampling strategy per tree (``"sqrt"``, ``"log2"``, a
        fraction, or a count).
    aggregation_method : str
        How member predictions are combined: ``"mean"`` or ``"median"``.
        River defaults to ``"median"`` because a single mis-adapted tree can
        drag a mean arbitrarily far in an unbounded output space.
    lambda_value : float
        Poisson λ for online bagging.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        n_models: int = 10,
        max_features: Union[str, float, int] = "sqrt",
        aggregation_method: str = "median",
        lambda_value: float = 6.0,
        seed: Optional[int] = 42,
    ) -> None:
        self.model = forest.ARFRegressor(
            n_models=n_models,
            max_features=max_features,
            aggregation_method=aggregation_method,
            lambda_value=lambda_value,
            seed=seed,
        )
        self._n_models = n_models
        self._max_features = max_features
        self._aggregation_method = aggregation_method
        self._lambda_value = lambda_value
        self._seed = seed

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "AdaptiveRandomForestRegressorModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        for xi, yi in zip(X, y):
            x_dict = self._to_dict(xi)
            self.model.learn_one(x_dict, float(yi))
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        preds = [
            _as_float(self.model.predict_one(self._to_dict(xi))) for xi in X
        ]
        return np.asarray(preds, dtype=float)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(
        self, x: Dict[str, float], y: Any
    ) -> "AdaptiveRandomForestRegressorModel":
        x = self._to_dict(x)
        self.model.learn_one(x, float(y))
        return self

    def predict_one(self, x: Dict[str, float]) -> float:
        x = self._to_dict(x)
        return _as_float(self.model.predict_one(x))

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "AdaptiveRandomForestRegressorModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"AdaptiveRandomForestRegressorModel(n_models={self._n_models}, "
            f"max_features={self._max_features!r}, "
            f"aggregation_method={self._aggregation_method!r}, "
            f"seed={self._seed})"
        )


class HoeffdingForestRegressorModel(BaseModel):
    """Ensemble of plain Hoeffding Tree regressors with online bagging — River.

    The regression twin of ``HoeffdingForestModel``, built the same way and for
    the same reason: a *passive* ensemble whose members never self-replace, so
    ECPF has full external control of the model lifecycle (save / restore /
    fade / merge) with no internal drift signal interfering.

    *   Each member is a vanilla ``HoeffdingTreeRegressor``.
    *   **Online bagging** with ``Poisson(λ)`` replication supplies diversity
        (Oza & Russell 2001), as in ARF.
    *   **Random feature subspace**: each tree is assigned a fixed random
        subset of the feature names at first ``learn_one``.  As in the
        classifier twin the mask is applied during *training only* — every
        member sees the full vector at prediction time.
    *   Exposes :meth:`predict_per_model`, the regression analogue of
        ``predict_proba_matrix``.

    Parameters
    ----------
    n_trees : int
        Number of trees in the forest.
    max_features : str or float or int or None
        Feature subsampling strategy per tree.  ``"sqrt"`` uses
        ``ceil(sqrt(n_features))`` features.
    lambda_poisson : float
        Poisson λ for online bagging.
    aggregation : str
        ``"mean"`` or ``"median"`` over the member predictions.  Default
        ``"mean"``: it is the centroid the ensemble-variance UQ signal is
        computed around, so point prediction and uncertainty describe the same
        distribution.  Switch to ``"median"`` if a heavy-tailed target makes
        robustness matter more than that coherence.
    grace_period, max_depth, delta, tau, leaf_prediction, leaf_model,
    model_selector_decay, min_samples_split, max_size
        Forwarded verbatim to each ``HoeffdingTreeRegressor``; see
        :class:`HoeffdingTreeRegressorModel`.
    seed : int or None
        Base random seed.  Tree ``i`` uses ``seed + i * 1000``, matching the
        classifier twin so paired classification/regression runs are
        comparable.
    """

    def __init__(
        self,
        n_trees: int = 10,
        max_features: Union[str, float, int, None] = "sqrt",
        lambda_poisson: float = 6.0,
        aggregation: str = "mean",
        grace_period: int = 200,
        max_depth: Optional[int] = None,
        delta: float = 1e-7,
        tau: float = 0.05,
        leaf_prediction: str = "adaptive",
        leaf_model: Any = None,
        model_selector_decay: float = 0.95,
        min_samples_split: int = 5,
        max_size: float = 500.0,
        seed: Optional[int] = 42,
    ) -> None:
        if aggregation not in ("mean", "median"):
            raise ValueError(
                "aggregation must be 'mean' or 'median', got %r" % (aggregation,)
            )
        self.n_trees = int(n_trees)
        self.max_features = max_features
        self.lambda_poisson = float(lambda_poisson)
        self.aggregation = aggregation
        self.seed = seed

        # Stored for cloning / fresh-model creation.
        # NOTE: as with the classifier twin, River's HoeffdingTreeRegressor
        # does NOT accept max_features — the random subspace is implemented
        # here by masking the feature dict during training.
        self._htr_kwargs = dict(
            grace_period=grace_period,
            max_depth=max_depth,
            delta=delta,
            tau=tau,
            leaf_prediction=leaf_prediction,
            leaf_model=leaf_model,
            model_selector_decay=model_selector_decay,
            min_samples_split=min_samples_split,
            max_size=max_size,
        )

        self.trees: List[tree.HoeffdingTreeRegressor] = []
        self._rngs: List[np.random.Generator] = []
        # Per-tree feature masks are lazily initialised on first learn_one
        # (the feature names are not known until then).
        self._feature_masks: List[Optional[List[str]]] = []
        for i in range(self.n_trees):
            self.trees.append(tree.HoeffdingTreeRegressor(**self._htr_kwargs))
            rng_seed = (seed + i * 1000) if seed is not None else None
            self._rngs.append(np.random.default_rng(rng_seed))
            self._feature_masks.append(None)

    # ------------------------------------------------------------------
    # Feature-subspace helpers
    # ------------------------------------------------------------------
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
    # Per-tree prediction access (key API for UQ)
    # ------------------------------------------------------------------
    def predict_per_model(self, x: Any) -> List[float]:
        """Return each member's point prediction for one sample.

        The regression analogue of
        ``HoeffdingForestModel.predict_proba_matrix``.  Ensemble variance over
        this vector is the epistemic-uncertainty scalar — the only one of the
        project's four UQ modes that has a meaning without a probability
        simplex.

        Parameters
        ----------
        x : dict or array-like
            Single sample.

        Returns
        -------
        list of float
            Exactly ``n_trees`` entries, in fixed member order, always finite.
            The length is invariant even before any tree has been trained (an
            untrained ``HoeffdingTreeRegressor`` predicts ``0.0``), so the
            variance a caller computes is never taken over a ragged sample.

        Notes
        -----
        As in the classifier twin, prediction uses the *full* feature dict: the
        random subspace exists to decorrelate training, and masking at
        inference would add a second, unwanted source of spread on top of the
        epistemic signal being measured.
        """
        x_dict = self._to_dict(x)
        return [_as_float(t.predict_one(x_dict)) for t in self.trees]

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "HoeffdingForestRegressorModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        for xi, yi in zip(X, y):
            self._learn_one_internal(self._to_dict(xi), float(yi))
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        return np.asarray([self.predict_one(xi) for xi in X], dtype=float)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Any, y: Any) -> "HoeffdingForestRegressorModel":
        self._learn_one_internal(self._to_dict(x), float(y))
        return self

    def predict_one(self, x: Any) -> float:
        """Aggregated point prediction across all trees."""
        preds = self.predict_per_model(x)
        if not preds:
            return 0.0
        if self.aggregation == "median":
            return float(np.median(preds))
        return float(np.mean(preds))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _learn_one_internal(self, x_dict: Dict[str, float], y: float) -> None:
        """Online bagging + random feature subspace.

        Each tree receives the sample ``k ~ Poisson(λ)`` times, with only its
        assigned subset of features visible during training.
        """
        # Lazy init: assign each tree a random feature subset.
        if self._feature_masks[0] is None and x_dict:
            self._init_feature_masks(sorted(x_dict.keys()))

        for i, t in enumerate(self.trees):
            k = int(self._rngs[i].poisson(self.lambda_poisson))
            if k == 0:
                continue
            mask = self._feature_masks[i]
            if mask is not None and len(mask) < len(x_dict):
                masked_x = {f: x_dict[f] for f in mask if f in x_dict}
            else:
                masked_x = x_dict
            for _ in range(k):
                t.learn_one(masked_x, y)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "HoeffdingForestRegressorModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"HoeffdingForestRegressorModel(n_trees={self.n_trees}, "
            f"max_features={self.max_features!r}, "
            f"lambda_poisson={self.lambda_poisson}, "
            f"aggregation={self.aggregation!r}, "
            f"seed={self.seed})"
        )
