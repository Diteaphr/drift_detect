"""Lightweight SEED-style detector for generic scalar streams.

This is an ECPF-level scalar-stream approximation inspired by SEED, not a full
reproduction of the original optimized SEED implementation. It preserves the
main old/new sub-window comparison idea with a Hoeffding-Bonferroni threshold
and bounded block coarsening, but rebuilds blocks from a bounded local window
on each update.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from typing import Deque, List


@dataclass
class _Block:
    n: int
    total: float

    @property
    def mean(self) -> float:
        return self.total / self.n if self.n else 0.0


class SEEDDetector:
    """A compact two-sub-window detector over bounded scalar values."""

    ROLE_PRESETS = {
        "warning": {
            "delta": 0.60,
            "min_num_instances": 10,
            "block_size": 10,
            "max_window": 2000,
            "max_blocks": 64,
        },
        "drift": {
            "delta": 0.45,
            "min_num_instances": 15,
            "block_size": 10,
            "max_window": 2000,
            "max_blocks": 64,
        },
    }

    def __init__(
        self,
        *,
        role: str = "drift",
        delta: float | None = None,
        min_num_instances: int | None = None,
        block_size: int | None = None,
        max_window: int | None = None,
        max_blocks: int | None = None,
        value_range: float = 1.0,
        two_sided: bool = False,
        compression_delta: float | None = None,
    ) -> None:
        if role not in self.ROLE_PRESETS:
            raise ValueError(
                f"Unknown SEED role {role!r}. Choose from {sorted(self.ROLE_PRESETS)}"
            )
        preset = self.ROLE_PRESETS[role]
        self.role = role
        delta = preset["delta"] if delta is None else delta
        min_num_instances = (
            preset["min_num_instances"]
            if min_num_instances is None
            else min_num_instances
        )
        block_size = preset["block_size"] if block_size is None else block_size
        max_window = preset["max_window"] if max_window is None else max_window
        max_blocks = preset["max_blocks"] if max_blocks is None else max_blocks
        self.delta = float(delta)
        self.min_num_instances = int(min_num_instances)
        self.block_size = int(max(1, block_size))
        self.max_window = int(max_window)
        self.max_blocks = int(max_blocks)
        self.value_range = float(value_range)
        self.two_sided = bool(two_sided)
        # Kept for older call sites. This prototype uses bounded coarsening
        # rather than SEED's full homogeneous-block compression.
        self.compression_delta = (
            float(compression_delta) if compression_delta is not None else float(delta)
        )
        self.values: Deque[float] = deque(maxlen=self.max_window)
        self.blocks: Deque[_Block] = deque()
        self.width = 0
        self.total = 0.0
        self.drift_detected = False

    def reset(self) -> None:
        self.values.clear()
        self.blocks.clear()
        self.width = 0
        self.total = 0.0
        self.drift_detected = False

    def update(self, value: float) -> bool:
        x = float(value)
        self.drift_detected = False
        self.values.append(x)
        self.width = len(self.values)
        self.total = sum(self.values)
        self._rebuild_blocks()

        if self.width < 2 * self.min_num_instances or len(self.blocks) < 2:
            return False

        cut_idx = self._find_cut()
        if cut_idx is None:
            return False

        cut_n = sum(b.n for b in list(self.blocks)[:cut_idx])
        recent_values = list(self.values)[cut_n:]
        self.values = deque(recent_values, maxlen=self.max_window)
        self.width = len(self.values)
        self.total = sum(self.values)
        self._rebuild_blocks()
        self.drift_detected = True
        return True

    def _find_cut(self) -> int | None:
        blocks = list(self.blocks)
        n0 = 0
        sum0 = 0.0
        total_n = self.width
        total_sum = self.total
        num_tests = max(1, len(blocks) - 1)

        for i, block in enumerate(blocks[:-1], start=1):
            n0 += block.n
            sum0 += block.total
            n1 = total_n - n0
            if n0 < self.min_num_instances or n1 < self.min_num_instances:
                continue
            mean0 = sum0 / n0
            mean1 = (total_sum - sum0) / n1
            diff = mean1 - mean0
            bound = self._hoeffding_bound(n0, n1, num_tests)
            if (abs(diff) if self.two_sided else diff) > bound:
                return i
        return None

    def _rebuild_blocks(self) -> None:
        """Build bounded blocks while preserving enough cut points to test.

        The previous version merged adjacent singleton blocks immediately using
        a very loose small-n Hoeffding bound, which could collapse the whole
        window into one block and make drift detection impossible.  Here we
        first keep evenly sized time-ordered blocks, then only merge adjacent
        old blocks when we exceed the memory budget.
        """
        values = list(self.values)
        if not values:
            self.blocks = deque()
            return
        block_size = max(1, min(self.block_size, len(values)))
        blocks: List[_Block] = []
        for start in range(0, len(values), block_size):
            chunk = values[start : start + block_size]
            blocks.append(_Block(len(chunk), sum(chunk)))
        while len(blocks) > self.max_blocks:
            merged: List[_Block] = []
            i = 0
            while i < len(blocks):
                if i + 1 < len(blocks):
                    merged.append(
                        _Block(
                            blocks[i].n + blocks[i + 1].n,
                            blocks[i].total + blocks[i + 1].total,
                        )
                    )
                    i += 2
                else:
                    merged.append(blocks[i])
                    i += 1
            blocks = merged
        self.blocks = deque(blocks)

    def _hoeffding_bound(
        self,
        n0: int,
        n1: int,
        num_tests: int,
        *,
        delta: float | None = None,
    ) -> float:
        alpha = max(1e-12, (self.delta if delta is None else delta) / max(1, num_tests))
        log_term = math.log(2.0 / alpha)
        return self.value_range * (
            math.sqrt(log_term / (2.0 * n0)) + math.sqrt(log_term / (2.0 * n1))
        )
