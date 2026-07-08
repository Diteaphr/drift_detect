# 先讀我：逐步輸出（Stage Trace）實驗復現指南

> **跑這個實驗前先看完這份。** 逐步輸出實驗會把 ECPF 流程「每一階段的中間結果」記錄下來，
> 供事後的可解釋性分析使用。它是 **observer-only（純觀察）**：只記錄 pipeline 本來就算出來的值，
> **不影響任何偵測 / adaptation 決策**，預設關閉，開啟後正常流程行為完全一致。

---

## 1. 這個實驗在做什麼

在一次 ECPF run 裡，針對每個 drift event 記錄四個階段的中間輸出，全部以 `event_id` 對齊，方便 join：

| 階段 | 內容 | 產出檔 |
|------|------|--------|
| **Stage 1 — signals** | 每個 event 前後 `±trace_window` 範圍內的逐 sample：`err`、warning/drift signal、是否觸發 | `stage1_signals.csv` |
| **Stage 2 — detection** | 每個 event 的 warning / confirmation 時間點與 detector 統計 | `stage2_detection.jsonl` |
| **Stage 3 — profiling** | 每個 event 的 `ECPFMetaLearner.on_drift` 細節（reuse 候選、各 expert 在 warning buffer 上的 accuracy、pool merge…） | `stage3_profiling.jsonl` |
| **Stage 4 — duel** | 每個 event drift 後 in-control 期間，leader vs 新訓練 shadow 的對決軌跡、leader-swap 步數與最終贏家 | `stage4_duel.jsonl` |

核心驗證問題：**drift 當下用 warning buffer 快照挑出的 reuse 候選（`reuse_looked_better`），
是否真的撐過了 drift 後的實戰對決（`reuse_survived`）？** 兩者一致率即 `snapshot_matched_duel`。

---

## 2. 前置需求

- Python 環境（與本專案一致；`numpy`、`pandas` 必需，`matplotlib` 選用，缺了只是不畫 timeline 圖）。
- 資料已在 repo：`data/recurring_drift/recurring_sud_sea100k_g00..g09.csv`（含對應 `*_drift_times.txt`）。
- 在專案根目錄執行以下指令。

---

## 3. Step 1 — 產生 traces

逐步輸出是掛在既有 runner `scripts/run_ecpf_final_selection.py` 上，加 `--trace events` 開啟。

### 完整版（當初正式跑的那組，30 runs）

`uqdet_stageb` stage：config = `uq_vote_seqdrift2` / `uq_entropy_adwin` / `uq_variance_seqdrift2`，
資料 recurring g00–g09，每條 stream 前 50000 rows。

```
python scripts/run_ecpf_final_selection.py --stage uqdet_stageb --execute --output-dir outputs/stage_trace_recurring --trace events --trace-window 300
```

### 快速煙霧版（先確認能跑，幾分鐘）

`uqdet_smoke` stage 預設只跑 2 個檔；再用 `--max-steps` 砍短：

```
python scripts/run_ecpf_final_selection.py --stage uqdet_smoke --execute --output-dir outputs/smoke_stage_trace --trace events --limit-files 1 --max-steps 2000
```

**開關與參數：**

| 參數 | 意義 | 預設 |
|------|------|------|
| `--trace {off,events}` | `events` 才開啟逐步輸出 | `off` |
| `--trace-window N` | Stage 1 只保留每個 event 前後 ±N sample 的 signal | `300` |

> 底層對應 `PipelineConfig.trace_enabled` / `trace_window`（見 `src/config.py`）。
> 直接用 pipeline 時，設 `cfg.trace_enabled = True` 即可，無 tracer 時走 `NullTracer` 零成本。

產出落在 `<output-dir>/traces/<config_id>/<檔名>/`，每個 (config, file) 一組 stage1–4 + `meta.json`。

---

## 4. Step 2 — 分析 / join stages

```
python scripts/analyze_stage_interactions.py --run-dir outputs/stage_trace_recurring
```

參數：
- `--run-dir`：Step 1 的 `--output-dir`（底下要有 `traces/`）。
- `--extension N`：把 event 對齊 ground-truth drift interval 時的容忍 ±N sample（預設 0）。

產出於 `<run-dir>/analysis/`：
- `event_interactions.csv` — 每個 drift event 一列，join 了 stage 2/3/4 + ground-truth 對齊 + stage-1 pre-warning 特徵（斜率/峰值）。
- `timeline_<config>_<file>.png` — signal timeline，標出 warning（橘虛線）/ confirmation（紅實線）/ GT drift 區間（黃色），`matplotlib` 缺席則略過。

終端也會印摘要：TP/FP、reuse 是否在 buffer 上看起來較好、reuse 是否撐過對決、**snapshot 與 duel 的一致率**、平均 warning→confirm age。

---

## 5. 輸出檔案結構

```
outputs/stage_trace_recurring/
  uqdet_stageb_details.csv        # runner 原本的 per-run summary
  uqdet_stageb_events.csv
  uqdet_stageb_summary.csv
  ranked_configs.csv
  report.md
  traces/
    <config_id>/
      <stream>.csv/
        stage1_signals.csv        # event 附近逐 sample，tagged by event_id
        stage2_detection.jsonl    # 一行一 event：timing + detector stats
        stage3_profiling.jsonl    # 一行一 event：on_drift 細節
        stage4_duel.jsonl         # 一行一 event：drift 後對決軌跡
        meta.json                 # ground-truth drift starts/intervals + run metadata
  analysis/                       # analyze_stage_interactions.py 產出
    event_interactions.csv
    timeline_<config>_<file>.png
```

`event_interactions.csv` 幾個關鍵欄位：

| 欄位 | 意義 |
|------|------|
| `gt_match` | 該 event 是否命中 ground-truth drift interval（TP / FP） |
| `warning_to_confirm_age` | warning 到 confirmation 的間隔（sample 數） |
| `reuse_looked_better` | drift 當下，pool 最佳 model 在 warning buffer 上是否 ≥ 全新 model |
| `reuse_survived` | drift 後對決中，reuse 的 model 是否從未被 fresh 取代（`n_leader_swaps == 0`） |
| `snapshot_matched_duel` | 上面兩者是否一致（快照判斷 vs 實戰結果）——**核心指標** |
| `prewarn_slope/peak/mean` | warning 觸發前 warning signal 的斜率 / 峰值 / 均值 |

---

## 6. 注意：輸出很大，不進版控

完整 `uqdet_stageb` 一次跑下來 `outputs/stage_trace_recurring/` 約 **215MB**（Stage 1 逐 sample signal 是大宗）。
這些是**可重新生成的產物**，已在 `.gitignore` 排除，不 commit。要重現就照上面 Step 1–2 重跑即可。

---

## 7. 相關程式碼

| 檔案 | 角色 |
|------|------|
| `src/tracing.py` | `StageTracer` / `NullTracer`，observer-only，負責累積並 flush stage 1–4 |
| `src/config.py` | `trace_enabled` / `trace_window` 開關 |
| `src/pipeline.py` | 在 signal / duel / on_drift 處掛 tracer hook（不影響決策） |
| `src/ecpf.py` | `leader_swaps` 計數 + `acc_on_buffer`（stage 3/4 用） |
| `scripts/run_ecpf_final_selection.py` | `--trace` / `--trace-window`，把 tracer 接進 run loop |
| `scripts/analyze_stage_interactions.py` | join stages、算對齊與一致率、畫 timeline |
