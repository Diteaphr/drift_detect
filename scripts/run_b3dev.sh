#!/usr/bin/env bash
# B3-dev, a development check (not preregistered): HDDM-A reading the frozen reference in place of
# dual ADWIN, on DET3's 205 streams (already judged, so dev evidence only). Launch from repo root on a clean tree:
#   PYTHON_BIN=/path/to/python scripts/run_b3dev.sh gate   # e10bft + HDDM-A on 17 streams, to compare with stored DET3 runs
#   PYTHON_BIN=/path/to/python scripts/run_b3dev.sh main   # the four b3dev_ref_* presets
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
py=${PYTHON_BIN:-python}
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }

run() {
  echo "START $(date '+%Y-%m-%dT%H:%M:%S') $*"
  "$py" -u scripts/run_benchmark.py "$@" --workers "${WORKERS:-6}" --resume --record-warning-events
}

case "${1:-}" in
  gate)
    out=outputs/benchmark/b3dev_gate
    run --dataset injected_paper_electricity --trials 2 --preset e10bft det1_zone_hddm_a_lw0 --out-dir "$out"
    run --dataset insects_abrupt_balanced --preset e10bft det1_zone_hddm_a_lw0 --out-dir "$out" ;;
  main)
    out=outputs/benchmark/b3dev
    arms=(b3dev_ref_hddm_a_noguard b3dev_ref_hddm_a_guard b3dev_ref_hddm_a3e4_noguard b3dev_ref_hddm_a3e4_guard)
    run --dataset injected_paper_electricity --trials 20 --preset "${arms[@]}" --out-dir "$out"
    for ds in synthetic_multiclass insects_abrupt_balanced insects_incremental_balanced insects_incremental_gradual_balanced \
              insects_incremental_abrupt_reoccurring_balanced insects_incremental_reoccurring_balanced; do
      run --dataset "$ds" --preset "${arms[@]}" --out-dir "$out"
    done ;;
  *) echo "usage: $0 gate|main"; exit 2 ;;
esac
echo "DONE $(date '+%Y-%m-%dT%H:%M:%S') $1"
