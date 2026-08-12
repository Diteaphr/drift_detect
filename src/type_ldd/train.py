"""
Train the Type-LDD FAN ProtoNet on abrupt/gradual/incremental only (3-way).

Example:
  python -m src.type_ldd.train
  python -m src.type_ldd.train --num-episode 20 --data-sample-num 300  # smoke
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Tuple

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from .config import TypeLDDConfig
from .model import JointPrediction, compute_class_centroids
from .preprocessing import dataframe_to_arrays, load_drift_data_3way, train_test_split_arrays
from .sampler import PrototypicalBatchSampler


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_loaders(
    cfg: TypeLDDConfig,
) -> Tuple[DataLoader, DataLoader, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    print(f"Loading 3-way Type-LDD data from {cfg.data_dir()} ...")
    df = load_drift_data_3way(
        cfg.data_dir(),
        data_vector_length=cfg.data_vector_length,
        data_sample_num=cfg.data_sample_num,
    )
    x, y, loc = dataframe_to_arrays(df, cfg.data_vector_length)
    print(f"Loaded samples: {len(y)} | class counts={dict(zip(*np.unique(y, return_counts=True)))}")

    train_x, train_y, train_loc, test_x, test_y, test_loc = train_test_split_arrays(
        x, y, loc, train_ratio=cfg.train_ratio, seed=cfg.seed
    )
    n_classes = len(np.unique(y))
    if n_classes < cfg.nc:
        raise RuntimeError(
            f"Need at least Nc={cfg.nc} classes, found {n_classes}. Check data_dir."
        )

    train_sampler = PrototypicalBatchSampler(
        labels=train_y,
        classes_per_it=cfg.nc,
        num_samples=cfg.ns + cfg.nq,
        iterations=cfg.iterations,
    )
    test_sampler = PrototypicalBatchSampler(
        labels=test_y,
        classes_per_it=cfg.nc,
        num_samples=cfg.ns + cfg.nq,
        iterations=max(20, cfg.iterations // 5),
    )

    train_ds = TensorDataset(
        torch.FloatTensor(train_x),
        torch.LongTensor(train_y),
        torch.unsqueeze(torch.FloatTensor(train_loc), 1),
    )
    test_ds = TensorDataset(
        torch.FloatTensor(test_x),
        torch.LongTensor(test_y),
        torch.unsqueeze(torch.FloatTensor(test_loc), 1),
    )
    train_loader = DataLoader(train_ds, batch_sampler=train_sampler)
    test_loader = DataLoader(test_ds, batch_sampler=test_sampler)
    return train_loader, test_loader, train_x, train_y, test_x, test_y


def evaluate_episode_loader(model: JointPrediction, loader: DataLoader) -> Tuple[float, float]:
    model.eval()
    class_accs = []
    loc_accs = []
    with torch.no_grad():
        for datax, datay, locy in loader:
            _, class_acc, loc_acc, _ = model(datax, datay, locy)
            class_accs.append(float(class_acc))
            loc_accs.append(float(loc_acc))
    return float(np.mean(class_accs)), float(np.mean(loc_accs))


def evaluate_nearest_centroid(
    model: JointPrediction,
    centroids: torch.Tensor,
    x: np.ndarray,
    y: np.ndarray,
) -> float:
    model.eval()
    with torch.no_grad():
        emb = model.embed(torch.FloatTensor(x)).to("cpu")
        dists = torch.cdist(emb, centroids.to("cpu"))
        pred = torch.argmin(dists, dim=1).numpy()
    return float(np.mean(pred == y))


def train(cfg: TypeLDDConfig) -> Path:
    set_seed(cfg.seed)
    train_loader, test_loader, train_x, train_y, test_x, test_y = build_loaders(cfg)

    use_gpu = bool(cfg.use_gpu and torch.cuda.is_available())
    cfg.use_gpu = use_gpu
    model = JointPrediction(cfg)
    if use_gpu:
        model = model.cuda()

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, step_size=cfg.lr_scheduler_step, gamma=cfg.lr_scheduler_gamma
    )

    train_loss_hist = []
    train_class_hist = []
    train_loc_hist = []
    last_centroids = None

    print(
        f"Training FAN ProtoNet 3-way | episodes={cfg.num_episode} "
        f"Ns={cfg.ns} Nc={cfg.nc} Nq={cfg.nq} iterations/ep={cfg.iterations}"
    )
    for ep in range(cfg.num_episode):
        model.train()
        ep_loss, ep_class, ep_loc = [], [], []
        for datax, datay, locy in train_loader:
            if use_gpu:
                datax = datax.cuda()
                datay = datay.cuda()
                locy = locy.cuda()
            optimizer.zero_grad()
            loss, class_acc, loc_acc, centroid_matrix = model(datax, datay, locy)
            loss.backward()
            optimizer.step()
            ep_loss.append(float(loss.item()))
            ep_class.append(float(class_acc.detach()))
            ep_loc.append(float(loc_acc.detach()))
            last_centroids = centroid_matrix.detach().cpu()

        scheduler.step()
        avg_loss = float(np.mean(ep_loss))
        avg_class = float(np.mean(ep_class))
        avg_loc = float(np.mean(ep_loc))
        train_loss_hist.append(avg_loss)
        train_class_hist.append(avg_class)
        train_loc_hist.append(avg_loc)
        print(
            f"episode {ep:03d} | loss={avg_loss:.4f} "
            f"class_acc={avg_class:.4f} loc_R2={avg_loc:.4f}"
        )

    # Stable class centroids on full train split (for production inference)
    class_centroids = compute_class_centroids(
        model,
        torch.FloatTensor(train_x),
        torch.LongTensor(train_y),
        n_classes=cfg.nc,
    )
    test_ep_class, test_ep_loc = evaluate_episode_loader(model, test_loader)
    test_nn_acc = evaluate_nearest_centroid(model, class_centroids, test_x, test_y)
    print(
        f"Test episodic class_acc={test_ep_class:.4f} loc_R2={test_ep_loc:.4f} | "
        f"nearest-centroid acc={test_nn_acc:.4f}"
    )

    out_dir = Path(cfg.checkpoint_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "fan_joint_model.pt")
    torch.save(class_centroids, out_dir / "class_centroids.pt")
    if last_centroids is not None:
        torch.save(last_centroids, out_dir / "last_episode_centroids.pt")

    meta = cfg.to_dict()
    meta.update(
        {
            "n_train": int(len(train_y)),
            "n_test": int(len(test_y)),
            "test_episodic_class_acc": test_ep_class,
            "test_episodic_loc_r2": test_ep_loc,
            "test_nearest_centroid_acc": test_nn_acc,
            "final_train_class_acc": train_class_hist[-1] if train_class_hist else None,
            "label_map": {"0": "sudden", "1": "gradual", "2": "incremental"},
        }
    )
    with open(out_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    with open(out_dir / "train_history.json", "w") as f:
        json.dump(
            {
                "train_loss": train_loss_hist,
                "train_class_acc": train_class_hist,
                "train_loc_acc": train_loc_hist,
            },
            f,
        )
    print(f"Saved checkpoint to {out_dir}")
    return out_dir


def parse_args() -> TypeLDDConfig:
    p = argparse.ArgumentParser(description="Train Type-LDD FAN ProtoNet (3-way)")
    p.add_argument("--data-root", type=str, default=None)
    p.add_argument("--data-file", type=str, default="drift-50-15-4800")
    p.add_argument("--data-sample-num", type=int, default=4800)
    p.add_argument("--data-vector-length", type=int, default=50)
    p.add_argument("--num-episode", type=int, default=600)
    p.add_argument("--iterations", type=int, default=200)
    p.add_argument("--ns", type=int, default=5)
    p.add_argument("--nc", type=int, default=3)
    p.add_argument("--nq", type=int, default=5)
    p.add_argument("--lr", type=float, default=0.01)
    p.add_argument("--model-select", type=str, default="FAN")
    p.add_argument("--checkpoint-dir", type=str, default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gpu", action="store_true")
    args = p.parse_args()

    cfg = TypeLDDConfig(
        data_file=args.data_file,
        data_sample_num=args.data_sample_num,
        data_vector_length=args.data_vector_length,
        num_episode=args.num_episode,
        iterations=args.iterations,
        ns=args.ns,
        nc=args.nc,
        nq=args.nq,
        lr=args.lr,
        model_select=args.model_select,
        seed=args.seed,
        use_gpu=args.gpu,
    )
    if args.data_root:
        cfg.data_root = Path(args.data_root)
    if args.checkpoint_dir:
        cfg.checkpoint_dir = Path(args.checkpoint_dir)
    return cfg


def main() -> None:
    cfg = parse_args()
    train(cfg)


if __name__ == "__main__":
    main()
