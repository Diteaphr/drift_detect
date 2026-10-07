"""Read-only probe: at each GT drift, how visible is the change to
(a) any input-only detector (domain-classifier AUC, pre vs post window),
(b) an AE's reconstruction error, and
(c) a frozen model's loss (the frozen-reference signal)?
Per-sample AUC / effect size d = (mean_post - mean_pre) / sd_pre.
Null = two adjacent same-concept windows before the drift.
"""
import glob, json, os
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "synthetic_dataset_joe")
FAMS = {
    "rbf_sudden": ("multi classification/sudden_drift/medium", "recurring_sudden_rbf4_100k_g0[0-2].csv", "clf"),
    "rbf_gradual": ("multi classification/gradual_drift/medium", "recurring_gradual_rbf4_100k_g0[0-1].csv", "clf"),
    "friedman_sudden": ("regression/sudden_drift/medium", "recurring_sudden_friedman_100k_g0[0-1].csv", "reg"),
}
W = 1000


def auc(a, b):
    return roc_auc_score(np.r_[np.zeros(len(a)), np.ones(len(b))], np.r_[a, b])


def dom_auc(A, B, model):
    X = np.vstack([A, B]); y = np.r_[np.zeros(len(A)), np.ones(len(B))]
    p = cross_val_predict(model, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0),
                          method="predict_proba")[:, 1]
    return roc_auc_score(y, p)


def one_point(X, y, s, e, task):
    T, N1, N2, P = slice(s - 4 * W, s - 2 * W), slice(s - 2 * W, s - W), slice(s - W, s), slice(e, e + W)
    r = {}
    for tag, (a, b) in {"null": (N1, N2), "drift": (N2, P)}.items():
        r[f"dom_hgb_{tag}"] = dom_auc(X[a], X[b], HistGradientBoostingClassifier(max_iter=100))
        r[f"dom_lin_{tag}"] = dom_auc(X[a], X[b], LogisticRegression(max_iter=1000))
    # AE trained on an earlier same-concept window, scored out of sample
    sc = StandardScaler().fit(X[T])
    Zt = sc.transform(X[T])
    ae = MLPRegressor(hidden_layer_sizes=(32, 4, 32), max_iter=400, random_state=0).fit(Zt, Zt)
    rec = lambda Z: ((ae.predict(sc.transform(Z)) - sc.transform(Z)) ** 2).mean(1)
    # frozen model trained with labels on the same window (frozen-reference signal)
    if task == "clf":
        m = HistGradientBoostingClassifier(max_iter=200).fit(X[T], y[T])
        loss = lambda sl: (m.predict(X[sl]) != y[sl]).astype(float)
    else:
        m = HistGradientBoostingRegressor(max_iter=200).fit(X[T], y[T])
        loss = lambda sl: np.abs(m.predict(X[sl]) - y[sl])
    for name, f in {"ae": lambda sl: rec(X[sl]), "ref": loss}.items():
        n1, n2, p = f(N1), f(N2), f(P)
        r[f"{name}_auc_null"], r[f"{name}_auc_drift"] = auc(n1, n2), auc(n2, p)
        sd = n2.std() + 1e-12
        r[f"{name}_d_null"], r[f"{name}_d_drift"] = (n2.mean() - n1.mean()) / sd, (p.mean() - n2.mean()) / sd
    return r


rows = []
for fam, (sub, pat, task) in FAMS.items():
    for csv in sorted(glob.glob(os.path.join(BASE, sub, pat))):
        df = pd.read_csv(csv)
        X, y = df.drop(columns="y").to_numpy(float), df["y"].to_numpy()
        iv = json.load(open(csv[:-4] + "_drift_times.txt"))
        iv = [(v, v) if isinstance(v, int) else tuple(v) for v in iv]
        pts = []
        for i, (s, e) in enumerate(iv):
            prev_end = iv[i - 1][1] if i else 0
            next_start = iv[i + 1][0] if i + 1 < len(iv) else len(X)
            if s - 4 * W >= prev_end and e + W <= next_start:
                pts.append((s, e))
        res = Parallel(n_jobs=6)(delayed(one_point)(X, y, s, e, task) for s, e in pts)
        for (s, e), r in zip(pts, res):
            rows.append({"family": fam, "file": os.path.basename(csv), "s": s, "e": e, **r})
        print(fam, os.path.basename(csv), f"{len(pts)}/{len(iv)} drift points usable", flush=True)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(os.path.dirname(__file__), "probe_input_signal.csv"), index=False)
cols = [c for c in out.columns if c.startswith(("dom_", "ae_", "ref_"))]
pd.set_option("display.width", 250)
print(out.groupby("family")[cols].median().T.round(3))
print(out.groupby("family").size())
