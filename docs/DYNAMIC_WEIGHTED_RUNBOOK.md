# Dynamic Weighted Voting Runbook

This document explains the Dynamic Weighted Voting detector used by the drift
pipeline, with special focus on the ECPF path:

```bash
python3 run_ecpf_recurring_batch.py \
  --signal-mode meta_ecpf_dwm \
  --uq-mode mi_like \
  --print-events \
  --max-steps 20000
```

## Components

The core implementation is:

- `detectors/meta/dynamic_weighted.py`
- `detectors/meta_ecpf/dynamic_weighted.py`
- `detectors/meta_ecpf/indicators.py`

The ECPF entry point in the pipeline selects `DynamicWeightedVotingECPFDetector`
when `ecpf_signal_mode == "meta_ecpf_dwm"`.

## High-Level Flow

For each stream instance, the detector receives:

- `x`: current feature vector
- `y_true`: true label
- `y_pred`: current model prediction
- `err`: prediction error
- optional `proba_matrix`: per-tree probability outputs, if available

Then it runs three layers:

1. Proxy indicators
2. Atom detectors
3. Dynamic weighted vote

The final drift score is:

```text
score = sum(weight_i for atom detector i that votes drift) / sum(all weights)
global_drift = score >= threshold
```

The current fallback threshold is `0.5`, so one detector alone should not be
enough when the ensemble has the default six atom detectors.

## Proxy Indicators

In regular `DynamicWeightedVotingDetector`, the default proxy is:

- `KSDistributionIndicator`

In ECPF-DWM, `DynamicWeightedVotingECPFDetector` uses two proxy indicators:

- `UQWarningIndicator`
- `ErrorRateTrendIndicator`

ECPF-DWM sets:

```text
proxy_policy = "all"
```

That means the proxy gate opens only when both UQ and error trend agree.

This is intentional: UQ alone is noisy, and error trend alone is delayed/noisy.
Using both as a confirmation gate reduces the "one noisy teacher punishes all
atom detectors" problem.

## UQ Behavior

`UQWarningIndicator` wraps `src.uq_warning_detector.UQWarningDetector`.

If the model provides `proba_matrix`, UQ is based on the configured mode:

- `mi_like`
- `vote_disagreement`
- `predictive_entropy`

If no `proba_matrix` is available, it falls back to
`UncertaintyProxyIndicator`, using prediction instability as a lightweight
proxy. This keeps `meta_ecpf_dwm` from silently becoming UQ=0 when the current
model backend does not expose per-tree probabilities.

## Error Trend Behavior

ECPF-DWM uses:

```text
short_window = 50
long_window = 250
threshold = 0.05
```

The indicator fires when:

```text
mean(error over last 50) - mean(error over last 250) > threshold
```

This detects short-term performance degradation.

## Atom Detectors

The atom detector ensemble is managed by `UnifiedDriftDetector`.

Default atom detectors:

- `hddm_w`
- `eddm`
- `ddm`
- `hddm_a`
- `page_hinkley`
- `adwin`

Each atom detector sees the prediction error stream and votes `True` or `False`
for drift.

## Dynamic Weights

Weights start at `1.0`.

When the proxy gate is confirmed:

- Atom voted drift: mild reward, capped at `1.0`
- Atom did not vote: mild decay

When the proxy gate is not confirmed:

- No proxy-based punishment is applied
- Weights recover slowly toward `1.0`

This is important. Proxy indicators are not ground truth. They are only noisy
context signals. The detector should not aggressively punish atom detectors just
because UQ or error trend did not agree at one timestamp.

## ECPF Cooperation

In `meta_ecpf_dwm` mode, Dynamic Weighted Voting has two jobs:

1. Start an ECPF warning buffer
2. Confirm drift so ECPF can run its model-pool logic

The pipeline reads `proxy_indicators["any_warning"]`.

For ECPF-DWM, because `proxy_policy = "all"`, that field is intentionally
reported as the confirmed proxy gate, not simple OR.

The lifecycle is:

