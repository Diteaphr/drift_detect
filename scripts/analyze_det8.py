#!/usr/bin/env python3
"""Score the preregistered DET8 comparison: G3 (frozen reference read by HDDM-A at 3e-4, leader guard) vs H3
(HDDM-A at 3e-4 on the leader's own loss), with plain HDDM-A (H) as the third arm.

Rules: docs/ECPF_DET8_預註冊.md. Scoring is DET3's (scripts/analyze_det3.py), the scorability rule is DET5's,
and judge() is DET7's; what differs: the arms, the fresh trials (g200-g279 electricity, g200-g239 covertype
and gas), which pairs are judged, and the matched-FP chord check.

    python scripts/analyze_det8.py --commit <sha>                          # full verdict
    python scripts/analyze_det8.py --commit <sha> --datasets electricity   # main verdict only, while the rest runs
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
import scripts.analyze_det3 as a  # noqa: E402
from scripts.analyze_det7 import COV, ELEC, GAS, GROUP, LONG, SOURCE_SHA256, judge  # noqa: E402

TRIALS = {ELEC: (200, 280), COV: (200, 240), GAS: (200, 240)}  # judged trials [first, end) per cell
ARMS = ("G3", "H3", "H")
H2 = {"支持": "G3 較多", "相反": "G3 較少", "沒有差別": "沒有差別"}
a.ARMS = {"G3": "det7_g3", "H3": "det8_h3", "H": "det1_zone_hddm_a_lw0"}
a.ROOT, a.OUT = REPO / "outputs/benchmark/det8", REPO / "outputs/det8"
a.group_of = GROUP.__getitem__


def check_sources(datasets):
    """G6: the generator reads the registered source files (each run's manifest hash is checked by score_one)."""
    for ds in datasets:
        assert LONG[ds] == a.REGISTRY[ds]["delta_max"], ds
        got = a.sha256(REPO / a.REGISTRY[ds]["generator"]["source"])
        assert got == SOURCE_SHA256[ds], (ds, got)


def load(commit):
    rows = []
    for ds in a.DATASETS:  # DET3's loader applies the trial range and the long window to a.INJ only
        a.INJ, a.LONG, a.TRIALS = ds, LONG[ds], TRIALS[ds]
        for arm in ARMS:
            rows += a.load_arm(arm, commit, [ds])
    return rows


def chord(look, keys):
    """Matched-FP check: G3's X minus the H3-H chord's X at G3's FP. Same seed and draw count as compare()."""
    v = {arm: np.array([[look[k + (arm,)]["fp"], look[k + (arm,)]["X"]] for k in keys], dtype=float) for arm in ARMS}

    def gap(s):  # s: arm -> sums with (fp, X) on the last axis
        (fg, xg), (f3, x3), (fh, xh) = (np.moveaxis(s[arm], -1, 0) for arm in ARMS)
        ok = (f3 < fg) & (fg < fh)
        return np.where(ok, xg - x3 - (fg - f3) * (xh - x3) / np.where(ok, fh - f3, 1.0), np.nan), ok

    point, ok = gap({arm: x.sum(axis=0) for arm, x in v.items()})
    idx = np.random.default_rng(a.SEED).integers(0, len(keys), size=(a.DRAWS, len(keys)))
    draws, ok_draws = gap({arm: x[idx].sum(axis=1) for arm, x in v.items()})
    out = {"sums": {arm: dict(zip(("fp", "X"), map(float, x.sum(axis=0)))) for arm, x in v.items()},
           "defined_share": float(ok_draws.mean())}
    if not ok:
        return dict(out, gap=None, ci=None, status="不內插：G3 的誤報不在 H3 與 H 之間")
    ci = [float(np.nanpercentile(draws, 2.5)), float(np.nanpercentile(draws, 97.5))]
    status = "高於連線" if ci[0] > 0 else "低於連線" if ci[1] < 0 else "沒有差別"
    return dict(out, gap=float(point), ci=ci, status=status)


def analyse(rows):
    look = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    keys = {ds: sorted({r["stream"] for r in rows if r["dataset"] == ds and r["gt"]}) for ds in a.DATASETS}
    for ds in a.DATASETS:  # G4: every arm ran on the same streams with the same labels
        streams = {r["stream"] for r in rows if r["dataset"] == ds and r["arm"] == "H"}
        for arm in ARMS:
            assert {r["stream"] for r in rows if r["dataset"] == ds and r["arm"] == arm} == streams, (ds, arm)
            for st in streams:
                assert look[(ds, st, arm)]["y_true_sha256"] == look[(ds, st, "H")]["y_true_sha256"], (ds, st, arm)

    def strata(datasets, kind=None):
        return {GROUP[ds]: [(ds, st) for st in keys[ds] if kind is None or look[(ds, st, "H")]["cell"].startswith(kind + "/")]
                for ds in datasets}

    comp = {}
    if ELEC in a.DATASETS:
        comp["main_electricity"] = judge(look, strata([ELEC]), "G3", "H3")
    for ds in (COV, GAS):
        if ds in a.DATASETS:
            comp[f"secondary_{GROUP[ds]}"] = judge(look, strata([ds]), "G3", "H3")
    for ds in a.DATASETS:
        comp[f"secondary_{GROUP[ds]}_window{LONG[ds]}"] = judge(look, strata([ds]), "G3", "H3", "w2500")
        comp[f"secondary_{GROUP[ds]}_H3_vs_H"] = judge(look, strata([ds]), "H3", "H")
        comp[f"secondary_{GROUP[ds]}_G3_vs_H"] = judge(look, strata([ds]), "G3", "H")
    if set(a.DATASETS) == set(TRIALS):
        comp["secondary_pooled"] = judge(look, strata(a.DATASETS), "G3", "H3")
    for ds in a.DATASETS:
        for kind in ("abrupt", "gradual"):
            for window, name in ((None, ""), ("w2500", f"_window{LONG[ds]}")):
                c = a.compare({GROUP[ds]: [a.pair(look[k + ("G3",)], look[k + ("H3",)], window) for k in strata([ds], kind)[GROUP[ds]]]})
                comp[f"h2_{GROUP[ds]}_{kind}{name}"] = dict(c, pair="G3 - H3", h2=H2[c["h2"]])

    def by(ds, pred=lambda r: True):
        return {arm: a.aggregate([r for r in rows if r["arm"] == arm and r["dataset"] == ds and pred(r)]) for arm in ARMS}

    cells = {ds: sorted({r["cell"] for r in rows if r["dataset"] == ds}) for ds in a.DATASETS}
    return {
        "comparisons": comp,
        "chord": {GROUP[ds]: chord(look, strata([ds])[GROUP[ds]]) for ds in a.DATASETS},
        "layers": {GROUP[ds]: by(ds) for ds in a.DATASETS},
        "cells": {f"{GROUP[ds]}/{c}": by(ds, lambda r, c=c: r["cell"] == c) for ds in a.DATASETS for c in cells[ds]},
        "methods": {f"{GROUP[ds]}/{m}": by(ds, lambda r, m=m: r["cell"].endswith("/" + m))
                    for ds in a.DATASETS for m in sorted({c.split("/")[1] for c in cells[ds]})},
        "long_window": {GROUP[ds]: {"steps": LONG[ds], **{arm: {k: sum(r["w2500"][k] for r in rows if r["arm"] == arm and r["dataset"] == ds)
                                                                for k in ("fp", "hits", "C", "X")} for arm in ARMS}}
                        for ds in a.DATASETS},
    }


def report(data):
    for name, c in data["comparisons"].items():
        arm_x = "" if "x_ci_by_arm" not in c else "  " + " ".join(
            f"X({k}) [{v[0]:+.2f},{v[1]:+.2f}]" for k, v in c["x_ci_by_arm"].items())
        print(f"{name:40s} {c['pair']:7s} n={sum(c['streams'].values()):4d}  dFP={c['delta_fp']:+5d} [{c['ci_fp'][0]:+.1f},{c['ci_fp'][1]:+.1f}] {c['p1']}"
              f"  dX={c['delta_x']:+7.2f} [{c['ci_x'][0]:+.2f},{c['ci_x'][1]:+.2f}] {c['p2']}  -> {c['verdict']}"
              f"  dAcc={c['delta_acc']:+.4f} [{c['ci_acc'][0]:+.4f},{c['ci_acc'][1]:+.4f}] {c['h3']}{arm_x}")
    for name, c in data["chord"].items():
        gap = "—" if c["gap"] is None else f"{c['gap']:+.2f} [{c['ci'][0]:+.2f},{c['ci'][1]:+.2f}]"
        print(f"chord_{name:34s} gap={gap}  {c['status']}  defined {c['defined_share']:.3f}  sums {c['sums']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="commit every run must have been produced at")
    ap.add_argument("--datasets", nargs="+", choices=sorted(GROUP.values()), default=sorted(GROUP.values()))
    args = ap.parse_args()
    a.DATASETS = [ds for ds in (ELEC, COV, GAS) if GROUP[ds] in args.datasets]
    a.EXPECTED = {ds: 8 * (hi - lo) for ds, (lo, hi) in TRIALS.items()}
    check_sources(a.DATASETS)
    rows = load(args.commit)
    data = analyse(rows)
    data["gates"] = {"commit": args.commit, "runs": {ds: {arm: sum(r["dataset"] == ds and r["arm"] == arm for r in rows)
                                                          for arm in ARMS} for ds in a.DATASETS},
                     "source_sha256": {ds: SOURCE_SHA256[ds] for ds in a.DATASETS}}
    # a partial score goes to the git-ignored partial/ so the runs still to come see a clean tree
    out, suffix = (a.OUT, "") if len(a.DATASETS) == len(TRIALS) else (a.OUT / "partial", "_" + "_".join(GROUP[ds] for ds in a.DATASETS))
    out.mkdir(parents=True, exist_ok=True)
    (out / f"det8_verdict_data{suffix}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / f"det8_run_scores{suffix}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=a.FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r.get(k) for k in a.FIELDS} for r in rows)
    report(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
