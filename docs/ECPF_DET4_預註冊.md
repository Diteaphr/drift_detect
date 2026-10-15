# DET4 預註冊：warning × confirm 偵測器交叉矩陣

**登記：** 2026-10-15（Asia/Taipei）。本文件在任何 DET4 新實作、preset、smoke 或正式執行前獨立提交。研究承接 [DET1 預註冊](ECPF_DET1_預註冊.md)、[DET2 預註冊](ECPF_DET2_預註冊.md)、[DET3 預註冊](ECPF_DET3_預註冊.md)及其正式 verdict；正式結果不得回填為事前假設。本輪執行分支為 `shawn/det4-warning-confirm-matrix`，由 DET3 `ab44a59` 建立並合併 `origin/main` `cf9e92a`，merge commit 為 `e493d1a1`。PR #9 已於本輪開始時重新開啟。

**頂層結論框架：** DET4 將 Dual ADWIN 拆成 warning 與 confirm 兩個零件，分別在論文 ECPF（S0）與完整系統（S1）下跑 `3 × 3` 交叉矩陣。Q1/Q2 只以預先鎖定的 T1 配對母體判定；Q3 只有 `warning=ADWIN, confirm=HDDM-A` 是事前候選，且須同時通過 T1 與從未用於 DET 的 T3；Q4 對全部 23 個非迴歸資料集描述跨資料集穩健性。所有 ECPF pipeline 結果只做組內比較，不與 Cerqueira et al. 的 detector-only SOTA 並列。

## 先用全 registry 盤點鎖定 23 個非迴歸資料集

盤點來源為 `python3 scripts/run_benchmark.py --list-datasets --json` 的 registry 輸出與 `configs/datasets_0921.json`。2026-10-15 初次盤點缺少 `airlines_full`、`covertype_full`、`injected_paper_covertype`；已依 `missing_hint` 執行 `prepare_all.py --full`，重跑後 26/26 全部可用。`GT=無` 的資料只報分類與成本；`GT=sibling` 讀同名 drift 檔；`GT=generator` 由 runner 依固定 seed 產生。`insects_incremental_balanced` 的 sibling GT 是空集合，不進 TP/FP/X。

| dataset | task／role | 可比性 | GT | 串流 × 長度 | E／DET 使用史 | DET4 |
|---|---|---|---|---:|---|---|
| `electricity` | binary／report | 可比 | 無 | 1 × 45,312 | benchmark／E 來源曾用；非 DET | 納入 |
| `airlines` | binary／report | 不可比：僅前 100k | 無 | 1 × 100,000 | 未用於 DET | 納入 |
| `covertype` | multiclass／report | 不可比：僅前 100k | 無 | 1 × 100,000 | E13 注入來源曾用；非 DET | 納入 |
| `airlines_full` | binary／report | 可比 | 無 | 1 × 539,383 | 未用於 E／DET | 納入 |
| `covertype_full` | multiclass／report | 可比 | 無 | 1 × 581,012 | 未用於 DET | 納入 |
| `gas_sensor_drift` | multiclass／report | 不可比：文獻協定不同 | 無 | 1 × 13,910 | E 注入來源曾用；非 DET | 納入 |
| `ai4i2020` | binary／report | 不可比：無串流 benchmark | 無 | 1 × 10,000 | E 開發排除；非 DET | 納入 |
| `metro_interstate_traffic` | regression／report | 不可比 | 無 | 1 × 48,204 | 非 DET | **排除：迴歸** |
| `bike_sharing` | regression／report | 不可比 | 無 | 1 × 17,379 | 非 DET | **排除：迴歸** |
| `insects_abrupt_balanced` | multiclass／report | 可比 | sibling，非空 | 1 × 52,848 | E／DET1–3 曾用 | 納入 |
| `insects_incremental_balanced` | multiclass／report | 可比 | sibling，**空** | 1 × 57,018 | E／DET1–3 曾用 | 納入；不算偵測指標 |
| `insects_incremental_gradual_balanced` | multiclass／report | 可比 | sibling，非空 | 1 × 24,150 | E／DET1–3 曾用 | 納入 |
| `insects_incremental_abrupt_reoccurring_balanced` | multiclass／report | 可比 | sibling，非空 | 1 × 79,986 | E／DET1–3 曾用 | 納入 |
| `insects_incremental_reoccurring_balanced` | multiclass／report | 可比 | sibling，非空 | 1 × 79,986 | E／DET1–3 曾用 | 納入 |
| `injected_electricity` | binary／report | 不可比：舊注入協定 | sibling | 80 × 最多 45,312 input rows | E 曾用；非 DET 正式母體 | 納入 |
| `injected_airlines` | binary／dev | 不可比、開發用 | sibling | 80 × 最多 100,000 input rows | 未用於 DET | 納入 |
| `injected_ai4i2020` | binary／dev | 不可比、開發用 | sibling | 80 × 最多 10,000 input rows | 未用於 DET | 納入 |
| `injected_covertype` | multiclass／report | 不可比：舊注入且截斷 | sibling | 80 × 最多 100,000 input rows | E13 曾用；非 DET | 納入 |
| `injected_gas_sensor_drift` | multiclass／report | 不可比：舊注入協定 | sibling | 80 × 最多 13,910 input rows | E 曾用；非 DET | 納入 |
| `injected_paper_electricity` | binary／report | 僅 detector preset 可與文獻比 | generator | 400 × 45,312 input rows | DET1–3 前 20 trials 曾用；E 未用此精確母體 | 納入全部 50 trials |
| `injected_paper_covertype` | multiclass／report | 僅 detector preset 可與文獻比 | generator | 400 × 100,000 input rows | 未用於 DET | 納入全部 50 trials |
| `injected_paper_gas_sensor_drift` | multiclass／report | 僅 detector preset 可與文獻比 | generator | 400 × 13,910 input rows | 未用於 DET | 納入全部 50 trials |
| `synthetic_binary` | binary／dev | 不可比、開發用 | sibling | 40 × 100,000 | E 曾用；非 DET1–3 正式母體 | 納入 |
| `synthetic_multiclass` | multiclass／dev | 不可比、開發用 | sibling | 40 × 100,000 | E／DET1–3 曾用 | 納入 |
| `synthetic_regression` | regression／dev | 不可比、開發用 | sibling | 40 × 100,000 | E 曾用 | **排除：迴歸** |

