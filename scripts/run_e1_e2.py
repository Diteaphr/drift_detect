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
                  "ecpf_detector_warning_timeout": 1000},
        # E13 (docs/ECPF_E13_守衛凍結尺度_預註冊.md): E10bT with the guard's scale frozen per era (regression only)
        "E10bFT": {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500, "ecpf_leader_guard": True,
                   "ecpf_detector_warning_timeout": 1000, "ecpf_guard_frozen_scale": 500}}
# D5 (docs/ECPF_D5_預測範圍守衛_開發檢查.md): the same arms with the regression learners' prediction-range guard
ARMS.update({a + "C": ARMS[a] for a in ("baseT", "E2k500T", "E10bFT")})
D5_ARMS = ["baseTC", "E2k500TC", "E10bFTC"]
ARM_MODEL_KW = {a: {"clip_predictions": True} for a in D5_ARMS}   # model kwargs an arm adds (regression only)
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
_KINDS = (("sud", "sudden"), ("grad", "gradual"), ("inc", "incremental"), ("rec", "recurring"))
_METHODS = (("cp", "class_prior"), ("ls", "label_swap"), ("fp", "feature_permutation"), ("ff", "feature_filtering"))
_INJ13 = "data/dataset_0921/injected_real_dataset/{t}/{a}/{m}/{s}_{m}_{a}_g0[{g}].csv"
E13 = {  # E13 judges on fresh data: regression g06-g09, classification g06-g07, injected electricity g03-g05 and
         # covertype g00-g01; injected families are split by abruptness only to run cells in parallel
    **{"SYN2g69-REG-%s%s" % (k, sd): (sorted(glob.glob(_SYN.replace("g00", "g0" + sd).format(t="regression", d=d))),
                                     0, REG_LEARNERS, True)
       for sd in "6789" for k, d in _KINDS},
    **{"SYN2g67-%s-%s%s" % (g, k, sd): (sorted(glob.glob(_SYN.replace("g00", "g0" + sd).format(t=t, d=d))), 0, cfg,
                                        False)
       for sd in "67"
       for g, t, cfg in (("B", "binary", RERUN["B"][2]), ("MC", "multi_classification", [RERUN["MC-syn"][2][0]]))
       for k, d in _KINDS},
    **{"INJelec35-%s%s" % (k, a[0].upper()): (sorted(glob.glob(_INJ13.format(t="binary", a=a, m=m, s="electricity",
                                                                              g="3-5"))), 0, RERUN["B"][2], False)
       for k, m in _METHODS for a in ("abrupt", "gradual")},
    **{"INJcov01-%s%s" % (k, a[0].upper()): (sorted(glob.glob(_INJ13.format(t="multi_classification", a=a, m=m,
                                                                             s="covertype", g="0-1"))), 0,
                                            [RERUN["MC-syn"][2][0]], False)
       for k, m in _METHODS for a in ("abrupt", "gradual")},
}
E13_REG_ARMS, E13_CLS_ARMS = ["baseT", "E1T", "E2k500T", "E10bT", "E10bFT"], ["baseT", "E1T", "E10bT"]
E14 = {  # E14 classification confirmation: the last unused synthetic (g08-g09) and electricity (g06-g09) data
    **{"SYN2g89-%s-%s%s" % (g, k, sd): (sorted(glob.glob(_SYN.replace("g00", "g0" + sd).format(t=t, d=d))), 0, cfg,
                                        False)
       for sd in "89"
       for g, t, cfg in (("B", "binary", RERUN["B"][2]), ("MC", "multi_classification", [RERUN["MC-syn"][2][0]]))
       for k, d in _KINDS},
    **{"INJelec69-%s%s" % (k, a[0].upper()): (sorted(glob.glob(_INJ13.format(t="binary", a=a, m=m, s="electricity",
                                                                              g="6-9"))), 0, RERUN["B"][2], False)
       for k, m in _METHODS for a in ("abrupt", "gradual")},
}
E14_ARMS = ["baseT", "E10bFT"]
_REALREG = "data/dataset_0921/real_dataset/regression/{d}/{d}.csv"
A3 = {"REALreg-" + k: ([_REALREG.format(d=d)], 0, REG_LEARNERS, True)   # A3: real regression streams, no GT
      for k, d in (("bike", "bike_sharing"), ("metro", "metro_interstate_traffic"))}
A3_ARMS = ["baseT", "E2k500T", "E10bFT"]
ALL = {**CELLS, **HELD, **A1, **A2, **E10, **E11, **E12, **E13, **E14, **A3}


def e13_arms(fam: str):
    """E13 matrix: five arms on regression, three on classification (E10bFT == E10bT there, gate G3)."""
    return E13_REG_ARMS if ALL[fam][3] else E13_CLS_ARMS


def scored_gt(fam: str, intervals):
    """A2 rule (prereg): GT intervals that start inside the warm-up are not scored."""
    return [iv for iv in intervals if iv[0] >= WARM_START] if fam in A2 or fam in E10 or fam in E11 or fam in E12 or fam in E13 or fam in E14 else intervals
FP = ("echo", "orphan")
MATCH = 500
SIG_COLS = ["t", "err", "raw", "is_warning", "is_drift", "ref_err", "ref_age", "ref_switch", "switch_warning_age",
            "ref_refresh", "guard_drift", "guard_in"]


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
    # C1 break-even: E11-B raw TP (E2k500T 73 hits / 14 FP vs baseT 79 / 67) -> baseT cheaper once w > 53/6
    assert breakeven(73, 14, 79, 67) == ("other", 53 / 6) and breakeven(10, 5, 8, 20) == ("main", 0.0)


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
            sig, dets, swaps, stage3, intervals, _, n = run(path, mt, max_steps,
                                                            {**mk, **(ARM_MODEL_KW.get(arm, {}) if is_reg else {})}, pk)
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
    for fam, (_, _, configs, _) in (A3 if held == "a3" else E14 if held == "e14" else E13 if held == "e13" else E12 if held == "e12" else E11 if held == "e11" else E10 if held == "e10" else A2 if held == "a2" else A1 if held == "a1" else HELD if held else CELLS).items():
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
                         "n_gt": len(gt[key]),
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


