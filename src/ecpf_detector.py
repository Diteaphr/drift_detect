"""
Standalone ADWIN-dual warning+drift detector for ECPF experiments.

This file is intentionally separate from teammates' detector modules.
"""

from __future__ import annotations

from typing import Dict, Tuple

from river import drift


class ECPFWarningDriftDetector:
    """
    Two ADWINs on binary error stream:
      - warning detector: delta_w (more sensitive)
      - drift detector: delta (stricter)
    """

    def __init__(
        self,
        *,
        min_num_instances: int = 30,
        delta: float = 0.05,
        delta_w: float = 0.1,
    ) -> None:
        self.stats: Dict[str, float] = {}
        self.min_num_instances = int(min_num_instances)
        self.delta = float(delta)
        self.delta_w = float(delta_w)
        self._warn = drift.ADWIN(delta=self.delta_w, grace_period=min_num_instances)
        self._drift = drift.ADWIN(delta=self.delta, grace_period=min_num_instances)

    def reset(self) -> None:
        self._warn = drift.ADWIN(delta=self.delta_w, grace_period=self.min_num_instances)
        self._drift = drift.ADWIN(delta=self.delta, grace_period=self.min_num_instances)

    def update(self, err: float) -> Tuple[bool, bool]:
        x = 1.0 if float(err) > 0.5 else 0.0
        self._warn.update(x)
        self._drift.update(x)
        warning = bool(self._warn.drift_detected)
        drifted = bool(self._drift.drift_detected)
        self.stats = {"err": float(x)}
        if drifted:
            self.reset()
            return False, True
        return warning, False

