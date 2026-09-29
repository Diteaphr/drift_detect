## D1 per group (TP@3000, FP@3000, excess hits, quality = accuracy or MAE, max reference age)
SYN2-B   base     TP  44  FP  45  excess  32.1  quality 0.9536  max ref age      -
SYN2-B   E2k500   TP  30  FP  10  excess  27.3  quality 0.9430  max ref age  81041
SYN2-B   baseT    TP  46  FP  32  excess  37.5  quality 0.9548  max ref age      -
SYN2-B   E2k500T  TP  37  FP   3  excess  36.2  quality 0.9464  max ref age  67761
SYN2-REG base     TP  53  FP  16  excess  46.7  quality 2.8940  max ref age      -
SYN2-REG E2k500   TP  43  FP   8  excess  39.9  quality 2.8831  max ref age  47710
SYN2-REG baseT    TP  54  FP  15  excess  47.9  quality 2.9013  max ref age      -
SYN2-REG E2k500T  TP  46  FP   4  excess  44.4  quality 2.8690  max ref age  51582

A2's stale misses (E2k500 missed, its reference >= 10k steps old): 34; hit by base 28, baseT 30, E2k500T 12

hits per E2k500T reference age at drift onset:
        base  E2k500  baseT  E2k500T   n
bin_t                                   
<2k        2       1      2        1   2
2k-10k    35      36     35       35  45
>=10k     60      36     63       47  71

D1 reading: (1) excess E2k500T >= baseT in both groups: False | (2) stale misses recovered 12/34 >= 50%: False -> NOT resolved: the reference refresh rule is still open
