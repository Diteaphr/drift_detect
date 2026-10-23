# dataset_0921 vs literature (2026-10-22 05:28)

Runs used: 119 of 29431 (smoke runs excluded, non-comparable runs excluded).
Registry: `configs/datasets_0921.json`. Metrics: `src/metrics/evaluate_run.py`.

## Prequential datasets

Difference = our mean - best literature value for that metric. 95% CI is a t-interval over seeds.

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

### Ranking across datasets on `acc_prequential`

Blocks: 3; presets: 18. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| det4_s0_whddma_chddma | 6.00 | 0.7799 |
| det4_s0_wrddm_crddm | 7.00 | 0.7691 |
| det4_s1_whddma_chddma | 7.33 | 0.7717 |
| det4_s1_wadwin_chddma | 7.67 | 0.7515 |
| det4_s1_wrddm_cadwin | 8.00 | 0.7500 |
| det4_s1_whddma_cadwin | 8.00 | 0.7506 |
| det4_s1_wadwin_crddm | 8.00 | 0.7511 |
| det4_s1_wadwin_cadwin | 8.00 | 0.7656 |
| det4_s1_wrddm_crddm | 8.33 | 0.7631 |
| det4_s0_whddma_crddm | 9.67 | 0.7400 |
| det4_s1_whddma_crddm | 9.67 | 0.7482 |
| det4_s0_wrddm_chddma | 10.00 | 0.7391 |
| det4_s1_wrddm_chddma | 10.33 | 0.7480 |
| det4_s0_wadwin_cadwin | 11.33 | 0.7431 |
| det4_s0_wrddm_cadwin | 12.33 | 0.7283 |
| det4_s0_whddma_cadwin | 12.33 | 0.7310 |
| det4_s0_wadwin_chddma | 13.33 | 0.7339 |
| det4_s0_wadwin_crddm | 13.67 | 0.7344 |

Friedman chi2 = 9.409, p = 0.9265.
Caution: only 3 blocks; Friedman / Nemenyi have little power below about 10.

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

Blocks: 3; presets: 18. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| det4_s0_whddma_chddma | 6.00 | -0.5732 |
| det4_s0_wrddm_crddm | 7.00 | -0.7930 |
| det4_s1_whddma_chddma | 7.33 | -0.7190 |
| det4_s1_wadwin_chddma | 7.67 | -1.1327 |
| det4_s1_wrddm_cadwin | 8.00 | -1.1601 |
| det4_s1_whddma_cadwin | 8.00 | -1.1601 |
| det4_s1_wadwin_crddm | 8.00 | -1.1401 |
| det4_s1_wadwin_cadwin | 8.00 | -0.8438 |
| det4_s1_wrddm_crddm | 8.33 | -0.8797 |
| det4_s0_whddma_crddm | 9.67 | -1.3853 |
| det4_s1_whddma_crddm | 9.67 | -1.1783 |
| det4_s0_wrddm_chddma | 10.00 | -1.4005 |
| det4_s1_wrddm_chddma | 10.33 | -1.1707 |
| det4_s0_wadwin_cadwin | 11.33 | -1.1763 |
| det4_s0_wrddm_cadwin | 12.33 | -1.4532 |
| det4_s0_whddma_cadwin | 12.33 | -1.4605 |
| det4_s0_wadwin_chddma | 13.33 | -1.4252 |
| det4_s0_wadwin_crddm | 13.67 | -1.3587 |

Friedman chi2 = 9.409, p = 0.9265.
Caution: only 3 blocks; Friedman / Nemenyi have little power below about 10.

## Cost (time and memory)

Mean per run. `runtime_s` is wall time, `cpu_time_s` process CPU time (both exclude data loading); `rss_increment_mb` is the peak resident memory of the run's own process minus its level before the system was built, `ram_hours_gb` that increment integrated over the run (GB x hours), `model_size_final_mb` the system's Python object size after the last instance. `concurrent_runs` is the most runs that executed at the same time as a run. Memory is per process and valid at any concurrency; times are strict only where `concurrent_runs` is 1 (`--workers 1`) and comparable only between rows with the same machine and the same `concurrent_runs` (CPU time is less affected by parallel load than wall time).

| dataset | preset | n | runtime_s | runtime_std | cpu_time_s | instances_per_s | rss_increment_mb | rss_increment_max_mb | model_size_final_mb | ram_hours_gb | concurrent_runs | machine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
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
