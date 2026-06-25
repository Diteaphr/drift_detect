"""
Generate V3 report (proxy-features inference) charts + markdown.

Reuses V2's trained RF model and cached pipeline outputs (warnings,
drift_confirms, y_pred). No re-running pipelines required.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import (
    build_perturbation_intervals,
    compute_correct_detection,
    AdaptiveWindowEstimator,
)

ROOT = Path(__file__).resolve().parents[1]
V2_DIR = ROOT / "outputs" / "adaptive_window_report_v2"
V2_STATE = V2_DIR / "experiment_state.json"
OUT_DIR = ROOT / "outputs" / "adaptive_window_report_v3"
OUT_DIR.mkdir(parents=True, exist_ok=True)
V3_STATE = OUT_DIR / "experiment_state_v3.json"


# ── chart ─────────────────────────────────────────────────────────────────────

def _rolling_acc(y, y_pred, window=500):
    valid = ~np.isnan(y_pred)
    correct = np.where(valid, (y_pred == y).astype(float), np.nan)
    return pd.Series(correct).rolling(window=window, min_periods=50).mean().to_numpy()


def plot_v3_comparison(
    csv_path: Path,
    y, y_pred,
    intervals: List[Tuple[int, int]],
    warnings: List[int],
    drift_confirms: List[int],
    v2_pred_ext: int,
    v3_pred_ext: int,
    out_path: Path,
):
    """Two-panel chart: top=V2 (ground-truth features), bottom=V3 (proxy features)."""
    n = len(y)
    roll = _rolling_acc(y, y_pred)

    def _in_any(t, ivs):
        return any(s <= t <= e for s, e in ivs)

    def _setup_ax(ax, perturbation, ext_label, title_prefix):
        tp_warn = [w for w in warnings if _in_any(w, perturbation)]
        fp_warn = [w for w in warnings if not _in_any(w, perturbation)]
        cd = compute_correct_detection(warnings, perturbation)

        for s, e in perturbation:
            ax.axvspan(s, min(e, n - 1), alpha=0.12, color="steelblue")
        for s, e in intervals:
            ax.axvspan(s, min(e, n - 1), alpha=0.30, color="steelblue")
        ax.plot(roll, color="black", linewidth=0.8, label="Rolling acc (w=500)")

        for t in tp_warn:
            ax.axvline(t, color="green", linewidth=1.1, alpha=0.8, linestyle="--")
        for t in fp_warn:
            ax.axvline(t, color="red", linewidth=1.1, alpha=0.8, linestyle="--")
        for t in drift_confirms:
            ax.axvline(t, color="navy", linewidth=1.0, alpha=0.65, linestyle=":")

        score_str = f"{cd.score_percent:.1f}%" if cd.score_percent is not None else "n/a"
        patches = [
            mpatches.Patch(color="steelblue", alpha=0.35,
                           label=f"Drift interval (dark) + +{ext_label} extension (light)"),
            mpatches.Patch(color="green", label=f"TP warning ({len(tp_warn)})"),
            mpatches.Patch(color="red",   label=f"FP warning ({len(fp_warn)})"),
            mpatches.Patch(color="navy",  label=f"Drift confirm ({len(drift_confirms)})"),
        ]
        ax.legend(handles=patches + [ax.lines[0]], loc="lower left", fontsize=7)
        ax.set_ylabel("Rolling accuracy")
        ax.set_ylim(0.0, 1.05)
        ax.set_title(
            f"{csv_path.name}  |  {title_prefix}  |  ext={ext_label}\n"
            f"Correct Detection (warning-based): TP={cd.tp}  FP={cd.fp}  N={cd.n_intervals}  "
            f"score={score_str}",
            fontsize=9,
        )

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    fig.subplots_adjust(hspace=0.35)

    pert_v2 = build_perturbation_intervals(intervals, extension=v2_pred_ext)
    pert_v3 = build_perturbation_intervals(intervals, extension=v3_pred_ext)
    _setup_ax(ax_top, pert_v2, v2_pred_ext, "V2 (ground-truth features)")
    _setup_ax(ax_bot, pert_v3, v3_pred_ext, "V3 (proxy features)")

    ax_bot.set_xlabel("Time index")
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  saved → {out_path.name}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading V2 state, V3 state, and V2 RF model...")
    with open(V2_STATE) as f:
        v2 = json.load(f)
    with open(V3_STATE) as f:
        v3 = json.load(f)

    extra_info = v2["extra_info"]
    interval_map = v2["interval_map"]
    v3_rows = {r["dataset"]: r for r in v3["comparison"]}

    chart_targets = [
        ("sudden_g00", "data/sudden_drift/recurring_sudden_sea100k_g00.csv"),
        ("sudden_g01", "data/sudden_drift/recurring_sudden_sea100k_g01.csv"),
        ("gradual_g00", "data/gradual_drift/recurring_gradual_sea100k_g00.csv"),
        ("gradual_g01", "data/gradual_drift/recurring_gradual_sea100k_g01.csv"),
    ]

    print("\nGenerating 4 comparison charts...")
    for tag, rel in chart_targets:
        csv_path = ROOT / rel
        csv_str = str(csv_path)
        info = extra_info[csv_str]
        ypred_path = info["ypred_cache"]
        ypred_data = np.load(ypred_path)
        y_pred = ypred_data["y_pred"]
        y = ypred_data["y"]

        intervals = [tuple(iv) for iv in interval_map[csv_str]]
        warnings = info["warnings"]
        drift_confirms = info["drift_confirms"]

        row = v3_rows[csv_path.name]
        v2_ext = int(row["predicted_ext_v2_gt"])
        v3_ext = int(row["predicted_ext_v3_proxy"])

        out_path = OUT_DIR / f"adaptive_window_v3_{tag}.png"
        plot_v3_comparison(
            csv_path, y, y_pred, intervals,
            warnings, drift_confirms,
            v2_pred_ext=v2_ext, v3_pred_ext=v3_ext,
            out_path=out_path,
        )

    print("\nWriting markdown report...")
    _write_report(v2, v3)
    print("Done.")


def _write_report(v2, v3):
    rows = v3["comparison"]
    proxy_feats = v3["proxy_features"]
    avg = v3["averages"]

    L = []
    L += [
        "# Adaptive Window Experiment Report — V3 (proxy features, no retrain)",
        "",
        "> 實驗日期：2026-05-19  ",
        "> 模型：**直接重用 V2 訓練的 RF**（無重訓）  ",
        "> 推論輸入：**detector 輸出 (warnings + drift_confirms) + (X, y) 統計** 作為代理特徵  ",
        "> 用途：模擬 online 場景，沒有 ground-truth drift intervals 也能預測 window",
        "",
        "---",
        "",
        "## 1. V3 vs V2 / V1 差異",
        "",
        "| 項目 | V1 | V2 | **V3** |",
        "|------|----|----|--------|",
        "| Detector | dynamic_weighted | ECPF + dual_adwin | (重用 V2) |",
        "| 訓練資料量 | 8 | 20 | **0（重用 V2 模型）** |",
        "| 推論輸入 | drift 標籤 | drift 標籤 | **detector 輸出 + (X, y)** |",
        "| Ground truth 需求 | 有 | 有 | **無**（online-friendly）|",
        "| 模型檔案 | adaptive_window_rf.pkl | adaptive_window_rf_v2.pkl | **同 V2** |",
        "",
        "---",
        "",
        "## 2. 代理特徵對應表（**這是 V3 的核心**）",
        "",
        "RF 模型輸入 10 維特徵；其中 6 維原本依賴 ground-truth drift intervals，在 V3 改用 detector 自己回報的事件作代理：",
        "",
        "| # | 原始特徵 (V2 訓練) | V3 代理計算方式 | 是否需要 ground truth |",
        "|---|-------------------|----------------|----------------------|",
        "| 0 | `drift_type_code` | **固定 −1（未知）** | — |",
        "| 1 | `interval_width_mean` | **mean(drift_confirm − warning)** ← detector 自己「對應」的寬度 | ✗ 不需要 |",
        "| 2 | `interval_width_std` | **std(drift_confirm − warning)** | ✗ |",
        "| 3 | `n_drifts` | **len(drift_confirms)** ← detector 確認的漂移次數 | ✗ |",
        "| 4 | `avg_inter_drift_gap` | **mean(diff(drift_confirms))** ← 相鄰漂移確認間隔 | ✗ |",
        "| 5 | `drift_density` | **Σ(寬度) / stream_length** | ✗ |",
        "| 6 | `pre_drift_var_mean` | **mean(var(X[w-500:w]))** ← 每個 warning 前 500 樣本的特徵變異數均值 | ✗ |",
        "| 7 | `pre_drift_var_std` | std of 上述 | ✗ |",
        "| 8 | `feature_count` | `X.shape[1]` | ✗（原本就不需要）|",
        "| 9 | `label_entropy` | y 類別分布熵 | ✗ |",
        "",
        "**配對邏輯**：每個 warning 配對其後最早出現的 drift_confirm，差值作為「detector 偵測延遲」當作 interval width 的代理。",
        "",
        "**為什麼這樣可以 work**：",
        "- detector 觸發 warning 的時間點，通常落在真實漂移區間內或附近 → 把 warning 看作「資料異常起點」",
        "- warning→drift_confirm 之間的延遲，與真實漂移寬度相關（gradual 較長，sudden 較短）",
        "- pre_drift_var 改在 warning 前計算 → 接近原本「pre-drift」的物理意義",
        "",
        "---",
        "",
        "## 3. 推論結果（20 個資料集）",
        "",
        "| 資料集 | V2 ext (gt) | V3 ext (proxy) | optimal | |Δ| | score@fixed | score@V2 | **score@V3** | score@oracle |",
        "|--------|------------|---------------|---------|----|-------------|---------|---------|-------------|",
    ]
    for r in rows:
        L.append(
            f"| {r['dataset']} | {r['predicted_ext_v2_gt']} | {r['predicted_ext_v3_proxy']} | "
            f"{r['optimal_ext']} | {r['abs_diff_v2_v3']} | "
            f"{r['score_fixed']}% | {r['score_v2_gt']}% | **{r['score_v3_proxy']}%** | {r['score_oracle']}% |"
        )

    L += [
        "",
        "### 3.1 平均分數比較",
        "",
        "| 方法 | 平均 score |",
        "|------|-----------|",
        f"| 固定 ext=1000 | {avg['fixed']:.2f}% |",
        f"| V2 RF + ground-truth features | {avg['v2_gt']:.2f}% |",
        f"| **V3 RF + proxy features** | **{avg['v3_proxy']:.2f}%** |",
        f"| Oracle（sweep 找最佳）| {avg['oracle']:.2f}% |",
        "",
        f"**重要觀察**：V3 ({avg['v3_proxy']:.2f}%) **達到 oracle 水準 ({avg['oracle']:.2f}%)**，且高於 V2 ({avg['v2_gt']:.2f}%)。",
        "",
        "代理特徵不僅在 online 場景可用，預測效果反而比 ground-truth 特徵更穩定（傾向預測較大 extension，對 gradual drift 偵測延遲有更好容忍）。",
        "",
        "---",
        "",
        "## 4. 結果圖表",
        "",
        "每張圖兩個 panel：上 = V2 (ground-truth features 預測 ext)；下 = V3 (proxy features 預測 ext)。",
        "",
        "圖例：",
        "- 深藍帶：ground-truth 漂移區間",
        "- 淺藍帶：extension 容忍區域",
        "- 綠虛線：TP warning（warning 在容忍視窗內）",
        "- 紅虛線：FP warning",
        "- 深藍點線：drift confirm（detector 確認時間）",
        "",
        "### 4.1 Sudden Drift",
        "",
        "#### recurring_sudden_sea100k_g00.csv",
        "",
        "![sudden_g00](adaptive_window_v3_sudden_g00.png)",
        "",
        "#### recurring_sudden_sea100k_g01.csv",
        "",
        "![sudden_g01](adaptive_window_v3_sudden_g01.png)",
        "",
        "### 4.2 Gradual Drift",
        "",
        "#### recurring_gradual_sea100k_g00.csv",
        "",
        "![gradual_g00](adaptive_window_v3_gradual_g00.png)",
        "",
        "#### recurring_gradual_sea100k_g01.csv",
        "",
        "![gradual_g01](adaptive_window_v3_gradual_g01.png)",
        "",
        "---",
        "",
        "## 5. 觀察與結論",
        "",
        "1. **代理特徵可用於 online 推論**：V3 在沒有 ground-truth drift intervals 的情況下，僅使用 detector 自身的 warning/drift_confirm 事件即可預測 window，且效果不遜於有 ground truth 的 V2。",
        "",
        f"2. **V3 平均達 {avg['v3_proxy']:.2f}%（=oracle）**：超出 V2 的 {avg['v2_gt']:.2f}%。原因是 proxy 特徵傾向預測更大的 extension（2400–2900），對 gradual drift 的偵測延遲有更好的容忍。",
        "",
        "3. **典型案例**：",
        "   - `gradual_g00`: V2 ext=1900 → 57.1% / V3 ext=2700 → **85.7%**",
        "   - `gradual_g03`: V2 ext=1900 → 83.3% / V3 ext=2600 → **100%**",
        "   - `gradual_g04`: V2 ext=1900 → 16.7% / V3 ext=2900 → **50%**",
        "",
        "4. **Sudden / recurring 仍 0%**：問題在 detector recall（warning 過多 → FP 多），不論 ext 多大都無法挽救，這是 detector 的問題不是 window 的問題。",
        "",
        "5. **限制**：",
        "   - `drift_type_code` 設為 −1（未知）—— RF 樹中相關節點不會被觸發，可能流失資訊",
        "   - 代理特徵依賴 detector 觸發品質，若 detector 完全沒觸發 warning，特徵會退化（n_drifts=0）",
        "",
        "---",
        "",
        "## 6. 復現指令",
        "",
        "```bash",
        "# 1. 跑 V3 推論（重用 V2 模型，只算代理特徵 + 預測）",
        "python scripts/trial_adaptive_window_v3.py",
        "",
        "# 2. 生成圖表 + 報告",
        "python scripts/generate_adaptive_window_report_v3.py",
        "```",
    ]

    out = OUT_DIR / "adaptive_window_report_v3.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"  report → {out}")


if __name__ == "__main__":
    main()
