## E11 pooled per group (3000-step windows; missed = N - excess; cost = w * missed + FP)
group        arm         N   TP   FP  excess  missed   cost@1   cost@2   cost@5  cost@10
SYN2g23-B    base      118   79   86    51.3    66.7    152.7    219.4    419.5    752.9
SYN2g23-B    baseT     118   79   67    56.2    61.8    128.8    190.5    375.8    684.7
SYN2g23-B    E1T       118   72   12    68.3    49.7     61.7    111.5    260.7    509.4
SYN2g23-B    E2k500T   118   73   14    67.6    50.4     64.4    114.8    266.1    518.2
SYN2g23-MC   base       58   58   99    31.6    26.4    125.4    151.8    231.1    363.1
SYN2g23-MC   baseT      58   57   90    32.1    25.9    115.9    141.8    219.6    349.2
SYN2g23-MC   E1T        58   52    0    52.0     6.0      6.0     12.0     30.0     60.0
SYN2g23-MC   E2k500T    58   54    7    51.1     6.9     13.9     20.8     41.6     76.1
SYN2g23-REG  base      106   83   35    72.6    33.4     68.4    101.8    201.9    368.9
SYN2g23-REG  baseT     106   82   20    75.7    30.3     50.3     80.6    171.5    323.0
SYN2g23-REG  E1T       106   59   20    51.7    54.3     74.3    128.6    291.6    563.2
SYN2g23-REG  E2k500T   106   81    4    80.1    25.9     29.9     55.7    133.3    262.7
INJgas68     base       24   18   49     6.5    17.5     66.5     84.0    136.5    224.0
INJgas68     baseT      24   16   41     6.1    17.9     58.9     76.8    130.5    219.9
INJgas68     E1T        24   13    0    13.0    11.0     11.0     22.0     55.0    110.0
INJgas68     E2k500T    24   16    0    16.0     8.0      8.0     16.0     40.0     80.0

lowest-cost arm, excess basis (w = 1, 2, 5, 10):
SYN2g23-B    E1T | E1T | E1T | E1T
SYN2g23-MC   E1T | E1T | E1T | E1T
SYN2g23-REG  E2k500T | E2k500T | E2k500T | E2k500T
INJgas68     E2k500T | E2k500T | E2k500T | E2k500T

lowest-cost arm, raw basis (w = 1, 2, 5, 10):
SYN2g23-B    E1T | E1T=E2k500T | E2k500T | baseT
SYN2g23-MC   E1T | E1T | E2k500T | E2k500T
SYN2g23-REG  E2k500T | E2k500T | E2k500T | E2k500T
INJgas68     E2k500T | E2k500T | E2k500T | E2k500T

break-even, main arm vs each other arm:
SYN2g23-B    E2k500T vs base     excess: E2k500T never costlier           raw: base cheaper once w > 12.00
SYN2g23-B    E2k500T vs baseT    excess: E2k500T never costlier           raw: baseT cheaper once w > 8.83
SYN2g23-B    E2k500T vs E1T      excess: E1T never costlier               raw: E2k500T cheaper once w > 2.00
SYN2g23-MC   E2k500T vs base     excess: E2k500T never costlier           raw: base cheaper once w > 23.00
SYN2g23-MC   E2k500T vs baseT    excess: E2k500T never costlier           raw: baseT cheaper once w > 27.67
SYN2g23-MC   E2k500T vs E1T      excess: E1T never costlier               raw: E2k500T cheaper once w > 3.50
SYN2g23-REG  E2k500T vs base     excess: E2k500T never costlier           raw: base cheaper once w > 15.50
SYN2g23-REG  E2k500T vs baseT    excess: E2k500T never costlier           raw: baseT cheaper once w > 16.00
SYN2g23-REG  E2k500T vs E1T      excess: E2k500T never costlier           raw: E2k500T never costlier
INJgas68     E2k500T vs base     excess: E2k500T never costlier           raw: base cheaper once w > 24.50
INJgas68     E2k500T vs baseT    excess: E2k500T never costlier           raw: E2k500T never costlier
INJgas68     E2k500T vs E1T      excess: E2k500T never costlier           raw: E2k500T never costlier

