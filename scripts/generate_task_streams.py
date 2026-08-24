"""Generate synthetic multi-class and regression drift streams.

The repository ships 40 binary streams and nothing else, so there is no way to
validate multi-class or regression support against known drift points.  This
script emits streams in exactly the format the existing runners expect:

    <name>.csv               columns x0..x{d-1}, y
    <name>_drift_times.txt   [[start, end], ...]  (the format load_drift_intervals_file reads)

Drift is induced by changing which features drive the target, so the *concept*
(the X -> y mapping) changes while the marginal feature distribution does not.
That is real concept drift rather than covariate shift, which is what the ECPF
model pool is meant to handle.

Usage
-----
    python scripts/generate_task_streams.py                 # write the default set
    python scripts/generate_task_streams.py --out-dir data --n 20000
"""

from __future__ import annotations

import argparse
import os
from typing import Callable, List, Tuple

import numpy as np
import pandas as pd

N_FEATURES = 3


# ---------------------------------------------------------------------------
# Concept definitions
# ---------------------------------------------------------------------------
def _score(X: np.ndarray, concept: int) -> np.ndarray:
    """Latent score driving the target; ``concept`` selects which features matter."""
    if concept == 0:
        return 2.0 * X[:, 0] + 1.0 * X[:, 1] - 0.5 * X[:, 2]
    if concept == 1:
        return -1.0 * X[:, 0] + 2.5 * X[:, 2]
    return 1.5 * X[:, 1] - 2.0 * X[:, 2] + 0.5 * X[:, 0]


def _concept_series(n: int, drift_kind: str, n_concepts: int, rng: np.random.Generator):
    """Per-sample concept id plus the (start, end) intervals where it changes.

    sudden      : concept switches at a point
    gradual     : probabilistic mixing over a transition window
    recurring   : concepts cycle and revisit earlier ones
    """
    concepts = np.zeros(n, dtype=int)
    intervals: List[Tuple[int, int]] = []

    if drift_kind == "sudden":
        points = [int(n * f) for f in (0.25, 0.5, 0.75)]
        for i, p in enumerate(points):
            concepts[p:] = (i + 1) % n_concepts
            intervals.append((p, p + 1))

    elif drift_kind == "gradual":
        width = max(200, n // 40)
        points = [int(n * f) for f in (0.3, 0.65)]
        cur = 0
        for i, p in enumerate(points):
            nxt = (i + 1) % n_concepts
            lo, hi = p - width // 2, p + width // 2
            concepts[hi:] = nxt
            ramp = np.linspace(0.0, 1.0, hi - lo)
            flip = rng.random(hi - lo) < ramp
            concepts[lo:hi] = np.where(flip, nxt, cur)
            intervals.append((lo, hi))
            cur = nxt

    elif drift_kind == "recurring":
        seg = n // 6
        order = [0, 1, 2, 0, 1, 2][:6]
        for i, c in enumerate(order):
            concepts[i * seg : (i + 1) * seg] = c % n_concepts
            if i > 0:
                intervals.append((i * seg, i * seg + 1))
        concepts[6 * seg :] = order[-1] % n_concepts

    else:
        raise ValueError("unknown drift_kind %r" % drift_kind)

    return concepts, intervals


# ---------------------------------------------------------------------------
# Stream builders
# ---------------------------------------------------------------------------
def make_multiclass(n: int, k: int, drift_kind: str, seed: int):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0.0, 10.0, size=(n, N_FEATURES))
    concepts, intervals = _concept_series(n, drift_kind, 3, rng)

    s = np.empty(n, dtype=float)
    for c in np.unique(concepts):
        m = concepts == c
        s[m] = _score(X[m], int(c))

    # Per-concept quantile cuts keep the class prior balanced across concepts,
    # so a detector cannot cheat by watching the label marginal alone.
    y = np.empty(n, dtype=int)
    for c in np.unique(concepts):
        m = concepts == c
        cuts = np.quantile(s[m], np.linspace(0.0, 1.0, k + 1)[1:-1])
        y[m] = np.digitize(s[m], cuts)
    return X, y, intervals


def make_regression(n: int, drift_kind: str, seed: int, noise: float = 0.5):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0.0, 10.0, size=(n, N_FEATURES))
    concepts, intervals = _concept_series(n, drift_kind, 3, rng)

    y = np.empty(n, dtype=float)
    for c in np.unique(concepts):
        m = concepts == c
        y[m] = _score(X[m], int(c))
    y = y + rng.normal(0.0, noise, size=n)
    return X, y, intervals


# ---------------------------------------------------------------------------
def write_stream(out_dir: str, name: str, X: np.ndarray, y: np.ndarray,
                 intervals: List[Tuple[int, int]]) -> str:
    os.makedirs(out_dir, exist_ok=True)
    df = pd.DataFrame(X, columns=["x%d" % i for i in range(X.shape[1])])
    df["y"] = y
    csv_path = os.path.join(out_dir, name + ".csv")
    df.to_csv(csv_path, index=False)
    with open(os.path.join(out_dir, name + "_drift_times.txt"), "w", encoding="utf-8") as f:
        f.write(str([[int(a), int(b)] for a, b in intervals]))
    return csv_path


SPECS: List[Tuple[str, str, Callable]] = []
for _kind in ("sudden", "gradual", "recurring"):
    for _k in (3, 5):
        SPECS.append((
            "synthetic_multiclass",
            "mc%d_%s_20k" % (_k, _kind),
            lambda n, s, k=_k, kind=_kind: make_multiclass(n, k, kind, s),
        ))
    SPECS.append((
        "synthetic_regression",
        "reg_%s_20k" % _kind,
        lambda n, s, kind=_kind: make_regression(n, kind, s),
    ))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", default="data", help="root under which the two folders are written")
    ap.add_argument("--n", type=int, default=20000, help="samples per stream")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    print("%-24s %-22s %8s %10s  %s" % ("folder", "name", "rows", "target", "drift intervals"))
    print("-" * 96)
    for i, (folder, name, build) in enumerate(SPECS):
        X, y, intervals = build(args.n, args.seed + i)
        out = os.path.join(args.out_dir, folder)
        write_stream(out, name, X, y, intervals)
        desc = ("K=%d" % len(np.unique(y))) if y.dtype.kind in "iu" else "continuous"
        print("%-24s %-22s %8d %10s  %s" % (folder, name, len(y), desc, intervals))
    print("\nwrote %d streams under %s" % (len(SPECS), args.out_dir))


if __name__ == "__main__":
    main()
