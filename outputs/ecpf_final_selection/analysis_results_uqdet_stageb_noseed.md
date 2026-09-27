# ECPF UQ × Detector 實驗分析：ADWIN vs SeqDrift2 比較

## 文件對應

| 指標 | 本次實驗輸出 |
|------|--------------|
| Summary | `outputs/ecpf_final_selection/uqdet_stageb_noseed_summary.csv` |
| Per-file details | `outputs/ecpf_final_selection/uqdet_stageb_noseed_details.csv` |
| Per-config outputs | `outputs/ecpf_final_selection/uqdet_stageb_noseed/<config_id>/` |
| Runner | `scripts/run_ecpf_final_selection.py --stage uqdet_stageb` |

本次實驗排除 SEED，只比較 4 種 UQ warning signal 搭配 2 種 detector family：

```text
mi_like × ADWIN / SeqDrift2
vote_disagreement × ADWIN / SeqDrift2
predictive_entropy × ADWIN / SeqDrift2
variance_eu × ADWIN / SeqDrift2
```

共同設定：

```text
model_type = hf
warning_signal = UQ signal
drift_signal = error
warning_detector = ADWIN or SeqDrift2
drift_detector = same detector family
datasets = data/recurring_drift/recurring_sud_sea100k_g00..g09.csv
max_steps = 50000
warm_start = 200
```

---

## 1. 總覽：Summary 指標比較

### Accuracy（Prequential Accuracy）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | **0.9450** | 0.9440 | +0.0010 | ADWIN |
| `vote_disagreement` | **0.9442** | 0.9438 | +0.0005 | ADWIN |
| `predictive_entropy` | **0.9511** | 0.9490 | +0.0022 | ADWIN |
| `variance_eu` | 0.9434 | **0.9450** | -0.0015 | SeqDrift2 |

> [!IMPORTANT]
> **`predictive_entropy × ADWIN` 是本次 recurring screening 的最高 accuracy 組合**。整體來看 ADWIN 在 3/4 個 UQ signal 上 accuracy 較高，但 `vote_adwin` 與 `variance_adwin` 被標記為 `silent_detector`，解讀時不能只看 accuracy。

---

### Detected-to-Actual Ratio（偵測數與實際 drift 數比例，越接近 1 越好）

| UQ Signal | ADWIN | SeqDrift2 | 較接近 1 的設定 |
|-----------|------:|----------:|----------------|
| `mi_like` | **0.425** | 2.400 | ADWIN |
| `vote_disagreement` | **0.125** | 2.125 | ADWIN，但偏 silent |
| `predictive_entropy` | **0.650** | 2.350 | ADWIN |
| `variance_eu` | **0.150** | 2.125 | ADWIN，但偏 silent |

> [!NOTE]
> `silent_detector` 的規則是 `detected_to_actual_ratio < 0.3`。這不代表 end-to-end 一定差，而是代表該配置偵測覆蓋率不足，不能拿來主張「detector 抓 drift 抓得準」。若 accuracy 高、false adaptation 低，它仍可視為 conservative / low-adaptation baseline。

---

### Mean Recovery Delay（越低越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | 511.4 | **404.9** | +106.5 | SeqDrift2 |
| `vote_disagreement` | 406.9 | **342.2** | +64.7 | SeqDrift2 |
| `predictive_entropy` | 370.1 | **362.7** | +7.4 | SeqDrift2 |
| `variance_eu` | **357.0** | 371.3 | -14.3 | ADWIN |

> [!TIP]
> SeqDrift2 組普遍 recovery delay 較短，代表它比較積極觸發 ECPF adaptation。但這個優勢伴隨更高的 detected ratio 和 false event count，因此不能單獨當作 final ranking 依據。

---

### False Event Count（越低越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | **1.2** | 6.5 | -5.3 | ADWIN |
| `vote_disagreement` | **0.3** | 5.3 | -5.0 | ADWIN |
| `predictive_entropy` | **1.6** | 5.7 | -4.1 | ADWIN |
| `variance_eu` | **0.4** | 5.3 | -4.9 | ADWIN |

> [!IMPORTANT]
> ADWIN 的最大優勢是 false event 少很多。SeqDrift2 的問題不是「抓不到」，而是比較容易多抓，可能讓 ECPF 進入較頻繁的 adaptation。

---

