#!/usr/bin/env python3
"""Audit DET4 artifacts and compute the preregistered paired analyses."""
from __future__ import annotations

import collections
import hashlib
import json
import math
import statistics
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.analyze_det1_formal import sha256, type_flags, union_length, windows  # noqa: E402
from scripts.run_benchmark import dataset_sources, load_preset, load_stream  # noqa: E402
from src.metrics.evaluate_run import detection_metrics  # noqa: E402


OUT = REPO / "outputs" / "det4"
DET4_ROOT = REPO / "outputs" / "benchmark" / "det4"
TIMING_ROOT = REPO / "outputs" / "benchmark" / "det4_strict_timing"
DET1_ROOT = REPO / "outputs" / "benchmark" / "det1"
DET3_ROOT = REPO / "outputs" / "benchmark" / "det3"
REGISTRY = json.loads((REPO / "configs/datasets_0921.json").read_text())["datasets"]

DETECTORS = ("adwin", "hddma", "rddm")
FRAMEWORKS = ("s0", "s1")
PRESETS = tuple(
    f"det4_{framework}_w{warning}_c{confirm}"
    for framework in FRAMEWORKS
    for warning in DETECTORS
    for confirm in DETECTORS
)
NON_REGRESSION = tuple(
    name for name, entry in REGISTRY.items() if entry["task"] != "regression"
)
INSECTS = tuple(name for name in NON_REGRESSION if name.startswith("insects_"))
T1_DATASETS = ("injected_paper_electricity", "synthetic_multiclass", *INSECTS)
T1_STREAMS = 205
T3_STREAMS = 240
SEED = 20261012
N_BOOT = 10_000

REUSED = {
    "det4_s0_wadwin_cadwin": (DET1_ROOT, "det1_dual_adwin_lw0", "0b98e29a708ee55f3bcc7f47165696981aa2e282"),
    "det4_s0_whddma_chddma": (DET1_ROOT, "det1_zone_hddm_a_lw0", "0b98e29a708ee55f3bcc7f47165696981aa2e282"),
    "det4_s0_wrddm_crddm": (DET1_ROOT, "det1_zone_rddm_lw0", "0b98e29a708ee55f3bcc7f47165696981aa2e282"),
    "det4_s1_wadwin_cadwin": (DET3_ROOT, "det3_full_dual_adwin_lw1", "b86f5d679cba136705214f9fe9a5d5460d6bcaa4"),
    "det4_s1_whddma_chddma": (DET3_ROOT, "det3_full_hddm_a_lw1", "b86f5d679cba136705214f9fe9a5d5460d6bcaa4"),
}

FORMAL_SUMMARIES = {
    name: json.loads((OUT / f"formal_{name}_summary.json").read_text())
    for name in ("t1", "t3", "short", "paper", "full", "timing")
}
STAGE_COMMIT = {name: value["commit"] for name, value in FORMAL_SUMMARIES.items()}
SHORT_DATASETS = {
    result["dataset"] for result in FORMAL_SUMMARIES["short"]["results"]
}
PAPER_DATASETS = {
    result["dataset"] for result in FORMAL_SUMMARIES["paper"]["results"]
}
FULL_DATASETS = {
    result["dataset"] for result in FORMAL_SUMMARIES["full"]["results"]
}


def preset_parts(preset: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"det4_(s[01])_w(adwin|hddma|rddm)_c(adwin|hddma|rddm)", preset)
    if not match:
        raise ValueError(preset)
    return match.groups()


def category_of(dataset: str) -> str:
    if dataset.startswith("insects_"):
        return "INSECTS"
    if dataset.startswith("injected_paper_"):
        return "注入 paper"
    if dataset.startswith("injected_"):
        return "注入 CSV"
    if dataset.startswith("synthetic_"):
        return "合成"
    return "真實"


def t1_group(dataset: str) -> str:
    if dataset == "injected_paper_electricity":
        return "injected"
    if dataset == "synthetic_multiclass":
        return "synthetic"
    if dataset in INSECTS:
        return "INSECTS"
    raise ValueError(dataset)


def trial_number(stream: str) -> int | None:
    match = re.search(r"_g(\d+)$", stream)
    return int(match.group(1)) if match else None


