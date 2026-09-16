# 雙介面 Dashboard 規劃 · 一般使用者 vs 工程師

現況：`monitor_app.py`（970 行）是單一介面，等同本文的「工程師介面」雛形
（① 訊號時序 ② 警告緩衝 ③ 模型池 ④ in-control 對決 ⑤ 事件流 ⑧ 離線報告，
外加約 20 個 sidebar 參數）。本文規劃如何拆成兩個角色介面。

原始版面決策見 `docs/ECPF_MONITOR_PLAN.md`，本文只談角色分流後的增修。

---

## 0. 先解掉的前提問題：drift type 從哪來

> **現況（2026-09-16）**：下方建議的 v2 已到位 —— `src/pipeline.py` 在 ECPF 確認漂移時
> 呼叫 Type-LDD FAN ProtoNet（`src/type_ldd`，權重在 `checkpoints/type_ldd`），
> 把標籤寫進 `details["type_ldd_prediction"]`；`core/drift_type.py` 讀這個欄位，
> 並以 ECPF 重用判定優先給出 recurring（即 §0.3 的四分類）。
> 信心度尚未顯示：分類器的 softmax 在真實誤差序列上飽和到 0/1，校準前不能當信心用。
> 以下為原始規劃，保留作為決策紀錄。

一般使用者介面的核心欄位之一是「漂移型態」，但目前 **ECPF 路徑不會分類型態**：
`src/pipeline.py:817` 的 `_handle_ecpf_drift` 一律寫死 `DriftType.SUDDEN`。
真正的分類器在兩個地方，都沒有接進 ECPF：

| 來源 | 位置 | 輸出 | 成本 |
|---|---|---|---|
| DTC-RF（Type-LDD 風格） | `src/drift_type_classifier_dtc_rf.classify_drift_type(errors, t)` | sudden / gradual / incremental | 極低，已在非 ECPF 的 recurring 路徑使用（`pipeline.py:963`） |
| FAN + ProtoNet | `DriftTypeClassifier/`，`predict_drift_types_with_prototypes` + `checkpoints/best.pt` | label **與機率** | 需 torch，但有現成 checkpoint |

建議：
1. **v1**：在 `_handle_ecpf_drift` 確認漂移時，用手邊的 error 序列呼叫 DTC-RF，
   把結果寫進 `DriftDetection.drift_type`（或先只寫 `details["drift_type_pred"]`
   以免影響既有 ECPF 策略分支），監控台就有型態可顯示。
2. **v2**：改接 ProtoNet，因為它同時給機率 → 一般使用者介面可以顯示「信心度」，
   這是專題的賣點之一。
3. **recurring 不必靠分類器猜**：ECPF 若在事件當下重用了池中舊專家
   （`acc_best_on_warning >= acc_new_on_warning`），本身就是 recurring 的直接證據。
   把「三分類器 + ECPF 重用訊號」合成四分類（sudden/gradual/incremental/recurring），
   比單靠任一邊更有說服力。

**不要**用檔名或資料夾（`data/sudden_drift/…`）當型態來源 —— 那是 ground truth，
只能出現在離線報告裡當作對照，不能當成系統的輸出。

---

## 1. 分界原則

| | 一般使用者介面 | 工程師介面 |
|---|---|---|
| 使用者要回答的問題 | 「現在還能不能信這個模型？出事了嗎？要不要處理？」 | 「為什麼觸發？是哪一層決定的？參數怎麼調？」 |
| 時間視角 | 現在狀態 + 事後摘要 | 逐步過程、每一層的中間值 |
| 可調參數 | 只有「選資料 / 開始」 | 全部 |
| 語言 | 自然語言句子、狀態燈、少量圖 | 指標、時序圖、JSON |
| 錯誤處理 | 一句話 + 建議動作 | traceback / raw details |

一句話原則：**一般介面只呈現「結論與其後果」，工程師介面呈現「過程與其證據」。**

---

## 2. 一般使用者介面（Operator View）

### 2.1 必備區塊

1. **健康狀態燈**（畫面最上方，最大元素）
   - 🟢 穩定 / 🟡 觀察中（warning 開啟但未確認）/ 🔴 剛發生漂移（最近 N 步內）
   - 配一句話結論：「模型運作正常，近 5,000 筆準確率 0.87。」
   - 「觀察中」這個中間態很重要：它讓使用者看到系統不是只有事後才反應。

2. **一張主圖**：prequential 準確率時間軸 + 漂移紅線 + warning 淡黃區塊。
   其餘四張圖全部不出現。

3. **漂移事件卡片**（取代工程師介面的 JSON expander），每張卡片：
   - 何時：`t=12,340`（建議同時顯示成假想批次/日期，比 index 好懂）
   - 什麼型態：badge（突變 / 漸變 / 緩慢累積 / 舊概念重現）+ 信心度
   - 影響：漂移前後準確率（例：0.88 → 0.61，掉了 27 個百分點）
   - 系統做了什麼：「重用了先前學過的專家 #3」/「重新訓練了一個新模型」
   - 多久恢復：準確率回到漂移前 95% 所需步數
   - 建議動作：一句話（見 §4 模板）

4. **本次總結**：資料筆數、漂移次數、各型態次數、平均恢復時間、目前準確率。

5. **匯出**：一頁式摘要（CSV / Markdown；PDF 可後補）。老師/助教 demo 時很加分。

### 2.2 值得加、常被忽略的設計

- **恢復時間（time-to-recover）**：非技術使用者對「掉多少、多久回來」最有感，
  比 detection delay 更能溝通系統價值。目前程式沒有算，要新增。
