"""Generate the memory-aware pool fade presets and the ``pool_fade`` suite.

Each fade mechanism of ``src/ecpf.py`` is its own method on two backbones:

* ``e10bft_<mechanism>``: main method E10bFT with only the pool fade rule changed;
* ``ecpf_<mechanism>``: ``ecpf_reuse_value`` (plain ECPF, dual ADWIN) with only
  the fade rule changed.

Run once from the repo root; it overwrites only the files it generates.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PRESETS = REPO / "configs" / "presets"

# name suffix -> (description, config overrides)
VARIANTS = {
    "reuse_value": ("reuse-value fading (reference for the e10bft backbone)",
                    {"ecpf_fade_policy": "reuse_value"}),
    **{f"density_b{b}": (f"value per KB eviction, pool <= {b} x leader KB",
                         {"ecpf_fade_policy": "density", "ecpf_memory_budget_factor": float(b)})
       for b in (2, 4, 8)},
    **{f"rent_l{l}": (f"memory rent: idle cost {l} x KB / mean KB per drift",
                      {"ecpf_fade_policy": "rent", "ecpf_fade_lambda": float(l)})
       for l in (1, 2, 5, 10)},
    **{f"entry_f{f}": (f"entry fee {f} x KB / mean KB once, then fixed idle cost",
                       {"ecpf_fade_policy": "entry", "ecpf_fade_lambda": float(f)})
       for f in (5, 15, 30)},
    **{f"freq_b{b}": (f"reuse frequency x value per KB eviction, pool <= {b} x leader KB",
                      {"ecpf_fade_policy": "freq", "ecpf_memory_budget_factor": float(b)})
       for b in (2, 4, 8)},
    **{f"decay_g{int(g * 100):03d}": (f"exponential decay of idle credit, gamma {g}",
                                      {"ecpf_fade_policy": "decay", "ecpf_decay_gamma": g})
       for g in (0.5, 0.8, 0.95)},
    "subst": ("reuse value against the second-best stored expert or a fresh learner",
              {"ecpf_fade_policy": "subst"}),
}

BACKBONES = {"e10bft": "e10bft", "ecpf": "ecpf_reuse_value"}
REFERENCES = ["e10bft", "ecpf_paper", "ecpf_reuse_value"]


def main() -> None:
    names = list(REFERENCES)
    for prefix, base_name in BACKBONES.items():
        base = json.loads((PRESETS / f"{base_name}.json").read_text())
        for suffix, (desc, overrides) in VARIANTS.items():
            name = f"{prefix}_{suffix}"
            if name in REFERENCES:
                continue
            preset = json.loads(json.dumps(base))
            preset.update({
                "name": name,
                "role": "ablation",
                "description": f"{base_name} with pool fade = {desc}.",
                "source": "scripts/make_pool_fade_presets.py",
            })
            preset["config"].update({"ecpf_fade_enabled": True, **overrides})
            (PRESETS / f"{name}.json").write_text(json.dumps(preset, indent=2) + "\n")
            names.append(name)

    defaults_path = REPO / "configs" / "benchmark_defaults.json"
    defaults = json.loads(defaults_path.read_text())
    defaults["suites"]["pool_fade"] = {
        "presets": names,
        "description": "Memory-aware model-pool fade mechanisms (density, rent, entry, freq, decay, subst) "
                       "on the e10bft and ecpf_reuse_value backbones, with e10bft, ecpf_paper and "
                       "ecpf_reuse_value as references. Run with --pool-trace.",
    }
    text = json.dumps(defaults, indent=2, ensure_ascii=False)
    # Keep the file's one-line preset lists.
    text = re.sub(r'\[\s+((?:"[^"]*",?\s*)+)\]',
                  lambda m: "[" + ", ".join(re.findall(r'"[^"]*"', m.group(1))) + "]", text)
    defaults_path.write_text(text + "\n")
    print(f"{len(names)} presets in suite pool_fade")


if __name__ == "__main__":
    main()
