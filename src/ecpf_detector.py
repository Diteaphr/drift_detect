"""Compatibility wrapper for ECPF ADWIN-family warning+drift detectors."""

from __future__ import annotations

from typing import Optional, Tuple

from detectors.core.rddm_moa import MOARDDM
from detectors.core.magseed_candidate import MagSeedCandidate
from detectors.core.magseed_thesis_candidate import (
    MagSeed, MagSeedLiteral, MagSeedThesisCandidate, MagSeedUpward,
)
from detectors.meta_ecpf.adwin_family import ECPFAdwinFamilyDetector


class ECPFZoneDetector:
    """Official ECPF semantics (rand079/CPF): ONE binomial detector whose own warning
    ZONE drives the buffer. ``zone = True`` tells the pipeline to close the warning
    (and drop the buffer) when the detector leaves its warning zone without a drift.

    River's DDM / HDDM_A with their defaults (E9), or a port of MOA RDDM
    with its defaults. MagSeed follows Chen's 2016 thesis with the pre-registered
    interpretation X; MagSeedUpward is the one-sided A5u variant. The older
    candidate names remain exploratory. 0/1 error only -- classification.
    """

    zone = True

    def __init__(self, kind: str, drift_confidence: Optional[float] = None) -> None:
        from river.drift.binary import DDM, HDDM_A

        makers = {
            "ddm": DDM,
            "hddm_a": HDDM_A,
            "rddm": MOARDDM,
            "magseed_candidate": MagSeedCandidate,
            "magseed_thesis_candidate": MagSeedThesisCandidate,
            "magseed": MagSeed,
            "magseed_upward": MagSeedUpward,
            "magseed_literal_dev": MagSeedLiteral,
        }
        if kind not in makers:
            raise ValueError("ecpf_zone_detector must be one of %s, got %r" % (sorted(makers), kind))
        self.kind = kind
        self._make = makers[kind]
        if drift_confidence is not None:
            if kind != "hddm_a":
                raise ValueError("ecpf_zone_drift_confidence is only defined for hddm_a, got %r" % kind)
            c = float(drift_confidence)
            self._make = lambda: HDDM_A(drift_confidence=c, warning_confidence=5 * c)
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
        if drift and self.kind not in {"rddm", "magseed_candidate", "magseed_thesis_candidate", "magseed", "magseed_upward", "magseed_literal_dev"}:
            # RDDM replays; the old candidate resets, and the thesis candidate
            # retains only blocks right of the detected cut.
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
