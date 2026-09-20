"""Download and convert the six real-world datasets."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_covtype, fetch_openml

from common import (
    RAW_DIR,
    ROOT,
    ensure_layout,
    plot_y,
    rolling_download,
    to_x_columns,
    validate_df,
    write_csv,
    write_meta,
)


def _save_bundle(
    *,
    task: str,
    name: str,
    df: pd.DataFrame,
    meta: dict,
) -> Path:
    validate_df(df, task, name)
    out_dir = ROOT / task / name
    csv_path = out_dir / f"{name}.csv"
    write_csv(csv_path, df)
    write_meta(out_dir / f"{name}_meta.json", meta)
    plot_y(
        df,
        ROOT / task / "drift_plots" / f"{name}_y.png",
        task=task,
        title=f"{task} / {name}",
    )
    print(f"[{task}/{name}] rows={len(df)} cols={df.shape[1]} -> {csv_path}")
    return csv_path


# ---------------------------------------------------------------------------
# binary
# ---------------------------------------------------------------------------


def prepare_ai4i2020() -> Path:
    raw_csv = RAW_DIR / "ai4i2020" / "ai4i2020.csv"
    if not raw_csv.exists():
        try:
            from ucimlrepo import fetch_ucirepo

            print("  fetching AI4I via ucimlrepo id=601")
            ds = fetch_ucirepo(id=601)
            # features + targets
            feat = ds.data.features.copy()
            tgt = ds.data.targets.copy()
            raw = pd.concat([feat, tgt], axis=1)
            raw_csv.parent.mkdir(parents=True, exist_ok=True)
            raw.to_csv(raw_csv, index=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  ucimlrepo failed ({exc}); trying direct zip")
            zpath = RAW_DIR / "ai4i2020" / "ai4i.zip"
            rolling_download(
                "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip",
                zpath,
            )
            with zipfile.ZipFile(zpath) as zf:
                member = next(m for m in zf.namelist() if m.endswith(".csv"))
                raw_csv.parent.mkdir(parents=True, exist_ok=True)
                raw_csv.write_bytes(zf.read(member))

    raw = pd.read_csv(raw_csv)
    # Normalize column names
    cols = {c: c.strip() for c in raw.columns}
    raw = raw.rename(columns=cols)

    # Target: Machine failure
    y_col = None
    for cand in ("Machine failure", "Machine failure ", "machine failure", "Machine_failure"):
        if cand in raw.columns:
            y_col = cand
            break
    if y_col is None:
        # ucimlrepo may already split naming
        for c in raw.columns:
            if "failure" in c.lower() and "twf" not in c.lower() and c.lower() not in {
                "twf", "hdf", "pwf", "osf", "rnf"
            }:
                if raw[c].nunique() <= 2:
                    y_col = c
                    break
    if y_col is None:
        raise RuntimeError(f"AI4I: cannot find Machine failure column in {list(raw.columns)}")

    drop = [y_col, "UDI", "UID", "Product ID", "Product_ID", "TWF", "HDF", "PWF", "OSF", "RNF"]
    # Type is categorical L/M/H -> ordinal
    type_col = None
    for cand in ("Type", "type"):
        if cand in raw.columns:
            type_col = cand
            break

    feat_df = raw.drop(columns=[c for c in drop if c in raw.columns], errors="ignore")
    if type_col and type_col in feat_df.columns:
        mapping = {"L": 0, "M": 1, "H": 2}
        feat_df[type_col] = feat_df[type_col].map(mapping).astype(float)

    # keep only numeric
    feat_df = feat_df.apply(pd.to_numeric, errors="coerce")
    out = feat_df.copy()
    out["y"] = pd.to_numeric(raw[y_col], errors="coerce").astype(int)
    out = out.dropna().reset_index(drop=True)
    out = to_x_columns(out)

    return _save_bundle(
        task="binary",
        name="ai4i2020",
        df=out,
        meta={
            "source": "UCI AI4I 2020 Predictive Maintenance (id=601)",
            "url": "https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset",
            "target": "Machine failure (0/1)",
            "n_rows": int(len(out)),
            "n_features": int(out.shape[1] - 1),
            "preprocessing": [
                "drop id columns (UDI/Product ID)",
                "drop failure-mode detail columns TWF/HDF/PWF/OSF/RNF",
                "Type L/M/H -> ordinal 0/1/2",
                "rename features to x0..",
            ],
        },
    )


def prepare_electricity() -> Path:
    raw_path = RAW_DIR / "electricity" / "electricity.csv"
    if not raw_path.exists():
        print("  fetching Electricity via OpenML (electricity / id often 151)")
        try:
            bunch = fetch_openml(name="electricity", version=1, as_frame=True, parser="auto")
        except Exception:
            bunch = fetch_openml(data_id=151, as_frame=True, parser="auto")
        frame = bunch.frame.copy()
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(raw_path, index=False)

    raw = pd.read_csv(raw_path)
    # target usually 'class' with UP/DOWN or 0/1
    y_col = "class" if "class" in raw.columns else raw.columns[-1]
    y = raw[y_col]
    if y.dtype == object or str(y.dtype) == "category":
        # UP/DOWN
        mapping = {"UP": 1, "DOWN": 0, "up": 1, "down": 0}
        y = y.map(lambda v: mapping.get(str(v), v))
    y = pd.to_numeric(y, errors="coerce")
    # if still 1/2 style
    vals = sorted(y.dropna().unique().tolist())
    if vals == [1, 2] or vals == [1.0, 2.0]:
        y = y.map({1: 0, 2: 1, 1.0: 0, 2.0: 1})

    feats = raw.drop(columns=[y_col])
    # drop date-like if present (keep numeric stream features)
    for c in list(feats.columns):
        if c.lower() in {"date", "day", "period"} and feats[c].dtype == object:
            feats = feats.drop(columns=[c])
    feats = feats.apply(pd.to_numeric, errors="coerce")
    out = feats.copy()
    out["y"] = y.astype(int)
    out = out.dropna().reset_index(drop=True)
    out = to_x_columns(out)

    return _save_bundle(
        task="binary",
        name="electricity",
        df=out,
        meta={
            "source": "OpenML electricity (Elec2)",
            "url": "https://www.openml.org/d/151",
            "target": "class UP/DOWN -> 1/0",
            "n_rows": int(len(out)),
            "n_features": int(out.shape[1] - 1),
            "preprocessing": [
                "map UP/DOWN to 1/0",
                "coerce features numeric",
                "rename features to x0..",
            ],
        },
    )


# ---------------------------------------------------------------------------
# multi
# ---------------------------------------------------------------------------


def prepare_gas_sensor_drift() -> Path:
    """UCI Gas Sensor Array Drift Dataset (id=224), batches concatenated in order."""
    raw_dir = RAW_DIR / "gas_sensor_drift"
    raw_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw_dir / "gas_drift.zip"

    dat_files = sorted(raw_dir.glob("batch*.dat"))
    if not dat_files:
        try:
            from ucimlrepo import fetch_ucirepo

            print("  fetching Gas Sensor Drift via ucimlrepo id=224")
            ds = fetch_ucirepo(id=224)
            # May already be a single table
            feat = ds.data.features.copy()
            tgt = ds.data.targets.copy()
            raw = pd.concat([feat, tgt], axis=1)
            # ensure stream order if Batch exists
            if "BatchID" in raw.columns or "batch" in [c.lower() for c in raw.columns]:
                bcol = "BatchID" if "BatchID" in raw.columns else [c for c in raw.columns if c.lower() == "batch"][0]
                raw = raw.sort_values(bcol).reset_index(drop=True)
            y_col = ds.data.targets.columns[0]
            feats = raw.drop(columns=[y_col], errors="ignore")
            # drop batch id from features if present
            for c in list(feats.columns):
                if "batch" in c.lower():
                    feats = feats.drop(columns=[c])
            feats = feats.apply(pd.to_numeric, errors="coerce")
            out = feats.copy()
            out["y"] = pd.to_numeric(raw[y_col], errors="coerce").astype(int)
            # remap to 0-based if needed
            classes = sorted(out["y"].unique())
            remap = {c: i for i, c in enumerate(classes)}
            out["y"] = out["y"].map(remap).astype(int)
            out = out.dropna().reset_index(drop=True)
            out = to_x_columns(out)
            return _save_bundle(
                task="multi_classification",
                name="gas_sensor_drift",
                df=out,
                meta={
                    "source": "UCI Gas Sensor Array Drift Dataset (id=224)",
                    "url": "https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset",
                    "target": f"gas class remapped 0..{len(classes)-1} from {classes}",
                    "n_rows": int(len(out)),
                    "n_features": int(out.shape[1] - 1),
                    "n_classes": int(out["y"].nunique()),
                    "preprocessing": [
                        "concatenate/keep batch order if available",
                        "drop batch id from features",
                        "remap class labels to 0-based",
                        "rename features to x0..",
                    ],
                },
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  ucimlrepo failed ({exc}); trying zip of .dat batches")
            rolling_download(
                "https://archive.ics.uci.edu/static/public/224/gas+sensor+array+drift+dataset.zip",
                zip_path,
            )
            with zipfile.ZipFile(zip_path) as zf:
                for member in zf.namelist():
                    if member.endswith(".dat") and "batch" in member.lower():
                        target = raw_dir / Path(member).name
                        target.write_bytes(zf.read(member))
            dat_files = sorted(raw_dir.glob("batch*.dat"))

    if not dat_files:
        raise RuntimeError("Gas Sensor Drift: no batch*.dat files found")

    rows: list[dict] = []
    for fp in dat_files:
        # libsvm-like: label f1:v1 f2:v2 ...
        text = fp.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
        for line in text:
            parts = line.strip().split()
            if not parts:
                continue
            label = int(float(parts[0]))
            feats: dict[int, float] = {}
            for tok in parts[1:]:
                if ":" not in tok:
                    continue
                idx, val = tok.split(":", 1)
                feats[int(idx)] = float(val)
            row = {f"f{k}": v for k, v in sorted(feats.items())}
            row["y"] = label
            rows.append(row)

    raw = pd.DataFrame(rows)
    # fill missing feature keys with 0
    feat_cols = [c for c in raw.columns if c != "y"]
    raw[feat_cols] = raw[feat_cols].fillna(0.0)
    classes = sorted(raw["y"].unique())
    remap = {c: i for i, c in enumerate(classes)}
    raw["y"] = raw["y"].map(remap).astype(int)
    out = to_x_columns(raw)
    return _save_bundle(
        task="multi_classification",
        name="gas_sensor_drift",
        df=out,
        meta={
            "source": "UCI Gas Sensor Array Drift Dataset (.dat batches)",
            "url": "https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset",
            "target": f"gas class remapped 0..{len(classes)-1} from {classes}",
            "n_rows": int(len(out)),
            "n_features": int(out.shape[1] - 1),
            "n_classes": int(out["y"].nunique()),
            "preprocessing": [
                "concatenate batch1..batchN in filename order",
                "parse libsvm .dat",
                "remap labels to 0-based",
                "rename features to x0..",
            ],
        },
    )


def prepare_covertype() -> Path:
    print("  fetching Covertype via sklearn.fetch_covtype")
    bunch = fetch_covtype(as_frame=False, shuffle=False)
    X = bunch.data
    y = bunch.target  # 1..7
    # 0-based labels
    y0 = y.astype(int) - 1
    cols = {f"x{i}": X[:, i] for i in range(X.shape[1])}
    cols["y"] = y0
    out = pd.DataFrame(cols)
    # Covertype is large (~581k); keep full stream (no shuffle)
    return _save_bundle(
        task="multi_classification",
        name="covertype",
        df=out,
        meta={
            "source": "sklearn.datasets.fetch_covtype (UCI Covertype)",
            "url": "https://archive.ics.uci.edu/dataset/31/covertype",
            "target": "cover_type remapped to 0..6 (original 1..7)",
            "n_rows": int(len(out)),
            "n_features": int(out.shape[1] - 1),
            "n_classes": int(out["y"].nunique()),
            "preprocessing": [
                "shuffle=False to preserve original order",
                "labels 1..7 -> 0..6",
                "features named x0..",
            ],
        },
    )


# ---------------------------------------------------------------------------
# regression
# ---------------------------------------------------------------------------


def prepare_metro_interstate_traffic() -> Path:
    """UCI Metro Interstate Traffic Volume (id=492) — hourly traffic regression.

    Common real-world time-series regression benchmark (not high-frequency).
    y = traffic_volume; keep temporal order by date_time.
    """
    raw_dir = RAW_DIR / "metro_interstate_traffic"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_csv = raw_dir / "Metro_Interstate_Traffic_Volume.csv"

    if not raw_csv.exists():
        try:
            from ucimlrepo import fetch_ucirepo

            print("  fetching Metro Interstate Traffic via ucimlrepo id=492")
            ds = fetch_ucirepo(id=492)
            feat = ds.data.features.copy()
            tgt = ds.data.targets.copy()
            raw = pd.concat([feat, tgt], axis=1)
            # date_time may be in features
            raw.to_csv(raw_csv, index=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  ucimlrepo failed ({exc}); trying UCI csv.gz")
            gz_path = raw_dir / "Metro_Interstate_Traffic_Volume.csv.gz"
            rolling_download(
                "https://archive.ics.uci.edu/ml/machine-learning-databases/00492/Metro_Interstate_Traffic_Volume.csv.gz",
                gz_path,
            )
            raw = pd.read_csv(gz_path)
            raw.to_csv(raw_csv, index=False)

    raw = pd.read_csv(raw_csv)
    # Normalize column names
    colmap = {c: c.strip() for c in raw.columns}
    raw = raw.rename(columns=colmap)

    time_col = None
    for cand in ("date_time", "datetime", "DateTime"):
        if cand in raw.columns:
            time_col = cand
            break
    if time_col is not None:
        raw[time_col] = pd.to_datetime(raw[time_col], errors="coerce")
        raw = raw.sort_values(time_col).reset_index(drop=True)

    y_col = None
    for cand in ("traffic_volume", "Traffic_Volume", "trafficvolume"):
        if cand in raw.columns:
            y_col = cand
            break
    if y_col is None:
        raise RuntimeError(f"Metro traffic: cannot find traffic_volume in {list(raw.columns)}")

    drop = {y_col}
    if time_col:
        drop.add(time_col)

    feats = raw.drop(columns=[c for c in drop if c in raw.columns], errors="ignore")
    # Encode categoricals (holiday, weather_main, weather_description) as ordinal codes
    for c in list(feats.columns):
        if feats[c].dtype == object or str(feats[c].dtype) == "category":
            feats[c] = feats[c].astype("category").cat.codes.astype(float)

    feats = feats.apply(pd.to_numeric, errors="coerce")
    out = feats.copy()
    out["y"] = pd.to_numeric(raw[y_col], errors="coerce").astype(float)
    out = out.dropna().reset_index(drop=True)
    out = to_x_columns(out)

    return _save_bundle(
        task="regression",
        name="metro_interstate_traffic",
        df=out,
        meta={
            "source": "UCI Metro Interstate Traffic Volume (id=492)",
            "url": "https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume",
            "target": "traffic_volume (hourly)",
            "n_rows": int(len(out)),
            "n_features": int(out.shape[1] - 1),
            "preprocessing": [
                "sort by date_time (hourly stream order)",
                "drop date_time from features",
                "categorical holiday/weather_* -> category codes",
                "y = traffic_volume",
                "rename features to x0..",
            ],
            "sampling": "hourly (not high-frequency)",
            "replaced": "gas_sensor_dynamic_mixtures (~100Hz subsampled)",
        },
    )


def prepare_bike_sharing() -> Path:
    raw_dir = RAW_DIR / "bike_sharing"
    raw_dir.mkdir(parents=True, exist_ok=True)
    hour_csv = raw_dir / "hour.csv"

    if not hour_csv.exists():
        try:
            from ucimlrepo import fetch_ucirepo

            print("  fetching Bike Sharing via ucimlrepo id=275")
            ds = fetch_ucirepo(id=275)
            feat = ds.data.features.copy()
            tgt = ds.data.targets.copy()
            raw = pd.concat([feat, tgt], axis=1)
            raw.to_csv(hour_csv, index=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  ucimlrepo failed ({exc}); trying zip")
            zpath = raw_dir / "bike.zip"
            rolling_download(
                "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip",
                zpath,
            )
            with zipfile.ZipFile(zpath) as zf:
                member = next(m for m in zf.namelist() if m.endswith("hour.csv"))
                hour_csv.write_bytes(zf.read(member))

    raw = pd.read_csv(hour_csv)
    # Prefer hourly stream ordered by instant / dteday+hr
    if "instant" in raw.columns:
        raw = raw.sort_values("instant").reset_index(drop=True)
    elif {"dteday", "hr"}.issubset(raw.columns):
        raw = raw.sort_values(["dteday", "hr"]).reset_index(drop=True)

    y_col = "cnt" if "cnt" in raw.columns else ("count" if "count" in raw.columns else None)
    if y_col is None:
        # ucimlrepo targets
        for c in raw.columns:
            if c.lower() in {"cnt", "count"}:
                y_col = c
                break
    if y_col is None:
        raise RuntimeError(f"Bike Sharing: cannot find cnt column in {list(raw.columns)}")

    drop = {
        y_col,
        "instant",
        "dteday",
        "casual",
        "registered",  # leakage toward cnt
    }
    feats = raw.drop(columns=[c for c in drop if c in raw.columns], errors="ignore")
    feats = feats.apply(pd.to_numeric, errors="coerce")
    out = feats.copy()
    out["y"] = pd.to_numeric(raw[y_col], errors="coerce").astype(float)
    out = out.dropna().reset_index(drop=True)
    out = to_x_columns(out)

    return _save_bundle(
        task="regression",
        name="bike_sharing",
        df=out,
        meta={
            "source": "UCI Bike Sharing Dataset (hour.csv)",
            "url": "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset",
            "target": "cnt (hourly rental count)",
            "n_rows": int(len(out)),
            "n_features": int(out.shape[1] - 1),
            "preprocessing": [
                "use hour.csv; sort by instant (time order)",
                "drop instant/dteday/casual/registered (leakage)",
                "y = cnt",
                "rename features to x0..",
            ],
        },
    )


DATASETS: dict[str, dict[str, Callable[[], Path]]] = {
    "binary": {
        "ai4i2020": prepare_ai4i2020,
        "electricity": prepare_electricity,
    },
    "multi_classification": {
        "gas_sensor_drift": prepare_gas_sensor_drift,
        "covertype": prepare_covertype,
    },
    "regression": {
        "metro_interstate_traffic": prepare_metro_interstate_traffic,
        "bike_sharing": prepare_bike_sharing,
    },
}
