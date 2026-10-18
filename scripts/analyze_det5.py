#!/usr/bin/env python3
"""Score the preregistered DET5 comparison: E10bFT vs HDDM-A on injected covertype and gas sensor drift.

Rules: docs/ECPF_DET5_預註冊.md. Scoring is DET3's (scripts/analyze_det3.py) with DET3's two presets on a single
tree. What differs: the two datasets, the injected trials (g00-g39), the long window (each dataset's delta_max),
one main verdict per dataset, the scorability rule, and the det_adwin description.

    python scripts/analyze_det5.py --commit <sha>
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
from scripts.run_benchmark import load_preset  # noqa: E402
from src.metrics.evaluate_run import pool_detection_runs  # noqa: E402

COV, GAS = "injected_paper_covertype", "injected_paper_gas_sensor_drift"
GROUP = {COV: "covertype", GAS: "gas"}
LONG = {COV: 2500, GAS: 1500}  # each dataset's registry delta_max
SOURCE_SHA256 = {  # G6: the source files registered in section 3 of the prereg
    COV: "54c472fda7e5d0d64f4806050c36c9863cd6e1d2ff5038e2a50340793c98942d",
    GAS: "a89cc674add6eb83e6fcc16fe9cf1e31de83560ebc358c2e6abc01e35bc39801",
}
TRIALS = 40
REFERENCE = "det_adwin"  # described only, never judged
H2 = {"支持": "主方法較多", "相反": "主方法較少", "沒有差別": "沒有差別"}
P1_WORDS = {"成立": "E 較少", "不成立": "E 較多", "持平": "持平"}
a.ROOT, a.OUT, a.TRIALS = REPO / "outputs/benchmark/det5", REPO / "outputs/det5", (0, TRIALS)
a.DATASETS, a.EXPECTED, a.group_of = [COV, GAS], {COV: 8 * TRIALS, GAS: 8 * TRIALS}, GROUP.__getitem__


def check_sources():
    """G6: the generator reads the registered source files (each run's manifest hash is checked by score_one)."""
    for ds, want in SOURCE_SHA256.items():
        assert LONG[ds] == a.REGISTRY[ds]["delta_max"], ds
        got = a.sha256(REPO / a.REGISTRY[ds]["generator"]["source"])
        assert got == want, (ds, got)


def load(arm, commit):
    rows = []
    for ds in a.DATASETS:  # DET3's loader applies the trial range and the long window to a.INJ only
        a.INJ, a.LONG = ds, LONG[ds]
        rows += a.load_arm(arm, commit, [ds])
    return rows


def load_reference(commit):
    """det_adwin's metrics.json per stream, after the same completeness checks as the judged arms."""
    runs = {}
    for ds in a.DATASETS:
        paths = sorted((a.ROOT / ds / REFERENCE).glob("*/manifest.json"))
        assert len(paths) == a.EXPECTED[ds], (ds, REFERENCE, len(paths))
        for p in paths:
            m = a.read_json(p)
            assert m["preset"] == load_preset(REFERENCE) and m["git"] == {"commit": commit, "dirty": False}, p
            assert m["registry_entry"] == a.REGISTRY[ds] and m["max_steps"] is None, p
            runs[(ds, m["stream"])] = dict(a.read_json(p.parent / "metrics.json"), cell=m["cell"])
    return runs


def judge(look, strata, window=None):
    """DET3's paired comparison plus the scorability rule (each arm's own X CI, from the same draws)."""
    c = a.compare({g: [a.pair(look[k + ("E",)], look[k + ("H",)], window) for k in keys] for g, keys in strata.items()})
    alone = {}
    for arm in a.ARMS:  # same strata, order and sizes as above, so compare() draws the same streams
        side = {g: [look[k + (arm,)][window] if window else look[k + (arm,)] for k in keys] for g, keys in strata.items()}
        alone[arm] = a.compare({g: [(s["fp"], s["X"], 0.0, 1.0, 0.0, 1.0) for s in items] for g, items in side.items()})
    assert abs(alone["E"]["delta_x"] - alone["H"]["delta_x"] - c["delta_x"]) < 1e-6, (alone, c)
    c["x_ci_by_arm"] = {arm: r["ci_x"] for arm, r in alone.items()}
    c["scorable"] = any(ci[0] > 0 for ci in c["x_ci_by_arm"].values())
    if not c["scorable"]:
        c["p2"] = "不可判定"
        c["verdict"] = f"兩組的偵測都接近碰運氣；誤報 {P1_WORDS[c['p1']]}"
    return c


def cerqueira(rows, ref):
    """Each cell pooled the way Cerqueira et al. report it ([d_s, d_s + delta_max]), next to the paper's best."""
    out = {}
    for ds in a.DATASETS:
        best = a.REGISTRY[ds].get("sota_by_cell", {})
        for cell in sorted({r["cell"] for r in rows if r["dataset"] == ds}):
            pooled = {arm: pool_detection_runs([a.read_json(REPO / r["path"] / "metrics.json") for r in rows
                                                if r["dataset"] == ds and r["cell"] == cell and r["arm"] == arm])
                      for arm in a.ARMS}
            pooled[REFERENCE] = pool_detection_runs([v for (d, _), v in ref.items() if d == ds and v["cell"] == cell])
            out[f"{GROUP[ds]}/{cell}"] = {**pooled, "paper_best": best.get(cell)}
    return out


def analyse(rows, ref):
    look = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    keys = {ds: sorted({r["stream"] for r in rows if r["dataset"] == ds and r["gt"]}) for ds in a.DATASETS}
    for ds in a.DATASETS:
        streams = {r["stream"] for r in rows if r["dataset"] == ds}
        assert {s for d, s in ref if d == ds} == streams, ds  # det_adwin ran on the same streams
        for st in streams:  # G4
            assert look[(ds, st, "E")]["y_true_sha256"] == look[(ds, st, "H")]["y_true_sha256"], (ds, st)

    def strata(datasets, kind=None):
        return {GROUP[ds]: [(ds, st) for st in keys[ds] if kind is None or look[(ds, st, "E")]["cell"].startswith(kind + "/")]
                for ds in datasets}

    comp = {}
    for ds in a.DATASETS:
        comp[f"main_{GROUP[ds]}"] = judge(look, strata([ds]))
    for ds in a.DATASETS:
        comp[f"secondary_{GROUP[ds]}_window{LONG[ds]}"] = judge(look, strata([ds]), "w2500")
    comp["secondary_pooled"] = judge(look, strata(a.DATASETS))
    for ds in a.DATASETS:
        for kind in ("gradual", "abrupt"):
            for window, name in ((None, ""), ("w2500", f"_window{LONG[ds]}")):
                c = a.compare({GROUP[ds]: [a.pair(look[k + ("E",)], look[k + ("H",)], window) for k in strata([ds], kind)[GROUP[ds]]]})
                comp[f"h2_{GROUP[ds]}_{kind}{name}"] = dict(c, h2=H2[c["h2"]])

    def by(pred):
        return {arm: a.aggregate([r for r in rows if r["arm"] == arm and pred(r)]) for arm in a.ARMS}

    cells = {ds: sorted({r["cell"] for r in rows if r["dataset"] == ds}) for ds in a.DATASETS}
    return {
        "comparisons": comp,
        "layers": {GROUP[ds]: by(lambda r, ds=ds: r["dataset"] == ds) for ds in a.DATASETS},
        "cells": {f"{GROUP[ds]}/{c}": by(lambda r, ds=ds, c=c: r["dataset"] == ds and r["cell"] == c)
                  for ds in a.DATASETS for c in cells[ds]},
        "methods": {f"{GROUP[ds]}/{m}": by(lambda r, ds=ds, m=m: r["dataset"] == ds and r["cell"].endswith("/" + m))
                    for ds in a.DATASETS for m in sorted({c.split("/")[1] for c in cells[ds]})},
        "long_window": {GROUP[ds]: {"steps": LONG[ds], **{arm: {k: sum(r["w2500"][k] for r in rows if r["arm"] == arm and r["dataset"] == ds)
                                                                for k in ("fp", "hits", "C", "X")} for arm in a.ARMS}}
                        for ds in a.DATASETS},
        "cerqueira_cells": cerqueira(rows, ref),
        "accuracy_all_runs": {arm: sum(r["acc"] * r["n_scored"] for r in rows if r["arm"] == arm)
                              / sum(r["n_scored"] for r in rows if r["arm"] == arm) for arm in a.ARMS},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="commit every run must have been produced at")
    args = ap.parse_args()
    check_sources()
    rows = load("E", args.commit) + load("H", args.commit)
    data = analyse(rows, load_reference(args.commit))
    data["gates"] = {"commit": args.commit, "runs_per_arm": len(rows) // 2, "source_sha256": SOURCE_SHA256}
    a.OUT.mkdir(parents=True, exist_ok=True)
    (a.OUT / "det5_verdict_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (a.OUT / "det5_run_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=a.FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r.get(k) for k in a.FIELDS} for r in rows)
    for name, c in data["comparisons"].items():
        arm_x = "" if "x_ci_by_arm" not in c else "  X(E) [{:+.2f},{:+.2f}] X(H) [{:+.2f},{:+.2f}]".format(
            *c["x_ci_by_arm"]["E"], *c["x_ci_by_arm"]["H"])
        print(f"{name:34s} n={sum(c['streams'].values()):3d}  dFP={c['delta_fp']:+5d} [{c['ci_fp'][0]:+.1f},{c['ci_fp'][1]:+.1f}] {c['p1']}"
              f"  dX={c['delta_x']:+7.2f} [{c['ci_x'][0]:+.2f},{c['ci_x'][1]:+.2f}] {c['p2']}  -> {c['verdict']}"
              f"  dAcc={c['delta_acc']:+.4f} [{c['ci_acc'][0]:+.4f},{c['ci_acc'][1]:+.4f}] {c['h3']}{arm_x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
