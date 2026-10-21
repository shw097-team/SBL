#!/usr/bin/env python
"""Repair the registry routes' `fallbacks` lists after the GPT-6.1-SOL promotion.

DEFECT FOUND BY READ-BACK (not by the apply script's own report):
  The apply script derived `fallbacks` from the OLD `fallbacks` list, matched by
  (provider, model). But in the pre-image, the arm that was rank-1 -- the
  minimax arm -- lived in `arms` and NOT in `fallbacks`. So the demoted primary
  was DROPPED from `fallbacks` entirely, and the route ended up declaring:
      arms      = [gpt-6.1-sol, minimax, glm, deepseek, ...]
      fallbacks = [            glm, deepseek, ...]
  The route's own fallback list contradicted its own arm list, and the owner
  order's "the minimax arm is retained as a reachable fallback, not removed"
  was false in the artifact.

FIX: `fallbacks` == `arms[1:]` in provider/model order, always. The demoted
  primary is re-inserted at the front, and the fallback entry's fields
  (auth / canonical_identity / oauth) are taken from the matching `arms` entry
  so the two lists cannot disagree about an arm's identity.

This is a REPAIR, not a re-order: it touches only the `fallbacks` list of the
three routes, and every change is recorded.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
REG = HGK / "config" / "lane-routing-registry.yaml"
POOL = HGK / "config" / "lane-route-slots.candidate.json"
RECEIPT = HGK / "var" / "R7-LANES" / "gpt61_fallbacks_repair_receipt.json"

LANES = ("PLAN", "EXECUTE", "VERIFY_SECURITY")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    raw = REG.read_bytes()
    pre = sha256_bytes(raw)
    print("registry pre-image sha256:", pre)

    reg = yaml.safe_load(raw.decode("utf-8"))
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    pool_order = {}
    for lane in pool["lanes"]:
        pool_order[lane["lane"]] = [
            (e.get("provider"), e.get("model")) for e in lane["ordered_pool"]
        ]

    changes = []
    for route in reg.get("routes", []):
        lane = route.get("lane")
        if lane not in LANES:
            continue
        arms = route.get("arms", [])
        arm_by_key = {}
        for a in arms:
            arm_by_key.setdefault((a.get("provider"), a.get("model")), a)
        fbs = route.get("fallbacks", [])

        before = [(a.get("provider"), a.get("model")) for a in fbs]
        # the fallback list must mirror arms[1:] exactly
        new_fbs = []
        for a in arms[1:]:
            key = (a.get("provider"), a.get("model"))
            src = arm_by_key[key]
            # take the identity fields from the ARMS entry (one source of truth)
            new_fbs.append({
                "provider": src.get("provider"),
                "model": src.get("model"),
                "canonical_identity": src.get("canonical_identity", src.get("model")),
                "auth": src.get("auth"),
                "oauth": src.get("oauth"),
            })
        after = [(a.get("provider"), a.get("model")) for a in new_fbs]
        route["fallbacks"] = new_fbs
        if before != after:
            changes.append({"lane": lane, "before": before, "after": after})
            print(f"\n{lane}:")
            print("  before:", before)
            print("  after :", after)

    # the fallback order must also agree with the POOL's order
    for route in reg.get("routes", []):
        lane = route.get("lane")
        if lane not in LANES:
            continue
        arms_order = [(a.get("provider"), a.get("model")) for a in route.get("arms", [])]
        pool_lane = pool_order.get(lane, [])
        agree = arms_order == pool_lane
        print(f"\n{lane}: registry arms == pool ordered_pool ? {agree}")
        if not agree:
            print("   registry:", arms_order)
            print("   pool    :", pool_lane)
            print("REFUSE: the registry's arm order does not match the pool; "
                  "the two must be derived from one source.")
            return 2

    out = yaml.safe_dump(reg, sort_keys=False, allow_unicode=True, width=100)
    REG.write_text(out, encoding="utf-8", newline="\n")
    post = sha256_bytes(REG.read_bytes())
    print(f"\nregistry post-image sha256: {post}")

    # verify
    import sys as _s
    _s.path.insert(0, str(HGK / "src"))
    from hg_kseos import lane_policy as lp
    findings = lp.check_drift()
    print(f"drift gate: {len(findings)} findings, fatal={lp.drift_is_fatal(findings)}")
    for f in findings[:15]:
        print("  ", f.get("severity"), f.get("code"), f.get("path"), f.get("pointer"),
              "| exp:", str(f.get("expected"))[:40], "| act:", str(f.get("actual"))[:40])

    RECEIPT.write_text(json.dumps({
        "schema": "HGK-OWNER-AUTHORIZED-CONFIG-CHANGE/1",
        "artifact": "REGISTRY_FALLBACKS_REPAIR_RECEIPT",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "target": str(REG),
        "pre_image_sha256": pre,
        "post_image_sha256": post,
        "defect": (
            "the GPT-promotion apply derived `fallbacks` by matching the OLD fallback list, "
            "which did not contain the arm that was rank-1 (minimax). The demoted primary was "
            "therefore dropped from every route's fallback list, contradicting the route's own "
            "arms list and making 'the minimax arm is retained as a reachable fallback' false "
            "in the artifact."
        ),
        "fix": "fallbacks := arms[1:] in provider/model order, identity fields taken from the arms entry",
        "changes": changes,
        "drift_findings": findings,
        "applied": True,
        "claim_ceiling": (
            "a repair of the declaration's internal consistency, applied under the same owner "
            "order that produced it. CANDIDATE_ONLY: not a native issuer signature, not an "
            "acceptance of any subject, not a promotion of the pool to ACTIVE."
        ),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nreceipt: {RECEIPT}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