**So what：** 本輪涵蓋全部可用的非迴歸 registry，而不是只延伸 DET 的 205 條開發／判定母體；但 Q1/Q2 仍鎖定 T1，避免加入大量新資料後改寫原問題。沒有 GT 的真實資料不能支持偵測勝負；pipeline preset 在 `injected_paper_*` 亦不能支持文獻 SOTA 聲明。

## 以 DET3 實測鎖定約 6.5–9 天的執行規模

DET3 正式執行 615 個新 run、workers 6、零失敗，實耗 3,101 秒。DET4 牆上時間以 DET2／DET3 的實測為基準；已有 DET 實測者直接採其量級，新長串流依「列數 × 特徵數」相對 `injected_paper_electricity` 外推，再保留成本量測及排程誤差。以下是計畫值，不是正式結果。

| dataset | 正式 runs | 可沿用 | 新跑 | workers 6 粗估牆時 |
|---|---:|---:|---:|---:|
| `electricity` | 18 | 0 | 18 | <0.1 h |
| `airlines` | 18 | 0 | 18 | <0.1 h |
| `covertype` | 18 | 0 | 18 | 0.2–0.3 h |
| `gas_sensor_drift` | 18 | 0 | 18 | 約 0.1 h |
| `ai4i2020` | 18 | 0 | 18 | <0.1 h |
| `airlines_full` | 18 | 0 | 18 | 0.2–0.3 h |
| `covertype_full` | 18 | 0 | 18 | 1.3–2.0 h |
| `insects_abrupt_balanced` | 18 | 5 | 13 | 約 0.03 h |
| `insects_incremental_balanced` | 18 | 5 | 13 | 約 0.04 h |
| `insects_incremental_gradual_balanced` | 18 | 5 | 13 | 約 0.02 h |
| `insects_incremental_abrupt_reoccurring_balanced` | 18 | 5 | 13 | 約 0.05 h |
| `insects_incremental_reoccurring_balanced` | 18 | 5 | 13 | 約 0.06 h |
| `injected_electricity` | 1,440 | 0 | 1,440 | 1.2–1.8 h |
| `injected_airlines` | 1,440 | 0 | 1,440 | 2.3–3.5 h |
| `injected_ai4i2020` | 1,440 | 0 | 1,440 | 0.2–0.3 h |
| `injected_covertype` | 1,440 | 0 | 1,440 | 18–27 h |
| `injected_gas_sensor_drift` | 1,440 | 0 | 1,440 | 6–9 h |
| `injected_paper_electricity` | 7,200 | 800 | 6,400 | 5–8 h |
| `injected_paper_covertype` | 7,200 | 0 | 7,200 | 90–135 h |
| `injected_paper_gas_sensor_drift` | 7,200 | 0 | 7,200 | 30–45 h |
| `synthetic_binary` | 720 | 0 | 720 | 0.8–1.2 h |
| `synthetic_multiclass` | 720 | 200 | 520 | 1.9–3.0 h |
| **合計** | **30,456** | **1,025** | **29,431** | **約 157–216 h（6.5–9 天）** |

