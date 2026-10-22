import ast
import difflib
import json
import os

HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
SRC = os.path.join(HGK, "src", "hg_kseos", "lifecycle.py")
OUT = r"C:/Projects/Agent_Workspace/_r152_ev/workers/candidate_proposals/w15_gate"

OLD = '''        # CS-A D4: project-level DELIVERED must fail while required workorders
        # are still open (created/admitted/executing). Wave/subset closure is
        # recorded via checkpoints, not by claiming project delivery.
        if to_state == "DELIVERED":'''
NEW = '''        # CS-A D4: project-level DELIVERY_READY *and* DELIVERED must fail while
        # required workorders are still open or FAILED. Reaching DELIVERY_READY with
        # a FAILED order is what made a failed round read as almost-delivered.
        if to_state in ("DELIVERY_READY", "DELIVERED"):'''
OLD_ERR = '''                    f"ERR_PENDING_WORK_CANNOT_DELIVER {project_id}: {open_rows} required workorders open")'''
NEW_ERR = '''                    f"ERR_PENDING_WORK_CANNOT_DELIVER {project_id}: {open_rows} required workorders open "
                    f"(refused at {to_state})")'''


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    src = open(SRC, encoding="utf-8").read()
    if OLD not in src:
        raise SystemExit("anchor 1 not found — the guard moved; re-read before proposing")
    cand = src.replace(OLD, NEW).replace(OLD_ERR, NEW_ERR)
    open(os.path.join(OUT, "lifecycle.candidate.py"), "w", encoding="utf-8", newline="\n").write(cand)
    diff = "".join(difflib.unified_diff(src.splitlines(True), cand.splitlines(True),
                                        fromfile="a/src/hg_kseos/lifecycle.py",
                                        tofile="b/src/hg_kseos/lifecycle.py"))
    open(os.path.join(OUT, "proposal.diff"), "w", encoding="utf-8", newline="\n").write(diff)

    test = '''"""Behavioural test for the W15 gate proposal, run against an isolated sqlite mirror.

The proposal's whole claim is a COUNT: a project with a FAILED required workorder has non-zero blockers. That is
testable without importing HG-KSEOS, by running the same SQL against the same schema in a scratch database.
"""
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
SQL = ("SELECT COUNT(*) FROM workorders w JOIN taskspecs t ON t.taskspec_id=w.taskspec_id "
       "JOIN requirements r ON r.requirement_id=t.requirement_id "
       "WHERE r.project_id=? AND w.state NOT IN ('VERIFIED','ROLLED_BACK','CANCELLED')")


def make_db(rows):
    db = os.path.join(HERE, "_scratch.db")
    if os.path.exists(db):
        os.remove(db)
    c = sqlite3.connect(db)
    c.executescript("""
        CREATE TABLE requirements(requirement_id TEXT, project_id TEXT);
        CREATE TABLE taskspecs(taskspec_id TEXT, requirement_id TEXT);
        CREATE TABLE workorders(workorder_id TEXT, taskspec_id TEXT, state TEXT);
        INSERT INTO requirements VALUES ('r1','p1');
        INSERT INTO taskspecs VALUES ('t1','r1');
    """)
    for i, state in enumerate(rows):
        c.execute("INSERT INTO workorders VALUES (?,?,?)", (f"w{i}", "t1", state))
    c.commit()
    n = c.execute(SQL, ("p1",)).fetchone()[0]
    c.close()
    os.remove(db)
    return n


def test_failed_order_blocks_delivery():
    assert make_db(["VERIFIED", "FAILED"]) == 1


def test_created_order_blocks_delivery():
    assert make_db(["CREATED"]) == 1


def test_clean_project_does_not_block():
    assert make_db(["VERIFIED", "VERIFIED"]) == 0


def test_proposal_guards_both_states():
    text = open(os.path.join(HERE, "lifecycle.candidate.py"), encoding="utf-8").read()
    assert 'to_state in ("DELIVERY_READY", "DELIVERED")' in text
    assert "refused at {to_state}" in text
'''
    open(os.path.join(OUT, "test_gate_candidate.py"), "w", encoding="utf-8", newline="\n").write(test)

    meta = {
        "proposal": "W15 delivery gate must also refuse at DELIVERY_READY",
        "measured_correction": (
            "The earlier TT said the delivery gate ignores FAILED orders. Re-reading lifecycle.py 169-182 shows the "
            "DELIVERED transition DOES count FAILED as open; the actual defect is that DELIVERY_READY carries no such "
            "guard, so the state reads as 'almost delivered' with two FAILED orders present."),
        "applies_to": "src/hg_kseos/lifecycle.py",
        "apply": "git -C C:/Projects/Agent_Workspace/HG-KSEOS apply "
                 "workers/candidate_proposals/w15_gate/proposal.diff",
        "permit": "NOT_APPLIED — control-plane change; a HGK owner applies it",
        "claim_ceiling": "a 2-line guard plus four tests; no control-plane behaviour has changed here",
    }
    open(os.path.join(OUT, "META.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"diff_lines": len(diff.splitlines()), "dir": OUT}, ensure_ascii=False))
    print("GATE_PROPOSAL_OK")


if __name__ == "__main__":
    main()
