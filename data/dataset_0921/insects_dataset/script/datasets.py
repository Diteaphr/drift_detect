"""Convert downloaded Insects CSVs into experiment format."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from common import (
    CHANGE_POINTS,
    GDRIVE_IDS,
    PAPER_NAME,
    RAW_DIR,
    ROOT,
    TEMPERATURE_DESC,
    ensure_layout,
    plot_y_with_drifts,
    points_to_intervals,
    to_x_columns,
    write_drift_times,
    write_meta,
)


def _download_raw(name: str) -> Path:
    raw = RAW_DIR / f"{name}.csv"
    if raw.exists() and raw.stat().st_size > 10_000:
        return raw
    import gdown

    fid = GDRIVE_IDS[name]
    print(f"  downloading {name} via gdown")
    gdown.download(f"https://drive.google.com/uc?id={fid}", str(raw), quiet=False, fuzzy=True)
    return raw


def prepare_variant(name: str) -> Path:
    ensure_layout()
    raw_path = _download_raw(name)
    raw = pd.read_csv(raw_path, header=None)
    y_raw = raw.iloc[:, -1]
    classes = sorted(y_raw.unique().tolist())
    remap = {c: i for i, c in enumerate(classes)}
    feats = raw.iloc[:, :-1].apply(pd.to_numeric, errors="coerce")
    out = feats.copy()
    out["y"] = y_raw.map(remap).astype(int)
    out = out.dropna().reset_index(drop=True)
    out = to_x_columns(out)

    n = len(out)
    points = list(CHANGE_POINTS.get(name, []))
    intervals = points_to_intervals(points, n)

    out_dir = ROOT / "multi_classification" / name
    csv_path = out_dir / f"{name}.csv"
    drift_path = out_dir / f"{name}_drift_times.txt"
    meta_path = out_dir / f"{name}_meta.json"
    plot_path = ROOT / "multi_classification" / "drift_plots" / f"{name}_y.png"

    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv_path, index=False)
    write_drift_times(drift_path, intervals)
    write_meta(
        meta_path,
        {
            "source": "USP Insects stream (Souza et al. 2020)",
            "url_paper": "https://arxiv.org/abs/2005.00113",
            "url_repo": "https://sites.google.com/view/uspdsrepository",
            "variant": name,
            "paper_name": PAPER_NAME.get(name, name),
            "temperature_drift_description": TEMPERATURE_DESC.get(name, ""),
            "task": "multi_classification",
            "n_rows": int(n),
            "n_features": int(out.shape[1] - 1),
            "n_classes": int(out["y"].nunique()),
            "original_class_codes": classes,
            "class_remap": {str(k): int(v) for k, v in remap.items()},
            "change_points_paper_table2": points,
            "drift_times_format": "[[t, t], ...] from published change points; empty if continuous",
            "has_groundtruth_drift": True,
            "note": (
                "Separated from data/real_dataset because Insects provides "
                "published concept-drift change points (Table 2). "
                "Balanced variants only (imbal. / out-of-control omitted)."
            ),
            "preprocessing": [
                "features + class from USP/River CSV (no header)",
                "remap class labels to 0-based contiguous ids",
                "rename features to x0..",
                "write drift_times from Souza et al. 2020 Table 2",
            ],
        },
    )
    plot_y_with_drifts(out, intervals, plot_path, title=f"insects / {name}")
    print(f"[insects/{name}] rows={n} drifts={len(intervals)} -> {csv_path}")
    return csv_path


def prepare_all(names: list[str] | None = None) -> list[Path]:
    ensure_layout()
    selected = names if names is not None else list(GDRIVE_IDS.keys())
    paths: list[Path] = []
    for name in selected:
        if name not in GDRIVE_IDS:
            raise SystemExit(f"Unknown variant: {name}. Choices: {list(GDRIVE_IDS)}")
        paths.append(prepare_variant(name))
    return paths
