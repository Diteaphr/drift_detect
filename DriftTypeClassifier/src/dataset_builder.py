"""
Build train/val/test datasets from generated streams.
Samples = one per drift alert; optional alert timestamp noise.
"""

import json
import warnings
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .generators import StreamSample, generate_all_streams
from .stream_simulator import run_online_classifier
from .feature_extraction import extract_features


CLASS_TO_IDX = {"sudden": 0, "gradual": 1, "incremental": 2}
IDX_TO_CLASS = {0: "sudden", 1: "gradual", 2: "incremental"}


def build_dataset_from_streams(
    streams: List[StreamSample],
    pre_window: int = 150,
    post_window: int = 150,
    n_subwindows: int = 15,
    use_extra_features: bool = False,
    alert_noise_radius: int = 0,
    random_seed: Optional[int] = 42,
) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
    For each stream: run online classifier -> errors; then t_alert = t_drift + noise;
    extract features at t_alert. Returns (X, y, metadata_list).
    """
    rng = np.random.default_rng(random_seed)
    X_list = []
    y_list = []
    meta_list = []
    for s in streams:
        sim = run_online_classifier(s.X, s.y, warm_start=50, random_state=random_seed)
        t_alert = s.t_drift + rng.integers(-alert_noise_radius, alert_noise_radius + 1)
        t_alert = max(0, min(len(sim.errors) - 1, t_alert))
        feat, meta = extract_features(
            sim.errors, t_alert,
            pre_window, post_window, n_subwindows, use_extra_features,
        )
        X_list.append(feat)
        y_list.append(CLASS_TO_IDX[s.drift_type])
        meta_list.append({
            "stream_id": s.stream_id,
            "t_drift": s.t_drift,
            "t_alert": t_alert,
            "drift_type": s.drift_type,
        })
    max_len = max(len(x) for x in X_list)
    X = np.zeros((len(X_list), max_len), dtype=np.float32)
    for i, x in enumerate(X_list):
        X[i, : len(x)] = x
    y = np.array(y_list, dtype=np.int64)
    return X, y, meta_list


def split_by_stream_id(
    stream_ids: np.ndarray,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return train/val/test indices (sample indices, not stream ids)."""
    rng = np.random.default_rng(random_seed)
    unique_ids = np.unique(stream_ids)
    rng.shuffle(unique_ids)
    n = len(unique_ids)
    t = int(n * train_ratio)
    v = int(n * val_ratio)
    train_ids = set(unique_ids[: t])
    val_ids = set(unique_ids[t : t + v])
    test_ids = set(unique_ids[t + v :])
    train_idx = np.where(np.array([i in train_ids for i in stream_ids]))[0]
    val_idx = np.where(np.array([i in val_ids for i in stream_ids]))[0]
    test_idx = np.where(np.array([i in test_ids for i in stream_ids]))[0]
    return train_idx, val_idx, test_idx


