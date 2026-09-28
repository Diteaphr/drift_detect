## E9: official-ECPF detectors (classification families)
family   arm      FP@1000  TP@1000  FP@3000  TP@3000    delay  accuracy
B        base          11        6        6        9     1105    0.9551
B        E1             3        4        0        7     1540    0.9529
B        E2k500         7        5        6        6      738    0.9547
B        E9d           17       11       12       12      394    0.9495
B        E9h            2        2        0        4     5972    0.9550
MC-syn   base          48       35       21       39       98    0.7708
MC-syn   E1             5       37        4       37       83    0.7924
MC-syn   E2k500         5       37        1       38      108    0.7874
MC-syn   E9d           16       35       16       35       35    0.7812
MC-syn   E9h            3       40        3       40       20    0.8079
MC-RBF   base          24       22       18       20      692    0.6863
MC-RBF   E1             0       14        0       13      273    0.7091
MC-RBF   E2k500         3       21        1       20     1124    0.7007
MC-RBF   E9d            1       13        1       13      158    0.7014
MC-RBF   E9h            0       12        0       12      100    0.7093
MC-RBF gradual hits @1000: {'base': 10, 'E1': 5, 'E2k500': 11, 'E9d': 1, 'E9h': 0}
E9d: P1 FP@1000 34 vs base 83 (need <=41.5): True | P2 MC-RBF gradual hits 1 (need <=8): True
E9h: P1 FP@1000 5 vs base 83 (need <=41.5): True | P2 MC-RBF gradual hits 0 (need <=8): True
E9 verdict: CLAIM SUPPORTED: switching the detector algorithm does not fix the masked gradual drifts
