# E0 預註冊：ADWIN 原生切點方向的被動量測

**登記日期：** 2026-09-27　**狀態：** 已登記，未執行
**登記時點：** 以本文件第一次 commit 為準。E0 的任何程式碼（含儀器與分析腳本）都不得早於這個 commit 執行。之後若需修改，只能以附錄形式追加並註明日期，不得改寫本文的判準。
**上游：** 調查報告 `docs_myself/reports/ADWIN 改善誤讀 解法調查.md`（本機）、`docs/ECPF_迴歸側FP診斷_研究報告.md`、`docs/ECPF_多類別偵測_五實驗系列.md`。

---

## 一、要回答的問題

E1（ADWIN 原生方向閘，MOA `ADWINChangeDetector` 語意）的機制前提是：**誤報（FP）的確認主要由「切窗後估計值沒有上升」的切點觸發，真實命中（TP）則主要由上升切點觸發。** E0 在不改變任何決策的前提下量測這個前提。

E0 是 E1 的**必要條件檢驗**，不是 E1 效果量的預測。被吞掉的下降切點會保留切窗後的視窗，改變之後的整條觸發軌跡；這種閉環效應，開環量測看不到。前例是 P3：Joe 單樹的 FP 實際降了 68%，開環的固定尺度反事實只預測 8%。E1 的效果量只能由 E1 本身回答。

## 二、量測定義（儀器）

**原生方向。** 對某一臂在第 t 步的 `update(x)`：

- 更新前讀取 `est_b = estimation`、`w_b = width`、`tot_b = total`。
- 更新後若 `drift_detected` 為真，稱為一次**觸發**，讀取 `est_a`、`w_a`、`tot_a`。
- **方向 = 上升，若 est_a > est_b；否則 = 下降。** 相等歸為下降，與 MOA 的嚴格 `>` 一致。

**切掉的舊子窗與保留的新子窗。** μ_W1 = est_a（寬 w_a）；μ_W0 = (tot_b + x − tot_a) / (w_b + 1 − w_a)。μ_W1 − μ_W0 的符號用作交叉檢查（I2）。

**記錄範圍。** 兩臂的每一次觸發都記錄：步數 t、臂別（warning／drift）、est_b、est_a、w_b、w_a、tot_b、tot_a、x，以及 adapter 自行鏡像的 river tick（見 I5）。每個確認事件連結兩次觸發：**開啟該 warning 的 warning 臂觸發**，與**促成確認的 drift 臂觸發**。warning 未開啟時的 drift 臂觸發不產生確認，但會重建兩臂，另記為**丟棄觸發**。

**主要端點。** 每個確認事件的方向，定義為**促成確認的那次 drift 臂觸發的原生方向**。warning 開啟的方向是次要端點（M4）。

## 三、被動性與儀器有效性

以下全部通過，才可判讀任何結果。

| 代號 | 檢查 | 通過條件 |
|---|---|---|
| I0 | 被動性 | 儀器只讀取 ADWIN 的屬性，不寫入任何決策會讀到的狀態；旗標預設關閉 |
| I1 | 視窗寬度 | 每次觸發的 w_b，等於該臂自上次重建以來、本次更新之前的更新次數（100%）。依據：基線路徑中任何切點都會觸發，並使視窗被整窗重建（drift 臂由 `update_values`，warning 臂由 river 在下一次更新時的 `_reset()`），所以寬度只可能等於更新次數 |
| I2 | 方向交叉檢查 | sign(est_a − est_b) 與 sign(μ_W1 − μ_W0) 一致的比例 ≥ 99%；不一致者逐筆列出 |
| I3 | 逐位元一致 | 每個家族至少一組「記錄開／關」成對執行，偵測序列（warning_t, confirmation_t）、換將步數、MAE 或準確率逐位元相同。其餘執行與封存比對：迴歸比對 `detections.csv` 逐列相同；多類別比對 `results.csv` 的 n_events／tp／fp／cd_score／delay／quality_value 完全相同；二元比對 `binary_buffer_probe` 紀錄的確認步數與 buffer_len |
| I4 | binary byte gate | 三種訊號模式在 `recurring_sud_sea100k_g00` 跑 16000 步，事件 CSV 與改動前逐位元相同 |
| I5 | 評估時點 | river 0.23.0 只在 tick % 32 == 0 且寬度 > grace_period 時評估切點（`adwin_c.pyx` 的 `update()`）。每次觸發時，adapter 鏡像的 tick 必須符合這個條件（100%），這同時驗證 M1 的相位計算 |

