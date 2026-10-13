"""Behavior and isolation checks for the exploratory MagSeed candidate."""

import unittest

from detectors.core.magseed_candidate import MagSeedCandidate
from scripts.run_benchmark import make_detector
from src.ecpf_detector import ECPFZoneDetector


class TestMagSeedCandidate(unittest.TestCase):
    @staticmethod
    def _feed(detector, errors):
        warnings, drifts = [], []
        for i, error in enumerate(errors):
            detector.update(error)
            if detector.warning_detected:
                warnings.append(i)
            if detector.drift_detected:
                drifts.append(i)
        return warnings, drifts

    def test_rising_error_warns_before_drift(self):
        errors = [int(i % 10 == 0) for i in range(2000)] + [i % 2 for i in range(2000)]
        warnings, drifts = self._feed(MagSeedCandidate(), errors)
        self.assertTrue(warnings and drifts)
        self.assertGreaterEqual(warnings[0], 2000)
        self.assertLess(warnings[0], drifts[0])

    def test_falling_error_does_not_drift(self):
        errors = [i % 2 for i in range(2000)] + [int(i % 10 == 0) for i in range(2000)]
        _, drifts = self._feed(MagSeedCandidate(), errors)
        self.assertEqual(drifts, [])

    def test_historical_candidate_retains_distinct_entrypoint(self):
        self.assertIsInstance(make_detector("magseed_candidate", {}), MagSeedCandidate)
        zone = ECPFZoneDetector("magseed_candidate")
        self.assertEqual(zone.combo_name, "zone_magseed_candidate")
        self.assertEqual(zone._det.source_status, "inferred_candidate_not_original_magseed")
        self.assertNotEqual(
            make_detector("magseed", {}).source_status, zone._det.source_status
        )

    def test_window_reset_after_drift_and_binary_input(self):
        detector = MagSeedCandidate()
        errors = [int(i % 10 == 0) for i in range(2000)] + [i % 2 for i in range(2000)]
        for error in errors:
            detector.update(error)
            if detector.drift_detected:
                break
        else:
            self.fail("candidate did not confirm a drift")
        self.assertEqual(len(detector._older), 0)
        self.assertEqual(len(detector._recent), 0)
        detector.update(0)
        self.assertFalse(detector.drift_detected)
        with self.assertRaises(ValueError):
            detector.update(0.25)


if __name__ == "__main__":
    unittest.main()
