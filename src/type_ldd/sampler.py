"""Prototypical episode batch sampler (from Type-LDD-main)."""

from __future__ import annotations

import numpy as np
import torch


class PrototypicalBatchSampler:
    """
    Yields batches of indexes for episodic training.
    Each episode: classes_per_it classes × (support + query) samples.
    """

    def __init__(self, labels, classes_per_it: int, num_samples: int, iterations: int):
        super().__init__()
        self.labels = labels
        self.classes_per_it = classes_per_it
        self.sample_per_class = num_samples
        self.iterations = iterations

        self.classes, self.counts = np.unique(self.labels, return_counts=True)
        self.classes = torch.LongTensor(self.classes)

        self.indexes = np.empty((len(self.classes), max(self.counts)), dtype=float) * np.nan
        self.indexes = torch.Tensor(self.indexes)
        self.numel_per_class = torch.zeros_like(self.classes)
        for idx, label in enumerate(self.labels):
            label_idx = np.argwhere(self.classes == label).item()
            self.indexes[label_idx, np.where(np.isnan(self.indexes[label_idx]))[0][0]] = idx
            self.numel_per_class[label_idx] += 1

    def __iter__(self):
        spc = self.sample_per_class
        cpi = self.classes_per_it
        for _ in range(self.iterations):
            batch_size = spc * cpi
            batch = torch.LongTensor(batch_size)
            c_idxs = torch.randperm(len(self.classes))[:cpi]
            for i, c in enumerate(self.classes[c_idxs]):
                s = slice(i * spc, (i + 1) * spc)
                label_idx = torch.arange(len(self.classes)).long()[self.classes == c].item()
                sample_idxs = torch.randperm(int(self.numel_per_class[label_idx]))[:spc]
                batch[s] = self.indexes[label_idx][sample_idxs].long()
            batch = batch[torch.randperm(len(batch))]
            yield batch

    def __len__(self) -> int:
        return self.iterations
