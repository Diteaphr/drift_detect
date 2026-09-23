"""工程師介面 -- the original monitor console (plan §3).

Panels ①-⑤ + ⑧ are the ones that lived in ``monitor_app.py``, moved here
unchanged in behaviour but now reading their values off ``core.run``'s
``RunState`` / ``RunResult`` instead of poking at pipeline internals. That is
what lets the same panel render live during a run *and* from a stored result
after a role switch.

New in the two-view split (plan §3):
  1. the panels are grouped and labelled by layer (signal → detector → ECPF)
  2. ⑥ 成本 · 效能
  3. ⑦ 原始資料下載
  4. a ground-truth overlay toggle for panel ①
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from core import drift_type, metrics
from views.charts import pool_rings, type_pie
from core.run import (
    DETECTOR_CHOICES,
    GT_TOLERANCE,
    HIST_POINTS,
    ROLL_WINDOW,
    SIGNAL_CHOICES,
    RunResult,
    RunState,
    demo_streams,
    run_and_collect,
    stream_length,
)

# Scored with the batch runner's own definitions so the monitor's report and a
# `run_ecpf_uq_experiment.py` report of the same run cannot diverge. That module
# is guarded by `if __name__ == "__main__"`, so importing it is side-effect free.
from run_ecpf_uq_experiment import _detection_delay, _false_warning_rate

STRIDE = 50  # sampling grid for the recorded series; not user-facing

# The three chart panels (② prequential, ① signal, ④ duel) each rebuild a full
# Vega view every time they are drawn -- an order of magnitude costlier in the
# browser than the metric/text panels. Redrawing them on every trigger is what
# stalls long runs client-side: on a 100k file the script itself finishes in
# ~30s, but it emits ~900 chart rebuilds and the browser falls minutes behind.
# Raising STRIDE alone does not fix it, because drift / warning / leader-swap
# triggers set a floor of ~90 redraws that STRIDE cannot reach past. So charts
# get their own cadence, derived per run from the stream length (as in the
# operator view) so the browser cost stays flat whether the file is 20k rows or
# 1M. Confirmed drifts always punch through, so no event goes unseen.
#
# Matched to the operator view so the line grows at the same pace: fewer
# redraws than that reads as the chart jumping forward in chunks. Three charts
# per redraw makes this 3x that view's rebuild count, which is affordable only
# because the count no longer scales with the stream -- the old fixed interval
# put a 1M-row run at ~6,000 rebuilds against this 360.
TARGET_CHART_REDRAWS = 120

# ----------------------------------------------------------------------
# Sidebar tooltips
# ----------------------------------------------------------------------
# Written for non-specialists: what the knob is, then what moving it does.
# Keep the "調大/調小" contrast -- it is the part users actually act on.
HELP_CSV = """
要監控的資料串流檔案。

每個檔案是一段依時間排序的資料，中途概念會改變（例如同樣的特徵，
正確答案換了一套規則），系統的任務就是及時察覺這些變化。
換檔案等於換一個題目，難易度和漂移次數都會不同。

檔名前面的標籤是漂移型態：sudden（突變）、gradual（漸變）、
incremental（緩慢累積）、recurring（舊概念會再回來）。
每種型態各挑了幾份供展示。
"""

HELP_WARM_START = """
暖身筆數：一開始先讓模型安靜地學這麼多筆資料，期間不判定漂移。

模型剛開始什麼都不會，錯誤率天然就很高，這時去偵測「錯誤變多」
只會得到假警報。
**調大**：開頭更穩，但太大會讓第一次真實漂移被錯過。
**調小**：更早開始監控，但開頭容易出現假漂移。
"""

HELP_MAX_STEPS = """
這次最多跑幾筆資料。預設是所選檔案的總筆數（換檔會跟著變），`0` 也代表整個檔案跑完。

**調小**：很快看到結果，適合先試參數；但只看到資料的前段，
後面的漂移不會出現。
**調大或設 0**：完整結果，但要等比較久。
"""

HELP_SIGNAL_MODE = """
偵測漂移的整體策略，決定「怎麼判斷資料變了」。

- **detector**：最單純，用一組內建偵測器看錯誤率。想快速上手選這個。
- **dual_adwin / dual_seed / dual_seqdrift2**：兩階段把關，先發預警、
  再確認漂移，用的是三種不同的統計方法。誤報通常比較少。
- **uq_warning**：先用模型的「不確定感」提早示警，再用錯誤率確認。
  通常反應最快，但也最容易緊張。

選了不同模式，下面的 signal / detector 欄位才會實際生效。
"""

HELP_WARNING_SIGNAL = """
用哪個數值來發「預警」（可能要變了，先準備）。

- **error**：看模型答錯的比例，最直觀也最穩。
- **uq_*** 開頭：看模型自己有多猶豫（不同的猶豫算法）。
  模型往往在真正答錯之前就先開始猶豫，所以能更早示警，
  代價是有時候只是虛驚一場。
"""

HELP_DRIFT_SIGNAL = """
用哪個數值來「確認」漂移真的發生、該換模型了。

選項意義同 warning_signal。這是最後拍板的依據，
建議留 **error**：確認階段求穩，用實際答錯率最不會誤判。
"""

HELP_WARNING_DETECTOR = """
預警階段使用的統計方法（留空 `None` 表示交給 signal_mode 預設決定）。

三種方法都在問「最近的表現是不是和之前明顯不同」，只是算法不同：
**adwin** 反應快、最常用；**seed** 較節省記憶體；
**seqdrift2** 對緩慢的變化較敏感。不確定就留空。
"""

HELP_DRIFT_DETECTOR = """
確認階段使用的統計方法（留空 `None` 表示交給 signal_mode 預設決定）。

選項意義同 warning_detector。與預警用不同方法可以互相把關，
減少兩者同時看走眼的機會。
"""

HELP_DELTA = """
確認漂移的敏感度（給 drift_detector 用）。

**調大**（如 0.1）：比較神經質，漂移抓得早，但假警報變多，
模型會被頻繁換掉。
**調小**（如 0.01）：比較保守，只有很確定才認定漂移，
假警報少但反應慢。

預設 0.01。多類別 RBF 串流上掃過 0.05 / 0.01 / 0.002 / 0.0002：
0.01 比論文的 0.05 少 4 次誤報、準確率高 0.7 個百分點，16 個真漂移一樣抓到 15 個；
再收到 0.002 誤報雖降到 26 次，但會漏掉 3 個真漂移。
"""

HELP_DELTA_W = """
預警的敏感度（給 warning_detector 用）。

