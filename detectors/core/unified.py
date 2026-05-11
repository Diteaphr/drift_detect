"""Unified atomic drift detector library.

This module is the core detector entry point for meta-detectors.  It keeps the
atomic detector implementations and the registry in one place so callers do not
need to know whether an atom originally came from a sudden/gradual grouping.
"""

import math
from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Type

import numpy as np


class HDDM_W:
    """Hoeffding Drift Detection Method - W."""

    def __init__(self, min_samples: int = 30, delta: float = 0.002, lambda_: float = 0.95):
        self.min_samples = min_samples
        self.delta = delta
        self.lambda_ = lambda_
        self._errors: deque = deque()
        self._p0 = 0.0
        self._p1 = 0.0
        self._count = 0

    def update(self, error: float) -> None:
        self._count += 1
        self._errors.append(error)
        if len(self._errors) > self.min_samples:
            split = len(self._errors) // 2
            old_errors = list(self._errors)[:split]
            new_errors = list(self._errors)[split:]
            self._p0 = np.mean(old_errors) if old_errors else 0.0
            self._p1 = np.mean(new_errors) if new_errors else 0.0

    def detect(self) -> bool:
        if len(self._errors) < self.min_samples * 2:
            return False
        n = len(self._errors)
        m_harmonic = (n / 2.0 * n / 2.0) / n if n > 0 else 1.0
        epsilon = np.sqrt((1.0 / (2 * m_harmonic)) * np.log(2 / self.delta))
        return abs(self._p0 - self._p1) >= epsilon

    def reset(self) -> None:
        self._errors.clear()
        self._p0 = 0.0
        self._p1 = 0.0
        self._count = 0


class EDDM:
    """Early Drift Detection Method."""

    def __init__(self, min_samples: int = 30, warning_level: float = 0.95, drift_level: float = 0.90):
        self.min_samples = min_samples
        self.warning_level = warning_level
        self.drift_level = drift_level
        self._errors: deque = deque(maxlen=2000)
        self._error_distances: deque = deque(maxlen=2000)
        self._error_count = 0
        self._distance_sum = 0
        self._distance_count = 0

    def update(self, error: float) -> None:
        self._errors.append(error)
        if error == 1:
            self._error_count += 1
            if len(self._error_distances) > 0:
                distance = len(self._errors) - sum(self._error_distances) - 1
            else:
                distance = len(self._errors)
            self._error_distances.append(distance)
            self._distance_sum += distance
            self._distance_count += 1

    def detect(self) -> Tuple[bool, bool]:
        if self._distance_count < self.min_samples:
            return False, False
        avg_distance = self._distance_sum / max(self._distance_count, 1)
        if len(self._error_distances) <= 1:
            return False, False
        distances = list(self._error_distances)
        if np.std(distances) <= 0:
            return False, False
        p_mean = np.mean(distances)
        warning = avg_distance < self.warning_level * p_mean
        drift = avg_distance < self.drift_level * p_mean
        return drift, warning

    def reset(self) -> None:
        self._errors.clear()
        self._error_distances.clear()
        self._error_count = 0
        self._distance_sum = 0
        self._distance_count = 0


class DDM:
    """Drift Detection Method."""

    def __init__(self, min_samples: int = 100, warning_level: float = 2.0, drift_level: float = 3.0):
        self.min_samples = min_samples
        self.warning_level = warning_level
        self.drift_level = drift_level
        self._errors: deque = deque()
        self._error_count = 0
        self._total_samples = 0
        self._p = 0.0
        self._p_std = 0.0
        self._p_min = float("inf")
        self._p_std_min = float("inf")

    def update(self, error: float) -> None:
        self._total_samples += 1
        self._error_count += error
        self._p = self._error_count / self._total_samples
        self._p_std = np.sqrt(self._p * (1 - self._p) / self._total_samples)
        self._errors.append(error)
        if self._total_samples >= self.min_samples:
            if self._p + self._p_std < self._p_min + self._p_std_min:
                self._p_min = self._p
                self._p_std_min = self._p_std

    def detect(self) -> Tuple[bool, bool]:
        if self._total_samples < self.min_samples:
            return False, False
        warning = (self._p + self._p_std) > (self._p_min + self.warning_level * self._p_std_min)
        drift = (self._p + self._p_std) > (self._p_min + self.drift_level * self._p_std_min)
        return drift, warning

    def reset(self) -> None:
        self._errors.clear()
        self._error_count = 0
        self._total_samples = 0
        self._p = 0.0
        self._p_std = 0.0
        self._p_min = float("inf")
        self._p_std_min = float("inf")


