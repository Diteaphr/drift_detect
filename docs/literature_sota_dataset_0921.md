# dataset_0921 文獻 SOTA 對照表

> 整理日期：2026-10-07。目的：判斷本系統在 `data/dataset_0921/` 上的結果是否超過文獻最佳。
> 指標範圍：**預測準確率**（prequential accuracy）與 **漂移偵測品質**（precision / recall / F1 / 偵測延遲）。迴歸資料集只列狀態。
>
> 數字來源標記：**[原文]** = 從論文 PDF/HTML 原始文字或作者公開的結果 CSV 直接讀出；**[摘錄]** = 由網頁擷取工具讀表後轉錄，數字應正確，正式引用前建議再開原文核對一次。

---

## 0. 一張表看完

| 資料集 | 文獻最佳 prequential accuracy | 最佳的「經典串流學習器」 | 偵測品質基準 | 可直接比較？ |
|---|---|---|---|---|
| electricity (45,312) | **95.0%** TabFM+FIFO（Verma et al. 2026，基礎模型）[摘錄] | ARF **90.08%**（DriftMoE 2025）[摘錄] | 無 GT；injected 版見 §5 | ✅ 同資料、同長度 |
| airlines（本 repo 只取前 10 萬） | **70.33%** DriftMoE MoEData [摘錄] | SRP 68.55%（同文）；ARF 68.0%（AXGB 2020）[原文] | 無 GT | ⚠️ 文獻用全長 539,383 |
| covertype（本 repo 只取前 10 萬） | **95.51%** LTM（TabPFN，Lourenço et al. 2025）[摘錄] | SRP **95.27%**（DriftMoE 2025）[摘錄] | 無 GT；injected 版見 §5 | ⚠️ 文獻用全長 581,012 |
| gas_sensor_drift (13,910) | 沒有串流設定下的 accuracy SOTA（文獻用批次 domain adaptation） | — | 只在 Cerqueira 2026 做為注入漂移的來源資料 | ❌ 評估協定不同 |
| ai4i2020 (10,000) | 沒有串流 benchmark；故障率 3.4%，全猜 0 就有 96.6% accuracy | — | — | ❌ 不適合用 accuracy |
| INSECTS（5 個 balanced 版本） | ARF 64.29–77.92%（Souza et al. 2020 Table 5）[原文] | 同左 | NB+偵測器的 accuracy 與偵測次數（Table 6）[原文] | ✅ 同資料、同 GT |
| synthetic（SEA / RBF4 / Friedman） | 沒有可比的 SOTA（資料由本 repo 自己產生） | 參考值見 §4 | — | ❌ 只能當參考 |
| injected_real（Cerqueira 方法） | 不比 accuracy | — | **SEED / STEPD / ABCD** 最強，平均 F1 多在 0.1–0.6（§5） | ⚠️ 參數不同，見 §5.4 |

**結論先講：**
- **Electricity** 是最適合拿來宣稱突破的資料集：資料版本相同，文獻也最多。要超過「經典串流方法」須 > **90.1%**；要超過「目前全部方法」須 > **95.0%**（這個最佳值是 GPU 上跑的表格基礎模型）。另外要注意：最天真的 no-change（直接預測上一筆的標籤）就有 **85.3%**。
- **INSECTS** 是最適合拿來做「準確率 + 偵測」雙重比較的資料集，有官方 GT，原論文的基準清楚。
- **Injected** 資料的文獻 F1 普遍很低，abrupt 最佳約 0.3–0.6，gradual 約 0.1–0.46。真的要比的話，須先把參數對齊論文（§5.4），否則數字不能放在一起比。

---

## 1. Electricity（`real_dataset/binary/electricity`）

**資料一致性：** 本 repo 使用 OpenML 151（Elec2 / MOA `elecNormNew`），共 45,312 筆、8 個特徵（含 date、day、period），和文獻使用的版本相同。✅

### 1.1 Prequential accuracy（數值越高越好）

