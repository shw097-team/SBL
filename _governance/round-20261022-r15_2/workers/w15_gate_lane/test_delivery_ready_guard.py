"""W15 gate: behavioural proof for the DELIVERY_READY pending-work guard.

Drives the real ProjectLifecycleController transition code from the isolated
copy (`isolated/src`, supplied via PYTHONPATH) against a temporary spine
database. Fixture style copied from HG-KSEOS/tests/test_cs_a_gate_repair.py
(tempfile.mkdtemp + SharedSpine(tmp/"spine.db").initialize()); no ORM invented.

Four cases:
  T1 open required work order + -> DELIVERY_READY  => ERR_PENDING_WORK_CANNOT_DELIVER
  T2 open required work order + -> DELIVERED       => ERR_PENDING_WORK_CANNOT_DELIVER
  T3 all required work orders VERIFIED + -> DELIVERY_READY => allowed, persisted
  T4 illegal transition still refused ERR_ILLEGAL_TRANSITION (transition set not widened)
"""
import shutil
import tempfile
from pathlib import Path

import pytest

from hg_kseos.lifecycle import (
    VALID_TRANSITIONS,
    LifecycleError,
    ProjectLifecycleController,
    ProjectRequest,
)
from hg_kseos.spine import SharedSpine

# A real git checkout is only read (git rev-parse HEAD) to satisfy
# create_workorder(base_head=...). Nothing is written to it.
TARGET_ROOT = r"C:\Projects\Agent_Workspace\HG-KSEOS"
GOAL = "Build a knowledge system with tests and acceptance"


@pytest.fixture()
def spine():
    tmp = tempfile.mkdtemp(prefix="hgk-w15gate-")
    s = SharedSpine(Path(tmp) / "spine.db")
    s.initialize()
    try:
        yield s
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def boot_to_release_reducing(spine: SharedSpine, project_id: str = "HGK-PRJ-W15"):
    """start -> intake -> ... -> admit_workorders -> EXECUTING -> ... -> RELEASE_REDUCING.

    Work orders stay open (CREATED) at the end, which is exactly the state the
    new guard must refuse at DELIVERY_READY.
    """
    lc = ProjectLifecycleController(spine)
    req = ProjectRequest(goal=GOAL, source_paths=[], constraints=["local-first"],
                         non_goals=["no cloud"], target_root=TARGET_ROOT)
    lc.start(req, project_id=project_id)
    lc.intake(project_id, req)
    lc.transition(project_id, "INTENT_BOUND", trigger="INTENT_ROUNDTRIP")
    lc.transition(project_id, "REQUIREMENTS_READY", trigger="REQUIREMENTS_DERIVED")
    lc.transition(project_id, "DESIGN_READY", trigger="DESIGN_COMPLETE")
    lc.plan(project_id)
    admitted = lc.admit_workorders(project_id)
    lc.transition(project_id, "EXECUTING", trigger="WO_EXECUTE")
    lc.transition(project_id, "VERIFYING", trigger="VERIFY")
    lc.transition(project_id, "EVOLUTION_REVIEW", trigger="EVO_REVIEW")
    lc.transition(project_id, "RELEASE_REDUCING", trigger="REDUCE")
    return lc, admitted


def set_all_workorders(spine: SharedSpine, state: str) -> None:
    with spine.transaction() as conn:
        conn.execute("UPDATE workorders SET state=?", (state,))


def open_workorder_ids(spine: SharedSpine, project_id: str) -> list[str]:
    with spine.connect() as conn:
        rows = conn.execute(
            "SELECT w.workorder_id FROM workorders w JOIN taskspecs t ON t.taskspec_id=w.taskspec_id "
            "JOIN requirements r ON r.requirement_id=t.requirement_id "
            "WHERE r.project_id=? AND w.state NOT IN ('VERIFIED','ROLLED_BACK','CANCELLED')",
            (project_id,),
        ).fetchall()
    return [r[0] for r in rows]


def test_t1_delivery_ready_refused_with_open_workorder(spine):
    """T1: open required work order + -> DELIVERY_READY must be refused."""
    lc, admitted = boot_to_release_reducing(spine)
    pid = "HGK-PRJ-W15"
    assert admitted["count"] >= 1
    assert open_workorder_ids(spine, pid), "precondition: work orders must be open"

    with pytest.raises(LifecycleError) as exc:
        lc.transition(pid, "DELIVERY_READY", trigger="READY")

    assert "ERR_PENDING_WORK_CANNOT_DELIVER" in str(exc.value)
    # refusal must not move the state machine
    assert lc.status(pid)["state"] == "RELEASE_REDUCING"


def test_t2_delivered_refused_with_open_workorder(spine):
    """T2: open required work order + -> DELIVERED must still be refused."""
    lc, _ = boot_to_release_reducing(spine)
    pid = "HGK-PRJ-W15"
    # reach DELIVERY_READY legally (all terminal), then re-open one work order
    set_all_workorders(spine, "VERIFIED")
    lc.transition(pid, "DELIVERY_READY", trigger="READY")
    assert lc.status(pid)["state"] == "DELIVERY_READY"
    set_all_workorders(spine, "CREATED")
    assert open_workorder_ids(spine, pid), "precondition: work order re-opened"

    with pytest.raises(LifecycleError) as exc:
        lc.transition(pid, "DELIVERED", trigger="DELIVER")

    assert "ERR_PENDING_WORK_CANNOT_DELIVER" in str(exc.value)
    assert lc.status(pid)["state"] == "DELIVERY_READY"


def test_t3_delivery_ready_allowed_when_all_terminal(spine):
    """T3: all required work orders VERIFIED + -> DELIVERY_READY is allowed and persisted."""
    lc, _ = boot_to_release_reducing(spine)
    pid = "HGK-PRJ-W15"
    set_all_workorders(spine, "VERIFIED")
    assert open_workorder_ids(spine, pid) == []

    out = lc.transition(pid, "DELIVERY_READY", trigger="READY")
    assert out["state"] == "DELIVERY_READY"

    # persisted, not merely returned
    with spine.connect() as conn:
        row = conn.execute("SELECT state FROM project_lifecycles WHERE project_id=?", (pid,)).fetchone()
        last = conn.execute(
            "SELECT to_state FROM project_transitions WHERE project_id=? ORDER BY rowid DESC LIMIT 1",
            (pid,),
        ).fetchone()
    assert row[0] == "DELIVERY_READY"
    assert last[0] == "DELIVERY_READY"


def test_t4_illegal_transition_still_refused(spine):
    """T4: the guard must not widen the transition set (PROJECT_CREATED -> DELIVERED illegal)."""
    lc = ProjectLifecycleController(spine)
    pid = "HGK-PRJ-W15T4"
    lc.start(ProjectRequest(goal=GOAL, target_root=TARGET_ROOT), project_id=pid)
    assert lc.status(pid)["state"] == "PROJECT_CREATED"
    assert "DELIVERED" not in VALID_TRANSITIONS["PROJECT_CREATED"]
    assert "DELIVERY_READY" not in VALID_TRANSITIONS["PROJECT_CREATED"]

    with pytest.raises(LifecycleError) as exc:
        lc.transition(pid, "DELIVERED", trigger="DELIVER")

    assert "ERR_ILLEGAL_TRANSITION" in str(exc.value)
    assert "ERR_PENDING_WORK_CANNOT_DELIVER" not in str(exc.value)
    assert lc.status(pid)["state"] == "PROJECT_CREATED"
    # the pair really is absent from the machine, so nothing was widened
    assert ("DELIVERY_READY" in VALID_TRANSITIONS["PROJECT_CREATED"]) is False