def analyze_d3() -> None:
    """D3 development check (docs/ECPF_D3_主方法與參照過時_開發檢查.md): the main method E10bFT on A2's g00
    streams, where the stale reference bit (D1 / D2). Descriptive only."""
    arms, c = ["base", "E2k500", "baseT", "E2k500T", "E10bT", "E10bFT"], "E10bFT"
    groups, df, xs, m = g00_check("D3", arms)
    seq = {(r.family, r.dataset, r.learner, r.arm): (r.warn_t, r.conf_t)
           for r in df[df["group"] == "SYN2-B"].itertuples()}
    mine = [k for k in seq if k[3] == c]
    diff = [k[:3] for k in mine if seq[k] != seq[k[:3] + ("E10bT",)]]
    print("\n## V: SYN2-B runs where E10bFT's detections differ from E10bT's: %d of %d -> %s" % (
        len(diff), len(mine), "VALID" if mine and not diff else "INVALID"))
    if diff or not mine:
        print("D3 INVALID -- nothing is read")
        return
    fp = df.groupby(["group", "arm"])["fp"].sum()
    stale = m[~m["E2k500"] & (m["age"] >= 10000)]
    shown = ("base", "baseT", "E2k500T", "E10bT", c)
    print("\nA2's stale misses (E2k500 missed, its reference >= 10k steps old): %d; hit by %s" % (
        len(stale), ", ".join("%s %d" % (a, stale[a].sum()) for a in shown)))
    for g in groups:
        sg = stale[stale["group"] == g]
        print("  %-8s %2d; hit by %s" % (g, len(sg), ", ".join("%s %d" % (a, sg[a].sum()) for a in shown)))
    c1 = all(xs[(g, c)] >= xs[(g, "baseT")] for g in groups)
    c2 = len(stale) > 0 and stale[c].sum() >= 0.5 * len(stale)
    c3 = all(fp[(g, c)] <= 0.5 * fp[(g, "baseT")] for g in groups)
    print("\nD3 reading %s: (1) excess >= baseT in both groups %s | (2) stale recovered %d/%d >= 50%% %s | "
          "(3) FP <= 50%% of baseT in both groups %s -> %s | beats E2k500T in both groups: %s" % (
              c, c1, stale[c].sum(), len(stale), c2, c3,
              "FIXED" if c1 and c2 and c3 else "PARTLY" if c3 and (c1 or c2) else "NO",
              all(xs[(g, c)] > xs[(g, "E2k500T")] for g in groups)))
    sr = stale[stale["group"] == "SYN2-REG"]
    kx = xs[("SYN2-REG", c)] >= xs[("SYN2-REG", "E10bT")] - 1.0
    ks = sr[c].sum() >= sr["E10bT"].sum() - 1
    print("vs E10bT on SYN2-REG: excess %.1f vs %.1f (need >=%.1f: %s) | stale recovered %d vs %d (need >=%d: %s) -> %s" % (
        xs[("SYN2-REG", c)], xs[("SYN2-REG", "E10bT")], xs[("SYN2-REG", "E10bT")] - 1.0, kx, sr[c].sum(),
        sr["E10bT"].sum(), sr["E10bT"].sum() - 1, ks,
        "NOT WORSE than E10bT" if kx and ks else "the frozen scale WEAKENS the guard on stale-reference streams"))

    ev = {a: e13_guard_events(a, held="a2") for a in ("E10bT", c)}
    bad = sum(b for _, b in ev.values())
    print("\n## Guard-triggered confirmations on SYN2-REG (replay mismatches: %d -> %s)" % (
        bad, "VALID" if not bad else "INVALID: not read"))
    if not bad:
        for name, (d, _) in ev.items():
            gh = d[(d["label"] == "hit") & d["guard"]]
            print("%-6s confirmations %d | FP %d (guard %d) | hits %d (guard %d, rr>=1.1 %d, median guard-hit delay %.0f)" % (
                name, len(d), d["fp"].sum(), (d["fp"] & d["guard"]).sum(), (d["label"] == "hit").sum(), len(gh),
                int((gh["rr"] >= 1.1).sum()), gh["delay"].astype(float).median()))
    m["bin_t"] = pd.cut(m["age_t"], [-1, 10000, 10 ** 6], labels=["<10k", ">=10k"])
    for g in groups:
        mg = m[m["group"] == g]
        print("\n%s hits per E2k500T reference age at drift onset:\n%s" % (g, mg.groupby("bin_t", observed=True)[
            list(shown)].sum().assign(n=mg.groupby("bin_t", observed=True).size()).to_string()))


def miss_cost_rows(held: str, prefix: str, ref_arm=None):
    """D4: one row per (regression stream, learner, scored GT drift) -- whether E10bFT (F) and baseT (B) hit it, and
    both arms' summed |residual| over the post-drift window (3000 and 1000 steps, cut at the next GT start) and the
    pre-drift window (2000 steps, not before the previous GT start). ref_arm: also flag D1's stale misses."""
    arms = ["baseT", "E10bFT"] + ([ref_arm] if ref_arm else [])
    df = rescore(exts=(3000,), show=False, held=held)
    runs = runs_table(held=held)
    runs = runs[runs["family"].str.startswith(prefix) & runs["arm"].isin(arms)]
    rows = []
    for (f, ds, lr), g in runs.groupby(["family", "dataset", "learner"]):
        r = {x.arm: x for x in g.itertuples()}
        iv = sorted(scored_gt(f, load_stream(r["baseT"].path, ALL[f][1])[2]))
        sel = df[(df["family"] == f) & (df["dataset"] == ds) & (df["learner"] == lr)]
        warn = {a: sel[sel["arm"] == a]["warn_t"].iloc[0] for a in arms}
        raw = {k: r[a].sig.set_index("t")["raw"] for k, a in (("F", "E10bFT"), ("B", "baseT"))}
        age = r[ref_arm].sig.set_index("t")["ref_age"] if ref_arm else None
        starts = [s for s, _ in iv]
        for i, (s, e) in enumerate(iv):
            nxt, prv = (starts[i + 1] if i + 1 < len(starts) else 10 ** 9), (starts[i - 1] if i else 0)
            hit = {a: any(s <= w <= e + 3000 for w in warn[a]) for a in arms}
            row = {"kind": f.rsplit("-", 1)[1].rstrip("0123456789"), "learner": lr, "gt": s,
                   "cat": "ABCD"[2 * (not hit["baseT"]) + (not hit["E10bFT"])],
                   "stale": bool(ref_arm) and not hit[ref_arm] and int(age.get(s, -1)) >= 10000, "missF": not hit["E10bFT"]}
            for name, lo, hi in (("post", s, min(s + 3000, nxt)), ("post1k", s, min(s + 1000, nxt)),
                                 ("pre", max(s - 2000, prv), s)):
                for k in ("F", "B"):
                    row["%s_%s" % (name, k)] = float(raw[k].loc[lo:hi - 1].sum())
            rows.append(row)
    return pd.DataFrame(rows)


def analyze_d4() -> None:
    """D4 development check (docs/ECPF_D4_漏抓代價_開發檢查.md): does a regression drift that E10bFT misses and
    baseT hits (category B) cost prediction quality? Stored traces only."""
    ratio = lambda d, w: d[w + "_F"].sum() / d[w + "_B"].sum() if len(d) else float("nan")
    names = {"A": "both hit", "B": "E10bFT miss, baseT hit", "C": "E10bFT hit, baseT miss", "D": "both miss"}
    reads = []
    for label, held, prefix, ref in (("A2 g00 SYN2-REG (primary)", "a2", "SYN2-REG", "E2k500"),
                                     ("E13 SYN2g69-REG (replication)", "e13", "SYN2g69-REG", None)):
        m = miss_cost_rows(held, prefix, ref)
        print("## %s: %d scored drifts; ratio = E10bFT / baseT summed |residual| (>1: E10bFT worse)" % (label, len(m)))
        print("%-3s %-24s %4s %10s %10s %10s" % ("cat", "", "n", "post 3000", "post 1000", "pre 2000"))
        for c in "ABCD":
            d = m[m["cat"] == c]
            print("%-3s %-24s %4d %10.3f %10.3f %10.3f" % (c, names[c], len(d), ratio(d, "post"), ratio(d, "post1k"),
                                                         ratio(d, "pre")))
        print("%-3s %-24s %4d %10.3f %10.3f %10.3f" % ("all", "", len(m), ratio(m, "post"), ratio(m, "post1k"),
                                                      ratio(m, "pre")))
        b, a = m[m["cat"] == "B"], m[m["cat"] == "A"]
        r1 = ratio(b, "post")
        r2 = r1 / ratio(a, "post")
        read = ("not readable (B < 5)" if len(b) < 5 else "NO COST" if r1 <= 1.02 else "COST" if r1 > 1.05 else "SMALL cost")
        reads.append((read, r2))
        print("R1 category B post-window ratio %.3f (n=%d) -> %s" % (r1, len(b), read))
        print("R2 B / A = %.3f / %.3f = %.3f -> %s" % (
            r1, ratio(a, "post"), r2, "attributable cost (> 1.05)" if r2 > 1.05 else "no attributable cost"))
        print("B by drift type: %s" % ", ".join("%s n=%d %.3f" % (k, len(d), ratio(d, "post"))
                                                for k, d in b.groupby("kind")))
        if ref:
            st = m[m["stale"] & m["missF"]]
            print("D1's stale misses that E10bFT misses: n=%d, post-window ratio %.3f (of which baseT hit: n=%d, %.3f)" % (
                len(st), ratio(st, "post"), (st["cat"] == "B").sum(), ratio(st[st["cat"] == "B"], "post")))
        print()
    no_cost = all(r == "NO COST" and r2 <= 1.05 for r, r2 in reads)
    print("D4 conclusion: %s" % (
        "both data sets read NO COST with R2 <= 1.05 -> the regression stale reference is a limit of the recall "
        "METRIC, not an open problem of the method" if no_cost else
        "primary data reads COST -> a METHOD problem: regression needs a new trigger" if reads[0][0] == "COST" else
        "mixed -> reported as is"))


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


