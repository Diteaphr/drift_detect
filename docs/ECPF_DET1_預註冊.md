# DET1 預註冊：在同一 ECPF 底座比較論文偵測器與雙 ADWIN

**登記：** 2026-10-12（Asia/Taipei），以本文件的 commit 為準。所有 DET1 新偵測器程式、preset、smoke 與正式執行均在本文件提交且經使用者審閱後開始。既有報告數字只供事前預測，不用來選擇或修改本輪參數。

**頂層問題：** 在固定 ECPF、資料與學習器後，單一偵測器的 warning 區與 drift 確認能否同時降低誤報、保留超額命中？既有 E9 顯示 DDM/HDDM-A 誤報少，但漸變命中可能大幅下降；DET1 將此比較擴至 RDDM、MagSeed 及 warning 期間訓練。來源：[ECPF 論文 §3–4](https://arxiv.org/pdf/1905.08848)、tag `archive/ecpf-misread-2026-10` 的 `docs/ECPF_V1E9_預註冊.md` 與 `outputs/e1_e2/e9_verdict.md`。

## 固定底座與資料，讓判定只反映偵測器和 warning 訓練

### 三個研究問題

1. 在同一套 ECPF 下，只換「誰開 warning buffer、誰確認 drift」，A2–A5 與 A1 的偵測和適應表現如何？
2. `ecpf_learn_during_warning=True` 對哪個 detector 的準確率、誤報與超額命中幫助最大，代價為何？
3. A5 相對於相同 δ、δw 的 A1 有何差異？若 MagSeed 的 drift 核心或重置語意也不同，只稱**演算法比較**，不把差異單獨歸因於 warning 條件。

### 鎖定設定

| 項目 | DET1 固定值或規則 |
|---|---|
| ECPF 底座 | `configs/presets/ecpf_paper.json`：`model_type="ht"`、`use_ecpf=True`、`ecpf_swap_policy="strict"`、`ecpf_fade_policy="ecpf"`、`ecpf_fade_enabled=True`、`ecpf_max_pool_size=10`、`warm_start=200`。其餘未列欄位沿用該 preset 和 `PipelineConfig` 現值；不編輯原 preset |
| 輸入 | 分類 leader 預測的 0/1 error；warning/drift signal 均為 `error`；凍結參照及 leader guard 預設關閉。ECPF 各比較臂使用相同資料順序與預測流程 |
| warning 訓練 | 每個 A0–A5 preset 明寫 `ecpf_learn_during_warning=False` (`_lw0`，論文 §3) 或 `True` (`_lw1`，9/23 改法)；兩版都跑 |
| A1/A1t | 雙 River ADWIN，`detector_delta_w=0.1`、`detector_delta=0.05`；`ecpf_adwin_one_sided=False`，其餘 ADWIN 實作設定沿用現行程式。A1 timeout=0；A1t timeout=1000 |
| A2/A3/A4 | 單一 zone detector 讀同一 0/1 error；DDM、HDDM-A、RDDM 使用 MOA 預設參數；timeout=0。離開 warning 區而無 drift 時關閉並丟棄 buffer |
| A5 | 原文 MagSeed，δ=0.05、ε=0.01、α=0.8、δw=0.1；timeout=0。不得以現有近似 `SEEDDetector` 代替 |
| A0 | 真實 drift 起點開 warning，**起點後第 60 個原始 input 步**確認，即 input 座標 `d_s+60`；新增 DET1 專用選項，不更改既有 `oracle_60`。僅有 GT 的資料執行；上限參考，不參與 A1 勝負 |
| A6 | 既有 `e10bft` preset 原樣；每個資料集只跑一次，不乘 lw，也不參與勝負 |
| 學習器 | 主分析 `ht`。`hf` 僅在 `synthetic_multiclass` 做 A1/A3/A5 各 `_lw0`/`_lw1` 共六組，`model_kwargs={"n_trees":10}`，單一種子；不混入主表 P1/P2 |
| 執行環境 | `river==0.21.2`，不升級；CapyMOA 只在獨立 venv，不能加入主 requirements |
| 調參 | 不能依報告資料結果調參。任何會影響比較的改動記在本文件末尾「修訂」，保留原文及日期，必要時先停下確認 |

論文 §4 的實驗採 MOA 預設 HDDM-A/RDDM，MagSeed 使用上述四個參數；§3 明示 warning 期間暫停訓練、無 drift 時恢復。[原文](https://arxiv.org/pdf/1905.08848)。E9 的 River DDM/HDDM-A 接線與 MOA 預設相符；RDDM 仍須做獨立一致性檢查。

### 組別與要建立的 preset

| ID | 開 warning | 確認 drift | ECPF preset 前綴；每個產生 `_lw0`、`_lw1` |
|---|---|---|---|
| A0 | 真實 drift 起點 | 原始 input `d_s+60` | `det1_oracle60`，DET1 專用 oracle 選項 |
| A1 | ADWIN δw=0.1 | ADWIN δ=0.05 | `det1_dual_adwin`，timeout 0 |
| A1t | 同 A1 | 同 A1 | `det1_dual_adwin_t1000`，timeout 1000 |
| A2 | DDM warning 區 | DDM drift | `det1_zone_ddm`，`ecpf_zone_detector="ddm"` |
| A3 | HDDM-A warning 區 | HDDM-A drift | `det1_zone_hddm_a`，`ecpf_zone_detector="hddm_a"` |
| A4 | RDDM warning 區 | RDDM drift | `det1_zone_rddm`，`ecpf_zone_detector="rddm"` |
| A5 | MagSeed warning | MagSeed drift | `det1_zone_magseed`，`ecpf_zone_detector="magseed"` |
| A6 | E10bFT | E10bFT | 現有 `e10bft`，不新增或編輯 |

A2–A5 的 `ecpf_signal_mode` 固定為 `"dual_adwin"`，非空 zone 名稱取代雙 ADWIN。A0 只新增選項／接線，不變更既有 `oracle_60` 的 `d_s+59` 行為。若 A0 接線無法可靠處理 injected 被刪的列，依使用者授權可在正式執行前取消 A0 並於修訂記錄；P1/P2、A1–A5 不因此更動。
Injected 若起點列遭刪除，warning 從起點之後第一個保留列開始；確認只能在原始 input 座標 `d_s+60` 或之後的第一個保留列發生，實際延遲照原始 input 座標報告，不把保留列的第 60 筆誤當原始第 60 筆。串流結束仍未達目標者記為 censored。

新 ECPF preset 的 `role="ablation"`，新增 detector-only preset 的 `role="detector_reference"`；每個 preset 的 `description` 標明組別 ID，並用差異腳本核對固定底座。

Detector-only 組別僅在 `injected_paper_electricity` 跑：既有 `det_adwin` 與新增 `det_ddm`、`det_hddm_a`、`det_rddm`、`det_magseed`。全部遵循現有 Cerqueira 工作流：單棵 HT 持續訓練且不因警報重置，前 25% 原始 input 不餵 detector。既有 `det_adwin` 保持 correctness 訊號及既定 MOA 方向；新增四組使用 0/1 error，偵測錯誤率上升。Reset 語意以各 detector 原始論文／MOA 包裝為準，在 preset 和實作註明；不得為了提高文獻分數改方向。

### 資料用途與可比性

| 資料 | 規模 | GT／用途 |
|---|---:|---|
| `injected_paper_electricity` | 50 trials × 8 cells = 400 條 | 原始 input 座標的 GT；ECPF 組只與同 harness 組別比較；detector-only 組才可與 Cerqueira SOTA 並排 |
| `insects_abrupt_balanced` | 1 條、52,848 筆 | 5 個 GT 點；納入 P1/P2 |
| `insects_incremental_balanced` | 1 條、57,018 筆 | GT 檔 `[]`；只報準確率、警報數、runtime，不把警報算 FP，A0 不跑 |
| `synthetic_multiclass` | 40 條、每條 100,000 筆 | GT 可用，納入 P1/P2 及 drift 型態分表；registry role 為 `dev`，E 系列已用過部分資料，**本輪是參數鎖定後的評估，不是全新 holdout**，不可宣稱獨立外部驗證或文獻 SOTA |

正式執行在新隔離根目錄 `outputs/benchmark/det1/`，不覆寫既有 `outputs/benchmark/<dataset>/<preset>`；smoke 在 `outputs/det1/smoke/`，不進正式分析。既有 `det_adwin` 也在 DET1 根目錄重跑。所有正式 run 的 manifest 必須含固定 git commit、dataset source hash／生成設定與 seed、preset/effective config、版本、runtime。正式執行前須補**可中斷續跑**：只跳過輸出完整且 provenance 與本輪相同的 job；半成品重跑；`runs.csv` 能由已完成 manifest/metrics 重新建構。正式批次不因中斷而整批重算。

## 以兩種偵測口徑與 adaptation 指標完整報告結果

### 偵測主口徑及 E11 超額命中

P1/P2 在每條有 GT 的串流上用同一 **1000 步**主窗 `[d_s,d_s+1000]`（含端點、截到串流終點）；暖機前 GT 起點不計分。Injected 使用原始 input 座標，其他用輸出列座標。Injected 與 Cerqueira 的對照另依 registry 的 `[d_s,d_s+2500]` 及 `detect_from` 計分，不取代 P1/P2。前 25% 不計分規則沿用 benchmark evaluator；分析腳本不能把那段警報算進 P1/P2。

- **Cerqueira 警報口徑：** 每個在窗內的警報都計 TP；窗外警報計 FP；同一 drift 可有多個 TP。依現有 evaluator 的 episode ownership 防止單一警報同時歸兩個 drift；另報 FN、precision、recall、F1、MDT（每個已命中 drift 首次警報延遲）、FAR（FP／可計分步數 × 1000）、`episode_recall`。1000 步主窗由分析腳本重算並與既有 evaluator 的同窗欄位交叉驗證，**不修改 evaluator 原指標語意**。
- **E11 超額命中口徑：** 每個 GT 最多算一次 `episode_hit`。對每次執行，令 `W_i` 為可計分範圍內第 i 個 GT 窗，`O` 為可計分步數扣除全部 `W_i` 聯集，`λ=FP/O`，`C=Σ_i(1−exp(−λ·|W_i|))`，`X=Σ_i episode_hit_i−C`。FP 是該執行所有窗外警報數；窗內重複警報不增加 episode_hit，也不改寫既有 Cerqueira TP。各次執行先算 X，再跨指定資料組合計。若 `O=0`，X 標成不可估，不代入零；不得用原 evaluator 的逐警報 TP 直接減 C。來源：存檔 tag 的 E11 預註冊及 `scripts/run_e1_e2.py:648–668`；此處按本輪 1000 步與 benchmark 的可計分座標套用。
- **窗口自我檢查：** 相同 alarm/GT 若以 registry `delta_max=1000` 計分，分析腳本與 evaluator 的 TP/FP/FN 必須相同；模擬與 drift 無關的隨機警報 200 次，平均超額命中絕對值 <0.3。重疊窗、末端截斷、零 FP、無 GT、原始 input 缺列都要有明確檢查。

### Warning、adaptation 與成本

| 指標 | 固定定義／來源 |
|---|---|
| warning 開啟、未確認即關閉 | 實際 zone/ADWIN/oracle 狀態轉換事件；未確認即關閉含 detector 離區與 timeout，分因別列。串流結尾仍開啟者單列 censored，不算已關閉 |
| buffer 中位長度 | 每次已確認 drift 時交給 ECPF 的 buffer 筆數；另列未確認丟棄 buffer 的中位數及樣本數 |
| 總凍結步數 | warning 期間實際沒有呼叫 leader/shadow 訓練的串流步數；`lw1` 預期為 0，但以事件紀錄核實；分組加總 |
| prequential accuracy、kappa | benchmark evaluator 的全串流 test-then-train `acc_prequential`、`kappa`；insects incremental 也照報 |
| drift 後 1000 步 accuracy | 每個 GT 起點後可觀測的前 1000 個預測之正確率，再以該資料組所有可觀測預測加權彙總；被注入刪除的 input 列無預測、不進分母；重疊只計一次 |
| reuse 勝出率 | 每個確認 drift 後，重用副本與 fresh learner 的對決到下一次確認或串流終點為止；結束時仍由重用副本領先的有效對決數／有效對決數，平手與沒有後續樣本者另列，不硬判勝負；以 observer 紀錄，不用 `winner_initial`（初始永遠是 reused）充當結果 |
| runtime | manifest 的 `runtime_s`，各組總和與每條中位數；另列峰值記憶體作診斷，不參與判準 |

Observer-only warning 事件／reuse 記錄在階段三之後補線；需通過旗標關閉時的逐位元基線 gate。若某細節無法從既有輸出可靠還原，先補被動紀錄再跑 smoke，不能事後臆測。

## 以同 lw 的 A1 作對照，P1 與 P2 同時成立才判優

**主判定母體：** injected、INSECTS abrupt、synthetic 的全部 HT 正式 run。三組逐次合計原始 FP 與 X，統計時每條串流算一次；不平均各資料組、也不讓 hf10、A0、A6、insects incremental 進 P1/P2。A1t 僅作次要對照，不進 A1 的主判定。這會讓 400 條 injected 的權重大，故同時照常報三組各自數字。Synthetic 已使用過，結論範圍限定為本批已知資料的鎖參數比較。

對每個 `d∈{A2,A3,A4,A5}`、每個 `lw∈{0,1}`，均與同 lw 的 A1 配對判定：

| 條件 | 成立標準 |
|---|---|
| P1：誤報 | 三組 FP@1000 合計差 `ΔFP=FP(d,lw)−FP(A1,lw)`；負值有利於 d |
| P2：扣除機率後命中 | 三組 E11 超額命中@1000 合計差 `ΔX=X(d,lw)−X(A1,lw)`；正值有利於 d |

**不確定性與條件狀態：** 對每個 d × lw，以串流為單位做 **10,000 次配對、分層 bootstrap**，固定種子 **20261012**；在 injected（400 條）、INSECTS abrupt（1 條）、synthetic（40 條）三層內各自有放回抽樣，保持每層條數不變，同一抽樣索引同時套用 d 與對照組。每次重算三層合計的 ΔFP、ΔX；各取第 2.5 與 97.5 百分位作 95% percentile CI。單條 INSECTS 串流在 bootstrap 中固定重現，不能假稱該層有抽樣變異；CI 是對這批串流的條件不確定性，不代表全新資料的外推區間。若 P1 的 CI 上界 **<0**，P1「成立」；下界 **>0**，P1「不成立」；其餘（包括碰到或跨越 0）判「持平」。P2 的 CI 下界 **>0** 為「成立」、上界 **<0** 為「不成立」，其餘「持平」。點估計與 CI 均照報。缺少配對串流或 X 不可估時，該比較不可判定，不能改抽樣母體。

**次要對照：** A2–A5 × lw 另各以同 lw 的 A1t（timeout=1000）計算相同 ΔFP、ΔX、分層配對 bootstrap CI、P1/P2 狀態及下表結論；與 A1 主結論並列，清楚標「A1t 次要結論」。A1t 不是 A1 主判定的替代，兩種對照若結論相反仍各自保留。

| P1 | P2 | 對該 detector、該 lw 的結論 |
|---|---|---|
| 成立 | 成立 | 優於 Dual ADWIN |
| 不成立 | 不成立 | 不如 Dual ADWIN |
| 成立 | 不成立 | 如實報告，不下勝負結論 |
| 不成立 | 成立 | 如實報告，不下勝負結論 |
| 任一條件持平 | 另一條件任意狀態 | 持平；列出兩條件狀態，不下整體優劣結論 |
| 任一不可估／資料不完整 | — | 不可判定，列原因 |

**三組方向與一致性（描述性，不作判準）：** 對主 A1 與次要 A1t 每一個 d × lw × P1/P2，分別列 injected、INSECTS abrupt、synthetic 的點估計差值及方向：ΔFP <0／=0／>0 對應有利／相同／不利，ΔX >0／=0／<0 對應有利／相同／不利；再列「三組中幾組與三組合計的點估計方向一致」（0–3）。若合計恰為 0，僅報三組方向與合計相同，不賦予勝負意義。不以方向一致數修改 CI 判定或結論。

**型態分層：** 突變、漸變、incremental 各自依同一 P1/P2 方向判定，獨立於總結論；synthetic recurring 依 GT／檔案標籤另列，不事後合併到有利型態。Injected 的 abrupt/gradual 分表；INSECTS incremental 無 GT，只作 adaptation 描述，不能出現 TP/FP 或超額命中結論。漸變與 incremental 即使與總判定相反也必須顯示。

**warning 訓練因子：** 對 A0–A5 每一組列 `_lw1−_lw0` 的 accuracy、FP@1000、X@1000、凍結步數；以配對串流計算並另列資料組結果。「幫助最大」的描述性排序依三組合計 accuracy 差值，由高到低；若此指標相同，並列，不新增勝負門檻。A1t 相同方式照報。`lw1` 是否改善 FP/X 不從 accuracy 單獨推論。

**MagSeed 對 A1 消融：** 逐項列 warning 開啟／關閉、buffer、凍結、FP、X、accuracy、post-drift accuracy、runtime，在 lw0/lw1 各做配對。若原文 MagSeed 的 drift 機制與雙 ADWIN 不同，結論寫「A5 演算法相對 A1 的差異」；只有經實作與輸入／重置檢查證實兩者唯一差異是 warning 條件時，才稱純 warning 條件消融。

**統計輔助：** `compare_sota.py --target det1_dual_adwin_lw0` 與 `_lw1`，用 `--root outputs/benchmark/det1 --include-noncomparable` 及本輪 presets/datasets 過濾；每 injected cell pooled F1/precision/recall/MDT/FAR、Friedman 平均排名、Holm 校正 Wilcoxon 如工具有足夠完整 blocks 即照報。檢定 p 值不改 P1/P2 判準。Injected ECPF F1 只能標「參考、與文獻不可比」；只有 detector-only 五組的同格數值可與 registry `sota_by_cell`、`calibration` 並列。

## 事前預測：單側偵測器可能降低誤報，也可能漏掉漸變

- E9 的 1000 步窗：DDM 三家族合計 FP 34、HDDM-A 5，原雙 ADWIN base 83；MC-RBF gradual 命中 DDM 1、HDDM-A 0、base 10。故預測 A2/A3 對 A1 的 FP 較低，但漸變 X 較低；能否同時過 P1/P2 不確定。來源：存檔 tag 的 `outputs/e1_e2/e9_verdict.md`。E9 用不同資料，這不是 DET1 結果。
- RDDM 預測比 HDDM-A 敏感、警報更多；能否提升漸變 X 未知。ECPF 論文 Table 4 在其合成資料上 RDDM 的偵測數多於 HDDM-A，但資料與學習器不同，不能移植為本輪定論。[論文 Table 4](https://arxiv.org/pdf/1905.08848)。
- MagSeed 的額外 warning 條件**可能**使 A5 的 FP 少於 A1，但這是弱預測；同篇論文 Table 4 的 MagSeed 警報數偏高，已有相反證據。預註冊保留此不確定性，不因結果調整參數或判準。[論文 §4/Table 4](https://arxiv.org/pdf/1905.08848)。
- `lw1` 預測會縮短長 warning 對 accuracy 的損失，對長警告較多的組別幫助可能最大；持續學習也可能改變 detector 看到的 error，因此 FP/X 方向不預設。

## 實作與執行閘門未過時，先停下並如實報告

1. **文獻與實作：** RDDM 依 `moa.classifiers.core.driftdetection.RDDM` 原始碼移植，MOA 預設；在獨立 CapyMOA venv 餵同一 0/1 序列，±32 步內雙向觸發重合率各 ≥0.90。未達標報差異來源，不能稱忠於 MOA。MagSeed 先找 Chen、Koh、Riddle (2015) 全文；本 checkout 無 PDF，**進入 MagSeed 實作前停下請使用者提供**，不能依摘要或現有 SEED 近似版猜實作。[MagSeed 書目](https://doi.org/10.1007/978-3-319-26350-2_9)。
2. **共同零件：** 每個新 detector 在固定人造 0/1 error 0.1→0.5 上必須先 warning、後 drift；0.5→0.1 不得觸發。新增旗標關閉時，既有二元基線 byte gate 逐位元相同；`pytest` 全部通過，main 已失敗項需事前列出。
3. **Preset 與 provenance：** 新 preset 只能相對 `ecpf_paper` 改 detector 相關欄位、lw、timeout（A0 專用選項除外）；差異表存 `outputs/det1/preset_diff.md`。manifest 必須可核對 git commit、資料來源 hash／生成 seed、版本與設定；錯誤列或未授權參數使 smoke 失效。
4. **Smoke：** 每 preset × 每資料短跑；injected `--trials 3`（24 條），其餘 `--max-steps 5000`。檢查計分例外、0 觸發、觸發暴增、warning 卡住與 runtime；這些只觸發診斷或程式修正，**不是看 report 數字調參的許可**。Smoke 與正式目錄隔離；injected `--trials 3` 即使 runner 未標 smoke 也不進正式分析。修程式後重跑受影響 smoke。
5. **續跑與正式：** 完成且測試 resume、資料 hash/commit mismatch 拒絕誤跳過後才跑約 8,868 次正式 run；本機 10 logical cores，worker 數依 smoke 的記憶體／效能決定。原始 run 不手改。若 A0 取消，記修訂與次數變化；不得影響 A1–A5 的預註冊判準。
6. **缺失處理：** 演算法或記錄資料缺失、O=0、只有部分 trials、無法完成 MOA 驗證時，相關判定標「不可判定」並列失敗組數；不得把缺值設 0、悄悄剔除不利格或事後改窗。若需改規則，保留原文並於末尾加日期、原因、影響與批准紀錄。

## 照常報告所有數字，勝負只由 P1/P2 決定

- 兩種 lw 的 A0–A5 及 A6：每資料／每 cell 的 run 數、GT 數、警報數、TP/FP/FN@1000、episode hit/recall、X、MDT、FAR；injected 另報 @2500 及 8 cells pooled F1/precision/recall；A0 不併入勝負。
- warning 次數、未確認關閉及其原因、已確認／丟棄 buffer 中位長度、凍結步數、timeout 次數、串流結尾 censored 數；A1 與 A1t 的差異。
- prequential accuracy、kappa、post-drift 1000 步 accuracy、reuse 勝出／平手／無後續樣本、runtime；INSECTS incremental 只列 accuracy、警報數、runtime。
- 三組主判定的 FP、episode hits、期望機率命中 C、X 分項與合計；每個 A2–A5 × lw 對 A1 與 A1t 的 ΔFP、ΔX、10,000 次串流 bootstrap 95% CI、P1/P2 成立／不成立／持平狀態、主與次要結論、三組各自方向及一致組數、型態分層；`lw1−lw0`、MagSeed 對 A1 配對表、hf10 六組敏感性結果。
- Detector-only 五組與 Cerqueira 每格 SOTA/calibration 的差值；文獻僅在這組並排。比較報告的 Friedman/Wilcoxon/Holm 結果、限制與可比性註記。
- 所有 gate、版本／commit／資料 hash、正式完整性、失敗和偏離；事後觀察在 verdict 獨立標記，不新增判準。

**規劃次數：** injected 400×20=8,000；INSECTS abrupt 15；INSECTS incremental 13（無 A0）；synthetic HT 40×15=600；synthetic hf10 40×6=240；正式總數 **8,868**。原定 smoke **1,108** 次（不含 hf10），若實際 smoke 含 hf10，另列其 240 次；時間在 smoke 後更新。來源：`outputs/det1/stage1_readiness.md` 與 registry。

## 修訂（僅追加，不刪改上文）

預註冊提交時無修訂。之後若因實作或資料問題必須偏離，逐項追加日期、原規則、原因、替代做法、會影響的判定與使用者確認紀錄；正式結果不得倒填為事前預測。

### 2026-10-13：按 Chen 2016 修正 A5 方向、增列 A5u 並讓其他組別先行

**批准與時序：** 使用者於 2026-10-13（Asia/Taipei）明確批准以下五項變更；本修訂須先獨立提交，然後才能執行任何新的 DET1 report 資料。上文保留為最初登記的歷史內容；遇到 A5 行為閘門、來源停點、組別範圍與執行順序衝突時，以本段事前修訂為準。依據為 [Chen（2016）學位論文第 3 章，印刷頁 36–40](https://hdl.handle.net/2292/28911)、[MOA SEED 原始碼](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/SEEDChangeDetector.java)及已完成、但未用 report 資料調參的 [MagSeed 一手來源查核](../outputs/det1/magseed_thesis_source_check.html)。

1. **A5 改用原文雙向行為閘門。** 原規則「所有新 detector 在 0.5→0.1 不得觸發」對 A2–A4 仍適用，對 A5 **撤銷**。A5 保留固定 0/1 error 序列 0.1→0.5「先 warning、後 drift」；0.5→0.1 改檢查其 warning／drift 與論文式 (3.1) 的左右均值**絕對差、雙向**定義一致，應允許下降觸發 drift，逐事件位置及視窗切點須記錄。原因是原單側閘門為本研究添加，Chen 原文不是單側；A1 設 `ecpf_adwin_one_sided=False`，主比較維持雙向。此變更只替代 A5 的方向閘門，不改 P1/P2 的數學判準與資料組。
2. **增列 A5u 單側變體作次要分析。** A5u 對相同 0/1 error 只承認右側錯誤率**上升**的區塊切點；warning 的均值差條件與 drift 條件均限正向，100 筆 `p+s` warning 條件照 A5 保留。其他參數、壓縮和狀態邏輯與 A5 相同。明標「偏離原文的變體」，`ecpf_zone_detector="magseed_upward"`，兩種 lw 都跑四組 HT 資料；只做 A5u 對 A5／A1 的描述性次要比較，**不加入主要 P1/P2、A1t 判定、detector-only 文獻比較或 hf10 六組**。A5u 的 0.5→0.1 不得報 drift，作變體自身行為閘門。
3. **固定偽碼矛盾的主解讀與一次敏感度檢查。** [Chen（2016）Algorithm 1，印刷頁 39／PDF 頁 54](https://hdl.handle.net/2292/28911)第 17–25 行可設 drift 或由兩條件設 warning；第 27 行卻在 `warningFound=false` 時無條件設 no change。**解讀 X（主分析）**依第 3.3–3.4 節正文和印刷頁 46 的「drift 可無先前 warning」描述，採 `drift > 任一 warning > no change`，第 27 行只在兩者皆無時生效。**解讀 Y（字面敏感度）**照第 27 行無條件覆蓋，可能抹掉 drift 或僅由 `p+s` 觸發的 warning；保留此現象，不以事後結果修飾。Y 只在 `synthetic_multiclass` dev 的第一個 registry seed、HT、`lw0`、前 5,000 步執行**一次**，與相同輸入的 X 描述性比較警報／warning／runtime；不進正式 P1/P2、調參或勝負判定。若 registry 第一種子未明示，以 registry 展開順序第一條為準並在 manifest 記錄。
4. **缺參數先用論文，仍缺則逐項定值。** 已知且鎖定的 A5／A5u 值為 `δd=0.05`、`ε̂=0.01`、`α=0.8`、`δw=0.1`。Chen（2016）Table 3.3 對 `τ`、`cw` 只給測試範圍，**不是預設值**；區塊大小 `b`、100 筆窗未滿時的規則及 `s` 的母體／估計方式也未明示。故 `b=32`、`τ=75` 採 [MOA SEED 程式預設](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/SEEDChangeDetector.java)，理由是 MAGSEED 延伸 SEED；`cw=2` 取論文 Table 3.3 已評估的 1/2 中較保守值，理由是減少第二條 warning 的偶發觸發；100 筆湊滿才建立 `pmin,smin`，`s=sqrt(p(1-p))`，理由是正文稱錯誤指示值的 100 筆滑動標準差。壓縮依 SEED 程式由新向舊的相對區塊位置計算 `ε̂·α·t`。以上逐項是**來源支持的選擇或明示推論**，不是 Chen/ECPF 原作者已確認的完整設定；不因 report 結果改值。
5. **A5 入正式分析的條件及其他組先行。** 修訂先 commit；再將試作的主解讀 X 實作與文件同步，讓 A5 通過本段新閘門、原有 byte gate 與適用測試後，公開名稱改為 `magseed`，註明「依 Chen 2016 學位論文實作，偽碼矛盾處採 X 解讀」。此名稱不表示已取得 2015 會議 PDF 或原作者 MAGSEED 程式；來源限制照報。A5 通過前，不將它併入正式 P1/P2。A0–A4、A1t、A6 及 detector-only 組別的 preset、smoke 與後續執行**不必等 A5**，依階段四、五和既有續跑／provenance 閘門先行；`det_magseed` 仍要等 A5。A5u 只作本段次要分析。原規劃的 8,868 次是**不含 A5u**的主矩陣；A5u 四組 HT × 兩種 lw 另增 884 次（injected 800、INSECTS abrupt 2、incremental 2、synthetic 80），Y 的一次 dev 不混入正式總數。若 A5 最終未過，正式缺漏與實際次數如實列出，不把其他組別停掉。

6. **detector-only A5 的方向一併對齊原文。** 上文 detector-only 四組「偵測錯誤率上升」對 `det_magseed` 改為讀 0/1 error，並依 Chen（2016）式 (3.1) 的**雙向絕對差**報警；`det_ddm`、`det_hddm_a`、`det_rddm` 仍依各自原始語意偵測錯誤率上升。這是 A5 方向修訂在 detector-only 工作流的同一適用範圍，不把 `det_magseed` 偷換成 A5u。

### 2026-10-13：正式矩陣收斂為 ECPF 論文 detector 對 Dual ADWIN 的 lw0 比較

**批准、時序與理由：** 使用者於階段五 smoke 審閱通過後、任何正式 report run 之前明確批准本修訂；必須先 commit 本段，再啟動正式執行。當時只有 smoke 結果，沒有正式結果。研究問題聚焦於「Dual ADWIN 對 ECPF 論文 detector」，並縮短運算時間。上文保留歷史原文；正式執行範圍、資料母體、次要分析及報告交付若與上文衝突，以本段為準；P1/P2 的定義、1000 步主窗、E11 每 drift 最多一命中與機會值 C、10,000 次 CI 及缺失處理**不變**。Smoke 僅作執行可行性與異常檢查，不據以選有利串流或調參。

1. **唯一正式組別與設定。** A1 `det1_dual_adwin_lw0`、A2 `det1_zone_ddm_lw0`、A3 `det1_zone_hddm_a_lw0`、A4 `det1_zone_rddm_lw0`、A5 `det1_zone_magseed_lw0`；全用單棵 Hoeffding Tree、`ecpf_learn_during_warning=False`，對應 ECPF 論文 §3 的 warning 期間停止訓練。A5 一律稱「依 Chen 2016 學位論文實作的 MagSeed（偽碼矛盾處採 X 解讀）」；不稱忠實重現 2015 會議版或作者程式。只有 A2–A5 對 A1 的主 P1/P2 比較。
2. **本輪排除組別。** A0、A1t、A5u、A6、全部 `_lw1`、hf10 與所有 detector-only 組別均不執行；`lw1` 訓練因子留待後續獨立實驗。A1t 次要判定、`lw1−lw0`、hf10 敏感性及 detector-only 文獻數值比較在 verdict 明標「本輪未執行」，不得以缺值當零或改以其他組替代。
3. **正式資料母體。** `injected_paper_electricity` 的 registry 8 cells 各取**前 20 個 generator trial**，不挑選，共 160 條；`synthetic_multiclass` 全 40 條；registry 中全部五個 `insects_*_balanced` 各一條。執行前逐一讀其 sibling GT 檔：非空者列入 P1/P2、型態分層及「INSECTS」方向組；空 GT 者只報 prequential accuracy、警報數、runtime，不計 TP/FP、C、X 或方向。INSECTS 五條均仍執行，不能因無 GT 移除其描述性資料。三個主要判定組固定為 injected／synthetic／有 GT 的 INSECTS；injected 的延遲與警報使用原始輸入座標。若 GT 狀態與此規則或實際檔案不符，開跑前停下回報。
4. **統計與結論不因縮小母體改寫。** 對新母體的 A2–A5 各以 A1 配對，按三組分層、以串流為抽樣單位做 10,000 次 bootstrap，種子 20261012，報 ΔFP 與 ΔX 的 95% CI；CI 包含 0 時該條件「持平」。各 INSECTS 有 GT 串流各是一個配對單位，組內抽樣保持其條數；不以型態或 cell 事後挑選。依 abrupt／gradual／incremental／recurring 型態分層照報；複合名稱可在明示規則下同時出現在相關描述性層，不改三組合計 P1/P2 母體或重複計入總分。三組各自 ΔFP／ΔX 方向及與合計方向一致的組數照報，不作判準。A1t 次要判定明標「本輪未執行」。結論只限於**「在 ECPF 論文設定（warning 期間停止訓練、單棵 Hoeffding Tree）下」**。
5. **執行與交付閘門。** 更新後正式次數為每組 160 injected + 40 synthetic + 5 INSECTS，即 **5 × 205 = 1,025 runs**；205 條配對來源中的 GT/non-GT 身分在開跑前核實。先跑 synthetic 與全部 INSECTS，再跑 injected；6 workers，tmux 背景作業，整個執行指令以 `caffeinate -dims` 包住，log 放 `outputs/det1/logs/`，正式輸出只放 `outputs/benchmark/det1/`，使用 `--resume`。開跑前回報五個 GT 狀態、總次數、時間估計、剩餘磁碟與預估輸出大小；若 GT 意外缺失、磁碟不足或預估超過三小時則停下回報，否則直接開跑。每批回報完成、失敗及實際耗時。結束後產出 `outputs/det1/det1_verdict.md` 與 HTML，`docs/實驗脈絡總覽.md` 輪次表新增 DET1 一列，組別代號寫 `DET1-A1` 等；額外觀察獨立置於「事後觀察」，不新增判準。開 PR 到 main，標題 `DET1: ECPF paper detectors vs dual ADWIN (lw0)`，附 verdict 摘要，然後【停】。
