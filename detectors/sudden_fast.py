import math
from collections import deque
from typing import Tuple, Optional

class ECDD:
    """
    EWMA for Concept Drift Detection (ECDD).
    Uses an Exponentially Weighted Moving Average (EWMA) control chart to detect 
    changes in the error rate in O(1) time and memory.
    """
    def __init__(self, lambda_: float = 0.2, warning_level: float = 2.0, drift_level: float = 3.0):
        self.lambda_ = lambda_
        self.warning_level = warning_level
        self.drift_level = drift_level
        
        # Internal state
        self._n = 0
        self._error_sum = 0.0
        self._z_t = 0.0
        
    def update(self, error: float) -> None:
        """Update the detector with a new error value (0.0 for correct, 1.0 for incorrect)."""
        if self._n == 0:
            self._z_t = error
        else:
            self._z_t = self.lambda_ * error + (1.0 - self.lambda_) * self._z_t
            
        self._n += 1
        self._error_sum += error

    def detect(self) -> Tuple[bool, bool]:
        """Returns (drift_detected, warning_detected)."""
        if self._n < 30:  # Minimum samples to get a reliable mean
            return False, False
            
        p_0 = self._error_sum / self._n
        
        # Variance of the EWMA statistic
        sigma_z_t = math.sqrt(
            p_0 * (1.0 - p_0) * (self.lambda_ / (2.0 - self.lambda_)) *
            (1.0 - math.pow(1.0 - self.lambda_, 2 * self._n))
        )
        
        # We only care if the error rate strictly increases
        if self._z_t > p_0 + self.drift_level * sigma_z_t:
            return True, True
        elif self._z_t > p_0 + self.warning_level * sigma_z_t:
            return False, True
            
        return False, False

    def reset(self) -> None:
        """Reset the detector state."""
        self._n = 0
        self._error_sum = 0.0
        self._z_t = 0.0


class STEPD:
    """
    Statistical Test of Equal Proportions (STEPD).
    Compares the recent window of errors to the overall historical window.
    Maintains O(1) update and compute complexity using rolling sums.
    """
    def __init__(self, window_size: int = 30, warning_level: float = 0.05, drift_level: float = 0.005):
        self.window_size = window_size
        self.warning_level = warning_level
        self.drift_level = drift_level
        
        # Internal state
        self._recent_errors: deque = deque(maxlen=window_size)
        self._r_sum = 0.0
        
        self._h_count = 0
        self._h_sum = 0.0
        
    def update(self, error: float) -> None:
        """Update the detector with a new error value (0.0 for correct, 1.0 for incorrect)."""
        if len(self._recent_errors) == self.window_size:
            # Move the oldest item from recent to history
            popped = self._recent_errors.popleft()
            self._r_sum -= popped
            self._h_sum += popped
            self._h_count += 1
            
        self._recent_errors.append(error)
        self._r_sum += error

    def _norm_cdf(self, x: float) -> float:
        """Approximation of the Normal CDF for p-value calculation."""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def detect(self) -> Tuple[bool, bool]:
        """Returns (drift_detected, warning_detected)."""
        r_count = len(self._recent_errors)
        if r_count < self.window_size or self._h_count < 30:
            return False, False
            
        p_1 = self._r_sum / r_count
        p_2 = self._h_sum / self._h_count
        
        # If the recent error rate is not greater, no drift
        if p_1 <= p_2:
            return False, False
            
        p_overall = (self._r_sum + self._h_sum) / (r_count + self._h_count)
        
        # To avoid division by zero
        if p_overall == 0.0 or p_overall == 1.0:
            return False, False
            
        # Z-statistic for proportions
        var = p_overall * (1.0 - p_overall) * (1.0 / r_count + 1.0 / self._h_count)
        z = (p_1 - p_2) / math.sqrt(var)
        
        # One-sided test (since p_1 > p_2), p-value is 1 - CDF(z)
        p_value = 1.0 - self._norm_cdf(z)
        
        if p_value < self.drift_level:
            return True, True
        elif p_value < self.warning_level:
            return False, True
            
        return False, False

    def reset(self) -> None:
        """Reset the detector state."""
        self._recent_errors.clear()
        self._r_sum = 0.0
        self._h_count = 0
        self._h_sum = 0.0
