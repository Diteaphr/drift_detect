"""Lightweight SeqDrift2-style detector for generic scalar streams.

The detector compares a fixed recent block with a reservoir sample of older
values using a Bernstein-style bound. This is an ECPF-level approximation
inspired by SeqDrift2, not an exact MOA/paper reproduction. The recent block is
non-overlapping, so detection can only happen at block boundaries.
"""

from __future__ import annotations

from collections import deque
import math
import random
from typing import Deque, List


class SeqDrift2Detector:
    """Reservoir old-sample versus recent-block drift detector."""

    ROLE_PRESETS = {
        "warning": {
            "delta": 0.30,
            "reservoir_size": 500,
            "block_size": 100,
            "bound_scale": 0.10,
        },
        "drift": {
            "delta": 0.20,
            "reservoir_size": 500,
            "block_size": 200,
            "bound_scale": 0.30,
        },
    }

    def __init__(
        self,
        *,
        role: str = "drift",
        delta: float | None = None,
        min_num_instances: int = 30,
        reservoir_size: int | None = None,
        block_size: int | None = None,
        value_range: float = 1.0,
        two_sided: bool = False,
        bound_scale: float | None = None,
        seed: int = 42,
    ) -> None:
        if role not in self.ROLE_PRESETS:
            raise ValueError(
                f"Unknown SeqDrift2 role {role!r}. Choose from {sorted(self.ROLE_PRESETS)}"
            )
        preset = self.ROLE_PRESETS[role]
        if delta is None:
            delta = preset["delta"]
        if reservoir_size is None:
            reservoir_size = preset["reservoir_size"]
        if block_size is None:
            block_size = preset["block_size"]
        if bound_scale is None:
            bound_scale = preset["bound_scale"]
        self.role = role
        self.delta = float(delta)
        self.min_num_instances = int(min_num_instances)
        self.reservoir_size = int(reservoir_size)
        self.block_size = int(max(block_size, min_num_instances))
        self.value_range = float(value_range)
        self.two_sided = bool(two_sided)
        self.bound_scale = float(bound_scale)
        self.seed = int(seed)
        self._rng = random.Random(self.seed)
        self.reservoir: List[float] = []
        self.recent: Deque[float] = deque(maxlen=self.block_size)
        self._old_seen = 0
        self.drift_detected = False

    def reset(self) -> None:
        self._rng = random.Random(self.seed)
        self.reservoir = []
        self.recent = deque(maxlen=self.block_size)
        self._old_seen = 0
        self.drift_detected = False

    def update(self, value: float) -> bool:
        x = float(value)
        self.drift_detected = False
        self.recent.append(x)

        if len(self.recent) < self.block_size:
            return False
        if len(self.reservoir) < self.min_num_instances:
            self._fold_recent_into_reservoir()
            return False

        recent_values = list(self.recent)
        old_mean = sum(self.reservoir) / len(self.reservoir)
        new_mean = sum(recent_values) / len(recent_values)
        diff = new_mean - old_mean
        bound = self._bernstein_bound(self.reservoir, recent_values)
        if (abs(diff) if self.two_sided else diff) > bound:
            self.reservoir = recent_values[-self.reservoir_size :]
            self._old_seen = len(self.reservoir)
            self.recent.clear()
            self.drift_detected = True
            return True

        self._fold_recent_into_reservoir()
        return False

    def _fold_recent_into_reservoir(self) -> None:
        for x in self.recent:
            self._old_seen += 1
            if len(self.reservoir) < self.reservoir_size:
                self.reservoir.append(x)
            else:
                j = self._rng.randrange(self._old_seen)
                if j < self.reservoir_size:
                    self.reservoir[j] = x
        self.recent.clear()

    def _bernstein_bound(self, old: List[float], new: List[float]) -> float:
        n0 = len(old)
        n1 = len(new)
        if n0 == 0 or n1 == 0:
            return float("inf")
        mean0 = sum(old) / n0
        mean1 = sum(new) / n1
        var0 = sum((x - mean0) ** 2 for x in old) / n0
        var1 = sum((x - mean1) ** 2 for x in new) / n1
        variance = var0 / n0 + var1 / n1
        log_term = math.log(3.0 / max(self.delta, 1e-12))
        scale = (1.0 / n0) + (1.0 / n1)
        return self.bound_scale * (
            math.sqrt(2.0 * variance * log_term)
            + 3.0 * self.value_range * log_term * scale
        )
