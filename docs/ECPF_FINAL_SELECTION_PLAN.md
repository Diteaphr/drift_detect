# ECPF 最終配置選型實驗報告

## 摘要

這份報告的目標不是找出「單獨 detector 分數最高」的演算法，而是規劃一套可執行的實驗流程，用來找出最適合整體 ECPF 流程的配置。

ECPF 的 detector 不是孤立模組。它會決定：

- warning stage 什麼時候開啟 collection buffer
- drift confirmation stage 什麼時候觸發 ECPF adaptation
- UQ signal 是否有幫助，以及應該放在 warning、confirmation，還是兩者都放
- 最終配置是否真的改善 prediction、model reuse 與 post-drift recovery

因此舊 detector 指標只用來縮小候選集合；最後決策必須以完整 ECPF end-to-end 表現為準。`CD%`、`FP`、`delay` 是診斷指標，不是最終目標函數。

## 核心問題

本次實驗要回答的是：

1. ECPF 最適合使用哪一種 warning detector？
2. ECPF 最適合使用哪一種 drift confirmation detector？
3. SeqDrift2 應該放在 warning、confirmation、兩者都放，還是不要用？
4. UQ signal 應該用哪一種：`mi_like`、`vote_disagreement`、`predictive_entropy`、`variance_eu`？
5. 純 UQ 是否可行，還是應該採用「UQ warning + error confirmation」？
6. 哪一組配置在完整 ECPF 流程中 recovery 最快、false adaptation 最少、prediction 表現最好？

## 舊實驗證據

目前 repo 中有兩組舊實驗可以重用。它們不足以直接決定最終配置，但足夠用來篩出第一輪候選。

### 1. ADWIN / SEED / SeqDrift2 grid

- Runner: `run_ecpf_recurring_grid.py`
- Output: `outputs/ecpf_recurring_grid_20k_summary.csv`
- Dataset: `data/recurring_drift/recurring_sud_sea100k_g00..g09.csv`
- Rows: 每條 stream 前 20k rows
- Warm start: 200 rows
- 掃描維度：
  - warning detector: `adwin`, `seed`, `seqdrift2`
  - drift detector: `adwin`, `seed`, `seqdrift2`
  - warning signal: `error`, `uq_mi`, `uq_vote`, `uq_entropy`, `uq_variance`
  - drift signal: 同 warning signal set

這組實驗提供的線索：

- `adwin warning + seqdrift2 drift` 搭配 `error/error` 的 accuracy 高，而且 detected count 接近 actual drift count，是目前最值得優先重測的舊-grid 候選。
- `dual_adwin` 是強 baseline，但偵測數略偏敏感。
- `dual_seqdrift2` 是最敏感的 family，應視為 high-recall / possible high-FP candidate，而不是直接視為最佳配置。
- SEED-heavy configs 常看起來 accuracy 不錯，但主要原因可能是偵測太少，因此不能只用 accuracy 判斷。

### 2. HCDT / UQ-family ECPF runs

- Runners: `run_ecpf_recurring_batch.py`, `run_ecpf_uq_experiment.py`
- Outputs:
  - `outputs/ecpf_hcdt_20k_summary.csv`
  - `outputs/ecpf_hcdt_20k_balanced_summary.csv`
  - `outputs/ecpf_hcdt_20k_threshold_summary.csv`
  - `outputs/ecpf_hcdt_20k_sensitive_summary.csv`
- Dataset: recurring sudden `g00..g09`
- Rows: 多數為前 20k rows

這組實驗提供的線索：

- HCDT standard / threshold-style settings 值得重測。
- HCDT sensitive settings 會造成 event count 爆炸，不適合作為 default candidate。
- Pure UQ 或 UQ-heavy path 需要 end-to-end validation，因為 UQ 可能偵測到的是 uncertainty，而不一定是真正的 concept drift。

## 候選配置

