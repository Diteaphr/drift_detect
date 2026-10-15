#!/usr/bin/env python3
"""Run and audit the DET4 merge and diagonal bitwise replay gates."""

from __future__ import annotations

import argparse
import copy
import json
import multiprocessing
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import run_benchmark as benchmark  # noqa: E402
from src.metrics.run_cost import machine_info  # noqa: E402


SELECTION = REPO / "outputs" / "det3" / "repro_selection.json"
RAW_ROOT = REPO / "outputs" / "det4" / "gates_raw"
REPORT_JSON = REPO / "outputs" / "det4" / "repro_verification.json"
REPORT_MD = REPO / "outputs" / "det4" / "stage2_gate.md"

ARMS = {
    "det1_dual_adwin_lw0": ("det1", "adwin"),
    "det1_zone_hddm_a_lw0": ("det1", "hddm_a"),
    "det1_zone_rddm_lw0": ("det1", "rddm"),
    "det3_full_dual_adwin_lw1": ("det3", "adwin"),
    "det3_full_hddm_a_lw1": ("det3", "hddm_a"),
}


def selected_sources() -> list[tuple[str, dict[str, Any]]]:
    selection = json.loads(SELECTION.read_text())["groups"]
    registry = benchmark.load_registry()
    selected: list[tuple[str, dict[str, Any]]] = []

    injected = {s["stem"]: s for s in benchmark.dataset_sources(registry["injected_paper_electricity"], 20)}
    selected.extend(("injected_paper_electricity", injected[name]) for name in selection["injected"])

    synthetic = {s["stem"]: s for s in benchmark.dataset_sources(registry["synthetic_multiclass"], None)}
    selected.extend(("synthetic_multiclass", synthetic[name]) for name in selection["synthetic"])

    for dataset in selection["INSECTS"]:
        source = benchmark.dataset_sources(registry[dataset], None)
        if len(source) != 1:
            raise AssertionError(f"expected one source for {dataset}, got {len(source)}")
        selected.append((dataset, source[0]))
    if len(selected) != 15:
        raise AssertionError(f"expected 15 selected streams, got {len(selected)}")
    return selected


def gate_preset(name: str, detector: str, mode: str) -> dict[str, Any]:
    preset = copy.deepcopy(benchmark.load_preset(name))
    if mode == "mixed":
        preset["name"] = f"gate_{name}_{detector}_diagonal"
        preset["description"] = f"DET4 diagonal replay of {name} with independent {detector} arms"
        preset["config"]["ecpf_zone_detector"] = ""
        preset["config"]["ecpf_warning_detector"] = detector
        preset["config"]["ecpf_drift_detector"] = detector
    return preset


def expected_path(origin: str, dataset: str, preset: str, stem: str) -> Path:
    return REPO / "outputs" / "benchmark" / origin / dataset / preset / stem / "preds.npz"


def build_jobs(mode: str, git: dict[str, Any], workers: int) -> list[dict[str, Any]]:
    registry = benchmark.load_registry()
    machine = machine_info()
    jobs = []
    for preset_name, (origin, detector) in ARMS.items():
        preset = gate_preset(preset_name, detector, mode)
        for dataset, source in selected_sources():
            run_dir = RAW_ROOT / mode / dataset / preset_name / source["stem"]
            jobs.append({
                "source": source,
                "dataset": dataset,
                "entry": registry[dataset],
                "preset": preset,
                "seed": None,
                "max_steps": 0,
                "version_problems": benchmark.check_requirements(preset, False),
                "git": git,
                "record_warning_events": True,
                "machine": machine,
                "workers": workers,
                "model_size": False,
                "run_dir": str(run_dir),
                "expected": str(expected_path(origin, dataset, preset_name, source["stem"])),
                "origin_preset": preset_name,
                "gate_mode": mode,
            })
    return jobs


