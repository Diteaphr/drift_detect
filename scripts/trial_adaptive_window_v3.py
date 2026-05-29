"""
V3: Reuse V2-trained RF (no retraining). Inference uses proxy features
derived from detector outputs only (no ground-truth drift intervals).

Proxy mapping:
    n_drifts             ← n_drift_confirms
    interval_width_mean  ← mean(drift_confirm - warning)        # detector "drift duration"
    interval_width_std   ← std(drift_confirm - warning)
    avg_inter_drift_gap  ← mean gap between consecutive drift_confirms
    drift_density        ← sum(estimated_widths) / stream_length
    pre_drift_var_mean   ← mean feature variance in 500 samples before each WARNING
    pre_drift_var_std    ← std of those variances
    drift_type_code      ← -1 (unknown; no proxy available from stream alone)
    feature_count        ← X.shape[1]              (same as offline)
    label_entropy        ← entropy(y distribution) (same as offline)

Output: outputs/adaptive_window_report_v3/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import (
    build_perturbation_intervals,
    compute_correct_detection,
    AdaptiveWindowEstimator,
)

ROOT = Path(__file__).resolve().parents[1]
V2_DIR = ROOT / "outputs" / "adaptive_window_report_v2"
V2_STATE = V2_DIR / "experiment_state.json"
V2_MODEL = ROOT / "models" / "adaptive_window_rf_v2.pkl"

OUT_DIR = ROOT / "outputs" / "adaptive_window_report_v3"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def proxy_features(
    warnings: List[int],
    drift_confirms: List[int],
    stream_length: int,
    X: np.ndarray,
    y: np.ndarray,
    pre_window: int = 500,
) -> np.ndarray:
    """Compute 10-D feature vector using ONLY detector outputs + (X, y).
    No ground-truth drift intervals required."""

    # Pair each warning with its earliest matching drift_confirm (>= warning)
    paired_widths: List[int] = []
    for w in warnings:
        nxt = [d for d in drift_confirms if d >= w]
        if nxt:
            paired_widths.append(nxt[0] - w)
    widths = np.array(paired_widths, dtype=float) if paired_widths else np.array([0.0])

    n_drifts_proxy = len(drift_confirms)  # use confirmed drifts as count

    interval_width_mean = float(widths.mean())
    interval_width_std = float(widths.std()) if len(widths) > 1 else 0.0

    if n_drifts_proxy > 1:
        gaps = np.diff(sorted(drift_confirms))
        avg_inter_drift_gap = float(gaps.mean())
    else:
        avg_inter_drift_gap = float(stream_length)

    drift_density = float(widths.sum()) / stream_length if stream_length > 0 else 0.0

    pre_vars: List[float] = []
    for w in warnings:
        lo = max(0, w - pre_window)
        hi = w
        win = X[lo:hi]
        if len(win) > 1:
            pre_vars.append(float(np.var(win, axis=0).mean()))
        else:
            pre_vars.append(0.0)
    pre_var_mean = float(np.mean(pre_vars)) if pre_vars else 0.0
    pre_var_std = float(np.std(pre_vars)) if len(pre_vars) > 1 else 0.0

    feature_count = X.shape[1]

    _, counts = np.unique(y, return_counts=True)
    probs = counts / counts.sum()
    label_entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))

    drift_type_code = -1.0  # unknown from stream alone

    return np.array(
        [
            drift_type_code,
            interval_width_mean,
            interval_width_std,
            float(n_drifts_proxy),
            avg_inter_drift_gap,
            drift_density,
            pre_var_mean,
            pre_var_std,
            float(feature_count),
            label_entropy,
        ],
        dtype=float,
    )


def main():
    print("Loading V2 state and model...")
    with open(V2_STATE) as f:
        v2 = json.load(f)
    estimator = AdaptiveWindowEstimator.load(V2_MODEL)

    detection_results = v2["detection_results"]
    interval_map = v2["interval_map"]
    opt_map = v2["opt_map"]
    extra_info = v2["extra_info"]
    v2_comparison = {row["dataset"]: row for row in v2["comparison"]}

    rows = []
    proxy_features_log: dict[str, list[float]] = {}

    for csv_str in detection_results:
        csv_path = Path(csv_str)
        ds_name = csv_path.name

        warnings = extra_info[csv_str]["warnings"]
        drift_confirms = extra_info[csv_str]["drift_confirms"]
        det_ts = detection_results[csv_str]
        intervals = [tuple(iv) for iv in interval_map[csv_str]]
        opt_ext = opt_map[csv_str]

        df = pd.read_csv(csv_path)
        X = df.drop(columns=["y"]).values.astype(float)
        y = df["y"].values.astype(float)
        stream_length = len(y)

        proxy_feats = proxy_features(warnings, drift_confirms, stream_length, X, y)
        proxy_features_log[ds_name] = proxy_feats.tolist()

        # Inference with V2 RF using proxy features
        pred_ext_proxy = estimator.predict_extension(proxy_feats)
        # V2's prediction (ground-truth features) for comparison
        pred_ext_v2 = int(v2_comparison[ds_name]["predicted_ext"])

        # Score @ each extension
        def _score(ext):
            pert = build_perturbation_intervals(intervals, extension=ext)
            r = compute_correct_detection(det_ts, pert)
            return r.score_percent if r.score_percent is not None else 0.0

        score_fixed = _score(1000)
        score_v2 = _score(pred_ext_v2)
        score_v3 = _score(pred_ext_proxy)
        score_oracle = _score(opt_ext)

        rows.append({
            "dataset": ds_name,
            "predicted_ext_v2_gt": pred_ext_v2,
            "predicted_ext_v3_proxy": pred_ext_proxy,
            "optimal_ext": opt_ext,
            "abs_diff_v2_v3": abs(pred_ext_v2 - pred_ext_proxy),
            "score_fixed": round(score_fixed, 1),
            "score_v2_gt": round(score_v2, 1),
            "score_v3_proxy": round(score_v3, 1),
            "score_oracle": round(score_oracle, 1),
        })

    df_res = pd.DataFrame(rows)
    print("\n", df_res.to_string(index=False))

    avg = {
        "fixed": df_res["score_fixed"].mean(),
        "v2_gt": df_res["score_v2_gt"].mean(),
        "v3_proxy": df_res["score_v3_proxy"].mean(),
        "oracle": df_res["score_oracle"].mean(),
    }
    print(f"\nAverages: {avg}")

    state = {
        "comparison": rows,
        "averages": avg,
        "proxy_features": proxy_features_log,
        "v2_state_used": str(V2_STATE),
        "v2_model_used": str(V2_MODEL),
    }
    state_path = OUT_DIR / "experiment_state_v3.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"\nState saved → {state_path}")


if __name__ == "__main__":
    main()
