#!/usr/bin/env python3
"""Run one preregistered DET4 formal batch and write an auditable summary."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.run_benchmark import dataset_sources, load_registry  # noqa: E402


LOG_DIR = REPO / "outputs" / "det4" / "logs"
FORMAL_OUT = "outputs/benchmark/det4"
TIMING_OUT = "outputs/benchmark/det4_strict_timing"
MIN_FULL_FREE_GIB = 20

ALL_PRESETS = tuple(
    path.stem for path in sorted((REPO / "configs" / "presets").glob("det4_*.json"))
)
REUSED_DIAGONALS = {
    "det4_s0_wadwin_cadwin",
    "det4_s0_whddma_chddma",
    "det4_s0_wrddm_crddm",
    "det4_s1_wadwin_cadwin",
    "det4_s1_whddma_chddma",
}
OFF_DIAGONAL_PRESETS = tuple(name for name in ALL_PRESETS if name not in REUSED_DIAGONALS)


@dataclass(frozen=True)
class WorkItem:
    dataset: str
    presets: tuple[str, ...] = ALL_PRESETS
    trials: int | None = None
    trial_start: int = 0
    out_dir: str = FORMAL_OUT
    workers: int = 6


INSECTS = (
    "insects_abrupt_balanced",
    "insects_incremental_balanced",
    "insects_incremental_gradual_balanced",
    "insects_incremental_abrupt_reoccurring_balanced",
    "insects_incremental_reoccurring_balanced",
)
SHORT = (
    "electricity",
    "airlines",
    "covertype",
    "gas_sensor_drift",
    "ai4i2020",
    "injected_electricity",
    "injected_airlines",
    "injected_ai4i2020",
    "injected_covertype",
    "injected_gas_sensor_drift",
    "synthetic_binary",
)

BATCHES: dict[str, tuple[WorkItem, ...]] = {
    "t1": (
        WorkItem("injected_paper_electricity", OFF_DIAGONAL_PRESETS, trials=20),
        WorkItem("synthetic_multiclass", OFF_DIAGONAL_PRESETS),
        *(WorkItem(dataset, OFF_DIAGONAL_PRESETS) for dataset in INSECTS),
    ),
    "t3": (WorkItem("injected_paper_electricity", trials=30, trial_start=20),),
    "short": tuple(WorkItem(dataset) for dataset in SHORT),
    "paper": (
        WorkItem("injected_paper_covertype"),
        WorkItem("injected_paper_gas_sensor_drift"),
    ),
    "full": (WorkItem("airlines_full"), WorkItem("covertype_full")),
    "timing": (WorkItem("electricity", out_dir=TIMING_OUT, workers=1),),
}


def selected_sources(item: WorkItem) -> list[dict[str, Any]]:
    entry = load_registry()[item.dataset]
    return dataset_sources(entry, item.trials, item.trial_start)


def expected_runs(item: WorkItem) -> int:
    return len(selected_sources(item)) * len(item.presets)


def batch_expected(batch: str) -> int:
    return sum(expected_runs(item) for item in BATCHES[batch])


def command_for(item: WorkItem) -> list[str]:
    command = [
        sys.executable,
        str(REPO / "scripts" / "run_benchmark.py"),
        "--dataset",
        item.dataset,
        "--preset",
        *item.presets,
        "--workers",
        str(item.workers),
        "--out-dir",
        item.out_dir,
        "--record-warning-events",
        "--resume",
    ]
    if item.trials is not None:
        command.extend(("--trials", str(item.trials)))
    if item.trial_start:
        command.extend(("--trial-start", str(item.trial_start)))
    return command


def audit_item(item: WorkItem) -> dict[str, Any]:
    stems = {source["stem"] for source in selected_sources(item)}
    errors: list[str] = []
    complete = 0
    failed = 0
    seen: set[tuple[str, str]] = set()
    for preset in item.presets:
        runs_path = REPO / item.out_dir / item.dataset / preset / "runs.csv"
        if not runs_path.exists():
            errors.append(f"missing {runs_path.relative_to(REPO)}")
            continue
        frame = pd.read_csv(runs_path)
        selected = frame[frame["stream"].isin(stems)]
        for row in selected.to_dict("records"):
            key = (preset, str(row.get("stream")))
            if key in seen:
                errors.append(f"duplicate {preset}/{row.get('stream')}")
                continue
            seen.add(key)
            if pd.notna(row.get("error")):
                failed += 1
                errors.append(f"failed {preset}/{row.get('stream')}: {row.get('error')}")
                continue
            run_dir_value = row.get("run_dir")
            if pd.isna(run_dir_value):
                errors.append(f"missing run_dir {preset}/{row.get('stream')}")
                continue
            run_dir = REPO / str(run_dir_value)
            missing = [
                name
                for name in ("manifest.json", "metrics.json", "preds.npz", "warning_events.json")
                if not (run_dir / name).exists()
            ]
            if missing:
                errors.append(f"incomplete {preset}/{row.get('stream')}: {','.join(missing)}")
                continue
            complete += 1
    expected = expected_runs(item)
    missing_count = expected - len(seen)
    if missing_count:
        errors.append(f"missing {missing_count} run rows")
    return {
        "dataset": item.dataset,
        "out_dir": item.out_dir,
        "workers": item.workers,
        "trials": item.trials,
        "trial_start": item.trial_start,
        "presets": len(item.presets),
        "streams": len(stems),
        "expected": expected,
        "complete": complete,
        "failed": failed,
        "errors": errors,
    }


def free_gib() -> float:
    return shutil.disk_usage(REPO).free / 1024**3


def write_status(payload: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "formal_status.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )


def run_item(batch: str, index: int, total: int, item: WorkItem) -> dict[str, Any]:
    started = time.perf_counter()
    log_path = LOG_DIR / f"formal_{batch}_{index:02d}_{item.dataset}.log"
    command = command_for(item)
    attempts = 0
    audit: dict[str, Any] | None = None
    while attempts < 2:
        attempts += 1
        print(
            f"[{index}/{total}] {item.dataset}: attempt {attempts}, "
            f"expected {expected_runs(item)} runs",
            flush=True,
        )
        with log_path.open("a") as log:
            log.write(f"\n=== attempt {attempts} ===\n")
            completed = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
            log.write(f"\n=== returncode {completed.returncode} ===\n")
        audit = audit_item(item)
        if completed.returncode == 0 and not audit["errors"]:
            break
        print(
            f"[{index}/{total}] {item.dataset}: retrying "
            f"({audit['complete']}/{audit['expected']} complete, {audit['failed']} failed)",
            flush=True,
        )
    assert audit is not None
    audit["attempts"] = attempts
    audit["elapsed_s"] = round(time.perf_counter() - started, 2)
    audit["log"] = str(log_path.relative_to(REPO))
    audit["free_gib_after"] = round(free_gib(), 2)
    print(
        f"[{index}/{total}] {item.dataset}: {audit['complete']}/{audit['expected']} complete, "
        f"{audit['failed']} failed, {audit['elapsed_s'] / 60:.1f} min, "
        f"free {audit['free_gib_after']:.1f} GiB",
        flush=True,
    )
    return audit


def write_summary(batch: str, started: float, results: list[dict[str, Any]], skipped: list[dict[str, Any]]) -> dict[str, Any]:
    expected = sum(result["expected"] for result in results)
    complete = sum(result["complete"] for result in results)
    failed = sum(result["failed"] for result in results)
    errors = [error for result in results for error in result["errors"]]
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    summary = {
        "batch": batch,
        "commit": commit,
        "expected_runs": expected,
        "completed_runs": complete,
        "failed_runs": failed,
        "elapsed_s": round(time.perf_counter() - started, 2),
        "free_gib_after": round(free_gib(), 2),
        "results": results,
        "skipped": skipped,
        "errors": errors,
    }
    base = REPO / "outputs" / "det4" / f"formal_{batch}_summary"
    base.with_suffix(".json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    status = "通過" if not errors else "有缺漏"
    lines = [
        f"# DET4 formal {batch} 批次已{status}",
        "",
        f"**結論：** 完成 `{complete}/{expected}` runs；失敗 `{failed}`；牆上時間 `{summary['elapsed_s'] / 3600:.2f}` 小時；剩餘磁碟 `{summary['free_gib_after']:.1f}` GiB。",
        "",
        "| 資料集 | 完成 / 預期 | 失敗 | 嘗試 | 分鐘 |",
        "|---|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| `{result['dataset']}` | {result['complete']} / {result['expected']} | "
            f"{result['failed']} | {result['attempts']} | {result['elapsed_s'] / 60:.1f} |"
        )
    if skipped:
        lines += ["", "## 跳過", ""] + [f"- `{row['dataset']}`：{row['reason']}" for row in skipped]
    if errors:
        lines += ["", "## 失敗與缺漏", ""] + [f"- {error}" for error in errors]
    base.with_suffix(".md").write_text("\n".join(lines) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, choices=tuple(BATCHES))
    parser.add_argument("--workers", type=int, default=None, help="override batch workers (testing only)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    items = BATCHES[args.batch]
    if args.workers is not None:
        items = tuple(
            WorkItem(
                item.dataset,
                item.presets,
                item.trials,
                item.trial_start,
                item.out_dir,
                args.workers,
            )
            for item in items
        )
    if args.dry_run:
        payload = {
            "batch": args.batch,
            "expected_runs": sum(expected_runs(item) for item in items),
            "items": [
                {
                    "dataset": item.dataset,
                    "expected": expected_runs(item),
                    "command": command_for(item),
                }
                for item in items
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for index, item in enumerate(items, 1):
        if args.batch == "full" and free_gib() < MIN_FULL_FREE_GIB:
            row = {
                "dataset": item.dataset,
                "reason": f"free disk below {MIN_FULL_FREE_GIB} GiB before start",
            }
            skipped.append(row)
            print(f"[{index}/{len(items)}] {item.dataset}: skipped by disk gate", flush=True)
            continue
        write_status(
            {
                "batch": args.batch,
                "state": "running",
                "current_index": index,
                "total_items": len(items),
                "dataset": item.dataset,
                "completed_items": results,
                "free_gib": round(free_gib(), 2),
            }
        )
        results.append(run_item(args.batch, index, len(items), item))
    summary = write_summary(args.batch, started, results, skipped)
    write_status({"batch": args.batch, "state": "complete", "summary": summary})
    if summary["errors"]:
        raise SystemExit(f"DET4 formal {args.batch} completed with missing or failed runs")


if __name__ == "__main__":
    main()
