#!/usr/bin/env python3
"""Export DET4 run scores and the post-hoc subset-level summaries.

This script only reads completed DET1/DET3/DET4 artifacts. It never invokes the
benchmark runner. DET-series detection fields are delegated to
``scripts.analyze_det4_formal``; pooled skill detection fields are delegated to
``src.metrics.evaluate_run.pool_detection_runs``.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Iterable

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import analyze_det4_formal as det4  # noqa: E402
from scripts.render_det4_verdict import markdown_to_html  # noqa: E402
from src.metrics.evaluate_run import pool_detection_runs  # noqa: E402


OUT = REPO / "outputs" / "det4"
RUN_SCORES = OUT / "det4_run_scores.csv"
SUBSET_SUMMARY = OUT / "det4_subset_summary.csv"
DETECTION_POOLED = OUT / "det4_subset_detection_pooled.csv"
REPORT_MD = OUT / "det4_subset_report.md"
REPORT_HTML = OUT / "det4_subset_report.html"
FRAMEWORK_LABELS = {"s0": "論文ECPF", "s1": "完整系統"}
DETECTOR_LABELS = {"adwin": "ADWIN", "hddma": "HDDM-A", "rddm": "RDDM"}
COST_FIELDS = (
    "runtime_s",
    "cpu_time_s",
    "instances_per_s",
    "rss_increment_mb",
    "model_size_final_mb",
    "ram_hours_gb",
    "concurrent_runs",
)
RUN_SCORE_FIELDS = (
    "dataset", "subset", "stream", "cell", "subtype", "trial_or_seed",
    "framework", "warning", "confirm", "preset", "source", "status",
    "missing_reason", "path", "n_scored", "correct", "acc_prequential",
    "acc_window1000_mean", "kappa", "kappa_t", "kappa_m", "macro_f1",
    "baseline_no_change_acc", "baseline_majority_acc", "gt", "alarms", "tp",
    "fp", "fn", "hits", "C", "X", "O", "post_correct", "post_count", "mdt",
    "precision", "recall", "f1", "episode_recall", "far", "ar",
    "frozen_steps", "warning_opened", "warning_self_closed", "warning_timeout",
    "confirmations", *COST_FIELDS,
)
DELTA_METRICS = ("acc", "post_acc", "fp", "X")
SYNTHETIC_SUBTYPES = (
    "recurring_sudden",
    "recurring_gradual",
    "recurring_incremental",
    "sudden",
    "gradual",
    "incremental",
)


def optional(value: Any) -> Any:
    """Convert numpy scalars and NaN to CSV/JSON-safe Python values."""
    if isinstance(value, np.generic):
        value = value.item()
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def synthetic_subtype(stream: str) -> str:
    for subtype in SYNTHETIC_SUBTYPES:
        if stream.startswith(f"{subtype}_"):
            return subtype
    raise ValueError(f"Cannot parse synthetic subtype: {stream}")


def subset_for(dataset: str, stream: str, cell: str | None) -> tuple[str, str | None]:
    if dataset.startswith("injected_"):
        if not cell:
            raise ValueError(f"Missing injection cell for {dataset}/{stream}")
        return f"{dataset}/{cell}", None
    if dataset.startswith("synthetic_"):
        subtype = synthetic_subtype(stream)
        return f"{dataset}/{subtype}", subtype
    return dataset, None


def trial_or_seed(stream: str) -> int | None:
    match = re.search(r"_g(\d+)$", stream)
    return int(match.group(1)) if match else None


def source_label(row: dict[str, Any]) -> str:
    if not row.get("reused"):
        return "det4_new"
    path = str(row.get("path", ""))
    return "reused_det1" if "/det1/" in f"/{path}" else "reused_det3"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def score_rows() -> list[dict[str, Any]]:
    """Audit every logical run through the existing DET4 scorer and enrich it."""
    base_rows = det4.load_all(post_datasets=det4.NON_REGRESSION)
    result: list[dict[str, Any]] = []
    for base in base_rows:
        run_path = REPO / base["path"]
        metrics = load_json(run_path / "metrics.json")
        manifest = load_json(run_path / "manifest.json")
        subset, subtype = subset_for(base["dataset"], base["stream"], base.get("cell"))
        warning_counts = base["warning_counts"]
        row = {
            "dataset": base["dataset"],
            "subset": subset,
            "stream": base["stream"],
            "cell": base.get("cell"),
            "subtype": subtype,
            "trial_or_seed": trial_or_seed(base["stream"]),
            "framework": FRAMEWORK_LABELS[base["framework"]],
            "warning": DETECTOR_LABELS[base["warning_detector"]],
            "confirm": DETECTOR_LABELS[base["confirm_detector"]],
            "preset": base["preset"],
            "source": source_label(base),
            "status": "ok",
            "missing_reason": None,
            "path": base["path"],
            "n_scored": base["n_scored"],
            "correct": base["correct"],
            "acc_prequential": metrics.get("acc_prequential"),
            "acc_window1000_mean": metrics.get("acc_window1000_mean"),
            "kappa": metrics.get("kappa"),
            "kappa_t": metrics.get("kappa_t"),
            "kappa_m": metrics.get("kappa_m"),
            "macro_f1": metrics.get("macro_f1"),
            "baseline_no_change_acc": metrics.get("baseline_no_change_acc"),
            "baseline_majority_acc": metrics.get("baseline_majority_acc"),
            "gt": base["gt"],
            "alarms": base["alarms"],
            "tp": base["tp"],
            "fp": base["fp"],
            "fn": base["fn"],
            "hits": base["hits"],
            "C": base["C"],
            "X": base["X"],
            "O": base["O"],
            "post_correct": base["post_correct"],
            "post_count": base["post_count"],
            "mdt": base["mdt"],
            "precision": metrics.get("precision"),
            "recall": metrics.get("recall"),
            "f1": metrics.get("f1"),
            "episode_recall": metrics.get("episode_recall"),
            "far": metrics.get("far"),
            "ar": metrics.get("ar"),
            "frozen_steps": base["frozen"],
            "warning_opened": sum(v for k, v in warning_counts.items() if k.startswith("open:")),
            "warning_self_closed": warning_counts["close:zone_exit"],
            "warning_timeout": warning_counts["close:timeout"],
            "confirmations": warning_counts["close:confirmed"],
            **{field: base.get(field) for field in COST_FIELDS},
            # Private fields support downstream aggregation and are never exported.
            "_framework": base["framework"],
            "_warning": base["warning_detector"],
            "_confirm": base["confirm_detector"],
            "_acc": base["acc"],
            "_metrics": metrics,
            "_manifest": manifest,
            "_types": base["types"],
        }
        result.append(row)
    return result


def write_csv(path: Path, fields: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: optional(row.get(field)) for field in writer.fieldnames} for row in rows)


def write_run_scores(rows: list[dict[str, Any]]) -> Path:
    write_csv(RUN_SCORES, RUN_SCORE_FIELDS, rows)
    if RUN_SCORES.stat().st_size <= 50 * 1024 * 1024:
        return RUN_SCORES
    target = RUN_SCORES.with_suffix(".csv.gz")
    with RUN_SCORES.open("rb") as source, target.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as output:
            shutil.copyfileobj(source, output)
    RUN_SCORES.unlink()
    return target


def run_score_path() -> Path:
    return RUN_SCORES if RUN_SCORES.exists() else RUN_SCORES.with_suffix(".csv.gz")


def aggregate_input(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "dataset": row["dataset"],
        "stream": row["stream"],
        "preset": row["preset"],
        "n_scored": int(row["n_scored"]),
        "correct": int(row["correct"]),
        "acc": float(row["acc_prequential"]),
        "post_correct": optional(row["post_correct"]),
        "post_count": optional(row["post_count"]),
        "gt": int(row["gt"]),
        "alarms": int(row["alarms"]),
        "tp": optional(row["tp"]),
        "fp": optional(row["fp"]),
        "fn": optional(row["fn"]),
        "hits": optional(row["hits"]),
        "C": optional(row["C"]),
        "X": optional(row["X"]),
        "mdt": optional(row["mdt"]),
        "frozen": int(row["frozen_steps"]),
    }


def read_aggregate_rows() -> list[dict[str, Any]]:
    frame = pd.read_csv(run_score_path(), compression="infer", low_memory=False)
    frame = frame.loc[frame["status"] == "ok"]
    return [aggregate_input({key: optional(value) for key, value in record.items()})
            for record in frame.to_dict(orient="records")]


def assert_close(actual: Any, expected: Any, label: str, tolerance: float = 1e-9) -> None:
    if actual is None or expected is None:
        if actual is not None or expected is not None:
            raise AssertionError(f"{label}: {actual!r} != {expected!r}")
        return
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        if abs(float(actual) - float(expected)) >= tolerance:
            raise AssertionError(f"{label}: {actual!r} != {expected!r}")
        return
    if actual != expected:
        raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def validate_reproduction() -> dict[str, Any]:
    """Rebuild dataset/T1/T3 aggregates from the exported CSV."""
    rows = read_aggregate_rows()
    verdict = load_json(OUT / "det4_verdict_data.json")
    lookup = {(row["dataset"], row["stream"], row["preset"]): row for row in rows}
    q4_checks = 0
    q4_numeric_checks = 0
    for framework in det4.FRAMEWORKS:
        base = f"det4_{framework}_whddma_chddma"
        for dataset in det4.NON_REGRESSION:
            keys = sorted({(row["dataset"], row["stream"]) for row in rows
                           if row["dataset"] == dataset})
            has_gt = any(lookup[(*key, base)]["gt"] for key in keys)
            for preset in det4.PRESETS:
                if not preset.startswith(f"det4_{framework}_"):
                    continue
                arm_agg = det4.aggregate([lookup[(*key, preset)] for key in keys])
                base_agg = det4.aggregate([lookup[(*key, base)] for key in keys])
                points = {
                    "acc": arm_agg["acc"] - base_agg["acc"],
                    # The saved q4 used the preregistered T1 post-drift scope.
                    "post_acc": (
                        arm_agg["post_acc"] - base_agg["post_acc"]
                        if dataset in det4.T1_DATASETS
                        and arm_agg["post_acc"] is not None
                        and base_agg["post_acc"] is not None
                        else None
                    ),
                    "fp": arm_agg["fp"] - base_agg["fp"] if has_gt else None,
                    "X": arm_agg["X"] - base_agg["X"] if has_gt else None,
                }
                saved = verdict["q4"]["datasets"][framework][dataset][preset]
                for metric, point in points.items():
                    assert_close(point, saved[metric]["point"],
                                 f"q4.{framework}.{dataset}.{preset}.{metric}")
                    q4_checks += 1
                    q4_numeric_checks += saved[metric]["point"] is not None

    t1_keys = {
        (row["dataset"], row["stream"])
        for row in rows
        if row["dataset"] in det4.T1_DATASETS
        and not (row["dataset"] == "injected_paper_electricity"
                 and det4.trial_number(row["stream"]) >= 20)
    }
    t3_keys = {
        (row["dataset"], row["stream"])
        for row in rows
        if row["dataset"] == "injected_paper_electricity"
        and det4.trial_number(row["stream"]) >= 20
    }
    aggregate_checks = 0
    for name, keys in (("t1_aggregates", t1_keys), ("t3_aggregates", t3_keys)):
        for preset in det4.PRESETS:
            actual = det4.aggregate([lookup[(*key, preset)] for key in sorted(keys)])
            expected = verdict["t1_t3"][name][preset]
            for field, value in expected.items():
                assert_close(actual[field], value, f"{name}.{preset}.{field}")
                aggregate_checks += 1
    return {
        "passed": True,
        "tolerance": 1e-9,
        "q4_field_checks": q4_checks,
        "q4_point_checks": q4_numeric_checks,
        "t1_t3_aggregate_checks": aggregate_checks,
    }


def weighted_mean(rows: list[dict[str, Any]], field: str, weight: str = "n_scored") -> float | None:
    selected = [(row.get(field), row.get(weight)) for row in rows
                if row.get(field) is not None and row.get(weight)]
    denominator = sum(float(w) for _, w in selected)
    return sum(float(v) * float(w) for v, w in selected) / denominator if denominator else None


def median(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    return statistics.median(values) if values else None


def delta_columns(prefix: str, comparison: dict[str, Any], n_streams: int) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for metric in DELTA_METRICS:
        result = comparison[metric]
        ci = result["ci"] if n_streams >= 5 else None
        output[f"{prefix}_{metric}"] = result["point"]
        output[f"{prefix}_{metric}_ci_low"] = ci[0] if ci is not None else None
        output[f"{prefix}_{metric}_ci_high"] = ci[1] if ci is not None else None
    return output


def build_subset_outputs(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_rows = [aggregate_input(row) for row in rows if row["status"] == "ok"]
    lookup = {(row["dataset"], row["stream"], row["preset"]): row for row in base_rows}
    row_lookup = {(row["dataset"], row["stream"], row["preset"]): row for row in rows}
    subset_keys = sorted({(row["dataset"], row["subset"]) for row in rows})
    summary_rows: list[dict[str, Any]] = []
    pooled_rows: list[dict[str, Any]] = []
    for dataset, subset in subset_keys:
        streams = sorted({row["stream"] for row in rows
                          if row["dataset"] == dataset and row["subset"] == subset})
        keys = {(dataset, stream) for stream in streams}
        n_streams = len(streams)
        for preset in det4.PRESETS:
            selected = [row_lookup[(*key, preset)] for key in sorted(keys)]
            selected_base = [lookup[(*key, preset)] for key in sorted(keys)]
            aggregate = det4.aggregate(selected_base)
            framework, warning, confirm = det4.preset_parts(preset)
            diagonal = f"det4_{framework}_whddma_chddma"
            paired_framework = f"det4_{'s1' if framework == 's0' else 's0'}_w{warning}_c{confirm}"
            vs_diagonal = det4.comparison(lookup, preset, diagonal, keys, stratify=False)
            full_minus_paper = det4.comparison(
                lookup,
                f"det4_s1_w{warning}_c{confirm}",
                f"det4_s0_w{warning}_c{confirm}",
                keys,
                stratify=False,
            )
            has_gt = any(row["gt"] for row in selected_base)
            output = {
                "dataset": dataset,
                "subset": subset,
                "n_streams": n_streams,
                "framework": FRAMEWORK_LABELS[framework],
                "warning": DETECTOR_LABELS[warning],
                "confirm": DETECTOR_LABELS[confirm],
                "preset": preset,
                "accuracy": aggregate["acc"],
                "post_drift_1000_accuracy": aggregate["post_acc"],
                "fp1000_total": aggregate["fp"] if has_gt else None,
                "X_total": aggregate["X"] if has_gt else None,
                "mean_delay": aggregate["mdt"] if has_gt else None,
                "frozen_steps": aggregate["frozen"],
                "baseline_no_change_acc": weighted_mean(selected, "baseline_no_change_acc"),
                "baseline_majority_acc": weighted_mean(selected, "baseline_majority_acc"),
                **{f"{field}_median": median(selected, field) for field in COST_FIELDS},
                **delta_columns("delta_vs_hddma", vs_diagonal, n_streams),
                **delta_columns("delta_full_minus_paper", full_minus_paper, n_streams),
                "ci_note": "串流少於 5 條" if n_streams < 5 else "",
                "paired_framework_preset": paired_framework,
            }
            summary_rows.append(output)

            metric_rows = [row["_metrics"] for row in selected if row["_metrics"].get("n_gt")]
            if metric_rows:
                pooled = pool_detection_runs(metric_rows)
                pooled_rows.append({
                    "dataset": dataset,
                    "subset": subset,
                    "n_streams": n_streams,
                    "framework": FRAMEWORK_LABELS[framework],
                    "warning": DETECTOR_LABELS[warning],
                    "confirm": DETECTOR_LABELS[confirm],
                    "preset": preset,
                    "n_runs": pooled.get("n_runs"),
                    "n_episodes": pooled.get("n_episodes"),
                    "tp": pooled.get("tp"),
                    "fp": pooled.get("fp"),
                    "fn": pooled.get("fn"),
                    "precision": pooled.get("precision"),
                    "recall": pooled.get("recall"),
                    "f1": pooled.get("f1"),
                    "episode_recall": pooled.get("episode_recall"),
                    "mdt": pooled.get("mdt"),
                    "far": pooled.get("far_cerqueira"),
                    "far_per_run": pooled.get("far_per_run"),
                })
    return summary_rows, pooled_rows


def write_subset_outputs(summary_rows: list[dict[str, Any]], pooled_rows: list[dict[str, Any]]) -> None:
    summary_fields = list(summary_rows[0])
    pooled_fields = list(pooled_rows[0])
    write_csv(SUBSET_SUMMARY, summary_fields, summary_rows)
    write_csv(DETECTION_POOLED, pooled_fields, pooled_rows)


def fmt(value: Any, digits: int = 4) -> str:
    value = optional(value)
    return "—" if value is None else f"{float(value):.{digits}f}"


def fmt_ci(row: dict[str, Any], prefix: str, metric: str, digits: int = 4) -> str:
    point = optional(row.get(f"{prefix}_{metric}"))
    low = optional(row.get(f"{prefix}_{metric}_ci_low"))
    high = optional(row.get(f"{prefix}_{metric}_ci_high"))
    if point is None:
        return "—"
    if low is None or high is None:
        return fmt(point, digits)
    return f"{fmt(point, digits)} [{fmt(low, digits)}, {fmt(high, digits)}]"


def direction(value: Any, tolerance: float = 1e-15) -> str:
    value = optional(value)
    if value is None:
        return "na"
    if float(value) > tolerance:
        return "positive"
    if float(value) < -tolerance:
        return "negative"
    return "zero"


def pattern_sentence(label: str, selected: list[dict[str, Any]]) -> str:
    labels = {"positive": "正", "negative": "負", "zero": "零", "na": "無資料"}
    parts = []
    for metric, name in (("acc", "準確率"), ("post_acc", "drift 後準確率"),
                         ("fp", "FP"), ("X", "X")):
        counts = Counter(direction(row.get(f"delta_vs_hddma_{metric}")) for row in selected)
        counts.pop("na", None)
        if not counts:
            parts.append(f"{name}無可判讀資料")
        elif len(counts) == 1:
            key = next(iter(counts))
            parts.append(f"{name}一致為{labels[key]}（{counts[key]}/{sum(counts.values())}）")
        else:
            parts.append(
                f"{name}正/負/零={counts['positive']}/{counts['negative']}/{counts['zero']}"
            )
    return f"- **{label}：** " + "；".join(parts) + "。"


def report_patterns(summary_rows: list[dict[str, Any]]) -> list[str]:
    dual = [row for row in summary_rows if row["preset"] == "det4_s1_wadwin_cadwin"]
    output = [
        "嚴格以『同組所有可判讀子資料集同號』判定時，沒有任何 drift 型態或注入方式在任一指標上達到一致為正或一致為負；因此以下保留完整方向計數，不把多數方向寫成一致效果。",
        "",
        "方向解讀：準確率、drift 後準確率與 X 的正值有利 Dual ADWIN；FP 的負值才有利 Dual ADWIN。描述性分布上，突變組的準確率與 drift 後準確率負向較多，漸變組則正向較多；incremental／recurring 的準確率正向較多但 X 負向較多。四種注入方式仍各自同時出現正負值：class_prior 正向較多，feature_permutation 的 X 負向較多，label_swap 的 drift 後準確率負向較多；這些都不是一致效果。",
        "",
        "### Drift 型態均包含正負方向，不能推論普遍優勢",
        "",
    ]
    drift_types = ("突變", "漸變", "incremental", "recurring")
    for drift_type in drift_types:
        selected = []
        for row in dual:
            subset_text = row["subset"].lower()
            tags = det4.type_flags(row["dataset"], subset_text)
            if drift_type in tags:
                selected.append(row)
        output.append(pattern_sentence(drift_type, selected))
    output.extend(["", "### 注入方式以跨資料集／abruptness 的方向計數呈現", ""])
    methods = ("class_prior", "feature_filtering", "feature_permutation", "label_swap")
    for method in methods:
        selected = [row for row in dual if row["subset"].endswith(f"/{method}")]
        output.append(pattern_sentence(method, selected))
    return output


def build_report(summary_rows: list[dict[str, Any]], pooled_rows: list[dict[str, Any]],
                 validation: dict[str, Any], run_rows: list[dict[str, Any]]) -> str:
    by_key = {(row["subset"], row["preset"]): row for row in summary_rows}
    subsets = sorted({row["subset"] for row in summary_rows})
    primary = (
        ("論文 ECPF Dual ADWIN", "det4_s0_wadwin_cadwin"),
        ("論文 ECPF HDDM-A", "det4_s0_whddma_chddma"),
        ("完整系統 Dual ADWIN", "det4_s1_wadwin_cadwin"),
        ("完整系統 HDDM-A", "det4_s1_whddma_chddma"),
    )
    stream_counts = {(row["dataset"], row["subset"]): int(row["n_streams"])
                     for row in summary_rows}
    missing = [row for row in run_rows if row["status"] != "ok"]
    lines = [
        "# DET4 子資料集層級彙整：事後探索，不改變預註冊判定",
        "",
        "## 子資料集分析僅供事後探索，不產生新判定",
        "",
        "**定位聲明：** 子資料集分析是**事後探索分析**，不在 DET4 預註冊範圍內；本報告不產生新的判定，也不改變 H1–H3 的結論。",
        "",
        "**多重比較提醒：** 88 個子資料集 × 17 個比較，單純因為機率就會出現不少「信賴區間不含 0」的格子。以下只描述跨多個子資料集一致的型態，不以單一格子下結論；CI 是以串流為配對單位、10,000 次 percentile bootstrap、seed `20261012`。",
        "",
        "## 30,456 列逐 run 表完整重現既有 DET4 資料集層級結果",
        "",
        f"- 逐 run 列數：**{len(run_rows):,}**；18 個組合各 **{len(run_rows) // 18:,}** 列。",
        f"- 子資料集：**{len(subsets)}** 個；去重串流：**{sum(stream_counts.values()):,}** 條。",
        f"- 來源：DET4 新 run **{sum(row['source'] == 'det4_new' for row in run_rows):,}**；DET1 沿用 **{sum(row['source'] == 'reused_det1' for row in run_rows):,}**；DET3 沿用 **{sum(row['source'] == 'reused_det3' for row in run_rows):,}**。",
        f"- 重現檢查：**通過**；q4 數值點估計 {validation['q4_point_checks']:,} 格（另核對空值範圍，共 {validation['q4_field_checks']:,} 格）、T1/T3 aggregate {validation['t1_t3_aggregate_checks']:,} 欄，絕對誤差皆 `< {validation['tolerance']}`。",
        f"- skill pooled detection：**{len(pooled_rows):,}** 列；先加總 TP/FP/FN，再由 repo 既有 `pool_detection_runs` 計算 precision、recall、F1。",
        "",
        "## 四個主要組合顯示每個子資料集的加權準確率與 drift 後準確率",
        "",
        "每格為 `準確率 / drift 後 1000 步準確率`；`—` 表示該子資料集沒有可用 GT／drift 後窗口。",
        "",
        "| 子資料集 | n | " + " | ".join(label for label, _ in primary) + " |",
        "|---|---:|" + "---:|" * len(primary),
    ]
    for subset in subsets:
        n = int(by_key[(subset, primary[0][1])]["n_streams"])
        cells = [f"{fmt(by_key[(subset, preset)]['accuracy'])} / {fmt(by_key[(subset, preset)]['post_drift_1000_accuracy'])}"
                 for _, preset in primary]
        lines.append(f"| {subset} | {n} | " + " | ".join(cells) + " |")

    lines.extend([
        "",
        "## 完整系統 Dual ADWIN 相對完整系統 HDDM-A 的差異以配對 CI 呈現",
        "",
        "差值方向固定為 `完整系統 Dual ADWIN − 完整系統 HDDM-A`。子資料集少於 5 條串流時只列點估計。",
        "",
        "| 子資料集 | n | Δ準確率 [95% CI] | Δdrift 後準確率 [95% CI] | ΔFP [95% CI] | ΔX [95% CI] |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for subset in subsets:
        row = by_key[(subset, "det4_s1_wadwin_cadwin")]
        lines.append(
            f"| {subset} | {int(row['n_streams'])} | "
            f"{fmt_ci(row, 'delta_vs_hddma', 'acc')} | "
            f"{fmt_ci(row, 'delta_vs_hddma', 'post_acc')} | "
            f"{fmt_ci(row, 'delta_vs_hddma', 'fp', 2)} | "
            f"{fmt_ci(row, 'delta_vs_hddma', 'X', 2)} |"
        )

    lines.extend(["", "## 跨子資料集方向計數顯示型態是否一致", ""])
    lines.extend(report_patterns(summary_rows))
    lines.extend([
        "",
        "## 限制要求將成本缺口、CI 邊界與開發資料分開解讀",
        "",
        "- 沿用 DET1／DET3 的 run 若未記錄成本欄位，成本中位數排除空值；不得把不同機器或不同 `concurrent_runs` 的時間當成正式效能比較。",
        "- 單一串流，以及其他少於 5 條串流的子資料集，只報點估計、不報 bootstrap CI。",
        "- `synthetic_binary`、`synthetic_multiclass` 與部分資料曾用於開發；其子資料集結果不能視為獨立外部驗證。",
        "- 注入資料的 pooled detection 遵循 registry 的 skill window；DET 系列 `FP@1000`、`X` 則沿用 DET1–DET4 正式分析函式，兩者定義不可互換。",
        "",
        "## 缺漏保持可稽核，不以推估值補齊",
        "",
    ])
    if missing:
        lines.append(f"共有 **{len(missing)}** 列標為 missing／fallback；詳見逐 run 表的 `status`、`missing_reason` 與 `source`。")
    else:
        lines.append("未發現缺失或損毀 run；30,456 列皆由本機原始 artifact 讀取並通過既有 DET4 audit。")
    return "\n".join(lines).rstrip() + "\n"


def write_report(markdown: str) -> None:
    REPORT_MD.write_text(markdown)
    body = markdown_to_html(markdown)
    style = (
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
        "color:#17202a;background:#f6f8fa;margin:0}main{max-width:1500px;margin:0 auto;"
        "background:white;padding:32px 40px;box-shadow:0 1px 6px #ccd1d1}"
        "h1,h2,h3{color:#17365d}table{border-collapse:collapse;width:100%;font-size:12px;"
        "margin:14px 0 28px}th,td{border:1px solid #ccd1d1;padding:6px 8px;"
        "vertical-align:top}th{background:#eaf2f8;position:sticky;top:0}"
        "tr:nth-child(even){background:#fafafa}code{background:#eef2f5;padding:1px 4px}"
    )
    html = (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>DET4 子資料集層級彙整</title><style>{style}</style></head>"
        f"<body><main>{body}</main></body></html>\n"
    )
    REPORT_HTML.write_text(html)


def validate_cardinality(rows: list[dict[str, Any]], summary_rows: list[dict[str, Any]] | None = None) -> None:
    if len(rows) != 30_456:
        raise AssertionError(f"run rows: {len(rows)} != 30,456")
    preset_counts = Counter(row["preset"] for row in rows)
    if set(preset_counts.values()) != {1_692} or len(preset_counts) != 18:
        raise AssertionError(f"preset counts: {preset_counts}")
    stream_keys = {(row["dataset"], row["stream"]) for row in rows}
    subset_keys = {(row["dataset"], row["subset"]) for row in rows}
    if len(stream_keys) != 1_692 or len(subset_keys) != 88:
        raise AssertionError(f"streams/subsets: {len(stream_keys)}/{len(subset_keys)}")
    if summary_rows is not None and len(summary_rows) != 1_584:
        raise AssertionError(f"subset summary rows: {len(summary_rows)} != 1,584")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("run-scores", "subsets", "report", "all"), default="all")
    args = parser.parse_args()

    if args.stage == "report":
        run_rows = pd.read_csv(run_score_path(), low_memory=False).to_dict(orient="records")
        summary_rows = pd.read_csv(SUBSET_SUMMARY, low_memory=False).to_dict(orient="records")
        pooled_rows = pd.read_csv(DETECTION_POOLED, low_memory=False).to_dict(orient="records")
        validation = validate_reproduction()
        report = build_report(summary_rows, pooled_rows, validation, run_rows)
        write_report(report)
        print(f"report -> {REPORT_MD} and {REPORT_HTML}", flush=True)
        return

    rows = score_rows()
    validate_cardinality(rows)
    path = write_run_scores(rows)
    validation = validate_reproduction()
    print(f"run scores: {len(rows):,} rows -> {path}", flush=True)
    print(f"reproduction: PASS ({validation['q4_point_checks']} q4 points, "
          f"{validation['t1_t3_aggregate_checks']} aggregate fields)", flush=True)
    if args.stage == "run-scores":
        return

    summary_rows, pooled_rows = build_subset_outputs(rows)
    validate_cardinality(rows, summary_rows)
    write_subset_outputs(summary_rows, pooled_rows)
    print(f"subset summary: {len(summary_rows):,} rows -> {SUBSET_SUMMARY}", flush=True)
    print(f"pooled detection: {len(pooled_rows):,} rows -> {DETECTION_POOLED}", flush=True)
    if args.stage == "subsets":
        return

    report = build_report(summary_rows, pooled_rows, validation, rows)
    write_report(report)
    print(f"report -> {REPORT_MD} and {REPORT_HTML}", flush=True)


if __name__ == "__main__":
    main()
