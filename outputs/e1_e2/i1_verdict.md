## A0 longest warning->confirmation age: 960 -> VALID

## S3 per stream (3000-step windows; I1-inc has no GT, its confirmations are not FPs)
learner   stream         arm         N   TP@1k   TP@3k   FP@3k  excess  conf  guard  delay  maxage  paused accuracy
hf10sqrt  I1-abrupt      baseT       5       5       4      14     0.7    23      0     78       0    2272   0.6929
hf10sqrt  I1-abrupt      E2k500T     5       4       4       4     2.7     8      0     47   13634     616   0.6630
hf10sqrt  I1-abrupt      E10bFT      5       4       4       7     2.0    13     11     23   12639    1488   0.6974
hf10sqrt  I1-incabrupt   baseT       2       2       2      32     0.5    37      0     25       0    3909   0.7231
hf10sqrt  I1-incabrupt   E2k500T     2       2       2      19     0.9    24      0     26    6943    2209   0.7243
hf10sqrt  I1-incabrupt   E10bFT      2       2       2      22     0.8    26      9     20    6988    2317   0.7218
hf10sqrt  I1-increc      baseT       2       2       2      30     0.6    40      0     25       0    6472   0.7251
hf10sqrt  I1-increc      E2k500T     2       2       2      17     1.0    21      0     20   11775    2686   0.7229
hf10sqrt  I1-increc      E10bFT      2       2       2      19     0.9    25     11     27    7167    1996   0.7278
hf10sqrt  I1-incgrad     baseT       1       1       1      11     0.2    13      0     59       0    2751   0.7031
hf10sqrt  I1-incgrad     E2k500T     1       1       1       7     0.4     8      0     20    8575    1192   0.7221
hf10sqrt  I1-incgrad     E10bFT      1       1       1      10     0.2    11      4     20    8575    1323   0.7142
hf10sqrt  I1-inc         baseT       0       0       0       7     0.0     7      0    nan       0    1712   0.6088
hf10sqrt  I1-inc         E2k500T     0       0       0       4     0.0     4      0    nan   30853    3467   0.6081
hf10sqrt  I1-inc         E10bFT      0       0       0       6     0.0     6      2    nan   22911    2530   0.6076
ht        I1-abrupt      baseT       5       4       4      12     1.0    24      0     73       0    4348   0.6360
ht        I1-abrupt      E2k500T     5       4       4       3     3.0     7      0     43   13621    2366   0.6154
ht        I1-abrupt      E10bFT      5       4       4       7     2.0    14      8     64   13023    3488   0.6473
ht        I1-incabrupt   baseT       2       2       2      26     0.7    33      0     46       0    5555   0.6608
ht        I1-incabrupt   E2k500T     2       2       2      17     1.0    22      0     32    7231    2495   0.6472
ht        I1-incabrupt   E10bFT      2       2       2      29     0.6    35     18     20    6271    4172   0.6619
ht        I1-increc      baseT       2       2       2      40     0.4    45      0    153       0    6824   0.6669
ht        I1-increc      E2k500T     2       2       2      18     1.0    21      0     42   16159    3687   0.6626
ht        I1-increc      E10bFT      2       2       2      22     0.8    26     10     17   12543    3788   0.6732
ht        I1-incgrad     baseT       1       1       1      17     0.1    18      0     91       0    1339   0.6352
ht        I1-incgrad     E2k500T     1       0       0       6    -0.6     6      0    nan    8703     166   0.6499
ht        I1-incgrad     E10bFT      1       1       1      12     0.2    13     10     46    8447    2476   0.6645
ht        I1-inc         baseT       0       0       0       5     0.0     5      0    nan       0    2263   0.5455
ht        I1-inc         E2k500T     0       0       0       6     0.0     6      0    nan   28127     742   0.5635
ht        I1-inc         E10bFT      0       0       0       5     0.0     5      3    nan   26527    1262   0.5667

## Main reading (hf10sqrt; FP and excess pooled over the 4 streams with GT)
FP@3000 {'baseT': 87, 'E2k500T': 47, 'E10bFT': 58} | excess {'baseT': 2.1, 'E2k500T': 5.0, 'E10bFT': 3.9}
R3a FP E2k500T 47 vs baseT 87 (need <=43.5): False
R3b excess E2k500T 5.0 vs baseT 2.1 (need >=1.9): True
R3c accuracy >= baseT - 0.01 on all five: NO: I1-abrupt
-> C3: NOT reproduced (R3a False, R3b True); accuracy cost on I1-abrupt
R4a stale reference on abrupt: E2k500T 0.6630 vs baseT 0.6929 - 0.01: True
R4b E10bFT abrupt 0.6974 >= baseT - 0.01 (0.6829): guard FIXED the stale reference
R4c FP E10bFT 58 vs baseT 87 (need <=43.5: False) | excess 3.9 vs E2k500T 5.0 (need >=4.5): False
R4d accuracy E10bFT >= E2k500T - 0.01 on the other four: yes
R-all E10bFT vs baseT: FP False, excess 3.9 vs 2.1 (need >=1.9): True, accuracy ok on all five

