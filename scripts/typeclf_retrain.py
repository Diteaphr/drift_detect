#!/usr/bin/env python3
"""Offline check: does a drift-type classifier retrained on our own errors tell sudden from not?

Exploratory, nothing here touches the pipeline. Samples are cut from finished
``s1route_fw_c300`` runs (S1 framework, single Hoeffding Tree): for every
ground-truth drift, the leader's 0/1 error history since the last confirmed
alarm, taken 100 / 200 / 300 / 400 steps after the drift starts -- the input the
pipeline gives Type-LDD. Label: sudden (synthetic ``sudden`` / ``recurring_sudden``,
injected ``abrupt``) vs not.

Models, all scored with balanced accuracy (mean of the sudden and non-sudden
hit rates) and split by stream so no stream is on both sides:

* ``current``: the shipped 3-way Type-LDD checkpoint, mapped to sudden / not;
* ``fan``: the same FAN encoder, initialised from that checkpoint and retrained as a
  2-way prototypical network on our samples (nearest class centre at test time);
* ``simple``: six hand-made features of the windowed error rate + logistic regression;
* ``adapts``: ADAPTS' sudden rule (Li et al., KBS 2026) on block error rates, untrained.

Splits:

* A (transfer): train on the dev dataset ``synthetic_binary`` (25/50/100% of its
  streams), test on synthetic_multiclass and both injected_paper datasets;
* B (in-domain): pool those three report datasets, train on 10/20/50/80% of the
  streams (stratified by dataset x label), test on the rest.

Each training size is repeated with 3 seeds.

  python3 scripts/typeclf_retrain.py extract   # -> outputs/typeclf/samples.npz
  python3 scripts/typeclf_retrain.py run       # -> outputs/typeclf/results.json
  python3 scripts/typeclf_retrain.py adapts    # adds the untrained ADAPTS rule to results.json
  python3 scripts/typeclf_retrain.py export    # -> outputs/typeclf/simple_route_model.json (routing)
"""

from __future__ import annotations

import argparse
import glob
import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

OUT = REPO / "outputs" / "typeclf"
from src.drift_type_classifier_simple import SimpleTypeClassifier, simple_features, window_accuracy  # noqa: E402
SOURCE_PRESET = "s1route_fw_c300"
DEV = ("synthetic_binary",)
REPORT = ("synthetic_multiclass", "injected_paper_electricity", "injected_paper_gas_sensor_drift")
OFFSETS = (100, 200, 300, 400)
WINDOW, N_WIN = 15, 51          # the shipped checkpoint: 51 windows x 15 instances = 765
SEEDS = (0, 1, 2)
EXPORT_FOLDS, EXPORT_SEED = 5, 0
ROUTE_MODEL = OUT / "simple_route_model.json"
A_FRACTIONS = (0.25, 0.5, 1.0)
B_FRACTIONS = (0.1, 0.2, 0.5, 0.8)


# -- samples -----------------------------------------------------------------------
def stream_kind(dataset: str, stream: str, cell) -> str:
    if dataset.startswith("injected_"):
        return str(cell).split("/")[0]
    parts = stream.split("_")
    return "_".join(parts[:2]) if parts[0] == "recurring" else parts[0]


