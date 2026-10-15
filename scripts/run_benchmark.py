"""
Benchmark runner for data/dataset_0921: one system (preset) on one registered
dataset, treated as a black box.

Every run writes its raw record (``preds.npz``: y_true, y_pred, alarm indices)
plus a ``manifest.json`` (data hash, preset, effective config, seed, git commit,
package versions, machine, time and memory cost from ``src/metrics/run_cost.py``),
and the metrics come from the single evaluator in
``src/metrics/evaluate_run.py``. ``--reeval`` recomputes every ``metrics.json``
from the stored records, so a metric fix never needs a re-run.

Protocol fields (task, ground truth, delta_max, comparability) come from
``configs/datasets_0921.json``; system settings come from
``configs/presets/<name>.json``. Neither is overridable from the command line.

Datasets are either CSV files (``files``) or generated in memory from a seed
(``generator``: Cerqueira et al. drift injection with the paper's parameters).
Preset kinds: ``pipeline`` (this repo's system), ``baseline`` (a River learner,
plain test-then-train) and ``detector`` (Hoeffding Tree + a River detector in
Cerqueira et al.'s detection-only workflow).

Without --preset / --suite the main method (``main_preset`` in
configs/benchmark_defaults.json, currently e10bft) is run.

Every run executes in its own freshly spawned process (``--workers`` of them at
a time), so its memory numbers are its own even when runs execute in parallel.

Usage:
    python3 scripts/run_benchmark.py --list
    python3 scripts/run_benchmark.py --list-datasets [--json]                   # which data exists here
    python3 scripts/run_benchmark.py --dataset electricity                      # main method only
    python3 scripts/run_benchmark.py --dataset electricity --suite standard --seeds 5 --workers 5
    python3 scripts/run_benchmark.py --dataset electricity --preset e10bft arf100 ht
    python3 scripts/run_benchmark.py --dataset injected_paper_electricity --preset det_adwin --workers 8
    python3 scripts/run_benchmark.py --dataset injected_paper_electricity --preset e10bft --trials 10 --cells abrupt/class_prior
    python3 scripts/run_benchmark.py --dataset electricity --preset arf100 --max-steps 5000   # smoke
    python3 scripts/run_benchmark.py --reeval outputs/benchmark/electricity/e10bft
"""

from __future__ import annotations

import argparse
import dataclasses
import glob
import hashlib
import json
import multiprocessing
import os
import platform
import subprocess
import sys
import threading
import time
import types
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# One BLAS/OpenMP thread per run, set before numpy loads (spawned runs re-import this
# module): idle BLAS pools spin and inflate CPU time, and --workers would oversubscribe cores.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
             "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

REGISTRY_PATH = REPO / "configs" / "datasets_0921.json"
PRESET_DIR = REPO / "configs" / "presets"
DEFAULTS_PATH = REPO / "configs" / "benchmark_defaults.json"
INJECT_DIR = REPO / "data" / "dataset_0921" / "injected_real_dataset" / "script"
DEFAULT_OUT = "outputs/benchmark"
TASK_ALIASES = {"multi_classification": "multiclass"}


# ---------------------------------------------------------------------------
# Registry / presets
# ---------------------------------------------------------------------------
def load_registry() -> Dict[str, Dict[str, Any]]:
    return json.loads(REGISTRY_PATH.read_text())["datasets"]


def load_preset(name: str) -> Dict[str, Any]:
    path = PRESET_DIR / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"unknown preset {name!r}; available: {sorted(p.stem for p in PRESET_DIR.glob('*.json'))}")
    return json.loads(path.read_text())


def dataset_sources(
    entry: Dict[str, Any],
    n_trials: Optional[int],
    trial_start: int = 0,
) -> List[Dict[str, Any]]:
    """One source spec per stream: a CSV file or a generator trial."""
    gen = entry.get("generator")
    if gen is None:
        if trial_start:
            raise ValueError("trial_start applies only to generated datasets")
        files = sorted(Path(p) for p in glob.glob(str(REPO / entry["files"])))
        if not files:
            raise SystemExit(f"no files match {entry['files']}. {entry.get('files_hint', '')}")
        return [{"kind": "file", "csv": str(f), "stem": f.stem} for f in files]
    src = REPO / gen["source"]
    if not src.exists():
        raise SystemExit(f"generator source {gen['source']} is missing; {gen.get('source_hint', '')}")
    if trial_start < 0:
        raise ValueError("trial_start must be non-negative")
    trials = gen["n_trials"] if n_trials is None else n_trials
    if trials < 1:
        raise ValueError("n_trials must be positive")
    trial_stop = trial_start + trials
    if trial_stop > gen["n_trials"]:
        raise ValueError(
            f"trial range [{trial_start}, {trial_stop}) exceeds registered "
            f"n_trials={gen['n_trials']}"
        )
    name = gen["name"]
    return [{"kind": "generated", "method": m, "abruptness": a, "g_id": g,
             "stem": f"{name}_{m}_{a}_g{g:02d}"}
            for a in gen["abruptness"] for m in gen["methods"]
            for g in range(trial_start, trial_stop)]


def _count_rows(path: Path) -> int:
    with open(path, "rb") as f:
        return max(sum(chunk.count(b"\n") for chunk in iter(lambda: f.read(1 << 20), b"")) - 1, 0)


