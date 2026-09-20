#!/usr/bin/env python3
"""Prepare real_dataset: download, convert, plot, validate.

Examples:
  python3 prepare_all.py
  python3 prepare_all.py --tasks binary
  python3 prepare_all.py --datasets ai4i2020,electricity
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import ensure_layout  # noqa: E402
from datasets import DATASETS  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare data/real_dataset")
    parser.add_argument(
        "--tasks",
        default=None,
        help="Comma-separated: binary,multi_classification,regression",
    )
    parser.add_argument(
        "--datasets",
        default=None,
        help="Comma-separated dataset names, e.g. ai4i2020,covertype",
    )
    args = parser.parse_args()

    ensure_layout()
    wanted_tasks = (
        [t.strip() for t in args.tasks.split(",") if t.strip()]
        if args.tasks
        else list(DATASETS.keys())
    )
    wanted_names = (
        {d.strip() for d in args.datasets.split(",") if d.strip()}
        if args.datasets
        else None
    )

    summary: list[tuple[str, str, Path]] = []
    for task in wanted_tasks:
        if task not in DATASETS:
            raise SystemExit(f"Unknown task: {task}")
        for name, fn in DATASETS[task].items():
            if wanted_names is not None and name not in wanted_names:
                continue
            print(f"==> {task}/{name}")
            path = fn()
            summary.append((task, name, path))

    print("\nDone:")
    for task, name, path in summary:
        print(f"  {task:22s} {name:28s} {path}")


if __name__ == "__main__":
    main()
