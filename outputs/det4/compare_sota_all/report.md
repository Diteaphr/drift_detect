# dataset_0921 vs literature (2026-10-22 05:28)

Runs used: 29431 of 29431 (smoke runs excluded).

**Exploratory: includes non-comparable runs. Do not claim SOTA from this report.**
Registry: `configs/datasets_0921.json`. Metrics: `src/metrics/evaluate_run.py`.

## Prequential datasets

Difference = our mean - best literature value for that metric. 95% CI is a t-interval over seeds.

### ai4i2020 (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | macro_f1 | 1 | 0.5976 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | kappa | 1 | 0.2014 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | acc_prequential | 1 | 0.9666 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | macro_f1 | 1 | 0.6109 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | kappa | 1 | 0.2222 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.9550 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | macro_f1 | 1 | 0.5304 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | kappa | 1 | 0.0718 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.9649 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | macro_f1 | 1 | 0.5776 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | kappa | 1 | 0.1630 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.9664 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | macro_f1 | 1 | 0.5638 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | kappa | 1 | 0.1352 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 1 | 0.9648 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | macro_f1 | 1 | 0.5776 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | kappa | 1 | 0.1630 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.9664 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | macro_f1 | 1 | 0.6169 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 1 | 0.2380 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.9660 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | macro_f1 | 1 | 0.6322 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | kappa | 1 | 0.2682 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.9668 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | macro_f1 | 1 | 0.5699 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | kappa | 1 | 0.1476 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 1 | 0.9657 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | macro_f1 | 1 | 0.5960 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | kappa | 1 | 0.1978 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 1 | 0.9660 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | macro_f1 | 1 | 0.6175 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | kappa | 1 | 0.2393 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.9662 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | macro_f1 | 1 | 0.6175 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | kappa | 1 | 0.2393 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.9662 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | macro_f1 | 1 | 0.5776 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | kappa | 1 | 0.1630 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.9664 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | macro_f1 | 1 | 0.6163 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | kappa | 1 | 0.2367 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 1 | 0.9658 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | macro_f1 | 1 | 0.5776 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | kappa | 1 | 0.1630 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.9664 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | macro_f1 | 1 | 0.5776 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 1 | 0.1630 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.9664 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | macro_f1 | 1 | 0.5776 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | kappa | 1 | 0.1630 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.9664 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | macro_f1 | 1 | 0.5240 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | kappa | 1 | 0.0605 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.9657 | - | - | - | - | - | - | - | - |

No prequential benchmark exists; 3.4% failure rate makes accuracy uninformative (look at macro_f1 / kappa).

### airlines (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | acc_prequential | 1 | 0.6556 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0477 | 0.6855 | SRP | -0.0299 |
| det4_s0_wadwin_cadwin | kappa_m | 1 | 0.0401 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2938 | - | - | - |
| det4_s0_wadwin_cadwin | kappa_t | 1 | 0.1524 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.6594 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0439 | 0.6855 | SRP | -0.0261 |
| det4_s0_wadwin_chddma | kappa_m | 1 | 0.0506 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2833 | - | - | - |
| det4_s0_wadwin_chddma | kappa_t | 1 | 0.1616 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.6647 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0386 | 0.6855 | SRP | -0.0208 |
| det4_s0_wadwin_crddm | kappa_m | 1 | 0.0653 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2686 | - | - | - |
| det4_s0_wadwin_crddm | kappa_t | 1 | 0.1746 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.6632 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0401 | 0.6855 | SRP | -0.0223 |
| det4_s0_whddma_cadwin | kappa_m | 1 | 0.0612 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2727 | - | - | - |
| det4_s0_whddma_cadwin | kappa_t | 1 | 0.1710 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 1 | 0.6532 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0501 | 0.6855 | SRP | -0.0323 |
| det4_s0_whddma_chddma | kappa_m | 1 | 0.0332 | - | - | 0.3339 | DriftMoE (MoEData) | -0.3007 | - | - | - |
| det4_s0_whddma_chddma | kappa_t | 1 | 0.1463 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.6644 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0389 | 0.6855 | SRP | -0.0211 |
| det4_s0_whddma_crddm | kappa_m | 1 | 0.0647 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2692 | - | - | - |
| det4_s0_whddma_crddm | kappa_t | 1 | 0.1740 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.6637 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0396 | 0.6855 | SRP | -0.0218 |
| det4_s0_wrddm_cadwin | kappa_m | 1 | 0.0626 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2713 | - | - | - |
| det4_s0_wrddm_cadwin | kappa_t | 1 | 0.1722 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.6527 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0506 | 0.6855 | SRP | -0.0328 |
| det4_s0_wrddm_chddma | kappa_m | 1 | 0.0319 | - | - | 0.3339 | DriftMoE (MoEData) | -0.3020 | - | - | - |
| det4_s0_wrddm_chddma | kappa_t | 1 | 0.1451 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 1 | 0.6592 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0441 | 0.6855 | SRP | -0.0263 |
| det4_s0_wrddm_crddm | kappa_m | 1 | 0.0499 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2840 | - | - | - |
| det4_s0_wrddm_crddm | kappa_t | 1 | 0.1610 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 1 | 0.6517 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0516 | 0.6855 | SRP | -0.0338 |
| det4_s1_wadwin_cadwin | kappa_m | 1 | 0.0290 | - | - | 0.3339 | DriftMoE (MoEData) | -0.3049 | - | - | - |
| det4_s1_wadwin_cadwin | kappa_t | 1 | 0.1425 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.6698 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0335 | 0.6855 | SRP | -0.0157 |
| det4_s1_wadwin_chddma | kappa_m | 1 | 0.0796 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2543 | - | - | - |
| det4_s1_wadwin_chddma | kappa_t | 1 | 0.1872 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.6540 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0493 | 0.6855 | SRP | -0.0315 |
| det4_s1_wadwin_crddm | kappa_m | 1 | 0.0355 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2984 | - | - | - |
| det4_s1_wadwin_crddm | kappa_t | 1 | 0.1483 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.6592 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0441 | 0.6855 | SRP | -0.0263 |
| det4_s1_whddma_cadwin | kappa_m | 1 | 0.0501 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2838 | - | - | - |
| det4_s1_whddma_cadwin | kappa_t | 1 | 0.1611 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 1 | 0.6585 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0448 | 0.6855 | SRP | -0.0270 |
| det4_s1_whddma_chddma | kappa_m | 1 | 0.0480 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2859 | - | - | - |
| det4_s1_whddma_chddma | kappa_t | 1 | 0.1593 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.6564 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0469 | 0.6855 | SRP | -0.0291 |
| det4_s1_whddma_crddm | kappa_m | 1 | 0.0421 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2918 | - | - | - |
| det4_s1_whddma_crddm | kappa_t | 1 | 0.1541 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.6655 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0378 | 0.6855 | SRP | -0.0200 |
| det4_s1_wrddm_cadwin | kappa_m | 1 | 0.0675 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2664 | - | - | - |
| det4_s1_wrddm_cadwin | kappa_t | 1 | 0.1766 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.6574 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0459 | 0.6855 | SRP | -0.0281 |
| det4_s1_wrddm_chddma | kappa_m | 1 | 0.0449 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2890 | - | - | - |
| det4_s1_wrddm_chddma | kappa_t | 1 | 0.1566 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.6631 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0402 | 0.6855 | SRP | -0.0224 |
| det4_s1_wrddm_crddm | kappa_m | 1 | 0.0610 | - | - | 0.3339 | DriftMoE (MoEData) | -0.2729 | - | - | - |
| det4_s1_wrddm_crddm | kappa_t | 1 | 0.1708 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_no_change_acc | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_majority_acc | 1 | 0.6412 | - | - | - | - | - | - | - | - |

First 100,000 of 539,383 rows; literature uses the full stream. Compare on airlines_full instead.

### airlines_full (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | acc_prequential | 1 | 0.6338 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0695 | 0.6855 | SRP | -0.0517 |
| det4_s0_wadwin_cadwin | kappa_m | 1 | 0.1779 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1560 | - | - | - |
| det4_s0_wadwin_cadwin | kappa_t | 1 | 0.1271 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.6386 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0647 | 0.6855 | SRP | -0.0469 |
| det4_s0_wadwin_chddma | kappa_m | 1 | 0.1887 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1452 | - | - | - |
| det4_s0_wadwin_chddma | kappa_t | 1 | 0.1385 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.6334 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0699 | 0.6855 | SRP | -0.0521 |
| det4_s0_wadwin_crddm | kappa_m | 1 | 0.1771 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1568 | - | - | - |
| det4_s0_wadwin_crddm | kappa_t | 1 | 0.1262 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.6450 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0583 | 0.6855 | SRP | -0.0405 |
| det4_s0_whddma_cadwin | kappa_m | 1 | 0.2031 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1308 | - | - | - |
| det4_s0_whddma_cadwin | kappa_t | 1 | 0.1539 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 1 | 0.6305 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0728 | 0.6855 | SRP | -0.0550 |
| det4_s0_whddma_chddma | kappa_m | 1 | 0.1705 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1634 | - | - | - |
| det4_s0_whddma_chddma | kappa_t | 1 | 0.1191 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.6503 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0530 | 0.6855 | SRP | -0.0352 |
| det4_s0_whddma_crddm | kappa_m | 1 | 0.2149 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1190 | - | - | - |
| det4_s0_whddma_crddm | kappa_t | 1 | 0.1664 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.6427 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0606 | 0.6855 | SRP | -0.0428 |
| det4_s0_wrddm_cadwin | kappa_m | 1 | 0.1978 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1361 | - | - | - |
| det4_s0_wrddm_cadwin | kappa_t | 1 | 0.1482 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.6407 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0626 | 0.6855 | SRP | -0.0448 |
| det4_s0_wrddm_chddma | kappa_m | 1 | 0.1933 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1406 | - | - | - |
| det4_s0_wrddm_chddma | kappa_t | 1 | 0.1434 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 1 | 0.6326 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0707 | 0.6855 | SRP | -0.0529 |
| det4_s0_wrddm_crddm | kappa_m | 1 | 0.1752 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1587 | - | - | - |
| det4_s0_wrddm_crddm | kappa_t | 1 | 0.1242 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 1 | 0.6326 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0707 | 0.6855 | SRP | -0.0529 |
| det4_s1_wadwin_cadwin | kappa_m | 1 | 0.1751 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1588 | - | - | - |
| det4_s1_wadwin_cadwin | kappa_t | 1 | 0.1241 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.6397 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0636 | 0.6855 | SRP | -0.0458 |
| det4_s1_wadwin_chddma | kappa_m | 1 | 0.1912 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1427 | - | - | - |
| det4_s1_wadwin_chddma | kappa_t | 1 | 0.1411 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.6395 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0638 | 0.6855 | SRP | -0.0460 |
| det4_s1_wadwin_crddm | kappa_m | 1 | 0.1908 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1431 | - | - | - |
| det4_s1_wadwin_crddm | kappa_t | 1 | 0.1407 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.6463 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0570 | 0.6855 | SRP | -0.0392 |
| det4_s1_whddma_cadwin | kappa_m | 1 | 0.2059 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1280 | - | - | - |
| det4_s1_whddma_cadwin | kappa_t | 1 | 0.1568 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 1 | 0.6279 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0754 | 0.6855 | SRP | -0.0576 |
| det4_s1_whddma_chddma | kappa_m | 1 | 0.1647 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1692 | - | - | - |
| det4_s1_whddma_chddma | kappa_t | 1 | 0.1130 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.6398 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0635 | 0.6855 | SRP | -0.0457 |
| det4_s1_whddma_crddm | kappa_m | 1 | 0.1915 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1424 | - | - | - |
| det4_s1_whddma_crddm | kappa_t | 1 | 0.1414 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.6443 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0590 | 0.6855 | SRP | -0.0412 |
| det4_s1_wrddm_cadwin | kappa_m | 1 | 0.2014 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1325 | - | - | - |
| det4_s1_wrddm_cadwin | kappa_t | 1 | 0.1520 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.6373 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0660 | 0.6855 | SRP | -0.0482 |
| det4_s1_wrddm_chddma | kappa_m | 1 | 0.1858 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1481 | - | - | - |
| det4_s1_wrddm_chddma | kappa_t | 1 | 0.1354 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.6253 | - | - | 0.7033 | DriftMoE (MoEData) | -0.0780 | 0.6855 | SRP | -0.0602 |
| det4_s1_wrddm_crddm | kappa_m | 1 | 0.1588 | - | - | 0.3339 | DriftMoE (MoEData) | -0.1751 | - | - | - |
| det4_s1_wrddm_crddm | kappa_t | 1 | 0.1067 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_no_change_acc | 1 | 0.5805 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_majority_acc | 1 | 0.5546 | - | - | - | - | - | - | - | - |

Full OpenML airlines stream, 539,383 rows, same as DriftMoE. Airline / AirportFrom / AirportTo are integer codes, so River trees split them as numeric while MOA treats them as nominal; re-run SRP/ARF here rather than relying only on the cited values.

### covertype (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | acc_prequential | 1 | 0.8108 | - | - | 0.9551 | LTM (TabPFN) | -0.1443 | 0.9527 | SRP | -0.1419 |
| det4_s0_wadwin_cadwin | kappa_t | 1 | -1.0208 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | kappa_m | 1 | 0.4308 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_wadwin_cadwin | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.7908 | - | - | 0.9551 | LTM (TabPFN) | -0.1643 | 0.9527 | SRP | -0.1619 |
| det4_s0_wadwin_chddma | kappa_t | 1 | -1.2345 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | kappa_m | 1 | 0.3706 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_wadwin_chddma | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.7949 | - | - | 0.9551 | LTM (TabPFN) | -0.1602 | 0.9527 | SRP | -0.1578 |
| det4_s0_wadwin_crddm | kappa_t | 1 | -1.1904 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | kappa_m | 1 | 0.3830 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_wadwin_crddm | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.7862 | - | - | 0.9551 | LTM (TabPFN) | -0.1689 | 0.9527 | SRP | -0.1665 |
| det4_s0_whddma_cadwin | kappa_t | 1 | -1.2830 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | kappa_m | 1 | 0.3570 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_whddma_cadwin | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 1 | 0.8494 | - | - | 0.9551 | LTM (TabPFN) | -0.1057 | 0.9527 | SRP | -0.1033 |
| det4_s0_whddma_chddma | kappa_t | 1 | -0.6080 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | kappa_m | 1 | 0.5471 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_whddma_chddma | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.7775 | - | - | 0.9551 | LTM (TabPFN) | -0.1776 | 0.9527 | SRP | -0.1752 |
| det4_s0_whddma_crddm | kappa_t | 1 | -1.3765 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | kappa_m | 1 | 0.3306 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_whddma_crddm | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.7903 | - | - | 0.9551 | LTM (TabPFN) | -0.1648 | 0.9527 | SRP | -0.1624 |
| det4_s0_wrddm_cadwin | kappa_t | 1 | -1.2393 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | kappa_m | 1 | 0.3693 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_wrddm_cadwin | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.7813 | - | - | 0.9551 | LTM (TabPFN) | -0.1738 | 0.9527 | SRP | -0.1714 |
| det4_s0_wrddm_chddma | kappa_t | 1 | -1.3357 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | kappa_m | 1 | 0.3421 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_wrddm_chddma | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 1 | 0.8341 | - | - | 0.9551 | LTM (TabPFN) | -0.1210 | 0.9527 | SRP | -0.1186 |
| det4_s0_wrddm_crddm | kappa_t | 1 | -0.7719 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | kappa_m | 1 | 0.5009 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s0_wrddm_crddm | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 1 | 0.8226 | - | - | 0.9551 | LTM (TabPFN) | -0.1325 | 0.9527 | SRP | -0.1301 |
| det4_s1_wadwin_cadwin | kappa_t | 1 | -0.8943 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | kappa_m | 1 | 0.4665 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_wadwin_cadwin | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.8066 | - | - | 0.9551 | LTM (TabPFN) | -0.1485 | 0.9527 | SRP | -0.1461 |
| det4_s1_wadwin_chddma | kappa_t | 1 | -1.0656 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | kappa_m | 1 | 0.4182 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_wadwin_chddma | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.8079 | - | - | 0.9551 | LTM (TabPFN) | -0.1472 | 0.9527 | SRP | -0.1448 |
| det4_s1_wadwin_crddm | kappa_t | 1 | -1.0520 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | kappa_m | 1 | 0.4220 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_wadwin_crddm | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.8131 | - | - | 0.9551 | LTM (TabPFN) | -0.1420 | 0.9527 | SRP | -0.1396 |
| det4_s1_whddma_cadwin | kappa_t | 1 | -0.9966 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | kappa_m | 1 | 0.4376 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_whddma_cadwin | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 1 | 0.8376 | - | - | 0.9551 | LTM (TabPFN) | -0.1175 | 0.9527 | SRP | -0.1151 |
| det4_s1_whddma_chddma | kappa_t | 1 | -0.7349 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | kappa_m | 1 | 0.5113 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_whddma_chddma | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.8142 | - | - | 0.9551 | LTM (TabPFN) | -0.1409 | 0.9527 | SRP | -0.1385 |
| det4_s1_whddma_crddm | kappa_t | 1 | -0.9842 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | kappa_m | 1 | 0.4411 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_whddma_crddm | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.8122 | - | - | 0.9551 | LTM (TabPFN) | -0.1429 | 0.9527 | SRP | -0.1405 |
| det4_s1_wrddm_cadwin | kappa_t | 1 | -1.0056 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | kappa_m | 1 | 0.4351 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_wrddm_cadwin | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.8017 | - | - | 0.9551 | LTM (TabPFN) | -0.1534 | 0.9527 | SRP | -0.1510 |
| det4_s1_wrddm_chddma | kappa_t | 1 | -1.1177 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | kappa_m | 1 | 0.4035 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_wrddm_chddma | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.8336 | - | - | 0.9551 | LTM (TabPFN) | -0.1215 | 0.9527 | SRP | -0.1191 |
| det4_s1_wrddm_crddm | kappa_t | 1 | -0.7769 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | kappa_m | 1 | 0.4995 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_no_change_acc | 1 | 0.9064 | - | - | 0.9507 | No-Change | -0.0443 | - | - | - |
| det4_s1_wrddm_crddm | baseline_majority_acc | 1 | 0.6676 | - | - | - | - | - | - | - | - |

First 100,000 of 581,012 rows; literature accuracy uses the full stream (our no-change 90.64% vs Souza 95.07% on full). Compare on covertype_full instead.

### covertype_full (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | acc_prequential | 1 | 0.7841 | - | - | 0.9551 | LTM (TabPFN) | -0.1710 | 0.9527 | SRP | -0.1686 |
| det4_s0_wadwin_cadwin | kappa_t | 1 | -3.3706 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | kappa_m | 1 | 0.5787 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_wadwin_cadwin | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.7442 | - | - | 0.9551 | LTM (TabPFN) | -0.2109 | 0.9527 | SRP | -0.2085 |
| det4_s0_wadwin_chddma | kappa_t | 1 | -4.1784 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | kappa_m | 1 | 0.5009 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_wadwin_chddma | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.7565 | - | - | 0.9551 | LTM (TabPFN) | -0.1986 | 0.9527 | SRP | -0.1962 |
| det4_s0_wadwin_crddm | kappa_t | 1 | -3.9308 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | kappa_m | 1 | 0.5247 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_wadwin_crddm | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.7428 | - | - | 0.9551 | LTM (TabPFN) | -0.2123 | 0.9527 | SRP | -0.2099 |
| det4_s0_whddma_cadwin | kappa_t | 1 | -4.2077 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | kappa_m | 1 | 0.4980 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_whddma_cadwin | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 1 | 0.8618 | - | - | 0.9551 | LTM (TabPFN) | -0.0933 | 0.9527 | SRP | -0.0909 |
| det4_s0_whddma_chddma | kappa_t | 1 | -1.7991 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | kappa_m | 1 | 0.7302 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_whddma_chddma | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.7477 | - | - | 0.9551 | LTM (TabPFN) | -0.2074 | 0.9527 | SRP | -0.2050 |
| det4_s0_whddma_crddm | kappa_t | 1 | -4.1081 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | kappa_m | 1 | 0.5076 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_whddma_crddm | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.7478 | - | - | 0.9551 | LTM (TabPFN) | -0.2073 | 0.9527 | SRP | -0.2049 |
| det4_s0_wrddm_cadwin | kappa_t | 1 | -4.1072 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | kappa_m | 1 | 0.5077 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_wrddm_cadwin | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.7425 | - | - | 0.9551 | LTM (TabPFN) | -0.2126 | 0.9527 | SRP | -0.2102 |
| det4_s0_wrddm_chddma | kappa_t | 1 | -4.2135 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | kappa_m | 1 | 0.4975 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_wrddm_chddma | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 1 | 0.8299 | - | - | 0.9551 | LTM (TabPFN) | -0.1252 | 0.9527 | SRP | -0.1228 |
| det4_s0_wrddm_crddm | kappa_t | 1 | -2.4448 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | kappa_m | 1 | 0.6680 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s0_wrddm_crddm | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 1 | 0.8239 | - | - | 0.9551 | LTM (TabPFN) | -0.1312 | 0.9527 | SRP | -0.1288 |
| det4_s1_wadwin_cadwin | kappa_t | 1 | -2.5666 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | kappa_m | 1 | 0.6562 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_wadwin_cadwin | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.7831 | - | - | 0.9551 | LTM (TabPFN) | -0.1720 | 0.9527 | SRP | -0.1696 |
| det4_s1_wadwin_chddma | kappa_t | 1 | -3.3917 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | kappa_m | 1 | 0.5767 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_wadwin_chddma | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.7819 | - | - | 0.9551 | LTM (TabPFN) | -0.1732 | 0.9527 | SRP | -0.1708 |
| det4_s1_wadwin_crddm | kappa_t | 1 | -3.4155 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | kappa_m | 1 | 0.5744 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_wadwin_crddm | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.7805 | - | - | 0.9551 | LTM (TabPFN) | -0.1746 | 0.9527 | SRP | -0.1722 |
| det4_s1_whddma_cadwin | kappa_t | 1 | -3.4437 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | kappa_m | 1 | 0.5717 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_whddma_cadwin | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 1 | 0.8408 | - | - | 0.9551 | LTM (TabPFN) | -0.1143 | 0.9527 | SRP | -0.1119 |
| det4_s1_whddma_chddma | kappa_t | 1 | -2.2229 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | kappa_m | 1 | 0.6894 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_whddma_chddma | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.7780 | - | - | 0.9551 | LTM (TabPFN) | -0.1771 | 0.9527 | SRP | -0.1747 |
| det4_s1_whddma_crddm | kappa_t | 1 | -3.4949 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | kappa_m | 1 | 0.5668 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_whddma_crddm | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.7807 | - | - | 0.9551 | LTM (TabPFN) | -0.1744 | 0.9527 | SRP | -0.1720 |
| det4_s1_wrddm_cadwin | kappa_t | 1 | -3.4401 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | kappa_m | 1 | 0.5720 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_wrddm_cadwin | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.7791 | - | - | 0.9551 | LTM (TabPFN) | -0.1760 | 0.9527 | SRP | -0.1736 |
| det4_s1_wrddm_chddma | kappa_t | 1 | -3.4718 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | kappa_m | 1 | 0.5690 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_wrddm_chddma | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.8172 | - | - | 0.9551 | LTM (TabPFN) | -0.1379 | 0.9527 | SRP | -0.1355 |
| det4_s1_wrddm_crddm | kappa_t | 1 | -2.7014 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | kappa_m | 1 | 0.6432 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_no_change_acc | 1 | 0.9506 | - | - | 0.9507 | No-Change | -8.80e-05 | - | - | - |
| det4_s1_wrddm_crddm | baseline_majority_acc | 1 | 0.4876 | - | - | - | - | - | - | - | - |

Full 581,012 rows in UCI order. Calibrated: baseline_no_change_acc 95.06% vs Souza et al. 95.07%. Features are not min-max normalised as in MOA covtypeNorm; tree learners are unaffected, distance-based ones are not.

### electricity (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | acc_prequential | 1 | 0.8114 | - | - | 0.9500 | TabFM+FIFO | -0.1386 | 0.9008 | ARF (MOA, 100 trees) | -0.0894 |
| det4_s0_wadwin_cadwin | kappa_t | 1 | -0.2855 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.6092 | 0.3237 | ARF (MOA, 100 trees) | -0.6092 |
| det4_s0_wadwin_cadwin | kappa_m | 1 | 0.5557 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_wadwin_cadwin | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.8187 | - | - | 0.9500 | TabFM+FIFO | -0.1313 | 0.9008 | ARF (MOA, 100 trees) | -0.0821 |
| det4_s0_wadwin_chddma | kappa_t | 1 | -0.2356 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5593 | 0.3237 | ARF (MOA, 100 trees) | -0.5593 |
| det4_s0_wadwin_chddma | kappa_m | 1 | 0.5729 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_wadwin_chddma | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.8134 | - | - | 0.9500 | TabFM+FIFO | -0.1366 | 0.9008 | ARF (MOA, 100 trees) | -0.0874 |
| det4_s0_wadwin_crddm | kappa_t | 1 | -0.2717 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5954 | 0.3237 | ARF (MOA, 100 trees) | -0.5954 |
| det4_s0_wadwin_crddm | kappa_m | 1 | 0.5604 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_wadwin_crddm | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.8052 | - | - | 0.9500 | TabFM+FIFO | -0.1448 | 0.9008 | ARF (MOA, 100 trees) | -0.0956 |
| det4_s0_whddma_cadwin | kappa_t | 1 | -0.3276 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.6513 | 0.3237 | ARF (MOA, 100 trees) | -0.6513 |
| det4_s0_whddma_cadwin | kappa_m | 1 | 0.5411 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_whddma_cadwin | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 1 | 0.8475 | - | - | 0.9500 | TabFM+FIFO | -0.1025 | 0.9008 | ARF (MOA, 100 trees) | -0.0533 |
| det4_s0_whddma_chddma | kappa_t | 1 | -0.0397 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.3634 | 0.3237 | ARF (MOA, 100 trees) | -0.3634 |
| det4_s0_whddma_chddma | kappa_m | 1 | 0.6406 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_whddma_chddma | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.8219 | - | - | 0.9500 | TabFM+FIFO | -0.1281 | 0.9008 | ARF (MOA, 100 trees) | -0.0789 |
| det4_s0_whddma_crddm | kappa_t | 1 | -0.2142 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5379 | 0.3237 | ARF (MOA, 100 trees) | -0.5379 |
| det4_s0_whddma_crddm | kappa_m | 1 | 0.5803 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_whddma_crddm | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.7945 | - | - | 0.9500 | TabFM+FIFO | -0.1555 | 0.9008 | ARF (MOA, 100 trees) | -0.1063 |
| det4_s0_wrddm_cadwin | kappa_t | 1 | -0.4006 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.7243 | 0.3237 | ARF (MOA, 100 trees) | -0.7243 |
| det4_s0_wrddm_cadwin | kappa_m | 1 | 0.5159 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_wrddm_cadwin | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.8340 | - | - | 0.9500 | TabFM+FIFO | -0.1160 | 0.9008 | ARF (MOA, 100 trees) | -0.0668 |
| det4_s0_wrddm_chddma | kappa_t | 1 | -0.1315 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4552 | 0.3237 | ARF (MOA, 100 trees) | -0.4552 |
| det4_s0_wrddm_chddma | kappa_m | 1 | 0.6089 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_wrddm_chddma | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 1 | 0.8447 | - | - | 0.9500 | TabFM+FIFO | -0.1053 | 0.9008 | ARF (MOA, 100 trees) | -0.0561 |
| det4_s0_wrddm_crddm | kappa_t | 1 | -0.0584 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.3821 | 0.3237 | ARF (MOA, 100 trees) | -0.3821 |
| det4_s0_wrddm_crddm | kappa_m | 1 | 0.6342 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s0_wrddm_crddm | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 1 | 0.8403 | - | - | 0.9500 | TabFM+FIFO | -0.1097 | 0.9008 | ARF (MOA, 100 trees) | -0.0605 |
| det4_s1_wadwin_cadwin | kappa_t | 1 | -0.0887 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4124 | 0.3237 | ARF (MOA, 100 trees) | -0.4124 |
| det4_s1_wadwin_cadwin | kappa_m | 1 | 0.6237 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_wadwin_cadwin | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.8316 | - | - | 0.9500 | TabFM+FIFO | -0.1184 | 0.9008 | ARF (MOA, 100 trees) | -0.0692 |
| det4_s1_wadwin_chddma | kappa_t | 1 | -0.1476 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4713 | 0.3237 | ARF (MOA, 100 trees) | -0.4713 |
| det4_s1_wadwin_chddma | kappa_m | 1 | 0.6033 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_wadwin_chddma | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.8319 | - | - | 0.9500 | TabFM+FIFO | -0.1181 | 0.9008 | ARF (MOA, 100 trees) | -0.0689 |
| det4_s1_wadwin_crddm | kappa_t | 1 | -0.1456 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4693 | 0.3237 | ARF (MOA, 100 trees) | -0.4693 |
| det4_s1_wadwin_crddm | kappa_m | 1 | 0.6040 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_wadwin_crddm | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.8249 | - | - | 0.9500 | TabFM+FIFO | -0.1251 | 0.9008 | ARF (MOA, 100 trees) | -0.0759 |
| det4_s1_whddma_cadwin | kappa_t | 1 | -0.1933 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5170 | 0.3237 | ARF (MOA, 100 trees) | -0.5170 |
| det4_s1_whddma_cadwin | kappa_m | 1 | 0.5875 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_whddma_cadwin | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 1 | 0.8464 | - | - | 0.9500 | TabFM+FIFO | -0.1036 | 0.9008 | ARF (MOA, 100 trees) | -0.0544 |
| det4_s1_whddma_chddma | kappa_t | 1 | -0.0472 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.3709 | 0.3237 | ARF (MOA, 100 trees) | -0.3709 |
| det4_s1_whddma_chddma | kappa_m | 1 | 0.6380 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_whddma_chddma | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.8267 | - | - | 0.9500 | TabFM+FIFO | -0.1233 | 0.9008 | ARF (MOA, 100 trees) | -0.0741 |
| det4_s1_whddma_crddm | kappa_t | 1 | -0.1814 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5051 | 0.3237 | ARF (MOA, 100 trees) | -0.5051 |
| det4_s1_whddma_crddm | kappa_m | 1 | 0.5916 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_whddma_crddm | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.8251 | - | - | 0.9500 | TabFM+FIFO | -0.1249 | 0.9008 | ARF (MOA, 100 trees) | -0.0757 |
| det4_s1_wrddm_cadwin | kappa_t | 1 | -0.1922 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5159 | 0.3237 | ARF (MOA, 100 trees) | -0.5159 |
| det4_s1_wrddm_cadwin | kappa_m | 1 | 0.5879 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_wrddm_cadwin | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.8275 | - | - | 0.9500 | TabFM+FIFO | -0.1225 | 0.9008 | ARF (MOA, 100 trees) | -0.0733 |
| det4_s1_wrddm_chddma | kappa_t | 1 | -0.1758 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4995 | 0.3237 | ARF (MOA, 100 trees) | -0.4995 |
| det4_s1_wrddm_chddma | kappa_m | 1 | 0.5936 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_wrddm_chddma | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.8468 | - | - | 0.9500 | TabFM+FIFO | -0.1032 | 0.9008 | ARF (MOA, 100 trees) | -0.0540 |
| det4_s1_wrddm_crddm | kappa_t | 1 | -0.0444 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.3681 | 0.3237 | ARF (MOA, 100 trees) | -0.3681 |
| det4_s1_wrddm_crddm | kappa_m | 1 | 0.6390 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -1.61e-05 | - | - | - |
| det4_s1_wrddm_crddm | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |

OpenML 151 / MOA elecNormNew, 45,312 rows, same as literature. Calibrated: baseline_no_change_acc reproduces Souza et al. 85.33%.

### gas_sensor_drift (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | acc_prequential | 1 | 0.8377 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | kappa_t | 1 | 0.6021 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.7779 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | kappa_t | 1 | 0.4555 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.7774 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | kappa_t | 1 | 0.4543 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.6485 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | kappa_t | 1 | 0.1385 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 1 | 0.8876 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | kappa_t | 1 | 0.7246 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_chddma | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.6804 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | kappa_t | 1 | 0.2167 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.5671 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | kappa_t | 1 | -0.0610 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.7752 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | kappa_t | 1 | 0.4490 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 1 | 0.8990 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | kappa_t | 1 | 0.7524 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 1 | 0.8961 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | kappa_t | 1 | 0.7454 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.8464 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | kappa_t | 1 | 0.6234 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.8708 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | kappa_t | 1 | 0.6833 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.7900 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | kappa_t | 1 | 0.4853 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 1 | 0.9002 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | kappa_t | 1 | 0.7554 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_chddma | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.7540 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | kappa_t | 1 | 0.3970 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.8100 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | kappa_t | 1 | 0.5343 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.8180 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | kappa_t | 1 | 0.5540 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.9018 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | kappa_t | 1 | 0.7593 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | baseline_no_change_acc | 1 | 0.5920 | - | - | - | - | - | - | - | - |

Literature uses batch domain adaptation (train batch 1, test batches 2-10), not prequential.

### insects_abrupt_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_chddma | acc_window1000_mean | 1 | 0.5295 | - | - | 0.7434 | ARF | -0.2139 | 0.7434 | ARF | -0.2139 |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.5281 | - | - | 0.6602 | NB + STEPD | -0.1321 | - | - | - |
| det4_s0_wadwin_chddma | kappa | 1 | 0.4337 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | n_alarms | 1 | 6.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | f1 | 1 | 0.3636 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | episode_recall | 1 | 0.4000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_window1000_mean | 1 | 0.5473 | - | - | 0.7434 | ARF | -0.1961 | 0.7434 | ARF | -0.1961 |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.5481 | - | - | 0.6602 | NB + STEPD | -0.1121 | - | - | - |
| det4_s0_wadwin_crddm | kappa | 1 | 0.4577 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | n_alarms | 1 | 4.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | f1 | 1 | 0.4444 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | episode_recall | 1 | 0.4000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_window1000_mean | 1 | 0.5309 | - | - | 0.7434 | ARF | -0.2125 | 0.7434 | ARF | -0.2125 |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.5334 | - | - | 0.6602 | NB + STEPD | -0.1268 | - | - | - |
| det4_s0_whddma_cadwin | kappa | 1 | 0.4401 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_window1000_mean | 1 | 0.5180 | - | - | 0.7434 | ARF | -0.2254 | 0.7434 | ARF | -0.2254 |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.5183 | - | - | 0.6602 | NB + STEPD | -0.1419 | - | - | - |
| det4_s0_whddma_crddm | kappa | 1 | 0.4220 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_window1000_mean | 1 | 0.5663 | - | - | 0.7434 | ARF | -0.1771 | 0.7434 | ARF | -0.1771 |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.5625 | - | - | 0.6602 | NB + STEPD | -0.0977 | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 1 | 0.4750 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_window1000_mean | 1 | 0.5200 | - | - | 0.7434 | ARF | -0.2234 | 0.7434 | ARF | -0.2234 |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.5215 | - | - | 0.6602 | NB + STEPD | -0.1387 | - | - | - |
| det4_s0_wrddm_chddma | kappa | 1 | 0.4258 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_window1000_mean | 1 | 0.6308 | - | - | 0.7434 | ARF | -0.1126 | 0.7434 | ARF | -0.1126 |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.6349 | - | - | 0.6602 | NB + STEPD | -0.0253 | - | - | - |
| det4_s1_wadwin_chddma | kappa | 1 | 0.5619 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | n_alarms | 1 | 15.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | f1 | 1 | 0.5455 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_window1000_mean | 1 | 0.6291 | - | - | 0.7434 | ARF | -0.1143 | 0.7434 | ARF | -0.1143 |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.6252 | - | - | 0.6602 | NB + STEPD | -0.0350 | - | - | - |
| det4_s1_wadwin_crddm | kappa | 1 | 0.5503 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | n_alarms | 1 | 11.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | f1 | 1 | 0.5882 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_window1000_mean | 1 | 0.5995 | - | - | 0.7434 | ARF | -0.1439 | 0.7434 | ARF | -0.1439 |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.6037 | - | - | 0.6602 | NB + STEPD | -0.0565 | - | - | - |
| det4_s1_whddma_cadwin | kappa | 1 | 0.5244 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | n_alarms | 1 | 5.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | f1 | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_window1000_mean | 1 | 0.6139 | - | - | 0.7434 | ARF | -0.1295 | 0.7434 | ARF | -0.1295 |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.6101 | - | - | 0.6602 | NB + STEPD | -0.0501 | - | - | - |
| det4_s1_whddma_crddm | kappa | 1 | 0.5321 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | n_alarms | 1 | 6.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | f1 | 1 | 0.5455 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | episode_recall | 1 | 0.6000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_window1000_mean | 1 | 0.5731 | - | - | 0.7434 | ARF | -0.1703 | 0.7434 | ARF | -0.1703 |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.5764 | - | - | 0.6602 | NB + STEPD | -0.0838 | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 1 | 0.4917 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | n_alarms | 1 | 4.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | f1 | 1 | 0.4444 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | episode_recall | 1 | 0.4000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_window1000_mean | 1 | 0.6108 | - | - | 0.7434 | ARF | -0.1326 | 0.7434 | ARF | -0.1326 |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.6151 | - | - | 0.6602 | NB + STEPD | -0.0451 | - | - | - |
| det4_s1_wrddm_chddma | kappa | 1 | 0.5381 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | n_alarms | 1 | 6.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | episode_recall | 1 | 0.4000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_window1000_mean | 1 | 0.6274 | - | - | 0.7434 | ARF | -0.1160 | 0.7434 | ARF | -0.1160 |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.6317 | - | - | 0.6602 | NB + STEPD | -0.0285 | - | - | - |
| det4_s1_wrddm_crddm | kappa | 1 | 0.5580 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | n_alarms | 1 | 25.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | f1 | 1 | 0.3750 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |

