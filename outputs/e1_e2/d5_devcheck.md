## R1: real regression streams (A3), guard on vs A3's stored runs
data set       lr   arm                MAE    max |res|  wild  conf  rise
REALreg-bike   hfr  E10bFT           61.89        503.1     0     7     4
REALreg-bike   hfr  E10bFTC          61.89        503.1     0     7     4
REALreg-bike   hfr  E2k500T          59.97        579.3     0     6     4
REALreg-bike   hfr  E2k500TC         59.97        579.3     0     6     4
REALreg-bike   hfr  baseT            60.67          551     0     5     3
REALreg-bike   hfr  baseTC           60.67          551     0     5     3
REALreg-bike   htr  E10bFT           74.03          678     0     5     3
REALreg-bike   htr  E10bFTC          74.03          678     0     5     3
REALreg-bike   htr  E2k500T          73.36        662.2     0     6     3
REALreg-bike   htr  E2k500TC         73.36        662.2     0     6     3
REALreg-bike   htr  baseT            74.32        572.8     0     5     3
REALreg-bike   htr  baseTC           74.32        572.8     0     5     3
REALreg-metro  hfr  E10bFT        1.88e+09    8.962e+13    43    17     5
REALreg-metro  hfr  E10bFTC           1568         5475     0    19     7
REALreg-metro  hfr  E2k500T      3.286e+06    3.947e+10    10     4     2
REALreg-metro  hfr  E2k500TC          1556         5370     0    14     4
REALreg-metro  hfr  baseT         4.94e+06      1.3e+11     6     6     1
REALreg-metro  hfr  baseTC            1570         7663     0    24     3
REALreg-metro  htr  E10bFT            1676         5187     0    18     4
REALreg-metro  htr  E10bFTC           1676         5187     0    18     4
REALreg-metro  htr  E2k500T           1678         5153     0    10     0
REALreg-metro  htr  E2k500TC          1678         5153     0    10     0
REALreg-metro  htr  baseT             1687         5376     0    23     3
REALreg-metro  htr  baseTC            1687         5376     0    23     3

R1a steps with |residual| > 2 x target range under the guard: 0 (without it: 59) -> blow-up GONE
R1b REALreg-bike   MAE E10bFTC 67.962 vs baseTC 67.498 (ratio 1.007, need <=1.02): True | E2k500TC 66.666 (ratio 0.988) | R1c confirmations E10bFTC 12 vs baseTC 10 (<= half: False), E2k500TC 12
R1b REALreg-metro  MAE E10bFTC 1621.786 vs baseTC 1628.493 (ratio 0.996, need <=1.02): True | E2k500TC 1616.899 (ratio 0.993) | R1c confirmations E10bFTC 37 vs baseTC 47 (<= half: False), E2k500TC 24
R1c share of confirmations with rr >= 1.1: baseTC 12/57 = 0.21, E2k500TC 11/36 = 0.31, E10bFTC 18/49 = 0.37

## R2: E13's regression streams with the guard on
## A0(a) longest warning->confirmation age: 928 -> VALID

## Per group (3000-step windows; quality = accuracy, MAE for SYN2g69-REG; preFP only read on injected groups)
group        arm        N    TP    FP   excess  preFP   delay   quality
SYN2g69-REG  baseT    236   191    48    175.5      5     938    2.8084
SYN2g69-REG  E2k500T  236   201    15    195.2      2     736    2.7755
SYN2g69-REG  E10bFT   236   203    15    197.1      2     727    2.7759
SYN2g69-REG  baseTC   236   191    48    175.5      5     938    2.8084
SYN2g69-REG  E2k500TC  236   201    15    195.2      2     736    2.7755
SYN2g69-REG  E10bFTC  236   203    15    197.1      2     727    2.7759

E10bFTC: P3 SYN2g69-REG FP@3000 15 vs baseTC 48 (need <=24.0: True) | excess 197.1 vs 175.5 (need >=158.0): True
E10bFTC: P4 SYN2g69-REG quality 2.7759 vs baseTC 2.8084: True
R2a E10bFTC holds vs baseTC: True | excess E10bFTC 197.1 vs E2k500TC 195.2 -> E13's main decision UNCHANGED under the guard
R2b baseTC    runs identical to baseT    32 of 32 (htr 16, hfr 16) | TP +0 FP +0 excess +0.0 MAE +0.0000
R2b E2k500TC  runs identical to E2k500T  32 of 32 (htr 16, hfr 16) | TP +0 FP +0 excess +0.0 MAE +0.0000
R2b E10bFTC   runs identical to E10bFT   32 of 32 (htr 16, hfr 16) | TP +0 FP +0 excess +0.0 MAE +0.0000

D5 conclusion: R1a, R1b and R2a hold -> the guard is the SUGGESTED setting for the regression learners (development evidence only; adoption needs unused real regression data)
