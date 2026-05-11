"""HCDT controller for ECPF warning and drift confirmation."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np

from detectors.core.unified import HDDM_A, HDDM_W, RDDM


class HCDTECPFDetector:
    """Hierarchical Change-Detection Tests integrated with ECPF.

    The core HDDM/RDDM implementations live in ``detectors.core``.  This class
    owns only the ECPF-level policy: two-layer configuration, warning state,
    validation activation, false-positive cancellation, cooldown, and stats.
    """

    def __init__(self, config=None) -> None:
        self.config = config
        self.detection_layer_name = str(
            getattr(config, "ecpf_hcdt_detection_layer", "hddm_a")
        )
        self.validation_layer_name = str(
            getattr(config, "ecpf_hcdt_validation_layer", "rddm")
        )
        if self.validation_layer_name.lower() != "rddm":
            raise ValueError("HCDT currently supports validation_layer='rddm'.")

        self.min_confirmation_age = int(
            getattr(config, "ecpf_hcdt_min_confirmation_age", getattr(config, "ecpf_warning_length", 60))
        )
        self.warning_timeout = int(getattr(config, "ecpf_hcdt_warning_timeout", 1000))
        self.cooldown_duration = int(getattr(config, "ecpf_hcdt_cooldown", 200))
        self.cooldown_until: Optional[int] = None
        self.detection_threshold = float(
            getattr(config, "ecpf_hcdt_detection_threshold", 0.06)
        )

        self.detection_layer = self._build_detection_layer()
        self.validation_layer = RDDM(
            min_samples=int(getattr(config, "ecpf_hcdt_validation_min_samples", 30)),
            warning_level=float(getattr(config, "ecpf_hcdt_rddm_warning_level", 2.0)),
            drift_level=float(getattr(config, "ecpf_hcdt_rddm_drift_level", 3.0)),
            max_warning_length=int(getattr(config, "ecpf_hcdt_rddm_max_warning_length", 400)),
        )

        self.warning_active = False
        self.first_warning_t: Optional[int] = None
        self.n_warnings = 0
        self.n_drifts = 0
        self.n_false_positives = 0

    def _build_detection_layer(self):
        name = self.detection_layer_name.lower().replace("-", "_")
        kwargs = {
            "min_samples": int(getattr(self.config, "ecpf_hcdt_detection_min_samples", 30)),
            "delta": float(getattr(self.config, "ecpf_hcdt_detection_delta", 0.005)),
            "lambda_": float(getattr(self.config, "ecpf_hcdt_detection_lambda", 0.999)),
        }
        if name in {"hddm", "hddm_a"}:
            return HDDM_A(**kwargs)
        if name == "hddm_w":
            return HDDM_W(**kwargs)
        raise ValueError(f"HCDT detection layer must be hddm_a or hddm_w, got {self.detection_layer_name!r}.")

    def _detection_score(self) -> Optional[float]:
        if hasattr(self.detection_layer, "_p_short") and hasattr(self.detection_layer, "_p_long"):
            return abs(float(self.detection_layer._p_short) - float(self.detection_layer._p_long))
        if hasattr(self.detection_layer, "_p0") and hasattr(self.detection_layer, "_p1"):
            return abs(float(self.detection_layer._p0) - float(self.detection_layer._p1))
        return None

    def _detection_drift(self) -> bool:
        score = self._detection_score()
        count = int(getattr(self.detection_layer, "_count", len(getattr(self.detection_layer, "_errors", []))))
        if score is not None and count >= int(getattr(self.detection_layer, "min_samples", 0)):
            return score >= self.detection_threshold
        return bool(self.detection_layer.detect())

    def _detection_stats(self, drift: bool) -> Dict[str, Any]:
        score = self._detection_score()
        stats: Dict[str, Any] = {
            "detector": self.detection_layer_name,
            "warning": bool(drift),
            "drift": bool(drift),
            "score": score,
            "threshold": self.detection_threshold,
        }
        for attr in ("_count", "_p_short", "_p_long", "_p0", "_p1"):
            if hasattr(self.detection_layer, attr):
                stats[attr.lstrip("_")] = getattr(self.detection_layer, attr)
        return stats

    def _zero_one_loss(self, y_true: float, y_pred: float, err: float) -> float:
        try:
            return float(int(round(float(y_pred))) != int(round(float(y_true))))
        except Exception:
            return 1.0 if float(err) > 0.5 else 0.0

    def _reset_warning_state(self) -> None:
        self.warning_active = False
        self.first_warning_t = None
        self.validation_layer.reset()

    def update_and_detect(
        self,
        x: np.ndarray,
        y_true: float,
        y_pred: float,
        err: float,
        t: int,
        **kwargs,
    ) -> Tuple[bool, int, Dict[str, Any]]:
        err01 = self._zero_one_loss(y_true, y_pred, err)
        in_cooldown = self.cooldown_until is not None and t < self.cooldown_until

        self.detection_layer.update(err01)
        detection_drift = self._detection_drift()
        detection_stats = self._detection_stats(detection_drift)
        warning_event = bool(detection_drift and not self.warning_active and not in_cooldown)
        if warning_event:
            self.warning_active = True
            self.first_warning_t = int(t)
            self.n_warnings += 1

        validation_warning = False
        validation_drift = False
        self.validation_layer.update(err01)
        validation_drift, validation_warning = self.validation_layer.detect()
        validation_stats = self.validation_layer.stats()
        validation_stats.update(
            {
                "warning": bool(validation_warning),
                "drift": bool(validation_drift),
            }
        )

        warning_age = None
        if self.warning_active and self.first_warning_t is not None:
            warning_age = int(t) - self.first_warning_t

        timeout_false_positive = bool(
            self.warning_active
            and warning_age is not None
            and warning_age > self.warning_timeout
        )
        rddm_reconfigure = bool(self.warning_active and validation_stats.get("reconfigure", False))
        false_positive = bool(timeout_false_positive or rddm_reconfigure)

        min_age_met = warning_age is not None and warning_age >= self.min_confirmation_age
        global_drift = bool(
            self.warning_active
            and min_age_met
            and validation_drift
            and not false_positive
        )

        stats = {
            "proxy_indicators": {
                "any_warning": warning_event,
                "confirmed_warning": warning_event,
                "warning_active": self.warning_active and not false_positive,
                "warning_age": warning_age,
                "min_confirmation_age": self.min_confirmation_age,
                "cooldown_until": self.cooldown_until,
                "in_cooldown": in_cooldown,
                "raw_any_warning": bool(detection_drift),
                "policy": "hcdt_detection_then_validation",
                "first_warning_t": self.first_warning_t,
                "false_positive": false_positive,
                "details": {
                    "detection_layer": detection_stats,
                    "validation_layer": validation_stats,
                },
            },
            "ensemble_results": {
                "detection_warning": bool(detection_drift),
                "validation_drift": validation_drift,
            },
            "dynamic_weights": {},
            "meta_info": {
                "score_ratio": 1.0 if global_drift else 0.0,
                "strategy_used": "hcdt_ecpf",
                "detection_layer": self.detection_layer_name,
                "validation_layer": self.validation_layer_name,
                "validation_passed": validation_drift,
                "false_positive": false_positive,
                "warning_start_t": self.first_warning_t,
                "confirmation_t": int(t) if global_drift else None,
            },
        }

        if global_drift:
            self.n_drifts += 1
            self._reset_warning_state()
            self.detection_layer.reset()
            self.cooldown_until = int(t) + self.cooldown_duration
        elif false_positive:
            self.n_false_positives += 1
            self._reset_warning_state()
            self.cooldown_until = int(t) + self.cooldown_duration

        return global_drift, int(t), stats

    def reset(self) -> None:
        self.detection_layer.reset()
        self.validation_layer.reset()
        self.warning_active = False
        self.first_warning_t = None
        self.cooldown_until = None

    def notify_drift(self, **kwargs) -> None:
        self.reset()
