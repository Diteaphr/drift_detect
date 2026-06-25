# 偵測器靈敏度校準實驗

本文件整理目前「偵測器參數校準」的完整實驗設計與最新結果，包含：

1. **Standalone 校準**（直接看 detector 對 HF error stream 的反應）
2. **ECPF-integrated 校準**（在完整 pipeline 中比較不同 ECPF detector）

---

## 實驗目標

預設參數下，各 detector 的觸發次數（`N_detect`）常與實際 drift 次數（`N_actual`）偏差很大，直接比較延遲會失真。  
本實驗先做參數校準，再在 hold-out streams 上比較：

- `count_score = 1 - |N_detect - N_actual| / N_actual`
- `CD%`（correct detection rate）
- `avg_delay`（對上真實 drift 起點後的平均延遲，容忍窗 `tolerance=2000`）

---

## 資料切分

| 用途 | Streams |
|------|---------|
| 校準（Phase 1） | `data/recurring_drift/recurring_sud_sea100k_g00~g04.csv` |
| 評估（Phase 2） | `data/recurring_drift/recurring_sud_sea100k_g05~g09.csv` |

- 每條 stream 對應同名 `*_drift_times.txt`
- warm start：`200` samples
- drift matching tolerance：`2000` samples

---

## 實驗設計

## 1) Standalone 校準（`scripts/calibrate_standalone_detectors.py`）

### 模式
- 模型：`HoeffdingForestModel`（`n_trees=5`, `lambda_poisson=6`, `seed=42`）
- detector 直接吃 0/1 error stream，不經 ECPF 模型切換流程

### 參數搜尋空間
| 偵測器 | 參數 | grid |
|--------|------|------|
| `adwin` | `delta` | `[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3]` |
| `seqdrift2` | `delta` | `[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]` |

### 校準規則
- `warning_param`：找「`N_fires > N_actual` 中最小的 N」對應參數（略敏感）
- `confirm_param`：找「`N_fires <= N_actual` 中最大的 N」對應參數（較保守）
- 對 g00–g04 各 stream 算完後取 median，再 snap 回 grid

---

## 2) ECPF-integrated 校準（`scripts/calibrate_and_evaluate_detectors.py`）

### 模式
- `use_ecpf=True`
- `model_type="hf"`
- 每個 detector 掃一個主參數，先在 g00–g04 校準，再在 g05–g09 評估

### 參數搜尋空間
| 偵測器 | `param_attr` | grid |
|--------|--------------|------|
| `dual_adwin` | `detector_delta` | `[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3]` |
| `meta_ecpf_hcdt` | `ecpf_hcdt_detection_delta` | `[0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1]` |
| `meta_ecpf_gddm` | `ecpf_gddm_warning_alpha` | `[0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]` |
| `meta_ecpf_hier_parallel` | `ecpf_hier_validation_gap_threshold` | `[0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10]` |

### 校準規則
- 每條 calibration stream 上，選 `count_score` 最大的參數
- 最後取 5 條 stream 的 median-best，並 snap 到最近 grid 值

---

## 最終結果（最新輸出）

## A. Standalone（來源：`outputs/calibration_standalone/calibration_standalone_summary.csv`）

| detector | warning_param | warn_count_score | warn_CD% | warn_avg_delay | confirm_param | conf_count_score | conf_CD% | conf_avg_delay |
|----------|---------------|------------------|----------|----------------|---------------|------------------|----------|----------------|
| adwin | 0.05 | 0.225 | 7.5 | 368 | 0.02 | 0.358 | 5.0 | 418 |
| seqdrift2 | 0.25 | 0.550 | 16.7 | 279 | 0.20 | 0.533 | 25.8 | 333 |

重點：
- `seqdrift2` 在 standalone 下整體優於 `adwin`（count_score 與 CD% 均較高）
- `seqdrift2` 的 `warning_param=0.25` 取得最高 `warn_count_score=0.550`

## B. ECPF-integrated（來源：`outputs/calibration_comparison/calibration_summary.csv`）

| detector | param_attr | calib_param | count_score | CD% | avg_delay |
|----------|------------|-------------|-------------|-----|-----------|
| dual_adwin | detector_delta | 0.001 | 0.433 | 40.0 | 290 |
| meta_ecpf_hcdt | ecpf_hcdt_detection_delta | 0.005 | 0.583 | 42.5 | 150 |
| meta_ecpf_gddm | ecpf_gddm_warning_alpha | 0.01 | 0.000 | 0.0 | n/a |
| meta_ecpf_hier_parallel | ecpf_hier_validation_gap_threshold | 0.005 | 0.000 | 0.0 | n/a |

重點：
- 目前最佳是 `meta_ecpf_hcdt`（`count_score=0.583`, `CD%=42.5`, `avg_delay=150`）
- `dual_adwin` 次佳（`count_score=0.433`, `CD%=40.0`, `avg_delay=290`）
- `meta_ecpf_gddm`、`meta_ecpf_hier_parallel` 在這批設定下未產生有效偵測（分數為 0）

---

## 如何重跑

```bash
cd drift_detect

# Standalone calibration
python scripts/calibrate_standalone_detectors.py

# ECPF-integrated calibration + evaluation
python scripts/calibrate_and_evaluate_detectors.py
```

---

## 產出位置

- `outputs/calibration_standalone/calibration_standalone_summary.csv`
- `outputs/calibration_standalone_run.log`
- `outputs/calibration_comparison/calibration_summary.csv`
- `outputs/calibration_comparison_run.log`