C1_W = (1, 2, 5, 10)   # C1 cost ratios: a miss costs w false alarms


def breakeven(r_m: float, fp_m: float, r_o: float, fp_o: float):
    """C1: cost(w) = w * (N - recall) + FP for the main arm m and another arm o (N cancels).
    Returns (who, w*): 'main' or 'other' is the cheaper arm for every w > w*; w* = 0: never costlier at any w."""
    dr, dfp = r_m - r_o, fp_o - fp_m   # cost_o - cost_m = w * dr + dfp
    if dr >= 0 and dfp >= 0:
        return "main", 0.0
    if dr <= 0 and dfp <= 0:
        return "other", 0.0
    return ("main", -dfp / dr) if dr > 0 else ("other", dfp / -dr)


def analyze_c1() -> None:
    """C1 readings (docs/ECPF_C1_漏抓加權成本_預註冊.md): cost(w) = w * missed + FP on E11 / E12's stored runs,
    missed = scored GT drifts - excess hits at 3000 steps (raw basis, for contrast only: - TP@3000)."""
    cost = lambda r, col, w: w * (r["n_gt"] - r[col]) + r["fp"]

    def fmt(m, o, who, w):
        return "%s %s" % (m if who == "main" else o, "never costlier" if w == 0 else "cheaper once w > %.2f" % w)
    kinds, r1, r2, r3, r3_raw, r4 = ("sud", "grad", "inc", "rec"), [], [], [], 0, []
    for rnd, held, groups, arms, main_of in (
            ("E11", "e11", ["SYN2g23-B", "SYN2g23-MC", "SYN2g23-REG", "INJgas68"], ["base", "baseT", "E1T", "E2k500T"],
             lambda g: "E2k500T"),
            ("E12", "e12", ["SYN2g45-B", "SYN2g45-MC", "SYN2g45-REG", "INJgas9"], ["baseT", "E2k500T", "E10bT"],
             lambda g: "E2k500T" if g.endswith("REG") else "E10bT")):
        df = rescore(show=False, held=held)
        if df is None:
            print("RESCORE INVALID -- no reading")
            return
        df = df[df["ext"] == 3000].copy()
        df["xs"] = df["tp"] - np.array(chance_hits(df))
        df["group"] = df["family"].map(lambda f: f.rsplit("-", 1)[0])
        df["kind"] = df["family"].map(lambda f: f.rsplit("-", 1)[1].rstrip("0123456789"))
        t = df.groupby(["group", "arm"])[["n_gt", "tp", "fp", "xs"]].sum()
        assert (t.groupby("group")["n_gt"].nunique() == 1).all(), "N differs across arms: a cell is missing"
        print("## %s pooled per group (3000-step windows; missed = N - excess; cost = w * missed + FP)" % rnd)
        print("%-12s %-8s %4s %4s %4s %7s %7s" % ("group", "arm", "N", "TP", "FP", "excess", "missed")
              + "".join(" %8s" % ("cost@%d" % w) for w in C1_W))
        for g in groups:
            for a in arms:
                r = t.loc[(g, a)]
                print("%-12s %-8s %4d %4d %4d %7.1f %7.1f" % (g, a, r["n_gt"], r["tp"], r["fp"], r["xs"],
                                                             r["n_gt"] - r["xs"])
                      + "".join(" %8.1f" % cost(r, "xs", w) for w in C1_W))
        for basis, col in (("excess", "xs"), ("raw", "tp")):
            print("\nlowest-cost arm, %s basis (w = %s):" % (basis, ", ".join(map(str, C1_W))))
            for g in groups:
                c = {a: [cost(t.loc[(g, a)], col, w) for w in C1_W] for a in arms}
                print("%-12s %s" % (g, " | ".join("=".join(a for a in arms if c[a][i] <= min(v[i] for v in c.values())
                                                             + 1e-9) for i in range(len(C1_W)))))
        print("\nbreak-even, main arm vs each other arm:")
        for g in groups:
            m, rm = main_of(g), t.loc[(g, main_of(g))]
            for a in arms:
                if a != m:
                    ro = t.loc[(g, a)]
                    print("%-12s %s vs %-8s excess: %-32s raw: %s" % (
                        g, m, a, fmt(m, a, *breakeven(rm["xs"], rm["fp"], ro["xs"], ro["fp"])),
                        fmt(m, a, *breakeven(rm["tp"], rm["fp"], ro["tp"], ro["fp"]))))
            for b in ("base", "baseT"):
                if b in arms:
                    rb = t.loc[(g, b)]
                    r1.append(all(cost(rm, "xs", w) <= cost(rb, "xs", w) + 1e-9 for w in C1_W))
                    r2 += ["%s %s w=%d" % (g, b, w) for w in C1_W if cost(rb, "tp", w) < cost(rm, "tp", w)]

        k = df[df["group"].str.startswith("SYN2")].groupby(["group", "kind", "arm"])[["n_gt", "tp", "fp", "xs"]].sum()
        print("\n## %s per drift type (synthetic, two seeds pooled): main arm vs baseT" % rnd)
        for g in groups[:3]:
            m = main_of(g)
            for kd in kinds:
                rm, rb = k.loc[(g, kd, m)], k.loc[(g, kd, "baseT")]
                flip = cost(rb, "xs", 10) < cost(rm, "xs", 10)
                if flip:
                    r3.append("%s-%s" % (g, kd))
                r3_raw += int(cost(rb, "tp", 10) < cost(rm, "tp", 10))
                print("%-12s %-4s N %3d | %s excess %5.1f FP %3d | baseT excess %5.1f FP %3d | cost@10 %6.1f vs %6.1f"
                      " | %s%s" % (g, kd, rm["n_gt"], m, rm["xs"], rm["fp"], rb["xs"], rb["fp"], cost(rm, "xs", 10),
                                   cost(rb, "xs", 10), fmt(m, "baseT", *breakeven(rm["xs"], rm["fp"], rb["xs"], rb["fp"])),
                                   "  <- baseT cheaper at w=10" if flip else ""))
        if rnd == "E12":
            g = "SYN2g45-REG"
            print("\n## E12 regression: E10bT vs E2k500T (excess basis)")
            for name, re_, r2_ in [("pooled", t.loc[(g, "E10bT")], t.loc[(g, "E2k500T")])] + [
                    (kd, k.loc[(g, kd, "E10bT")], k.loc[(g, kd, "E2k500T")]) for kd in kinds]:
                ok = all(cost(re_, "xs", w) < cost(r2_, "xs", w) for w in C1_W)
                r4.append(ok)
                print("%-6s E10bT excess %5.1f FP %3d | E2k500T excess %5.1f FP %3d | %s | E10bT cheaper at every "
                      "registered w: %s" % (name, re_["xs"], re_["fp"], r2_["xs"], r2_["fp"],
                                             fmt("E10bT", "E2k500T", *breakeven(re_["xs"], re_["fp"], r2_["xs"],
                                                                                r2_["fp"])), ok))
        print()

    print("## Readings (registered; C1 changes no E11 / E12 verdict)")
    print("R1 pooled: main arm's cost <= baseT (E11: also base) at every w in all 8 groups: %s -> %s" % (
        all(r1), "miss weighting does not bring base back" if all(r1) else "base is cheaper somewhere: see tables"))
    print("R2 raw basis (contrast only), baseT cheaper than the main arm: %s" % (", ".join(r2) or "nowhere"))
    print("R3 drift-type cells where baseT is cheaper than the main arm at w=10: %d of %d %s -> %s (raw basis: %d)" % (
        len(r3), 2 * 3 * len(kinds), r3, "the main arm holds per drift type; exceptions are few" if len(r3) <= 4
        else "with heavy miss costs, choose by drift type", r3_raw))
    n4 = sum(r4[1:])
    print("R4 regression E10bT vs E2k500T: pooled cheaper at every w %s; drift types cheaper at every w %d of 4 -> %s" % (
        r4[0], n4, "cost view supports E10bT for regression (candidate for a registered round on fresh seeds)"
        if r4[0] and n4 >= 3 else "cost view keeps E2k500T"))


