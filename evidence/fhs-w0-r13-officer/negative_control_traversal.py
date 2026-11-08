"""Traversal-failure classification controls, run read-only.

`classify_walk_errors` decides whether an unreadable subtree may be excluded from the copy census.
Three cases must hold, and all three are pure-function tests so no directory, no privilege and no write
is needed:

  A. a fixture-looking path with no declared member under it  -> excluded (denied)
  B. a fixture-looking path that IS an ancestor of a declared member -> covering (must refuse)
  C. a non-fixture failure, and a failure carrying no path at all    -> other (must refuse)

Case C is the one that matters most: a failure whose path could not be captured must never be quietly
treated as a fixture, because that is how an exclusion turns into a silent pass.
"""
import importlib.util, json, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("gate_r13", os.path.join(root, "tools", "gate_r13.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

declared = {g._plain_path(r"C:\Projects\Agent_Workspace\X\acl_probe2\protected_aa\doc.md")}
cases = [
    {"path": r"C:\Projects\Agent_Workspace\X\acl_probe2\protected_zz", "msg": "[WinError 5]"},
    {"path": r"C:\Projects\Agent_Workspace\X\acl_probe2\protected_aa", "msg": "[WinError 5]"},
    {"path": r"C:\Projects\Agent_Workspace\X\ordinary_dir", "msg": "[WinError 5]"},
    {"path": "", "msg": "[WinError 5] no filename attribute"},
]
denied, other, covering = g.classify_walk_errors(cases, declared)
result = {
    "excluded_fixtures": [e["path"] for e in denied],
    "refused_other": [e["path"] for e in other],
    "refused_over_declared": [[e["path"], len(c)] for e, c in covering],
    "A_excludes_fixture_without_member": len(denied) == 1,
    "B_refuses_fixture_covering_member": len(covering) == 1 and bool(covering[0][1]),
    "C_refuses_non_fixture_and_unlocated": len(other) == 2,
    "check_bites": len(denied) == 1 and len(covering) == 1 and len(other) == 2,
}
print(json.dumps(result, ensure_ascii=False, indent=1))
