# ECPF UQ × Detector 實驗分析：ADWIN 0.05/0.02 vs SeqDrift2 0.550/0.553

## 文件對應

| 指標 | 新 delta 實驗輸出 |
|------|-------------------|
| Summary | `outputs/ecpf_final_selection/uqdet_stageb_noseed_adwin005_002_seq0550_0553_summary.csv` |
| Per-file details | `outputs/ecpf_final_selection/uqdet_stageb_noseed_adwin005_002_seq0550_0553_details.csv` |
| Per-config outputs | `outputs/ecpf_final_selection/uqdet_stageb_noseed_adwin005_002_seq0550_0553/<config_id>/` |
| 舊 delta 報告 | `outputs/ecpf_final_selection/analysis_results_uqdet_stageb_noseed.md` |
| 舊 delta summary | `outputs/ecpf_final_selection/uqdet_stageb_noseed_summary.csv` |
| Runner | `scripts/run_ecpf_final_selection.py --stage uqdet_stageb` |

本次實驗排除 SEED，只比較 4 種 UQ warning signal 搭配 2 種 detector family：

```text
mi_like × ADWIN / SeqDrift2
vote_disagreement × ADWIN / SeqDrift2
predictive_entropy × ADWIN / SeqDrift2
variance_eu × ADWIN / SeqDrift2
```

本輪 delta 設定：

