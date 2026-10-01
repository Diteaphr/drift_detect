## A0(a) longest warning->confirmation age: 983 -> VALID

## Per group (3000-step windows; quality = accuracy; preFP only read on injected groups)
group        arm        N    TP    FP   excess  preFP   delay   quality
SYN2g89-B    baseT    106    81    80     58.1      5     728    0.9534
SYN2g89-B    E10bFT   106    92    20     85.7      4     756    0.9563
SYN2g89-MC   baseT     58    58    73     38.2     10     347    0.7260
SYN2g89-MC   E10bFT    58    55     8     51.9      0     448    0.7441
INJelec69    baseT     64    32    76     25.7     56     944    0.7736
INJelec69    E10bFT    64    40    18     38.4     10    1200    0.7736

## B: E10bFT vs baseT (recall = excess hits)
E10bFT: P1 INJelec69 pre-drift FP 10 vs baseT 56 (need <=16.8: True) | P2 excess 38.4 vs 25.7 (need >=23.1): True
E10bFT: P3 SYN2g89-B FP@3000 20 vs baseT 80 (need <=40.0: True) | excess 85.7 vs 58.1 (need >=52.3): True
E10bFT: P3 SYN2g89-MC FP@3000 8 vs baseT 73 (need <=36.5: True) | excess 51.9 vs 38.2 (need >=34.4): True
E10bFT: P4 SYN2g89-B quality 0.9563 vs baseT 0.9534: True
E10bFT: P4 SYN2g89-MC quality 0.7441 vs baseT 0.7260: True
E10bFT: P4 INJelec69 quality 0.7736 vs baseT 0.7736: True

## Main reading: ALL PASS -> classification CONFIRMED; one main method E10bFT for both tasks (classification holds in E12 and E14, missed in E13)

## S1 learner split on INJelec69: E10bFT excess / baseT
hf10   baseT  14.3  E10bFT  20.3  ratio 1.42
ht     baseT  11.4  E10bFT  18.1  ratio 1.59
-> not learner-bound

## S2 electricity pooled with E13 (E13's E10bT == E10bFT on classification)
pooled pre-drift FP E10bFT 21 vs baseT 105 (P1 need <=31.5: True) | excess 62.0 vs 52.7 (P2 need >=47.5: True)

## S3 per injection method (abrupt + gradual pooled)
      n_gt           tp          pre           xs      
arm E10bFT baseT E10bFT baseT E10bFT baseT E10bFT baseT
m                                                      
cp      16    16     12    10      3    16   11.6   8.3
ff      16    16      3     3      4    13    2.2   1.4
fp      16    16     12     6      3    17   11.7   3.9
ls      16    16     13    13      0    10   13.0  12.0

E10bFT confirmations 240, of which the leader guard fired the drift: 121; max reference age 45111
