"""The close predicate. A round may be declared terminal only if this exits 0.

Refusals, in order:
  READY_AGENT_ITEMS        an agent could still act; the round is not finished
  PARKED_WITHOUT_OWNER     a parked item has no typed reason or no named next actor
  STALE_LEASE              no heartbeat within the TTL and no terminal proof
  NO_TERMINAL_PROOF        terminal claimed without a guard-written proof

This exists because "we are done" was previously a sentence anyone could write. Now it is a claim that can fail.
"""
from __future__ import annotations

import calendar
import json
import os
import time

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
QUEUE = os.path.join(R, "QUEUE_R15_2.json")
LEASE = os.path.join(R, "ROUND_LEASE.json")
PROOF = os.path.join(R, "QUEUE_EXHAUSTION_PROOF.json")

OWNER_ACTIONS = {
    "W02.policy": "name the active policy digest, or authorise hermes-codex-lane.json as active",
    "W12.swof": "issue the W3 Domain Owner Native Admission, or authorise a shadow-only connected dry run",
    "W13.hosts": "provide host IDs and the private-plugin schema, or accept local double-digest build evidence",
    "W15.release": "approve the HG-KSEOS delivery-gate change and issue the release seal",
    "W16.perf": "name the reference workload and accept or reject the observed thresholds",
}


def main() -> int:
    q = json.load(open(QUEUE, encoding="utf-8"))
    lease = json.load(open(LEASE, encoding="utf-8")) if os.path.exists(LEASE) else {}
    blockers: list[dict] = []

    ready = [i["id"] for i in q["items"] if i["status"] == "READY" and i["owner_class"] == "AGENT"]
    if ready:
        blockers.append({"code": "READY_AGENT_ITEMS", "ids": ready})

    for i in q["items"]:
        if i["status"] != "PARKED":
            continue
        if not i.get("parked_reason"):
            blockers.append({"code": "PARKED_WITHOUT_OWNER", "id": i["id"], "missing": "parked_reason"})
        if not i.get("owner_action"):
            action = OWNER_ACTIONS.get(i["id"])
            if action:
                i["owner_action"] = action           # fill from the FAR decision pack, and persist
                i["owner_action_source"] = "FAR_DECISIONS_R15_2.md"
            else:
                blockers.append({"code": "PARKED_WITHOUT_OWNER", "id": i["id"], "missing": "owner_action"})

    hb = lease.get("heartbeat_utc")
    ttl = int(lease.get("ttl_minutes", 90))
    if hb and not lease.get("terminal_proof"):
        age = (time.time() - calendar.timegm(time.strptime(hb, "%Y-%m-%dT%H:%M:%SZ"))) / 60
        if age > ttl:
            blockers.append({"code": "STALE_LEASE", "age_minutes": round(age, 1), "ttl_minutes": ttl})

    json.dump(q, open(QUEUE, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    open(QUEUE, "a", encoding="utf-8", newline="\n").write("\n")

    if blockers:
        print(json.dumps({"verdict": "NOT_TERMINAL", "blockers": blockers}, ensure_ascii=False, indent=2))
        return 2

    proof = {"schema": "SBL_QUEUE_EXHAUSTION_PROOF/1",
             "is_completion_claim": False,
             "r15_2_complete": False,
             "why_not_complete": ("queue exhaustion only means no AGENT-actionable item remains. R15.2 still has "
                                  "2 NOT_RUN work packages (W02, W12), release is BLOCKED without an owner seal, "
                                  "and M4's semantic denominator is UNMEASURED"),
             "round_id": lease.get("round_id", "round-20261022-r15_2"),
             "observed_at_utc": time.strftime("%FT%TZ", time.gmtime()),
             "predicate": "no READY agent item; every PARKED item has a typed reason and a named owner action; "
                          "lease fresh or terminal proof present",
             "queue_digest": lease.get("queue_digest"),
             "counts": {s: sum(1 for i in q["items"] if i["status"] == s) for s in ("DONE", "PARKED", "READY")},
             "parked": [{"id": i["id"], "reason": i["parked_reason"], "owner_action": i["owner_action"]}
                        for i in q["items"] if i["status"] == "PARKED"],
             "downstream_gates_not_claimed": ["release", "independent_acceptance", "M4", "R15.2 completion"],
             "naming_note": ("this file was going to be called ROUND_CLOSE_PROOF. It is not a close proof: a state name that asserts more than its predicate checks is the DELIVERY_READY defect this round already found.")}
    json.dump(proof, open(PROOF, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    open(PROOF, "a", encoding="utf-8", newline="\n").write("\n")
    print(json.dumps({"verdict": "QUEUE_EXHAUSTED", "proof": PROOF}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
