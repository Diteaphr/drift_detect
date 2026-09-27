"""E0 -- native ADWIN cut direction behind each ECPF confirmation.

Pre-registration: docs/ECPF_E0_原生切點方向_預註冊.md (appendix A: offline replay).

In the baseline dual_adwin path every ADWIN cut fires, a drift fire rebuilds both
arms, and a warning fire makes river reset that arm on its next update -- so each
arm's window is exactly "every err since its last rebuild". Replaying river ADWIN on
the logged err reproduces both arms; the replay must match every logged fire before
anything is read.

    python scripts/analyze_native_direction.py --run   # rerun MC/binary baselines, then analyse
    python scripts/analyze_native_direction.py         # analyse only
"""
import argparse
import glob
import gzip
import json
import os
import sys

import numpy as np
import pandas as pd
from river import drift

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagnose_regression_fp import classify, dataset_key, run  # noqa: E402

OUT = "outputs/e0_native_direction"
DELTA_W, DELTA_D, GRACE = 0.1, 0.05, 30  # detector_delta_w, detector_delta, ecpf_detector_min_instances
HF10 = [("hf10sqrt/error", "hf", {"n_trees": 10, "max_features": "sqrt"}),
        ("hf10all/error", "hf", {"n_trees": 10, "max_features": None})]
RBF = [p for p in glob.glob("data/synthetic_dataset_joe/multi classification/*_drift/*/recurring_*_rbf4_100k_g00.csv")
       if "incremental" not in p]
RERUN = {  # family -> (paths, max_steps, configs): same settings as the archived campaigns
    "MC-syn": (sorted(glob.glob("data/synthetic_multiclass/mc*_20k.csv")), 20000, HF10),
    "MC-RBF": (sorted(RBF), 20000, HF10),
    "B": (["data/sudden_drift/sudden_sea100k_g00.csv", "data/gradual_drift/gradual_sea100k_g00.csv",
           "data/recurring_drift/recurring_sud_sea100k_g00.csv"], 30000,
          [("ht/error", "ht", {}), ("hf10/error", "hf", {"n_trees": 10})]),
}
ARCHIVED = [("REG-syn", "outputs/regression_fp_p3_synth", {"htr-nr/error", "hfr-nr/error"}),
            ("REG-Joe", "outputs/regression_fp_p3_joe_htr", {"htr-nr/error"}),
            ("REG-Joe", "outputs/regression_fp_p3_joe_hfr", {"hfr-nr/error"})]
FP = ("echo", "orphan")


def sig_name(dataset: str, config: str) -> str:
    return "%s__%s.csv.gz" % (dataset.replace("/", "_").replace(".csv", ""), config.replace("/", "_"))


def rerun() -> None:
    for fam, (paths, max_steps, configs) in RERUN.items():
        d = os.path.join(OUT, fam)
        os.makedirs(os.path.join(d, "signals"), exist_ok=True)
        rows = []
        for path in paths:
            key = dataset_key(path)
            for label, mt, mk in configs:
                sig, dets, swaps, stage3, intervals, _, n = run(path, mt, max_steps, mk, {})
                for r in classify(dets, intervals, sig, swaps, n):
                    s3 = stage3.get((r["warning_t"], r["confirmation_t"]), {})
                    rows.append({**r, "dataset": key, "config": label, "buffer_len": s3.get("buffer_len")})
                with gzip.open(os.path.join(d, "signals", sig_name(key, label)), "wt") as f:
                    sig[["t", "err", "raw", "is_warning", "is_drift"]].to_csv(f, index=False)
                print(fam, key, label, "detections=%d swaps=%d" % (len(dets), len(swaps)), flush=True)
        pd.DataFrame(rows).to_csv(os.path.join(d, "detections.csv"), index=False)


def replay(sig: pd.DataFrame, col: str = "err"):
    """Replay both arms (+ an M1 shadow warning arm with clock=1) on the logged detector input.

    col="ref_err" replays the frozen-reference arms (E2/E6): a reference switch rebuilds
    both arms before that step's update (`_switch_reference` runs before `update_values`).
    """
    err, ts = sig[col].to_numpy(float), sig["t"].to_numpy(int)
    lw, ld = sig["is_warning"].to_numpy(bool), sig["is_drift"].to_numpy(bool)
    switch = sig["ref_switch"].fillna(0).to_numpy(bool) if "ref_switch" in sig else np.zeros(len(sig), bool)
    mk = lambda delta, clock=32: drift.ADWIN(delta=delta, grace_period=GRACE, clock=clock)
    arms, start = {"w": mk(DELTA_W), "d": mk(DELTA_D)}, {"w": 0, "d": 0}
    shadow, shadow_first = mk(DELTA_W, 1), None
    fires, shadow_at, bad_fire, bad_width = {}, {}, 0, 0
    for i, x in enumerate(err):
        if switch[i]:
            arms, start = {"w": mk(DELTA_W), "d": mk(DELTA_D)}, {"w": i, "d": i}
            shadow, shadow_first = mk(DELTA_W, 1), None
        fired = {}
        for a, det in arms.items():
            eb, wb = det.estimation, det.width
            det.update(x)
            if det.drift_detected:
                fired[a] = (eb, det.estimation, wb, det.width, start[a])
                bad_width += int(wb != i - start[a])  # window == everything since the last rebuild
        shadow.update(x)
        if shadow.drift_detected and shadow_first is None:
            shadow_first = int(ts[i])
        bad_fire += int(("w" in fired) != lw[i]) + int(("d" in fired) != ld[i])
        if fired:
            fires[int(ts[i])] = fired
        if "w" in fired:  # river resets the warning arm on its next update
            shadow_at[int(ts[i])] = shadow_first
            start["w"] = i + 1
        if "d" in fired:  # update_values rebuilds both arms
            arms, start = {"w": mk(DELTA_W), "d": mk(DELTA_D)}, {"w": i + 1, "d": i + 1}
        if fired:
            shadow, shadow_first = mk(DELTA_W, 1), None
    return fires, shadow_at, bad_fire, bad_width


