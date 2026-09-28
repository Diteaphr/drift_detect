## A2 per group (quality = accuracy, or MAE for SYN2-REG; delay = median hit delay at 3000)
group     arm      TP@1000  FP@1000  TP@3000  FP@3000   delay   quality
SYN2-B    base          41       61       44       45     708    0.9536
SYN2-B    E1            40        5       41        4     799    0.9516
SYN2-B    E2k500        26       14       30       10    1012    0.9430
SYN2-MC   base          32       80       35       56     590    0.6801
SYN2-MC   E1            34        1       34        1     522    0.7327
SYN2-MC   E2k500        28       10       31        4     706    0.7137
SYN2-REG  base          39       30       53       16    1007    2.8940
SYN2-REG  E1            30       19       33       16     836    2.8522
SYN2-REG  E2k500        37       14       43        8     879    2.8831
INJ-gas   base          10       54       15       48    1006    0.6905
INJ-gas   E1             7        1        7        1     373    0.6980
INJ-gas   E2k500        10        8       13        5     796    0.6965

## INJ-gas per injection method (6 streams each, one drift per stream)
method arm      preFP  TP@1000  TP@3000  FP@1000  FP@3000  accuracy
cp     base        12        0        2       14       12    0.7114
cp     E1           0        0        0        0        0    0.7291
cp     E2k500       2        0        1        3        2    0.7206
ls     base        12        1        3       14       12    0.7062
ls     E1           0        2        2        0        0    0.7026
ls     E2k500       0        1        3        2        0    0.7032
fp     base        11        4        5       15       13    0.6494
fp     E1           1        4        4        1        1    0.6632
fp     E2k500       0        6        6        0        0    0.6648
ff     base        11        5        5       11       11    0.6949
ff     E1           0        1        1        0        0    0.6970
ff     E2k500       3        3        3        3        3    0.6976

## Criteria
E1: P1 pre-drift FP 1 vs base 46 (need <=13.8, base>=10): True | P2 TP@3000 7 vs base 15 (need >=13.5): False
E1: P3 SYN2-B FP@3000 4 vs base 45 (need <=22.5: True) | TP@3000 41 vs base 44 (need >=39.6): True -> True
E1: P3 SYN2-MC FP@3000 1 vs base 56 (need <=28.0: True) | TP@3000 34 vs base 35 (need >=31.5): True -> True
E1: P3 SYN2-REG FP@3000 16 vs base 16 (need <=8.0: False) | TP@3000 33 vs base 53 (need >=47.7): False -> False
E1: P4 SYN2-B quality 0.9516 vs base 0.9536: True
E1: P4 SYN2-MC quality 0.7327 vs base 0.6801: True
E1: P4 SYN2-REG quality 2.8522 vs base 2.8940: True
E1: P4 INJ-gas quality 0.6980 vs base 0.6905: True
E2k500: P1 pre-drift FP 5 vs base 46 (need <=13.8, base>=10): True | P2 TP@3000 13 vs base 15 (need >=13.5): False
E2k500: P3 SYN2-B FP@3000 10 vs base 45 (need <=22.5: True) | TP@3000 30 vs base 44 (need >=39.6): False -> False
E2k500: P3 SYN2-MC FP@3000 4 vs base 56 (need <=28.0: True) | TP@3000 31 vs base 35 (need >=31.5): False -> False
E2k500: P3 SYN2-REG FP@3000 8 vs base 16 (need <=8.0: True) | TP@3000 43 vs base 53 (need >=47.7): False -> False
E2k500: P4 SYN2-B quality 0.9430 vs base 0.9536: False
E2k500: P4 SYN2-MC quality 0.7137 vs base 0.6801: True
E2k500: P4 SYN2-REG quality 2.8831 vs base 2.8940: True
E2k500: P4 INJ-gas quality 0.6965 vs base 0.6905: True
P5 gradual+incremental TP@3000 {'base': 97, 'E1': 81, 'E2k500': 86} -> E2k500 >= E1: True
hyperplane incremental: confirmations with warning in [200, 1950] (unscored GT [0, 950]): {'base': 0, 'E1': 0, 'E2k500': 0}
A2 verdict E1: classification does NOT hold; regression does NOT hold
A2 verdict E2k500: classification does NOT hold; regression does NOT hold

