"""Binary / multiclass / regression stream generators."""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Any

import numpy as np
from river.datasets import synth

from common import (
    annotate_fixed_windows,
    build_segment_plan,
    choose_recurring_mode,
    deterministic_seed,
    drift_dir,
    drift_intervals_for_positions,
    ensure_dirs,
    extract_from_chunks,
    g_tag,
    plots_dir,
    plot_stream_overview,
    save_recurring_manifest,
    validate_dataset,
    width_for_mode,
    write_csv,
    write_drift_times,
    write_json,
)
from config import (
    BINARY_HYPERPLANE_FEATURES,
    BINARY_SEA_FEATURES,
    GRADUAL_WIDTH,
    HYPERPLANE_NOISE,
    INCR_ANNOTATION_WIDTH,
    MASTER_SEED,
    MULTI_N_CENTROIDS,
    MULTI_N_CLASSES,
    MULTI_N_FEATURES,
    REG_INCR_PARAM_STEP,
    REG_JUMP_SCALE,
    REG_N_FEATURES,
    SUDDEN_WIDTH,
)


# ---------------------------------------------------------------------------
# Binary helpers (SEA / Hyperplane)
# ---------------------------------------------------------------------------


def _chained_sea_pairs(rng: np.random.Generator, n: int) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    current = int(rng.integers(0, 4))
    for _ in range(n):
        candidates = [j for j in range(4) if j != current]
        v_to = int(rng.choice(candidates))
        pairs.append((current, v_to))
        current = v_to
    return pairs


def _recurring_sea_pairs(rng: np.random.Generator, n: int) -> list[tuple[int, int]]:
    """Alternate between two SEA variants A <-> B."""
    a = int(rng.integers(0, 4))
    b = int(rng.choice([j for j in range(4) if j != a]))
    pairs: list[tuple[int, int]] = []
    cur = a
    other = b
    for _ in range(n):
        pairs.append((cur, other))
        cur, other = other, cur
    return pairs


def _sea_chunks(plan: dict, width: int, seed: int) -> list[tuple]:
    chunks: list[tuple] = []
    rng_meta = np.random.default_rng(seed)
    for i, seg_len in enumerate(plan["lengths"]):
        v_from, v_to = plan["variant_pairs"][i]
        chunk_pos = plan["local_positions"][i]
        sub_seed = seed + i * 97 + int(rng_meta.integers(0, 10_000))
        cds = synth.ConceptDriftStream(
            stream=synth.SEA(seed=sub_seed, variant=v_from),
            drift_stream=synth.SEA(seed=sub_seed + 3, variant=v_to),
            position=chunk_pos,
            width=width,
            seed=sub_seed + 11,
        )
        chunks.append((cds, seg_len))
    return chunks


def _hyperplane_static(seed: int) -> synth.Hyperplane:
    return synth.Hyperplane(
        seed=seed,
        n_features=BINARY_HYPERPLANE_FEATURES,
        n_drift_features=0,
        mag_change=0.0,
        noise_percentage=HYPERPLANE_NOISE,
    )


def _hyperplane_chunks(plan: dict, width: int, seed: int, concept_keys: list[int]) -> list[tuple]:
    chunks: list[tuple] = []
    rng_meta = np.random.default_rng(seed)
    for i, seg_len in enumerate(plan["lengths"]):
        from_k = concept_keys[i]
        to_k = concept_keys[i + 1]
        chunk_pos = plan["local_positions"][i]
        sub_seed = seed + i * 97 + int(rng_meta.integers(0, 10_000))
        cds = synth.ConceptDriftStream(
            stream=_hyperplane_static(from_k),
            drift_stream=_hyperplane_static(to_k),
            position=chunk_pos,
            width=width,
            seed=sub_seed + 11,
        )
        chunks.append((cds, seg_len))
    return chunks


def _build_concept_keys(n_drifts: int, rng: np.random.Generator, recurring: bool) -> list[int]:
    if recurring:
        a = int(rng.integers(1, 2**30))
        b = int(rng.integers(1, 2**30))
        while b == a:
            b = int(rng.integers(1, 2**30))
        keys = [a]
        cur, other = a, b
        for _ in range(n_drifts):
            cur, other = other, cur
            keys.append(cur)
        return keys
    keys = [int(rng.integers(1, 2**30))]
    for _ in range(n_drifts):
        nxt = int(rng.integers(1, 2**30))
        while nxt == keys[-1]:
            nxt = int(rng.integers(1, 2**30))
        keys.append(nxt)
    return keys