def direction(rec) -> str:
    return "inc" if rec[1] > rec[0] else "dec"  # MOA: change only if the estimate rose


def analyse_run(fam: str, sig: pd.DataFrame, dets: pd.DataFrame, col: str = "err"):
    fires, shadow_at, bad_fire, bad_width = replay(sig, col)
    pos = {t: i for i, t in enumerate(sig["t"].to_numpy(int))}
    raw = sig["raw"].to_numpy(float)
    confirmed = set(dets["confirmation_t"].astype(int))
    rows = []
    for r in dets.sort_values("confirmation_t").itertuples():
        ct, wt = int(r.confirmation_t), int(r.warning_t)
        fd, fw = fires.get(ct, {}).get("d"), fires.get(wt, {}).get("w")
        row = {"family": fam, "dataset": r.dataset, "config": r.config, "warning_t": wt,
               "confirmation_t": ct, "label": r.label, "lead": ct - wt,
               "d_dir": direction(fd) if fd else "missing", "w_dir": direction(fw) if fw else "missing",
               "install_ratio": getattr(r, "install_ratio", np.nan),
               "gap_prev_gt": getattr(r, "gap_prev_gt", np.nan)}
        if fd:  # M3: raw |residual| over the dropped (W0) and kept (W1) sub-windows
            i, wa, s = pos[ct], int(fd[3]), fd[4]
            w0, w1 = raw[s:i - wa + 1], raw[i - wa + 1:i + 1]
            row.update(raw_w0=w0.mean() if len(w0) else np.nan, raw_w1=w1.mean())
        if row["lead"] == 0:  # M1: how early a clock=1 warning arm would have fired
            sf = shadow_at.get(ct)
            row["shadow_lead"] = ct - sf if sf is not None else 0
        rows.append(row)
    dropped = [direction(f["d"]) for t, f in fires.items() if "d" in f and t not in confirmed]
    return rows, dropped, bad_fire, bad_width, len(sig)


