# 偵測器靈敏度校準實驗

## 目標

每個偵測器的預設參數下，偵測次數（N_detect）與實際 drift 次數（N_actual）差距很大，比較延遲沒有意義。  
本實驗先把每個偵測器的靈敏度旋鈕調到 N_detect ≈ N_actual，再在同等基準下比較平均偵測延遲。

---

## 資料

| 用途 | Streams |
|------|---------|
| 校準（Phase 1） | `data/recurring_drift/recurring_sud_sea100k_g00~g04.csv` |
| 評估（Phase 2） | `data/recurring_drift/recurring_sud_sea100k_g05~g09.csv` |

- 每條 stream 搭配同名 `_drift_times.txt`，格式為 `[[start, end], ...]`
- N_actual 約 10 次 drift（各 stream 不同）

---

## 偵測器與校準參數

| 偵測器 | signal_mode | 校準參數 | 預設值 | 搜尋範圍 | 靈敏度方向 |
|--------|-------------|----------|--------|----------|------------|
| dual_adwin | `dual_adwin` | `detector_delta` | 0.05 | `[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3]` | 越大越敏感 |
| meta_ecpf_hcdt | `meta_ecpf_hcdt` | `ecpf_hcdt_detection_delta` | 0.005 | `[0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1]` | 越大越敏感 |
| meta_ecpf_gddm | `meta_ecpf_gddm` | `ecpf_gddm_warning_alpha` | 0.10 | `[0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]` | 越大越敏感 |
| meta_ecpf_hier_parallel | `meta_ecpf_hier_parallel` | `ecpf_hier_validation_gap_threshold` | 0.02 | `[0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10]` | 越小越敏感 |

補充規則：
- `dual_adwin`：`detector_delta_w = detector_delta * 2`（warning 比 drift 寬鬆一倍）
- `meta_ecpf_gddm`：`ecpf_gddm_drift_alpha = ecpf_gddm_warning_alpha / 10`

---

## 流程

### Phase 1：校準（g00–g04）

```
for each detector:
    for each stream in g00–g04:
        for each param in grid:
            run pipeline → get warning_timestamps
            count_score = 1 - |N_warn - N_actual| / N_actual
        best_param[stream] = argmax(count_score)
    calibrated_param = median(best_param over 5 streams)
              → snap to nearest grid value
```

### Phase 2：評估（g05–g09）

```
for each detector at calibrated_param:
    for each stream in g05–g09:
        compute:
            count_score    = 1 - |N_warn - N_actual| / N_actual
            avg_delay      = mean(first_warning_t - true_drift_start_t)
                             (matched within tolerance=2000 samples)
            CD%            = correct detection % (TP-FP)/N * 100
    report mean over 5 streams
```

### 輸出

- 表格印在終端機
- CSV：`outputs/calibration_comparison/calibration_summary.csv`

---

## 執行

```bash
cd drift_detect
pip install -r requirements.txt
python scripts/calibrate_and_evaluate_detectors.py
```

---

## ht vs hf 的差異與實驗影響

### 模型定義

| | ht（Hoeffding Tree） | hf（Hoeffding Forest，River ARF） |
|-|----------------------|-----------------------------------|
| 結構 | 單棵樹 | 多棵樹的 ensemble |
| 速度 | 快 | 慢（預設 10 棵樹） |
| `proba_matrix` 輸出 | **無**（None） | **有**（per-tree 機率字典） |
| UQ 信號可用性 | 無（全 fallback 0） | 可計算 uq_mi / uq_vote / uq_entropy |

### 對各偵測器的影響

| 偵測器 | 用到的信號 | ht 下的行為 | hf 下的行為 |
|--------|-----------|------------|------------|
| `dual_adwin` | error（0/1 loss） | ✅ 正常 | ✅ 正常 |
| `meta_ecpf_hcdt` | error（HDDM_A） | ✅ 正常 | ✅ 正常 |
| `meta_ecpf_gddm` | **per-tree error rates + UQ** | ⚠️ proba_matrix=None → 無法建構 signal vector，警報數極少或極多 | ✅ 正常設計行為 |
| `meta_ecpf_hier_parallel` | **UQ warning + error validation** | ⚠️ UQ 信號 fallback 0 → warning layer 幾乎不觸發 | ✅ 正常設計行為 |

### 結論與建議

**如果全部用 `ht`：**
- `dual_adwin` 和 `hcdt` 正常；`gddm` 和 `hier_parallel` 嚴重退化（等於沒在用它們的核心機制）
- 實驗結果會低估 `gddm` 和 `hier_parallel` 的真實能力

**建議：全部改成 `hf`**
- `dual_adwin` 和 `hcdt` 只用 error signal，換成 hf 結果不變，只是慢一些
- `gddm` 和 `hier_parallel` 恢復正常
- 四個偵測器共用同一個 model，比較公平

修改方式：在 `scripts/calibrate_and_evaluate_detectors.py` 第 96 行改一個字：

```python
# 原本
cfg.model_type = "ht"

# 改成
cfg.model_type = "hf"
```

**預期影響：**
- 每條 stream 的執行時間增加約 3–5 倍
- `gddm` 的 count_score 應從 0 恢復到有意義的數字
- `hier_parallel` 的 UQ warning 層才會真正作用

---

## 相關檔案

| 路徑 | 說明 |
|------|------|
| `scripts/calibrate_and_evaluate_detectors.py` | 主實驗腳本 |
| `src/metrics/detection_delay.py` | 延遲指標計算 |
| `src/metrics/detection_evaluation.py` | count_score / CD% |
| `src/config.py` | PipelineConfig（所有超參數定義） |
| `data/recurring_drift/` | 實驗資料（已進 git） |
| `outputs/calibration_comparison/` | 結果輸出目錄（自動建立） |
