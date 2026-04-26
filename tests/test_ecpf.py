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
