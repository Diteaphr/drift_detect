"""
Enhanced Concept Profiling Framework (ECPF), Anderson et al. (TKDE).

Reference: paper Algorithm 1 / MOA ``ECPF.java`` (rand079/CPF).
Default hyperparameters match the paper's experiments: similarity m = 0.95,
fade points f = 15, model-check frequency = 1.

The pipeline can drive drift timing in two ways:

* ``oracle_60`` — synthetic protocol from the paper: enter WARNING at each
  *true* drift index ``T`` (user-supplied), accumulate exactly ``warning_length``
  instances (default 60), then run the ECPF drift handler on that buffer.
* ``meta_retro_60`` — when the meta-detector fires drift at ``T``, use the last
  ``warning_length`` ``(x, y)`` tuples ending at ``T`` as the warning buffer
  (approximates a fixed-length warning period without a separate warning signal).
"""

from __future__ import annotations

import ast
import copy
import logging
import pickle
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def _deep_clone(obj: Any) -> Any:
    """Clone sklearn PredictionModel or River BaseModel via pickle when needed."""
    try:
        return copy.deepcopy(obj)
    except Exception:
        return pickle.loads(pickle.dumps(obj))


def _wrong(pred: float, y: float) -> bool:
    return int(round(float(pred))) != int(round(float(y)))


@dataclass
class _SlotStats:
    """Lifetime accuracy tracking for a stored expert (paper / MOA)."""

    n_inst: int = 0
    n_correct: int = 0


