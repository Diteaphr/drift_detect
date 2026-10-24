# I2 預註冊：合成多類別上的 ③④ 消融，以及 warning 期間訓練（兩個資料集）

**登記：** 2026-10-24，以本文件的 commit 為準。I2 的任何執行都在這個 commit 之後。
**目的：**
1. **A 部分：** 把 I1 的三階消融（baseT → E2k500T → E10bFT）搬到合成多類別的 40 條串流上，讓兩個資料集用同一套臂、學習器與計分。
2. **W 部分：** 在 INSECTS 五條與合成多類別 40 條上，檢查「warning 期間照常訓練 leader」對三個臂各有什麼影響。

**資料性質：兩個資料集都已經看過。** INSECTS 見 I1 第二節；合成多類別 40 條在 A2、E10–E14（SYN2-MC 組）與 DET3、DET4 都用過，主方法就是在這批資料上設計、判定的。本輪結果只能寫成「在看過的資料上」，不能當成可推廣的證據，也不改變 E14 的主方法結論。

## 一、前置定義

### 新元件：warning 期間訓練（L）

- **現況：** warning 一開啟，pipeline 就在訓練之前提早返回；樣本只進 buffer，leader 與 shadow 都不學，直到確認或 1000 步逾時（逾時時 buffer 丟棄）。
- **L 的定義：** warning 開啟期間，每一步照常讓 ECPF 訓練 leader 與 shadow（`ECPF.on_stream_instance`），並照常記錄對決。buffer 的收集、偵測器、參照與守衛都不變。
- **來源：** 移植 main 的 f34933e（`ecpf_learn_during_warning`），呼叫點與內容相同：四個 warning 期間的提早返回處都加。差別只在預設值：本分支預設 **關閉**，維持所有既有結果不變。
- **注意：** E10bFT 的主偵測器讀凍結參照，leader 學不學不影響它；但 leader 守衛讀 leader 自己的損失，L 會讓守衛看到的是持續適應中的 leader。

### 臂

| 臂 | 元件 | 旗標 |
|---|---|---|
| baseT | 無 | `ecpf_detector_warning_timeout=1000` |
| E2k500T | ③ + ④a | baseT + `ecpf_reference_signal`、`ecpf_reference_warmup=500` |
| E10bFT | ③ + ④a + ④b | E2k500T + `ecpf_leader_guard`、`ecpf_guard_frozen_scale=500` |
| baseTL / E2k500TL / E10bFTL | 同上 + L | 上列各臂 + `ecpf_learn_during_warning=True` |

- ③、④a、④b 的定義與 C3、C4 兩個對比同 I1 第一節。③ 與 ④a 依舊綁在 C3 裡。
- **W 對比：** WX = XL 對 X，X ∈ {baseT, E2k500T, E10bFT}。

### 指標

同 I1：準確率（prequential）、TP@1000／3000、FP@3000、超額命中、確認次數、守衛觸發的確認數、最大參照年齡、warning 開啟步數（無 L 的臂 = 暫停訓練步數）、命中延遲中位數。

### 資料

| 資料集 | 串流 | 步數 | 學習器 |
|---|---|---|---|
| INSECTS | 五個 balanced 變體（同 I1） | 全長 | hf10 遮罩（主）、ht（次） |
| 合成多類別 | origin/main d29bb70 `data/dataset_0921/synthetic_dataset/multi_classification/`，RandomRBF 4 類，sudden、gradual、incremental 各 g00–g09；recurring g00–g09（Joe 隨機混合：sudden 3、gradual 5、incremental 2 條） | 100,000 | hf10 遮罩（主）、ht（次） |

- 合成資料的漂移型別依 recurring 的 manifest 拆成使用者指定的六類：sudden、gradual、incremental、recurring·sudden、recurring·gradual、recurring·incremental。
- GT 規則同 A2：起點落在前 200 步的 GT 不計分。
- 檔案雜湊在執行前與本機檔案比對（node2 快照的 SHA256 清單）。

