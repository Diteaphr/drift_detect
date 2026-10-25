"""
Sudden-vs-not drift classifier: six readable features + logistic regression.

The "simple baseline" of ``scripts/typeclf_retrain.py``, exported as plain numbers so
the pipeline can use it without scikit-learn state. The model file holds one fitted
model per cross-fitting fold plus a ``default`` model, and maps each training stream
(``"<dataset>|<stream>"``) to the fold whose model never saw it; streams outside the
training data use ``default``.

Input is the same as for Type-LDD: the leader's error history since the last
confirmation (``StreamBuffer.get_errors()``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from .config import DriftType

WINDOW, N_WIN = 15, 51
REPO = Path(__file__).resolve().parents[1]


def window_accuracy(errors: np.ndarray) -> np.ndarray:
    """51 windowed accuracies of the last 765 errors, padded like the Type-LDD adapter."""
    need = N_WIN * WINDOW
    e = np.asarray(errors, dtype=float)
    if len(e) == 0:
        e = np.zeros(1)
    if len(e) < need:
        e = np.concatenate([np.full(need - len(e), e[0]), e])
    e = e[-need:]
    return 1.0 - np.clip(e.reshape(N_WIN, WINDOW).mean(axis=1), 0.0, 1.0)


def simple_features(acc: np.ndarray) -> np.ndarray:
    """Six readable descriptors of the windowed error rate (one row per sample)."""
    e = 1.0 - acc
    d = np.diff(e, axis=1)
    pos = np.clip(d, 0, None)
    t = np.arange(20)
    late = e[:, -20:]
    slope = ((late - late.mean(1, keepdims=True)) * (t - t.mean())).sum(1) / ((t - t.mean()) ** 2).sum()
    return np.column_stack([
        d.max(1),                                   # largest single rise
        e.max(1) - e.min(1),                        # range
        d.max(1) / (pos.sum(1) + 1e-6),             # share of the total rise in the largest step
        slope,                                      # trend over the last 20 windows
        e[:, -10:].mean(1) - e[:, :10].mean(1),     # late minus early level
        d.std(1),                                   # roughness
    ])


class SimpleTypeClassifier:
    def __init__(self, params: Dict):
        self.mean = np.asarray(params["mean"], dtype=float)
        self.scale = np.asarray(params["scale"], dtype=float)
        self.coef = np.asarray(params["coef"], dtype=float)
        self.intercept = float(params["intercept"])

    def is_sudden(self, errors: np.ndarray) -> bool:
        x = (simple_features(window_accuracy(errors)[None, :])[0] - self.mean) / self.scale
        return float(x @ self.coef + self.intercept) > 0.0

    def predict_errors(self, errors: np.ndarray) -> DriftType:
        return DriftType.SUDDEN if self.is_sudden(errors) else DriftType.GRADUAL


_cache: Dict[tuple, SimpleTypeClassifier] = {}


def load_simple_classifier(path: str, stream_key: Optional[str] = None) -> SimpleTypeClassifier:
    """Model for ``stream_key`` from the file at ``path`` (relative paths: repo root)."""
    p = Path(path)
    p = p if p.is_absolute() else REPO / p
    spec = json.loads(p.read_text())
    fold = spec["stream_fold"].get(stream_key or "", "default")
    key = (str(p), fold)
    if key not in _cache:
        _cache[key] = SimpleTypeClassifier(spec["models"][fold])
    return _cache[key]
