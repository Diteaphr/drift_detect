"""Offline metrics (decoupled from stream/pipeline)."""

from .detection_delay import compute_detection_delays
from .correct_detection import (
    CorrectDetectionResult,
    DEFAULT_PERTURBATION_EXTENSION,
    build_perturbation_intervals,
    compute_correct_detection,
)
from .detection_evaluation import compute_count_score
from .evaluate_run import evaluate_run, pool_detection_runs

__all__ = [
    "evaluate_run",
    "pool_detection_runs",
    "compute_detection_delays",
    "CorrectDetectionResult",
    "build_perturbation_intervals",
    "compute_correct_detection",
    "DEFAULT_PERTURBATION_EXTENSION",
    "compute_count_score",
]
