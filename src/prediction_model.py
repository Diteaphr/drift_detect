"""
Prediction model wrapper: supports linear (retrain) and nonlinear (fine-tune)
for incremental adaptation from the model pool.

Task coverage
-------------
The wrapper was originally written against a binary ``{0, 1}`` target and hard-
coded that assumption in three places, each of which is a hard failure the
moment ``src/task.py`` reports something else:

*   ``partial_fit`` was handed the literal ``np.array([0, 1])``.  sklearn locks
    the label set in on the first call and then *validates* every later
    ``classes`` argument against it, so a 3-class stream raises
    ``ValueError: classes=array([0, 1]) is not the same as on last call to
    partial_fit``.  That is a ``ValueError``, so the surrounding
    ``except TypeError`` never saw it.
*   the ``predict_proba`` fallback allocated ``(n, 2)`` and wrote to column
    ``int(label)``, which both truncates ``K > 2`` and assumes the labels *are*
    their own column indices.
*   there was no regressor at all, so a continuous target died in ``fit`` with
    ``ValueError: Unknown label type``.

This module now learns the label set from data and remembers it, indexes
probability columns by position rather than by label value, and adds an
``"sgdr"`` model type backed by :class:`sklearn.linear_model.SGDRegressor`.

Binary compatibility
--------------------
The published results in this repository were produced on 40 binary streams, so
the binary path is *pinned*, not merely expected to keep working: whenever every
label observed so far lies in ``{0, 1}``, ``partial_fit`` receives exactly the
same :data:`_LEGACY_BINARY_CLASSES` array the old code passed unconditionally.
This matters for more than tidiness -- ``src/ecpf.py`` builds a fresh wrapper and
may drive it with a *single-sample* ``fine_tune`` before it ever sees both
labels, and learning the class set from that one sample would collapse the model
to a single class.  See :meth:`PredictionModel._partial_fit_classes`.

The learned-class machinery is therefore reachable only on streams whose labels
leave ``{0, 1}`` -- streams that previously raised.

Declaring beats inferring
-------------------------
That pin only rescues the ``{0, 1}`` case, so on a K > 2 stream the same
single-sample-first-fit hazard is live and unguarded: whichever label arrives
first becomes the estimator's entire ``classes_``, forever.  Inference cannot
fix this -- by the time a second label shows up sklearn has already committed
and offers no way to widen.  The label set must be *declared* before the first
fit, which is what :func:`needs_class_declaration` gates and what
``src/pipeline.py`` (``declarable_classes``) and ``src/ecpf.py``
(``_fresh_model``) now do from ``TaskSpec.classes``, a set resolved over the
whole target array.
"""

import logging
from typing import Any, Optional, Sequence

import numpy as np
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


#: The exact ``classes`` array the pre-multiclass code passed on every
#: ``partial_fit``.  Kept as a module constant, and kept *int-typed*, so the
#: binary code path is byte-for-byte what produced the published results.
_LEGACY_BINARY_CLASSES = np.array([0, 1])

#: ``model_type`` values that select a regressor instead of a classifier.
_REGRESSOR_TYPES = frozenset({"sgdr"})


def _is_legacy_binary(classes: Optional[np.ndarray]) -> bool:
    """True when *classes* is a subset of ``{0, 1}`` -- the pinned legacy path."""
    if classes is None or classes.size > 2:
        return False
    try:
        return bool(np.all(np.isin(classes, _LEGACY_BINARY_CLASSES)))
    except TypeError:
        # Non-numeric labels (string classes) are never the legacy path.
        return False


def needs_class_declaration(classes: Optional[Sequence[Any]]) -> bool:
    """Should this label set be *declared* to every wrapper the pipeline builds?

    Answer: only when it leaves ``{0, 1}``.

    Inside ``{0, 1}`` a declaration would buy nothing -- ``_partial_fit_classes``
    already pins :data:`_LEGACY_BINARY_CLASSES` unconditionally on that path --
    but it *would* make :meth:`PredictionModel._needs_seeded_fit` reachable on
    the 40 published binary streams, rerouting ``fit`` through a single-epoch
    ``partial_fit`` and changing their numbers.  So the binary path is left
    exactly as it was, and the declaration is switched on precisely for the label
    sets that have no pin and therefore break (see :func:`_is_legacy_binary`).

    Callers pass ``TaskSpec.classes``, which is computed over the *whole* target
    array, so declaring it removes any dependence on which labels happen to
    arrive first.
    """
    if classes is None:
        return False
    arr = np.unique(np.asarray(classes).ravel())
    if arr.size == 0:
        return False
    return not _is_legacy_binary(arr)


