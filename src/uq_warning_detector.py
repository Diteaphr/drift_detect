"""
uq_warning_detector.py
======================
UQ-based early-warning detector for ECPF.

Wraps a ``UQExtractor``, an **EMA smoother**, and an ADWIN instance.

For each incoming sample the forest's per-tree probability matrix is reduced
to a single UQ scalar (e.g. MI-like disagreement).  The raw scalar is then
smoothed with an **Exponential Moving Average** (EMA) before being fed into
ADWIN for change detection.

Why EMA smoothing?
    Hoeffding Forest predictions are inherently stochastic — online-bagging
    and random feature subspaces cause the MI-like scalar to jitter
    sample-to-sample even under a stable concept.  ADWIN is designed to
    detect *mean-level shifts*, not high-frequency noise.  Without
    smoothing, ADWIN fires on transient spikes → false warnings →
    buffer bloat (e.g. buf=15 000, false_warn=1.00).

    EMA (``α ∈ (0, 1]``) acts as a low-pass filter:
        s_t = α · u_t + (1 − α) · s_{t−1}
    Only sustained UQ trend changes propagate to ADWIN.

Design rationale
----------------
* The UQ scalar is label-free: it only depends on the forest members'
  probability outputs, not on the true label.
* ADWIN on the *smoothed* UQ stream is configured with a smaller delta
  (e.g. 0.01) than the error-based ADWIN (e.g. 0.05), making it able
  to trigger warnings earlier — but only for real distributional shifts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from river import drift

from .uq_extractor import UQExtractor


class UQWarningDetector:
    """ADWIN-based warning detector driven by EMA-smoothed forest UQ scalar.

    Parameters
    ----------
    uq_mode : str
        UQ scalar extraction mode.  One of ``"mi_like"``,
        ``"vote_disagreement"``, ``"predictive_entropy"``,
        ``"variance_eu"``.
    delta : float
        ADWIN delta for the UQ stream.  Smaller = more sensitive.
    grace_period : int
        Minimum number of instances ADWIN must observe before it can
        detect a change.
    smoothing_alpha : float
        EMA coefficient in ``(0, 1]``.  Smaller = heavier smoothing
        (more lag but fewer false warnings).  ``1.0`` disables smoothing.
    """

    def __init__(
        self,
        *,
        uq_mode: str = "mi_like",
        delta: float = 0.01,
        grace_period: int = 50,
        smoothing_alpha: float = 0.1,
    ) -> None:
        self.uq_mode = uq_mode
        self.delta = float(delta)
        self.grace_period = int(grace_period)
        self.smoothing_alpha = float(max(0.01, min(1.0, smoothing_alpha)))

        self._extractor = UQExtractor(mode=uq_mode)
        self._adwin = drift.ADWIN(delta=self.delta, grace_period=self.grace_period)

        # EMA state
        self._ema: Optional[float] = None  # None until first update

        # Diagnostics
        self.last_uq_extracted: float = 0.0
        self.last_uq_raw: float = 0.0
        self.last_uq_smoothed: float = 0.0
        self.last_uq_value: float = 0.0  # alias for backwards compat
        self.last_uq_scale: Optional[float] = None
        self.n_warnings: int = 0
        self.n_updates: int = 0

    def reset(self) -> None:
        """Reset ADWIN and EMA state (e.g. after a drift is handled)."""
        self._adwin = drift.ADWIN(delta=self.delta, grace_period=self.grace_period)
        self._ema = None

    def update(self, proba_matrix: List[Dict[Any, float]]) -> bool:
        """Feed one sample's per-tree probability matrix and check for warning.

        Parameters
        ----------
        proba_matrix : list of dict
            Per-tree class probability dicts (from
            ``HoeffdingForestModel.predict_proba_matrix``).

        Returns
        -------
        bool
            ``True`` if a warning (distributional shift in smoothed UQ
            stream) is detected at this step.
        """
        u_extracted = self._extractor.extract(proba_matrix)
        u_raw, scale = self._scale_for_detector(u_extracted, proba_matrix)
        self.last_uq_extracted = u_extracted
        self.last_uq_raw = u_raw
        self.last_uq_scale = scale
        self.n_updates += 1

        # EMA smoothing: s_t = α·u_t + (1-α)·s_{t-1}
        if self._ema is None:
            self._ema = u_raw
        else:
            self._ema = self.smoothing_alpha * u_raw + (1.0 - self.smoothing_alpha) * self._ema
        u_smoothed = self._ema
        self.last_uq_smoothed = u_smoothed
        self.last_uq_value = u_smoothed  # backwards compat

        self._adwin.update(u_smoothed)
        warning = bool(self._adwin.drift_detected)

        if warning:
            self.n_warnings += 1
        return warning

    def _scale_for_detector(
        self,
        value: float,
        proba_matrix: List[Dict[Any, float]],
    ) -> tuple[float, Optional[float]]:
        """Return the scalar that ADWIN should see plus the applied scale.

        ``variance_eu`` has a class-count-dependent upper bound of
        ``1 - 1/K``.  Scaling it to roughly [0, 1] keeps it comparable with
        the entropy-like UQ streams under the same ADWIN parameters.
        """
        if self.uq_mode != "variance_eu":
            return float(value), None
        classes: set[Any] = set()
        for proba in proba_matrix:
            classes.update(proba.keys())
        n_classes = len(classes)
        if n_classes <= 1:
            return 0.0, None
        scale = 1.0 - (1.0 / n_classes)
        if scale <= 0.0:
            return 0.0, None
        return max(0.0, min(1.0, float(value) / scale)), scale

    @property
    def stats(self) -> Dict[str, Any]:
        """Diagnostic stats for logging / event details."""
        return {
            "uq_mode": self.uq_mode,
            "uq_extracted": self.last_uq_extracted,
            "uq_raw": self.last_uq_raw,
            "uq_smoothed": self.last_uq_smoothed,
            "uq_scale": self.last_uq_scale,
            "uq_n_warnings": self.n_warnings,
            "uq_n_updates": self.n_updates,
        }

