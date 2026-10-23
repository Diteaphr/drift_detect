# DET3 預註冊：完整系統對 ECPF 論文偵測器

**登記：** 2026-10-13（Asia/Taipei）。本文件在任何 DET3 正式執行前獨立提交。研究底座與比較口徑承接 [DET1 預註冊](ECPF_DET1_預註冊.md)、[DET1 verdict](../outputs/det1/det1_verdict.md)、[DET2 預註冊](ECPF_DET2_預註冊.md)及[DET2 verdict](../outputs/det2/det2_verdict.md)。新系統元件來自 [`e10bft.json`](../configs/presets/e10bft.json)；共同底座以 [`ecpf_paper.json`](../configs/presets/ecpf_paper.json)為準。接線已在[可行性檢查](ECPF_DET3_接線可行性.md)核實。

**頂層問題：** 在固定單棵 Hoeffding Tree 與相同 205 條配對串流上，Dual ADWIN 加 frozen reference、leader 守衛、warning 逾時及 warning 期間持續學習，對 ECPF 論文設定下的 HDDM-A，偵測與準確率各自是否勝出？兩面向分開判，不合成單一勝負。

## 固定底座與七臂，隔離訊號、偵測器和訓練因子

所有**新臂**複製 `ecpf_paper` 底座：`model_type=ht`、`use_ecpf=true`、`ecpf_signal_mode=dual_adwin`、`ecpf_swap_policy=strict`、`ecpf_fade_policy=ecpf`、`ecpf_fade_enabled=true`、`ecpf_max_pool_size=10`、warm start 200、`river==0.21.2`。偵測設定沿 DET1：Dual ADWIN `detector_delta_w=0.1`、`detector_delta=0.05`、`ecpf_adwin_one_sided=false`；HDDM-A 採 River 0.21.2／MOA 對應預設。`ecpf_warning_signal=ecpf_drift_signal=error`。新臂共同啟用 `ecpf_reference_signal=true`、`ecpf_reference_warmup=500`、`ecpf_leader_guard=true`、`ecpf_detector_warning_timeout=1000`。`ecpf_guard_frozen_scale=500` 可明寫以對齊 E10bFT，但只在迴歸生效，分類結果不受影響。只變更 `ecpf_learn_during_warning` 或 `ecpf_zone_detector` 以區分新臂。不得直接使用或修改 `e10bft.json`、`ecpf_paper.json`；兩者實際政策差異在 preset diff 中逐項列明。

| DET3 ID | preset | 來源／用途 |
|---|---|---|
| P-D | `det1_dual_adwin_lw0` | DET1 沿用，論文底座 Dual ADWIN lw0 |
| P-H | `det1_zone_hddm_a_lw0` | DET1 沿用，論文底座最佳 detector HDDM-A lw0，Q1 對照 |
| P-H1 | `det1_zone_hddm_a_lw1` | DET2 沿用，Q3 對照 |
| P-D1 | `det1_dual_adwin_lw1` | DET2 沿用，Q3 對照 |
| F-D0 | `det3_full_dual_adwin_lw0` | 新跑，完整訊號／守衛／逾時，lw0 |
| F-D1 | `det3_full_dual_adwin_lw1` | 新跑，完整系統，Q1/Q2 |
| F-H1 | `det3_full_hddm_a_lw1` | 新跑，同完整元件，HDDM-A，Q2 對照 |

新跑 **3 × 205 = 615 次**。資料固定為 `injected_paper_electricity` 八格各 registry 展開前 20 trials（160）、`synthetic_multiclass` 全 40、全部五個 `insects_*_balanced` 各一。INSECTS 四條非空 GT 進偵測計分；`insects_incremental_balanced` 空 GT 只報準確率、警報數與 runtime，仍進全串流 accuracy。synthetic 在 E 系列已使用，是鎖參數後評估，並非新 holdout。所有 arm 使用相同來源、順序、warm start、有效預測與 GT。

## 使用 DET1 同一計分與配對推論，分開判偵測和準確率

主指標：全部 205 條的 prequential accuracy（各 run 可計分預測數加權）；有 GT 204 條的 drift 後 accuracy（GT 起點後 **1,000 個座標步**內可觀測預測加權，重疊只計一次，injected 為原始 input 座標）、FP@1000、E11 超額命中 `X=episode_hits−C`。偵測窗含端點 `[d_s,d_s+1000]`；暖機前 GT 排除，injected 前 25% 警報不計分。每 GT 最多算一次命中；`C=Σ[1−exp(−FP/O·|W_i|)]`，`O` 為可計分窗外步數。次要報 episode hits、MDT、kappa、凍結步數、warning 開啟／確認／離區關閉／逾時／reference switch／截尾與 runtime。全串流 accuracy 含空 GT INSECTS；FP、X、drift 後 accuracy 不含它。

