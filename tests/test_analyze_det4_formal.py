from scripts.analyze_det4_formal import (
    accuracy_verdict,
    category_of,
    detection_verdict,
    preset_parts,
    trial_number,
)


def test_det4_name_and_scope_helpers():
    assert preset_parts("det4_s1_wadwin_chddma") == ("s1", "adwin", "hddma")
    assert trial_number("electricity_class_prior_abrupt_g20") == 20
    assert category_of("airlines_full") == "真實"
    assert category_of("injected_paper_covertype") == "注入 paper"
    assert category_of("injected_covertype") == "注入 CSV"


def test_preregistered_detection_verdict_requires_both_conditions():
    assert detection_verdict([-3.0, -1.0], [1.0, 4.0]) == "優於"
    assert detection_verdict([1.0, 3.0], [-4.0, -1.0]) == "不如"
    assert detection_verdict([-3.0, -1.0], [-4.0, -1.0]) == "持平"
    assert detection_verdict([-1.0, 1.0], [1.0, 4.0]) == "持平"
    assert detection_verdict(None, [1.0, 4.0]) == "不可判定"


def test_preregistered_accuracy_verdict_uses_ci_sign():
    assert accuracy_verdict([0.01, 0.02]) == "優於"
    assert accuracy_verdict([-0.02, -0.01]) == "不如"
    assert accuracy_verdict([-0.01, 0.02]) == "持平"
    assert accuracy_verdict(None) == "不可判定"
