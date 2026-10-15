"""ADWIN-family warning/drift detector combinations for scalar streams."""

from __future__ import annotations

from typing import Dict, Tuple

from river import drift

from detectors.core.rddm_moa import MOARDDM

from .seed import SEEDDetector
from .seqdrift2 import SeqDrift2Detector


DETECTOR_ALIASES = {"hddma": "hddm_a"}
SUPPORTED_DETECTORS = frozenset({"adwin", "hddm_a", "rddm", "seed", "seqdrift2"})


def normalize_detector_type(detector_type: str) -> str:
    kind = detector_type.lower()
    return DETECTOR_ALIASES.get(kind, kind)


class _OneSidedADWIN(drift.ADWIN):
    """MOA ``ADWINChangeDetector`` semantics (Waikato/moa 585577f, 2017): report a cut
    only if the estimate rose. A suppressed cut keeps its post-cut window, exactly as
    MOA does -- river would otherwise wipe the whole window on the next update."""

    def update(self, x):
        if self.drift_detected:
            self._reset()
        before = self.estimation
        self._drift_detected = self._helper.update(x)
        if self._drift_detected and self.estimation <= before:
            self._drift_detected = False
        return self


class _ADWINAdapter:
    def __init__(self, *, delta: float, min_num_instances: int, one_sided: bool = False) -> None:
        self.delta = float(delta)
        self.min_num_instances = int(min_num_instances)
        self._cls = _OneSidedADWIN if one_sided else drift.ADWIN
        self._detector = self._cls(delta=self.delta, grace_period=self.min_num_instances)
        self.drift_detected = False

    def reset(self) -> None:
        self._detector = self._cls(delta=self.delta, grace_period=self.min_num_instances)
        self.drift_detected = False

    def update(self, value: float) -> bool:
        self._detector.update(value)
        self.drift_detected = bool(self._detector.drift_detected)
        return self.drift_detected

    def reset_after_confirmation(self) -> None:
        self.reset()


class _ZoneDetectorAdapter:
    """Expose a zone detector as one arm of an independent warning/confirm pair.

    HDDM-A resets immediately after a drift in the existing ``ECPFZoneDetector``.
    MOA RDDM instead keeps its replay buffer and re-baselines on the next update;
    ``reset_after_confirmation`` preserves that behavior when this arm itself
    fired, while still resetting it when the other arm confirmed first.
    """

    zone_capable = True

    def __init__(self, kind: str, role: str) -> None:
        from river.drift.binary import HDDM_A

        makers = {"hddm_a": HDDM_A, "rddm": MOARDDM}
        self.kind = normalize_detector_type(kind)
        self.role = role
        self._make = makers[self.kind]
        self._detector = self._make()
        self.warning_detected = False
        self.drift_detected = False

    def reset(self) -> None:
        self._detector = self._make()
        self.warning_detected = False
        self.drift_detected = False

    def update(self, value: float) -> bool:
        self._detector.update(int(round(float(value))))
        self.drift_detected = bool(self._detector.drift_detected)
        self.warning_detected = bool(self._detector.warning_detected) or self.drift_detected
        result = self.warning_detected if self.role == "warning" else self.drift_detected
        if self.drift_detected and self.kind == "hddm_a":
            # Match ECPFZoneDetector: keep this step's outward flags but start
            # the next step from a fresh River HDDM-A instance.
            self._detector = self._make()
        return result

    def reset_after_confirmation(self) -> None:
        if self.kind == "rddm" and self.drift_detected:
            return  # preserve MOA's post-drift replay state
        self.reset()


def _make_detector(
    detector_type: str,
    *,
    role: str,
    delta: float,
    min_num_instances: int,
    random_seed: int,
    value_range: float,
    one_sided: bool = False,
):
    kind = normalize_detector_type(detector_type)
    if kind == "adwin":
        return _ADWINAdapter(delta=delta, min_num_instances=min_num_instances, one_sided=one_sided)
    if kind in {"hddm_a", "rddm"}:
        return _ZoneDetectorAdapter(kind, role)
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
        one_sided: bool = False,
    ) -> None:
        self.warning_detector_type = normalize_detector_type(warning_detector_type)
        self.drift_detector_type = normalize_detector_type(drift_detector_type)
        for detector_type in (self.warning_detector_type, self.drift_detector_type):
            if detector_type not in SUPPORTED_DETECTORS:
                raise ValueError(
                    f"Unknown ECPF detector type {detector_type!r}; "
                    f"choose from {', '.join(sorted(SUPPORTED_DETECTORS))}"
                )
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
            one_sided=one_sided,
        )
        self._drift = _make_detector(
            self.drift_detector_type,
            role="drift",
            delta=self.delta,
            min_num_instances=self.min_num_instances,
            random_seed=self.random_seed + 1,
            value_range=self.drift_value_range,
            one_sided=one_sided,
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

    @property
    def zone(self) -> bool:
        """Whether the warning arm has a persistent zone that can close itself."""
        return bool(getattr(self._warn, "zone_capable", False))

    def reset(self) -> None:
        self._warn.reset()
        self._drift.reset()

    def reset_warning(self) -> None:
        """Re-baseline only the warning arm (used by the warning timeout)."""
        if not self.zone:
            self._warn.reset()

    def _reset_after_confirmation(self) -> None:
        for detector in (self._warn, self._drift):
            reset = getattr(detector, "reset_after_confirmation", detector.reset)
            reset()

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
            self._reset_after_confirmation()
            return warning, True
        return warning, False
