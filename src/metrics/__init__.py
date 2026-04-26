"""Offline metrics (decoupled from stream/pipeline)."""

from .correct_detection import CorrectDetectionResult, compute_correct_detection

__all__ = ["CorrectDetectionResult", "compute_correct_detection"]
