#!/usr/bin/env python3
"""Validate DET3's three fixed presets and render both requested diffs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "configs/presets"
OUT = ROOT / "outputs/det3/preset_diff.md"
names = ["det3_full_dual_adwin_lw0", "det3_full_dual_adwin_lw1", "det3_full_hddm_a_lw1"]
paper = json.loads((P / "ecpf_paper.json").read_text())
e10 = json.loads((P / "e10bft.json").read_text())
arms = [json.loads((P / f"{n}.json").read_text()) for n in names]
for arm in arms:
    assert arm["warm_start"] == 200 and arm["requires"]["river"] == "0.21.2"
    for key, value in paper["config"].items():
        assert arm["config"][key] == value, (arm["name"], key)
    for key in ("ecpf_reference_signal", "ecpf_reference_warmup", "ecpf_leader_guard",
                "ecpf_detector_warning_timeout", "ecpf_guard_frozen_scale"):
        assert arm["config"][key] == e10["config"][key], (arm["name"], key)
assert arms[0]["config"]["ecpf_learn_during_warning"] is False
assert arms[1]["config"]["ecpf_learn_during_warning"] is True
assert arms[2]["config"]["ecpf_zone_detector"] == "hddm_a"
assert "ecpf_zone_detector" not in arms[0]["config"] and "ecpf_zone_detector" not in arms[1]["config"]

lines = ["# DET3 preset 差異：共同 ECPF 論文底座，加上 E10bFT 分類元件", "",
         "**結論：** 三個新臂均保留 `ecpf_paper` 的 strict swap、ECPF fade 與 pool cap 10；從 E10bFT 只取 frozen reference、500 步二次凍結、leader 守衛、1,000 步 warning 逾時及分類不生效的 frozen scale。F-D0/F-D1 只差 lw 開關；F-D1/F-H1 只差 zone detector。", ""]
for base_name, base in (("ecpf_paper.json", paper), ("e10bft.json", e10)):
    lines += [f"## 相對 `{base_name}` 的 config 差異", "",
              "| 欄位 | 基準 | F-D0 | F-D1 | F-H1 |", "|---|---|---|---|---|"]
    keys = sorted(set(base["config"]).union(*(set(a["config"]) for a in arms)))
    for key in keys:
        vals = [base["config"].get(key, "<default>")] + [a["config"].get(key, "<default>") for a in arms]
        if len({json.dumps(x, sort_keys=True) for x in vals}) > 1:
            lines.append("| `" + key + "` | " + " | ".join(f"`{json.dumps(v, ensure_ascii=False)}`" for v in vals) + " |")
    lines.append("")
lines += ["`<default>` 表示該 preset 未明寫、由 `PipelineConfig` 預設決定。E10bFT 未明寫 swap/fade/pool policy，DET3 明寫論文底座值；E10bFT 的 regression task override 未移入，本輪僅分類。`ecpf_guard_frozen_scale=500` 在分類分支不生效。", ""]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines))
print(OUT)
