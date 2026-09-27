"""E1 + E2, same round (docs/ECPF_E1E2_預註冊.md): native ADWIN direction gate vs
frozen reference, against the E0 baseline runs (same streams, learners, steps).

    python scripts/run_e1_e2.py --family MC-RBF --arm E1   # one cell; run cells in parallel
    python scripts/run_e1_e2.py --analyze                   # pre-registered verdicts

Must run on river 0.21.2 (Anaconda python), like E0 and the archives.
"""
import argparse
import glob
import gzip
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_native_direction import ARCHIVED, RERUN, sig_name  # noqa: E402
from diagnose_regression_fp import PERTURBATION, classify, dataset_key, discover, load_stream, run  # noqa: E402
from src.metrics import build_perturbation_intervals  # noqa: E402

OUT, E0 = "outputs/e1_e2", "outputs/e0_native_direction"
ARMS = {"E1": {"ecpf_adwin_one_sided": True},
        "E2k0": {"ecpf_reference_signal": True},
        "E2k500": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500}}
P3 = {"ecpf_normalizer_reset_on_drift": True}  # the regression baseline (htr-nr / hfr-nr) has it on
REG_LEARNERS = [("htr/error", "htr", {}), ("hfr/error", "hfr", {})]
CELLS = {**{f: (p, s, c, False) for f, (p, s, c) in RERUN.items()},
         "REG-syn": (discover("synthetic", 2, False), 0, REG_LEARNERS, True),
         "REG-Joe": (discover("joe", 2, False), 0, REG_LEARNERS, True)}
FP = ("echo", "orphan")
MATCH = 500
SIG_COLS = ["t", "err", "raw", "is_warning", "is_drift", "ref_err", "ref_age", "ref_switch", "switch_warning_age"]


def learner(config: str) -> str:
    """'hf10sqrt/error', 'htr-nr/error', 'htr-E1/error' -> 'hf10sqrt', 'htr', 'htr'."""
    return config.split("/")[0].split("-")[0]


def self_check() -> None:
    from river import drift
    from detectors.meta_ecpf.adwin_family import _OneSidedADWIN

    def fires(det, xs):
        n = 0
        for x in xs:
            det.update(x)
            n += det.drift_detected
        return n
    down, up = [1.0] * 400 + [0.0] * 400, [0.0] * 400 + [1.0] * 400
    assert fires(drift.ADWIN(delta=0.05, grace_period=30), down) >= 1   # two-sided fires on a drop
    assert fires(_OneSidedADWIN(delta=0.05, grace_period=30), down) == 0
    assert fires(_OneSidedADWIN(delta=0.05, grace_period=30), up) >= 1


def run_cell(family: str, arm: str) -> None:
    paths, max_steps, configs, is_reg = CELLS[family]
    d = os.path.join(OUT, family, arm)
    os.makedirs(os.path.join(d, "signals"), exist_ok=True)
    rows = []
    for path in paths:
        key = dataset_key(path)
        for base_label, mt, mk in configs:
            label = base_label.replace("/", "-%s/" % arm)
            pk = {**ARMS[arm], **(P3 if is_reg else {})}
            sig, dets, swaps, stage3, intervals, _, n = run(path, mt, max_steps, mk, pk)
            for r in classify(dets, intervals, sig, swaps, n):
                rows.append({**r, "dataset": key, "config": label, "path": path})
            with gzip.open(os.path.join(d, "signals", sig_name(key, label)), "wt") as f:
                sig[[c for c in SIG_COLS if c in sig.columns]].to_csv(f, index=False)
            print(family, arm, key, label, "detections=%d swaps=%d" % (len(dets), len(swaps)), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(d, "detections.csv"), index=False)


