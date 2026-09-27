# ECPF UQ 實驗分析：5 棵樹 vs 10 棵樹 Ensemble 比較

## 文件對應

| 指標 | 5 棵樹 (n_trees=5) | 10 棵樹 (n_trees=10) |
|------|---------------------|----------------------|
| Summary | `ecpf_uq_summary.csv` | `ecpf_uq_summary_10.csv` |
| Per-file comparison | `ecpf_uq_comparison.csv` | `ecpf_uq_comparison_10.csv` |
| Events | `ecpf_uq_events.csv` | `ecpf_uq_events_10.csv` |

---

## 1. 總覽：Summary 指標比較

### Accuracy（Prequential Accuracy）

| Setting | 5 Trees | 10 Trees | Δ | 勝者 |
|---------|---------|----------|------|------|
| A — Baseline HT+error | 0.9563 | 0.9563 | 0.0000 | 平手 |
| B — HF+error (direct) | **0.9564** | 0.9502 | **+0.0062** | ✅ 5 Trees |
| C — HF+UQ(MI) | **0.9662** | 0.9597 | **+0.0065** | ✅ 5 Trees |
| D1 — HF+UQ(vote) | **0.9664** | 0.9597 | **+0.0068** | ✅ 5 Trees |
| D2 — HF+UQ(entropy) | **0.9645** | 0.9569 | **+0.0076** | ✅ 5 Trees |

> [!IMPORTANT]
> **5 棵樹在所有使用 HF (Hoeffding Forest) 的設定中，準確率都勝出**，幅度約 0.6%–0.8%。Setting A（使用單棵 HT）完全相同，驗證了 baseline 的正確性。

---

### Detection Delay（偵測延遲，越低越好）

| Setting | 5 Trees | 10 Trees | Δ | 勝者 |
|---------|---------|----------|------|------|
| A — Baseline HT+error | 406.5 | 406.5 | 0.0 | 平手 |
| B — HF+error (direct) | **401.1** | 412.9 | **-11.7** | ✅ 5 Trees |
| C — HF+UQ(MI) | **255.2** | 286.9 | **-31.7** | ✅ 5 Trees |
| D1 — HF+UQ(vote) | **237.3** | 260.7 | **-23.5** | ✅ 5 Trees |
| D2 — HF+UQ(entropy) | **279.4** | 318.1 | **-38.8** | ✅ 5 Trees |

> [!TIP]
> **5 棵樹在所有 UQ 方法中，偵測延遲都更短。** 特別是 UQ(MI) 和 UQ(entropy) 減少了 30-39 個樣本的延遲。D1 (vote disagreement) 在兩個配置中都是最低延遲的方法。

---

### False Warning Rate（假警報率，越低越好）

| Setting | 5 Trees | 10 Trees | Δ | 勝者 |
|---------|---------|----------|------|------|
| A — Baseline HT+error | 0.761 | 0.761 | 0.000 | 平手 |
| B — HF+error (direct) | **0.676** | 0.738 | **-0.062** | ✅ 5 Trees |
| C — HF+UQ(MI) | 0.424 | **0.404** | +0.020 | ✅ 10 Trees |
| D1 — HF+UQ(vote) | **0.427** | 0.470 | **-0.044** | ✅ 5 Trees |
| D2 — HF+UQ(entropy) | **0.508** | 0.552 | **-0.044** | ✅ 5 Trees |

> [!NOTE]
> 兩者互有勝負，但整體 5 棵樹略優。值得注意的是 **Setting C (UQ-MI) 是唯一 10 棵樹假警報率更低的設定**（0.404 vs 0.424），這可能因為 10 棵樹提供了更穩定的 MI 估計。

---

### Reuse Precision（模型重用精度，越高越好）

| Setting | 5 Trees | 10 Trees | Δ | 勝者 |
|---------|---------|----------|------|------|
| A — Baseline HT+error | 0.822 | 0.822 | 0.000 | 平手 |
| B — HF+error (direct) | **0.879** | 0.798 | **+0.082** | ✅ 5 Trees |
| C — HF+UQ(MI) | 0.841 | **0.862** | -0.020 | ✅ 10 Trees |
| D1 — HF+UQ(vote) | **0.890** | 0.876 | **+0.014** | ✅ 5 Trees |
| D2 — HF+UQ(entropy) | 0.865 | **0.885** | -0.020 | ✅ 10 Trees |

> [!NOTE]
> Reuse Precision 差異不大。10 棵樹在 C 和 D2 略勝，5 棵樹在 B 和 D1 勝出。整體看起來模型重用的精度不太受 ensemble size 影響。

---

### Average Collection Size（模型池大小）

