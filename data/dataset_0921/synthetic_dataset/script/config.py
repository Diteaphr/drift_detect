"""Central parameters for synthetic_dataset generation."""

from __future__ import annotations

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent  # data/synthetic_dataset

MASTER_SEED = 42

# Defaults for full generation
N_SAMPLES = 100_000
G_IDS = list(range(10))  # g00..g09

# Transition widths (hard caps)
SUDDEN_WIDTH = 50
GRADUAL_WIDTH = 1000  # <= 1000
INCR_ANNOTATION_WIDTH = 1000  # annotated transition / monitor window <= 1000

# Drift count range (full runs)
N_DRIFTS_MIN = 5
N_DRIFTS_MAX = 10

# Smoke-test friendly minimum segment length; full runs keep this low like joe
MIN_SEGMENT_LEN = 2

# Binary
BINARY_SEA_FEATURES = 3  # x0,x1,x2
BINARY_HYPERPLANE_FEATURES = 2  # x0,x1 (align old dataset)
HYPERPLANE_MAG_CHANGE = 0.1
HYPERPLANE_NOISE = 0.05

# Multi-class RandomRBF
MULTI_N_CLASSES = 4
MULTI_N_FEATURES = 10
MULTI_N_CENTROIDS = 50
MULTI_INCR_CHANGE_SPEED = 0.01
MULTI_INCR_N_DRIFT_CENTROIDS = 45

# Regression Friedman
REG_N_FEATURES = 10
REG_JUMP_SCALE = 1.0
REG_INCR_PARAM_STEP = 8e-8

TASKS = ("binary", "multi_classification", "regression")
DRIFT_TYPES = ("sudden", "gradual", "incremental", "recurring")
RECURRING_MODES = ("sudden", "gradual", "incremental")
