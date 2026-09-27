# ECPF UQ 指標比較報告：EMA+ADWIN、HCDT、DWM

## 實驗輸出來源

| 類別 | 路徑 |
|------|------|
| 舊 EMA+ADWIN / HCDT 主結果 | `outputs/variance_eu_full_compare/` |
| 新 DWM + MI | `outputs/dwm_norm_mi/` |
| 新 DWM + vote disagreement | `outputs/dwm_norm_vote/` |
| 新 DWM + predictive entropy | `outputs/dwm_norm_entropy/` |
| 新 DWM + normalized variance_eu | `outputs/dwm_norm_var/` |

本次比較資料集為 `recurring_sud_sea100k_g00.csv` 到 `g09.csv`，總 ground-truth drift 數為 82。Detection delay 的 tolerance 為 500；沒有在 `[GT, GT+500]` 內 match 到 detection 的 ground-truth drift 會以 500 計入平均 delay。

---

## 1. 實驗流程與 Detector 標準

### EMA+ADWIN UQ-warning 組：C / D1 / D2 / D3

流程是 HF 每筆樣本輸出 per-tree probability matrix，再抽成單一 UQ scalar。UQ scalar 先經 EMA smoothing，接著餵給 ADWIN 作 warning。

| 層級 | 輸入訊號 | 判定方式 | 是否吃 label / err |
|------|----------|----------|--------------------|
| Warning | `mi_like` / `vote_disagreement` / `predictive_entropy` / `variance_eu` | UQ scalar -> EMA alpha=0.1 -> ADWIN delta=0.01, grace=50 | 不吃 err，只吃 HF per-tree proba |
| Drift confirmation | 0/1 error | error ADWIN，delta=0.05，delta_w=0.1，min instances=30 | 吃 err |

UQ-warning 組的重點是：warning 由 UQ 開，error ADWIN 只負責 drift confirmation。也就是說，這不是純 UQ detector；它是「UQ warning + error confirmation」。

### HCDT 組：H

HCDT 全程使用 error stream，不吃 UQ。

| 層級 | 輸入訊號 | 判定方式 | 是否吃 label / err |
|------|----------|----------|--------------------|
| Detection / warning | 0/1 error | HDDM-A，min samples=30，delta=0.005，lambda=0.98，score threshold=0.07 | 吃 err |
| Validation / drift | 0/1 error | RDDM，warning level=1.75，drift level=2.5，max warning length=400 | 吃 err |

HCDT 需要先有 detection layer warning，再等 RDDM validation drift，且 warning age 至少 45。Timeout 為 1000，cooldown 為 1500。

### 新 DWM 組：E(MI) / E(vote) / E(entropy) / E(varEU)

DWM 是兩階段：

| 層級 | 輸入訊號 | 判定方式 | 是否吃 label / err |
|------|----------|----------|--------------------|
| Stage 1 proxy warning | UQWarningIndicator + KSWINFeatureIndicator | proxy policy=`any`，但需 120 筆內累積至少 2 次 proxy warning | UQ 不吃 err；KSWIN 只吃 features |
| Stage 2 drift confirmation | 0/1 error | ADWIN + HDDM-W voting，weighted score >= 0.5，min confirmation age=60 | 吃 err |

這代表 DWM 不是純 UQ detector。它的 warning gate 由 UQ / feature shift 打開，但真正 drift confirmation 還是 error-based ADWIN + HDDM-W。

---

## 2. Summary 總表

| Setting | GT Drift | Detected | Accuracy | Delay | False Warning | Reuse Precision | Avg Pool | Runtime(s) |
|---------|---------:|---------:|---------:|------:|--------------:|----------------:|---------:|-----------:|
| C - HF+UQ(MI)+EMA/ADWIN | 82 | 46 | 0.9496 | 480.8 | 0.755 | 0.676 | 2.36 | 168.4 |
| D1 - HF+UQ(vote)+EMA/ADWIN | 82 | 28 | 0.9480 | 488.5 | 0.679 | 0.626 | 2.30 | 240.3 |
| D2 - HF+UQ(entropy)+EMA/ADWIN | 82 | 66 | 0.9507 | 473.5 | 0.632 | 0.873 | 3.09 | 162.3 |
| D3 - HF+UQ(varEU raw)+EMA/ADWIN | 82 | 11 | 0.9438 | 500.0 | 0.480 | 0.760 | 1.36 | 287.6 |
| E(MI) - HF+UQ(MI)+DWM | 82 | 37 | 0.9316 | 499.0 | 0.769 | 0.594 | 2.93 | 312.4 |
| E(vote) - HF+UQ(vote)+DWM | 82 | 30 | 0.9341 | 499.0 | 0.775 | 0.403 | 2.55 | 256.7 |
| E(entropy) - HF+UQ(entropy)+DWM | 82 | 35 | 0.9284 | 499.2 | 0.780 | 0.367 | 2.75 | 275.3 |
| E(varEU) - HF+UQ(varEU norm)+DWM | 82 | 36 | 0.9343 | 490.2 | 0.849 | 0.517 | 2.85 | 266.4 |
| H - HF+HCDT | 82 | 74 | **0.9624** | **277.8** | **0.368** | 0.644 | 3.01 | 165.0 |

