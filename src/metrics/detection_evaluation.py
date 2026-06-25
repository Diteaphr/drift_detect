"""
Unified offline evaluation summary for drift detection runs.

Metrics:
- n_warnings / n_alerts / n_actual
- count_score_warning / count_score_alert: 1 - |N_detect - N_actual| / N_actual
- cd_score_pct: interval-based correct detection on alert timestamps (uses DEFAULT_PERTURBATION_EXTENSION)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, List, Mapping, Optional, Sequence, Tuple

from .correct_detection import (
    DEFAULT_PERTURBATION_EXTENSION,
    Interval,
    build_perturbation_intervals,
    compute_correct_detection,
)


def compute_count_score(n_detect: int, n_actual: int) -> Optional[float]:
    """Score = 1 - |N_detect - N_actual| / N_actual, clamped to [0, 1]."""
    if n_actual <= 0:
        return None
    raw = 1.0 - abs(int(n_detect) - int(n_actual)) / float(n_actual)
    return max(0.0, min(1.0, raw))


@dataclass(frozen=True)
class DetectionEvaluationSummary:
    n_warnings: int
    n_alerts: int
    n_actual: int
    count_score_warning: Optional[float]
    count_score_alert: Optional[float]
    cd_tp: int
    cd_fp: int
    cd_n: int
    cd_score_pct: Optional[float]
    perturbation_extension: int = DEFAULT_PERTURBATION_EXTENSION

    def to_dict(self) -> dict:
        return asdict(self)


def summary_from_dict(data: Mapping[str, Any]) -> DetectionEvaluationSummary:
    """Build a summary from a flat dict (e.g. pipeline run row / CSV row)."""
    return DetectionEvaluationSummary(
        n_warnings=int(data.get("n_warnings", 0)),
        n_alerts=int(data.get("n_alerts", 0)),
        n_actual=int(data.get("n_actual", 0)),
        count_score_warning=data.get("count_score_warning"),
        count_score_alert=data.get("count_score_alert"),
        cd_tp=int(data.get("cd_tp", 0)),
        cd_fp=int(data.get("cd_fp", 0)),
        cd_n=int(data.get("cd_n", 0)),
        cd_score_pct=data.get("cd_score_pct"),
        perturbation_extension=int(
            data.get("perturbation_extension", DEFAULT_PERTURBATION_EXTENSION)
        ),
    )


def evaluate_detection_run(
    warning_timestamps: Sequence[int],
    alert_timestamps: Sequence[int],
    drift_intervals: Sequence[Interval],
    *,
    extension: int = DEFAULT_PERTURBATION_EXTENSION,
) -> DetectionEvaluationSummary:
    """Compute unified evaluation metrics from a single stream run."""
    n_warnings = len(list(warning_timestamps))
    n_alerts = len(list(alert_timestamps))
    n_actual = len(list(drift_intervals))

    count_score_warning = compute_count_score(n_warnings, n_actual)
    count_score_alert = compute_count_score(n_alerts, n_actual)

    perturbation = build_perturbation_intervals(drift_intervals, extension=extension)
    cd = compute_correct_detection(alert_timestamps, perturbation)

    return DetectionEvaluationSummary(
        n_warnings=n_warnings,
        n_alerts=n_alerts,
        n_actual=n_actual,
        count_score_warning=count_score_warning,
        count_score_alert=count_score_alert,
        cd_tp=cd.tp,
        cd_fp=cd.fp,
        cd_n=cd.n_intervals,
        cd_score_pct=cd.score_percent,
        perturbation_extension=extension,
    )


def _fmt_count_score(value: Optional[float]) -> str:
    return f"{value:.3f}" if value is not None else "n/a"


def _fmt_cd_pct(value: Optional[float]) -> str:
    return f"{value:.1f}%" if value is not None else "n/a"


def _align_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    aligns: Optional[Sequence[str]] = None,
) -> str:
    """Render a fixed-width ASCII table (no external deps)."""
    if not rows:
        return ""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    if aligns is None:
        aligns = ["<"] * len(headers)

    def _fmt_row(cells: Sequence[str]) -> str:
        parts = []
        for i, cell in enumerate(cells):
            w = widths[i]
            if aligns[i] == ">":
                parts.append(cell.rjust(w))
            elif aligns[i] == "^":
                parts.append(cell.center(w))
            else:
                parts.append(cell.ljust(w))
        return "  ".join(parts)

    sep = "  ".join("-" * w for w in widths)
    lines = [_fmt_row(headers), sep]
    lines.extend(_fmt_row(r) for r in rows)
    return "\n".join(lines)


def format_evaluation_summary_compact(summary: DetectionEvaluationSummary) -> str:
    """One-line summary for plot titles."""
    return (
        f"warn={summary.n_warnings} alert={summary.n_alerts} "
        f"actual={summary.n_actual} score_a={_fmt_count_score(summary.count_score_alert)} "
        f"CD={_fmt_cd_pct(summary.cd_score_pct)}"
    )


def format_evaluation_summary(summary: DetectionEvaluationSummary) -> str:
    """Two-column metrics table for a single run."""
    rows = [
        ("Warnings", str(summary.n_warnings)),
        ("Alerts", str(summary.n_alerts)),
        ("Actual drifts (N)", str(summary.n_actual)),
        ("Count score (warning)", _fmt_count_score(summary.count_score_warning)),
        ("Count score (alert)", _fmt_count_score(summary.count_score_alert)),
        ("Correct detection", _fmt_cd_pct(summary.cd_score_pct)),
        ("CD detail (TP / FP / N)", f"{summary.cd_tp} / {summary.cd_fp} / {summary.cd_n}"),
        ("Perturbation window", f"+{summary.perturbation_extension}"),
    ]
    return _align_table(["Metric", "Value"], rows, aligns=["<", ">"])


_BatchCol = Tuple[str, Callable[[DetectionEvaluationSummary, Mapping[str, Any]], str], str]
_ExtraCol = Tuple[str, Callable[[Mapping[str, Any]], str], str, str]

_BATCH_COLUMNS: List[_BatchCol] = [
    ("warn", lambda s, _: str(s.n_warnings), ">"),
    ("alert", lambda s, _: str(s.n_alerts), ">"),
    ("actual", lambda s, _: str(s.n_actual), ">"),
    ("score_w", lambda s, _: _fmt_count_score(s.count_score_warning), ">"),
    ("score_a", lambda s, _: _fmt_count_score(s.count_score_alert), ">"),
    ("CD%", lambda s, _: _fmt_cd_pct(s.cd_score_pct), ">"),
    ("TP", lambda s, _: str(s.cd_tp), ">"),
    ("FP", lambda s, _: str(s.cd_fp), ">"),
    ("N", lambda s, _: str(s.cd_n), ">"),
]


def format_evaluation_batch_table(
    entries: Sequence[Tuple[str, DetectionEvaluationSummary, Mapping[str, Any]]],
    *,
    extra_columns: Optional[Sequence[_ExtraCol]] = None,
    title: str = "Detection evaluation",
    mean_label: str = "MEAN",
    include_mean: bool = True,
) -> str:
    """
    Multi-row table for batch runs.

    Each entry is (label, summary, extras_dict). ``extra_columns`` entries are
    ``(header, getter, align, numeric_key)``; ``numeric_key`` must exist in
    extras_dict for MEAN aggregation.
    """
    if not entries:
        return f"{title}\n(no runs)"

    extra_columns = list(extra_columns or [])
    headers = ["dataset"] + [c[0] for c in _BATCH_COLUMNS] + [c[0] for c in extra_columns]
    aligns = ["<"] + [c[2] for c in _BATCH_COLUMNS] + [c[2] for c in extra_columns]

    table_rows: List[List[str]] = []
    sum_warn = sum_alert = sum_actual = sum_tp = sum_fp = sum_n = 0
    count_w_vals: List[float] = []
    count_a_vals: List[float] = []
    cd_vals: List[float] = []
    extra_numeric: dict[str, List[float]] = {c[3]: [] for c in extra_columns}

    for label, summary, extras in entries:
        cells = [label]
        for _, getter, _ in _BATCH_COLUMNS:
            cells.append(getter(summary, extras))
        for col_name, getter, _, num_key in extra_columns:
            raw = extras.get(num_key)
            text = getter(extras)
            cells.append(text)
            if isinstance(raw, (int, float)) and raw == raw:
                extra_numeric[num_key].append(float(raw))

        table_rows.append(cells)
        sum_warn += summary.n_warnings
        sum_alert += summary.n_alerts
        sum_actual += summary.n_actual
        sum_tp += summary.cd_tp
        sum_fp += summary.cd_fp
        sum_n += summary.cd_n
        if summary.count_score_warning is not None:
            count_w_vals.append(summary.count_score_warning)
        if summary.count_score_alert is not None:
            count_a_vals.append(summary.count_score_alert)
        if summary.cd_score_pct is not None:
            cd_vals.append(summary.cd_score_pct)

    n = len(entries)
    mean_cells = [mean_label]
    mean_cells.append(f"{sum_warn / n:.1f}")
    mean_cells.append(f"{sum_alert / n:.1f}")
    mean_cells.append(f"{sum_actual / n:.1f}")
    mean_cells.append(
        f"{sum(count_w_vals) / len(count_w_vals):.3f}" if count_w_vals else "n/a"
    )
    mean_cells.append(
        f"{sum(count_a_vals) / len(count_a_vals):.3f}" if count_a_vals else "n/a"
    )
    mean_cells.append(f"{sum(cd_vals) / len(cd_vals):.1f}%" if cd_vals else "n/a")
    mean_cells.append(f"{sum_tp / n:.1f}")
    mean_cells.append(f"{sum_fp / n:.1f}")
    mean_cells.append(f"{sum_n / n:.1f}")
    for col_name, _, _, num_key in extra_columns:
        vals = extra_numeric[num_key]
        if not vals:
            mean_cells.append("n/a")
        elif num_key == "runtime_s" or col_name == "time_s":
            mean_cells.append(f"{sum(vals) / len(vals):.1f}")
        elif num_key == "detection_delay" or col_name == "delay":
            mean_cells.append(f"{sum(vals) / len(vals):.0f}")
        else:
            mean_cells.append(f"{sum(vals) / len(vals):.4f}")

    if include_mean:
        table_rows.append(mean_cells)
    body = _align_table(headers, table_rows, aligns=aligns)
    ext = entries[0][1].perturbation_extension
    return f"{title}  (perturbation=drift_interval+{ext})\n{body}"


def print_evaluation_batch_table(
    entries: Sequence[Tuple[str, DetectionEvaluationSummary, Mapping[str, Any]]],
    **kwargs: Any,
) -> None:
    print(format_evaluation_batch_table(entries, **kwargs))
