"""Mandate gate: refuse work that bypassed its mandated lane.

Two modes:
  check --role PLAN|EXECUTE|VERIFY   pre-flight. Exit 0 only if that lane has a receipt (ok + nonce). Run this BEFORE
                                     doing research/writing/verifying, so the cheapest path is also the compliant one.
  audit                              post-flight. Exit 0 only if every DONE queue row whose required_lane is not AGENT
                                     has a matching lane receipt.

The point is not to trust the model. The point is that a violation has to fail something.
"""
from __future__ import annotations

import glob
import json
import os
import sys

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
MANDATE = os.path.join(R, "MANDATE_R15_2.json")
QUEUE = os.path.join(R, "QUEUE_R15_2.json")
DISPATCH = os.path.join(R, "receipts", "dispatch")


def receipts() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for f in glob.glob(os.path.join(DISPATCH, "*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        lane = d.get("lane")
        if not lane:
            continue
        a = (d.get("attempts") or [{}])[0]
        out.setdefault(lane, []).append({"file": os.path.basename(f), "ok": bool(d.get("ok")),
                                         "nonce": bool(a.get("nonce_present")),
                                         "model": d.get("used_transport_model"),
                                         "secs": a.get("seconds")})
    return out


def check(role: str) -> int:
    m = json.load(open(MANDATE, encoding="utf-8"))
    spec = m["roles"].get(role)
    if not spec:
        print(f"UNKNOWN_ROLE {role}; known: {list(m['roles'])}")
        return 2
    good = [r for r in receipts().get(spec["lane"], []) if r["ok"] and r["nonce"]]
    if not good:
        print(json.dumps({"verdict": "REFUSED", "role": role, "lane": spec["lane"],
                          "required_model": spec["provider_model"],
                          "action": ("dispatch through the lane first: python tools/run_lane.py "
                                     f"--role {role} --brief <file>")}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"verdict": "ALLOWED", "role": role, "lane": spec["lane"],
                      "latest_receipt": good[-1]}, ensure_ascii=False, indent=2))
    return 0


def audit() -> int:
    q = json.load(open(QUEUE, encoding="utf-8"))
    rec = receipts()
    missing = []
    for i in q["items"]:
        lane = i.get("required_lane", "AGENT")
        if lane == "AGENT" or i["status"] != "DONE":
            continue
        if not [r for r in rec.get(lane, []) if r["ok"] and r["nonce"]]:
            missing.append({"id": i["id"], "lane": lane})
        elif not i.get("lane_receipt_file"):
            missing.append({"id": i["id"], "lane": lane, "reason": "receipt exists for the lane but none is bound to this item"})
    if missing:
        print(json.dumps({"verdict": "AUDIT_FAILED", "unbound_or_missing": missing}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"verdict": "AUDIT_CLEAN", "checked": len(q["items"])}, ensure_ascii=False))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: mandate_gate.py check --role PLAN | audit")
        return 2
    if sys.argv[1] == "audit":
        return audit()
    if sys.argv[1] == "check":
        role = sys.argv[sys.argv.index("--role") + 1] if "--role" in sys.argv else ""
        return check(role)
    print("unknown mode")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
