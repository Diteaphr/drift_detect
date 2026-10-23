# A5 按 Chen 2016 的雙向定義通過新閘門；A5u 保持次要變體

**結論：** 2026-10-13 的[預註冊修訂](../../docs/ECPF_DET1_預註冊.html)已先於本輪任何資料執行提交（`43dead2`）。A5 現以 `magseed` 公開，按 [Chen（2016）學位論文第 3 章](https://hdl.handle.net/2292/28911)式 (3.1) 的絕對差偵測雙向變化，偽碼衝突採修訂中的 **X 解讀：drift > 任一 warning > no change**。A5u 以 `magseed_upward` 公開，僅正向切點可觸發，明確是偏離原文的次要變體。2015 會議 PDF 與原作者 MAGSEED 程式仍未取得；名稱表示**依 2016 學位論文實作**，不表示逐事件重現原作者程式。

## 固定序列顯示 A5 雙向觸發，A5u 只保留正向

每條 4,000 筆固定 0/1 error：前後各 2,000 筆，0.1 以每 10 筆 1 錯表示，0.5 以每 2 筆 1 錯表示。索引從 0 起算。切點欄為首次 drift 時視窗的區塊序號／左側筆數／右側筆數／右減左錯誤率。

| 序列 | Detector | 首次 warning | 首次 drift | 首次 drift 切點 |
|---|---|---:|---:|---|
| 0.1→0.5 | A5 `magseed` | 2035 | 2053 | 62／1984／70／+0.29970 |
| 0.5→0.1 | A5 `magseed` | 2076 | 2079 | 62／1984／96／−0.33333 |
| 0.1→0.5 | A5u `magseed_upward` | 2035 | 2053 | 62／1984／70／+0.29970 |
| 0.5→0.1 | A5u `magseed_upward` | 無 | 無 | 無 |

**判定：** A5 上升時先 warning 後 drift；下降時依絕對差仍可 drift，符合新閘門。A5u 的下降無 drift，符合單側變體定義。這是預設參數的人造序列行為檢查，不是 report 資料的 P1/P2 結果。[實作](../../detectors/core/magseed_thesis_candidate.py)保留 `last_cut` 的左／右筆數與有號均值差，供重現方向與切點。

## 既有路徑與來源限制均有可核對的證據

- `make_detector("magseed", {})` 與 `ECPFZoneDetector("magseed")` 都使用相同的 A5 類別；`magseed_upward` 是獨立 A5u 類別，Y 解讀以 `magseed_literal_dev` 隔離。[入口](../../scripts/run_benchmark.py)、[zone](../../src/ecpf_detector.py)。
- 新入口不改既有基線：electricity／`ecpf_paper` 全 45,312 筆重跑，`y_pred`、80 個 `alarm_idx` 與 80 個 `alarm_ts` 對既有 `preds.npz` 逐陣列一致。比對在 `river==0.21.2` 的主環境執行。
- 主專案測試排除已知在本分支事前就無法收集的 `tests/test_detection_evaluation.py`，結果 **93 passed**；新增測試核對雙向有號切點、A5u 下降無 drift、Y 解讀可覆蓋 drift。[測試](../../tests/test_magseed_thesis_candidate.py)。
- `b=32`、壓縮間隔 75 來自 [MOA SEED 預設](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/SEEDChangeDetector.java)；`cw=2` 與 100 筆標準差方式依預註冊修訂固定，仍屬原文未完全交代的選擇。X／Y dev 敏感度執行安排於階段五，**不影響 A5 入主判定的方向閘門**。

**下一步：** 進入階段四生成 preset 和差異表；階段五對每個適用資料短跑，另執行一次 Y 解讀 dev 敏感度檢查。正式 P1/P2 必須再通過 smoke、manifest 來源與續跑閘門。
