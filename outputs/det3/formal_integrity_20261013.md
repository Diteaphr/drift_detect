# DET3 階段四：615 次正式新跑完整且來源固定

**結論：** 第一批 synthetic＋五條 INSECTS **135／135、0 失敗、1,960 秒**；第二批 injected **480／480、0 失敗、1,141 秒**。合計 **615／615、0 失敗、51 分 41 秒**。原始輸出約 34.0 MB，執行後可用磁碟約 14.3 GiB。

每臂 205 條，與 DET1／DET2 對應串流配對：synthetic 40、injected 160、INSECTS 5。每個 manifest 均記錄乾淨 commit `b86f5d679cba136705214f9fe9a5d5460d6bcaa4`、River 0.21.2、完整步數及 warning 事件；所有 run 的 warning 開啟數等於關閉與截尾之和，F-D1／F-H1 的實測凍結步數逐 run 為 0。完整計分、來源 SHA-256 與跨臂 `y_true` 配對稽核在階段五分析程式再次執行。

執行依[預註冊](../../docs/ECPF_DET3_預註冊.md)使用 6 workers、tmux 背景、整個 runner 包在 `caffeinate -dims`、`--resume`，log 存 `outputs/det3/logs/formal_20261013.log`。原始 run 只在本機 `outputs/benchmark/det3/`，未改動 DET1／DET2、smoke 或 gate 輸出。完整機器核對見[JSON](formal_integrity_20261013.json)。
