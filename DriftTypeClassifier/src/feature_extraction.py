"""
Feature extraction around drift alert timestamps: gap sequence (paper-style) + optional extra features.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any


def extract_gap_sequence(
    errors: np.ndarray,
    t_alert: int,
    pre_window: int = 150,
    post_window: int = 150,
    n_subwindows: int = 15,
) -> np.ndarray:
    """
    Paper-style: window [t_alert - pre_window, t_alert + post_window],
    split into n_subwindows, compute mean error per subwindow, then gaps = diff(means).
    Returns shape (n_subwindows - 1,) or (n_subwindows,) with last gap zero-padded if needed.
    """
    n = len(errors)
    start = max(0, t_alert - pre_window)
    end = min(n, t_alert + post_window)
    window_errors = errors[start:end]
    if len(window_errors) == 0:
        return np.zeros(n_subwindows - 1, dtype=np.float64)
    sub_len = max(1, len(window_errors) // n_subwindows)
    means = []
    for j in range(n_subwindows):
        beg = j * sub_len
        fin = min((j + 1) * sub_len, len(window_errors))
        if beg < fin:
            means.append(np.mean(window_errors[beg:fin]))
        else:
            means.append(means[-1] if means else 0.0)
    means = np.array(means, dtype=np.float64)
    gaps = np.diff(means)
    return gaps


def extract_extra_features(
    errors: np.ndarray,
    t_alert: int,
    pre_window: int = 150,
    post_window: int = 150,
) -> np.ndarray:
    """Extra scalar features: mean before/after, max jump, slope, variance, etc."""
    n = len(errors)
    start = max(0, t_alert - pre_window)
    end = min(n, t_alert + post_window)
    before = errors[max(0, t_alert - pre_window) : t_alert]
    after = errors[t_alert : min(n, t_alert + post_window)]
    mean_before = float(np.mean(before)) if len(before) > 0 else 0.0
    mean_after = float(np.mean(after)) if len(after) > 0 else 0.0
    window = errors[start:end]
    max_jump = 0.0
    if len(window) > 1:
        jumps = np.abs(np.diff(window))
        max_jump = float(np.max(jumps))
    slope_before = 0.0
    if len(before) > 1:
        slope_before = float(np.polyfit(np.arange(len(before)), before, 1)[0])
    slope_after = 0.0
    if len(after) > 1:
        slope_after = float(np.polyfit(np.arange(len(after)), after, 1)[0])
    var_before = float(np.var(before)) if len(before) > 1 else 0.0
    var_after = float(np.var(after)) if len(after) > 1 else 0.0
    cum_increase = mean_after - mean_before
    return np.array([
        mean_before, mean_after, max_jump,
        slope_before, slope_after, var_before, var_after, cum_increase,
    ], dtype=np.float64)


def extract_features(
    errors: np.ndarray,
    t_alert: int,
    pre_window: int = 150,
    post_window: int = 150,
    n_subwindows: int = 15,
    use_extra_features: bool = False,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Extract feature vector for one alert.
    Returns (features, meta). features: gap sequence only, or gap + extra concatenated.
    """
    gaps = extract_gap_sequence(
        errors, t_alert, pre_window, post_window, n_subwindows,
    )
    if not use_extra_features:
        return gaps, {"gap_len": len(gaps)}
    extra = extract_extra_features(errors, t_alert, pre_window, post_window)
    features = np.concatenate([gaps, extra])
    return features, {"gap_len": len(gaps), "extra_len": len(extra)}


def extract_features_batch(
    errors_list: list,
    t_alert_list: list,
    pre_window: int = 150,
    post_window: int = 150,
    n_subwindows: int = 15,
    use_extra_features: bool = False,
) -> Tuple[np.ndarray, list]:
    """
    Extract features for multiple (errors, t_alert) pairs.
    Returns (X, meta_list) where X is (n_samples, feat_dim).
    """
    X_list = []
    meta_list = []
    for errors, t_alert in zip(errors_list, t_alert_list):
        feat, meta = extract_features(
            errors, t_alert, pre_window, post_window, n_subwindows, use_extra_features,
        )
        X_list.append(feat)
        meta_list.append(meta)
    # Pad to same length if needed
    max_len = max(len(x) for x in X_list)
    X = np.zeros((len(X_list), max_len), dtype=np.float64)
    for i, x in enumerate(X_list):
        X[i, : len(x)] = x
    return X, meta_list