另以 workers 1 在 `electricity` 跑 18 個組合作嚴格時間比較，總正式執行量為 30,474 runs。T1 為 3,690 格（其中沿用 1,025）、T3 為 4,320 格，其餘為 22,446 格。現有 DET1–3 benchmark 輸出 172 MiB；依逐筆預測檔、manifest、metrics、warning events 與長串流外推，DET4 預估新增 4–6 GiB。資料準備完成後磁碟剩餘 37 GiB，高於 20 GiB 門檻；若後續低於門檻，先跳過尚未開始的 `airlines_full`、`covertype_full`，不刪除既有輸出。

## 固定兩個框架，只改 warning 與 confirm 零件

| ID | 固定框架 | 範本 preset |
|---|---|---|
| **S0 論文 ECPF** | `ecpf_paper` 底座；leader 0/1 誤差；lw0；無 timeout、reference、guard | `det1_*_lw0` |
| **S1 完整系統** | 同底座加 frozen reference（warmup 500）、leader guard、1000 步 timeout、`ecpf_guard_frozen_scale=500`、lw1 | `det3_full_*_lw1` |

兩個框架都使用單棵 Hoeffding Tree、warm start 200、`river==0.21.2`、`ecpf_swap_policy=strict`、`ecpf_fade_policy=ecpf`、`ecpf_fade_enabled=true`、`ecpf_max_pool_size=10`。S1 是 DET3 的「完整元件 + lw1」，不是 `e10bft.json` 原樣。新 preset 的 `role` 一律為 `ablation`；不修改 `ecpf_paper.json`、`e10bft.json`、DET1–3 preset 或 `configs/benchmark_defaults.json` 的 `main_preset`。

warning 與 confirm 各取 `{ADWIN, HDDM-A, RDDM}`，共 9 格 × 2 框架 = 18 組。ADWIN warning 使用雙向 `delta_w=0.1`，ADWIN confirm 使用雙向 `delta=0.05`；HDDM-A 使用 River 0.21.2 預設；RDDM 使用 DET1 已驗證的 `MOARDDM` 與 MOA 預設。DDM 與 MagSeed 不納入。

## 先鎖定兩個獨立實例的混搭語意，再用對角閘門驗證

實作沿用已存在且預設關閉的 `PipelineConfig.ecpf_warning_detector` 與 `ecpf_drift_detector`；本輪把後者解讀為 confirm detector。兩欄皆為 `None` 時必須走既有路徑且結果逐位元不變。

既有路徑查核結果：

1. `ECPFAdwinFamilyDetector` 的 warning 與 confirm 是兩個獨立實例，每步讀相同指定訊號；ADWIN warning 只有瞬時觸發，沒有自行解除 zone。
2. Dual ADWIN 的 confirm 在沒有 active warning 時，pipeline 不建立 drift detection，也不換模型；confirm arm 依既有 detector 行為自行 reset，warning arm保持原狀。
3. `ECPFZoneDetector` 的 HDDM-A／RDDM 用單一 detector 同時產生 warning zone 與 drift；drift 當步也被視為 warning，因此可用一筆 buffer 完成確認。離開 zone 而未 drift 時，pipeline 關 warning 並清空 buffer。
4. 有效確認後，Dual ADWIN 內部 reset 兩個 arm；HDDM-A 在 wrapper 內 reset，RDDM 依其 MOA replay/reset 語意處理。S1 的 guard 存在時，pipeline 另將 guard 與主 detector 一起 reset。
5. timeout 目前呼叫 `reset_warning()`：Dual ADWIN 只 reset warning arm；zone wrapper 的 `reset_warning()` 是 no-op，因此可能在下一步立即重開。這是 DET3 已知行為，對角重現優先於事後修正。