def source_for(dataset: str, preset: str, stream: str) -> tuple[Path, str, str, bool]:
    """Return root, physical preset, expected commit and whether the run is reused."""
    if preset in REUSED and dataset in T1_DATASETS:
        root, physical, commit = REUSED[preset]
        candidate = root / dataset / physical / stream / "manifest.json"
        if candidate.exists():
            return root, physical, commit, True
    if dataset == "injected_paper_electricity":
        trial = trial_number(stream)
        if trial is None:
            raise AssertionError(stream)
        commit = STAGE_COMMIT["t1"] if trial < 20 else STAGE_COMMIT["t3"]
    elif dataset in T1_DATASETS:
        commit = STAGE_COMMIT["t1"]
    elif dataset in SHORT_DATASETS:
        commit = STAGE_COMMIT["short"]
    elif dataset in PAPER_DATASETS:
        commit = STAGE_COMMIT["paper"]
    elif dataset in FULL_DATASETS:
        commit = STAGE_COMMIT["full"]
    else:
        raise AssertionError(f"unmapped dataset: {dataset}")
    return DET4_ROOT, preset, commit, False


def expected_sources(dataset: str) -> list[dict]:
    return dataset_sources(REGISTRY[dataset], None)


def cost_fields(manifest: dict) -> dict:
    cost = manifest.get("cost") or {}
    machine = manifest.get("machine") or {}
    return {
        "runtime_s": cost.get("runtime_s", manifest.get("runtime_s")),
        "cpu_time_s": cost.get("cpu_time_s"),
        "instances_per_s": cost.get("instances_per_s"),
        "rss_increment_mb": cost.get("rss_increment_mb"),
        "model_size_final_mb": cost.get("model_size_final_mb"),
        "ram_hours_gb": cost.get("ram_hours_gb"),
        "concurrent_runs": cost.get("concurrent_runs"),
        "machine": machine,
    }


