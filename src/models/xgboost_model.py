"""
xgboost_model.py
================
Model C — XGBoost gradient-boosted trees with a **buffer-based incremental
learning** strategy.

XGBoost is a batch algorithm and has no native ``learn_one`` method.  We
bridge this gap with the following approach:

1.  Incoming ``learn_one`` calls are accumulated in an in-memory buffer.
2.  Once the buffer reaches ``buffer_size`` samples, we trigger an incremental
    ``xgb.train()`` call using the ``xgb_model`` parameter, which continues
    training from the existing booster rather than starting from scratch.
3.  This keeps the model up-to-date while amortising the cost of tree
    construction across many samples.

Task types
----------
The booster objective used to be the hard-coded constant ``binary:logistic``,
which makes XGBoost reject any label outside {0, 1}::

    XGBoostError: label must be in [0,1] for logistic regression

so a K>2 stream or a continuous target died inside ``fit``.  The objective is
now *derived* from the labels the model has actually observed (see
:meth:`XGBoostModel._resolve_task`), or from an explicit ``task_type`` /
``n_classes`` declaration when the caller has a :class:`~src.task.TaskSpec` on
hand.

**A K=2 stream is deliberately left on exactly the old code path**: the
resolver returns ``binary:logistic`` and hands back the very same parameter
dict object, so the booster built for a binary run is bit-identical to the one
the published binary results were produced with.

Why the label *range* and not the label *cardinality*
-----------------------------------------------------
:func:`src.task.infer_task` decides binary-vs-multiclass from the number of
distinct labels, which is the right call on a whole dataset but is unsafe here:
this model resolves its objective from a 50-sample buffer, and a buffer that
happens to be all-zeros has cardinality 1 — which would flip a perfectly
ordinary binary run onto ``multi:softmax`` with ``num_class=1``.  Label
statistics are therefore accumulated across every batch ever seen, and the
binary-vs-multiclass split is made on ``max(label)``: anything that stays
within {0, 1} is binary, which is exactly the historical behaviour.
"""

from __future__ import annotations

import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import xgboost as xgb

from ..task import TaskType
from .base_model import BaseModel

#: Objective for a 2-class stream.  Duplicated from the historical default on
#: purpose — a binary run must not observe any change at all.
_BINARY_OBJECTIVE = "binary:logistic"
_MULTICLASS_OBJECTIVE = "multi:softmax"
_REGRESSION_OBJECTIVE = "reg:squarederror"

#: ``(objective, num_class)`` — identifies the booster currently held, so an
#: incremental update can tell whether it may continue from it.
_ObjectiveKey = Tuple[str, Optional[int]]


