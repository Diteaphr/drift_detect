# GDDM Runbook for This Repo

This runbook explains how the ECPF-GDDM path works in this repository, how to run it, and how to diagnose common results such as too many detected drifts.

## 1. Where GDDM Lives

Main implementation:

```text
detectors/meta_ecpf/gddm.py
```

Pipeline integration:

```text
src/pipeline.py
```

Config defaults:

```text
src/config.py
```

Runner entry points:

```text
run_ecpf_recurring.py
run_ecpf_recurring_batch.py
run_ecpf_uq_experiment.py
```

The signal mode is:

```text
meta_ecpf_gddm
```

## 2. What This GDDM Implementation Is

The paper's GDDM detects group drift from multiple error-rate streams. The idea is:

```text
Many individual streams may change only weakly.
But if many streams shift together, the group statistic becomes large.
```

In this repo, `ECPFGDDMDetector` adapts that idea to ECPF.

Primary input:

```text
per-tree prequential error-rate streams from Hoeffding Forest
```

Auxiliary input:

```text
UQ signals from the forest probability matrix
```

So the signal vector at time `t` is roughly:

```text
Z_t = [
  tree_1_rolling_error,
  tree_2_rolling_error,
  ...,
  tree_M_rolling_error,
  MI-like UQ,
  vote disagreement,
  predictive entropy,
  ensemble margin
]
```

This is closest to original GDDM when labels are available, because per-tree errors are observed. The UQ signals are repo-specific auxiliary signals.

## 3. How The Statistic Works

GDDM keeps two windows:

```text
reference window: older signal vectors
test window: recent signal vectors
```

Current defaults:

```text
ecpf_gddm_reference_window = 160
ecpf_gddm_test_window = 60
```

For each signal dimension, it compares the ranks of the recent window against the reference window using a Mann-Whitney-U-style statistic.

Then it sums squared standardized scores across dimensions:

```text
U = sum(z_j^2 for each signal dimension j)
```

Thresholds are estimated by permutation:

```text
G_warning = permutation quantile at 1 - warning_alpha
G_drift   = permutation quantile at 1 - drift_alpha
```

Current defaults:

```text
ecpf_gddm_warning_alpha = 0.10
ecpf_gddm_drift_alpha = 0.01
ecpf_gddm_n_permutations = 19
ecpf_gddm_threshold_update_interval = 250
```

The detector reports these values in event CSVs:

```text
gddm_U
gddm_G_warning
gddm_G_drift
gddm_drift_type
```

## 4. How GDDM Connects To ECPF

The pipeline path is:

```text
Hoeffding Forest prediction
-> per-tree proba matrix
-> GDDM signal vector
-> GDDM warning/drift state
-> ECPF warning buffer
-> ECPF model pool / expert comparison
```

In `src/pipeline.py`, GDDM runs under:

```text
ecpf_signal_mode == "meta_ecpf_gddm"
```

When GDDM opens warning:

```text
pipeline starts collecting _ecpf_buffer
```

When GDDM confirms drift:

```text
pipeline calls _handle_ecpf_drift(...)
```

Then ECPF compares:

```text
current model vs best reusable model vs newly trained model
```

The event source will be:

```text
meta_ecpf_gddm
```

The protocol will be:

```text
gddm_group_warning_then_rank_drift
```

## 5. How To Run

Single dataset:

```bash
MPLBACKEND=Agg python3 run_ecpf_recurring.py \
  --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
  --signal-mode meta_ecpf_gddm \
  --uq-mode mi_like \
  --warm-start 200 \
  --max-steps 20000
```

Batch `g00 ... g09`:

```bash
python3 run_ecpf_recurring_batch.py \
  --signal-mode meta_ecpf_gddm \
  --uq-mode mi_like \
  --warm-start 200 \
  --max-steps 20000 \
  --print-events \
  --out-csv outputs/gddm_20k_summary.csv \
  --events-csv outputs/gddm_20k_events.csv
```

UQ experiment table:

