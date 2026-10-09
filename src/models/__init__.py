from .base_model import BaseModel
from .elastic_net import (
    MULTICLASS_CAPABLE_BACKENDS,
    ElasticNetModel,
    MulticlassNotSupportedError,
)
from .random_forest import RandomForestModel
from .hoeffding_tree import HoeffdingTreeModel
from .hoeffding_forest import HoeffdingForestModel
from .regression_models import (
    AdaptiveRandomForestRegressorModel,
    HoeffdingForestRegressorModel,
    HoeffdingTreeRegressorModel,
)

try:
    from .xgboost_model import XGBoostModel
except ImportError:  # Optional dependency.
    XGBoostModel = None

try:
    from .gru_model import GRUModel
except ImportError:  # torch not installed or failed to load
    GRUModel = None

__all__ = [
    "BaseModel",
    "ElasticNetModel",
    "RandomForestModel",
    "XGBoostModel",
    "GRUModel",
    "HoeffdingTreeModel",
    "HoeffdingForestModel",
    # Regression learners (continuous targets).
    "HoeffdingTreeRegressorModel",
    "AdaptiveRandomForestRegressorModel",
    "HoeffdingForestRegressorModel",
    # Task-type guard raised by the binary-only ElasticNet backend.
    "MulticlassNotSupportedError",
    "MULTICLASS_CAPABLE_BACKENDS",
]

