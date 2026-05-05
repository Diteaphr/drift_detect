# Hierarchical Parallel ECPF Runbook

This runbook documents the experimental hierarchical-parallel ECPF detector.
It is added alongside the existing Dynamic Weighted ECPF detector; it does not
replace the original DWM implementation.

## Files

- `detectors/meta_ecpf/hierarchical_parallel.py`
- `detectors/meta_ecpf/dynamic_weighted.py`
- `detectors/meta_ecpf/indicators.py`
- `detectors/meta/dynamic_weighted.py`

The new detector class is:

```python
HierarchicalParallelECPFDetector
```

It subclasses `DynamicWeightedVotingECPFDetector` so it can reuse the existing
indicator and atom-detector plumbing while changing the decision logic.

## Why This Exists

The original DWM idea tried to combine heterogeneous atom detectors using one
weighted vote. In practice, that can become a consensus bottleneck:

- sudden detectors can fire alone but get diluted by gradual detectors
- UQ and ErrorTrend are noisy and should not grade atom detector correctness
- requiring all signals to align on the same exact instance is too strict

The hierarchical-parallel detector separates responsibilities instead of
forcing everything into one pool-level vote.

## State Machine

The intended lifecycle is:

```text
Step 1. UQ + ErrorTrend both trigger
        -> open warning buffer

Step 2. While warning buffer is active
        -> atom detectors keep reading the error stream

Step 3. gradual-path atom vote >= threshold
        and warning age >= minimum confirmation age
        -> confirmed drift

Step 4. ECPF uses warning buffer for expert comparison

Step 5. After drift is handled
        -> reset atom/proxy transient state
        -> close warning buffer
        -> enter cooldown
```

## Paths

Fast path:

```text
ADWIN, DDM
```

These are tracked separately for diagnostics. They are intended to represent
fast/sudden sensitivity.

Gradual confirmation path:

```text
HDDM_A, PageHinkley
```

These confirm drift during an active warning buffer.

Current confirmation rule:

```text
gradual_path_score >= 0.5
```

With two gradual-path detectors, this means at least one gradual-path detector
must vote drift while warning is active and the minimum warning-buffer age has
been reached.

## Proxy Role

UQ and ErrorTrend are not treated as ground truth.

They do not punish or reward atom detector weights. Their only role is to open
the warning state.

This avoids the earlier logical problem where noisy proxy signals acted like a
teacher grading atom detectors.

## ECPF Interaction

The detector returns the same shape as other meta detectors:

- `is_drift`
- `t`
- `sub_detector_stats`

Pipeline behavior is unchanged:

1. `proxy_indicators["any_warning"]` opens the ECPF warning buffer.
2. Incoming stream samples are collected into `_ecpf_buffer`.
3. `is_drift=True` calls `_handle_ecpf_drift(...)`.
4. ECPF compares stored experts and a fresh learner on the warning buffer.
5. `notify_drift()` resets transient detector state and enters cooldown.

## Diagnostics

Useful fields in event details:

- `meta_info.score_ratio`: all-atom weighted score
- `meta_info.fast_path_score`: score for ADWIN/DDM
- `meta_info.gradual_path_score`: score for HDDM_A/PageHinkley
- `meta_info.gradual_confirm_threshold`
- `proxy_indicators.warning_age`
- `proxy_indicators.cooldown_until`

These help distinguish:

- warning opened but gradual path never confirmed
- gradual path confirmed too early
- cooldown suppressing repeated warnings
- fast path seeing something that gradual path does not confirm

## How To Test

The detector is available through an explicit signal mode:

```text
meta_ecpf_hier_parallel
```

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

## Expected Benefits

Compared with plain DWM, this design should:

- avoid sudden/gradual vote dilution
- keep proxy signals out of atom-detector grading
- allow warning and confirmation to happen over a window instead of the same
  exact sample
- produce warning buffers that ECPF can use for expert comparison

## Known Risks

This design is still experimental.

Possible failure modes:

- UQ + ErrorTrend may open warning too early
- gradual confirmation may still produce false positives
- warning buffers may be too short or too long if timeout/min-age parameters are
  not tuned
- reuse precision can be low if the fresh learner beats stored experts on the
  warning buffer

Interpret results as detector-behavior diagnostics first, not as final model
quality.
