"""
Convert instance-level prediction errors into Type-LDD 50-d relative gap features.

Training data uses window accuracies; at inference we approximate:
  window_acc = 1 - mean(error in chunk)
then the same relative-gap formula as Type-LDD preprocessing.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def errors_to_relative_gaps(
    errors: np.ndarray,
    *,
    data_vector_length: int = 50,
    instances_per_window: int = 15,
    n_accuracy_windows: Optional[int] = None,
) -> np.ndarray:
    """
    Build a fixed-length relative-gap vector from a 1D error sequence.

    Parameters
    ----------
    errors :
        Per-instance errors (0/1 or absolute error). Recent history preferred.
    data_vector_length :
        Output length (Type-LDD default 50).
    instances_per_window :
        Chunk size for windowed accuracy (~15 in their data gen).
    n_accuracy_windows :
        How many accuracy points to form before taking gaps.
        Default: data_vector_length + 1 (so gaps length == data_vector_length).
    """
    errs = np.asarray(errors, dtype=np.float64).ravel()
    if n_accuracy_windows is None:
        n_accuracy_windows = data_vector_length + 1

    need = n_accuracy_windows * instances_per_window
    if len(errs) == 0:
        return np.zeros(data_vector_length, dtype=np.float64)

    if len(errs) < need:
        pad_val = float(errs[0])
        errs = np.concatenate(
            [np.full(need - len(errs), pad_val, dtype=np.float64), errs]
        )
    else:
        errs = errs[-need:]

    acc = []
    for i in range(n_accuracy_windows):
        chunk = errs[i * instances_per_window : (i + 1) * instances_per_window]
        mean_err = float(np.mean(chunk)) if len(chunk) else 0.0
        mean_err = float(np.clip(mean_err, 0.0, 1.0))
        acc.append(1.0 - mean_err)
    acc = np.asarray(acc, dtype=np.float64)

    prev = acc[:-1]
    nxt = acc[1:]
    with np.errstate(divide="ignore", invalid="ignore"):
        gaps = (nxt - prev) / prev
    gaps = np.nan_to_num(gaps, nan=0.0, posinf=0.0, neginf=0.0)

    if len(gaps) < data_vector_length:
        gaps = np.concatenate(
            [gaps, np.zeros(data_vector_length - len(gaps), dtype=np.float64)]
        )
    else:
        gaps = gaps[:data_vector_length]
    return gaps.astype(np.float64)