1. UQ + ErrorTrend both warn
2. Pipeline opens `_ecpf_warning_active`
3. Incoming `(x, y)` samples are appended to `_ecpf_buffer`
4. Atom weighted vote reaches threshold
5. Pipeline calls `_handle_ecpf_drift(...)`
6. ECPF compares stored experts and a fresh learner on the warning buffer
7. ECPF installs the selected reused expert copy as active model
8. Pipeline calls `meta_detector.notify_drift()`

## Why Large Event Counts Are Suspicious

This kind of summary is not healthy:

```text
g03 detected_drift_events = 237
g09 detected_drift_events = 190
```

The event CSV showed many rows with:

```text
buffer_len = 1
```

That means the system was repeatedly doing:

1. Drift confirmed
2. ECPF buffer cleared
3. Next sample immediately starts/finishes another drift
4. ECPF receives a one-sample warning buffer

That is not a meaningful recurring drift signal. It is repeated detector state
leaking across ECPF drift handling.

The fix is in `DynamicWeightedVotingDetector.notify_drift()`:

- Keep learned DWM weights
- Reset atom detector state
- Reset proxy indicator state
- Clear `first_proxy_warning_t`

This prevents stale atom/proxy states from immediately retriggering ECPF.

## Reading Batch Results

Useful columns:

- `groundtruth_drift_count`: number of true drift starts inside the evaluated prefix
- `detected_drift_events`: number of ECPF drift handlings
- `pool_alive_snapshots`: number of live ECPF experts after the run
- `prequential_accuracy`: test-then-train stream accuracy after warm start

Healthy behavior for `max_steps=20000` is not necessarily "detected equals
ground truth", because `meta_ecpf_dwm` is not using oracle drift times. But
hundreds of detections on one 20k stream is almost always a bug or an overly
sensitive confirmation loop.

## Debug Checklist

When results look wrong, inspect `outputs/ecpf_batch_events.csv`:

- If many events have `buffer_len=1`, look for repeated state-triggering.
- If `uq_raw` / `uq_smoothed` are empty, the model likely did not provide
  `proba_matrix` and the fallback proxy was used.
- If event timestamps form long consecutive runs, atom detectors are probably
  not being reset after ECPF handles drift.
- If there are zero events everywhere, the UQ + ErrorTrend gate may be too
  strict or the model is adapting before the error trend can rise.

## Practical Interpretation

Dynamic Weighted Voting should be treated as a confirmation and coordination
layer, not a source of truth.

Good behavior:

- Proxy signals open a warning only when uncertainty and error trend agree.
- Atom detectors confirm drift by weighted majority.
- ECPF receives a non-trivial warning buffer.
- After ECPF handles drift, detector state is cleared while learned weights are
  preserved.

Bad behavior:

- One atom detector can trigger global drift alone.
- Proxy indicators punish atom detectors aggressively.
- ECPF receives many one-sample buffers.
- Drift events cluster in long consecutive sequences.

## Comparison: Dynamic Weighted vs Dual ADWIN

Two ECPF signal modes are commonly compared:

```bash
python3 run_ecpf_recurring_batch.py --signal-mode detector --print-events
```

and:

```bash
python3 run_ecpf_recurring_batch.py \
  --signal-mode meta_ecpf_dwm \
  --uq-mode mi_like \
  --print-events \
  --max-steps 20000
```

They are not measuring exactly the same thing.

### Dual ADWIN

`--signal-mode detector` uses the standalone ECPF detector:

- warning ADWIN on the binary error stream
- drift ADWIN on the binary error stream
- ECPF starts buffering at warning
- ECPF handles drift when drift ADWIN fires

This is conceptually clean because warning and drift confirmation are both
derived from the same supervised error stream.

In the full recurring batch, Dual ADWIN produced roughly ground-truth-scale
event counts:

```text
total ground-truth drifts ~= 82
total detected events ~= 80
mean accuracy ~= 0.959
```

That is broadly reasonable as a detector-driven ECPF baseline.

But it still has two warning-buffer symptoms to watch:

- very short buffers such as `buf=33` or `buf=65`
- very long buffers such as `buf=7000+` or `buf=10000+`

Short buffers mean warning and drift fired very close together. Long buffers
mean warning opened much earlier than drift confirmation. Both can be valid in
ADWIN terms, but they make ECPF's model comparison sensitive to warning-window
quality.

### Dynamic Weighted ECPF

`--signal-mode meta_ecpf_dwm` uses:

