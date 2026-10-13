# DET2 階段三：820 次正式新跑完整且來源配對一致

**結論：** 第一批 synthetic＋五條 INSECTS **180／180、0 失敗、2,091 秒**；第二批 injected **640／640、0 失敗、1,113 秒**。合計 **820／820、0 失敗、3,204 秒（53 分 24 秒）**。正式原始輸出約 53 MB，目錄為 `outputs/benchmark/det2/`；執行後可用磁碟約 16 GiB。

每臂 205 條與 DET1 對應串流配對：synthetic 40、injected 160、INSECTS 5。每個 manifest 均記錄乾淨 commit `55bfc81999c98954ad5a4b4aa05df691faac0cff`、River `0.21.2`、完整步數、warning 事件；來源資料、registry、GT 與 DET1 相同，`y_true` 逐位元相同。每條 run 的 warning 開啟數等於關閉與截尾合計；三個 lw1 臂所有 run 的實測凍結步數皆為 **0**。

| 新跑組別 | 205 條完整 | 總凍結步數 |
|---|---:|---:|
| `det1_dual_adwin_lw1` | 205 | 0 |
| `det1_zone_hddm_a_lw1` | 205 | 0 |
| `det1_zone_rddm_lw1` | 205 | 0 |
| `det2_dual_adwin_d001_lw0` | 205 | 3,728,743 |

執行順序、6 workers、tmux＋`caffeinate -dims`、`--resume` 與 log 路徑見 [預註冊](../../docs/ECPF_DET2_預註冊.md)；完整機器核對見 [JSON](formal_integrity_20261013.json)。未修改 DET1 正式輸出。
