"""
Train FAN ProtoNet with episodic few-shot learning.
"""

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dataset_builder import build_and_save, CLASS_TO_IDX, IDX_TO_CLASS
from src.episodic_sampler import DriftDataset, EpisodicSampler
from src.models import build_protonet
from src.models.fan_encoder import FANEncoder, MLPEncoder


def load_config(config_path: Path) -> dict:
    try:
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception:
        with open(config_path) as f:
            return json.load(f)


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int = 3) -> float:
    from sklearn.metrics import f1_score
    return float(f1_score(y_true, y_pred, average="macro", zero_division=0))


class StandardClassifier(nn.Module):
    """FAN encoder + linear head for 3-way classification. Used when train_mode=standard."""

    def __init__(self, encoder: nn.Module, embed_dim: int, n_classes: int = 3):
        super().__init__()
        self.encoder = encoder
        self.head = nn.Linear(embed_dim, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T) or (B, T, 1)
        return self.head(self.encoder(x))


def build_standard_classifier(seq_len: int, config: dict, n_classes: int = 3) -> StandardClassifier:
    encoder_type = config.get("encoder_type", "fan").lower()
    embed_dim = config.get("embed_dim", 64)
    if encoder_type == "mlp":
        encoder = MLPEncoder(seq_len=seq_len, input_dim=1, hidden_dim=64, embed_dim=embed_dim)
    else:
        encoder = FANEncoder(
            input_dim=1,
            d_model=config.get("d_model", 64),
            n_heads=config.get("n_heads", 4),
            n_layers=config.get("n_layers", 3),
            dim_feedforward=config.get("dim_feedforward", 128),
            dropout=config.get("dropout", 0.1),
            embed_dim=embed_dim,
            use_pos_encoding=True,
            max_len=seq_len + 10,
            norm_first=config.get("norm_first", False),
        )
    return StandardClassifier(encoder, embed_dim, n_classes)


def evaluate_protonet_episodic(
    model: nn.Module,
    X: np.ndarray,
    y: np.ndarray,
    n_way: int = 3,
    k_shot: int = 5,
    n_episodes: int = 50,
    device: torch.device = torch.device("cpu"),
    seed: int = 42,
) -> float:
    """Sample episodes from (X, y), run ProtoNet, return mean query macro-F1. Used for val and test."""
    model.eval()
    dataset = DriftDataset(X, y)
    sampler = EpisodicSampler(dataset, n_way=n_way, k_shot=k_shot, q_query=15, n_episodes=n_episodes, seed=seed)
    f1_list = []
    with torch.no_grad():
        for support_x, support_y, query_x, query_y in sampler:
            support_x = support_x.to(device)
            support_y = support_y.to(device)
            query_x = query_x.to(device)
            query_y = query_y.to(device)
            logits = model(support_x, support_y, query_x)
            pred = logits.argmax(dim=-1)
            f1_list.append(macro_f1(query_y.cpu().numpy(), pred.cpu().numpy(), n_way))
    return float(np.mean(f1_list))


def _evaluate_test_set(
    ckpt_path: Path,
    X: np.ndarray,
    y: np.ndarray,
    test_idx: np.ndarray,
    seq_len: int,
    config: dict,
    device: torch.device,
    n_episodes: int = 100,
    seed: int = 12345,
) -> float:
    """Load best checkpoint, evaluate on test set (episodic), return test_macro_f1."""
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=True)
    model = build_protonet(
        seq_len=seq_len,
        input_dim=1,
        d_model=config.get("d_model", 64),
        n_heads=config.get("n_heads", 4),
        n_layers=config.get("n_layers", 3),
        dim_feedforward=config.get("dim_feedforward", 128),
        dropout=config.get("dropout", 0.1),
        embed_dim=config.get("embed_dim", 64),
        n_way=config.get("n_way", 3),
        norm_first=config.get("norm_first", False),
    ).to(device)
    model.load_state_dict(ckpt["model_state"])
    X_test = X[test_idx]
    y_test = y[test_idx]
    return evaluate_protonet_episodic(
        model,
        X_test,
        y_test,
        n_way=config.get("n_way", 3),
        k_shot=config.get("k_shot", 5),
        n_episodes=n_episodes,
        device=device,
        seed=seed,
    )


def _evaluate_standard(model: nn.Module, X: np.ndarray, y: np.ndarray, device: torch.device) -> float:
    """Standard classifier: forward on all X, return macro F1."""
    model.eval()
    with torch.no_grad():
        x_t = torch.from_numpy(X).float().to(device)
        if x_t.dim() == 2:
            x_t = x_t.unsqueeze(-1)
        logits = model(x_t)
        pred = logits.argmax(dim=-1).cpu().numpy()
    return macro_f1(y, pred, n_classes=3)


