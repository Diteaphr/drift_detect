"""Experiment harness: run the ECPF pipeline across task types, backends and UQ signals.

Covers the three target types the pipeline now supports -- binary (the historical
case, included as a control), multi-class, and regression -- so the results table
shows both that nothing regressed and that the new paths do real work.

Scoring reuses the project's existing functions rather than reimplementing them
(``src.metrics.compute_correct_detection`` and the delay / false-warning-rate
helpers in ``run_ecpf_uq_experiment``), so these numbers stay comparable with the
batch reports. ``run_ecpf_uq_experiment`` is import-safe: it guards its entry
point with ``if __name__ == "__main__"``.

Results stream to CSV row by row, and an existing CSV is read back on startup so
an interrupted matrix resumes instead of restarting.

Usage
-----
    python scripts/run_task_matrix.py --out-dir outputs/task_matrix
    python scripts/run_task_matrix.py --max-steps 8000 --only regression
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
import traceback
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_ecpf_uq_experiment import _detection_delay, _false_warning_rate  # noqa: E402
from src.config import PipelineConfig  # noqa: E402
from src.ecpf import load_drift_intervals_file  # noqa: E402
from src.metrics.correct_detection import (  # noqa: E402
    build_perturbation_intervals,
    compute_correct_detection,
)
from src.pipeline import ConceptDriftPipeline  # noqa: E402
from src.task import infer_task  # noqa: E402

WARM_START = 200

# A detector cannot realistically fire inside a zero-width ground-truth interval
# like (5000, 5001), so the right edge is extended before scoring. 1000 matches
# what run_ecpf_recurring.py reports, keeping these numbers comparable with it.
PERTURBATION = 1000

# (label, model_type, warning_signal, drift_signal)
CLASSIFICATION_CONFIGS = [
    ("ht/error",      "ht", "error",       "error"),
    ("rf/error",      "rf", "error",       "error"),
    ("hf/error",      "hf", "error",       "error"),
    ("hf/uq_var",     "hf", "uq_variance", "error"),
    ("hf/uq_mi",      "hf", "uq_mi",       "error"),
]

REGRESSION_CONFIGS = [
    ("htr/error",     "htr",  "error",       "error"),
    ("arfr/error",    "arfr", "error",       "error"),
    ("hfr/error",     "hfr",  "error",       "error"),
    ("hfr/uq_var",    "hfr",  "uq_variance", "error"),
]

#: Trimmed sets for large external sweeps. 'rf'/'arfr' are dropped: they are the
#: slowest by far and their internal per-tree ADWIN confounds any claim about the
#: external detector, so they buy little per unit of runtime here.
CLASSIFICATION_CONFIGS_LEAN = [c for c in CLASSIFICATION_CONFIGS if c[1] != "rf"
                               and c[0] != "hf/uq_mi"]
REGRESSION_CONFIGS_LEAN = [c for c in REGRESSION_CONFIGS if c[1] != "arfr"]

#: UQ-signal ablation: same forest, same detector, only the warning signal
#: changes, with 'error' as the reference. Motivated by the finding that the
#: probability-space modes (mi_like / variance_eu) FALL after a drift while the
#: hard-vote mode RISES -- so this asks whether switching the primary UQ mode
#: actually buys detections and post-drift accuracy.
#: With the default 5 trees the vote signal takes only 4 distinct values
#: ({0, .2, .4, .6}) and has high sampling variance -- a coarse, noisy stream for
#: ADWIN. The 15-tree arm controls for that: 8 levels, variance down by ~3x.
UQ_ABLATION_CONFIGS = [
    ("hf/error",       "hf", "error",             "error", {}),
    ("hf/uq_vote",     "hf", "vote_disagreement", "error", {}),
    ("hf/uq_mi",       "hf", "uq_mi",             "error", {}),
    ("hf/uq_var",      "hf", "uq_variance",       "error", {}),
    ("hf15/error",     "hf", "error",             "error", {"n_trees": 15}),
    ("hf15/uq_vote",   "hf", "vote_disagreement", "error", {"n_trees": 15}),
    ("hf15/uq_mi",     "hf", "uq_mi",             "error", {"n_trees": 15}),
]

#: Forest-size sweep with the ERROR signal fixed. Motivated by the UQ ablation,
#: where a 15-tree forest's post-drift error jumped far more than a 5-tree one
#: (+275% vs +40%): a larger forest fits the old concept more tightly, so a new
#: concept makes it fail more decisively -- exactly the property an error-driven
#: detector wants. 'ht' is the single-tree control: it had the fewest FPs on the
#: RBF data, but possibly only because it never learns well enough to be
#: sensitive; the sweep separates those two readings.
TREE_SWEEP_CONFIGS = [
    ("ht/error",       "ht", "error", "error", {}),
    ("hf5/error",      "hf", "error", "error", {"n_trees": 5}),
    ("hf10/error",     "hf", "error", "error", {"n_trees": 10}),
    ("hf15/error",     "hf", "error", "error", {"n_trees": 15}),
    ("hf25/error",     "hf", "error", "error", {"n_trees": 25}),
]

#: Detector-calibration sweep. Learner (hf10) and signal (error) are FIXED --
#: three earlier experiments showed neither UQ-signal choice nor forest size
#: moves the post-drift error jump much beyond shift/sd ~0.7 on multi-class
#: streams. That leaves the detector: ADWIN's delta and warm-up were tuned on
#: binary streams whose error variance is ~2.5x lower (sd 0.20 vs 0.36 at K=4),
#: so the same delta is implicitly MORE conservative at K>2. Two factors:
#:   delta   (drift ADWIN confidence)   0.02 / 0.05 (current default) / 0.15
#:   min_inst (warm-up before it may fire) 30 (current) / 100 / 300
#: The (0.05, 30) cell IS the current default, so every other cell reads as a
#: delta against it. delta_w (warning ADWIN) is scaled 2x delta throughout,
#: preserving the default 0.1/0.05 ratio.
#: Echo-suppression sweep. Per-drift analysis showed hf10+error already RECALLS
#: 90-95% of ground-truth drifts; what drags the CD score down is that every true
#: drift is followed by 1-2 extra confirmations (median gap 1120 steps) while the
#: freshly swapped-in leader settles. Two mechanisms, tested separately and
#: together: RESET re-baselines the ADWIN windows on the new model; COOLDOWN
#: ignores confirmations for N steps. Cooldowns are placed at the p25 / median /
#: 60th percentile of the measured echo gaps, all well below the shortest true
#: inter-drift spacing in these streams (3333).
_HF10 = {"n_trees": 10}
ECHO_CONFIGS = [
    ("baseline",       "hf", "error", "error", _HF10, {}),
    ("reset",          "hf", "error", "error", _HF10, {"ecpf_detector_reset_on_drift": True}),
    ("cool500",        "hf", "error", "error", _HF10, {"ecpf_detector_cooldown": 500}),
    ("cool1000",       "hf", "error", "error", _HF10, {"ecpf_detector_cooldown": 1000}),
    ("cool1500",       "hf", "error", "error", _HF10, {"ecpf_detector_cooldown": 1500}),
    ("reset+cool1000", "hf", "error", "error", _HF10,
     {"ecpf_detector_reset_on_drift": True, "ecpf_detector_cooldown": 1000}),
]

#: Combined remedy, 2x2 factorial. Per-detection classification on the RBF
#: sudden streams split the false positives into two populations with different
#: causes: ECHOES (800-2000 steps after a true hit; the new leader settling)
#: and ORPHANS (mid-concept, accuracy unchanged before/after; the detector
#: firing on within-concept error noise at K=4's high base error rate). Cooldown
#: addresses echoes, a tighter ADWIN delta addresses orphans; they should stack.
#: The 2x2 separates "both needed" from "one suffices".
COMBO_CONFIGS = [
    ("d0.05",           "hf", "error", "error", _HF10, {}),
    ("d0.05+cool1000",  "hf", "error", "error", _HF10, {"ecpf_detector_cooldown": 1000}),
    ("d0.02",           "hf", "error", "error", _HF10,
     {"detector_delta": 0.02, "detector_delta_w": 0.04}),
    ("d0.02+cool1000",  "hf", "error", "error", _HF10,
     {"detector_delta": 0.02, "detector_delta_w": 0.04, "ecpf_detector_cooldown": 1000}),
]

#: Direction-gate validation, 2x2 with the warning timeout. The gate accepts a
#: drift confirmation only when the recent error exceeds the older baseline
#: (deterioration); the timeout closes warnings that stay open unconfirmed so a
#: later real confirmation is not stamped with a stale warning time. Offline
#: simulation on 4 sudden streams: gate at margin 0.05 suppressed 9/11 echoes
#: and 13/14 orphans while keeping 10/12 hits (both losses had special causes).
#: This matrix is the LIVE validation, including the gradual/recurring streams
#: the simulation did not cover.
#: Feature-mask sweep, accuracy-first. The hf forest defaults to
#: max_features="sqrt": each tree sees ceil(sqrt(d)) features per split -- 2 of 3
#: on the synthetic streams, 4 of 10 on the RBF ones. Three prior measurements
#: implicate the mask as the main within-concept accuracy gap (streaming plateau
#: ~0.81 vs batch ceiling ~1.0): the unmasked regression twin htr beat masked
#: hfr by 60% MAE; the single unmasked ht beat hf5 on 3-feature streams; and the
#: plateau gap itself. Trade-off to quantify: the mask is what MAKES tree
#: diversity, and diversity is the raw material of the ensemble-disagreement UQ
#: signals -- the companion signal probe measures what each mask level does to
#: those (accuracy first, UQ curve as a by-product, per the research decision).
MASK_CONFIGS = [
    ("hf10/sqrt", "hf", "error", "error", {"n_trees": 10, "max_features": "sqrt"}),
    ("hf10/f0.7", "hf", "error", "error", {"n_trees": 10, "max_features": 0.7}),
    ("hf10/all",  "hf", "error", "error", {"n_trees": 10, "max_features": None}),
]

#: Completion cell for the mask sweep: unmasked forest PLUS the already-validated
#: FP remedies. Removing the mask bought +0.108 accuracy but tripled FP -- the
#: extra detections are improvement-misreads (the better model's steeper, longer
#: learning slides), i.e. the exact FP family the warning timeout + cooldown were
#: validated against. This asks whether accuracy and CD can be had together.
MASK_FIX_CONFIGS = [
    ("all+fix", "hf", "error", "error", {"n_trees": 10, "max_features": None},
     {"ecpf_detector_warning_timeout": 3000, "ecpf_detector_cooldown": 1000}),
]

#: UQ-revival test. The direction-flip replication showed that on UNMASKED
#: forests over the 3-feature streams, the probability-space UQ signals rise at
#: drift (mi_like +0.343/80% rising vs -0.607/30% masked). Direction is
#: necessary but not sufficient -- this asks whether the revived signals can
#: actually DRIVE detection. Arms: error baseline (= the accuracy-default
#: config), each UQ signal as the warning opener with error confirmation, one
#: full-UQ arm, and a masked-UQ control to make the revival comparison paired.
_ALL10 = {"n_trees": 10, "max_features": None}
UQ_REVIVAL_CONFIGS = [
    ("all+error",   "hf", "error",             "error", _ALL10),
    ("all+uq_mi",   "hf", "uq_mi",             "error", _ALL10),
    ("all+uq_var",  "hf", "uq_variance",       "error", _ALL10),
    ("all+vote",    "hf", "vote_disagreement", "error", _ALL10),
    ("all+mi_full", "hf", "uq_mi",             "uq_mi", _ALL10),
    ("sqrt+uq_mi",  "hf", "uq_mi",             "error", {"n_trees": 10, "max_features": "sqrt"}),
]

GATE_CONFIGS = [
    ("baseline",      "hf", "error", "error", _HF10, {}),
    ("gate",          "hf", "error", "error", _HF10, {"ecpf_drift_direction_gate": True}),
    ("wtimeout",      "hf", "error", "error", _HF10, {"ecpf_detector_warning_timeout": 3000}),
    ("gate+wtimeout", "hf", "error", "error", _HF10,
     {"ecpf_drift_direction_gate": True, "ecpf_detector_warning_timeout": 3000}),
]

DETECTOR_CALIB_CONFIGS = []
for _d in (0.02, 0.05, 0.15):
    for _m in (30, 100, 300):
        DETECTOR_CALIB_CONFIGS.append((
            "d%.2f/m%d" % (_d, _m), "hf", "error", "error", {"n_trees": 10},
            {"detector_delta": _d, "detector_delta_w": min(0.5, 2 * _d),
             "ecpf_detector_min_instances": _m},
        ))

FIELDS = [
    "dataset", "drift_type", "sensitivity", "task", "n_classes", "config", "model_type",
    "warning_signal", "drift_signal", "status", "n_events",
    "tp", "fp", "n_intervals", "cd_score", "delay", "false_warning_rate",
    "quality_metric", "quality_value", "pool_size", "secs", "detail",
]


# ---------------------------------------------------------------------------
def discover_datasets(only: Optional[str], data: Optional[str] = None,
                      per_cell: int = 0) -> List[Tuple[str, str]]:
    """(group-label, csv-path) pairs.

    With *data* the caller supplies the streams (a CSV or a folder of them) and the
    group is decided per file by :func:`infer_task`, so an arbitrary dataset drops
    in without touching this file. Otherwise: one binary control plus the
    generated synthetic streams.
    """
    if data:
        paths = (
            sorted(_ls(data, recursive=True)) if os.path.isdir(data)
            else ([data] if os.path.exists(data) else [])
        )
        if per_cell:
            # Externally supplied trees ship ~10 replicates per
            # (drift_type, sensitivity) cell; take the first *per_cell* of each so
            # the matrix stays affordable while covering every cell.
            buckets: Dict[Tuple[str, str, str], List[str]] = {}
            for p in paths:
                dtype, tier = path_facets(p)
                buckets.setdefault((os.path.dirname(p), dtype, tier), []).append(p)
            paths = sorted(q for group in buckets.values() for q in sorted(group)[:per_cell])
        out = []
        for p in paths:
            try:
                spec = infer_task(pd.read_csv(p, usecols=lambda c: c == "y")["y"].values)
            except Exception:
                continue
            out.append(("regression" if spec.is_regression else "classification", p))
        return out

    out: List[Tuple[str, str]] = []
    if only in (None, "all", "binary"):
        out.append(("binary", "data/recurring_drift/recurring_sud_sea100k_g00.csv"))
    if only in (None, "all", "multiclass"):
        out += [("multiclass", p) for p in sorted(_ls("data/synthetic_multiclass"))]
    if only in (None, "all", "regression"):
        out += [("regression", p) for p in sorted(_ls("data/synthetic_regression"))]
    return [(g, p) for g, p in out if os.path.exists(p)]


def _ls(folder: str, recursive: bool = False) -> List[str]:
    """CSV paths under *folder*, skipping the summary/report files that sit
    alongside real streams in externally supplied dataset trees."""
    if not os.path.isdir(folder):
        return []
    out: List[str] = []
    if recursive:
        for root, _dirs, files in os.walk(folder):
            out += [os.path.join(root, f) for f in files if f.endswith(".csv")]
    else:
        out = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".csv")]
    skip = ("summary.csv", "sensitivity_validation_report.csv", "metadata.csv")
    return [p for p in out if os.path.basename(p) not in skip]


#: Sensitivity tier folder names used by the externally supplied dataset trees.
_TIERS = ("low", "medium", "high")


def dataset_key(path: str) -> str:
    """Unique, human-readable id for a stream in the results table.

    External trees reuse the same basename across drift_type/tier folders
    (every cell has a g00.csv), so the bare basename is not unique -- and a
    flat copy of such a tree silently overwrites files. Prefix with the facets
    when the layout carries them.
    """
    dtype, tier = path_facets(path)
    base = os.path.basename(path)
    return "%s/%s/%s" % (dtype or "-", tier or "-", base) if (dtype or tier) else base


def path_facets(path: str) -> Tuple[str, str]:
    """(drift_type, sensitivity) recovered from the directory layout.

    External dataset trees encode both in the path, e.g.
    ``.../multi classification/sudden_drift/high/foo.csv``. Returns empty
    strings when the layout does not carry them.
    """
    parts = [p.lower() for p in os.path.normpath(path).split(os.sep)]
    tier = next((p for p in parts if p in _TIERS), "")
    dtype = next((p.replace("_drift", "") for p in parts if p.endswith("_drift")), "")
    return dtype, tier


def load_stream(csv_path: str, max_steps: int):
    df = pd.read_csv(csv_path)
    if max_steps and max_steps > 0:
        df = df.iloc[:max_steps]
    y = df["y"].values
    X = df[[c for c in df.columns if c != "y"]].values.astype(np.float64)

    gt_path = os.path.splitext(csv_path)[0] + "_drift_times.txt"
    intervals = load_drift_intervals_file(gt_path) if os.path.exists(gt_path) else []
    if max_steps and max_steps > 0:
        intervals = [iv for iv in intervals if iv[0] < max_steps]
    return X, y, intervals


# ---------------------------------------------------------------------------
def run_one(csv_path: str, cfg_label: str, model_type: str,
            warning_signal: str, drift_signal: str, max_steps: int,
            model_kwargs: Optional[Dict[str, Any]] = None,
            cfg_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    X, y, intervals = load_stream(csv_path, max_steps)
    spec = infer_task(y)

    dtype, tier = path_facets(csv_path)
    row: Dict[str, Any] = {
        "dataset": dataset_key(csv_path),
        "drift_type": dtype,
        "sensitivity": tier,
        "task": spec.task_type.value,
        "n_classes": spec.n_classes if spec.is_classification else "",
        "config": cfg_label,
        "model_type": model_type,
        "warning_signal": warning_signal,
        "drift_signal": drift_signal,
    }

    cfg_kwargs: Dict[str, Any] = dict(
        model_type=model_type,
        model_kwargs=dict(model_kwargs or {}),
        use_ecpf=True,
        ecpf_signal_mode="dual_adwin",
        ecpf_warning_signal=warning_signal,
        ecpf_drift_signal=drift_signal,
        ecpf_detector_min_instances=30,
    )
    cfg_kwargs.update(cfg_overrides or {})   # detector-calibration cells override here
    cfg = PipelineConfig(**cfg_kwargs)

    t0 = time.time()
    try:
        pipe = ConceptDriftPipeline(cfg)
        detections: List[Any] = []
        y_true_all: List[float] = []
        y_pred_all: List[float] = []
        for idx, yt, yp, dets, _ in pipe.run_stream(X, y, warm_start_samples=WARM_START):
            detections.extend(dets)
            y_true_all.append(float(yt))
            y_pred_all.append(float(yp))
    except Exception as exc:
        row.update({
            "status": "CRASH", "secs": round(time.time() - t0, 1),
            "detail": "%s: %s" % (type(exc).__name__, str(exc).split("\n")[0][:160]),
        })
        row["_traceback"] = traceback.format_exc()
        return row

    times = [int(d.timestamp) for d in detections]
    gt_starts = [int(a) for a, _ in intervals]

    scored = build_perturbation_intervals(intervals, extension=PERTURBATION) if intervals else []
    cd = compute_correct_detection(times, scored) if scored else None
    yt_arr = np.asarray(y_true_all, dtype=np.float64)
    yp_arr = np.asarray(y_pred_all, dtype=np.float64)

    if spec.is_regression:
        metric_name = "MAE"
        metric_value = float(np.mean(np.abs(yt_arr - yp_arr))) if yt_arr.size else float("nan")
    else:
        metric_name = "accuracy"
        metric_value = float(np.mean(np.rint(yt_arr) == np.rint(yp_arr))) if yt_arr.size else float("nan")

    row.update({
        "status": "ok",
        "n_events": len(times),
        "tp": cd.tp if cd else "",
        "fp": cd.fp if cd else "",
        "n_intervals": cd.n_intervals if cd else "",
        "cd_score": round(cd.score_percent, 1) if cd and cd.score_percent is not None else "",
        "delay": round(_detection_delay(gt_starts, times), 1) if gt_starts else "",
        "false_warning_rate": round(_false_warning_rate(times, gt_starts), 3) if gt_starts else "",
        "quality_metric": metric_name,
        "quality_value": round(metric_value, 4),
        "pool_size": sum(1 for s in pipe._ecpf.slots if s is not None) if pipe._ecpf else "",
        "secs": round(time.time() - t0, 1),
        "detail": "",
    })
    return row


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", default="outputs/task_matrix")
    ap.add_argument("--max-steps", type=int, default=20000)
    ap.add_argument("--only", choices=["all", "binary", "multiclass", "regression"], default="all")
    ap.add_argument("--data", default=None,
                    help="a CSV or folder of CSVs (searched recursively) to run instead of "
                         "the built-in set; the task type of each file is inferred")
    ap.add_argument("--per-cell", type=int, default=0,
                    help="with --data, keep at most N replicates per "
                         "(folder, drift_type, sensitivity) cell; 0 = all")
    ap.add_argument("--configs",
                    choices=["default", "uq_ablation", "tree_sweep", "detector_calib", "echo",
                             "combo", "gate", "mask", "mask_fix", "uq_revival"],
                    default="default",
                    help="'uq_ablation' fixes the forest and varies only the UQ warning "
                         "signal; 'tree_sweep' fixes the error signal and varies forest size; "
                         "'detector_calib' fixes hf10+error and varies ADWIN delta x warm-up")
    ap.add_argument("--fresh", action="store_true", help="ignore an existing CSV instead of resuming")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    csv_out = os.path.join(args.out_dir, "results.csv")

    done: set = set()
    rows: List[Dict[str, Any]] = []
    if os.path.exists(csv_out) and not args.fresh:
        prev = pd.read_csv(csv_out)
        rows = prev.to_dict("records")
        done = {(r["dataset"], r["config"]) for r in rows}
        print("resuming: %d rows already present" % len(done))

    datasets = discover_datasets(args.only, args.data, args.per_cell)
    if not datasets:
        raise SystemExit("no datasets found (looked at %r)" % (args.data or "the built-in set"))
    jobs: List[Tuple[str, Tuple[str, str, str, str]]] = []
    lean = bool(args.data)
    for group, path in datasets:
        if args.configs in ("uq_ablation", "tree_sweep", "detector_calib", "echo", "combo",
                            "gate", "mask", "mask_fix", "uq_revival"):
            if group.startswith("regression"):
                continue   # all are classification questions
            configs = {"uq_ablation": UQ_ABLATION_CONFIGS,
                       "tree_sweep": TREE_SWEEP_CONFIGS,
                       "detector_calib": DETECTOR_CALIB_CONFIGS,
                       "echo": ECHO_CONFIGS,
                       "combo": COMBO_CONFIGS,
                       "gate": GATE_CONFIGS,
                       "mask": MASK_CONFIGS,
                       "mask_fix": MASK_FIX_CONFIGS,
                       "uq_revival": UQ_REVIVAL_CONFIGS}[args.configs]
        elif group.startswith("regression"):
            configs = REGRESSION_CONFIGS_LEAN if lean else REGRESSION_CONFIGS
        else:
            configs = CLASSIFICATION_CONFIGS_LEAN if lean else CLASSIFICATION_CONFIGS
        for c in configs:
            if (dataset_key(path), c[0]) not in done:
                jobs.append((path, c))

    print("%d datasets, %d runs to do (max_steps=%d)\n" % (len(datasets), len(jobs), args.max_steps))
    print("%-24s %-11s %-7s %7s %9s %9s %5s %5s %7s %7s" %
          ("dataset", "config", "status", "events", "metric", "value",
           "tp", "fp", "cd%", "secs"))
    print("-" * 104)

    for path, c in jobs:
        # Config tuples: (label, model_type, warning_signal, drift_signal
        #                 [, model_kwargs [, pipeline_config_overrides]]).
        label, mt, ws, ds = c[:4]
        mk = c[4] if len(c) > 4 else None
        ov = c[5] if len(c) > 5 else None
        row = run_one(path, label, mt, ws, ds, args.max_steps, model_kwargs=mk, cfg_overrides=ov)
        tb = row.pop("_traceback", None)
        rows.append(row)
        print("%-24s %-11s %-7s %7s %9s %9s %5s %5s %7s %7s" % (
            row["dataset"].replace(".csv", "")[:24], label, row["status"],
            row.get("n_events", ""), row.get("quality_metric", ""),
            row.get("quality_value", ""), row.get("tp", ""), row.get("fp", ""),
            row.get("cd_score", ""), row.get("secs", "")))
        if tb:
            print("    " + row["detail"])
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    print("\nwrote %s (%d rows)" % (csv_out, len(rows)))


if __name__ == "__main__":
    main()
