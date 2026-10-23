# DET4 preset 差異：18 組只改 warning／confirm detector

**結論：** 18/18 preset 的 `role=ablation`；相對各自 S0／S1 範本，執行 config 的差異只有 `ecpf_warning_detector` 與 `ecpf_drift_detector`。名稱、描述與來源是非執行 metadata。

| preset | 範本 | warning | confirm | 其他 execution config 差異 |
|---|---|---|---|---|
| `det4_s0_wadwin_cadwin` | `det1_dual_adwin_lw0` | `adwin` | `adwin` | 無 |
| `det4_s0_wadwin_chddma` | `det1_dual_adwin_lw0` | `adwin` | `hddm_a` | 無 |
| `det4_s0_wadwin_crddm` | `det1_dual_adwin_lw0` | `adwin` | `rddm` | 無 |
| `det4_s0_whddma_cadwin` | `det1_dual_adwin_lw0` | `hddm_a` | `adwin` | 無 |
| `det4_s0_whddma_chddma` | `det1_dual_adwin_lw0` | `hddm_a` | `hddm_a` | 無 |
| `det4_s0_whddma_crddm` | `det1_dual_adwin_lw0` | `hddm_a` | `rddm` | 無 |
| `det4_s0_wrddm_cadwin` | `det1_dual_adwin_lw0` | `rddm` | `adwin` | 無 |
| `det4_s0_wrddm_chddma` | `det1_dual_adwin_lw0` | `rddm` | `hddm_a` | 無 |
| `det4_s0_wrddm_crddm` | `det1_dual_adwin_lw0` | `rddm` | `rddm` | 無 |
| `det4_s1_wadwin_cadwin` | `det3_full_dual_adwin_lw1` | `adwin` | `adwin` | 無 |
| `det4_s1_wadwin_chddma` | `det3_full_dual_adwin_lw1` | `adwin` | `hddm_a` | 無 |
| `det4_s1_wadwin_crddm` | `det3_full_dual_adwin_lw1` | `adwin` | `rddm` | 無 |
| `det4_s1_whddma_cadwin` | `det3_full_dual_adwin_lw1` | `hddm_a` | `adwin` | 無 |
| `det4_s1_whddma_chddma` | `det3_full_dual_adwin_lw1` | `hddm_a` | `hddm_a` | 無 |
| `det4_s1_whddma_crddm` | `det3_full_dual_adwin_lw1` | `hddm_a` | `rddm` | 無 |
| `det4_s1_wrddm_cadwin` | `det3_full_dual_adwin_lw1` | `rddm` | `adwin` | 無 |
| `det4_s1_wrddm_chddma` | `det3_full_dual_adwin_lw1` | `rddm` | `hddm_a` | 無 |
| `det4_s1_wrddm_crddm` | `det3_full_dual_adwin_lw1` | `rddm` | `rddm` | 無 |

S0 範本固定 lw0、無 reference／guard／timeout；S1 範本固定 lw1、frozen reference、leader guard 與 1000 步 timeout。`main_preset` 未修改。
