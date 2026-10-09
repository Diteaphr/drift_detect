"""Compatibility wrapper for ECPF ADWIN-family warning+drift detectors."""

from __future__ import annotations

from typing import Tuple

from detectors.meta_ecpf.adwin_family import ECPFAdwinFamilyDetector


class ECPFZoneDetector:
    """Official ECPF semantics (rand079/CPF): ONE binomial detector whose own warning
    ZONE drives the buffer. ``zone = True`` tells the pipeline to close the warning
    (and drop the buffer) when the detector leaves its warning zone without a drift.

    river's DDM / HDDM_A with their defaults, which equal MOA's (E9,
    docs/實驗脈絡總覽.md). 0/1 error only -- classification.
    """

    zone = True

    def __init__(self, kind: str) -> None:
        from river.drift.binary import DDM, HDDM_A

        makers = {"ddm": DDM, "hddm_a": HDDM_A}
        if kind not in makers:
            raise ValueError("ecpf_zone_detector must be one of %s, got %r" % (sorted(makers), kind))
        self.kind = kind
        self._make = makers[kind]
        self._det = self._make()
        self.stats: dict = {}

    @property
    def combo_name(self) -> str:
        return "zone_" + self.kind

    def reset(self) -> None:
        self._det = self._make()

    def reset_warning(self) -> None:
        """A single detector has no separate warning arm; its zone ends on its own."""

    def update_values(self, warning_value: float, drift_value: float) -> Tuple[bool, bool]:
        self._det.update(int(round(float(drift_value))))
        drift = bool(self._det.drift_detected)
        warning = bool(self._det.warning_detected) or drift  # a drift step is also inside the zone
        self.stats = {"drift_value": float(drift_value), "detector_type": self.combo_name}
        if drift:
            self.reset()
        return warning, drift


class ECPFWarningDriftDetector(ECPFAdwinFamilyDetector):
    """Backward-compatible name for the original dual-ADWIN ECPF detector."""

    def __init__(
        self,
        *,
        min_num_instances: int = 30,
        delta: float = 0.05,
        delta_w: float = 0.1,
        one_sided: bool = False,
    ) -> None:
        super().__init__(
            warning_detector_type="adwin",
            drift_detector_type="adwin",
            min_num_instances=min_num_instances,
            delta=delta,
            delta_w=delta_w,
            one_sided=one_sided,
        )