## Stale-reference check: E2-k500 max reference age per group; aligned tail after its last freeze
group
INJ-gas     13709
SYN2-B      81041
SYN2-MC     26220
SYN2-REG    47710
   group                                                           run  max_age  tail   base     E1  E2k500
 INJ-gas          gas_sensor_drift_class_prior_abrupt_g00.csv hf10sqrt    12816 12815 0.7241 0.7210  0.7210
 INJ-gas          gas_sensor_drift_class_prior_abrupt_g02.csv hf10sqrt    12893 12892 0.7200 0.7287  0.7287
 INJ-gas         gas_sensor_drift_class_prior_gradual_g00.csv hf10sqrt    12918 12917 0.6670 0.7293  0.7293
 INJ-gas         gas_sensor_drift_class_prior_gradual_g01.csv hf10sqrt    12800 12799 0.7034 0.7100  0.7100
 INJ-gas         gas_sensor_drift_class_prior_gradual_g02.csv hf10sqrt    13076 13075 0.7116 0.7485  0.7485
 INJ-gas    gas_sensor_drift_feature_filtering_abrupt_g01.csv hf10sqrt    10596 10595 0.6911 0.7025  0.7025
 INJ-gas    gas_sensor_drift_feature_filtering_abrupt_g02.csv hf10sqrt     5651  5650 0.7367 0.7446  0.7514
 INJ-gas   gas_sensor_drift_feature_filtering_gradual_g01.csv hf10sqrt     7446  7445 0.7830 0.7827  0.7632
 INJ-gas  gas_sensor_drift_feature_permutation_abrupt_g00.csv hf10sqrt     8159  5049 0.5875 0.6794  0.6723
 INJ-gas  gas_sensor_drift_feature_permutation_abrupt_g01.csv hf10sqrt     7679  5529 0.6727 0.6890  0.6890
 INJ-gas gas_sensor_drift_feature_permutation_gradual_g00.csv hf10sqrt     7615  5593 0.6199 0.6832  0.6829
 INJ-gas           gas_sensor_drift_label_swap_abrupt_g01.csv hf10sqrt    13709 13708 0.6788 0.6735  0.6753
 INJ-gas          gas_sensor_drift_label_swap_gradual_g00.csv hf10sqrt    13709 13708 0.7074 0.7080  0.7084
 INJ-gas          gas_sensor_drift_label_swap_gradual_g01.csv hf10sqrt    13709 13708 0.7133 0.7029  0.7029
  SYN2-B                                  gradual_sea100k_g00.csv hf10    67761 67760 0.9432 0.9515  0.9174
  SYN2-B                                    gradual_sea100k_g00.csv ht    24831  7057 0.9634 0.9538  0.9626
  SYN2-B                      incremental_hyperplane_100k_g00.csv hf10    24063  7460 0.9330 0.9459  0.9492
  SYN2-B                        incremental_hyperplane_100k_g00.csv ht    21727  7844 0.9229 0.9275  0.9293
  SYN2-B                          recurring_gradual_sea100k_g00.csv ht    81041 81040 0.9726 0.9726  0.9272
  SYN2-B                                   sudden_sea100k_g00.csv hf10    20063 11684 0.9845 0.9371  0.9785
  SYN2-B                                     sudden_sea100k_g00.csv ht    47211 47210 0.9834 0.9639  0.9393
 SYN2-MC              recurring_incremental_rbf4_100k_g00.csv hf10sqrt    26220 26219 0.7345 0.7885  0.7233
 SYN2-MC                             sudden_rbf4_100k_g00.csv hf10sqrt    16383 10104 0.7146 0.7292  0.7385
SYN2-REG                             gradual_friedman_100k_g00.csv hfr    16607  5995 3.3713 3.3799  3.3561
SYN2-REG                             gradual_friedman_100k_g00.csv htr    23263  5758 1.9583 1.7729  1.9791
SYN2-REG                    recurring_sudden_friedman_100k_g00.csv hfr    47710 47709 2.9854 2.9762  2.9744
SYN2-REG                    recurring_sudden_friedman_100k_g00.csv htr    41247 31133 1.8627 1.7012  1.6721
SYN2-REG                              sudden_friedman_100k_g00.csv hfr    37151 13834 2.7013 2.8385  2.7209
SYN2-REG                              sudden_friedman_100k_g00.csv htr    23551 12951 1.6632 1.6603  1.7257
