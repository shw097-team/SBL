"""D-18 acceptance: the native ACK gate must bind issuer, subject, scope, permit and expiry.

Every refusal test here is written to pass ONLY against a gate that enforces the binding.
On the pre-patch gate (``sbl_core/modes.py`` sha256 ``b0d81ee6...``) each of them accepts the
defective ACK, so each one fails with ``ACCEPTED`` instead of the expected refusal.

The signature helper signs with the strongest canonical form the imported gate implements:
``SBL-ACK@2`` (all seven fields) when it exists, else the legacy three-field ``SBL-ACK@1``
form that the pre-patch gate accepts and that ignores every extra key. That fallback is the
defect being measured: pre-patch, one signature over (issuer, permit_id, subject_id)
authorises any scope, any expiry and any permit.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from datetime import datetime, timedelta, timezone

import pytest

from sbl_core import modes
from sbl_core.errors import SBLError

KEY = "k" * 32
ISSUER = "native-host"
PERMIT_ID = "PERMIT-d18"
SUBJECT = "ECP-d18a4f3c0d1e2b5a"
SCOPE = ["sbl_core/modes.py", "tests/test_ack_binding.py"]
FIXED = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _dt(seconds: int) -> str:
    return _iso(FIXED + timedelta(seconds=seconds))


def _scope_digest(scope) -> str:
    """The contract's scope digest, reimplemented here so the tests pin the bytes."""

    material = "".join(f"{len(p)}:{p}" for p in sorted(str(x) for x in scope)).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _sign(ack: dict, key: str = KEY) -> str:
    signer = getattr(modes, "ack_signature_v2", None)
    if signer is None:  # pre-patch: the only form that exists, and it ignores extra keys
        return modes.ack_signature(ack["issuer"], ack["permit_id"], ack["subject_id"], key)
    return signer(
        ack.get("issuer", ""),
        ack.get("permit_id", ""),
        ack.get("subject_id", ""),
        ack.get("permit_sha256", ""),
        ack.get("scope", ""),
        ack.get("issued_at", ""),
        ack.get("expires_at", ""),
        key,
    )


def _permit_doc(**overrides) -> dict:
    doc = {
        "permit_id": PERMIT_ID,
        "subject_id": SUBJECT,
        "scope": _scope_digest(SCOPE),
        "issued_at": _dt(-120),
        "expires_at": _dt(3600),
    }
    doc.update(overrides)
    return doc


