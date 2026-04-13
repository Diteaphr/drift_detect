from typing import Tuple, Dict, Any, List
import numpy as np

from .base import BaseMetaDetector
from detectors.meta.indicators import BaseIndicator, KSDistributionIndicator
from detectors.unified import UnifiedDriftDetector

class TwoStageVotingDetector(BaseMetaDetector):
    """
    Current Two-Stage Architecture (Data Drift Warning -> Dynamic Ensemble Strategy).
    - Stage 1: Continuous Unsupervised K-S test (and other proxy indicators) trigger warning.
    - Stage 2: Supervised Error tracking via UnifiedDriftDetector. Switch policy ANY/MAJORITY
               based on warning signal.
    """

    def __init__(self, config=None, custom_indicators: List[BaseIndicator] = None):
        """
        config should allow configuring inner modules. Assumes `pipeline.config` structure
        if present, otherwise default to reasonable parameters.
        """
        ks_window_size = config.meta_ks_window_size if config else 100
        atom_min_samples = config.atom_min_samples if config else 30
        atom_kwargs = config.atom_kwargs if config else {}
        
        # 模組化：支援多重 Indicator 觸發警告機制 (Stage 1 Warning)
        if custom_indicators is not None:
            self.indicators = custom_indicators
        else:
            self.indicators = [KSDistributionIndicator(window_size=ks_window_size)]
            
        self.drift_detector = UnifiedDriftDetector(min_samples=atom_min_samples, atom_kwargs=atom_kwargs)
        self.ensemble_strategy = "majority"

    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int
    ) -> Tuple[bool, int, Dict[str, Any]]:
        # 1. Update all indicators and check if ANY proxy generates a warning
        any_proxy_warning = False
        all_indicator_stats = {}
        for idx, indicator in enumerate(self.indicators):
            indicator.update(x, y_true, y_pred, err)
            flag, stats = indicator.detect()
            if flag:
                any_proxy_warning = True
            all_indicator_stats[f"indicator_{idx}"] = {"warning": flag, "stats": stats}

        # 2. Update supervised ensemble detector
        self.drift_detector.update(err)

        # 3. Dynamic Strategy Switch (War-time / Peace-time)
        if any_proxy_warning:
            self.ensemble_strategy = "any"  # 至少 2 票 (大於 0.33)
            
            # 讓 Atom Detectors 更敏感 (進入備戰狀態)
            self.drift_detector.ddm.drift_level = 3.0
            self.drift_detector.page_hinkley.threshold = 10.0
            self.drift_detector.adwin.delta = 0.1
        else:
            self.ensemble_strategy = "lenient"  # 至少 3 票 (大於 0.
            
            # 恢復 Atom Detectors 預設參數 (和平狀態)
            self.drift_detector.ddm.drift_level = 4.0
            self.drift_detector.page_hinkley.threshold = 15.0
            self.drift_detector.adwin.delta = 0.01

        # 4. Gather ensemble results and apply strategy decision
        drift_details = self.drift_detector.detect()
        
        drift_detected = False
        if self.ensemble_strategy == "majority":
            votes = sum(drift_details.values())
            drift_detected = votes >= 3
        elif self.ensemble_strategy == "lenient":
            votes = sum(drift_details.values())
            drift_detected = votes >= 2
        elif self.ensemble_strategy == "any":
            drift_detected = any(drift_details.values())
        elif self.ensemble_strategy == "all":
            drift_detected = all(drift_details.values())

        # 5. Bundle detailed Sub-Detector Statistics
        sub_detector_stats = {
            "proxy_indicators": {
                "any_warning": any_proxy_warning,
                "details": all_indicator_stats
            },
            "ensemble_results": drift_details,
            "meta_info": {
                "strategy_used": self.ensemble_strategy
            }
        }
        
        return drift_detected, t, sub_detector_stats

    def reset(self) -> None:
        for indicator in self.indicators:
            indicator.reset()
        self.drift_detector.reset()
