"""
Check that g00 drift effect increases: low < medium < high.

Classification: rolling majority baseline prequential error jump at drift intervals.
Regression: rolling MSE jump at drift intervals.
"""

from __future__ import annotations

import argparse
import ast
import csv
from pathlib import Path

import numpy as np
import pandas as pd

import sys

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from drift_common.sensitivity import SENSITIVITY_TIERS

REPO = Path(__file__).resolve().parent.parent
WINDOW = 2000
G_TAG = "g00"


def load_intervals(path: Path) -> list[list[int]]:
    if not path.is_file():
        return []
    return ast.literal_eval(path.read_text(encoding="utf-8").strip())


def drift_effect_classification(csv_path: Path, intervals: list[list[int]]) -> float:
    df = pd.read_csv(csv_path)
    y = df["y"].to_numpy()
    n = len(y)
    if n == 0 or not intervals:
        return 0.0

    maj = []
    for i in range(n):
        start = max(0, i - WINDOW + 1)
        window = y[start : i + 1]
        vals, counts = np.unique(window, return_counts=True)
        maj.append(vals[np.argmax(counts)])
    maj = np.array(maj)
    err = (y != maj).astype(float)

    deltas: list[float] = []
    margin = WINDOW
    for s, e in intervals:
        s, e = int(s), int(e)
        before_start = max(0, s - margin)
        before_end = max(0, s - 1)
        after_start = min(n - 1, e + 1)
        after_end = min(n - 1, e + margin)
        if before_end <= before_start or after_end <= after_start:
            continue
        before_err = err[before_start : before_end + 1].mean()
        after_err = err[after_start : after_end + 1].mean()
        deltas.append(abs(float(after_err - before_err)))

    return float(np.mean(deltas)) if deltas else 0.0


def drift_effect_regression(csv_path: Path, intervals: list[list[int]]) -> float:
    df = pd.read_csv(csv_path)
    y = df["y"].to_numpy(dtype=float)
    n = len(y)
    if n == 0 or not intervals:
        return 0.0

    roll_mean = pd.Series(y).rolling(WINDOW, min_periods=1).mean().to_numpy()
    sq_err = (y - roll_mean) ** 2

    deltas: list[float] = []
    margin = WINDOW
    for s, e in intervals:
        s, e = int(s), int(e)
        before_start = max(0, s - margin)
        before_end = max(0, s - 1)
        after_start = min(n - 1, e + 1)
        after_end = min(n - 1, e + margin)
        if before_end <= before_start or after_end <= after_start:
            continue
        before_mse = sq_err[before_start : before_end + 1].mean()
        after_mse = sq_err[after_start : after_end + 1].mean()
        deltas.append(abs(float(after_mse - before_mse)))

    return float(np.mean(deltas)) if deltas else 0.0


def _binary_paths(drift_type: str, tier: str) -> tuple[Path, Path]:
    base = REPO / "binary classification" / f"{drift_type}_drift" / tier
    stem = f"recurring_{drift_type}_sea100k_{G_TAG}"
    return base / f"{stem}.csv", base / f"{stem}_drift_times.txt"


def _multiclass_paths(drift_type: str, tier: str) -> tuple[Path, Path]:
    base = REPO / "multi classification" / f"{drift_type}_drift" / tier
    stem = f"recurring_{drift_type}_rbf4_100k_{G_TAG}"
    return base / f"{stem}.csv", base / f"{stem}_drift_times.txt"


def _regression_paths(drift_type: str, tier: str) -> tuple[Path, Path]:
    base = REPO / "regression" / f"{drift_type}_drift" / tier
    stem = f"recurring_{drift_type}_friedman_100k_{G_TAG}"
    return base / f"{stem}.csv", base / f"{stem}_drift_times.txt"


def evaluate_task(
    task: str,
    drift_types: list[str],
    path_fn,
    effect_fn,
) -> list[dict]:
    rows: list[dict] = []
    for drift_type in drift_types:
        effects: dict[str, float] = {}
        for tier in SENSITIVITY_TIERS:
            csv_p, dt_p = path_fn(drift_type, tier)
            effects[tier] = effect_fn(csv_p, load_intervals(dt_p))

        mono = effects["low"] < effects["medium"] < effects["high"]
        rows.append(
            {
                "task": task,
                "drift_type": drift_type,
                "delta_low": effects["low"],
                "delta_medium": effects["medium"],
                "delta_high": effects["high"],
                "monotonic": mono,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate low < medium < high drift effect on g00")
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO / "drift_common" / "sensitivity_validation_report.csv",
    )
    args = parser.parse_args()

    rows: list[dict] = []
    rows.extend(
        evaluate_task(
            "binary",
            ["sudden", "gradual"],
            _binary_paths,
            drift_effect_classification,
        )
    )
    rows.extend(
        evaluate_task(
            "multiclass",
            ["sudden", "gradual", "incremental"],
            _multiclass_paths,
            drift_effect_classification,
        )
    )
    rows.extend(
        evaluate_task(
            "regression",
            ["sudden", "gradual", "incremental"],
            _regression_paths,
            drift_effect_regression,
        )
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            w.writeheader()
            w.writerows(rows)

    print(f"Report: {args.out}")
    for r in rows:
        status = "OK" if r["monotonic"] else "FAIL"
        print(
            f"  [{status}] {r['task']}/{r['drift_type']}: "
            f"low={r['delta_low']:.6f} med={r['delta_medium']:.6f} high={r['delta_high']:.6f}"
        )

    failed = [r for r in rows if not r["monotonic"]]
    if failed:
        print(f"\nWarning: {len(failed)} configuration(s) did not satisfy low < medium < high on g00.")


if __name__ == "__main__":
    main()