def generate_binary_sea_transition(
    *,
    n_samples: int,
    seed: int,
    width: int,
    recurring: bool = False,
) -> tuple[list, list, list[list[int]], dict]:
    rng = np.random.default_rng(seed)
    plan = build_segment_plan(n_samples, rng, width_ref=min(width, SUDDEN_WIDTH))
    if recurring:
        plan["variant_pairs"] = _recurring_sea_pairs(rng, plan["n_drifts"])
    else:
        plan["variant_pairs"] = _chained_sea_pairs(rng, plan["n_drifts"])
    chunks = _sea_chunks(plan, width, seed)
    xs, ys = extract_from_chunks(chunks, n_samples)
    ys = [int(y) for y in ys]
    intervals = drift_intervals_for_positions(plan["drift_positions"], width, n_samples)
    meta = {
        "generator": "SEA+ConceptDriftStream",
        "width": width,
        "n_drifts": plan["n_drifts"],
        "drift_positions": plan["drift_positions"],
        "variant_pairs": plan["variant_pairs"],
        "recurring": recurring,
    }
    return xs, ys, intervals, meta


def _take_n(dataset: Any, n: int) -> tuple[list, list]:
    xs: list = []
    ys: list = []
    if n <= 0:
        return xs, ys
    for i, (x, y) in enumerate(dataset):
        if i >= n:
            break
        xs.append(x)
        ys.append(y)
    return xs, ys


def generate_binary_hyperplane_incremental(
    *,
    n_samples: int,
    seed: int,
) -> tuple[list, list, list[list[int]], dict]:
    """Incremental: transition width ≤1000; new concept persists until next drift."""
    xs, ys, intervals, meta = generate_binary_hyperplane_transition(
        n_samples=n_samples,
        seed=seed,
        width=INCR_ANNOTATION_WIDTH,
        recurring=False,
    )
    meta["generator"] = "Hyperplane+ConceptDriftStream"
    meta["drift_policy"] = "persist_after_transition"
    meta["annotation_width"] = INCR_ANNOTATION_WIDTH
    return xs, ys, intervals, meta


def generate_binary_no_drift(
    *,
    n_samples: int,
    seed: int,
    kind: str,
) -> tuple[list, list]:
    """Baseline stream: single static concept (same seed family as drifted gens)."""
    if kind == "sea":
        xs, ys = _take_n(synth.SEA(seed=seed, variant=0), n_samples)
        return xs, [int(y) for y in ys]
    if kind == "hyperplane":
        xs, ys = _take_n(_hyperplane_static(seed), n_samples)
        return xs, [int(y) for y in ys]
    raise ValueError(kind)


def generate_binary_hyperplane_transition(
    *,
    n_samples: int,
    seed: int,
    width: int,
    recurring: bool = False,
) -> tuple[list, list, list[list[int]], dict]:
    rng = np.random.default_rng(seed)
    plan = build_segment_plan(n_samples, rng, width_ref=min(width, SUDDEN_WIDTH))
    keys = _build_concept_keys(plan["n_drifts"], rng, recurring=recurring)
    chunks = _hyperplane_chunks(plan, width, seed, keys)
    xs, ys = extract_from_chunks(chunks, n_samples)
    ys = [int(y) for y in ys]
    intervals = drift_intervals_for_positions(plan["drift_positions"], width, n_samples)
    meta = {
        "generator": "Hyperplane+ConceptDriftStream",
        "width": width,
        "n_drifts": plan["n_drifts"],
        "concept_keys": keys,
        "recurring": recurring,
    }
    return xs, ys, intervals, meta


# ---------------------------------------------------------------------------
# Multiclass (RandomRBF)
# ---------------------------------------------------------------------------


