#!/usr/bin/env python3
"""Analysis of the routed-confirmation experiment (docs/ECPF_ROUTED_預註冊.md).

Scores runs with the DET4 definitions (scripts/analyze_det4_formal.py): prequential
accuracy, accuracy in the 1,000 steps after each GT drift, FP@1000, E11 excess hits
X, and compares arms with DET4's stratified paired bootstrap (10,000 draws, seed
20261012) and verdict rules. Baselines are read from the existing DET score tables,
never re-run: ``det4_s1_wadwin_cadwin`` (ADWIN only), ``det4_s1_whddma_chddma``
(HDDM-A only) from outputs/det4/det4_run_scores.csv and DET3 ``F-D0-lw0``
(e10bft, learn-during-warning off) from outputs/det3/det3_run_scores.csv.

  python3 scripts/analyze_routed.py gate    # fixed routes vs DET4 rows, must match exactly
  python3 scripts/analyze_routed.py dev     # cooldown selection on synthetic_binary
  python3 scripts/analyze_routed.py formal  # pre-registered comparisons -> outputs/routed/
  python3 scripts/analyze_routed.py followup  # exploratory: decision at 300 steps, injected datasets
  python3 scripts/analyze_routed.py simpleclf # exploratory: design 1 with the simple-baseline classifier
  python3 scripts/analyze_routed.py oracle    # exploratory: routing by the true drift type (upper bound)
  python3 scripts/analyze_routed.py step01    # exploratory: cooldown control + design 1 decided at HDDM-A's drift
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from scripts.analyze_det1_formal import union_length, windows  # noqa: E402
import scripts.analyze_det4_formal as det4  # noqa: E402
from scripts.analyze_det4_formal import (  # noqa: E402
    INSECTS, accuracy_verdict, add_post_accuracy, aggregate, detection_verdict, expected_sources, paired_delta,
)
from scripts.run_benchmark import load_stream  # noqa: E402
from src.metrics.evaluate_run import detection_metrics  # noqa: E402

_det4_t1_group = det4.t1_group


def _strata(dataset: str) -> str:
    """DET4's bootstrap strata, extended so every injected_paper_* dataset is 'injected'."""
    return "injected" if dataset.startswith("injected_paper_") else _det4_t1_group(dataset)


det4.t1_group = _strata  # paired_delta looks the strata up through this module attribute

ROOT = REPO / "outputs" / "benchmark_routed"
OUT = REPO / "outputs" / "routed"
REGISTRY = json.loads((REPO / "configs/datasets_0921.json").read_text())["datasets"]
FORMAL_DATASETS = (*sorted(INSECTS), "synthetic_multiclass")
DEV_DATASET = "synthetic_binary"
POLICY_SHORT = {"first_warner": "fw", "type_classifier": "tr", "union": "union"}
ARM_LABEL = {
    "fw": "設計 2：誰先發誰確認",
    "tr": "設計 1：分類器分流",
    "union": "聯集",
    "adwin": "只用 ADWIN（DET4 S1）",
    "hddma": "只用 HDDM-A（DET4 S1）",
    "e10bft_lw0": "e10bft lw0（DET3 F-D0-lw0）",
    "hddma_adwin": "HDDM-A warning + ADWIN 確認（DET4 S1）",
    "adwin_hddma": "ADWIN warning + HDDM-A 確認（DET4 S1）",
    "tr300": "設計 1（第 300 步判斷）",
    "trs300": "設計 1・簡單基準（第 300 步判斷）",
    "oracle": "理想分流（真實類型：sudden → HDDM-A，其他 → ADWIN）",
    "anti": "反向分流（真實類型：sudden → ADWIN，其他 → HDDM-A）",
    "gate": "設計 1b（HDDM-A 發出 drift 時判斷，簡單基準）",
    "hddma_c300": "只用 HDDM-A + 冷卻期 300",
}
INJECTED_DATASETS = ("injected_paper_electricity", "injected_paper_gas_sensor_drift")
FOLLOWUP_PRESETS = {"tr300": "s1route_tr_d300_c300", "tr": "s1route_tr_c300",
                    "fw": "s1route_fw_c300", "union": "s1route_union_c300"}
