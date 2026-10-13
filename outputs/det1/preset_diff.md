# 16 個 DET1 ECPF preset 只改已核准欄位；A6 沿用既有檔

**結論：** 與 `ecpf_paper.json` 比對，16 個 ECPF preset 均保留 HT、ECPF strict swap、fade、pool cap 10、warm start 200 及 River 0.21.2 要求。兩種 warning 訓練開關明寫，A0 只限有 GT 的三組資料，A5u 只作次要分析。`det1` suite 含 16 個新 ECPF preset 與既有 `e10bft` 一次。Detector-only 四組另列，不在 suite 中。來源：[DET1 預註冊與 2026-10-13 修訂](../../docs/ECPF_DET1_預註冊.html)。

| Preset | 與 `ecpf_paper.config` 不同或新加的欄位 |
|---|---|
| `det1_oracle60_lw0` | `detector_delta_w=0.1`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_signal_mode="oracle_input_60"`, `ecpf_warning_length=60`, `ecpf_warning_signal="error"` |
| `det1_oracle60_lw1` | `detector_delta_w=0.1`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_signal_mode="oracle_input_60"`, `ecpf_warning_length=60`, `ecpf_warning_signal="error"` |
| `det1_dual_adwin_lw0` | `detector_delta_w=0.1`, `ecpf_adwin_one_sided=false`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_warning_signal="error"` |
| `det1_dual_adwin_lw1` | `detector_delta_w=0.1`, `ecpf_adwin_one_sided=false`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_warning_signal="error"` |
| `det1_dual_adwin_t1000_lw0` | `detector_delta_w=0.1`, `ecpf_adwin_one_sided=false`, `ecpf_detector_warning_timeout=1000`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_warning_signal="error"` |
| `det1_dual_adwin_t1000_lw1` | `detector_delta_w=0.1`, `ecpf_adwin_one_sided=false`, `ecpf_detector_warning_timeout=1000`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_warning_signal="error"` |
| `det1_zone_ddm_lw0` | `detector_delta_w=0.1`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="ddm"` |
| `det1_zone_ddm_lw1` | `detector_delta_w=0.1`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="ddm"` |
| `det1_zone_hddm_a_lw0` | `detector_delta_w=0.1`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="hddm_a"` |
| `det1_zone_hddm_a_lw1` | `detector_delta_w=0.1`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="hddm_a"` |
| `det1_zone_rddm_lw0` | `detector_delta_w=0.1`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="rddm"` |
| `det1_zone_rddm_lw1` | `detector_delta_w=0.1`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="rddm"` |
| `det1_zone_magseed_lw0` | `detector_alpha=0.8`, `detector_delta_w=0.1`, `detector_epsilon=0.01`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="magseed"` |
| `det1_zone_magseed_lw1` | `detector_alpha=0.8`, `detector_delta_w=0.1`, `detector_epsilon=0.01`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="magseed"` |
| `det1_zone_magseed_upward_lw0` | `detector_alpha=0.8`, `detector_delta_w=0.1`, `detector_epsilon=0.01`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=false`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="magseed_upward"` |
| `det1_zone_magseed_upward_lw1` | `detector_alpha=0.8`, `detector_delta_w=0.1`, `detector_epsilon=0.01`, `ecpf_detector_warning_timeout=0`, `ecpf_drift_signal="error"`, `ecpf_learn_during_warning=true`, `ecpf_warning_signal="error"`, `ecpf_zone_detector="magseed_upward"` |

## Detector-only 四組保持 Cerqueira 的訓練協定

| Preset | Detector | 輸入 | 訓練與 reset |
|---|---|---|---|
| `det_ddm` | `ddm` | 0/1 error，前 25% 原始 input 不餵 detector | 單棵 HT 持續訓練，不因警報重置；detector 自身依原始語意維持／重置 |
| `det_hddm_a` | `hddm_a` | 0/1 error，前 25% 原始 input 不餵 detector | 單棵 HT 持續訓練，不因警報重置；detector 自身依原始語意維持／重置 |
| `det_rddm` | `rddm` | 0/1 error，前 25% 原始 input 不餵 detector | 單棵 HT 持續訓練，不因警報重置；detector 自身依原始語意維持／重置 |
| `det_magseed` | `magseed` | 0/1 error，前 25% 原始 input 不餵 detector | 單棵 HT 持續訓練，不因警報重置；detector 自身依原始語意維持／重置 |

**來源限制：** `det_magseed` 依 Chen（2016）學位論文、X 解讀與雙向絕對差；尚無 2015 會議版或原作者實作的逐事件對照。A0 使用新增的 `oracle_input_60`，不改既有 `oracle_60`。
