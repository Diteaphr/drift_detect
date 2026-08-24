"""Unified sensitivity tiers: low=0.5×, medium=1×, high=2×."""

from __future__ import annotations

SENSITIVITY_TIERS = ("low", "medium", "high")

MULTIPLIER: dict[str, float] = {
    "low": 0.5,
    "medium": 1.0,
    "high": 2.0,
}


def _check_tier(tier: str) -> float:
    if tier not in MULTIPLIER:
        raise ValueError(f"Unknown sensitivity tier: {tier!r}; expected one of {SENSITIVITY_TIERS}")
    return MULTIPLIER[tier]


def scale_rate(base: float, tier: str) -> float:
    """Larger value → faster/stronger drift (incremental rates, etc.)."""
    return base * _check_tier(tier)


def scale_width_for_transition(base: int, tier: str, *, min_val: int = 20) -> int:
    """Wider transition → weaker/slower perceived drift; narrow → stronger."""
    m = _check_tier(tier)
    return max(min_val, int(round(base / m)))


def scale_int(base: int, tier: str, *, min_val: int = 1, max_val: int | None = None) -> int:
    """Integer rate parameters (e.g. n_drift_centroids)."""
    v = max(min_val, int(round(base * _check_tier(tier))))
    if max_val is not None:
        v = min(v, max_val)
    return v