def _rbf_static(concept_key: int, run_seed: int) -> synth.RandomRBFDrift:
    sm = ((concept_key * 10007 + run_seed) % (2**31 - 2)) + 1
    ss = ((concept_key ^ run_seed) & 0x7FFFFFFF) + 1
    return synth.RandomRBFDrift(
        seed_model=sm,
        seed_sample=ss,
        n_classes=MULTI_N_CLASSES,
        n_features=MULTI_N_FEATURES,
        n_centroids=MULTI_N_CENTROIDS,
        change_speed=0.0,
        n_drift_centroids=0,
    )


def generate_multiclass_transition(
    *,
    n_samples: int,
    seed: int,
    width: int,
    recurring: bool = False,
) -> tuple[list, list, list[list[int]], dict]:
    rng = np.random.default_rng(seed)
    plan = build_segment_plan(n_samples, rng, width_ref=min(width, SUDDEN_WIDTH))
    keys = _build_concept_keys(plan["n_drifts"], rng, recurring=recurring)
    chunks: list[tuple] = []
    rng_meta = np.random.default_rng(seed)
    for i, seg_len in enumerate(plan["lengths"]):
        from_k, to_k = keys[i], keys[i + 1]
        chunk_pos = plan["local_positions"][i]
        sub_seed = seed + i * 97 + int(rng_meta.integers(0, 10_000))
        cds = synth.ConceptDriftStream(
            stream=_rbf_static(from_k, seed),
            drift_stream=_rbf_static(to_k, seed),
            position=chunk_pos,
            width=width,
            seed=sub_seed + 11,
        )
        chunks.append((cds, seg_len))
    xs, ys = extract_from_chunks(chunks, n_samples)
    ys = [int(y) for y in ys]
    intervals = drift_intervals_for_positions(plan["drift_positions"], width, n_samples)
    meta = {
        "generator": "RandomRBFDrift+ConceptDriftStream",
        "n_classes": MULTI_N_CLASSES,
        "n_features": MULTI_N_FEATURES,
        "width": width,
        "n_drifts": plan["n_drifts"],
        "concept_keys": keys,
        "recurring": recurring,
    }
    return xs, ys, intervals, meta


def generate_multiclass_incremental(
    *,
    n_samples: int,
    seed: int,
) -> tuple[list, list, list[list[int]], dict]:
    """Incremental: transition width ≤1000; new concept persists until next drift."""
    xs, ys, intervals, meta = generate_multiclass_transition(
        n_samples=n_samples,
        seed=seed,
        width=INCR_ANNOTATION_WIDTH,
        recurring=False,
    )
    meta["drift_policy"] = "persist_after_transition"
    meta["annotation_width"] = INCR_ANNOTATION_WIDTH
    return xs, ys, intervals, meta


def generate_multiclass_no_drift(*, n_samples: int, seed: int) -> tuple[list, list]:
    xs, ys = _take_n(_rbf_static(seed, seed), n_samples)
    return xs, [int(y) for y in ys]


# ---------------------------------------------------------------------------
# Regression (Friedman)
# ---------------------------------------------------------------------------

COEFF_INIT = np.array([10.0, 20.0, 10.0, 5.0], dtype=float)
COEFF_LO = np.array([4.0, 8.0, 4.0, 2.0], dtype=float)
COEFF_HI = np.array([22.0, 32.0, 18.0, 12.0], dtype=float)


def _friedman_y(x: dict[int, float], coeff: np.ndarray, rng_py: random.Random) -> float:
    a, b, c, d = coeff.tolist()
    return (
        a * math.sin(math.pi * x[0] * x[1])
        + b * (x[2] - 0.5) ** 2
        + c * x[3]
        + d * x[4]
        + rng_py.gauss(0.0, 1.0)
    )


def _random_target_coeff(rng_np: np.random.Generator) -> np.ndarray:
    u = rng_np.beta(2.0, 2.0, size=4)
    return COEFF_LO + u * (COEFF_HI - COEFF_LO)


