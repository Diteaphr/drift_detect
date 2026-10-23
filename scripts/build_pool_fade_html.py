"""Build the pool_fade presentation page (self-contained HTML) from a pool fade report.

Reads ``pool_summary.csv`` written by ``scripts/report_pool_fade.py`` (one row per
dataset x preset, multi-stream datasets already averaged) and each run's
``pool_trace.json`` for the memory timelines, then fills
``scripts/templates/pool_fade_presentation.html``. No metric is recomputed here.

  python3 scripts/build_pool_fade_html.py \
      --report-dir outputs/benchmark_poolfade/pool_fade_20261020_222312 \
      --root outputs/benchmark_poolfade \
      --timeline-stream synthetic_binary=recurring_sudden_sea100k_g01
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "scripts" / "templates" / "pool_fade_presentation.html"

# Display order and short labels; unknown datasets are appended with their own name.
LABELS = {
    "electricity": "electricity",
    "insects_abrupt_balanced": "insects_abrupt",
    "insects_incremental_abrupt_reoccurring_balanced": "insects_inc_abrupt_reoc",
    "insects_incremental_reoccurring_balanced": "insects_inc_reoc",
    "synthetic_binary": "synth_bin_recurring",
}


def _num(v: Any) -> Any:
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report-dir", required=True, help="folder with pool_summary.csv")
    ap.add_argument("--root", default="outputs/benchmark_poolfade", help="benchmark output root (runs.csv)")
    ap.add_argument("--out", default=None, help="default: <report-dir>/pool_fade_presentation.html")
    ap.add_argument("--timeline-stream", action="append", default=[], metavar="DATASET=STREAM",
                    help="stream to plot in figure 2 for a multi-stream dataset (default: first stream)")
    args = ap.parse_args()

    report_dir = REPO / args.report_dir
    summary = pd.read_csv(report_dir / "pool_summary.csv")
    chosen = dict(s.split("=", 1) for s in args.timeline_stream)

    rows: List[Dict[str, Any]] = [dict(
        dataset=r.dataset, preset=r.preset, backbone=r.backbone, mechanism=r.mechanism,
        acc=_num(r.acc_prequential), kappa_m=_num(r.kappa_m), kb=_num(r.pool_kb_mean), kb_peak=_num(r.pool_kb_peak),
        slots=_num(r.pool_slots_mean), rec=_num(r.recovery_acc_mean), regret=_num(r.regret_rate),
        ev=[int(round(r[f"evictions_{k}"] or 0)) for k in ("fade", "cap", "budget", "merge")],
        rv=_num(r.reuse_value_mean), model_mb=_num(r.model_size_final_mb), runtime=_num(r.runtime_s),
    ) for _, r in summary.iterrows()]

    present = list(summary["dataset"].unique())
    order = [d for d in LABELS if d in present] + [d for d in present if d not in LABELS]
    datasets, timelines, nlen, tl_stream = [], {}, {}, {}
    for ds in order:
        g = summary[summary["dataset"] == ds]
        n_streams = int(g["n_streams"].max())
        datasets.append([ds, LABELS.get(ds, ds), n_streams, bool(g["comparable"].all())])
        runs = pd.concat(pd.read_csv(p) for p in sorted((REPO / args.root / ds).glob("*/runs.csv")))
        streams = sorted(runs["stream"].astype(str).unique())
        stream = chosen.get(ds, streams[0])
        if stream not in streams:
            raise SystemExit(f"{ds}: stream {stream!r} not found; choose one of {streams}")
        if n_streams > 1:
            tl_stream[ds] = stream
        for _, r in runs[runs["stream"].astype(str) == stream].iterrows():
            trace = json.loads((REPO / r["run_dir"] / "pool_trace.json").read_text())
            timelines[f"{ds}|{r['preset']}"] = [[int(t), int(n), round(kb, 1)] for t, n, kb in trace["timeline"]]
            nlen[ds] = int(r["n_samples"])

    html = TEMPLATE.read_text()
    for key, value in (("__DATA__", rows), ("__TIMELINE__", timelines), ("__NLEN__", nlen),
                       ("__TL_STREAM__", tl_stream), ("__DATASETS__", datasets)):
        if html.count(key) != 1:
            raise SystemExit(f"template placeholder {key} must appear exactly once")
        html = html.replace(key, json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    out = Path(args.out) if args.out else report_dir / "pool_fade_presentation.html"
    out.write_text(html)
    print(f"{len(rows)} rows, {len(datasets)} datasets, {len(timelines)} timelines -> {out}")


if __name__ == "__main__":
    main()
