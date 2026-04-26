"""Unit tests for interval-based Correct Detection score."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import DriftDetection, DriftType
from src.metrics import compute_correct_detection
from tests.evaluation import correct_detection_from_detections


class TestComputeCorrectDetection(unittest.TestCase):
    def test_one_detection_in_overlap_counts_two_tp(self):
        # Overlapping ground-truth: same timestamp can satisfy two intervals
        r = compute_correct_detection([1000], [[900, 1000], [950, 1100]])
        self.assertEqual(r.tp, 2)
        self.assertEqual(r.fp, 0)
        self.assertEqual(r.n_intervals, 2)
        self.assertAlmostEqual(r.score_percent, 100.0)

    def test_tp_fp_mixed(self):
        # 100,200 in first interval; 5000 is outside all -> one FP
        r = compute_correct_detection([100, 200, 5000], [[100, 200], [300, 400]])
        self.assertEqual(r.tp, 1)
        self.assertEqual(r.fp, 1)
        self.assertEqual(r.n_intervals, 2)
        self.assertEqual(r.score_percent, 0.0)

    def test_tp_lteq_fp_floors_to_zero(self):
        r = compute_correct_detection([10, 20], [[0, 5]])
        self.assertEqual(r.tp, 0)
        self.assertEqual(r.fp, 2)
        self.assertEqual(r.n_intervals, 1)
        self.assertEqual(r.score_percent, 0.0)

    def test_n_zero(self):
        r = compute_correct_detection([1, 2, 3], [])
        self.assertEqual(r.n_intervals, 0)
        self.assertIsNone(r.score_percent)
        self.assertEqual(r.tp, 0)
        self.assertEqual(r.fp, 3)

    def test_multiple_fires_in_one_interval_count_as_one_tp(self):
        r = compute_correct_detection([100, 101, 102], [[50, 200]])
        self.assertEqual(r.tp, 1)
        self.assertEqual(r.fp, 0)
        self.assertEqual(r.n_intervals, 1)
        self.assertEqual(r.score_percent, 100.0)

    def test_reversed_interval_bounds(self):
        r = compute_correct_detection([100], [[150, 50]])
        self.assertEqual(r.tp, 1)
        self.assertEqual(r.fp, 0)


class TestWrapper(unittest.TestCase):
    def test_from_detections(self):
        dets = [
            DriftDetection(10, DriftType.SUDDEN, "a"),
            DriftDetection(99, DriftType.SUDDEN, "b"),
        ]
        r = correct_detection_from_detections(dets, [[0, 5], [50, 100]])
        self.assertEqual(r.tp, 1)
        self.assertEqual(r.fp, 1)
        self.assertEqual(r.n_intervals, 2)
        self.assertEqual(r.score_percent, 0.0)


if __name__ == "__main__":
    unittest.main()
