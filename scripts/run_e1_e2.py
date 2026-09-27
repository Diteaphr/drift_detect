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
        "E2k500": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500},
        # E6 (docs/ECPF_E6_疊加_預註冊.md): E2-k500 plus the one-sided gate on the reference's loss
        "E6": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_adwin_one_sided": True},
        # E7 (docs/ECPF_E7_δ校準_預註冊.md): E2-k500 with ADWIN's usual delta (warning/drift ratio kept at 2)
        "E7": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500,
               "detector_delta": 0.002, "detector_delta_w": 0.004}}
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
def iter_runs():
    """Yield (family, arm, path, dataset, config, detections, signals) for every run in the matrix.

    Runs are enumerated from the matrix, not from detections.csv: a run with zero
    confirmations has no rows there but still counts.
    """
    def runs_of(fam, arm, det_csv, sig_dir, labels):
        det = pd.read_csv(det_csv)
        for path in CELLS[fam][0]:
            ds = dataset_key(path)
            for cfg in labels:
                yield (fam, arm, path, ds, cfg, det[(det["dataset"] == ds) & (det["config"] == cfg)],
                       pd.read_csv(os.path.join(sig_dir, sig_name(ds, cfg))))
    for fam, (_, _, configs) in RERUN.items():  # baselines: E0 reruns and the regression archives
        yield from runs_of(fam, "base", os.path.join(E0, fam, "detections.csv"), os.path.join(E0, fam, "signals"),
                           [c for c, _, _ in configs])
    for fam, d, cfgs in ARCHIVED:
        yield from runs_of(fam, "base", os.path.join(d, "detections_labelled.csv"), os.path.join(d, "signals"),
                           sorted(cfgs))
    for fam, (_, _, configs, _) in CELLS.items():
        for arm in ARMS:
            d = os.path.join(OUT, fam, arm)
            if os.path.exists(os.path.join(d, "detections.csv")):  # cell finished
                yield from runs_of(fam, arm, os.path.join(d, "detections.csv"), os.path.join(d, "signals"),
                                   [c.replace("/", "-%s/" % arm) for c, _, _ in configs])


def runs_table():
    """One row per (family, arm, dataset, learner): hits, FP, delay, accuracy/MAE, detection times."""
    recs = []
    for fam, arm, path, ds, cfg, g, sig in iter_runs():
        hits = g[g["label"] == "hit"]
        recs.append({"family": fam, "arm": arm, "dataset": ds, "learner": learner(cfg),
                     "tp": len(hits), "fp": int(g["label"].isin(FP).sum()),
                     "delay": pd.to_numeric(hits["gap_prev_gt"], errors="coerce").tolist(),
                     "quality": float(sig["raw"].mean() if fam.startswith("REG") else 1 - sig["err"].mean()),
                     "conf_t": g["confirmation_t"].astype(int).tolist(), "path": path, "sig": sig})
    return pd.DataFrame(recs)


def rescore(exts=(1000, 3000), show: bool = True):
    """Relabel every run with wider scoring windows -- classify() itself, only PERTURBATION changes.
    ext=1000 must reproduce the stored labels exactly (checked). Returns one row per (run, ext)."""
    import diagnose_regression_fp as drf
    recs, gt = [], {}
    for fam, arm, path, ds, cfg, g, sig in iter_runs():
        key = (path, CELLS[fam][1])
        if key not in gt:
            gt[key] = load_stream(path, CELLS[fam][1])[2]
        dets = list(zip(g["warning_t"].astype(int), g["confirmation_t"].astype(int)))
        for ext in exts:
            drf.PERTURBATION = ext
            rows = drf.classify(dets, gt[key], sig, [], len(sig))
            labels = [r["label"] for r in rows]
            recs.append({"family": fam, "arm": arm, "ext": ext, "dataset": ds, "learner": learner(cfg),
                         "tp": labels.count("hit"), "fp": sum(lab in FP for lab in labels),
                         "delays": [float(r["gap_prev_gt"]) for r in rows if r["label"] == "hit"],
                         "fp_t": [r["confirmation_t"] for r in rows if r["label"] in FP],
                         "conf_t": [r["confirmation_t"] for r in rows],
                         "stored_tp": int((g["label"] == "hit").sum()), "stored_fp": int(g["label"].isin(FP).sum())})
    drf.PERTURBATION = 1000
    df = pd.DataFrame(recs)
    chk = df[df["ext"] == 1000]
    bad = int(((chk["tp"] != chk["stored_tp"]) | (chk["fp"] != chk["stored_fp"])).sum())
    if not show:
        return None if bad else df
    print("## Rescore (classify() with scoring window = GT start + ext)")
    print("validity: runs where ext=1000 differs from stored labels = %d" % bad)
    if bad:
        print("RESCORE INVALID")
        return None
    t = df.groupby(["family", "arm", "ext"])[["tp", "fp"]].sum().unstack("ext")
    t.columns = ["%s@%d" % c for c in t.columns]
    print(t.to_string())
    tot = df.groupby(["arm", "ext"])[["tp", "fp"]].sum().unstack("ext")
    tot.columns = ["%s@%d" % c for c in tot.columns]
    print()
    print("all families:")
    print(tot.to_string())
    df.drop(columns=["delays", "fp_t", "conf_t"]).to_csv(os.path.join(OUT, "rescore.csv"), index=False)
    return df


