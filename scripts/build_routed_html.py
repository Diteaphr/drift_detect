"""Fill the routed-confirmation pages in outputs/benchmark_routed/ with their data.

Each page carries its own markup and script; this only (re)writes the data lines
(``const R = ...;``, ``const DEV = ...;``, ``const F = ...;``) from the analysis
outputs, so a page can be regenerated after ``scripts/analyze_routed.py`` reruns.
A fresh page may hold ``__RESULTS__``-style placeholders instead. No metric is
recomputed here.

  python3 scripts/build_routed_html.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "outputs" / "routed"
PAGES = REPO / "outputs" / "benchmark_routed"
# page -> {JS constant: (placeholder, data file)}
SOURCES = {
    "routed_presentation.html": {"R": ("__RESULTS__", "routed_verdict_data.json"),
                                 "DEV": ("__DEV__", "dev_selection.json")},
    "routed_followup.html": {"F": ("__FOLLOWUP__", "followup_verdict_data.json")},
    "routed_simpleclf.html": {"F": ("__SIMPLECLF__", "simpleclf_verdict_data.json")},
    "routed_oracle.html": {"F": ("__ORACLE__", "oracle_verdict_data.json")},
    "routed_step01.html": {"F": ("__STEP01__", "step01_verdict_data.json")},
}


def fill(html: str, const: str, placeholder: str, value: dict) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if html.count(placeholder) == 1:
        return html.replace(placeholder, payload)
    html, n = re.subn(rf"^const {const} = .*;$", lambda _: f"const {const} = {payload};", html, count=1, flags=re.M)
    if n != 1:
        raise SystemExit(f"no {placeholder} or `const {const} = ...;` line to fill")
    return html


def main() -> None:
    for page, consts in SOURCES.items():
        path = PAGES / page
        if not path.exists():
            print(f"skip {page}: not found")
            continue
        html = path.read_text()
        for const, (placeholder, source) in consts.items():
            data = json.loads((RESULTS / source).read_text())
            if data.get("smoke"):
                raise SystemExit(f"{source} comes from smoke runs; rerun the analysis on full runs first")
            html = fill(html, const, placeholder, data)
        path.write_text(html)
        print(f"-> {path.relative_to(REPO)} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
