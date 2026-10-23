#!/usr/bin/env python3
"""Render the audited DET4 analysis as Markdown, HTML and heatmaps."""
from __future__ import annotations

import json
import html as html_lib
import math
import os
from pathlib import Path
import re
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "det4-mpl-cache"))
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np


REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "outputs" / "det4"
FIG = OUT / "figures"
S = json.loads((OUT / "det4_verdict_data.json").read_text())

DETECTORS = ("adwin", "hddma", "rddm")
FRAMEWORKS = ("s0", "s1")
LABEL = {"adwin": "ADWIN", "hddma": "HDDM-A", "rddm": "RDDM"}
METRIC_LABEL = {
    "acc": "prequential accuracy",
    "post_acc": "post-drift 1000-step accuracy",
    "fp": "FP@1000",
    "X": "E11 excess hits X",
}


def preset(framework: str, warning: str, confirm: str) -> str:
    return f"det4_{framework}_w{warning}_c{confirm}"


def cell_label(name: str) -> str:
    _, framework, warning, confirm = name.split("_")
    return f"{framework.upper()} {LABEL[warning[1:]]}/{LABEL[confirm[1:]]}"


def n(value, digits=2, signed=False):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    template = f"{{:{'+' if signed else ''},.{digits}f}}"
    return template.format(value)


def integer(value):
    return "—" if value is None else f"{value:,.0f}"


def delta(value: dict, scale=1.0, digits=2) -> str:
    if value["point"] is None:
        return "—"
    point = n(value["point"] * scale, digits, True)
    if value["ci"] is None:
        return f"{point}（單一串流）"
    low, high = value["ci"]
    return f"{point} [{n(low * scale, digits, True)}, {n(high * scale, digits, True)}]"


def table(headers, rows):
    return [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
        *["| " + " | ".join(str(value) for value in row) + " |" for row in rows],
        "",
    ]


def save_matrix_heatmap(framework: str, metric: str) -> str:
    values = np.array([
        [S["t1_t3"]["t1_aggregates"][preset(framework, warning, confirm)][metric]
         for confirm in DETECTORS]
        for warning in DETECTORS
    ], dtype=float)
    display = values * 100 if metric in ("acc", "post_acc") else values
    cmap = "RdYlGn_r" if metric == "fp" else "RdYlGn"
    fig, ax = plt.subplots(figsize=(6.8, 5.5))
    image = ax.imshow(display, cmap=cmap, aspect="equal")
    ax.set_xticks(range(3), [LABEL[value] for value in DETECTORS])
    ax.set_yticks(range(3), [LABEL[value] for value in DETECTORS])
    ax.set_xlabel("Confirm detector")
    ax.set_ylabel("Warning detector")
    ax.set_title(f"{framework.upper()} T1 — {METRIC_LABEL[metric]}")
    threshold = (float(np.nanmax(display)) + float(np.nanmin(display))) / 2
    for row in range(3):
        for col in range(3):
            text = f"{display[row, col]:.3f}" if metric in ("acc", "post_acc") else f"{display[row, col]:,.1f}"
            ax.text(col, row, text, ha="center", va="center",
                    color="white" if abs(display[row, col] - threshold) > np.ptp(display) * 0.32 else "black",
                    fontsize=10, fontweight="bold")
    fig.colorbar(image, ax=ax, shrink=0.82)
    fig.tight_layout()
    name = f"t1_{framework}_{metric}.png"
    fig.savefig(FIG / name, dpi=180)
    plt.close(fig)
    return name


