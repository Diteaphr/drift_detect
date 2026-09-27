## 0. FP sub-labels (post hoc) and the expert the preceding hit installed

| config | label | (none) | late | pre_drift | stale_warning |
|---|---|---|---|---|---|
| hfr/error | echo | 4 | 0 | 0 | 0 |
| hfr/error | orphan | 16 | 5 | 0 | 3 |
| htr/error | echo | 19 | 0 | 0 | 0 |
| htr/error | orphan | 55 | 6 | 2 | 3 | 

Reuse decision at each confirmation: length of the warning buffer it was made on (buffer = confirm_age + 1 instances; the reused best slot is chosen by its score on it):

| config | label | n | buf_median | buf_is_1 | buf_le_10 |
|---|---|---|---|---|---|
| hfr/error | echo | 4 | 721.000 | 0.000 | 0.000 |
| hfr/error | echo_inwin | 6 | 49.000 | 0.500 | 0.500 |
| hfr/error | hit | 19 | 33.000 | 0.421 | 0.421 |
| hfr/error | orphan | 24 | 273.000 | 0.292 | 0.292 |
| htr/error | echo | 19 | 33.000 | 0.421 | 0.421 |
| htr/error | echo_inwin | 15 | 33.000 | 0.333 | 0.333 |
| htr/error | hit | 22 | 17.000 | 0.500 | 0.500 |
| htr/error | orphan | 66 | 81.000 | 0.288 | 0.288 | 

Immediate effect of the model installed at each confirmation: raw MAE over the 200 steps after the install vs the 200 before it (ratio > 1.5 = the replacement made things worse):

| config | label | n | median_ratio | worse_x1_5 | better_x0_67 |
|---|---|---|---|---|---|
| hfr/error | echo | 4 | 1.100 | 0.000 | 0.000 |
| hfr/error | echo_inwin | 6 | 0.994 | 0.000 | 0.000 |
| hfr/error | hit | 19 | 0.876 | 0.000 | 0.263 |
| hfr/error | orphan | 24 | 1.011 | 0.000 | 0.000 |
| htr/error | echo | 19 | 1.022 | 0.105 | 0.105 |
| htr/error | echo_inwin | 15 | 1.068 | 0.400 | 0.067 |
| htr/error | hit | 22 | 1.078 | 0.227 | 0.091 |
| htr/error | orphan | 66 | 1.118 | 0.242 | 0.030 | 

## 1. Recall and FP structure (per config x group)

| group | config | streams | n_gt | tp | recall | fp | fp_per_stream | echo | orphan | echo_inwin | dropped | swaps | mae | cd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| joe-sudden | hfr/error | 6 | 18 | 10 | 0.556 | 21 | 3.500 | 1 | 20 | 0 | 0 | 401 | 3.458 | 0.000 |
| joe-sudden | htr/error | 6 | 18 | 12 | 0.667 | 65 | 10.833 | 7 | 58 | 5 | 0 | 298 | 1.921 | 0.000 |
| synthetic | hfr/error | 3 | 10 | 9 | 0.900 | 7 | 2.333 | 3 | 4 | 6 | 0 | 27 | 2.889 | 17.767 |
| synthetic | htr/error | 3 | 10 | 10 | 1.000 | 20 | 6.667 | 12 | 8 | 10 | 0 | 68 | 2.671 | 0.000 | 

## 2. Error direction at the detection, by label (pooled over configs)

| config | label | fall | flat | rise |
|---|---|---|---|---|
| hfr/error | echo | 0 | 3 | 1 |
| hfr/error | echo_inwin | 5 | 0 | 1 |
| hfr/error | hit | 6 | 8 | 5 |
| hfr/error | orphan | 3 | 16 | 5 |
| htr/error | echo | 8 | 5 | 6 |
| htr/error | echo_inwin | 10 | 3 | 2 |
| htr/error | hit | 2 | 7 | 13 |
| htr/error | orphan | 7 | 30 | 29 | 

