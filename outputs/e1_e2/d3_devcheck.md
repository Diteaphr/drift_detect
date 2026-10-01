## D3 per group (TP@3000, FP@3000, excess hits, quality = accuracy or MAE, max reference age)
SYN2-B   base     TP  44  FP  45  excess  32.1  quality 0.9536  max ref age      -
SYN2-B   E2k500   TP  30  FP  10  excess  27.3  quality 0.9430  max ref age  81041
SYN2-B   baseT    TP  46  FP  32  excess  37.5  quality 0.9548  max ref age      -
SYN2-B   E2k500T  TP  37  FP   3  excess  36.2  quality 0.9464  max ref age  67761
SYN2-B   E10bT    TP  44  FP   6  excess  41.9  quality 0.9546  max ref age  50463
SYN2-B   E10bFT   TP  44  FP   6  excess  41.9  quality 0.9546  max ref age  50463
SYN2-REG base     TP  53  FP  16  excess  46.7  quality 2.8940  max ref age      -
SYN2-REG E2k500   TP  43  FP   8  excess  39.9  quality 2.8831  max ref age  47710
SYN2-REG baseT    TP  54  FP  15  excess  47.9  quality 2.9013  max ref age      -
SYN2-REG E2k500T  TP  46  FP   4  excess  44.4  quality 2.8690  max ref age  51582
SYN2-REG E10bT    TP  50  FP   7  excess  47.1  quality 2.8812  max ref age  38463
SYN2-REG E10bFT   TP  49  FP   7  excess  46.4  quality 2.8796  max ref age  30955

## V: SYN2-B runs where E10bFT's detections differ from E10bT's: 0 of 8 -> VALID

A2's stale misses (E2k500 missed, its reference >= 10k steps old): 34; hit by base 28, baseT 30, E2k500T 12, E10bT 22, E10bFT 22
  SYN2-B   19; hit by base 17, baseT 19, E2k500T 9, E10bT 18, E10bFT 18
  SYN2-REG 15; hit by base 11, baseT 11, E2k500T 3, E10bT 4, E10bFT 4

D3 reading E10bFT: (1) excess >= baseT in both groups False | (2) stale recovered 22/34 >= 50% True | (3) FP <= 50% of baseT in both groups True -> PARTLY | beats E2k500T in both groups: True
vs E10bT on SYN2-REG: excess 46.4 vs 47.1 (need >=46.1: True) | stale recovered 4 vs 4 (need >=3: True) -> NOT WORSE than E10bT

## Guard-triggered confirmations on SYN2-REG (replay mismatches: 0 -> VALID)
E10bT  confirmations 57 | FP 7 (guard 4) | hits 50 (guard 14, rr>=1.1 10, median guard-hit delay 621)
E10bFT confirmations 56 | FP 7 (guard 0) | hits 49 (guard 12, rr>=1.1 9, median guard-hit delay 654)

SYN2-B hits per E2k500T reference age at drift onset:
       base  baseT  E2k500T  E10bT  E10bFT   n
bin_t                                         
<10k      7      6        8      7       7   9
>=10k    37     40       29     37      37  41

SYN2-REG hits per E2k500T reference age at drift onset:
       base  baseT  E2k500T  E10bT  E10bFT   n
bin_t                                         
<10k     30     31       28     30      29  38
>=10k    23     23       18     20      20  30