# ---------------------------------------------------------------------------
# E13 (docs/ECPF_E13_守衛凍結尺度_預註冊.md): a frozen guard scale for regression; E1T vs E10bT on classification
def gate_rerun(family: str, arm: str, stored: str) -> bool:
    """G2 / G3: rerun a stored cell with `arm`; every run's detections must equal the stored `stored` arm's."""
    paths, max_steps, configs, is_reg = ALL[family]
    det = pd.read_csv(os.path.join(OUT, family, stored, "detections.csv"))
    same = True
    for path in paths:
        for base_label, mt, mk in configs:
            _, dets, *_ = run(path, mt, max_steps, mk, {**ARMS[arm], **(P3 if is_reg else {})})
            g = det[(det["dataset"] == dataset_key(path)) & (det["config"] == base_label.replace("/", "-%s/" % stored))]
            ok = sorted(dets) == sorted(zip(g["warning_t"].astype(int), g["confirmation_t"].astype(int)))
            print("%s %s %s: %d detections vs stored %s %d -> %s" % (
                family, base_label, arm, len(dets), stored, len(g), "IDENTICAL" if ok else "DIFFERENT"), flush=True)
            same &= ok
    return same


def check_e13() -> None:
    """G4: the frozen guard scale through the pipeline itself (htr, P3 on, a reference that never fires)."""
    from src.config import PipelineConfig
    from src.pipeline import ConceptDriftPipeline

    class Flat:  # a reference detector that never fires: only the guard can confirm
        zone, combo_name, stats = False, "flat", {}

        def update_values(self, w, d):
            return False, False

        def reset(self):
            pass

    def pipe_run(X, y):
        pipe = ConceptDriftPipeline(PipelineConfig(
            model_type="htr", use_ecpf=True, ecpf_signal_mode="dual_adwin", ecpf_warning_signal="error",
            ecpf_drift_signal="error", ecpf_detector_min_instances=30, trace_enabled=True, **ARMS["E10bFT"], **P3))
        pipe._ecpf_detector = Flat()
        dets = [(int(d.timestamp), i) for i, _, _, ds, _ in pipe.run_stream(X, y, warm_start_samples=WARM_START)
                for d in ds]
        return pd.DataFrame(pipe.tracer._signals), dets
    rng = np.random.default_rng(0)
    n = 8000
    X, t = rng.random((n, 2)), np.arange(n)
    f = 10 * X[:, 0] + 5 * X[:, 1]
    sig, dets = pipe_run(X, f + rng.normal(0, 1, n) + np.where(t >= 4000, rng.normal(0, 6, n), 0))
    print("G4 residual step up at 4000: confirmations %s" % dets)
    assert dets and all(w >= 4000 for w, _ in dets)                            # (b) a raw rise confirms, not before
    idle = sig["guard_in"].isna().to_numpy()
    ts = sig["t"].to_numpy(int)
    expect = ts < ts[0] + 500
    for _, c in dets:
        expect |= (ts > c) & (ts < c + 500)
    assert (idle == expect).all()                                               # (a) idle exactly k steps per era
    sig, dets = pipe_run(X, f + rng.normal(0, 1, n) * np.linspace(4, 1, n))
    print("G4 residual falling slowly, no drift: confirmations %s" % dets)
    assert not dets                                                             # (b) a decline stays quiet
    print("G4 PASS")


def e13_guard_events(arm: str, held: str = "e13"):
    """Every regression confirmation of `arm` in a round (E13 by default): trigger (guard / ref / both, from an exact replay of both drift
    arms), FP@3000 label, hit delay, raw residual over the guard cut's dropped / kept sub-windows, and rr = raw over
    the last 300 steps / the 2000 before. Returns (DataFrame, replay mismatches); A0(b) needs 0 mismatches."""
    import diagnose_regression_fp as drf
    from detectors.meta_ecpf.adwin_family import _ADWINAdapter
    mk = lambda one: _ADWINAdapter(delta=0.05, min_num_instances=30, one_sided=one)
    rows, bad = [], 0
    for fam, a, path, ds, cfg, g, sig in iter_runs(held):
        if a != arm or not ALL[fam][3]:
            continue
        gt = scored_gt(fam, load_stream(path, ALL[fam][1])[2])
        dets = sorted(zip(g["warning_t"].astype(int), g["confirmation_t"].astype(int)), key=lambda d: d[1])
        drf.PERTURBATION = 3000
        lab = {r["confirmation_t"]: r for r in drf.classify(dets, gt, sig, [], len(sig))}
        drf.PERTURBATION = 1000
        pos = {t: i for i, t in enumerate(sig["t"].to_numpy(int))}
        conf = {pos[ct] for _, ct in dets}
        gin = (sig["guard_in"] if "guard_in" in sig else sig["err"]).to_numpy(float)
        ref, sw = sig["ref_err"].to_numpy(float), sig["ref_switch"].fillna(0).to_numpy(bool)
        gd, rd, cut = mk(True), mk(False), {}
        gf, rf = np.zeros(len(sig), bool), np.zeros(len(sig), bool)
        for i in range(len(sig)):
            if sw[i]:   # _switch_reference runs before the step's detector update
                rd = mk(False)
            if not np.isnan(gin[i]):
                wb = int(gd._detector.width)
                if gd.update(gin[i]):
                    gf[i], cut[i], gd = True, (wb, int(gd._detector.width)), mk(True)
            if rd.update(ref[i]):
                rf[i], rd = True, mk(False)
            if i in conf:
                gd, rd = mk(True), mk(False)
        bad += int((gf != sig["guard_drift"].astype(bool).to_numpy()).sum())
        bad += int(((gf | rf) != sig["is_drift"].astype(bool).to_numpy()).sum())
        raw = sig["raw"].to_numpy(float)
        for _, ct in dets:
            i, r = pos[ct], lab[ct]
            row = {"family": fam, "learner": learner(cfg), "confirmation_t": ct, "label": r["label"],
                   "delay": r["gap_prev_gt"] if r["label"] == "hit" else np.nan,
                   "src": "both" if gf[i] and rf[i] else "guard" if gf[i] else "ref",
                   "rr": raw[max(0, i - 299):i + 1].mean() / raw[max(0, i - 2299):max(1, i - 299)].mean()}
            if gf[i]:
                wb, wa = cut[i]
                row.update(raw_w0=raw[i - wb:i - wa + 1].mean(), raw_w1=raw[i - wa + 1:i + 1].mean())
            rows.append(row)
    ev = pd.DataFrame(rows)
    if len(ev):
        ev["fp"] = ev["label"].isin(FP)
        ev["guard"] = ev["src"] != "ref"
        ev["catch"] = ev.get("raw_w1", np.nan) <= 1.05 * ev.get("raw_w0", np.nan)
    return ev, bad


