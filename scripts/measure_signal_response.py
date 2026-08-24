"""Measure how each ECPF signal responds to a known drift.

Answers one question that a detection count cannot: after a ground-truth drift,
does the scalar an ADWIN is watching actually go UP? ADWIN fires on an increase,
so a signal that *falls* after drift cannot trigger it however the threshold is
tuned -- and lowering the threshold then only buys false positives.

Windows are taken relative to each ground-truth drift point, with a guard band
around the drift itself, and the shift is reported in units of the pre-drift
standard deviation so signals living on different scales are comparable.

Usage
-----
    python scripts/measure_signal_response.py
    python scripts/measure_signal_response.py --max-steps 20000 --post 3000
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.meta_ecpf.signal_routing import extract_signal as _orig  # noqa: E402
import src.pipeline as P  # noqa: E402
from src.config import PipelineConfig  # noqa: E402
from src.ecpf import load_drift_intervals_file  # noqa: E402
from src.pipeline import ConceptDriftPipeline  # noqa: E402

STREAMS = [
    ("data/synthetic_multiclass/mc3_sudden_20k.csv", "hf"),
    ("data/synthetic_multiclass/mc3_recurring_20k.csv", "hf"),
    ("data/synthetic_multiclass/mc5_sudden_20k.csv", "hf"),
    ("data/synthetic_regression/reg_sudden_20k.csv", "hfr"),
]
SIGNALS_CLS = ["error", "uq_variance", "uq_mi"]
SIGNALS_REG = ["error", "uq_variance"]


def trace(csv_path: str, model_type: str, signal: str, max_steps: int):
    """Run the pipeline and record the signal value at each instance.

    ``extract_signal`` is called twice per instance (once for the warning stream,
    once for the drift stream), so only the first call per timestamp is kept --
    otherwise the recorded series is double-length and every index is off by 2x
    relative to the ground-truth drift points.
    """
    df = pd.read_csv(csv_path).iloc[:max_steps]
    y = df["y"].values
    X = df[[c for c in df.columns if c != "y"]].values.astype(float)

    seen: dict = {}
    cur = {"t": -1}

    def spy(s, **kw):
        v = _orig(s, **kw)
        if s == signal:
            seen.setdefault(cur["t"], v)
        return v

    P.extract_signal = spy
    try:
        cfg = PipelineConfig(
            model_type=model_type, use_ecpf=True, ecpf_signal_mode="dual_adwin",
            ecpf_warning_signal=signal, ecpf_drift_signal=signal,
        )
        pipe = ConceptDriftPipeline(cfg)
        n_events = 0
        for t, _, _, dets, _ in pipe.run_stream(X, y, warm_start_samples=200):
            cur["t"] = t
            n_events += len(dets)
    finally:
        P.extract_signal = _orig

    ts = np.array(sorted(seen))
    return ts, np.array([seen[t] for t in ts]), n_events


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-steps", type=int, default=12000)
    ap.add_argument("--pre", type=int, default=1500, help="samples before each drift")
    ap.add_argument("--post", type=int, default=1000, help="samples after each drift")
    ap.add_argument("--guard", type=int, default=100, help="samples skipped either side of the drift")
    args = ap.parse_args()

    print("%-28s %-6s %-12s %7s %9s %9s %9s %8s" %
          ("stream", "model", "signal", "events", "pre", "post", "shift", "shift/sd"))
    print("-" * 100)

    pooled: dict = {}
    for path, mt in STREAMS:
        if not os.path.exists(path):
            print("  (missing %s -- run scripts/generate_task_streams.py first)" % path)
            continue
        gt = load_drift_intervals_file(os.path.splitext(path)[0] + "_drift_times.txt")
        points = [a for a, _ in gt if a < args.max_steps - args.post]
        for sig in (SIGNALS_REG if mt.endswith("r") else SIGNALS_CLS):
            ts, vs, n_events = trace(path, mt, sig, args.max_steps)
            pres, posts, shifts = [], [], []
            for d in points:
                pre = vs[(ts >= d - args.pre) & (ts < d - args.guard)]
                post = vs[(ts > d + args.guard) & (ts <= d + args.post)]
                if pre.size < 50 or post.size < 50:
                    continue
                pres.append(pre.mean())
                posts.append(post.mean())
                sd = pre.std()
                shifts.append((post.mean() - pre.mean()) / sd if sd > 0 else 0.0)
            if not shifts:
                continue
            print("%-28s %-6s %-12s %7d %9.4f %9.4f %+9.4f %+8.2f" % (
                os.path.basename(path).replace(".csv", "")[:28], mt, sig, n_events,
                np.mean(pres), np.mean(posts), np.mean(posts) - np.mean(pres),
                np.mean(shifts)))
            pooled.setdefault(sig, []).extend(shifts)

    print()
    print("=== mean shift in pre-drift standard deviations, pooled over all drifts ===")
    for sig, xs in pooled.items():
        a = np.array(xs)
        print("  %-12s n_drifts=%2d  mean=%+.3f sd  median=%+.3f sd  fraction rising=%.0f%%"
              % (sig, len(a), a.mean(), np.median(a), 100.0 * (a > 0).mean()))
    print()
    print("ADWIN fires on an INCREASE. A signal whose 'fraction rising' is near or")
    print("below 50%% cannot be fixed by lowering its threshold.")


if __name__ == "__main__":
    main()
