"""Load a trained Type-LDD FAN ProtoNet and classify gap / error sequences."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

import numpy as np
import torch
import torch.nn.functional as F

from ..config import DriftType
from .config import TypeLDDConfig
from .features import errors_to_relative_gaps
from .model import JointPrediction, euclidean_dist

IDX_TO_DRIFT_TYPE = {
    0: DriftType.SUDDEN,
    1: DriftType.GRADUAL,
    2: DriftType.INCREMENTAL,
}


class TypeLDDClassifier:
    """Nearest-centroid classification in FAN embedding space."""

    def __init__(
        self,
        model: JointPrediction,
        centroids: torch.Tensor,
        cfg: TypeLDDConfig,
    ):
        self.model = model
        self.centroids = centroids.to("cpu")
        self.cfg = cfg
        self.model.eval()

    @classmethod
    def from_checkpoint(cls, checkpoint_dir: Union[str, Path]) -> "TypeLDDClassifier":
        checkpoint_dir = Path(checkpoint_dir)
        meta_path = checkpoint_dir / "meta.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"Missing meta.json in {checkpoint_dir}")
        with open(meta_path) as f:
            meta = json.load(f)

        cfg = TypeLDDConfig(
            data_file=meta.get("data_file", "drift-50-15-4800"),
            data_vector_length=int(meta.get("data_vector_length", 50)),
            centroid_vector_length=int(meta.get("centroid_vector_length", 30)),
            model_select=meta.get("model_select", "FAN"),
            instances_per_window=int(meta.get("instances_per_window", 15)),
            nc=int(meta.get("nc", 3)),
            ns=int(meta.get("ns", 5)),
            nq=int(meta.get("nq", 5)),
            use_gpu=False,
            checkpoint_dir=checkpoint_dir,
        )
        model = JointPrediction(cfg)
        state_path = checkpoint_dir / "fan_joint_model.pt"
        try:
            state = torch.load(state_path, map_location="cpu", weights_only=True)
            centroids = torch.load(
                checkpoint_dir / "class_centroids.pt",
                map_location="cpu",
                weights_only=True,
            )
        except TypeError:
            state = torch.load(state_path, map_location="cpu")
            centroids = torch.load(
                checkpoint_dir / "class_centroids.pt",
                map_location="cpu",
            )
        model.load_state_dict(state)
        return cls(model=model, centroids=centroids, cfg=cfg)

    def predict_gaps(self, gaps: np.ndarray) -> DriftType:
        x = np.asarray(gaps, dtype=np.float64).ravel()
        L = self.cfg.data_vector_length
        if len(x) < L:
            x = np.concatenate([x, np.zeros(L - len(x))])
        else:
            x = x[:L]
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
        with torch.no_grad():
            emb = self.model.embed(torch.FloatTensor(x).unsqueeze(0)).to("cpu")
            dists = euclidean_dist(emb, self.centroids)
            pred = int(torch.argmin(dists, dim=1).item())
        return IDX_TO_DRIFT_TYPE.get(pred, DriftType.SUDDEN)

    def predict_errors(self, errors: np.ndarray, drift_timestamp: Optional[int] = None) -> DriftType:
        """Pipeline-facing API: instance errors → relative gaps → type."""
        errs = np.asarray(errors, dtype=np.float64).ravel()
        if drift_timestamp is not None and 0 <= drift_timestamp < len(errs):
            # Use history up to (and including) the alert index.
            errs = errs[: drift_timestamp + 1]
        gaps = errors_to_relative_gaps(
            errs,
            data_vector_length=self.cfg.data_vector_length,
            instances_per_window=self.cfg.instances_per_window,
        )
        return self.predict_gaps(gaps)

    def predict_proba_gaps(self, gaps: np.ndarray) -> np.ndarray:
        x = np.asarray(gaps, dtype=np.float64).ravel()
        L = self.cfg.data_vector_length
        if len(x) < L:
            x = np.concatenate([x, np.zeros(L - len(x))])
        else:
            x = x[:L]
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
        with torch.no_grad():
            emb = self.model.embed(torch.FloatTensor(x).unsqueeze(0)).to("cpu")
            dists = euclidean_dist(emb, self.centroids)
            probs = F.softmax(-dists, dim=1).numpy().ravel()
        return probs


def load_classifier(checkpoint_dir: Optional[Union[str, Path]] = None) -> TypeLDDClassifier:
    from .config import DEFAULT_CHECKPOINT_DIR

    path = Path(checkpoint_dir) if checkpoint_dir is not None else DEFAULT_CHECKPOINT_DIR
    return TypeLDDClassifier.from_checkpoint(path)