| 方法 | Accuracy | 論文 | 備註 |
|---|---|---|---|
| **TabFM + FIFO** | **95.0** | Verma et al., *Rethinking Tabular Foundation Models On Data Streams*, arXiv:2610.05352 (2026), Table 9 [摘錄] | 表格基礎模型，需要 GPU，延遲 >10× |
| TabICL + FIFO | 94.4 | 同上 | |
| CURE | 93.6 | 同上 | |
| EvoAutoML | 92.8 | 同上 | 串流 AutoML |
| LTM（TabPFN + sliding memory） | 91.70 | Lourenço et al., arXiv:2502.16840 (2025), Table 1 [摘錄] | |
| ARF | 90.08 ± 0.04 | Aspis et al., *DriftMoE*, arXiv:2507.18464 (2025), Table 2 [摘錄] | **經典方法最佳** |
| ARF / ASML | 90.0 | Verma et al. 2026 [摘錄] | |
| BOLE | 90.17 ± 0.98 | Lourenço et al. 2025 [摘錄] | |
| SRP | 89.64 / 88.70 / 87.85 | DriftMoE / LTM / DynED（不同論文） | 相同方法在不同論文差 ~2% |
| Leveraging Bagging | 88.6 | Žliobaitė, arXiv:1301.3524 (2013), Table 1 [原文] | |
| DynED | 87.88 | Abadifard et al., arXiv:2308.10807 (2023), Table 2 [摘錄] | |
| **No-change（預測上一筆的標籤）** | **85.3** | Žliobaitė 2013, Table 1 [原文]；Verma 2026 為 85.3 | ⚠️ 必比的基準線 |
| Majority class | 57.5 | Verma 2026 [摘錄] | |

### 1.2 注意事項
- **自相關很強：** Žliobaitė (2013) 指出 Electricity 的標籤有強烈的時間自相關。no-change 就有 85.3%，大多數在 MOA 上測過的自適應方法反而贏不過它。報告結果時**一定要同時附上 no-change 基準線和 Kappa-Temporal**。
- DriftMoE 論文中 ARF 在 Electricity 的 Kappa-Temporal 只有 **32.37**，SRP 為 29.37 [摘錄]。如果本系統的 κ_temporal 高於這兩個值，就比單看 accuracy 更有說服力。
- 同一個 ARF 在不同論文落在 85.3–90.1%（ensemble 大小、grace period、實作 MOA/River/CapyMOA 不同）。最嚴謹的做法是**用相同框架自己重跑 ARF/SRP 當基準**。

---

## 2. Airlines（`real_dataset/binary/airlines`）

**資料一致性：** ⚠️ 本 repo **只取前 100,000 筆**（原始 539,383 筆）；類別欄位轉成 category code。文獻都用全長，所以分數**不能直接比**，要宣稱超越須改用全長資料重跑。

| 方法 | Accuracy | 論文 |
|---|---|---|
| **DriftMoE (MoEData)** | **70.33 ± 0.18** | Aspis et al. 2025, Table 2 [摘錄] |
| SRP | 68.55 ± 0.04 | 同上 |
| ARF | 68.0 | Montiel et al., *Adaptive XGBoost*, arXiv:2005.07353 (2020), Table IV [原文] |
| Leveraging Bagging (HT) | 67.0 | 同上 [原文] |
| ARF | 64.51 ± 0.02 | DriftMoE 2025（同方法、不同設定） |
| AXGB | 62.1 | Montiel et al. 2020 [原文] |

Kappa-M：DriftMoE MoEData 33.39、SRP 29.40 [摘錄]。

---

## 3. Covertype（`real_dataset/multi_classification/covertype`）

**資料一致性：** ⚠️ 本 repo **只取前 100,000 筆**。準確率相關的文獻都用全長 581,012 筆，所以不能直接比。不過 Cerqueira 2026（§5）的偵測實驗剛好也用 **100,000 筆**。

| 方法 | Accuracy | 論文 |
|---|---|---|
| **LTM (TabPFN)** | **95.51** | Lourenço et al. 2025, Table 1 [摘錄] |
| SRP | 95.27 ± 0.01 | DriftMoE 2025 [摘錄] |
| ARF | 94.78 ± 0.02 | DriftMoE 2025 [摘錄] |
| DynED | 94.66 | Abadifard et al. 2023 [摘錄] |
| SRP | 94.54 ± 0.20 | Lourenço et al. 2025 [摘錄] |
| ARF（RF-HT） | 93.9 | Read, arXiv:1810.02266, Table 3 [原文] |

Covertype 的 Kappa-Temporal 幾乎所有方法都 ≤ 4（DriftMoE Table 4）[摘錄]。這代表標籤同樣有很強的時間自相關，看 accuracy 時要特別小心。

---

## 4. 其餘資料集

### 4.1 Gas sensor drift（13,910 筆，6 類）
- 文獻主流是**批次 domain adaptation**（用 batch 1 訓練，再預測 batch 2–10），不是 prequential，所以數字**不可比**。參考值：DAELM-T(50) Setting 1 平均 **91.86%**、Setting 2 平均 **91.82%**；原作者 Vergara 的 SVM ensemble 在 Setting 2 平均 **80.04%**（Zhang & Zhang, IEEE TIM 2015, Table II/III）[原文]。
- 在偵測方面，它是 Cerqueira 2026 的 7 個來源資料之一，見 §5。