def judged_round(label: str, held: str, fams, arms_of_fam, groups, arms_of_group, mae_group=None):
    """Front half of the E13 / E14 verdicts: completeness, A0 confirmation ages, the per-group table.
    Returns (t, q, df, runs) at 3000 steps with excess hits, or None (incomplete or invalid: no verdict)."""
    n_cells = sum(len(arms_of_fam(f)) for f in fams)
    missing = [(f, a) for f in fams for a in arms_of_fam(f)
               if not os.path.exists(os.path.join(OUT, f, a, "detections.csv"))]
    if missing:   # paused or still running: never judge a partial matrix
        print("%s INCOMPLETE: %d of %d cells missing -- no verdict" % (label, len(missing), n_cells))
        return None
    ages = []
    for f in fams:
        for a in arms_of_fam(f):
            try:
                ages += pd.read_csv(os.path.join(OUT, f, a, "detections.csv"))["confirm_age"].tolist()
            except pd.errors.EmptyDataError:
                pass
    print("## A0(a) longest warning->confirmation age: %d -> %s" % (
        max(ages, default=0), "VALID" if max(ages, default=0) <= 1001 else "INVALID"))
    if max(ages, default=0) > 1001:
        print("%s INVALID -- no verdict" % label)
        return None
    df = rescore(show=False, held=held)
    if df is None:
        print("RESCORE INVALID -- no verdict")
        return None
    runs = runs_table(held=held)
    grp = lambda f: f.rsplit("-", 1)[0]
    df, runs["group"] = df[df["ext"] == 3000].copy(), runs["family"].map(grp)
    df["group"] = df["family"].map(grp)
    df["xs"] = df["tp"] - np.array(chance_hits(df))
    t = df.groupby(["group", "arm"])[["n_gt", "tp", "fp", "xs", "pre"]].sum()
    assert (t.groupby("group")["n_gt"].nunique() == 1).all(), "N differs across arms: a cell is missing"
    q = runs.groupby(["group", "arm"])["quality"].mean()
    med = lambda s: float(np.median(sum(s, []))) if sum(s, []) else np.nan
    dl = df.groupby(["group", "arm"])["delays"].apply(lambda s: med(list(s)))
    print("\n## Per group (3000-step windows; quality = accuracy%s; preFP only read on injected groups)" % (
        ", MAE for %s" % mae_group if mae_group else ""))
    print("%-12s %-7s %4s %5s %5s %8s %6s %7s %9s" % ("group", "arm", "N", "TP", "FP", "excess", "preFP", "delay",
                                                    "quality"))
    for g in groups:
        for a in arms_of_group(g):
            r = t.loc[(g, a)]
            print("%-12s %-7s %4d %5d %5d %8.1f %6d %7.0f %9.4f" % (g, a, r["n_gt"], r["tp"], r["fp"], r["xs"], r["pre"],
                                                                    dl[(g, a)], q[(g, a)]))
    return t, q, df, runs


def crit_p12(t, g, a):
    """P1 (pre-drift FP <= 30% of baseT, None if baseT < 10) and P2 (excess >= 90%) on an injected group."""
    pb, pa = t.loc[(g, "baseT"), "pre"], t.loc[(g, a), "pre"]
    p1 = bool(pa <= 0.30 * pb) if pb >= 10 else None
    p2 = bool(t.loc[(g, a), "xs"] >= 0.90 * t.loc[(g, "baseT"), "xs"])
    print("%s: P1 %s pre-drift FP %d vs baseT %d (%s) | P2 excess %.1f vs %.1f (need >=%.1f): %s" % (
        a, g, pa, pb, "not evaluable" if p1 is None else "need <=%.1f: %s" % (0.3 * pb, p1),
        t.loc[(g, a), "xs"], t.loc[(g, "baseT"), "xs"], 0.9 * t.loc[(g, "baseT"), "xs"], p2))
    return [p1 is not False, p2]


def crit_p3(t, g, a, ref: str = "baseT"):
    """P3: FP@3000 <= 50% of the baseline (not evaluable if it has < 6) and excess >= 90% of the baseline."""
    bfp, efp, bx, ex = t.loc[(g, ref), "fp"], t.loc[(g, a), "fp"], t.loc[(g, ref), "xs"], t.loc[(g, a), "xs"]
    fp_ok = bool(efp <= 0.5 * bfp) if bfp >= 6 else None
    tp_ok = bool(ex >= 0.9 * bx)
    print("%s: P3 %s FP@3000 %d vs %s %d (%s) | excess %.1f vs %.1f (need >=%.1f): %s" % (
        a, g, efp, ref, bfp, "not evaluable" if fp_ok is None else "need <=%.1f: %s" % (0.5 * bfp, fp_ok), ex, bx,
        0.9 * bx, tp_ok))
    return tp_ok and fp_ok is not False


def crit_p4(q, g, a, mae: bool = False, ref: str = "baseT"):
    """P4 quality guard: accuracy >= baseline - 0.01, or MAE <= 1.02 x baseline."""
    qb, qe = q[(g, ref)], q[(g, a)]
    ok = bool(qe <= 1.02 * qb) if mae else bool(qe >= qb - 0.01)
    print("%s: P4 %s quality %.4f vs %s %.4f: %s" % (a, g, qe, ref, qb, ok))
    return ok


