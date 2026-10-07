"""Flag-off baseline reuse check for the two slow families (prereg gate): one rerun each
must reproduce the E0 / archived detection sequence."""
import os
import sys

import pandas as pd

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "scripts")
from diagnose_regression_fp import dataset_key, discover, run  # noqa: E402

checks = [
    ("MC-RBF", "data/synthetic_dataset_joe/multi classification/sudden_drift/high/recurring_sudden_rbf4_100k_g00.csv",
     "hf10sqrt/error", "hf", {"n_trees": 10, "max_features": "sqrt"}, {}, 20000,
     "outputs/e0_native_direction/MC-RBF/detections.csv"),
    ("REG-Joe", discover("joe", 2, False)[0], "htr-nr/error", "htr", {}, {"ecpf_normalizer_reset_on_drift": True}, 0,
     "outputs/regression_fp_p3_joe_htr/detections_labelled.csv"),
]
for fam, path, label, mt, mk, pk, ms, ref in checks:
    _, dets, *_ = run(path, mt, ms, mk, pk)
    base = pd.read_csv(ref)
    key = dataset_key(path)
    b = base[(base.dataset == key) & (base.config == label)][["warning_t", "confirmation_t"]].astype(int).values.tolist()
    print(fam, key, label, "IDENTICAL" if sorted(map(list, dets)) == sorted(b) else "DIFFERS", flush=True)
