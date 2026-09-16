"""Drift-type prediction for the operator view (plan §0).

Fills the "這是什麼型態的漂移" slot on each event card with the Type-LDD FAN
ProtoNet's answer: ``sudden`` / ``gradual`` / ``incremental``.
``src/pipeline.py`` runs the classifier (``src/type_ldd``, checkpoint in
``checkpoints/type_ldd``) once, at ECPF drift confirmation, on the
per-instance error history, and records the label in
``details["type_ldd_prediction"]``. Nothing here re-runs the model: the view
reads what the run recorded, so a stored ``RunResult`` renders the same as a
live one.

The label is shown as-is (English), which is what the classifier emits and
what the literature calls these types; ``TYPE_ZH`` is available for prose.

ECPF's reuse decision (``acc_best_on_warning >= acc_new_on_warning``) is
exposed as ``reused`` alongside, not folded into the label: it is a statement
about the model pool ("a stored expert fit this drift"), not about the shape
of the drift, and the two are shown separately so neither hides the other.

Confidence is deliberately left ``None``. The classifier's ``predict_proba``
is a softmax over negative centroid distances and saturates to ~0/1 on real
error sequences -- pushed through the 高/中/低 bands it would read "高" on
every event, misfires included. Until the scores are calibrated the badge
shows the label alone.

Deliberately **not** used as a source: the file name / folder
(``data/sudden_drift/…``). That is ground truth, not a system output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

# What the Type-LDD adapter can emit (src/type_ldd/infer.py IDX_TO_DRIFT_TYPE).
# Anything else in the details -- or the key missing, as on non-ECPF paths --
# means the classifier did not answer.
TYPE_LABELS = ("sudden", "gradual", "incremental")

# Chinese names for prose / tooltips. The badge itself shows the English label.
TYPE_ZH = {
    "sudden": "突變",
    "gradual": "漸變",
    "incremental": "緩慢累積",
}

# Streamlit badge colours (`:red-badge[...]` in markdown / `st.badge`). Hot to
# cold by how abrupt the change is. Pending is grey so it reads as "no answer",
# not a type.
TYPE_COLOR = {
    "sudden": "red",
    "gradual": "orange",
    "incremental": "blue",
}

PENDING_LABEL = "待分類"


@dataclass
class DriftTypePrediction:
    """One event's drift type.

    ``label is None`` means "no classifier answered", which the view must show
    as pending rather than guessing a type.
    """

    label: Optional[str]
    confidence: Optional[float]
    source: str          # "type_ldd" | "placeholder"
    is_placeholder: bool
    reused: bool = False  # ECPF reused a pooled expert for this drift

    @property
    def text(self) -> str:
        """What the badge shows: the classifier's label, or 待分類."""
        return self.label if self.label is not None else PENDING_LABEL

    @property
    def label_zh(self) -> str:
        if self.label is None:
            return PENDING_LABEL
        return TYPE_ZH.get(self.label, self.label)

    @property
    def color(self) -> str:
        return TYPE_COLOR.get(self.label or "", "gray")

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
    """Read one drift event's type. See the module docstring for scope."""
    d = event.get("details") or {}
    acc_best = d.get("acc_best_on_warning")
    acc_new = d.get("acc_new_on_warning")
    reused = acc_best is not None and acc_new is not None and acc_best >= acc_new

    # Only the classifier's own key counts. `event["drift_type"]` carries the
    # same value on the ECPF path but is not read here: on other paths it is a
    # hardcoded default, and a default rendered as a verdict is worse than 待分類.
    label = d.get("type_ldd_prediction")
    if label in TYPE_LABELS:
        return DriftTypePrediction(
            label=str(label), confidence=None,
            source="type_ldd", is_placeholder=False, reused=reused,
        )

    return DriftTypePrediction(
        label=None, confidence=None,
        source="placeholder", is_placeholder=True, reused=reused,
    )
