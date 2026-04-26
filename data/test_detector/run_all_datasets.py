import csv
import re
import subprocess
import time
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    python_bin = root / ".venv" / "bin" / "python"
    if not python_bin.exists():
        raise FileNotFoundError(f"Missing virtualenv python: {python_bin}")

    groups = ["gradual_drift", "incremental_drift", "sudden_drift"]
    pattern = re.compile(
        r"Correct detection: TP=(?P<tp>-?\d+), FP=(?P<fp>-?\d+), "
        r"N=(?P<n>-?\d+), score=(?P<score>-?\d+(?:\.\d+)?)%"
    )

    rows = []
    for group in groups:
        data_dir = root / "data" / group
        for csv_path in sorted(data_dir.glob("*.csv")):
            dataset = csv_path.stem
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

            matched = pattern.search(line) if line else None
            row = {
                "group": group,
                "dataset": dataset,
                "return_code": proc.returncode,
                "duration_sec": duration,
                "tp": int(matched.group("tp")) if matched else None,
                "fp": int(matched.group("fp")) if matched else None,
                "n": int(matched.group("n")) if matched else None,
                "score_pct": float(matched.group("score")) if matched else None,
                "correct_detection_line": line,
            }
            rows.append(row)
            print(f"[{group}] {dataset}: {line or '(no line found)'}")

    out_dir = root / "data" / "test_detector"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_out = out_dir / "correct_detection_results.csv"
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
                "correct_detection_line",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    md_out = out_dir / "correct_detection_results.md"
    with md_out.open("w", encoding="utf-8") as f:
        f.write("# Correct Detection Results\n\n")
        f.write("| group | dataset | rc | tp | fp | n | score(%) | duration(s) |\n")
        f.write("|---|---|---:|---:|---:|---:|---:|---:|\n")
        for r in rows:
            tp = "" if r["tp"] is None else r["tp"]
            fp = "" if r["fp"] is None else r["fp"]
            n = "" if r["n"] is None else r["n"]
            score = "" if r["score_pct"] is None else r["score_pct"]
            f.write(
                f"| {r['group']} | {r['dataset']} | {r['return_code']} "
                f"| {tp} | {fp} | {n} | {score} | {r['duration_sec']} |\n"
            )

    print(f"Wrote {csv_out}")
    print(f"Wrote {md_out}")


if __name__ == "__main__":
    main()
