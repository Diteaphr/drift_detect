# dataset_0921 vs literature (2026-10-21 01:55)

Runs used: 152 of 532 (smoke runs excluded, non-comparable runs excluded).
Registry: `configs/datasets_0921.json`. Metrics: `src/metrics/evaluate_run.py`.

## Prequential datasets

Difference = our mean - best literature value for that metric. 95% CI is a t-interval over seeds.

### electricity (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e10bft | acc_prequential | 1 | 0.8267 | - | - | 0.9500 | TabFM+FIFO | -0.1233 | 0.9008 | ARF (MOA, 100 trees) | -0.0741 |
| e10bft | kappa_t | 1 | -0.1814 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5051 | 0.3237 | ARF (MOA, 100 trees) | -0.5051 |
| e10bft | kappa_m | 1 | 0.5916 | - | - | - | - | - | - | - | - |
| e10bft | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | acc_prequential | 1 | 0.8315 | - | - | 0.9500 | TabFM+FIFO | -0.1185 | 0.9008 | ARF (MOA, 100 trees) | -0.0693 |
| e10bft_decay_g050 | kappa_t | 1 | -0.1486 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4723 | 0.3237 | ARF (MOA, 100 trees) | -0.4723 |
| e10bft_decay_g050 | kappa_m | 1 | 0.6030 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_decay_g050 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | acc_prequential | 1 | 0.8270 | - | - | 0.9500 | TabFM+FIFO | -0.1230 | 0.9008 | ARF (MOA, 100 trees) | -0.0738 |
| e10bft_decay_g080 | kappa_t | 1 | -0.1795 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5032 | 0.3237 | ARF (MOA, 100 trees) | -0.5032 |
| e10bft_decay_g080 | kappa_m | 1 | 0.5923 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_decay_g080 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | acc_prequential | 1 | 0.8282 | - | - | 0.9500 | TabFM+FIFO | -0.1218 | 0.9008 | ARF (MOA, 100 trees) | -0.0726 |
| e10bft_decay_g095 | kappa_t | 1 | -0.1709 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4946 | 0.3237 | ARF (MOA, 100 trees) | -0.4946 |
| e10bft_decay_g095 | kappa_m | 1 | 0.5953 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_decay_g095 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | acc_prequential | 1 | 0.8344 | - | - | 0.9500 | TabFM+FIFO | -0.1156 | 0.9008 | ARF (MOA, 100 trees) | -0.0664 |
| e10bft_density_b2 | kappa_t | 1 | -0.1288 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4525 | 0.3237 | ARF (MOA, 100 trees) | -0.4525 |
| e10bft_density_b2 | kappa_m | 1 | 0.6098 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_density_b2 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | acc_prequential | 1 | 0.8322 | - | - | 0.9500 | TabFM+FIFO | -0.1178 | 0.9008 | ARF (MOA, 100 trees) | -0.0686 |
| e10bft_density_b4 | kappa_t | 1 | -0.1438 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4675 | 0.3237 | ARF (MOA, 100 trees) | -0.4675 |
| e10bft_density_b4 | kappa_m | 1 | 0.6046 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_density_b4 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | acc_prequential | 1 | 0.8257 | - | - | 0.9500 | TabFM+FIFO | -0.1243 | 0.9008 | ARF (MOA, 100 trees) | -0.0751 |
| e10bft_density_b8 | kappa_t | 1 | -0.1883 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5120 | 0.3237 | ARF (MOA, 100 trees) | -0.5120 |
| e10bft_density_b8 | kappa_m | 1 | 0.5892 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_density_b8 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | acc_prequential | 1 | 0.8274 | - | - | 0.9500 | TabFM+FIFO | -0.1226 | 0.9008 | ARF (MOA, 100 trees) | -0.0734 |
| e10bft_entry_f15 | kappa_t | 1 | -0.1766 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5003 | 0.3237 | ARF (MOA, 100 trees) | -0.5003 |
| e10bft_entry_f15 | kappa_m | 1 | 0.5933 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_entry_f15 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | acc_prequential | 1 | 0.8274 | - | - | 0.9500 | TabFM+FIFO | -0.1226 | 0.9008 | ARF (MOA, 100 trees) | -0.0734 |
| e10bft_entry_f30 | kappa_t | 1 | -0.1766 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5003 | 0.3237 | ARF (MOA, 100 trees) | -0.5003 |
| e10bft_entry_f30 | kappa_m | 1 | 0.5933 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_entry_f30 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | acc_prequential | 1 | 0.8299 | - | - | 0.9500 | TabFM+FIFO | -0.1201 | 0.9008 | ARF (MOA, 100 trees) | -0.0709 |
| e10bft_entry_f5 | kappa_t | 1 | -0.1596 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4833 | 0.3237 | ARF (MOA, 100 trees) | -0.4833 |
| e10bft_entry_f5 | kappa_m | 1 | 0.5992 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_entry_f5 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | acc_prequential | 1 | 0.8307 | - | - | 0.9500 | TabFM+FIFO | -0.1193 | 0.9008 | ARF (MOA, 100 trees) | -0.0701 |
| e10bft_freq_b2 | kappa_t | 1 | -0.1540 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4777 | 0.3237 | ARF (MOA, 100 trees) | -0.4777 |
| e10bft_freq_b2 | kappa_m | 1 | 0.6011 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_freq_b2 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | acc_prequential | 1 | 0.8322 | - | - | 0.9500 | TabFM+FIFO | -0.1178 | 0.9008 | ARF (MOA, 100 trees) | -0.0686 |
| e10bft_freq_b4 | kappa_t | 1 | -0.1438 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4675 | 0.3237 | ARF (MOA, 100 trees) | -0.4675 |
| e10bft_freq_b4 | kappa_m | 1 | 0.6046 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_freq_b4 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | acc_prequential | 1 | 0.8294 | - | - | 0.9500 | TabFM+FIFO | -0.1206 | 0.9008 | ARF (MOA, 100 trees) | -0.0714 |
| e10bft_freq_b8 | kappa_t | 1 | -0.1631 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4868 | 0.3237 | ARF (MOA, 100 trees) | -0.4868 |
| e10bft_freq_b8 | kappa_m | 1 | 0.5980 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_freq_b8 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | acc_prequential | 1 | 0.8301 | - | - | 0.9500 | TabFM+FIFO | -0.1199 | 0.9008 | ARF (MOA, 100 trees) | -0.0707 |
| e10bft_rent_l1 | kappa_t | 1 | -0.1579 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4816 | 0.3237 | ARF (MOA, 100 trees) | -0.4816 |
| e10bft_rent_l1 | kappa_m | 1 | 0.5998 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_rent_l1 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | acc_prequential | 1 | 0.8307 | - | - | 0.9500 | TabFM+FIFO | -0.1193 | 0.9008 | ARF (MOA, 100 trees) | -0.0701 |
| e10bft_rent_l10 | kappa_t | 1 | -0.1537 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4774 | 0.3237 | ARF (MOA, 100 trees) | -0.4774 |
| e10bft_rent_l10 | kappa_m | 1 | 0.6012 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_rent_l10 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | acc_prequential | 1 | 0.8336 | - | - | 0.9500 | TabFM+FIFO | -0.1164 | 0.9008 | ARF (MOA, 100 trees) | -0.0672 |
| e10bft_rent_l2 | kappa_t | 1 | -0.1342 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4579 | 0.3237 | ARF (MOA, 100 trees) | -0.4579 |
| e10bft_rent_l2 | kappa_m | 1 | 0.6080 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_rent_l2 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | acc_prequential | 1 | 0.8283 | - | - | 0.9500 | TabFM+FIFO | -0.1217 | 0.9008 | ARF (MOA, 100 trees) | -0.0725 |
| e10bft_rent_l5 | kappa_t | 1 | -0.1706 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4943 | 0.3237 | ARF (MOA, 100 trees) | -0.4943 |
| e10bft_rent_l5 | kappa_m | 1 | 0.5954 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_rent_l5 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | acc_prequential | 1 | 0.8288 | - | - | 0.9500 | TabFM+FIFO | -0.1212 | 0.9008 | ARF (MOA, 100 trees) | -0.0720 |
| e10bft_reuse_value | kappa_t | 1 | -0.1667 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4904 | 0.3237 | ARF (MOA, 100 trees) | -0.4904 |
| e10bft_reuse_value | kappa_m | 1 | 0.5967 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_reuse_value | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft_subst | acc_prequential | 1 | 0.8297 | - | - | 0.9500 | TabFM+FIFO | -0.1203 | 0.9008 | ARF (MOA, 100 trees) | -0.0711 |
| e10bft_subst | kappa_t | 1 | -0.1608 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4845 | 0.3237 | ARF (MOA, 100 trees) | -0.4845 |
| e10bft_subst | kappa_m | 1 | 0.5988 | - | - | - | - | - | - | - | - |
| e10bft_subst | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| e10bft_subst | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | acc_prequential | 1 | 0.8370 | - | - | 0.9500 | TabFM+FIFO | -0.1130 | 0.9008 | ARF (MOA, 100 trees) | -0.0638 |
| ecpf_decay_g050 | kappa_t | 1 | -0.1110 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4347 | 0.3237 | ARF (MOA, 100 trees) | -0.4347 |
| ecpf_decay_g050 | kappa_m | 1 | 0.6160 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_decay_g050 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | acc_prequential | 1 | 0.8278 | - | - | 0.9500 | TabFM+FIFO | -0.1222 | 0.9008 | ARF (MOA, 100 trees) | -0.0730 |
| ecpf_decay_g080 | kappa_t | 1 | -0.1736 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4973 | 0.3237 | ARF (MOA, 100 trees) | -0.4973 |
| ecpf_decay_g080 | kappa_m | 1 | 0.5943 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_decay_g080 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | acc_prequential | 1 | 0.8268 | - | - | 0.9500 | TabFM+FIFO | -0.1232 | 0.9008 | ARF (MOA, 100 trees) | -0.0740 |
| ecpf_decay_g095 | kappa_t | 1 | -0.1802 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5039 | 0.3237 | ARF (MOA, 100 trees) | -0.5039 |
| ecpf_decay_g095 | kappa_m | 1 | 0.5921 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_decay_g095 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | acc_prequential | 1 | 0.8333 | - | - | 0.9500 | TabFM+FIFO | -0.1167 | 0.9008 | ARF (MOA, 100 trees) | -0.0675 |
| ecpf_density_b2 | kappa_t | 1 | -0.1364 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4601 | 0.3237 | ARF (MOA, 100 trees) | -0.4601 |
| ecpf_density_b2 | kappa_m | 1 | 0.6072 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_density_b2 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | acc_prequential | 1 | 0.8281 | - | - | 0.9500 | TabFM+FIFO | -0.1219 | 0.9008 | ARF (MOA, 100 trees) | -0.0727 |
| ecpf_density_b4 | kappa_t | 1 | -0.1718 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4955 | 0.3237 | ARF (MOA, 100 trees) | -0.4955 |
| ecpf_density_b4 | kappa_m | 1 | 0.5950 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_density_b4 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | acc_prequential | 1 | 0.8288 | - | - | 0.9500 | TabFM+FIFO | -0.1212 | 0.9008 | ARF (MOA, 100 trees) | -0.0720 |
| ecpf_density_b8 | kappa_t | 1 | -0.1668 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4905 | 0.3237 | ARF (MOA, 100 trees) | -0.4905 |
| ecpf_density_b8 | kappa_m | 1 | 0.5967 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_density_b8 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | acc_prequential | 1 | 0.8355 | - | - | 0.9500 | TabFM+FIFO | -0.1145 | 0.9008 | ARF (MOA, 100 trees) | -0.0653 |
| ecpf_entry_f15 | kappa_t | 1 | -0.1211 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4448 | 0.3237 | ARF (MOA, 100 trees) | -0.4448 |
| ecpf_entry_f15 | kappa_m | 1 | 0.6125 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_entry_f15 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | acc_prequential | 1 | 0.8355 | - | - | 0.9500 | TabFM+FIFO | -0.1145 | 0.9008 | ARF (MOA, 100 trees) | -0.0653 |
| ecpf_entry_f30 | kappa_t | 1 | -0.1211 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4448 | 0.3237 | ARF (MOA, 100 trees) | -0.4448 |
| ecpf_entry_f30 | kappa_m | 1 | 0.6125 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_entry_f30 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | acc_prequential | 1 | 0.8255 | - | - | 0.9500 | TabFM+FIFO | -0.1245 | 0.9008 | ARF (MOA, 100 trees) | -0.0753 |
| ecpf_entry_f5 | kappa_t | 1 | -0.1894 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5131 | 0.3237 | ARF (MOA, 100 trees) | -0.5131 |
| ecpf_entry_f5 | kappa_m | 1 | 0.5889 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_entry_f5 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | acc_prequential | 1 | 0.8329 | - | - | 0.9500 | TabFM+FIFO | -0.1171 | 0.9008 | ARF (MOA, 100 trees) | -0.0679 |
| ecpf_freq_b2 | kappa_t | 1 | -0.1391 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4628 | 0.3237 | ARF (MOA, 100 trees) | -0.4628 |
| ecpf_freq_b2 | kappa_m | 1 | 0.6062 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_freq_b2 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | acc_prequential | 1 | 0.8298 | - | - | 0.9500 | TabFM+FIFO | -0.1202 | 0.9008 | ARF (MOA, 100 trees) | -0.0710 |
| ecpf_freq_b4 | kappa_t | 1 | -0.1599 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4836 | 0.3237 | ARF (MOA, 100 trees) | -0.4836 |
| ecpf_freq_b4 | kappa_m | 1 | 0.5991 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_freq_b4 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | acc_prequential | 1 | 0.8288 | - | - | 0.9500 | TabFM+FIFO | -0.1212 | 0.9008 | ARF (MOA, 100 trees) | -0.0720 |
| ecpf_freq_b8 | kappa_t | 1 | -0.1668 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4905 | 0.3237 | ARF (MOA, 100 trees) | -0.4905 |
| ecpf_freq_b8 | kappa_m | 1 | 0.5967 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_freq_b8 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_paper | acc_prequential | 1 | 0.8276 | - | - | 0.9500 | TabFM+FIFO | -0.1224 | 0.9008 | ARF (MOA, 100 trees) | -0.0732 |
| ecpf_paper | kappa_t | 1 | -0.1751 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4988 | 0.3237 | ARF (MOA, 100 trees) | -0.4988 |
| ecpf_paper | kappa_m | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| ecpf_paper | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_paper | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | acc_prequential | 1 | 0.8276 | - | - | 0.9500 | TabFM+FIFO | -0.1224 | 0.9008 | ARF (MOA, 100 trees) | -0.0732 |
| ecpf_rent_l1 | kappa_t | 1 | -0.1751 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4988 | 0.3237 | ARF (MOA, 100 trees) | -0.4988 |
| ecpf_rent_l1 | kappa_m | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_rent_l1 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | acc_prequential | 1 | 0.8405 | - | - | 0.9500 | TabFM+FIFO | -0.1095 | 0.9008 | ARF (MOA, 100 trees) | -0.0603 |
| ecpf_rent_l10 | kappa_t | 1 | -0.0868 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4105 | 0.3237 | ARF (MOA, 100 trees) | -0.4105 |
| ecpf_rent_l10 | kappa_m | 1 | 0.6243 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_rent_l10 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | acc_prequential | 1 | 0.8299 | - | - | 0.9500 | TabFM+FIFO | -0.1201 | 0.9008 | ARF (MOA, 100 trees) | -0.0709 |
| ecpf_rent_l2 | kappa_t | 1 | -0.1593 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4830 | 0.3237 | ARF (MOA, 100 trees) | -0.4830 |
| ecpf_rent_l2 | kappa_m | 1 | 0.5993 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_rent_l2 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | acc_prequential | 1 | 0.8321 | - | - | 0.9500 | TabFM+FIFO | -0.1179 | 0.9008 | ARF (MOA, 100 trees) | -0.0687 |
| ecpf_rent_l5 | kappa_t | 1 | -0.1441 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4678 | 0.3237 | ARF (MOA, 100 trees) | -0.4678 |
| ecpf_rent_l5 | kappa_m | 1 | 0.6045 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_rent_l5 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | acc_prequential | 1 | 0.8299 | - | - | 0.9500 | TabFM+FIFO | -0.1201 | 0.9008 | ARF (MOA, 100 trees) | -0.0709 |
| ecpf_reuse_value | kappa_t | 1 | -0.1594 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4831 | 0.3237 | ARF (MOA, 100 trees) | -0.4831 |
| ecpf_reuse_value | kappa_m | 1 | 0.5992 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_reuse_value | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_subst | acc_prequential | 1 | 0.8299 | - | - | 0.9500 | TabFM+FIFO | -0.1201 | 0.9008 | ARF (MOA, 100 trees) | -0.0709 |
| ecpf_subst | kappa_t | 1 | -0.1594 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4831 | 0.3237 | ARF (MOA, 100 trees) | -0.4831 |
| ecpf_subst | kappa_m | 1 | 0.5992 | - | - | - | - | - | - | - | - |
| ecpf_subst | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| ecpf_subst | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |

