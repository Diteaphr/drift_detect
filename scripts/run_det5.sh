#!/usr/bin/env bash
# DET5 preregistered run (docs/ECPF_DET5_預註冊.md), on node2. Launch from repo root on a clean tree:
#   PYTHON_BIN=/path/to/python scripts/run_det5.sh     # gates, both datasets x both arms + det_adwin, verdict data
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
py=${PYTHON_BIN:-python}
out=outputs/benchmark/det5
commit=$(git rev-parse HEAD)
arms=(det1_zone_hddm_a_lw0 e10bft)
datasets=(injected_paper_covertype injected_paper_gas_sensor_drift)
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }

run() {  # run <workers> <dataset> [extra run_benchmark arguments]
  echo "START $(date '+%Y-%m-%dT%H:%M:%S') $2"
  "$py" -u scripts/run_benchmark.py --dataset "$2" --preset "${arms[@]}" --workers "$1" --out-dir "$out" --resume --record-warning-events "${@:3}"
  echo "END $(date '+%Y-%m-%dT%H:%M:%S') $2"
}

# G2: both presets are byte-identical to DET3's registration
git diff --quiet d161895 HEAD -- configs/presets/e10bft.json configs/presets/det1_zone_hddm_a_lw0.json \
  || { echo "G2: presets changed since d161895"; exit 1; }
echo "G2: presets unchanged since d161895"

# G1: the single-tree main method still reproduces main's committed electricity result
"$py" -u scripts/run_benchmark.py --dataset electricity --preset e10bft --out-dir "$out" --resume
"$py" - <<'PY'
import json, sys
a = json.load(open("outputs/benchmark/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
b = json.load(open("outputs/benchmark/det5/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
diff = [k for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G1: {len(a)} committed fields, {len(diff)} differ {diff}")
sys.exit(1 if diff or len(a) != 37 else 0)
PY

# G3: both arms give the same result twice on abrupt/class_prior g49 of each dataset (the pilot trial, never judged)
for rep in a b; do
  for ds in "${datasets[@]}"; do
    "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset "${arms[@]}" --trials 50 --cells class_prior_abrupt_g49 \
      --out-dir "outputs/det5/wiring/g3_$rep" --record-warning-events
  done
done
"$py" - <<'PY'
import glob, json, sys
bad, n = [], 0
for p in sorted(glob.glob("outputs/det5/wiring/g3_a/*/*/*/metrics.json")):
    a, b = (json.load(open(x, encoding="utf-8")) for x in (p, p.replace("g3_a", "g3_b", 1)))
    n += 1
    bad += [(p, k) for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G3: {n} runs repeated, differences: {bad}")
sys.exit(1 if bad or n != 4 else 0)
PY

for ds in "${datasets[@]}"; do
  run "${WORKERS:-12}" "$ds" --trials 40
  echo "START $(date '+%Y-%m-%dT%H:%M:%S') $ds det_adwin"
  "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset det_adwin --workers "${WORKERS:-12}" --out-dir "$out" --resume --trials 40
  echo "END $(date '+%Y-%m-%dT%H:%M:%S') $ds det_adwin"
done
"$py" scripts/analyze_det5.py --commit "$commit"
