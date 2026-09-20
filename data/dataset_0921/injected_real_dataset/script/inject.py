"""Cerqueira et al. (2026) drift injection into shuffled real streams.

Reference:
  https://arxiv.org/abs/2606.07789
  https://github.com/vcerqueira/experiments-drift_evaluation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pandas as pd

from config import DRIFT_REGION, GRADUAL_WIDTH_MAX, LABEL_SKIP_PROBA


@dataclass
class TrialParams:
    drift_onset: int
    drift_end: int
    width: int
    y_selected: Optional[int] = None
    y_swap: Optional[int] = None
    x_perm: Optional[list[int]] = None
    x_filter_idx: Optional[int] = None
    x_filter_tau: Optional[float] = None


def _should_apply(i: int, onset: int, width: int, rng: np.random.Generator) -> bool:
    if i < onset:
        return False
    if width <= 0 or i >= onset + width:
        return True
    progress = (i - onset) / width
    return bool(rng.random() < progress)


def inject_stream(
    df: pd.DataFrame,
    *,
    method: str,
    abruptness: str,
    drift_width: int,
    rng: np.random.Generator,
    max_n: int | None = None,
    drift_region: tuple[float, float] = DRIFT_REGION,
    label_skip_proba: float = LABEL_SKIP_PROBA,
) -> tuple[pd.DataFrame, list[list[int]], dict[str, Any], pd.DataFrame, list[int]]:
    """Shuffle + inject one drift.

    Returns (out_df, drift_times_output, meta, baseline_df, kept_orig_idx).
    baseline_df: shuffled stream without transform (same order).
    kept_orig_idx: shuffle-index of each kept output row (for aligned plots).
    """
    feat_cols = [c for c in df.columns if c != "y"]
    work = df[feat_cols + ["y"]].copy()
    if max_n is not None and len(work) > max_n:
        # Keep first max_n rows of the (already stream-ordered) source; then shuffle.
        work = work.iloc[:max_n].reset_index(drop=True)

    shuffle_idx = rng.permutation(len(work))
    work = work.iloc[shuffle_idx].reset_index(drop=True)
    baseline = work.rename(columns={c: f"x{i}" for i, c in enumerate(feat_cols)})
    # ensure column order x* + y
    baseline = baseline[[f"x{i}" for i in range(len(feat_cols))] + ["y"]].copy()
    X = work[feat_cols].to_numpy(dtype=float)
    y = work["y"].to_numpy()

    n = len(work)
    lo, hi = drift_region
    # abrupt: w=0; gradual: paper width, hard-capped ≤ GRADUAL_WIDTH_MAX and ≤ 30% of n
    if abruptness == "abrupt":
        width = 0
    else:
        width = min(int(drift_width), int(GRADUAL_WIDTH_MAX), max(0, int(0.3 * n)))
    max_onset = max(1, n - width - 1)
    onset = int(rng.uniform(lo, hi) * n)
    onset = int(np.clip(onset, int(lo * n), max_onset))
    end = min(n - 1, onset + width)

    classes = np.unique(y)
    is_class = np.issubdtype(y.dtype, np.integer) or (
        np.allclose(y, np.round(y)) and len(classes) <= 100
    )
    y_int = np.round(y).astype(int) if is_class else y

    y_sel = y_swap = None
    x_perm = None
    x_filter_idx = None
    x_filter_tau = None

    if method in ("class_prior", "label_swap"):
        if not is_class or len(classes) < 2:
            raise ValueError(f"{method} requires ≥2 discrete classes")
        y_sel = int(rng.choice(np.unique(y_int)))
        others = [int(c) for c in np.unique(y_int) if int(c) != y_sel]
        y_swap = int(rng.choice(others))

    if method == "feature_permutation":
        x_perm = rng.permutation(X.shape[1]).tolist()

    if method == "feature_filtering":
        # Paper Alg.5: τ = median of values observed before drift onset
        x_filter_idx = int(rng.integers(0, X.shape[1]))
        pre = X[:onset, x_filter_idx]
        x_filter_tau = float(np.median(pre)) if len(pre) else float(np.median(X[:, x_filter_idx]))

    rows: list[list[Any]] = []
    out_ys: list[Any] = []
    kept_orig_idx: list[int] = []
    # map original i -> output index for kept rows
    orig_to_out: dict[int, int] = {}

    for i in range(n):
        apply = _should_apply(i, onset, width, rng)
        xi = X[i].copy()
        yi = y[i]

        if apply:
            if method == "class_prior":
                if int(y_int[i]) == y_sel and rng.random() < label_skip_proba:
                    continue
            elif method == "label_swap":
                if int(y_int[i]) == y_sel:
                    yi = y_swap
            elif method == "feature_permutation":
                assert x_perm is not None
                xi = xi[np.asarray(x_perm)]
            elif method == "feature_filtering":
                assert x_filter_idx is not None and x_filter_tau is not None
                if xi[x_filter_idx] > x_filter_tau:
                    continue
            else:
                raise ValueError(f"Unknown method: {method}")

        out_idx = len(rows)
        orig_to_out[i] = out_idx
        kept_orig_idx.append(i)
        rows.append(xi.tolist())
        out_ys.append(yi)

    if not rows:
        raise RuntimeError("All instances dropped; try another seed")

    out = pd.DataFrame(rows, columns=[f"x{j}" for j in range(X.shape[1])])
    # preserve int labels when classification
    if is_class:
        out["y"] = np.asarray(out_ys, dtype=int)
    else:
        out["y"] = np.asarray(out_ys, dtype=float)

    def _map_bound(orig_t: int, *, after: bool) -> int:
        """Map original index bound to nearest kept output index."""
        if after:
            for j in range(orig_t, n):
                if j in orig_to_out:
                    return orig_to_out[j]
            return len(out) - 1
        for j in range(orig_t, -1, -1):
            if j in orig_to_out:
                return orig_to_out[j]
        return 0

    ds_out = _map_bound(onset, after=True)
    de_out = _map_bound(end, after=True) if width > 0 else ds_out
    if de_out < ds_out:
        de_out = ds_out
    intervals = [[int(ds_out), int(de_out)]]
    intervals_input = [[int(onset), int(end)]]

    meta = {
        "method": method,
        "abruptness": abruptness,
        "n_input": int(n),
        "n_output": int(len(out)),
        "drift_onset_input": int(onset),
        "drift_end_input": int(end),
        "drift_width": int(width),
        "drift_times_output": intervals,
        "drift_times_input": intervals_input,
        "y_selected": y_sel,
        "y_swap": y_swap,
        "x_perm": x_perm,
        "x_filter_idx": x_filter_idx,
        "x_filter_tau": x_filter_tau,
        "label_skip_proba": label_skip_proba if method == "class_prior" else None,
        "drift_region": list(drift_region),
    }
    return out, intervals, meta, baseline, kept_orig_idx
