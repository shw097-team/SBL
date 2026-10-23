"""C05/M1: the principal-separation clause must actually refuse, not merely name a second identity.

Each test is a negative case the external acceptance officer named as the reason for NOT_ESTABLISHED. The positive
case proves the checker admits a genuinely separated pair, on one frozen subject, with pinned registry bytes.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone

import pytest

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "tools", "check_principal_separation.py")
FAB = r"C:/Projects/Agent_Workspace/Fabric/FABRIC"
REGISTRY = os.path.join(FAB, "assurance", "principals.json")
PIN = os.path.join(FAB, "assurance", "principals.pinned.sha256")


def _load_tool():
    spec = importlib.util.spec_from_file_location("cps", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def tool():
    return _load_tool()


@pytest.fixture()
def registry(tool):
    return tool.load(REGISTRY)


SUBJECT = {"candidate_sha256": "a" * 64, "environment_sha256": "b" * 64, "abi_sha256": "c" * 64}


def verdict(producer="hermes", checker="VERIFY lane", grants=("G-ORCH-MAKER-01", "G-VERIFY-CHECKER-01")):
    return {"verdict_id": "V-TEST-1", "producer_identity": [producer],
            "independent_checker_identity": checker, "subject": dict(SUBJECT),
            "grant_ids": list(grants)}


def run(tool, v, reg=None):
    reg = reg if reg is not None else tool.load(REGISTRY)
    return tool.check_verdict(v, reg=reg, at=datetime(2026, 10, 23, tzinfo=timezone.utc),
                              registry=REGISTRY, pin=PIN)


def test_separated_pair_is_admissible(tool):
    res = run(tool, verdict())
    assert res["result"] == "IDENTITY_SEPARATION_ADMISSIBLE"
    assert res["acceptance_effect"] is None
    assert "distinct and attested" in res["claim_ceiling"]


def test_same_principal_is_inadmissible(tool):
    res = run(tool, verdict(producer="hermes", checker="hermes"))
    assert res["result"] == "INADMISSIBLE"
    assert res["acceptance_effect"] == "NOT_ESTABLISHED"


def test_alias_of_the_same_controller_is_inadmissible(tool):
    """'SBL-Commander session' and 'hermes' are aliases of one controller; a second name is not a second principal."""
    res = run(tool, verdict(producer="hermes", checker="SBL-Commander session"))
    assert res["result"] == "INADMISSIBLE"
    assert any(p["id"] == "P3_distinct_controller" and not p["ok"] for p in res["predicates"])


def test_model_name_is_not_a_principal(tool):
    res = run(tool, verdict(producer="hermes", checker="deepseek-v4.1-flash"))
    assert res["result"] == "INADMISSIBLE"


def test_missing_principal_record_fails_closed(tool):
    res = run(tool, verdict(checker="someone-unregistered"))
    assert res["result"] == "INADMISSIBLE"
    assert any(p["id"] == "P2_identity_resolved" and not p["ok"] for p in res["predicates"])


def test_checker_delegated_from_producer_is_inadmissible(tool, registry):
    reg = copy.deepcopy(registry)
    reg["grants"].append({"grant_id": "G-BAD-DELEGATION", "principal_id": "P-CODEX-VERIFY", "role": "final_checker",
                          "authority_principal_id": "P-HERMES-ORCH", "delegation_parent_grant_id": "G-ORCH-MAKER-01",
                          "valid_from": "2026-10-23T00:00:00Z", "expires_at": "2027-10-23T00:00:00Z", "revoked": False})
    res = run(tool, verdict(grants=("G-BAD-DELEGATION",)), reg=reg)
    assert res["result"] == "INADMISSIBLE"
    assert any(p["id"] == "P5_grant_bound_and_clean" and not p["ok"] for p in res["predicates"])


def test_subject_must_be_the_frozen_one(tool):
    res = run(tool, {"verdict_id": "V-TEST-1", "producer_identity": ["hermes"],
                     "independent_checker_identity": "VERIFY lane",
                     "subject": {"candidate_sha256": "not-64-hex"},
                     "grant_ids": ["G-ORCH-MAKER-01", "G-VERIFY-CHECKER-01"]})
    assert res["result"] == "INADMISSIBLE"
    assert any(p["id"] == "P0_subject_bound" and not p["ok"] for p in res["predicates"])


def test_expired_grant_is_inadmissible(tool, registry):
    reg = copy.deepcopy(registry)
    for g in reg["grants"]:
        if g["grant_id"] == "G-VERIFY-CHECKER-01":
            g["expires_at"] = "2020-01-01T00:00:00Z"
    res = run(tool, verdict(), reg=reg)
    assert res["result"] == "INADMISSIBLE"


def test_registry_bytes_must_match_the_pin(tool, tmp_path):
    reg = tool.load(REGISTRY)
    altered = copy.deepcopy(reg)
    altered["principals"][0]["controller_id"] = "C-DIFFERENT"
    target = tmp_path / "principals.json"
    target.write_text(json.dumps(altered), encoding="utf-8")
    res = tool.check_verdict(verdict(), reg=altered, at=datetime(2026, 10, 23, tzinfo=timezone.utc),
                             registry=str(target), pin=PIN)
    assert res["result"] == "INADMISSIBLE"
    assert any(p["id"] == "P1_registry_pinned" and not p["ok"] for p in res["predicates"])


def test_no_checker_grant_means_inadmissible(tool):
    res = run(tool, verdict(grants=("G-ORCH-MAKER-01",)))
    assert res["result"] == "INADMISSIBLE"


def test_stale_attestation_is_inadmissible(tool, registry):
    reg = copy.deepcopy(registry)
    for p in reg["principals"]:
        p["attestation"]["expires_at"] = "2020-01-01T00:00:00Z"
    res = run(tool, verdict(), reg=reg)
    assert res["result"] == "INADMISSIBLE"


def test_kb_canonical_field_binds_to_the_same_principal(tool):
    """DOC-07#3394 names the canonical field independent_checker_ref; two spellings must not resolve differently."""
    v = verdict()
    v["independent_checker_ref"] = "VERIFY lane"
    assert run(tool, v)["result"] == "IDENTITY_SEPARATION_ADMISSIBLE"
    v2 = verdict()
    v2["independent_checker_ref"] = "hermes"
    res = run(tool, v2)
    assert res["result"] == "INADMISSIBLE"


