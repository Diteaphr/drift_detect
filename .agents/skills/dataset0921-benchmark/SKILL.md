---
name: dataset0921-benchmark
description: Runs experiments on data/dataset_0921 through the benchmark harness and compares results with the literature SOTA. Use when the user asks to run an experiment, benchmark or SOTA comparison on a dataset_0921 dataset (electricity, airlines, covertype, INSECTS, injected, synthetic), to compare the main method or another preset against SOTA or baselines, to re-evaluate stored runs, or to add a new system configuration for benchmarking.
---

# dataset_0921 Benchmark

The harness fixes the protocol and the metric definitions; this skill only drives it. It is tool-neutral: any coding agent that can read files and run shell commands can follow it (Cursor, Claude Code, Codex, Copilot, Gemini CLI, ...). Commands run from the repo root; use `python` instead of `python3` where that is the interpreter's name (usually Windows).

This file and `protocols.md` are the only copy. `.claude/skills/dataset0921-benchmark/SKILL.md`, `AGENTS.md`, `GEMINI.md` and `.github/copilot-instructions.md` only point here; when you change this skill's `name` or `description`, update the copy in `.claude/skills/` too (`tests/test_agent_skill.py` checks it).

| File | Role |
|---|---|
| `configs/datasets_0921.json` | Protocol per dataset (task, ground truth, delta_max, comparable, role) and literature SOTA values |
| `configs/presets/<name>.json` | Frozen system settings; `role` says what each one is: `main`, `ablation`, `baseline`, `detector_reference` |
| `configs/benchmark_defaults.json` | `main_preset` (the system under test when nobody names one) and preset suites (`standard`, `quick`, `ablation`, `main_only`) |
| `scripts/run_benchmark.py` | Runs presets on a dataset, stores raw records, evaluates with `src/metrics/evaluate_run.py` |
| `scripts/compare_sota.py` | Aggregates `runs.csv` files into the comparison report |

## The main method

**"Our system" is `e10bft` unless the user explicitly names another preset**: E10bFT detection (frozen reference model, leader guard, warning timeout, dual ADWIN on ECPF) on a **single Hoeffding Tree** (`htr` on regression streams). `run_benchmark.py` runs it when no `--preset`/`--suite` is given, and every suite starts with it. `ecpf_paper` and `ecpf_reuse_value` are ablations, not the main method.

## Step 0: check which datasets exist on this machine

Teammates may not have every dataset (`real_dataset/_full/` is not in git, so a fresh clone has no `airlines_full`, `covertype_full` or `injected_paper_covertype` source). Before asking anything, run:

```bash
python3 scripts/run_benchmark.py --list-datasets --json
```

Each entry has `name`, `task`, `role` (report/dev), `comparable`, `comparable_kinds`, `available`, `n_streams`, `rows_per_stream`, `note`, `results` (presets that already have `outputs/benchmark/<name>/<preset>/runs.csv`) and, when the data is missing, `missing_hint` (the command that creates it). Build the `datasets` question below from this output, never from a fixed list or from memory: the registry can grow and every machine has different data. On a fresh clone the usual gaps are `airlines_full`, `covertype_full` and `injected_paper_covertype` (all three come from `prepare_all.py --full`).

## Step 1: ask what the user wants (multiple choice)

Collect the experiment plan as multiple-choice questions, prompts and labels in the user's language, and **do not run any experiment before the user has answered**. Skip a question when the user's message already answers it; if the user says "use the defaults" / "你決定", take every option marked (建議) without asking.

