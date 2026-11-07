"""SBL 39 ModeGate: 13 gates x 3 modes."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .dto import ModeDecision
from .errors import SBLError

MODES: tuple[str, ...] = ("STANDALONE", "PREW3_SHADOW", "SWOF_CONNECTED")
GATE_IDS: tuple[str, ...] = tuple(f"G{i:02d}" for i in range(13))

DISPOSITIONS: dict[str, str] = {
    "STANDALONE": "ACTIVE",
    "PREW3_SHADOW": "SHADOW_NOEFFECT",
    "SWOF_CONNECTED": "BLOCKED_EXTERNAL",
}

_NATIVE_ACK_FIELDS = ("issuer", "permit_id", "subject_id", "signature")
# A native acknowledgement is a claim by an external issuer, so the four non-empty strings a caller can
# type are not evidence of anything. It is accepted only when the issuer is on the configured allowlist
# and the signature is the HMAC of the three identity fields under a key this build was given out of
# band. With no issuer list or no key the gate refuses, because an unverifiable ACK is not an ACK.
_ACK_ISSUERS_ENV = "SBL_SWOF_ACK_ISSUERS"
_ACK_KEY_ENV = "SBL_SWOF_ACK_KEY"
_PERMIT_STORE_ENV = "SBL_SWOF_PERMIT_STORE"
_ACK_LEGACY_ENV = "SBL_SWOF_ACK_LEGACY"

# D-18 / owner ruling: the gate itself -- not the tool around it -- must bind the ACK to a subject, a
# scope, a permit and a validity window. These four fields are therefore both REQUIRED and SIGNED.
# SBL-ACK@1 signed only (issuer, permit_id, subject_id), which made any of these fields an unauthenticated
# extra: an ACK with no expiry, a foreign subject, an undeclared scope or an unknown permit verified
# exactly like a good one (evidence D18/01_prepatch_holes.txt, P1-P5).
_BOUND_ACK_FIELDS = ("permit_sha256", "scope", "issued_at", "expires_at")
_ACK_SCHEME = "SBL-ACK@2"
_TIMESTAMP_FMT = "%Y-%m-%dT%H:%M:%SZ"
_PERMIT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def ack_signature(issuer: str, permit_id: str, subject_id: str, key: str) -> str:
    """The legacy (SBL-ACK@1) signature: three fields, no expiry, no scope, no permit binding.

    Kept verbatim because :data:`SBL_SWOF_ACK_LEGACY_ENV` still has to verify the ACKs that were
    issued under it, and because existing callers import it.
    """

    # Length-prefixed, not delimiter-joined: with a bare separator, ("a\x1fB", "C") and ("a", "B\x1fC")
    # produce identical material and therefore interchangeable signatures (V16-MODE-02).
    parts = (str(issuer), str(permit_id), str(subject_id))
    material = "".join(f"{len(part)}:{part}" for part in parts).encode("utf-8")
    return hmac.new(str(key).encode("utf-8"), material, hashlib.sha256).hexdigest()


def ack_canonical_v2(
    issuer: str,
    permit_id: str,
    subject_id: str,
    permit_sha256: str,
    scope: str,
    issued_at: str,
    expires_at: str,
) -> bytes:
    """The canonical bytes SBL-ACK@2 signs: a scheme tag plus all seven fields, length-prefixed.

    The scheme tag is the first segment so a signature minted under one scheme can never be read as a
    signature under another. An absent field is the empty string, encoded as ``0:`` -- distinct from
    every non-empty value because of the length prefix, which is why the four-field form cannot be
    confused with a bound one that happens to omit a field.
    """

    parts = (
        _ACK_SCHEME,
        str(issuer),
        str(permit_id),
        str(subject_id),
        str(permit_sha256 or ""),
        str(scope or ""),
        str(issued_at or ""),
        str(expires_at or ""),
    )
    return "".join(f"{len(part)}:{part}" for part in parts).encode("utf-8")


def ack_signature_v2(
    issuer: str,
    permit_id: str,
    subject_id: str,
    permit_sha256: str,
    scope: str,
    issued_at: str,
    expires_at: str,
    key: str,
) -> str:
    """HMAC-SHA256 over :func:`ack_canonical_v2`. The only signature the strict gate accepts."""

    material = ack_canonical_v2(
        issuer, permit_id, subject_id, permit_sha256, scope, issued_at, expires_at
    )
    return hmac.new(str(key).encode("utf-8"), material, hashlib.sha256).hexdigest()


def scope_digest(scope: Iterable[str]) -> str:
    """sha256 over the sorted, length-prefixed members of an ECP scope.

    Sorted, because a scope is a set of paths and the digest must not depend on declaration order;
    length-prefixed, because ``["a:b"]`` and ``["a", "b"]`` must not collide.
    """

    parts = sorted(str(item) for item in scope)
    material = "".join(f"{len(part)}:{part}" for part in parts).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _now() -> datetime:
    """The gate's only clock. A function so a test can freeze it; not reachable from an ACK."""

    return datetime.now(timezone.utc)


