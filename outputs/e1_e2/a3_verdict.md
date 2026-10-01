## A0 longest warning->confirmation age: 928 -> VALID

## Per run (MAE after warm-up; rise = confirmations with rr >= 1.1; guard = fired by the leader guard)
data set       arm      lr    steps        MAE  conf  rise  guard  max age
REALreg-bike   E10bFT   hfr   17179     61.893     7     4      1     3967
REALreg-bike   E2k500T  hfr   17179     59.972     6     4      0     4415
REALreg-bike   baseT    hfr   17179     60.672     5     3      0        0
REALreg-bike   E10bFT   htr   17179     74.030     5     3      2     4863
REALreg-bike   E2k500T  htr   17179     73.360     6     3      0     4991
REALreg-bike   baseT    htr   17179     74.324     5     3      0        0
REALreg-metro  E10bFT   hfr   48004 1879752789.454    17     5      5    11315
REALreg-metro  E2k500T  hfr   48004 3285584.302     4     2      0    43127
REALreg-metro  baseT    hfr   48004 4940491.586     6     1      0        0
REALreg-metro  E10bFT   htr   48004   1675.600    18     4      9     5215
REALreg-metro  E2k500T  htr   48004   1677.759    10     0      0    12735
REALreg-metro  baseT    htr   48004   1687.254    23     3      0        0

## Q1 quality guard and Q2 confirmations, per data set (MAE = mean of the two learners)
REALreg-bike   Q1 MAE E10bFT 67.962 vs baseT 67.498 (ratio 1.007, need <=1.02): True | E2k500T 66.666 (ratio 0.988) | Q2 confirmations E10bFT 12 vs baseT 10 (need <=5.0): False | E2k500T 12
REALreg-metro  Q1 MAE E10bFT 939877232.527 vs baseT 2471089.420 (ratio 380.349, need <=1.02): False | E2k500T 1643631.030 (ratio 0.665) | Q2 confirmations E10bFT 35 vs baseT 29 (need <=14.5): False | E2k500T 14

## Q3 share of confirmations preceded by a real residual rise (rr >= 1.1), both data sets pooled
baseT    10 of 39 = 0.26
E2k500T  9 of 26 = 0.35
E10bFT   16 of 47 = 0.34
Q3 E10bFT >= baseT: True

A3 conclusion: boundary condition -- Q1 fails on REALreg-metro