def analyze_e13() -> None:
    """E13 verdict (docs/ECPF_E13_守衛凍結尺度_預註冊.md)."""
    B, MC, REG, ELEC, COV = "SYN2g67-B", "SYN2g67-MC", "SYN2g69-REG", "INJelec35", "INJcov01"
    res = judged_round("E13", "e13", E13, e13_arms, (B, MC, REG, ELEC, COV),
                       lambda g: E13_REG_ARMS if g == REG else E13_CLS_ARMS, mae_group=REG)
    if res is None:
        return
    t, q, df, runs = res
    print("\n## B: each arm vs baseT (recall = excess hits)")
    cls, reg = {}, {}
    for a in ("E1T", "E10bT"):
        ok = []
        for g in (ELEC, COV):
            ok += crit_p12(t, g, a)
        ok += [crit_p3(t, g, a) for g in (B, MC)] + [crit_p4(q, g, a) for g in (B, MC, ELEC, COV)]
        cls[a] = all(ok)
    for a in ("E1T", "E2k500T", "E10bT", "E10bFT"):
        reg[a] = crit_p3(t, REG, a) & crit_p4(q, REG, a, mae=True)
    for a in ("E1T", "E2k500T", "E10bT", "E10bFT"):
        print("E13 verdict %s: classification %s; regression %s" % (
            a, "-" if a not in cls else "HOLDS" if cls[a] else "does NOT hold", "HOLDS" if reg[a] else "does NOT hold"))

    x = lambda g, a: float(t.loc[(g, a), "xs"])
    c = reg["E10bFT"] and x(REG, "E10bFT") >= x(REG, "E2k500T")
    print("\n## C (main decision): E10bFT holds for regression %s | excess E10bFT %.1f vs E2k500T %.1f -> %s" % (
        reg["E10bFT"], x(REG, "E10bFT"), x(REG, "E2k500T"),
        "E10bFT REPLACES E2k500T for regression" if c else "keep E2k500T for regression"))
    if c:
        print("   E10bT holds for classification in E13: %s -> %s" % (cls["E10bT"], (
            "ONE main method: E10bFT (== E10bT on classification)" if cls["E10bT"]
            else "conflict with E12 reported; classification stays as E12 decided, no unification claim")))

    ev = {a: e13_guard_events(a) for a in ("E10bT", "E10bFT")}
    bad = sum(b for _, b in ev.values())
    print("\n## A0(b) guard / reference replay mismatches on regression: %d -> %s" % (
        bad, "VALID" if not bad else "INVALID: M1 / M2 not read"))
    e, f = ev["E10bT"][0], ev["E10bFT"][0]
    for name, d in (("E10bT", e), ("E10bFT", f)):
        gfp = d[d["fp"] & d["guard"]]
        gh = d[(d["label"] == "hit") & d["guard"]]
        print("%-6s confirmations %d | FP %d (guard %d, catch-up pattern %d) | hits %d (guard %d, rr>=1.1 %d, "
              "median guard-hit delay %.0f)" % (name, len(d), d["fp"].sum(), len(gfp), int(gfp["catch"].sum()),
                                                (d["label"] == "hit").sum(), len(gh), int((gh["rr"] >= 1.1).sum()),
                                                gh["delay"].astype(float).median()))
        print("        FP rr %s" % " ".join("%.2f" % v for v in sorted(gfp["rr"])))
    if not bad:
        ge, gf_ = int((e["fp"] & e["guard"]).sum()), int((f["fp"] & f["guard"]).sum())
        m1 = bool(gf_ <= 0.30 * ge) if ge >= 5 else None
        real = int(((e["label"] == "hit") & e["guard"] & (e["rr"] >= 1.1)).sum())
        m2 = bool(int(((f["label"] == "hit") & f["guard"]).sum()) >= 0.70 * real)
        print("M1 guard FP E10bFT %d vs E10bT %d (need <=%.1f, E10bT>=5): %s" % (
            gf_, ge, 0.3 * ge, "not evaluable" if m1 is None else m1))
        print("M2 guard hits E10bFT %d vs E10bT's rr>=1.1 guard hits %d (need >=%.1f): %s" % (
            int(((f["label"] == "hit") & f["guard"]).sum()), real, 0.7 * real, m2))
        if c and m1 is not True:
            print("   C adopts E10bFT, but the catch-up explanation is NOT supported (M1)")

    print("\n## Q: E1T vs E10bT on classification, cost(w) = w * (N - excess) + FP@3000")
    cost = lambda g, a, w: w * (t.loc[(g, a), "n_gt"] - t.loc[(g, a), "xs"]) + t.loc[(g, a), "fp"]
    wins = 0
    for g in (B, MC, ELEC, COV):
        e1 = all(cost(g, "E1T", w) <= cost(g, "E10bT", w) + 1e-9 for w in C1_W)
        wins += e1
        who, ws = breakeven(x(g, "E10bT"), t.loc[(g, "E10bT"), "fp"], x(g, "E1T"), t.loc[(g, "E1T"), "fp"])
        print("%-12s %s | E1T <= E10bT at every w: %s | %s" % (
            g, " ".join("w=%d %.1f/%.1f" % (w, cost(g, "E1T", w), cost(g, "E10bT", w)) for w in C1_W), e1,
            "%s %s" % ("E10bT" if who == "main" else "E1T",
                       "never costlier" if ws == 0 else "cheaper once w > %.2f" % ws)))
    print("Q reading: E1T holds for classification %s, cheaper at every w in %d of 4 groups -> %s" % (
        cls["E1T"], wins, "MOA's one-sided rule SUFFICES for classification (recommend E1T)"
        if cls["E1T"] and wins >= 3 else "E10bT stays the classification main method"))

    print("\n## Regression per drift type (4 seeds pooled; cost at w = 1 / 10)")
    rd = df[df["group"] == REG].assign(kind=lambda d: d["family"].map(lambda s: s.rsplit("-", 1)[1].rstrip("0123456789")))
    k = rd.groupby(["kind", "arm"])[["n_gt", "fp", "xs"]].sum()
    for kd, _ in _KINDS:
        print("%-5s %s" % (kd, " | ".join("%s xs %.1f FP %d c %.0f/%.0f" % (
            a, k.loc[(kd, a), "xs"], k.loc[(kd, a), "fp"], (k.loc[(kd, a), "n_gt"] - k.loc[(kd, a), "xs"]) + k.loc[(kd, a), "fp"],
            10 * (k.loc[(kd, a), "n_gt"] - k.loc[(kd, a), "xs"]) + k.loc[(kd, a), "fp"]) for a in E13_REG_ARMS)))
    ra = runs[runs["group"] == REG]
    ra = ra[ra["arm"].isin(["E2k500T", "E10bT", "E10bFT"])].assign(max_age=lambda d: [int(s["ref_age"].max()) for s in d["sig"]])
    print("\nmax reference age (regression): %s" % ra.groupby("arm")["max_age"].max().to_dict())
    rows = []
    for (fm, ds, lr), g in runs[runs["group"] == REG].groupby(["family", "dataset", "learner"]):
        r = {z.arm: z for z in g.itertuples()}
        iv = scored_gt(fm, load_stream(r["E2k500T"].path, ALL[fm][1])[2])
        age = r["E2k500T"].sig.set_index("t")["ref_age"]
        sel = df[(df["family"] == fm) & (df["dataset"] == ds) & (df["learner"] == lr)]
        warn = {a: sel[sel["arm"] == a]["warn_t"].iloc[0] for a in E13_REG_ARMS}
        for s, e_ in iv:
            rows.append({"age": int(age.get(s, -1)), **{a: any(s <= w <= e_ + 3000 for w in warn[a]) for a in E13_REG_ARMS}})
    m = pd.DataFrame(rows)
    m["bin"] = pd.cut(m["age"], [-1, 10000, 10 ** 6], labels=["<10k", ">=10k"])
    print("regression hits per E2k500T reference age at drift onset:\n%s" % m.groupby("bin", observed=True)[
        E13_REG_ARMS].sum().assign(n=m.groupby("bin", observed=True).size()).to_string())


def analyze_e14() -> None:
    """E14 verdict (docs/ECPF_E14_分類確認_預註冊.md): does E10bFT hold for classification?"""
    B, MC, ELEC = "SYN2g89-B", "SYN2g89-MC", "INJelec69"
    res = judged_round("E14", "e14", E14, lambda f: E14_ARMS, (B, MC, ELEC), lambda g: E14_ARMS)
    if res is None:
        return
    t, q, df, runs = res
    a = "E10bFT"
    print("\n## B: E10bFT vs baseT (recall = excess hits)")
    ok = crit_p12(t, ELEC, a)
    p2 = ok[1]
    ok += [crit_p3(t, g, a) for g in (B, MC)] + [crit_p4(q, g, a) for g in (B, MC, ELEC)]
    print("\n## Main reading: %s" % (
        "ALL PASS -> classification CONFIRMED; one main method E10bFT for both tasks (classification holds in E12 and "
        "E14, missed in E13)" if all(ok) else "NOT all pass -> no one-method claim" + (
            "; INJ-elec P2 missed in two rounds running -> registered boundary condition of the main method"
            if not p2 else "")))

    e = df[df["group"] == ELEC].copy()
    print("\n## S1 learner split on %s: E10bFT excess / baseT" % ELEC)
    sl = e.groupby(["learner", "arm"])["xs"].sum().unstack("arm")
    for lr, r in sl.iterrows():
        print("%-6s baseT %5.1f  E10bFT %5.1f  ratio %.2f" % (lr, r["baseT"], r[a], r[a] / r["baseT"]))
    rat = (sl[a] / sl["baseT"]).tolist()
    print("-> %s" % ("shortfall bound to a learner" if min(rat) < 0.9 <= max(rat) else "not learner-bound"))

    print("\n## S2 electricity pooled with E13 (E13's E10bT == E10bFT on classification)")
    old = rescore(show=False, held="e13")
    old = old[(old["ext"] == 3000) & old["family"].str.startswith("INJelec35") & old["arm"].isin(["baseT", "E10bT"])].copy()
    old["xs"] = old["tp"] - np.array(chance_hits(old))
    old["arm"] = old["arm"].replace({"E10bT": a})
    both = pd.concat([old, e])
    pt = both.groupby("arm")[["pre", "xs"]].sum()
    print("pooled pre-drift FP E10bFT %d vs baseT %d (P1 need <=%.1f: %s) | excess %.1f vs %.1f (P2 need >=%.1f: %s)" % (
        pt.loc[a, "pre"], pt.loc["baseT", "pre"], 0.3 * pt.loc["baseT", "pre"], pt.loc[a, "pre"] <= 0.3 * pt.loc["baseT", "pre"],
        pt.loc[a, "xs"], pt.loc["baseT", "xs"], 0.9 * pt.loc["baseT", "xs"], pt.loc[a, "xs"] >= 0.9 * pt.loc["baseT", "xs"]))

    print("\n## S3 per injection method (abrupt + gradual pooled)")
    e["m"] = e["family"].map(lambda f: f.rsplit("-", 1)[1][:-1])
    print(e.groupby(["m", "arm"])[["n_gt", "tp", "pre", "xs"]].sum().round(1).unstack("arm").to_string())

    r10 = runs[runs["arm"] == a]
    n_guard = sum(int(x.sig.set_index("t")["guard_drift"].reindex(x.conf_t).fillna(0).sum()) for x in r10.itertuples())
    print("\nE10bFT confirmations %d, of which the leader guard fired the drift: %d; max reference age %d" % (
        sum(len(x.conf_t) for x in r10.itertuples()), n_guard, max(int(x.sig["ref_age"].max()) for x in r10.itertuples())))


