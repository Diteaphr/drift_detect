"""Run the ECPF pipeline once and collect everything both views need.

Plan: ``docs/DASHBOARD_TWO_VIEWS_PLAN.md`` §5 -- **一次 run，兩種呈現**. The
engineer view used to drive the stream itself and paint as it went, which meant
nothing survived the run: switching roles re-ran the pipeline. Here the loop
lives in one place, hands live state to an optional ``on_tick`` callback (that
is how the engineer view still animates), and returns a ``RunResult`` the
caller parks in ``st.session_state`` for both views to render afterwards.

Views never touch pipeline internals: everything they display is lifted onto
``RunState`` / ``RunResult`` here, so the same ``draw_*`` function works both
live and from a stored result.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline, load_recurring_stream_pair

SIGNAL_CHOICES = ["error", "uq_mi", "uq_vote", "uq_entropy", "uq_variance"]
DETECTOR_CHOICES = ["adwin", "seed", "seqdrift2"]

# Curated demo streams: a few files per drift type so the deployed selector
# stays short (and the app stays snappy) instead of listing all ~40 files.
# The loader (`load_recurring_stream_pair`) is generic -- it reads any CSV with
# a `y` column and finds the sibling `_drift_times.txt` -- so every drift-type
# folder works, not just recurring_drift.
DEMO_DRIFT_DIRS = [
    ("sudden", Path("data/sudden_drift")),
    ("gradual", Path("data/gradual_drift")),
    ("incremental", Path("data/incremental_drift")),
    ("recurring", Path("data/recurring_drift")),
    # 10x-length stand-in for sudden g00, for runs long enough to watch
    # (see scripts/generate_long_sudden_stream.py).
    ("長版 ×10", Path("data/long_drift")),
]
DEMO_PER_TYPE = 2  # how many files to expose per drift type

# Ring-buffer depth for the history series, in sampled points (one per stride).
# At STRIDE=50 this spans ~100k samples, i.e. a whole standard file.
HIST_POINTS = 2000

# Width of the rolling-accuracy window. The cumulative (prequential) curve is
# too smooth to show a drift dip; this one is what the operator view's
# "近期準確率" line and every recovery metric in `core.metrics` are read off.
ROLL_WINDOW = 500

# Half-width of the ground-truth tolerance window. A drift confirmed inside it
# counts as a true positive -- the same tolerance the batch runner scores with
# (`run_ecpf_uq_experiment._detection_delay`).
GT_TOLERANCE = 500

# What the operator view runs with: it exposes no parameters at all (plan §1),
# so it needs one sane, fixed configuration.
DEFAULT_OPTS: Dict[str, Any] = dict(
    signal_mode="detector",
    warning_signal="error",
    drift_signal="error",
    warning_detector=None,
    drift_detector=None,
    detector_delta=0.05,
    detector_delta_w=0.1,
    detector_min_instances=30,
    max_pool_size=10,
    similarity_margin=0.95,
    fade_points=15,
    fade_enabled=True,
    model_type="ht",
)


def demo_streams() -> "List[Tuple[str, Path]]":
    """Return curated ``(drift_type_label, csv_path)`` pairs for the selector."""
    out: List[Tuple[str, Path]] = []
    for label, d in DEMO_DRIFT_DIRS:
        if d.is_dir():
            for p in sorted(d.glob("*.csv"))[:DEMO_PER_TYPE]:
                out.append((label, p))
    return out


def build_pipeline(opts: Dict[str, Any]) -> ConceptDriftPipeline:
    """Construct a pipeline from the view's options.

    Mirrors the config assembly in ``run_ecpf_uq_experiment.run_one`` so a
    monitored run is comparable to a batch one.
    """
    # UQ signals need per-class probabilities, which the plain Hoeffding tree
    # does not expose -- the batch runner promotes ht -> hf for the same reason.
    model_type = opts["model_type"]
    if model_type == "ht" and (
        opts["warning_signal"] != "error" or opts["drift_signal"] != "error"
    ):
        model_type = "hf"

    cfg = PipelineConfig(
        use_ecpf=True,
        model_type=model_type,
        ecpf_signal_mode=opts["signal_mode"],
        ecpf_oracle_true_drift_times=None,
        ecpf_warning_length=60,
        ecpf_max_pool_size=opts["max_pool_size"],
        ecpf_similarity_margin=opts["similarity_margin"],
        ecpf_fade_points=opts["fade_points"],
        ecpf_fade_enabled=opts["fade_enabled"],
        detector_delta=opts["detector_delta"],
        detector_delta_w=opts["detector_delta_w"],
        ecpf_detector_min_instances=opts["detector_min_instances"],
        ecpf_warning_detector=opts["warning_detector"],
        ecpf_drift_detector=opts["drift_detector"],
        ecpf_warning_signal=opts["warning_signal"],
        ecpf_drift_signal=opts["drift_signal"],
    )
    return ConceptDriftPipeline(cfg)


def pool_snapshot(ecpf: Any) -> List[Dict[str, Any]]:
    """Read the live model-pool state. Returns [] when ECPF is not active."""
    if ecpf is None:
        return []
    rows = []
    for idx, slot in enumerate(ecpf.slots):
        if slot is None:
            continue
        rows.append(
            {
                "slot": idx,
                "fade": ecpf.fade_scores.get(idx, 0),
                "is_leader": idx == ecpf.current_idx,
            }
        )
    return rows


# ----------------------------------------------------------------------
# State handed to the views
# ----------------------------------------------------------------------
@dataclass
class RunState:
    """Live snapshot passed to ``on_tick``. Mutated in place -- a view must
    read what it needs during the call, not stash the object.
    """

    t: int = 0
    n_seen: int = 0
    n_total: int = 0
    gt_times: List[int] = field(default_factory=list)
    elapsed: float = 0.0
    drift: bool = False  # this tick confirmed a drift

    roll_acc: Optional[float] = None
    preq_acc: Optional[float] = None

    events: List[Dict[str, Any]] = field(default_factory=list)
    signal_hist: List[Dict[str, Any]] = field(default_factory=list)
    preq_hist: List[Dict[str, Any]] = field(default_factory=list)
    duel_hist: List[Dict[str, Any]] = field(default_factory=list)
    pool: List[Dict[str, Any]] = field(default_factory=list)
    # Closed warning phases plus, while one is open, the partial span up to
    # `t` -- so a live chart can grow the amber band instead of only showing
    # it once the phase ends.
    warning_spans: List[Tuple[int, int]] = field(default_factory=list)

    # warning buffer (panel ②)
    warning_active: bool = False
    warning_start: Optional[int] = None
    buffer_len: int = 0

    # in-control duel (panel ④)
    has_shadow: bool = False
    leader_correct: int = 0
    shadow_correct: int = 0
    leader_swaps: int = 0


@dataclass
class RunResult:
    """Everything a finished run produced. Parked in ``st.session_state`` so
    switching roles re-renders instead of re-running.
    """

    csv_path: str
    stream_label: str
    opts: Dict[str, Any]
    warm_start: int
    max_steps: int
    stride: int

    n_total: int
    n_seen: int
    gt_times: List[int]
    events: List[Dict[str, Any]]
    signal_hist: List[Dict[str, Any]]
    preq_hist: List[Dict[str, Any]]
    duel_hist: List[Dict[str, Any]]
    warning_spans: List[Tuple[int, int]]
    pool: List[Dict[str, Any]]

    preq_acc: Optional[float]
    roll_acc: Optional[float]
    elapsed: float

    warning_active: bool
    warning_start: Optional[int]
    buffer_len: int
    has_shadow: bool
    leader_correct: int
    shadow_correct: int
    leader_swaps: int

    @property
    def throughput(self) -> float:
        """Samples per second, end to end."""
        return self.n_seen / self.elapsed if self.elapsed > 0 else 0.0


# ----------------------------------------------------------------------
# The run
# ----------------------------------------------------------------------
def run_and_collect(
    csv_path: Any,
    *,
    warm_start: int,
    max_steps: int,
    opts: Dict[str, Any],
    stride: int,
    stream_label: str = "",
    on_tick: Optional[Callable[[RunState], None]] = None,
) -> RunResult:
    """Drive ``ConceptDriftPipeline.run_stream`` and collect the whole run.

    ``on_tick`` is called on the same triggers the old monitor redrew on
    (drift confirmed / leader swap / warning opened or closed / every
    ``stride`` samples) and once more at the end. Read-only: nothing the
    callback does is fed back into the pipeline, so a monitored run behaves
    identically to the same run under ``run_ecpf_uq_experiment.py``.
    """
    X, y, gt_times = load_recurring_stream_pair(str(csv_path))
    if max_steps > 0:
        n = min(int(max_steps), len(y))
        X, y = X[:n], y[:n]
        gt_times = [t for t in gt_times if t < n]
    n_total = len(y)

    pipe = build_pipeline(opts)

    signal_hist: deque = deque(maxlen=HIST_POINTS)
    preq_hist: deque = deque(maxlen=HIST_POINTS)
    duel_hist: deque = deque(maxlen=HIST_POINTS)
    events: List[Dict[str, Any]] = []
    warning_spans: List[Tuple[int, int]] = []

    correct: deque = deque(maxlen=ROLL_WINDOW)
    warn_win: deque = deque(maxlen=200)  # rolling windows for the signal lines
    drift_win: deque = deque(maxlen=200)
    n_correct_total = 0  # cumulative, never evicted -- matches
    n_seen_total = 0     # run_ecpf_uq_experiment's `prequential_accuracy`
    last_swaps = 0
    last_warn_active = False
    warn_open_at: Optional[int] = None

    state = RunState(n_total=n_total, gt_times=list(gt_times), events=events)
    t0 = time.perf_counter()

    def sync(t: int, drift: bool) -> None:
        ecpf = pipe._ecpf
        state.t = t
        state.n_seen = n_seen_total
        state.drift = drift
        state.elapsed = time.perf_counter() - t0
        state.roll_acc = (sum(correct) / len(correct)) if correct else None
        state.preq_acc = (n_correct_total / n_seen_total) if n_seen_total else None
        state.signal_hist = list(signal_hist)
        state.preq_hist = list(preq_hist)
        state.duel_hist = list(duel_hist)
        state.pool = pool_snapshot(ecpf)
        state.warning_active = bool(getattr(pipe, "_ecpf_warning_active", False))
        state.warning_spans = list(warning_spans) + (
            [(int(warn_open_at), t)]
            if (state.warning_active and warn_open_at is not None) else []
        )
        state.warning_start = getattr(pipe, "_ecpf_warning_start_idx", None)
        state.buffer_len = len(getattr(pipe, "_ecpf_buffer", ()) or ())
        state.has_shadow = ecpf is not None and ecpf.new_model is not None
        state.leader_correct = getattr(ecpf, "curr_correct", 0) if ecpf else 0
        state.shadow_correct = getattr(ecpf, "new_correct", 0) if ecpf else 0
        state.leader_swaps = ecpf.leader_swaps if ecpf is not None else 0

    t = 0
    for t, y_true, y_pred, dets, drift in pipe.run_stream(X, y, int(warm_start)):
        is_correct = 1 if y_pred == y_true else 0
        correct.append(is_correct)
        n_correct_total += is_correct
        n_seen_total += 1
        ecpf = pipe._ecpf

        # ECPFAdwinFamilyDetector.stats is (re)written on every update_values
        # call; it is absent before the first call and the detector itself is
        # None for signal modes that do not use it (e.g. oracle_*).
        stats = getattr(pipe._ecpf_detector, "stats", None) or {}
        if stats.get("warning_value") is not None:
            warn_win.append(float(stats["warning_value"]))
        if stats.get("drift_value") is not None:
            drift_win.append(float(stats["drift_value"]))
        # The rolling windows above advance every sample, but the chart series
        # is sampled once per stride: at HIST_POINTS=2000 that spans the whole
        # 100k stream, so the ground-truth bands stay on screen instead of
        # scrolling off after 2000 samples.
        # Both signal lines are rolling means. Raw values are unreadable at
        # this density: with signal="error" they are a 0/1 spike train, and
        # even continuous UQ signals are heavily jittered per sample.
        if t % stride == 0 or drift:
            signal_hist.append(
                {
                    "t": t,
                    "warn_val": (sum(warn_win) / len(warn_win)) if warn_win else None,
                    "drift_val": (sum(drift_win) / len(drift_win)) if drift_win else None,
                }
            )
            preq_hist.append(
                {
                    "t": t,
                    "preq": n_correct_total / n_seen_total,
                    "roll": sum(correct) / len(correct),
                }
            )
        if ecpf is not None and ecpf.new_model is not None:
            duel_hist.append(
                {"t": t, "leader": ecpf.curr_correct, "shadow": ecpf.new_correct}
            )

        for d in dets:
            # `DriftDetection.timestamp` is the *warning start*, not the
            # confirmation (`_handle_ecpf_drift` is called with the buffered
            # `_ecpf_warning_start_idx`). The confirmation is the step we are
            # on right now. The batch runner scores against `timestamp` too,
            # so TP/FP here match its numbers.
            events.append(
                {
                    "timestamp": int(d.timestamp),
                    "warning_t": int(d.timestamp),
                    "confirmation_t": int(t),
                    "source": d.detector_source,
                    "drift_type": d.drift_type.value,
                    "details": d.details or {},
                }
            )

        swaps = ecpf.leader_swaps if ecpf is not None else 0
        warn_active = bool(getattr(pipe, "_ecpf_warning_active", False))
        # Warning spans are drawn as bands on the operator chart, so they are
        # recorded from the edges rather than sampled per stride (a short
        # warning phase can open and close inside one stride).
        if warn_active and not last_warn_active:
            warn_open_at = getattr(pipe, "_ecpf_warning_start_idx", None) or t
        elif last_warn_active and not warn_active and warn_open_at is not None:
            warning_spans.append((int(warn_open_at), int(t)))
            warn_open_at = None

        # 常態低頻聚合、關鍵事件穿透. Warning open/close is a trigger too: a
        # short warning phase can otherwise begin and end inside one stride and
        # never be drawn at all.
        if (
            drift
            or swaps != last_swaps
            or warn_active != last_warn_active
            or t % stride == 0
        ):
            if on_tick is not None:
                sync(t, drift)
                on_tick(state)
        last_swaps = swaps
        last_warn_active = warn_active

    if warn_open_at is not None:
        warning_spans.append((int(warn_open_at), int(t)))

    sync(max(t, n_total - 1), drift=False)
    if on_tick is not None:
        on_tick(state)

    return RunResult(
        csv_path=str(csv_path),
        stream_label=stream_label or str(csv_path),
        opts=dict(opts),
        warm_start=int(warm_start),
        max_steps=int(max_steps),
        stride=int(stride),
        n_total=n_total,
        n_seen=n_seen_total,
        gt_times=list(gt_times),
        events=events,
        signal_hist=list(signal_hist),
        preq_hist=list(preq_hist),
        duel_hist=list(duel_hist),
        warning_spans=warning_spans,
        pool=state.pool,
        preq_acc=state.preq_acc,
        roll_acc=state.roll_acc,
        elapsed=state.elapsed,
        warning_active=state.warning_active,
        warning_start=state.warning_start,
        buffer_len=state.buffer_len,
        has_shadow=state.has_shadow,
        leader_correct=state.leader_correct,
        shadow_correct=state.shadow_correct,
        leader_swaps=state.leader_swaps,
    )
