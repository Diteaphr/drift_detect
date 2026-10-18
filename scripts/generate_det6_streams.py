#!/usr/bin/env python3
"""Generate DET6's slow-gradual streams (docs/ECPF_DET6_預註冊.md).

Each stream: 100,000 rows of river's RandomRBF (4 classes, 10 features, 50 centroids, as Joe's multiclass
generator), three drifts to a new concept, each a linear transition of `width` steps: inside [d_s, d_e] a row
comes from the new concept with probability (t - d_s) / width, so the drift starts exactly at d_s and ends at
d_e = d_s + width. Every draw is seeded from the cell and trial alone, so the files are reproducible anywhere.

    python scripts/generate_det6_streams.py                 # g00-g39 and g49 of every width
    python scripts/generate_det6_streams.py --out DIR --trials 49 --widths 16000
    python scripts/generate_det6_streams.py --digest        # combined sha256 of the judged files (g00-g39)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import numpy as np
from river.datasets import synth

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / "data/det6_slow_gradual"
N, N_DRIFTS, N_CLASSES, N_FEATURES, N_CENTROIDS = 100_000, 3, 4, 10, 50
WIDTHS = (4000, 8000, 16000)
TRIALS = (*range(40), 49)  # g00-g39 judged, g49 for the determinism gate only
LEAD, GAP, TAIL = 10_000, 10_000, 5_000  # minimum steps before the first drift, between drifts, after the last


def stem(width, g):
    return f"det6_slow_gradual_w{width:05d}_g{g:02d}"


def seed_of(width, g):
    return int(hashlib.sha256(f"DET6|{width}|{g}".encode()).hexdigest()[:8], 16)


def layout(width, rng):
    """Three [d_s, d_e] transitions: the fixed minimum spacing, plus the slack split at random over the 4 gaps."""
    slack = N - LEAD - GAP * (N_DRIFTS - 1) - TAIL - N_DRIFTS * width
    extra = rng.multinomial(slack, [1 / (N_DRIFTS + 1)] * (N_DRIFTS + 1))
    out, t = [], LEAD + int(extra[0])
    for i in range(N_DRIFTS):
        out.append((t, t + width))
        t += width + GAP + int(extra[i + 1])
    assert out[-1][1] + TAIL <= N - 1, out
    return out


def generate(width, g):
    seed = seed_of(width, g)
    rng = np.random.default_rng(seed)
    gt = layout(width, rng)
    seeds = [(int(rng.integers(1, 2**31)), int(rng.integers(1, 2**31))) for _ in range(N_DRIFTS + 1)]
    concepts = [iter(synth.RandomRBF(seed_model=m, seed_sample=s, n_classes=N_CLASSES, n_features=N_FEATURES,
                                     n_centroids=N_CENTROIDS)) for m, s in seeds]
    u = rng.random(N)
    rows, k = [], 0
    for t in range(N):
        while k < N_DRIFTS and t > gt[k][1]:
            k += 1
        new = k < N_DRIFTS and t >= gt[k][0] and u[t] < (t - gt[k][0]) / width
        x, y = next(concepts[k + 1 if new else k])
        rows.append(",".join(f"{x[i]:.6f}" for i in range(N_FEATURES)) + f",{int(y)}")
    meta = {"cell": f"w{width:05d}", "width": width, "g_id": g, "seed": seed, "n_samples": N, "intervals": gt,
            "concept_seeds": seeds, "generator": "scripts/generate_det6_streams.py (RandomRBF, linear transitions)"}
    return rows, gt, meta


def write(out, width, g):
    rows, gt, meta = generate(width, g)
    base = out / stem(width, g)
    header = ",".join(f"x{i}" for i in range(N_FEATURES)) + ",y"
    base.with_suffix(".csv").write_bytes(("\n".join([header, *rows]) + "\n").encode())
    pathlib.Path(f"{base}_drift_times.txt").write_bytes(json.dumps([list(z) for z in gt]).encode())
    base.with_suffix(".json").write_bytes((json.dumps(meta, indent=1) + "\n").encode())


def digest(out):
    """sha256 over 'name sha256' lines of the judged CSVs (g00-g39), sorted by name."""
    lines = []
    for width in WIDTHS:
        for g in range(40):
            p = out / f"{stem(width, g)}.csv"
            lines.append(f"{p.name} {hashlib.sha256(p.read_bytes()).hexdigest()}\n")
    return hashlib.sha256("".join(sorted(lines)).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--widths", type=int, nargs="+", default=list(WIDTHS))
    ap.add_argument("--trials", type=int, nargs="+", default=list(TRIALS))
    ap.add_argument("--digest", action="store_true", help="print the combined sha256 of the judged files and exit")
    args = ap.parse_args()
    if args.digest:
        print(digest(args.out))
        return
    args.out.mkdir(parents=True, exist_ok=True)
    for width in args.widths:
        for g in args.trials:
            write(args.out, width, g)
        print(f"w{width}: {len(args.trials)} streams")


if __name__ == "__main__":
    main()