def relative_gaps(acc: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        g = (acc[1:] - acc[:-1]) / acc[:-1]
    return np.nan_to_num(g, nan=0.0, posinf=0.0, neginf=0.0)


def extract(args) -> None:
    from scripts.analyze_routed import gt_in_output  # maps injected GT to output positions

    rows: List[Dict] = []
    accs: List[np.ndarray] = []
    for dataset in DEV + REPORT:
        runs = sorted(glob.glob(str(REPO / "outputs" / "benchmark_routed" / dataset / SOURCE_PRESET / "*" / "manifest.json")))
        for k, mpath in enumerate(runs):
            run = Path(mpath).parent
            m = json.loads((run / "manifest.json").read_text())
            rec = np.load(run / "preds.npz")
            y_true, y_pred = rec["y_true"], rec["y_pred"]
            valid = np.isfinite(y_pred)
            err = (y_true != y_pred).astype(float)
            alarms = np.sort(np.asarray(rec["alarm_idx"], dtype=int))
            gt = gt_in_output({"dataset": dataset, "stream": m["stream"], "coordinates": m["coordinates"],
                               "gt_intervals": [tuple(g) for g in (m["gt_intervals"] or [])]})
            starts = [s for s, _ in gt]
            kind = stream_kind(dataset, m["stream"], m.get("cell"))
            label = int(kind in ("sudden", "recurring_sudden", "abrupt"))
            for d, s in enumerate(starts):
                nxt = starts[d + 1] if d + 1 < len(starts) else len(y_true)
                for off in OFFSETS:
                    t = s + off
                    if t >= nxt or t >= len(y_true):
                        continue
                    prev = alarms[alarms < t]
                    since = int(prev[-1]) + 1 if len(prev) else 0
                    hist = err[since:t + 1][valid[since:t + 1]]
                    accs.append(window_accuracy(hist))
                    rows.append({"dataset": dataset, "stream": m["stream"], "kind": kind, "label": label,
                                 "drift": d, "offset": off, "history": int(len(hist))})
            if (k + 1) % 100 == 0:
                print(f"{dataset}: {k + 1}/{len(runs)} streams", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / "samples.npz", acc=np.stack(accs))
    (OUT / "samples_meta.json").write_text(json.dumps(rows))
    by = {}
    for r in rows:
        key = f"{r['dataset']}:{'sudden' if r['label'] else 'not'}"
        by.setdefault(key, set()).add(r["stream"])
    print(f"{len(rows)} samples;", {k: len(v) for k, v in sorted(by.items())}, "streams")


# -- models ------------------------------------------------------------------------
class SimpleModel:
    def fit(self, acc, y):
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        self.m = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=1000))
        self.m.fit(simple_features(acc), y)
        return self

    def predict(self, acc):
        return self.m.predict(simple_features(acc))


class AdaptsRule:
    """ADAPTS' sudden-drift rule (Li et al., KBS 2026, Algorithm 3), no training.

    tau = mean + phi * std of the previous window's losses; sudden when at least
    ``share`` of the current window's losses exceed tau. ADAPTS uses per-point VAE
    reconstruction losses; our per-instance loss is a 0/1 error, for which
    mean + 3 std almost always exceeds 1, so the loss here is the error rate of
    each 15-instance block (``1 - acc``). The current window is the last ``w``
    blocks and the previous window the ``w`` blocks before it.
    """

    def __init__(self, w: int = 10, phi: float = 3.0, share: float = 0.5):
        self.w, self.phi, self.share = w, phi, share

    def predict(self, acc):
        e = 1.0 - acc
        cur, prev = e[:, -self.w:], e[:, -2 * self.w:-self.w]
        tau = prev.mean(1, keepdims=True) + self.phi * prev.std(1, keepdims=True)
        return ((cur > tau).mean(1) >= self.share).astype(int)


ADAPTS_GRID = [(w, phi) for w in (3, 5, 10, 15, 20, 25) for phi in (1.0, 2.0, 3.0)]


class CurrentModel:
    """The shipped 3-way checkpoint: sudden vs gradual/incremental."""

    def __init__(self):
        from src.type_ldd.infer import load_classifier
        self.clf = load_classifier()

    def predict(self, acc):
        return np.array([int(self.clf.predict_gaps(relative_gaps(a)).value == "sudden") for a in acc])


