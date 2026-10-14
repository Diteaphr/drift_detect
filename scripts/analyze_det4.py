#!/usr/bin/env python3
"""Score the preregistered DET4 comparison: E10bFT vs HDDM-A on a 10-tree Hoeffding forest.

Rules: docs/ECPF_DET4_預註冊.md. Scoring is DET3's (scripts/analyze_det3.py); only the presets,
the injected trials (g20-g39) and the list of comparisons differ.

    python scripts/analyze_det4.py --commit <sha> --main-only   # injected layer only: the main verdict
    python scripts/analyze_det4.py --commit <sha>               # all three layers
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

BASE = {"E": "e10bft", "H": "det1_zone_hddm_a_lw0"}
FOREST = {"model_type": "hf", "model_kwargs": {"n_trees": 10, "max_features": "sqrt"}}
a.ARMS = {"E": "det4_e10bft_hf10", "H": "det4_zone_hddm_a_lw0_hf10"}
a.ROOT, a.OUT, a.MODEL, a.TRIALS = REPO / "outputs/benchmark/det4", REPO / "outputs/det4", "hf", (20, 40)


def check_presets():
    """G2: each forest preset is its single-tree original with only the learner changed."""
    for arm, base in BASE.items():
        assert load_preset(a.ARMS[arm])["config"] == {**load_preset(base)["config"], **FOREST}, arm


def analyse(rows, main_only):
    look = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    groups = ("injected",) if main_only else ("injected", "synthetic", "INSECTS")
    keys = {g: sorted({(r["dataset"], r["stream"]) for r in rows if r["group"] == g and r["gt"]}) for g in groups}
    for ds, st in {(r["dataset"], r["stream"]) for r in rows}:
        assert look[(ds, st, "E")]["y_true_sha256"] == look[(ds, st, "H")]["y_true_sha256"], (ds, st)

    def pairs(group, kind=None, window=None):
        return [a.pair(look[(ds, st, "E")], look[(ds, st, "H")], window) for ds, st in keys[group]
                if kind is None or look[(ds, st, "E")]["cell"].startswith(kind + "/")]

    comp = {
        "main_injected": a.compare({"injected": pairs("injected")}),
        "secondary_window2500": a.compare({"injected": pairs("injected", window="w2500")}),
        "h2_gradual": a.compare({"injected": pairs("injected", "gradual")}),
        "h2_abrupt": a.compare({"injected": pairs("injected", "abrupt")}),
        "window2500_gradual": a.compare({"injected": pairs("injected", "gradual", "w2500")}),
        "window2500_abrupt": a.compare({"injected": pairs("injected", "abrupt", "w2500")}),
    }
    if not main_only:
        comp.update(
            secondary_synthetic=a.compare({"synthetic": pairs("synthetic")}),
            secondary_injected_synthetic=a.compare({g: pairs(g) for g in ("injected", "synthetic")}),
            secondary_all_with_gt=a.compare({g: pairs(g) for g in groups}),
        )

    def by(pred):
        return {arm: a.aggregate([r for r in rows if r["arm"] == arm and pred(r)]) for arm in a.ARMS}

    data = {
        "comparisons": comp,
        "layers": {g: by(lambda r, g=g: r["group"] == g and r["gt"]) for g in groups},
        "cells": {c: by(lambda r, c=c: r["cell"] == c) for c in sorted({r["cell"] for r in rows if r["cell"]})},
        "injected_window2500": {arm: {k: sum(r["w2500"][k] for r in rows if r["arm"] == arm and r["dataset"] == a.INJ)
                                      for k in ("fp", "hits", "C", "X")} for arm in a.ARMS},
        "accuracy_all_runs": {arm: sum(r["acc"] * r["n_scored"] for r in rows if r["arm"] == arm)
                              / sum(r["n_scored"] for r in rows if r["arm"] == arm) for arm in a.ARMS},
    }
    if not main_only:
        data["types"] = {t: by(lambda r, t=t: r["gt"] and r["group"] != "INSECTS" and t in r["types"]) for t in a.TYPES}
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="commit every run must have been produced at")
    ap.add_argument("--main-only", action="store_true", help="score the injected layer only (main verdict)")
    args = ap.parse_args()
    check_presets()
    datasets = [a.INJ] if args.main_only else a.DATASETS
    rows = a.load_arm("E", args.commit, datasets) + a.load_arm("H", args.commit, datasets)
    data = analyse(rows, args.main_only)
    data["gates"] = {"commit": args.commit, "runs_per_arm": len(rows) // 2, "main_only": args.main_only}
    out = a.OUT / "logs/main_only" if args.main_only else a.OUT  # the interim copy stays out of git status
    out.mkdir(parents=True, exist_ok=True)
    (out / "det4_verdict_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "det4_run_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=a.FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r.get(k) for k in a.FIELDS} for r in rows)
    for name, c in data["comparisons"].items():
        print(f"{name:30s} n={sum(c['streams'].values()):3d}  dFP={c['delta_fp']:+5d} [{c['ci_fp'][0]:+.1f},{c['ci_fp'][1]:+.1f}] {c['p1']}"
              f"  dX={c['delta_x']:+7.2f} [{c['ci_x'][0]:+.2f},{c['ci_x'][1]:+.2f}] {c['p2']}  -> {c['verdict']}"
              f"  dAcc={c['delta_acc']:+.4f} [{c['ci_acc'][0]:+.4f},{c['ci_acc'][1]:+.4f}] {c['h3']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
