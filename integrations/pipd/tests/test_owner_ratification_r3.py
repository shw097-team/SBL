"""Owner ratification verification: a valid signature passes, tampering does not.

The tool is exercised as a subprocess against a temporary tree signed by a
throwaway key, so nothing here touches the real owner key or the real contract.
Skipped when `cryptography` is unavailable, because the tool fails closed then.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("cryptography")

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "verify_owner_ratification.py"
CONTRACT = ROOT / "contracts" / "operation-registry.pre-v2-r3.json"


def canon(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def build(tmp: Path, *, tamper_payload: bool = False, wrong_key: bool = False) -> Path:
    contracts = tmp / "contracts"
    tools = tmp / "tools"
    contracts.mkdir(parents=True)
    tools.mkdir(parents=True)
    shutil.copy2(TOOL, tools / TOOL.name)
    shutil.copy2(CONTRACT, contracts / CONTRACT.name)

    key = Ed25519PrivateKey.generate()
    other = Ed25519PrivateKey.generate()
    public_hex = (other if wrong_key else key).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()
    (contracts / "owner-enrollment.json").write_text(
        json.dumps(
            {
                "schema": "SBL.PRE_V2.OWNER_ENROLLMENT@1",
                "owner_public_hex": public_hex,
                "owner_fingerprint": "test",
            }
        ).replace("\r\n", "\n"),
        encoding="utf-8",
    )
    body = {
        "schema": "SBL.PRE_V2.OWNER_RATIFICATION@1",
        "decision": "RATIFY_OPERATION_EFFECT_BINDING",
        "contract_id": "SBL-PRE-V2-OPERATION-EFFECT-2026-11-03-r3",
        "contract_sha256": hashlib.sha256((contracts / CONTRACT.name).read_bytes()).hexdigest(),
        "operations": ["SOURCE_READ", "LOCAL_DRAFT_WRITE", "REPOSITORY_WRITE"],
        "claim_ceiling": "DESIGN_ONLY",
    }
    payload = canon(body)
    signature = key.sign(payload).hex()
    stored_payload = payload
    if tamper_payload:
        body["operations"] = ["SOURCE_READ"]
        stored_payload = canon(body)  # digest recomputed, signature no longer matches
    (contracts / "operation-registry.pre-v2-r3.owner.sig.json").write_text(
        json.dumps(
            {
                "schema": "SBL.PRE_V2.OWNER_RATIFICATION@1",
                "contract_id": body["contract_id"],
                "contract_sha256": body["contract_sha256"],
                "payload_sha256": hashlib.sha256(stored_payload).hexdigest(),
                "payload_json": stored_payload.decode(),
                "signature_hex": signature,
                "window_id": "WIN-test",
            }
        ).replace("\r\n", "\n"),
        encoding="utf-8",
    )
    return tmp


def run(tmp: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(tmp / "tools" / TOOL.name)], capture_output=True, text=True, timeout=60
    )
    return proc.returncode, json.loads(proc.stdout or "{}")


def test_pos_signature_verifies(tmp_path: Path) -> None:
    code, out = run(build(tmp_path))
    assert code == 0 and out["verified"] is True, out
    assert out["authority"] == "SOURCE_BOUND_OWNER_RATIFIED"
    assert out["grant_state"] == "NOT_GRANTED"
    assert out["claim_ceiling"] == "DESIGN_ONLY"


def test_neg_tampered_payload_rejected(tmp_path: Path) -> None:
    code, out = run(build(tmp_path, tamper_payload=True))
    assert code == 1 and out["verified"] is False
    assert out["first_fail"] == "SIGNATURE_INVALID"


def test_neg_wrong_owner_key_rejected(tmp_path: Path) -> None:
    code, out = run(build(tmp_path, wrong_key=True))
    assert code == 1 and out["verified"] is False
    assert out["first_fail"] == "SIGNATURE_INVALID"


def test_neg_contract_changed_after_signing(tmp_path: Path) -> None:
    tmp = build(tmp_path)
    contract = tmp / "contracts" / CONTRACT.name
    contract.write_bytes(contract.read_bytes().replace(b'"r3.1"', b'"r3.9"'))
    code, out = run(tmp)
    assert code == 1 and out["first_fail"] == "CONTRACT_SHA_MISMATCH"
