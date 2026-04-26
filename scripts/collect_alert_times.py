#!/usr/bin/env python3
"""
Collect drift alert timestamps for one or more CSV streams (no ground truth).

Run from the **repository root**::

    python scripts/collect_alert_times.py --csv data/sudden_drift/recurring_sudden_sea100k_g00.csv --out alerts.json

    python scripts/collect_alert_times.py --glob 'data/sudden_drift/*.csv' --setting myrun --out alerts.json

Optional ``--config-json`` merges keys into :class:`src.config.PipelineConfig` (same
defaults as ``main.py``). Output JSON: ``setting`` + ``runs`` with ``csv`` (absolute
path), ``csv_stem``, ``n_samples``, ``n_alerts``, ``alert_times``.
"""

from __future__ import annotations

import argparse
import json
import sys
from glob import glob as glob_fn
from pathlib import Path

# Repo root (parent of scripts/)
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.alert_collection import (  # noqa: E402
    load_stream_csv,
    pipeline_config_from_dict,
    run_pipeline_alerts,
)


def _collect_csv_paths(csv_args: list[str], glob_args: list[str]) -> list[Path]:
    seen: dict[str, None] = {}
    out: list[Path] = []
    for s in csv_args:
        p = Path(s).resolve()
        key = str(p)
        if key not in seen:
            seen[key] = None
            out.append(p)
    for pattern in glob_args:
        for match in sorted(glob_fn(pattern)):
            p = Path(match).resolve()
            if p.suffix.lower() != ".csv":
                continue
            key = str(p)
            if key not in seen:
                seen[key] = None
                out.append(p)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the drift pipeline on CSV(s) and write alert timestamps to JSON.",
    )
    parser.add_argument(
        "--csv",
        action="append",
        default=[],
        metavar="PATH",
        help="CSV path (repeatable). Must contain a 'y' column.",
    )
    parser.add_argument(
        "--glob",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Glob pattern relative to cwd (repeatable), e.g. data/sudden_drift/*.csv",
    )
    parser.add_argument(
        "--setting",
        default="default",
        help="Label for this batch (e.g. different hyperparameters).",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON path.",
    )
    parser.add_argument(
        "--config-json",
        type=Path,
        default=None,
        help="Optional JSON object of PipelineConfig fields to override defaults (main.py-style).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each file to stderr as it runs.",
    )
    args = parser.parse_args()

    paths = _collect_csv_paths(args.csv, args.glob)
    if not paths:
        parser.error("No CSV files: pass --csv and/or --glob")

    overrides = None
    if args.config_json is not None:
        with open(args.config_json, "r", encoding="utf-8") as f:
            overrides = json.load(f)
        if not isinstance(overrides, dict):
            parser.error("--config-json must contain a JSON object")
    config = pipeline_config_from_dict(overrides)

    runs: list[dict] = []
    for path in paths:
        if args.verbose:
            print(f"[collect_alert_times] {path}", file=sys.stderr)
        X, y = load_stream_csv(path)
        alert_times = run_pipeline_alerts(X, y, config=config)
        runs.append(
            {
                "csv": str(path),
                "csv_stem": path.stem,
                "n_samples": int(len(y)),
                "n_alerts": len(alert_times),
                "alert_times": alert_times,
            }
        )

    payload = {"setting": args.setting, "runs": runs}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if args.verbose:
        print(f"[collect_alert_times] wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
