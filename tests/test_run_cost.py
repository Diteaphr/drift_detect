import time
import unittest

import numpy as np

from src.metrics.run_cost import CostMeter, deep_sizeof, machine_info, rss_available


class _Node:
    def __init__(self, payload, child=None):
        self.payload = payload
        self.child = child


class _Slotted:
    __slots__ = ("arr",)

    def __init__(self, arr):
        self.arr = arr


class TestDeepSizeof(unittest.TestCase):
    def test_counts_owned_array_data(self):
        arr = np.zeros(100_000)
        self.assertGreaterEqual(deep_sizeof(_Node(arr)), arr.nbytes)

    def test_shared_object_counted_once(self):
        arr = np.zeros(100_000)
        once = deep_sizeof([arr])
        twice = deep_sizeof([arr, arr])
        self.assertLess(twice - once, 100)

    def test_view_counts_its_base_once(self):
        base = np.zeros(100_000)
        self.assertLess(deep_sizeof([base, base[:10]]) - deep_sizeof([base]), 1000)

    def test_excluded_objects_are_skipped(self):
        data = np.zeros(100_000)
        holder = _Node(1, child=data)
        self.assertLess(deep_sizeof(holder, exclude=(data,)), data.nbytes)

    def test_follows_slots_and_nested_objects(self):
        arr = np.zeros(50_000)
        self.assertGreaterEqual(deep_sizeof(_Node(None, child=_Slotted(arr))), arr.nbytes)

    def test_does_not_follow_classes_or_modules(self):
        self.assertLess(deep_sizeof({"cls": np.ndarray, "mod": np}), 2000)


class TestCostMeter(unittest.TestCase):
    def test_records_time_and_memory(self):
        meter = CostMeter(interval=0.01)
        meter.start()
        blob = np.ones(20_000_000)  # 160 MB that stays alive until stop()
        time.sleep(0.05)
        res = meter.stop(n_instances=1000)
        del blob
        self.assertGreater(res["runtime_s"], 0.04)
        self.assertGreaterEqual(res["cpu_time_s"], 0)
        self.assertIsNotNone(res["instances_per_s"])
        if rss_available():
            self.assertGreater(res["rss_increment_mb"], 100)
            self.assertGreater(res["ram_hours_gb"], 0)
            self.assertGreaterEqual(res["rss_samples"], 2)

    def test_machine_info_fields(self):
        info = machine_info()
        for key in ("os", "cpu", "cpu_count", "ram_gb", "blas_threads"):
            self.assertIn(key, info)


if __name__ == "__main__":
    unittest.main()
