# dataset_0921

本目錄彙整 2026-09-21 可用的概念漂移實驗資料集。  
統一格式：特徵欄 `x0,x1,...` + 目標 `y`；有 GT 者另附 `*_drift_times.txt`（`[[start, end], ...]`）。

## 資料夾一覽

| 資料夾 | 類型 | 有無 GT drift | 主要任務 | 一句話 |
|---|---|---|---|---|
| [`synthetic_dataset`](./synthetic_dataset/) | 合成 | 有 | binary / multi / regression | 可控 sudden／gradual／incremental／recurring |
| [`real_dataset`](./real_dataset/) | 真實 | **無** | binary / multi / regression | 原始真實串流，不虛構 drift 時間 |
| [`insects_dataset`](./insects_dataset/) | 真實（獨立） | **有**（論文公布） | multi | USP Insects；溫度概念切換點已知 |
| [`injected_real_dataset`](./injected_real_dataset/) | 半合成 | 有（注入） | binary / multi | 對 real 分類資料 shuffle 後注入四種已知 drift |

---

### `synthetic_dataset`

- **用途**：可控、可重現的合成基準，對齊 ECPF / `load_recurring_stream_pair` 管線。
- **特色**：
  - 任務：SEA（binary）、RandomRBF4（multi）、Friedman（regression）
  - 漂移：sudden、gradual／incremental（width≤1000，過渡後新概念持續）、recurring
  - 預設約 100k 樣本、g00–g09；含驗證圖 `drift_plots/`
- **細節**：見 [`synthetic_dataset/README.md`](./synthetic_dataset/README.md)

### `real_dataset`

- **用途**：真實世界串流，保留原始時間／列順序，供無 GT 或 proxy 評估。
- **特色**：
  - **不**產生虛構 `drift_times`
  - binary：ai4i2020、electricity、airlines  
  - multi：gas_sensor_drift、covertype（>100k 截前 10 萬筆）  
  - regression：metro_interstate_traffic、bike_sharing
- **細節**：見 [`real_dataset/README.md`](./real_dataset/README.md)

### `insects_dataset`

- **用途**：與 `real_dataset` **分開存放**的真實集——有 Souza et al. 2020 **Table 2 公布的 change points**。
- **特色**：
  - 僅 balanced variants（abrupt / incremental-gradual / incremental / incremental-abrupt-reoccurring / incremental-reoccurring）
  - 6 類昆蟲、33 維特徵；漂移由溫度區間切換定義
  - 注意：y 比例圖上的尖峰多為物種成群出現，**≠** GT 概念點
- **細節**：見 [`insects_dataset/README.md`](./insects_dataset/README.md)

### `injected_real_dataset`

- **用途**：依 Cerqueira et al. (arXiv:2606.07789) 對分類用 `real_dataset` 做 **Monte Carlo 單點漂移注入**，得到有 GT 的半合成串流。
- **特色**：
  - 僅 **classification**（論文設定；不含 regression）
  - 四法：class_prior、label_swap、feature_permutation、feature_filtering × abrupt / gradual（width≤1000）
  - 來源：ai4i2020、electricity、airlines、gas_sensor_drift、covertype；g00–g09
  - 長串流來源已在 `real_dataset` 截為 ≤100k，避免單檔過大
  - 先 shuffle 再注入，以降低原始未知漂移干擾
- **細節**：見 [`injected_real_dataset/README.md`](./injected_real_dataset/README.md)

---

## 怎麼選

| 需求 | 建議 |
|---|---|
| 完全可控的多種漂移型態 | `synthetic_dataset` |
| 真實資料、不假設 drift 點 | `real_dataset` |
| 真實資料 + 論文公布的 drift 時間 | `insects_dataset` |
| 真實特徵複雜度 + 已知注入 drift（分類） | `injected_real_dataset` |

## 路徑

```text
data/dataset_0921/
├── README.md                 ← 本檔
├── synthetic_dataset/
├── real_dataset/
├── insects_dataset/
└── injected_real_dataset/
```

各子目錄內仍有 `script/` 可重跑產生；路徑以各子目錄為根，彼此相對引用（例如 injected → 同層 `real_dataset`）。