def split_train_val_k_fold(
    stream_ids: np.ndarray,
    train_val_idx: np.ndarray,
    n_folds: int = 5,
    random_seed: int = 42,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    K-fold on train+val data: same idea as the diagram.
    - test set is already held out (train_val_idx = indices of non-test samples).
    - Split stream_ids of train_val into K folds by stream_id.
    - Return [(train_idx_f0, val_idx_f0), (train_idx_f1, val_idx_f1), ...]
    so each fold has a different validation set, same test set (not returned here).
    """
    rng = np.random.default_rng(random_seed)
    # stream_id for each sample in train_val
    stream_ids_tv = stream_ids[train_val_idx]
    unique_ids = np.unique(stream_ids_tv)
    rng.shuffle(unique_ids)
    n = len(unique_ids)
    fold_size = max(1, n // n_folds)
    folds = []
    for k in range(n_folds):
        start = k * fold_size
        end = (k + 1) * fold_size if k < n_folds - 1 else n
        val_stream_ids = set(unique_ids[start:end])
        val_mask = np.array([sid in val_stream_ids for sid in stream_ids_tv])
        val_idx = train_val_idx[val_mask]
        train_idx = train_val_idx[~val_mask]
        folds.append((train_idx, val_idx))
    return folds


def build_and_save(
    output_dir: Path,
    config: Dict[str, Any],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate streams, build dataset, split, save .npz and metadata.json. Returns indices."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    streams = generate_all_streams(
        n_streams=config.get("n_streams", 300),
        streams_per_class=config.get("streams_per_class", 100),
        stream_length=config.get("stream_length", 2000),
        n_features=config.get("n_features", 10),
        n_classes=config.get("n_classes", 2),
        drift_position_range=tuple(config.get("drift_position_range", [0.4, 0.6])),
        gradual_window_size=config.get("gradual_window_size", 200),
        incremental_window_size=config.get("incremental_window_size", 400),
        random_seed=config.get("random_seed", 42),
    )

    stream_ids = np.array([s.stream_id for s in streams])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)  # sklearn ConvergenceWarning etc.
        X, y, meta_list = build_dataset_from_streams(
            streams,
            pre_window=config.get("pre_window", 150),
            post_window=config.get("post_window", 150),
            n_subwindows=config.get("n_subwindows", 15),
            use_extra_features=config.get("use_extra_features", False),
            alert_noise_radius=config.get("alert_noise_radius", 20),
            random_seed=config.get("random_seed", 42),
        )

    test_ratio = config.get("test_ratio", 0.15)
    n_folds = config.get("n_folds", 0)

    if n_folds <= 1:
        # Single split: train / val / test
        train_idx, val_idx, test_idx = split_by_stream_id(
            stream_ids,
            config.get("train_ratio", 0.7),
            config.get("val_ratio", 0.15),
            test_ratio,
            config.get("random_seed", 42),
        )
        scale_idx = train_idx
    else:
        # K-fold: fixed test set; train+val split into K folds (each fold = different val set)
        rng = np.random.default_rng(config.get("random_seed", 42))
        unique_ids = np.unique(stream_ids)
        rng.shuffle(unique_ids)
        n = len(unique_ids)
        n_test = max(1, int(n * test_ratio))
        test_ids = set(unique_ids[n - n_test :])
        train_val_ids = set(unique_ids[: n - n_test])
        test_idx = np.where(np.array([i in test_ids for i in stream_ids]))[0]
        train_val_idx = np.where(np.array([i in train_val_ids for i in stream_ids]))[0]
        folds = split_train_val_k_fold(
            stream_ids, train_val_idx,
            n_folds=n_folds,
            random_seed=config.get("random_seed", 42),
        )
        scale_idx = train_val_idx  # use all non-test for scale
        train_idx, val_idx = folds[0][0], folds[0][1]  # for return

    # Standardize features using train (or train+val) statistics so the model sees normalized inputs
    X_mean = np.float32(X[scale_idx].mean(axis=0))
    X_std = np.float32(X[scale_idx].std(axis=0)) + 1e-8
    X = np.float32((X - X_mean) / X_std)

    if n_folds <= 1:
        np.savez(
            output_dir / "dataset.npz",
            X=X, y=y, stream_ids=stream_ids,
            train_idx=train_idx, val_idx=val_idx, test_idx=test_idx,
            n_folds=0, X_mean=X_mean, X_std=X_std,
        )
    else:
        save_dict = {
            "X": X, "y": y, "stream_ids": stream_ids,
            "test_idx": test_idx,
            "n_folds": n_folds,
            "X_mean": X_mean, "X_std": X_std,
        }
        for k, (tr_idx, va_idx) in enumerate(folds):
            save_dict[f"fold{k}_train"] = tr_idx
            save_dict[f"fold{k}_val"] = va_idx
        np.savez(output_dir / "dataset.npz", **save_dict)
    def _to_json(o):
        if hasattr(o, "tolist"):
            return o.tolist()
        if isinstance(o, dict):
            return {k: _to_json(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_to_json(x) for x in o]
        if isinstance(o, (np.integer, np.int64)):
            return int(o)
        if isinstance(o, (np.floating, np.float64)):
            return float(o)
        return o

    with open(output_dir / "metadata.json", "w") as f:
        json.dump({"config": config, "n_samples": int(len(y)), "meta_per_sample": _to_json(meta_list[:5])}, f, indent=2)

    return X, y, train_idx, val_idx, test_idx, stream_ids  # train_idx/val_idx are fold0 when n_folds>1
