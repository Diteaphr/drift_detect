"""Aggregate the per-detection regression FP diagnosis into report tables.

Reads what ``diagnose_regression_fp.py`` wrote and prints markdown tables:
label counts and recall, error direction by label, leader-swap coincidence by
label against its chance baseline, normalizer discordance, echo/orphan gap
distributions, per-segment normalized-vs-raw error levels, and a counterfactual
replay of the drift ADWIN on the RAW residual at a fixed scale (how many fires
the online normalizer itself manufactures).

Usage
-----
    python scripts/analyze_regression_fp.py --dir outputs/regression_fp_diagnosis
"""

from __future__ import annotations

import argparse
import glob
import gzip
import os
import sys
import warnings

import numpy as np
import pandas as pd
from river import drift

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_task_matrix import PERTURBATION, load_stream  # noqa: E402
from src.metrics.correct_detection import (  # noqa: E402
    build_perturbation_intervals, compute_correct_detection,
)

LABELS = ["hit", "echo_inwin", "echo", "orphan"]


def md(df: pd.DataFrame, floatfmt: str = "%.3f") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append(floatfmt % v if isinstance(v, float) and not np.isnan(v) else
                         "" if isinstance(v, float) else str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


ECHO_GAP = 3000


def stream_path(ds: str) -> str:
    """Dataset key (as written by diagnose_regression_fp.py) -> csv path."""
    if "/" not in ds:
        return "data/synthetic_regression/" + ds
    kind, tier, base = ds.split("/")
    return "data/synthetic_dataset_joe/regression/%s_drift/%s/%s" % (kind, tier, base)


def sublabel(det: pd.DataFrame, summ: pd.DataFrame) -> None:
    """Refine the FP labels post hoc, in place.

    stale_warning : the warning opened before a MISSED ground-truth drift and the
                    confirmation came after it -- the detection is stamped with the
                    stale warning time, so a real hit is scored as an FP (the defect
                    the warning timeout fixes on multi-class)
    late          : FP within ECHO_GAP after a missed drift = a slow detection that
                    fell outside the 1000-step scoring window
    pre_drift     : FP whose warning opened <= 500 steps before the next drift
    Also parses the reuse decision out of the stage-3 details: the warning-buffer
    length the decision was made on, and the buffer scores of the reused best
    slot vs the fresh learner.
    """
    det["sub"] = ""
    for col in ("buffer_len", "acc_best", "acc_new", "acc_current"):
        key = {"buffer_len": "buffer_len", "acc_best": "acc_best_on_warning",
               "acc_new": "acc_new_on_warning", "acc_current": "acc_current_on_warning"}[col]
        det[col] = pd.to_numeric(det["stage3"].astype(str).str.extract(r'"%s": ([-\d.e]+)' % key)[0],
                                 errors="coerce")
    for (ds, cfg), sub in det.groupby(["dataset", "config"]):
        n = int(summ[(summ["dataset"] == ds) & (summ["config"] == cfg)]["n_steps"].iloc[0])
        _, _, intervals = load_stream(stream_path(ds), n)
        hits = sub[sub["label"] == "hit"]
        hit_starts = {int(r.warning_t - r.gap_prev_gt) for r in hits.itertuples()
                      if r.gap_prev_gt == r.gap_prev_gt}
        missed = [s for s, _ in intervals if s not in hit_starts]
        for r in sub.sort_values("warning_t").itertuples():
            if r.label not in ("echo", "orphan"):
                continue
            tag = ""
            if any(r.warning_t < s <= r.confirmation_t for s in missed):
                tag = "stale_warning"
            elif any(0 < r.warning_t - s <= ECHO_GAP for s in missed):
                tag = "late"
            elif r.gap_next_gt == r.gap_next_gt and r.gap_next_gt <= 500:
                tag = "pre_drift"
            det.loc[r.Index, "sub"] = tag


def replay(series: np.ndarray, delta: float = 0.05, grace: int = 30):
    """ADWIN that resets itself on every fire = the pipeline's drift arm."""
    a = drift.ADWIN(delta=delta, grace_period=grace)
    fires = []
    for i, v in enumerate(series):
        a.update(float(v))
        if a.drift_detected:
            fires.append(i)
            a = drift.ADWIN(delta=delta, grace_period=grace)
    return fires


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default="outputs/regression_fp_diagnosis")
    ap.add_argument("--no-replay", action="store_true")
    args = ap.parse_args()

    det = pd.read_csv(os.path.join(args.dir, "detections.csv"))
    summ = pd.read_csv(os.path.join(args.dir, "summary.csv"))
    segs = pd.read_csv(os.path.join(args.dir, "segment_levels.csv"))
    for df in (det, summ, segs):
        df["group"] = np.where(df["dataset"].str.contains("/"),
                               "joe-" + df["dataset"].str.split("/").str[0], "synthetic")
    det["fake_rise"] = (det["direction"] == "rise") & (det["raw_rel_change"] < 0.05)
    det["discord"] = det["discord"].fillna("")
    det.loc[det["fake_rise"], "discord"] = "fake_rise"
    sublabel(det, summ)
    det.to_csv(os.path.join(args.dir, "detections_labelled.csv"), index=False)

    print("## 0. FP sub-labels (post hoc) and the expert the preceding hit installed\n")
    fp = det[det["label"].isin(["echo", "orphan"])]
    t = fp.assign(sub=fp["sub"].replace("", "(none)")).groupby(["config", "label", "sub"]).size()
    print(md(t.unstack(fill_value=0).reset_index()), "\n")
    print("Reuse decision at each confirmation: length of the warning buffer it was made on",
          "(buffer = confirm_age + 1 instances; the reused best slot is chosen by its score on it):\n")
    b = det.groupby(["config", "label"]).agg(
        n=("buffer_len", "size"), buf_median=("buffer_len", "median"),
        buf_is_1=("buffer_len", lambda s: float((s == 1).mean())),
        buf_le_10=("buffer_len", lambda s: float((s <= 10).mean())),
    ).reset_index()
    print(md(b), "\n")

    print("Immediate effect of the model installed at each confirmation: raw MAE over the 200 steps",
          "after the install vs the 200 before it (ratio > 1.5 = the replacement made things worse):\n")
    det["install_ratio"] = np.nan
    for (ds, cfg), sub in det.groupby(["dataset", "config"]):
        fn = os.path.join(args.dir, "signals", "%s__%s.csv.gz" % (
            ds.replace("/", "_").replace(".csv", ""), cfg.replace("/", "_")))
        if not os.path.exists(fn):
            continue
        with gzip.open(fn, "rt") as f:
            sg = pd.read_csv(f).set_index("t")
        raw, nrm = sg["raw"], sg["err"]
        for r in sub.itertuples():
            o, nw = nrm.loc[r.confirmation_t - 2000:r.confirmation_t - 501], nrm.loc[r.confirmation_t - 500:r.confirmation_t - 1]
            if len(o) > 300 and len(nw) > 100:
                det.loc[r.Index, "pre_trend_norm"] = nw.mean() - o.mean()
            # slower scale for what ADWIN's long window can cut: last 3000 vs the 6000 before
            lo, ln = raw.loc[r.confirmation_t - 9000:r.confirmation_t - 3001], raw.loc[r.confirmation_t - 3000:r.confirmation_t - 1]
            lon, lnn = nrm.loc[r.confirmation_t - 9000:r.confirmation_t - 3001], nrm.loc[r.confirmation_t - 3000:r.confirmation_t - 1]
            if len(lo) > 2000 and len(ln) > 1500 and lo.mean() > 0:
                det.loc[r.Index, "long_trend"] = ln.mean() / lo.mean() - 1
                det.loc[r.Index, "long_trend_norm"] = lnn.mean() - lon.mean()
            b, a = raw.loc[r.confirmation_t - 200:r.confirmation_t - 1], raw.loc[r.confirmation_t:r.confirmation_t + 199]
            if len(b) > 50 and len(a) > 50 and b.mean() > 0:
                det.loc[r.Index, "install_ratio"] = a.mean() / b.mean()
            # trend the detector saw BEFORE it fired: last 500 steps vs the 1500 before them
            old, new = raw.loc[r.confirmation_t - 2000:r.confirmation_t - 501], raw.loc[r.confirmation_t - 500:r.confirmation_t - 1]
            if len(old) > 300 and len(new) > 100 and old.mean() > 0:
                det.loc[r.Index, "pre_trend"] = new.mean() / old.mean() - 1
    det["pre_dir"] = np.select([det["pre_trend"] > 0.05, det["pre_trend"] < -0.05], ["rise", "fall"], "flat")
    det["pre_dir_norm"] = np.select([det["pre_trend_norm"] > 0.02, det["pre_trend_norm"] < -0.02],
                                    ["rise", "fall"], "flat")
    print("Pre-confirmation trend of the RAW error (500 steps before vs the 1500 before those):\n")
    pt = det.dropna(subset=["pre_trend"]).groupby(["config", "label", "pre_dir"]).size().unstack(fill_value=0)
    print(md(pt.reset_index()), "\n")
    print("Same windows on the NORMALIZED error, orphans only, cross-tabbed against the raw trend",
          "(raw flat but normalized moving = the online normalizer's statistics, not the model):\n")
    orp = det[(det["label"] == "orphan")].dropna(subset=["pre_trend"])
    ct = orp.groupby(["config", "pre_dir", "pre_dir_norm"]).size().unstack(fill_value=0)
    print(md(ct.reset_index()), "\n")
    print("Orphans that are flat at the short scale, re-examined at ADWIN's scale (last 3000 vs the 6000",
          "before): raw trend vs normalized trend (thresholds 5% raw, 0.02 normalized):\n")
    ff = orp[(orp["pre_dir"] == "flat") & (orp["pre_dir_norm"] == "flat")].dropna(subset=["long_trend"]).copy()
    ff["raw_long"] = np.select([ff["long_trend"] > 0.05, ff["long_trend"] < -0.05], ["rise", "fall"], "flat")
    ff["norm_long"] = np.select([ff["long_trend_norm"] > 0.02, ff["long_trend_norm"] < -0.02], ["rise", "fall"], "flat")
    print(md(ff.groupby(["config", "raw_long", "norm_long"]).size().unstack(fill_value=0).reset_index()),
          "\n(n=%d of %d flat/flat orphans had 9000 steps of history)\n" % (len(ff), int(((orp["pre_dir"] == "flat") & (orp["pre_dir_norm"] == "flat")).sum())))
    ir = det.dropna(subset=["install_ratio"]).groupby(["config", "label"]).agg(
        n=("install_ratio", "size"), median_ratio=("install_ratio", "median"),
        worse_x1_5=("install_ratio", lambda s: float((s > 1.5).mean())),
        better_x0_67=("install_ratio", lambda s: float((s < 0.67).mean()))).reset_index()
    print(md(ir), "\n")
    det.to_csv(os.path.join(args.dir, "detections_labelled.csv"), index=False)

    print("## 1. Recall and FP structure (per config x group)\n")
    g = summ.groupby(["group", "config"]).agg(
        streams=("dataset", "count"), n_gt=("n_gt", "sum"), hits=("hit", "sum"),
        tp=("tp", "sum"), fp=("fp", "sum"), echo=("echo", "sum"), orphan=("orphan", "sum"),
        echo_inwin=("echo_inwin", "sum"), dropped=("dropped_confirms", "sum"),
        swaps=("n_swaps", "sum"), mae=("mae", "mean"), cd=("cd", "mean")).reset_index()
    g["recall"] = g["tp"] / g["n_gt"]
    g["fp_per_stream"] = g["fp"] / g["streams"]
    print(md(g[["group", "config", "streams", "n_gt", "tp", "recall", "fp", "fp_per_stream",
                "echo", "orphan", "echo_inwin", "dropped", "swaps", "mae", "cd"]]), "\n")

    print("## 2. Error direction at the detection, by label (pooled over configs)\n")
    d = det.groupby(["config", "label", "direction"]).size().unstack(fill_value=0)
    print(md(d.reset_index()), "\n")
    print("Mean normalized delta / raw relative change by label:\n")
    m = det.groupby(["config", "label"]).agg(n=("label", "size"), norm_delta=("norm_delta", "mean"),
                                             raw_rel=("raw_rel_change", "mean"),
                                             confirm_age=("confirm_age", "median")).reset_index()
    print(md(m), "\n")

    print("## 3. Leader-swap coincidence (detection <= 600 steps after a swap), by label\n")
    base = (summ["swap_baseline"] * summ["n_steps"]).sum() / summ["n_steps"].sum()
    s = det.groupby(["config", "label"]).agg(n=("swap_within", "size"),
                                             within600=("swap_within", "mean")).reset_index()
    for cfg in summ["config"].unique():
        sub = summ[summ["config"] == cfg]
        s.loc[s["config"] == cfg, "chance"] = (sub["swap_baseline"] * sub["n_steps"]).sum() / sub["n_steps"].sum()
    print(md(s), "\n(pooled chance baseline %.3f)\n" % base)

    print("## 4. Normalizer discordance by label\n")
    dc = det.groupby(["label", "discord"]).size().unstack(fill_value=0)
    print(md(dc.reset_index()), "\n")

    print("## 5. Gap distributions\n")
    for lab in ("echo", "echo_inwin", "orphan"):
        x = pd.to_numeric(det.loc[det["label"] == lab, "gap_prev_gt"], errors="coerce").dropna()
        if len(x):
            print("- %s: n=%d, steps after the previous ground-truth drift: p25=%d median=%d p75=%d max=%d"
                  % (lab, len(x), x.quantile(.25), x.median(), x.quantile(.75), x.max()))
    first = det[(det["label"] == "orphan") & det["gap_prev_gt"].isna()]
    print("- orphans BEFORE the first ground-truth drift (first-concept learning ramp): %d of %d orphans"
          % (len(first), (det["label"] == "orphan").sum()))
    print()

    print("## 6. Per-segment error level (normalized vs raw), first -> last stable segment\n")
    rows = []
    for (ds, cfg), sub in segs.groupby(["dataset", "config"]):
        sub = sub.sort_values("seg_start")
        if len(sub) < 2:
            continue
        rows.append({"dataset": ds, "config": cfg, "segments": len(sub),
                     "norm_first": sub["norm"].iloc[0], "norm_last": sub["norm"].iloc[-1],
                     "raw_first": sub["raw"].iloc[0], "raw_last": sub["raw"].iloc[-1]})
    seg_df = pd.DataFrame(rows)
    if len(seg_df):
        seg_df["norm_change"] = seg_df["norm_last"] - seg_df["norm_first"]
        seg_df["raw_rel_change"] = seg_df["raw_last"] / seg_df["raw_first"] - 1
        print(md(seg_df), "\n")

    if args.no_replay:
        return
    print("## 7. Counterfactual replay: drift ADWIN on normalized err vs raw residual at a FIXED scale\n")
    print("Replay fidelity = replay fires on `err` vs the pipeline's own drift-arm fires (is_drift rows).",
          "Fixed scale = raw / (mean + 3 sd of the whole stream's raw residual), clipped to [0, 1].\n")
    rows = []
    for path in sorted(glob.glob(os.path.join(args.dir, "signals", "*.csv.gz"))):
        name = os.path.basename(path)[:-7]
        key, cfg = name.rsplit("__", 1)
        with gzip.open(path, "rt") as f:
            sig = pd.read_csv(f)
        # find the stream's ground truth again from its dataset key
        drow = summ[(summ["dataset"].str.replace("/", "_").str.replace(".csv", "") == key)
                    & (summ["config"] == cfg.replace("_", "/"))]
        ds = drow["dataset"].iloc[0]
        _, _, intervals = load_stream(stream_path(ds), int(drow["n_steps"].iloc[0]))
        windows = build_perturbation_intervals(intervals, extension=PERTURBATION)
        t = sig["t"].values
        f_norm = replay(sig["err"].values)
        raw = sig["raw"].values
        scale = raw.mean() + 3 * raw.std()
        f_raw = replay(np.clip(raw / scale, 0, 1))
        pipe_fires = int(sig["is_drift"].sum())
        cd_n = compute_correct_detection([int(t[i]) for i in f_norm], windows)
        cd_r = compute_correct_detection([int(t[i]) for i in f_raw], windows)
        rows.append({"dataset": ds, "config": cfg.replace("_", "/"), "pipe_fires": pipe_fires,
                     "replay_norm": len(f_norm), "norm_tp": cd_n.tp, "norm_fp": cd_n.fp,
                     "replay_raw_fixed": len(f_raw), "raw_tp": cd_r.tp, "raw_fp": cd_r.fp})
    r = pd.DataFrame(rows)
    print(md(r), "\n")
    tot = r.groupby("config")[["pipe_fires", "replay_norm", "norm_tp", "norm_fp",
                               "replay_raw_fixed", "raw_tp", "raw_fp"]].sum().reset_index()
    print("Totals:\n")
    print(md(tot))


if __name__ == "__main__":
    main()
