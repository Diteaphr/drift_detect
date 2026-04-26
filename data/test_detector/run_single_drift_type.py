import argparse
import ast
import csv
import re
import subprocess
import time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")


ALERT_PATTERN = re.compile(r"Pipeline Alert -> Drift at t=(?P<ts>\d+):")
CD_PATTERN = re.compile(
    r"Correct detection: TP=(?P<tp>-?\d+), FP=(?P<fp>-?\d+), "
    r"N=(?P<n>-?\d+), score=(?P<score>-?\d+(?:\.\d+)?)%"
)


def parse_alert_timestamps(stdout_text: str) -> list[int]:
    return [int(m.group("ts")) for m in ALERT_PATTERN.finditer(stdout_text)]


def load_drift_intervals(path: Path) -> list[tuple[int, int]]:
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    parsed = ast.literal_eval(raw)
    intervals: list[tuple[int, int]] = []
    for item in parsed:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            start = int(item[0])
            end = int(item[1])
            if start > end:
                start, end = end, start
            intervals.append((start, end))
    return intervals


def is_in_intervals(timestamp: int, intervals: list[tuple[int, int]]) -> bool:
    return any(start <= timestamp <= end for start, end in intervals)


def draw_alert_plot(
    csv_path: Path,
    intervals: list[tuple[int, int]],
    alert_timestamps: list[int],
    out_path: Path,
    *,
    window_size: int = 1000,
) -> None:
    df = pd.read_csv(csv_path)
    if "y" not in df.columns:
        raise ValueError(f"Missing 'y' column in {csv_path}")

    y = df["y"].to_numpy()
    n_samples = int(len(y))

    centers: list[float] = []
    ratios: list[float] = []
    for start in range(0, n_samples, window_size):
        end = min(start + window_size, n_samples)
        chunk = y[start:end]
        if len(chunk) == 0:
            continue
        centers.append(start + (end - start) / 2.0)
        ratios.append(float(np.mean(chunk == 0)))

    fig, ax = plt.subplots(figsize=(14, 5))

    if centers:
        bar_width = max(int(window_size * 0.9), 1)
        ax.bar(
            centers,
            ratios,
            width=bar_width,
            color="#e88b7f",
            edgecolor="#666666",
            alpha=0.75,
            label=f"class 0 ratio (per {window_size} samples)",
        )
        ax.plot(
            centers,
            ratios,
            color="#2f8f9d",
            linewidth=1.6,
            label="class 0 ratio trend",
        )

    for i, (start, end) in enumerate(intervals):
        ax.axvspan(
            start,
            end,
            color="#b0b0b0",
            alpha=0.22,
            label="ground-truth drift interval" if i == 0 else None,
        )

    in_labeled = False
    out_labeled = False
    if centers and ratios:
        xp = np.asarray(centers, dtype=float)
        yp = np.asarray(ratios, dtype=float)
        for ts in alert_timestamps:
            yv = float(np.interp(ts, xp, yp))
            if is_in_intervals(ts, intervals):
                ax.scatter(
                    ts,
                    yv,
                    s=55,
                    color="#2ca02c",
                    edgecolor="black",
                    zorder=5,
                    label="alert in interval" if not in_labeled else None,
                )
                in_labeled = True
            else:
                ax.scatter(
                    ts,
                    yv,
                    s=55,
                    color="#d62728",
                    edgecolor="black",
                    zorder=5,
                    label="alert out of interval" if not out_labeled else None,
                )
                out_labeled = True
    else:
        for ts in alert_timestamps:
            color = "#2ca02c" if is_in_intervals(ts, intervals) else "#d62728"
            label = None
            if color == "#2ca02c" and not in_labeled:
                label = "alert in interval"
                in_labeled = True
            if color == "#d62728" and not out_labeled:
                label = "alert out of interval"
                out_labeled = True
            ax.axvline(ts, color=color, linewidth=1.2, linestyle="--", label=label)

    ax.set_title(
        f"{csv_path.stem}: class 0 ratio + drift alerts (green=in, red=out)",
        fontsize=12,
    )
    ax.set_xlabel("Sample index")
    ax.set_ylabel("Class 0 ratio")
    ax.set_ylim(0.0, 1.0)
    ax.set_xlim(0, max(n_samples - 1, 1))
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", framealpha=0.92)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run detector evaluation for a single drift type group.",
    )
    parser.add_argument(
        "--group",
        type=str,
        default="gradual_drift",
        choices=["gradual_drift", "incremental_drift", "sudden_drift"],
        help="Which drift group to run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    python_bin = root / ".venv" / "bin" / "python"
    if not python_bin.exists():
        raise FileNotFoundError(f"Missing virtualenv python: {python_bin}")

    group = args.group
    data_dir = root / "data" / group
    datasets = sorted(data_dir.glob("*.csv"))
    if not datasets:
        raise FileNotFoundError(f"No csv found under: {data_dir}")

    out_dir = root / "data" / "test_detector"
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = out_dir / "plots" / group
    plot_dir.mkdir(parents=True, exist_ok=True)
    csv_out = out_dir / f"correct_detection_{group}.csv"
    md_out = out_dir / f"correct_detection_{group}.md"

    rows = []
    total = len(datasets)
    print(f"[START] group={group}, datasets={total}", flush=True)

    for idx, csv_path in enumerate(datasets, start=1):
        dataset = csv_path.stem
        print(f"[{idx}/{total}] running {dataset} ...", flush=True)
        t0 = time.time()
        proc = subprocess.run(
            [
                str(python_bin),
                "main.py",
                "--data-dir",
                str(data_dir),
                "--dataset",
                dataset,
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        duration = round(time.time() - t0, 2)

        line = ""
        for out_line in proc.stdout.splitlines():
            if out_line.startswith("Correct detection: "):
                line = out_line
                break

        matched = CD_PATTERN.search(line) if line else None
        alert_timestamps = parse_alert_timestamps(proc.stdout)
        interval_path = data_dir / f"{dataset}_drift_times.txt"
        intervals = load_drift_intervals(interval_path)
        in_interval_alerts = sum(1 for ts in alert_timestamps if is_in_intervals(ts, intervals))
        out_interval_alerts = len(alert_timestamps) - in_interval_alerts

        plot_path = plot_dir / f"{dataset}_alerts.png"
        try:
            draw_alert_plot(csv_path, intervals, alert_timestamps, plot_path)
            plot_rel = str(plot_path.relative_to(root))
        except Exception as exc:  # pragma: no cover - visualization should not break benchmark
            plot_rel = f"(plot failed: {exc})"

        row = {
            "group": group,
            "dataset": dataset,
            "return_code": proc.returncode,
            "duration_sec": duration,
            "tp": int(matched.group("tp")) if matched else None,
            "fp": int(matched.group("fp")) if matched else None,
            "n": int(matched.group("n")) if matched else None,
            "score_pct": float(matched.group("score")) if matched else None,
            "alert_count": len(alert_timestamps),
            "in_interval_alerts": in_interval_alerts,
            "out_interval_alerts": out_interval_alerts,
            "alert_timestamps": ";".join(str(ts) for ts in alert_timestamps),
            "alert_plot": plot_rel,
            "correct_detection_line": line,
        }
        rows.append(row)
        print(
            f"[{idx}/{total}] done {dataset} in {duration}s -> "
            f"{line or '(no line found)'}",
            flush=True,
        )

    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "group",
                "dataset",
                "return_code",
                "duration_sec",
                "tp",
                "fp",
                "n",
                "score_pct",
                "alert_count",
                "in_interval_alerts",
                "out_interval_alerts",
                "alert_timestamps",
                "alert_plot",
                "correct_detection_line",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    with md_out.open("w", encoding="utf-8") as f:
        f.write(f"# Correct Detection Results ({group})\n\n")
        f.write("| dataset | rc | tp | fp | n | score(%) | alerts | in | out | duration(s) | plot |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")
        for r in rows:
            tp = "" if r["tp"] is None else r["tp"]
            fp = "" if r["fp"] is None else r["fp"]
            n = "" if r["n"] is None else r["n"]
            score = "" if r["score_pct"] is None else r["score_pct"]
            f.write(
                f"| {r['dataset']} | {r['return_code']} | {tp} | {fp} | "
                f"{n} | {score} | {r['alert_count']} | {r['in_interval_alerts']} | "
                f"{r['out_interval_alerts']} | {r['duration_sec']} | {r['alert_plot']} |\n"
            )

    print(f"[DONE] wrote {csv_out}", flush=True)
    print(f"[DONE] wrote {md_out}", flush=True)


if __name__ == "__main__":
    main()
