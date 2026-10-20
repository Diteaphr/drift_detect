"""Report for the pool_fade suite: accuracy vs model-pool memory per fade mechanism.

Reads the runner's ``runs.csv`` (benchmark metrics and cost) and each run's
``pool_metrics.json`` (written by ``run_benchmark.py --pool-trace``); it does not
recompute any benchmark metric. Writes to ``reports/pool_fade_<timestamp>/``:

* ``pool_summary.csv``: one row per dataset x preset;
* ``pareto_<dataset>.png``: accuracy vs time-weighted mean pool KB;
* ``report.md``: per-dataset tables, Pareto-optimal presets, accuracy lost per
  KB saved against each backbone's reuse_value reference, average ranks and a
  Friedman test across datasets.

  python3 scripts/report_pool_fade.py --root outputs/benchmark_poolfade
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]

# Fixed categorical order (reference palette, light surface).
MECHANISMS = ["ecpf", "reuse_value", "density", "rent", "entry", "freq", "decay", "subst"]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MARKERS = {"e10bft": "o", "ecpf": "s"}
INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"

METRIC_COLS = ["acc_prequential", "kappa_m", "kappa_t", "runtime_s", "cpu_time_s", "rss_increment_mb",
               "model_size_final_mb", "ram_hours_gb", "concurrent_runs", "comparable", "smoke"]
POOL_COLS = ["pool_kb_mean", "pool_kb_peak", "pool_slots_mean", "pool_kb_x_instances",
             "recovery_acc_mean", "regret_rate", "regret_count", "evictions_total", "evictions_fade",
             "evictions_cap", "evictions_budget", "evictions_merge", "evicted_never_reused_frac",
             "reuse_episodes", "reuse_value_mean", "reuse_positive_frac", "pool_time_s",
             "sizing_time_s", "trace_time_s", "num_drifts"]


def parse_preset(name: str) -> Dict[str, Any]:
    """Backbone, mechanism and parameter label from a pool_fade preset name."""
    if name == "e10bft":
        return {"backbone": "e10bft", "mechanism": "ecpf", "param": ""}
    if name == "ecpf_paper":
        return {"backbone": "ecpf", "mechanism": "ecpf", "param": ""}
    if name == "ecpf_reuse_value":
        return {"backbone": "ecpf", "mechanism": "reuse_value", "param": ""}
    backbone, _, rest = name.partition("_")
    for mech in MECHANISMS:
        if rest == mech or rest.startswith(mech + "_"):
            return {"backbone": backbone, "mechanism": mech, "param": rest[len(mech) + 1:]}
    return {"backbone": backbone, "mechanism": rest, "param": ""}


def collect(root: Path, datasets: Optional[List[str]]) -> pd.DataFrame:
    rows = []
    for runs in sorted(root.glob("*/*/runs.csv")):
        dataset = runs.parent.parent.name
        if datasets and dataset not in datasets:
            continue
        df = pd.read_csv(runs)
        for _, r in df.iterrows():
            row = {"dataset": dataset, "preset": r["preset"], **parse_preset(r["preset"])}
            row.update({c: r.get(c) for c in METRIC_COLS})
            pm_path = REPO / r["run_dir"] / "pool_metrics.json"
            pm = json.loads(pm_path.read_text()) if pm_path.exists() else {}
            row.update({c: pm.get(c) for c in POOL_COLS})
            rows.append(row)
    return pd.DataFrame(rows)


def pareto(df: pd.DataFrame) -> List[str]:
    """Presets not dominated on (higher accuracy, lower mean pool KB)."""
    d = df.dropna(subset=["acc_prequential", "pool_kb_mean"])
    keep = []
    for _, r in d.iterrows():
        dominated = ((d["acc_prequential"] >= r["acc_prequential"]) & (d["pool_kb_mean"] <= r["pool_kb_mean"])
                     & ((d["acc_prequential"] > r["acc_prequential"]) | (d["pool_kb_mean"] < r["pool_kb_mean"])))
        if not dominated.any():
            keep.append(r["preset"])
    return keep


def add_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy change (points) per 100 KB of pool saved, vs the backbone's reuse_value reference."""
    ref_name = {"e10bft": "e10bft_reuse_value", "ecpf": "ecpf_reuse_value"}
    out = []
    for (ds, bb), g in df.groupby(["dataset", "backbone"]):
        ref = g[g["preset"] == ref_name.get(bb)]
        g = g.copy()
        if len(ref):
            ra, rk = float(ref["acc_prequential"].iloc[0]), ref["pool_kb_mean"].iloc[0]
            g["d_acc_pts"] = (g["acc_prequential"] - ra) * 100
            g["d_pool_kb"] = g["pool_kb_mean"] - rk if pd.notna(rk) else np.nan
            saved = -g["d_pool_kb"]
            g["acc_pts_per_100kb_saved"] = np.where(saved > 1e-9, g["d_acc_pts"] / saved * 100, np.nan)
        out.append(g)
    return pd.concat(out) if out else df


