# DET4 階段三：18 組 × 22 資料集 smoke

**結論：通過。** 完成 `432/432` runs，涵蓋 `18/18` presets 與 `22/22` 非迴歸資料集；runner error rows `0`。

| 核對 | 結果 |
|---|---|
| 每組固定 injected 2、synthetic 2、INSECTS abrupt 1，其餘資料集各 1 | 通過 |
| manifest、metrics、preds、warning events | 通過 |
| 成本欄位皆有值 | 通過 |
| warning 開啟 = close + censored | 通過 |
| S1 凍結步數 = 0 | 通過 |

Warning 結束原因：`confirmed`=811, `reference_switch`=34, `stream_end`=31, `timeout`=7, `zone_exit`=4627.
牆上時間 `35.6` 分鐘；所有 smoke 均標示 non-comparable。