class RDDM(DDM):
    """Reactive Drift Detection Method.

    RDDM reuses DDM's binomial error-rate bounds and adds warning-period
    bookkeeping so callers can reconfigure after long unconfirmed warnings.
    """

    def __init__(
        self,
        min_samples: int = 30,
        warning_level: float = 2.0,
        drift_level: float = 3.0,
        max_warning_length: int = 400,
    ):
        super().__init__(
            min_samples=min_samples,
            warning_level=warning_level,
            drift_level=drift_level,
        )
        self.max_warning_length = int(max_warning_length)
        self._warning_active = False
        self._warning_start_n: Optional[int] = None
        self._last_reconfigure = False

    def detect(self) -> Tuple[bool, bool]:
        drift, warning = super().detect()
        self._last_reconfigure = False

        if warning and not self._warning_active:
            self._warning_active = True
            self._warning_start_n = self._total_samples

        warning_age = self.warning_age
        if (
            self._warning_active
            and not drift
            and warning_age is not None
            and warning_age >= self.max_warning_length
        ):
            self._last_reconfigure = True
            self.reset()
            return False, False

        return drift, warning

    @property
    def warning_age(self) -> Optional[int]:
        if self._warning_start_n is None:
            return None
        return self._total_samples - self._warning_start_n

    @property
    def reconfigure_triggered(self) -> bool:
        return self._last_reconfigure

    def stats(self) -> Dict[str, Any]:
        return {
            "detector": "rddm",
            "updates": self._total_samples,
            "p": self._p,
            "s": self._p_std,
            "p_min": None if not math.isfinite(self._p_min) else self._p_min,
            "s_min": None if not math.isfinite(self._p_std_min) else self._p_std_min,
            "warning_active": self._warning_active,
            "warning_age": self.warning_age,
            "reconfigure": self._last_reconfigure,
        }

    def reset(self) -> None:
        super().reset()
        self._warning_active = False
        self._warning_start_n = None


class HDDM_A:
    """Hoeffding Drift Detection Method - A."""

    def __init__(self, min_samples: int = 100, delta: float = 0.005, lambda_: float = 0.999):
        self.min_samples = min_samples
        self.delta = delta
        self.lambda_ = lambda_
        self._errors: deque = deque(maxlen=2000)
        self._p_short = 0.0
        self._p_long = 0.0
        self._count = 0

    def update(self, error: float) -> None:
        self._count += 1
        self._p_short = self.lambda_ * self._p_short + (1 - self.lambda_) * error
        self._p_long = (1 - self.delta) * self._p_long + self.delta * error
        self._errors.append(error)

    def detect(self) -> bool:
        if self._count < self.min_samples:
            return False
        return abs(self._p_short - self._p_long) >= 0.1

    def reset(self) -> None:
        self._errors.clear()
        self._p_short = 0.0
        self._p_long = 0.0
        self._count = 0


class PageHinkley:
    """Page-Hinkley style cumulative deviation detector."""

    def __init__(self, delta: float = 0.05, threshold: float = 15.0, min_samples: int = 30):
        self.delta = delta
        self.threshold = threshold
        self.min_samples = min_samples
        self._n = 0
        self._sum = 0.0
        self._ph = 0.0

    def update(self, error: float) -> None:
        self._n += 1
        self._sum += error
        mean = self._sum / self._n
        self._ph = self._ph + (error - mean - self.delta)
        if self._ph < 0:
            self._ph = 0.0

    def detect(self) -> bool:
        if self._n < self.min_samples:
            return False
        return self._ph >= self.threshold

    def reset(self) -> None:
        self._n = 0
        self._sum = 0.0
        self._ph = 0.0


