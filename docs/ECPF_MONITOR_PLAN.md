# ECPF 即時監控台 · 實作規劃

**狀態：** 已定案，v1 實作中
**產出：** `monitor_app.py`（Streamlit，專案根目錄）
**對 `src/` 的修改：** 零

---

## 1. 為什麼是 Streamlit（以及為什麼不是自幹 SSE）

第一版規劃走的是「`StreamTracer` + `http.server` SSE + 手刻前端」，前提是
**「即時資料通道不存在，要自己建」**。這個前提是錯的：

- `ConceptDriftPipeline.run_stream()`（`src/pipeline.py:1083`）本身就是
  **generator**，每筆 yield `(index, y_true, y_pred, detections, drift_occurred)`。
- `DriftDetection.details`（`src/config.py:24`）在 `_handle_ecpf_drift`
  （`src/pipeline.py:794`）裡已經是 `detector_details`（stage2）與
  `ecpf.on_drift()` 回傳（stage3）**合併後的完整 dict**。
- 對決與模型池狀態每步都可從 `pipeline._ecpf` 直接讀：
  `curr_correct` / `new_correct` / `total_inst` / `leader_swaps` /
  `slots` / `fade_scores` / `current_idx`。

也就是說 **stage 1–4 的資料早就從 generator 送出來了**。原規劃等於改
`tracing.py` 再把同一份資料用 SSE 推第二遍 — 純屬多餘。

**結論：** 一個 `for` 迴圈 + `st.empty()` placeholder 就夠。約 200 行，單檔，
零侵入。

### `src/tracing.py` 的定位不變

`StageTracer` 是**批次落地**用的（累積在記憶體，`flush()` 時寫
`stage1_signals.csv` / `stage2_detection.jsonl` / `stage3_profiling.jsonl` /
`stage4_duel.jsonl`），服務離線可解釋性分析。監控台不碰它，兩者互不影響。
未來的回放模式會反過來**讀**這些落地檔案。

---

## 2. 架構

```python
# monitor_app.py — streamlit run monitor_app.py
pipe = ConceptDriftPipeline(cfg)
ph = {k: st.empty() for k in ("head", "chart", "pool", "duel", "events")}

for t, y_true, y_pred, dets, drift in pipe.run_stream(X, y, warm_start):
    hist.append(...)                    # ring buffer，最近 N 點
    if dets:
        events.append(dets[0])          # details 已含 stage2 + stage3
    if t % STRIDE == 0 or dets:         # 常態節流、事件穿透
        redraw(ph, hist, events, pipe._ecpf)
```

### 節流

唯一從第一版規劃留下來的設計。每筆都重繪會卡（不論用什麼框架都一樣）：

| 情況 | 策略 |
| --- | --- |
| 常態 | 每 `STRIDE`（預設 50）筆重繪一次 |
| 漂移確認 | **立即重繪**，不等 stride |
| leader 換將 | 立即重繪（`leader_swaps` 增加時） |

即「常態低頻聚合、關鍵事件穿透」。`STRIDE` 做成 sidebar 可調。

---

## 3. 版面

不照搬 `docs/ecpf_gui_manual` 的 8 步動線 — 那是**教學動線**（逐步講解），
即時監控要的是**同時看見**。

| 區塊 | 元件 | 資料來源 |
| --- | --- | --- |
| 頂列 | `st.progress` + `st.metric` × 3（t / acc / 池大小） | 迴圈變數 |
| 左① | 訊號時序圖，drift 垂直線 | `hist` |
| 左② | 警告緩衝累積 + `new_model` 訓練結果 | `pipe._ecpf_warning_active` / `_ecpf_buffer`；`acc_*_on_warning` |
| 左④ | leader vs shadow 對決雙線、換將標記 | `pipe._ecpf.curr_correct` / `new_correct` |
| 右③ | 模型池 slot 卡 + fade 分數條，leader 高亮 | `pipe._ecpf.slots` / `fade_scores` / `current_idx` |
| 右⑤ | 事件表，展開看全欄位 | `st.json(d.details)` |

### ② 警告緩衝面板的兩個時鐘

這一區對應 HTML 手冊的 S9。要注意它的兩半跑在不同時鐘上：

- **buffer 累積是即時的** — 每步 `_ecpf_buffer.append()` 一筆，直到漂移確認。
- **`new_model` 訓練不是。** 它在漂移那一瞬間由 `_fit_on_buffer()` 一次 fit 完
  （`src/ecpf.py:273`），**沒有逐步訓練曲線**，只有結果。

**不畫 buffer 進度條**：detector 模式下 buffer 無上限，一路長到漂移確認為止
（實測最大 2048 筆）。`ecpf_warning_length=60` 只在 oracle / retro 模式套用
（`src/pipeline.py:381`）。畫成「填到 60」會是假的。

**顯示三方對比**而非只有 `acc_new`：`acc_current_on_warning` /
`acc_best_on_warning` / `acc_new_on_warning`，因為「重用 vs 全新」的勝負才是
這一步的決策內容。S9 只顯示了 new。

**不提供 precision / recall / F1**：S9 那三張卡片標的是「示意」（由 acc 模擬）。
per-class 明細未存於事件層，沒有真值可畫，因此本監控台直接不做。

Sidebar：資料檔選擇、`warm_start`、`max_steps`、偵測器組合、`STRIDE`，
按「開始」才跑。

---

## 4. 已知取捨（v1 接受）

**4.1 視覺不會像 `ecpf_gui_manual`。**
那份是手刻的 `#1A7A4A` 綠 / `#EAE8E0` 底 / Noto Serif TC 標題。Streamlit 要逼近
只能靠 `st.markdown(unsafe_allow_html=True)` 硬塞 CSS，而那正好把「用 Streamlit
比較簡單」的好處吃掉。v1 先接受預設外觀，功能對了再談皮。

**4.2 不做暫停 / 續跑。**
Streamlit 每次互動整個 script 重跑，會直接砍掉迴圈。要做得靠
`st.session_state` 分段跑，複雜度回升。v1 直接跑到完。

**4.3 `docs/ecpf_training_monitor/` 是假資料。**
它用 `seededRng(seed)` 產生確定性的「示意」數值，UI 骨架在、資料是捏的。
本監控台**取代**它的功能定位；那份保留為設計稿參考，不接真實資料。

---

## 5. 後續（非 v1）

- **回放模式**：讀落地的 `stage*.jsonl` 餵同一套 `redraw()`，讓 `outputs/`
  裡的歷史 run 也能用同一個介面看。在 Streamlit 反而比 live 更簡單。
- **多 config 並排**：目前只監控單檔 run（對應 `run_ecpf_uq_experiment.run_one`）。
  若要監控 `run_ecpf_recurring_grid.py` 那種網格，UI 需要多一層 config 切換。
- **視覺美化**：見 4.1。

---

## 6. 依賴

Streamlit **未安裝**（`.venv` / `.venv311` 皆無）：

```bash
pip install streamlit
```

`requirements.txt` 刻意維持精簡（`torch` / `xgboost` 都是註解掉的 optional），
因此 `streamlit` 同樣列入 optional 註解區，不進 core。
