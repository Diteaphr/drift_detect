# dataset_0921 vs literature (2026-10-12 03:20)

Runs used: 800 of 813 (smoke runs excluded, non-comparable runs excluded).
Registry: `configs/datasets_0921.json`. Metrics: `src/metrics/evaluate_run.py`.

## Injected drift detection (pooled over trials)

tp/fp/fn are summed over all trials of a cell before precision/recall/F1, as in Cerqueira et al.; `far_cerqueira` is their FAR (summed false alarms / one stream length x 1000), `far_per_run` the per-stream average. `sota_f1` is the best of their 14 detectors for that cell.

### injected_paper_electricity

Only preset kinds ['detector'] follow the literature protocol on this dataset; other rows appear only with --include-noncomparable.

| cell | preset | n_runs | f1 | precision | recall | episode_recall | mdt | far_cerqueira | sota_f1 | sota_method | diff_f1_vs_sota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | det_adwin | 50 | 0.2775 | 0.2162 | 0.3871 | 0.2400 | 1691.5000 | 1.9200 | 0.6980 | ADWIN | -0.4205 |
| abrupt/class_prior | det_adwin_river | 50 | 0.2198 | 0.2439 | 0.2000 | 0.2000 | 1757.4000 | 0.6841 | 0.6980 | ADWIN | -0.4782 |
| abrupt/feature_filtering | det_adwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.5076 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_filtering | det_adwin_river | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.2648 | 0.2450 | CUSUM | -0.2450 |
| abrupt/feature_permutation | det_adwin | 50 | 0.3364 | 0.2467 | 0.5286 | 0.3400 | 1369.2941 | 2.4938 | 1.0000 | ABCD(X) | -0.6636 |
| abrupt/feature_permutation | det_adwin_river | 50 | 0.6577 | 0.5765 | 0.7656 | 0.7000 | 823.8857 | 0.7945 | 1.0000 | ABCD(X) | -0.3423 |
| abrupt/label_swap | det_adwin | 50 | 0.2193 | 0.1276 | 0.7789 | 0.5800 | 1532.1034 | 11.1670 | 0.5660 | SEED | -0.3467 |
| abrupt/label_swap | det_adwin_river | 50 | 0.4557 | 0.3214 | 0.7826 | 0.7000 | 747.7429 | 2.5159 | 0.5660 | SEED | -0.1103 |
| gradual/class_prior | det_adwin | 50 | 0.0097 | 0.0064 | 0.0200 | 0.0200 | 439.0000 | 3.4428 | 0.2950 | STEPD | -0.2853 |
| gradual/class_prior | det_adwin_river | 50 | 0.0215 | 0.0233 | 0.0200 | 0.0200 | 439.0000 | 0.9269 | 0.2950 | STEPD | -0.2735 |
| gradual/feature_filtering | det_adwin | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.5076 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_filtering | det_adwin_river | 50 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | - | 0.3090 | 0.1470 | STUDD | -0.1470 |
| gradual/feature_permutation | det_adwin | 50 | 0.0163 | 0.0137 | 0.0200 | 0.0200 | 1557.0000 | 1.5890 | 0.9840 | ABCD(X) | -0.9677 |
| gradual/feature_permutation | det_adwin_river | 50 | 0.3273 | 0.3000 | 0.3600 | 0.3600 | 1817.6111 | 0.9269 | 0.9840 | ABCD(X) | -0.6567 |
| gradual/label_swap | det_adwin | 50 | 0.0043 | 0.0024 | 0.0200 | 0.0200 | 1563.0000 | 9.1808 | 0.3830 | STEPD | -0.3787 |
| gradual/label_swap | det_adwin_river | 50 | 0.2653 | 0.1793 | 0.5098 | 0.5000 | 1675.4800 | 2.6262 | 0.3830 | STEPD | -0.1177 |

Calibration: `det_adwin` vs their ADWIN delta=0.01 (their hypertuned setup) (same cell, pooled):

| cell | f1 | calib_f1 | episode_recall | calib_episode_recall | mdt | calib_mdt | far_cerqueira | calib_far |
|---|---|---|---|---|---|---|---|---|
| abrupt/class_prior | 0.2775 | 0.6980 | 0.2400 | 0.5600 | 1691.5000 | 1202.0000 | 1.9200 | 2.5800 |
| abrupt/feature_filtering | 0.0000 | 0.1870 | 0.0000 | 0.1000 | - | 1504.0000 | 0.5076 | 2.4700 |
| abrupt/feature_permutation | 0.3364 | 0.7370 | 0.3400 | 0.8000 | 1369.2941 | 1093.0000 | 2.4938 | 1.3200 |
| abrupt/label_swap | 0.2193 | 0.2510 | 0.5800 | 0.8200 | 1532.1034 | 1682.0000 | 11.1670 | 16.9300 |
| gradual/class_prior | 0.0097 | 0.0880 | 0.0200 | 0.1000 | 439.0000 | 2266.0000 | 3.4428 | 6.3600 |
| gradual/feature_filtering | 0.0000 | 0.0250 | 0.0000 | 0.0400 | - | 1362.0000 | 0.5076 | 2.3800 |
| gradual/feature_permutation | 0.0163 | 0.0500 | 0.0200 | 0.0600 | 1557.0000 | 2146.0000 | 1.5890 | 1.4800 |
| gradual/label_swap | 0.0043 | 0.0000 | 0.0200 | 0.0000 | 1563.0000 | - | 9.1808 | 17.6600 |

### Ranking across dataset x cell on pooled F1

Blocks: 8; presets: 2. Average rank (1 = best):

| preset | avg rank | mean score |
|---|---|---|
| det_adwin_river | 1.25 | 0.2434 |
| det_adwin | 1.75 | 0.1079 |

Wilcoxon signed-rank, det_adwin vs others (two-sided, Holm-corrected):

| other | mean diff | W | p | p (Holm) |
|---|---|---|---|---|
| det_adwin_river | -0.1355 | 2.0 | 0.07474 | 0.07474 |