OpenML 151 / MOA elecNormNew, 45,312 rows, same as literature. Calibrated: baseline_no_change_acc reproduces Souza et al. 85.33%.

### insects_abrupt_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e10bft | acc_window1000_mean | 1 | 0.6425 | - | - | 0.7434 | ARF | -0.1009 | 0.7434 | ARF | -0.1009 |
| e10bft | acc_prequential | 1 | 0.6469 | - | - | 0.6602 | NB + STEPD | -0.0133 | - | - | - |
| e10bft | kappa | 1 | 0.5762 | - | - | - | - | - | - | - | - |
| e10bft | n_alarms | 1 | 14.0000 | - | - | - | - | - | - | - | - |
| e10bft | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_decay_g050 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_decay_g050 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_decay_g080 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_decay_g080 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_decay_g095 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_decay_g095 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_density_b2 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_density_b2 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_density_b4 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_density_b4 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_density_b8 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_density_b8 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | acc_window1000_mean | 1 | 0.6364 | - | - | 0.7434 | ARF | -0.1070 | 0.7434 | ARF | -0.1070 |
| e10bft_entry_f15 | acc_prequential | 1 | 0.6408 | - | - | 0.6602 | NB + STEPD | -0.0194 | - | - | - |
| e10bft_entry_f15 | kappa | 1 | 0.5690 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | n_alarms | 1 | 18.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | f1 | 1 | 0.4167 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | acc_window1000_mean | 1 | 0.6364 | - | - | 0.7434 | ARF | -0.1070 | 0.7434 | ARF | -0.1070 |
| e10bft_entry_f30 | acc_prequential | 1 | 0.6408 | - | - | 0.6602 | NB + STEPD | -0.0194 | - | - | - |
| e10bft_entry_f30 | kappa | 1 | 0.5690 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | n_alarms | 1 | 18.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | f1 | 1 | 0.4167 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_entry_f5 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_entry_f5 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_freq_b2 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_freq_b2 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_freq_b4 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_freq_b4 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_freq_b8 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_freq_b8 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_rent_l1 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_rent_l1 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_rent_l10 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_rent_l10 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_rent_l2 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_rent_l2 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_rent_l5 | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_rent_l5 | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_reuse_value | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_reuse_value | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| e10bft_subst | acc_window1000_mean | 1 | 0.6408 | - | - | 0.7434 | ARF | -0.1026 | 0.7434 | ARF | -0.1026 |
| e10bft_subst | acc_prequential | 1 | 0.6452 | - | - | 0.6602 | NB + STEPD | -0.0150 | - | - | - |
| e10bft_subst | kappa | 1 | 0.5742 | - | - | - | - | - | - | - | - |
| e10bft_subst | n_alarms | 1 | 17.0000 | - | - | - | - | - | - | - | - |
| e10bft_subst | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft_subst | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_decay_g050 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_decay_g050 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_decay_g080 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_decay_g080 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_decay_g095 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_decay_g095 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | acc_window1000_mean | 1 | 0.6373 | - | - | 0.7434 | ARF | -0.1061 | 0.7434 | ARF | -0.1061 |
| ecpf_density_b2 | acc_prequential | 1 | 0.6415 | - | - | 0.6602 | NB + STEPD | -0.0187 | - | - | - |
| ecpf_density_b2 | kappa | 1 | 0.5698 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_density_b4 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_density_b4 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_density_b8 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_density_b8 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | acc_window1000_mean | 1 | 0.6314 | - | - | 0.7434 | ARF | -0.1120 | 0.7434 | ARF | -0.1120 |
| ecpf_entry_f15 | acc_prequential | 1 | 0.6356 | - | - | 0.6602 | NB + STEPD | -0.0246 | - | - | - |
| ecpf_entry_f15 | kappa | 1 | 0.5627 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | n_alarms | 1 | 21.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | f1 | 1 | 0.4828 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | acc_window1000_mean | 1 | 0.6314 | - | - | 0.7434 | ARF | -0.1120 | 0.7434 | ARF | -0.1120 |
| ecpf_entry_f30 | acc_prequential | 1 | 0.6356 | - | - | 0.6602 | NB + STEPD | -0.0246 | - | - | - |
| ecpf_entry_f30 | kappa | 1 | 0.5627 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | n_alarms | 1 | 21.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | f1 | 1 | 0.4828 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_entry_f5 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_entry_f5 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | acc_window1000_mean | 1 | 0.6349 | - | - | 0.7434 | ARF | -0.1085 | 0.7434 | ARF | -0.1085 |
| ecpf_freq_b2 | acc_prequential | 1 | 0.6392 | - | - | 0.6602 | NB + STEPD | -0.0210 | - | - | - |
| ecpf_freq_b2 | kappa | 1 | 0.5671 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | f1 | 1 | 0.4118 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_freq_b4 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_freq_b4 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_freq_b8 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_freq_b8 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_paper | acc_window1000_mean | 1 | 0.6384 | - | - | 0.7434 | ARF | -0.1050 | 0.7434 | ARF | -0.1050 |
| ecpf_paper | acc_prequential | 1 | 0.6426 | - | - | 0.6602 | NB + STEPD | -0.0176 | - | - | - |
| ecpf_paper | kappa | 1 | 0.5712 | - | - | - | - | - | - | - | - |
| ecpf_paper | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| ecpf_paper | f1 | 1 | 0.4571 | - | - | - | - | - | - | - | - |
| ecpf_paper | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_rent_l1 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_rent_l1 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_rent_l10 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_rent_l10 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_rent_l2 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_rent_l2 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_rent_l5 | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_rent_l5 | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_reuse_value | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_reuse_value | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_subst | acc_window1000_mean | 1 | 0.6351 | - | - | 0.7434 | ARF | -0.1083 | 0.7434 | ARF | -0.1083 |
| ecpf_subst | acc_prequential | 1 | 0.6393 | - | - | 0.6602 | NB + STEPD | -0.0209 | - | - | - |
| ecpf_subst | kappa | 1 | 0.5672 | - | - | - | - | - | - | - | - |
| ecpf_subst | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| ecpf_subst | f1 | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| ecpf_subst | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |

