# 正式執行前核對：五組 lw0、1,025 次，未觸發停跑條件

本核對完成於預註冊縮減修訂提交 `c53db93` 之後、任何正式 report run 之前。選 A1–A5 的 `lw0`，第一批 synthetic 200 次與 INSECTS 25 次，第二批 injected 800 次。GT 檔逐一讀取 JSON，非以換行數判定；五份檔案都存在。

| INSECTS registry dataset | CSV 筆數 | GT 標記數 | 正式用途 |
|---|---:|---:|---|
| `insects_abrupt_balanced` | 52,848 | 5 | P1/P2、方向與型態 |
| `insects_incremental_balanced` | 57,018 | 0 | 只報 accuracy、警報數、runtime |
| `insects_incremental_gradual_balanced` | 24,150 | 1 | P1/P2、方向與型態 |
| `insects_incremental_abrupt_reoccurring_balanced` | 79,986 | 2 | P1/P2、方向與型態 |
| `insects_incremental_reoccurring_balanced` | 79,986 | 2 | P1/P2、方向與型態 |

資料來源：[registry](../../configs/datasets_0921.json) 與其中五個 sibling `*_drift_times.txt`。有 GT 的四條共同組成「INSECTS」判定層；空 GT 的 incremental 不計 TP/FP、C、X。

以 [階段五 smoke 稽核](stage5_smoke_audit.json)中所選五組 runtime，injected 24→160 串流、synthetic 5,000→100,000 步、INSECTS 依完整 CSV 筆數線性換算，約 **15,500 CPU 秒**；六工理想下限 **0.72 小時**。長串流成本及檔案 I/O 另留餘裕，執行估計 **1–2.5 小時**，低於 3 小時停跑門檻。此為估計而非結果。

開跑前 `df -k .` 顯示可用 **17,626,092 KiB（約 16.8 GiB）**。所選組別 smoke 原始檔依 trial 數及步數外推約 **111 MB**；考慮 warning 事件、manifest、CSV 與 log，先保守預留 **500 MB**，磁碟充足。六工按 smoke 峰值每 worker 約 435 MB，基本工作集約 2.6 GB，另有主程序及資料載入成本。

正式輸出 `outputs/benchmark/det1/` 與本機 log `outputs/det1/logs/` 分別隔離並忽略原始輸出；`--resume` 需乾淨 Git、相同 commit／preset／registry／資料 SHA-256，不能跳過不相符 run。tmux 3.8 與 `caffeinate` 已可用。若執行中途失敗，應保留已完成 run，以相同提交重跑腳本；不得手改 manifest 或原始數據。
