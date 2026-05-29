"""Offline metrics (decoupled from stream/pipeline)."""

from .detection_delay import compute_detection_delays
from .correct_detection import (
    CorrectDetectionResult,
    DEFAULT_PERTURBATION_EXTENSION,
    build_perturbation_intervals,
    compute_correct_detection,
)
from .adaptive_window import AdaptiveWindowEstimator, WindowFeatures
from .detection_evaluation import (
    DetectionEvaluationSummary,
    compute_count_score,
    evaluate_detection_run,
    format_evaluation_batch_table,
    format_evaluation_summary,
    format_evaluation_summary_compact,
    print_evaluation_batch_table,
    summary_from_dict,
)

__all__ = [
    "compute_detection_delays",
    "CorrectDetectionResult",
    "build_perturbation_intervals",
    "compute_correct_detection",
    "AdaptiveWindowEstimator",
    "WindowFeatures",
    "DEFAULT_PERTURBATION_EXTENSION",
    "DetectionEvaluationSummary",
    "compute_count_score",
    "evaluate_detection_run",
    "format_evaluation_summary",
    "format_evaluation_summary_compact",
    "format_evaluation_batch_table",
    "print_evaluation_batch_table",
    "summary_from_dict",
]