Same data and change points as Souza et al. 2020. Table 5 is sliding-window (1000) accuracy -> compare acc_window1000_mean; Table 6 (NB + detector) -> compare acc_prequential. delta_max is not from the paper (it reports detection counts only).

### insects_incremental_abrupt_reoccurring_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_chddma | acc_window1000_mean | 1 | 0.5540 | - | - | 0.7495 | ARF | -0.1955 | 0.7495 | ARF | -0.1955 |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.5556 | - | - | 0.6877 | NB + STEPD | -0.1321 | - | - | - |
| det4_s0_wadwin_chddma | kappa | 1 | 0.4667 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | n_alarms | 1 | 8.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_window1000_mean | 1 | 0.5945 | - | - | 0.7495 | ARF | -0.1550 | 0.7495 | ARF | -0.1550 |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.5958 | - | - | 0.6877 | NB + STEPD | -0.0919 | - | - | - |
| det4_s0_wadwin_crddm | kappa | 1 | 0.5150 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | n_alarms | 1 | 10.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | f1 | 1 | 0.1667 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | episode_recall | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_window1000_mean | 1 | 0.5007 | - | - | 0.7495 | ARF | -0.2488 | 0.7495 | ARF | -0.2488 |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.5012 | - | - | 0.6877 | NB + STEPD | -0.1865 | - | - | - |
| det4_s0_whddma_cadwin | kappa | 1 | 0.4014 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_window1000_mean | 1 | 0.5550 | - | - | 0.7495 | ARF | -0.1945 | 0.7495 | ARF | -0.1945 |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.5565 | - | - | 0.6877 | NB + STEPD | -0.1312 | - | - | - |
| det4_s0_whddma_crddm | kappa | 1 | 0.4678 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | n_alarms | 1 | 3.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | f1 | 1 | 0.8571 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | episode_recall | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_window1000_mean | 1 | 0.5028 | - | - | 0.7495 | ARF | -0.2467 | 0.7495 | ARF | -0.2467 |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.5046 | - | - | 0.6877 | NB + STEPD | -0.1831 | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 1 | 0.4056 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_window1000_mean | 1 | 0.5201 | - | - | 0.7495 | ARF | -0.2294 | 0.7495 | ARF | -0.2294 |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.5217 | - | - | 0.6877 | NB + STEPD | -0.1660 | - | - | - |
| det4_s0_wrddm_chddma | kappa | 1 | 0.4261 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | n_alarms | 1 | 4.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_window1000_mean | 1 | 0.6325 | - | - | 0.7495 | ARF | -0.1170 | 0.7495 | ARF | -0.1170 |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.6344 | - | - | 0.6877 | NB + STEPD | -0.0533 | - | - | - |
| det4_s1_wadwin_chddma | kappa | 1 | 0.5613 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | n_alarms | 1 | 22.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | f1 | 1 | 0.4286 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_window1000_mean | 1 | 0.6321 | - | - | 0.7495 | ARF | -0.1174 | 0.7495 | ARF | -0.1174 |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.6340 | - | - | 0.6877 | NB + STEPD | -0.0537 | - | - | - |
| det4_s1_wadwin_crddm | kappa | 1 | 0.5608 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | n_alarms | 1 | 24.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | f1 | 1 | 0.4000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_window1000_mean | 1 | 0.6310 | - | - | 0.7495 | ARF | -0.1185 | 0.7495 | ARF | -0.1185 |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.6322 | - | - | 0.6877 | NB + STEPD | -0.0555 | - | - | - |
| det4_s1_whddma_cadwin | kappa | 1 | 0.5586 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | n_alarms | 1 | 16.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | f1 | 1 | 0.5455 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_window1000_mean | 1 | 0.5891 | - | - | 0.7495 | ARF | -0.1604 | 0.7495 | ARF | -0.1604 |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.5906 | - | - | 0.6877 | NB + STEPD | -0.0971 | - | - | - |
| det4_s1_whddma_crddm | kappa | 1 | 0.5087 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | n_alarms | 1 | 14.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | f1 | 1 | 0.6000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_window1000_mean | 1 | 0.6302 | - | - | 0.7495 | ARF | -0.1193 | 0.7495 | ARF | -0.1193 |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.6316 | - | - | 0.6877 | NB + STEPD | -0.0561 | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 1 | 0.5580 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | n_alarms | 1 | 18.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | f1 | 1 | 0.4348 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_window1000_mean | 1 | 0.6284 | - | - | 0.7495 | ARF | -0.1211 | 0.7495 | ARF | -0.1211 |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.6298 | - | - | 0.6877 | NB + STEPD | -0.0579 | - | - | - |
| det4_s1_wrddm_chddma | kappa | 1 | 0.5558 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | n_alarms | 1 | 15.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | f1 | 1 | 0.5714 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_window1000_mean | 1 | 0.6522 | - | - | 0.7495 | ARF | -0.0973 | 0.7495 | ARF | -0.0973 |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.6541 | - | - | 0.6877 | NB + STEPD | -0.0336 | - | - | - |
| det4_s1_wrddm_crddm | kappa | 1 | 0.5850 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | n_alarms | 1 | 47.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | f1 | 1 | 0.2264 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |

See insects_abrupt_balanced for the metric mapping.

### insects_incremental_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_chddma | acc_window1000_mean | 1 | 0.5046 | - | - | 0.6429 | ARF | -0.1383 | 0.6429 | ARF | -0.1383 |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.5066 | - | - | 0.5663 | NB + CUSUM | -0.0597 | - | - | - |
| det4_s0_wadwin_chddma | kappa | 1 | 0.4079 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | n_alarms | 1 | 2.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_window1000_mean | 1 | 0.5156 | - | - | 0.6429 | ARF | -0.1273 | 0.6429 | ARF | -0.1273 |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.5172 | - | - | 0.5663 | NB + CUSUM | -0.0491 | - | - | - |
| det4_s0_wadwin_crddm | kappa | 1 | 0.4206 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_window1000_mean | 1 | 0.5163 | - | - | 0.6429 | ARF | -0.1266 | 0.6429 | ARF | -0.1266 |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.5183 | - | - | 0.5663 | NB + CUSUM | -0.0480 | - | - | - |
| det4_s0_whddma_cadwin | kappa | 1 | 0.4220 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | n_alarms | 1 | 2.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_window1000_mean | 1 | 0.5149 | - | - | 0.6429 | ARF | -0.1280 | 0.6429 | ARF | -0.1280 |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.5167 | - | - | 0.5663 | NB + CUSUM | -0.0496 | - | - | - |
| det4_s0_whddma_crddm | kappa | 1 | 0.4200 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_window1000_mean | 1 | 0.5142 | - | - | 0.6429 | ARF | -0.1287 | 0.6429 | ARF | -0.1287 |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.5160 | - | - | 0.5663 | NB + CUSUM | -0.0503 | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 1 | 0.4192 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_window1000_mean | 1 | 0.5552 | - | - | 0.6429 | ARF | -0.0877 | 0.6429 | ARF | -0.0877 |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.5567 | - | - | 0.5663 | NB + CUSUM | -0.0096 | - | - | - |
| det4_s0_wrddm_chddma | kappa | 1 | 0.4681 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | n_alarms | 1 | 3.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_window1000_mean | 1 | 0.5367 | - | - | 0.6429 | ARF | -0.1062 | 0.6429 | ARF | -0.1062 |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.5389 | - | - | 0.5663 | NB + CUSUM | -0.0274 | - | - | - |
| det4_s1_wadwin_chddma | kappa | 1 | 0.4466 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | n_alarms | 1 | 2.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_window1000_mean | 1 | 0.5362 | - | - | 0.6429 | ARF | -0.1067 | 0.6429 | ARF | -0.1067 |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.5384 | - | - | 0.5663 | NB + CUSUM | -0.0279 | - | - | - |
| det4_s1_wadwin_crddm | kappa | 1 | 0.4461 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | n_alarms | 1 | 2.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_window1000_mean | 1 | 0.5498 | - | - | 0.6429 | ARF | -0.0931 | 0.6429 | ARF | -0.0931 |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.5519 | - | - | 0.5663 | NB + CUSUM | -0.0144 | - | - | - |
| det4_s1_whddma_cadwin | kappa | 1 | 0.4623 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | n_alarms | 1 | 3.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_window1000_mean | 1 | 0.5556 | - | - | 0.6429 | ARF | -0.0873 | 0.6429 | ARF | -0.0873 |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.5572 | - | - | 0.5663 | NB + CUSUM | -0.0091 | - | - | - |
| det4_s1_whddma_crddm | kappa | 1 | 0.4686 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | n_alarms | 1 | 3.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_window1000_mean | 1 | 0.5320 | - | - | 0.6429 | ARF | -0.1109 | 0.6429 | ARF | -0.1109 |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.5335 | - | - | 0.5663 | NB + CUSUM | -0.0328 | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 1 | 0.4402 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_window1000_mean | 1 | 0.5655 | - | - | 0.6429 | ARF | -0.0774 | 0.6429 | ARF | -0.0774 |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.5675 | - | - | 0.5663 | NB + CUSUM | 0.0012 | - | - | - |
| det4_s1_wrddm_chddma | kappa | 1 | 0.4810 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | n_alarms | 1 | 6.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_window1000_mean | 1 | 0.5672 | - | - | 0.6429 | ARF | -0.0757 | 0.6429 | ARF | -0.0757 |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.5694 | - | - | 0.5663 | NB + CUSUM | 0.0031 | - | - | - |
| det4_s1_wrddm_crddm | kappa | 1 | 0.4833 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | n_alarms | 1 | 15.0000 | - | - | - | - | - | - | - | - |

Continuous drift, empty ground truth: detection fields are null. See insects_abrupt_balanced for the metric mapping.

### insects_incremental_gradual_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_chddma | acc_window1000_mean | 1 | 0.6043 | - | - | 0.7792 | ARF | -0.1749 | 0.7792 | ARF | -0.1749 |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.6084 | - | - | 0.7226 | NB + ADWIN | -0.1142 | - | - | - |
| det4_s0_wadwin_chddma | kappa | 1 | 0.5301 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | n_alarms | 1 | 4.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s0_wadwin_chddma | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_window1000_mean | 1 | 0.5924 | - | - | 0.7792 | ARF | -0.1868 | 0.7792 | ARF | -0.1868 |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.5950 | - | - | 0.7226 | NB + ADWIN | -0.1276 | - | - | - |
| det4_s0_wadwin_crddm | kappa | 1 | 0.5140 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | n_alarms | 1 | 3.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s0_wadwin_crddm | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_window1000_mean | 1 | 0.5773 | - | - | 0.7792 | ARF | -0.2019 | 0.7792 | ARF | -0.2019 |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.5840 | - | - | 0.7226 | NB + ADWIN | -0.1386 | - | - | - |
| det4_s0_whddma_cadwin | kappa | 1 | 0.5008 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s0_whddma_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_window1000_mean | 1 | 0.5797 | - | - | 0.7792 | ARF | -0.1995 | 0.7792 | ARF | -0.1995 |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.5864 | - | - | 0.7226 | NB + ADWIN | -0.1362 | - | - | - |
| det4_s0_whddma_crddm | kappa | 1 | 0.5037 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s0_whddma_crddm | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_window1000_mean | 1 | 0.5799 | - | - | 0.7792 | ARF | -0.1993 | 0.7792 | ARF | -0.1993 |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.5865 | - | - | 0.7226 | NB + ADWIN | -0.1361 | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 1 | 0.5039 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s0_wrddm_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_window1000_mean | 1 | 0.5730 | - | - | 0.7792 | ARF | -0.2062 | 0.7792 | ARF | -0.2062 |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.5800 | - | - | 0.7226 | NB + ADWIN | -0.1426 | - | - | - |
| det4_s0_wrddm_chddma | kappa | 1 | 0.4960 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s0_wrddm_chddma | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_window1000_mean | 1 | 0.6483 | - | - | 0.7792 | ARF | -0.1309 | 0.7792 | ARF | -0.1309 |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.6545 | - | - | 0.7226 | NB + ADWIN | -0.0681 | - | - | - |
| det4_s1_wadwin_chddma | kappa | 1 | 0.5854 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | n_alarms | 1 | 10.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | f1 | 1 | 0.1818 | - | - | 0.2500 | PHT + HT | -0.0682 | - | - | - |
| det4_s1_wadwin_chddma | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_window1000_mean | 1 | 0.6639 | - | - | 0.7792 | ARF | -0.1153 | 0.7792 | ARF | -0.1153 |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.6693 | - | - | 0.7226 | NB + ADWIN | -0.0533 | - | - | - |
| det4_s1_wadwin_crddm | kappa | 1 | 0.6032 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | n_alarms | 1 | 11.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | f1 | 1 | 0.1667 | - | - | 0.2500 | PHT + HT | -0.0833 | - | - | - |
| det4_s1_wadwin_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_window1000_mean | 1 | 0.6334 | - | - | 0.7792 | ARF | -0.1458 | 0.7792 | ARF | -0.1458 |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.6384 | - | - | 0.7226 | NB + ADWIN | -0.0842 | - | - | - |
| det4_s1_whddma_cadwin | kappa | 1 | 0.5661 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | n_alarms | 1 | 3.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | f1 | 1 | 0.5000 | - | - | 0.2500 | PHT + HT | 0.2500 | - | - | - |
| det4_s1_whddma_cadwin | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_window1000_mean | 1 | 0.6263 | - | - | 0.7792 | ARF | -0.1529 | 0.7792 | ARF | -0.1529 |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.6328 | - | - | 0.7226 | NB + ADWIN | -0.0898 | - | - | - |
| det4_s1_whddma_crddm | kappa | 1 | 0.5593 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | n_alarms | 1 | 4.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s1_whddma_crddm | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_window1000_mean | 1 | 0.6526 | - | - | 0.7792 | ARF | -0.1266 | 0.7792 | ARF | -0.1266 |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.6576 | - | - | 0.7226 | NB + ADWIN | -0.0650 | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 1 | 0.5892 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | n_alarms | 1 | 4.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | f1 | 1 | 0.0000 | - | - | 0.2500 | PHT + HT | -0.2500 | - | - | - |
| det4_s1_wrddm_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_window1000_mean | 1 | 0.6332 | - | - | 0.7792 | ARF | -0.1460 | 0.7792 | ARF | -0.1460 |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.6383 | - | - | 0.7226 | NB + ADWIN | -0.0843 | - | - | - |
| det4_s1_wrddm_chddma | kappa | 1 | 0.5659 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | n_alarms | 1 | 3.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | f1 | 1 | 0.5000 | - | - | 0.2500 | PHT + HT | 0.2500 | - | - | - |
| det4_s1_wrddm_chddma | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_window1000_mean | 1 | 0.6651 | - | - | 0.7792 | ARF | -0.1141 | 0.7792 | ARF | -0.1141 |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.6723 | - | - | 0.7226 | NB + ADWIN | -0.0503 | - | - | - |
| det4_s1_wrddm_crddm | kappa | 1 | 0.6067 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | n_alarms | 1 | 16.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | f1 | 1 | 0.1176 | - | - | 0.2500 | PHT + HT | -0.1324 | - | - | - |
| det4_s1_wrddm_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |

See insects_abrupt_balanced for the metric mapping.

### insects_incremental_reoccurring_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_chddma | acc_window1000_mean | 1 | 0.5899 | - | - | 0.7713 | ARF | -0.1814 | 0.7713 | ARF | -0.1814 |
| det4_s0_wadwin_chddma | acc_prequential | 1 | 0.5919 | - | - | 0.6982 | NB + SEED | -0.1063 | - | - | - |
| det4_s0_wadwin_chddma | kappa | 1 | 0.5103 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | n_alarms | 1 | 12.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | f1 | 1 | 0.1429 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | episode_recall | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_window1000_mean | 1 | 0.5916 | - | - | 0.7713 | ARF | -0.1797 | 0.7713 | ARF | -0.1797 |
| det4_s0_wadwin_crddm | acc_prequential | 1 | 0.5935 | - | - | 0.6982 | NB + SEED | -0.1047 | - | - | - |
| det4_s0_wadwin_crddm | kappa | 1 | 0.5122 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | n_alarms | 1 | 12.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | f1 | 1 | 0.2857 | - | - | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_window1000_mean | 1 | 0.4739 | - | - | 0.7713 | ARF | -0.2974 | 0.7713 | ARF | -0.2974 |
| det4_s0_whddma_cadwin | acc_prequential | 1 | 0.4744 | - | - | 0.6982 | NB + SEED | -0.2238 | - | - | - |
| det4_s0_whddma_cadwin | kappa | 1 | 0.3692 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_window1000_mean | 1 | 0.4930 | - | - | 0.7713 | ARF | -0.2783 | 0.7713 | ARF | -0.2783 |
| det4_s0_whddma_crddm | acc_prequential | 1 | 0.4944 | - | - | 0.6982 | NB + SEED | -0.2038 | - | - | - |
| det4_s0_whddma_crddm | kappa | 1 | 0.3933 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | n_alarms | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_whddma_crddm | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_window1000_mean | 1 | 0.4575 | - | - | 0.7713 | ARF | -0.3138 | 0.7713 | ARF | -0.3138 |
| det4_s0_wrddm_cadwin | acc_prequential | 1 | 0.4578 | - | - | 0.6982 | NB + SEED | -0.2404 | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 1 | 0.3494 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | f1 | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | episode_recall | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_window1000_mean | 1 | 0.5772 | - | - | 0.7713 | ARF | -0.1941 | 0.7713 | ARF | -0.1941 |
| det4_s0_wrddm_chddma | acc_prequential | 1 | 0.5787 | - | - | 0.6982 | NB + SEED | -0.1195 | - | - | - |
| det4_s0_wrddm_chddma | kappa | 1 | 0.4944 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | n_alarms | 1 | 2.0000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | episode_recall | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_window1000_mean | 1 | 0.6475 | - | - | 0.7713 | ARF | -0.1238 | 0.7713 | ARF | -0.1238 |
| det4_s1_wadwin_chddma | acc_prequential | 1 | 0.6488 | - | - | 0.6982 | NB + SEED | -0.0494 | - | - | - |
| det4_s1_wadwin_chddma | kappa | 1 | 0.5786 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | n_alarms | 1 | 20.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_window1000_mean | 1 | 0.6453 | - | - | 0.7713 | ARF | -0.1260 | 0.7713 | ARF | -0.1260 |
| det4_s1_wadwin_crddm | acc_prequential | 1 | 0.6466 | - | - | 0.6982 | NB + SEED | -0.0516 | - | - | - |
| det4_s1_wadwin_crddm | kappa | 1 | 0.5759 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | n_alarms | 1 | 19.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | f1 | 1 | 0.2727 | - | - | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_window1000_mean | 1 | 0.5847 | - | - | 0.7713 | ARF | -0.1866 | 0.7713 | ARF | -0.1866 |
| det4_s1_whddma_cadwin | acc_prequential | 1 | 0.5858 | - | - | 0.6982 | NB + SEED | -0.1124 | - | - | - |
| det4_s1_whddma_cadwin | kappa | 1 | 0.5030 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | n_alarms | 1 | 9.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | episode_recall | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_window1000_mean | 1 | 0.6496 | - | - | 0.7713 | ARF | -0.1217 | 0.7713 | ARF | -0.1217 |
| det4_s1_whddma_crddm | acc_prequential | 1 | 0.6507 | - | - | 0.6982 | NB + SEED | -0.0475 | - | - | - |
| det4_s1_whddma_crddm | kappa | 1 | 0.5809 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | n_alarms | 1 | 19.0000 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | f1 | 1 | 0.3478 | - | - | - | - | - | - | - | - |
| det4_s1_whddma_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_window1000_mean | 1 | 0.5940 | - | - | 0.7713 | ARF | -0.1773 | 0.7713 | ARF | -0.1773 |
| det4_s1_wrddm_cadwin | acc_prequential | 1 | 0.5953 | - | - | 0.6982 | NB + SEED | -0.1029 | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 1 | 0.5144 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | n_alarms | 1 | 14.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | episode_recall | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_window1000_mean | 1 | 0.6368 | - | - | 0.7713 | ARF | -0.1345 | 0.7713 | ARF | -0.1345 |
| det4_s1_wrddm_chddma | acc_prequential | 1 | 0.6386 | - | - | 0.6982 | NB + SEED | -0.0596 | - | - | - |
| det4_s1_wrddm_chddma | kappa | 1 | 0.5663 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | n_alarms | 1 | 10.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | f1 | 1 | 0.3333 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_window1000_mean | 1 | 0.6731 | - | - | 0.7713 | ARF | -0.0982 | 0.7713 | ARF | -0.0982 |
| det4_s1_wrddm_crddm | acc_prequential | 1 | 0.6750 | - | - | 0.6982 | NB + SEED | -0.0232 | - | - | - |
| det4_s1_wrddm_crddm | kappa | 1 | 0.6100 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | n_alarms | 1 | 51.0000 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | f1 | 1 | 0.1455 | - | - | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | episode_recall | 1 | 1.0000 | - | - | - | - | - | - | - | - |

See insects_abrupt_balanced for the metric mapping.

### synthetic_binary (role: dev)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_cadwin | acc_prequential | 40 | 0.9507 | 0.0158 | 0.0051 | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | kappa | 40 | 0.8960 | 0.0289 | 0.0092 | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | f1 | 40 | 0.3232 | 0.1671 | 0.0534 | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | episode_recall | 40 | 0.4687 | 0.2560 | 0.0819 | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | mdt | 38 | 621.9634 | 200.2180 | 65.8100 | - | - | - | - | - | - |
| det4_s0_wadwin_cadwin | far | 40 | 0.1012 | 0.0360 | 0.0115 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | acc_prequential | 40 | 0.9279 | 0.0222 | 0.0071 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | kappa | 40 | 0.8481 | 0.0413 | 0.0132 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | f1 | 40 | 0.2705 | 0.2075 | 0.0664 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | episode_recall | 40 | 0.2305 | 0.1946 | 0.0622 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | mdt | 31 | 617.2215 | 205.7240 | 75.4602 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | far | 40 | 0.0292 | 0.0183 | 0.0059 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 40 | 0.9290 | 0.0331 | 0.0106 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | kappa | 40 | 0.8514 | 0.0635 | 0.0203 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | f1 | 40 | 0.3732 | 0.2044 | 0.0654 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | episode_recall | 40 | 0.3173 | 0.1865 | 0.0596 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | mdt | 35 | 560.3114 | 180.0135 | 61.8368 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | far | 40 | 0.0227 | 0.0093 | 0.0030 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 40 | 0.9269 | 0.0311 | 0.0099 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | kappa | 40 | 0.8467 | 0.0594 | 0.0190 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | f1 | 40 | 0.0856 | 0.1605 | 0.0513 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | episode_recall | 40 | 0.0570 | 0.1141 | 0.0365 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | mdt | 11 | 667.1970 | 207.3511 | 139.3003 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | far | 40 | 0.0030 | 0.0046 | 0.0015 | - | - | - | - | - | - |
| det4_s0_whddma_chddma | acc_prequential | 40 | 0.9554 | 0.0165 | 0.0053 | - | - | - | - | - | - |
| det4_s0_whddma_chddma | kappa | 40 | 0.9063 | 0.0308 | 0.0098 | - | - | - | - | - | - |
| det4_s0_whddma_chddma | f1 | 40 | 0.3889 | 0.2876 | 0.0920 | - | - | - | - | - | - |
| det4_s0_whddma_chddma | episode_recall | 40 | 0.3479 | 0.2868 | 0.0917 | - | - | - | - | - | - |
| det4_s0_whddma_chddma | mdt | 32 | 570.9529 | 227.9744 | 82.1936 | - | - | - | - | - | - |
| det4_s0_whddma_chddma | far | 40 | 0.0238 | 0.0169 | 0.0054 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 40 | 0.9255 | 0.0341 | 0.0109 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | kappa | 40 | 0.8437 | 0.0656 | 0.0210 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | f1 | 40 | 0.0447 | 0.1015 | 0.0325 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | episode_recall | 40 | 0.0261 | 0.0597 | 0.0191 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | mdt | 7 | 622.0714 | 210.8009 | 194.9584 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | far | 40 | 0.0028 | 0.0051 | 0.0016 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 40 | 0.9247 | 0.0308 | 0.0099 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 40 | 0.8417 | 0.0592 | 0.0189 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | f1 | 40 | 0.0755 | 0.1394 | 0.0446 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | episode_recall | 40 | 0.0479 | 0.0954 | 0.0305 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | mdt | 12 | 653.1944 | 244.7072 | 155.4795 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | far | 40 | 0.0040 | 0.0074 | 0.0024 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 40 | 0.9319 | 0.0265 | 0.0085 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | kappa | 40 | 0.8568 | 0.0504 | 0.0161 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | f1 | 40 | 0.1063 | 0.1631 | 0.0521 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | episode_recall | 40 | 0.0734 | 0.1221 | 0.0390 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | mdt | 15 | 576.4222 | 290.9814 | 161.1401 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | far | 40 | 0.0078 | 0.0077 | 0.0025 | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | acc_prequential | 40 | 0.9505 | 0.0130 | 0.0041 | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | kappa | 40 | 0.8951 | 0.0228 | 0.0073 | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | f1 | 40 | 0.4127 | 0.1534 | 0.0491 | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | episode_recall | 40 | 0.6627 | 0.2173 | 0.0695 | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | mdt | 40 | 452.1187 | 167.2560 | 53.4911 | - | - | - | - | - | - |
| det4_s0_wrddm_crddm | far | 40 | 0.1820 | 0.0978 | 0.0313 | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | acc_prequential | 40 | 0.9550 | 0.0164 | 0.0052 | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | kappa | 40 | 0.9053 | 0.0303 | 0.0097 | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | f1 | 40 | 0.4981 | 0.2543 | 0.0813 | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | episode_recall | 40 | 0.5195 | 0.2820 | 0.0902 | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | mdt | 38 | 618.8494 | 169.6814 | 55.7729 | - | - | - | - | - | - |
| det4_s1_wadwin_cadwin | far | 40 | 0.0382 | 0.0217 | 0.0069 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 40 | 0.9547 | 0.0158 | 0.0051 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | kappa | 40 | 0.9046 | 0.0295 | 0.0094 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | f1 | 40 | 0.4709 | 0.2782 | 0.0890 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | episode_recall | 40 | 0.4642 | 0.2920 | 0.0934 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | mdt | 35 | 637.5073 | 170.8798 | 58.6993 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | far | 40 | 0.0297 | 0.0173 | 0.0055 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 40 | 0.9529 | 0.0155 | 0.0049 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | kappa | 40 | 0.9008 | 0.0285 | 0.0091 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | f1 | 40 | 0.4236 | 0.2377 | 0.0760 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | episode_recall | 40 | 0.4149 | 0.2572 | 0.0822 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | mdt | 36 | 631.8583 | 186.9358 | 63.2500 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | far | 40 | 0.0350 | 0.0184 | 0.0059 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 40 | 0.9333 | 0.0278 | 0.0089 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | kappa | 40 | 0.8598 | 0.0533 | 0.0171 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | f1 | 40 | 0.1852 | 0.1831 | 0.0586 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | episode_recall | 40 | 0.1300 | 0.1372 | 0.0439 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | mdt | 24 | 639.6215 | 215.4974 | 90.9966 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | far | 40 | 0.0103 | 0.0095 | 0.0030 | - | - | - | - | - | - |
| det4_s1_whddma_chddma | acc_prequential | 40 | 0.9525 | 0.0161 | 0.0052 | - | - | - | - | - | - |
| det4_s1_whddma_chddma | kappa | 40 | 0.8997 | 0.0313 | 0.0100 | - | - | - | - | - | - |
| det4_s1_whddma_chddma | f1 | 40 | 0.4213 | 0.2771 | 0.0886 | - | - | - | - | - | - |
| det4_s1_whddma_chddma | episode_recall | 40 | 0.3809 | 0.2762 | 0.0883 | - | - | - | - | - | - |
| det4_s1_whddma_chddma | mdt | 35 | 607.4006 | 214.9152 | 73.8260 | - | - | - | - | - | - |
| det4_s1_whddma_chddma | far | 40 | 0.0230 | 0.0154 | 0.0049 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 40 | 0.9292 | 0.0298 | 0.0095 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | kappa | 40 | 0.8513 | 0.0571 | 0.0183 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | f1 | 40 | 0.1422 | 0.1751 | 0.0560 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | episode_recall | 40 | 0.0963 | 0.1313 | 0.0420 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | mdt | 19 | 655.8991 | 231.7578 | 111.7037 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | far | 40 | 0.0072 | 0.0085 | 0.0027 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 40 | 0.9406 | 0.0213 | 0.0068 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 40 | 0.8747 | 0.0411 | 0.0132 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | f1 | 40 | 0.2937 | 0.2161 | 0.0691 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | episode_recall | 40 | 0.2224 | 0.1747 | 0.0559 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | mdt | 30 | 671.0467 | 195.9736 | 73.1777 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | far | 40 | 0.0143 | 0.0115 | 0.0037 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 40 | 0.9380 | 0.0271 | 0.0087 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | kappa | 40 | 0.8696 | 0.0521 | 0.0167 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | f1 | 40 | 0.2750 | 0.2230 | 0.0713 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | episode_recall | 40 | 0.2126 | 0.1836 | 0.0587 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | mdt | 28 | 670.7095 | 198.8837 | 77.1190 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | far | 40 | 0.0158 | 0.0117 | 0.0038 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 40 | 0.9488 | 0.0143 | 0.0046 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | kappa | 40 | 0.8916 | 0.0260 | 0.0083 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | f1 | 40 | 0.2653 | 0.0815 | 0.0261 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | episode_recall | 40 | 0.7155 | 0.2260 | 0.0723 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | mdt | 40 | 372.1198 | 156.2011 | 49.9555 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | far | 40 | 0.5490 | 0.2311 | 0.0739 | - | - | - | - | - | - |

Generated in-repo with River SEA (100k rows, no label noise); literature uses MOA SEA (1M rows, 10% noise). Compare only against baselines re-run here.

### synthetic_multiclass (role: dev)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| det4_s0_wadwin_chddma | acc_prequential | 40 | 0.5207 | 0.0396 | 0.0127 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | kappa | 40 | 0.3555 | 0.0536 | 0.0171 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | macro_f1 | 40 | 0.5154 | 0.0413 | 0.0132 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | f1 | 40 | 0.7107 | 0.2357 | 0.0754 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | episode_recall | 40 | 0.6682 | 0.2509 | 0.0802 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | mdt | 39 | 451.9809 | 193.4558 | 62.7111 | - | - | - | - | - | - |
| det4_s0_wadwin_chddma | far | 40 | 0.0118 | 0.0098 | 0.0031 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | acc_prequential | 40 | 0.5257 | 0.0468 | 0.0150 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | kappa | 40 | 0.3626 | 0.0623 | 0.0199 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | macro_f1 | 40 | 0.5203 | 0.0474 | 0.0152 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | f1 | 40 | 0.7281 | 0.2493 | 0.0797 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | episode_recall | 40 | 0.6785 | 0.2569 | 0.0822 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | mdt | 40 | 559.3199 | 180.7598 | 57.8098 | - | - | - | - | - | - |
| det4_s0_wadwin_crddm | far | 40 | 0.0110 | 0.0113 | 0.0036 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | acc_prequential | 40 | 0.5992 | 0.0329 | 0.0105 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | kappa | 40 | 0.4622 | 0.0434 | 0.0139 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | macro_f1 | 40 | 0.5965 | 0.0319 | 0.0102 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | f1 | 40 | 0.0904 | 0.1472 | 0.0471 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | episode_recall | 40 | 0.0514 | 0.0851 | 0.0272 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | mdt | 12 | 508.3750 | 210.4496 | 133.7133 | - | - | - | - | - | - |
| det4_s0_whddma_cadwin | far | 40 | 0.0008 | 0.0027 | 0.0009 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | acc_prequential | 40 | 0.6004 | 0.0306 | 0.0098 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | kappa | 40 | 0.4639 | 0.0404 | 0.0129 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | macro_f1 | 40 | 0.5976 | 0.0297 | 0.0095 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | f1 | 40 | 0.0592 | 0.1068 | 0.0342 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | episode_recall | 40 | 0.0345 | 0.0625 | 0.0200 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | mdt | 10 | 601.6500 | 229.9534 | 164.4987 | - | - | - | - | - | - |
| det4_s0_whddma_crddm | far | 40 | 0.0010 | 0.0030 | 0.0010 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | acc_prequential | 40 | 0.5984 | 0.0276 | 0.0088 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | kappa | 40 | 0.4612 | 0.0359 | 0.0115 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | macro_f1 | 40 | 0.5959 | 0.0264 | 0.0084 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | f1 | 40 | 0.2388 | 0.2079 | 0.0665 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | episode_recall | 40 | 0.1602 | 0.1570 | 0.0502 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | mdt | 28 | 531.9821 | 228.9485 | 88.7770 | - | - | - | - | - | - |
| det4_s0_wrddm_cadwin | far | 40 | 0.0040 | 0.0063 | 0.0020 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | acc_prequential | 40 | 0.6051 | 0.0310 | 0.0099 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | kappa | 40 | 0.4701 | 0.0409 | 0.0131 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | macro_f1 | 40 | 0.6027 | 0.0304 | 0.0097 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | f1 | 40 | 0.3731 | 0.2853 | 0.0913 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | episode_recall | 40 | 0.2878 | 0.2445 | 0.0782 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | mdt | 30 | 487.5984 | 214.5259 | 80.1053 | - | - | - | - | - | - |
| det4_s0_wrddm_chddma | far | 40 | 0.0055 | 0.0075 | 0.0024 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | acc_prequential | 40 | 0.6285 | 0.0306 | 0.0098 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | kappa | 40 | 0.5018 | 0.0400 | 0.0128 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | macro_f1 | 40 | 0.6262 | 0.0301 | 0.0096 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | f1 | 40 | 0.8178 | 0.1649 | 0.0527 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | episode_recall | 40 | 0.8034 | 0.1784 | 0.0571 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | mdt | 40 | 554.2447 | 178.2173 | 56.9966 | - | - | - | - | - | - |
| det4_s1_wadwin_chddma | far | 40 | 0.0128 | 0.0147 | 0.0047 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | acc_prequential | 40 | 0.6269 | 0.0280 | 0.0090 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | kappa | 40 | 0.4997 | 0.0369 | 0.0118 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | macro_f1 | 40 | 0.6246 | 0.0274 | 0.0088 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | f1 | 40 | 0.8058 | 0.1443 | 0.0461 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | episode_recall | 40 | 0.7907 | 0.1513 | 0.0484 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | mdt | 40 | 568.4631 | 193.2402 | 61.8012 | - | - | - | - | - | - |
| det4_s1_wadwin_crddm | far | 40 | 0.0140 | 0.0146 | 0.0047 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | acc_prequential | 40 | 0.6154 | 0.0269 | 0.0086 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | kappa | 40 | 0.4843 | 0.0353 | 0.0113 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | macro_f1 | 40 | 0.6132 | 0.0263 | 0.0084 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | f1 | 40 | 0.4663 | 0.2228 | 0.0713 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | episode_recall | 40 | 0.3427 | 0.1928 | 0.0616 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | mdt | 37 | 560.1518 | 227.1069 | 75.7212 | - | - | - | - | - | - |
| det4_s1_whddma_cadwin | far | 40 | 0.0047 | 0.0078 | 0.0025 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | acc_prequential | 40 | 0.6139 | 0.0247 | 0.0079 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | kappa | 40 | 0.4821 | 0.0324 | 0.0104 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | macro_f1 | 40 | 0.6113 | 0.0238 | 0.0076 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | f1 | 40 | 0.4451 | 0.2236 | 0.0715 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | episode_recall | 40 | 0.3345 | 0.1964 | 0.0628 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | mdt | 36 | 516.2880 | 235.0645 | 79.5344 | - | - | - | - | - | - |
| det4_s1_whddma_crddm | far | 40 | 0.0068 | 0.0105 | 0.0033 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | acc_prequential | 40 | 0.6172 | 0.0249 | 0.0080 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | kappa | 40 | 0.4866 | 0.0322 | 0.0103 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | macro_f1 | 40 | 0.6146 | 0.0238 | 0.0076 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | f1 | 40 | 0.5502 | 0.2440 | 0.0780 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | episode_recall | 40 | 0.4546 | 0.2543 | 0.0813 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | mdt | 38 | 526.9461 | 207.1742 | 68.0965 | - | - | - | - | - | - |
| det4_s1_wrddm_cadwin | far | 40 | 0.0083 | 0.0084 | 0.0027 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | acc_prequential | 40 | 0.6192 | 0.0255 | 0.0082 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | kappa | 40 | 0.4892 | 0.0335 | 0.0107 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | macro_f1 | 40 | 0.6168 | 0.0249 | 0.0080 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | f1 | 40 | 0.5831 | 0.2212 | 0.0707 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | episode_recall | 40 | 0.4979 | 0.2371 | 0.0758 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | mdt | 39 | 476.5801 | 189.7324 | 61.5041 | - | - | - | - | - | - |
| det4_s1_wrddm_chddma | far | 40 | 0.0112 | 0.0130 | 0.0042 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | acc_prequential | 40 | 0.6109 | 0.0283 | 0.0090 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | kappa | 40 | 0.4781 | 0.0378 | 0.0121 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | macro_f1 | 40 | 0.6086 | 0.0277 | 0.0089 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | f1 | 40 | 0.5583 | 0.1037 | 0.0332 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | episode_recall | 40 | 0.9036 | 0.1240 | 0.0397 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | mdt | 40 | 365.7073 | 139.3657 | 44.5713 | - | - | - | - | - | - |
| det4_s1_wrddm_crddm | far | 40 | 0.1742 | 0.0746 | 0.0239 | - | - | - | - | - | - |

