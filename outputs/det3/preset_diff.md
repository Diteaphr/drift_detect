# DET3 preset 差異：共同 ECPF 論文底座，加上 E10bFT 分類元件

**結論：** 三個新臂均保留 `ecpf_paper` 的 strict swap、ECPF fade 與 pool cap 10；從 E10bFT 只取 frozen reference、500 步二次凍結、leader 守衛、1,000 步 warning 逾時及分類不生效的 frozen scale。F-D0/F-D1 只差 lw 開關；F-D1/F-H1 只差 zone detector。

## 相對 `ecpf_paper.json` 的 config 差異

| 欄位 | 基準 | F-D0 | F-D1 | F-H1 |
|---|---|---|---|---|
| `detector_delta_w` | `"<default>"` | `0.1` | `0.1` | `0.1` |
| `ecpf_adwin_one_sided` | `"<default>"` | `false` | `false` | `false` |
| `ecpf_detector_warning_timeout` | `"<default>"` | `1000` | `1000` | `1000` |
| `ecpf_drift_signal` | `"<default>"` | `"error"` | `"error"` | `"error"` |
| `ecpf_guard_frozen_scale` | `"<default>"` | `500` | `500` | `500` |
| `ecpf_leader_guard` | `"<default>"` | `true` | `true` | `true` |
| `ecpf_learn_during_warning` | `"<default>"` | `false` | `true` | `true` |
| `ecpf_reference_signal` | `"<default>"` | `true` | `true` | `true` |
| `ecpf_reference_warmup` | `"<default>"` | `500` | `500` | `500` |
| `ecpf_warning_signal` | `"<default>"` | `"error"` | `"error"` | `"error"` |
| `ecpf_zone_detector` | `"<default>"` | `"<default>"` | `"<default>"` | `"hddm_a"` |

## 相對 `e10bft.json` 的 config 差異

| 欄位 | 基準 | F-D0 | F-D1 | F-H1 |
|---|---|---|---|---|
| `detector_delta_w` | `"<default>"` | `0.1` | `0.1` | `0.1` |
| `ecpf_adwin_one_sided` | `"<default>"` | `false` | `false` | `false` |
| `ecpf_fade_enabled` | `"<default>"` | `true` | `true` | `true` |
| `ecpf_fade_policy` | `"<default>"` | `"ecpf"` | `"ecpf"` | `"ecpf"` |
| `ecpf_learn_during_warning` | `false` | `false` | `true` | `true` |
| `ecpf_max_pool_size` | `"<default>"` | `10` | `10` | `10` |
| `ecpf_swap_policy` | `"<default>"` | `"strict"` | `"strict"` | `"strict"` |
| `ecpf_zone_detector` | `"<default>"` | `"<default>"` | `"<default>"` | `"hddm_a"` |

`<default>` 表示該 preset 未明寫、由 `PipelineConfig` 預設決定。E10bFT 未明寫 swap/fade/pool policy，DET3 明寫論文底座值；E10bFT 的 regression task override 未移入，本輪僅分類。`ecpf_guard_frozen_scale=500` 在分類分支不生效。
