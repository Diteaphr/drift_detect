"""
Sudden drift detector: detects abrupt change in prediction error distribution
using HDDM-W, EDDM, and ADWIN ensemble methods.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict
from collections import deque


class HDDM_W:
    """Hoeffding Drift Detection Method - W (Weighted window)."""
    
    def __init__(self, min_samples: int = 30, delta: float = 0.002, lambda_: float = 0.95):
        self.min_samples = min_samples
        self.delta = delta
        self.lambda_ = lambda_
        self._errors: deque = deque(maxlen=2000)
        self._p0 = 0.0  # old distribution estimate
        self._p1 = 0.0  # new distribution estimate
        self._count = 0
        self._change_detected = False
        
    def update(self, error: float) -> None:
        """error should be binary (0 or 1) or converted from continuous."""
        self._count += 1
        self._errors.append(error)
        
        # Update estimates with decay - newer samples weighted more
        decayed_error = error if len(self._errors) <= self.min_samples else error
        
        # Split into two windows with bias towards recent
        if len(self._errors) > self.min_samples:
            split = len(self._errors) // 2
            old_errors = list(self._errors)[: split]
            new_errors = list(self._errors)[split :]
            
            self._p0 = np.mean(old_errors) if old_errors else 0.0
            self._p1 = np.mean(new_errors) if new_errors else 0.0
        
    def detect(self) -> bool:
        """Returns True if sudden drift detected."""
        if len(self._errors) < self.min_samples * 2:
            return False
        
        # Hoeffding bound correctly computed for comparing two means (N/2 elements each)
        n = len(self._errors)
        m_harmonic = (n / 2.0 * n / 2.0) / n if n > 0 else 1.0  # Harmonic mean of split windows which is N/4
        epsilon = np.sqrt((1.0 / (2 * m_harmonic)) * np.log(2 / self.delta))
        
        return abs(self._p0 - self._p1) >= epsilon
    
    def reset(self) -> None:
        self._errors.clear()
        self._p0 = 0.0
        self._p1 = 0.0
        self._count = 0
        self._change_detected = False


class EDDM:
    """Early Drift Detection Method."""
    
    def __init__(self, min_samples: int = 30, warning_level: float = 0.95, drift_level: float = 0.90):
        self.min_samples = min_samples
        self.warning_level = warning_level
        self.drift_level = drift_level
        self._errors: deque = deque(maxlen=2000)
        self._error_distances: deque = deque(maxlen=2000)  # distances between consecutive errors
        self._error_count = 0
        self._distance_sum = 0
        self._distance_count = 0
        
    def update(self, error: float) -> None:
        """error should be binary (0 or 1)."""
        self._errors.append(error)
        
        if error == 1:  # prediction error occurred
            self._error_count += 1
            
            # Distance to previous error
            if len(self._error_distances) > 0:
                distance = len(self._errors) - sum(self._error_distances) - 1
            else:
                distance = len(self._errors)
                
            self._error_distances.append(distance)
            self._distance_sum += distance
            self._distance_count += 1
    
    def detect(self) -> Tuple[bool, bool]:
        """Returns (drift_detected, warning_detected)."""
        if self._distance_count < self.min_samples:
            return False, False
        
        # Average distance between errors (should be large in normal, small in drift)
        avg_distance = self._distance_sum / max(self._distance_count, 1)
        
        # Standard deviation of distances
        if len(self._error_distances) > 1:
            distances = list(self._error_distances)
            std_distance = np.std(distances)
        else:
            std_distance = 0.0
        
        # Drift when distance decreases (errors closer together)
        if std_distance > 0:
            p_current = avg_distance
            p_mean = np.mean(list(self._error_distances))
            
            warning = p_current < self.warning_level * p_mean
            drift = p_current < self.drift_level * p_mean
            
            return drift, warning
        
        return False, False
    
    def reset(self) -> None:
        self._errors.clear()
        self._error_distances.clear()
        self._error_count = 0
        self._distance_sum = 0
        self._distance_count = 0


class ADWIN:
    """Adaptive Windowing (ADWIN) for sudden drift detection."""
    
    def __init__(self, delta: float = 0.002, max_buckets: int = 5):
        self.delta = delta
        self.max_buckets = max_buckets
        self._buckets: List[Tuple[int, float, float]] = []  # (count, sum, sum_sq)
        self._total_count = 0
        self._total_sum = 0.0
        self._total_sq = 0.0
        
    def update(self, value: float) -> bool:
        """Add value and detect sudden drift. Returns True if drift detected."""
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
        
        # Check for drift - more aggressive for sudden detection
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
        """Detect if distribution changed suddenly."""
        if len(self._buckets) < 2:
            return False
        
        # Compare tail buckets for sudden changes
        c0, s0, sq0 = self._buckets[0]
        c1, s1, sq1 = self._buckets[-1]
        
        if c0 == 0 or c1 == 0:
            return False
        
        mean0 = s0 / c0
        mean1 = s1 / c1
        
        # Variance estimators
        var0 = max((sq0 / c0) - (mean0 ** 2), 0)
        var1 = max((sq1 / c1) - (mean1 ** 2), 0)
        
        # Hoeffding bound
        m = (1.0 / c0 + 1.0 / c1)
        epsilon = np.sqrt((1.0 / (2 * m)) * np.log(2 / self.delta))
        
        # More sensitive threshold for sudden detection
        return abs(mean0 - mean1) >= epsilon * 0.5
    
    def reset(self) -> None:
        self._buckets.clear()
        self._total_count = 0
        self._total_sum = 0.0
        self._total_sq = 0.0


class SuddenDriftDetector:
    """
    Composite sudden drift detector combining:
    - HDDM-W (Hoeffding Drift Detection Method - W)
    - EDDM (Early Drift Detection Method)
    - ADWIN (Adaptive Windowing)
    
    Detects abrupt changes in error distribution.
    """

    def __init__(
        self,
        window_size: int = 50,
        min_samples: int = 20,
        ensemble_strategy: str = "majority",
    ):
        """
        Args:
            window_size: Size of comparison windows
            min_samples: Minimum samples before detection
            ensemble_strategy: How to combine detector outputs
                - "majority": drift if majority agree
                - "any": drift if any detector signals
                - "all": drift if all detectors signal
        """
        self.window_size = window_size
        self.min_samples = min_samples
        self.ensemble_strategy = ensemble_strategy
        
        self.hddm_w = HDDM_W(min_samples=min_samples)
        self.eddm = EDDM(min_samples=min_samples)
        self.adwin = ADWIN()
        
        self._buffer: deque = deque(maxlen=2 * window_size)

    def update(self, error: float) -> None:
        """Update all detectors with new error value."""
        self._buffer.append(error)
        
        # Convert continuous error to binary for HDDM-W and EDDM
        # If the problem is classification, error is already 0.0 or 1.0
        # For general regression, thresholding at 0.5 works if errors are normalized
        binary_error = 1 if error > 0.5 else 0
        
        self.hddm_w.update(binary_error)
        self.eddm.update(binary_error)
        self.adwin.update(error)

    def detect(self) -> Tuple[bool, Dict[str, bool]]:
        """
        Detect sudden drift using ensemble of methods.
        
        Returns:
            (drift_detected, detector_results)
        """
        # Get individual detector results
        hddm_w_drift = self.hddm_w.detect()
        eddm_drift, _ = self.eddm.detect()
        adwin_drift = self.adwin._detect_change() if len(self.adwin._buckets) >= 2 else False
        
        results = {
            "HDDM-W": hddm_w_drift,
            "EDDM": eddm_drift,
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
        return np.array(list(self._buffer), dtype=np.float64)

    def reset(self) -> None:
        self._buffer.clear()
        self.hddm_w.reset()
        self.eddm.reset()
        self.adwin.reset()
