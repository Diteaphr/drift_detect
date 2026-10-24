## I2 A0 longest warning->confirmation age: 992 -> VALID
## I1+L A0 longest warning->confirmation age: 992 -> VALID

# Part A: three-arm ablation on the synthetic multiclass streams (40 streams, 3000-step windows)

## Main reading (hf10sqrt)
type                   arm         N    TP    FP   excess accuracy
gradual (10)           baseT      79    79   135     36.3   0.6929
gradual (10)           E2k500T    79    73    10     68.6   0.7218
gradual (10)           E10bFT     79    77    11     72.4   0.7210
incremental (10)       baseT      76    75   121     37.0   0.6947
incremental (10)       E2k500T    76    72     8     68.9   0.7247
incremental (10)       E10bFT     76    73    11     67.7   0.7213
sudden (10)            baseT      76    75   137     42.8   0.6959
sudden (10)            E2k500T    76    68     7     65.9   0.7251
sudden (10)            E10bFT     76    73     4     71.8   0.7260
recurring_gradual (5)  baseT      31    31    32     22.1   0.7643
recurring_gradual (5)  E2k500T    31    18     8     15.6   0.7762
recurring_gradual (5)  E10bFT     31    31     6     29.0   0.7692
recurring_incremental (2) baseT      17    16    15     10.1   0.7524
recurring_incremental (2) E2k500T    17    14     3     12.6   0.7357
recurring_incremental (2) E10bFT     17    17     2     16.1   0.7342
recurring_sudden (3)   baseT      24    23    13     19.1   0.7776
recurring_sudden (3)   E2k500T    24    23     4     21.8   0.7740
recurring_sudden (3)   E10bFT     24    22     7     19.6   0.7833
all (40)               baseT     303   299   453    167.4   0.7123
all (40)               E2k500T   303   268    40    253.4   0.7348
all (40)               E10bFT    303   293    41    276.6   0.7337
R3a FP E2k500T 40 vs baseT 453 (need <=226.5): True
R3b excess E2k500T 253.4 vs baseT 167.4 (need >=150.7): True
R3c mean accuracy E2k500T 0.7348 vs baseT 0.7123 - 0.01: True
-> C3: frozen reference (with k=500) reproduced: FP halved, recall kept
R4c FP E10bFT 41 vs baseT 453 (need <=226.5: True) | excess 276.6 vs E2k500T 253.4 (need >=228.1): True
R4e excess E10bFT 276.6 > E2k500T 253.4: True
R4d mean accuracy E10bFT 0.7337 vs E2k500T 0.7348 - 0.01: True
-> C4: leader guard raises recall and keeps the frozen reference's FP cut
R-all E10bFT vs baseT: FP True, excess 276.6 vs 167.4 (need >=150.7): True, accuracy 0.7337 vs 0.7123: True
GT points by E2k500T reference age (hit = confirmation within 3000 steps): <2k N 18: baseT 18, E2k500T 18, E10bFT 18; 2-10k N 131: baseT 129, E2k500T 122, E10bFT 131; >=10k N 154: baseT 153, E2k500T 130, E10bFT 153

## S1 single tree (ht)
type                   arm         N    TP    FP   excess accuracy
gradual (10)           baseT      79    77    40     60.7   0.5934
gradual (10)           E2k500T    79    70     9     66.0   0.6020
gradual (10)           E10bFT     79    79     5     76.7   0.6057
incremental (10)       baseT      76    73    40     59.1   0.6061
incremental (10)       E2k500T    76    74     6     71.8   0.6202
incremental (10)       E10bFT     76    75    11     70.8   0.6192
sudden (10)            baseT      76    75    50     61.9   0.6099
sudden (10)            E2k500T    76    65     8     62.6   0.6155
sudden (10)            E10bFT     76    76     6     74.2   0.6228
recurring_gradual (5)  baseT      31    31    16     26.6   0.6500
recurring_gradual (5)  E2k500T    31    26     4     24.5   0.6575
recurring_gradual (5)  E10bFT     31    31     3     29.7   0.6491
recurring_incremental (2) baseT      17    16    11     11.3   0.6237
recurring_incremental (2) E2k500T    17    17     2     16.1   0.6532
recurring_incremental (2) E10bFT     17    17     2     16.1   0.6312
recurring_sudden (3)   baseT      24    24     9     21.1   0.6558
recurring_sudden (3)   E2k500T    24    24     1     23.8   0.6470
recurring_sudden (3)   E10bFT     24    22     3     21.1   0.6687
all (40)               baseT     303   296   166    240.7   0.6139
all (40)               E2k500T   303   276    30    264.8   0.6228
all (40)               E10bFT    303   300    30    288.6   0.6248
R3a FP E2k500T 30 vs baseT 166 (need <=83.0): True
R3b excess E2k500T 264.8 vs baseT 240.7 (need >=216.7): True
R3c mean accuracy E2k500T 0.6228 vs baseT 0.6139 - 0.01: True
-> C3: frozen reference (with k=500) reproduced: FP halved, recall kept
R4c FP E10bFT 30 vs baseT 166 (need <=83.0: True) | excess 288.6 vs E2k500T 264.8 (need >=238.3): True
R4e excess E10bFT 288.6 > E2k500T 264.8: True
R4d mean accuracy E10bFT 0.6248 vs E2k500T 0.6228 - 0.01: True
-> C4: leader guard raises recall and keeps the frozen reference's FP cut
R-all E10bFT vs baseT: FP True, excess 288.6 vs 240.7 (need >=216.7): True, accuracy 0.6248 vs 0.6139: True
GT points by E2k500T reference age (hit = confirmation within 3000 steps): <2k N 12: baseT 12, E2k500T 12, E10bFT 12; 2-10k N 124: baseT 119, E2k500T 120, E10bFT 124; >=10k N 167: baseT 163, E2k500T 147, E10bFT 167

