from scripts.run_det4_formal import (
    ALL_PRESETS,
    BATCHES,
    OFF_DIAGONAL_PRESETS,
    batch_expected,
    command_for,
)


def test_det4_formal_batches_match_preregistered_new_run_count() -> None:
    assert len(ALL_PRESETS) == 18
    assert len(OFF_DIAGONAL_PRESETS) == 13
    assert batch_expected("t1") == 2_665
    assert batch_expected("t3") == 4_320
    assert batch_expected("short") == 8_010
    assert batch_expected("paper") == 14_400
    assert batch_expected("full") == 36
    assert sum(batch_expected(name) for name in ("t1", "t3", "short", "paper", "full")) == 29_431
    assert batch_expected("timing") == 18


def test_t3_command_selects_only_trials_21_to_50() -> None:
    command = command_for(BATCHES["t3"][0])

    assert command[command.index("--trials") + 1] == "30"
    assert command[command.index("--trial-start") + 1] == "20"
    assert command[command.index("--workers") + 1] == "6"


def test_strict_timing_uses_isolated_root_and_one_worker() -> None:
    command = command_for(BATCHES["timing"][0])

    assert command[command.index("--out-dir") + 1] == "outputs/benchmark/det4_strict_timing"
    assert command[command.index("--workers") + 1] == "1"
