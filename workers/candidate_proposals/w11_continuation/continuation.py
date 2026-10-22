"""HG-KSEOS continuation lease — PROPOSAL, not applied.

Deliberately dependency-free (sqlite3 + time only) so it can be imported and tested from the round tree without an
installed control plane. Applying it means copying this file to src/hg_kseos/continuation.py and calling
ensure_schema(conn) from the spine bootstrap.

Why it belongs in the control plane and not in the round tree: a lease held by the thing it governs is not a lease.
The round tree can be deleted or re-cloned; the control plane's record of "this round was in flight, with this
denominator, until this time, and here is why it claims to be finished" is what survives.
"""
from __future__ import annotations

import json
import sqlite3
import time

DDL = """
CREATE TABLE IF NOT EXISTS continuation_leases (
    round_id TEXT PRIMARY KEY,
    subject_sha TEXT NOT NULL,
    denominator_ref TEXT NOT NULL,
    driver_cmd TEXT NOT NULL,
    stop_conditions TEXT NOT NULL,
    ttl_minutes INTEGER NOT NULL DEFAULT 90,
    heartbeat_utc TEXT NOT NULL,
    terminal_proof TEXT,
    closed_by TEXT
);
CREATE TABLE IF NOT EXISTS continuation_heartbeats (
    round_id TEXT NOT NULL,
    at_utc TEXT NOT NULL,
    step TEXT,
    ready_count INTEGER NOT NULL DEFAULT 0
);
"""


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(DDL)
    conn.commit()


def stamp(conn: sqlite3.Connection, *, round_id: str, subject_sha: str, denominator_ref: str, driver_cmd: str,
          stop_conditions: list[str], ttl_minutes: int = 90, step: str | None = None,
          ready_count: int = 0) -> dict:
    now = utc_now()
    conn.execute(
        "INSERT INTO continuation_leases (round_id, subject_sha, denominator_ref, driver_cmd, stop_conditions, "
        "ttl_minutes, heartbeat_utc) VALUES (?,?,?,?,?,?,?) "
        "ON CONFLICT(round_id) DO UPDATE SET heartbeat_utc=excluded.heartbeat_utc, subject_sha=excluded.subject_sha",
        (round_id, subject_sha, denominator_ref, driver_cmd, json.dumps(stop_conditions), ttl_minutes, now))
    conn.execute("INSERT INTO continuation_heartbeats VALUES (?,?,?,?)", (round_id, now, step, ready_count))
    conn.commit()
    return lease(conn, round_id)


def lease(conn: sqlite3.Connection, round_id: str) -> dict | None:
    row = conn.execute("SELECT round_id, subject_sha, denominator_ref, driver_cmd, stop_conditions, ttl_minutes, "
                       "heartbeat_utc, terminal_proof, closed_by FROM continuation_leases WHERE round_id=?",
                       (round_id,)).fetchone()
    if not row:
        return None
    keys = ("round_id", "subject_sha", "denominator_ref", "driver_cmd", "stop_conditions", "ttl_minutes",
            "heartbeat_utc", "terminal_proof", "closed_by")
    out = dict(zip(keys, row))
    out["stop_conditions"] = json.loads(out["stop_conditions"])
    return out


def heartbeat_age_minutes(conn: sqlite3.Connection, round_id: str) -> float | None:
    row = conn.execute("SELECT heartbeat_utc FROM continuation_leases WHERE round_id=?", (round_id,)).fetchone()
    if not row:
        return None
    return (time.time() - time.mktime(time.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ")) + time.timezone) / 60


def close_blockers(conn: sqlite3.Connection, round_id: str, *, ready_count: int, parked_without_owner: list[str],
                   now: float | None = None) -> list[dict]:
    """A round may be declared finished only when this returns []."""
    out: list[dict] = []
    if ready_count > 0:
        out.append({"code": "READY_AGENT_ITEMS", "count": ready_count})
    if parked_without_owner:
        out.append({"code": "PARKED_WITHOUT_OWNER", "ids": list(parked_without_owner)})
    row = conn.execute("SELECT heartbeat_utc, ttl_minutes, terminal_proof FROM continuation_leases WHERE round_id=?",
                       (round_id,)).fetchone()
    if row is None:
        out.append({"code": "NO_LEASE", "round_id": round_id})
        return out
    hb, ttl, proof = row
    age = ((now or time.time()) - time.mktime(time.strptime(hb, "%Y-%m-%dT%H:%M:%SZ")) + time.timezone) / 60
    if age > ttl and not proof:
        out.append({"code": "STALE_LEASE", "age_minutes": round(age, 1), "ttl_minutes": ttl})
    if not proof:
        out.append({"code": "NO_TERMINAL_PROOF"})
    return out


def record_terminal(conn: sqlite3.Connection, round_id: str, proof: dict, closed_by: str) -> None:
    blockers = [(r[0],) for r in conn.execute("SELECT terminal_proof FROM continuation_leases WHERE round_id=?",
                                              (round_id,))]
    if not blockers:
        raise ValueError("NO_LEASE")
    conn.execute("UPDATE continuation_leases SET terminal_proof=?, closed_by=? WHERE round_id=?",
                 (json.dumps(proof, ensure_ascii=False), closed_by, round_id))
    conn.commit()