def test_missing_subject_is_inadmissible(tool):
    v = verdict()
    v.pop("subject")
    assert run(tool, v)["result"] == "INADMISSIBLE"


def test_dangling_delegation_parent_is_a_broken_chain(tool, registry):
    import copy
    reg = copy.deepcopy(registry)
    for g in reg["grants"]:
        if g["grant_id"] == "G-VERIFY-CHECKER-01":
            g["delegation_parent_grant_id"] = "G-DOES-NOT-EXIST"
            g["authority_principal_id"] = "P-HERMES-ORCH"
    res = run(tool, verdict(grants=("G-VERIFY-CHECKER-01",)), reg=reg)
    assert res["result"] == "INADMISSIBLE"


def test_two_principals_sharing_a_controller_are_one_actor(tool, registry):
    import copy
    reg = copy.deepcopy(registry)
    for p in reg["principals"]:
        if p["principal_id"] == "P-CODEX-VERIFY":
            p["controller_id"] = "C-RUNTIME-HERMES"
    res = run(tool, verdict(), reg=reg)
    assert res["result"] == "INADMISSIBLE"
    assert any(x["id"] == "P3_distinct_controller" and not x["ok"] for x in res["predicates"])


def test_failure_carries_its_own_ceiling(tool):
    res = run(tool, verdict(producer="hermes", checker="hermes"))
    assert res["failure_ceiling"] == "NO_IDENTITY_SEPARATION_ESTABLISHED__ACCEPTANCE_NOT_ESTABLISHED"
    assert res["kb_basis"]
