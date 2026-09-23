"""Config for Cerqueira et al. drift-injection into real_dataset."""

from __future__ import annotations

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent  # data/injected_real_dataset
REAL_ROOT = SCRIPT_DIR.parent.parent / "real_dataset"

MASTER_SEED = 42
G_IDS = list(range(10))  # g00..g09 Monte Carlo trials (paper uses 50)

# Paper default region for drift onset (text: 50%–80%; ref code used 0.5–0.7)
DRIFT_REGION = (0.5, 0.8)

# Class-prior skip probability (ref: label_skip_proba=0.75 → P(drop)=0.75)
LABEL_SKIP_PROBA = 0.75

# Transition modes (paper): abrupt width=0; gradual width ≤ GRADUAL_WIDTH_MAX
ABRUPTNESS = ("abrupt", "gradual")
GRADUAL_WIDTH_MAX = 1000

# Four injection methods from the paper
DRIFT_METHODS = (
    "class_prior",           # y_prior_skip
    "label_swap",            # y_swaps
    "feature_permutation",   # x_permutations
    "feature_filtering",     # x_exceed_skip
)

# Methods that require discrete class labels
CLASS_ONLY_METHODS = frozenset({"class_prior", "label_swap"})

TASKS = ("binary", "multi_classification")

# Source datasets under data/real_dataset (classification only; paper is classification)
# drift_width: gradual transition length (hard-capped by GRADUAL_WIDTH_MAX)
# max_n: safety cap (real_dataset already keeps ≤100k for long streams)
DATASETS: dict[str, dict] = {
    "ai4i2020": {
        "task": "binary",
        "path": REAL_ROOT / "binary" / "ai4i2020" / "ai4i2020.csv",
        "methods": list(DRIFT_METHODS),
        "drift_width": 500,
        "max_n": None,
    },
    "electricity": {
        "task": "binary",
        "path": REAL_ROOT / "binary" / "electricity" / "electricity.csv",
        "methods": list(DRIFT_METHODS),
        "drift_width": 1000,
        "max_n": None,
    },
    "airlines": {
        "task": "binary",
        "path": REAL_ROOT / "binary" / "airlines" / "airlines.csv",
        "methods": list(DRIFT_METHODS),
        "drift_width": 1000,
        "max_n": 100_000,
    },
    "gas_sensor_drift": {
        "task": "multi_classification",
        "path": REAL_ROOT / "multi_classification" / "gas_sensor_drift" / "gas_sensor_drift.csv",
        "methods": list(DRIFT_METHODS),
        "drift_width": 1000,
        "max_n": None,
    },
    "covertype": {
        "task": "multi_classification",
        "path": REAL_ROOT / "multi_classification" / "covertype" / "covertype.csv",
        "methods": list(DRIFT_METHODS),
        "drift_width": 1000,
        "max_n": 100_000,
    },
}
