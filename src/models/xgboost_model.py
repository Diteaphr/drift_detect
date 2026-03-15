"""
xgboost_model.py
================
Model C — XGBoost gradient-boosted trees with a **buffer-based incremental
learning** strategy.

XGBoost is a batch algorithm and has no native ``learn_one`` method.  We
bridge this gap with the following approach:

1.  Incoming ``learn_one`` calls are accumulated in an in-memory buffer.
2.  Once the buffer reaches ``buffer_size`` samples, we trigger an incremental
    ``xgb.train()`` call using the ``xgb_model`` parameter, which continues
    training from the existing booster rather than starting from scratch.
3.  This keeps the model up-to-date while amortising the cost of tree
    construction across many samples.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import xgboost as xgb

from .base_model import BaseModel


class XGBoostModel(BaseModel):
    """XGBoost classifier with buffer-based online updates.

    Parameters
    ----------
    params : dict or None
        XGBoost booster parameters.
    num_boost_round : int
        Number of boosting rounds for initial ``fit`` and each incremental
        update.
    buffer_size : int
        How many ``learn_one`` samples to accumulate before triggering an
        incremental training step.
    """

    def __init__(
        self,
        params: Optional[Dict[str, Any]] = None,
        num_boost_round: int = 50,
        buffer_size: int = 50,
    ) -> None:
        self.params: Dict[str, Any] = params or {
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "max_depth": 4,
            "learning_rate": 0.1,
            "verbosity": 0,
        }
        self.num_boost_round = num_boost_round
        self.buffer_size = buffer_size

        self._booster: Optional[xgb.Booster] = None
        self._feature_names: Optional[List[str]] = None
        self._buffer_X: List[np.ndarray] = []
        self._buffer_y: List[float] = []

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(self, X: Any, y: Any) -> "XGBoostModel":
        X = self._to_numpy(X)
        y = np.asarray(y, dtype=np.float32).ravel()
        self._feature_names = [f"f{i}" for i in range(X.shape[1])]
        dtrain = xgb.DMatrix(X, label=y, feature_names=self._feature_names)
        self._booster = xgb.train(
            self.params,
            dtrain,
            num_boost_round=self.num_boost_round,
        )
        self._buffer_X.clear()
        self._buffer_y.clear()
        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X)
        if self._booster is None:
            return np.zeros(X.shape[0], dtype=int)
        dmat = xgb.DMatrix(X, feature_names=self._feature_names)
        probs = self._booster.predict(dmat)
        return (probs >= 0.5).astype(int)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "XGBoostModel":
        x_arr = self._dict_to_array(x)
        self._buffer_X.append(x_arr)
        self._buffer_y.append(float(y))

        if len(self._buffer_X) >= self.buffer_size:
            self._flush_buffer()
        return self

    def predict_one(self, x: Dict[str, float]) -> Any:
        x_arr = self._dict_to_array(x).reshape(1, -1)
        if self._booster is None:
            return 0
        dmat = xgb.DMatrix(x_arr, feature_names=self._feature_names)
        prob = self._booster.predict(dmat)[0]
        return int(prob >= 0.5)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _dict_to_array(self, x: Dict[str, float]) -> np.ndarray:
        if self._feature_names is None:
            self._feature_names = sorted(x.keys())
        return np.array([x.get(k, 0.0) for k in self._feature_names], dtype=np.float32)

    def _flush_buffer(self) -> None:
        X = np.vstack(self._buffer_X)
        y = np.array(self._buffer_y, dtype=np.float32)
        dtrain = xgb.DMatrix(X, label=y, feature_names=self._feature_names)

        self._booster = xgb.train(
            self.params,
            dtrain,
            num_boost_round=self.num_boost_round,
            xgb_model=self._booster,
        )
        self._buffer_X.clear()
        self._buffer_y.clear()

    def flush(self) -> "XGBoostModel":
        """Force-flush the buffer even if it is not full."""
        if self._buffer_X:
            self._flush_buffer()
        return self

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "params": self.params,
            "num_boost_round": self.num_boost_round,
            "buffer_size": self.buffer_size,
            "feature_names": self._feature_names,
            "buffer_X": self._buffer_X,
            "buffer_y": self._buffer_y,
        }
        booster_bytes: Optional[bytes] = None
        if self._booster is not None:
            booster_bytes = self._booster.save_raw()
        state["booster_raw"] = booster_bytes

        with open(path, "wb") as f:
            pickle.dump(state, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "XGBoostModel":
        with open(path, "rb") as f:
            state = pickle.load(f)
        obj = cls(
            params=state["params"],
            num_boost_round=state["num_boost_round"],
            buffer_size=state["buffer_size"],
        )
        obj._feature_names = state["feature_names"]
        obj._buffer_X = state["buffer_X"]
        obj._buffer_y = state["buffer_y"]
        if state["booster_raw"] is not None:
            obj._booster = xgb.Booster()
            obj._booster.load_model(bytearray(state["booster_raw"]))
        return obj

    def __repr__(self) -> str:
        buf = len(self._buffer_X)
        trained = self._booster is not None
        return (
            f"XGBoostModel(buffer={buf}/{self.buffer_size}, "
            f"trained={trained})"
        )
