"""Ablation: ECPF conceptual-equivalence definition -- error-bitset (paper) vs
label-agreement (this project's modification).

The literature check established that the published ECPF/CPF similarity is an
error-bitset XOR (paper §3.1 and ECPF.java agree), under which two experts that
are BOTH WRONG count as agreeing even when they predicted different wrong
classes. At K = 2 this equals label agreement (both-wrong forces the same other
label); at K > 2 they decouple and the bitset inflates agreement exactly where
the pool matters most -- low-accuracy post-drift buffers. This script measures
whether that theoretical divergence has real consequences, with everything else
held at pure defaults (no timeout / cooldown / gate).

Predictions, written before running:
  P1  K = 2 control: both modes produce IDENTICAL detections and merges
      (mathematical equivalence; doubles as an implementation check)
  P2  K > 2: the bitset arm merges MORE (inflated agreement)
  P3  the bitset arm's CROSS-CONCEPT merge rate is higher -- it deletes experts
      that represent different ground-truth concepts
  P4  downstream, the label arm's reuse quality at recurrences
      (acc_best_on_warning) and prequential accuracy are >= the bitset arm's

Era -> concept mapping: era k is the stretch between confirmed drifts k and
k+1; its concept is the ground-truth concept at the era's midpoint. Slots carry
the era they last represented (ECPFMetaLearner.slot_eras); a merge whose kept
and removed slots map to different concepts is a cross-concept merge.
"""

from __future__ import annotations

import os
import sys
import warnings
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PipelineConfig  # noqa: E402
from src.ecpf import load_drift_intervals_file  # noqa: E402
from src.pipeline import ConceptDriftPipeline  # noqa: E402

WARM = 200
HIT_TOL = 1000
RECOVERY_WIN = 1000


def concept_mc_sudden(t: int) -> int:
    # generator: boundary rotates at 0.25/0.5/0.75 of 20k; concepts 0,1,2,0
    if t < 5000:
        return 0
    if t < 10000:
        return 1
    if t < 15000:
        return 2
    return 0


