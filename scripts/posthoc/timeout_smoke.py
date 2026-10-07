# E11 gate: the dev run with the longest stuck warning (E10 SYN2g01-B-grad, ht, E2-k500: 50,881 steps)
# rerun with the 1000-step timeout must confirm nothing later than 1001 steps after its warning opened.
import sys

sys.path.insert(0, "scripts")
import run_e1_e2 as r  # noqa: E402

path = r.E10["SYN2g01-B-grad"][0][0]
for arm in ("E2k500", "E2k500T"):
    sig, dets, *_ = r.run(path, "ht", 0, {}, dict(r.ARMS[arm]))
    ages = [c - w for w, c in dets]
    print(arm, "confirmations", len(dets), "longest warning->confirmation", max(ages, default=0))
assert max(ages, default=0) <= 1001, "timeout gate FAILED"
print("timeout gate passed")