- UQ proxy
- error trend proxy
- atom detector weighted vote
- ECPF warning buffer

The intended logic is:

```text
UQ + ErrorTrend agree within a short temporal join window -> open warning buffer
while warning is active, atom detectors continue reading the error stream
weighted atom vote >= threshold after minimum buffer age -> confirm drift
ECPF compares experts/new learner on warning buffer
after drift handling, reset transient atom/proxy state and enter cooldown
```

After resetting transient atom/proxy state in `notify_drift()`, the pathological
hundreds-of-events behavior is gone. For the 20k prefix, the observed scale was:

```text
total ground-truth drifts = 14
total detected events = 9
mean accuracy ~= 0.942
```

That is far more plausible than the previous `g03=237` / `g09=190` result.

However, it is still not as clean as Dual ADWIN. Many Dynamic Weighted event
timestamps are early warning-start timestamps, not the later atom-confirmation
timestamps printed by the DWM debug block. Example pattern:

```text
[Dynamic DWM] Global Drift Detected at step t=6601
[event] timestamp=791, buffer_len=5811
```

This means:

- warning opened at `791`
- weighted atom vote confirmed at about `6601`
- ECPF event timestamp records warning start

So the large `buffer_len` values are not a print bug. They indicate warning
opened too early and remained active for thousands of samples.

### Current Fairness Issue

If `run_ecpf_recurring.py` / batch config uses `model_type="ht"`, then the model
does not provide per-tree probability matrices. In that case, `--uq-mode
mi_like` does not actually produce MI-like forest UQ; the UQ indicator falls
back to prediction-instability proxy behavior.

The empty `uq_raw` / `uq_smoothed` columns in events are a clue that real UQ was
not available for those runs.

So a fair comparison is:

- Dual ADWIN: supervised binary-error ADWIN baseline
- Dynamic Weighted current run: hybrid proxy gate, but not necessarily true
  MI-like UQ unless the model exposes `proba_matrix`

### Is The Approach Reasonable?

Dual ADWIN is currently the more reasonable baseline:

- simpler
- fewer moving parts
- event counts closer to ground truth on full streams
- better mean accuracy in the shown run
- warning/drift semantics are internally consistent

Dynamic Weighted is reasonable as a research direction, but the current version
should be treated as experimental:

- it mixes heterogeneous signals with different lag/noise properties
- warning often opens too early
- confirmation can arrive thousands of samples later
- true UQ may be absent depending on model backend
- debug output reports confirmation time while event CSV records warning-start
  time, which can make interpretation confusing

The next thing to tune is not adding more atom detectors. It is making the
warning lifecycle stricter:

- cap warning age
- require a minimum and maximum ECPF buffer length
- log both `warning_start_t` and `confirmation_t`
- avoid using fallback prediction variance when the experiment claims
  `mi_like` UQ

## Current State-Machine Implementation

The current DWM/ECPF implementation follows this lifecycle:

```text
Step 1. UQ + ErrorTrend agree within the proxy join window
        -> open warning buffer

Step 2. While warning buffer is active
        -> atom detectors keep reading the error stream

Step 3. weighted atom vote >= threshold
        and warning age >= minimum confirmation age
        -> confirmed drift

Step 4. ECPF uses warning buffer for expert comparison

Step 5. After drift is handled
        -> reset atom/proxy transient state
        -> close warning buffer
        -> enter cooldown
```

Important design choice:

```text
Proxy signals do not punish or reward atom detector weights.
```

UQ and ErrorTrend are not ground truth. They only open the warning state. Atom
detectors only confirm drift. Until there is labeled detector correctness, DWM
weights are kept stable instead of being adjusted by proxy agreement.

In the latest 20k ECPF-DWM probe, this state machine changed behavior from:

```text
no DWM events, pool ~= 1.0, reuse_precision = NaN
```

to:

```text
mean accuracy ~= 0.950
mean delay ~= 465
false warning rate ~= 0.45
reuse precision ~= 0.19
average pool size ~= 1.4
```

This means the implementation now reaches ECPF reuse decisions, but ECPF often
finds the fresh learner better than the reused expert on the warning buffer.
That is a model-pool quality/result issue, not a "DWM never calls ECPF" issue.