```text
ADWIN warning delta = 0.05
ADWIN drift delta   = 0.02

SeqDrift2 warning delta = 0.550
SeqDrift2 drift delta   = 0.553
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

> [!NOTE]
> 本輪已修正 runner 路徑，讓 SeqDrift2 實際吃外部傳入的 `delta`。舊實驗中 SeqDrift2 使用的是內建 role preset；本輪 SeqDrift2 則使用 `detector_delta_w=0.550` 與 `detector_delta=0.553`。

---

## 1. 總覽：Summary 指標比較

### Accuracy（Prequential Accuracy）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | 0.9439 | **0.9511** | -0.0072 | SeqDrift2 |
| `vote_disagreement` | 0.9455 | **0.9503** | -0.0048 | SeqDrift2 |
| `predictive_entropy` | 0.9469 | **0.9532** | -0.0063 | SeqDrift2 |
| `variance_eu` | 0.9453 | **0.9518** | -0.0065 | SeqDrift2 |

> [!IMPORTANT]
> 只看 accuracy，本輪 SeqDrift2 四組全部勝過 ADWIN，最高是 `uq_entropy_seqdrift2`。但這個結論不能單獨使用，因為所有 SeqDrift2 組都同時出現 `event_explosion`。

---

### Detected-to-Actual Ratio（偵測數與實際 drift 數比例，越接近 1 越好）

| UQ Signal | ADWIN | SeqDrift2 | 較接近 1 的設定 |
|-----------|------:|----------:|----------------|
| `mi_like` | **0.300** | 4.625 | ADWIN |
| `vote_disagreement` | **0.125** | 4.550 | ADWIN，但偏 silent |
| `predictive_entropy` | **0.700** | 4.750 | ADWIN |
| `variance_eu` | **0.225** | 4.525 | ADWIN，但偏 silent |

> [!WARNING]
> SeqDrift2 新 delta 讓偵測數膨脹到實際 drift 數的 4.5 倍以上。這已經不是單純「比較敏感」，而是會影響 ECPF 解讀的 event explosion。

---

### Mean Recovery Delay（越低越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | 448.5 | **299.7** | +148.8 | SeqDrift2 |
| `vote_disagreement` | 431.3 | **322.7** | +108.6 | SeqDrift2 |
| `predictive_entropy` | 434.8 | **288.4** | +146.4 | SeqDrift2 |
| `variance_eu` | 375.4 | **286.8** | +88.6 | SeqDrift2 |

> [!TIP]
> SeqDrift2 recovery delay 全面更低，這符合「更敏感、更早觸發 adaptation」的現象。但它是用大量額外 events 換來的，不能直接視為更好的 final ECPF 行為。

---

### False Event Count（越低越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | **0.9** | 14.4 | -13.5 | ADWIN |
| `vote_disagreement` | **0.4** | 14.5 | -14.1 | ADWIN |
| `predictive_entropy` | **2.4** | 14.3 | -11.9 | ADWIN |
| `variance_eu` | **0.7** | 14.0 | -13.3 | ADWIN |

> [!IMPORTANT]
> 本輪最關鍵的反證在 false events：SeqDrift2 雖然 accuracy 較高，但 false event count 大幅升高。若最終目標是可部署 ECPF，而不是單純追求 raw accuracy，這是一個很大的風險。

---

### Reuse Best Beats Current Rate（越高越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | 0.000 | **0.457** | -0.457 | SeqDrift2 |
| `vote_disagreement` | 0.000 | **0.375** | -0.375 | SeqDrift2 |
| `predictive_entropy` | 0.112 | **0.427** | -0.315 | SeqDrift2 |
| `variance_eu` | 0.000 | **0.351** | -0.351 | SeqDrift2 |

> SeqDrift2 觸發更多事件，因此有更多機會讓 pool model 勝過 current model。這表示它確實啟動了更多 reuse 機會，但同時也帶來大量 false events。

---

### Runtime（秒，越低越好）

| UQ Signal | ADWIN | SeqDrift2 | Δ (ADWIN - SeqDrift2) | 勝者 |
|-----------|------:|----------:|----------------------:|------|
| `mi_like` | **60.9** | 63.6 | -2.7 | ADWIN |
| `vote_disagreement` | **60.6** | 66.0 | -5.5 | ADWIN |
| `predictive_entropy` | 75.1 | **60.6** | +14.5 | SeqDrift2 |
| `variance_eu` | 66.3 | **64.6** | +1.8 | SeqDrift2 |

Runtime 不是這輪主要差異。真正的差異是 SeqDrift2 的 detected ratio 與 false events。

---

## 2. 關鍵發現

### SeqDrift2 新 delta 的效果

```text
Accuracy 全面上升
Recovery delay 全面下降
Reuse activity 全面增加
Detected-to-actual ratio 全面爆量
False event count 全面大幅增加
```

SeqDrift2 `0.550 / 0.553` 讓 detector 變得非常敏感。它可以製造比較高的 end-to-end accuracy，但代價是所有 SeqDrift2 組都被標成 `event_explosion`。

### ADWIN 新 delta 的效果

```text
ADWIN warning = 0.05
ADWIN drift = 0.02
```

這組 ADWIN 比上一輪更保守。結果是：

```text
uq_entropy_adwin accuracy 下降
uq_mi_like_adwin detected ratio 降到 0.30
uq_vote_adwin / uq_variance_adwin 仍偏 silent
```

因此 ADWIN 新 delta 沒有明顯改善 recurring screening 的整體表現。

### 最值得注意的 UQ 指標

```text
predictive_entropy
```

`predictive_entropy` 仍然是最穩定的 UQ signal：

| Config | Accuracy | Detected Ratio | Recovery Delay | False Events | Reject |
|--------|---------:|---------------:|---------------:|-------------:|--------|
| `uq_entropy_adwin` | 0.9469 | 0.70 | 434.8 | 2.4 | - |
| `uq_entropy_seqdrift2` | **0.9532** | 4.75 | **288.4** | 14.3 | `event_explosion` |

> [!IMPORTANT]
> 如果要追求「乾淨可部署」，`uq_entropy_adwin` 仍比 SeqDrift2 乾淨；如果要研究「高敏感、高 adaptation」極限，`uq_entropy_seqdrift2` 是這輪最強但風險最高的配置。

---

## 3. 舊 delta vs 新 delta 比較

舊 delta 結果來自：

```text
outputs/ecpf_final_selection/analysis_results_uqdet_stageb_noseed.md
outputs/ecpf_final_selection/uqdet_stageb_noseed_summary.csv
```

### Accuracy 變化

| Config | 舊 Accuracy | 新 Accuracy | Δ |
|--------|------------:|------------:|--:|
| `uq_entropy_adwin` | **0.9511** | 0.9469 | -0.0043 |
| `uq_entropy_seqdrift2` | 0.9490 | **0.9532** | +0.0042 |
| `uq_mi_like_adwin` | **0.9450** | 0.9439 | -0.0011 |
| `uq_mi_like_seqdrift2` | 0.9440 | **0.9511** | +0.0071 |
| `uq_variance_adwin` | 0.9434 | **0.9453** | +0.0019 |
| `uq_variance_seqdrift2` | 0.9450 | **0.9518** | +0.0069 |
| `uq_vote_adwin` | 0.9442 | **0.9455** | +0.0012 |
| `uq_vote_seqdrift2` | 0.9438 | **0.9503** | +0.0065 |

> 新 delta 對 SeqDrift2 的 accuracy 幫助很明顯；對 ADWIN 則混合，且最重要的 `entropy_adwin` 反而變差。

### Detected Ratio 變化

| Config | 舊 Ratio | 新 Ratio | Δ |
|--------|---------:|---------:|--:|
| `uq_entropy_adwin` | 0.650 | 0.700 | +0.050 |
| `uq_entropy_seqdrift2` | 2.350 | 4.750 | +2.400 |
| `uq_mi_like_adwin` | 0.425 | 0.300 | -0.125 |
| `uq_mi_like_seqdrift2` | 2.400 | 4.625 | +2.225 |
| `uq_variance_adwin` | 0.150 | 0.225 | +0.075 |
| `uq_variance_seqdrift2` | 2.125 | 4.525 | +2.400 |
| `uq_vote_adwin` | 0.125 | 0.125 | 0.000 |
| `uq_vote_seqdrift2` | 2.125 | 4.550 | +2.425 |

> [!WARNING]
> 新 delta 讓 SeqDrift2 的 detected ratio 全部增加到 4.5 以上。這就是本輪所有 SeqDrift2 組被標 `event_explosion` 的原因。

### False Event Count 變化

| Config | 舊 False Events | 新 False Events | Δ |
|--------|----------------:|----------------:|--:|
| `uq_entropy_adwin` | 1.6 | 2.4 | +0.8 |
| `uq_entropy_seqdrift2` | 5.7 | 14.3 | +8.6 |
| `uq_mi_like_adwin` | 1.2 | 0.9 | -0.3 |
| `uq_mi_like_seqdrift2` | 6.5 | 14.4 | +7.9 |
| `uq_variance_adwin` | 0.4 | 0.7 | +0.3 |
| `uq_variance_seqdrift2` | 5.3 | 14.0 | +8.7 |
| `uq_vote_adwin` | 0.3 | 0.4 | +0.1 |
| `uq_vote_seqdrift2` | 5.3 | 14.5 | +9.2 |

> SeqDrift2 新 delta 的 false event 增幅非常大，這比 accuracy 提升更需要重視。

### Hard Reject 狀態變化

| Config | 舊 Reject | 新 Reject | 解讀 |
|--------|-----------|-----------|------|
| `uq_entropy_adwin` | - | - | 仍可用，但新 delta accuracy 較低 |
| `uq_mi_like_adwin` | - | - | 仍可用，但 detected ratio 壓到 0.30 邊界 |
| `uq_vote_adwin` | `silent_detector` | `silent_detector` | 仍是 conservative / low-adaptation baseline |
| `uq_variance_adwin` | `silent_detector` | `silent_detector` | 仍是 conservative / low-adaptation baseline |
| `uq_entropy_seqdrift2` | - | `event_explosion` | 新 delta 過敏 |
| `uq_mi_like_seqdrift2` | - | `event_explosion` | 新 delta 過敏 |
| `uq_vote_seqdrift2` | - | `event_explosion` | 新 delta 過敏 |
| `uq_variance_seqdrift2` | - | `event_explosion` | 新 delta 過敏 |

---

## 4. 各設定深入分析

### `uq_entropy_adwin`：新 delta 下最乾淨的主候選

| 指標 | 舊 delta | 新 delta | 結論 |
|------|---------:|---------:|------|
| Accuracy | **0.9511** | 0.9469 | 新 delta 變差 |
| Detected Ratio | 0.65 | 0.70 | 稍接近 1 |
| Recovery Delay | **370.1** | 434.8 | 新 delta 變慢 |
| False Events | **1.6** | 2.4 | 新 delta 變多 |

`uq_entropy_adwin` 仍是新 delta 裡最乾淨的非 rejected 主候選，但和舊 delta 相比沒有改善。

### SeqDrift2 variants：高 accuracy 但全部 event explosion

| Config | Accuracy | Detected Ratio | False Events | Reject |
|--------|---------:|---------------:|-------------:|--------|
| `uq_entropy_seqdrift2` | **0.9532** | 4.75 | 14.3 | `event_explosion` |
| `uq_variance_seqdrift2` | 0.9518 | 4.53 | 14.0 | `event_explosion` |
| `uq_mi_like_seqdrift2` | 0.9511 | 4.63 | 14.4 | `event_explosion` |
| `uq_vote_seqdrift2` | 0.9503 | 4.55 | 14.5 | `event_explosion` |

SeqDrift2 新 delta 可以當作高敏感壓力測試，但不建議直接作為 final deployable candidate。

### Silent ADWIN variants：仍可當保守對照

| Config | Accuracy | Detected Ratio | False Events | Reject |
|--------|---------:|---------------:|-------------:|--------|
| `uq_vote_adwin` | 0.9455 | 0.125 | 0.4 | `silent_detector` |
| `uq_variance_adwin` | 0.9453 | 0.225 | 0.7 | `silent_detector` |

`silent_detector` 不等於一定不好，但這兩組沒有超過 `uq_entropy_adwin`，因此仍不建議當主配置。

---

## 5. 結論與建議

### 新 delta 實驗本身的排序

| 優先順序 | 配置 | 理由 |
|----------|------|------|
| 1 | `uq_entropy_adwin` | 非 rejected 中最乾淨，detected ratio 0.70 |
| 2 | `uq_mi_like_adwin` | 非 rejected，但 accuracy 較低且 detected ratio 卡在 0.30 |
| 3 | `uq_entropy_seqdrift2` | raw accuracy 最高，但 `event_explosion` |
| 4 | `uq_variance_seqdrift2` | raw accuracy 第二，但 `event_explosion` |

### 和舊 delta 比較後的建議

```text
舊 delta 的 uq_entropy_adwin 仍比新 delta 的 uq_entropy_adwin 好。
新 delta 的 SeqDrift2 提高 accuracy，但代價是全面 event explosion。
因此不建議用 ADWIN 0.05/0.02 + SeqDrift2 0.550/0.553 作為下一輪主設定。
```

最合理的下一步不是直接採用新 delta，而是：

```text
保留舊 delta 的 uq_entropy_adwin 作乾淨主候選
若要繼續調 SeqDrift2，應往降低敏感度方向調
例如把 SeqDrift2 warning/drift delta 往舊 preset 附近或中間值回拉
```

> [!WARNING]
> 本輪結果再次提醒：Final ECPF selection 不能只看 accuracy。SeqDrift2 新 delta 的 accuracy 很漂亮，但 event count 和 false events 已經超過合理部署範圍，應視為高敏感 ablation，而不是最終配置。