def generate_regression_sudden(
    *,
    n_samples: int,
    seed: int,
    recurring: bool = False,
) -> tuple[list, list, list[list[int]], dict]:
    rng_py = random.Random(seed)
    rng_np = np.random.default_rng(seed)
    plan = build_segment_plan(n_samples, rng_np, width_ref=SUDDEN_WIDTH)
    jump_at = set(plan["drift_positions"])

    if recurring:
        a = COEFF_INIT.copy()
        b = _random_target_coeff(rng_np)
        targets = []
        use_b = True
        for _ in plan["drift_positions"]:
            targets.append(b.copy() if use_b else a.copy())
            use_b = not use_b
    else:
        targets = [_random_target_coeff(rng_np) for _ in plan["drift_positions"]]

    coeff = COEFF_INIT.copy()
    xs: list = []
    ys: list = []
    ti = 0
    for t in range(n_samples):
        if t in jump_at:
            target = targets[ti]
            ti += 1
            coeff = coeff + REG_JUMP_SCALE * (target - coeff)
            coeff = np.clip(coeff, COEFF_LO, COEFF_HI)
        x = {i: rng_py.uniform(0.0, 1.0) for i in range(REG_N_FEATURES)}
        xs.append(x)
        ys.append(_friedman_y(x, coeff, rng_py))

    intervals = annotate_fixed_windows(n_samples, plan["drift_positions"], SUDDEN_WIDTH)
    # sudden: keep intervals very short (≈ width)
    meta = {
        "generator": "manual_Friedman_sudden",
        "width": SUDDEN_WIDTH,
        "n_drifts": plan["n_drifts"],
        "recurring": recurring,
    }
    return xs, ys, intervals, meta


def generate_regression_gradual(
    *,
    n_samples: int,
    seed: int,
    width: int = GRADUAL_WIDTH,
    recurring: bool = False,
) -> tuple[list, list, list[list[int]], dict]:
    """Manual gradual coeff blend over windows of length <= width (not River gsg defaults)."""
    rng_py = random.Random(seed)
    rng_np = np.random.default_rng(seed)
    plan = build_segment_plan(n_samples, rng_np, width_ref=SUDDEN_WIDTH)
    positions = plan["drift_positions"]

    if recurring:
        a = COEFF_INIT.copy()
        b = _random_target_coeff(rng_np)
        seq = []
        use_b = True
        for _ in positions:
            seq.append(b.copy() if use_b else a.copy())
            use_b = not use_b
    else:
        seq = [_random_target_coeff(rng_np) for _ in positions]

    coeff = COEFF_INIT.copy()
    xs: list = []
    ys: list = []
    # precompute blend schedules: for each drift center, blend over [p-half, p+half]
    half = width // 2
    blends: list[tuple[int, int, np.ndarray, np.ndarray]] = []
    cur = coeff.copy()
    for p, target in zip(positions, seq):
        s = max(0, p - half)
        e = min(n_samples - 1, p + half)
        blends.append((s, e, cur.copy(), target.copy()))
        cur = target.copy()

    active = {t: i for i, (s, e, _, _) in enumerate(blends) for t in range(s, e + 1)}
    coeff = COEFF_INIT.copy()

    for t in range(n_samples):
        if t in active:
            i = active[t]
            s, e, c0, c1 = blends[i]
            span = max(1, e - s)
            alpha = (t - s) / span
            coeff = (1 - alpha) * c0 + alpha * c1
            if t == e:
                coeff = c1.copy()
        x = {i: rng_py.uniform(0.0, 1.0) for i in range(REG_N_FEATURES)}
        xs.append(x)
        ys.append(_friedman_y(x, coeff, rng_py))

    intervals = drift_intervals_for_positions(positions, width, n_samples)
    meta = {
        "generator": "manual_Friedman_gradual",
        "width": width,
        "n_drifts": plan["n_drifts"],
        "recurring": recurring,
    }
    return xs, ys, intervals, meta


def generate_regression_incremental(
    *,
    n_samples: int,
    seed: int,
    recurring: bool = False,
) -> tuple[list, list, list[list[int]], dict]:
    """Incremental: blend over width ≤1000; new Friedman coeffs persist until next drift."""
    xs, ys, intervals, meta = generate_regression_gradual(
        n_samples=n_samples,
        seed=seed,
        width=INCR_ANNOTATION_WIDTH,
        recurring=recurring,
    )
    meta["generator"] = "manual_Friedman_incremental"
    meta["drift_policy"] = "persist_after_transition"
    meta["annotation_width"] = INCR_ANNOTATION_WIDTH
    return xs, ys, intervals, meta


