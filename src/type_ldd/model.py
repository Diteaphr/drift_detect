"""
Joint FAN ProtoNet + DriftPointNet from Type-LDD-main/JointNetDrift.py.

Parameterised via TypeLDDConfig instead of their global argparse `args`.
"""

from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import TypeLDDConfig


def euclidean_dist(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    n = x.size(0)
    m = y.size(0)
    d = x.size(1)
    if d != y.size(1):
        raise ValueError(f"euclidean_dist dim mismatch: {d} vs {y.size(1)}")
    x = x.unsqueeze(1).expand(n, m, d)
    y = y.unsqueeze(0).expand(n, m, d)
    return torch.pow(x - y, 2).sum(2)


class AutomaticWeightedLoss(nn.Module):
    def __init__(self, num: int = 2):
        super().__init__()
        self.params = nn.Parameter(torch.ones(num, requires_grad=True))

    def forward(self, *losses: torch.Tensor) -> torch.Tensor:
        loss_sum = 0.0
        for i, loss in enumerate(losses):
            loss_sum = loss_sum + 0.5 / (self.params[i] ** 2) * loss + torch.log(
                1 + self.params[i] ** 2
            )
        return loss_sum


class FNN(nn.Module):
    def __init__(self, data_vector_length: int, centroid_vector_length: int):
        super().__init__()
        self.fc1 = nn.Linear(data_vector_length, 250)
        self.fc2 = nn.Linear(250, 250)
        self.fc3 = nn.Linear(250, 250)
        self.fc4 = nn.Linear(250, centroid_vector_length)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)


class FAN(nn.Module):
    """Attention feed-attention-network (Type-LDD)."""

    def __init__(self, data_vector_length: int, centroid_vector_length: int):
        super().__init__()
        if data_vector_length > 50:
            self.hidden_size = data_vector_length * 2
        else:
            self.hidden_size = data_vector_length * 3
        self.attn = nn.Linear(data_vector_length, self.hidden_size)
        self.W_s = nn.Linear(data_vector_length, self.hidden_size)
        self.attn_combine = nn.Linear(self.hidden_size * 2, centroid_vector_length)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        attn_weights = F.softmax(self.attn(x), dim=1)
        q_s = F.relu(self.W_s(x))
        attn_applied = torch.mul(attn_weights, q_s)
        combine = torch.cat((q_s, attn_applied), 1)
        return self.attn_combine(combine)


class FQN(nn.Module):
    def __init__(self, data_vector_length: int, centroid_vector_length: int):
        super().__init__()
        self.embedding = nn.Linear(data_vector_length, data_vector_length)
        self.W_s = nn.Linear(data_vector_length, data_vector_length * 2)
        self.out = nn.Linear(data_vector_length * 2, centroid_vector_length)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embed_x = F.relu(self.embedding(x))
        q_s = torch.tanh(self.W_s(embed_x))
        encoded_mask = torch.ones_like(q_s) * -100
        attn_combine = q_s + encoded_mask
        return self.out(attn_combine)


class LSTMEncoder(nn.Module):
    def __init__(self, data_vector_length: int, centroid_vector_length: int):
        super().__init__()
        self.data_vector_length = data_vector_length
        self.rnn = nn.LSTM(
            input_size=1,
            hidden_size=32,
            num_layers=2,
            bidirectional=True,
            batch_first=True,
        )
        self.out = nn.Linear(64, centroid_vector_length)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        m_t = x.reshape(-1, self.data_vector_length, 1)
        r_out, _ = self.rnn(m_t, None)
        return self.out(r_out[:, -1, :])


class FCN(nn.Module):
    def __init__(self, data_vector_length: int, centroid_vector_length: int):
        super().__init__()
        self.dim = data_vector_length
        self.conv_kernal_size = 5
        self.pool_kernal_size = 2
        self.stride = 1
        self.conv1 = nn.Conv1d(1, 16, self.conv_kernal_size, self.stride)
        self.max_pool1 = nn.MaxPool1d(self.pool_kernal_size)
        self.conv2 = nn.Conv1d(16, 32, self.conv_kernal_size, self.stride)
        self.max_pool2 = nn.MaxPool1d(self.pool_kernal_size)
        self.conv3 = nn.Conv1d(32, 64, self.conv_kernal_size, self.stride)
        self.max_pool3 = nn.MaxPool1d(self.pool_kernal_size)
        cvo1 = ((self.dim - self.conv_kernal_size) / self.stride) + 1
        mpl1 = cvo1 / self.pool_kernal_size
        cvo2 = ((mpl1 - self.conv_kernal_size) / self.stride) + 1
        mpl2 = cvo2 / self.pool_kernal_size
        cvo3 = ((mpl2 - self.conv_kernal_size) / self.stride) + 1
        self.mpl3 = int(cvo3 / self.pool_kernal_size)
        self.dropout = nn.Dropout()
        self.liner1 = nn.Linear(64 * self.mpl3, centroid_vector_length)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.unsqueeze(1)
        x = F.relu(self.conv1(x))
        x = self.max_pool1(x)
        x = F.relu(self.conv2(x))
        x = self.max_pool2(x)
        x = F.relu(self.conv3(x))
        x = self.max_pool3(x)
        x = x.view(-1, 64 * self.mpl3)
        x = self.dropout(x)
        return self.liner1(x)


def build_encoder(
    model_select: str,
    data_vector_length: int,
    centroid_vector_length: int,
) -> nn.Module:
    key = model_select.upper()
    if key == "FNN":
        return FNN(data_vector_length, centroid_vector_length)
    if key == "FAN":
        return FAN(data_vector_length, centroid_vector_length)
    if key == "FCN":
        return FCN(data_vector_length, centroid_vector_length)
    if key == "RNN":
        return LSTMEncoder(data_vector_length, centroid_vector_length)
    if key == "FQN":
        return FQN(data_vector_length, centroid_vector_length)
    raise ValueError(f"Unknown model_select={model_select!r}")