# ---------------------------------------------------------------------------
def runs_table():
    """One row per (family, arm, dataset, learner): hits, FP, delay, accuracy/MAE, detection times.

    Runs are enumerated from the matrix, not from detections.csv: a run with zero
    confirmations has no rows there but still counts (TP=FP=0, its accuracy/MAE).
    """
    recs = []

    def add(fam, arm, det_csv, sig_dir, labels):
        det = pd.read_csv(det_csv)
        for path in CELLS[fam][0]:
            ds = dataset_key(path)
            for cfg in labels:
                g = det[(det["dataset"] == ds) & (det["config"] == cfg)]
                sig = pd.read_csv(os.path.join(sig_dir, sig_name(ds, cfg)))
                hits = g[g["label"] == "hit"]
                recs.append({"family": fam, "arm": arm, "dataset": ds, "learner": learner(cfg),
                             "tp": len(hits), "fp": int(g["label"].isin(FP).sum()),
                             "delay": pd.to_numeric(hits["gap_prev_gt"], errors="coerce").tolist(),
                             "quality": float(sig["raw"].mean() if fam.startswith("REG") else 1 - sig["err"].mean()),
                             "conf_t": g["confirmation_t"].astype(int).tolist(), "path": path, "sig": sig})
    for fam, (_, _, configs) in RERUN.items():  # baselines: E0 reruns and the regression archives
        add(fam, "base", os.path.join(E0, fam, "detections.csv"), os.path.join(E0, fam, "signals"),
            [c for c, _, _ in configs])
    for fam, d, cfgs in ARCHIVED:
        add(fam, "base", os.path.join(d, "detections_labelled.csv"), os.path.join(d, "signals"), sorted(cfgs))
    for fam, (_, _, configs, _) in CELLS.items():
        for arm in ARMS:
            d = os.path.join(OUT, fam, arm)
            if os.path.exists(os.path.join(d, "detections.csv")):  # cell finished
                add(fam, arm, os.path.join(d, "detections.csv"), os.path.join(d, "signals"),
                    [c.replace("/", "-%s/" % arm) for c, _, _ in configs])
    return pd.DataFrame(recs)


def gone(events: pd.DataFrame, runs: pd.DataFrame, arm: str) -> float:
    """Share of baseline events with no confirmation of *arm* within MATCH steps (same run)."""
    idx = {(r.family, r.dataset, r.learner): r.conf_t for r in runs[runs["arm"] == arm].itertuples()}
    hit = [all(abs(t - e.confirmation_t) > MATCH for t in idx.get((e.family, e.dataset, learner(e.config)), []))
           for e in events.itertuples()]
    return float(np.mean(hit)) if hit else float("nan")


