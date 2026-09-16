"""Drift-type prediction -- **interface placeholder** (plan §0).

The operator view has a slot for "這是什麼型態的漂移，有多確定"; the classifier
that fills it is not wired in yet. This module is that slot: one function, one
return type, so swapping the real model in later touches nothing in the views.

What is real today and what is not:

* ``recurring`` **is** real. It does not need a classifier -- when ECPF's best
  reused expert beats a freshly trained one on the warning buffer, the concept
  demonstrably existed in the pool before (plan §0.3). That comes straight off
  the event details.
* ``sudden`` / ``gradual`` / ``incremental`` are **not** predicted yet. Those
  need one of the two classifiers listed in plan §0
  (``src.drift_type_classifier_dtc_rf.classify_drift_type``, cheap, no
  confidence; or ``DriftTypeClassifier``'s FAN+ProtoNet, which returns
  probabilities). Until one is connected, ``predict`` returns ``label=None``
  and the view renders a clearly-marked pending badge.

Deliberately **not** used as a source: the file name / folder
(``data/sudden_drift/…``). That is ground truth, not a system output.

``DriftDetection.drift_type`` off the pipeline is not consulted either: the
ECPF path hardcodes ``DriftType.SUDDEN`` (``src/pipeline.py:817``), so reading
it would show "sudden" for every event and look like a working classifier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Display names, keyed by the labels the real classifier will emit.
TYPE_ZH = {
    "sudden": "突變",
    "gradual": "漸變",
    "incremental": "緩慢累積",
    "recurring": "舊概念重現",
}

TYPE_ICON = {
    "sudden": "⚡",
    "gradual": "🌊",
    "incremental": "📈",
    "recurring": "🔁",
}


@dataclass
class DriftTypePrediction:
    """One event's drift type.

    ``label is None`` means "no classifier answered", which the view must show
    as pending rather than guessing a type.
    """

    label: Optional[str]
    confidence: Optional[float]
    source: str          # "ecpf_reuse" | "placeholder" | (later) "dtc_rf" / "protonet"
    is_placeholder: bool

    @property
    def label_zh(self) -> str:
        if self.label is None:
            return "待分類"
        return TYPE_ZH.get(self.label, self.label)

    @property
    def icon(self) -> str:
        return TYPE_ICON.get(self.label or "", "🔍")

    @property
    def confidence_zh(self) -> Optional[str]:
        """Text bands, not a raw number -- plan §2.2."""
        if self.confidence is None:
            return None
        if self.confidence >= 0.8:
            return "高"
        if self.confidence >= 0.6:
            return "中"
        return "低"


def predict(event: Dict[str, Any]) -> DriftTypePrediction:
    """Classify one drift event's type. See the module docstring for scope."""
    d = event.get("details") or {}
    acc_best = d.get("acc_best_on_warning")
    acc_new = d.get("acc_new_on_warning")

    if acc_best is not None and acc_new is not None and acc_best >= acc_new:
        # A pooled expert beat a model trained on this drift's own data: the
        # concept is one the system has seen before.
        return DriftTypePrediction(
            label="recurring", confidence=None,
            source="ecpf_reuse", is_placeholder=False,
        )

    return DriftTypePrediction(
        label=None, confidence=None,
        source="placeholder", is_placeholder=True,
    )
