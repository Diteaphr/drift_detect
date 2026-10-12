"""Source-derived invariants for the explicitly non-A5 MAGSEED trial."""

import math
import unittest

from detectors.core.magseed_thesis_candidate import MagSeedThesisCandidate, _Block
from scripts.run_benchmark import make_detector
from src.ecpf_detector import ECPFZoneDetector


class TestMagSeedThesisCandidate(unittest.TestCase):
    def test_chapter_three_bound_uses_window_variance_and_bonferroni(self):
        got = MagSeedThesisCandidate._bound(0.05, 100, 100, 200, 0.25)
        inverse_m = 1 / 100 + 1 / 100
        log_term = math.log(2 * 200 / 0.05)
        expected = math.sqrt(2 * inverse_m * 0.25 * log_term) + 2 / 3 * inverse_m * log_term
        self.assertAlmostEqual(got, expected)
        self.assertLess(MagSeedThesisCandidate._bound(0.1, 100, 100, 200, 0.25), got)

    def test_block_splits_detect_both_directions_and_keep_right_window(self):
        for errors in ([0] * 1000 + [1] * 200, [1] * 1000 + [0] * 200):
            detector = MagSeedThesisCandidate()
            for i, error in enumerate(errors):
                detector.update(error)
                if detector.drift_detected:
                    break
            else:
                self.fail("thesis-based block comparison missed a large shift")
            self.assertGreaterEqual(i, 1000)
            self.assertGreater(detector._width, 0)
            self.assertLess(detector._width, 200)
            self.assertEqual(sum(b.n for b in detector._blocks), detector._width)
            self.assertEqual(sum(b.errors for b in detector._blocks), detector._errors)
            if detector.severity is not None:
                self.assertGreaterEqual(detector.severity, 0)
                self.assertLessEqual(detector.severity, 1)

    def test_compression_retains_the_incomplete_tail(self):
        detector = MagSeedThesisCandidate(block_size=4, compression_interval=2)
        detector._blocks = [_Block(4, 0) for _ in range(3)] + [_Block(1, 0)]
        detector._compress()
        self.assertEqual(len(detector._blocks), 2)  # two full blocks merged; partial tail retained

    def test_explicit_entrypoints_and_binary_input(self):
        self.assertIsInstance(make_detector("magseed_thesis_candidate", {}), MagSeedThesisCandidate)
        zone = ECPFZoneDetector("magseed_thesis_candidate")
        self.assertEqual(zone._det.source_status, "thesis_grounded_candidate_not_verified_a5")
        with self.assertRaises(ValueError):
            zone._det.update(0.2)
        with self.assertRaises(ValueError):
            make_detector("magseed", {})
        with self.assertRaises(ValueError):
            ECPFZoneDetector("magseed")

    def test_zone_propagates_warning_then_drift(self):
        zone = ECPFZoneDetector("magseed_thesis_candidate")
        warnings, drifts = [], []
        errors = [int(i % 10 == 0) for i in range(2000)] + [i % 2 for i in range(2000)]
        for i, error in enumerate(errors):
            warning, drift = zone.update_values(error, error)
            if warning:
                warnings.append(i)
            if drift:
                drifts.append(i)
        self.assertEqual(warnings[0], 2035)
        self.assertEqual(drifts[0], 2053)


if __name__ == "__main__":
    unittest.main()