Same data and change points as Souza et al. 2020. Table 5 is sliding-window (1000) accuracy -> compare acc_window1000_mean; Table 6 (NB + detector) -> compare acc_prequential. delta_max is not from the paper (it reports detection counts only).

### insects_incremental_abrupt_reoccurring_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e10bft | acc_window1000_mean | 1 | 0.6603 | - | - | 0.7495 | ARF | -0.0892 | 0.7495 | ARF | -0.0892 |
| e10bft | acc_prequential | 1 | 0.6622 | - | - | 0.6877 | NB + STEPD | -0.0255 | - | - | - |
| e10bft | kappa | 1 | 0.5946 | - | - | - | - | - | - | - | - |
| e10bft | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| e10bft | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| e10bft | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | acc_window1000_mean | 1 | 0.6552 | - | - | 0.7495 | ARF | -0.0943 | 0.7495 | ARF | -0.0943 |
| e10bft_decay_g050 | acc_prequential | 1 | 0.6572 | - | - | 0.6877 | NB + STEPD | -0.0305 | - | - | - |
| e10bft_decay_g050 | kappa | 1 | 0.5886 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | acc_window1000_mean | 1 | 0.6553 | - | - | 0.7495 | ARF | -0.0942 | 0.7495 | ARF | -0.0942 |
| e10bft_decay_g080 | acc_prequential | 1 | 0.6572 | - | - | 0.6877 | NB + STEPD | -0.0305 | - | - | - |
| e10bft_decay_g080 | kappa | 1 | 0.5886 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | acc_window1000_mean | 1 | 0.6647 | - | - | 0.7495 | ARF | -0.0848 | 0.7495 | ARF | -0.0848 |
| e10bft_decay_g095 | acc_prequential | 1 | 0.6666 | - | - | 0.6877 | NB + STEPD | -0.0211 | - | - | - |
| e10bft_decay_g095 | kappa | 1 | 0.6000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | acc_window1000_mean | 1 | 0.6490 | - | - | 0.7495 | ARF | -0.1005 | 0.7495 | ARF | -0.1005 |
| e10bft_density_b2 | acc_prequential | 1 | 0.6509 | - | - | 0.6877 | NB + STEPD | -0.0368 | - | - | - |
| e10bft_density_b2 | kappa | 1 | 0.5811 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | n_alarms | 1 | 28.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | f1 | 1 | 0.3529 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | acc_window1000_mean | 1 | 0.6552 | - | - | 0.7495 | ARF | -0.0943 | 0.7495 | ARF | -0.0943 |
| e10bft_density_b4 | acc_prequential | 1 | 0.6572 | - | - | 0.6877 | NB + STEPD | -0.0305 | - | - | - |
| e10bft_density_b4 | kappa | 1 | 0.5886 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | acc_window1000_mean | 1 | 0.6647 | - | - | 0.7495 | ARF | -0.0848 | 0.7495 | ARF | -0.0848 |
| e10bft_density_b8 | acc_prequential | 1 | 0.6666 | - | - | 0.6877 | NB + STEPD | -0.0211 | - | - | - |
| e10bft_density_b8 | kappa | 1 | 0.6000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | acc_window1000_mean | 1 | 0.6483 | - | - | 0.7495 | ARF | -0.1012 | 0.7495 | ARF | -0.1012 |
| e10bft_entry_f15 | acc_prequential | 1 | 0.6503 | - | - | 0.6877 | NB + STEPD | -0.0374 | - | - | - |
| e10bft_entry_f15 | kappa | 1 | 0.5803 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | n_alarms | 1 | 28.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | f1 | 1 | 0.3529 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | acc_window1000_mean | 1 | 0.6483 | - | - | 0.7495 | ARF | -0.1012 | 0.7495 | ARF | -0.1012 |
| e10bft_entry_f30 | acc_prequential | 1 | 0.6503 | - | - | 0.6877 | NB + STEPD | -0.0374 | - | - | - |
| e10bft_entry_f30 | kappa | 1 | 0.5803 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | n_alarms | 1 | 28.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | f1 | 1 | 0.3529 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | acc_window1000_mean | 1 | 0.6607 | - | - | 0.7495 | ARF | -0.0888 | 0.7495 | ARF | -0.0888 |
| e10bft_entry_f5 | acc_prequential | 1 | 0.6626 | - | - | 0.6877 | NB + STEPD | -0.0251 | - | - | - |
| e10bft_entry_f5 | kappa | 1 | 0.5951 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | n_alarms | 1 | 31.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | f1 | 1 | 0.3243 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | acc_window1000_mean | 1 | 0.6469 | - | - | 0.7495 | ARF | -0.1026 | 0.7495 | ARF | -0.1026 |
| e10bft_freq_b2 | acc_prequential | 1 | 0.6488 | - | - | 0.6877 | NB + STEPD | -0.0389 | - | - | - |
| e10bft_freq_b2 | kappa | 1 | 0.5786 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | n_alarms | 1 | 36.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | f1 | 1 | 0.2857 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | acc_window1000_mean | 1 | 0.6552 | - | - | 0.7495 | ARF | -0.0943 | 0.7495 | ARF | -0.0943 |
| e10bft_freq_b4 | acc_prequential | 1 | 0.6572 | - | - | 0.6877 | NB + STEPD | -0.0305 | - | - | - |
| e10bft_freq_b4 | kappa | 1 | 0.5886 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | acc_window1000_mean | 1 | 0.6647 | - | - | 0.7495 | ARF | -0.0848 | 0.7495 | ARF | -0.0848 |
| e10bft_freq_b8 | acc_prequential | 1 | 0.6666 | - | - | 0.6877 | NB + STEPD | -0.0211 | - | - | - |
| e10bft_freq_b8 | kappa | 1 | 0.6000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | acc_window1000_mean | 1 | 0.6647 | - | - | 0.7495 | ARF | -0.0848 | 0.7495 | ARF | -0.0848 |
| e10bft_rent_l1 | acc_prequential | 1 | 0.6666 | - | - | 0.6877 | NB + STEPD | -0.0211 | - | - | - |
| e10bft_rent_l1 | kappa | 1 | 0.6000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | acc_window1000_mean | 1 | 0.6618 | - | - | 0.7495 | ARF | -0.0877 | 0.7495 | ARF | -0.0877 |
| e10bft_rent_l10 | acc_prequential | 1 | 0.6637 | - | - | 0.6877 | NB + STEPD | -0.0240 | - | - | - |
| e10bft_rent_l10 | kappa | 1 | 0.5965 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | acc_window1000_mean | 1 | 0.6649 | - | - | 0.7495 | ARF | -0.0846 | 0.7495 | ARF | -0.0846 |
| e10bft_rent_l2 | acc_prequential | 1 | 0.6668 | - | - | 0.6877 | NB + STEPD | -0.0209 | - | - | - |
| e10bft_rent_l2 | kappa | 1 | 0.6002 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | n_alarms | 1 | 31.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | f1 | 1 | 0.3243 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | acc_window1000_mean | 1 | 0.6552 | - | - | 0.7495 | ARF | -0.0943 | 0.7495 | ARF | -0.0943 |
| e10bft_rent_l5 | acc_prequential | 1 | 0.6572 | - | - | 0.6877 | NB + STEPD | -0.0305 | - | - | - |
| e10bft_rent_l5 | kappa | 1 | 0.5886 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | acc_window1000_mean | 1 | 0.6647 | - | - | 0.7495 | ARF | -0.0848 | 0.7495 | ARF | -0.0848 |
| e10bft_reuse_value | acc_prequential | 1 | 0.6666 | - | - | 0.6877 | NB + STEPD | -0.0211 | - | - | - |
| e10bft_reuse_value | kappa | 1 | 0.6000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_subst | acc_window1000_mean | 1 | 0.6607 | - | - | 0.7495 | ARF | -0.0888 | 0.7495 | ARF | -0.0888 |
| e10bft_subst | acc_prequential | 1 | 0.6626 | - | - | 0.6877 | NB + STEPD | -0.0251 | - | - | - |
| e10bft_subst | kappa | 1 | 0.5952 | - | - | - | - | - | - | - | - |
| e10bft_subst | n_alarms | 1 | 31.0000 | - | - | - | - | - | - | - | - |
| e10bft_subst | f1 | 1 | 0.3243 | - | - | - | - | - | - | - | - |
| e10bft_subst | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | acc_window1000_mean | 1 | 0.6548 | - | - | 0.7495 | ARF | -0.0947 | 0.7495 | ARF | -0.0947 |
| ecpf_decay_g050 | acc_prequential | 1 | 0.6567 | - | - | 0.6877 | NB + STEPD | -0.0310 | - | - | - |
| ecpf_decay_g050 | kappa | 1 | 0.5880 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | n_alarms | 1 | 38.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | f1 | 1 | 0.2727 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | acc_window1000_mean | 1 | 0.6625 | - | - | 0.7495 | ARF | -0.0870 | 0.7495 | ARF | -0.0870 |
| ecpf_decay_g080 | acc_prequential | 1 | 0.6645 | - | - | 0.6877 | NB + STEPD | -0.0232 | - | - | - |
| ecpf_decay_g080 | kappa | 1 | 0.5974 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | f1 | 1 | 0.2400 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | acc_window1000_mean | 1 | 0.6650 | - | - | 0.7495 | ARF | -0.0845 | 0.7495 | ARF | -0.0845 |
| ecpf_decay_g095 | acc_prequential | 1 | 0.6669 | - | - | 0.6877 | NB + STEPD | -0.0208 | - | - | - |
| ecpf_decay_g095 | kappa | 1 | 0.6003 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | acc_window1000_mean | 1 | 0.6548 | - | - | 0.7495 | ARF | -0.0947 | 0.7495 | ARF | -0.0947 |
| ecpf_density_b2 | acc_prequential | 1 | 0.6567 | - | - | 0.6877 | NB + STEPD | -0.0310 | - | - | - |
| ecpf_density_b2 | kappa | 1 | 0.5880 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | n_alarms | 1 | 42.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | f1 | 1 | 0.2500 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | acc_window1000_mean | 1 | 0.6635 | - | - | 0.7495 | ARF | -0.0860 | 0.7495 | ARF | -0.0860 |
| ecpf_density_b4 | acc_prequential | 1 | 0.6654 | - | - | 0.6877 | NB + STEPD | -0.0223 | - | - | - |
| ecpf_density_b4 | kappa | 1 | 0.5985 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | n_alarms | 1 | 37.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | f1 | 1 | 0.2791 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | acc_window1000_mean | 1 | 0.6650 | - | - | 0.7495 | ARF | -0.0845 | 0.7495 | ARF | -0.0845 |
| ecpf_density_b8 | acc_prequential | 1 | 0.6669 | - | - | 0.6877 | NB + STEPD | -0.0208 | - | - | - |
| ecpf_density_b8 | kappa | 1 | 0.6003 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | acc_window1000_mean | 1 | 0.6476 | - | - | 0.7495 | ARF | -0.1019 | 0.7495 | ARF | -0.1019 |
| ecpf_entry_f15 | acc_prequential | 1 | 0.6491 | - | - | 0.6877 | NB + STEPD | -0.0386 | - | - | - |
| ecpf_entry_f15 | kappa | 1 | 0.5789 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | n_alarms | 1 | 29.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | f1 | 1 | 0.3429 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | acc_window1000_mean | 1 | 0.6476 | - | - | 0.7495 | ARF | -0.1019 | 0.7495 | ARF | -0.1019 |
| ecpf_entry_f30 | acc_prequential | 1 | 0.6491 | - | - | 0.6877 | NB + STEPD | -0.0386 | - | - | - |
| ecpf_entry_f30 | kappa | 1 | 0.5789 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | n_alarms | 1 | 29.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | f1 | 1 | 0.3429 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | acc_window1000_mean | 1 | 0.6650 | - | - | 0.7495 | ARF | -0.0845 | 0.7495 | ARF | -0.0845 |
| ecpf_entry_f5 | acc_prequential | 1 | 0.6669 | - | - | 0.6877 | NB + STEPD | -0.0208 | - | - | - |
| ecpf_entry_f5 | kappa | 1 | 0.6003 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | acc_window1000_mean | 1 | 0.6616 | - | - | 0.7495 | ARF | -0.0879 | 0.7495 | ARF | -0.0879 |
| ecpf_freq_b2 | acc_prequential | 1 | 0.6632 | - | - | 0.6877 | NB + STEPD | -0.0245 | - | - | - |
| ecpf_freq_b2 | kappa | 1 | 0.5958 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | n_alarms | 1 | 43.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | f1 | 1 | 0.2449 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | acc_window1000_mean | 1 | 0.6635 | - | - | 0.7495 | ARF | -0.0860 | 0.7495 | ARF | -0.0860 |
| ecpf_freq_b4 | acc_prequential | 1 | 0.6654 | - | - | 0.6877 | NB + STEPD | -0.0223 | - | - | - |
| ecpf_freq_b4 | kappa | 1 | 0.5985 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | n_alarms | 1 | 37.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | f1 | 1 | 0.2791 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | acc_window1000_mean | 1 | 0.6650 | - | - | 0.7495 | ARF | -0.0845 | 0.7495 | ARF | -0.0845 |
| ecpf_freq_b8 | acc_prequential | 1 | 0.6669 | - | - | 0.6877 | NB + STEPD | -0.0208 | - | - | - |
| ecpf_freq_b8 | kappa | 1 | 0.6003 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_paper | acc_window1000_mean | 1 | 0.6460 | - | - | 0.7495 | ARF | -0.1035 | 0.7495 | ARF | -0.1035 |
| ecpf_paper | acc_prequential | 1 | 0.6479 | - | - | 0.6877 | NB + STEPD | -0.0398 | - | - | - |
| ecpf_paper | kappa | 1 | 0.5775 | - | - | - | - | - | - | - | - |
| ecpf_paper | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_paper | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_paper | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | acc_window1000_mean | 1 | 0.6568 | - | - | 0.7495 | ARF | -0.0927 | 0.7495 | ARF | -0.0927 |
| ecpf_rent_l1 | acc_prequential | 1 | 0.6587 | - | - | 0.6877 | NB + STEPD | -0.0290 | - | - | - |
| ecpf_rent_l1 | kappa | 1 | 0.5904 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | n_alarms | 1 | 38.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | f1 | 1 | 0.2727 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | acc_window1000_mean | 1 | 0.6570 | - | - | 0.7495 | ARF | -0.0925 | 0.7495 | ARF | -0.0925 |
| ecpf_rent_l10 | acc_prequential | 1 | 0.6589 | - | - | 0.6877 | NB + STEPD | -0.0288 | - | - | - |
| ecpf_rent_l10 | kappa | 1 | 0.5907 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | acc_window1000_mean | 1 | 0.6650 | - | - | 0.7495 | ARF | -0.0845 | 0.7495 | ARF | -0.0845 |
| ecpf_rent_l2 | acc_prequential | 1 | 0.6669 | - | - | 0.6877 | NB + STEPD | -0.0208 | - | - | - |
| ecpf_rent_l2 | kappa | 1 | 0.6003 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | acc_window1000_mean | 1 | 0.6530 | - | - | 0.7495 | ARF | -0.0965 | 0.7495 | ARF | -0.0965 |
| ecpf_rent_l5 | acc_prequential | 1 | 0.6545 | - | - | 0.6877 | NB + STEPD | -0.0332 | - | - | - |
| ecpf_rent_l5 | kappa | 1 | 0.5854 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | n_alarms | 1 | 32.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | f1 | 1 | 0.3158 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | acc_window1000_mean | 1 | 0.6650 | - | - | 0.7495 | ARF | -0.0845 | 0.7495 | ARF | -0.0845 |
| ecpf_reuse_value | acc_prequential | 1 | 0.6669 | - | - | 0.6877 | NB + STEPD | -0.0208 | - | - | - |
| ecpf_reuse_value | kappa | 1 | 0.6003 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | n_alarms | 1 | 35.0000 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | f1 | 1 | 0.2927 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_subst | acc_window1000_mean | 1 | 0.6644 | - | - | 0.7495 | ARF | -0.0851 | 0.7495 | ARF | -0.0851 |
| ecpf_subst | acc_prequential | 1 | 0.6663 | - | - | 0.6877 | NB + STEPD | -0.0214 | - | - | - |
| ecpf_subst | kappa | 1 | 0.5996 | - | - | - | - | - | - | - | - |
| ecpf_subst | n_alarms | 1 | 34.0000 | - | - | - | - | - | - | - | - |
| ecpf_subst | f1 | 1 | 0.3000 | - | - | - | - | - | - | - | - |
| ecpf_subst | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |

