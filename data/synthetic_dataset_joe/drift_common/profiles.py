"""Resolve drift parameters per task, drift type, and sensitivity tier."""

from __future__ import annotations

from drift_common.sensitivity import (
    MULTIPLIER,
    scale_int,
    scale_rate,
    scale_width_for_transition,
)

# Medium-tier baseline constants (single source of truth)
SUDDEN_WIDTH = 80
GRADUAL_WIDTH_BINARY = 10_000
GRADUAL_WIDTH_MULTICLASS = 8_000
INCR_CHANGE_SPEED = 0.01
INCR_N_DRIFT_CENTROIDS = 45
INCR_PARAM_STEP = 8e-8
N_CENTROIDS_MULTICLASS = 50


def resolve(task: str, drift_type: str, tier: str) -> dict:
    """
    Return parameters for one (task, drift_type, tier) combination.

    Keys vary by drift_type:
    - sudden/gradual: width, sensitivity, sensitivity_multiplier
    - incremental: change_speed, n_drift_centroids (multiclass) or param_step (regression)
    """
    if tier not in MULTIPLIER:
        raise ValueError(f"Unknown tier: {tier!r}")

    mult = MULTIPLIER[tier]
    base: dict = {
        "sensitivity": tier,
        "sensitivity_multiplier": mult,
    }

    if drift_type == "sudden":
        if task == "regression":
            base["jump_scale"] = mult
            return base
        base["width"] = scale_width_for_transition(SUDDEN_WIDTH, tier)
        return base

    if drift_type == "gradual":
        if task == "binary":
            gw = GRADUAL_WIDTH_BINARY
        elif task == "multiclass":
            gw = GRADUAL_WIDTH_MULTICLASS
        elif task == "regression":
            # Regression gradual uses per-run random tw; flag for post-scale
            base["scale_transition_window"] = True
            return base
        else:
            raise ValueError(f"Unknown task: {task!r}")
        base["width"] = scale_width_for_transition(gw, tier)
        return base

    if drift_type == "incremental":
        if task == "multiclass":
            base["change_speed"] = scale_rate(INCR_CHANGE_SPEED, tier)
            base["n_drift_centroids"] = scale_int(
                INCR_N_DRIFT_CENTROIDS,
                tier,
                min_val=1,
                max_val=N_CENTROIDS_MULTICLASS,
            )
        elif task == "regression":
            base["param_step"] = scale_rate(INCR_PARAM_STEP, tier)
            base["jump_scale"] = mult
        else:
            raise ValueError(f"Task {task!r} has no incremental drift")
        return base

    if drift_type == "sudden" and task == "regression":
        base["jump_scale"] = mult
        return base

    raise ValueError(f"Unknown (task, drift_type): ({task!r}, {drift_type!r})")
