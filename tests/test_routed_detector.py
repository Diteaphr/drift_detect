"""Routing rules of RoutedConfirmDetector, driven by scripted warning/drift pairs."""

import pytest

from detectors.meta_ecpf.routed import RoutedConfirmDetector


class FakePair:
    """Replays (warning, drift) per step; drift resets nothing (the wrapper handles it)."""

    def __init__(self, script, zone=False):
        self.script = list(script)
        self.t = 0
        self.zone = zone
        self.stats = {}
        self.resets = 0
        self.warning_resets = 0

    def update_values(self, w, d):
        out = self.script[self.t] if self.t < len(self.script) else (False, False)
        self.t += 1
        return out

    def reset(self):
        self.resets += 1

    def reset_warning(self):
        self.warning_resets += 1


W, D, N, B = (True, False), (True, True), (False, False), (False, True)


def make(policy, adwin, hddma, classify=None, delay=3):
    return RoutedConfirmDetector(
        policy=policy, decision_delay=delay, classify_fn=classify,
        pairs={"adwin": FakePair(adwin), "hddma": FakePair(hddma, zone=True)},
    )


def run(det, n):
    out = []
    for t in range(n):
        det.clock = t
        out.append(det.update_values(0.0, 0.0))
    return out


def test_first_warner_waits_for_the_opener():
    # ADWIN warns at 0; HDDM-A drifts at 1 (ignored); ADWIN drifts at 3.
    det = make("first_warner", [W, N, N, D], [N, D, W, W])
    out = run(det, 4)
    assert out[:3] == [(True, False)] * 3 and out[3] == (True, True)
    ep = det.episode_log[-1]
    assert ep["opener"] == "adwin" and ep["confirmed_by"] == "adwin"
    assert ep["ignored_drifts"] == 1 and ep["end_reason"] == "confirmed"


def test_union_confirms_on_the_first_drift_of_either_pair():
    det = make("union", [W, N, N, D], [N, D, W, W])
    out = run(det, 2)
    assert out[1] == (True, True)
    assert det.episode_log[-1]["confirmed_by"] == "hddma"


def test_tie_goes_to_hddma():
    det = make("first_warner", [W, D], [W, W])
    run(det, 2)
    assert det._ep["opener"] == "hddma"  # ADWIN's drift at step 1 does not confirm


def test_type_classifier_decides_after_the_delay_and_uses_a_latched_drift():
    calls = []

    def classify():
        calls.append(1)
        return "sudden"

    # Both warn at 0 (HDDM-A opens), HDDM-A drifts at 1, decision at step 3 -> confirm then.
    det = make("type_classifier", [W, N, N, N], [W, D, W, W], classify=classify, delay=3)
    out = run(det, 4)
    assert out[1] == (True, False) and out[3] == (True, True)
    ep = det.episode_log[-1]
    assert ep["decision_type"] == "sudden" and ep["confirmed_by"] == "hddma"
    assert calls  # classifier was consulted


def test_type_classifier_keeps_an_hddma_episode_after_its_zone_closes():
    # HDDM-A warns at 0, drifts at 1 and leaves its zone; the decision at step 3 still confirms.
    det = make("type_classifier", [N] * 4, [W, D, N, N], classify=lambda: "sudden", delay=3)
    out = run(det, 4)
    assert out[2] == (True, False) and out[3] == (True, True) and det.zone is False
    assert det.episode_log[-1]["confirmed_by"] == "hddma"


def test_type_classifier_routes_non_sudden_to_adwin():
    det = make("type_classifier", [W, N, N, N, D], [N] * 5, classify=lambda: "gradual", delay=3)
    out = run(det, 5)
    assert out[3] == (True, False) and out[4] == (True, True)
    assert det.episode_log[-1]["confirmed_by"] == "adwin"


def test_hddma_episode_ends_when_hddma_leaves_its_zone():
    det = make("first_warner", [N, N, N], [W, N, N])
    out = run(det, 2)
    assert out[1] == (False, False)
    assert det.episode_log[-1]["end_reason"] == "zone_exit" and det.zone is False


def test_adwin_episode_survives_until_timeout():
    det = make("first_warner", [W, N, N], [N, N, N])
    out = run(det, 3)
    assert out == [(True, False)] * 3 and det.zone is False
    det.reset_warning()
    assert det.episode_log[-1]["end_reason"] == "timeout"
    assert all(p.warning_resets == 1 for p in det.pairs.values())


def test_discard_episode_and_reset():
    det = make("first_warner", [W, N], [N, N])
    run(det, 1)
    det.discard_episode()
    assert det.episode_log[-1]["end_reason"] == "cooldown" and det._ep is None
    run(det, 1)
    det.reset()
    assert all(p.resets == 1 for p in det.pairs.values())


@pytest.mark.parametrize("policy,pair", [("fixed_adwin", "adwin"), ("fixed_hddma", "hddma")])
def test_fixed_policies_pass_one_pair_through(policy, pair):
    adwin, hddma = [W, D, N], [N, W, D]
    det = make(policy, adwin, hddma)
    assert run(det, 3) == (adwin if pair == "adwin" else hddma)
    assert det.zone is (pair == "hddma")
    det.reset_warning()
    assert det.pairs[pair].warning_resets == 1
    assert det.episode_log == []


def test_unknown_policy_and_missing_classifier_are_rejected():
    with pytest.raises(ValueError):
        RoutedConfirmDetector(policy="nope")
    with pytest.raises(ValueError):
        RoutedConfirmDetector(policy="type_classifier")
