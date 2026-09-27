C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\computation\expressions.py:21: UserWarning: Pandas requires version '2.8.4' or newer of 'numexpr' (version '2.8.3' currently installed).
  from pandas.core.computation.check import NUMEXPR_INSTALLED
C:\Users\chenp\anaconda3\lib\site-packages\pandas\core\arrays\masked.py:61: UserWarning: Pandas requires version '1.3.6' or newer of 'bottleneck' (version '1.3.5' currently installed).
  from pandas.core import (
## 0. FP sub-labels (post hoc) and the expert the preceding hit installed

| config | label | (none) | late | pre_drift |
|---|---|---|---|---|
| hfr-all/error | echo | 5 | 0 | 1 |
| hfr-all/error | orphan | 5 | 0 | 0 |
| hfr/error | echo | 3 | 0 | 0 |
| hfr/error | orphan | 2 | 2 | 0 | 

Reuse decision at each confirmation: length of the warning buffer it was made on (buffer = confirm_age + 1 instances; the reused best slot is chosen by its score on it):

| config | label | n | buf_median | buf_is_1 | buf_le_10 |
|---|---|---|---|---|---|
| hfr-all/error | echo | 6 | 81.000 | 0.167 | 0.167 |
| hfr-all/error | echo_inwin | 9 | 33.000 | 0.444 | 0.444 |
| hfr-all/error | hit | 10 | 1.000 | 0.700 | 0.700 |
| hfr-all/error | orphan | 5 | 97.000 | 0.400 | 0.400 |
| hfr/error | echo | 3 | 577.000 | 0.000 | 0.000 |
| hfr/error | echo_inwin | 6 | 49.000 | 0.500 | 0.500 |
| hfr/error | hit | 9 | 1.000 | 0.556 | 0.556 |
| hfr/error | orphan | 4 | 1.000 | 0.750 | 0.750 | 

Immediate effect of the model installed at each confirmation: raw MAE over the 200 steps after the install vs the 200 before it (ratio > 1.5 = the replacement made things worse):

Pre-confirmation trend of the RAW error (500 steps before vs the 1500 before those):

| config | label | fall | flat | rise |
|---|---|---|---|---|
| hfr-all/error | echo | 6 | 0 | 0 |
| hfr-all/error | echo_inwin | 1 | 0 | 8 |
| hfr-all/error | hit | 0 | 0 | 10 |
| hfr-all/error | orphan | 4 | 0 | 1 |
| hfr/error | echo | 2 | 1 | 0 |
| hfr/error | echo_inwin | 2 | 0 | 4 |
| hfr/error | hit | 0 | 0 | 9 |
| hfr/error | orphan | 3 | 1 | 0 | 

Same windows on the NORMALIZED error, orphans only, cross-tabbed against the raw trend (raw flat but normalized moving = the online normalizer's statistics, not the model):

| config | pre_dir | fall | flat | rise |
|---|---|---|---|---|
| hfr-all/error | fall | 2 | 2 | 0 |
| hfr-all/error | rise | 0 | 0 | 1 |
| hfr/error | fall | 2 | 1 | 0 |
| hfr/error | flat | 0 | 1 | 0 | 

Orphans that are flat at the short scale, re-examined at ADWIN's scale (last 3000 vs the 6000 before): raw trend vs normalized trend (thresholds 5% raw, 0.02 normalized):

| config | raw_long | flat |
|---|---|---|
| hfr/error | flat | 1 | 
(n=1 of 1 flat/flat orphans had 9000 steps of history)

| config | label | n | median_ratio | worse_x1_5 | better_x0_67 |
|---|---|---|---|---|---|
| hfr-all/error | echo | 6 | 0.962 | 0.000 | 0.000 |
| hfr-all/error | echo_inwin | 9 | 0.912 | 0.111 | 0.222 |
| hfr-all/error | hit | 10 | 0.962 | 0.300 | 0.400 |
| hfr-all/error | orphan | 5 | 1.063 | 0.200 | 0.000 |
| hfr/error | echo | 3 | 1.133 | 0.000 | 0.000 |
| hfr/error | echo_inwin | 6 | 0.994 | 0.000 | 0.000 |
| hfr/error | hit | 9 | 0.624 | 0.000 | 0.556 |
| hfr/error | orphan | 4 | 0.943 | 0.000 | 0.000 | 

## 1. Recall and FP structure (per config x group)

| group | config | streams | n_gt | tp | recall | fp | fp_per_stream | echo | orphan | echo_inwin | dropped | swaps | mae | cd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic | hfr-all/error | 3 | 10 | 10 | 1.000 | 11 | 3.667 | 6 | 5 | 9 | 0 | 43 | 1.481 | 13.333 |
| synthetic | hfr/error | 3 | 10 | 9 | 0.900 | 7 | 2.333 | 3 | 4 | 6 | 0 | 27 | 2.889 | 17.767 | 

## 2. Error direction at the detection, by label (pooled over configs)

| config | label | fall | flat | rise |
|---|---|---|---|---|
| hfr-all/error | echo | 0 | 5 | 1 |
| hfr-all/error | echo_inwin | 8 | 1 | 0 |
| hfr-all/error | hit | 4 | 0 | 6 |
| hfr-all/error | orphan | 0 | 4 | 1 |
| hfr/error | echo | 0 | 2 | 1 |
| hfr/error | echo_inwin | 5 | 0 | 1 |
| hfr/error | hit | 3 | 4 | 2 |
| hfr/error | orphan | 2 | 2 | 0 | 

Mean normalized delta / raw relative change by label:

| config | label | n | norm_delta | raw_rel | confirm_age |
|---|---|---|---|---|---|
| hfr-all/error | echo | 6 | 0.002 | 0.083 | 80.000 |
| hfr-all/error | echo_inwin | 9 | -0.087 | -0.436 | 32.000 |
| hfr-all/error | hit | 10 | 0.054 | 0.780 | 0.000 |
| hfr-all/error | orphan | 5 | 0.061 | 1.013 | 96.000 |
| hfr/error | echo | 3 | 0.008 | 0.039 | 576.000 |
| hfr/error | echo_inwin | 6 | -0.033 | -0.098 | 48.000 |
| hfr/error | hit | 9 | 0.000 | -0.057 | 0.000 |
| hfr/error | orphan | 4 | -0.046 | -0.189 | 0.000 | 

## 3. Leader-swap coincidence (detection <= 600 steps after a swap), by label

| config | label | n | within600 | chance |
|---|---|---|---|---|
| hfr-all/error | echo | 6 | 0.000 | 0.184 |
| hfr-all/error | echo_inwin | 9 | 0.889 | 0.184 |
| hfr-all/error | hit | 10 | 0.100 | 0.184 |
| hfr-all/error | orphan | 5 | 0.000 | 0.184 |
| hfr/error | echo | 3 | 0.000 | 0.154 |
| hfr/error | echo_inwin | 6 | 0.833 | 0.154 |
| hfr/error | hit | 9 | 0.000 | 0.154 |
| hfr/error | orphan | 4 | 0.250 | 0.154 | 
(pooled chance baseline 0.169)

## 4. Normalizer discordance by label

| label |  | masked_fall |
|---|---|---|
| echo | 3 | 6 |
| echo_inwin | 14 | 1 |
| hit | 16 | 3 |
| orphan | 7 | 2 | 

## 5. Gap distributions

- echo: n=9, steps after the previous ground-truth drift: p25=1463 median=2649 p75=2833 max=2871
- echo_inwin: n=15, steps after the previous ground-truth drift: p25=474 median=697 p75=925 max=1273
- orphan: n=6, steps after the previous ground-truth drift: p25=2468 median=3576 p75=4195 max=4889
- orphans BEFORE the first ground-truth drift (first-concept learning ramp): 3 of 9 orphans

## 6. Per-segment error level (normalized vs raw), first -> last stable segment

| dataset | config | segments | norm_first | norm_last | raw_first | raw_last | norm_change | raw_rel_change |
|---|---|---|---|---|---|---|---|---|
| reg_gradual_20k.csv | hfr-all/error | 3 | 0.440 | 0.481 | 1.057 | 1.281 | 0.040 | 0.213 |
| reg_gradual_20k.csv | hfr/error | 3 | 0.491 | 0.465 | 2.351 | 2.352 | -0.026 | 0.001 |
| reg_recurring_20k.csv | hfr-all/error | 6 | 0.454 | 0.463 | 1.150 | 1.126 | 0.009 | -0.021 |
| reg_recurring_20k.csv | hfr/error | 6 | 0.488 | 0.456 | 2.365 | 2.465 | -0.032 | 0.042 |
| reg_sudden_20k.csv | hfr-all/error | 4 | 0.442 | 0.454 | 1.104 | 0.848 | 0.012 | -0.232 |
| reg_sudden_20k.csv | hfr/error | 4 | 0.488 | 0.466 | 2.271 | 2.260 | -0.022 | -0.005 | 

## 7. Counterfactual replay: drift ADWIN on normalized err vs raw residual at a FIXED scale

Replay fidelity = replay fires on `err` vs the pipeline's own drift-arm fires (is_drift rows). Fixed scale = raw / (mean + 3 sd of the whole stream's raw residual), clipped to [0, 1].

| dataset | config | pipe_fires | replay_norm | norm_tp | norm_fp | replay_raw_fixed | raw_tp | raw_fp |
|---|---|---|---|---|---|---|---|---|
| reg_gradual_20k.csv | hfr-all/error | 10 | 10 | 2 | 5 | 12 | 2 | 6 |
| reg_gradual_20k.csv | hfr/error | 7 | 7 | 2 | 2 | 7 | 2 | 2 |
| reg_recurring_20k.csv | hfr-all/error | 11 | 11 | 5 | 3 | 14 | 5 | 5 |
| reg_recurring_20k.csv | hfr/error | 9 | 9 | 5 | 3 | 11 | 5 | 3 |
| reg_sudden_20k.csv | hfr-all/error | 9 | 9 | 3 | 4 | 12 | 3 | 7 |
| reg_sudden_20k.csv | hfr/error | 6 | 6 | 3 | 2 | 8 | 3 | 3 | 

Totals:

| config | pipe_fires | replay_norm | norm_tp | norm_fp | replay_raw_fixed | raw_tp | raw_fp |
|---|---|---|---|---|---|---|---|
| hfr-all/error | 30 | 30 | 10 | 12 | 38 | 10 | 18 |
| hfr/error | 22 | 22 | 10 | 7 | 26 | 10 | 8 |