DET4 預設混搭語意固定如下：

1. warning 與 confirm 為獨立實例，每步都讀 S0 leader 0/1 誤差或 S1 frozen-reference loss。
2. warning 實例觸發 warning 時開 buffer；S0 同時凍結訓練。ADWIN warning 不會自行解除。
3. HDDM-A／RDDM warning 實例的 zone 結束且尚未確認時關閉 warning 並清空 buffer；confirm 實例繼續累積，不因 zone exit reset。
4. confirm 實例 drift 但沒有 active warning 時，沿 Dual ADWIN 行為忽略該次確認；confirm 依原 detector 語意 reset，warning 不受影響。
5. active warning 下 confirm 時才是有效確認；兩個實例均 reset。S1 leader guard 繼續獨立 OR 合併並照 DET3 reset。
6. S1 1000 步 timeout 關閉 buffer。為優先重現既有對角格，warning=ADWIN 時 reset warning arm；warning=HDDM-A/RDDM 時先保留既有 zone `reset_warning()` no-op 語意。若此安排仍不能同時重現對角，依下列閘門規則處理。

**對角重現優先規則：** 新欄位關閉時先證明 merge 不改結果；新欄位開啟且 `warning=confirm` 時再證明可重現 S0 三個與 S1 兩個 DET 對角。若 merge 已改結果，所有對角重跑。若統一混搭介面無法逐位元重現 zone 對角，全部 9 格改採目前 Dual ADWIN 路徑的統一語意、zone 對角全部重跑，並在本文件「修訂」及 verdict「偏離」記錄與 DET HDDM-A/RDDM 的差異。

## 把 T1、T3 與全部資料分工，避免挑最好格

| 子集 | 固定內容 | 用途 |
|---|---|---|
| **T1 主判定** | `injected_paper_electricity` 每格 trials 1–20（160）、`synthetic_multiclass` 40、5 個 INSECTS，共 205 條 | Q1、Q2；與 DET1–3 對照 |
| **T3 保留驗證** | `injected_paper_electricity` 每格 trials 21–50，共 240 條 | Q3 唯一事前候選的確認 |
| **全部** | 23 個非迴歸資料集 | Q4 與逐資料集報告 |

全部資料都跑完整串流；分析子集不改執行範圍。`injected_paper_*` 固定 8 格 × 50 trials，不因耗時縮減。

## 所有指標由 runner、evaluator 與既有 DET 分析定義產生

正式執行只經 `scripts/run_benchmark.py`，標準彙總只經 `scripts/compare_sota.py --root outputs/benchmark/det4`；不修改 `configs/datasets_0921.json` 或 `src/metrics/evaluate_run.py`。分類與偵測標準指標來自 `metrics.json`／`runs.csv`，DET 衍生指標 X 與 FP@1000 沿用已有單元測試的 `scripts/analyze_det*_formal.py` 定義。

**判定用指標（同 DET3）：** prequential accuracy、GT 後 1000 座標步 accuracy、FP@1000、E11 excess hits `X=episode_hits−C`。`insects_incremental_balanced` 因 GT 空集合，不算 TP、FP、X 或 drift 後 accuracy。

**skill 標準指標（全報、不改主要判定）：**

- 分類：`acc_prequential`、`acc_window1000_mean`、`kappa`、`kappa_t`、`kappa_m`、`macro_f1`，每列並列 `baseline_no_change_acc`、`baseline_majority_acc`。
- 有 GT 的偵測：`tp`、`fp`、`fn`、`precision`、`recall`、`f1`、`episode_recall`、`mdt`、`ndt`、`far`、`ar` 及全部 `*_paper_window` 欄位。
- `injected_*` 依 cell 對 trials 使用 `pool_detection_runs`，先合計 TP/FP/FN 再算 F1，不平均逐 trial F1。
- 成本：`runtime_s`、`cpu_time_s`、`instances_per_s`、`rss_increment_mb`、`model_size_final_mb`、`ram_hours_gb`、`concurrent_runs`、`machine`。
- 機制：凍結步數、warning 開啟、自行關閉、timeout 關閉、確認、結束仍開啟、平均確認延遲。事件守恆為 `開啟 = 自行關閉 + timeout + reference switch + 確認 + 結束仍開啟`；若另有明示關閉原因，須單列且納入守恆。

