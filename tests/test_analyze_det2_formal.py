"""Focused checks for DET2 paired weighting, GT eligibility and CI rules."""

from scripts.analyze_det2_formal import paired_delta, condition, det1_verdict


def _row(dataset, stream, arm, group, correct, scored, gt, fp=None, x=None):
    return {
        "dataset": dataset, "stream": stream, "arm": arm, "group": group,
        "correct": correct, "n_scored": scored, "gt": gt,
        "post_correct": correct if gt else 0, "post_count": scored if gt else 0,
        "fp": fp, "X": x,
    }


def test_accuracy_reweights_prediction_counts_and_includes_empty_gt_stream():
    rows = [
        _row("i", "long", "new", "injected", 900, 1000, 1, 1, 1),
        _row("i", "long", "old", "injected", 800, 1000, 1, 2, 0),
        _row("s", "short", "new", "synthetic", 0, 10, 1, 0, 1),
        _row("s", "short", "old", "synthetic", 10, 10, 1, 1, 0),
        _row("n", "nogt", "new", "INSECTS", 100, 100, 0),
        _row("n", "nogt", "old", "INSECTS", 0, 100, 0),
    ]
    lookup = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    keys = {(r["dataset"], r["stream"]) for r in rows}
    got = paired_delta(lookup, "new", "old", "acc", keys)
    expected = 1000 / 1110 - 810 / 1110
    assert got["n"] == 3 and abs(got["point"] - expected) < 1e-12
    assert got["ci"] == [expected, expected]


def test_detection_excludes_empty_gt_and_keeps_paired_differences():
    rows = [
        _row("i", "gt", "new", "injected", 1, 1, 1, 3, 0.25),
        _row("i", "gt", "old", "injected", 1, 1, 1, 5, 0.1),
        _row("n", "nogt", "new", "INSECTS", 1, 1, 0),
        _row("n", "nogt", "old", "INSECTS", 1, 1, 0),
    ]
    lookup = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    keys = {(r["dataset"], r["stream"]) for r in rows}
    fp = paired_delta(lookup, "new", "old", "fp", keys)
    x = paired_delta(lookup, "new", "old", "X", keys)
    assert fp["n"] == x["n"] == 1
    assert fp["point"] == -2
    assert abs(x["point"] - 0.15) < 1e-12


def test_zero_endpoint_is_tie_and_det1_requires_both_conditions():
    assert condition([-3, 0], "negative") == "持平"
    assert condition([0, 2], "positive") == "持平"
    assert condition([-4, -1], "negative") == "成立"
    assert condition([1, 4], "positive") == "成立"
    assert det1_verdict("成立", "成立") == "優於"
    assert det1_verdict("不成立", "不成立") == "不如"
    assert det1_verdict("成立", "不成立") == "如實報告"
