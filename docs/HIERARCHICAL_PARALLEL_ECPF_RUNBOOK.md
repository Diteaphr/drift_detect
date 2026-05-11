# Hierarchical Hypothesis ECPF Runbook

This runbook documents the detector currently exposed as:

```python
HierarchicalParallelECPFDetector
```

The class and signal-mode names are kept for experiment compatibility, but the
implementation is now a hierarchical multiple-hypothesis trigger:

```text
Detection Layer -> candidate drift
Validation Layer -> confirmed drift
ECPF -> expert reuse / new learner comparison
```

It is no longer a dynamic weighted voting detector. It subclasses the existing
ECPF-DWM class only to reuse indicator, atom-detector, and pipeline plumbing.

## Files

- `detectors/meta_ecpf/hierarchical_parallel.py`
- `src/config.py`
- `src/pipeline.py`
- `run_ecpf_recurring.py`
- `run_ecpf_uq_experiment.py`

The signal mode is still:

```text
meta_ecpf_hier_parallel
```

## Core Idea

The old version used UQ + ErrorTrend to open a warning buffer, then let gradual
atom-detector votes directly confirm drift. That behaved like a path-based DWM.

The new version separates the hypotheses:

```text
H_detect:
    low-cost detector or proxy signal proposes a candidate warning/drift

H_valid:
    recent zero-one loss must be worse than the pre-warning baseline

Detection result:
    drift is returned only when validation passes
```

So:

```text
candidate drift != confirmed drift
```

## Default Detector Stack

Default detection layer:

```text
HDDM-W
```

This keeps per-instance cost low. You can still override `selected_detectors`,
but the recommended efficient configuration is one or two detectors, such as:

```python
selected_detectors=["hddm_w"]
selected_detectors=["adwin", "hddm_w"]
selected_detectors=["page_hinkley"]
```

The detector still reports path diagnostics:

```text
fast path:    ADWIN, DDM
gradual path: HDDM-W, HDDM_A, PageHinkley, EDDM
```

With the default `["hddm_w"]`, a single HDDM-W drift vote is enough to propose a
candidate. It does not confirm drift by itself.

## State Machine

```text
Step 1. Update proxy indicators and the low-cost detection layer.

Step 2. If a proxy warning or detector candidate appears:
        -> open ECPF warning buffer
        -> start validation layer

Step 3. While warning is active:
        -> collect ECPF warning samples
        -> collect recent zero-one losses for validation

Step 4. Once minimum warning age is reached:
        -> compare recent error with baseline error
        -> confirm drift only if validation gap passes threshold

Step 5. After confirmed drift:
        -> ECPF compares current / best historical / fresh learner
        -> reset transient detector and validation state
        -> enter cooldown
```

A warning can therefore be opened by either:

```text
proxy_warning_event or candidate_drift
```

This avoids relying on UQ and ErrorTrend to fire on the same exact timestep.

## Validation Layer

The validation layer uses zero-one loss:

```python
err = int(y_pred != y_true)
```

It maintains:

```text
W_hist = pre-warning baseline errors
W_new  = warning-window recent errors
```

and computes:

```text
validation_gap = mean(W_new) - mean(W_hist)
```

Drift is confirmed only if:

```text
validation_gap > ecpf_hier_validation_gap_threshold
```

Default validation parameters:

```python
ecpf_hier_validation_hist_size = 250
ecpf_hier_validation_new_size = 60
ecpf_hier_validation_min_new_size = 30
ecpf_hier_validation_gap_threshold = 0.02
```

The validation cost is O(1) per instance.

## Config Knobs

```python
ecpf_hier_fast_candidate_threshold = 0.5
ecpf_hier_gradual_candidate_threshold = 0.5
ecpf_hier_proxy_policy = "any"
ecpf_hier_validation_hist_size = 250
ecpf_hier_validation_new_size = 60
ecpf_hier_validation_min_new_size = 30
ecpf_hier_validation_gap_threshold = 0.02
```

Shared ECPF timing knobs still apply:

```python
ecpf_warning_length       # minimum confirmation age
ecpf_uq_warning_timeout   # max active warning age
```

## Event Diagnostics

The event CSV now includes the important hierarchical-hypothesis fields:

```csv
candidate_drift,
candidate_source,
fast_path_score,
gradual_path_score,
validation_passed,
validation_gap,
hist_error,
new_error,
warning_start_t,
confirmation_t,
warning_age,
buffer_len
```

These columns are the main evidence that the validation layer is doing work,
instead of simply returning atom-detector votes.

## How To Test

Single-file run:

```bash
python3 run_ecpf_recurring.py \
  --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
  --signal-mode meta_ecpf_hier_parallel \
  --uq-mode mi_like \
  --max-steps 20000
```

Batch run:

```bash
python3 run_ecpf_recurring_batch.py \
  --signal-mode meta_ecpf_hier_parallel \
  --uq-mode mi_like \
  --print-events \
  --max-steps 20000
```

UQ experiment run:

```bash
python3 run_ecpf_uq_experiment.py \
  --settings F_hier_parallel \
  --max-steps 20000 \
  --print-events
```

Recommended comparison:

```text
A_baseline_ht_error
B_hf_error_direct
E_meta_ecpf_dwm
F_hier_parallel
```

Interpret `F_hier_parallel` as:

```text
ECPF + HF + HDDM-W candidate + zero-one validation
```

## Expected Benefits

- lower runtime than the old six-detector path ensemble
- cleaner distinction between warning, candidate drift, and confirmed drift
- fewer false confirmations from one noisy atom vote
- event logs that expose why validation passed or failed

## Known Risks

- `validation_gap_threshold=0.02` may need a dataset sweep
- if the baseline error is already high, the gap can be conservative
- if the model adapts very quickly during warning collection, the gap can shrink
- proxy-only warnings will not confirm unless a detector candidate has also been
  seen during the warning lifecycle
