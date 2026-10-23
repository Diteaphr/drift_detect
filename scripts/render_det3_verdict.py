#!/usr/bin/env python3
"""Render audited DET3 results as a self-contained Markdown and HTML verdict."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "outputs/det3/det3_verdict_data.json").exists():
    ROOT = Path("/Users/diteaphr/Desktop/26 Spring/drift_detect")
OUT = ROOT / "outputs/det3"
S = json.loads((OUT / "det3_verdict_data.json").read_text())

LABEL = {
    "A1-lw0": "P-D（Dual ADWIN，lw0）", "A1-lw1": "P-D1（Dual ADWIN，lw1）",
    "A3-lw0": "P-H（HDDM-A，lw0）", "A3-lw1": "P-H1（HDDM-A，lw1）",
    "F-D0-lw0": "F-D0（完整元件，Dual ADWIN，lw0）",
    "F-D1-lw1": "F-D1（完整系統，Dual ADWIN，lw1）",
    "F-H1-lw1": "F-H1（完整元件，HDDM-A，lw1）",
    "A4-lw0": "DET1-A4（RDDM，lw0）", "A4-lw1": "DET2-A4（RDDM，lw1）",
}
MAIN = ("A1-lw0", "A1-lw1", "A3-lw0", "A3-lw1", "F-D0-lw0", "F-D1-lw1", "F-H1-lw1", "A4-lw0", "A4-lw1")
Q_MAIN = ("Q1_FD1_vs_PH", "Q1_secondary_FH1_vs_PH", "Q2_FD1_vs_FH1")
Q_LABEL = {
    "Q1_FD1_vs_PH": "Q1 主：F-D1 − P-H",
    "Q1_secondary_FH1_vs_PH": "Q1 次：F-H1 − P-H",
    "Q2_FD1_vs_FH1": "Q2：F-D1 − F-H1",
    "Q3_signal_lw0": "Q3 訊號／守衛／逾時：F-D0 − P-D",
    "Q3_learn_full": "Q3 完整系統 lw1：F-D1 − F-D0",
    "Q3_learn_paper": "Q3 論文底座 lw1：P-D1 − P-D",
    "Q3_HDDM_lw1": "",
    "Q3_hddm_components_lw1": "Q3 HDDM-A 完整元件：F-H1 − P-H1",
    "Q3_hddm_full_vs_paper": "Q3 HDDM-A 含 lw1：F-H1 − P-H",
}


def n(v, digits=2, signed=False):
    if v is None:
        return "—"
    return f"{v:+,.{digits}f}" if signed else f"{v:,.{digits}f}"


def i(v):
    return "—" if v is None else f"{v:,}"


def d(item, metric, scale=1, digits=2):
    v = item[metric]
    if v["point"] is None:
        return "—"
    lo, hi = v["ci"]
    return f"{n(v['point']*scale,digits,True)} [{n(lo*scale,digits,True)}, {n(hi*scale,digits,True)}]"


def table(headers, rows):
    return ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|",
            *["| " + " | ".join(str(v) for v in row) + " |" for row in rows], ""]


def main():
    q1 = S["total"]["Q1_FD1_vs_PH"]
    q2 = S["total"]["Q2_FD1_vs_FH1"]
    inj = S["strata"]["groups"]["injected"]["Q1_FD1_vs_PH"]
    caveats = []
    if q1["detection"] == "優於" and (inj["fp"]["point"] > 0 or inj["X"]["point"] < 0):
        caveats.append("偵測優勢依賴曾用於開發的資料")
    if q1["accuracy"] == "優於" and inj["acc"]["point"] < 0:
        caveats.append("準確率優勢依賴曾用於開發的資料")
    title = f"DET3：完整系統對論文 HDDM-A，偵測{q1['detection']}、準確率{q1['accuracy']}"
    lines = [
        "# " + title, "",
        f"**主結論：** Q1 F-D1 對 P-H 的偵測為**{q1['detection']}**（ΔFP {d(q1,'fp')}；ΔX {d(q1,'X')}），全串流準確率為**{q1['accuracy']}**（Δaccuracy 百分點 {d(q1,'acc',100,3)}）。但 X 的 CI 全負，drift 後 accuracy 差為 {d(q1,'post_acc',100,3)} 個百分點且 CI 全負；偵測的「持平」只代表 P1/P2 未同時證實勝負，不能解讀為兩項指標等效。Q2 F-D1 對 F-H1 的偵測為**{q2['detection']}**、全串流準確率為**{q2['accuracy']}**，其 X 與 drift 後 accuracy 也較低。兩軸判定均限於鎖定的單棵 HT 與 205 條配對串流。" + ("**" + "；".join(caveats) + "。**" if caveats else ""),
        "",
        "依[DET3 預註冊](../../docs/ECPF_DET3_預註冊.md)固定 1000 步窗、E11 X、三資料組分層配對 bootstrap 10,000 次（seed `20261012`），95% percentile CI 含 0 判持平。P1 為 FP 差 CI 全負，P2 為 X 差 CI 全正；兩者均朝不利方向才判偵測不如。全串流 accuracy 含無 GT INSECTS，FP/X 與 drift 後 accuracy 僅含 204 條有 GT 串流。CI 描述本批串流的條件不確定性。",
        "", "## Q1／Q2：完整系統的偵測與準確率須分開判", "",
    ]
    comparison_rows = []
    for key in Q_MAIN:
        v = S["total"][key]
        comparison_rows.append([Q_LABEL[key], d(v,"fp"), v["p1"], d(v,"X"), v["p2"],
                                v["detection"], d(v,"acc",100,3), v["accuracy"], d(v,"post_acc",100,3)])
    lines += table(["配對比較", "ΔFP [CI]", "P1", "ΔX [CI]", "P2", "偵測", "Δaccuracy 百分點 [CI]", "準確率", "Δdrift 後 acc. 百分點 [CI]"], comparison_rows)
    lines += ["比較差值均為表中左臂減右臂；FP 越少越好，X 與 accuracy 越大越好。Q1 次列 F-H1 對 P-H 是預先指定的次要比較。Q1/Q2 的 X 差 CI 均全負而 FP 差 CI 含 0，故依事前**雙條件**規則為偵測持平；這不構成 X 等效。兩項 drift 後 accuracy 差 CI 均全負，亦屬已觀察到的代價，未用於改寫預註冊兩軸勝負。", "",
              "## 三組資料揭示效果來源，injected 是未參與 E10bFT 開發的本輪資料", ""]
    group_rows = []
    for g in ("injected", "synthetic", "INSECTS"):
        for key in Q_MAIN:
            v = S["strata"]["groups"][g][key]
            group_rows.append(["injected_paper_electricity（未開發）" if g == "injected" else g,
                               Q_LABEL[key], f"{v['acc']['n']}／{v['fp']['n']}", d(v,"fp"), d(v,"X"),
                               d(v,"acc",100,3), v["detection"], v["accuracy"]])
    lines += table(["資料組", "比較", "accuracy／GT 串流", "ΔFP [CI]", "ΔX [CI]", "Δaccuracy 百分點 [CI]", "偵測方向", "準確率方向"], group_rows)
    lines += ["各資料組 CI 只供方向與穩健性描述，不作另一輪勝負門檻。INSECTS accuracy 層含無 GT 的 incremental 一條；偵測層不含。" + (" Q1 總體優於但 injected 反向：" + "；".join(caveats) + "。" if caveats else ""), "",
              "## 四種漂移型態顯示異質性，不更改總判準", ""]
    type_rows = []
    for t in ("突變", "漸變", "incremental", "recurring"):
        for key in Q_MAIN:
            v = S["strata"]["types"][t][key]
            type_rows.append([t, Q_LABEL[key], f"{v['acc']['n']}／{v['fp']['n']}",
                              d(v,"fp"), d(v,"X"), d(v,"acc",100,3)])
    lines += table(["型態", "比較", "accuracy／GT 串流", "ΔFP [CI]", "ΔX [CI]", "Δaccuracy 百分點 [CI]"], type_rows)
    lines += ["型態按 DET1 命名規則：`abrupt/sudden`、`gradual`、`incremental`、`recurring/reoccurring`；複合標籤可在多個描述層出現，但總判定每串流只計一次。", "",
              "## Q3：換訊號與 warning 持續學習的組合效果", ""]
    q3rows = []
    for key in ("Q3_signal_lw0", "Q3_learn_full", "Q3_learn_paper", "Q3_hddm_components_lw1", "Q3_hddm_full_vs_paper"):
        v = S["total"][key]
        q3rows.append([Q_LABEL[key], d(v,"fp"), d(v,"X"), d(v,"acc",100,3), d(v,"post_acc",100,3)])
    lines += table(["描述性對比", "ΔFP [CI]", "ΔX [CI]", "Δaccuracy 百分點 [CI]", "Δdrift 後 acc. 百分點 [CI]"], q3rows)
    q3_signal = S["total"]["Q3_signal_lw0"]
    q3_learn_full = S["total"]["Q3_learn_full"]
    q3_learn_paper = S["total"]["Q3_learn_paper"]
    lines += [
        f"Q3 的點估計顯示：F-D0 相對 P-D 減少 FP {n(-q3_signal['fp']['point'],0)}、增加 X {n(q3_signal['X']['point'])}，全串流 accuracy 提高 {n(q3_signal['acc']['point']*100,3)} 個百分點，三項 CI 均朝有利方向。完整底座開啟 lw1 再提高 accuracy {n(q3_learn_full['acc']['point']*100,3)} 個百分點；論文底座的 lw1 對比為 {n(q3_learn_paper['acc']['point']*100,3)} 個百分點。這是點估計大小的描述，不是兩個 lw1 效果差異的顯著性檢定。",
        "F-D0−P-D 同時加入 frozen reference、守衛與逾時，不能稱為 reference 的純因果效果。F-D1−F-D0 與 P-D1−P-D 分別描述不同底座上的 lw1 對比；不做跨對比的顯著性判定。", "",
              "## DET1＋DET2＋DET3 總表支援同母體對照", ""]
    overall_rows = []
    for arm in MAIN:
        v = S["by_arm"][arm]
        overall_rows.append([LABEL[arm], n(v["acc"],4), n(v["post_acc"],4), i(v["fp"]), i(v["hits"]),
                             n(v["C"]), n(v["X"]), n(v["mdt"],1), n(v["kappa"],4),
                             i(v["frozen"]), n(v["runtime"]/60,1)])
    lines += table(["組別", "preq. accuracy", "drift 後 accuracy", "FP@1000", "episode hits", "C", "X", "MDT 步", "kappa", "凍結步數", "CPU 分"], overall_rows)
    lines += ["總表 accuracy 按全 205 條可計分預測數加權；偵測指標與 drift 後 accuracy 只用 204 條有 GT 串流。CPU 分為 205 次 run 的 runtime 合計，非 6 workers 牆上時間。RDDM 僅供前輪脈絡，不進本輪 Q1/Q2。", "",
              "## Warning 生命週期與無 GT 串流提供機制核對", ""]
    event_rows = []
    for arm in MAIN:
        c = S["warnings"][arm];v = S["by_arm"][arm]
        count = lambda prefix: sum(num for key,num in c.items() if key.startswith(prefix))
        event_rows.append([LABEL[arm], i(count("open:")), i(c.get("close:confirmed",0)),
                           i(c.get("close:zone_exit",0)), i(c.get("close:timeout",0)),
                           i(c.get("close:reference_switch",0)), i(count("censored:")), i(v["frozen"])])
    lines += table(["組別", "開啟", "確認", "zone 離區", "逾時", "reference switch 關閉", "截尾", "凍結步數"], event_rows)
    lines += ["每 run 驗證開啟 = 各種關閉 + 截尾。Reference switch 若沒有開啟中的 warning，不產生 warning 關閉事件；[階段三 trace 診斷](stage3_trace_diagnostics.json)另核實 reference switch 與守衛欄位。", ""]
    ngrows = []
    for arm in MAIN:
        v=S["no_gt"][arm]
        ngrows.append([LABEL[arm], n(v["acc"],4), i(v["alarms"]), n(v["runtime"],2)])
    lines += table(["insects_incremental_balanced（無 GT）", "preq. accuracy", "警報數", "CPU 秒"], ngrows)
    lines += ["無 GT 串流只描述 accuracy、警報數、runtime，不計 TP／FP／C／X。", "",
              "## 正式矩陣已完成來源與計分稽核", "",
              f"新跑固定 commit `{S['metadata']['det3_commit']}`；DET1／DET2 沿用 commit `{S['metadata']['det1_commit']}`／`{S['metadata']['det2_commit']}`。新跑 615／615、失敗 0；每臂 160 injected、40 synthetic、5 INSECTS。逐 run 驗證 preset、registry、來源 SHA-256、乾淨 commit、River 0.21.2、GT、同串流 `y_true`、warning 守恆與 evaluator TP／FP／FN。詳見[逐 run 分數](det3_run_scores.csv)、[資料與 CI](det3_verdict_data.json)、[正式完整性紀錄](formal_integrity_20261013.md)及[重現／smoke](stage3_gate_smoke.md)。原始 run 在本機 git-ignored `outputs/benchmark/det3/`，與前輪及 smoke 隔離。", "",
              "## 事後觀察只協助解釋，不新增判準", "",
              f"- F-D0 的凍結步數 {i(S['by_arm']['F-D0-lw0']['frozen'])}，相較 P-D 的 {i(S['by_arm']['A1-lw0']['frozen'])} 大幅下降；F-D1 為 0。reference、守衛、逾時及後續 detector 狀態一同改變，不能將差額單獨歸因於某個元件。",
              f"- F-D1 的 CPU 成本 {n(S['by_arm']['F-D1-lw1']['runtime']/60,1)} 分，高於 P-H 的 {n(S['by_arm']['A3-lw0']['runtime']/60,1)} 分；這是 205 條 run 的加總，不是實際牆上耗時。",
              "- injected 的 Q1 accuracy 點差略為負、FP CI 全正；synthetic 與 INSECTS 的 accuracy 點差為正。此異質性支持資料重疊註記，但不據此挑選子組重定義主要勝負。", "",
              "## 限制界定可外推範圍", "",
              "只有單一 Hoeffding Tree，不外推到森林；synthetic 不是新 holdout；injected 每格只用 registry 前 20 trials；Dual ADWIN 採 River 0.21.2，不直接等同 MOA。E10bFT 元件曾在 synthetic、部分 INSECTS 與其他注入型 electricity 資料上開發；本輪 `injected_paper_electricity` 未參與開發，但也不是對所有元件獨立、全新分布的外部驗證。", "",
              "## 偏離與失敗與缺漏", "",
              "正式執行沒有失敗或缺漏；四個沿用組別通過 60／60 逐位元閘門。階段三 CLI 子字串篩選多跑 16 個 synthetic 隔離檢查、INSECTS 首次 0-run 空 CSV 後於新隔離目錄重跑，均未進正式分析，詳見[階段三紀錄](stage3_gate_smoke.md)。", "",
    ]
    md = "\n".join(lines)
    (OUT / "det3_verdict.md").write_text(md)
    import markdown
    body = markdown.markdown(md, extensions=["tables", "fenced_code"])
    style = ('body{margin:0;background:#f2f5f7;color:#19283a;font:16px/1.72 -apple-system,'
             'BlinkMacSystemFont,"Noto Sans TC","PingFang TC",sans-serif}'
             'main{max-width:1300px;margin:28px auto;padding:36px 42px;background:white;'
             'border:1px solid #d8e2ea;border-radius:10px;box-shadow:0 6px 24px #122d440b}'
             'h1{color:#0b2d48;line-height:1.25;font-size:2rem}'
             'h2{margin-top:2.4rem;padding-bottom:.4rem;border-bottom:2px solid #087c79;'
             'color:#0b2d48;font-size:1.35rem}'
             'table{display:block;overflow:auto;border-collapse:collapse;font-size:.87rem;line-height:1.48;margin:1rem 0 1.4rem}'
             'td,th{border:1px solid #d8e2ea;padding:.5rem .62rem;vertical-align:top;min-width:70px}'
             'th{background:#eaf4f5;white-space:nowrap}tbody tr:nth-child(even){background:#f9fbfc}'
             'a{color:#076979}strong{color:#073b56}code{background:#edf3f6;border-radius:3px;padding:.1em .28em;overflow-wrap:anywhere}'
             '@media(max-width:720px){main{margin:0;padding:20px 16px;border-radius:0}h1{font-size:1.5rem}}')
    html = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>DET3：完整系統對 ECPF 論文</title><style>' + style +
            '</style></head><body><main>' + body + '</main></body></html>\n')
    (OUT / "det3_verdict.html").write_text(html)
    print("rendered", OUT / "det3_verdict.md", OUT / "det3_verdict.html")


if __name__ == "__main__":
    main()
