"""ECPF 即時監控台 (Streamlit)。

    streamlit run monitor_app.py

Drives ``ConceptDriftPipeline.run_stream`` over one recurring-drift CSV and
redraws a four-panel console as the stream advances. Read-only: it observes the
values the pipeline already yields and never feeds anything back, so a monitored
run behaves identically to the same run under ``run_ecpf_uq_experiment.py``.

Design notes and rejected alternatives: ``docs/ECPF_MONITOR_PLAN.md``.
"""

from __future__ import annotations

import time
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline, load_recurring_stream_pair

# Scored with the batch runner's own definitions so the monitor's report and a
# `run_ecpf_uq_experiment.py` report of the same run cannot diverge. That module
# is guarded by `if __name__ == "__main__"`, so importing it is side-effect free.
from run_ecpf_uq_experiment import _detection_delay, _false_warning_rate

SIGNAL_CHOICES = ["error", "uq_mi", "uq_vote", "uq_entropy", "uq_variance"]
DETECTOR_CHOICES = ["adwin", "seed", "seqdrift2"]
# Curated demo streams: a few files per drift type so the deployed selector
# stays short (and the app stays snappy) instead of listing all ~40 files.
# The loader (`load_recurring_stream_pair`) is generic -- it reads any CSV with
# a `y` column and finds the sibling `_drift_times.txt` -- so every drift-type
# folder works, not just recurring_drift.
DEMO_DRIFT_DIRS = [
    ("sudden", Path("data/sudden_drift")),
    ("gradual", Path("data/gradual_drift")),
    ("incremental", Path("data/incremental_drift")),
    ("recurring", Path("data/recurring_drift")),
]
DEMO_PER_TYPE = 2  # how many files to expose per drift type


def demo_streams() -> "List[tuple[str, Path]]":
    """Return curated ``(drift_type_label, csv_path)`` pairs for the selector."""
    out: List[tuple] = []
    for label, d in DEMO_DRIFT_DIRS:
        if d.is_dir():
            for p in sorted(d.glob("*.csv"))[:DEMO_PER_TYPE]:
                out.append((label, p))
    return out

# Ring-buffer depth for the signal chart, in sampled points (one per stride).
# At STRIDE=50 this spans ~100k samples, i.e. a whole standard file.
HIST_POINTS = 2000

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
這次最多跑幾筆資料，`0` 代表整個檔案跑完。

**調小**：很快看到結果，適合先試參數；但只看到資料的前段，
後面的漂移不會出現。
**調大或設 0**：完整結果，但要等比較久。
"""

HELP_STRIDE = """
畫面每隔幾筆資料重畫一次。只影響「看起來順不順」，不影響偵測結果。

**調小**：畫面更即時、更細膩，但跑得比較慢。
**調大**：跑得快，但線圖比較粗略。
不管設多少，偵測到漂移或換模型時都會立刻重畫，不會漏看。
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
0.05 是常用的折衷值。
"""

HELP_DELTA_W = """
預警的敏感度（給 warning_detector 用）。

意義同 detector_delta，但作用在「提早示警」這一關。
通常設得比 detector_delta 大（預設 0.1 對 0.05），
意思是預警寧可寬鬆一點、早點注意，真正的把關留給確認階段。
"""

HELP_MIN_INSTANCES = """
偵測器至少要看過幾筆資料才允許報漂移。