In-repo RandomRBF4; compare only against baselines re-run here.

### Ranking across datasets on `acc_prequential`

Blocks: 8; presets: 18. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| det4_s1_wadwin_chddma | 6.81 | 0.8123 |
| det4_s1_whddma_chddma | 6.88 | 0.8287 |
| det4_s0_whddma_chddma | 7.25 | 0.8313 |
| det4_s0_wrddm_crddm | 7.31 | 0.8270 |
| det4_s1_wrddm_cadwin | 7.31 | 0.8056 |
| det4_s1_wrddm_crddm | 7.44 | 0.8253 |
| det4_s1_wadwin_cadwin | 8.06 | 0.8235 |
| det4_s1_whddma_cadwin | 8.44 | 0.8017 |
| det4_s1_wadwin_crddm | 8.56 | 0.8131 |
| det4_s0_wadwin_cadwin | 9.12 | 0.8063 |
| det4_s1_wrddm_chddma | 9.94 | 0.8032 |
| det4_s1_whddma_crddm | 10.19 | 0.7956 |
| det4_s0_whddma_crddm | 11.19 | 0.7793 |
| det4_s0_wrddm_chddma | 11.38 | 0.7906 |
| det4_s0_whddma_cadwin | 12.19 | 0.7730 |
| det4_s0_wadwin_crddm | 12.50 | 0.7918 |
| det4_s0_wrddm_cadwin | 13.06 | 0.7621 |
| det4_s0_wadwin_chddma | 13.38 | 0.7891 |

Friedman chi2 = 24.872, p = 0.09761.
Caution: only 8 blocks; Friedman / Nemenyi have little power below about 10.

### Ranking across datasets on `acc_window1000_mean`

Blocks: 5; presets: 13. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| det4_s1_wrddm_crddm | 1.40 | 0.6370 |
| det4_s1_wadwin_chddma | 3.20 | 0.6191 |
| det4_s1_wadwin_crddm | 3.60 | 0.6213 |
| det4_s1_whddma_crddm | 4.80 | 0.6069 |
| det4_s1_wrddm_chddma | 4.80 | 0.6149 |
| det4_s1_whddma_cadwin | 5.80 | 0.5997 |
| det4_s1_wrddm_cadwin | 5.80 | 0.5964 |
| det4_s0_wadwin_crddm | 8.40 | 0.5683 |
| det4_s0_wadwin_chddma | 10.00 | 0.5565 |
| det4_s0_wrddm_chddma | 10.00 | 0.5491 |
| det4_s0_whddma_crddm | 11.00 | 0.5321 |
| det4_s0_wrddm_cadwin | 11.00 | 0.5242 |
| det4_s0_whddma_cadwin | 11.20 | 0.5198 |

Friedman chi2 = 45.996, p = 6.95e-06.
Caution: only 5 blocks; Friedman / Nemenyi have little power below about 10.

### Ranking across datasets on `kappa_t`

Blocks: 6; presets: 18. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| det4_s0_wrddm_crddm | 6.17 | -0.3729 |
| det4_s1_whddma_chddma | 6.17 | -0.3296 |
| det4_s1_wrddm_crddm | 6.17 | -0.4143 |
| det4_s0_whddma_chddma | 6.67 | -0.2428 |
| det4_s1_wadwin_chddma | 7.00 | -0.6088 |
| det4_s1_wrddm_cadwin | 7.33 | -0.6292 |
| det4_s1_wadwin_cadwin | 8.50 | -0.4229 |
| det4_s1_whddma_cadwin | 8.50 | -0.6384 |
| det4_s1_wadwin_crddm | 9.17 | -0.6068 |
| det4_s1_whddma_crddm | 10.50 | -0.6613 |
| det4_s1_wrddm_chddma | 10.67 | -0.6532 |
| det4_s0_wadwin_cadwin | 10.83 | -0.6326 |
| det4_s0_whddma_crddm | 11.17 | -0.8569 |
| det4_s0_wadwin_crddm | 11.67 | -0.7730 |
| det4_s0_wadwin_chddma | 12.33 | -0.8155 |
| det4_s0_wrddm_cadwin | 12.50 | -0.9146 |
| det4_s0_whddma_cadwin | 12.67 | -0.8925 |
| det4_s0_wrddm_chddma | 13.00 | -0.8239 |

Friedman chi2 = 22.175, p = 0.1781.
Caution: only 6 blocks; Friedman / Nemenyi have little power below about 10.

## Injected drift detection (pooled over trials)

tp/fp/fn are summed over all trials of a cell before precision/recall/F1, as in Cerqueira et al.; `far_cerqueira` is their FAR (summed false alarms / one stream length x 1000), `far_per_run` the per-stream average. `sota_f1` is the best of their 14 detectors for that cell.

### injected_ai4i2020

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 1.1651 | - | - | - |
| abrupt/class_prior | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4208 | - | - | - |
| abrupt/class_prior | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1009 | - | - | - |
| abrupt/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2825 | - | - | - |
| abrupt/class_prior | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4205 | - | - | - |
| abrupt/class_prior | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/class_prior | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2557 | - | - | - |
| abrupt/class_prior | det4_s0_wrddm_crddm | 10 | 0.2381 | 0.1613 | 0.4545 | 0.4000 | 165.0000 | 2.9730 | - | - | - |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 10 | 0.3000 | 0.3000 | 0.3000 | 0.3000 | 395.6667 | 0.7443 | - | - | - |
| abrupt/class_prior | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.5588 | - | - | - |
| abrupt/class_prior | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.5588 | - | - | - |
| abrupt/class_prior | det4_s1_whddma_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 450.0000 | 0.0000 | - | - | - |
| abrupt/class_prior | det4_s1_whddma_chddma | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 313.0000 | 0.4043 | - | - | - |
| abrupt/class_prior | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/class_prior | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1380 | - | - | - |
| abrupt/class_prior | det4_s1_wrddm_crddm | 10 | 0.1455 | 0.0825 | 0.6154 | 0.5000 | 48.2000 | 10.0904 | - | - | - |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3768 | - | - | - |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 2.2569 | - | - | - |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2459 | - | - | - |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.1143 | 0.0690 | 0.3333 | 0.2000 | 82.5000 | 6.4363 | - | - | - |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2000 | - | - | - |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 98.0000 | 0.0000 | - | - | - |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 4.0000 | 0.0000 | - | - | - |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 1.6000 | - | - | - |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2000 | - | - | - |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.1053 | 0.0615 | 0.3636 | 0.3000 | 174.0000 | 6.1000 | - | - | - |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 10 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 58.8333 | 0.4000 | - | - | - |
| abrupt/label_swap | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s0_wadwin_crddm | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 16.0000 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s0_whddma_chddma | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 26.0000 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s0_wrddm_chddma | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 33.0000 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s0_wrddm_crddm | 10 | 0.3158 | 0.2143 | 0.6000 | 0.6000 | 19.1667 | 2.2000 | - | - | - |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 10 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 53.5000 | 0.4000 | - | - | - |
| abrupt/label_swap | det4_s1_wadwin_chddma | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 58.8333 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s1_wadwin_crddm | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 50.6667 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s1_whddma_cadwin | 10 | 0.6667 | 1.0000 | 0.5000 | 0.5000 | 51.4000 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s1_whddma_chddma | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 23.8333 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s1_whddma_crddm | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 54.2500 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 10 | 0.6667 | 1.0000 | 0.5000 | 0.5000 | 51.4000 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s1_wrddm_chddma | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 54.2500 | 0.0000 | - | - | - |
| abrupt/label_swap | det4_s1_wrddm_crddm | 10 | 0.1224 | 0.0682 | 0.6000 | 0.6000 | 8.5000 | 8.2000 | - | - | - |
| gradual/class_prior | det4_s0_wadwin_cadwin | 10 | 0.1053 | 0.1111 | 0.1000 | 0.1000 | 418.0000 | 0.9123 | - | - | - |
| gradual/class_prior | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4198 | - | - | - |
| gradual/class_prior | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1263 | - | - | - |
| gradual/class_prior | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4198 | - | - | - |
| gradual/class_prior | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/class_prior | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/class_prior | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1496 | - | - | - |
| gradual/class_prior | det4_s0_wrddm_crddm | 10 | 0.1818 | 0.1163 | 0.4167 | 0.3000 | 309.3333 | 4.6074 | - | - | - |
| gradual/class_prior | det4_s1_wadwin_cadwin | 10 | 0.1053 | 0.1111 | 0.1000 | 0.1000 | 418.0000 | 0.9291 | - | - | - |
| gradual/class_prior | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.6466 | - | - | - |
| gradual/class_prior | det4_s1_wadwin_crddm | 10 | 0.1250 | 0.1667 | 0.1000 | 0.1000 | 424.0000 | 0.6466 | - | - | - |
| gradual/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1323 | - | - | - |
| gradual/class_prior | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.5460 | - | - | - |
| gradual/class_prior | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1323 | - | - | - |
| gradual/class_prior | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1323 | - | - | - |
| gradual/class_prior | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2819 | - | - | - |
| gradual/class_prior | det4_s1_wrddm_crddm | 10 | 0.0952 | 0.0532 | 0.4545 | 0.4000 | 380.5000 | 10.3611 | - | - | - |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1237 | - | - | - |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2298 | - | - | - |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 2.5970 | - | - | - |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.0759 | 0.0441 | 0.2727 | 0.2000 | 281.0000 | 7.7556 | - | - | - |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.0645 | 0.0476 | 0.1000 | 0.1000 | 442.0000 | 2.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.0899 | 0.0513 | 0.3636 | 0.3000 | 261.6667 | 7.4000 | - | - | - |
| gradual/label_swap | det4_s0_wadwin_cadwin | 10 | 0.5185 | 0.5000 | 0.5385 | 0.4000 | 213.0000 | 0.7000 | - | - | - |
| gradual/label_swap | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| gradual/label_swap | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_whddma_chddma | 10 | 0.6667 | 1.0000 | 0.5000 | 0.4000 | 156.7500 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_whddma_crddm | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 294.0000 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_wrddm_chddma | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 302.0000 | 0.1000 | - | - | - |
| gradual/label_swap | det4_s0_wrddm_crddm | 10 | 0.4211 | 0.3333 | 0.5714 | 0.4000 | 106.7500 | 1.6000 | - | - | - |
| gradual/label_swap | det4_s1_wadwin_cadwin | 10 | 0.5385 | 0.5385 | 0.5385 | 0.4000 | 213.0000 | 0.6000 | - | - | - |
| gradual/label_swap | det4_s1_wadwin_chddma | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 213.0000 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s1_wadwin_crddm | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 213.0000 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s1_whddma_cadwin | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 213.0000 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s1_whddma_chddma | 10 | 0.6667 | 0.8000 | 0.5714 | 0.4000 | 161.5000 | 0.2000 | - | - | - |
| gradual/label_swap | det4_s1_whddma_crddm | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 209.7500 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s1_wrddm_cadwin | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 213.0000 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s1_wrddm_chddma | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 213.0000 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s1_wrddm_crddm | 10 | 0.2750 | 0.1746 | 0.6471 | 0.4000 | 108.2500 | 5.2000 | - | - | - |

### injected_airlines

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 10 | 0.3590 | 0.2414 | 0.7000 | 0.7000 | 470.4286 | 0.2542 | - | - | - |
| abrupt/class_prior | det4_s0_wadwin_chddma | 10 | 0.1053 | 0.1111 | 0.1000 | 0.1000 | 561.0000 | 0.0945 | - | - | - |
| abrupt/class_prior | det4_s0_wadwin_crddm | 10 | 0.3478 | 0.3077 | 0.4000 | 0.4000 | 298.7500 | 0.1052 | - | - | - |
| abrupt/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/class_prior | det4_s0_whddma_chddma | 10 | 0.3158 | 0.2222 | 0.5455 | 0.5000 | 140.2000 | 0.2500 | - | - | - |
| abrupt/class_prior | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 504.0000 | 0.0121 | - | - | - |
| abrupt/class_prior | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0479 | - | - | - |
| abrupt/class_prior | det4_s0_wrddm_crddm | 10 | 0.2791 | 0.1875 | 0.5455 | 0.5000 | 273.6000 | 0.3018 | - | - | - |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 10 | 0.4800 | 0.4000 | 0.6000 | 0.6000 | 842.0000 | 0.1020 | - | - | - |
| abrupt/class_prior | det4_s1_wadwin_chddma | 10 | 0.4706 | 0.5714 | 0.4000 | 0.4000 | 903.7500 | 0.0340 | - | - | - |
| abrupt/class_prior | det4_s1_wadwin_crddm | 10 | 0.4706 | 0.5714 | 0.4000 | 0.4000 | 737.5000 | 0.0340 | - | - | - |
| abrupt/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0340 | - | - | - |
| abrupt/class_prior | det4_s1_whddma_chddma | 10 | 0.4286 | 0.3529 | 0.5455 | 0.5000 | 260.0000 | 0.1298 | - | - | - |
| abrupt/class_prior | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0460 | - | - | - |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 941.0000 | 0.0340 | - | - | - |
| abrupt/class_prior | det4_s1_wrddm_chddma | 10 | 0.2353 | 0.2857 | 0.2000 | 0.2000 | 432.5000 | 0.0571 | - | - | - |
| abrupt/class_prior | det4_s1_wrddm_crddm | 10 | 0.1519 | 0.0882 | 0.5455 | 0.5000 | 445.0000 | 0.7321 | - | - | - |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2251 | - | - | - |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0993 | - | - | - |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0743 | - | - | - |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1391 | - | - | - |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0250 | - | - | - |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3797 | - | - | - |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0887 | - | - | - |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0122 | - | - | - |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0483 | - | - | - |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0122 | - | - | - |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1119 | - | - | - |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0122 | - | - | - |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0122 | - | - | - |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0122 | - | - | - |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.1000 | 0.0588 | 0.3333 | 0.2000 | 266.0000 | 0.7928 | - | - | - |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3600 | - | - | - |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1300 | - | - | - |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 10 | 0.0606 | 0.0435 | 0.1000 | 0.1000 | 32.0000 | 0.2200 | - | - | - |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0300 | - | - | - |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0400 | - | - | - |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.0857 | 0.0500 | 0.3000 | 0.3000 | 466.0000 | 0.5700 | - | - | - |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1400 | - | - | - |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.2353 | 0.2857 | 0.2000 | 0.2000 | 993.5000 | 0.0500 | - | - | - |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0500 | - | - | - |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 10 | 0.2727 | 0.2500 | 0.3000 | 0.3000 | 919.3333 | 0.0900 | - | - | - |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0400 | - | - | - |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.1333 | 0.2000 | 0.1000 | 0.1000 | 999.0000 | 0.0400 | - | - | - |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.0556 | 0.0301 | 0.3636 | 0.3000 | 470.6667 | 1.2900 | - | - | - |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 10 | 0.5789 | 0.4074 | 1.0000 | 1.0000 | 548.7000 | 0.1600 | - | - | - |
| abrupt/label_swap | det4_s0_wadwin_chddma | 10 | 0.3333 | 0.3750 | 0.3000 | 0.3000 | 129.0000 | 0.0500 | - | - | - |
| abrupt/label_swap | det4_s0_wadwin_crddm | 10 | 0.3158 | 0.3333 | 0.3000 | 0.3000 | 185.6667 | 0.0600 | - | - | - |
| abrupt/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| abrupt/label_swap | det4_s0_whddma_chddma | 10 | 0.2857 | 0.2222 | 0.4000 | 0.4000 | 46.0000 | 0.1400 | - | - | - |
| abrupt/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0200 | - | - | - |
| abrupt/label_swap | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| abrupt/label_swap | det4_s0_wrddm_crddm | 10 | 0.1071 | 0.0652 | 0.3000 | 0.3000 | 118.0000 | 0.4300 | - | - | - |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 10 | 0.6429 | 0.5000 | 0.9000 | 0.9000 | 608.4444 | 0.0900 | - | - | - |
| abrupt/label_swap | det4_s1_wadwin_chddma | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 241.0000 | 0.0300 | - | - | - |
| abrupt/label_swap | det4_s1_wadwin_crddm | 10 | 0.2500 | 0.3333 | 0.2000 | 0.2000 | 298.0000 | 0.0400 | - | - | - |
| abrupt/label_swap | det4_s1_whddma_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 241.0000 | 0.0100 | - | - | - |
| abrupt/label_swap | det4_s1_whddma_chddma | 10 | 0.3200 | 0.2667 | 0.4000 | 0.4000 | 174.5000 | 0.1100 | - | - | - |
| abrupt/label_swap | det4_s1_whddma_crddm | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 241.0000 | 0.0100 | - | - | - |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 241.0000 | 0.0100 | - | - | - |
| abrupt/label_swap | det4_s1_wrddm_chddma | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 151.5000 | 0.0100 | - | - | - |
| abrupt/label_swap | det4_s1_wrddm_crddm | 10 | 0.0667 | 0.0364 | 0.4000 | 0.4000 | 92.5000 | 1.0600 | - | - | - |
| gradual/class_prior | det4_s0_wadwin_cadwin | 10 | 0.1143 | 0.0800 | 0.2000 | 0.2000 | 895.0000 | 0.2627 | - | - | - |
| gradual/class_prior | det4_s0_wadwin_chddma | 10 | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 785.8000 | 0.0560 | - | - | - |
| gradual/class_prior | det4_s0_wadwin_crddm | 10 | 0.2222 | 0.2500 | 0.2000 | 0.2000 | 766.0000 | 0.0678 | - | - | - |
| gradual/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/class_prior | det4_s0_whddma_chddma | 10 | 0.5714 | 0.5455 | 0.6000 | 0.6000 | 722.3333 | 0.0570 | - | - | - |
| gradual/class_prior | det4_s0_whddma_crddm | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 802.0000 | 0.0000 | - | - | - |
| gradual/class_prior | det4_s0_wrddm_cadwin | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 881.0000 | 0.0229 | - | - | - |
| gradual/class_prior | det4_s0_wrddm_chddma | 10 | 0.4444 | 0.5000 | 0.4000 | 0.4000 | 726.5000 | 0.0466 | - | - | - |
| gradual/class_prior | det4_s0_wrddm_crddm | 10 | 0.3830 | 0.2647 | 0.6923 | 0.6000 | 750.1667 | 0.2866 | - | - | - |
| gradual/class_prior | det4_s1_wadwin_cadwin | 10 | 0.2500 | 0.2143 | 0.3000 | 0.3000 | 873.3333 | 0.1254 | - | - | - |
| gradual/class_prior | det4_s1_wadwin_chddma | 10 | 0.1176 | 0.1429 | 0.1000 | 0.1000 | 773.0000 | 0.0696 | - | - | - |
| gradual/class_prior | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0922 | - | - | - |
| gradual/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0229 | - | - | - |
| gradual/class_prior | det4_s1_whddma_chddma | 10 | 0.6316 | 0.6667 | 0.6000 | 0.6000 | 691.6667 | 0.0351 | - | - | - |
| gradual/class_prior | det4_s1_whddma_crddm | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 564.0000 | 0.0223 | - | - | - |
| gradual/class_prior | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0692 | - | - | - |
| gradual/class_prior | det4_s1_wrddm_chddma | 10 | 0.2353 | 0.2857 | 0.2000 | 0.2000 | 597.0000 | 0.0582 | - | - | - |
| gradual/class_prior | det4_s1_wrddm_crddm | 10 | 0.1368 | 0.0777 | 0.5714 | 0.4000 | 519.0000 | 1.0996 | - | - | - |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2692 | - | - | - |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1184 | - | - | - |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1177 | - | - | - |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1288 | - | - | - |
| gradual/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0711 | - | - | - |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0112 | - | - | - |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0122 | - | - | - |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3650 | - | - | - |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1517 | - | - | - |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0465 | - | - | - |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0346 | - | - | - |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0243 | - | - | - |
| gradual/feature_filtering | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1062 | - | - | - |
| gradual/feature_filtering | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0473 | - | - | - |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.0187 | 0.0103 | 0.1000 | 0.1000 | 594.0000 | 1.1108 | - | - | - |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2500 | - | - | - |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0900 | - | - | - |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | - | - | - |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0200 | - | - | - |
| gradual/feature_permutation | det4_s0_whddma_chddma | 10 | 0.0588 | 0.0417 | 0.1000 | 0.1000 | 958.0000 | 0.2300 | - | - | - |
| gradual/feature_permutation | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 741.0000 | 0.0100 | - | - | - |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0500 | - | - | - |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3500 | - | - | - |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0400 | - | - | - |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0200 | - | - | - |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/feature_permutation | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1900 | - | - | - |
| gradual/feature_permutation | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0200 | - | - | - |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | - | - | - |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0200 | - | - | - |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.7200 | - | - | - |
| gradual/label_swap | det4_s0_wadwin_cadwin | 10 | 0.2222 | 0.1538 | 0.4000 | 0.4000 | 841.2500 | 0.2200 | - | - | - |
| gradual/label_swap | det4_s0_wadwin_chddma | 10 | 0.2353 | 0.2857 | 0.2000 | 0.2000 | 267.0000 | 0.0500 | - | - | - |
| gradual/label_swap | det4_s0_wadwin_crddm | 10 | 0.2727 | 0.2500 | 0.3000 | 0.3000 | 360.6667 | 0.0900 | - | - | - |
| gradual/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_whddma_chddma | 10 | 0.4138 | 0.3333 | 0.5455 | 0.5000 | 429.4000 | 0.1200 | - | - | - |
| gradual/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_wrddm_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 918.0000 | 0.0000 | - | - | - |
| gradual/label_swap | det4_s0_wrddm_chddma | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 374.0000 | 0.0100 | - | - | - |
| gradual/label_swap | det4_s0_wrddm_crddm | 10 | 0.1111 | 0.0625 | 0.5000 | 0.5000 | 544.2000 | 0.7500 | - | - | - |
| gradual/label_swap | det4_s1_wadwin_cadwin | 10 | 0.5600 | 0.5000 | 0.6364 | 0.6000 | 769.8333 | 0.0700 | - | - | - |
| gradual/label_swap | det4_s1_wadwin_chddma | 10 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 948.0000 | 0.0300 | - | - | - |
| gradual/label_swap | det4_s1_wadwin_crddm | 10 | 0.4000 | 0.6000 | 0.3000 | 0.3000 | 947.6667 | 0.0200 | - | - | - |
| gradual/label_swap | det4_s1_whddma_cadwin | 10 | 0.2857 | 0.5000 | 0.2000 | 0.2000 | 948.0000 | 0.0200 | - | - | - |
| gradual/label_swap | det4_s1_whddma_chddma | 10 | 0.5385 | 0.5000 | 0.5833 | 0.5000 | 478.6000 | 0.0700 | - | - | - |
| gradual/label_swap | det4_s1_whddma_crddm | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 992.0000 | 0.0200 | - | - | - |
| gradual/label_swap | det4_s1_wrddm_cadwin | 10 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 875.0000 | 0.0300 | - | - | - |
| gradual/label_swap | det4_s1_wrddm_chddma | 10 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 657.0000 | 0.0300 | - | - | - |
| gradual/label_swap | det4_s1_wrddm_crddm | 10 | 0.2174 | 0.1299 | 0.6667 | 0.5000 | 443.8000 | 0.6700 | - | - | - |

### injected_covertype

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 10 | 0.2041 | 0.1316 | 0.4545 | 0.4000 | 1300.0000 | 0.3481 | 0.1330 | ABCD | 0.0711 |
| abrupt/class_prior | det4_s0_wadwin_chddma | 10 | 0.2222 | 0.2500 | 0.2000 | 0.2000 | 142.0000 | 0.0623 | 0.1330 | ABCD | 0.0892 |
| abrupt/class_prior | det4_s0_wadwin_crddm | 10 | 0.1818 | 0.1667 | 0.2000 | 0.2000 | 874.5000 | 0.1051 | 0.1330 | ABCD | 0.0488 |
| abrupt/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1330 | ABCD | -0.1330 |
| abrupt/class_prior | det4_s0_whddma_chddma | 10 | 0.1333 | 0.1000 | 0.2000 | 0.2000 | 89.0000 | 0.2026 | 0.1330 | ABCD | 0.0003 |
| abrupt/class_prior | det4_s0_whddma_crddm | 10 | 0.3077 | 1.0000 | 0.1818 | 0.1000 | 319.0000 | 0.0000 | 0.1330 | ABCD | 0.1747 |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0123 | 0.1330 | ABCD | -0.1330 |
| abrupt/class_prior | det4_s0_wrddm_chddma | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 247.0000 | 0.0205 | 0.1330 | ABCD | 0.0208 |
| abrupt/class_prior | det4_s0_wrddm_crddm | 10 | 0.1579 | 0.1111 | 0.2727 | 0.2000 | 323.5000 | 0.2537 | 0.1330 | ABCD | 0.0249 |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 10 | 0.3810 | 0.3636 | 0.4000 | 0.4000 | 1122.2500 | 0.0793 | 0.1330 | ABCD | 0.2480 |
| abrupt/class_prior | det4_s1_wadwin_chddma | 10 | 0.1250 | 0.1667 | 0.1000 | 0.1000 | 1008.0000 | 0.0588 | 0.1330 | ABCD | -0.0080 |
| abrupt/class_prior | det4_s1_wadwin_crddm | 10 | 0.1250 | 0.1667 | 0.1000 | 0.1000 | 1084.0000 | 0.0588 | 0.1330 | ABCD | -0.0080 |
| abrupt/class_prior | det4_s1_whddma_cadwin | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 1020.0000 | 0.0220 | 0.1330 | ABCD | 0.0208 |
| abrupt/class_prior | det4_s1_whddma_chddma | 10 | 0.2069 | 0.1667 | 0.2727 | 0.2000 | 597.5000 | 0.1668 | 0.1330 | ABCD | 0.0739 |
| abrupt/class_prior | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0220 | 0.1330 | ABCD | -0.1330 |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0548 | 0.1330 | ABCD | -0.1330 |
| abrupt/class_prior | det4_s1_wrddm_chddma | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 215.0000 | 0.0321 | 0.1330 | ABCD | 0.0099 |
| abrupt/class_prior | det4_s1_wrddm_crddm | 10 | 0.0667 | 0.0370 | 0.3333 | 0.2000 | 295.0000 | 1.1022 | 0.1330 | ABCD | -0.0663 |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.1111 | 0.0769 | 0.2000 | 0.2000 | 784.0000 | 0.2439 | 0.0920 | STEPD | 0.0191 |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0870 | 0.0769 | 0.1000 | 0.1000 | 1655.0000 | 0.1201 | 0.0920 | STEPD | -0.0050 |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.1905 | 0.1818 | 0.2000 | 0.2000 | 639.0000 | 0.0902 | 0.0920 | STEPD | 0.0985 |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 10 | 0.0769 | 0.0625 | 0.1000 | 0.1000 | 2042.0000 | 0.1563 | 0.0920 | STEPD | -0.0151 |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0111 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0588 | 0.0417 | 0.1000 | 0.1000 | 1364.0000 | 0.2343 | 0.0920 | STEPD | -0.0332 |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 2301.0000 | 0.0215 | 0.0920 | STEPD | 0.0618 |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 10 | 0.1053 | 0.1111 | 0.1000 | 0.1000 | 1338.0000 | 0.0811 | 0.0920 | STEPD | 0.0133 |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 814.0000 | 0.0201 | 0.0920 | STEPD | 0.0618 |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 2301.0000 | 0.0000 | 0.0920 | STEPD | 0.0898 |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0211 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.0630 | 0.0351 | 0.3077 | 0.1000 | 878.0000 | 1.1045 | 0.0920 | STEPD | -0.0290 |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.3500 | 0.2333 | 0.7000 | 0.7000 | 704.0000 | 0.2300 | 1.0000 | ABCD(X) | -0.6500 |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.5926 | 0.5000 | 0.7273 | 0.7000 | 195.0000 | 0.0800 | 1.0000 | ABCD(X) | -0.4074 |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.5600 | 0.4667 | 0.7000 | 0.7000 | 539.4286 | 0.0800 | 1.0000 | ABCD(X) | -0.4400 |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 10 | 0.5405 | 0.3704 | 1.0000 | 1.0000 | 262.5000 | 0.1700 | 1.0000 | ABCD(X) | -0.4595 |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.3333 | 1.0000 | 0.2000 | 0.2000 | 620.5000 | 0.0000 | 1.0000 | ABCD(X) | -0.6667 |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.5490 | 0.3784 | 1.0000 | 1.0000 | 397.9000 | 0.2300 | 1.0000 | ABCD(X) | -0.4510 |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.7000 | 0.7000 | 0.7000 | 0.7000 | 733.2857 | 0.0300 | 1.0000 | ABCD(X) | -0.3000 |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.7778 | 0.8750 | 0.7000 | 0.7000 | 753.4286 | 0.0100 | 1.0000 | ABCD(X) | -0.2222 |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.7000 | 0.7000 | 0.7000 | 0.7000 | 742.8571 | 0.0300 | 1.0000 | ABCD(X) | -0.3000 |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.5333 | 0.8000 | 0.4000 | 0.4000 | 451.2500 | 0.0100 | 1.0000 | ABCD(X) | -0.4667 |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 10 | 0.5000 | 0.3810 | 0.7273 | 0.7000 | 256.1429 | 0.1300 | 1.0000 | ABCD(X) | -0.5000 |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 10 | 0.5000 | 0.6667 | 0.4000 | 0.4000 | 310.0000 | 0.0200 | 1.0000 | ABCD(X) | -0.5000 |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.4706 | 0.5714 | 0.4000 | 0.4000 | 451.2500 | 0.0300 | 1.0000 | ABCD(X) | -0.5294 |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.3158 | 0.3333 | 0.3000 | 0.3000 | 245.3333 | 0.0600 | 1.0000 | ABCD(X) | -0.6842 |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.1887 | 0.1056 | 0.8824 | 0.8000 | 372.7500 | 1.2700 | 1.0000 | ABCD(X) | -0.8113 |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 10 | 0.0500 | 0.0333 | 0.1000 | 0.1000 | 318.0000 | 0.2900 | 0.1720 | SEED | -0.1220 |
| abrupt/label_swap | det4_s0_wadwin_chddma | 10 | 0.1739 | 0.1538 | 0.2000 | 0.2000 | 1258.0000 | 0.1100 | 0.1720 | SEED | 0.0019 |
| abrupt/label_swap | det4_s0_wadwin_crddm | 10 | 0.0870 | 0.0769 | 0.1000 | 0.1000 | 1054.0000 | 0.1200 | 0.1720 | SEED | -0.0850 |
| abrupt/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1720 | SEED | -0.1720 |
| abrupt/label_swap | det4_s0_whddma_chddma | 10 | 0.0769 | 0.0625 | 0.1000 | 0.1000 | 10.0000 | 0.1500 | 0.1720 | SEED | -0.0951 |
| abrupt/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.1720 | SEED | -0.1720 |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1720 | SEED | -0.1720 |
| abrupt/label_swap | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.1720 | SEED | -0.1720 |
| abrupt/label_swap | det4_s0_wrddm_crddm | 10 | 0.0571 | 0.0400 | 0.1000 | 0.1000 | 125.0000 | 0.2400 | 0.1720 | SEED | -0.1149 |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 10 | 0.1111 | 0.1250 | 0.1000 | 0.1000 | 81.0000 | 0.0700 | 0.1720 | SEED | -0.0609 |
| abrupt/label_swap | det4_s1_wadwin_chddma | 10 | 0.1250 | 0.1667 | 0.1000 | 0.1000 | 382.0000 | 0.0500 | 0.1720 | SEED | -0.0470 |
| abrupt/label_swap | det4_s1_wadwin_crddm | 10 | 0.1111 | 0.1250 | 0.1000 | 0.1000 | 382.0000 | 0.0700 | 0.1720 | SEED | -0.0609 |
| abrupt/label_swap | det4_s1_whddma_cadwin | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 382.0000 | 0.0300 | 0.1720 | SEED | -0.0291 |
| abrupt/label_swap | det4_s1_whddma_chddma | 10 | 0.0870 | 0.0769 | 0.1000 | 0.1000 | 103.0000 | 0.1200 | 0.1720 | SEED | -0.0850 |
| abrupt/label_swap | det4_s1_whddma_crddm | 10 | 0.1176 | 0.1429 | 0.1000 | 0.1000 | 382.0000 | 0.0600 | 0.1720 | SEED | -0.0544 |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 10 | 0.1333 | 0.2000 | 0.1000 | 0.1000 | 94.0000 | 0.0400 | 0.1720 | SEED | -0.0387 |
| abrupt/label_swap | det4_s1_wrddm_chddma | 10 | 0.1176 | 0.1429 | 0.1000 | 0.1000 | 39.0000 | 0.0600 | 0.1720 | SEED | -0.0544 |
| abrupt/label_swap | det4_s1_wrddm_crddm | 10 | 0.1566 | 0.0878 | 0.7222 | 0.5000 | 184.8000 | 1.3500 | 0.1720 | SEED | -0.0154 |
| gradual/class_prior | det4_s0_wadwin_cadwin | 10 | 0.2222 | 0.1364 | 0.6000 | 0.6000 | 1206.8333 | 0.4259 | 0.1890 | STEPD | 0.0332 |
| gradual/class_prior | det4_s0_wadwin_chddma | 10 | 0.3750 | 0.5000 | 0.3000 | 0.3000 | 831.0000 | 0.0309 | 0.1890 | STEPD | 0.1860 |
| gradual/class_prior | det4_s0_wadwin_crddm | 10 | 0.2400 | 0.2000 | 0.3000 | 0.3000 | 861.6667 | 0.1273 | 0.1890 | STEPD | 0.0510 |
| gradual/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1890 | STEPD | -0.1890 |
| gradual/class_prior | det4_s0_whddma_chddma | 10 | 0.2941 | 0.2273 | 0.4167 | 0.3000 | 808.0000 | 0.2013 | 0.1890 | STEPD | 0.1051 |
| gradual/class_prior | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1890 | STEPD | -0.1890 |
| gradual/class_prior | det4_s0_wrddm_cadwin | 10 | 0.4286 | 0.7500 | 0.3000 | 0.3000 | 912.0000 | 0.0126 | 0.1890 | STEPD | 0.2396 |
| gradual/class_prior | det4_s0_wrddm_chddma | 10 | 0.3529 | 0.4286 | 0.3000 | 0.3000 | 679.3333 | 0.0519 | 0.1890 | STEPD | 0.1639 |
| gradual/class_prior | det4_s0_wrddm_crddm | 10 | 0.3265 | 0.2286 | 0.5714 | 0.4000 | 668.0000 | 0.3048 | 0.1890 | STEPD | 0.1375 |
| gradual/class_prior | det4_s1_wadwin_cadwin | 10 | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 1155.0000 | 0.0569 | 0.1890 | STEPD | 0.3110 |
| gradual/class_prior | det4_s1_wadwin_chddma | 10 | 0.2353 | 0.2857 | 0.2000 | 0.2000 | 1682.0000 | 0.0591 | 0.1890 | STEPD | 0.0463 |
| gradual/class_prior | det4_s1_wadwin_crddm | 10 | 0.2500 | 0.3333 | 0.2000 | 0.2000 | 1682.0000 | 0.0490 | 0.1890 | STEPD | 0.0610 |
| gradual/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1890 | STEPD | -0.1890 |
| gradual/class_prior | det4_s1_whddma_chddma | 10 | 0.3571 | 0.3125 | 0.4167 | 0.3000 | 744.0000 | 0.1143 | 0.1890 | STEPD | 0.1681 |
| gradual/class_prior | det4_s1_whddma_crddm | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 452.0000 | 0.0000 | 0.1890 | STEPD | -0.0072 |
| gradual/class_prior | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1890 | STEPD | -0.1890 |
| gradual/class_prior | det4_s1_wrddm_chddma | 10 | 0.2857 | 0.6667 | 0.1818 | 0.1000 | 614.0000 | 0.0132 | 0.1890 | STEPD | 0.0967 |
| gradual/class_prior | det4_s1_wrddm_crddm | 10 | 0.1207 | 0.0680 | 0.5385 | 0.4000 | 643.2500 | 1.0662 | 0.1890 | STEPD | -0.0683 |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2603 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0902 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1302 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1202 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0455 | 0.0294 | 0.1000 | 0.1000 | 245.0000 | 0.3307 | 0.0650 | HDDM_W | -0.0195 |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0101 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1103 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.1008 | 0.0571 | 0.4286 | 0.2000 | 376.0000 | 0.9919 | 0.0650 | HDDM_W | 0.0358 |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.3750 | 0.2432 | 0.8182 | 0.8000 | 1341.8750 | 0.2800 | 0.6670 | ABCD(X) | -0.2920 |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.5000 | 0.4286 | 0.6000 | 0.6000 | 549.3333 | 0.0800 | 0.6670 | ABCD(X) | -0.1670 |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.2963 | 0.2353 | 0.4000 | 0.4000 | 837.0000 | 0.1300 | 0.6670 | ABCD(X) | -0.3707 |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 1258.0000 | 0.0100 | 0.6670 | ABCD(X) | -0.5003 |
| gradual/feature_permutation | det4_s0_whddma_chddma | 10 | 0.5946 | 0.4231 | 1.0000 | 1.0000 | 905.8000 | 0.1500 | 0.6670 | ABCD(X) | -0.0724 |
| gradual/feature_permutation | det4_s0_whddma_crddm | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 960.0000 | 0.0000 | 0.6670 | ABCD(X) | -0.4852 |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 700.5000 | 0.0100 | 0.6670 | ABCD(X) | -0.3593 |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.4000 | 0.6000 | 0.3000 | 0.3000 | 651.3333 | 0.0200 | 0.6670 | ABCD(X) | -0.2670 |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.4815 | 0.3171 | 1.0000 | 1.0000 | 849.5000 | 0.2800 | 0.6670 | ABCD(X) | -0.1855 |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.7273 | 0.7273 | 0.7273 | 0.7000 | 1332.8571 | 0.0300 | 0.6670 | ABCD(X) | 0.0603 |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.7619 | 0.8000 | 0.7273 | 0.7000 | 1328.2857 | 0.0200 | 0.6670 | ABCD(X) | 0.0949 |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.6667 | 0.6364 | 0.7000 | 0.7000 | 1301.5714 | 0.0400 | 0.6670 | ABCD(X) | -0.0003 |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 2250.0000 | 0.0100 | 0.6670 | ABCD(X) | -0.3593 |
| gradual/feature_permutation | det4_s1_whddma_chddma | 10 | 0.5185 | 0.4375 | 0.6364 | 0.6000 | 999.5000 | 0.0900 | 0.6670 | ABCD(X) | -0.1485 |
| gradual/feature_permutation | det4_s1_whddma_crddm | 10 | 0.3750 | 0.5000 | 0.3000 | 0.3000 | 1702.0000 | 0.0300 | 0.6670 | ABCD(X) | -0.2920 |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.2857 | 0.5000 | 0.2000 | 0.2000 | 2250.0000 | 0.0200 | 0.6670 | ABCD(X) | -0.3813 |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.4762 | 0.4545 | 0.5000 | 0.5000 | 1422.4000 | 0.0600 | 0.6670 | ABCD(X) | -0.1908 |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.2282 | 0.1288 | 1.0000 | 1.0000 | 912.6000 | 1.1500 | 0.6670 | ABCD(X) | -0.4388 |
| gradual/label_swap | det4_s0_wadwin_cadwin | 10 | 0.1026 | 0.0714 | 0.1818 | 0.1000 | 808.0000 | 0.2600 | 0.1750 | ABCD | -0.0724 |
| gradual/label_swap | det4_s0_wadwin_chddma | 10 | 0.1053 | 0.1111 | 0.1000 | 0.1000 | 366.0000 | 0.0800 | 0.1750 | ABCD | -0.0697 |
| gradual/label_swap | det4_s0_wadwin_crddm | 10 | 0.0741 | 0.0588 | 0.1000 | 0.1000 | 500.0000 | 0.1600 | 0.1750 | ABCD | -0.1009 |
| gradual/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.1750 | ABCD | -0.1750 |
| gradual/label_swap | det4_s0_whddma_chddma | 10 | 0.0870 | 0.0769 | 0.1000 | 0.1000 | 501.0000 | 0.1200 | 0.1750 | ABCD | -0.0880 |
| gradual/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.1750 | ABCD | -0.1750 |
| gradual/label_swap | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0300 | 0.1750 | ABCD | -0.1750 |
| gradual/label_swap | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.1750 | ABCD | -0.1750 |
| gradual/label_swap | det4_s0_wrddm_crddm | 10 | 0.0816 | 0.0513 | 0.2000 | 0.2000 | 542.0000 | 0.3700 | 0.1750 | ABCD | -0.0934 |
| gradual/label_swap | det4_s1_wadwin_cadwin | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 744.0000 | 0.0300 | 0.1750 | ABCD | -0.0321 |
| gradual/label_swap | det4_s1_wadwin_chddma | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 808.0000 | 0.0200 | 0.1750 | ABCD | -0.0212 |
| gradual/label_swap | det4_s1_wadwin_crddm | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 808.0000 | 0.0300 | 0.1750 | ABCD | -0.0321 |
| gradual/label_swap | det4_s1_whddma_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 744.0000 | 0.0100 | 0.1750 | ABCD | -0.0083 |
| gradual/label_swap | det4_s1_whddma_chddma | 10 | 0.0800 | 0.0667 | 0.1000 | 0.1000 | 808.0000 | 0.1400 | 0.1750 | ABCD | -0.0950 |
| gradual/label_swap | det4_s1_whddma_crddm | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 808.0000 | 0.0300 | 0.1750 | ABCD | -0.0321 |
| gradual/label_swap | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0100 | 0.1750 | ABCD | -0.1750 |
| gradual/label_swap | det4_s1_wrddm_chddma | 10 | 0.1429 | 0.2500 | 0.1000 | 0.1000 | 808.0000 | 0.0300 | 0.1750 | ABCD | -0.0321 |
| gradual/label_swap | det4_s1_wrddm_crddm | 10 | 0.0492 | 0.0273 | 0.2500 | 0.1000 | 808.0000 | 1.0700 | 0.1750 | ABCD | -0.1258 |