def dataset_status(name: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    """Whether the data for one registry entry exists on this machine."""
    gen = entry.get("generator")
    if gen is None:
        files = sorted(Path(p) for p in glob.glob(str(REPO / entry["files"])))
        available = bool(files)
        n_streams = len(files)
        rows = _count_rows(files[0]) if len(files) == 1 else None
        hint = entry.get("files_hint", "")
    else:
        src = REPO / gen["source"]
        available = src.exists()
        n_streams = gen["n_trials"] * len(gen["methods"]) * len(gen["abruptness"])
        rows = min(_count_rows(src), gen["max_n"]) if available else None
        hint = gen.get("source_hint", "")
    results_dir = REPO / "outputs" / "benchmark" / name
    results = sorted(p.parent.name for p in results_dir.glob("*/runs.csv"))
    return {
        "name": name, "group": entry["group"], "task": entry["task"], "role": entry["role"],
        "comparable": entry["comparable"], "comparable_kinds": entry.get("comparable_kinds"),
        "available": available, "n_streams": n_streams, "rows_per_stream": rows,
        "note": entry.get("comparability_note", ""),
        "missing_hint": "" if available else (hint or f"missing: {entry.get('files') or gen['source']}"),
        "results": results,
    }


def load_gt(csv: Path, entry: Dict[str, Any]) -> Optional[List[Tuple[int, int]]]:
    if entry.get("gt") != "sibling":
        return None
    path = csv.with_name(csv.stem + "_drift_times.txt")
    raw = json.loads(path.read_text()) if path.exists() else []
    return [(int(a), int(b)) for a, b in raw]


# ---------------------------------------------------------------------------
# Streams
# ---------------------------------------------------------------------------
_SOURCE_CACHE: Dict[str, pd.DataFrame] = {}


def _read_source(path: Path) -> pd.DataFrame:
    key = str(path)
    if key not in _SOURCE_CACHE:
        _SOURCE_CACHE[key] = pd.read_csv(path)
    return _SOURCE_CACHE[key]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_hash_path(source: Dict[str, Any], entry: Dict[str, Any]) -> Path:
    """Underlying bytes determining a file or reproducible injected trial."""
    if source["kind"] == "file":
        return Path(source["csv"])
    return REPO / entry["generator"]["source"]


def load_stream(source: Dict[str, Any], entry: Dict[str, Any]) -> Dict[str, Any]:
    """Return X, y (rows the system sees) and ground truth in evaluation coordinates.

    Generated streams drop rows (class prior / feature filtering); Cerqueira et
    al. keep counting dropped rows, so their alarms, drift points and stream
    length are input positions. ``kept`` maps each output row to its input
    position and the ground truth is returned in input coordinates.
    """
    if source["kind"] == "file":
        csv = Path(source["csv"])
        df = pd.read_csv(csv)
        cell = None
        if entry.get("cell_from_meta"):
            meta = json.loads(csv.with_suffix(".json").read_text())
            cell = "/".join(str(meta[k]) for k in entry["cell_from_meta"])
        return {"df": df, "gt": load_gt(csv, entry), "kept": None, "n_input": len(df), "cell": cell,
                "data_id": {"file": str(csv.relative_to(REPO)), "sha256": sha256_of(csv)}}

    os.environ.setdefault("MPLBACKEND", "Agg")
    if str(INJECT_DIR) not in sys.path:
        sys.path.insert(0, str(INJECT_DIR))
    from common import deterministic_seed  # injected_real_dataset/script/common.py
    from inject import inject_stream

    gen = entry["generator"]
    src = REPO / gen["source"]
    seed = deterministic_seed(gen["seed_tag"], gen["name"], source["method"], source["abruptness"], source["g_id"])
    out, _, meta, _, kept = inject_stream(
        _read_source(src),
        method=source["method"],
        abruptness=source["abruptness"],
        drift_width=int(gen["width"]),
        rng=np.random.default_rng(seed),
        max_n=gen.get("max_n"),
        drift_region=tuple(gen.get("drift_region", (0.5, 0.8))),
        label_skip_proba=float(gen.get("label_skip_proba", 0.75)),
        width_cap=None,
        truncate_after_shuffle=bool(gen.get("truncate_after_shuffle", True)),
    )
    gt = [(int(a), int(b)) for a, b in meta["drift_times_input"]]
    data_id = {"generator": gen, "source_sha256": sha256_of(src), "seed": seed,
               "method": source["method"], "abruptness": source["abruptness"], "g_id": source["g_id"],
               "trial_meta": {k: meta[k] for k in ("n_input", "n_output", "drift_onset_input", "drift_end_input",
                                                   "drift_width", "y_selected", "y_swap", "x_filter_idx")}}
    return {"df": out, "gt": gt, "kept": np.asarray(kept, dtype=np.int64), "n_input": int(meta["n_input"]),
            "cell": f"{source['abruptness']}/{source['method']}", "data_id": data_id}


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------
def git_state() -> Dict[str, Any]:
    def run(*cmd: str) -> str:
        return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True).stdout.strip()

    return {"commit": run("git", "rev-parse", "HEAD"), "dirty": bool(run("git", "status", "--porcelain"))}


def versions() -> Dict[str, str]:
    import river

    return {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
            "river": river.__version__}


def check_requirements(preset: Dict[str, Any], allow_mismatch: bool) -> List[str]:
    installed = versions()
    problems = [f"{pkg} {installed.get(pkg)} != required {want}"
                for pkg, want in preset.get("requires", {}).items() if installed.get(pkg) != want]
    if problems and not allow_mismatch:
        raise SystemExit("version mismatch: " + "; ".join(problems) + " (use --allow-version-mismatch to run anyway)")
    return problems


# ---------------------------------------------------------------------------
# Systems
# ---------------------------------------------------------------------------
def _set_path(d: Dict[str, Any], dotted: str, value: Any) -> None:
    keys = dotted.split(".")
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


def effective_pipeline_config(preset: Dict[str, Any], task: str, seed: Optional[int]) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(preset["config"]))
    for k, v in preset.get("task_overrides", {}).get(task, {}).items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            cfg[k].update(v)
        else:
            cfg[k] = v
    if seed is not None and preset.get("seed_param"):
        _set_path(cfg, preset["seed_param"], seed)
    return cfg


