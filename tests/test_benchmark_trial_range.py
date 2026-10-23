import pytest

from scripts.run_benchmark import dataset_sources, load_registry


def test_generated_trial_range_selects_reserved_trials() -> None:
    entry = load_registry()["injected_paper_electricity"]

    sources = dataset_sources(entry, n_trials=30, trial_start=20)

    assert len(sources) == 8 * 30
    assert {source["g_id"] for source in sources} == set(range(20, 50))
    assert all("_g00" not in source["stem"] for source in sources)


def test_generated_trial_range_rejects_registry_overflow() -> None:
    entry = load_registry()["injected_paper_electricity"]

    with pytest.raises(ValueError, match="exceeds registered"):
        dataset_sources(entry, n_trials=31, trial_start=20)


def test_trial_start_rejects_file_datasets() -> None:
    entry = load_registry()["electricity"]

    with pytest.raises(ValueError, match="generated datasets"):
        dataset_sources(entry, n_trials=None, trial_start=1)
