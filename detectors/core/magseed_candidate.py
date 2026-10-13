"""Experimental MagSeed-inspired binary-error detector, NOT original MagSeed.

Evidence: Anderson et al., *Recurring Concept Meta-learning for Evolving Data
Streams* (2019), sections 2.2 and 4.0.1, describes two warning conditions
(a looser Hoeffding bound and a change in mean error between sliding windows),
warning before drift, and delta=.05, epsilon=.01, alpha=.8, delta_w=.1.
https://arxiv.org/pdf/1905.08848

The Chen, Koh & Riddle (2015) MagSeed paper is not available for this project.
The following are explicit, UNVERIFIED choices: fixed adjacent windows;
Hoeffding union bound below; alpha scales the warning bound; epsilon is a
minimum mean increase; both warning conditions must hold; the drift bound
must hold after an earlier warning step; and a drift clears all window state.
No volatility or published severity formula is claimed. Do not use this
candidate for preregistered DET1 A5 or describe it as original MagSeed.
"""

from __future__ import annotations

from collections import deque
import math


class MagSeedCandidate:
    """Constant-time, increase-only prototype over 0/1 classification errors."""

    source_status = "inferred_candidate_not_original_magseed"

    def __init__(
        self,
        *,
        delta: float = 0.05,
        epsilon: float = 0.01,
        alpha: float = 0.8,
        delta_w: float = 0.1,
        window_size: int = 128,
        min_window: int = 32,
    ) -> None:
        if not (0.0 < delta < 1.0 and 0.0 < delta_w < 1.0):
            raise ValueError("delta and delta_w must be in (0, 1)")
        if not (0.0 <= epsilon < 1.0 and 0.0 < alpha <= 1.0):
            raise ValueError("epsilon must be in [0, 1), alpha in (0, 1]")
        if not (2 <= min_window <= window_size):
            raise ValueError("require 2 <= min_window <= window_size")
        self.delta = float(delta)
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.delta_w = float(delta_w)
        self.window_size = int(window_size)
        self.min_window = int(min_window)
        self.reset()

    def reset(self) -> None:
        """Discard both error windows and the pending warning state."""
        self._older: deque[int] = deque()
        self._recent: deque[int] = deque()
        self._older_sum = 0
        self._recent_sum = 0
        self._warning_on_prior_step = False
        self.warning_detected = False
        self.drift_detected = False
        self.mean_gap_proxy = 0.0
        self.estimation = 0.0

    @staticmethod
    def _bound(delta: float, n_old: int, n_new: int) -> float:
        # Union-bound two Hoeffding mean estimates for Bernoulli errors.
        return math.sqrt(math.log(2.0 / delta) / 2.0 * (1.0 / n_old + 1.0 / n_new))

    def update(self, value: int | float) -> "MagSeedCandidate":
        error = float(value)
        if error not in (0.0, 1.0):
            raise ValueError("MagSeedCandidate requires a 0/1 classification error")
        self.drift_detected = False
        self.warning_detected = False

        if len(self._recent) == self.window_size:
            moved = self._recent.popleft()
            self._recent_sum -= moved
            if len(self._older) == self.window_size:
                self._older_sum -= self._older.popleft()
            self._older.append(moved)
            self._older_sum += moved
        self._recent.append(int(error))
        self._recent_sum += int(error)
        self.estimation = self._recent_sum / len(self._recent)

        n_old, n_new = len(self._older), len(self._recent)
        if n_old < self.min_window or n_new < self.min_window:
            self._warning_on_prior_step = False
            self.mean_gap_proxy = 0.0
            return self

        gap = self._recent_sum / n_new - self._older_sum / n_old
        self.mean_gap_proxy = gap
        warning = gap > self.epsilon and gap > self.alpha * self._bound(
            self.delta_w, n_old, n_new
        )
        drift = (
            warning
            and self._warning_on_prior_step
            and gap > self._bound(self.delta, n_old, n_new)
        )
        self.warning_detected = warning
        self._warning_on_prior_step = warning
        if drift:
            # Inferred reset policy; preserve this step's outward flags.
            self.reset()
            self.warning_detected = True
            self.drift_detected = True
            self.mean_gap_proxy = gap
        return self
