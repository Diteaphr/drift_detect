"""
Standalone calibration of adwin / seed / seqdrift2 on HF error stream.

Each detector runs directly on the 0/1 error stream produced by a
HoeffdingForestModel (n_trees=5, lambda_poisson=6, seed=42).
No ECPF pipeline — the model keeps learning online without any swap.

Calibration logic (per stream, then median across g00-g04):
  warning_param = param giving minimum N > N_actual
                  (just over-sensitive: fires slightly more than GT)
  confirm_param = param giving maximum N <= N_actual
                  (just conservative: fires at most as often as GT)

Delta sensitivity direction:
  adwin      : smaller delta  → more sensitive
  seed       : larger  delta  → more sensitive
  seqdrift2  : larger  delta  → more sensitive

Streams:
  Calibration : data/recurring_drift/recurring_sud_sea100k_g00~g04.csv
  Evaluation  : data/recurring_drift/recurring_sud_sea100k_g05~g09.csv
"""

from __future__ import annotations

import csv
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from river import drift as river_drift

from detectors.meta_ecpf.seed import SEEDDetector
from detectors.meta_ecpf.seqdrift2 import SeqDrift2Detector
from src.ecpf import load_drift_intervals_file
from src.models.hoeffding_forest import HoeffdingForestModel
from src.metrics.detection_delay import compute_detection_delays
from src.metrics.correct_detection import (
    DEFAULT_PERTURBATION_EXTENSION,
    build_perturbation_intervals,
    compute_correct_detection,
)
from src.metrics.detection_evaluation import compute_count_score

DATA_DIR = ROOT / "data" / "recurring_drift"
OUT_DIR = ROOT / "outputs" / "calibration_standalone"
WARM_START = 200
TOLERANCE = DEFAULT_PERTURBATION_EXTENSION  # 2000 samples
CALIB_SUFFIXES = [f"g0{i}" for i in range(5)]
EVAL_SUFFIXES = [f"g0{i}" for i in range(5, 10)]

HF_KWARGS: Dict[str, Any] = {"n_trees": 5, "lambda_poisson": 6.0, "seed": 42}


# ---------------------------------------------------------------------------
# Detector specs
# ---------------------------------------------------------------------------

@dataclass
class DetectorSpec:
    name: str
    delta_grid: List[float]
    make: Callable[[float], Any]   # factory: delta → detector with .update(v) → bool


def _make_adwin(delta: float):
    class _Wrapper:
        def __init__(self):
            self._d = river_drift.ADWIN(delta=delta, grace_period=30)

        def update(self, value: float) -> bool:
            self._d.update(value)
            return bool(self._d.drift_detected)

        def reset(self):
            self._d = river_drift.ADWIN(delta=delta, grace_period=30)

    return _Wrapper()


def _make_seed(delta: float):
    return SEEDDetector(role="drift", delta=delta)


def _make_seqdrift2(delta: float):
    return SeqDrift2Detector(role="drift", delta=delta, seed=42)


DETECTORS: List[DetectorSpec] = [
    DetectorSpec(
        name="adwin",
        # smaller delta → more sensitive
        delta_grid=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3],
        make=_make_adwin,
    ),
    DetectorSpec(
        name="seqdrift2",
        # larger delta → more sensitive (Bernstein bound scale)
        delta_grid=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50],
        make=_make_seqdrift2,
    ),
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _stream_paths(suffixes: List[str]) -> List[Tuple[Path, Path]]:
    pairs = []
    for sfx in suffixes:
        csv_p = DATA_DIR / f"recurring_sud_sea100k_{sfx}.csv"
        txt_p = DATA_DIR / f"recurring_sud_sea100k_{sfx}_drift_times.txt"
        if not csv_p.exists():
            print(f"[WARN] missing: {csv_p}", file=sys.stderr)
            continue
        pairs.append((csv_p, txt_p))
    return pairs


def _load_stream(csv_path: Path, txt_path: Path):
    """Return (X, y, drift_starts, drift_intervals)."""
    import pandas as pd
    from src.ecpf import load_drift_times_file

    df = pd.read_csv(csv_path)
    y_col = df.columns[-1]
    X = df.drop(columns=[y_col]).values.astype(float)
    y = df[y_col].values

    drift_starts = load_drift_times_file(str(txt_path))
    drift_intervals = load_drift_intervals_file(str(txt_path))
    return X, y, drift_starts, drift_intervals


