#!/usr/bin/env python3
"""Prepare real_dataset: download, convert, plot, validate.

Examples:
  python3 prepare_all.py
  python3 prepare_all.py --tasks binary
  python3 prepare_all.py --datasets ai4i2020,electricity
  python3 prepare_all.py --full     # uncapped airlines + covertype under _full/ (not in git)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import datasets as datasets_mod  # noqa: E402
from common import ensure_layout  # noqa: E402
from datasets import DATASETS  # noqa: E402

#: Datasets the default run caps at MAX_STREAM_ROWS; --full rebuilds these uncapped.
CAPPED = {"airlines", "covertype"}


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
        help="Comma-separated dataset names, e.g. ai4i2020,airlines,covertype",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Write uncapped versions of the capped datasets under _full/",
    )
    args = parser.parse_args()

    ensure_layout()
    if args.full:
        datasets_mod.FULL_LENGTH = True
        if args.datasets is None:
            args.datasets = ",".join(sorted(CAPPED))
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
