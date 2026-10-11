"""
A/B experiment for two optional ECPF mechanisms (see src/ecpf.py docstring):

* swap policy  : strict (paper)  vs  hoeffding (ARCUS/ARF-style reliability)
* fade policy  : ecpf (paper)    vs  reuse_value (AiRStream-style valuation)

Four variants (baseline / hoeffding / reuse_value / both) are run on every
recurring stream under each setting, and per-run metrics are written to
``<out-dir>/runs.csv`` plus a per-(setting, variant) summary.

Type-LDD is annotation-only on the ECPF path, so it is stubbed out here to
avoid the torch dependency; it does not influence any ECPF decision.

Usage:
    python3 scripts/experiment_ecpf_swap_fade.py --workers 8
    python3 scripts/experiment_ecpf_swap_fade.py --max-steps 20000 --limit-files 2   # smoke
"""

from __future__ import annotations

import argparse
import sys
import time
import types
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

VARIANTS: Dict[str, Dict[str, str]] = {
    "baseline": {"ecpf_swap_policy": "strict", "ecpf_fade_policy": "ecpf"},
    "hoeffding": {"ecpf_swap_policy": "hoeffding", "ecpf_fade_policy": "ecpf"},
    "reuse_value": {"ecpf_swap_policy": "strict", "ecpf_fade_policy": "reuse_value"},
    "both": {"ecpf_swap_policy": "hoeffding", "ecpf_fade_policy": "reuse_value"},
}

# setting -> (signal mode, max pool size, extra config)
SETTINGS: Dict[str, Tuple[str, int, Dict[str, Any]]] = {
    # True drift points, paper protocol: isolates the pool mechanics.
    "oracle": ("oracle_60", 10, {}),
    # Same, but a tight pool forces eviction decisions every drift.
    "oracle_pool3": ("oracle_60", 3, {}),
    # Real detector with the repo-default delta: false alarms fill the pool
    # with near-duplicate experts, which is where fade/swap rules matter most.
    "detector": ("dual_adwin", 10, {"detector_delta": 0.05}),
    # Detector with a tight pool; the only pool-pressure setting that works on
    # real streams, which have no ground-truth drift times for oracle mode.
    "detector_pool3": ("dual_adwin", 3, {"detector_delta": 0.05}),
}

DATA_DIRS = [
    "data/old dataset/recurring_drift",
    "data/dataset_0921/synthetic_dataset/binary/recurring",
    "data/dataset_0921/synthetic_dataset/multi_classification/recurring",
]

RECOVERY_WINDOW = 1000


def _stub_type_ldd() -> None:
    from src.config import DriftType

    stub = types.ModuleType("src.drift_type_classifier_type_ldd")
    stub.classify_drift_type = lambda errors, idx, **kw: DriftType.SUDDEN
    sys.modules["src.drift_type_classifier_type_ldd"] = stub


def _list_streams(data_dirs: List[str], limit: Optional[int]) -> List[Path]:
    out: List[Path] = []
    for d in data_dirs:
        files = sorted(p for p in (REPO / d).glob("*.csv"))
        out.extend(files[:limit] if limit else files)
    return out