def analyze() -> None:
    runs = runs_table()
    e0 = pd.read_csv(os.path.join(E0, "confirmations.csv"))
    fam_arm = runs.groupby(["family", "arm"]).agg(
        runs=("tp", "size"), tp=("tp", "sum"), fp=("fp", "sum"), quality=("quality", "mean"),
        delay=("delay", lambda s: float(np.nanmedian(sum(s, [])) if sum(s, []) else np.nan)))
    print("## Per family x arm (quality = accuracy, or MAE for REG)\n%s" % fam_arm.round(4).to_string())

    # ---- E1
    allow = {"B": 1, "MC-syn": 3, "MC-RBF": 11, "REG-syn": 1, "REG-Joe": 4}
    target = {"B": .40, "MC-syn": .40, "REG-syn": .40, "MC-RBF": .30}
    print("\n## E1")
    fails = []
    for f in allow:
        if (f, "E1") not in fam_arm.index:
            print(f, "missing")
            continue
        b, e = fam_arm.loc[(f, "base")], fam_arm.loc[(f, "E1")]
        red = 1 - e.fp / b.fp if b.fp else float("nan")
        dec = e0[(e0["family"] == f) & e0["label"].isin(FP) & (e0["d_dir"] == "dec")]
        mech = gone(dec, runs, "E1")
        line = "%-8s FP %d->%d (%.0f%%)  TP %d->%d (allow -%d)  delay %+.0f  quality %.4f->%.4f  dec-FPs gone %.2f" % (
            f, b.fp, e.fp, 100 * red, b.tp, e.tp, allow[f], e.delay - b.delay, b.quality, e.quality, mech)
        if f in target:
            ok = red >= target[f] and b.tp - e.tp <= allow[f] and e.delay - b.delay <= 100 and mech >= 0.70
            line += "  -> %s" % ("PASS" if ok else "not met")
            if e.tp == 0 or red < 0.20:
                fails.append(f)
        elif red > 0.20:
            line += "  -> predicted ineffective but FP fell >20%: needs a closed-loop explanation"
        if f in ("MC-syn", "MC-RBF"):
            line += "  | M4 accuracy up: %s" % (e.quality >= b.quality)
        print(line)
    print("E1 FAILURE (TP->0 or FP drop <20%%): %s" % (fails or "none"))

    # ---- E2
    print("\n## E2 (k=0 primary)")
    reg = fam_arm.loc[[i for i in fam_arm.index if i[0].startswith("REG") and i[1] in ("E1", "E2k0")]]
    fp_e1 = int(reg.xs("E1", level="arm")["fp"].sum())
    fp_e2 = int(reg.xs("E2k0", level="arm")["fp"].sum())
    m3 = pd.read_csv(os.path.join(E0, "m3_catchup_events.csv"))
    m3_gone = gone(m3, runs, "E2k0")
    h1 = fp_e2 <= fp_e1 - 2 and m3_gone >= 0.50
    print("H1: REG FP E1=%d E2k0=%d; M3 events gone in E2k0=%.2f (n=%d)  -> %s"
          % (fp_e1, fp_e2, m3_gone, len(m3), "SUPPORTED" if h1 else "not supported"))
    audit = e0[(e0["label"] == "hit") & (e0["d_dir"] == "dec")]
    keys = {(r.family, r.dataset, learner(r.config)) for r in audit.itertuples()}
    tp_on = lambda arm: int(sum(r.tp for r in runs[runs["arm"] == arm].itertuples()
                                if (r.family, r.dataset, r.learner) in keys))
    h2 = tp_on("E2k0") >= tp_on("E1") + 1
    print("H2: TP on the %d audit runs E1=%d E2k0=%d  -> %s" % (len(keys), tp_on("E1"), tp_on("E2k0"),
                                                              "SUPPORTED" if h2 else "not supported"))
    print("E2 verdict: %s" % ("frozen reference stays a main-method candidate" if h1 or h2
                              else "E1 is the main mechanism; frozen reference -> analysis tool"))

    # ---- k=500 vs k=0
    k0, k5 = runs[runs["arm"] == "E2k0"], runs[runs["arm"] == "E2k500"]
    killed = 0
    for r in k5.itertuples():
        sw = r.sig[(r.sig.get("ref_switch", 0) == 1) & (r.sig.get("switch_warning_age", -1) >= 100)] \
            if "ref_switch" in r.sig else r.sig.iloc[0:0]
        if len(sw) and r.path:
            _, _, intervals = load_stream(r.path, 0)
            wins = build_perturbation_intervals(intervals, extension=PERTURBATION)
            killed += sum(any(s <= t - a <= e for s, e in wins) for t, a in zip(sw["t"], sw["switch_warning_age"]))
    keep = k5["fp"].sum() <= k0["fp"].sum() - 2 and k5["tp"].sum() >= k0["tp"].sum() and killed == 0
    print("\n## k=500: FP %d vs k0 %d, TP %d vs %d, switch-killed true warnings=%d  -> %s" % (
        k5["fp"].sum(), k0["fp"].sum(), k5["tp"].sum(), k0["tp"].sum(), killed,
        "keep two-phase" if keep else "k=0 suffices"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=list(CELLS))
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--check", action="store_true", help="run the E1 self-check only")
    a = ap.parse_args()
    self_check()
    if a.family and a.arm:
        run_cell(a.family, a.arm)
    if a.analyze:
        analyze()