class PrototypicalNet(nn.Module):
    def __init__(
        self,
        data_vector_length: int,
        centroid_vector_length: int,
        model_select: str = "FAN",
        use_gpu: bool = False,
    ):
        super().__init__()
        self.gpu = use_gpu
        self.f = build_encoder(model_select, data_vector_length, centroid_vector_length)
        if self.gpu:
            self.f = self.f.cuda()

    def forward(self, datax: torch.Tensor) -> torch.Tensor:
        return self.f(datax)


class DriftPointNet(nn.Module):
    def __init__(self, data_vector_length: int, centroid_vector_length: int):
        super().__init__()
        self.embedding = nn.Linear(data_vector_length, 800)
        self.mlp1 = nn.Linear(data_vector_length + centroid_vector_length, 800)
        self.mlp2 = nn.Linear(800, 800)
        self.out = nn.Linear(800, 1)

    def forward(self, centroid: torch.Tensor, datax: torch.Tensor) -> torch.Tensor:
        v_x = F.relu(self.embedding(datax))
        j_x = torch.cat((datax, centroid), dim=1)
        j2_x = F.relu(self.mlp1(j_x))
        r_x = F.relu(self.mlp2(j2_x))
        z_x = v_x + r_x
        return self.out(z_x)


class JointPrediction(nn.Module):
    """Joint type (ProtoNet) + location (DriftPointNet) model."""

    def __init__(self, cfg: TypeLDDConfig):
        super().__init__()
        self.ns = cfg.ns
        self.nc = cfg.nc
        self.nq = cfg.nq
        self.data_vector_length = cfg.data_vector_length
        self.model_select = cfg.model_select
        self.loc_loss_fun = nn.MSELoss()
        self.prototypical_net = PrototypicalNet(
            data_vector_length=cfg.data_vector_length,
            centroid_vector_length=cfg.centroid_vector_length,
            model_select=cfg.model_select,
            use_gpu=cfg.use_gpu,
        )
        self.drift_point_net = DriftPointNet(
            data_vector_length=cfg.data_vector_length,
            centroid_vector_length=cfg.centroid_vector_length,
        )
        self.automatic_weighted_loss = AutomaticWeightedLoss(2)

    def forward(
        self,
        datax: torch.Tensor,
        datay: torch.Tensor,
        locy: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        emb = self.prototypical_net(datax)
        class_loss, class_acc, centroid_matrix = self.prototypical_loss(emb, datay, self.ns)
        pre_loc_y = self.drift_point_net(emb, datax)
        loc_loss = self.loc_loss_fun(pre_loc_y, locy)
        loc_acc = self.cal_loc_acc(pre_loc_y, locy)
        loss = self.automatic_weighted_loss(class_loss, loc_loss)
        return loss, class_acc, loc_acc, centroid_matrix

    def embed(self, datax: torch.Tensor) -> torch.Tensor:
        return self.prototypical_net(datax)

    def cal_loc_acc(self, pre_loc_y: torch.Tensor, locy: torch.Tensor) -> torch.Tensor:
        u = torch.sum(torch.abs(locy - pre_loc_y) ** 2)
        v = torch.sum(torch.abs(locy - torch.mean(locy)) ** 2)
        return 1 - u / (v + 1e-8)

    def prototypical_loss(
        self,
        input_emb: torch.Tensor,
        target: torch.Tensor,
        n_support: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        target_cpu = target.to("cpu")
        input_cpu = input_emb.to("cpu")

        def supp_idxs(c):
            return target_cpu.eq(c).nonzero(as_tuple=False)[:n_support].squeeze(1)

        classes = torch.unique(target_cpu)
        n_classes = len(classes)
        n_query = target_cpu.eq(classes[0].item()).sum().item() - n_support

        support_idxs = list(map(supp_idxs, classes))
        prototypes = torch.stack([input_cpu[idx_list].mean(0) for idx_list in support_idxs])

        query_idxs = torch.stack(
            [
                target_cpu.eq(c).nonzero(as_tuple=False)[n_support:].squeeze(1)
                for c in classes
            ]
        ).view(-1)

        query_samples = input_emb.to("cpu")[query_idxs]
        dists = euclidean_dist(query_samples, prototypes)
        log_p_y = F.log_softmax(-dists, dim=1).view(n_classes, n_query, -1)

        target_inds = torch.arange(0, n_classes).view(n_classes, 1, 1)
        target_inds = target_inds.expand(n_classes, n_query, 1).long()

        loss_val = -log_p_y.gather(2, target_inds).squeeze().view(-1).mean()
        _, y_hat = log_p_y.max(2)
        acc_val = y_hat.eq(target_inds.squeeze()).float().mean()
        return loss_val, acc_val, prototypes


def compute_class_centroids(
    model: JointPrediction,
    x: torch.Tensor,
    y: torch.Tensor,
    n_classes: int = 3,
) -> torch.Tensor:
    """Stable per-class mean embeddings for inference (better than last-episode protos)."""
    model.eval()
    with torch.no_grad():
        emb = model.embed(x).to("cpu")
        y_cpu = y.to("cpu")
        centroids = []
        for c in range(n_classes):
            mask = y_cpu.eq(c)
            if mask.any():
                centroids.append(emb[mask].mean(0))
            else:
                centroids.append(torch.zeros(emb.size(1)))
        return torch.stack(centroids, dim=0)
