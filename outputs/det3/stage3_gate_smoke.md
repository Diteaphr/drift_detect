# DET3 階段三：四個沿用組別逐位元一致，三個新組別通過 smoke

**結論：** 固定 seed `20261012` 選 injected 9、synthetic 5、INSECTS 1 條，對 P-D、P-H、P-D1、P-H1 合計 **60／60** 次 `y_true`、`y_pred`、`alarm_idx` 與適用的 `alarm_idx_input` 逐位元相同，因此沿用 DET1／DET2 正式輸出。F-D0、F-D1、F-H1 各跑 injected 2 條完整、synthetic 2 條前 5,000 步、INSECTS abrupt 1 條前 5,000 步，合計 **15／15** smoke 通過。

| 核對 | 結果 |
|---|---|
| manifest／版本／固定參數 | 15 條完整；River 0.21.2、HT、reference／guard／timeout 設定與 preset 一致 |
| 計分 | 15 條的 accuracy、TP／FP／FN、警報數及可計分預測數由儲存的預測與 GT 重算一致 |
| warning 守恆 | 每 run 開啟 = 關閉 + 結尾截尾；樣本合計確認 6、逾時關閉 11、zone 離區關閉 23 |
| lw1 凍結 | F-D1、F-H1 共 10 條逐 run 均為 0 |
| reference 接線 | F-H1 的一條完整 injected trace 共 41,524 步，zone 的 warning/drift 值逐步等於 reference 0/1 損失，觀察到 1 次 reference switch |
| 守衛接線 | trace 每步含 `guard_drift`；該自然串流觸發 0 次。另以隔離的單步強制守衛確認測試，確認 trace 有 1 次守衛 drift、合併 drift 與 warning 確認；不進正式計分 |

**篩選命令偏離：** CLI `--cells` 做子字串比對，synthetic 額外執行 4 條 × 4 臂＝16 次；固定抽中的 20 次 synthetic 仍逐位元相同，額外 run 留在隔離 `repro/`，不進正式分析。INSECTS 的 registry 檔名 stem 與資料集名稱不同，首次篩選為 0 run 並留下空 `runs.csv`；重跑時在新的 `repro/retry/` 目錄執行唯一串流四臂，均逐位元相同。上述問題只在閘門命令與隔離輸出，不改 preset、pipeline、判準或正式資料。詳見[抽樣](repro_selection.json)、[逐位元驗證](repro_verification.json)、[smoke 稽核](stage3_smoke_audit.json)、[trace 診斷](stage3_trace_diagnostics.json)與[preset 差異](preset_diff.md)。
