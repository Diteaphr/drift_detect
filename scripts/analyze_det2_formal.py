#!/usr/bin/env python3
"""Audit DET2 artifacts and compute the preregistered paired comparisons."""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import math
import pathlib
import statistics
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from scripts.analyze_det1_formal import windows, union_length, type_flags, sha256
from scripts.run_benchmark import dataset_sources, load_preset, load_stream
from src.metrics.evaluate_run import detection_metrics

DET1_ROOT = REPO / "outputs/benchmark/det1"
DET2_ROOT = REPO / "outputs/benchmark/det2"
DET1_COMMIT = "0b98e29a708ee55f3bcc7f47165696981aa2e282"
DET2_COMMIT = "55bfc81999c98954ad5a4b4aa05df691faac0cff"
REGISTRY = json.loads((REPO / "configs/datasets_0921.json").read_text())["datasets"]
INSECTS = [d for d in REGISTRY if d.startswith("insects_") and d.endswith("_balanced")]
DATASETS = ["synthetic_multiclass", *INSECTS, "injected_paper_electricity"]
COUNTS = {"synthetic_multiclass": 40, "injected_paper_electricity": 160, **{d: 1 for d in INSECTS}}
ARMS = {
    "A1-lw0": (DET1_ROOT, "det1_dual_adwin_lw0", DET1_COMMIT),
    "A3-lw0": (DET1_ROOT, "det1_zone_hddm_a_lw0", DET1_COMMIT),
    "A4-lw0": (DET1_ROOT, "det1_zone_rddm_lw0", DET1_COMMIT),
    "A1-lw1": (DET2_ROOT, "det1_dual_adwin_lw1", DET2_COMMIT),
    "A3-lw1": (DET2_ROOT, "det1_zone_hddm_a_lw1", DET2_COMMIT),
    "A4-lw1": (DET2_ROOT, "det1_zone_rddm_lw1", DET2_COMMIT),
    "A1d-lw0": (DET2_ROOT, "det2_dual_adwin_d001_lw0", DET2_COMMIT),
}
ORDER = list(ARMS)
GROUPS = ("injected", "synthetic", "INSECTS")
TYPES = ("突變", "漸變", "incremental", "recurring")
SEED = 20261012
N_BOOT = 10_000


def group_of(ds):
    if ds == "injected_paper_electricity":
        return "injected"
    if ds == "synthetic_multiclass":
        return "synthetic"
    if ds in INSECTS:
        return "INSECTS"
    raise ValueError(ds)