### injected_electricity

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 10 | 0.5625 | 0.4286 | 0.8182 | 0.8000 | 1585.5000 | 0.2996 | 0.6980 | ADWIN | -0.1355 |
| abrupt/class_prior | det4_s0_wadwin_chddma | 10 | 0.2222 | 0.2500 | 0.2000 | 0.2000 | 996.5000 | 0.1497 | 0.6980 | ADWIN | -0.4758 |
| abrupt/class_prior | det4_s0_wadwin_crddm | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 680.0000 | 0.0510 | 0.6980 | ADWIN | -0.5442 |
| abrupt/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s0_whddma_chddma | 10 | 0.1333 | 0.2000 | 0.1000 | 0.1000 | 413.0000 | 0.1032 | 0.6980 | ADWIN | -0.5647 |
| abrupt/class_prior | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0257 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0236 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s0_wrddm_crddm | 10 | 0.0588 | 0.0417 | 0.1000 | 0.1000 | 2195.0000 | 0.5848 | 0.6980 | ADWIN | -0.6392 |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 10 | 0.4211 | 0.4444 | 0.4000 | 0.4000 | 1075.5000 | 0.1271 | 0.6980 | ADWIN | -0.2769 |
| abrupt/class_prior | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0493 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0493 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0257 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s1_whddma_chddma | 10 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 1708.5000 | 0.0766 | 0.6980 | ADWIN | -0.4313 |
| abrupt/class_prior | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 609.0000 | 0.0257 | 0.6980 | ADWIN | -0.5313 |
| abrupt/class_prior | det4_s1_wrddm_chddma | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 288.0000 | 0.0000 | 0.6980 | ADWIN | -0.5162 |
| abrupt/class_prior | det4_s1_wrddm_crddm | 10 | 0.1143 | 0.0800 | 0.2000 | 0.2000 | 446.5000 | 0.5798 | 0.6980 | ADWIN | -0.5837 |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3476 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0284 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 10 | 0.2105 | 0.2500 | 0.1818 | 0.1000 | 1484.0000 | 0.1478 | 0.2450 | CUSUM | -0.0345 |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0242 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0280 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4874 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1661 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0277 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0277 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0556 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.8593 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.4516 | 0.3500 | 0.6364 | 0.6000 | 731.6667 | 0.2869 | 1.0000 | ABCD(X) | -0.5484 |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 250.6667 | 0.0000 | 1.0000 | ABCD(X) | -0.2500 |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.7059 | 0.8571 | 0.6000 | 0.6000 | 447.6667 | 0.0221 | 1.0000 | ABCD(X) | -0.2941 |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 10 | 0.7619 | 0.7273 | 0.8000 | 0.8000 | 127.2500 | 0.0662 | 1.0000 | ABCD(X) | -0.2381 |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0441 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.3750 | 0.5000 | 0.3000 | 0.3000 | 180.3333 | 0.0662 | 1.0000 | ABCD(X) | -0.6250 |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.3750 | 0.2432 | 0.8182 | 0.8000 | 308.6250 | 0.6179 | 1.0000 | ABCD(X) | -0.6250 |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.7500 | 0.6923 | 0.8182 | 0.8000 | 542.7500 | 0.0883 | 1.0000 | ABCD(X) | -0.2500 |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.6364 | 0.6364 | 0.6364 | 0.6000 | 558.3333 | 0.0883 | 1.0000 | ABCD(X) | -0.3636 |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 466.5000 | 0.0883 | 1.0000 | ABCD(X) | -0.4000 |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 174.0000 | 0.0000 | 1.0000 | ABCD(X) | -0.8182 |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 10 | 0.9091 | 0.9091 | 0.9091 | 0.9000 | 253.8889 | 0.0221 | 1.0000 | ABCD(X) | -0.0909 |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 174.0000 | 0.0221 | 1.0000 | ABCD(X) | -0.8333 |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.3529 | 0.4286 | 0.3000 | 0.3000 | 330.6667 | 0.0883 | 1.0000 | ABCD(X) | -0.6471 |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 1018.0000 | 0.0662 | 1.0000 | ABCD(X) | -0.7333 |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.3243 | 0.1978 | 0.9000 | 0.8000 | 172.1250 | 1.6111 | 1.0000 | ABCD(X) | -0.6757 |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 10 | 0.6250 | 0.4762 | 0.9091 | 0.9000 | 816.1111 | 0.2428 | 0.5660 | SEED | 0.0590 |
| abrupt/label_swap | det4_s0_wadwin_chddma | 10 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 284.6667 | 0.0883 | 0.5660 | SEED | 0.0340 |
| abrupt/label_swap | det4_s0_wadwin_crddm | 10 | 0.7000 | 0.7000 | 0.7000 | 0.7000 | 430.1429 | 0.0662 | 0.5660 | SEED | 0.1340 |
| abrupt/label_swap | det4_s0_whddma_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 662.0000 | 0.0000 | 0.5660 | SEED | -0.3842 |
| abrupt/label_swap | det4_s0_whddma_chddma | 10 | 0.7619 | 0.7273 | 0.8000 | 0.8000 | 196.7500 | 0.0662 | 0.5660 | SEED | 0.1959 |
| abrupt/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5660 | SEED | -0.5660 |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5660 | SEED | -0.5660 |
| abrupt/label_swap | det4_s0_wrddm_chddma | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 1439.0000 | 0.0441 | 0.5660 | SEED | -0.4122 |
| abrupt/label_swap | det4_s0_wrddm_crddm | 10 | 0.2642 | 0.1628 | 0.7000 | 0.7000 | 177.1429 | 0.7945 | 0.5660 | SEED | -0.3018 |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 10 | 0.8182 | 0.7500 | 0.9000 | 0.9000 | 506.8889 | 0.0662 | 0.5660 | SEED | 0.2522 |
| abrupt/label_swap | det4_s1_wadwin_chddma | 10 | 0.8421 | 0.8889 | 0.8000 | 0.8000 | 531.3750 | 0.0221 | 0.5660 | SEED | 0.2761 |
| abrupt/label_swap | det4_s1_wadwin_crddm | 10 | 0.8421 | 0.8889 | 0.8000 | 0.8000 | 485.0000 | 0.0221 | 0.5660 | SEED | 0.2761 |
| abrupt/label_swap | det4_s1_whddma_cadwin | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 533.5000 | 0.0000 | 0.5660 | SEED | 0.1840 |
| abrupt/label_swap | det4_s1_whddma_chddma | 10 | 0.6957 | 0.6154 | 0.8000 | 0.8000 | 372.7500 | 0.1103 | 0.5660 | SEED | 0.1297 |
| abrupt/label_swap | det4_s1_whddma_crddm | 10 | 0.5333 | 0.8000 | 0.4000 | 0.4000 | 718.7500 | 0.0221 | 0.5660 | SEED | -0.0327 |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 10 | 0.7059 | 0.8571 | 0.6000 | 0.6000 | 533.5000 | 0.0221 | 0.5660 | SEED | 0.1399 |
| abrupt/label_swap | det4_s1_wrddm_chddma | 10 | 0.6667 | 0.7500 | 0.6000 | 0.6000 | 465.1667 | 0.0441 | 0.5660 | SEED | 0.1007 |
| abrupt/label_swap | det4_s1_wrddm_crddm | 10 | 0.2667 | 0.1562 | 0.9091 | 0.9000 | 324.5556 | 1.1917 | 0.5660 | SEED | -0.2993 |
| gradual/class_prior | det4_s0_wadwin_cadwin | 10 | 0.3704 | 0.2941 | 0.5000 | 0.5000 | 1708.4000 | 0.3036 | 0.2950 | STEPD | 0.0754 |
| gradual/class_prior | det4_s0_wadwin_chddma | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 1016.0000 | 0.0514 | 0.2950 | STEPD | -0.1412 |
| gradual/class_prior | det4_s0_wadwin_crddm | 10 | 0.3333 | 1.0000 | 0.2000 | 0.2000 | 1169.0000 | 0.0000 | 0.2950 | STEPD | 0.0383 |
| gradual/class_prior | det4_s0_whddma_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 1131.0000 | 0.0000 | 0.2950 | STEPD | -0.1132 |
| gradual/class_prior | det4_s0_whddma_chddma | 10 | 0.2500 | 0.3333 | 0.2000 | 0.2000 | 2053.5000 | 0.0956 | 0.2950 | STEPD | -0.0450 |
| gradual/class_prior | det4_s0_whddma_crddm | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 1091.0000 | 0.0000 | 0.2950 | STEPD | -0.1132 |
| gradual/class_prior | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0243 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s0_wrddm_crddm | 10 | 0.1364 | 0.0909 | 0.2727 | 0.2000 | 1496.0000 | 0.7566 | 0.2950 | STEPD | -0.1586 |
| gradual/class_prior | det4_s1_wadwin_cadwin | 10 | 0.3810 | 0.3636 | 0.4000 | 0.4000 | 2063.0000 | 0.1724 | 0.2950 | STEPD | 0.0860 |
| gradual/class_prior | det4_s1_wadwin_chddma | 10 | 0.2857 | 0.5000 | 0.2000 | 0.2000 | 1630.5000 | 0.0482 | 0.2950 | STEPD | -0.0093 |
| gradual/class_prior | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0740 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0243 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s1_whddma_chddma | 10 | 0.5000 | 0.5556 | 0.4545 | 0.4000 | 1392.5000 | 0.1014 | 0.2950 | STEPD | 0.2050 |
| gradual/class_prior | det4_s1_whddma_crddm | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 901.0000 | 0.0243 | 0.2950 | STEPD | -0.1283 |
| gradual/class_prior | det4_s1_wrddm_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 779.0000 | 0.0243 | 0.2950 | STEPD | -0.1283 |
| gradual/class_prior | det4_s1_wrddm_chddma | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 818.0000 | 0.0243 | 0.2950 | STEPD | -0.1283 |
| gradual/class_prior | det4_s1_wrddm_crddm | 10 | 0.0800 | 0.0513 | 0.1818 | 0.1000 | 492.0000 | 0.9352 | 0.2950 | STEPD | -0.2150 |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.0952 | 0.0909 | 0.1000 | 0.1000 | 2196.0000 | 0.2551 | 0.1470 | STUDD | -0.0518 |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1091 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0248 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0784 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1271 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0250 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0526 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.7049 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1499 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1024 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1024 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0248 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_whddma_chddma | 10 | 0.2500 | 0.3333 | 0.2000 | 0.2000 | 1284.0000 | 0.1073 | 0.1470 | STUDD | 0.1030 |
| gradual/feature_filtering | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0485 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0498 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0498 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 1.5616 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.4444 | 0.3333 | 0.6667 | 0.6000 | 1043.3333 | 0.3531 | 0.9840 | ABCD(X) | -0.5396 |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.6316 | 0.6667 | 0.6000 | 0.6000 | 604.3333 | 0.0662 | 0.9840 | ABCD(X) | -0.3524 |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.6316 | 0.7500 | 0.5455 | 0.5000 | 814.4000 | 0.0441 | 0.9840 | ABCD(X) | -0.3524 |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.9840 | ABCD(X) | -0.9840 |
| gradual/feature_permutation | det4_s0_whddma_chddma | 10 | 0.6364 | 0.5833 | 0.7000 | 0.7000 | 788.7143 | 0.1103 | 0.9840 | ABCD(X) | -0.3476 |
| gradual/feature_permutation | det4_s0_whddma_crddm | 10 | 0.3333 | 1.0000 | 0.2000 | 0.2000 | 1099.0000 | 0.0000 | 0.9840 | ABCD(X) | -0.6507 |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.3333 | 1.0000 | 0.2000 | 0.2000 | 813.5000 | 0.0000 | 0.9840 | ABCD(X) | -0.6507 |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.6667 | 0.7500 | 0.6000 | 0.6000 | 955.1667 | 0.0441 | 0.9840 | ABCD(X) | -0.3173 |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.4898 | 0.3429 | 0.8571 | 0.8000 | 799.3750 | 0.5076 | 0.9840 | ABCD(X) | -0.4942 |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.6923 | 0.6000 | 0.8182 | 0.8000 | 954.7500 | 0.1324 | 0.9840 | ABCD(X) | -0.2917 |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.5714 | 0.5455 | 0.6000 | 0.6000 | 1166.6667 | 0.1103 | 0.9840 | ABCD(X) | -0.4126 |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.5455 | 0.5000 | 0.6000 | 0.6000 | 1139.1667 | 0.1324 | 0.9840 | ABCD(X) | -0.4385 |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.4615 | 1.0000 | 0.3000 | 0.3000 | 1325.0000 | 0.0000 | 0.9840 | ABCD(X) | -0.5225 |
| gradual/feature_permutation | det4_s1_whddma_chddma | 10 | 0.7333 | 0.5789 | 1.0000 | 1.0000 | 739.2000 | 0.1766 | 0.9840 | ABCD(X) | -0.2507 |
| gradual/feature_permutation | det4_s1_whddma_crddm | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 1159.2500 | 0.0000 | 0.9840 | ABCD(X) | -0.4126 |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.6250 | 1.0000 | 0.4545 | 0.4000 | 939.5000 | 0.0000 | 0.9840 | ABCD(X) | -0.3590 |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.7368 | 0.7778 | 0.7000 | 0.7000 | 608.1429 | 0.0441 | 0.9840 | ABCD(X) | -0.2472 |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.3218 | 0.1972 | 0.8750 | 0.8000 | 1272.1250 | 1.2579 | 0.9840 | ABCD(X) | -0.6622 |
| gradual/label_swap | det4_s0_wadwin_cadwin | 10 | 0.3636 | 0.3333 | 0.4000 | 0.4000 | 928.0000 | 0.1766 | 0.3830 | STEPD | -0.0194 |
| gradual/label_swap | det4_s0_wadwin_chddma | 10 | 0.2353 | 0.2857 | 0.2000 | 0.2000 | 1223.5000 | 0.1103 | 0.3830 | STEPD | -0.1477 |
| gradual/label_swap | det4_s0_wadwin_crddm | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 1073.3333 | 0.0000 | 0.3830 | STEPD | 0.3670 |
| gradual/label_swap | det4_s0_whddma_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 908.0000 | 0.0000 | 0.3830 | STEPD | -0.2012 |
| gradual/label_swap | det4_s0_whddma_chddma | 10 | 0.6957 | 0.6154 | 0.8000 | 0.8000 | 789.8750 | 0.1103 | 0.3830 | STEPD | 0.3127 |
| gradual/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.3830 | STEPD | -0.3830 |
| gradual/label_swap | det4_s0_wrddm_cadwin | 10 | 0.3333 | 1.0000 | 0.2000 | 0.2000 | 1007.0000 | 0.0000 | 0.3830 | STEPD | -0.0497 |
| gradual/label_swap | det4_s0_wrddm_chddma | 10 | 0.6250 | 0.8333 | 0.5000 | 0.5000 | 999.6000 | 0.0221 | 0.3830 | STEPD | 0.2420 |
| gradual/label_swap | det4_s0_wrddm_crddm | 10 | 0.3478 | 0.2222 | 0.8000 | 0.8000 | 887.0000 | 0.6179 | 0.3830 | STEPD | -0.0352 |
| gradual/label_swap | det4_s1_wadwin_cadwin | 10 | 0.5263 | 0.5556 | 0.5000 | 0.5000 | 1064.8000 | 0.0883 | 0.3830 | STEPD | 0.1433 |
| gradual/label_swap | det4_s1_wadwin_chddma | 10 | 0.5000 | 0.6667 | 0.4000 | 0.4000 | 829.7500 | 0.0441 | 0.3830 | STEPD | 0.1170 |
| gradual/label_swap | det4_s1_wadwin_crddm | 10 | 0.5333 | 0.8000 | 0.4000 | 0.4000 | 840.0000 | 0.0221 | 0.3830 | STEPD | 0.1503 |
| gradual/label_swap | det4_s1_whddma_cadwin | 10 | 0.3333 | 1.0000 | 0.2000 | 0.2000 | 895.0000 | 0.0000 | 0.3830 | STEPD | -0.0497 |
| gradual/label_swap | det4_s1_whddma_chddma | 10 | 0.5217 | 0.5000 | 0.5455 | 0.5000 | 671.0000 | 0.1324 | 0.3830 | STEPD | 0.1387 |
| gradual/label_swap | det4_s1_whddma_crddm | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 2077.0000 | 0.0441 | 0.3830 | STEPD | -0.2292 |
| gradual/label_swap | det4_s1_wrddm_cadwin | 10 | 0.4286 | 0.7500 | 0.3000 | 0.3000 | 1219.3333 | 0.0221 | 0.3830 | STEPD | 0.0456 |
| gradual/label_swap | det4_s1_wrddm_chddma | 10 | 0.5000 | 0.8000 | 0.3636 | 0.3000 | 985.0000 | 0.0221 | 0.3830 | STEPD | 0.1170 |
| gradual/label_swap | det4_s1_wrddm_crddm | 10 | 0.2807 | 0.1778 | 0.6667 | 0.6000 | 526.6667 | 0.8166 | 0.3830 | STEPD | -0.1023 |

### injected_gas_sensor_drift

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0748 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0740 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_whddma_chddma | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 1261.0000 | 0.1504 | 0.4000 | DDM | -0.2462 |
| abrupt/class_prior | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wrddm_crddm | 10 | 0.1429 | 0.1111 | 0.2000 | 0.2000 | 415.0000 | 1.2032 | 0.4000 | DDM | -0.2571 |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2221 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_whddma_chddma | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 644.0000 | 0.1504 | 0.4000 | DDM | -0.2462 |
| abrupt/class_prior | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0768 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wrddm_crddm | 10 | 0.2222 | 0.1515 | 0.4167 | 0.3000 | 557.3333 | 2.1245 | 0.4000 | DDM | -0.1778 |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.6400 | 0.5714 | 0.7273 | 0.7000 | 657.5714 | 0.5405 | 0.5710 | SEED | 0.0690 |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 635.0000 | 0.0813 | 0.5710 | SEED | -0.2633 |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 977.5000 | 0.0930 | 0.5710 | SEED | -0.2633 |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1743 | 0.5710 | SEED | -0.5710 |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 10 | 0.5263 | 0.5556 | 0.5000 | 0.5000 | 198.8000 | 0.3559 | 0.5710 | SEED | -0.0447 |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5710 | SEED | -0.5710 |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 629.5000 | 0.0813 | 0.5710 | SEED | -0.2633 |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.4000 | 0.6000 | 0.3000 | 0.3000 | 589.3333 | 0.1743 | 0.5710 | SEED | -0.1710 |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.4286 | 0.3529 | 0.5455 | 0.5000 | 391.0000 | 0.9985 | 0.5710 | SEED | -0.1424 |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.7619 | 0.7273 | 0.8000 | 0.8000 | 686.5000 | 0.2585 | 0.5710 | SEED | 0.1909 |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.7059 | 0.8571 | 0.6000 | 0.6000 | 814.8333 | 0.0813 | 0.5710 | SEED | 0.1349 |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.6667 | 0.7500 | 0.6000 | 0.6000 | 793.0000 | 0.1700 | 0.5710 | SEED | 0.0957 |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 981.5000 | 0.0813 | 0.5710 | SEED | -0.2633 |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 10 | 0.6667 | 0.7500 | 0.6000 | 0.6000 | 598.8333 | 0.1660 | 0.5710 | SEED | 0.0957 |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 651.0000 | 0.0813 | 0.5710 | SEED | -0.4043 |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 981.5000 | 0.0813 | 0.5710 | SEED | -0.2633 |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.5333 | 0.8000 | 0.4000 | 0.4000 | 865.2500 | 0.0813 | 0.5710 | SEED | -0.0377 |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.4286 | 0.3103 | 0.6923 | 0.6000 | 415.6667 | 1.7937 | 0.5710 | SEED | -0.1424 |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.7500 | 0.6923 | 0.8182 | 0.8000 | 422.0000 | 0.2876 | 1.0000 | ABCD(X) | -0.2500 |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.4615 | 1.0000 | 0.3000 | 0.3000 | 267.3333 | 0.0000 | 1.0000 | ABCD(X) | -0.5385 |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 297.5000 | 0.0719 | 1.0000 | ABCD(X) | -0.6923 |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 363.0000 | 0.0719 | 1.0000 | ABCD(X) | -0.8333 |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 10 | 0.8333 | 0.7143 | 1.0000 | 1.0000 | 86.6000 | 0.2876 | 1.0000 | ABCD(X) | -0.1667 |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 121.0000 | 0.0719 | 1.0000 | ABCD(X) | -0.8333 |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 285.0000 | 0.0000 | 1.0000 | ABCD(X) | -0.8182 |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 69.0000 | 0.0000 | 1.0000 | ABCD(X) | -0.8182 |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.5625 | 0.4091 | 0.9000 | 0.9000 | 181.7778 | 0.9346 | 1.0000 | ABCD(X) | -0.4375 |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.9524 | 0.9091 | 1.0000 | 1.0000 | 279.5000 | 0.0719 | 1.0000 | ABCD(X) | -0.0476 |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.7778 | 0.8750 | 0.7000 | 0.7000 | 373.7143 | 0.0719 | 1.0000 | ABCD(X) | -0.2222 |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.9000 | 0.9000 | 0.9000 | 0.9000 | 426.3333 | 0.0719 | 1.0000 | ABCD(X) | -0.1000 |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.7059 | 0.8571 | 0.6000 | 0.6000 | 406.1667 | 0.0719 | 1.0000 | ABCD(X) | -0.2941 |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 10 | 0.9524 | 0.9091 | 1.0000 | 1.0000 | 93.6000 | 0.0719 | 1.0000 | ABCD(X) | -0.0476 |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 10 | 0.6667 | 0.8571 | 0.5455 | 0.5000 | 444.8000 | 0.0719 | 1.0000 | ABCD(X) | -0.3333 |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.8000 | 0.8000 | 0.8000 | 0.8000 | 334.0000 | 0.1438 | 1.0000 | ABCD(X) | -0.2000 |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.6667 | 0.7000 | 0.6364 | 0.6000 | 355.0000 | 0.2157 | 1.0000 | ABCD(X) | -0.3333 |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.6383 | 0.4688 | 1.0000 | 1.0000 | 191.6000 | 1.2221 | 1.0000 | ABCD(X) | -0.3617 |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 10 | 0.3636 | 0.3333 | 0.4000 | 0.4000 | 872.5000 | 0.5751 | 0.5250 | SEED | -0.1614 |
| abrupt/label_swap | det4_s0_wadwin_chddma | 10 | 0.3333 | 1.0000 | 0.2000 | 0.2000 | 841.5000 | 0.0000 | 0.5250 | SEED | -0.1917 |
| abrupt/label_swap | det4_s0_wadwin_crddm | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 540.0000 | 0.0719 | 0.5250 | SEED | -0.2173 |
| abrupt/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 0.5250 | SEED | -0.5250 |
| abrupt/label_swap | det4_s0_whddma_chddma | 10 | 0.5455 | 0.5000 | 0.6000 | 0.6000 | 733.1667 | 0.4313 | 0.5250 | SEED | 0.0205 |
| abrupt/label_swap | det4_s0_whddma_crddm | 10 | 0.2857 | 0.5000 | 0.2000 | 0.2000 | 529.0000 | 0.1438 | 0.5250 | SEED | -0.2393 |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 1436.0000 | 0.1438 | 0.5250 | SEED | -0.3712 |
| abrupt/label_swap | det4_s0_wrddm_chddma | 10 | 0.7778 | 0.8750 | 0.7000 | 0.7000 | 869.2857 | 0.0719 | 0.5250 | SEED | 0.2528 |
| abrupt/label_swap | det4_s0_wrddm_crddm | 10 | 0.5882 | 0.4348 | 0.9091 | 0.9000 | 621.1111 | 0.9346 | 0.5250 | SEED | 0.0632 |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 10 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 1040.1667 | 0.2876 | 0.5250 | SEED | 0.0750 |
| abrupt/label_swap | det4_s1_wadwin_chddma | 10 | 0.3333 | 0.3750 | 0.3000 | 0.3000 | 758.0000 | 0.3595 | 0.5250 | SEED | -0.1917 |
| abrupt/label_swap | det4_s1_wadwin_crddm | 10 | 0.3333 | 0.3750 | 0.3000 | 0.3000 | 716.0000 | 0.3595 | 0.5250 | SEED | -0.1917 |
| abrupt/label_swap | det4_s1_whddma_cadwin | 10 | 0.3750 | 0.5000 | 0.3000 | 0.3000 | 1049.0000 | 0.2157 | 0.5250 | SEED | -0.1500 |
| abrupt/label_swap | det4_s1_whddma_chddma | 10 | 0.8182 | 0.7500 | 0.9000 | 0.9000 | 591.4444 | 0.2157 | 0.5250 | SEED | 0.2932 |
| abrupt/label_swap | det4_s1_whddma_crddm | 10 | 0.1333 | 0.2000 | 0.1000 | 0.1000 | 337.0000 | 0.2876 | 0.5250 | SEED | -0.3917 |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 10 | 0.2500 | 0.3333 | 0.2000 | 0.2000 | 1413.5000 | 0.2876 | 0.5250 | SEED | -0.2750 |
| abrupt/label_swap | det4_s1_wrddm_chddma | 10 | 0.2500 | 0.3333 | 0.2000 | 0.2000 | 327.0000 | 0.2876 | 0.5250 | SEED | -0.2750 |
| abrupt/label_swap | det4_s1_wrddm_crddm | 10 | 0.4127 | 0.2653 | 0.9286 | 0.9000 | 440.6667 | 2.5881 | 0.5250 | SEED | -0.1123 |
| gradual/class_prior | det4_s0_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0753 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wadwin_crddm | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 1021.0000 | 0.0000 | 0.5190 | STUDD | -0.3372 |
| gradual/class_prior | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0762 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wrddm_crddm | 10 | 0.1538 | 0.1250 | 0.2000 | 0.2000 | 645.5000 | 1.0484 | 0.5190 | STUDD | -0.3652 |
| gradual/class_prior | det4_s1_wadwin_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wadwin_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wadwin_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_whddma_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0759 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wrddm_chddma | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wrddm_crddm | 10 | 0.1111 | 0.0800 | 0.1818 | 0.1000 | 848.0000 | 1.7152 | 0.5190 | STUDD | -0.4079 |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 10 | 0.6400 | 0.5333 | 0.8000 | 0.8000 | 973.2500 | 0.6141 | 0.4040 | STUDD | 0.2360 |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 10 | 0.1818 | 1.0000 | 0.1000 | 0.1000 | 922.0000 | 0.0000 | 0.4040 | STUDD | -0.2222 |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 1414.0000 | 0.0930 | 0.4040 | STUDD | -0.2373 |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4040 | STUDD | -0.4040 |
| gradual/feature_filtering | det4_s0_whddma_chddma | 10 | 0.6667 | 0.6364 | 0.7000 | 0.7000 | 830.7143 | 0.3376 | 0.4040 | STUDD | 0.2627 |
| gradual/feature_filtering | det4_s0_whddma_crddm | 10 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 647.5000 | 0.2583 | 0.4040 | STUDD | -0.1373 |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 10 | 0.4615 | 1.0000 | 0.3000 | 0.3000 | 1181.0000 | 0.0000 | 0.4040 | STUDD | 0.0575 |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 762.5000 | 0.0927 | 0.4040 | STUDD | -0.0963 |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 10 | 0.4324 | 0.3200 | 0.6667 | 0.6000 | 808.3333 | 1.4855 | 0.4040 | STUDD | 0.0284 |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 10 | 0.5833 | 0.5000 | 0.7000 | 0.7000 | 963.0000 | 0.5959 | 0.4040 | STUDD | 0.1793 |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 10 | 0.6000 | 0.6000 | 0.6000 | 0.6000 | 1021.8333 | 0.3424 | 0.4040 | STUDD | 0.1960 |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 10 | 0.5714 | 0.5455 | 0.6000 | 0.6000 | 1012.6667 | 0.4351 | 0.4040 | STUDD | 0.1674 |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 10 | 0.2857 | 0.5000 | 0.2000 | 0.2000 | 1067.0000 | 0.1787 | 0.4040 | STUDD | -0.1183 |
| gradual/feature_filtering | det4_s1_whddma_chddma | 10 | 0.6667 | 0.6364 | 0.7000 | 0.7000 | 841.4286 | 0.3538 | 0.4040 | STUDD | 0.2627 |
| gradual/feature_filtering | det4_s1_whddma_crddm | 10 | 0.4000 | 0.6000 | 0.3000 | 0.3000 | 906.6667 | 0.1787 | 0.4040 | STUDD | -0.0040 |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 10 | 0.5882 | 0.7143 | 0.5000 | 0.5000 | 1002.4000 | 0.1787 | 0.4040 | STUDD | 0.1842 |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 10 | 0.5882 | 0.7143 | 0.5000 | 0.5000 | 1046.0000 | 0.1787 | 0.4040 | STUDD | 0.1842 |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 10 | 0.5000 | 0.3514 | 0.8667 | 0.8000 | 803.3750 | 2.1046 | 0.4040 | STUDD | 0.0960 |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 10 | 0.8333 | 0.7143 | 1.0000 | 1.0000 | 795.2000 | 0.2876 | 0.7040 | ABCD | 0.1293 |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 10 | 0.4615 | 1.0000 | 0.3000 | 0.3000 | 840.6667 | 0.0000 | 0.7040 | ABCD | -0.2425 |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 473.0000 | 0.1438 | 0.7040 | ABCD | -0.5502 |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.7040 | ABCD | -0.7040 |
| gradual/feature_permutation | det4_s0_whddma_chddma | 10 | 0.8696 | 0.7692 | 1.0000 | 1.0000 | 611.8000 | 0.2157 | 0.7040 | ABCD | 0.1656 |
| gradual/feature_permutation | det4_s0_whddma_crddm | 10 | 0.3077 | 0.6667 | 0.2000 | 0.2000 | 628.0000 | 0.0719 | 0.7040 | ABCD | -0.3963 |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 10 | 0.4286 | 0.7500 | 0.3000 | 0.3000 | 1029.3333 | 0.0719 | 0.7040 | ABCD | -0.2754 |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 391.0000 | 0.0719 | 0.7040 | ABCD | -0.5373 |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 10 | 0.5143 | 0.3750 | 0.8182 | 0.8000 | 428.2500 | 1.0784 | 0.7040 | ABCD | -0.1897 |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 10 | 0.8696 | 0.7692 | 1.0000 | 1.0000 | 689.6000 | 0.2157 | 0.7040 | ABCD | 0.1656 |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 10 | 0.9524 | 0.9091 | 1.0000 | 1.0000 | 790.6000 | 0.0719 | 0.7040 | ABCD | 0.2484 |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 10 | 0.9524 | 0.9091 | 1.0000 | 1.0000 | 792.1000 | 0.0719 | 0.7040 | ABCD | 0.2484 |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 10 | 0.7500 | 1.0000 | 0.6000 | 0.6000 | 949.0000 | 0.0000 | 0.7040 | ABCD | 0.0460 |
| gradual/feature_permutation | det4_s1_whddma_chddma | 10 | 0.7586 | 0.6111 | 1.0000 | 1.0000 | 518.2000 | 0.5032 | 0.7040 | ABCD | 0.0546 |
| gradual/feature_permutation | det4_s1_whddma_crddm | 10 | 0.5714 | 1.0000 | 0.4000 | 0.4000 | 749.7500 | 0.0000 | 0.7040 | ABCD | -0.1326 |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 10 | 0.8235 | 1.0000 | 0.7000 | 0.7000 | 945.7143 | 0.0000 | 0.7040 | ABCD | 0.1195 |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 10 | 0.6667 | 0.6364 | 0.7000 | 0.7000 | 679.5714 | 0.2876 | 0.7040 | ABCD | -0.0373 |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 10 | 0.7241 | 0.5676 | 1.0000 | 1.0000 | 494.1000 | 1.1503 | 0.7040 | ABCD | 0.0201 |
| gradual/label_swap | det4_s0_wadwin_cadwin | 10 | 0.3000 | 0.3000 | 0.3000 | 0.3000 | 930.6667 | 0.5032 | 0.3840 | STUDD | -0.0840 |
| gradual/label_swap | det4_s0_wadwin_chddma | 10 | 0.1667 | 0.5000 | 0.1000 | 0.1000 | 985.0000 | 0.0719 | 0.3840 | STUDD | -0.2173 |
| gradual/label_swap | det4_s0_wadwin_crddm | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 182.0000 | 0.1438 | 0.3840 | STUDD | -0.2302 |
| gradual/label_swap | det4_s0_whddma_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.3840 | STUDD | -0.3840 |
| gradual/label_swap | det4_s0_whddma_chddma | 10 | 0.4000 | 0.4000 | 0.4000 | 0.4000 | 881.5000 | 0.4313 | 0.3840 | STUDD | 0.0160 |
| gradual/label_swap | det4_s0_whddma_crddm | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 0.3840 | STUDD | -0.3840 |
| gradual/label_swap | det4_s0_wrddm_cadwin | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2157 | 0.3840 | STUDD | -0.3840 |
| gradual/label_swap | det4_s0_wrddm_chddma | 10 | 0.4286 | 0.7500 | 0.3000 | 0.3000 | 858.6667 | 0.0719 | 0.3840 | STUDD | 0.0446 |
| gradual/label_swap | det4_s0_wrddm_crddm | 10 | 0.3404 | 0.2353 | 0.6154 | 0.5000 | 724.2000 | 1.8692 | 0.3840 | STUDD | -0.0436 |
| gradual/label_swap | det4_s1_wadwin_cadwin | 10 | 0.2857 | 0.2727 | 0.3000 | 0.3000 | 930.6667 | 0.5751 | 0.3840 | STUDD | -0.0983 |
| gradual/label_swap | det4_s1_wadwin_chddma | 10 | 0.4444 | 0.5000 | 0.4000 | 0.4000 | 969.2500 | 0.2876 | 0.3840 | STUDD | 0.0604 |
| gradual/label_swap | det4_s1_wadwin_crddm | 10 | 0.6316 | 0.6667 | 0.6000 | 0.6000 | 1079.1667 | 0.2157 | 0.3840 | STUDD | 0.2476 |
| gradual/label_swap | det4_s1_whddma_cadwin | 10 | 0.1538 | 0.3333 | 0.1000 | 0.1000 | 875.0000 | 0.1438 | 0.3840 | STUDD | -0.2302 |
| gradual/label_swap | det4_s1_whddma_chddma | 10 | 0.5000 | 0.4286 | 0.6000 | 0.6000 | 1019.5000 | 0.5751 | 0.3840 | STUDD | 0.1160 |
| gradual/label_swap | det4_s1_whddma_crddm | 10 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 938.5000 | 0.2157 | 0.3840 | STUDD | -0.1173 |
| gradual/label_swap | det4_s1_wrddm_cadwin | 10 | 0.2500 | 0.3333 | 0.2000 | 0.2000 | 988.0000 | 0.2876 | 0.3840 | STUDD | -0.1340 |
| gradual/label_swap | det4_s1_wrddm_chddma | 10 | 0.5000 | 0.6667 | 0.4000 | 0.4000 | 1092.7500 | 0.1438 | 0.3840 | STUDD | 0.1160 |
| gradual/label_swap | det4_s1_wrddm_crddm | 10 | 0.2667 | 0.1702 | 0.6154 | 0.5000 | 772.0000 | 2.8037 | 0.3840 | STUDD | -0.1173 |