def load_all():
    """Yield (family, signals, detections) for every run in the E0 matrix."""
    for fam, d, configs in ARCHIVED:
        det = pd.read_csv(os.path.join(d, "detections_labelled.csv"))
        for (ds, cfg), g in det[det["config"].isin(configs)].groupby(["dataset", "config"]):
            yield fam, pd.read_csv(os.path.join(d, "signals", sig_name(ds, cfg))), g
    for fam in RERUN:
        det = pd.read_csv(os.path.join(OUT, fam, "detections.csv"))
        for (ds, cfg), g in det.groupby(["dataset", "config"]):
            yield fam, pd.read_csv(os.path.join(OUT, fam, "signals", sig_name(ds, cfg))), g


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="rerun the MC/binary baselines first")
    args = ap.parse_args()
    if args.run:
        rerun()

    rows, dropped, steps, bad_fire, bad_width = [], {}, {}, 0, 0
    for fam, sig, dets in load_all():
        r, dr, bf, bw, n = analyse_run(fam, sig, dets)
        rows += r
        dropped.setdefault(fam, []).extend(dr)
        steps[fam] = steps.get(fam, 0) + n
        bad_fire, bad_width = bad_fire + bf, bad_width + bw
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "confirmations.csv"), index=False)

    # ---- validity: the replay must reproduce every logged fire before anything is read
    missing = int((df["d_dir"] == "missing").sum() + (df["w_dir"] == "missing").sum())
    print("## Validity\nfire mismatches=%d  width mismatches=%d  unlinked confirmations=%d"
          % (bad_fire, bad_width, missing))
    if bad_fire or bad_width or missing:
        print("REPLAY INVALID -- no result is read (prereg §三 / appendix A).")
        return

    fp, tp = df[df["label"].isin(FP)], df[df["label"] == "hit"]
    print("\n## T1  family x label x native direction (drift arm at confirmation)")
    print(pd.crosstab([df["family"], df["label"]], df["d_dir"]).to_string())

    # ---- D1
    fam = fp.groupby("family")["d_dir"].agg(n="size", p_dec=lambda s: (s == "dec").mean())
    pooled = float((fp["d_dir"] == "dec").mean()) if len(fp) else float("nan")
    low = fam[(fam["n"] >= 10) & (fam["p_dec"] < 0.50)]
    d1 = ("NO-GO" if not pooled >= 0.60 else "PARTIAL GO (predicted ineffective: %s)" % ", ".join(low.index)
          if len(low) else "GO")
    print("\n## D1  p_dec(FP)\n%s\npooled=%.3f (n=%d)  ->  %s" % (fam.round(3).to_string(), pooled, len(fp), d1))

    # ---- D2
    tpd = tp.groupby("family")["d_dir"].agg(n="size", tp_dec=lambda s: int((s == "dec").sum()))
    n_dec = int(tpd["tp_dec"].sum())
    same_round = n_dec >= max(2, 0.10 * len(tp)) or bool((tpd["tp_dec"] >= 2).any())
    print("\n## D2  decrease-triggered hits\n%s\npooled TP_dec=%d of %d  ->  E2 %s"
          % (tpd.to_string(), n_dec, len(tp), "SAME ROUND as E1" if same_round else "after E1"))
    print("E1 TP-loss allowance per family: %s"
          % json.dumps({f: max(1, int(v)) for f, v in tpd["tp_dec"].items()}))
    print("decrease-triggered hits (audit list, no decision weight):")
    print(tp[tp["d_dir"] == "dec"][["family", "dataset", "config", "warning_t", "confirmation_t"]].to_string(index=False))

    # ---- M1: lead / shadow
    m1 = df[df["lead"] == 0]
    if len(m1):
        share = float((m1["shadow_lead"] >= 16).mean())
        print("\n## M1  lead=0 confirmations: %d of %d; shadow_lead>=16 in %.2f  ->  %s"
              % (len(m1), len(df), share, "clock=1 warning diagnostic SCHEDULED" if share >= 0.50
                 else "threshold-bound, report item 8 dropped"))
        print(m1.groupby("family")["shadow_lead"].describe()[["count", "50%", "max"]].to_string())

    # ---- M2: cascade candidates (regression)
    reg = df[df["family"].str.startswith("REG")].sort_values(["dataset", "config", "confirmation_t"])
    prev = reg.groupby(["dataset", "config"])
    reg = reg.assign(prev_ratio=prev["install_ratio"].shift(), prev_wt=prev["warning_t"].shift())
    prev_gt = reg["warning_t"] - reg["gap_prev_gt"]
    cand = reg[reg["label"].isin(FP) & (reg["prev_ratio"] > 1.5)
               & (prev_gt.isna() | (prev_gt <= reg["prev_wt"]))]
    if len(cand) >= 8:
        p = float((cand["d_dir"] == "dec").mean())
        verdict = "E3 stays conditional on post-E1 residual" if p >= 0.50 else "E3 SCHEDULED after E1 unconditionally"
        print("\n## M2  cascade-candidate FPs: n=%d, dec share=%.2f  ->  %s" % (len(cand), p, verdict))
    else:
        print("\n## M2  cascade-candidate FPs: n=%d (<8, descriptive only)" % len(cand))

    # ---- M3: normalizer catch-up among regression rise-FPs
    rise = reg[reg["label"].isin(FP) & (reg["d_dir"] == "inc")]
    catch = rise[rise["raw_w1"] <= 1.05 * rise["raw_w0"]]
    hit3 = len(catch) >= 5 and len(rise) and len(catch) / len(rise) >= 0.30
    print("\n## M3  regression rise-FPs=%d, raw-flat-or-falling=%d  ->  %s"
          % (len(rise), len(catch), "E2 H1 target set = these events" if hit3 else "no special H1 set"))
    catch.to_csv(os.path.join(OUT, "m3_catchup_events.csv"), index=False)

    # ---- M4: training paused under decrease-opened warnings; M5: dropped drift fires
    print("\n## M4 / M5")
    for f in sorted(df["family"].unique()):
        g = df[df["family"] == f]
        pause = int(g.loc[g["w_dir"] == "dec", "lead"].sum())
        share = pause / steps[f]
        wdec = float((g["w_dir"] == "dec").mean())
        dr = dropped.get(f, [])
        print("%-8s warnings opened by a decrease=%.2f  paused steps=%d (%.1f%% of stream)%s  |  "
              "dropped drift fires=%d (dec %.2f)" % (
                  f, wdec, pause, 100 * share, "  -> E1 secondary: accuracy/MAE should IMPROVE" if share >= 0.05 else "",
                  len(dr), (np.array(dr) == "dec").mean() if dr else float("nan")))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    main()
