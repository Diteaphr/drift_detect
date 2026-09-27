"""Mechanism probes behind the regression FP diagnosis (docs/ECPF_迴歸側逐漂移FP診斷.md §4.4-4.6).

Each probe is a few lines that isolate ONE candidate cause, so a claim in the
report has a directly runnable measurement behind it:

  normalizer   never-reset Welford normalizer on a stationary tail after a residual
               burst -> does ADWIN fire on the slow relaxation? (fixed scale = control)
  bare_htr     River HoeffdingTreeRegressor alone on a stationary stream -> the
               learning-curve orphan rate with no drift and no ECPF
  tree_growth  reg_sudden + htr through the pipeline, logging the leader's node
               count around the 16 000-17 000 reuse cascade
  buffer_len   multi-class hf10: how often the warning buffer the reuse decision is
               made on is a single instance (is the problem regression-specific?)
  chance       per-concept shuffled replay of the saved normalized-error signals:
               ADWIN fires with ordering destroyed vs kept, across delta

Usage
-----
    python scripts/probe_regression_fp_mechanisms.py normalizer
    python scripts/probe_regression_fp_mechanisms.py chance --dir outputs/regression_fp_diagnosis/sudden_block
    python scripts/probe_regression_fp_mechanisms.py all
"""

from __future__ import annotations

import argparse
import glob
import gzip
import os
import sys
import warnings

import numpy as np
import pandas as pd
from river import drift, tree

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_regression_fp import replay, stream_path  # noqa: E402
from generate_task_streams import _score  # noqa: E402
from run_task_matrix import WARM_START, load_stream  # noqa: E402
from src.config import PipelineConfig  # noqa: E402
from src.pipeline import ConceptDriftPipeline  # noqa: E402
from src.task import ErrorNormalizer  # noqa: E402


def probe_normalizer(seeds: int = 5, burst_scale: float = 4.0, burst_len: int = 1500, tail: int = 20000) -> None:
    print("== normalizer: |N(0,1)| x5000, burst |N(0,%.0f)| x%d, then a STATIONARY tail of %d ==" % (burst_scale, burst_len, tail))
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        raw = np.concatenate([np.abs(rng.normal(0, 1, 5000)), np.abs(rng.normal(0, burst_scale, burst_len)),
                              np.abs(rng.normal(0, 1, tail))])
        norm = ErrorNormalizer()
        z = np.array([norm.update(v) for v in raw])
        c0 = 5000 + burst_len
        q = tail // 4
        levels = [round(float(z[c0 + k * q:c0 + (k + 1) * q].mean()), 4) for k in range(4)]
        print("seed %d  normalized level per quarter of the tail: %s | ADWIN fires: normalized %d, fixed scale %d"
              % (seed, levels, len(replay(z[c0:])), len(replay(raw[c0:] / 6.0))))


def probe_bare_htr(seeds: int = 3, n: int = 20000) -> None:
    print("== bare HoeffdingTreeRegressor(grace 200) on a stationary concept-0 stream, no drift ==")
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        X = rng.uniform(0, 10, size=(n, 3))
        y = _score(X, 0) + rng.normal(0, 0.5, n)
        m = tree.HoeffdingTreeRegressor(grace_period=200)
        raw = np.empty(n)
        for i in range(n):
            xi = {"x%d" % j: float(v) for j, v in enumerate(X[i])}
            raw[i] = abs(y[i] - m.predict_one(xi))
            m.learn_one(xi, y[i])
        r = raw[200:]
        roll = np.convolve(r, np.ones(200) / 200, mode="valid")
        fires = replay(np.clip(r / (r.mean() + 3 * r.std()), 0, 1))
        print("seed %d  rolling MAE every 2k: %s | ADWIN(fixed scale) fires: %d at %s"
              % (seed, [round(float(roll[k]), 2) for k in range(0, len(roll), 2000)], len(fires), [f + 200 for f in fires]))