任何一項失敗：不判讀結果，修正儀器後重跑；本文件的判準不因此修改。**若封存無法重現**（例如 08 月之後、旗標預設關閉的改動影響了多類別路徑），先用現行程式、記錄關閉重跑，建立新的基準並寫下差異原因；E0 改以「記錄開／關」成對比對作為 I3。

## 四、資料與設定矩陣

一律使用既有基線設定，不加任何處方。迴歸的 P3（正規化器隨確認重置）例外，它本來就是迴歸的比較基線。

| 家族 | 串流 | 學習器／設定 | 步數 | 封存對照 |
|---|---|---|---|---|
| B 二元 | 與 `outputs/binary_buffer_probe` 相同的 3 條 SEA（sudden／gradual／recurring） | ht、hf10 | 30,000 | `binary_buffer_probe/*.txt` |
| MC-syn 多類別合成 | mc3／mc5 × sudden／gradual／recurring，共 6 條（20k） | hf10 遮罩（sqrt）、hf10 全特徵（all） | 同封存 | `outputs/mask_synth/results.csv` |
| MC-RBF 多類別 RBF | Joe RBF g00 × {sudden, gradual} × {low, medium, high}，共 6 條 | hf10 sqrt、hf10 all | 同封存 | `outputs/mask_joe/results.csv` |
| REG-syn 迴歸合成 | reg_sudden／gradual／recurring_20k，共 3 條 | htr-nr、hfr-nr | 全長 | `outputs/regression_fp_p3_synth`、`outputs/regression_fp_ref_synth` |
| REG-Joe 迴歸 Joe | Joe Friedman sudden 6 條（與 P3 Joe 批相同） | htr-nr、hfr-nr | 全長 | `outputs/regression_fp_p3_joe_htr`、`_hfr` |

共同設定：`ecpf_signal_mode="dual_adwin"`，兩臂訊號皆為 error，`ecpf_detector_min_instances=30`，`detector_delta=0.05`、`detector_delta_w=0.1`（現行預設）；warning 逾時、冷卻期、方向閘、P2 全部關閉。

## 五、事件標籤（沿用，不改）

- 標籤一律由 `scripts/diagnose_regression_fp.py` 的 `classify()` 產生：hit、echo_inwin、echo（命中之 GT 起點後 `ECHO_GAP = 3000` 步內）、orphan。`ECHO_GAP`、`SWAP_NEAR = 600`、`PERTURBATION` 維持現值。
- **FP = echo + orphan。** echo_inwin 不是 FP，另列。
- 「安裝更差」沿用 `scripts/analyze_regression_fp.py` 的 install_ratio：安裝後 200 步的原始 MAE ÷ 安裝前 200 步，> 1.5 為更差。只用於迴歸（M2）。
- 同一家族內的學習器／設定分開列表，但判準以家族為單位。

## 六、主要判準

### D1：E1 的 go／no-go

對每個家族計算 **p_dec(FP) = FP 確認中原生方向為下降的比例**。

- **GO**：全部家族合併的 p_dec(FP) ≥ 0.60，而且每個 FP ≥ 10 的家族各自 ≥ 0.50。
- **部分 GO**：合併 ≥ 0.60，但有 FP ≥ 10 的家族 < 0.50。E1 照做（同一個旗標），但該家族在 E1 登記為「預測無效」。若 E1 在該家族的 FP 降幅超過 20%，代表 E0 漏看了閉環效應，必須回頭解釋，不能算成 E1 的機制功勞。
- **NO-GO**：合併 < 0.60。E1 不當主臂；下一步改為 E2（凍結參照對 P3 基線，照 v4 設計），E1 最多作為診斷。
- FP < 10 的家族只報告，不參與判定。