def compare_job(job: dict[str, Any]) -> dict[str, Any]:
    actual = Path(job["run_dir"]) / "preds.npz"
    expected = Path(job["expected"])
    result = {
        "mode": job["gate_mode"],
        "dataset": job["dataset"],
        "stream": job["source"]["stem"],
        "preset": job["origin_preset"],
        "expected": str(expected.relative_to(REPO)),
        "actual": str(actual.relative_to(REPO)),
        "matched": False,
        "fields": {},
    }
    if not expected.exists():
        result["error"] = "missing expected DET output"
        return result
    fields = ["y_true", "y_pred", "alarm_idx"]
    with np.load(expected) as old, np.load(actual) as new:
        fields.append("alarm_idx_input" if "alarm_idx_input" in old.files else "alarm_ts")
        for field in fields:
            same = field in new.files and old[field].dtype == new[field].dtype
            same = same and old[field].shape == new[field].shape
            same = same and np.array_equal(old[field], new[field], equal_nan=True)
            result["fields"][field] = bool(same)
    result["matched"] = all(result["fields"].values())
    return result


def write_report(rows: list[dict[str, Any]], elapsed_s: float, commit: str) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "selection_seed": 20261012,
        "commit": commit,
        "expected": 150,
        "completed": len(rows),
        "matched": sum(bool(r.get("matched")) for r in rows),
        "failed": sum(not bool(r.get("matched")) for r in rows),
        "by_mode": {
            mode: {
                "expected": 75,
                "matched": sum(r.get("matched", False) for r in rows if r["mode"] == mode),
            }
            for mode in ("legacy", "mixed")
        },
        "elapsed_s": round(elapsed_s, 2),
        "rows": rows,
    }
    REPORT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    failures = [r for r in rows if not r.get("matched")]
    status = "通過" if not failures and len(rows) == 150 else "失敗"
    lines = [
        "# DET4 階段二：merge 與混搭對角逐位元閘門",
        "",
        f"**結論：{status}。** 固定 seed `20261012` 的 15 條串流，五個既有對角各跑 legacy／mixed 兩種模式，共 `{len(rows)}/150`；逐位元相同 `{summary['matched']}/150`。",
        "",
        "| 閘門 | 預期 | 逐位元相同 | 結論 |",
        "|---|---:|---:|---|",
        f"| 合併 main 後、DET4 欄位關閉 | 75 | {summary['by_mode']['legacy']['matched']} | {'通過' if summary['by_mode']['legacy']['matched'] == 75 else '失敗'} |",
        f"| DET4 欄位開啟、warning=confirm 對角 | 75 | {summary['by_mode']['mixed']['matched']} | {'通過' if summary['by_mode']['mixed']['matched'] == 75 else '失敗'} |",
        "",
        f"執行 commit `{commit}`；牆上時間 `{elapsed_s / 60:.1f}` 分鐘。核對欄位為 `y_true`、`y_pred`、`alarm_idx`，以及適用的 `alarm_idx_input`（否則 `alarm_ts`）。單元測試另驗證獨立更新、zone exit 清 buffer、confirm reset、timeout 與 guard。",
    ]
    if failures:
        lines += ["", "## 失敗", ""]
        lines.extend(f"- `{r['mode']}/{r['dataset']}/{r['preset']}/{r['stream']}`：{r.get('error') or r['fields']}" for r in failures)
    REPORT_MD.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    git = benchmark.git_state()
    if git["dirty"]:
        raise SystemExit("DET4 gate requires a clean worktree")

    jobs = build_jobs("legacy", git, args.workers) + build_jobs("mixed", git, args.workers)
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=ctx) as pool:
        future_jobs = {pool.submit(benchmark.run_one_big_stack, job): job for job in jobs}
        for index, future in enumerate(as_completed(future_jobs), 1):
            job = future_jobs[future]
            try:
                future.result()
                row = compare_job(job)
            except Exception as exc:  # preserve all failures in the audit
                row = {
                    "mode": job["gate_mode"], "dataset": job["dataset"],
                    "stream": job["source"]["stem"], "preset": job["origin_preset"],
                    "matched": False, "error": repr(exc), "fields": {},
                }
            rows.append(row)
            print(f"[{index}/{len(jobs)}] {row['mode']} {row['preset']} {row['stream']} matched={row['matched']}", flush=True)
    rows.sort(key=lambda r: (r["mode"], r["preset"], r["dataset"], r["stream"]))
    write_report(rows, time.perf_counter() - started, git["commit"])
    if len(rows) != 150 or any(not row.get("matched") for row in rows):
        raise SystemExit("DET4 replay gate failed; see outputs/det4/repro_verification.json")


if __name__ == "__main__":
    main()
