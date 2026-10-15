# Protocols and metric definitions

All metrics are computed by `src/metrics/evaluate_run.py`; this page only says what they mean and which literature number each one lines up with.

## Common rules

- Test-then-train from the first instance. Pipeline presets with a warm start predict each warm-start row before learning it, so `acc_prequential` covers the whole stream (`metric_scope = "full"`).
- `acc_post_warmup` is the old in-repo number (rows after the warm start only); never compare it with literature.
- Alarms are the step index at which the system reported a drift (`alarm_idx`), not the retro-dated warning time (`alarm_ts`, also stored).

## Classification metrics (MOA / CapyMOA definitions)

| Column | Definition |
|---|---|
| `acc_prequential` | Fraction correct over the whole stream |
| `acc_window1000_mean` | Mean over all instances of the accuracy of the last 1000 predictions (partial windows at the start) |
| `kappa` | Cohen's kappa |
| `kappa_t` | Kappa vs no-change classifier (predict previous label; first prediction is class 0) |
| `kappa_m` | Kappa vs majority classifier (class counts include the current instance) |
| `macro_f1` | Mean per-class F1 over all classes 0..K-1; never-predicted classes count as 0 |
| `baseline_no_change_acc`, `baseline_majority_acc` | Accuracy of those two reference classifiers on the same stream |

## Detection metrics (Cerqueira et al. `EvaluateDriftDetector`)

| Column | Definition |
|---|---|
| `tp`, `fp`, `fn` | Every alarm inside a drift's window is a TP (several per drift possible); others are FP; a drift with no alarm in its window is a FN |
| `precision`, `recall`, `f1` | From those counts (recall may count several hits per drift) |
| `episode_recall` | Fraction of drifts with at least one alarm in the window |
| `mdt`, `ndt` | Mean delay of the first in-window alarm after d_s; ndt = mdt / delta_max |
| `far`, `ar` | False alarms / all alarms per 1000 instances |
| `*_paper_window` | Same counts with the window ending at d_e + delta_max instead of d_s + delta_max |

Window: `[d_s, d_s + delta_max]` (what their code scores). For abrupt drifts both windows are identical.

Per-run rows hold one stream each. A literature cell is the pool of its 50 trials (`pool_detection_runs`): tp/fp/fn summed before precision/recall/F1; MDT = mean first-hit delay over detected trials; `far_cerqueira` = summed false alarms / one stream length x 1000 (their formula, equal to the sum of per-run `far`), `far_per_run` = the per-stream average.

On `injected_paper_*` (`coordinates: "input"`) alarm indices, drift points and the stream length count the rows the injection dropped, as their workflow does; `alarm_idx_input` in `preds.npz` holds the mapped alarms. Alarms before `int(0.25 x n_input) + 1` are ignored (`detect_from`).

## Cost metrics (`src/metrics/run_cost.py`)

Recorded for every run in `manifest.json` (`cost`, `machine`) and in `runs.csv`; `compare_sota.py` aggregates them into `cost.csv` and the report's cost table. Every run executes in its own freshly spawned process with one BLAS/OpenMP thread, and the libraries it needs are imported before the memory baseline.

| Column | Definition |
|---|---|
| `runtime_s` | Wall time of the predict-then-learn loop (data loading, evaluation and model sizing excluded) |
| `cpu_time_s` | Process CPU time over the same window; less sensitive to parallel load than wall time |
| `instances_per_s` | Stream length / `runtime_s` |
| `rss_before_mb`, `rss_peak_mb` | Resident memory (RSS, what the operating system reports) of the run's process right before the system is built, and the highest value sampled every 0.2 s while it runs |
| `rss_increment_mb` | `rss_peak_mb - rss_before_mb`: real memory the system needed. Memory freed while loading the data can be reused, so for very small models it can read slightly below `model_size_final_mb` |
| `ram_hours_gb` | The RSS increment integrated over wall time, in GB x hours (MOA reports RAM-Hours from model size; this one uses real memory) |
| `process_peak_rss_mb` | Peak RSS of the whole process (interpreter, libraries and data included) |
| `model_size_final_mb` | Python object graph of the system after the last instance (`deep_sizeof`; input data excluded; memory inside C extensions without Python references is not seen). Measured after the timed window; `--no-model-size` skips it |
| `concurrent_runs` | Most runs (this one included) that executed at the same time as this run; 1 = it ran alone |
| `workers`, `machine` | The `--workers` setting and the hardware (`manifest.machine`: CPU, cores, RAM, BLAS threads) |

Memory numbers are per process and stay valid with `--workers > 1` as long as the machine does not swap. Presets run one after another and only the seeds / streams of one preset run in parallel, so `workers` overstates the load of single-run presets; use `concurrent_runs`. Times are strict only where `concurrent_runs` is 1 (`--workers 1`) and comparable only between runs on the same machine with the same `concurrent_runs`. Runs made before cost tracking have empty cost columns; re-run them to get costs.

## Protocols

| Protocol | Datasets | Compare with |
|---|---|---|
| `real_prequential` | electricity, airlines_full, covertype_full (comparable); airlines, covertype (100k cap), gas, ai4i, regression | `acc_prequential`, `kappa_t`, `kappa_m` vs DriftMoE / Souza; detection fields are null (no ground truth) |
| `insects` | 5 balanced INSECTS variants | `acc_window1000_mean` vs Souza Table 5 (ARF); `acc_prequential` vs Table 6 (NB + detector); detection F1 has no paper baseline except Minato et al. on incremental_gradual |
| `injected_detection` | injected_paper_* (comparable, `detector` presets only); injected_* (old width ≤ 1000, 10 trials, reference only) | Pooled detection metrics per cell (`abrupt/class_prior`, ...) vs `sota_by_cell` (best of their 14 detectors) and `calibration` (their ADWIN) |
| `synthetic` | synthetic_* | Only vs baselines re-run in this harness |

## Detection-only workflow (`kind: "detector"` presets)

Reproduces `SupervisedStreamingWorkflow` of Cerqueira et al.: one Hoeffding Tree with library defaults trained on every row and never reset; after 25% of the input stream the detector receives `int(y == y_pred)` each row; alarms are only recorded. `det_adwin` uses MOA's `ADWINChangeDetector` semantics (what CapyMOA's ADWIN runs): the window is not reset after a detection and only a rise of the input mean counts, which with a correctness signal means their ADWIN fires when accuracy goes **up** (typically when the tree recovers after a drift). `det_adwin_river` keeps River's semantics (reset after each detection, both directions) for contrast.
