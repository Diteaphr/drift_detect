# concept_drift_visualization.py
# 使用 River 套件展示 concept drift（二元分類），
# 僅透過資料分布驗證 drift，不使用任何機器學習模型。
# 兩條資料流：Sudden / Gradual；每條 5~10 個 drift，分段與 drift 時間隨機。
# 各段 SEA variant 鏈式銜接：第 i+1 段從第 i 段漂移後的概念接續（例如 1→2 再接 2→0）。

from collections import deque
import os
import secrets
import numpy as np
import matplotlib.pyplot as plt
from river.datasets import synth


# =========================
# 設定
# =========================
N_SAMPLES = 100_000
WINDOW = 500
# 僅作為「手動指定」時的預設；主程式每次執行預設改用隨機種子（見 _get_run_seed）
SEED = 42

# Medium-tier defaults (see drift_common/profiles.py); generators pass scaled width per tier.
SUDDEN_WIDTH = 80
GRADUAL_WIDTH = 10_000

# 分段僅需滿足「每段至少能放一個 drift 點」（不為 gradual 預留完整過渡長度）
MIN_SEGMENT_LEN = 2

# 每次實驗 drift 發生次數（段數 = drift 點數）之隨機範圍 [N_DRIFTS_MIN, N_DRIFTS_MAX]
N_DRIFTS_MIN = 5
N_DRIFTS_MAX = 10

# 僅輸出「標籤機率分布」圖檔的目錄（與腳本同層）
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drift_plots")


def _get_run_seed() -> int:
    """
    每次執行產生不同種子，使 drift 時間（分段、各段內 drift 位置）隨機。
    若設定環境變數 DRIFT_SEED=整數，則固定該種子以便重現同一組 drift 時間。
    """
    env = os.environ.get("DRIFT_SEED")
    if env is not None and env.strip() != "":
        return int(env.strip())
    # 與 numpy.random.Generator 相容的隨機整數種子
    return secrets.randbelow(2**32)


# =========================
# 隨機 drift 計畫（分段長度、每段 variant、每段內 drift 位置）
# =========================


def _random_n_drifts(rng: np.random.Generator) -> int:
    """每條資料流隨機選擇 drift 次數（含 N_DRIFTS_MAX，即 5～10 次）。"""
    return int(rng.integers(N_DRIFTS_MIN, N_DRIFTS_MAX + 1))


def _random_partition_multinomial(
    rng: np.random.Generator,
    n: int,
    k: int,
    min_len: int,
) -> list[int]:
    """將 n 分為 k 段正整數，每段至少 min_len，總和為 n。"""
    if n < k * min_len:
        raise ValueError(f"n={n} 太小，無法分成 {k} 段且每段至少 {min_len}")
    remaining = n - k * min_len
    extras = rng.multinomial(remaining, [1.0 / k] * k)
    return [min_len + int(x) for x in extras]


def _max_offset_for_width(width: int) -> int:
    """sigmoid 不溢位：River 使用 v=-4*(t-p)/w，需 4*dist/w < ~700。"""
    return max(1, int(174 * width))


