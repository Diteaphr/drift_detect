"""
Gradual drift detector: composite detector using DDM, HDDM-A, Page-Hinkley, and ADWIN.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict
from collections import deque


class DDM:
    """Drift Detection Method (DDM)."""
    
    def __init__(self, min_samples: int = 100, warning_level: float = 2.0, drift_level: float = 3.0):
        self.min_samples = min_samples
        self.warning_level = warning_level
        self.drift_level = drift_level
        self._errors: deque = deque()
        self._error_count = 0
        self._total_samples = 0
        self._p = 0.0
        self._p_std = 0.0
        
    def update(self, error: float) -> None:
        self._total_samples += 1
        self._error_count += error  # error is binary (0 or 1)
        self._p = self._error_count / self._total_samples
        self._p_std = np.sqrt(self._p * (1 - self._p) / self._total_samples)
        self._errors.append(error)
        
    def detect(self) -> Tuple[bool, bool]:
        """Returns (drift_detected, warning_detected)."""
        if self._total_samples < self.min_samples:
            return False, False
        
        warning = self._p + self.warning_level * self._p_std
        drift = self._p + self.drift_level * self._p_std
        
        return drift >= 0.5, warning >= 0.5
    
    def reset(self) -> None:
        self._errors.clear()
        self._error_count = 0
        self._total_samples = 0
        self._p = 0.0
        self._p_std = 0.0


class HDDM_A:
    """Hoeffding Drift Detection Method - A (HDDM-A)."""
    
    def __init__(self, min_samples: int = 100, delta: float = 0.005, lambda_: float = 0.999):
        self.min_samples = min_samples
        self.delta = delta
        self.lambda_ = lambda_
        self._errors: deque = deque()
        self._p_short = 0.0  # short window mean
        self._p_long = 0.0   # long window mean
        self._count = 0
        
    def update(self, error: float) -> None:
        self._count += 1
        # Exponential moving average
        self._p_short = self.lambda_ * self._p_short + (1 - self.lambda_) * error
        self._p_long = (1 - self.delta) * self._p_long + self.delta * error
        self._errors.append(error)
        
    def detect(self) -> bool:
        """Returns True if drift detected."""
        if self._count < self.min_samples:
            return False
        # Drift when difference between short and long windows is significant
        return abs(self._p_short - self._p_long) >= 0.1
    
    def reset(self) -> None:
        self._errors.clear()
        self._p_short = 0.0
        self._p_long = 0.0
        self._count = 0


class PageHinkley:
    """Page-Hinkley style detector: cumulative sum of (error - running_mean) with drift."""
    
    def __init__(
        self,
        window_size: int = 150,
        delta: float = 0.05,
        lambda_: float = 0.99,
        threshold: float = 50.0,
        min_samples: int = 100,
    ):
        self.window_size = window_size
        self.delta = delta
        self.lambda_ = lambda_
        self.threshold = threshold
        self.min_samples = min_samples
        self._errors: deque = deque(maxlen=window_size)
        self._m = 0.0  # running mean (exponential)
        self._ph = 0.0  # Page-Hinkley statistic
        self._min_ph = 0.0
        
    def update(self, error: float) -> None:
        self._errors.append(error)
        # Exponential moving average for reference level
        self._m = self.lambda_ * self._m + (1 - self.lambda_) * error
        # Cumulative deviation
        self._ph = self._ph + (error - self._m - self.delta)
        self._min_ph = min(self._min_ph, self._ph)
        
    def detect(self) -> bool:
        """Returns True if drift detected."""
        if len(self._errors) < self.min_samples:
            return False
        # Drift when PH - min_PH exceeds threshold
        return self._ph - self._min_ph >= self.threshold
    
    def reset(self) -> None:
        self._errors.clear()
        self._m = 0.0
        self._ph = 0.0
        self._min_ph = 0.0


class ADWIN:
    """Adaptive Windowing (ADWIN) for drift detection."""
    
    def __init__(self, delta: float = 0.01, max_buckets: int = 5):
        self.delta = delta
        self.max_buckets = max_buckets
        self._buckets: List[Tuple[int, float, float]] = []  # (count, sum, sum_sq)
        self._total_count = 0
        self._total_sum = 0.0
        self._total_sq = 0.0
        
    def update(self, value: float) -> bool:
        """Add value and detect drift. Returns True if drift detected."""
        drift_detected = False
        
        self._total_count += 1
        self._total_sum += value
        self._total_sq += value ** 2
        
        # Add to first bucket
        if self._buckets:
            count, s, sq = self._buckets[0]
            self._buckets[0] = (count + 1, s + value, sq + value ** 2)
        else:
            self._buckets.append((1, value, value ** 2))
        
        # Merge buckets if needed
        if len(self._buckets) > self.max_buckets:
            self._merge_buckets()
        
        # Check for drift
        if self._total_count > 10:
            drift_detected = self._detect_change()
            
        return drift_detected
    
    def _merge_buckets(self) -> None:
        """Merge oldest buckets."""
        if len(self._buckets) > self.max_buckets:
            c0, s0, sq0 = self._buckets.pop(0)
            c1, s1, sq1 = self._buckets.pop(0)
            self._buckets.insert(0, (c0 + c1, s0 + s1, sq0 + sq1))
    
    def _detect_change(self) -> bool:
        """Detect if distribution changed significantly."""
        if len(self._buckets) < 2:
            return False
        
        # Compare first and last bucket statistics
        c0, s0, sq0 = self._buckets[0]
        c1, s1, sq1 = self._buckets[-1]
        
        if c0 == 0 or c1 == 0:
            return False
        
        mean0 = s0 / c0
        mean1 = s1 / c1
        
        # Variance estimators
        var0 = (sq0 / c0) - (mean0 ** 2) if sq0 >= 0 else 0
        var1 = (sq1 / c1) - (mean1 ** 2) if sq1 >= 0 else 0
        
        # Hoeffding bound
        m = (1.0 / c0 + 1.0 / c1)
        epsilon = np.sqrt((1.0 / (2 * m)) * np.log(2 / self.delta))
        
        return abs(mean0 - mean1) >= epsilon
    
    def reset(self) -> None:
        self._buckets.clear()
        self._total_count = 0
        self._total_sum = 0.0
        self._total_sq = 0.0


class GradualDriftDetector:
    """
    Composite gradual drift detector combining:
    - DDM (Drift Detection Method)
    - HDDM-A (Hoeffding Drift Detection Method - A)
    - Page-Hinkley (cumulative sum)
    - ADWIN (Adaptive Windowing)
    """
    
    def __init__(self, ensemble_strategy: str = "majority"):
        """
        Args:
            ensemble_strategy: How to combine detector outputs
                - "majority": drift if majority of detectors agree
                - "any": drift if any detector signals  
                - "all": drift if all detectors signal
        """
        self.ensemble_strategy = ensemble_strategy
        self.ddm = DDM()
        self.hddm_a = HDDM_A()
        self.page_hinkley = PageHinkley()
        self.adwin = ADWIN()
        self._errors: deque = deque(maxlen=1000)
        
    def update(self, error: float) -> None:
        """Update all detectors with new error value."""
        self._errors.append(error)
        
        # Convert error to binary for DDM (e.g., 1 if error > threshold else 0)
        binary_error = 1 if error > 0.5 else 0
        
        self.ddm.update(binary_error)
        self.hddm_a.update(error)
        self.page_hinkley.update(error)
        self.adwin.update(error)
        
    def detect(self) -> Tuple[bool, Dict[str, bool]]:
        """
        Detect drift using ensemble of methods.
        
        Returns:
            (drift_detected, detector_results)
        """
        ddm_drift, _ = self.ddm.detect()
        hddm_drift = self.hddm_a.detect()
        ph_drift = self.page_hinkley.detect()
        adwin_drift = self.adwin.update(
            np.mean(list(self._errors)) if self._errors else 0
        )
        
        results = {
            "DDM": ddm_drift,
            "HDDM-A": hddm_drift,
            "PageHinkley": ph_drift,
            "ADWIN": adwin_drift,
        }
        
        # Ensemble decision
        if self.ensemble_strategy == "majority":
            votes = sum(results.values())
            drift_detected = votes >= 2
        elif self.ensemble_strategy == "any":
            drift_detected = any(results.values())
        elif self.ensemble_strategy == "all":
            drift_detected = all(results.values())
        else:
            drift_detected = False
            
        return drift_detected, results
    
    def get_errors(self) -> np.ndarray:
        return np.array(list(self._errors), dtype=np.float64)
    
    def reset(self) -> None:
        self._errors.clear()
        self.ddm.reset()
        self.hddm_a.reset()
        self.page_hinkley.reset()
        self.adwin.reset()