## E11 per drift type (synthetic, two seeds pooled): main arm vs baseT
SYN2g23-B    sud  N  34 | E2k500T excess  21.9 FP   3 | baseT excess  23.2 FP  15 | cost@10  123.6 vs  123.4 | baseT cheaper once w > 9.87  <- baseT cheaper at w=10
SYN2g23-B    grad N  26 | E2k500T excess  15.1 FP   5 | baseT excess   9.5 FP  22 | cost@10  114.2 vs  187.2 | E2k500T never costlier
SYN2g23-B    inc  N  32 | E2k500T excess  21.2 FP   4 | baseT excess  15.5 FP  18 | cost@10  112.1 vs  182.5 | E2k500T never costlier
SYN2g23-B    rec  N  26 | E2k500T excess   9.4 FP   2 | baseT excess   8.0 FP  12 | cost@10  168.3 vs  191.6 | E2k500T never costlier
SYN2g23-MC   sud  N  15 | E2k500T excess  13.5 FP   2 | baseT excess   9.2 FP  25 | cost@10   17.2 vs   83.1 | E2k500T never costlier
SYN2g23-MC   grad N  12 | E2k500T excess  12.0 FP   0 | baseT excess   5.8 FP  29 | cost@10    0.0 vs   90.8 | E2k500T never costlier
SYN2g23-MC   inc  N  18 | E2k500T excess  15.7 FP   2 | baseT excess   6.8 FP  26 | cost@10   24.5 vs  137.5 | E2k500T never costlier
SYN2g23-MC   rec  N  13 | E2k500T excess   9.9 FP   3 | baseT excess  10.2 FP  10 | cost@10   34.3 vs   37.8 | baseT cheaper once w > 19.58
SYN2g23-REG  sud  N  24 | E2k500T excess  18.4 FP   3 | baseT excess  16.9 FP   6 | cost@10   59.2 vs   77.3 | E2k500T never costlier
SYN2g23-REG  grad N  30 | E2k500T excess  23.0 FP   0 | baseT excess  21.2 FP   2 | cost@10   70.0 vs   90.4 | E2k500T never costlier
SYN2g23-REG  inc  N  32 | E2k500T excess  29.0 FP   0 | baseT excess  23.9 FP   6 | cost@10   30.0 vs   86.9 | E2k500T never costlier
SYN2g23-REG  rec  N  20 | E2k500T excess   9.8 FP   1 | baseT excess  13.8 FP   6 | cost@10  103.4 vs   68.5 | baseT cheaper once w > 1.25  <- baseT cheaper at w=10

## E12 pooled per group (3000-step windows; missed = N - excess; cost = w * missed + FP)
group        arm         N   TP   FP  excess  missed   cost@1   cost@2   cost@5  cost@10
SYN2g45-B    baseT     124   89   86    58.5    65.5    151.5    216.9    413.4    740.7
SYN2g45-B    E2k500T   124   75    9    70.8    53.2     62.2    115.5    275.2    541.4
SYN2g45-B    E10bT     124  104   22    94.9    29.1     51.1     80.3    167.7    313.4
SYN2g45-MC   baseT      60   59   83    34.3    25.7    108.7    134.3    211.3    339.6
SYN2g45-MC   E2k500T    60   45   10    41.1    18.9     28.9     47.8    104.4    198.9
SYN2g45-MC   E10bT      60   58   10    53.9     6.1     16.1     22.1     40.3     70.6
SYN2g45-REG  baseT     118   86   23    78.5    39.5     62.5    102.1    220.7    418.4
SYN2g45-REG  E2k500T   118   91   10    87.7    30.3     40.3     70.7    161.7    313.4
SYN2g45-REG  E10bT     118   99   15    94.1    23.9     38.9     62.8    134.4    253.8
INJgas9      baseT       8    5   13     1.8     6.2     19.2     25.4     44.1     75.1
INJgas9      E2k500T     8    3    2     2.5     5.5      7.5     13.1     29.7     57.4
INJgas9      E10bT       8    3    2     2.5     5.5      7.5     13.1     29.7     57.4

lowest-cost arm, excess basis (w = 1, 2, 5, 10):
SYN2g45-B    E10bT | E10bT | E10bT | E10bT
SYN2g45-MC   E10bT | E10bT | E10bT | E10bT
SYN2g45-REG  E10bT | E10bT | E10bT | E10bT
INJgas9      E2k500T=E10bT | E2k500T=E10bT | E2k500T=E10bT | E2k500T=E10bT

lowest-cost arm, raw basis (w = 1, 2, 5, 10):
SYN2g45-B    E10bT | E10bT | E10bT | E10bT
SYN2g45-MC   E10bT | E10bT | E10bT | E10bT
SYN2g45-REG  E10bT | E10bT | E10bT | E10bT
INJgas9      E2k500T=E10bT | E2k500T=E10bT | E2k500T=E10bT | baseT

