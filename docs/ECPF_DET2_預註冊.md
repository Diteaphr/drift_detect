# DET2 預註冊：warning 期間持續學習對三種偵測器的效果

**登記：** 2026-10-13（Asia/Taipei）。本文件必須獨立提交，先於 DET2 新程式碼、重跑、smoke 及正式資料執行。DET1 的既有結果只用於鎖定研究問題與事前預測；不得依 DET2 正式結果改參數、資料或判準。後續偏離以本文件末尾「修訂」追加，不改寫原文。

**頂層問題：** 在 DET1 已鎖定的 ECPF 底座、資料與單棵 Hoeffding Tree 上，讓 leader 與 shadow 在 warning 期間繼續訓練，是否改善準確率，以及改善的代價為何？本輪把 DET1 的 lw0 結論與新的 lw1 配對比較，不宣稱是獨立外部驗證。背景來源：[DET1 預註冊](ECPF_DET1_預註冊.md)、[DET1 正式 verdict](../outputs/det1/det1_verdict.md)、[warning 持續學習變更 `f34933e`](https://github.com/Diteaphr/drift_detect/commit/f34933e)、[預設 delta 變更 `d29bb70`](https://github.com/Diteaphr/drift_detect/commit/d29bb70)。

## 鎖定三個問題與判定範圍，避免把機制觀察當勝負

1. **Q1（主要）：** 同一偵測器的 lw1 相對 lw0，是否提高全串流 prequential accuracy？改善點估計排序是否與 DET1 lw0 凍結步數排序 A1 > A4 > A3 同序？
2. **Q2：** 開啟 lw1 後，Dual ADWIN 對 HDDM-A、RDDM 的偵測品質是否追上？
3. **Q3（敏感度）：** Dual ADWIN 的 drift delta 從 DET1 的 0.05 改為 main 預設 0.01，在 lw0 下是否改變 DET1 的 A3/A4 對 A1 判定？

Q1 的準確率判定與 Q2 的 P1/P2 判定分開。凍結時間、warning 事件與 runtime 用於解釋成本，不用來更改 Q1/Q2 的門檻。

## 固定 ECPF、配對串流與七個組別，隔離 warning 訓練因子

| 項目 | 事前固定設定 |
|---|---|
| 底座與版本 | DET1 的 `ecpf_paper` 底座、單棵 `ht`、warm start 200、`river==0.21.2`；同一份資料順序、預測／訓練流程及現有 pipeline 實作 |
| 偵測器 | A1 雙向 dual ADWIN，`detector_delta_w=0.1`、`detector_delta=0.05`、timeout 0；A3 HDDM-A、A4 RDDM 的參數與 DET1 相同。A1d 唯一改動是 `detector_delta=0.01` |
| 訓練因子 | `_lw0`：`ecpf_learn_during_warning=False`；`_lw1`：`True`，leader 與 shadow 在 warning 期間照常訓練。其他設定不變 |
| injected | `injected_paper_electricity`，registry 八個 cell 各取展開順序前 20 個 generator trial，合計 160 條；GT、警報與延遲用原始 input 座標 |
| synthetic | `synthetic_multiclass` 全 40 條；E 系列曾使用，本輪是鎖參數後評估，不是新 holdout |
| INSECTS | registry 全五個 `insects_*_balanced` 各一條；其中四條非空 GT 進 Q1/Q2/Q3 的偵測計分，一條 `insects_incremental_balanced` 空 GT 只作準確率、警報數及成本描述 |
| 偵測計分 | DET1 的含端點 `[d_s,d_s+1000]` 主窗、暖機前 GT 排除、injected 前 25% 不計警報、每 GT 最多一次 episode hit；每個 run 以窗外 `FP/O` 算 `C=Σ(1−exp(−FP/O·|W_i|))`，`X=hits−C`。重疊窗依 DET1 evaluator episode ownership；`O=0` 時 X 不可估 |
| 推論 | injected／synthetic／INSECTS 三組內，以**串流為單位配對、有放回分層 bootstrap 10,000 次**，固定 seed `20261012`；保留每層原條數，同一抽樣索引同時套用兩臂。Q1 全串流 prequential accuracy 的 INSECTS 層含五條；漂移後 accuracy 與 FP/X 的 INSECTS 層只含四條有 GT 串流。CI 為 percentile 2.5／97.5，含 0（含端點）判持平。準確率每次重算分子、可計分預測數之比；FP、X 每次按 run 合計，不先平均資料組 |

| DET2 ID | preset | 正式來源與用途 |
|---|---|---|
| DET2-A1-lw0 | `det1_dual_adwin_lw0` | 通過重現閘門才沿用 DET1 正式輸出 |
| DET2-A3-lw0 | `det1_zone_hddm_a_lw0` | 同上 |
| DET2-A4-lw0 | `det1_zone_rddm_lw0` | 同上 |
| DET2-A1-lw1 | `det1_dual_adwin_lw1` | 新跑，Q1/Q2 |
| DET2-A3-lw1 | `det1_zone_hddm_a_lw1` | 新跑，Q1/Q2 |
| DET2-A4-lw1 | `det1_zone_rddm_lw1` | 新跑，Q1/Q2 |
| DET2-A1d-lw0 | 新增 `det2_dual_adwin_d001_lw0` | 新跑，只作 Q3 敏感度，不進 Q1/Q2 |

新跑 **4 × 205 = 820 次**。三個 lw0 若任一重現失敗，三組皆改在 DET2 專用根目錄重跑完整 205 條，再增 **615 次**；不得混用部分 DET1、部分 DET2 的 lw0 結果。新跑的 source/GT/stream 名稱須與 DET1 正式矩陣逐一配對。

## 以事前 CI 規則分別判 Q1、Q2，並把 Q3 留作敏感度

**主要指標。** 全串流 prequential accuracy 取 benchmark evaluator 的 `acc_prequential`，按各 run 可計分預測筆數加權；漂移後 accuracy 取每個 GT 起點後最多 1,000 個可觀測預測的正確數／預測數，重疊只計一次，被注入刪除的原始列不進分母。後者仍在所有有 GT 串流上按預測數加權。對 lw1−lw0 報點差與配對 CI；空 GT INSECTS 進全串流 accuracy，但不進漂移後 accuracy 或 FP/X。

**次要與機制指標。** FP@1000、X、episode hits、首次命中 MDT、kappa；總凍結步數（lw1 預期為 0，須以 metrics／事件核對）、warning 開啟／確認／離區關閉與串流末端截尾、確認 buffer 中位長度、runtime。每臂既報有 GT 三組偵測總和，也報含空 GT 串流的全 205 條準確率與成本。警報、開啟、關閉及截尾須守恆；不以 warning 次數代替 drift 次數。

**Q1：** 對 A1、A3、A4 各自計 `lw1−lw0` 的全 205 條、以可計分預測數加權的 prequential accuracy 差。95% CI 全正判「改善」、全負判「惡化」，其餘判「持平」。另報漂移後 accuracy、FP、X 的點差與 CI，不用它們改判主要準確率狀態；若準確率改善而 X 的 CI 全負，文字必須寫「準確率改善、偵測品質下降」。MDT、episode hits、kappa、凍結及 runtime 照報。描述性列出三臂 Δaccuracy 點估計由大到小，對照原凍結總步數 A1 **1,717,081** > A4 **462,397** > A3 **32,212**；不另設排序顯著性門檻。

**Q2：** 以 `A1-lw1 − A3-lw1`、`A1-lw1 − A4-lw1` 報差，並照 DET1 P1/P2 的有利方向判斷 Dual ADWIN：P1 需 `ΔFP` 的 CI **全負**，P2 需 `ΔX` 的 CI **全正**。兩者皆成立稱「優於／追上並超越」；兩者皆不成立且 CI 分別全正、全負稱「不如」；其餘（任一 CI 含 0，或兩條件方向相反）稱「持平／未證實追上」，並逐條照報 P1/P2 狀態，不強稱等效。另報 prequential accuracy 差與 CI。此處「追上」僅按預註冊 P1/P2 勝負，不以 accuracy 單獨判定。

**Q3：** 先比較 `A1d-lw0 − A1-lw0` 的 FP、X、prequential accuracy 點差及 CI，再以 `A3-lw0 − A1d-lw0`、`A4-lw0 − A1d-lw0` 重算 DET1 同一 P1/P2。若 DET1 原本「A3、A4 皆優於 A1」的任一對結論改變，即記為**足以改變 DET1 判定**；否則記為未改變。Q3 不納入 Q1/Q2、六格整合表的主判定。

缺少配對串流、X 不可估、正式 run 失敗且重試一次仍失敗時，相關對比標「不可判定」，列出缺漏，不刪除不利格，也不以其他資料替代。三組與型態表按 DET1 的命名規則（`abrupt/sudden`、`gradual`、`incremental`、`recurring/reoccurring`）描述；複合標籤可在多個描述層出現，但總分每串流只計一次。分層 CI 若有報告，採同樣配對抽樣與 seed，只限該層，不改總判準。

## 鎖定事前預測，正式資料只用於檢驗

DET1 lw0 凍結總步數為 A1 > A4 > A3，因此預測 lw1 的 Δaccuracy 點估計排序也為 **A1 > A4 > A3**；A3 的變化可能持平。Q2 不預測方向。Q3 預測影響很小：`d29bb70` 附近的既有紀錄顯示 delta 0.05→0.01 時誤報 39→35；此數字來自早期不同設定，**不是 DET2 結果，也不保證本母體同幅度**。來源：上述兩個 commit 與 [DET1 verdict](../outputs/det1/det1_verdict.md)。

## 先驗證 lw0 可沿用，再按固定順序執行與報告

1. **重現閘門。** 在預註冊提交後、任何新正式 run 之前，用 seed `20261012` 從 DET1 已鎖 205 條中按資料組抽 injected 9、synthetic 5、INSECTS 1 條，對 A1/A3/A4 lw0 各重跑一次，共 45 個 gate run；依固定 registry 展開順序建立抽樣清單，以同一抽樣串流套用三臂。比較 `y_true`、`y_pred`、`alarm_idx`（如有 input 座標欄位亦比較）之 dtype、shape 與位元內容。全部逐位元一致才沿用 DET1 的完整 lw0 輸出；任一不同，先在本文件末尾修訂記錄原因，再將三個 lw0 的 205 條全部重跑，不因 gate 失敗另停等批准。Gate 輸出置於 DET2 專用檢查目錄，不進正式計分。
2. **preset 與 smoke。** 新增唯一 A1d preset；對 A1-lw0 的結構化差異應只有名稱／描述／來源及 `detector_delta`，執行 config 唯一差別應是 delta。差異表存 `outputs/det2/preset_diff.md`。四個新跑臂各 smoke injected 2 條（registry 展開順序第一條 abrupt、第一條 gradual；兩條完整跑）、synthetic 前 2 條各前 5,000 步、INSECTS abrupt 1 條前 5,000 步。Smoke 與 gate 均隔離於正式根目錄。核對 manifest、計分、warning 事件守恆、lw1 凍結為 0；可修復的程式錯誤修正後重跑受影響 smoke，不更動偵測器參數與判準。
3. **執行閘門。** 正式預設 820 次；若 gate 失敗且需重跑 lw0 則 1,435 次。依已觀察 smoke 與 DET1 實測估時；若**預估超過三小時**或磁碟不足，停下回報。其餘先在對話報次數、估時、剩餘磁碟，再直接跑。順序先 synthetic＋全部 INSECTS，後 injected；6 workers、tmux 背景、整個指令包在 `caffeinate -dims`、`--resume`，log 放 `outputs/det2/logs/`，正式輸出只放 `outputs/benchmark/det2/`。每批報完成數、失敗數、實際耗時。個別失敗以 `--resume` 重試一次；仍失敗才在 verdict 標缺漏與「不可判定」。
4. **verdict 與整合。** 產出 `outputs/det2/det2_verdict.md` 及 HTML：Q1 三臂 lw0/lw1 與差值及 CI、三資料組與四型態、排序；Q2 P1/P2 與 accuracy；Q3 delta 敏感度；六格 DET1＋DET2 表；warning 事件、成本、無 GT 描述、失敗與缺漏。額外發現只列「事後觀察」，不新增判準；「限制」明列單一學習器、synthetic 非新 holdout、injected 每 cell 20 trials、River 版 ADWIN。DET1 原始資料與文件不得刪除或覆寫。
5. **交付。** 在 `docs/實驗脈絡總覽.md` 輪次表新增 DET2 一列，以 DET2-A1-lw1 等代號；推送功能分支並開往 main 的 PR，標題 `DET2: learn-during-warning effect per detector`，附 verdict 摘要；不合併、不直接更新 main。每階段完成各自 commit，英文祈使句，單一主題。

## 修訂（只追加；正式執行前明示，執行後列偏離）

預註冊提交時無修訂。規格未明但不影響結論者，採最接近 DET1 的做法並追加日期、理由及影響範圍；會影響結論且本文件未規定者，先停下請使用者決定。正式結果不得回填成事前預測。