第一輪不要把所有 detector、UQ、model backend、ECPF 參數全部交叉相乘。建議先使用 4-6 個 candidate families，每個 family 只給很小的 parameter grid。`C0` 是上限參考，不是可部署配置。

### C0: Oracle Upper Bound

目的：作為 sanity upper bound。

```text
signal_mode = oracle_60
model_type = ht and/or hf
```

這組用來估計「如果 warning timing 完美，ECPF 最多能帶來多少改善」。如果 `oracle_60` 都沒有幫助，代表問題不在 detector tuning，而是整體 ECPF design 或 adaptation 方式需要調整。

### C1: Dual ADWIN Baseline

目的：建立穩定 baseline。

```text
signal_mode = dual_adwin
warning_signal = error
drift_signal = error
model_type = ht
detector_delta in [0.02, 0.05, 0.10]
detector_delta_w = 2 * detector_delta
```

這組回答的是：最簡單的 two-stage error detector 放進 ECPF 後，整體表現可以到哪裡。

### C2: ADWIN Warning + SeqDrift2 Drift

目的：重測舊 grid 中最有潛力的候選。

```text
signal_mode = hybrid_adwin_family
warning_detector = adwin
drift_detector = seqdrift2
warning_signal = error
drift_signal = error
model_type = ht
detector_delta in [0.02, 0.05, 0.10]
detector_delta_w = 2 * detector_delta
detector_min_instances in [30, 60]
```

解讀方式：ADWIN 負責開啟 warning buffer，SeqDrift2 負責較嚴格的 drift confirmation。這組是目前最值得優先進入完整 ECPF 重測的配置。

### C3: SeqDrift2 Warning + ADWIN Drift

目的：做 symmetry check，測試 SeqDrift2 是否適合當 early-warning detector。

```text
signal_mode = hybrid_adwin_family
warning_detector = seqdrift2
drift_detector = adwin
warning_signal = error
drift_signal = error
model_type = ht
detector_delta in [0.02, 0.05, 0.10]
detector_delta_w = 2 * detector_delta
detector_min_instances in [30, 60]
```

解讀方式：SeqDrift2 嘗試提早開啟 collection buffer，ADWIN 負責確認 drift。如果這組表現好，表示 SeqDrift2 可作為 warning detector；如果 over-collect 或 false adaptation 偏多，則 SeqDrift2 較適合只放在 confirmation stage。

### C4: Dual SeqDrift2

目的：測試 high-sensitivity boundary。

```text
signal_mode = dual_seqdrift2
warning_signal = error
drift_signal = error
model_type = ht
detector_min_instances in [30, 60, 100]
```

這組不應預設為最佳配置。它的用途是測量 SeqDrift2 的高敏感度到底能不能改善 recovery，還是只會造成 false adaptation。

### C5: HCDT ECPF

目的：測試 structured two-layer detector candidate。

```text
signal_mode = meta_ecpf_hcdt
model_type = ht or hf
ecpf_hcdt_detection_delta in [0.003, 0.005, 0.01]
ecpf_hcdt_detection_threshold in [0.05, 0.07, 0.10]
ecpf_hcdt_rddm_drift_level in [2.5, 3.0]
```

建議從 standard / threshold-like settings 開始。除非目標是壓力測試，否則不要把舊的 sensitive profile 放進第一輪候選。

### C6: UQ Warning + Error Confirmation

目的：先測最合理的 UQ 設計。

```text
signal_mode = uq_warning
model_type = hf
ecpf_uq_mode in [
  mi_like,
  vote_disagreement,
  predictive_entropy,
  variance_eu
]
drift confirmation = error-based ADWIN path
ecpf_uq_delta in [0.005, 0.01, 0.02]
ecpf_uq_smoothing_alpha in [0.05, 0.10, 0.20]
ecpf_uq_warning_timeout in [500, 1000, 2000]
```