def concept_mc_recurring(t: int) -> int:
    # generator: six segments of n//6 = 3333, order [0,1,2,0,1,2]
    return min(t // 3333, 5) % 3


STREAMS: List[Tuple[str, int, Callable[[int], int], str]] = [
    ("data/recurring_drift/recurring_sud_sea100k_g00.csv", 16000, None, "binary_control"),
    ("data/synthetic_multiclass/mc3_sudden_20k.csv", 20000, concept_mc_sudden, "mc3_sudden"),
    ("data/synthetic_multiclass/mc5_sudden_20k.csv", 20000, concept_mc_sudden, "mc5_sudden"),
    ("data/synthetic_multiclass/mc3_recurring_20k.csv", 20000, concept_mc_recurring, "mc3_recurring"),
    ("data/synthetic_multiclass/mc5_recurring_20k.csv", 20000, concept_mc_recurring, "mc5_recurring"),
]
MODES = ["error_bitset", "label_agreement"]


def run(csv, max_steps, mode):
    df = pd.read_csv(csv).iloc[:max_steps]
    y = df["y"].values
    X = df[[c for c in df.columns if c != "y"]].values.astype(float)
    cfg = PipelineConfig(model_type="hf", model_kwargs={"n_trees": 10}, use_ecpf=True,
                         ecpf_signal_mode="dual_adwin",
                         ecpf_warning_signal="error", ecpf_drift_signal="error",
                         ecpf_similarity_mode=mode)
    pipe = ConceptDriftPipeline(cfg)
    acc = []
    dets = []   # (warn_t, conf_t, details)
    for t, yt, yp, ds, _ in pipe.run_stream(X, y, warm_start_samples=WARM):
        acc.append(1.0 if int(round(float(yt))) == int(round(float(yp))) else 0.0)
        for d in ds:
            dets.append((int(d.timestamp), t, dict(d.details)))
    ec = pipe._ecpf
    return dict(acc=np.array(acc), dets=dets, offset=WARM,
                merges=ec.model_merges, reuses=ec.model_reuses, swaps=ec.leader_swaps,
                pool=sum(1 for s in ec.slots if s is not None))


def era_concepts(dets, max_steps, concept_of):
    """era index -> ground-truth concept at the era's midpoint."""
    confs = [c for _, c, _ in dets]
    bounds = [WARM] + confs + [max_steps]
    return {k: concept_of((bounds[k] + bounds[k + 1]) // 2) for k in range(len(bounds) - 1)}


rows = []
identity: Dict[str, Dict[str, list]] = {}
for csv, max_steps, concept_of, name in STREAMS:
    if not os.path.exists(csv):
        print("missing %s" % csv)
        continue
    gt = [a for a, _ in load_drift_intervals_file(os.path.splitext(csv)[0] + "_drift_times.txt")
          if a < max_steps]
    for mode in MODES:
        r = run(csv, max_steps, mode)
        warns = [w for w, _, _ in r["dets"]]
        tp = sum(1 for g in gt if any(g <= w <= g + HIT_TOL for w in warns))
        fp = sum(1 for w in warns if not any(g <= w <= g + HIT_TOL for g in gt))

        cc_merges, n_pairs = 0, 0
        if concept_of is not None:
            eras = era_concepts(r["dets"], max_steps, concept_of)
            for _, _, det in r["dets"]:
                slot_eras = det.get("slot_eras", {})
                for keep, lose in det.get("merge_pairs", []):
                    n_pairs += 1
                    ck = eras.get(slot_eras.get(keep, -1))
                    cl = eras.get(slot_eras.get(lose, -1))
                    if ck is not None and cl is not None and ck != cl:
                        cc_merges += 1

        acc = r["acc"]
        rec = []
        for _, c, _ in r["dets"]:
            i = c - r["offset"]
            seg = acc[i:i + RECOVERY_WIN]
            if seg.size >= 200:
                rec.append(float(seg.mean()))
        abw = [d.get("acc_best_on_warning") for _, _, d in r["dets"]
               if d.get("acc_best_on_warning") is not None]

        rows.append(dict(stream=name, mode=mode, dets=len(warns), tp=tp, fp=fp,
                         merges=r["merges"], merge_pairs=n_pairs, cc_merges=cc_merges,
                         pool=r["pool"], swaps=r["swaps"],
                         acc_best_warn=np.mean(abw) if abw else np.nan,
                         recovery=np.mean(rec) if rec else np.nan,
                         prequential=float(acc.mean())))
        identity.setdefault(name, {})[mode] = [(w, c, d.get("merged")) for w, c, d in r["dets"]]
        print("%-16s %-16s dets=%2d tp=%d fp=%d merges=%2d cc=%d pool=%d preq=%.4f"
              % (name, mode, len(warns), tp, fp, r["merges"], cc_merges, r["pool"],
                 float(acc.mean())))

df = pd.DataFrame(rows)
print()
print("=" * 100)
print("P1  K=2 identity check")
b = identity.get("binary_control", {})
same = b.get(MODES[0]) == b.get(MODES[1])
print("  detections+merges identical across modes: %s" % same)
print()
print("=" * 100)
print("P2-P4  K>2 comparison (bitset vs label)")
mc = df[df.stream != "binary_control"]
piv = mc.pivot_table(index="stream",
                     columns="mode",
                     values=["merges", "cc_merges", "tp", "fp", "acc_best_warn",
                             "recovery", "prequential", "pool"],
                     aggfunc="first")
print(piv.round(4).to_string())
print()
agg = mc.groupby("mode")[["merges", "cc_merges", "tp", "fp",
                          "acc_best_warn", "recovery", "prequential"]].mean()
print(agg.round(4).to_string())

out = "outputs/similarity_ablation"
os.makedirs(out, exist_ok=True)
df.to_csv(os.path.join(out, "results.csv"), index=False)
print()
print("wrote %s/results.csv (%d rows)" % (out, len(df)))
