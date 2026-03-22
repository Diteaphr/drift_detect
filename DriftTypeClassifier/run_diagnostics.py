"""
Diagnostics: verify data pipeline and check if inputs have signal.
Run from DriftTypeClassifier: python run_diagnostics.py
"""

import sys
from pathlib import Path
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))

def main():
    data_dir = Path(__file__).parent / "data"
    npz_path = data_dir / "dataset.npz"
    if not npz_path.exists():
        print("No dataset.npz found. Run: python -m src.train (will build dataset first)")
        return

    data = np.load(npz_path, allow_pickle=False)
    X = data["X"]
    y = data["y"]
    n_folds = int(data.get("n_folds", 0))

    print("=" * 60)
    print("1. DATA SHAPES AND LABELS")
    print("=" * 60)
    print(f"X shape: {X.shape}  (n_samples, seq_len)")
    print(f"y shape: {y.shape}")
    unique, counts = np.unique(y, return_counts=True)
    for u, c in zip(unique, counts):
        print(f"  class {u}: {c} samples")
    print()

    # Use first fold or single split for diagnostics
    if n_folds > 1:
        train_idx = data[f"fold0_train"]
        val_idx = data[f"fold0_val"]
    else:
        train_idx = data["train_idx"]
        val_idx = data["val_idx"]
    X_train, y_train = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx], y[val_idx]
    print(f"Train: {len(train_idx)}, Val: {len(val_idx)}")
    print()

    print("=" * 60)
    print("2. DO GAP FEATURES DIFFER BY CLASS? (mean vector per class)")
    print("=" * 60)
    for c in range(3):
        mask = y_train == c
        if mask.sum() == 0:
            print(f"  class {c}: no samples")
            continue
        mean_vec = X_train[mask].mean(axis=0)
        std_vec = X_train[mask].std(axis=0)
        print(f"  class {c} (n={mask.sum()}): mean = {mean_vec.round(4)}, std = {std_vec.round(4)}")
    print("  (If all three mean vectors are almost identical, the input has weak signal.)")
    print()

    print("=" * 60)
    print("3. SIMPLE CLASSIFIER ON RAW FEATURES (does input have signal?)")
    print("=" * 60)
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import f1_score
        clf = LogisticRegression(max_iter=500, random_state=42)
        clf.fit(X_train, y_train)
        pred_val = clf.predict(X_val)
        f1 = f1_score(y_val, pred_val, average="macro", zero_division=0)
        print(f"  Logistic regression on raw gap features:")
        print(f"  Val macro F1 = {f1:.4f}")
        if f1 < 0.4:
            print("  -> Low F1: gap features may have weak signal, or data is hard.")
        else:
            print("  -> Input has some signal; ProtoNet might improve with better training.")
    except Exception as e:
        print(f"  Skipped: {e}")
    print()

    print("=" * 60)
    print("4. ONE EPISODE: MODEL FORWARD AND LOGITS")
    print("=" * 60)
    from src.episodic_sampler import DriftDataset, EpisodicSampler
    from src.models import build_protonet

    dataset = DriftDataset(X_train, y_train)
    sampler = EpisodicSampler(dataset, n_way=3, k_shot=5, q_query=15, n_episodes=1, seed=42)
    support_x, support_y, query_x, query_y = next(iter(sampler))

    seq_len = X.shape[1]
    model = build_protonet(
        seq_len=seq_len,
        input_dim=1,
        d_model=64,
        n_heads=4,
        n_layers=3,
        dim_feedforward=128,
        dropout=0.0,
        embed_dim=64,
        n_way=3,
    )
    model.eval()
    with torch.no_grad():
        logits = model(support_x, support_y, query_x)

    print(f"  support_x shape: {support_x.shape}, query_x shape: {query_x.shape}")
    print(f"  logits shape: {logits.shape}  (n_query, n_way)")
    print(f"  logits (first 5 query): {logits[:5].numpy().round(4)}")
    logits_mean = logits.mean().item()
    logits_std = logits.std().item()
    print(f"  logits mean: {logits_mean:.4f}, std: {logits_std:.4f}")
    pred = logits.argmax(dim=-1)
    acc = (pred == query_y).float().mean().item()
    print(f"  Accuracy on this episode (random init): {acc:.4f}")
    if logits_std < 0.1:
        print("  -> Logits almost constant: encoder may be outputting similar embeddings (check init or scale).")
    print()

    print("=" * 60)
    print("5. ONE TRAINING STEP: LOSS AND GRADIENT")
    print("=" * 60)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
    sampler2 = EpisodicSampler(dataset, n_way=3, k_shot=5, q_query=15, n_episodes=1, seed=123)
    support_x, support_y, query_x, query_y = next(iter(sampler2))
    optimizer.zero_grad()
    logits = model(support_x, support_y, query_x)
    loss = torch.nn.functional.cross_entropy(logits, query_y)
    loss.backward()
    print(f"  One episode (untrained): loss = {loss.item():.4f}  (ln(3) ≈ 1.099 = random)")
    grad_norms = [p.grad.norm().item() for p in model.parameters() if p.grad is not None]
    if grad_norms:
        print(f"  Gradient norms: min={min(grad_norms):.6f}, max={max(grad_norms):.6f}")
        if max(grad_norms) < 1e-5:
            print("  -> Gradients very small: possible vanishing gradient or bad scale.")
    else:
        print("  -> No gradients (bug?).")
    print("=" * 60)
    print("6. FIXED PROTOTYPES (train centroids → classify val by nearest)")
    print("=" * 60)
    # If the encoder learned well, mean embedding per class on train should separate;
    # then val assigned to nearest train centroid should get decent F1.
    from src.models import build_protonet
    model2 = build_protonet(
        seq_len=seq_len, input_dim=1, d_model=64, n_heads=4, n_layers=3,
        dim_feedforward=128, dropout=0.0, embed_dim=64, n_way=3,
    )
    model2.eval()
    with torch.no_grad():
        emb_train = model2.encoder(torch.from_numpy(X_train).float().unsqueeze(-1))
        emb_val = model2.encoder(torch.from_numpy(X_val).float().unsqueeze(-1))
    # (n_train, D), (n_val, D)
    centroids = []
    for c in range(3):
        m = (y_train == c)
        if m.sum() > 0:
            centroids.append(emb_train[m].mean(dim=0))
        else:
            centroids.append(emb_train[0] * 0)
    centroids = torch.stack(centroids, dim=0)
    dist = torch.cdist(emb_val, centroids, p=2)
    pred_fixed = dist.argmin(dim=1)
    from sklearn.metrics import f1_score
    f1_fixed = f1_score(y_val, pred_fixed.numpy(), average="macro", zero_division=0)
    print(f"  Untrained encoder: val F1 (nearest train centroid) = {f1_fixed:.4f}")
    print("  (After training, re-run and compare: if this stays ~0.33, encoder is not learning.)")
    print()
    print("=" * 60)
    print("7. PYTORCH LINEAR(14, 3) BASELINE (same data path as FAN)")
    print("=" * 60)
    # If this gets ~0.75 like sklearn LR, the DataLoader/data path is correct; FAN is the issue.
    from torch.utils.data import DataLoader
    linear_model = torch.nn.Sequential(
        torch.nn.Flatten(),
        torch.nn.Linear(14, 3),
    )
    opt = torch.optim.Adam(linear_model.parameters(), lr=0.01)
    train_ds = DriftDataset(X_train, y_train)
    loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    for _ in range(50):
        linear_model.train()
        for bx, by in loader:
            opt.zero_grad()
            logits = linear_model(bx)
            loss = torch.nn.functional.cross_entropy(logits, by)
            loss.backward()
            opt.step()
    linear_model.eval()
    with torch.no_grad():
        logits = linear_model(torch.from_numpy(X_val).float())
        pred = logits.argmax(dim=1).numpy()
    f1_linear = f1_score(y_val, pred, average="macro", zero_division=0)
    print(f"  PyTorch Linear(14, 3) after 50 epochs: val F1 = {f1_linear:.4f}")
    print("  (If this is ~0.75, data path is fine and the issue is the FAN encoder.)")
    print()
    print("SUMMARY: LR on raw features got val F1 ≈ 0.75 → input HAS signal.")
    print("If ProtoNet val F1 stays ~0.33, the issue is episodic training or optimization, not data.")

if __name__ == "__main__":
    main()
