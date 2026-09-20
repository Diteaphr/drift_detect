# injected_real_dataset

依 [Cerqueira et al., *A Framework for Evaluating and Benchmarking Concept Drift Detection Methods*](https://arxiv.org/abs/2606.07789) 的 **drift simulation**：  
對同層 [`real_dataset`](../real_dataset/) 的 **分類** 資料先 **shuffle**，再以 Monte Carlo 注入 **單一已知 drift**，輸出與 `synthetic_dataset` 相同可用的 `csv` + `*_drift_times.txt`。

論文設定為 **data stream classification**（binary / multi-class），故 **不含 regression**。

參考實作：[vcerqueira/experiments-drift_evaluation](https://github.com/vcerqueira/experiments-drift_evaluation)

## 四種注入方法

| method | 論文名稱 | 作法 |
|---|---|---|
| `class_prior` | Class prior | drift 後以機率 \(p=0.75\) 丟棄選定類別實例 |
| `label_swap` | Class label swap | drift 後將選定類別標籤改為另一類 |
| `feature_permutation` | Feature permutation | drift 後依固定隨機排列重排特徵 |
| `feature_filtering` | Feature filtering | drift 後若選定特徵 \(>\) 漂移前中位數則丟棄 |

每種方法各有 **abrupt**（\(w=0\)）與 **gradual**（寬度 ≤ **1000**，見下表；過渡區內變換機率線性 0→1）。

## 可處理的來源資料

| 來源 (`real_dataset`) | 任務 | 適用方法 | gradual width | 備註 |
|---|---|---|---|---|
| `ai4i2020` | binary | 四種皆可 | 500 | |
| `electricity` | binary | 四種皆可 | 1000 | |
| `gas_sensor_drift` | multi | 四種皆可 | 1000 | |
| `covertype` | multi | 四種皆可 | 1000 | 抽樣至 100k（論文 Table 3） |

## 檔案結構

```text
data/injected_real_dataset/
├── binary/
│   ├── abrupt/{class_prior,label_swap,feature_permutation,feature_filtering}/
│   ├── gradual/...
│   └── drift_plots/          # g00 驗證圖
├── multi_classification/
│   └── ...
├── script/
└── README.md
```

檔名：`{dataset}_{method}_{abrupt|gradual}_gXX.csv`  
另附：`*_drift_times.txt`（輸出串流索引 `[[ds, de]]`）、`*.json`（該 trial 的 seed／選類／排列等）。

## 重跑

```bash
cd data/injected_real_dataset/script

# 快速檢查
python3 generate_all.py --smoke

# 完整：4 資料集 × 4 方法 × abrupt/gradual × g00–g09
python3 generate_all.py

# 子集
python3 generate_all.py --datasets electricity --methods class_prior,label_swap --g-ids 0,1
```