## S1 single tree (ht; FP and excess pooled over the 4 streams with GT)
FP@3000 {'baseT': 95, 'E2k500T': 44, 'E10bFT': 70} | excess {'baseT': 2.2, 'E2k500T': 4.4, 'E10bFT': 3.6}
R3a FP E2k500T 44 vs baseT 95 (need <=47.5): True
R3b excess E2k500T 4.4 vs baseT 2.2 (need >=2.0): True
R3c accuracy >= baseT - 0.01 on all five: NO: I1-abrupt, I1-incabrupt
-> C3: frozen reference (with k=500) reproduced on INSECTS: FP halved, recall kept; accuracy cost on I1-abrupt, I1-incabrupt
R4a stale reference on abrupt: E2k500T 0.6154 vs baseT 0.6360 - 0.01: True
R4b E10bFT abrupt 0.6473 >= baseT - 0.01 (0.6260): guard FIXED the stale reference
R4c FP E10bFT 70 vs baseT 95 (need <=47.5: False) | excess 3.6 vs E2k500T 4.4 (need >=3.9): False
R4d accuracy E10bFT >= E2k500T - 0.01 on the other four: yes
R-all E10bFT vs baseT: FP False, excess 3.6 vs 2.2 (need >=2.0): True, accuracy ok on all five

## S2 timeout effect vs A1 (no timeout, hf10sqrt): accuracy / FP@3000 / confirmations
I1-abrupt      base   0.6919 /  14 /  24   baseT   0.6929 /  14 /  23
I1-abrupt      E2k500 0.6630 /   4 /   8   E2k500T 0.6630 /   4 /   8
I1-incabrupt   base   0.7137 /  30 /  35   baseT   0.7231 /  32 /  37
I1-incabrupt   E2k500 0.7243 /  19 /  24   E2k500T 0.7243 /  19 /  24
I1-increc      base   0.7263 /  32 /  42   baseT   0.7251 /  30 /  40
I1-increc      E2k500 0.7257 /  20 /  23   E2k500T 0.7229 /  17 /  21
I1-incgrad     base   0.7123 /  12 /  14   baseT   0.7031 /  11 /  13
I1-incgrad     E2k500 0.7190 /   7 /   8   E2k500T 0.7221 /   7 /   8
I1-inc         base   0.6077 /   8 /   8   baseT   0.6088 /   7 /   7
I1-inc         E2k500 0.6009 /   7 /   7   E2k500T 0.6081 /   4 /   4

## S4 reference age at each GT point (descriptive; hit = a confirmation within 3000 steps)
hf10sqrt  I1-abrupt      E2k500T  14352:hit 469  19500:hit 1003  33240:hit 3217  38682:hit 161  39510:MISS 297
hf10sqrt  I1-abrupt      E10bFT   14352:hit 1013  19500:hit 1617  33240:hit 4573  38682:hit 64  39510:MISS 296
hf10sqrt  I1-incabrupt   E2k500T  26568:hit 2875  53364:hit 2799
hf10sqrt  I1-incabrupt   E10bFT   26568:hit 2932  53364:hit 2843
hf10sqrt  I1-increc      E2k500T  26568:hit 2894  53364:hit 169
hf10sqrt  I1-increc      E10bFT   26568:hit 2964  53364:hit 354
hf10sqrt  I1-incgrad     E2k500T  14028:hit 108
hf10sqrt  I1-incgrad     E10bFT   14028:hit 108
hf10sqrt  abrupt E2k500T  last freeze t=39214, then 13633 steps: leader err 0.332, reference err 0.385
hf10sqrt  abrupt E10bFT   last freeze t=52546, then 301 steps: leader err 0.000, reference err 0.000
ht        I1-abrupt      E2k500T  14352:hit 629  19500:hit 971  33240:hit 13156  38682:hit 180  39510:MISS 284
ht        I1-abrupt      E10bFT   14352:hit 629  19500:hit 1649  33240:hit 4554  38682:hit 154  39510:MISS 290
ht        I1-incabrupt   E2k500T  26568:hit 2523  53364:hit 2722
ht        I1-incabrupt   E10bFT   26568:hit 2510  53364:hit 2792
ht        I1-increc      E2k500T  26568:hit 2587  53364:hit 15
ht        I1-increc      E10bFT   26568:hit 2414  53364:hit 303
ht        I1-incgrad     E2k500T  14028:MISS 31
ht        I1-incgrad     E10bFT   14028:hit 82
ht        abrupt E2k500T  last freeze t=39227, then 13620 steps: leader err 0.385, reference err 0.455
ht        abrupt E10bFT   last freeze t=52603, then 244 steps: leader err 0.000, reference err 0.000
