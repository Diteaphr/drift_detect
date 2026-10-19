#!/usr/bin/env python3
"""Score the preregistered DET7 comparison: G3 (frozen reference read by HDDM-A at 3e-4, leader guard) vs HDDM-A.

Rules: docs/ECPF_DET7_預註冊.md. Scoring is DET3's (scripts/analyze_det3.py) and the scorability rule is DET5's;
what differs: the arms, the fresh injected trials (electricity g40-g119, covertype and gas g50-g89), the long
window per dataset (its registry delta_max), and which pairs are judged.

    python scripts/analyze_det7.py --commit <sha>
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
import scripts.analyze_det3 as a  # noqa: E402

ELEC, COV, GAS = "injected_paper_electricity", "injected_paper_covertype", "injected_paper_gas_sensor_drift"
GROUP = {ELEC: "electricity", COV: "covertype", GAS: "gas"}
LONG = {ELEC: 2500, COV: 2500, GAS: 1500}  # each dataset's registry delta_max
TRIALS = {ELEC: (40, 120), COV: (50, 90), GAS: (50, 90)}  # judged trials [first, end) per cell
SOURCE_SHA256 = {  # G6: the source files registered in section 3 of the prereg
    ELEC: "49fe649b0c6a038dd39a9e8e9ad541ab2bd8096eaebc2bbfb46c0a19ccacde94",
    COV: "54c472fda7e5d0d64f4806050c36c9863cd6e1d2ff5038e2a50340793c98942d",
    GAS: "a89cc674add6eb83e6fcc16fe9cf1e31de83560ebc358c2e6abc01e35bc39801",
}
ARMS_BY_DS = {ELEC: ("G3", "G", "E", "H"), COV: ("G3", "H"), GAS: ("G3", "H")}
H2 = {"支持": "G3 較多", "相反": "G3 較少", "沒有差別": "沒有差別"}
P1_WORDS = {"成立": "較少", "不成立": "較多", "持平": "持平"}
a.ARMS = {"G3": "det7_g3", "G": "det7_g", "E": "e10bft", "H": "det1_zone_hddm_a_lw0"}
a.ROOT, a.OUT = REPO / "outputs/benchmark/det7", REPO / "outputs/det7"
a.DATASETS = [ELEC, COV, GAS]
a.EXPECTED = {ds: 8 * (hi - lo) for ds, (lo, hi) in TRIALS.items()}
a.group_of = GROUP.__getitem__


def check_sources():
    """G6: the generator reads the registered source files (each run's manifest hash is checked by score_one)."""
    for ds, want in SOURCE_SHA256.items():
        assert LONG[ds] == a.REGISTRY[ds]["delta_max"], ds
        got = a.sha256(REPO / a.REGISTRY[ds]["generator"]["source"])
        assert got == want, (ds, got)


def load(commit):
    rows = []
    for ds in a.DATASETS:  # DET3's loader applies the trial range and the long window to a.INJ only
        a.INJ, a.LONG, a.TRIALS = ds, LONG[ds], TRIALS[ds]
        for arm in ARMS_BY_DS[ds]:
            rows += a.load_arm(arm, commit, [ds])
    return rows


def judge(look, strata, x, ref, window=None):
    """DET3's paired comparison of x against ref, plus DET5's scorability rule (each arm's own X CI, same draws)."""
    c = a.compare({g: [a.pair(look[k + (x,)], look[k + (ref,)], window) for k in keys] for g, keys in strata.items()})
    alone = {}
    for arm in (x, ref):  # same strata, order and sizes as above, so compare() draws the same streams
        side = {g: [look[k + (arm,)][window] if window else look[k + (arm,)] for k in keys] for g, keys in strata.items()}
        alone[arm] = a.compare({g: [(s["fp"], s["X"], 0.0, 1.0, 0.0, 1.0) for s in items] for g, items in side.items()})
    assert abs(alone[x]["delta_x"] - alone[ref]["delta_x"] - c["delta_x"]) < 1e-6, (alone, c)
    c["pair"] = f"{x} - {ref}"
    c["x_ci_by_arm"] = {arm: r["ci_x"] for arm, r in alone.items()}
    c["scorable"] = any(ci[0] > 0 for ci in c["x_ci_by_arm"].values())
    if not c["scorable"]:
        c["p2"] = "不可判定"
        c["verdict"] = f"兩組的偵測都接近碰運氣；誤報 {x} {P1_WORDS[c['p1']]}"
    return c


def analyse(rows):
    look = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    keys = {ds: sorted({r["stream"] for r in rows if r["dataset"] == ds and r["gt"]}) for ds in a.DATASETS}
    for ds in a.DATASETS:  # G4: every arm ran on the same streams with the same labels
        streams = {r["stream"] for r in rows if r["dataset"] == ds and r["arm"] == "H"}
        for arm in ARMS_BY_DS[ds]:
            assert {r["stream"] for r in rows if r["dataset"] == ds and r["arm"] == arm} == streams, (ds, arm)
            for st in streams:
                assert look[(ds, st, arm)]["y_true_sha256"] == look[(ds, st, "H")]["y_true_sha256"], (ds, st, arm)

    def strata(datasets, kind=None):
        return {GROUP[ds]: [(ds, st) for st in keys[ds] if kind is None or look[(ds, st, "H")]["cell"].startswith(kind + "/")]
                for ds in datasets}

    comp = {"main_electricity": judge(look, strata([ELEC]), "G3", "H")}
    for ds in (COV, GAS):
        comp[f"secondary_{GROUP[ds]}"] = judge(look, strata([ds]), "G3", "H")
    for ds in a.DATASETS:
        comp[f"secondary_{GROUP[ds]}_window{LONG[ds]}"] = judge(look, strata([ds]), "G3", "H", "w2500")
    comp["secondary_electricity_default_G"] = judge(look, strata([ELEC]), "G", "H")
    comp["secondary_electricity_vs_E10bFT"] = judge(look, strata([ELEC]), "G3", "E")
    comp["secondary_pooled"] = judge(look, strata(a.DATASETS), "G3", "H")
    for ds in a.DATASETS:
        for kind in ("abrupt", "gradual"):
            for window, name in ((None, ""), ("w2500", f"_window{LONG[ds]}")):
                c = a.compare({GROUP[ds]: [a.pair(look[k + ("G3",)], look[k + ("H",)], window) for k in strata([ds], kind)[GROUP[ds]]]})
                comp[f"h2_{GROUP[ds]}_{kind}{name}"] = dict(c, pair="G3 - H", h2=H2[c["h2"]])

    def by(ds, pred=lambda r: True):
        return {arm: a.aggregate([r for r in rows if r["arm"] == arm and r["dataset"] == ds and pred(r)]) for arm in ARMS_BY_DS[ds]}

    cells = {ds: sorted({r["cell"] for r in rows if r["dataset"] == ds}) for ds in a.DATASETS}
    return {
        "comparisons": comp,
        "layers": {GROUP[ds]: by(ds) for ds in a.DATASETS},
        "cells": {f"{GROUP[ds]}/{c}": by(ds, lambda r, c=c: r["cell"] == c) for ds in a.DATASETS for c in cells[ds]},
        "methods": {f"{GROUP[ds]}/{m}": by(ds, lambda r, m=m: r["cell"].endswith("/" + m))
                    for ds in a.DATASETS for m in sorted({c.split("/")[1] for c in cells[ds]})},
        "long_window": {GROUP[ds]: {"steps": LONG[ds], **{arm: {k: sum(r["w2500"][k] for r in rows if r["arm"] == arm and r["dataset"] == ds)
                                                                for k in ("fp", "hits", "C", "X")} for arm in ARMS_BY_DS[ds]}}
                        for ds in a.DATASETS},
    }


def report(data):
    for name, c in data["comparisons"].items():
        arm_x = "" if "x_ci_by_arm" not in c else "  " + " ".join(
            f"X({k}) [{v[0]:+.2f},{v[1]:+.2f}]" for k, v in c["x_ci_by_arm"].items())
        print(f"{name:40s} {c['pair']:7s} n={sum(c['streams'].values()):3d}  dFP={c['delta_fp']:+5d} [{c['ci_fp'][0]:+.1f},{c['ci_fp'][1]:+.1f}] {c['p1']}"
              f"  dX={c['delta_x']:+7.2f} [{c['ci_x'][0]:+.2f},{c['ci_x'][1]:+.2f}] {c['p2']}  -> {c['verdict']}"
              f"  dAcc={c['delta_acc']:+.4f} [{c['ci_acc'][0]:+.4f},{c['ci_acc'][1]:+.4f}] {c['h3']}{arm_x}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="commit every run must have been produced at")
    args = ap.parse_args()
    check_sources()
    rows = load(args.commit)
    data = analyse(rows)
    data["gates"] = {"commit": args.commit, "runs": {ds: {arm: sum(r["dataset"] == ds and r["arm"] == arm for r in rows)
                                                          for arm in ARMS_BY_DS[ds]} for ds in a.DATASETS},
                     "source_sha256": SOURCE_SHA256}
    a.OUT.mkdir(parents=True, exist_ok=True)
    (a.OUT / "det7_verdict_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (a.OUT / "det7_run_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=a.FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r.get(k) for k in a.FIELDS} for r in rows)
    report(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
