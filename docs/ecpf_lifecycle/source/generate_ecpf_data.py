"""Regenerate ../ecpf_data.js from event_interactions.csv.

`ecpf_data.js` is the data layer for index.html: a single global
`window.__ECPF_DATA` — a JSON array with one record per drift/warning event.
Each record maps directly to a CSV row, plus three derived fields:

    idx        0-based row index (used as the selector index)
    fileShort  `file` with the trailing ".csv" stripped
    isStar     True when gt_match == "TP" and reuse_looked_better == 0
               (a true drift where the *new* model looked better on the buffer)

Run:  python generate_ecpf_data.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "event_interactions.csv")
OUT = os.path.join(HERE, "..", "ecpf_data.js")

# CSV column -> JS field. `file` is dropped in favour of derived `fileShort`.
RENAME = {
    "warning_to_confirm_age": "age",
    "acc_current_on_warning": "acc_current",
    "acc_best_on_warning": "acc_best",
    "acc_new_on_warning": "acc_new",
    "file": None,
}
INT_FIELDS = {
    "warning_t", "confirmation_t", "age", "best_idx", "current_idx",
    "collection_size", "buffer_len", "reuse_looked_better", "nearest_drift_start",
    "confirmation_delay", "n_leader_swaps", "fresh_ever_led", "duel_final_margin",
    "duel_segment_len", "reuse_survived", "snapshot_matched_duel",
}
FLOAT_FIELDS = {
    "acc_current", "acc_best", "acc_new", "acc_best_minus_new",
    "prewarn_slope", "prewarn_peak", "prewarn_mean",
}


def conv(field, raw):
    raw = (raw or "").strip()
    if raw == "":
        return None  # empty prewarn_* -> null -> rendered as "—"
    if field in INT_FIELDS:
        try:
            return int(raw)
        except ValueError:
            return int(float(raw))
    if field in FLOAT_FIELDS:
        return float(raw)
    return raw


def main():
    with open(SRC, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    out = []
    for i, r in enumerate(rows):
        rec = {"idx": i}
        for col, val in r.items():
            js = RENAME.get(col, col)
            if js is None:
                continue
            rec[js] = conv(js, val)
        fn = (r.get("file") or "").strip()
        rec["fileShort"] = fn[:-4] if fn.lower().endswith(".csv") else fn
        rec["isStar"] = (rec.get("gt_match") == "TP" and rec.get("reuse_looked_better") == 0)
        out.append(rec)

    js = "window.__ECPF_DATA = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(js)

    tp = sum(1 for e in out if e["gt_match"] == "TP")
    stars = sum(1 for e in out if e["isStar"])
    print("events: %d  TP: %d  FP: %d  stars: %d  ->  %s"
          % (len(out), tp, len(out) - tp, stars, os.path.normpath(OUT)))


if __name__ == "__main__":
    main()
