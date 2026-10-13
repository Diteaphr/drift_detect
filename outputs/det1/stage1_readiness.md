# DET1 階段一：資料齊全，但判定口徑與 oracle 接線需先確認

日期：2026-10-12（Asia/Taipei）。基準：main `929dd20`。分支：`shawn/ecpf-detector-comparison`。
本階段只讀取架構、檢查資料與記錄待確認事項；未跑新模型實驗、未改 evaluator、既有 preset 或 registry。

## Zone 可沿用 dual_adwin 模式，warning 訓練與 timeout 均會執行

| 項目 | 已確認行為 | 來源 |
|---|---|---|
| 接線 | `use_ecpf=True`、`ecpf_signal_mode="dual_adwin"`、`ecpf_zone_detector="ddm"` 或 `"hddm_a"`；非空 zone 名稱優先取代雙 ADWIN。亦接受 ADWIN family 的其他模式，但 DET1 建議固定 dual_adwin | `src/pipeline.py:69,204` |
| 輸入 | Zone 只使用 `drift_value`，四捨五入轉成 0/1；不使用 warning_value。預設 error 為 leader 的分類誤差；reference 與 guard 預設關閉 | `src/ecpf_detector.py:41`、`src/config.py:204,211,264` |
| Warning 開啟 | detector 的 warning 區開 buffer；drift 當步亦視為 warning，因此可能同一步才開 warning 並確認，不保證實際資料一定先 warning 後 drift | `src/ecpf_detector.py:45`、`src/pipeline.py:817` |
| 未確認即離區 | 關閉 warning、清除起點、丟掉 buffer；該步回到正常訓練，不重播丟棄資料 | `src/pipeline.py:828,1170` |
| `learn_during_warning=False` | warning 開啟的非確認步直接返回，不訓練 leader/shadow；確認步由 drift handler 訓練新模型 | `src/pipeline.py:557,883`、`src/ecpf.py:597` |
| `learn_during_warning=True` | 上述 warning 步會呼叫 ECPF `on_stream_instance`，訓練 leader 與存在的 shadow，也推進對決與換將 | `src/pipeline.py:544`、`src/ecpf.py:449` |
| Timeout | ADWIN family 共用分支，zone 也會執行；条件為 warning age **大於**設定值，1000 因此在 age=1001 時觸發 | `src/pipeline.py:796` |
| Zone timeout 的限制 | 清空 buffer，但 zone 的 `reset_warning()` 是 no-op，且本步 warning 已在 timeout 前算好；若仍在 warning 區，立即以當步重開 buffer。它不會讓單一 detector 重新建立統計基準 | `src/ecpf_detector.py:38`、`src/pipeline.py:814,817` |

DET1 保守設定：A2–A5 使用 dual_adwin 模式搭配 zone 名稱、error 輸入、timeout=0；只讓 A1t 使用 timeout=1000。所有 lw 值明寫，不依賴預設。

已閱讀任務指定背景、benchmark skill/protocol、全部既有 preset，以及 archived E9 預註冊與 verdict。Runbook 的「只有 adwin_dual」及預設 delta=0.05 描述已落後於程式：目前另有 zone 路徑，`src/config.py` 的 delta 預設為 0.01；DET1 應明寫 0.05。

## 四組資料均存在，但 incremental 沒有可計分的 GT

實際執行：`python3 scripts/run_benchmark.py --list-datasets --json`。
系統 `/opt/homebrew/bin/python3`（3.14）第一次因缺 numpy 失敗。其後在 `/private/tmp/det1-inspect-venv` 安裝 numpy/pandas，使用該 venv 的 python3 成功執行同一指令；完整結果保存於 `stage1_dataset_inventory.json`。
該 venv 僅供清單檢查，未安裝 river/CapyMOA，不是正式實驗環境。主環境、requirements 未變更；正式環境仍須在後續階段建立並驗證 river==0.21.2。

| Dataset | 可用 | 串流 × 筆數 | registry role | GT |
|---|---|---|---|---|
| injected_paper_electricity | 是 | 400 × 原始 45,312（50 trials × 8 cells；部分注入方式會刪列） | report | generator 提供，input 座標 |
| insects_abrupt_balanced | 是 | 1 × 52,848 | report | 5 個點 |
| insects_incremental_balanced | 是 | 1 × 57,018 | report | sibling 檔為 `[]` |
| synthetic_multiclass | 是 | 40 × 100,000 | dev | 40 份 GT 皆非空 |

來源：`configs/datasets_0921.json`、實際 CSV 行數與 sibling GT 檔。無須準備缺失資料。
incremental 的 `tp/fp/episode_recall/mdt/far` 在 evaluator 中為 null，不能把所有警報當 FP，更不能以 0 補值加入 P1/P2。

## 超額命中尚未實作，需保留 E11 的 episode 語意

`src/metrics/evaluate_run.py` 沒有 excess hits。E11 定義：每次執行窗外步數 O，λ=FP/O，C=Σ(1−exp(−λL))，X=命中數−C，跨執行加總。
來源：tag `archive/ecpf-misread-2026-10` 的 `docs/ECPF_E11_逾時與超額命中_預註冊.md` 與 `scripts/run_e1_e2.py:648–668`。

现 evaluator 的 TP 計每個窗內警報，可對同一 GT 累計多次；C 卻是各 GT「至少命中一次」的期望。直接使用 evaluator.tp−C 會混合兩種單位。
建議分析腳本獨立報 `episode_hits−C`，並並列既有 TP/FP；GT 窗長與聯集以離散座標、評估範圍截斷後計算，O=0 時標為不可估計，不以 λ=0 代替。1000 步窗與 injected registry 的 2500 步窗分開報；不改 evaluator 指標。
這會影響 P2，必須在預註冊前確認。本階段不寫新分析程式，以遵守「任何新程式碼之前先預註冊」；階段一第 3 步要求立即補寫分析程式與此順序有衝突，列為待確認項目。

