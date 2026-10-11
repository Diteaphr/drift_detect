"""
Does reuse-value eviction keep the ECPF model pool small without a size cap?

Runs the real streams under five pool-management configs and records, per
drift, the pool size and the serialized size of the stored experts, plus the
time spent in ECPF drift handling:

* ecpf_cap10    : paper fade + cap 10 (the repo default, reference)
* reuse_cap10   : reuse-value fade + cap 10
* ecpf_nocap    : paper fade, no cap
* reuse_nocap   : reuse-value fade, no cap
* nofade_nocap  : no fade, no cap (upper bound on pool growth; merges still apply)

Type-LDD is annotation-only on the ECPF path and is stubbed (no torch needed).

Usage:
    python3 scripts/experiment_ecpf_pool_unbounded.py --workers 8
    python3 scripts/experiment_ecpf_pool_unbounded.py --model-type hf --out-dir outputs/ecpf_pool_unbounded_hf
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
import types
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

NO_CAP = 10**9

# config -> (fade policy, fade enabled, max pool size)
CONFIGS: Dict[str, tuple] = {
    "ecpf_cap10": ("ecpf", True, 10),
    "reuse_cap10": ("reuse_value", True, 10),
    "ecpf_nocap": ("ecpf", True, NO_CAP),
    "reuse_nocap": ("reuse_value", True, NO_CAP),
    "nofade_nocap": ("ecpf", False, NO_CAP),
}

REAL = "data/dataset_0921/real_dataset"
STREAMS = [
    f"{REAL}/binary/electricity/electricity.csv",
    f"{REAL}/binary/airlines/airlines.csv",
    f"{REAL}/multi_classification/covertype/covertype.csv",
    f"{REAL}/multi_classification/gas_sensor_drift/gas_sensor_drift.csv",
]


def run_one_big_stack(*args: Any) -> Dict[str, Any]:
    """Run ``run_one`` in a thread with a large C stack.

    Copying and pickling deep River trees recurses once per tree level; the
    raised recursion limit (see src/ecpf.py ``_deep_clone``) needs a stack big
    enough not to overflow before Python's limit is reached.
    """
    import threading

    result: Dict[str, Any] = {}
    error: List[BaseException] = []

    def target() -> None:
        try:
            result.update(run_one(*args))
        except BaseException as exc:  # re-raised in the calling thread
            error.append(exc)

    old_stack = threading.stack_size(512 * 1024 * 1024)
    try:
        t = threading.Thread(target=target)
        t.start()
        t.join()
    finally:
        threading.stack_size(old_stack)
    if error:
        raise error[0]
    return result


def _stub_type_ldd() -> None:
    from src.config import DriftType

    stub = types.ModuleType("src.drift_type_classifier_type_ldd")
    stub.classify_drift_type = lambda errors, idx, **kw: DriftType.SUDDEN
    sys.modules["src.drift_type_classifier_type_ldd"] = stub


def run_one(csv: str, config: str, warm_start: int, model_type: str = "ht",
            n_trees: int = 0) -> Dict[str, Any]:
    warnings.filterwarnings("ignore")
    sys.setrecursionlimit(20_000)  # pickling deep forests for the size measurement
    _stub_type_ldd()
    import src.ecpf as E
    from src.config import PipelineConfig
    from src.pipeline import ConceptDriftPipeline

    df = pd.read_csv(REPO / csv)
    y = df["y"].to_numpy(dtype=float)
    X = df.drop(columns=["y"]).to_numpy(dtype=np.float64)

    fade_policy, fade_enabled, cap = CONFIGS[config]
    cfg = PipelineConfig()
    cfg.use_ecpf = True
    cfg.model_type = model_type
    if n_trees:
        cfg.model_kwargs = {"n_trees": n_trees}
    cfg.ecpf_signal_mode = "dual_adwin"
    cfg.detector_delta = 0.05
    cfg.ecpf_fade_policy = fade_policy
    cfg.ecpf_fade_enabled = fade_enabled
    cfg.ecpf_max_pool_size = cap

    # Instrument on_drift: time it, then record pool size and stored bytes.
    # Archived slots are frozen, so each object's pickle size is cached.
    size_cache: Dict[int, tuple] = {}
    pool_sizes: List[int] = []
    pool_mb: List[float] = []
    drift_secs: List[float] = []

    def nbytes(obj: Any) -> int:
        hit = size_cache.get(id(obj))
        if hit is not None and hit[0] is obj:
            return hit[1]
        n = len(pickle.dumps(obj))
        size_cache[id(obj)] = (obj, n)
        return n

    orig = E.ECPFMetaLearner.on_drift

    def timed_on_drift(self, prediction_model, buffer):
        t0 = time.perf_counter()
        out = orig(self, prediction_model, buffer)
        drift_secs.append(time.perf_counter() - t0)
        alive = [s for s in self.slots if s is not None]
        pool_sizes.append(len(alive))
        pool_mb.append(sum(nbytes(s) for s in alive) / 1e6)
        return out

    E.ECPFMetaLearner.on_drift = timed_on_drift

    t0 = time.perf_counter()
    pipe = ConceptDriftPipeline(cfg)
    correct = np.zeros(len(y), dtype=bool)
    for i, yt, yp, _, _ in pipe.run_stream(X, y, warm_start_samples=warm_start):
        correct[i] = int(round(yp)) == int(round(yt))
    total = time.perf_counter() - t0

    ec = pipe._ecpf
    rv = [r["reuse_value"] for r in ec.reuse_value_log]
    created = len(ec.slots)
    alive = sum(1 for s in ec.slots if s is not None)
    return {
        "config": config,
        "model_type": model_type,
        "file": Path(csv).name,
        "samples": len(y),
        "accuracy": float(correct[warm_start:].mean()),
        "ecpf_drifts": ec.num_drifts,
        "slots_created": created,
        "merges": ec.model_merges,
        "evicted": created - alive - ec.model_merges,
        "pool_final": alive,
        "pool_mean": float(np.mean(pool_sizes)) if pool_sizes else 1.0,
        "pool_max": int(max(pool_sizes)) if pool_sizes else 1,
        "mb_mean": float(np.mean(pool_mb)) if pool_mb else 0.0,
        "mb_max": float(max(pool_mb)) if pool_mb else 0.0,
        "kb_per_model": float(1000 * np.sum(pool_mb) / np.sum(pool_sizes)) if pool_sizes else 0.0,
        "total_s": total,
        "drift_s": float(np.sum(drift_secs)),
        "drift_share": float(np.sum(drift_secs) / total),
        "ms_per_drift": float(1000 * np.mean(drift_secs)) if drift_secs else 0.0,
        "reuse_value_neg_frac": float(np.mean([v < 0 for v in rv])) if rv else np.nan,
        "pool_trace": pool_sizes,
        "mb_trace": [round(v, 4) for v in pool_mb],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", nargs="+", default=list(CONFIGS))
    ap.add_argument("--streams", nargs="+", default=STREAMS)
    ap.add_argument("--warm-start", type=int, default=200)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model-type", default="ht", help="ht (Hoeffding Tree) or hf (Hoeffding Forest)")
    ap.add_argument("--n-trees", type=int, default=0, help="hf only; 0 keeps the adapter default (5)")
    ap.add_argument("--out-dir", default="outputs/ecpf_pool_unbounded")
    args = ap.parse_args()

    jobs = [(s, c) for s in args.streams for c in args.configs]
    print(f"{len(jobs)} runs ({len(args.streams)} streams x {len(args.configs)} configs)", flush=True)
    out_dir = REPO / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_one_big_stack, s, c, args.warm_start, args.model_type, args.n_trees): (s, c) for s, c in jobs}
        for n, fut in enumerate(as_completed(futs), 1):
            s, c = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:  # keep the batch going; report at the end
                r = {"config": c, "file": Path(s).name, "error": repr(exc)}
            rows.append(r)
            print(f"[{n}/{len(jobs)}] {c:13s} {Path(s).name:22s} acc={r.get('accuracy', float('nan')):.4f} "
                  f"pool mean/max={r.get('pool_mean', float('nan')):.1f}/{r.get('pool_max', '-')} "
                  f"{r.get('total_s', 0):.0f}s {r.get('error', '')}", flush=True)
            (out_dir / "runs.json").write_text(json.dumps(rows))

    df = pd.DataFrame([{k: v for k, v in r.items() if not k.endswith("_trace")} for r in rows])
    df.to_csv(out_dir / "runs.csv", index=False)
    print(df.drop(columns=[c for c in ["error"] if c in df]).to_string(index=False))


if __name__ == "__main__":
    main()
