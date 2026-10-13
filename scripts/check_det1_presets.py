"""Validate DET1 presets against ecfp_paper and write the stage-four diff."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESETS = ROOT / "configs" / "presets"
OUTPUT = ROOT / "outputs" / "det1" / "preset_diff.md"
ALLOWED_CONFIG = {
    "ecpf_signal_mode", "detector_delta", "detector_delta_w",
    "ecpf_warning_signal", "ecpf_drift_signal", "ecpf_adwin_one_sided",
    "ecpf_detector_warning_timeout", "ecpf_zone_detector",
    "ecpf_learn_during_warning", "ecpf_warning_length",
    "detector_epsilon", "detector_alpha",
}


def check() -> str:
    base = json.loads((PRESETS / "ecpf_paper.json").read_text())
    defaults = json.loads((ROOT / "configs" / "benchmark_defaults.json").read_text())
    suite = defaults["suites"]["det1"]["presets"]
    expected = [
        f"det1_{slug}_lw{lw}"
        for slug in (
            "oracle60", "dual_adwin", "dual_adwin_t1000", "zone_ddm",
            "zone_hddm_a", "zone_rddm", "zone_magseed",
            "zone_magseed_upward",
        )
        for lw in (0, 1)
    ]
    assert suite == ["e10bft", *expected], "DET1 suite has missing/extra/order-changing arms"
    lines = [
        "# 16 個 DET1 ECPF preset 只改已核准欄位；A6 沿用既有檔",
        "",
        "**結論：** 與 `ecpf_paper.json` 比對，16 個 ECPF preset 均保留 HT、ECPF strict swap、fade、pool cap 10、warm start 200 及 River 0.21.2 要求。兩種 warning 訓練開關明寫，A0 只限有 GT 的三組資料，A5u 只作次要分析。`det1` suite 含 16 個新 ECPF preset 與既有 `e10bft` 一次。Detector-only 四組另列，不在 suite 中。來源：[DET1 預註冊與 2026-10-13 修訂](../../docs/ECPF_DET1_預註冊.html)。",
        "",
        "| Preset | 與 `ecpf_paper.config` 不同或新加的欄位 |",
        "|---|---|",
    ]
    for name in expected:
        p = json.loads((PRESETS / f"{name}.json").read_text())
        assert p["name"] == name and p["kind"] == "pipeline" and p["role"] == "ablation"
        assert p["requires"] == base["requires"]
        assert p["warm_start"] == base["warm_start"] == 200
        assert p["seed_param"] == base["seed_param"]
        assert p["task_overrides"] == base["task_overrides"]
        assert p["tasks"] == ["binary", "multiclass"]
        assert p["config"]["ecpf_learn_during_warning"] == name.endswith("lw1")
        assert p["config"]["detector_delta"] == 0.05
        assert p["config"]["detector_delta_w"] == 0.1
        all_keys = set(base["config"]) | set(p["config"])
        diff = {k: p["config"].get(k) for k in sorted(all_keys)
                if p["config"].get(k) != base["config"].get(k)}
        assert set(diff) <= ALLOWED_CONFIG, f"{name}: unauthorized config changes {set(diff)-ALLOWED_CONFIG}"
        for k in set(base["config"]) - ALLOWED_CONFIG:
            assert p["config"][k] == base["config"][k], (name, k)
        if name.startswith("det1_oracle60"):
            assert p["datasets"] == [
                "injected_paper_electricity", "insects_abrupt_balanced",
                "synthetic_multiclass",
            ]
            assert p["config"]["ecpf_signal_mode"] == "oracle_input_60"
        else:
            assert "datasets" not in p
        if name.startswith(("det1_dual_adwin_lw", "det1_dual_adwin_t1000")):
            assert p["config"]["ecpf_adwin_one_sided"] is False
        cells = ", ".join(f"`{k}={json.dumps(v, ensure_ascii=False)}`" for k, v in diff.items())
        lines.append(f"| `{name}` | {cells} |")

    lines += ["", "## Detector-only 四組保持 Cerqueira 的訓練協定", "",
              "| Preset | Detector | 輸入 | 訓練與 reset |", "|---|---|---|---|"]
    for detector in ("ddm", "hddm_a", "rddm", "magseed"):
        p = json.loads((PRESETS / f"det_{detector}.json").read_text())
        assert p["kind"] == "detector" and p["role"] == "detector_reference"
        assert p["detector"] == detector and p["signal"] == "error"
        assert p["learner"] == "ht" and p["min_train_fraction"] == 0.25
        assert p["datasets"] == ["injected_paper_electricity"]
        lines.append(f"| `det_{detector}` | `{detector}` | 0/1 error，前 25% 原始 input 不餵 detector | 單棵 HT 持續訓練，不因警報重置；detector 自身依原始語意維持／重置 |")
    lines += ["", "**來源限制：** `det_magseed` 依 Chen（2016）學位論文、X 解讀與雙向絕對差；尚無 2015 會議版或原作者實作的逐事件對照。A0 使用新增的 `oracle_input_60`，不改既有 `oracle_60`。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite existing output: {OUTPUT}")
    report = check()
    OUTPUT.write_text(report)
    print(OUTPUT)