def _make_linear_model():
    try:
        from sklearn.linear_model import SGDClassifier
        return SGDClassifier(max_iter=500, warm_start=True, random_state=42, tol=1e-3, loss='log_loss')
    except ImportError:
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression()


def _make_nonlinear_model():
    try:
        from sklearn.naive_bayes import GaussianNB
        # Gaussian Naive Bayes supports partial_fit and can model non-linear boundaries probabilistically.
        return GaussianNB()
    except ImportError:
        return _make_linear_model()


def _make_regressor_model():
    """Build the regression counterpart of :func:`_make_linear_model`.

    ``SGDRegressor`` is chosen for symmetry with the linear classifier: same
    solver family, same ``partial_fit`` support (so ``fine_tune`` stays a real
    incremental update rather than a hidden full refit), and the same
    ``random_state`` so runs remain reproducible.  ``loss`` is deliberately left
    at its default, whose *name* changed across sklearn versions
    (``squared_loss`` -> ``squared_error``) even though the objective did not.
    """
    from sklearn.linear_model import SGDRegressor
    return SGDRegressor(max_iter=500, warm_start=True, random_state=42, tol=1e-3)


class PredictionModel:
    """
    Wrapper around a classifier. Supports:
    - predict(X)
    - predict_proba(X)
    - retrain (linear): fit from scratch on new data
    - fine_tune (nonlinear): partial_fit / additional fit on new data

    Parameters
    ----------
    model_type : str, default="linear"
        ``"linear"`` and ``"nonlinear"`` select classifiers (unchanged);
        ``"sgdr"`` selects a regressor.  Any other value keeps the historical
        behaviour of falling through to the nonlinear classifier.
    classes : sequence, optional
        Full label set, when the caller already knows it (e.g. from
        ``TaskSpec.classes``, which is computed over the whole target array).
        Declaring it up front is the only way to be safe on a multi-class stream
        whose first training batch does not happen to contain every label,
        because sklearn's ``partial_fit`` cannot widen its label set afterwards.
        Ignored for regressors.
    """

    def __init__(self, model_type: str = "linear", classes: Optional[Sequence[Any]] = None):
        self.model_type = model_type.lower()
        self.scaler = StandardScaler()
        self._scaler_fitted = False
        self._is_regressor = self.model_type in _REGRESSOR_TYPES
        # Running union of every label seen (or declared).  ``None`` means
        # "nothing observed yet".
        self._classes: Optional[np.ndarray] = None
        # Kept separately because ``fit`` resets the *learned* set (sklearn's
        # own ``classes_`` is reset by ``fit``) but must not forget a set the
        # caller declared from the whole target array.
        self._declared_classes: Optional[np.ndarray] = None
        # Labels we have already complained about, so a long stream warns once
        # per novel label instead of once per instance.
        self._unseen_label_warned: set = set()

        self._model = self._build_estimator()

        if classes is not None and not self._is_regressor:
            self.set_classes(classes)

    def _build_estimator(self) -> Any:
        """Construct a pristine estimator for this ``model_type``."""
        if self._is_regressor:
            return _make_regressor_model()
        if self.model_type == "linear":
            return _make_linear_model()
        return _make_nonlinear_model()

    # ------------------------------------------------------------------
    # Task introspection
    # ------------------------------------------------------------------
    @property
    def is_regressor(self) -> bool:
        """True when the wrapped estimator predicts a continuous target."""
        return self._is_regressor

    @property
    def classes(self) -> Optional[np.ndarray]:
        """Label set learned from data (or declared), or ``None`` for a regressor."""
        return self._classes

    def set_classes(self, classes: Sequence[Any]) -> None:
        """Declare the full label set before training.

        Use when the label set is known from the whole target array but a given
        training batch may not contain all of it.
        """
        if self._is_regressor:
            raise ValueError("a regressor has no class set; model_type=%r" % self.model_type)
        self._declared_classes = np.unique(np.asarray(classes).ravel())
        self._classes = self._declared_classes

    # ------------------------------------------------------------------
    # Internal class-set bookkeeping
    # ------------------------------------------------------------------
    def _observe_classes(self, y: np.ndarray) -> None:
        """Fold the labels in *y* into the remembered set.

        Kept as a running *union* rather than a per-call ``np.unique`` because
        ``fine_tune`` is normally called one sample at a time: any single call
        sees a strict subset of the classes, and sklearn demands the full set
        every time.
        """
        seen = np.unique(y)
        self._classes = seen if self._classes is None else np.union1d(self._classes, seen)

    @staticmethod
    def _is_binary_label_set(classes: np.ndarray) -> bool:
        """True when *classes* is a subset of ``{0, 1}`` -- the pinned path.

        Note what this guard does *not* cover, and why it was never enough on its
        own: it only rescues a wrapper whose observed labels sit inside
        ``{0, 1}``.  On a K > 2 stream a fresh wrapper trained from a
        single-label batch observes e.g. ``{2}``, falls through to the learned
        set, and sklearn locks ``classes_`` to that one label for good.  The full
        set has to be *declared*; see :func:`needs_class_declaration`.
        """
        return _is_legacy_binary(classes)

    def _partial_fit_classes(self) -> np.ndarray:
        """Choose the ``classes`` array to hand sklearn's ``partial_fit``.

        Three cases, in priority order:

        1. Nothing observed, or everything observed lies in ``{0, 1}``: return
           the legacy constant.  This keeps binary runs bit-identical *and*
           keeps a fresh wrapper trained one sample at a time from collapsing
           to whichever single label arrived first.
        2. The estimator has already committed to a ``classes_``: return that
           array verbatim, since sklearn compares against it by value and any
           other array can only fail the check.
        3. Otherwise: return the union learned so far.
        """
        if self._classes is None or self._is_binary_label_set(self._classes):
            return _LEGACY_BINARY_CLASSES
        locked = getattr(self._model, "classes_", None)
        if locked is not None:
            return np.asarray(locked)
        return self._classes

    def _needs_seeded_fit(self, y: np.ndarray) -> bool:
        """True when ``fit`` must be routed through ``partial_fit`` to keep a
        declared label that this batch does not contain.

        Gated on an explicit declaration, so the default
        ``PredictionModel(model_type=...)`` construction used by the published
        binary runs can never reach it.
        """
        if self._is_regressor or self._declared_classes is None:
            return False
        if not hasattr(self._model, "partial_fit"):
            return False
        return not bool(np.isin(self._declared_classes, np.unique(y)).all())

    def _partial_fit_dropping_novel(self, X: np.ndarray, y: np.ndarray, exc: ValueError) -> None:
        """Recover from a label the estimator cannot accept, or re-raise.

        sklearn's ``partial_fit`` cannot widen a committed label set, so a class
        that first appears mid-stream is unrepresentable.  Dropping those few
        samples (loudly) keeps a long run alive, whereas propagating would throw
        away the whole experiment.  If the ``ValueError`` was not about unknown
        labels it is re-raised untouched -- this handler must not mask real bugs.
        """
        known = getattr(self._model, "classes_", None)
        if known is None:
            raise exc
        mask = np.isin(y, known)
        if mask.all():
            raise exc  # not a novel-label problem
        for label in np.unique(y[~mask]):
            if label not in self._unseen_label_warned:
                self._unseen_label_warned.add(label)
                logger.warning(
                    "PredictionModel: label %r appeared after partial_fit committed to "
                    "classes=%r; its samples are being skipped. Declare the full label "
                    "set up front via PredictionModel(classes=...) or set_classes().",
                    label, known,
                )
        if mask.any():
            self._model.partial_fit(X[mask], y[mask], classes=np.asarray(known))

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------
    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if self._scaler_fitted:
            X = self.scaler.transform(X)
        return self._model.predict(X).ravel()

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns probability estimates for classification. Useful for future Uncertainty Module."""
        if self._is_regressor:
            raise NotImplementedError(
                "predict_proba is undefined for a regressor (model_type=%r). The "
                "uncertainty measures that consume a probability simplex "
                "(mi_like / predictive_entropy / vote_disagreement) have no "
                "regression analogue; use variance-based uncertainty instead."
                % self.model_type
            )
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if self._scaler_fitted:
            X = self.scaler.transform(X)
        if hasattr(self._model, "predict_proba"):
            return self._model.predict_proba(X)
        else:
            # Fallback if model doesn't support probability: emit a one-hot row.
            # The column is the label's *position* in the class set, not
            # ``int(label)`` -- labels need be neither 0..K-1 nor even numeric,
            # and the old ``probs[i, int(p)]`` both truncated K > 2 and indexed
            # out of bounds for any label >= 2.
            preds = self._model.predict(X).ravel()
            classes = self._classes
            if classes is None:
                classes = getattr(self._model, "classes_", None)
            if classes is None:
                classes = np.unique(preds)
            classes = np.asarray(classes)
            probs = np.zeros((len(preds), classes.size), dtype=float)
            for i, p in enumerate(preds):
                hits = np.flatnonzero(classes == p)
                if hits.size:
                    probs[i, hits[0]] = 1.0
                # A prediction outside the known class set leaves an all-zero
                # row, which is honest about "no mass assigned" rather than
                # crashing or silently mislabelling a column.
            return probs

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def fit(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        X = self.scaler.fit_transform(X)
        self._scaler_fitted = True
        if self._needs_seeded_fit(y):
            # sklearn's ``fit`` re-derives ``classes_`` from *y* alone and gives
            # no way to widen it, so a warm-up batch that happens to miss a
            # declared label would lock that label out of the model for good.
            # ``partial_fit`` is the only entry point that accepts the full set,
            # so seed through it -- on a *fresh* estimator, to preserve the
            # "fit trains from scratch" contract that ``retrain`` relies on.
            # Reachable only when the caller explicitly declared a class set.
            self._model = self._build_estimator()
            self._model.partial_fit(X, y, classes=self._declared_classes)
        else:
            self._model.fit(X, y)
        if not self._is_regressor:
            # Record what sklearn actually committed to, so the next
            # partial_fit hands back an array that passes its identity check.
            # ``fit`` resets ``classes_``, so this replaces rather than unions.
            fitted = getattr(self._model, "classes_", None)
            fitted = np.asarray(fitted) if fitted is not None else np.unique(y)
            self._classes = (
                fitted if self._declared_classes is None
                else np.union1d(self._declared_classes, fitted)
            )
        return self

    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if not self._scaler_fitted:
            X = self.scaler.fit_transform(X)
            self._scaler_fitted = True
        else:
            # Incrementally update scaler
            self.scaler.partial_fit(X)
            X = self.scaler.transform(X)

        if hasattr(self._model, "partial_fit"):
            if self._is_regressor:
                # A regressor has no label set; passing ``classes`` is a TypeError.
                self._model.partial_fit(X, y)
                return self
            self._observe_classes(y)
            classes = self._partial_fit_classes()
            try:
                self._model.partial_fit(X, y, classes=classes)
            except TypeError:
                self._model.partial_fit(X, y)  # non-classifier fallback
            except ValueError as exc:
                self._partial_fit_dropping_novel(X, y, exc)
        else:
            self._model.fit(X, y)
        return self

    def retrain(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        """Full retrain (for linear): fit from scratch."""
        return self.fit(X, y)

    def fine_tune(self, X: np.ndarray, y: np.ndarray) -> "PredictionModel":
        """Incremental update (for nonlinear): partial_fit."""
        return self.partial_fit(X, y)

    # ------------------------------------------------------------------
    # Model pool / ECPF plumbing
    # ------------------------------------------------------------------
    def get_model(self) -> Any:
        return self._model

    def set_model(self, model: Any) -> None:
        """Install a foreign estimator (model-pool reuse, ECPF leader swap).

        Adopts the incoming estimator's committed ``classes_`` as well: after a
        swap, ``self._classes`` would otherwise describe the *discarded* model
        and the next ``partial_fit`` would pass an array the new estimator
        rejects.  ``src/ecpf.py`` transplants ``scaler`` / ``_scaler_fitted``
        around this call for the same reason.

        ``_is_regressor`` is intentionally *not* re-derived from *model*: it
        follows ``model_type``, which is fixed for the lifetime of the wrapper,
        and every caller (ECPF leader swap, model-pool reuse) swaps in an
        estimator built from the same ``model_type``.
        """
        self._model = model
        if self._is_regressor:
            return
        adopted = getattr(model, "classes_", None)
        if adopted is not None:
            adopted = np.asarray(adopted)
            # A declared set is knowledge about the *stream*, not about the
            # estimator being discarded, so a swap must not narrow it. Without
            # the union, an incoming estimator that saw fewer labels would drag
            # this wrapper back onto the drop-novel path. No-op for the binary
            # runs, where nothing is ever declared.
            self._classes = (
                adopted if self._declared_classes is None
                else np.union1d(self._declared_classes, adopted)
            )
