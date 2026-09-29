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

if __name__ == "__main__" and "--family" in sys.argv and os.path.exists("outputs/e1_e2/PAUSE"):
    # pause switch, checked before the heavy imports: a queued cell skips itself at once, while
    # running cells finish and save as usual; delete the file and relaunch the missing cells to resume
    print("skipped: outputs/e1_e2/PAUSE exists")
    sys.exit(0)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_native_direction import ARCHIVED, RERUN, sig_name  # noqa: E402
from diagnose_regression_fp import PERTURBATION, WARM_START, classify, dataset_key, discover, load_stream, run  # noqa: E402
from src.metrics import build_perturbation_intervals  # noqa: E402

OUT, E0 = "outputs/e1_e2", "outputs/e0_native_direction"
ARMS = {"E1": {"ecpf_adwin_one_sided": True},
        "E2k0": {"ecpf_reference_signal": True},
        "E2k500": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500},
        # E6 (docs/ECPF_E6_疊加_預註冊.md): E2-k500 plus the one-sided gate on the reference's loss
        "E6": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_adwin_one_sided": True},
        # E7 (docs/ECPF_E7_δ校準_預註冊.md): E2-k500 with ADWIN's usual delta (warning/drift ratio kept at 2)
        "E7": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500,
               "detector_delta": 0.002, "detector_delta_w": 0.004},
        # E9 (docs/ECPF_V1E9_預註冊.md): official-ECPF single detector on the leader's 0/1 error
        "E9d": {"ecpf_zone_detector": "ddm"},
        "E9h": {"ecpf_zone_detector": "hddm_a"},
        # new-data validation (A1+): the plain baseline has to be run there too
        "base": {},
        # E10 (docs/ECPF_E10_參照更新_預註冊.md): E2-k500 plus an age cap / a one-sided leader guard
        "E10a": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_reference_max_age": 5000},
        "E10b": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_leader_guard": True},
        # E11 (docs/ECPF_E11_逾時與超額命中_預註冊.md): the existing 1000-step warning timeout on base / E1 / E2-k500
        "baseT": {"ecpf_detector_warning_timeout": 1000},
        "E1T": {"ecpf_adwin_one_sided": True, "ecpf_detector_warning_timeout": 1000},
        "E2k500T": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_detector_warning_timeout": 1000},
        # D2 (docs/ECPF_D2_參照更新加逾時_開發檢查.md): E10a / E10b under the 1000-step timeout
        "E10aT": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_reference_max_age": 5000,
                  "ecpf_detector_warning_timeout": 1000},
        "E10bT": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_leader_guard": True,
                  "ecpf_detector_warning_timeout": 1000}}
P3 = {"ecpf_normalizer_reset_on_drift": True}  # the regression baseline (htr-nr / hfr-nr) has it on
REG_LEARNERS = [("htr/error", "htr", {}), ("hfr/error", "hfr", {})]
CELLS = {**{f: (p, s, c, False) for f, (p, s, c) in RERUN.items()},
         "REG-syn": (discover("synthetic", 2, False), 0, REG_LEARNERS, True),
         "REG-Joe": (discover("joe", 2, False), 0, REG_LEARNERS, True)}
HELD = {  # E8 held-out streams (docs/ECPF_E8_按任務δ_預註冊.md): never used in E0-E7
    "B-ho": (["data/sudden_drift/sudden_sea100k_g01.csv", "data/gradual_drift/gradual_sea100k_g01.csv",
              "data/recurring_drift/recurring_sud_sea100k_g01.csv"], 30000, RERUN["B"][2], False),
    "MC-syn-ho": (sorted(glob.glob("data/heldout_s1042/synthetic_multiclass/mc*_20k.csv")), 20000,
                  RERUN["MC-syn"][2], False),
    "MC-RBF-ho": (sorted(p for p in glob.glob("data/synthetic_dataset_joe/multi classification/*_drift/*/"
                                              "recurring_*_rbf4_100k_g01.csv") if "incremental" not in p),
                  20000, RERUN["MC-syn"][2], False),
    "REG-syn-ho": (sorted(glob.glob("data/heldout_s1042/synthetic_regression/*.csv")), 0, REG_LEARNERS, True),
    "REG-Joe-ho": (sorted(glob.glob("data/synthetic_dataset_joe/regression/sudden_drift/*/"
                                    "recurring_sudden_friedman_100k_g0[23].csv")), 0, REG_LEARNERS, True),
}
_INJ = "data/dataset_0921/injected_real_dataset/binary/*/{m}/electricity_{m}_*_g0[0-2].csv"
_INS = "data/dataset_0921/insects_dataset/multi_classification/{v}/{v}.csv"
A1 = {  # A1 (docs/ECPF_A1_新資料驗證_預註冊.md); split into sub-families only to run cells in parallel
    **{"INJ-elec-" + k: (sorted(glob.glob(_INJ.format(m=m))), 0, RERUN["B"][2], False)
       for k, m in (("cp", "class_prior"), ("ls", "label_swap"), ("fp", "feature_permutation"),
                    ("ff", "feature_filtering"))},
    **{"INS-" + k: ([_INS.format(v=v)], 0, [RERUN["MC-syn"][2][0]], False)
       for k, v in (("abrupt", "abrupt_balanced"), ("incabrupt", "incremental_abrupt_reoccurring_balanced"),
                    ("increc", "incremental_reoccurring_balanced"), ("incgrad", "incremental_gradual_balanced"),
                    ("inc", "incremental_balanced"))},
}
_SYN = "data/dataset_0921/synthetic_dataset/{t}/{d}/*_g00.csv"
_GAS = "data/dataset_0921/injected_real_dataset/multi_classification/*/{m}/gas_sensor_drift_{m}_*_g0[0-2].csv"
A2 = {  # A2 (docs/ECPF_A2_新資料驗證_預註冊.md); one sub-family per stream / method, only to run cells in parallel
    **{"SYN2-%s-%s" % (g, k): (sorted(glob.glob(_SYN.format(t=t, d=d))), 0, cfg, g == "REG")
       for g, t, cfg in (("B", "binary", RERUN["B"][2]), ("MC", "multi_classification", [RERUN["MC-syn"][2][0]]),
                         ("REG", "regression", REG_LEARNERS))
       for k, d in (("sud", "sudden"), ("grad", "gradual"), ("inc", "incremental"), ("rec", "recurring"))},
    **{"INJ-gas-" + k: (sorted(glob.glob(_GAS.format(m=m))), 0, [RERUN["MC-syn"][2][0]], False)
       for k, m in (("cp", "class_prior"), ("ls", "label_swap"), ("fp", "feature_permutation"),
                    ("ff", "feature_filtering"))},
}
E10 = {  # E10 judges on fresh data only: synthetic v2 g01 and gas g03-g05, same layout as A2
    **{"SYN2g01-%s-%s" % (g, k): (sorted(glob.glob(_SYN.replace("g00", "g01").format(t=t, d=d))), 0, cfg, g == "REG")
       for g, t, cfg in (("B", "binary", RERUN["B"][2]), ("MC", "multi_classification", [RERUN["MC-syn"][2][0]]),
                         ("REG", "regression", REG_LEARNERS))
       for k, d in (("sud", "sudden"), ("grad", "gradual"), ("inc", "incremental"), ("rec", "recurring"))},
    **{"INJgas35-" + k: (sorted(glob.glob(_GAS.replace("g0[0-2]", "g0[3-5]").format(m=m))), 0,
                         [RERUN["MC-syn"][2][0]], False)
       for k, m in (("cp", "class_prior"), ("ls", "label_swap"), ("fp", "feature_permutation"),
                    ("ff", "feature_filtering"))},
}
E11 = {  # E11 judges on fresh data: synthetic v2 g02 + g03 (the two seeds pool into one group) and gas g06-g08
    **{"SYN2g23-%s-%s%s" % (g, k, sd): (sorted(glob.glob(_SYN.replace("g00", "g0" + sd).format(t=t, d=d))), 0, cfg,
                                        g == "REG")
       for sd in ("2", "3")
       for g, t, cfg in (("B", "binary", RERUN["B"][2]), ("MC", "multi_classification", [RERUN["MC-syn"][2][0]]),
                         ("REG", "regression", REG_LEARNERS))
       for k, d in (("sud", "sudden"), ("grad", "gradual"), ("inc", "incremental"), ("rec", "recurring"))},
    **{"INJgas68-" + k: (sorted(glob.glob(_GAS.replace("g0[0-2]", "g0[6-8]").format(m=m))), 0,
                         [RERUN["MC-syn"][2][0]], False)
       for k, m in (("cp", "class_prior"), ("ls", "label_swap"), ("fp", "feature_permutation"),
                    ("ff", "feature_filtering"))},
}
E12 = {  # E12 judges on fresh data: synthetic v2 g04 + g05 (pooled per group) and gas g09
    **{"SYN2g45-%s-%s%s" % (g, k, sd): (sorted(glob.glob(_SYN.replace("g00", "g0" + sd).format(t=t, d=d))), 0, cfg,
                                        g == "REG")
       for sd in ("4", "5")
       for g, t, cfg in (("B", "binary", RERUN["B"][2]), ("MC", "multi_classification", [RERUN["MC-syn"][2][0]]),
                         ("REG", "regression", REG_LEARNERS))
       for k, d in (("sud", "sudden"), ("grad", "gradual"), ("inc", "incremental"), ("rec", "recurring"))},
    **{"INJgas9-" + k: (sorted(glob.glob(_GAS.replace("g0[0-2]", "g09").format(m=m))), 0,
                        [RERUN["MC-syn"][2][0]], False)
       for k, m in (("cp", "class_prior"), ("ls", "label_swap"), ("fp", "feature_permutation"),
                    ("ff", "feature_filtering"))},
}
ALL = {**CELLS, **HELD, **A1, **A2, **E10, **E11, **E12}


