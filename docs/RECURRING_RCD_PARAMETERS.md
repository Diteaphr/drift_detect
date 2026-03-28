# Recurring detector: parameters vs Gonçalves Jr. & Barros (2013) RCD

## Significance **α** (default **0.01**)

- In code: `PipelineConfig.recurring_stat_alpha` / `ConceptMemory.significance`.
- **Rule:** declare **recurring** if the permutation **p-value > α** for **any** stored reference window (fail to reject “same distribution”).
- **Paper:** they denote this as **s**; best configuration in their grid used **s = 0.01** (also tried 0.05). The repo default is now **0.01** to match that best setting.

## What matches the paper vs what is adapted

| Item | Paper (RCD) | This implementation |
|------|-------------|---------------------|
| **α (s)** | Tuned; best **0.01** | Default **0.01** ✓ |
| **k (kNN)** | Odd values; best **k = 5** | Default **5** ✓ |
| **Buffer size (b)** | Up to **400** instances per context | `recurring_max_buffer_size = 400` ✓ |
| **Drift trigger** | DDM / EDDM on classifier | Your pipeline’s sudden/gradual detectors → then recurring check |
| **Statistical test** | Multivariate **kNN mixing** (R package MTSKNN / Schilling–Henze style) | **Same idea:** kNN graph on pooled standardized data + **permutation p-value** for label mixing (not the R package; implemented in Python + scikit-learn) |
| **Test frequency (t)** | How often tests run in their **evaluation** protocol | We run the test **only when a drift alert fires**, not every t steps |
| **Multiple comparisons** | Compare new buffer to **all** stored contexts | Same: recurring if **any** match passes **p > α** (no Bonferroni unless you add it) |
| **Data in the test** | **Raw instance** buffers (FIFO, cap **b**) | **Pipeline:** after sudden/gradual alarm, **FIFO** of up to **400** samples **from the alert step onward** (`recurring_fifo_min_samples` default **100** before test). **Eval script:** same idea — `prediction_errors[t : t+L]` with `L ≤ 400`. **Fallback:** legacy slice around alert if `recurring_use_post_alert_fifo=False`. |

So: **α, k, buffer cap** follow the paper’s **reported best** settings; the **test statistic** is the same **family** (kNN-based two-sample mixing) but **not** byte-for-byte identical to MTSKNN; **when** the test runs is driven by **your** drift alerts, not DDM inside this module.

## What data we use for evaluation

Script: `python -m data_generation.evaluate_recurring`

- **Generator:** `data_generation.generators.generate_recurring_stream` — synthetic stream with **recurring concepts** (repeated concept IDs across drifts).
- **Ground truth:** `ground_truth_recurring.npy` — per drift, **True** if that drift’s concept was **seen before** in the sequence.
- **Inputs to the detector:** saved `prediction_errors.npy`, `drift_alert_timestamps.npy`, and (after regenerate) optional `stream_X.npy` for multivariate windows.

Default output folder: `data_generation/output_recurring/`.

## How to know if it’s performing well

1. **Run the eval script** (from repo root):

   ```bash
   python -m data_generation.evaluate_recurring
   ```

2. It prints **accuracy, precision, recall, F1, specificity** with **recurring = positive class**, plus a **confusion matrix (TN, FP, FN, TP)** and the boolean **predictions** vs the stream order.

3. **Regenerate data with X** (delete or rename old `output_recurring` if you want fresh files) so `stream_X.npy` exists — then the script prints `Using raw X stream: True` and the test uses **feature windows** closer to the paper; with only errors it prints `False` and uses **1D error windows**.

4. For **your** real pipeline, log **recurring vs new** and compare to any available labels, or use **downstream metrics** (e.g. model accuracy after retrieval vs unnecessary resets).

**Note:** Stricter **α = 0.01** vs **0.05** makes “recurring” **harder** to accept (need **higher p**), which usually **reduces false recurring** and can **increase false new** — inspect precision/recall on your data.