## 二、已經看過的結果

- **INSECTS：** I1 的全部結果（`outputs/e1_e2/i1_verdict.md`），以及 I1 第二節列出的 A1、E10、DET3、DET4。
- **合成多類別（hf10 遮罩，各輪不同的 g）：** E11 g02–g03 E2k500T 對 baseT：FP 7 對 90，超額命中 51.1 對 32.1。E12 g04–g05：超額命中 E10bT 53.9 > E2k500T 41.1 > baseT 34.3。E14 g08–g09 E10bFT 對 baseT：FP 8 對 73，超額命中 51.9 對 38.2，準確率 .7441 對 .7260。A2 g00 的 E2k500（無逾時）FP 4、TP 31（baseT 前身 base FP 56、TP 35）。
- **warning 期間訓練：** main f34933e 的提交說明（18 對執行，平均 +1.74 個百分點，誤報 163 → 155）；Shawn 的 DET3 F-D1（`lw1`）對 P-H：準確率 +0.28 個百分點，偵測持平。這兩個都不是在本 harness 的三個臂上量的。
- **沒看過的：** 本 harness 上三臂在合成 40 條上的同輪結果；任何 L 臂的結果。

## 三、背景與假說

- **A 部分的理由：** I1 只有 10 個 GT 點；合成 40 條有數百個 GT 點，可以讓 C3、C4 的方向在同一套設定下更穩定。各輪 SYN2-MC 的結果分散在不同的 g 與不同的臂組合上，沒有一張三階並列的表。
- **W 部分的理由：** 主方法暫停訓練的步數比 HDDM-A 多約 8 倍（DET3），逾時只限制單次暫停的長度。L 直接取消暫停，是否同時傷害偵測需要量。
- **假說：**
  - **H3、H4：** 同 I1。合成上預期 C3 誤報大減、召回不掉；C4 召回比 E2k500T 高（E12）。
  - **HW-acc：** L 提高準確率，對 E10bFT 的提升最多（它暫停最多）。
  - **HW-det：** baseT、E2k500T 的偵測幾乎不受影響；E10bFT 的守衛可能少觸發，召回略降。

## 四、判讀規則

**A0（有效性）：** 所有臂的確認間隔都 ≤ 1001 步；不成立則本輪無效。

### A 部分（合成 40 條；hf10 主讀法，ht 為 S1）

FP 與超額命中為 40 條合計；準確率為 40 條平均。

- **R3a：** E2k500T 的 FP@3000 ≤ baseT 的 50%（baseT < 6 時不可判定）。
- **R3b：** E2k500T 的超額命中 ≥ baseT 的 90%。
- **R3c：** E2k500T 平均準確率 ≥ baseT − 0.01。
- **C3 讀法：** R3a、R3b 都成立 → 「③（含 ④a）重現」；R3c 不過另外寫成準確率代價。
- **R4c：** E10bFT 的 FP@3000 ≤ baseT 的 50%，而且超額命中 ≥ E2k500T 的 90%。
- **R4e：** E10bFT 的超額命中 > E2k500T。
- **R4d：** E10bFT 平均準確率 ≥ E2k500T − 0.01。
- **C4 讀法：** R4c、R4e 都成立 → 「④b 在合成上提高召回，且不吃掉 ③ 的誤報優勢」。
- **R-all：** E10bFT 對 baseT，用 E14 的 P3、P4 規則。
- **描述（不判定）：** 六種漂移型別各自的三臂表；GT 點按 E2k500T 的參照年齡（<2k、2–10k、≥10k）分組的命中數（E12 的參照過時指標）。

### W 部分（兩個資料集分開判；hf10 主讀法，ht 為 S1）

對每個 X ∈ {baseT, E2k500T, E10bFT}，比較 XL 對 X（同串流、同學習器配對）：

