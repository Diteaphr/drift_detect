"""
gru_model.py
============
Model D — GRU (Gated Recurrent Unit) network built with PyTorch.

Architecture:  ``input → GRU → Linear → (sigmoid | softmax | identity)``

Online learning strategy
------------------------
Since PyTorch is a batch framework, we implement ``learn_one`` by:

1.  Maintaining a **sliding window** of the most recent ``window_size``
    samples so the GRU can learn temporal patterns even in a single-step
    update.
2.  Each ``learn_one`` call appends the new sample to the window, constructs
    a mini-sequence, and performs **one gradient descent step** (forward →
    loss → backward → optimizer.step).
3.  The hidden state is carried forward across successive calls, giving the
    GRU continuity even though each update only sees a short window.

Lazy network construction
-------------------------
``input_size`` used to be a constructor default of 4 that nothing ever
inferred from the data.  Every dataset in ``data/`` has 2 or 3 features and no
runner passes ``model_kwargs``, so the first forward pass always died with::

    RuntimeError: input.size(-1) must be equal to input_size. Expected 4, got 3

The network is therefore built **on the first sample actually seen**, from that
sample's own width.  ``input_size`` survives as an explicit override for
callers who know the width up front; when the override disagrees with the data
the data wins (with a warning), because refusing to run would just reinstate
the bug this change exists to remove.

Passing an explicit ``input_size`` keeps the eager construction path: the
network, criterion and optimizer are created in ``__init__`` in exactly the
original order, so the sequence of RNG draws that initialises the weights — and
therefore every number a seeded binary run produces — is unchanged.

Task types
----------
``task_type`` / ``n_classes`` (the vocabulary of :mod:`src.task`) select the
output head:

===============  ============  =====================  ===================
task             output units  loss                   ``predict_one``
===============  ============  =====================  ===================
binary (K=2)     1             ``BCEWithLogitsLoss``  ``int(p >= 0.5)``
multiclass       K             ``CrossEntropyLoss``   ``int(argmax)``
regression       1             ``MSELoss``            ``float``
===============  ============  =====================  ===================

The binary row is the pre-existing code path, reproduced exactly.  When no task
is declared the model starts binary and *promotes* itself if the labels turn
out to contradict that (see :meth:`GRUModel._maybe_promote`) — a safety net for
un-wired callers, and one that can never fire on labels confined to {0, 1}.
"""

from __future__ import annotations

import warnings
from collections import deque
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn

from ..task import TaskType
from .base_model import BaseModel


