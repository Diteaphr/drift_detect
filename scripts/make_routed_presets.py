"""Generate the routed-confirmation presets on the DET S1 framework.

Every preset copies ``det3_full_dual_adwin_lw1`` (frozen reference, one-sided
leader guard, 1000-step warning timeout, learn during warning) and only adds the
routing fields of ``src/config.py``:

* ``s1route_fixed_adwin`` / ``s1route_fixed_hddma``: one pair passed through,
  the reproducibility gate against ``det4_s1_wadwin_cadwin`` / ``det4_s1_whddma_chddma``;
* ``s1route_{fw,tr,union}_c{C}``: first warner, type classifier and union routing
  with a post-confirmation cooldown of C steps.

Run from the repo root; it overwrites only the files it generates.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PRESETS = REPO / "configs" / "presets"
TEMPLATE = "det3_full_dual_adwin_lw1"
POLICIES = {"fw": "first_warner", "tr": "type_classifier", "union": "union"}
COOLDOWNS = (0, 100, 300)
DESCRIPTIONS = {
    "first_warner": "the pair (ADWIN or HDDM-A) that warned first confirms",
    "type_classifier": "Type-LDD after 100 warning steps: sudden -> HDDM-A confirms, otherwise ADWIN",
    "union": "either pair's drift confirms",
    "hddma_gate": ("ADWIN's drift confirms at once; an HDDM-A drift runs Type-LDD on the spot and "
                   "confirms only if sudden, otherwise only ADWIN may confirm"),
    "fixed_adwin": "ADWIN pair only (reproduces det4_s1_wadwin_cadwin)",
    "fixed_hddma": "HDDM-A pair only (reproduces det4_s1_whddma_chddma)",
}


def write(name: str, policy: str, cooldown: int, base: dict, delay: int = 100, classifier: str = "") -> None:
    preset = json.loads(json.dumps(base))
    preset.update({
        "name": name,
        "role": "ablation",
        "description": (f"{TEMPLATE} with routed confirmation: "
                        f"{DESCRIPTIONS[policy].replace('after 100 warning steps', f'after {delay} warning steps')}"
                        f"{'' if not (cooldown and policy.startswith('fixed_')) else ' -- with the cooldown, not a DET4 replica'}"
                        f"; cooldown {cooldown}."),
        "source": "scripts/make_routed_presets.py",
    })
    preset["config"].update({
        "ecpf_route_policy": policy,
        "ecpf_route_decision_delay": delay,
        "ecpf_confirm_cooldown": cooldown,
    })
    if classifier:
        preset["description"] = preset["description"].replace("Type-LDD", "the simple baseline (cross-fitted)")
        preset["config"]["ecpf_route_classifier"] = classifier
    (PRESETS / f"{name}.json").write_text(json.dumps(preset, indent=2) + "\n")


def main() -> None:
    base = json.loads((PRESETS / f"{TEMPLATE}.json").read_text())
    names = []
    for policy in ("fixed_adwin", "fixed_hddma"):
        name = f"s1route_{policy}"
        write(name, policy, 0, base)
        names.append(name)
    for short, policy in POLICIES.items():
        for cooldown in COOLDOWNS:
            name = f"s1route_{short}_c{cooldown}"
            write(name, policy, cooldown, base)
            names.append(name)
    # Follow-up (preregistration amendment 2): type classifier decided 300 warning steps in,
    # about 400 steps after the drift starts, where the offline Type-LDD test peaked.
    write("s1route_tr_d300_c300", "type_classifier", 300, base, delay=300)
    names.append("s1route_tr_d300_c300")
    # Exploratory: the same, with the simple baseline of scripts/typeclf_retrain.py
    # (6 features + logistic regression, cross-fitted on split B) instead of Type-LDD.
    write("s1route_trsimple_d300_c300", "type_classifier", 300, base, delay=300,
          classifier="outputs/typeclf/simple_route_model.json")
    names.append("s1route_trsimple_d300_c300")
    # Step 0: the single-detector diagonals with the designs' cooldown, to separate
    # the cooldown's effect from the routing's.
    write("s1route_fixed_hddma_c300", "fixed_hddma", 300, base)
    names.append("s1route_fixed_hddma_c300")
    # Step 1: design 1 decided when HDDM-A's drift fires (simple baseline classifier).
    write("s1route_gate_simple_c300", "hddma_gate", 300, base,
          classifier="outputs/typeclf/simple_route_model.json")
    names.append("s1route_gate_simple_c300")
    print(f"{len(names)} presets: {', '.join(names)}")


if __name__ == "__main__":
    main()
