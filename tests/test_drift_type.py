"""core.drift_type reads what the run recorded; it never runs a model."""

from core.drift_type import predict


def _event(**details):
    return {
        "timestamp": 0, "warning_t": 0, "confirmation_t": 0,
        "source": "ecpf", "drift_type": "sudden", "details": details,
    }


def test_type_ldd_label_is_shown_verbatim():
    p = predict(_event(type_ldd_prediction="gradual",
                       acc_best_on_warning=0.5, acc_new_on_warning=0.8))
    assert p.label == "gradual" and p.text == "gradual"
    assert p.source == "type_ldd" and not p.is_placeholder
    assert p.label_zh == "漸變"
    assert p.confidence is None and p.confidence_zh is None
    assert p.reused is False


def test_ecpf_reuse_does_not_override_the_label():
    p = predict(_event(type_ldd_prediction="sudden",
                       acc_best_on_warning=0.9, acc_new_on_warning=0.8))
    assert p.label == "sudden"
    assert p.reused is True


def test_drift_type_field_alone_is_not_trusted():
    # `drift_type` is "sudden" on the event, but without the classifier's own
    # key it must stay pending rather than echo a default as a verdict.
    p = predict(_event())
    assert p.label is None and p.is_placeholder and p.text == "待分類"


def test_unknown_label_is_pending():
    p = predict(_event(type_ldd_prediction="none"))
    assert p.label is None and p.is_placeholder


def test_badge_color_per_type():
    assert predict(_event(type_ldd_prediction="sudden")).color == "red"
    assert predict(_event(type_ldd_prediction="gradual")).color == "orange"
    assert predict(_event(type_ldd_prediction="incremental")).color == "blue"
    assert predict(_event()).color == "gray"


def test_type_counts_orders_labels_and_hides_empty_pending():
    from core.metrics import type_counts
    evs = [_event(type_ldd_prediction="sudden"), _event(type_ldd_prediction="sudden"),
           _event(type_ldd_prediction="incremental")]
    assert type_counts(evs) == {"sudden": 2, "gradual": 0, "incremental": 1}
    assert type_counts(evs + [_event()]) == {
        "sudden": 2, "gradual": 0, "incremental": 1, "待分類": 1}
