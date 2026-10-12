"""
evaluate_run.py
===============
The single place where benchmark metrics are computed.

Every runner stores the raw per-instance record of a run (``y_true``,
``y_pred``, alarm indices) and calls :func:`evaluate_run` on it, so a metric
definition is fixed in one file and a bug fix only needs a re-evaluation, not a
re-run.

Definitions follow the implementations the literature numbers were produced
with, not the paper prose:

* Classification -- MOA ``BasicClassificationPerformanceEvaluator`` (which
  CapyMOA wraps; DriftMoE and Cerqueira et al. report through CapyMOA):
  accuracy, Cohen's kappa, Kappa-T against a no-change classifier whose
  "last seen class" starts at 0, Kappa-M against a majority classifier whose
  class counts already include the current instance, and macro-F1 over the full
  label set with undefined per-class precision/recall counted as 0.
* Detection -- ``EvaluateDriftDetector`` from Cerqueira et al. (KDD'26,
  github.com/vcerqueira/experiments-drift_evaluation, ``src/eval_detector.py``):
  every alarm inside the acceptable window is a TP (recall can exceed the
  episode count); ``episode_recall`` is the one-hit-per-drift variant. Their
  real-data runs record a gradual drift as ``(onset, onset)``, so the default
  window is ``[d_s - delta_pre, d_s + delta_max]``; the paper-text window
  ``[d_s - delta_pre, d_e + delta_max]`` is reported alongside with the
  ``_paper_window`` suffix.

Instances the system did not score (e.g. a warm-start segment that was only
trained on) are passed as NaN in ``y_pred``. Literature numbers are computed
over the whole stream, so ``acc_prequential`` and the kappa family are only
reported when every instance was scored; otherwise they fall back to the
scored suffix and ``metric_scope`` says so.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

CLASSIFICATION_TASKS = frozenset({"binary", "multiclass", "multi_classification"})


def _safe_kappa(p0: float, pc: float) -> Optional[float]:
    return None if pc >= 1.0 else float((p0 - pc) / (1.0 - pc))


def no_change_correct(y_true: np.ndarray) -> np.ndarray:
    """Per-instance hits of MOA's no-change classifier (``lastSeenClass`` starts at 0)."""
    prev = np.concatenate(([0], y_true[:-1]))
    return prev == y_true


def majority_correct(y_true: np.ndarray) -> np.ndarray:
    """Per-instance hits of MOA's majority classifier.

    MOA updates the class counts with the current label before asking for the
    majority, and breaks ties towards the lowest class index.
    """
    counts: Dict[int, int] = {}
    maj, maj_count = 0, 0
    out = np.empty(len(y_true), dtype=bool)
    for i, y in enumerate(y_true.tolist()):
        c = counts.get(y, 0) + 1
        counts[y] = c
        if c > maj_count or (c == maj_count and y < maj):
            maj, maj_count = y, c
        out[i] = maj == y
    return out


def windowed_accuracy_mean(correct: np.ndarray, window: int) -> float:
    """Mean over all instances of the sliding-window accuracy (partial windows at the start)."""
    cs = np.concatenate(([0], np.cumsum(correct, dtype=np.int64)))
    t = np.arange(1, len(correct) + 1)
    lo = np.maximum(t - window, 0)
    return float(np.mean((cs[t] - cs[lo]) / (t - lo)))


def classification_metrics(
    y_true: Sequence,
    y_pred: Sequence,
    *,
    n_classes: Optional[int] = None,
    window: int = 1000,
) -> Dict[str, Any]:
    yt = np.rint(np.asarray(y_true, dtype=float)).astype(np.int64)
    yp = np.rint(np.asarray(y_pred, dtype=float)).astype(np.int64)
    n = len(yt)
    if n == 0:
        raise ValueError("empty stream")
    k = int(n_classes) if n_classes else int(max(yt.max(), yp.max())) + 1

    correct = yp == yt
    acc = float(correct.mean())
    in_range = (yp >= 0) & (yp < k)
    row = np.bincount(yp[in_range], minlength=k)[:k] / n
    col = np.bincount(yt, minlength=k)[:k] / n
    acc_nc = float(no_change_correct(yt).mean())
    acc_maj = float(majority_correct(yt).mean())

    tp = np.bincount(yt[correct], minlength=k)[:k].astype(float)
    pred_cnt = np.bincount(yp[in_range], minlength=k)[:k].astype(float)
    true_cnt = np.bincount(yt, minlength=k)[:k].astype(float)
    prec = np.divide(tp, pred_cnt, out=np.zeros(k), where=pred_cnt > 0)
    rec = np.divide(tp, true_cnt, out=np.zeros(k), where=true_cnt > 0)
    f1 = np.divide(2 * prec * rec, prec + rec, out=np.zeros(k), where=(prec + rec) > 0)

    return {
        "accuracy": acc,
        f"acc_window{window}_mean": windowed_accuracy_mean(correct, window),
        "kappa": _safe_kappa(acc, float(np.sum(row * col))),
        "kappa_m": _safe_kappa(acc, acc_maj),
        "kappa_t": _safe_kappa(acc, acc_nc),
        "macro_f1": float(f1.mean()),
        "baseline_no_change_acc": acc_nc,
        "baseline_majority_acc": acc_maj,
        "n_classes": k,
    }


