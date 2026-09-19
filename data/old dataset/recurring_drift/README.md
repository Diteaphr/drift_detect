# recurring_sud_sea100k 資料集說明與誤報分析

本文件說明 `data/old dataset/recurring_drift/` 中 10 個 recurring sudden drift 資料集的實際結構，
以及為什麼在**非 groundtruth 的位置**會出現大量偵測到的 drift。

分析日期：2026-08-13。所有數字皆由實測反推得出（腳本見文末「重現方式」）。

---

## 1. 檔案內容

| 項目 | 內容 |
|---|---|
| 檔案 | `recurring_sud_sea100k_g00.csv` ~ `g09.csv` |
| 樣本數 | 每個檔案 100,000 筆 |
| 欄位 | `x0, x1, x2, y`，三個特徵皆 ~ Uniform(0, 10)，`x2` 為無關特徵 |
| 標籤 | 二元 |
| Groundtruth | `recurring_sud_sea100k_gXX_drift_times.txt`，格式為 `[[start, end], ...]` 的 index 對 |

## 2. 真實概念函數（反推結果）

每個檔案都是 river `synth.SEA` 產生的，標籤規則為：

```
y = 1  if  x0 + x1 > θ
y = 0  otherwise
```

其中 θ 只會在 SEA 的四個 variant 門檻 `{7, 8, 9, 9.5}` 中取值。

**關鍵發現：每個檔案只在「兩個」門檻之間來回切換，且完全沒有 label noise。**

用反推的 θ 重建標籤，與檔案中的 `y` 吻合度為 **100.00%**（全部 10 個檔案、全部區段）。

| 檔案 | 交替的 θ | drift 次數 | 概念差異帶佔比（severity） |
|---|---|---|---|
| g00 | 8 ↔ 7 | 10 | 7.50% |
| g01 | 8 ↔ 9 | 8 | 8.50% |
| g02 | 7 ↔ 8 | 8 | 7.50% |
| g03 | 8 ↔ 9 | 12 | 8.50% |
| g04 | 9 ↔ 7 | 6 | 16.00% |
| g05 | 9.5 ↔ 7 | 8 | **20.63%**（最強） |
| g06 | 9 ↔ 7 | 8 | 16.00% |
| g07 | 8 ↔ 7 | 8 | 7.50% |
| g08 | 9.5 ↔ 9 | 6 | **4.63%**（最弱） |
| g09 | 7 ↔ 9 | 8 | 16.00% |

### severity 的定義與計算

兩個概念 θ_lo、θ_hi 只在 `θ_lo < x0+x1 ≤ θ_hi` 這條帶狀區域上標籤不同，其餘區域標籤完全相同。
因此 **一次 drift 能造成的錯誤率上升幅度，上限就是這條帶佔全體樣本的比例**。

令 `s = x0 + x1`，因 `x0, x1 ~ U(0,10)` 獨立，`s` 的機率密度在 `0 ≤ s ≤ 10` 為 `f(s) = s/100`：

```
severity = P(θ_lo < s ≤ θ_hi) = (θ_hi² − θ_lo²) / 200        （θ ≤ 10 時）
```

以 g01（θ = 8 ↔ 9）為例：`(81 − 64) / 200 = 8.5%`。實測各 drift 點後 2000 筆的帶內比例為
7.7% ~ 9.25%，與理論值一致。

> **這是本資料集最重要的性質：一次真 drift 最多只讓錯誤率上升幾個百分點。**
> 實務上更小，因為模型的階梯狀決策邊界在那條窄帶內本來就有誤差。

---

## 3. 為什麼在非 groundtruth 的位置會抓到 drift

有三個獨立的成因，且都會讓錯誤率序列產生**真實的**震盪 —— 所以「檢查 err 發現該點確實有震盪」並不代表那裡真的有概念漂移。

### 成因 A：斜的決策邊界 + 軸平行切割 → 錯誤率永遠階梯式下降

真實邊界 `x0 + x1 = θ` 是一條**斜線**，而 Hoeffding Tree 只能用軸平行切割做階梯逼近，
理論上**永遠逼不完**。結果是樹在整個 stream 上持續生長：

```
g01, HoeffdingTreeClassifier 節點數
i=10k: 11 → 30k: 31 → 50k: 41 → 70k: 47 → 90k: 53
```

每長出一刀，錯誤率就往下掉一階。在**完全沒有 drift 的區段內部**，rolling(1000) 錯誤率：

```
i=15000: 0.064 → 20000: 0.037 → 25000: 0.020     （13318~28724 為同一概念）
i=30000: 0.071 → 35000: 0.063 → 40000: 0.033 → 45000: 0.018   （28724~45219 為同一概念）
```

