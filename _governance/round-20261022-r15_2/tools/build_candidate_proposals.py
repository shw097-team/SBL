"""Emit candidate proposals for gaps that cannot be written without a product permit.

Nothing here touches sbl_core. Each proposal is a unified diff an owner can apply with one command, plus a test that
runs against the candidate text so the proposal is coherent before anyone applies it.
"""
from __future__ import annotations

import ast
import difflib
import json
import os

WT = r"C:/Projects/Agent_Workspace/_r152_ev"
OUT = os.path.join(WT, "workers", "candidate_proposals")
SRC = os.path.join(WT, "sbl_core", "m03_routing.py")

# The declared denominator is 8 kinds; DEFAULT_POLICY implements 5. These three are the inference targets the product
# routes to today by fallback, so naming them changes routing from implicit to explicit.
ADDITIONS = {
    "DOC_SET": "SBLM02_SPEC_COMPILER",
    "REPAIR_TASK": "SBLM06_BOUNDED_REPAIR",
    "EVAL_HARNESS": "SBLM05_ACCEPTANCE_HARNESS",
}


def candidate_text(src: str) -> str:
    old = '    "AI_SYSTEM": None,\n}'
    new_rows = "".join(f'    "{k}": "{v}",\n' for k, v in ADDITIONS.items())
    if old not in src:
        raise SystemExit("anchor not found — the source moved, re-read it before proposing")
    return src.replace(old, '    "AI_SYSTEM": None,\n' + new_rows + "}")


def policy_keys(text: str) -> list[str]:
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "DEFAULT_POLICY":
            return [k.value for k in node.value.keys]
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "DEFAULT_POLICY" for t in node.targets):
            return [k.value for k in node.value.keys]
    return []


def main() -> None:
    d = os.path.join(OUT, "w06_kinds")
    os.makedirs(d, exist_ok=True)
    src = open(SRC, encoding="utf-8").read()
    cand = candidate_text(src)

    open(os.path.join(d, "m03_routing.candidate.py"), "w", encoding="utf-8", newline="\n").write(cand)
    diff = "".join(difflib.unified_diff(src.splitlines(True), cand.splitlines(True),
                                        fromfile="a/sbl_core/m03_routing.py",
                                        tofile="b/sbl_core/m03_routing.py"))
    open(os.path.join(d, "proposal.diff"), "w", encoding="utf-8", newline="\n").write(diff)

    current, proposed = policy_keys(src), policy_keys(cand)
    test = f'''"""Coherence test for the W06 kinds proposal. Runs against the candidate text; nothing is applied."""
import ast, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def keys(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "DEFAULT_POLICY":
            return {{k.value: (v.value if isinstance(v, ast.Constant) else None) for k, v in zip(node.value.keys, node.value.values)}}
    return {{}}

def test_declared_denominator_is_eight():
    got = keys(os.path.join(HERE, "m03_routing.candidate.py"))
    assert len(got) == 8, sorted(got)

def test_every_router_target_exists():
    targets = set(keys(os.path.join(HERE, "m03_routing.candidate.py")).values()) - {{None}}
    src = open(os.path.join(HERE, "m03_routing.candidate.py"), encoding="utf-8").read()
    for t in targets:
        assert t in src, t

def test_source_still_has_five():
    got = keys(os.path.join(HERE, "..", "..", "..", "sbl_core", "m03_routing.py"))
    assert len(got) == 5, sorted(got)
'''
    open(os.path.join(d, "test_kinds_candidate.py"), "w", encoding="utf-8", newline="\n").write(test)

    meta = {"proposal": "W06 kinds 5 -> 8", "applies_to": "sbl_core/m03_routing.py",
            "apply": "git apply workers/candidate_proposals/w06_kinds/proposal.diff",
            "current": current, "proposed": proposed, "added": ADDITIONS,
            "permit": "NOT_APPLIED — product writes need a permit; this is a candidate diff only",
            "claim_ceiling": "coherent diff plus tests; no product behaviour has changed"}
    open(os.path.join(d, "META.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"current": len(current), "proposed": len(proposed), "diff_lines": len(diff.splitlines()),
                      "dir": d}, ensure_ascii=False))
    print("PROPOSALS_OK")


if __name__ == "__main__":
    main()