def probe_tree_growth(csv_path: str = "data/synthetic_regression/reg_sudden_20k.csv", lo: int = 14800, hi: int = 18000) -> None:
    print("== reg_sudden + htr: leader tree size around the reuse cascade (%d..%d) ==" % (lo, hi))
    X, y, _ = load_stream(csv_path, hi)
    cfg = PipelineConfig(model_type="htr", use_ecpf=True, ecpf_signal_mode="dual_adwin",
                         ecpf_warning_signal="error", ecpf_drift_signal="error", ecpf_detector_min_instances=30)
    pipe = ConceptDriftPipeline(cfg)
    riv = lambda w: getattr(w.get_model(), "model", w.get_model())  # noqa: E731
    rows, prev = [], 0
    for i, yt, yp, dets, _ in pipe.run_stream(X, y, warm_start_samples=WARM_START):
        e = pipe._ecpf
        if i >= lo:
            s = riv(pipe.prediction_model).summary
            rows.append(dict(t=i, raw=abs(yt - yp), n_nodes=s.get("n_nodes"), cur_idx=e.current_idx,
                             swap=int(e.leader_swaps > prev), det=len(dets)))
        prev = e.leader_swaps
    df = pd.DataFrame(rows)
    df["raw200"] = df["raw"].rolling(200).mean().round(2)
    print(df.iloc[::100][["t", "raw200", "n_nodes", "cur_idx"]].to_string(index=False))
    print("swaps:", df.loc[df.swap == 1, "t"].tolist(), " confirmations:", df.loc[df.det > 0, "t"].tolist())


def probe_buffer_len() -> None:
    print("== multi-class hf10: warning-buffer length at each confirmation ==")
    for path in ("data/synthetic_multiclass/mc3_sudden_20k.csv", "data/synthetic_multiclass/mc5_recurring_20k.csv"):
        X, y, _ = load_stream(path, 20000)
        cfg = PipelineConfig(model_type="hf", model_kwargs={"n_trees": 10}, use_ecpf=True, ecpf_signal_mode="dual_adwin",
                             ecpf_warning_signal="error", ecpf_drift_signal="error", ecpf_detector_min_instances=30,
                             trace_enabled=True)
        pipe = ConceptDriftPipeline(cfg)
        for _ in pipe.run_stream(X, y, warm_start_samples=WARM_START):
            pass
        bl = [e["stage3"].get("buffer_len") for e in pipe.tracer._events]
        print("%s: buffer_len=%s  frac==1: %.2f" % (os.path.basename(path), bl, np.mean([b == 1 for b in bl]) if bl else float("nan")))


def probe_chance(sig_dir: str, deltas=(0.05, 0.02, 0.002), ramp: int = 1500) -> None:
    print("== per-concept replay of saved normalized error: ordered vs shuffled (3x), fresh ADWIN per stretch ==")
    res = []
    for fn in sorted(glob.glob(os.path.join(sig_dir, "signals", "*.csv.gz"))):
        key, cfg = os.path.basename(fn)[:-7].rsplit("__", 1)
        # keys written by diagnose_regression_fp.py: '<kind>_<tier>_<base>' for Joe, '<base>' for synthetic
        parts = key.split("_")
        ds = key + ".csv" if key.startswith("reg_") else "%s/%s/%s.csv" % (parts[0], parts[1], "_".join(parts[2:]))
        with gzip.open(fn, "rt") as f:
            sig = pd.read_csv(f)
        _, _, iv = load_stream(stream_path(ds), 0)
        edges = [0] + [s for s, _ in iv] + [int(sig["t"].max()) + 1]
        t, err = sig["t"].values, sig["err"].values
        rng = np.random.default_rng(0)
        for a, b in zip(edges[:-1], edges[1:]):
            m = (t >= a + ramp) & (t < b)
            if m.sum() < 3000:
                continue
            e = err[m]
            for d in deltas:
                res.append(dict(group="joe" if "/" in ds else "synthetic", config=cfg.replace("_", "/"), delta=d,
                                steps=int(m.sum()), ordered=len(replay(e, delta=d)),
                                shuffled=np.mean([len(replay(rng.permutation(e), delta=d)) for _ in range(3)])))
    g = pd.DataFrame(res).groupby(["group", "config", "delta"]).agg(
        stretches=("steps", "size"), steps=("steps", "sum"), ordered=("ordered", "sum"), shuffled=("shuffled", "sum")).reset_index()
    pd.set_option("display.width", 200)
    print(g.round(2).to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("probe", choices=["normalizer", "bare_htr", "tree_growth", "buffer_len", "chance", "all"])
    ap.add_argument("--dir", default="outputs/regression_fp_diagnosis/sudden_block", help="for 'chance': diagnosis output dir")
    args = ap.parse_args()
    todo = ["normalizer", "bare_htr", "tree_growth", "buffer_len", "chance"] if args.probe == "all" else [args.probe]
    for p in todo:
        {"normalizer": probe_normalizer, "bare_htr": probe_bare_htr, "tree_growth": probe_tree_growth,
         "buffer_len": probe_buffer_len, "chance": lambda: probe_chance(args.dir)}[p]()
        print()


if __name__ == "__main__":
    main()