class _GRUNet(nn.Module):
    """Minimal GRU → Linear head.

    ``output_size`` defaults to 1 so that the binary construction sequence
    (``nn.GRU`` then ``nn.Linear(hidden_size, 1)``) is byte-for-byte the one
    this module has always used.
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int = 1,
        output_size: int = 1,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(
        self, x: torch.Tensor, h: Optional[torch.Tensor] = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        out, h_n = self.gru(x, h)
        logits = self.fc(out[:, -1, :])
        return logits, h_n


class GRUModel(BaseModel):
    """GRU-based online learner for binary, multi-class or regression streams.

    Parameters
    ----------
    input_size : int or None
        Number of features per time step.  ``None`` (the default) infers it
        from the first sample seen, which is what any caller in this repo
        wants; an explicit value is an override and builds the net eagerly.
    hidden_size : int
        Number of hidden units in the GRU.
    num_layers : int
        Number of stacked GRU layers.
    learning_rate : float
        Learning rate for Adam optimizer.
    window_size : int
        Length of the sliding window used to form the input sequence during
        online learning.
    device : str
        ``"cpu"`` or ``"cuda"``.
    task_type : str, TaskType or None
        Declared task.  ``None`` starts binary and self-corrects from the
        labels; declaring it is strongly preferred for K>2 and regression,
        because a declaration is known before the first gradient step whereas
        a promotion discards the output head it replaces.
    n_classes : int or None
        Declared K.  Only used for a multi-class task, where it sizes the
        output layer even if some class has not been observed yet.
    """

    def __init__(
        self,
        input_size: Optional[int] = None,
        hidden_size: int = 32,
        num_layers: int = 1,
        learning_rate: float = 1e-3,
        window_size: int = 10,
        device: str = "cpu",
        task_type: Optional[Union[str, TaskType]] = None,
        n_classes: Optional[int] = None,
    ) -> None:
        self.input_size: Optional[int] = int(input_size) if input_size is not None else None
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self._lr = learning_rate
        self.window_size = window_size
        self.device = torch.device(device)
        self.task_type: Optional[TaskType] = (
            TaskType(task_type) if task_type is not None else None
        )
        self.n_classes: Optional[int] = int(n_classes) if n_classes is not None else None

        self.net: Optional[_GRUNet] = None
        self.criterion: Optional[nn.Module] = None
        self.optimizer: Optional[torch.optim.Optimizer] = None
        self.output_size: Optional[int] = None
        self._task: Optional[TaskType] = None

        # Cumulative label statistics, used only when no task was declared.
        # They are running aggregates because a single ``learn_one`` label — or
        # one all-zeros buffer — says nothing about the cardinality of the
        # stream it came from.
        self._label_min: Optional[float] = None
        self._label_max: Optional[float] = None
        self._labels_integral: bool = True

        self._window: deque = deque(maxlen=window_size)
        self._hidden: Optional[torch.Tensor] = None

        if self.task_type is TaskType.MULTICLASS and self.n_classes is None:
            # K sizes the output layer, so it has to be known *before* the
            # first gradient step.  Without it the head is sized from whatever
            # labels have turned up so far and is thrown away each time a
            # larger class index appears — correct, but it wastes training.
            warnings.warn(
                "task_type='multiclass' was declared without n_classes; the "
                "output layer will be sized from the labels seen so far and "
                "rebuilt whenever a larger class index appears. Pass "
                "n_classes=K (TaskSpec.n_classes) to avoid this.",
                RuntimeWarning,
                stacklevel=2,
            )

        if self.input_size is not None:
            task, out = self._declared_head()
            self._build(self.input_size, task, out)

    # ------------------------------------------------------------------
    # Task resolution / network construction
    # ------------------------------------------------------------------
    def _declared_head(self) -> Tuple[TaskType, int]:
        """Head implied by the declaration alone (no labels seen yet)."""
        task = self.task_type or TaskType.BINARY
        if task is TaskType.MULTICLASS:
            return task, max(self.n_classes or 2, 2)
        return task, 1

    def _observe_labels(self, y: np.ndarray) -> None:
        arr = np.asarray(y, dtype=np.float64).ravel()
        finite = arr[np.isfinite(arr)]
        if finite.size == 0:
            return
        lo, hi = float(finite.min()), float(finite.max())
        self._label_min = lo if self._label_min is None else min(self._label_min, lo)
        self._label_max = hi if self._label_max is None else max(self._label_max, hi)
        if self._labels_integral and not bool(np.all(np.mod(finite, 1.0) == 0.0)):
            self._labels_integral = False

    def _head_from_labels(self) -> Tuple[TaskType, int]:
        """Head implied by the declaration plus every label observed so far.

        Binary-vs-multiclass is decided on ``max(label)``, not on the number of
        distinct labels: a stream that has only shown class 0 so far is still
        an ordinary binary stream, and must not be pushed onto a K-way head.
        """
        declared = self.task_type
        if declared is TaskType.REGRESSION:
            return TaskType.REGRESSION, 1
        if self._label_min is None:
            return self._declared_head()
        if not self._labels_integral:
            if declared is not None:
                raise ValueError(
                    "task_type=%r was declared but the observed labels are not "
                    "integral (min=%r, max=%r); a classification head cannot "
                    "consume a continuous target."
                    % (declared.value, self._label_min, self._label_max)
                )
            return TaskType.REGRESSION, 1
        if self._label_min < 0:
            raise ValueError(
                "GRU classification requires labels in [0, K-1] but the "
                "observed minimum label is %r. Encode the classes as 0..K-1, "
                "or pass task_type='regression' if the target is continuous."
                % (self._label_min,)
            )
        hi = int(round(self._label_max))
        if declared is TaskType.MULTICLASS:
            return TaskType.MULTICLASS, max(hi + 1, self.n_classes or 0, 2)
        if hi <= 1:
            # {0}, {1} and {0,1} all land here — the untouched binary head.
            return TaskType.BINARY, 1
        if declared is TaskType.BINARY:
            warnings.warn(
                "task_type='binary' was declared but labels up to %r were "
                "observed; following the data and switching to a %d-class head."
                % (self._label_max, hi + 1),
                RuntimeWarning,
                stacklevel=3,
            )
        return TaskType.MULTICLASS, hi + 1

    def _make_criterion(self, task: TaskType) -> nn.Module:
        if task is TaskType.MULTICLASS:
            return nn.CrossEntropyLoss()
        if task is TaskType.REGRESSION:
            return nn.MSELoss()
        return nn.BCEWithLogitsLoss()

    def _build(self, input_size: int, task: TaskType, output_size: int) -> None:
        """Create net + criterion + optimizer in the original order."""
        self.net = _GRUNet(input_size, self.hidden_size, self.num_layers, output_size).to(
            self.device
        )
        self.criterion = self._make_criterion(task)
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=self._lr)
        self.input_size = int(input_size)
        self.output_size = int(output_size)
        self._task = task

    def _ensure_built(self, x_arr: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Build the net for this sample's width, or rebuild on a width change."""
        width = int(x_arr.shape[-1])
        if self.net is None:
            if y is not None:
                self._observe_labels(y)
            task, out = self._head_from_labels()
            self._build(width, task, out)
            return
        if width != self.input_size:
            warnings.warn(
                "GRU was configured for input_size=%r but the data has %d "
                "features; rebuilding the network for the observed width. Pass "
                "input_size=None (the default) to infer it instead."
                % (self.input_size, width),
                RuntimeWarning,
                stacklevel=3,
            )
            self._build(width, self._task, self.output_size)
            self._window.clear()
            self._hidden = None

    def _maybe_promote(self) -> None:
        """Widen / re-purpose the output head when the labels demand it.

        Labels confined to {0, 1} always resolve back to the binary head, so a
        binary run never takes this path.  The GRU body is kept — only the
        final linear layer is replaced — so what the recurrent weights have
        already learned survives the change.
        """
        if self.net is None:
            return
        task, out = self._head_from_labels()
        if task is self._task and out <= (self.output_size or 1):
            return
        warnings.warn(
            "GRU labels imply a %s task with %d output unit(s) but the network "
            "was built for %s with %s; replacing the output head. Declare "
            "task_type/n_classes up front to avoid discarding it."
            % (task.value, out, self._task.value if self._task else "?", self.output_size),
            RuntimeWarning,
            stacklevel=3,
        )
        if out != self.output_size:
            self.net.fc = nn.Linear(self.hidden_size, out).to(self.device)
            self.optimizer = torch.optim.Adam(self.net.parameters(), lr=self._lr)
        self.criterion = self._make_criterion(task)
        self.output_size = out
        self._task = task

    # ------------------------------------------------------------------
    # Target / output shaping
    # ------------------------------------------------------------------
    def _targets(self, labels: np.ndarray) -> torch.Tensor:
        """Shape a batch of labels for the active criterion.

        ``CrossEntropyLoss`` wants 1-D int64 class indices against ``(B, K)``
        logits; ``BCEWithLogitsLoss`` and ``MSELoss`` want ``(B, 1)`` floats.
        """
        if self._task is TaskType.MULTICLASS:
            return torch.tensor(
                np.asarray(labels).ravel(), dtype=torch.long
            ).to(self.device)
        return (
            torch.tensor(np.asarray(labels).ravel(), dtype=torch.float32)
            .unsqueeze(1)
            .to(self.device)
        )

    def _decode(self, logits: torch.Tensor) -> Any:
        """Turn a single row of logits into the model's output value."""
        if self._task is TaskType.MULTICLASS:
            return int(torch.argmax(logits, dim=-1).item())
        if self._task is TaskType.REGRESSION:
            return float(logits.item())
        return int(torch.sigmoid(logits).item() >= 0.5)

    # ------------------------------------------------------------------
    # Batch interface
    # ------------------------------------------------------------------
    def fit(
        self,
        X: Any,
        y: Any,
        epochs: int = 10,
        batch_size: int = 32,
    ) -> "GRUModel":
        X = self._to_numpy(X).astype(np.float32)
        y = np.asarray(y, dtype=np.float32).ravel()
        # A full batch is the most trustworthy place to infer the task, so it
        # is handed to the builder before any weight exists.
        self._ensure_built(X[0] if X.shape[0] else np.zeros(X.shape[1]), y)
        self._observe_labels(y)
        self._maybe_promote()
        seq_len = self.window_size

        self.net.train()
        for epoch in range(epochs):
            indices = list(range(seq_len, len(X) + 1))
            np.random.shuffle(indices)
            for start in range(0, len(indices), batch_size):
                batch_idx = indices[start : start + batch_size]
                seqs, labels = [], []
                for end in batch_idx:
                    seqs.append(X[end - seq_len : end])
                    labels.append(y[end - 1])

                X_t = torch.tensor(np.array(seqs), dtype=torch.float32).to(self.device)
                y_t = self._targets(np.array(labels))

                self.optimizer.zero_grad()
                logits, _ = self.net(X_t)
                loss = self.criterion(logits, y_t)
                loss.backward()
                self.optimizer.step()

        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X).astype(np.float32)
        if X.shape[0] == 0:
            return np.array([])
        self._ensure_built(X[0])
        self.net.eval()
        preds = []
        h = None
        with torch.no_grad():
            for i in range(X.shape[0]):
                x_t = (
                    torch.tensor(X[i], dtype=torch.float32)
                    .unsqueeze(0)
                    .unsqueeze(0)
                    .to(self.device)
                )
                logit, h = self.net(x_t, h)
                preds.append(self._decode(logit))
        return np.array(preds)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "GRUModel":
        x_arr = self._dict_to_array(x)
        y_arr = np.asarray([float(y)], dtype=np.float64)
        # Built (or rebuilt) before the window is touched, so a width change
        # cannot leave stale-width vectors behind.
        self._ensure_built(x_arr, y_arr)
        self._observe_labels(y_arr)
        self._maybe_promote()

        self._window.append((x_arr, float(y)))

        X_seq = np.array([s[0] for s in self._window], dtype=np.float32)
        target = float(self._window[-1][1])

        X_t = torch.tensor(X_seq, dtype=torch.float32).unsqueeze(0).to(self.device)
        y_t = self._targets(np.array([target], dtype=np.float32))

        self.net.train()
        self.optimizer.zero_grad()

        h = self._hidden.detach() if self._hidden is not None else None

        logits, h_n = self.net(X_t, h)
        loss = self.criterion(logits, y_t)
        loss.backward()
        self.optimizer.step()

        self._hidden = h_n.detach()
        return self

    def predict_one(self, x: Dict[str, float]) -> Any:
        x_arr = self._dict_to_array(x)
        self._ensure_built(x_arr)
        x_t = (
            torch.tensor(x_arr, dtype=torch.float32)
            .unsqueeze(0)
            .unsqueeze(0)
            .to(self.device)
        )

        self.net.eval()
        with torch.no_grad():
            h = self._hidden
            logit, h_n = self.net(x_t, h)
            return self._decode(logit)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _dict_to_array(self, x: Dict[str, float]) -> np.ndarray:
        if isinstance(x, dict):
            keys = sorted(x.keys())
            return np.array([x[k] for k in keys], dtype=np.float32)
        if isinstance(x, np.ndarray):
            return x.astype(np.float32).flatten()
        return np.array(x, dtype=np.float32).flatten()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "lr": self._lr,
            "window_size": self.window_size,
            "device": str(self.device),
            # The resolved head is persisted, not just the declaration: a model
            # that promoted itself mid-stream must come back the same shape.
            "task": self._task.value if self._task else None,
            "task_type": self.task_type.value if self.task_type else None,
            "n_classes": self.n_classes,
            "output_size": self.output_size,
            "label_min": self._label_min,
            "label_max": self._label_max,
            "labels_integral": self._labels_integral,
            "net_state_dict": self.net.state_dict() if self.net is not None else None,
            "optimizer_state_dict": (
                self.optimizer.state_dict() if self.optimizer is not None else None
            ),
            "window": list(self._window),
        }
        torch.save(state, path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "GRUModel":
        state = torch.load(path, map_location="cpu", weights_only=False)
        obj = cls(
            input_size=None,  # built below, from the persisted head
            hidden_size=state["hidden_size"],
            num_layers=state["num_layers"],
            learning_rate=state["lr"],
            window_size=state["window_size"],
            device=state["device"],
            task_type=state.get("task_type"),
            n_classes=state.get("n_classes"),
        )
        obj._label_min = state.get("label_min")
        obj._label_max = state.get("label_max")
        obj._labels_integral = bool(state.get("labels_integral", True))
        if state.get("net_state_dict") is not None:
            task = TaskType(state["task"]) if state.get("task") else TaskType.BINARY
            obj._build(
                int(state["input_size"]),
                task,
                int(state.get("output_size") or 1),
            )
            obj.net.load_state_dict(state["net_state_dict"])
            if state.get("optimizer_state_dict") is not None:
                obj.optimizer.load_state_dict(state["optimizer_state_dict"])
        obj._window = deque(state["window"], maxlen=state["window_size"])
        return obj

    def __repr__(self) -> str:
        task = self._task.value if self._task else "unbuilt"
        return (
            f"GRUModel(task={task}, input={self.input_size}, "
            f"hidden={self.hidden_size}, layers={self.num_layers}, "
            f"window={self.window_size})"
        )
