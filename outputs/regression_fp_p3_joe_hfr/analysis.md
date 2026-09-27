C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\computation\expressions.py:21: UserWarning: Pandas requires version '2.8.4' or newer of 'numexpr' (version '2.8.3' currently installed).
  from pandas.core.computation.check import NUMEXPR_INSTALLED
C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\arrays\masked.py:61: UserWarning: Pandas requires version '1.3.6' or newer of 'bottleneck' (version '1.3.5' currently installed).
  from pandas.core import (
## 0. FP sub-labels (post hoc) and the expert the preceding hit installed

| config | label | (none) | late | stale_warning |
|---|---|---|---|---|
| hfr-mwa50/error | echo | 1 | 0 | 0 |
| hfr-mwa50/error | orphan | 17 | 4 | 1 |
| hfr-nr/error | orphan | 2 | 6 | 0 |
| hfr/error | echo | 1 | 0 | 0 |
| hfr/error | orphan | 14 | 3 | 3 | 

Reuse decision at each confirmation: length of the warning buffer it was made on (buffer = confirm_age + 1 instances; the reused best slot is chosen by its score on it):

| config | label | n | buf_median | buf_is_1 | buf_le_10 |
|---|---|---|---|---|---|
| hfr-mwa50/error | echo | 1 | 961.000 | 0.000 | 0.000 |
| hfr-mwa50/error | hit | 10 | 57.500 | 0.000 | 0.000 |
| hfr-mwa50/error | orphan | 22 | 753.000 | 0.000 | 0.000 |
| hfr-nr/error | hit | 8 | 1.000 | 0.625 | 0.625 |
| hfr-nr/error | orphan | 8 | 97.000 | 0.125 | 0.125 |
| hfr/error | echo | 1 | 865.000 | 0.000 | 0.000 |
| hfr/error | hit | 10 | 33.000 | 0.300 | 0.300 |
| hfr/error | orphan | 20 | 529.000 | 0.200 | 0.200 | 

Immediate effect of the model installed at each confirmation: raw MAE over the 200 steps after the install vs the 200 before it (ratio > 1.5 = the replacement made things worse):

Pre-confirmation trend of the RAW error (500 steps before vs the 1500 before those):

| config | label | fall | flat | rise |
|---|---|---|---|---|
| hfr-mwa50/error | echo | 0 | 1 | 0 |
| hfr-mwa50/error | hit | 2 | 0 | 8 |
| hfr-mwa50/error | orphan | 5 | 16 | 1 |
| hfr-nr/error | hit | 0 | 0 | 8 |
| hfr-nr/error | orphan | 4 | 3 | 1 |
| hfr/error | echo | 0 | 1 | 0 |
| hfr/error | hit | 3 | 0 | 7 |
| hfr/error | orphan | 5 | 13 | 2 | 

Same windows on the NORMALIZED error, orphans only, cross-tabbed against the raw trend (raw flat but normalized moving = the online normalizer's statistics, not the model):

| config | pre_dir | fall | flat | rise |
|---|---|---|---|---|
| hfr-mwa50/error | fall | 3 | 2 | 0 |
| hfr-mwa50/error | flat | 0 | 16 | 0 |
| hfr-mwa50/error | rise | 0 | 0 | 1 |
| hfr-nr/error | fall | 3 | 1 | 0 |
| hfr-nr/error | flat | 0 | 3 | 0 |
| hfr-nr/error | rise | 0 | 0 | 1 |
| hfr/error | fall | 3 | 2 | 0 |
| hfr/error | flat | 0 | 13 | 0 |
| hfr/error | rise | 0 | 0 | 2 | 

Orphans that are flat at the short scale, re-examined at ADWIN's scale (last 3000 vs the 6000 before): raw trend vs normalized trend (thresholds 5% raw, 0.02 normalized):

| config | raw_long | fall | flat | rise |
|---|---|---|---|---|
| hfr-mwa50/error | flat | 1 | 13 | 0 |
| hfr-mwa50/error | rise | 0 | 1 | 1 |
| hfr-nr/error | fall | 1 | 0 | 0 |
| hfr-nr/error | flat | 0 | 1 | 0 |
| hfr-nr/error | rise | 0 | 1 | 0 |
| hfr/error | fall | 1 | 0 | 0 |
| hfr/error | flat | 1 | 9 | 0 |
| hfr/error | rise | 0 | 1 | 1 | 
(n=32 of 32 flat/flat orphans had 9000 steps of history)

| config | label | n | median_ratio | worse_x1_5 | better_x0_67 |
|---|---|---|---|---|---|
| hfr-mwa50/error | echo | 1 | 1.014 | 0.000 | 0.000 |
| hfr-mwa50/error | hit | 10 | 0.907 | 0.000 | 0.100 |
| hfr-mwa50/error | orphan | 22 | 1.008 | 0.000 | 0.000 |
| hfr-nr/error | hit | 8 | 0.910 | 0.000 | 0.000 |
| hfr-nr/error | orphan | 8 | 1.001 | 0.000 | 0.000 |
| hfr/error | echo | 1 | 1.027 | 0.000 | 0.000 |
| hfr/error | hit | 10 | 0.960 | 0.000 | 0.000 |
| hfr/error | orphan | 20 | 1.060 | 0.000 | 0.000 | 

## 1. Recall and FP structure (per config x group)

| group | config | streams | n_gt | tp | recall | fp | fp_per_stream | echo | orphan | echo_inwin | dropped | swaps | mae | cd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| joe-sudden | hfr-mwa50/error | 6 | 18 | 10 | 0.556 | 23 | 3.833 | 1 | 22 | 0 | 10 | 502 | 3.460 | 5.550 |
| joe-sudden | hfr-nr/error | 6 | 18 | 8 | 0.444 | 8 | 1.333 | 0 | 8 | 0 | 0 | 258 | 3.451 | 16.650 |
| joe-sudden | hfr/error | 6 | 18 | 10 | 0.556 | 21 | 3.500 | 1 | 20 | 0 | 0 | 401 | 3.458 | 0.000 | 

## 2. Error direction at the detection, by label (pooled over configs)

| config | label | fall | flat | rise |
|---|---|---|---|---|
| hfr-mwa50/error | echo | 0 | 1 | 0 |
| hfr-mwa50/error | hit | 4 | 2 | 4 |
| hfr-mwa50/error | orphan | 2 | 15 | 5 |
| hfr-nr/error | hit | 8 | 0 | 0 |
| hfr-nr/error | orphan | 2 | 1 | 5 |
| hfr/error | echo | 0 | 1 | 0 |
| hfr/error | hit | 3 | 4 | 3 |
| hfr/error | orphan | 1 | 14 | 5 | 

Mean normalized delta / raw relative change by label:

| config | label | n | norm_delta | raw_rel | confirm_age |
|---|---|---|---|---|---|
| hfr-mwa50/error | echo | 1 | -0.006 | 0.033 | 960.000 |
| hfr-mwa50/error | hit | 10 | -0.009 | -0.024 | 56.500 |
| hfr-mwa50/error | orphan | 22 | 0.005 | 0.026 | 752.000 |
| hfr-nr/error | hit | 8 | -0.114 | -0.017 | 0.000 |
| hfr-nr/error | orphan | 8 | 0.024 | -0.011 | 96.000 |
| hfr/error | echo | 1 | -0.011 | 0.017 | 864.000 |
| hfr/error | hit | 10 | 0.001 | 0.026 | 32.000 |
| hfr/error | orphan | 20 | 0.008 | 0.041 | 528.000 | 

## 3. Leader-swap coincidence (detection <= 600 steps after a swap), by label

| config | label | n | within600 | chance |
|---|---|---|---|---|
| hfr-mwa50/error | echo | 1 | 0.000 | 0.065 |
| hfr-mwa50/error | hit | 10 | 0.000 | 0.065 |
| hfr-mwa50/error | orphan | 22 | 0.045 | 0.065 |
| hfr-nr/error | hit | 8 | 0.000 | 0.031 |
| hfr-nr/error | orphan | 8 | 0.000 | 0.031 |
| hfr/error | echo | 1 | 0.000 | 0.048 |
| hfr/error | hit | 10 | 0.000 | 0.048 |
| hfr/error | orphan | 20 | 0.050 | 0.048 | 
(pooled chance baseline 0.048)

## 4. Normalizer discordance by label

| label |  | fake_fall | fake_rise |
|---|---|---|---|
| echo | 2 | 0 | 0 |
| hit | 23 | 5 | 0 |
| orphan | 42 | 3 | 5 | 

## 5. Gap distributions

- echo: n=2, steps after the previous ground-truth drift: p25=2727 median=2727 p75=2727 max=2727
- orphan: n=50, steps after the previous ground-truth drift: p25=2597 median=10807 p75=18708 max=50531
- orphans BEFORE the first ground-truth drift (first-concept learning ramp): 0 of 50 orphans

## 6. Per-segment error level (normalized vs raw), first -> last stable segment

| dataset | config | segments | norm_first | norm_last | raw_first | raw_last | norm_change | raw_rel_change |
|---|---|---|---|---|---|---|---|---|
| sudden/high/recurring_sudden_friedman_100k_g00.csv | hfr-mwa50/error | 4 | 0.496 | 0.547 | 2.913 | 3.874 | 0.051 | 0.330 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | hfr-nr/error | 4 | 0.496 | 0.497 | 2.913 | 3.871 | 0.001 | 0.329 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | hfr/error | 4 | 0.496 | 0.547 | 2.913 | 3.876 | 0.051 | 0.331 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | hfr-mwa50/error | 4 | 0.496 | 0.558 | 2.927 | 5.092 | 0.062 | 0.740 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | hfr-nr/error | 4 | 0.496 | 0.499 | 2.927 | 5.042 | 0.004 | 0.723 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | hfr/error | 4 | 0.496 | 0.557 | 2.927 | 5.060 | 0.061 | 0.729 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | hfr-mwa50/error | 4 | 0.498 | 0.472 | 2.954 | 2.574 | -0.026 | -0.129 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | hfr-nr/error | 4 | 0.498 | 0.497 | 2.954 | 2.570 | -0.000 | -0.130 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | hfr/error | 4 | 0.498 | 0.472 | 2.954 | 2.574 | -0.026 | -0.129 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | hfr-mwa50/error | 4 | 0.498 | 0.490 | 2.896 | 3.226 | -0.008 | 0.114 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | hfr-nr/error | 4 | 0.498 | 0.492 | 2.896 | 3.228 | -0.005 | 0.115 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | hfr/error | 4 | 0.498 | 0.489 | 2.896 | 3.224 | -0.008 | 0.113 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | hfr-mwa50/error | 4 | 0.495 | 0.519 | 2.917 | 3.800 | 0.024 | 0.303 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | hfr-nr/error | 4 | 0.495 | 0.497 | 2.917 | 3.771 | 0.001 | 0.293 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | hfr/error | 4 | 0.495 | 0.519 | 2.917 | 3.793 | 0.024 | 0.300 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | hfr-mwa50/error | 4 | 0.497 | 0.485 | 2.917 | 3.306 | -0.012 | 0.133 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | hfr-nr/error | 4 | 0.497 | 0.497 | 2.917 | 3.313 | 0.001 | 0.136 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | hfr/error | 4 | 0.497 | 0.485 | 2.917 | 3.312 | -0.011 | 0.135 | 