class ADWIN:
    """Adaptive Windowing detector used by the unified atom ensemble."""

    def __init__(self, delta: float = 0.01, max_buckets: int = 5, chunk_size: int = 200):
        self.delta = delta
        self.max_buckets = max_buckets
        self.chunk_size = chunk_size
        self._buckets: List[Tuple[int, float, float]] = []
        self._total_count = 0
        self._total_sum = 0.0
        self._total_sq = 0.0

    def update(self, value: float) -> bool:
        drift_detected = False
        self._total_count += 1
        self._total_sum += value
        self._total_sq += value ** 2
        if not self._buckets or self._buckets[-1][0] >= self.chunk_size:
            self._buckets.append((1, value, value ** 2))
        else:
            count, s, sq = self._buckets[-1]
            self._buckets[-1] = (count + 1, s + value, sq + value ** 2)
        if len(self._buckets) > self.max_buckets:
            self._merge_buckets()
        if self._total_count >= self.chunk_size * 2:
            drift_detected = self._detect_change()
            if drift_detected:
                self.reset()
        return drift_detected

    def _merge_buckets(self) -> None:
        if len(self._buckets) > self.max_buckets:
            c0, s0, sq0 = self._buckets.pop(0)
            c1, s1, sq1 = self._buckets.pop(0)
            self._buckets.insert(0, (c0 + c1, s0 + s1, sq0 + sq1))

    def _detect_change(self) -> bool:
        if len(self._buckets) < 2:
            return False
        c0, s0, _sq0 = self._buckets[0]
        c1, s1, _sq1 = self._buckets[-1]
        if c0 == 0 or c1 == 0:
            return False
        mean0 = s0 / c0
        mean1 = s1 / c1
        m_harmonic = 1.0 / ((1.0 / c0) + (1.0 / c1))
        epsilon = np.sqrt((1.0 / (2 * m_harmonic)) * np.log(4 / self.delta))
        return abs(mean0 - mean1) >= epsilon

    def reset(self) -> None:
        self._buckets.clear()
        self._total_count = 0
        self._total_sum = 0.0
        self._total_sq = 0.0


class ECDD:
    """EWMA for Concept Drift Detection."""

    def __init__(self, lambda_: float = 0.2, warning_level: float = 2.0, drift_level: float = 3.0):
        self.lambda_ = lambda_
        self.warning_level = warning_level
        self.drift_level = drift_level
        self._n = 0
        self._error_sum = 0.0
        self._z_t = 0.0

    def update(self, error: float) -> None:
        if self._n == 0:
            self._z_t = error
        else:
            self._z_t = self.lambda_ * error + (1.0 - self.lambda_) * self._z_t
        self._n += 1
        self._error_sum += error

    def detect(self) -> Tuple[bool, bool]:
        if self._n < 30:
            return False, False
        p_0 = self._error_sum / self._n
        sigma_z_t = math.sqrt(
            p_0
            * (1.0 - p_0)
            * (self.lambda_ / (2.0 - self.lambda_))
            * (1.0 - math.pow(1.0 - self.lambda_, 2 * self._n))
        )
        if self._z_t > p_0 + self.drift_level * sigma_z_t:
            return True, True
        if self._z_t > p_0 + self.warning_level * sigma_z_t:
            return False, True
        return False, False

    def reset(self) -> None:
        self._n = 0
        self._error_sum = 0.0
        self._z_t = 0.0


class STEPD:
    """Statistical Test of Equal Proportions."""

    def __init__(self, window_size: int = 30, warning_level: float = 0.05, drift_level: float = 0.005):
        self.window_size = window_size
        self.warning_level = warning_level
        self.drift_level = drift_level
        self._recent_errors: deque = deque(maxlen=window_size)
        self._r_sum = 0.0
        self._h_count = 0
        self._h_sum = 0.0

    def update(self, error: float) -> None:
        if len(self._recent_errors) == self.window_size:
            popped = self._recent_errors.popleft()
            self._r_sum -= popped
            self._h_sum += popped
            self._h_count += 1
        self._recent_errors.append(error)
        self._r_sum += error

    def _norm_cdf(self, x: float) -> float:
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def detect(self) -> Tuple[bool, bool]:
        r_count = len(self._recent_errors)
        if r_count < self.window_size or self._h_count < 30:
            return False, False
        p_1 = self._r_sum / r_count
        p_2 = self._h_sum / self._h_count
        if p_1 <= p_2:
            return False, False
        p_overall = (self._r_sum + self._h_sum) / (r_count + self._h_count)
        if p_overall == 0.0 or p_overall == 1.0:
            return False, False
        var = p_overall * (1.0 - p_overall) * (1.0 / r_count + 1.0 / self._h_count)
        z = (p_1 - p_2) / math.sqrt(var)
        p_value = 1.0 - self._norm_cdf(z)
        if p_value < self.drift_level:
            return True, True
        if p_value < self.warning_level:
            return False, True
        return False, False

    def reset(self) -> None:
        self._recent_errors.clear()
        self._r_sum = 0.0
        self._h_count = 0
        self._h_sum = 0.0


