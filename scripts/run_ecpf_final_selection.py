"""Run staged end-to-end ECPF final-selection experiments.

This script prepares the experiment described in
``docs/ECPF_FINAL_SELECTION_PLAN.md``.  It is intentionally opt-in: stage runs
require ``--execute`` so ``--help`` and dry-run inspection never start the
expensive experiments by accident.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline, load_recurring_stream_pair
from src.ecpf import load_drift_intervals_file
from src.metrics.correct_detection import (
    build_perturbation_intervals,
    compute_correct_detection,
)


STAGE_DEFAULT_MAX_STEPS = {
    "stage0": 5000,
    "stage1": 20000,
    "stage2": 50000,
    "stage3": 0,
    "uqdet_smoke": 20000,
    "uqdet_stageb": 50000,
}

STAGE_DEFAULT_GROUPS = {
    "stage0": ["recurring"],
    "stage1": ["recurring"],
    "stage2": ["recurring"],
    "stage3": ["recurring", "sudden", "gradual", "incremental"],
    "uqdet_smoke": ["recurring"],
    "uqdet_stageb": ["recurring"],
}

STAGE_DEFAULT_LIMIT_FILES = {
    "stage0": 0,
    "stage1": 0,
    "stage2": 0,
    "stage3": 0,
    "uqdet_smoke": 2,
    "uqdet_stageb": 0,
}

DATASET_GROUP_DIRS = {
    "recurring": "recurring_drift",
    "sudden": "sudden_drift",
    "gradual": "gradual_drift",
    "incremental": "incremental_drift",
}

PERTURBATION_EXTENSION = 1000
DELAY_TOLERANCE = 2000
RECOVERY_WINDOW = 2000
RECOVERY_EVAL_WINDOW = 200
FALSE_EVENT_WINDOW = 200


@dataclass(frozen=True)
class ExperimentSpec:
    config_id: str
    family: str
    description: str
    model_type: str
    signal_mode: str
    uq_mode: str = "mi_like"
    warning_detector: Optional[str] = None
    drift_detector: Optional[str] = None
    warning_signal: str = "error"
    drift_signal: str = "error"
    detector_delta: float = 0.05
    detector_delta_w: float = 0.1
    detector_min_instances: int = 30
    uq_num_classes: Optional[int] = 2
    warning_value_range: float = 1.0
    drift_value_range: float = 1.0
    ecpf_warning_length: int = 60
    ecpf_max_pool_size: int = 10
    ecpf_similarity_margin: float = 0.95
    ecpf_fade_points: int = 15
    ecpf_fade_enabled: bool = True
    ecpf_uq_delta: float = 0.01
    ecpf_uq_smoothing_alpha: float = 0.1
    ecpf_uq_warning_timeout: int = 1000
    extra_attrs: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StreamCase:
    group: str
    csv_path: Path
    drift_path: Path
    g_index: Optional[int]


def _fmt_num(value: float) -> str:
    text = f"{value:.4g}"
    return text.replace(".", "p").replace("-", "m")


def _with_delta_w(delta: float) -> float:
    return float(delta) * 2.0


def _spec(
    *,
    config_id: str,
    family: str,
    description: str,
    model_type: str,
    signal_mode: str,
    **kwargs: Any,
) -> ExperimentSpec:
    return ExperimentSpec(
        config_id=config_id,
        family=family,
        description=description,
        model_type=model_type,
        signal_mode=signal_mode,
        **kwargs,
    )


def build_uq_detector_matrix_specs() -> List[ExperimentSpec]:
    """Return UQ-warning x detector-family configs for recurring screening."""

    uq_signals = [
        ("mi_like", "uq_mi", "mi_like"),
        ("vote", "uq_vote", "vote_disagreement"),
        ("entropy", "uq_entropy", "predictive_entropy"),
        ("variance", "uq_variance", "variance_eu"),
    ]
    detector_families = [
        ("adwin", "ADWIN", 0.05, 0.02),
        ("seed", "SEED", 0.10, 0.05),
        ("seqdrift2", "SeqDrift2", 0.550, 0.553),
    ]

    specs: List[ExperimentSpec] = []
    for uq_id, warning_signal, uq_mode in uq_signals:
        for detector, detector_label, warning_delta, drift_delta in detector_families:
            specs.append(
                _spec(
                    config_id=f"uq_{uq_id}_{detector}",
                    family="UQ_detector_matrix",
                    description=(
                        f"{uq_mode} warning signal with {detector_label} "
                        "warning/error-confirmation detectors "
                        f"(warning_delta={warning_delta}, drift_delta={drift_delta})."
                    ),
                    model_type="hf",
                    signal_mode="hybrid_adwin_family",
                    warning_detector=detector,
                    drift_detector=detector,
                    warning_signal=warning_signal,
                    drift_signal="error",
                    detector_delta=drift_delta,
                    detector_delta_w=warning_delta,
                    detector_min_instances=30,
                    uq_mode=uq_mode,
                )
            )
    return specs


def build_stage_specs(stage: str) -> List[ExperimentSpec]:
    """Return built-in candidates for a stage.

    Stage 0 is intentionally small.  Stage 1 covers all primary families with
    tiny grids.  Stage 2 adds refinement and pure-UQ ablations.  Stage 3 has a
    conservative default finalist set but should normally be narrowed with
    ``--config-id`` after reviewing Stage 1/2 outputs.
    """

    if stage in {"uqdet_smoke", "uqdet_stageb"}:
        return build_uq_detector_matrix_specs()

    specs: List[ExperimentSpec] = []

    if stage in {"stage1", "stage3"}:
        specs.append(
            _spec(
                config_id="c0_oracle60_ht",
                family="C0_oracle",
                description="Oracle upper bound with perfect warning starts.",
                model_type="ht",
                signal_mode="oracle_60",
            )
        )

    c1_deltas = [0.05] if stage == "stage0" else [0.02, 0.05, 0.10]
    for delta in c1_deltas:
        specs.append(
            _spec(
                config_id=f"c1_dual_adwin_d{_fmt_num(delta)}",
                family="C1_dual_adwin",
                description="Dual ADWIN error/error baseline.",
                model_type="ht",
                signal_mode="dual_adwin",
                warning_signal="error",
                drift_signal="error",
                detector_delta=delta,
                detector_delta_w=_with_delta_w(delta),
            )
        )

    c23_deltas = [0.05] if stage == "stage0" else [0.02, 0.05, 0.10]
    c23_mins = [30] if stage == "stage0" else [30, 60]
    for delta in c23_deltas:
        for min_instances in c23_mins:
            specs.append(
                _spec(
                    config_id=f"c2_adwin_warn_seqdrift2_drift_d{_fmt_num(delta)}_m{min_instances}",
                    family="C2_adwin_warning_seqdrift2_drift",
                    description="ADWIN opens warning buffer; SeqDrift2 confirms drift.",
                    model_type="ht",
                    signal_mode="hybrid_adwin_family",
                    warning_detector="adwin",
                    drift_detector="seqdrift2",
                    warning_signal="error",
                    drift_signal="error",
                    detector_delta=delta,
                    detector_delta_w=_with_delta_w(delta),
                    detector_min_instances=min_instances,
                )
            )
            specs.append(
                _spec(
                    config_id=f"c3_seqdrift2_warn_adwin_drift_d{_fmt_num(delta)}_m{min_instances}",
                    family="C3_seqdrift2_warning_adwin_drift",
                    description="SeqDrift2 opens warning buffer; ADWIN confirms drift.",
                    model_type="ht",
                    signal_mode="hybrid_adwin_family",
                    warning_detector="seqdrift2",
                    drift_detector="adwin",
                    warning_signal="error",
                    drift_signal="error",
                    detector_delta=delta,
                    detector_delta_w=_with_delta_w(delta),
                    detector_min_instances=min_instances,
                )
            )

    c4_mins = [60] if stage == "stage0" else [30, 60, 100]
    for min_instances in c4_mins:
        specs.append(
            _spec(
                config_id=f"c4_dual_seqdrift2_m{min_instances}",
                family="C4_dual_seqdrift2",
                description="Dual SeqDrift2 high-sensitivity boundary.",
                model_type="ht",
                signal_mode="dual_seqdrift2",
                warning_signal="error",
                drift_signal="error",
                detector_min_instances=min_instances,
            )
        )

    hcdt_profiles = [
        ("standard_ht", "ht", 0.005, 0.07, 2.5),
    ]
    if stage != "stage0":
        hcdt_profiles.extend(
            [
                ("standard_hf", "hf", 0.005, 0.07, 2.5),
                ("threshold_ht", "ht", 0.003, 0.05, 2.5),
                ("strict_ht", "ht", 0.003, 0.10, 3.0),
            ]
        )
    if stage == "stage2":
        hcdt_profiles.extend(
            [
                ("loose_ht", "ht", 0.010, 0.05, 2.5),
                ("threshold_hf", "hf", 0.003, 0.05, 2.5),
            ]
        )
    for name, model_type, delta, threshold, drift_level in hcdt_profiles:
        specs.append(
            _spec(
                config_id=f"c5_hcdt_{name}",
                family="C5_hcdt",
                description="HCDT two-layer ECPF detector.",
                model_type=model_type,
                signal_mode="meta_ecpf_hcdt",
                extra_attrs={
                    "ecpf_hcdt_detection_delta": delta,
                    "ecpf_hcdt_detection_threshold": threshold,
                    "ecpf_hcdt_rddm_drift_level": drift_level,
                },
            )
        )

    uq_modes = ["mi_like"] if stage == "stage0" else [
        "mi_like",
        "vote_disagreement",
        "predictive_entropy",
        "variance_eu",
    ]
    uq_deltas = [0.01]
    uq_alphas = [0.1]
    uq_timeouts = [1000]
    if stage == "stage2":
        uq_deltas = [0.005, 0.01, 0.02]
        uq_alphas = [0.05, 0.1, 0.2]
        uq_timeouts = [500, 1000, 2000]
    for mode in uq_modes:
        for delta in uq_deltas:
            for alpha in uq_alphas:
                for timeout in uq_timeouts:
                    specs.append(
                        _spec(
                            config_id=(
                                f"c6_uq_warning_{mode}_"
                                f"d{_fmt_num(delta)}_a{_fmt_num(alpha)}_t{timeout}"
                            ),
                            family="C6_uq_warning_error_confirmation",
                            description="UQ warning layer with error-based ADWIN confirmation.",
                            model_type="hf",
                            signal_mode="uq_warning",
                            uq_mode=mode,
                            ecpf_uq_delta=delta,
                            ecpf_uq_smoothing_alpha=alpha,
                            ecpf_uq_warning_timeout=timeout,
                        )
                    )

    if stage == "stage2":
        pure_uq = [
            ("adwin", "adwin", "uq_entropy", "uq_entropy"),
            ("adwin", "adwin", "uq_vote", "uq_vote"),
            ("adwin", "seqdrift2", "uq_mi", "uq_mi"),
            ("seqdrift2", "seqdrift2", "uq_vote", "uq_vote"),
        ]
        for warn_det, drift_det, warn_sig, drift_sig in pure_uq:
            specs.append(
                _spec(
                    config_id=f"uq_pure_{warn_det}_{drift_det}_{warn_sig}_{drift_sig}",
                    family="UQ_pure_ablation",
                    description="Pure-UQ ablation: UQ drives both warning and confirmation.",
                    model_type="hf",
                    signal_mode="hybrid_adwin_family",
                    warning_detector=warn_det,
                    drift_detector=drift_det,
                    warning_signal=warn_sig,
                    drift_signal=drift_sig,
                    detector_delta=0.05,
                    detector_delta_w=0.1,
                    detector_min_instances=30,
                )
            )

    if stage == "stage3":
        preferred = {
            "c0_oracle60_ht",
            "c1_dual_adwin_d0p05",
            "c2_adwin_warn_seqdrift2_drift_d0p05_m30",
            "c5_hcdt_standard_ht",
            "c6_uq_warning_mi_like_d0p01_a0p1_t1000",
        }
        specs = [s for s in specs if s.config_id in preferred]

    return specs


def _parse_csv_arg(value: Optional[str], default: Sequence[str]) -> List[str]:
    if not value:
        return list(default)
    out: List[str] = []
    for part in value.split(","):
        item = part.strip()
        if item:
            out.append(item)
    return out


def _parse_repeated_csv(values: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        out.extend(_parse_csv_arg(value, []))
    return out


def select_specs(
    specs: Sequence[ExperimentSpec],
    *,
    config_ids: Sequence[str],
    families: Sequence[str],
    limit_configs: int,
) -> List[ExperimentSpec]:
    selected = list(specs)
    if config_ids:
        wanted = set(config_ids)
        selected = [s for s in selected if s.config_id in wanted]
    if families:
        wanted_families = set(families)
        selected = [s for s in selected if s.family in wanted_families]
    if limit_configs > 0:
        selected = selected[:limit_configs]
    return selected


def discover_streams(
    *,
    data_root: Path,
    groups: Sequence[str],
    split: str,
    limit_files: int,
) -> List[StreamCase]:
    streams: List[StreamCase] = []
    for group in groups:
        if group not in DATASET_GROUP_DIRS:
            raise ValueError(
                f"Unknown dataset group {group!r}; choose from {sorted(DATASET_GROUP_DIRS)}"
            )
        group_dir = data_root / DATASET_GROUP_DIRS[group]
        for csv_path in sorted(group_dir.glob("*.csv")):
            drift_path = csv_path.with_name(csv_path.stem + "_drift_times.txt")
            if not drift_path.exists():
                continue
            g_index = _extract_g_index(csv_path)
            if split == "tune" and (g_index is None or not (0 <= g_index <= 4)):
                continue
            if split == "validation" and (g_index is None or not (5 <= g_index <= 9)):
                continue
            streams.append(
                StreamCase(
                    group=group,
                    csv_path=csv_path,
                    drift_path=drift_path,
                    g_index=g_index,
                )
            )
    if limit_files > 0:
        streams = streams[:limit_files]
    return streams


def _extract_g_index(path: Path) -> Optional[int]:
    match = re.search(r"_g(\d+)", path.stem)
    if not match:
        return None
    return int(match.group(1))


def build_pipeline_config(spec: ExperimentSpec, drift_starts: Sequence[int]) -> PipelineConfig:
    cfg = PipelineConfig(
        use_ecpf=True,
        model_type=spec.model_type,
        ecpf_signal_mode=spec.signal_mode,
        ecpf_oracle_true_drift_times=list(drift_starts)
        if spec.signal_mode == "oracle_60"
        else None,
        ecpf_uq_mode=spec.uq_mode,
        ecpf_warning_length=spec.ecpf_warning_length,
        ecpf_similarity_margin=spec.ecpf_similarity_margin,
        ecpf_fade_points=spec.ecpf_fade_points,
        ecpf_fade_enabled=spec.ecpf_fade_enabled,
        ecpf_max_pool_size=spec.ecpf_max_pool_size,
        detector_delta=spec.detector_delta,
        detector_delta_w=spec.detector_delta_w,
        ecpf_detector_min_instances=spec.detector_min_instances,
        ecpf_warning_detector=spec.warning_detector,
        ecpf_drift_detector=spec.drift_detector,
        ecpf_warning_signal=spec.warning_signal,
        ecpf_drift_signal=spec.drift_signal,
        ecpf_uq_num_classes=spec.uq_num_classes,
        ecpf_warning_value_range=spec.warning_value_range,
        ecpf_drift_value_range=spec.drift_value_range,
        ecpf_uq_delta=spec.ecpf_uq_delta,
        ecpf_uq_smoothing_alpha=spec.ecpf_uq_smoothing_alpha,
        ecpf_uq_warning_timeout=spec.ecpf_uq_warning_timeout,
    )
    for attr, value in spec.extra_attrs.items():
        setattr(cfg, attr, value)
    return cfg


def run_stream_case(
    *,
    spec: ExperimentSpec,
    case: StreamCase,
    warm_start: int,
    max_steps: int,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    X, y, drift_starts = load_recurring_stream_pair(
        str(case.csv_path),
        str(case.drift_path),
    )
    drift_intervals = load_drift_intervals_file(str(case.drift_path))

    if max_steps > 0:
        n = min(max_steps, len(y))
        X = X[:n]
        y = y[:n]
        drift_starts = [t for t in drift_starts if t < n]
        drift_intervals = [(s, e) for s, e in drift_intervals if s < n]

    if len(y) <= warm_start:
        raise ValueError(
            f"warm_start ({warm_start}) must be smaller than stream length ({len(y)})"
        )

    cfg = build_pipeline_config(spec, drift_starts)
    pipe = ConceptDriftPipeline(cfg)
    pipe.warm_start(X[:warm_start], y[:warm_start])

    y_pred = np.full(len(y), np.nan, dtype=float)
    event_rows: List[Dict[str, Any]] = []
    pool_sizes: List[int] = []
    started = time.perf_counter()

    for i in range(warm_start, len(y)):
        yp, detections, drift = pipe.step(X[i], y[i], index=i)
        y_pred[i] = yp
        if pipe._ecpf is not None:
            pool_sizes.append(sum(1 for slot in pipe._ecpf.slots if slot is not None))
        if not drift:
            continue
        for d in detections:
            warning_t = int(d.details.get("warning_start_t", d.timestamp))
            confirmation_t = int(d.details.get("confirmation_t", i))
            row = {
                "config_id": spec.config_id,
                "family": spec.family,
                "dataset_group": case.group,
                "file": case.csv_path.name,
                "warning_t": warning_t,
                "confirmation_t": confirmation_t,
                "timestamp": int(d.timestamp),
                "warning_to_confirm_age": confirmation_t - warning_t,
                "source": d.detector_source,
                "drift_type": d.drift_type.value,
                "ecpf_protocol": d.details.get("ecpf_protocol"),
                "detector_type": d.details.get("detector_type"),
                "warning_detector": d.details.get("warning_detector"),
                "drift_detector": d.details.get("drift_detector"),
                "warning_signal": d.details.get("warning_signal"),
                "drift_signal": d.details.get("drift_signal"),
                "uq_mode": d.details.get("uq_mode"),
                "uq_raw": d.details.get("uq_raw"),
                "uq_smoothed": d.details.get("uq_smoothed"),
                "buffer_len": d.details.get("buffer_len"),
                "pool_size": d.details.get("collection_size"),
                "best_idx": d.details.get("best_idx"),
                "acc_current_on_warning": d.details.get("acc_current_on_warning"),
                "acc_best_on_warning": d.details.get("acc_best_on_warning"),
                "acc_new_on_warning": d.details.get("acc_new_on_warning"),
            }
            event_rows.append(row)

    runtime_s = time.perf_counter() - started
    warning_ts = [int(r["warning_t"]) for r in event_rows]
    confirmation_ts = [int(r["confirmation_t"]) for r in event_rows]
    perturbation = build_perturbation_intervals(
        drift_intervals,
        extension=PERTURBATION_EXTENSION,
    )
    cd_warning = compute_correct_detection(warning_ts, perturbation)
    cd_confirmation = compute_correct_detection(confirmation_ts, perturbation)
    delay_warning = compute_detection_delays(
        warning_ts,
        drift_starts,
        tolerance=DELAY_TOLERANCE,
    )
    delay_confirmation = compute_detection_delays(
        confirmation_ts,
        drift_starts,
        tolerance=DELAY_TOLERANCE,
    )
    accuracy = compute_accuracy(y, y_pred)
    mistakes = compute_mistakes(y, y_pred)
    recovery = compute_recovery_metrics(y, y_pred, drift_intervals, warm_start)
    false_cost = compute_false_adaptation_cost(
        y,
        y_pred,
        confirmation_ts,
        perturbation,
        window=FALSE_EVENT_WINDOW,
    )
    reuse = compute_reuse_metrics(event_rows)

    alive = sum(1 for slot in pipe._ecpf.slots if slot is not None) if pipe._ecpf else 0
    avg_pool_size = float(np.mean(pool_sizes)) if pool_sizes else 0.0
    warning_age_values = [
        int(r["warning_to_confirm_age"])
        for r in event_rows
        if r.get("warning_to_confirm_age") is not None
    ]

    summary = {
        "config_id": spec.config_id,
        "family": spec.family,
        "description": spec.description,
        "dataset_group": case.group,
        "file": case.csv_path.name,
        "samples": int(len(y)),
        "max_steps": int(max_steps),
        "warm_start": int(warm_start),
        "groundtruth_drift_count": int(len(drift_starts)),
        "groundtruth_drift_times": " ".join(str(t) for t in drift_starts),
        "detected_drift_events": int(len(event_rows)),
        "prequential_accuracy": accuracy,
        "mistake_count": mistakes,
        "runtime_s": runtime_s,
        "model_type": spec.model_type,
        "signal_mode": spec.signal_mode,
        "uq_mode": spec.uq_mode,
        "warning_detector": spec.warning_detector,
        "drift_detector": spec.drift_detector,
        "warning_signal": spec.warning_signal,
        "drift_signal": spec.drift_signal,
        "detector_delta": spec.detector_delta,
        "detector_delta_w": spec.detector_delta_w,
        "detector_min_instances": spec.detector_min_instances,
        "ecpf_uq_delta": spec.ecpf_uq_delta,
        "ecpf_uq_smoothing_alpha": spec.ecpf_uq_smoothing_alpha,
        "ecpf_uq_warning_timeout": spec.ecpf_uq_warning_timeout,
        "pool_alive_final": int(alive),
        "pool_size_mean": avg_pool_size,
        "cd_warning_tp": cd_warning.tp,
        "cd_warning_fp": cd_warning.fp,
        "cd_warning_n": cd_warning.n_intervals,
        "cd_warning_score_pct": cd_warning.score_percent,
        "cd_confirmation_tp": cd_confirmation.tp,
        "cd_confirmation_fp": cd_confirmation.fp,
        "cd_confirmation_n": cd_confirmation.n_intervals,
        "cd_confirmation_score_pct": cd_confirmation.score_percent,
        "count_score_confirmation": compute_count_score(len(confirmation_ts), len(drift_starts)),
        "count_score_warning": compute_count_score(len(warning_ts), len(drift_starts)),
        "mean_warning_delay": delay_warning["mean_delay"],
        "matched_warning_drifts": delay_warning["n_matched"],
        "mean_confirmation_delay": delay_confirmation["mean_delay"],
        "matched_confirmation_drifts": delay_confirmation["n_matched"],
        "mean_warning_to_confirm_age": safe_mean(warning_age_values),
        "post_drift_error_rate_1000": recovery["post_drift_error_rate_1000"],
        "mean_recovery_delay": recovery["mean_recovery_delay"],
        "false_event_count": false_cost["false_event_count"],
        "false_adaptation_cost": false_cost["false_adaptation_cost"],
        "reuse_best_beats_current_rate": reuse["best_beats_current_rate"],
        "reuse_new_beats_current_rate": reuse["new_beats_current_rate"],
        "reuse_eval_event_count": reuse["reuse_eval_event_count"],
    }
    for attr, value in spec.extra_attrs.items():
        summary[attr] = value
    return summary, event_rows


def compute_accuracy(y: np.ndarray, y_pred: np.ndarray) -> float:
    valid = ~np.isnan(y_pred)
    if not np.any(valid):
        return float("nan")
    correct = np.round(y_pred[valid]).astype(int) == np.round(y[valid]).astype(int)
    return float(np.mean(correct.astype(float)))


def compute_mistakes(y: np.ndarray, y_pred: np.ndarray) -> int:
    valid = ~np.isnan(y_pred)
    if not np.any(valid):
        return 0
    wrong = np.round(y_pred[valid]).astype(int) != np.round(y[valid]).astype(int)
    return int(np.sum(wrong))


def compute_count_score(n_detect: int, n_actual: int) -> Optional[float]:
    if n_actual <= 0:
        return None
    raw = 1.0 - abs(int(n_detect) - int(n_actual)) / float(n_actual)
    return max(0.0, min(1.0, raw))


def compute_detection_delays(
    detection_timestamps: Sequence[int],
    drift_starts: Sequence[int],
    *,
    tolerance: int,
) -> Dict[str, Any]:
    alerts = sorted(int(t) for t in detection_timestamps)
    used: set[int] = set()
    delays: List[int] = []
    for gt in sorted(int(t) for t in drift_starts):
        matched_idx: Optional[int] = None
        for idx, alert in enumerate(alerts):
            if idx in used:
                continue
            if alert < gt:
                continue
            if alert > gt + tolerance:
                break
            matched_idx = idx
            break
        if matched_idx is not None:
            used.add(matched_idx)
            delays.append(alerts[matched_idx] - gt)
    return {
        "delays": delays,
        "mean_delay": safe_mean(delays),
        "n_matched": len(delays),
        "n_missed": max(0, len(drift_starts) - len(delays)),
    }


def compute_recovery_metrics(
    y: np.ndarray,
    y_pred: np.ndarray,
    intervals: Sequence[Tuple[int, int]],
    warm_start: int,
) -> Dict[str, float]:
    error_rates: List[float] = []
    recovery_delays: List[int] = []
    global_acc = compute_accuracy(y, y_pred)
    for start, end in intervals:
        if start >= len(y):
            continue
        end = min(int(end), len(y) - 1)
        post_acc = accuracy_window(y, y_pred, end, min(len(y), end + 1000))
        if not math.isnan(post_acc):
            error_rates.append(1.0 - post_acc)

        pre_start = max(warm_start, int(start) - 500)
        pre_acc = accuracy_window(y, y_pred, pre_start, int(start))
        if math.isnan(pre_acc):
            pre_acc = global_acc
        threshold = max(0.0, float(pre_acc) - 0.05)
        found = RECOVERY_WINDOW
        search_start = max(warm_start, end)
        search_end = min(len(y), end + RECOVERY_WINDOW)
        for t in range(search_start, search_end):
            acc = accuracy_window(y, y_pred, t, min(len(y), t + RECOVERY_EVAL_WINDOW))
            if not math.isnan(acc) and acc >= threshold:
                found = t - end
                break
        recovery_delays.append(int(found))
    return {
        "post_drift_error_rate_1000": safe_mean(error_rates),
        "mean_recovery_delay": safe_mean(recovery_delays),
    }


def compute_false_adaptation_cost(
    y: np.ndarray,
    y_pred: np.ndarray,
    event_ts: Sequence[int],
    true_windows: Sequence[Tuple[int, int]],
    *,
    window: int,
) -> Dict[str, float]:
    false_events = [int(t) for t in event_ts if not in_any_interval(int(t), true_windows)]
    costs: List[float] = []
    for t in false_events:
        pre = accuracy_window(y, y_pred, max(0, t - window), t)
        post = accuracy_window(y, y_pred, t, min(len(y), t + window))
        if not math.isnan(pre) and not math.isnan(post):
            costs.append(pre - post)
    return {
        "false_event_count": float(len(false_events)),
        "false_adaptation_cost": safe_mean(costs),
    }


def compute_reuse_metrics(event_rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    best_wins = 0
    new_wins = 0
    total = 0
    for row in event_rows:
        current = parse_float(row.get("acc_current_on_warning"))
        best = parse_float(row.get("acc_best_on_warning"))
        new = parse_float(row.get("acc_new_on_warning"))
        if current is None:
            continue
        counted = False
        if best is not None:
            best_wins += int(best > current)
            counted = True
        if new is not None:
            new_wins += int(new > current)
            counted = True
        if counted:
            total += 1
    return {
        "best_beats_current_rate": (best_wins / total) if total else float("nan"),
        "new_beats_current_rate": (new_wins / total) if total else float("nan"),
        "reuse_eval_event_count": float(total),
    }


def accuracy_window(y: np.ndarray, y_pred: np.ndarray, start: int, end: int) -> float:
    start = max(0, int(start))
    end = min(len(y), int(end))
    if end <= start:
        return float("nan")
    pred = y_pred[start:end]
    truth = y[start:end]
    valid = ~np.isnan(pred)
    if not np.any(valid):
        return float("nan")
    correct = np.round(pred[valid]).astype(int) == np.round(truth[valid]).astype(int)
    return float(np.mean(correct.astype(float)))


def in_any_interval(t: int, intervals: Sequence[Tuple[int, int]]) -> bool:
    return any(int(s) <= int(t) <= int(e) for s, e in intervals)


def safe_mean(values: Iterable[Any]) -> float:
    vals: List[float] = []
    for value in values:
        parsed = parse_float(value)
        if parsed is not None and not math.isnan(parsed):
            vals.append(parsed)
    return float(np.mean(vals)) if vals else float("nan")


def parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed):
        return None
    return parsed


def aggregate_summaries(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["config_id"]), []).append(row)

    aggregated: List[Dict[str, Any]] = []
    for config_id, items in grouped.items():
        first = items[0]
        actual = safe_mean(row.get("groundtruth_drift_count") for row in items)
        detected = safe_mean(row.get("detected_drift_events") for row in items)
        detected_ratio = detected / actual if actual and not math.isnan(actual) else float("nan")
        hard_reject_reason = ""
        if not math.isnan(detected_ratio) and detected_ratio > 3.0:
            hard_reject_reason = "event_explosion"
        elif not math.isnan(detected_ratio) and detected_ratio < 0.3:
            hard_reject_reason = "silent_detector"
        mean_runtime = safe_mean(row.get("runtime_s") for row in items)
        if not math.isnan(mean_runtime) and mean_runtime > 300.0:
            hard_reject_reason = hard_reject_reason or "runtime_high"

        agg = {
            "config_id": config_id,
            "family": first.get("family"),
            "description": first.get("description"),
            "files": len(items),
            "mean_accuracy": safe_mean(row.get("prequential_accuracy") for row in items),
            "mean_mistake_count": safe_mean(row.get("mistake_count") for row in items),
            "mean_actual_drifts": actual,
            "mean_detected_drifts": detected,
            "detected_to_actual_ratio": detected_ratio,
            "mean_cd_warning_score_pct": safe_mean(row.get("cd_warning_score_pct") for row in items),
            "mean_cd_confirmation_score_pct": safe_mean(row.get("cd_confirmation_score_pct") for row in items),
            "mean_cd_confirmation_fp": safe_mean(row.get("cd_confirmation_fp") for row in items),
            "mean_count_score_confirmation": safe_mean(row.get("count_score_confirmation") for row in items),
            "mean_warning_delay": safe_mean(row.get("mean_warning_delay") for row in items),
            "mean_confirmation_delay": safe_mean(row.get("mean_confirmation_delay") for row in items),
            "mean_warning_to_confirm_age": safe_mean(row.get("mean_warning_to_confirm_age") for row in items),
            "mean_post_drift_error_rate_1000": safe_mean(row.get("post_drift_error_rate_1000") for row in items),
            "mean_recovery_delay": safe_mean(row.get("mean_recovery_delay") for row in items),
            "mean_false_event_count": safe_mean(row.get("false_event_count") for row in items),
            "mean_false_adaptation_cost": safe_mean(row.get("false_adaptation_cost") for row in items),
            "mean_reuse_best_beats_current_rate": safe_mean(
                row.get("reuse_best_beats_current_rate") for row in items
            ),
            "mean_runtime_s": mean_runtime,
            "hard_reject": bool(hard_reject_reason),
            "hard_reject_reason": hard_reject_reason,
        }
        aggregated.append(agg)

    aggregated.sort(key=aggregate_sort_key)
    for rank, row in enumerate(aggregated, start=1):
        row["rank"] = rank
    return aggregated


def aggregate_sort_key(row: Dict[str, Any]) -> Tuple[Any, ...]:
    return (
        bool(row.get("hard_reject")),
        -nan_to_value(row.get("mean_accuracy"), -1.0),
        nan_to_value(row.get("mean_recovery_delay"), 1e12),
        nan_to_value(row.get("mean_false_adaptation_cost"), 1e12),
        nan_to_value(row.get("mean_runtime_s"), 1e12),
    )


def nan_to_value(value: Any, fallback: float) -> float:
    parsed = parse_float(value)
    return fallback if parsed is None else parsed


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_manifest(path: Path, specs: Sequence[ExperimentSpec], args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "stage": args.stage,
        "warm_start": args.warm_start,
        "max_steps": args.max_steps_effective,
        "limit_files": args.limit_files_effective,
        "groups": args.groups_effective,
        "split": args.split,
        "config_count": len(specs),
        "configs": [asdict(spec) for spec in specs],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_report(path: Path, stage: str, ranked_rows: Sequence[Dict[str, Any]]) -> None:
    lines = [
        f"# ECPF Final Selection Report ({stage})",
        "",
        "This report is generated by `scripts/run_ecpf_final_selection.py`.",
        "",
        "## Top Configs",
        "",
        "| rank | config_id | family | accuracy | recovery_delay | false_cost | reject |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for row in list(ranked_rows)[:20]:
        lines.append(
            "| {rank} | `{config_id}` | {family} | {acc:.4f} | {rec:.0f} | {cost:.4f} | {rej} |".format(
                rank=row.get("rank"),
                config_id=row.get("config_id"),
                family=row.get("family"),
                acc=nan_to_value(row.get("mean_accuracy"), float("nan")),
                rec=nan_to_value(row.get("mean_recovery_delay"), float("nan")),
                cost=nan_to_value(row.get("mean_false_adaptation_cost"), float("nan")),
                rej=row.get("hard_reject_reason") or "",
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_manifest(specs: Sequence[ExperimentSpec], streams: Sequence[StreamCase]) -> None:
    print(f"configs: {len(specs)}")
    for spec in specs:
        print(
            f"  {spec.config_id:58s} {spec.family:38s} "
            f"model={spec.model_type} mode={spec.signal_mode}"
        )
    print(f"streams: {len(streams)}")
    for case in streams:
        print(f"  {case.group:11s} {case.csv_path}")


def run_stage(args: argparse.Namespace) -> None:
    stage_for_selection = "stage1" if args.stage == "list" else args.stage
    specs = build_stage_specs(stage_for_selection)
    config_ids = _parse_repeated_csv(args.config_id)
    families = _parse_repeated_csv(args.family)
    specs = select_specs(
        specs,
        config_ids=config_ids,
        families=families,
        limit_configs=args.limit_configs,
    )

    args.groups_effective = _parse_csv_arg(
        args.groups,
        STAGE_DEFAULT_GROUPS[stage_for_selection],
    )
    args.max_steps_effective = (
        STAGE_DEFAULT_MAX_STEPS[stage_for_selection]
        if args.max_steps is None
        else args.max_steps
    )
    args.limit_files_effective = (
        STAGE_DEFAULT_LIMIT_FILES[stage_for_selection]
        if args.limit_files == 0
        else args.limit_files
    )
    streams = discover_streams(
        data_root=Path(args.data_root),
        groups=args.groups_effective,
        split=args.split,
        limit_files=args.limit_files_effective,
    )

    if args.dry_run or args.stage == "list":
        print_manifest(specs, streams)
        return

    if not args.execute:
        raise SystemExit(
            "Refusing to start experiments without --execute. "
            "Use --dry-run to inspect the plan."
        )

    if not specs:
        raise SystemExit("No configs selected.")
    if not streams:
        raise SystemExit("No streams selected.")

    output_dir = Path(args.output_dir)
    stage_prefix = args.stage
    details_path = output_dir / f"{stage_prefix}_details.csv"
    events_path = output_dir / f"{stage_prefix}_events.csv"
    summary_path = output_dir / f"{stage_prefix}_summary.csv"
    ranked_path = output_dir / "ranked_configs.csv"
    manifest_path = output_dir / "config_manifest.json"
    report_path = output_dir / "report.md"

    write_manifest(manifest_path, specs, args)

    details: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []

    total = len(specs) * len(streams)
    done = 0
    for spec in specs:
        for case in streams:
            done += 1
            print(
                f"[{done}/{total}] {spec.config_id} :: {case.group}/{case.csv_path.name}",
                flush=True,
            )
            summary, event_rows = run_stream_case(
                spec=spec,
                case=case,
                warm_start=args.warm_start,
                max_steps=args.max_steps_effective,
            )
            details.append(summary)
            events.extend(event_rows)
            if args.flush_each:
                write_csv(details_path, details)
                write_csv(events_path, events)

    ranked = aggregate_summaries(details)
    write_csv(details_path, details)
    write_csv(events_path, events)
    write_csv(summary_path, ranked)
    write_csv(ranked_path, ranked)
    write_report(report_path, args.stage, ranked)

    print("\nExperiment stage complete")
    print(f"details: {details_path}")
    print(f"events:  {events_path}")
    print(f"summary: {summary_path}")
    print(f"ranked:  {ranked_path}")
    print(f"report:  {report_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run staged end-to-end ECPF final-selection experiments.",
    )
    parser.add_argument(
        "--stage",
        choices=[
            "list",
            "stage0",
            "stage1",
            "stage2",
            "stage3",
            "uqdet_smoke",
            "uqdet_stageb",
        ],
        default="list",
        help="Stage to inspect or run. Stage runs require --execute.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually run the selected stage. Without this, stage runs are refused.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected configs and streams without running experiments.",
    )
    parser.add_argument("--data-root", default=str(ROOT / "data"))
    parser.add_argument("--output-dir", default=str(ROOT / "outputs" / "ecpf_final_selection"))
    parser.add_argument("--groups", default=None, help="Comma-separated dataset groups.")
    parser.add_argument(
        "--split",
        choices=["all", "tune", "validation"],
        default="all",
        help="Dataset split by g-index. tune=g00..g04, validation=g05..g09.",
    )
    parser.add_argument("--warm-start", type=int, default=200)
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Rows per stream. Default is stage-specific; 0 means full stream.",
    )
    parser.add_argument(
        "--config-id",
        action="append",
        default=None,
        help="Config id(s) to include. Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--family",
        action="append",
        default=None,
        help="Family name(s) to include. Can be repeated or comma-separated.",
    )
    parser.add_argument("--limit-configs", type=int, default=0)
    parser.add_argument(
        "--limit-files",
        type=int,
        default=0,
        help="Limit selected streams. 0 uses the stage default; uqdet_smoke defaults to 2.",
    )
    parser.add_argument(
        "--flush-each",
        action="store_true",
        help="Write detail/event CSVs after each stream for long runs.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_stage(args)


if __name__ == "__main__":
    main()
