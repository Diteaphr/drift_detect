"""V1 (docs/ECPF_V1E9_預註冊.md): is E1's detector faithful to MOA's ADWINChangeDetector?

Offline replay of E1's logged detector input through MOA (via CapyMOA). The rebuild
schedule follows E1's LOGGED fires (both arms after a drift fire, the warning arm after
a warning fire), so both implementations see the same input and the same window starts;
any difference comes from the detectors themselves.

CapyMOA needs numpy 2.x, so this runs in an isolated venv, not the project env:
    <venv>/python scripts/verify_moa_adwin.py
"""
import glob
import os

import numpy as np
import pandas as pd
from capymoa.drift.detectors import ADWIN

FAMILIES = ["B", "MC-syn", "MC-RBF", "REG-syn", "REG-Joe"]
DELTA_W, DELTA_D, TOL = 0.1, 0.05, 32


def replay(sig: pd.DataFrame):
    err, t = sig["err"].to_numpy(float), sig["t"].to_numpy(int)
    lw, ld = sig["is_warning"].to_numpy(bool), sig["is_drift"].to_numpy(bool)
    w, d = ADWIN(delta=DELTA_W), ADWIN(delta=DELTA_D)
    moa = {"w": [], "d": []}
    meta = {"w": [], "d": []}          # (window age at the fire, steps since the previous MOA fire in this window)
    age = {"w": 0, "d": 0}
    last = {"w": None, "d": None}
    for i, x in enumerate(err):
        w.add_element(float(x))
        d.add_element(float(x))
        age["w"] += 1
        age["d"] += 1
        for arm, det in (("w", w), ("d", d)):
            if det.detected_change():
                moa[arm].append(int(t[i]))
                meta[arm].append((age[arm], None if last[arm] is None else i - last[arm]))
                last[arm] = i
        if ld[i]:
            w, d = ADWIN(delta=DELTA_W), ADWIN(delta=DELTA_D)
            age, last = {"w": 0, "d": 0}, {"w": None, "d": None}
        elif lw[i]:
            w = ADWIN(delta=DELTA_W)
            age["w"], last["w"] = 0, None
    return moa, {"w": t[lw].tolist(), "d": t[ld].tolist()}, meta


def matched(a, b):
    """How many of a have some b within TOL steps, and how many exactly."""
    b = np.asarray(b)
    near = sum(bool(len(b)) and np.min(np.abs(b - x)) <= TOL for x in a)
    exact = sum(x in set(b.tolist()) for x in a)
    return near, exact


def main() -> None:
    rows = []
    for fam in FAMILIES:
        for f in sorted(glob.glob(os.path.join("outputs", "e1_e2", fam, "E1", "signals", "*.csv.gz"))):
            moa, e1, meta = replay(pd.read_csv(f))
            for arm in ("w", "d"):
                n1, x1 = matched(e1[arm], moa[arm])
                n2, _ = matched(moa[arm], e1[arm])
                # where the MOA-only fires come from (registered: report discrepancy sources)
                b = np.asarray(e1[arm])
                early = refire = other = 0
                for tm, (a, gap) in zip(moa[arm], meta[arm]):
                    if len(b) and np.min(np.abs(b - tm)) <= TOL:
                        continue
                    if a <= 30:
                        early += 1          # river's grace_period (30) would not allow a cut yet
                    elif gap is not None and gap <= TOL:
                        refire += 1         # MOA keeps the post-cut window and cuts again
                    else:
                        other += 1
                rows.append({"family": fam, "run": os.path.basename(f), "arm": arm, "e1_fires": len(e1[arm]),
                             "moa_fires": len(moa[arm]), "e1_matched": n1, "e1_exact": x1, "moa_matched": n2,
                             "moa_only_early": early, "moa_only_refire": refire, "moa_only_other": other})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join("outputs", "e1_e2", "v1_moa_adwin.csv"), index=False)
    print("## V1: E1 detector vs MOA ADWINChangeDetector (CapyMOA), tolerance +-%d steps" % TOL)
    for arm, name in (("d", "drift arm"), ("w", "warning arm")):
        a = df[df["arm"] == arm]
        g = a.groupby("family")[["e1_fires", "moa_fires", "e1_matched", "e1_exact", "moa_matched"]].sum()
        g["e1->moa"] = (g["e1_matched"] / g["e1_fires"]).round(3)
        g["moa->e1"] = (g["moa_matched"] / g["moa_fires"]).round(3)
        g["exact"] = (g["e1_exact"] / g["e1_fires"]).round(3)
        tot = a[["e1_fires", "moa_fires", "e1_matched", "e1_exact", "moa_matched"]].sum()
        r1, r2 = tot["e1_matched"] / tot["e1_fires"], tot["moa_matched"] / tot["moa_fires"]
        print("\n%s:\n%s\npooled: e1->moa %.3f  moa->e1 %.3f  exact %.3f" % (
            name, g.to_string(), r1, r2, tot["e1_exact"] / tot["e1_fires"]))
        src = a[["moa_only_early", "moa_only_refire", "moa_only_other"]].sum()
        print("MOA-only fires by source: first 30 steps of a window %d | re-fire within %d steps %d | other %d"
              % (src["moa_only_early"], TOL, src["moa_only_refire"], src["moa_only_other"]))
        if arm == "d":
            verdict = ("FAITHFUL to MOA" if r1 >= 0.90 and r2 >= 0.90 else
                       "NOT faithful: describe E1 as 'river ADWIN core + MOA direction semantics'")
            print("V1 verdict (drift arm, both >= 0.90): %s" % verdict)


if __name__ == "__main__":
    main()
