# dataset_0921 vs literature (2026-10-12 11:29)

Runs used: 11 of 811 (smoke runs excluded, non-comparable runs excluded).
Registry: `configs/datasets_0921.json`. Metrics: `src/metrics/evaluate_run.py`.

## Prequential datasets

Difference = our mean - best literature value for that metric. 95% CI is a t-interval over seeds.

### electricity (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| arf10 | acc_prequential | 1 | 0.8812 | - | - | 0.9500 | TabFM+FIFO | -0.0688 | 0.9008 | ARF (MOA, 100 trees) | -0.0196 |
| arf10 | kappa_t | 1 | 0.1901 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.1336 | 0.3237 | ARF (MOA, 100 trees) | -0.1336 |
| arf10 | kappa_m | 1 | 0.7201 | - | - | - | - | - | - | - | - |
| arf10 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -0.0000 | - | - | - |
| arf10 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| arf100 | acc_prequential | 1 | 0.8954 | - | - | 0.9500 | TabFM+FIFO | -0.0546 | 0.9008 | ARF (MOA, 100 trees) | -0.0054 |
| arf100 | kappa_t | 1 | 0.2869 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.0368 | 0.3237 | ARF (MOA, 100 trees) | -0.0368 |
| arf100 | kappa_m | 1 | 0.7535 | - | - | - | - | - | - | - | - |
| arf100 | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -0.0000 | - | - | - |
| arf100 | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| e10bft | acc_prequential | 1 | 0.8267 | - | - | 0.9500 | TabFM+FIFO | -0.1233 | 0.9008 | ARF (MOA, 100 trees) | -0.0741 |
| e10bft | kappa_t | 1 | -0.1814 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.5051 | 0.3237 | ARF (MOA, 100 trees) | -0.5051 |
| e10bft | kappa_m | 1 | 0.5916 | - | - | - | - | - | - | - | - |
| e10bft | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -0.0000 | - | - | - |
| e10bft | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_paper | acc_prequential | 1 | 0.8276 | - | - | 0.9500 | TabFM+FIFO | -0.1224 | 0.9008 | ARF (MOA, 100 trees) | -0.0732 |
| ecpf_paper | kappa_t | 1 | -0.1751 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4988 | 0.3237 | ARF (MOA, 100 trees) | -0.4988 |
| ecpf_paper | kappa_m | 1 | 0.5938 | - | - | - | - | - | - | - | - |
| ecpf_paper | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -0.0000 | - | - | - |
| ecpf_paper | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | acc_prequential | 1 | 0.8299 | - | - | 0.9500 | TabFM+FIFO | -0.1201 | 0.9008 | ARF (MOA, 100 trees) | -0.0709 |
| ecpf_reuse_value | kappa_t | 1 | -0.1594 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.4831 | 0.3237 | ARF (MOA, 100 trees) | -0.4831 |
| ecpf_reuse_value | kappa_m | 1 | 0.5992 | - | - | - | - | - | - | - | - |
| ecpf_reuse_value | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -0.0000 | - | - | - |
| ecpf_reuse_value | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| ht | acc_prequential | 1 | 0.7956 | - | - | 0.9500 | TabFM+FIFO | -0.1544 | 0.9008 | ARF (MOA, 100 trees) | -0.1052 |
| ht | kappa_t | 1 | -0.3931 | - | - | 0.3237 | ARF (MOA, 100 trees) | -0.7168 | 0.3237 | ARF (MOA, 100 trees) | -0.7168 |
| ht | kappa_m | 1 | 0.5185 | - | - | - | - | - | - | - | - |
| ht | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -0.0000 | - | - | - |
| ht | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |
| nb | acc_prequential | 1 | 0.7287 | - | - | 0.9500 | TabFM+FIFO | -0.2213 | 0.9008 | ARF (MOA, 100 trees) | -0.1721 |
| nb | kappa_t | 1 | -0.8490 | - | - | 0.3237 | ARF (MOA, 100 trees) | -1.1727 | 0.3237 | ARF (MOA, 100 trees) | -1.1727 |
| nb | kappa_m | 1 | 0.3609 | - | - | - | - | - | - | - | - |
| nb | baseline_no_change_acc | 1 | 0.8533 | - | - | 0.8533 | No-Change | -0.0000 | - | - | - |
| nb | baseline_majority_acc | 1 | 0.5755 | - | - | - | - | - | - | - | - |

OpenML 151 / MOA elecNormNew, 45,312 rows, same as literature. Calibrated: baseline_no_change_acc reproduces Souza et al. 85.33%.

### insects_abrupt_balanced (role: report)

| preset | metric | n | mean | std | ci95 | sota_value | sota_method | diff_vs_sota | classic_value | classic_method | diff_vs_classic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| arf10 | acc_window1000_mean | 1 | 0.7309 | - | - | 0.7434 | ARF | -0.0125 | 0.7434 | ARF | -0.0125 |
| arf10 | acc_prequential | 1 | 0.7350 | - | - | 0.6602 | NB + STEPD | 0.0748 | - | - | - |
| arf10 | kappa | 1 | 0.6820 | - | - | - | - | - | - | - | - |
| arf10 | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |
| e10bft | acc_window1000_mean | 1 | 0.6425 | - | - | 0.7434 | ARF | -0.1009 | 0.7434 | ARF | -0.1009 |
| e10bft | acc_prequential | 1 | 0.6469 | - | - | 0.6602 | NB + STEPD | -0.0133 | - | - | - |
| e10bft | kappa | 1 | 0.5762 | - | - | - | - | - | - | - | - |
| e10bft | n_alarms | 1 | 14.0000 | - | - | - | - | - | - | - | - |
| e10bft | f1 | 1 | 0.5000 | - | - | - | - | - | - | - | - |
| e10bft | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| ecpf_paper | acc_window1000_mean | 1 | 0.6384 | - | - | 0.7434 | ARF | -0.1050 | 0.7434 | ARF | -0.1050 |
| ecpf_paper | acc_prequential | 1 | 0.6426 | - | - | 0.6602 | NB + STEPD | -0.0176 | - | - | - |
| ecpf_paper | kappa | 1 | 0.5712 | - | - | - | - | - | - | - | - |
| ecpf_paper | n_alarms | 1 | 26.0000 | - | - | - | - | - | - | - | - |
| ecpf_paper | f1 | 1 | 0.4571 | - | - | - | - | - | - | - | - |
| ecpf_paper | episode_recall | 1 | 0.8000 | - | - | - | - | - | - | - | - |
| nb | acc_window1000_mean | 1 | 0.5058 | - | - | 0.7434 | ARF | -0.2376 | 0.7434 | ARF | -0.2376 |
| nb | acc_prequential | 1 | 0.5068 | - | - | 0.6602 | NB + STEPD | -0.1534 | - | - | - |
| nb | kappa | 1 | 0.4081 | - | - | - | - | - | - | - | - |
| nb | n_alarms | 1 | 0.0000 | - | - | - | - | - | - | - | - |

Same data and change points as Souza et al. 2020. Table 5 is sliding-window (1000) accuracy -> compare acc_window1000_mean; Table 6 (NB + detector) -> compare acc_prequential. delta_max is not from the paper (it reports detection counts only).

### Ranking across datasets on `acc_prequential`

_Not enough complete blocks for rank tests (1 blocks x 7 presets with every preset present)._

### Ranking across datasets on `acc_window1000_mean`

_Not enough complete blocks for rank tests (1 blocks x 4 presets with every preset present)._

### Ranking across datasets on `kappa_t`

_Not enough complete blocks for rank tests (1 blocks x 7 presets with every preset present)._

