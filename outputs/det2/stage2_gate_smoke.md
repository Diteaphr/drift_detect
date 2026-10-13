# DET2 階段二：lw0 可重用，四組新臂通過 smoke

**結論：** 固定 seed `20261012` 抽 15 條串流（injected 9、synthetic 5、INSECTS 1），三個 lw0 組別共 45 次與 DET1 的 `y_true`、`y_pred`、`alarm_idx`、`alarm_idx_input` 逐位元相同；故沿用 DET1 正式 lw0。四個新跑組別各 5 個 smoke，共 20 次，全部 manifest／preds／metrics 齊全。

| 驗證 | 結果 |
|---|---|
| lw0 重現 | 45／45 逐位元相同 |
| smoke | 20／20 完成；每組 injected 2、synthetic 2、INSECTS abrupt 1 |
| warning 事件 | 每 run 開啟 = 關閉 + 截尾 |
| lw1 凍結 | 三組共 15 run，逐 run 為 0 |
| 計分 | 有 GT 時 evaluator TP/FP/FN 與重算一致；截短後無 GT 時保留 null |

重現檢查使用 `outputs/det2/repro_selection.json` 的 15 條預先抽選清單。CLI `--cells` 的子字串規則使 synthetic 實際多跑 4 條串流 × 3 組＝12 次；額外檢查輸出留在隔離目錄、**不進 45 次重現判定或任何正式計分**。未改 DET1 原始輸出。Smoke 使用兩條 injected 完整串流、synthetic 首兩條及 INSECTS abrupt 前 5,000 步；截短後無 GT 的偵測欄位為 null，符合 evaluator 語意。

詳見 [固定抽樣](repro_selection.json)、[逐位元核對](repro_verification.json)、[preset 差異](preset_diff.md) 及 [逐次核對 JSON](stage2_gate_smoke.json)。