def scored_gt(fam: str, intervals):
    """A2 rule (prereg): GT intervals that start inside the warm-up are not scored."""
    return [iv for iv in intervals if iv[0] >= WARM_START] if fam in A2 or fam in E10 or fam in E11 or fam in E12 else intervals
FP = ("echo", "orphan")
MATCH = 500
SIG_COLS = ["t", "err", "raw", "is_warning", "is_drift", "ref_err", "ref_age", "ref_switch", "switch_warning_age",
            "ref_refresh", "guard_drift"]


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
    # E9 zone detectors: a 0.1 -> 0.5 error jump must give warning then drift; a drop must never fire
    import random
    from src.ecpf_detector import ECPFZoneDetector
    rng = random.Random(0)
    jump = [int(rng.random() < 0.1) for _ in range(2000)] + [int(rng.random() < 0.5) for _ in range(600)]
    drop = [int(rng.random() < 0.5) for _ in range(2000)] + [int(rng.random() < 0.1) for _ in range(2000)]
    for kind in ("ddm", "hddm_a"):
        z, warned, first = ECPFZoneDetector(kind), False, None
        for i, x in enumerate(jump):
            w, dr = z.update_values(x, x)
            if i >= 2000 and first is None:
                warned = warned or (w and not dr)
                if dr:
                    first = i
        assert first is not None and first < 2600 and warned, kind
        z, fired = ECPFZoneDetector(kind), 0
        for i, x in enumerate(drop):
            fired += (z.update_values(x, x)[1] and i >= 2000)
        assert fired == 0, kind
    # E11 excess hits: a detector that ignores the drifts must score ~0 excess hits on average
    rng, xs = np.random.default_rng(0), []
    wins = [(s, s + 3000) for s in range(5000, 95000, 10000)]
    for _ in range(200):
        det = rng.integers(WARM_START, 100000, rng.poisson(30))
        tp = sum(bool(((det >= s) & (det < e)).any()) for s, e in wins)
        fp = sum(not any(s <= d < e for s, e in wins) for d in det)
        xs.append(tp - expected_chance(fp, 100000 - WARM_START - 3000 * len(wins), [3000] * len(wins)))
    assert abs(np.mean(xs)) < 0.3, np.mean(xs)


def check_e10() -> None:
    """E10 gates (docs/ECPF_E10_參照更新_預註冊.md), through the pipeline itself; run with --check before launching."""
    from src.config import PipelineConfig
    from src.pipeline import ConceptDriftPipeline

    class Flat:  # a reference detector that never fires: only the E10b guard can confirm
        zone, combo_name, stats = False, "flat", {}

        def update_values(self, w, d):
            return False, False

        def reset(self):
            pass

    def pipe_run(X, y, flags, flat_ref=False):
        pipe = ConceptDriftPipeline(PipelineConfig(
            model_type="ht", use_ecpf=True, ecpf_signal_mode="dual_adwin", ecpf_warning_signal="error",
            ecpf_drift_signal="error", ecpf_detector_min_instances=30, trace_enabled=True, **flags))
        if flat_ref:
            pipe._ecpf_detector = Flat()
        dets = [(int(d.timestamp), i) for i, _, _, ds, _ in pipe.run_stream(X, y, warm_start_samples=WARM_START)
                for d in ds]
        return pd.DataFrame(pipe.tracer._signals), dets
    rng = np.random.default_rng(0)
    X = rng.random((5000, 2))
    easy = (X[:, 0] > 0.5).astype(int)
    sig, dets = pipe_run(X, easy, {**ARMS["E10a"], "ecpf_reference_max_age": 1000})
    assert not dets and sig["is_warning"].sum() == 0, "E10a check needs a warning-free stream"
    assert sig["ref_age"].max() < 1000 and sig["ref_refresh"].sum() >= 4       # E10a: age capped at R
    t = np.arange(5000)
    _, dets = pipe_run(X, np.where(t < 2500, easy, 1 - easy), ARMS["E10b"], flat_ref=True)
    assert any(c >= 2500 for _, c in dets)                                      # leader error up: guard confirms
    _, dets = pipe_run(X, np.where(t < 2500, rng.integers(0, 2, 5000), easy), ARMS["E10b"], flat_ref=True)
    assert not any(w >= 2500 for w, _ in dets)                                  # leader error down: guard quiet


def run_cell(family: str, arm: str) -> None:
    paths, max_steps, configs, is_reg = ALL[family]
    d = os.path.join(OUT, family, arm)
    os.makedirs(os.path.join(d, "signals"), exist_ok=True)
    rows = []
    for path in paths:
        key = dataset_key(path)
        for base_label, mt, mk in configs:
            label = base_label.replace("/", "-%s/" % arm)
            pk = {**ARMS[arm], **(P3 if is_reg else {})}
            sig, dets, swaps, stage3, intervals, _, n = run(path, mt, max_steps, mk, pk)
            for r in classify(dets, scored_gt(family, intervals), sig, swaps, n):
                rows.append({**r, "dataset": key, "config": label, "path": path})
            with gzip.open(os.path.join(d, "signals", sig_name(key, label)), "wt") as f:
                sig[[c for c in SIG_COLS if c in sig.columns]].to_csv(f, index=False)
            print(family, arm, key, label, "detections=%d swaps=%d" % (len(dets), len(swaps)), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(d, "detections.csv"), index=False)