class FanModel:
    """FAN encoder from the shipped checkpoint, retrained as a 2-way prototypical net."""

    def __init__(self, seed: int, epochs: int = 60, iterations: int = 100, ns: int = 5, nq: int = 5, lr: float = 0.01):
        self.seed, self.epochs, self.iterations, self.ns, self.nq, self.lr = seed, epochs, iterations, ns, nq, lr

    def fit(self, acc, y):
        import torch
        import torch.nn.functional as F
        from src.type_ldd.model import PrototypicalNet, euclidean_dist
        torch.manual_seed(self.seed)
        rng = np.random.default_rng(self.seed)
        meta = json.loads((REPO / "checkpoints/type_ldd/meta.json").read_text())
        net = PrototypicalNet(meta["data_vector_length"], meta["centroid_vector_length"], meta["model_select"])
        state = torch.load(REPO / "checkpoints/type_ldd/fan_joint_model.pt", map_location="cpu", weights_only=True)
        net.load_state_dict({k[len("prototypical_net."):]: v for k, v in state.items() if k.startswith("prototypical_net.")})
        x = torch.FloatTensor(np.stack([relative_gaps(a) for a in acc]))
        idx = {c: np.flatnonzero(y == c) for c in (0, 1)}
        opt = torch.optim.Adam(net.parameters(), lr=self.lr)
        sched = torch.optim.lr_scheduler.StepLR(opt, step_size=30, gamma=0.9)
        k = self.ns + self.nq
        for _ in range(self.epochs):
            net.train()
            for _ in range(self.iterations):
                pick = {c: rng.choice(idx[c], size=k, replace=len(idx[c]) < k) for c in (0, 1)}
                emb = {c: net(x[pick[c]]) for c in (0, 1)}
                protos = torch.stack([emb[c][: self.ns].mean(0) for c in (0, 1)])
                query = torch.cat([emb[c][self.ns:] for c in (0, 1)])
                target = torch.cat([torch.full((self.nq,), c, dtype=torch.long) for c in (0, 1)])
                loss = F.cross_entropy(-euclidean_dist(query, protos), target)
                opt.zero_grad()
                loss.backward()
                opt.step()
            sched.step()
        net.eval()
        with torch.no_grad():
            emb = net(x)
            self.centroids = torch.stack([emb[torch.as_tensor(y == c)].mean(0) for c in (0, 1)])
        self.net, self.torch = net, torch
        return self

    def predict(self, acc):
        torch = self.torch
        with torch.no_grad():
            emb = self.net(torch.FloatTensor(np.stack([relative_gaps(a) for a in acc])))
            return torch.argmin(torch.cdist(emb, self.centroids), dim=1).numpy()


# -- evaluation --------------------------------------------------------------------
def scores(y: np.ndarray, p: np.ndarray) -> Dict:
    sud = float(np.mean(p[y == 1] == 1)) if (y == 1).any() else None
    non = float(np.mean(p[y == 0] == 0)) if (y == 0).any() else None
    bal = None if sud is None or non is None else (sud + non) / 2
    return {"n": int(len(y)), "n_sudden": int((y == 1).sum()), "sudden": sud, "non_sudden": non, "balanced": bal}


def breakdown(meta: List[Dict], mask: np.ndarray, y: np.ndarray, p: np.ndarray) -> Dict:
    out = {"all": scores(y[mask], p[mask])}
    ds = np.array([r["dataset"] for r in meta])
    off = np.array([r["offset"] for r in meta])
    for d in sorted(set(ds[mask])):
        out[f"dataset:{d}"] = scores(y[mask & (ds == d)], p[mask & (ds == d)])
    for o in OFFSETS:
        out[f"offset:{o}"] = scores(y[mask & (off == o)], p[mask & (off == o)])
    return out


def stream_bootstrap(meta, mask, y, p, draws: int = 1000, seed: int = 20261012) -> List[float]:
    """95% CI of balanced accuracy, resampling test streams."""
    streams = np.array([f"{r['dataset']}|{r['stream']}" for r in meta])
    uniq = np.unique(streams[mask])
    pos = {s: np.flatnonzero(mask & (streams == s)) for s in uniq}
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        rows = np.concatenate([pos[s] for s in rng.choice(uniq, size=len(uniq), replace=True)])
        b = scores(y[rows], p[rows])["balanced"]
        if b is not None:
            vals.append(b)
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def pick_streams(meta, pool: np.ndarray, fraction: float, seed: int) -> set:
    """Stratified (dataset x label) random subset of the streams in ``pool``."""
    strata: Dict[tuple, List[str]] = {}
    for i in np.flatnonzero(pool):
        r = meta[i]
        strata.setdefault((r["dataset"], r["label"]), [])
        key = f"{r['dataset']}|{r['stream']}"
        if key not in strata[(r["dataset"], r["label"])]:
            strata[(r["dataset"], r["label"])].append(key)
    rnd = random.Random(seed)
    chosen = set()
    for keys in strata.values():
        keys = sorted(keys)
        rnd.shuffle(keys)
        chosen.update(keys[: max(1, round(fraction * len(keys)))])
    return chosen