### injected_paper_covertype

Only preset kinds ['detector'] follow the literature protocol on this dataset; other rows appear only with --include-noncomparable.

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 50 | 0.1046 | 0.0625 | 0.3200 | 0.3200 | 1375.6875 | 2.4000 | 0.1330 | ABCD | -0.0284 |
| abrupt/class_prior | det4_s0_wadwin_chddma | 50 | 0.1026 | 0.1429 | 0.0800 | 0.0800 | 412.5000 | 0.2400 | 0.1330 | ABCD | -0.0304 |
| abrupt/class_prior | det4_s0_wadwin_crddm | 50 | 0.0708 | 0.0635 | 0.0800 | 0.0800 | 1251.7500 | 0.5900 | 0.1330 | ABCD | -0.0622 |
| abrupt/class_prior | det4_s0_whddma_cadwin | 50 | 0.0333 | 0.1000 | 0.0200 | 0.0200 | 1877.0000 | 0.0900 | 0.1330 | ABCD | -0.0997 |
| abrupt/class_prior | det4_s0_whddma_chddma | 50 | 0.0873 | 0.0559 | 0.2000 | 0.2000 | 388.8000 | 1.6900 | 0.1330 | ABCD | -0.0457 |
| abrupt/class_prior | det4_s0_whddma_crddm | 50 | 0.0635 | 0.1538 | 0.0400 | 0.0400 | 107.0000 | 0.1100 | 0.1330 | ABCD | -0.0695 |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 50 | 0.0588 | 0.1111 | 0.0400 | 0.0400 | 1258.0000 | 0.1600 | 0.1330 | ABCD | -0.0742 |
| abrupt/class_prior | det4_s0_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.5000 | 0.1330 | ABCD | -0.1330 |
| abrupt/class_prior | det4_s0_wrddm_crddm | 50 | 0.1379 | 0.0874 | 0.3273 | 0.2600 | 1084.0000 | 1.8800 | 0.1330 | ABCD | 0.0049 |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 50 | 0.1294 | 0.0917 | 0.2200 | 0.2200 | 950.9091 | 1.0900 | 0.1330 | ABCD | -0.0036 |
| abrupt/class_prior | det4_s1_wadwin_chddma | 50 | 0.1014 | 0.0795 | 0.1400 | 0.1400 | 1071.5714 | 0.8100 | 0.1330 | ABCD | -0.0316 |
| abrupt/class_prior | det4_s1_wadwin_crddm | 50 | 0.0667 | 0.0500 | 0.1000 | 0.1000 | 1190.6000 | 0.9500 | 0.1330 | ABCD | -0.0663 |
| abrupt/class_prior | det4_s1_whddma_cadwin | 50 | 0.0263 | 0.0385 | 0.0200 | 0.0200 | 1087.0000 | 0.2500 | 0.1330 | ABCD | -0.1067 |
| abrupt/class_prior | det4_s1_whddma_chddma | 50 | 0.1102 | 0.0909 | 0.1400 | 0.1400 | 456.0000 | 0.7000 | 0.1330 | ABCD | -0.0228 |
| abrupt/class_prior | det4_s1_whddma_crddm | 50 | 0.0526 | 0.0769 | 0.0400 | 0.0400 | 627.0000 | 0.2400 | 0.1330 | ABCD | -0.0804 |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 50 | 0.0455 | 0.0526 | 0.0400 | 0.0400 | 1133.5000 | 0.3600 | 0.1330 | ABCD | -0.0875 |
| abrupt/class_prior | det4_s1_wrddm_chddma | 50 | 0.0612 | 0.0625 | 0.0600 | 0.0600 | 449.3333 | 0.4500 | 0.1330 | ABCD | -0.0718 |
| abrupt/class_prior | det4_s1_wrddm_crddm | 50 | 0.0707 | 0.0414 | 0.2407 | 0.1800 | 1296.4444 | 3.0100 | 0.1330 | ABCD | -0.0623 |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 50 | 0.0511 | 0.0314 | 0.1373 | 0.1200 | 969.1667 | 2.1600 | 0.0920 | STEPD | -0.0409 |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 50 | 0.0476 | 0.0588 | 0.0400 | 0.0400 | 2130.0000 | 0.3200 | 0.0920 | STEPD | -0.0444 |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 50 | 0.0536 | 0.0484 | 0.0600 | 0.0600 | 1388.3333 | 0.5900 | 0.0920 | STEPD | -0.0384 |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 50 | 0.0849 | 0.0531 | 0.2115 | 0.1800 | 1709.8889 | 1.9600 | 0.0920 | STEPD | -0.0071 |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0900 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 50 | 0.0294 | 0.0556 | 0.0200 | 0.0200 | 2195.0000 | 0.1700 | 0.0920 | STEPD | -0.0626 |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3500 | 0.0920 | STEPD | -0.0920 |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 50 | 0.0581 | 0.0349 | 0.1731 | 0.1400 | 1356.2857 | 2.4900 | 0.0920 | STEPD | -0.0339 |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 50 | 0.0670 | 0.0465 | 0.1200 | 0.1200 | 1677.8333 | 1.2300 | 0.0920 | STEPD | -0.0250 |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 50 | 0.0510 | 0.0374 | 0.0800 | 0.0800 | 1805.5000 | 1.0300 | 0.0920 | STEPD | -0.0410 |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 50 | 0.0606 | 0.0435 | 0.1000 | 0.1000 | 1774.6000 | 1.1000 | 0.0920 | STEPD | -0.0314 |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 50 | 0.0250 | 0.0333 | 0.0200 | 0.0200 | 922.0000 | 0.2900 | 0.0920 | STEPD | -0.0670 |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 50 | 0.0526 | 0.0469 | 0.0600 | 0.0600 | 457.3333 | 0.6100 | 0.0920 | STEPD | -0.0394 |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 50 | 0.0440 | 0.0488 | 0.0400 | 0.0400 | 1573.0000 | 0.3900 | 0.0920 | STEPD | -0.0480 |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 50 | 0.0417 | 0.0435 | 0.0400 | 0.0400 | 896.5000 | 0.4400 | 0.0920 | STEPD | -0.0503 |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 50 | 0.0204 | 0.0208 | 0.0200 | 0.0200 | 922.0000 | 0.4700 | 0.0920 | STEPD | -0.0716 |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 50 | 0.0628 | 0.0367 | 0.2182 | 0.1400 | 1038.7143 | 3.1500 | 0.0920 | STEPD | -0.0292 |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 50 | 0.3478 | 0.2128 | 0.9524 | 0.9400 | 399.2553 | 2.2200 | 1.0000 | ABCD(X) | -0.6522 |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 50 | 0.7455 | 0.6833 | 0.8200 | 0.8200 | 153.4146 | 0.1900 | 1.0000 | ABCD(X) | -0.2545 |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 50 | 0.4478 | 0.3571 | 0.6000 | 0.6000 | 165.0667 | 0.5400 | 1.0000 | ABCD(X) | -0.5522 |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 50 | 0.0606 | 0.1250 | 0.0400 | 0.0400 | 638.5000 | 0.1400 | 1.0000 | ABCD(X) | -0.9394 |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 50 | 0.3776 | 0.2348 | 0.9643 | 0.9600 | 124.6042 | 1.7600 | 1.0000 | ABCD(X) | -0.6224 |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1000 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 50 | 0.0800 | 0.1200 | 0.0600 | 0.0600 | 256.3333 | 0.2200 | 1.0000 | ABCD(X) | -0.9200 |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 50 | 0.2941 | 0.2941 | 0.2941 | 0.2800 | 386.2143 | 0.3600 | 1.0000 | ABCD(X) | -0.7059 |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 50 | 0.3247 | 0.1969 | 0.9259 | 0.9200 | 258.6087 | 2.0400 | 1.0000 | ABCD(X) | -0.6753 |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 50 | 0.4498 | 0.3013 | 0.8868 | 0.8800 | 398.5455 | 1.0900 | 1.0000 | ABCD(X) | -0.5502 |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 50 | 0.4481 | 0.3130 | 0.7885 | 0.7800 | 483.2308 | 0.9000 | 1.0000 | ABCD(X) | -0.5519 |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 50 | 0.4409 | 0.3060 | 0.7885 | 0.7800 | 434.7692 | 0.9300 | 1.0000 | ABCD(X) | -0.5591 |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 50 | 0.3542 | 0.3696 | 0.3400 | 0.3400 | 317.6471 | 0.2900 | 1.0000 | ABCD(X) | -0.6458 |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 50 | 0.4568 | 0.3364 | 0.7115 | 0.7000 | 196.2857 | 0.7300 | 1.0000 | ABCD(X) | -0.5432 |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 50 | 0.3636 | 0.3333 | 0.4000 | 0.4000 | 288.3500 | 0.4000 | 1.0000 | ABCD(X) | -0.6364 |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 50 | 0.3810 | 0.3636 | 0.4000 | 0.4000 | 388.1500 | 0.3500 | 1.0000 | ABCD(X) | -0.6190 |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 50 | 0.3866 | 0.3382 | 0.4510 | 0.4400 | 322.8636 | 0.4500 | 1.0000 | ABCD(X) | -0.6134 |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 50 | 0.2596 | 0.1538 | 0.8312 | 0.7400 | 204.8649 | 3.5200 | 1.0000 | ABCD(X) | -0.7404 |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 50 | 0.1529 | 0.0920 | 0.4528 | 0.4200 | 995.0476 | 2.3700 | 0.1720 | SEED | -0.0191 |
| abrupt/label_swap | det4_s0_wadwin_chddma | 50 | 0.2917 | 0.3182 | 0.2692 | 0.2400 | 368.2500 | 0.3000 | 0.1720 | SEED | 0.1197 |
| abrupt/label_swap | det4_s0_wadwin_crddm | 50 | 0.2114 | 0.1781 | 0.2600 | 0.2600 | 911.1538 | 0.6000 | 0.1720 | SEED | 0.0394 |
| abrupt/label_swap | det4_s0_whddma_cadwin | 50 | 0.0667 | 0.2000 | 0.0400 | 0.0400 | 2224.5000 | 0.0800 | 0.1720 | SEED | -0.1053 |
| abrupt/label_swap | det4_s0_whddma_chddma | 50 | 0.1277 | 0.0811 | 0.3000 | 0.3000 | 442.2667 | 1.7000 | 0.1720 | SEED | -0.0443 |
| abrupt/label_swap | det4_s0_whddma_crddm | 50 | 0.0533 | 0.0800 | 0.0400 | 0.0400 | 1189.5000 | 0.2300 | 0.1720 | SEED | -0.1187 |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 50 | 0.0769 | 0.1071 | 0.0600 | 0.0600 | 537.6667 | 0.2500 | 0.1720 | SEED | -0.0951 |
| abrupt/label_swap | det4_s0_wrddm_chddma | 50 | 0.0723 | 0.0909 | 0.0600 | 0.0600 | 743.0000 | 0.3000 | 0.1720 | SEED | -0.0997 |
| abrupt/label_swap | det4_s0_wrddm_crddm | 50 | 0.1176 | 0.0711 | 0.3396 | 0.3000 | 1018.9333 | 2.3500 | 0.1720 | SEED | -0.0544 |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 50 | 0.1758 | 0.1212 | 0.3200 | 0.3200 | 672.5625 | 1.1600 | 0.1720 | SEED | 0.0038 |
| abrupt/label_swap | det4_s1_wadwin_chddma | 50 | 0.1216 | 0.0918 | 0.1800 | 0.1800 | 529.7778 | 0.8900 | 0.1720 | SEED | -0.0504 |
| abrupt/label_swap | det4_s1_wadwin_crddm | 50 | 0.1176 | 0.0874 | 0.1800 | 0.1800 | 519.0000 | 0.9400 | 0.1720 | SEED | -0.0544 |
| abrupt/label_swap | det4_s1_whddma_cadwin | 50 | 0.0290 | 0.0526 | 0.0200 | 0.0200 | 474.0000 | 0.1800 | 0.1720 | SEED | -0.1430 |
| abrupt/label_swap | det4_s1_whddma_chddma | 50 | 0.2097 | 0.1757 | 0.2600 | 0.2600 | 680.0000 | 0.6100 | 0.1720 | SEED | 0.0377 |
| abrupt/label_swap | det4_s1_whddma_crddm | 50 | 0.0241 | 0.0303 | 0.0200 | 0.0200 | 474.0000 | 0.3200 | 0.1720 | SEED | -0.1479 |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 50 | 0.0222 | 0.0250 | 0.0200 | 0.0200 | 474.0000 | 0.3900 | 0.1720 | SEED | -0.1498 |
| abrupt/label_swap | det4_s1_wrddm_chddma | 50 | 0.1000 | 0.1333 | 0.0800 | 0.0800 | 1148.5000 | 0.2600 | 0.1720 | SEED | -0.0720 |
| abrupt/label_swap | det4_s1_wrddm_crddm | 50 | 0.1552 | 0.0909 | 0.5294 | 0.3600 | 581.0556 | 3.6000 | 0.1720 | SEED | -0.0168 |
| gradual/class_prior | det4_s0_wadwin_cadwin | 50 | 0.0824 | 0.0509 | 0.2157 | 0.2000 | 1682.9000 | 2.0500 | 0.1890 | STEPD | -0.1066 |
| gradual/class_prior | det4_s0_wadwin_chddma | 50 | 0.1687 | 0.2121 | 0.1400 | 0.1400 | 1731.8571 | 0.2600 | 0.1890 | STEPD | -0.0203 |
| gradual/class_prior | det4_s0_wadwin_crddm | 50 | 0.0909 | 0.0833 | 0.1000 | 0.1000 | 1764.2000 | 0.5500 | 0.1890 | STEPD | -0.0981 |
| gradual/class_prior | det4_s0_whddma_cadwin | 50 | 0.0351 | 0.1429 | 0.0200 | 0.0200 | 2201.0000 | 0.0600 | 0.1890 | STEPD | -0.1539 |
| gradual/class_prior | det4_s0_whddma_chddma | 50 | 0.0533 | 0.0343 | 0.1200 | 0.1200 | 1574.8333 | 1.6900 | 0.1890 | STEPD | -0.1357 |
| gradual/class_prior | det4_s0_whddma_crddm | 50 | 0.0317 | 0.0769 | 0.0200 | 0.0200 | 1988.0000 | 0.1200 | 0.1890 | STEPD | -0.1573 |
| gradual/class_prior | det4_s0_wrddm_cadwin | 50 | 0.0563 | 0.0952 | 0.0400 | 0.0400 | 1504.0000 | 0.1900 | 0.1890 | STEPD | -0.1327 |
| gradual/class_prior | det4_s0_wrddm_chddma | 50 | 0.0732 | 0.0938 | 0.0600 | 0.0600 | 995.3333 | 0.2900 | 0.1890 | STEPD | -0.1158 |
| gradual/class_prior | det4_s0_wrddm_crddm | 50 | 0.1284 | 0.0785 | 0.3519 | 0.3000 | 1190.2000 | 2.2300 | 0.1890 | STEPD | -0.0606 |
| gradual/class_prior | det4_s1_wadwin_cadwin | 50 | 0.1164 | 0.0791 | 0.2200 | 0.2200 | 1711.4545 | 1.2800 | 0.1890 | STEPD | -0.0726 |
| gradual/class_prior | det4_s1_wadwin_chddma | 50 | 0.0892 | 0.0654 | 0.1400 | 0.1400 | 1584.7143 | 1.0000 | 0.1890 | STEPD | -0.0998 |
| gradual/class_prior | det4_s1_wadwin_crddm | 50 | 0.0870 | 0.0636 | 0.1373 | 0.1200 | 1325.0000 | 1.0300 | 0.1890 | STEPD | -0.1020 |
| gradual/class_prior | det4_s1_whddma_cadwin | 50 | 0.0506 | 0.0690 | 0.0400 | 0.0400 | 1715.0000 | 0.2700 | 0.1890 | STEPD | -0.1384 |
| gradual/class_prior | det4_s1_whddma_chddma | 50 | 0.1606 | 0.1264 | 0.2200 | 0.2200 | 1695.0000 | 0.7600 | 0.1890 | STEPD | -0.0284 |
| gradual/class_prior | det4_s1_whddma_crddm | 50 | 0.0235 | 0.0286 | 0.0200 | 0.0200 | 2287.0000 | 0.3400 | 0.1890 | STEPD | -0.1655 |
| gradual/class_prior | det4_s1_wrddm_cadwin | 50 | 0.0444 | 0.0500 | 0.0400 | 0.0400 | 1322.0000 | 0.3800 | 0.1890 | STEPD | -0.1446 |
| gradual/class_prior | det4_s1_wrddm_chddma | 50 | 0.1373 | 0.1346 | 0.1400 | 0.1400 | 1617.1429 | 0.4500 | 0.1890 | STEPD | -0.0517 |
| gradual/class_prior | det4_s1_wrddm_crddm | 50 | 0.1292 | 0.0765 | 0.4167 | 0.3000 | 1012.6000 | 3.0200 | 0.1890 | STEPD | -0.0598 |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 50 | 0.0308 | 0.0190 | 0.0800 | 0.0800 | 1454.5000 | 2.0600 | 0.0650 | HDDM_W | -0.0342 |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 50 | 0.0408 | 0.0417 | 0.0400 | 0.0400 | 1950.5000 | 0.4600 | 0.0650 | HDDM_W | -0.0242 |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 50 | 0.0522 | 0.0462 | 0.0600 | 0.0600 | 1384.6667 | 0.6200 | 0.0650 | HDDM_W | -0.0128 |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0900 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_whddma_chddma | 50 | 0.0403 | 0.0253 | 0.1000 | 0.1000 | 775.4000 | 1.9300 | 0.0650 | HDDM_W | -0.0247 |
| gradual/feature_filtering | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1300 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 50 | 0.0286 | 0.0500 | 0.0200 | 0.0200 | 99.0000 | 0.1900 | 0.0650 | HDDM_W | -0.0364 |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4400 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 50 | 0.0451 | 0.0279 | 0.1176 | 0.1000 | 1093.6000 | 2.0900 | 0.0650 | HDDM_W | -0.0199 |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 50 | 0.0248 | 0.0180 | 0.0400 | 0.0400 | 1980.5000 | 1.0900 | 0.0650 | HDDM_W | -0.0402 |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 50 | 0.0426 | 0.0330 | 0.0600 | 0.0600 | 1730.0000 | 0.8800 | 0.0650 | HDDM_W | -0.0224 |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 50 | 0.0423 | 0.0326 | 0.0600 | 0.0600 | 1538.0000 | 0.8900 | 0.0650 | HDDM_W | -0.0227 |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2900 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_whddma_chddma | 50 | 0.0550 | 0.0508 | 0.0600 | 0.0600 | 1994.3333 | 0.5600 | 0.0650 | HDDM_W | -0.0100 |
| gradual/feature_filtering | det4_s1_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4000 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3300 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3700 | 0.0650 | HDDM_W | -0.0650 |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 50 | 0.0663 | 0.0393 | 0.2115 | 0.1800 | 1159.1111 | 2.6900 | 0.0650 | HDDM_W | 0.0013 |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 50 | 0.2602 | 0.1524 | 0.8889 | 0.8800 | 1062.2273 | 2.6700 | 0.6670 | ABCD(X) | -0.4068 |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 50 | 0.6508 | 0.5467 | 0.8039 | 0.8000 | 945.8250 | 0.3400 | 0.6670 | ABCD(X) | -0.0162 |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 50 | 0.5294 | 0.4235 | 0.7059 | 0.7000 | 973.6286 | 0.4900 | 0.6670 | ABCD(X) | -0.1376 |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 50 | 0.4110 | 0.6522 | 0.3000 | 0.3000 | 1764.8667 | 0.0800 | 0.6670 | ABCD(X) | -0.2560 |
| gradual/feature_permutation | det4_s0_whddma_chddma | 50 | 0.3821 | 0.2423 | 0.9038 | 0.9000 | 699.7778 | 1.4700 | 0.6670 | ABCD(X) | -0.2849 |
| gradual/feature_permutation | det4_s0_whddma_crddm | 50 | 0.0968 | 0.2727 | 0.0588 | 0.0400 | 1713.0000 | 0.0800 | 0.6670 | ABCD(X) | -0.5702 |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 50 | 0.3913 | 0.4286 | 0.3600 | 0.3600 | 1359.1667 | 0.2400 | 0.6670 | ABCD(X) | -0.2757 |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 50 | 0.3740 | 0.3151 | 0.4600 | 0.4600 | 941.8696 | 0.5000 | 0.6670 | ABCD(X) | -0.2930 |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 50 | 0.3512 | 0.2161 | 0.9365 | 0.9200 | 703.4783 | 2.1400 | 0.6670 | ABCD(X) | -0.3158 |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 50 | 0.3670 | 0.2395 | 0.7843 | 0.7800 | 945.6410 | 1.2700 | 0.6670 | ABCD(X) | -0.3000 |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 50 | 0.4084 | 0.2766 | 0.7800 | 0.7800 | 1012.2821 | 1.0200 | 0.6670 | ABCD(X) | -0.2586 |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 50 | 0.4194 | 0.2868 | 0.7800 | 0.7800 | 959.1795 | 0.9700 | 0.6670 | ABCD(X) | -0.2476 |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 50 | 0.1856 | 0.1915 | 0.1800 | 0.1800 | 1376.0000 | 0.3800 | 0.6670 | ABCD(X) | -0.4814 |
| gradual/feature_permutation | det4_s1_whddma_chddma | 50 | 0.4268 | 0.3182 | 0.6481 | 0.6200 | 1015.8065 | 0.7500 | 0.6670 | ABCD(X) | -0.2402 |
| gradual/feature_permutation | det4_s1_whddma_crddm | 50 | 0.1782 | 0.1765 | 0.1800 | 0.1800 | 1264.0000 | 0.4200 | 0.6670 | ABCD(X) | -0.4888 |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 50 | 0.3478 | 0.3077 | 0.4000 | 0.4000 | 1510.8500 | 0.4500 | 0.6670 | ABCD(X) | -0.3192 |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 50 | 0.3415 | 0.2917 | 0.4118 | 0.4000 | 1293.4000 | 0.5100 | 0.6670 | ABCD(X) | -0.3255 |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 50 | 0.2847 | 0.1702 | 0.8696 | 0.7600 | 916.4211 | 3.9000 | 0.6670 | ABCD(X) | -0.3823 |
| gradual/label_swap | det4_s0_wadwin_cadwin | 50 | 0.1342 | 0.0814 | 0.3818 | 0.3200 | 1169.0000 | 2.3700 | 0.1750 | ABCD | -0.0408 |
| gradual/label_swap | det4_s0_wadwin_chddma | 50 | 0.2128 | 0.2326 | 0.1961 | 0.1800 | 1416.6667 | 0.3300 | 0.1750 | ABCD | 0.0378 |
| gradual/label_swap | det4_s0_wadwin_crddm | 50 | 0.2087 | 0.1846 | 0.2400 | 0.2400 | 1464.9167 | 0.5300 | 0.1750 | ABCD | 0.0337 |
| gradual/label_swap | det4_s0_whddma_cadwin | 50 | 0.0923 | 0.2000 | 0.0600 | 0.0600 | 1862.3333 | 0.1200 | 0.1750 | ABCD | -0.0827 |
| gradual/label_swap | det4_s0_whddma_chddma | 50 | 0.1048 | 0.0660 | 0.2549 | 0.2400 | 1152.5000 | 1.8400 | 0.1750 | ABCD | -0.0702 |
| gradual/label_swap | det4_s0_whddma_crddm | 50 | 0.0606 | 0.1250 | 0.0400 | 0.0400 | 1073.5000 | 0.1400 | 0.1750 | ABCD | -0.1144 |
| gradual/label_swap | det4_s0_wrddm_cadwin | 50 | 0.0779 | 0.1111 | 0.0600 | 0.0600 | 1727.6667 | 0.2400 | 0.1750 | ABCD | -0.0971 |
| gradual/label_swap | det4_s0_wrddm_chddma | 50 | 0.0426 | 0.0455 | 0.0400 | 0.0400 | 1077.5000 | 0.4200 | 0.1750 | ABCD | -0.1324 |
| gradual/label_swap | det4_s0_wrddm_crddm | 50 | 0.1280 | 0.0775 | 0.3684 | 0.2800 | 1291.5000 | 2.5000 | 0.1750 | ABCD | -0.0470 |
| gradual/label_swap | det4_s1_wadwin_cadwin | 50 | 0.1596 | 0.1103 | 0.2885 | 0.2600 | 1528.1538 | 1.2100 | 0.1750 | ABCD | -0.0154 |
| gradual/label_swap | det4_s1_wadwin_chddma | 50 | 0.1882 | 0.1345 | 0.3137 | 0.3000 | 1613.0000 | 1.0300 | 0.1750 | ABCD | 0.0132 |
| gradual/label_swap | det4_s1_wadwin_crddm | 50 | 0.2093 | 0.1488 | 0.3529 | 0.3400 | 1535.0000 | 1.0300 | 0.1750 | ABCD | 0.0343 |
| gradual/label_swap | det4_s1_whddma_cadwin | 50 | 0.0723 | 0.0909 | 0.0600 | 0.0600 | 1102.0000 | 0.3000 | 0.1750 | ABCD | -0.1027 |
| gradual/label_swap | det4_s1_whddma_chddma | 50 | 0.1495 | 0.1429 | 0.1569 | 0.1400 | 1283.8571 | 0.4800 | 0.1750 | ABCD | -0.0255 |
| gradual/label_swap | det4_s1_whddma_crddm | 50 | 0.0682 | 0.0789 | 0.0600 | 0.0600 | 1465.0000 | 0.3500 | 0.1750 | ABCD | -0.1068 |
| gradual/label_swap | det4_s1_wrddm_cadwin | 50 | 0.0842 | 0.0889 | 0.0800 | 0.0800 | 1863.0000 | 0.4100 | 0.1750 | ABCD | -0.0908 |
| gradual/label_swap | det4_s1_wrddm_chddma | 50 | 0.1905 | 0.1818 | 0.2000 | 0.2000 | 1402.4000 | 0.4500 | 0.1750 | ABCD | 0.0155 |
| gradual/label_swap | det4_s1_wrddm_crddm | 50 | 0.1284 | 0.0754 | 0.4333 | 0.3200 | 1297.4375 | 3.1900 | 0.1750 | ABCD | -0.0466 |

### injected_paper_electricity

