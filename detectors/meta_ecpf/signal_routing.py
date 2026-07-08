"""Signal extraction for ECPF ADWIN-family scalar detectors."""

from __future__ import annotations

import math
import logging
from typing import Any, Dict, List, Optional

from src.uq_extractor import UQExtractor


SIGNAL_CHOICES = {"error", "uq_mi", "uq_vote", "uq_entropy", "uq_variance"}
logger = logging.getLogger(__name__)
_WARNED_MISSING_PROBA: set[str] = set()


def normalize_signal_name(signal: str) -> str:
    name = signal.lower()
    aliases = {
        "err": "error",
        "err01": "error",
        "0_1_loss": "error",
        "zero_one_loss": "error",
        "uq_mi_like": "uq_mi",
        "mi_like": "uq_mi",
        "uq_vote_disagreement": "uq_vote",
        "vote_disagreement": "uq_vote",
        "uq_predictive_entropy": "uq_entropy",
        "predictive_entropy": "uq_entropy",
        "uq_variance_eu": "uq_variance",
        "variance_eu": "uq_variance",
        "prob_variance": "uq_variance",
    }
    name = aliases.get(name, name)
    if name not in SIGNAL_CHOICES:
        raise ValueError(f"Unknown ECPF signal {signal!r}. Choose from {sorted(SIGNAL_CHOICES)}")
    return name


def extract_signal(
    signal: str,
    *,
    y_true: float,
    y_pred: float,
    err: float,
    proba_matrix: Optional[List[Dict[Any, float]]],
    num_classes: Optional[int] = None,
) -> float:
    """Extract one scalar stream value for a detector.

    ``error`` is always the supervised zero-one loss.  UQ signals are computed
    from the per-tree probability matrix when available, otherwise they fall
    back to 0.0 so non-forest models can still run the same CLI surface.
    """

    name = normalize_signal_name(signal)
    if name == "error":
        return 1.0 if int(round(float(y_pred))) != int(round(float(y_true))) else 0.0
    if not proba_matrix:
        if name not in _WARNED_MISSING_PROBA:
            logger.warning(
                "ECPF UQ signal %s requested but proba_matrix is unavailable; "
                "falling back to 0.0. Use a model backend that exposes "
                "predict_proba_matrix, e.g. model_type='hf'.",
                name,
            )
            _WARNED_MISSING_PROBA.add(name)
        return 0.0
    if name == "uq_mi":
        return _normalize_entropy_like(
            UQExtractor("mi_like", num_classes=num_classes).extract(proba_matrix),
            proba_matrix,
            num_classes=num_classes,
        )
    if name == "uq_vote":
        return float(
            UQExtractor("vote_disagreement", num_classes=num_classes).extract(
                proba_matrix
            )
        )
    if name == "uq_entropy":
        return _normalize_entropy_like(
            UQExtractor("predictive_entropy", num_classes=num_classes).extract(
                proba_matrix
            ),
            proba_matrix,
            num_classes=num_classes,
        )
    if name == "uq_variance":
        return _normalize_variance_eu(
            UQExtractor("variance_eu", num_classes=num_classes).extract(
                proba_matrix
            ),
            proba_matrix,
            num_classes=num_classes,
        )
    return float(err)


def _normalize_entropy_like(
    value: float,
    proba_matrix: List[Dict[Any, float]],
    *,
    num_classes: Optional[int] = None,
) -> float:
    classes: set[Any] = set()
    for proba in proba_matrix:
        classes.update(proba.keys())
    n_classes = int(num_classes) if num_classes is not None else len(classes)
    if n_classes <= 1:
        return 0.0
    max_entropy = math.log2(n_classes)
    if max_entropy <= 0.0:
        return 0.0
    return max(0.0, min(1.0, float(value) / max_entropy))


def _normalize_variance_eu(
    value: float,
    proba_matrix: List[Dict[Any, float]],
    *,
    num_classes: Optional[int] = None,
) -> float:
    classes: set[Any] = set()
    for proba in proba_matrix:
        classes.update(proba.keys())
    n_classes = int(num_classes) if num_classes is not None else len(classes)
    if n_classes <= 1:
        return 0.0
    max_variance_eu = 1.0 - (1.0 / n_classes)
    if max_variance_eu <= 0.0:
        return 0.0
    return max(0.0, min(1.0, float(value) / max_variance_eu))
