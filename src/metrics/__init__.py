"""Offline metrics (decoupled from stream/pipeline)."""

from .correct_detection import (
    CorrectDetectionResult,
    build_perturbation_intervals,
    compute_correct_detection,
)

__all__ = [
    "CorrectDetectionResult",
    "build_perturbation_intervals",
    "compute_correct_detection",
]
