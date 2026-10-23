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

（尚無）
