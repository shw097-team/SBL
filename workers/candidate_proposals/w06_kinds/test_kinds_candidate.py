"""Coherence test for the W06 kinds proposal. Runs against the candidate text; nothing is applied."""
import ast, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def keys(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "DEFAULT_POLICY":
            return {k.value: (v.value if isinstance(v, ast.Constant) else None) for k, v in zip(node.value.keys, node.value.values)}
    return {}

def test_declared_denominator_is_eight():
    got = keys(os.path.join(HERE, "m03_routing.candidate.py"))
    assert len(got) == 8, sorted(got)

def test_every_router_target_exists():
    targets = set(keys(os.path.join(HERE, "m03_routing.candidate.py")).values()) - {None}
    src = open(os.path.join(HERE, "m03_routing.candidate.py"), encoding="utf-8").read()
    for t in targets:
        assert t in src, t

def test_source_still_has_five():
    got = keys(os.path.join(HERE, "..", "..", "..", "sbl_core", "m03_routing.py"))
    assert len(got) == 5, sorted(got)
