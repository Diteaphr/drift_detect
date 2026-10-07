"""Step 0 (dev check, no new runs): what are E10bT's regression false alarms?

Rules fixed BEFORE reading any result (2026-10-01):
  Data   E12 SYN2g45-REG-* (primary) + D2 SYN2-REG-* (A2 g00), arm E10bT, htr + hfr; labels = FP@3000.
  V      replay the guard's drift arm (one-sided river ADWIN, delta 0.05, grace 30, on `err`) and the
         reference's drift arm (two-sided, on `ref_err`); must reproduce logged guard_drift and
         is_drift (= ref | guard) at EVERY row, else nothing is read.
  S1     share of FP whose confirmation step has a guard drift fire (guard alone or both).
  S2     among guard FPs: catch-up = raw |residual| over the kept sub-window W1 <= 1.05 x the dropped W0
         (E0's M3 rule), i.e. the normalized error rose but the raw residual did not.
  Read   A normalizer catch-up   S1 >= 0.5 and S2 >= 0.6
         B real leader rises     S1 >= 0.5 and S2 <= 0.4
         C not the guard         S1 <  0.5
         otherwise mixed (descriptive only). Pooled over both rounds; per round shown.
"""
import os
import sys

import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import diagnose_regression_fp as drf  # noqa: E402
import run_e1_e2 as h  # noqa: E402
from detectors.meta_ecpf.adwin_family import _ADWINAdapter  # noqa: E402

GRACE, DELTA = 30, 0.05
ROUNDS = (("E12", "e12", "SYN2g45-REG"), ("D2", "a2", "SYN2-REG"))


def replay(sig, conf_rows):
    """Per row: guard drift fire (+ W0/W1 widths), reference drift fire. Mirrors pipeline order:
    switch reset -> updates -> self-reset on own fire -> confirmation resets both pairs."""
    err, ref = sig["err"].to_numpy(float), sig["ref_err"].to_numpy(float)
    switch = sig["ref_switch"].fillna(0).to_numpy(bool)
    mk = lambda one: _ADWINAdapter(delta=DELTA, min_num_instances=GRACE, one_sided=one)
    g, r = mk(True), mk(False)
    gfire, rfire, cut = np.zeros(len(sig), bool), np.zeros(len(sig), bool), {}
    for i in range(len(sig)):
        if switch[i]:
            r = mk(False)
        wb = g._detector.width
        if g.update(err[i]):
            gfire[i], cut[i] = True, (wb, g._detector.width)
            g = mk(True)
        if r.update(ref[i]):
            rfire[i] = True
            r = mk(False)
        if i in conf_rows:
            g, r = mk(True), mk(False)
    return gfire, rfire, cut