def oracle_input_schedule(
    gt: Optional[List[Tuple[int, int]]], position: np.ndarray, *, allow_empty: bool = False
) -> List[Dict[str, Any]]:
    """Map raw drift start/+60 to first retained rows at or after each point."""
    if not gt and not allow_empty:
        raise ValueError("oracle_input_60 requires nonempty ground truth")
    if not gt:
        return []
    if len(position) and np.any(np.diff(position) <= 0):
        raise ValueError("input positions must be strictly increasing")
    schedule: List[Dict[str, Any]] = []
    for start, _ in gt:
        warning_idx = int(np.searchsorted(position, start, side="left"))
        if warning_idx >= len(position):
            continue
        confirm_idx = int(np.searchsorted(position, start + 60, side="left"))
        schedule.append({
            "warning_index": warning_idx,
            "confirm_index": confirm_idx if confirm_idx < len(position) else None,
            "raw_start": int(start),
            "raw_confirm": int(start + 60),
        })
    for left, right in zip(schedule, schedule[1:]):
        if left["confirm_index"] is None or left["confirm_index"] >= right["warning_index"]:
            raise ValueError("overlapping or censored oracle schedule cannot be replayed")
    return schedule


def _stub_type_ldd_if_missing() -> bool:
    """Type-LDD only annotates drift types on the ECPF path; stub it when torch is absent."""
    try:
        import torch  # noqa: F401
        return False
    except ImportError:
        from src.config import DriftType

        stub = types.ModuleType("src.drift_type_classifier_type_ldd")
        stub.classify_drift_type = lambda errors, idx, **kw: DriftType.SUDDEN
        sys.modules["src.drift_type_classifier_type_ldd"] = stub
        return True


def preload_libraries(preset: Dict[str, Any]) -> None:
    """Import what a run needs before its memory baseline, so library code is not counted as system memory."""
    import importlib

    import river.drift.binary  # noqa: F401
    from river import ensemble, forest, naive_bayes, tree  # noqa: F401

    if preset["kind"] == "pipeline":
        if preset.get("config", {}).get("use_ecpf"):
            _stub_type_ldd_if_missing()
        for mod in ("src.config", "src.pipeline", "src.ecpf", "src.ecpf_detector", "src.model_adapter",
                    "src.prediction_model", "src.models.base_model"):
            importlib.import_module(mod)


def run_pipeline(X: np.ndarray, y: np.ndarray, cfg_dict: Dict[str, Any], warm_start: int) -> Dict[str, Any]:
    stubbed = _stub_type_ldd_if_missing() if cfg_dict.get("use_ecpf") else False
    from src.config import PipelineConfig
    from src.pipeline import ConceptDriftPipeline

    fields = {f.name for f in dataclasses.fields(PipelineConfig)}
    unknown = set(cfg_dict) - fields
    if unknown:
        raise ValueError(f"preset sets unknown PipelineConfig fields: {sorted(unknown)}")
    cfg = PipelineConfig(**cfg_dict)
    pipe = ConceptDriftPipeline(cfg)
    y_pred = np.full(len(y), np.nan)
    alarm_idx: List[int] = []
    alarm_ts: List[int] = []
    for i, _, yp, dets, _ in pipe.run_stream(X, y, warm_start_samples=warm_start, prequential_warm_start=True):
        y_pred[i] = yp
        raw = [d for d in dets if d.raw_drift]
        if raw:
            alarm_idx.append(i)
            alarm_ts.append(int(raw[0].timestamp))
    if cfg.ecpf_record_warning_events and pipe._ecpf_warning_active:
        pipe._record_ecpf_warning(len(y) - 1, "censored", "stream_end")
    effective = {k: v for k, v in dataclasses.asdict(cfg).items() if k in fields}
    return {"y_pred": y_pred, "alarm_idx": alarm_idx, "alarm_ts": alarm_ts, "emits_alarms": True,
            "type_ldd_stubbed": stubbed, "effective_config": effective,
            "warning_events": pipe._ecpf_warning_events,
            "frozen_steps": pipe._ecpf_frozen_steps,
            "system": pipe}


def make_learner(learner: str, params: Dict[str, Any]):
    from river import ensemble, forest, naive_bayes, tree

    factories = {
        "arf": forest.ARFClassifier,
        "srp": ensemble.SRPClassifier,
        "ht": tree.HoeffdingTreeClassifier,
        "nb": naive_bayes.GaussianNB,
        "htr": tree.HoeffdingTreeRegressor,
    }
    if learner not in factories:
        raise ValueError(f"unknown learner {learner!r}")
    return factories[learner](**params)


class MOAADWINChangeDetector:
    """MOA ``ADWINChangeDetector`` semantics on River's ADWIN window (what CapyMOA's ADWIN runs).

    Unlike ``river.drift.ADWIN`` the window is never reset after a detection
    (ADWIN only drops the old sub-window, so a lasting change fires repeatedly),
    and a cut only counts as a change when the window mean went up.
    """

    def __init__(self, delta: float = 0.002, clock: int = 32, max_buckets: int = 5,
                 min_window_length: int = 5, grace_period: int = 10):
        from river.drift.adwin_c import AdaptiveWindowing

        self._w = AdaptiveWindowing(delta=delta, clock=clock, max_buckets=max_buckets,
                                    min_window_length=min_window_length, grace_period=grace_period)
        self.drift_detected = False

    def _estimation(self) -> float:
        width = self._w.get_width()
        return self._w.get_total() / width if width > 0 else 0.0

    def update(self, x: float) -> None:
        before = self._estimation()
        self.drift_detected = bool(self._w.update(x)) and self._estimation() > before


