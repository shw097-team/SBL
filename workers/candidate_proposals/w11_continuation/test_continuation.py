"""Tests for the continuation-lease proposal. Run against the candidate module directly; nothing is installed."""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import continuation as C  # noqa: E402


def fresh():
    conn = sqlite3.connect(":memory:")
    C.ensure_schema(conn)
    C.stamp(conn, round_id="r1", subject_sha="deadbeef", denominator_ref="DENOM.json",
            driver_cmd="advance", stop_conditions=["destructive", "credential", "lane", "owner"], step="t0")
    return conn


def test_stamp_then_lease_roundtrip():
    conn = fresh()
    lease = C.lease(conn, "r1")
    assert lease["subject_sha"] == "deadbeef"
    assert lease["stop_conditions"] == ["destructive", "credential", "lane", "owner"]


def test_ready_work_blocks_closure():
    conn = fresh()
    C.record_terminal(conn, "r1", {"is_completion_claim": False}, "guard")
    codes = [b["code"] for b in C.close_blockers(conn, "r1", ready_count=2, parked_without_owner=[])]
    assert "READY_AGENT_ITEMS" in codes


def test_parked_without_owner_blocks_closure():
    conn = fresh()
    C.record_terminal(conn, "r1", {"is_completion_claim": False}, "guard")
    codes = [b["code"] for b in C.close_blockers(conn, "r1", ready_count=0, parked_without_owner=["W02"])]
    assert "PARKED_WITHOUT_OWNER" in codes


def test_missing_proof_blocks_closure():
    conn = fresh()
    codes = [b["code"] for b in C.close_blockers(conn, "r1", ready_count=0, parked_without_owner=[])]
    assert "NO_TERMINAL_PROOF" in codes


def test_stale_lease_is_detected():
    conn = fresh()
    import time as _t
    future = _t.time() + 91 * 60
    codes = [b["code"] for b in C.close_blockers(conn, "r1", ready_count=0, parked_without_owner=[], now=future)]
    assert "STALE_LEASE" in codes


def test_clean_round_closes():
    conn = fresh()
    C.record_terminal(conn, "r1", {"is_completion_claim": False}, "guard")
    assert C.close_blockers(conn, "r1", ready_count=0, parked_without_owner=[]) == []