def run(args) -> None:
    acc = np.load(OUT / "samples.npz")["acc"]
    meta = json.loads((OUT / "samples_meta.json").read_text())
    y = np.array([r["label"] for r in meta])
    ds = np.array([r["dataset"] for r in meta])
    key = np.array([f"{r['dataset']}|{r['stream']}" for r in meta])
    dev, report = np.isin(ds, DEV), np.isin(ds, REPORT)
    current = CurrentModel().predict(acc)
    results: Dict = {"offsets": OFFSETS, "seeds": SEEDS, "source_preset": SOURCE_PRESET,
                     "samples": {d: {"samples": int((ds == d).sum()), "streams": int(len(set(key[ds == d]))),
                                     "sudden_streams": int(len(set(key[(ds == d) & (y == 1)])))}
                                 for d in DEV + REPORT},
                     "A": [], "B": []}
    results["current_on_report"] = breakdown(meta, report, y, current)
    results["current_on_report"]["ci"] = stream_bootstrap(meta, report, y, current)
    results["current_on_dev"] = breakdown(meta, dev, y, current)

    for split, fractions, pool, test_fixed in (("A", A_FRACTIONS, dev, report), ("B", B_FRACTIONS, report, None)):
        for frac in fractions:
            for seed in SEEDS:
                t0 = time.time()
                chosen = pick_streams(meta, pool, frac, seed)
                train = pool & np.isin(key, list(chosen))
                test = test_fixed if test_fixed is not None else (pool & ~train)
                entry = {"fraction": frac, "seed": seed, "train_samples": int(train.sum()),
                         "train_streams": len(chosen), "test_samples": int(test.sum())}
                for name, model in (("simple", SimpleModel()), ("fan", FanModel(seed))):
                    pred = model.fit(acc[train], y[train]).predict(acc)
                    entry[name] = breakdown(meta, test, y, pred)
                    if frac == fractions[-1] and seed == SEEDS[0]:
                        entry[name]["ci"] = stream_bootstrap(meta, test, y, pred)
                entry["current"] = breakdown(meta, test, y, current)
                results[split].append(entry)
                print(f"{split} frac={frac} seed={seed} train={entry['train_streams']} streams | "
                      f"current {entry['current']['all']['balanced']:.3f}  simple {entry['simple']['all']['balanced']:.3f}  "
                      f"fan {entry['fan']['all']['balanced']:.3f}  ({time.time() - t0:.0f}s)", flush=True)
    add_adapts(results, acc, meta)
    (OUT / "results.json").write_text(json.dumps(results, indent=2))
    print("->", (OUT / "results.json").relative_to(REPO))


def add_adapts(results: Dict, acc: np.ndarray, meta: List[Dict]) -> None:
    """Score the untrained ADAPTS rule on every test set already in ``results``.

    The headline keeps the paper's phi = 3 and share = 0.5; w = 10 blocks is the
    best phi = 3 window on the dev set (synthetic_binary). The grid is reported too.
    """
    y = np.array([r["label"] for r in meta])
    ds = np.array([r["dataset"] for r in meta])
    key = np.array([f"{r['dataset']}|{r['stream']}" for r in meta])
    dev, report = np.isin(ds, DEV), np.isin(ds, REPORT)
    adapts = AdaptsRule().predict(acc)
    results["adapts_on_report"] = breakdown(meta, report, y, adapts)
    results["adapts_on_report"]["ci"] = stream_bootstrap(meta, report, y, adapts)
    grid = []
    for w, phi in ADAPTS_GRID:
        p = AdaptsRule(w, phi).predict(acc)
        grid.append({"w": w, "phi": phi, "dev": scores(y[dev], p[dev]), "report": scores(y[report], p[report])})
    results["adapts_grid"] = grid
    for split, pool, test_fixed in (("A", dev, report), ("B", report, None)):
        for entry in results[split]:
            train = pool & np.isin(key, list(pick_streams(meta, pool, entry["fraction"], entry["seed"])))
            test = test_fixed if test_fixed is not None else (pool & ~train)
            assert int(test.sum()) == entry["test_samples"]
            entry["adapts"] = breakdown(meta, test, y, adapts)


def adapts_step(args) -> None:
    """Add the ADAPTS rule to an existing results.json without retraining."""
    acc = np.load(OUT / "samples.npz")["acc"]
    meta = json.loads((OUT / "samples_meta.json").read_text())
    results = json.loads((OUT / "results.json").read_text())
    add_adapts(results, acc, meta)
    (OUT / "results.json").write_text(json.dumps(results, indent=2))
    best = max(results["adapts_grid"], key=lambda g: g["dev"]["balanced"])
    print(f"adapts (w=10, phi=3) report balanced {results['adapts_on_report']['all']['balanced']:.3f} "
          f"ci {results['adapts_on_report']['ci']}; best-on-dev w={best['w']} phi={best['phi']} "
          f"report {best['report']['balanced']:.3f}")


