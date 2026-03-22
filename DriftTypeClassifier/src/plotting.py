"""Plotting: confusion matrix, t-SNE/PCA of embeddings, training curves."""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Optional


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    save_path: Optional[Path] = None,
) -> None:
    fig, ax = plt.subplots()
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_yticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="black")
    ax.set_title("Confusion matrix")
    fig.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.close()


def plot_embeddings_tsne(
    embeddings: np.ndarray,
    labels: np.ndarray,
    class_names: List[str],
    save_path: Optional[Path] = None,
) -> None:
    try:
        from sklearn.manifold import TSNE
    except ImportError:
        return
    tsne = TSNE(n_components=2, random_state=42)
    X_2d = tsne.fit_transform(embeddings)
    fig, ax = plt.subplots()
    for i, name in enumerate(class_names):
        mask = labels == i
        ax.scatter(X_2d[mask, 0], X_2d[mask, 1], label=name, alpha=0.6)
    ax.legend()
    ax.set_title("t-SNE of embeddings")
    if save_path:
        plt.savefig(save_path)
    plt.close()


def plot_training_curves(
    train_losses: List[float],
    val_metrics: List[float],
    metric_name: str = "val_macro_f1",
    save_path: Optional[Path] = None,
) -> None:
    fig, ax1 = plt.subplots()
    ax1.plot(train_losses, color="tab:blue", label="train_loss")
    ax2 = ax1.twinx()
    ax2.plot(val_metrics, color="tab:orange", label=metric_name)
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax2.set_ylabel(metric_name)
    fig.legend(loc="upper right")
    if save_path:
        plt.savefig(save_path)
    plt.close()