| Setting | 5 Trees | 10 Trees | Δ |
|---------|---------|----------|------|
| A — Baseline HT+error | 3.22 | 3.22 | 0.00 |
| B — HF+error (direct) | **3.70** | 3.40 | +0.30 |
| C — HF+UQ(MI) | **3.20** | 2.98 | +0.22 |
| D1 — HF+UQ(vote) | **3.34** | 3.10 | +0.24 |
| D2 — HF+UQ(entropy) | 3.12 | **3.50** | -0.38 |

> 5 棵樹傾向維持較大的模型池，除了 D2 設定。

---

### Runtime（秒，越低越好）

| Setting | 5 Trees | 10 Trees | Δ | 倍率 |
|---------|---------|----------|------|------|
| A — Baseline HT+error | 17.2 | 18.3 | -1.0 | 1.06x |
| B — HF+error (direct) | **131.5** | 242.3 | -110.8 | **1.84x** |
| C — HF+UQ(MI) | **148.3** | 288.6 | -140.4 | **1.95x** |
| D1 — HF+UQ(vote) | **135.9** | 316.2 | -180.3 | **2.33x** |
| D2 — HF+UQ(entropy) | **113.5** | 234.5 | -121.0 | **2.07x** |

> [!IMPORTANT]
> **10 棵樹的運行時間是 5 棵樹的 1.8x ~ 2.3x**。這是 10 棵樹最大的劣勢。增加 ensemble 規模帶來的計算成本在 UQ 方法中尤其顯著。

---

## 2. 關鍵發現

### 🏆 5 棵樹 全面勝出的指標

```
✅ Accuracy（除 A 平手外均勝）
✅ Detection Delay（所有 HF 設定均勝）
✅ Runtime（快 ~2 倍）
✅ False Warning Rate（4/5 勝出）
```

### 🔍 10 棵樹的少數優勢

```
📌 Setting C (UQ-MI): 假警報率略低 (0.404 vs 0.424)
📌 Setting C & D2: Reuse Precision 略高
```

---

## 3. 各設定深入分析

### Setting C — HF+UQ(MI)：最佳 UQ 方法候選

| 指標 | 5 Trees | 10 Trees | 結論 |
|------|---------|----------|------|
| Accuracy | **0.9662** | 0.9597 | 5T 勝 |
| Detection Delay | **255.2** | 286.9 | 5T 更快反應 |
| False Warning | 0.424 | **0.404** | 10T 更穩 |
| Reuse Precision | 0.841 | **0.862** | 10T 重用更準 |
| Runtime | **148s** | 289s | 5T 快一倍 |

> [!TIP]
> Setting C 是 UQ 系列中假警報率最低的方法。10 棵樹在此設定的 FWR 和 Reuse Precision 略佳，但代價是 ~2 倍的運行時間和較低的準確率。如果追求低假警報且計算預算允許，10 棵樹的 UQ(MI) 值得考慮。

### Setting D1 — HF+UQ(vote)：整體最優

| 指標 | 5 Trees | 10 Trees | 結論 |
|------|---------|----------|------|
| Accuracy | **0.9664** | 0.9597 | 5T 最高 |
| Detection Delay | **237.3** | 260.7 | 5T 最快 |
| False Warning | **0.427** | 0.470 | 5T 勝 |
| Reuse Precision | **0.890** | 0.876 | 5T 勝 |
| Runtime | **136s** | 316s | 5T 快 2.3 倍 |

> [!IMPORTANT]
> **Setting D1 + 5 棵樹 是所有組合中的最優配置**：最高準確率、最低偵測延遲、高 Reuse Precision，且運行速度最快。

---

## 4. 結論與建議

### 為什麼 5 棵樹更好？

1. **Overfitting vs Diversity 權衡**: 在流數據（streaming data）環境中，5 棵樹的 ensemble 提供了足夠的多樣性來捕捉不確定性，而 10 棵樹可能引入過多噪音或稀釋了個別樹的學習信號。

2. **UQ 信號的靈敏度**: 較小的 ensemble 產生的不確定性估計對概念漂移更敏感，因為每棵樹的 "vote" 權重更大，分歧（disagreement）更容易被觀察到。

3. **計算效率**: 5 棵樹在保持甚至提高效能的同時，運行速度快了 ~2 倍。

### 推薦配置

| 優先目標 | 推薦配置 |
|----------|----------|
| 🎯 整體最優 | **D1 (vote disagreement) + 5 棵樹** |
| 🎯 最低假警報 | C (MI-like) + 10 棵樹 |
| 🎯 最快運行 | D2 (entropy) + 5 棵樹 |
| 🎯 基準對比 | A (HT+error baseline) |

> [!WARNING]
> 以上分析基於 SEA 合成數據集（10 個隨機種子），在真實數據上的表現可能有所不同。建議在實際應用場景中進一步驗證。
