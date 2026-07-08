"""Observer-only stage tracer for the ECPF pipeline.

Captures the intermediate output of each ECPF stage so downstream
interpretability analysis can join them by ``event_id``:

* **Stage 1 — signals**   : per-sample ``err`` and warning/drift signals,
  kept only for a ``window`` neighbourhood around each drift event.
* **Stage 2 — detection** : per-event warning/confirmation timing + detector stats.
* **Stage 3 — profiling** : per-event ``ECPFMetaLearner.on_drift`` details
  (reuse candidate, per-expert buffer accuracy, pool merges, ...).
* **Stage 4 — duel**      : per-event post-drift in-control duel trajectory
  (leader vs freshly-trained shadow), leader-swap steps, and final winner.

The tracer is **read-only**: it only records values the pipeline already
computes; it never influences a decision. It is disabled by default
(``config.trace_enabled=False`` -> :class:`NullTracer`), so the normal pipeline
pays zero cost and behaves identically.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _f(value: Any) -> Optional[float]:
    """Best-effort float conversion that tolerates ``None``/numpy scalars."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _jsonable(obj: Any) -> Any:
    """Recursively coerce numpy / dict / list structures into JSON-safe values."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    # numpy scalars / arrays
    if hasattr(obj, "tolist"):
        try:
            return _jsonable(obj.tolist())
        except Exception:  # pragma: no cover - defensive
            return str(obj)
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:  # pragma: no cover - defensive
            return str(obj)
    return str(obj)


class NullTracer:
    """No-op tracer used when tracing is disabled. Every hook returns immediately."""

    enabled = False

    def configure(self, *args: Any, **kwargs: Any) -> None:
        return None

    def set_groundtruth(self, *args: Any, **kwargs: Any) -> None:
        return None

    def log_signal(self, *args: Any, **kwargs: Any) -> None:
        return None

    def on_event(self, *args: Any, **kwargs: Any) -> None:
        return None

    def log_duel(self, *args: Any, **kwargs: Any) -> None:
        return None

    def flush(self, *args: Any, **kwargs: Any) -> None:
        return None


class StageTracer:
    """Accumulate stage 1-3 outputs in memory, then flush to disk per (config, file).

    Output layout (under ``<out_dir>/<config_id>/<file>/``)::

        stage1_signals.csv      # rows within ±window of an event, tagged by event_id
        stage2_detection.jsonl  # one event per line: timing + detector stats
        stage3_profiling.jsonl  # one event per line: on_drift details
        meta.json               # ground-truth drift starts/intervals + run metadata
    """

    enabled = True

    STAGE1_COLUMNS = [
        "event_id",
        "t",
        "y_true",
        "y_pred",
        "err",
        "warning_value",
        "drift_value",
        "is_warning",
        "is_drift",
    ]

    def __init__(self, window: int = 300, duel_stride: int = 50) -> None:
        self.window = int(window)
        self.duel_stride = max(1, int(duel_stride))
        self._signals: List[Dict[str, Any]] = []
        self._events: List[Dict[str, Any]] = []
        self._drift_starts: List[int] = []
        self._drift_intervals: List[Tuple[int, int]] = []
        self._out_dir: Optional[Path] = None
        self._config_id: str = "config"
        self._file: str = "file"
        # stage-4 duel capture (post-drift in-control segment per event)
        self._duel_open: Optional[Dict[str, Any]] = None
        self._duel_segments: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def configure(self, out_dir: Any, config_id: str, file: str) -> None:
        self._out_dir = Path(out_dir)
        self._config_id = str(config_id)
        self._file = str(file)

    def set_groundtruth(
        self,
        drift_starts: Optional[Sequence[int]],
        drift_intervals: Optional[Sequence[Tuple[int, int]]] = None,
    ) -> None:
        self._drift_starts = [int(t) for t in (drift_starts or [])]
        self._drift_intervals = [
            (int(s), int(e)) for s, e in (drift_intervals or [])
        ]

    # ------------------------------------------------------------------
    # Hooks (called from the pipeline)
    # ------------------------------------------------------------------
    def log_signal(
        self,
        t: int,
        y_true: float,
        y_pred: float,
        err: float,
        warning_value: Any,
        drift_value: Any,
        is_warning: bool = False,
        is_drift: bool = False,
    ) -> None:
        self._signals.append(
            {
                "t": int(t),
                "y_true": _f(y_true),
                "y_pred": _f(y_pred),
                "err": _f(err),
                "warning_value": _f(warning_value),
                "drift_value": _f(drift_value),
                "is_warning": int(bool(is_warning)),
                "is_drift": int(bool(is_drift)),
            }
        )

    def on_event(
        self,
        *,
        warning_t: int,
        confirmation_t: int,
        source: str,
        stage2: Optional[Dict[str, Any]] = None,
        stage3: Optional[Dict[str, Any]] = None,
    ) -> None:
        event_id = f"{self._config_id}::{self._file}::{int(warning_t)}::{int(confirmation_t)}"
        # stage-4: the duel that ran up to this drift belonged to the PREVIOUS
        # event; close it, then open a fresh segment owned by this new event
        # (the post-drift duel that begins now belongs to this event).
        self._finalize_open_duel()
        self._duel_open = {"owner": event_id, "samples": [], "swap_steps": []}
        self._events.append(
            {
                "event_id": event_id,
                "config_id": self._config_id,
                "file": self._file,
                "warning_t": int(warning_t),
                "confirmation_t": int(confirmation_t),
                "warning_to_confirm_age": int(confirmation_t) - int(warning_t),
                "source": source,
                "stage2": _jsonable(stage2 or {}),
                "stage3": _jsonable(stage3 or {}),
            }
        )

    def log_duel(
        self,
        t: int,
        curr_correct: int,
        new_correct: int,
        total_inst: int,
        swapped: bool = False,
        current_idx: Optional[int] = None,
        has_shadow: bool = True,
    ) -> None:
        """Record one in-control duel sample into the current post-drift segment.

        ``curr_correct``/``new_correct`` are the running tallies of the active
        leader vs the shadow ``new_model`` since the last drift; ``swapped`` is
        True on the step a leader-swap fired. No-op until a drift has opened a
        segment and a shadow exists.
        """
        seg = self._duel_open
        if seg is None or not has_shadow:
            return
        if swapped:
            seg["swap_steps"].append(int(t))
        # keep the first sample, every ``duel_stride``-th step, and all swaps
        if swapped or not seg["samples"] or (int(total_inst) % self.duel_stride == 0):
            seg["samples"].append(
                {
                    "t": int(t),
                    "curr_correct": int(curr_correct),
                    "new_correct": int(new_correct),
                    "total_inst": int(total_inst),
                }
            )

    def _finalize_open_duel(self) -> None:
        seg = self._duel_open
        self._duel_open = None
        if seg is None or not seg["samples"]:
            return
        samples = seg["samples"]
        last = samples[-1]
        n_swaps = len(seg["swap_steps"])
        self._duel_segments.append(
            {
                "event_id": seg["owner"],
                "config_id": self._config_id,
                "file": self._file,
                "duel_start_t": samples[0]["t"],
                "duel_end_t": last["t"],
                "duel_segment_len": last["total_inst"],
                "n_leader_swaps": n_swaps,
                "fresh_ever_led": int(n_swaps >= 1),
                # after k swaps the live leader holds fresh-origin weights iff k is odd
                "final_leader_origin": "fresh" if n_swaps % 2 == 1 else "reused",
                "duel_final_curr_correct": last["curr_correct"],
                "duel_final_new_correct": last["new_correct"],
                "duel_final_margin": last["curr_correct"] - last["new_correct"],
                "swap_steps": seg["swap_steps"],
                "trajectory": samples,
            }
        )

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------
    def flush(self) -> None:
        if self._out_dir is None:
            return
        dst = self._out_dir / self._config_id / self._file
        dst.mkdir(parents=True, exist_ok=True)
        self._write_stage1(dst / "stage1_signals.csv")
        self._write_jsonl(
            dst / "stage2_detection.jsonl",
            [
                {
                    "event_id": e["event_id"],
                    "config_id": e["config_id"],
                    "file": e["file"],
                    "warning_t": e["warning_t"],
                    "confirmation_t": e["confirmation_t"],
                    "warning_to_confirm_age": e["warning_to_confirm_age"],
                    "source": e["source"],
                    **e["stage2"],
                }
                for e in self._events
            ],
        )
        self._write_jsonl(
            dst / "stage3_profiling.jsonl",
            [
                {
                    "event_id": e["event_id"],
                    "config_id": e["config_id"],
                    "file": e["file"],
                    "warning_t": e["warning_t"],
                    "confirmation_t": e["confirmation_t"],
                    **e["stage3"],
                }
                for e in self._events
            ],
        )
        self._finalize_open_duel()
        self._write_jsonl(dst / "stage4_duel.jsonl", self._duel_segments)
        self._write_meta(dst / "meta.json")

    # ------------------------------------------------------------------
    # Writers
    # ------------------------------------------------------------------
    def _event_ranges(self) -> List[Tuple[int, int, str]]:
        """``(lo, hi, event_id)`` windows kept for the stage-1 signal trace."""
        ranges: List[Tuple[int, int, str]] = []
        for e in self._events:
            lo = e["warning_t"] - self.window
            hi = e["confirmation_t"] + self.window
            ranges.append((lo, hi, e["event_id"]))
        return ranges

    def _write_stage1(self, path: Path) -> None:
        ranges = self._event_ranges()
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.STAGE1_COLUMNS)
            writer.writeheader()
            if not ranges:
                return
            for row in self._signals:
                t = row["t"]
                event_id = None
                for lo, hi, eid in ranges:
                    if lo <= t <= hi:
                        event_id = eid
                        break
                if event_id is None:
                    continue
                out = {"event_id": event_id}
                out.update(row)
                writer.writerow(out)

    @staticmethod
    def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(_jsonable(row), ensure_ascii=False) + "\n")

    def _write_meta(self, path: Path) -> None:
        meta = {
            "config_id": self._config_id,
            "file": self._file,
            "window": self.window,
            "n_events": len(self._events),
            "n_signal_samples": len(self._signals),
            "n_duel_segments": len(self._duel_segments),
            "duel_stride": self.duel_stride,
            "drift_starts": self._drift_starts,
            "drift_intervals": [list(iv) for iv in self._drift_intervals],
        }
        path.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
