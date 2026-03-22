"""Utility helpers."""

import json
import numpy as np
from pathlib import Path
from typing import Any, Dict


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def load_yaml(path: Path) -> Dict[str, Any]:
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        with open(path) as f:
            return json.load(f)


def save_json(obj: Any, path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
