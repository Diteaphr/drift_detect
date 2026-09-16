"""一般使用者介面 -- 「現在還能不能信這個模型？」(plan §2).

Shows conclusions and their consequences, never the process: no parameters, no
detector names, no UQ signals, no pool table, no precision/recall, no raw JSON
(plan §2.3). The status light and the chart update live while the stream runs
-- but on two different clocks: the light is text and repaints freely, while
the chart is a full Vega rebuild and gets a cadence scaled to the stream length
(``TARGET_CHART_REDRAWS``), so a 1M-row run costs the browser about as much as
a 20k one. Event cards and the summary are post-run only.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import altair as alt
import pandas as pd
import streamlit as st

from core import drift_type, insights, metrics
from core.run import (
    DEFAULT_OPTS,
    ROLL_WINDOW,
    RunResult,
    RunState,
    demo_streams,
    run_and_collect,
)

# A drift confirmed within this many samples of the end still counts as "just
# happened" -- the red light. Wide enough that a drift at the tail of a 20k run
# is not reported as 一切正常.
RECENT_WINDOW = 3_000

# How much of the chosen file to run. 0 = the whole file; the 1M-row long
# stream takes over a minute at that setting, hence the smaller defaults.
RUN_LENGTHS = {"2 萬筆（快）": 20_000, "10 萬筆": 100_000, "全部": 0}

STRIDE = 50          # sampling grid for the recorded series; not user-facing

# Roughly how many times the chart is rebuilt over a whole run, whatever the
# stream length. The engineer view fixes a redraw *interval* instead, which on
# a 1M-row stream means 20x the redraws of a 20k one; here the interval is
# derived from the length so the browser cost stays flat. Confirmed drifts
# always punch through, so no event goes unseen.
TARGET_CHART_REDRAWS = 120
STATUS_EVERY = 10    # ticks between status/progress repaints (text is cheap)

# Minimum seconds the light stays on one colour before it may change again.
# Without it a warning that opens and closes within a few hundred samples makes
# the biggest element on the page blink 🟢🟡🟢 in a fraction of a second, which
# reads as a glitch rather than as information.
STATUS_MIN_DWELL = 1.0

ACC_ROLL = "#0d7a4f"   # 近期準確率 -- the line that shows drops
ACC_CUM = "#a8b0ab"    # 累積準確率 -- context, deliberately recessive
DRIFT_RED = "#d03b3b"
WARN_AMBER = "#e8b93b"


# ----------------------------------------------------------------------
# Status
# ----------------------------------------------------------------------
def _status(result: RunResult) -> Dict[str, str]:
    return _status_at(result.events, result.n_total - 1, result.warning_active,
                      result.roll_acc, result.n_seen)


def _status_at(events: List[Dict[str, Any]], now: int, warning_active: bool,
               acc: Optional[float], n_seen: int) -> Dict[str, str]:
    """🟢 穩定 / 🟡 觀察中 / 🔴 剛發生漂移 + a one-line conclusion (plan §2.1).

    Takes loose values rather than a ``RunResult`` so the same wording drives
    the live light mid-run and the final one.
    """
    end = now
    acc_txt = "—" if acc is None else f"{acc:.0%}"
    # warning_t is the canonical event time everywhere in this project (it is
    # what the batch runner scores against), so the two views point at the
    # same sample when they say "第 X 筆".
    last = max((e["warning_t"] for e in events), default=None)

    if last is not None and end - last <= RECENT_WINDOW:
        return {
            "level": "error",
            "icon": "🔴",
            "title": "剛發生資料變化",
            # No canned "已換上更合適的模型" claim here: what actually happened
            # differs per event and is on the card.
            "line": f"最近一次變化在第 {last:,} 筆，近期準確率 {acc_txt}。",
        }
    if warning_active:
        return {
            "level": "warning",
            "icon": "🟡",
            "title": "觀察中",
            "line": f"偵測到疑似變化，正在蒐集資料確認中。近期準確率 {acc_txt}。",
        }
    if not events:
        return {
            "level": "success",
            "icon": "🟢",
            "title": "運作正常",
            "line": f"這 {n_seen:,} 筆沒有偵測到變化，近期準確率 {acc_txt}。",
        }
    return {
        "level": "success",
        "icon": "🟢",
        "title": "運作正常",
        "line": (f"{len(events)} 次變化都已處理完畢，"
                 f"近期準確率 {acc_txt}。"),
    }


class _StatusLight:
    """The status light, rate-limited to one colour change per
    ``STATUS_MIN_DWELL`` seconds.

    Only *colour* changes are held back; the same colour repaints freely so its
    numbers stay current, and that repaint does not restart the dwell clock. A
    state shorter than the dwell is skipped rather than queued: the display
    always shows a state the run is actually in, just not every one it passed
    through. The final post-run paint bypasses this entirely -- the last frame
    has to be the true one.
    """

    def __init__(self, ph, min_dwell: float = STATUS_MIN_DWELL) -> None:
        self._ph = ph
        self._min_dwell = min_dwell
        self._shown: Optional[Dict[str, str]] = None
        self._shown_at = 0.0

    def update(self, status: Dict[str, str], now: Optional[float] = None) -> None:
        now = time.perf_counter() if now is None else now
        if self._shown is None:
            self._paint(status, now)
            return
        if status["level"] == self._shown["level"]:
            if status != self._shown:
                self._paint(status, self._shown_at)  # same colour, fresh numbers
            return
        if now - self._shown_at >= self._min_dwell:
            self._paint(status, now)

    def _paint(self, status: Dict[str, str], at: float) -> None:
        _draw_status(self._ph, status)
        self._shown = status
        self._shown_at = at


def _draw_status(ph, status: Dict[str, str]) -> None:
    with ph.container():
        box = {"success": st.success, "warning": st.warning,
               "error": st.error}[status["level"]]
        box(f"### {status['icon']} {status['title']}\n\n{status['line']}")


# ----------------------------------------------------------------------
# The one chart (plan §2.1.2)
# ----------------------------------------------------------------------
def _draw_chart(ph, s: Any) -> None:
    """Paint the accuracy chart from a ``RunState`` (live) or ``RunResult``.

    Both carry ``preq_hist`` / ``warning_spans`` / ``events`` / ``n_total``;
    mid-run ``warning_spans`` includes the phase still open, so the amber band
    grows as the system deliberates.
    """
    with ph.container():
        _chart_body(s)


def _chart_body(result: Any) -> None:
    st.markdown("##### 模型表現")
    if not result.preq_hist:
        st.info("等待資料…")
        return

    df = pd.DataFrame(result.preq_hist)
    # Skip the warm-up transient: at the very first samples both curves are
    # averages over a handful of predictions and can sit near 0. Left in, one
    # such point drags the y axis down to zero and flattens the part that
    # matters (a few points of accuracy lost and regained).
    warm = df[df["t"] >= df["t"].iloc[0] + ROLL_WINDOW]
    if not warm.empty:
        df = warm

    long = df.melt(
        "t", value_vars=["roll", "preq"], var_name="series", value_name="acc"
    ).dropna()
    names = {"roll": f"近期準確率（最近 {ROLL_WINDOW} 筆）", "preq": "累積準確率"}
    long["series"] = long["series"].map(names)
    order = [names["roll"], names["preq"]]

    # Zoom the y axis to the data: anchored at 0 the whole story (a few points
    # of accuracy lost and regained) collapses into a flat line at the top.
    lo = max(0.0, float(long["acc"].min()) - 0.03)
    hi = min(1.0, float(long["acc"].max()) + 0.01)

    layers = []

    # Warning phases: the system suspected a change and was gathering evidence.
    if result.warning_spans:
        spans = pd.DataFrame(result.warning_spans, columns=["lo", "hi"])
        layers.append(
            alt.Chart(spans).mark_rect(color=WARN_AMBER, opacity=0.18)
            .encode(x="lo:Q", x2="hi:Q")
        )

    layers.append(
        alt.Chart(long).mark_line(size=2).encode(
            # Fixed to the whole stream: live, an auto-fitted axis rescales
            # on every redraw and the line appears to stand still.
            x=alt.X("t:Q", title="資料筆數",
                    scale=alt.Scale(domain=[0, result.n_total], nice=False)),
            y=alt.Y("acc:Q", title="準確率", axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[lo, hi], nice=False, clamp=True)),
            color=alt.Color("series:N", title=None,
                            scale=alt.Scale(domain=order,
                                            range=[ACC_ROLL, ACC_CUM]),
                            legend=alt.Legend(orient="top")),
            tooltip=["t:Q", "series:N", alt.Tooltip("acc:Q", format=".1%")],
        )
    )

    if result.events:
        # The rule marks the confirmation, i.e. the *right* edge of that
        # event's amber band -- the band's left edge is where the system first
        # suspected something. Drawn at warning_t instead, the rule lands on
        # the band's left edge and reads as if the system confirmed a change
        # before it suspected one.
        marks = pd.DataFrame({"t": [e["confirmation_t"] for e in result.events]})
        layers.append(
            alt.Chart(marks).mark_rule(color=DRIFT_RED, size=2)
            .encode(x="t:Q", tooltip=alt.Tooltip("t:Q", title="確認變化"))
        )

    # Not `.interactive()`: pan/zoom is an engineer-view affordance, and a
    # scale bound to a zoom selection can override the y domain set above.
    st.altair_chart(alt.layer(*layers).properties(height=300), width="stretch")
    st.caption("🟡 黃底 = 觀察期（左緣察覺、右緣 🔴 確認換模型）　深綠 = 近期　淺灰 = 累積")


# ----------------------------------------------------------------------
# Event cards (plan §2.1.3)
# ----------------------------------------------------------------------
def _action_text(event: Dict[str, Any]) -> str:
    """What the system did about this drift -- one short phrase for the card."""
    d = event.get("details") or {}
    acc_best = d.get("acc_best_on_warning")
    acc_new = d.get("acc_new_on_warning")
    slot = d.get("best_idx")
    if acc_best is None or acc_new is None:
        return "重新調整了模型"
    if acc_best >= acc_new:
        return f"切回第 {slot} 號舊模式"
    return "重新訓練新模型接手"


def _type_badge(pred: drift_type.DriftTypePrediction) -> str:
    """The drift-type slot, as one inline phrase for the card header.

    Only ``recurring`` is inferred today; the rest reads 待分類 until a
    classifier is wired in (plan §0). What that means is said once in the
    page footnote rather than on every card.
    """
    if pred.label is None:
        return f"{pred.icon} 待分類"
    conf = f"（信心 {pred.confidence_zh}）" if pred.confidence_zh else ""
    return f"{pred.icon} {pred.label_zh}{conf}"


def _draw_events(result: RunResult) -> None:
    st.markdown(f"##### 資料變化紀錄 · {len(result.events)} 次")
    if not result.events:
        st.info(f"這 {result.n_seen:,} 筆資料中沒有偵測到任何變化，模型穩定。")
        return

    pct = lambda v: "—" if v is None else f"{v:.0%}"  # noqa: E731
    impacts = metrics.all_impacts(result)

    # Three short lines per card: what/where, the damage, the response. The
    # numbers used to be st.metric tiles, which made each event a screen tall
    # for six numbers.
    for i in range(len(result.events) - 1, -1, -1):  # newest first
        e, imp = result.events[i], impacts[i]
        with st.container(border=True):
            st.markdown(
                f"**#{i + 1}　第 {e['warning_t']:,} 筆**　"
                f"{_type_badge(drift_type.predict(e))}"
            )

            # No "（-N 個百分點）" suffix: rounded to whole percents it
            # contradicts the two endpoints it sits next to (92% → 91% with a
            # 1.6-point drop reads as -2), and the arrow already says it.
            bits = [f"準確率 {pct(imp['acc_before'])} → {pct(imp['acc_trough'])}"]
            bits.append(
                f"{imp['recovery_steps']:,} 筆後恢復"
                if imp["recovery_steps"] is not None else "尚未回復"
            )
            # A warning can also confirm on the step it opens -- no observation
            # window, and no amber band on the chart to point at.
            gap = e["confirmation_t"] - e["warning_t"]
            bits.append(f"確認花了 {gap:,} 筆" if gap else "立刻確認")
            st.caption("　·　".join(bits))

            advice = insights.event_insight(result, i, imp)
            st.caption(f"→ {_action_text(e)}" + (f"　{advice}" if advice else ""))


# ----------------------------------------------------------------------
# Summary + export (plan §2.1.4-5)
# ----------------------------------------------------------------------
def _summary_markdown(result: RunResult, s: Dict[str, Any]) -> str:
    """One-page summary for download (plan §2.1.5). Same facts as the page."""
    status = _status(result)
    pct = lambda v: "—" if v is None else f"{v:.1%}"  # noqa: E731

    lines = [
        "# 模型健康狀態摘要",
        "",
        f"- 資料：{result.stream_label}",
        f"- 狀態：{status['icon']} {status['title']} — {status['line']}",
        f"- 檢查資料量：{s['n_seen']:,} 筆",
        f"- 偵測到變化：{s['n_events']} 次",
        f"- 整體準確率：{pct(s['preq_acc'])}　近期準確率：{pct(s['roll_acc'])}",
    ]
    if s["mean_recovery"] is not None:
        lines.append(
            f"- 平均恢復所需資料：{s['mean_recovery']:,.0f} 筆"
            f"（{s['n_recovered']} / {s['n_events']} 次已回復）"
        )
    if s["max_drop"] is not None:
        lines.append(f"- 最大準確率跌幅：{s['max_drop'] * 100:.0f} 個百分點")

    if result.events:
        lines += ["", "## 變化紀錄", "",
                  "| # | 位置 | 型態 | 變化前 | 最低 | 恢復所需 | 系統做了什麼 |",
                  "|---|---|---|---|---|---|---|"]
        for i, (e, imp) in enumerate(zip(result.events, metrics.all_impacts(result)), 1):
            pred = drift_type.predict(e)
            rec = ("尚未回復" if imp["recovery_steps"] is None
                   else f"{imp['recovery_steps']:,} 筆")
            lines.append(
                f"| {i} | 第 {e['warning_t']:,} 筆 | {pred.label_zh} | "
                f"{pct(imp['acc_before'])} | {pct(imp['acc_trough'])} | {rec} | "
                f"{_action_text(e)} |"
            )

    lines += ["", f"> 型態分類器尚未接上，「待分類」為介面示意欄位"
                  f"（docs/DASHBOARD_TWO_VIEWS_PLAN.md §0）。",
              f"> 自然語言建議：{insights.PLACEHOLDER_NOTE}。"]
    return "\n".join(lines)


def _draw_summary(result: RunResult) -> None:
    st.markdown("##### 本次總結")
    s = metrics.run_summary(result)

    cols = st.columns(4)
    cols[0].metric("檢查資料量", f"{s['n_seen']:,} 筆")
    cols[1].metric("偵測到變化", f"{s['n_events']} 次")
    cols[2].metric(
        "平均恢復所需資料",
        "—" if s["mean_recovery"] is None else f"{s['mean_recovery']:,.0f} 筆",
        help=f"只計算已回復的 {s['n_recovered']} 次變化",
    )
    cols[3].metric(
        "整體準確率",
        "—" if s["preq_acc"] is None else f"{s['preq_acc']:.1%}",
        help="從頭到尾累積的總成績",
    )

    note = insights.run_insight(result)
    if note:
        st.markdown(note)


def _draw_export(result: RunResult) -> None:
    """The download sits at the foot of the page: the summary block it exports
    now leads the page, and a download button is not what should greet the
    reader there.
    """
    st.download_button(
        "⬇ 下載一頁式摘要（Markdown）",
        _summary_markdown(result, metrics.run_summary(result)),
        file_name="drift_summary.md",
        mime="text/markdown",
    )


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def render() -> None:
    st.title("模型健康狀態")

    streams = demo_streams()
    with st.sidebar:
        st.header("選擇資料")
        if not streams:
            st.error("找不到資料：請確認 data/*_drift 內有 *.csv")
            return
        labels = {p: f"{label} · {p.name}" for label, p in streams}
        csv_path = st.selectbox("要檢查的資料", [p for _, p in streams],
                                format_func=lambda p: labels[p])
        # Length is part of "選哪份資料", not a detector knob -- the long
        # stream (1M rows) is unusable at a fixed 20k, and a full run of it
        # takes over a minute.
        n_label = st.selectbox("檢查多少筆", list(RUN_LENGTHS))
        start = st.button("▶ 開始檢查", type="primary", width="stretch")
        st.caption("偵測參數已預設好，不需調整。要調參數請切換到工程師介面。")

    result: Optional[RunResult] = st.session_state.get("run_result")
    if not start and result is None:
        st.info("在左側選一份資料，按「開始檢查」。")
        return

    # Painted in place: the same slots carry the live frames during the run and
    # the final render afterwards.
    ph_caption = st.empty()
    ph_status = st.empty()
    ph_progress = st.empty()
    ph_summary = st.empty()
    ph_chart = st.empty()
    ph_events = st.empty()

    if start:
        ph_caption.caption(f"資料：{labels[csv_path]} · 檢查中…")
        bar = ph_progress.progress(0.0, text="檢查中…")
        light = _StatusLight(ph_status)
        n_tick = 0
        chart_every = None
        last_warn = False

        def on_tick(s: RunState) -> None:
            nonlocal n_tick, chart_every, last_warn
            n_tick += 1
            if chart_every is None:
                # One tick per STRIDE samples, plus event triggers -- close
                # enough to size the cadence off the stream length.
                expected = max(1, s.n_total // STRIDE)
                chart_every = max(1, round(expected / TARGET_CHART_REDRAWS))

            # The light also repaints the moment a warning opens or closes, so
            # 🟡 觀察中 is not missed between two scheduled repaints.
            warn_edge = s.warning_active != last_warn
            last_warn = s.warning_active
            if warn_edge or s.drift or n_tick % STATUS_EVERY == 0:
                # `s.elapsed` is the run's own monotonic clock, so the dwell is
                # measured against the same time base everywhere.
                light.update(
                    _status_at(s.events, s.t, s.warning_active,
                               s.roll_acc, s.n_seen),
                    now=s.elapsed,
                )
                bar.progress(
                    min(1.0, s.t / s.n_total) if s.n_total else 0.0,
                    text=f"檢查中… {s.t:,} / {s.n_total:,} 筆，"
                         f"已發現 {len(s.events)} 次變化",
                )
            if s.drift or (n_tick - 1) % chart_every == 0:
                _draw_chart(ph_chart, s)

        result = run_and_collect(
            csv_path, warm_start=200, max_steps=RUN_LENGTHS[n_label],
            opts=DEFAULT_OPTS, stride=STRIDE,
            stream_label=labels[csv_path], on_tick=on_tick,
        )
        ph_progress.empty()
        st.session_state["run_result"] = result

    ph_caption.caption(f"資料：{result.stream_label} · 共檢查 {result.n_seen:,} 筆")
    _draw_status(ph_status, _status(result))
    with ph_summary.container():
        _draw_summary(result)
    _draw_chart(ph_chart, result)
    with ph_events.container():
        _draw_events(result)
    _draw_export(result)

    # Both placeholders (plan §0 型態分類 and §4 insight) are stated once here
    # rather than repeated on every card.
    st.caption(
        "「待分類」是介面示意：型態分類器（突變 / 漸變 / 緩慢累積）尚未接上，"
        "目前只有「舊概念重現」是真的判讀。每張卡片的建議文字待實作。"
    )