def generate_regression_no_drift(*, n_samples: int, seed: int) -> tuple[list, list]:
    """Fixed Friedman coefficients (no concept change)."""
    rng_py = random.Random(seed)
    coeff = COEFF_INIT.copy()
    xs: list = []
    ys: list = []
    for _ in range(n_samples):
        x = {i: rng_py.uniform(0.0, 1.0) for i in range(REG_N_FEATURES)}
        xs.append(x)
        ys.append(_friedman_y(x, coeff, rng_py))
    return xs, ys


# ---------------------------------------------------------------------------
# Task runners
# ---------------------------------------------------------------------------


def _cap_for_validate(drift_type: str, mode: str | None = None) -> int | None:
    """Max allowed inclusive interval length (width + 1 for centered windows)."""
    if drift_type == "sudden":
        return SUDDEN_WIDTH + 1
    if drift_type in {"gradual", "incremental"}:
        return INCR_ANNOTATION_WIDTH + 1
    if drift_type == "recurring":
        assert mode is not None
        if mode == "sudden":
            return SUDDEN_WIDTH + 1
        return INCR_ANNOTATION_WIDTH + 1
    return None


def _stem_binary(drift_type: str, g_id: int, mode: str | None = None) -> str:
    tag = g_tag(g_id)
    if drift_type == "sudden":
        return f"sudden_sea100k_{tag}"
    if drift_type == "gradual":
        return f"gradual_sea100k_{tag}"
    if drift_type == "incremental":
        return f"incremental_hyperplane_100k_{tag}"
    assert mode is not None
    if mode == "sudden":
        return f"recurring_sudden_sea100k_{tag}"
    if mode == "gradual":
        return f"recurring_gradual_sea100k_{tag}"
    return f"recurring_incremental_hyperplane_100k_{tag}"


def _stem_multi(drift_type: str, g_id: int, mode: str | None = None) -> str:
    tag = g_tag(g_id)
    if drift_type == "recurring":
        assert mode is not None
        return f"recurring_{mode}_rbf4_100k_{tag}"
    return f"{drift_type}_rbf4_100k_{tag}"


def _stem_reg(drift_type: str, g_id: int, mode: str | None = None) -> str:
    tag = g_tag(g_id)
    if drift_type == "recurring":
        assert mode is not None
        return f"recurring_{mode}_friedman_100k_{tag}"
    return f"{drift_type}_friedman_100k_{tag}"


def run_binary(
    *,
    n_samples: int,
    g_ids: list[int],
    drift_types: list[str],
    master_seed: int = MASTER_SEED,
    make_plots: bool = True,
) -> list[dict]:
    ensure_dirs("binary")
    recurring_rows: list[dict] = []
    written: list[dict] = []

    for g_id in g_ids:
        for drift_type in drift_types:
            seed = deterministic_seed("binary", drift_type, g_id, master=master_seed)
            mode: str | None = None
            if drift_type == "sudden":
                xs, ys, intervals, meta = generate_binary_sea_transition(
                    n_samples=n_samples, seed=seed, width=SUDDEN_WIDTH
                )
                n_feat = BINARY_SEA_FEATURES
            elif drift_type == "gradual":
                xs, ys, intervals, meta = generate_binary_sea_transition(
                    n_samples=n_samples, seed=seed, width=GRADUAL_WIDTH
                )
                n_feat = BINARY_SEA_FEATURES
            elif drift_type == "incremental":
                xs, ys, intervals, meta = generate_binary_hyperplane_incremental(
                    n_samples=n_samples, seed=seed
                )
                n_feat = BINARY_HYPERPLANE_FEATURES
            elif drift_type == "recurring":
                mode = choose_recurring_mode("binary", g_id, master=master_seed)
                w = width_for_mode(mode)
                if mode in {"sudden", "gradual"}:
                    xs, ys, intervals, meta = generate_binary_sea_transition(
                        n_samples=n_samples, seed=seed, width=w, recurring=True
                    )
                    n_feat = BINARY_SEA_FEATURES
                else:
                    xs, ys, intervals, meta = generate_binary_hyperplane_transition(
                        n_samples=n_samples, seed=seed, width=w, recurring=True
                    )
                    n_feat = BINARY_HYPERPLANE_FEATURES
                meta["chosen_drift_mode"] = mode
            else:
                raise ValueError(drift_type)

            stem = _stem_binary(drift_type, g_id, mode)
            out_dir = drift_dir("binary", drift_type)
            csv_path = out_dir / f"{stem}.csv"
            txt_path = out_dir / f"{stem}_drift_times.txt"
            write_csv(csv_path, xs, ys, n_feat)
            write_drift_times(txt_path, intervals)
            validate_dataset(
                csv_path,
                txt_path,
                n_samples=n_samples,
                max_transition_width=_cap_for_validate(drift_type, mode),
            )

            row = {
                "task": "binary",
                "drift_type": drift_type,
                "g_id": g_id,
                "stem": stem,
                "seed": seed,
                "n_samples": n_samples,
                "chosen_drift_mode": mode,
                **{k: meta[k] for k in meta if k != "concept_keys"},
            }
            if drift_type == "recurring":
                meta_path = out_dir / f"{stem}.json"
                write_json(meta_path, {**row, "intervals": intervals, "meta": meta})
                recurring_rows.append(row)
            written.append(row)
            print(f"[binary] wrote {csv_path.name} (n={n_samples})")

            if make_plots and g_id == g_ids[0]:
                if drift_type in {"sudden", "gradual"} or (
                    drift_type == "recurring" and mode in {"sudden", "gradual"}
                ):
                    _, ys_base = generate_binary_no_drift(
                        n_samples=n_samples, seed=seed, kind="sea"
                    )
                else:
                    _, ys_base = generate_binary_no_drift(
                        n_samples=n_samples, seed=seed, kind="hyperplane"
                    )
                plot_stream_overview(
                    csv_path,
                    txt_path,
                    plots_dir("binary") / f"{stem}.png",
                    title=f"binary / {drift_type} / {stem}",
                    task="binary",
                    y_baseline=ys_base,
                )

    if recurring_rows:
        save_recurring_manifest("binary", recurring_rows)
    return written