# ---------------------------------------------------------------------------
# Core: run one detector on one stream
# ---------------------------------------------------------------------------

def _run_detector(
    X: np.ndarray,
    y: np.ndarray,
    delta: float,
    spec: DetectorSpec,
) -> List[int]:
    """Run detector on error stream produced by HF model. Return fire timestamps."""
    model = HoeffdingForestModel(**HF_KWARGS)
    detector = spec.make(delta)
    fire_times: List[int] = []

    for i in range(len(y)):
        x_dict = {f"f{j}": float(v) for j, v in enumerate(X[i])}
        y_true = int(y[i])

        if i < WARM_START:
            model.learn_one(x_dict, y_true)
            continue

        y_pred = model.predict_one(x_dict)
        if y_pred is None:
            y_pred = 0
        err = 1.0 if int(y_pred) != y_true else 0.0
        model.learn_one(x_dict, y_true)

        fired = detector.update(err)
        if fired:
            fire_times.append(i)

    return fire_times


# ---------------------------------------------------------------------------
# Phase 1: calibration
# ---------------------------------------------------------------------------

def _find_warning_confirm(
    sweep: List[Tuple[float, int]],
    n_actual: int,
    grid: List[float],
) -> Tuple[float, float]:
    """
    sweep : [(delta, N_fires), ...]
    Returns (warning_param, confirm_param).
      warning_param : param giving min N > N_actual  (just over-sensitive)
      confirm_param : param giving max N <= N_actual (just conservative)
    Falls back to grid extremes when no candidate exists.
    """
    over = [(N, d) for d, N in sweep if N > n_actual]
    under = [(N, d) for d, N in sweep if N <= n_actual]

    warning_param = min(over, key=lambda t: t[0])[1] if over else grid[0]
    confirm_param = max(under, key=lambda t: t[0])[1] if under else grid[-1]
    return warning_param, confirm_param


def calibrate(
    spec: DetectorSpec,
    calib_paths: List[Tuple[Path, Path]],
) -> Tuple[float, float]:
    """Return (warning_param, confirm_param) as median across calib streams."""
    warn_per_stream: List[float] = []
    conf_per_stream: List[float] = []

    for csv_path, txt_path in calib_paths:
        X, y, drift_starts, _ = _load_stream(csv_path, txt_path)
        n_actual = len(drift_starts)
        sweep: List[Tuple[float, int]] = []

        for delta in spec.delta_grid:
            fires = _run_detector(X, y, delta, spec)
            n_fires = len(fires)
            score = compute_count_score(n_fires, n_actual) or 0.0
            print(
                f"  [calib] {spec.name} | {csv_path.name} | "
                f"delta={delta:<5g} N_fire={n_fires:3d} N_actual={n_actual:2d} "
                f"count_score={score:.3f}",
                flush=True,
            )
            sweep.append((delta, n_fires))

        w, c = _find_warning_confirm(sweep, n_actual, spec.delta_grid)
        warn_per_stream.append(w)
        conf_per_stream.append(c)
        print(
            f"  {csv_path.name}: warning_param={w}  confirm_param={c}",
            flush=True,
        )

    warning_param = float(np.median(warn_per_stream))
    confirm_param = float(np.median(conf_per_stream))
    warning_param = min(spec.delta_grid, key=lambda v: abs(v - warning_param))
    confirm_param = min(spec.delta_grid, key=lambda v: abs(v - confirm_param))
    return warning_param, confirm_param


# ---------------------------------------------------------------------------
# Phase 2: evaluation
# ---------------------------------------------------------------------------

@dataclass
class EvalResult:
    count_score: float
    mean_delay: float
    cd_pct: Optional[float]
    n_fires: int
    n_actual: int


def _fmt(v: Any, fmt: str = ".3f") -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    return format(v, fmt)


