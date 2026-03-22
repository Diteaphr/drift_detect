# DriftTypeClassifier

Concept drift **type** classification (sudden / gradual / incremental) using a **FAN-based prototypical network**, with synthetic data generation, episodic few-shot training, and inference on drift alert timestamps.

## Goal

- **Input:** Drift alert timestamps (assumed already available).
- **Output:** For each alert, a drift type in `{sudden, gradual, incremental}`.
- **Pipeline:** Synthetic streams → online classifier → error sequence → gap features around each alert → FAN encoder → prototypical classification.

## Design choices

- **Synthetic generators:** Separate generators per type. **Sudden:** Abrupt change of class-conditional means at `t_drift`. **Gradual:** Mixture of old/new concept over a transition window (sigmoid-like blend). **Incremental:** Linear interpolation of concept parameters over a long window (smooth, many small steps). So gradual = bounded transition window; incremental = longer, smoother parameter drift.
- **Error-gap features:** Following Type-LDD/Type-DD: subwindow mean errors around the alert, then **gaps** (differences between consecutive subwindow means). Sudden drift → one large gap; gradual → spread of smaller gaps; incremental → many tiny gaps. Default representation is this gap sequence only; optional extra scalars (mean before/after, max jump, slopes, etc.) can be concatenated.
- **FAN encoder:** Full attention (Transformer encoder) on the 1D gap sequence: linear projection → positional encoding → multi-head self-attention + FFN layers → global mean pooling → embedding. Gives a single vector per alert for prototype comparison.
- **Prototypical training:** Per episode, sample N_way=3 classes, K_shot support and Q_query query per class; prototypes = mean support embedding per class; query loss = cross-entropy on negative distances to prototypes. Validation by episodic macro-F1; early stopping and best checkpoint by val macro-F1.
- **Alert noise:** Training can use `t_alert = t_drift + epsilon` with `epsilon` in `[-alert_noise_radius, alert_noise_radius]` to simulate approximate alerts and improve robustness.

## Setup

```bash
cd DriftTypeClassifier
pip install -r requirements.txt
```

## File structure

```
DriftTypeClassifier/
  configs/
    default.yaml
  data/                 # generated after first run
  checkpoints/
  src/
    generators.py       # sudden / gradual / incremental stream generators
    stream_simulator.py  # online classifier → error sequence
    feature_extraction.py
    dataset_builder.py
    episodic_sampler.py
    models/
      fan_encoder.py
      protonet.py
    train.py
    evaluate.py
    inference.py
    baseline.py
    utils.py
    plotting.py
  run_compare_baseline_vs_protonet.py
  README.md
  requirements.txt
```

## Run instructions

**1. Generate data and train (default config):**

```bash
python -m src.train
```

This builds the dataset (if missing) under `data/`, then runs episodic training and saves the best model to `checkpoints/best.pt`.

**2. Evaluate:**

```bash
python -m src.evaluate --checkpoint checkpoints/best.pt --data_dir data
```

**3. Inference on new stream and alerts:**

From Python:

```python
from src.inference import predict_drift_types_for_alerts
from src.models import build_protonet
import torch
# Load model, config, and a support set (e.g. from training data)
# support_X, support_y = ...
pred_labels, probs, features = predict_drift_types_for_alerts(
    X, y, alert_timestamps, model, support_X, support_y, config,
)
```

**4. Compare baseline vs ProtoNet:**

```bash
python run_compare_baseline_vs_protonet.py
```

**5. Ablations**

- **Exact vs noisy alerts:** In `configs/default.yaml`, set `alert_noise_radius: 0` for exact, or e.g. `20` for noisy.
- **Gap-only vs gap+extra:** Set `use_extra_features: false` or `true` in config; rebuild data and retrain.
- **FAN vs MLP encoder:** The codebase uses FAN by default; the baseline script compares against an MLP on flattened features (see `baseline.py`).

## Default experiment

- 300 streams (100 per class), length 2000, 10 features, one drift per stream near the middle.
- Alert noise radius 20; context window 150 before/after; 15 subwindows (gap length 14).
- 3-way episodic training: 5-shot, 15 query, 100 episodes per epoch; early stopping on validation macro-F1.

## Dependencies

- Python 3.10+
- PyTorch, numpy, scikit-learn, matplotlib, PyYAML