def _write_store(root, doc: dict, filename: str | None = None) -> tuple[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / (filename or f"{doc.get('permit_id', PERMIT_ID)}.json")
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(root), hashlib.sha256(path.read_bytes()).hexdigest()


def _ack(permit_sha: str, **overrides) -> dict:
    ack = {
        "issuer": ISSUER,
        "permit_id": PERMIT_ID,
        "subject_id": SUBJECT,
        "permit_sha256": permit_sha,
        "scope": _scope_digest(SCOPE),
        "issued_at": _dt(-60),
        "expires_at": _dt(600),
    }
    ack.update(overrides)
    for field in [key for key, value in overrides.items() if value is None]:
        ack.pop(field, None)
    ack["signature"] = _sign(ack)
    return ack


@pytest.fixture
def world(monkeypatch, tmp_path):
    """Trust anchors, one permit store, and a frozen clock."""

    monkeypatch.setattr(modes, "_now", lambda: FIXED, raising=False)
    monkeypatch.setenv("SBL_SWOF_ACK_ISSUERS", ISSUER)
    monkeypatch.setenv("SBL_SWOF_ACK_KEY", KEY)
    store, permit_sha = _write_store(tmp_path / "permits", _permit_doc())
    monkeypatch.setenv("SBL_SWOF_PERMIT_STORE", store)
    monkeypatch.delenv("SBL_SWOF_ACK_LEGACY", raising=False)
    return {"store": store, "permit_sha": permit_sha, "tmp": tmp_path}


ECP = {"subject_id": SUBJECT, "scope": list(SCOPE)}

# The pre-patch constructor takes only (mode, native_ack): there is no ECP for it to bind against.
# Fall back to that call shape so a refusal test fails with "ACCEPTED", not with a TypeError.
_ACCEPTS_ECP = "ecp" in inspect.signature(modes.ModeGate.__init__).parameters


def _decide(ack, ecp=ECP):
    gate = (
        modes.ModeGate("SWOF_CONNECTED", native_ack=ack, ecp=ecp)
        if _ACCEPTS_ECP
        else modes.ModeGate("SWOF_CONNECTED", native_ack=ack)
    )
    return gate.decide("repo.write")


def _expect_refusal(ack, code: str, ecp=ECP, state: str | None = None) -> SBLError:
    try:
        decision = _decide(ack, ecp)
    except SBLError as exc:
        assert exc.code == code, f"expected {code}, got {exc.code} ({exc.detail})"
        if state is not None:
            assert state in str(exc.detail.get("state")), f"expected state~{state}, got {exc.detail}"
        return exc
    raise AssertionError(
        f"ACCEPTED: allowed={decision.allowed} reason={decision.reason} for ack {ack}"
    )


# --------------------------------------------------------------------------- positive path


def test_strict_positive_bound_ack_is_allowed(world):
    decision = _decide(_ack(world["permit_sha"]))
    assert decision.allowed is True
    assert decision.no_effect is False
    assert decision.reason == "NATIVE_ACK_VERIFIED_STRICT"


def test_scope_digest_bytes_are_pinned():
    """The digest the ACK signs is a byte-level contract, not an internal detail."""

    assert _scope_digest(SCOPE) == "6899759aaa5f21cee9106e5d39bfd6661f83b12becb9ea3d9d8f4805d05db7cc"
    assert _scope_digest(["b", "a"]) == _scope_digest(["a", "b"])  # order-insensitive set
    assert _scope_digest(["a:b"]) != _scope_digest(["a", "b"])  # length prefixes, no join
    assert modes.scope_digest(list(SCOPE)) == _scope_digest(SCOPE)


# --------------------------------------------------------------------------- expiry


@pytest.mark.parametrize("missing", ["expires_at", "issued_at", "scope", "permit_sha256"])
def test_refuses_ack_missing_a_bound_field(world, missing):
    ack = _ack(world["permit_sha"], **{missing: None})
    _expect_refusal(ack, "SBL_E_ACK_MISSING_FIELD", state=missing)


def test_refuses_expired_ack(world):
    ack = _ack(world["permit_sha"], issued_at=_dt(-7200), expires_at=_dt(-3600))
    _expect_refusal(ack, "SBL_E_ACK_EXPIRED")


def test_refuses_ack_expiring_exactly_now(world):
    ack = _ack(world["permit_sha"], expires_at=_dt(0))
    _expect_refusal(ack, "SBL_E_ACK_EXPIRED")


def test_refuses_ack_issued_in_the_future(world):
    ack = _ack(world["permit_sha"], issued_at=_dt(120), expires_at=_dt(3600))
    _expect_refusal(ack, "SBL_E_ACK_NOT_YET_VALID")


def test_refuses_ack_whose_expiry_precedes_its_issue(world):
    ack = _ack(world["permit_sha"], issued_at=_dt(60), expires_at=_dt(30))
    _expect_refusal(ack, "SBL_E_ACK_MALFORMED_FIELD", state="expires_at")


def test_refuses_unparseable_expiry(world):
    ack = _ack(world["permit_sha"], expires_at="next tuesday")
    _expect_refusal(ack, "SBL_E_ACK_MALFORMED_FIELD", state="expires_at")


# --------------------------------------------------------------------------- subject


def test_refuses_subject_that_is_not_the_ecp_subject(world):
    ack = _ack(world["permit_sha"], subject_id="ECP-someone-elses-subject")
    _expect_refusal(ack, "SBL_E_ACK_SUBJECT_MISMATCH")


def test_refuses_when_no_ecp_is_supplied(world):
    _expect_refusal(_ack(world["permit_sha"]), "SBL_E_ACK_ECP_MISSING", ecp=None)


def test_refuses_when_ecp_declares_no_subject(world):
    _expect_refusal(
        _ack(world["permit_sha"]), "SBL_E_ACK_ECP_MISSING", ecp={"scope": list(SCOPE)}
    )


# --------------------------------------------------------------------------- scope


def test_refuses_scope_that_appears_nowhere(world):
    ack = _ack(world["permit_sha"], scope="SCOPE-NEVER-DECLARED-ANYWHERE")
    _expect_refusal(ack, "SBL_E_ACK_SCOPE_MISMATCH")


def test_refuses_scope_that_is_a_superset_of_the_ecp_scope(world):
    ack = _ack(world["permit_sha"], scope=_scope_digest(SCOPE + ["sbl_core/errors.py"]))
    _expect_refusal(ack, "SBL_E_ACK_SCOPE_MISMATCH")


def test_refuses_when_ecp_declares_no_scope(world):
    _expect_refusal(
        _ack(world["permit_sha"]), "SBL_E_ACK_ECP_MISSING", ecp={"subject_id": SUBJECT}
    )


# --------------------------------------------------------------------------- permit


def test_refuses_permit_that_no_store_knows(world):
    ack = _ack(world["permit_sha"], permit_id="PERMIT-does-not-exist")
    _expect_refusal(ack, "SBL_E_ACK_PERMIT_UNKNOWN")


def test_refuses_when_no_permit_store_is_configured(world, monkeypatch):
    monkeypatch.delenv("SBL_SWOF_PERMIT_STORE", raising=False)
    _expect_refusal(_ack(world["permit_sha"]), "SBL_E_ACK_PERMIT_UNKNOWN", state="NO_PERMIT_STORE")


def test_refuses_permit_digest_mismatch(world):
    ack = _ack("0" * 64)
    _expect_refusal(ack, "SBL_E_ACK_PERMIT_MISMATCH", state="permit_sha256")


def test_refuses_permit_id_that_escapes_the_store(world):
    ack = _ack(world["permit_sha"], permit_id="../../etc/passwd")
    _expect_refusal(ack, "SBL_E_ACK_PERMIT_UNKNOWN")


def test_refuses_ack_that_outlives_its_permit(world, monkeypatch, tmp_path):
    store, permit_sha = _write_store(tmp_path / "short", _permit_doc(expires_at=_dt(300)))
    monkeypatch.setenv("SBL_SWOF_PERMIT_STORE", store)
    ack = _ack(permit_sha, expires_at=_dt(600))
    _expect_refusal(ack, "SBL_E_ACK_PERMIT_MISMATCH", state="ACK_OUTLIVES_PERMIT")


def test_refuses_expired_permit(world, monkeypatch, tmp_path):
    store, permit_sha = _write_store(
        tmp_path / "dead", _permit_doc(issued_at=_dt(-7200), expires_at=_dt(-60))
    )
    monkeypatch.setenv("SBL_SWOF_PERMIT_STORE", store)
    _expect_refusal(_ack(permit_sha), "SBL_E_ACK_PERMIT_MISMATCH", state="PERMIT_EXPIRED")


def test_refuses_permit_bound_to_another_subject(world, monkeypatch, tmp_path):
    store, permit_sha = _write_store(
        tmp_path / "other", _permit_doc(permit_id=PERMIT_ID, subject_id="ECP-other-subject")
    )
    monkeypatch.setenv("SBL_SWOF_PERMIT_STORE", store)
    _expect_refusal(
        _ack(permit_sha), "SBL_E_ACK_PERMIT_MISMATCH", state="PERMIT_BINDING_SUBJECT"
    )


def test_refuses_permit_bound_to_another_scope(world, monkeypatch, tmp_path):
    store, permit_sha = _write_store(
        tmp_path / "narrow", _permit_doc(scope=_scope_digest(["sbl_core/modes.py"]))
    )
    monkeypatch.setenv("SBL_SWOF_PERMIT_STORE", store)
    _expect_refusal(_ack(permit_sha), "SBL_E_ACK_PERMIT_MISMATCH", state="PERMIT_BINDING_SCOPE")


def test_refuses_permit_without_a_parseable_window(world, monkeypatch, tmp_path):
    doc = _permit_doc()
    del doc["expires_at"]
    store, permit_sha = _write_store(tmp_path / "nowindow", doc)
    monkeypatch.setenv("SBL_SWOF_PERMIT_STORE", store)
    _expect_refusal(
        _ack(permit_sha), "SBL_E_ACK_MALFORMED_FIELD", state="MALFORMED:permit.expires_at"
    )


# --------------------------------------------------------------------------- canonical form


@pytest.mark.parametrize(
    "field,value,state",
    [
        ("permit_sha256", "1" * 64, "SIGNATURE_MISMATCH"),
        ("scope", "1" * 64, "SIGNATURE_MISMATCH"),
        ("issued_at", _dt(-30), "SIGNATURE_MISMATCH"),
        ("expires_at", _dt(900), "SIGNATURE_MISMATCH"),
    ],
)
def test_signature_covers_each_newly_bound_field(world, field, value, state):
    """Each of these four fields is outside the pre-patch SBL-ACK@1 form, so the old gate
    accepted a mutated copy of a valid ACK (see evidence P0/P3/P5)."""

    ack = _ack(world["permit_sha"])
    ack[field] = value  # same signature, different claim
    _expect_refusal(ack, "SBL_E_REQUIRES_NATIVE_ACK", state=state)


@pytest.mark.parametrize(
    "field,value,state",
    [
        ("issuer", "other-host", "ISSUER_NOT_TRUSTED"),
        ("permit_id", "PERMIT-other", "SIGNATURE_MISMATCH"),
        ("subject_id", "ECP-other", "SIGNATURE_MISMATCH"),
    ],
)
def test_signature_already_covered_identity_fields_before_this_patch(world, field, value, state):
    """Regression only: these three were inside the SBL-ACK@1 form already and still are.
    Unlike the rest of this file, these cases pass on the pre-patch gate as well."""

    ack = _ack(world["permit_sha"])
    ack[field] = value
    _expect_refusal(ack, "SBL_E_REQUIRES_NATIVE_ACK", state=state)


def test_one_signature_cannot_be_reused_for_another_scope(world):
    """Pre-patch a single signature authorised any scope (P0 and P3 shared it)."""

    ack = _ack(world["permit_sha"])
    signature = ack["signature"]
    for scope in (_scope_digest(["sbl_core/modes.py"]), "SCOPE-NEVER-DECLARED-ANYWHERE"):
        ack["scope"] = scope
        _expect_refusal(dict(ack), "SBL_E_REQUIRES_NATIVE_ACK", state="SIGNATURE_MISMATCH")
    assert signature != _sign(ack)


def test_hostile_signature_encoding_is_refused_not_crashed(world):
    """A non-ASCII signature used to raise TypeError out of the constant-time compare."""

    ack = _ack(world["permit_sha"])
    ack["signature"] = "ünicode-signature"
    _expect_refusal(ack, "SBL_E_REQUIRES_NATIVE_ACK", state="SIGNATURE_MISMATCH")


def test_canonical_material_is_length_prefixed_not_joined(world):
    material = modes.ack_canonical_v2("issuer", "a\x1fB", "C", "", "", "", "")
    assert isinstance(material, bytes)
    assert material.startswith(b"9:SBL-ACK@2")
    assert b"3:a\x1fB" in material


# --------------------------------------------------------------------------- legacy mode


def _legacy_ack() -> dict:
    ack = {"issuer": ISSUER, "permit_id": PERMIT_ID, "subject_id": SUBJECT}
    ack["signature"] = modes.ack_signature(ISSUER, PERMIT_ID, SUBJECT, KEY)
    return ack


def test_legacy_four_field_ack_is_refused_by_default(world):
    """A pre-patch ACK carries none of the four signed fields, so the strict path refuses it."""

    _expect_refusal(_legacy_ack(), "SBL_E_ACK_MISSING_FIELD", state="MISSING:permit_sha256")


@pytest.mark.parametrize("value", ["", "0", "true", "yes", "TRUE", " 1"])
def test_legacy_mode_cannot_be_selected_by_a_near_miss_value(world, monkeypatch, value):
    monkeypatch.setenv("SBL_SWOF_ACK_LEGACY", value)
    _expect_refusal(_legacy_ack(), "SBL_E_ACK_MISSING_FIELD", state="MISSING:permit_sha256")


def test_legacy_mode_only_on_exact_flag_and_says_so(world, monkeypatch):
    monkeypatch.setenv("SBL_SWOF_ACK_LEGACY", "1")
    decision = modes.ModeGate("SWOF_CONNECTED", native_ack=_legacy_ack()).decide("repo.write")
    assert decision.allowed is True
    assert decision.reason == "NATIVE_ACK_VERIFIED_LEGACY_UNBOUND"
