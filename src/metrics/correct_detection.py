"""
Interval-based "Correct Detection" score for concept drift (offline evaluation only).

**Definitions** (independent of DriftDetection types; this module only uses integers):

- **N (n_intervals)**: number of ground-truth drift intervals.
- **TP**: for each true interval [start, end] (inclusive, closed), count 1 if at least
  one detection timestamp falls in that interval; at most 1 per interval regardless
  of how many fires occurred inside. If two intervals overlap, each can
  contribute 1 TP when covered.
- **FP**: one count per detection timestamp that falls **outside** the union of all
  true intervals (each DriftDetection row counts separately; duplicate timestamps
  are not deduplicated).
- **Score (%)**: ``max(0, (TP - FP) / N * 100)`` when ``N > 0``; if ``TP <= FP`` the
  score is 0% (not negative). If ``N == 0``, ``score_percent`` is ``None`` to
  avoid division by zero (TP/FP are still defined: TP=0, FP=all detections).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Union

# Ground-truth interval as (start, end) or [start, end] with int bounds.
Interval = Union[Tuple[int, int], List[int]]

DEFAULT_PERTURBATION_EXTENSION = 2000


@dataclass(frozen=True)
class CorrectDetectionResult:
    tp: int
    fp: int
    n_intervals: int
    score_percent: Optional[float]
    """
    When ``n_intervals == 0``, ``score_percent`` is None.
    When ``n_intervals > 0``, ``score_percent`` is in [0, 100] (floored at 0).
    """


def _as_closed_bounds(intervals: Sequence[Interval]) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    for it in intervals:
        a, b = int(it[0]), int(it[1])
        if a > b:
            a, b = b, a
        out.append((a, b))
    return out


def _in_union(t: int, bounds: List[Tuple[int, int]]) -> bool:
    for s, e in bounds:
        if s <= t <= e:
            return True
    return False


def build_perturbation_intervals(
    drift_intervals: Sequence[Interval],
    extension: int = DEFAULT_PERTURBATION_EXTENSION,
) -> List[Tuple[int, int]]:
    """Extend each ground-truth drift interval's right edge by ``extension`` samples.

    e.g. [250, 2000] with extension=1000 → [250, 3000].
    Bounds are normalised so start ≤ end before extending.
    """
    out: List[Tuple[int, int]] = []
    for it in drift_intervals:
        s, e = int(it[0]), int(it[1])
        if s > e:
            s, e = e, s
        out.append((s, e + extension))
    return out


def compute_correct_detection(
    detection_timestamps: Sequence[int],
    ground_truth_intervals: Sequence[Interval],
) -> CorrectDetectionResult:
    """
    Compute TP, FP, N, and Correct Detection percent from raw timestamps and intervals.
    """
    times = [int(t) for t in detection_timestamps]
    bounds = _as_closed_bounds(ground_truth_intervals)
    n = len(bounds)

    if n == 0:
        return CorrectDetectionResult(
            tp=0,
            fp=len(times),
            n_intervals=0,
            score_percent=None,
        )

    tp = 0
    for s, e in bounds:
        if any(s <= t <= e for t in times):
            tp += 1

    fp = sum(1 for t in times if not _in_union(t, bounds))

    score = max(0.0, (tp - fp) / n * 100.0)

    return CorrectDetectionResult(
        tp=tp,
        fp=fp,
        n_intervals=n,
        score_percent=score,
    )
