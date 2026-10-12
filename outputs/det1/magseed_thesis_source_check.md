# 找到 MAGSEED 一手演算法；新候選版可執行，但 A5 仍不能結案

**結論：** [Kylie Chen（2016）奧克蘭大學學位論文](https://hdl.handle.net/2292/28911)第 3 章（印刷頁 36–40；PDF 頁 51–55）包含 MAGSEED 的公式、文字狀態說明與 Algorithm 1。這推翻先前「目前只有間接描述」的來源狀態；[先前的證據盤點](magseed_evidence_audit.html)保留作當時查核紀錄，以本報告更新。根據論文與 [MOA 的 SEED 原始碼](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/SEEDChangeDetector.java)，已加入獨立的 `magseed_thesis_candidate`。它仍有原文歧義和 ECPF 參數缺口，且下降錯誤率會觸發 drift，**不列為預註冊 A5，也不啟動正式 P1/P2 比較**。

## 用作者學位論文修正先前候選版的核心假設

| 議題 | 論文與原始碼可確認的行為 | 對本專案的影響 |
|---|---|---|
| 演算法來源 | 學位論文前言明示第 3 章部分內容已發表為 Chen、Koh、Riddle（2015）會議文。這是同一第一作者的一手詳細版本，但不能保證與會議版逐字或逐版一致。[學位論文](https://hdl.handle.net/2292/28911) PDF 頁 8、第 3 章。 | 可據以做來源註明的試作；尚不能宣稱核對了 2015 會議 PDF 或其實驗程式。 |
| Drift | 把 0/1 分類誤差分塊，在所有可用區塊邊界比較左右平均值的**絕對差**。超過變異數感知的 Hoeffding–Bonferroni 界後，丟掉切點左側區塊。[論文](https://hdl.handle.net/2292/28911) PDF 頁 52，式 (3.1)–(3.2)。 | 先前固定兩個相鄰視窗、只偵測錯誤率上升的試作不是 MAGSEED 原文邏輯。下降也可能報 drift。 |
| Warning | 第一條用相同切點、較寬的 `δw` 界；第二條用 100 筆滑動錯誤率的 `p+s > pmin+cw·smin`。正文寫**任一條**成立便進 warning。[論文](https://hdl.handle.net/2292/28911) PDF 頁 53，式 (3.3)–(3.4)。 | 先前候選版把兩條條件相與，已被原文否定。Warning 解除則回到 no change，恢復壓縮。 |
| `ε=0.01`、`α=0.8` | `ε̂` 是壓縮相鄰同質區塊的基值，`α` 是線性增長項。MOA SEED 由新往舊掃描，容許差依區塊相對位置逐步增加。[論文](https://hdl.handle.net/2292/28911) PDF 頁 52；[SEED 程式](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/SEEDChangeDetector.java)。 | 兩者不是 warning 界的縮放率或均值差下限。舊候選版的參數語意不成立。 |
| Severity | 有 warning 後到 drift 期間的誤分類比例；沒有 warning 的 drift 可存在。[論文](https://hdl.handle.net/2292/28911) PDF 頁 53，式 (3.5)；PDF 頁 61，Table 3.9 與正文。 | 不得把「先 warning 才能 drift」寫成原文的硬條件；偵測到 drift 時以既有 warning buffer 計算 `Rate`，無 warning 則記錄缺值。 |

## 保留三個影響忠實重現的未決點

1. **偽碼覆蓋矛盾。** Algorithm 1 第 27 行寫 `warningFound=false` 時直接把狀態設成 no change，會覆蓋第 18 行已設的 drift，也可能覆蓋第 12 行的第二種 warning；這與相鄰正文及 Table 3.9 的「部分 drift 沒有 warning」相矛盾。[論文](https://hdl.handle.net/2292/28911) PDF 頁 53–55、61。試作採 **drift 優先，其次任一 warning，最後 no change**，並明確標示為解讀，不宣稱原作者程式行為。
2. **參數仍不完整。** [ECPF 論文](https://arxiv.org/pdf/1905.08848)只列 `δd=0.05`、`ε̂=0.01`、`α=0.8`、`δw=0.1`。Chen 論文 Table 3.3 另列壓縮間隔 `τ∈{50,75,100}`、`cw∈{1,2}`，沒有給 ECPF 當年所用的 `τ`、`cw` 或區塊大小。試作採 [MOA SEED 預設](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/SEEDChangeDetector.java)的 `block_size=32`、`τ=75`，`cw=2` 則是 Chen 研究過的值，**不是已知的 ECPF 設定**。正式 A5 不能把這些缺值當作既定事實。
3. **100 筆統計的初始化與 `s` 定義。** 論文稱 100-instance sliding window 的平均與標準差，未明示不足 100 筆時的處理及 `s` 是否為 Bernoulli 樣本標準差或錯誤率的標準誤。試作待滿 100 筆才更新基線，取 `sqrt(p(1-p))`。兩種解讀可能改變 warning 時間，需原作者程式或數值例比對。

## 新候選版通過基本行為檢查，但下降 drift 與預註冊閘門衝突

程式：[來源註解與實作](../../detectors/core/magseed_thesis_candidate.py)、[行為測試](../../tests/test_magseed_thesis_candidate.py)。公開入口為 `make_detector("magseed_thesis_candidate", {})` 與 `ECPFZoneDetector("magseed_thesis_candidate")`；`magseed` 仍拒絕建立。舊 `magseed_candidate` 留作先前探索版，不以新資料追認其忠實度。PDF 僅存研究過程的暫存路徑，未收入 repo 或對外重製。

| 固定 0/1 序列，4,000 筆 | 首次 warning | 首次 drift | 判讀 |
|---|---:|---:|---|
| 前 2,000 筆每 10 筆 1 錯、後 2,000 筆每 2 筆 1 錯 | 2,035 | 2,053 | 先 warning 後 drift，符合上升序列行為閘門。 |
| 前 2,000 筆每 2 筆 1 錯、後 2,000 筆每 10 筆 1 錯 | 2,076 | 2,079 | 也觸發 drift，符合式 (3.1) 絕對差，但**不符合預註冊「0.5→0.1 不 drift」閘門**。 |
| 全為 0 | 無 | 無 | 無虛構警報。 |

以上序列只做行為檢查，沒有對原作者 MAGSEED 的逐事件輸出比對，也沒有用 GT 計算 P1/P2。目標測試 9 項通過；主專案測試（排除既有無法收集的 `tests/test_detection_evaluation.py`）為 **91 passed**。完整 8,868 次正式執行仍未開始。若要把下降 drift 篩除，須先確認「原文雙向偵測」與 DET1「只把錯誤率上升列為 drift」的衝突如何處理，不能在得知測試結果後默默修改 A5 定義。

**階段三狀態：** RDDM 的 MOA 對照已完成；MAGSEED 有一手論文與可執行試作，但未通過原文／預註冊一致性門檻。下一步是取得 2015 會議版或原作者實作，核對 `cw`、`τ`、warning 標準差與狀態優先序，再決定 A5 是否可按既定判準執行。