**可比性聲明：** 18 組全是 ECPF pipeline preset。registry 對 `injected_paper_*` 只允許 `detector` preset 與 Cerqueira et al. 比較，因此 DET4 偵測結果只能做 18 組之間比較；不得與文獻 SOTA 並列或宣稱勝出。accuracy 只與本 harness 重跑或同 protocol 的既有輸出比較。

## 分開估計 warning 列效果與 confirm 欄效果

S0、S1 分開產生 accuracy、drift 後 accuracy、FP、X 四張 `3 × 3` 熱圖。T1 上每一對比較都做三資料層的配對 bootstrap 10,000 次，固定 seed `20261012`，95% percentile CI；同一抽樣索引套用兩臂，CI 含 0（含端點）判持平。accuracy 每次重算正確數／有效預測數；FP 與 X 依 run 聚合，不先平均資料組。

- **列效果：** 固定 confirm，比較三種 warning。
- **欄效果：** 固定 warning，比較三種 confirm。
- **每格對 HDDM-A 對角：** 偵測需 `ΔFP` CI 全負且 `ΔX` CI 全正才算優於；兩者均顯著朝不利方向判不如，其餘持平。accuracy 的 CI 全正為優於、全負為不如，其餘持平。兩軸分開，不合成總分。

## 事前預測只允許 H3 指定格接受保留驗證

- **H1（S0）：** warning 選擇影響較大；warning=ADWIN 的三格凍結步數最多、accuracy 最低，不論 confirm。
- **H2（S1）：** confirm 選擇影響較大；confirm=ADWIN 的三格 X 與 drift 後 accuracy 最低。
- **H3（S1；Q3 唯一候選）：** `warning=ADWIN, confirm=HDDM-A` 在偵測與 accuracy 兩軸都不輸 HDDM-A 對角。
- **H4（Q4）：** 無方向預測，只描述含 ADWIN 組合的跨資料集變異與最差情況。

H3 必須在 T1 與 T3 都不輸才可宣稱成立。其他格即使 T1 更好，也只能列為「事後觀察」，並附 T3 結果，不得改列候選或宣稱勝出。

## Q4 用逐資料集相對差判斷穩健性，不把不同規模混成單一平均

每個框架內，對每一格、每個資料集計相對 HDDM-A 對角的 `Δaccuracy`；有非空 GT 者另計 `ΔX`。報告中位數、最差資料集與「CI 全負」資料集數。多串流資料集以串流為單位做配對 bootstrap；單串流只報點估計並明示不能形成串流層 CI。23 × 9 heatmap 分 S0、S1，各資料集保留自身尺度，不以總樣本數加權掩蓋最差資料集。

## 逐位元閘門、smoke 與正式執行順序先於結果解讀

### 實作與閘門

1. 新欄位預設關閉時，固定 seed `20261012` 從 DET1／DET3 正式矩陣按 registry 順序抽 injected 9、synthetic 5、INSECTS 1 條；重跑 S0 三對角與 S1 兩對角。`y_true`、`y_pred`、`alarm_idx` 及適用的 `alarm_idx_input` 必須 dtype、shape、逐位元相同。
2. 新欄位開啟且設成對角組合時，同一 15 條重跑相同五個對角並逐位元比較。
3. 單元測試固定驗證：warning／confirm 實例獨立且每步各更新一次；zone 自行關閉清空 buffer；有效確認後兩者 reset；無 active warning 的 confirm 被忽略；S1 timeout 與 guard 保持作用。
4. merge gate 失敗則不沿用任何 DET 對角；混搭 diagonal gate 無法修正則依前述 Dual 路徑統一語意重跑 zone 對角。其他無法修正的程式／資料問題只跳過受影響 run，標不可判定。

### Preset 與 smoke

新增 `det4_{s0|s1}_w{adwin|hddma|rddm}_c{adwin|hddma|rddm}` 共 18 個 `ablation` preset。S0 只由對應 DET1 範本改 detector 欄位；S1 只由對應 DET3 範本改 detector 欄位。結構化差異表寫到 `outputs/det4/preset_diff.md`。

