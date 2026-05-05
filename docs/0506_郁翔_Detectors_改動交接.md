# 0506 郁翔 Detectors 改動交接

這份文件整理目前我在架構圖中「綠色區塊」負責的 Detectors / drift trigger 部分做了哪些改動，以及這些改動會怎麼影響其他人的模組。

## 我負責的範圍

圖中的綠色區塊主要包含：

- `Sudden Drift Detector`
- `Gradual Drift Detector`
- `Warning buffer open`
- `Drift Confirmed?`
- 與 ECPF warning buffer / model pool 的觸發銜接

也就是說，我主要處理「什麼時候開 warning buffer」以及「什麼時候確認 drift，讓 ECPF 去做 expert comparison」。

## 這次主要改動

### 1. 保留原本 Dynamic Weighted ECPF Detector

原本的 DWM 路線保留在：

```text
detectors/meta_ecpf/dynamic_weighted.py
detectors/meta/dynamic_weighted.py
```

它仍然可以透過：

```bash
--signal-mode meta_ecpf_dwm
```

來測試。

這條路線目前是：

```text
UQ / ErrorTrend proxy warning
-> atom detectors weighted vote
-> ECPF drift handling
```

但這條路線我現在不把它當成最終答案，原因如下。

#### 為什麼原本 Dynamic Weighted Voting 不理想

1. 它把 proxy signal 和 atom detector 混在一起做單一加權決策，容易變成共識瓶頸。
1. UQ / ErrorTrend 本來就不是 ground truth，如果拿來獎懲 atom detector，邏輯上會有點像用 noisy teacher 評分 noisy student。
1. fast detector 和 gradual detector 放在同一個 pool 裡，會出現稀釋問題。某些 detector 明明有抓到漂移，但被其他沒響的 detector 壓掉。
1. 如果門檻太高，會太保守；如果門檻太低，又會過度敏感。這讓權重機制很容易兩面不討好。

所以我把它保留下來，但不把它當成唯一的主路線。

### 2. 新增 Hierarchical Parallel ECPF Detector

新增實驗 detector：

```text
detectors/meta_ecpf/hierarchical_parallel.py
```

對應的 signal mode：

```bash
--signal-mode meta_ecpf_hier_parallel
```

這不是取代原本 DWM，而是新增一條實驗路線，方便比較。

#### 為什麼要新增 hierarchical parallel

我想把「開 warning」和「confirm drift」拆開，不要全部綁在一個 weighted vote 裡面。

比較像這樣：

```text
Step 1. UQ + ErrorTrend 同時成立
        -> open warning buffer

Step 2. warning buffer active 期間
        -> atom detectors 持續看 error stream

Step 3. atom confirmation 夠強
        -> confirmed drift

Step 4. ECPF 用 warning buffer 做 expert comparison

Step 5. drift handled 後 reset transient state + cooldown
```

這樣的好處是：

1. proxy 只負責開 warning，不負責評分 atom detector。
1. atom detector 負責 confirm，角色比較清楚。
1. warning buffer 跟 expert comparison 的資料來源比較一致。
1. 之後如果要換更好的 confirmation path，也比較好換。

### 3. 新增三個 runner 的測試入口

現在以下三個檔案都可以跑新的 hierarchical parallel detector：

```text
run_ecpf_recurring.py
run_ecpf_recurring_batch.py
run_ecpf_uq_experiment.py
```

使用方式如下。

單一資料集：

```bash
python3 run_ecpf_recurring.py \
  --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
  --signal-mode meta_ecpf_hier_parallel \
  --uq-mode mi_like \
  --max-steps 20000
```

批次 recurring drift：

```bash
python3 run_ecpf_recurring_batch.py \
  --signal-mode meta_ecpf_hier_parallel \
  --uq-mode mi_like \
  --print-events \
  --max-steps 20000
```

UQ experiment：

```bash
python3 run_ecpf_uq_experiment.py \
  --settings F_hier_parallel \
  --max-steps 20000 \
  --print-events
```

### 4. 新增 runbook

新增說明文件：

```text
docs/HIERARCHICAL_PARALLEL_ECPF_RUNBOOK.md
```

裡面有更詳細的流程、測試方法、診斷欄位與目前風險。

## Hierarchical Parallel 的設計邏輯

原本 Dynamic Weighted Voting 把 sudden / gradual detectors 放在同一個 weighted pool 裡面，容易產生「共識瓶頸」：

```text
ADWIN 或 DDM 看到 sudden drift
但其他 gradual detectors 沒響
-> 總票數被稀釋
-> drift 沒被確認
```

所以新的 hierarchical parallel 設計改成分層：

```text
Step 1. UQ + ErrorTrend 同時成立
        -> open warning buffer

Step 2. warning buffer active 期間
        -> atom detectors 持續看 error stream

Step 3. gradual-path atom vote >= threshold
        且 warning age >= minimum confirmation age
        -> confirmed drift

Step 4. ECPF 用 warning buffer 做 expert comparison

Step 5. drift handled 後
        -> reset atom/proxy transient state
        -> close warning buffer
        -> enter cooldown
```

目前 fast path / gradual path 分工如下：

