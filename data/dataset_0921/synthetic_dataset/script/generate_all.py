#!/usr/bin/env python3
"""Generate curated synthetic datasets under data/synthetic_dataset/.

Examples:
  # smoke test
  python generate_all.py --smoke

  # full 100k, all tasks / drifts, g00-g09
  python generate_all.py

  # only binary sudden, g00-g02
  python generate_all.py --tasks binary --drift-types sudden --g-ids 0,1,2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from script/ directory
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from config import DRIFT_TYPES, G_IDS, MASTER_SEED, N_SAMPLES, TASKS  # noqa: E402
from generators import run_binary, run_multiclass, run_regression  # noqa: E402


def _parse_csv_ints(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip() != ""]


def _parse_csv_strs(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip() != ""]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate data/synthetic_dataset streams.")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Smoke test: N=2000, g00 only, all tasks/drifts.",
    )
    parser.add_argument("--n-samples", type=int, default=None)
    parser.add_argument("--g-ids", type=str, default=None, help="Comma-separated, e.g. 0,1,2")
    parser.add_argument(
        "--tasks",
        type=str,
        default=None,
        help=f"Comma-separated subset of {','.join(TASKS)}",
    )
    parser.add_argument(
        "--drift-types",
        type=str,
        default=None,
        help=f"Comma-separated subset of {','.join(DRIFT_TYPES)}",
    )
    parser.add_argument("--master-seed", type=int, default=MASTER_SEED)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()

    if args.smoke:
        n_samples = 2_000
        g_ids = [0]
    else:
        n_samples = args.n_samples if args.n_samples is not None else N_SAMPLES
        g_ids = _parse_csv_ints(args.g_ids) if args.g_ids else list(G_IDS)

    tasks = _parse_csv_strs(args.tasks) if args.tasks else list(TASKS)
    drift_types = _parse_csv_strs(args.drift_types) if args.drift_types else list(DRIFT_TYPES)

    for t in tasks:
        if t not in TASKS:
            raise SystemExit(f"Unknown task: {t}")
    for d in drift_types:
        if d not in DRIFT_TYPES:
            raise SystemExit(f"Unknown drift type: {d}")

    make_plots = not args.no_plots
    all_rows: list[dict] = []

    print(
        f"Generating: n_samples={n_samples}, g_ids={g_ids}, "
        f"tasks={tasks}, drift_types={drift_types}, master_seed={args.master_seed}"
    )

    if "binary" in tasks:
        all_rows.extend(
            run_binary(
                n_samples=n_samples,
                g_ids=g_ids,
                drift_types=drift_types,
                master_seed=args.master_seed,
                make_plots=make_plots,
            )
        )
    if "multi_classification" in tasks:
        all_rows.extend(
            run_multiclass(
                n_samples=n_samples,
                g_ids=g_ids,
                drift_types=drift_types,
                master_seed=args.master_seed,
                make_plots=make_plots,
            )
        )
    if "regression" in tasks:
        all_rows.extend(
            run_regression(
                n_samples=n_samples,
                g_ids=g_ids,
                drift_types=drift_types,
                master_seed=args.master_seed,
                make_plots=make_plots,
            )
        )

    print(f"Done. Wrote {len(all_rows)} dataset files.")
    recurring = [r for r in all_rows if r.get("drift_type") == "recurring"]
    if recurring:
        print("Recurring mode draws:")
        for r in recurring:
            print(
                f"  {r['task']:22s} g{r['g_id']:02d} -> {r.get('chosen_drift_mode')}  ({r['stem']})"
            )


if __name__ == "__main__":
    main()
