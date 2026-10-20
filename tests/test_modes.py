"""Slice A acceptance: 39 ModeGate matrix and mode decisions."""

from __future__ import annotations

import pytest

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


def test_swof_positive_with_complete_ack():
    ack = {
        "issuer": "native-host",
        "permit_id": "P-1",
        "subject_id": "S-1",
        "signature": "sig",
    }
    decision = ModeGate("SWOF_CONNECTED", native_ack=ack).decide("net.call")
    assert decision.allowed is True
    assert decision.no_effect is False


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