```text
Fast path: ADWIN, DDM
Gradual confirmation path: HDDM_A, PageHinkley
```

目前版本中 fast path 主要保留為診斷欄位，真正 confirm 使用 gradual path。

## 很重要的設計決定

目前 proxy 不會 punish / reward atom detector。

也就是：

```text
UQ / ErrorTrend 不是 ground truth
所以不能拿來幫 ADWIN、DDM、PageHinkley 打考績
```

proxy 只負責開 warning 狀態，不負責調整 atom detector 權重。

這是為了避免之前提到的問題：

```text
用 noisy proxy 當老師
去處罰可能正確的 atom detector
```

這一點我希望其他人看文件時特別注意，因為這也是 hierarchical parallel 和原本 DWM 最大的差別之一。

## 對其他人的影響

### 對崇耘 UQ 模組的影響

新的 detector 會使用 UQ signal 來開 warning。

如果 model 是 `hf`，會使用 forest 的 per-tree probability matrix 來算 UQ。

如果沒有 `proba_matrix`，目前有 fallback，但實驗上要注意：

```text
沒有 proba_matrix 時，就不是真正的 MI-like UQ
```

所以如果要比較 UQ 方法，建議使用：

```text
model_type = hf
```

### 對俊諺 / 芊寧 ECPF model pool 的影響

Detectors 只決定何時：

```text
open warning buffer
confirm drift
```

一旦 confirm drift，後面仍然是 ECPF 原本流程：

```text
warning buffer
-> compare current / restored / new model
-> choose winner
-> update model pool
```

所以我的改動不直接改 model pool 的比較邏輯，但會影響 ECPF 收到的 warning buffer 品質。

如果 warning 太早開，buffer 會太長。

如果 confirm 太晚，ECPF comparison 可能混到太多不同概念的資料。

如果 buffer 太短，new model / restored model 的比較會不穩。

### 對聖家 Offline Evaluation 的影響

新的 signal mode 會改變 detector event 的時間與數量。

評估時需要注意：

```text
event timestamp = warning buffer start time
不是一定等於 drift confirmation time
```

如果要更精準分析，建議之後在 event details 中同時記錄：

```text
warning_start_t
confirmation_t
buffer_len
fast_path_score
gradual_path_score
```

目前 `meta_info` 裡已經有部分診斷欄位：

```text
score_ratio
fast_path_score
gradual_path_score
gradual_confirm_threshold
strategy_used
```

## Baseline 的位置

我目前認為 `dual adwin` 可以當成新的 baseline。

它的優點是：

1. 結構比較單純。
1. warning / drift 都是從 error stream 出來，語意很一致。
1. 跟 ECPF 的銜接也比較直接。
1. 在 recurring batch 裡通常比較容易得到穩定的 reuse 指標。

所以比較上可以這樣看：

```text
dual adwin = 簡單、穩定的 baseline
hierarchical parallel = 我們正在探索的新方法
original DWM = 保留作為對照，但不是我現在最推薦的版本
```

## 目前測試觀察

之前原始 DWM 曾出現：

```text
pool = 1.0
reuse_precision = NaN
```

代表根本沒有進入 ECPF drift handling，所以沒有 reuse 的機會。

狀態機版本跑起來後，已經可以讓 ECPF 產生 event、pool 成長，也會進入 reuse decision。

但目前仍然是實驗中的 detector，還要繼續看 false warning、reuse precision、buffer 長度是不是穩定。

## 後續可能方向

我之後可能會再研究 `paired learner`。

如果之後真的往這條線走，我比較想把它當成另一種 model-level baseline，跟現在這條 detector-level hierarchy 分開看：

```text
detector layer:
  hierarchical parallel / dual adwin / original DWM

model layer:
  paired learner / model pool / restored vs new expert comparison
```

這樣比較不會把「偵測漂移」和「怎麼換模型」混成同一件事。

但目前還不是最終版，主要風險是：

- false warning rate 還需要調
- reuse precision 可能偏低
- warning buffer 長度需要繼續控制
- fast path 目前偏診斷用途，還沒有直接觸發 confirm

## 建議大家測試時使用的指令

### 原本 DWM

```bash
python3 run_ecpf_uq_experiment.py \
  --settings E_meta_ecpf_dwm \
  --max-steps 20000 \
  --print-events
```

### 新的 Hierarchical Parallel

```bash
python3 run_ecpf_uq_experiment.py \
  --settings F_hier_parallel \
  --max-steps 20000 \
  --print-events
```

### 和 Dual ADWIN baseline 比較

```bash
python3 run_ecpf_uq_experiment.py \
  --settings A_baseline_ht_error B_hf_error_direct F_hier_parallel \
  --max-steps 20000 \
  --print-events
```

## 總結

這次改動的核心不是要宣稱 hierarchical parallel 一定比 Dual ADWIN 好，而是把綠色 Detectors 區塊拆得更清楚：

```text
proxy 負責 warning
atom detectors 負責 confirmation
ECPF 負責 model reuse / expert comparison
offline evaluation 負責判斷 detector quality
```

這樣比較容易 debug，也比較不會讓 UQ / ErrorTrend 這種 proxy signal 被誤用成 ground truth。