### Reuse Best Beats Current Rate（越高越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | 0.083 | **0.367** | -0.284 | SeqDrift2 |
| `vote_disagreement` | 0.000 | **0.296** | -0.296 | SeqDrift2 |
| `predictive_entropy` | 0.058 | **0.301** | -0.243 | SeqDrift2 |
| `variance_eu` | 0.000 | **0.287** | -0.287 | SeqDrift2 |

> [!NOTE]
> SeqDrift2 因為觸發事件較多，ECPF 有更多機會檢查 pool model 是否勝過 current model，因此 reuse 指標較高。但這不保證 final accuracy 較高；本次結果中 SeqDrift2 的 reuse 較活躍，卻沒有贏過 `predictive_entropy × ADWIN` 的整體 accuracy。

---

### Runtime（秒，越低越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | 71.1 | **63.8** | +7.4 | SeqDrift2 |
| `vote_disagreement` | **60.0** | 62.8 | -2.8 | ADWIN |
| `predictive_entropy` | 76.4 | **61.3** | +15.1 | SeqDrift2 |
| `variance_eu` | **61.4** | 65.1 | -3.6 | ADWIN |

> Runtime 差異存在，但不是本次主要瓶頸。這次更重要的是 accuracy、detected ratio、false event count 和 recovery delay 的 trade-off。

---

## 2. 關鍵發現

### ADWIN 的優勢

```text
Accuracy: 3/4 個 UQ signal 勝出
False event count: 4/4 勝出
Detected ratio: 比 SeqDrift2 更接近 1，但部分設定過於保守
```

ADWIN 比較像「穩定 confirmation」路線。它不容易大量觸發 ECPF，因此 false event 少；但 `vote_adwin` 與 `variance_adwin` 已經接近 low-adaptation baseline，而不是強 detector。

### SeqDrift2 的優勢

```text
Recovery delay: 3/4 個 UQ signal 較低
Reuse activity: 4/4 個 UQ signal 較高
Detected events: 明顯更敏感
```

SeqDrift2 比較像「積極 adaptation」路線。它能讓 ECPF 更常啟動 reuse / adaptation，但 recurring screening 上 false events 偏多，accuracy 沒有超過最佳 ADWIN 組。

### 最穩定的 UQ 指標

```text
predictive_entropy
```

`predictive_entropy` 在 ADWIN 和 SeqDrift2 兩邊都表現最好：

| Config | Accuracy | Detected Ratio | Recovery Delay | False Events |
|--------|---------:|---------------:|---------------:|-------------:|
| `uq_entropy_adwin` | **0.9511** | 0.65 | 370.1 | **1.6** |
| `uq_entropy_seqdrift2` | 0.9490 | 2.35 | **362.7** | 5.7 |

> [!IMPORTANT]
> 如果只選一組進 final validation，優先選 `uq_entropy_adwin`。如果要保留一組 SeqDrift2 對照，選 `uq_entropy_seqdrift2`。

---

## 3. 各設定深入分析

### `uq_entropy_adwin`：目前最佳整體候選

| 指標 | 數值 | 解讀 |
|------|-----:|------|
| Accuracy | **0.9511** | 本次最高 |
| Detected-to-Actual Ratio | 0.65 | 偵測偏保守，但未 silent |
| Recovery Delay | 370.1 | 中等偏好 |
| False Event Count | **1.6** | 非常低 |
| Reuse Best Beats Current Rate | 0.058 | reuse 活動少 |
| Runtime | 76.4s | 稍慢，但可接受 |

> [!TIP]
> 這組不像 SeqDrift2 那麼積極，但 accuracy 與 false event 的平衡最好。若最終目標是 ECPF end-to-end performance，而不是 detector recall，這是目前最乾淨的候選。

### `uq_entropy_seqdrift2`：SeqDrift2 family 內最佳

| 指標 | 數值 | 解讀 |
|------|-----:|------|
| Accuracy | **0.9490** | SeqDrift2 組最高 |
| Detected-to-Actual Ratio | 2.35 | 偏敏感 |
| Recovery Delay | 362.7 | 比 entropy+ADWIN 略快 |
| False Event Count | 5.7 | 明顯偏高 |
| Reuse Best Beats Current Rate | 0.301 | reuse 活動高 |
| Runtime | 61.3s | 比 entropy+ADWIN 快 |

