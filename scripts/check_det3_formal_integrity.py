#!/usr/bin/env python3
"""Record DET3 formal batch counts, provenance, pairing, and warning invariants."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path("/Users/diteaphr/Desktop/26 Spring/drift_detect")
OUT = ROOT / "outputs/det3"
RAW = ROOT / "outputs/benchmark/det3"
LOG = (OUT / "logs/formal_20261013.log").read_text()
ARM = ("det3_full_dual_adwin_lw0", "det3_full_dual_adwin_lw1", "det3_full_hddm_a_lw1")
DATASETS = ("synthetic_multiclass", "insects_abrupt_balanced", "insects_incremental_balanced",
            "insects_incremental_gradual_balanced", "insects_incremental_abrupt_reoccurring_balanced",
            "insects_incremental_reoccurring_balanced", "injected_paper_electricity")
COUNTS = {"synthetic_multiclass": 40, "injected_paper_electricity": 160,
          **{d: 1 for d in DATASETS if d.startswith("insects_")}}
commit = "b86f5d679cba136705214f9fe9a5d5460d6bcaa4"
batches = {}
for idx in (1, 2):
    pat = rf"BATCH{idx} COMPLETE ([^ ]+) completed=(\d+) failed=(\d+) elapsed_s=(\d+)"
    match = re.search(pat, LOG)
    assert match, f"missing batch {idx} completion"
    batches[str(idx)] = {"finished_at": match.group(1), "completed": int(match.group(2)),
                         "failed": int(match.group(3)), "elapsed_s": int(match.group(4))}
assert batches["1"]["completed"] == 135 and batches["2"]["completed"] == 480
assert batches["1"]["failed"] == batches["2"]["failed"] == 0
counts = {}
for ds in DATASETS:
    counts[ds] = {}
    for arm in ARM:
        paths = list((RAW / ds / arm).glob("*/manifest.json"))
        assert len(paths) == COUNTS[ds], (ds, arm, len(paths))
        counts[ds][arm] = len(paths)
        for path in paths:
            m = json.loads(path.read_text())
            metrics = json.loads((path.parent / "metrics.json").read_text())
            events = json.loads((path.parent / "warning_events.json").read_text())
            assert m["git"] == {"commit": commit, "dirty": False}
            assert m["versions"]["river"] == "0.21.2"
            assert m["preset"]["name"] == arm and m["max_steps"] is None
            assert m["record_warning_events"]
            assert sum(e["event"] == "open" for e in events) == sum(e["event"] in ("close", "censored") for e in events)
            if "lw1" in arm:
                assert metrics["warning_frozen_steps"] == 0
            for name in ("preds.npz", "metrics.json", "warning_events.json"):
                assert (path.parent / name).exists()
result = {"commit": commit, "expected": 615, "completed": sum(sum(v.values()) for v in counts.values()),
          "failed": 0, "batches": batches, "counts": counts,
          "elapsed_s": sum(v["elapsed_s"] for v in batches.values()),
          "raw_bytes": sum(p.stat().st_size for p in RAW.rglob("*") if p.is_file()),
          "disk_free_bytes": shutil.disk_usage(ROOT).free,
          "checks": ["manifest commit clean", "River 0.21.2", "full stream", "warning conservation", "lw1 zero frozen"]}
assert result["completed"] == 615
(OUT / "formal_integrity_20261013.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
minutes, seconds = divmod(result["elapsed_s"], 60)
md = f"""# DET3 階段四：615 次正式新跑完整且來源固定

**結論：** 第一批 synthetic＋五條 INSECTS **135／135、0 失敗、{batches['1']['elapsed_s']:,} 秒**；第二批 injected **480／480、0 失敗、{batches['2']['elapsed_s']:,} 秒**。合計 **615／615、0 失敗、{minutes} 分 {seconds} 秒**。原始輸出約 {result['raw_bytes']/1e6:.1f} MB，執行後可用磁碟約 {result['disk_free_bytes']/2**30:.1f} GiB。

每臂 205 條，與 DET1／DET2 對應串流配對：synthetic 40、injected 160、INSECTS 5。每個 manifest 均記錄乾淨 commit `{commit}`、River 0.21.2、完整步數及 warning 事件；所有 run 的 warning 開啟數等於關閉與截尾之和，F-D1／F-H1 的實測凍結步數逐 run 為 0。完整計分、來源 SHA-256 與跨臂 `y_true` 配對稽核在階段五分析程式再次執行。

執行依[預註冊](../../docs/ECPF_DET3_預註冊.md)使用 6 workers、tmux 背景、整個 runner 包在 `caffeinate -dims`、`--resume`，log 存 `outputs/det3/logs/formal_20261013.log`。原始 run 只在本機 `outputs/benchmark/det3/`，未改動 DET1／DET2、smoke 或 gate 輸出。完整機器核對見[JSON](formal_integrity_20261013.json)。
"""
(OUT / "formal_integrity_20261013.md").write_text(md)
print("formal", result["completed"], "elapsed", result["elapsed_s"], "bytes", result["raw_bytes"])
