"""
Regression concept drift（River + 手動 incremental / sudden）

- sudden  → 手動 Friedman 係數跳變（River lea 無幅度旋鈕；跳變幅度 × sensitivity）
- gradual → synth.FriedmanDrift(drift_type='gsg')，transition_window 依 tier 縮放
- incremental：手動迴圈；INCR_PARAM_STEP 依 tier 縮放

輸出：sudden_drift / gradual_drift / incremental_drift 各 {low,medium,high}/ 下 10 組 CSV + drift_times.txt + summary.csv。
"""

from __future__ import annotations

import csv
import glob
import math
import os
import random
import secrets
import sys
from typing import Any

import numpy as np
from river.datasets import synth

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from drift_common.profiles import resolve
from drift_common.sensitivity import SENSITIVITY_TIERS, scale_width_for_transition

N_SAMPLES = 100_000
N_FEATURES = 10
N_RUNS = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUDDEN_DIR = os.path.join(BASE_DIR, "sudden_drift")
GRADUAL_DIR = os.path.join(BASE_DIR, "gradual_drift")
INCR_DIR = os.path.join(BASE_DIR, "incremental_drift")

INCR_N_DRIFTS_MIN = 1
INCR_N_DRIFTS_MAX = 5
INCR_MIN_SEGMENT_LEN = 8000

COEFF_INIT = np.array([10.0, 20.0, 10.0, 5.0], dtype=float)
COEFF_LO = np.array([4.0, 8.0, 4.0, 2.0], dtype=float)
COEFF_HI = np.array([22.0, 32.0, 18.0, 12.0], dtype=float)


def _random_partition_multinomial(
    rng: np.random.Generator,
    n: int,
    k: int,
    min_len: int,
) -> list[int]:
    if n < k * min_len:
        raise ValueError(f"n={n} 太小，無法分成 {k} 段且每段至少 {min_len}")
    remaining = n - k * min_len
    extras = rng.multinomial(remaining, [1.0 / k] * k)
    return [min_len + int(x) for x in extras]


def take_dataset(dataset: Any, n: int) -> tuple[list, list]:
    xs: list = []
    ys: list = []
    for i, (x, y) in enumerate(dataset):
        if i >= n:
            break
        xs.append(x)
        ys.append(float(y))
    return xs, ys