## Oracle 與診斷紀錄需要後續補線，否則無法完成預定指標

- `run_benchmark.run_one` 取得 GT 後未傳給 `run_pipeline`，config 的 oracle GT 預設空，因此只新增 A0 preset 會得到零 oracle 警報。後續應傳入 GT 起點，injected 需把 input 座標映射至保留列，明定被刪除起點與延遲的處理。
- 現有 oracle 將起點當步放入 buffer，長度到 60 就確認，所以實際在 `d_s+59`，與任務表「+60 筆」差一筆。需明定沿用現有模式，或在不影響既有結果的新增選項下精確執行 +60。
- Benchmark 目前只保存 y_true/y_pred、alarm_idx/alarm_ts（以及 input alarms）、manifest/metrics；没有完整 warning 開/關事件、未確認 buffer、凍結步數與 reuse 勝出統計。tracer 預設關閉，stage1 又只留漂移附近資料。後續需 observer-only 紀錄，不修改 adaptation 邏輯，不靠事後從警報推算 warning。
- manifest 已有 commit、effective_config、versions；檔案資料保存 CSV hash，generated 保存 source hash、generator、seed。沒有生成串流本身的 hash，若 smoke 要求該項，需要額外記錄。
- runner 有 `--trials/--cells/--limit-files` 及 merge 舊 runs.csv；**沒有 resume/skip-completed**，重跑同一 job 會覆寫原 run dir，且 runs.csv 到整批完成才保存。正式執行前需補跳過已完成且 provenance 一致的 jobs 或外部續跑機制，smoke 與正式使用不同 out-dir。
- compare_sota 預設排除不具可比性的 ECPF injected 與 synthetic。DET1 必須使用 `--include-noncomparable`，並只納入本實驗的 presets，ECPF F1 一律為參考。
- 本 checkout 未找到 Chen/Koh/Riddle 2015 PDF，`docs/refs/` 不存在。依任務要求，階段三到 MagSeed 時須停止等待 PDF，不能使用近似 SEED 代替。

來源：`scripts/run_benchmark.py:273–295,435–518,659–714`、`src/pipeline.py:689–723`、`src/tracing.py`、`scripts/compare_sota.py`。

## 正式執行約 8,868 次，時間需由 smoke 更新

計數假設：14 個 DET1 ECPF presets + 不變的 A6/e10bft；A0 的 lw0/lw1 在無 GT 的 incremental 略過；detector-only 共 5 組；hf10 為指定 A1/A3/A5 × 2 lw，單次種子（尚待預註冊明定）。

| 工作 | 計算 | 次數 |
|---|---|---:|
| injected 正式 | 400 × (15 ECPF/reference + 5 detector) | 8,000 |
| insects abrupt | 1 × 15 | 15 |
| insects incremental | 1 × 13，略過 2 oracle | 13 |
| synthetic ht | 40 × 15 | 600 |
| synthetic hf10 | 40 × 6 | 240 |
| 正式合計 | | 8,868 |
| smoke（不含 hf10，依階段五原文） | 24 × 20 + 15 + 13 + 40 × 15 | 1,108 |
| smoke + 正式 | 不含閘門、MOA check、必要重跑 | 9,976 |

若 A6 不納入正式清單，正式減 442 次至 8,426，smoke 減 66 次至 1,042。完整 trial 重跑 existing det_adwin 是否使用新隔離根目錄，也須於預註冊鎖定，不能覆寫既有輸出。

本機 10 logical CPUs。仅讀取既有 runs.csv 的 runtime，未使用 report 的品質或偵測結果來選參數：electricity ecpf_paper 21.75s、e10bft 29.84s；insects abrupt ecpf_paper 90.43s；injected det_adwin 的 400 次 runtime 中位數 2.80s。
粗估 HT 主批約 60–120 CPU 小時；hf10 額外約 20–60 CPU 小時（尚無相同設定實測，僅成本規劃範圍）。以 4–8 個有效 workers 粗估正式約 10–45 小時，另加 smoke 與新 detector 驗證。這不是完成時間承諾：warning 凍結、模型池 deep-copy 與 MagSeed 實作可能明顯改變耗時；階段五需用逐組 smoke 更新。

## 階段二前須確認影響結論的決定

1. **P1/P2 資料範圍：** 建議用 injected + insects abrupt + synthetic 三個有 GT 家族；INSECTS incremental 只報 adaptation/警報數/runtime，synthetic incremental 仍可獨立判定。保留 registry 的 dev 身分，預註冊宣告此次為鎖參數後的評估，且非全新 holdout（E11–E14 已用過部分種子）。
2. **超額命中：** 建議依 E11 使用 episode hits−C；Cerqueira TP/FP 原值另報，E11 式一個 episode 一次 hit 與其餘警報的 FP 口徑需在分析定義中明寫。P2 主窗建議統一 1000；injected 2500 另列文獻口徑。
3. **A0：** 確認「60 筆 buffer」或「真實起點後 +60 筆」及 injected 是否以原始 input 筆數計延遲。
4. **執行範圍：** 建議 A6 在四組皆跑一次、不乘 lw；hf10 單種子先沿用任務所列 6 組；新分析程式、oracle/observer/resume 補線全部延後預註冊核准後。

本階段至此停止；未開始階段二預註冊。
