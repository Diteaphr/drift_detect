# 階段五 smoke 完成；正式矩陣仍待停點審閱

**結論。** 2026-10-13 的 DET1 階段五已完成 **1,240 次**預註冊 smoke，另完成 **1 次** MagSeed 偽碼 Y 解讀的 dev 敏感度檢查。逐筆完整性稽核錯誤為 **0**；A5（學位論文雙向解讀 X）與 A5u（單側變體）均完成短跑。沒有依 smoke 的結果改動 detector 參數或 P1/P2 判準。依原始 DET1 任務的階段五 **【停】** 要求，正式 report 資料尚未執行，須先審閱本報告。

## 1,240 次短跑皆可追溯；GT 缺席的前綴不作偵測判讀

| 資料組 | 預設 × 串流 | 完成 | 前綴中無 GT 的 run | 原始警報為 0 的 run | 最多原始警報／run | runtime 合計（CPU 秒） |
|---|---:|---:|---:|---:|---:|---:|
| injected_paper_electricity，3 trials／cell | 22 × 24 | 528 | 0 | 148 | 24 | 5,121.13 |
| INSECTS abrupt，前 5,000 筆 | 17 × 1 | 17 | 17 | 15 | 2 | 46.22 |
| INSECTS incremental，前 5,000 筆 | 15 × 1 | 15 | 15，原 GT 檔為空 | 4 | 1 | 46.37 |
| synthetic_multiclass，前 5,000 筆 | 17 × 40 | 680 | 272 | 309 | 3 | 777.28 |
| **合計** |  | **1,240** |  |  |  | **5,991.00** |

22 個 injected 預設是 17 個 ECPF（含 A6 與 A5u 兩個 lw）加 5 個 detector-only。INSECTS incremental 依預註冊略過 A0 兩個 lw，且只報準確率、警報數與 runtime；**不計 TP/FP**。`injected --trials 3` 的 manifest 雖標 `smoke=false`，但輸出隔離在 `outputs/det1/smoke_full_20261013_v2/`，不得混入正式分析。原始警報欄含 injected 偵測起點以前的警報；正式評分會依 manifest 的 `detect_from` 過濾。

INSECTS abrupt 的 drift 起點不在 5,000 步前綴，17 次短跑無法測試該組命中率。Synthetic 有 272 次短跑的 GT 不在前綴，因此零警報不能直接解讀為失靈；另有 82 次零警報且前綴含 GT，正式全長資料才可判定其影響。Injected 的 148 次零警報前綴均含 GT，屬應保留的觀察，不據以調參。

稽核逐筆檢查 `manifest.json`、`preds.npz`、`metrics.json`，ECPF 另檢查 `warning_events.json`；交叉核對預測筆數、依 `detect_from` 過濾後的警報數、原始輸入座標、資料來源 SHA-256／生成來源 SHA-256、Git commit `644dcf1` 且工作樹乾淨、River `0.21.2`。**1,241 筆全通過，錯誤 0**。後一筆為下節 Y 解讀 dev，不列入 1,240 次矩陣。可稽核摘要見 [JSON](stage5_smoke_audit.json)；原始 run 位於本機隔離 smoke 目錄，未提交至 Git。

## A5 的密集 warning 與單串流警報尖峰需在正式分析照報

ECPF 16 個新預設與 A6 合計記錄 **33,925** 次 warning 開啟；其中 **1,103** 次確認 drift、**32,710** 次因 detector 離開 warning 區而關閉、**56** 次 timeout、**56** 次串流結尾 censored。開啟數等於關閉或截尾數，沒有未結算的 warning。A5 雙向 `lw0/lw1` 分別有 5,871／7,642 次開啟，A5u 單側分別有 5,860／7,668 次；絕大多數是 `zone_exit`，顯示頻繁進出 warning 區，並非 buffer 永久卡住。