HCDT 仍然是這批結果裡最強的 baseline：accuracy 最高、delay 最短、false warning rate 最低，而且 detected count 達到 `74 / 82`。

---

## 3. Accuracy 排名

| Rank | Setting | Accuracy | 備註 |
|------|---------|---------:|------|
| 1 | H - HF+HCDT | **0.9624** | 整體最佳 |
| 2 | D2 - HF+UQ(entropy)+EMA/ADWIN | 0.9507 | UQ-warning 組最佳 |
| 3 | C - HF+UQ(MI)+EMA/ADWIN | 0.9496 | 接近 entropy |
| 4 | D1 - HF+UQ(vote)+EMA/ADWIN | 0.9480 | 穩定但 detection 較少 |
| 5 | D3 - HF+UQ(varEU raw)+EMA/ADWIN | 0.9438 | 舊 raw varEU，不公平比較 |
| 6 | E(varEU) - HF+UQ(varEU norm)+DWM | 0.9343 | DWM 組最高 |
| 7 | E(vote) - HF+UQ(vote)+DWM | 0.9341 | 幾乎等同 DWM-varEU |
| 8 | E(MI) - HF+UQ(MI)+DWM | 0.9316 | DWM-MI 未改善 |
| 9 | E(entropy) - HF+UQ(entropy)+DWM | 0.9284 | DWM 組最低 |

新 DWM 補跑後，DWM 內部最佳是 normalized varEU，但它仍然明顯落後 HCDT，也落後原本的 EMA+ADWIN UQ-warning 組。

---

## 4. Detection Delay 排名

| Setting | Delay | 備註 |
|---------|------:|------|
| H - HF+HCDT | **277.8** | 唯一明顯早偵測 |
| D2 - HF+UQ(entropy)+EMA/ADWIN | 473.5 | UQ-warning 組最佳 |
| C - HF+UQ(MI)+EMA/ADWIN | 480.8 | 接近 entropy |
| D1 - HF+UQ(vote)+EMA/ADWIN | 488.5 | 偏晚 |
| E(varEU) - HF+UQ(varEU norm)+DWM | 490.2 | DWM 組最佳，但仍偏晚 |
| E(MI) - HF+UQ(MI)+DWM | 499.0 | 幾乎 miss |
| E(vote) - HF+UQ(vote)+DWM | 499.0 | 幾乎 miss |
| E(entropy) - HF+UQ(entropy)+DWM | 499.2 | 幾乎 miss |
| D3 - HF+UQ(varEU raw)+EMA/ADWIN | 500.0 | 幾乎全 miss |

`500` 附近代表大多數 ground-truth drift 沒有在 tolerance window 內被及時 match 到。DWM 的問題不是沒有 event，而是 warning 到 confirmation 的 buffer 拉太長，導致有效 delay 仍然接近 miss。

---

## 5. False Warning Rate 排名

| Setting | False Warning Rate | 備註 |
|---------|-------------------:|------|
| H - HF+HCDT | **0.368** | 最乾淨 |
| D3 - HF+UQ(varEU raw)+EMA/ADWIN | 0.480 | 但 detected 只有 11，不代表好 |
| D2 - HF+UQ(entropy)+EMA/ADWIN | 0.632 | UQ-warning 組較佳 |
| D1 - HF+UQ(vote)+EMA/ADWIN | 0.679 | 中等 |
| C - HF+UQ(MI)+EMA/ADWIN | 0.755 | 偏高 |
| E(MI) - HF+UQ(MI)+DWM | 0.769 | 偏高 |
| E(vote) - HF+UQ(vote)+DWM | 0.775 | 偏高 |
| E(entropy) - HF+UQ(entropy)+DWM | 0.780 | 偏高 |
| E(varEU) - HF+UQ(varEU norm)+DWM | 0.849 | DWM 組最高 |

DWM-varEU 的 accuracy / delay 是 DWM 裡最好的，但 false warning rate 也最高。這代表 normalized varEU 有把訊號拉起來，但目前 DWM confirmation gate 還沒把 false alarms 壓住。

---

## 6. Reuse Precision 排名