def analyze_a3() -> None:
    """A3 verdict (docs/ECPF_A3_真實迴歸資料_預註冊.md): the main method on real regression streams without GT --
    MAE guard (Q1), number of confirmations (Q2), share of confirmations preceded by a real residual rise (Q3)."""
    missing = [(f, a) for f in A3 for a in A3_ARMS if not os.path.exists(os.path.join(OUT, f, a, "detections.csv"))]
    if missing:   # never judge a partial matrix
        print("A3 INCOMPLETE: %d of %d cells missing -- no verdict" % (len(missing), len(A3) * len(A3_ARMS)))
        return
    ages = []
    for f in A3:
        for a in A3_ARMS:
            try:
                ages += pd.read_csv(os.path.join(OUT, f, a, "detections.csv"))["confirm_age"].tolist()
            except pd.errors.EmptyDataError:
                pass
    print("## A0 longest warning->confirmation age: %d -> %s" % (
        max(ages, default=0), "VALID" if max(ages, default=0) <= 1001 else "INVALID"))
    if max(ages, default=0) > 1001:
        print("A3 INVALID -- no verdict")
        return
    rows = []
    for x in runs_table(held="a3").itertuples():
        raw, pos = x.sig["raw"].to_numpy(float), {t: i for i, t in enumerate(x.sig["t"].to_numpy(int))}
        rr = [raw[max(0, i - 299):i + 1].mean() / raw[max(0, i - 2299):max(1, i - 299)].mean()
              for i in (pos[t] for t in x.conf_t)]
        guard = int(x.sig.set_index("t")["guard_drift"].reindex(x.conf_t).fillna(0).sum()) if "guard_drift" in x.sig else 0
        rows.append({"family": x.family, "arm": x.arm, "learner": x.learner, "steps": len(raw), "mae": x.quality,
                     "conf": len(rr), "rise": sum(v >= 1.1 for v in rr), "guard": guard,
                     "max_age": int(x.sig["ref_age"].max()) if "ref_age" in x.sig else 0})
    m = pd.DataFrame(rows)
    print("\n## Per run (MAE after warm-up; rise = confirmations with rr >= 1.1; guard = fired by the leader guard)")
    print("%-14s %-8s %-4s %6s %10s %5s %5s %6s %8s" % ("data set", "arm", "lr", "steps", "MAE", "conf", "rise", "guard",
                                                      "max age"))
    for r in m.sort_values(["family", "learner", "arm"]).itertuples():
        print("%-14s %-8s %-4s %6d %10.3f %5d %5d %6d %8d" % (r.family, r.arm, r.learner, r.steps, r.mae, r.conf, r.rise,
                                                             r.guard, r.max_age))
    q, c = m.groupby(["family", "arm"])["mae"].mean(), m.groupby(["family", "arm"])["conf"].sum()
    print("\n## Q1 quality guard and Q2 confirmations, per data set (MAE = mean of the two learners)")
    q1, q2 = {}, {}
    for f in A3:
        q1[f] = bool(q[(f, "E10bFT")] <= 1.02 * q[(f, "baseT")])
        q2[f] = bool(c[(f, "E10bFT")] <= 0.5 * c[(f, "baseT")])
        print("%-14s Q1 MAE E10bFT %.3f vs baseT %.3f (ratio %.3f, need <=1.02): %s | E2k500T %.3f (ratio %.3f) | "
              "Q2 confirmations E10bFT %d vs baseT %d (need <=%.1f): %s | E2k500T %d" % (
                  f, q[(f, "E10bFT")], q[(f, "baseT")], q[(f, "E10bFT")] / q[(f, "baseT")], q1[f], q[(f, "E2k500T")],
                  q[(f, "E2k500T")] / q[(f, "baseT")], c[(f, "E10bFT")], c[(f, "baseT")], 0.5 * c[(f, "baseT")], q2[f],
                  c[(f, "E2k500T")]))
    tot = m.groupby("arm")[["conf", "rise"]].sum()
    share = tot["rise"] / tot["conf"]
    q3 = None if min(tot.loc["E10bFT", "conf"], tot.loc["baseT", "conf"]) < 5 else bool(share["E10bFT"] >= share["baseT"])
    print("\n## Q3 share of confirmations preceded by a real residual rise (rr >= 1.1), both data sets pooled")
    for a in A3_ARMS:
        print("%-8s %d of %d = %.2f" % (a, tot.loc[a, "rise"], tot.loc[a, "conf"], share[a]))
    print("Q3 E10bFT >= baseT: %s" % ("not readable (< 5 confirmations)" if q3 is None else q3))
    print("\nA3 conclusion: %s" % (
        "the main method is NOT WORSE than baseT on real regression data%s" % (
            ", with at most half the confirmations" if all(q2.values()) else "") if all(q1.values()) else
        "boundary condition -- Q1 fails on %s" % ", ".join(f for f in A3 if not q1[f])))


def check_d5() -> None:
    """D5 gate G3: the prediction-range guard on the regression models themselves."""
    from src.model_adapter import create_base_model
    rng = np.random.default_rng(0)
    X = rng.random((400, 3))
    y = 100 + 50 * X[:, 0] + rng.normal(0, 1, 400)
    for mt in ("htr", "hfr"):
        off, on = create_base_model(mt, {}), create_base_model(mt, {"clip_predictions": True})
        assert on.predict_one(X[0]) == off.predict_one(X[0]) == 0.0          # nothing seen yet: left alone
        for xi, yi in zip(X, y):
            off.learn_one(xi, yi)
            on.learn_one(xi, yi)
        lo, hi = y.min(), y.max()
        far = np.array([1e9, -1e9, 1e9])                                       # a row that makes a linear leaf extrapolate
        members = on.predict_per_model(far) if mt == "hfr" else [on.predict_one(far)]
        assert all(lo - (hi - lo) <= v <= hi + (hi - lo) for v in members), (mt, members)
        assert all(on.predict_one(xi) == off.predict_one(xi) for xi in X[:200])  # in-range predictions untouched
        assert create_base_model(mt, {}).clip_predictions is False              # default off
    print("G3 PASS")