def analyze_delta() -> None:
    """E7 verdict (docs/ECPF_E7_δ校準_預註冊.md): 3000-step window is primary."""
    df = rescore(show=False)
    if df is None:
        print("RESCORE INVALID -- no verdict")
        return
    q = runs_table().groupby(["family", "arm"])["quality"].mean()
    w = df[df["ext"] == 3000]
    e7 = {(r.family, r.dataset, r.learner): r.conf_t for r in w[w["arm"] == "E7"].itertuples()}
    base_fp = [((r.family, r.dataset, r.learner), t) for r in w[w["arm"] == "E2k500"].itertuples() for t in r.fp_t]
    mech = float(np.mean([all(abs(c - t) > MATCH for c in e7.get(k, [])) for k, t in base_fp])) if base_fp else np.nan
    med = lambda s: float(np.median(sum(s, []))) if sum(s, []) else np.nan
    print("## E7 vs E2-k500 (primary: 3000-step window; quality = accuracy, or MAE for REG)")
    ok2 = ok3 = True
    done = [f for f in CELLS if (f, "E7") in q.index]
    w = w[w["family"].isin(done)]
    for f in CELLS:
        if f not in done:
            print("%-8s E7 missing" % f)
            continue
        b, e = (w[(w["family"] == f) & (w["arm"] == a)] for a in ("E2k500", "E7"))
        b1, e1 = (df[(df["ext"] == 1000) & (df["family"] == f) & (df["arm"] == a)] for a in ("E2k500", "E7"))
        qb, qe = q[(f, "E2k500")], q[(f, "E7")]
        q_ok = qe <= 1.02 * qb if f.startswith("REG") else qe >= qb - 0.005
        ok2 &= b["tp"].sum() - e["tp"].sum() <= 1
        ok3 &= bool(q_ok)
        print("%-8s FP@3000 %d->%d  TP@3000 %d->%d  delay %.0f->%.0f  quality %.4f->%.4f (%s)  | @1000 TP %d->%d FP %d->%d"
              % (f, b["fp"].sum(), e["fp"].sum(), b["tp"].sum(), e["tp"].sum(), med(b["delays"]), med(e["delays"]),
                 qb, qe, "ok" if q_ok else "WORSE", b1["tp"].sum(), e1["tp"].sum(), b1["fp"].sum(), e1["fp"].sum()))
    fp_b, fp_e = int(w[w["arm"] == "E2k500"]["fp"].sum()), int(w[w["arm"] == "E7"]["fp"].sum())
    ok1 = fp_e <= 0.70 * fp_b
    print("mechanism: E2-k500 FP@3000 gone in E7 = %.2f (n=%d) -> %s" % (mech, len(base_fp), "PASS" if mech >= 0.50 else "not met"))
    print("adopt E7: FP@3000 %d->%d (need <=%.1f): %s | TP@3000 loss <=1 per family: %s | quality: %s  ->  %s" % (
        fp_b, fp_e, 0.70 * fp_b, ok1, ok2, ok3,
        "E7 REPLACES E2-k500" if ok1 and ok2 and ok3 else "keep E2-k500; E7 reported as ablation"))


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