class ECPFMetaLearner:
    """
    ECPF model pool + duel between reused copy and new learner.

    Works with either ``PredictionModel`` (sklearn path) or ``BaseModelAdapter``
    (River / RF path). Archives are **frozen** snapshots; only ``current_idx``
    expert and ``new_model`` receive stream updates in IN_CONTROL.
    """

    def __init__(
        self,
        *,
        similarity_margin: float = 0.95,
        fade_points: int = 15,
        model_check_freq: int = 1,
        fade_enabled: bool = True,
        max_pool_size: int = 10,
        use_advanced: bool = False,
        model_type: str = "linear",
        model_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.similarity_margin = float(similarity_margin)
        self.fade_points = int(fade_points)
        self.model_check_freq = int(model_check_freq)
        self.fade_enabled = bool(fade_enabled)
        self.max_pool_size = max(1, int(max_pool_size))
        self.use_advanced = bool(use_advanced)
        self.model_type = model_type
        self.model_kwargs = dict(model_kwargs or {})

        # Collection: None = removed slot
        self.slots: List[Optional[Any]] = []
        self.slot_stats: List[_SlotStats] = []
        # cumulative (seen, agreed) for conceptual equivalence (paper §3.1)
        self._pair_seen: Dict[Tuple[int, int], int] = {}
        self._pair_agreed: Dict[Tuple[int, int], int] = {}
        self.fade_scores: Dict[int, int] = {}

        self.current_idx: int = 0
        self.new_model: Optional[Any] = None

        self.curr_correct = 0
        self.new_correct = 0
        self.total_inst = 0

        self.num_drifts = 0
        self.model_reuses = 0
        self.model_merges = 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def bootstrap_first_expert(self, prediction_model: Any) -> None:
        """Call after initial warm-start: archive the first working model."""
        self.slots = [_deep_clone(prediction_model)]
        self.slot_stats = [_SlotStats()]
        self.fade_scores = {0: self.fade_points}
        self.current_idx = 0
        self.new_model = None
        self.curr_correct = 0
        self.new_correct = 0
        self.total_inst = 0

    def _predict_one(self, model: Any, x: np.ndarray) -> float:
        x = np.asarray(x, dtype=np.float64).ravel()
        if self.use_advanced:
            return float(model.predict_one(x.reshape(1, -1)))
        return float(model.predict(x.reshape(1, -1))[0])

    def _train_one(self, model: Any, x: np.ndarray, y: float) -> None:
        x = np.asarray(x, dtype=np.float64).ravel()
        if self.use_advanced:
            model.learn_one(x.reshape(1, -1), y)
            return
        model.fine_tune(x.reshape(1, -1), np.array([y], dtype=float))

    def _fit_on_buffer(self, model: Any, buffer: List[Tuple[np.ndarray, float]]) -> None:
        if not buffer:
            return
        X = np.stack([np.asarray(a, dtype=np.float64).ravel() for a, _ in buffer], axis=0)
        y = np.array([float(b) for _, b in buffer], dtype=float)
        if self.use_advanced:
            model.fit(X, y)
        else:
            model.fit(X, y)

    def leader_predict(self, prediction_model: Any, x: np.ndarray) -> float:
        """Predict with the current leading expert (must match ``prediction_model`` state)."""
        return self._predict_one(prediction_model, x)

    def on_stream_instance(
        self,
        prediction_model: Any,
        x: np.ndarray,
        y_true: float,
        y_pred_leader: Optional[float] = None,
    ) -> None:
        """
        IN_CONTROL training: update leader and ``new_model`` if present; duel counters.
        ``prediction_model`` must be the active leader object (same reference as pipeline).
        """
        if y_pred_leader is None:
            y_pred = self._predict_one(prediction_model, x)
        else:
            y_pred = float(y_pred_leader)
        if self.new_model is not None:
            ny = self._predict_one(self.new_model, x)
            if not _wrong(ny, y_true):
                self.new_correct += 1
        if not _wrong(y_pred, y_true):
            self.curr_correct += 1
        self.total_inst += 1

        if self.total_inst % self.model_check_freq == 0:
            self._compare_classifiers(prediction_model)

        self._train_one(prediction_model, x, y_true)
        if self.new_model is not None:
            self._train_one(self.new_model, x, y_true)

    def _compare_classifiers(self, prediction_model: Any) -> None:
        """Swap leader if shadow ``new_model`` is strictly more accurate since last drift."""
        if self.new_model is None:
            return
        if self.curr_correct < self.new_correct:
            self.curr_correct, self.new_correct = self.new_correct, self.curr_correct
            if self.use_advanced:
                tmp = prediction_model.get_model()
                prediction_model.set_model(self.new_model.get_model())
                self.new_model.set_model(tmp)
            else:
                m_a = prediction_model.get_model()
                sc_a = copy.deepcopy(prediction_model.scaler)
                fit_a = prediction_model._scaler_fitted
                m_b = self.new_model.get_model()
                sc_b = copy.deepcopy(self.new_model.scaler)
                fit_b = self.new_model._scaler_fitted
                prediction_model.set_model(m_b)
                prediction_model.scaler = sc_b
                prediction_model._scaler_fitted = fit_b
                self.new_model.set_model(m_a)
                self.new_model.scaler = sc_a
                self.new_model._scaler_fitted = fit_a
            self.slots[self.current_idx] = _deep_clone(prediction_model)
            logger.info("ECPF: swapped leader in favour of shadow learner")

    def on_drift(
        self,
        prediction_model: Any,
        buffer: List[Tuple[np.ndarray, float]],
    ) -> Dict[str, Any]:
        """
        Run ECPF steps 8–14 (paper): save leader, pick reuse, train new on buffer,
        merge by similarity, fade, clear counters.
        """
        self.num_drifts += 1
        details: Dict[str, Any] = {"buffer_len": len(buffer)}

        # Freeze current leader into its slot before buffer comparisons
        self.slots[self.current_idx] = _deep_clone(prediction_model)

        # Update lifetime stats for current leader slot (MOA getNextModel start)
        st = self.slot_stats[self.current_idx]
        st.n_inst += self.total_inst
        st.n_correct += self.curr_correct

        # Error bitsets on buffer for each alive slot
        alive = [i for i, m in enumerate(self.slots) if m is not None]
        if not alive:
            self.bootstrap_first_expert(prediction_model)
            alive = [0]

        wrong_bits: Dict[int, np.ndarray] = {}
        acc_on_buffer: Dict[int, float] = {}
        for i in alive:
            bits = np.zeros(len(buffer), dtype=np.uint8)
            correct = 0
            for t, (xv, yv) in enumerate(buffer):
                pred = self._predict_one(self.slots[i], xv)
                w = 1 if _wrong(pred, yv) else 0
                bits[t] = w
                if not w:
                    correct += 1
            wrong_bits[i] = bits
            acc_on_buffer[i] = correct / len(buffer) if buffer else 0.0

        # Pairwise similarity update (paper §3.1)
        for a in range(len(alive)):
            for b in range(a + 1, len(alive)):
                i, j = alive[a], alive[b]
                key = (min(i, j), max(i, j))
                diff = np.bitwise_xor(wrong_bits[i], wrong_bits[j])
                agreed = int(len(buffer) - int(diff.sum()))
                self._pair_seen[key] = self._pair_seen.get(key, 0) + len(buffer)
                self._pair_agreed[key] = self._pair_agreed.get(key, 0) + agreed

        # Merge similar slots (may remove indices)
        removed = self._merge_models(alive)
        details["merged"] = removed

        if self.slots[self.current_idx] is None:
            survivors = [i for i, m in enumerate(self.slots) if m is not None]
            self.current_idx = survivors[0] if survivors else 0

        # Recompute survivors and buffer accuracy after merges
        alive = [i for i, m in enumerate(self.slots) if m is not None]
        acc_on_buffer = {}
        for i in alive:
            correct = 0
            for xv, yv in buffer:
                pred = self._predict_one(self.slots[i], xv)
                if not _wrong(pred, yv):
                    correct += 1
            acc_on_buffer[i] = correct / len(buffer) if buffer else 0.0

        # Fresh learner trained on full warning buffer
        self.new_model = self._fresh_model()
        self._fit_on_buffer(self.new_model, buffer)

        # Best existing expert on buffer (reuse candidate)
        if not alive:
            best_i = self.current_idx
        else:
            best_i = max(alive, key=lambda idx: acc_on_buffer.get(idx, 0.0))

        # Accuracy diagnostics on the warning buffer.
        acc_best = float(acc_on_buffer.get(best_i, 0.0))
        acc_current = float(acc_on_buffer.get(self.current_idx, 0.0))
        new_correct = 0
        for xv, yv in buffer:
            p = self._predict_one(self.new_model, xv)
            if not _wrong(p, yv):
                new_correct += 1
        acc_new = float(new_correct / len(buffer)) if buffer else 0.0

        # Copy of best → new slot becomes active (MOA addModel(copy of best))
        clone_best = _deep_clone(self.slots[best_i])
        self.slots.append(clone_best)
        new_idx = len(self.slots) - 1
        self.slot_stats.append(_SlotStats())
        self.fade_scores.setdefault(new_idx, 0)
        self.current_idx = new_idx

        # Install leader weights into pipeline model = copy of best
        self._copy_model_into(prediction_model, clone_best)

        if self.fade_enabled:
            self._fade_models()
        self._enforce_pool_cap()

        self.curr_correct = 0
        self.new_correct = 0
        self.total_inst = 0
        self.model_reuses += 1

        details["collection_size"] = sum(1 for s in self.slots if s is not None)
        details["current_idx"] = self.current_idx
        details["best_idx"] = best_i
        details["acc_current_on_warning"] = acc_current
        details["acc_best_on_warning"] = acc_best
        details["acc_new_on_warning"] = acc_new
        details["winner_initial"] = "reused_copy"
        return details

    def _fresh_model(self) -> Any:
        if self.use_advanced:
            from .model_adapter import BaseModelAdapter

            return BaseModelAdapter(
                model_type=self.model_type,
                model_kwargs=self.model_kwargs,
            )
        from .prediction_model import PredictionModel

        return PredictionModel(model_type=self.model_type)

    def _copy_model_into(self, target: Any, source: Any) -> None:
        if self.use_advanced:
            target.set_model(_deep_clone(source.get_model()))
            return
        target.set_model(copy.deepcopy(source.get_model()))
        target.scaler = copy.deepcopy(source.scaler)
        target._scaler_fitted = source._scaler_fitted

    def _merge_models(self, alive: List[int]) -> List[int]:
        """Remove redundant experts when pairwise similarity ≥ m (paper)."""
        removed: List[int] = []
        alive = [i for i in alive if self.slots[i] is not None]
        for a in range(len(alive)):
            for b in range(a + 1, len(alive)):
                i, j = alive[a], alive[b]
                if self.slots[i] is None or self.slots[j] is None:
                    continue
                key = (min(i, j), max(i, j))
                seen = self._pair_seen.get(key, 0)
                if seen <= 0:
                    continue
                agreed = self._pair_agreed.get(key, 0)
                if agreed / seen < self.similarity_margin:
                    continue
                ai = self.slot_stats[i]
                aj = self.slot_stats[j]
                acc_i = ai.n_correct / max(1, ai.n_inst)
                acc_j = aj.n_correct / max(1, aj.n_inst)
                lose, keep = (j, i) if acc_i >= acc_j else (i, j)
                self._remove_slot(lose)
                removed.append(lose)
                self.model_merges += 1
                if self.fade_enabled:
                    self.fade_scores[keep] = self.fade_scores.get(keep, 0) + self.fade_scores.get(
                        lose, 0
                    )
                    self.fade_scores.pop(lose, None)
        return removed

    def _remove_slot(self, idx: int) -> None:
        self.slots[idx] = None
        if idx < len(self.slot_stats):
            self.slot_stats[idx] = _SlotStats()
        keys = [k for k in self._pair_seen if idx in k]
        for k in keys:
            self._pair_seen.pop(k, None)
            self._pair_agreed.pop(k, None)

    def _fade_models(self) -> None:
        """MOA-style fade: current gains f; others lose 1; at 0 remove."""
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                continue
            if i == self.current_idx:
                self.fade_scores[i] = self.fade_scores.get(i, 0) + self.fade_points
            else:
                fs = self.fade_scores.get(i, 0) - 1
                if fs <= 0:
                    self._remove_slot(i)
                    self.fade_scores.pop(i, None)
                else:
                    self.fade_scores[i] = fs

    def _enforce_pool_cap(self) -> None:
        """Keep at most ``max_pool_size`` alive snapshots, excluding current leader."""
        while sum(1 for s in self.slots if s is not None) > self.max_pool_size:
            candidates: List[Tuple[int, int]] = []
            for i, slot in enumerate(self.slots):
                if slot is None or i == self.current_idx:
                    continue
                candidates.append((self.fade_scores.get(i, 0), i))
            if not candidates:
                break
            _, rm_idx = min(candidates)
            self._remove_slot(rm_idx)
            self.fade_scores.pop(rm_idx, None)


def load_drift_times_file(path: str) -> List[int]:
    """Load drift times from txt (ints, space-separated, or list-of-pairs)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return []
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, list):
            out: List[int] = []
            for item in obj:
                if isinstance(item, (list, tuple)) and item:
                    out.append(int(item[0]))
                else:
                    out.append(int(item))
            return out
    except Exception:
        pass
    lines = text.replace(",", " ").replace("[", " ").replace("]", " ").split()
    return [int(x) for x in lines if x.lstrip("-").isdigit()]
