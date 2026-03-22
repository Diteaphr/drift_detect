#!/usr/bin/env python3
"""
Run and compare different models from the terminal.

Usage:
  python run_compare_models.py --list             # list available model names
  python run_compare_models.py                    # run all models (slow)
  python run_compare_models.py --models baseline_rf baseline_mlp
  python run_compare_models.py --models standard_mlp standard_fan

Models:
  baseline_rf, baseline_mlp   - fast (no training, fit on train set)
  standard_mlp, standard_fan  - train encoder+linear (standard_mlp is fast and gets ~0.7 F1)
  episodic_fan                - train ProtoNet (slowest)
"""

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Model name -> (description, config overrides for neural models, or None for baseline)
MODEL_CONFIGS = {
    "baseline_rf": ("RandomForest on gap features", None),
    "baseline_mlp": ("sklearn MLP on gap features", None),
    "standard_mlp": ("FAN-style MLP encoder + linear (standard CE)", {"train_mode": "standard", "encoder_type": "mlp", "n_folds": 0}),
    "standard_fan": ("FAN encoder + linear (standard CE)", {"train_mode": "standard", "encoder_type": "fan", "n_folds": 0}),
    "standard_fan_light": ("FAN light + linear (standard CE)", {
        "train_mode": "standard", "encoder_type": "fan", "n_folds": 0,
        "d_model": 32, "n_heads": 2, "n_layers": 1, "dim_feedforward": 64,
        "dropout": 0.0, "embed_dim": 32, "norm_first": True,
    }),
    "episodic_fan": ("ProtoNet episodic (full FAN encoder)", {"train_mode": "episodic", "encoder_type": "fan", "n_folds": 0}),
    "episodic_fan_light": ("FAN light + ProtoNet (paper flow: embed → prototypes → nearest)", {
        "train_mode": "episodic", "encoder_type": "fan", "n_folds": 0,
        "d_model": 32, "n_heads": 2, "n_layers": 1, "dim_feedforward": 64,
        "dropout": 0.0, "embed_dim": 32, "norm_first": True,
    }),
}


def ensure_dataset_single_split():
    """Ensure dataset.npz exists and has single split (train_idx, val_idx, test_idx)."""
    data_path = ROOT / "data" / "dataset.npz"
    if not data_path.exists():
        import yaml
        with open(ROOT / "configs" / "default.yaml") as f:
            config = yaml.safe_load(f)
        config["n_folds"] = 0
        from src.dataset_builder import build_and_save
        build_and_save(ROOT / "data", config)
        return
    data = np.load(data_path, allow_pickle=False)
    if int(data.get("n_folds", 0)) > 1:
        # Rebuild with single split so we have train_idx, val_idx, test_idx
        import yaml
        with open(ROOT / "configs" / "default.yaml") as f:
            config = yaml.safe_load(f)
        config["n_folds"] = 0
        from src.dataset_builder import build_and_save
        build_and_save(ROOT / "data", config)


def load_data():
    data = np.load(ROOT / "data" / "dataset.npz", allow_pickle=False)
    X, y = data["X"], data["y"]
    n_folds = int(data.get("n_folds", 0))
    if n_folds > 1:
        train_idx = data["fold0_train"]
        val_idx = data["fold0_val"]
    else:
        train_idx = data["train_idx"]
        val_idx = data["val_idx"]
    test_idx = data["test_idx"]
    return X, y, train_idx, val_idx, test_idx


def run_baseline(name: str, X_train, y_train, X_test, y_test) -> float:
    from src.baseline import train_baseline_rf, train_baseline_mlp, evaluate_baseline
    if name == "baseline_rf":
        clf = train_baseline_rf(X_train, y_train)
    else:
        clf = train_baseline_mlp(X_train, y_train)
    metrics = evaluate_baseline(clf, X_test, y_test)
    return metrics["macro_f1"]


def write_compare_config(name: str, overrides: dict):
    import yaml
    with open(ROOT / "configs" / "default.yaml") as f:
        config = yaml.safe_load(f)
    config.update(overrides)
    out = ROOT / "configs" / f"compare_{name}.yaml"
    with open(out, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    return out


def run_train(name: str, config_path: Path, checkpoint_dir: Path) -> bool:
    cmd = [
        sys.executable, "-m", "src.train",
        "--config", str(config_path),
        "--data_dir", str(ROOT / "data"),
        "--checkpoint_dir", str(checkpoint_dir),
    ]
    ret = subprocess.run(cmd, cwd=str(ROOT))
    return ret.returncode == 0


def evaluate_checkpoint(ckpt_path: Path, X_test: np.ndarray, y_test: np.ndarray, device: torch.device) -> float:
    """Load checkpoint (standard or ProtoNet) and return test macro F1."""
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    config = ckpt.get("config", {})
    seq_len = X_test.shape[1]

    if config.get("train_mode") == "standard":
        from src.train import build_standard_classifier, _evaluate_standard
        model = build_standard_classifier(seq_len, config, n_classes=3).to(device)
        model.load_state_dict(ckpt["model_state"])
        return _evaluate_standard(model, X_test, y_test, device)
    else:
        from src.train import _evaluate_test_set
        test_idx = np.arange(len(y_test))
        return _evaluate_test_set(
            ckpt_path, X_test, y_test, test_idx, seq_len, config, device, n_episodes=100, seed=12345,
        )


def main():
    parser = argparse.ArgumentParser(description="Run and compare drift type classifier models")
    parser.add_argument("--models", nargs="+", default=["all"],
                        help="Model names (or 'all'). Use --list to see names.")
    parser.add_argument("--list", action="store_true", help="List available model names and exit")
    args = parser.parse_args()

    if args.list:
        print("Available models:")
        for name, (desc, _) in MODEL_CONFIGS.items():
            print(f"  {name}: {desc}")
        return

    if args.models == ["all"]:
        to_run = list(MODEL_CONFIGS.keys())
    else:
        to_run = args.models
        for m in to_run:
            if m not in MODEL_CONFIGS:
                print(f"Unknown model: {m}. Use --list to see names.", file=sys.stderr)
                sys.exit(1)

    ensure_dataset_single_split()
    X, y, train_idx, val_idx, test_idx = load_data()
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    results = []

    for name in to_run:
        desc, overrides = MODEL_CONFIGS[name]
        print(f"\n--- {name}: {desc} ---")
        if overrides is None:
            test_f1 = run_baseline(name, X_train, y_train, X_test, y_test)
            results.append((name, None, test_f1))
            print(f"  Test macro F1: {test_f1:.4f}")
        else:
            config_path = write_compare_config(name, overrides)
            ckpt_dir = ROOT / "checkpoints" / f"compare_{name}"
            ckpt_dir.mkdir(parents=True, exist_ok=True)
            ok = run_train(name, config_path, ckpt_dir)
            ckpt_path = ckpt_dir / "best.pt"
            if ok and ckpt_path.exists():
                test_f1 = evaluate_checkpoint(ckpt_path, X_test, y_test, device)
                results.append((name, None, test_f1))
                print(f"  Test macro F1: {test_f1:.4f}")
            else:
                results.append((name, None, float("nan")))
                print("  Failed or no checkpoint.")

    print("\n" + "=" * 60)
    print("COMPARISON (Test macro F1)")
    print("=" * 60)
    for name, _, test_f1 in results:
        if np.isnan(test_f1):
            print(f"  {name}: —")
        else:
            print(f"  {name}: {test_f1:.4f}")
    print()


if __name__ == "__main__":
    main()
