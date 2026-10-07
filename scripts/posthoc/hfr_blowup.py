"""Diagnosis only (no src change): plain prequential hfr / htr on metro, outside the ECPF pipeline.
Where does a member tree explode, on which rows, and what would clipping each member to the target range seen so
far do to the MAE?"""
import os
import sys

import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
sys.path.insert(0, REPO)
from src.model_adapter import _MODEL_REGISTRY  # noqa: E402

df = pd.read_csv("data/dataset_0921/real_dataset/regression/metro_interstate_traffic/metro_interstate_traffic.csv")
X, y = df.drop(columns="y").to_numpy(float), df["y"].to_numpy(float)
cls, kw = _MODEL_REGISTRY["hfr"]
m = cls(**kw)
lo, hi = np.inf, -np.inf
err, err_clip, events = [], [], []
for i in range(len(y)):
    per = m.predict_per_model(X[i])
    p = float(np.mean(per))
    err.append(abs(y[i] - p))
    if np.isfinite(lo):
        pc = float(np.mean(np.clip(per, lo, hi)))
        err_clip.append(abs(y[i] - pc))
    else:
        err_clip.append(abs(y[i] - p))
    if max(abs(v) for v in per) > 1e4:
        events.append((i, [float("%.3g" % v) for v in per], X[i].tolist(), y[i]))
    m.learn_one(X[i], y[i])
    lo, hi = min(lo, y[i]), max(hi, y[i])
err, err_clip = np.array(err), np.array(err_clip)
print("plain prequential hfr on metro: %d steps" % len(y))
print("MAE as is %.4g | median %.1f | max %.3g | steps with a member beyond 1e4: %d" % (
    err.mean(), np.median(err), err.max(), len(events)))
print("MAE with each member clipped to the target range seen so far: %.1f | max %.1f" % (err_clip.mean(), err_clip.max()))
print("steps changed by the clip: %d of %d" % (int((np.abs(err - err_clip) > 1e-9).sum()), len(y)))
print("\nfirst exploding steps (row, member predictions, features, y):")
for e in events[:12]:
    print(e)
print("\nfeature columns: mean / std / max")
for j, c in enumerate(df.columns[:-1]):
    print("  %s mean %.2f std %.2f max %.1f" % (c, X[:, j].mean(), X[:, j].std(), X[:, j].max()))
rows = [e[0] for e in events]
ex = X[rows]
print("\nat exploding rows: how many features lie beyond 3 sd of their column -> %s" % (
    [int((np.abs((ex[k] - X.mean(0)) / (X.std(0) + 1e-12)) > 3).sum()) for k in range(min(len(rows), 20))]))
