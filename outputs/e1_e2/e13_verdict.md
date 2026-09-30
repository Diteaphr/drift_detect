## A0(a) longest warning->confirmation age: 992 -> VALID

## Per group (3000-step windows; quality = accuracy, MAE for SYN2g69-REG; preFP only read on injected groups)
group        arm        N    TP    FP   excess  preFP   delay   quality
SYN2g67-B    baseT    138    97    67     70.6     12     733    0.9491
SYN2g67-B    E1T      138    83    14     77.1      1     688    0.9486
SYN2g67-B    E10bT    138   100    17     92.7      2     778    0.9516
SYN2g67-MC   baseT     63    62   103     32.2     10     346    0.7050
SYN2g67-MC   E1T       63    54     1     53.8      1     490    0.7362
SYN2g67-MC   E10bT     63    61     8     58.3      1     462    0.7268
SYN2g69-REG  baseT    236   191    48    175.5      5     938    2.8084
SYN2g69-REG  E1T      236   140    33    128.9      0     619    2.7783
SYN2g69-REG  E2k500T  236   201    15    195.2      2     736    2.7755
SYN2g69-REG  E10bT    236   203    34    191.0      2     685    2.7798
SYN2g69-REG  E10bFT   236   203    15    197.1      2     727    2.7759
INJelec35    baseT     48    32    59     27.0     49    1359    0.7762
INJelec35    E1T       48    11     7     10.4      5     356    0.7745
INJelec35    E10bT     48    25    17     23.6     11    1062    0.7762
INJcov01     baseT     16     2    24      1.1     16    1352    0.7028
INJcov01     E1T       16     0     5     -0.2      0     nan    0.7035
INJcov01     E10bT     16     3     8      2.7      4    1532    0.7031

## B: each arm vs baseT (recall = excess hits)
E1T: P1 INJelec35 pre-drift FP 5 vs baseT 49 (need <=14.7: True) | P2 excess 10.4 vs 27.0 (need >=24.3): False
E1T: P1 INJcov01 pre-drift FP 0 vs baseT 16 (need <=4.8: True) | P2 excess -0.2 vs 1.1 (need >=1.0): False
E1T: P3 SYN2g67-B FP@3000 14 vs baseT 67 (need <=33.5: True) | excess 77.1 vs 70.6 (need >=63.6): True
E1T: P3 SYN2g67-MC FP@3000 1 vs baseT 103 (need <=51.5: True) | excess 53.8 vs 32.2 (need >=29.0): True
E1T: P4 SYN2g67-B quality 0.9486 vs baseT 0.9491: True
E1T: P4 SYN2g67-MC quality 0.7362 vs baseT 0.7050: True
E1T: P4 INJelec35 quality 0.7745 vs baseT 0.7762: True
E1T: P4 INJcov01 quality 0.7035 vs baseT 0.7028: True
E10bT: P1 INJelec35 pre-drift FP 11 vs baseT 49 (need <=14.7: True) | P2 excess 23.6 vs 27.0 (need >=24.3): False
E10bT: P1 INJcov01 pre-drift FP 4 vs baseT 16 (need <=4.8: True) | P2 excess 2.7 vs 1.1 (need >=1.0): True
E10bT: P3 SYN2g67-B FP@3000 17 vs baseT 67 (need <=33.5: True) | excess 92.7 vs 70.6 (need >=63.6): True
E10bT: P3 SYN2g67-MC FP@3000 8 vs baseT 103 (need <=51.5: True) | excess 58.3 vs 32.2 (need >=29.0): True
E10bT: P4 SYN2g67-B quality 0.9516 vs baseT 0.9491: True
E10bT: P4 SYN2g67-MC quality 0.7268 vs baseT 0.7050: True
E10bT: P4 INJelec35 quality 0.7762 vs baseT 0.7762: True
E10bT: P4 INJcov01 quality 0.7031 vs baseT 0.7028: True
E1T: P3 SYN2g69-REG FP@3000 33 vs baseT 48 (need <=24.0: False) | excess 128.9 vs 175.5 (need >=158.0): False
E1T: P4 SYN2g69-REG quality 2.7783 vs baseT 2.8084: True
E2k500T: P3 SYN2g69-REG FP@3000 15 vs baseT 48 (need <=24.0: True) | excess 195.2 vs 175.5 (need >=158.0): True
E2k500T: P4 SYN2g69-REG quality 2.7755 vs baseT 2.8084: True
E10bT: P3 SYN2g69-REG FP@3000 34 vs baseT 48 (need <=24.0: False) | excess 191.0 vs 175.5 (need >=158.0): True
E10bT: P4 SYN2g69-REG quality 2.7798 vs baseT 2.8084: True
E10bFT: P3 SYN2g69-REG FP@3000 15 vs baseT 48 (need <=24.0: True) | excess 197.1 vs 175.5 (need >=158.0): True
E10bFT: P4 SYN2g69-REG quality 2.7759 vs baseT 2.8084: True
E13 verdict E1T: classification does NOT hold; regression does NOT hold
E13 verdict E2k500T: classification -; regression HOLDS
E13 verdict E10bT: classification does NOT hold; regression does NOT hold
E13 verdict E10bFT: classification -; regression HOLDS

