## E6 vs E2-k500 (quality = accuracy, or MAE for REG)
MC-syn   FP 5->2  TP 37->37  delay +0  quality 0.7874->0.7866  dec-FPs gone n/a
MC-RBF   FP 3->3  TP 21->21  delay +0  quality 0.7007->0.7003  dec-FPs gone n/a
B        FP 7->7  TP 5->4  delay +601  quality 0.9547->0.9549  dec-FPs gone n/a
REG-syn  FP 0->0  TP 20->20  delay +6  quality 2.7366->2.7463  dec-FPs gone n/a
REG-Joe  FP 13->13  TP 21->19  delay -3  quality 2.6438->2.6456  dec-FPs gone n/a
adopt E6: FP 28->25 (need <=20): False | TP loss <=1 per family: False | delay +<=100: False  ->  keep E2-k500; E6 reported as ablation
