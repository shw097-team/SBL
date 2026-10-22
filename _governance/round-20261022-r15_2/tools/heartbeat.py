"""Stamp the round lease. A lease is the only fact that distinguishes 'in flight' from 'abandoned'."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
LEASE = os.path.join(R, "ROUND_LEASE.json")
QUEUE = os.path.join(R, "QUEUE_R15_2.json")
TTL_MINUTES = 90


def queue_digest() -> str:
    raw = open(QUEUE, "rb").read()
    return hashlib.sha256(raw).hexdigest()


def stamp(step: str | None = None) -> dict:
    q = json.load(open(QUEUE, encoding="utf-8"))
    lease = json.load(open(LEASE, encoding="utf-8")) if os.path.exists(LEASE) else {
        "schema": "SBL_ROUND_LEASE/1",
        "round_id": "round-20261022-r15_2",
        "subject_sha": None,
        "denominator_ref": "DENOMINATOR_R15_2.json",
        "ready_set_ref": "QUEUE_R15_2.json",
        "driver_cmd": "python tools/advance_queue.py --max-steps 3",
        "stop_conditions": ["destructive action", "missing credential", "mandated lane unavailable",
                            "owner-only decision"],
        "ttl_minutes": TTL_MINUTES,
        "heartbeats": [],
        "terminal_proof": None,
    }
    lease["heartbeat_utc"] = time.strftime("%FT%TZ", time.gmtime())
    lease["queue_digest"] = queue_digest()
    lease["queue_counts"] = {s: sum(1 for i in q["items"] if i["status"] == s)
                             for s in ("READY", "DONE", "PARKED", "RUNNING")}
    lease["last_step"] = step or lease.get("last_step")
    lease.setdefault("heartbeats", []).append({"at": lease["heartbeat_utc"], "step": lease.get("last_step"),
                                               "ready": lease["queue_counts"]["READY"]})
    lease["heartbeats"] = lease["heartbeats"][-50:]
    json.dump(lease, open(LEASE, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    open(LEASE, "a", encoding="utf-8", newline="\n").write("\n")
    return lease


if __name__ == "__main__":
    lease = stamp(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps({"heartbeat": lease["heartbeat_utc"], "counts": lease["queue_counts"],
                      "digest": lease["queue_digest"][:12]}, ensure_ascii=False))
    print("LEASE_OK")