def save_q4_heatmap(framework: str, metric: str) -> str:
    datasets = list(S["q4"]["datasets"][framework])
    if metric == "X":
        datasets = [
            dataset for dataset in datasets
            if S["q4"]["datasets"][framework][dataset][preset(framework, "hddma", "hddma")][metric]["point"] is not None
        ]
    cells = [preset(framework, warning, confirm) for warning in DETECTORS for confirm in DETECTORS]
    values = np.array([
        [S["q4"]["datasets"][framework][dataset][cell][metric]["point"] for cell in cells]
        for dataset in datasets
    ], dtype=float)
    if metric == "acc":
        values *= 100
    extent = float(np.nanmax(np.abs(values))) or 1.0
    fig, ax = plt.subplots(figsize=(15, max(8, len(datasets) * 0.47)))
    image = ax.imshow(values, cmap="RdBu", norm=TwoSlopeNorm(vmin=-extent, vcenter=0, vmax=extent), aspect="auto")
    ax.set_xticks(range(9), [f"{LABEL[w]}\n{LABEL[c]}" for w in DETECTORS for c in DETECTORS], rotation=35, ha="right")
    ax.set_yticks(range(len(datasets)), datasets)
    ax.set_xlabel("Warning / confirm")
    ax.set_title(f"{framework.upper()} Q4 — Δ{'accuracy (percentage points)' if metric == 'acc' else 'X'} vs HDDM-A/HDDM-A")
    for row in range(len(datasets)):
        for col in range(9):
            value = values[row, col]
            ax.text(col, row, f"{value:+.2f}" if metric == "acc" else f"{value:+.1f}",
                    ha="center", va="center", fontsize=6.1,
                    color="white" if abs(value) > extent * 0.55 else "black")
    fig.colorbar(image, ax=ax, shrink=0.75)
    fig.tight_layout()
    name = f"q4_{framework}_delta_{metric}.png"
    fig.savefig(FIG / name, dpi=180)
    plt.close(fig)
    return name


def render_figures() -> dict:
    FIG.mkdir(parents=True, exist_ok=True)
    result = {framework: {} for framework in FRAMEWORKS}
    for framework in FRAMEWORKS:
        for metric in ("acc", "post_acc", "fp", "X"):
            result[framework][metric] = save_matrix_heatmap(framework, metric)
        result[framework]["q4_acc"] = save_q4_heatmap(framework, "acc")
        result[framework]["q4_X"] = save_q4_heatmap(framework, "X")
    return result


def inline_markdown(value: str) -> str:
    value = html_lib.escape(value)
    value = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', value)
    value = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return value