最大的警報尖峰是 injected `electricity_label_swap_gradual_g00` 的 A5 `lw0`：**24 次原始警報**，其中 20 次位於 GT 結束後；其 GT 為原始輸入座標 **[35,988, 38,488]**。同一串流 A1 `lw0` 有 3 次原始警報，A5 `lw1` 2 次，A5u `lw0/lw1` 為 3／1 次。A5 `lw0` 有 330 次 warning 開啟、306 次 `zone_exit`、24 次確認；事件數守恆。這是 smoke 的可定位異常，不改變雙向 A5 的原文導向設定。正式 P1/P2 必須保留該串流及其他不利資料格，並分列原始警報、Cerqueira TP/FP、episode hit 與扣除機會值後的 X。

## Y 解讀只做一次 dev；目前無法辨別兩種解讀

依 [預註冊修訂](../../docs/ECPF_DET1_預註冊.md)，只在 `synthetic_multiclass/gradual_rbf4_100k_g00` 前 5,000 筆執行一次 `magseed_literal_dev`，並與同串流 A5 主解讀 X 配對。兩者 `y_true` 相同；X／Y 均 0 次警報、0 次 warning、prequential accuracy 均為 **0.5776**。此一次檢查**沒有提供區分 X／Y 的事件**，不能推論兩種解讀等價；Y 不參與正式 P1/P2，也不追加第二次 dev。A5 對外名稱 `magseed` 的意義限於「依 Chen 2016 學位論文實作，偽碼矛盾處採 X 解讀」，不是宣稱取得 Chen、Koh、Riddle 2015 會議原文或作者程式。文獻來源：[Chen 學位論文](https://hdl.handle.net/2292/28911)。

## 以 smoke 換算正式約 9,752 次；先維持 4 workers

正式矩陣為原定 **8,868 次**加 A5u **884 次**，共 **9,752 次**：injected 8,800、INSECTS abrupt 17、INSECTS incremental 15、synthetic HT 680、synthetic hf10 240。Y 的一次 dev 不納入。依 smoke runtime 線性換算，前四組共約 **101,900 CPU 秒（28.3 CPU 小時）**：injected 以 3→50 trials 乘 50/3，兩個 INSECTS 以全長 52,848／57,018 筆除以 5,000，synthetic HT 以 100,000／5,000。4 workers 的理想下限約 **7.1 小時**，不含資料載入、輸出與 hf10。此次實測每 worker 峰值 RSS 最高 **444.7 MB**；正式先沿用 smoke 成功的 4 workers，並用 `--resume` 保護中斷進度。

**hf10 未短跑，時間估計不具實測基礎。** 階段一曾粗估 hf10 另需 20–60 CPU 小時；若沿用該規劃區間，總量約 48–88 CPU 小時，4 workers 理想約 **12–22 小時**。考慮長串流非線性成本與 I/O，先預留 **15–30 小時**作執行排程，並在正式首批完成後依實測更新；此為容量規劃，非完成時間承諾。來源：[階段一資源估計](stage1_readiness.md)、本次[逐筆稽核](stage5_smoke_audit.json)。

## 階段六前保留原有判準與續跑閘門

`--resume` 已在 injected ECPF 主批對兩個 A5u 預設各驗證 **24 筆已完成、0 筆待跑**；單元測試亦覆蓋 commit／資料 hash 不符時拒絕誤跳過。Smoke 初次執行曾遇到 A0 的 5,000 步前綴無 GT 與摘要欄位型別問題；修復後以 commit `644dcf1` 重新完成受影響 smoke，早期失敗輸出保留在不同目錄，本報告只採上述完整批次。現有定向測試 **98 passed**；RDDM／MOA 對照與 A5 行為閘門已在階段三報告／後續修訂驗證。上述修復不變更預註冊判準或 detector 參數。

正式開始前需維持階段五的 **【停】**：審閱密集 warning／警報尖峰與時間估計後，才可執行階段六 report 資料。正式結果的 P1/P2、A1t 次要判定、10,000 次 bootstrap CI 及三組方向一致性，均不從 smoke 推導。
