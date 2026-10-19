#!/usr/bin/env bash
# DET7 preregistered run (docs/ECPF_DET7_預註冊.md), on lucas-jang. Launch from repo root on a clean tree:
#   PYTHON_BIN=/path/to/python scripts/run_det7.sh     # gates, all arms on the fresh trials, verdict data
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
py=${PYTHON_BIN:-python}
out=outputs/benchmark/det7
commit=$(git rev-parse HEAD)
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }

run() {  # run <dataset> <trials> <presets...> -- <cell substrings...>
  local ds=$1 trials=$2; shift 2
  local presets=() cells=()
  while [[ $1 != -- ]]; do presets+=("$1"); shift; done; shift
  cells=("$@")
  echo "START $(date '+%Y-%m-%dT%H:%M:%S') $ds ${presets[*]}"
  "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset "${presets[@]}" --trials "$trials" --cells "${cells[@]}" \
    --workers "${WORKERS:-10}" --out-dir "$out" --resume --record-warning-events
  echo "END $(date '+%Y-%m-%dT%H:%M:%S') $ds"
}

# G2: E10bFT and HDDM-A are DET3's presets (d161895); G3 and G are the B3-dev presets (6965dca) under new names
git diff --quiet d161895 HEAD -- configs/presets/e10bft.json configs/presets/det1_zone_hddm_a_lw0.json \
  || { echo "G2: E10bFT / HDDM-A presets changed since d161895"; exit 1; }
git diff --quiet 6965dca HEAD -- configs/presets/b3dev_ref_hddm_a3e4_guard.json configs/presets/b3dev_ref_hddm_a_guard.json \
  || { echo "G2: B3-dev presets changed since 6965dca"; exit 1; }
"$py" - <<'PY'
import json, sys
load = lambda n: json.load(open(f"configs/presets/{n}.json", encoding="utf-8"))
pairs = [("det7_g3", "b3dev_ref_hddm_a3e4_guard"), ("det7_g", "b3dev_ref_hddm_a_guard")]
bad = [p for p in pairs if load(p[0])["config"] != load(p[1])["config"] or load(p[0])["warm_start"] != load(p[1])["warm_start"]]
print(f"G2: presets unchanged; DET7 configs equal B3-dev's: {not bad}")
sys.exit(1 if bad else 0)
PY

# G1: the single-tree main method still reproduces main's committed electricity result
"$py" -u scripts/run_benchmark.py --dataset electricity --preset e10bft --out-dir "$out" --resume
"$py" - <<'PY'
import json, sys
a = json.load(open("outputs/benchmark/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
b = json.load(open("outputs/benchmark/det7/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
diff = [k for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G1: {len(a)} committed fields, {len(diff)} differ {diff}")
sys.exit(1 if diff or len(a) != 37 else 0)
PY

# G3: G3 and HDDM-A give the same result twice on abrupt/class_prior g199 (the pilot trial, never judged)
for rep in a b; do
  for ds in injected_paper_electricity injected_paper_gas_sensor_drift; do
    "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset det7_g3 det1_zone_hddm_a_lw0 --trials 200 \
      --cells class_prior_abrupt_g199 --workers 4 --out-dir "outputs/det7/wiring/g3_$rep" --record-warning-events
  done
done
"$py" - <<'PY'
import glob, json, sys
bad, n = [], 0
for p in sorted(glob.glob("outputs/det7/wiring/g3_a/*/*/*/metrics.json")):
    a, b = (json.load(open(x, encoding="utf-8")) for x in (p, p.replace("g3_a", "g3_b", 1)))
    n += 1
    bad += [(p, k) for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G3: {n} runs repeated, differences: {bad}")
sys.exit(1 if bad or n != 4 else 0)
PY

# Judged runs: electricity g40-g119 (four arms), then gas and covertype g50-g89 (G3 and HDDM-A)
run injected_paper_electricity 120 det7_g3 det1_zone_hddm_a_lw0 det7_g e10bft -- _g4 _g5 _g6 _g7 _g8 _g9 $(seq -f "_g%g" 100 119)
run injected_paper_gas_sensor_drift 90 det7_g3 det1_zone_hddm_a_lw0 -- _g5 _g6 _g7 _g8
run injected_paper_covertype 90 det7_g3 det1_zone_hddm_a_lw0 -- _g5 _g6 _g7 _g8
"$py" scripts/analyze_det7.py --commit "$commit"
echo "DONE $(date '+%Y-%m-%dT%H:%M:%S')"