def analyze_d5() -> None:
    """D5 development check (docs/ECPF_D5_預測範圍守衛_開發檢查.md): the regression learners' prediction-range
    guard on the A3 streams (R1) and on E13's regression streams (R2). Arms with the guard end in 'C'."""
    pair = dict(zip(D5_ARMS, ["baseT", "E2k500T", "E10bFT"]))
    reg = {f: v for f, v in E13.items() if v[3]}
    missing = [(f, a) for f in list(A3) + list(reg) for a in D5_ARMS
               if not os.path.exists(os.path.join(OUT, f, a, "detections.csv"))]
    if missing:
        print("D5 INCOMPLETE: %d cells missing -- nothing is read" % len(missing))
        return
    print("## R1: real regression streams (A3), guard on vs A3's stored runs")
    rows = []
    for x in runs_table(held="a3").itertuples():
        raw, pos = x.sig["raw"].to_numpy(float), {t: i for i, t in enumerate(x.sig["t"].to_numpy(int))}
        yv = load_stream(x.path, 0)[1]
        rr = [raw[max(0, i - 299):i + 1].mean() / raw[max(0, i - 2299):max(1, i - 299)].mean()
              for i in (pos[t] for t in x.conf_t)]
        rows.append({"family": x.family, "arm": x.arm, "learner": x.learner, "mae": x.quality, "max": raw.max(),
                     "wild": int((raw > 2 * (yv.max() - yv.min())).sum()), "conf": len(rr),
                     "rise": sum(v >= 1.1 for v in rr)})
    m = pd.DataFrame(rows)
    print("%-14s %-4s %-9s %12s %12s %5s %5s %5s" % ("data set", "lr", "arm", "MAE", "max |res|", "wild", "conf", "rise"))
    for r in m.sort_values(["family", "learner", "arm"]).itertuples():
        print("%-14s %-4s %-9s %12.4g %12.4g %5d %5d %5d" % (r.family, r.learner, r.arm, r.mae, r.max, r.wild, r.conf,
                                                         r.rise))
    c = m[m["arm"].isin(D5_ARMS)]
    r1a = int(c["wild"].sum()) == 0
    print("\nR1a steps with |residual| > 2 x target range under the guard: %d (without it: %d) -> %s" % (
        c["wild"].sum(), m[m["arm"].isin(pair.values())]["wild"].sum(), "blow-up GONE" if r1a else "blow-up REMAINS"))
    q, n = m.groupby(["family", "arm"])["mae"].mean(), m.groupby(["family", "arm"])["conf"].sum()
    r1b = {}
    for f in A3:
        r1b[f] = bool(q[(f, "E10bFTC")] <= 1.02 * q[(f, "baseTC")])
        print("R1b %-14s MAE E10bFTC %.3f vs baseTC %.3f (ratio %.3f, need <=1.02): %s | E2k500TC %.3f (ratio %.3f) | "
              "R1c confirmations E10bFTC %d vs baseTC %d (<= half: %s), E2k500TC %d" % (
                  f, q[(f, "E10bFTC")], q[(f, "baseTC")], q[(f, "E10bFTC")] / q[(f, "baseTC")], r1b[f],
                  q[(f, "E2k500TC")], q[(f, "E2k500TC")] / q[(f, "baseTC")], n[(f, "E10bFTC")], n[(f, "baseTC")],
                  bool(n[(f, "E10bFTC")] <= 0.5 * n[(f, "baseTC")]), n[(f, "E2k500TC")]))
    tot = c.groupby("arm")[["conf", "rise"]].sum()
    print("R1c share of confirmations with rr >= 1.1: %s" % ", ".join(
        "%s %d/%d = %.2f" % (a, tot.loc[a, "rise"], tot.loc[a, "conf"], tot.loc[a, "rise"] / tot.loc[a, "conf"])
        for a in D5_ARMS))

    print("\n## R2: E13's regression streams with the guard on")
    REG = "SYN2g69-REG"
    res = judged_round("D5-R2", "e13", reg, lambda f: D5_ARMS, (REG,), lambda g: list(pair.values()) + D5_ARMS,
                       mae_group=REG)
    if res is None:
        return
    t, q2, df, _ = res
    print()
    holds = crit_p3(t, REG, "E10bFTC", ref="baseTC") & crit_p4(q2, REG, "E10bFTC", mae=True, ref="baseTC")
    xe, xk = float(t.loc[(REG, "E10bFTC"), "xs"]), float(t.loc[(REG, "E2k500TC"), "xs"])
    r2a = bool(holds and xe >= xk)
    print("R2a E10bFTC holds vs baseTC: %s | excess E10bFTC %.1f vs E2k500TC %.1f -> %s" % (
        holds, xe, xk, "E13's main decision UNCHANGED under the guard" if r2a else "E13's main decision CHANGES"))
    d = df[df["group"] == REG]
    seq = {(r.family, r.dataset, r.learner, r.arm): (r.warn_t, r.conf_t) for r in d.itertuples()}
    for a, old in pair.items():
        keys = [k for k in seq if k[3] == a]
        same = sum(seq[k] == seq[k[:3] + (old,)] for k in keys)
        print("R2b %-9s runs identical to %-8s %2d of %d (htr %d, hfr %d) | TP %+d FP %+d excess %+.1f MAE %+.4f" % (
            a, old, same, len(keys), sum(seq[k] == seq[k[:3] + (old,)] for k in keys if k[2] == "htr"),
            sum(seq[k] == seq[k[:3] + (old,)] for k in keys if k[2] == "hfr"),
            t.loc[(REG, a), "tp"] - t.loc[(REG, old), "tp"], t.loc[(REG, a), "fp"] - t.loc[(REG, old), "fp"],
            t.loc[(REG, a), "xs"] - t.loc[(REG, old), "xs"], q2[(REG, a)] - q2[(REG, old)]))
    print("\nD5 conclusion: %s" % (
        "R1a, R1b and R2a hold -> the guard is the SUGGESTED setting for the regression learners (development "
        "evidence only; adoption needs unused real regression data)" if r1a and all(r1b.values()) and r2a else
        "R2a fails -> the guard changes the synthetic conclusion: not suggested" if not r2a else
        "the guard removes the blow-up%s; R1b fails on %s -> real regression data stays a boundary condition" % (
            "" if r1a else " only partly", ", ".join(f for f in A3 if not r1b[f]))))


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
    ap.add_argument("--analyze-d3", action="store_true", help="D3 dev check: E10bFT on A2 g00 (stale references)")
    ap.add_argument("--analyze-d4", action="store_true", help="D4 dev check: MAE cost of missed regression drifts")
    ap.add_argument("--analyze-c1", action="store_true", help="C1 readings (miss-weighted cost on E11 / E12)")
    ap.add_argument("--gate-e13", choices=["g2", "g3", "g4"], help="E13 pre-launch gates (G2 flag-off rerun, G3 "
                    "classification identity, G4 self-check)")
    ap.add_argument("--analyze-e13", action="store_true", help="E13 verdict (frozen guard scale; E1T vs E10bT)")
    ap.add_argument("--analyze-e14", action="store_true", help="E14 verdict (classification confirmation of E10bFT)")
    ap.add_argument("--analyze-a3", action="store_true", help="A3 verdict (real regression streams without GT)")
    ap.add_argument("--gate-d5", choices=["g2", "g3"], help="D5 gates (G2 flag-off rerun of an E13 cell, G3 self-check)")
    ap.add_argument("--analyze-d5", action="store_true", help="D5 dev check (prediction-range guard)")
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
    if a.analyze_d3:
        analyze_d3()
    if a.analyze_d4:
        analyze_d4()
    if a.analyze_c1:
        analyze_c1()
    if a.gate_e13 == "g2":
        print("G2 %s" % ("PASS" if gate_rerun("SYN2g45-REG-sud4", "E10bT", "E10bT") else "FAIL"))
    if a.gate_e13 == "g3":
        print("G3 %s" % ("PASS" if gate_rerun("SYN2g45-B-sud4", "E10bFT", "E10bT") else "FAIL"))
    if a.gate_e13 == "g4":
        check_e13()
    if a.analyze_e13:
        analyze_e13()
    if a.analyze_e14:
        analyze_e14()
    if a.analyze_a3:
        analyze_a3()
    if a.gate_d5 == "g2":
        print("G2 %s" % ("PASS" if gate_rerun("SYN2g69-REG-sud6", "E10bFT", "E10bFT") else "FAIL"))
    if a.gate_d5 == "g3":
        check_d5()
    if a.analyze_d5:
        analyze_d5()
