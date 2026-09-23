#!/usr/bin/env python3
"""Inject Cerqueira et al. drifts into data/real_dataset → data/injected_real_dataset.

Examples:
  python3 generate_all.py --smoke
  python3 generate_all.py
  python3 generate_all.py --datasets electricity,ai4i2020 --methods class_prior,label_swap
  python3 generate_all.py --g-ids 0,1,2 --abruptness abrupt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    deterministic_seed,
    ensure_layout,
    g_tag,
    out_dir,
    plot_stream,
    plots_dir,
    write_csv,
    write_drift_times,
    write_json,
)
from config import (  # noqa: E402
    ABRUPTNESS,
    DATASETS,
    DRIFT_METHODS,
    G_IDS,
    MASTER_SEED,
    TASKS,
)
from inject import inject_stream  # noqa: E402


def _parse_csv_ints(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip() != ""]


def _parse_csv_strs(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip() != ""]


def generate_one(
    name: str,
    method: str,
    abruptness: str,
    g_id: int,
    *,
    master_seed: int,
    make_plot: bool,
    max_n_override: int | None,
) -> Path:
    cfg = DATASETS[name]
    task = cfg["task"]
    if method not in cfg["methods"]:
        raise ValueError(f"{name} does not support method={method}")

    src = Path(cfg["path"])
    if not src.exists():
        raise FileNotFoundError(f"Missing source CSV: {src}")

    df = pd.read_csv(src)
    seed = deterministic_seed(master_seed, name, method, abruptness, g_id)
    rng = np_rng(seed)

    max_n = max_n_override if max_n_override is not None else cfg.get("max_n")
    out_df, intervals, trial_meta, baseline_df, kept_orig_idx = inject_stream(
        df,
        method=method,
        abruptness=abruptness,
        drift_width=int(cfg["drift_width"]),
        rng=rng,
        max_n=max_n,
    )

    ensure_layout(task, abruptness, method)
    tag = g_tag(g_id)
    stem = f"{name}_{method}_{abruptness}_{tag}"
    base = out_dir(task, abruptness, method)
    csv_path = base / f"{stem}.csv"
    drift_path = base / f"{stem}_drift_times.txt"
    meta_path = base / f"{stem}.json"

    write_csv(csv_path, out_df)
    write_drift_times(drift_path, intervals)
    write_json(
        meta_path,
        {
            "source_dataset": name,
            "source_path": str(src),
            "task": task,
            "paper": "Cerqueira et al. A Framework for Evaluating and Benchmarking Concept Drift Detection Methods (arXiv:2606.07789)",
            "framework": "shuffle + Monte Carlo single-drift injection",
            "g_id": g_id,
            "seed": seed,
            **trial_meta,
        },
    )

    if make_plot and g_id == 0:
        plot_path = plots_dir(task) / f"{stem}_y.png"
        plot_stream(
            out_df,
            intervals,
            plot_path,
            task=task,
            title=f"{name} / {method} / {abruptness}",
            df_baseline=baseline_df,
            kept_orig_idx=kept_orig_idx,
            intervals_input=trial_meta.get("drift_times_input"),
        )

    print(
        f"[{task}/{abruptness}/{method}] {stem} "
        f"n={len(out_df)} drift={intervals} -> {csv_path.name}"
    )
    return csv_path


def np_rng(seed: int):
    import numpy as np

    return np.random.default_rng(seed)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inject paper drifts into real_dataset → injected_real_dataset"
    )
    parser.add_argument("--smoke", action="store_true", help="g00 only, max_n=3000")
    parser.add_argument("--g-ids", default=None, help="e.g. 0,1,2")
    parser.add_argument("--datasets", default=None, help=f"subset of {','.join(DATASETS)}")
    parser.add_argument("--methods", default=None, help=f"subset of {','.join(DRIFT_METHODS)}")
    parser.add_argument("--abruptness", default=None, help="abrupt,gradual")
    parser.add_argument("--tasks", default=None, help=f"subset of {','.join(TASKS)}")
    parser.add_argument("--master-seed", type=int, default=MASTER_SEED)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()

    g_ids = [0] if args.smoke else (_parse_csv_ints(args.g_ids) if args.g_ids else list(G_IDS))
    names = _parse_csv_strs(args.datasets) if args.datasets else list(DATASETS.keys())
    methods = _parse_csv_strs(args.methods) if args.methods else list(DRIFT_METHODS)
    abrupt_list = (
        _parse_csv_strs(args.abruptness) if args.abruptness else list(ABRUPTNESS)
    )
    tasks_filter = set(_parse_csv_strs(args.tasks)) if args.tasks else None
    max_n_override = 3000 if args.smoke else None

    for n in names:
        if n not in DATASETS:
            raise SystemExit(f"Unknown dataset: {n}")
    for m in methods:
        if m not in DRIFT_METHODS:
            raise SystemExit(f"Unknown method: {m}")
    for a in abrupt_list:
        if a not in ABRUPTNESS:
            raise SystemExit(f"Unknown abruptness: {a}")

    n_written = 0
    for name in names:
        cfg = DATASETS[name]
        if tasks_filter is not None and cfg["task"] not in tasks_filter:
            continue
        for method in methods:
            if method not in cfg["methods"]:
                continue
            for abruptness in abrupt_list:
                for g_id in g_ids:
                    generate_one(
                        name,
                        method,
                        abruptness,
                        g_id,
                        master_seed=args.master_seed,
                        make_plot=not args.no_plots,
                        max_n_override=max_n_override,
                    )
                    n_written += 1

    print(f"\nDone. Wrote {n_written} streams under {Path(SCRIPT_DIR).parent}/")


if __name__ == "__main__":
    main()
