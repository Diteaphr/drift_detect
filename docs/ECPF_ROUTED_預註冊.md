# ECPF 分流確認實驗預註冊

**登記：** 2026-10-23（Asia/Taipei），分支 `feat/routed-detectors`，實作 commit `356a3d5`。本文件在 dev 調參與正式執行前提交；正式結果不得回填為事前假設。判定方式沿用 [DET4 預註冊](ECPF_DET4_預註冊.md)。

**問題：** 讓 ADWIN 與 HDDM-A 同時監看，依規則決定由誰確認 drift，能否在不損失正確率的前提下改善偵測？分類器（Type-LDD）判斷 drift 類型值不值得用？

## 框架與組別

所有組別都建立在 DET 的 S1 框架（`det3_full_dual_adwin_lw1`）：凍結參照模型、只認變差的 leader guard、1000 步 warning timeout、凍結守衛尺度、warning 期間繼續學習。這是使用者指定的主方法版本。

| 組別 | preset | 說明 |
|---|---|---|
| 設計 1：分類器分流 | `s1route_tr_c{C}` | warning 開啟後 100 步用 Type-LDD 判斷；sudden → HDDM-A 確認，否則 ADWIN |
| 設計 2：誰先發誰確認 | `s1route_fw_c{C}` | 先發 warning 的那組負責確認 |
| 聯集 | `s1route_union_c{C}` | 任一組的 drift 都算確認 |
| 只用 ADWIN | `det4_s1_wadwin_cadwin` | 沿用 DET4 結果，不重跑 |
| 只用 HDDM-A | `det4_s1_whddma_chddma` | 沿用 DET4 結果，不重跑 |
| e10bft lw0 | DET3 `F-D0-lw0` | 沿用 DET3 結果；warning 期間不學習，只作描述性參考 |

ADWIN 組與 HDDM-A 組的 detector 與 DET4 對角完全相同（ADWIN warning `delta_w=0.1`、confirm `delta=0.05`；HDDM-A 用 River 0.21.2 預設），不調整靈敏度。

## 共同規則（實作於 `detectors/meta_ecpf/routed.py`）

1. 任一組發 warning（或 drift）就開啟事件；同一步同時發，視為 HDDM-A 先發。
2. 事件期間各組的 drift 都會記住；確認者決定後，若它已發過 drift 就在當下確認。非確認者的 drift 不確認，只記錄。
3. 由 HDDM-A 開啟的事件，在設計 2 與聯集中，HDDM-A 離開 warning 區就結束（同 DET4 HDDM-A 對角）；設計 1 的事件只會因確認或 timeout 結束，確保能收滿 100 步。ADWIN 開啟的事件只會因確認或 timeout 結束。
4. leader guard 與 DET4 S1 相同：獨立運作、以 OR 合併，不參與分流。
5. 冷卻期 C：確認後 C 步內不開 warning、不確認（detector 照常更新），涵蓋 guard。
6. 每次事件記錄先發者、第 100／200／300 步與確認當下的分類結果、確認者與結束原因。

## 可重現性閘門

以 `s1route_fixed_adwin`、`s1route_fixed_hddma`（只輸出單一組、冷卻期 0）在 13 條以上的正式資料流上執行。每個 run 的 `n_scored、correct、alarms、tp、fp、fn、hits、post_correct、post_count、warning_opened、warning_self_closed、warning_timeout、confirmations` 與 X 必須與 `outputs/det4/det4_run_scores.csv` 對應列完全相同。未通過就停止，不進行後續步驟。

**閘門結果（登記前已完成）：** 通過。15 條資料流（synthetic_multiclass 6 種類型各 2 條、3 個 INSECTS）× 2 種固定分流，共 30/30 個 run 全部相同，見 `outputs/routed/gate.md`。

## dev 調參（只在 `synthetic_binary`）

在 `synthetic_binary` 全部 40 條資料流上，三種設計各跑 C ∈ {0, 100, 300}。每種設計各自選 C：**合併 X 不高於 C=0 的前提下，取合併 accuracy 最高者；同分取較小的 C。** 選定後凍結，不再看正式資料調整。

## 正式資料與指標

正式資料為 45 條：`insects_abrupt_balanced`、`insects_incremental_balanced`、`insects_incremental_gradual_balanced`、`insects_incremental_abrupt_reoccurring_balanced`、`insects_incremental_reoccurring_balanced` 各 1 條，`synthetic_multiclass` 40 條（sudden、gradual、incremental 各 10；recurring·sudden 3、recurring·gradual 5、recurring·incremental 2）。報告另分 11 個資料組列點估計。