## C (main decision): E10bFT holds for regression True | excess E10bFT 197.1 vs E2k500T 195.2 -> E10bFT REPLACES E2k500T for regression
   E10bT holds for classification in E13: False -> conflict with E12 reported; classification stays as E12 decided, no unification claim

## A0(b) guard / reference replay mismatches on regression: 0 -> VALID
E10bT  confirmations 241 | FP 34 (guard 22, catch-up pattern 22) | hits 203 (guard 56, rr>=1.1 49, median guard-hit delay 500)
        FP rr 0.91 0.94 0.96 0.96 0.96 0.97 0.97 0.99 1.00 1.00 1.04 1.05 1.05 1.05 1.06 1.08 1.08 1.10 1.14 1.14 1.14 1.61
E10bFT confirmations 218 | FP 15 (guard 2, catch-up pattern 0) | hits 203 (guard 67, rr>=1.1 63, median guard-hit delay 590)
        FP rr 0.82 1.83
M1 guard FP E10bFT 2 vs E10bT 22 (need <=6.6, E10bT>=5): True
M2 guard hits E10bFT 67 vs E10bT's rr>=1.1 guard hits 49 (need >=34.3): True

## Q: E1T vs E10bT on classification, cost(w) = w * (N - excess) + FP@3000
SYN2g67-B    w=1 74.9/62.3 w=2 135.8/107.6 w=5 318.5/243.4 w=10 623.0/469.9 | E1T <= E10bT at every w: False | E10bT cheaper once w > 0.19
SYN2g67-MC   w=1 10.2/12.7 w=2 19.4/17.3 w=5 46.9/31.4 w=10 92.9/54.7 | E1T <= E10bT at every w: False | E10bT cheaper once w > 1.55
INJelec35    w=1 44.6/41.4 w=2 82.1/65.8 w=5 194.8/138.9 w=10 382.5/260.9 | E1T <= E10bT at every w: False | E10bT cheaper once w > 0.76
INJcov01     w=1 21.2/21.3 w=2 37.4/34.6 w=5 85.9/74.6 w=10 166.9/141.2 | E1T <= E10bT at every w: False | E10bT cheaper once w > 1.05
Q reading: E1T holds for classification False, cheaper at every w in 0 of 4 groups -> E10bT stays the classification main method

## Regression per drift type (4 seeds pooled; cost at w = 1 / 10)
sud   baseT xs 41.2 FP 13 c 32/201 | E1T xs 32.8 FP 11 c 38/283 | E2k500T xs 45.2 FP 6 c 21/154 | E10bT xs 44.1 FP 10 c 26/169 | E10bFT xs 47.8 FP 4 c 16/126
grad  baseT xs 36.5 FP 12 c 33/227 | E1T xs 25.2 FP 8 c 41/336 | E2k500T xs 44.9 FP 2 c 15/133 | E10bT xs 48.9 FP 2 c 11/93 | E10bFT xs 46.8 FP 3 c 14/115
inc   baseT xs 37.6 FP 13 c 27/157 | E1T xs 29.2 FP 3 c 26/231 | E2k500T xs 45.9 FP 4 c 10/65 | E10bT xs 43.6 FP 13 c 21/97 | E10bFT xs 43.4 FP 5 c 14/91
rec   baseT xs 60.3 FP 10 c 16/67 | E1T xs 41.7 FP 11 c 35/254 | E2k500T xs 59.1 FP 3 c 10/72 | E10bT xs 54.3 FP 9 c 21/126 | E10bFT xs 59.1 FP 3 c 10/72

max reference age (regression): {'E10bFT': 42815, 'E10bT': 38847, 'E2k500T': 38847}
regression hits per E2k500T reference age at drift onset:
       baseT  E1T  E2k500T  E10bT  E10bFT    n
bin                                           
<10k      78   61       84     84      86   95
>=10k    113   79      117    119     117  141