- **「系統現在用哪個概念」的人話版**：ECPF 的 pool / leader swap 是很強的故事，
  但要翻譯成「系統切回了先前學過的模式（第 3 種）」而不是 `leader_swaps=4`。
- **信心度用文字分級**：高 / 中 / 低，不要直接丟 0.62。
- **無事發生時也要有話講**：「過去 20,000 筆沒有偵測到漂移，模型穩定。」
  空白畫面會讓使用者以為壞了。
- **不要即時逐格更新**：建議一般介面「跑完後呈現」或只更新狀態燈，
  避免圖表重繪把瀏覽器拖垮（這正是 `CHART_EVERY_DEFAULT` 註解描述的問題）。

### 2.3 明確不放

參數、detector 名稱、UQ signal、model pool 表格、buffer 對決、precision/recall/F1、
raw details JSON。這些一律留在工程師介面。

---

## 3. 工程師介面（Engineer View）

保留現有 ①–⑤ + ⑧，並補：

1. **三層結構標示**：把面板依 signal → detector → ECPF 決策 分組並標明層級，
   現在的編號看不出因果順序。
2. **成本面板**：throughput（筆/秒）、pool 佔用、每次漂移的重訓成本。
3. **原始資料下載**：events JSON、per-step 指標 CSV。
4. **Ground truth 疊圖開關**：目前 gt 只在報告用，圖上疊 gt 線能一眼看出延遲。

---

## 4. 自然語言 insight 怎麼產

還沒實作 先放 placeholder

---

## 5. 實作架構建議

`monitor_app.py` 已 970 行，兩個介面塞同一檔會失控。建議：

```
app.py                 # 入口，角色切換（st.navigation 或 sidebar radio）
views/operator.py      # 一般使用者介面
views/engineer.py      # 工程師介面（搬移現有 draw_* 面板）
core/run.py            # 跑 pipeline、收集 events / 指標（兩介面共用）
core/insights.py       # 事件 → 自然語言（§4）
core/metrics.py        # 恢復時間、漂移前後準確率等新指標
```

關鍵：**一次 run，兩種呈現**。把 run 結果（events、preq 曲線、pool 快照）存進
`st.session_state`，切換角色時不重跑。目前程式是「按開始 → 邊跑邊畫 → 結束」，
沒有保存 run 結果，這點要先改。

角色切換放 sidebar 最上方，預設「一般使用者」（老師打開第一眼看到的應該是簡潔版）。
不需要做登入/權限，這是展示用途，加了只會增加 demo 風險。

---

## 6. 建議實作順序

1. 把 run 結果存進 `st.session_state`，並拆出 `core/run.py`（其他全部依賴這步）。
2. ECPF 路徑接 drift type 分類（§0 的 v1），事件才有型態可顯示。
3. 新增恢復時間 / 漂移前後準確率指標。
4. 做 `core/insights.py` 模板。
5. 建 operator view（狀態燈 + 主圖 + 事件卡片 + 總結）。
6. 現有面板搬進 engineer view，加事件 drill-down 與 preset。
7. 有餘力再做：ProtoNet 信心度、run 比較、匯出。

---

## 7. 實作狀態（2026-08-24）

```
app.py                 # 入口，sidebar 最上方切換角色，預設一般使用者
core/run.py            # 跑 pipeline、收集 RunResult（兩介面共用）
core/metrics.py        # 恢復時間、漂移前後準確率、成本統計
core/drift_type.py     # 型態分類的介面（placeholder，見下）
core/insights.py       # 自然語言 insight（placeholder，§4）
views/operator.py      # 一般使用者介面
views/engineer.py      # 工程師介面（原 monitor_app.py 的面板）
monitor_app.py         # 轉接檔，指向 app.py（部署設定沿用舊檔名）
```

已完成：

- **一次 run，兩種呈現**：run 結果存進 `st.session_state["run_result"]`，
  切換角色只重畫、不重跑。跑的過程只有工程師介面即時畫面板，
  一般使用者介面只顯示進度條。
- 一般使用者介面：狀態燈（🟢/🟡/🔴）+ 一句話結論、一張準確率主圖
  （疊漂移紅線與 warning 黃底）、事件卡片（型態 / 掉幅 / 恢復 / 系統做了什麼）、
  本次總結、Markdown 摘要下載。
- 工程師介面：原 ①–⑤ + ⑧ 全部保留，加上面板分層標示、⑥ 成本效能、
  ⑦ events JSON 與 per-step CSV 下載、① 圖的 ground truth 疊圖開關。
- 恢復時間定義：以 **warning_t（變化開始）** 為起點，
  準確率回到變化前 95% 所需的資料量；視窗到下一次事件為止。
  兩個介面的「第 X 筆」一律以 warning_t 為準，與批次腳本計分口徑一致。

**型態分類仍是 placeholder（§0 尚未做）**：`core/drift_type.py` 是那個介面。
`recurring` 已經是真的 —— 當 ECPF 重用的舊專家在 warning buffer 上贏過
全新訓練的模型，就直接判為舊概念重現（§0.3），不需要分類器。
`sudden / gradual / incremental` 一律回傳 `label=None`，卡片上顯示
「🔍 待分類」並標明分類器尚未接上。接上時只要改 `drift_type.predict()`，
兩個介面都不用動。

工程師介面 ⑤ 事件流上的 `drift_type` 欄仍是 pipeline 的原始欄位，
在 ECPF 路徑一律是 `sudden`（`src/pipeline.py` 寫死），面板說明已註明，
不要拿它當分類結果看。