指標同 DET4：prequential accuracy、GT 後 1000 步 accuracy、FP@1000、E11 excess hits X。`insects_incremental_balanced` 無 GT，不計偵測與 drift 後 accuracy。

比較使用 DET4 的分層配對 bootstrap（synthetic 與 INSECTS 兩層，10,000 次，seed `20261012`，95% percentile CI）。accuracy：CI 全正為優於、全負為不如、否則持平。偵測：ΔFP 的 CI 全負且 ΔX 的 CI 全正為優於，兩者同時顯著反向為不如，其餘持平。

## 事前假設

| 假設 | 比較 | 成立條件 |
|---|---|---|
| H1：設計 2 不比只用 HDDM-A 差 | 設計 2 − 只用 HDDM-A | accuracy 與偵測都不是「不如」 |
| H2：分類器值得用 | 設計 1 − 設計 2 | accuracy 為「優於」 |
| H3：限定確認者有幫助 | 設計 2 − 聯集 | 偵測為「優於」 |

其他比較（對只用 ADWIN、對 e10bft lw0、各資料組、分流診斷、分類器在各時間點判斷是否 sudden 的準確度）只作描述，不作為成立與否的依據。

## 已知限制

1. 沒有保留資料（DET4 的 T3），結論強度低於 DET4。
2. INSECTS 每個資料集只有 1 條、recurring 子組只有 2 到 5 條，分組只能給點估計。
3. `synthetic_multiclass` 在 registry 是 dev 資料集，結果只作組內比較，不與文獻比較。
4. 基線由其他機器產生；以可重現性閘門確認一致。合成資料以 3 條並行執行，執行時間只作參考。
5. 設計 1 必須等 100 步才決定，確認時間可能比單一 detector 晚最多約 100 步。

## 修訂

**修訂 1（2026-10-23，正式結果產生前）：三個設計的冷卻期統一為 C = 300。**

dev 依原規則選出設計 2 與聯集 C = 300、設計 1 C = 0（`outputs/routed/dev_selection.md`）。差距極小：C = 100 在三個設計都沒有擋到任何警報，與 C = 0 完全相同；C = 300 只擋到 15 到 27 次，設計 2 與聯集比 C = 0 多答對 5 筆、設計 1 少答對 19 筆（皆為 4,000,000 筆中）。使用者決定三個設計統一使用 C = 300，讓三者只差在分流方式，比較更乾淨。

這個決定在任何正式資料流跑完之前做出：當時只有冒煙測試（截斷、不可比）與 21 個設計 2 的正式 run 完成，這些 run 的結果沒有被查看，並已刪除重跑。設計 1 因此偏離原規則的選擇（C = 0）；原規則的結果保留在 `dev_selection.json` 的 `choice`，修訂後的設定記在 `final`。正式組別改為 `s1route_fw_c300`、`s1route_tr_c300`、`s1route_union_c300`。

**修訂 2（2026-10-24，正式結果之後的追加實驗）：判斷時間改為第 300 步，並加入兩個 injected 資料集。**

H1–H3 的判定維持原本 45 條、第 100 步的正式結果，不受本修訂影響。本修訂的追加實驗全部屬於**探索性分析**，不作為假設成立與否的依據，理由是判斷時間是看過正式結果與離線測試之後才選的：離線測試（拿正式 run 的誤差序列，在真正 drift 之後固定步數分類）顯示目前的權重在 drift 後 +400 步左右分得最準，而 warning 中位數在 drift 後約 90 步開啟，因此使用者選擇 warning 後第 300 步判斷。

1. 新組別 `s1route_tr_d300_c300`：設計 1 改為 warning 開啟後第 300 步判斷，其餘設定與 `s1route_tr_c300` 相同。
2. 原本 45 條資料流：只補跑 `s1route_tr_d300_c300`，與第 100 步版本及各基線比較。
3. 新資料：`injected_paper_electricity` 與 `injected_paper_gas_sensor_drift`（各 400 條、abrupt／gradual 各半），執行 `s1route_tr_d300_c300`、`s1route_fw_c300`、`s1route_union_c300`。基線沿用 DET4 S1 的 2×2 四格（兩個資料集各 400 條都有）與 DET3 e10bft lw0（只有 `injected_paper_electricity` 前 20 個 trial 的 160 條）。
4. 先以固定分流在兩個 injected 資料集各 8 條（每格 trial 1）跑可重現性閘門，必須與 DET4 完全相同才繼續。
5. 統計方法與判定規則同上；分層加入 injected 一層。injected 資料集的 abrupt 視為 sudden、gradual 視為非 sudden，用於分類器診斷。
