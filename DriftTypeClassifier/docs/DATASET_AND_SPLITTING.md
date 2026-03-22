# The dataset you're using and how it's split

## 1. What the dataset is

**One sample = one stream.**  
You don't have one big table of many time steps. You have **300 rows** (or whatever `n_streams` is): each row is **one stream**, turned into **one feature vector** and **one label**.

**Contents:**
- **X:** shape `(300, 14)`. Row `i` = the **14-d gap vector** for stream `i` (after standardization).
- **y:** shape `(300,)`. Label per stream: **0** = sudden, **1** = gradual, **2** = incremental.
- **stream_ids:** shape `(300,)`. `stream_ids[i]` = id of the stream that produced row `i` (0 to 299).

So the "dataset" is: **300 samples**, each a 14-d vector + one of three drift types. No timestamps are stored in the matrix; the 14 numbers are already a summary of one stream (the gap around the alert time).

---

## 2. How the dataset is built (step by step)

**Step 1 – Generate streams**  
`generate_all_streams(...)` creates **300 streams** (default): 100 sudden, 100 gradual, 100 incremental. Each stream is a time series of length 2000 (features + labels over time) with **one** drift event. These are **synthetic** (your own generators), not SEA or another benchmark.

**Step 2 – Error sequence per stream**  
For each stream, an **online classifier** (e.g. SGD) is run step by step along the stream. That gives an **error sequence**: at each time step, 0 (correct) or 1 (wrong). So each stream → one error sequence of length 2000.

**Step 3 – Alert time**  
For each stream you define an **alert time**:  
`t_alert = t_drift + noise`  
(with `noise` in `[-alert_noise_radius, alert_noise_radius]`). So it's near the true drift, with small random shift.

**Step 4 – Gap features**  
For each stream you take the error sequence **around** `t_alert` (window `[t_alert - 150, t_alert + 150]`), split that window into 15 subwindows, take the **mean error** in each subwindow, then **gaps = differences** between consecutive means → **14 numbers**. That 14-d vector is the **input** for that stream. (See `feature_extraction.extract_gap_sequence`.)

**Step 5 – One row per stream**  
So each stream gives **one** 14-d vector and **one** label (its drift type). You stack these into **X** (300×14) and **y** (300,).

**Step 6 – Standardization**  
You compute **mean** and **std** of X on the **train** (or train+val) set only, then do `(X - mean) / std` for **all** rows. So train/val/test all use the same scaling (from train). `X_mean` and `X_std` are saved in the `.npz` so you can reapply the same scaling later.

**Saved file:** `data/dataset.npz` contains `X`, `y`, `stream_ids`, split indices (see below), and optionally `X_mean`, `X_std`.

---

## 3. Data splitting (by stream, not by time step)

Splits are **by stream_id**: a stream never appears in two of train/val/test. So you're splitting **streams** (and hence their single 14-d sample), not time steps.

**Single split (n_folds ≤ 1, e.g. default when n_folds=0):**

- All **stream_ids** (0…299) are **shuffled** once (with a fixed seed).
- You split the **list of stream_ids** into three chunks by ratio:
  - **train_ratio** (e.g. 0.7) → first 70% of stream_ids = train streams.
  - **val_ratio** (e.g. 0.15) → next 15% = val streams.
  - **test_ratio** (e.g. 0.15) → last 15% = test streams.
- Then you turn that into **sample indices**:  
  `train_idx` = indices of rows in X/y whose `stream_id` is in the train set of stream_ids (same for val, test).

So with 300 streams and 0.7 / 0.15 / 0.15 you get roughly **210 train**, **45 val**, **45 test** **samples** (one per stream). Each of these is a 14-d vector + label.

**K-fold (n_folds > 1, e.g. 5):**

- **Test set is fixed first:**  
  Same as above: shuffle stream_ids, take last 15% (for example) as **test stream_ids**. Those streams (and their rows in X/y) are the **test set** for everything that follows. They are **never** used for training or validation.
- **The rest** (e.g. 85% of streams) are the **train+val pool**. You split **this pool** into **K folds** (e.g. 5) **by stream_id**:
  - Fold 1: fold 1’s chunk of stream_ids = **val** for this fold; the other 4 chunks = **train**.
  - Fold 2: fold 2’s chunk = **val**; the rest = **train**.
  - … same for folds 3, 4, 5.
- So you get **K pairs** `(train_idx, val_idx)`. In each fold, **train** and **val** are different streams; **test** is the same 15% of streams for all folds.

So:
- **Single split:** one train/val/test split by stream_id (e.g. 70% / 15% / 15% of streams).
- **K-fold:** one fixed test set (e.g. 15% of streams); the other 85% are split into K folds so each fold has a **different** validation set (and the rest as training). No stream appears in both train and val in the same fold, and no stream in test is ever in train or val.

---

## 4. Summary

- **Dataset:** 300 samples (one per stream). Each sample = **14-d gap vector** (standardized) + **label** 0/1/2. Built from synthetic streams → online classifier errors → gap around alert time.
- **Splitting:** Always **by stream_id** (one stream = one sample; that sample is only in train, or only in val, or only in test).  
  - **Single split:** 70% / 15% / 15% of streams → train / val / test.  
  - **K-fold:** 15% of streams = fixed test; remaining 85% split into K folds so each fold has different val (and same test).  
- **What you train/evaluate on:** The **same** X and y; only the **indices** (train_idx, val_idx, test_idx or per-fold indices) decide which 14-d rows are train/val/test.
