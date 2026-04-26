# ECPF Runbook (How To Run + What Is Implemented)

This document explains:
- what has been implemented for ECPF so far,
- how to run single-file and batch experiments,
- what output files mean,
- how to interpret key metrics.

## 1) What Has Been Implemented

### Core ECPF logic
- Implemented in `src/ecpf.py` as `ECPFMetaLearner`.
- Uses ECPF-style model pool management:
  - dual-model competition (`current` vs `new`),
  - reuse of best historical model on warning buffer,
  - similarity-based merge,
  - fading mechanism,
  - hard pool-size cap.

### Prediction model used
- Default model set to **Hoeffding Tree** (`model_type="ht"`), from:
  - `src/models/hoeffding_tree.py`
  - wired in `src/model_adapter.py`.

### Detector for ECPF experiments (separate from teammate detectors)
- Implemented in `src/ecpf_detector.py`.
- Current version keeps **only `adwin_dual`**:
  - warning ADWIN uses `delta_w` (more sensitive),
  - drift ADWIN uses `delta` (stricter).

### Pipeline integration
- ECPF path is integrated in `src/pipeline.py`.
- Main ECPF signal modes:
  - `oracle_60`: warning at true drift `T`, drift handled after 60 samples,
  - `detector`: warning/drift from standalone `adwin_dual`.

### Data loading helpers
- Recurring stream loader in `src/pipeline.py`:
  - `load_recurring_stream_pair(...)`
- Supports matched files like:
  - `recurring_sud_sea100k_g00.csv`
  - `recurring_sud_sea100k_g00_drift_times.txt`

## 2) Key Config (Current Defaults)

In `src/config.py`:
- `use_ecpf=True`
- `model_type="ht"`
- `ecpf_max_pool_size=10`
- `ecpf_similarity_margin=0.95`
- `ecpf_fade_points=15`
- `ecpf_warning_length=60`
- detector parity params stored:
  - `detector_delta=0.05`
  - `detector_epsilon=0.01`
  - `detector_alpha=0.8`
  - `detector_delta_w=0.1`

Note: in detector mode we currently use ADWIN dual (mainly `delta` / `delta_w`).

## 3) How To Run

## 3.1 Single file run

```bash
python run_ecpf_recurring.py \
  --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
  --warm-start 200 \
  --signal-mode detector \
  --detector-type adwin_dual
```

Optional oracle baseline:

```bash
python run_ecpf_recurring.py \
  --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
  --warm-start 200 \
  --signal-mode oracle_60
```

## 3.2 Batch run `g00 ... g09`

```bash
python run_ecpf_recurring_batch.py \
  --signal-mode detector \
  --print-events
```

Optional shorter debug run:

```bash
python run_ecpf_recurring_batch.py \
  --signal-mode detector \
  --max-steps 5000 \
  --print-events
```

## 4) Output Files

### Single run
- `outputs/ecpf_events.csv`
  - per-drift event details.
- `outputs/ecpf_timeline.png`
  - rolling accuracy + pool-size timeline.

### Batch run
- `outputs/ecpf_batch_summary.csv`
  - one row per file (`g00..g09`), includes:
    - ground-truth drift count/times,
    - detected drift events,
    - final pool size,
    - prequential accuracy.
- `outputs/ecpf_batch_events.csv`
  - event-level logs across all files.

## 5) How To Interpret Console Event Lines

Example:

```text
[event] t=22759 src=ecpf_detector_adwin_dual buf=257 pool=3 acc(cur/best/new)=(0.887,0.988,0.953)
```

- `t`: drift handling timestamp.
- `src`: which detector path triggered this event.
- `buf`: warning-buffer length used by ECPF for this event.
- `pool`: alive snapshots after ECPF update.
- `acc(cur/best/new)` on warning buffer:
  - `cur`: current leader before switch,
  - `best`: best reusable model from pool,
  - `new`: freshly trained model on warning buffer.

## 6) Metric Notes

### Prequential accuracy
- Online **test-then-train** accuracy of the **actual served predictions**.
- At each step:
  1. predict,
  2. compare with truth (correct=1, wrong=0),
  3. update model.
- Final score is the mean of those 0/1 outcomes (post warm-start region).

### Warm start
- Initial samples used to fit a stable initial model before online loop.
- With `--warm-start 200`, first 200 samples are used for initialization.

## 7) Current Limitations / Next Steps

- Detector mode currently only keeps `adwin_dual`.
- Plot is functional but not final publication style.
- Good next improvements:
  - cleaner multi-panel visualization,
  - side-by-side oracle vs detector comparison in batch output,
  - detector parameter sweep script.