> [!NOTE]
> 這組適合用來檢驗「更積極觸發 adaptation 是否能在其他 drift type 上追回 accuracy」。在 recurring screening 裡，它沒有贏過 `uq_entropy_adwin`，但仍是 SeqDrift2 路線中最值得保留的 finalist。

### `uq_mi_like_adwin`：保守但 recovery 偏慢

| 指標 | 數值 | 解讀 |
|------|-----:|------|
| Accuracy | 0.9450 | 中段 |
| Detected-to-Actual Ratio | 0.425 | 偵測偏少 |
| Recovery Delay | 511.4 | 本次偏慢 |
| False Event Count | 1.2 | 低 |
| Reuse Best Beats Current Rate | 0.083 | 低 |

`mi_like × ADWIN` 的 false event 很少，但 recovery delay 偏高，表示它即使少觸發，也沒有換到更好的整體 accuracy。

### SeqDrift2 UQ variants：敏感但 false events 偏高

| Config | Accuracy | Detected Ratio | Recovery Delay | False Events |
|--------|---------:|---------------:|---------------:|-------------:|
| `uq_entropy_seqdrift2` | **0.9490** | 2.35 | 362.7 | 5.7 |
| `uq_variance_seqdrift2` | 0.9450 | 2.125 | 371.3 | 5.3 |
| `uq_mi_like_seqdrift2` | 0.9440 | 2.40 | 404.9 | 6.5 |
| `uq_vote_seqdrift2` | 0.9438 | 2.125 | **342.2** | 5.3 |

SeqDrift2 的共同特徵是「事件多、reuse 多、false event 多」。`vote_seqdrift2` recovery delay 最短，但 accuracy 最低；`entropy_seqdrift2` 是這組裡最平衡的。

### Silent ADWIN variants：不能直接判死刑，但不是第一候選

| Config | Accuracy | Detected Ratio | Recovery Delay | False Events | Hard Reject |
|--------|---------:|---------------:|---------------:|-------------:|-------------|
| `uq_vote_adwin` | 0.9442 | 0.125 | 406.9 | 0.3 | `silent_detector` |
| `uq_variance_adwin` | 0.9434 | 0.150 | 357.0 | 0.4 | `silent_detector` |

> [!WARNING]
> `silent_detector` 不代表一定不好。它代表這組幾乎不觸發 ECPF，因此不能用 detector recall 的角度說它成功。若它的 accuracy 很高，可以視為 conservative baseline；但本次它們沒有超過 `uq_entropy_adwin`，所以不建議作為主候選。

---

## 4. 結論與建議

### 本次 recurring screening 的推薦排序

| 優先順序 | 推薦配置 | 理由 |
|----------|----------|------|
| 1 | `uq_entropy_adwin` | 最高 accuracy、false event 少、未 silent |
| 2 | `uq_entropy_seqdrift2` | SeqDrift2 family 最佳，適合作積極 adaptation 對照 |
| 3 | `uq_mi_like_adwin` | 保守、false event 低，但 recovery 偏慢 |
| 4 | `uq_variance_seqdrift2` | SeqDrift2 次佳，但 false event 偏高 |

### 不建議優先投入的配置

```text
uq_vote_adwin
uq_variance_adwin
```

這兩組是 conservative / silent 類型，可以保留作對照，但目前沒有足夠證據支持它們成為主配置。

```text
uq_mi_like_seqdrift2
uq_vote_seqdrift2
```

這兩組 SeqDrift2 夠敏感，但 false events 偏高且 accuracy 沒有優勢。除非後續研究目標是「最快 recovery」或「高 recall detector」，否則不應優先進 final selection。

### 下一步建議

Final validation 不需要把 8 組全部帶進去。建議只保留：

```text
uq_entropy_adwin
uq_entropy_seqdrift2
```

再與既有 baseline / candidate 比較：

```text
dual_adwin error/error
adwin warning + seqdrift2 drift error/error
seqdrift2 warning + adwin drift error/error
meta_ecpf_hcdt
oracle_60
```

> [!WARNING]
> 以上分析只基於 `recurring_sud_sea100k_g00..g09` 的 50k-row screening。它可以用來篩選 finalist，但不能直接當作最終結論。最後仍需要在 sudden、gradual、incremental drift 上做 end-to-end validation。
