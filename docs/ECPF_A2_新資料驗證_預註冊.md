# A2 預註冊：新資料集驗證（新版合成資料、注入 gas_sensor）

**登記：** 2026-09-28，以本文件的 commit 為準；本 commit 同時納入 A2 用到的資料子集。A2 的任何執行都在這個 commit 之後。
**目的：** 延續 A1，在前面各輪（E0–E9、A1）從未用過的資料上檢驗 E1 與 E2-k500。A2 補上 A1 沒有的三塊：迴歸、多類別的注入資料、10 萬步的長合成串流。
**背景：** A1 裡 INSECTS abrupt 上 E2-k500 的準確率比 base 低 2.9 個百分點。事後從 trace 診斷，91% 的差距來自兩處論文 GT 沒標的類別組成變化。E2-k500 的參照在最後一次再凍結後已經 13,634 步沒更新，損失持平，偵測器一次都沒觸發；仍在學習的 leader 誤差卻大漲。這稱為**參照過時**。所以本輪新增準確率護欄（P4），並報告參照年齡。

## 資料（取自 origin/main 的 `data/dataset_0921/`，只取本輪用到的 99 個檔，550 MB）

| 家族 | 串流 | 學習器 | 步數 |
|---|---|---|---|
| **SYN2-B** | SEA sudden、gradual、recurring_gradual（3 特徵）；hyperplane incremental（2 特徵）；皆 g00 | ht、hf10（同 B） | 100,000 |
| **SYN2-MC** | RBF4 sudden、gradual、incremental、recurring_incremental（10 特徵、4 類）；皆 g00 | hf10 遮罩（sqrt） | 100,000 |
| **SYN2-REG** | Friedman sudden、gradual、incremental、recurring_sudden（10 特徵）；皆 g00 | htr、hfr（P3 開） | 100,000 |
| **INJ-gas** | 注入 gas_sensor_drift（128 特徵、6 類）：{class_prior, label_swap, feature_permutation, feature_filtering} × {abrupt, gradual} × g00–g02，共 24 條；每條只有一個已知漂移 | hf10 遮罩（sqrt） | 全長（10,797–13,910） |

- 合成資料每條有 5–10 個 GT 漂移。
- **GT 規則：** 起點落在暖機（前 200 步）內的 GT 區間不計分。這條規則只影響 hyperplane incremental 的第一個區間 [0, 950]：串流一開始就在漂移，沒有「之前的概念」。各臂在 [200, 1950] 內的確認數照常報告。
- 注入集的特性同 A1：先打亂再注入，漂移前整段是平穩資料。

## 臂與設定

- **三臂：** base、E1（`ecpf_adwin_one_sided`）、E2-k500（`ecpf_reference_signal`，暖機 500）。
- **設定：** 與 E0–E9、A1 相同：δ 0.05／0.1、warning 期間暫停訓練、river 0.21.2；迴歸開 P3。不合併 `main` 的程式改動。
- `src/` 不改動，所以不需要 byte gate。

## 計分

- 標籤一律用 `classify()`；1000 步窗與 3000 步窗都算，判準用 3000 步窗（與 A1 相同）。
- 漂移前 FP 的定義同 A1，只用於 INJ-gas。

## 判準

- **P1（機制，INJ-gas）：** 合計的漂移前 FP，E1 與 E2-k500 各自 ≤ base 的 30%。base 合計至少要有 10 個，這條才可判定。
- **P2（召回，INJ-gas）：** 合計 TP@3000 ≥ base 的 90%。
- **P3（SYN2，B、MC、REG 三組分開判）：** FP@3000 ≤ base 的 50%，而且 TP@3000 ≥ base 的 90%。該組 base 的 FP@3000 少於 6 個時，FP 部分不可判定，只判召回。
- **P4（準確率護欄，SYN2-B、SYN2-MC、SYN2-REG、INJ-gas 四組分開判）：** 分類的平均準確率 ≥ base − 0.01；迴歸的平均 MAE ≤ base × 1.02。
- **P5（漸變，H2）：** 檔名含 gradual 或 incremental 的所有串流（含 INJ-gas 的 gradual）合計，E2-k500 的 TP@3000 ≥ E1 的 TP@3000。
- **結論規則（每臂分開、分類與迴歸分開）：**
  - 分類：P1、P2、P3-B、P3-MC，以及 SYN2-B、SYN2-MC、INJ-gas 的 P4 全部成立 →「在新資料的分類上成立」；
  - 迴歸：P3-REG 與 SYN2-REG 的 P4 都成立 →「在新資料的迴歸上成立」。E0 已預測 E1 對 Friedman 類迴歸無效（REG-Joe p_dec 0.45）；
  - P5 單獨報告。
- **照常報告：**
  - 各組的延遲中位數；INJ-gas 各注入方法分開的數字（`feature_filtering` 是只改 P(X) 的虛擬漂移，不設門檻）。
  - **參照過時的檢查：** E2-k500 參照的最大年齡。另外取 E2-k500 每次執行中「參照最後一次凍結（`ref_age` 歸零）到串流結束」的區段；區段長度 ≥ 5000 步時，報告三臂在同一區段的準確率或 MAE。
