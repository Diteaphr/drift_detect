"""
Prototypical network: FAN encoder + class prototypes from support set, query classified by distance.
"""

import torch
import torch.nn as nn
from typing import Optional
from .fan_encoder import FANEncoder


class ProtoNet(nn.Module):
    """
    Prototypical network for N-way classification.
    - Encoder (FAN) maps input sequence to embedding
    - Prototypes = mean of support embeddings per class
    - Query logits = negative Euclidean distance to prototypes
    """

    def __init__(
        self,
        encoder: nn.Module,
        n_way: int = 3,
    ):
        super().__init__()
        self.encoder = encoder
        self.n_way = n_way

    def forward(
        self,
        support_x: torch.Tensor,
        support_y: torch.Tensor,
        query_x: torch.Tensor,
    ) -> torch.Tensor:
        """
        support_x: (N*K, seq_len) or (N*K, seq_len, 1)
        support_y: (N*K,) class indices in [0, N-1]
        query_x: (N*Q, seq_len)
        Returns logits (N*Q, N)
        """
        support_emb = self.encoder(support_x)
        query_emb = self.encoder(query_x)
        prototypes = self._compute_prototypes(support_emb, support_y)
        logits = self._distance_to_logits(query_emb, prototypes)
        return logits

    def _compute_prototypes(self, support_emb: torch.Tensor, support_y: torch.Tensor) -> torch.Tensor:
        """support_emb (N*K, D), support_y (N*K,) -> prototypes (N, D)"""
        n_way = self.n_way
        prototypes = []
        for c in range(n_way):
            mask = support_y == c
            if mask.any():
                prototypes.append(support_emb[mask].mean(dim=0))
            else:
                prototypes.append(support_emb[0] * 0)
        return torch.stack(prototypes, dim=0)

    def _distance_to_logits(self, query_emb: torch.Tensor, prototypes: torch.Tensor) -> torch.Tensor:
        """Euclidean distance -> negative distance as logits."""
        # query_emb (Q, D), prototypes (N, D)
        dist = torch.cdist(query_emb, prototypes, p=2)
        return -dist

    def predict_from_embeddings(self, query_emb: torch.Tensor, prototypes: torch.Tensor) -> torch.Tensor:
        """Given query embeddings and prototypes, return class indices."""
        logits = self._distance_to_logits(query_emb, prototypes)
        return logits.argmax(dim=-1)


def build_protonet(
    seq_len: int = 14,
    input_dim: int = 1,
    d_model: int = 64,
    n_heads: int = 4,
    n_layers: int = 3,
    dim_feedforward: int = 128,
    dropout: float = 0.1,
    embed_dim: int = 64,
    n_way: int = 3,
    norm_first: bool = False,
) -> ProtoNet:
    encoder = FANEncoder(
        input_dim=input_dim,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        dim_feedforward=dim_feedforward,
        dropout=dropout,
        embed_dim=embed_dim,
        use_pos_encoding=True,
        max_len=seq_len + 10,
        norm_first=norm_first,
    )
    return ProtoNet(encoder=encoder, n_way=n_way)