Mean normalized delta / raw relative change by label:

| config | label | n | norm_delta | raw_rel | confirm_age |
|---|---|---|---|---|---|
| hfr/error | echo | 4 | 0.003 | 0.034 | 720.000 |
| hfr/error | echo_inwin | 6 | -0.033 | -0.098 | 48.000 |
| hfr/error | hit | 19 | 0.001 | -0.013 | 32.000 |
| hfr/error | orphan | 24 | -0.001 | 0.003 | 272.000 |
| htr/error | echo | 19 | -0.015 | -0.009 | 32.000 |
| htr/error | echo_inwin | 15 | -0.044 | -0.153 | 32.000 |
| htr/error | hit | 22 | 0.075 | 0.464 | 16.000 |
| htr/error | orphan | 66 | 0.012 | 0.072 | 80.000 | 

## 3. Leader-swap coincidence (detection <= 600 steps after a swap), by label

| config | label | n | within600 | chance |
|---|---|---|---|---|
| hfr/error | echo | 4 | 0.000 | 0.057 |
| hfr/error | echo_inwin | 6 | 0.833 | 0.057 |
| hfr/error | hit | 19 | 0.000 | 0.057 |
| hfr/error | orphan | 24 | 0.083 | 0.057 |
| htr/error | echo | 19 | 0.421 | 0.065 |
| htr/error | echo_inwin | 15 | 0.667 | 0.065 |
| htr/error | hit | 22 | 0.091 | 0.065 |
| htr/error | orphan | 66 | 0.197 | 0.065 | 
(pooled chance baseline 0.061)

## 4. Normalizer discordance by label

| label |  | fake_fall | masked_fall |
|---|---|---|---|
| echo | 20 | 0 | 3 |
| echo_inwin | 21 | 0 | 0 |
| hit | 35 | 0 | 6 |
| orphan | 80 | 1 | 9 | 

## 5. Gap distributions

- echo: n=23, steps after the previous ground-truth drift: p25=1373 median=1561 p75=2269 max=2877
- echo_inwin: n=21, steps after the previous ground-truth drift: p25=472 median=785 p75=863 max=1017
- orphan: n=82, steps after the previous ground-truth drift: p25=4531 median=8103 p75=12689 max=50531
- orphans BEFORE the first ground-truth drift (first-concept learning ramp): 8 of 90 orphans

## 6. Per-segment error level (normalized vs raw), first -> last stable segment

| dataset | config | segments | norm_first | norm_last | raw_first | raw_last | norm_change | raw_rel_change |
|---|---|---|---|---|---|---|---|---|
| reg_gradual_20k.csv | hfr/error | 3 | 0.491 | 0.465 | 2.351 | 2.352 | -0.026 | 0.001 |
| reg_gradual_20k.csv | htr/error | 3 | 0.447 | 0.459 | 2.174 | 2.021 | 0.011 | -0.070 |
| reg_recurring_20k.csv | hfr/error | 6 | 0.488 | 0.456 | 2.365 | 2.465 | -0.032 | 0.042 |
| reg_recurring_20k.csv | htr/error | 6 | 0.460 | 0.434 | 2.358 | 1.733 | -0.026 | -0.265 |
| reg_sudden_20k.csv | hfr/error | 4 | 0.488 | 0.466 | 2.271 | 2.260 | -0.022 | -0.005 |
| reg_sudden_20k.csv | htr/error | 4 | 0.443 | 0.458 | 1.777 | 2.003 | 0.014 | 0.127 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | hfr/error | 4 | 0.496 | 0.547 | 2.913 | 3.876 | 0.051 | 0.331 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | htr/error | 4 | 0.483 | 0.546 | 1.743 | 2.257 | 0.063 | 0.295 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | hfr/error | 4 | 0.496 | 0.557 | 2.927 | 5.060 | 0.061 | 0.729 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | htr/error | 4 | 0.479 | 0.470 | 1.774 | 1.927 | -0.009 | 0.086 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | hfr/error | 4 | 0.498 | 0.472 | 2.954 | 2.574 | -0.026 | -0.129 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | htr/error | 4 | 0.477 | 0.492 | 1.803 | 1.686 | 0.015 | -0.065 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | hfr/error | 4 | 0.498 | 0.489 | 2.896 | 3.224 | -0.008 | 0.113 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | htr/error | 4 | 0.481 | 0.498 | 1.777 | 1.924 | 0.017 | 0.083 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | hfr/error | 4 | 0.495 | 0.519 | 2.917 | 3.793 | 0.024 | 0.300 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | htr/error | 4 | 0.482 | 0.488 | 1.788 | 1.921 | 0.006 | 0.075 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | hfr/error | 4 | 0.497 | 0.485 | 2.917 | 3.312 | -0.011 | 0.135 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | htr/error | 4 | 0.478 | 0.470 | 1.801 | 1.629 | -0.008 | -0.096 | 

