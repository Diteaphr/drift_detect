## Per family x arm (quality = accuracy, or MAE for REG)
                runs  tp  fp  quality   delay
family  arm                                  
B       E1         6   4   3   0.9529  1540.0
        E2k0       6   5   8   0.9544   738.0
        E2k500     6   5   7   0.9547   738.0
        base       6   6  11   0.9551  1105.0
MC-RBF  E1        12  14   0   0.7091   273.0
        E2k0      12  22   1   0.6968  1062.0
        E2k500    12  21   3   0.7007  1124.0
        base      12  22  24   0.6863   691.5
MC-syn  E1        12  37   5   0.7924    83.0
        E2k0      12  38   4   0.7745   183.0
        E2k500    12  37   5   0.7874   108.0
        base      12  35  48   0.7708    98.0
REG-Joe E1        12  20  24   2.6538   192.0
        E2k0      12  20  16   2.6560   473.0
        E2k500    12  21  13   2.6438   288.0
        base      12  23  29   2.6659   317.0
REG-syn E1         6  19  10   2.7161    79.0
        E2k0       6  19   1   3.0763   215.0
        E2k500     6  20   0   2.7366   122.0
        base       6  18  20   2.8063    81.0

## E1
B        FP 11->3 (73%)  TP 6->4 (allow -1)  delay +435  quality 0.9551->0.9529  dec-FPs gone 1.00  -> not met
MC-syn   FP 48->5 (90%)  TP 35->37 (allow -3)  delay -15  quality 0.7708->0.7924  dec-FPs gone 0.85  -> PASS  | M4 accuracy up: True
MC-RBF   FP 24->0 (100%)  TP 22->14 (allow -11)  delay -418  quality 0.6863->0.7091  dec-FPs gone 1.00  -> PASS  | M4 accuracy up: True
REG-syn  FP 20->10 (50%)  TP 18->19 (allow -1)  delay -2  quality 2.8063->2.7161  dec-FPs gone 0.92  -> PASS
REG-Joe  FP 29->24 (17%)  TP 23->20 (allow -4)  delay -125  quality 2.6659->2.6538  dec-FPs gone 1.00
E1 FAILURE (TP->0 or FP drop <20%): none

## E2 (k=0 primary)
H1: REG FP E1=34 E2k0=17; M3 events gone in E2k0=0.80 (n=20)  -> SUPPORTED
H2: TP on the 16 audit runs E1=24 E2k0=34  -> SUPPORTED
E2 verdict: frozen reference stays a main-method candidate

## k=500: FP 28 vs k0 30, TP 104 vs 104, switch-killed true warnings=0  -> keep two-phase