def score_one(path, arm, hashes):
    root, preset_name, commit = ARMS[arm]
    manifest = json.loads((path / "manifest.json").read_text())
    metrics = json.loads((path / "metrics.json").read_text())
    events = json.loads((path / "warning_events.json").read_text())
    ds, stream = manifest["dataset"], manifest["stream"]
    assert path == root / ds / preset_name / stream
    assert manifest["preset"] == load_preset(preset_name)
    assert manifest["git"] == {"commit": commit, "dirty": False}
    assert manifest["registry_entry"] == REGISTRY[ds]
    assert manifest["max_steps"] is None and manifest["record_warning_events"]
    assert manifest["versions"]["river"] == "0.21.2"
    assert manifest["effective_config"]["model_type"] == "ht"
    assert manifest["effective_config"]["ecpf_learn_during_warning"] == ("lw1" in arm)
    assert manifest["effective_config"]["detector_delta"] == (0.01 if arm == "A1d-lw0" else 0.05)
    source_data = manifest["data"]
    source = REPO / source_data.get("file", source_data.get("generator", {}).get("source", ""))
    if source not in hashes:
        hashes[source] = sha256(source)
    assert hashes[source] == source_data.get("sha256", source_data.get("source_sha256"))
    gt = [tuple(x) for x in manifest["gt_intervals"]]
    n, scored_start = manifest["n_input"], max(manifest["detect_from"], manifest["warm_start"])
    with np.load(path / "preds.npz") as rec:
        true, pred = rec["y_true"].copy(), rec["y_pred"].copy()
        alarms_all = (rec["alarm_idx_input"] if manifest["coordinates"] == "input" else rec["alarm_idx"]).copy()
    assert len(true) == len(pred) == metrics["n_samples"]
    mask = np.isfinite(pred)
    correct = int(np.count_nonzero(true[mask] == pred[mask]))
    assert int(mask.sum()) == metrics["n_scored"]
    assert abs(correct / metrics["n_scored"] - metrics["acc_prequential"]) < 1e-12
    assert int((alarms_all >= manifest["detect_from"]).sum()) == metrics["n_alarms"]
    assert len(gt) == metrics["n_gt"]
    assert sum(e["event"] == "open" for e in events) == sum(e["event"] in ("close", "censored") for e in events)
    if "lw1" in arm:
        assert metrics["warning_frozen_steps"] == 0, path
    warnings = collections.Counter((e["event"], e["reason"]) for e in events)
    row = {
        "dataset": ds, "stream": stream, "arm": arm, "group": group_of(ds), "cell": manifest["cell"],
        "types": type_flags(ds, stream), "n_input": n, "n_output": len(true),
        "n_scored": metrics["n_scored"], "correct": correct,
        "acc": metrics["acc_prequential"], "kappa": metrics["kappa"],
        "runtime": manifest["runtime_s"], "rss": manifest["peak_rss_mb"],
        "alarms": metrics["n_alarms"], "gt": 0, "frozen": metrics["warning_frozen_steps"],
        "warning": {f"{event}:{reason}": count for (event, reason), count in warnings.items()},
        "confirmed_buffers": [e["buffer_len"] for e in events if e["event"] == "close" and e["reason"] == "confirmed"],
        "discarded_buffers": [e["buffer_len"] for e in events if e["event"] == "close" and e["reason"] != "confirmed"],
        "true_hash": hashlib.sha256(true.tobytes()).hexdigest(),
        "true_dtype": str(true.dtype), "path": str(path.relative_to(REPO)),
    }
    scored_gt = [(s, e) for s, e in gt if scored_start <= s < n]
    row["gt"] = len(scored_gt)
    if not scored_gt:
        assert ds == "insects_incremental_balanced" and metrics["tp"] is None and metrics["fp"] is None
        row.update(tp=None, fp=None, fn=None, hits=None, C=None, X=None, O=None, mdt=None)
        return row
    alarms = np.sort(alarms_all[alarms_all >= scored_start])
    det = detection_metrics(alarms, scored_gt, n_instances=n, delta_max=1000, anchor="start")
    bench = detection_metrics(
        alarms_all[alarms_all >= manifest["detect_from"]], gt,
        n_instances=n, delta_max=REGISTRY[ds]["delta_max"], anchor="start",
    )
    assert (bench["tp"], bench["fp"], bench["fn"]) == (metrics["tp"], metrics["fp"], metrics["fn"]), path
    if scored_gt == gt and REGISTRY[ds]["delta_max"] == 1000:
        assert (det["tp"], det["fp"], det["fn"]) == (metrics["tp"], metrics["fp"], metrics["fn"]), path
    wins = windows(gt, n, scored_start)
    outside = n - scored_start - union_length(wins)
    assert outside > 0, path
    chance = sum(-math.expm1(-det["fp"] / outside * (end - start + 1)) for start, end in wins)
    hits = det["n_episodes"] - det["fn"]
    row.update(tp=det["tp"], fp=det["fp"], fn=det["fn"], hits=hits,
               C=chance, X=hits - chance, O=outside, mdt=det["mdt"])
    return row


