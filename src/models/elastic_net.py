"""
elastic_net.py
==============
Model A — Logistic Regression with L1+L2 (Elastic Net) regularization,
built on top of River's online ``LogisticRegression``.

River's ``LogisticRegression`` natively supports ``learn_one`` so this is the
simplest wrapper: every public method delegates almost directly to River.

**Elastic Net implementation note:**
River >=0.21 does not support setting both ``l1`` and ``l2`` simultaneously on
``LogisticRegression``.  We work around this by:

*   Letting River handle the L2 (Ridge) penalty natively — this is applied
    inside the SGD gradient step.
*   Applying the L1 (Lasso) penalty ourselves via a **proximal
    soft-thresholding** step after each ``learn_one`` update.  This is the
    standard Elastic Net / proximal-gradient algorithm used by scikit-learn and
    other frameworks.

**Task-type limitation (enforced, not documented-and-forgotten):**
River's ``LogisticRegression`` is binary-only (``_multiclass`` is ``False``).
Fed a K>2 stream it does not crash — see :class:`MulticlassNotSupportedError`
for why that silence is the dangerous part — so this module raises instead.
"""

from __future__ import annotations

import math
import pickle
from pathlib import Path
from typing import Any, Dict, Set, Tuple, Union

import numpy as np
from river import linear_model, optim, preprocessing

from .base_model import BaseModel

#: ``model_adapter`` registry keys whose backends natively handle K>2 classes.
#: Named in the error message so the fix is a one-word config edit.
MULTICLASS_CAPABLE_BACKENDS: Tuple[str, ...] = ("rf", "ht", "hf")


class MulticlassNotSupportedError(ValueError):
    """A binary-only backend was handed a K>2 or continuous target.

    Subclasses ``ValueError`` so that any pre-existing ``except ValueError``
    handler upstream keeps working, while callers that want to react
    specifically (e.g. to suggest another backend) can catch this type.

    Why an exception rather than an automatic one-vs-rest wrapper: a silent
    fallback would change what ``ElasticNetModel`` means, and the published
    binary results were produced by the un-wrapped model.  The mismatch is a
    configuration error and must surface as one.
    """


