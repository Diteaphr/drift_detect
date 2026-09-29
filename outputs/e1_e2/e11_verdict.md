## A0 validity: longest warning->confirmation age {'base': 44576, 'baseT': 992, 'E1T': 960, 'E2k500T': 800} -> VALID

## E11 per group (quality = accuracy, or MAE for SYN2g23-REG; delay = median hit delay at 3000)
group     arm      TP@1000  FP@1000  TP@3000  FP@3000   delay   quality   excess
SYN2g23-B base          58      120       79       86     890    0.9484     51.3
SYN2g23-B baseT         62       95       79       67     850    0.9519     56.2
SYN2g23-B E1T           65       19       72       12     780    0.9530     68.3
SYN2g23-B E2k500T       61       27       73       14     901    0.9510     67.6
SYN2g23-MC base          52      148       58       99     574    0.7130     31.6
SYN2g23-MC baseT         55      132       57       90     486    0.7143     32.1
SYN2g23-MC E1T           52        0       52        0     590    0.7397     52.0
SYN2g23-MC E2k500T       51       12       54        7     760    0.7326     51.1
SYN2g23-REG base          64       55       83       35    1088    2.9130     72.6
SYN2g23-REG baseT         70       34       82       20     959    2.8961     75.7
SYN2g23-REG E1T           53       26       59       20     679    2.9030     51.7
SYN2g23-REG E2k500T       70       15       81        4     845    2.8991     80.1
INJgas68  base          13       55       18       49     635    0.6945      6.5
INJgas68  baseT         11       48       16       41     620    0.6961      6.1
INJgas68  E1T           12        1       13        0     540    0.6999     13.0
INJgas68  E2k500T       13        3       16        0     640    0.6987     16.0

## INJgas68 per injection method (6 streams each, one drift per stream)
method arm      preFP  TP@1000  TP@3000  FP@1000  FP@3000  accuracy
cp     base        11        3        4       12       11    0.7191
cp     baseT        9        1        4       12        9    0.7207
cp     E1T          0        0        0        0        0    0.7247
cp     E2k500T      0        0        0        0        0    0.7247
ls     base        11        3        4       15       14    0.7036
ls     baseT        9        3        3       12       12    0.7047
ls     E1T          0        5        5        0        0    0.7020
ls     E2k500T      0        2        5        3        0    0.7014
fp     base        13        5        6       17       16    0.6669
fp     baseT       10        6        6       15       13    0.6688
fp     E1T          0        5        5        0        0    0.6798
fp     E2k500T      0        6        6        0        0    0.6787
ff     base         8        2        4       11        8    0.6883
ff     baseT        7        1        3        9        7    0.6903
ff     E1T          0        2        3        1        0    0.6932
ff     E2k500T      0        5        5        0        0    0.6902

## Criteria
E1T: P1 pre-drift FP 0 vs baseT 35 (need <=10.5, baseT>=10): True | P2 excess@3000 13.0 vs baseT 6.1 (need >=5.5): True
E1T: P3 SYN2g23-B FP@3000 12 vs baseT 67 (need <=33.5: True) | excess@3000 68.3 vs baseT 56.2 (need >=50.6): True -> True
E1T: P3 SYN2g23-MC FP@3000 0 vs baseT 90 (need <=45.0: True) | excess@3000 52.0 vs baseT 32.1 (need >=28.9): True -> True
E1T: P3 SYN2g23-REG FP@3000 20 vs baseT 20 (need <=10.0: False) | excess@3000 51.7 vs baseT 75.7 (need >=68.1): False -> False
E1T: P4 SYN2g23-B quality 0.9530 vs baseT 0.9519: True
E1T: P4 SYN2g23-MC quality 0.7397 vs baseT 0.7143: True
E1T: P4 SYN2g23-REG quality 2.9030 vs baseT 2.8961: True
E1T: P4 INJgas68 quality 0.6999 vs baseT 0.6961: True
E2k500T: P1 pre-drift FP 0 vs baseT 35 (need <=10.5, baseT>=10): True | P2 excess@3000 16.0 vs baseT 6.1 (need >=5.5): True
E2k500T: P3 SYN2g23-B FP@3000 14 vs baseT 67 (need <=33.5: True) | excess@3000 67.6 vs baseT 56.2 (need >=50.6): True -> True
E2k500T: P3 SYN2g23-MC FP@3000 7 vs baseT 90 (need <=45.0: True) | excess@3000 51.1 vs baseT 32.1 (need >=28.9): True -> True
E2k500T: P3 SYN2g23-REG FP@3000 4 vs baseT 20 (need <=10.0: True) | excess@3000 80.1 vs baseT 75.7 (need >=68.1): True -> True
E2k500T: P4 SYN2g23-B quality 0.9510 vs baseT 0.9519: True
E2k500T: P4 SYN2g23-MC quality 0.7326 vs baseT 0.7143: True
E2k500T: P4 SYN2g23-REG quality 2.8991 vs baseT 2.8961: True
E2k500T: P4 INJgas68 quality 0.6987 vs baseT 0.6961: True

## A: the timeout itself (base vs baseT, paired)
SYN2g23-B   quality base 0.9484 -> baseT 0.9519: True
SYN2g23-MC  quality base 0.7130 -> baseT 0.7143: True
SYN2g23-REG quality base 2.9130 -> baseT 2.8961: True
INJgas68    quality base 0.6945 -> baseT 0.6961: True
pooled excess hits base 162.0 -> baseT 170.1 (need >= 145.8) | FP@3000 269 -> 218
A1 True -> the 1000-step timeout becomes the standard setting

## B verdicts (vs baseT, recall = excess hits)
E11 verdict E1T: classification HOLDS; regression does NOT hold
E11 verdict E2k500T: classification HOLDS; regression HOLDS

## warning->confirmation ages
base     confirmations  597  p50   32  p95  3437  max 44576
baseT    confirmations  541  p50   32  p95   576  max   992
E1T      confirmations  228  p50   32  p95   522  max   960
E2k500T  confirmations  252  p50   32  p95   398  max   800