def score_run(
    dataset: str,
    preset: str,
    stream: str,
    source_hashes: dict[Path, str],
) -> dict:
    root, physical_preset, expected_commit, reused = source_for(dataset, preset, stream)
    path = root / dataset / physical_preset / stream
    manifest = json.loads((path / "manifest.json").read_text())
    metrics = json.loads((path / "metrics.json").read_text())
    events = json.loads((path / "warning_events.json").read_text())

    assert manifest["dataset"] == dataset and manifest["stream"] == stream
    assert manifest["preset"] == load_preset(physical_preset)
    assert manifest["git"] == {"commit": expected_commit, "dirty": False}
    assert manifest["registry_entry"] == REGISTRY[dataset]
    assert manifest["max_steps"] is None and manifest["record_warning_events"]
    assert manifest["versions"]["river"] == "0.21.2"
    assert manifest["effective_config"]["model_type"] == "ht"
    framework, warning, confirm = preset_parts(preset)
    assert manifest["effective_config"]["ecpf_learn_during_warning"] == (framework == "s1")
    if not reused:
        names = {"adwin": "adwin", "hddma": "hddm_a", "rddm": "rddm"}
        assert manifest["effective_config"]["ecpf_warning_detector"] == names[warning]
        assert manifest["effective_config"]["ecpf_drift_detector"] == names[confirm]

    source_data = manifest["data"]
    source_path = REPO / source_data.get(
        "file", source_data.get("generator", {}).get("source", "")
    )
    expected_hash = source_data.get("sha256", source_data.get("source_sha256"))
    if source_path not in source_hashes:
        source_hashes[source_path] = sha256(source_path)
    assert source_hashes[source_path] == expected_hash

    opened = sum(event["event"] == "open" for event in events)
    closed = sum(event["event"] in ("close", "censored") for event in events)
    assert opened == closed, path
    confirmed_events = [
        event for event in events
        if event["event"] == "close" and event["reason"] == "confirmed"
    ]
    alarm_key = "input_index" if manifest["coordinates"] == "input" else "index"
    alarms_all = np.array([event[alarm_key] for event in confirmed_events], dtype=int)
    assert int((alarms_all >= manifest["detect_from"]).sum()) == metrics["n_alarms"], path
    assert np.all(alarms_all[:-1] <= alarms_all[1:]) if len(alarms_all) > 1 else True

    n = manifest["n_input"]
    scored_start = max(manifest["detect_from"], manifest["warm_start"])
    gt = [tuple(value) for value in (manifest["gt_intervals"] or [])]
    scored_gt = [(start, end) for start, end in gt if scored_start <= start < n]
    alarms = alarms_all[alarms_all >= scored_start]
    row = {
        "dataset": dataset,
        "stream": stream,
        "preset": preset,
        "framework": framework,
        "warning_detector": warning,
        "confirm_detector": confirm,
        "category": category_of(dataset),
        "types": type_flags(dataset, stream),
        "cell": manifest.get("cell"),
        "n_input": n,
        "n_output": metrics["n_samples"],
        "n_scored": metrics["n_scored"],
        "correct": int(round(metrics["acc_prequential"] * metrics["n_scored"])),
        "acc": metrics["acc_prequential"],
        "post_correct": None,
        "post_count": None,
        "gt": len(scored_gt),
        "alarms": len(alarms),
        "frozen": metrics.get("warning_frozen_steps", 0),
        "warning_counts": collections.Counter(
            f"{event['event']}:{event['reason']}" for event in events
        ),
        "confirmed_delays": [event["buffer_len"] for event in confirmed_events],
        "reused": reused,
        "path": str(path.relative_to(REPO)),
        **cost_fields(manifest),
    }
    assert abs(row["correct"] / row["n_scored"] - row["acc"]) < 1e-12
    if framework == "s1":
        assert row["frozen"] == 0, path

    if not scored_gt:
        assert metrics["tp"] is None and metrics["fp"] is None
        row.update(tp=None, fp=None, fn=None, hits=None, C=None, X=None, O=None, mdt=None)
        return row

    detector = detection_metrics(
        alarms,
        scored_gt,
        n_instances=n,
        delta_max=1000,
        anchor="start",
    )
    registry_delta = REGISTRY[dataset]["delta_max"]
    benchmark = detection_metrics(
        alarms_all[alarms_all >= manifest["detect_from"]],
        gt,
        n_instances=n,
        delta_max=registry_delta,
        anchor="start",
    )
    assert (benchmark["tp"], benchmark["fp"], benchmark["fn"]) == (
        metrics["tp"], metrics["fp"], metrics["fn"]
    ), path
    scoring_windows = windows(gt, n, scored_start)
    outside = n - scored_start - union_length(scoring_windows)
    assert outside > 0, path
    chance = sum(
        -math.expm1(-detector["fp"] / outside * (end - start + 1))
        for start, end in scoring_windows
    )
    hits = detector["n_episodes"] - detector["fn"]
    row.update(
        tp=detector["tp"],
        fp=detector["fp"],
        fn=detector["fn"],
        hits=hits,
        C=chance,
        X=hits - chance,
        O=outside,
        mdt=detector["mdt"],
    )
    return row


def add_post_accuracy(
    rows: list[dict],
    datasets: tuple[str, ...] = T1_DATASETS,
) -> None:
    """Add accuracy in the 1,000 positions after each scored drift.

    ``datasets`` defaults to the preregistered T1 scope so the DET4 verdict is
    unchanged. Post-hoc reports may explicitly request the wider completed-run
    scope while continuing to use this audited implementation.
    """
    selected = [
        row for row in rows
        if row["dataset"] in datasets and row["gt"]
    ]
    source_maps: dict[str, dict[str, dict]] = {}
    mask_cache: dict[tuple[str, str], np.ndarray] = {}
    for index, row in enumerate(selected, 1):
        dataset, stream = row["dataset"], row["stream"]
        path = REPO / row["path"]
        manifest = json.loads((path / "manifest.json").read_text())
        key = (dataset, stream)
        if key not in mask_cache:
            with np.load(path / "preds.npz") as record:
                length = len(record["y_true"])
            positions = np.arange(length)
            if manifest["coordinates"] == "input":
                if dataset not in source_maps:
                    source_maps[dataset] = {
                        source["stem"]: source for source in expected_sources(dataset)
                    }
                source = load_stream(source_maps[dataset][stream], REGISTRY[dataset])
                positions = source["kept"]
                assert len(positions) == length
            mask = np.zeros(length, dtype=bool)
            threshold = max(manifest["warm_start"], manifest["detect_from"])
            for start, _ in manifest["gt_intervals"]:
                if start < threshold:
                    continue
                mask |= (positions >= start) & (positions <= start + 999)
            mask_cache[key] = mask
        with np.load(path / "preds.npz") as record:
            true = record["y_true"]
            pred = record["y_pred"]
            mask = mask_cache[key] & np.isfinite(pred)
            row["post_correct"] = int(np.count_nonzero(true[mask] == pred[mask]))
            row["post_count"] = int(mask.sum())
        if index % 1000 == 0:
            print(f"post-accuracy {index}/{len(selected)}", flush=True)


