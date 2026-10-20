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
    """V15-MODE-01: typed-but-unverified strings used to be accepted as a native authorisation."""

    monkeypatch.setenv("SBL_SWOF_ACK_ISSUERS", "native-host")
    monkeypatch.setenv("SBL_SWOF_ACK_KEY", "k" * 32)
    with pytest.raises(SBLError) as caught:
        ModeGate("SWOF_CONNECTED", native_ack=_ack()).decide("net.call")
    assert caught.value.code == "SBL_E_REQUIRES_NATIVE_ACK"
    assert caught.value.detail.get("state") == "SIGNATURE_MISMATCH"


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
    """The refusal must not be blanket: a correctly signed ACK from a trusted issuer still allows."""

    key = "k" * 32
    monkeypatch.setenv("SBL_SWOF_ACK_ISSUERS", "native-host,other-host")
    monkeypatch.setenv("SBL_SWOF_ACK_KEY", key)
    ack = _ack(signature=modes.ack_signature("native-host", "P-1", "S-1", key))
    decision = ModeGate("SWOF_CONNECTED", native_ack=ack).decide("net.call")
    assert decision.allowed is True
    assert decision.no_effect is False
    assert decision.reason == "NATIVE_ACK_VERIFIED"


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
