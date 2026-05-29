"""Detection delay metric for offline drift detector evaluation."""

from __future__ import annotations

import math
from typing import Dict, List, Sequence


def compute_detection_delays(
    warning_timestamps: Sequence[int],
    true_drift_starts: Sequence[int],
    *,
    tolerance: int = 2000,
) -> Dict[str, object]:
    """Match each true drift to the earliest warning in [start, start+tolerance].

    Each true drift is matched at most once; each warning is used at most once.
    Delay is measured in samples from true_drift_start to the matched warning.

    Returns a dict with keys:
        delays       - list of per-drift delays (only matched drifts)
        mean_delay   - float mean delay, or nan if no matches
        n_matched    - number of true drifts successfully matched
        n_missed     - number of true drifts with no warning in tolerance window
        n_actual     - total true drifts
        n_warnings   - total warnings emitted
    """
    alerts = sorted(warning_timestamps)
    used: set[int] = set()  # indices into alerts
    delays: List[int] = []
    n_missed = 0

    for t_true in sorted(true_drift_starts):
        window_end = t_true + tolerance
        matched_idx = None
        for i, a in enumerate(alerts):
            if a < t_true:
                continue
            if a > window_end:
                break
            if i not in used:
                matched_idx = i
                break
        if matched_idx is not None:
            used.add(matched_idx)
            delays.append(alerts[matched_idx] - t_true)
        else:
            n_missed += 1

    mean_delay = float(sum(delays)) / len(delays) if delays else math.nan
    return {
        "delays": delays,
        "mean_delay": mean_delay,
        "n_matched": len(delays),
        "n_missed": n_missed,
        "n_actual": len(list(true_drift_starts)),
        "n_warnings": len(alerts),
    }
