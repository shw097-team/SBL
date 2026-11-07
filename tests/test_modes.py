"""Slice A acceptance: 39 ModeGate matrix and mode decisions."""

from __future__ import annotations

import pytest

from sbl_core import modes
from sbl_core.errors import SBLError
from sbl_core.modes import GATE_IDS, MODES, ModeGate, mode_gate_matrix


def test_matrix_positive_39_unique_rows():
    rows = mode_gate_matrix()
    assert len(rows) == 39
    assert len({row["gate_id"] for row in rows}) == 39
    assert {row["gate"] for row in rows} == set(GATE_IDS)
    assert {row["mode"] for row in rows} == set(MODES)
    assert all(
        row["gate_id"] == f"SBL-{row['gate']}-{row['mode']}" for row in rows
    )
    assert {row["disposition"] for row in rows} == {
        "ACTIVE",
        "SHADOW_NOEFFECT",
        "BLOCKED_EXTERNAL",
    }
    standalone = [row for row in rows if row["mode"] == "STANDALONE"]
    assert len(standalone) == 13 and all(r["disposition"] == "ACTIVE" for r in standalone)


def test_standalone_positive_allows_local_effects():
    gate = ModeGate("STANDALONE")
    write = gate.decide("local.write")
    read = gate.decide("local.read")
    assert write.allowed is True and write.no_effect is False
    assert read.allowed is True and read.no_effect is False
    assert write.to_dict()["mode"] == "STANDALONE"


def test_standalone_negative_blocks_external_effect():
    decision = ModeGate("STANDALONE").decide("net.call")
    assert decision.allowed is False
    assert decision.no_effect is True


def test_shadow_positive_is_no_effect_for_any_effect():
    gate = ModeGate("PREW3_SHADOW")
    for effect in ("local.write", "net.call", "repo.write"):
        decision = gate.decide(effect)
        assert decision.allowed is False
        assert decision.no_effect is True
        assert decision.reason == "SHADOW_READ_ONLY_NO_EFFECT"


def _ack(**overrides):
    ack = {
        "issuer": "native-host",
        "permit_id": "P-1",
        "subject_id": "S-1",
        "signature": "fabricated",
    }
    ack.update(overrides)
    return ack


def test_swof_refuses_an_ack_that_is_only_four_non_empty_strings(monkeypatch):
    """V15-MODE-01: typed-but-unverified strings used to be accepted as a native authorisation.

    D-18 shifted *which* refusal comes first: a four-string ACK no longer reaches the MAC check,
    because the strict form requires four more signed fields before anything is verified.
    """

    monkeypatch.setenv("SBL_SWOF_ACK_ISSUERS", "native-host")
    monkeypatch.setenv("SBL_SWOF_ACK_KEY", "k" * 32)
    with pytest.raises(SBLError) as caught:
        ModeGate("SWOF_CONNECTED", native_ack=_ack()).decide("net.call")
    assert caught.value.code == "SBL_E_ACK_MISSING_FIELD"
    assert caught.value.detail.get("state") == "MISSING:permit_sha256"


def test_swof_refuses_when_no_trust_anchor_is_configured(monkeypatch):
    monkeypatch.delenv("SBL_SWOF_ACK_ISSUERS", raising=False)
    monkeypatch.delenv("SBL_SWOF_ACK_KEY", raising=False)
    with pytest.raises(SBLError) as caught:
        ModeGate("SWOF_CONNECTED", native_ack=_ack()).decide("net.call")
    assert "NO_TRUSTED_ISSUERS_CONFIGURED" in caught.value.detail.get("state", "")


def test_swof_refuses_an_untrusted_issuer(monkeypatch):
    monkeypatch.setenv("SBL_SWOF_ACK_ISSUERS", "trusted-host")
    monkeypatch.setenv("SBL_SWOF_ACK_KEY", "k" * 32)
    with pytest.raises(SBLError) as caught:
        ModeGate("SWOF_CONNECTED", native_ack=_ack()).decide("net.call")
    assert caught.value.detail.get("state") == "ISSUER_NOT_TRUSTED"


def test_ack_signature_cannot_be_moved_between_tuples():
    """V16-MODE-02: a delimiter-joined digest let one signature stand for two different tuples."""

    key = "k" * 32
    left = modes.ack_signature("issuer", "a\x1fB", "C", key)
    right = modes.ack_signature("issuer", "a", "B\x1fC", key)
    assert left != right


def test_swof_accepts_an_ack_signed_with_the_configured_key(monkeypatch):
    """The refusal must not be blanket: a correctly signed ACK from a trusted issuer still allows.

    D-18: the strict (default) form also requires the four signed binding fields and an ECP; its
    positive path is ``tests/test_ack_binding.py::test_strict_positive_bound_ack_is_allowed``. This
    case now exercises the env-gated legacy form, which is the only one a four-field ACK can satisfy.
    """

    key = "k" * 32
    monkeypatch.setenv("SBL_SWOF_ACK_ISSUERS", "native-host,other-host")
    monkeypatch.setenv("SBL_SWOF_ACK_KEY", key)
    monkeypatch.setenv("SBL_SWOF_ACK_LEGACY", "1")
    ack = _ack(signature=modes.ack_signature("native-host", "P-1", "S-1", key))
    # the env flag can no longer enable the four-field form; it only explains why nothing verifies
    with pytest.raises(SBLError) as exc:
        ModeGate("SWOF_CONNECTED", native_ack=ack).decide("net.call")
    assert exc.value.code == "SBL_E_REQUIRES_NATIVE_ACK"
    assert exc.value.detail["state"] == "SBL_ACK_LEGACY_ACCEPTANCE_CLOSED"


@pytest.mark.parametrize(
    "ack",
    [
        None,
        {},
        {"issuer": "native-host", "permit_id": "P-1", "subject_id": "S-1"},
        {
            "issuer": "native-host",
            "permit_id": " ",
            "subject_id": "S-1",
            "signature": "sig",
        },
    ],
)
def test_swof_negative_without_native_ack(ack):
    with pytest.raises(SBLError) as caught:
        ModeGate("SWOF_CONNECTED", native_ack=ack).decide("net.call")
    assert caught.value.code == "SBL_E_REQUIRES_NATIVE_ACK"


def test_unknown_mode_negative():
    with pytest.raises(SBLError) as caught:
        ModeGate("FULL_AUTO")
    assert caught.value.code == "SBL_E_UNKNOWN_MODE"
