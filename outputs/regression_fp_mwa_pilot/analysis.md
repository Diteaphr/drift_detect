C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\computation\expressions.py:21: UserWarning: Pandas requires version '2.8.4' or newer of 'numexpr' (version '2.8.3' currently installed).
  from pandas.core.computation.check import NUMEXPR_INSTALLED
C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\arrays\masked.py:61: UserWarning: Pandas requires version '1.3.6' or newer of 'bottleneck' (version '1.3.5' currently installed).
  from pandas.core import (
## 0. FP sub-labels (post hoc) and the expert the preceding hit installed

| config | label | (none) | late | pre_drift | stale_warning |
|---|---|---|---|---|---|
| hfr-mwa50/error | echo | 4 | 0 | 0 | 0 |
| hfr/error | echo | 3 | 0 | 0 | 0 |
| hfr/error | orphan | 2 | 2 | 0 | 0 |
| htr-mwa50/error | echo | 10 | 0 | 0 | 0 |
| htr-mwa50/error | orphan | 9 | 1 | 1 | 1 |
| htr/error | echo | 12 | 0 | 0 | 0 |
| htr/error | orphan | 7 | 0 | 1 | 0 | 

Reuse decision at each confirmation: length of the warning buffer it was made on (buffer = confirm_age + 1 instances; the reused best slot is chosen by its score on it):

| config | label | n | buf_median | buf_is_1 | buf_le_10 |
|---|---|---|---|---|---|
| hfr-mwa50/error | echo | 4 | 577.000 | 0.000 | 0.000 |
| hfr-mwa50/error | echo_inwin | 8 | 57.500 | 0.000 | 0.000 |
| hfr-mwa50/error | hit | 10 | 50.000 | 0.000 | 0.000 |
| hfr/error | echo | 3 | 577.000 | 0.000 | 0.000 |
| hfr/error | echo_inwin | 6 | 49.000 | 0.500 | 0.500 |
| hfr/error | hit | 9 | 1.000 | 0.556 | 0.556 |
| hfr/error | orphan | 4 | 1.000 | 0.750 | 0.750 |
| htr-mwa50/error | echo | 10 | 50.000 | 0.000 | 0.000 |
| htr-mwa50/error | echo_inwin | 13 | 50.000 | 0.000 | 0.000 |
| htr-mwa50/error | hit | 9 | 50.000 | 0.000 | 0.000 |
| htr-mwa50/error | orphan | 12 | 65.000 | 0.000 | 0.000 |
| htr/error | echo | 12 | 17.000 | 0.500 | 0.500 |
| htr/error | echo_inwin | 10 | 33.000 | 0.400 | 0.400 |
| htr/error | hit | 10 | 1.000 | 0.800 | 0.800 |
| htr/error | orphan | 8 | 49.000 | 0.375 | 0.375 | 

Immediate effect of the model installed at each confirmation: raw MAE over the 200 steps after the install vs the 200 before it (ratio > 1.5 = the replacement made things worse):

Pre-confirmation trend of the RAW error (500 steps before vs the 1500 before those):

| config | label | fall | flat | rise |
|---|---|---|---|---|
| hfr-mwa50/error | echo | 3 | 0 | 1 |
| hfr-mwa50/error | echo_inwin | 0 | 0 | 8 |
| hfr-mwa50/error | hit | 0 | 0 | 10 |
| hfr/error | echo | 2 | 1 | 0 |
| hfr/error | echo_inwin | 2 | 0 | 4 |
| hfr/error | hit | 0 | 0 | 9 |
| hfr/error | orphan | 3 | 1 | 0 |
| htr-mwa50/error | echo | 8 | 0 | 2 |
| htr-mwa50/error | echo_inwin | 2 | 0 | 11 |
| htr-mwa50/error | hit | 0 | 0 | 9 |
| htr-mwa50/error | orphan | 8 | 0 | 4 |
| htr/error | echo | 8 | 1 | 3 |
| htr/error | echo_inwin | 0 | 0 | 10 |
| htr/error | hit | 0 | 0 | 10 |
| htr/error | orphan | 7 | 0 | 1 | 

Same windows on the NORMALIZED error, orphans only, cross-tabbed against the raw trend (raw flat but normalized moving = the online normalizer's statistics, not the model):

| config | pre_dir | fall | flat | rise |
|---|---|---|---|---|
| hfr/error | fall | 2 | 1 | 0 |
| hfr/error | flat | 0 | 1 | 0 |
| htr-mwa50/error | fall | 5 | 3 | 0 |
| htr-mwa50/error | rise | 0 | 0 | 4 |
| htr/error | fall | 6 | 1 | 0 |
| htr/error | rise | 0 | 0 | 1 | 

Orphans that are flat at the short scale, re-examined at ADWIN's scale (last 3000 vs the 6000 before): raw trend vs normalized trend (thresholds 5% raw, 0.02 normalized):

| config | raw_long | flat |
|---|---|---|
| hfr/error | flat | 1 | 
(n=1 of 1 flat/flat orphans had 9000 steps of history)

| config | label | n | median_ratio | worse_x1_5 | better_x0_67 |
|---|---|---|---|---|---|
| hfr-mwa50/error | echo | 4 | 1.344 | 0.250 | 0.000 |
| hfr-mwa50/error | echo_inwin | 8 | 0.940 | 0.000 | 0.125 |
| hfr-mwa50/error | hit | 10 | 0.484 | 0.000 | 0.800 |
| hfr/error | echo | 3 | 1.133 | 0.000 | 0.000 |
| hfr/error | echo_inwin | 6 | 0.994 | 0.000 | 0.000 |
| hfr/error | hit | 9 | 0.624 | 0.000 | 0.556 |
| hfr/error | orphan | 4 | 0.943 | 0.000 | 0.000 |
| htr-mwa50/error | echo | 10 | 1.028 | 0.000 | 0.000 |
| htr-mwa50/error | echo_inwin | 13 | 1.158 | 0.231 | 0.154 |
| htr-mwa50/error | hit | 9 | 0.802 | 0.000 | 0.333 |
| htr-mwa50/error | orphan | 12 | 0.951 | 0.167 | 0.083 |
| htr/error | echo | 12 | 0.943 | 0.083 | 0.167 |
| htr/error | echo_inwin | 10 | 1.142 | 0.400 | 0.100 |
| htr/error | hit | 10 | 1.249 | 0.400 | 0.200 |
| htr/error | orphan | 8 | 0.991 | 0.125 | 0.000 | 

## 1. Recall and FP structure (per config x group)

| group | config | streams | n_gt | tp | recall | fp | fp_per_stream | echo | orphan | echo_inwin | dropped | swaps | mae | cd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic | hfr-mwa50/error | 3 | 10 | 10 | 1.000 | 4 | 1.333 | 4 | 0 | 8 | 14 | 46 | 2.813 | 63.333 |
| synthetic | hfr/error | 3 | 10 | 9 | 0.900 | 7 | 2.333 | 3 | 4 | 6 | 0 | 27 | 2.889 | 17.767 |
| synthetic | htr-mwa50/error | 3 | 10 | 9 | 0.900 | 22 | 7.333 | 10 | 12 | 13 | 32 | 63 | 2.774 | 0.000 |
| synthetic | htr/error | 3 | 10 | 10 | 1.000 | 20 | 6.667 | 12 | 8 | 10 | 0 | 68 | 2.671 | 0.000 | 

## 2. Error direction at the detection, by label (pooled over configs)

| config | label | fall | flat | rise |
|---|---|---|---|---|
| hfr-mwa50/error | echo | 0 | 2 | 2 |
| hfr-mwa50/error | echo_inwin | 8 | 0 | 0 |
| hfr-mwa50/error | hit | 5 | 3 | 2 |
| hfr/error | echo | 0 | 2 | 1 |
| hfr/error | echo_inwin | 5 | 0 | 1 |
| hfr/error | hit | 3 | 4 | 2 |
| hfr/error | orphan | 2 | 2 | 0 |
| htr-mwa50/error | echo | 5 | 4 | 1 |
| htr-mwa50/error | echo_inwin | 9 | 4 | 0 |
| htr-mwa50/error | hit | 2 | 0 | 7 |
| htr-mwa50/error | orphan | 3 | 7 | 2 |
| htr/error | echo | 7 | 2 | 3 |
| htr/error | echo_inwin | 7 | 2 | 1 |
| htr/error | hit | 2 | 0 | 8 |
| htr/error | orphan | 2 | 5 | 1 | 

Mean normalized delta / raw relative change by label:

| config | label | n | norm_delta | raw_rel | confirm_age |
|---|---|---|---|---|---|
| hfr-mwa50/error | echo | 4 | 0.091 | 0.811 | 576.000 |
| hfr-mwa50/error | echo_inwin | 8 | -0.096 | -0.396 | 56.500 |
| hfr-mwa50/error | hit | 10 | -0.040 | -0.157 | 49.000 |
| hfr/error | echo | 3 | 0.008 | 0.039 | 576.000 |
| hfr/error | echo_inwin | 6 | -0.033 | -0.098 | 48.000 |
| hfr/error | hit | 9 | 0.000 | -0.057 | 0.000 |
| hfr/error | orphan | 4 | -0.046 | -0.189 | 0.000 |
| htr-mwa50/error | echo | 10 | -0.029 | -0.148 | 49.000 |
| htr-mwa50/error | echo_inwin | 13 | -0.051 | -0.244 | 49.000 |
| htr-mwa50/error | hit | 9 | 0.079 | 0.507 | 49.000 |
| htr-mwa50/error | orphan | 12 | 0.010 | 0.287 | 64.000 |
| htr/error | echo | 12 | -0.028 | -0.044 | 16.000 |
| htr/error | echo_inwin | 10 | -0.055 | -0.198 | 32.000 |
| htr/error | hit | 10 | 0.094 | 0.636 | 0.000 |
| htr/error | orphan | 8 | -0.005 | -0.067 | 48.000 | 

## 3. Leader-swap coincidence (detection <= 600 steps after a swap), by label

| config | label | n | within600 | chance |
|---|---|---|---|---|
| hfr-mwa50/error | echo | 4 | 0.000 | 0.172 |
| hfr-mwa50/error | echo_inwin | 8 | 1.000 | 0.172 |
| hfr-mwa50/error | hit | 10 | 0.100 | 0.172 |
| hfr/error | echo | 3 | 0.000 | 0.154 |
| hfr/error | echo_inwin | 6 | 0.833 | 0.154 |
| hfr/error | hit | 9 | 0.000 | 0.154 |
| hfr/error | orphan | 4 | 0.250 | 0.154 |
| htr-mwa50/error | echo | 10 | 0.300 | 0.252 |
| htr-mwa50/error | echo_inwin | 13 | 0.769 | 0.252 |
| htr-mwa50/error | hit | 9 | 0.000 | 0.252 |
| htr-mwa50/error | orphan | 12 | 0.000 | 0.252 |
| htr/error | echo | 12 | 0.500 | 0.203 |
| htr/error | echo_inwin | 10 | 0.800 | 0.203 |
| htr/error | hit | 10 | 0.000 | 0.203 |
| htr/error | orphan | 8 | 0.000 | 0.203 | 
(pooled chance baseline 0.196)

## 4. Normalizer discordance by label

| label |  | fake_fall | masked_fall |
|---|---|---|---|
| echo | 23 | 0 | 6 |
| echo_inwin | 35 | 1 | 1 |
| hit | 32 | 0 | 6 |
| orphan | 15 | 0 | 9 | 

## 5. Gap distributions

- echo: n=29, steps after the previous ground-truth drift: p25=1346 median=1647 p75=2306 max=2871
- echo_inwin: n=37, steps after the previous ground-truth drift: p25=418 median=696 p75=817 max=1425
- orphan: n=16, steps after the previous ground-truth drift: p25=3218 median=3443 p75=4409 max=4823
- orphans BEFORE the first ground-truth drift (first-concept learning ramp): 8 of 24 orphans

## 6. Per-segment error level (normalized vs raw), first -> last stable segment

| dataset | config | segments | norm_first | norm_last | raw_first | raw_last | norm_change | raw_rel_change |
|---|---|---|---|---|---|---|---|---|
| reg_gradual_20k.csv | hfr-mwa50/error | 3 | 0.491 | 0.467 | 2.351 | 2.317 | -0.024 | -0.014 |
| reg_gradual_20k.csv | hfr/error | 3 | 0.491 | 0.465 | 2.351 | 2.352 | -0.026 | 0.001 |
| reg_gradual_20k.csv | htr-mwa50/error | 3 | 0.447 | 0.471 | 2.175 | 2.495 | 0.024 | 0.147 |
| reg_gradual_20k.csv | htr/error | 3 | 0.447 | 0.459 | 2.174 | 2.021 | 0.011 | -0.070 |
| reg_recurring_20k.csv | hfr-mwa50/error | 6 | 0.488 | 0.454 | 2.365 | 2.296 | -0.034 | -0.029 |
| reg_recurring_20k.csv | hfr/error | 6 | 0.488 | 0.456 | 2.365 | 2.465 | -0.032 | 0.042 |
| reg_recurring_20k.csv | htr-mwa50/error | 6 | 0.460 | 0.433 | 2.358 | 1.733 | -0.027 | -0.265 |
| reg_recurring_20k.csv | htr/error | 6 | 0.460 | 0.434 | 2.358 | 1.733 | -0.026 | -0.265 |
| reg_sudden_20k.csv | hfr-mwa50/error | 4 | 0.488 | 0.468 | 2.271 | 2.262 | -0.020 | -0.004 |
| reg_sudden_20k.csv | hfr/error | 4 | 0.488 | 0.466 | 2.271 | 2.260 | -0.022 | -0.005 |
| reg_sudden_20k.csv | htr-mwa50/error | 4 | 0.444 | 0.444 | 1.781 | 1.642 | 0.001 | -0.078 |
| reg_sudden_20k.csv | htr/error | 4 | 0.443 | 0.458 | 1.777 | 2.003 | 0.014 | 0.127 | 

## 7. Counterfactual replay: drift ADWIN on normalized err vs raw residual at a FIXED scale

Replay fidelity = replay fires on `err` vs the pipeline's own drift-arm fires (is_drift rows). Fixed scale = raw / (mean + 3 sd of the whole stream's raw residual), clipped to [0, 1].

| dataset | config | pipe_fires | replay_norm | norm_tp | norm_fp | replay_raw_fixed | raw_tp | raw_fp |
|---|---|---|---|---|---|---|---|---|
| reg_gradual_20k.csv | hfr-mwa50/error | 5 | 5 | 2 | 1 | 6 | 2 | 2 |
| reg_gradual_20k.csv | hfr/error | 7 | 7 | 2 | 2 | 7 | 2 | 2 |
| reg_gradual_20k.csv | htr-mwa50/error | 11 | 11 | 2 | 6 | 13 | 2 | 7 |
| reg_gradual_20k.csv | htr/error | 8 | 8 | 2 | 4 | 13 | 2 | 7 |
| reg_recurring_20k.csv | hfr-mwa50/error | 11 | 11 | 5 | 2 | 14 | 5 | 3 |
| reg_recurring_20k.csv | hfr/error | 9 | 9 | 5 | 3 | 11 | 5 | 3 |
| reg_recurring_20k.csv | htr-mwa50/error | 16 | 16 | 5 | 6 | 18 | 5 | 8 |
| reg_recurring_20k.csv | htr/error | 17 | 17 | 5 | 6 | 20 | 5 | 7 |
| reg_sudden_20k.csv | hfr-mwa50/error | 6 | 6 | 3 | 0 | 8 | 3 | 1 |
| reg_sudden_20k.csv | hfr/error | 6 | 6 | 3 | 2 | 8 | 3 | 3 |
| reg_sudden_20k.csv | htr-mwa50/error | 17 | 17 | 3 | 10 | 19 | 3 | 11 |
| reg_sudden_20k.csv | htr/error | 15 | 15 | 3 | 10 | 16 | 3 | 11 | 

Totals:

| config | pipe_fires | replay_norm | norm_tp | norm_fp | replay_raw_fixed | raw_tp | raw_fp |
|---|---|---|---|---|---|---|---|
| hfr-mwa50/error | 22 | 22 | 10 | 3 | 28 | 10 | 6 |
| hfr/error | 22 | 22 | 10 | 7 | 26 | 10 | 8 |
| htr-mwa50/error | 44 | 44 | 10 | 22 | 50 | 10 | 26 |
| htr/error | 40 | 40 | 10 | 20 | 49 | 10 | 25 |