意義同 detector_delta，但作用在「提早示警」這一關。
通常設得比 detector_delta 大（預設 0.1 對 0.01），
意思是預警寧可寬鬆一點、早點注意，真正的把關留給確認階段。
"""

HELP_MIN_INSTANCES = """
ADWIN 的靜默期（River `grace_period`）：偵測器**每次重置後**至少要看過這麼多筆
才允許再報變化。開頭算一次，之後每次漂移確認都會重置 warning 和 drift 兩個偵測器、
重新計時 —— 所以它實際上是「確認漂移後的冷卻時間」。

**只有大於相鄰警報的間距才有作用。** 在 sudden_sea100k_g00 上事件最短相隔 ~600 筆，
30 或 300 都攔不到任何一個；設到 3000 才把換模型後的餘震誤報從 15 個壓到 11 個，
真漂移一個沒漏（它們至少相隔 5,000 多筆）。

**調大**：砍掉確認後不久的重複警報；但靜默期內若真的又漂移，會直接漏掉。
**調小**：反應快，餘震照報。
預設 30 是全專案共用的 `PipelineConfig` 值，批次腳本也用它。
"""

HELP_MAX_POOL_SIZE = """
最多保留幾個舊模型備用。

這套系統的重點是「概念會重複出現」：今天的狀況可能和上個月一樣。
留著舊模型，之後遇到相同狀況就能直接調回來用，不必從零學起。
**調大**：更多歷史狀況能被重複利用，但佔用較多記憶體。
**調小**：省資源，但舊模型會被淘汰，重複出現的概念得重學。
"""

HELP_SIMILARITY_MARGIN = """
兩個模型多常給出一樣的答案（一致度），達到這個門檻就合併成一個。

池裡累積久了，常常會有兩個模型其實學到同一套規則，
留著兩份沒有意義，白佔位置。系統會持續記錄每對模型的預測一致度，
一旦 ≥ 這個門檻，就留下比較準的那個，把另一個淘汰、fade 分數併過去。
**調高**：門檻更嚴，更少合併，池子留得較細、較大。
**調低**：門檻更鬆，更常合併，池子更精簡但可能誤把不同概念併在一起。
"""

HELP_FADE_POINTS = """
leader 每做一輪 +幾分、其他 slot 每輪 -1 分，分數見底就淘汰。

這是模型池的「活體維護」機制：常被選中當 leader 的模型分數越滾越高，
長期沒被選中的慢慢扣到 0 就被移除，騰出位置給新模型。
**調大**：leader 加分更多，舊模型能撐更久才被淘汰，池子較滿。
**調小**：淘汰更快，池子更精簡，但可能太快丟掉還有用的舊概念。
"""

HELP_FADE_ENABLED = """
是否啟用上面的淡出淘汰機制。

**開啟**（預設）：沒用的模型會被自動清掉，池子大小自我調節。
**關閉**：fade 分數不再被更新（永遠停在剛加入時的分數），
模型只會在池滿（達 `ecpf_max_pool_size`）時才被踢，
且因為分數都沒在變，淘汰對象基本上等於隨機／先進先踢。
"""

HELP_MODEL_TYPE = """
底層預測模型。

- **ht**（單棵決策樹）：輕量、快。
- **hf**（一片樹林）：多棵樹一起投票，較準，也才能算出「不確定感」。

注意：只要 signal 選了任何 `uq_*` 選項，系統會自動改用 **hf**，
因為單棵樹算不出不確定感。
"""

HELP_ACC_WINDOW = """
最近 500 筆預測的正確率，只看近況，不代表整趟跑下來的總表現。

漂移剛發生時這個數字會明顯跌下去，之後隨著 leader 換上更適合的模型
慢慢回升——這正是它的用途：看「現在」好不好，反應快但會晃。
想看整趟跑下來真正的總成績，見下方「整體預測 · prequential accuracy」。
"""

# Tooltip for the prequential-accuracy panel (below the header).
HELP_PANEL_PREQ = """
從 `warm_start` 之後累積到目前為止的整體正確率（test-then-train），
不會隨時間被沖淡或遺忘——這跟上方「Accuracy（窗）」只看最近 500 筆不同。

這條線通常會愈跑愈平：早期單一漂移對它的影響大，跑得夠久後，
單一事件對整體平均的影響會被稀釋，曲線因此收斂變穩定。
數值定義跟 `run_ecpf_uq_experiment` 報表裡的 `prequential_accuracy`
完全一致，所以這裡最終看到的數字可以直接拿去跟批次報表對照。
"""

# Tooltip for panel ① (the signal time-series chart).
HELP_PANEL_SIGNAL = f"""
這張圖把系統每一步監看的數值畫成隨時間變化的曲線。由後往前疊三層：

**彩色曲線（會上下起伏）** — 主角，是實際被監看的訊號值。
- 🟢 **warning signal**（淺綠線）：左欄 `warning_signal` 選的訊號，
  負責「提早示警」。線越高代表錯誤率或不確定感越高。
- 🟢 **drift signal**（深綠線）：`drift_signal` 選的訊號，負責「確認漂移」。
- 兩者若選同一個訊號，只會有一條綠線，圖例直接標該訊號的名字（如 `error`）。

**灰色背景（不會動）** — 對照用的標準答案（左側「① 圖疊 ground truth」可關）。
- 灰帶：ground truth 漂移 ± `gt_tolerance`（左側可調，預設 {GT_TOLERANCE}），判定為 TP 的容許窗。
- 灰虛線：真實漂移點。

**紅線** — 系統確認漂移的時刻（`confirmation_t`），也就是實際換模型的那一步。
批次腳本計分用的是 warning 開始的時間（`warning_t`），所以紅線會比
⑧ 報告裡同一個事件的位置晚幾十筆（即 ② 的「確認延遲」）。

看法：綠線衝高後，理想上緊接著出現一條落在灰帶裡的紅線，
就代表這次漂移被準確抓到；紅線在灰帶外＝誤報，灰帶內沒紅線＝漏抓。
"""

# Tooltip for panel ③ (the model pool).
HELP_PANEL_POOL = """
系統目前留著的所有模型快照，最多 `max_pool_size` 個。

- **slot**：模型在池裡的編號，只是位置代號，跟訓練順序或好壞無關。
- **fade**：這個模型有多「新鮮」。當它是 leader 時每輪
  +`ecpf_fade_points`（左側可調，預設 15）分，被冷落的其他 slot 每輪 -1 分，
  歸零就會被移除。分數越高＝越常被選中、越不容易被淘汰；
  池滿時會優先踢掉分數最低的。這整套機制可用 `ecpf_fade_enabled` 關掉。