def run_multiclass(
    *,
    n_samples: int,
    g_ids: list[int],
    drift_types: list[str],
    master_seed: int = MASTER_SEED,
    make_plots: bool = True,
) -> list[dict]:
    ensure_dirs("multi_classification")
    recurring_rows: list[dict] = []
    written: list[dict] = []

    for g_id in g_ids:
        for drift_type in drift_types:
            seed = deterministic_seed("multi", drift_type, g_id, master=master_seed)
            mode: str | None = None
            if drift_type == "sudden":
                xs, ys, intervals, meta = generate_multiclass_transition(
                    n_samples=n_samples, seed=seed, width=SUDDEN_WIDTH
                )
            elif drift_type == "gradual":
                xs, ys, intervals, meta = generate_multiclass_transition(
                    n_samples=n_samples, seed=seed, width=GRADUAL_WIDTH
                )
            elif drift_type == "incremental":
                xs, ys, intervals, meta = generate_multiclass_incremental(
                    n_samples=n_samples, seed=seed
                )
            elif drift_type == "recurring":
                mode = choose_recurring_mode("multi_classification", g_id, master=master_seed)
                w = width_for_mode(mode)
                if mode == "incremental":
                    # recurring incremental: alternate two RBF concepts with width=1000
                    xs, ys, intervals, meta = generate_multiclass_transition(
                        n_samples=n_samples, seed=seed, width=w, recurring=True
                    )
                else:
                    xs, ys, intervals, meta = generate_multiclass_transition(
                        n_samples=n_samples, seed=seed, width=w, recurring=True
                    )
                meta["chosen_drift_mode"] = mode
            else:
                raise ValueError(drift_type)

            stem = _stem_multi(drift_type, g_id, mode)
            out_dir = drift_dir("multi_classification", drift_type)
            csv_path = out_dir / f"{stem}.csv"
            txt_path = out_dir / f"{stem}_drift_times.txt"
            write_csv(csv_path, xs, ys, MULTI_N_FEATURES)
            write_drift_times(txt_path, intervals)
            validate_dataset(
                csv_path,
                txt_path,
                n_samples=n_samples,
                max_transition_width=_cap_for_validate(drift_type, mode),
            )
            row = {
                "task": "multi_classification",
                "drift_type": drift_type,
                "g_id": g_id,
                "stem": stem,
                "seed": seed,
                "n_samples": n_samples,
                "chosen_drift_mode": mode,
                "n_drifts": meta.get("n_drifts"),
                "width": meta.get("width") or meta.get("annotation_width"),
            }
            if drift_type == "recurring":
                write_json(out_dir / f"{stem}.json", {**row, "intervals": intervals, "meta": meta})
                recurring_rows.append(row)
            written.append(row)
            print(f"[multi] wrote {csv_path.name} (n={n_samples})")

            if make_plots and g_id == g_ids[0]:
                _, ys_base = generate_multiclass_no_drift(n_samples=n_samples, seed=seed)
                plot_stream_overview(
                    csv_path,
                    txt_path,
                    plots_dir("multi_classification") / f"{stem}.png",
                    title=f"multi / {drift_type} / {stem}",
                    task="multi_classification",
                    y_baseline=ys_base,
                )

    if recurring_rows:
        save_recurring_manifest("multi_classification", recurring_rows)
    return written