def make_detector(name: str, params: Dict[str, Any]):
    from river import drift
    from detectors.core.rddm_moa import MOARDDM
    from detectors.core.magseed_candidate import MagSeedCandidate
    from detectors.core.magseed_thesis_candidate import (
        MagSeed, MagSeedLiteral, MagSeedThesisCandidate, MagSeedUpward,
    )

    factories = {
        "adwin_moa": MOAADWINChangeDetector,
        "adwin": drift.ADWIN,
        "page_hinkley": drift.PageHinkley,
        "kswin": drift.KSWIN,
        "ddm": drift.binary.DDM,
        "eddm": drift.binary.EDDM,
        "hddm_a": drift.binary.HDDM_A,
        "hddm_w": drift.binary.HDDM_W,
        "rddm": MOARDDM,
        "magseed_candidate": MagSeedCandidate,
        "magseed_thesis_candidate": MagSeedThesisCandidate,
        "magseed": MagSeed,
        "magseed_upward": MagSeedUpward,
        "magseed_literal_dev": MagSeedLiteral,
    }
    if name not in factories:
        raise ValueError(f"unknown detector {name!r}")
    return factories[name](**params)


def _seeded(params: Dict[str, Any], seed_param: Optional[str], seed: Optional[int]) -> Dict[str, Any]:
    params = dict(params)
    if seed is not None and seed_param:
        params[seed_param] = seed
    return params


def run_baseline(X: np.ndarray, y: np.ndarray, preset: Dict[str, Any], task: str, seed: Optional[int]) -> Dict[str, Any]:
    params = _seeded(preset.get("params", {}), preset.get("seed_param"), seed)
    model = make_learner(preset["learner"], params)
    is_clf = task != "regression"
    labels = y.astype(int) if is_clf else y
    y_pred = np.empty(len(y))
    for i in range(len(y)):
        x = dict(enumerate(X[i].tolist()))
        p = model.predict_one(x)
        # An untrained model abstains; MOA scores that as class 0 (argmax of empty votes).
        y_pred[i] = 0.0 if p is None else float(p)
        model.learn_one(x, labels[i].item())
    return {"y_pred": y_pred, "alarm_idx": [], "alarm_ts": [], "emits_alarms": False,
            "effective_config": {"learner": preset["learner"], **params}, "system": model}


def run_detector(X: np.ndarray, y: np.ndarray, preset: Dict[str, Any], position: np.ndarray,
                 n_input: int, seed: Optional[int]) -> Dict[str, Any]:
    """Cerqueira et al. ``SupervisedStreamingWorkflow``: the learner trains on every
    instance and is never reset; after ``min_train_fraction`` of the input stream
    the detector receives ``int(y == y_pred)`` (``"error"`` feeds the complement)."""
    model = make_learner(preset["learner"], _seeded(preset.get("params", {}), preset.get("seed_param"), seed))
    det = make_detector(preset["detector"], preset.get("detector_params", {}))
    min_train = int(n_input * float(preset.get("min_train_fraction", 0.25)))
    feed_error = preset.get("signal", "correct") == "error"
    labels = y.astype(int)
    y_pred = np.empty(len(y))
    alarms: List[int] = []
    for i in range(len(y)):
        x = dict(enumerate(X[i].tolist()))
        p = model.predict_one(x)
        p = 0 if p is None else int(p)
        y_pred[i] = p
        if position[i] > min_train:
            hit = int(p == labels[i])
            det.update(1 - hit if feed_error else hit)
            if det.drift_detected:
                alarms.append(i)
        model.learn_one(x, labels[i].item())
    return {"y_pred": y_pred, "alarm_idx": alarms, "alarm_ts": alarms, "emits_alarms": True,
            "effective_config": {"learner": preset["learner"], "detector": preset["detector"],
                                 "detector_params": preset.get("detector_params", {}),
                                 "min_train": min_train, "signal": preset.get("signal", "correct")},
            "system": (model, det)}