| Setting | Reuse Precision | 備註 |
|---------|----------------:|------|
| D2 - HF+UQ(entropy)+EMA/ADWIN | **0.873** | ECPF reuse 最穩 |
| D3 - HF+UQ(varEU raw)+EMA/ADWIN | 0.760 | detected 太少，解讀要保守 |
| C - HF+UQ(MI)+EMA/ADWIN | 0.676 | 中等 |
| H - HF+HCDT | 0.644 | timing / false warning 更好，但 reuse precision 不是最高 |
| D1 - HF+UQ(vote)+EMA/ADWIN | 0.626 | 中等 |
| E(MI) - HF+UQ(MI)+DWM | 0.594 | DWM 中較好 |
| E(varEU) - HF+UQ(varEU norm)+DWM | 0.517 | DWM 中第二 |
| E(vote) - HF+UQ(vote)+DWM | 0.403 | 偏低 |
| E(entropy) - HF+UQ(entropy)+DWM | 0.367 | 最低 |

如果只看 ECPF reuse，predictive entropy 的 EMA+ADWIN 組仍然最漂亮。HCDT 的優勢主要在更準、更快、更少 false warning。

---

## 7. Event Buffer 診斷

| Setting | Events | Mean Buffer | Median Buffer | Min | Max | UQ Extracted Mean | UQ Raw Mean | UQ Smooth Mean |
|---------|-------:|------------:|--------------:|----:|----:|------------------:|------------:|---------------:|
| C - HF+UQ(MI)+EMA/ADWIN | 46 | 423.6 | 401.0 | 25 | 961 | - | 0.235 | 0.220 |
| D1 - HF+UQ(vote)+EMA/ADWIN | 28 | 463.0 | 545.0 | 33 | 993 | - | 0.129 | 0.143 |
| D2 - HF+UQ(entropy)+EMA/ADWIN | 66 | 473.5 | 453.0 | 9 | 929 | - | 0.634 | 0.657 |
| D3 - HF+UQ(varEU raw)+EMA/ADWIN | 11 | 427.9 | 497.0 | 65 | 905 | - | 0.094 | 0.087 |
| E(MI) - HF+UQ(MI)+DWM | 37 | **11036.8** | **10031.0** | 209 | 32864 | 0.2625 | 0.2625 | 0.2135 |
| E(vote) - HF+UQ(vote)+DWM | 30 | **9735.4** | **8935.0** | 395 | 32864 | 0.2600 | 0.2600 | 0.1559 |
| E(entropy) - HF+UQ(entropy)+DWM | 35 | **11049.2** | **10201.0** | 76 | 33276 | 0.8210 | 0.8210 | 0.7083 |
| E(varEU) - HF+UQ(varEU norm)+DWM | 36 | **13708.1** | **11836.0** | 305 | **73007** | 0.1235 | 0.2471 | 0.1905 |
| H - HF+HCDT | 74 | **53.7** | **46.0** | 46 | 337 | - | - | - |

DWM 的最大問題非常明顯：warning buffer 比 EMA+ADWIN UQ-warning 大約多一個數量級以上。這表示 Stage 1 proxy warning 很早打開，但 Stage 2 error confirmation 常常拖很久才過，導致 buffer 膨脹、delay 接近 500，也拖累 ECPF reuse。

HCDT 則相反，median buffer 只有 46，因此它比較像是「短 warning + 快 confirmation」。

---

## 8. Per-file Detected Count

| File | MI EMA/ADWIN | Vote EMA/ADWIN | Entropy EMA/ADWIN | varEU raw EMA/ADWIN | DWM-MI | DWM-Vote | DWM-Entropy | DWM-varEU norm | HCDT |
|------|-------------:|---------------:|------------------:|--------------------:|-------:|---------:|------------:|---------------:|-----:|
| g00 | 3 | 2 | 5 | 1 | 0 | 0 | 0 | 2 | 4 |
| g01 | 7 | 1 | 9 | 0 | 5 | 3 | 3 | 5 | 7 |
| g02 | 1 | 2 | 5 | 0 | 4 | 1 | 3 | 4 | 7 |
| g03 | 7 | 3 | 10 | 1 | 1 | 1 | 1 | 1 | 5 |
| g04 | 4 | 5 | 5 | 1 | 3 | 2 | 3 | 3 | 7 |
| g05 | 3 | 3 | 4 | 3 | 9 | 4 | 10 | 5 | 11 |
| g06 | 6 | 7 | 9 | 0 | 4 | 4 | 8 | 9 | 11 |
| g07 | 4 | 0 | 6 | 0 | 8 | 6 | 4 | 4 | 8 |
| g08 | 3 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 1 |
| g09 | 8 | 4 | 9 | 5 | 3 | 9 | 3 | 3 | 13 |

HCDT 在多數檔案上的 detection count 最接近 ground truth。DWM 在某些檔案會爆出很多 events，例如 DWM-entropy 的 g05、DWM-varEU 的 g06，但不一定轉成更好的 delay 或 false warning。

---