這是最有機會成功的 UQ 架構：UQ 用來提早開啟 warning buffer，但 drift confirmation 仍由 error signal 驗證，避免 UQ 因為 ambiguity、冷啟動或 ensemble disagreement 過度觸發。

## 純 UQ 是否可行

結論：純 UQ 可以測，但不應作為第一輪主候選。它比較適合作為 Stage 2 ablation。

純 UQ 指的是 warning 與 confirmation 都由 UQ signal 驅動：

```text
signal_mode = hybrid_adwin_family
warning_detector = adwin or seqdrift2
drift_detector = adwin or seqdrift2
warning_signal = uq_mi / uq_vote / uq_entropy / uq_variance
drift_signal = same UQ signal
model_type = hf
```

純 UQ 的假設：

- UQ-only 可能比 error-only 更早反應。
- 但它也可能對 class overlap、cold start、model uncertainty 或 ensemble disagreement 觸發，而不是真正的 drift。
- 因此純 UQ 不能只看 early detection，必須看 false adaptation cost。

建議的 pure-UQ ablations：

```text
adwin/adwin + uq_entropy/uq_entropy
adwin/adwin + uq_vote/uq_vote
adwin/seqdrift2 + uq_mi/uq_mi
seqdrift2/seqdrift2 + uq_vote/uq_vote
```

如果 pure UQ 的 warning delay 變好，但 ECPF accuracy、reuse 或 recovery 變差，就應保留 UQ 作為 warning-only signal，而不是讓 UQ 同時控制 confirmation。

## 實驗流程

### Stage 0: Smoke Test

目的：在昂貴實驗前先抓出壞掉的 config。

- Datasets: `recurring_sud_sea100k_g00.csv`, `recurring_sud_sea100k_g01.csv`
- Rows: first 5k or 10k
- Candidates: `C1-C6`，每組只跑一個 default parameter setting
- 必要輸出：
  - no crash
  - event rows are saved
  - `cd_tp`, `cd_fp`, `cd_n`, `cd_score_pct` are present
  - prediction accuracy is not NaN

若 config crash，或 event log 明顯不完整，直接剔除。

### Stage 1: Candidate Screening

目的：從 6 個 candidate families 中選出最值得進入 full-size run 的 3-4 組。

- Datasets: `data/recurring_drift/recurring_sud_sea100k_g00..g09.csv`
- Rows: first 20k
- Warm start: 200
- 固定 ECPF core settings：
  - `ecpf_warning_length = 60`
  - `ecpf_max_pool_size = 10`
  - `ecpf_similarity_margin = 0.95`
  - `ecpf_fade_points = 15`
  - `ecpf_fade_enabled = True`
- 跑 `C1-C6` 的 tiny grids

主要 screening signals：

- mean prequential accuracy
- post-drift recovery speed
- false adaptation cost
- detected events compared with actual drifts
- runtime

Detector diagnostics：

- `CD%`
- FP per stream
- average delay
- count score
- warning-to-confirm age

不要只用 `CD%` 排名。`CD%` 應該用來解釋某個 ECPF config 為什麼成功或失敗。

### Stage 2: Parameter Refinement

目的：只針對 Stage 1 表現好的 family 做細部調參。

- 保留 Stage 1 前 3-4 組 families
- Split:
  - tune: `g00..g04`
  - validation: `g05..g09`
- Rows:
  - runtime 允許時跑 full stream
  - 否則先跑 50k，再讓 finalists 跑 full stream

一次只調一條軸：

1. detector sensitivity
2. warning timeout / buffer age
3. UQ mode and smoothing
4. ECPF similarity margin / pool size

避免在同一個 broad grid 裡同時掃 detector params 與 ECPF params，否則很難解釋結果。

### Stage 3: Final End-To-End Evaluation

目的：回答「最終應該使用哪一組 config」。

- Finalists: 只保留 2-3 組
- Datasets:
  - `data/recurring_drift`
  - `data/sudden_drift`
  - `data/gradual_drift`
  - `data/incremental_drift`
