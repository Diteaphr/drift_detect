#!/usr/bin/env python3
"""Run and audit the preregistered DET4 smoke matrix."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.run_benchmark import load_registry  # noqa: E402


OUT = "outputs/det4/smoke"
LOG_DIR = REPO / "outputs" / "det4" / "logs"
AUDIT_JSON = REPO / "outputs" / "det4" / "stage3_smoke_audit.json"
AUDIT_MD = REPO / "outputs" / "det4" / "stage3_smoke.md"
PRESETS = sorted(path.stem for path in (REPO / "configs" / "presets").glob("det4_*.json"))
PRIMARY = {
    "injected_paper_electricity": 2,
    "synthetic_multiclass": 2,
    "insects_abrupt_balanced": 1,
}
COST_FIELDS = (
    "runtime_s", "cpu_time_s", "instances_per_s", "rss_increment_mb",
    "model_size_final_mb", "ram_hours_gb", "concurrent_runs",
)


def datasets() -> list[tuple[str, int]]:
    registry = load_registry()
    included = [name for name, entry in registry.items() if entry["task"] != "regression"]
    ordered = list(PRIMARY)
    ordered.extend(name for name in included if name not in PRIMARY)
    result = [(name, PRIMARY.get(name, 1)) for name in ordered]
    if len(result) != 23:
        raise AssertionError(f"expected 23 non-regression datasets, got {len(result)}")
    return result


def run_smoke(workers: int) -> dict:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    commands = []
    for index, (dataset, limit) in enumerate(datasets(), 1):
        command = [
            sys.executable, str(REPO / "scripts" / "run_benchmark.py"),
            "--dataset", dataset,
            "--preset", *PRESETS,
            "--limit-files", str(limit),
            "--max-steps", "5000",
            "--workers", str(workers),
            "--out-dir", OUT,
            "--record-warning-events",
            "--resume",
        ]
        log_path = LOG_DIR / f"smoke_{dataset}.log"
        print(f"[{index}/{len(datasets())}] smoke {dataset}: {18 * limit} runs", flush=True)
        with log_path.open("w") as log:
            completed = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
        commands.append({
            "dataset": dataset,
            "limit_files": limit,
            "runs": 18 * limit,
            "returncode": completed.returncode,
            "log": str(log_path.relative_to(REPO)),
        })
    return {"elapsed_s": time.perf_counter() - started, "commands": commands}


def audit_smoke(run_info: dict | None = None) -> dict:
    root = REPO / OUT
    rows = []
    errors = []
    reason_counts: dict[str, int] = {}
    for runs_path in sorted(root.glob("*/*/runs.csv")):
        frame = pd.read_csv(runs_path)
        for row in frame.to_dict("records"):
            rows.append(row)
            if pd.notna(row.get("error")):
                errors.append(f"{runs_path}: {row['error']}")
                continue
            run_dir = REPO / str(row["run_dir"])
            for filename in ("manifest.json", "metrics.json", "preds.npz", "warning_events.json"):
                if not (run_dir / filename).exists():
                    errors.append(f"{run_dir}: missing {filename}")
            if errors and errors[-1].startswith(str(run_dir)):
                continue
            manifest = json.loads((run_dir / "manifest.json").read_text())
            metrics = json.loads((run_dir / "metrics.json").read_text())
            events = json.loads((run_dir / "warning_events.json").read_text())
            if manifest.get("max_steps") != 5000:
                errors.append(f"{run_dir}: max_steps is not 5000")
            if row.get("comparable") not in (False, "False", 0):
                errors.append(f"{run_dir}: smoke row marked comparable")
            cost = manifest.get("cost", {})
            for field in COST_FIELDS:
                value = row.get(field, cost.get(field))
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    errors.append(f"{run_dir}: missing cost {field}")
            opens = sum(event.get("event") == "open" for event in events)
            terminal = sum(event.get("event") in {"close", "censored"} for event in events)
            if opens != terminal:
                errors.append(f"{run_dir}: warning conservation {opens} != {terminal}")
            for event in events:
                if event.get("event") in {"close", "censored"}:
                    reason = str(event.get("reason"))
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
            if str(row["preset"]).startswith("det4_s1_") and metrics.get("warning_frozen_steps") != 0:
                errors.append(f"{run_dir}: S1 warning_frozen_steps={metrics.get('warning_frozen_steps')}")

    expected = 18 * sum(limit for _, limit in datasets())
    if len(rows) != expected:
        errors.append(f"expected {expected} rows, found {len(rows)}")
    if run_info:
        for command in run_info["commands"]:
            if command["returncode"] != 0:
                errors.append(f"runner failed for {command['dataset']}: returncode {command['returncode']}")
    result = {
        "expected_runs": expected,
        "completed_runs": len(rows),
        "failed_runs": sum(pd.notna(row.get("error")) for row in rows),
        "presets": len({row.get("preset") for row in rows}),
        "datasets": len({row.get("dataset") for row in rows}),
        "warning_close_reasons": reason_counts,
        "elapsed_s": round(run_info["elapsed_s"], 2) if run_info else None,
        "errors": errors,
        "commands": run_info["commands"] if run_info else None,
    }
    AUDIT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    status = "通過" if not errors else "失敗"
    lines = [
        "# DET4 階段三：18 組 × 23 資料集 smoke",
        "",
        f"**結論：{status}。** 完成 `{len(rows)}/{expected}` runs，涵蓋 `{result['presets']}/18` presets 與 `{result['datasets']}/23` 非迴歸資料集；runner error rows `{result['failed_runs']}`。",
        "",
        "| 核對 | 結果 |",
        "|---|---|",
        "| 每組固定 injected 2、synthetic 2、INSECTS abrupt 1，其餘資料集各 1 | " + ("通過" if len(rows) == expected else "失敗") + " |",
        "| manifest、metrics、preds、warning events | " + ("通過" if not any("missing" in e for e in errors) else "失敗") + " |",
        "| 成本欄位皆有值 | " + ("通過" if not any("missing cost" in e for e in errors) else "失敗") + " |",
        "| warning 開啟 = close + censored | " + ("通過" if not any("warning conservation" in e for e in errors) else "失敗") + " |",
        "| S1 凍結步數 = 0 | " + ("通過" if not any("warning_frozen_steps" in e for e in errors) else "失敗") + " |",
        "",
        "Warning 結束原因：" + ", ".join(f"`{key}`={value}" for key, value in sorted(reason_counts.items())) + ".",
    ]
    if run_info:
        lines.append(f"牆上時間 `{run_info['elapsed_s'] / 60:.1f}` 分鐘；所有 smoke 均標示 non-comparable。")
    if errors:
        lines += ["", "## 錯誤", ""] + [f"- {error}" for error in errors]
    AUDIT_MD.write_text("\n".join(lines) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    run_info = None if args.audit_only else run_smoke(args.workers)
    audit = audit_smoke(run_info)
    if audit["errors"]:
        raise SystemExit("DET4 smoke failed; see outputs/det4/stage3_smoke_audit.json")


if __name__ == "__main__":
    main()
