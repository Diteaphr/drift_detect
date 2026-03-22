"""
Episodic sampler for few-shot prototypical training.
"""

import numpy as np
import torch
from torch.utils.data import Dataset
from typing import Tuple, Optional


class DriftDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.from_numpy(X).float()
        self.y = torch.from_numpy(y).long()
        self.n_classes = int(np.max(y)) + 1

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, i: int) -> Tuple[torch.Tensor, int]:
        return self.X[i], self.y[i].item()


class EpisodicSampler:
    """Sample N-way K-shot Q-query episodes from a dataset."""

    def __init__(
        self,
        dataset: DriftDataset,
        n_way: int = 3,
        k_shot: int = 5,
        q_query: int = 15,
        n_episodes: int = 100,
        seed: Optional[int] = None,
    ):
        self.dataset = dataset
        self.n_way = n_way
        self.k_shot = k_shot
        self.q_query = q_query
        self.n_episodes = n_episodes
        self.rng = np.random.default_rng(seed)
        self.class_to_idx = {}
        for c in range(dataset.n_classes):
            self.class_to_idx[c] = np.where(dataset.y.numpy() == c)[0]
        self.classes = list(self.class_to_idx.keys())

    def __iter__(self):
        for _ in range(self.n_episodes):
            yield self._sample_episode()

    def _sample_episode(self) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Returns (support_x, support_y, query_x, query_y)."""
        chosen = self.rng.choice(self.classes, size=self.n_way, replace=False)
        support_x_list, support_y_list = [], []
        query_x_list, query_y_list = [], []
        for i, c in enumerate(chosen):
            idx = self.class_to_idx[c]
            self.rng.shuffle(idx)
            need = self.k_shot + self.q_query
            if len(idx) < need:
                idx = np.tile(idx, (need // len(idx) + 1))[: need]
            else:
                idx = idx[: need]
            sup_idx, q_idx = idx[: self.k_shot], idx[self.k_shot : self.k_shot + self.q_query]
            for j in sup_idx:
                support_x_list.append(self.dataset.X[j])
                support_y_list.append(i)
            for j in q_idx:
                query_x_list.append(self.dataset.X[j])
                query_y_list.append(i)
        support_x = torch.stack(support_x_list, dim=0)
        support_y = torch.tensor(support_y_list, dtype=torch.long)
        query_x = torch.stack(query_x_list, dim=0)
        query_y = torch.tensor(query_y_list, dtype=torch.long)
        return support_x, support_y, query_x, query_y
