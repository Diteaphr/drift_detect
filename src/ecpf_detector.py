"""Compatibility wrapper for ECPF ADWIN-family warning+drift detectors."""

from __future__ import annotations

from detectors.meta_ecpf.adwin_family import ECPFAdwinFamilyDetector


class ECPFWarningDriftDetector(ECPFAdwinFamilyDetector):
    """Backward-compatible name for the original dual-ADWIN ECPF detector."""

    def __init__(
        self,
        *,
        min_num_instances: int = 30,
        delta: float = 0.05,
        delta_w: float = 0.1,
    ) -> None:
        super().__init__(
            warning_detector_type="adwin",
            drift_detector_type="adwin",
            min_num_instances=min_num_instances,
            delta=delta,
            delta_w=delta_w,
        )