def regression_metrics(y_true: Sequence, y_pred: Sequence) -> Dict[str, Any]:
    err = np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)
    return {"mae": float(np.mean(np.abs(err))), "rmse": float(np.sqrt(np.mean(err**2)))}


def detection_metrics(
    alarms: Sequence[int],
    gt_intervals: Sequence[Tuple[int, int]],
    *,
    n_instances: int,
    delta_max: int,
    delta_pre: int = 0,
    anchor: str = "start",
    rate_period: int = 1000,
) -> Dict[str, Any]:
    """Cerqueira et al. detection metrics for one stream.

    Alarms are split into one episode per drift: episode *k* owns the alarms in
    ``(end_{k-1} + delta_max, end_k + delta_max]``; alarms after the last window
    belong to the last episode and therefore count as FPs, as in their
    single-drift real-data runs.

    ``anchor="start"`` scores a drift as ``(d_s, d_s)`` (their code),
    ``anchor="end"`` as ``(d_s, d_e)`` (their paper text).
    """
    if delta_max <= 0:
        raise ValueError("delta_max must be positive")
    if anchor not in ("start", "end"):
        raise ValueError("anchor must be 'start' or 'end'")
    al = np.sort(np.asarray(list(alarms), dtype=np.int64))
    eps = sorted((int(s), int(s) if anchor == "start" else int(e)) for s, e in gt_intervals)

    tp = fp = fn = etp = 0
    delays = []
    lo = -np.inf
    for k, (s, e) in enumerate(eps):
        hi = np.inf if k == len(eps) - 1 else e + delta_max
        mine = al[(al > lo) & (al <= hi)]
        hit = (mine >= s - delta_pre) & (mine <= e + delta_max)
        tp += int(hit.sum())
        fp += int((~hit).sum())
        if hit.any():
            etp += 1
            delays.append(int(mine[hit][0]) - s)
        else:
            fn += 1
        lo = hi
    if not eps:
        fp = len(al)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    mdt = float(np.mean(delays)) if delays else None
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "episode_recall": etp / max(1, len(eps)),
        "mdt": mdt,
        "ndt": None if mdt is None else mdt / delta_max,
        "far": fp / max(1, n_instances) * rate_period,
        "ar": len(al) / max(1, n_instances) * rate_period,
        "n_episodes": len(eps),
        "n_alarms": int(len(al)),
    }


_DETECTION_KEYS = ("tp", "fp", "fn", "precision", "recall", "f1", "episode_recall", "mdt", "ndt", "far")
_PAPER_WINDOW_KEYS = ("tp", "fp", "precision", "recall", "f1", "episode_recall", "mdt")


