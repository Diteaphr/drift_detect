"""Behavior gates for the MOA-compatible RDDM port."""

import unittest

from detectors.core.rddm_moa import MOARDDM
from scripts.run_benchmark import make_detector
from src.ecpf_detector import ECPFZoneDetector


class TestMOARDDM(unittest.TestCase):
    @staticmethod
    def _feed(detector, values):
        warnings = []
        drifts = []
        for i, value in enumerate(values):
            detector.update(value)
            if detector.warning_detected:
                warnings.append(i)
            if detector.drift_detected:
                drifts.append(i)
        return warnings, drifts

    def test_error_increase_warns_before_drift(self):
        errors = [int(i % 10 == 0) for i in range(2000)] + [i % 2 for i in range(2000)]
        warnings, drifts = self._feed(MOARDDM(), errors)
        self.assertTrue(warnings)
        self.assertTrue(drifts)
        self.assertGreaterEqual(warnings[0], 2000)
        self.assertGreater(drifts[0], warnings[0])

    def test_error_decrease_does_not_fire(self):
        errors = [i % 2 for i in range(2000)] + [int(i % 10 == 0) for i in range(2000)]
        _, drifts = self._feed(MOARDDM(), errors)
        self.assertEqual(drifts, [])

    def test_both_entry_points_keep_moa_replay_state(self):
        self.assertIsInstance(make_detector("rddm", {}), MOARDDM)
        zone = ECPFZoneDetector("rddm")
        detector = zone._det
        errors = [int(i % 10 == 0) for i in range(2000)] + [i % 2 for i in range(2000)]
        for error in errors:
            _, drift = zone.update_values(error, error)
            if drift:
                break
        else:
            self.fail("RDDM never detected the injected increase")
        self.assertIs(zone._det, detector)
        zone.update_values(0, 0)
        self.assertIs(zone._det, detector)


if __name__ == "__main__":
    unittest.main()
