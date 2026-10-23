"""Model-pool diagnostics from an ECPF pool trace (``ECPFMetaLearner.pool_trace_dict``).

Written by ``scripts/run_benchmark.py --pool-trace`` as ``pool_metrics.json`` next
to a run's ``metrics.json``. These are diagnostics of the pool mechanism, not
literature metrics: the benchmark metrics stay in ``evaluate_run.py``.

* pool memory: time-weighted mean / peak / final stored KB and the KB x
  instances integral over the stream (the pool's own "RAM-hours");
* evictions by reason, with size, age and reuse history of what was dropped;
* regret: drifts where a recently evicted expert would have scored higher on
  the warning buffer than the best expert still stored;
* recovery: prequential accuracy in the ``window`` instances after each alarm;
* reuse: distribution of reuse values (reused copy vs. its alternative);
* time spent in pool operations (excluding the regret diagnostic).
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Sequence

import numpy as np


def _step_integral(timeline: Sequence[Sequence[float]], end: int, col: int) -> Optional[float]:
    """Integral of a step function given as (t, ...) change points up to ``end``."""
    pts = sorted((int(r[0]), float(r[col])) for r in timeline)
    if not pts or end <= pts[0][0]:
        return None
    total = 0.0
    for (t, v), (t_next, _) in zip(pts, pts[1:] + [(end, 0.0)]):
        t_next = min(t_next, end)
        if t_next > t:
            total += v * (t_next - t)
    return total


def _recovery(y_true: np.ndarray, y_pred: np.ndarray, alarms: Sequence[int], window: int) -> Dict[str, Any]:
    valid = ~np.isnan(y_pred)
    correct = (y_pred == y_true) & valid
    per_alarm: List[float] = []
    hits = n = 0
    for a in alarms:
        lo, hi = int(a) + 1, min(int(a) + 1 + window, len(y_true))
        m = valid[lo:hi]
        if m.sum() == 0:
            continue
        c = int(correct[lo:hi].sum())
        per_alarm.append(c / int(m.sum()))
        hits += c
        n += int(m.sum())
    return {
        "recovery_window": window,
        "recovery_n_alarms": len(per_alarm),
        "recovery_acc_mean": float(np.mean(per_alarm)) if per_alarm else None,
        "recovery_acc_pooled": hits / n if n else None,
    }


def pool_metrics(
    trace: Dict[str, Any],
    y_true: np.ndarray,
    y_pred: np.ndarray,
    alarm_idx: Sequence[int],
    task: str,
    window: Optional[int] = None,
) -> Dict[str, Any]:
    n = len(y_true)
    tl = trace.get("timeline", [])
    out: Dict[str, Any] = {"fade_policy": trace.get("fade_policy")}

    kb_int = _step_integral(tl, n, 2)
    slot_int = _step_integral(tl, n, 1)
    span = n - min(int(r[0]) for r in tl) if tl else 0
    out.update({
        "pool_kb_mean": kb_int / span if kb_int is not None and span else None,
        "pool_kb_peak": max(float(r[2]) for r in tl) if tl else None,
        "pool_kb_final": float(tl[-1][2]) if tl else None,
        "pool_slots_mean": slot_int / span if slot_int is not None and span else None,
        "pool_kb_x_instances": kb_int,
    })

    ev = trace.get("evictions", [])
    reasons = Counter(e["reason"] for e in ev)
    dropped = [e for e in ev if e["reason"] != "merge"]
    out.update({
        "evictions_total": len(ev),
        **{f"evictions_{r}": int(reasons.get(r, 0)) for r in ("fade", "cap", "budget", "merge")},
        "evicted_kb_mean": float(np.mean([e["kb"] for e in dropped])) if dropped else None,
        "evicted_age_mean": float(np.mean([e["age_drifts"] for e in dropped])) if dropped else None,
        "evicted_never_reused_frac": (
            float(np.mean([e["reuses"] == 0 for e in dropped])) if dropped else None
        ),
    })

    rg = trace.get("regret", [])
    regrets = [r for r in rg if r["regret"]]
    out.update({
        "regret_checks": len(rg),
        "regret_count": len(regrets),
        "regret_rate": len(regrets) / len(rg) if rg else None,
        "regret_gap_mean": float(np.mean([r["gap"] for r in regrets])) if regrets else None,
    })

    rv = np.asarray([r["reuse_value"] for r in trace.get("reuse_values", [])], dtype=float)
    ends = [r.get("leader_is_reused_at_end") for r in trace.get("reuse_values", [])]
    ends = [e for e in ends if e is not None]
    out.update({
        "reuse_episodes": int(rv.size),
        "reuse_value_mean": float(rv.mean()) if rv.size else None,
        "reuse_value_median": float(np.median(rv)) if rv.size else None,
        "reuse_value_q10": float(np.quantile(rv, 0.1)) if rv.size else None,
        "reuse_value_q90": float(np.quantile(rv, 0.9)) if rv.size else None,
        "reuse_positive_frac": float((rv > 0).mean()) if rv.size else None,
        "reuse_kept_leader_frac": float(np.mean(ends)) if ends else None,
    })

    out.update({
        "num_drifts": trace.get("num_drifts"),
        "pool_time_s": trace.get("pool_time_s"),
        "sizing_time_s": trace.get("sizing_time_s"),
        "trace_time_s": trace.get("trace_time_s"),
    })
    if task != "regression":
        out.update(_recovery(np.asarray(y_true, float), np.asarray(y_pred, float), alarm_idx,
                             int(window or trace.get("reuse_value_window") or 500)))
    return out