**調大**：判斷根據更充足，開頭和剛換模型後不會亂報，
但反應變慢。
**調小**：反應更快，但樣本太少時容易被幾筆倒楣的資料誤導。
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
HELP_PANEL_SIGNAL = """
這張圖把系統每一步監看的數值畫成隨時間變化的曲線。由後往前疊三層：

**彩色曲線（會上下起伏）** — 主角，是實際被監看的訊號值。
- 🟢 **warning signal**（淺綠線）：左欄 `warning_signal` 選的訊號，
  負責「提早示警」。線越高代表錯誤率或不確定感越高。
- 🟢 **drift signal**（深綠線）：`drift_signal` 選的訊號，負責「確認漂移」。
- 兩者若選同一個訊號，只會有一條綠線，圖例直接標該訊號的名字（如 `error`）。

**灰色背景（不會動）** — 對照用的標準答案。
- 灰色色帶：真實漂移點的容許窗（±500）。
- 灰色虛線：真正發生漂移的確切時間。

**紅色直線** — 系統實際偵測並確認漂移的時刻。

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

進度條長度＝該 slot 的 fade 分數相對於目前最高分的比例，只是視覺化，不代表百分比。
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
  不是確認時間點，是為了跟批次腳本計分口徑一致
  （對照 ① 圖上的紅線）。
- **source**：哪個偵測器 / 訊號模式觸發了這次確認。
- **drift_type**：系統判斷出的漂移型態，例如
  `sudden`（突然）、`gradual`（漸進）、`incremental`（漸變累積）、
  `recurring`（舊概念重現，對到模型池裡的舊模型）。
- 點開展開項可看完整細節 JSON，
  包含 buffer 筆數、各模型在 buffer 上的準確率、最終勝出者等
  （即 ② 面板算出來的那些數字）。
"""

# Half-width of the ground-truth band drawn behind the signal chart. A drift
# confirmed inside the band counts as a true positive -- same tolerance the
# batch runner scores with (`run_ecpf_uq_experiment._detection_delay`).
GT_TOLERANCE = 500

# Chart palette: warning signal (light green) and drift signal (dark green) --
# two shades so the two signals read as a family yet stay distinguishable by
# lightness. Both kept clear of the muted-ink ground-truth band and the reserved
# red drift rule.
SIG_WARNING, SIG_DRIFT = "#6fc99a", "#0d7a4f"
STATUS_CRITICAL = "#d03b3b"
INK_MUTED = "#52514e"


# ----------------------------------------------------------------------
# Pipeline wiring
# ----------------------------------------------------------------------
def build_pipeline(opts: Dict[str, Any]) -> ConceptDriftPipeline:
    """Construct a pipeline from sidebar options.

    Mirrors the config assembly in ``run_ecpf_uq_experiment.run_one`` so a
    monitored run is comparable to a batch one.
    """
    # UQ signals need per-class probabilities, which the plain Hoeffding tree
    # does not expose -- the batch runner promotes ht -> hf for the same reason.
    model_type = opts["model_type"]
    if model_type == "ht" and (
        opts["warning_signal"] != "error" or opts["drift_signal"] != "error"
    ):
        model_type = "hf"

    cfg = PipelineConfig(
        use_ecpf=True,
        model_type=model_type,
        ecpf_signal_mode=opts["signal_mode"],
        ecpf_oracle_true_drift_times=None,
        ecpf_warning_length=60,
        ecpf_max_pool_size=opts["max_pool_size"],
        ecpf_similarity_margin=opts["similarity_margin"],
        ecpf_fade_points=opts["fade_points"],
        ecpf_fade_enabled=opts["fade_enabled"],
        detector_delta=opts["detector_delta"],
        detector_delta_w=opts["detector_delta_w"],
        ecpf_detector_min_instances=opts["detector_min_instances"],
        ecpf_warning_detector=opts["warning_detector"],
        ecpf_drift_detector=opts["drift_detector"],
        ecpf_warning_signal=opts["warning_signal"],
        ecpf_drift_signal=opts["drift_signal"],
    )
    return ConceptDriftPipeline(cfg)


def pool_snapshot(ecpf: Any) -> List[Dict[str, Any]]:
    """Read the live model-pool state. Returns [] when ECPF is not active."""
    if ecpf is None:
        return []
    rows = []
    for idx, slot in enumerate(ecpf.slots):
        if slot is None:
            continue
        rows.append(
            {
                "slot": idx,
                "fade": ecpf.fade_scores.get(idx, 0),
                "is_leader": idx == ecpf.current_idx,
            }
        )
    return rows