def _mac_equal(left: Any, right: Any) -> bool:
    """Constant-time comparison of two untrusted strings.

    ``hmac.compare_digest`` raises ``TypeError`` when either ``str`` contains non-ASCII, which would
    turn a hostile ACK field into a crash instead of a typed refusal. Comparing UTF-8 bytes keeps the
    comparison constant-time for every input.
    """

    return hmac.compare_digest(str(left).encode("utf-8"), str(right).encode("utf-8"))


def _parse_instant(value: str, field: str) -> datetime:
    try:
        return datetime.strptime(str(value), _TIMESTAMP_FMT).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        raise SBLError(
            "SBL_E_ACK_MALFORMED_FIELD",
            f"native ACK field {field!r} is not a UTC timestamp of the form YYYY-MM-DDTHH:MM:SSZ",
            {"state": f"MALFORMED:{field}", "required_format": _TIMESTAMP_FMT, "field": field},
        ) from None


def _configured_issuers() -> set[str]:
    raw = os.environ.get(_ACK_ISSUERS_ENV, "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _legacy_enabled() -> bool:
    """Legacy SBL-ACK@1 acceptance is CLOSED. Always False.

    The four-field form has no expiry, no scope and no permit binding, so one signature authorised
    every claim that reused it (measured: 461472d2 signed six different subjects). The switch is kept
    as a symbol because callers import it, but it can no longer enable acceptance: setting the env now
    yields ``SBL_ACK_LEGACY_ACCEPTANCE_CLOSED`` instead of a verified ACK.

    Original note, kept for archaeology: exact ``1`` only, and never the default.

    ``""``, ``"0"``, ``"true"``, ``"yes"``, ``" 1"`` all read as strict, so the downgrade cannot be
    reached by a config flag that merely looks truthy. It is still an env switch, which is the same
    trust root the ACK key and issuer list already come from: a process able to set this can set
    ``SBL_SWOF_ACK_KEY`` and mint a compliant ACK anyway, so it grants no authority that was not
    already there. It does make the resulting decisions say so (``NATIVE_ACK_VERIFIED_LEGACY_UNBOUND``).
    """

    return False


def _complete_ack(native_ack: Any) -> bool:
    if not isinstance(native_ack, dict):
        return False
    for field in _NATIVE_ACK_FIELDS:
        value = native_ack.get(field)
        if not isinstance(value, str) or not value.strip():
            return False
    return True


def _present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_bound_fields(native_ack: dict[str, Any]) -> None:
    """Missing-field refusal, one field at a time, so the detail names what the issuer must add."""

    for field in _BOUND_ACK_FIELDS:
        if not _present(native_ack.get(field)):
            raise SBLError(
                "SBL_E_ACK_MISSING_FIELD",
                f"native ACK is missing the signed field {field!r}",
                {
                    "state": f"MISSING:{field}",
                    "field": field,
                    "required": list(_NATIVE_ACK_FIELDS) + list(_BOUND_ACK_FIELDS),
                },
            )


def _resolve_permit(permit_id: str, permit_sha256: str) -> dict[str, Any]:
    """Resolve ``permit_id`` in the permit store and prove the ACK carries that permit's digest.

    The store is a directory of ``<permit_id>.json`` files; the digest is over the file's exact bytes,
    so a permit document that is edited after the ACK was issued stops matching. ``permit_id`` is
    validated against an allowlist pattern before it touches the filesystem, so an ACK cannot walk out
    of the store.
    """

    root = os.environ.get(_PERMIT_STORE_ENV, "")
    if not root or not Path(root).is_dir():
        raise SBLError(
            "SBL_E_ACK_PERMIT_UNKNOWN",
            "no permit store is configured, so the ACK's permit cannot be resolved",
            {"state": "NO_PERMIT_STORE", "env": _PERMIT_STORE_ENV, "permit_id": permit_id},
        )
    if not _PERMIT_ID_RE.match(permit_id):
        raise SBLError(
            "SBL_E_ACK_PERMIT_UNKNOWN",
            "permit_id is not a storable permit identifier",
            {"state": "PERMIT_ID_UNSAFE", "permit_id": permit_id},
        )
    path = Path(root) / f"{permit_id}.json"
    if not path.is_file():
        raise SBLError(
            "SBL_E_ACK_PERMIT_UNKNOWN",
            f"permit {permit_id!r} is not in the permit store",
            {"state": "PERMIT_NOT_IN_STORE", "permit_id": permit_id, "store": str(root)},
        )
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if not _mac_equal(actual, str(permit_sha256).strip().lower()):
        raise SBLError(
            "SBL_E_ACK_PERMIT_MISMATCH",
            "the ACK's permit digest is not the digest of the stored permit",
            {
                "state": "MISMATCH:permit_sha256",
                "permit_id": permit_id,
                "ack": str(permit_sha256),
                "store": actual,
            },
        )
    try:
        document = json.loads(raw)
    except ValueError:
        raise SBLError(
            "SBL_E_ACK_PERMIT_UNKNOWN",
            f"permit {permit_id!r} is not readable as JSON",
            {"state": "PERMIT_UNREADABLE", "permit_id": permit_id},
        ) from None
    if not isinstance(document, dict):
        raise SBLError(
            "SBL_E_ACK_PERMIT_UNKNOWN",
            f"permit {permit_id!r} is not a permit object",
            {"state": "PERMIT_UNREADABLE", "permit_id": permit_id},
        )
    if document.get("permit_id") != permit_id:
        raise SBLError(
            "SBL_E_ACK_PERMIT_MISMATCH",
            "the stored permit does not declare the permit_id the ACK names",
            {"state": "PERMIT_BINDING_ID", "permit_id": permit_id},
        )
    return document


def _ecp_binding(ecp: Any) -> tuple[str, str]:
    """Returns (subject_id, scope_digest) for the ECP the effect claims to be authorised under."""

    if not isinstance(ecp, dict):
        raise SBLError(
            "SBL_E_ACK_ECP_MISSING",
            "SWOF_CONNECTED needs the ECP to bind the ACK to; none was supplied",
            {"state": "ECP_ABSENT", "required": ["subject_id", "scope"]},
        )
    subject = ecp.get("subject_id")
    if not _present(subject):
        raise SBLError(
            "SBL_E_ACK_ECP_MISSING",
            "the ECP declares no subject_id, so the ACK's subject cannot be checked",
            {"state": "ECP_SUBJECT_MISSING", "ecp_keys": sorted(str(k) for k in ecp)},
        )
    scope = ecp.get("scope")
    if (
        not isinstance(scope, (list, tuple))
        or not scope
        or not all(_present(item) for item in scope)
    ):
        raise SBLError(
            "SBL_E_ACK_ECP_MISSING",
            "the ECP declares no non-empty scope list, so the ACK's scope cannot be checked",
            {"state": "ECP_SCOPE_MISSING", "ecp_keys": sorted(str(k) for k in ecp)},
        )
    return str(subject).strip(), scope_digest(scope)


def _ack_state(native_ack: Any, ecp: Any = None) -> tuple[bool, str]:
    """Returns (verified, reason) for the legacy form; raises :class:`SBLError` for every bound refusal.

    Anything short of a verified ACK is a refusal, never a default allow. The order is deliberate:
    presence, then trust anchors, then issuer, then the signature over ALL signed fields, and only
    then the semantic binds (ECP, clock, permit). A semantic refusal therefore always proves the ACK
    was authentic -- which is what makes each code below actionable by the issuer.
    """

    if not _complete_ack(native_ack):
        return False, "ACK_INCOMPLETE"
    issuers = _configured_issuers()
    if not issuers:
        return False, f"NO_TRUSTED_ISSUERS_CONFIGURED:{_ACK_ISSUERS_ENV}"
    key = os.environ.get(_ACK_KEY_ENV, "")
    if not key:
        return False, f"NO_VERIFICATION_KEY_CONFIGURED:{_ACK_KEY_ENV}"
    issuer = str(native_ack.get("issuer"))
    if issuer not in issuers:
        return False, "ISSUER_NOT_TRUSTED"

    if os.environ.get(_ACK_LEGACY_ENV, "") == "1":
        # The escape hatch is closed: an operator who sets it must be told the mode is gone rather
        # than silently receiving a strict-mode refusal they cannot interpret.
        return False, "SBL_ACK_LEGACY_ACCEPTANCE_CLOSED"

    _require_bound_fields(native_ack)
    expected_v2 = ack_signature_v2(
        issuer,
        str(native_ack.get("permit_id")),
        str(native_ack.get("subject_id")),
        str(native_ack.get("permit_sha256")),
        str(native_ack.get("scope")),
        str(native_ack.get("issued_at")),
        str(native_ack.get("expires_at")),
        key,
    )
    if not _mac_equal(expected_v2, str(native_ack.get("signature")).strip().lower()):
        return False, "SIGNATURE_MISMATCH"

    ecp_subject, ecp_scope = _ecp_binding(ecp)
    issued_at = _parse_instant(native_ack["issued_at"], "issued_at")
    expires_at = _parse_instant(native_ack["expires_at"], "expires_at")
    now = _now()

    if expires_at <= issued_at:
        raise SBLError(
            "SBL_E_ACK_MALFORMED_FIELD",
            "the ACK's expiry does not follow its issue time",
            {
                "state": "MALFORMED:expires_at",
                "issued_at": native_ack["issued_at"],
                "expires_at": native_ack["expires_at"],
            },
        )
    if issued_at > now:
        raise SBLError(
            "SBL_E_ACK_NOT_YET_VALID",
            "the ACK is not valid yet",
            {"state": "ISSUED_IN_FUTURE", "issued_at": native_ack["issued_at"]},
        )
    if expires_at <= now:
        raise SBLError(
            "SBL_E_ACK_EXPIRED",
            "the ACK has expired",
            {
                "state": "EXPIRED",
                "expires_at": native_ack["expires_at"],
                "now": now.strftime(_TIMESTAMP_FMT),
            },
        )

    if str(native_ack["subject_id"]).strip() != ecp_subject:
        raise SBLError(
            "SBL_E_ACK_SUBJECT_MISMATCH",
            "the ACK's subject is not the ECP's subject",
            {
                "state": "SUBJECT_MISMATCH",
                "ack": str(native_ack["subject_id"]),
                "ecp": ecp_subject,
            },
        )

    if str(native_ack["scope"]).strip() != ecp_scope:
        raise SBLError(
            "SBL_E_ACK_SCOPE_MISMATCH",
            "the ACK's scope is not the scope the ECP declares",
            {
                "state": "SCOPE_MISMATCH",
                "ack": str(native_ack["scope"]),
                "ecp": ecp_scope,
            },
        )

    permit = _resolve_permit(str(native_ack["permit_id"]), str(native_ack["permit_sha256"]))
    if str(permit.get("subject_id", "")).strip() != ecp_subject:
        raise SBLError(
            "SBL_E_ACK_PERMIT_MISMATCH",
            "the stored permit is issued to a different subject",
            {
                "state": "PERMIT_BINDING_SUBJECT",
                "permit_id": native_ack["permit_id"],
                "permit": permit.get("subject_id"),
                "ecp": ecp_subject,
            },
        )
    if str(permit.get("scope", "")).strip() != str(native_ack["scope"]).strip():
        raise SBLError(
            "SBL_E_ACK_PERMIT_MISMATCH",
            "the stored permit authorises a different scope",
            {
                "state": "PERMIT_BINDING_SCOPE",
                "permit_id": native_ack["permit_id"],
                "permit": permit.get("scope"),
                "ack": native_ack["scope"],
            },
        )
    permit_issued = _parse_instant(permit.get("issued_at", ""), "permit.issued_at")
    permit_expires = _parse_instant(permit.get("expires_at", ""), "permit.expires_at")
    if permit_expires <= now:
        raise SBLError(
            "SBL_E_ACK_PERMIT_MISMATCH",
            "the stored permit has expired",
            {
                "state": "PERMIT_EXPIRED",
                "permit_id": native_ack["permit_id"],
                "expires_at": permit.get("expires_at"),
            },
        )
    if permit_issued > now:
        raise SBLError(
            "SBL_E_ACK_PERMIT_MISMATCH",
            "the stored permit is not yet valid",
            {"state": "PERMIT_NOT_YET_VALID", "permit_id": native_ack["permit_id"]},
        )
    if expires_at > permit_expires:
        raise SBLError(
            "SBL_E_ACK_PERMIT_MISMATCH",
            "the ACK outlives the permit it cites",
            {
                "state": "ACK_OUTLIVES_PERMIT",
                "expires_at": native_ack["expires_at"],
                "permit_expires_at": permit.get("expires_at"),
            },
        )
    return True, "NATIVE_ACK_VERIFIED_STRICT"


def mode_gate_matrix() -> list[dict[str, str]]:
    """Returns 39 unique gate rows: each gate in each of the three modes."""

    rows: list[dict[str, str]] = []
    for mode in MODES:
        for gate in GATE_IDS:
            rows.append(
                {
                    "gate_id": f"SBL-{gate}-{mode}",
                    "mode": mode,
                    "gate": gate,
                    "disposition": DISPOSITIONS[mode],
                }
            )
    return rows


class ModeGate:
    """Decides whether an effect may occur in the active execution mode."""

    def __init__(
        self,
        mode: str,
        native_ack: dict[str, Any] | None = None,
        ecp: dict[str, Any] | None = None,
    ) -> None:
        if mode not in MODES:
            raise SBLError(
                "SBL_E_UNKNOWN_MODE",
                f"unknown mode: {mode!r}",
                {"mode": mode, "modes": list(MODES)},
            )
        self.mode = mode
        self.native_ack = dict(native_ack) if isinstance(native_ack, dict) else None
        # ``ecp`` is what the effect claims to be authorised under. Without it there is nothing to bind
        # the ACK's subject and scope to, so SWOF_CONNECTED refuses rather than allowing.
        self.ecp = dict(ecp) if isinstance(ecp, dict) else ecp

    def decide(self, effect: str) -> ModeDecision:
        effect = str(effect)
        if self.mode == "PREW3_SHADOW":
            return ModeDecision(
                mode=self.mode,
                effect=effect,
                allowed=False,
                no_effect=True,
                reason="SHADOW_READ_ONLY_NO_EFFECT",
            )
        if self.mode == "STANDALONE":
            allowed = effect in {"local.write", "local.read"}
            return ModeDecision(
                mode=self.mode,
                effect=effect,
                allowed=allowed,
                no_effect=not allowed,
                reason="LOCAL_EFFECT_ALLOWED" if allowed else "EFFECT_NOT_ALLOWED",
            )
        verified, ack_reason = _ack_state(self.native_ack, self.ecp)
        if not verified:
            raise SBLError(
                "SBL_E_REQUIRES_NATIVE_ACK",
                "SWOF_CONNECTED requires a verifiable native acknowledgement",
                {
                    "mode": self.mode,
                    "required": list(_NATIVE_ACK_FIELDS) + list(_BOUND_ACK_FIELDS),
                    "state": ack_reason,
                },
            )
        return ModeDecision(
            mode=self.mode,
            effect=effect,
            allowed=True,
            no_effect=False,
            reason=ack_reason,
        )