def _train_standard_one_split(
    X_train, y_train, X_val, y_val, seq_len, config,
    max_epochs, patience, lr, device, checkpoint_dir,
):
    """Train encoder + linear head with mini-batch CE. No episodic sampling."""
    from torch.utils.data import DataLoader
    # Use dropout=0 for standard mode so encoder can learn (small data)
    config_std = {**config, "dropout": 0.0}
    model = build_standard_classifier(seq_len, config_std, n_classes=3).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    train_dataset = DriftDataset(X_train, y_train)
    loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    print(f"Train samples: {len(X_train)}, val samples: {len(X_val)}")
    best_f1 = 0.0
    no_improve = 0
    for epoch in range(max_epochs):
        model.train()
        total_loss = 0.0
        n_batches = 0
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            if batch_x.dim() == 2:
                batch_x = batch_x.unsqueeze(-1)
            batch_y = batch_y.to(device)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.get("gradient_clip", 1.0))
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1
        val_f1 = _evaluate_standard(model, X_val, y_val, device)
        print(f"Epoch {epoch+1} loss={total_loss/max(1,n_batches):.4f} val_macro_f1={val_f1:.6f}")
        if val_f1 > best_f1:
            best_f1 = val_f1
            no_improve = 0
            torch.save({"epoch": epoch, "model_state": model.state_dict(), "config": config}, checkpoint_dir / "best.pt")
        else:
            no_improve += 1
        if no_improve >= patience:
            print(f"Early stopping. Best val_macro_f1={best_f1:.6f}")
            break
    return model, best_f1


def train(
    config_path: Path = Path("configs/default.yaml"),
    data_dir: Path = Path("data"),
    checkpoint_dir: Path = Path("checkpoints"),
    resume: bool = False,
):
    root = Path(__file__).resolve().parent.parent
    config = load_config(root / config_path)
    data_dir = root / data_dir
    checkpoint_dir = root / checkpoint_dir
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    npz_path = data_dir / "dataset.npz"
    if not npz_path.exists():
        print("Building dataset...")
        build_and_save(data_dir, config)
    data = np.load(npz_path, allow_pickle=False)
    X = data["X"]
    y = data["y"]
    test_idx = data["test_idx"]
    n_folds = int(data.get("n_folds", 0))

    n_way = config.get("n_way", 3)
    k_shot = config.get("k_shot", 5)
    q_query = config.get("q_query", 15)
    episodes_per_epoch = config.get("episodes_per_epoch", 100)
    max_epochs = config.get("max_epochs", 100)
    patience = config.get("early_stopping_patience", 15)
    lr = config.get("lr", 0.02)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seq_len = X.shape[1]
    train_mode = config.get("train_mode", "episodic")

    # Standard mode: encoder + linear layer, mini-batch CE (no episodic). Use to verify encoder can learn.
    if train_mode == "standard":
        train_idx = data["fold0_train"] if n_folds > 1 else data["train_idx"]
        val_idx = data["fold0_val"] if n_folds > 1 else data["val_idx"]
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        print("Train mode: standard (encoder + linear head, no episodic)")
        model, best_val_f1 = _train_standard_one_split(
            X_train, y_train, X_val, y_val, seq_len, config, max_epochs, patience, lr, device, checkpoint_dir
        )
        # Evaluate with best checkpoint
        ckpt = torch.load(checkpoint_dir / "best.pt", map_location=device, weights_only=True)
        model.load_state_dict(ckpt["model_state"])
        test_f1 = _evaluate_standard(model, X[test_idx], y[test_idx], device)
        print(f"\nTest set (final): test_macro_f1 = {test_f1:.6f}")
        return model, best_val_f1

    if n_folds > 1:
        # K-fold: each fold has different validation set; test set is the same for all
        fold_val_f1s = []
        fold_test_f1s = []
        for fold_id in range(n_folds):
            train_idx = data[f"fold{fold_id}_train"]
            val_idx = data[f"fold{fold_id}_val"]
            X_train, y_train = X[train_idx], y[train_idx]
            X_val, y_val = X[val_idx], y[val_idx]
            print(f"\n--- Fold {fold_id + 1}/{n_folds} (val set = fold {fold_id + 1}) ---")
            model, best_val_f1 = _train_one_split(
                X_train, y_train, X_val, y_val, seq_len, config,
                n_way, k_shot, q_query, episodes_per_epoch, max_epochs, patience, lr,
                device, checkpoint_dir, fold_id=fold_id,
            )
            fold_val_f1s.append(best_val_f1)
            # Final metric: evaluate on test set (same for all folds)
            ckpt_path = checkpoint_dir / f"best_fold{fold_id}.pt"
            test_f1 = _evaluate_test_set(ckpt_path, X, y, test_idx, seq_len, config, device, n_episodes=100, seed=12345)
            fold_test_f1s.append(test_f1)
            print(f"Fold {fold_id + 1} test_macro_f1 = {test_f1:.6f}")
        mean_val_f1 = float(np.mean(fold_val_f1s))
        mean_test_f1 = float(np.mean(fold_test_f1s))
        std_test_f1 = float(np.std(fold_test_f1s))
        print(f"\nK-fold done. Mean val_macro_f1 = {mean_val_f1:.6f}")
        print(f"Test set (final): mean test_macro_f1 = {mean_test_f1:.6f} ± {std_test_f1:.6f}")
        return None, mean_val_f1
    else:
        train_idx = data["train_idx"]
        val_idx = data["val_idx"]
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        model, best_val_f1 = _train_one_split(
            X_train, y_train, X_val, y_val, seq_len, config,
            n_way, k_shot, q_query, episodes_per_epoch, max_epochs, patience, lr,
            device, checkpoint_dir, fold_id=None,
        )
        # Final metric: evaluate on test set once (never used during training)
        test_f1 = _evaluate_test_set(
            checkpoint_dir / "best.pt", X, y, test_idx, seq_len, config, device, n_episodes=100, seed=12345
        )
        print(f"\nTest set (final): test_macro_f1 = {test_f1:.6f}")
        return model, best_val_f1


