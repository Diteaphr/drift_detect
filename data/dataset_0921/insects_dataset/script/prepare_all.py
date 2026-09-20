#!/usr/bin/env python3
"""Prepare data/insects_dataset (GT drift times; separate from real_dataset).

Examples:
  python3 prepare_all.py
  python3 prepare_all.py --variants abrupt_balanced,incremental_gradual_balanced
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import GDRIVE_IDS  # noqa: E402
from datasets import prepare_all  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare Insects streams with published drift change points."
    )
    parser.add_argument(
        "--variants",
        default=None,
        help=f"Comma-separated. Default all. Choices: {','.join(GDRIVE_IDS)}",
    )
    args = parser.parse_args()
    names = (
        [v.strip() for v in args.variants.split(",") if v.strip()]
        if args.variants
        else None
    )
    paths = prepare_all(names)
    print(f"\nDone. Wrote {len(paths)} variants under data/insects_dataset/")


if __name__ == "__main__":
    main()