由於資料**完全無 noise**，錯誤率可以壓到 0.01 附近，使得每一階的相對變化更加顯著。

### 成因 B：ADWIN 家族是雙向偵測，錯誤率「下降」照樣報警

ADWIN / SEED / SeqDrift2 偵測的是「兩個子視窗的平均值是否不同」，**不分上升或下降**。
因此成因 A 的階梯下降會被直接判為 drift。

實測 g01（HoeffdingTree + ADWIN δ=0.05，模型不重置），11 次 alarm 的前後視窗平均：

```
t=3455    0.060 → 0.092  RISE  非GT
t=10783   0.036 → 0.036  FALL  非GT   ← 學習曲線
t=20543   0.024 → 0.016  FALL  非GT   ← 學習曲線
t=28095   0.012 → 0.008  FALL  非GT   ← 學習曲線
t=29183   0.068 → 0.088  RISE  GT+459
t=37279   0.036 → 0.016  FALL  非GT   ← 學習曲線
t=45919   0.072 → 0.060  FALL  GT+700
t=54655   0.072 → 0.028  FALL  非GT   ← drift 後的恢復
t=71967   0.052 → 0.052  FALL  GT+672
t=83839   0.008 → 0.036  RISE  GT+966
t=93407   0.048 → 0.072  RISE  GT+474
```

### 成因 C：drift 之後的「恢復下降」會再觸發一次

真 drift 讓錯誤率上升 → 模型學會新概念 → 錯誤率掉回來。這個**掉回來**本身又是一次
mean shift，若落在 tolerance window 之外就被記成 FP（例如上表 t=54655）。
severity 越大，這個恢復落差也越大。

---

## 4. 實測數據（全部 10 個檔案）

基線設定：`HoeffdingTreeClassifier` + `ADWIN(delta=0.05)`，以 0/1 錯誤為訊號，
**模型不重置**（純粹量測資料集本身造成的誤報壓力），tolerance window = 2000。

| 檔案 | severity | GT drift | alarms | TP | FP | 平均延遲 |
|---|---|---|---|---|---|---|
| g00 | 0.075 | 10 | 8 | 3 | 5 | 402 |
| g01 | 0.085 | 8 | 11 | 5 | 6 | 654 |
| g02 | 0.075 | 8 | 14 | 8 | 6 | 708 |
| g03 | 0.085 | 12 | 16 | 7 | 9 | 670 |
| g04 | 0.160 | 6 | 13 | 6 | 7 | 582 |
| g05 | 0.206 | 8 | 22 | 6 | 16 | 225 |
| g06 | 0.160 | 8 | 17 | 6 | 11 | 233 |
| g07 | 0.075 | 8 | 13 | 4 | 9 | 594 |
| g08 | 0.046 | 6 | 9 | 3 | 6 | 1233 |
| g09 | 0.160 | 8 | 15 | 6 | 8 | 380 |

### FP 的方向分解

把每個 FP 依「前 1000~300 筆平均」vs「前 300 筆平均」分類：

| 檔案 | FP 錯誤率上升 | FP 錯誤率**下降** | 其中屬 drift 後恢復（GT+2000~6000） | 遠離任何 GT |
|---|---|---|---|---|
| g00 | 2 | 3 | 1 | 4 |
| g01 | 2 | 4 | 1 | 5 |
| g02 | 0 | 6 | 1 | 5 |
| g03 | 4 | 5 | 3 | 6 |
| g04 | 0 | 7 | 2 | 5 |
| g05 | 4 | 12 | 6 | 10 |
| g06 | 3 | 8 | 6 | 5 |
| g07 | 3 | 6 | 2 | 7 |
| g08 | 3 | 3 | 2 | 4 |
| g09 | 1 | 7 | 3 | 5 |
| **合計** | **22** | **61** | **27** | **56** |

**83 個 FP 中有 61 個（73%）是錯誤率「下降」時觸發的**，而且 56 個（67%）距離任何
groundtruth 都超過 6000 筆 —— 也就是純粹的學習曲線階梯，與概念漂移無關。

### 提高 severity 並不能解決誤報

值得注意的是 **g05（severity 最高，20.6%）反而 FP 最多（16 個）**。
原因是 severity 越大，drift 後的錯誤率尖峰越高、恢復落差也越大，
雙向偵測器在「上升」和「下降」各觸發一次，同時樹在 drift 後需要更多重構、
產生更多階梯。**所以把概念差異拉大只能改善 recall，無法降低 FP。**

---

## 5. 對評估與實驗設計的建議

