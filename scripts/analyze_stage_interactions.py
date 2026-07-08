"""Join ECPF stage traces and visualise stage interactions (minimal version).

Reads the per-(config, file) traces produced by
``run_ecpf_final_selection.py --trace events`` and produces, per run:

* ``analysis/event_interactions.csv`` -- one row per drift event, joining
  stage-2 (detection timing) + stage-3 (concept profiling) + ground-truth
  alignment + simple stage-1 signal features (pre-warning slope/peak).
* ``analysis/timeline_<config>_<file>.png`` -- signal timeline with warning /
  confirmation markers and ground-truth drift intervals (skipped if matplotlib
  is unavailable).

Stage 4 (post-drift duel) is joined in as well: each event row carries the
duel outcome (``n_leader_swaps``, ``reuse_survived``, ``snapshot_matched_duel``).

See ``docs/READ_FIRST_stage_trace_experiment_zh.md`` for the full reproduction
guide (how to generate the traces this script consumes).

Usage::

    python scripts/analyze_stage_interactions.py --run-dir outputs/stage_trace_recurring
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    MATPLOTLIB_OK = True
except Exception:  # pragma: no cover - plotting is optional
    MATPLOTLIB_OK = False


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _read_stage1(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _gt_alignment(
    confirmation_t: int,
    warning_t: int,
    drift_intervals: List[List[int]],
    drift_starts: List[int],
    extension: int,
) -> Dict[str, Any]:
    """Classify an event vs ground truth.

    TP if the event span ``[warning_t, confirmation_t]`` overlaps a drift interval
    (extended by ``extension``). Overlap — not endpoint proximity — is required
    because warning->confirm spans can be long and straddle a 1-sample interval.
    """
    is_tp = False
    for s, e in drift_intervals:
        if warning_t <= (e + extension) and confirmation_t >= (s - extension):
            is_tp = True
            break
    nearest_start: Optional[int] = None
    delay: Optional[int] = None
    if drift_starts:
        nearest_start = min(drift_starts, key=lambda t: abs(confirmation_t - t))
        delay = confirmation_t - nearest_start
    return {
        "gt_match": "TP" if is_tp else "FP",
        "nearest_drift_start": nearest_start,
        "confirmation_delay": delay,
    }


def _prewarning_features(
    signals: List[Dict[str, Any]], warning_t: int
) -> Dict[str, Any]:
    """Slope / peak / mean of the warning signal in the run-up to the warning."""
    xs: List[float] = []
    ys: List[float] = []
    for row in signals:
        t = int(row["t"])
        if t > warning_t:
            continue
        val = row.get("warning_value")
        if val in (None, ""):
            continue
        try:
            ys.append(float(val))
            xs.append(float(t))
        except ValueError:
            continue
    if not ys:
        return {"prewarn_slope": None, "prewarn_peak": None, "prewarn_mean": None}
    slope = None
    if len(ys) >= 2:
        slope = float(np.polyfit(np.asarray(xs), np.asarray(ys), 1)[0])
    return {
        "prewarn_slope": slope,
        "prewarn_peak": float(np.max(ys)),
        "prewarn_mean": float(np.mean(ys)),
    }


def _to_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _plot_timeline(
    out_path: Path,
    config_id: str,
    file: str,
    signals: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    drift_intervals: List[List[int]],
) -> bool:
    if not MATPLOTLIB_OK or not signals:
        return False
    t = np.asarray([int(r["t"]) for r in signals], dtype=float)
    warn = np.asarray([_to_float(r.get("warning_value")) or np.nan for r in signals])
    err = np.asarray([_to_float(r.get("err")) or np.nan for r in signals])

    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.plot(t, warn, lw=0.8, color="#2b6cb0", label="warning_value (stage 1)")
    ax.plot(t, err, lw=0.6, color="#a0aec0", alpha=0.7, label="err")

    for s, e in drift_intervals:
        ax.axvspan(s, e, color="#f6e05e", alpha=0.25)
    for ev in events:
        ax.axvline(ev["warning_t"], color="#dd6b20", ls="--", lw=0.9)
        ax.axvline(ev["confirmation_t"], color="#e53e3e", ls="-", lw=0.9)

    ax.set_title(f"{config_id} :: {file}  (orange=warning, red=confirmation, yellow=GT drift)")
    ax.set_xlabel("t")
    ax.set_ylabel("signal")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return True


def analyze_run(run_dir: Path, extension: int = 0) -> None:
    traces_root = run_dir / "traces"
    if not traces_root.exists():
        raise SystemExit(f"No traces/ under {run_dir}. Run with --trace events first.")

    analysis_dir = run_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    interaction_rows: List[Dict[str, Any]] = []
    n_plots = 0

    for config_dir in sorted(p for p in traces_root.iterdir() if p.is_dir()):
        for file_dir in sorted(p for p in config_dir.iterdir() if p.is_dir()):
            meta_path = file_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            drift_intervals = meta.get("drift_intervals", [])
            drift_starts = meta.get("drift_starts", [])

            stage2 = {r["event_id"]: r for r in _read_jsonl(file_dir / "stage2_detection.jsonl")}
            stage3 = {r["event_id"]: r for r in _read_jsonl(file_dir / "stage3_profiling.jsonl")}
            stage4 = {r["event_id"]: r for r in _read_jsonl(file_dir / "stage4_duel.jsonl")}
            signals = _read_stage1(file_dir / "stage1_signals.csv")
            signals_by_event: Dict[str, List[Dict[str, Any]]] = {}
            for row in signals:
                signals_by_event.setdefault(row.get("event_id", ""), []).append(row)

            events_for_plot: List[Dict[str, Any]] = []
            for event_id, s2 in stage2.items():
                s3 = stage3.get(event_id, {})
                warning_t = int(s2["warning_t"])
                confirmation_t = int(s2["confirmation_t"])
                events_for_plot.append(
                    {"warning_t": warning_t, "confirmation_t": confirmation_t}
                )
                row: Dict[str, Any] = {
                    "event_id": event_id,
                    "config_id": s2.get("config_id"),
                    "file": s2.get("file"),
                    "warning_t": warning_t,
                    "confirmation_t": confirmation_t,
                    "warning_to_confirm_age": s2.get("warning_to_confirm_age"),
                    "source": s2.get("source"),
                    # stage 3 (concept profiling)
                    "best_idx": s3.get("best_idx"),
                    "current_idx": s3.get("current_idx"),
                    "collection_size": s3.get("collection_size"),
                    "acc_current_on_warning": s3.get("acc_current_on_warning"),
                    "acc_best_on_warning": s3.get("acc_best_on_warning"),
                    "acc_new_on_warning": s3.get("acc_new_on_warning"),
                    "buffer_len": s3.get("buffer_len"),
                }
                # Interaction: at on_drift, did reuse look better than a fresh learner?
                acc_best = row["acc_best_on_warning"]
                acc_new = row["acc_new_on_warning"]
                if acc_best is not None and acc_new is not None:
                    row["reuse_looked_better"] = int(acc_best >= acc_new)
                    row["acc_best_minus_new"] = float(acc_best) - float(acc_new)
                else:
                    row["reuse_looked_better"] = None
                    row["acc_best_minus_new"] = None
                row.update(
                    _gt_alignment(
                        confirmation_t, warning_t, drift_intervals, drift_starts, extension
                    )
                )
                row.update(_prewarning_features(signals_by_event.get(event_id, []), warning_t))
                # stage 4 (post-drift duel outcome)
                s4 = stage4.get(event_id, {})
                n_swaps = s4.get("n_leader_swaps")
                row["n_leader_swaps"] = n_swaps
                row["fresh_ever_led"] = s4.get("fresh_ever_led")
                row["final_leader_origin"] = s4.get("final_leader_origin")
                row["duel_final_margin"] = s4.get("duel_final_margin")
                row["duel_segment_len"] = s4.get("duel_segment_len")
                # reuse_survived = the initial reused copy was never displaced by the
                # fresh learner during the post-drift duel (n_leader_swaps == 0)
                row["reuse_survived"] = int(n_swaps == 0) if n_swaps is not None else None
                # KEY validation: did the drift-time buffer snapshot (reuse_looked_better)
                # match the actual post-drift duel outcome (reuse_survived)?
                rlb, rs = row.get("reuse_looked_better"), row.get("reuse_survived")
                row["snapshot_matched_duel"] = (
                    int(bool(rlb) == bool(rs)) if (rlb is not None and rs is not None) else None
                )
                interaction_rows.append(row)

            plot_path = analysis_dir / f"timeline_{config_dir.name}_{file_dir.name}.png"
            if _plot_timeline(
                plot_path, config_dir.name, file_dir.name, signals, events_for_plot, drift_intervals
            ):
                n_plots += 1

    # Write the joined interaction table.
    out_csv = analysis_dir / "event_interactions.csv"
    if interaction_rows:
        fieldnames = list(interaction_rows[0].keys())
        with out_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(interaction_rows)

    _print_summary(interaction_rows, out_csv, n_plots)


def _print_summary(rows: List[Dict[str, Any]], out_csv: Path, n_plots: int) -> None:
    n = len(rows)
    print(f"events: {n}")
    if n:
        tp = sum(1 for r in rows if r.get("gt_match") == "TP")
        looked = [r for r in rows if r.get("reuse_looked_better") is not None]
        reuse_better = sum(r["reuse_looked_better"] for r in looked)
        ages = [r["warning_to_confirm_age"] for r in rows if r.get("warning_to_confirm_age") is not None]
        print(f"  TP / FP            : {tp} / {n - tp}")
        if looked:
            print(f"  reuse looked better: {reuse_better}/{len(looked)} events (acc_best >= acc_new)")
        # stage 4 (post-drift duel outcome)
        duel = [r for r in rows if r.get("reuse_survived") is not None]
        if duel:
            survived = sum(r["reuse_survived"] for r in duel)
            print(f"  reuse survived duel : {survived}/{len(duel)} (never displaced by fresh)")
            matched = [r for r in duel if r.get("snapshot_matched_duel") is not None]
            if matched:
                agree = sum(r["snapshot_matched_duel"] for r in matched)
                print(f"  snapshot matched duel: {agree}/{len(matched)} ({100*agree/len(matched):.0f}%)")
            looked_worse = [r for r in duel if r.get("reuse_looked_better") == 0]
            if looked_worse:
                fresh_won = sum(1 for r in looked_worse if r.get("reuse_survived") == 0)
                print(f"  of 'fresh looked better on buffer': {fresh_won}/{len(looked_worse)} fresh actually took over")
        if ages:
            print(f"  mean warning->confirm age: {np.mean(ages):.1f}")
        print(f"  table : {out_csv}")
    print(f"  plots : {n_plots}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Join ECPF stage traces and plot interactions.")
    parser.add_argument("--run-dir", required=True, help="Run output dir containing traces/.")
    parser.add_argument(
        "--extension",
        type=int,
        default=0,
        help="± tolerance (samples) when matching events to ground-truth drift intervals.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    analyze_run(Path(args.run_dir), extension=args.extension)


if __name__ == "__main__":
    main()