### 4.2 AI4I 2020（10,000 筆，故障率 3.4%）
- 找不到使用 prequential 協定的串流 benchmark。少數漂移相關論文（Prashanth et al., CMC 2025）報告 DNN 84% / SVM 89% / RF 100%（作者自己註明 overfit），而且 DNN 只偵測到 1 個漂移點 [原文]，可信度低。
- 全猜「不故障」就有 96.6% accuracy，**accuracy 不適合用來評估**。如果要用，請改看 F1、balanced accuracy 或 Kappa。

### 4.3 INSECTS（`insects_dataset`，5 個 balanced 版本）
**資料一致性：** ✅ 相同資料、相同 change points（Souza et al. 2020, Table 2）。

**(a) 分類準確率**：Souza et al., *Challenges in Benchmarking Stream Learning Algorithms with Real-world Data*, DMKD 2020（arXiv:2005.00113）**Table 5** [原文]。評估方式為 prequential、MOA、sliding window 1,000（window 1,000 與 ARF 的參數尚未從原文第 7 節核對）。

| 版本（bal.） | No-Change | NB | VFDT | Lev.Bag | **ARF（最佳）** |
|---|---|---|---|---|---|
| incremental | 16.04 | 47.37 | 45.65 | 61.42 | **64.29** |
| abrupt | 28.98 | 50.77 | 49.85 | 68.39 | **74.34** |
| incremental-gradual | 38.43 | 52.32 | 51.85 | 72.51 | **77.92** |
| incremental-abrupt-reoccurring | 42.39 | 58.55 | 58.39 | 70.91 | **74.95** |
| incremental-reoccurring | 40.46 | 48.77 | 47.83 | 72.30 | **77.13** |

**(b) 偵測器 + Naive Bayes**：同一篇論文 **Table 6** [原文]，Acc. = prequential accuracy，CD = 偵測到的漂移次數。

| 版本（bal.） | 真實 change points 數 | 最佳 Acc.（偵測器） | 各偵測器 CD |
|---|---|---|---|
| incremental | 連續漂移（沒有離散點） | 56.63（CUSUM） | ADWIN 3 / PHT 1 / CUSUM 5 / DDM 1 / EWMA 0 / SEED 9 / STEPD 30 |
| abrupt | 5 | 66.02（STEPD） | 7 / 6 / 8 / 5 / 90 / 21 / 28 |
| incremental-gradual | 1 | 72.26（ADWIN） | 6 / 7 / 9 / 6 / 39 / 14 / 25 |
| incremental-abrupt-reoccurring | 2 | 68.77（STEPD） | 22 / 17 / 25 / 16 / 114 / 60 / 61 |
| incremental-reoccurring | 2 | 69.82（SEED） | 26 / 16 / 21 / 21 / 108 / 47 / 59 |

- 原論文沒有計算偵測 F1。在 abrupt 版本中，STEPD 抓到全部 5 個突變點，但也有 28 次警報（Fig. 28）。DDM 只報 5 次，最接近真實點數（但沒有逐點核對）。
- 近期的偵測 F1 參考：Minato et al., *The Blind Spot Paradox*, arXiv:2610.05853 (2026) Table II [摘錄]。在 incremental_gradual_balanced 上，PHT+HT 的 F1 = **0.25**，PHT+ARF 只有 0.02。整體來說，INSECTS 上的偵測 F1 很低，不容易做高。
- **建議比較方式：** 拿本系統的 accuracy 和 Table 5 的 ARF 比；如果本系統的偵測器搭配 NB，則和 Table 6 比。偵測 F1 自行計算，並和 Blind Spot 論文的數字並列。

### 4.4 Synthetic（SEA / RandomRBF4 / Friedman）
- ❌ **不可比**：資料由本 repo 用 River 自行產生，每條串流 100k 筆、5–10 個漂移、SEA 沒有加 label noise。文獻常用的是 MOA 的 SEA（1M 筆、3 個漂移、10% noise，上限約 90%）。
- 參考值（MOA 設定）：SEA abrupt 的 ARF 為 89.68、SEA gradual 的 ARF 為 89.33（DriftMoE 2025）；SEA-Abrupt 的 DynED 為 90.61（DynED 2023）[摘錄]。
- ECPF 原論文（Anderson et al., arXiv:1905.08848）的合成實驗用的是 Agrawal / CIRCLES / LED / RandomRBF / STAGGER，**沒有 SEA**。真實資料只畫成圖、沒有列表，文中說法是「ARF 通常最準，ECPF 第二，差距在 4% 以內」[摘錄]。
- 合成資料比較適合**和自己重跑的基準（ARF、ECPF 原版）比**，不適合拿來宣稱超越 SOTA。

