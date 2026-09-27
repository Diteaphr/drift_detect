C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\computation\expressions.py:21: UserWarning: Pandas requires version '2.8.4' or newer of 'numexpr' (version '2.8.3' currently installed).
  from pandas.core.computation.check import NUMEXPR_INSTALLED
C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\arrays\masked.py:61: UserWarning: Pandas requires version '1.3.6' or newer of 'bottleneck' (version '1.3.5' currently installed).
  from pandas.core import (
## 0. FP sub-labels (post hoc) and the expert the preceding hit installed

| config | label | (none) | late | pre_drift | stale_warning |
|---|---|---|---|---|---|
| htr-mwa50/error | echo | 13 | 0 | 0 | 0 |
| htr-mwa50/error | orphan | 148 | 7 | 1 | 2 |
| htr-nr/error | echo | 2 | 0 | 0 | 0 |
| htr-nr/error | orphan | 17 | 0 | 0 | 2 |
| htr/error | echo | 7 | 0 | 0 | 0 |
| htr/error | orphan | 48 | 6 | 1 | 3 | 

Reuse decision at each confirmation: length of the warning buffer it was made on (buffer = confirm_age + 1 instances; the reused best slot is chosen by its score on it):

| config | label | n | buf_median | buf_is_1 | buf_le_10 |
|---|---|---|---|---|---|
| htr-mwa50/error | echo | 13 | 50.000 | 0.000 | 0.000 |
| htr-mwa50/error | echo_inwin | 3 | 50.000 | 0.000 | 0.000 |
| htr-mwa50/error | hit | 12 | 50.000 | 0.000 | 0.000 |
| htr-mwa50/error | orphan | 158 | 65.000 | 0.000 | 0.000 |
| htr-nr/error | echo | 2 | 2081.000 | 0.000 | 0.000 |
| htr-nr/error | echo_inwin | 1 | 33.000 | 0.000 | 0.000 |
| htr-nr/error | hit | 15 | 33.000 | 0.467 | 0.467 |
| htr-nr/error | orphan | 19 | 705.000 | 0.211 | 0.211 |
| htr/error | echo | 7 | 65.000 | 0.286 | 0.286 |
| htr/error | echo_inwin | 5 | 65.000 | 0.200 | 0.200 |
| htr/error | hit | 12 | 33.000 | 0.250 | 0.250 |
| htr/error | orphan | 58 | 129.000 | 0.276 | 0.276 | 

Immediate effect of the model installed at each confirmation: raw MAE over the 200 steps after the install vs the 200 before it (ratio > 1.5 = the replacement made things worse):

Pre-confirmation trend of the RAW error (500 steps before vs the 1500 before those):

| config | label | fall | flat | rise |
|---|---|---|---|---|
| htr-mwa50/error | echo | 11 | 1 | 1 |
| htr-mwa50/error | echo_inwin | 0 | 0 | 3 |
| htr-mwa50/error | hit | 3 | 0 | 9 |
| htr-mwa50/error | orphan | 88 | 46 | 24 |
| htr-nr/error | echo | 0 | 2 | 0 |
| htr-nr/error | echo_inwin | 0 | 0 | 1 |
| htr-nr/error | hit | 3 | 0 | 12 |
| htr-nr/error | orphan | 3 | 11 | 5 |
| htr/error | echo | 5 | 1 | 1 |
| htr/error | echo_inwin | 0 | 0 | 5 |
| htr/error | hit | 3 | 0 | 9 |
| htr/error | orphan | 24 | 22 | 12 | 

Same windows on the NORMALIZED error, orphans only, cross-tabbed against the raw trend (raw flat but normalized moving = the online normalizer's statistics, not the model):

| config | pre_dir | fall | flat | rise |
|---|---|---|---|---|
| htr-mwa50/error | fall | 69 | 19 | 0 |
| htr-mwa50/error | flat | 0 | 46 | 0 |
| htr-mwa50/error | rise | 0 | 11 | 13 |
| htr-nr/error | fall | 0 | 3 | 0 |
| htr-nr/error | flat | 0 | 11 | 0 |
| htr-nr/error | rise | 0 | 4 | 1 |
| htr/error | fall | 12 | 12 | 0 |
| htr/error | flat | 0 | 22 | 0 |
| htr/error | rise | 0 | 2 | 10 | 

Orphans that are flat at the short scale, re-examined at ADWIN's scale (last 3000 vs the 6000 before): raw trend vs normalized trend (thresholds 5% raw, 0.02 normalized):

| config | raw_long | fall | flat | rise |
|---|---|---|---|---|
| htr-mwa50/error | fall | 9 | 8 | 0 |
| htr-mwa50/error | flat | 1 | 18 | 0 |
| htr-mwa50/error | rise | 0 | 4 | 6 |
| htr-nr/error | fall | 0 | 4 | 0 |
| htr-nr/error | flat | 0 | 6 | 0 |
| htr-nr/error | rise | 0 | 1 | 0 |
| htr/error | fall | 2 | 4 | 0 |
| htr/error | flat | 0 | 12 | 0 |
| htr/error | rise | 0 | 2 | 2 | 
(n=79 of 79 flat/flat orphans had 9000 steps of history)

| config | label | n | median_ratio | worse_x1_5 | better_x0_67 |
|---|---|---|---|---|---|
| htr-mwa50/error | echo | 13 | 1.491 | 0.462 | 0.000 |
| htr-mwa50/error | echo_inwin | 3 | 1.568 | 0.667 | 0.000 |
| htr-mwa50/error | hit | 12 | 1.044 | 0.167 | 0.000 |
| htr-mwa50/error | orphan | 158 | 1.452 | 0.354 | 0.000 |
| htr-nr/error | echo | 2 | 0.983 | 0.000 | 0.000 |
| htr-nr/error | echo_inwin | 1 | 1.281 | 0.000 | 0.000 |
| htr-nr/error | hit | 15 | 0.934 | 0.133 | 0.000 |
| htr-nr/error | orphan | 19 | 1.061 | 0.053 | 0.000 |
| htr/error | echo | 7 | 1.230 | 0.143 | 0.000 |
| htr/error | echo_inwin | 5 | 1.068 | 0.400 | 0.000 |
| htr/error | hit | 12 | 1.052 | 0.083 | 0.000 |
| htr/error | orphan | 58 | 1.154 | 0.259 | 0.034 | 

## 1. Recall and FP structure (per config x group)

| group | config | streams | n_gt | tp | recall | fp | fp_per_stream | echo | orphan | echo_inwin | dropped | swaps | mae | cd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| joe-sudden | htr-mwa50/error | 6 | 18 | 12 | 0.667 | 171 | 28.500 | 13 | 158 | 3 | 95 | 1316 | 2.106 | 0.000 |
| joe-sudden | htr-nr/error | 6 | 18 | 15 | 0.833 | 21 | 3.500 | 2 | 19 | 1 | 0 | 219 | 1.881 | 5.550 |
| joe-sudden | htr/error | 6 | 18 | 12 | 0.667 | 65 | 10.833 | 7 | 58 | 5 | 0 | 298 | 1.921 | 0.000 | 

## 2. Error direction at the detection, by label (pooled over configs)

| config | label | fall | flat | rise |
|---|---|---|---|---|
| htr-mwa50/error | echo | 2 | 1 | 10 |
| htr-mwa50/error | echo_inwin | 1 | 1 | 1 |
| htr-mwa50/error | hit | 1 | 5 | 6 |
| htr-mwa50/error | orphan | 13 | 62 | 83 |
| htr-nr/error | echo | 0 | 0 | 2 |
| htr-nr/error | echo_inwin | 1 | 0 | 0 |
| htr-nr/error | hit | 12 | 0 | 3 |
| htr-nr/error | orphan | 1 | 14 | 4 |
| htr/error | echo | 1 | 3 | 3 |
| htr/error | echo_inwin | 3 | 1 | 1 |
| htr/error | hit | 0 | 7 | 5 |
| htr/error | orphan | 5 | 25 | 28 | 

Mean normalized delta / raw relative change by label:

| config | label | n | norm_delta | raw_rel | confirm_age |
|---|---|---|---|---|---|
| htr-mwa50/error | echo | 13 | 0.029 | 0.174 | 49.000 |
| htr-mwa50/error | echo_inwin | 3 | -0.011 | -0.021 | 49.000 |
| htr-mwa50/error | hit | 12 | 0.050 | 0.263 | 49.000 |
| htr-mwa50/error | orphan | 158 | 0.026 | 0.147 | 64.000 |
| htr-nr/error | echo | 2 | 0.043 | 0.014 | 2080.000 |
| htr-nr/error | echo_inwin | 1 | -0.034 | -0.094 | 32.000 |
| htr-nr/error | hit | 15 | -0.050 | 0.214 | 32.000 |
| htr-nr/error | orphan | 19 | 0.007 | 0.094 | 704.000 |
| htr/error | echo | 7 | 0.008 | 0.050 | 64.000 |
| htr/error | echo_inwin | 5 | -0.023 | -0.063 | 64.000 |
| htr/error | hit | 12 | 0.060 | 0.321 | 32.000 |
| htr/error | orphan | 58 | 0.015 | 0.091 | 128.000 | 

## 3. Leader-swap coincidence (detection <= 600 steps after a swap), by label

| config | label | n | within600 | chance |
|---|---|---|---|---|
| htr-mwa50/error | echo | 13 | 0.308 | 0.182 |
| htr-mwa50/error | echo_inwin | 3 | 0.667 | 0.182 |
| htr-mwa50/error | hit | 12 | 0.083 | 0.182 |
| htr-mwa50/error | orphan | 158 | 0.500 | 0.182 |
| htr-nr/error | echo | 2 | 0.000 | 0.042 |
| htr-nr/error | echo_inwin | 1 | 1.000 | 0.042 |
| htr-nr/error | hit | 15 | 0.000 | 0.042 |
| htr-nr/error | orphan | 19 | 0.000 | 0.042 |
| htr/error | echo | 7 | 0.286 | 0.051 |
| htr/error | echo_inwin | 5 | 0.400 | 0.051 |
| htr/error | hit | 12 | 0.167 | 0.051 |
| htr/error | orphan | 58 | 0.224 | 0.051 | 
(pooled chance baseline 0.091)

## 4. Normalizer discordance by label

| label |  | fake_fall | fake_rise | masked_fall |
|---|---|---|---|---|
| echo | 21 | 0 | 1 | 0 |
| echo_inwin | 9 | 0 | 0 | 0 |
| hit | 23 | 9 | 3 | 4 |
| orphan | 219 | 2 | 3 | 11 | 

## 5. Gap distributions

- echo: n=22, steps after the previous ground-truth drift: p25=1796 median=2077 p75=2479 max=2918
- echo_inwin: n=9, steps after the previous ground-truth drift: p25=505 median=701 p75=890 max=954
- orphan: n=223, steps after the previous ground-truth drift: p25=6759 median=12035 p75=21523 max=56867
- orphans BEFORE the first ground-truth drift (first-concept learning ramp): 12 of 235 orphans

## 6. Per-segment error level (normalized vs raw), first -> last stable segment

| dataset | config | segments | norm_first | norm_last | raw_first | raw_last | norm_change | raw_rel_change |
|---|---|---|---|---|---|---|---|---|
| sudden/high/recurring_sudden_friedman_100k_g00.csv | htr-mwa50/error | 4 | 0.483 | 0.542 | 1.743 | 2.320 | 0.059 | 0.331 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | htr-nr/error | 4 | 0.484 | 0.488 | 1.743 | 2.206 | 0.004 | 0.265 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | htr/error | 4 | 0.483 | 0.546 | 1.743 | 2.257 | 0.063 | 0.295 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | htr-mwa50/error | 4 | 0.479 | 0.466 | 1.774 | 2.075 | -0.013 | 0.169 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | htr-nr/error | 4 | 0.479 | 0.485 | 1.774 | 2.064 | 0.007 | 0.163 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | htr/error | 4 | 0.479 | 0.470 | 1.774 | 1.927 | -0.009 | 0.086 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | htr-mwa50/error | 4 | 0.477 | 0.490 | 1.803 | 1.672 | 0.014 | -0.073 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | htr-nr/error | 4 | 0.477 | 0.489 | 1.803 | 1.634 | 0.012 | -0.094 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | htr/error | 4 | 0.477 | 0.492 | 1.803 | 1.686 | 0.015 | -0.065 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | htr-mwa50/error | 4 | 0.481 | 0.460 | 1.777 | 1.854 | -0.021 | 0.043 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | htr-nr/error | 4 | 0.482 | 0.494 | 1.777 | 1.882 | 0.012 | 0.059 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | htr/error | 4 | 0.481 | 0.498 | 1.777 | 1.924 | 0.017 | 0.083 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | htr-mwa50/error | 4 | 0.482 | 0.508 | 1.788 | 2.089 | 0.027 | 0.168 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | htr-nr/error | 4 | 0.482 | 0.494 | 1.788 | 1.904 | 0.012 | 0.065 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | htr/error | 4 | 0.482 | 0.488 | 1.788 | 1.921 | 0.006 | 0.075 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | htr-mwa50/error | 4 | 0.478 | 0.543 | 1.801 | 2.790 | 0.065 | 0.549 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | htr-nr/error | 4 | 0.478 | 0.492 | 1.801 | 1.564 | 0.014 | -0.132 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | htr/error | 4 | 0.478 | 0.470 | 1.801 | 1.629 | -0.008 | -0.096 | 

