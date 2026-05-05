from typing import List
from detectors.meta.two_stage_voting import TwoStageVotingDetector
from detectors.meta.indicators import BaseIndicator
from .indicators import UQWarningIndicator

class TwoStageVotingECPFDetector(TwoStageVotingDetector):
    """
    ECPF-specific TSV variant.
    Automatically initializes with a UQWarningIndicator to serve as the ECPF proxy.
    """
    def __init__(self, config=None, uq_mode: str = "mi_like", selected_detectors: List[str] = None):
        custom_indicators = [UQWarningIndicator(uq_mode=uq_mode)]
        super().__init__(config=config, custom_indicators=custom_indicators, selected_detectors=selected_detectors)
