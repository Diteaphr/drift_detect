from typing import List, Optional

from detectors.meta.dynamic_weighted import DynamicWeightedVotingDetector
from detectors.meta.indicators import BaseIndicator, ErrorRateTrendIndicator
from .indicators import UQWarningIndicator

class DynamicWeightedVotingECPFDetector(DynamicWeightedVotingDetector):
    """
    ECPF-specific DWM variant.
    Uses UQ and error-rate trend as parallel confirmation signals.
    """
    def __init__(
        self,
        config=None,
        uq_mode: str = "mi_like",
        selected_detectors: Optional[List[str]] = None,
        custom_indicators: Optional[List[BaseIndicator]] = None,
    ):
        uq_delta = config.ecpf_uq_delta if config is not None else 0.01
        uq_grace_period = config.ecpf_uq_grace_period if config is not None else 50
        uq_smoothing_alpha = config.ecpf_uq_smoothing_alpha if config is not None else 0.1
        indicators = custom_indicators or [
            UQWarningIndicator(
                uq_mode=uq_mode,
                delta=uq_delta,
                grace_period=uq_grace_period,
                smoothing_alpha=uq_smoothing_alpha,
            ),
            ErrorRateTrendIndicator(short_window=50, long_window=250, threshold=0.05),
        ]
        super().__init__(
            config=config,
            custom_indicators=indicators,
            selected_detectors=selected_detectors,
            proxy_policy="all",
        )
        self.threshold = min(self.threshold, 2.0 / max(len(self.weights), 1))
