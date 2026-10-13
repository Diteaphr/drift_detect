#!/usr/bin/env bash
# DET3 preregistered run (docs/ECPF_DET3_預註冊.md). Launch from repo root on a clean tree:
#   PYTHON_BIN=/path/to/python scripts/run_det3.sh gate    # G1, re-run HDDM-A, G2-G3
#   PYTHON_BIN=/path/to/python scripts/run_det3.sh judge   # E10bFT once, then the verdict data
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
py=${PYTHON_BIN:-python}
out=outputs/benchmark/det3
commit=$(git rev-parse HEAD)
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }

run_arm() {
  local preset=$1 ds
  for ds in synthetic_multiclass insects_abrupt_balanced insects_incremental_balanced insects_incremental_gradual_balanced \
            insects_incremental_abrupt_reoccurring_balanced insects_incremental_reoccurring_balanced; do
    echo "START $(date '+%Y-%m-%dT%H:%M:%S') $preset $ds"
    "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset "$preset" --workers "${WORKERS:-6}" --out-dir "$out" --resume --record-warning-events
  done
  echo "START $(date '+%Y-%m-%dT%H:%M:%S') $preset injected_paper_electricity"
  "$py" -u scripts/run_benchmark.py --dataset injected_paper_electricity --trials 20 --preset "$preset" --workers "${WORKERS:-6}" --out-dir "$out" --resume --record-warning-events
}

case "${1:-}" in
  gate)
    "$py" -u scripts/run_benchmark.py --dataset electricity --preset e10bft --out-dir "$out" --resume
    "$py" - <<'PY'
import json, sys
a = json.load(open("outputs/benchmark/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
b = json.load(open("outputs/benchmark/det3/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
diff = [k for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G1: {len(a)} committed fields, {len(diff)} differ {diff}")
sys.exit(1 if diff or len(a) != 37 else 0)
PY
    run_arm det1_zone_hddm_a_lw0
    "$py" scripts/analyze_det3.py --commit "$commit" --gate ;;
  judge)
    run_arm e10bft
    "$py" scripts/analyze_det3.py --commit "$commit" ;;
  *) echo "usage: $0 gate|judge"; exit 2 ;;
esac