def load_all():
    rows, hashes = [], {}
    for ds in DATASETS:
        expected = {s["stem"] for s in dataset_sources(REGISTRY[ds], 20 if ds == "injected_paper_electricity" else None)}
        assert len(expected) == COUNTS[ds]
        for arm, (root, preset, _) in ARMS.items():
            base = root / ds / preset
            paths = sorted(base.glob("*/manifest.json"))
            assert len(paths) == COUNTS[ds], (ds, arm, len(paths))
            assert {p.parent.name for p in paths} == expected, (ds, arm)
            rows.extend(score_one(p.parent, arm, hashes) for p in paths)
    assert len(rows) == 7 * 205
    assert len(list(DET2_ROOT.rglob("manifest.json"))) == 820
    for ds in DATASETS:
        for stream in {r["stream"] for r in rows if r["dataset"] == ds}:
            paired = [r for r in rows if r["dataset"] == ds and r["stream"] == stream]
            assert len(paired) == 7
            assert len({(r["true_hash"], r["true_dtype"], r["n_output"], r["n_input"]) for r in paired}) == 1
            assert len({r["gt"] for r in paired}) == 1
    return rows


def add_post_accuracy(rows):
    injected_entry = REGISTRY["injected_paper_electricity"]
    sources = {s["stem"]: s for s in dataset_sources(injected_entry, 20)}
    masks = {}
    for row in rows:
        if not row["gt"]:
            row["post_correct"] = row["post_count"] = 0
            continue
        ds, stream = row["dataset"], row["stream"]
        key = (ds, stream)
        if key not in masks:
            base = DET1_ROOT / ds / ARMS["A1-lw0"][1] / stream
            manifest = json.loads((base / "manifest.json").read_text())
            with np.load(base / "preds.npz") as rec:
                base_true = rec["y_true"].copy()
            positions = np.arange(len(base_true))
            if ds == "injected_paper_electricity":
                source = load_stream(sources[stream], injected_entry)
                positions = source["kept"]
                assert np.array_equal(source["df"]["y"].to_numpy(dtype=float), base_true)
            mask = np.zeros(len(base_true), dtype=bool)
            for start, _ in manifest["gt_intervals"]:
                if start < max(manifest["warm_start"], manifest["detect_from"]):
                    continue
                mask |= (positions >= start) & (positions <= start + 999)
            masks[key] = mask
        root, preset, _ = ARMS[row["arm"]]
        with np.load(root / ds / preset / stream / "preds.npz") as rec:
            true, pred = rec["y_true"].copy(), rec["y_pred"].copy()
        mask = masks[key] & np.isfinite(pred)
        row["post_correct"] = int(np.count_nonzero(true[mask] == pred[mask]))
        row["post_count"] = int(mask.sum())


def aggregate(items):
    valid = [r for r in items if r["gt"]]
    scored = sum(r["n_scored"] for r in items)
    post_n = sum(r["post_count"] for r in valid)
    hits = sum(r["hits"] for r in valid)
    return {
        "runs": len(items), "gt_streams": len(valid), "gt": sum(r["gt"] for r in valid),
        "acc": sum(r["correct"] for r in items) / scored if scored else None,
        "post_acc": sum(r["post_correct"] for r in valid) / post_n if post_n else None,
        "kappa": sum(r["kappa"] * r["n_scored"] for r in items) / scored if scored else None,
        "alarms": sum(r["alarms"] for r in items), "tp": sum(r["tp"] for r in valid),
        "fp": sum(r["fp"] for r in valid), "fn": sum(r["fn"] for r in valid),
        "hits": hits, "C": sum(r["C"] for r in valid), "X": sum(r["X"] for r in valid),
        "mdt": sum(r["mdt"] * r["hits"] for r in valid if r["mdt"] is not None) / hits if hits else None,
        "frozen": sum(r["frozen"] for r in items), "runtime": sum(r["runtime"] for r in items),
        "rss_max": max((r["rss"] for r in items), default=None),
    }


