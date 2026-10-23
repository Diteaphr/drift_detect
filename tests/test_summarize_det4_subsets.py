from scripts.summarize_det4_subsets import subset_for, synthetic_subtype, trial_or_seed


def test_synthetic_subtype_prefers_recurring_prefix():
    assert synthetic_subtype("recurring_gradual_rbf4_100k_g03") == "recurring_gradual"
    assert synthetic_subtype("incremental_sea100k_g01") == "incremental"


def test_subset_keys_follow_the_preregistered_dataset_dimensions():
    assert subset_for("electricity", "electricity", None) == ("electricity", None)
    assert subset_for(
        "injected_electricity",
        "electricity_class_prior_abrupt_g00",
        "abrupt/class_prior",
    ) == ("injected_electricity/abrupt/class_prior", None)
    assert subset_for(
        "synthetic_multiclass",
        "recurring_gradual_rbf4_100k_g03",
        None,
    ) == ("synthetic_multiclass/recurring_gradual", "recurring_gradual")


def test_trial_or_seed_uses_g_suffix():
    assert trial_or_seed("electricity_class_prior_abrupt_g09") == 9
    assert trial_or_seed("electricity") is None
