from typing import Tuple, Dict, Any, List
import numpy as np

from .base import BaseMetaDetector
from detectors.meta.indicators import BaseIndicator, KSDistributionIndicator
from detectors.core.unified import UnifiedDriftDetector

class TwoStageVotingDetector(BaseMetaDetector):
    """
    Current Two-Stage Architecture (Data Drift Warning -> Dynamic Ensemble Strategy).
    - Stage 1: Continuous Unsupervised K-S test (and other proxy indicators) trigger warning.
    - Stage 2: Supervised Error tracking via UnifiedDriftDetector. Switch policy ANY/MAJORITY
               based on warning signal.
    """

    def __init__(self, config=None, custom_indicators: List[BaseIndicator] = None, selected_detectors: List[str] = None):
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
            
        self.drift_detector = UnifiedDriftDetector(
            min_samples=atom_min_samples, 
            atom_kwargs=atom_kwargs,
            selected_detectors=selected_detectors
        )
        self.ensemble_strategy = "majority"
        self.first_proxy_warning_t = None

    def _update_indicators(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        **kwargs,
    ) -> Tuple[bool, Dict[str, Any]]:
        any_proxy_warning = False
        all_indicator_stats = {}
        for indicator in self.indicators:
            indicator.update(x, y_true, y_pred, err, **kwargs)
            flag, stats = indicator.detect()
            any_proxy_warning = any_proxy_warning or bool(flag)
            name = getattr(indicator, "name", indicator.__class__.__name__)
            all_indicator_stats[name] = {"warning": bool(flag), "stats": stats}
        return any_proxy_warning, all_indicator_stats

    def _select_strategy(self, any_proxy_warning: bool) -> str:
        return "any" if any_proxy_warning else "lenient"

    def _vote(self, drift_details: Dict[str, bool], strategy: str) -> bool:
        votes = sum(drift_details.values())
        total_detectors = len(self.drift_detector.detectors)
        if strategy == "majority":
            return votes >= max(3, int(total_detectors * 0.7))
        if strategy == "lenient":
            return votes >= max(2, int(total_detectors * 0.5))
        if strategy == "any":
            return votes >= max(1, int(total_detectors * 0.15))
        if strategy == "all":
            return all(drift_details.values())
        raise ValueError(f"Unknown ensemble strategy: {strategy}")

    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int, **kwargs
    ) -> Tuple[bool, int, Dict[str, Any]]:
        # 1. Update all indicators and check if ANY proxy generates a warning
        any_proxy_warning, all_indicator_stats = self._update_indicators(
            x, y_true, y_pred, err, **kwargs
        )

        if any_proxy_warning and self.first_proxy_warning_t is None:
            self.first_proxy_warning_t = t

        # 2. Update supervised ensemble detector
        self.drift_detector.update(err)

        # 3. Dynamic Strategy Switch (War-time / Peace-time)
        self.ensemble_strategy = self._select_strategy(any_proxy_warning)
        profile = "sensitive" if any_proxy_warning else "normal"
        self.drift_detector.set_sensitivity(profile)

        # 4. Gather ensemble results and apply strategy decision
        drift_details = self.drift_detector.detect()
        
        drift_detected = self._vote(drift_details, self.ensemble_strategy)

        # 5. Bundle detailed Sub-Detector Statistics
        sub_detector_stats = {
            "proxy_indicators": {
                "any_warning": any_proxy_warning,
                "first_warning_t": self.first_proxy_warning_t,
                "details": all_indicator_stats
            },
            "ensemble_results": drift_details,
            "meta_info": {
                "strategy_used": self.ensemble_strategy
            }
        }
        
        return drift_detected, t, sub_detector_stats

    def reset(self) -> None:
        self.first_proxy_warning_t = None
        for indicator in self.indicators:
            indicator.reset()
        self.drift_detector.reset()
