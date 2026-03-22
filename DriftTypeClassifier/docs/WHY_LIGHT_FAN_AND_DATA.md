# Why light FAN works better, why full FAN struggles, and how your data is generated

## 1. Why is the light version of FAN performing better?

In short: **the full FAN is too big and too hard to optimize for your current setup** (short sequences, small dataset). The light FAN is smaller and easier to train, so it actually learns.

**Full FAN (3 layers, 4 heads, d_model 64):**
- Many parameters (multiple Transformer layers, large feedforward blocks).
- For a **14-dimensional** input (the gap sequence) and only **~200–250 training samples**, the model can:
  - **Overfit** to noise instead of learning a stable pattern.
  - **Fail to learn at all** because the optimization landscape is harder (more parameters, more local minima, gradients can be small or unstable).
- With standard training, the loss often stayed near ln(3) (~1.1), meaning the model was outputting almost uniform predictions and not moving.

**Light FAN (1 layer, 2 heads, d_model 32):**
- Fewer parameters, so:
  - The same amount of data can pin down the weights.
  - Optimization is simpler (fewer layers, smaller matrices), so gradient updates actually change the embeddings in a useful way.
- **No dropout** and **Pre-LN (norm_first)** also help: less randomness and more stable gradients so the encoder can improve.
- So the light FAN learns a useful 32-d representation, and the linear head (or prototypes) can separate the three drift types.

So “light performs better” here is mainly: **right-sized model and training setup for your data**, not that attention is bad. With more data or different benchmarks, the full FAN might do better.

---

## 2. Why is the full FAN performing so bad when the paper says it’s the best?

The paper likely used a **different setting** from yours. “Best model” in a paper usually means best **in their experiments**: different data, scale, and hyperparameters. So full FAN can be best there and weak in your setup.

Possible differences:

**Data scale**
- Papers often use **larger** datasets (many more streams or samples). With more data, a bigger model can learn without overfitting and with a more stable optimization.
- You have **300 streams** and a **14-d gap vector** per stream. That’s small for a 3-layer Transformer.

**Benchmarks**
- The paper may use **standard benchmarks** (e.g. SEA, or other concept-drift datasets) with:
  - Longer or different input sequences.
  - Different preprocessing and features.
  - Different train/val/test splits and evaluation protocols.
- Your pipeline uses **custom synthetic streams** (see below). Different data distribution and difficulty.

**Hyperparameters**
- The paper likely tuned **learning rate, dropout, depth, width** for their data. Their “best” FAN may use different lr, fewer layers, or different regularization than your default full FAN.
- Your full FAN (default config) may simply be a bad fit for your data size and feature length.

**Task and protocol**
- If the paper uses **episodic (ProtoNet)** evaluation, they may have trained with more episodes, different N-way K-shot, or different seeds, making the full FAN train better in their setup.

So: **full FAN is not “bad” in general**; it’s a bad fit for **your current data size and feature length**. The paper’s “best” claim applies to their setting. In your setting, the light FAN is a better fit.

---

## 3. How are you generating data now? (No SEA or other known benchmarks)

You are **not** using SEA, or other standard drift benchmarks (e.g. from River or the literature). You are using **custom synthetic streams** defined in `src/generators.py`. Here’s the flow in simple terms.

**Step 1: Streams (one per “scenario”)**
- You generate **300 streams** (100 sudden, 100 gradual, 100 incremental).
- Each stream is a **time series** of length 2000. At each time step you have:
  - **X_t**: a feature vector (e.g. 10 dimensions),
  - **y_t**: a class label (e.g. 0 or 1).
- The **underlying concept** (how X and y relate) changes **once** in the stream at a drift time `t_drift` (random in [0.4, 0.6] × length). The **way** it changes defines the drift type:
  - **Sudden:** Before `t_drift` you use one set of class means; after `t_drift` you switch to a different set. Abrupt change.
  - **Gradual:** In a window around `t_drift`, you mix “old” and “new” concept: at each time in the window you sample from the old concept with probability (1 − α) and from the new with probability α, with α going from 0 to 1 across the window.
  - **Incremental:** In a long window around `t_drift`, the **means** of the classes move smoothly from the pre-drift to the post-drift values (linear interpolation in parameter space). So the concept changes in many small steps.

So the **raw data** is: **synthetic, rotating-hyperplane style** streams (different class means before/after drift), with three **transition types** (sudden, gradual, incremental). No SEA, no real-world benchmark; it’s your own controlled setup.

**Step 2: Simulated online classifier and errors**
- For each stream, an **online classifier** (e.g. SGD) is run step by step and produces **errors** (right/wrong) over time.
- So from each stream you get an **error sequence** (0/1 over time), which reflects how the drift type affects classifier performance.

**Step 3: Alert time and gap features**
- You define an **alert time** (e.g. near the true drift, with small noise).
- Around that time you extract a **gap sequence**: a window of the error sequence is split into subwindows, you take the mean error per subwindow, then take **differences** between consecutive means → **14 numbers** (the “gap” or “G” features).

**Step 4: One sample per stream**
- Each stream gives **one** 14-d gap vector and **one** label: sudden (0), gradual (1), or incremental (2).
- So you end up with **300 labeled samples** in a 14-d feature space, coming from your **custom synthetic** streams, not from SEA or other standard benchmarks.

**Summary**
- **Data source:** Your own generators (`generate_sudden_streams`, `generate_gradual_streams`, `generate_incremental_streams`).
- **Style:** Synthetic streams with a single drift per stream; concept change is “different class means before/after” with three transition types.
- **Not used:** SEA, or other known benchmark generators (unless you add them later). Your results are therefore for **this custom synthetic setup**, not directly comparable to papers that report on SEA or other benchmarks unless you align data and protocol.
