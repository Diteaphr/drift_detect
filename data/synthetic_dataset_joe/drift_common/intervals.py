"""Drift interval annotation shared across generators."""

from __future__ import annotations


def drift_intervals_for_positions(
    drift_positions: list[int],
    width: int,
    n_samples: int,
) -> list[list[int]]:
    """Map each drift center p and transition width to [start, end] (inclusive, clipped)."""
    out: list[list[int]] = []
    half = width // 2
    for p in drift_positions:
        s = max(0, int(p) - half)
        e = min(n_samples - 1, int(p) + half)
        out.append([s, e])
    return out