## 7. Counterfactual replay: drift ADWIN on normalized err vs raw residual at a FIXED scale

Replay fidelity = replay fires on `err` vs the pipeline's own drift-arm fires (is_drift rows). Fixed scale = raw / (mean + 3 sd of the whole stream's raw residual), clipped to [0, 1].

| dataset | config | pipe_fires | replay_norm | norm_tp | norm_fp | replay_raw_fixed | raw_tp | raw_fp |
|---|---|---|---|---|---|---|---|---|
| reg_gradual_20k.csv | hfr/error | 7 | 7 | 2 | 2 | 7 | 2 | 2 |
| reg_gradual_20k.csv | htr/error | 8 | 8 | 2 | 4 | 13 | 2 | 7 |
| reg_recurring_20k.csv | hfr/error | 9 | 9 | 5 | 3 | 11 | 5 | 3 |
| reg_recurring_20k.csv | htr/error | 17 | 17 | 5 | 6 | 20 | 5 | 7 |
| reg_sudden_20k.csv | hfr/error | 6 | 6 | 3 | 2 | 8 | 3 | 3 |
| reg_sudden_20k.csv | htr/error | 15 | 15 | 3 | 10 | 16 | 3 | 11 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | hfr/error | 5 | 5 | 2 | 3 | 3 | 2 | 1 |
| sudden/high/recurring_sudden_friedman_100k_g00.csv | htr/error | 13 | 13 | 3 | 9 | 9 | 2 | 6 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | hfr/error | 8 | 8 | 3 | 5 | 3 | 3 | 0 |
| sudden/high/recurring_sudden_friedman_100k_g01.csv | htr/error | 21 | 21 | 3 | 16 | 21 | 3 | 15 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | hfr/error | 3 | 3 | 0 | 3 | 4 | 0 | 4 |
| sudden/low/recurring_sudden_friedman_100k_g00.csv | htr/error | 6 | 6 | 1 | 5 | 9 | 1 | 8 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | hfr/error | 6 | 6 | 1 | 5 | 5 | 1 | 4 |
| sudden/low/recurring_sudden_friedman_100k_g01.csv | htr/error | 10 | 10 | 2 | 8 | 11 | 2 | 9 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | hfr/error | 5 | 5 | 3 | 2 | 4 | 3 | 1 |
| sudden/medium/recurring_sudden_friedman_100k_g00.csv | htr/error | 24 | 24 | 2 | 21 | 19 | 2 | 16 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | hfr/error | 4 | 4 | 1 | 3 | 3 | 2 | 0 |
| sudden/medium/recurring_sudden_friedman_100k_g01.csv | htr/error | 8 | 8 | 2 | 6 | 9 | 2 | 6 | 

Totals:

| config | pipe_fires | replay_norm | norm_tp | norm_fp | replay_raw_fixed | raw_tp | raw_fp |
|---|---|---|---|---|---|---|---|
| hfr/error | 53 | 53 | 20 | 28 | 48 | 21 | 18 |
| htr/error | 122 | 122 | 23 | 85 | 127 | 22 | 85 |