# ---------------------------------------------------------------------------
# One run
# ---------------------------------------------------------------------------
def evaluate_record(rec: Dict[str, Any], entry: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
    from src.metrics.evaluate_run import evaluate_run

    input_coords = manifest.get("coordinates") == "input" and "alarm_idx_input" in rec
    gt = manifest["gt_intervals"] if manifest["emits_alarms"] else None
    return evaluate_run(
        rec["y_true"], rec["y_pred"],
        task=manifest["task"],
        alarms=rec["alarm_idx_input"] if input_coords else rec["alarm_idx"],
        gt_intervals=gt,
        delta_max=entry.get("delta_max"),
        warm_start=manifest["warm_start"],
        window=entry.get("window", 1000),
        n_classes=manifest.get("n_classes"),
        detect_from=int(manifest.get("detect_from") or 0),
        detection_n_instances=manifest.get("n_input") if input_coords else None,
    )


def detect_from_for(entry: Dict[str, Any], n_input: int) -> int:
    frac = entry.get("detect_from_fraction")
    return int(n_input * float(frac)) + 1 if frac else 0


def run_one(job: Dict[str, Any]) -> Dict[str, Any]:
    warnings.filterwarnings("ignore")
    sys.setrecursionlimit(20_000)  # ECPF deep-clones River trees recursively
    entry, preset, seed = job["entry"], job["preset"], job["seed"]
    task = TASK_ALIASES.get(entry["task"], entry["task"])

    stream = load_stream(job["source"], entry)
    df, gt, kept, n_input = stream["df"], stream["gt"], stream["kept"], stream["n_input"]
    y = df["y"].to_numpy(dtype=float)
    X = df.drop(columns=["y"]).to_numpy(dtype=np.float64)
    n_classes = int(y.max()) + 1 if task != "regression" else None
    if job["max_steps"] and job["max_steps"] < len(y):
        ms = job["max_steps"]
        X, y = X[:ms], y[:ms]
        if kept is not None:
            kept = kept[:ms]
            n_input = int(kept[-1]) + 1
        else:
            n_input = ms
        gt = None if gt is None else [iv for iv in gt if iv[0] < n_input]
    position = kept if kept is not None else np.arange(len(y))

    from src.metrics.run_cost import CostMeter, deep_sizeof, process_peak_rss_mb

    warm_start = int(preset.get("warm_start", 0))
    preload_libraries(preset)
    meter = CostMeter()
    meter.start()
    kind = preset["kind"]
    if kind == "pipeline":
        config = effective_pipeline_config(preset, task, seed)
        if job.get("record_warning_events"):
            config["ecpf_record_warning_events"] = True
        if config.get("ecpf_signal_mode") == "oracle_input_60":
            config["ecpf_oracle_input_schedule"] = oracle_input_schedule(
                gt, position, allow_empty=bool(job["max_steps"])
            )
        out = run_pipeline(X, y, config, warm_start)
    elif kind == "baseline":
        if task not in preset.get("tasks", [task]):
            raise ValueError(f"preset {preset['name']} does not support task {task}")
        warm_start = 0
        out = run_baseline(X, y, preset, task, seed)
    elif kind == "detector":
        if task == "regression":
            raise ValueError("detector presets are classification-only")
        warm_start = 0
        out = run_detector(X, y, preset, position, n_input, seed)
    else:
        raise ValueError(f"unknown preset kind {kind!r}")
    cost = meter.stop(len(y))
    cost["process_peak_rss_mb"] = process_peak_rss_mb()
    cost["model_size_final_mb"] = None
    if job["model_size"]:
        t_size = time.perf_counter()
        cost["model_size_final_mb"] = round(deep_sizeof(out["system"], exclude=(X, y, df)) / 2 ** 20, 2)
        cost["model_size_time_s"] = round(time.perf_counter() - t_size, 2)
    cost["workers"] = job["workers"]

    run_dir = Path(job["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)
    alarm_idx = np.asarray(out["alarm_idx"], dtype=np.int64)
    rec = {"y_true": y, "y_pred": out["y_pred"], "alarm_idx": alarm_idx,
           "alarm_ts": np.asarray(out["alarm_ts"], dtype=np.int64)}
    if kept is not None:
        rec["alarm_idx_input"] = position[alarm_idx] if len(alarm_idx) else alarm_idx
    np.savez_compressed(run_dir / "preds.npz", **rec)

    events = [dict(event, input_index=int(position[event["index"]]))
              for event in out.get("warning_events", [])]
    if job.get("record_warning_events"):
        (run_dir / "warning_events.json").write_text(json.dumps(events, indent=2))

    manifest = {
        "dataset": job["dataset"],
        "stream": job["source"]["stem"],
        "data": stream["data_id"],
        "cell": stream["cell"],
        "task": task,
        "n_classes": n_classes,
        "coordinates": "input" if kept is not None else "output",
        "n_input": n_input,
        "detect_from": detect_from_for(entry, n_input),
        "gt_intervals": gt,
        "registry_entry": entry,
        "preset": preset,
        "effective_config": out["effective_config"],
        "seed": seed,
        "warm_start": warm_start,
        "prequential_warm_start": True,
        "max_steps": job["max_steps"] or None,
        "record_warning_events": bool(job.get("record_warning_events")),
        "emits_alarms": out["emits_alarms"],
        "type_ldd_stubbed": out.get("type_ldd_stubbed", False),
        "version_problems": job["version_problems"],
        "git": job["git"],
        "versions": versions(),
        "machine": job["machine"],
        "cost": cost,
        "runtime_s": round(cost["runtime_s"], 2),
        "peak_rss_mb": cost["process_peak_rss_mb"],
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=_json_default))
    metrics = evaluate_record(rec, entry, manifest)
    if job.get("record_warning_events"):
        metrics.update({
            "warning_open_count": sum(e["event"] == "open" for e in events),
            "warning_close_count": sum(e["event"] == "close" for e in events),
            "warning_censored_count": sum(e["event"] == "censored" for e in events),
            "warning_timeout_count": sum(e["reason"] == "timeout" for e in events),
            "warning_frozen_steps": int(out.get("frozen_steps", 0)),
        })
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return summary_row(manifest, metrics, run_dir)


def _json_default(o: Any) -> Any:
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serializable: {type(o)}")


def run_isolated(job: Dict[str, Any]) -> Dict[str, Any]:
    """One run in its own freshly spawned process, so its memory numbers start from zero."""
    with ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn")) as pool:
        return pool.submit(run_one_big_stack, job).result()


class ConcurrencyTracker:
    """Highest number of runs executing at the same time during each run's lifetime."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._peak: Dict[str, int] = {}

    def enter(self, key: str) -> None:
        with self._lock:
            self._peak[key] = 0
            n = len(self._peak)
            for k in self._peak:
                self._peak[k] = max(self._peak[k], n)

    def leave(self, key: str) -> int:
        with self._lock:
            return self._peak.pop(key)


def record_concurrency(row: Dict[str, Any], peak: int) -> None:
    """Store the observed concurrency in the run's manifest and summary row."""
    path = REPO / row["run_dir"] / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest.setdefault("cost", {})["concurrent_runs"] = peak
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    row["concurrent_runs"] = peak


def run_one_big_stack(job: Dict[str, Any]) -> Dict[str, Any]:
    """Run in a thread with a large C stack: pickling deep River trees recurses per tree level."""
    result: Dict[str, Any] = {}
    error: List[BaseException] = []

    def target() -> None:
        try:
            result.update(run_one(job))
        except BaseException as exc:
            error.append(exc)

    old = threading.stack_size(512 * 1024 * 1024)
    try:
        t = threading.Thread(target=target)
        t.start()
        t.join()
    finally:
        threading.stack_size(old)
    if error:
        raise error[0]
    return result


def comparability(manifest: Dict[str, Any]) -> Tuple[bool, str]:
    entry = manifest["registry_entry"]
    if not entry.get("comparable"):
        return False, "dataset not comparable"
    if manifest["max_steps"]:
        return False, "truncated (--max-steps)"
    if manifest["version_problems"]:
        return False, "version mismatch"
    kinds = entry.get("comparable_kinds")
    if kinds and manifest["preset"]["kind"] not in kinds:
        return False, f"protocol needs preset kind {kinds}"
    return True, ""


COST_COLUMNS = ["cpu_time_s", "instances_per_s", "rss_before_mb", "rss_peak_mb", "rss_increment_mb",
                "ram_hours_gb", "process_peak_rss_mb", "model_size_final_mb", "workers", "concurrent_runs"]


def summary_row(manifest: Dict[str, Any], metrics: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
    ok, why = comparability(manifest)
    cost = manifest.get("cost", {})
    machine = manifest.get("machine") or {}
    return {
        "dataset": manifest["dataset"],
        "stream": manifest.get("stream") or Path(manifest.get("file", "")).stem,
        "cell": manifest["cell"],
        "preset": manifest["preset"]["name"],
        "preset_kind": manifest["preset"]["kind"],
        "seed": manifest["seed"],
        "comparable": ok,
        "not_comparable_reason": why,
        "smoke": bool(manifest["max_steps"]),
        "runtime_s": manifest["runtime_s"],
        **{c: cost.get(c) for c in COST_COLUMNS},
        "machine": f"{machine.get('cpu', '')} / {machine.get('ram_gb', '')} GB" if machine else None,
        "run_dir": str(run_dir.relative_to(REPO)),
        **metrics,
    }


# ---------------------------------------------------------------------------
# Re-evaluation and summaries
# ---------------------------------------------------------------------------
def reeval(root: Path) -> List[Dict[str, Any]]:
    registry = load_registry()
    rows = []
    for mpath in sorted(root.rglob("manifest.json")):
        run_dir = mpath.parent
        manifest = json.loads(mpath.read_text())
        entry = registry.get(manifest["dataset"], manifest["registry_entry"])
        manifest["registry_entry"] = entry
        with np.load(run_dir / "preds.npz") as z:
            rec = {k: z[k] for k in z.files}
        metrics = evaluate_record(rec, entry, manifest)
        (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
        rows.append(summary_row(manifest, metrics, run_dir))
    return rows


def print_summary(df: pd.DataFrame, entry: Dict[str, Any]) -> None:
    keys = [m for m in entry.get("required_metrics", []) if m in df.columns]
    if not keys:
        return
    by = ["preset", "cell"] if df["cell"].notna().any() else ["preset"]
    num = df[by + keys].copy()
    for k in keys:
        num[k] = pd.to_numeric(num[k], errors="coerce")
    agg = num.groupby(by, dropna=False)[keys].agg(["mean", "std", "count"])
    with pd.option_context("display.width", 200, "display.max_columns", 50):
        print(agg.round(4).to_string())
    cost_keys = [c for c in ("runtime_s", "cpu_time_s", "rss_increment_mb", "ram_hours_gb", "model_size_final_mb",
                             "concurrent_runs")
                 if c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any()]
    if cost_keys:
        cost = df[["preset"] + cost_keys].copy()
        for k in cost_keys:
            cost[k] = pd.to_numeric(cost[k], errors="coerce")
        print("\ncost (mean per run; memory is per process; wall time is only strict where concurrent_runs = 1):")
        with pd.option_context("display.width", 200, "display.max_columns", 50):
            print(cost.groupby("preset")[cost_keys].mean().round(4).to_string())
    if "comparable" in df and not df["comparable"].astype(bool).all():
        reasons = sorted(set(df.loc[~df["comparable"].astype(bool), "not_comparable_reason"]))
        print(f"\n[not comparable] {'; '.join(reasons)}. {entry.get('comparability_note', '')}")
    for ref in entry.get("sota", []):
        if ref["metric"] in df.columns:
            print(f"  literature {ref['metric']:<22} {ref['value']:.4f}  {ref['method']} ({ref['source']})")
    if "n_gt" in df and df["cell"].notna().any() and pd.to_numeric(df["n_gt"], errors="coerce").fillna(0).gt(0).any():
        from src.metrics.evaluate_run import pool_detection_runs

        print("\npooled over trials (how Cerqueira et al. report a cell):")
        refs = entry.get("sota_by_cell", {})
        for (preset, cell), g in df.groupby(["preset", "cell"]):
            p = pool_detection_runs(g.to_dict("records"))
            if not p:
                continue
            ref = refs.get(cell)
            lit = f"   literature best {ref['method']} f1={ref['value']:.3f} mdt={ref.get('mdt')}" if ref else ""
            mdt = "-" if p["mdt"] is None else f"{p['mdt']:.0f}"
            print(f"  {preset:<18} {cell:<28} f1={p['f1']:.3f} P={p['precision']:.3f} R={p['recall']:.3f} "
                  f"ep_recall={p['episode_recall']:.2f} mdt={mdt} far={p['far_cerqueira']:.2f} (n={p['n_runs']}){lit}")


def load_defaults() -> Dict[str, Any]:
    return json.loads(DEFAULTS_PATH.read_text())


def resolve_presets(names: Optional[List[str]], suite: Optional[str], defaults: Dict[str, Any]) -> List[str]:
    """Explicit presets win; otherwise the suite; otherwise the main method."""
    if names:
        return names
    if suite:
        if suite not in defaults["suites"]:
            raise SystemExit(f"unknown suite {suite!r}; available: {sorted(defaults['suites'])}")
        return list(defaults["suites"][suite]["presets"])
    return [defaults["main_preset"]]


def supports_task(preset: Dict[str, Any], task: str) -> bool:
    tasks = preset.get("tasks")
    if preset["kind"] == "detector" and task == "regression":
        return False
    return tasks is None or task in tasks


def resumable_row(job: Dict[str, Any], source_hash: str) -> Optional[Dict[str, Any]]:
    """Return a completed row; reject any conflicting provenance before work starts."""
    run_dir = Path(job["run_dir"])
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None  # an interrupted run is safe to regenerate
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resume corrupt manifest {manifest_path}: {exc}") from exc
    expected = {
        "dataset": job["dataset"],
        "stream": job["source"]["stem"],
        "preset": job["preset"],
        "registry_entry": job["entry"],
        "seed": job["seed"],
        "max_steps": job["max_steps"] or None,
        "record_warning_events": bool(job.get("record_warning_events")),
        "git": job["git"],
        "version_problems": job["version_problems"],
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"resume mismatch at {manifest_path}: {key}")
    data = manifest.get("data") or {}
    actual_hash = data.get("sha256") if job["source"]["kind"] == "file" else data.get("source_sha256")
    if actual_hash != source_hash:
        raise ValueError(f"resume mismatch at {manifest_path}: data SHA-256")
    if job["source"]["kind"] == "file":
        expected_file = str(source_hash_path(job["source"], job["entry"]).relative_to(REPO))
        if data.get("file") != expected_file:
            raise ValueError(f"resume mismatch at {manifest_path}: data path")
    if not (run_dir / "preds.npz").exists() or not (run_dir / "metrics.json").exists():
        return None
    if job.get("record_warning_events") and not (run_dir / "warning_events.json").exists():
        return None
    try:
        with np.load(run_dir / "preds.npz") as rec:
            for required in ("y_true", "y_pred", "alarm_idx", "alarm_ts"):
                _ = rec[required].shape
        metrics = json.loads((run_dir / "metrics.json").read_text())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resume corrupt completed run {run_dir}: {exc}") from exc
    return summary_row(manifest, metrics, run_dir)


def run_preset(args: argparse.Namespace, entry: Dict[str, Any], preset: Dict[str, Any], git: Dict[str, Any]) -> None:
    version_problems = check_requirements(preset, args.allow_version_mismatch)
    sources = dataset_sources(entry, args.trials, args.trial_start)
    if args.cells:
        sources = [s for s in sources if f"{s.get('abruptness')}/{s.get('method')}" in args.cells
                   or any(c in s["stem"] for c in args.cells)]
    if args.limit_files:
        sources = sources[: args.limit_files]
    seeds: List[Optional[int]] = list(range(args.seeds)) if preset.get("seed_param") else [None]
    if args.seeds > 1 and not preset.get("seed_param"):
        print(f"preset {preset['name']} is deterministic; running one seed")

    root = REPO / args.out_dir / args.dataset / preset["name"]
    jobs = [{
        "source": s, "dataset": args.dataset, "entry": entry, "preset": preset, "seed": seed,
        "max_steps": args.max_steps, "version_problems": version_problems, "git": git,
        "record_warning_events": bool(args.record_warning_events or preset["name"].startswith("det1_")),
        "machine": args.machine, "workers": max(1, args.workers), "model_size": args.model_size,
        "run_dir": str(root / (s["stem"] + ("" if seed is None else f"__s{seed}"))),
    } for s in sources for seed in seeds]
    role = preset.get("role", preset["kind"])
    print(f"\n{len(jobs)} runs: {args.dataset} x {preset['name']} [{role}] "
          f"({len(sources)} streams x {len(seeds)} seeds) -> {root}")

    rows: List[Dict[str, Any]] = []
    if args.resume:
        if git["dirty"]:
            raise SystemExit("--resume requires a clean worktree so the commit identifies the code")
        hashes: Dict[Path, str] = {}
        pending = []
        for job in jobs:
            path = source_hash_path(job["source"], entry)
            if path not in hashes:
                hashes[path] = sha256_of(path)
            previous = resumable_row(job, hashes[path])
            if previous is None:
                pending.append(job)
            else:
                rows.append(previous)
        print(f"resume: {len(rows)} verified complete, {len(pending)} pending", flush=True)
        jobs_to_run = pending
    else:
        jobs_to_run = jobs
    tracker = ConcurrencyTracker()
    peaks: Dict[str, int] = {}

    def run_tracked(job: Dict[str, Any]) -> Dict[str, Any]:
        tracker.enter(job["run_dir"])
        try:
            return run_isolated(job)
        finally:
            peaks[job["run_dir"]] = tracker.leave(job["run_dir"])

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(run_tracked, j): j for j in jobs_to_run}
        for n, fut in enumerate(as_completed(futs), 1):
            j = futs[fut]
            try:
                r = fut.result()
                record_concurrency(r, peaks[j["run_dir"]])
            except Exception as exc:
                r = {"dataset": args.dataset, "stream": j["source"]["stem"], "preset": preset["name"],
                     "seed": j["seed"], "error": repr(exc)}
            rows.append(r)
            acc, f1 = r.get("acc_prequential"), r.get("f1")
            print(f"[{n}/{len(jobs)}] {r['stream']:52s} seed={r['seed']} "
                  f"acc={'-' if acc is None else f'{acc:.4f}'} f1={'-' if f1 is None else f'{f1:.3f}'} "
                  f"{r.get('error', '')}", flush=True)

    df = pd.DataFrame(rows)
    root.mkdir(parents=True, exist_ok=True)
    # Merge with earlier runs of this dataset x preset so a partial re-run (fewer seeds,
    # a subset of trials) does not drop rows of run directories that still exist.
    runs_csv = root / "runs.csv"
    merged = df
    if runs_csv.exists() and "run_dir" in df:
        old = pd.read_csv(runs_csv)
        if "run_dir" in old:
            old = old[old["run_dir"].notna() & ~old["run_dir"].isin(df["run_dir"].dropna())]
            merged = pd.concat([old, df], ignore_index=True)
    merged.to_csv(runs_csv, index=False)
    if "error" in df and df["error"].notna().any():
        print(df[df["error"].notna()][["stream", "seed", "error"]].to_string(index=False))
        df = df[df["error"].isna()]
    if len(df):
        print_summary(df, entry)
    print(f"\nruns -> {runs_csv} ({len(merged)} rows incl. earlier runs)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset")
    ap.add_argument("--preset", nargs="+", default=None,
                    help="one or more presets (default: main_preset in configs/benchmark_defaults.json)")
    ap.add_argument("--suite", default=None, help="named preset set from configs/benchmark_defaults.json, e.g. standard")
    ap.add_argument("--seeds", type=int, default=1, help="seeds 0..N-1; ignored for deterministic presets")
    ap.add_argument("--limit-files", type=int, default=0)
    ap.add_argument("--trials", type=int, default=None, help="generated datasets: trials per cell (default: registry)")
    ap.add_argument("--trial-start", type=int, default=0,
                    help="generated datasets: zero-based first trial; use with --trials")
    ap.add_argument("--cells", nargs="+", default=None, help="only these cells, e.g. abrupt/class_prior")
    ap.add_argument("--max-steps", type=int, default=0, help="truncate streams (smoke test; marks runs non-comparable)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--allow-version-mismatch", action="store_true")
    ap.add_argument("--resume", action="store_true", help="skip only complete runs whose commit, preset, protocol and source hash match")
    ap.add_argument("--record-warning-events", action="store_true", help="passively record ECPF warning lifecycle events")
    ap.add_argument("--model-size", action=argparse.BooleanOptionalAction, default=True,
                    help="measure the final system's object size after each run (can take a minute for 100-tree "
                         "forests on long streams; --no-model-size skips it)")
    ap.add_argument("--reeval", metavar="DIR", help="recompute metrics.json under DIR from stored preds.npz")
    ap.add_argument("--list", action="store_true", help="list registered datasets and presets")
    ap.add_argument("--list-datasets", action="store_true",
                    help="list every registered dataset and whether its data exists on this machine")
    ap.add_argument("--json", action="store_true", help="with --list-datasets: print JSON")
    args = ap.parse_args()

    registry = load_registry()
    defaults = load_defaults()
    if args.list_datasets:
        status = [dataset_status(n, e) for n, e in registry.items()]
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=1))
            return
        for s in status:
            comp = "comparable" if s["comparable"] else "reference"
            if s["comparable_kinds"]:
                comp += f"({'/'.join(s['comparable_kinds'])} only)"
            rows = f"{s['rows_per_stream']:,}" if s["rows_per_stream"] else "-"
            mark = "ok     " if s["available"] else "MISSING"
            print(f"{mark} {s['name']:48s} {s['task']:10s} role={s['role']:6s} {comp:28s} "
                  f"streams={s['n_streams']:<4d} rows/stream={rows:<8s} results={','.join(s['results']) or '-'}")
            if not s["available"]:
                print(f"        -> {s['missing_hint']}")
        return
    if args.list:
        for name, e in registry.items():
            print(f"{name:52s} {e['group']:9s} {e['task']:10s} role={e['role']:6s} comparable={e['comparable']}")
        print(f"\npresets (main method: {defaults['main_preset']}):")
        for p in sorted(PRESET_DIR.glob("*.json")):
            pr = json.loads(p.read_text())
            print(f"  {p.stem:20s} {pr.get('role', pr['kind']):19s} {pr['description'][:90]}")
        print("\nsuites:")
        for name, s in defaults["suites"].items():
            print(f"  {name:12s} {', '.join(s['presets'])}")
        return

    if args.reeval:
        root = (REPO / args.reeval) if not Path(args.reeval).is_absolute() else Path(args.reeval)
        rows = reeval(root)
        df = pd.DataFrame(rows)
        df.to_csv(root / "runs.csv", index=False)
        print(f"re-evaluated {len(rows)} runs -> {root / 'runs.csv'}")
        for ds in df["dataset"].unique():
            print_summary(df[df["dataset"] == ds], registry[ds])
        return

    if not args.dataset:
        ap.error("--dataset is required (or use --list / --reeval)")
    if args.dataset not in registry:
        raise SystemExit(f"unknown dataset {args.dataset!r}; see --list")
    entry = registry[args.dataset]
    if args.trial_start and args.trials is None:
        ap.error("--trial-start requires --trials")
    task = TASK_ALIASES.get(entry["task"], entry["task"])
    names = resolve_presets(args.preset, args.suite, defaults)
    presets = [load_preset(n) for n in names]
    skipped = [p["name"] for p in presets if not supports_task(p, task)]
    presets = [p for p in presets if supports_task(p, task)]
    excluded = [p["name"] for p in presets if p.get("datasets") and args.dataset not in p["datasets"]]
    presets = [p for p in presets if not p.get("datasets") or args.dataset in p["datasets"]]
    if skipped:
        print(f"skipping presets that do not support task {task}: {', '.join(skipped)}")
    if excluded:
        print(f"skipping presets outside dataset scope: {', '.join(excluded)}")
    if not presets:
        raise SystemExit("no preset left to run")
    if not args.preset and not args.suite:
        print(f"no preset given: running the main method {defaults['main_preset']}")
    git = git_state()
    if git["dirty"]:
        print("warning: working tree has uncommitted changes; the manifest records the commit only")
    from src.metrics.run_cost import machine_info, rss_available

    if not rss_available():
        print("warning: psutil is not installed, so memory (RSS) is not recorded; pip install -r requirements.txt")
    args.machine = machine_info()
    print(f"machine: {args.machine['cpu']}, {args.machine['cpu_count']} cores, {args.machine['ram_gb']} GB RAM; "
          f"{max(1, args.workers)} parallel run(s), each in its own process")
    for preset in presets:
        run_preset(args, entry, preset, git)


if __name__ == "__main__":
    main()
