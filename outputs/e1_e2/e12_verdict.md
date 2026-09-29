## A0 validity: longest warning->confirmation age {'baseT': 960, 'E2k500T': 928, 'E10bT': 845} -> VALID

## E12 per group (quality = accuracy, or MAE for SYN2g45-REG; delay = median hit delay at 3000)
group     arm      TP@1000  FP@1000  TP@3000  FP@3000   delay   quality   excess
SYN2g45-B baseT         75      116       89       86     791    0.9515     58.5
SYN2g45-B E2k500T       58       26       75        9    1013    0.9498     70.8
SYN2g45-B E10bT         90       36      104       22     827    0.9549     94.9
SYN2g45-MC baseT         57      122       59       83     518    0.7159     34.3
SYN2g45-MC E2k500T       43       13       45       10     813    0.7392     41.1
SYN2g45-MC E10bT         58       12       58       10     549    0.7363     53.9
SYN2g45-REG baseT         66       43       86       23    1173    2.6934     78.5
SYN2g45-REG E2k500T       78       23       91       10     963    2.6864     87.7
SYN2g45-REG E10bT         87       27       99       15     836    2.6835     94.1
INJgas9   baseT          3       17        5       13     494    0.6973      1.8
INJgas9   E2k500T        3        2        3        2     851    0.6990      2.5
INJgas9   E10bT          3        2        3        2     339    0.6983      2.5

## INJgas9 per injection method (2 streams each, one drift per stream)
method arm      preFP  TP@1000  TP@3000  FP@1000  FP@3000  accuracy
cp     baseT        3        0        1        4        3    0.7270
cp     E2k500T      0        0        0        0        0    0.7197
cp     E10bT        0        0        0        0        0    0.7197
ls     baseT        5        0        1        6        5    0.7085
ls     E2k500T      1        0        0        1        1    0.7126
ls     E10bT        1        0        0        1        1    0.7126
fp     baseT        1        2        2        4        2    0.6525
fp     E2k500T      0        2        2        0        0    0.6672
fp     E10bT        0        2        2        0        0    0.6643
ff     baseT        3        1        1        3        3    0.7013
ff     E2k500T      1        1        1        1        1    0.6965
ff     E10bT        1        1        1        1        1    0.6965

## Criteria
E2k500T: P1 pre-drift FP 2 vs baseT 12 (need <=3.6, baseT>=10): True | P2 excess@3000 2.5 vs baseT 1.8 (need >=1.6): True
E2k500T: P3 SYN2g45-B FP@3000 9 vs baseT 86 (need <=43.0: True) | excess@3000 70.8 vs baseT 58.5 (need >=52.7): True -> True
E2k500T: P3 SYN2g45-MC FP@3000 10 vs baseT 83 (need <=41.5: True) | excess@3000 41.1 vs baseT 34.3 (need >=30.9): True -> True
E2k500T: P3 SYN2g45-REG FP@3000 10 vs baseT 23 (need <=11.5: True) | excess@3000 87.7 vs baseT 78.5 (need >=70.6): True -> True
E2k500T: P4 SYN2g45-B quality 0.9498 vs baseT 0.9515: True
E2k500T: P4 SYN2g45-MC quality 0.7392 vs baseT 0.7159: True
E2k500T: P4 SYN2g45-REG quality 2.6864 vs baseT 2.6934: True
E2k500T: P4 INJgas9 quality 0.6990 vs baseT 0.6973: True
E10bT: P1 pre-drift FP 2 vs baseT 12 (need <=3.6, baseT>=10): True | P2 excess@3000 2.5 vs baseT 1.8 (need >=1.6): True
E10bT: P3 SYN2g45-B FP@3000 22 vs baseT 86 (need <=43.0: True) | excess@3000 94.9 vs baseT 58.5 (need >=52.7): True -> True
E10bT: P3 SYN2g45-MC FP@3000 10 vs baseT 83 (need <=41.5: True) | excess@3000 53.9 vs baseT 34.3 (need >=30.9): True -> True
E10bT: P3 SYN2g45-REG FP@3000 15 vs baseT 23 (need <=11.5: False) | excess@3000 94.1 vs baseT 78.5 (need >=70.6): True -> False
E10bT: P4 SYN2g45-B quality 0.9549 vs baseT 0.9515: True
E10bT: P4 SYN2g45-MC quality 0.7363 vs baseT 0.7159: True
E10bT: P4 SYN2g45-REG quality 2.6835 vs baseT 2.6934: True
E10bT: P4 INJgas9 quality 0.6983 vs baseT 0.6973: True

## B verdicts (vs baseT, recall = excess hits; P1 None = not evaluable, then left out)
E12 verdict E2k500T: classification HOLDS; regression HOLDS
E12 verdict E10bT: classification HOLDS; regression does NOT hold

## C: replacement (E10bT replaces E2k500T where it holds and has at least E2k500T's excess hits)
classification: E10bT holds True | excess E10bT 151.3 vs E2k500T 114.3 -> E10bT REPLACES E2k500T
regression: E10bT holds False | excess E10bT 94.1 vs E2k500T 87.7 -> keep E2k500T

E10bT confirmations 318, of which the leader guard fired the drift: 164
max reference age:
arm          E10bT  E2k500T
group                      
INJgas9      13709    13709
SYN2g45-B    48415    92132
SYN2g45-MC   18444    95556
SYN2g45-REG  44556    61567

hits per E2k500T reference age at drift onset:
       baseT  E2k500T  E10bT    n
bin                              
<10k      94      102    103  129
>=10k    145      112    161  181