- **🟢 leader**：目前正在做預測的那個模型，其他都是備用。
  漂移確認時，勝出的模型會被安裝成新 leader（見 ② 的比較結果）。
- 另外系統會持續比對每對模型的預測一致度，一致度達
  `ecpf_similarity_margin`（左側可調，預設 0.95）就合併成一個，
  避免池子塞滿其實學到同一套規則的重複模型。

圓環填滿的比例＝該 slot 的 fade 分數相對於目前最高分，只是視覺化，不代表百分比；
中間的數字是 fade 分數本身，空心圓環是還沒用到的 slot。
"""

# Tooltip for panel ② (warning buffer + new_model training).
HELP_PANEL_BUFFER = """
warning 期間收集資料、拿去訓練一個全新模型的過程。

- **🟡 warning 開啟中**：目前正在收樣本進 buffer，累積筆數與已持續步數。
  這個階段還沒有結果，純粹在等 buffer 長大或漂移被確認。
- **⚪ 目前無 warning**：沒有在收，等下一次訊號衝高再開始。
- 一旦漂移確認，buffer 會整批拿去訓練一個「全新 new_model」，
  同時系統會把 buffer 拿去跟現有模型池裡的舊模型比對，
  找出「最佳重用」的那個（見下方三個數字）。
- **現任 leader / 最佳重用 / 全新 new_model**：三者都是在同一份 buffer 上
  算出來的準確率，用來比較「繼續用舊的」「調回池裡某個舊模型」
  「重新訓練一個」哪個比較好。
- 不論這三個數字誰贏，ECPF **一律先把「最佳重用」模型裝成新 leader**；
  剛訓練好的 new_model 不會馬上上任，而是轉去當 shadow，
  進入 ④ 的 in-control 對決繼續觀察，之後若持續勝出才會換將。
"""

# Tooltip for panel ⑤ (drift event stream).
HELP_PANEL_EVENTS = """
每一次「漂移被確認」都會在這裡留一筆紀錄，最新的排最上面。

- **t=...**：warning 開始的時間點（`warning_t`），
  不是確認時間點，是為了跟批次腳本計分口徑一致。
  ① 圖上的紅線畫的是確認點，會比這個數字晚幾十筆。
- **source**：哪個偵測器 / 訊號模式觸發了這次確認。
- **型態 badge**：ECPF 確認漂移時由 Type-LDD 分類器（`src/type_ldd`）在
  誤差序列上判定的 sudden / gradual / incremental，同一個值也在細節 JSON 的
  `type_ldd_prediction`（`core/drift_type.py`）。
- 點開展開項可看完整細節 JSON，
  包含 buffer 筆數、各模型在 buffer 上的準確率、最終勝出者等
  （即 ② 面板算出來的那些數字）。
"""



HELP_GT_TOLERANCE = f"""
判定「抓對」的容許窗：事件的 warning_t 落在某個真漂移的 ± 這個範圍內就算 TP，
否則算 FP。只影響 ① 的灰帶和 ⑧ 報告的計分，**不影響偵測本身**，
改了不用重跑，報告會直接用新值重算。

**調大**：延遲較久的偵測也算抓到，TP 變多、FP 變少；太大會把不相干的誤報也算進去。
**調小**：只認很快的偵測；這批資料的偵測延遲中位數約 400–700，
低於 1000 會讓不少真的抓到被記成一個 FP 加一個 FN。
預設 {GT_TOLERANCE}；批次腳本 `run_ecpf_uq_experiment.py` 用的是它自己的預設。
"""

HELP_SHOW_GT = """
在 ① 訊號時序圖上疊出 ground truth（真實漂移點與 ±500 容許窗）。

