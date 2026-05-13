"""
Run ConceptDriftPipeline on a stream and collect alert timestamps only (no ground truth).
"""

from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline


def load_stream_csv(path: Union[str, Path]) -> tuple[np.ndarray, np.ndarray]:
    """Load a CSV with target column ``y``; all other columns are features."""
    p = Path(path)
    df = pd.read_csv(p)
    if "y" not in df.columns:
        raise ValueError(f"CSV must contain a 'y' column: {p}")
    X = df.drop(columns=["y"]).values
    y = df["y"].values
    return X, y


def default_pipeline_config() -> PipelineConfig:
    """
    Default for **alert-only** collection: run the same streaming + meta/atom
    stack as a normal demo, but **disable ECPF** so
    :meth:`~src.pipeline.ConceptDriftPipeline.step` actually runs
    ``meta_detector.update_and_detect`` and fills ``pipeline.detections``.

    (Repository default :class:`PipelineConfig` has ``use_ecpf=True`` with empty
    oracle times, which silences meta drifts; this override fixes that for
    off-line alert logging.)

    Tuned to stay close to :file:`main.py` (Hoeffding + atom subset + two_stage).
    Override via :func:`pipeline_config_from_dict` or ``--config-json`` /
    ``--meta`` in :file:`scripts/collect_alert_times.py`.
    """
    return PipelineConfig(
        use_ecpf=False,
        meta_ks_window_size=100,
        atom_min_samples=30,
        update_batch_size=500,
        recurrence_threshold=0.15,
        model_type="ht",
        meta_detector_type="two_stage",
        selected_detectors=["ddm", "hddm_a", "page_hinkley"],
        atom_kwargs={
            "adwin": {"delta": 0.01},
            "ddm": {"drift_level": 3.0},
            "page_hinkley": {"threshold": 15.0},
            "ecdd": {"warning_level": 2.0, "drift_level": 3.0},
        },
    )


def pipeline_config_from_dict(overrides: Optional[Dict[str, Any]] = None) -> PipelineConfig:
    """Build config from :func:`default_pipeline_config` with JSON-serializable overrides."""
    base = default_pipeline_config()
    if not overrides:
        return base
    valid = {f.name for f in fields(PipelineConfig)}
    bad = set(overrides) - valid
    if bad:
        raise ValueError(f"Unknown PipelineConfig field(s): {sorted(bad)}")
    return replace(base, **{k: overrides[k] for k in overrides})


def run_pipeline_alerts(
    X: np.ndarray,
    y: np.ndarray,
    config: Optional[PipelineConfig] = None,
    warm_start: int = 50,
) -> List[int]:
    """
    Run the full pipeline on the stream and return alert **timestamps** (one per
    :class:`DriftDetection` in order of **occurrence**). Timestamps are then **sorted
    ascending** for stable comparison between runs; duplicate times are **kept** (same
    index as sorted multiset).
    """
    X = np.asarray(X)
    y = np.asarray(y).ravel()
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    n = len(y)
    if n != len(X):
        raise ValueError("X and y length mismatch")
    if warm_start < 1 or warm_start >= n:
        raise ValueError("warm_start must be in [1, n-1]")

    cfg = config or default_pipeline_config()
    pipeline = ConceptDriftPipeline(config=cfg)
    pipeline.warm_start(X[:warm_start], y[:warm_start])
    for i in range(warm_start, n):
        pipeline.step(X[i], y[i], index=i)
    times = [d.timestamp for d in pipeline.detections]
    return sorted(times)
