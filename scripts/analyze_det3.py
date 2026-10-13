#!/usr/bin/env python3
"""Score the preregistered DET3 comparison: E10bFT vs HDDM-A on DET1's streams.

Rules: docs/ECPF_DET3_預註冊.md. The window, false-alarm and excess-hit maths are
DET1's (scripts/analyze_det1_formal.py); only the arms, populations and the
extra window in S2 are new.

    python scripts/analyze_det3.py --commit <sha> --gate    # G2-G3 on the re-run HDDM-A arm only
    python scripts/analyze_det3.py --commit <sha>           # full verdict (both arms present)
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.metrics.evaluate_run import detection_metrics  # noqa: E402
from scripts.run_benchmark import dataset_sources, load_preset  # noqa: E402
from scripts.analyze_det1_formal import (  # noqa: E402
    DATASETS, EXPECTED, REGISTRY, group_of, sha256, type_flags, union_length, windows,
)

ROOT = REPO / "outputs/benchmark/det3"
OUT = REPO / "outputs/det3"
STORED = REPO / "outputs/det1/det1_run_scores.csv"
ARMS = {"E": "e10bft", "H": "det1_zone_hddm_a_lw0"}
SEED, DRAWS = 20261012, 10000
INJ = "injected_paper_electricity"
TYPES = ("突變", "漸變", "incremental", "recurring")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def score_window(alarms, scored_gt, n, start, delta):
    """DET1's per-run scoring for the inclusive window [d_s, d_s + delta]."""
    wins = windows(scored_gt, n, start, delta)
    det = detection_metrics(alarms, scored_gt, n_instances=n, delta_max=delta, anchor="start")
    O = n - start - union_length(wins)
    assert O > 0, O
    lam = det["fp"] / O
    C = sum(-math.expm1(-lam * (e - s + 1)) for s, e in wins)
    hits = det["n_episodes"] - det["fn"]
    return {"fp": det["fp"], "tp": det["tp"], "fn": det["fn"], "hits": hits, "C": C, "X": hits - C, "O": O, "mdt": det["mdt"]}


def score_one(path, arm, commit, source_hashes):
    m, v, events = read_json(path / "manifest.json"), read_json(path / "metrics.json"), read_json(path / "warning_events.json")
    ds, stream, n = m["dataset"], m["stream"], m["n_input"]
    gt = [tuple(z) for z in m["gt_intervals"]]
    assert m["preset"] == load_preset(ARMS[arm]), path
    assert m["git"] == {"commit": commit, "dirty": False}, (path, m["git"])
    assert m["registry_entry"] == REGISTRY[ds] and ds in DATASETS
    assert m["max_steps"] is None and m["record_warning_events"] and m["versions"]["river"] == "0.21.2"
    assert m["effective_config"]["model_type"] == "ht" and m["effective_config"]["ecpf_learn_during_warning"] is False
    source = REPO / m["data"].get("file", m["data"].get("generator", {}).get("source", ""))
    if source not in source_hashes:
        source_hashes[source] = sha256(source)
    assert source_hashes[source] == m["data"].get("sha256", m["data"].get("source_sha256")), path
    with np.load(path / "preds.npz") as rec:
        yt, yp = rec["y_true"].copy(), rec["y_pred"].copy()
        al = rec["alarm_idx_input"].copy() if m["coordinates"] == "input" else rec["alarm_idx"].copy()
    assert len(yt) == len(yp) == v["n_samples"] and n >= len(yt) and len(gt) == v["n_gt"]
    assert int((al >= m["detect_from"]).sum()) == v["n_alarms"]
    assert sum(e["event"] == "open" for e in events) == sum(e["event"] in ("close", "censored") for e in events), path
    start = max(m["detect_from"], m["warm_start"])
    alarms = np.sort(al[al >= start])
    scored_gt = [(s, e) for s, e in gt if start <= s < n]
    row = {
        "arm": arm, "dataset": ds, "stream": stream, "group": group_of(ds), "cell": m["cell"],
        "n_input": n, "n_output": len(yt), "n_scored": v["n_scored"], "acc": v["acc_prequential"], "kappa": v["kappa"],
        "runtime": m["runtime_s"], "alarms": len(alarms), "gt": len(scored_gt), "types": type_flags(ds, stream),
        "path": path.relative_to(REPO).as_posix(), "y_true_sha256": hashlib.sha256(yt.tobytes()).hexdigest(),
        "frozen": v.get("warning_frozen_steps", 0),
        "warning": dict(collections.Counter(f"{e['event']}:{e['reason']}" for e in events)),
    }
    if not scored_gt:
        assert ds == "insects_incremental_balanced" and v["tp"] is None and v["fp"] is None
        row.update(fp=None, tp=None, fn=None, hits=None, C=None, X=None, O=None, mdt=None, w2500=None)
        return row
    bench = detection_metrics(al[al >= m["detect_from"]], gt, n_instances=n, delta_max=REGISTRY[ds]["delta_max"], anchor="start")
    assert (bench["tp"], bench["fp"], bench["fn"]) == (v["tp"], v["fp"], v["fn"]), (path, bench, v)
    row.update(score_window(alarms, scored_gt, n, start, 1000))
    row["w2500"] = score_window(alarms, scored_gt, n, start, 2500) if ds == INJ else None
    return row


