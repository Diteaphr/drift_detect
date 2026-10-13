"""Source-derived invariants for the explicitly non-A5 MAGSEED trial."""

import math
import unittest

from detectors.core.magseed_thesis_candidate import (
    MagSeed, MagSeedLiteral, MagSeedThesisCandidate, MagSeedUpward, _Block,
)
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
        self.assertIsInstance(make_detector("magseed", {}), MagSeed)
        self.assertIsInstance(make_detector("magseed_upward", {}), MagSeedUpward)
        self.assertEqual(ECPFZoneDetector("magseed")._det.source_status,
                         "chen_2016_thesis_interpretation_x")

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

    def test_a5_bidirectional_gate_and_a5u_directional_gate(self):
        rise = [int(i % 10 == 0) for i in range(2000)] + [i % 2 for i in range(2000)]
        fall = [i % 2 for i in range(2000)] + [int(i % 10 == 0) for i in range(2000)]
        for sequence, direction in ((rise, 1), (fall, -1)):
            detector = MagSeed()
            warning_idx = drift_idx = None
            for i, error in enumerate(sequence):
                detector.update(error)
                if detector.warning_detected and warning_idx is None:
                    warning_idx = i
                if detector.drift_detected and drift_idx is None:
                    drift_idx = i
                    self.assertIsNotNone(detector.last_cut)
                    self.assertGreater(detector.last_cut["left_n"], 0)
                    self.assertGreater(detector.last_cut["right_n"], 0)
                    self.assertGreater(direction * detector.last_cut["signed_gap"], 0)
            self.assertIsNotNone(warning_idx)
            self.assertIsNotNone(drift_idx)
            self.assertLess(warning_idx, drift_idx)
        upward = MagSeedUpward()
        self.assertFalse(any(upward.update(x).drift_detected for x in fall))

    def test_literal_interpretation_can_override_drift_state(self):
        main, literal = MagSeed(), MagSeedLiteral()
        errors = [0] * 1000 + [1] * 1000
        main_drifts = literal_drifts = 0
        for error in errors:
            main_drifts += bool(main.update(error).drift_detected)
            literal_drifts += bool(literal.update(error).drift_detected)
        self.assertGreater(main_drifts, literal_drifts)


if __name__ == "__main__":
    unittest.main()
