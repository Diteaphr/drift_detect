"""Tests for unified detection evaluation summary."""

import pytest

from src.metrics import (
    DEFAULT_PERTURBATION_EXTENSION,
    compute_count_score,
    evaluate_detection_run,
    format_evaluation_batch_table,
    format_evaluation_summary,
)
from src.metrics.detection_evaluation import DetectionEvaluationSummary
from src.metrics.correct_detection import compute_correct_detection


class TestComputeCountScore:
    def test_perfect_match(self):
        assert compute_count_score(10, 10) == 1.0

    def test_off_by_two(self):
        assert compute_count_score(8, 10) == pytest.approx(0.8)

    def test_zero_actual(self):
        assert compute_count_score(5, 0) is None

    def test_clamped_at_zero(self):
        assert compute_count_score(100, 10) == 0.0


class TestEvaluateDetectionRun:
    def test_matches_compute_correct_detection_on_alerts(self):
        intervals = [(100, 200), (500, 600)]
        warnings = [50, 150, 700]
        alerts = [150, 700]

        summary = evaluate_detection_run(
            warnings, alerts, intervals, extension=DEFAULT_PERTURBATION_EXTENSION
        )
        pert = [(100, 2200), (500, 2600)]
        cd = compute_correct_detection(alerts, pert)

        assert summary.cd_tp == cd.tp
        assert summary.cd_fp == cd.fp
        assert summary.cd_n == cd.n_intervals
        assert summary.cd_score_pct == cd.score_percent
        assert summary.n_warnings == 3
        assert summary.n_alerts == 2
        assert summary.n_actual == 2
        assert summary.count_score_warning == compute_count_score(3, 2)
        assert summary.count_score_alert == compute_count_score(2, 2)


class TestFormatTables:
    def test_single_summary_table_has_headers(self):
        s = DetectionEvaluationSummary(
            n_warnings=3,
            n_alerts=2,
            n_actual=2,
            count_score_warning=0.5,
            count_score_alert=1.0,
            cd_tp=1,
            cd_fp=0,
            cd_n=2,
            cd_score_pct=50.0,
        )
        text = format_evaluation_summary(s)
        assert "Metric" in text
        assert "Warnings" in text
        assert "MEAN" not in text

    def test_batch_table_includes_mean_row(self):
        s = DetectionEvaluationSummary(
            n_warnings=1,
            n_alerts=1,
            n_actual=1,
            count_score_warning=1.0,
            count_score_alert=1.0,
            cd_tp=1,
            cd_fp=0,
            cd_n=1,
            cd_score_pct=100.0,
        )
        text = format_evaluation_batch_table([("g00.csv", s, {"acc": 0.9, "pool": 2})])
        assert "dataset" in text
        assert "MEAN" in text
        assert "g00.csv" in text
