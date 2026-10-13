# RDDM 通過 MOA 對照；階段三等待 MagSeed 原文全文

**結論：** RDDM 的 MOA 預設參數移植、兩個人造誤差閘門、既有二元 ECPF 基線逐位元閘門均通過。五條 0/1 序列共 98,500 步，RDDM 的 **28 次 drift 與 374 次 warning 進區**均與 CapyMOA 0.14.0 的 MOA RDDM 在**同一步**發生，雙向 ±32 步重合率皆為 **1.000**，高於預註冊的 0.90。MagSeed 仍缺 Chen、Koh、Riddle (2015) 原文 PDF，故階段三尚未完成，未開始後續正式實驗。

## RDDM 的來源語意已接入兩個入口

新檔 `detectors/core/rddm_moa.py` 依 [Waikato MOA 的 RDDM.java](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/RDDM.java) 移植，使用其預設值：`minNumInstances=129`、`warningLevel=1.773`、`driftLevel=2.258`、`maxSizeConcept=40000`、`minSizeStableConcept=7000`、`warnLimit=1400`。保留 warning 起點後的 ring buffer replay、超過 warning limit 的強制 drift，以及最大 concept 長度後的內部重啟；每筆只接受 0/1 分類誤差。授權文本置於 `detectors/core/LICENSE.rddm-moa.txt`。

`ECPFZoneDetector("rddm")` 與 benchmark `make_detector("rddm", {})` 均使用此實作。ECPF zone 在 drift 時保留同一個 RDDM 物件，讓下一筆輸入執行 MOA 的內部 replay；其他既有 zone 行為不變。驗證腳本為 `scripts/verify_moa_rddm.py`，完整逐序列結果見 [RDDM／MOA 一致性檢查](rddm_moa_check.html)。

## RDDM 通過三項共同閘門與 MOA 對照

| 閘門 | 結果 | 證據與範圍 |
|---|---|---|
| 0.1→0.5 錯誤率先 warning、後 drift | 通過 | 固定的 4,000 筆 0/1 序列，首次 warning 在索引 2,025、drift 在 2,041；`tests/test_rddm_moa.py`。 |
| 0.5→0.1 不觸發 drift | 通過 | 固定的 4,000 筆 0/1 序列，drift 為 0；同一測試檔。 |
| 新 zone 未啟用時，既有二元結果逐位元相同 | 通過 | electricity／`ecpf_paper` 全長 45,312 筆重新執行；與既有 `outputs/benchmark/electricity/ecpf_paper/electricity/preds.npz` 比較，`y_true`、`y_pred`、80 個 `alarm_idx` 與 80 個 `alarm_ts` 的 dtype、shape、原始 bytes 全相同。對照檔的 River 版本為 0.21.2；本輪使用 River 0.21.2、numpy 1.26.4、pandas 2.3.3。 |
| RDDM 對 MOA 雙向 ±32 步 drift 重合率 ≥0.90 | 通過 | 五條序列：Python→MOA 28/28、MOA→Python 28/28；warning 進區亦為 374/374；全部同一步。固定 seed `20261012`；見[完整結果](rddm_moa_check.html)。 |

在主專案與 `test_integration.py` 範圍，排除一個既有失敗檔後 **82 tests passed**；巢狀 `DriftTypeClassifier/tests` 另 **4 passed**。`tests/test_detection_evaluation.py` 在收集時匯入 `src.metrics` 未匯出的 `evaluate_detection_run` 等函式；對照本次改動前的 `HEAD`，該測試與匯出清單已存在此不一致。直接由 repo 根目錄執行未限範圍的 `pytest` 還會先載入巢狀專案同名的 `src` 套件，使主專案的 `src.config` 無法匯入；因此本輪分開執行兩個測試範圍，並如實保留上述既有失敗。這些失敗不作為 RDDM 通過所有既有測試的聲稱。

## MagSeed 的原文缺口阻止階段三結案

已檢查本 repo、`docs/refs/` 與目前附件，未見 Chen、Koh、Riddle (2015) *Tracking Drift Severity in Data Streams* 原文 PDF。網路查詢的[出版社頁](https://link.springer.com/chapter/10.1007/978-3-319-26350-2_9)僅提供摘要並標示訂閱內容；[ResearchGate 頁](https://www.researchgate.net/publication/315528399_Tracking_Drift_Severity_in_Data_Streams)亦標示全文不可用、需向作者索取。DOI `10.1007/978-3-319-26350-2_9` 僅能確認書目與摘要，無法核對 MagSeed 的演算法、warning 條件和狀態重置。

[ECPF 論文 §4.0.1](https://arxiv.org/pdf/1905.08848)雖指向其[作者程式庫 `rand079/CPF`](https://github.com/rand079/CPF)，但該庫在檢查時的提交 `8142b0c9` 只有 CPF/ECPF 框架 Java 類別、共用 drift wrapper、README 與授權檔；`ECPF.java` 使用 MOA 的通用 `ChangeDetector` 選項，庫內沒有 MagSeed 類別或其實作。因此可取得的是**引用 MagSeed 的 ECPF 程式碼**，不是 **MagSeed detector 的原始碼**；不能據此解除原文核對要求。這只界定已查的作者庫，不聲稱網路上絕無其他實作。

使用者亦確認目前未找到原文。依原任務的【停】規則，沒有用摘要、ECPF 的轉述或現有 `SEEDDetector` 近似版猜實作；`"magseed"` 尚未接線。

取得可讀的原文 PDF 後，下一步是逐節核對實作細節、補 MagSeed 與相同閘門，再完成階段三報告；目前不進入階段四。
