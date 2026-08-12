"""
產生 sudden / gradual concept drift 模擬資料（CSV + drift_times.txt）與 summary.csv。
依賴 concept_drift_visualization 中的 River 串流邏輯。

輸出目錄（每種 drift 下分 low / medium / high）：
- sudden_drift/{tier}/recurring_sudden_sea100k_g{00-09}.csv
- gradual_drift/{tier}/recurring_gradual_sea100k_g{00-09}.csv
"""

from __future__ import annotations

import csv
import glob
import os
import secrets
import sys

import numpy as np

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from concept_drift_visualization import (  # noqa: E402
    N_SAMPLES,
    build_drift_plan,
    extract_stream_from_chunks,
    make_multi_gradual_drift_stream,
    make_multi_sudden_drift_stream,
    _random_n_drifts,
)
from drift_common.intervals import drift_intervals_for_positions  # noqa: E402
from drift_common.profiles import resolve  # noqa: E402
from drift_common.sensitivity import SENSITIVITY_TIERS  # noqa: E402


def write_drift_times_txt(path: str, intervals: list[list[int]]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(repr(intervals))


def write_dataset_csv(path: str, xs: list, ys: np.ndarray) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x0", "x1", "x2", "y"])
        for x, yi in zip(xs, ys):
            w.writerow([x[0], x[1], x[2], int(yi)])


def _clear_legacy_flat_files(drift_dir: str) -> None:
    """Remove CSV/txt placed directly under drift_dir (pre-tier layout)."""
    for pat in ("*.csv", "*_drift_times.txt"):
        for fp in glob.glob(os.path.join(drift_dir, pat)):
            try:
                os.remove(fp)
            except OSError:
                pass


def _summary_row(
    drift_type: str,
    tier: str,
    params: dict,
    run_id: int,
    rel_csv: str,
    rel_txt: str,
    seed: int,
) -> dict:
    return {
        "drift_type": drift_type,
        "sensitivity": tier,
        "sensitivity_multiplier": params["sensitivity_multiplier"],
        "run_id": run_id,
        "csv_filename": rel_csv,
        "drift_times_filename": rel_txt,
        "random_seed": seed,
    }


def main() -> None:
    out_dir = os.getcwd()
    sudden_base = os.path.join(out_dir, "sudden_drift")
    gradual_base = os.path.join(out_dir, "gradual_drift")
    _clear_legacy_flat_files(sudden_base)
    _clear_legacy_flat_files(gradual_base)

    n_runs = 10
    rows_summary: list[dict] = []

    for tier in SENSITIVITY_TIERS:
        sudden_params = resolve("binary", "sudden", tier)
        sudden_dir = os.path.join(sudden_base, tier)
        os.makedirs(sudden_dir, exist_ok=True)
        width = sudden_params["width"]

        for run_id in range(1, n_runs + 1):
            g_tag = f"g{run_id - 1:02d}"
            seed = secrets.randbelow(2**32)
            rng = np.random.default_rng(seed)
            n_drifts = _random_n_drifts(rng)
            plan = build_drift_plan(N_SAMPLES, n_drifts, rng, width_ref=width)

            csv_name = f"recurring_sudden_sea100k_{g_tag}.csv"
            txt_name = f"recurring_sudden_sea100k_{g_tag}_drift_times.txt"
            csv_path = os.path.join(sudden_dir, csv_name)
            txt_path = os.path.join(sudden_dir, txt_name)

            chunks, _meta = make_multi_sudden_drift_stream(
                n_samples=N_SAMPLES,
                seed=seed,
                plan=plan,
                transition_width=width,
            )
            xs, ys = extract_stream_from_chunks(chunks, n_samples=N_SAMPLES)
            assert len(xs) == N_SAMPLES
            write_dataset_csv(csv_path, xs, ys)
            intervals = drift_intervals_for_positions(
                plan["drift_positions"], width, N_SAMPLES
            )
            write_drift_times_txt(txt_path, intervals)

            rows_summary.append(
                _summary_row(
                    "sudden",
                    tier,
                    sudden_params,
                    run_id,
                    os.path.join("sudden_drift", tier, csv_name),
                    os.path.join("sudden_drift", tier, txt_name),
                    seed,
                )
            )

    for tier in SENSITIVITY_TIERS:
        gradual_params = resolve("binary", "gradual", tier)
        gradual_dir = os.path.join(gradual_base, tier)
        os.makedirs(gradual_dir, exist_ok=True)
        width = gradual_params["width"]

        for run_id in range(1, n_runs + 1):
            g_tag = f"g{run_id - 1:02d}"
            seed = secrets.randbelow(2**32)
            rng = np.random.default_rng(seed)
            n_drifts = _random_n_drifts(rng)
            plan = build_drift_plan(N_SAMPLES, n_drifts, rng, width_ref=width)

            csv_name = f"recurring_gradual_sea100k_{g_tag}.csv"
            txt_name = f"recurring_gradual_sea100k_{g_tag}_drift_times.txt"
            csv_path = os.path.join(gradual_dir, csv_name)
            txt_path = os.path.join(gradual_dir, txt_name)

            chunks, _meta = make_multi_gradual_drift_stream(
                n_samples=N_SAMPLES,
                seed=seed,
                plan=plan,
                transition_width=width,
            )
            xs, ys = extract_stream_from_chunks(chunks, n_samples=N_SAMPLES)
            assert len(xs) == N_SAMPLES
            write_dataset_csv(csv_path, xs, ys)
            intervals = drift_intervals_for_positions(
                plan["drift_positions"], width, N_SAMPLES
            )
            write_drift_times_txt(txt_path, intervals)

            rows_summary.append(
                _summary_row(
                    "gradual",
                    tier,
                    gradual_params,
                    run_id,
                    os.path.join("gradual_drift", tier, csv_name),
                    os.path.join("gradual_drift", tier, txt_name),
                    seed,
                )
            )

    summary_path = os.path.join(out_dir, "summary.csv")
    fieldnames = [
        "drift_type",
        "sensitivity",
        "sensitivity_multiplier",
        "run_id",
        "csv_filename",
        "drift_times_filename",
        "random_seed",
    ]
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows_summary:
            w.writerow(row)

    print(
        f"已寫入 {sudden_base}/{{low,medium,high}}、"
        f"{gradual_base}/{{low,medium,high}} 與 {summary_path}（共 {len(rows_summary)} 組）"
    )


if __name__ == "__main__":
    main()