def load_all(
    post_datasets: tuple[str, ...] = T1_DATASETS,
) -> list[dict]:
    rows: list[dict] = []
    source_hashes: dict[Path, str] = {}
    for dataset in NON_REGRESSION:
        streams = [source["stem"] for source in expected_sources(dataset)]
        assert len(streams) == len(set(streams))
        for preset in PRESETS:
            for stream in streams:
                rows.append(score_run(dataset, preset, stream, source_hashes))
        dataset_rows = [row for row in rows if row["dataset"] == dataset]
        assert len(dataset_rows) == len(streams) * len(PRESETS)
        for stream in streams:
            paired = [row for row in dataset_rows if row["stream"] == stream]
            assert len(paired) == 18
            assert len({(row["n_input"], row["n_output"], row["n_scored"], row["gt"]) for row in paired}) == 1
        print(f"audited {dataset}: {len(dataset_rows)} logical runs", flush=True)
    expected = sum(len(expected_sources(dataset)) * 18 for dataset in NON_REGRESSION)
    assert expected == 30_456
    assert len(rows) == expected
    assert sum(row["reused"] for row in rows) == 1_025
    assert len(rows) - sum(row["reused"] for row in rows) == 29_431
    add_post_accuracy(rows, post_datasets)
    return rows


def aggregate(items: list[dict]) -> dict:
    valid = [row for row in items if row["gt"]]
    post = [row for row in valid if row["post_count"] is not None]
    n_scored = sum(row["n_scored"] for row in items)
    post_n = sum(row["post_count"] for row in post)
    hits = sum(row["hits"] for row in valid)
    return {
        "runs": len(items),
        "streams": len({(row["dataset"], row["stream"]) for row in items}),
        "gt_streams": len(valid),
        "gt": sum(row["gt"] for row in valid),
        "acc": sum(row["correct"] for row in items) / n_scored if n_scored else None,
        "post_acc": sum(row["post_correct"] for row in post) / post_n if post_n else None,
        "alarms": sum(row["alarms"] for row in items),
        "tp": sum(row["tp"] for row in valid),
        "fp": sum(row["fp"] for row in valid),
        "fn": sum(row["fn"] for row in valid),
        "hits": hits,
        "C": sum(row["C"] for row in valid),
        "X": sum(row["X"] for row in valid),
        "mdt": (
            sum(row["mdt"] * row["hits"] for row in valid if row["mdt"] is not None) / hits
            if hits else None
        ),
        "frozen": sum(row["frozen"] for row in items),
    }


def paired_delta(
    lookup: dict[tuple[str, str, str], dict],
    arm: str,
    base: str,
    keys: set[tuple[str, str]],
    metric: str,
    stratify: bool = True,
) -> dict:
    keys = sorted(keys)
    if metric in ("fp", "X", "post_acc"):
        keys = [key for key in keys if lookup[(*key, arm)]["gt"]]
    if metric == "post_acc":
        keys = [key for key in keys if lookup[(*key, arm)]["post_count"] is not None]
    if not keys:
        return {"point": None, "ci": None, "n": 0}

    if stratify:
        groups = {
            group: [key for key in keys if t1_group(key[0]) == group]
            for group in ("injected", "synthetic", "INSECTS")
        }
    else:
        groups = {"all": keys}
    rng = np.random.default_rng(SEED)
    if metric in ("fp", "X"):
        point = 0.0
        samples = np.zeros(N_BOOT)
        for subset in groups.values():
            if not subset:
                continue
            diff = np.array(
                [lookup[(*key, arm)][metric] - lookup[(*key, base)][metric] for key in subset],
                dtype=float,
            )
            point += diff.sum()
            idx = rng.integers(0, len(diff), size=(N_BOOT, len(diff)))
            samples += diff[idx].sum(axis=1)
    else:
        numerator = "correct" if metric == "acc" else "post_correct"
        denominator = "n_scored" if metric == "acc" else "post_count"
        total = np.zeros(4)
        sampled = np.zeros((N_BOOT, 4))
        for subset in groups.values():
            if not subset:
                continue
            values = np.array(
                [
                    [
                        lookup[(*key, arm)][numerator],
                        lookup[(*key, arm)][denominator],
                        lookup[(*key, base)][numerator],
                        lookup[(*key, base)][denominator],
                    ]
                    for key in subset
                ],
                dtype=float,
            )
            total += values.sum(axis=0)
            idx = rng.integers(0, len(values), size=(N_BOOT, len(values)))
            sampled += values[idx].sum(axis=1)
        assert total[1] > 0 and total[3] > 0
        point = total[0] / total[1] - total[2] / total[3]
        samples = sampled[:, 0] / sampled[:, 1] - sampled[:, 2] / sampled[:, 3]
    ci = None if len(keys) == 1 else [float(value) for value in np.percentile(samples, [2.5, 97.5])]
    return {"point": float(point), "ci": ci, "n": len(keys)}