def markdown_to_html(value: str) -> str:
    """Small deterministic renderer for the report's headings, tables, lists and images."""
    source = value.splitlines()
    output: list[str] = []
    index = 0
    in_list = False
    while index < len(source):
        line = source[index]
        if not line:
            if in_list:
                output.append("</ul>")
                in_list = False
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            if in_list:
                output.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            output.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            index += 1
            continue
        if line.startswith("| ") and index + 1 < len(source) and source[index + 1].startswith("|"):
            if in_list:
                output.append("</ul>")
                in_list = False
            headers = [cell.strip() for cell in line.strip("|").split("|")]
            output.append("<table><thead><tr>" + "".join(f"<th>{inline_markdown(cell)}</th>" for cell in headers) + "</tr></thead><tbody>")
            index += 2
            while index < len(source) and source[index].startswith("|"):
                cells = [cell.strip() for cell in source[index].strip("|").split("|")]
                output.append("<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in cells) + "</tr>")
                index += 1
            output.append("</tbody></table>")
            continue
        if line.startswith("- "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{inline_markdown(line[2:])}</li>")
            index += 1
            continue
        if in_list:
            output.append("</ul>")
            in_list = False
        rendered = inline_markdown(line)
        output.append(rendered if rendered.startswith("<img ") else f"<p>{rendered}</p>")
        index += 1
    if in_list:
        output.append("</ul>")
    return "\n".join(output)


def pair_effect_rows(kind: str):
    rows = []
    source = S["t1_t3"][kind]
    fixed_label = "固定 confirm" if kind == "warning_effects" else "固定 warning"
    for framework in FRAMEWORKS:
        for fixed in DETECTORS:
            for pair, result in source[framework][fixed].items():
                left, right = pair.split("-")
                rows.append([
                    framework.upper(), f"{fixed_label}={LABEL[fixed]}",
                    f"{LABEL[left]} − {LABEL[right]}", delta(result["fp"], digits=1),
                    delta(result["X"], digits=2), result["detection"],
                    delta(result["acc"], 100, 3), result["accuracy"],
                ])
    return rows


def main():
    figures = render_figures()
    h1 = S["t1_t3"]["h1"]
    h2 = S["t1_t3"]["h2"]
    h3 = S["t1_t3"]["h3"]
    metadata = S["metadata"]
    candidate_q4 = S["q4"]["summary"]["s1"][h3["candidate"]]
    lines = [
        "# DET4：三項預註冊假設均未成立，ADWIN/HDDM-A 不取代 HDDM-A 對角", "",
        "**主結論：** H1、H2、H3 均未成立。S0 的 warning 軸 accuracy 變動確實大於 confirm 軸，且 ADWIN warning 在三欄的凍結步數都最多；但 confirm=ADWIN 時，ADWIN warning 的 accuracy 不是最低，因此 H1 的完整預測未通過。S1 的 warning 軸在 X 與 drift 後 accuracy 的變動都大於 confirm 軸，且 warning=ADWIN 時 confirm=ADWIN 並非兩項最低，因此 H2 未通過。H3 候選 `warning=ADWIN, confirm=HDDM-A` 在 T1 的偵測與全串流 accuracy 均持平，但在 T3 的 accuracy 顯著較低，故不得採用。", "",
        f"H3 在 T3 的 Δaccuracy 為 **{delta(h3['t3']['acc'], 100, 3)} 個百分點**；偵測仍判{h3['t3']['detection']}，但 ΔX 為 {delta(h3['t3']['X'], digits=2)}。跨 22 個資料集，該候選相對 HDDM-A 對角的 accuracy 中位數為 {n(candidate_q4['accuracy_median'] * 100, 3, True)} 個百分點，最差是 `{candidate_q4['accuracy_worst_dataset']}` 的 {n(candidate_q4['accuracy_worst'] * 100, 3, True)} 個百分點。", "",
        "判定依[DET4 預註冊](../../docs/ECPF_DET4_預註冊.md)：T1 為 205 條配對串流，T3 為 240 條未用於 DET 的保留串流；三資料層配對 bootstrap 10,000 次、seed `20261012`。偵測只有 ΔFP 的 CI 全負且 ΔX 的 CI 全正才算優於，兩者同時顯著反向才算不如，其餘持平；accuracy CI 全正／全負才判優於／不如。", "",
        "## H1–H3 的事前預測未獲完整支持", "",
    ]
    h_rows = [
        ["H1（S0）", "未成立" if not h1["holds"] else "成立",
         f"warning accuracy range {n(h1['axis']['warning_accuracy_range'] * 100, 3)} pp；confirm {n(h1['axis']['confirm_accuracy_range'] * 100, 3)} pp",
         "; ".join(f"C={LABEL[item['confirm']]}：凍結最多={'是' if item['adwin_frozen_most'] else '否'}、accuracy 最低={'是' if item['adwin_accuracy_lowest'] else '否'}" for item in h1["checks"])],
        ["H2（S1）", "未成立" if not h2["holds"] else "成立",
         f"X range warning {n(h2['axis']['warning_X_range'], 2)} vs confirm {n(h2['axis']['confirm_X_range'], 2)}；post-acc {n(h2['axis']['warning_post_accuracy_range'] * 100, 3)} vs {n(h2['axis']['confirm_post_accuracy_range'] * 100, 3)} pp",
         "; ".join(f"W={LABEL[item['warning']]}：ADWIN X 最低={'是' if item['adwin_X_lowest'] else '否'}、post-acc 最低={'是' if item['adwin_post_accuracy_lowest'] else '否'}" for item in h2["checks"])],
        ["H3（S1 ADWIN/HDDM-A）", "未成立" if not h3["holds"] else "成立",
         f"T1 偵測{h3['t1']['detection']}、accuracy {h3['t1']['accuracy']}；T3 偵測{h3['t3']['detection']}、accuracy {h3['t3']['accuracy']}",
         "必須 T1 與 T3 的兩軸都不輸；T3 accuracy 不如，故失敗"],
    ]
    lines += table(["假設", "結論", "量化結果", "So what"], h_rows)

    lines += ["## H3 在保留資料失敗，T1 的持平不能覆蓋 T3 的 accuracy 損失", ""]
    h3_rows = []
    for subset in ("t1", "t3"):
        value = h3[subset]
        h3_rows.append([
            subset.upper(), str(value["acc"]["n"]), delta(value["fp"], digits=1),
            delta(value["X"], digits=2), value["detection"],
            delta(value["acc"], 100, 3), value["accuracy"],
            delta(value["post_acc"], 100, 3),
        ])
    lines += table(["子集", "串流", "ΔFP [CI]", "ΔX [CI]", "偵測", "Δaccuracy pp [CI]", "accuracy", "Δdrift 後 acc. pp [CI]"], h3_rows)
    lines += ["差值皆為 S1 ADWIN/HDDM-A 減 S1 HDDM-A/HDDM-A。T1 的 ΔFP 有利但 ΔX 顯著不利，依雙條件規則只能判持平；T3 同樣如此，且全串流 accuracy 的 CI 全負。", ""]

    for framework in FRAMEWORKS:
        lines += [f"## {framework.upper()} 的 T1 3×3 矩陣顯示 detector 角色不可互換", ""]
        for metric in ("acc", "post_acc", "fp", "X"):
            lines += [f"![{framework.upper()} {METRIC_LABEL[metric]}](figures/{figures[framework][metric]})", ""]
        matrix_rows = []
        for warning in DETECTORS:
            for confirm in DETECTORS:
                value = S["t1_t3"]["t1_aggregates"][preset(framework, warning, confirm)]
                matrix_rows.append([
                    LABEL[warning], LABEL[confirm], n(value["acc"], 4), n(value["post_acc"], 4),
                    integer(value["fp"]), n(value["X"], 2), integer(value["frozen"]),
                ])
        lines += table(["warning", "confirm", "preq. accuracy", "drift 後 accuracy", "FP@1000", "X", "凍結步數"], matrix_rows)

    lines += ["## 每格對 HDDM-A 對角的雙軸判定沒有產生可取代 H3 的事前候選", ""]
    diagonal_rows = []
    for framework in FRAMEWORKS:
        for warning in DETECTORS:
            for confirm in DETECTORS:
                name = preset(framework, warning, confirm)
                value = S["t1_t3"]["vs_diagonal"][framework][name]
                diagonal_rows.append([
                    cell_label(name), delta(value["fp"], digits=1), delta(value["X"], digits=2),
                    value["detection"], delta(value["acc"], 100, 3), value["accuracy"],
                    delta(value["post_acc"], 100, 3),
                ])
    lines += table(["格（相對同框架 HDDM-A/HDDM-A）", "ΔFP [CI]", "ΔX [CI]", "偵測", "Δaccuracy pp [CI]", "accuracy", "Δpost-acc pp [CI]"], diagonal_rows)
    lines += ["H3 以外的格即使 T1 較好，也依預註冊只屬事後觀察，不改列候選。", ""]

    lines += ["## Warning 列效果與 confirm 欄效果呈現交互作用，不能用單一 detector 排名取代", ""]
    lines += table(["框架", "固定條件", "配對差", "ΔFP [CI]", "ΔX [CI]", "偵測", "Δaccuracy pp [CI]", "accuracy"], pair_effect_rows("warning_effects"))
    lines += table(["框架", "固定條件", "配對差", "ΔFP [CI]", "ΔX [CI]", "偵測", "Δaccuracy pp [CI]", "accuracy"], pair_effect_rows("confirm_effects"))

    lines += ["## Q4 顯示跨資料集不穩健，最差情況否定全域替換", ""]
    for framework in FRAMEWORKS:
        lines += [f"![{framework.upper()} Q4 Δaccuracy](figures/{figures[framework]['q4_acc']})", "",
                  f"![{framework.upper()} Q4 ΔX](figures/{figures[framework]['q4_X']})", ""]
    q4_rows = []
    for framework in FRAMEWORKS:
        for warning in DETECTORS:
            for confirm in DETECTORS:
                name = preset(framework, warning, confirm)
                value = S["q4"]["summary"][framework][name]
                q4_rows.append([
                    cell_label(name), n(value["accuracy_median"] * 100, 3, True),
                    f"{value['accuracy_worst_dataset']} ({n(value['accuracy_worst'] * 100, 3, True)})",
                    str(value["accuracy_negative_ci_datasets"]), n(value["X_median"], 2, True),
                    f"{value['X_worst_dataset']} ({n(value['X_worst'], 2, True)})",
                    str(value["X_negative_ci_datasets"]),
                ])
    lines += table(["格", "Δaccuracy 中位數 pp", "最差資料集 (pp)", "CI 全負資料集", "ΔX 中位數", "最差資料集 (ΔX)", "X CI 全負資料集"], q4_rows)
    lines += ["Accuracy 涵蓋 22 個非迴歸 registry 資料集；X 只涵蓋 14 個有非空 GT 的資料集。單串流資料集只報點估計，不計入『CI 全負』。各資料集先在自身尺度配對，不用總樣本數加權掩蓋最差情況。", ""]

    lines += ["## 資料類別與 drift 型態分層顯示效果來源異質", ""]
    category_rows = []
    for framework in FRAMEWORKS:
        for warning in DETECTORS:
            for confirm in DETECTORS:
                name = preset(framework, warning, confirm)
                row = [cell_label(name)]
                for category in ("真實", "INSECTS", "注入 CSV", "注入 paper", "合成"):
                    value = S["q4"]["categories"][framework][category][name]
                    x = "—" if value["X_median"] is None else n(value["X_median"], 1, True)
                    row.append(f"{n(value['accuracy_median'] * 100, 2, True)} / {x}")
                category_rows.append(row)
    lines += table(["格", "真實 Δacc/X", "INSECTS Δacc/X", "注入 CSV Δacc/X", "注入 paper Δacc/X", "合成 Δacc/X"], category_rows)
    type_rows = []
    for framework in FRAMEWORKS:
        for warning in DETECTORS:
            for confirm in DETECTORS:
                name = preset(framework, warning, confirm)
                row = [cell_label(name)]
                for drift_type in ("突變", "漸變", "incremental", "recurring"):
                    value = S["t1_t3"]["strata"]["types"][drift_type][framework][name]
                    row.append(f"{delta(value['acc'], 100, 2)} / {delta(value['X'], digits=1)}")
                type_rows.append(row)
    lines += table(["格", "突變 Δacc/X", "漸變 Δacc/X", "incremental Δacc/X", "recurring Δacc/X"], type_rows)
    lines += ["類別表採各資料集相對差的中位數；型態表用 T1 同型態串流的配對 bootstrap。複合型態可出現在多欄，分層只描述異質性，不改主要判定。", ""]

    lines += ["## Warning 生命週期與成本證據可重現且需分開解讀", ""]
    mechanism_rows = []
    for framework in FRAMEWORKS:
        for warning in DETECTORS:
            for confirm in DETECTORS:
                name = preset(framework, warning, confirm)
                value = S["mechanisms"][name]
                mechanism_rows.append([
                    cell_label(name), integer(value["opened"]), integer(value["confirmed"]),
                    integer(value["zone_exit"]), n(value["self_close_ratio"] * 100 if value["self_close_ratio"] is not None else None, 1),
                    integer(value["timeout"]), integer(value["reference_switch"]), integer(value["censored"]),
                    n(value["mean_confirmation_delay"], 1), integer(value["frozen_steps"]),
                ])
    lines += table(["格", "warning 開啟", "確認", "自行關閉", "自行關閉 %", "timeout", "reference switch", "截尾", "平均確認延遲", "凍結步數"], mechanism_rows)
    lines += ["逐 run 驗證 `開啟 = close + censored`。平均確認延遲用 confirmed warning buffer 長度；S1 凍結步數固定為 0。", ""]

    timing_rows = []
    for framework in FRAMEWORKS:
        for warning in DETECTORS:
            for confirm in DETECTORS:
                name = preset(framework, warning, confirm)
                value = S["costs"]["strict_electricity"][name]
                timing_rows.append([
                    cell_label(name), n(value["runtime_s"], 2), n(value["cpu_time_s"], 2),
                    n(value["instances_per_s"], 1), n(value["rss_increment_mb"], 1),
                    n(value["model_size_final_mb"], 2), n(value["ram_hours_gb"], 6),
                ])
    lines += table(["格（electricity, workers=1）", "runtime s", "CPU s", "instances/s", "RSS 增量 MB", "final model MB", "RAM-hours GB"], timing_rows)
    missing_cost = sum(value["runs_without_cost"] for value in S["costs"]["parallel"].values())
    lines += [
        f"Strict timing 的 18/18 runs 均為 Apple M4、`concurrent_runs=1`，可直接比較時間；完整批次多數 `concurrent_runs=6`，時間只作參考，記憶體仍是逐程序量測。五個沿用對角共 {missing_cost:,} 個舊 run 沒有新版 cost block，未補算；其餘成本見[全範圍 cost.csv](compare_sota_all/cost.csv)。",
        "[正式可比標準報表](compare_sota/report.md)只保留 registry 可比列；[全 22 資料集 exploratory 報表](compare_sota_all/report.md)明示不可據此宣稱 SOTA，並提供每資料集 × preset 的標準分類、偵測與成本欄位。DET4 全為 ECPF pipeline preset，`injected_paper_*` 只有 detector-only preset 可與 Cerqueira et al. 比較，因此本報告不作文獻 SOTA 聲明。", "",
    ]

    formal_hours = metadata["formal_elapsed_s"] / 3600
    lines += ["## 30,456 個邏輯 runs 全數通過完整性稽核", "",
              f"正式矩陣共 {metadata['logical_runs']:,} 個邏輯 runs：新跑 {metadata['new_runs']:,}、沿用對角 {metadata['reused_runs']:,}；22 個資料集 × 18 組配置的規劃數全部到齊。T1、T3、short、paper、full 五批皆 failed=0、errors=[]、skipped=[]；正式批次牆上時間合計 {formal_hours:.2f} 小時，另有 strict timing {metadata['strict_timing_elapsed_s'] / 60:.2f} 分鐘。", "",
              "稽核逐 run 驗證 preset、registry、來源 SHA-256、乾淨 commit、River 0.21.2、完整串流、GT、evaluator TP/FP/FN、warning 事件守恆與 S1 零凍結；T1/T3 另從 preds 重算 drift 後 1000 步 accuracy。資料與 CI 見[機器可讀 verdict data](det4_verdict_data.json)，replay 與 smoke 見[stage2 gate](stage2_gate.md)及[stage3 smoke](stage3_smoke.md)。大型逐 run artifacts 保持 git-ignored。", "",
              "## 事後觀察不改寫預註冊結論", ""]
    for framework in FRAMEWORKS:
        cells = [preset(framework, w, c) for w in DETECTORS for c in DETECTORS]
        best_acc = max(cells, key=lambda cell: S["t1_t3"]["t1_aggregates"][cell]["acc"])
        best_x = max(cells, key=lambda cell: S["t1_t3"]["t1_aggregates"][cell]["X"])
        lines.append(f"- {framework.upper()} T1 accuracy 點估計最高為 {cell_label(best_acc)}（{n(S['t1_t3']['t1_aggregates'][best_acc]['acc'], 4)}）；X 最高為 {cell_label(best_x)}（{n(S['t1_t3']['t1_aggregates'][best_x]['X'], 2)}）。兩者只作事後描述，沒有 T3 事前候選資格。")
    lines += ["", "## 偏離、失敗與缺漏不改變主要判定", "",
              "- Registry 在 smoke 前確認實際為 25 個資料集、排除 3 個迴歸後為 22 個；不是原附件文字的 23 個。此修訂已在正式執行前追加至預註冊，未補造資料，30,456 總量不變。",
              "- Full 批次第一次執行在 Airlines 完成後，位於 `/private/tmp` 的暫存 Python runtime 被系統清理，Covertype 因缺少標準庫／pandas 中止。已保留 18/18 Airlines checkpoint，改用專案內 `.venv311` 從 Covertype 恢復；最終 full summary 為 36/36、回傳碼 0、零失敗。這是執行環境偏離，不改資料、preset、metric 或判準。",
              f"- 沿用的 {missing_cost:,} 個 DET1/DET3 對角 runs 沒有新版 cost block；判定指標完整，成本缺值不補算。另行 strict timing 18/18 完整，提供統一環境的時間與記憶體比較。", "",
              "## 限制把結論鎖定在本研究的 ECPF pipeline", "",
              "本輪只測單棵 Hoeffding Tree；ADWIN 與 HDDM-A 來自 River 0.21.2，RDDM 採已驗證的 MOA replay 實作。Synthetic、部分 INSECTS 與 injected 資料曾用於前輪開發；T3 只對 H3 指定格提供未用於 DET 的保留驗證。迴歸未測；混搭 warning/confirm 的 reset、zone exit 與 timeout 語意是本研究定義。沒有 GT 的真實資料只支持預測與成本描述；pipeline 偵測指標不可與 detector-only 文獻 SOTA 並列。CI 描述本批配對串流的條件不確定性，不是跨任務母體保證。", "",
    ]

    markdown_text = "\n".join(lines)
    (OUT / "det4_verdict.md").write_text(markdown_text)

    body = markdown_to_html(markdown_text)
    style = (
        'body{margin:0;background:#eef3f5;color:#172534;font:15px/1.68 -apple-system,BlinkMacSystemFont,"Noto Sans TC","PingFang TC",sans-serif}'
        'main{max-width:1480px;margin:26px auto;padding:34px 40px;background:#fff;border:1px solid #d5e0e5;border-radius:10px;box-shadow:0 7px 26px #17304210}'
        'h1{color:#0b3047;line-height:1.24;font-size:2rem}h2{margin-top:2.25rem;padding-bottom:.38rem;border-bottom:2px solid #0b7b78;color:#0b3047;font-size:1.32rem}'
        'table{display:block;overflow:auto;border-collapse:collapse;font-size:.82rem;line-height:1.43;margin:1rem 0 1.35rem}'
        'td,th{border:1px solid #d6e0e5;padding:.46rem .58rem;vertical-align:top;min-width:68px}th{background:#e8f3f3;white-space:nowrap}tbody tr:nth-child(even){background:#f8fafb}'
        'img{display:block;max-width:100%;height:auto;margin:1rem auto 1.6rem;border:1px solid #d6e0e5;background:white}'
        'a{color:#076b76}strong{color:#083d55}code{background:#edf2f4;border-radius:3px;padding:.1em .28em;overflow-wrap:anywhere}'
        '@media(max-width:720px){main{margin:0;padding:18px 14px;border-radius:0}h1{font-size:1.45rem}}'
    )
    html = (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>DET4 warning × confirm detector matrix</title><style>' + style +
        '</style></head><body><main>' + body + '</main></body></html>\n'
    )
    (OUT / "det4_verdict.html").write_text(html)
    print("rendered", OUT / "det4_verdict.md", OUT / "det4_verdict.html", "and", len(list(FIG.glob("*.png"))), "figures")


if __name__ == "__main__":
    main()
