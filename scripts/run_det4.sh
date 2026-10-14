#!/usr/bin/env bash
# DET4 preregistered run (docs/ECPF_DET4_預註冊.md). Launch from repo root on a clean tree:
#   PYTHON_BIN=/path/to/python scripts/run_det4.sh main        # gates, injected g20-g39, main verdict
#   PYTHON_BIN=/path/to/python scripts/run_det4.sh secondary   # synthetic + INSECTS, full verdict data
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
py=${PYTHON_BIN:-python}
out=outputs/benchmark/det4
commit=$(git rev-parse HEAD)
arms=(det4_zone_hddm_a_lw0_hf10 det4_e10bft_hf10)
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }

run() {  # run <workers> <dataset> [extra run_benchmark arguments]
  echo "START $(date '+%Y-%m-%dT%H:%M:%S') $2"
  "$py" -u scripts/run_benchmark.py --dataset "$2" --preset "${arms[@]}" --workers "$1" --out-dir "$out" --resume --record-warning-events "${@:3}"
  echo "END $(date '+%Y-%m-%dT%H:%M:%S') $2"
}

case "${1:-}" in
  main)
    # G1: the single-tree main method still reproduces main's committed electricity result
    "$py" -u scripts/run_benchmark.py --dataset electricity --preset e10bft --out-dir "$out" --resume
    "$py" - <<'PY'
import json, sys
a = json.load(open("outputs/benchmark/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
b = json.load(open("outputs/benchmark/det4/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
diff = [k for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G1: {len(a)} committed fields, {len(diff)} differ {diff}")
sys.exit(1 if diff or len(a) != 37 else 0)
PY
    # G3: both forest presets give the same result twice (first 8000 rows of raw electricity, not a judged stream)
    for rep in a b; do
      "$py" -u scripts/run_benchmark.py --dataset electricity --preset "${arms[@]}" --max-steps 8000 --out-dir "outputs/det4/wiring/g3_$rep" --record-warning-events
    done
    "$py" - <<'PY'
import json, sys
bad = []
for p in ("det4_zone_hddm_a_lw0_hf10", "det4_e10bft_hf10"):
    a, b = (json.load(open(f"outputs/det4/wiring/g3_{r}/electricity/{p}/electricity/metrics.json", encoding="utf-8")) for r in "ab")
    bad += [(p, k) for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G3: forest repeat differences: {bad}")
sys.exit(1 if bad else 0)
PY
    run "${WORKERS:-10}" injected_paper_electricity --trials 40 --cells _g2 _g3
    "$py" scripts/analyze_det4.py --commit "$commit" --main-only ;;
  secondary)
    for ds in insects_abrupt_balanced insects_incremental_balanced insects_incremental_gradual_balanced \
              insects_incremental_abrupt_reoccurring_balanced insects_incremental_reoccurring_balanced; do
      run 1 "$ds" &
    done
    run "${WORKERS:-6}" synthetic_multiclass
    wait
    "$py" scripts/analyze_det4.py --commit "$commit" ;;
  *) echo "usage: $0 main|secondary"; exit 2 ;;
esac
