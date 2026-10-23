# MagSeed 候選版通過行為閘門；仍不能作為預註冊 A5

**結論：** 已加入可執行的 `magseed_candidate`，可用於探索 [ECPF 論文 §2.2、§4.0.1](https://arxiv.org/pdf/1905.08848)描述的「相鄰錯誤率視窗、兩個 warning 條件、warning 先於 drift」是否能在本 repo 的 ECPF zone 路徑運作。它**不是** Chen、Koh、Riddle（2015）原文 MagSeed；[原文章節](https://link.springer.com/chapter/10.1007/978-3-319-26350-2_9)目前只取得摘要，公式、視窗管理和重置順序未能核對。`magseed` 原名仍拒絕建立；本候選版不得列為已核准[預註冊](../../docs/ECPF_DET1_預註冊.html)的 A5、`det_magseed` 或正式 P1/P2 比較。

## 用明示的推定規則建立可測試候選版

程式位於 `detectors/core/magseed_candidate.py`，對 0/1 分類錯誤以固定長度 128 的兩個相鄰視窗維持均值，至少要求舊窗 32 筆。每筆更新為 O(1) 時間，因為兩窗計數與總和增量維護。令 `g = mean(recent) − mean(older)`，`H(q)=sqrt[ln(2/q)/2 × (1/n_old+1/n_new)]`：

| 步驟 | 本候選版的操作規則 | 原文證據狀態 |
|---|---|---|
| warning | `g > ε` 且 `g > α·H(δw)`；使用 `ε=.01`、`α=.8`、`δw=.1`。 | ECPF 只描述「較鬆 Hoeffding bound」與視窗均值變化，**未給出這組公式或 AND 邏輯**。 |
| drift | 前一筆已在 warning，且本筆 `g > H(δ)`，`δ=.05`；只偵測錯誤率上升。 | 先 warning 再 drift 符合 ECPF 的文字方向；精確閾值、方向及是否另有 SEED 檢驗**未經原文證實**。 |
| 結束 warning／reset | warning 條件失效即離區；drift 後清空兩窗。`mean_gap_proxy` 只作診斷，不稱為論文的 severity 指標。 | 清除與重置語意、severity 公式和 SEED volatility 權重**未知**。 |

四個數值取自 [ECPF 論文 §4.0.1](https://arxiv.org/pdf/1905.08848)，但 `α` 乘 warning bound、`ε` 作絕對均值差門檻、固定窗長 128 等都是**本次自行判斷**，不是文獻公式。這個候選版提供一種可反駁的操作化版本，不能由測試通過推論原文忠實度。

## 入口已接通；既有二元結果未改變

| 檢查 | 結果 | 範圍 |
|---|---|---|
| 0.1→0.5 人造錯誤率 | 通過 | 4,000 筆固定序列；首次 warning 在索引 2,037，首次 drift 在 2,055。 |
| 0.5→0.1 人造錯誤率 | 通過 | 同長度序列；0 次 warning、0 次 drift。 |
| ECPF zone 與 detector-only 入口 | 通過 | `ECPFZoneDetector("magseed_candidate")`、`make_detector("magseed_candidate", {})`；`"magseed"` 在兩入口均拒絕。 |
| ECPF 實際短跑 | 通過 | electricity 前 5,000 筆、`ecpf_paper` 固定底座加候選 zone：5,000 筆皆有預測，7 次警報；此數只表示流程可跑，不代表偵測品質。 |
| 未啟用候選版的二元基線 | 通過 | electricity 全長 45,312 筆、原 `ecpf_paper`；`y_true`、`y_pred`、80 個 `alarm_idx`、80 個 `alarm_ts` 之 dtype、shape、bytes 與既有輸出完全相同。 |
| 主專案測試 | 通過 | 排除先前已知匯入失敗的 `tests/test_detection_evaluation.py`，`pytest tests` 共 **86 passed**（含候選版新增 4 項測試）。 |

**判定：** 這是可執行、可檢查的探索原型，並未解除 A5 的來源閘門。下一步若取得可讀原文 PDF 或可核驗的原作者程式，先核對視窗、兩條 warning 不等式、SEED／severity／volatility、狀態機及 reset，再決定能否改成正式 `magseed`。在此之前不新增 A5 preset、不跑正式 P1/P2，也不將本候選版與 ECPF Table 4 當作同一演算法比較。
