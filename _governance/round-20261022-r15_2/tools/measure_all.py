"""One measurement pass over the R15.2 denominators, printed for the queue driver to check."""
from __future__ import annotations

import json
import os
import re
import sys

SBL = r"C:/Projects/Agent_Workspace/SBL"
WT = r"C:/Projects/Agent_Workspace/_r152_ev"


def ledger_counts() -> dict:
    out = {}
    for name, key in (("child_outcome_ledger.json", "parents"), ("child_outcome_ledger.json", "children"),
                      ("source_identity_441_ledger.json", None), ("surface_c001_c038_ledger.json", "surfaces")):
        p = os.path.join(SBL, "evidence_ledger", name)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if key:
            out[key] = len(d.get(key) or [])
        else:
            parts = {k: len(v) for k, v in d.items() if isinstance(v, list)}
            out["identity_parts"] = parts
            out["identity_total"] = sum(parts.values())
    return out


def kinds() -> list[str]:
    s = open(os.path.join(WT, "sbl_core", "m03_routing.py"), encoding="utf-8").read()
    m = re.search(r"DEFAULT_POLICY[^=]*=\s*\{(.+?)\n\}", s, re.S)
    return re.findall(r'"([A-Z_]+)"\s*:', m.group(1)) if m else []


def modes_gates() -> dict:
    s = open(os.path.join(WT, "sbl_core", "modes.py"), encoding="utf-8").read()
    modes = re.search(r"^MODES[^=]*=\s*\((.+?)\)", s, re.M)
    gates = re.search(r"^GATE_IDS[^=]*=\s*tuple\(f\"G\{i:02d\}\" for i in range\((\d+)\)\)", s, re.M)
    nm = len(re.findall(r'"[A-Z_]+"', modes.group(1))) if modes else 0
    ng = int(gates.group(1)) if gates else 0
    return {"modes": nm, "gates": ng, "mode_gates": nm * ng}


def product_surface() -> dict:
    skills = [d for d in os.listdir(os.path.join(WT, "skills"))] if os.path.isdir(os.path.join(WT, "skills")) else []
    skill_md = sum(len([f for f in fs if f.endswith(".md")]) for _, _, fs in os.walk(os.path.join(WT, "skills")))
    contracts = len([f for f in os.listdir(os.path.join(WT, "contracts")) if f.endswith(".json")]) \
        if os.path.isdir(os.path.join(WT, "contracts")) else 0
    cli = re.findall(r'"([a-z][a-z\-]*)"\s*:', open(os.path.join(WT, "sbl_cli", "sbl_todo.py"),
                                                  encoding="utf-8").read())
    return {"skill_dirs": len(skills), "skill_md": skill_md, "contract_json": contracts, "cli_verbs": len(set(cli))}


def r14() -> dict:
    p = os.path.join(WT, "_governance", "round-20261022-r15_2", "workers", "r14ledger", "SUMMARY.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    return d.get("counts") or d


if __name__ == "__main__":
    res = {"ledgers": ledger_counts(), "kinds": {"list": kinds(), "count": len(kinds())},
           "mode_gates": modes_gates(), "product_surface": product_surface(), "r14": r14()}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("MEASURED_OK")