def _random_local_drift_position(
    rng: np.random.Generator,
    seg_len: int,
    width_sudden: int,
) -> int:
    """
    在段內隨機選 drift 中心；與 River v=-4*(t-p)/w 對齊。
    長段且 width 較窄時，僅在段首 [1, margin+1] 內選點（避免 exp 溢位）。
    """
    if seg_len <= 2:
        return max(0, seg_len // 2)

    margin = _max_offset_for_width(width_sudden)
    hi = min(seg_len - 1, margin + 1)
    if hi < 1:
        return 1
    return int(rng.integers(1, hi + 1))


def _random_chained_variant_pairs(rng: np.random.Generator, n: int) -> list[tuple[int, int]]:
    """
    產生 n 段 (v_from, v_to)，使各 drift 段彼此銜接：
    第 1 段從隨機起始 variant 出發轉到 v_to；
    第 i+1 段的 v_from 必等於第 i 段的 v_to（例如 1→2 後，下一段必為 2→k）。
    每段的目標 v_to 在「與當前相異」的 variant 中隨機選取。
    """
    pairs: list[tuple[int, int]] = []
    current = int(rng.integers(0, 4))
    for _ in range(n):
        candidates = [j for j in range(4) if j != current]
        v_to = int(rng.choice(candidates))
        pairs.append((current, v_to))
        current = v_to
    return pairs


def build_drift_plan(
    n_samples: int,
    n_drifts: int,
    rng: np.random.Generator,
    width_ref: int = SUDDEN_WIDTH,
) -> dict:
    """
    產生單次實驗的 drift 計畫：分段長度、每段 (v_from, v_to)、每段內 drift 位置（全域索引）。
    variant 轉換為鏈式銜接：每段 drift_stream 的目標即下一段 stream 的起始概念。
    """
    lengths = _random_partition_multinomial(rng, n_samples, n_drifts, MIN_SEGMENT_LEN)
    local_positions: list[int] = []
    drift_positions_global: list[int] = []
    offset = 0

    variant_pairs = _random_chained_variant_pairs(rng, n_drifts)
    for i, seg_len in enumerate(lengths):
        lp = _random_local_drift_position(rng, seg_len, width_ref)
        local_positions.append(lp)
        drift_positions_global.append(offset + lp)
        offset += seg_len

    return {
        "lengths": lengths,
        "variant_pairs": variant_pairs,
        "local_positions": local_positions,
        "drift_positions": drift_positions_global,
        "n_drifts": n_drifts,
    }


def build_multi_drift_chunks_from_plan(
    plan: dict,
    width: int,
    seed: int,
) -> tuple[list[tuple], list[int]]:
    """依計畫建立多段 ConceptDriftStream；drift_positions 與 plan 一致。"""
    chunks: list[tuple] = []
    rng_meta = np.random.default_rng(seed)

    for i, seg_len in enumerate(plan["lengths"]):
        v_from, v_to = plan["variant_pairs"][i]
        chunk_pos = plan["local_positions"][i]
        sub_seed = seed + i * 97 + int(rng_meta.integers(0, 10_000))

        dataset = synth.ConceptDriftStream(
            stream=synth.SEA(seed=sub_seed, variant=v_from),
            drift_stream=synth.SEA(seed=sub_seed + 3, variant=v_to),
            position=chunk_pos,
            width=width,
            seed=sub_seed + 11,
        )
        chunks.append((dataset, seg_len))

    return chunks, list(plan["drift_positions"])


def _format_variant_summary(variant_pairs: list[tuple[int, int]]) -> str:
    parts = [f"{a}→{b}" for a, b in variant_pairs[:5]]
    suffix = "..." if len(variant_pairs) > 5 else ""
    return ",".join(parts) + suffix


def make_multi_sudden_drift_stream(
    n_samples=N_SAMPLES,
    seed=SEED,
    n_drifts: int | None = None,
    plan: dict | None = None,
    transition_width: int = SUDDEN_WIDTH,
):
    """單一 sudden 資料流。"""
    if plan is None:
        rng = np.random.default_rng(seed)
        if n_drifts is None:
            n_drifts = _random_n_drifts(rng)
        plan = build_drift_plan(n_samples, n_drifts, rng, width_ref=SUDDEN_WIDTH)
    chunks, drift_positions = build_multi_drift_chunks_from_plan(
        plan, transition_width, seed
    )
    meta = {
        "name": (
            f"Multi Sudden (random SEA, {plan['n_drifts']} drifts, w={transition_width})\n"
            f"transitions: {_format_variant_summary(plan['variant_pairs'])}"
        ),
        "drift_positions": drift_positions,
        "n_drifts": plan["n_drifts"],
        "width": transition_width,
        "plan": plan,
    }
    return chunks, meta


def make_multi_gradual_drift_stream(
    n_samples=N_SAMPLES,
    seed=SEED,
    n_drifts: int | None = None,
    plan: dict | None = None,
    transition_width: int = GRADUAL_WIDTH,
):
    """單一 gradual 資料流（與 sudden 共用同一 plan 時，分段與 drift 位置一致，僅 width 不同）。"""
    if plan is None:
        rng = np.random.default_rng(seed + 999)
        if n_drifts is None:
            n_drifts = _random_n_drifts(rng)
        plan = build_drift_plan(n_samples, n_drifts, rng, width_ref=SUDDEN_WIDTH)
    chunks, drift_positions = build_multi_drift_chunks_from_plan(
        plan, transition_width, seed + 999
    )
    meta = {
        "name": (
            f"Multi Gradual (random SEA, {plan['n_drifts']} drifts, w={transition_width})\n"
            f"transitions: {_format_variant_summary(plan['variant_pairs'])}"
        ),
        "drift_positions": drift_positions,
        "n_drifts": plan["n_drifts"],
        "width": transition_width,
        "plan": plan,
    }
    return chunks, meta


# =========================
# 資料擷取與滑動窗口
# =========================


def extract_stream_from_chunks(
    chunks: list[tuple],
    n_samples: int,
) -> tuple[list, np.ndarray]:
    xs: list = []
    ys: list = []
    for dataset, chunk_len in chunks:
        for x, y in dataset.take(chunk_len):
            xs.append(x)
            ys.append(int(y))
            if len(xs) >= n_samples:
                return xs[:n_samples], np.array(ys[:n_samples], dtype=int)
    return xs, np.array(ys, dtype=int)


def get_feature_names(xs):
    return sorted(xs[0].keys())


def to_matrix(xs, feature_names):
    return np.array(
        [[x[k] for k in feature_names] for x in xs],
        dtype=float,
    )


def rolling_label_proportion(labels, window=WINDOW):
    proportions = []
    q = deque()
    current_sum = 0
    for y in labels:
        q.append(y)
        current_sum += y
        if len(q) > window:
            current_sum -= q.popleft()
        proportions.append(current_sum / len(q))
    return np.array(proportions)


def rolling_feature_mean(values, window=WINDOW):
    means = []
    q = deque()
    current_sum = 0.0
    for v in values:
        q.append(v)
        current_sum += v
        if len(q) > window:
            current_sum -= q.popleft()
        means.append(current_sum / len(q))
    return np.array(means)


def sample_before_after(X, y, position, before_size=1500, after_size=1500):
    gap = max(500, position // 10)
    before_start = max(0, position - gap - before_size)
    before_end = position - gap
    after_start = position + gap
    after_end = min(len(y), position + gap + after_size)

    before_idx = np.arange(before_start, before_end)
    after_idx = np.arange(after_start, after_end)

    if len(before_idx) == 0:
        before_idx = np.arange(0, min(before_size, position))
    if len(after_idx) == 0:
        after_idx = np.arange(position, min(position + after_size, len(y)))

    return (X[before_idx], y[before_idx]), (X[after_idx], y[after_idx])


# =========================
# 繪圖
# =========================


def plot_label_distribution_over_time(
    times,
    proportions,
    title,
    drift_positions,
    save_path: str | None = None,
):
    """滑動窗口 P(Y=1) 隨時間變化；預設寫入圖檔（機率分布驗證 drift）。"""
    plt.figure(figsize=(14, 4))
    plt.plot(times, proportions, color="steelblue", linewidth=0.6)
    for pos in drift_positions:
        plt.axvline(pos, color="coral", linestyle="--", linewidth=0.9, alpha=0.85)
    plt.xlabel("Time step")
    plt.ylabel("Sliding-window P(Y=1)")
    plt.title(f"{title}\nLabel Distribution Over Time (vertical lines = drift centers)")
    plt.ylim(0.0, 1.0)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path is not None:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    # plt.show()
    plt.close()


def plot_feature_scatter_before_after(before_data, after_data, title, x_name, y_name):
    (X_before, y_before) = before_data
    (X_after, y_after) = after_data

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    ax1.scatter(X_before[:, 0], X_before[:, 1], c=y_before, alpha=0.5, s=12, cmap="coolwarm")
    ax1.set_xlabel(x_name)
    ax1.set_ylabel(y_name)
    ax1.set_title(f"{title}\nBefore first drift (x1 vs x2)")

    ax2.scatter(X_after[:, 0], X_after[:, 1], c=y_after, alpha=0.5, s=12, cmap="coolwarm")
    ax2.set_xlabel(x_name)
    ax2.set_ylabel(y_name)
    ax2.set_title(f"{title}\nAfter first drift (x1 vs x2)")

    plt.tight_layout()
    # plt.show()
    plt.close()


def plot_feature_mean_over_time(times, means, title, feature_name, drift_positions):
    plt.figure(figsize=(14, 4))
    plt.plot(times, means, color="darkgreen", linewidth=0.6)
    for pos in drift_positions:
        plt.axvline(pos, color="coral", linestyle="--", linewidth=0.9, alpha=0.85)
    plt.xlabel("Time step")
    plt.ylabel(f"Sliding-window mean({feature_name})")
    plt.title(f"{title}\nFeature Statistics Over Time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # plt.show()
    plt.close()


# =========================
# 實驗流程
# =========================


def run_multi_drift_experiment(
    chunks_and_meta_fn,
    n_samples=N_SAMPLES,
    label_plot_filename: str = "label_distribution.png",
):
    chunks, meta = chunks_and_meta_fn(n_samples=n_samples)
    _xs, ys = extract_stream_from_chunks(chunks, n_samples=n_samples)

    # 若需 scatter / 特徵時間序列圖，請取消註解並使用 xs、X、feature_names
    # xs, ys = extract_stream_from_chunks(chunks, n_samples=n_samples)
    # feature_names = get_feature_names(xs)
    # X = to_matrix(xs, feature_names)
    # first_pos = meta["drift_positions"][0]

    times = np.arange(len(ys))
    drift_positions = meta["drift_positions"]

    label_prop = rolling_label_proportion(ys, window=WINDOW)
    out_path = os.path.join(OUTPUT_DIR, label_plot_filename)
    plot_label_distribution_over_time(
        times, label_prop, meta["name"], drift_positions, save_path=out_path
    )
    print(f"  已儲存：{out_path}")

    # --- 以下僅保留供日後分析，目前不繪製／不顯示 ---
    # before_data, after_data = sample_before_after(
    #     X[:, :2], ys, first_pos,
    #     before_size=min(3000, n_samples // 10),
    #     after_size=min(3000, n_samples // 10),
    # )
    # x_name = f"x1 (feature {feature_names[0]})"
    # y_name = f"x2 (feature {feature_names[1]})"
    # plot_feature_scatter_before_after(before_data, after_data, meta["name"], x_name, y_name)

    # mean_x1 = rolling_feature_mean(X[:, 0], window=WINDOW)
    # plot_feature_mean_over_time(
    #     times, mean_x1, meta["name"],
    #     feature_name="x1",
    #     drift_positions=drift_positions,
    # )


# =========================
# 主程式
# =========================


def main():
    run_seed = _get_run_seed()
    rng = np.random.default_rng(run_seed)
    n_drifts = _random_n_drifts(rng)
    plan = build_drift_plan(N_SAMPLES, n_drifts, rng)

    print(f"本次 run_seed = {run_seed}（未設 DRIFT_SEED 時每次不同；重現請設 DRIFT_SEED={run_seed}）")
    print(f"資料長度：{N_SAMPLES}，本輪 drift 點數：{n_drifts}（5~10，隨機）")
    print("drift 時間（全域索引）：", plan["drift_positions"])
    print("各段隨機 SEA 轉換：", plan["variant_pairs"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("生成並儲存圖檔：Multi Sudden Drift ...")
    run_multi_drift_experiment(
        lambda n_samples=N_SAMPLES: make_multi_sudden_drift_stream(
            n_samples=n_samples, seed=run_seed, plan=plan
        ),
        n_samples=N_SAMPLES,
        label_plot_filename="label_distribution_sudden.png",
    )

    print("生成並儲存圖檔：Multi Gradual Drift ...")
    run_multi_drift_experiment(
        lambda n_samples=N_SAMPLES: make_multi_gradual_drift_stream(
            n_samples=n_samples, seed=run_seed, plan=plan
        ),
        n_samples=N_SAMPLES,
        label_plot_filename="label_distribution_gradual.png",
    )

    print(f"完成。機率分布圖已儲存至：{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
