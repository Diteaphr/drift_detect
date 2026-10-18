#!/usr/bin/env python3
"""Score the preregistered DET6 comparison: E10bFT vs HDDM-A on slow gradual drift.

Rules: docs/ECPF_DET6_預註冊.md. Scoring is DET3's (scripts/analyze_det3.py) and DET5's scorability rule
(scripts/analyze_det5.py). What differs: the streams (scripts/generate_det6_streams.py), the main window, which
covers the whole transition plus 1000 steps ([d_s, d_e + 1000]), the strata (one per transition width), and a
second learner (DET4's forest presets) judged as a secondary.

    python scripts/analyze_det6.py --commit <sha>
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
import scripts.analyze_det5 as d5  # noqa: E402  (judge: DET3's comparison plus the scorability rule)
import scripts.generate_det6_streams as gen  # noqa: E402

DS = "synthetic_slow_gradual"
LEARNERS = {  # learner -> (model_type, arms)
    "single": ("ht", {"E": "e10bft", "H": "det1_zone_hddm_a_lw0"}),
    "forest": ("hf", {"E": "det4_e10bft_hf10", "H": "det4_zone_hddm_a_lw0_hf10"}),
}
DATA_SHA256 = "a815e10579f284c05b040cedc4fedd545b7ac5838d1c8590854ea3cc1c579566"  # G6: gen.digest() of the judged streams, registered in section 3 of the prereg
JUDGED = [gen.stem(w, g) for w in gen.WIDTHS for g in range(40)]
WINDOW = ("fp", "tp", "fn", "hits", "C", "X", "O", "mdt")
H2 = d5.H2
ROOT, OUT = REPO / "outputs/benchmark/det6", REPO / "outputs/det6"
a.DATASETS, a.INJ, a.group_of = [DS], DS, lambda ds: "synthetic"


def load(learner, commit):
    """Every judged stream for both arms of one learner. Top level = main window, "short" = [d_s, d_s + 1000]."""
    a.MODEL, a.ARMS = LEARNERS[learner]
    rows, sources = [], {}
    for arm, preset in a.ARMS.items():
        paths = sorted((ROOT / DS / preset).glob("*/manifest.json"))
        paths = [p for p in paths if p.parent.name in JUDGED]
        assert len(paths) == len(JUDGED), (preset, len(paths))  # G5
        for p in paths:
            a.LONG = int(a.read_json(p)["cell"][1:]) + 1000  # "w16000" -> [d_s, d_s + 17000] = [d_s, d_e + 1000]
            r = a.score_one(p.parent, arm, commit, sources)
            r["short"] = {k: r[k] for k in WINDOW}
            r.update(r.pop("w2500"), learner=learner)
            assert r["gt"] == gen.N_DRIFTS, p
            rows.append(r)
    assert sorted({r["stream"] for r in rows}) == sorted(JUDGED)
    return rows


def analyse(rows):
    look = {(r["learner"], r["stream"], r["arm"]): r for r in rows}
    for learner in LEARNERS:
        for st in JUDGED:  # G4
            assert look[(learner, st, "E")]["y_true_sha256"] == look[(learner, st, "H")]["y_true_sha256"], st

    def view(learner):
        return {(DS, st, arm): r for (lr, st, arm), r in look.items() if lr == learner}

    def strata(widths=gen.WIDTHS):
        return {f"w{w}": [(DS, st) for st in JUDGED if f"_w{w:05d}_" in st] for w in widths}

    single, forest = view("single"), view("forest")
    comp = {
        "main_single": d5.judge(single, strata()),
        "secondary_forest": d5.judge(forest, strata()),
        "secondary_single_window1000": d5.judge(single, strata(), "short"),
        "describe_forest_window1000": d5.judge(forest, strata(), "short"),
    }
    for learner, lk in (("single", single), ("forest", forest)):
        for w in gen.WIDTHS:
            c = a.compare({f"w{w}": [a.pair(lk[k + ("E",)], lk[k + ("H",)]) for k in strata([w])[f"w{w}"]]})
            comp[f"h2_{learner}_w{w}"] = dict(c, h2=H2[c["h2"]])

    def by(pred):
        return {arm: a.aggregate([r for r in rows if r["arm"] == arm and pred(r)]) for arm in a.ARMS}

    def short(pred):
        return {arm: {k: sum(r["short"][k] for r in rows if r["arm"] == arm and pred(r)) for k in ("fp", "hits", "C", "X")}
                for arm in a.ARMS}

    return {
        "comparisons": comp,
        "layers": {lr: by(lambda r, lr=lr: r["learner"] == lr) for lr in LEARNERS},
        "cells": {f"{lr}/w{w}": by(lambda r, lr=lr, w=w: r["learner"] == lr and r["cell"] == f"w{w:05d}")
                  for lr in LEARNERS for w in gen.WIDTHS},
        "window1000": {f"{lr}/w{w}": short(lambda r, lr=lr, w=w: r["learner"] == lr and r["cell"] == f"w{w:05d}")
                       for lr in LEARNERS for w in gen.WIDTHS},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="commit every run must have been produced at")
    args = ap.parse_args()
    assert gen.digest(gen.OUT) == DATA_SHA256  # G6 (each run's manifest hash is checked by score_one)
    rows = load("single", args.commit) + load("forest", args.commit)
    data = analyse(rows)
    data["gates"] = {"commit": args.commit, "runs_per_arm": len(JUDGED), "data_sha256": DATA_SHA256}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "det6_verdict_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["learner", *a.FIELDS, "short_fp", "short_hits", "short_C", "short_X"]
    with (OUT / "det6_run_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows({**{k: r.get(k) for k in fields}, **{f"short_{k}": r["short"][k] for k in ("fp", "hits", "C", "X")}}
                    for r in rows)
    for name, c in data["comparisons"].items():
        arm_x = "" if "x_ci_by_arm" not in c else "  X(E) [{:+.2f},{:+.2f}] X(H) [{:+.2f},{:+.2f}]".format(
            *c["x_ci_by_arm"]["E"], *c["x_ci_by_arm"]["H"])
        print(f"{name:30s} n={sum(c['streams'].values()):3d}  dFP={c['delta_fp']:+5d} [{c['ci_fp'][0]:+.1f},{c['ci_fp'][1]:+.1f}] {c['p1']}"
              f"  dX={c['delta_x']:+7.2f} [{c['ci_x'][0]:+.2f},{c['ci_x'][1]:+.2f}] {c['p2']}  -> {c['verdict']}"
              f"  dAcc={c['delta_acc']:+.4f} [{c['ci_acc'][0]:+.4f},{c['ci_acc'][1]:+.4f}] {c['h3']}{arm_x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
