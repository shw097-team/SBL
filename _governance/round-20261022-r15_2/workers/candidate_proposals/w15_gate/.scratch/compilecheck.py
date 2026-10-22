"""Syntax + AST check on the after-image, plus a behavioural mirror of the guarded COUNT."""
from __future__ import annotations

import ast
import json
import os
import py_compile
import sqlite3

SRC = r"C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lifecycle.py"
SCR = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/candidate_proposals/w15_gate/.scratch"

COND_OLD = '        if to_state == "DELIVERED":'
COND_NEW = '        if to_state in ("DELIVERY_READY", "DELIVERED"):'
ERR_OLD = '{open_rows} required workorders open")'
ERR_NEW = '{open_rows} required workorders open (refused at {to_state})")'

SQL = ("SELECT COUNT(*) FROM workorders w JOIN taskspecs t ON t.taskspec_id=w.taskspec_id "
       "JOIN requirements r ON r.requirement_id=t.requirement_id "
       "WHERE r.project_id=? AND w.state NOT IN ('VERIFIED','ROLLED_BACK','CANCELLED')")


def build_after() -> str:
    before = open(SRC, "rb").read().decode("utf-8").replace("\r\n", "\n")
    return before.replace(COND_OLD, COND_NEW).replace(ERR_OLD, ERR_NEW)


def count(rows) -> int:
    c = sqlite3.connect(":memory:")
    c.executescript("""
        CREATE TABLE requirements(requirement_id TEXT, project_id TEXT);
        CREATE TABLE taskspecs(taskspec_id TEXT, requirement_id TEXT);
        CREATE TABLE workorders(workorder_id TEXT, taskspec_id TEXT, state TEXT);
        INSERT INTO requirements VALUES ('r1','p1');
        INSERT INTO taskspecs VALUES ('t1','r1');
    """)
    for i, s in enumerate(rows):
        c.execute("INSERT INTO workorders VALUES (?,?,?)", (f"w{i}", "t1", s))
    c.commit()
    n = c.execute(SQL, ("p1",)).fetchone()[0]
    c.close()
    return n


def main() -> int:
    after = build_after()
    path = os.path.join(SCR, "lifecycle_after_check.py")
    open(path, "w", encoding="utf-8", newline="\n").write(after)
    py_compile.compile(path, cfile=os.path.join(SCR, "lifecycle_after_check.pyc"), doraise=True)
    tree = ast.parse(after)

    # Find the guard `if` and confirm its test is the two-state membership test.
    guard_ok = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            if (isinstance(node.test.left, ast.Name) and node.test.left.id == "to_state"
                    and isinstance(node.test.ops[0], ast.In)):
                vals = [e.value for e in node.test.comparators[0].elts]
                guard_ok = vals == ["DELIVERY_READY", "DELIVERED"]
                break
    # The error string must interpolate to_state.
    msg_ok = "(refused at {to_state})" in after
    fstring_ok = any(
        isinstance(n, ast.JoinedStr) and "(refused at " in "".join(
            p.value if isinstance(p, ast.Constant) else "{x}" for p in n.values)
        for n in ast.walk(tree))

    ev = {
        "after_image_compiles": True,
        "guard_ast_is_two_state_membership": guard_ok,
        "error_string_has_refused_at": msg_ok,
        "error_string_is_fstring_with_interpolation": fstring_ok,
        "counts": {
            "verified_plus_failed": count(["VERIFIED", "FAILED"]),
            "created_only": count(["CREATED"]),
            "all_verified": count(["VERIFIED", "VERIFIED"]),
            "cancelled_and_rolled_back": count(["CANCELLED", "ROLLED_BACK"]),
        },
    }
    os.remove(path)
    print(json.dumps(ev, ensure_ascii=False, indent=2))
    ok = (guard_ok and msg_ok and fstring_ok
          and ev["counts"]["verified_plus_failed"] == 1
          and ev["counts"]["created_only"] == 1
          and ev["counts"]["all_verified"] == 0
          and ev["counts"]["cancelled_and_rolled_back"] == 0)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