ATOM_DETECTORS: Dict[str, Type] = {
    "hddm_w": HDDM_W,
    "eddm": EDDM,
    "ddm": DDM,
    "rddm": RDDM,
    "hddm_a": HDDM_A,
    "page_hinkley": PageHinkley,
    "adwin": ADWIN,
    "ecdd": ECDD,
    "stepd": STEPD,
}

DEFAULT_ATOM_DETECTORS = ["hddm_w", "eddm", "ddm", "hddm_a", "page_hinkley", "adwin"]

SENSITIVITY_PROFILES: Dict[str, Dict[str, Dict[str, float]]] = {
    "normal": {
        "ddm": {"drift_level": 4.0},
        "page_hinkley": {"threshold": 15.0},
        "adwin": {"delta": 0.01},
        "ecdd": {"drift_level": 3.0},
    },
    "sensitive": {
        "ddm": {"drift_level": 3.0},
        "page_hinkley": {"threshold": 10.0},
        "adwin": {"delta": 0.1},
        "ecdd": {"drift_level": 2.0},
    },
    "dwm_normal": {
        "ddm": {"drift_level": 5.0},
        "page_hinkley": {"threshold": 15.0},
        "adwin": {"delta": 0.01},
        "ecdd": {"drift_level": 3.0},
    },
    "dwm_sensitive": {
        "ddm": {"drift_level": 3.5},
        "page_hinkley": {"threshold": 5.0},
        "adwin": {"delta": 0.1},
        "ecdd": {"drift_level": 2.0},
    },
}


class UnifiedDriftDetector:
    """Registry-backed manager for atomic concept drift detectors."""

    def __init__(
        self,
        min_samples: int = 30,
        atom_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
        selected_detectors: Optional[List[str]] = None,
    ):
        self.min_samples = min_samples
        self.atom_kwargs = atom_kwargs or {}
        if selected_detectors is None:
            selected_detectors = DEFAULT_ATOM_DETECTORS

        self.detectors: Dict[str, Any] = {}
        for name in selected_detectors:
            name_lower = name.lower()
            detector_cls = ATOM_DETECTORS.get(name_lower)
            if detector_cls is None:
                raise ValueError(f"Unknown atom detector: {name}")
            kwargs = dict(self.atom_kwargs.get(name_lower, {}))
            if name_lower in {"hddm_w", "eddm", "rddm"} and "min_samples" not in kwargs:
                kwargs["min_samples"] = min_samples
            self.detectors[name_lower] = detector_cls(**kwargs)

        self._buffer: deque = deque(maxlen=2000)
        self._returns_tuple = {"eddm", "ddm", "rddm", "ecdd", "stepd"}
        self.sensitivity_profile: Optional[str] = None

    def update(self, error: float) -> None:
        self._buffer.append(error)
        binary_error = 1 if error > 0.5 else 0

        for name, detector in self.detectors.items():
            if name in {"hddm_w", "eddm", "ddm", "rddm"}:
                detector.update(binary_error)
            elif name in {"ecdd", "stepd"}:
                detector.update(float(binary_error))
            elif name == "adwin":
                detector._last_drift = detector.update(error)
            else:
                detector.update(error)

    def detect(self) -> Dict[str, bool]:
        results = {}
        for name, detector in self.detectors.items():
            if name == "adwin":
                drift = getattr(detector, "_last_drift", False)
            elif name in self._returns_tuple:
                drift, _warning = detector.detect()
            else:
                drift = detector.detect()
            results[name] = bool(drift)
        return results

    def set_sensitivity(self, profile: str) -> None:
        if profile == self.sensitivity_profile:
            return
        settings = SENSITIVITY_PROFILES.get(profile)
        if settings is None:
            raise ValueError(f"Unknown sensitivity profile: {profile}")
        for detector_name, params in settings.items():
            detector = self.detectors.get(detector_name)
            if detector is None:
                continue
            for attr, value in params.items():
                if hasattr(detector, attr):
                    setattr(detector, attr, value)
        self.sensitivity_profile = profile

    def get_errors(self) -> np.ndarray:
        return np.array(list(self._buffer), dtype=np.float64)

    def reset(self) -> None:
        self._buffer.clear()
        self.sensitivity_profile = None
        for name, detector in self.detectors.items():
            detector.reset()
            if name == "adwin":
                detector._last_drift = False
