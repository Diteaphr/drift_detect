#!/usr/bin/env bash
# DET3 preregistered formal matrix. Launch under tmux + caffeinate from repo root.
set -euo pipefail
cd "$(dirname "$0")/.."

python_bin=${DET3_PYTHON:-/private/tmp/det1-main-venv/bin/python}
out_dir=outputs/benchmark/det3
log_dir=outputs/det3/logs
mkdir -p "$log_dir" "$out_dir"
log_file="$log_dir/formal_20261013.log"
exec >>"$log_file" 2>&1

presets=(det3_full_dual_adwin_lw0 det3_full_dual_adwin_lw1 det3_full_hddm_a_lw1)
common=(--preset "${presets[@]}" --workers 6 --out-dir "$out_dir" --resume --record-warning-events)

count_manifests() {
  find "$out_dir/$1" -name manifest.json -type f | wc -l | tr -d ' '
}

run_dataset() {
  local dataset=$1 expected=$2
  shift 2
  mkdir -p "$out_dir/$dataset"
  echo "START $(date -u '+%Y-%m-%dT%H:%M:%SZ') $dataset expected=$expected"
  if ! "$python_bin" -u scripts/run_benchmark.py --dataset "$dataset" "${common[@]}" "$@"; then
    echo "RUNNER_ERROR $dataset; retrying incomplete jobs once"
  fi
  local completed
  completed=$(count_manifests "$dataset")
  if [[ "$completed" -ne "$expected" ]]; then
    echo "RETRY $dataset completed=$completed expected=$expected"
    if ! "$python_bin" -u scripts/run_benchmark.py --dataset "$dataset" "${common[@]}" "$@"; then
      echo "RETRY_RUNNER_ERROR $dataset"
    fi
  fi
  completed=$(count_manifests "$dataset")
  echo "DONE $(date -u '+%Y-%m-%dT%H:%M:%SZ') $dataset completed=$completed failed=$((expected-completed))"
}

echo "DET3 formal start $(date -u '+%Y-%m-%dT%H:%M:%SZ') git=$(git rev-parse HEAD)"
batch_start=$(date +%s)
run_dataset synthetic_multiclass 120
run_dataset insects_abrupt_balanced 3
run_dataset insects_incremental_balanced 3
run_dataset insects_incremental_gradual_balanced 3
run_dataset insects_incremental_abrupt_reoccurring_balanced 3
run_dataset insects_incremental_reoccurring_balanced 3
batch_done=$(count_manifests synthetic_multiclass)
for dataset in insects_abrupt_balanced insects_incremental_balanced insects_incremental_gradual_balanced insects_incremental_abrupt_reoccurring_balanced insects_incremental_reoccurring_balanced; do
  batch_done=$((batch_done+$(count_manifests "$dataset")))
done
echo "BATCH1 COMPLETE $(date -u '+%Y-%m-%dT%H:%M:%SZ') completed=$batch_done failed=$((135-batch_done)) elapsed_s=$(($(date +%s)-batch_start))"

batch_start=$(date +%s)
run_dataset injected_paper_electricity 480 --trials 20
batch_done=$(count_manifests injected_paper_electricity)
echo "BATCH2 COMPLETE $(date -u '+%Y-%m-%dT%H:%M:%SZ') completed=$batch_done failed=$((480-batch_done)) elapsed_s=$(($(date +%s)-batch_start))"
echo "DET3 formal complete $(date -u '+%Y-%m-%dT%H:%M:%SZ') total=$((135+batch_done))"
