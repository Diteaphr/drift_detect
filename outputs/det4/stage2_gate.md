# DET4 階段二：merge 與混搭對角逐位元閘門

**結論：通過。** 固定 seed `20261012` 的 15 條串流，五個既有對角各跑 legacy／mixed 兩種模式，共 `150/150`；逐位元相同 `150/150`。

| 閘門 | 預期 | 逐位元相同 | 結論 |
|---|---:|---:|---|
| 合併 main 後、DET4 欄位關閉 | 75 | 75 | 通過 |
| DET4 欄位開啟、warning=confirm 對角 | 75 | 75 | 通過 |

執行 commit `739a0984f65b865ec776d73ef84569fccf2fa0c0`；牆上時間 `17.3` 分鐘。核對欄位為 `y_true`、`y_pred`、`alarm_idx`，以及適用的 `alarm_idx_input`（否則 `alarm_ts`）。單元測試另驗證獨立更新、zone exit 清 buffer、confirm reset、timeout 與 guard。