def premise() -> None:
    """E6 premise: native cut direction in REFERENCE space, replayed on the E2-k500 traces."""
    from analyze_native_direction import analyse_run
    rows, bad_fire, bad_width = [], 0, 0
    for fam, (paths, _, configs, _) in CELLS.items():
        d = os.path.join(OUT, fam, "E2k500")
        det = pd.read_csv(os.path.join(d, "detections.csv"))
        for path in paths:
            ds = dataset_key(path)
            for base_label, _, _ in configs:
                cfg = base_label.replace("/", "-E2k500/")
                sig = pd.read_csv(os.path.join(d, "signals", sig_name(ds, cfg)))
                r, _, bf, bw, _ = analyse_run(fam, sig, det[(det["dataset"] == ds) & (det["config"] == cfg)], "ref_err")
                rows, bad_fire, bad_width = rows + r, bad_fire + bf, bad_width + bw
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "e6_premise.csv"), index=False)
    missing = int((df["d_dir"] == "missing").sum() + (df["w_dir"] == "missing").sum())
    print("## E6 premise (reference space, E2-k500 traces)")
    print("validity: fire mismatches=%d  width=%d  unlinked=%d" % (bad_fire, bad_width, missing))
    if bad_fire or bad_width or missing:
        print("REPLAY INVALID -- no prediction registered")
        return
    is_fp = df["label"].isin(FP)
    for f in CELLS:
        g, gf = df[df["family"] == f], df[(df["family"] == f) & is_fp]
        p = float((gf["d_dir"] == "dec").mean()) if len(gf) else float("nan")
        tpd = int(((g["label"] == "hit") & (g["d_dir"] == "dec")).sum())
        pred = "predicted ineffective" if len(gf) >= 3 and p < 0.50 else ("mechanism check applies" if len(gf) >= 3 else "FP<3, report only")
        print("%-8s FP=%d  p_dec_ref=%.2f  TP=%d  TP_dec_ref=%d  -> %s" % (f, len(gf), p, int((g["label"] == "hit").sum()), tpd, pred))
    n_dec = int((df.loc[is_fp, "d_dir"] == "dec").sum())
    print("absorbable FP = %d of %d  -> %s" % (n_dec, int(is_fp.sum()), "PREDICTED NOT ADOPTED (<30%)"
                                              if n_dec < 0.30 * is_fp.sum() else "adoption possible"))


def analyze_stack() -> None:
    runs = runs_table()
    prem = pd.read_csv(os.path.join(OUT, "e6_premise.csv"))
    fa = runs.groupby(["family", "arm"]).agg(
        tp=("tp", "sum"), fp=("fp", "sum"), quality=("quality", "mean"),
        delay=("delay", lambda s: float(np.nanmedian(sum(s, []))) if sum(s, []) else np.nan))
    print("## E6 vs E2-k500 (quality = accuracy, or MAE for REG)")
    ok2 = ok3 = True
    fp_b = fp_e = 0
    for f in CELLS:
        b, e = fa.loc[(f, "E2k500")], fa.loc[(f, "E6")]
        dec = prem[(prem["family"] == f) & prem["label"].isin(FP) & (prem["d_dir"] == "dec")]
        n_fp = int(prem[(prem["family"] == f) & prem["label"].isin(FP)].shape[0])
        mech = gone(dec, runs, "E6")
        check = n_fp >= 3 and len(dec) >= 0.50 * n_fp
        ok2 &= b.tp - e.tp <= 1
        ok3 &= not (e.delay - b.delay > 100)
        fp_b, fp_e = fp_b + b.fp, fp_e + e.fp
        print("%-8s FP %d->%d  TP %d->%d  delay %+.0f  quality %.4f->%.4f  dec-FPs gone %s" % (
            f, b.fp, e.fp, b.tp, e.tp, e.delay - b.delay, b.quality, e.quality,
            ("%.2f (%s)" % (mech, "PASS" if mech >= 0.70 else "not met")) if check else "n/a"))
    ok1 = fp_e <= 0.70 * fp_b
    print("adopt E6: FP %d->%d (need <=%.0f): %s | TP loss <=1 per family: %s | delay +<=100: %s  ->  %s" % (
        fp_b, fp_e, 0.70 * fp_b, ok1, ok2, ok3,
        "E6 REPLACES E2-k500" if ok1 and ok2 and ok3 else "keep E2-k500; E6 reported as ablation"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=list(CELLS))
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--check", action="store_true", help="run the E1 self-check only")
    ap.add_argument("--premise", action="store_true", help="E6 premise replay on the E2-k500 traces")
    ap.add_argument("--analyze-stack", action="store_true", help="E6 vs E2-k500 verdict")
    ap.add_argument("--rescore", action="store_true", help="relabel all runs with 1000/3000-step windows")
    ap.add_argument("--analyze-delta", action="store_true", help="E7 vs E2-k500 verdict")
    a = ap.parse_args()
    self_check()
    if a.family and a.arm:
        run_cell(a.family, a.arm)
    if a.analyze:
        analyze()
    if a.premise:
        premise()
    if a.analyze_stack:
        analyze_stack()
    if a.rescore:
        rescore()
    if a.analyze_delta:
        analyze_delta()