### 5.1 Tolerance window 至少設 2000

實測延遲中位數約 400~700，最大值出現在 g08（severity 最低）達 1233。
window 設太小會讓遲到的 TP 被同時記成一個 FP 加一個 FN，雙重懲罰。

### 5.2 加單邊限制（只認錯誤率上升）—— 有效但代價高

在 g01 上實測，alarm 後檢查 `mean(近300) > mean(前700) + 0.01` 才採納：

| 設定 | alarms | TP | FP |
|---|---|---|---|
| 原始 | 11 | 5 / 8 | 6 |
| 加單邊過濾 | 3 | 2 / 8 | 1 |

FP 從 6 降到 1，但 recall 從 5/8 掉到 2/8。這是低訊噪比的典型特徵：
只能在 precision 與 recall 之間硬換，沒有明顯甜蜜點。
若採用，建議把門檻（此處 0.01）當成需要校準的超參數。

### 5.3 其他可行方向

- **足夠長的 warm start**：前 5000 筆是學習曲線最陡的階段，階梯下降最密集。
  建議 warm start ≥ 5000 再開啟偵測（目前 `run_ecpf_recurring_batch.py` 預設 200）。
- **換 base learner**：`HoeffdingTreeClassifier(leaf_prediction="nba")` 或
  logistic regression 對斜邊界較友善，能減少階梯效應。
- **Alarm cooldown**：單獨使用效果有限（g01 上 cooldown=1500 只把 alarms 從 11 降到 10），
  需搭配上述其他手段。
- **報告 severity 分層結果**：g08（4.6%）與 g05（20.6%）難度差 4 倍以上，
  把 10 個檔案的指標平均會掩蓋這個差異。建議至少分成
  低 severity（g00, g01, g02, g03, g07, g08）與高 severity（g04, g05, g06, g09）兩組報告。

### 5.4 資料集本身的限制（撰寫論文時應揭露）

1. **無 label noise**，與真實串流資料差距大；模型可將錯誤率壓到接近 0，
   放大了學習曲線抖動的相對幅度。
2. **只有兩個交替概念**，不是真正的多概念 recurring；對 model pool 類方法
   （如 ECPF）而言 pool 大小需求被低估。
3. **概念差異侷限在一條窄帶**，屬於低 severity drift。
4. `x2` 為完全無關的特徵，不影響標籤。

---

## 6. 重現方式

以下腳本可重現本文件所有數字（於專案根目錄執行）。

**反推概念函數與 severity：**

```python
import pandas as pd, numpy as np, ast, pathlib
D = pathlib.Path("data/old dataset/recurring_drift")
for i in range(10):
    df = pd.read_csv(D / f"recurring_sud_sea100k_g{i:02d}.csv")
    gt = [p[0] for p in ast.literal_eval(
        (D / f"recurring_sud_sea100k_g{i:02d}_drift_times.txt").read_text().strip())]
    s = (df.x0 + df.x1).values
    bnds = [0] + gt + [len(df)]
    for a, b in zip(bnds[:-1], bnds[1:]):
        acc, th = max((((s[a:b] > t).astype(int) == df.y.values[a:b]).mean(), t)
                      for t in [7, 8, 9, 9.5])
        print(f"g{i:02d} [{a},{b}) theta={th} agree={acc:.4f}")
```

**基線偵測實驗：**

```python
from river import tree, drift
model = tree.HoeffdingTreeClassifier()
ad = drift.ADWIN(delta=0.05)
errs, alarms = [], []
for k, (x, y) in enumerate(zip(df[["x0","x1","x2"]].to_dict("records"), df.y.values)):
    p = model.predict_one(x)
    e = 0 if p == y else 1
    errs.append(e)
    model.learn_one(x, y)
    ad.update(e)
    if ad.drift_detected:
        alarms.append(k)
```

---

## 7. 結論

> 這批資料集的 drift 幅度（4.6% ~ 20.6% 的樣本標籤翻轉）與模型自身學習曲線的
> 階梯抖動處於**同一數量級**。在雙向 mean-shift 偵測器（ADWIN 家族）下，
> 有 73% 的誤報來自錯誤率**下降**，其中三分之二遠離任何 groundtruth ——
> 偵測器實際上是在「偵測 Hoeffding Tree 什麼時候長了新枝」，而不是概念漂移。

因此在非 groundtruth 點看到 err 震盪並伴隨 alarm 是**預期行為**，
不是偵測器實作錯誤。改善方向應放在偵測訊號的方向性、warm start 長度、
base learner 選擇，以及評估時的 tolerance window 與 severity 分層。
