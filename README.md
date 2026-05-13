# Concept Drift Detection and Adaptation Pipeline

Pipeline for detecting **sudden**, **gradual**, and **recurring** concept drift in a data stream, with model pool and incremental adaptation (retrain/fine-tune).

## Workflow (high level)

1. **Data stream** → Preprocessing (prediction errors from y, ŷ)
2. **Meta-detector** (voting ensemble) → if drift: trigger ECPF or RCD recurring check
3. **Recurring drift detector** (inputs: prediction errors, drift timestamp, concept memory) → Recurring? Yes → restore model from pool; No → **Drift type classifier**
4. **Drift type classifier** → Sudden vs Gradual vs Incremental
5. **Model pool** + **Prediction model** → Incremental adaptation on drift
6. **Offline evaluation** → Correct Detection score, precision/recall/F1, prediction MAE

## Setup

1. Clone and enter the project directory:
   ```bash
   git clone https://github.com/Diteaphr/drift_detect.git
   cd drift_detect
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run full pipeline

```bash
python main.py [tsv|dwm|statistical|dwme]
```

Loads `data/sudden_drift/recurring_sudden_sea100k_g03.csv`, runs the full pipeline, then prints Correct Detection score, precision/recall/F1, and prediction MAE.

**Optional: save a timeline plot after evaluation:**

```bash
python main.py dwm --plot                          # saves to outputs/recurring_sudden_sea100k_g03_dwm_cd.png
python main.py dwm --plot --plot-path my_plot.png  # custom path
```

The plot shows rolling accuracy, perturbation intervals (drift interval + 1000 samples), and each alert coloured green (TP) or red (FP).

To **only record alert timestamps**, from the project root:
```bash
python scripts/collect_alert_times.py --csv path/to/data.csv --out alerts.json
```
Optional flags: `--meta tsv|dwm|statistical`, `--config-json`, `--ecpf`.

## Run ECPF on a recurring-drift CSV

```bash
python run_ecpf_recurring.py \
  --csv data/recurring_drift/recurring_sud_sea100k_g00.csv \
  --signal-mode oracle_60
```

Prints a Correct Detection score at the end and saves an event log CSV and timeline PNG to `outputs/`.

**Batch across g00–g09:**

```bash
python run_ecpf_recurring_batch.py \
  --signal-mode oracle_60 \
  --data-dir data/recurring_drift
```

Each row reports `cd(TP=…, FP=…, N=…, score=…%)`. The final summary prints the mean Correct Detection score across all files.

## Correct Detection score

Score formula (Bifet et al.):

```
score = max(0, (TP - FP) / N) × 100
```

- **N** — number of ground-truth drift intervals in the stream
- **TP** — each interval counts at most once, regardless of how many alerts fall inside it
- **FP** — each alert outside every interval counts as one false positive
- **Perturbation interval** — ground-truth drift interval extended by +1000 samples on the right (e.g. `[250, 2000]` → `[250, 3000]`)

Implementation:

| File | Role |
|------|------|
| `src/metrics/correct_detection.py` | `compute_correct_detection`, `build_perturbation_intervals` — pure calculation |
| `tests/evaluation.py` | `correct_detection_from_detections` — wraps `DriftDetection` objects |
| `main.py` | Calls evaluation, optionally plots results |
| `run_ecpf_recurring.py` | Prints score after each single-file run |
| `run_ecpf_recurring_batch.py` | Adds `cd_tp/fp/n/score_pct` columns to summary CSV |

## Use pipeline on your own stream

```python
from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline
import numpy as np

config = PipelineConfig(update_batch_size=50, recurrence_threshold=0.5)
pipeline = ConceptDriftPipeline(config=config)
pipeline.warm_start(X[:100], y[:100])

for i in range(100, len(X)):
    y_pred, detections, drift_occurred = pipeline.step(X[i], y[i], index=i)
    for d in detections:
        print(f"Drift at {d.timestamp}: {d.drift_type.value}")
```

## Use recurring detector only

See `tests/example_usage.py`: pass prediction errors, drift alert timestamp, and a `ConceptMemory` instance; get back `recurring: bool`.

```bash
python -m tests.example_usage
```
