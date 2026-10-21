#!/usr/bin/env python
"""Update the registry's SoD declaration to match the owner-ordered model assignment.

DEFECT FOUND BY THE CONFORMANCE TEST (not by inspection):
  After the GPT-6.1-SOL promotion, the EXECUTE and VERIFY_SECURITY lanes run on
  DIFFERENT models (deepseek-v4.1-flash vs gpt-6.1-sol), so the SoD check now
  reports them as SEPARATED. But the registry's `sod_invariants.pairs` still
  declared that pair `distinct_required: false` -- a leftover from the round in
  which all three lanes ran minimax. The conformance test asserts that a pair
  declared OPEN really IS colliding, so the stale declaration fails the gate.

  The declaration must follow the owner order:
    EXECUTE      = opencode-go/deepseek-v4.1-flash
    VERIFY       = openai-codex/gpt-6.1-sol
    PLAN         = openai-codex/gpt-6.1-sol
  so:
    EXECUTE ~ VERIFY_SECURITY  -> DIFFERENT models, DIFFERENT providers -> the
        separation HOLDS and must be asserted (`distinct_required: true`).
    PLAN ~ VERIFY_SECURITY     -> the SAME model, BY OWNER ORDER -> the
        collision is real and is declared OPEN_OWNER_ORDERED (SOD006-C4), so
        `distinct_required: false` stays and the declared conflict must exist.

  This is a DECLARATION update under the same owner order that produced the
  model assignment; it does not weaken any check.
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
RECEIPT = HGK / "var" / "R7-LANES" / "gpt61_sod_declaration_receipt.json"

# The owner-ordered model per lane, from the pool that is now in force.
LANE_MODEL = {
    "PLAN": ("openai-codex", "gpt-6.1-sol"),
    "EXECUTE": ("opencode-go", "deepseek-v4.1-flash"),
    "VERIFY_SECURITY": ("openai-codex", "gpt-6.1-sol"),
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    raw = REG.read_bytes()
    pre = sha256_bytes(raw)
    print("registry pre-image sha256:", pre)

    reg = yaml.safe_load(raw.decode("utf-8"))
    sod = reg.setdefault("sod_invariants", {})

    changes = []
    for pair in sod.get("pairs", []):
        maker, checker = pair.get("maker"), pair.get("checker")
        if maker not in LANE_MODEL or checker not in LANE_MODEL:
            continue
        mp, mm = LANE_MODEL[maker]
        cp, cm = LANE_MODEL[checker]
        same_model = (mm == cm)
        want_distinct = not same_model
        if pair.get("distinct_required") != want_distinct:
            changes.append({
                "pair": f"{maker}~{checker}",
                "was": pair.get("distinct_required"),
                "now": want_distinct,
                "why": (
                    f"{maker} is {mp}/{mm} and {checker} is {cp}/{cm}; "
                    + ("the models are the SAME, so the collision is real and is declared OPEN"
                       if same_model else
                       "the models DIFFER, so the separation holds and must be asserted")
                ),
            })
            pair["distinct_required"] = want_distinct
        pair["note"] = (
            f"Owner order 2026-10-21 (GPT quota restored): {maker} is {mp}/{mm} and {checker} "
            f"is {cp}/{cm}. "
            + (f"The models are the SAME, so the collision is REAL and is declared "
               f"OPEN_OWNER_ORDERED; independence for this pair is PROCESS separation only and "
               f"model independence is NOT claimed."
               if same_model else
               f"The models DIFFER and so do the providers, so the maker/checker separation "
               f"HOLDS on the model axis and is asserted here.")
        )

    # the declared conflicts must list the pairs that are genuinely open
    conflicts = sod.setdefault("declared_conflicts", [])
    open_pairs = {f"{p['maker']}~{p['checker']}"
                  for p in sod.get("pairs", [])
                  if p.get("distinct_required") is False}
    declared_ids = {c.get("id") for c in conflicts}
    for c in conflicts:
        pair_ref = c.get("pair")
        if pair_ref and pair_ref in open_pairs:
            continue
    # the EXECUTE~VERIFY conflict (SOD006-C3, same-model collision) is now
    # SUPERSEDED: the two lanes are on different models again. Mark it, do not
    # delete it -- the history stays auditable.
    for c in conflicts:
        if c.get("id") == "SOD006-C3" and c.get("pair") == "EXECUTE~VERIFY_SECURITY":
            c["status"] = "SUPERSEDED_2026_10_21"
            c["superseded_by"] = (
                "Owner order 2026-10-21 (GPT quota restored): EXECUTE is "
                "opencode-go/deepseek-v4.1-flash and VERIFY_SECURITY is "
                "openai-codex/gpt-6.1-sol, so the same-model collision this conflict "
                "declared NO LONGER HOLDS; the pair is separated on the model axis again."
            )
            changes.append({"conflict": "SOD006-C3", "now": "SUPERSEDED_2026_10_21"})

    for ch in changes:
        print("  change:", ch)

    out = yaml.safe_dump(reg, sort_keys=False, allow_unicode=True, width=100)
    REG.write_text(out, encoding="utf-8", newline="\n")
    post = sha256_bytes(REG.read_bytes())
    print(f"\nregistry post-image sha256: {post}")

    sys.path.insert(0, str(HGK / "src"))
    from hg_kseos import lane_policy as lp
    findings = lp.check_drift()
    print(f"drift gate: {len(findings)} findings, fatal={lp.drift_is_fatal(findings)}")
    for f in findings[:15]:
        print("  ", f.get("severity"), f.get("code"), f.get("path"), f.get("pointer"),
              "| exp:", str(f.get("expected"))[:40], "| act:", str(f.get("actual"))[:40])

    RECEIPT.write_text(json.dumps({
        "schema": "HGK-OWNER-AUTHORIZED-CONFIG-CHANGE/1",
        "artifact": "REGISTRY_SOD_DECLARATION_RECEIPT",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "target": str(REG),
        "pre_image_sha256": pre,
        "post_image_sha256": post,
        "defect": (
            "the EXECUTE~VERIFY_SECURITY SoD pair was still declared distinct_required=false "
            "from the round in which all three lanes ran minimax; after the GPT-6.1-SOL "
            "promotion the two lanes run DIFFERENT models, so the stale declaration fails "
            "the conformance gate."
        ),
        "fix": (
            "distinct_required is recomputed from the owner-ordered model per lane: false "
            "where the models are the same (PLAN~VERIFY_SECURITY, both gpt-6.1-sol, declared "
            "OPEN_OWNER_ORDERED) and true where they differ (EXECUTE~VERIFY_SECURITY). The "
            "superseded same-model conflict is MARKED, not deleted."
        ),
        "changes": changes,
        "drift_findings": findings,
        "applied": True,
        "claim_ceiling": (
            "a declaration update under the owner order that produced the model assignment. "
            "CANDIDATE_ONLY: not a native issuer signature, not an acceptance of any subject."
        ),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nreceipt: {RECEIPT}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
