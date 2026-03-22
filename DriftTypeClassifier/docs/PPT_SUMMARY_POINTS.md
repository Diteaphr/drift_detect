# Summary points for PPT (copy-paste)

## Dataset
- **300 synthetic streams** (100 sudden, 100 gradual, 100 incremental); one drift per stream
- **One sample per stream**: 14-d **gap vector** (from error sequence around alert time) + label (0/1/2)
- **Gap**: window around alert → 15 subwindows → mean error per subwindow → **gaps = diff(means)** → 14 numbers
- **Split by stream_id**: train / val / test (e.g. 70% / 15% / 15%); optional **5-fold** on train+val with **fixed test set**
- **Not SEA or standard benchmarks**; custom synthetic (rotating-hyperplane style)

## Models compared
- **Baselines:** Random Forest, sklearn MLP — direct on 14-d gap (no encoder)
- **Standard (encoder + linear head):** MLP encoder, FAN encoder, or **FAN light** encoder → linear layer → 3 classes; trained with **mini-batch cross-entropy**
- **Episodic (ProtoNet):** Same encoder → **no linear head** → **prototype centers** (mean of support embeddings per class) → **nearest-prototype classification**; trained with **episodic N-way K-shot**

## Key terms
- **Encoder:** Maps 14-d gap → fixed-length embedding (e.g. 32-d or 64-d)
- **FAN:** Full Attention Network — Transformer encoder (self-attention + FFN) for the 14-d sequence
- **FAN light:** 1 layer, 2 heads, d=32; better on small data than full FAN (3 layers, 4 heads, d=64)
- **Episodic:** Each batch = random episode (support + query); learn embedding where **same class → close, different class → far**; classify by **nearest prototype**

## Pipeline (paper-style flow)
1. **Error features G** = 14-d gap (from online classifier errors around alert)
2. **Embedding network** = FAN or FAN light (or MLP)
3. **Prototype centers** = mean of support-set embeddings per class (episodic only)
4. **Classification** = nearest prototype (episodic) or linear head (standard)

## Results (typical)
- **FAN light + linear (standard):** ~0.8 val F1, ~0.68–0.78 test F1
- **FAN light + ProtoNet (episodic):** ~0.85 val F1, ~0.64 test F1
- **Full FAN** (standard or episodic): weak on this data (~0.33) without more data or tuning
