"""Charts both views draw the same way."""

from __future__ import annotations

from typing import Dict

import altair as alt
import pandas as pd

from core import drift_type

# Slice colours, matched to the type badges (red / orange / blue). Validated
# with the dataviz palette checker: adjacent pairs clear the CVD and
# normal-vision floors; the orange is under 3:1 against the surface, which is
# why every slice also carries its count as a direct label. Pending is a
# neutral, not a type, and only appears when an event has no label.
TYPE_COLORS = {
    "sudden": "#d03b3b",
    "gradual": "#e0a020",
    "incremental": "#2f6fdb",
    drift_type.PENDING_LABEL: "#8a9290",
}


def type_pie(counts: Dict[str, int], *, height: int = 200) -> alt.Chart:
    """Donut of drift-type counts, legend on the right, count on each slice.

    ``counts`` comes from ``core.metrics.type_counts``; zero-count types are
    dropped so the legend lists only what occurred.
    """
    rows = [{"type": k, "n": v} for k, v in counts.items() if v > 0]
    df = pd.DataFrame(rows)
    order = [k for k in counts if k in set(df["type"])]

    base = alt.Chart(df).encode(
        theta=alt.Theta("n:Q", stack=True),
        color=alt.Color(
            "type:N", title=None,
            scale=alt.Scale(domain=order, range=[TYPE_COLORS[k] for k in order]),
            legend=alt.Legend(orient="right"),
        ),
        order=alt.Order("type_order:Q"),
        tooltip=[alt.Tooltip("type:N", title="型態"), alt.Tooltip("n:Q", title="次數")],
    ).transform_calculate(
        type_order=f"indexof({order!r}, datum.type)"
    )
    # 2px surface gap between slices (dataviz mark spec) via the stroke.
    arcs = base.mark_arc(innerRadius=int(height * 0.24), outerRadius=int(height * 0.42),
                         stroke="#ffffff", strokeWidth=2)
    # `color=alt.value(...)` overrides the inherited series-colour encoding;
    # left as a mark property the digits would be painted in the slice colour
    # and vanish into it.
    labels = base.mark_text(radius=int(height * 0.33), size=13,
                            fontWeight="bold").encode(
        text="n:Q", color=alt.value("#ffffff"),
    )
    return alt.layer(arcs, labels).properties(height=height)


POOL_LEADER = "#0d7a4f"   # status: the slot doing the predicting
POOL_OTHER = "#8a9290"    # neutral: a stored, idle expert
POOL_TRACK = "#e6e6e3"    # empty ring / unused slot


def pool_rings(pool: list, max_pool: int, *, columns: int = 5,
               size: int = 64) -> alt.Chart:
    """One ring per pool slot, fill = fade score relative to the top score.

    Compact replacement for a bar per slot: the live slots in slot order,
    padded with empty tracks up to ``max_pool`` so spare capacity shows,
    wrapped into rows of ``columns``, each with the fade score in the centre.
    The leader is green *and* labelled, never colour alone.

    Slot ids are not bounded by ``max_pool``: ``ecpf.slots`` grows and leaves
    ``None`` where an expert was evicted, so late in a run the live ids read
    21, 22, ... Indexing rings by id would then draw every ring empty.
    """
    fade_max = max((p["fade"] for p in pool), default=1) or 1
    rows = []
    for p in sorted(pool, key=lambda p: p["slot"]):
        rows.append({
            "order": len(rows), "slot": p["slot"],
            "label": f"slot {p['slot']} · leader" if p["is_leader"] else f"slot {p['slot']}",
            "fade": p["fade"], "text": str(p["fade"]),
            "end": min(1.0, max(0.0, p["fade"] / fade_max)),
            "color": POOL_LEADER if p["is_leader"] else POOL_OTHER,
        })
    for k in range(max(0, max_pool - len(rows))):
        rows.append({"order": len(rows), "slot": None, "label": f"空位 {k + 1}",
                     "fade": None, "text": "", "end": 0.0, "color": POOL_TRACK})
    df = pd.DataFrame(rows)
    # theta2 takes its type from theta, so both must be fields (a datum on
    # theta leaves theta2 untyped and Vega-Lite fails to compile the spec).
    df["start"] = 0.0
    df["full"] = 1.0

    # theta/theta2 share one scale: domain [0, 1] maps onto a full turn.
    theta_scale = alt.Scale(domain=[0, 1], range=[0, 6.283185307179586])
    r_out, r_in = int(size * 0.46), int(size * 0.34)
    base = alt.Chart(df).properties(width=size, height=size)
    track = base.mark_arc(innerRadius=r_in, outerRadius=r_out, color=POOL_TRACK).encode(
        theta=alt.Theta("start:Q", scale=theta_scale), theta2=alt.Theta2("full:Q"),
    )
    fill = base.mark_arc(innerRadius=r_in, outerRadius=r_out).encode(
        theta=alt.Theta("start:Q", scale=theta_scale), theta2=alt.Theta2("end:Q"),
        color=alt.Color("color:N", scale=None),
        tooltip=[alt.Tooltip("label:N", title="slot"),
                 alt.Tooltip("fade:Q", title="fade")],
    )
    score = base.mark_text(size=12, fontWeight="bold", color="#262626").encode(text="text:N")
    return (
        alt.layer(track, fill, score)
        .facet(facet=alt.Facet("label:N", title=None, sort=alt.SortField("order"),
                               header=alt.Header(labelFontSize=11, labelPadding=2)),
               columns=columns, spacing=4)
        .configure_view(stroke=None)
    )