# ---------------------------------------------------------------------------
def iter_runs(held: bool = False):
    """Yield (family, arm, path, dataset, config, detections, signals) for every run in the matrix
    (held=True: only the E8 held-out families, which have no base arm).

    Runs are enumerated from the matrix, not from detections.csv: a run with zero
    confirmations has no rows there but still counts.
    """
    def runs_of(fam, arm, det_csv, sig_dir, labels):
        try:
            det = pd.read_csv(det_csv)
        except pd.errors.EmptyDataError:  # a cell with zero confirmations in every run writes an empty file
            det = pd.DataFrame(columns=["dataset", "config", "warning_t", "confirmation_t", "label", "gap_prev_gt"])
        for path in ALL[fam][0]:
            ds = dataset_key(path)
            for cfg in labels:
                yield (fam, arm, path, ds, cfg, det[(det["dataset"] == ds) & (det["config"] == cfg)],
                       pd.read_csv(os.path.join(sig_dir, sig_name(ds, cfg))))
    for fam, (_, _, configs) in ({} if held else RERUN).items():  # baselines: E0 reruns + archives
        yield from runs_of(fam, "base", os.path.join(E0, fam, "detections.csv"), os.path.join(E0, fam, "signals"),
                           [c for c, _, _ in configs])
    for fam, d, cfgs in ([] if held else ARCHIVED):
        yield from runs_of(fam, "base", os.path.join(d, "detections_labelled.csv"), os.path.join(d, "signals"),
                           sorted(cfgs))
    for fam, (_, _, configs, _) in (E12 if held == "e12" else E11 if held == "e11" else E10 if held == "e10" else A2 if held == "a2" else A1 if held == "a1" else HELD if held else CELLS).items():
        for arm in ARMS:
            d = os.path.join(OUT, fam, arm)
            if os.path.exists(os.path.join(d, "detections.csv")):  # cell finished
                yield from runs_of(fam, arm, os.path.join(d, "detections.csv"), os.path.join(d, "signals"),
                                   [c.replace("/", "-%s/" % arm) for c, _, _ in configs])


def runs_table(held: bool = False):
    """One row per (family, arm, dataset, learner): hits, FP, delay, accuracy/MAE, detection times."""
    recs = []
    for fam, arm, path, ds, cfg, g, sig in iter_runs(held):
        hits = g[g["label"] == "hit"]
        recs.append({"family": fam, "arm": arm, "dataset": ds, "learner": learner(cfg),
                     "tp": len(hits), "fp": int(g["label"].isin(FP).sum()),
                     "delay": pd.to_numeric(hits["gap_prev_gt"], errors="coerce").tolist(),
                     "quality": float(sig["raw"].mean() if ALL[fam][3] else 1 - sig["err"].mean()),
                     "conf_t": g["confirmation_t"].astype(int).tolist(), "path": path, "sig": sig})
    return pd.DataFrame(recs)


