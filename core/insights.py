"""事件 → 自然語言 insight -- **placeholder** (plan §4: 還沒實作 先放 placeholder).

The operator view calls these and renders whatever comes back inside a clearly
marked placeholder block, so the section exists in the layout (and in the demo)
before the wording engine does. When §4 gets implemented, fill these in and the
view needs no change.

Note the split: the *facts* the operator view shows -- 準確率掉幅、恢復步數、
系統做了什麼 -- are computed in ``core.metrics`` and rendered directly. Only
the prose lives here. A future LLM pass must polish these sentences, never
produce the numbers.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .run import RunResult

PLACEHOLDER_NOTE = "自然語言 insight 尚未實作（見 docs/DASHBOARD_TWO_VIEWS_PLAN.md §4）"


def event_insight(result: RunResult, index: int,
                  impact: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """One sentence of advice for a single drift event. ``None`` until §4."""
    return None


def run_insight(result: RunResult) -> Optional[str]:
    """A paragraph summarising the whole run. ``None`` until §4."""
    return None
