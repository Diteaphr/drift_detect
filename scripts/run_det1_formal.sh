#!/usr/bin/env bash
# DET1 preregistered lw0 matrix. Launch from repo root under tmux + caffeinate.
set -euo pipefail
cd "$(dirname "$0")/.."

python_bin=/private/tmp/det1-main-venv/bin/python
out_dir=outputs/benchmark/det1
log_dir=outputs/det1/logs
mkdir -p "$log_dir" "$out_dir"
log_file="$log_dir/formal_20261013.log"
exec >>"$log_file" 2>&1

presets=(det1_dual_adwin_lw0 det1_zone_ddm_lw0 det1_zone_hddm_a_lw0 det1_zone_rddm_lw0 det1_zone_magseed_lw0)
common=(--preset "${presets[@]}" --workers 6 --out-dir "$out_dir" --resume --record-warning-events)

count_manifests() {
  find "$out_dir/$1" -name manifest.json -type f | wc -l | tr -d ' '
}

run_dataset() {
  local dataset=$1 expected=$2
  shift 2
  echo "START $(date -u '+%Y-%m-%dT%H:%M:%SZ') $dataset expected=$expected"
  "$python_bin" -u scripts/run_benchmark.py --dataset "$dataset" "${common[@]}" "$@"
  local completed
  completed=$(count_manifests "$dataset")
  if [[ "$completed" -ne "$expected" ]]; then
    echo "FAILED $dataset: expected $expected manifests, found $completed"
    exit 1
  fi
  echo "DONE $(date -u '+%Y-%m-%dT%H:%M:%SZ') $dataset completed=$completed failed=0"
}

echo "DET1 formal start $(date -u '+%Y-%m-%dT%H:%M:%SZ') git=$(git rev-parse HEAD)"
batch_start=$(date +%s)
run_dataset synthetic_multiclass 200
run_dataset insects_abrupt_balanced 5
run_dataset insects_incremental_balanced 5
run_dataset insects_incremental_gradual_balanced 5
run_dataset insects_incremental_abrupt_reoccurring_balanced 5
run_dataset insects_incremental_reoccurring_balanced 5
echo "BATCH1 COMPLETE $(date -u '+%Y-%m-%dT%H:%M:%SZ') completed=225 failed=0 elapsed_s=$(($(date +%s)-batch_start))"

batch_start=$(date +%s)
run_dataset injected_paper_electricity 800 --trials 20
echo "BATCH2 COMPLETE $(date -u '+%Y-%m-%dT%H:%M:%SZ') completed=800 failed=0 elapsed_s=$(($(date +%s)-batch_start))"
echo "DET1 formal complete $(date -u '+%Y-%m-%dT%H:%M:%SZ') total=1025"
