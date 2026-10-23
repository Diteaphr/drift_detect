# DET2-A1d 與 DET1-A1-lw0 的 preset 差異

**結論：** 執行 config 唯一差異為 `detector_delta: 0.05 → 0.01`；其他三項為識別與來源欄位。基準：`configs/presets/det1_dual_adwin_lw0.json`。

| 欄位 | DET1-A1-lw0 | DET2-A1d-lw0 |
|---|---|---|
| `config.detector_delta` | `0.05` | `0.01` |
| `description` | `DET1 A1: bidirectional dual ADWIN, timeout 0; learn during warning=False.` | `DET2 A1d: dual ADWIN drift delta=0.01; warning delta=0.1, bidirectional, timeout 0, learn during warning=False.` |
| `name` | `det1_dual_adwin_lw0` | `det2_dual_adwin_d001_lw0` |
| `source` | `docs/ECPF_DET1_預註冊.md, 2026-10-13 revision` | `docs/ECPF_DET2_預註冊.md, 2026-10-13` |

Q3 敏感度以同一 lw0 ECPF 底座、資料與評分比較，不把 A1d 納入 Q1/Q2。