def load_arm(arm, commit):
    rows, sources = [], {}
    for ds in DATASETS:
        paths = sorted((ROOT / ds / ARMS[arm]).glob("*/manifest.json"))
        if len(paths) != EXPECTED[ds]:
            raise ValueError(f"{ds}/{ARMS[arm]}: {len(paths)} runs, expected {EXPECTED[ds]}")
        rows += [score_one(p.parent, arm, commit, sources) for p in paths]
        registered = {z["stem"] for z in dataset_sources(REGISTRY[ds], 20 if ds == INJ else None)}
        assert {r["stream"] for r in rows if r["dataset"] == ds} == registered, ds
    assert len(rows) == 205
    return rows


def stored_rows():
    with STORED.open(encoding="utf-8", newline="") as f:
        return {(r["dataset"], r["stream"], r["arm"]): r for r in csv.DictReader(f)}


def gate_g2(h_rows, stored):
    """Re-run HDDM-A must equal DET1's stored A3 scores stream by stream."""
    bad = []
    for r in h_rows:
        s = stored[(r["dataset"], r["stream"], "A3")]
        for k in ("n_input", "n_output", "n_scored", "gt", "alarms"):
            if int(float(s[k])) != r[k]:
                bad.append((r["dataset"], r["stream"], k, s[k], r[k]))
        if s["y_true_sha256"] != r["y_true_sha256"]:
            bad.append((r["dataset"], r["stream"], "y_true_sha256", s["y_true_sha256"][:12], r["y_true_sha256"][:12]))
        for k in ("acc", "kappa"):
            if abs(float(s[k]) - r[k]) > 1e-9:
                bad.append((r["dataset"], r["stream"], k, s[k], r[k]))
        if r["gt"]:
            for k in ("tp", "fp", "fn", "hits", "O"):
                if int(float(s[k])) != r[k]:
                    bad.append((r["dataset"], r["stream"], k, s[k], r[k]))
            for k in ("C", "X"):
                if abs(float(s[k]) - r[k]) > 1e-9:
                    bad.append((r["dataset"], r["stream"], k, s[k], r[k]))
    return bad


def pair(e, h, window=None):
    """One paired stream: (dFP, dX, accE*nE, nE, accH*nH, nH)."""
    a, b = (e[window], h[window]) if window else (e, h)
    return (a["fp"] - b["fp"], a["X"] - b["X"], e["acc"] * e["n_scored"], e["n_scored"], h["acc"] * h["n_scored"], h["n_scored"])