See insects_abrupt_balanced for the metric mapping.

### insects_incremental_reoccurring_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e10bft | acc_window1000_mean | 1 | 0.6716 | - | - | 0.7713 | ARF | -0.0997 | 0.7713 | ARF | -0.0997 |
| e10bft | acc_prequential | 1 | 0.6734 | - | - | 0.6982 | NB + SEED | -0.0248 | - | - | - |
| e10bft | kappa | 1 | 0.6081 | - | - | - | - | - | - | - | - |
| e10bft | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | acc_window1000_mean | 1 | 0.6791 | - | - | 0.7713 | ARF | -0.0922 | 0.7713 | ARF | -0.0922 |
| e10bft_decay_g050 | acc_prequential | 1 | 0.6809 | - | - | 0.6982 | NB + SEED | -0.0173 | - | - | - |
| e10bft_decay_g050 | kappa | 1 | 0.6171 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | n_alarms | 1 | 31.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | f1 | 1 | 0.2286 | - | - | - | - | - | - | - | - |
| e10bft_decay_g050 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | acc_window1000_mean | 1 | 0.6722 | - | - | 0.7713 | ARF | -0.0991 | 0.7713 | ARF | -0.0991 |
| e10bft_decay_g080 | acc_prequential | 1 | 0.6741 | - | - | 0.6982 | NB + SEED | -0.0241 | - | - | - |
| e10bft_decay_g080 | kappa | 1 | 0.6089 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | n_alarms | 1 | 30.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | f1 | 1 | 0.2353 | - | - | - | - | - | - | - | - |
| e10bft_decay_g080 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | acc_window1000_mean | 1 | 0.6736 | - | - | 0.7713 | ARF | -0.0977 | 0.7713 | ARF | -0.0977 |
| e10bft_decay_g095 | acc_prequential | 1 | 0.6754 | - | - | 0.6982 | NB + SEED | -0.0228 | - | - | - |
| e10bft_decay_g095 | kappa | 1 | 0.6105 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | n_alarms | 1 | 27.0000 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | f1 | 1 | 0.2581 | - | - | - | - | - | - | - | - |
| e10bft_decay_g095 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | acc_window1000_mean | 1 | 0.6704 | - | - | 0.7713 | ARF | -0.1009 | 0.7713 | ARF | -0.1009 |
| e10bft_density_b2 | acc_prequential | 1 | 0.6722 | - | - | 0.6982 | NB + SEED | -0.0260 | - | - | - |
| e10bft_density_b2 | kappa | 1 | 0.6067 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_density_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | acc_window1000_mean | 1 | 0.6751 | - | - | 0.7713 | ARF | -0.0962 | 0.7713 | ARF | -0.0962 |
| e10bft_density_b4 | acc_prequential | 1 | 0.6769 | - | - | 0.6982 | NB + SEED | -0.0213 | - | - | - |
| e10bft_density_b4 | kappa | 1 | 0.6123 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_density_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | acc_window1000_mean | 1 | 0.6751 | - | - | 0.7713 | ARF | -0.0962 | 0.7713 | ARF | -0.0962 |
| e10bft_density_b8 | acc_prequential | 1 | 0.6769 | - | - | 0.6982 | NB + SEED | -0.0213 | - | - | - |
| e10bft_density_b8 | kappa | 1 | 0.6123 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_density_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | acc_window1000_mean | 1 | 0.6636 | - | - | 0.7713 | ARF | -0.1077 | 0.7713 | ARF | -0.1077 |
| e10bft_entry_f15 | acc_prequential | 1 | 0.6655 | - | - | 0.6982 | NB + SEED | -0.0327 | - | - | - |
| e10bft_entry_f15 | kappa | 1 | 0.5985 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | n_alarms | 1 | 27.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | f1 | 1 | 0.2581 | - | - | - | - | - | - | - | - |
| e10bft_entry_f15 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | acc_window1000_mean | 1 | 0.6636 | - | - | 0.7713 | ARF | -0.1077 | 0.7713 | ARF | -0.1077 |
| e10bft_entry_f30 | acc_prequential | 1 | 0.6655 | - | - | 0.6982 | NB + SEED | -0.0327 | - | - | - |
| e10bft_entry_f30 | kappa | 1 | 0.5985 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | n_alarms | 1 | 27.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | f1 | 1 | 0.2581 | - | - | - | - | - | - | - | - |
| e10bft_entry_f30 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | acc_window1000_mean | 1 | 0.6736 | - | - | 0.7713 | ARF | -0.0977 | 0.7713 | ARF | -0.0977 |
| e10bft_entry_f5 | acc_prequential | 1 | 0.6754 | - | - | 0.6982 | NB + SEED | -0.0228 | - | - | - |
| e10bft_entry_f5 | kappa | 1 | 0.6105 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | n_alarms | 1 | 27.0000 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | f1 | 1 | 0.2581 | - | - | - | - | - | - | - | - |
| e10bft_entry_f5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | acc_window1000_mean | 1 | 0.6704 | - | - | 0.7713 | ARF | -0.1009 | 0.7713 | ARF | -0.1009 |
| e10bft_freq_b2 | acc_prequential | 1 | 0.6722 | - | - | 0.6982 | NB + SEED | -0.0260 | - | - | - |
| e10bft_freq_b2 | kappa | 1 | 0.6067 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_freq_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | acc_window1000_mean | 1 | 0.6751 | - | - | 0.7713 | ARF | -0.0962 | 0.7713 | ARF | -0.0962 |
| e10bft_freq_b4 | acc_prequential | 1 | 0.6769 | - | - | 0.6982 | NB + SEED | -0.0213 | - | - | - |
| e10bft_freq_b4 | kappa | 1 | 0.6123 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_freq_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | acc_window1000_mean | 1 | 0.6751 | - | - | 0.7713 | ARF | -0.0962 | 0.7713 | ARF | -0.0962 |
| e10bft_freq_b8 | acc_prequential | 1 | 0.6769 | - | - | 0.6982 | NB + SEED | -0.0213 | - | - | - |
| e10bft_freq_b8 | kappa | 1 | 0.6123 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_freq_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | acc_window1000_mean | 1 | 0.6763 | - | - | 0.7713 | ARF | -0.0950 | 0.7713 | ARF | -0.0950 |
| e10bft_rent_l1 | acc_prequential | 1 | 0.6781 | - | - | 0.6982 | NB + SEED | -0.0201 | - | - | - |
| e10bft_rent_l1 | kappa | 1 | 0.6137 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_rent_l1 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | acc_window1000_mean | 1 | 0.6684 | - | - | 0.7713 | ARF | -0.1029 | 0.7713 | ARF | -0.1029 |
| e10bft_rent_l10 | acc_prequential | 1 | 0.6703 | - | - | 0.6982 | NB + SEED | -0.0279 | - | - | - |
| e10bft_rent_l10 | kappa | 1 | 0.6043 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | n_alarms | 1 | 32.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | f1 | 1 | 0.2222 | - | - | - | - | - | - | - | - |
| e10bft_rent_l10 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | acc_window1000_mean | 1 | 0.6751 | - | - | 0.7713 | ARF | -0.0962 | 0.7713 | ARF | -0.0962 |
| e10bft_rent_l2 | acc_prequential | 1 | 0.6769 | - | - | 0.6982 | NB + SEED | -0.0213 | - | - | - |
| e10bft_rent_l2 | kappa | 1 | 0.6123 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_rent_l2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | acc_window1000_mean | 1 | 0.6756 | - | - | 0.7713 | ARF | -0.0957 | 0.7713 | ARF | -0.0957 |
| e10bft_rent_l5 | acc_prequential | 1 | 0.6775 | - | - | 0.6982 | NB + SEED | -0.0207 | - | - | - |
| e10bft_rent_l5 | kappa | 1 | 0.6130 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | n_alarms | 1 | 31.0000 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | f1 | 1 | 0.2286 | - | - | - | - | - | - | - | - |
| e10bft_rent_l5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | acc_window1000_mean | 1 | 0.6763 | - | - | 0.7713 | ARF | -0.0950 | 0.7713 | ARF | -0.0950 |
| e10bft_reuse_value | acc_prequential | 1 | 0.6781 | - | - | 0.6982 | NB + SEED | -0.0201 | - | - | - |
| e10bft_reuse_value | kappa | 1 | 0.6137 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_reuse_value | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| e10bft_subst | acc_window1000_mean | 1 | 0.6763 | - | - | 0.7713 | ARF | -0.0950 | 0.7713 | ARF | -0.0950 |
| e10bft_subst | acc_prequential | 1 | 0.6781 | - | - | 0.6982 | NB + SEED | -0.0201 | - | - | - |
| e10bft_subst | kappa | 1 | 0.6137 | - | - | - | - | - | - | - | - |
| e10bft_subst | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| e10bft_subst | f1 | 1 | 0.2667 | - | - | - | - | - | - | - | - |
| e10bft_subst | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | acc_window1000_mean | 1 | 0.6740 | - | - | 0.7713 | ARF | -0.0973 | 0.7713 | ARF | -0.0973 |
| ecpf_decay_g050 | acc_prequential | 1 | 0.6754 | - | - | 0.6982 | NB + SEED | -0.0228 | - | - | - |
| ecpf_decay_g050 | kappa | 1 | 0.6105 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | n_alarms | 1 | 36.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | f1 | 1 | 0.2000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g050 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | acc_window1000_mean | 1 | 0.6715 | - | - | 0.7713 | ARF | -0.0998 | 0.7713 | ARF | -0.0998 |
| ecpf_decay_g080 | acc_prequential | 1 | 0.6733 | - | - | 0.6982 | NB + SEED | -0.0249 | - | - | - |
| ecpf_decay_g080 | kappa | 1 | 0.6080 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_decay_g080 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_decay_g095 | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_decay_g095 | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_decay_g095 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | acc_window1000_mean | 1 | 0.6642 | - | - | 0.7713 | ARF | -0.1071 | 0.7713 | ARF | -0.1071 |
| ecpf_density_b2 | acc_prequential | 1 | 0.6661 | - | - | 0.6982 | NB + SEED | -0.0321 | - | - | - |
| ecpf_density_b2 | kappa | 1 | 0.5993 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | n_alarms | 1 | 38.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | f1 | 1 | 0.1905 | - | - | - | - | - | - | - | - |
| ecpf_density_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | acc_window1000_mean | 1 | 0.6696 | - | - | 0.7713 | ARF | -0.1017 | 0.7713 | ARF | -0.1017 |
| ecpf_density_b4 | acc_prequential | 1 | 0.6711 | - | - | 0.6982 | NB + SEED | -0.0271 | - | - | - |
| ecpf_density_b4 | kappa | 1 | 0.6053 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | n_alarms | 1 | 41.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | f1 | 1 | 0.2174 | - | - | - | - | - | - | - | - |
| ecpf_density_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_density_b8 | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_density_b8 | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_density_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | acc_window1000_mean | 1 | 0.6600 | - | - | 0.7713 | ARF | -0.1113 | 0.7713 | ARF | -0.1113 |
| ecpf_entry_f15 | acc_prequential | 1 | 0.6619 | - | - | 0.6982 | NB + SEED | -0.0363 | - | - | - |
| ecpf_entry_f15 | kappa | 1 | 0.5942 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | n_alarms | 1 | 32.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | f1 | 1 | 0.2222 | - | - | - | - | - | - | - | - |
| ecpf_entry_f15 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | acc_window1000_mean | 1 | 0.6600 | - | - | 0.7713 | ARF | -0.1113 | 0.7713 | ARF | -0.1113 |
| ecpf_entry_f30 | acc_prequential | 1 | 0.6619 | - | - | 0.6982 | NB + SEED | -0.0363 | - | - | - |
| ecpf_entry_f30 | kappa | 1 | 0.5942 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | n_alarms | 1 | 32.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | f1 | 1 | 0.2222 | - | - | - | - | - | - | - | - |
| ecpf_entry_f30 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_entry_f5 | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_entry_f5 | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_entry_f5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | acc_window1000_mean | 1 | 0.6642 | - | - | 0.7713 | ARF | -0.1071 | 0.7713 | ARF | -0.1071 |
| ecpf_freq_b2 | acc_prequential | 1 | 0.6661 | - | - | 0.6982 | NB + SEED | -0.0321 | - | - | - |
| ecpf_freq_b2 | kappa | 1 | 0.5993 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | n_alarms | 1 | 38.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | f1 | 1 | 0.1905 | - | - | - | - | - | - | - | - |
| ecpf_freq_b2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | acc_window1000_mean | 1 | 0.6697 | - | - | 0.7713 | ARF | -0.1016 | 0.7713 | ARF | -0.1016 |
| ecpf_freq_b4 | acc_prequential | 1 | 0.6712 | - | - | 0.6982 | NB + SEED | -0.0270 | - | - | - |
| ecpf_freq_b4 | kappa | 1 | 0.6054 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | n_alarms | 1 | 41.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | f1 | 1 | 0.2174 | - | - | - | - | - | - | - | - |
| ecpf_freq_b4 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_freq_b8 | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_freq_b8 | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_freq_b8 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_paper | acc_window1000_mean | 1 | 0.6760 | - | - | 0.7713 | ARF | -0.0953 | 0.7713 | ARF | -0.0953 |
| ecpf_paper | acc_prequential | 1 | 0.6779 | - | - | 0.6982 | NB + SEED | -0.0203 | - | - | - |
| ecpf_paper | kappa | 1 | 0.6135 | - | - | - | - | - | - | - | - |
| ecpf_paper | n_alarms | 1 | 46.0000 | - | - | - | - | - | - | - | - |
| ecpf_paper | f1 | 1 | 0.1961 | - | - | - | - | - | - | - | - |
| ecpf_paper | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_rent_l1 | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_rent_l1 | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_rent_l1 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | acc_window1000_mean | 1 | 0.6718 | - | - | 0.7713 | ARF | -0.0995 | 0.7713 | ARF | -0.0995 |
| ecpf_rent_l10 | acc_prequential | 1 | 0.6737 | - | - | 0.6982 | NB + SEED | -0.0245 | - | - | - |
| ecpf_rent_l10 | kappa | 1 | 0.6084 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | n_alarms | 1 | 38.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | f1 | 1 | 0.2326 | - | - | - | - | - | - | - | - |
| ecpf_rent_l10 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_rent_l2 | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_rent_l2 | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_rent_l2 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | acc_window1000_mean | 1 | 0.6681 | - | - | 0.7713 | ARF | -0.1032 | 0.7713 | ARF | -0.1032 |
| ecpf_rent_l5 | acc_prequential | 1 | 0.6696 | - | - | 0.6982 | NB + SEED | -0.0286 | - | - | - |
| ecpf_rent_l5 | kappa | 1 | 0.6035 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | n_alarms | 1 | 41.0000 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | f1 | 1 | 0.1778 | - | - | - | - | - | - | - | - |
| ecpf_rent_l5 | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_reuse_value | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_reuse_value | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| ecpf_subst | acc_window1000_mean | 1 | 0.6735 | - | - | 0.7713 | ARF | -0.0978 | 0.7713 | ARF | -0.0978 |
| ecpf_subst | acc_prequential | 1 | 0.6753 | - | - | 0.6982 | NB + SEED | -0.0229 | - | - | - |
| ecpf_subst | kappa | 1 | 0.6104 | - | - | - | - | - | - | - | - |
| ecpf_subst | n_alarms | 1 | 44.0000 | - | - | - | - | - | - | - | - |
| ecpf_subst | f1 | 1 | 0.2041 | - | - | - | - | - | - | - | - |
| ecpf_subst | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |

See insects_abrupt_balanced for the metric mapping.

### Ranking across datasets on `acc_prequential`

Blocks: 4; presets: 38. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| e10bft_rent_l2 | 7.88 | 0.7056 |
| e10bft_rent_l1 | 9.38 | 0.7050 |
| e10bft_reuse_value | 11.38 | 0.7047 |
| e10bft_decay_g050 | 12.25 | 0.7037 |
| e10bft_freq_b8 | 12.62 | 0.7045 |
| e10bft_subst | 13.12 | 0.7039 |
| e10bft_density_b4 | 13.62 | 0.7029 |
| e10bft_freq_b4 | 13.62 | 0.7029 |
| e10bft_decay_g095 | 14.75 | 0.7039 |
| e10bft_entry_f5 | 15.25 | 0.7033 |
| e10bft_density_b8 | 16.38 | 0.7036 |
| ecpf_rent_l2 | 16.62 | 0.7029 |
| e10bft_rent_l5 | 17.00 | 0.7020 |
| ecpf_reuse_value | 17.00 | 0.7029 |
| e10bft_rent_l10 | 17.62 | 0.7025 |
| e10bft_density_b2 | 18.50 | 0.7007 |
| ecpf_decay_g050 | 18.62 | 0.7021 |
| ecpf_density_b8 | 18.75 | 0.7026 |
| ecpf_freq_b8 | 18.75 | 0.7026 |
| ecpf_rent_l10 | 18.88 | 0.7031 |
| ecpf_subst | 19.38 | 0.7027 |
| e10bft | 20.75 | 0.7023 |
| ecpf_decay_g095 | 21.38 | 0.7021 |
| e10bft_freq_b2 | 22.00 | 0.6992 |
| ecpf_entry_f5 | 22.12 | 0.7018 |
| ecpf_density_b2 | 22.12 | 0.6994 |
| e10bft_decay_g080 | 22.62 | 0.7009 |
| ecpf_paper | 22.88 | 0.6990 |
| ecpf_freq_b4 | 23.00 | 0.7014 |
| ecpf_freq_b2 | 23.88 | 0.7003 |
| ecpf_decay_g080 | 24.88 | 0.7012 |
| ecpf_rent_l1 | 25.12 | 0.7002 |
| ecpf_density_b4 | 25.25 | 0.7010 |
| ecpf_rent_l5 | 25.62 | 0.6989 |
| ecpf_entry_f15 | 28.50 | 0.6955 |
| ecpf_entry_f30 | 28.50 | 0.6955 |
| e10bft_entry_f30 | 30.50 | 0.6960 |
| e10bft_entry_f15 | 30.50 | 0.6960 |

