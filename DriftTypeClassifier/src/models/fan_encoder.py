"""
FAN: Full Attention Network encoder for 1D temporal sequences.
Input: (batch, seq_len) or (batch, seq_len, 1) -> Output: (batch, embed_dim)
"""

import math
import warnings
import torch
import torch.nn as nn
from typing import Optional


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 512, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, D)
        x = x + self.pe[:, : x.size(1), :]
        return self.dropout(x)


class FeedForward(nn.Module):
    def __init__(self, d_model: int, dim_feedforward: int, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(self.activation(self.linear1(x))))


class FANEncoder(nn.Module):
    """
    Full Attention Network for 1D sequences.
    - Linear projection to d_model
    - Optional positional encoding
    - N layers of multi-head self-attention + FFN + residual + LN
    - Global mean pooling
    - Optional projection to embed_dim
    """

    def __init__(
        self,
        input_dim: int = 1,
        d_model: int = 64,
        n_heads: int = 4,
        n_layers: int = 3,
        dim_feedforward: int = 128,
        dropout: float = 0.1,
        embed_dim: Optional[int] = None,
        use_pos_encoding: bool = True,
        max_len: int = 512,
        norm_first: bool = False,
    ):
        super().__init__()
        self.d_model = d_model
        self.embed_dim = embed_dim or d_model
        self.input_proj = nn.Linear(input_dim, d_model)
        self.input_norm = nn.LayerNorm(d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout) if use_pos_encoding else None
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=norm_first,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)  # nested_tensor when norm_first=True
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
        if self.embed_dim != d_model:
            self.out_proj = nn.Linear(d_model, self.embed_dim)
        else:
            self.out_proj = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (B, T) or (B, T, 1)
        returns (B, embed_dim)
        """
        if x.dim() == 2:
            x = x.unsqueeze(-1)
        B, T, _ = x.shape
        x = self.input_norm(self.input_proj(x))
        if self.pos_encoding is not None:
            x = self.pos_encoding(x)
        x = self.transformer(x)
        x = x.transpose(1, 2)
        x = self.pool(x).squeeze(-1)
        return self.out_proj(x)


class MLPEncoder(nn.Module):
    """Simple MLP encoder: flatten (B, T, D) -> (B, T*D), then Linear -> ReLU -> Linear. Same I/O as FANEncoder."""

    def __init__(self, seq_len: int, input_dim: int = 1, hidden_dim: int = 64, embed_dim: int = 64):
        super().__init__()
        self.flat_dim = seq_len * input_dim
        self.mlp = nn.Sequential(
            nn.Linear(self.flat_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, embed_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(-1)
        B, T, D = x.shape
        x = x.reshape(B, -1)
        return self.mlp(x)
