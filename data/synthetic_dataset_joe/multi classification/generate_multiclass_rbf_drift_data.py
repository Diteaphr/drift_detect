"""
Multi-class concept drift（River）：

- sudden / gradual：多段 ConceptDriftStream，每段連接「兩個不同」的 RandomRBFDrift
  （前一段的 drift_stream 與下一段的 stream 使用相同種子／概念，鏈式銜接）。
  sudden 與 gradual 僅以 transition width 區分（窄 vs 寬）。

- incremental：單一 RandomRBFDrift，以 change_speed + n_drift_centroids 做質心漸進漂移。

輸出：sudden_drift / gradual_drift / incremental_drift 各 sensitivity 子目錄下 10 組 CSV + drift_times.txt，以及 summary.csv。
"""

from __future__ import annotations

import csv
import glob
import os
import secrets
import sys

import numpy as np
from river.datasets import synth

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from drift_common.intervals import drift_intervals_for_positions
from drift_common.profiles import SUDDEN_WIDTH, resolve
from drift_common.sensitivity import SENSITIVITY_TIERS

N_SAMPLES = 100_000
N_CLASSES = 4
N_FEATURES = 10
N_CENTROIDS = 50
N_RUNS = 10

MIN_SEGMENT_LEN = 2
N_DRIFTS_MIN = 5
N_DRIFTS_MAX = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUDDEN_DIR = os.path.join(BASE_DIR, "sudden_drift")
GRADUAL_DIR = os.path.join(BASE_DIR, "gradual_drift")
INCR_DIR = os.path.join(BASE_DIR, "incremental_drift")


def _random_n_drifts(rng: np.random.Generator) -> int:
    return int(rng.integers(N_DRIFTS_MIN, N_DRIFTS_MAX + 1))


def _random_partition_multinomial(
    rng: np.random.Generator,
    n: int,
    k: int,
    min_len: int,
) -> list[int]:
    if n < k * min_len:
        raise ValueError(f"n={n} 太小，無法分成 {k} 段且每段至少 {min_len}")
    remaining = n - k * min_len
    extras = rng.multinomial(remaining, [1.0 / k] * k)
    return [min_len + int(x) for x in extras]


def _max_offset_for_width(width: int) -> int:
    """River ConceptDriftStream: v=-4*(t-p)/w; keep 4*dist/w below exp overflow."""
    return max(1, int(174 * width))