Friedman chi2 = 40.458, p = 0.3202.
Caution: only 4 blocks; Friedman / Nemenyi have little power below about 10.

Wilcoxon signed-rank, e10bft vs others (two-sided, Holm-corrected):

| other | mean diff | W | p | p (Holm) |
|---|---|---|---|---|
| e10bft_decay_g050 | -0.0014 | 4.0 | 0.875 | 1 |
| e10bft_decay_g080 | +0.0014 | 3.0 | 0.625 | 1 |
| e10bft_decay_g095 | -0.0016 | 2.0 | 0.375 | 1 |
| e10bft_density_b2 | +0.0016 | 3.0 | 0.625 | 1 |
| e10bft_density_b4 | -0.0006 | 4.0 | 0.875 | 1 |
| e10bft_density_b8 | -0.0013 | 3.0 | 0.625 | 1 |
| e10bft_entry_f15 | +0.0063 | 1.0 | 0.25 | 1 |
| e10bft_entry_f30 | +0.0063 | 1.0 | 0.25 | 1 |
| e10bft_entry_f5 | -0.0010 | 2.0 | 0.375 | 1 |
| e10bft_freq_b2 | +0.0031 | 3.0 | 0.625 | 1 |
| e10bft_freq_b4 | -0.0006 | 4.0 | 0.875 | 1 |
| e10bft_freq_b8 | -0.0022 | 1.0 | 0.25 | 1 |
| e10bft_rent_l1 | -0.0027 | 1.0 | 0.25 | 1 |
| e10bft_rent_l10 | -0.0002 | 5.0 | 1 | 1 |
| e10bft_rent_l2 | -0.0033 | 1.0 | 0.25 | 1 |
| e10bft_rent_l5 | +0.0003 | 4.0 | 0.875 | 1 |
| e10bft_reuse_value | -0.0024 | 1.0 | 0.25 | 1 |
| e10bft_subst | -0.0016 | 2.0 | 0.375 | 1 |
| ecpf_decay_g050 | +0.0002 | 5.0 | 1 | 1 |
| ecpf_decay_g080 | +0.0010 | 5.0 | 1 | 1 |
| ecpf_decay_g095 | +0.0002 | 4.0 | 0.875 | 1 |
| ecpf_density_b2 | +0.0029 | 3.0 | 0.625 | 1 |
| ecpf_density_b4 | +0.0013 | 4.0 | 0.875 | 1 |
| ecpf_density_b8 | -0.0003 | 4.0 | 0.875 | 1 |
| ecpf_entry_f15 | +0.0068 | 1.0 | 0.25 | 1 |
| ecpf_entry_f30 | +0.0068 | 1.0 | 0.25 | 1 |
| ecpf_entry_f5 | +0.0005 | 5.0 | 1 | 1 |
| ecpf_freq_b2 | +0.0019 | 3.0 | 0.625 | 1 |
| ecpf_freq_b4 | +0.0009 | 5.0 | 1 | 1 |
| ecpf_freq_b8 | -0.0003 | 4.0 | 0.875 | 1 |
| ecpf_paper | +0.0033 | 4.0 | 0.875 | 1 |
| ecpf_rent_l1 | +0.0020 | 3.0 | 0.625 | 1 |
| ecpf_rent_l10 | -0.0008 | 5.0 | 1 | 1 |
| ecpf_rent_l2 | -0.0006 | 4.0 | 0.875 | 1 |
| ecpf_rent_l5 | +0.0034 | 2.0 | 0.375 | 1 |
| ecpf_reuse_value | -0.0006 | 4.0 | 0.875 | 1 |
| ecpf_subst | -0.0004 | 4.0 | 0.875 | 1 |

### Ranking across datasets on `acc_window1000_mean`

Blocks: 3; presets: 38. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| e10bft_reuse_value | 7.50 | 0.6606 |
| e10bft_rent_l1 | 7.50 | 0.6606 |
| e10bft_rent_l2 | 8.50 | 0.6603 |
| e10bft_density_b8 | 9.50 | 0.6602 |
| e10bft_freq_b8 | 9.50 | 0.6602 |
| e10bft_subst | 10.50 | 0.6592 |
| e10bft_decay_g095 | 11.00 | 0.6597 |
| e10bft_decay_g050 | 12.33 | 0.6584 |
| e10bft_rent_l5 | 14.00 | 0.6572 |
| e10bft_entry_f5 | 14.33 | 0.6583 |
| e10bft_density_b4 | 15.00 | 0.6570 |
| e10bft_freq_b4 | 15.00 | 0.6570 |
| e10bft | 15.67 | 0.6581 |
| ecpf_rent_l2 | 16.83 | 0.6579 |
| ecpf_reuse_value | 16.83 | 0.6579 |
| ecpf_freq_b8 | 16.83 | 0.6579 |
| ecpf_entry_f5 | 16.83 | 0.6579 |
| ecpf_decay_g095 | 16.83 | 0.6579 |
| ecpf_density_b8 | 16.83 | 0.6579 |
| e10bft_decay_g080 | 18.83 | 0.6561 |
| e10bft_rent_l10 | 19.17 | 0.6570 |
| ecpf_subst | 20.00 | 0.6576 |
| ecpf_paper | 20.33 | 0.6535 |
| e10bft_density_b2 | 23.00 | 0.6534 |
| ecpf_rent_l1 | 23.33 | 0.6551 |
| ecpf_decay_g080 | 23.50 | 0.6564 |
| ecpf_decay_g050 | 23.50 | 0.6546 |
| ecpf_freq_b4 | 24.00 | 0.6561 |
| ecpf_density_b4 | 24.33 | 0.6561 |
| e10bft_freq_b2 | 24.67 | 0.6527 |
| ecpf_rent_l10 | 24.83 | 0.6546 |
| ecpf_density_b2 | 27.17 | 0.6521 |
| ecpf_freq_b2 | 29.17 | 0.6536 |
| e10bft_entry_f30 | 29.83 | 0.6494 |
| e10bft_entry_f15 | 29.83 | 0.6494 |
| ecpf_rent_l5 | 30.50 | 0.6521 |
| ecpf_entry_f30 | 36.83 | 0.6463 |
| ecpf_entry_f15 | 36.83 | 0.6463 |

Friedman chi2 = 56.530, p = 0.02087.
Caution: only 3 blocks; Friedman / Nemenyi have little power below about 10.

Wilcoxon signed-rank, e10bft vs others (two-sided, Holm-corrected):

| other | mean diff | W | p | p (Holm) |
|---|---|---|---|---|
| e10bft_decay_g050 | -0.0003 | 3.0 | 1 | 1 |
| e10bft_decay_g080 | +0.0020 | 1.0 | 0.5 | 1 |
| e10bft_decay_g095 | -0.0016 | 1.0 | 0.5 | 1 |
| e10bft_density_b2 | +0.0047 | 0.0 | 0.25 | 1 |
| e10bft_density_b4 | +0.0011 | 2.0 | 0.75 | 1 |
| e10bft_density_b8 | -0.0021 | 1.0 | 0.5 | 1 |
| e10bft_entry_f15 | +0.0087 | 0.0 | 0.25 | 1 |
| e10bft_entry_f30 | +0.0087 | 0.0 | 0.25 | 1 |
| e10bft_entry_f5 | -0.0002 | 2.0 | 0.75 | 1 |
| e10bft_freq_b2 | +0.0054 | 0.0 | 0.25 | 1 |
| e10bft_freq_b4 | +0.0011 | 2.0 | 0.75 | 1 |
| e10bft_freq_b8 | -0.0021 | 1.0 | 0.5 | 1 |
| e10bft_rent_l1 | -0.0025 | 1.0 | 0.5 | 1 |
| e10bft_rent_l10 | +0.0011 | 1.0 | 0.5 | 1 |
| e10bft_rent_l2 | -0.0021 | 1.0 | 0.5 | 1 |
| e10bft_rent_l5 | +0.0009 | 2.0 | 0.75 | 1 |
| e10bft_reuse_value | -0.0025 | 1.0 | 0.5 | 1 |
| e10bft_subst | -0.0011 | 2.0 | 0.75 | 1 |
| ecpf_decay_g050 | +0.0035 | 1.0 | 0.5 | 1 |
| ecpf_decay_g080 | +0.0017 | 2.0 | 0.75 | 1 |
| ecpf_decay_g095 | +0.0003 | 3.0 | 1 | 1 |
| ecpf_density_b2 | +0.0060 | 0.0 | 0.25 | 1 |
| ecpf_density_b4 | +0.0021 | 2.0 | 0.75 | 1 |
| ecpf_density_b8 | +0.0003 | 3.0 | 1 | 1 |
| ecpf_entry_f15 | +0.0118 | 0.0 | 0.25 | 1 |
| ecpf_entry_f30 | +0.0118 | 0.0 | 0.25 | 1 |
| ecpf_entry_f5 | +0.0003 | 3.0 | 1 | 1 |
| ecpf_freq_b2 | +0.0045 | 1.0 | 0.5 | 1 |
| ecpf_freq_b4 | +0.0020 | 2.0 | 0.75 | 1 |
| ecpf_freq_b8 | +0.0003 | 3.0 | 1 | 1 |
| ecpf_paper | +0.0046 | 2.0 | 0.75 | 1 |
| ecpf_rent_l1 | +0.0030 | 1.0 | 0.5 | 1 |
| ecpf_rent_l10 | +0.0035 | 1.0 | 0.5 | 1 |
| ecpf_rent_l2 | +0.0003 | 3.0 | 1 | 1 |
| ecpf_rent_l5 | +0.0060 | 0.0 | 0.25 | 1 |
| ecpf_reuse_value | +0.0003 | 3.0 | 1 | 1 |
| ecpf_subst | +0.0005 | 3.0 | 1 | 1 |

### Ranking across datasets on `kappa_t`

_Not enough complete blocks for rank tests (1 blocks x 38 presets with every preset present)._

## Cost (time and memory)

Mean per run. `runtime_s` is wall time, `cpu_time_s` process CPU time (both exclude data loading); `rss_increment_mb` is the peak resident memory of the run's own process minus its level before the system was built, `ram_hours_gb` that increment integrated over the run (GB x hours), `model_size_final_mb` the system's Python object size after the last instance. `concurrent_runs` is the most runs that executed at the same time as a run. Memory is per process and valid at any concurrency; times are strict only where `concurrent_runs` is 1 (`--workers 1`) and comparable only between rows with the same machine and the same `concurrent_runs` (CPU time is less affected by parallel load than wall time).

