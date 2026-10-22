"""Behavioural test for the W15 gate proposal, run against an isolated sqlite mirror.

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
