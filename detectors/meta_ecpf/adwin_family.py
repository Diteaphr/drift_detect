"""ADWIN-family warning/drift detector combinations for scalar streams."""

from __future__ import annotations

from typing import Dict, Tuple

from river import drift

from .seed import SEEDDetector
from .seqdrift2 import SeqDrift2Detector


class _ADWINAdapter:
    def __init__(self, *, delta: float, min_num_instances: int) -> None:
        self.delta = float(delta)
        self.min_num_instances = int(min_num_instances)
        self._detector = drift.ADWIN(delta=self.delta, grace_period=self.min_num_instances)
        self.drift_detected = False

    def reset(self) -> None:
        self._detector = drift.ADWIN(delta=self.delta, grace_period=self.min_num_instances)
        self.drift_detected = False

    def update(self, value: float) -> bool:
        self._detector.update(value)
        self.drift_detected = bool(self._detector.drift_detected)
        return self.drift_detected


def _make_detector(
    detector_type: str,
    *,
    role: str,
    delta: float,
    min_num_instances: int,
    random_seed: int,
    value_range: float,
):
    kind = detector_type.lower()
    if kind == "adwin":
        return _ADWINAdapter(delta=delta, min_num_instances=min_num_instances)
    if kind == "seed":
        return SEEDDetector(
            role=role,
            delta=delta,
            value_range=value_range,
        )
    if kind in {"seqdrift2", "seqdrift"}:
        return SeqDrift2Detector(
            role=role,
            delta=delta,
            min_num_instances=min_num_instances,
            value_range=value_range,
            seed=random_seed,
        )
    raise ValueError(f"Unknown ECPF ADWIN-family detector type: {detector_type}")


class ECPFAdwinFamilyDetector:
    """Dual warning/confirmation detector over scalar streams."""

    COMBOS: Dict[str, Tuple[str, str]] = {
        "dual_adwin": ("adwin", "adwin"),
        "dual_seed": ("seed", "seed"),
        "dual_seqdrift2": ("seqdrift2", "seqdrift2"),
        "seed_warning_adwin_drift": ("seed", "adwin"),
        "adwin_warning_seed_drift": ("adwin", "seed"),
        "seqdrift2_warning_adwin_drift": ("seqdrift2", "adwin"),
        "adwin_warning_seqdrift2_drift": ("adwin", "seqdrift2"),
        "seed_warning_seqdrift2_drift": ("seed", "seqdrift2"),
        "seqdrift2_warning_seed_drift": ("seqdrift2", "seed"),
    }

    def __init__(
        self,
        *,
        warning_detector_type: str = "adwin",
        drift_detector_type: str = "adwin",
        min_num_instances: int = 30,
        delta: float = 0.05,
        delta_w: float = 0.1,
        random_seed: int = 42,
        warning_value_range: float = 1.0,
        drift_value_range: float = 1.0,
    ) -> None:
        self.warning_detector_type = warning_detector_type.lower()
        self.drift_detector_type = drift_detector_type.lower()
        self.min_num_instances = int(min_num_instances)
        self.delta = float(delta)
        self.delta_w = float(delta_w)
        self.random_seed = int(random_seed)
        self.warning_value_range = float(warning_value_range)
        self.drift_value_range = float(drift_value_range)
        self.stats: Dict[str, float | str] = {}
        self._warn = _make_detector(
            self.warning_detector_type,
            role="warning",
            delta=self.delta_w,
            min_num_instances=self.min_num_instances,
            random_seed=self.random_seed,
            value_range=self.warning_value_range,
        )
        self._drift = _make_detector(
            self.drift_detector_type,
            role="drift",
            delta=self.delta,
            min_num_instances=self.min_num_instances,
            random_seed=self.random_seed + 1,
            value_range=self.drift_value_range,
        )

    @classmethod
    def from_combo(
        cls,
        combo: str,
        *,
        min_num_instances: int = 30,
        delta: float = 0.05,
        delta_w: float = 0.1,
        random_seed: int = 42,
    ) -> "ECPFAdwinFamilyDetector":
        normalized = combo.lower()
        if normalized not in cls.COMBOS:
            known = ", ".join(sorted(cls.COMBOS))
            raise ValueError(f"Unknown ECPF ADWIN-family combo: {combo}. Known: {known}")
        warning_type, drift_type = cls.COMBOS[normalized]
        return cls(
            warning_detector_type=warning_type,
            drift_detector_type=drift_type,
            min_num_instances=min_num_instances,
            delta=delta,
            delta_w=delta_w,
            random_seed=random_seed,
        )

    @property
    def combo_name(self) -> str:
        for name, pair in self.COMBOS.items():
            if pair == (self.warning_detector_type, self.drift_detector_type):
                return name
        return f"{self.warning_detector_type}_warning_{self.drift_detector_type}_drift"

    def reset(self) -> None:
        self._warn.reset()
        self._drift.reset()

    def update(self, err: float) -> Tuple[bool, bool]:
        return self.update_values(err, err)

    def update_values(self, warning_value: float, drift_value: float) -> Tuple[bool, bool]:
        w = float(warning_value)
        d = float(drift_value)
        warning = bool(self._warn.update(w))
        drifted = bool(self._drift.update(d))
        self.stats = {
            "warning_value": w,
            "drift_value": d,
            "detector_type": self.combo_name,
            "warning_detector": self.warning_detector_type,
            "drift_detector": self.drift_detector_type,
        }
        if drifted:
            self.reset()
            return warning, True
        return warning, False