每組 smoke 固定跑 injected 2 條、synthetic 2 條、INSECTS abrupt 1 條，再對其餘每個資料集取 registry 第一條，全部 `--max-steps 5000`，隔離於正式根目錄。核對 manifest、評分、成本欄位、warning 事件守恆；S1 `ecpf_learn_during_warning=true`，因此凍結步數必須為 0。程式問題修正後只重跑受影響 smoke，不改參數或判準。

### 正式執行與成本

正式輸出根目錄固定為 `outputs/benchmark/det4/`，順序為：T1 → T3 → 其餘短資料集 → `injected_paper_covertype`／`injected_paper_gas_sensor_drift` → `airlines_full`／`covertype_full`。使用 workers 6、`--resume`、`--record-warning-events`，在 tmux 背景執行，整體命令包在 `caffeinate -dims`，logs 寫入 `outputs/det4/logs/`。每個 run 失敗重試一次；仍失敗才列入「失敗與缺漏」並將受影響判定標不可判定。每批完成後提交彙總，不提交大型逐 run 輸出。

workers 6 的 wall time 只作參考，因 `concurrent_runs>1`；RSS 仍可比較。另以 workers 1 在 `electricity` 對 18 組各跑一次，作嚴格時間比較。實際耗時超過估計時繼續執行並更新 ETA；剩餘磁碟低於 20 GiB 時只跳過尚未開始的兩個 full 真實資料集。

## Verdict 必須先回答 H1–H3，再描述 Q4 與限制

`outputs/det4/det4_verdict.md` 與 HTML 固定包含：

1. S0、S1 各四張 `3 × 3` heatmap，格內附 accuracy、drift 後 accuracy、FP、X 數值。
2. warning 列效果與 confirm 欄效果表及 CI；H1、H2 是否成立。
3. 每格對 HDDM-A 對角的偵測／accuracy 雙軸判定。
4. H3 指定格在 T1、T3 的結果與結論。
5. 23 資料集 × 9 格的 `Δaccuracy` heatmap（S0、S1 各一），以及中位數、最差資料集與 CI 全負數；有 GT 者另報 `ΔX`。
6. 資料類別（真實、INSECTS、注入 CSV、注入 paper、合成）及 drift 類型（突變、漸變、incremental、recurring）分層。
7. 每格凍結步數、warning 自行關閉比例、timeout、確認與平均延遲。
8. `compare_sota.py --root outputs/benchmark/det4` 產生的每資料集 × 組別標準指標與成本總表，明示嚴格時間與並行參考時間。
9. 事後觀察、失敗與缺漏、修訂／偏離、限制。限制至少明列：單棵 HT、River ADWIN、River 預設 HDDM-A、synthetic 與部分 INSECTS／injected 曾用於開發、迴歸未測、混搭語意為本研究定義、pipeline 偵測指標不可與文獻比較。

最後只更新 `docs/實驗脈絡總覽.md` 的 DET4 一列；推送功能分支並開往 main 的 PR `DET4: warning x confirm detector matrix`，不合併、不直接 push main。

## 自行處理規則確保長任務不中途改研究問題

規格未明處採最保守、最接近 DET3 的做法並在「修訂」追加理由。合併差異、混搭 diagonal 差異、資料缺漏、失敗重試、超時與磁碟門檻均按本文件既定規則處理，不因正式結果調參、不擴充 detector、不刪除或覆寫既有輸出。每階段單獨 commit，訊息使用英文祈使句。

## 修訂（只追加，不改寫原始預測）

預註冊提交時無修訂。後續任何語意調整、無法重現、跳過資料、成本或執行偏離均在此追加日期、原因、影響 run 與對結論的限制。

### 2026-10-15：更正無 active warning 時的 confirm reset 範圍

在將既有行為寫成單元測試時重新逐行核對 `ECPFAdwinFamilyDetector.update_values()`：confirm arm 觸發 drift 後會在回傳前呼叫 `self.reset()`，因此即使 pipeline 因沒有 active warning 而不產生 drift detection，**warning 與 confirm 兩個 arm都會 reset**。上文「既有路徑查核結果」第 2 點及「DET4 預設混搭語意」第 4 點中「warning 保持原狀」的描述不正確，由本修訂取代；其他行為與假設不變。DET4 統一採既有 Dual ADWIN 行為：任一 confirm drift 都 reset 兩個 detector 實例；只有 active warning 下的 confirm 才會產生 ECPF drift、模型切換及 confirmed 關閉事件。