# Part W: training during warnings (XL vs X, paired per stream and learner)

## synthetic multiclass (40), Main reading (hf10sqrt; FP and excess over the 40 streams with GT)
W(baseT): accuracy delta mean +0.0042, 20 up / 20 down of 40 -> tied | FP 453 -> 482 (need <=498.3: True), excess 167.4 -> 163.2 (need >=150.7: True) -> detection unaffected
        confirmations 1058 -> 1108, guard-fired 0 -> 0, warning-open steps 252311 -> 215364
  -> L can be added to baseT (seen data)
W(E2k500T): accuracy delta mean +0.0018, 19 up / 21 down of 40 -> tied | FP 40 -> 57 (need <=44.0: False), excess 253.4 -> 257.3 (need >=228.1: True) -> detection AFFECTED
        confirmations 319 -> 349, guard-fired 0 -> 0, warning-open steps 94416 -> 104225
  -> L NOT adoptable on E2k500T
W(E10bFT): accuracy delta mean +0.0038, 25 up / 15 down of 40 -> raised | FP 41 -> 45 (need <=45.1: True), excess 276.6 -> 277.0 (need >=249.0: True) -> detection unaffected
        confirmations 358 -> 371, guard-fired 232 -> 224, warning-open steps 120322 -> 117613
  -> L can be added to E10bFT (seen data)

## synthetic multiclass (40), S1 single tree (ht; FP and excess over the 40 streams with GT)
W(baseT): accuracy delta mean +0.0039, 26 up / 14 down of 40 -> raised | FP 166 -> 179 (need <=182.6: True), excess 240.7 -> 235.8 (need >=216.7: True) -> detection unaffected
        confirmations 657 -> 681, guard-fired 0 -> 0, warning-open steps 160222 -> 161428
  -> L can be added to baseT (seen data)
W(E2k500T): accuracy delta mean +0.0017, 24 up / 15 down of 40 -> tied | FP 30 -> 22 (need <=33.0: True), excess 264.8 -> 267.9 (need >=238.3: True) -> detection unaffected
        confirmations 313 -> 306, guard-fired 0 -> 0, warning-open steps 70119 -> 69468
  -> L can be added to E2k500T (seen data)
W(E10bFT): accuracy delta mean +0.0065, 29 up / 10 down of 40 -> raised | FP 30 -> 28 (need <=33.0: True), excess 288.6 -> 287.7 (need >=259.8: True) -> detection unaffected
        confirmations 350 -> 341, guard-fired 203 -> 184, warning-open steps 76018 -> 87753
  -> L can be added to E10bFT (seen data)

## INSECTS (5), Main reading (hf10sqrt; FP and excess over the 4 streams with GT)
W(baseT): accuracy delta mean +0.0021, 3 up / 2 down of 5 -> raised | FP 87 -> 81 (need <=95.7: True), excess 2.1 -> 2.8 (need >=1.9: True) -> detection unaffected
        confirmations 120 -> 109, guard-fired 0 -> 0, warning-open steps 17116 -> 18138
  -> L can be added to baseT (seen data)
W(E2k500T): accuracy delta mean +0.0071, 3 up / 2 down of 5 -> raised | FP 47 -> 49 (need <=51.7: True), excess 5.0 -> 4.3 (need >=4.5: False) -> detection AFFECTED
        confirmations 65 -> 66, guard-fired 0 -> 0, warning-open steps 10170 -> 8749
  -> L NOT adoptable on E2k500T
W(E10bFT): accuracy delta mean +0.0043, 4 up / 1 down of 5 -> raised | FP 58 -> 57 (need <=63.8: True), excess 3.9 -> 4.2 (need >=3.5: True) -> detection unaffected
        confirmations 81 -> 79, guard-fired 37 -> 34, warning-open steps 9654 -> 11236
  -> L can be added to E10bFT (seen data)

## INSECTS (5), S1 single tree (ht; FP and excess over the 4 streams with GT)
W(baseT): accuracy delta mean +0.0056, 4 up / 1 down of 5 -> raised | FP 95 -> 94 (need <=104.5: True), excess 2.2 -> 2.2 (need >=2.0: True) -> detection unaffected
        confirmations 125 -> 124, guard-fired 0 -> 0, warning-open steps 20329 -> 24374
  -> L can be added to baseT (seen data)
W(E2k500T): accuracy delta mean -0.0020, 0 up / 4 down of 5 -> lowered | FP 44 -> 46 (need <=48.4: True), excess 4.4 -> 4.3 (need >=3.9: True) -> detection unaffected
        confirmations 62 -> 65, guard-fired 0 -> 0, warning-open steps 9456 -> 9194
  -> L NOT adoptable on E2k500T
W(E10bFT): accuracy delta mean +0.0013, 4 up / 1 down of 5 -> tied | FP 70 -> 71 (need <=77.0: True), excess 3.6 -> 3.5 (need >=3.2: True) -> detection unaffected
        confirmations 93 -> 94, guard-fired 49 -> 49, warning-open steps 15186 -> 11861
  -> L can be added to E10bFT (seen data)
