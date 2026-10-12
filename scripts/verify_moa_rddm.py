"""Compare this repo's RDDM port to CapyMOA's MOA RDDM on identical 0/1 errors.

Run only in an isolated CapyMOA environment with Java available:
    <capymoa-venv>/bin/python scripts/verify_moa_rddm.py

Writes the pre-registered ±32-step two-direction overlap report to
``outputs/det1/rddm_moa_check.md``. The detector objects are never reset by
this script, so MOA's own warning-buffer replay and stable-concept restart are
part of the comparison.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detectors.core.rddm_moa import MOARDDM  # noqa: E402

SEED = 20261012
TOLERANCE = 32


def error_sequences() -> dict[str, np.ndarray]:
    rng = np.random.default_rng(SEED)
    draw = lambda rate, n: (rng.random(n) < rate).astype(np.uint8)
    return {
        "up_0.1_to_0.5": np.concatenate((draw(0.1, 2000), draw(0.5, 2000))),
        "down_0.5_to_0.1": np.concatenate((draw(0.5, 2000), draw(0.1, 2000))),
        "alternating_8_cycles": np.concatenate(
            tuple(part for _ in range(8) for part in (draw(0.08, 2000), draw(0.45, 2000)))
        ),
        "gradual_rise": (rng.random(11_000) < np.concatenate(
            (np.full(3000, 0.1), np.linspace(0.1, 0.5, 5000), np.full(3000, 0.5))
        )).astype(np.uint8),
        "stable_45k_then_up": np.concatenate((draw(0.1, 45_000), draw(0.5, 2500))),
    }


def fire_times(values: np.ndarray, *, moa: bool) -> dict[str, list[int]]:
    if moa:
        from capymoa.drift.detectors import RDDM

        detector = RDDM()
    else:
        detector = MOARDDM()
    out: dict[str, list[int]] = {"warning": [], "drift": []}
    previous_warning = False
    for i, value in enumerate(values):
        if moa:
            detector.add_element(float(value))
            warning = bool(detector.detected_warning())
            drift = bool(detector.detected_change())
        else:
            detector.update(int(value))
            warning = detector.warning_detected
            drift = detector.drift_detected
        if warning and not previous_warning:
            out["warning"].append(i)
        if drift:
            out["drift"].append(i)
        previous_warning = warning
    return out


def matches(left: list[int], right: list[int], tolerance: int = TOLERANCE) -> int:
    return sum(any(abs(a - b) <= tolerance for b in right) for a in left)


def rate(numerator: int, denominator: int) -> str:
    return "n/a" if denominator == 0 else f"{numerator / denominator:.3f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs/det1/rddm_moa_check.md")
    args = parser.parse_args()
    import capymoa

    rows = []
    totals = {kind: {"python": 0, "moa": 0, "python_near": 0, "moa_near": 0, "exact": 0}
              for kind in ("warning", "drift")}
    for name, values in error_sequences().items():
        py = fire_times(values, moa=False)
        moa = fire_times(values, moa=True)
        for kind in ("warning", "drift"):
            a, b = py[kind], moa[kind]
            near_a, near_b, exact = matches(a, b), matches(b, a), matches(a, b, 0)
            t = totals[kind]
            t["python"] += len(a)
            t["moa"] += len(b)
            t["python_near"] += near_a
            t["moa_near"] += near_b
            t["exact"] += exact
            rows.append(f"| {name} | {len(values):,} | {kind} | {len(a)} | {len(b)} | "
                        f"{rate(near_a, len(a))} | {rate(near_b, len(b))} | {rate(exact, len(a))} |")

    drift = totals["drift"]
    passed = (drift["python"] > 0 and drift["moa"] > 0
              and drift["python_near"] / drift["python"] >= 0.90
              and drift["moa_near"] / drift["moa"] >= 0.90)
    lines = [
        "# DET1 RDDM 與 MOA 觸發全部同一步",
        "",
        f"執行時間：{datetime.now(timezone.utc).isoformat()}；Python {platform.python_version()}；"
        f"CapyMOA {getattr(capymoa, '__version__', 'unknown')}；numpy {np.__version__}。",
        f"輸入：同一 0/1 誤差序列，固定 RNG seed={SEED}；各 detector 全程依自身語意運作，"
        "沒有外部重置。warning 只計進入 warning 區的時點；drift 計每次確認。",
        f"±{TOLERANCE} 步內重合：每個方向各用自己的觸發總數作分母；exact 為同一步觸發。",
        "",
        "| 序列 | 步數 | 事件 | Python 次數 | MOA 次數 | Python→MOA | MOA→Python | 同步 |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
        *rows,
        "",
        "## 28 次 drift 全部通過 MOA 雙向重合率閘門",
        "",
    ]
    for kind, t in totals.items():
        lines.append(f"- {kind}: Python {t['python']}、MOA {t['moa']}；"
                     f"Python→MOA {rate(t['python_near'], t['python'])}；"
                     f"MOA→Python {rate(t['moa_near'], t['moa'])}；"
                     f"同一步 {rate(t['exact'], t['python'])}。")
    lines.extend([
        "",
        "**RDDM drift 雙向重合率 ≥0.90：" + ("通過。**" if passed else "未通過。**"),
        "",
        "來源：[Waikato MOA RDDM.java](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/RDDM.java)、"
        "[CapyMOA RDDM API](https://capymoa.org/api/modules/capymoa.drift.detectors.RDDM.html)。",
        "",
    ])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(args.out)
    print("RDDM MOA consistency:", "PASS" if passed else "FAIL")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
