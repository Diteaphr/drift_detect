"""Training / inference config for the Type-LDD 3-way FAN ProtoNet."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "Type-LDD-main" / "input" / "Data"
DEFAULT_CHECKPOINT_DIR = REPO_ROOT / "checkpoints" / "type_ldd"


@dataclass
class TypeLDDConfig:
    # Data (matches Type-LDD-main defaults; 3-way excludes normal)
    data_root: Path = DEFAULT_DATA_ROOT
    data_file: str = "drift-50-15-4800"
    data_sample_num: int = 4800
    data_vector_length: int = 50
    centroid_vector_length: int = 30
    train_ratio: float = 0.8
    # Accuracy-window size used in their data generation (~15 instances / window)
    instances_per_window: int = 15

    # Model
    model_select: str = "FAN"  # FAN | FNN | FCN | RNN | FQN
    use_gpu: bool = False

    # Episodic training (Nc=3 for abrupt/gradual/incremental)
    ns: int = 5
    nc: int = 3
    nq: int = 5
    iterations: int = 200
    num_episode: int = 600
    lr: float = 0.01
    lr_scheduler_gamma: float = 0.9
    lr_scheduler_step: int = 30

    # IO
    checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR
    seed: int = 42

    def data_dir(self) -> Path:
        return Path(self.data_root) / self.data_file

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["data_root"] = str(self.data_root)
        d["checkpoint_dir"] = str(self.checkpoint_dir)
        return d