def write_csv_regression(path: str, xs: list, ys: list) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    header = [f"x{i}" for i in range(N_FEATURES)] + ["y"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for x, yi in zip(xs, ys):
            row = [x[i] for i in range(N_FEATURES)] + [yi]
            w.writerow(row)


def write_drift_times(path: str, intervals: list[list[int]]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(repr(intervals))


def _friedman_y(x: dict[int, float], coeff: np.ndarray, rng_py: random.Random) -> float:
    a, b, c, d = coeff.tolist()
    return (
        a * math.sin(math.pi * x[0] * x[1])
        + b * (x[2] - 0.5) ** 2
        + c * x[3]
        + d * x[4]
        + rng_py.gauss(0.0, 1.0)
    )


def _random_target_coeff(rng_np: np.random.Generator) -> np.ndarray:
    u = rng_np.beta(2.0, 2.0, size=4)
    return COEFF_LO + u * (COEFF_HI - COEFF_LO)


def _sudden_drift_positions(seed: int, n_samples: int) -> tuple[int, int, int]:
    rng = np.random.default_rng(seed)
    p1 = int(rng.integers(8_000, 22_000))
    p2 = int(rng.integers(28_000, 48_000))
    p3 = int(rng.integers(58_000, 92_000))
    p1, p2, p3 = sorted([p1, p2, p3])
    p3 = min(p3, n_samples - 5)
    if p2 <= p1:
        p2 = p1 + 15_000
    if p3 <= p2:
        p3 = min(p2 + 18_000, n_samples - 5)
    return p1, p2, p3


def generate_sudden_manual_friedman(
    seed: int,
    n_samples: int,
    jump_scale: float,
) -> tuple[list, list, list[list[int]]]:
    """三點係數跳變；jump_scale 為 sensitivity multiplier（0.5 / 1 / 2）。"""
    rng_py = random.Random(seed)
    rng_np = np.random.default_rng(seed)
    p1, p2, p3 = _sudden_drift_positions(seed, n_samples)
    jump_at = sorted({p1, p2, p3})

    coeff = COEFF_INIT.copy()
    xs: list = []
    ys: list = []
    times = [
        [p1, min(p1 + 1, n_samples - 1)],
        [p2, min(p2 + 1, n_samples - 1)],
        [p3, min(p3 + 1, n_samples - 1)],
    ]

    for t in range(n_samples):
        if t in jump_at:
            target = _random_target_coeff(rng_np)
            coeff = coeff + jump_scale * (target - coeff)
            coeff = np.clip(coeff, COEFF_LO, COEFF_HI)

        x = {i: rng_py.uniform(0.0, 1.0) for i in range(N_FEATURES)}
        xs.append(x)
        ys.append(_friedman_y(x, coeff, rng_py))

    return xs, ys, times


def build_friedman_gradual_gsg(
    seed: int,
    n_samples: int,
    tier: str,
) -> tuple[synth.FriedmanDrift, list[list[int]]]:
    rng = np.random.default_rng(seed)
    p1 = int(rng.integers(10_000, 28_000))
    p2 = int(rng.integers(42_000, 72_000))
    if p2 <= p1 + 18_000:
        p2 = p1 + 22_000
    p2 = min(p2, n_samples - 5)
    gap = p2 - p1
    tw = int(rng.integers(8000, min(14_000, max(gap // 2, 4000))))
    tw = min(tw, gap - 2)
    tw = max(500, tw)
    if tw > gap - 1:
        tw = max(500, (gap - 1) // 2)
    tw = scale_width_for_transition(tw, tier)
    ds = synth.FriedmanDrift(
        drift_type="gsg",
        position=(p1, p2),
        transition_window=tw,
        seed=seed,
    )
    t_end1 = min(n_samples - 1, p1 + tw - 1)
    t_end2 = min(n_samples - 1, p2 + tw - 1)
    times = [[p1, t_end1], [p2, t_end2]]
    return ds, times


def generate_incremental_manual_friedman(
    seed: int,
    n_samples: int,
    param_step: float,
    jump_scale: float,
) -> tuple[list, list, list[list[int]]]:
    rng_py = random.Random(seed)
    rng_np = np.random.default_rng(seed)

    n_drifts = int(rng_np.integers(INCR_N_DRIFTS_MIN, INCR_N_DRIFTS_MAX + 1))
    seg_lens = _random_partition_multinomial(
        rng_np, n_samples, n_drifts + 1, INCR_MIN_SEGMENT_LEN
    )

    coeff = COEFF_INIT.copy()
    lo, hi = COEFF_LO, COEFF_HI

    xs: list = []
    ys: list = []
    drift_intervals: list[list[int]] = []
    t = 0
    for seg_i, seg_len in enumerate(seg_lens):
        seg_len = int(seg_len)
        has_target = seg_i < len(seg_lens) - 1
        if has_target:
            target = _random_target_coeff(rng_np)
            delta = jump_scale * (target - coeff) / max(1, seg_len)
            drift_intervals.append([t, min(n_samples - 1, t + seg_len - 1)])
        else:
            target = None
            delta = np.zeros(4, dtype=float)

        for _ in range(seg_len):
            if t >= n_samples:
                break
            x = {i: rng_py.uniform(0.0, 1.0) for i in range(N_FEATURES)}
            xs.append(x)
            ys.append(_friedman_y(x, coeff, rng_py))
            noise = rng_np.normal(0.0, param_step, size=4)
            coeff = coeff + delta + noise
            coeff = np.clip(coeff, lo, hi)
            t += 1

        if has_target and target is not None:
            coeff = np.clip(target, lo, hi)

    return xs, ys, drift_intervals


def _clear_legacy_flat_files(drift_dir: str) -> None:
    for pat in ("*.csv", "*_drift_times.txt"):
        for fp in glob.glob(os.path.join(drift_dir, pat)):
            try:
                os.remove(fp)
            except OSError:
                pass


def _summary_row(
    label: str,
    tier: str,
    params: dict,
    run_id: int,
    drift_folder: str,
    csv_name: str,
    txt_name: str,
    seed: int,
) -> dict:
    return {
        "drift_type": label,
        "sensitivity": tier,
        "sensitivity_multiplier": params["sensitivity_multiplier"],
        "run_id": run_id,
        "csv_filename": f"{drift_folder}/{tier}/{csv_name}",
        "drift_times_filename": f"{drift_folder}/{tier}/{txt_name}",
        "random_seed": seed,
    }


def main() -> None:
    for d in (SUDDEN_DIR, GRADUAL_DIR, INCR_DIR):
        _clear_legacy_flat_files(d)
        os.makedirs(d, exist_ok=True)

    rows: list[dict] = []
    prefix_by_label = {
        "sudden": "recurring_sudden_friedman_100k",
        "gradual": "recurring_gradual_friedman_100k",
        "incremental": "recurring_incremental_friedman_100k",
    }
    folder_by_label = {
        "sudden": "sudden_drift",
        "gradual": "gradual_drift",
        "incremental": "incremental_drift",
    }
    for tier in SENSITIVITY_TIERS:
        sudden_p = resolve("regression", "sudden", tier)
        out_sudden = os.path.join(SUDDEN_DIR, tier)
        os.makedirs(out_sudden, exist_ok=True)
        for run_id in range(1, N_RUNS + 1):
            g_tag = f"g{run_id - 1:02d}"
            seed = secrets.randbelow(2**32)
            xs, ys, intervals = generate_sudden_manual_friedman(
                seed, N_SAMPLES, sudden_p["jump_scale"]
            )
            csv_name = f"{prefix_by_label['sudden']}_{g_tag}.csv"
            txt_name = f"{prefix_by_label['sudden']}_{g_tag}_drift_times.txt"
            write_csv_regression(os.path.join(out_sudden, csv_name), xs, ys)
            write_drift_times(os.path.join(out_sudden, txt_name), intervals)
            rows.append(
                _summary_row(
                    "sudden", tier, sudden_p, run_id,
                    folder_by_label["sudden"], csv_name, txt_name, seed,
                )
            )

    for tier in SENSITIVITY_TIERS:
        gradual_p = resolve("regression", "gradual", tier)
        out_gradual = os.path.join(GRADUAL_DIR, tier)
        os.makedirs(out_gradual, exist_ok=True)
        for run_id in range(1, N_RUNS + 1):
            g_tag = f"g{run_id - 1:02d}"
            seed = secrets.randbelow(2**32)
            dataset, intervals = build_friedman_gradual_gsg(seed, N_SAMPLES, tier)
            xs, ys = take_dataset(dataset, N_SAMPLES)
            csv_name = f"{prefix_by_label['gradual']}_{g_tag}.csv"
            txt_name = f"{prefix_by_label['gradual']}_{g_tag}_drift_times.txt"
            write_csv_regression(os.path.join(out_gradual, csv_name), xs, ys)
            write_drift_times(os.path.join(out_gradual, txt_name), intervals)
            rows.append(
                _summary_row(
                    "gradual", tier, gradual_p, run_id,
                    folder_by_label["gradual"], csv_name, txt_name, seed,
                )
            )

    for tier in SENSITIVITY_TIERS:
        incr_p = resolve("regression", "incremental", tier)
        out_incr = os.path.join(INCR_DIR, tier)
        os.makedirs(out_incr, exist_ok=True)
        for run_id in range(1, N_RUNS + 1):
            g_tag = f"g{run_id - 1:02d}"
            seed = secrets.randbelow(2**32)
            xs, ys, intervals = generate_incremental_manual_friedman(
                seed,
                N_SAMPLES,
                incr_p["param_step"],
                incr_p["jump_scale"],
            )
            csv_name = f"{prefix_by_label['incremental']}_{g_tag}.csv"
            txt_name = f"{prefix_by_label['incremental']}_{g_tag}_drift_times.txt"
            write_csv_regression(os.path.join(out_incr, csv_name), xs, ys)
            write_drift_times(os.path.join(out_incr, txt_name), intervals)
            rows.append(
                _summary_row(
                    "incremental", tier, incr_p, run_id,
                    folder_by_label["incremental"], csv_name, txt_name, seed,
                )
            )

    summary_path = os.path.join(BASE_DIR, "summary.csv")
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
        for row in rows:
            w.writerow(row)

    print(f"完成：{BASE_DIR}（{len(rows)} 組 CSV + drift_times + summary.csv）")


if __name__ == "__main__":
    main()
