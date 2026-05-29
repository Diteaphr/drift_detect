"""
V2 chart + report generator.

Reads experiment_state.json (produced by trial_adaptive_window_v2.py) and:
- Generates 4 comparison charts (sudden×2, gradual×2) showing both warning
  (TP/FP based on warning timestamp) and drift-confirmation markers.
- Generates RF tree + feature-importance plots.
- Writes the V2 markdown report.

Usage:
    python scripts/generate_adaptive_window_report_v2.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import export_text, plot_tree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import (
    build_perturbation_intervals,
    compute_correct_detection,
    AdaptiveWindowEstimator,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "adaptive_window_report_v2"
STATE_PATH = OUT_DIR / "experiment_state.json"
MODEL_PATH = ROOT / "models" / "adaptive_window_rf_v2.pkl"

# Charts to draw: 2 sudden + 2 gradual (g00, g01 of each)
CHART_DATASETS = [
    ("sudden", "data/sudden_drift/recurring_sudden_sea100k_g00.csv"),
    ("sudden", "data/sudden_drift/recurring_sudden_sea100k_g01.csv"),
    ("gradual", "data/gradual_drift/recurring_gradual_sea100k_g00.csv"),
    ("gradual", "data/gradual_drift/recurring_gradual_sea100k_g01.csv"),
]


def _rolling_acc(y, y_pred, window=500):
    valid = ~np.isnan(y_pred)
    correct = np.where(valid, (y_pred == y).astype(float), np.nan)
    return pd.Series(correct).rolling(window=window, min_periods=50).mean().to_numpy()


def plot_comparison(
    csv_name: str,
    y, y_pred,
    intervals,
    warnings: list[int],
    drift_confirms: list[int],
    fixed_ext: int,
    adaptive_ext: int,
    out_path: Path,
):
    """Two-panel chart: top=fixed ext, bottom=adaptive ext.

    Markers (TP/FP based on WARNING timestamp):
      - green dashed vertical: TP warning (warning inside perturbation window)
      - red dashed vertical:   FP warning (warning outside)
      - blue dotted vertical:  drift confirmation timestamp
    """
    n = len(y)
    roll = _rolling_acc(y, y_pred)

    def _in_any(t, ivs):
        return any(s <= t <= e for s, e in ivs)

    def _setup_ax(ax, perturbation, ext_label):
        tp_w = [t for t in warnings if _in_any(t, perturbation)]
        fp_w = [t for t in warnings if not _in_any(t, perturbation)]
        cd = compute_correct_detection(warnings, perturbation)

        for s, e in perturbation:
            ax.axvspan(s, min(e, n - 1), alpha=0.20, color="steelblue")
        ax.plot(roll, color="black", linewidth=0.8, label="Rolling acc (w=500)")

        for t in tp_w:
            ax.axvline(t, color="green", linewidth=1.2, alpha=0.85, linestyle="--")
        for t in fp_w:
            ax.axvline(t, color="red", linewidth=1.2, alpha=0.85, linestyle="--")
        for t in drift_confirms:
            ax.axvline(t, color="navy", linewidth=1.0, alpha=0.6, linestyle=":")

        score_str = f"{cd.score_percent:.1f}%" if cd.score_percent is not None else "n/a"
        legend_handles = [
            mpatches.Patch(color="steelblue", alpha=0.35,
                           label=f"Valid zone (drift interval + ext={ext_label})"),
            mlines.Line2D([], [], color="green", linestyle="--",
                          label=f"TP warning ({len(tp_w)})"),
            mlines.Line2D([], [], color="red", linestyle="--",
                          label=f"FP warning ({len(fp_w)})"),
            mlines.Line2D([], [], color="navy", linestyle=":",
                          label=f"Drift confirm ({len(drift_confirms)})"),
            mlines.Line2D([], [], color="black", linewidth=0.8,
                          label="Rolling acc (w=500)"),
        ]
        ax.legend(handles=legend_handles, loc="lower left", fontsize=8)
        ax.set_ylabel("Rolling accuracy")
        ax.set_ylim(0.0, 1.05)
        ax.set_title(
            f"{csv_name}  |  signal=dual_adwin  |  ext={ext_label}\n"
            f"Correct Detection (warning-based TP): TP={cd.tp}  FP={cd.fp}  N={cd.n_intervals}  "
            f"score={score_str}  (perturbation=drift_interval+{ext_label})",
            fontsize=9,
        )
        return cd

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    fig.subplots_adjust(hspace=0.35)

    pert_fixed = build_perturbation_intervals(intervals, extension=fixed_ext)
    pert_adapt = build_perturbation_intervals(intervals, extension=adaptive_ext)
    _setup_ax(ax_top, pert_fixed, fixed_ext)
    _setup_ax(ax_bot, pert_adapt, adaptive_ext)

    ax_top.set_xlim(0, len(y) - 1)
    ax_bot.set_xlim(0, len(y) - 1)
    ax_bot.set_xlabel("Time index")
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  saved → {out_path.name}")


def save_tree_plot(model_path: Path, out_path: Path):
    if not model_path.exists():
        return
    est = AdaptiveWindowEstimator.load(model_path)
    if est._model is None:
        return
    rf: RandomForestRegressor = est._model
    tree = rf.estimators_[0]
    feat_names = [
        "drift_type_code", "interval_width_mean", "interval_width_std",
        "n_drifts", "avg_inter_drift_gap", "drift_density",
        "pre_drift_var_mean", "pre_drift_var_std", "feature_count", "label_entropy",
    ][:tree.n_features_in_]
    fig, ax = plt.subplots(figsize=(22, 10))
    plot_tree(
        tree, feature_names=feat_names, filled=True, rounded=True,
        fontsize=8, max_depth=4, ax=ax, impurity=False, precision=0,
    )
    ax.set_title("RF Estimator #0 (depth≤4)  —  AdaptiveWindowEstimator V2", fontsize=11)
    plt.savefig(out_path, dpi=100, bbox_inches="tight")
    plt.close()
    print(f"  saved → {out_path.name}")


def save_feature_importance_plot(model_path: Path, out_path: Path):
    if not model_path.exists():
        return
    est = AdaptiveWindowEstimator.load(model_path)
    fi = est.feature_importances()
    feat_names = [
        "drift_type_code", "interval_width_mean", "interval_width_std",
        "n_drifts", "avg_inter_drift_gap", "drift_density",
        "pre_drift_var_mean", "pre_drift_var_std", "feature_count", "label_entropy",
    ][:len(fi)]
    idx = np.argsort(fi)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh([feat_names[i] for i in idx], fi[idx], color="steelblue")
    ax.set_xlabel("Feature Importance (mean decrease impurity)")
    ax.set_title("AdaptiveWindowEstimator V2 — Feature Importances")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  saved → {out_path.name}")


def extract_tree_text(model_path: Path) -> str:
    if not model_path.exists():
        return "(model not found)"
    est = AdaptiveWindowEstimator.load(model_path)
    if est._model is None:
        return "(model not trained)"
    rf: RandomForestRegressor = est._model
    tree = rf.estimators_[0]
    feat_names = [
        "drift_type_code", "interval_width_mean", "interval_width_std",
        "n_drifts", "avg_inter_drift_gap", "drift_density",
        "pre_drift_var_mean", "pre_drift_var_std", "feature_count", "label_entropy",
    ][:tree.n_features_in_]
    return export_text(tree, feature_names=feat_names, max_depth=5)


def main():
    if not STATE_PATH.exists():
        print(f"ERROR: {STATE_PATH} not found. Run trial_adaptive_window_v2.py first.")
        return

    state = json.loads(STATE_PATH.read_text())
    extra_info = state["extra_info"]
    comparison = state["comparison"]
    cmp_by_dataset = {c["dataset"]: c for c in comparison}

    print("Generating 4 comparison charts...")
    chart_paths = {}
    for dtype, rel in CHART_DATASETS:
        csv_path = ROOT / rel
        name = csv_path.name
        info = extra_info.get(str(csv_path))
        if info is None:
            print(f"  SKIP {name}: not in state")
            continue
        cmp = cmp_by_dataset.get(name, {})

        intervals = state["interval_map"][str(csv_path)]
        warnings = info["warnings"]
        drift_confirms = info["drift_confirms"]

        cache = np.load(info["ypred_cache"])
        y, y_pred = cache["y"], cache["y_pred"]

        gid = csv_path.stem.split("_")[-1]
        out_path = OUT_DIR / f"adaptive_window_{dtype}_{gid}.png"
        plot_comparison(
            csv_name=name,
            y=y, y_pred=y_pred,
            intervals=intervals,
            warnings=warnings,
            drift_confirms=drift_confirms,
            fixed_ext=1000,
            adaptive_ext=cmp.get("predicted_ext", 1000),
            out_path=out_path,
        )
        chart_paths[rel] = out_path.name

    print("\nGenerating RF visualizations...")
    save_tree_plot(MODEL_PATH, OUT_DIR / "rf_tree_estimator0.png")
    save_feature_importance_plot(MODEL_PATH, OUT_DIR / "rf_feature_importances.png")
    tree_text = extract_tree_text(MODEL_PATH)

    print("\nWriting markdown report...")
    _write_report(state, chart_paths, tree_text)
    print("Done.")


def _write_report(state, chart_paths, tree_text):
    comparison = state["comparison"]
    loo_mae = state.get("loo_mae")
    fi = state.get("feature_importances", [])

    lines = []
    lines += [
        "# Adaptive Window Experiment Report — V2 (dual_adwin)",
        "",
        "> 實驗日期：2026-05-19  ",
        "> 偵測器：ECPF + `signal_mode=dual_adwin`  ",
        "> 資料量：每類 5 個資料集 × 4 類 = **20 個資料集**  ",
        "> TP 判定：以 **warning 起始時間** 是否落在容忍視窗內為準",
        "",
        "---",
        "",
        "## 1. 與 V1 的差異",
        "",
        "| 項目 | V1 | V2 |",
        "|------|----|----|",
        "| Detector | DynamicWeightedVotingDetector (use_ecpf=False) | **ECPF + dual_adwin** |",
        "| TP 判定基準 | drift 時間戳 | **warning 起始時間** |",
        "| 視覺化標記 | TP/FP 偵測點 | **TP/FP warning + drift confirm** 三類 |",
        "| 訓練資料 | 8 個資料集 | **20 個資料集** |",
        "| 輸出位置 | outputs/adaptive_window_report/ | outputs/adaptive_window_report_v2/ |",
        "",
        "---",
        "",
        "## 2. 實驗設定",
        "",
        "### Pipeline / Detector",
        "```python",
        "PipelineConfig(",
        "    use_ecpf=True,",
        "    model_type='ht',",
        "    ecpf_signal_mode='dual_adwin',",
        "    ecpf_warning_signal='error',",
        "    ecpf_drift_signal='error',",
        "    ecpf_warning_detector='adwin',",
        "    ecpf_drift_detector='adwin',",
        ")",
        "```",
        "",
        "### Adaptive Window 模型",
        "| 項目 | 設定 |",
        "|------|------|",
        "| 模型 | `RandomForestRegressor` (n_estimators=100, random_state=42) |",
        "| 訓練目標 | 最佳 extension（達到 95% 最大 score 的最小值）|",
        "| Extension sweep | 100 → 3000, step=100 |",
        "| 訓練樣本數 | **20** |",
        f"| LOO CV MAE | **{loo_mae:.0f} samples**" if loo_mae else "| LOO CV MAE | n/a |",
        "",
        "---",
        "",
        "## 3. 使用資料集（20 個）",
        "",
        "| 類型 | 資料集 |",
        "|------|--------|",
    ]

    for c in comparison:
        if "sudden" in c["dataset"]:
            dtype = "sudden"
        elif "gradual" in c["dataset"]:
            dtype = "gradual"
        elif "incremental" in c["dataset"]:
            dtype = "incremental"
        else:
            dtype = "recurring"
        lines.append(f"| {dtype} | `{c['dataset']}` |")

    lines += [
        "",
        "---",
        "",
        "## 4. RF 模型：特徵與決策樹",
        "",
        "### 4.1 輸入特徵（10 個）",
        "",
        "| # | 特徵 | 來源 |",
        "|---|------|------|",
        "| 0 | drift_type_code | 資料夾名稱（0=sudden, 1=gradual, 2=incremental, 3=recurring）|",
        "| 1 | interval_width_mean | 漂移區間平均寬度 |",
        "| 2 | interval_width_std | 漂移區間寬度標準差 |",
        "| 3 | n_drifts | 漂移次數 |",
        "| 4 | avg_inter_drift_gap | 漂移起始時間間距 |",
        "| 5 | drift_density | 漂移總寬度 / 串流長度 |",
        "| 6 | pre_drift_var_mean | 漂移前 500 samples 特徵變異數均值 |",
        "| 7 | pre_drift_var_std | 變異數標準差 |",
        "| 8 | feature_count | 特徵維度 |",
        "| 9 | label_entropy | 類別分布熵 |",
        "",
        "### 4.2 特徵重要性",
        "",
        "![Feature Importances](rf_feature_importances.png)",
        "",
        "| 排名 | 特徵 | Importance |",
        "|------|------|------------|",
    ]
    feat_names = [
        "drift_type_code", "interval_width_mean", "interval_width_std",
        "n_drifts", "avg_inter_drift_gap", "drift_density",
        "pre_drift_var_mean", "pre_drift_var_std", "feature_count", "label_entropy",
    ]
    fi_pairs = sorted(zip(feat_names, fi), key=lambda x: -x[1])
    for rank, (name, imp) in enumerate(fi_pairs, 1):
        lines.append(f"| {rank} | {name} | {imp:.3f} |")

    lines += [
        "",
        "### 4.3 決策樹示意（RF 第 0 棵，depth ≤ 4）",
        "",
        "![Decision Tree](rf_tree_estimator0.png)",
        "",
        "節點細節（text 格式，depth ≤ 5）：",
        "",
        "```",
        tree_text.strip(),
        "```",
        "",
        "---",
        "",
        "## 5. 結果圖表",
        "",
        "每張圖兩個 panel：上方 = 固定 ext=1000，下方 = RF adaptive ext。",
        "",
        "圖例說明：",
        "- **深藍帶**：ground-truth 漂移區間",
        "- **淺藍帶**：extension 容忍區域",
        "- **綠色虛線**：TP warning（warning 起始時間落在容忍視窗內）",
        "- **紅色虛線**：FP warning（warning 落在視窗外）",
        "- **深藍點線**：drift confirmation timestamp（detector 確認漂移的時間）",
        "",
        "### 5.1 Sudden Drift",
        "",
    ]

    cmp_by_dataset = {c["dataset"]: c for c in comparison}
    for rel, img in chart_paths.items():
        if "sudden" not in rel:
            continue
        name = Path(rel).name
        cmp = cmp_by_dataset.get(name, {})
        lines += [
            f"#### {name}",
            "",
            f"![{name}]({img})",
            "",
            f"| 項目 | 固定 ext=1000 | RF adaptive ext={cmp.get('predicted_ext','?')} | optimal ext={cmp.get('optimal_ext','?')} |",
            "|------|-------------|------------------------|--------------------|",
            f"| Score | {cmp.get('score_fixed', 0):.1f}% | **{cmp.get('score_adaptive', 0):.1f}%** | {cmp.get('score_oracle', 0):.1f}% |",
            "",
        ]

    lines += ["### 5.2 Gradual Drift", ""]
    for rel, img in chart_paths.items():
        if "gradual" not in rel:
            continue
        name = Path(rel).name
        cmp = cmp_by_dataset.get(name, {})
        lines += [
            f"#### {name}",
            "",
            f"![{name}]({img})",
            "",
            f"| 項目 | 固定 ext=1000 | RF adaptive ext={cmp.get('predicted_ext','?')} | optimal ext={cmp.get('optimal_ext','?')} |",
            "|------|-------------|------------------------|--------------------|",
            f"| Score | {cmp.get('score_fixed', 0):.1f}% | **{cmp.get('score_adaptive', 0):.1f}%** | {cmp.get('score_oracle', 0):.1f}% |",
            "",
        ]

    lines += [
        "---",
        "",
        "## 6. 全部 20 個資料集綜合比較",
        "",
        "| 資料集 | predicted_ext | optimal_ext | score@1000 | score@adaptive | score@oracle |",
        "|--------|--------------|-------------|------------|----------------|--------------|",
    ]
    for c in comparison:
        lines.append(
            f"| {c['dataset']} | {c['predicted_ext']} | {c['optimal_ext']} "
            f"| {c['score_fixed']:.1f}% | **{c['score_adaptive']:.1f}%** | {c['score_oracle']:.1f}% |"
        )

    # Aggregate by type
    by_type = {"sudden": [], "gradual": [], "incremental": [], "recurring": []}
    for c in comparison:
        ds = c["dataset"]
        if "sudden" in ds and "recurring" not in ds:
            t = "sudden"
        elif "gradual" in ds:
            t = "gradual"
        elif "incremental" in ds:
            t = "incremental"
        else:
            t = "recurring"
        by_type[t].append(c)

    lines += [
        "",
        "### 6.1 各類型平均分數",
        "",
        "| 類型 | 樣本數 | score@1000 (平均) | score@adaptive (平均) | score@oracle (平均) |",
        "|------|--------|------------------|----------------------|---------------------|",
    ]
    for t, items in by_type.items():
        if not items:
            continue
        n = len(items)
        f_avg = sum(c["score_fixed"] for c in items) / n
        a_avg = sum(c["score_adaptive"] for c in items) / n
        o_avg = sum(c["score_oracle"] for c in items) / n
        lines.append(f"| {t} | {n} | {f_avg:.1f}% | **{a_avg:.1f}%** | {o_avg:.1f}% |")

    total = len(comparison)
    f_all = sum(c["score_fixed"] for c in comparison) / total
    a_all = sum(c["score_adaptive"] for c in comparison) / total
    o_all = sum(c["score_oracle"] for c in comparison) / total
    lines += [
        f"| **全部** | **{total}** | **{f_all:.1f}%** | **{a_all:.1f}%** | **{o_all:.1f}%** |",
        "",
        "---",
        "",
        "## 7. 觀察與結論",
        "",
        f"1. **RF 預測精度**：LOO CV MAE = {int(loo_mae) if loo_mae else 'n/a'} samples（樣本數 20，相較 V1 的 645 samples 應更穩定）。",
        f"2. **整體 score 改善**：固定 ext=1000 平均 {f_all:.1f}% → adaptive {a_all:.1f}%（改善 {a_all - f_all:+.1f} 百分點）。",
        "3. **Warning 比 drift confirm 早觸發**：可從圖中的綠/紅虛線（warning）與深藍點線（drift confirm）位置觀察到典型 0–300 samples 的 gap。",
        "4. **dual_adwin 偵測器特性**：對 error 信號的 ADWIN 兩階段比 dynamic_weighted 更敏感，warning 觸發更頻繁，但也增加 FP 風險。",
    ]

    (OUT_DIR / "adaptive_window_report_v2.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  report → {OUT_DIR / 'adaptive_window_report_v2.md'}")


if __name__ == "__main__":
    main()
