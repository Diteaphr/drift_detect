import numpy as np
from typing import Any, Dict, Optional, Tuple

from detectors.meta.indicators import BaseIndicator, UncertaintyProxyIndicator
from src.uq_warning_detector import UQWarningDetector

class UQWarningIndicator(BaseIndicator):
    """
    Indicator that wraps ECPF's UQ warning proxy logic.
    Provides proxy warnings based on Uncertainty Quantification of Hoeffding Forest.
    """
    def __init__(
        self,
        uq_mode: str = "mi_like",
        delta: float = 0.01,
        grace_period: int = 50,
        smoothing_alpha: float = 0.1,
    ):
        self.detector = UQWarningDetector(
            uq_mode=uq_mode,
            delta=delta,
            grace_period=grace_period,
            smoothing_alpha=smoothing_alpha,
        )
        self.fallback = UncertaintyProxyIndicator(window_size=100, variance_threshold=0.20)
        self.last_warning = False
        self.last_stats: Dict[str, Any] = {}
        self.uq_smoothed = 0.0

    def update(self, x: np.ndarray, y_true: float, y_pred: float, err: float, **kwargs) -> None:
        proba_matrix = kwargs.get("proba_matrix", None)
        if proba_matrix is None or len(proba_matrix) == 0:
            self.fallback.update(x, y_true, y_pred, err, **kwargs)
            self.last_warning, self.last_stats = self.fallback.detect()
            return

        self.last_warning = self.detector.update(proba_matrix)
        self.uq_smoothed = self.detector.last_uq_smoothed
        self.last_stats = self.detector.stats

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        if self.last_stats:
            return self.last_warning, self.last_stats
        return self.last_warning, {"uq_smoothed": self.uq_smoothed}

    def reset(self) -> None:
        self.detector.reset()
        self.fallback.reset()
        self.last_warning = False
        self.last_stats = {}
        self.uq_smoothed = 0.0