### 4.5 迴歸（metro_interstate_traffic、bike_sharing）
這次範圍不含迴歸，因此沒有查。

---

## 5. Injected real dataset — 方法論來源論文

**論文：** Cerqueira, Gomes, Heyden, Pfahringer, Bifet. *A Framework for Evaluating and Benchmarking Concept Drift Detection Methods.* KDD 2026. arXiv:2606.07789。程式與結果：[vcerqueira/experiments-drift_evaluation](https://github.com/vcerqueira/experiments-drift_evaluation)。

### 5.1 實驗設計
| 項目 | 論文設定 |
|---|---|
| 來源資料（7 個） | Asfault (8,563)、**Covertype (100,000)**、**Electricity (45,312)**、**GasSensorArray (13,910)**、NOAA (18,159)、Posture (100,000)、Rialto (82,250) |
| 漂移注入 | 先 shuffle，在串流長度 **50%–80%** 之間隨機放 **1 個**漂移，每種組合做 **k = 50** 次 Monte Carlo |
| 四種方法 | class prior（p_skip）、label swap、feature permutation、feature filtering（以 > 中位數篩選） |
| gradual 寬度 / 最大延遲 δ_max | Electricity、Covertype、Posture、Rialto 為 **2,500**；Gas、NOAA 為 **1,500**；Asfault 為 500 |
| 偵測器（14 個） | ADWIN, CUSUM, DDM, EDDM, EWMA, GMA, HDDM_A, HDDM_W, PH, RDDM, SEED, STEPD, ABCD, ABCD(X), STUDD |
| 基底分類器 | Hoeffding Tree |
| 調參 | leave-one-dataset-out，random search 30 次，目標為偵測 F1 |
| 指標 | F1（窗內**每一次**警報都算 TP，所以 recall 可能把同一個漂移算好幾次；「每個漂移只算 1 次」的是另一個指標 Episode Recall）、MDT（平均偵測延遲）、FAR（誤報率）。窗的實際定義見 §5.1.1 |

#### 5.1.1 作者程式碼和論文正文不一致、或正文沒寫的地方

以下讀自作者公開的程式（`src/eval_detector.py`、`src/prequential_workflow.py`、`scripts/experiments/run_workflows/3_real.py`、`src/streams/`）。論文表格的數字是用這份程式跑出來的，所以對齊時以程式為準。

| 項目 | 程式碼的實際做法 |
|---|---|
| F1 計分 | `tp += 1` 對窗內每一次警報都加；`episode_recall = 有偵測到的漂移數 / 漂移數` 另外算 |
| gradual 漂移的窗 | 真實資料實驗把漂移記成 `(onset, onset)`，所以窗是 **[d_s, d_s + δ_max]**，不是正文的 [d_s, d_e + δ_max]。寬度 = δ_max，等於窗在漂移結束時就關閉 |
| 前段資料 | 前 **25%** 不預測、不送進偵測器（`min_training_size = 0.25 × 串流長度`） |
| 偵測後 | 只記錄警報，**不重置也不替換模型**（純偵測流程）；偵測器輸入是 `int(y == ŷ)` |
| shuffle 與截斷 | 先打亂**整個**資料集，再取前 100,000 筆 |
| 基底分類器 | CapyMOA `HoeffdingTree`，全部預設值 |
| ADWIN 調參 | 搜尋空間 δ ∈ {0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01}，調完幾乎都是 0.01 |
| class prior | `label_skip_proba = 0.75` |
| 一格的數字怎麼算 | 50 次 trial 當成同一次 `calc_performance` 的 50 個 episode：tp/fp/fn **先加總**再算 precision/recall/F1（不是各 trial F1 的平均）；MDT 是所有有偵測到的 trial 的第一次命中延遲平均；FAR = 加總的誤報數 ÷ **一條**串流長度 × 1000（所以等於各 trial FAR 的總和） |
| 座標 | 被注入丟掉的資料列仍會讓 `instances_processed` 加 1，所以警報位置、漂移點和串流長度都是「輸入資料列」的座標 |
| feature filtering 門檻 | 用事先算好的整份資料中位數（`STREAM_MEDIANS`），特徵用 Python `random.choice` 選 |
| ADWIN 的實作 | CapyMOA 的 ADWIN 包的是 MOA `ADWINChangeDetector`：偵測後**不重置**視窗（只丟掉舊的子視窗，所以持續的變化會一直觸發），而且只有在視窗平均值**上升**時才算偵測。偵測器輸入是「答對 = 1」，所以他們的 ADWIN 是在**準確率上升**時（通常是模型在漂移後恢復時）才報警。River 的 ADWIN 每次偵測後整個重置，且升降都算 |

本 repo 的 `src/metrics/evaluate_run.py` 依程式碼的定義計分，並另外輸出正文窗的版本（欄位後綴 `_paper_window`）；`pool_detection_runs` 依上表的方式合併 50 次 trial。驗證：把作者公開的 ADWIN 警報（Electricity / class prior / abrupt 的 `predictions.csv`）丟進我們的評估器，tp/fp/fn、F1 0.698、MDT 1,201.75、FAR 2.58 完全一致（`tests/test_evaluate_run.py::test_pooled_matches_published_cell`）。

### 5.2 七個資料集的平均偵測 F1（Table 5 / 6）[原文，已二次核對]

| 偵測器 | Abrupt：filter / permute / prior / swap | Gradual：filter / permute / prior / swap |
|---|---|---|
| **SEED** | 0.24 / 0.61 / 0.30 / **0.37** | 0.11 / **0.46** / 0.17 / **0.29** |
| **STEPD** | **0.26** / 0.53 / 0.28 / 0.33 | 0.13 / 0.45 / **0.20** / 0.28 |
| ABCD | 0.11 / 0.51 / 0.16 / 0.25 | 0.03 / 0.33 / 0.07 / 0.18 |
| ABCD(X)（無監督，只看 X） | 0.02 / **0.98** / 0.00 / 0.00 | 0.00 / **0.70** / 0.00 / 0.00 |
| ADWIN | 0.24 / 0.27 / **0.31** / 0.16 | 0.10 / 0.04 / 0.15 / 0.08 |
| HDDM_A | 0.17 / 0.36 / 0.20 / 0.24 | 0.07 / 0.10 / 0.13 / 0.06 |

作者的結論是：**SEED 的 F1 排名最好，FAR 也只是中等，是整體最平衡的選擇**；SEED、STEPD、ABCD 是新的基準。GMA 和 RDDM 的 recall 接近 1，但 precision 只有約 0.05，不能用。

### 5.3 與本 repo 重疊資料集的「每格最佳」（作者公開的 hypertuned `results.csv`）[原文]
格式為「最佳偵測器 F1（MDT，單位：筆）」：

| 資料集 / 漂移 | class_prior | label_swap | feature_permutation | feature_filtering |
|---|---|---|---|---|
| Electricity abrupt | ADWIN **0.698**（1,202） | SEED **0.566**（277） | ABCD(X) **1.000**（40） | CUSUM **0.245**（1,154） |
| Electricity gradual | STEPD 0.295（2,044） | STEPD 0.383（905） | ABCD(X) 0.984（709） | STUDD 0.147（751） |
| Covertype abrupt | ABCD 0.133（1,216） | SEED 0.172（715） | ABCD(X) 1.000（72） | STEPD 0.092（1,342） |
| Covertype gradual | STEPD 0.189（1,527） | ABCD 0.175（1,396） | ABCD(X) 0.667（825） | HDDM_W 0.065（789） |
| GasSensor abrupt | DDM 0.400（753） | SEED 0.525（571） | ABCD(X) 1.000（406） | SEED 0.571（474） |
| GasSensor gradual | STUDD 0.519（509） | STUDD 0.384（495） | ABCD 0.704（1,034） | STUDD 0.404（654） |

airlines 和 ai4i2020 **不在**論文的資料集中，沒有文獻基準可比。

### 5.4 與本 repo 版本的差異（直接比之前必看）
| 項目 | 論文 | 舊版 `injected_*`（磁碟上的 CSV） | 論文版 `injected_paper_*`（runner 即時產生） |
|---|---|---|---|
| gradual 寬度 | 2,500（elec/covtype）、1,500（gas） | **≤ 1,000** | 同論文 |
| 容許延遲 δ_max | 同寬度（1,500–2,500） | 登錄表設成論文值 | 同論文 |
| 試驗次數 | 50 | 10（g00–g09） | 50 |
| shuffle 與截斷 | 先打亂整份再取 10 萬筆 | 先取前 10 萬筆再打亂 | 同論文（covertype 用全長檔） |
| 漂移位置 | 50%–80% 隨機 | 相同 | 相同 |
| 座標 | 輸入資料列（含被丟掉的列） | 輸出資料列 | 同論文 |
| 前 25% | 不偵測 | 沒處理 | 評估器忽略這段的警報 |
| 偵測流程 | 單一 HT，偵測後不調整模型 | 本系統的 pipeline（偵測後會換模型） | `detector` preset 照論文流程；pipeline preset 只能當參考 |
| 計分 | 50 次 trial 加總後算 F1 | `pool_detection_runs` | `pool_detection_runs` |

剩下的差異：我們用 River，論文用 CapyMOA/MOA；隨機抽樣不同；feature filtering 的門檻用漂移前的中位數。

**校準現況（2026-10-12）：** 計分已用作者的警報逐筆驗證一致；但用 River 重現的 `det_adwin` 還追不上他們的 ADWIN（Electricity abrupt/class_prior 合併 F1 0.28 vs 0.698、feature_permutation 0.34 vs 0.74；label_swap 0.22 vs 0.25 較接近）。我們的觸發次數明顯較少，差異來自學習器 / 偵測器的實作（MOA 和 River 的 Hoeffding Tree 成長方式不同，影響「準確率上升」的時機）。在補上 CapyMOA 之前，和 §5.3 的比較只能當參考，偵測器之間的比較應以本 harness 內重跑的 `det_adwin` 為準。

**要宣稱 injected 上的偵測超越 SOTA，最低限度要做到：** 在 `injected_paper_*` 上用 `detector` 類型的 preset 跑滿 50 次 × 8 格，用合併後的 F1 和 §5.3 每格的最佳值比較，並附上同 harness 的 `det_adwin`。

---

## 6. 如何拿本系統的結果對比（檢查清單）
1. **協定一致：** 使用 prequential（test-then-train）、逐筆評估、整條串流平均。INSECTS 的 Souza 表格用 sliding window 1,000。
2. **資料長度一致：** airlines 和 covertype 要和 accuracy 文獻比的話，用登錄表的 `airlines_full` / `covertype_full`（全長檔不進 git，先執行 `cd data/dataset_0921/real_dataset/script && python3 prepare_all.py --full`）。
3. **附基準線：** 每個資料集都附上 no-change 和 majority 的結果，以及 Kappa-M 或 Kappa-Temporal（Electricity、Covertype 特別需要）。
4. **自己重跑對照組：** 用相同框架跑 ARF 和 SRP（River 或 CapyMOA），因為同一方法在不同論文的分數可差 2–5%。
5. **偵測：** 回報 precision、recall、F1、Episode Recall、MDT、FAR，評估窗與計分照 Cerqueira 2026 的程式碼（§5.1.1）。
6. **多次種子：** 回報 mean ± std。
7. **調參協定：** 要報告的資料集不能參與挑選設定。先在開發用資料集上調好、把設定凍結成 preset 並 commit，再跑報告用資料集（登錄表的 `role` 欄位）。

---

## 7. 系統輸出要怎麼調整（盤點日期：2026-10-07）

### 7.1 目前輸出和文獻比較時的落差

| # | 位置 | 現況 | 為什麼對不上文獻 |
|---|---|---|---|
| 1 | [main.py:103-117](../main.py#L103-L117) | 一定要讀 `*_drift_times.txt`，而且用區間中點當漂移時間 | `real_dataset` 沒有 GT 檔，main.py 會直接失敗；用中點和 Cerqueira 以 d_s 起算的定義不同 |
| 2 | [main.py:238](../main.py#L238) | precision/recall 用中點 ±300 判定 | 偵測窗和文獻的 [d_s, d_e + δ_max] 不同 |
| 3 | [main.py:267-271](../main.py#L267-L271) | 分類任務輸出的是 MAE | 文獻用 accuracy 和 Kappa；在多類別資料上 MAE 沒有意義（例如把 0 錯判成 5，誤差會算成 5） |
| 4 | [run_ecpf_recurring.py:209](../run_ecpf_recurring.py#L209) 與 `scripts/experiment_*` | accuracy 只算 warm-start（前 200 筆）之後 | 文獻是整條串流一起算 prequential accuracy |
| 5 | [run_ecpf_recurring.py:233-247](../run_ecpf_recurring.py#L233-L247) | 只有 Correct Detection（TP/FP/score） | 沒有 F1、MDT、FAR，無法和 Cerqueira 或 INSECTS 的結果對齊 |
| 6 | [src/metrics/detection_evaluation.py](../src/metrics/detection_evaluation.py) 和 [correct_detection.py](../src/metrics/correct_detection.py) | 預設延伸為 **2000**，但 main.py 和 run_ecpf 傳入的是 **1000** | 同一個系統裡有兩套容許窗 |
| 7 | [correct_detection.py](../src/metrics/correct_detection.py) | score = (TP − FP)/N，每個窗外警報各算一次 FP | 不是標準指標，文獻不採用；只能當內部參考 |
| 8 | [src/preprocessing.py:45](../src/preprocessing.py#L45)、[src/pipeline.py:385](../src/pipeline.py#L385) | 誤差訊號是 \|y − ŷ\| | 多類別時錯誤的「大小」取決於類別編號。ECPF 路徑的 `extract_signal("error")` 已經改用 0/1，但 meta-detector、Type-LDD 和 recurring 用的 buffer 誤差還沒改 |
| 9 | 所有輸出 | 沒有 no-change / majority 基準線，也沒有 Kappa-M、Kappa-T | Electricity、Covertype、INSECTS 的文獻都要求附上這些 |
| 10 | 各 runner | 各自用 print、events.csv 或 dict 輸出，欄位都不一樣 | 無法一次跑所有資料集並彙整結果 |

### 7.2 各資料集需要配合的設定

| 資料集 | 要開啟或調整的地方 |
|---|---|
| electricity | 沒有 GT，偵測欄位輸出 `null`。須輸出 no-change accuracy 和 κ_T |
| airlines、covertype | 輸出 `truncated: true`。要和文獻比 accuracy 時改用全長資料（建議全長檔放在 `_raw/`，不進 git） |
| INSECTS | 另外輸出 sliding-window 1000 的 accuracy（對齊 Souza Table 5）；GT 是單點 `[t, t]`，須指定 δ_max（建議 1000）；`incremental_balanced` 的 GT 是空的，偵測欄位為 `null` |
| injected | δ_max 依 Cerqueira 設定：electricity、covertype 為 2500，gas 為 1500。F1 用 Cerqueira 程式碼的計分（窗內每次警報都算 TP），另附 `episode_recall`。和論文比時 trial 數要補到 50 |
| synthetic | 多個漂移時用相同的 F1 定義，δ_max 建議 1000（等於 gradual 寬度） |
| 所有多類別資料 | 誤差一律用 0/1 loss；不輸出 MAE，改輸出 accuracy 和 macro-F1 |

### 7.3 統一輸出格式（建議）

每次執行（一條串流 × 一組設定）輸出**一列** JSON 或 CSV，欄位固定；沒有資料的欄位填 `null`：

```text
# 識別
dataset, group(real|insects|injected|synthetic), task(binary|multi|regression),
inject_method, drift_kind(abrupt|gradual|sudden|incremental|recurring), g_id, seed,
n_samples, truncated, warm_start, system_config(名稱 + hash)

# 預測（任務為分類時）
acc_prequential            # 整條串流，含 warm-start（和文獻同口徑）
acc_post_warmup            # 保留舊口徑，方便和過去的結果比較
acc_window1000_mean        # 對齊 INSECTS 的 Souza 表
kappa, kappa_m, kappa_t, macro_f1
baseline_no_change_acc, baseline_majority_acc
# 預測（任務為迴歸時）
mae, rmse

# 偵測（有 GT 才填）
n_gt, n_alerts, delta_max,
tp, fp, fn, precision, recall, f1,   # Cerqueira 程式碼定義：窗 [d_s, d_s + δ_max]，窗內每次警報都算 TP
episode_recall,                      # 每個漂移最多算 1 次
mdt, ndt, far, ar,
*_paper_window                       # 正文的窗 [d_s, d_e + δ_max]
cd_score_legacy                      # 舊的 (TP − FP)/N，只當內部參考

# 成本
runtime_s, peak_mem_mb
```

**已實作（2026-10-12）：**
- 評估器：[src/metrics/evaluate_run.py](../src/metrics/evaluate_run.py)，校準測試在 [tests/test_evaluate_run.py](../tests/test_evaluate_run.py)（對照 MOA 的計算方式、River、Cerqueira 的範例，以及 electricity no-change = 85.33%）。
- 資料集登錄表：[configs/datasets_0921.json](../configs/datasets_0921.json)；系統設定：`configs/presets/`。
- 統一 runner：[scripts/run_benchmark.py](../scripts/run_benchmark.py)，會存逐筆紀錄，`--reeval` 可在指標修正後直接重算。支援即時產生的論文版 injected 資料（`injected_paper_*`）和只偵測模式（`kind: "detector"` 的 preset，例如 `det_adwin`）。
- 全長資料：`airlines_full`、`covertype_full`（`prepare_all.py --full` 產生）。
- 彙整與統計：[scripts/compare_sota.py](../scripts/compare_sota.py)，輸出 mean ± std、95% CI、injected 每格合併指標，以及 Friedman + Nemenyi、Wilcoxon（Holm 校正）。
- 尚未改寫：main.py、run_ecpf_recurring.py 和各個 `scripts/experiment_*` 仍用各自的算法，和文獻比較時請改用 runner。

---

## 8. 要不要刪資料集

判斷標準有三條：**(a) 有沒有可比的文獻 SOTA、(b) 任務類型是否和主線（分類 + 漂移偵測）一致、(c) 能不能用統一的指標評估。**

| 資料集 | 建議 | 理由 |
|---|---|---|
| **ai4i2020**（real 和 injected 兩邊） | 🗑️ **移除** | 故障率 3.4%，accuracy 沒有意義；只有 10k 筆；沒有串流 benchmark；也不在 Cerqueira 的資料集中。三條都不符合 |
| **metro_interstate_traffic、bike_sharing**（real/regression） | 🗑️ **移除（或移到封存區）** | 任務是迴歸，指標無法和分類統一；也沒有找到串流 SOTA |
| **synthetic/regression（Friedman）** | ⚠️ 看情況 | 如果系統主線只做分類，就和上一列一起封存；如果還要保留迴歸能力展示，就留下 |
| **airlines**（injected） | ⚠️ 可移除 | Cerqueira 沒用這個資料集，沒有偵測基準可比 |
| **gas_sensor_drift** | ✅ **建議保留** | 它雖然沒有 accuracy SOTA，卻是 Cerqueira 7 個資料集之一（§5.3 有逐格基準），而且是 injected 中僅有的 3 個能直接比的資料集之一。刪掉它，多類別的偵測比較就只剩 covertype |
| electricity、covertype、INSECTS | ✅ 保留 | 主要用來宣稱 SOTA |
| airlines（real） | ✅ 保留 | 有 accuracy SOTA，但須補全長版本 |

**整理後的主線：**
- **real**：electricity、airlines、covertype、gas_sensor_drift
- **insects**：5 個版本
- **injected**：electricity、covertype、gas_sensor_drift（可再加 airlines）× 4 種方法 × abrupt/gradual
- **synthetic**：binary 和 multi_classification

全部是分類任務，所以 §7.3 的欄位可以全部共用。

---

## 參考文獻
- Aspis, Cajas Ordoñez, Suárez-Cetrulo, Simón Carbajo. *DriftMoE: A Mixture of Experts Approach to Handle Concept Drifts.* arXiv:2507.18464, 2025. https://arxiv.org/abs/2507.18464
- Abadifard et al. *DynED: Dynamic Ensemble Diversification in Data Stream Classification.* arXiv:2308.10807, 2023. https://arxiv.org/abs/2308.10807
- Anderson, Koh, Dobbie, Lensen. *Recurring Concept Meta-learning for Evolving Data Streams* (ECPF). arXiv:1905.08848. https://arxiv.org/abs/1905.08848
- Cerqueira, Gomes, Heyden, Pfahringer, Bifet. *A Framework for Evaluating and Benchmarking Concept Drift Detection Methods.* KDD 2026, arXiv:2606.07789. https://arxiv.org/abs/2606.07789 ；結果：https://github.com/vcerqueira/experiments-drift_evaluation
- Lourenço et al. *In-context learning of evolving data streams with tabular foundational models.* arXiv:2502.16840, 2025. https://arxiv.org/abs/2502.16840
- Minato, Popineau, Rimmel, Doan. *The Blind Spot Paradox: When Adaptive Classifiers Defeat Drift Detectors.* arXiv:2610.05853, 2026. https://arxiv.org/abs/2610.05853
- Montiel et al. *Adaptive XGBoost for Evolving Data Streams.* IJCNN 2020, arXiv:2005.07353. https://arxiv.org/abs/2005.07353
- Prashanth et al. *Leveraging Safe and Secure AI for Predictive Maintenance of Mechanical Devices Using Incremental Learning and Drift Detection.* CMC 83(3), 2025. doi:10.32604/cmc.2025.060881
- Read. *Concept-drifting Data Streams are Time Series; The Case for Continuous Adaptation.* arXiv:1810.02266. https://arxiv.org/abs/1810.02266
- Souza, dos Reis, Maletzke, Batista. *Challenges in Benchmarking Stream Learning Algorithms with Real-world Data.* DMKD 2020, arXiv:2005.00113. https://arxiv.org/abs/2005.00113
- Verma et al. *Rethinking Tabular Foundation Models On Data Streams.* arXiv:2610.05352, 2026. https://arxiv.org/abs/2610.05352
- Zhang & Zhang. *Domain Adaptation Extreme Learning Machines for Drift Compensation in E-nose Systems.* IEEE TIM 2015, arXiv:1505.06405. https://arxiv.org/abs/1505.06405
- Žliobaitė. *How good is the Electricity benchmark for evaluating concept drift adaptation.* arXiv:1301.3524, 2013. https://arxiv.org/abs/1301.3524