def compare(pairs_by_stratum):
    """Paired, stratified percentile bootstrap over streams; DET1's draw order and seed."""
    rng = np.random.default_rng(SEED)
    draws, point, sizes = np.zeros((DRAWS, 6)), np.zeros(6), {}
    for g, items in pairs_by_stratum.items():
        a = np.array(items, dtype=float)
        assert len(a) and np.isfinite(a).all(), g
        point += a.sum(axis=0)
        sizes[g] = len(a)
        idx = rng.integers(0, len(a), size=(DRAWS, len(a)))
        draws += a[idx].sum(axis=1)

    def dacc(x):
        return x[..., 2] / x[..., 3] - x[..., 4] / x[..., 5]

    def ci(x):
        return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]

    fp, x, acc = ci(draws[:, 0]), ci(draws[:, 1]), ci(dacc(draws))
    p1 = "成立" if fp[1] < 0 else "不成立" if fp[0] > 0 else "持平"
    p2 = "成立" if x[0] > 0 else "不成立" if x[1] < 0 else "持平"
    verdict = "優於" if (p1, p2) == ("成立", "成立") else "不如" if (p1, p2) == ("不成立", "不成立") else "持平" if "持平" in (p1, p2) else "有得有失"
    return {
        "streams": sizes, "delta_fp": int(point[0]), "ci_fp": fp, "p1": p1,
        "delta_x": float(point[1]), "ci_x": x, "p2": p2, "verdict": verdict,
        "h2": "支持" if x[0] > 0 else "相反" if x[1] < 0 else "沒有差別",
        "delta_acc": float(dacc(point)), "ci_acc": acc, "h3": "較好" if acc[0] > 0 else "較差" if acc[1] < 0 else "持平",
    }


def aggregate(items):
    valid = [r for r in items if r["gt"]]
    n = sum(r["n_scored"] for r in items)
    hits = sum(r["hits"] for r in valid)
    warn = collections.Counter()
    for r in items:
        warn.update(r["warning"])
    return {
        "runs": len(items), "gt": sum(r["gt"] for r in valid), "alarms": sum(r["alarms"] for r in items),
        "fp": sum(r["fp"] for r in valid), "tp": sum(r["tp"] for r in valid), "hits": hits,
        "C": sum(r["C"] for r in valid), "X": sum(r["X"] for r in valid),
        "mdt": sum(r["mdt"] * r["hits"] for r in valid if r["mdt"] is not None) / hits if hits else None,
        "acc": sum(r["acc"] * r["n_scored"] for r in items) / n, "kappa": sum(r["kappa"] * r["n_scored"] for r in items) / n,
        "runtime_s": sum(r["runtime"] for r in items), "frozen": sum(r["frozen"] for r in items), "warning": dict(warn),
    }


