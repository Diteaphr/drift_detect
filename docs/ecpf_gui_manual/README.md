# ECPF GUI 操作手冊 · 監控台（互動）

一個**獨立、可離線開啟**的互動式操作手冊，模擬「假想中的 ECPF 使用者 GUI」，
用一個 8 步驟監控台逐步說明：從輸入資料、即時推論、漂移訊號、警告緩衝、
`on_drift` 確認、模型池活體維護、in-control 對決（stage④），到離線事件報告 —
每一步 GUI 會呈現給使用者什麼數據與視覺化。數值取自真實 CSV（798 事件）。

**兩個檢視頁（頂端切換）：**

- **📖 逐步操作手冊** — 原設計稿：左側步驟導覽、中間監控台視覺化、右側說明；
  每一步下方附「本頁相關」的可調參數面板。
- **⚙ 全部可調參數** — *新增*：把原本散落在步驟 1 / 2 / 3 / 6 / 7 的 10 個可調
  超參數**集中在同一頁**，分組、附滑桿／開關、目前值、預設值、效果說明與設定摘要。
  兩頁共用同一組 `settings`，任一邊調整都會即時同步。

## 開啟方式

```bash
cd docs/ecpf_gui_manual
python -m http.server 8779
# 開 http://127.0.0.1:8779/index.html
```

（直接 `file://` 開啟可能被 CORS 擋下 `ecpf_data.js`，建議用本機伺服器。）

## 集中的可調參數

| 參數 | 原步驟 | 預設 | 說明 |
| --- | --- | --- | --- |
| `warm_start` | ① | 200 | 開頭先 fit、不判漂移的筆數（runner 旗標 `--warm-start`） |
| `n_trees` | ② | 10 | Hoeffding 森林棵數（分析建議 5：更準、更快） |
| `detector_delta` / `_w` | ③ | 依偵測器 | 漂移／警告門檻；尺度隨 ADWIN vs SeqDrift2 而變 |
| `ecpf_max_pool_size` | ⑥ | 10 | 模型池上限 |
| `ecpf_similarity_margin` | ⑥ | 0.95 | 一致度 ≥ m 即合併 |
| `ecpf_fade_points` | ⑥ | 15 | leader 每漂移 +f、其餘 −1、≤0 淘汰 |
| `ecpf_fade_enabled` | ⑥ | True | 是否啟用淡出 |
| `ecpf_model_check_freq` | ⑦ | 1 | 每幾步檢查一次對決換將 |
| `_lock_out_duration` | ⑦ | 100 | 鎖定期長度（硬寫常數，非 config；此處僅介面示範） |

> `detector_delta` 的尺度依「尺度參考事件」的偵測器家族而定：ADWIN 事件顯示 ~0.02–0.05，
> SeqDrift2 事件顯示 ~0.55。用工具列的 ‹ › 切換事件即可看到另一家族的尺度。

**注意：** 滑桿／開關僅示範介面控制，**不重算**手冊中顯示的事件數值（那些是既有執行
結果）。實際生效需以對應參數重跑實驗。

## 檔案

| 路徑 | 說明 |
| --- | --- |
| `index.html` | 完整實作：x-dc `dc-runtime`（取代 support.js）＋逐字移植的 `Component`（8 步監控台）＋ `App` 擴充（集中參數頁）。 |
| `ecpf_data.js` | 資料層 `window.__ECPF_DATA`（798 事件），與 [../ecpf_lifecycle](../ecpf_lifecycle) 同一份。 |
| `source/ECPF_GUI_操作手冊.dc.html` | 原始 Claude Design 稿（provenance）。 |

## 由來 / 實作說明

實作自 Claude Design 專案 `ECPF GUI 操作手冊.dc.html`。作法與 [../ecpf_lifecycle](../ecpf_lifecycle)
相同：`index.html` 內含精簡 `dc-runtime` 重現原稿用到的 `x-dc` 語法
（`{{path}}` 內插、`sc-if`、`sc-for as=`、`onClick/onChange/onInput/value` 綁定、SVG、
`DCLogic` 生命週期），並逐字保留原稿的 `Component` 邏輯類別。

集中參數頁由 `App extends Component` 擴充：重用原稿自己的 `_buildParams` /
`_paramMeta` / `_deltaSpec` 與共用的 `this.state.settings`，把所有步驟的參數收攏到
單一頁的分組網格，因此與逐步手冊的每頁面板完全同步。

滑桿在放開（`change`）時提交、拖曳中（`input`）即時更新讀數 —
如此全頁重繪不會打斷原生拖曳。
