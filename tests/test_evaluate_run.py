"""Calibration tests for src/metrics/evaluate_run.py.

The classification metrics are checked against a line-by-line port of MOA's
``BasicClassificationPerformanceEvaluator.addResult`` and against River; the
detection metrics against the docstring example and the scoring rules of
Cerqueira et al.'s ``EvaluateDriftDetector``.
"""
import json
import sys
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.metrics.evaluate_run import detection_metrics, evaluate_run, pool_detection_runs

ELECTRICITY = REPO / "data/dataset_0921/real_dataset/binary/electricity/electricity.csv"


def moa_reference(y_true, y_pred, num_classes):
    """Port of MOA BasicClassificationPerformanceEvaluator (unit weights)."""
    n = 0
    correct = 0
    row = [0] * num_classes
    col = [0] * num_classes
    prec_hit = [0] * num_classes
    prec_n = [0] * num_classes
    rec_hit = [0] * num_classes
    rec_n = [0] * num_classes
    nochange = 0
    majority = 0
    last_seen = 0
    for t, p in zip(y_true, y_pred):
        n += 1
        correct += p == t
        for i in range(num_classes):
            row[i] += p == i
            col[i] += t == i
            if p == i:
                prec_n[i] += 1
                prec_hit[i] += p == t
            if t == i:
                rec_n[i] += 1
                rec_hit[i] += p == t
        nochange += last_seen == t
        maj, best = 0, 0.0
        for i in range(num_classes):
            if col[i] / n > best:
                maj, best = i, col[i] / n
        majority += maj == t
        last_seen = t
    p0 = correct / n
    pc = sum(row[i] / n * col[i] / n for i in range(num_classes))
    f1s = []
    for i in range(num_classes):
        p = prec_hit[i] / prec_n[i] if prec_n[i] else 0.0
        r = rec_hit[i] / rec_n[i] if rec_n[i] else 0.0
        f1s.append(2 * p * r / (p + r) if p + r else 0.0)
    return {
        "acc_prequential": p0,
        "kappa": (p0 - pc) / (1 - pc),
        "kappa_t": (p0 - nochange / n) / (1 - nochange / n),
        "kappa_m": (p0 - majority / n) / (1 - majority / n),
        "macro_f1": sum(f1s) / num_classes,
        "baseline_no_change_acc": nochange / n,
        "baseline_majority_acc": majority / n,
    }


def noisy_stream(rng, n, k, skill):
    """Autocorrelated labels plus a predictor that is right with prob ``skill``."""
    y = np.empty(n, dtype=int)
    y[0] = rng.integers(k)
    for i in range(1, n):
        y[i] = y[i - 1] if rng.random() < 0.7 else rng.integers(k)
    pred = np.where(rng.random(n) < skill, y, rng.integers(k, size=n))
    return y, pred


