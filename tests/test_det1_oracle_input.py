"""DET1 oracle counts the original input coordinate despite injected row loss."""

import unittest

import numpy as np

from scripts.run_benchmark import (
    effective_pipeline_config, load_preset, oracle_input_schedule, run_pipeline,
)


class TestOracleInputSchedule(unittest.TestCase):
    def test_deleted_warning_and_confirm_rows_map_to_next_retained_input(self):
        position = np.array([i for i in range(400) if i not in {100, 160}])
        schedule = oracle_input_schedule([(100, 100)], position)
        self.assertEqual(schedule[0]["raw_confirm"], 160)
        self.assertEqual(int(position[schedule[0]["warning_index"]]), 101)
        self.assertEqual(int(position[schedule[0]["confirm_index"]]), 161)

        cfg = effective_pipeline_config(load_preset("ecpf_paper"), "binary", None)
        cfg.update(
            ecpf_signal_mode="oracle_input_60",
            ecpf_oracle_input_schedule=schedule,
            ecpf_learn_during_warning=False,
        )
        X = np.array([[i % 3, i % 7] for i in range(len(position))], dtype=float)
        y = np.array([i % 2 for i in range(len(position))], dtype=float)
        out = run_pipeline(X, y, cfg, 0)
        self.assertEqual(out["alarm_idx"], [schedule[0]["confirm_index"]])
        self.assertEqual(int(position[out["alarm_idx"][0]]), 161)

    def test_missing_gt_and_nonmonotone_positions_rejected(self):
        with self.assertRaisesRegex(ValueError, "ground truth"):
            oracle_input_schedule([], np.arange(100))
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            oracle_input_schedule([(20, 20)], np.array([0, 2, 2, 3]))

    def test_earlier_oracle_mode_remains_available(self):
        cfg = effective_pipeline_config(load_preset("ecpf_paper"), "binary", None)
        cfg.update(
            ecpf_signal_mode="oracle_60",
            ecpf_oracle_true_drift_times=[100],
            ecpf_warning_length=60,
        )
        X = np.array([[i % 3, i % 7] for i in range(400)], dtype=float)
        y = np.array([i % 2 for i in range(400)], dtype=float)
        out = run_pipeline(X, y, cfg, 0)
        self.assertEqual(out["alarm_idx"], [159])


if __name__ == "__main__":
    unittest.main()