# ----------------------------------------------------------------------
# Rendering
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
        st.progress(min(1.0, t / n_total) if n_total else 0.0)


def draw_prequential(ph, preq_hist: deque, preq_acc: Optional[float]) -> None:
    """Cumulative test-then-train accuracy since warm_start -- the same
    number `run_ecpf_uq_experiment` reports as `prequential_accuracy`, so a
    monitored run's final value is directly comparable to a batch one.
    """
    with ph.container():
        st.caption(
            "整體預測 · prequential accuracy"
            + ("" if preq_acc is None else f" · 目前 {preq_acc:.3f}"),
            help=HELP_PANEL_PREQ,
        )
        if not preq_hist:
            return
        df = pd.DataFrame(list(preq_hist)).set_index("t")
        st.line_chart(df[["acc"]], height=120)


def draw_chart(
    ph,
    hist: deque,
    events: List[Dict[str, Any]],
    gt_times: List[int],
    warn_name: str,
    drift_name: str,
) -> None:
    """Signal time series over ground-truth bands, with drift markers.

    Three layers, back to front: ground-truth tolerance bands, the signal
    lines, then a red rule per confirmed drift. A detection landing inside a
    band is a true positive, outside it a false positive -- the same
    ±GT_TOLERANCE rule the batch runner scores with.
    """
    with ph.container():
        st.caption("① 訊號時序 · warning / drift signal", help=HELP_PANEL_SIGNAL)
        if not hist:
            st.info("等待資料…")
            return

        df = pd.DataFrame(list(hist))
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

        x_axis = alt.X("t:Q", title="t",
                       scale=alt.Scale(domain=[t_lo, t_hi], nice=False))
        layers = []

        # --- ground-truth bands (recessive, behind everything) ---
        gt_vis = [g for g in gt_times if t_lo - GT_TOLERANCE <= g <= t_hi + GT_TOLERANCE]
        if gt_vis:
            band = pd.DataFrame(
                {"lo": [g - GT_TOLERANCE for g in gt_vis],
                 "hi": [g + GT_TOLERANCE for g in gt_vis]}
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
        det_vis = [e["timestamp"] for e in events if t_lo <= e["timestamp"] <= t_hi]
        if det_vis:
            layers.append(
                alt.Chart(pd.DataFrame({"t": det_vis}))
                .mark_rule(color=STATUS_CRITICAL, size=2)
                .encode(x="t:Q", tooltip=alt.Tooltip("t:Q", title="warning_t"))
            )

        st.altair_chart(
            alt.layer(*layers).properties(height=280).interactive(),
            width="stretch",
        )
        st.caption(
            f"灰帶 = ground truth 漂移 ±{GT_TOLERANCE}（判定為 TP 的容許窗）· "
            f"灰虛線 = 真實漂移點 · 紅線 = 事件的 warning_t（非確認點，"
            f"與批次腳本計分所用的時間一致）"
        )


def draw_pool(ph, pool: List[Dict[str, Any]], max_pool: int) -> None:
    with ph.container():
        st.caption(f"③ 模型池 · {len(pool)} / {max_pool} slots", help=HELP_PANEL_POOL)
        if not pool:
            st.info("池尚未建立")
            return
        # fade score drives the bar; leader is flagged rather than sorted first
        # so a slot keeps a stable visual position across redraws.
        fade_max = max((p["fade"] for p in pool), default=1) or 1
        for p in pool:
            tag = "🟢 leader" if p["is_leader"] else "　"
            st.write(f"`slot {p['slot']:>2}` {tag}　fade **{p['fade']}**")
            st.progress(min(1.0, max(0.0, p["fade"] / fade_max)))


def draw_buffer(ph, pipe: Any, t: int, events: List[Dict[str, Any]]) -> None:
    """② warning buffer accumulation + the new_model fit it produced.

    Two halves, because they run on different clocks. The buffer fills live,
    one sample per step, for as long as the warning stays open. The fresh model
    is then fit on the whole buffer in a single `_fit_on_buffer` call at the
    moment of drift confirmation (`ecpf.py:273`) -- there is no incremental
    training curve to show, only its result.
    """
    with ph.container():
        st.caption("② 警告緩衝 · new_model 訓練", help=HELP_PANEL_BUFFER)

        active = getattr(pipe, "_ecpf_warning_active", False)
        if active:
            start = pipe._ecpf_warning_start_idx
            n_buf = len(pipe._ecpf_buffer)
            st.warning(
                f"🟡 warning 開啟中 · warning_t = **{start:,}**　"
                f"已累積 **{n_buf:,}** 筆（持續 {t - (start or t):,} 步）"
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
        if acc_best is not None:
            verdict = "重用勝出" if acc_best >= acc_new else "全新勝出"
            st.caption(
                f"buffer 上的對比：{verdict}。ECPF 一律先安裝最佳重用副本為 leader"
                f"（winner_initial={d.get('winner_initial')}），全新模型轉為 shadow "
                f"進入 ④ 的 in-control 對決。"
            )
        # S9 in the HTML manual also showed precision / recall / F1 here, but
        # those were labelled 示意 (simulated from acc) -- per-class detail
        # for the trained model is not stored at the event layer, so there is
        # nothing real to plot in this panel.
        st.caption(
            "註：new_model 逐類別的 precision / recall / F1 未存於事件層，"
            "此面板不提供。漂移偵測（TP/FP/FN）層級的 precision/recall/F1 "
            "在下方 ⑧ 事件報告面板。"
        )


def draw_duel(ph, ecpf: Any, duel_hist: deque) -> None:
    with ph.container():
        st.caption("④ in-control 對決 · leader vs shadow")
        if ecpf is None or ecpf.new_model is None:
            st.info("目前無 shadow model（非 lockout 期）")
            return
        cols = st.columns(3)
        cols[0].metric("leader", ecpf.curr_correct)
        cols[1].metric("shadow", ecpf.new_correct)
        cols[2].metric("換將次數", ecpf.leader_swaps)
        if duel_hist:
            df = pd.DataFrame(list(duel_hist)).set_index("t")
            st.line_chart(df[["leader", "shadow"]], height=180)


def draw_events(ph, events: List[Dict[str, Any]]) -> None:
    with ph.container():
        st.caption(f"⑤ 漂移事件流 · {len(events)} 筆", help=HELP_PANEL_EVENTS)
        if not events:
            st.info("尚無漂移事件")
            return
        for e in reversed(events[-10:]):
            label = f"t={e['timestamp']:,} · {e['source']} · {e['drift_type']}"
            with st.expander(label):
                st.json(e["details"])


def draw_report(events: List[Dict[str, Any]], gt_times: List[int]) -> None:
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
        return any(abs(e["timestamp"] - g) <= GT_TOLERANCE for g in gt_times)

    n_tp = sum(1 for e in events if is_tp(e))
    n_fp = len(events) - n_tp
    missed = [g for g in gt_times
              if not any(abs(d - g) <= GT_TOLERANCE for d in det_times)]

    delay = _detection_delay(gt_times, det_times, GT_TOLERANCE)
    fw_rate = _false_warning_rate(det_times, gt_times, GT_TOLERANCE)
    conf_delays = [e["confirmation_t"] - e["warning_t"] for e in events]
    reuse_better = [
        e for e in events
        if (e["details"].get("acc_best_on_warning") is not None
            and e["details"].get("acc_new_on_warning") is not None
            and e["details"]["acc_best_on_warning"] >= e["details"]["acc_new_on_warning"])
    ]

    cols = st.columns(4)
    cols[0].metric("TP · 真漂移", n_tp)
    cols[1].metric("FP · 誤報", n_fp, delta=f"誤報率 {fw_rate:.0%}",
                   delta_color="inverse")
    cols[2].metric("漏報 · 未偵測到", len(missed), f"/ {len(gt_times)} 個真漂移")
    cols[3].metric("平均偵測延遲", f"{delay:.0f}",
                   help=f"每個真漂移到最近偵測的平均距離；未配對者以 {GT_TOLERANCE} 計"
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
        "非逐筆分類的 per-class 版本 —— 後者未存於事件層，見 ② 面板說明。"
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
        f"TP/FP 以 warning_t 與最近真漂移相距 ≤ {GT_TOLERANCE} 判定，"
        f"計分函式直接取自 `run_ecpf_uq_experiment`，故與批次報表一致。"
    )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="ECPF 即時監控台", layout="wide")
    st.title("ECPF 即時監控台")

    streams = demo_streams()
    stream_labels = {p: f"{label} · {p.name}" for label, p in streams}

    with st.sidebar:
        st.header("設定")
        if not streams:
            dirs = "、".join(str(d) for _, d in DEMO_DRIFT_DIRS)
            st.error(f"找不到資料：請確認 {dirs} 內有 *.csv")
            st.stop()
        csv_path = st.selectbox("資料檔", [p for _, p in streams],
                                format_func=lambda p: stream_labels[p],
                                help=HELP_CSV)
        warm_start = st.number_input("warm_start", 0, 10_000, 200, step=50,
                                     help=HELP_WARM_START)
        max_steps = st.number_input("max_steps（0 = 全部）", 0, 200_000, 20_000, step=1000,
                                    help=HELP_MAX_STEPS)
        stride = st.slider("重繪間隔 STRIDE", 10, 500, 50, step=10, help=HELP_STRIDE)
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
        detector_delta = st.number_input("detector_delta", 0.0, 1.0, 0.05, step=0.01,
                                         format="%.3f", help=HELP_DELTA)
        detector_delta_w = st.number_input("detector_delta_w", 0.0, 1.0, 0.1, step=0.01,
                                           format="%.3f", help=HELP_DELTA_W)
        detector_min_instances = st.number_input("detector_min_instances", 1, 1000, 30,
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

    if not start:
        st.info("在左側設定參數後按「開始監控」。跑完為止，中途無法暫停"
                "（見 docs/ECPF_MONITOR_PLAN.md §4.2）。")
        return

    opts = dict(
        signal_mode=signal_mode, warning_signal=warning_signal,
        drift_signal=drift_signal, warning_detector=warning_detector,
        drift_detector=drift_detector, detector_delta=detector_delta,
        detector_delta_w=detector_delta_w,
        detector_min_instances=detector_min_instances,
        max_pool_size=max_pool_size,
        similarity_margin=similarity_margin,
        fade_points=fade_points, fade_enabled=fade_enabled,
        model_type=model_type,
    )

    X, y, gt_times = load_recurring_stream_pair(str(csv_path))
    if max_steps > 0:
        n = min(int(max_steps), len(y))
        X, y = X[:n], y[:n]
        gt_times = [t for t in gt_times if t < n]
    n_total = len(y)

    pipe = build_pipeline(opts)

    ph_head = st.empty()
    ph_preq = st.empty()
    col_l, col_r = st.columns(2)
    ph_chart, ph_buffer, ph_duel = col_l.empty(), col_l.empty(), col_l.empty()
    ph_pool, ph_events = col_r.empty(), col_r.empty()

    hist: deque = deque(maxlen=HIST_POINTS)
    preq_hist: deque = deque(maxlen=HIST_POINTS)
    duel_hist: deque = deque(maxlen=HIST_POINTS)
    events: List[Dict[str, Any]] = []
    correct: deque = deque(maxlen=500)  # rolling accuracy window
    warn_win: deque = deque(maxlen=200)  # rolling windows for the signal lines
    drift_win: deque = deque(maxlen=200)
    n_correct_total = 0  # cumulative, never evicted -- matches
    n_seen_total = 0     # run_ecpf_uq_experiment's `prequential_accuracy`
    last_swaps = 0
    last_warn_active = False
    t0 = time.perf_counter()

    def redraw(t: int) -> None:
        ecpf = pipe._ecpf
        pool = pool_snapshot(ecpf)
        acc = (sum(correct) / len(correct)) if correct else None
        preq_acc = (n_correct_total / n_seen_total) if n_seen_total else None
        draw_header(ph_head, t, n_total, acc, len(pool), len(events),
                    time.perf_counter() - t0)
        draw_prequential(ph_preq, preq_hist, preq_acc)
        draw_chart(ph_chart, hist, events, gt_times,
                   opts["warning_signal"], opts["drift_signal"])
        draw_buffer(ph_buffer, pipe, t, events)
        draw_duel(ph_duel, ecpf, duel_hist)
        draw_pool(ph_pool, pool, opts["max_pool_size"])
        draw_events(ph_events, events)

    for t, y_true, y_pred, dets, drift in pipe.run_stream(X, y, int(warm_start)):
        is_correct = 1 if y_pred == y_true else 0
        correct.append(is_correct)
        n_correct_total += is_correct
        n_seen_total += 1
        ecpf = pipe._ecpf

        # ECPFAdwinFamilyDetector.stats is (re)written on every update_values
        # call; it is absent before the first call and the detector itself is
        # None for signal modes that do not use it (e.g. oracle_*).
        stats = getattr(pipe._ecpf_detector, "stats", None) or {}
        if stats.get("warning_value") is not None:
            warn_win.append(float(stats["warning_value"]))
        if stats.get("drift_value") is not None:
            drift_win.append(float(stats["drift_value"]))
        # The rolling windows above advance every sample, but the chart series
        # is sampled once per stride: at HIST_POINTS=2000 that spans the whole
        # 100k stream, so the ground-truth bands stay on screen instead of
        # scrolling off after 2000 samples.
        # Both lines are rolling means. Raw values are unreadable at this
        # density: with signal="error" they are a 0/1 spike train, and even
        # continuous UQ signals are heavily jittered per sample.
        if t % stride == 0 or drift:
            hist.append(
                {
                    "t": t,
                    "warn_val": (sum(warn_win) / len(warn_win)) if warn_win else None,
                    "drift_val": (sum(drift_win) / len(drift_win)) if drift_win else None,
                }
            )
            preq_hist.append({"t": t, "acc": n_correct_total / n_seen_total})
        if ecpf is not None and ecpf.new_model is not None:
            duel_hist.append(
                {"t": t, "leader": ecpf.curr_correct, "shadow": ecpf.new_correct}
            )

        for d in dets:
            # `DriftDetection.timestamp` is the *warning start*, not the
            # confirmation (`_handle_ecpf_drift` is called with the buffered
            # `_ecpf_warning_start_idx`). The confirmation is the step we are
            # on right now. The batch runner scores against `timestamp` too,
            # so TP/FP here match its numbers.
            events.append(
                {
                    "timestamp": int(d.timestamp),
                    "warning_t": int(d.timestamp),
                    "confirmation_t": int(t),
                    "source": d.detector_source,
                    "drift_type": d.drift_type.value,
                    "details": d.details or {},
                }
            )

        # 常態低頻聚合、關鍵事件穿透. Warning open/close is a trigger too: a
        # short warning phase can otherwise begin and end inside one stride and
        # never be drawn at all.
        swaps = ecpf.leader_swaps if ecpf is not None else 0
        warn_active = bool(getattr(pipe, "_ecpf_warning_active", False))
        if (
            drift
            or swaps != last_swaps
            or warn_active != last_warn_active
            or t % stride == 0
        ):
            redraw(t)
        last_swaps = swaps
        last_warn_active = warn_active

    redraw(n_total - 1)
    st.success(
        f"完成：{n_total:,} 筆，{len(events)} 個漂移事件，"
        f"耗時 {time.perf_counter() - t0:.1f}s"
    )
    draw_report(events, gt_times)


if __name__ == "__main__":
    main()
