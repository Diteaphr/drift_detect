"""Warning-buffer length at each ECPF confirmation on BINARY streams (dual ADWIN, error signal).

Same question as probe_buffer_len() in scripts/probe_regression_fp_mechanisms.py, asked of the
binary data: how often is the reuse decision made on a 1-instance buffer, and does it differ
between hits (warning within 1000 steps after a ground-truth drift) and the rest?

    python probe_binary_buffer.py <max_steps> <csv> [<csv> ...]
"""
import os
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
os.chdir(REPO)

from run_task_matrix import WARM_START, load_stream  # noqa: E402
from src.config import PipelineConfig  # noqa: E402
from src.pipeline import ConceptDriftPipeline  # noqa: E402


def run(path, model_type, kwargs, max_steps):
    X, y, intervals = load_stream(path, max_steps)
    cfg = PipelineConfig(model_type=model_type, model_kwargs=kwargs, use_ecpf=True,
                         ecpf_signal_mode="dual_adwin", ecpf_warning_signal="error",
                         ecpf_drift_signal="error", ecpf_detector_min_instances=30,
                         trace_enabled=True)
    pipe = ConceptDriftPipeline(cfg)
    for _ in pipe.run_stream(X, y, warm_start_samples=WARM_START):
        pass
    starts = [s for s, _ in intervals]
    rows = []
    for e in pipe.tracer._events:
        wt, ct = e["warning_t"], e["confirmation_t"]
        bl = e["stage3"].get("buffer_len")
        hit = any(s <= wt <= s + 1000 for s in starts)
        rows.append((wt, ct, bl, hit))
    return rows, starts


def summarize(name, rows):
    if not rows:
        print("   %-8s n=0" % name)
        return
    bl = np.array([r[2] for r in rows], dtype=float)
    print("   %-8s n=%2d  buf==1: %.2f  median=%.0f  buf<=10: %.2f  lens=%s"
          % (name, len(bl), (bl == 1).mean(), np.median(bl), (bl <= 10).mean(), [int(b) for b in bl]))


if __name__ == "__main__":
    max_steps = int(sys.argv[1])
    for p in sys.argv[2:]:
        for label, mt, kw in (("ht", "ht", {}), ("hf10", "hf", {"n_trees": 10})):
            rows, starts = run(p, mt, kw, max_steps)
            print("%s  %s  gt=%s  confirmations=%d" % (os.path.basename(p), label, starts, len(rows)))
            summarize("all", rows)
            summarize("hits", [r for r in rows if r[3]])
            summarize("non-hit", [r for r in rows if not r[3]])
            print()
