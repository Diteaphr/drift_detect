"""Post-hoc, descriptive only (not registered): the 15 SYN2-REG stale misses of D1, per drift.
For each: drift type, learner, which arms hit, and under E10bFT the leader's raw residual after the drift
relative to before (after = GT start .. +1000, before = the 2000 steps before GT start), the guard's input over the
same windows, and whether the guard was idle / how old its ADWIN window was."""
import os
import sys

import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import run_e1_e2 as h  # noqa: E402

arms = ["baseT", "E2k500T", "E10bT", "E10bFT"]
df = h.rescore(exts=(3000,), show=False, held="a2")
runs = h.runs_table(held="a2")
fams = [f for f in h.A2 if f.startswith("SYN2-REG")]
runs = runs[runs["family"].isin(fams) & runs["arm"].isin(arms + ["E2k500"])]
rows = []
for (f, ds, lr), g in runs.groupby(["family", "dataset", "learner"]):
    r = {x.arm: x for x in g.itertuples()}
    iv = h.scored_gt(f, h.load_stream(r["E2k500"].path, h.ALL[f][1])[2])
    age = r["E2k500"].sig.set_index("t")["ref_age"]
    sel = df[(df["family"] == f) & (df["dataset"] == ds) & (df["learner"] == lr)]
    warn = {a: sel[sel["arm"] == a]["warn_t"].iloc[0] for a in arms + ["E2k500"]}
    sig = r["E10bFT"].sig.set_index("t")
    conf = np.array(sorted(r["E10bFT"].conf_t))
    for s, e in iv:
        hit = {a: any(s <= w <= e + 3000 for w in warn[a]) for a in arms + ["E2k500"]}
        if hit["E2k500"] or int(age.get(s, -1)) < 10000:
            continue
        b, a_ = sig.loc[s - 2000:s - 1], sig.loc[s:s + 1000]
        last = conf[conf < s].max() if (conf < s).any() else 200
        rows.append({"type": f.rsplit("-", 1)[1], "lr": lr, "gt": s, "width": e - s,
                     **{a: int(hit[a]) for a in arms},
                     "raw_ratio": a_["raw"].mean() / b["raw"].mean(),
                     "gin_before": b["guard_in"].mean(), "gin_after": a_["guard_in"].mean(),
                     "since_conf": s - last, "ref_age_FT": int(sig["ref_age"].get(s, -1))})
m = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(m.round(3).to_string(index=False))
print("\nby type:\n%s" % m.groupby("type")[arms].sum().assign(n=m.groupby("type").size()).to_string())
print("\nby learner:\n%s" % m.groupby("lr")[arms].sum().assign(n=m.groupby("lr").size()).to_string())
miss, got = m[m["E10bFT"] == 0], m[m["E10bFT"] == 1]
print("\nE10bFT missed %d: median raw_ratio %.3f (min %.3f, max %.3f) | hit %d: median raw_ratio %.3f" % (
    len(miss), miss["raw_ratio"].median(), miss["raw_ratio"].min(), miss["raw_ratio"].max(), len(got),
    got["raw_ratio"].median()))
print("of the E10bFT misses, baseT hit %d; their median raw_ratio %.3f" % (
    miss["baseT"].sum(), miss.loc[miss["baseT"] == 1, "raw_ratio"].median()))
