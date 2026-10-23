#!/usr/bin/env python3
"""Audit all DET3 paired runs and compute preregistered 10,000-draw CIs."""
from __future__ import annotations

import collections
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "scripts/analyze_det2_formal.py").exists():
    ROOT = Path("/Users/diteaphr/Desktop/26 Spring/drift_detect")
sys.path.insert(0, str(ROOT))
from scripts import analyze_det2_formal as prior

OUT = ROOT / "outputs/det3"
DET3_ROOT = ROOT / "outputs/benchmark/det3"
DET3_COMMIT = "b86f5d679cba136705214f9fe9a5d5460d6bcaa4"
ARMS = {
    "A1-lw0": (prior.DET1_ROOT, "det1_dual_adwin_lw0", prior.DET1_COMMIT),
    "A3-lw0": (prior.DET1_ROOT, "det1_zone_hddm_a_lw0", prior.DET1_COMMIT),
    "A1-lw1": (prior.DET2_ROOT, "det1_dual_adwin_lw1", prior.DET2_COMMIT),
    "A3-lw1": (prior.DET2_ROOT, "det1_zone_hddm_a_lw1", prior.DET2_COMMIT),
    "F-D0-lw0": (DET3_ROOT, "det3_full_dual_adwin_lw0", DET3_COMMIT),
    "F-D1-lw1": (DET3_ROOT, "det3_full_dual_adwin_lw1", DET3_COMMIT),
    "F-H1-lw1": (DET3_ROOT, "det3_full_hddm_a_lw1", DET3_COMMIT),
    "A4-lw0": (prior.DET1_ROOT, "det1_zone_rddm_lw0", prior.DET1_COMMIT),
    "A4-lw1": (prior.DET2_ROOT, "det1_zone_rddm_lw1", prior.DET2_COMMIT),
}
prior.ARMS = ARMS
prior.ORDER = list(ARMS)


def load_all():
    rows, hashes = [], {}
    for ds in prior.DATASETS:
        expected = {s["stem"] for s in prior.dataset_sources(prior.REGISTRY[ds], 20 if ds == "injected_paper_electricity" else None)}
        assert len(expected) == prior.COUNTS[ds]
        for arm, (root, preset, _) in ARMS.items():
            paths = sorted((root / ds / preset).glob("*/manifest.json"))
            assert len(paths) == prior.COUNTS[ds], (ds, arm, len(paths))
            assert {p.parent.name for p in paths} == expected, (ds, arm)
            rows.extend(prior.score_one(p.parent, arm, hashes) for p in paths)
    assert len(rows) == 9 * 205
    assert len(list(DET3_ROOT.rglob("manifest.json"))) == 615
    for ds in prior.DATASETS:
        for stream in {r["stream"] for r in rows if r["dataset"] == ds}:
            paired = [r for r in rows if r["dataset"] == ds and r["stream"] == stream]
            assert len(paired) == 9
            assert len({(r["true_hash"], r["true_dtype"], r["n_output"], r["n_input"]) for r in paired}) == 1
            assert len({r["gt"] for r in paired}) == 1
    prior.add_post_accuracy(rows)
    return rows


def compare(lookup, arm, base, keys):
    d = {metric: prior.paired_delta(lookup, arm, base, metric, keys)
         for metric in ("fp", "X", "acc", "post_acc")}
    d["p1"] = prior.condition(d["fp"]["ci"], "negative")
    d["p2"] = prior.condition(d["X"]["ci"], "positive")
    d["detection"] = prior.det1_verdict(d["p1"], d["p2"])
    if d["detection"] == "如實報告":
        d["detection"] = "持平"
    ci = d["acc"]["ci"]
    d["accuracy"] = "不可判定" if ci is None else "優於" if ci[0] > 0 else "不如" if ci[1] < 0 else "持平"
    return d


