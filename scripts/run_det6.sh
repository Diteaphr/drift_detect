#!/usr/bin/env bash
# DET6 preregistered run (docs/ECPF_DET6_預註冊.md), on node2. Launch from repo root on a clean tree:
#   PYTHON_BIN=/path/to/python scripts/run_det6.sh     # streams, gates, both learners x both arms, verdict data
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
py=${PYTHON_BIN:-python}
out=outputs/benchmark/det6
ds=synthetic_slow_gradual
commit=$(git rev-parse HEAD)
arms=(det1_zone_hddm_a_lw0 e10bft det4_zone_hddm_a_lw0_hf10 det4_e10bft_hf10)
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }

# G0: the generator reproduces the registered streams (g00-g39 and the gate trial g49 of each width)
pids=()
for w in 4000 8000 16000; do "$py" -W ignore scripts/generate_det6_streams.py --widths "$w" & pids+=($!); done
for p in "${pids[@]}"; do wait "$p"; done
got=$("$py" -W ignore scripts/generate_det6_streams.py --digest)
want=$("$py" -W ignore -c "import scripts.analyze_det6 as d; print(d.DATA_SHA256)")
[[ "$got" == "$want" ]] || { echo "G0: judged streams digest $got, registered $want"; exit 1; }
echo "G0: judged streams match the registered digest"

# G2: the single-tree presets are DET3's (d161895), the forest presets DET4's (fc1298d)
git diff --quiet d161895 HEAD -- configs/presets/e10bft.json configs/presets/det1_zone_hddm_a_lw0.json \
  || { echo "G2: single-tree presets changed since d161895"; exit 1; }
git diff --quiet fc1298d HEAD -- configs/presets/det4_e10bft_hf10.json configs/presets/det4_zone_hddm_a_lw0_hf10.json \
  || { echo "G2: forest presets changed since fc1298d"; exit 1; }
echo "G2: presets unchanged"

# G1: the single-tree main method still reproduces main's committed electricity result
"$py" -u scripts/run_benchmark.py --dataset electricity --preset e10bft --out-dir "$out" --resume
"$py" - <<'PY'
import json, sys
a = json.load(open("outputs/benchmark/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
b = json.load(open("outputs/benchmark/det6/electricity/e10bft/electricity/metrics.json", encoding="utf-8"))
diff = [k for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G1: {len(a)} committed fields, {len(diff)} differ {diff}")
sys.exit(1 if diff or len(a) != 37 else 0)
PY

# G3: all four presets give the same result twice on w16000 g49 (the gate trial, never judged)
for rep in a b; do
  "$py" -u scripts/run_benchmark.py --dataset "$ds" --preset "${arms[@]}" --cells _w16000_g49 --workers 4 \
    --out-dir "outputs/det6/wiring/g3_$rep" --record-warning-events
done
"$py" - <<'PY'
import glob, json, sys
bad, n = [], 0
for p in sorted(glob.glob("outputs/det6/wiring/g3_a/*/*/*/metrics.json")):
    a, b = (json.load(open(x, encoding="utf-8")) for x in (p, p.replace("g3_a", "g3_b", 1)))
    n += 1
    bad += [(p, k) for k in a if a[k] != b.get(k) and not (a[k] != a[k] and b.get(k) != b.get(k))]
print(f"G3: {n} runs repeated, differences: {bad}")
sys.exit(1 if bad or n != 4 else 0)
PY

echo "START $(date '+%Y-%m-%dT%H:%M:%S') $ds"
"$py" -u scripts/run_benchmark.py --dataset "$ds" --preset "${arms[@]}" --cells _g0 _g1 _g2 _g3 --workers "${WORKERS:-12}" \
  --out-dir "$out" --resume --record-warning-events
echo "END $(date '+%Y-%m-%dT%H:%M:%S') $ds"
"$py" scripts/analyze_det6.py --commit "$commit"
