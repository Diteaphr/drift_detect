# Instructions for AI coding agents

## Benchmark / SOTA experiments on `data/dataset_0921`

When the user asks to run an experiment, a benchmark or a SOTA comparison on a `data/dataset_0921` dataset (electricity, airlines, covertype, INSECTS, injected, synthetic), to compare the main method or another system against SOTA or baselines, to re-evaluate stored runs, or to report existing results:

1. Read [`.agents/skills/dataset0921-benchmark/SKILL.md`](.agents/skills/dataset0921-benchmark/SKILL.md) and follow it step by step (it links `protocols.md` in the same folder).
2. Before running anything, ask the user the multiple-choice questions in its Step 1 (experiment goal, datasets available on this machine, system, baselines, seeds, scope, report, timing strictness) and wait for the answers.

Short version of its rules:
- The system under test is the main method preset `e10bft` (single Hoeffding Tree) unless the user names another preset.
- Run experiments only through `scripts/run_benchmark.py` and report through `scripts/compare_sota.py`; never compute or quote metrics yourself.
- Never claim SOTA from rows or datasets marked not comparable.
