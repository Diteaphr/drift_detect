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

## Protocols

| Protocol | Datasets | Compare with |
|---|---|---|
| `real_prequential` | electricity, airlines_full, covertype_full (comparable); airlines, covertype (100k cap), gas, ai4i, regression | `acc_prequential`, `kappa_t`, `kappa_m` vs DriftMoE / Souza; detection fields are null (no ground truth) |
| `insects` | 5 balanced INSECTS variants | `acc_window1000_mean` vs Souza Table 5 (ARF); `acc_prequential` vs Table 6 (NB + detector); detection F1 has no paper baseline except Minato et al. on incremental_gradual |
| `injected_detection` | injected_paper_* (comparable, `detector` presets only); injected_* (old width ≤ 1000, 10 trials, reference only) | Pooled detection metrics per cell (`abrupt/class_prior`, ...) vs `sota_by_cell` (best of their 14 detectors) and `calibration` (their ADWIN) |
| `synthetic` | synthetic_* | Only vs baselines re-run in this harness |

## Detection-only workflow (`kind: "detector"` presets)

Reproduces `SupervisedStreamingWorkflow` of Cerqueira et al.: one Hoeffding Tree with library defaults trained on every row and never reset; after 25% of the input stream the detector receives `int(y == y_pred)` each row; alarms are only recorded. `det_adwin` uses MOA's `ADWINChangeDetector` semantics (what CapyMOA's ADWIN runs): the window is not reset after a detection and only a rise of the input mean counts, which with a correctness signal means their ADWIN fires when accuracy goes **up** (typically when the tree recovers after a drift). `det_adwin_river` keeps River's semantics (reset after each detection, both directions) for contrast.
