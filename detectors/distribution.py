"""
Data Distribution Drift Detector (Type 3).
Monitors input features X for distribution changes without relying on true labels.
Uses Kolmogorov-Smirnov (K-S) test.
"""

import numpy as np
from collections import deque
from typing import Tuple, Dict, Any
try:
    from scipy.stats import ks_2samp
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class DistributionModule:
    """
    Unsupervised data distribution drift detector using K-S Test.
    Maintains a sliding buffer split into reference and current windows.
    """
    def __init__(self, window_size: int = 150, p_value_threshold: float = 0.05):
        """
        Args:
            window_size: Size of the comparison windows (reference vs current).
                         Total buffer size will be 2 * window_size.
            p_value_threshold: Significance level for the K-S test.
        """
        self.window_size = window_size
        self.p_value_threshold = p_value_threshold
        self.test_interval = 50  # Only perform K-S test every 50 steps
        self._step_count = 0     # Counter to track steps
        # Buffer holds 2 * window_size: first half is reference, second half is recent
        self._buffer = deque(maxlen=2 * window_size)
        self._is_ready = False
        self.n_features = 0

    def update(self, x: np.ndarray) -> None:
        """Update buffer with new feature vector X."""
        self._step_count += 1
        x_flat = np.asarray(x).ravel()
        if self.n_features == 0:
            self.n_features = len(x_flat)
        
        self._buffer.append(x_flat)
        
        if len(self._buffer) == 2 * self.window_size:
            self._is_ready = True

    def detect(self) -> Tuple[bool, dict]:
        """
        Detect if P(X) has changed using two-sample K-S test.
        Returns:
            (drift_detected_bool, stats_dict)
            stats_dict contains feature-level K-S statistics.
        """
        if not self._is_ready or not SCIPY_AVAILABLE:
            return False, {}
            
        # Optimization: Only run heavy KS test periodically
        if self._step_count % self.test_interval != 0:
            return False, {}
            
        data = np.array(self._buffer)
        ref_data = data[:self.window_size]
        curr_data = data[self.window_size:]
        
        # Check each feature independently
        drift_detected = False
        stats_dict = {}
        for i in range(self.n_features):
            # K-S test on feature i
            stat, p_value = ks_2samp(ref_data[:, i], curr_data[:, i])
            stats_dict[f"feat_{i}"] = {"stat": float(stat), "p_value": float(p_value)}
            
            # If any feature's distribution drifted significantly
            if p_value < self.p_value_threshold:
                # print(f"  [DistributionModule] Warning! Feat {i} shifted. K-S p_value: {p_value:.4f}")
                drift_detected = True
                
        return drift_detected, stats_dict

    def reset(self) -> None:
        """Clear buffer (usually called after a drift is confirmed)."""
        self._buffer.clear()
        self._is_ready = False
        self._step_count = 0
