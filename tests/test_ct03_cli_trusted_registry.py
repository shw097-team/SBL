"""CT-03: the shipped CLI must not accept a caller-supplied effect registry.

POS: the committed canonical contract loads and the owner's Ed25519 ratification verifies.
NEG: a caller-supplied registry, a mismatched sha, a tampered signature and a tampered
contract are refused *before* any ECP is written, with a typed code and exit 2.

The CLI refusals are exercised as a subprocess so the test sees the real exit code and the
machine-readable envelope, which is what a downstream consumer reacts to.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "integrations" / "pipd" / "src"
CONTRACTS = ROOT / "integrations" / "pipd" / "contracts"
CANONICAL = CONTRACTS / "operation-registry.pre-v2-r3.json"

sys.path.insert(0, str(SRC))

from pipd_ls_sp import operation_registry as reg  # noqa: E402


def cli(*args: str) -> tuple[int, dict]:
    # Capture bytes: the child may emit non-UTF-8 on a Windows console, and a decode error must
    # not be mistaken for the refusal this test is looking for.
    env = {**__import__("os").environ, "PYTHONPATH": str(SRC), "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, "-m", "pipd_ls_sp.cli", *args],
        capture_output=True, timeout=120, env=env, cwd=str(ROOT),
    )
    out = (proc.stdout or b"").decode("utf-8", "replace")
    err = (proc.stderr or b"").decode("utf-8", "replace")
    try:
        return proc.returncode, json.loads(out or "{}")
    except json.JSONDecodeError:
        return proc.returncode, {"raw": out[-400:], "stderr": err[-400:]}


def stub_bundle(tmp: Path) -> tuple[Path, Path, Path]:
    pd = tmp / "pd.json"
    pi = tmp / "pi.json"
    intent = tmp / "intent.json"
    for path in (pd, pi, intent):
        path.write_text("{}", encoding="utf-8")
    return pd, pi, intent


def test_pos_canonical_contract_is_owner_ratified() -> None:
    pytest.importorskip("cryptography")
    contract, sha, ratification = reg.load_trusted(ROOT)
    assert sha == "bedf8754284a15a877cea86e257c13871da98160a7ca70c7e8b779d80cf7a631"
    assert ratification["verified"] is True
    assert ratification["authority"] == reg.RATIFIED
    assert ratification["grant_state"] == "NOT_GRANTED"
    assert ratification["claim_ceiling"] == "DESIGN_ONLY"
    assert set(ratification["operations"]) == {"SOURCE_READ", "LOCAL_DRAFT_WRITE", "REPOSITORY_WRITE"}
    assert {row["operation_type"] for row in contract["operations"]} == set(ratification["operations"])


def test_neg_caller_supplied_registry_is_refused(tmp_path: Path) -> None:
    pd, pi, intent = stub_bundle(tmp_path)
    forged = tmp_path / "forged-registry.json"
    forged.write_text(json.dumps({"schema": "SBL.OperationRegistry.Binding@2"}), encoding="utf-8")
    code, out = cli("compile-ecp", "--pd", str(pd), "--pi", str(pi), "--effect-intent", str(intent),
                    "--operation-registry", str(forged), "--operation-registry-sha256", "0" * 64)
    assert code == 2, out
    assert out.get("code") == "REGISTRY_NOT_CANONICAL"


def test_neg_supplied_sha_must_match_the_contract(tmp_path: Path) -> None:
    pytest.importorskip("cryptography")
    pd, pi, intent = stub_bundle(tmp_path)
    code, out = cli("compile-ecp", "--pd", str(pd), "--pi", str(pi), "--effect-intent", str(intent),
                    "--operation-registry", str(CANONICAL), "--operation-registry-sha256", "f" * 64)
    assert code == 2, out
    assert out.get("code") == "REGISTRY_SHA_MISMATCH"


def test_neg_tampered_signature_is_refused(tmp_path: Path) -> None:
    pytest.importorskip("cryptography")
    repo = tmp_path / "repo"
    for rel in ("integrations/pipd/contracts/operation-registry.pre-v2-r3.json",
                "integrations/pipd/contracts/owner-enrollment.json",
                "integrations/pipd/contracts/operation-registry.pre-v2-r3.owner.sig.json"):
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / rel).read_bytes())
    sig = repo / "integrations/pipd/contracts/operation-registry.pre-v2-r3.owner.sig.json"
    body = json.loads(sig.read_text(encoding="utf-8"))
    body["signature_hex"] = ("00" * 64)
    sig.write_text(json.dumps(body), encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@e.invalid", "-c", "user.name=t", "commit", "-qm", "x"],
                   cwd=repo, check=True)
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.load_trusted(repo)
    assert str(exc.value) == "OWNER_SIGNATURE_INVALID"


def test_neg_changed_contract_breaks_the_ratification(tmp_path: Path) -> None:
    pytest.importorskip("cryptography")
    repo = tmp_path / "repo"
    for rel in ("integrations/pipd/contracts/operation-registry.pre-v2-r3.json",
                "integrations/pipd/contracts/owner-enrollment.json",
                "integrations/pipd/contracts/operation-registry.pre-v2-r3.owner.sig.json"):
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / rel).read_bytes())
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@e.invalid", "-c", "user.name=t", "commit", "-qm", "x"],
                   cwd=repo, check=True)
    contract = repo / "integrations/pipd/contracts/operation-registry.pre-v2-r3.json"
    contract.write_bytes(contract.read_bytes().replace(b'"r3.1"', b'"r3.9"'))
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@e.invalid", "-c", "user.name=t", "commit", "-qm", "y"],
                   cwd=repo, check=True)
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.load_trusted(repo)
    assert str(exc.value) == "SIGNED_CONTRACT_SHA_MISMATCH"


def test_neg_unknown_operation_still_refused() -> None:
    contract, _sha, _rat = reg.load_trusted(ROOT) if _has_crypto() else (None, None, None)
    if contract is None:
        pytest.skip("cryptography unavailable; load_trusted fails closed by design")
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.effect_for_operation(contract, "OP-NOT-IN-CONTRACT")
    assert str(exc.value) == "OPERATION_TYPE_UNKNOWN_OR_DUPLICATE"


def _has_crypto() -> bool:
    try:
        import cryptography  # noqa: F401
        return True
    except Exception:
        return False