def html(args) -> None:
    """Write results.json into outputs/typeclf/typeclf_report.html (placeholder or `const T = ...;`)."""
    import re
    page = OUT / "typeclf_report.html"
    text = page.read_text()
    payload = json.dumps(json.loads((OUT / "results.json").read_text()), ensure_ascii=False, separators=(",", ":"))
    if "__TYPECLF__" in text:
        text = text.replace("__TYPECLF__", payload, 1)
    else:
        text, n = re.subn(r"^const T = .*;$", lambda _: f"const T = {payload};", text, count=1, flags=re.M)
        if n != 1:
            raise SystemExit("no __TYPECLF__ or `const T = ...;` line in the report")
    page.write_text(text)
    print("->", page.relative_to(REPO), f"({len(text) // 1024} KB)")


def export(args) -> None:
    """Fit the simple baseline for routing (split B, cross-fitted by stream).

    The report streams are split into 5 folds stratified by dataset x label; each
    stream is classified by the model fitted on the other 4 folds (80 % of the
    streams, like split B at 0.8), so no run is routed by a model that saw it.
    ``default`` is fitted on all report streams and serves streams without labels
    (INSECTS).
    """
    acc = np.load(OUT / "samples.npz")["acc"]
    meta = json.loads((OUT / "samples_meta.json").read_text())
    y = np.array([r["label"] for r in meta])
    ds = np.array([r["dataset"] for r in meta])
    key = np.array([f"{r['dataset']}|{r['stream']}" for r in meta])
    report = np.isin(ds, REPORT)
    strata: Dict[tuple, List[str]] = {}
    for i in np.flatnonzero(report):
        strata.setdefault((meta[i]["dataset"], meta[i]["label"]), [])
        if key[i] not in strata[(meta[i]["dataset"], meta[i]["label"])]:
            strata[(meta[i]["dataset"], meta[i]["label"])].append(key[i])
    rnd = random.Random(EXPORT_SEED)
    fold_of: Dict[str, str] = {}
    for keys in strata.values():
        keys = sorted(keys)
        rnd.shuffle(keys)
        for j, k in enumerate(keys):
            fold_of[k] = f"fold{j % EXPORT_FOLDS}"

    def params(mask):
        m = SimpleModel().fit(acc[mask], y[mask]).m
        sc, lr = m.named_steps["standardscaler"], m.named_steps["logisticregression"]
        return {"mean": sc.mean_.tolist(), "scale": sc.scale_.tolist(),
                "coef": lr.coef_[0].tolist(), "intercept": float(lr.intercept_[0]), "train_samples": int(mask.sum())}

    folds = np.array([fold_of.get(k, "") for k in key])
    models = {"default": params(report)}
    pred = np.zeros(len(y), dtype=int)
    for f in sorted(set(fold_of.values())):
        models[f] = params(report & (folds != f))
        clf, rows = SimpleTypeClassifier(models[f]), np.flatnonzero(report & (folds == f))
        z = (simple_features(acc[rows]) - clf.mean) / clf.scale @ clf.coef + clf.intercept
        pred[rows] = (z > 0).astype(int)
    cv = breakdown(meta, report, y, pred)
    spec = {"description": "simple baseline (6 features + logistic regression), sudden vs not; "
                           "cross-fitted on split B, see scripts/typeclf_retrain.py export",
            "source_samples": "outputs/typeclf/samples.npz", "folds": EXPORT_FOLDS, "seed": EXPORT_SEED,
            "cv_on_report": cv, "stream_fold": fold_of, "models": models}
    ROUTE_MODEL.write_text(json.dumps(spec, indent=2))
    print(f"-> {ROUTE_MODEL.relative_to(REPO)}; cross-fitted balanced {cv['all']['balanced']:.3f} "
          f"(sudden {cv['all']['sudden']:.3f}, not {cv['all']['non_sudden']:.3f})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["extract", "run", "adapts", "html", "export"])
    args = ap.parse_args()
    {"extract": extract, "run": run, "adapts": adapts_step, "html": html, "export": export}[args.step](args)


if __name__ == "__main__":
    main()