三資料組（injected／synthetic／INSECTS）內以**串流為配對單位**有放回分層 bootstrap **10,000 次**，seed `20261012`，每層保持原串流數，同一索引套用兩臂。CI 為 percentile 95%；accuracy 每次重算正確／可計分數，FP、X 每次按 run 合計。CI 含 0（含端點）判持平。資料組與型態（突變／漸變／incremental／recurring）各自另列點差及 CI，但不加新門檻；複合型態可在描述層重複，總判定每串流只計一次。缺配對 run 或必要分數無法估算時，相關判定為「不可判定」，不選擇性剔除。

**Q1（主要）：F-D1 − P-H。** 偵測按 DET1 P1／P2：`ΔFP` CI 全負且 `ΔX` CI 全正判「優於」；兩者均顯著朝不利方向（FP 全正、X 全負）判「不如」；含 0 或兩指標方向相反判「持平」。準確率按 `Δaccuracy` CI 全正判「優於」、全負判「不如」，其餘「持平」。報告固定格式「偵測：○○；準確率：○○」，不合成單一勝負。F-H1 − P-H 用相同規則作次要比較。

**Q2：F-D1 − F-H1。** 同 Q1 分別判偵測與準確率。報 P1、P2 各自狀態及 CI，不將準確率代替偵測品質。

**Q3（描述性，附 CI）：** F-D0 − P-D 是 lw0 的換訊號／守衛／逾時組合效果；F-D1 − F-D0 是完整系統的 lw1 效果；對照 DET2 的 P-D1 − P-D。HDDM-A 另報 F-H1 − P-H1（完整元件在 lw1 下）與 F-H1 − P-H（完整元件及 lw1 同時改動）。這些是組合對比，不把 frozen reference、守衛和逾時拆成獨立因果效果。

**開發資料重疊的事前限制：** E10bFT 元件曾在 E 系列資料開發，synthetic、部分 INSECTS 及注入型 electricity 曾參與；本輪確切的 `injected_paper_electricity` 未參與。每個判定另列三組方向。若 Q1 總判「優於」，而 injected 單組點估計在相應面向反向，該面向結論必須加註「優勢依賴曾用於開發的資料」。單組方向只報告，不改總判準。

## 先驗預測與執行閘門鎖定後續解讀

依 E 系列，預測完整元件組合主要降低 FP；F-D1 對 P-H 的偵測可能持平或優於。Q2 無方向預測。完整系統的 lw1 效果可能小於論文底座，因逾時已限制長期凍結。預測不是判準，不據結果改門檻或參數。

1. 以固定 seed 從正式矩陣抽 15 條（injected 9、synthetic 5、INSECTS 1），重跑 P-D、P-H、P-H1、P-D1，逐位元比較 `y_true`、`y_pred`、`alarm_idx` 與適用的 `alarm_idx_input`。全同才沿用 DET1／DET2；任一不同則四臂均在 DET3 專用目錄重跑 205 條（另增 820 次），於本文件末尾追加修訂說明。
2. 新建三個 preset；對 `ecpf_paper.json` 與 `e10bft.json` 產生差異表。Smoke 每新臂取 injected 2 條完整、synthetic 2 條前 5,000 步、INSECTS abrupt 1 條前 5,000 步，隔離於正式輸出。核對 manifest、計分、warning 事件守恆、lw1 凍結 0、reference 與守衛診斷欄位。可修復程式錯誤修正後重跑受影響 smoke，不改固定參數與判準。
3. 正式輸出 `outputs/benchmark/det3/`，先 synthetic＋全部 INSECTS，再 injected；6 workers、tmux 背景、整個指令包於 `caffeinate -dims`、`--resume`，log 在 `outputs/det3/logs/`。開跑前報次數、估時、磁碟；估時超過三小時或磁碟不足則停下。失敗 run 重試一次；仍失敗記缺漏並將相關判定標不可判定。每批報完成／失敗／實耗。
4. 產出 `outputs/det3/det3_verdict.md` 與 HTML，分開列 Q1/Q2 偵測及準確率、三組與四型態、Q3、七臂加 RDDM 總表、warning／機制數字、無 GT 描述、事後觀察、限制與缺漏。最後更新 `docs/實驗脈絡總覽.md`，推 DET3 分支並開往 main 的 PR，不合併。

## 修訂

預註冊提交時無修訂。正式執行前若按既定規則修復問題，只在此處追加日期、原因與影響；正式結果不回填成先驗預測。無法自行處理且會影響結論的設計決定須停下詢問。