def paired_delta(lookup, arm, base, metric, keys):
    """Stratified paired bootstrap; rate metrics recompute weighted numerator/denominator."""
    keys = sorted(keys)
    if metric in ("fp", "X", "post_acc"):
        keys = [key for key in keys if lookup[(*key, arm)]["gt"]]
    if not keys:
        return {"point": None, "ci": None, "n": 0}
    grouped = {g: [key for key in keys if lookup[(*key, arm)]["group"] == g] for g in GROUPS}
    rng = np.random.default_rng(SEED)
    if metric in ("fp", "X"):
        point, samples = 0.0, np.zeros(N_BOOT)
        for group in GROUPS:
            subset = grouped[group]
            if not subset:
                continue
            diff = np.array([lookup[(*key, arm)][metric] - lookup[(*key, base)][metric] for key in subset], dtype=float)
            assert np.isfinite(diff).all()
            point += diff.sum()
            idx = rng.integers(0, len(diff), size=(N_BOOT, len(diff)))
            samples += diff[idx].sum(axis=1)
    else:
        numer = "correct" if metric == "acc" else "post_correct"
        denom = "n_scored" if metric == "acc" else "post_count"
        total = np.zeros(4)
        sampled = np.zeros((N_BOOT, 4))
        for group in GROUPS:
            subset = grouped[group]
            if not subset:
                continue
            values = np.array([[lookup[(*key, arm)][numer], lookup[(*key, arm)][denom],
                                lookup[(*key, base)][numer], lookup[(*key, base)][denom]] for key in subset], dtype=float)
            total += values.sum(axis=0)
            idx = rng.integers(0, len(values), size=(N_BOOT, len(values)))
            sampled += values[idx].sum(axis=1)
        assert total[1] > 0 and total[3] > 0 and np.all(sampled[:, [1, 3]] > 0)
        point = total[0] / total[1] - total[2] / total[3]
        samples = sampled[:, 0] / sampled[:, 1] - sampled[:, 2] / sampled[:, 3]
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return {"point": float(point), "ci": [float(lo), float(hi)], "n": len(keys)}


def condition(ci, favorable):
    if ci is None:
        return "不可判定"
    lo, hi = ci
    if favorable == "negative":
        return "成立" if hi < 0 else "不成立" if lo > 0 else "持平"
    return "成立" if lo > 0 else "不成立" if hi < 0 else "持平"


def det1_verdict(p1, p2):
    if "不可判定" in (p1, p2):
        return "不可判定"
    if (p1, p2) == ("成立", "成立"):
        return "優於"
    if (p1, p2) == ("不成立", "不成立"):
        return "不如"
    if "持平" in (p1, p2):
        return "持平"
    return "如實報告"