def evaluate(
    spec: DetectorSpec,
    delta: float,
    eval_paths: List[Tuple[Path, Path]],
    label: str,
) -> List[EvalResult]:
    results = []
    for csv_path, txt_path in eval_paths:
        X, y, drift_starts, drift_intervals = _load_stream(csv_path, txt_path)
        fires = _run_detector(X, y, delta, spec)

        n_actual = len(drift_starts)
        score = compute_count_score(len(fires), n_actual) or 0.0
        delay_info = compute_detection_delays(fires, drift_starts, tolerance=TOLERANCE)
        perturbation = build_perturbation_intervals(drift_intervals, extension=TOLERANCE)
        cd = compute_correct_detection(fires, perturbation)

        results.append(EvalResult(
            count_score=score,
            mean_delay=delay_info["mean_delay"],
            cd_pct=cd.score_percent,
            n_fires=len(fires),
            n_actual=n_actual,
        ))
        print(
            f"  [eval/{label}] {spec.name} | {csv_path.name} | "
            f"delta={delta:<5g} N_fire={len(fires):3d} N_actual={n_actual:2d} "
            f"count_score={score:.3f} "
            f"avg_delay={_fmt(delay_info['mean_delay'], '.0f')} "
            f"CD%={_fmt(cd.score_percent, '.1f')}",
            flush=True,
        )
    return results


def _agg(results: List[EvalResult]) -> Dict[str, str]:
    scores = [r.count_score for r in results]
    delays = [r.mean_delay for r in results if not math.isnan(r.mean_delay)]
    cds = [r.cd_pct for r in results if r.cd_pct is not None]
    return {
        "count_score": _fmt(np.mean(scores) if scores else math.nan),
        "CD%": _fmt(np.mean(cds) if cds else math.nan, ".1f"),
        "avg_delay": _fmt(np.mean(delays) if delays else math.nan, ".0f"),
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

FIELDNAMES = [
    "detector",
    "warning_param", "warn_count_score", "warn_CD%", "warn_avg_delay",
    "confirm_param", "conf_count_score", "conf_CD%", "conf_avg_delay",
]


def print_summary(rows: List[Dict[str, str]]) -> None:
    widths = {f: max(len(f), max(len(str(r[f])) for r in rows)) for f in FIELDNAMES}
    header = "  ".join(f.ljust(widths[f]) for f in FIELDNAMES)
    sep = "  ".join("-" * widths[f] for f in FIELDNAMES)
    print("\n=== Standalone Detector Calibration ===")
    print(f"Calibration: g00–g04   Evaluation: g05–g09   tolerance={TOLERANCE}")
    print(header)
    print(sep)
    for r in rows:
        print("  ".join(str(r[f]).ljust(widths[f]) for f in FIELDNAMES))


def save_csv(rows: List[Dict[str, str]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "calibration_standalone_summary.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    calib_paths = _stream_paths(CALIB_SUFFIXES)
    eval_paths = _stream_paths(EVAL_SUFFIXES)
    if not calib_paths:
        sys.exit("No calibration streams found.")

    summary_rows: List[Dict[str, str]] = []

    for spec in DETECTORS:
        print(f"\n[{spec.name}] Calibrating on {len(calib_paths)} streams...", flush=True)
        warning_param, confirm_param = calibrate(spec, calib_paths)
        print(f"  → warning_param={warning_param}  confirm_param={confirm_param}", flush=True)

        print(f"\n[{spec.name}] Evaluating warning_param={warning_param}...", flush=True)
        warn_results = evaluate(spec, warning_param, eval_paths, label="warning")

        print(f"\n[{spec.name}] Evaluating confirm_param={confirm_param}...", flush=True)
        conf_results = evaluate(spec, confirm_param, eval_paths, label="confirm")

        warn_agg = _agg(warn_results)
        conf_agg = _agg(conf_results)

        summary_rows.append({
            "detector": spec.name,
            "warning_param": warning_param,
            "warn_count_score": warn_agg["count_score"],
            "warn_CD%": warn_agg["CD%"],
            "warn_avg_delay": warn_agg["avg_delay"],
            "confirm_param": confirm_param,
            "conf_count_score": conf_agg["count_score"],
            "conf_CD%": conf_agg["CD%"],
            "conf_avg_delay": conf_agg["avg_delay"],
        })

    print_summary(summary_rows)
    save_csv(summary_rows)


if __name__ == "__main__":
    main()