- **W-acc：** 每條串流的準確率差 Δ = XL − X。平均 Δ ≥ +0.002 且超過一半的串流 Δ > 0 → 「提升」；平均 Δ ≤ −0.002 且超過一半 Δ < 0 → 「下降」；其他 → 「持平」。
- **W-det：** XL 的合計 FP@3000 ≤ X 的 1.1 倍，而且合計超額命中 ≥ X 的 90% → 「偵測不受影響」；否則列出哪一條不過。INSECTS 的 FP 與超額命中只用 4 條有 GT 的串流。
- **WX 讀法：** W-acc 不是「下降」且 W-det「不受影響」→ 「L 可以加到 X 上（看過的資料上）」。
- **主讀法關注 W(E10bFT)。** 若成立，下一步才是在新資料上登記一輪把 L 加進主方法；本輪不改主方法。
- **描述：** 每臂 warning 開啟步數、E10bFT 與 E10bFTL 的守衛觸發確認數。

### 事前預測（不影響判讀）

- **A 部分：** C3 成立、R3c 過；C4 的 R4e 成立（E12），R4c 可能因 E10bFT 的守衛誤報而接近門檻（I1 的 hf10 上 E10bFT 的 FP 比 E2k500T 多 23%）。
- **W-acc：** 合成上三臂都「提升」或「持平」，E10bFT 的 Δ 最大；INSECTS 上不確定（I1 中 hf10 E10bFT 只暫停約 2.5–5.5% 的步數）。
- **W-det：** baseT、E2k500T 不受影響；E10bFT 不確定，守衛觸發可能變少。

## 五、局限

- **資料看過：** 兩個資料集都是設計主方法時用過的資料；判讀規則與預測是知道 I1、E11–E14 的結果之後寫的。
- **單次執行：** 每條串流、每臂、每個學習器只跑一次，沒有種子重複；合成 40 條本身就是 40 個不同的種子。
- **L 只移植了 main 的寫法：** shadow 的訓練與對決記錄照 main；沒有測試別的變體（例如只訓練 leader、或逾時時把 buffer 回放給 leader）。
- **③ 與 ④a 仍綁在一起**（同 I1）。

## 六、執行計畫

- **程式：**
  - `src/config.py` 加 `ecpf_learn_during_warning: bool = False`；`src/pipeline.py` 加 `_ecpf_warning_step()`，在四個 warning 期間的提早返回處呼叫（同 f34933e）。
  - `scripts/run_e1_e2.py` 加三個 L 臂、`I2` 字典（每條合成串流一個家族 `I2-<stem>`，學習器 hf10 遮罩 + ht）、`--gate-i2`、`--analyze-i2`。INSECTS 的 W 部分用 I1 的家族與已存的三臂結果，只補三個 L 臂。
- **閘門（全部在 node2 上，正式執行前）：**
  - **G0：** 快照 SHA256 清單核對。
  - **G1：** 旗標關閉時，重跑 A1 的 `INS-abrupt` E2k500，必須與存檔逐筆相同。
  - **G2：** 旗標關閉時，重跑 I1 的 `I1-incgrad` E10bFT（hf10 + ht），必須與 I1 存檔逐筆相同（確認新程式不改變 I1 的結果，W 部分才能和 I1 的存檔配對）。
  - **G3：** 自檢：同一條串流，L 開啟時 ECPF 看過的樣本數必須多於關閉時。
- **正式執行：** INSECTS 5 家族 × 3 個 L 臂 = 15 格；合成 40 家族 × 6 臂 = 240 格；共 255 格，每格 2 個學習器，每臂只跑一次。node2 `-P 15`，INSECTS 與最長的格子先排。依 I1 的單格時間估算約 5–6 小時。
- **輸出：** `outputs/e1_e2/I1-*/<L 臂>/`、`outputs/e1_e2/I2-*/<臂>/`；判讀寫到 `outputs/e1_e2/i2_verdict.md`，照常 commit。
