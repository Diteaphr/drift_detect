"""MAGSEED from Chen's 2016 thesis, chapter 3 (pp. 36-40).

Sources: Chen (2016), *Characterizing Drifts for Proactive Drift Detection in
Data Streams*, chapter 3, pp. 36-40, https://hdl.handle.net/2292/28911;
Huang et al.'s MOA SEED implementation for block/compression defaults:
https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/SEEDChangeDetector.java

Interpretation X (main): drift has priority over either warning condition,
then no change. Algorithm 1 line 27 literally contradicts this by resetting
the state when no split-warning was found; literal interpretation Y is exposed
only for a pre-registered dev sensitivity check. The warning coefficient 2 is
an evaluated thesis value, not a reported ECPF setting. See the 2026-10-13
revision of docs/ECPF_DET1_預註冊.md for every source gap and fixed choice.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math


@dataclass
class _Block:
    n: int
    errors: int

    @property
    def mean(self) -> float:
        return self.errors / self.n


class MagSeedThesisCandidate:
    """Block-split, variance-aware MAGSEED candidate over binary errors."""

    source_status = "thesis_grounded_candidate_not_verified_a5"

    def __init__(
        self,
        *,
        delta: float = 0.05,
        epsilon: float = 0.01,
        alpha: float = 0.8,
        delta_w: float = 0.1,
        block_size: int = 32,
        compression_interval: int = 75,
        warning_c: float = 2.0,
        one_sided: bool = False,
        state_interpretation: str = "X",
    ) -> None:
        if not (0 < delta < delta_w < 1):
            raise ValueError("require 0 < delta < delta_w < 1")
        if not (0 <= epsilon <= 1 and 0 < alpha <= 1):
            raise ValueError("epsilon must be in [0,1], alpha in (0,1]")
        if block_size < 2 or compression_interval < 1 or not (1 <= warning_c < 3):
            raise ValueError("invalid block or warning parameters")
        if state_interpretation not in {"X", "Y"}:
            raise ValueError("state_interpretation must be X or Y")
        self.delta = float(delta)
        self.epsilon = float(epsilon)  # epsilon-hat for compression, not a mean-gap floor
        self.alpha = float(alpha)  # compression growth, not a warning multiplier
        self.delta_w = float(delta_w)
        self.block_size = int(block_size)
        self.compression_interval = int(compression_interval)
        self.warning_c = float(warning_c)
        self.one_sided = bool(one_sided)
        self.state_interpretation = state_interpretation
        self.reset()

    def reset(self) -> None:
        self._blocks: list[_Block] = []
        self._width = 0
        self._errors = 0
        self._rolling: deque[int] = deque(maxlen=100)
        self._rolling_errors = 0
        self._p_min = math.inf
        self._s_min = math.inf
        self._completed_blocks_since_compression = 0
        self._warning_length = 0
        self._warning_errors = 0
        self.warning_detected = False
        self.drift_detected = False
        self.false_warning_detected = False
        self.severity: float | None = None
        self.last_cut: dict[str, int | float] | None = None
        self.estimation = 0.0

    @staticmethod
    def _bound(delta: float, left: int, right: int, width: int, variance: float) -> float:
        # Chen (2016), Eq. 3.2 and Eq. 2.17: m = 1/(1/n_left + 1/n_right).
        inverse_m = 1.0 / left + 1.0 / right
        log_term = math.log(2.0 * width / delta)
        return math.sqrt(2.0 * inverse_m * variance * log_term) + (
            2.0 / 3.0 * inverse_m * log_term
        )

    def _compress(self) -> None:
        # MOA SEED's fixed-term linear compression scans newest to oldest.
        # Epsilon-hat * alpha * t uses the relative block position t, starting at 1.
        # A just-opened tail is incomplete; MOA SEED compresses full blocks
        # immediately before opening it.
        i = len(self._blocks) - (2 if self._blocks[-1].n < self.block_size else 1)
        relative_position = 1
        while i > 0:
            older, newer = self._blocks[i - 1], self._blocks[i]
            tolerance = self.epsilon * self.alpha * relative_position
            if abs(newer.mean - older.mean) < tolerance:
                self._blocks[i - 1] = _Block(
                    older.n + newer.n, older.errors + newer.errors
                )
                del self._blocks[i]
            i -= 1
            relative_position += 1

    def update(self, value: int | float) -> "MagSeedThesisCandidate":
        error = float(value)
        if error not in (0.0, 1.0):
            raise ValueError("MAGSEED requires a binary 0/1 classification error")
        bit = int(error)
        self.warning_detected = False
        self.drift_detected = False
        self.false_warning_detected = False
        self.severity = None
        self.last_cut = None

        if not self._blocks or self._blocks[-1].n == self.block_size:
            if self._blocks:
                self._completed_blocks_since_compression += 1
            self._blocks.append(_Block(0, 0))
        tail = self._blocks[-1]
        tail.n += 1
        tail.errors += bit
        self._width += 1
        self._errors += bit
        self.estimation = self._errors / self._width

        if len(self._rolling) == 100:
            self._rolling_errors -= self._rolling[0]
        self._rolling.append(bit)
        self._rolling_errors += bit
        rate_warning = False
        if len(self._rolling) == 100:
            p = self._rolling_errors / 100.0
            s = math.sqrt(p * (1.0 - p))
            if p + s < self._p_min + self._s_min:
                self._p_min, self._s_min = p, s
            rate_warning = p + s > self._p_min + self.warning_c * self._s_min

        split_warning = False
        cut: int | None = None
        cut_details: dict[str, int | float] | None = None
        left_n = left_errors = 0
        variance = self.estimation * (1.0 - self.estimation)
        for i, block in enumerate(self._blocks[:-1], start=1):
            left_n += block.n
            left_errors += block.errors
            right_n = self._width - left_n
            signed_gap = (self._errors - left_errors) / right_n - left_errors / left_n
            gap = signed_gap if self.one_sided else abs(signed_gap)
            if gap > self._bound(self.delta, left_n, right_n, self._width, variance):
                cut = i
                cut_details = {
                    "block_index": i,
                    "left_n": left_n,
                    "right_n": right_n,
                    "signed_gap": signed_gap,
                }
                break
            if gap > self._bound(self.delta_w, left_n, right_n, self._width, variance):
                split_warning = True

        if cut is not None:
            self.last_cut = cut_details
            old = self._blocks[:cut]
            self._blocks = self._blocks[cut:]
            self._width -= sum(block.n for block in old)
            self._errors -= sum(block.errors for block in old)
            self.estimation = self._errors / self._width
            # Y models the literal final assignment of Algorithm 1 line 27:
            # if no split-warning was found, the outward drift state vanishes
            # even though line 21 already dropped the left blocks.
            self.drift_detected = self.state_interpretation == "X" or split_warning
            if self._warning_length:
                self.severity = (self._warning_errors + bit) / (self._warning_length + 1)
            self._warning_length = self._warning_errors = 0
            self._p_min = self._s_min = math.inf
            return self

        self.warning_detected = (
            rate_warning or split_warning
            if self.state_interpretation == "X"
            else split_warning
        )
        if self.warning_detected:
            self._warning_length += 1
            self._warning_errors += bit
        elif self._warning_length:
            self.false_warning_detected = True
            self._warning_length = self._warning_errors = 0

        if not self.warning_detected and (
            self._completed_blocks_since_compression >= self.compression_interval
        ):
            self._compress()
            self._completed_blocks_since_compression = 0
        return self


class MagSeed(MagSeedThesisCandidate):
    """A5: Chen 2016 thesis, with state conflict resolved by interpretation X."""

    source_status = "chen_2016_thesis_interpretation_x"


class MagSeedUpward(MagSeedThesisCandidate):
    """A5u: one-sided experimental variant; differs from Chen's absolute gap."""

    source_status = "one_sided_variant_not_original_magseed"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(one_sided=True, **kwargs)


class MagSeedLiteral(MagSeedThesisCandidate):
    """Interpretation Y: literal Algorithm 1 line 27, dev sensitivity only."""

    source_status = "chen_2016_pseudocode_literal_dev_only"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(state_interpretation="Y", **kwargs)