依據：E1 只能直接吸收由下降切點觸發的 FP。調查報告為 E1 建議的總體目標是合成 FP −40%、Joe −30%；0.60 的門檻為閉環再觸發保留了餘裕。逐家族 0.50 的下限，是「聚合指標藏形狀」這條教訓的防線。

### D2：E1 會放棄的 TP

**TP_dec(f) = 家族 f 中，原生方向為下降的 hit 數。**

- 若合併 TP_dec ≥ max(2, 總 hit 數 × 10%)，或任一家族 TP_dec ≥ 2：**E2 與 E1 同輪執行。** 凍結參照保有雙向語意，它相對 E1 唯一的優勢正好落在這些事件上，兩者必須在同一批執行上比較。
- 否則照原順序，E1 之後才做 E2。
- 不論哪種情況，**E1 的 TP 損失容許量登記為每家族 max(1, TP_dec(f))。**
- 所有下降觸發的 hit 都逐筆列出（步數、距 GT 起點的距離、距上一次換將的距離），供人工檢視是否為「剛好落在 GT 窗內的改善觸發」。這份清單不影響判定。

## 七、次要量測

| 代號 | 量測 | 登記的預期（依讀碼推論） | 決策作用 |
|---|---|---|---|
| M1 相位與領先 | ① 每個確認時，兩臂鏡像 tick 是否同相（差 ≡ 0 mod 32）。② lead = 確認步 − warning 開啟步。③ 影子 warning 臂：與 warning 臂同 δ、`clock = 1`、與真 warning 臂同步重建、不接任何決策；記錄它在每個 lead = 0 的確認之前第一次觸發的步數，得 shadow_lead | ① 同相 = 100%（逾時、冷卻、閘全關時，兩臂只會一起重建，而 warning 臂在 river 內部重設時仍落在同一格上）。② 不登記 | ① 若 < 100%，「兩臂相位鎖定」的讀碼推論錯誤，照實記錄。③ 若 lead = 0 的確認中有 ≥ 50% 的 shadow_lead ≥ 16：評估時點是 1 筆緩衝的綁定約束，「warning 臂 `clock = 1`」排為 E3 之前的零成本診斷；否則綁定約束在門檻本身，調查報告的 ⑧ 撤下 |
| M2 連鎖 | 迴歸家族的「連鎖候選 FP」：緊接在前的確認 install_ratio > 1.5，而且發生在下一個 GT 起點之前。量它的原生方向 | 下降 ≥ 50% | 合併候選數 ≥ 8 才判定。< 50%：E3（保守安裝）無條件排在 E1 之後；≥ 50%：E3 維持「E1 後仍有連鎖才做」 |
| M3 正規化器追趕 | 迴歸家族中原生上升的 FP：用 w_b、w_a 重建 W0／W1，計算原始 \|殘差\| 的平均。「追趕」= 原始 μ_W1 ≤ 1.05 × 原始 μ_W0（正規化值上升、原始值沒升） | 不登記 | 追趕事件 ≥ 5 且占迴歸上升 FP ≥ 30%：這批事件登記為 E2 假說 H1 的目標集合（凍結參照應移除、E1 移不掉） |
| M4 warning 開啟 | 所有 warning 的開啟方向；下降開啟的 warning 所造成的訓練暫停總步數（開啟到確認；`pipeline.py` 在 warning 期間提前返回，leader 與 shadow 都不訓練） | 不登記 | 若某家族下降開啟造成的暫停總步數 ≥ 串流長度的 5%，E1 登記次要預測「該家族準確率／MAE 不降反升」 |
| M5 丟棄觸發 | warning 未開時的 drift 臂觸發次數與方向 | 不登記 | 只描述基線有多少次「因下降而清空證據」，不影響判定 |

## 八、判讀順序與禁止事項

1. I0–I5 全部通過。
2. 分析腳本機械化輸出 D1、D2 判定，不經人工調整。
3. M1–M5 依第七節的規則輸出決策。
4. 所有家族、所有設定都要報告，包括不利的結果。

**禁止：** 看到資料後調整任何門檻；刪除串流或家族；在 `classify()` 之外重新標籤；把 echo_inwin 併入 FP；以「理由充分」為名，把個別事件改判方向。

