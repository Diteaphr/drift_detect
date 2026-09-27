"""Per-detection diagnosis of regression-side false positives.

Mirrors the multi-class per-drift analysis (five-experiment series, exp. 4 + 6
post-script) on the regression streams: every detection is laid against ground
truth and classified as a HIT (first detection inside a scored window), an ECHO
(false positive shortly after a hit -- the new leader settling) or an ORPHAN
(mid-concept false positive). For each one we record what the error stream was
doing (fall / rise / flat, before vs after), whether a duel leader-swap happened
just before it, and -- regression-specific -- whether the RAW residual agrees
with the NORMALIZED one, because the online normalizer (``ErrorNormalizer``,
global Welford mean/sd, never reset) can make a flat raw error look like a slow
decline after the residual scale has been inflated by a drift.

Nothing in the pipeline is changed: the observer-only ``StageTracer`` supplies
the per-step signal, and leader swaps are read from ``ECPFMetaLearner``
counters between steps.

Usage
-----
    python scripts/diagnose_regression_fp.py --max-steps 4000 --only synthetic   # smoke
    python scripts/diagnose_regression_fp.py                                      # full
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import sys
import time
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_task_matrix import (  # noqa: E402
    PERTURBATION, WARM_START, _ls, dataset_key, load_stream, path_facets,
)
from src.config import PipelineConfig  # noqa: E402
from src.metrics.correct_detection import (  # noqa: E402
    build_perturbation_intervals, compute_correct_detection,
)
from src.pipeline import ConceptDriftPipeline  # noqa: E402

# Same two error-signal configs the regression rows of the task matrix used
# (hfr = 5 trees, max_features="sqrt" -- the masked default; htr = the
# unmasked single tree that had the better MAE and 2-3x the false positives).
# (label, model_type, model_kwargs, pipeline_kwargs)
CONFIGS = [("htr/error", "htr", {}, {}), ("hfr/error", "hfr", {}, {}),
           # unmasked forest: separates "ensemble vs single tree" from "masked vs unmasked"
           ("hfr-all/error", "hfr", {"max_features": None}, {}),
           # prescription #2: hold the confirmation until the warning buffer has 50 instances
           ("htr-mwa50/error", "htr", {}, {"ecpf_min_warning_age": 50}),
           ("hfr-mwa50/error", "hfr", {}, {"ecpf_min_warning_age": 50}),
           # prescription #3: re-baseline the residual normalizer at every confirmation
           ("htr-nr/error", "htr", {}, {"ecpf_normalizer_reset_on_drift": True}),
           ("hfr-nr/error", "hfr", {}, {"ecpf_normalizer_reset_on_drift": True}),
           # frozen reference (docs_myself/凍結參照模型_問題報告.md §7.2): the matched
           # baseline is *-nr (prescription 3 on in every arm).  -ref = k=0 primary arm,
           # -ref500 = k=500 secondary (maturation) arm.
           ("htr-ref/error", "htr", {}, {"ecpf_reference_signal": True, "ecpf_normalizer_reset_on_drift": True}),
           ("htr-ref500/error", "htr", {}, {"ecpf_reference_signal": True, "ecpf_reference_warmup": 500,
                                            "ecpf_normalizer_reset_on_drift": True}),
           ("hfr-ref/error", "hfr", {}, {"ecpf_reference_signal": True, "ecpf_normalizer_reset_on_drift": True})]

ECHO_GAP = 3000   # FP within this many steps after a HIT's ground-truth start = echo
LOCAL = 500       # steps before warning / after confirmation for the local error stats
SWAP_NEAR = 600   # a detection <= this many steps after a leader swap "coincides" with it
FLAT = 0.02       # |after - before| below this on the normalized error = flat


def discover(only: str, per_cell: int, joe_gradual: bool) -> List[str]:
    paths: List[str] = []
    if only in ("all", "synthetic"):
        paths += sorted(_ls("data/synthetic_regression"))
    if only in ("all", "joe"):
        kinds = ["sudden_drift"] + (["gradual_drift"] if joe_gradual else [])
        for kind in kinds:
            for tier in ("low", "medium", "high"):
                folder = os.path.join("data/synthetic_dataset_joe/regression", kind, tier)
                paths += sorted(_ls(folder))[:per_cell]
    return [p for p in paths if os.path.exists(p)]


# ---------------------------------------------------------------------------
def run(csv_path: str, model_type: str, max_steps: int, model_kwargs: Optional[Dict[str, Any]] = None,
        pipe_kwargs: Optional[Dict[str, Any]] = None):
    """One pipeline run -> (signals DataFrame, detections, swap steps, stage3 per event)."""
    X, y, intervals = load_stream(csv_path, max_steps)
    cfg = PipelineConfig(
        model_type=model_type, model_kwargs=dict(model_kwargs or {}),
        use_ecpf=True, ecpf_signal_mode="dual_adwin",
        ecpf_warning_signal="error", ecpf_drift_signal="error",
        ecpf_detector_min_instances=30, trace_enabled=True,
        **(pipe_kwargs or {}),
    )
    pipe = ConceptDriftPipeline(cfg)
    dets: List[Tuple[int, int]] = []      # (warning_t = scored timestamp, confirmation_t)
    swaps: List[int] = []
    prev_swaps = 0
    y_pred_all = np.full(len(y), np.nan)
    for i, _yt, yp, new_dets, _ in pipe.run_stream(X, y, warm_start_samples=WARM_START):
        y_pred_all[i] = yp
        for d in new_dets:
            dets.append((int(d.timestamp), int(i)))
        if pipe._ecpf is not None and pipe._ecpf.leader_swaps > prev_swaps:
            swaps.append(int(i))
            prev_swaps = pipe._ecpf.leader_swaps
    sig = pd.DataFrame(pipe.tracer._signals)
    sig["raw"] = (sig["y_true"] - sig["y_pred"]).abs()
    stage3 = {(e["warning_t"], e["confirmation_t"]): e["stage3"] for e in pipe.tracer._events}
    mae = float(np.nanmean(np.abs(y - y_pred_all)[WARM_START:]))
    return sig, dets, swaps, stage3, intervals, mae, len(y)


def _mean(s: pd.Series, lo: int, hi: int, col: str) -> float:
    v = s.loc[(s["t"] >= lo) & (s["t"] < hi), col]
    return float(v.mean()) if len(v) else float("nan")


def classify(dets, intervals, sig, swaps, n):
    """Label each detection; returns rows (dicts) in stream order."""
    windows = build_perturbation_intervals(intervals, extension=PERTURBATION)
    starts = [s for s, _ in intervals]
    claimed: set = set()
    hit_for_gt: Dict[int, int] = {}       # gt start -> warning_t of its hit
    rows = []
    prev_wt: Optional[int] = None
    for wt, ct in sorted(dets):
        win = next((k for k, (s, e) in enumerate(windows) if s <= wt <= e), None)
        prev_gt = max((s for s in starts if s <= wt), default=None)
        next_gt = min((s for s in starts if s > wt), default=None)
        if win is not None and win not in claimed:
            claimed.add(win)
            hit_for_gt[starts[win]] = wt
            label = "hit"
        elif win is not None:
            label = "echo_inwin"       # extra confirmation inside a scored window (not an FP)
        elif prev_gt is not None and prev_gt in hit_for_gt and wt - prev_gt <= ECHO_GAP:
            label = "echo"
        else:
            label = "orphan"
        # local error behaviour: LOCAL steps before the warning vs after confirmation
        nb, na = _mean(sig, wt - LOCAL, wt, "err"), _mean(sig, ct, ct + LOCAL, "err")
        rb, ra = _mean(sig, wt - LOCAL, wt, "raw"), _mean(sig, ct, ct + LOCAL, "raw")
        d_norm = na - nb
        direction = "flat" if abs(d_norm) < FLAT else ("fall" if d_norm < 0 else "rise")
        raw_rel = (ra - rb) / rb if rb and rb == rb else float("nan")
        last_swap = max((s for s in swaps if s <= wt), default=None)
        rows.append({
            "warning_t": wt, "confirmation_t": ct, "confirm_age": ct - wt, "label": label,
            "gap_prev_gt": (wt - prev_gt) if prev_gt is not None else "",
            "gap_next_gt": (next_gt - wt) if next_gt is not None else "",
            "gap_prev_det": (wt - prev_wt) if prev_wt is not None else "",
            "norm_before": round(nb, 4), "norm_after": round(na, 4), "norm_delta": round(d_norm, 4),
            "direction": direction,
            "raw_before": round(rb, 4), "raw_after": round(ra, 4), "raw_rel_change": round(raw_rel, 4),
            # normalizer artefacts, both directions: the normalized error falls
            # while raw MAE does not (fake decline), or raw MAE falls >5% while
            # the normalized reading stays flat (masked improvement)
            "discord": ("fake_fall" if direction == "fall" and raw_rel > -0.05 else
                        "masked_fall" if direction == "flat" and raw_rel < -0.05 else ""),
            "swap_gap": (wt - last_swap) if last_swap is not None else "",
            "swap_within": int(last_swap is not None and wt - last_swap <= SWAP_NEAR),
        })
        prev_wt = wt
    return rows


def swap_baseline(swaps: List[int], n: int) -> float:
    """Fraction of the stream lying within SWAP_NEAR steps after some swap."""
    covered = np.zeros(n, dtype=bool)
    for s in swaps:
        covered[s:min(n, s + SWAP_NEAR + 1)] = True
    return float(covered[WARM_START:].mean()) if n > WARM_START else 0.0


def segment_levels(sig: pd.DataFrame, intervals, n: int) -> List[Dict[str, float]]:
    """Normalized vs raw error level per concept segment (between ground-truth starts),
    skipping the first 1500 steps of each segment so the adaptation ramp is excluded."""
    edges = [WARM_START] + [s for s, _ in intervals] + [n]
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        lo = a + 1500
        if b - lo < 500:
            continue
        out.append({"seg_start": a, "seg_end": b,
                    "norm": _mean(sig, lo, b, "err"), "raw": _mean(sig, lo, b, "raw")})
    return out


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", default="outputs/regression_fp_diagnosis")
    ap.add_argument("--max-steps", type=int, default=0, help="0 = whole stream")
    ap.add_argument("--only", choices=["all", "synthetic", "joe"], default="all")
    ap.add_argument("--per-cell", type=int, default=2)
    ap.add_argument("--joe-gradual", action="store_true", help="also run Joe's gradual cells")
    ap.add_argument("--configs", default="", help="comma-separated config labels to run (default: all)")
    args = ap.parse_args()
    configs = [c for c in CONFIGS if not args.configs or c[0] in args.configs.split(",")]

    os.makedirs(os.path.join(args.out_dir, "signals"), exist_ok=True)
    det_csv = os.path.join(args.out_dir, "detections.csv")
    sum_csv = os.path.join(args.out_dir, "summary.csv")
    seg_csv = os.path.join(args.out_dir, "segment_levels.csv")
    for p in (det_csv, sum_csv, seg_csv):
        if os.path.exists(p):
            os.remove(p)

    paths = discover(args.only, args.per_cell, args.joe_gradual)
    print("%d streams x %d configs\n" % (len(paths), len(configs)))
    for path in paths:
        key = dataset_key(path)
        for label, mt, mk, pk in configs:
            t0 = time.time()
            sig, dets, swaps, stage3, intervals, mae, n = run(path, mt, args.max_steps, mk, pk)
            rows = classify(dets, intervals, sig, swaps, n)
            scored = build_perturbation_intervals(intervals, extension=PERTURBATION)
            cd = compute_correct_detection([wt for wt, _ in dets], scored) if scored else None
            for r in rows:
                r.update({"dataset": key, "config": label,
                          "stage3": json.dumps(stage3.get((r["warning_t"], r["confirmation_t"]), {}),
                                               default=str)[:400]})
            counts = {k: sum(r["label"] == k for r in rows) for k in ("hit", "echo_inwin", "echo", "orphan")}
            # drift-ADWIN fires that produced no detection (no warning open) -- the pairing loss
            confirmed = {ct for _, ct in dets}
            dropped = int(((sig["is_drift"] == 1) & ~sig["t"].isin(confirmed)).sum())
            summary = {
                "dataset": key, "config": label, "n_steps": n, "n_gt": len(intervals),
                "n_det": len(dets), "tp": cd.tp if cd else "", "fp": cd.fp if cd else "",
                "cd": round(cd.score_percent, 1) if cd and cd.score_percent is not None else "",
                **counts, "dropped_confirms": dropped, "n_swaps": len(swaps),
                "swap_baseline": round(swap_baseline(swaps, n), 3),
                "mae": round(mae, 4), "secs": round(time.time() - t0, 1),
            }
            segs = [{"dataset": key, "config": label, **s} for s in segment_levels(sig, intervals, n)]
            for p, data in ((det_csv, rows), (sum_csv, [summary]), (seg_csv, segs)):
                if not data:
                    continue
                new = not os.path.exists(p)
                with open(p, "a", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                    if new:
                        w.writeheader()
                    w.writerows(data)
            with gzip.open(os.path.join(args.out_dir, "signals", "%s__%s.csv.gz" % (
                    key.replace("/", "_").replace(".csv", ""), label.replace("/", "_"))), "wt") as f:
                cols = ["t", "err", "raw", "is_warning", "is_drift", "drift_value",
                        "ref_err", "ref_raw", "ref_age", "shadow_raw", "ref_switch", "switch_warning_age"]
                sig[[c for c in cols if c in sig.columns]].to_csv(f, index=False)
            # timeline, like the multi-class report
            print("%s  %s  gt=%s  swaps=%d  MAE=%.3f  (%.0fs)" % (
                key, label, [s for s, _ in intervals], len(swaps), mae, summary["secs"]))
            print("   tp=%s fp=%s cd=%s | %s | dropped=%d" % (
                summary["tp"], summary["fp"], summary["cd"],
                " ".join("%s=%d" % kv for kv in counts.items()), dropped))
            for r in rows:
                print("   %6d..%-6d %-10s norm %.3f->%.3f (%s)  raw %.2f->%.2f  swap_gap=%s" % (
                    r["warning_t"], r["confirmation_t"], r["label"], r["norm_before"],
                    r["norm_after"], r["direction"], r["raw_before"], r["raw_after"], r["swap_gap"]))
            print()
    print("wrote", det_csv, sum_csv, seg_csv)


if __name__ == "__main__":
    main()
