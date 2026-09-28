## E7 vs E2-k500 (primary: 3000-step window; quality = accuracy, or MAE for REG)
MC-syn   FP@3000 1->0  TP@3000 38->40  delay 110->144  quality 0.7874->0.7944 (ok)  | @1000 TP 37->39 FP 5->1
MC-RBF   FP@3000 1->0  TP@3000 20->21  delay 921->1457  quality 0.7007->0.7083 (ok)  | @1000 TP 21->22 FP 3->1
B        FP@3000 6->2  TP@3000 6->5  delay 1080->1901  quality 0.9547->0.9539 (ok)  | @1000 TP 5->1 FP 7->6
REG-syn  FP@3000 0->0  TP@3000 20->20  delay 122->146  quality 2.7366->2.7499 (ok)  | @1000 TP 20->20 FP 0->0
REG-Joe  FP@3000 5->8  TP@3000 29->25  delay 502->630  quality 2.6438->2.6488 (ok)  | @1000 TP 21->19 FP 13->14
mechanism: E2-k500 FP@3000 gone in E7 = 0.69 (n=13) -> PASS
adopt E7: FP@3000 13->10 (need <=9.1): False | TP@3000 loss <=1 per family: False | quality: True  ->  keep E2-k500; E7 reported as ablation