**開啟**：一眼看出每條紅線（系統確認的漂移）落在灰帶內（抓對）
還是灰帶外（誤報），以及延遲多久。
**關閉**：只看系統自己看得到的東西，模擬「上線後沒有標準答案」的情境。
"""

# Chart palette: warning signal (light green) and drift signal (dark green) --
# two shades so the two signals read as a family yet stay distinguishable by
# lightness. Both kept clear of the muted-ink ground-truth band and the reserved
# red drift rule.
SIG_WARNING, SIG_DRIFT = "#6fc99a", "#0d7a4f"
STATUS_CRITICAL = "#d03b3b"
INK_MUTED = "#52514e"
WARN_AMBER = "#e8b93b"


# ----------------------------------------------------------------------
# Panels
# ----------------------------------------------------------------------
def draw_header(ph, t: int, n_total: int, acc: Optional[float], n_pool: int,
                n_events: int, elapsed: float) -> None:
    with ph.container():
        cols = st.columns(5)
        cols[0].metric("樣本 t", f"{t:,}", f"/ {n_total:,}")
        cols[1].metric("Accuracy (窗)", "—" if acc is None else f"{acc:.3f}",
                       help=HELP_ACC_WINDOW)
        cols[2].metric("模型池", n_pool)
        cols[3].metric("漂移事件", n_events)
        cols[4].metric("已耗時", f"{elapsed:.0f}s")


def draw_prequential(ph, preq_hist: List[Dict[str, Any]],
                     preq_acc: Optional[float], events: List[Dict[str, Any]],
                     warning_spans: List[Any], n_total: int) -> None:
    """Cumulative test-then-train accuracy since warm_start -- the same
    number `run_ecpf_uq_experiment` reports as `prequential_accuracy`, so a
    monitored run's final value is directly comparable to a batch one.

    Layered like panel ① rather than left to `st.line_chart`: a cumulative
    curve moves by a few percentage points over a whole run, so on an axis
    anchored at 0 it flattens against the top of the panel and the dip at each
    drift -- the only thing worth reading here -- disappears.
    """
    with ph.container():
        st.caption(
            "整體預測 · prequential accuracy"
            + ("" if preq_acc is None else f" · 目前 {preq_acc:.3f}"),
            help=HELP_PANEL_PREQ,
        )
        if not preq_hist:
            return

        df = pd.DataFrame(preq_hist).dropna(subset=["preq"])
        # Drop the warm-up transient: the first points average a handful of
        # predictions and can sit near 0, which drags the y domain down and
        # flattens everything after it.
        warm = df[df["t"] >= df["t"].iloc[0] + ROLL_WINDOW]
        if not warm.empty:
            df = warm
        if df.empty:
            return

        lo = max(0.0, float(df["preq"].min()) - 0.01)
        hi = min(1.0, float(df["preq"].max()) + 0.01)

        layers = []

        # Warning phases, behind the line: the span between first suspicion and
        # the red confirmation rule at its right edge.
        if warning_spans:
            spans = pd.DataFrame(warning_spans, columns=["lo", "hi"])
            layers.append(
                alt.Chart(spans).mark_rect(color=WARN_AMBER, opacity=0.18)
                .encode(x="lo:Q", x2="hi:Q")
            )

        layers.append(
            alt.Chart(df).mark_line(size=2, color=SIG_DRIFT).encode(
                # Right edge pinned to the whole stream so the line grows into
                # it; an auto-fitted axis rescales on every redraw and the line
                # appears to stand still instead. The left edge follows the
                # retained history rather than sitting at 0, because the series
                # is a capped deque and slides once a run outruns HIST_POINTS.
                x=alt.X("t:Q", title="t",
                        scale=alt.Scale(domain=[int(df["t"].iloc[0]), n_total],
                                        nice=False)),
                y=alt.Y("preq:Q", title=None, axis=alt.Axis(format="%"),
                        scale=alt.Scale(domain=[lo, hi], nice=False, clamp=True)),
                tooltip=["t:Q", alt.Tooltip("preq:Q", format=".2%")],
            )
        )

        if events:
            # `confirmation_t`, not `timestamp`: this chart and ① both mark
            # when the system acted. The batch runner scores on `timestamp`
            # (warning_t), which is what ⑧ reports against.
            marks = pd.DataFrame({"t": [e["confirmation_t"] for e in events]})
            layers.append(
                alt.Chart(marks).mark_rule(color=STATUS_CRITICAL, size=2)
                .encode(x="t:Q", tooltip=alt.Tooltip("t:Q", title="確認漂移"))
            )

        # Not `.interactive()` unlike panel ①: a scale bound to a zoom
        # selection can override the y domain set above, which is the whole
        # point of this panel's layout.
        st.altair_chart(alt.layer(*layers).properties(height=200),
                        width="stretch")
        st.caption(f"y 軸已縮放至資料範圍（非 0 起點）· 前 {ROLL_WINDOW} 筆暖機已略去"
                   " · 🟡 觀察期　🔴 確認漂移")


def draw_chart(
    ph,
    hist: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    gt_times: List[int],
    warn_name: str,
    drift_name: str,
    n_total: int,
    show_gt: bool = True,
    tolerance: int = GT_TOLERANCE,
) -> None:
    """Signal time series over ground-truth bands, with drift markers.

    Three layers, back to front: ground-truth tolerance bands, the signal
    lines, then a red rule per confirmed drift. A detection landing inside a
    band is a true positive, outside it a false positive -- the same
    ±tolerance rule ⑧ scores with. The bands are the only part that needs
    ground truth, so `show_gt` drops just that layer.
    """
    with ph.container():
        st.caption("① 訊號時序 · warning / drift signal", help=HELP_PANEL_SIGNAL)
        if not hist:
            st.info("等待資料…")
            return

        df = pd.DataFrame(hist)
        t_lo, t_hi = int(df["t"].iloc[0]), int(df["t"].iloc[-1])

        # When both detectors watch the same signal the two series are
        # identical at every step, so drawing both hides one entirely behind
        # the other and leaves a legend entry pointing at an invisible line.
        # Collapse them into one honestly-named series instead.
        same_signal = warn_name == drift_name
        if same_signal:
            # One signal feeds both roles, so there is a single line -- label it
            # by the signal name alone; "warning + drift" would imply two lines.
            df = df.drop(columns=["warn_val"]).rename(
                columns={"drift_val": drift_name}
            )
        else:
            df = df.rename(columns={"warn_val": f"warning signal ({warn_name})",
                                    "drift_val": f"drift signal ({drift_name})"})
        value_cols = [c for c in df.columns if c != "t"]
        long = df.melt("t", value_vars=value_cols,
                       var_name="signal", value_name="value").dropna()

        # Right edge pinned to the whole stream, matching ② and ④, so the line
        # grows across the panel as the run proceeds. Fitted to `t_hi` instead
        # it always spans the full width and rescales on every redraw, which
        # reads as a line standing still. Left edge follows the retained
        # history: the series is a capped deque that slides on long runs.
        x_axis = alt.X("t:Q", title="t",
                       scale=alt.Scale(domain=[t_lo, n_total], nice=False))
        layers = []

        # --- ground-truth bands (recessive, behind everything) ---
        gt_vis = ([g for g in gt_times if t_lo - tolerance <= g <= t_hi + tolerance]
                  if show_gt else [])
        if gt_vis:
            band = pd.DataFrame(
                {"lo": [g - tolerance for g in gt_vis],
                 "hi": [g + tolerance for g in gt_vis]}
            )
            layers.append(
                alt.Chart(band).mark_rect(color=INK_MUTED, opacity=0.13)
                .encode(x="lo:Q", x2="hi:Q")
            )
            # exact drift point inside its band
            layers.append(
                alt.Chart(pd.DataFrame({"t": gt_vis}))
                .mark_rule(color=INK_MUTED, strokeDash=[3, 3], size=1)
                .encode(x="t:Q")
            )

        # --- signal lines ---
        layers.append(
            alt.Chart(long).mark_line(size=2).encode(
                x=x_axis,
                y=alt.Y("value:Q", title=None),
                color=alt.Color(
                    "signal:N", title=None,
                    scale=alt.Scale(
                        domain=value_cols,
                        range=[SIG_WARNING, SIG_DRIFT][: len(value_cols)],
                    ),
                    legend=alt.Legend(orient="top"),
                ),
                tooltip=["t:Q", "signal:N", alt.Tooltip("value:Q", format=".3f")],
            )
        )

        # --- confirmed drifts, on top ---
        # Drawn at `confirmation_t`: this chart is about when the system acted.
        # The batch runner scores on `warning_t`, so a rule can sit a few dozen
        # samples right of where the report counts the same event.
        det_vis = [e["confirmation_t"] for e in events
                   if t_lo <= e["confirmation_t"] <= t_hi]
        if det_vis:
            layers.append(
                alt.Chart(pd.DataFrame({"t": det_vis}))
                .mark_rule(color=STATUS_CRITICAL, size=2)
                .encode(x="t:Q", tooltip=alt.Tooltip("t:Q", title="confirmation_t"))
            )

        # Legend for the bands / lines lives in HELP_PANEL_SIGNAL (the ⓘ next to
        # the panel title), not under the chart.
        st.altair_chart(
            alt.layer(*layers).properties(height=280).interactive(),
            width="stretch",
        )


def draw_pool(ph, pool: List[Dict[str, Any]], max_pool: int) -> None:
    with ph.container():
        st.caption(f"③ 模型池 · {len(pool)} / {max_pool} slots", help=HELP_PANEL_POOL)
        if not pool:
            st.info("池尚未建立")
            return
        # One ring per slot in slot order, so a slot keeps a stable position
        # across redraws; the leader is flagged, not sorted first.
        st.altair_chart(pool_rings(pool, max_pool), width="content")


def draw_buffer(ph, warning_active: bool, warning_start: Optional[int],
                buffer_len: int, t: int, events: List[Dict[str, Any]]) -> None:
    """② warning buffer accumulation + the new_model fit it produced.

    Two halves, because they run on different clocks. The buffer fills live,
    one sample per step, for as long as the warning stays open. The fresh model
    is then fit on the whole buffer in a single `_fit_on_buffer` call at the
    moment of drift confirmation (`ecpf.py:273`) -- there is no incremental
    training curve to show, only its result.
    """
    with ph.container():
        st.caption("② 警告緩衝 · new_model 訓練", help=HELP_PANEL_BUFFER)

        if warning_active:
            st.warning(
                f"🟡 warning 開啟中 · warning_t = **{(warning_start or 0):,}**　"
                f"已累積 **{buffer_len:,}** 筆（持續 {t - (warning_start or t):,} 步）"
            )
            # Deliberately no progress bar: in detector mode the buffer has no
            # target length -- it grows until drift confirms. Only the oracle /
            # retro modes cap it at config.ecpf_warning_length.
        else:
            st.info("⚪ 目前無 warning，buffer 未累積")

        if not events:
            st.caption("尚無訓練結果（需先有漂移確認）")
            return

        d = events[-1]["details"]
        acc_new = d.get("acc_new_on_warning")
        acc_best = d.get("acc_best_on_warning")
        acc_cur = d.get("acc_current_on_warning")
        if acc_new is None:
            return

        st.markdown(
            f"**最近一次訓練** · t={events[-1]['timestamp']:,} · "
            f"buffer {d.get('buffer_len', 0):,} 筆"
        )
        cols = st.columns(3)
        cols[0].metric("現任 leader", f"{acc_cur:.3f}" if acc_cur is not None else "—")
        cols[1].metric(
            f"最佳重用 (slot {d.get('best_idx', '?')})",
            f"{acc_best:.3f}" if acc_best is not None else "—",
        )
        cols[2].metric(
            "全新 new_model",
            f"{acc_new:.3f}",
            delta=None if acc_best is None else f"{acc_new - acc_best:+.3f}",
        )
        # What ECPF does with the comparison (best reuse becomes leader, the
        # fresh model goes to ④ as shadow) is in HELP_PANEL_BUFFER, not
        # repeated under the numbers; `winner_initial` is in the ⑤ JSON.
        # S9 in the HTML manual also showed precision / recall / F1 here, but
        # those were labelled 示意 (simulated from acc) -- per-class detail
        # for the trained model is not stored at the event layer, so there is
        # nothing real to plot in this panel.


def draw_duel(ph, has_shadow: bool, leader_correct: int, shadow_correct: int,
              leader_swaps: int, duel_hist: List[Dict[str, Any]],
              n_total: int) -> None:
    """leader vs shadow, plotted as the gap the swap rule actually reads.

    `ECPF.check_swap` swaps when `curr_correct < new_correct`, so
    ``leader - shadow`` crossing below zero *is* the decision. Drawn as two
    cumulative count lines instead, the pair runs nearly on top of itself and
    the crossing -- the only moment that matters -- is unreadable.

    The counters are per-duel, not per-run: a drift zeroes both
    (`ecpf.py:304`) while a swap merely exchanges them, leaving their sum
    intact. So each duel is drawn as its own line rather than joined across
    the resets.
    """
    with ph.container():
        st.caption("④ in-control 對決 · leader vs shadow")
        if not duel_hist:
            st.info("目前無 shadow model（非 lockout 期）")
            return

        cols = st.columns(3)
        cols[0].metric("leader", leader_correct)
        cols[1].metric("shadow", shadow_correct)
        cols[2].metric("換將次數", leader_swaps)
        if not has_shadow:
            st.caption("目前非 lockout 期，以下為先前各場對決的紀錄。")

        df = pd.DataFrame(duel_hist)
        df["gap"] = df["leader"] - df["shadow"]
        # A falling *total* marks a drift reset; a swap keeps the total and
        # only flips the sign of the gap, so `leader` falling is not on its own
        # the start of a new duel.
        total = df["leader"] + df["shadow"]
        df["duel"] = (total < total.shift(fill_value=0)).cumsum()

        pad = max(1.0, float(df["gap"].abs().max()) * 0.1)
        lo = min(0.0, float(df["gap"].min())) - pad
        hi = max(0.0, float(df["gap"].max())) + pad

        zero = (
            alt.Chart(pd.DataFrame({"y": [0]}))
            .mark_rule(color=INK_MUTED, strokeDash=[3, 3], size=1)
            .encode(y="y:Q")
        )
        line = alt.Chart(df).mark_line(size=2, color=SIG_DRIFT).encode(
            x=alt.X("t:Q", title="t",
                    scale=alt.Scale(domain=[int(df["t"].iloc[0]), n_total],
                                    nice=False)),
            y=alt.Y("gap:Q", title="leader − shadow",
                    scale=alt.Scale(domain=[lo, hi], nice=False, clamp=True)),
            detail="duel:N",
            tooltip=["t:Q", "leader:Q", "shadow:Q", "gap:Q"],
        )
        st.altair_chart(alt.layer(zero, line).properties(height=200),
                        width="stretch")
        st.caption("0 以上 = leader 仍領先；跌破 0 = shadow 較準，"
                   "下次確認時換將 · 每場對決獨立一條線（漂移會把計數歸零）")


def draw_events(ph, events: List[Dict[str, Any]]) -> None:
    with ph.container():
        st.caption(f"⑤ 漂移事件流 · {len(events)} 筆", help=HELP_PANEL_EVENTS)
        if not events:
            st.info("尚無漂移事件")
            return
        for e in reversed(events[-10:]):
            # `drift_type` is Type-LDD's label; render it as the same badge
            # the operator view uses.
            p = drift_type.predict(e)
            label = (f"t={e['timestamp']:,} · {e['source']} · "
                     f":{p.color}-badge[{p.text}]")
            with st.expander(label):
                st.json(e["details"])


def draw_cost(result: RunResult) -> None:
    """⑥ 成本 · 效能 (plan §3.2)."""
    st.divider()
    st.subheader("⑥ 成本 · 效能")
    c = metrics.cost_summary(result)
    cols = st.columns(4)
    cols[0].metric("throughput", f"{c['throughput']:,.0f} 筆/s",
                   help="端到端：跑完的筆數 ÷ 總耗時，含畫面重繪成本。")
    cols[1].metric("模型池佔用", f"{c['pool_used']} / {c['pool_max']}",
                   help="池中實際佔用的 slot 數，對應 ③ 面板。")
    cols[2].metric("重訓次數", f"{c['n_refits']}",
                   help="每次漂移確認都會在整個 warning buffer 上重訓一個 new_model。")
    cols[3].metric("換將次數", f"{c['leader_swaps']}",
                   help="in-control 對決中 shadow 取代 leader 的次數（④ 面板）。")

    cols = st.columns(3)
    cols[0].metric("重訓總樣本數", f"{c['refit_samples']:,}",
                   help="所有事件的 buffer_len 總和 —— 重訓的真實工作量。")
    cols[1].metric("平均 buffer",
                   f"{c['mean_buffer']:,.0f}" if c["mean_buffer"] is not None else "—",
                   help="每次重訓平均用掉幾筆資料。")
    cols[2].metric("總耗時", f"{c['elapsed']:.1f}s")
    st.caption(
        "重訓成本以樣本數計：每次漂移確認會在整個 warning buffer 上重新 fit 一個模型"
        "（`ecpf.py` `_fit_on_buffer`），故 `buffer_len` 就是該次事件的實際工作量。"
    )


def draw_downloads(result: RunResult) -> None:
    """⑦ 原始資料下載 (plan §3.3)."""
    st.divider()
    st.subheader("⑦ 原始資料下載")

    events_json = json.dumps(result.events, ensure_ascii=False,
                             indent=2, default=str)

    # Per-step metrics: the two sampled series share the same stride grid, so
    # they join cleanly on t.
    df = pd.DataFrame(result.preq_hist)
    if result.signal_hist:
        df = df.merge(pd.DataFrame(result.signal_hist), on="t", how="outer")
    df = df.sort_values("t")

    stem = f"{result.stream_label.replace(' · ', '_').replace('/', '_')}"
    cols = st.columns(2)
    cols[0].download_button(
        "⬇ events JSON", events_json, file_name=f"events_{stem}.json",
        mime="application/json", width="stretch",
    )
    cols[1].download_button(
        "⬇ per-step 指標 CSV", df.to_csv(index=False),
        file_name=f"metrics_{stem}.csv", mime="text/csv", width="stretch",
    )
    st.caption(
        f"指標 CSV 每 STRIDE={result.stride} 筆取樣一次（漂移確認時額外補點）："
        "`preq` 累積準確率、`roll` 近期準確率、`warn_val` / `drift_val` 訊號值。"
    )


def draw_report(events: List[Dict[str, Any]], gt_times: List[int],
                tolerance: int = GT_TOLERANCE) -> None:
    """⑧ Offline event report -- scored against ground truth after the run.

    This is the offline layer: it needs the ground-truth drift schedule, so
    unlike panels ①-⑤ it cannot exist while the stream is still running, and
    it feeds nothing back into the pipeline.
    """
    st.divider()
    st.subheader("⑧ 事件報告 · 離線")

    if not events:
        st.info("本次執行沒有漂移事件，無報告可產生。")
        return

    det_times = [e["timestamp"] for e in events]

    def is_tp(e: Dict[str, Any]) -> bool:
        return any(abs(e["timestamp"] - g) <= tolerance for g in gt_times)

    n_tp = sum(1 for e in events if is_tp(e))
    n_fp = len(events) - n_tp
    missed = [g for g in gt_times
              if not any(abs(d - g) <= tolerance for d in det_times)]

    delay = _detection_delay(gt_times, det_times, tolerance)
    fw_rate = _false_warning_rate(det_times, gt_times, tolerance)
    conf_delays = [e["confirmation_t"] - e["warning_t"] for e in events]
    reuse_better = [
        e for e in events
        if (e["details"].get("acc_best_on_warning") is not None
            and e["details"].get("acc_new_on_warning") is not None
            and e["details"]["acc_best_on_warning"] >= e["details"]["acc_new_on_warning"])
    ]

    # Type distribution first: what the classifier said, and -- the part an
    # engineer wants next to it -- how many of each type were real drifts.
    counts = metrics.type_counts(events)
    left, right = st.columns([1, 1])
    with left:
        st.caption("型態分布 · Type-LDD")
        st.altair_chart(type_pie(counts), width="stretch")
    with right:
        st.caption("各型態的 TP / FP")
        by_type = {}
        for e in events:
            label = drift_type.predict(e).text
            row = by_type.setdefault(label, {"TP": 0, "FP": 0})
            row["TP" if is_tp(e) else "FP"] += 1
        rows = [{"型態": k, "次數": counts.get(k, 0), "TP": v["TP"], "FP": v["FP"]}
                for k, v in by_type.items()]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    cols = st.columns(4)
    cols[0].metric("TP · 真漂移", n_tp)
    cols[1].metric("FP · 誤報", n_fp, delta=f"誤報率 {fw_rate:.0%}",
                   delta_color="inverse")
    cols[2].metric("漏報 · 未偵測到", len(missed), f"/ {len(gt_times)} 個真漂移")
    cols[3].metric("平均偵測延遲", f"{delay:.0f}",
                   help=f"每個真漂移到最近偵測的平均距離；未配對者以 {tolerance} 計"
                        "（同 run_ecpf_uq_experiment._detection_delay）")

    # Drift-detection precision/recall/F1 -- computable from the TP/FP/FN
    # counts above (all real, scored against ground truth). Not to be
    # confused with per-class classification precision/recall on panel ②,
    # which really is unavailable (see the comment there / ECPF_MONITOR_PLAN
    # §"不提供 precision / recall / F1").
    n_fn = len(missed)
    precision = n_tp / (n_tp + n_fp) if (n_tp + n_fp) else 0.0
    recall = n_tp / (n_tp + n_fn) if (n_tp + n_fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    cols = st.columns(3)
    cols[0].metric("precision", f"{precision:.3f}",
                   help="TP / (TP + FP)：確認過的漂移裡，有幾成真的對到 ground truth。")
    cols[1].metric("recall", f"{recall:.3f}",
                   help="TP / (TP + FN)：所有真漂移裡，有幾成被抓到了。")
    cols[2].metric("F1", f"{f1:.3f}",
                   help="precision 與 recall 的調和平均，兩者要同時不差才會高。")
    st.caption(
        "以上是漂移偵測層級（事件 vs. ground truth）的 precision/recall/F1，"
        "非逐筆分類的 per-class 版本。"
    )

    cols = st.columns(2)
    cols[0].metric(
        "reuse_looked_better",
        f"{len(reuse_better)} / {len(events)}",
        help="buffer 上最佳重用專家的準確度 ≥ 全新訓練模型的事件數",
    )
    cols[1].metric(
        "平均 confirmation_delay",
        f"{np.mean(conf_delays):.0f}" if conf_delays else "—",
        help="warning_t → confirmation_t 的平均步數",
    )

    rows = []
    for e in events:
        d = e["details"]
        near = min(gt_times, key=lambda g: abs(g - e["timestamp"])) if gt_times else None
        acc_best = d.get("acc_best_on_warning")
        acc_new = d.get("acc_new_on_warning")
        rows.append(
            {
                "warning_t": e["warning_t"],
                "confirm_t": e["confirmation_t"],
                "delay": e["confirmation_t"] - e["warning_t"],
                "gt": "TP" if is_tp(e) else "FP",
                "nearest_gt": near,
                "offset": None if near is None else e["timestamp"] - near,
                "buffer": d.get("buffer_len"),
                "acc_best": acc_best,
                "acc_new": acc_new,
                "reuse": (
                    None if acc_best is None or acc_new is None
                    else ("重用" if acc_best >= acc_new else "全新")
                ),
            }
        )
    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
        column_config={
            "acc_best": st.column_config.NumberColumn(format="%.3f"),
            "acc_new": st.column_config.NumberColumn(format="%.3f"),
        },
    )
    st.caption(
        f"**離線層**：需 ground truth 才能算，執行後產生，與 runtime 無回饋箭頭。"
        f"TP/FP 以 warning_t 與最近真漂移相距 ≤ {tolerance} 判定，"
        f"計分函式直接取自 `run_ecpf_uq_experiment`，故與批次報表一致。"
    )


# ----------------------------------------------------------------------
# Layout (plan §3.1: panels grouped by layer, not by number)
# ----------------------------------------------------------------------
class _Panels:
    """Placeholders for the live panels, laid out by pipeline layer.

    The panels live in ``st.empty()`` slots so a redraw that skips the costly
    chart panels leaves their previous frame on screen instead of blanking it.
    """

    def __init__(self) -> None:
        self.notice = st.empty()
        self.head = st.empty()
        # Its own slot rather than the tail of `head`: dropping an element from
        # a rewritten container leaves the old one on screen, but clearing a
        # placeholder that holds only the bar removes it.
        self.progress = st.empty()
        self.preq = st.empty()
        # Layer 1 spans the page: the signal chart is a time series on the
        # same t axis as the prequential chart above it, and at half width
        # its ground-truth bands and drift rules were too cramped to read
        # against that one.
        st.markdown("##### 第 1 層 · 訊號")
        self.chart = st.empty()
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("##### 第 2 層 · 偵測與確認")
            self.buffer = st.empty()
        with col_r:
            st.markdown("##### 第 3 層 · ECPF 模型管理")
            self.pool = st.empty()
            self.duel = st.empty()
            st.markdown("##### 事件")
            self.events = st.empty()


def _paint(panels: _Panels, s: Any, t: int, opts: Dict[str, Any],
           show_gt: bool, running: bool = True,
           tolerance: int = GT_TOLERANCE) -> None:
    """Repaint the panels from a ``RunState`` (live) or ``RunResult`` (stored).

    Both carry the same field names for everything drawn here, which is the
    point of lifting the values out of the pipeline in ``core.run``.

    Every panel is painted together. Splitting them -- cheap panels on every
    tick, charts on a coarser cadence -- sends the browser several times more
    deltas than it can apply, and the charts then land in bursts rather than
    growing; the caller controls the rate by calling this less often instead.
    """
    draw_header(panels.head, t, s.n_total, s.roll_acc, len(s.pool),
                len(s.events), s.elapsed)
    # Parked at 100% the bar only repeats the 樣本 t metric above it, and a
    # full-width red bar reads as a drift marker -- that is what the colour
    # means in every other panel.
    if running:
        panels.progress.progress(min(1.0, t / s.n_total) if s.n_total else 0.0)
    else:
        panels.progress.empty()
    draw_prequential(panels.preq, s.preq_hist, s.preq_acc, s.events,
                     s.warning_spans, s.n_total)
    draw_chart(panels.chart, s.signal_hist, s.events, s.gt_times,
               opts["warning_signal"], opts["drift_signal"], s.n_total,
               show_gt, tolerance)
    draw_buffer(panels.buffer, s.warning_active, s.warning_start,
                s.buffer_len, t, s.events)
    draw_pool(panels.pool, s.pool, opts["max_pool_size"])
    draw_duel(panels.duel, s.has_shadow, s.leader_correct,
              s.shadow_correct, s.leader_swaps, s.duel_hist, s.n_total)
    draw_events(panels.events, s.events)


# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
def _sidebar() -> Optional[Dict[str, Any]]:
    streams = demo_streams()
    with st.sidebar:
        st.header("設定")
        if not streams:
            st.error("找不到資料：請確認 data/*_drift 內有 *.csv")
            return None
        labels = {p: f"{label} · {p.name}" for label, p in streams}
        csv_path = st.selectbox("資料檔", [p for _, p in streams],
                                format_func=lambda p: labels[p], help=HELP_CSV)
        warm_start = st.number_input("warm_start", 0, 10_000, 200, step=50,
                                     help=HELP_WARM_START)
        # Default is the selected file's own length, so a run covers the whole
        # stream unless the user trims it. Keyed by file: a number_input keeps
        # its value across reruns, so without a per-file key switching from a
        # 100k file to the 1M one would silently keep 100k.
        n_rows = stream_length(csv_path)
        max_steps = st.number_input(
            "max_steps（0 = 全部）", 0, max(1_000_000, n_rows), n_rows,
            step=1000, help=HELP_MAX_STEPS, key=f"max_steps:{csv_path}",
        )
        show_gt = st.checkbox("① 圖疊 ground truth", value=True, help=HELP_SHOW_GT)
        gt_tolerance = st.number_input("gt_tolerance（容許窗 ±）", 0, 10_000,
                                       GT_TOLERANCE, step=100, help=HELP_GT_TOLERANCE)
        st.divider()
        signal_mode = st.selectbox(
            "signal_mode",
            ["detector", "dual_adwin", "dual_seqdrift2", "dual_seed", "uq_warning"],
            help=HELP_SIGNAL_MODE,
        )
        warning_signal = st.selectbox("warning_signal", SIGNAL_CHOICES,
                                      help=HELP_WARNING_SIGNAL)
        drift_signal = st.selectbox("drift_signal", SIGNAL_CHOICES,
                                    help=HELP_DRIFT_SIGNAL)
        warning_detector = st.selectbox("warning_detector", [None] + DETECTOR_CHOICES,
                                        help=HELP_WARNING_DETECTOR)
        drift_detector = st.selectbox("drift_detector", [None] + DETECTOR_CHOICES,
                                      help=HELP_DRIFT_DETECTOR)
        st.divider()
        detector_delta = st.number_input("detector_delta", 0.0, 1.0, 0.01, step=0.01,
                                         format="%.3f", help=HELP_DELTA)
        detector_delta_w = st.number_input("detector_delta_w", 0.0, 1.0, 0.1, step=0.01,
                                           format="%.3f", help=HELP_DELTA_W)
        # Cap at 10k: the values that actually suppress post-swap aftershocks
        # are in the thousands (see HELP_MIN_INSTANCES); the old 1,000 ceiling
        # kept the useful range out of reach.
        detector_min_instances = st.number_input("detector_min_instances", 1, 10_000, 30,
                                                 step=10, help=HELP_MIN_INSTANCES)
        max_pool_size = st.number_input("ecpf_max_pool_size", 1, 50, 10,
                                        help=HELP_MAX_POOL_SIZE)
        similarity_margin = st.slider("ecpf_similarity_margin", 0.80, 1.0, 0.95,
                                      step=0.01, help=HELP_SIMILARITY_MARGIN)
        fade_points = st.number_input("ecpf_fade_points", 1, 60, 15,
                                      help=HELP_FADE_POINTS)
        fade_enabled = st.checkbox("ecpf_fade_enabled", value=True,
                                   help=HELP_FADE_ENABLED)
        model_type = st.selectbox("model_type", ["ht", "hf"], help=HELP_MODEL_TYPE)
        start = st.button("▶ 開始監控", type="primary", width="stretch")

    return dict(
        csv_path=csv_path,
        stream_label=labels[csv_path],
        warm_start=int(warm_start),
        max_steps=int(max_steps),
        show_gt=bool(show_gt),
        gt_tolerance=int(gt_tolerance),
        start=bool(start),
        opts=dict(
            signal_mode=signal_mode, warning_signal=warning_signal,
            drift_signal=drift_signal, warning_detector=warning_detector,
            drift_detector=drift_detector, detector_delta=detector_delta,
            detector_delta_w=detector_delta_w,
            detector_min_instances=detector_min_instances,
            max_pool_size=max_pool_size,
            similarity_margin=similarity_margin,
            fade_points=fade_points, fade_enabled=fade_enabled,
            model_type=model_type,
        ),
    )


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def render() -> None:
    st.title("ECPF Monitor")
    st.caption(
        "面板依因果分層：**訊號**（監看什麼數值）→ **偵測與確認**"
        "（誰在什麼時候拍板）→ **ECPF 模型管理**（拍板後模型怎麼換）。"
    )

    cfg = _sidebar()
    if cfg is None:
        return

    result: Optional[RunResult] = st.session_state.get("run_result")
    if not cfg["start"] and result is None:
        st.info("在左側設定參數後按「開始監控」。跑完為止，中途無法暫停"
                "（見 docs/ECPF_MONITOR_PLAN.md §4.2）。")
        return

    # Built only once there is something to put in it -- an empty run would
    # otherwise render as a page of bare layer headings.
    panels = _Panels()

    if cfg["start"]:
        n_redraw = 0  # counts triggers, to thin out the repaints
        redraw_every = None
        last_warn = False

        def on_tick(s: RunState) -> None:
            nonlocal n_redraw, redraw_every, last_warn
            n_redraw += 1
            if redraw_every is None:
                # One tick per STRIDE samples, plus event triggers -- close
                # enough to size the cadence off the stream length.
                expected = max(1, s.n_total // STRIDE)
                redraw_every = max(1, round(expected / TARGET_CHART_REDRAWS))
            # A warning opening or closing repaints too, so ② does not sit on a
            # stale buffer state between two scheduled frames.
            warn_edge = s.warning_active != last_warn
            last_warn = s.warning_active
            # Offset by one so the *first* tick paints instead of leaving the
            # panels blank until the redraw_every-th one. A confirmed drift
            # always forces a frame, whatever the cadence.
            if not (s.drift or warn_edge or (n_redraw - 1) % redraw_every == 0):
                return
            _paint(panels, s, s.t, cfg["opts"], cfg["show_gt"],
                   tolerance=cfg["gt_tolerance"])

        result = run_and_collect(
            cfg["csv_path"], warm_start=cfg["warm_start"],
            max_steps=cfg["max_steps"], opts=cfg["opts"], stride=STRIDE,
            stream_label=cfg["stream_label"], on_tick=on_tick,
        )
        st.session_state["run_result"] = result
        # Repaint once the run is over: drops the progress bar, and settles the
        # chart panels on the finished result rather than on whichever tick the
        # redraw cadence happened to land on last.
        _paint(panels, result, result.n_total - 1, result.opts,
               cfg["show_gt"], running=False, tolerance=cfg["gt_tolerance"])
        st.success(
            f"完成：{result.n_total:,} 筆，{len(result.events)} 個漂移事件，"
            f"耗時 {result.elapsed:.1f}s"
        )
    elif result is not None:
        # Re-render a run that finished earlier (possibly under the other
        # role) -- 一次 run，兩種呈現.
        panels.notice.info(
            f"顯示先前的執行結果：{result.stream_label} · "
            f"{result.n_seen:,} 筆 · {len(result.events)} 個漂移事件。"
            "改參數後按左側「開始監控」重跑。"
        )
        _paint(panels, result, result.n_total - 1, result.opts,
               cfg["show_gt"], running=False, tolerance=cfg["gt_tolerance"])

    draw_cost(result)
    draw_downloads(result)
    draw_report(result.events, result.gt_times, cfg["gt_tolerance"])