Only preset kinds ['detector'] follow the literature protocol on this dataset; other rows appear only with --include-noncomparable.

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 30 | 0.2687 | 0.2432 | 0.3000 | 0.3000 | 1387.5556 | 0.6179 | 0.6980 | ADWIN | -0.4293 |
| abrupt/class_prior | det4_s0_wadwin_chddma | 50 | 0.3099 | 0.5238 | 0.2200 | 0.2200 | 1552.9091 | 0.2207 | 0.6980 | ADWIN | -0.3881 |
| abrupt/class_prior | det4_s0_wadwin_crddm | 50 | 0.2286 | 0.4000 | 0.1600 | 0.1600 | 1694.3750 | 0.2648 | 0.6980 | ADWIN | -0.4694 |
| abrupt/class_prior | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s0_whddma_chddma | 30 | 0.2000 | 0.4000 | 0.1333 | 0.1333 | 1376.0000 | 0.1324 | 0.6980 | ADWIN | -0.4980 |
| abrupt/class_prior | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.6980 | ADWIN | -0.6980 |
| abrupt/class_prior | det4_s0_wrddm_chddma | 50 | 0.0714 | 0.3333 | 0.0400 | 0.0400 | 792.0000 | 0.0883 | 0.6980 | ADWIN | -0.6266 |
| abrupt/class_prior | det4_s0_wrddm_crddm | 30 | 0.1786 | 0.1923 | 0.1667 | 0.1667 | 1388.4000 | 0.4635 | 0.6980 | ADWIN | -0.5194 |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 30 | 0.3158 | 0.3333 | 0.3000 | 0.3000 | 1774.3333 | 0.3972 | 0.6980 | ADWIN | -0.3822 |
| abrupt/class_prior | det4_s1_wadwin_chddma | 50 | 0.1071 | 0.5000 | 0.0600 | 0.0600 | 1375.6667 | 0.0662 | 0.6980 | ADWIN | -0.5909 |
| abrupt/class_prior | det4_s1_wadwin_crddm | 50 | 0.0385 | 0.5000 | 0.0200 | 0.0200 | 986.0000 | 0.0221 | 0.6980 | ADWIN | -0.6595 |
| abrupt/class_prior | det4_s1_whddma_cadwin | 50 | 0.0769 | 1.0000 | 0.0400 | 0.0400 | 1541.0000 | 0.0000 | 0.6980 | ADWIN | -0.6211 |
| abrupt/class_prior | det4_s1_whddma_chddma | 30 | 0.5556 | 0.6250 | 0.5000 | 0.5000 | 1130.7333 | 0.1986 | 0.6980 | ADWIN | -0.1424 |
| abrupt/class_prior | det4_s1_whddma_crddm | 50 | 0.1429 | 0.6667 | 0.0800 | 0.0800 | 461.5000 | 0.0441 | 0.6980 | ADWIN | -0.5551 |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 50 | 0.1695 | 0.5556 | 0.1000 | 0.1000 | 1230.2000 | 0.0883 | 0.6980 | ADWIN | -0.5285 |
| abrupt/class_prior | det4_s1_wrddm_chddma | 50 | 0.2333 | 0.7000 | 0.1400 | 0.1400 | 957.7143 | 0.0662 | 0.6980 | ADWIN | -0.4647 |
| abrupt/class_prior | det4_s1_wrddm_crddm | 50 | 0.2997 | 0.1972 | 0.6232 | 0.4800 | 1016.8750 | 3.8621 | 0.6980 | ADWIN | -0.3983 |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 30 | 0.1111 | 0.1250 | 0.1000 | 0.1000 | 1298.3333 | 0.4635 | 0.2450 | CUSUM | -0.1339 |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 50 | 0.0357 | 0.1667 | 0.0200 | 0.0200 | 2421.0000 | 0.1103 | 0.2450 | CUSUM | -0.2093 |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1986 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 30 | 0.0435 | 0.0625 | 0.0333 | 0.0333 | 1535.0000 | 0.3310 | 0.2450 | CUSUM | -0.2015 |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 30 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2869 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 30 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0883 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0441 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0883 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 30 | 0.1111 | 0.3333 | 0.0667 | 0.0667 | 940.0000 | 0.0883 | 0.2450 | CUSUM | -0.1339 |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0883 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0441 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 50 | 0.0584 | 0.0465 | 0.0784 | 0.0600 | 975.3333 | 1.8097 | 0.2450 | CUSUM | -0.1866 |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 30 | 0.6000 | 0.5333 | 0.6857 | 0.6333 | 770.5789 | 0.4635 | 1.0000 | ABCD(X) | -0.4000 |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 50 | 0.6667 | 0.8710 | 0.5400 | 0.5400 | 181.5185 | 0.0883 | 1.0000 | ABCD(X) | -0.3333 |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 50 | 0.5195 | 0.7407 | 0.4000 | 0.4000 | 403.3500 | 0.1545 | 1.0000 | ABCD(X) | -0.4805 |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 50 | 0.0392 | 1.0000 | 0.0200 | 0.0200 | 259.0000 | 0.0000 | 1.0000 | ABCD(X) | -0.9608 |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 30 | 0.7711 | 0.6809 | 0.8889 | 0.8667 | 166.9615 | 0.3310 | 1.0000 | ABCD(X) | -0.2289 |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 50 | 0.0769 | 1.0000 | 0.0400 | 0.0400 | 368.0000 | 0.0000 | 1.0000 | ABCD(X) | -0.9231 |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 50 | 0.1034 | 0.3750 | 0.0600 | 0.0600 | 850.0000 | 0.1103 | 1.0000 | ABCD(X) | -0.8966 |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 50 | 0.2000 | 0.3684 | 0.1373 | 0.1200 | 181.3333 | 0.2648 | 1.0000 | ABCD(X) | -0.8000 |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 30 | 0.6139 | 0.4921 | 0.8158 | 0.7667 | 512.3478 | 0.7062 | 1.0000 | ABCD(X) | -0.3861 |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 30 | 0.8065 | 0.7812 | 0.8333 | 0.8333 | 740.2400 | 0.1545 | 1.0000 | ABCD(X) | -0.1935 |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 50 | 0.7778 | 0.8750 | 0.7000 | 0.7000 | 871.9429 | 0.1103 | 1.0000 | ABCD(X) | -0.2222 |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 50 | 0.8211 | 0.8667 | 0.7800 | 0.7800 | 852.2308 | 0.1324 | 1.0000 | ABCD(X) | -0.1789 |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 50 | 0.3000 | 0.9000 | 0.1800 | 0.1800 | 828.5556 | 0.0221 | 1.0000 | ABCD(X) | -0.7000 |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 30 | 0.7895 | 0.6818 | 0.9375 | 0.9333 | 509.9286 | 0.3090 | 1.0000 | ABCD(X) | -0.2105 |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 50 | 0.3889 | 0.7000 | 0.2692 | 0.2400 | 642.5833 | 0.1324 | 1.0000 | ABCD(X) | -0.6111 |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 50 | 0.5352 | 0.9048 | 0.3800 | 0.3800 | 815.6842 | 0.0441 | 1.0000 | ABCD(X) | -0.4648 |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 50 | 0.6133 | 0.9583 | 0.4510 | 0.4400 | 713.3182 | 0.0221 | 1.0000 | ABCD(X) | -0.3867 |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 50 | 0.4516 | 0.2961 | 0.9515 | 0.9000 | 481.2444 | 5.1421 | 1.0000 | ABCD(X) | -0.5484 |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 30 | 0.6761 | 0.6000 | 0.7742 | 0.7667 | 728.4783 | 0.3531 | 0.5660 | SEED | 0.1101 |
| abrupt/label_swap | det4_s0_wadwin_chddma | 50 | 0.5432 | 0.7333 | 0.4314 | 0.4200 | 543.7143 | 0.1766 | 0.5660 | SEED | -0.0228 |
| abrupt/label_swap | det4_s0_wadwin_crddm | 50 | 0.5185 | 0.6774 | 0.4200 | 0.4200 | 677.8095 | 0.2207 | 0.5660 | SEED | -0.0475 |
| abrupt/label_swap | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5660 | SEED | -0.5660 |
| abrupt/label_swap | det4_s0_whddma_chddma | 30 | 0.7419 | 0.7188 | 0.7667 | 0.7667 | 213.3478 | 0.1986 | 0.5660 | SEED | 0.1759 |
| abrupt/label_swap | det4_s0_whddma_crddm | 50 | 0.0392 | 1.0000 | 0.0200 | 0.0200 | 159.0000 | 0.0000 | 0.5660 | SEED | -0.5268 |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 50 | 0.1481 | 1.0000 | 0.0800 | 0.0800 | 618.5000 | 0.0000 | 0.5660 | SEED | -0.4179 |
| abrupt/label_swap | det4_s0_wrddm_chddma | 50 | 0.4545 | 0.9375 | 0.3000 | 0.3000 | 553.8000 | 0.0221 | 0.5660 | SEED | -0.1115 |
| abrupt/label_swap | det4_s0_wrddm_crddm | 30 | 0.7143 | 0.6579 | 0.7812 | 0.7667 | 475.6957 | 0.2869 | 0.5660 | SEED | 0.1483 |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 30 | 0.7931 | 0.8214 | 0.7667 | 0.7667 | 529.4783 | 0.1103 | 0.5660 | SEED | 0.2271 |
| abrupt/label_swap | det4_s1_wadwin_chddma | 50 | 0.7013 | 1.0000 | 0.5400 | 0.5400 | 476.2222 | 0.0000 | 0.5660 | SEED | 0.1353 |
| abrupt/label_swap | det4_s1_wadwin_crddm | 50 | 0.7317 | 0.9375 | 0.6000 | 0.6000 | 484.6000 | 0.0441 | 0.5660 | SEED | 0.1657 |
| abrupt/label_swap | det4_s1_whddma_cadwin | 50 | 0.2456 | 1.0000 | 0.1400 | 0.1400 | 374.0000 | 0.0000 | 0.5660 | SEED | -0.3204 |
| abrupt/label_swap | det4_s1_whddma_chddma | 30 | 0.8387 | 0.8125 | 0.8667 | 0.8667 | 426.1154 | 0.1324 | 0.5660 | SEED | 0.2727 |
| abrupt/label_swap | det4_s1_whddma_crddm | 50 | 0.2712 | 0.8889 | 0.1600 | 0.1600 | 578.8750 | 0.0221 | 0.5660 | SEED | -0.2948 |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 50 | 0.3492 | 0.8462 | 0.2200 | 0.2200 | 407.4545 | 0.0441 | 0.5660 | SEED | -0.2168 |
| abrupt/label_swap | det4_s1_wrddm_chddma | 50 | 0.5000 | 0.9444 | 0.3400 | 0.3400 | 419.1765 | 0.0221 | 0.5660 | SEED | -0.0660 |
| abrupt/label_swap | det4_s1_wrddm_crddm | 50 | 0.4677 | 0.3357 | 0.7705 | 0.7200 | 350.9722 | 2.0524 | 0.5660 | SEED | -0.0983 |
| gradual/class_prior | det4_s0_wadwin_cadwin | 30 | 0.1111 | 0.0952 | 0.1333 | 0.1333 | 2176.7500 | 0.8386 | 0.2950 | STEPD | -0.1839 |
| gradual/class_prior | det4_s0_wadwin_chddma | 50 | 0.0625 | 0.1429 | 0.0400 | 0.0400 | 2336.5000 | 0.2648 | 0.2950 | STEPD | -0.2325 |
| gradual/class_prior | det4_s0_wadwin_crddm | 50 | 0.0923 | 0.2000 | 0.0600 | 0.0600 | 2235.3333 | 0.2648 | 0.2950 | STEPD | -0.2027 |
| gradual/class_prior | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s0_whddma_chddma | 30 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1103 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s0_whddma_crddm | 50 | 0.0392 | 1.0000 | 0.0200 | 0.0200 | 2056.0000 | 0.0000 | 0.2950 | STEPD | -0.2558 |
| gradual/class_prior | det4_s0_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0662 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s0_wrddm_chddma | 50 | 0.0678 | 0.2222 | 0.0400 | 0.0400 | 2310.5000 | 0.1545 | 0.2950 | STEPD | -0.2272 |
| gradual/class_prior | det4_s0_wrddm_crddm | 30 | 0.1111 | 0.1304 | 0.0968 | 0.0667 | 1902.5000 | 0.4414 | 0.2950 | STEPD | -0.1839 |
| gradual/class_prior | det4_s1_wadwin_cadwin | 30 | 0.1270 | 0.1212 | 0.1333 | 0.1333 | 2435.2500 | 0.6400 | 0.2950 | STEPD | -0.1680 |
| gradual/class_prior | det4_s1_wadwin_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1766 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s1_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1545 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s1_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.2950 | STEPD | -0.2950 |
| gradual/class_prior | det4_s1_whddma_chddma | 30 | 0.2041 | 0.2632 | 0.1667 | 0.1667 | 2108.0000 | 0.3090 | 0.2950 | STEPD | -0.0909 |
| gradual/class_prior | det4_s1_whddma_crddm | 50 | 0.0714 | 0.3333 | 0.0400 | 0.0400 | 2252.5000 | 0.0883 | 0.2950 | STEPD | -0.2236 |
| gradual/class_prior | det4_s1_wrddm_cadwin | 50 | 0.0317 | 0.0769 | 0.0200 | 0.0200 | 2435.0000 | 0.2648 | 0.2950 | STEPD | -0.2633 |
| gradual/class_prior | det4_s1_wrddm_chddma | 50 | 0.1471 | 0.2778 | 0.1000 | 0.1000 | 2124.6000 | 0.2869 | 0.2950 | STEPD | -0.1479 |
| gradual/class_prior | det4_s1_wrddm_crddm | 50 | 0.1495 | 0.1006 | 0.2909 | 0.2200 | 1754.6364 | 3.1559 | 0.2950 | STEPD | -0.1455 |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 30 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.4855 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 50 | 0.0357 | 0.1667 | 0.0200 | 0.0200 | 1915.0000 | 0.1103 | 0.1470 | STUDD | -0.1113 |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1545 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_whddma_chddma | 30 | 0.0500 | 0.1000 | 0.0333 | 0.0333 | 1008.0000 | 0.1986 | 0.1470 | STUDD | -0.0970 |
| gradual/feature_filtering | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 30 | 0.1695 | 0.1923 | 0.1515 | 0.0667 | 1682.5000 | 0.4635 | 0.1470 | STUDD | 0.0225 |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 30 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1986 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_whddma_chddma | 30 | 0.0500 | 0.1000 | 0.0333 | 0.0333 | 165.0000 | 0.1986 | 0.1470 | STUDD | -0.0970 |
| gradual/feature_filtering | det4_s1_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0221 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 50 | 0.0479 | 0.0348 | 0.0769 | 0.0400 | 1634.5000 | 2.4497 | 0.1470 | STUDD | -0.0991 |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 30 | 0.4091 | 0.3158 | 0.5806 | 0.5667 | 1609.9412 | 0.8607 | 0.9840 | ABCD(X) | -0.5749 |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 50 | 0.5618 | 0.6410 | 0.5000 | 0.5000 | 1238.1600 | 0.3090 | 0.9840 | ABCD(X) | -0.4222 |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 50 | 0.6190 | 0.7647 | 0.5200 | 0.5200 | 1280.1923 | 0.1766 | 0.9840 | ABCD(X) | -0.3650 |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 50 | 0.0741 | 0.5000 | 0.0400 | 0.0400 | 1942.0000 | 0.0441 | 0.9840 | ABCD(X) | -0.9099 |
| gradual/feature_permutation | det4_s0_whddma_chddma | 30 | 0.6667 | 0.6216 | 0.7188 | 0.7000 | 1273.6190 | 0.3090 | 0.9840 | ABCD(X) | -0.3173 |
| gradual/feature_permutation | det4_s0_whddma_crddm | 50 | 0.1429 | 0.6667 | 0.0800 | 0.0800 | 1840.2500 | 0.0441 | 0.9840 | ABCD(X) | -0.8411 |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 50 | 0.3030 | 0.6250 | 0.2000 | 0.2000 | 1478.0000 | 0.1324 | 0.9840 | ABCD(X) | -0.6810 |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 50 | 0.5600 | 0.8750 | 0.4118 | 0.4000 | 1200.3000 | 0.0662 | 0.9840 | ABCD(X) | -0.4240 |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 30 | 0.6331 | 0.4944 | 0.8800 | 0.8000 | 1235.5417 | 0.9931 | 0.9840 | ABCD(X) | -0.3509 |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 30 | 0.7143 | 0.6410 | 0.8065 | 0.8000 | 1610.8750 | 0.3090 | 0.9840 | ABCD(X) | -0.2697 |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 50 | 0.5618 | 0.6410 | 0.5000 | 0.5000 | 1872.4000 | 0.3090 | 0.9840 | ABCD(X) | -0.4222 |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 50 | 0.5747 | 0.6757 | 0.5000 | 0.5000 | 1875.8400 | 0.2648 | 0.9840 | ABCD(X) | -0.4093 |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 50 | 0.2769 | 0.6000 | 0.1800 | 0.1800 | 1636.3333 | 0.1324 | 0.9840 | ABCD(X) | -0.7071 |
| gradual/feature_permutation | det4_s1_whddma_chddma | 30 | 0.7654 | 0.6327 | 0.9688 | 0.9667 | 1238.3103 | 0.3972 | 0.9840 | ABCD(X) | -0.2186 |
| gradual/feature_permutation | det4_s1_whddma_crddm | 50 | 0.3611 | 0.5909 | 0.2600 | 0.2600 | 1334.0769 | 0.1986 | 0.9840 | ABCD(X) | -0.6229 |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 50 | 0.3562 | 0.5652 | 0.2600 | 0.2600 | 1733.4615 | 0.2207 | 0.9840 | ABCD(X) | -0.6278 |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 50 | 0.5591 | 0.6190 | 0.5098 | 0.5000 | 1306.0400 | 0.3531 | 0.9840 | ABCD(X) | -0.4249 |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 50 | 0.4323 | 0.2829 | 0.9167 | 0.8200 | 1116.4390 | 5.5394 | 0.9840 | ABCD(X) | -0.5517 |
| gradual/label_swap | det4_s0_wadwin_cadwin | 30 | 0.4731 | 0.4000 | 0.5789 | 0.4667 | 1446.5000 | 0.7283 | 0.3830 | STEPD | 0.0901 |
| gradual/label_swap | det4_s0_wadwin_chddma | 50 | 0.5952 | 0.7576 | 0.4902 | 0.4800 | 1235.8333 | 0.1766 | 0.3830 | STEPD | 0.2122 |
| gradual/label_swap | det4_s0_wadwin_crddm | 50 | 0.5909 | 0.6842 | 0.5200 | 0.5200 | 1498.3077 | 0.2648 | 0.3830 | STEPD | 0.2079 |
| gradual/label_swap | det4_s0_whddma_cadwin | 50 | 0.0755 | 0.6667 | 0.0400 | 0.0400 | 1864.0000 | 0.0221 | 0.3830 | STEPD | -0.3075 |
| gradual/label_swap | det4_s0_whddma_chddma | 30 | 0.5538 | 0.5143 | 0.6000 | 0.6000 | 1216.1111 | 0.3752 | 0.3830 | STEPD | 0.1708 |
| gradual/label_swap | det4_s0_whddma_crddm | 50 | 0.4062 | 0.9286 | 0.2600 | 0.2600 | 1364.9231 | 0.0221 | 0.3830 | STEPD | 0.0232 |
| gradual/label_swap | det4_s0_wrddm_cadwin | 50 | 0.3607 | 1.0000 | 0.2200 | 0.2200 | 1487.4545 | 0.0000 | 0.3830 | STEPD | -0.0223 |
| gradual/label_swap | det4_s0_wrddm_chddma | 50 | 0.4571 | 0.8000 | 0.3200 | 0.3200 | 1320.5625 | 0.0883 | 0.3830 | STEPD | 0.0741 |
| gradual/label_swap | det4_s0_wrddm_crddm | 30 | 0.6341 | 0.5652 | 0.7222 | 0.6667 | 1165.6500 | 0.4414 | 0.3830 | STEPD | 0.2511 |
| gradual/label_swap | det4_s1_wadwin_cadwin | 30 | 0.6389 | 0.5897 | 0.6970 | 0.6667 | 1662.5500 | 0.3531 | 0.3830 | STEPD | 0.2559 |
| gradual/label_swap | det4_s1_wadwin_chddma | 50 | 0.5316 | 0.7241 | 0.4200 | 0.4200 | 1536.0952 | 0.1766 | 0.3830 | STEPD | 0.1486 |
| gradual/label_swap | det4_s1_wadwin_crddm | 50 | 0.5823 | 0.7931 | 0.4600 | 0.4600 | 1582.2609 | 0.1324 | 0.3830 | STEPD | 0.1993 |
| gradual/label_swap | det4_s1_whddma_cadwin | 50 | 0.3385 | 0.7333 | 0.2200 | 0.2200 | 1552.5455 | 0.0883 | 0.3830 | STEPD | -0.0445 |
| gradual/label_swap | det4_s1_whddma_chddma | 30 | 0.7059 | 0.6857 | 0.7273 | 0.7000 | 1247.9048 | 0.2428 | 0.3830 | STEPD | 0.3229 |
| gradual/label_swap | det4_s1_whddma_crddm | 50 | 0.4110 | 0.6818 | 0.2941 | 0.2800 | 1278.0714 | 0.1545 | 0.3830 | STEPD | 0.0280 |
| gradual/label_swap | det4_s1_wrddm_cadwin | 50 | 0.3836 | 0.6087 | 0.2800 | 0.2800 | 1590.7143 | 0.1986 | 0.3830 | STEPD | 0.0006 |
| gradual/label_swap | det4_s1_wrddm_chddma | 50 | 0.5128 | 0.7143 | 0.4000 | 0.4000 | 1389.4500 | 0.1766 | 0.3830 | STEPD | 0.1298 |
| gradual/label_swap | det4_s1_wrddm_crddm | 50 | 0.5200 | 0.3801 | 0.8228 | 0.7200 | 1161.8056 | 2.3393 | 0.3830 | STEPD | 0.1370 |

### injected_paper_gas_sensor_drift

Only preset kinds ['detector'] follow the literature protocol on this dataset; other rows appear only with --include-noncomparable.

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det4_s0_wadwin_cadwin | 50 | 0.0339 | 0.1111 | 0.0200 | 0.0200 | 1175.0000 | 0.5751 | 0.4000 | DDM | -0.3661 |
| abrupt/class_prior | det4_s0_wadwin_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wadwin_crddm | 50 | 0.0377 | 0.3333 | 0.0200 | 0.0200 | 213.0000 | 0.1438 | 0.4000 | DDM | -0.3623 |
| abrupt/class_prior | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_whddma_chddma | 50 | 0.0317 | 0.0769 | 0.0200 | 0.0200 | 543.0000 | 0.8627 | 0.4000 | DDM | -0.3683 |
| abrupt/class_prior | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s0_wrddm_chddma | 50 | 0.0370 | 0.2500 | 0.0200 | 0.0200 | 731.0000 | 0.2157 | 0.4000 | DDM | -0.3630 |
| abrupt/class_prior | det4_s0_wrddm_crddm | 50 | 0.1558 | 0.2222 | 0.1200 | 0.1200 | 890.8333 | 1.5097 | 0.4000 | DDM | -0.2442 |
| abrupt/class_prior | det4_s1_wadwin_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2157 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wadwin_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1438 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_whddma_chddma | 50 | 0.0312 | 0.0714 | 0.0200 | 0.0200 | 969.0000 | 0.9346 | 0.4000 | DDM | -0.3688 |
| abrupt/class_prior | det4_s1_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1438 | 0.4000 | DDM | -0.4000 |
| abrupt/class_prior | det4_s1_wrddm_crddm | 50 | 0.2087 | 0.2000 | 0.2182 | 0.1400 | 733.7143 | 3.4508 | 0.4000 | DDM | -0.1913 |
| abrupt/feature_filtering | det4_s0_wadwin_cadwin | 50 | 0.5941 | 0.6122 | 0.5769 | 0.5600 | 831.5357 | 1.3659 | 0.5710 | SEED | 0.0231 |
| abrupt/feature_filtering | det4_s0_wadwin_chddma | 50 | 0.3226 | 0.8333 | 0.2000 | 0.2000 | 777.1000 | 0.1438 | 0.5710 | SEED | -0.2484 |
| abrupt/feature_filtering | det4_s0_wadwin_crddm | 50 | 0.1053 | 0.4286 | 0.0600 | 0.0600 | 609.6667 | 0.2876 | 0.5710 | SEED | -0.4657 |
| abrupt/feature_filtering | det4_s0_whddma_cadwin | 50 | 0.0392 | 1.0000 | 0.0200 | 0.0200 | 662.0000 | 0.0000 | 0.5710 | SEED | -0.5318 |
| abrupt/feature_filtering | det4_s0_whddma_chddma | 50 | 0.5055 | 0.5750 | 0.4510 | 0.4400 | 575.6818 | 1.2221 | 0.5710 | SEED | -0.0655 |
| abrupt/feature_filtering | det4_s0_whddma_crddm | 50 | 0.1053 | 0.4286 | 0.0600 | 0.0600 | 415.6667 | 0.2876 | 0.5710 | SEED | -0.4657 |
| abrupt/feature_filtering | det4_s0_wrddm_cadwin | 50 | 0.0392 | 1.0000 | 0.0200 | 0.0200 | 511.0000 | 0.0000 | 0.5710 | SEED | -0.5318 |
| abrupt/feature_filtering | det4_s0_wrddm_chddma | 50 | 0.2857 | 0.6923 | 0.1800 | 0.1800 | 411.6667 | 0.2876 | 0.5710 | SEED | -0.2853 |
| abrupt/feature_filtering | det4_s0_wrddm_crddm | 50 | 0.5294 | 0.5294 | 0.5294 | 0.5200 | 534.5000 | 1.7254 | 0.5710 | SEED | -0.0416 |
| abrupt/feature_filtering | det4_s1_wadwin_cadwin | 50 | 0.5745 | 0.6136 | 0.5400 | 0.5400 | 909.2963 | 1.2221 | 0.5710 | SEED | 0.0035 |
| abrupt/feature_filtering | det4_s1_wadwin_chddma | 50 | 0.3836 | 0.6087 | 0.2800 | 0.2800 | 801.5000 | 0.6470 | 0.5710 | SEED | -0.1874 |
| abrupt/feature_filtering | det4_s1_wadwin_crddm | 50 | 0.3947 | 0.5769 | 0.3000 | 0.3000 | 804.6667 | 0.7908 | 0.5710 | SEED | -0.1763 |
| abrupt/feature_filtering | det4_s1_whddma_cadwin | 50 | 0.1935 | 0.5000 | 0.1200 | 0.1200 | 563.0000 | 0.4313 | 0.5710 | SEED | -0.3775 |
| abrupt/feature_filtering | det4_s1_whddma_chddma | 50 | 0.4944 | 0.5789 | 0.4314 | 0.4200 | 437.0476 | 1.1503 | 0.5710 | SEED | -0.0766 |
| abrupt/feature_filtering | det4_s1_whddma_crddm | 50 | 0.1935 | 0.5000 | 0.1200 | 0.1200 | 527.1667 | 0.4313 | 0.5710 | SEED | -0.3775 |
| abrupt/feature_filtering | det4_s1_wrddm_cadwin | 50 | 0.2424 | 0.5000 | 0.1600 | 0.1600 | 687.0000 | 0.5751 | 0.5710 | SEED | -0.3286 |
| abrupt/feature_filtering | det4_s1_wrddm_chddma | 50 | 0.3529 | 0.6667 | 0.2400 | 0.2400 | 536.9167 | 0.4313 | 0.5710 | SEED | -0.2181 |
| abrupt/feature_filtering | det4_s1_wrddm_crddm | 50 | 0.4106 | 0.3263 | 0.5536 | 0.5000 | 532.1600 | 4.6010 | 0.5710 | SEED | -0.1604 |
| abrupt/feature_permutation | det4_s0_wadwin_cadwin | 50 | 0.8376 | 0.7778 | 0.9074 | 0.9000 | 477.9778 | 1.0065 | 1.0000 | ABCD(X) | -0.1624 |
| abrupt/feature_permutation | det4_s0_wadwin_chddma | 50 | 0.4308 | 0.9333 | 0.2800 | 0.2800 | 214.8571 | 0.0719 | 1.0000 | ABCD(X) | -0.5692 |
| abrupt/feature_permutation | det4_s0_wadwin_crddm | 50 | 0.3881 | 0.7647 | 0.2600 | 0.2600 | 390.3077 | 0.2876 | 1.0000 | ABCD(X) | -0.6119 |
| abrupt/feature_permutation | det4_s0_whddma_cadwin | 50 | 0.1786 | 0.8333 | 0.1000 | 0.1000 | 413.2000 | 0.0719 | 1.0000 | ABCD(X) | -0.8214 |
| abrupt/feature_permutation | det4_s0_whddma_chddma | 50 | 0.9273 | 0.8793 | 0.9808 | 0.9800 | 127.7347 | 0.5032 | 1.0000 | ABCD(X) | -0.0727 |
| abrupt/feature_permutation | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 1.0000 | ABCD(X) | -1.0000 |
| abrupt/feature_permutation | det4_s0_wrddm_cadwin | 50 | 0.1786 | 0.8333 | 0.1000 | 0.1000 | 460.2000 | 0.0719 | 1.0000 | ABCD(X) | -0.8214 |
| abrupt/feature_permutation | det4_s0_wrddm_chddma | 50 | 0.3492 | 0.8462 | 0.2200 | 0.2200 | 67.9091 | 0.1438 | 1.0000 | ABCD(X) | -0.6508 |
| abrupt/feature_permutation | det4_s0_wrddm_crddm | 50 | 0.7761 | 0.6500 | 0.9630 | 0.9600 | 178.4167 | 2.0129 | 1.0000 | ABCD(X) | -0.2239 |
| abrupt/feature_permutation | det4_s1_wadwin_cadwin | 50 | 0.9623 | 0.9273 | 1.0000 | 1.0000 | 302.4200 | 0.2876 | 1.0000 | ABCD(X) | -0.0377 |
| abrupt/feature_permutation | det4_s1_wadwin_chddma | 50 | 0.9000 | 0.9184 | 0.8824 | 0.8800 | 487.9545 | 0.2876 | 1.0000 | ABCD(X) | -0.1000 |
| abrupt/feature_permutation | det4_s1_wadwin_crddm | 50 | 0.8911 | 0.9000 | 0.8824 | 0.8800 | 457.2273 | 0.3595 | 1.0000 | ABCD(X) | -0.1089 |
| abrupt/feature_permutation | det4_s1_whddma_cadwin | 50 | 0.5867 | 0.8800 | 0.4400 | 0.4400 | 485.7727 | 0.2157 | 1.0000 | ABCD(X) | -0.4133 |
| abrupt/feature_permutation | det4_s1_whddma_chddma | 50 | 0.9189 | 0.8500 | 1.0000 | 1.0000 | 93.2800 | 0.6470 | 1.0000 | ABCD(X) | -0.0811 |
| abrupt/feature_permutation | det4_s1_whddma_crddm | 50 | 0.5333 | 0.8000 | 0.4000 | 0.4000 | 445.5000 | 0.3595 | 1.0000 | ABCD(X) | -0.4667 |
| abrupt/feature_permutation | det4_s1_wrddm_cadwin | 50 | 0.7073 | 0.9062 | 0.5800 | 0.5800 | 427.2414 | 0.2157 | 1.0000 | ABCD(X) | -0.2927 |
| abrupt/feature_permutation | det4_s1_wrddm_chddma | 50 | 0.7229 | 0.9091 | 0.6000 | 0.6000 | 302.0667 | 0.2157 | 1.0000 | ABCD(X) | -0.2771 |
| abrupt/feature_permutation | det4_s1_wrddm_crddm | 50 | 0.7155 | 0.5608 | 0.9881 | 0.9800 | 192.4286 | 4.6729 | 1.0000 | ABCD(X) | -0.2845 |
| abrupt/label_swap | det4_s0_wadwin_cadwin | 50 | 0.3617 | 0.3864 | 0.3400 | 0.3400 | 842.2941 | 1.9410 | 0.5250 | SEED | -0.1633 |
| abrupt/label_swap | det4_s0_wadwin_chddma | 50 | 0.2121 | 0.4375 | 0.1400 | 0.1400 | 673.8571 | 0.6470 | 0.5250 | SEED | -0.3129 |
| abrupt/label_swap | det4_s0_wadwin_crddm | 50 | 0.2727 | 0.5625 | 0.1800 | 0.1800 | 734.7778 | 0.5032 | 0.5250 | SEED | -0.2523 |
| abrupt/label_swap | det4_s0_whddma_cadwin | 50 | 0.2069 | 0.7500 | 0.1200 | 0.1200 | 877.5000 | 0.1438 | 0.5250 | SEED | -0.3181 |
| abrupt/label_swap | det4_s0_whddma_chddma | 50 | 0.6214 | 0.6154 | 0.6275 | 0.6200 | 598.6452 | 1.4378 | 0.5250 | SEED | 0.0964 |
| abrupt/label_swap | det4_s0_whddma_crddm | 50 | 0.2712 | 0.8889 | 0.1600 | 0.1600 | 703.8750 | 0.0719 | 0.5250 | SEED | -0.2538 |
| abrupt/label_swap | det4_s0_wrddm_cadwin | 50 | 0.1967 | 0.5455 | 0.1200 | 0.1200 | 769.8333 | 0.3595 | 0.5250 | SEED | -0.3283 |
| abrupt/label_swap | det4_s0_wrddm_chddma | 50 | 0.4167 | 0.6818 | 0.3000 | 0.3000 | 552.6000 | 0.5032 | 0.5250 | SEED | -0.1083 |
| abrupt/label_swap | det4_s0_wrddm_crddm | 50 | 0.6325 | 0.5692 | 0.7115 | 0.7000 | 690.4571 | 2.0129 | 0.5250 | SEED | 0.1075 |
| abrupt/label_swap | det4_s1_wadwin_cadwin | 50 | 0.5102 | 0.5208 | 0.5000 | 0.5000 | 878.9600 | 1.6535 | 0.5250 | SEED | -0.0148 |
| abrupt/label_swap | det4_s1_wadwin_chddma | 50 | 0.4091 | 0.4737 | 0.3600 | 0.3600 | 895.6111 | 1.4378 | 0.5250 | SEED | -0.1159 |
| abrupt/label_swap | det4_s1_wadwin_crddm | 50 | 0.4545 | 0.5263 | 0.4000 | 0.4000 | 907.8500 | 1.2940 | 0.5250 | SEED | -0.0705 |
| abrupt/label_swap | det4_s1_whddma_cadwin | 50 | 0.2188 | 0.5000 | 0.1400 | 0.1400 | 941.7143 | 0.5032 | 0.5250 | SEED | -0.3063 |
| abrupt/label_swap | det4_s1_whddma_chddma | 50 | 0.7679 | 0.7288 | 0.8113 | 0.8000 | 613.5750 | 1.1503 | 0.5250 | SEED | 0.2429 |
| abrupt/label_swap | det4_s1_whddma_crddm | 50 | 0.2687 | 0.5294 | 0.1800 | 0.1800 | 575.2222 | 0.5751 | 0.5250 | SEED | -0.2563 |
| abrupt/label_swap | det4_s1_wrddm_cadwin | 50 | 0.2667 | 0.4000 | 0.2000 | 0.2000 | 787.6000 | 1.0784 | 0.5250 | SEED | -0.2583 |
| abrupt/label_swap | det4_s1_wrddm_chddma | 50 | 0.5500 | 0.7333 | 0.4400 | 0.4400 | 638.3182 | 0.5751 | 0.5250 | SEED | 0.0250 |
| abrupt/label_swap | det4_s1_wrddm_crddm | 50 | 0.5730 | 0.4513 | 0.7846 | 0.7200 | 578.2222 | 4.4572 | 0.5250 | SEED | 0.0480 |
| gradual/class_prior | det4_s0_wadwin_cadwin | 50 | 0.0339 | 0.1111 | 0.0200 | 0.0200 | 599.0000 | 0.5751 | 0.5190 | STUDD | -0.4851 |
| gradual/class_prior | det4_s0_wadwin_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1438 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1438 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0719 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_whddma_chddma | 50 | 0.0678 | 0.2222 | 0.0400 | 0.0400 | 1041.5000 | 0.5032 | 0.5190 | STUDD | -0.4512 |
| gradual/class_prior | det4_s0_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1438 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.0000 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s0_wrddm_chddma | 50 | 0.0385 | 0.5000 | 0.0200 | 0.0200 | 1285.0000 | 0.0719 | 0.5190 | STUDD | -0.4805 |
| gradual/class_prior | det4_s0_wrddm_crddm | 50 | 0.1026 | 0.1429 | 0.0800 | 0.0800 | 832.2500 | 1.7254 | 0.5190 | STUDD | -0.4164 |
| gradual/class_prior | det4_s1_wadwin_cadwin | 50 | 0.0351 | 0.1429 | 0.0200 | 0.0200 | 566.0000 | 0.4313 | 0.5190 | STUDD | -0.4839 |
| gradual/class_prior | det4_s1_wadwin_chddma | 50 | 0.0364 | 0.2000 | 0.0200 | 0.0200 | 566.0000 | 0.2876 | 0.5190 | STUDD | -0.4826 |
| gradual/class_prior | det4_s1_wadwin_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2876 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1438 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_whddma_chddma | 50 | 0.0678 | 0.2222 | 0.0400 | 0.0400 | 1106.0000 | 0.5032 | 0.5190 | STUDD | -0.4512 |
| gradual/class_prior | det4_s1_whddma_crddm | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2157 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.1438 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wrddm_chddma | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2157 | 0.5190 | STUDD | -0.5190 |
| gradual/class_prior | det4_s1_wrddm_crddm | 50 | 0.1228 | 0.1094 | 0.1400 | 0.1400 | 609.7143 | 4.0978 | 0.5190 | STUDD | -0.3962 |
| gradual/feature_filtering | det4_s0_wadwin_cadwin | 50 | 0.2020 | 0.2041 | 0.2000 | 0.2000 | 1235.3000 | 2.8037 | 0.4040 | STUDD | -0.2020 |
| gradual/feature_filtering | det4_s0_wadwin_chddma | 50 | 0.1034 | 0.3750 | 0.0600 | 0.0600 | 1232.3333 | 0.3595 | 0.4040 | STUDD | -0.3006 |
| gradual/feature_filtering | det4_s0_wadwin_crddm | 50 | 0.0364 | 0.2000 | 0.0200 | 0.0200 | 1293.0000 | 0.2876 | 0.4040 | STUDD | -0.3676 |
| gradual/feature_filtering | det4_s0_whddma_cadwin | 50 | 0.0385 | 0.5000 | 0.0200 | 0.0200 | 1491.0000 | 0.0719 | 0.4040 | STUDD | -0.3655 |
| gradual/feature_filtering | det4_s0_whddma_chddma | 50 | 0.2857 | 0.3529 | 0.2400 | 0.2400 | 1176.4167 | 1.5816 | 0.4040 | STUDD | -0.1183 |
| gradual/feature_filtering | det4_s0_whddma_crddm | 50 | 0.1379 | 0.5000 | 0.0800 | 0.0800 | 1451.2500 | 0.2876 | 0.4040 | STUDD | -0.2661 |
| gradual/feature_filtering | det4_s0_wrddm_cadwin | 50 | 0.0645 | 0.1667 | 0.0400 | 0.0400 | 958.5000 | 0.7189 | 0.4040 | STUDD | -0.3395 |
| gradual/feature_filtering | det4_s0_wrddm_chddma | 50 | 0.1846 | 0.4000 | 0.1200 | 0.1200 | 1134.6667 | 0.6470 | 0.4040 | STUDD | -0.2194 |
| gradual/feature_filtering | det4_s0_wrddm_crddm | 50 | 0.3802 | 0.3485 | 0.4182 | 0.3600 | 1234.1111 | 3.0913 | 0.4040 | STUDD | -0.0238 |
| gradual/feature_filtering | det4_s1_wadwin_cadwin | 50 | 0.1304 | 0.1429 | 0.1200 | 0.1200 | 1254.8333 | 2.5881 | 0.4040 | STUDD | -0.2736 |
| gradual/feature_filtering | det4_s1_wadwin_chddma | 50 | 0.1282 | 0.1786 | 0.1000 | 0.1000 | 1286.4000 | 1.6535 | 0.4040 | STUDD | -0.2758 |
| gradual/feature_filtering | det4_s1_wadwin_crddm | 50 | 0.1282 | 0.1786 | 0.1000 | 0.1000 | 1332.8000 | 1.6535 | 0.4040 | STUDD | -0.2758 |
| gradual/feature_filtering | det4_s1_whddma_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.6470 | 0.4040 | STUDD | -0.4040 |
| gradual/feature_filtering | det4_s1_whddma_chddma | 50 | 0.2727 | 0.3158 | 0.2400 | 0.2400 | 1279.6667 | 1.8692 | 0.4040 | STUDD | -0.1313 |
| gradual/feature_filtering | det4_s1_whddma_crddm | 50 | 0.0882 | 0.1667 | 0.0600 | 0.0600 | 1342.3333 | 1.0784 | 0.4040 | STUDD | -0.3158 |
| gradual/feature_filtering | det4_s1_wrddm_cadwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 1.2221 | 0.4040 | STUDD | -0.4040 |
| gradual/feature_filtering | det4_s1_wrddm_chddma | 50 | 0.1690 | 0.2857 | 0.1200 | 0.1200 | 1258.8333 | 1.0784 | 0.4040 | STUDD | -0.2350 |
| gradual/feature_filtering | det4_s1_wrddm_crddm | 50 | 0.2500 | 0.1957 | 0.3462 | 0.3200 | 1087.0000 | 5.3199 | 0.4040 | STUDD | -0.1540 |
| gradual/feature_permutation | det4_s0_wadwin_cadwin | 50 | 0.6299 | 0.5405 | 0.7547 | 0.7400 | 940.6216 | 2.4443 | 0.7040 | ABCD | -0.0741 |
| gradual/feature_permutation | det4_s0_wadwin_chddma | 50 | 0.2581 | 0.6667 | 0.1600 | 0.1600 | 704.6250 | 0.2876 | 0.7040 | ABCD | -0.4459 |
| gradual/feature_permutation | det4_s0_wadwin_crddm | 50 | 0.2667 | 0.8000 | 0.1600 | 0.1600 | 649.1250 | 0.1438 | 0.7040 | ABCD | -0.4373 |
| gradual/feature_permutation | det4_s0_whddma_cadwin | 50 | 0.1481 | 1.0000 | 0.0800 | 0.0800 | 579.7500 | 0.0000 | 0.7040 | ABCD | -0.5559 |
| gradual/feature_permutation | det4_s0_whddma_chddma | 50 | 0.9027 | 0.8226 | 1.0000 | 1.0000 | 530.2400 | 0.7908 | 0.7040 | ABCD | 0.1987 |
| gradual/feature_permutation | det4_s0_whddma_crddm | 50 | 0.1404 | 0.5714 | 0.0800 | 0.0800 | 723.5000 | 0.2157 | 0.7040 | ABCD | -0.5636 |
| gradual/feature_permutation | det4_s0_wrddm_cadwin | 50 | 0.3810 | 0.9231 | 0.2400 | 0.2400 | 931.7500 | 0.0719 | 0.7040 | ABCD | -0.3230 |
| gradual/feature_permutation | det4_s0_wrddm_chddma | 50 | 0.5600 | 0.8400 | 0.4200 | 0.4200 | 555.0000 | 0.2876 | 0.7040 | ABCD | -0.1440 |
| gradual/feature_permutation | det4_s0_wrddm_crddm | 50 | 0.6806 | 0.5328 | 0.9420 | 0.9200 | 526.7609 | 4.0978 | 0.7040 | ABCD | -0.0234 |
| gradual/feature_permutation | det4_s1_wadwin_cadwin | 50 | 0.9273 | 0.8644 | 1.0000 | 1.0000 | 895.0200 | 0.5751 | 0.7040 | ABCD | 0.2233 |
| gradual/feature_permutation | det4_s1_wadwin_chddma | 50 | 0.7723 | 0.7647 | 0.7800 | 0.7800 | 965.0000 | 0.8627 | 0.7040 | ABCD | 0.0683 |
| gradual/feature_permutation | det4_s1_wadwin_crddm | 50 | 0.7308 | 0.7037 | 0.7600 | 0.7600 | 939.3158 | 1.1503 | 0.7040 | ABCD | 0.0268 |
| gradual/feature_permutation | det4_s1_whddma_cadwin | 50 | 0.4474 | 0.6538 | 0.3400 | 0.3400 | 943.7647 | 0.6470 | 0.7040 | ABCD | -0.2566 |
| gradual/feature_permutation | det4_s1_whddma_chddma | 50 | 0.9286 | 0.8667 | 1.0000 | 1.0000 | 689.3800 | 0.5751 | 0.7040 | ABCD | 0.2246 |
| gradual/feature_permutation | det4_s1_whddma_crddm | 50 | 0.5897 | 0.8214 | 0.4600 | 0.4600 | 832.0000 | 0.3595 | 0.7040 | ABCD | -0.1143 |
| gradual/feature_permutation | det4_s1_wrddm_cadwin | 50 | 0.8043 | 0.8810 | 0.7400 | 0.7400 | 915.4865 | 0.3595 | 0.7040 | ABCD | 0.1003 |
| gradual/feature_permutation | det4_s1_wrddm_chddma | 50 | 0.7312 | 0.7907 | 0.6800 | 0.6800 | 702.3824 | 0.6470 | 0.7040 | ABCD | 0.0272 |
| gradual/feature_permutation | det4_s1_wrddm_crddm | 50 | 0.6300 | 0.4649 | 0.9773 | 0.9600 | 705.6667 | 7.1172 | 0.7040 | ABCD | -0.0740 |
| gradual/label_swap | det4_s0_wadwin_cadwin | 50 | 0.1111 | 0.1250 | 0.1000 | 0.1000 | 1228.6000 | 2.5162 | 0.3840 | STUDD | -0.2729 |
| gradual/label_swap | det4_s0_wadwin_chddma | 50 | 0.1270 | 0.3077 | 0.0800 | 0.0800 | 1361.7500 | 0.6470 | 0.3840 | STUDD | -0.2570 |
| gradual/label_swap | det4_s0_wadwin_crddm | 50 | 0.1290 | 0.3333 | 0.0800 | 0.0800 | 1152.7500 | 0.5751 | 0.3840 | STUDD | -0.2550 |
| gradual/label_swap | det4_s0_whddma_cadwin | 50 | 0.0702 | 0.2857 | 0.0400 | 0.0400 | 1268.5000 | 0.3595 | 0.3840 | STUDD | -0.3138 |
| gradual/label_swap | det4_s0_whddma_chddma | 50 | 0.2828 | 0.2857 | 0.2800 | 0.2800 | 1193.2857 | 2.5162 | 0.3840 | STUDD | -0.1012 |
| gradual/label_swap | det4_s0_whddma_crddm | 50 | 0.1905 | 0.4615 | 0.1200 | 0.1200 | 1302.5000 | 0.5032 | 0.3840 | STUDD | -0.1935 |
| gradual/label_swap | det4_s0_wrddm_cadwin | 50 | 0.0690 | 0.2500 | 0.0400 | 0.0400 | 1267.5000 | 0.4313 | 0.3840 | STUDD | -0.3150 |
| gradual/label_swap | det4_s0_wrddm_chddma | 50 | 0.2000 | 0.3500 | 0.1400 | 0.1400 | 1313.2857 | 0.9346 | 0.3840 | STUDD | -0.1840 |
| gradual/label_swap | det4_s0_wrddm_crddm | 50 | 0.4698 | 0.3889 | 0.5932 | 0.5200 | 1096.4231 | 3.9540 | 0.3840 | STUDD | 0.0858 |
| gradual/label_swap | det4_s1_wadwin_cadwin | 50 | 0.1667 | 0.1739 | 0.1600 | 0.1600 | 1263.2500 | 2.7318 | 0.3840 | STUDD | -0.2173 |
| gradual/label_swap | det4_s1_wadwin_chddma | 50 | 0.1333 | 0.1500 | 0.1200 | 0.1200 | 1266.0000 | 2.4443 | 0.3840 | STUDD | -0.2507 |
| gradual/label_swap | det4_s1_wadwin_crddm | 50 | 0.1163 | 0.1389 | 0.1000 | 0.1000 | 1286.2000 | 2.2286 | 0.3840 | STUDD | -0.2677 |
| gradual/label_swap | det4_s1_whddma_cadwin | 50 | 0.1408 | 0.2381 | 0.1000 | 0.1000 | 1263.2000 | 1.1503 | 0.3840 | STUDD | -0.2432 |
| gradual/label_swap | det4_s1_whddma_chddma | 50 | 0.2936 | 0.2712 | 0.3200 | 0.3200 | 1289.6250 | 3.0913 | 0.3840 | STUDD | -0.0904 |
| gradual/label_swap | det4_s1_whddma_crddm | 50 | 0.1918 | 0.3043 | 0.1400 | 0.1400 | 1250.8571 | 1.1503 | 0.3840 | STUDD | -0.1922 |
| gradual/label_swap | det4_s1_wrddm_cadwin | 50 | 0.1622 | 0.2500 | 0.1200 | 0.1200 | 1262.6667 | 1.2940 | 0.3840 | STUDD | -0.2218 |
| gradual/label_swap | det4_s1_wrddm_chddma | 50 | 0.2889 | 0.3250 | 0.2600 | 0.2600 | 1273.6923 | 1.9410 | 0.3840 | STUDD | -0.0951 |
| gradual/label_swap | det4_s1_wrddm_crddm | 50 | 0.3314 | 0.2458 | 0.5088 | 0.4400 | 1084.9091 | 6.3983 | 0.3840 | STUDD | -0.0526 |

