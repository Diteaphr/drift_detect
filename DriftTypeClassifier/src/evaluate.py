"""
Evaluate trained model: accuracy, macro P/R/F1, confusion matrix, per-class F1.
Supports both ProtoNet (episodic) and StandardClassifier (encoder + linear) checkpoints.
"""

import json
import numpy as np
import torch
from pathlib import Path
from typing import Dict, Any, Optional

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

from .dataset_builder import IDX_TO_CLASS
from .episodic_sampler import DriftDataset, EpisodicSampler
from .models import build_protonet
from .train import build_standard_classifier


def load_config(path: Path) -> dict:
    path = Path(path)
    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml
            with open(path) as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    with open(path) as f:
        return json.load(f)


def evaluate(
    model: torch.nn.Module,
    X: np.ndarray,
    y: np.ndarray,
    n_way: int = 3,
    k_shot: int = 5,
    n_episodes: int = 200,
    device: torch.device = torch.device("cpu"),
    seed: int = 123,
) -> Dict[str, Any]:
    """Episodic evaluation: sample episodes, aggregate predictions, compute metrics."""
    model.eval()
    dataset = DriftDataset(X, y)
    sampler = EpisodicSampler(dataset, n_way=n_way, k_shot=k_shot, q_query=15, n_episodes=n_episodes, seed=seed)
    all_true, all_pred = [], []
    with torch.no_grad():
        for support_x, support_y, query_x, query_y in sampler:
            support_x = support_x.to(device)
            support_y = support_y.to(device)
            query_x = query_x.to(device)
            logits = model(support_x, support_y, query_x)
            pred = logits.argmax(dim=-1)
            all_true.extend(query_y.cpu().tolist())
            all_pred.extend(pred.cpu().tolist())
    y_true = np.array(all_true)
    y_pred = np.array(all_pred)
    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    p_per, r_per, f1_per, _ = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    return {
        "accuracy": float(acc),
        "macro_precision": float(p),
        "macro_recall": float(r),
        "macro_f1": float(f1),
        "per_class_f1": f1_per.tolist(),
        "confusion_matrix": cm.tolist(),
        "class_names": [IDX_TO_CLASS.get(i, str(i)) for i in range(len(f1_per))],
    }


def evaluate_standard(
    model: torch.nn.Module,
    X: np.ndarray,
    y: np.ndarray,
    device: torch.device,
) -> Dict[str, Any]:
    """Standard classifier: forward on all X, return same metrics dict as evaluate()."""
    model.eval()
    with torch.no_grad():
        x_t = torch.from_numpy(X).float().to(device)
        if x_t.dim() == 2:
            x_t = x_t.unsqueeze(-1)
        logits = model(x_t)
        y_pred = logits.argmax(dim=-1).cpu().numpy()
    y_true = y
    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    p_per, r_per, f1_per, _ = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    return {
        "accuracy": float(acc),
        "macro_precision": float(p),
        "macro_recall": float(r),
        "macro_f1": float(f1),
        "per_class_f1": f1_per.tolist(),
        "confusion_matrix": cm.tolist(),
        "class_names": [IDX_TO_CLASS.get(i, str(i)) for i in range(len(f1_per))],
    }


def run_evaluate(
    checkpoint_path: Path,
    data_dir: Path,
    config_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load model and data, run evaluation, return metrics. Supports standard and episodic checkpoints."""
    checkpoint_path = Path(checkpoint_path)
    data_dir = Path(data_dir)
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    config = ckpt.get("config", {})
    if config_path:
        config = {**config, **load_config(config_path)}

    data = np.load(data_dir / "dataset.npz")
    X_test = data["X"][data["test_idx"]]
    y_test = data["y"][data["test_idx"]]
    seq_len = X_test.shape[1]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if config.get("train_mode") == "standard":
        model = build_standard_classifier(seq_len, config, n_classes=3)
        model.load_state_dict(ckpt["model_state"])
        model = model.to(device)
        return evaluate_standard(model, X_test, y_test, device)
    else:
        model = build_protonet(
            seq_len=seq_len,
            input_dim=1,
            d_model=config.get("d_model", 64),
            n_heads=config.get("n_heads", 4),
            n_layers=config.get("n_layers", 3),
            dim_feedforward=config.get("dim_feedforward", 128),
            dropout=0.0,
            embed_dim=config.get("embed_dim", 64),
            n_way=3,
            norm_first=config.get("norm_first", False),
        )
        model.load_state_dict(ckpt["model_state"])
        model = model.to(device)
        return evaluate(
            model, X_test, y_test,
            n_way=3, k_shot=5, n_episodes=200, device=device, seed=42,
        )


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="checkpoints/best.pt")
    ap.add_argument("--data_dir", default="data")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    root = Path(__file__).resolve().parent.parent
    metrics = run_evaluate(root / args.checkpoint, root / args.data_dir, args.config and (root / args.config))
    print(json.dumps(metrics, indent=2))
