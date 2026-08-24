"""Insert repository root on sys.path so generators can import drift_common."""

from __future__ import annotations

import os
import sys


def ensure_repo_root() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    return root