class TestClassificationAgainstMOA(unittest.TestCase):
    def test_matches_moa_port(self):
        rng = np.random.default_rng(0)
        for k, task in ((2, "binary"), (5, "multiclass")):
            for skill in (0.3, 0.8):
                y, pred = noisy_stream(rng, 3000, k, skill)
                got = evaluate_run(y, pred.astype(float), task=task, n_classes=k)
                ref = moa_reference(y.tolist(), pred.tolist(), k)
                for key, val in ref.items():
                    self.assertAlmostEqual(got[key], val, places=12, msg=f"{key} k={k} skill={skill}")

    def test_never_predicted_class_counts_in_macro_f1(self):
        y = np.array([0, 1, 2, 0, 1, 2])
        pred = np.array([0, 1, 1, 0, 1, 1])
        got = evaluate_run(y, pred.astype(float), task="multiclass", n_classes=3)
        ref = moa_reference(y.tolist(), pred.tolist(), 3)
        self.assertAlmostEqual(got["macro_f1"], ref["macro_f1"])

    def test_matches_river(self):
        from river import metrics

        rng = np.random.default_rng(1)
        y, pred = noisy_stream(rng, 2000, 4, 0.6)
        acc, kappa = metrics.Accuracy(), metrics.CohenKappa()
        for t, p in zip(y.tolist(), pred.tolist()):
            acc.update(t, p)
            kappa.update(t, p)
        got = evaluate_run(y, pred.astype(float), task="multiclass", n_classes=4)
        self.assertAlmostEqual(got["acc_prequential"], acc.get(), places=12)
        self.assertAlmostEqual(got["kappa"], kappa.get(), places=12)

    def test_hand_computed_baselines(self):
        # no-change starts from class 0: hits at t=0 (0==0), t=2 (1==1)
        # majority (counts include current, ties -> lowest class):
        # t=0 ->0 hit, t=1 tie->0 miss, t=2 ->1 hit, t=3 tie->0 hit
        y = np.array([0, 1, 1, 0])
        got = evaluate_run(y, y.astype(float), task="binary")
        self.assertAlmostEqual(got["baseline_no_change_acc"], 0.5)
        self.assertAlmostEqual(got["baseline_majority_acc"], 0.75)
        self.assertAlmostEqual(got["kappa_t"], 1.0)

    @unittest.skipUnless(ELECTRICITY.exists(), "electricity.csv not present")
    def test_electricity_no_change_matches_souza(self):
        import pandas as pd

        y = pd.read_csv(ELECTRICITY)["y"].to_numpy()
        got = evaluate_run(y, y.astype(float), task="binary")
        # Souza et al. 2020 (arXiv:2005.00113): No-Change on Electricity = 85.33%
        self.assertAlmostEqual(got["baseline_no_change_acc"] * 100, 85.33, places=2)


class TestScoringScope(unittest.TestCase):
    def test_unscored_prefix(self):
        y = np.array([0, 1, 1, 1, 0, 0])
        pred = np.array([np.nan, np.nan, 1, 1, 0, 1])
        got = evaluate_run(y, pred, task="binary", warm_start=2)
        self.assertIsNone(got["acc_prequential"])
        self.assertEqual(got["metric_scope"], "scored_suffix")
        self.assertAlmostEqual(got["acc_post_warmup"], 0.75)

    def test_full_scope_and_post_warmup(self):
        y = np.array([0, 1, 1, 1, 0, 0])
        pred = np.array([1, 0, 1, 1, 0, 1], dtype=float)
        got = evaluate_run(y, pred, task="binary", warm_start=2)
        self.assertEqual(got["metric_scope"], "full")
        self.assertAlmostEqual(got["acc_prequential"], 3 / 6)
        self.assertAlmostEqual(got["acc_post_warmup"], 3 / 4)

    def test_gap_in_scoring_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_run(np.zeros(4), np.array([0, np.nan, 0, 0]), task="binary")

    def test_window_accuracy(self):
        y = np.zeros(4)
        pred = np.array([0, 1, 0, 0], dtype=float)
        got = evaluate_run(y, pred, task="binary", window=2)
        # rolling acc: 1/1, 1/2, 1/2, 2/2
        self.assertAlmostEqual(got["acc_window2_mean"], (1 + 0.5 + 0.5 + 1) / 4)

    def test_regression(self):
        got = evaluate_run(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 5.0]), task="regression")
        self.assertAlmostEqual(got["mae"], 2 / 3)
        self.assertAlmostEqual(got["rmse"], np.sqrt(4 / 3))