| dataset | preset | n | runtime_s | runtime_std | cpu_time_s | instances_per_s | rss_increment_mb | rss_increment_max_mb | model_size_final_mb | ram_hours_gb | concurrent_runs | machine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| electricity | e10bft | 1 | 27.3600 | - | 27.2390 | 1656.4000 | 10.9000 | 10.9000 | 10.7500 | 2.20e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_decay_g050 | 1 | 24.0500 | - | 24.1760 | 1884.2000 | 22.0000 | 22.0000 | 6.1300 | 9.60e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_decay_g080 | 1 | 25.3500 | - | 25.4640 | 1787.5000 | 23.6000 | 23.6000 | 5.8500 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_decay_g095 | 1 | 25.8900 | - | 26.0220 | 1750.5000 | 24.4000 | 24.4000 | 6.7200 | 8.92e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_density_b2 | 1 | 24.9500 | - | 25.0500 | 1816.4000 | 19.7000 | 19.7000 | 5.2600 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_density_b4 | 1 | 25.8200 | - | 25.9410 | 1755.0000 | 20.8000 | 20.8000 | 6.7400 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_density_b8 | 1 | 28.3600 | - | 28.4820 | 1597.5000 | 21.3000 | 21.3000 | 7.3900 | 7.47e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_entry_f15 | 1 | 25.8000 | - | 25.9900 | 1756.4000 | 14.7000 | 14.7000 | 4.6700 | 8.65e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_entry_f30 | 1 | 26.2700 | - | 26.1810 | 1724.9000 | 16.4000 | 16.4000 | 4.6700 | 6.16e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_entry_f5 | 1 | 27.4200 | - | 27.5080 | 1652.7000 | 24.3000 | 24.3000 | 7.5900 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_freq_b2 | 1 | 25.3300 | - | 25.4620 | 1788.6000 | 23.1000 | 23.1000 | 5.9400 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_freq_b4 | 1 | 27.3000 | - | 26.5470 | 1659.8000 | 21.4000 | 21.4000 | 6.7400 | 6.80e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_freq_b8 | 1 | 27.0900 | - | 27.1490 | 1672.9000 | 26.6000 | 26.6000 | 8.4300 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_rent_l1 | 1 | 26.5700 | - | 26.6450 | 1705.7000 | 20.1000 | 20.1000 | 10.1700 | 8.17e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_rent_l10 | 1 | 24.8800 | - | 25.0380 | 1821.5000 | 23.3000 | 23.3000 | 5.9600 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_rent_l2 | 1 | 26.5200 | - | 26.5930 | 1708.7000 | 10.6000 | 10.6000 | 8.3700 | 1.92e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_rent_l5 | 1 | 25.8100 | - | 25.9670 | 1755.4000 | 24.1000 | 24.1000 | 7.7600 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_reuse_value | 1 | 27.5800 | - | 27.6880 | 1642.7000 | 20.9000 | 20.9000 | 10.6200 | 8.29e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | e10bft_subst | 1 | 33.2700 | - | 33.3750 | 1361.8000 | 13.4000 | 13.4000 | 10.1000 | 1.25e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_decay_g050 | 1 | 19.0300 | - | 19.2980 | 2381.6000 | 23.9000 | 23.9000 | 4.8700 | 7.11e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_decay_g080 | 1 | 19.1700 | - | 19.3530 | 2363.8000 | 27.6000 | 27.6000 | 6.4100 | 8.35e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_decay_g095 | 1 | 17.9500 | - | 18.0910 | 2523.9000 | 16.8000 | 16.8000 | 5.0900 | 4.34e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_density_b2 | 1 | 18.8000 | - | 19.0260 | 2410.2000 | 25.2000 | 25.2000 | 4.2600 | 9.88e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_density_b4 | 1 | 18.3300 | - | 18.5360 | 2472.0000 | 22.4000 | 22.4000 | 5.6000 | 6.04e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_density_b8 | 1 | 18.4300 | - | 18.5980 | 2459.2000 | 18.8000 | 18.8000 | 6.9500 | 4.61e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_entry_f15 | 1 | 19.2300 | - | 19.3460 | 2356.9000 | 18.9000 | 18.9000 | 3.7000 | 6.45e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_entry_f30 | 1 | 19.3200 | - | 19.6660 | 2345.0000 | 25.0000 | 25.0000 | 3.7000 | 9.50e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_entry_f5 | 1 | 18.7700 | - | 18.9180 | 2414.6000 | 20.0000 | 20.0000 | 6.8000 | 4.66e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_freq_b2 | 1 | 19.0100 | - | 19.2990 | 2383.2000 | 25.6000 | 25.6000 | 4.0500 | 9.93e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_freq_b4 | 1 | 18.4500 | - | 18.6260 | 2455.4000 | 24.8000 | 24.8000 | 4.8300 | 6.55e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_freq_b8 | 1 | 18.4300 | - | 18.6270 | 2459.0000 | 18.7000 | 18.7000 | 6.9500 | 4.54e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_paper | 1 | 19.5100 | - | 19.3840 | 2322.0000 | 13.9000 | 13.9000 | 11.3900 | 2.31e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_rent_l1 | 1 | 19.3400 | - | 19.5260 | 2343.4000 | 14.1000 | 14.1000 | 7.0000 | 4.07e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_rent_l10 | 1 | 19.1800 | - | 19.3700 | 2361.9000 | 28.2000 | 28.2000 | 6.1000 | 9.45e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_rent_l2 | 1 | 17.4400 | - | 17.5600 | 2597.6000 | 20.4000 | 20.4000 | 5.9800 | 4.47e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_rent_l5 | 1 | 19.5200 | - | 19.7590 | 2321.2000 | 27.1000 | 27.1000 | 6.4500 | 8.00e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_reuse_value | 1 | 18.3600 | - | 18.4610 | 2468.5000 | 14.1000 | 14.1000 | 5.9500 | 4.14e-05 | 1 | Apple M5 / 24.0 GB |
| electricity | ecpf_subst | 1 | 20.9000 | - | 21.0900 | 2168.0000 | 17.4000 | 17.4000 | 6.9600 | 5.81e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft | 1 | 77.9900 | - | 78.6130 | 677.6000 | 38.1000 | 38.1000 | 41.7400 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_decay_g050 | 1 | 77.8300 | - | 78.0580 | 679.0000 | 18.8000 | 18.8000 | 13.1400 | 4.21e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_decay_g080 | 1 | 77.6000 | - | 78.1800 | 681.0000 | 37.8000 | 37.8000 | 14.7900 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_decay_g095 | 1 | 76.9700 | - | 77.5660 | 686.6000 | 39.3000 | 39.3000 | 14.7900 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_density_b2 | 1 | 76.7400 | - | 77.3870 | 688.7000 | 53.1000 | 53.1000 | 14.7900 | 0.0006 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_density_b4 | 1 | 77.4200 | - | 77.4460 | 682.6000 | 3.8000 | 3.8000 | 14.7900 | 5.85e-07 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_density_b8 | 1 | 77.6200 | - | 78.2110 | 680.8000 | 38.4000 | 38.4000 | 14.7900 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_entry_f15 | 1 | 82.8500 | - | 83.4950 | 637.9000 | 79.5000 | 79.5000 | 13.5900 | 0.0009 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_entry_f30 | 1 | 85.1700 | - | 83.5460 | 620.5000 | 63.3000 | 63.3000 | 13.5900 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_entry_f5 | 1 | 77.7700 | - | 78.1980 | 679.5000 | 28.1000 | 28.1000 | 13.1400 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_freq_b2 | 1 | 81.6700 | - | 82.0510 | 647.1000 | 26.6000 | 26.6000 | 14.7900 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_freq_b4 | 1 | 78.6400 | - | 79.1530 | 672.0000 | 28.0000 | 28.0000 | 14.7900 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_freq_b8 | 1 | 76.1100 | - | 76.5210 | 694.3000 | 22.8000 | 22.8000 | 14.7900 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_rent_l1 | 1 | 77.0500 | - | 77.5880 | 685.9000 | 48.5000 | 48.5000 | 14.7900 | 0.0006 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_rent_l10 | 1 | 77.3000 | - | 78.0160 | 683.6000 | 39.7000 | 39.7000 | 13.1400 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_rent_l2 | 1 | 77.5900 | - | 78.1370 | 681.1000 | 43.3000 | 43.3000 | 14.7900 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_rent_l5 | 1 | 77.4100 | - | 77.8980 | 682.7000 | 31.3000 | 31.3000 | 13.1400 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_reuse_value | 1 | 76.8900 | - | 77.5270 | 687.3000 | 37.7000 | 37.7000 | 14.7900 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | e10bft_subst | 1 | 79.4800 | - | 80.1270 | 664.9000 | 39.4000 | 39.4000 | 14.7900 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_decay_g050 | 1 | 92.3500 | - | 92.2040 | 572.3000 | 8.5000 | 8.5000 | 11.7000 | 1.70e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_decay_g080 | 1 | 90.9500 | - | 90.6280 | 581.1000 | 21.4000 | 21.4000 | 11.7000 | 3.64e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_decay_g095 | 1 | 90.5600 | - | 90.4170 | 583.6000 | 4.0000 | 4.0000 | 11.7000 | 6.66e-07 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_density_b2 | 1 | 92.7300 | - | 93.1180 | 569.9000 | 61.6000 | 61.6000 | 11.7000 | 0.0007 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_density_b4 | 1 | 91.3900 | - | 90.9110 | 578.3000 | 2.3000 | 2.3000 | 11.7000 | 2.87e-07 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_density_b8 | 1 | 87.9500 | - | 88.3420 | 600.9000 | 20.5000 | 20.5000 | 25.7700 | 4.18e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_entry_f15 | 1 | 106.4600 | - | 107.2870 | 496.4000 | 42.1000 | 42.1000 | 10.2600 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_entry_f30 | 1 | 109.6600 | - | 108.4250 | 481.9000 | 7.1000 | 7.1000 | 10.2600 | 1.26e-06 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_entry_f5 | 1 | 89.7400 | - | 90.3830 | 588.9000 | 33.9000 | 33.9000 | 11.7000 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_freq_b2 | 1 | 96.4900 | - | 94.5250 | 547.7000 | 4.4000 | 4.4000 | 11.8100 | 6.22e-07 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_freq_b4 | 1 | 89.6900 | - | 90.4100 | 589.2000 | 38.5000 | 38.5000 | 11.7000 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_freq_b8 | 1 | 97.5800 | - | 98.0400 | 541.6000 | 18.7000 | 18.7000 | 25.7700 | 4.95e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_paper | 1 | 77.5300 | - | 76.8240 | 681.6000 | 2.7000 | 2.7000 | 45.1800 | 1.15e-06 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_rent_l1 | 1 | 88.6400 | - | 89.1650 | 596.2000 | 20.5000 | 20.5000 | 25.7700 | 4.10e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_rent_l10 | 1 | 92.1900 | - | 92.9790 | 573.2000 | 43.3000 | 43.3000 | 11.7000 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_rent_l2 | 1 | 90.0900 | - | 90.7350 | 586.6000 | 18.6000 | 18.6000 | 11.7000 | 4.31e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_rent_l5 | 1 | 88.2800 | - | 88.9620 | 598.7000 | 32.1000 | 32.1000 | 11.7000 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_reuse_value | 1 | 89.9300 | - | 90.5150 | 587.7000 | 9.7000 | 9.7000 | 25.7700 | 5.16e-05 | 1 | Apple M5 / 24.0 GB |
| insects_abrupt_balanced | ecpf_subst | 1 | 95.6200 | - | 96.1870 | 552.7000 | 7.6000 | 7.6000 | 25.7800 | 3.84e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft | 1 | 132.0500 | - | 131.9810 | 605.7000 | 17.2000 | 17.2000 | 41.3200 | 6.56e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_decay_g050 | 1 | 120.5000 | - | 121.5470 | 663.8000 | 105.4000 | 105.4000 | 18.4500 | 0.0019 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_decay_g080 | 1 | 118.5900 | - | 119.4200 | 674.4000 | 99.2000 | 99.2000 | 24.2100 | 0.0017 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_decay_g095 | 1 | 122.9800 | - | 123.8600 | 650.4000 | 99.0000 | 99.0000 | 21.9800 | 0.0024 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_density_b2 | 1 | 119.2500 | - | 119.5860 | 670.8000 | 43.6000 | 43.6000 | 14.1500 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_density_b4 | 1 | 119.6100 | - | 120.4630 | 668.7000 | 81.3000 | 81.3000 | 18.4500 | 0.0015 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_density_b8 | 1 | 122.8700 | - | 123.8910 | 651.0000 | 72.2000 | 72.2000 | 21.9800 | 0.0015 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_entry_f15 | 1 | 119.8300 | - | 120.9370 | 667.5000 | 94.2000 | 94.2000 | 14.1600 | 0.0018 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_entry_f30 | 1 | 118.6900 | - | 119.7100 | 673.9000 | 95.6000 | 95.6000 | 14.1600 | 0.0018 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_entry_f5 | 1 | 125.3100 | - | 126.1420 | 638.3000 | 99.7000 | 99.7000 | 28.6400 | 0.0018 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_freq_b2 | 1 | 122.7900 | - | 123.8790 | 651.4000 | 99.0000 | 99.0000 | 17.4700 | 0.0019 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_freq_b4 | 1 | 119.5300 | - | 120.4170 | 669.1000 | 107.0000 | 107.0000 | 18.4500 | 0.0019 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_freq_b8 | 1 | 122.2400 | - | 123.2960 | 654.3000 | 76.9000 | 76.9000 | 21.9800 | 0.0016 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_rent_l1 | 1 | 122.5500 | - | 123.6270 | 652.7000 | 69.0000 | 69.0000 | 21.9800 | 0.0015 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_rent_l10 | 1 | 123.5100 | - | 123.9630 | 647.6000 | 44.8000 | 44.8000 | 19.3700 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_rent_l2 | 1 | 124.8600 | - | 125.5670 | 640.6000 | 41.6000 | 41.6000 | 27.7000 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_rent_l5 | 1 | 119.4000 | - | 120.2730 | 669.9000 | 104.1000 | 104.1000 | 18.4500 | 0.0019 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_reuse_value | 1 | 122.7200 | - | 123.4540 | 651.8000 | 34.6000 | 34.6000 | 21.9800 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | e10bft_subst | 1 | 138.2900 | - | 136.3130 | 578.4000 | 59.8000 | 59.8000 | 28.8000 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_decay_g050 | 1 | 160.7400 | - | 161.6110 | 497.6000 | 123.0000 | 123.0000 | 17.0300 | 0.0031 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_decay_g080 | 1 | 116.5400 | - | 117.3920 | 686.3000 | 48.4000 | 48.4000 | 17.2600 | 0.0008 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_decay_g095 | 1 | 145.8200 | - | 146.9320 | 548.5000 | 37.0000 | 37.0000 | 33.8300 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_density_b2 | 1 | 156.1000 | - | 157.1580 | 512.4000 | 36.3000 | 36.3000 | 12.8200 | 0.0006 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_density_b4 | 1 | 115.7400 | - | 116.5670 | 691.1000 | 95.0000 | 95.0000 | 17.0300 | 0.0013 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_density_b8 | 1 | 153.8800 | - | 154.0510 | 519.8000 | 22.8000 | 22.8000 | 21.5100 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_entry_f15 | 1 | 126.9900 | - | 127.3420 | 629.8000 | 99.2000 | 99.2000 | 12.2800 | 0.0020 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_entry_f30 | 1 | 127.0500 | - | 127.8880 | 629.5000 | 65.9000 | 65.9000 | 12.2800 | 0.0009 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_entry_f5 | 1 | 147.9000 | - | 148.3030 | 540.8000 | 12.0000 | 12.0000 | 33.8300 | 3.14e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_freq_b2 | 1 | 129.3200 | - | 130.0300 | 618.5000 | 26.8000 | 26.8000 | 13.8400 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_freq_b4 | 1 | 113.8800 | - | 114.6330 | 702.4000 | 59.5000 | 59.5000 | 17.0300 | 0.0009 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_freq_b8 | 1 | 146.2100 | - | 146.6980 | 547.1000 | 52.1000 | 52.1000 | 21.5100 | 0.0006 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_paper | 1 | 141.1000 | - | 141.9510 | 566.9000 | 15.9000 | 15.9000 | 44.7100 | 7.06e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_rent_l1 | 1 | 121.8100 | - | 121.4180 | 656.6000 | 10.3000 | 10.3000 | 37.3800 | 9.62e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_rent_l10 | 1 | 135.8200 | - | 136.8860 | 588.9000 | 47.0000 | 47.0000 | 17.1200 | 0.0007 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_rent_l2 | 1 | 148.1900 | - | 148.1600 | 539.8000 | 7.8000 | 7.8000 | 29.6500 | 1.06e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_rent_l5 | 1 | 133.5800 | - | 134.2420 | 598.8000 | 57.1000 | 57.1000 | 22.2400 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_reuse_value | 1 | 144.8000 | - | 145.9870 | 552.4000 | 21.9000 | 21.9000 | 38.1100 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | ecpf_subst | 1 | 125.5000 | - | 126.4320 | 637.3000 | 76.6000 | 76.6000 | 17.5200 | 0.0011 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft | 1 | 68.9000 | - | 68.5840 | 1160.9000 | 17.0000 | 17.0000 | 39.0900 | 9.84e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_decay_g050 | 1 | 74.9700 | - | 75.0560 | 1066.9000 | 46.5000 | 46.5000 | 15.7800 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_decay_g080 | 1 | 74.3100 | - | 74.1760 | 1076.3000 | 6.7000 | 6.7000 | 25.6200 | 2.44e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_decay_g095 | 1 | 78.6500 | - | 78.2780 | 1017.0000 | 9.1000 | 9.1000 | 20.0500 | 7.60e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_density_b2 | 1 | 76.3100 | - | 76.0350 | 1048.1000 | 18.6000 | 18.6000 | 15.6500 | 3.17e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_density_b4 | 1 | 72.8600 | - | 72.7920 | 1097.8000 | 17.0000 | 17.0000 | 18.5200 | 6.01e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_density_b8 | 1 | 71.0500 | - | 71.2530 | 1125.7000 | 19.7000 | 19.7000 | 24.3200 | 7.50e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_entry_f15 | 1 | 75.3300 | - | 74.9960 | 1061.8000 | 12.5000 | 12.5000 | 14.1600 | 2.03e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_entry_f30 | 1 | 73.1100 | - | 72.9900 | 1094.1000 | 31.6000 | 31.6000 | 14.1600 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_entry_f5 | 1 | 74.2300 | - | 74.0130 | 1077.5000 | 17.2000 | 17.2000 | 20.0500 | 1.01e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_freq_b2 | 1 | 72.9300 | - | 73.0830 | 1096.7000 | 29.7000 | 29.7000 | 15.6500 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_freq_b4 | 1 | 72.0400 | - | 72.5140 | 1110.2000 | 63.6000 | 63.6000 | 18.5200 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_freq_b8 | 1 | 71.8300 | - | 71.9570 | 1113.6000 | 14.9000 | 14.9000 | 24.3200 | 3.23e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_rent_l1 | 1 | 69.1000 | - | 69.1000 | 1157.5000 | 9.2000 | 9.2000 | 32.5700 | 1.72e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_rent_l10 | 1 | 69.1600 | - | 69.1900 | 1156.5000 | 18.8000 | 18.8000 | 15.7800 | 4.56e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_rent_l2 | 1 | 69.5100 | - | 70.0080 | 1150.7000 | 59.6000 | 59.6000 | 24.3200 | 0.0005 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_rent_l5 | 1 | 70.8800 | - | 70.7160 | 1128.4000 | 15.2000 | 15.2000 | 19.5500 | 2.37e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_reuse_value | 1 | 73.7600 | - | 73.6400 | 1084.4000 | 6.8000 | 6.8000 | 28.5000 | 3.24e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | e10bft_subst | 1 | 83.2800 | - | 82.9770 | 960.5000 | 22.8000 | 22.8000 | 28.5100 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_decay_g050 | 1 | 85.7500 | - | 86.5590 | 932.7000 | 52.7000 | 52.7000 | 22.1400 | 0.0004 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_decay_g080 | 1 | 79.0100 | - | 79.6250 | 1012.4000 | 28.6000 | 28.6000 | 26.4400 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_decay_g095 | 1 | 76.6900 | - | 77.3750 | 1043.0000 | 34.0000 | 34.0000 | 30.7000 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_density_b2 | 1 | 88.9100 | - | 89.2550 | 899.6000 | 35.2000 | 35.2000 | 13.1700 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_density_b4 | 1 | 85.5800 | - | 86.2600 | 934.6000 | 32.1000 | 32.1000 | 13.5800 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_density_b8 | 1 | 83.4300 | - | 83.5440 | 958.7000 | 15.9000 | 15.9000 | 30.7000 | 3.44e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_entry_f15 | 1 | 85.6800 | - | 86.4450 | 933.5000 | 45.1000 | 45.1000 | 11.0500 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_entry_f30 | 1 | 86.6000 | - | 87.1220 | 923.7000 | 14.9000 | 14.9000 | 11.0500 | 7.92e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_entry_f5 | 1 | 75.9900 | - | 76.4690 | 1052.6000 | 51.4000 | 51.4000 | 30.7000 | 0.0003 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_freq_b2 | 1 | 83.0600 | - | 83.5050 | 963.0000 | 14.8000 | 14.8000 | 13.1700 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_freq_b4 | 1 | 79.8300 | - | 80.6910 | 1001.9000 | 88.8000 | 88.8000 | 13.5700 | 0.0008 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_freq_b8 | 1 | 74.7200 | - | 75.2450 | 1070.5000 | 36.2000 | 36.2000 | 30.7000 | 0.0002 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_paper | 1 | 74.2000 | - | 73.6700 | 1077.9000 | 9.5000 | 9.5000 | 42.3400 | 9.72e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_rent_l1 | 1 | 95.4400 | - | 94.5170 | 838.1000 | 10.9000 | 10.9000 | 30.7000 | 2.70e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_rent_l10 | 1 | 71.9900 | - | 71.8920 | 1111.0000 | 13.8000 | 13.8000 | 13.1700 | 4.29e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_rent_l2 | 1 | 92.1600 | - | 91.5360 | 867.9000 | 11.7000 | 11.7000 | 30.7000 | 3.17e-06 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_rent_l5 | 1 | 124.3700 | - | 124.3560 | 643.1000 | 24.7000 | 24.7000 | 17.8600 | 0.0001 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_reuse_value | 1 | 80.1500 | - | 80.2850 | 998.0000 | 22.4000 | 22.4000 | 30.7000 | 8.23e-05 | 1 | Apple M5 / 24.0 GB |
| insects_incremental_reoccurring_balanced | ecpf_subst | 1 | 82.6300 | - | 83.3140 | 968.0000 | 37.9000 | 37.9000 | 30.7000 | 0.0002 | 1 | Apple M5 / 24.0 GB |