break-even, main arm vs each other arm:
SYN2g45-B    E10bT vs baseT    excess: E10bT never costlier             raw: E10bT never costlier
SYN2g45-B    E10bT vs E2k500T  excess: E10bT cheaper once w > 0.54      raw: E10bT cheaper once w > 0.45
SYN2g45-MC   E10bT vs baseT    excess: E10bT never costlier             raw: baseT cheaper once w > 73.00
SYN2g45-MC   E10bT vs E2k500T  excess: E10bT never costlier             raw: E10bT never costlier
SYN2g45-REG  E2k500T vs baseT    excess: E2k500T never costlier           raw: E2k500T never costlier
SYN2g45-REG  E2k500T vs E10bT    excess: E10bT cheaper once w > 0.77      raw: E10bT cheaper once w > 0.62
INJgas9      E10bT vs baseT    excess: E10bT never costlier             raw: baseT cheaper once w > 5.50
INJgas9      E10bT vs E2k500T  excess: E10bT never costlier             raw: E10bT never costlier

## E12 per drift type (synthetic, two seeds pooled): main arm vs baseT
SYN2g45-B    sud  N  36 | E10bT excess  30.4 FP   7 | baseT excess  16.2 FP  32 | cost@10   62.8 vs  230.1 | E10bT never costlier
SYN2g45-B    grad N  26 | E10bT excess  22.4 FP   6 | baseT excess  14.5 FP  21 | cost@10   42.1 vs  135.8 | E10bT never costlier
SYN2g45-B    inc  N  36 | E10bT excess  18.1 FP   9 | baseT excess  13.8 FP  16 | cost@10  188.5 vs  237.7 | E10bT never costlier
SYN2g45-B    rec  N  26 | E10bT excess  24.0 FP   0 | baseT excess  14.0 FP  17 | cost@10   20.0 vs  137.2 | E10bT never costlier
SYN2g45-MC   sud  N  15 | E10bT excess  12.4 FP   2 | baseT excess   8.1 FP  25 | cost@10   27.8 vs   93.8 | E10bT never costlier
SYN2g45-MC   grad N  16 | E10bT excess  14.6 FP   3 | baseT excess   7.1 FP  27 | cost@10   17.4 vs  115.7 | E10bT never costlier
SYN2g45-MC   inc  N  13 | E10bT excess  12.3 FP   2 | baseT excess   7.8 FP  19 | cost@10    8.9 vs   70.6 | E10bT never costlier
SYN2g45-MC   rec  N  16 | E10bT excess  14.7 FP   3 | baseT excess  11.2 FP  12 | cost@10   16.5 vs   59.5 | E10bT never costlier
SYN2g45-REG  sud  N  32 | E2k500T excess  21.7 FP   4 | baseT excess  23.1 FP   3 | cost@10  106.9 vs   91.6 | baseT never costlier  <- baseT cheaper at w=10
SYN2g45-REG  grad N  34 | E2k500T excess  30.5 FP   1 | baseT excess  22.6 FP   5 | cost@10   35.6 vs  119.1 | E2k500T never costlier
SYN2g45-REG  inc  N  20 | E2k500T excess  12.3 FP   3 | baseT excess   8.1 FP   8 | cost@10   80.2 vs  127.1 | E2k500T never costlier
SYN2g45-REG  rec  N  32 | E2k500T excess  23.1 FP   2 | baseT excess  24.6 FP   7 | cost@10   90.6 vs   80.6 | baseT cheaper once w > 3.32  <- baseT cheaper at w=10

## E12 regression: E10bT vs E2k500T (excess basis)
pooled E10bT excess  94.1 FP  15 | E2k500T excess  87.7 FP  10 | E10bT cheaper once w > 0.77 | E10bT cheaper at every registered w: True
sud    E10bT excess  23.1 FP   6 | E2k500T excess  21.7 FP   4 | E10bT cheaper once w > 1.45 | E10bT cheaper at every registered w: False
grad   E10bT excess  31.1 FP   2 | E2k500T excess  30.5 FP   1 | E10bT cheaper once w > 1.85 | E10bT cheaper at every registered w: False
inc    E10bT excess  14.0 FP   4 | E2k500T excess  12.3 FP   3 | E10bT cheaper once w > 0.57 | E10bT cheaper at every registered w: True
rec    E10bT excess  25.9 FP   3 | E2k500T excess  23.1 FP   2 | E10bT cheaper once w > 0.36 | E10bT cheaper at every registered w: True

## Readings (registered; C1 changes no E11 / E12 verdict)
R1 pooled: main arm's cost <= baseT (E11: also base) at every w in all 8 groups: True -> miss weighting does not bring base back
R2 raw basis (contrast only), baseT cheaper than the main arm: SYN2g23-B baseT w=10, INJgas9 baseT w=10
R3 drift-type cells where baseT is cheaper than the main arm at w=10: 4 of 24 ['SYN2g23-B-sud', 'SYN2g23-REG-rec', 'SYN2g45-REG-sud', 'SYN2g45-REG-rec'] -> the main arm holds per drift type; exceptions are few (raw basis: 5)
R4 regression E10bT vs E2k500T: pooled cheaper at every w True; drift types cheaper at every w 2 of 4 -> cost view keeps E2k500T