def _random_local_drift_position(
    rng: np.random.Generator,
    seg_len: int,
    width_ref: int,
) -> int:
    if seg_len <= 2:
        return max(0, seg_len // 2)
    margin = _max_offset_for_width(width_ref)
    hi = min(seg_len - 1, margin + 1)
    if hi < 1:
        return 1
    return int(rng.integers(1, hi + 1))


def _build_concept_chain(n_drifts: int, rng: np.random.Generator) -> list[int]:
    """長度 n_drifts+1：相鄰概念鍵必相異，用於鏈式 RandomRBFDrift。"""
    chain: list[int] = []
    first = int(rng.integers(1, 2**30))
    chain.append(first)
    for _ in range(n_drifts):
        nxt = int(rng.integers(1, 2**30))
        while nxt == chain[-1]:
            nxt = int(rng.integers(1, 2**30))
        chain.append(nxt)
    return chain


def _rbf_static_for_concept(concept_key: int, run_seed: int) -> synth.RandomRBFDrift:
    """固定概念：質心不漂移，供 ConceptDriftStream 兩端混合。"""
    sm = ((concept_key * 10007 + run_seed) % (2**31 - 2)) + 1
    ss = ((concept_key ^ run_seed) & 0x7FFFFFFF) + 1
    return synth.RandomRBFDrift(
        seed_model=sm,
        seed_sample=ss,
        n_classes=N_CLASSES,
        n_features=N_FEATURES,
        n_centroids=N_CENTROIDS,
        change_speed=0.0,
        n_drift_centroids=0,
    )


def build_drift_plan(
    n_samples: int,
    n_drifts: int,
    rng: np.random.Generator,
    width_ref: int = SUDDEN_WIDTH,
) -> dict:
    lengths = _random_partition_multinomial(rng, n_samples, n_drifts, MIN_SEGMENT_LEN)
    local_positions: list[int] = []
    drift_positions_global: list[int] = []
    offset = 0
    for seg_len in lengths:
        lp = _random_local_drift_position(rng, seg_len, width_ref)
        local_positions.append(lp)
        drift_positions_global.append(offset + lp)
        offset += seg_len
    concept_chain = _build_concept_chain(n_drifts, rng)
    return {
        "lengths": lengths,
        "local_positions": local_positions,
        "drift_positions": drift_positions_global,
        "n_drifts": n_drifts,
        "concept_chain": concept_chain,
    }


def build_concept_drift_chunks(
    plan: dict,
    transition_width: int,
    run_seed: int,
) -> list[tuple]:
    """每段 ConceptDriftStream：stream=概念 i，drift_stream=概念 i+1（與下一段 stream 相同配置）。"""
    chunks: list[tuple] = []
    rng_meta = np.random.default_rng(run_seed)
    chain = plan["concept_chain"]
    n = plan["n_drifts"]
    for i in range(n):
        seg_len = plan["lengths"][i]
        chunk_pos = plan["local_positions"][i]
        from_k = chain[i]
        to_k = chain[i + 1]
        stream = _rbf_static_for_concept(from_k, run_seed)
        drift_stream = _rbf_static_for_concept(to_k, run_seed)
        sub_seed = run_seed + i * 97 + int(rng_meta.integers(0, 10_000))
        cds = synth.ConceptDriftStream(
            stream=stream,
            drift_stream=drift_stream,
            position=chunk_pos,
            width=transition_width,
            seed=sub_seed + 11,
        )
        chunks.append((cds, seg_len))
    return chunks


def extract_stream_from_chunks(chunks: list[tuple], n_samples: int) -> tuple[list, list]:
    xs: list = []
    ys: list = []
    for dataset, chunk_len in chunks:
        for x, y in dataset.take(chunk_len):
            xs.append(x)
            ys.append(int(y))
            if len(xs) >= n_samples:
                return xs[:n_samples], ys[:n_samples]
    return xs, ys


def incremental_drift_intervals(seed: int, n_samples: int) -> list[list[int]]:
    """漸進式漂移：以數個連續時間區段標示監測區間（隨機但可重現）。"""
    rng = np.random.default_rng(seed + 31)
    n_seg = int(rng.integers(4, 8))
    lens = rng.multinomial(n_samples, [1.0 / n_seg] * n_seg)
    intervals: list[list[int]] = []
    t = 0
    for ln in lens:
        ln = max(1, int(ln))
        s = t
        e = min(n_samples - 1, t + ln - 1)
        intervals.append([s, e])
        t = e + 1
        if t >= n_samples:
            break
    return intervals


def write_csv_multiclass(path: str, xs: list, ys: list) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    header = [f"x{i}" for i in range(N_FEATURES)] + ["y"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for x, yi in zip(xs, ys):
            w.writerow([x[i] for i in range(N_FEATURES)] + [int(yi)])


def write_drift_times(path: str, intervals: list[list[int]]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(repr(intervals))


def file_prefix(profile: str) -> str:
    return f"recurring_{profile}_rbf{N_CLASSES}_100k"


def clear_old_outputs() -> None:
    for d in (SUDDEN_DIR, GRADUAL_DIR, INCR_DIR):
        for pat in ("*.csv", "*_drift_times.txt"):
            for fp in glob.glob(os.path.join(d, pat)):
                try:
                    os.remove(fp)
                except OSError:
                    pass
        for tier in SENSITIVITY_TIERS:
            tier_dir = os.path.join(d, tier)
            for pat in ("*.csv", "*_drift_times.txt"):
                for fp in glob.glob(os.path.join(tier_dir, pat)):
                    try:
                        os.remove(fp)
                    except OSError:
                        pass
    sp = os.path.join(BASE_DIR, "summary.csv")
    if os.path.isfile(sp):
        os.remove(sp)


def _append_summary_row(
    rows: list,
    drift_type: str,
    tier: str,
    params: dict,
    run_id: int,
    drift_folder: str,
    csv_name: str,
    txt_name: str,
    seed: int,
) -> None:
    rows.append(
        {
            "drift_type": drift_type,
            "sensitivity": tier,
            "sensitivity_multiplier": params["sensitivity_multiplier"],
            "run_id": run_id,
            "csv_filename": f"{drift_folder}/{tier}/{csv_name}",
            "drift_times_filename": f"{drift_folder}/{tier}/{txt_name}",
            "random_seed": seed,
        }
    )


def run_concept_drift_profile(
    profile: str,
    base_dir: str,
    drift_folder: str,
    rows: list,
) -> None:
    prefix = file_prefix(profile)
    for tier in SENSITIVITY_TIERS:
        params = resolve("multiclass", profile, tier)
        transition_width = params["width"]
        out_dir = os.path.join(base_dir, tier)
        os.makedirs(out_dir, exist_ok=True)

        for run_id in range(1, N_RUNS + 1):
            g_tag = f"g{run_id - 1:02d}"
            seed = secrets.randbelow(2**32)
            rng = np.random.default_rng(seed)
            n_drifts = _random_n_drifts(rng)
            plan = build_drift_plan(
                N_SAMPLES, n_drifts, rng, width_ref=transition_width
            )
            chunks = build_concept_drift_chunks(plan, transition_width, seed)
            xs, ys = extract_stream_from_chunks(chunks, N_SAMPLES)
            assert len(xs) == N_SAMPLES

            csv_name = f"{prefix}_{g_tag}.csv"
            txt_name = f"{prefix}_{g_tag}_drift_times.txt"
            csv_path = os.path.join(out_dir, csv_name)
            txt_path = os.path.join(out_dir, txt_name)
            write_csv_multiclass(csv_path, xs, ys)
            intervals = drift_intervals_for_positions(
                plan["drift_positions"], transition_width, N_SAMPLES
            )
            write_drift_times(txt_path, intervals)
            _append_summary_row(
                rows, profile, tier, params, run_id, drift_folder, csv_name, txt_name, seed
            )


def run_incremental_profile(rows: list) -> None:
    prefix = file_prefix("incremental")
    for tier in SENSITIVITY_TIERS:
        params = resolve("multiclass", "incremental", tier)
        out_dir = os.path.join(INCR_DIR, tier)
        os.makedirs(out_dir, exist_ok=True)

        for run_id in range(1, N_RUNS + 1):
            g_tag = f"g{run_id - 1:02d}"
            seed = secrets.randbelow(2**32)
            ds = synth.RandomRBFDrift(
                seed_model=seed,
                seed_sample=seed ^ 0xA5A5A5A5,
                n_classes=N_CLASSES,
                n_features=N_FEATURES,
                n_centroids=N_CENTROIDS,
                change_speed=params["change_speed"],
                n_drift_centroids=params["n_drift_centroids"],
            )
            xs: list = []
            ys: list = []
            for i, (x, y) in enumerate(ds):
                if i >= N_SAMPLES:
                    break
                xs.append(x)
                ys.append(int(y))
            csv_name = f"{prefix}_{g_tag}.csv"
            txt_name = f"{prefix}_{g_tag}_drift_times.txt"
            csv_path = os.path.join(out_dir, csv_name)
            txt_path = os.path.join(out_dir, txt_name)
            write_csv_multiclass(csv_path, xs, ys)
            intervals = incremental_drift_intervals(seed, N_SAMPLES)
            write_drift_times(txt_path, intervals)
            _append_summary_row(
                rows,
                "incremental",
                tier,
                params,
                run_id,
                "incremental_drift",
                csv_name,
                txt_name,
                seed,
            )


def main() -> None:
    clear_old_outputs()
    for d in (SUDDEN_DIR, GRADUAL_DIR, INCR_DIR):
        os.makedirs(d, exist_ok=True)

    rows: list[dict] = []
    run_concept_drift_profile("sudden", SUDDEN_DIR, "sudden_drift", rows)
    run_concept_drift_profile("gradual", GRADUAL_DIR, "gradual_drift", rows)
    run_incremental_profile(rows)

    summary_path = os.path.join(BASE_DIR, "summary.csv")
    fieldnames = [
        "drift_type",
        "sensitivity",
        "sensitivity_multiplier",
        "run_id",
        "csv_filename",
        "drift_times_filename",
        "random_seed",
    ]
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print(
        f"已清除舊檔並重新寫入：{BASE_DIR}（{len(rows)} 組資料 + summary.csv）"
    )


if __name__ == "__main__":
    main()