- Rows: full available streams
- Compare against:
  - no ECPF / existing main pipeline if applicable
  - `oracle_60` upper bound
  - `dual_adwin error/error` baseline

最終 ranking 必須基於 end-to-end ECPF behavior，而不是 detector-only behavior。

## 評估指標與排名規則

### End-to-end primary metrics

這些指標用於最終排名：

- `prequential_accuracy`
- cumulative error 或 mistake count
- post-drift recovery speed
- post-drift area under error curve
- false adaptation cost：detected event 不靠近 true drift 時，後續 performance 是否下降
- ECPF reuse usefulness:
  - best pool model 在 warning buffer 上勝過 current model 的比例
  - reuse precision
  - model pool size and churn
- runtime per stream

### Detector diagnostics

這些指標用於解釋結果，不直接作為最終目標函數：

- warning timestamps 與 confirmation timestamps 各自的 `CD%`
- FP count
- average detection delay
- count score: `1 - abs(N_detect - N_actual) / N_actual`
- warning-to-confirm age
- warning timeout / cancelled-warning count if available
- buffer length at drift handling

### Ranking rule

建議使用兩階段 ranking rule。

1. Hard reject:
   - event explosion: average `N_detect > 3 * N_actual`
   - silent detector: average `N_detect < 0.3 * N_actual`，除非 accuracy / recovery 明顯更好
   - severe runtime blow-up
   - recurrent false adaptation that lowers accuracy after events

2. Rank remaining configs:
   - primary: mean prequential accuracy and post-drift recovery
   - secondary: reuse usefulness and false adaptation cost
   - tertiary: `CD%`, `FP`, `delay`, runtime

## 輸出檔案

建議使用獨立 output root，避免覆蓋舊實驗：

```text
outputs/ecpf_final_selection/
  stage0_smoke_summary.csv
  stage0_smoke_events.csv
  stage1_screening_summary.csv
  stage1_screening_details.csv
  stage1_screening_events.csv
  stage2_tuning_summary.csv
  stage2_tuning_details.csv
  stage3_final_summary.csv
  stage3_final_details.csv
  ranked_configs.csv
  config_manifest.json
  report.md
```

每一列 summary / detail row 都應包含：

- `config_id`
- `family`
- `dataset`
- `max_steps`
- `model_type`
- `signal_mode`
- `warning_detector`
- `drift_detector`
- `warning_signal`
- `drift_signal`
- UQ params
- detector params
- ECPF params
- end-to-end metrics
- detector diagnostic metrics

## 最小候選執行清單

如果 runtime 緊，先從這六組開始：

```text
C1 dual_adwin error/error ht
C2 adwin warning + seqdrift2 drift error/error ht
C3 seqdrift2 warning + adwin drift error/error ht
C4 dual_seqdrift2 error/error ht
C5 meta_ecpf_hcdt ht/hf standard
C6 uq_warning hf with mi_like, vote_disagreement, predictive_entropy, variance_eu
```

如果 `C6` 表現有潛力，再跑 pure-UQ ablations：

```text
adwin/adwin uq_entropy/uq_entropy hf
adwin/adwin uq_vote/uq_vote hf
adwin/seqdrift2 uq_mi/uq_mi hf
seqdrift2/seqdrift2 uq_vote/uq_vote hf
```

## 最後要回答的問題

最終報告應明確回答：

1. Best overall ECPF config 是哪一組？
2. Best low-runtime config 是哪一組？
3. Best high-recall config 是哪一組？
4. SeqDrift2 應該用在 warning、confirmation、兩者都用，還是排除？
5. UQ 應該是 warning-only、confirmation-only、兩者都用，還是排除？
6. 哪一種 UQ mode 最穩定？
7. 失敗配置是 detector behavior 的問題，還是 ECPF adaptation behavior 的問題？