def detection_verdict(fp_ci: list[float] | None, x_ci: list[float] | None) -> str:
    if fp_ci is None or x_ci is None:
        return "不可判定"
    if fp_ci[1] < 0 and x_ci[0] > 0:
        return "優於"
    if fp_ci[0] > 0 and x_ci[1] < 0:
        return "不如"
    return "持平"


def accuracy_verdict(ci: list[float] | None) -> str:
    if ci is None:
        return "不可判定"
    if ci[0] > 0:
        return "優於"
    if ci[1] < 0:
        return "不如"
    return "持平"


def comparison(
    lookup: dict[tuple[str, str, str], dict],
    arm: str,
    base: str,
    keys: set[tuple[str, str]],
    stratify: bool = True,
) -> dict:
    result = {
        metric: paired_delta(lookup, arm, base, keys, metric, stratify)
        for metric in ("acc", "post_acc", "fp", "X")
    }
    fp_ci, x_ci, acc_ci = result["fp"]["ci"], result["X"]["ci"], result["acc"]["ci"]
    result.update(
        detection=detection_verdict(fp_ci, x_ci),
        accuracy=accuracy_verdict(acc_ci),
    )
    return result


def t1_t3(rows: list[dict]) -> dict:
    lookup = {(row["dataset"], row["stream"], row["preset"]): row for row in rows}
    t1_keys = {
        (row["dataset"], row["stream"])
        for row in rows
        if row["dataset"] in T1_DATASETS
        and not (row["dataset"] == "injected_paper_electricity" and trial_number(row["stream"]) >= 20)
    }
    t3_keys = {
        (row["dataset"], row["stream"])
        for row in rows
        if row["dataset"] == "injected_paper_electricity" and trial_number(row["stream"]) >= 20
    }
    assert len(t1_keys) == T1_STREAMS and len(t3_keys) == T3_STREAMS
    t1_aggregates = {
        preset: aggregate([lookup[(*key, preset)] for key in sorted(t1_keys)])
        for preset in PRESETS
    }
    t3_aggregates = {
        preset: aggregate([lookup[(*key, preset)] for key in sorted(t3_keys)])
        for preset in PRESETS
    }

    diagonal = {framework: f"det4_{framework}_whddma_chddma" for framework in FRAMEWORKS}
    vs_diagonal = {
        framework: {
            preset: comparison(lookup, preset, diagonal[framework], t1_keys)
            for preset in PRESETS if preset.startswith(f"det4_{framework}_")
        }
        for framework in FRAMEWORKS
    }
    pairs = (("adwin", "hddma"), ("adwin", "rddm"), ("hddma", "rddm"))
    warning_effects: dict[str, dict] = {}
    confirm_effects: dict[str, dict] = {}
    for framework in FRAMEWORKS:
        warning_effects[framework] = {}
        confirm_effects[framework] = {}
        for confirm in DETECTORS:
            warning_effects[framework][confirm] = {}
            for left, right in pairs:
                left_arm = f"det4_{framework}_w{left}_c{confirm}"
                right_arm = f"det4_{framework}_w{right}_c{confirm}"
                warning_effects[framework][confirm][f"{left}-{right}"] = comparison(
                    lookup, left_arm, right_arm, t1_keys
                )
        for warning in DETECTORS:
            confirm_effects[framework][warning] = {}
            for left, right in pairs:
                left_arm = f"det4_{framework}_w{warning}_c{left}"
                right_arm = f"det4_{framework}_w{warning}_c{right}"
                confirm_effects[framework][warning][f"{left}-{right}"] = comparison(
                    lookup, left_arm, right_arm, t1_keys
                )

    def axis_range(framework: str, metric: str, axis: str) -> float:
        ranges = []
        if axis == "warning":
            for confirm in DETECTORS:
                values = [
                    t1_aggregates[f"det4_{framework}_w{warning}_c{confirm}"][metric]
                    for warning in DETECTORS
                ]
                ranges.append(max(values) - min(values))
        else:
            for warning in DETECTORS:
                values = [
                    t1_aggregates[f"det4_{framework}_w{warning}_c{confirm}"][metric]
                    for confirm in DETECTORS
                ]
                ranges.append(max(values) - min(values))
        return statistics.mean(ranges)

    h1_checks = []
    for confirm in DETECTORS:
        adwin = t1_aggregates[f"det4_s0_wadwin_c{confirm}"]
        others = [
            t1_aggregates[f"det4_s0_w{warning}_c{confirm}"]
            for warning in ("hddma", "rddm")
        ]
        h1_checks.append({
            "confirm": confirm,
            "adwin_frozen_most": adwin["frozen"] >= max(value["frozen"] for value in others),
            "adwin_accuracy_lowest": adwin["acc"] <= min(value["acc"] for value in others),
        })
    h1_axis = {
        "warning_accuracy_range": axis_range("s0", "acc", "warning"),
        "confirm_accuracy_range": axis_range("s0", "acc", "confirm"),
    }
    h1_holds = (
        h1_axis["warning_accuracy_range"] > h1_axis["confirm_accuracy_range"]
        and all(check["adwin_frozen_most"] and check["adwin_accuracy_lowest"] for check in h1_checks)
    )

    h2_checks = []
    for warning in DETECTORS:
        adwin = t1_aggregates[f"det4_s1_w{warning}_cadwin"]
        others = [
            t1_aggregates[f"det4_s1_w{warning}_c{confirm}"]
            for confirm in ("hddma", "rddm")
        ]
        h2_checks.append({
            "warning": warning,
            "adwin_X_lowest": adwin["X"] <= min(value["X"] for value in others),
            "adwin_post_accuracy_lowest": adwin["post_acc"] <= min(value["post_acc"] for value in others),
        })
    h2_axis = {
        "warning_X_range": axis_range("s1", "X", "warning"),
        "confirm_X_range": axis_range("s1", "X", "confirm"),
        "warning_post_accuracy_range": axis_range("s1", "post_acc", "warning"),
        "confirm_post_accuracy_range": axis_range("s1", "post_acc", "confirm"),
    }
    h2_holds = (
        h2_axis["confirm_X_range"] > h2_axis["warning_X_range"]
        and h2_axis["confirm_post_accuracy_range"] > h2_axis["warning_post_accuracy_range"]
        and all(check["adwin_X_lowest"] and check["adwin_post_accuracy_lowest"] for check in h2_checks)
    )

    candidate = "det4_s1_wadwin_chddma"
    base = diagonal["s1"]
    h3_t1 = comparison(lookup, candidate, base, t1_keys)
    h3_t3 = comparison(lookup, candidate, base, t3_keys, stratify=False)
    h3_holds = all(
        value[axis] not in ("不如", "不可判定")
        for value in (h3_t1, h3_t3)
        for axis in ("detection", "accuracy")
    )

    strata = {"groups": {}, "types": {}}
    for group in ("injected", "synthetic", "INSECTS"):
        keys = {key for key in t1_keys if t1_group(key[0]) == group}
        strata["groups"][group] = {
            framework: {
                preset: comparison(lookup, preset, diagonal[framework], keys, stratify=False)
                for preset in PRESETS if preset.startswith(f"det4_{framework}_")
            }
            for framework in FRAMEWORKS
        }
    for drift_type in ("突變", "漸變", "incremental", "recurring"):
        keys = {
            key for key in t1_keys
            if drift_type in lookup[(*key, "det4_s0_whddma_chddma")]["types"]
        }
        strata["types"][drift_type] = {
            framework: {
                preset: comparison(lookup, preset, diagonal[framework], keys, stratify=False)
                for preset in PRESETS if preset.startswith(f"det4_{framework}_")
            }
            for framework in FRAMEWORKS
        }
    return {
        "t1_keys": len(t1_keys),
        "t3_keys": len(t3_keys),
        "t1_aggregates": t1_aggregates,
        "t3_aggregates": t3_aggregates,
        "warning_effects": warning_effects,
        "confirm_effects": confirm_effects,
        "vs_diagonal": vs_diagonal,
        "h1": {"holds": h1_holds, "checks": h1_checks, "axis": h1_axis},
        "h2": {"holds": h2_holds, "checks": h2_checks, "axis": h2_axis},
        "h3": {"holds": h3_holds, "candidate": candidate, "base": base, "t1": h3_t1, "t3": h3_t3},
        "strata": strata,
    }


