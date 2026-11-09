"""WP-FHS-03 — HGK Registry / Issuer / Receiver binding.

The W1 contract asks for one typed output: `IssuerReceiverBinding@design`, plus the statement that
an ECP intent is not a Permit. This module makes that statement executable:

* a Permit is a **signed** object with `work_id`, `subject`, `scope`, `policy_epoch`, `ttl`,
  `nonce`, `receiver`, `principal_sid` and an Ed25519 signature by the enrolled issuer key;
* an ECP / ECP intent / PLAN / TaskSpec presented as a Permit is refused with
  `WP-FHS-03.FIRST_FAIL:ISSUER_BINDING_INVALID` — the candidate namespace never mints work identity;
* the binding is only `BOUND` when the receiver exists in the *same* registry revision, is `ACTIVE`,
  speaks the same ABI, accepts the principal's SID, the nonce is unused and the TTL has not expired;
* an `UNKNOWN` world effect may not be retried: `reconcile` demands the original WorldReader's
  readback first.

Nothing here activates a work item: `state=BOUND` is a *design-time* binding at
`claim_ceiling=AUTHOR_DESIGN_ONLY`, the signature verification is real but the issuer is a test or
candidate key, and `issuer_permit_issued` stays `False`.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any

SCHEMA = "HGK.IssuerReceiverBinding@design"
WORK_ID_RE = re.compile(r"^WO-[A-Z0-9][A-Z0-9._:-]{2,63}$")
PERMIT_ID_RE = re.compile(r"^PERMIT-[A-Z0-9][A-Z0-9._:-]{2,63}$")

PERMIT_FIELDS = ("permit_id", "work_id", "subject", "scope", "policy_epoch", "issued_at",
                 "ttl_seconds", "nonce", "receiver", "receiver_abi", "principal_sid",
                 "issuer_key_id", "signature_hex")

# Document kinds that are *candidates*. Presenting one of them as a Permit is the W1 NEG.
CANDIDATE_KINDS = {"ECP", "ECP_INTENT", "ECP-CANDIDATE", "PLAN", "PLAN_PROPOSAL", "TASKSPEC",
                   "PI-PKG", "PD-PKG", "GITHUB_ISSUE", "REPO_FILE", "AUTHOR_DESIGN"}


class IssuerBindingRefusal(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code

    def as_dict(self) -> dict[str, Any]:
        return {"verdict": "REFUSED", "code": self.code, "message": str(self)}


def _invalid(message: str) -> IssuerBindingRefusal:
    return IssuerBindingRefusal(message, code="WP-FHS-03.FIRST_FAIL:ISSUER_BINDING_INVALID")


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def permit_body(permit: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in permit.items() if k != "signature_hex"}


def body_sha256(permit: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(permit_body(permit))).hexdigest()


def verify_signature(permit: dict[str, Any], issuer_public_hex: str) -> bool:
    """Verify the issuer's Ed25519 signature over the canonical permit body.

    Fails closed: a missing crypto library or a malformed key is a refusal, never a pass.
    """
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception as exc:  # pragma: no cover - environment failure, not a test path
        raise _invalid(f"signature verification unavailable: {exc}") from None
    try:
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(issuer_public_hex))
        key.verify(bytes.fromhex(permit["signature_hex"]), canonical(permit_body(permit)))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def admit_permit(permit: dict[str, Any]) -> dict[str, Any]:
    """Shape gate: a Permit must BE a permit, with every binding field present."""
    if not isinstance(permit, dict):
        raise _invalid("a permit is an object")
    kind = str(permit.get("kind") or permit.get("schema") or permit.get("type") or "").upper()
    if kind in CANDIDATE_KINDS:
        raise _invalid(
            f"a {kind} document is candidate material, not a Permit: an ECP intent cannot mint "
            "work identity or permission")
    missing = [f for f in PERMIT_FIELDS if not str(permit.get(f) or "").strip()]
    if missing:
        raise _invalid("permit is missing binding fields: " + ", ".join(missing))
    if not WORK_ID_RE.match(str(permit["work_id"])):
        raise _invalid(f"work_id is not an original WorkID: {permit['work_id']!r}")
    if not PERMIT_ID_RE.match(str(permit["permit_id"])):
        raise _invalid(f"permit_id is not an original Permit id: {permit['permit_id']!r}")
    if str(permit["receiver_abi"]).upper() not in {"HGK.PERMIT@2", "HGK.PERMIT@1"}:
        raise _invalid(f"receiver ABI is not an HGK permit ABI: {permit['receiver_abi']!r}")
    return dict(permit)


def bind(permit: dict[str, Any], registry: dict[str, Any], *, issuer_public_hex: str,
         now: float | None = None) -> dict[str, Any]:
    """Bind a Permit to its receiver inside ONE registry revision."""
    permit = admit_permit(permit)
    now = time.time() if now is None else float(now)
    reg_epoch = registry.get("policy_epoch")
    if str(reg_epoch) != str(permit["policy_epoch"]):
        raise IssuerBindingRefusal(
            f"permit epoch {permit['policy_epoch']} does not match registry epoch {reg_epoch}",
            code="ISSUER_WORK_BINDING_NACK")
    if not verify_signature(permit, issuer_public_hex):
        raise _invalid("issuer signature does not verify over the canonical permit body")

    receiver = (registry.get("receivers") or {}).get(permit["receiver"])
    if not receiver:
        raise IssuerBindingRefusal(
            f"receiver {permit['receiver']!r} is not in registry revision {registry.get('registry_rev')}",
            code="ISSUER_WORK_BINDING_NACK")
    if str(receiver.get("status") or "").upper() != "ACTIVE":
        raise IssuerBindingRefusal(f"receiver {permit['receiver']!r} is not ACTIVE",
                                   code="ISSUER_WORK_BINDING_NACK")
    if str(receiver.get("abi") or "") != str(permit["receiver_abi"]):
        raise IssuerBindingRefusal(
            f"receiver ABI {receiver.get('abi')!r} != permit ABI {permit['receiver_abi']!r}",
            code="ISSUER_WORK_BINDING_NACK")
    acl = {str(s) for s in (receiver.get("principal_acl") or [])}
    if acl and str(permit["principal_sid"]) not in acl:
        raise IssuerBindingRefusal(
            f"principal {permit['principal_sid']!r} is not admitted for receiver "
            f"{permit['receiver']!r}", code="ISSUER_PRINCIPAL_ACL_DENY")
    used = {str(n) for n in (registry.get("used_nonces") or [])}
    if str(permit["nonce"]) in used:
        raise IssuerBindingRefusal(f"nonce {permit['nonce']!r} was already used in this revision",
                                   code="ISSUER_WORK_BINDING_NACK")
    if str(permit["permit_id"]) in {str(p) for p in (registry.get("revoked_permits") or [])}:
        raise IssuerBindingRefusal(f"permit {permit['permit_id']!r} is revoked",
                                   code="ISSUER_WORK_BINDING_NACK")
    expires_at = float(permit["issued_at"]) + float(permit["ttl_seconds"])
    if now >= expires_at:
        raise IssuerBindingRefusal(
            f"permit expired at {time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(expires_at))}Z",
            code="ISSUER_WORK_BINDING_NACK")

    record = {
        "schema": SCHEMA,
        "work_id": permit["work_id"],
        "permit_id": permit["permit_id"],
        "subject": permit["subject"],
        "scope": permit["scope"],
        "policy_epoch": permit["policy_epoch"],
        "registry_rev": registry.get("registry_rev"),
        "receiver": permit["receiver"],
        "receiver_abi": permit["receiver_abi"],
        "principal_sid": permit["principal_sid"],
        "issuer_key_id": permit["issuer_key_id"],
        "nonce": permit["nonce"],
        "expires_at": int(expires_at),
        "permit_body_sha256": body_sha256(permit),
        "signature": {"alg": "ed25519", "verified": True,
                      "verified_against": "caller-supplied enrolled issuer key",
                      "original_issuer_receipt": "NOT_OBSERVED"},
        "state": "BOUND",
        "claim_ceiling": "AUTHOR_DESIGN_ONLY",
        "issuer_permit_issued": False,
        "not_claimed": ["permit effective", "host effect", "release"],
    }
    record["binding_sha256"] = hashlib.sha256(canonical(record)).hexdigest()
    return record


def reconcile(effect_state: str, *, world_readback: dict[str, Any] | None = None) -> dict[str, Any]:
    """`UNKNOWN` is reconciled by the original WorldReader; a blind retry is refused."""
    if str(effect_state).upper() != "UNKNOWN":
        return {"state": str(effect_state).upper(), "action": "NO_RECONCILE_REQUIRED"}
    if not world_readback:
        raise IssuerBindingRefusal(
            "an UNKNOWN world effect may not be retried before the original WorldReader readback: "
            "UNKNOWN_BLIND_RETRY_DENY", code="UNKNOWN_BLIND_RETRY_DENY")
    return {"state": "RECONCILED", "action": "MATCH_OR_COMPENSATE",
            "world_readback_sha256": hashlib.sha256(canonical(world_readback)).hexdigest(),
            "reader": world_readback.get("reader", "ORIGINAL_WORLD_READER")}


def revoke(permit: dict[str, Any], *, fence: int, reason: str) -> dict[str, Any]:
    """The original issuer's Revoke / lease fence — recorded, not executed here."""
    permit = admit_permit(permit)
    return {"schema": "HGK.IssuerRevocation@design", "permit_id": permit["permit_id"],
            "work_id": permit["work_id"], "fence_epoch": int(fence), "reason": reason,
            "state": "REVOKE_REQUESTED", "executed_by": "ORIGINAL_HGK_ISSUER",
            "executed": False, "rollback": "issuer revoke + lease fence; UNKNOWN reconciled first"}
