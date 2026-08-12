"""Shared drift sensitivity configuration and utilities."""

from drift_common.intervals import drift_intervals_for_positions
from drift_common.profiles import resolve
from drift_common.sensitivity import (
    MULTIPLIER,
    SENSITIVITY_TIERS,
    scale_int,
    scale_rate,
    scale_width_for_transition,
)

__all__ = [
    "MULTIPLIER",
    "SENSITIVITY_TIERS",
    "drift_intervals_for_positions",
    "resolve",
    "scale_int",
    "scale_rate",
    "scale_width_for_transition",
]
