# ECPF 資料流 × 模型池生命週期 — 互動流程圖

一個**獨立、可離線開啟**的互動式流程圖，說明 ECPF（Evolving Concept-Pool
Framework）從冷啟動、逐筆推論、訊號抽取、漂移偵測、警告緩衝、`on_drift`
（含模型池維護）到 in-control 對決（stage④）的完整資料流與模型池活體維護。

選一個真實漂移事件，畫面上所有「事件層有資料」的節點會即時亮出該事件的數值
（KPI、node 3/4/5、6h/6j 快照、stage④ 對決、離線分析、③→④ 散點）。

## 開啟方式

因為 `index.html` 透過 `<script src="ecpf_data.js">` 載入資料，直接用
`file://` 開啟在部分瀏覽器可能被 CORS 擋下。建議用本機伺服器：

```bash
cd docs/ecpf_lifecycle
python -m http.server 8777
# 開 http://127.0.0.1:8777/index.html
```

## 檔案

| 路徑 | 說明 |
| --- | --- |
| `index.html` | 完整實作。內含 x-dc 樣板、`dc-runtime`（取代 Claude Design 的 `support.js`）、以及**原封不動移植**自設計稿的邏輯類別 `Component`。 |
| `ecpf_data.js` | 資料層 `window.__ECPF_DATA`（798 事件 · 3 configs · 含 stage④ 對決 7 欄）。 |
| `source/event_interactions.csv` | 正規資料來源（29 欄 · 798 列）。 |
| `source/generate_ecpf_data.py` | 由上面 CSV 重新產生 `ecpf_data.js`。 |
| `source/ECPF_資料流與模型池生命週期.dc.html` | 原始 Claude Design 稿（provenance）。 |

## 由來 / 實作說明

本頁**實作**自 Claude Design 專案
`Copy of ECPF資料流與模型池生命週期`
（`ECPF 資料流與模型池生命週期.dc.html`）。原稿是 Claude Design 的 `x-dc`
樣板，只能在 Claude 的設計執行環境（`support.js`）內渲染。實作做了兩件事：

1. **`dc-runtime`（`index.html` 內）** — 一個精簡、獨立的 `x-dc` 執行環境，
   支援原稿用到的全部語法：`{{ dotted.path }}` 內插（文字與屬性值）、
   `<sc-if>`、`<sc-for as=…>`、`onClick/onChange/value` 綁定、SVG 子樹，
   以及與原稿 `DCLogic` 一致的 `state / setState / mount` 生命週期。
   樣板標記與邏輯類別皆逐字保留，僅替換底層執行環境。

2. **完整資料** — 設計專案內附的 `ecpf_data.js` 因 Design API 的 256 KiB
   讀取上限被截斷（只剩 348 筆、且缺第三個 config `uq_vote_seqdrift2`）。
   本頁改由未截斷的 `event_interactions.csv`（29 欄）重新產生完整 798 事件。
   重生資料與原稿寫死的統計完全吻合：TP 164、★ 46、TP 收盤 leader
   fresh 101 / reused 63、reuse 較準 118 / 新模型較準 46。

### 重新產生資料

```bash
cd docs/ecpf_lifecycle/source
python generate_ecpf_data.py
```

`ecpf_data.js` 的每筆 = CSV 一列，另加三個衍生欄位：`idx`（列序）、
`fileShort`（`file` 去掉 `.csv`）、`isStar`（`gt_match=="TP"` 且
`reuse_looked_better==0`）。

## 圖例

- 🟢 **實線** — 真資料流 / 真池狀態變更（output 真的餵給下一步或真的改寫池）
- 🟡 **虛線分叉** — 診斷值 → logging（observer-only，不回饋 runtime 決策）
- ⚪ **獨立區塊** — 離線事後分析（無回饋箭頭）
- ⚙ **池維護** — 每漂移／每步改變模型池的機制節點（CSV 多半無欄位）
