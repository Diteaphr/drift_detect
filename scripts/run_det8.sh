#!/usr/bin/env bash
# DET8 preregistered run (docs/ECPF_DET8_預註冊.md), on node1 in a snapshot of the registered commit
# (SNAPSHOT_OF names it, SNAPSHOT_SHA256SUMS lists its files). Launch from the snapshot root on a clean tree:
#   PYTHON_BIN=/path/to/python STATUS=/d/det8/STATUS scripts/run_det8.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
py=${PYTHON_BIN:-python}
out=outputs/benchmark/det8
st=${STATUS:-/dev/null}
status() { echo "9 $* $(date '+%F %T')" > "$st"; }
trap 'status failed' ERR
commit=$(git rev-parse HEAD)
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }

run() {  # run <dataset> <trials> <presets...> -- <cell substrings...>
  local ds=$1 trials=$2; shift 2
  local presets=() cells=()
  while [[ $1 != -- ]]; do presets+=("$1"); shift; done; shift
  cells=("$@")
  # every judged run must record a clean tree (G5), so stop before running on a dirty one
  [[ -z "$(git status --porcelain)" ]] || { echo "tree became dirty:"; git status --porcelain | head; exit 1; }
  status running "$ds"
  echo "START $(date '+%Y-%m-%dT%H:%M:%S') $ds ${presets[*]}"
  "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset "${presets[@]}" --trials "$trials" --cells "${cells[@]}" \
    --workers "${WORKERS:-6}" --out-dir "$out" --resume --record-warning-events
  echo "END $(date '+%Y-%m-%dT%H:%M:%S') $ds"
}

# G0: the snapshot holds the registered commit's files byte for byte
status running gates
sha256sum --quiet -c SNAPSHOT_SHA256SUMS
echo "G0: snapshot of $(cat SNAPSHOT_OF) verified, $(wc -l < SNAPSHOT_SHA256SUMS) files; snapshot commit $commit"

# G2: H3 is HDDM-A's preset plus the one confidence field
"$py" - <<'PY'
import json, sys
load = lambda n: json.load(open(f"configs/presets/{n}.json", encoding="utf-8"))
h, h3 = load("det1_zone_hddm_a_lw0"), load("det8_h3")
ok = h3["config"] == dict(h["config"], ecpf_zone_drift_confidence=0.0003) and h3["warm_start"] == h["warm_start"]
print(f"G2: det8_h3 = det1_zone_hddm_a_lw0 + ecpf_zone_drift_confidence 3e-4: {ok}")
sys.exit(0 if ok else 1)
PY

# G1: the single-tree main method still reproduces main's committed electricity result on this machine
"$py" -u scripts/run_benchmark.py --dataset electricity --preset e10bft --out-dir "$out" --resume
"$py" - <<'PY'
import json, sys
a = json.load(open("outputs/benchmark/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
b = json.load(open("outputs/benchmark/det8/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
diff = [k for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G1: {len(a)} committed fields, {len(diff)} differ {diff}")
sys.exit(1 if diff or len(a) != 37 else 0)
PY

# G3: G3 and H3 give the same result twice on abrupt/class_prior g199 (the pilot trial, never judged)
for rep in a b; do
  for ds in injected_paper_electricity injected_paper_gas_sensor_drift; do
    "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset det7_g3 det8_h3 --trials 200 \
      --cells class_prior_abrupt_g199 --workers 4 --out-dir "outputs/det8/wiring/g3_$rep" --record-warning-events
  done
done
"$py" - <<'PY'
import glob, json, sys
bad, n = [], 0
for p in sorted(glob.glob("outputs/det8/wiring/g3_a/*/*/*/metrics.json")):
    a, b = (json.load(open(x, encoding="utf-8")) for x in (p, p.replace("g3_a", "g3_b", 1)))
    n += 1
    bad += [(p, k) for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G3: {n} runs repeated, differences: {bad}")
sys.exit(1 if bad or n != 4 else 0)
PY

# Judged runs: electricity g200-g279, then gas and covertype g200-g239, all three arms. The main verdict is
# scored as soon as electricity is done; the full verdict at the end.
run injected_paper_electricity 280 det7_g3 det8_h3 det1_zone_hddm_a_lw0 -- $(seq -f "_g%g" 200 279)
"$py" scripts/analyze_det8.py --commit "$commit" --datasets electricity
run injected_paper_gas_sensor_drift 240 det7_g3 det8_h3 det1_zone_hddm_a_lw0 -- $(seq -f "_g%g" 200 239)
run injected_paper_covertype 240 det7_g3 det8_h3 det1_zone_hddm_a_lw0 -- $(seq -f "_g%g" 200 239)
status running scoring
"$py" scripts/analyze_det8.py --commit "$commit"
status done
echo "DONE $(date '+%Y-%m-%dT%H:%M:%S')"