### Ranking across dataset x cell on pooled F1

Blocks: 64; presets: 18. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| det4_s1_whddma_chddma | 4.62 | 0.3659 |
| det4_s1_wadwin_cadwin | 5.70 | 0.3442 |
| det4_s0_whddma_chddma | 6.16 | 0.3197 |
| det4_s0_wrddm_crddm | 7.45 | 0.2633 |
| det4_s1_wrddm_crddm | 7.84 | 0.2228 |
| det4_s1_wadwin_chddma | 7.98 | 0.2856 |
| det4_s1_wadwin_crddm | 8.25 | 0.2820 |
| det4_s0_wadwin_cadwin | 8.41 | 0.2652 |
| det4_s0_wadwin_chddma | 8.72 | 0.2257 |
| det4_s1_wrddm_chddma | 8.94 | 0.2522 |
| det4_s0_wadwin_crddm | 9.18 | 0.2077 |
| det4_s1_wrddm_cadwin | 11.04 | 0.2082 |
| det4_s0_wrddm_chddma | 11.31 | 0.1722 |
| det4_s1_whddma_cadwin | 11.80 | 0.1726 |
| det4_s1_whddma_crddm | 11.83 | 0.1742 |
| det4_s0_wrddm_cadwin | 13.29 | 0.0976 |
| det4_s0_whddma_crddm | 13.84 | 0.0664 |
| det4_s0_whddma_cadwin | 14.65 | 0.0382 |

Friedman chi2 = 378.578, p = 5.515e-70.

## Cost (time and memory)

Mean per run. `runtime_s` is wall time, `cpu_time_s` process CPU time (both exclude data loading); `rss_increment_mb` is the peak resident memory of the run's own process minus its level before the system was built, `ram_hours_gb` that increment integrated over the run (GB x hours), `model_size_final_mb` the system's Python object size after the last instance. `concurrent_runs` is the most runs that executed at the same time as a run. Memory is per process and valid at any concurrency; times are strict only where `concurrent_runs` is 1 (`--workers 1`) and comparable only between rows with the same machine and the same `concurrent_runs` (CPU time is less affected by parallel load than wall time).

Some runs shared the machine with other runs (`concurrent_runs` > 1): their times are indicative only.

