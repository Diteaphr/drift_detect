# Concept Drift Detection and Adaptation Pipeline

Pipeline for detecting **sudden**, **gradual**, and **recurring** concept drift in a data stream, with model pool and incremental adaptation (retrain/fine-tune).

## Workflow (high level)

1. **Data stream** → Preprocessing (prediction errors from y, ŷ)
2. **Sudden drift detector** → if drift: go to Recurring detector
3. **Gradual drift detector** (if no sudden) → if drift: go to Recurring detector
4. **Recurring drift detector** (inputs: prediction errors, drift timestamp, concept memory) → Recurring? Yes → **Recurring drift**; No → **Drift type classifier**
5. **Drift type classifier** → Sudden vs Gradual
6. **Model pool** + **Prediction model** → Incremental adaptation (retrain linear / fine-tune nonlinear) when batch size is reached or on drift
7. **Offline evaluation** for detectors and classifier

## Project layout

```
drift/
├── config.py              # DriftType, PipelineConfig
├── preprocessing.py       # StreamBuffer, compute_prediction_errors
├── detectors/
│   ├── sudden.py          # SuddenDriftDetector
│   └── gradual.py         # GradualDriftDetector (Page-Hinkley style)
├── recurring_drift_detector.py  # ConceptMemory, detect_recurring_drift
├── drift_type_classifier.py     # classify_drift_type (sudden vs gradual)
├── model_pool.py          # ModelPool (save/retrieve)
├── prediction_model.py    # PredictionModel (linear/nonlinear, retrain/fine-tune)
├── pipeline.py            # ConceptDriftPipeline, run_pipeline_demo
├── evaluation.py          # evaluate_detectors, evaluate_drift_type_classifier
├── main.py                # Run demo + evaluation
├── example_usage.py       # Minimal recurring-detector usage
└── requirements.txt
```

## Setup

```bash
cd drift
pip install -r requirements.txt
```

## Run full pipeline

```bash
python main.py
```

This runs a synthetic stream with drifts at t=200, 400, 600, runs all detectors and the classifier, then prints detector and classifier evaluation plus prediction MAE.

## Use recurring detector only

See `example_usage.py`: pass prediction errors, drift alert timestamp, and a `ConceptMemory` instance; get back `recurring: bool`.

## Use pipeline on your own stream

```python
from config import PipelineConfig
from pipeline import ConceptDriftPipeline
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
- Implemented in `recurring_drift_detector.py` and wired in `pipeline.py` after sudden/gradual detectors.
