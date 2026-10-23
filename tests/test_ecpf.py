"""Unit tests for ECPF (no full pipeline import if optional deps missing)."""

import numpy as np

from src.ecpf import ECPFMetaLearner
from src.prediction_model import PredictionModel


def test_ecpf_on_drift_smoke():
    pm = PredictionModel("linear")
    rng = np.random.default_rng(0)
    X = rng.standard_normal((200, 2))
    y = (X[:, 0] + X[:, 1] > 0).astype(float)
    pm.fit(X[:50], y[:50])
    ec = ECPFMetaLearner(
        similarity_margin=0.95,
        fade_points=15,
        model_check_freq=1,
        fade_enabled=True,
        use_advanced=False,
        model_type="linear",
    )
    ec.bootstrap_first_expert(pm)
    buf = [(X[i], y[i]) for i in range(50, 110)]
    det = ec.on_drift(pm, buf)
    assert det["buffer_len"] == 60
    assert det["collection_size"] >= 1


def test_ecpf_stream_duel_counts():
    pm = PredictionModel("linear")
    rng = np.random.default_rng(1)
    X = rng.standard_normal((30, 2))
    y = (X[:, 0] > 0).astype(float)
    pm.fit(X[:10], y[:10])
    ec = ECPFMetaLearner(use_advanced=False, model_type="linear")
    ec.bootstrap_first_expert(pm)
    ec.new_model = PredictionModel("linear")
    ec.new_model.fit(X[:10], y[:10])
    for i in range(10, 20):
        yp = float(pm.predict(X[i : i + 1])[0])
        ec.on_stream_instance(pm, X[i], float(y[i]), y_pred_leader=yp)
    assert ec.total_inst == 10


def _duel_learner(swap_policy, **kw):
    """ECPF with a leader and a shadow ready to duel (counters set by hand)."""
    pm = PredictionModel("linear")
    rng = np.random.default_rng(2)
    X = rng.standard_normal((20, 2))
    y = (X[:, 0] > 0).astype(float)
    pm.fit(X, y)
    ec = ECPFMetaLearner(use_advanced=False, model_type="linear", swap_policy=swap_policy, **kw)
    ec.bootstrap_first_expert(pm)
    ec.new_model = PredictionModel("linear")
    ec.new_model.fit(X, y)
    return ec, pm


def test_hoeffding_swap_ignores_small_lead():
    strict, pm_s = _duel_learner("strict")
    hoeff, pm_h = _duel_learner("hoeffding", swap_delta=0.05)
    for ec in (strict, hoeff):
        ec.curr_correct, ec.new_correct, ec.total_inst = 50, 51, 60
    strict._compare_classifiers(pm_s)
    hoeff._compare_classifiers(pm_h)
    assert strict.leader_swaps == 1
    assert hoeff.leader_swaps == 0


def test_hoeffding_swap_accepts_clear_lead():
    ec, pm = _duel_learner("hoeffding", swap_delta=0.05)
    # lead 0.4 > eps = sqrt(2 ln 20 / 200) ~= 0.173
    ec.curr_correct, ec.new_correct, ec.total_inst = 100, 180, 200
    ec._compare_classifiers(pm)
    assert ec.leader_swaps == 1
    assert ec._leader_is_reused is False


def test_reuse_value_credits_source_slot():
    pm = PredictionModel("linear")
    rng = np.random.default_rng(3)
    X = rng.standard_normal((400, 2))
    y = (X[:, 0] + X[:, 1] > 0).astype(float)
    pm.fit(X[:50], y[:50])
    ec = ECPFMetaLearner(
        use_advanced=False, model_type="linear", fade_policy="reuse_value",
        reuse_value_window=100, fade_points=15,
    )
    ec.bootstrap_first_expert(pm)
    ec.on_drift(pm, [(X[i], y[i]) for i in range(50, 110)])
    src = ec._reuse_source
    assert src is not None
    # Pretend the reused copy beat the fresh learner by 30 over the window.
    ec._rv_reused_correct, ec._rv_fresh_correct, ec._rv_n = 95, 65, 100
    before = ec.fade_scores.get(src, 0)
    det = ec.on_drift(pm, [(X[i], y[i]) for i in range(110, 170)])
    assert det["reuse_value"] == 30
    assert det["reuse_value_source"] == src
    if ec.slots[src] is not None:
        # +30 credit, then idle cost 1 if it is not the leader any more
        assert ec.fade_scores[src] >= before + 30 - 1