# DET4 S1 2x2 of warning x confirm detectors (the two diagonals and the two mixed cells).
BASELINES = {"adwin": ("det4", "det4_s1_wadwin_cadwin"), "hddma": ("det4", "det4_s1_whddma_chddma"),
             "hddma_adwin": ("det4", "det4_s1_whddma_cadwin"), "adwin_hddma": ("det4", "det4_s1_wadwin_chddma"),
             "e10bft_lw0": ("det3", "F-D0-lw0")}
GATE_PAIRS = {"s1route_fixed_adwin": "det4_s1_wadwin_cadwin", "s1route_fixed_hddma": "det4_s1_whddma_chddma"}
EXACT = ["n_scored", "correct", "alarms", "tp", "fp", "fn", "hits", "post_correct", "post_count",
         "warning_opened", "warning_self_closed", "warning_timeout", "confirmations"]
SUDDEN_TYPES = {"sudden", "recurring_sudden"}


def group_of(dataset: str, stream: str, cell: Optional[str] = None) -> str:
    """Reporting groups: each INSECTS dataset, synthetic_multiclass by type, injected by cell."""
    if dataset in INSECTS:
        return dataset
    if dataset.startswith("injected_"):
        return f"{dataset}:{cell}"
    parts = stream.split("_")
    return f"{dataset}:{'_'.join(parts[:2]) if parts[0] == 'recurring' else parts[0]}"


def true_type(group: str) -> Optional[str]:
    """Known drift type of a group: synthetic by generator, injected abrupt -> sudden."""
    if ":" not in group:
        return None
    kind = group.split(":", 1)[1]
    if kind.startswith("abrupt"):
        return "sudden"
    if kind.startswith("gradual"):
        return "gradual"
    return kind


def _none(value: Any) -> Any:
    return None if value is None or (isinstance(value, float) and math.isnan(value)) else value


