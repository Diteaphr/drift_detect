# Concept Drift Detection and Adaptation Pipeline

Pipeline for detecting **sudden**, **gradual**, and **recurring** concept drift in a data stream, with model pool and incremental adaptation (retrain/fine-tune).

## Workflow (high level)

1. **Data stream** → Preprocessing (prediction errors from y, ŷ)
2. **Sudden drift detector** → if drift: go to Recurring detector
3. **Gradual drift detector** (if no sudden) → if drift: go to Recurring detector
4. **Recurring drift detector** (inputs: prediction errors, drift timestamp, concept memory) → Recurring? Yes → **Recurring drift**; No → **Drift type classifier**
5. **Drift type classifier** → Sudden vs Gradual
6. **Model pool** + **Prediction model** → Incremental adaptation (retrain linear / fine-tune nonlinear) when batch size is reached or on drift
7. **Offline evaluation** for detectors and classifier (in `tests/`)

## Project layout

```
drift_detect/
├── main.py                 # Run demo (imports from src + tests)
├── requirements.txt
├── detectors/              # All drift detectors (sudden, gradual, recurring)
│   ├── __init__.py
│   ├── sudden.py
│   ├── gradual.py
│   └── recurring_drift_detector.py  # ConceptMemory, detect_recurring_drift
├── src/                    # Core pipeline and components
│   ├── __init__.py
│   ├── config.py           # DriftType, PipelineConfig
│   ├── preprocessing.py    # StreamBuffer, compute_prediction_errors
│   ├── drift_type_classifier.py     # classify_drift_type (sudden vs gradual)
│   ├── model_pool.py       # ModelPool (save/retrieve)
│   ├── prediction_model.py # PredictionModel (linear/nonlinear, retrain/fine-tune)
│   └── pipeline.py         # ConceptDriftPipeline, run_pipeline_demo
└── tests/                  # Evaluation and examples
    ├── __init__.py
    ├── evaluation.py       # evaluate_detectors, evaluate_drift_type_classifier, prediction_metrics
    └── example_usage.py    # Minimal recurring-detector usage
```

## Setup

1. Clone the repository and go to the project directory:
   ```bash
   git clone https://github.com/Diteaphr/drift_detect.git
   cd drift_detect
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run full pipeline

```bash
python main.py
```

This runs a synthetic stream with drifts at t=200, 400, 600, runs all detectors and the classifier, then prints detector and classifier evaluation plus prediction MAE.

To **only record alert timestamps** for several CSV streams (no ground truth), from the project root: `python scripts/collect_alert_times.py --csv path/to/data.csv --out alerts.json` (see script docstring for `--glob` and optional `--config-json`).

## Use recurring detector only

See `tests/example_usage.py`: pass prediction errors, drift alert timestamp, and a `ConceptMemory` instance; get back `recurring: bool`. Run from project root: `python -m tests.example_usage` or `python tests/example_usage.py` (with project root on `PYTHONPATH`).

## Use pipeline on your own stream

```python
from src.config import PipelineConfig
from src.pipeline import ConceptDriftPipeline
import numpy as np

config = PipelineConfig(update_batch_size=50, recurrence_threshold=0.5)
pipeline = ConceptDriftPipeline(config=config)
pipeline.warm_start(X[:100], y[:100])  # initial fit

for i in range(100, len(X)):
    y_pred, detections, drift_occurred = pipeline.step(X[i], y[i], index=i)
    for d in detections:
        print(f"Drift at {d.timestamp}: {d.drift_type.value}")
```

## Recurring drift detector (your component)

- **Inputs:** Streamline prediction error, drift alert timestamp, Concept Memory  
- **Output:** Recurring drift or not (bool)  
- Implemented in `detectors/recurring_drift_detector.py` and wired in `src/pipeline.py` after sudden/gradual detectors.
