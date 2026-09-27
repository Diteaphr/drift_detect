"""H0/H1 diagnostics for the frozen-reference arms (docs_myself/凍結參照模型_問題報告.md §7.2-7.3).

Reads a diagnose_regression_fp.py output dir (detections.csv, summary.csv, signals/*.csv.gz)
and, per (dataset, config), computes for every detection:

  z_ref, z_leader   fixed-window shift at the confirmation t_c with BOTH windows BEFORE t_c and
                    inside the SAME reference era (recent = last w steps, previous = the w before;
                    w = min(500, era_len // 2), NaN when the era is shorter than 100 steps), on
                    the RAW residual of the reference / the leader.  Never crosses a reference
                    replacement -- at t_c the k=0 arm swaps the reference.
  z_split           detector-native split statistic over the drift arm's window (since its last
                    fire) on the value the detector actually consumed (drift_value), best split
                    with >= 30 per side: |mL-mR| / sqrt(vL/nL + vR/nR).
  ref_age           how long the reference had been frozen at t_c.

and for every ground-truth drift, hit or missed, ground_truth_drift_shift: the shift of the
reference active at the drift on [s-500, s) vs [s, s+500), the after-window truncated at the
next freeze (effective length < 100 flagged unreliable).

Then the pre-registered verdict: median |z_ref| for TP vs FP and AUC(|z_ref|, TP vs FP);
reject if AUC <= 0.6 or median_FP >= median_TP; support pattern median_FP < 1 and median_TP >= 2.

    python scripts/analyze_reference_signal.py --dir outputs/regression_fp_ref_synth
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

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_regression_fp import stream_path  # noqa: E402
from run_task_matrix import PERTURBATION, WARM_START, load_stream  # noqa: E402
from src.metrics.correct_detection import build_perturbation_intervals  # noqa: E402

TP_LABELS = {"hit"}
FP_LABELS = {"echo", "orphan"}          # scored false positives; echo_inwin reported separately
AGE_BUCKETS = [(0, 2000), (2000, 5000), (5000, 10000), (10000, 10**9)]


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else (f"{v:.3f}" if isinstance(v, float) else str(v))
                                       for v in r.values) + " |")
    return "\n".join(lines)


def era_starts(sig: pd.DataFrame, confirmations: list) -> np.ndarray:
    """Index positions where the reference (or, without one, the leader) was replaced."""
    if "ref_age" in sig.columns and sig["ref_age"].notna().any():
        return sig.loc[sig["ref_age"] == 0, "t"].to_numpy()
    return np.array(sorted(set([WARM_START] + [int(c) for c in confirmations])))


def two_window_shift(series: np.ndarray, t_idx: np.ndarray, ct: int, era_start: int):
    """(recent - previous) / sd(previous), both windows before ct inside [era_start, ct]."""
    era_len = ct - era_start + 1
    w = min(500, era_len // 2)
    if w < 50:
        return np.nan, w
    pos = np.searchsorted(t_idx, ct)
    if pos >= len(series) or t_idx[pos] != ct:
        return np.nan, w
    recent = series[pos - w + 1: pos + 1]
    prev = series[pos - 2 * w + 1: pos - w + 1]
    sd = prev.std()
    if not np.isfinite(sd) or sd <= 0 or len(prev) < w:
        return np.nan, w
    return float((recent.mean() - prev.mean()) / sd), w


def split_z(x: np.ndarray, min_side: int = 30) -> float:
    n = len(x)
    if n < 2 * min_side:
        return np.nan
    cs, cs2 = np.cumsum(x), np.cumsum(x * x)
    best = 0.0
    for k in range(min_side, n - min_side + 1):
        nl, nr = k, n - k
        ml, mr = cs[k - 1] / nl, (cs[-1] - cs[k - 1]) / nr
        vl = max(cs2[k - 1] / nl - ml * ml, 1e-12)
        vr = max((cs2[-1] - cs2[k - 1]) / nr - mr * mr, 1e-12)
        best = max(best, abs(ml - mr) / np.sqrt(vl / nl + vr / nr))
    return float(best)


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    # rank-based AUC = P(score_pos > score_neg) with ties counted half
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + 0.5 * eq) / (len(pos) * len(neg)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default="outputs/regression_fp_ref_synth")
    args = ap.parse_args()

    det = pd.read_csv(os.path.join(args.dir, "detections.csv"))
    summ = pd.read_csv(os.path.join(args.dir, "summary.csv"))
    rows, gt_rows, sw_rows = [], [], []

    for path in sorted(glob.glob(os.path.join(args.dir, "signals", "*.csv.gz"))):
        key, cfg = os.path.basename(path)[:-7].rsplit("__", 1)
        cfg = cfg.replace("_", "/")
        with gzip.open(path, "rt") as f:
            sig = pd.read_csv(f)
        drow = summ[(summ["dataset"].str.replace("/", "_").str.replace(".csv", "") == key) & (summ["config"] == cfg)]
        if drow.empty:
            continue
        ds, n_steps = drow["dataset"].iloc[0], int(drow["n_steps"].iloc[0])
        d = det[(det["dataset"] == ds) & (det["config"] == cfg)].sort_values("confirmation_t")
        _, _, intervals = load_stream(stream_path(ds), n_steps)
        starts = [s for s, _ in intervals]
        windows = build_perturbation_intervals(intervals, extension=PERTURBATION)  # the scorer's hit windows
        t_idx = sig["t"].to_numpy()
        raw = sig["raw"].to_numpy(dtype=float)
        has_ref = "ref_raw" in sig.columns and sig["ref_raw"].notna().any()
        ref_raw = sig["ref_raw"].to_numpy(dtype=float) if has_ref else None
        dval = sig["drift_value"].to_numpy(dtype=float) if "drift_value" in sig.columns else sig["err"].to_numpy(dtype=float)
        fires = sig.loc[sig["is_drift"] == 1, "t"].to_numpy()
        eras = era_starts(sig, d["confirmation_t"].tolist())

        for _, r in d.iterrows():
            ct = int(r["confirmation_t"])
            era0 = int(eras[eras <= ct].max()) if (eras <= ct).any() else WARM_START
            z_l, w = two_window_shift(raw, t_idx, ct, era0)
            z_r = two_window_shift(ref_raw, t_idx, ct, era0)[0] if has_ref else np.nan
            prev_fire = fires[fires < ct]
            lo = int(prev_fire.max()) + 1 if len(prev_fire) else WARM_START
            pos_lo, pos_hi = np.searchsorted(t_idx, lo), np.searchsorted(t_idx, ct)
            zs = split_z(dval[pos_lo: pos_hi + 1])
            age = float(sig.loc[sig["t"] == ct, "ref_age"].iloc[0]) if has_ref and (sig["t"] == ct).any() else np.nan
            rows.append({"dataset": ds, "config": cfg, "warning_t": int(r["warning_t"]), "confirmation_t": ct,
                         "label": r["label"], "window": w, "z_leader": z_l, "z_ref": z_r,
                         "ref_dir": ("rise" if z_r > 0 else "fall") if np.isfinite(z_r) else "",
                         "z_split": zs, "det_window": ct - lo + 1, "ref_age": age})

        if has_ref:
            hit_wts = d.loc[d["label"] == "hit", "warning_t"].to_numpy()
            for s, (ws, we) in zip(starts, windows):
                hit = bool(((hit_wts >= ws) & (hit_wts <= we)).any())
                p = np.searchsorted(t_idx, s)
                e0 = int(eras[eras <= s].max()) if (eras <= s).any() else WARM_START
                before = ref_raw[max(np.searchsorted(t_idx, e0), p - 500): p]
                nxt = eras[eras > s]
                stop = min(p + 500, np.searchsorted(t_idx, int(nxt.min())) if len(nxt) else p + 500)
                after = ref_raw[p: stop]
                z = ((after.mean() - before.mean()) / before.std()) if len(before) >= 100 and len(after) >= 1 and before.std() > 0 else np.nan
                gt_rows.append({"dataset": ds, "config": cfg, "gt_start": s, "hit": int(hit),
                                "before_n": len(before), "after_n": len(after),
                                "reliable": int(len(before) >= 100 and len(after) >= 100), "gt_shift_z": z})
            if "ref_switch" in sig.columns:
                for _, srow in sig[sig["ref_switch"] == 1].iterrows():
                    t0 = int(srow["t"])
                    seg = sig[(sig["t"] >= t0) & (sig["t"] < t0 + 500)]
                    both = seg.dropna(subset=["shadow_raw", "ref_raw"])
                    wage = int(srow["switch_warning_age"]) if pd.notna(srow.get("switch_warning_age")) else -1
                    gt_after = any(t0 < s <= t0 + 1000 for s in starts)
                    sw_rows.append({"dataset": ds, "config": cfg, "t": t0, "closed_warning_age": wage,
                                    "gt_within_1000_after": int(gt_after),
                                    "delta_switch_mean": float((both["ref_raw"] - both["shadow_raw"]).mean()) if len(both) else np.nan,
                                    "var_ratio_new_over_old": float(both["ref_raw"].var() / both["shadow_raw"].var()) if len(both) > 1 and both["shadow_raw"].var() > 0 else np.nan,
                                    "n": len(both)})

    ev = pd.DataFrame(rows)
    ev.to_csv(os.path.join(args.dir, "reference_events.csv"), index=False)
    print("## 1. Per-config H0/H1 statistics (TP = hit; FP = echo + orphan)\n")
    out = []
    for cfg, g in ev.groupby("config"):
        tp, fp = g[g["label"].isin(TP_LABELS)], g[g["label"].isin(FP_LABELS)]
        o = {"config": cfg, "n_tp": len(tp), "n_fp": len(fp), "n_echo_inwin": int((g["label"] == "echo_inwin").sum())}
        for space in ("z_ref", "z_leader", "z_split"):
            a, b = tp[space].abs().to_numpy(dtype=float), fp[space].abs().to_numpy(dtype=float)
            o[f"med_{space}_TP"] = float(np.nanmedian(a)) if np.isfinite(a).any() else np.nan
            o[f"med_{space}_FP"] = float(np.nanmedian(b)) if np.isfinite(b).any() else np.nan
            o[f"auc_{space}"] = auc(a, b)
        o["z_ref_nan"] = int(g["z_ref"].isna().sum())
        out.append(o)
    st = pd.DataFrame(out)
    print(md(st), "\n")

    print("## 2. Pre-registered verdict on z_ref (reference space)\n")
    for _, o in st.iterrows():
        if not np.isfinite(o["med_z_ref_TP"]):
            print(f"- {o['config']}: no reference signal (baseline arm)")
            continue
        a, mt, mf = o["auc_z_ref"], o["med_z_ref_TP"], o["med_z_ref_FP"]
        if (np.isfinite(a) and a <= 0.6) or (np.isfinite(mf) and mf >= mt):
            v = "REJECT H1 (line stops): FP shift in reference space is not separable from TP"
        elif mf < 1.0 and mt >= 2.0:
            v = "SUPPORTS H1: FP |z_ref| < 1 sd, TP |z_ref| >= 2 sd"
        else:
            v = "INCONCLUSIVE: inspect the event table before any next step"
        print(f"- {o['config']}: AUC={a:.2f}  median|z_ref| TP={mt:.2f} FP={mf:.2f}  -> {v}")
    print()

    print("## 3. Direction of the reference shift at detections\n")
    print(md(ev[ev["ref_dir"] != ""].groupby(["config", "label", "ref_dir"]).size().unstack(fill_value=0).reset_index()), "\n")

    if gt_rows:
        gt = pd.DataFrame(gt_rows)
        gt.to_csv(os.path.join(args.dir, "reference_gt_shift.csv"), index=False)
        print("## 4. ground_truth_drift_shift: every ground-truth drift, hit or missed (reference active at the drift)\n")
        g = gt[gt["reliable"] == 1].groupby(["config", "hit"]).agg(n=("gt_shift_z", "size"), med_abs_z=("gt_shift_z", lambda s: float(np.nanmedian(np.abs(s)))),
                                                                   min_abs_z=("gt_shift_z", lambda s: float(np.nanmin(np.abs(s))))).reset_index()
        print(md(g), f"\n(unreliable windows excluded: {int((gt['reliable'] == 0).sum())})\n")

    print("## 5. FP rate by reference age at the detection\n")
    ev_ref = ev[ev["ref_age"].notna()].copy()
    if len(ev_ref):
        ev_ref["bucket"] = pd.cut(ev_ref["ref_age"], [b[0] for b in AGE_BUCKETS] + [AGE_BUCKETS[-1][1]],
                                  labels=["0-2k", "2-5k", "5-10k", ">10k"], right=False)
        b = ev_ref[ev_ref["label"].isin(TP_LABELS | FP_LABELS)].groupby(["config", "bucket"], observed=True)["label"].agg(
            n="size", fp=lambda s: int(s.isin(FP_LABELS).sum())).reset_index()
        b["fp_rate"] = b["fp"] / b["n"]
        print(md(b), "\n")

    if sw_rows:
        sw = pd.DataFrame(sw_rows)
        sw.to_csv(os.path.join(args.dir, "reference_switches.csv"), index=False)
        print("## 6. Reference switches (secondary arm)\n")
        s = sw.groupby("config").agg(switches=("t", "size"), closed_warnings=("closed_warning_age", lambda a: int((a >= 0).sum())),
                                     closed_age_ge100=("closed_warning_age", lambda a: int((a >= 100).sum())),
                                     closed_then_gt=("gt_within_1000_after", "sum"),
                                     delta_switch_mean=("delta_switch_mean", "mean"),
                                     var_ratio=("var_ratio_new_over_old", "median")).reset_index()
        print(md(s), "\n")
    print("wrote", os.path.join(args.dir, "reference_events.csv"))


if __name__ == "__main__":
    main()
