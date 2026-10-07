"""Unit tests for the per-instance error signal fed to the drift detectors.

The pipeline used to define that signal as ``abs(y_true - y_pred)``, which is
only a 0-1 loss when the labels happen to be exactly {0, 1}.  These tests pin
down both halves of the fix: that the new definition is a *no-op* on binary
data (so previously published binary results stay valid), and that it stops
treating class indices as ordinal once K > 2.
"""

import itertools

import numpy as np

from src.ecpf import _wrong
from src.preprocessing import StreamBuffer, compute_prediction_errors, zero_one_loss


# ---------------------------------------------------------------------------
# The no-op guarantee on binary data
# ---------------------------------------------------------------------------
def test_binary_labels_match_the_old_absolute_difference():
    """On labels {0, 1}, the new loss reproduces ``abs(y_true - y_pred)`` exactly.

    This is the regression guard behind the claim that swapping the formula
    cannot move any binary experiment: every dataset shipped in ``data/`` uses
    ``y`` in {0, 1}, and every model backend returns a hard class label.
    """
    for y_true, y_pred in itertools.product([0.0, 1.0], repeat=2):
        assert zero_one_loss(y_true, y_pred) == float(np.abs(y_true - y_pred))


def test_buffer_errors_match_the_old_formula_on_a_binary_stream():
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 2, size=500).astype(float)
    y_pred = rng.integers(0, 2, size=500).astype(float)

    buf = StreamBuffer(max_len=1000)
    for t, (yt, yp) in enumerate(zip(y_true, y_pred)):
        buf.append(yt, yp, t)

    np.testing.assert_array_equal(buf.get_errors(), np.abs(y_true - y_pred))


# ---------------------------------------------------------------------------
# The actual bug: ordinal treatment of class indices
# ---------------------------------------------------------------------------
def test_multiclass_confusion_costs_one_regardless_of_label_distance():
    """A 0-vs-3 confusion is one mistake, not three.

    The old formula returned 3.0 here, and that magnitude reached ADWIN,
    HDDM_A and Page-Hinkley unbinarized (detectors/core/unified.py), rescaling
    their bounds by the arbitrary numeric distance between class indices.
    """
    assert zero_one_loss(0.0, 3.0) == 1.0
    assert zero_one_loss(0.0, 1.0) == 1.0
    assert zero_one_loss(3.0, 3.0) == 0.0

    # ...and the old formula demonstrably did not.
    assert np.abs(0.0 - 3.0) == 3.0


def test_non_zero_one_binary_encoding_still_costs_one():
    """A {-1, +1} or {1, 2} encoding scored 2.0 per mistake under the old formula."""
    assert zero_one_loss(-1.0, 1.0) == 1.0
    assert zero_one_loss(1.0, 2.0) == 1.0


def test_error_signal_honours_the_detector_contract():
    """``detectors/meta/base.py`` documents err as 1.0 (wrong) or 0.0 (correct)."""
    rng = np.random.default_rng(1)
    y_true = rng.integers(0, 7, size=300).astype(float)
    y_pred = rng.integers(0, 7, size=300).astype(float)

    buf = StreamBuffer(max_len=500)
    for t, (yt, yp) in enumerate(zip(y_true, y_pred)):
        buf.append(yt, yp, t)

    assert set(np.unique(buf.get_errors())) <= {0.0, 1.0}


# ---------------------------------------------------------------------------
# One definition, not several
# ---------------------------------------------------------------------------
def test_agrees_with_the_ecpf_internal_correctness_test():
    """The buffer's notion of "wrong" must match ECPF's ``_wrong``.

    ECPF builds its conceptual-equivalence bitsets with ``_wrong``; the
    detectors are driven by the buffer.  Before the fix these two disagreed
    for any K > 2 stream.
    """
    for y_true in range(5):
        for y_pred in range(5):
            assert zero_one_loss(y_true, y_pred) == float(_wrong(y_pred, y_true))


def test_vectorised_form_matches_the_scalar_form():
    rng = np.random.default_rng(2)
    y_true = rng.integers(0, 5, size=200).astype(float)
    y_pred = rng.integers(0, 5, size=200).astype(float)

    expected = np.array([zero_one_loss(a, b) for a, b in zip(y_true, y_pred)])
    np.testing.assert_array_equal(compute_prediction_errors(y_true, y_pred), expected)


def test_vectorised_form_rejects_length_mismatch():
    try:
        compute_prediction_errors(np.zeros(3), np.zeros(4))
    except ValueError:
        return
    raise AssertionError("expected ValueError on mismatched lengths")
