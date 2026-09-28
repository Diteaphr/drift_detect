## A1 injected electricity (24 streams x ht, hf10; one drift per stream)
method arm      preFP  TP@1000  TP@3000  FP@1000  FP@3000    delay  accuracy
cp    base        21        0        3       30       27     1209    0.7623
cp    E1           4        0        0        4        4      nan    0.7597
cp    E2k500       4        3       10       12        5     1342    0.7636
ls    base        14        6       10       19       15     1136    0.8279
ls    E1           3        5        6        4        3      832    0.8222
ls    E2k500       5        5        8        9        6     1216    0.8174
fp    base        16        3        6       27       22      956    0.7425
fp    E1           4        3        7        8        4     1222    0.7434
fp    E2k500       5        5        8       10        7      999    0.7440
ff    base        19        0        1       25       24     3445    0.7535
ff    E1           1        0        0        1        1      nan    0.7537
ff    E2k500       1        1        2        6        5     1560    0.7544
pooled: pre-drift FP {'base': 70, 'E1': 12, 'E2k500': 15} | TP@3000 {'base': 20, 'E1': 13, 'E2k500': 28} | gradual TP@3000 {'base': 10, 'E1': 6, 'E2k500': 14} | accuracy {'base': 0.7715, 'E1': 0.7698, 'E2k500': 0.7699}
E1: P1 pre-drift FP 12 vs base 70 (need <=21.0, base>=10): True | P2 TP@3000 13 vs base 20 (need >=18.0): False
E2k500: P1 pre-drift FP 15 vs base 70 (need <=21.0, base>=10): True | P2 TP@3000 28 vs base 20 (need >=18.0): True
P3 gradual TP@3000 E2k500 14 vs E1 6 -> True

## A1 INSECTS (hf10 masked)
variant    arm      FP@1000  TP@1000  FP@3000  TP@3000  accuracy
abrupt     base          16        5       14        4    0.6919
abrupt     E1             6        4        5        4    0.6951
abrupt     E2k500         4        4        4        4    0.6630
incabrupt  base          30        2       30        2    0.7137
incabrupt  E1            18        2       18        2    0.7145
incabrupt  E2k500        19        2       19        2    0.7243
increc     base          35        2       32        2    0.7263
increc     E1            14        2       13        2    0.7252
increc     E2k500        20        2       20        2    0.7257
incgrad    base          12        1       12        1    0.7123
incgrad    E1             6        0        6        0    0.7161
incgrad    E2k500         7        1        7        1    0.7190
inc        base           8        0        8        0    0.6077
inc        E1             4        0        4        0    0.6106
inc        E2k500         7        0        7        0    0.6009
P4 INSECTS abrupt: E2k500 FP@3000 4 vs base 14, TP@3000 4 vs E1 4 -> True (supporting evidence only)

A1 verdict: E2-k500 HOLDS on new data; E1 does NOT hold on new data
