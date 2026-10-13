# DET2 開跑前核對：820 次在時間與磁碟門檻內

**結論：** DET1 lw0 的 45 次逐位元重現通過，三組正式 lw0 可沿用；DET2 新跑為 4 臂 × 205 條＝**820 次**。階段二 smoke 20／20 完整，三個 lw1 組別的凍結步數均為 0。預估正式執行 **60–105 分鐘**，低於三小時停點；目前磁碟可用約 **17 GiB**，預估 DET2 原始輸出約 **66 MB**，即使保留數倍餘裕仍足夠。

| 資料 | 串流數 | 新跑次數 | GT 狀態 |
|---|---:|---:|---|
| synthetic_multiclass | 40 | 160 | 有 GT；四個暖機前 GT 依 DET1 規則排除 |
| insects_abrupt_balanced | 1 | 4 | 5 個 GT |
| insects_incremental_balanced | 1 | 4 | GT 空；只作描述 |
| insects_incremental_gradual_balanced | 1 | 4 | 1 個 GT |
| insects_incremental_abrupt_reoccurring_balanced | 1 | 4 | 2 個 GT |
| insects_incremental_reoccurring_balanced | 1 | 4 | 2 個 GT |
| injected_paper_electricity | 160 | 640 | 八 cell 各取 registry 前 20 trials，原始 input 座標 |

時間估計以 DET1 相同 205 條、五臂 1,025 次的實測 **77 分 4 秒**為基準，按 820／1,025 比例得約 62 分鐘，再留近七成餘裕；smoke 的新臂 runtime 未見超過此範圍的趨勢。輸出大小以 DET1 原始目錄約 82 MB 比例換算約 66 MB；正式根目錄單獨使用 `outputs/benchmark/det2/`。空間數字取自開跑前 `df -h .`，精度以檔案系統顯示為準。

正式順序固定為 synthetic＋全部 INSECTS，接著 injected；6 workers，tmux、`caffeinate -dims`、`--resume`、warning 事件紀錄及 `outputs/det2/logs/`。若單次 job 失敗，腳本對該資料集以 `--resume` 重試一次並記完成數。
