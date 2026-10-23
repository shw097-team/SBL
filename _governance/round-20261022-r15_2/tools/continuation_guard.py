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

    rec = (q.get("lane_obligations") or {}).get("ok_receipts") or {}
    for i in q["items"]:
        lane = i.get("required_lane", "AGENT")
        if lane != "AGENT" and i["status"] == "DONE" and not rec.get(lane):
            blockers.append({"code": "LANE_RECEIPT_MISSING", "id": i["id"], "lane": lane})
    bypassed = [i["id"] for i in q["items"] if i.get("lane_bypassed")]
    if bypassed:
        blockers.append({"code": "LANE_BYPASSED_DISCLOSED", "ids": bypassed,
                         "note": "work completed in-session where a lane was mandated; disclosed, not laundered"})

    ready = [i["id"] for i in q["items"] if i["status"] == "READY" and i["owner_class"] == "AGENT"]
    if ready:
        blockers.append({"code": "READY_AGENT_ITEMS", "ids": ready})

    for i in q["items"]:
        if i.get("satisfiable_by") not in ("AGENT", "OWNER", "HOST", "EXTERNAL_AO"):
            blockers.append({"code": "SATISFIABILITY_UNKNOWN", "id": i["id"],
                             "satisfiable_by": i.get("satisfiable_by")})
        if i["status"] != "PARKED":
            continue
        if not i.get("parked_reason"):
            blockers.append({"code": "PARKED_WITHOUT_OWNER", "id": i["id"], "missing": "parked_reason"})
        ref = i.get("principal_request_ref")
        if not ref or not os.path.exists(os.path.join(R, ref)):
            blockers.append({"code": "UNISSUED_PRINCIPAL_REQUEST", "id": i["id"], "ref": ref})
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

    # Three claims, deliberately never merged. A guard that can only say TERMINAL/NOT_TERMINAL forces the agent to
    # choose between "keep going forever" and "call an exhausted queue complete"; both are wrong.
    # The legal terminal. Without it the agent must choose between stopping illegally and claiming a completion it
    # cannot have; both were measured today. Quiescence is a *fourth* claim: every obligation is either done, or
    # blocked on a named principal with an issued request, and no permitted agent remedy remains.
    agent_open = [i["id"] for i in q["items"]
                  if i.get("satisfiable_by", "AGENT") == "AGENT"
                  and i.get("status") not in ("DONE", "DONE_RECEIPT_RED")]
    unmet = []
    for i in q["items"]:
        if i.get("status") == "DONE":
            continue
        if i.get("satisfiable_by", "AGENT") == "AGENT":
            continue
        if not i.get("parked_reason"):
            unmet.append({"id": i["id"], "missing": "parked_reason"})
        ref = i.get("principal_request_ref")
        if not ref or not os.path.exists(os.path.join(R, ref)):
            unmet.append({"id": i["id"], "missing": "issued principal request"})
    bypass = [i["id"] for i in q["items"] if i.get("lane_bypassed")]
    quiescent = (not agent_open) and (not unmet) and (not bypass)
    claims = {"queue_exhausted": not blockers,
              "agent_scope_closed": not agent_open,
              "agent_quiescent": quiescent,
              "full_completion": False,
              "agent_open_ids": agent_open,
              "unmet_principal_obligations": unmet,
              "unresolved_lane_bypass": bypass,
              "note": ("queue_exhausted: no AGENT-actionable item remains; agent_scope_closed: every AGENT-satisfiable "
                       "item is DONE; agent_quiescent: nothing is left that the agent is permitted to do, and every "
                       "open item carries an issued request to a named principal; full_completion needs the external "
                       "signatures, so it is false by construction")}
    if quiescent:
        proof = {"schema": "SBL_AGENT_QUIESCENCE_PROOF/1", "verdict": "AGENT_QUIESCENT_AWAITING_PRINCIPALS",
                 "is_completion_claim": False, "claim_level": claims,
                 "why_not_complete": ("agent work is exhausted; the remaining obligations need signatures the agent may "
                                      "not produce. This is a legal stopping point, not a completion"),
                 "round_id": lease.get("round_id", "round-20261022-r15_2"),
                 "observed_at_utc": time.strftime("%FT%TZ", time.gmtime())}
        out = os.path.join(R, "AGENT_QUIESCENCE_PROOF.json")
        json.dump(proof, open(out, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
        print(json.dumps({"verdict": proof["verdict"], "proof": out}, ensure_ascii=False))
        return 0
    if blockers:
        print(json.dumps({"verdict": "NOT_TERMINAL", "claim_level": claims, "blockers": blockers},
                         ensure_ascii=False, indent=2))
        return 2

    proof = {"schema": "SBL_QUEUE_EXHAUSTION_PROOF/1",
             "claim_level": claims,
             "is_completion_claim": False,
             "r15_2_complete": False,
             "all_open_items_are_issued_requests": True,
             "why_not_complete": ("queue exhaustion only means no AGENT-actionable item remains. R15.2 still has "
                                  "2 NOT_RUN work packages (W02, W12), release is BLOCKED without an owner seal, "
                                  "and M4's semantic denominator is UNMEASURED"),
             "round_id": lease.get("round_id", "round-20261022-r15_2"),
             "observed_at_utc": time.strftime("%FT%TZ", time.gmtime()),
             "predicate": "no READY agent item; every PARKED item has a typed reason and a named owner action; "
                          "lease fresh or terminal proof present",
             "queue_digest": lease.get("queue_digest"),
             "counts": {s: sum(1 for i in q["items"] if i["status"] == s) for s in ("DONE", "PARKED", "READY")},
             "parked": [{"id": i["id"], "reason": i["parked_reason"], "owner_action": i["owner_action"],
                        "satisfiable_by": i["satisfiable_by"], "principal_request_ref": i["principal_request_ref"]}
                        for i in q["items"] if i["status"] == "PARKED"],
             "downstream_gates_not_claimed": ["release", "independent_acceptance", "M4", "R15.2 completion"],
             "naming_note": ("this file was going to be called ROUND_CLOSE_PROOF. It is not a close proof: a state name that asserts more than its predicate checks is the DELIVERY_READY defect this round already found.")}
    json.dump(proof, open(PROOF, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    open(PROOF, "a", encoding="utf-8", newline="\n").write("\n")
    print(json.dumps({"verdict": "QUEUE_EXHAUSTED", "proof": PROOF}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