| dataset | preset | n | runtime_s | runtime_std | cpu_time_s | instances_per_s | rss_increment_mb | rss_increment_max_mb | model_size_final_mb | ram_hours_gb | concurrent_runs | machine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ai4i2020 | det4_s0_wadwin_cadwin | 1 | 0.8100 | - | 0.8080 | 12339.4000 | 13.9000 | 13.9000 | 4.7500 | 2.00e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_wadwin_chddma | 1 | 0.7100 | - | 0.7320 | 14002.1000 | 13.9000 | 13.9000 | 5.6100 | 1.26e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_wadwin_crddm | 1 | 1.2300 | - | 1.1640 | 8154.6000 | 5.5000 | 5.5000 | 4.3200 | 1.30e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_whddma_cadwin | 1 | 0.8000 | - | 0.8050 | 12526.5000 | 4.0000 | 4.0000 | 3.1300 | 7.15e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_whddma_chddma | 1 | 0.9800 | - | 0.9900 | 10183.9000 | 13.8000 | 13.8000 | 5.1400 | 2.52e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_whddma_crddm | 1 | 0.8100 | - | 0.8170 | 12274.4000 | 4.1000 | 4.1000 | 3.1300 | 7.36e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_wrddm_cadwin | 1 | 0.7000 | - | 0.6990 | 14312.3000 | 4.3000 | 4.3000 | 3.1400 | 6.56e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_wrddm_chddma | 1 | 0.7900 | - | 0.7930 | 12677.8000 | 4.1000 | 4.1000 | 3.1400 | 7.09e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s0_wrddm_crddm | 1 | 0.8900 | - | 0.8890 | 11264.1000 | 13.5000 | 13.5000 | 4.9200 | 2.67e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_wadwin_cadwin | 1 | 1.0100 | - | 1.0220 | 9902.6000 | 14.8000 | 14.8000 | 5.0100 | 2.68e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_wadwin_chddma | 1 | 1.1400 | - | 1.1510 | 8812.6000 | 14.3000 | 14.3000 | 5.7800 | 2.97e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_wadwin_crddm | 1 | 1.0600 | - | 1.0860 | 9455.0000 | 14.6000 | 14.6000 | 5.7900 | 2.63e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_whddma_cadwin | 1 | 0.9300 | - | 0.9370 | 10754.5000 | 4.1000 | 4.1000 | 3.1800 | 8.52e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_whddma_chddma | 1 | 1.1600 | - | 1.1760 | 8604.8000 | 14.6000 | 14.6000 | 5.7800 | 3.27e-06 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_whddma_crddm | 1 | 0.9400 | - | 0.9430 | 10652.7000 | 4.1000 | 4.1000 | 3.1900 | 8.50e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_wrddm_cadwin | 1 | 0.8500 | - | 0.8570 | 11689.5000 | 4.2000 | 4.2000 | 3.2000 | 8.03e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_wrddm_chddma | 1 | 0.9400 | - | 0.9510 | 10631.0000 | 4.3000 | 4.3000 | 3.2000 | 9.04e-07 | 1 | Apple M4 / 24.0 GB |
| ai4i2020 | det4_s1_wrddm_crddm | 1 | 1.2000 | - | 1.2060 | 8355.9000 | 14.5000 | 14.5000 | 5.2800 | 3.84e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_wadwin_cadwin | 1 | 10.1400 | - | 10.2030 | 9863.6000 | 10.7000 | 10.7000 | 6.1000 | 1.14e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_wadwin_chddma | 1 | 11.5500 | - | 11.6580 | 8654.2000 | 13.6000 | 13.6000 | 7.1300 | 9.77e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_wadwin_crddm | 1 | 11.7700 | - | 12.0440 | 8493.6000 | 4.3000 | 4.3000 | 8.4900 | 1.14e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_whddma_cadwin | 1 | 12.4500 | - | 12.4820 | 8035.5000 | 12.7000 | 12.7000 | 5.5700 | 3.27e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_whddma_chddma | 1 | 11.6500 | - | 11.7080 | 8585.4000 | 12.1000 | 12.1000 | 7.0000 | 1.74e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_whddma_crddm | 1 | 13.5800 | - | 13.2540 | 7363.1000 | 11.9000 | 11.9000 | 5.8200 | 2.00e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_wrddm_cadwin | 1 | 11.4900 | - | 11.3870 | 8705.8000 | 12.0000 | 12.0000 | 5.7800 | 4.92e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_wrddm_chddma | 1 | 11.3200 | - | 11.4050 | 8831.2000 | 23.6000 | 23.6000 | 6.2800 | 6.34e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s0_wrddm_crddm | 1 | 12.6300 | - | 12.2390 | 7917.1000 | 11.7000 | 11.7000 | 7.2900 | 3.10e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_wadwin_cadwin | 1 | 12.3600 | - | 12.4260 | 8089.1000 | 13.0000 | 13.0000 | 6.3200 | 4.43e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_wadwin_chddma | 1 | 14.0200 | - | 14.1430 | 7131.9000 | 12.3000 | 12.3000 | 9.0400 | 2.45e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_wadwin_crddm | 1 | 13.1300 | - | 13.3840 | 7613.2000 | 15.0000 | 15.0000 | 7.5200 | 4.64e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_whddma_cadwin | 1 | 14.5900 | - | 14.3890 | 6855.9000 | 13.8000 | 13.8000 | 6.1800 | 7.19e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_whddma_chddma | 1 | 14.0100 | - | 14.2300 | 7139.6000 | 15.2000 | 15.2000 | 7.4300 | 2.01e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_whddma_crddm | 1 | 14.2200 | - | 14.4390 | 7034.0000 | 13.1000 | 13.1000 | 6.0400 | 2.73e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_wrddm_cadwin | 1 | 14.4000 | - | 14.5900 | 6945.4000 | 15.1000 | 15.1000 | 8.0300 | 4.60e-05 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_wrddm_chddma | 1 | 15.1500 | - | 15.2140 | 6598.3000 | 12.7000 | 12.7000 | 9.0700 | 6.34e-06 | 1 | Apple M4 / 24.0 GB |
| airlines | det4_s1_wrddm_crddm | 1 | 15.8000 | - | 16.0020 | 6328.3000 | 21.5000 | 21.5000 | 9.8800 | 4.69e-05 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_wadwin_cadwin | 1 | 134.1700 | - | 132.0080 | 4020.1000 | 4.6000 | 4.6000 | 20.3500 | 8.88e-07 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_wadwin_chddma | 1 | 141.7700 | - | 140.2420 | 3804.7000 | 19.2000 | 19.2000 | 18.8100 | 6.96e-05 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_wadwin_crddm | 1 | 146.5400 | - | 145.2660 | 3680.7000 | 8.6000 | 8.6000 | 13.8700 | 4.01e-06 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_whddma_cadwin | 1 | 140.2600 | - | 138.1040 | 3845.6000 | 18.3000 | 18.3000 | 19.2700 | 8.38e-05 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_whddma_chddma | 1 | 139.2800 | - | 135.8650 | 3872.5000 | 9.7000 | 9.7000 | 14.7400 | 1.02e-06 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_whddma_crddm | 1 | 146.2300 | - | 142.2980 | 3688.6000 | 7.8000 | 7.8000 | 20.4600 | 8.03e-07 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_wrddm_cadwin | 1 | 138.9200 | - | 134.8620 | 3882.6000 | 9.6000 | 9.6000 | 26.4900 | 5.70e-06 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_wrddm_chddma | 1 | 138.1000 | - | 132.4710 | 3905.6000 | 0.0000 | 0.0000 | 16.7100 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s0_wrddm_crddm | 1 | 156.1700 | - | 149.4210 | 3453.9000 | 7.3000 | 7.3000 | 16.6100 | 1.44e-06 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_wadwin_cadwin | 1 | 191.4200 | - | 182.6330 | 2817.8000 | 15.4000 | 15.4000 | 12.5400 | 4.46e-05 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_wadwin_chddma | 1 | 179.6700 | - | 172.4870 | 3002.1000 | 0.0000 | 0.0000 | 16.0300 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_wadwin_crddm | 1 | 159.0300 | - | 154.6140 | 3391.6000 | 8.5000 | 8.5000 | 19.8000 | 6.63e-07 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_whddma_cadwin | 1 | 137.5600 | - | 135.3200 | 3921.1000 | 12.3000 | 12.3000 | 16.2900 | 7.84e-06 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_whddma_chddma | 1 | 137.2300 | - | 135.0150 | 3930.6000 | 14.7000 | 14.7000 | 12.8500 | 9.69e-06 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_whddma_crddm | 1 | 133.7000 | - | 131.7770 | 4034.3000 | 15.1000 | 15.1000 | 16.0400 | 1.29e-05 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_wrddm_cadwin | 1 | 133.5600 | - | 130.7460 | 4038.4000 | 9.9000 | 9.9000 | 18.3100 | 1.15e-06 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_wrddm_chddma | 1 | 165.2100 | - | 160.0470 | 3264.8000 | 13.4000 | 13.4000 | 11.4300 | 1.14e-05 | 1 | Apple M4 / 24.0 GB |
| airlines_full | det4_s1_wrddm_crddm | 1 | 168.3200 | - | 162.7560 | 3204.5000 | 7.6000 | 7.6000 | 16.6900 | 4.40e-07 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_wadwin_cadwin | 1 | 84.0100 | - | 83.3730 | 1190.4000 | 0.0000 | 0.0000 | 34.1900 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_wadwin_chddma | 1 | 76.8700 | - | 76.3710 | 1300.9000 | 19.7000 | 19.7000 | 45.8100 | 8.46e-06 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_wadwin_crddm | 1 | 90.7100 | - | 90.1680 | 1102.4000 | 15.4000 | 15.4000 | 45.9300 | 4.73e-06 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_whddma_cadwin | 1 | 44.0800 | - | 43.7860 | 2268.5000 | 14.1000 | 14.1000 | 52.1600 | 6.88e-06 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_whddma_chddma | 1 | 114.7700 | - | 113.3790 | 871.3000 | 55.1000 | 55.1000 | 42.5400 | 8.91e-05 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_whddma_crddm | 1 | 51.2900 | - | 50.1480 | 1949.7000 | 47.6000 | 47.6000 | 37.1400 | 4.83e-05 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_wrddm_cadwin | 1 | 51.4700 | - | 50.9860 | 1943.1000 | 0.0000 | 0.0000 | 57.0400 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_wrddm_chddma | 1 | 51.2400 | - | 50.9790 | 1951.7000 | 0.0000 | 0.0000 | 28.7100 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s0_wrddm_crddm | 1 | 88.0100 | - | 87.6400 | 1136.3000 | 21.4000 | 21.4000 | 49.0100 | 5.00e-06 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_wadwin_cadwin | 1 | 121.8000 | - | 120.9410 | 821.0000 | 40.1000 | 40.1000 | 47.2900 | 5.87e-05 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_wadwin_chddma | 1 | 121.4400 | - | 120.5680 | 823.5000 | 26.2000 | 26.2000 | 50.9400 | 1.98e-05 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_wadwin_crddm | 1 | 134.5300 | - | 134.0820 | 743.3000 | 0.0000 | 0.0000 | 63.2700 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_whddma_cadwin | 1 | 88.5600 | - | 88.0280 | 1129.2000 | 21.3000 | 21.3000 | 46.2600 | 1.09e-05 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_whddma_chddma | 1 | 159.5000 | - | 158.5240 | 626.9000 | 63.1000 | 63.1000 | 51.8000 | 0.0001 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_whddma_crddm | 1 | 89.9600 | - | 89.4190 | 1111.7000 | 27.7000 | 27.7000 | 42.3000 | 2.48e-06 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_wrddm_cadwin | 1 | 84.8900 | - | 84.4880 | 1178.0000 | 0.0000 | 0.0000 | 32.4100 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_wrddm_chddma | 1 | 88.2000 | - | 87.9680 | 1133.8000 | 6.7000 | 6.7000 | 39.1600 | 4.09e-07 | 1 | Apple M4 / 24.0 GB |
| covertype | det4_s1_wrddm_crddm | 1 | 111.6300 | - | 111.2770 | 895.8000 | 84.2000 | 84.2000 | 54.8500 | 0.0013 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_wadwin_cadwin | 1 | 1067.0600 | - | 1030.0830 | 544.5000 | 14.2000 | 14.2000 | 123.5100 | 1.86e-06 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_wadwin_chddma | 1 | 1337.2600 | - | 1266.9590 | 434.5000 | 16.7000 | 16.7000 | 95.4700 | 1.31e-06 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_wadwin_crddm | 1 | 1461.3200 | - | 1384.6670 | 397.6000 | 0.0000 | 0.0000 | 95.4300 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_whddma_cadwin | 1 | 716.4100 | - | 676.0140 | 811.0000 | 5.4000 | 5.4000 | 43.7900 | 1.24e-06 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_whddma_chddma | 1 | 1280.8900 | - | 1241.7120 | 453.6000 | 0.0000 | 0.0000 | 461.3900 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_whddma_crddm | 1 | 508.3500 | - | 502.7710 | 1142.9000 | 0.0000 | 0.0000 | 64.0400 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_wrddm_cadwin | 1 | 397.1800 | - | 395.6580 | 1462.8000 | 14.1000 | 14.1000 | 89.3000 | 3.10e-06 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_wrddm_chddma | 1 | 534.8200 | - | 529.1590 | 1086.4000 | 0.0000 | 0.0000 | 67.9000 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s0_wrddm_crddm | 1 | 737.9800 | - | 732.7790 | 787.3000 | 10.0000 | 10.0000 | 254.9500 | 1.01e-06 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_wadwin_cadwin | 1 | 1098.7900 | - | 1090.0950 | 528.8000 | 0.0000 | 0.0000 | 322.3400 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_wadwin_chddma | 1 | 1141.4700 | - | 1132.3140 | 509.0000 | 0.0000 | 0.0000 | 170.5300 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_wadwin_crddm | 1 | 1514.7500 | - | 1483.8720 | 383.6000 | 7.2000 | 7.2000 | 178.9200 | 4.36e-07 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_whddma_cadwin | 1 | 1117.8000 | - | 1080.0630 | 519.8000 | 16.2000 | 16.2000 | 113.1000 | 5.40e-06 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_whddma_chddma | 1 | 2037.1600 | - | 1963.4950 | 285.2000 | 0.0000 | 0.0000 | 985.5600 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_whddma_crddm | 1 | 1037.6200 | - | 1011.7100 | 559.9000 | 7.1000 | 7.1000 | 104.4200 | 7.17e-07 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_wrddm_cadwin | 1 | 1023.7200 | - | 992.5080 | 567.5000 | 0.0000 | 0.0000 | 113.3600 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_wrddm_chddma | 1 | 1040.8500 | - | 1005.5400 | 558.2000 | 0.0000 | 0.0000 | 120.4100 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| covertype_full | det4_s1_wrddm_crddm | 1 | 1301.2900 | - | 1250.4210 | 446.5000 | 0.0000 | 0.0000 | 220.4100 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_wadwin_cadwin | 1 | 7.4100 | - | 7.4270 | 6111.5000 | 14.8000 | 14.8000 | 13.7500 | 1.10e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_wadwin_chddma | 1 | 7.8400 | - | 7.8570 | 5780.9000 | 22.3000 | 22.3000 | 11.6100 | 3.50e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_wadwin_crddm | 1 | 7.3500 | - | 7.2530 | 6166.9000 | 8.1000 | 8.1000 | 9.4200 | 8.64e-07 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_whddma_cadwin | 1 | 5.7000 | - | 5.7370 | 7955.2000 | 7.8000 | 7.8000 | 10.6400 | 7.07e-07 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_whddma_chddma | 1 | 8.6500 | - | 8.6750 | 5237.7000 | 16.2000 | 16.2000 | 6.8500 | 3.30e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_whddma_crddm | 1 | 6.4300 | - | 6.4700 | 7050.8000 | 18.2000 | 18.2000 | 7.9600 | 2.54e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_wrddm_cadwin | 1 | 6.2300 | - | 5.8630 | 7268.2000 | 11.5000 | 11.5000 | 8.8900 | 2.62e-06 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_wrddm_chddma | 1 | 6.5000 | - | 6.4620 | 6973.2000 | 18.2000 | 18.2000 | 9.0500 | 1.51e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s0_wrddm_crddm | 1 | 7.7800 | - | 7.7290 | 5824.6000 | 15.4000 | 15.4000 | 9.2800 | 6.03e-06 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_wadwin_cadwin | 1 | 9.8000 | - | 9.7830 | 4624.3000 | 12.6000 | 12.6000 | 10.7000 | 2.59e-06 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_wadwin_chddma | 1 | 10.1400 | - | 10.1290 | 4469.3000 | 0.0000 | 0.0000 | 12.5500 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_wadwin_crddm | 1 | 10.2100 | - | 10.2470 | 4438.9000 | 23.2000 | 23.2000 | 12.4600 | 3.07e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_whddma_cadwin | 1 | 8.9600 | - | 8.6340 | 5056.6000 | 9.6000 | 9.6000 | 8.2800 | 5.63e-07 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_whddma_chddma | 1 | 15.6600 | - | 15.6580 | 2893.0000 | 17.5000 | 17.5000 | 15.1700 | 5.20e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_whddma_crddm | 1 | 8.5900 | - | 8.6550 | 5274.6000 | 17.4000 | 17.4000 | 7.9800 | 3.48e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_wrddm_cadwin | 1 | 7.2800 | - | 7.3420 | 6224.3000 | 15.4000 | 15.4000 | 8.3500 | 2.36e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_wrddm_chddma | 1 | 8.4800 | - | 8.5470 | 5340.2000 | 18.3000 | 18.3000 | 8.7100 | 3.29e-05 | 1 | Apple M4 / 24.0 GB |
| electricity | det4_s1_wrddm_crddm | 1 | 11.1400 | - | 10.9370 | 4065.9000 | 16.5000 | 16.5000 | 10.3900 | 1.24e-05 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_wadwin_cadwin | 1 | 27.3700 | - | 27.0160 | 508.2000 | 51.3000 | 51.3000 | 109.9000 | 6.36e-05 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_wadwin_chddma | 1 | 33.0000 | - | 33.0470 | 421.5000 | 84.3000 | 84.3000 | 140.3700 | 0.0004 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_wadwin_crddm | 1 | 31.6900 | - | 31.6160 | 438.9000 | 158.6000 | 158.6000 | 145.7500 | 0.0009 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_whddma_cadwin | 1 | 21.2600 | - | 21.1350 | 654.4000 | 57.9000 | 57.9000 | 47.0100 | 0.0002 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_whddma_chddma | 1 | 27.6300 | - | 27.5850 | 503.4000 | 226.6000 | 226.6000 | 137.3700 | 0.0012 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_whddma_crddm | 1 | 26.0000 | - | 25.9940 | 535.1000 | 37.9000 | 37.9000 | 54.5400 | 6.41e-05 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_wrddm_cadwin | 1 | 14.1800 | - | 13.9350 | 981.1000 | 24.1000 | 24.1000 | 26.3100 | 5.13e-06 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_wrddm_chddma | 1 | 23.6900 | - | 23.7120 | 587.2000 | 65.2000 | 65.2000 | 97.0500 | 0.0003 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s0_wrddm_crddm | 1 | 26.4500 | - | 26.3630 | 525.8000 | 132.9000 | 132.9000 | 131.5000 | 0.0005 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_wadwin_cadwin | 1 | 36.9300 | - | 36.8700 | 376.7000 | 113.3000 | 113.3000 | 97.7500 | 0.0006 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_wadwin_chddma | 1 | 40.7500 | - | 40.0930 | 341.4000 | 100.3000 | 100.3000 | 98.8600 | 0.0003 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_wadwin_crddm | 1 | 44.2100 | - | 43.6710 | 314.6000 | 59.0000 | 59.0000 | 111.0200 | 0.0002 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_whddma_cadwin | 1 | 28.1900 | - | 28.2630 | 493.4000 | 107.4000 | 107.4000 | 103.6300 | 0.0003 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_whddma_chddma | 1 | 39.6200 | - | 39.3310 | 351.1000 | 99.6000 | 99.6000 | 129.7100 | 0.0002 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_whddma_crddm | 1 | 27.7000 | - | 27.6380 | 502.1000 | 143.8000 | 143.8000 | 101.3100 | 0.0007 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_wrddm_cadwin | 1 | 33.1600 | - | 33.0990 | 419.5000 | 59.8000 | 59.8000 | 97.0000 | 0.0001 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_wrddm_chddma | 1 | 33.4200 | - | 33.2300 | 416.2000 | 117.7000 | 117.7000 | 138.4800 | 0.0007 | 1 | Apple M4 / 24.0 GB |
| gas_sensor_drift | det4_s1_wrddm_crddm | 1 | 37.9700 | - | 37.9950 | 366.4000 | 152.1000 | 152.1000 | 113.1400 | 0.0009 | 1 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_wadwin_cadwin | 80 | 1.6606 | 0.2229 | 1.6125 | 5661.2400 | 6.6375 | 15.5000 | 3.7621 | 1.39e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_wadwin_chddma | 80 | 1.7740 | 0.2513 | 1.7084 | 5310.0962 | 4.2700 | 14.1000 | 3.4212 | 1.22e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_wadwin_crddm | 80 | 1.6110 | 0.2417 | 1.5701 | 5835.2962 | 3.6162 | 13.6000 | 3.3156 | 9.91e-07 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_whddma_cadwin | 80 | 1.8320 | 0.3228 | 1.7649 | 5168.7175 | 3.7750 | 14.5000 | 3.1454 | 1.22e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_whddma_chddma | 80 | 1.8493 | 0.2752 | 1.8100 | 5086.7337 | 4.1888 | 13.9000 | 3.3576 | 1.32e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_whddma_crddm | 80 | 1.7928 | 0.2777 | 1.7570 | 5251.4338 | 3.7938 | 16.3000 | 3.1480 | 1.32e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_wrddm_cadwin | 80 | 1.6414 | 0.2357 | 1.5783 | 5741.6438 | 3.5112 | 5.3000 | 3.1339 | 1.16e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_wrddm_chddma | 80 | 1.7635 | 0.3013 | 1.7079 | 5358.5625 | 4.4250 | 14.9000 | 3.2959 | 1.33e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s0_wrddm_crddm | 80 | 1.9269 | 0.3414 | 1.8732 | 4938.3912 | 11.1687 | 15.2000 | 4.2532 | 3.81e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_wadwin_cadwin | 80 | 1.9258 | 0.3307 | 1.8758 | 4909.7238 | 7.3787 | 17.8000 | 4.1008 | 1.79e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_wadwin_chddma | 80 | 2.1822 | 0.3837 | 2.0681 | 4343.1887 | 5.4588 | 17.0000 | 3.5968 | 1.86e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_wadwin_crddm | 80 | 1.9207 | 0.3313 | 1.8841 | 4920.2850 | 6.1213 | 16.2000 | 3.6016 | 1.72e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_whddma_cadwin | 80 | 2.0744 | 0.3111 | 2.0333 | 4534.8000 | 5.2400 | 14.4000 | 3.4454 | 1.96e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_whddma_chddma | 80 | 2.1716 | 0.3002 | 2.1292 | 4315.5875 | 4.9500 | 17.4000 | 3.6068 | 1.88e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_whddma_crddm | 80 | 2.1224 | 0.3032 | 2.0599 | 4416.5175 | 4.1587 | 15.3000 | 3.4169 | 1.63e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_wrddm_cadwin | 80 | 1.9081 | 0.3218 | 1.8611 | 4949.5525 | 4.8000 | 16.3000 | 3.4504 | 1.61e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_wrddm_chddma | 80 | 2.0673 | 0.2945 | 2.0192 | 4544.0338 | 4.9350 | 15.2000 | 3.4688 | 1.82e-06 | 6 | Apple M4 / 24.0 GB |
| injected_ai4i2020 | det4_s1_wrddm_crddm | 80 | 2.3194 | 0.3651 | 2.2794 | 4078.7312 | 12.2450 | 16.0000 | 4.6858 | 5.92e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_wadwin_cadwin | 80 | 24.1982 | 3.1344 | 23.5871 | 3852.7287 | 8.5888 | 19.7000 | 8.9490 | 8.95e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_wadwin_chddma | 80 | 20.6111 | 3.8773 | 20.2096 | 4621.1650 | 8.9613 | 21.8000 | 13.2340 | 1.09e-05 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_wadwin_crddm | 80 | 20.8293 | 4.0847 | 20.4243 | 4581.9988 | 9.0537 | 37.6000 | 11.9404 | 1.33e-05 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_whddma_cadwin | 80 | 20.3122 | 3.0267 | 19.7775 | 4597.3288 | 4.8625 | 15.6000 | 4.9615 | 3.60e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_whddma_chddma | 80 | 24.5557 | 4.7349 | 23.7409 | 3848.3738 | 7.7088 | 22.0000 | 7.7476 | 9.38e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_whddma_crddm | 80 | 21.1952 | 3.0036 | 20.4050 | 4405.1725 | 5.4612 | 17.1000 | 5.4304 | 5.30e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_wrddm_cadwin | 80 | 19.8525 | 2.6045 | 19.2169 | 4690.4988 | 4.8462 | 17.3000 | 5.2964 | 3.03e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_wrddm_chddma | 80 | 20.9074 | 3.2352 | 20.3157 | 4471.5813 | 5.5450 | 17.6000 | 5.7248 | 6.92e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s0_wrddm_crddm | 80 | 25.2091 | 3.6716 | 24.6422 | 3716.4737 | 11.7300 | 21.1000 | 8.2242 | 1.45e-05 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_wadwin_cadwin | 80 | 25.3255 | 3.9986 | 24.7082 | 3704.5387 | 7.1450 | 28.7000 | 8.2519 | 5.61e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_wadwin_chddma | 80 | 24.9719 | 4.0670 | 24.3805 | 3753.2725 | 7.2338 | 19.7000 | 6.8030 | 1.18e-05 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_wadwin_crddm | 80 | 24.5435 | 3.9570 | 23.8409 | 3822.0050 | 6.3662 | 30.6000 | 6.8989 | 7.02e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_whddma_cadwin | 80 | 23.9123 | 3.4950 | 23.3388 | 3902.8137 | 5.5950 | 18.6000 | 5.6452 | 4.91e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_whddma_chddma | 80 | 27.1017 | 4.5725 | 26.3902 | 3464.5900 | 6.3900 | 18.0000 | 8.4401 | 6.92e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_whddma_crddm | 80 | 24.4877 | 3.5620 | 23.8723 | 3814.2838 | 5.8400 | 19.4000 | 5.8230 | 4.67e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_wrddm_cadwin | 80 | 23.3362 | 3.4350 | 22.8214 | 4007.6512 | 6.4050 | 20.3000 | 6.0090 | 7.27e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_wrddm_chddma | 80 | 24.4770 | 3.7879 | 23.8884 | 3820.2488 | 6.2313 | 22.4000 | 6.2127 | 7.25e-06 | 6 | Apple M4 / 24.0 GB |
| injected_airlines | det4_s1_wrddm_crddm | 80 | 30.8642 | 4.2598 | 29.7711 | 3028.1025 | 11.7188 | 18.2000 | 10.3521 | 1.11e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_wadwin_cadwin | 80 | 90.9105 | 35.5114 | 88.0896 | 1547.1000 | 12.4425 | 47.3000 | 56.8102 | 1.78e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_wadwin_chddma | 80 | 67.9006 | 33.2747 | 66.0685 | 1887.1638 | 17.2150 | 94.3000 | 57.6133 | 2.87e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_wadwin_crddm | 80 | 89.7947 | 31.8709 | 86.7510 | 1238.0400 | 11.6612 | 57.3000 | 49.6465 | 1.42e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_whddma_cadwin | 80 | 56.7280 | 6.6261 | 55.0748 | 1744.5887 | 10.2050 | 28.0000 | 21.9950 | 1.34e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_whddma_chddma | 80 | 83.5181 | 20.6217 | 80.9336 | 1253.5000 | 14.3362 | 66.1000 | 41.5969 | 4.69e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_whddma_crddm | 80 | 55.9916 | 10.0174 | 54.2414 | 1788.4588 | 11.3838 | 47.2000 | 22.5934 | 2.46e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_wrddm_cadwin | 80 | 54.1696 | 6.6696 | 52.0528 | 1834.3250 | 11.9275 | 37.2000 | 23.8319 | 1.47e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_wrddm_chddma | 80 | 57.9773 | 11.1628 | 55.7332 | 1743.3462 | 8.5137 | 29.4000 | 25.2477 | 6.47e-06 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s0_wrddm_crddm | 80 | 97.7401 | 20.1979 | 93.6781 | 1058.2713 | 16.3900 | 40.8000 | 46.9986 | 2.24e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_wadwin_cadwin | 80 | 75.3625 | 19.9645 | 72.3675 | 1383.9125 | 12.0275 | 39.4000 | 37.3563 | 1.76e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_wadwin_chddma | 80 | 108.8610 | 63.4526 | 79.4489 | 1153.7062 | 10.1188 | 24.1000 | 33.3589 | 1.11e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_wadwin_crddm | 80 | 96.0851 | 35.4195 | 86.3368 | 1148.9763 | 12.6588 | 53.6000 | 33.7646 | 1.88e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_whddma_cadwin | 80 | 81.8239 | 20.1518 | 77.0926 | 1250.4725 | 10.8763 | 48.2000 | 26.8736 | 1.65e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_whddma_chddma | 80 | 116.2973 | 33.6217 | 109.1324 | 920.5325 | 11.2637 | 31.3000 | 44.4334 | 1.43e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_whddma_crddm | 80 | 93.2105 | 27.0934 | 85.3028 | 1117.2300 | 8.9275 | 34.2000 | 30.1439 | 8.18e-06 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_wrddm_cadwin | 80 | 93.5740 | 25.5605 | 83.0366 | 1104.2112 | 11.8912 | 61.9000 | 28.8666 | 1.92e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_wrddm_chddma | 80 | 112.3794 | 36.5581 | 97.5347 | 942.7450 | 11.3700 | 44.7000 | 32.7828 | 1.79e-05 | 6 | Apple M4 / 24.0 GB |
| injected_covertype | det4_s1_wrddm_crddm | 80 | 196.1106 | 43.2143 | 181.8745 | 526.2500 | 20.6050 | 51.0000 | 62.4374 | 5.51e-05 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_wadwin_cadwin | 80 | 10.8196 | 1.7448 | 10.5429 | 3985.5200 | 9.4037 | 28.4000 | 7.3634 | 9.94e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_wadwin_chddma | 80 | 9.2471 | 2.0541 | 9.0200 | 4743.3588 | 6.7250 | 25.0000 | 8.5038 | 5.31e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_wadwin_crddm | 80 | 8.9721 | 1.7473 | 8.6471 | 4840.8762 | 7.2850 | 20.5000 | 7.8201 | 6.65e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_whddma_cadwin | 80 | 9.2803 | 1.1170 | 9.0638 | 4589.0925 | 4.4213 | 16.3000 | 4.3688 | 4.50e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_whddma_chddma | 80 | 10.8387 | 2.0398 | 10.4290 | 3989.2188 | 7.4488 | 19.5000 | 5.9783 | 7.28e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_whddma_crddm | 80 | 9.3141 | 1.2799 | 9.1157 | 4582.8562 | 4.9637 | 16.9000 | 4.4642 | 4.40e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_wrddm_cadwin | 80 | 8.9744 | 1.2847 | 8.6605 | 4754.9150 | 4.1375 | 18.1000 | 4.4064 | 3.20e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_wrddm_chddma | 80 | 9.6564 | 1.5970 | 9.4123 | 4443.5100 | 5.7887 | 16.2000 | 5.0919 | 5.72e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s0_wrddm_crddm | 80 | 11.9601 | 1.5622 | 11.5645 | 3569.2500 | 10.7150 | 18.6000 | 7.8680 | 1.02e-05 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_wadwin_cadwin | 80 | 12.4104 | 1.7034 | 12.1133 | 3441.3887 | 7.7363 | 22.7000 | 7.1581 | 8.09e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_wadwin_chddma | 80 | 12.4940 | 1.7728 | 12.2096 | 3413.2575 | 6.5900 | 20.9000 | 5.9854 | 6.80e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_wadwin_crddm | 80 | 11.9010 | 1.8090 | 11.6909 | 3590.4925 | 7.0075 | 20.1000 | 5.9450 | 7.64e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_whddma_cadwin | 80 | 11.7186 | 1.4513 | 11.4710 | 3627.5412 | 4.3925 | 20.2000 | 4.9151 | 4.62e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_whddma_chddma | 80 | 12.6249 | 2.0069 | 12.3555 | 3391.9738 | 6.2000 | 19.9000 | 6.7229 | 5.39e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_whddma_crddm | 80 | 12.2190 | 1.8702 | 11.7790 | 3503.1600 | 5.9512 | 22.9000 | 5.0413 | 7.27e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_wrddm_cadwin | 80 | 11.6567 | 1.7236 | 11.4600 | 3663.6238 | 6.4150 | 21.2000 | 5.4387 | 7.61e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_wrddm_chddma | 80 | 12.5597 | 2.0147 | 11.9857 | 3417.8300 | 5.2388 | 18.3000 | 5.5905 | 5.50e-06 | 6 | Apple M4 / 24.0 GB |
| injected_electricity | det4_s1_wrddm_crddm | 80 | 14.1953 | 2.3593 | 13.7761 | 3033.9238 | 12.0525 | 22.4000 | 8.8844 | 1.60e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_wadwin_cadwin | 80 | 67.1796 | 28.3137 | 56.3688 | 226.3300 | 20.8863 | 73.0000 | 46.8158 | 4.66e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_wadwin_chddma | 80 | 49.9866 | 15.4526 | 45.6161 | 282.5850 | 18.2975 | 51.6000 | 33.6852 | 3.46e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_wadwin_crddm | 80 | 31.0511 | 7.9597 | 30.1631 | 448.6062 | 22.7037 | 72.6000 | 34.2626 | 5.28e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_whddma_cadwin | 80 | 41.0771 | 8.6498 | 38.1249 | 332.1975 | 19.7263 | 73.8000 | 29.5100 | 4.64e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_whddma_chddma | 80 | 65.3063 | 18.1334 | 56.6034 | 214.9262 | 19.6550 | 54.6000 | 45.7011 | 5.00e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_whddma_crddm | 80 | 53.7936 | 18.1532 | 48.0447 | 259.6612 | 16.4475 | 65.4000 | 31.5810 | 4.53e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_wrddm_cadwin | 80 | 46.3475 | 10.9987 | 43.0695 | 293.8175 | 19.2375 | 58.8000 | 32.7304 | 5.09e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_wrddm_chddma | 80 | 48.1291 | 9.9513 | 44.5868 | 281.4337 | 18.3062 | 70.9000 | 34.1494 | 5.14e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s0_wrddm_crddm | 80 | 83.4659 | 21.2375 | 79.0899 | 169.4100 | 30.6512 | 98.6000 | 60.9264 | 0.0001 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_wadwin_cadwin | 80 | 77.9197 | 16.3742 | 75.1263 | 175.3475 | 22.5900 | 84.7000 | 53.2250 | 7.08e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_wadwin_chddma | 80 | 70.5396 | 15.0475 | 68.8085 | 193.1538 | 23.5112 | 89.5000 | 48.6490 | 9.16e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_wadwin_crddm | 80 | 71.1333 | 13.9961 | 69.2133 | 191.0262 | 24.9225 | 78.8000 | 49.8055 | 8.67e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_whddma_cadwin | 80 | 63.1020 | 13.0097 | 61.9063 | 214.5475 | 26.9688 | 71.3000 | 40.8743 | 9.79e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_whddma_chddma | 80 | 74.0701 | 18.2914 | 72.5192 | 185.7612 | 24.7138 | 102.5000 | 54.5111 | 0.0001 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_whddma_crddm | 80 | 65.4430 | 14.3018 | 63.8315 | 207.6775 | 23.1638 | 64.8000 | 39.9633 | 8.07e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_wrddm_cadwin | 80 | 65.6152 | 14.1338 | 63.6878 | 207.5200 | 26.1500 | 80.2000 | 43.5894 | 0.0001 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_wrddm_chddma | 80 | 68.4287 | 18.0153 | 67.0361 | 201.3800 | 24.6800 | 69.6000 | 44.7321 | 7.39e-05 | 6 | Apple M4 / 24.0 GB |
| injected_gas_sensor_drift | det4_s1_wrddm_crddm | 80 | 98.0095 | 24.6054 | 96.0725 | 143.2550 | 45.6737 | 96.5000 | 77.2550 | 0.0002 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_wadwin_cadwin | 400 | 164.1872 | 62.4541 | 157.5126 | 808.3192 | 18.0235 | 77.2000 | 56.4707 | 4.92e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_wadwin_chddma | 400 | 126.0689 | 56.7996 | 122.9561 | 1121.0873 | 15.6775 | 107.6000 | 52.8352 | 3.82e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_wadwin_crddm | 400 | 159.5217 | 45.1338 | 155.5309 | 681.8785 | 16.7530 | 80.9000 | 44.3823 | 4.62e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_whddma_cadwin | 400 | 87.7022 | 20.9652 | 85.5862 | 1166.2115 | 10.7760 | 44.0000 | 23.1775 | 2.32e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_whddma_chddma | 400 | 138.3135 | 32.2650 | 133.5628 | 750.5688 | 11.1858 | 46.5000 | 46.5005 | 2.01e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_whddma_crddm | 400 | 79.4309 | 25.3599 | 76.3386 | 1325.4770 | 9.6385 | 45.1000 | 23.8189 | 1.45e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_wrddm_cadwin | 400 | 110.9638 | 33.6186 | 102.5552 | 951.0020 | 11.5843 | 32.5000 | 26.2816 | 2.02e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_wrddm_chddma | 400 | 129.3807 | 52.4582 | 119.9759 | 868.0588 | 12.5060 | 49.9000 | 30.8467 | 2.95e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s0_wrddm_crddm | 400 | 148.9534 | 35.5643 | 144.7536 | 687.1728 | 12.9017 | 52.1000 | 47.8320 | 2.88e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_wadwin_cadwin | 400 | 123.1034 | 32.2043 | 120.7052 | 862.7225 | 10.9322 | 56.1000 | 47.1640 | 1.91e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_wadwin_chddma | 400 | 124.0775 | 34.0430 | 120.7943 | 860.2758 | 10.5220 | 58.4000 | 45.8211 | 1.46e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_wadwin_crddm | 400 | 181.3078 | 78.2661 | 164.2408 | 640.4575 | 11.6263 | 46.9000 | 45.8133 | 1.94e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_whddma_cadwin | 400 | 133.1555 | 67.2845 | 114.3063 | 872.0910 | 10.3605 | 54.6000 | 32.3624 | 1.34e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_whddma_chddma | 400 | 121.5625 | 37.9798 | 118.6215 | 896.8410 | 10.8310 | 49.4000 | 41.2714 | 1.66e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_whddma_crddm | 400 | 109.3199 | 35.7475 | 106.9212 | 985.9357 | 10.9437 | 53.0000 | 34.5618 | 2.39e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_wrddm_cadwin | 400 | 121.5213 | 39.2153 | 117.2505 | 888.2135 | 11.9650 | 58.4000 | 35.7794 | 2.54e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_wrddm_chddma | 400 | 171.3074 | 76.7892 | 148.2665 | 685.6452 | 11.3532 | 48.9000 | 36.4165 | 1.84e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_covertype | det4_s1_wrddm_crddm | 400 | 289.9982 | 233.8977 | 225.3804 | 435.7982 | 14.2387 | 76.0000 | 54.5574 | 2.08e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_wadwin_cadwin | 240 | 9.6813 | 2.3833 | 9.3465 | 4582.5688 | 8.7096 | 29.4000 | 7.1948 | 7.80e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_wadwin_chddma | 400 | 10.3797 | 2.9274 | 9.0645 | 4353.3495 | 5.1040 | 25.0000 | 8.2222 | 3.82e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_wadwin_crddm | 400 | 9.1995 | 2.4429 | 8.7102 | 4898.2653 | 6.2742 | 25.8000 | 7.9290 | 4.73e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_whddma_cadwin | 400 | 10.8979 | 1.5389 | 10.2242 | 3936.8895 | 3.7645 | 12.4000 | 4.2997 | 2.83e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_whddma_chddma | 240 | 13.2565 | 2.4211 | 12.7258 | 3273.9608 | 7.0879 | 19.6000 | 6.4136 | 7.39e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_whddma_crddm | 400 | 11.4766 | 2.0025 | 10.5922 | 3768.3010 | 4.1740 | 17.0000 | 4.5743 | 2.58e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_wrddm_cadwin | 400 | 10.5081 | 2.0058 | 9.7823 | 4143.5783 | 4.2855 | 21.0000 | 4.6109 | 2.86e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_wrddm_chddma | 400 | 10.7422 | 2.0022 | 10.2185 | 4060.6908 | 5.1180 | 20.4000 | 5.0498 | 4.31e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s0_wrddm_crddm | 240 | 13.5752 | 1.9940 | 13.1719 | 3169.3183 | 11.2754 | 25.0000 | 7.6585 | 1.36e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_wadwin_cadwin | 240 | 14.8384 | 2.1410 | 14.2442 | 2890.1504 | 5.5217 | 19.2000 | 7.3166 | 4.73e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_wadwin_chddma | 400 | 14.4516 | 2.7679 | 13.7492 | 3006.0595 | 4.9470 | 17.5000 | 5.8643 | 3.86e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_wadwin_crddm | 400 | 16.6161 | 8.9189 | 14.2469 | 2778.3195 | 5.3855 | 21.9000 | 5.9497 | 6.56e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_whddma_cadwin | 400 | 13.8117 | 3.4343 | 12.9667 | 3229.6395 | 4.4998 | 17.5000 | 4.9942 | 5.30e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_whddma_chddma | 240 | 13.5851 | 1.9597 | 13.2473 | 3158.0437 | 5.6921 | 19.3000 | 7.2086 | 4.85e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_whddma_crddm | 400 | 13.0855 | 2.8830 | 11.9788 | 3347.0867 | 4.5840 | 22.7000 | 5.2794 | 3.50e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_wrddm_cadwin | 400 | 12.6328 | 2.2245 | 11.8888 | 3422.1960 | 4.6387 | 21.4000 | 5.6140 | 3.56e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_wrddm_chddma | 400 | 14.0782 | 5.2725 | 12.6124 | 3200.0447 | 4.3680 | 22.5000 | 5.7893 | 3.35e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_electricity | det4_s1_wrddm_crddm | 400 | 18.8067 | 6.9236 | 15.3460 | 2483.7623 | 8.7658 | 24.3000 | 9.2542 | 7.17e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_wadwin_cadwin | 400 | 77.5966 | 26.2860 | 59.2918 | 188.3605 | 8.2767 | 56.2000 | 45.0069 | 6.41e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_wadwin_chddma | 400 | 61.3479 | 26.9699 | 47.4069 | 247.8388 | 7.5573 | 30.9000 | 33.7116 | 4.74e-06 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_wadwin_crddm | 400 | 33.5289 | 16.1360 | 31.1331 | 431.5915 | 35.7653 | 98.6000 | 32.8329 | 0.0002 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_whddma_cadwin | 400 | 32.6367 | 4.9172 | 32.2933 | 410.2290 | 32.7945 | 85.3000 | 29.5557 | 0.0003 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_whddma_chddma | 400 | 45.4022 | 11.6372 | 44.9161 | 307.3955 | 50.0415 | 107.7000 | 45.8017 | 0.0005 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_whddma_crddm | 400 | 34.8212 | 7.6204 | 34.4774 | 390.0718 | 35.6213 | 86.4000 | 31.3174 | 0.0003 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_wrddm_cadwin | 400 | 31.6639 | 4.9904 | 31.3424 | 423.6830 | 35.1792 | 84.2000 | 30.7687 | 0.0003 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_wrddm_chddma | 400 | 33.4949 | 7.0731 | 33.1653 | 406.8240 | 38.1675 | 85.2000 | 34.8599 | 0.0003 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s0_wrddm_crddm | 400 | 55.2050 | 13.0556 | 54.6486 | 256.0557 | 58.3775 | 131.8000 | 58.3396 | 0.0006 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_wadwin_cadwin | 400 | 54.4540 | 11.0943 | 53.7993 | 250.5633 | 57.6372 | 129.6000 | 52.3171 | 0.0006 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_wadwin_chddma | 400 | 55.7603 | 11.2959 | 54.6514 | 244.3545 | 54.3565 | 118.0000 | 48.0166 | 0.0006 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_wadwin_crddm | 400 | 65.0052 | 18.7789 | 61.0169 | 216.3992 | 22.4632 | 104.9000 | 48.1776 | 0.0002 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_whddma_cadwin | 400 | 53.9919 | 11.0104 | 52.1483 | 252.7947 | 14.1485 | 78.2000 | 39.5892 | 2.46e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_whddma_chddma | 400 | 62.7484 | 14.5971 | 61.0536 | 220.1185 | 17.8390 | 103.0000 | 54.5812 | 4.20e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_whddma_crddm | 400 | 66.2172 | 23.0138 | 60.4614 | 217.4735 | 12.1915 | 64.0000 | 40.9655 | 1.57e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_wrddm_cadwin | 400 | 78.9043 | 42.3851 | 68.8653 | 191.4570 | 9.5890 | 73.6000 | 43.0190 | 1.26e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_wrddm_chddma | 400 | 66.2677 | 19.3152 | 62.4948 | 214.2480 | 11.4625 | 69.0000 | 44.8312 | 1.96e-05 | 6 | Apple M4 / 24.0 GB |
| injected_paper_gas_sensor_drift | det4_s1_wrddm_crddm | 400 | 173.6268 | 50.7416 | 146.6075 | 83.9848 | 12.4640 | 61.9000 | 72.8750 | 2.22e-05 | 6 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s0_wadwin_chddma | 1 | 44.8100 | - | 45.1410 | 1179.3000 | 13.7000 | 13.7000 | 32.2600 | 2.21e-05 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s0_wadwin_crddm | 1 | 24.0800 | - | 24.2050 | 2194.6000 | 27.6000 | 27.6000 | 34.3500 | 8.65e-05 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s0_whddma_cadwin | 1 | 14.4300 | - | 14.6400 | 3662.3000 | 7.8000 | 7.8000 | 10.8100 | 4.22e-06 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s0_whddma_crddm | 1 | 14.6500 | - | 14.6310 | 3606.4000 | 9.6000 | 9.6000 | 10.4700 | 6.06e-06 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s0_wrddm_cadwin | 1 | 19.8900 | - | 20.1220 | 2656.8000 | 15.8000 | 15.8000 | 18.4000 | 4.30e-05 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s0_wrddm_chddma | 1 | 14.3700 | - | 14.4780 | 3676.6000 | 10.9000 | 10.9000 | 15.7700 | 3.85e-06 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s1_wadwin_chddma | 1 | 33.1900 | - | 33.1270 | 1592.3000 | 9.3000 | 9.3000 | 38.0100 | 2.49e-06 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s1_wadwin_crddm | 1 | 34.7700 | - | 34.7890 | 1520.1000 | 19.9000 | 19.9000 | 45.4700 | 2.03e-05 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s1_whddma_cadwin | 1 | 31.7000 | - | 32.2100 | 1667.3000 | 20.6000 | 20.6000 | 24.2300 | 0.0001 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s1_whddma_crddm | 1 | 33.6000 | - | 33.3990 | 1573.0000 | 24.5000 | 24.5000 | 31.6600 | 8.41e-05 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s1_wrddm_cadwin | 1 | 34.0400 | - | 33.7270 | 1552.4000 | 3.9000 | 3.9000 | 28.4700 | 6.92e-07 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s1_wrddm_chddma | 1 | 34.2600 | - | 34.6850 | 1542.7000 | 26.9000 | 26.9000 | 33.5300 | 6.24e-05 | 1 | Apple M4 / 24.0 GB |
| insects_abrupt_balanced | det4_s1_wrddm_crddm | 1 | 49.4100 | - | 49.5550 | 1069.7000 | 31.0000 | 31.0000 | 40.5400 | 6.35e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s0_wadwin_chddma | 1 | 63.6500 | - | 64.1430 | 1256.6000 | 27.4000 | 27.4000 | 40.7700 | 5.12e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s0_wadwin_crddm | 1 | 60.4500 | - | 60.9780 | 1323.1000 | 22.7000 | 22.7000 | 49.2500 | 1.66e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s0_whddma_cadwin | 1 | 27.4600 | - | 27.4640 | 2912.7000 | 9.4000 | 9.4000 | 24.9900 | 2.06e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s0_whddma_crddm | 1 | 33.0600 | - | 33.2010 | 2419.5000 | 27.4000 | 27.4000 | 28.5300 | 0.0001 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s0_wrddm_cadwin | 1 | 31.9000 | - | 32.3020 | 2507.1000 | 18.5000 | 18.5000 | 23.0600 | 8.46e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s0_wrddm_chddma | 1 | 38.1600 | - | 38.2170 | 2096.3000 | 21.4000 | 21.4000 | 31.1200 | 8.30e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s1_wadwin_chddma | 1 | 52.4100 | - | 52.6500 | 1526.3000 | 25.6000 | 25.6000 | 46.8400 | 8.73e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s1_wadwin_crddm | 1 | 54.1800 | - | 54.6550 | 1476.3000 | 48.1000 | 48.1000 | 45.7900 | 0.0002 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s1_whddma_cadwin | 1 | 54.2700 | - | 52.8520 | 1474.0000 | 28.2000 | 28.2000 | 39.6900 | 1.63e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s1_whddma_crddm | 1 | 49.5200 | - | 49.0430 | 1615.4000 | 8.7000 | 8.7000 | 38.2600 | 3.12e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s1_wrddm_cadwin | 1 | 51.2900 | - | 50.9370 | 1559.6000 | 21.4000 | 21.4000 | 45.2100 | 1.08e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s1_wrddm_chddma | 1 | 51.4000 | - | 51.3830 | 1556.1000 | 26.1000 | 26.1000 | 45.1800 | 3.80e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_abrupt_reoccurring_balanced | det4_s1_wrddm_crddm | 1 | 55.8100 | - | 55.8040 | 1433.1000 | 38.0000 | 38.0000 | 40.2100 | 0.0003 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s0_wadwin_chddma | 1 | 47.2700 | - | 47.2170 | 1206.2000 | 11.9000 | 11.9000 | 25.5200 | 1.26e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s0_wadwin_crddm | 1 | 31.6400 | - | 31.7490 | 1802.3000 | 15.6000 | 15.6000 | 25.6200 | 4.84e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s0_whddma_cadwin | 1 | 31.2800 | - | 31.4390 | 1822.6000 | 4.5000 | 4.5000 | 21.1800 | 3.04e-07 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s0_whddma_crddm | 1 | 31.6000 | - | 31.9920 | 1804.4000 | 9.3000 | 9.3000 | 23.4200 | 4.07e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s0_wrddm_cadwin | 1 | 18.3000 | - | 18.6590 | 3115.4000 | 4.7000 | 4.7000 | 10.6300 | 1.18e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s0_wrddm_chddma | 1 | 35.2900 | - | 35.5160 | 1615.8000 | 18.9000 | 18.9000 | 24.1900 | 6.28e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s1_wadwin_chddma | 1 | 45.4400 | - | 45.4940 | 1254.9000 | 9.9000 | 9.9000 | 22.7900 | 3.10e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s1_wadwin_crddm | 1 | 44.9500 | - | 44.9240 | 1268.5000 | 14.0000 | 14.0000 | 22.9900 | 1.13e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s1_whddma_cadwin | 1 | 43.8700 | - | 43.9490 | 1299.7000 | 16.0000 | 16.0000 | 26.5700 | 3.06e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s1_whddma_crddm | 1 | 44.0500 | - | 43.9460 | 1294.2000 | 3.4000 | 3.4000 | 28.1100 | 2.26e-07 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s1_wrddm_cadwin | 1 | 69.3000 | - | 65.6600 | 822.7000 | 11.5000 | 11.5000 | 20.4600 | 1.23e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s1_wrddm_chddma | 1 | 140.8400 | - | 108.9410 | 404.8000 | 0.0000 | 0.0000 | 30.4400 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_balanced | det4_s1_wrddm_crddm | 1 | 155.7400 | - | 79.1270 | 366.1000 | 6.6000 | 6.6000 | 46.1900 | 4.32e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s0_wadwin_chddma | 1 | 17.3400 | - | 17.5560 | 1392.9000 | 30.7000 | 30.7000 | 23.7700 | 0.0001 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s0_wadwin_crddm | 1 | 10.2400 | - | 10.0700 | 2357.7000 | 16.3000 | 16.3000 | 22.6000 | 2.40e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s0_whddma_cadwin | 1 | 7.9900 | - | 7.6410 | 3021.3000 | 6.0000 | 6.0000 | 8.9300 | 1.80e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s0_whddma_crddm | 1 | 7.0100 | - | 7.0660 | 3445.9000 | 10.4000 | 10.4000 | 8.9400 | 4.99e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s0_wrddm_cadwin | 1 | 6.7400 | - | 6.8240 | 3584.3000 | 9.2000 | 9.2000 | 8.9600 | 7.11e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s0_wrddm_chddma | 1 | 6.9300 | - | 6.9560 | 3485.1000 | 7.5000 | 7.5000 | 8.9400 | 2.06e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s1_wadwin_chddma | 1 | 17.6800 | - | 17.8870 | 1365.6000 | 37.2000 | 37.2000 | 34.4100 | 0.0001 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s1_wadwin_crddm | 1 | 17.5500 | - | 17.6840 | 1376.5000 | 32.8000 | 32.8000 | 24.3500 | 0.0001 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s1_whddma_cadwin | 1 | 16.6300 | - | 16.8620 | 1452.4000 | 22.3000 | 22.3000 | 19.0700 | 4.14e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s1_whddma_crddm | 1 | 16.8800 | - | 17.1420 | 1430.6000 | 21.0000 | 21.0000 | 21.0000 | 7.00e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s1_wrddm_cadwin | 1 | 15.7100 | - | 15.6320 | 1537.2000 | 15.5000 | 15.5000 | 25.4100 | 1.23e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s1_wrddm_chddma | 1 | 16.1400 | - | 16.3750 | 1496.5000 | 21.9000 | 21.9000 | 19.6900 | 6.92e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_gradual_balanced | det4_s1_wrddm_crddm | 1 | 17.4000 | - | 17.5680 | 1388.1000 | 44.6000 | 44.6000 | 36.8500 | 0.0002 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s0_wadwin_chddma | 1 | 83.8100 | - | 84.4770 | 954.4000 | 15.9000 | 15.9000 | 41.2100 | 3.79e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s0_wadwin_crddm | 1 | 66.2200 | - | 66.5870 | 1207.8000 | 63.2000 | 63.2000 | 43.6500 | 0.0005 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s0_whddma_cadwin | 1 | 22.2300 | - | 22.2570 | 3598.2000 | 8.4000 | 8.4000 | 11.6000 | 1.93e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s0_whddma_crddm | 1 | 35.9400 | - | 35.9920 | 2225.7000 | 10.5000 | 10.5000 | 25.8600 | 2.28e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s0_wrddm_cadwin | 1 | 20.1200 | - | 20.0760 | 3975.7000 | 8.6000 | 8.6000 | 10.0300 | 1.73e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s0_wrddm_chddma | 1 | 36.8000 | - | 36.8150 | 2173.5000 | 24.5000 | 24.5000 | 27.6000 | 7.58e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s1_wadwin_chddma | 1 | 52.7000 | - | 52.6930 | 1517.9000 | 12.8000 | 12.8000 | 49.6800 | 6.16e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s1_wadwin_crddm | 1 | 53.3700 | - | 53.0350 | 1498.7000 | 0.0000 | 0.0000 | 48.0100 | 0.0000 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s1_whddma_cadwin | 1 | 50.1300 | - | 50.2510 | 1595.6000 | 21.1000 | 21.1000 | 33.0100 | 4.98e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s1_whddma_crddm | 1 | 52.7800 | - | 53.0220 | 1515.4000 | 13.1000 | 13.1000 | 47.3600 | 1.35e-05 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s1_wrddm_cadwin | 1 | 52.6400 | - | 52.2490 | 1519.4000 | 12.0000 | 12.0000 | 33.3000 | 3.07e-06 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s1_wrddm_chddma | 1 | 48.0900 | - | 47.9130 | 1663.3000 | 11.6000 | 11.6000 | 26.1800 | 6.52e-07 | 1 | Apple M4 / 24.0 GB |
| insects_incremental_reoccurring_balanced | det4_s1_wrddm_crddm | 1 | 63.0600 | - | 62.4530 | 1268.5000 | 34.3000 | 34.3000 | 46.6600 | 3.11e-05 | 1 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_wadwin_cadwin | 40 | 25.0267 | 1.6166 | 25.0443 | 4013.6925 | 12.0925 | 22.2000 | 5.5998 | 2.67e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_wadwin_chddma | 40 | 27.0345 | 3.8580 | 27.4380 | 3793.0600 | 10.2650 | 21.9000 | 8.9210 | 1.09e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_wadwin_crddm | 40 | 26.0345 | 2.0385 | 26.6936 | 3865.5425 | 11.7450 | 28.6000 | 7.0842 | 3.06e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_whddma_cadwin | 40 | 23.8008 | 2.5275 | 23.5399 | 4248.1250 | 4.0775 | 13.1000 | 3.8880 | 2.55e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_whddma_chddma | 40 | 27.0445 | 2.2836 | 26.8481 | 3724.4025 | 7.1975 | 17.1000 | 5.5270 | 1.26e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_whddma_crddm | 40 | 24.1292 | 1.8094 | 23.9569 | 4165.7650 | 5.6300 | 17.7000 | 3.7345 | 1.31e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_wrddm_cadwin | 40 | 24.1270 | 2.3420 | 23.4666 | 4182.4050 | 5.6100 | 16.6000 | 3.9558 | 3.82e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_wrddm_chddma | 40 | 26.5973 | 2.9812 | 25.6361 | 3808.3450 | 5.4550 | 18.7000 | 4.3865 | 5.41e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s0_wrddm_crddm | 40 | 24.5822 | 2.0677 | 24.2995 | 4100.0375 | 13.2000 | 21.4000 | 7.4285 | 3.42e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_wadwin_cadwin | 40 | 29.4893 | 1.1225 | 29.3787 | 3396.0100 | 9.3900 | 17.3000 | 5.7535 | 1.25e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_wadwin_chddma | 40 | 33.4903 | 2.1981 | 32.4013 | 2998.7475 | 9.7825 | 17.4000 | 5.6173 | 1.16e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_wadwin_crddm | 40 | 32.9382 | 1.6207 | 31.2922 | 3043.2650 | 9.8425 | 18.6000 | 5.8232 | 3.27e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_whddma_cadwin | 40 | 29.9735 | 2.8878 | 29.6647 | 3370.0000 | 8.5725 | 20.0000 | 4.8875 | 1.18e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_whddma_chddma | 40 | 30.9635 | 2.3770 | 30.8385 | 3249.8600 | 10.2050 | 19.0000 | 5.7870 | 2.76e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_whddma_crddm | 40 | 28.8048 | 3.1190 | 28.7426 | 3516.5375 | 7.1900 | 17.5000 | 4.7198 | 1.30e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_wrddm_cadwin | 40 | 28.7995 | 2.3395 | 28.6699 | 3496.6950 | 8.9425 | 17.9000 | 5.3902 | 1.97e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_wrddm_chddma | 40 | 29.8645 | 2.5745 | 29.7899 | 3373.9475 | 7.8150 | 21.2000 | 5.5373 | 1.29e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_binary | det4_s1_wrddm_crddm | 40 | 30.0263 | 2.5434 | 29.8479 | 3354.0475 | 12.1650 | 21.9000 | 5.6535 | 3.62e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s0_wadwin_chddma | 40 | 124.2000 | 48.9558 | 76.4071 | 962.6975 | 4.7075 | 19.6000 | 16.7042 | 2.89e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s0_wadwin_crddm | 40 | 131.8570 | 46.0522 | 80.0432 | 846.2000 | 6.7875 | 24.8000 | 16.0767 | 3.84e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s0_whddma_cadwin | 40 | 46.0158 | 9.8664 | 35.7870 | 2264.5725 | 4.7575 | 15.6000 | 7.8097 | 2.19e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s0_whddma_crddm | 40 | 46.7410 | 12.0193 | 37.0469 | 2269.0275 | 5.5450 | 15.1000 | 7.2843 | 3.08e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s0_wrddm_cadwin | 40 | 50.0347 | 12.2416 | 41.5164 | 2124.9875 | 6.1300 | 21.1000 | 9.8112 | 3.66e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s0_wrddm_chddma | 40 | 42.3720 | 8.2306 | 40.0635 | 2465.6700 | 6.7475 | 18.7000 | 10.7508 | 3.69e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s1_wadwin_chddma | 40 | 57.5960 | 9.5961 | 51.6730 | 1779.1425 | 7.7600 | 20.4000 | 15.8628 | 7.07e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s1_wadwin_crddm | 40 | 48.4430 | 3.8467 | 47.8142 | 2077.5575 | 9.3175 | 28.1000 | 15.1585 | 1.15e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s1_whddma_cadwin | 40 | 55.3505 | 10.1482 | 49.0058 | 1869.0475 | 7.5375 | 23.3000 | 11.4683 | 1.06e-05 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s1_whddma_crddm | 40 | 46.3722 | 4.8505 | 45.4100 | 2182.7775 | 7.4525 | 24.3000 | 12.0113 | 6.09e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s1_wrddm_cadwin | 40 | 46.2542 | 3.6531 | 46.2245 | 2176.7000 | 5.0875 | 16.6000 | 12.4078 | 2.41e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s1_wrddm_chddma | 40 | 52.8388 | 8.2777 | 50.2601 | 1937.1350 | 6.4000 | 19.0000 | 13.7468 | 5.21e-06 | 6 | Apple M4 / 24.0 GB |
| synthetic_multiclass | det4_s1_wrddm_crddm | 40 | 52.7220 | 4.5735 | 52.3395 | 1913.4975 | 9.2475 | 21.5000 | 16.9295 | 8.06e-06 | 6 | Apple M4 / 24.0 GB |