def run_one(csv: str, setting: str, variant: str, warm_start: int, max_steps: int) -> Dict[str, Any]:
    warnings.filterwarnings("ignore")
    _stub_type_ldd()
    from src.config import PipelineConfig
    from src.ecpf import load_drift_intervals_file
    from src.pipeline import ConceptDriftPipeline, load_recurring_stream_pair

    gt_path = Path(csv).with_name(Path(csv).stem + "_drift_times.txt")
    if gt_path.exists():
        X, y, drift_times = load_recurring_stream_pair(csv)
        intervals = load_drift_intervals_file(str(gt_path))
    else:  # real streams: no ground truth, so only detector settings apply
        df = pd.read_csv(csv)
        y = df["y"].to_numpy(dtype=float)
        X = df.drop(columns=["y"]).to_numpy(dtype=np.float64)
        drift_times, intervals = [], []
        if SETTINGS[setting][0] == "oracle_60":
            raise ValueError(f"{Path(csv).name} has no drift_times; oracle settings need ground truth")
    if max_steps:
        X, y = X[:max_steps], y[:max_steps]
        drift_times = [t for t in drift_times if t < max_steps]
        intervals = [iv for iv in intervals if iv[0] < max_steps]

    signal_mode, pool, extra = SETTINGS[setting]
    cfg = PipelineConfig()
    cfg.use_ecpf = True
    cfg.model_type = "ht"
    cfg.ecpf_signal_mode = signal_mode
    cfg.ecpf_oracle_true_drift_times = drift_times
    cfg.ecpf_warning_length = 60
    cfg.ecpf_max_pool_size = pool
    for k, v in {**extra, **VARIANTS[variant]}.items():
        setattr(cfg, k, v)

    t0 = time.time()
    pipe = ConceptDriftPipeline(cfg)
    correct = np.zeros(len(y), dtype=bool)
    n_events = 0
    for i, yt, yp, dets, _ in pipe.run_stream(X, y, warm_start_samples=warm_start):
        correct[i] = int(round(yp)) == int(round(yt))
        n_events += len(dets)

    ec = pipe._ecpf
    rec = [correct[s : min(s + RECOVERY_WINDOW, len(y))].mean() for s, _ in intervals if s >= warm_start]
    rv = [r["reuse_value"] for r in ec.reuse_value_log]
    return {
        "setting": setting,
        "variant": variant,
        "file": Path(csv).name,
        "dataset": Path(csv).parent.parent.name if "dataset_0921" in csv else "old_recurring",
        "no_change_acc": float(np.mean(y[warm_start + 1:] == y[warm_start:-1])),
        "samples": len(y),
        "gt_drifts": len(intervals),
        "ecpf_drifts": ec.num_drifts,
        "accuracy": float(correct[warm_start:].mean()),
        "recovery_acc": float(np.mean(rec)) if rec else np.nan,
        "leader_swaps": ec.leader_swaps,
        "merges": ec.model_merges,
        "pool_alive": sum(1 for s in ec.slots if s is not None),
        "reuse_value_mean": float(np.mean(rv)) if rv else np.nan,
        "reuse_value_neg_frac": float(np.mean([v < 0 for v in rv])) if rv else np.nan,
        "seconds": round(time.time() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", nargs="+", default=list(SETTINGS))
    ap.add_argument("--variants", nargs="+", default=list(VARIANTS))
    ap.add_argument("--warm-start", type=int, default=200)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--data-dirs", nargs="+", default=DATA_DIRS)
    ap.add_argument("--limit-files", type=int, default=0, help="per data dir")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out-dir", default="outputs/ecpf_swap_fade")
    args = ap.parse_args()

    streams = _list_streams(args.data_dirs, args.limit_files or None)
    jobs = [(str(f), s, v) for s in args.settings for f in streams for v in args.variants]
    print(f"{len(jobs)} runs ({len(streams)} streams x {len(args.settings)} settings x {len(args.variants)} variants)")

    out_dir = REPO / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_one, f, s, v, args.warm_start, args.max_steps): (f, s, v) for f, s, v in jobs}
        for n, fut in enumerate(as_completed(futs), 1):
            f, s, v = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:  # keep the batch going; report at the end
                r = {"setting": s, "variant": v, "file": Path(f).name, "error": repr(exc)}
            rows.append(r)
            print(f"[{n}/{len(jobs)}] {s:13s} {v:11s} {Path(f).name:45s} "
                  f"acc={r.get('accuracy', float('nan')):.4f} swaps={r.get('leader_swaps', '-')} "
                  f"{r.get('error', '')}", flush=True)
            pd.DataFrame(rows).to_csv(out_dir / "runs.csv", index=False)

    df = pd.DataFrame(rows)
    if "error" in df:
        print(df[df["error"].notna()][["setting", "variant", "file", "error"]])
        df = df[df["error"].isna()]
    summary = (
        df.groupby(["setting", "variant"])
        .agg(files=("file", "count"), accuracy=("accuracy", "mean"), recovery_acc=("recovery_acc", "mean"),
             leader_swaps=("leader_swaps", "mean"), ecpf_drifts=("ecpf_drifts", "mean"),
             pool_alive=("pool_alive", "mean"), merges=("merges", "mean"),
             reuse_value_mean=("reuse_value_mean", "mean"))
        .reset_index()
    )
    summary.to_csv(out_dir / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