def q4(rows: list[dict]) -> dict:
    lookup = {(row["dataset"], row["stream"], row["preset"]): row for row in rows}
    results: dict[str, dict] = {framework: {} for framework in FRAMEWORKS}
    for framework in FRAMEWORKS:
        base = f"det4_{framework}_whddma_chddma"
        for dataset in NON_REGRESSION:
            keys = {
                (row["dataset"], row["stream"])
                for row in rows if row["dataset"] == dataset
            }
            results[framework][dataset] = {}
            for preset in PRESETS:
                if not preset.startswith(f"det4_{framework}_"):
                    continue
                results[framework][dataset][preset] = comparison(
                    lookup, preset, base, keys, stratify=False
                )

    summaries: dict[str, dict] = {framework: {} for framework in FRAMEWORKS}
    categories: dict[str, dict] = {framework: {} for framework in FRAMEWORKS}
    for framework in FRAMEWORKS:
        for preset in PRESETS:
            if not preset.startswith(f"det4_{framework}_"):
                continue
            acc = [results[framework][dataset][preset]["acc"] for dataset in NON_REGRESSION]
            x = [value for dataset in NON_REGRESSION if (value := results[framework][dataset][preset]["X"])["point"] is not None]
            worst_acc_dataset = min(
                NON_REGRESSION,
                key=lambda dataset: results[framework][dataset][preset]["acc"]["point"],
            )
            x_datasets = [
                dataset for dataset in NON_REGRESSION
                if results[framework][dataset][preset]["X"]["point"] is not None
            ]
            worst_x_dataset = min(
                x_datasets,
                key=lambda dataset: results[framework][dataset][preset]["X"]["point"],
            )
            summaries[framework][preset] = {
                "accuracy_median": statistics.median(value["point"] for value in acc),
                "accuracy_worst_dataset": worst_acc_dataset,
                "accuracy_worst": results[framework][worst_acc_dataset][preset]["acc"]["point"],
                "accuracy_negative_ci_datasets": sum(
                    value["ci"] is not None and value["ci"][1] < 0 for value in acc
                ),
                "X_median": statistics.median(value["point"] for value in x),
                "X_worst_dataset": worst_x_dataset,
                "X_worst": results[framework][worst_x_dataset][preset]["X"]["point"],
                "X_negative_ci_datasets": sum(
                    value["ci"] is not None and value["ci"][1] < 0 for value in x
                ),
                "datasets": len(acc),
                "gt_datasets": len(x),
            }
        for category in ("真實", "INSECTS", "注入 CSV", "注入 paper", "合成"):
            category_datasets = [dataset for dataset in NON_REGRESSION if category_of(dataset) == category]
            categories[framework][category] = {}
            for preset in PRESETS:
                if not preset.startswith(f"det4_{framework}_"):
                    continue
                acc_points = [results[framework][dataset][preset]["acc"]["point"] for dataset in category_datasets]
                x_points = [
                    results[framework][dataset][preset]["X"]["point"]
                    for dataset in category_datasets
                    if results[framework][dataset][preset]["X"]["point"] is not None
                ]
                categories[framework][category][preset] = {
                    "datasets": len(acc_points),
                    "accuracy_median": statistics.median(acc_points),
                    "gt_datasets": len(x_points),
                    "X_median": statistics.median(x_points) if x_points else None,
                }
    return {"datasets": results, "summary": summaries, "categories": categories}