class ElasticNetModel(BaseModel):
    """Online Logistic Regression with Elastic-Net regularization.

    The L2 term is delegated to River's built-in SGD, while the L1 term is
    applied as a proximal soft-thresholding step after each weight update.

    Parameters
    ----------
    l1 : float
        L1 (Lasso) regularization strength.  Applied via a manual proximal
        step after every ``learn_one`` call.
    l2 : float
        L2 (Ridge) regularization strength.  Handled natively by River.
    learning_rate : float
        Step size for the SGD optimizer.

    Raises
    ------
    MulticlassNotSupportedError
        From :meth:`fit` / :meth:`learn_one` as soon as the target is shown to
        be multi-class (a third distinct label) or continuous (a non-integral
        value).  Binary streams never trigger it.
    """

    def __init__(
        self,
        l1: float = 0.01,
        l2: float = 0.01,
        learning_rate: float = 0.01,
    ) -> None:
        self.model = linear_model.LogisticRegression(
            optimizer=optim.SGD(lr=learning_rate),
            l2=l2,
            l1=0.0,
        )
        self.scaler = preprocessing.StandardScaler()
        self._l1 = l1
        self._l2 = l2
        self._lr = learning_rate
        # Distinct finite labels observed so far.  Bounded at 3 entries by
        # construction: the third one raises, so this never grows with the
        # stream and costs one set lookup per update.
        self._seen_labels: Set[Any] = set()

    # ------------------------------------------------------------------
    # Task-type guard
    # ------------------------------------------------------------------
    @staticmethod
    def _unsupported(reason: str) -> "MulticlassNotSupportedError":
        """Build the actionable error, naming the backends that do work."""
        return MulticlassNotSupportedError(
            "ElasticNetModel cannot be trained on this target: %s. "
            "It wraps river.linear_model.LogisticRegression, which is "
            "binary-only (`_multiclass` is False): predict_proba_one() only "
            "ever returns the keys {False, True}, so predict_one() can never "
            "return a third class and the run would finish with a silently "
            "capped accuracy instead of an error. "
            "Use a multi-class-capable backend instead — model_type=%s "
            "(ARFClassifier / HoeffdingTreeClassifier / HoeffdingForest), or "
            "one of the regression models for a continuous target. "
            "One-vs-rest is deliberately NOT applied automatically: it would "
            "silently redefine this model and diverge from the published "
            "binary configuration."
            % (reason, " / ".join(repr(k) for k in MULTICLASS_CAPABLE_BACKENDS))
        )

    def _reject_unsupported_target(self, y: Any) -> None:
        """Fail loudly on any target this backend cannot actually represent.

        Two rejections, both checked before a single weight is touched so the
        model is never left half-updated:

        * **Continuous** — a finite non-integral label means regression, and a
          logistic link on a real-valued target is meaningless.
        * **Multi-class** — the third distinct label observed.  This is the
          earliest instant at which K>2 is *provable* from a stream, which is
          why the check lives here rather than in ``__init__``.

        Non-finite labels are skipped entirely.  A NaN target is a data defect
        rather than a task-type signal, and because ``float('nan') !=
        float('nan')`` each occurrence would otherwise count as a new distinct
        label and turn a corrupt row into a spurious multi-class error.

        Binary streams (y in {0, 1}, however typed) pass through untouched: the
        guard only reads *y* and never influences the SGD update.
        """
        labels = getattr(self, "_seen_labels", None)
        if labels is None:
            # Models pickled before this guard existed lack the attribute.
            labels = self._seen_labels = set()

        try:
            value = float(y)
        except (TypeError, ValueError):
            # Non-numeric (string / categorical) label: cardinality is still a
            # valid multi-class test, integrality is not.
            key: Any = str(y)
        else:
            if not math.isfinite(value):
                return
            if not value.is_integer():
                raise self._unsupported(
                    "target value %r is not integral, i.e. the stream is a "
                    "regression task" % (y,)
                )
            key = value

        if key in labels:
            return
        labels.add(key)
        if len(labels) > 2:
            raise self._unsupported(
                "%d distinct labels seen (%s), i.e. the stream is multi-class"
                % (len(labels), sorted(labels, key=repr))
            )

    @staticmethod
    def supports_task(task_spec: Any) -> bool:
        """Whether *task_spec* is a task this model can legitimately run.

        Duck-typed on purpose: it reads ``.task_type`` (a ``str``-valued Enum in
        ``src/task.py``, so plain string comparison works) without importing
        ``src.task``, keeping ``src/models`` free of an upward dependency.
        """
        task_type = getattr(task_spec, "task_type", task_spec)
        return str(getattr(task_type, "value", task_type)) == "binary"

    @classmethod
    def assert_task_supported(cls, task_spec: Any) -> None:
        """Fail at configuration time rather than mid-stream.

        The per-sample guard cannot fire until the third distinct label shows
        up, which may be thousands of instances into a run.  When the caller
        already knows the task (``resolve_task`` output), calling this first
        turns that into an immediate, cheap failure.
        """
        if cls.supports_task(task_spec):
            return
        describe = getattr(task_spec, "describe", None)
        detail = describe() if callable(describe) else repr(task_spec)
        raise cls._unsupported("task is %s, not binary" % detail)

    # ------------------------------------------------------------------
    # L1 proximal step (Elastic Net)
    # ------------------------------------------------------------------
    def _apply_l1_proximal(self) -> None:
        """Apply soft-thresholding to the model weights for L1 regularization.

        For each weight w_i, the proximal update is::

            w_i ← sign(w_i) * max(|w_i| - λ₁ * lr, 0)
        """
        if self._l1 <= 0:
            return
        threshold = self._l1 * self._lr
        weights = self.model._weights
        for feature, w in list(weights.items()):
            shrunk = float(np.sign(w) * max(abs(w) - threshold, 0.0))
            if shrunk == 0.0:
                del weights[feature]
            else:
                weights[feature] = shrunk

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "ElasticNetModel":
        X = self._to_numpy(X)
        y = np.asarray(y).ravel()
        # Scan the whole warm-up batch first: it already proves the task type,
        # so an unsupported stream fails before any weight or scaler statistic
        # is touched instead of half-way through the batch.
        for yi in y:
            self._reject_unsupported_target(yi)
        for xi, yi in zip(X, y):
            x_dict = self._to_dict(xi)
            self.scaler.learn_one(x_dict)
            x_dict = self.scaler.transform_one(x_dict)
            self.model.learn_one(x_dict, yi)
            self._apply_l1_proximal()
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        preds = []
        for xi in X:
            x_dict = self._to_dict(xi)
            x_dict = self.scaler.transform_one(x_dict)
            proba = self.model.predict_proba_one(x_dict)
            if proba:
                preds.append(max(proba, key=proba.get))
            else:
                preds.append(0)
        return np.array(preds)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "ElasticNetModel":
        self._reject_unsupported_target(y)
        x = self._to_dict(x)
        self.scaler.learn_one(x)
        x = self.scaler.transform_one(x)
        self.model.learn_one(x, y)
        self._apply_l1_proximal()
        return self

    def predict_one(self, x: Dict[str, float]) -> Any:
        x = self._to_dict(x)
        x = self.scaler.transform_one(x)
        proba = self.model.predict_proba_one(x)
        if proba:
            return max(proba, key=proba.get)
        return 0

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "ElasticNetModel":
        with open(path, "rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(obj).__name__}")
        return obj

    def __repr__(self) -> str:
        return (
            f"ElasticNetModel(l1={self._l1}, l2={self._l2}, lr={self._lr})"
        )