def rescore(exts=(1000, 3000), show: bool = True, held: bool = False):
    """Relabel every run with wider scoring windows -- classify() itself, only PERTURBATION changes.
    ext=1000 must reproduce the stored labels exactly (checked). Returns one row per (run, ext)."""
    import diagnose_regression_fp as drf
    recs, gt = [], {}
    for fam, arm, path, ds, cfg, g, sig in iter_runs(held):
        key = (path, ALL[fam][1])
        if key not in gt:
            gt[key] = scored_gt(fam, load_stream(path, ALL[fam][1])[2])
        dets = list(zip(g["warning_t"].astype(int), g["confirmation_t"].astype(int)))
        for ext in exts:
            drf.PERTURBATION = ext
            rows = drf.classify(dets, gt[key], sig, [], len(sig))
            labels = [r["label"] for r in rows]
            start = gt[key][0][0] if gt[key] else None
            recs.append({"family": fam, "arm": arm, "ext": ext, "dataset": ds, "learner": learner(cfg),
                         "tp": labels.count("hit"), "fp": sum(lab in FP for lab in labels),
                         "delays": [float(r["gap_prev_gt"]) for r in rows if r["label"] == "hit"],
                         "fp_t": [r["confirmation_t"] for r in rows if r["label"] in FP],
                         "conf_t": [r["confirmation_t"] for r in rows],
                         "warn_t": [r["warning_t"] for r in rows],
                         "pre": sum(start is not None and r["warning_t"] < start for r in rows),
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
    df.drop(columns=["delays", "fp_t", "conf_t", "warn_t"]).to_csv(os.path.join(OUT, "rescore.csv"), index=False)
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


def analyze_e8() -> None:
    """E8 verdict on the held-out streams (docs/ECPF_E8_按任務δ_預註冊.md): E7 vs E2k500, 3000-step window."""
    df = rescore(show=False, held=True)
    if df is None:
        print("RESCORE INVALID -- no verdict")
        return
    q = runs_table(held=True).groupby(["family", "arm"])["quality"].mean()
    w = df[df["ext"] == 3000]
    med = lambda s: float(np.median(sum(s, []))) if sum(s, []) else np.nan
    cls, reg = ["B-ho", "MC-syn-ho", "MC-RBF-ho"], ["REG-syn-ho", "REG-Joe-ho"]
    print("## E8 held-out: E7 (delta 0.002/0.004) vs E2k500 (0.05/0.1), 3000-step window")
    tp_loss, qual_ok = {}, {}
    for f in cls + reg:
        b, e = (w[(w["family"] == f) & (w["arm"] == a)] for a in ("E2k500", "E7"))
        b1, e1 = (df[(df["ext"] == 1000) & (df["family"] == f) & (df["arm"] == a)] for a in ("E2k500", "E7"))
        qb, qe = q[(f, "E2k500")], q[(f, "E7")]
        tp_loss[f] = int(b["tp"].sum() - e["tp"].sum())
        qual_ok[f] = bool(qe <= 1.02 * qb if f in reg else qe >= qb - 0.005)
        print("%-10s FP@3000 %d->%d  TP@3000 %d->%d  delay %.0f->%.0f  quality %.4f->%.4f  | @1000 TP %d->%d FP %d->%d"
              % (f, b["fp"].sum(), e["fp"].sum(), b["tp"].sum(), e["tp"].sum(), med(b["delays"]), med(e["delays"]),
                 qb, qe, b1["tp"].sum(), e1["tp"].sum(), b1["fp"].sum(), e1["fp"].sum()))
    fp = lambda fams, arm: int(w[w["family"].isin(fams) & (w["arm"] == arm)]["fp"].sum())
    # (a) classification replication
    a1 = fp(cls, "E7") <= 0.70 * fp(cls, "E2k500")
    a2 = all(tp_loss[f] <= 1 for f in cls)
    a3 = all(qual_ok[f] for f in cls)
    a_pass = a1 and a2 and a3
    print("(a) classification: FP@3000 %d->%d (need <=%.1f): %s | TP loss <=1: %s | accuracy: %s  ->  %s" % (
        fp(cls, "E2k500"), fp(cls, "E7"), 0.70 * fp(cls, "E2k500"), a1, a2, a3, "PASS" if a_pass else "FAIL"))
    # (b) does regression really need the original delta?
    split = any(tp_loss[f] > 1 for f in reg) or fp(reg, "E7") > fp(reg, "E2k500")
    print("(b) regression: TP loss %s, FP@3000 %d->%d  ->  split %s" % (
        {f: tp_loss[f] for f in reg}, fp(reg, "E2k500"), fp(reg, "E7"), "SUPPORTED" if split else "NOT supported"))
    # mechanism (report only)
    e7 = {(r.family, r.dataset, r.learner): r.conf_t for r in w[(w["arm"] == "E7") & w["family"].isin(cls)].itertuples()}
    ev = [((r.family, r.dataset, r.learner), t) for r in w[(w["arm"] == "E2k500") & w["family"].isin(cls)].itertuples()
          for t in r.fp_t]
    if ev:
        g = float(np.mean([all(abs(c - t) > MATCH for c in e7.get(k, [])) for k, t in ev]))
        print("mechanism (report only): classification E2k500 FP@3000 gone in E7 = %.2f (n=%d)" % (g, len(ev)))
    verdict = ("ADOPT task-specific delta: classification 0.002/0.004, regression 0.05/0.1" if a_pass and split
               else "split refuted: ADOPT uniform delta 0.002/0.004" if a_pass
               else "classification gain did not replicate: keep uniform delta 0.05/0.1 (E2-k500)")
    print("E8 verdict: %s" % verdict)


def analyze_e9() -> None:
    """E9 verdict (docs/ECPF_V1E9_預註冊.md): official-ECPF single detectors vs base / E1 / E2-k500."""
    df = rescore(show=False)
    if df is None:
        print("RESCORE INVALID -- no verdict")
        return
    runs = runs_table()
    q = runs.groupby(["family", "arm"])["quality"].mean()
    cls, arms = ["B", "MC-syn", "MC-RBF"], ["base", "E1", "E2k500", "E9d", "E9h"]
    med = lambda s: float(np.median(sum(s, []))) if sum(s, []) else np.nan
    print("## E9: official-ECPF detectors (classification families)")
    print("%-8s %-7s %8s %8s %8s %8s %8s %9s" % ("family", "arm", "FP@1000", "TP@1000", "FP@3000", "TP@3000",
                                                "delay", "accuracy"))
    for f in cls:
        for a in arms:
            if (f, a) not in q.index:
                continue
            g1 = df[(df["ext"] == 1000) & (df["family"] == f) & (df["arm"] == a)]
            g3 = df[(df["ext"] == 3000) & (df["family"] == f) & (df["arm"] == a)]
            print("%-8s %-7s %8d %8d %8d %8d %8.0f %9.4f" % (f, a, g1["fp"].sum(), g1["tp"].sum(), g3["fp"].sum(),
                                                            g3["tp"].sum(), med(g1["delays"]), q[(f, a)]))
    grad = runs[(runs["family"] == "MC-RBF") & runs["dataset"].str.startswith("gradual")].groupby("arm")["tp"].sum()
    print("MC-RBF gradual hits @1000: %s" % {a: int(grad.get(a, 0)) for a in arms})
    base_fp = int(df[(df["ext"] == 1000) & df["family"].isin(cls) & (df["arm"] == "base")]["fp"].sum())
    p2 = {}
    for det in ("E9d", "E9h"):
        fp = int(df[(df["ext"] == 1000) & df["family"].isin(cls) & (df["arm"] == det)]["fp"].sum())
        p1 = fp <= 0.5 * base_fp
        g = int(grad.get(det, 0))
        p2[det] = (g <= 8, g, p1)
        print("%s: P1 FP@1000 %d vs base %d (need <=%.1f): %s | P2 MC-RBF gradual hits %d (need <=8): %s" % (
            det, fp, base_fp, 0.5 * base_fp, p1, g, g <= 8))
    if all(v[0] for v in p2.values()):
        verdict = "CLAIM SUPPORTED: switching the detector algorithm does not fix the masked gradual drifts"
    elif any(v[1] >= 11 and v[2] for v in p2.values()):
        verdict = "CLAIM REFUTED: a detector alone recovers the gradual drifts with low FP"
    else:
        verdict = "mixed: report as is, no conclusion"
    print("E9 verdict: %s" % verdict)


def analyze_a1() -> None:
    """A1 verdict (docs/ECPF_A1_新資料驗證_預註冊.md): base vs E1 vs E2-k500 on new data."""
    df = rescore(show=False, held="a1")
    if df is None:
        print("RESCORE INVALID -- no verdict")
        return
    q = runs_table(held="a1").groupby(["family", "arm"])["quality"].mean()
    arms, med = ["base", "E1", "E2k500"], lambda s: float(np.median(sum(s, []))) if sum(s, []) else np.nan
    inj = df[df["family"].str.startswith("INJ-elec")]
    print("## A1 injected electricity (24 streams x ht, hf10; one drift per stream)")
    print("%-5s %-7s %6s %8s %8s %8s %8s %8s %9s" % ("method", "arm", "preFP", "TP@1000", "TP@3000", "FP@1000",
                                                  "FP@3000", "delay", "accuracy"))
    for k in ("cp", "ls", "fp", "ff"):
        for a in arms:
            f = "INJ-elec-" + k
            g1 = inj[(inj["family"] == f) & (inj["arm"] == a) & (inj["ext"] == 1000)]
            g3 = inj[(inj["family"] == f) & (inj["arm"] == a) & (inj["ext"] == 3000)]
            if not len(g1):
                continue
            print("%-5s %-7s %6d %8d %8d %8d %8d %8.0f %9.4f" % (k, a, g1["pre"].sum(), g1["tp"].sum(), g3["tp"].sum(),
                                                            g1["fp"].sum(), g3["fp"].sum(), med(g3["delays"]), q[(f, a)]))
    tot = {a: inj[(inj["arm"] == a) & (inj["ext"] == 3000)] for a in arms}
    pre = {a: int(tot[a]["pre"].sum()) for a in arms}
    tp = {a: int(tot[a]["tp"].sum()) for a in arms}
    grad = {a: int(tot[a][tot[a]["dataset"].str.contains("_gradual_")]["tp"].sum()) for a in arms}
    acc = {a: float(np.mean([q[("INJ-elec-" + k, a)] for k in ("cp", "ls", "fp", "ff")])) for a in arms}
    print("pooled: pre-drift FP %s | TP@3000 %s | gradual TP@3000 %s | accuracy %s" % (
        pre, tp, grad, {a: round(v, 4) for a, v in acc.items()}))
    ok = {}
    for a in ("E1", "E2k500"):
        p1 = pre["base"] >= 10 and pre[a] <= 0.30 * pre["base"]
        p2 = tp[a] >= 0.90 * tp["base"]
        ok[a] = p1 and p2
        print("%s: P1 pre-drift FP %d vs base %d (need <=%.1f, base>=10): %s | P2 TP@3000 %d vs base %d (need >=%.1f): %s"
              % (a, pre[a], pre["base"], 0.30 * pre["base"], p1, tp[a], tp["base"], 0.90 * tp["base"], p2))
    print("P3 gradual TP@3000 E2k500 %d vs E1 %d -> %s" % (grad["E2k500"], grad["E1"], grad["E2k500"] >= grad["E1"]))

    ins = df[df["family"].str.startswith("INS-")]
    print("\n## A1 INSECTS (hf10 masked)")
    print("%-10s %-7s %8s %8s %8s %8s %9s" % ("variant", "arm", "FP@1000", "TP@1000", "FP@3000", "TP@3000", "accuracy"))
    for k in ("abrupt", "incabrupt", "increc", "incgrad", "inc"):
        for a in arms:
            f = "INS-" + k
            g1 = ins[(ins["family"] == f) & (ins["arm"] == a) & (ins["ext"] == 1000)]
            g3 = ins[(ins["family"] == f) & (ins["arm"] == a) & (ins["ext"] == 3000)]
            if len(g1):
                print("%-10s %-7s %8d %8d %8d %8d %9.4f" % (k, a, g1["fp"].sum(), g1["tp"].sum(), g3["fp"].sum(),
                                                        g3["tp"].sum(), q[(f, a)]))
    ab = {a: ins[(ins["family"] == "INS-abrupt") & (ins["arm"] == a) & (ins["ext"] == 3000)] for a in arms}
    if all(len(v) for v in ab.values()):
        p4 = ab["E2k500"]["fp"].sum() <= ab["base"]["fp"].sum() and ab["E2k500"]["tp"].sum() >= ab["E1"]["tp"].sum()
        print("P4 INSECTS abrupt: E2k500 FP@3000 %d vs base %d, TP@3000 %d vs E1 %d -> %s (supporting evidence only)" % (
            ab["E2k500"]["fp"].sum(), ab["base"]["fp"].sum(), ab["E2k500"]["tp"].sum(), ab["E1"]["tp"].sum(), p4))
    print("\nA1 verdict: E2-k500 %s on new data; E1 %s on new data" % (
        "HOLDS" if ok["E2k500"] else "does NOT hold", "HOLDS" if ok["E1"] else "does NOT hold"))


def expected_chance(fp: float, outside: float, lens) -> float:
    """Hits a Poisson false-alarm process at a run's own out-of-window rate scores by chance
    (docs/ECPF_E11_逾時與超額命中_預註冊.md): sum over windows of 1 - exp(-rate * window length)."""
    lam = fp / outside if outside > 0 else 0.0
    return float(sum(1 - np.exp(-lam * L) for L in lens))


def chance_hits(df):
    """expected_chance() for every rescore row; windows = scored GT + the row's ext, clipped to the stream."""
    gts, out = {}, []
    for r in df.itertuples():
        if (r.family, r.dataset) not in gts:
            path = next(p for p in ALL[r.family][0] if dataset_key(p) == r.dataset)
            _, y, iv = load_stream(path, ALL[r.family][1])
            gts[(r.family, r.dataset)] = (len(y), scored_gt(r.family, iv))
        n, iv = gts[(r.family, r.dataset)]
        wins, cover, end = sorted((s, min(e + r.ext, n)) for s, e in iv), 0, WARM_START
        for s, e in wins:   # length of the union of the windows
            cover += max(0, e - max(s, end))
            end = max(end, e)
        out.append(expected_chance(r.fp, n - WARM_START - cover, [e - s for s, e in wins]))
    return out


def new_data_criteria(label: str, held: str, groups, arms, judged, ref: str = "base", excess: bool = False,
                      per_method: int = 6):
    """Per-group tables and the new-data criteria P1-P4 that A2, E10 and E11 share.
    groups = [B, MC, REG, gas] family groups (a family is group + '-' + suffix); ref = the baseline arm;
    excess=True (E11): P2/P3 recall is excess hits, not TP@3000. Returns (ok, df, runs), or None."""
    df = rescore(show=False, held=held)
    if df is None:
        print("RESCORE INVALID -- no verdict")
        return None
    runs = runs_table(held=held)
    grp = lambda f: f.rsplit("-", 1)[0]   # SYN2-B-sud -> SYN2-B
    df["group"], runs["group"] = df["family"].map(grp), runs["family"].map(grp)
    if excess:
        df["xs"] = df["tp"] - np.array(chance_hits(df))
    rc, rname = ("xs", "excess@3000") if excess else ("tp", "TP@3000")
    fv = (lambda v: "%.1f" % v) if excess else (lambda v: "%d" % v)
    med = lambda s: float(np.median(sum(s, []))) if sum(s, []) else np.nan
    q, qf = runs.groupby(["group", "arm"])["quality"].mean(), runs.groupby(["family", "arm"])["quality"].mean()
    d1, d3 = df[df["ext"] == 1000], df[df["ext"] == 3000]
    tot = lambda d, g, a, c: int(d[(d["group"] == g) & (d["arm"] == a)][c].sum())
    ftot = lambda d, g, a, c: float(d[(d["group"] == g) & (d["arm"] == a)][c].sum())
    B, MC, REG, gas = groups
    print("## %s per group (quality = accuracy, or MAE for %s; delay = median hit delay at 3000)" % (label, REG))
    print("%-9s %-7s %8s %8s %8s %8s %7s %9s" % ("group", "arm", "TP@1000", "FP@1000", "TP@3000", "FP@3000", "delay",
                                               "quality") + (" %8s" % "excess" if excess else ""))
    for g in groups:
        for a in arms:
            print("%-9s %-7s %8d %8d %8d %8d %7.0f %9.4f" % (
                g, a, tot(d1, g, a, "tp"), tot(d1, g, a, "fp"), tot(d3, g, a, "tp"), tot(d3, g, a, "fp"),
                med(d3[(d3["group"] == g) & (d3["arm"] == a)]["delays"]), q[(g, a)])
                + (" %8.1f" % ftot(d3, g, a, "xs") if excess else ""))
    print("\n## %s per injection method (%d streams each, one drift per stream)" % (gas, per_method))
    print("%-6s %-7s %6s %8s %8s %8s %8s %9s" % ("method", "arm", "preFP", "TP@1000", "TP@3000", "FP@1000", "FP@3000",
                                              "accuracy"))
    for k in ("cp", "ls", "fp", "ff"):
        for a in arms:
            f = gas + "-" + k
            g1, g3 = (d[(d["family"] == f) & (d["arm"] == a)] for d in (d1, d3))
            print("%-6s %-7s %6d %8d %8d %8d %8d %9.4f" % (k, a, g1["pre"].sum(), g1["tp"].sum(), g3["tp"].sum(),
                                                         g1["fp"].sum(), g3["fp"].sum(), qf[(f, a)]))

    print("\n## Criteria")
    pre = {a: tot(d3, gas, a, "pre") for a in arms}
    rec = {a: ftot(d3, gas, a, rc) for a in arms}
    ok = {a: {} for a in judged}
    for a in ok:
        ok[a]["P1"] = (pre[a] <= 0.30 * pre[ref]) if pre[ref] >= 10 else None   # None: not evaluable
        ok[a]["P2"] = rec[a] >= 0.90 * rec[ref]
        print("%s: P1 pre-drift FP %d vs %s %d (need <=%.1f, %s>=10): %s | P2 %s %s vs %s %s (need >=%.1f): %s"
              % (a, pre[a], ref, pre[ref], 0.3 * pre[ref], ref, ok[a]["P1"], rname, fv(rec[a]), ref, fv(rec[ref]),
                 0.9 * rec[ref], ok[a]["P2"]))
        for g in (B, MC, REG):
            bfp, efp = tot(d3, g, ref, "fp"), tot(d3, g, a, "fp")
            btp, etp = ftot(d3, g, ref, rc), ftot(d3, g, a, rc)
            fp_ok = efp <= 0.5 * bfp if bfp >= 6 else None          # None: FP part not evaluable
            tp_ok = etp >= 0.9 * btp
            ok[a]["P3-" + g] = tp_ok and fp_ok is not False
            print("%s: P3 %s FP@3000 %d vs %s %d (%s) | %s %s vs %s %s (need >=%.1f): %s -> %s" % (
                a, g, efp, ref, bfp, "not evaluable" if fp_ok is None else "need <=%.1f: %s" % (0.5 * bfp, fp_ok),
                rname, fv(etp), ref, fv(btp), 0.9 * btp, tp_ok, ok[a]["P3-" + g]))
        for g in groups:
            qb, qe = q[(g, ref)], q[(g, a)]
            ok[a]["P4-" + g] = qe <= 1.02 * qb if g == REG else qe >= qb - 0.01
            print("%s: P4 %s quality %.4f vs %s %.4f: %s" % (a, g, qe, ref, qb, ok[a]["P4-" + g]))
    return ok, df, runs


def analyze_a2() -> None:
    """A2 verdict (docs/ECPF_A2_新資料驗證_預註冊.md): base vs E1 vs E2-k500 on synthetic v2 and injected gas."""
    arms, grp = ["base", "E1", "E2k500"], lambda f: f.rsplit("-", 1)[0]
    res = new_data_criteria("A2", "a2", ["SYN2-B", "SYN2-MC", "SYN2-REG", "INJ-gas"], arms, ["E1", "E2k500"])
    if res is None:
        return
    ok, df, runs = res
    d3 = df[df["ext"] == 3000]
    sub = d3[d3["dataset"].str.contains("gradual|incremental")]
    p5 = {a: int(sub[sub["arm"] == a]["tp"].sum()) for a in arms}
    print("P5 gradual+incremental TP@3000 %s -> E2k500 >= E1: %s" % (p5, p5["E2k500"] >= p5["E1"]))
    hp = d3[d3["dataset"].str.contains("hyperplane")]
    print("hyperplane incremental: confirmations with warning in [200, 1950] (unscored GT [0, 950]): %s" % {
        a: sum(200 <= w <= 1950 for ws in hp[hp["arm"] == a]["warn_t"] for w in ws) for a in arms})
    for a in ok:
        cls = all(ok[a][k] for k in ("P1", "P2", "P3-SYN2-B", "P3-SYN2-MC", "P4-SYN2-B", "P4-SYN2-MC", "P4-INJ-gas"))
        reg = ok[a]["P3-SYN2-REG"] and ok[a]["P4-SYN2-REG"]
        print("A2 verdict %s: classification %s; regression %s" % (
            a, "HOLDS" if cls else "does NOT hold", "HOLDS" if reg else "does NOT hold"))

    print("\n## Stale-reference check: E2-k500 max reference age per group; aligned tail after its last freeze")
    rows = []
    for (f, ds, lr), g in runs.groupby(["family", "dataset", "learner"]):
        s = {r.arm: r.sig for r in g.itertuples()}
        e2 = s.get("E2k500")
        if e2 is None or "ref_age" not in e2.columns:
            continue
        t0 = int(e2.loc[e2["ref_age"] <= 1, "t"].iloc[-1])   # last freeze: switch (age 0) or confirmation (age 1)
        n = int(e2["t"].iloc[-1]) - t0
        val = lambda x: float(x.loc[x["t"] >= t0, "raw"].mean() if ALL[f][3] else 1 - x.loc[x["t"] >= t0, "err"].mean())
        rows.append({"group": grp(f), "run": "%s %s" % (ds, lr), "max_age": int(e2["ref_age"].max()), "tail": n,
                     **({a: val(s[a]) for a in arms if a in s} if n >= 5000 else {})})
    st = pd.DataFrame(rows)
    print(st.groupby("group")["max_age"].max().to_string())
    long = st[st["tail"] >= 5000]
    print(long.round(4).to_string(index=False) if len(long) else "no run has a tail >= 5000 steps")


def analyze_e10() -> None:
    """E10 verdict (docs/ECPF_E10_參照更新_預註冊.md): E10a / E10b on fresh data; E1 and E2-k500 are references."""
    groups, arms = ["SYN2g01-B", "SYN2g01-MC", "SYN2g01-REG", "INJgas35"], ["base", "E1", "E2k500", "E10a", "E10b"]
    res = new_data_criteria("E10", "e10", groups, arms, ["E10a", "E10b"])
    if res is None:
        return
    ok, df, runs = res
    B, MC, REG, gas = groups
    d3 = df[df["ext"] == 3000]
    tp = lambda a, gs: int(d3[(d3["arm"] == a) & d3["group"].isin(gs)]["tp"].sum())
    sub = d3[d3["dataset"].str.contains("gradual|incremental")]
    print("gradual+incremental TP@3000 %s" % {a: int(sub[sub["arm"] == a]["tp"].sum()) for a in arms})
    for task, keys, gs in (("classification", ["P1", "P2", "P3-" + B, "P3-" + MC, "P4-" + B, "P4-" + MC, "P4-" + gas],
                            [B, MC, gas]), ("regression", ["P3-" + REG, "P4-" + REG], [REG])):
        passed = [a for a in ok if all(ok[a][k] for k in keys)]
        if len(passed) == 2:   # both pass: more TP@3000 wins; within 2 hits, the simpler E10a
            pick = "E10b" if tp("E10b", gs) - tp("E10a", gs) > 2 else "E10a"
        else:
            pick = passed[0] if passed else None
        print("E10 verdict %s: passed %s; TP@3000 E10a %d, E10b %d -> %s" % (
            task, passed or "none", tp("E10a", gs), tp("E10b", gs),
            "ADOPT " + pick if pick else "neither adopted: E2-k500's long-stream recall problem remains"))

    print("\n## Mechanism (reported, not judged)")
    rows, gts = [], {}
    for (f, ds, lr), g in runs.groupby(["family", "dataset", "learner"]):
        r = {x.arm: x for x in g.itertuples()}
        path = r["E2k500"].path
        if path not in gts:
            gts[path] = scored_gt(f, load_stream(path, ALL[f][1])[2])
        age = r["E2k500"].sig.set_index("t")["ref_age"]
        sel = d3[(d3["family"] == f) & (d3["dataset"] == ds) & (d3["learner"] == lr)]
        warn = {a: sel[sel["arm"] == a]["warn_t"].iloc[0] for a in arms}
        for s, e in gts[path]:
            rows.append({"age": int(age.get(s, -1)), **{a: any(s <= w <= e + 3000 for w in warn[a]) for a in arms}})
    m = pd.DataFrame(rows)
    stale = m[~m["E2k500"] & (m["age"] >= 10000)]
    print("GT drifts missed by E2-k500 with its reference >= 10k steps old: %d; hit by base %d, E1 %d, E10a %d, E10b %d"
          % (len(stale), stale["base"].sum(), stale["E1"].sum(), stale["E10a"].sum(), stale["E10b"].sum()))
    e10a, e10b = runs[runs["arm"] == "E10a"], runs[runs["arm"] == "E10b"]
    print("E10a reference refreshes: %d" % sum(int(x.sig["ref_refresh"].sum()) for x in e10a.itertuples()
                                               if "ref_refresh" in x.sig.columns))
    n_guard = sum(int(x.sig.set_index("t")["guard_drift"].reindex(x.conf_t).fillna(0).sum()) for x in e10b.itertuples())
    print("E10b confirmations %d, of which the leader guard fired the drift: %d" % (
        sum(len(x.conf_t) for x in e10b.itertuples()), n_guard))
    ages = runs[runs["arm"].isin(["E2k500", "E10a", "E10b"])].copy()
    ages["max_age"] = [int(x["ref_age"].max()) for x in ages["sig"]]
    print("max reference age:\n%s" % ages.groupby(["group", "arm"])["max_age"].max().unstack().to_string())

    ins = runs_table(held="a1")
    ins = ins[ins["family"] == "INS-abrupt"]
    print("\n## Development check, INSECTS abrupt (not judged): accuracy, TP@1000, FP@1000, confirmations")
    for a in arms:
        x = ins[ins["arm"] == a]
        if len(x):
            print("%-7s %.4f %3d %3d %3d" % (a, x["quality"].mean(), x["tp"].sum(), x["fp"].sum(),
                                            len(sum(x["conf_t"], []))))


def analyze_e11() -> None:
    """E11 verdict (docs/ECPF_E11_逾時與超額命中_預註冊.md): 1000-step warning timeout; recall as excess hits."""
    groups, arms = ["SYN2g23-B", "SYN2g23-MC", "SYN2g23-REG", "INJgas68"], ["base", "baseT", "E1T", "E2k500T"]
    missing = [(f, a) for f in E11 for a in arms if not os.path.exists(os.path.join(OUT, f, a, "detections.csv"))]
    if missing:   # paused or still running: never judge a partial matrix
        print("E11 INCOMPLETE: %d of %d cells missing -- no verdict" % (len(missing), len(E11) * len(arms)))
        return
    ages = {}
    for a in arms:
        ages[a] = []
        for f in E11:
            try:
                ages[a] += pd.read_csv(os.path.join(OUT, f, a, "detections.csv"))["confirm_age"].tolist()
            except pd.errors.EmptyDataError:
                pass
    a0 = all(max(ages[a], default=0) <= 1001 for a in ("baseT", "E1T", "E2k500T"))
    print("## A0 validity: longest warning->confirmation age %s -> %s\n" % (
        {a: int(max(v, default=0)) for a, v in ages.items()}, "VALID" if a0 else "INVALID"))
    if not a0:
        print("E11 INVALID -- no verdict")
        return
    res = new_data_criteria("E11", "e11", groups, arms, ["E1T", "E2k500T"], ref="baseT", excess=True)
    if res is None:
        return
    ok, df, runs = res
    B, MC, REG, gas = groups
    d3 = df[df["ext"] == 3000]
    q = runs.groupby(["group", "arm"])["quality"].mean()
    qa = {g: q[(g, "baseT")] <= 1.01 * q[(g, "base")] if g == REG else q[(g, "baseT")] >= q[(g, "base")] - 0.005
          for g in groups}
    xs = {a: float(d3[d3["arm"] == a]["xs"].sum()) for a in ("base", "baseT")}
    a1 = all(qa.values()) and xs["baseT"] >= 0.9 * xs["base"]
    print("\n## A: the timeout itself (base vs baseT, paired)")
    for g in groups:
        print("%-11s quality base %.4f -> baseT %.4f: %s" % (g, q[(g, "base")], q[(g, "baseT")], qa[g]))
    print("pooled excess hits base %.1f -> baseT %.1f (need >= %.1f) | FP@3000 %d -> %d" % (
        xs["base"], xs["baseT"], 0.9 * xs["base"], d3[d3["arm"] == "base"]["fp"].sum(),
        d3[d3["arm"] == "baseT"]["fp"].sum()))
    print("A1 %s -> %s" % (a1, "the 1000-step timeout becomes the standard setting" if a1 else
                           "timeout NOT adopted; part B is for reference only"))
    print("\n## B verdicts (vs baseT, recall = excess hits)")
    for a in ok:
        cls = all(ok[a][k] for k in ("P1", "P2", "P3-" + B, "P3-" + MC, "P4-" + B, "P4-" + MC, "P4-" + gas))
        reg = ok[a]["P3-" + REG] and ok[a]["P4-" + REG]
        print("E11 verdict %s: classification %s; regression %s%s" % (
            a, "HOLDS" if cls else "does NOT hold", "HOLDS" if reg else "does NOT hold",
            "" if a1 else " (reference only: A1 failed)"))
    print("\n## warning->confirmation ages")
    for a in arms:
        v = np.array(ages[a])
        if len(v):
            print("%-8s confirmations %4d  p50 %4.0f  p95 %5.0f  max %5.0f" % (
                a, len(v), np.percentile(v, 50), np.percentile(v, 95), v.max()))


def excess_report() -> None:
    """Descriptive and post hoc: excess hits for the earlier new-data rounds (their verdicts stand unchanged)."""
    for held, fams in (("a1", A1), ("a2", A2), ("e10", E10)):
        df = rescore(exts=(3000,), show=False, held=held)
        df = df[df["family"].isin(list(fams))].copy()
        df["chance"] = chance_hits(df)
        df["group"] = df["family"].map(lambda f: f.rsplit("-", 1)[0])
        t = df.groupby(["group", "arm"], sort=False)[["tp", "fp", "chance"]].sum()
        t["excess"] = t["tp"] - t["chance"]
        print("## %s: TP@3000, FP@3000, expected chance hits, excess hits\n%s\n" % (held.upper(), t.round(1).to_string()))


def g00_check(label: str, arms):
    """Shared by the D1 / D2 development checks on A2's g00 SYN2-B / SYN2-REG streams: prints the per-group
    table and returns (groups, df, xs, m); m = one row per GT drift with the hit of every arm and the reference
    ages of A2's E2k500 (age) and of E2k500T (age_t) at the drift onset."""
    groups = ["SYN2-B", "SYN2-REG"]
    fams = [f for f in A2 if f.rsplit("-", 1)[0] in groups]
    df = rescore(exts=(3000,), show=False, held="a2")
    df = df[df["family"].isin(fams) & df["arm"].isin(arms)].copy()
    df["xs"] = df["tp"] - np.array(chance_hits(df))
    df["group"] = df["family"].map(lambda f: f.rsplit("-", 1)[0])
    runs = runs_table(held="a2")
    runs = runs[runs["family"].isin(fams) & runs["arm"].isin(arms)].copy()
    runs["group"] = runs["family"].map(lambda f: f.rsplit("-", 1)[0])
    q = runs.groupby(["group", "arm"])["quality"].mean()
    xs = df.groupby(["group", "arm"])["xs"].sum()
    print("## %s per group (TP@3000, FP@3000, excess hits, quality = accuracy or MAE, max reference age)" % label)
    for g in groups:
        for a in arms:
            x, r = df[(df["group"] == g) & (df["arm"] == a)], runs[(runs["group"] == g) & (runs["arm"] == a)]
            age = max((int(s["ref_age"].max()) for s in r["sig"] if "ref_age" in s.columns), default=0)
            print("%-8s %-8s TP %3d  FP %3d  excess %5.1f  quality %.4f  max ref age %6s" % (
                g, a, x["tp"].sum(), x["fp"].sum(), xs[(g, a)], q[(g, a)], age or "-"))

    rows = []
    for (f, ds, lr), g in runs.groupby(["family", "dataset", "learner"]):
        r = {x.arm: x for x in g.itertuples()}
        iv = scored_gt(f, load_stream(r["E2k500"].path, ALL[f][1])[2])
        age, age_t = (r[a].sig.set_index("t")["ref_age"] for a in ("E2k500", "E2k500T"))
        sel = df[(df["family"] == f) & (df["dataset"] == ds) & (df["learner"] == lr)]
        warn = {a: sel[sel["arm"] == a]["warn_t"].iloc[0] for a in arms}
        for s, e in iv:
            rows.append({"group": f.rsplit("-", 1)[0], "age": int(age.get(s, -1)), "age_t": int(age_t.get(s, -1)),
                         **{a: any(s <= w <= e + 3000 for w in warn[a]) for a in arms}})
    return groups, df, xs, pd.DataFrame(rows)


def analyze_d1() -> None:
    """D1 development check (docs/ECPF_D1_逾時與參照過時_開發檢查.md): does the 1000-step timeout also remove
    A2's stale-reference cascades?  A2 g00 SYN2-B / SYN2-REG; base and E2k500 are A2's own runs."""
    arms = ["base", "E2k500", "baseT", "E2k500T"]
    groups, df, xs, m = g00_check("D1", arms)
    stale = m[~m["E2k500"] & (m["age"] >= 10000)]
    print("\nA2's stale misses (E2k500 missed, its reference >= 10k steps old): %d; hit by base %d, baseT %d, E2k500T %d"
          % (len(stale), stale["base"].sum(), stale["baseT"].sum(), stale["E2k500T"].sum()))
    m["bin_t"] = pd.cut(m["age_t"], [-1, 2000, 10000, 10 ** 6], labels=["<2k", "2k-10k", ">=10k"])
    print("\nhits per E2k500T reference age at drift onset:\n%s" % m.groupby("bin_t", observed=True)[arms].sum().assign(
        n=m.groupby("bin_t", observed=True).size()).to_string())
    c1 = all(xs[(g, "E2k500T")] >= xs[(g, "baseT")] for g in groups)
    c2 = len(stale) > 0 and stale["E2k500T"].sum() >= 0.5 * len(stale)
    print("\nD1 reading: (1) excess E2k500T >= baseT in both groups: %s | (2) stale misses recovered %d/%d >= 50%%: %s"
          " -> %s" % (c1, stale["E2k500T"].sum(), len(stale), c2,
                      "timeout RESOLVES the stale reference" if c1 and c2 else "PARTLY resolved" if c1 or c2
                      else "NOT resolved: the reference refresh rule is still open"))


def analyze_d2() -> None:
    """D2 development check (docs/ECPF_D2_參照更新加逾時_開發檢查.md): E10a / E10b plus the timeout on A2's g00."""
    arms = ["base", "E2k500", "baseT", "E2k500T", "E10aT", "E10bT"]
    groups, df, xs, m = g00_check("D2", arms)
    fp = df.groupby(["group", "arm"])["fp"].sum()
    stale = m[~m["E2k500"] & (m["age"] >= 10000)]
    print("\nA2's stale misses (E2k500 missed, its reference >= 10k steps old): %d; hit by %s" % (
        len(stale), ", ".join("%s %d" % (a, stale[a].sum()) for a in ("base", "baseT", "E2k500T", "E10aT", "E10bT"))))
    for c in ("E10aT", "E10bT"):
        c1 = all(xs[(g, c)] >= xs[(g, "baseT")] for g in groups)
        c2 = len(stale) > 0 and stale[c].sum() >= 0.5 * len(stale)
        c3 = all(fp[(g, c)] <= 0.5 * fp[(g, "baseT")] for g in groups)
        print("D2 reading %s: (1) excess >= baseT in both groups %s | (2) stale recovered %d/%d >= 50%% %s | "
              "(3) FP <= 50%% of baseT in both groups %s -> %s | beats E2k500T in both groups: %s" % (
                  c, c1, stale[c].sum(), len(stale), c2, c3,
                  "FIXED" if c1 and c2 and c3 else "PARTLY" if c3 and (c1 or c2) else "NO",
                  all(xs[(g, c)] > xs[(g, "E2k500T")] for g in groups)))


def analyze_e12() -> None:
    """E12 verdict (docs/ECPF_E12_leader守衛取代_預註冊.md): can E10bT replace E2k500T as the main method?"""
    groups, arms = ["SYN2g45-B", "SYN2g45-MC", "SYN2g45-REG", "INJgas9"], ["baseT", "E2k500T", "E10bT"]
    missing = [(f, a) for f in E12 for a in arms if not os.path.exists(os.path.join(OUT, f, a, "detections.csv"))]
    if missing:   # paused or still running: never judge a partial matrix
        print("E12 INCOMPLETE: %d of %d cells missing -- no verdict" % (len(missing), len(E12) * len(arms)))
        return
    ages = {a: [] for a in arms}
    for a in arms:
        for f in E12:
            try:
                ages[a] += pd.read_csv(os.path.join(OUT, f, a, "detections.csv"))["confirm_age"].tolist()
            except pd.errors.EmptyDataError:
                pass
    a0 = all(max(v, default=0) <= 1001 for v in ages.values())
    print("## A0 validity: longest warning->confirmation age %s -> %s\n" % (
        {a: int(max(v, default=0)) for a, v in ages.items()}, "VALID" if a0 else "INVALID"))
    if not a0:
        print("E12 INVALID -- no verdict")
        return
    res = new_data_criteria("E12", "e12", groups, arms, ["E2k500T", "E10bT"], ref="baseT", excess=True, per_method=2)
    if res is None:
        return
    ok, df, runs = res
    B, MC, REG, gas = groups
    d3 = df[df["ext"] == 3000]
    xs = lambda a, gs: float(d3[(d3["arm"] == a) & d3["group"].isin(gs)]["xs"].sum())
    print("\n## B verdicts (vs baseT, recall = excess hits; P1 None = not evaluable, then left out)")
    holds = {}
    for a in ok:
        cls = all((ok[a][k] is not False) if k == "P1" else ok[a][k]
                  for k in ("P1", "P2", "P3-" + B, "P3-" + MC, "P4-" + B, "P4-" + MC, "P4-" + gas))
        reg = ok[a]["P3-" + REG] and ok[a]["P4-" + REG]
        holds[a] = (cls, reg)
        print("E12 verdict %s: classification %s; regression %s" % (
            a, "HOLDS" if cls else "does NOT hold", "HOLDS" if reg else "does NOT hold"))
    print("\n## C: replacement (E10bT replaces E2k500T where it holds and has at least E2k500T's excess hits)")
    for task, gs, i in (("classification", [B, MC, gas], 0), ("regression", [REG], 1)):
        x_b, x_e = xs("E10bT", gs), xs("E2k500T", gs)
        print("%s: E10bT holds %s | excess E10bT %.1f vs E2k500T %.1f -> %s" % (
            task, holds["E10bT"][i], x_b, x_e,
            "E10bT REPLACES E2k500T" if holds["E10bT"][i] and x_b >= x_e else "keep E2k500T"))

    e10b = runs[runs["arm"] == "E10bT"]
    n_guard = sum(int(x.sig.set_index("t")["guard_drift"].reindex(x.conf_t).fillna(0).sum()) for x in e10b.itertuples())
    print("\nE10bT confirmations %d, of which the leader guard fired the drift: %d" % (
        sum(len(x.conf_t) for x in e10b.itertuples()), n_guard))
    ra = runs[runs["arm"].isin(["E2k500T", "E10bT"])].copy()
    ra["max_age"] = [int(s["ref_age"].max()) for s in ra["sig"]]
    print("max reference age:\n%s" % ra.groupby(["group", "arm"])["max_age"].max().unstack().to_string())
    rows = []
    for (f, ds, lr), g in runs.groupby(["family", "dataset", "learner"]):
        r = {x.arm: x for x in g.itertuples()}
        iv = scored_gt(f, load_stream(r["E2k500T"].path, ALL[f][1])[2])
        age = r["E2k500T"].sig.set_index("t")["ref_age"]
        sel = d3[(d3["family"] == f) & (d3["dataset"] == ds) & (d3["learner"] == lr)]
        warn = {a: sel[sel["arm"] == a]["warn_t"].iloc[0] for a in arms}
        for s, e in iv:
            rows.append({"age": int(age.get(s, -1)), **{a: any(s <= w <= e + 3000 for w in warn[a]) for a in arms}})
    m = pd.DataFrame(rows)
    m["bin"] = pd.cut(m["age"], [-1, 10000, 10 ** 6], labels=["<10k", ">=10k"])
    print("\nhits per E2k500T reference age at drift onset:\n%s" % m.groupby("bin", observed=True)[arms].sum().assign(
        n=m.groupby("bin", observed=True).size()).to_string())


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
    ap.add_argument("--family", choices=list(ALL))
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--check", action="store_true", help="run the self-checks only (incl. the E10 pipeline gates)")
    ap.add_argument("--premise", action="store_true", help="E6 premise replay on the E2-k500 traces")
    ap.add_argument("--analyze-stack", action="store_true", help="E6 vs E2-k500 verdict")
    ap.add_argument("--rescore", action="store_true", help="relabel all runs with 1000/3000-step windows")
    ap.add_argument("--analyze-delta", action="store_true", help="E7 vs E2-k500 verdict")
    ap.add_argument("--analyze-e8", action="store_true", help="E8 held-out verdict (task-specific delta)")
    ap.add_argument("--analyze-e9", action="store_true", help="E9 verdict (official-ECPF detectors)")
    ap.add_argument("--analyze-a1", action="store_true", help="A1 verdict (new data: injected electricity, INSECTS)")
    ap.add_argument("--analyze-a2", action="store_true", help="A2 verdict (new data: synthetic v2, injected gas)")
    ap.add_argument("--analyze-e10", action="store_true", help="E10 verdict (reference refresh arms, fresh data)")
    ap.add_argument("--analyze-e11", action="store_true", help="E11 verdict (warning timeout, excess-hit recall)")
    ap.add_argument("--excess-report", action="store_true", help="post-hoc excess hits for A1 / A2 / E10")
    ap.add_argument("--analyze-d1", action="store_true", help="D1 dev check: timeout vs stale references on A2 g00")
    ap.add_argument("--analyze-d2", action="store_true", help="D2 dev check: E10a / E10b plus the timeout on A2 g00")
    ap.add_argument("--analyze-e12", action="store_true", help="E12 verdict (can E10bT replace E2k500T?)")
    a = ap.parse_args()
    self_check()
    if a.check:
        check_e10()
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
    if a.analyze_e8:
        analyze_e8()
    if a.analyze_e9:
        analyze_e9()
    if a.analyze_a1:
        analyze_a1()
    if a.analyze_a2:
        analyze_a2()
    if a.analyze_e10:
        analyze_e10()
    if a.analyze_e11:
        analyze_e11()
    if a.excess_report:
        excess_report()
    if a.analyze_d1:
        analyze_d1()
    if a.analyze_d2:
        analyze_d2()
    if a.analyze_e12:
        analyze_e12()
