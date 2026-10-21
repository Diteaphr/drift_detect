"""
Compare benchmark runs against the literature values in configs/datasets_0921.json.

Reads every ``runs.csv`` under ``outputs/benchmark`` (written by
``scripts/run_benchmark.py``), keeps comparable full-length runs, and writes a
markdown report plus CSV tables:

* prequential datasets: mean, std, 95% t-interval and n of every required
  metric per dataset x preset, next to the registry SOTA values (difference =
  ours - literature);
* injected datasets: per dataset x cell x preset, detection metrics pooled over
  trials exactly as Cerqueira et al. report a cell, next to the best detector of
  their table;
* across datasets (or cells): average ranks, Friedman test with Nemenyi
  critical difference, and Wilcoxon signed-rank tests of ``--target`` against
  every other preset (Holm-corrected);
* cost: wall and CPU time, memory increment, RAM-hours and final model size
  per dataset x preset (``cost.csv``), with the machine and the number of runs
  that executed concurrently.

Usage:
    python3 scripts/compare_sota.py
    python3 scripts/compare_sota.py --target e10bft --datasets electricity insects_abrupt_balanced
    python3 scripts/compare_sota.py --include-noncomparable   # exploratory, flagged in the report
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.metrics.evaluate_run import pool_detection_runs  # noqa: E402

REGISTRY_PATH = REPO / "configs" / "datasets_0921.json"
RANK_METRICS = ("acc_prequential", "acc_window1000_mean", "kappa_t")  # higher is better
# Studentized range / sqrt(2) for alpha = 0.05 (Demsar 2006, Table 5a), k = 2..10.
NEMENYI_Q05 = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164}
POOLED_KEYS = ["f1", "precision", "recall", "episode_recall", "mdt", "ndt", "far_cerqueira", "far_per_run"]


def load_runs(root: Path) -> pd.DataFrame:
    frames = [pd.read_csv(p) for p in sorted(root.rglob("runs.csv"))]
    if not frames:
        raise SystemExit(f"no runs.csv under {root}")
    df = pd.concat(frames, ignore_index=True)
    if "error" in df:
        df = df[df["error"].isna()]
    return df.drop_duplicates("run_dir", keep="last")


def ci95(x: np.ndarray) -> Optional[float]:
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return None
    return float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / math.sqrt(len(x)))


def fmt(v: Any, nd: int = 4) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    if isinstance(v, (float, np.floating)):
        return f"{v:.2e}" if 0 < abs(v) < 10 ** -nd else f"{v:.{nd}f}"
    return str(v)


def prequential_table(df: pd.DataFrame, entry: Dict[str, Any], name: str) -> pd.DataFrame:
    rows = []
    for preset, g in df.groupby("preset"):
        for metric in entry.get("required_metrics", []):
            if metric not in g:
                continue
            x = pd.to_numeric(g[metric], errors="coerce").to_numpy(dtype=float)
            if np.isnan(x).all():
                continue
            mean = float(np.nanmean(x))
            refs = [r for r in entry.get("sota", []) if r["metric"] == metric]
            best = max(refs, key=lambda r: r["value"]) if refs else None
            classic = [r for r in refs if r.get("tier") == "classic"]
            cbest = max(classic, key=lambda r: r["value"]) if classic else None
            rows.append({
                "dataset": name, "preset": preset, "metric": metric, "n": int((~np.isnan(x)).sum()),
                "mean": mean, "std": float(np.nanstd(x, ddof=1)) if (~np.isnan(x)).sum() > 1 else None,
                "ci95": ci95(x),
                "sota_value": best["value"] if best else None,
                "sota_method": best["method"] if best else None,
                "sota_source": best["source"] if best else None,
                "diff_vs_sota": mean - best["value"] if best else None,
                "classic_value": cbest["value"] if cbest else None,
                "classic_method": cbest["method"] if cbest else None,
                "diff_vs_classic": mean - cbest["value"] if cbest else None,
            })
    return pd.DataFrame(rows)


def detection_table(df: pd.DataFrame, entry: Dict[str, Any], name: str) -> pd.DataFrame:
    rows = []
    refs = entry.get("sota_by_cell", {})
    cal = entry.get("calibration", {})
    for (preset, cell), g in df.groupby(["preset", "cell"]):
        p = pool_detection_runs(g.to_dict("records"))
        if not p:
            continue
        ref = refs.get(cell, {})
        cref = cal.get("by_cell", {}).get(cell, {}) if cal.get("preset") == preset else {}
        rows.append({"dataset": name, "cell": cell, "preset": preset, "n_runs": p["n_runs"],
                     **{k: p.get(k) for k in POOLED_KEYS},
                     "sota_f1": ref.get("value"), "sota_method": ref.get("method"), "sota_mdt": ref.get("mdt"),
                     "diff_f1_vs_sota": p["f1"] - ref["value"] if ref else None,
                     "calib_f1": cref.get("f1"), "calib_episode_recall": cref.get("episode_recall"),
                     "calib_mdt": cref.get("mdt"), "calib_far": cref.get("far")})
    return pd.DataFrame(rows)


def cost_table(df: pd.DataFrame) -> pd.DataFrame:
    """Time and memory per dataset x preset, from runs that recorded cost (run_benchmark.py with run_cost)."""
    if "cpu_time_s" not in df:
        return pd.DataFrame()
    df = df[pd.to_numeric(df["cpu_time_s"], errors="coerce").notna()]
    rows = []
    for (name, preset), g in df.groupby(["dataset", "preset"]):
        def col(c: str) -> np.ndarray:
            return pd.to_numeric(g[c], errors="coerce").to_numpy(dtype=float) if c in g else np.array([np.nan])

        def sd(x: np.ndarray) -> Optional[float]:
            x = x[~np.isnan(x)]
            return float(x.std(ddof=1)) if len(x) > 1 else None

        wall, cpu = col("runtime_s"), col("cpu_time_s")
        rows.append({
            "dataset": name, "preset": preset, "n": len(g),
            "runtime_s": float(np.nanmean(wall)), "runtime_std": sd(wall),
            "cpu_time_s": float(np.nanmean(cpu)), "cpu_time_std": sd(cpu),
            "instances_per_s": float(np.nanmean(col("instances_per_s"))),
            "rss_increment_mb": float(np.nanmean(col("rss_increment_mb"))),
            "rss_increment_max_mb": float(np.nanmax(col("rss_increment_mb"))),
            "model_size_final_mb": float(np.nanmean(col("model_size_final_mb"))),
            "ram_hours_gb": float(np.nanmean(col("ram_hours_gb"))),
            "process_peak_rss_mb": float(np.nanmean(col("process_peak_rss_mb"))),
            "workers": ",".join(sorted({str(int(w)) for w in col("workers") if not np.isnan(w)})),
            "concurrent_runs": ",".join(sorted({str(int(c)) for c in col("concurrent_runs") if not np.isnan(c)})),
            "machine": "; ".join(sorted(set(g["machine"].dropna().astype(str)))) if "machine" in g else "",
        })
    return pd.DataFrame(rows)


def rank_tests(scores: pd.DataFrame, target: Optional[str]) -> List[str]:
    """scores: rows = blocks (datasets / cells), columns = presets; higher is better."""
    lines: List[str] = []
    scores = scores.dropna(axis=0, how="any")
    n, k = scores.shape
    if n < 2 or k < 2:
        return [f"_Not enough complete blocks for rank tests ({n} blocks x {k} presets with every preset present)._"]
    ranks = scores.rank(axis=1, ascending=False)
    avg = ranks.mean().sort_values()
    lines.append(f"Blocks: {n}; presets: {k}. Average rank (1 = best):\n")
    lines.append("| preset | avg rank | mean score |")
    lines.append("|---|---|---|")
    for p, r in avg.items():
        lines.append(f"| {p} | {r:.2f} | {scores[p].mean():.4f} |")
    if k >= 3:
        stat, pval = stats.friedmanchisquare(*[scores[c].to_numpy() for c in scores.columns])
        lines.append(f"\nFriedman chi2 = {stat:.3f}, p = {pval:.4g}.")
        q = NEMENYI_Q05.get(k)
        if q:
            cd = q * math.sqrt(k * (k + 1) / (6.0 * n))
            lines.append(f"Nemenyi critical difference (alpha 0.05) = {cd:.3f}; presets whose average ranks differ by more than this differ significantly.")
        if n < 10:
            lines.append(f"Caution: only {n} blocks; Friedman / Nemenyi have little power below about 10.")
    if target and target in scores:
        others = [c for c in scores.columns if c != target]
        res = []
        for o in others:
            d = scores[target] - scores[o]
            if np.allclose(d, 0):
                res.append((o, float("nan"), 1.0, d.mean()))
                continue
            w = stats.wilcoxon(scores[target], scores[o], zero_method="wilcox")
            res.append((o, float(w.statistic), float(w.pvalue), d.mean()))
        order = sorted(range(len(res)), key=lambda i: res[i][2])
        holm = [None] * len(res)
        running = 0.0
        for rank, i in enumerate(order):
            running = max(running, min(1.0, (len(res) - rank) * res[i][2]))
            holm[i] = running
        lines.append(f"\nWilcoxon signed-rank, {target} vs others (two-sided, Holm-corrected):\n")
        lines.append("| other | mean diff | W | p | p (Holm) |")
        lines.append("|---|---|---|---|---|")
        for (o, wstat, pval, md), ph in zip(res, holm):
            lines.append(f"| {o} | {md:+.4f} | {fmt(wstat, 1)} | {pval:.4g} | {ph:.4g} |")
    return lines


def md_table(df: pd.DataFrame, cols: List[str]) -> List[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt(r[c]) if isinstance(r[c], float) else fmt(r[c]) for c in cols) + " |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="outputs/benchmark")
    ap.add_argument("--datasets", nargs="+")
    ap.add_argument("--presets", nargs="+")
    ap.add_argument("--target", help="preset tested against every other preset (Wilcoxon)")
    ap.add_argument("--include-noncomparable", action="store_true",
                    help="also use non-comparable runs (report is marked exploratory)")
    ap.add_argument("--out", default=None, help="output directory (default reports/sota_<timestamp>)")
    args = ap.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text())["datasets"]
    df = load_runs(REPO / args.root)
    n_all = len(df)
    df = df[~df["smoke"].astype(bool)]
    if not args.include_noncomparable:
        df = df[df["comparable"].astype(bool)]
    if args.datasets:
        df = df[df["dataset"].isin(args.datasets)]
    if args.presets:
        df = df[df["preset"].isin(args.presets)]
    if df.empty:
        raise SystemExit("no runs left after filtering (smoke runs and non-comparable runs are excluded by default)")

    out_dir = REPO / (args.out or f"reports/sota_{time.strftime('%Y%m%d_%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)

    preq_tables, det_tables = [], []
    for name, g in df.groupby("dataset"):
        entry = registry[name]
        if entry["protocol"] == "injected_detection":
            det_tables.append(detection_table(g, entry, name))
        else:
            preq_tables.append(prequential_table(g, entry, name))
    preq_tables = [t for t in preq_tables if len(t)]
    det_tables = [t for t in det_tables if len(t)]
    preq = pd.concat(preq_tables, ignore_index=True) if preq_tables else pd.DataFrame()
    det = pd.concat(det_tables, ignore_index=True) if det_tables else pd.DataFrame()
    if len(preq):
        preq.to_csv(out_dir / "prequential.csv", index=False)
    if len(det):
        det.to_csv(out_dir / "detection_pooled.csv", index=False)

    lines = [f"# dataset_0921 vs literature ({time.strftime('%Y-%m-%d %H:%M')})", ""]
    lines.append(f"Runs used: {len(df)} of {n_all} (smoke runs excluded"
                 f"{'' if args.include_noncomparable else ', non-comparable runs excluded'}).")
    if args.include_noncomparable:
        lines.append("\n**Exploratory: includes non-comparable runs. Do not claim SOTA from this report.**")
    lines.append(f"Registry: `{REGISTRY_PATH.relative_to(REPO)}`. Metrics: `src/metrics/evaluate_run.py`.\n")

    if len(preq):
        lines.append("## Prequential datasets\n")
        lines.append("Difference = our mean - best literature value for that metric. 95% CI is a t-interval over seeds.\n")
        for name, g in preq.groupby("dataset"):
            entry = registry[name]
            lines.append(f"### {name} (role: {entry['role']})\n")
            lines += md_table(g, ["preset", "metric", "n", "mean", "std", "ci95", "sota_value", "sota_method", "diff_vs_sota",
                                  "classic_value", "classic_method", "diff_vs_classic"])
            lines.append(f"\n{entry.get('comparability_note', '')}\n")
        prim = preq[preq["metric"].isin(RANK_METRICS)]
        if len(prim):
            for metric, gm in prim.groupby("metric"):
                lines.append(f"### Ranking across datasets on `{metric}`\n")
                lines += rank_tests(gm.pivot_table(index="dataset", columns="preset", values="mean"), args.target)
                lines.append("")

    if len(det):
        lines.append("## Injected drift detection (pooled over trials)\n")
        lines.append("tp/fp/fn are summed over all trials of a cell before precision/recall/F1, as in Cerqueira et al.; "
                     "`far_cerqueira` is their FAR (summed false alarms / one stream length x 1000), `far_per_run` the per-stream average. "
                     "`sota_f1` is the best of their 14 detectors for that cell.\n")
        for name, g in det.groupby("dataset"):
            entry = registry[name]
            kinds = entry.get("comparable_kinds")
            lines.append(f"### {name}\n")
            if kinds:
                lines.append(f"Only preset kinds {kinds} follow the literature protocol on this dataset; other rows appear only with --include-noncomparable.\n")
            lines += md_table(g.sort_values(["cell", "preset"]),
                              ["cell", "preset", "n_runs", "f1", "precision", "recall", "episode_recall", "mdt", "far_cerqueira",
                               "sota_f1", "sota_method", "diff_f1_vs_sota"])
            cal = entry.get("calibration")
            gc = g[g["preset"] == cal["preset"]] if cal else g.iloc[0:0]
            if len(gc):
                lines.append(f"\nCalibration: `{cal['preset']}` vs their {cal['method']} (same cell, pooled):\n")
                lines += md_table(gc.sort_values("cell"),
                                  ["cell", "f1", "calib_f1", "episode_recall", "calib_episode_recall", "mdt", "calib_mdt",
                                   "far_cerqueira", "calib_far"])
            lines.append("")
        lines.append("### Ranking across dataset x cell on pooled F1\n")
        det = det.assign(block=det["dataset"] + ":" + det["cell"])
        lines += rank_tests(det.pivot_table(index="block", columns="preset", values="f1"), args.target)
        lines.append("")

    cost = cost_table(df)
    lines.append("## Cost (time and memory)\n")
    if len(cost):
        cost.to_csv(out_dir / "cost.csv", index=False)
        n_without = len(df) - int(cost["n"].sum())
        lines.append("Mean per run. `runtime_s` is wall time, `cpu_time_s` process CPU time (both exclude data loading); "
                     "`rss_increment_mb` is the peak resident memory of the run's own process minus its level before the "
                     "system was built, `ram_hours_gb` that increment integrated over the run (GB x hours), "
                     "`model_size_final_mb` the system's Python object size after the last instance. "
                     "`concurrent_runs` is the most runs that executed at the same time as a run. "
                     "Memory is per process and valid at any concurrency; times are strict only where "
                     "`concurrent_runs` is 1 (`--workers 1`) and comparable only between rows with the same machine "
                     "and the same `concurrent_runs` (CPU time is less affected by parallel load than wall time).\n")
        if n_without:
            lines.append(f"{n_without} run(s) predate cost tracking and are not in this table.\n")
        if cost["machine"].str.contains(";").any() or cost["machine"].nunique() > 1:
            lines.append("**Runs come from more than one machine: do not compare their times directly.**\n")
        mixed = [name for name, g in cost.groupby("dataset")
                 if g["concurrent_runs"].str.contains(",").any() or g["concurrent_runs"].nunique() > 1]
        if mixed:
            lines.append(f"**Different `concurrent_runs` within {', '.join(mixed)}: those times were measured under "
                         "different parallel load and are not directly comparable; re-run with `--workers 1` for a "
                         "strict time comparison.**\n")
        elif (cost["concurrent_runs"] != "1").any():
            lines.append("Some runs shared the machine with other runs (`concurrent_runs` > 1): their times are "
                         "indicative only.\n")
        lines += md_table(cost.sort_values(["dataset", "preset"]),
                          ["dataset", "preset", "n", "runtime_s", "runtime_std", "cpu_time_s", "instances_per_s",
                           "rss_increment_mb", "rss_increment_max_mb", "model_size_final_mb", "ram_hours_gb",
                           "concurrent_runs", "machine"])
    else:
        lines.append("_No run in this selection recorded cost; re-run with the current scripts/run_benchmark.py._")
    lines.append("")

    (out_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n")
    print("\n".join(lines))
    print(f"\nreport -> {out_dir / 'report.md'}")


if __name__ == "__main__":
    main()
