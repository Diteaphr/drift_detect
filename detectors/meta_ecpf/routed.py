"""Routed confirmation: ADWIN and HDDM-A warn in parallel, a rule picks who confirms.

Two warning/confirm pairs run side by side on the same signal, each built exactly
like its DET4 diagonal (``det4_s1_wadwin_cadwin`` / ``det4_s1_whddma_chddma``):
the dual ADWIN of ``ECPFWarningDriftDetector`` and the HDDM-A/HDDM-A
``ECPFAdwinFamilyDetector``. A warning *episode* opens when either pair warns
(or drifts); a routing policy decides whose drift confirms it:

* ``first_warner``: the pair that warned first confirms (a tie goes to HDDM-A).
* ``type_classifier``: after ``decision_delay`` steps of the episode the
  drift-type classifier runs; ``sudden`` -> HDDM-A confirms, otherwise ADWIN.
* ``union``: either pair's drift confirms.
* ``hddma_gate``: an ADWIN drift confirms at once; an HDDM-A drift runs the
  classifier at that step -- ``sudden`` confirms at once, otherwise HDDM-A is
  vetoed for the rest of the episode and only ADWIN can confirm.
* ``fixed_adwin`` / ``fixed_hddma``: pass one pair's output through unchanged
  (reproduces the DET4 diagonals; used as the reproducibility gate).

A drift from the pair that is not (or not yet) the confirmer is remembered for
the episode, so a drift that fired before the type decision still confirms at
the decision step, and drifts from the other pair are logged as ignored.

Zone semantics follow the opener, as DET4 derives them from the warning arm:
an episode opened by HDDM-A ends when HDDM-A leaves its warning zone without a
confirmation (the pipeline then drops the buffer); an ADWIN episode lasts until
confirmation or the pipeline's warning timeout. ``type_classifier`` episodes
never end on a zone exit, so the decision always gets its ``decision_delay``
steps; a ``hddma_gate`` episode stops ending on a zone exit once HDDM-A is
vetoed, so it can wait for ADWIN. The pipeline's warning timeout
calls :meth:`reset_warning`; its post-confirmation cooldown calls
:meth:`discard_episode`.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from .adwin_family import ECPFAdwinFamilyDetector

POLICIES = ("first_warner", "type_classifier", "union", "hddma_gate", "fixed_adwin", "fixed_hddma")
NEEDS_CLASSIFIER = ("type_classifier", "hddma_gate")
PAIRS = ("adwin", "hddma")
# Classifications recorded for analysis only (steps after the episode opened).
OBSERVE_AT = (100, 200, 300)


class RoutedConfirmDetector:
    def __init__(
        self,
        *,
        policy: str,
        decision_delay: int = 100,
        min_num_instances: int = 30,
        delta: float = 0.05,
        delta_w: float = 0.1,
        one_sided: bool = False,
        random_seed: int = 42,
        warning_value_range: float = 1.0,
        drift_value_range: float = 1.0,
        classify_fn: Optional[Callable[[], str]] = None,
        pairs: Optional[Dict[str, Any]] = None,
    ) -> None:
        if policy not in POLICIES:
            raise ValueError(f"ecpf_route_policy must be one of {POLICIES}, got {policy!r}")
        if policy in NEEDS_CLASSIFIER and classify_fn is None:
            raise ValueError(f"{policy} routing needs a classify_fn")
        self.policy = policy
        self.decision_delay = max(1, int(decision_delay))
        self.classify_fn = classify_fn
        if pairs is None:
            # ADWIN pair = ECPFWarningDriftDetector; HDDM-A pair = the family detector the
            # pipeline builds for ecpf_warning_detector = ecpf_drift_detector = "hddm_a".
            pairs = {
                "adwin": ECPFAdwinFamilyDetector(
                    warning_detector_type="adwin", drift_detector_type="adwin",
                    min_num_instances=min_num_instances, delta=delta, delta_w=delta_w,
                    one_sided=one_sided,
                ),
                "hddma": ECPFAdwinFamilyDetector(
                    warning_detector_type="hddm_a", drift_detector_type="hddm_a",
                    min_num_instances=min_num_instances, delta=delta, delta_w=delta_w,
                    random_seed=random_seed, warning_value_range=warning_value_range,
                    drift_value_range=drift_value_range, one_sided=one_sided,
                ),
            }
        self.pairs = pairs
        self.clock: int = 0  # stream index, set by the pipeline before each update
        self.stats: Dict[str, Any] = {}
        self.episode_log: List[Dict[str, Any]] = []
        self._ep: Optional[Dict[str, Any]] = None

    # -- interface the pipeline uses -------------------------------------------------
    @property
    def combo_name(self) -> str:
        return f"routed_{self.policy}"

    @property
    def zone(self) -> bool:
        fixed = self._fixed_pair()
        if fixed is not None:
            return bool(self.pairs[fixed].zone)
        return self._zone_applies()

    def reset(self) -> None:
        """Both pairs restart (pipeline: after a confirmation, guard included)."""
        self._end_episode("reset")
        for pair in self.pairs.values():
            pair.reset()

    def reset_warning(self) -> None:
        """Pipeline warning timeout: close the episode, re-baseline the warning arms."""
        fixed = self._fixed_pair()
        if fixed is not None:
            self.pairs[fixed].reset_warning()
            return
        self._end_episode("timeout")
        for pair in self.pairs.values():
            pair.reset_warning()

    def discard_episode(self) -> None:
        """Pipeline cooldown: forget an episode opened while warnings are suppressed."""
        if self._ep is not None:
            self._end_episode("cooldown")

    def finish(self) -> None:
        """Stream end: record an episode that is still open."""
        if self._ep is not None:
            self._end_episode("stream_end")

    def update_values(self, warning_value: float, drift_value: float) -> Tuple[bool, bool]:
        out = {name: pair.update_values(warning_value, drift_value) for name, pair in self.pairs.items()}
        fixed = self._fixed_pair()
        if fixed is not None:
            self.stats = dict(self.pairs[fixed].stats, route_policy=self.policy)
            return out[fixed]

        (wa, da), (wh, dh) = out["adwin"], out["hddma"]
        opened_now = False
        if self._ep is None and (wa or wh or da or dh):
            opener = "hddma" if (wh or dh) else "adwin"
            self._ep = {
                "open_t": int(self.clock), "opener": opener, "steps": 0,
                "confirmer": {"first_warner": opener, "union": "any"}.get(self.policy),
                "decision_t": None, "decision_type": None, "observed_types": {},
                "first_drift_t": {"adwin": None, "hddma": None}, "ignored_drifts": 0,
                "both_warned_at_open": bool((wa or da) and (wh or dh)),
            }
            opened_now = True
        ep = self._ep
        if ep is None:
            self.stats = {"route_policy": self.policy}
            return False, False

        if not opened_now:
            ep["steps"] += 1
        for name, fired in (("adwin", da), ("hddma", dh)):
            if fired and ep["first_drift_t"][name] is None:
                ep["first_drift_t"][name] = int(self.clock)
        self._observe_type(ep)

        if self.policy == "type_classifier" and ep["confirmer"] is None and ep["steps"] >= self.decision_delay:
            kind = ep["observed_types"].get(self.decision_delay) or self.classify_fn()
            ep["decision_t"], ep["decision_type"] = int(self.clock), kind
            ep["confirmer"] = "hddma" if kind == "sudden" else "adwin"

        if self.policy == "hddma_gate":
            return self._gate_step(ep, da, dh, wh)

        confirmer = ep["confirmer"]
        emit = False
        if confirmer == "any":
            emit = ep["first_drift_t"]["adwin"] is not None or ep["first_drift_t"]["hddma"] is not None
        elif confirmer is not None:
            emit = ep["first_drift_t"][confirmer] is not None
            other = "hddma" if confirmer == "adwin" else "adwin"
            if (da if other == "adwin" else dh):
                ep["ignored_drifts"] += 1
        self.stats = {"route_policy": self.policy, "route_opener": ep["opener"],
                      "route_confirmer": confirmer, "route_type": ep["decision_type"]}
        if emit:
            if self.classify_fn is not None:
                ep["observed_types"]["confirm"] = self.classify_fn()
            self._end_episode("confirmed")
            for pair in self.pairs.values():
                pair.reset()
            return True, True

        if self._zone_applies() and not wh:
            # HDDM-A left its warning zone: the pipeline closes the warning this step.
            self._end_episode("zone_exit")
            return False, False
        return True, False

    # -- helpers ------------------------------------------------------------------
    def _gate_step(self, ep: Dict[str, Any], da: bool, dh: bool, wh: bool) -> Tuple[bool, bool]:
        """``hddma_gate``: ADWIN confirms at once; an HDDM-A drift is classified on the spot."""
        by = None
        if dh and ep["confirmer"] is None:
            kind = self.classify_fn()
            ep["decision_t"], ep["decision_type"] = int(self.clock), kind
            ep["confirmer"] = "hddma" if kind == "sudden" else "adwin"
            if kind == "sudden":
                by = "hddma"
        elif dh:
            ep["ignored_drifts"] += 1
        if by is None and ep["first_drift_t"]["adwin"] is not None:
            by = "adwin"
        self.stats = {"route_policy": self.policy, "route_opener": ep["opener"],
                      "route_confirmer": ep["confirmer"], "route_type": ep["decision_type"]}
        if by is not None:
            ep["confirmer"] = by
            ep["observed_types"]["confirm"] = ep["decision_type"] if by == "hddma" else self.classify_fn()
            self._end_episode("confirmed")
            for pair in self.pairs.values():
                pair.reset()
            return True, True
        if self._zone_applies() and not wh:
            self._end_episode("zone_exit")
            return False, False
        return True, False

    def _zone_applies(self) -> bool:
        """An HDDM-A episode ends when HDDM-A leaves its zone -- except under
        ``type_classifier``, which must keep the episode for ``decision_delay``
        steps (HDDM-A's zone usually closes within a few steps, often right after
        its own drift), so its episodes end only by confirmation or timeout."""
        return (self._ep is not None and self._ep["opener"] == "hddma"
                and self.policy != "type_classifier"
                and not (self.policy == "hddma_gate" and self._ep["confirmer"] == "adwin"))

    def _fixed_pair(self) -> Optional[str]:
        return {"fixed_adwin": "adwin", "fixed_hddma": "hddma"}.get(self.policy)

    def _observe_type(self, ep: Dict[str, Any]) -> None:
        if self.classify_fn is None:
            return
        for at in OBSERVE_AT:
            if ep["steps"] == at and at not in ep["observed_types"]:
                ep["observed_types"][at] = self.classify_fn()

    def _end_episode(self, reason: str) -> None:
        ep = self._ep
        if ep is None:
            return
        drifts = ep["first_drift_t"]
        if reason == "confirmed":
            by = ep["confirmer"]
            if by == "any":
                hits = [(t, name) for name, t in drifts.items() if t is not None]
                by = min(hits)[1]
            ep["confirmed_by"] = by
        ep.update(end_t=int(self.clock), end_reason=reason,
                  observed_types={str(k): v for k, v in ep["observed_types"].items()})
        self.episode_log.append(ep)
        self._ep = None