def plot(df: pd.DataFrame, dataset: str, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = df.dropna(subset=["acc_prequential", "pool_kb_mean"])
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for mech, color in zip(MECHANISMS, COLORS):
        for bb, marker in MARKERS.items():
            g = d[(d["mechanism"] == mech) & (d["backbone"] == bb)]
            if g.empty:
                continue
            ax.scatter(g["pool_kb_mean"], g["acc_prequential"] * 100, s=64, marker=marker, color=color,
                       edgecolors=SURFACE, linewidths=2, label=f"{mech} ({bb})", zorder=3)
    front = d[d["preset"].isin(pareto(d))].sort_values("pool_kb_mean")
    ax.plot(front["pool_kb_mean"], front["acc_prequential"] * 100, color=INK2, linewidth=2,
            linestyle="--", zorder=2, label="Pareto front")
    for _, r in front.iterrows():
        ax.annotate(r["preset"], (r["pool_kb_mean"], r["acc_prequential"] * 100), fontsize=7,
                    color=INK2, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("Mean model-pool memory (KB, time-weighted)", color=INK)
    ax.set_ylabel("Prequential accuracy (%)", color=INK)
    ax.set_title(f"{dataset}: accuracy vs pool memory", color=INK, loc="left")
    ax.grid(color="#e5e4e0", linewidth=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2)
    ax.legend(fontsize=7, ncol=2, frameon=False, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fmt(v: Any, nd: int = 4) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    return f"{v:.{nd}f}" if isinstance(v, (float, np.floating)) else str(v)


def ranks_and_friedman(df: pd.DataFrame) -> List[str]:
    lines: List[str] = []
    piv = df.pivot_table(index="dataset", columns="preset", values="acc_prequential").dropna(axis=1)
    kb = df.pivot_table(index="dataset", columns="preset", values="pool_kb_mean").reindex(columns=piv.columns)
    if piv.shape[0] < 2 or piv.shape[1] < 3:
        return ["Not enough datasets / presets for ranks."]
    acc_rank = piv.rank(axis=1, ascending=False).mean().rename("avg_rank_acc")
    kb_rank = kb.rank(axis=1, ascending=True).mean().rename("avg_rank_pool_kb")
    tab = pd.concat([acc_rank, kb_rank], axis=1).sort_values("avg_rank_acc")
    lines += ["| preset | avg rank accuracy (1 = best) | avg rank pool KB (1 = smallest) |", "|---|---|---|"]
    lines += [f"| {p} | {fmt(r.avg_rank_acc, 2)} | {fmt(r.avg_rank_pool_kb, 2)} |" for p, r in tab.iterrows()]
    try:
        from scipy.stats import friedmanchisquare
        stat, p = friedmanchisquare(*[piv[c].to_numpy() for c in piv.columns])
        lines += ["", f"Friedman test on accuracy over {piv.shape[0]} datasets x {piv.shape[1]} presets: "
                      f"chi2 = {stat:.2f}, p = {p:.3g}."
                      + (" With fewer than 5 datasets this test has very little power; treat ranks as indicative."
                         if piv.shape[0] < 5 else "")]
    except Exception as exc:  # pragma: no cover - scipy missing or degenerate input
        lines += ["", f"Friedman test not computed ({exc})."]
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="outputs/benchmark_poolfade")
    ap.add_argument("--datasets", nargs="+", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    df = collect(REPO / args.root, args.datasets)
    if df.empty:
        raise SystemExit(f"no runs.csv under {args.root}")
    df = add_efficiency(df)
    out = REPO / (args.out or f"reports/pool_fade_{time.strftime('%Y%m%d_%H%M%S')}")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "pool_summary.csv", index=False)

    md = [f"# Pool fade mechanisms — accuracy vs pool memory", "",
          f"Source: `{args.root}`; benchmark metrics from `runs.csv`, pool diagnostics from `pool_metrics.json`.", ""]
    smoke = df["smoke"].astype(str).str.lower().eq("true").any()
    noncomp = df["comparable"].astype(str).str.lower().eq("false").any()
    if smoke or noncomp:
        md += ["**Warning:** some rows are smoke or non-comparable runs; numbers are reference only.", ""]
    if df["concurrent_runs"].nunique(dropna=True) > 1:
        md += ["**Warning:** rows mix different `concurrent_runs`; times are indicative only.", ""]
    for ds, g in df.groupby("dataset"):
        g = g.sort_values(["backbone", "mechanism", "param"])
        md += [f"## {ds}", "", f"![pareto](pareto_{ds}.png)", "",
               f"Pareto-optimal (accuracy up, pool KB down): {', '.join(pareto(g)) or 'none'}", "",
               "| preset | acc | kappa_m | pool KB mean | pool KB peak | slots | recovery acc | regret rate "
               "| evictions (fade/cap/budget/merge) | reuse value mean | Δacc pts vs reuse_value "
               "| acc pts per 100 KB saved | pool time s | runtime s |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in g.iterrows():
            ev = "/".join(fmt(r.get(f"evictions_{k}"), 0) or "0" for k in ("fade", "cap", "budget", "merge"))
            md.append(" | ".join([
                f"| {r['preset']}", fmt(r["acc_prequential"]), fmt(r["kappa_m"]), fmt(r["pool_kb_mean"], 1),
                fmt(r["pool_kb_peak"], 1), fmt(r["pool_slots_mean"], 2), fmt(r["recovery_acc_mean"]),
                fmt(r["regret_rate"], 3), ev, fmt(r["reuse_value_mean"], 2), fmt(r.get("d_acc_pts"), 2),
                fmt(r.get("acc_pts_per_100kb_saved"), 3), fmt(r["pool_time_s"], 2),
                fmt(r["runtime_s"], 1)]) + " |")
        md.append("")
        plot(g, ds, out / f"pareto_{ds}.png")
    md += ["## Across datasets", ""] + ranks_and_friedman(df) + [""]
    md += ["## Notes", "",
           "- Pool KB is the summed `deep_sizeof` of the stored experts' models (estimator only, without "
           "the adapter's copied sample buffer), time-weighted over the stream.",
           "- Regret = a recently evicted expert (last 20) would have scored higher on the warning buffer "
           "than the best stored one; the archive is diagnostic only and is excluded from model size, "
           "but it is held in process memory, so RSS includes it for every preset alike.",
           "- Recovery acc = prequential accuracy over the 500 instances after each alarm.",
           "- `acc pts per 100 KB saved` = accuracy change (points) per 100 KB of mean pool memory saved "
           "against the backbone's reuse_value reference: positive = more accurate and smaller, negative = the "
           "accuracy paid for the memory saved; empty when the preset does not use less pool memory."]
    (out / "report.md").write_text("\n".join(md) + "\n")
    print(f"report -> {out / 'report.md'}")


if __name__ == "__main__":
    main()
