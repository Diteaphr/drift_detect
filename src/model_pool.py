"""Model pool: save and retrieve models for adaptation (e.g. on recurring drift).

Supports both sklearn model objects (original) and BaseModel instances
(advanced models from the IM concept-drift library).
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional


class ModelPool:
    """
    Stores trained models by id (e.g. concept id or timestamp).
    Supports save, retrieve, list, and find_nearest for recurring drift.

    For BaseModel instances, uses their native ``save()`` / ``load()`` methods
    when persisting to disk.  In-memory storage works for any object type.
    """

    def __init__(self, in_memory: bool = True, cache_dir: Optional[Path] = None):
        self.in_memory = in_memory
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._models: Dict[str, Any] = {}
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def save(self, model_id: str, model: Any) -> None:
        if self.in_memory:
            self._models[model_id] = model
        if self.cache_dir:
            path = self.cache_dir / f"{model_id}.pkl"
            if _is_base_model(model):
                model.save(path)
            else:
                with open(path, "wb") as f:
                    pickle.dump(model, f)

    def retrieve(self, model_id: str) -> Optional[Any]:
        if self.in_memory and model_id in self._models:
            return self._models[model_id]
        if self.cache_dir:
            path = self.cache_dir / f"{model_id}.pkl"
            if path.exists():
                with open(path, "rb") as f:
                    return pickle.load(f)
        return None

    def list_ids(self) -> List[str]:
        if self.in_memory:
            return list(self._models.keys())
        if self.cache_dir and self.cache_dir.exists():
            return [p.stem for p in self.cache_dir.glob("*.pkl")]
        return []

    def remove(self, model_id: str) -> bool:
        removed = False
        if self.in_memory and model_id in self._models:
            del self._models[model_id]
            removed = True
        if self.cache_dir:
            path = self.cache_dir / f"{model_id}.pkl"
            if path.exists():
                path.unlink()
                removed = True
        return removed

    def has(self, model_id: str) -> bool:
        if self.in_memory:
            return model_id in self._models
        if self.cache_dir:
            return (self.cache_dir / f"{model_id}.pkl").exists()
        return False

    def __len__(self) -> int:
        return len(self.list_ids())


def _is_base_model(obj: Any) -> bool:
    """Check if *obj* is a BaseModel instance without importing it at module level."""
    try:
        from .models.base_model import BaseModel
        return isinstance(obj, BaseModel)
    except ImportError:
        return False
