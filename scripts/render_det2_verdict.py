#!/usr/bin/env python3
"""Render the audited DET2 summary as Markdown and a standalone HTML report."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/det2"
S = json.loads((OUT / "det2_verdict_data.json").read_text())
ARMS = ("A1-lw0", "A1-lw1", "A3-lw0", "A3-lw1", "A4-lw0", "A4-lw1")
LABEL = {"A1": "Dual ADWIN", "A3": "HDDM-A", "A4": "RDDM"}


def num(x, digits=2, signed=False):
    if x is None:
        return "—"
    return f"{x:+,.{digits}f}" if signed else f"{x:,.{digits}f}"


def integer(x):
    return "—" if x is None else f"{x:,}"


def ci(x, scale=1, digits=2):
    if x is None:
        return "—"
    return f"[{num(x[0] * scale, digits, True)}, {num(x[1] * scale, digits, True)}]"


def delta(item, metric, scale=1, digits=2):
    d = item[metric]
    return f"{num(d['point'] * scale, digits, True)} {ci(d['ci'], scale, digits)}"


def table(headers, rows):
    return ["| " + " | ".join(headers) + " |",
            "|" + "|".join("---" for _ in headers) + "|",
            *["| " + " | ".join(str(x) for x in row) + " |" for row in rows], ""]


def main():
    q1, q2, q3 = S["q1"], S["q2"], S["q3"]
    d1, d2 = S["metadata"]["det1_commit"], S["metadata"]["det2_commit"]
    lines = [
        "# DET2：warning 期間持續學習改善 A1、A4 準確率，但 Dual ADWIN 未追上 A3、A4",
        "",
        "**主結論：** 在 DET1 固定的單棵 Hoeffding Tree、205 條配對串流下，開啟 warning 期間持續學習後，Dual ADWIN（A1）的全串流 prequential accuracy 提高 **0.456 個百分點**（95% CI [+0.240, +0.670]），RDDM（A4）提高 **0.282 個百分點**（CI [+0.066, +0.506]）；HDDM-A（A3）提高 0.050 個百分點，CI 跨 0，判為**持平**。點估計排序 **A1 > A4 > A3** 與事前 lw0 凍結步數排序一致。A1-lw1 對 A3-lw1、A4-lw1 的 FP 與 X 兩條件皆為不利、CI 不跨 0，故 Q2 **未追上，判不如**。將 A1 的 drift delta 改成 0.01 雖使 FP 減少 188，仍未改變 DET1 中 A3/A4 優於 A1 的判定。",
        "",
        "分析依 [DET2 預註冊](../../docs/ECPF_DET2_預註冊.md)事前鎖定的三組分層、串流配對 bootstrap 10,000 次、seed `20261012`，95% percentile CI 包含 0 即持平。[DET1 verdict](../det1/det1_verdict.html)與[階段三完整性紀錄](formal_integrity_20261013.md)提供前輪結果及本輪 run 來源。全串流 accuracy 含五條 INSECTS；FP、X 與 drift 後 accuracy 只用 204 條有 GT 串流。CI 描述本批串流的條件不確定性，不代表全新資料的外推區間。",
        "",
        "## Q1：A1 與 A4 的全串流準確率改善，A3 持平",
        "",
    ]
    main_rows = []
    for detector in ("A1", "A3", "A4"):
        for lw in ("lw0", "lw1"):
            arm = f"{detector}-{lw}"
            v = S["by_arm"][arm]
            main_rows.append([
                f"DET2-{arm} {LABEL[detector]}", num(v["acc"], 4), num(v["post_acc"], 4),
                integer(v["fp"]), integer(v["hits"]), num(v["X"]),
                num(v["mdt"], 1), num(v["kappa"], 4), integer(v["frozen"]),
                num(v["runtime"] / 60, 1),
            ])
    lines += table(
        ["組別", "preq. acc.", "drift 後 acc.", "FP@1000", "hits", "X", "MDT 步", "kappa", "凍結步數", "CPU 分"],
        main_rows,
    )
    lines += [
        "Accuracy 以可計分預測筆數加權；drift 後 accuracy 沿用 DET1 實際分析程式，在 GT 起點後 1,000 個座標步內取可觀測預測的加權正確率（injected 為原始 input 座標），重疊只計一次。FP、X、hits、MDT 排除空 GT INSECTS；CPU 分是 205 次 run 的 runtime 合計，不是 6 workers 的實際牆上時間。X 依 DET1 的每 drift 最多一次命中，並扣除機率命中期望值 C。",
        "",
    ]
    diff_rows = []
    for detector in ("A1", "A3", "A4"):
        v = q1[detector]
        wording = v["verdict"]
        if v["accuracy_up_detection_down"]:
            wording = "準確率改善、偵測品質下降"
        diff_rows.append([
            f"DET2-{detector} lw1−lw0", delta(v, "acc", 100, 3), wording,
            delta(v, "post_acc", 100, 3), delta(v, "fp", 1, 2), delta(v, "X", 1, 2),
        ])
    lines += table(
        ["配對比較", "Δpreq. acc. 百分點 [95% CI]", "Q1", "Δdrift 後 acc. 百分點 [CI]",
         "ΔFP [CI]", "ΔX [CI]"], diff_rows,
    )
    lines += [
        "Q1 只以全 205 條的 prequential accuracy CI 判「改善／惡化／持平」。三組 X 的 CI 均跨 0；因此 A1 與 A4 的準確率改善**不附帶已證實的 X 下降**，也不能以 accuracy 上升推論偵測品質改善。A4 的 FP 差 CI 全負，是次要偵測指標結果。",
        "",
        "## 凍結步數排序與改善點估計同序，但不當成因果證明",
        "",
        "| 偵測器 | DET1 lw0 凍結步數 | DET2 lw1 凍結步數 | Δaccuracy（百分點） | 改善點估計名次 |",
        "|---|---:|---:|---:|---:|",
    ]
    ranked = sorted(("A1", "A3", "A4"), key=lambda a: -q1[a]["acc"]["point"])
    for detector in ranked:
        lines.append(f"| DET2-{detector} {LABEL[detector]} | {integer(S['by_arm'][detector+'-lw0']['frozen'])} | 0 | {num(q1[detector]['acc']['point']*100, 3, True)} | {ranked.index(detector)+1} |")
    lines += [
        "",
        "開啟 lw1 時三個組別的所有正式 run 均實測凍結 0 步。排序一致是事前預測的描述性檢查；持續學習也改變後續 0/1 error 與偵測器狀態，不能將 accuracy 差全歸因於被解除的凍結。",
        "",
        "## 三資料組與四型態揭示 Q1 改善所在，不改總判準",
        "",
    ]
    for class_key, title, names in [
        ("groups", "三組資料", ("injected", "synthetic", "INSECTS")),
        ("types", "drift 型態", ("突變", "漸變", "incremental", "recurring")),
    ]:
        lines += [f"### {title}配對差值", ""]
        strata_rows = []
        for name in names:
            for detector in ("A1", "A3", "A4"):
                item = S["strata"][class_key][name][detector]
                strata_rows.append([
                    name, f"DET2-{detector}", f"{item['acc']['n']} / {item['fp']['n']}",
                    delta(item, "acc", 100, 3), delta(item, "post_acc", 100, 3),
                    delta(item, "fp", 1, 2), delta(item, "X", 1, 2),
                ])
        lines += table(
            ["資料／型態", "偵測器", "accuracy／GT 串流", "Δpreq. acc. 百分點 [CI]",
             "Δdrift 後 acc. 百分點 [CI]", "ΔFP [CI]", "ΔX [CI]"], strata_rows,
        )
    lines += [
        "型態依 DET1 的名稱規則標記：`abrupt/sudden`、`gradual`、`incremental`、`recurring/reoccurring`；複合名稱可落在多個描述層，總判定每串流只算一次。incremental 的 accuracy 層含一條空 GT INSECTS（16 條），偵測層只含其餘 15 條。各層 CI 只描述該層，不設額外勝負門檻。",
        "",
        "## Q2：A1-lw1 的 FP 與 X 仍同時不如 A3、A4",
        "",
    ]
    q2_rows = []
    for other in ("A3-lw1", "A4-lw1"):
        item = q2[other]
        q2_rows.append([
            f"DET2-A1-lw1 − DET2-{other}", delta(item, "fp", 1, 2), item["p1"],
            delta(item, "X", 1, 2), item["p2"], delta(item, "acc", 100, 3), item["verdict"],
        ])
    lines += table(["比較（A1 減對照）", "ΔFP [CI]", "P1", "ΔX [CI]", "P2",
                    "Δpreq. acc. 百分點 [CI]", "Q2 結論"], q2_rows)
    lines += [
        "P1 需 A1 的 FP 差 CI 全負，P2 需 A1 的 X 差 CI 全正。兩個對照的 FP CI 全正、X CI 全負，所以「不如」指這兩條預註冊偵測判準；accuracy 差另列，不代替 P1/P2。只有兩條都成立才能稱「追上並超越」；CI 含 0 或方向相反時標持平，不宣稱等效。",
        "",
        "## Q3：δ=0.01 減少 A1 誤報，卻未改變 DET1 的勝負",
        "",
    ]
    d = q3["delta_vs_a1"]
    lines += table(
        ["敏感度比較", "ΔFP [CI]", "ΔX [CI]", "Δpreq. acc. 百分點 [CI]"],
        [["DET2-A1d-lw0 − DET2-A1-lw0", delta(d, "fp", 1, 2),
          delta(d, "X", 1, 2), delta(d, "acc", 100, 3)]],
    )
    retest_rows = []
    for other in ("A3-lw0", "A4-lw0"):
        item = q3["det1_retest"][other]
        retest_rows.append([
            f"DET2-{other} − DET2-A1d-lw0", delta(item, "fp", 1, 2), item["p1"],
            delta(item, "X", 1, 2), item["p2"], item["verdict"],
        ])
    lines += table(["重算比較", "ΔFP [CI]", "P1", "ΔX [CI]", "P2", "敏感度結論"], retest_rows)
    lines += [
        "δ=0.01 的 A1d 僅作 lw0 敏感度，不進 Q1/Q2。A1d 相對 A1 原版的 X CI 跨 0；FP 明確下降，但全串流 accuracy 明確下降。以 A1d 作對照重算後，A3、A4 仍各自同時通過 DET1 的 P1/P2，因此預註冊所定「是否改變 DET1 判定」的答案為**否**。",
        "",
        "## 六格整合表保留 DET1 與 DET2 的同一母體比較",
        "",
    ]
    integrated_rows = []
    for detector in ("A1", "A3", "A4"):
        for lw in ("lw0", "lw1"):
            arm = f"{detector}-{lw}"
            v = S["by_arm"][arm]
            integrated_rows.append([
                f"DET2-{arm}", LABEL[detector], lw, num(v["acc"], 4), num(v["post_acc"], 4),
                integer(v["fp"]), integer(v["hits"]), num(v["C"]), num(v["X"]),
                num(v["kappa"], 4), integer(v["frozen"]), num(v["runtime"] / 60, 1),
            ])
    lines += table(["組別", "偵測器", "訓練", "全串流 acc.", "drift 後 acc.", "FP",
                    "episode hits", "C", "X", "kappa", "凍結步數", "CPU 分"], integrated_rows)
    lines += [
        "六格的 lw0 原始 run 沿用 DET1，經 45 次逐位元重現閘門通過；lw1 為本輪新跑。整合表的 accuracy 以**全部 205 條**計，因此 lw0 數字與 DET1「三組有 GT 合計」表的 204 條 accuracy 略有不同；偵測 FP／C／X 均只來自相同的 204 條有 GT 串流，與 DET1 逐項一致。",
        "",
        "## Warning 事件核對了零凍結及 buffer 成本",
        "",
    ]
    warning_rows = []
    for arm in (*ARMS, "A1d-lw0"):
        w = S["warnings"][arm]
        closed = sum(v for k, v in w["counts"].items() if k.startswith("close:"))
        other = closed - w["confirmed"] - w["zone_exit"]
        warning_rows.append([
            f"DET2-{arm}", integer(w["opened"]), integer(w["confirmed"]), integer(w["zone_exit"]),
            integer(other), integer(w["censored"]), integer(S["by_arm"][arm]["frozen"]),
            num(w["confirmed_buffer_median"], 1),
        ])
    lines += table(["組別", "開啟", "確認", "離區關閉", "其他關閉", "截尾", "凍結步數", "確認 buffer 中位"],
                   warning_rows)
    lines += [
        "每條 run 均驗證 warning 開啟數等於各種關閉與結尾截尾之和；凍結步數來自 metrics 的被動計數欄位，不由 warning 長度推估。確認事件可發生在 detector 計分起點前，故事件確認總數不能直接替代 FP 或 hits。",
        "",
        "## 空 GT 的 INSECTS incremental 僅提供描述性結果",
        "",
    ]
    no_gt_rows = []
    for arm in (*ARMS, "A1d-lw0"):
        v = S["no_gt"][arm]
        no_gt_rows.append([f"DET2-{arm}", num(v["acc"], 4), integer(v["alarms"]), num(v["runtime"], 2)])
    lines += table(["insects_incremental_balanced", "preq. acc.", "警報", "CPU 秒"], no_gt_rows)
    lines += [
        "該 GT 檔為空；此表不計 TP、FP、C、X，亦不從警報數推斷偵測正誤。全串流 Q1 accuracy 仍納入這條串流。",
        "",
        "## 正式輸出可追溯，失敗與缺漏均為零",
        "",
        f"DET2 新跑的固定程式 commit 為 `{d2}`，DET1 沿用來源 commit 為 `{d1}`；所有 manifest 工作樹乾淨、River `0.21.2`。新跑 **820／820、0 失敗**：第一批 180／180、2,091 秒；第二批 640／640、1,113 秒，總計 **3,204 秒（53 分 24 秒）**。每臂都有 160 injected、40 synthetic、5 INSECTS；有 GT 的 204 條配對、無 GT 的 1 條描述。分析逐 run 驗證 preset、source SHA-256、registry、版本、配對 `y_true`、warning 守恆及原 evaluator TP/FP/FN；lw0 偵測總數與 DET1 summary 交叉核對。詳見[逐 run 分數](det2_run_scores.csv)、[彙總資料與 CI](det2_verdict_data.json)、[正式完整性紀錄](formal_integrity_20261013.md)及[重現閘門／smoke](stage2_gate_smoke.md)。正式原始 run 在本機 git-ignored `outputs/benchmark/det2/`，與 DET1、smoke 隔離。",
        "",
        "評分仍用 DET1 的含端點 1,000 步窗 `[d_s,d_s+1000]`；injected 的 GT／警報採原始 input 座標且前 25% 警報不計分。每個 drift 最多算一次 episode hit，`C=Σ(1−exp(−FP/O·|W_i|))`、`X=hits−C`。四個 synthetic 暖機前 GT 排除後，正式偵測母體共 473 個可計分 GT。配對 bootstrap 依資料組保留 160／40／4 條有 GT 串流；全串流 accuracy 則保留 160／40／5 條。沒有因結果改窗、選串流或調參。",
        "",
        "## 偏離與口徑釐清不改主要判定",
        "",
        "階段二 CLI 的 `--cells` 子字串匹配，使固定抽中的 5 條 synthetic 之外額外跑出 4 條 × 3 組＝12 次 lw0 檢查 run。預先抽中的 **15 條／45 次**逐位元閘門仍全部通過；額外 run 留在隔離檢查目錄，不進任何正式計分或 CI。正式 820 次沒有偏離、失敗或缺漏。",
        "",
        "DET2 預註冊對 drift 後 accuracy 的文字寫「最多 1,000 個可觀測預測」；DET1 已提交的實際分析程式則以 GT 起點後 **1,000 個座標步**建立窗，injected 使用原始 input 座標，被注入刪除的列沒有預測，故該窗可能少於 1,000 個預測。本輪為保持與 DET1 完全相同，沿用其實際程式口徑，並在主表註解明示。這只影響次要 drift 後 accuracy 的解讀；Q1 主要全串流 accuracy 與 Q2/Q3 的 FP、X 判準不使用此欄。",
        "",
        "## 事後觀察指出 delta 與訓練機制的代價，不新增判準",
        "",
        "- A1d 的 lw0 凍結步數為 **3,728,743**，高於 A1 原版的 **1,717,081**；其確認 buffer 中位長度為 353 對 33。這與 delta=0.01 下更長的 warning 持續狀態一致，但 detector 狀態與 error 回饋也一起變動，不能將 accuracy 下降單獨歸因於凍結。",
        "- 空 GT INSECTS incremental 上，A1 的 lw1 accuracy 低於 lw0；它與整體 Q1 的 A1 改善方向不同，不能以整體結果保證每條串流受益。",
        "- A4 的 lw1 FP 比 lw0 少 48，CI [−95, −3] 全負；X 減少約 6.37，但 CI 跨 0。這是次要偵測指標，並未作為 Q1 準確率勝負門檻。",
        "",
        "## 證據只涵蓋鎖定的單棵樹與已使用資料",
        "",
        "本輪只有**單一 Hoeffding Tree**，不外推到森林或其他學習器。synthetic 曾用於 E 系列，是參數鎖定後評估，**不是新 holdout**；injected 每格只取 registry 前 **20 trials**。Dual ADWIN 採 **River 0.21.2** 實作，不能直接等同 MOA 或其他版本。Q2 的「不如」只依本輪預註冊的 FP 與 X 判準；各型態、INSECTS 子組的 CI 是描述性分層，不提供分布外效果保證。",
        "",
    ]
    md = "\n".join(lines)
    (OUT / "det2_verdict.md").write_text(md)
    try:
        import markdown
    except ImportError as exc:
        raise SystemExit("Markdown report written; install python-markdown to render HTML") from exc
    body = markdown.markdown(md, extensions=["tables", "fenced_code"])
    style = (
        'body{margin:0;background:#f2f5f7;color:#19283a;font:16px/1.72 -apple-system,'
        'BlinkMacSystemFont,"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif}'
        'main{max-width:1250px;margin:28px auto;padding:36px 42px;background:white;'
        'border:1px solid #d8e2ea;border-radius:10px;box-shadow:0 6px 24px #122d440b}'
        'h1{color:#0b2d48;line-height:1.25;font-size:2rem}'
        'h2{margin-top:2.4rem;padding-bottom:.4rem;border-bottom:2px solid #087c79;'
        'color:#0b2d48;font-size:1.35rem}h3{color:#0b4b64}'
        'table{display:block;overflow:auto;border-collapse:collapse;font-size:.87rem;'
        'line-height:1.48;margin:1rem 0 1.4rem}'
        'td,th{border:1px solid #d8e2ea;padding:.5rem .62rem;vertical-align:top;min-width:70px}'
        'th{background:#eaf4f5;white-space:nowrap}tbody tr:nth-child(even){background:#f9fbfc}'
        'a{color:#076979}strong{color:#073b56}code{background:#edf3f6;border-radius:3px;'
        'padding:.1em .28em;overflow-wrap:anywhere}li{margin:.3rem 0}'
        '@media(max-width:720px){main{margin:0;padding:20px 16px;border-radius:0}h1{font-size:1.5rem}}'
    )
    html = (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>DET2：warning 期間持續學習的配對比較</title><style>' + style +
        '</style></head><body><main>' + body + '</main></body></html>\n'
    )
    (OUT / "det2_verdict.html").write_text(html)
    print("rendered", OUT / "det2_verdict.md", OUT / "det2_verdict.html")


if __name__ == "__main__":
    main()