# ----------------------------------------------------------------------
# Memory-aware fade policies
# ----------------------------------------------------------------------
def _stream_ec(policy, n_drifts=6, **kw):
    """Linear experts on a stream whose concept flips every segment."""
    pm = PredictionModel("linear")
    rng = np.random.default_rng(1)
    X = rng.standard_normal((200 * (n_drifts + 1), 2))
    sign = np.repeat([1.0, -1.0] * (n_drifts + 1), 200)[: len(X)]
    y = (sign * (X[:, 0] + X[:, 1]) > 0).astype(float)
    pm.fit(X[:50], y[:50])
    ec = ECPFMetaLearner(model_type="linear", fade_policy=policy, reuse_value_window=50,
                         pool_trace=True, **kw)
    ec.bootstrap_first_expert(pm)
    for t in range(50, len(X)):
        ec.clock = t
        if t % 200 == 0:
            ec.on_drift(pm, [(X[i], y[i]) for i in range(t - 60, t)])
        else:
            ec.on_stream_instance(pm, X[t], y[t])
    return ec


def test_every_fade_policy_runs_and_traces():
    from src.ecpf import FADE_POLICIES

    for policy in FADE_POLICIES:
        ec = _stream_ec(policy)
        tr = ec.pool_trace_dict()
        assert tr["num_drifts"] == 6
        assert tr["timeline"], policy
        assert all(kb > 0 for _, _, kb in tr["timeline"])
        assert len(tr["reuse_values"]) == 5


def test_memory_budget_caps_stored_kb():
    ec = _stream_ec("density", memory_budget_factor=1.5)
    assert ec.pool_kb() <= 1.5 * ec.slot_kb[ec.current_idx] + 1e-9
    assert any(e["reason"] == "budget" for e in ec.eviction_log)


def test_rent_charges_by_size():
    ec = ECPFMetaLearner(model_type="linear", fade_policy="rent", fade_lambda=2.0)
    ec.slots = [object(), object(), object()]
    ec.slot_stats = [None] * 3
    ec.slot_kb = {0: 10.0, 1: 30.0, 2: 20.0}  # mean 20
    ec.fade_scores = {0: 10.0, 1: 2.0, 2: 10.0}
    ec.current_idx = 2
    ec._fade_models()
    assert ec.fade_scores[0] == 9.0      # 10 - 2 * 10/20
    assert ec.slots[1] is None           # 2 - 2 * 30/20 < 0 -> evicted
    assert ec.fade_scores[2] == 15       # leader grace


def test_density_evicts_lowest_value_per_kb():
    ec = ECPFMetaLearner(model_type="linear", fade_policy="density", max_pool_size=2)
    ec.slots = [object(), object(), object()]
    ec.slot_stats = [None] * 3
    ec.slot_kb = {0: 100.0, 1: 10.0, 2: 10.0}
    ec.fade_scores = {0: 30.0, 1: 8.0, 2: 15.0}   # 0.3/KB vs 0.8/KB
    ec.current_idx = 2
    ec._enforce_pool_cap()
    assert ec.slots[0] is None and ec.slots[1] is not None


def test_decay_shrinks_idle_credit():
    ec = ECPFMetaLearner(model_type="linear", fade_policy="decay", decay_gamma=0.5)
    ec.slots = [object(), object()]
    ec.slot_stats = [None] * 2
    ec.fade_scores = {0: 20.0, 1: 15.0}
    ec.current_idx = 1
    ec._fade_models()
    assert ec.fade_scores[0] == 9.0      # 0.5 * 20 - 1


def test_default_policy_measures_nothing():
    ec = _stream_ec("ecpf")
    ec_plain = ECPFMetaLearner(model_type="linear")
    assert not ec_plain._track_sizes
