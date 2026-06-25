"""Calibrate detector sensitivity so N_detect ≈ N_actual, then measure detection delay.

Calibration streams : data/recurring_drift/ g00–g04
Evaluation streams  : data/recurring_drift/ g05–g09

For each detector:
  1. Sweep one sensitivity parameter over a grid (calibration streams).
  2. Pick the param value that maximises count_score = 1 - |N_warn - N_actual| / N_actual,
     using the median-best param across the 5 calibration streams.
  3. At that calibrated param, evaluate on the 5 held-out streams:
       - count_score  (N_warn vs N_actual)
       - avg_delay    (samples from true drift start to first warning in tolerance window)
       - CD%          (correct detection %)
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import PipelineConfig
from src.ecpf import load_drift_times_file, load_drift_intervals_file
from src.pipeline import ConceptDriftPipeline, load_recurring_stream_pair
from src.metrics.detection_delay import compute_detection_delays
from src.metrics.correct_detection import (
    DEFAULT_PERTURBATION_EXTENSION,
    build_perturbation_intervals,
    compute_correct_detection,
)
from src.metrics.detection_evaluation import compute_count_score

DATA_DIR = ROOT / "data" / "recurring_drift"
OUT_DIR = ROOT / "outputs" / "calibration_comparison"
WARM_START = 200
TOLERANCE = DEFAULT_PERTURBATION_EXTENSION  # 2000 samples


# ---------------------------------------------------------------------------
# Detector specifications
# ---------------------------------------------------------------------------

@dataclass
class DetectorSpec:
    name: str
    signal_mode: str
    param_attr: str           # PipelineConfig attribute to sweep
    param_grid: List[float]
    extra_attrs: Dict[str, Any] = field(default_factory=dict)
    delta_w_ratio: Optional[float] = None  # if set, also sets detector_delta_w = param * ratio


DETECTORS: List[DetectorSpec] = [
    DetectorSpec(
        name="dual_adwin",
        signal_mode="dual_adwin",
        param_attr="detector_delta",
        param_grid=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3],
        delta_w_ratio=2.0,  # detector_delta_w = delta * 2
    ),
    DetectorSpec(
        name="meta_ecpf_hcdt",
        signal_mode="meta_ecpf_hcdt",
        param_attr="ecpf_hcdt_detection_delta",
        param_grid=[0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1],
    ),
    DetectorSpec(
        name="meta_ecpf_gddm",
        signal_mode="meta_ecpf_gddm",
        param_attr="ecpf_gddm_warning_alpha",
        param_grid=[0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50],
        extra_attrs={"ecpf_gddm_drift_alpha": None},  # set to warning_alpha / 10 dynamically
    ),
    DetectorSpec(
        name="meta_ecpf_hier_parallel",
        signal_mode="meta_ecpf_hier_parallel",
        param_attr="ecpf_hier_validation_gap_threshold",
        param_grid=[0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10],
    ),
]

CALIB_SUFFIXES = [f"g0{i}" for i in range(5)]   # g00–g04
EVAL_SUFFIXES = [f"g0{i}" for i in range(5, 10)]  # g05–g09


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stream_paths(suffixes: List[str]) -> List[Tuple[Path, Path]]:
    """Return (csv_path, drift_times_path) pairs for the given stream suffixes."""
    pairs = []
    for sfx in suffixes:
        csv = DATA_DIR / f"recurring_sud_sea100k_{sfx}.csv"
        txt = DATA_DIR / f"recurring_sud_sea100k_{sfx}_drift_times.txt"
        if not csv.exists():
            print(f"[WARN] missing stream: {csv}", file=sys.stderr)
            continue
        pairs.append((csv, txt))
    return pairs


def _build_config(spec: DetectorSpec, param_value: float) -> PipelineConfig:
    cfg = PipelineConfig()
    cfg.use_ecpf = True
    cfg.model_type = "hf"
    cfg.ecpf_signal_mode = spec.signal_mode
    cfg.ecpf_oracle_true_drift_times = None  # never oracle during calibration

    setattr(cfg, spec.param_attr, param_value)

    if spec.delta_w_ratio is not None:
        cfg.detector_delta_w = param_value * spec.delta_w_ratio

    for attr, val in spec.extra_attrs.items():
        if val is None:
            # dynamic: gddm drift_alpha = warning_alpha / 10
            if attr == "ecpf_gddm_drift_alpha":
                setattr(cfg, attr, param_value / 10.0)
        else:
            setattr(cfg, attr, val)

    return cfg


def _run_stream(csv_path: Path, txt_path: Path, cfg: PipelineConfig) -> Tuple[List[int], List[int], List[Tuple[int, int]]]:
    """Run pipeline on one stream. Returns (warning_timestamps, drift_starts, drift_intervals)."""
    X, y, drift_starts = load_recurring_stream_pair(str(csv_path), str(txt_path))
    drift_intervals = load_drift_intervals_file(str(txt_path))

    pipeline = ConceptDriftPipeline(cfg)
    pipeline.warm_start(X[:WARM_START], y[:WARM_START])
    warning_timestamps: List[int] = []
    for i in range(WARM_START, len(y)):
        _, detections, _ = pipeline.step(X[i], y[i], index=i)
        for d in detections:
            if getattr(d, "timestamp", None) is not None:
                warning_timestamps.append(int(d.timestamp))

    # Backward compatibility: old pipeline versions exposed warning_timestamps.
    if not warning_timestamps and hasattr(pipeline, "warning_timestamps"):
        warning_timestamps = [int(t) for t in getattr(pipeline, "warning_timestamps")]

    return warning_timestamps, drift_starts, drift_intervals


def _print_stream_done(
    phase: str,
    detector: str,
    csv_path: Path,
    param: float,
    n_warnings: int,
    n_actual: int,
    count_score: float,
    *,
    mean_delay: Optional[float] = None,
    cd_pct: Optional[float] = None,
) -> None:
    msg = (
        f"  [{phase}] {detector} | {csv_path.name} | param={param:g} | "
        f"N_warn={n_warnings} N_actual={n_actual} count_score={count_score:.3f}"
    )
    if mean_delay is not None:
        delay_str = _fmt(mean_delay, ".0f")
        cd_str = _fmt(cd_pct, ".1f")
        msg += f" avg_delay={delay_str} CD%={cd_str}"
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Phase 1: calibration
# ---------------------------------------------------------------------------

def calibrate(spec: DetectorSpec, calib_paths: List[Tuple[Path, Path]]) -> float:
    """Return the median-best param value across calibration streams."""
    best_per_stream: List[float] = []

    for csv_path, txt_path in calib_paths:
        best_score = -1.0
        best_param = spec.param_grid[0]

        for param in spec.param_grid:
            cfg = _build_config(spec, param)
            warnings, drift_starts, _ = _run_stream(csv_path, txt_path, cfg)
            n_actual = len(drift_starts)
            score = compute_count_score(len(warnings), n_actual) or 0.0
            _print_stream_done(
                "calibrate",
                spec.name,
                csv_path,
                param,
                len(warnings),
                n_actual,
                score,
            )
            if score > best_score:
                best_score = score
                best_param = param

        best_per_stream.append(best_param)
        print(
            f"  {csv_path.name}: best_param={best_param}  count_score={best_score:.3f}",
            flush=True,
        )

    calibrated = float(np.median(best_per_stream))
    # snap to nearest grid value
    calibrated = min(spec.param_grid, key=lambda v: abs(v - calibrated))
    return calibrated


# ---------------------------------------------------------------------------
# Phase 2: evaluation
# ---------------------------------------------------------------------------

@dataclass
class StreamResult:
    count_score: float
    mean_delay: float
    cd_pct: Optional[float]
    n_warnings: int
    n_actual: int
    n_matched: int


def evaluate_at_param(
    spec: DetectorSpec,
    param: float,
    eval_paths: List[Tuple[Path, Path]],
) -> List[StreamResult]:
    results = []
    for csv_path, txt_path in eval_paths:
        cfg = _build_config(spec, param)
        warnings, drift_starts, drift_intervals = _run_stream(csv_path, txt_path, cfg)

        n_actual = len(drift_starts)
        score = compute_count_score(len(warnings), n_actual) or 0.0

        delay_info = compute_detection_delays(warnings, drift_starts, tolerance=TOLERANCE)

        perturbation = build_perturbation_intervals(drift_intervals, extension=TOLERANCE)
        cd = compute_correct_detection(warnings, perturbation)
        cd_pct = cd.score_percent

        results.append(StreamResult(
            count_score=score,
            mean_delay=delay_info["mean_delay"],
            cd_pct=cd_pct,
            n_warnings=len(warnings),
            n_actual=n_actual,
            n_matched=delay_info["n_matched"],
        ))
        _print_stream_done(
            "eval",
            spec.name,
            csv_path,
            param,
            len(warnings),
            n_actual,
            score,
            mean_delay=delay_info["mean_delay"],
            cd_pct=cd_pct,
        )

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _fmt(v: Any, fmt: str = ".3f") -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    return format(v, fmt)


def print_summary(rows: List[Dict[str, Any]]) -> None:
    headers = ["detector", "param_attr", "calib_param", "count_score", "CD%", "avg_delay"]
    widths = [max(len(h), max(len(str(r[h])) for r in rows)) for h in headers]

    sep = "  ".join("-" * w for w in widths)
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print("\n=== Calibration + Delay Evaluation ===")
    print(f"Calibration: g00–g04   Evaluation: g05–g09   tolerance={TOLERANCE}")
    print(header_line)
    print(sep)
    for r in rows:
        print("  ".join(str(r[h]).ljust(widths[i]) for i, h in enumerate(headers)))


def save_csv(rows: List[Dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "calibration_summary.csv"
    import csv
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
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
        sys.exit("No calibration streams found. Check DATA_DIR.")

    summary_rows: List[Dict[str, Any]] = []

    for spec in DETECTORS:
        print(f"\n[{spec.name}] Calibrating on {len(calib_paths)} streams...")
        calibrated_param = calibrate(spec, calib_paths)
        print(f"  → calibrated {spec.param_attr} = {calibrated_param}")

        print(f"[{spec.name}] Evaluating on {len(eval_paths)} streams at {spec.param_attr}={calibrated_param}...")
        eval_results = evaluate_at_param(spec, calibrated_param, eval_paths)

        valid_scores = [r.count_score for r in eval_results]
        valid_delays = [r.mean_delay for r in eval_results if not math.isnan(r.mean_delay)]
        valid_cd = [r.cd_pct for r in eval_results if r.cd_pct is not None]

        row = {
            "detector": spec.name,
            "param_attr": spec.param_attr,
            "calib_param": calibrated_param,
            "count_score": _fmt(np.mean(valid_scores) if valid_scores else math.nan),
            "CD%": _fmt(np.mean(valid_cd) if valid_cd else math.nan, ".1f"),
            "avg_delay": _fmt(np.mean(valid_delays) if valid_delays else math.nan, ".0f"),
        }
        summary_rows.append(row)

    print_summary(summary_rows)
    save_csv(summary_rows)


if __name__ == "__main__":
    main()
