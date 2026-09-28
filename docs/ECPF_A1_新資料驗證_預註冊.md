# A1 預註冊：新資料集驗證（注入 electricity、INSECTS）

**登記：** 2026-09-28，以本文件的 commit 為準；本 commit 同時納入 A1 用到的資料子集。A1 的任何執行都在這個 commit 之後。
**目的：** 檢驗我們的修正在前面各輪從未用過的資料上是否仍然有效。修正指 E1（river ADWIN 核心＋MOA 方向規則）與 E2-k500（凍結參照，500 步後再凍結）。
**範圍：** 這是新資料驗證的第一階段。ai4i2020 因正類只有 3.4% 而排除；real_dataset 沒有 GT，放到最後。

## 資料（取自 origin/main 的 `data/dataset_0921/`，只取本輪用到的檔案，143 MB）

| 家族 | 串流 | 學習器 | 步數 |
|---|---|---|---|
| **INJ-elec** | 注入 electricity：{class_prior, label_swap, feature_permutation, feature_filtering} × {abrupt, gradual} × g00–g02，共 24 條；每條只有一個已知漂移 | ht、hf10（與 B 家族相同） | 全長 |
| **INS** | INSECTS balanced 5 個變體（33 特徵、6 類） | hf10 遮罩（sqrt） | 全長 |

- **注入集的特性：** 注入前先把資料打亂順序，所以**漂移前的整段都是獨立同分布的平穩資料**。這段裡的確認不可能是真漂移，只可能來自學習器自己的改善或雜訊。
- **INSECTS 的 GT：** abrupt 有 5 個點；incremental_abrupt_reoccurring 與 incremental_reoccurring 各 2 個點；incremental_gradual 1 個點；incremental 沒有離散點。

## 臂與設定

- **三臂：** base（雙向 dual ADWIN）、E1（`ecpf_adwin_one_sided`）、E2-k500（`ecpf_reference_signal`，暖機 500）。
- **設定：** 與 E0–E9 相同：δ 0.05／0.1、warning 期間暫停訓練、river 0.21.2。不合併 `main` 的程式改動。
- `src/` 不改動，所以不需要 byte gate。

## 計分

- 標籤一律用 `classify()`；計分窗 1000 步為主、3000 步為輔。
- **注入集另計「漂移前 FP」：** warning 開啟時刻早於 GT 起點的確認數。
- 每條注入串流只有一個 GT，所以每一次執行的 TP 只會是 0 或 1。

## 判準

- **P1（機制，INJ-elec）：** 合計的漂移前 FP，E1 與 E2-k500 各自 ≤ base 的 30%。base 合計至少要有 10 個，這條才可判定。
- **P2（召回，INJ-elec）：** 合計 TP@3000 ≥ base 的 90%。E1、E2-k500 分別判定。
- **P3（漸變，INJ-elec 的 gradual 子集）：** E2-k500 的 TP@3000 ≥ E1 的 TP@3000。這是 H2 在新資料上的檢驗。
- **P4（INSECTS abrupt）：** E2-k500 的 FP@3000 ≤ base，而且 E2-k500 的 TP@3000 ≥ E1。樣本數小，只當作支持性證據。
- **結論規則：**
  - E2-k500 的 P1 與 P2 都成立：「E2-k500 在新資料上成立」；
  - E1 的 P1 與 P2 都成立：「E1 在新資料上成立」；
  - P3、P4 單獨報告。
- **照常報告：** 準確率；各注入方法分開的偵測率（`feature_filtering` 是只改 P(X) 的虛擬漂移，不設門檻）；INSECTS 其他變體的準確率與偵測數。incremental 段落裡的 FP 不好定義，另外註明。