def evaluate_run(
    y_true: Sequence,
    y_pred: Sequence,
    *,
    task: str,
    alarms: Optional[Sequence[int]] = None,
    gt_intervals: Optional[Sequence[Tuple[int, int]]] = None,
    delta_max: Optional[int] = None,
    delta_pre: int = 0,
    warm_start: int = 0,
    window: int = 1000,
    n_classes: Optional[int] = None,
    rate_period: int = 1000,
    detect_from: int = 0,
    detection_n_instances: Optional[int] = None,
) -> Dict[str, Any]:
    """Compute every benchmark metric for one run.

    ``gt_intervals=None`` means the stream has no ground truth: detection
    fields are ``None`` and only the alarm rate is reported.

    Alarms and ``gt_intervals`` may live in a different coordinate system than
    the predictions: Cerqueira et al. count dropped instances, so their alarm
    indices, drift points and stream length are input-stream positions. Pass
    alarms/intervals in that system together with ``detection_n_instances``.
    Alarms before ``detect_from`` are ignored (their detectors only start after
    25% of the stream).
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    if yt.shape != yp.shape:
        raise ValueError(f"y_true {yt.shape} and y_pred {yp.shape} differ")
    n = len(yt)
    scored = ~np.isnan(yp)
    first = int(np.argmax(scored)) if scored.any() else n
    if scored.any() and not scored[first:].all():
        raise ValueError("unscored instances must form a prefix of the stream")
    full = bool(scored.all())
    alarms = [] if alarms is None else [int(a) for a in alarms if int(a) >= detect_from]
    n_det = n if detection_n_instances is None else int(detection_n_instances)

    out: Dict[str, Any] = {
        "task": task,
        "n_samples": n,
        "n_scored": int(scored.sum()),
        "warm_start": int(warm_start),
        "metric_scope": "full" if full else "scored_suffix",
    }

    is_clf = task in CLASSIFICATION_TASKS
    ws = min(max(int(warm_start), first), n)
    if is_clf:
        m = classification_metrics(yt[first:], yp[first:], n_classes=n_classes, window=window)
        post = np.rint(yp[ws:]) == np.rint(yt[ws:])
        acc = m.pop("accuracy")
        out["acc_prequential"] = acc if full else None
        out["acc_post_warmup"] = float(post.mean()) if len(post) else None
        out.update(m)
    elif task == "regression":
        m = regression_metrics(yt[first:], yp[first:])
        out.update(m)
        out["mae_post_warmup"] = regression_metrics(yt[ws:], yp[ws:])["mae"] if ws < n else None
    else:
        raise ValueError(f"unknown task {task!r}")

    out["n_alarms"] = len(alarms)
    out["ar"] = len(alarms) / max(1, n_det) * rate_period
    out["delta_max"] = delta_max
    out["detect_from"] = int(detect_from)
    if gt_intervals is None or len(gt_intervals) == 0:
        out["n_gt"] = 0 if gt_intervals is not None else None
        for key in _DETECTION_KEYS:
            out[key] = None
        for key in _PAPER_WINDOW_KEYS:
            out[f"{key}_paper_window"] = None
        return out
    if delta_max is None:
        raise ValueError("delta_max is required when gt_intervals is given")

    kw = dict(n_instances=n_det, delta_max=int(delta_max), delta_pre=delta_pre, rate_period=rate_period)
    det = detection_metrics(alarms, gt_intervals, anchor="start", **kw)
    paper = detection_metrics(alarms, gt_intervals, anchor="end", **kw)
    out["n_gt"] = det["n_episodes"]
    for key in _DETECTION_KEYS:
        out[key] = det[key]
    for key in _PAPER_WINDOW_KEYS:
        out[f"{key}_paper_window"] = paper[key]
    return out


def pool_detection_runs(runs: Sequence[Dict[str, Any]], suffix: str = "") -> Dict[str, Any]:
    """Pool per-run detection results the way Cerqueira et al. report a table cell.

    Their ``calc_performance`` receives all Monte Carlo trials as episodes of one
    call: tp/fp/fn are summed before precision/recall/F1, MDT averages the first
    in-window delay of every detected episode, and FAR/AR divide the summed
    counts by a single stream length (so they equal the sum of per-run rates
    when all trials have the same length). ``suffix="_paper_window"`` pools the
    paper-text-window fields instead.
    """
    rows = [r for r in runs if r.get("n_gt")]
    if not rows:
        return {}
    tp = sum(int(r[f"tp{suffix}"]) for r in rows)
    fp = sum(int(r[f"fp{suffix}"]) for r in rows)
    etp = [r[f"episode_recall{suffix}"] * r["n_gt"] for r in rows]
    n_ep = sum(int(r["n_gt"]) for r in rows)
    fn = n_ep - int(round(sum(etp)))
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    w = [(r[f"mdt{suffix}"], e) for r, e in zip(rows, etp) if r[f"mdt{suffix}"] is not None and e > 0]
    mdt = sum(m * e for m, e in w) / sum(e for _, e in w) if w else None
    delta_max = rows[0].get("delta_max")
    out = {
        "n_runs": len(rows), "n_episodes": n_ep, "tp": tp, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall, "f1": f1,
        "episode_recall": (n_ep - fn) / n_ep, "mdt": mdt,
        "ndt": None if mdt is None or not delta_max else mdt / delta_max,
    }
    if not suffix:
        out["far_cerqueira"] = sum(float(r["far"]) for r in rows)
        out["ar_cerqueira"] = sum(float(r["ar"]) for r in rows)
        out["far_per_run"] = out["far_cerqueira"] / len(rows)
    return out