def analyse(rows, stored):
    look = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    keys = {g: sorted({(r["dataset"], r["stream"]) for r in rows if r["group"] == g and r["gt"]}) for g in ("injected", "synthetic", "INSECTS")}
    for ds, st in {(r["dataset"], r["stream"]) for r in rows}:
        assert look[(ds, st, "E")]["y_true_sha256"] == look[(ds, st, "H")]["y_true_sha256"], (ds, st)

    def pairs(group, keep=lambda ds, st: True, window=None):
        return [pair(look[(ds, st, "E")], look[(ds, st, "H")], window) for ds, st in keys[group] if keep(ds, st)]

    def cell_is(kind):
        return lambda ds, st: look[(ds, st, "E")]["cell"].startswith(kind + "/")

    def not_smoke(ds, st):
        return st.rsplit("_", 1)[1] not in ("g00", "g01", "g02")

    def vs_stored(arm):
        out = []
        for ds, st in keys["injected"]:
            e, s = look[(ds, st, "E")], stored[(ds, st, arm)]
            out.append((e["fp"] - float(s["fp"]), e["X"] - float(s["X"]), e["acc"] * e["n_scored"], e["n_scored"], float(s["acc"]) * float(s["n_scored"]), float(s["n_scored"])))
        return out

    comp = {
        "main_injected": compare({"injected": pairs("injected")}),
        "secondary_synthetic": compare({"synthetic": pairs("synthetic")}),
        "secondary_injected_synthetic": compare({"injected": pairs("injected"), "synthetic": pairs("synthetic")}),
        "secondary_det1_population": compare({g: pairs(g) for g in ("injected", "synthetic", "INSECTS")}),
        "h2_gradual": compare({"injected": pairs("injected", cell_is("gradual"))}),
        "h2_abrupt": compare({"injected": pairs("injected", cell_is("abrupt"))}),
        "s1_without_g00_g02": compare({"injected": pairs("injected", not_smoke)}),
        "s2_window2500": compare({"injected": pairs("injected", window="w2500")}),
        "s2_window2500_gradual": compare({"injected": pairs("injected", cell_is("gradual"), "w2500")}),
        "s2_window2500_abrupt": compare({"injected": pairs("injected", cell_is("abrupt"), "w2500")}),
        "s3_vs_dual_adwin_A1": compare({"injected": vs_stored("A1")}),
        "s3_vs_rddm_A4": compare({"injected": vs_stored("A4")}),
    }

    def by(pred):
        return {a: aggregate([r for r in rows if r["arm"] == a and pred(r)]) for a in ARMS}

    w2500 = {a: {k: sum(r["w2500"][k] for r in rows if r["arm"] == a and r["dataset"] == INJ) for k in ("fp", "hits", "C", "X")} for a in ARMS}
    return {
        "comparisons": comp,
        "layers": {g: by(lambda r, g=g: r["group"] == g and r["gt"]) for g in ("injected", "synthetic", "INSECTS")},
        "cells": {c: by(lambda r, c=c: r["cell"] == c) for c in sorted({r["cell"] for r in rows if r["cell"]})},
        "types": {t: by(lambda r, t=t: r["gt"] and r["group"] != "INSECTS" and t in r["types"]) for t in TYPES},
        "all_205_accuracy": {a: {"acc": sum(r["acc"] * r["n_scored"] for r in rows if r["arm"] == a) / sum(r["n_scored"] for r in rows if r["arm"] == a)} for a in ARMS},
        "injected_window2500": w2500,
    }


FIELDS = ["dataset", "stream", "cell", "arm", "group", "n_input", "n_output", "n_scored", "gt", "alarms", "tp", "fp", "fn", "hits", "C", "X", "O", "mdt", "acc", "kappa", "runtime", "frozen", "y_true_sha256", "path"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="commit every run must have been produced at")
    ap.add_argument("--gate", action="store_true", help="only score the re-run HDDM-A arm and compare it with DET1's stored scores")
    args = ap.parse_args()
    stored = stored_rows()
    h_rows = load_arm("H", args.commit)
    bad = gate_g2(h_rows, stored)
    print(f"G2/G3: {len(h_rows)} HDDM-A runs scored; {len(bad)} field mismatches against DET1's stored A3 scores")
    for b in bad[:40]:
        print("  mismatch", b)
    if args.gate:
        return 1 if bad else 0
    rows = load_arm("E", args.commit) + h_rows
    data = analyse(rows, stored)
    data["gates"] = {"commit": args.commit, "g2_mismatches": [list(map(str, b)) for b in bad], "runs_per_arm": 205}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "det3_verdict_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT / "det3_run_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r.get(k) for k in FIELDS} for r in rows)
    for name, c in data["comparisons"].items():
        print(f"{name:30s} n={sum(c['streams'].values()):3d}  dFP={c['delta_fp']:+5d} [{c['ci_fp'][0]:+.1f},{c['ci_fp'][1]:+.1f}] {c['p1']}"
              f"  dX={c['delta_x']:+7.2f} [{c['ci_x'][0]:+.2f},{c['ci_x'][1]:+.2f}] {c['p2']}  -> {c['verdict']}"
              f"  dAcc={c['delta_acc']:+.4f} [{c['ci_acc'][0]:+.4f},{c['ci_acc'][1]:+.4f}] {c['h3']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
