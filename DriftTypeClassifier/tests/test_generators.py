"""Basic tests for generators."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.generators import generate_sudden_streams, generate_gradual_streams, generate_incremental_streams, generate_all_streams


def test_sudden():
    streams = generate_sudden_streams(5, 500, 4, random_seed=42)
    assert len(streams) == 5
    for s in streams:
        assert s.X.shape == (500, 4)
        assert s.y.shape == (500,)
        assert s.drift_type == "sudden"
        assert 0 <= s.t_drift < 500


def test_gradual():
    streams = generate_gradual_streams(5, 500, 4, gradual_window_size=50, random_seed=42)
    assert len(streams) == 5
    for s in streams:
        assert s.drift_type == "gradual"


def test_incremental():
    streams = generate_incremental_streams(5, 500, 4, incremental_window_size=80, random_seed=42)
    assert len(streams) == 5
    for s in streams:
        assert s.drift_type == "incremental"


def test_all():
    streams = generate_all_streams(n_streams=30, streams_per_class=10, stream_length=300, random_seed=42)
    assert len(streams) == 30
    types = [s.drift_type for s in streams]
    assert types.count("sudden") == 10
    assert types.count("gradual") == 10
    assert types.count("incremental") == 10