## 九、產出

- **執行腳本：** `scripts/probe_native_direction.py`（待寫），重用 `diagnose_regression_fp.run()` 與 `classify()`，不另寫標籤邏輯。
- **分析腳本：** `scripts/analyze_native_direction.py`（待寫），依第六、七節機械化輸出判定。
- **輸出目錄：** `outputs/e0_native_direction/`。內容包括每次執行的觸發紀錄（fires.csv）、確認事件與觸發的連結（confirmations.csv）、表 T1–T6、判定摘要（verdict.md）。
- **表：** T1 家族 × 標籤 × 原生方向；T2 D1／D2 判定；T3 相位、lead 與 shadow_lead（M1）；T4 連鎖候選（M2）；T5 迴歸上升 FP 的原始與正規化對照（M3）；T6 warning 開啟方向、暫停步數與丟棄觸發（M4、M5）。
- **成本預估：** 二元、多類別合成與迴歸合成合計約數十分鐘；Joe 迴歸與 RBF（每條 100k 步）需數小時，背景執行。

## 十、E0 如何決定 E1 的登記

E1 另立預註冊文件。E0 的結果決定其中五項：

1. 哪些家族有 FP 降幅目標（p_dec ≥ 0.50），哪些登記為「預測無效」（D1）。
2. 每家族的 TP 損失容許量 max(1, TP_dec(f))（D2）。
3. E2 是否與 E1 同輪（D2）。
4. E3 是否無條件排在 E1 之後（M2），以及 E2 假說 H1 的目標集合（M3）。
5. E1 的準確率／MAE 次要預測（M4）。

---

## 附錄 A（2026-09-27，執行前、未看任何方向資料）：儀器改為離線重播

判準（第五至八節）一字未改，只換量測方法，理由是更簡單、而且不必動 `src/`。

- **方法。** 基線路徑中，任何切點都會觸發；drift 臂觸發會重建兩臂；warning 臂觸發後 river 會在下一次更新重設該臂。所以每一臂的視窗恰好是「上次重建以來的全部 err」。tracer 已逐步記錄 err 與兩臂的觸發旗標，用同參數的 river ADWIN（warning δ = 0.1、drift δ = 0.05、grace_period = 30、clock = 32）重播，即可在每次觸發時讀出 est_b、est_a、w_b、w_a。M1 的影子臂同樣離線重播（clock = 1，隨真 warning 臂一起重建）。
- **有效性檢查取代 I0–I5。** 重播必須逐步重現所有記錄到的 warning／drift 觸發（不符數 = 0）；每次觸發的 w_b 必須等於上次重建以來的步數（不符數 = 0）；每個確認都必須連得到它的 drift 觸發與 warning 開啟觸發。任何一項不為 0，就不判讀任何結果。因為沒有改動 `src/`，I0、I3（記錄開／關）與 I4（byte gate）不再需要。M1 ①「兩臂同相」在這些重建規則下按構造成立，不另外量。
- **資料。** 迴歸兩個家族直接使用封存的 trace 與 `detections_labelled.csv`（`regression_fp_p3_synth`、`regression_fp_p3_joe_htr`、`regression_fp_p3_joe_hfr`，設定 htr-nr、hfr-nr）。二元與多類別沒有封存 trace，以 `diagnose_regression_fp.run()` 依第四節設定重跑，步數與封存相同（多類別 20,000、二元 30,000）。
- **腳本。** `scripts/analyze_native_direction.py` 一支，`--run` 重跑二元與多類別，接著機械化輸出第六、七節的判定。
- **直譯器（執行前發現）。** 封存的執行用的是 Anaconda 的 `python`（river 0.21.2），不是 repo 的 `.venv`（river 0.23.0）。兩版 ADWIN 在同一輸入上的觸發時點不同：reg_gradual hfr-nr 的第一次觸發，0.21.2 在 6055（與記錄相符），0.23.0 在 5959。E0 的重播與重跑一律使用 river 0.21.2。在這個條件下，重播在全部 18 次封存的迴歸執行上重現了所有記錄（95 個確認；觸發不符 0、寬度不符 0、未連結 0）。
