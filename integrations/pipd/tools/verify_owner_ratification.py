#!/usr/bin/env python3
"""Verify an owner-signed ratification of the operation→effect contract.

The writer does not promote its own authority: this tool is the independent check.
It pins the owner public key from `contracts/owner-enrollment.json` (never from the
sidecar, which an attacker could self-sign), recomputes the payload digest over the
exact signed bytes, and verifies the Ed25519 signature.

Exit codes: 0 verified, 1 refused, 2 verifier unavailable.

Needs `cryptography` for Ed25519. If it is missing this tool fails closed (exit 2)
rather than accepting an unverified claim.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CONTRACTS = Path(__file__).resolve().parents[1] / "contracts"
CONTRACT = CONTRACTS / "operation-registry.pre-v2-r3.json"
ENROLLMENT = CONTRACTS / "owner-enrollment.json"
SIDECAR = CONTRACTS / "operation-registry.pre-v2-r3.owner.sig.json"

REQUIRED_DECISION = "RATIFY_OPERATION_EFFECT_BINDING"


def fail(code: str, **extra) -> int:
    print(json.dumps({"verified": False, "first_fail": code, **extra}, ensure_ascii=False, sort_keys=True))
    return 1


def main() -> int:
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception:  # pragma: no cover - environment dependent
        print(json.dumps({"verified": False, "first_fail": "OWNER_SIGNATURE_VERIFIER_UNAVAILABLE"}, sort_keys=True))
        return 2

    for path in (CONTRACT, ENROLLMENT, SIDECAR):
        if not path.is_file():
            return fail("MISSING:" + path.name)

    contract_sha = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    enrollment = json.loads(ENROLLMENT.read_text(encoding="utf-8"))
    sidecar = json.loads(SIDECAR.read_text(encoding="utf-8"))

    if enrollment.get("schema") != "SBL.PRE_V2.OWNER_ENROLLMENT@1":
        return fail("ENROLLMENT_SCHEMA")
    if sidecar.get("contract_sha256") != contract_sha:
        return fail("CONTRACT_SHA_MISMATCH", expected=contract_sha, signed=sidecar.get("contract_sha256"))

    payload = (sidecar.get("payload_json") or "").encode("utf-8")
    if hashlib.sha256(payload).hexdigest() != sidecar.get("payload_sha256"):
        return fail("PAYLOAD_SHA_MISMATCH")

    body = json.loads(payload)
    if body.get("decision") != REQUIRED_DECISION:
        return fail("DECISION_NOT_RATIFICATION", decision=body.get("decision"))
    if body.get("contract_id") != sidecar.get("contract_id"):
        return fail("CONTRACT_ID_MISMATCH")
    if body.get("contract_sha256") != contract_sha:
        return fail("PAYLOAD_CONTRACT_SHA_MISMATCH")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    declared = {row.get("operation_type") for row in contract.get("operations", [])}
    ratified = set(body.get("operations") or [])
    if not ratified or not ratified <= declared:
        return fail("RATIFIED_OPERATIONS_NOT_IN_CONTRACT", ratified=sorted(ratified), declared=sorted(declared))

    try:
        public = Ed25519PublicKey.from_public_bytes(bytes.fromhex(enrollment["owner_public_hex"]))
        public.verify(bytes.fromhex(sidecar["signature_hex"]), payload)
    except InvalidSignature:
        return fail("SIGNATURE_INVALID")
    except Exception as exc:  # malformed hex, wrong length, ...
        return fail("SIGNATURE_UNREADABLE", detail=type(exc).__name__)

    print(
        json.dumps(
            {
                "verified": True,
                "authority": "SOURCE_BOUND_OWNER_RATIFIED",
                "contract_id": sidecar["contract_id"],
                "contract_sha256": contract_sha,
                "owner_fingerprint": enrollment.get("owner_fingerprint"),
                "window_id": sidecar.get("window_id"),
                "signed_at": sidecar.get("signed_at"),
                "operations": sorted(ratified),
                "grant_state": "NOT_GRANTED",
                "claim_ceiling": "DESIGN_ONLY",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
