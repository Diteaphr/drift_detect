"""Generate a 10x-length stand-in for ``data/sudden_drift/sudden_sea100k_g00.csv``.

The shipped demo files are 100k rows, which the dashboard finishes in seconds.
This produces a 1,000,000-row stream with the same generating process so a run
can be watched for a while and accumulate dozens of drifts.

The process was reverse-engineered from g00 itself (the same way
``data/recurring_drift/README.md`` documents its own files), and reproduced
here rather than guessed:

* features ``x0, x1, x2`` ~ Uniform(0, 10); ``x2`` is irrelevant to the label
* label ``y = 1 if x0 + x1 > theta else 0`` -- river's SEA rule
* ``theta`` alternates between the base 8 and one of {7, 9, 9.5}; outside the
  transition windows the labels match that rule exactly (verified: 1.00000)
* each drift is an 80-sample transition window recorded as ``[start, start+80]``
  in the sibling ``_drift_times.txt``; inside it the concept ramps linearly from
  old to new (g00 matches the new theta ~93-97% there, which is what a ramp --
  or equivalently a 50/50 mix -- over that width produces)
* drift spacing is kept at g00's own scale (~5k-22k apart) rather than stretched
  10x, so any window of the stream looks like the original; the file is longer,
  not slower-moving

Usage:

    python scripts/generate_long_sudden_stream.py
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pandas as pd

OUT_DIR = Path("data/long_drift")
STEM = "sudden_sea1m_g00"

N_SAMPLES = 1_000_000
TRANSITION = 80          # width of each drift's transition window, as in g00
BASE_THETA = 8.0
PARTNER_THETAS = (7.0, 9.0, 9.5)
GAP_LO, GAP_HI = 5_000, 22_000   # observed inter-drift range in g00
SEED = 20260825


def build() -> tuple[pd.DataFrame, list[list[int]]]:
    rng = np.random.default_rng(SEED)

    # --- concept schedule: alternate base <-> partner, like g00 ---
    starts: list[int] = []
    thetas: list[float] = [BASE_THETA]
    t = int(rng.integers(GAP_LO // 2, GAP_HI))
    while t < N_SAMPLES - TRANSITION:
        starts.append(t)
        prev = thetas[-1]
        # Back to base, or away from it to a fresh partner -- never base->base.
        nxt = float(rng.choice(PARTNER_THETAS)) if prev == BASE_THETA else BASE_THETA
        thetas.append(nxt)
        t += int(rng.integers(GAP_LO, GAP_HI))

    # --- features ---
    X = rng.uniform(0.0, 10.0, size=(N_SAMPLES, 3))
    s = X[:, 0] + X[:, 1]

    # --- labels: piecewise theta, with a linear ramp across each window ---
    theta_at = np.full(N_SAMPLES, thetas[0], dtype=np.float64)
    for i, start in enumerate(starts):
        theta_at[start:] = thetas[i + 1]
    y = (s > theta_at).astype(np.int8)

    for i, start in enumerate(starts):
        old, new = thetas[i], thetas[i + 1]
        end = min(start + TRANSITION, N_SAMPLES)
        w = end - start
        # p(new concept) ramps 0 -> 1 across the window; before it wins the
        # sample still comes from the old concept.
        p_new = (np.arange(w) + 1) / w
        take_old = rng.random(w) >= p_new
        seg = s[start:end]
        y[start:end] = np.where(take_old, seg > old, seg > new).astype(np.int8)

    df = pd.DataFrame(
        {"x0": X[:, 0], "x1": X[:, 1], "x2": X[:, 2], "y": y}
    )
    drift_times = [[int(t), int(t + TRANSITION)] for t in starts]
    return df, drift_times


def main() -> None:
    df, drift_times = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / f"{STEM}.csv"
    txt_path = OUT_DIR / f"{STEM}_drift_times.txt"
    df.to_csv(csv_path, index=False)
    txt_path.write_text(str(drift_times))

    print(f"{csv_path}: {len(df):,} rows, {len(drift_times)} drifts")
    print(f"{txt_path}: {drift_times[:3]} ...")
    print(f"label balance: {df['y'].mean():.4f}")


if __name__ == "__main__":
    main()