def summarize(rows):
    lookup = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    keys = {(r["dataset"], r["stream"]) for r in rows}
    assert len(keys) == 205
    by_arm = {a: prior.aggregate([r for r in rows if r["arm"] == a]) for a in ARMS}
    by_group = {g: {a: prior.aggregate([r for r in rows if r["arm"] == a and r["group"] == g]) for a in ARMS} for g in prior.GROUPS}
    by_type = {t: {a: prior.aggregate([r for r in rows if r["arm"] == a and t in r["types"]]) for a in ARMS} for t in prior.TYPES}
    contrasts = {
        "Q1_FD1_vs_PH": ("F-D1-lw1", "A3-lw0"),
        "Q1_secondary_FH1_vs_PH": ("F-H1-lw1", "A3-lw0"),
        "Q2_FD1_vs_FH1": ("F-D1-lw1", "F-H1-lw1"),
        "Q3_signal_lw0": ("F-D0-lw0", "A1-lw0"),
        "Q3_learn_full": ("F-D1-lw1", "F-D0-lw0"),
        "Q3_learn_paper": ("A1-lw1", "A1-lw0"),
        "Q3_hddm_components_lw1": ("F-H1-lw1", "A3-lw1"),
        "Q3_hddm_full_vs_paper": ("F-H1-lw1", "A3-lw0"),
    }
    total = {name: compare(lookup, arm, base, keys) for name, (arm, base) in contrasts.items()}
    strata = {"groups": {}, "types": {}}
    for g in prior.GROUPS:
        subset = {key for key in keys if lookup[(*key, "A1-lw0")]["group"] == g}
        strata["groups"][g] = {name: compare(lookup, arm, base, subset) for name, (arm, base) in contrasts.items()}
    for t in prior.TYPES:
        subset = {key for key in keys if t in lookup[(*key, "A1-lw0")]["types"]}
        strata["types"][t] = {name: compare(lookup, arm, base, subset) for name, (arm, base) in contrasts.items()}
    warnings = {}
    for arm in ARMS:
        selected = [r for r in rows if r["arm"] == arm]
        counts = collections.Counter()
        for row in selected:
            counts.update(row["warning"])
        warnings[arm] = dict(counts)
        assert sum(v for k, v in counts.items() if k.startswith("open:")) == sum(v for k, v in counts.items() if k.startswith(("close:", "censored:")))
    no_gt = {arm: prior.aggregate([r for r in rows if r["arm"] == arm and not r["gt"]]) for arm in ARMS}
    return {
        "metadata": {"det1_commit": prior.DET1_COMMIT, "det2_commit": prior.DET2_COMMIT,
                     "det3_commit": DET3_COMMIT, "new_runs": 615, "paired_streams": 205,
                     "gt_streams": 204, "n_boot": prior.N_BOOT, "seed": prior.SEED},
        "arms": {a: {"root": str(root.relative_to(ROOT)), "preset": preset, "commit": commit} for a, (root, preset, commit) in ARMS.items()},
        "contrasts": contrasts, "by_arm": by_arm, "by_group": by_group, "by_type": by_type,
        "total": total, "strata": strata, "warnings": warnings, "no_gt": no_gt,
    }


def main():
    rows = load_all()
    summary = summarize(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "det3_verdict_data.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    fields = ["dataset", "stream", "cell", "group", "arm", "n_input", "n_output", "n_scored", "correct",
              "gt", "alarms", "tp", "fp", "fn", "hits", "C", "X", "O", "acc", "kappa",
              "post_correct", "post_count", "runtime", "rss", "frozen", "true_hash", "path"]
    with (OUT / "det3_run_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows({field: row.get(field) for field in fields} for row in rows)
    print("audited", len(rows), "rows", "new", len(list(DET3_ROOT.rglob('manifest.json'))))
    for name in ("Q1_FD1_vs_PH", "Q1_secondary_FH1_vs_PH", "Q2_FD1_vs_FH1"):
        d = summary["total"][name]
        print(name, d["detection"], d["accuracy"], "FP", d["fp"]["point"], "X", d["X"]["point"], "acc", d["acc"]["point"])


if __name__ == "__main__":
    main()