def _train_one_split(
    X_train, y_train, X_val, y_val, seq_len, config,
    n_way, k_shot, q_query, episodes_per_epoch, max_epochs, patience, lr,
    device, checkpoint_dir, fold_id=None,
):
    model = build_protonet(
        seq_len=seq_len,
        input_dim=1,
        d_model=config.get("d_model", 64),
        n_heads=config.get("n_heads", 4),
        n_layers=config.get("n_layers", 3),
        dim_feedforward=config.get("dim_feedforward", 128),
        dropout=config.get("dropout", 0.1),
        embed_dim=config.get("embed_dim", 64),
        n_way=n_way,
        norm_first=config.get("norm_first", False),
    ).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    train_dataset = DriftDataset(X_train, y_train)
    print(f"Train samples: {len(X_train)}, val samples: {len(X_val)}")
    best_f1 = 0.0
    best_epoch = 0
    no_improve = 0
    ckpt_name = (checkpoint_dir / f"best_fold{fold_id}.pt") if fold_id is not None else (checkpoint_dir / "best.pt")

    for epoch in range(max_epochs):
        model.train()
        total_loss = 0.0
        sampler = EpisodicSampler(
            train_dataset, n_way=n_way, k_shot=k_shot, q_query=q_query,
            n_episodes=episodes_per_epoch, seed=config.get("random_seed", 42) + epoch,
        )
        for support_x, support_y, query_x, query_y in sampler:
            support_x = support_x.to(device)
            support_y = support_y.to(device)
            query_x = query_x.to(device)
            query_y = query_y.to(device)
            optimizer.zero_grad()
            logits = model(support_x, support_y, query_x)
            loss = criterion(logits, query_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.get("gradient_clip", 1.0))
            optimizer.step()
            total_loss += loss.item()
        # Vary val seed by epoch so we measure different episodes each time (avoids stuck constant F1)
        val_f1 = evaluate_protonet_episodic(
            model, X_val, y_val,
            n_way=n_way, k_shot=k_shot, n_episodes=50, device=device,
            seed=config.get("random_seed", 42) + 999 + epoch,
        )
        print(f"Epoch {epoch+1} loss={total_loss/episodes_per_epoch:.4f} val_macro_f1={val_f1:.6f}")
        if val_f1 > best_f1:
            best_f1 = val_f1
            best_epoch = epoch + 1
            no_improve = 0
            torch.save({"epoch": epoch, "model_state": model.state_dict(), "config": config}, ckpt_name)
        else:
            no_improve += 1
        if no_improve >= patience:
            print(f"Early stopping. Best val_macro_f1={best_f1:.6f} at epoch {best_epoch}")
            break
    return model, best_f1


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Train drift type classifier")
    p.add_argument("--config", type=Path, default=Path("configs/default.yaml"), help="Config file path")
    p.add_argument("--data_dir", type=Path, default=Path("data"), help="Data directory")
    p.add_argument("--checkpoint_dir", type=Path, default=Path("checkpoints"), help="Checkpoint directory")
    args = p.parse_args()
    train(config_path=args.config, data_dir=args.data_dir, checkpoint_dir=args.checkpoint_dir)
