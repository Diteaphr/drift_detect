## D2 per group (TP@3000, FP@3000, excess hits, quality = accuracy or MAE, max reference age)
SYN2-B   base     TP  44  FP  45  excess  32.1  quality 0.9536  max ref age      -
SYN2-B   E2k500   TP  30  FP  10  excess  27.3  quality 0.9430  max ref age  81041
SYN2-B   baseT    TP  46  FP  32  excess  37.5  quality 0.9548  max ref age      -
SYN2-B   E2k500T  TP  37  FP   3  excess  36.2  quality 0.9464  max ref age  67761
SYN2-B   E10aT    TP  42  FP   3  excess  41.2  quality 0.9505  max ref age   5416
SYN2-B   E10bT    TP  44  FP   6  excess  41.9  quality 0.9546  max ref age  50463
SYN2-REG base     TP  53  FP  16  excess  46.7  quality 2.8940  max ref age      -
SYN2-REG E2k500   TP  43  FP   8  excess  39.9  quality 2.8831  max ref age  47710
SYN2-REG baseT    TP  54  FP  15  excess  47.9  quality 2.9013  max ref age      -
SYN2-REG E2k500T  TP  46  FP   4  excess  44.4  quality 2.8690  max ref age  51582
SYN2-REG E10aT    TP  37  FP   1  excess  36.4  quality 2.8602  max ref age   5096
SYN2-REG E10bT    TP  50  FP   7  excess  47.1  quality 2.8812  max ref age  38463

A2's stale misses (E2k500 missed, its reference >= 10k steps old): 34; hit by base 28, baseT 30, E2k500T 12, E10aT 21, E10bT 22
D2 reading E10aT: (1) excess >= baseT in both groups False | (2) stale recovered 21/34 >= 50% True | (3) FP <= 50% of baseT in both groups True -> PARTLY | beats E2k500T in both groups: False
D2 reading E10bT: (1) excess >= baseT in both groups False | (2) stale recovered 22/34 >= 50% True | (3) FP <= 50% of baseT in both groups True -> PARTLY | beats E2k500T in both groups: True
