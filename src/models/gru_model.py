"""
gru_model.py
============
Model D — GRU (Gated Recurrent Unit) network built with PyTorch.

Architecture:  ``input → GRU → Linear → sigmoid``

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
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
import torch
import torch.nn as nn

from .base_model import BaseModel


class _GRUNet(nn.Module):
    """Minimal GRU → Linear binary classifier."""

    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(
        self, x: torch.Tensor, h: Optional[torch.Tensor] = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        out, h_n = self.gru(x, h)
        logits = self.fc(out[:, -1, :])
        return logits, h_n


class GRUModel(BaseModel):
    """GRU-based binary classifier with online-learning support.

    Parameters
    ----------
    input_size : int
        Number of features per time step.
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
    """

    def __init__(
        self,
        input_size: int = 4,
        hidden_size: int = 32,
        num_layers: int = 1,
        learning_rate: float = 1e-3,
        window_size: int = 10,
        device: str = "cpu",
    ) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self._lr = learning_rate
        self.window_size = window_size
        self.device = torch.device(device)

        self.net = _GRUNet(input_size, hidden_size, num_layers).to(self.device)
        self.criterion = nn.BCEWithLogitsLoss()
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=learning_rate)

        self._window: deque = deque(maxlen=window_size)
        self._hidden: Optional[torch.Tensor] = None

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
                y_t = torch.tensor(np.array(labels), dtype=torch.float32).to(
                    self.device
                ).unsqueeze(1)

                self.optimizer.zero_grad()
                logits, _ = self.net(X_t)
                loss = self.criterion(logits, y_t)
                loss.backward()
                self.optimizer.step()

        return self

    def predict(self, X: Any) -> np.ndarray:
        X = self._to_numpy(X).astype(np.float32)
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
                preds.append(int(torch.sigmoid(logit).item() >= 0.5))
        return np.array(preds)

    # ------------------------------------------------------------------
    # Streaming / online interface
    # ------------------------------------------------------------------
    def learn_one(self, x: Dict[str, float], y: Any) -> "GRUModel":
        x_arr = self._dict_to_array(x)
        self._window.append((x_arr, float(y)))

        X_seq = np.array([s[0] for s in self._window], dtype=np.float32)
        target = float(self._window[-1][1])

        X_t = torch.tensor(X_seq, dtype=torch.float32).unsqueeze(0).to(self.device)
        y_t = torch.tensor([[target]], dtype=torch.float32).to(self.device)

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
            prob = torch.sigmoid(logit).item()
        return int(prob >= 0.5)

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
            "net_state_dict": self.net.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "window": list(self._window),
        }
        torch.save(state, path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "GRUModel":
        state = torch.load(path, map_location="cpu", weights_only=False)
        obj = cls(
            input_size=state["input_size"],
            hidden_size=state["hidden_size"],
            num_layers=state["num_layers"],
            learning_rate=state["lr"],
            window_size=state["window_size"],
            device=state["device"],
        )
        obj.net.load_state_dict(state["net_state_dict"])
        obj.optimizer.load_state_dict(state["optimizer_state_dict"])
        obj._window = deque(state["window"], maxlen=state["window_size"])
        return obj

    def __repr__(self) -> str:
        return (
            f"GRUModel(input={self.input_size}, hidden={self.hidden_size}, "
            f"layers={self.num_layers}, window={self.window_size})"
        )
