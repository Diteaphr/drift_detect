"""Inspect a dataset and report what the pipeline will do with it.

Point this at a teammate's CSV before running anything. It reports the inferred
task type, which model backends can actually carry that task, which detectors are
statistically valid for it, and a ready-to-run command -- so a mismatch surfaces
here rather than as a strange number three hours into a grid search.

Usage
-----
    python scripts/inspect_dataset.py path/to/data.csv
    python scripts/inspect_dataset.py path/to/folder --target label
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings
from typing import List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model_adapter import (  # noqa: E402
    MULTICLASS_MODEL_TYPES,
    REGRESSION_MODEL_TYPES,
)
from src.task import BINOMIAL_DETECTORS, REAL_VALUED_DETECTORS, TaskType, infer_task  # noqa: E402

BINARY_MODEL_TYPES = ("linear", "nonlinear", "elastic", "rf", "ht", "hf", "xgb", "gru")


def find_target_column(df: pd.DataFrame, declared: Optional[str]) -> str:
    if declared:
        if declared not in df.columns:
            raise SystemExit("target column %r not found; columns are %s"
                             % (declared, list(df.columns)))
        return declared
    for candidate in ("y", "label", "target", "class"):
        if candidate in df.columns:
            return candidate
    # Fall back to the last column, which is the usual stream-data convention.
    return df.columns[-1]


def describe(path: str, target: Optional[str]) -> None:
    df = pd.read_csv(path)
    tcol = find_target_column(df, target)
    y = df[tcol].values
    feats = [c for c in df.columns if c != tcol]

    print("=" * 78)
    print(os.path.basename(path))
    print("=" * 78)
    print("  rows            : %d" % len(df))
    print("  feature columns : %d  %s" % (len(feats), feats[:8] + (["..."] if len(feats) > 8 else [])))
    print("  target column   : %r  dtype=%s" % (tcol, y.dtype))

    non_numeric = y.dtype.kind in ("U", "S", "O")
    n_unique = len(pd.unique(y))
    print("  distinct values : %d" % n_unique)
    if not non_numeric:
        finite = np.asarray(y, dtype=np.float64)
        finite = finite[np.isfinite(finite)]
        n_missing = len(y) - len(finite)
        if n_missing:
            print("  WARNING         : %d non-finite target values (NaN/inf)" % n_missing)
        if finite.size:
            print("  target range    : [%.4g, %.4g]" % (finite.min(), finite.max()))

    try:
        spec = infer_task(y)
    except ValueError as exc:
        print("\n  CANNOT INFER TASK: %s" % exc)
        return

    print()
    print("  INFERRED TASK   : %s" % spec.describe())

    gt = os.path.splitext(path)[0] + "_drift_times.txt"
    print("  ground truth    : %s" % (gt if os.path.exists(gt) else
                                      "MISSING (%s) -- TP/FP cannot be scored" % os.path.basename(gt)))

    if spec.task_type is TaskType.REGRESSION:
        models: List[str] = sorted(REGRESSION_MODEL_TYPES)
        note = "classification backends will be rejected"
        detectors = sorted(REAL_VALUED_DETECTORS)
        det_note = ("%s are INVALID here (binomial bounds need a Bernoulli error stream)"
                    % sorted(BINOMIAL_DETECTORS))
        signals = "'error' or 'uq_variance' (needs model_type='hfr')"
    elif spec.task_type is TaskType.MULTICLASS:
        models = sorted(MULTICLASS_MODEL_TYPES)
        note = "'elastic' is binary-only and now raises instead of silently capping itself"
        detectors = sorted(REAL_VALUED_DETECTORS | BINOMIAL_DETECTORS)
        det_note = "all detectors valid"
        signals = "'error', or any uq_* signal with model_type='hf'"
    else:
        models = sorted(BINARY_MODEL_TYPES)
        note = "the historical case; every backend applies"
        detectors = sorted(REAL_VALUED_DETECTORS | BINOMIAL_DETECTORS)
        det_note = "all detectors valid"
        signals = "'error', or any uq_* signal with model_type='hf'"

    print()
    print("  usable backends : %s" % ", ".join(models))
    print("                    (%s)" % note)
    print("  usable detectors: %s" % ", ".join(detectors))
    print("                    (%s)" % det_note)
    print("  usable signals  : %s" % signals)

    stem = os.path.splitext(os.path.basename(path))[0]
    print()
    print("  run it:")
    print("    python scripts/run_task_matrix.py --data %s \\" % path.replace("\\", "/"))
    print("        --out-dir outputs/%s --max-steps %d" % (stem, min(len(df), 20000)))
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="CSV file or a folder of CSVs")
    ap.add_argument("--target", default=None, help="target column name (default: y/label/target/class, else last)")
    args = ap.parse_args()

    if os.path.isdir(args.path):
        paths = sorted(os.path.join(args.path, f)
                       for f in os.listdir(args.path) if f.endswith(".csv"))
        if not paths:
            raise SystemExit("no CSV files under %s" % args.path)
    else:
        paths = [args.path]

    for p in paths:
        describe(p, args.target)


if __name__ == "__main__":
    main()