def main():
    rows, bad = [], 0
    for rnd, held, prefix in ROUNDS:
        for fam, arm, path, ds, cfg, g, sig in h.iter_runs(held):
            if arm != "E10bT" or not fam.startswith(prefix):
                continue
            gt = h.scored_gt(fam, drf.load_stream(path, h.ALL[fam][1])[2])
            dets = list(zip(g["warning_t"].astype(int), g["confirmation_t"].astype(int)))
            drf.PERTURBATION = 3000
            lab = {r["confirmation_t"]: r for r in drf.classify(dets, gt, sig, [], len(sig))}
            drf.PERTURBATION = 1000
            pos = {t: i for i, t in enumerate(sig["t"].to_numpy(int))}
            conf = {pos[ct] for _, ct in dets}
            gfire, rfire, cut = replay(sig, conf)
            bad += int((gfire != sig["guard_drift"].astype(bool).to_numpy()).sum())
            bad += int(((gfire | rfire) != sig["is_drift"].astype(bool).to_numpy()).sum())
            raw, err = sig["raw"].to_numpy(float), sig["err"].to_numpy(float)
            ts = sig["t"].to_numpy(int)  # descriptive (added after the registered reading): chance coverage
            cover = np.zeros(len(ts), bool)
            for s, e in h.build_perturbation_intervals(gt, extension=3000):
                cover |= (ts >= s) & (ts <= e)
            prev = None
            for wt, ct in sorted(dets, key=lambda d: d[1]):
                i, lr = pos[ct], lab[ct]
                row = {"round": rnd, "family": fam, "learner": h.learner(cfg), "warning_t": wt, "confirmation_t": ct,
                       "label": lr["label"], "src": "both" if gfire[i] and rfire[i] else "guard" if gfire[i] else "ref",
                       "since_conf": ct - prev if prev is not None else ct, "ref_age": sig["ref_age"].iloc[i],
                       "cov": cover.mean(), "rr": raw[max(0, i - 299):i + 1].mean() / raw[max(0, i - 2299):max(1, i - 299)].mean()}
                if gfire[i]:
                    wb, wa = map(int, cut[i])
                    s0, s1 = slice(i - wb, i - wa + 1), slice(i - wa + 1, i + 1)
                    row.update(w0=wb + 1 - wa, w1=wa, raw_w0=raw[s0].mean(), raw_w1=raw[s1].mean(),
                               err_w0=err[s0].mean(), err_w1=err[s1].mean())
                rows.append(row)
                prev = ct
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "step0_guard_fp.csv"), index=False)

    print("## V  replay mismatches (guard_drift + is_drift rows) = %d" % bad)
    if bad:
        print("REPLAY INVALID -- nothing is read")
        return
    df["fp"] = df["label"].isin(h.FP)
    gd = df[df["src"] != "ref"]
    print("guard cuts with err_w1 <= err_w0 (must be 0, one-sided): %d" % int((gd["err_w1"] <= gd["err_w0"]).sum()))
    df["catch"] = df["raw_w1"] <= 1.05 * df["raw_w0"]

    print("\n## confirmations by round x label x trigger")
    print(pd.crosstab([df["round"], df["label"].where(~df["fp"], "FP")], df["src"], margins=True).to_string())
    for name, d in list(df.groupby("round")) + [("pooled", df)]:
        fp = d[d["fp"]]
        gfp = fp[fp["src"] != "ref"]
        s1 = len(gfp) / len(fp) if len(fp) else float("nan")
        s2 = gfp["catch"].mean() if len(gfp) else float("nan")
        read = ("C not the guard" if s1 < 0.5 else "A normalizer catch-up" if s2 >= 0.6
                else "B real leader rises" if s2 <= 0.4 else "mixed")
        print("\n%-6s FP=%d  guard FP=%d  S1=%.2f  catch-up=%d  S2=%.2f  -> %s%s"
              % (name, len(fp), len(gfp), s1, int(gfp["catch"].sum()), s2, read,
                 "  (THE registered reading)" if name == "pooled" else ""))

    print("\n## descriptive (added after the reading): are the catch-up-pattern guard fires chance-like?")
    print("cov = share of the stream inside a scoring window [GT start, end+3000] = hit chance of a random fire (upper bound)")
    print("rr  = raw |residual| over the last 300 steps / the 2000 before (a drift trigger shows rr > 1)")
    gf = df[df["src"] != "ref"].assign(kind=lambda d: np.where(d["catch"], "catch-up", "raw-rise"))
    for k, d in list(gf.groupby("kind")) + [("ref-only", df[df["src"] == "ref"])]:
        print("%-8s fires=%3d  hit=%3d  FP=%3d  in-window echo=%2d  chance hits<=%.1f  median rr hit %.3f / FP %.3f"
              % (k, len(d), (d["label"] == "hit").sum(), d["fp"].sum(), (d["label"] == "echo_inwin").sum(),
                 d["cov"].sum(), d.loc[d["label"] == "hit", "rr"].median(), d.loc[d["fp"], "rr"].median()))

    fp = df[df["fp"]]
    print("\n## descriptive: FP by learner x trigger")
    print(pd.crosstab(fp["learner"], fp["src"]).to_string())
    print("\n## descriptive: guard-triggered confirmations (raw rel. change W0->W1, steps since last confirmation)")
    gd = df[df["src"] != "ref"].assign(raw_rel=lambda d: d["raw_w1"] / d["raw_w0"] - 1)
    cols = ["round", "family", "learner", "confirmation_t", "label", "src", "since_conf", "ref_age",
            "w0", "w1", "raw_w0", "raw_w1", "raw_rel", "err_w0", "err_w1"]
    print(gd[cols].sort_values(["label", "round", "family"]).round(3).to_string(index=False))
    hits = df[df["label"] == "hit"]
    print("\n## hits by trigger: %s" % hits["src"].value_counts().to_dict())
    print("guard-only hits (reference silent): %d, of which catch-up pattern: %d"
          % ((hits["src"] == "guard").sum(), int(hits.loc[hits["src"] == "guard", "catch"].sum())))


if __name__ == "__main__":
    main()