def mechanisms(rows: list[dict]) -> dict:
    result = {}
    for preset in PRESETS:
        selected = [row for row in rows if row["preset"] == preset]
        counts = collections.Counter()
        delays = []
        for row in selected:
            counts.update(row["warning_counts"])
            delays.extend(row["confirmed_delays"])
        opened = sum(value for key, value in counts.items() if key.startswith("open:"))
        closed = sum(value for key, value in counts.items() if key.startswith(("close:", "censored:")))
        assert opened == closed
        result[preset] = {
            "runs": len(selected),
            "opened": opened,
            "confirmed": counts["close:confirmed"],
            "zone_exit": counts["close:zone_exit"],
            "timeout": counts["close:timeout"],
            "reference_switch": counts["close:reference_switch"],
            "censored": sum(value for key, value in counts.items() if key.startswith("censored:")),
            "other_close": {
                key: value for key, value in counts.items()
                if key.startswith("close:") and key not in {
                    "close:confirmed", "close:zone_exit", "close:timeout", "close:reference_switch"
                }
            },
            "self_close_ratio": counts["close:zone_exit"] / opened if opened else None,
            "mean_confirmation_delay": statistics.mean(delays) if delays else None,
            "frozen_steps": sum(row["frozen"] for row in selected),
        }
    return result