How to ask depends on the tool you run in:
- **A structured question tool** (Cursor `AskQuestion`, Claude Code `AskUserQuestion`, or your environment's equivalent): put all questions in one call. If the tool caps questions or options per call (Claude Code: at most 4 questions, 2-4 options each), ask in rounds — round 1: `goal`, `system`, `baselines`, `scope`; round 2: `seeds`, `report`, `timing` — and ask `datasets` as the plain-text list below, since it has more options than such tools allow.
- **No such tool**: send all questions in one message as a numbered list with lettered options, mark the recommended ones (建議), allow several letters where the question is multiple choice, and tell the user they can reply like `1a 2 a,c,f 3a 4a 5a 6a 7a 8a` or just `你決定`. Then stop and wait for the reply.

Use these questions (ids and labels can be shortened, keep the meaning):

1. `goal` — 這次要做什麼實驗？ (single)
   - `sota`: 和文獻 SOTA 比較（主方法 + 對照組，最後出報告）(建議)
   - `quick`: 先快速看一下結果（便宜的對照組，不當正式結果）
   - `ablation`: 主方法的消融比較（e10bft vs ecpf_paper vs ecpf_reuse_value）
   - `report_only`: 不跑新實驗，用現有結果出報告 / 重新計分
   - `new_preset`: 測試一組新的系統設定（會另存新 preset）
2. `datasets` — 用哪些資料集？ (multiple; options generated from Step 0)
   - **List every registry entry, including the ones missing on this machine**, so the user sees the whole menu and what this machine lacks. Prompt: `用哪些資料集？（可複選）這台電腦有 <A>/<T> 個；缺少：<missing names or 無>`.
   - Shortcut options first:
     - `all_comparable`: 全部可比、且這台電腦有的資料集（<N> 個：<names>）(建議) — `available`, `comparable` true, no `comparable_kinds`.
     - `all_insects`: 全部 INSECTS（<N> 個）— only if at least two `insects_*` entries are available.
     - `prepare_missing`: 先準備缺少的資料再一起跑（<missing names>）— only if something is missing.
   - Then **one option per registry entry**, id = registry name, in this order: comparable report datasets, comparable with `comparable_kinds` (injected_paper_*), reference-only report datasets, dev datasets. Label: `<name> — <task>，<size>，<status>[，<availability>][，<results>]`:
     - `<size>`: `<rows_per_stream> 筆` for one stream, `<n_streams> 串 x <rows_per_stream> 筆` when both are known, `<n_streams> 串` when `rows_per_stream` is null; for missing entries use the row count from `note` or omit.
     - `<status>`: `可比`, plus `，跑很久` when rows x streams > 300,000; `偵測指標，只有 detector preset 可比，主方法僅供參考` (`comparable_kinds: ["detector"]`); `僅供參考：<short reason from note>` (role report, not comparable, e.g. truncated airlines/covertype: point to the `_full` entry); `開發用，只能調參` (role dev).
     - `<availability>`: only for missing entries: `這台沒有，選了會先準備資料（需網路，數分鐘）`; when `missing_hint` starts with `missing:` write `這台沒有，請先 git pull`.
     - `<results>`: when `results` is not empty: `已有結果：<presets>`.
   - Last option `other`: 其他（請說明）.
   - For `goal = report_only`, list only entries with a non-empty `results`, labelled with those presets; if none have results, say so and ask whether to run an experiment instead.

   Example label set on a fresh clone (shortened):
   `all_comparable`: 全部可比、且這台電腦有的資料集（6 個：electricity、insects_abrupt_balanced、…）(建議) / `prepare_missing`: 先準備缺少的資料再一起跑（airlines_full、covertype_full、injected_paper_covertype）/ `electricity` — binary，45,312 筆，可比 / `airlines_full` — binary，539,383 筆，可比，跑很久，這台沒有，選了會先準備資料（需網路，數分鐘）/ `injected_paper_electricity` — binary，400 串 x 45,312 筆，偵測指標，只有 detector preset 可比，主方法僅供參考 / `airlines` — binary，100,000 筆，僅供參考：只有前 10 萬筆，正式比較用 airlines_full / `synthetic_binary` — binary，40 串，開發用，只能調參 / `other`: 其他（請說明）
3. `system` — 受測系統？ (single)
   - `main`: 主方法 e10bft（單棵 Hoeffding Tree）(建議)
   - `other`: 其他已存在的 preset（請說明名稱）
4. `baselines` — 對照組？ (single)
   - `standard`: 標準組 arf100、srp10、ht、nb（迴歸用 htr）(建議)
   - `quick`: 快速組 arf10、ht、nb（不是文獻設定）
   - `ablation`: 只和 ecpf_paper、ecpf_reuse_value 比
   - `none`: 不跑對照組（只看主方法）
   - `custom`: 自己指定（請列出 preset）
5. `seeds` — 有隨機性的對照組（森林）跑幾個種子？ (single; skip if no forest preset is selected)
   - `3`: 3 個 (建議)
   - `5`: 5 個（論文常用，時間約多 70%）
   - `1`: 1 個（沒有標準差，只看趨勢）
6. `scope` — 執行方式？ (single)
   - `smoke_then_full`: 先冒煙測試，通過再跑完整 (建議)
   - `full`: 直接跑完整
   - `smoke_only`: 只做冒煙測試
7. `report` — 跑完要不要出 SOTA 比較報告（compare_sota）？ (single)
   - `yes`: 要，以受測系統為 target (建議)
   - `no`: 不用，只要 runs.csv
8. `timing` — 時間成本要量多嚴格？ (single; skip for `report_only`, or when only one run per preset is planned: one dataset stream and no forest preset or one seed. Then every run is alone anyway)
   - `parallel`: 平常模式：同一個 preset 的多個種子 / 串流同時跑（較快；記憶體照樣準，時間只能當參考）(建議)
   - `strict`: 嚴格量時間：一次只跑一個 run（`--workers 1`，時間可以正式比較；森林部分總時間約變成「種子數」倍）

Map the answers: `system` → `--preset <name>` (main = no flag needed); `timing` → `parallel`: `--workers <seeds>` on single-stream datasets (3 with the default seeds), `--workers 8` on multi-stream datasets (`injected_paper_*`, INSECTS sets with several streams, synthetic), never more than the machine's performance cores minus one; `strict`: `--workers 1` (multiply the forest part of the runtime estimate by the number of seeds); `baselines` → `--suite standard|quick|ablation` or an explicit `--preset` list (when the system is not `e10bft`, pass `--preset <system> <baselines...>` instead of a suite, since suites start with `e10bft`); dataset ids are registry names, one `--dataset` command each; `all_comparable` / `all_insects` expand to their lists (print them in the plan); `prepare_missing`, or picking a missing dataset directly → run each distinct `missing_hint` command first (it downloads from OpenML/UCI, so it needs network and may take minutes), re-run Step 0 to confirm the data is now `available`, then include those datasets in the run (with `prepare_missing` alone, add every newly available comparable one). If preparing fails, tell the user and continue with the datasets that exist. A `missing_hint` of the form `missing: <path>` means the file is normally in git: tell the user to pull instead of generating it.

## Step 2: show the plan, then run

Print the commands and a rough runtime before starting. Measured on this machine, one run on electricity (45k rows): `ht`/`nb` ~5 s, `e10bft`/`ecpf_*` ~30 s, `arf10` ~1 min, `arf100` ~7 min per seed. Scale roughly with rows x features: `covertype_full` / `airlines_full` are 12-13x longer streams, so `arf100` there takes hours per seed; an `injected_paper_*` dataset is 400 streams. If the plan is longer than about 30 minutes, ask once more (開始 / 改成快速組 / 減少資料集, same asking rules as Step 1) before launching. Launch long runs in the background with a log file (e.g. `nohup python3 scripts/run_benchmark.py ... > /tmp/<name>.log 2>&1 &`, or your tool's background-command feature) and check the log periodically instead of blocking the session.

```
- [ ] 1. Uncommitted changes? Ask whether to commit first (the manifest records the commit)
- [ ] 2. Smoke test: add --max-steps 5000 (marked non-comparable, never reported)
- [ ] 3. Full run, one command per dataset
- [ ] 4. Check the log: no error rows, versions OK, comparable column as expected, no psutil warning, a "cost" block per preset
- [ ] 5. python3 scripts/compare_sota.py --target <system> [--datasets ...]; write the summary from its report.md, including its cost table
```

Time and memory cost are recorded automatically for every run (definitions: "Cost metrics" in [protocols.md](protocols.md)); memory needs `psutil` from `requirements.txt`. Memory stays valid with `--workers > 1`. Presets run one after another and only the seeds / streams of one preset run in parallel, so the runner records for each run `concurrent_runs`, the most runs that executed at the same time as it (deterministic presets with one stream show 1 even with `--workers 3`). Times are strict only where `concurrent_runs` is 1 and comparable only between rows with the same machine and the same `concurrent_runs`; `compare_sota.py` warns when a dataset mixes values. This is what the `timing` question decides. Measuring the final model size runs at roughly 100 MB of model per second after each run (seconds for most systems, longer for 100-tree forests on full-length streams); `--no-model-size` skips it if the user does not need it.

Commands (repo root; ECPF presets need `river==0.21.2`, the runner refuses otherwise):

```bash
python3 scripts/run_benchmark.py --list-datasets                                   # every dataset, ok / MISSING on this machine
python3 scripts/run_benchmark.py --list                                            # datasets, presets (with role), suites
python3 scripts/run_benchmark.py --dataset electricity                             # main method only
python3 scripts/run_benchmark.py --dataset electricity --suite standard --seeds 3 --workers 3   # timing = parallel
python3 scripts/run_benchmark.py --dataset electricity --suite standard --seeds 3 --workers 1   # timing = strict
python3 scripts/run_benchmark.py --dataset covertype_full --preset e10bft arf100 --seeds 3 --workers 3
python3 scripts/run_benchmark.py --dataset injected_paper_electricity --workers 8   # 400 streams
python3 scripts/run_benchmark.py --dataset electricity --suite standard --max-steps 5000   # smoke
python3 scripts/run_benchmark.py --reeval outputs/benchmark                         # after an evaluator fix
python3 scripts/compare_sota.py --target e10bft                                     # report -> reports/sota_<timestamp>/
```

Presets that do not support the dataset's task are skipped automatically (forests on regression, `htr` on classification). Seeds only matter for presets with a `seed_param` (forests); `e10bft`, `ht`, `nb`, `ecpf_*` are deterministic and run once.

Outputs: `outputs/benchmark/<dataset>/<preset>/runs.csv` (one row per run, merged with earlier runs of the same pair; includes the cost columns and `machine`) and one directory per run with `preds.npz`, `manifest.json` (with `cost` and `machine`), `metrics.json`. `compare_sota.py` also writes `cost.csv`. Re-running the same dataset x preset x stream x seed overwrites that run directory; use `--out-dir outputs/benchmark_<tag>` to keep a separate version, and `compare_sota.py --root` to report on it.

Data that is not in git: `airlines_full` / `covertype_full` and the source of `injected_paper_covertype` need `cd data/dataset_0921/real_dataset/script && python3 prepare_all.py --full` once. `injected_paper_*` streams are generated in memory from a fixed seed per trial (50 trials x 8 cells); `--trials` / `--cells` select a subset, but only the full set is comparable with the paper's cells.

## Hard rules

- Never compute a metric yourself. All numbers come from `metrics.json` / `runs.csv` written by the runner and from `compare_sota.py`.
- Never edit `src/metrics/evaluate_run.py`, `configs/datasets_0921.json` or an existing preset during an experiment. If a definition looks wrong, stop and tell the user; after a fix, run `--reeval` instead of re-running.
- Never claim SOTA on a dataset whose registry entry has `"comparable": false`, or from a row whose `comparable` column is `False` (smoke run, version mismatch, or a preset kind outside the entry's `comparable_kinds`). Report those numbers as reference only, quoting `comparability_note` and `not_comparable_reason`.
- Datasets with `"role": "report"` are for final numbers. Do not tune or pick settings by looking at their results; tune on `"role": "dev"` datasets, freeze a new preset, commit, then run the report datasets.
- New system settings go into a **new** preset file (copy an existing one, change `name`, set `role`). Do not change a preset that already has reported results. Changing `main_preset` in `configs/benchmark_defaults.json` needs the user's explicit request.
- Never compare times of runs from different machines (`machine` column) or with different `concurrent_runs`; say so when a report mixes them. Present a time difference as a result only from rows with `concurrent_runs` = 1; otherwise call the times indicative. Never compare our cost numbers with costs printed in papers (different hardware and implementations); compare only with baselines re-run here.

## Which metric to compare

Use the registry entry's `required_metrics` and `sota` list; the metric names match `runs.csv` columns. Protocol details and metric definitions: [protocols.md](protocols.md).

Always put these next to the system's numbers:
- `baseline_no_change_acc` and `baseline_majority_acc` (in every classification row);
- baselines re-run in this harness (the `standard` suite), because the same method differs by 2-5% across papers.

Injected detection cells are reported **pooled over the 50 trials** (tp/fp/fn summed, then F1), as Cerqueira et al. fill their tables; `compare_sota.py` and the runner summary do this through `pool_detection_runs`. Never compare averaged per-trial F1 with their numbers. On `injected_paper_*` only `detector` presets are comparable; the main method replaces models on alarms, so its detection F1 there is reference only (say so).

## Report template

```markdown
## <dataset> — <system> vs literature

Comparable to literature: yes/no (<comparability_note if no>)
Runs: <n streams> x <n seeds>, commit <sha>, river <version>

| System | acc_prequential | kappa_t | kappa_m | ... | source |
|---|---|---|---|---|---|
| e10bft (ours, main) | value | ... | | | this harness |
| arf100 (re-run) | mean ± std | ... | | | this harness |
| No-change | ... | | | | this harness |
| <literature method> | value | ... | | | <source from registry> |

Cost (from compare_sota's cost table; machine <cpu / RAM>; times strict / indicative):

| System | runtime_s | cpu_time_s | rss_increment_mb | model_size_final_mb | ram_hours_gb | concurrent_runs |
|---|---|---|---|---|---|---|
| e10bft (ours, main) | mean ± std | ... | | | | 1 |
| arf100 (re-run) | mean ± std | ... | | | | 3 |

Claim strength: "beats re-run baselines in the same harness, significant in compare_sota's tests" (strong) vs "above the published number" (weak, implementations differ).
```

## Known limitations

Tell the user instead of improvising:
- The detector presets (`det_adwin*`, role `detector_reference`) use River, not CapyMOA/MOA. Scoring is verified exactly against Cerqueira et al.'s published alarms, but `det_adwin` does not yet reproduce their ADWIN cells (registry `calibration` block). They are only needed for claims about detectors in Cerqueira et al.'s detection-only workflow.
- `main.py`, `run_ecpf_recurring.py` and `scripts/experiment_*` still compute their own metrics; never quote them as benchmark numbers.
