# Episodic vs standard, the six models, input/output, and how the gap is computed

## 1. What is “episodic”?

**Episodic** here means: training and evaluation are done in **small random tasks** called **episodes**, instead of “take a batch of labeled examples and predict their class.”

**One episode:**
- You sample **N classes** (e.g. 3: sudden, gradual, incremental).
- For each class you take **K support examples** (e.g. 5) and **Q query examples** (e.g. 15).
- You build **one prototype per class** (e.g. mean of the support embeddings).
- You **classify each query** by “nearest prototype” (no linear classifier).
- The **loss** is computed only on the query predictions.

**Episodic training** = every batch is a **new** random episode (different support/query sets). So the model never sees a fixed “train on these 210 samples”; it sees “this time the 3 classes are these streams, support is these 15, query is these 45.” The goal is to learn an embedding where “same class → close, different class → far” so that nearest-prototype works on any episode.

**Non-episodic (standard)** = normal supervised learning: batches of (input, label), one shared classifier (e.g. linear head), loss = cross-entropy on that batch. No support/query, no prototypes.

So **“episodic”** = **episode-based, few-shot style**: support set → prototypes → classify queries by nearest prototype.

---

## 2. Comparison of the six models

All models get the **same input**: one **14-d gap vector** per stream (see section 4). They differ in **architecture** and **how they are trained / how they predict**.

| Model | Encoder | How it predicts | Training |
|-------|--------|-------------------|----------|
| **baseline_rf** | None | Random Forest on the 14-d vector | Fit once on train set (no epochs). |
| **baseline_mlp** | None | sklearn MLP (14 → 64 → 32 → 3) on the 14-d vector | Fit once on train set (backprop). |
| **standard_mlp** | MLP (14→64→64) | Linear(64→3) on encoder output | Standard: mini-batch CE. |
| **standard_fan** | FAN (3L, 4H, d=64) | Linear(64→3) on encoder output | Standard: mini-batch CE. |
| **standard_fan_light** | FAN light (1L, 2H, d=32) | Linear(32→3) on encoder output | Standard: mini-batch CE. |
| **episodic_fan** | FAN (3L, 4H, d=64) | Nearest prototype (no head) | Episodic: N-way K-shot episodes, CE on query. |
| **episodic_fan_light** | FAN light (1L, 2H, d=32) | Nearest prototype (no head) | Episodic: N-way K-shot episodes, CE on query. |

**Summary:**
- **Baselines:** No learned encoder; direct classifier (RF or MLP) on the 14-d gap. Not episodic.
- **Standard_*:** Encoder + **linear head**. Training = standard mini-batch CE. **Not episodic.**
- **Episodic_*:** Encoder only; **no linear head**. Prediction = nearest prototype in embedding space. Training = **episodic** (episode-based, prototype + CE on query).

(So there are **seven** entries in the comparison script; the “six models” in the title can mean “six *neural* setups” or you can count baseline_rf + baseline_mlp as two and the five neural as five → “six” if you group one baseline. The table above lists all seven.)

---

## 3. Input and output of the model

**Input (what the model sees at prediction time):**
- **Shape:** `(batch_size, 14)` or `(batch_size, 14, 1)`.
- **Meaning:** Each row is **one 14-d gap vector** for one stream (the “error features G” in your paper). So **one stream → one 14-d vector**.
- **Where it comes from:** For each stream you have an error sequence and an alert time; you compute the **gap sequence** (section 4) and optionally standardize; that vector is the input.

**Output (what the model returns):**
- **Standard models (encoder + linear head):**  
  **Logits** of shape `(batch_size, 3)` → class with **argmax** (0 = sudden, 1 = gradual, 2 = incremental).
- **Episodic models (ProtoNet):**  
  For each **episode** you pass a **support set** (N×K examples) and **query set** (N×Q examples). The model returns **logits** of shape `(N*Q, N)` (scores for each query over the N classes). Prediction = **argmax** over those N scores (nearest prototype = highest score).

So in both cases the “output” you care about is **class indices 0, 1, or 2**; the only difference is that episodic models get there via prototypes (no linear layer), and they need a support set to form those prototypes for each episode.

---

## 4. How the gap is calculated in your code

The gap is computed in **`src/feature_extraction.py`**, in **`extract_gap_sequence`**. Logic:

**Step 1 – Window around the alert**
- `errors`: 1D array of 0/1 (error at each time step) for one stream.
- `t_alert`: alert time (e.g. near the true drift).
- You take a **window** from `t_alert - pre_window` to `t_alert + post_window` (defaults 150 and 150 → length 300 if in range).
- So `window_errors = errors[start:end]` is the error sequence in that window.

**Step 2 – Subwindows and mean error**
- That window is split into **`n_subwindows`** (default 15) equal-sized segments.
- For each segment you compute the **mean error** (a number between 0 and 1).
- So you get **15 numbers**: `m_1, m_2, …, m_15`.

**Step 3 – Gaps**
- **Gaps** = differences between consecutive means:  
  `gap_j = m_{j+1} - m_j` for j = 1..14.  
- So **14 numbers** → that’s your **14-d gap vector**.

**In code** (from `feature_extraction.py`):

```python
# Window
start = max(0, t_alert - pre_window)
end = min(n, t_alert + post_window)
window_errors = errors[start:end]

# Split into n_subwindows (e.g. 15), get mean per subwindow
sub_len = max(1, len(window_errors) // n_subwindows)
means = []
for j in range(n_subwindows):
    beg = j * sub_len
    fin = min((j + 1) * sub_len, len(window_errors))
    means.append(np.mean(window_errors[beg:fin]))
means = np.array(means)

# Gaps = diff(means) → 14 values
gaps = np.diff(means)
return gaps
```

So: **one stream** → one error sequence + one `t_alert` → one window → 15 subwindow means → **14 gaps** = one 14-d input vector for the model. That vector is what you call “error features G” and is the only input to every model in the comparison.
