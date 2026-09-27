# E0 verdict (2026-09-27, river 0.21.2; prereg docs/ECPF_E0_原生切點方向_預註冊.md)

## Validity
fire mismatches=0  width mismatches=0  unlinked confirmations=0

## T1  family x label x native direction (drift arm at confirmation)
d_dir               dec  inc
family  label               
B       echo          1    0
        echo_inwin    0    1
        hit           1    5
        orphan        9    1
MC-RBF  echo          6    0
        echo_inwin   10    0
        hit          11   11
        orphan       15    3
MC-syn  echo         17    3
        echo_inwin   19    0
        hit           3   32
        orphan       23    5
REG-Joe echo          1    1
        echo_inwin    1    0
        hit           4   19
        orphan       12   15
REG-syn echo          4    5
        echo_inwin    4    0
        hit           1   17
        orphan        8    3

## D1  p_dec(FP)
          n  p_dec
family            
B        11  0.909
MC-RBF   24  0.875
MC-syn   48  0.833
REG-Joe  29  0.448
REG-syn  20  0.600
pooled=0.727 (n=132)  ->  PARTIAL GO (predicted ineffective: REG-Joe)

## D2  decrease-triggered hits
          n  tp_dec
family             
B         6       1
MC-RBF   22      11
MC-syn   35       3
REG-Joe  23       4
REG-syn  18       1
pooled TP_dec=20 of 104  ->  E2 SAME ROUND as E1
E1 TP-loss allowance per family: {"B": 1, "MC-RBF": 11, "MC-syn": 3, "REG-Joe": 4, "REG-syn": 1}
decrease-triggered hits (audit list, no decision weight):
 family                                              dataset         config  warning_t  confirmation_t
REG-syn                                   reg_sudden_20k.csv   htr-nr/error      15015           15047
REG-Joe   sudden/high/recurring_sudden_friedman_100k_g01.csv   htr-nr/error      39271           39303
REG-Joe sudden/medium/recurring_sudden_friedman_100k_g00.csv   htr-nr/error      40519           40519
REG-Joe sudden/medium/recurring_sudden_friedman_100k_g01.csv   htr-nr/error      17319           17479
REG-Joe sudden/medium/recurring_sudden_friedman_100k_g01.csv   htr-nr/error      71239           71271
 MC-syn                                   mc3_sudden_20k.csv  hf10all/error       5575            5575
 MC-syn                                   mc5_sudden_20k.csv  hf10all/error       5511            5511
 MC-syn                                   mc5_sudden_20k.csv  hf10all/error      10503           10535
 MC-RBF     gradual/high/recurring_gradual_rbf4_100k_g00.csv  hf10all/error       9703           10535
 MC-RBF     gradual/high/recurring_gradual_rbf4_100k_g00.csv  hf10all/error      16615           16615
 MC-RBF     gradual/high/recurring_gradual_rbf4_100k_g00.csv hf10sqrt/error      12711           12711
 MC-RBF      gradual/low/recurring_gradual_rbf4_100k_g00.csv  hf10all/error       2503            2503
 MC-RBF      gradual/low/recurring_gradual_rbf4_100k_g00.csv hf10sqrt/error       2695            3783
 MC-RBF      gradual/low/recurring_gradual_rbf4_100k_g00.csv hf10sqrt/error      15911           15911
 MC-RBF   gradual/medium/recurring_gradual_rbf4_100k_g00.csv  hf10all/error      18471           19623
 MC-RBF   gradual/medium/recurring_gradual_rbf4_100k_g00.csv hf10sqrt/error      14151           14215
 MC-RBF       sudden/high/recurring_sudden_rbf4_100k_g00.csv hf10sqrt/error      16679           16807
 MC-RBF        sudden/low/recurring_sudden_rbf4_100k_g00.csv hf10sqrt/error        807             807
 MC-RBF     sudden/medium/recurring_sudden_rbf4_100k_g00.csv  hf10all/error      17639           17671
      B            recurring/-/recurring_sud_sea100k_g00.csv     hf10/error      14535           14535

## M1  lead=0 confirmations: 115 of 271; shadow_lead>=16 in 0.45  ->  threshold-bound, report item 8 dropped
         count   50%      max
family                       
B          5.0   4.0      4.0
MC-RBF    23.0   4.0   6268.0
MC-syn    50.0   9.5   2396.0
REG-Joe   17.0  19.0  23289.0
REG-syn   20.0  13.5    278.0

## M2  cascade-candidate FPs: n=3 (<8, descriptive only)

## M3  regression rise-FPs=24, raw-flat-or-falling=20  ->  E2 H1 target set = these events

## M4 / M5
B        warnings opened by a decrease=0.56  paused steps=5728 (3.2% of stream)  |  dropped drift fires=0 (dec nan)
MC-RBF   warnings opened by a decrease=0.77  paused steps=16512 (6.9% of stream)  -> E1 secondary: accuracy/MAE should IMPROVE  |  dropped drift fires=0 (dec nan)
MC-syn   warnings opened by a decrease=0.66  paused steps=30240 (12.7% of stream)  -> E1 secondary: accuracy/MAE should IMPROVE  |  dropped drift fires=0 (dec nan)
REG-Joe  warnings opened by a decrease=0.40  paused steps=42880 (3.6% of stream)  |  dropped drift fires=0 (dec nan)
REG-syn  warnings opened by a decrease=0.45  paused steps=2848 (2.4% of stream)  |  dropped drift fires=0 (dec nan)
