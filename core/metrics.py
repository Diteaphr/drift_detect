"""Per-event impact metrics for the operator view (plan §2.2).

"掉了多少、多久回來" is what a non-specialist actually reads a drift dashboard
for, and none of it existed: the pipeline reports detection delay, not
recovery. Everything here is derived from the rolling-accuracy series recorded
in ``core.run`` (sampled once per stride), never from ground truth -- these
numbers must stay computable on a stream with no drift schedule.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import drift_type
from .run import RunResult

# An event's aftermath is measured up to this many samples past confirmation,
# or until the next event's warning -- whichever comes first. Beyond that the
# recovery is no longer attributable to this drift.
IMPACT_HORIZON = 20_000

# Recovery = the rolling accuracy climbing back to this fraction of its
# pre-drift level. Not 100%: the rolling window jitters by a few points, so an
# exact-recovery test almost never fires even on a fully recovered model.
RECOVERY_RATIO = 0.95


def _series(result: RunResult) -> List[tuple]:
    return [(int(r["t"]), float(r["roll"])) for r in result.preq_hist
            if r.get("roll") is not None]


def _value_at(series: List[tuple], t: int) -> Optional[float]:
    """Last sampled rolling accuracy at or before ``t``."""
    val = None
    for ts, v in series:
        if ts > t:
            break
        val = v
    return val


def event_impact(result: RunResult, index: int) -> Dict[str, Any]:
    """Accuracy before / trough after / recovery for ``result.events[index]``.

    Any field can be ``None`` -- a drift near the end of the stream simply has
    no aftermath recorded, and the view must say so rather than invent one.
    """
    e = result.events[index]
    series = _series(result)
    warning_t = int(e["warning_t"])
    confirm_t = int(e["confirmation_t"])

    # The window closes at the next event's warning: after that, any dip
    # belongs to the next drift, not this one.
    nxt = result.events[index + 1]["warning_t"] if index + 1 < len(result.events) else None
    end = min(confirm_t + IMPACT_HORIZON, nxt if nxt is not None else 10**12)

    acc_before = _value_at(series, warning_t)
    after = [(ts, v) for ts, v in series if warning_t < ts <= end]

    if not after:
        return {
            "acc_before": acc_before, "acc_trough": None, "trough_t": None,
            "drop": None, "recovery_t": None, "recovery_steps": None,
            "acc_end": None, "recovered": None,
        }

    trough_t, acc_trough = min(after, key=lambda p: p[1])
    drop = None if acc_before is None else acc_before - acc_trough

    recovery_t = None
    if acc_before is not None:
        target = acc_before * RECOVERY_RATIO
        for ts, v in after:
            if ts > trough_t and v >= target:
                recovery_t = ts
                break

    return {
        "acc_before": acc_before,
        "acc_trough": acc_trough,
        "trough_t": trough_t,
        "drop": drop,
        "recovery_t": recovery_t,
        # Counted from the drift's start (warning_t), not from confirmation:
        # the accuracy can climb back before the system finishes confirming,
        # which measured from confirm_t would report a negative recovery.
        "recovery_steps": None if recovery_t is None else recovery_t - warning_t,
        "acc_end": after[-1][1],
        "recovered": None if acc_before is None else recovery_t is not None,
    }


def all_impacts(result: RunResult) -> List[Dict[str, Any]]:
    return [event_impact(result, i) for i in range(len(result.events))]


def run_summary(result: RunResult) -> Dict[str, Any]:
    """Headline numbers for the operator view's 本次總結 block."""
    impacts = all_impacts(result)
    recoveries = [i["recovery_steps"] for i in impacts if i["recovery_steps"] is not None]
    drops = [i["drop"] for i in impacts if i["drop"] is not None]
    return {
        "n_seen": result.n_seen,
        "n_events": len(result.events),
        "preq_acc": result.preq_acc,
        "roll_acc": result.roll_acc,
        "mean_recovery": (sum(recoveries) / len(recoveries)) if recoveries else None,
        "n_recovered": len(recoveries),
        "max_drop": max(drops) if drops else None,
        "elapsed": result.elapsed,
        "throughput": result.throughput,
    }


def type_counts(events: List[Dict[str, Any]]) -> Dict[str, int]:
    """How many events the Type-LDD classifier put in each type.

    Keys in display order: the three labels the classifier can emit, plus
    ``drift_type.PENDING_LABEL`` only when some event has no label (so a
    fully classified run shows three slices, not four).
    """
    counts = {label: 0 for label in drift_type.TYPE_LABELS}
    pending = 0
    for e in events:
        p = drift_type.predict(e)
        if p.label is None:
            pending += 1
        else:
            counts[p.label] += 1
    if pending:
        counts[drift_type.PENDING_LABEL] = pending
    return counts


OPERATOR_COST_NOTE = "模型成本指標待定義（docs/DASHBOARD_TWO_VIEWS_PLAN.md §2.1）"


def operator_cost(result: RunResult) -> Optional[Dict[str, Any]]:
    """模型成本 for the operator view -- **placeholder**.

    The raw counts exist (``cost_summary``: refits, samples refit on, pool
    slots, wall time), but none of them is a number a non-specialist can
    act on. What this should report -- and in what unit: seconds of compute,
    samples relabelled, a cost model over both -- is not decided, so the view
    shows a clearly marked pending tile until it is. Returns ``None`` until
    defined; when it does return, ``value`` is the display string and
    ``help`` the one-line explanation, and the view needs no change.
    """
    return None


def cost_summary(result: RunResult) -> Dict[str, Any]:
    """成本 / 效能 panel (plan §3.2).

    Retraining cost is counted in samples: every confirmed drift refits a fresh
    model on the whole warning buffer (``ecpf.py`` ``_fit_on_buffer``), so
    ``buffer_len`` is the real work done per event.
    """
    buf = [e["details"].get("buffer_len") for e in result.events]
    buf = [int(b) for b in buf if b is not None]
    return {
        "throughput": result.throughput,
        "elapsed": result.elapsed,
        "n_seen": result.n_seen,
        "pool_used": len(result.pool),
        "pool_max": result.opts.get("max_pool_size"),
        "n_refits": len(result.events),
        "refit_samples": sum(buf),
        "mean_buffer": (sum(buf) / len(buf)) if buf else None,
        "leader_swaps": result.leader_swaps,
    }