def summarize(rows):
    lookup = {(r["dataset"], r["stream"], r["arm"]): r for r in rows}
    all_keys = {(r["dataset"], r["stream"]) for r in rows}
    assert len(all_keys) == 205
    by_arm = {arm: aggregate([r for r in rows if r["arm"] == arm]) for arm in ORDER}
    by_group = {g: {arm: aggregate([r for r in rows if r["group"] == g and r["arm"] == arm]) for arm in ORDER} for g in GROUPS}
    by_type = {typ: {arm: aggregate([r for r in rows if typ in r["types"] and r["arm"] == arm]) for arm in ORDER} for typ in TYPES}
    no_gt = {arm: aggregate([r for r in rows if r["arm"] == arm and not r["gt"]]) for arm in ORDER}
    q1, strata = {}, {"groups": {}, "types": {}}
    for detector in ("A1", "A3", "A4"):
        old, new = f"{detector}-lw0", f"{detector}-lw1"
        delta = {metric: paired_delta(lookup, new, old, metric, all_keys) for metric in ("acc", "post_acc", "fp", "X")}
        ci = delta["acc"]["ci"]
        delta["verdict"] = "改善" if ci[0] > 0 else "惡化" if ci[1] < 0 else "持平"
        delta["accuracy_up_detection_down"] = delta["verdict"] == "改善" and delta["X"]["ci"][1] < 0
        q1[detector] = delta
        for g in GROUPS:
            keys = {key for key in all_keys if lookup[(*key, new)]["group"] == g}
            strata["groups"].setdefault(g, {})[detector] = {
                metric: paired_delta(lookup, new, old, metric, keys) for metric in ("acc", "post_acc", "fp", "X")
            }
        for typ in TYPES:
            keys = {key for key in all_keys if typ in lookup[(*key, new)]["types"]}
            strata["types"].setdefault(typ, {})[detector] = {
                metric: paired_delta(lookup, new, old, metric, keys) for metric in ("acc", "post_acc", "fp", "X")
            }
    q2 = {}
    for other in ("A3-lw1", "A4-lw1"):
        d = {metric: paired_delta(lookup, "A1-lw1", other, metric, all_keys) for metric in ("fp", "X", "acc")}
        d["p1"] = condition(d["fp"]["ci"], "negative")
        d["p2"] = condition(d["X"]["ci"], "positive")
        d["verdict"] = det1_verdict(d["p1"], d["p2"])
        if d["verdict"] == "如實報告":
            d["verdict"] = "持平"
        q2[other] = d
    q3 = {"delta_vs_a1": {metric: paired_delta(lookup, "A1d-lw0", "A1-lw0", metric, all_keys) for metric in ("fp", "X", "acc")}}
    q3["det1_retest"] = {}
    for other in ("A3-lw0", "A4-lw0"):
        d = {metric: paired_delta(lookup, other, "A1d-lw0", metric, all_keys) for metric in ("fp", "X")}
        d["p1"] = condition(d["fp"]["ci"], "negative")
        d["p2"] = condition(d["X"]["ci"], "positive")
        d["verdict"] = det1_verdict(d["p1"], d["p2"])
        q3["det1_retest"][other] = d
    q3["changes_det1_verdict"] = any(d["verdict"] != "優於" for d in q3["det1_retest"].values())
    warnings = {}
    for arm in ORDER:
        selected = [r for r in rows if r["arm"] == arm]
        counts = collections.Counter()
        confirmed, discarded = [], []
        for row in selected:
            counts.update(row["warning"])
            confirmed.extend(row["confirmed_buffers"])
            discarded.extend(row["discarded_buffers"])
        warnings[arm] = {
            "counts": dict(counts), "opened": sum(v for k, v in counts.items() if k.startswith("open:")),
            "confirmed": counts["close:confirmed"], "zone_exit": counts["close:zone_exit"],
            "censored": sum(v for k, v in counts.items() if k.startswith("censored:")),
            "confirmed_buffer_median": statistics.median(confirmed) if confirmed else None,
            "discarded_buffer_median": statistics.median(discarded) if discarded else None,
        }
        assert warnings[arm]["opened"] == sum(v for k, v in counts.items() if k.startswith(("close:", "censored:")))
    return {
        "metadata": {"seed": SEED, "n_boot": N_BOOT, "det1_commit": DET1_COMMIT, "det2_commit": DET2_COMMIT,
                     "new_runs": 820, "reused_runs": 615, "paired_streams": 205, "gt_streams": 204},
        "by_arm": by_arm, "by_group": by_group, "by_type": by_type, "no_gt": no_gt,
        "q1": q1, "strata": strata, "q2": q2, "q3": q3, "warnings": warnings,
    }


def main():
    rows = load_all()
    add_post_accuracy(rows)
    summary = summarize(rows)
    out = REPO / "outputs/det2/det2_verdict_data.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    fields = ["dataset", "stream", "cell", "group", "arm", "n_input", "n_output", "n_scored", "correct",
              "gt", "alarms", "tp", "fp", "fn", "hits", "C", "X", "O", "acc", "kappa",
              "post_correct", "post_count", "runtime", "rss", "frozen", "true_hash", "path"]
    with (REPO / "outputs/det2/det2_run_scores.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)
    print("audited", len(rows), "rows", "summary", out)
    for detector, item in summary["q1"].items():
        print("Q1", detector, item["acc"]["point"], item["acc"]["ci"], item["verdict"])
    for arm, item in summary["q2"].items():
        print("Q2", arm, item["p1"], item["p2"], item["verdict"])
    print("Q3 changes DET1", summary["q3"]["changes_det1_verdict"])


if __name__ == "__main__":
    main()