```bash
python3 run_ecpf_uq_experiment.py \
  --settings G_meta_ecpf_gddm \
  --warm-start 200 \
  --max-steps 20000 \
  --out-dir outputs/gddm_20k_uq
```

## 6. Why Detected Drift Can Be Much Larger Than Ground Truth

If you see output like:

```text
gt=1 detected=87
```

that does not mean the data has 87 real drifts.

It usually means GDDM is too sensitive or has entered a feedback loop:

```text
GDDM detects drift
-> ECPF changes/reuses/trains model
-> model output distribution changes
-> GDDM sees that model-induced change
-> GDDM detects drift again
```

This is especially likely if event rows show:

```text
buffer_len is very small
timestamps are almost periodic
current model accuracy on warning buffer is already high
```

Small `buffer_len` means the detector confirmed before ECPF collected enough warning data. That makes model-pool decisions noisy and can create more downstream instability.

## 7. Parameters That Control Over-Detection

Most important knobs in `src/config.py`:

```text
ecpf_gddm_min_updates
```

Minimum GDDM samples after reset before it can fire. Larger values reduce early false alarms.

```text
ecpf_gddm_min_confirmation_age
```

Minimum warning-buffer age before drift can be confirmed. This prevents one-sample or tiny-buffer drift events.

```text
ecpf_gddm_cooldown
```

Minimum quiet period after a confirmed drift. This reduces repeated alarms from ECPF's own model changes.

```text
ecpf_gddm_drift_alpha
```

Smaller means stricter drift threshold.

```text
ecpf_gddm_reference_window
ecpf_gddm_test_window
```

Larger windows are slower but usually less twitchy.

Current conservative defaults are:

```text
ecpf_gddm_min_updates = 2000
ecpf_gddm_min_confirmation_age = 60
ecpf_gddm_cooldown = 2000
ecpf_gddm_n_permutations = 19
ecpf_gddm_threshold_update_interval = 250
```

## 10. Performance Notes

GDDM is slower than ADWIN/DDM-style scalar detectors because it estimates an adaptive group threshold by permutation.

The expensive part is:

```text
for each threshold update:
  run n_permutations random splits
  for each split:
    rank every signal dimension
    compute the group statistic
```

With the current signal vector, one sample has about:

```text
number of trees + UQ signals = 5 + 4 = 9 dimensions
```

So a 20k batch over 10 files can become slow if thresholds are recomputed too frequently. The debug-friendly defaults now cache thresholds longer:

```text
ecpf_gddm_threshold_update_interval = 250
ecpf_gddm_n_permutations = 19
```

For more paper-like but slower runs, increase `ecpf_gddm_n_permutations`. For faster parameter search, reduce it further and increase `ecpf_gddm_threshold_update_interval`.

## 8. How To Read Event Rows

Useful event columns:

```text
timestamp
source
drift_type
ecpf_protocol
gddm_U
gddm_G_warning
gddm_G_drift
gddm_drift_type
buffer_len
acc_current_on_warning
acc_best_on_warning
acc_new_on_warning
```

Interpretation:

```text
gddm_U > gddm_G_warning
```

means GDDM considered the group shift suspicious.

```text
gddm_U > gddm_G_drift
```

means GDDM considered it large enough for drift confirmation, subject to persistence, buffer age, and cooldown rules.

If:

```text
acc_current_on_warning is high
acc_best_on_warning is high
acc_new_on_warning is low
```

then the alarm may be a detector/model-output shift rather than a true concept drift.

## 9. Current Caveats

This module is a GDDM-style implementation, not a line-by-line reproduction of the paper.

Important differences:

```text
Original GDDM input: multi-stream error-rate vector
This repo input: per-tree rolling error rates + optional UQ signals
```

When labels are available, per-tree errors keep it close to the original paper. UQ signals are an ECPF-specific extension.

Also, because ECPF changes the model after drift, GDDM is watching a moving system. That means cooldown and minimum buffer age are not optional details; they are necessary to prevent detector-induced drift loops.
