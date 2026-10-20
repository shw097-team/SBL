"""Slice B1: specialised principals cannot exceed their manifests."""

from __future__ import annotations

import pytest

from sbl_core.errors import SBLError
from sbl_sp import assert_permission, load_manifest, sign_verdict


def test_loads_all_three_manifests() -> None:
    tpm = load_manifest("tpm_sp")
    commander = load_manifest("commander_sp")
    challenger = load_manifest("external_challenge_sp")

    assert tpm["schema"] == "SBL-SP-MANIFEST/1"
    assert tpm["role"] == "product-manager"
    assert commander["role"] == "build-commander"
    assert challenger["role"] == "independent-challenger"
    assert challenger["read_only"] is True
    assert "challenge.sign" in challenger["permissions"]


def test_unknown_sp_is_refused() -> None:
    with pytest.raises(SBLError) as excinfo:
        load_manifest("ghost_sp")
    assert excinfo.value.code == "SBL_E_UNKNOWN_SP"

    with pytest.raises(SBLError) as excinfo:
        assert_permission("ghost_sp", "goal.read")
    assert excinfo.value.code == "SBL_E_UNKNOWN_SP"


def test_path_traversal_in_sp_id_is_refused() -> None:
    for sp_id in ("../manifests/tpm_sp", "..\\tpm_sp", "manifests/tpm_sp"):
        with pytest.raises(SBLError) as excinfo:
            load_manifest(sp_id)
        assert excinfo.value.code == "SBL_E_UNKNOWN_SP"


def test_tpm_cannot_write_product() -> None:
    with pytest.raises(SBLError) as excinfo:
        assert_permission("tpm_sp", "product.write")
    assert excinfo.value.code == "SBL_E_PERMISSION_DENIED"
    assert excinfo.value.detail == {"sp_id": "tpm_sp", "action": "product.write"}


def test_commander_cannot_sign_challenge() -> None:
    with pytest.raises(SBLError) as excinfo:
        assert_permission("commander_sp", "challenge.sign")
    assert excinfo.value.code == "SBL_E_PERMISSION_DENIED"

    with pytest.raises(SBLError) as excinfo:
        sign_verdict("commander_sp", "tpm_sp", {"ok": True})
    assert excinfo.value.code == "SBL_E_PERMISSION_DENIED"


def test_maker_cannot_sign_own_verdict() -> None:
    with pytest.raises(SBLError) as excinfo:
        sign_verdict("external_challenge_sp", " External_Challenge_SP ", {"ok": True})
    assert excinfo.value.code == "SBL_E_SELF_CHECK_FORBIDDEN"


def test_distinct_principal_signs_verdict() -> None:
    verdict = {"schema": "SBL-VERDICT/1", "pass": True}
    signed = sign_verdict("external_challenge_sp", "commander_sp", verdict)

    assert signed["schema"] == "SBL-CHALLENGE-VERDICT/1"
    assert signed["principal"] == "external_challenge_sp"
    assert signed["maker"] == "commander_sp"
    assert signed["verdict"] == verdict
    assert signed["signature"].startswith("SIG-")
    assert len(signed["signature"]) == len("SIG-") + 16
    assert sign_verdict("external_challenge_sp", "commander_sp", verdict) == signed


def test_permitted_action_returns_none() -> None:
    assert assert_permission("tpm_sp", "spec.write") is None
    assert assert_permission("external_challenge_sp", "challenge.sign") is None