class XGBoostModel(BaseModel):
    """XGBoost model with buffer-based online updates.

    Parameters
    ----------
    params : dict or None
        XGBoost booster parameters.  When this dict carries an explicit
        ``"objective"`` key it is honoured verbatim and never rewritten — the
        caller is assumed to know what they are doing.
    num_boost_round : int
        Number of boosting rounds for initial ``fit`` and each incremental
        update.
    buffer_size : int
        How many ``learn_one`` samples to accumulate before triggering an
        incremental training step.
    task_type : str, TaskType or None
        Declared task.  ``None`` (the default) means "infer from the labels",
        which reproduces the historical binary behaviour on binary data.
    n_classes : int or None
        Declared number of classes.  Only consulted for a multi-class task; it
        raises ``num_class`` above what the observed labels alone would imply,
        which matters when a rare class has not been seen yet.
    """

    def __init__(
        self,
        params: Optional[Dict[str, Any]] = None,
        num_boost_round: int = 50,
        buffer_size: int = 50,
        task_type: Optional[Union[str, TaskType]] = None,
        n_classes: Optional[int] = None,
    ) -> None:
        self.params: Dict[str, Any] = params or {
            "objective": _BINARY_OBJECTIVE,
            "eval_metric": "logloss",
            "max_depth": 4,
            "learning_rate": 0.1,
            "verbosity": 0,
        }
        # Distinguishes "the caller pinned an objective" from "this is our
        # default dict", which happens to contain one.  Without the flag a
        # save/load round-trip would freeze the model into whatever objective
        # it last used, because ``load`` feeds ``self.params`` back in.
        self._objective_is_explicit: bool = bool(params) and "objective" in params
        self.num_boost_round = num_boost_round
        self.buffer_size = buffer_size
        self.task_type: Optional[TaskType] = (
            TaskType(task_type) if task_type is not None else None
        )
        self.n_classes: Optional[int] = int(n_classes) if n_classes is not None else None

        self._booster: Optional[xgb.Booster] = None
        self._feature_names: Optional[List[str]] = None
        self._buffer_X: List[np.ndarray] = []
        self._buffer_y: List[float] = []

        # Cumulative label statistics — see the module docstring for why these
        # are running aggregates rather than a per-batch inference.
        self._label_min: Optional[float] = None
        self._label_max: Optional[float] = None
        self._labels_integral: bool = True
        self._active_objective: Optional[_ObjectiveKey] = None

    # ------------------------------------------------------------------
    # Task resolution
    # ------------------------------------------------------------------
    def _observe_labels(self, y: np.ndarray) -> None:
        """Fold a batch of labels into the running min / max / integrality."""
        arr = np.asarray(y, dtype=np.float64).ravel()
        finite = arr[np.isfinite(arr)]
        if finite.size == 0:
            return
        lo, hi = float(finite.min()), float(finite.max())
        self._label_min = lo if self._label_min is None else min(self._label_min, lo)
        self._label_max = hi if self._label_max is None else max(self._label_max, hi)
        if self._labels_integral and not bool(np.all(np.mod(finite, 1.0) == 0.0)):
            self._labels_integral = False

    def _resolve_task(self) -> Tuple[TaskType, Optional[int]]:
        """Return ``(task_type, num_class)`` implied by declaration + labels.

        ``num_class`` is ``None`` for anything that is not multi-class.  For a
        multi-class task it is ``max(label) + 1`` rather than the number of
        distinct labels, because XGBoost requires labels to live in
        ``[0, num_class)``: a stream labelled {0, 2, 5} needs ``num_class=6``,
        and paying for three unused output groups is cheaper (and far less
        error-prone) than maintaining a stateful label remapping across
        incremental updates.
        """
        declared = self.task_type
        if declared is TaskType.REGRESSION:
            return TaskType.REGRESSION, None
        if self._label_min is None:
            # Nothing observed yet; the historical default is the safe answer
            # and no booster exists to be affected by it.
            return TaskType.BINARY, None

        if not self._labels_integral:
            if declared is not None:
                raise ValueError(
                    "task_type=%r was declared but the observed labels are not "
                    "integral (min=%r, max=%r); a classification objective "
                    "cannot consume a continuous target."
                    % (declared.value, self._label_min, self._label_max)
                )
            return TaskType.REGRESSION, None

        if self._label_min < 0:
            raise ValueError(
                "XGBoost classification requires labels in [0, K-1] but the "
                "observed minimum label is %r. Encode the classes as 0..K-1, "
                "or declare task_type='regression' if the target is continuous."
                % (self._label_min,)
            )

        k = max(int(round(self._label_max)) + 1, self.n_classes or 0)
        if declared is TaskType.BINARY and k > 2:
            warnings.warn(
                "task_type='binary' was declared but labels up to %r were "
                "observed; following the data and switching to a %d-class "
                "objective." % (self._label_max, k),
                RuntimeWarning,
                stacklevel=3,
            )
        elif k <= 2 and declared is not TaskType.MULTICLASS:
            # {0}, {1} and {0,1} all land here — the untouched binary path.
            return TaskType.BINARY, None
        return TaskType.MULTICLASS, max(k, 2)

    def _effective_params(self) -> Tuple[Dict[str, Any], _ObjectiveKey]:
        """Booster params for the current task, plus the key identifying them."""
        if self._objective_is_explicit:
            objective = str(self.params.get("objective"))
            num_class = self.params.get("num_class")
            return self.params, (objective, num_class)

        task, num_class = self._resolve_task()
        if task is TaskType.BINARY:
            if self.params.get("objective") == _BINARY_OBJECTIVE:
                # Hand back the *same object* the historical code trained on.
                return self.params, (_BINARY_OBJECTIVE, None)
            params = dict(self.params)
            params.pop("num_class", None)
            params["objective"] = _BINARY_OBJECTIVE
            params.setdefault("eval_metric", "logloss")
            return params, (_BINARY_OBJECTIVE, None)

        params = dict(self.params)
        if task is TaskType.MULTICLASS:
            params["objective"] = _MULTICLASS_OBJECTIVE
            params["num_class"] = int(num_class)
            if params.get("eval_metric") in (None, "logloss"):
                params["eval_metric"] = "mlogloss"
            return params, (_MULTICLASS_OBJECTIVE, int(num_class))

        params["objective"] = _REGRESSION_OBJECTIVE
        params.pop("num_class", None)
        if params.get("eval_metric") in (None, "logloss", "mlogloss"):
            params["eval_metric"] = "rmse"
        return params, (_REGRESSION_OBJECTIVE, None)

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "XGBoostModel":
        X = self._to_numpy(X)
        y = np.asarray(y, dtype=np.float32).ravel()
        self._observe_labels(y)
        self._feature_names = [f"f{i}" for i in range(X.shape[1])]
        dtrain = xgb.DMatrix(X, label=y, feature_names=self._feature_names)
        params, key = self._effective_params()
        self._booster = xgb.train(
            params,
            dtrain,
            num_boost_round=self.num_boost_round,
        )
        self._active_objective = key
        self._buffer_X.clear()
        self._buffer_y.clear()
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        if self._booster is None:
            return self._cold_start_predictions(X.shape[0])
        dmat = xgb.DMatrix(X, feature_names=self._feature_names)
        return self._postprocess(self._booster.predict(dmat))

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "XGBoostModel":
        x_arr = self._dict_to_array(x)
        self._buffer_X.append(x_arr)
        self._buffer_y.append(float(y))

        if len(self._buffer_X) >= self.buffer_size:
            self._flush_buffer()
        return self

    def predict_one(self, x: Dict[str, float]) -> Any:
        x_arr = self._dict_to_array(x).reshape(1, -1)
        if self._booster is None:
            return self._cold_start_predictions(1)[0].item()
        dmat = xgb.DMatrix(x_arr, feature_names=self._feature_names)
        return self._postprocess(self._booster.predict(dmat))[0].item()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _cold_start_predictions(self, n: int) -> np.ndarray:
        """Placeholder output before any booster exists.

        Class 0 for classification (unchanged), 0.0 for regression — returning
        an integer there would make the residual look artificially discrete.
        """
        if self._resolve_task()[0] is TaskType.REGRESSION:
            return np.zeros(n, dtype=float)
        return np.zeros(n, dtype=int)

    def _postprocess(self, raw: np.ndarray) -> np.ndarray:
        """Turn raw booster output into hard labels / real values.

        The decision is driven by the objective the *held booster* was built
        with rather than by a fresh resolution, so a model restored from disk
        decodes its own output correctly even before it sees a label.
        """
        objective = (
            self._active_objective[0]
            if self._active_objective is not None
            else self._effective_params()[1][0]
        )
        if objective.startswith("multi:"):
            # ``multi:softmax`` already returns the winning class index;
            # ``multi:softprob`` returns the full simplex.
            if raw.ndim == 2:
                return raw.argmax(axis=1).astype(int)
            return np.rint(raw).astype(int)
        if objective.startswith("binary:"):
            return (raw >= 0.5).astype(int)
        return raw.astype(float)

    def _dict_to_array(self, x: Dict[str, float]) -> np.ndarray:
        if self._feature_names is None:
            self._feature_names = sorted(x.keys())
        return np.array([x.get(k, 0.0) for k in self._feature_names], dtype=np.float32)

    def _flush_buffer(self) -> None:
        X = np.vstack(self._buffer_X)
        y = np.array(self._buffer_y, dtype=np.float32)
        self._observe_labels(y)
        dtrain = xgb.DMatrix(X, label=y, feature_names=self._feature_names)
        params, key = self._effective_params()

        # A booster trained under a different objective has a different number
        # of output groups, so it cannot be continued from — XGBoost would
        # either error or silently mis-shape the update.  This can only trigger
        # when the task changes underneath us (e.g. class 2 appears in a stream
        # that looked binary for its first buffer); a genuine binary run never
        # leaves ``binary:logistic`` and so never discards its booster.
        resume = self._booster
        if resume is not None and self._active_objective != key:
            warnings.warn(
                "Observed labels changed the XGBoost objective from %r to %r; "
                "the existing booster cannot be extended and is being rebuilt "
                "from the current buffer. Declare task_type/n_classes up front "
                "to avoid this."
                % (self._active_objective, key),
                RuntimeWarning,
                stacklevel=3,
            )
            resume = None

        self._booster = xgb.train(
            params,
            dtrain,
            num_boost_round=self.num_boost_round,
            xgb_model=resume,
        )
        self._active_objective = key
        self._buffer_X.clear()
        self._buffer_y.clear()

    def flush(self) -> "XGBoostModel":
        """Force-flush the buffer even if it is not full."""
        if self._buffer_X:
            self._flush_buffer()
        return self

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "params": self.params,
            "num_boost_round": self.num_boost_round,
            "buffer_size": self.buffer_size,
            "feature_names": self._feature_names,
            "buffer_X": self._buffer_X,
            "buffer_y": self._buffer_y,
            "objective_is_explicit": self._objective_is_explicit,
            "task_type": self.task_type.value if self.task_type else None,
            "n_classes": self.n_classes,
            "label_min": self._label_min,
            "label_max": self._label_max,
            "labels_integral": self._labels_integral,
            "active_objective": self._active_objective,
        }
        booster_bytes: Optional[bytes] = None
        if self._booster is not None:
            booster_bytes = self._booster.save_raw()
        state["booster_raw"] = booster_bytes

        with open(path, "wb") as f:
            pickle.dump(state, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "XGBoostModel":
        with open(path, "rb") as f:
            state = pickle.load(f)
        obj = cls(
            params=state["params"],
            num_boost_round=state["num_boost_round"],
            buffer_size=state["buffer_size"],
            task_type=state.get("task_type"),
            n_classes=state.get("n_classes"),
        )
        # ``params`` always contains an objective by the time it is persisted,
        # so the constructor's heuristic would wrongly report "explicit".
        # Pre-task-type checkpoints are binary by construction, hence False.
        obj._objective_is_explicit = bool(state.get("objective_is_explicit", False))
        obj._feature_names = state["feature_names"]
        obj._buffer_X = state["buffer_X"]
        obj._buffer_y = state["buffer_y"]
        obj._label_min = state.get("label_min")
        obj._label_max = state.get("label_max")
        obj._labels_integral = bool(state.get("labels_integral", True))
        obj._active_objective = state.get("active_objective")
        if state["booster_raw"] is not None:
            obj._booster = xgb.Booster()
            obj._booster.load_model(bytearray(state["booster_raw"]))
            if obj._active_objective is None:
                # Checkpoint written before objectives were tracked.
                obj._active_objective = (_BINARY_OBJECTIVE, None)
        return obj

    def __repr__(self) -> str:
        buf = len(self._buffer_X)
        trained = self._booster is not None
        objective = self._active_objective[0] if self._active_objective else "unset"
        return (
            f"XGBoostModel(objective={objective}, buffer={buf}/{self.buffer_size}, "
            f"trained={trained})"
        )
