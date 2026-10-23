"""A completed DET1 run is skipped only with matching provenance."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

import scripts.run_benchmark as benchmark


class TestDet1Resume(unittest.TestCase):
    def test_summary_handles_object_typed_comparability_after_partial_failures(self):
        df = pd.DataFrame({
            "preset": ["a", "a"], "cell": [None, None],
            "acc_prequential": [0.5, 0.6],
            "comparable": pd.Series([False, False], dtype=object),
            "not_comparable_reason": ["truncated", "truncated"],
        })
        benchmark.print_summary(df, {"required_metrics": ["acc_prequential"],
                                     "comparability_note": "dev"})

    def test_complete_run_skips_but_commit_and_hash_mismatch_refuse(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            run_dir = repo / "out" / "run"
            run_dir.mkdir(parents=True)
            source = repo / "data.csv"
            source.write_text("y\n0\n")
            entry = {"comparable": True, "comparable_kinds": None}
            preset = {"name": "det1_test", "kind": "pipeline"}
            git = {"commit": "abc123", "dirty": False}
            job = {
                "run_dir": str(run_dir), "dataset": "dummy", "source": {
                    "kind": "file", "csv": str(source), "stem": "data",
                },
                "entry": entry, "preset": preset, "seed": None,
                "max_steps": 10, "git": git, "version_problems": [],
                "record_warning_events": False,
            }
            digest = benchmark.sha256_of(source)
            manifest = {
                "dataset": "dummy", "stream": "data", "preset": preset,
                "registry_entry": entry, "seed": None, "max_steps": 10,
                "git": git, "version_problems": [], "cell": None,
                "record_warning_events": False,
                "data": {"file": "data.csv", "sha256": digest},
                "runtime_s": 1.0,
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest))
            (run_dir / "metrics.json").write_text(json.dumps({"acc_prequential": 0.5}))
            np.savez(run_dir / "preds.npz", y_true=[0], y_pred=[0],
                     alarm_idx=[], alarm_ts=[])
            with patch.object(benchmark, "REPO", repo):
                row = benchmark.resumable_row(job, digest)
                self.assertEqual(row["acc_prequential"], 0.5)
                with self.assertRaisesRegex(ValueError, "data SHA-256"):
                    benchmark.resumable_row(job, "different")
                changed = dict(job, git={"commit": "new", "dirty": False})
                with self.assertRaisesRegex(ValueError, "git"):
                    benchmark.resumable_row(changed, digest)
                (run_dir / "metrics.json").unlink()
                self.assertIsNone(benchmark.resumable_row(job, digest))


if __name__ == "__main__":
    unittest.main()