def costs(rows: list[dict]) -> dict:
    parallel = {}
    for preset in PRESETS:
        selected = [row for row in rows if row["preset"] == preset]
        with_cost = [row for row in selected if row["cpu_time_s"] is not None]
        assert with_cost
        parallel[preset] = {
            "runs": len(selected),
            "runs_with_cost": len(with_cost),
            "runs_without_cost": len(selected) - len(with_cost),
            "runtime_mean_s": statistics.mean(row["runtime_s"] for row in with_cost),
            "cpu_time_sum_s": sum(row["cpu_time_s"] for row in with_cost),
            "rss_increment_max_mb": max(row["rss_increment_mb"] for row in with_cost),
            "model_size_mean_mb": statistics.mean(row["model_size_final_mb"] for row in with_cost),
            "ram_hours_sum_gb": sum(row["ram_hours_gb"] for row in with_cost),
            "concurrent_runs": sorted({row["concurrent_runs"] for row in with_cost}),
        }
    strict = {}
    for preset in PRESETS:
        path = TIMING_ROOT / "electricity" / preset / "runs.csv"
        frame = pd.read_csv(path)
        assert len(frame) == 1 and int(frame.iloc[0]["concurrent_runs"]) == 1
        row = frame.iloc[0]
        strict[preset] = {
            "runtime_s": float(row["runtime_s"]),
            "cpu_time_s": float(row["cpu_time_s"]),
            "instances_per_s": float(row["instances_per_s"]),
            "rss_increment_mb": float(row["rss_increment_mb"]),
            "model_size_final_mb": float(row["model_size_final_mb"]),
            "ram_hours_gb": float(row["ram_hours_gb"]),
            "concurrent_runs": int(row["concurrent_runs"]),
            "machine": str(row["machine"]),
        }
    return {"parallel": parallel, "strict_electricity": strict}


def summarize(rows: list[dict]) -> dict:
    for summary in FORMAL_SUMMARIES.values():
        assert summary["failed_runs"] == 0 and not summary["errors"] and not summary["skipped"]
    return {
        "metadata": {
            "logical_runs": len(rows),
            "new_runs": sum(not row["reused"] for row in rows),
            "reused_runs": sum(row["reused"] for row in rows),
            "datasets": len(NON_REGRESSION),
            "presets": len(PRESETS),
            "n_boot": N_BOOT,
            "seed": SEED,
            "river": "0.21.2",
            "stage_commits": STAGE_COMMIT,
            "formal_elapsed_s": sum(
                FORMAL_SUMMARIES[name]["elapsed_s"] for name in ("t1", "t3", "short", "paper", "full")
            ),
            "strict_timing_elapsed_s": FORMAL_SUMMARIES["timing"]["elapsed_s"],
        },
        "t1_t3": t1_t3(rows),
        "q4": q4(rows),
        "mechanisms": mechanisms(rows),
        "costs": costs(rows),
    }


def main() -> None:
    rows = load_all()
    summary = summarize(rows)
    path = OUT / "det4_verdict_data.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(
        "audited",
        summary["metadata"]["logical_runs"],
        "logical runs; H1",
        summary["t1_t3"]["h1"]["holds"],
        "H2",
        summary["t1_t3"]["h2"]["holds"],
        "H3",
        summary["t1_t3"]["h3"]["holds"],
    )
    print("summary ->", path)


if __name__ == "__main__":
    main()