def run_regression(
    *,
    n_samples: int,
    g_ids: list[int],
    drift_types: list[str],
    master_seed: int = MASTER_SEED,
    make_plots: bool = True,
) -> list[dict]:
    ensure_dirs("regression")
    recurring_rows: list[dict] = []
    written: list[dict] = []

    for g_id in g_ids:
        for drift_type in drift_types:
            seed = deterministic_seed("regression", drift_type, g_id, master=master_seed)
            mode: str | None = None
            if drift_type == "sudden":
                xs, ys, intervals, meta = generate_regression_sudden(
                    n_samples=n_samples, seed=seed
                )
            elif drift_type == "gradual":
                xs, ys, intervals, meta = generate_regression_gradual(
                    n_samples=n_samples, seed=seed, width=GRADUAL_WIDTH
                )
            elif drift_type == "incremental":
                xs, ys, intervals, meta = generate_regression_incremental(
                    n_samples=n_samples, seed=seed
                )
            elif drift_type == "recurring":
                mode = choose_recurring_mode("regression", g_id, master=master_seed)
                if mode == "sudden":
                    xs, ys, intervals, meta = generate_regression_sudden(
                        n_samples=n_samples, seed=seed, recurring=True
                    )
                elif mode == "gradual":
                    xs, ys, intervals, meta = generate_regression_gradual(
                        n_samples=n_samples, seed=seed, width=GRADUAL_WIDTH, recurring=True
                    )
                else:
                    xs, ys, intervals, meta = generate_regression_incremental(
                        n_samples=n_samples, seed=seed, recurring=True
                    )
                meta["chosen_drift_mode"] = mode
            else:
                raise ValueError(drift_type)

            stem = _stem_reg(drift_type, g_id, mode)
            out_dir = drift_dir("regression", drift_type)
            csv_path = out_dir / f"{stem}.csv"
            txt_path = out_dir / f"{stem}_drift_times.txt"
            write_csv(csv_path, xs, ys, REG_N_FEATURES)
            write_drift_times(txt_path, intervals)
            validate_dataset(
                csv_path,
                txt_path,
                n_samples=n_samples,
                max_transition_width=_cap_for_validate(drift_type, mode),
            )
            row = {
                "task": "regression",
                "drift_type": drift_type,
                "g_id": g_id,
                "stem": stem,
                "seed": seed,
                "n_samples": n_samples,
                "chosen_drift_mode": mode,
                "n_drifts": meta.get("n_drifts"),
                "width": meta.get("width") or meta.get("annotation_width"),
            }
            if drift_type == "recurring":
                write_json(out_dir / f"{stem}.json", {**row, "intervals": intervals, "meta": meta})
                recurring_rows.append(row)
            written.append(row)
            print(f"[regression] wrote {csv_path.name} (n={n_samples})")

            if make_plots and g_id == g_ids[0]:
                _, ys_base = generate_regression_no_drift(n_samples=n_samples, seed=seed)
                plot_stream_overview(
                    csv_path,
                    txt_path,
                    plots_dir("regression") / f"{stem}.png",
                    title=f"regression / {drift_type} / {stem}",
                    task="regression",
                    y_baseline=ys_base,
                )

    if recurring_rows:
        save_recurring_manifest("regression", recurring_rows)
    return written
