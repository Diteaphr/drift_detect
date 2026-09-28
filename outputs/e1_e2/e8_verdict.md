## E8 held-out: E7 (delta 0.002/0.004) vs E2k500 (0.05/0.1), 3000-step window
B-ho       FP@3000 4->2  TP@3000 11->9  delay 1031->1232  quality 0.9509->0.9502  | @1000 TP 8->6 FP 7->5
MC-syn-ho  FP@3000 3->0  TP@3000 38->40  delay 128->186  quality 0.7960->0.8007  | @1000 TP 38->39 FP 3->1
MC-RBF-ho  FP@3000 3->1  TP@3000 12->14  delay 1084->1404  quality 0.7126->0.7153  | @1000 TP 12->13 FP 4->2
REG-syn-ho FP@3000 0->0  TP@3000 20->20  delay 100->141  quality 2.6015->2.7499  | @1000 TP 20->20 FP 0->0
REG-Joe-ho FP@3000 7->7  TP@3000 29->25  delay 478->616  quality 2.7892->2.7693  | @1000 TP 21->18 FP 15->14
(a) classification: FP@3000 10->3 (need <=7.0): True | TP loss <=1: False | accuracy: True  ->  FAIL
(b) regression: TP loss {'REG-syn-ho': 0, 'REG-Joe-ho': 4}, FP@3000 7->7  ->  split SUPPORTED
mechanism (report only): classification E2k500 FP@3000 gone in E7 = 0.50 (n=10)
E8 verdict: classification gain did not replicate: keep uniform delta 0.05/0.1 (E2-k500)
