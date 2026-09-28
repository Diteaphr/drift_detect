## E10 per group (quality = accuracy, or MAE for SYN2g01-REG; delay = median hit delay at 3000)
group     arm      TP@1000  FP@1000  TP@3000  FP@3000   delay   quality
SYN2g01-B base          22       66       39       42     913    0.9512
SYN2g01-B E1            32       14       37        9     666    0.9553
SYN2g01-B E2k500        28       16       38        6     992    0.9481
SYN2g01-B E10a          31        8       35        4     652    0.9509
SYN2g01-B E10b          37       19       42       14     798    0.9553
SYN2g01-MC base          24       65       28       41     554    0.7078
SYN2g01-MC E1            22        3       22        3     533    0.7518
SYN2g01-MC E2k500        26        7       24        7     612    0.7363
SYN2g01-MC E10a          25       10       26        6     524    0.7353
SYN2g01-MC E10b          22       10       20       10     478    0.7399
SYN2g01-REG base          34       25       47       11    1313    2.6442
SYN2g01-REG E1            25       15       30       10    1042    2.5792
SYN2g01-REG E2k500        37       21       49        7    1066    2.5926
SYN2g01-REG E10a          37        6       41        2     971    2.5989
SYN2g01-REG E10b          41       25       53       10    1092    2.5971
INJgas35  base          10       55       16       44    1020    0.6949
INJgas35  E1             7        3        7        3     619    0.7035
INJgas35  E2k500        10        8       12        6    1000    0.6846
INJgas35  E10a           8        7        9        6     472    0.6843
INJgas35  E10b          10       10       11        9     754    0.6844

## INJgas35 per injection method (6 streams each, one drift per stream)
method arm      preFP  TP@1000  TP@3000  FP@1000  FP@3000  accuracy
cp     base         6        2        4        8        6    0.7089
cp     E1           0        0        0        0        0    0.7275
cp     E2k500       1        0        0        1        1    0.7078
cp     E10a         1        0        0        1        1    0.7079
cp     E10b         1        0        0        1        1    0.7020
ls     base        11        3        5       14       11    0.6977
ls     E1           3        1        1        3        3    0.7009
ls     E2k500       3        1        3        5        3    0.6670
ls     E10a         3        2        2        3        3    0.6646
ls     E10b         6        0        1        7        6    0.6613
fp     base        13        4        6       19       13    0.6712
fp     E1           0        5        5        0        0    0.6782
fp     E2k500       0        6        6        0        0    0.6769
fp     E10a         0        6        6        0        0    0.6778
fp     E10b         0        6        6        0        0    0.6782
ff     base        14        1        1       14       14    0.7019
ff     E1           0        1        1        0        0    0.7076
ff     E2k500       2        3        3        2        2    0.6866
ff     E10a         2        0        1        3        2    0.6872
ff     E10b         2        4        4        2        2    0.6960

## Criteria
E10a: P1 pre-drift FP 6 vs base 44 (need <=13.2, base>=10): True | P2 TP@3000 9 vs base 16 (need >=14.4): False
E10a: P3 SYN2g01-B FP@3000 4 vs base 42 (need <=21.0: True) | TP@3000 35 vs base 39 (need >=35.1): False -> False
E10a: P3 SYN2g01-MC FP@3000 6 vs base 41 (need <=20.5: True) | TP@3000 26 vs base 28 (need >=25.2): True -> True
E10a: P3 SYN2g01-REG FP@3000 2 vs base 11 (need <=5.5: True) | TP@3000 41 vs base 47 (need >=42.3): False -> False
E10a: P4 SYN2g01-B quality 0.9509 vs base 0.9512: True
E10a: P4 SYN2g01-MC quality 0.7353 vs base 0.7078: True
E10a: P4 SYN2g01-REG quality 2.5989 vs base 2.6442: True
E10a: P4 INJgas35 quality 0.6843 vs base 0.6949: False
E10b: P1 pre-drift FP 9 vs base 44 (need <=13.2, base>=10): True | P2 TP@3000 11 vs base 16 (need >=14.4): False
E10b: P3 SYN2g01-B FP@3000 14 vs base 42 (need <=21.0: True) | TP@3000 42 vs base 39 (need >=35.1): True -> True
E10b: P3 SYN2g01-MC FP@3000 10 vs base 41 (need <=20.5: True) | TP@3000 20 vs base 28 (need >=25.2): False -> False
E10b: P3 SYN2g01-REG FP@3000 10 vs base 11 (need <=5.5: False) | TP@3000 53 vs base 47 (need >=42.3): True -> False
E10b: P4 SYN2g01-B quality 0.9553 vs base 0.9512: True
E10b: P4 SYN2g01-MC quality 0.7399 vs base 0.7078: True
E10b: P4 SYN2g01-REG quality 2.5971 vs base 2.6442: True
E10b: P4 INJgas35 quality 0.6844 vs base 0.6949: False
gradual+incremental TP@3000 {'base': 92, 'E1': 65, 'E2k500': 87, 'E10a': 75, 'E10b': 85}
E10 verdict classification: passed none; TP@3000 E10a 70, E10b 73 -> neither adopted: E2-k500's long-stream recall problem remains
E10 verdict regression: passed none; TP@3000 E10a 41, E10b 53 -> neither adopted: E2-k500's long-stream recall problem remains

## Mechanism (reported, not judged)
GT drifts missed by E2-k500 with its reference >= 10k steps old: 22; hit by base 15, E1 10, E10a 8, E10b 15
E10a reference refreshes: 318
E10b confirmations 175, of which the leader guard fired the drift: 80
max reference age:
arm           E10a   E10b  E2k500
group                            
INJgas35     13161  13311   13311
SYN2g01-B    54975  30494   54975
SYN2g01-MC   14335  28063   40479
SYN2g01-REG   8767  28671   31615

## Development check, INSECTS abrupt (not judged): accuracy, TP@1000, FP@1000, confirmations
base    0.6919   5  16  24
E1      0.6951   4   6  11
E2k500  0.6630   4   4   8
E10a    0.7026   3   6   9
E10b    0.6499   4   6  12