def _same(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return float(a) == float(b)


# -- scoring -----------------------------------------------------------------------
def score_run(path: Path, allow_smoke: bool = False) -> Dict[str, Any]:
    """DET4's score_run without its DET4-only provenance checks."""
    manifest = json.loads((path / "manifest.json").read_text())
    metrics = json.loads((path / "metrics.json").read_text())
    events = json.loads((path / "warning_events.json").read_text())
    routing_path = path / "routing_events.json"
    routing = json.loads(routing_path.read_text()) if routing_path.exists() else None
    assert manifest["record_warning_events"], path
    assert allow_smoke or manifest["max_steps"] is None, path
    assert manifest["effective_config"]["ecpf_learn_during_warning"] is True, path

    opened = sum(e["event"] == "open" for e in events)
    closed = sum(e["event"] in ("close", "censored") for e in events)
    assert opened == closed, path
    confirmed = [e for e in events if e["event"] == "close" and e["reason"] == "confirmed"]
    key = "input_index" if manifest["coordinates"] == "input" else "index"
    alarms_all = np.array([e[key] for e in confirmed], dtype=int)
    assert int((alarms_all >= manifest["detect_from"]).sum()) == metrics["n_alarms"], path

    n = manifest["n_input"]
    scored_start = max(manifest["detect_from"], manifest["warm_start"])
    gt = [tuple(v) for v in (manifest["gt_intervals"] or [])]
    scored_gt = [(s, e) for s, e in gt if scored_start <= s < n]
    alarms = alarms_all[alarms_all >= scored_start]
    counts = collections.Counter(f"{e['event']}:{e['reason']}" for e in events)
    dataset, stream = manifest["dataset"], manifest["stream"]
    row: Dict[str, Any] = {
        "dataset": dataset, "stream": stream, "arm": manifest["preset"]["name"],
        "group": group_of(dataset, stream, manifest.get("cell")), "n_input": n,
        "coordinates": manifest["coordinates"],
        "n_scored": metrics["n_scored"],
        "correct": int(round(metrics["acc_prequential"] * metrics["n_scored"])),
        "acc": metrics["acc_prequential"], "post_correct": None, "post_count": None,
        "gt": len(scored_gt), "gt_intervals": gt, "alarms": len(alarms),
        "frozen": metrics.get("warning_frozen_steps", 0),
        "warning_opened": sum(v for k, v in counts.items() if k.startswith("open:")),
        "warning_self_closed": counts["close:zone_exit"],
        "warning_timeout": counts["close:timeout"],
        "confirmations": counts["close:confirmed"],
        "runtime_s": manifest["runtime_s"],
        "concurrent_runs": manifest.get("cost", {}).get("concurrent_runs"),
        "routing": routing,
        "path": str(path.relative_to(REPO)),
    }
    if not scored_gt:
        row.update(tp=None, fp=None, fn=None, hits=None, C=None, X=None, mdt=None)
        return row
    det = detection_metrics(alarms, scored_gt, n_instances=n, delta_max=1000, anchor="start")
    win = windows(gt, n, scored_start)
    outside = n - scored_start - union_length(win)
    assert outside > 0, path
    chance = sum(-math.expm1(-det["fp"] / outside * (e - s + 1)) for s, e in win)
    hits = det["n_episodes"] - det["fn"]
    row.update(tp=det["tp"], fp=det["fp"], fn=det["fn"], hits=hits, C=chance, X=hits - chance,
               mdt=det["mdt"])
    return row


def load_runs(presets: List[str], datasets: List[str], root: Path, allow_smoke: bool) -> List[Dict]:
    rows = []
    for dataset in datasets:
        for preset in presets:
            for run_dir in sorted((root / dataset / preset).glob("*/manifest.json")):
                rows.append(score_run(run_dir.parent, allow_smoke))
    add_post_accuracy(rows, datasets=tuple(datasets))
    return rows


def load_baselines(datasets: List[str]) -> List[Dict]:
    det4 = pd.read_csv(REPO / "outputs/det4/det4_run_scores.csv", low_memory=False)
    det3 = pd.read_csv(REPO / "outputs/det3/det3_run_scores.csv", low_memory=False)
    rows = []
    for arm, (source, name) in BASELINES.items():
        table = det4[det4.preset == name] if source == "det4" else det3[det3.arm == name]
        for _, r in table[table.dataset.isin(datasets)].iterrows():
            row = {k: _none(r.get(k)) for k in
                   ("dataset", "stream", "n_scored", "correct", "gt", "alarms", "tp", "fp", "fn",
                    "hits", "C", "X", "post_correct", "post_count", "mdt", "warning_opened",
                    "warning_self_closed", "warning_timeout", "confirmations")}
            row.update(arm=arm, group=group_of(row["dataset"], row["stream"], _none(r.get("cell"))),
                       source=f"{source}:{name}",
                       frozen=_none(r.get("frozen_steps", r.get("frozen"))) or 0)
            rows.append(row)
    return rows


# -- comparisons -------------------------------------------------------------------
def lookup_of(rows: List[Dict]) -> Dict:
    return {(r["dataset"], r["stream"], r["arm"]): r for r in rows}


def compare(lookup: Dict, arm: str, base: str, stratify: bool = True) -> Dict:
    keys = {(d, s) for d, s, a in lookup if a == arm} & {(d, s) for d, s, a in lookup if a == base}
    result = {m: paired_delta(lookup, arm, base, keys, m, stratify) for m in ("acc", "post_acc", "fp", "X")}
    result.update(detection=detection_verdict(result["fp"]["ci"], result["X"]["ci"]),
                  accuracy=accuracy_verdict(result["acc"]["ci"]), streams=len(keys))
    return result


def summary(rows: List[Dict]) -> Dict:
    s = aggregate(rows)
    if not any(r.get("mdt") is not None for r in rows if r["gt"]):
        s["mdt"] = None  # DET3's score table has no delay column
    return {k: s[k] for k in ("streams", "gt", "acc", "post_acc", "alarms", "fp", "X", "mdt")}


# -- routing diagnostics -----------------------------------------------------------
_POSITIONS: Dict[tuple, np.ndarray] = {}


def gt_in_output(row: Dict) -> List[tuple]:
    """GT intervals in pipeline (output) positions, where routing episodes are timed.

    Injected streams are scored in input coordinates; the generator drops rows, so
    map each interval through the stream's kept-row positions (as add_post_accuracy does).
    """
    gt = row["gt_intervals"]
    if row.get("coordinates") != "input" or not gt:
        return gt
    key = (row["dataset"], row["stream"])
    if key not in _POSITIONS:
        source = next(s for s in expected_sources(row["dataset"]) if s["stem"] == row["stream"])
        _POSITIONS[key] = np.asarray(load_stream(source, REGISTRY[row["dataset"]])["kept"])
    pos = _POSITIONS[key]
    return [(int(np.searchsorted(pos, s)), int(np.searchsorted(pos, e, side="right")) - 1) for s, e in gt]


def routing_diagnostics(rows: List[Dict]) -> Dict:
    out: Dict[str, Any] = {}
    for arm in sorted({r["arm"] for r in rows if r.get("routing")}):
        eps, blocked = [], 0
        for r in rows:
            if r["arm"] != arm or not r.get("routing"):
                continue
            blocked += r["routing"]["cooldown_blocked"]
            gt = gt_in_output(r)
            for ep in r["routing"]["episodes"]:
                drift = next((s for s, e in gt if s <= ep["open_t"] <= e + 1000), None)
                true = true_type(r["group"]) if drift is not None else None
                eps.append(dict(ep, group=r["group"], at_drift=drift is not None, true_type=true,
                                offset=None if drift is None else ep["open_t"] - drift))
        ends = collections.Counter(ep["end_reason"] for ep in eps)
        openers = collections.Counter(ep["opener"] for ep in eps)
        confirmed = [ep for ep in eps if ep["end_reason"] == "confirmed"]
        typed = [ep for ep in eps if ep["true_type"] is not None]
        classifier = {}
        for at in ("100", "200", "300", "confirm"):
            pairs = [(ep["observed_types"][at] == "sudden", ep["true_type"] in SUDDEN_TYPES)
                     for ep in typed if at in ep["observed_types"]]
            if pairs:
                classifier[at] = {
                    "n": len(pairs), "accuracy": float(np.mean([p == t for p, t in pairs])),
                    "sudden_recall": _rate([p for p, t in pairs if t]),
                    "non_sudden_recall": _rate([not p for p, t in pairs if not t]),
                }
        opener_match = [(ep["opener"] == "hddma") == (ep["true_type"] in SUDDEN_TYPES) for ep in typed]
        out[arm] = {
            "episodes": len(eps), "end_reasons": dict(ends), "opener_share": dict(openers),
            "confirmed_by": dict(collections.Counter(ep.get("confirmed_by") for ep in confirmed)),
            "ignored_drifts": int(sum(ep["ignored_drifts"] for ep in eps)),
            "cooldown_blocked": blocked,
            "episodes_at_gt_drift": len(typed),
            "opener_matches_type": float(np.mean(opener_match)) if opener_match else None,
            "classifier_sudden_vs_not": classifier,
        }
    return out


def _rate(values: List[bool]) -> Optional[float]:
    return float(np.mean(values)) if values else None


# -- modes -------------------------------------------------------------------------
def run_gate(args) -> None:
    datasets = args.datasets or list(FORMAL_DATASETS)
    rows = load_runs(list(GATE_PAIRS), datasets, args.root, allow_smoke=False)
    det4 = pd.read_csv(REPO / "outputs/det4/det4_run_scores.csv", low_memory=False)
    lines, bad = ["| preset | dataset | stream | result | differing fields |", "|---|---|---|---|---|"], 0
    for r in rows:
        ref = det4[(det4.preset == GATE_PAIRS[r["arm"]]) & (det4.dataset == r["dataset"]) & (det4.stream == r["stream"])]
        assert len(ref) == 1, (r["arm"], r["stream"])
        ref = ref.iloc[0]
        diff = [f for f in EXACT if not _same(_none(ref[f]), r[f])]
        if r["X"] is not None and _none(ref["X"]) is not None and abs(r["X"] - ref["X"]) > 1e-9:
            diff.append("X")
        bad += bool(diff)
        lines.append(f"| {r['arm']} | {r['dataset']} | {r['stream']} | {'相同' if not diff else '不同'} | {', '.join(diff)} |")
    OUT.mkdir(parents=True, exist_ok=True)
    verdict = "通過" if bad == 0 and rows else "未通過"
    text = "\n".join([f"# 分流確認：可重現性閘門 {verdict}", "",
                      f"**結論：** {len(rows) - bad}/{len(rows)} 個 run 的 {', '.join(EXACT)} 與 X 和 DET4 完全相同。", ""] + lines)
    (OUT / (args.gate_name or "gate.md")).write_text(text + "\n")
    print(text.splitlines()[2])
    sys.exit(0 if verdict == "通過" else 1)


def run_dev(args) -> None:
    presets = [f"s1route_{p}_c{c}" for p in POLICY_SHORT.values() for c in (0, 100, 300)]
    rows = load_runs(presets, [DEV_DATASET], args.root, allow_smoke=False)
    table, choice = [], {}
    for short in POLICY_SHORT.values():
        stats = {c: summary([r for r in rows if r["arm"] == f"s1route_{short}_c{c}"]) for c in (0, 100, 300)}
        x0 = stats[0]["X"]
        ok = [c for c in (0, 100, 300) if stats[c]["X"] <= x0 + 1e-9]
        best = max(ok, key=lambda c: (round(stats[c]["acc"], 12), -c))
        choice[short] = best
        for c, s in stats.items():
            table.append({"policy": short, "cooldown": c, **s, "chosen": c == best})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dev_selection.json").write_text(json.dumps({"choice": choice, "table": table}, indent=2))
    lines = ["# 分流確認：dev 冷卻期選擇（synthetic_binary）", "",
             "規則（預註冊）：X 不高於 C=0 的前提下取 accuracy 最高；同分取較小的 C。", "",
             "| 設計 | C | accuracy | drift 後 accuracy | FP | X | 平均延遲 | 選定 |", "|---|---|---|---|---|---|---|---|"]
    for t in table:
        lines.append(f"| {t['policy']} | {t['cooldown']} | {t['acc']:.4f} | {t['post_acc']:.4f} | {t['fp']} | "
                     f"{t['X']:.2f} | {t['mdt']:.1f} | {'✓' if t['chosen'] else ''} |")
    (OUT / "dev_selection.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(choice))


def run_formal(args) -> None:
    selection = json.loads((OUT / "dev_selection.json").read_text())
    # "final" holds the cooldowns after a preregistration amendment; "choice" the rule's own pick.
    choice = selection.get("final", selection["choice"])
    presets = {short: f"s1route_{short}_c{c}" for short, c in choice.items()}
    rows = load_runs(list(presets.values()), list(FORMAL_DATASETS), args.root, args.allow_smoke)
    for r in rows:
        r["arm"] = next(k for k, v in presets.items() if v == r["arm"])
    rows += load_baselines(list(FORMAL_DATASETS))
    lookup = lookup_of(rows)
    arms = ["tr", "fw", "union", "hddma", "adwin", "hddma_adwin", "adwin_hddma", "e10bft_lw0"]
    # The first three pairs are preregistered (H1-H3); the rest are descriptive.
    comps = {f"{a}_vs_{b}": compare(lookup, a, b)
             for a, b in [("fw", "hddma"), ("tr", "fw"), ("fw", "union"), ("tr", "hddma"),
                          ("union", "hddma"), ("fw", "adwin"), ("tr", "adwin"), ("union", "adwin"),
                          ("fw", "e10bft_lw0"), ("tr", "e10bft_lw0"), ("union", "e10bft_lw0"),
                          ("tr", "hddma_adwin"), ("fw", "hddma_adwin"), ("union", "hddma_adwin"),
                          ("tr", "adwin_hddma"), ("hddma_adwin", "hddma"), ("adwin_hddma", "adwin")]}
    pooled = {a: summary([r for r in rows if r["arm"] == a]) for a in arms}
    groups = sorted({r["group"] for r in rows})
    by_group = {g: {a: summary([r for r in rows if r["arm"] == a and r["group"] == g]) for a in arms} for g in groups}
    diag = routing_diagnostics(rows)
    hyp = {
        "H1": {"claim": "設計 2 不比只用 HDDM-A 差", "comparison": "fw_vs_hddma",
               "holds": comps["fw_vs_hddma"]["accuracy"] != "不如" and comps["fw_vs_hddma"]["detection"] != "不如"},
        "H2": {"claim": "設計 1 的 accuracy 優於設計 2", "comparison": "tr_vs_fw",
               "holds": comps["tr_vs_fw"]["accuracy"] == "優於"},
        "H3": {"claim": "設計 2 的偵測優於聯集", "comparison": "fw_vs_union",
               "holds": comps["fw_vs_union"]["detection"] == "優於"},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"presets": presets, "hypotheses": hyp, "comparisons": comps, "pooled": pooled,
            "by_group": by_group, "routing": diag, "smoke": args.allow_smoke}
    (OUT / "routed_verdict_data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    pd.DataFrame([{k: v for k, v in r.items() if k not in ("routing", "gt_intervals")} for r in rows]).to_csv(
        OUT / "routed_run_scores.csv", index=False)
    write_report(data, groups, arms)
    print({k: v["holds"] for k, v in hyp.items()})


FOLLOWUP_PAIRS = {
    "original": [("tr300", "tr"), ("tr300", "fw"), ("tr300", "union"), ("tr300", "hddma"), ("tr300", "adwin"),
                 ("tr300", "hddma_adwin"), ("tr300", "adwin_hddma"), ("tr300", "e10bft_lw0")],
    "injected": [("fw", "hddma"), ("tr300", "fw"), ("fw", "union"), ("tr300", "hddma"), ("union", "hddma"),
                 ("tr300", "adwin"), ("fw", "adwin"), ("union", "adwin"), ("tr300", "hddma_adwin"),
                 ("fw", "hddma_adwin"), ("tr300", "adwin_hddma"), ("hddma_adwin", "hddma"), ("adwin_hddma", "adwin"),
                 ("tr300", "e10bft_lw0")],
}
FOLLOWUP_ARMS = {"original": ["tr300", "tr", "fw", "union", "hddma", "adwin", "hddma_adwin", "adwin_hddma", "e10bft_lw0"],
                 "injected": ["tr300", "fw", "union", "hddma", "adwin", "hddma_adwin", "adwin_hddma", "e10bft_lw0"]}


SIMPLECLF_PRESETS = dict(FOLLOWUP_PRESETS, trs300="s1route_trsimple_d300_c300")
SIMPLECLF_PAIRS = [("trs300", "tr300"), ("trs300", "fw"), ("trs300", "union"), ("trs300", "hddma"),
                   ("trs300", "adwin"), ("trs300", "hddma_adwin"), ("trs300", "adwin_hddma")]
SIMPLECLF_ARMS = ["trs300", "tr300", "fw", "union", "hddma", "adwin", "hddma_adwin", "adwin_hddma"]


def run_followup(args) -> None:
    """Exploratory follow-up (preregistration amendment 2): decision at 300 warning steps,
    and all designs on injected_paper_electricity / injected_paper_gas_sensor_drift."""
    _followup_like(args, FOLLOWUP_PRESETS, FOLLOWUP_ARMS, FOLLOWUP_PAIRS, "followup")


def run_simpleclf(args) -> None:
    """Exploratory: design 1 with the simple-baseline classifier (scripts/typeclf_retrain.py
    export, cross-fitted on split B) against design 1 with Type-LDD, design 2, union and DET4."""
    _followup_like(args, SIMPLECLF_PRESETS, {"original": SIMPLECLF_ARMS, "injected": SIMPLECLF_ARMS},
                   {"original": SIMPLECLF_PAIRS, "injected": SIMPLECLF_PAIRS}, "simpleclf")


# Oracle routing: each stream has one drift type, so routing by the true type with no
# decision delay is the DET4 diagonal of that type's detector, taken stream by stream.
ORACLE_ARMS = ["oracle", "anti", "trs300", "tr300", "fw", "union", "hddma", "adwin"]
ORACLE_PAIRS = [("oracle", "hddma"), ("oracle", "adwin"), ("oracle", "fw"), ("oracle", "union"),
                ("oracle", "trs300"), ("oracle", "tr300"), ("oracle", "anti")]
INSECTS_TYPE = {"insects_abrupt_balanced": "sudden", "insects_incremental_balanced": "incremental",
                "insects_incremental_gradual_balanced": "gradual",
                "insects_incremental_reoccurring_balanced": "incremental"}  # abrupt+incremental mix: no oracle


def stream_type(row: Dict) -> Optional[str]:
    return INSECTS_TYPE.get(row["dataset"]) if row["dataset"] in INSECTS else true_type(row["group"])


def oracle_rows(rows: List[Dict], keep_untyped: bool = False) -> List[Dict]:
    """Add the oracle and reversed-oracle arms; keep only streams with a known type
    unless ``keep_untyped`` (then the other arms keep every stream)."""
    lookup = lookup_of(rows)
    out = []
    for r in rows:
        if r["arm"] != "hddma" or stream_type(r) is None:
            continue
        sudden = stream_type(r) in SUDDEN_TYPES
        for arm, pick in (("oracle", "hddma" if sudden else "adwin"), ("anti", "adwin" if sudden else "hddma")):
            out.append(dict(lookup[(r["dataset"], r["stream"], pick)], arm=arm, routed_to=pick))
    typed = {(r["dataset"], r["stream"]) for r in out}
    return [r for r in rows if keep_untyped or (r["dataset"], r["stream"]) in typed] + out


def run_oracle(args) -> None:
    """Exploratory upper bound of type routing: the true type picks the confirming detector."""
    _followup_like(args, SIMPLECLF_PRESETS, {"original": ORACLE_ARMS, "injected": ORACLE_ARMS},
                   {"original": ORACLE_PAIRS, "injected": ORACLE_PAIRS}, "oracle", extend=oracle_rows)


# Amendment 4: step 0 (HDDM-A with the designs' cooldown) and step 1 (hddma_gate).
STEP01_PRESETS = dict(SIMPLECLF_PRESETS, gate="s1route_gate_simple_c300", hddma_c300="s1route_fixed_hddma_c300")
STEP01_ARMS = ["gate", "hddma_c300", "trs300", "fw", "union", "hddma", "adwin", "oracle"]
STEP01_PAIRS = [
    # preregistered criteria for step 1
    ("gate", "hddma"), ("gate", "adwin"), ("gate", "hddma_c300"), ("gate", "trs300"),
    # descriptive
    ("gate", "fw"), ("gate", "union"), ("gate", "oracle"),
    # step 0: the cooldown alone, and the routing net of the cooldown
    ("hddma_c300", "hddma"), ("fw", "hddma_c300"), ("union", "hddma_c300"),
]


def run_step01(args) -> None:
    """Exploratory (amendment 4): cooldown control and design 1 decided at HDDM-A's drift."""
    _followup_like(args, STEP01_PRESETS, {"original": STEP01_ARMS, "injected": STEP01_ARMS},
                   {"original": STEP01_PAIRS, "injected": STEP01_PAIRS}, "step01",
                   extend=lambda rows: oracle_rows(rows, keep_untyped=True))


def _followup_like(args, all_presets: Dict[str, str], arms_of: Dict[str, List[str]],
                   pairs_of: Dict[str, List[tuple]], name: str, extend=None) -> None:
    scopes = {"original": list(FORMAL_DATASETS), "injected": list(INJECTED_DATASETS)}
    data: Dict[str, Any] = {"presets": all_presets, "smoke": args.allow_smoke}
    for scope, datasets in scopes.items():
        presets = {a: p for a, p in all_presets.items() if a in arms_of[scope]}
        rows = load_runs(list(presets.values()), datasets, args.root, args.allow_smoke)
        for r in rows:
            r["arm"] = next(k for k, v in presets.items() if v == r["arm"])
        rows += load_baselines(datasets)
        if extend is not None:
            rows = extend(rows)
        lookup = lookup_of(rows)
        arms = [a for a in arms_of[scope] if any(r["arm"] == a for r in rows)]
        groups = sorted({r["group"] for r in rows})
        data[scope] = {
            "arms": arms,
            "comparisons": {f"{a}_vs_{b}": compare(lookup, a, b) for a, b in pairs_of[scope]},
            "pooled": {a: summary([r for r in rows if r["arm"] == a]) for a in arms},
            "by_group": {g: {a: summary([r for r in rows if r["arm"] == a and r["group"] == g]) for a in arms}
                         for g in groups},
            "routing": routing_diagnostics(rows),
        }
        pd.DataFrame([{k: v for k, v in r.items() if k not in ("routing", "gt_intervals")} for r in rows]).to_csv(
            OUT / f"{name}_{scope}_run_scores.csv", index=False)
        print(scope, {a: round(s["acc"], 4) for a, s in data[scope]["pooled"].items() if s["acc"] is not None})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}_verdict_data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def _f(v: Any, nd: int = 4) -> str:
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def _ci(d: Dict, scale: float = 1.0, nd: int = 3) -> str:
    if d["point"] is None:
        return "—"
    ci = "" if d["ci"] is None else f" [{d['ci'][0] * scale:+.{nd}f}, {d['ci'][1] * scale:+.{nd}f}]"
    return f"{d['point'] * scale:+.{nd}f}{ci}"


def write_report(data: Dict, groups: List[str], arms: List[str]) -> None:
    hyp, comps, pooled = data["hypotheses"], data["comparisons"], data["pooled"]
    lines = ["# 分流確認實驗結果", ""]
    if data["smoke"]:
        lines += ["**冒煙測試結果，不可作為結論。**", ""]
    lines += ["依 [預註冊](../../docs/ECPF_ROUTED_預註冊.md) 判定。差值 = 前者 − 後者；accuracy 單位為百分點；"
              "CI 為分層配對 bootstrap 10,000 次（seed 20261012）的 95% 區間。", "",
              "## 假設判定", "", "| 假設 | 內容 | 比較 | 結果 |", "|---|---|---|---|"]
    for k, h in hyp.items():
        lines.append(f"| {k} | {h['claim']} | `{h['comparison']}` | {'成立' if h['holds'] else '不成立'} |")
    lines += ["", "## 配對比較（45 條串流合併）", "",
              "| 比較 | 串流 | Δaccuracy pp [CI] | accuracy | Δdrift 後 acc. pp [CI] | ΔFP [CI] | ΔX [CI] | 偵測 |",
              "|---|---|---|---|---|---|---|---|"]
    for name, c in comps.items():
        lines.append(f"| `{name}` | {c['streams']} | {_ci(c['acc'], 100)} | {c['accuracy']} | {_ci(c['post_acc'], 100)} | "
                     f"{_ci(c['fp'], 1, 1)} | {_ci(c['X'], 1, 2)} | {c['detection']} |")
    lines += ["", "e10bft lw0 的 learn_during_warning 與其他組不同，只作描述性參考。", "",
              "## 各組合併數值", "", "| 組別 | accuracy | drift 後 accuracy | 警報 | FP | X | 平均延遲 |", "|---|---|---|---|---|---|---|"]
    for a in arms:
        s = pooled[a]
        lines.append(f"| {ARM_LABEL[a]} | {_f(s['acc'])} | {_f(s['post_acc'])} | {s['alarms']} | {s['fp']} | {_f(s['X'], 2)} | {_f(s['mdt'], 1)} |")
    lines += ["", "## 11 個資料組（點估計）", ""]
    for metric, label, nd in (("acc", "accuracy", 4), ("X", "X", 2), ("fp", "FP", 0)):
        lines += [f"### {label}", "", "| 資料組 | " + " | ".join(ARM_LABEL[a] for a in arms) + " |",
                  "|---|" + "---|" * len(arms)]
        for g in groups:
            vals = [data["by_group"][g][a][metric] for a in arms]
            lines.append(f"| {g} | " + " | ".join(_f(v, nd) if isinstance(v, float) else _f(v) for v in vals) + " |")
        lines.append("")
    lines += ["## 分流診斷", ""]
    for arm, d in data["routing"].items():
        lines += [f"### {ARM_LABEL.get(arm, arm)}", "",
                  f"- warning 事件 {d['episodes']} 次；結束原因 {d['end_reasons']}",
                  f"- 先發 warning：{d['opener_share']}；確認者：{d['confirmed_by']}",
                  f"- 被分流忽略的 drift {d['ignored_drifts']} 次；冷卻期擋掉 {d['cooldown_blocked']} 次",
                  f"- 落在真實 drift 的事件 {d['episodes_at_gt_drift']} 次；先發者與類型相符 {_f(d['opener_matches_type'], 3)}",
                  f"- 分類器（是否 sudden）：{json.dumps(d['classifier_sudden_vs_not'], ensure_ascii=False)}", ""]
    (OUT / "routed_verdict.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["gate", "dev", "formal", "followup", "simpleclf", "oracle", "step01"])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--allow-smoke", action="store_true", help="formal: accept truncated runs (smoke check)")
    ap.add_argument("--datasets", nargs="+", default=None, help="gate: datasets to check (default: formal set)")
    ap.add_argument("--gate-name", default=None, help="gate: report file name under outputs/routed/")
    args = ap.parse_args()
    {"gate": run_gate, "dev": run_dev, "formal": run_formal, "followup": run_followup, "simpleclf": run_simpleclf, "oracle": run_oracle, "step01": run_step01}[args.mode](args)


if __name__ == "__main__":
    main()
