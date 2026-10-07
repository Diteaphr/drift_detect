# Post-hoc: rebuild the warning-open state (training paused) from each trace and report long pauses.
# Rules: a ref switch closes an open warning first, then the timeout (arms with one) closes a warning older
# than it; a warning fire opens one; a drift fire while open confirms it. The original helper (ins_pause.py,
# the A1 INSECTS diagnosis) was not kept; rebuild() below was rewritten from these rules on 2026-10-07 (the
# timeout is new: the "T" arms did not exist when this first ran) and is checked against detections.csv in
# every run it reads. Run from the repo root.
import sys

sys.path.insert(0, "scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import run_e1_e2 as r  # noqa: E402


def rebuild(sig, timeout=0):
    """(paused mask per row, [(warning_t, confirmation_t)], warning_t still open at the end or None)."""
    t = sig["t"].to_numpy(int)
    warn, drift = sig["is_warning"].to_numpy(bool), sig["is_drift"].to_numpy(bool)
    switch = sig["ref_switch"].fillna(0).to_numpy(bool) if "ref_switch" in sig else np.zeros(len(sig), bool)
    paused, conf, start = np.zeros(len(sig), bool), [], None
    for i in range(len(sig)):
        if switch[i] or (timeout and start is not None and t[i] - start > timeout):
            start = None
        if warn[i] and start is None:
            start = int(t[i])
        if start is not None:
            paused[i] = True
            if drift[i]:
                conf.append((start, int(t[i])))
                start = None
    return paused, conf, start


rows = []
for held in ("a2", "e10"):
    for fam, arm, path, ds, cfg, g, sig in r.iter_runs(held):
        paused, conf, open_end = rebuild(sig, r.ARMS.get(arm, {}).get("ecpf_detector_warning_timeout", 0))
        stored = list(zip(g["warning_t"].astype(int), g["confirmation_t"].astype(int)))
        runs_ = np.diff(np.concatenate([[0], paused.astype(int), [0]]))
        s_idx, e_idx = np.where(runs_ == 1)[0], np.where(runs_ == -1)[0]
        longest = int((e_idx - s_idx).max()) if len(s_idx) else 0
        rows.append({"round": held, "group": fam.rsplit("-", 1)[0], "arm": arm, "run": "%s %s" % (
            ds.split("/")[-1][:-4], r.learner(cfg)), "paused_pct": 100 * paused.mean(), "longest": longest,
            "open_at_end": open_end is not None, "rebuilt_ok": conf == stored})
t = pd.DataFrame(rows)
print("rebuild matches stored detections in %d / %d runs" % (t["rebuilt_ok"].sum(), len(t)))
print("\nshare of steps with training paused (mean over runs) and longest single pause, by round/group/arm:")
print(t.groupby(["round", "group", "arm"], sort=False).agg(paused_pct=("paused_pct", "mean"),
                                                         longest=("longest", "max"),
                                                         open_at_end=("open_at_end", "sum")).round(1).to_string())
print("\nruns with a pause >= 10000 steps:")
print(t[t["longest"] >= 10000].sort_values("longest", ascending=False).round(1).to_string(index=False))
