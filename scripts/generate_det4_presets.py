#!/usr/bin/env python3
"""Generate and verify the 18 preregistered DET4 ablation presets."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PRESETS = REPO / "configs" / "presets"
REPORT = REPO / "outputs" / "det4" / "preset_diff.md"
BASES = {
    "s0": "det1_dual_adwin_lw0",
    "s1": "det3_full_dual_adwin_lw1",
}
DETECTORS = {
    "adwin": "adwin",
    "hddma": "hddm_a",
    "rddm": "rddm",
}


def expected_presets() -> dict[str, dict]:
    result = {}
    for framework, base_name in BASES.items():
        base = json.loads((PRESETS / f"{base_name}.json").read_text())
        for warning_slug, warning in DETECTORS.items():
            for confirm_slug, confirm in DETECTORS.items():
                name = f"det4_{framework}_w{warning_slug}_c{confirm_slug}"
                preset = copy.deepcopy(base)
                preset.update({
                    "name": name,
                    "role": "ablation",
                    "description": (
                        f"DET4 {framework.upper()}: independent warning={warning} and "
                        f"confirm={confirm} detector arms."
                    ),
                    "source": "docs/ECPF_DET4_預註冊.md",
                })
                preset["config"]["ecpf_warning_detector"] = warning
                preset["config"]["ecpf_drift_detector"] = confirm
                result[name] = preset
    return result


def config_diff(base: dict, preset: dict) -> dict:
    keys = set(base) | set(preset)
    return {key: {"base": base.get(key), "det4": preset.get(key)}
            for key in sorted(keys) if base.get(key) != preset.get(key)}


def write_all(expected: dict[str, dict]) -> None:
    for name, preset in expected.items():
        (PRESETS / f"{name}.json").write_text(
            json.dumps(preset, indent=2, ensure_ascii=False) + "\n"
        )


def verify(expected: dict[str, dict]) -> list[tuple[str, str, dict]]:
    rows = []
    for name, wanted in expected.items():
        path = PRESETS / f"{name}.json"
        if not path.exists():
            raise AssertionError(f"missing preset: {path}")
        actual = json.loads(path.read_text())
        if actual != wanted:
            raise AssertionError(f"preset differs from generator: {path}")
        framework = name.split("_")[1]
        base_name = BASES[framework]
        base = json.loads((PRESETS / f"{base_name}.json").read_text())
        diff = config_diff(base["config"], actual["config"])
        if set(diff) != {"ecpf_warning_detector", "ecpf_drift_detector"}:
            raise AssertionError(f"unexpected execution-config diff for {name}: {sorted(diff)}")
        rows.append((name, base_name, diff))
    return rows


def write_report(rows: list[tuple[str, str, dict]]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# DET4 preset 差異：18 組只改 warning／confirm detector",
        "",
        "**結論：** 18/18 preset 的 `role=ablation`；相對各自 S0／S1 範本，執行 config 的差異只有 `ecpf_warning_detector` 與 `ecpf_drift_detector`。名稱、描述與來源是非執行 metadata。",
        "",
        "| preset | 範本 | warning | confirm | 其他 execution config 差異 |",
        "|---|---|---|---|---|",
    ]
    for name, base_name, diff in rows:
        lines.append(
            f"| `{name}` | `{base_name}` | `{diff['ecpf_warning_detector']['det4']}` | "
            f"`{diff['ecpf_drift_detector']['det4']}` | 無 |"
        )
    lines += [
        "",
        "S0 範本固定 lw0、無 reference／guard／timeout；S1 範本固定 lw1、frozen reference、leader guard 與 1000 步 timeout。`main_preset` 未修改。",
    ]
    REPORT.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify files without rewriting them")
    args = parser.parse_args()
    expected = expected_presets()
    if not args.check:
        write_all(expected)
    rows = verify(expected)
    if not args.check:
        write_report(rows)
    print(f"verified {len(rows)} DET4 presets")


if __name__ == "__main__":
    main()
