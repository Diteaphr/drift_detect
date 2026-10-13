# MagSeed 可確認外形，但缺公式與狀態機；A5 暫不能忠實實作

**結論：** 截至 2026-10-12，公開可讀的一手資料只有 [Chen、Koh、Riddle（2015）的出版社摘要](https://link.springer.com/chapter/10.1007/978-3-319-26350-2_9)；[ECPF 論文](https://arxiv.org/pdf/1905.08848)提供對 MagSeed 的**間接描述**、四個實驗參數與結果，但沒有足以重建 detector 的公式和狀態更新順序。[ECPF 作者公開的 CPF 程式庫](https://github.com/rand079/CPF)也沒有 MagSeed 類別。這些證據可界定 A5 的研究問題，**不能**把雙 ADWIN、SEED 近似版或自行設計的 warning 閘門標成「原文 MagSeed」。本報告只做來源查核；依已核准[預註冊](../../docs/ECPF_DET1_預註冊.html)的停點，A5 與正式實驗仍等可讀原文或可核驗的原作者實作。

## 用三層證據界定目前能下的結論

| 層級 | 已查來源 | 可核實內容 | 界限 |
|---|---|---|---|
| 原作者的一手摘要 | [Springer 章節頁，DOI 10.1007/978-3-319-26350-2_9](https://link.springer.com/chapter/10.1007/978-3-319-26350-2_9) | 作者、2015 年、頁 96–108；MagSeed 旨在追蹤 drift severity；摘要稱以合成與真實資料比較 ADWIN2、DDM。 | 頁面明示「subscription content」；摘要沒有偵測公式、演算法步驟或程式碼。摘要的「高 TP／低 FP」是作者主張，不能當成 DET1 已驗證結果。 |
| 引用者的間接描述與實驗 | [Anderson 等，ECPF 論文 §2.2、§4.0.1、Table 4](https://arxiv.org/pdf/1905.08848) | 描述 MagSeed 為 SEED 的後續延伸，使用兩種 warning 條件，warning 先於 drift；在 ECPF 實驗中設 `δ=0.05`、`ε=0.01`、`α=0.8`、`δw=0.1`，並公開 synthetic 結果。 | 對 MagSeed 而言屬轉述與使用紀錄，不是 Chen 等人的演算法規格；參數**名稱與值**可知，各參數在公式中的精確作用未知。 |
| 引用者的公開程式 | [rand079/CPF](https://github.com/rand079/CPF)，查核提交 `8142b0c9b789e4452f0e9044ab4dfbb51b8d3327` | 提交樹只有 `meta/AbstractCPF.java`、`meta/CPF.java`、`meta/ECPF.java`、`drift/DriftDetectionMethodClassifierExt.java` 等七個檔案；`ECPF.java` 使用 MOA 通用 `ChangeDetector` 選項。 | 此提交沒有 MagSeed 類別或可用來回推其內部邏輯的 detector 原始碼。結論只限這個已查提交，不能聲稱全網不存在其他實作。 |

網路以精確題名、作者組合、`MagSeed` 加 `code`／`GitHub`／`algorithm` 搜尋；可見的 [ResearchGate 書目頁](https://www.researchgate.net/publication/315528399_Tracking_Drift_Severity_in_Data_Streams)標示全文不可用、須向作者索取。搜尋未找到可驗證為原文的開放 PDF 或原作者程式；這是**本次查核範圍的陰性結果**，不是不存在的證明。

## 從 ECPF 轉述可鎖定比較方向，卻不能推回完整 MagSeed

| 問題 | 目前可取得的間接資料 | 對 DET1 的含義 |
|---|---|---|
| 監看的訊號 | ECPF §2.2 說 MagSeed 比較串流中相鄰視窗的底層平均錯誤率，而非 DDM 那種自上次 drift 起的累積平均；ADWIN 的輸入通常是分類器錯誤。 | A5 應以 0/1 分類誤差作候選輸入；但原文如何定義兩窗、何時更新、是否另用 severity 統計，仍未證實。 |
| 兩個 warning 條件 | ECPF §2.2 描述為較寬鬆的 Hoeffding bound 與視窗間平均錯誤率變化；drift 前需觸發 warning flags。 | 可以確定 A5 不宜簡化成「單一 ADWIN 警報就是 drift」。但 `flags` 是兩者同時、先後、保持多久、清除條件為何，轉述沒有形式化。 |
| drift 與參數 | ECPF §4.0.1 稱它是加上 warning bound 的 ADWIN 版本，使用 `δ=0.05`、`ε=0.01`、`α=0.8`、`δw=0.1`。 | 四個數值可預先鎖定；不能只依名稱猜 `ε`、`α` 乘在哪個閾值，也不能把 `δw=0.1` 當成第二個獨立 ADWIN 就宣稱同演算法。 |
| ECPF 使用結果 | ECPF Table 4 每個 synthetic stream 有 400 個真 drift。使用 MagSeed 時，ECPF 的報告警報均數依次為 Agrawal 930、CIRCLES 689、LED 993、RandomRBF 838、STAGGER 1,052；作者亦討論部分配置警報偏多。 | 這是外部**量級參考**，可用來發現極端偏離；警報數大於 400 不等於可直接算出 FP，因為需要逐筆 GT 配對規則。資料生成、模型回饋及框架也須匹配才可嚴格對照。 |

以上 MagSeed 特性均是 [ECPF 論文](https://arxiv.org/pdf/1905.08848)對先前工作的描述；Table 4 則是 ECPF 作者自己的實驗結果。它們的證據角色不同，不能合併成「原作者提供的 pseudocode」。

## 六個缺口會直接改變警報、warning 與重置結果

| 待核對細節 | 現有材料缺什麼 | 猜錯後的實質影響 | 優先級 |
|---|---|---|---|
| 1. 視窗與切點 | SEED／MagSeed 的視窗維護、候選切點、最小樣本量、壓縮與更新時序。 | 改變每一步使用的樣本、計算量及 drift 時點。 | 阻斷 |
| 2. 兩個 warning 的精確不等式 | Hoeffding bound 的形式、均值差的定義、方向性與 `ε`、`α`、`δw` 的作用。 | 直接改變 warning 誤報、進區時點；無法與雙 ADWIN 做有效機制消融。 | 阻斷 |
| 3. warning 到 drift 的狀態機 | 兩條件是 AND／OR、同步或序列觸發；如何保持、撤銷 warning；正式 drift 判定是否須再過原 SEED／ADWIN 檢驗。 | 改變 A5 的 warning buffer、凍結區段、FP 與超額命中 X。 | 阻斷 |
| 4. severity 與 volatility 的用途 | severity 的計算、是否回饋偵測門檻；SEED 的 drift-frequency／volatility 權重是否在 MagSeed 沿用。 | 若省略核心修正，實作可能只剩「ADWIN 加 warning」，已不是原文 MagSeed。 | 阻斷 |
| 5. drift 後 reset 與輸出語意 | 截窗或重建、保留哪些統計、同筆能否同時 warning/drift、下一筆如何開始。 | 連續 drift 的警報數與時間偏移會變，且影響 DET1 接線。 | 阻斷 |
| 6. 可比性與驗證 | 原作者實作、數值例、測試序列或完整偽碼；ECPF 當年使用的 MagSeed 版本與輸入／reset 包裝。 | 目前無法建立如 RDDM 對 MOA 的逐事件忠實度檢查；ECPF Table 4 只能提供弱外部參考。 | 阻斷 |

**推論邊界：** 以上「缺什麼」指已查來源**未提供足以定案的細節**，不主張原文一定沒有寫。`SEEDDetector` 或現有雙 ADWIN 的行為也不能代填，因為同樣參數可對應多種不等式、視窗管理與 reset 實作。

## 取得原文或原作者程式後，先關閉六個缺口再接 A5

1. 透過學校機構訂閱開啟 [Springer 原文章節](https://link.springer.com/chapter/10.1007/978-3-319-26350-2_9)，或以 [ResearchGate 的 Request full-text](https://www.researchgate.net/publication/315528399_Tracking_Drift_Severity_in_Data_Streams)向作者索取。取得合法可讀的 PDF、作者預印本，或明確來源的原作者程式均可啟動下一輪核對。
2. 逐項記錄上表六個細節的**原文頁碼／公式／圖號或原碼行號**，再定義 `warning`、`drift`、`reset` 的逐筆語意，特別核對四參數及錯誤輸入方向。
3. 先跑預註冊的人造 0/1 序列、警報方向、未啟用 zone 的二元基線閘門；有可執行參考實作時再做逐事件對照。完成後才可將 A5 標為「原文 MagSeed」，並進入後續正式實驗。

**目前決策：** RDDM 已依[階段三狀態報告](stage3_rddm_status.html)完成；MagSeed 的 A5、`det_magseed` 與正式 8,868 次規模執行保持暫停。本報告沒有改動預註冊、演算法或任何實驗結果。