class TestDetectionAgainstCerqueira(unittest.TestCase):
    def test_docstring_example(self):
        # EvaluateDriftDetector docstring: preds=[500,1200,1250,2100], trues=[1000,2000],
        # max_delay=200, tot_n_instances=200
        m = detection_metrics([500, 1200, 1250, 2100], [(1000, 1000), (2000, 2000)],
                              n_instances=200, delta_max=200)
        self.assertEqual((m["tp"], m["fp"], m["fn"]), (2, 2, 0))
        self.assertAlmostEqual(m["precision"], 0.5)
        self.assertAlmostEqual(m["recall"], 1.0)
        self.assertAlmostEqual(m["f1"], 2 / 3)
        self.assertAlmostEqual(m["mdt"], 150.0)
        self.assertAlmostEqual(m["ndt"], 0.75)
        self.assertAlmostEqual(m["far"], 10.0)
        self.assertAlmostEqual(m["ar"], 20.0)

    def test_every_alarm_in_window_is_a_tp(self):
        m = detection_metrics([1000, 1010, 1020], [(1000, 1000)], n_instances=5000, delta_max=100)
        self.assertEqual((m["tp"], m["fp"], m["fn"]), (3, 0, 0))
        self.assertAlmostEqual(m["recall"], 1.0)
        self.assertAlmostEqual(m["episode_recall"], 1.0)
        self.assertAlmostEqual(m["mdt"], 0.0)

    def test_missed_drift(self):
        m = detection_metrics([5000], [(1000, 1000)], n_instances=6000, delta_max=100)
        self.assertEqual((m["tp"], m["fp"], m["fn"]), (0, 1, 1))
        self.assertEqual(m["f1"], 0.0)
        self.assertIsNone(m["mdt"])

    def test_alarms_after_last_window_are_false_positives(self):
        m = detection_metrics([150, 900], [(100, 100)], n_instances=1000, delta_max=100)
        self.assertEqual((m["tp"], m["fp"]), (1, 1))

    def test_alarm_before_onset_is_false_positive(self):
        m = detection_metrics([99], [(100, 100)], n_instances=1000, delta_max=100)
        self.assertEqual((m["tp"], m["fp"], m["fn"]), (0, 1, 1))

    def test_gradual_anchor(self):
        gt = [(100, 300)]
        start = detection_metrics([350], gt, n_instances=1000, delta_max=100, anchor="start")
        end = detection_metrics([350], gt, n_instances=1000, delta_max=100, anchor="end")
        self.assertEqual((start["tp"], start["fn"]), (0, 1))
        self.assertEqual((end["tp"], end["fn"]), (1, 0))

    def test_evaluate_run_reports_both_windows(self):
        y = np.zeros(1000)
        got = evaluate_run(y, y, task="binary", alarms=[350], gt_intervals=[(100, 300)], delta_max=100)
        self.assertEqual(got["tp"], 0)
        self.assertEqual(got["tp_paper_window"], 1)
        self.assertEqual(got["n_gt"], 1)

    def test_detect_from_and_input_coordinates(self):
        # Alarms before detect_from are dropped; rates use the input-stream length.
        y = np.zeros(800)
        got = evaluate_run(y, y, task="binary", alarms=[100, 600, 950], gt_intervals=[(900, 900)],
                           delta_max=100, detect_from=250, detection_n_instances=1000)
        self.assertEqual((got["tp"], got["fp"], got["n_alarms"]), (1, 1, 2))
        self.assertAlmostEqual(got["far"], 1.0)
        self.assertAlmostEqual(got["ar"], 2.0)

    def test_pooled_matches_published_cell(self):
        # Their ADWIN alarms for Electricity / class prior / abrupt, scored per trial
        # and pooled, must reproduce their results.csv row.
        fx = json.loads((Path(__file__).parent / "fixtures" / "cerqueira_electricity_prior_abrupt_adwin.json").read_text())
        n = fx["tot_n_instances"]
        y = np.zeros(10)
        runs = [evaluate_run(y, y, task="binary", alarms=ep["preds"], gt_intervals=[tuple(ep["true"])],
                             delta_max=fx["max_delay"], detection_n_instances=n) for ep in fx["episodes"]]
        pooled = pool_detection_runs(runs)
        want = fx["results"]
        for key in ("tp", "fp", "fn"):
            self.assertEqual(pooled[key], int(want[key]), key)
        for key in ("precision", "recall", "f1", "episode_recall", "mdt"):
            self.assertAlmostEqual(pooled[key], want[key], places=9, msg=key)
        self.assertAlmostEqual(pooled["far_cerqueira"], want["far"], places=9)
        self.assertAlmostEqual(pooled["ar_cerqueira"], want["ar"], places=9)

    def test_no_ground_truth(self):
        y = np.zeros(2000)
        got = evaluate_run(y, y, task="binary", alarms=[10, 20])
        self.assertIsNone(got["f1"])
        self.assertIsNone(got["n_gt"])
        self.assertEqual(got["n_alarms"], 2)
        self.assertAlmostEqual(got["ar"], 1.0)


if __name__ == "__main__":
    unittest.main()
