"""POS/NEG for the repo-bound REPOSITORY_WRITE instance (OWNER control pack v1.1 section 2 A).

Every test answers a question the r3 contract could not answer: *which* repository, at *which*
head, with *which* exact write set. The positive case is deliberately weak — a resolved instance
means the request matches a description, never that the request may run.

Two placement facts are pinned as tests rather than assumed:
  * the resolver lives in ``integrations/pipd/tools/`` because ``OriginalPipd`` pins every
    ``src/pipd_ls_sp/*.py``; a new module inside that package would change the pin set and
    refuse every existing reader, so adding a file there is a contract act;
  * ``ECP.intent.schema.json`` closes ``details`` with ``additionalProperties: false``, so the
    instance identity cannot be smuggled into an intent. The gate runs where the write is about
    to happen, or the schema has to be re-ratified — those are the only two options.

Run with ``python -m pytest tests/test_operation_instance_r4.py`` or standalone.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
PIPD = HERE.parents[1]
SRC = PIPD / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipd_ls_sp import operation_registry as oreg  # noqa: E402
from pipd_ls_sp import pre_v2_adapter as pva  # noqa: E402

_TOOLS = PIPD / "tools" / "operation_instance.py"
_spec = importlib.util.spec_from_file_location("wp06_operation_instance", _TOOLS)
assert _spec is not None and _spec.loader is not None, "cannot load %s" % _TOOLS
oi = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = oi
_spec.loader.exec_module(oi)

CONTRACT = PIPD / "contracts" / "operation-registry.pre-v2-r3.json"
SIDECAR = PIPD / "contracts" / "operation-registry.pre-v2-r3.owner.sig.json"
INSTANCE = "OP-WP06-FHSVNEXT-ADD-01"

WS1 = "adapters/hgk_admission/admission_ref.py"
WS2 = "tests/affected/W1/test_hgk_admission_ref.py"
WS1_SHA = "21ee790faebc5cbe62b7033bfdf253bd17d26e2f1ddd5f00b10bc2d80079b52c"
WS2_SHA = "110f081659a14c12380cfe0252e5c0d2a2ecc316f81384640ed388bcb1e3e1a8"
CLEAN = pathlib.Path(r"C:/Projects/Agent_Workspace/FHS_NEXT_Workspace/"
                     r"FHS_W0W1_WP06_MIN_AUTH_v1_R4_20261117T2231/staging/fhs_vnext_clean")

#: the scope the r3 signature (window WIN-f3452453f719, 2026-11-03) actually covered
R3_SIGNED_SCOPE = ["src/demo/billing.py", "tests/test_billing.py"]


def contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def repo_state() -> dict:
    """The shape ``pre_v2_adapter.probe_repo`` returns for this write scope."""
    return {
        "root": "C:/staging/fhs_vnext",
        "head": "27abc69b21f66cbf345fc799263d7ed83e34b7cf",
        "branch": "HEAD",
        "dirty": False,
        "status_sha256": "0" * 64,
        "tracked": 989,
        "untracked": 0,
        "untracked_files": [],
        "write_scope": [WS1, WS2],
        "preimages": {WS1: "ABSENT", WS2: "ABSENT"},
        "process_writable": True,
        "repo_id": 1457756751,
        "full_name": "shw097-team/FHS_vNEXT",
    }


def refusal(fn) -> str:
    try:
        fn()
    except oi.InstanceRefused as exc:
        return exc.code
    return "NO_REFUSAL"


# ------------------------------------------------------------------ what the change may not do

def test_candidate_passes_the_existing_validator_unchanged():
    """No loader change is required: r3's validate() accepts the instance-bearing contract."""
    body = contract()
    oreg.validate(body)
    assert body["authority_state"] == "SOURCE_BOUND_OWNER_UNVERIFIED"


def test_candidate_does_not_add_or_rename_any_operation():
    body = contract()
    assert [r["operation_type"] for r in body["operations"]] == \
        ["SOURCE_READ", "LOCAL_DRAFT_WRITE", "REPOSITORY_WRITE"]
    assert [r["effect_class"] for r in body["operations"]] == \
        ["SOURCE_READ", "LOCAL_DRAFT_WRITE", "REPOSITORY_WRITE"]


def test_demo_scope_is_not_widened():
    assert contract()["operation_scopes"] == {
        "SOURCE_READ": ["src/demo/billing.py", "tests/test_billing.py"],
        "LOCAL_DRAFT_WRITE": ["src/demo/billing.py"],
        "REPOSITORY_WRITE": ["src/demo/billing.py"],
    }


def test_effect_lookup_still_returns_the_same_effect_for_the_demo_row():
    assert oreg.effect_for_operation(contract(), "REPOSITORY_WRITE") == "REPOSITORY_WRITE"


def test_resolver_is_outside_the_pinned_reader_surface():
    """A module inside src/pipd_ls_sp would change ORIGINAL_READER_PIN_SET for every reader."""
    pinned = {p.name for p in (SRC / "pipd_ls_sp").glob("*.py")}
    assert "operation_instance.py" not in pinned
    assert _TOOLS.is_file()


def test_ecp_intent_schema_is_closed_to_the_instance_identity():
    """Pins the measured constraint: details has additionalProperties false."""
    schema = json.loads((SRC / "pipd_ls_sp" / "schemas" / "pre-v2" / "ECP.intent.schema.json")
                        .read_text(encoding="utf-8"))
    details_schemas = [variant["properties"]["details"] for variant in schema["oneOf"]]
    assert all(d.get("additionalProperties") is False for d in details_schemas)
    assert all("operation_instance" not in (d.get("properties") or {}) for d in details_schemas)


# ------------------------------------------------------------------ POS

def test_pos_instance_resolves_only_when_repo_head_and_write_set_all_match():
    out = oi.evaluate(contract(), INSTANCE, repo_state(), observed={WS1: WS1_SHA, WS2: WS2_SHA})
    assert out["instance_id"] == INSTANCE
    assert out["effect_class"] == "REPOSITORY_WRITE"
    assert out["effect_state"] == "EFFECT_UNBOUND"
    assert out["grant_state"] == "NOT_GRANTED"
    assert out["admitted"] is False
    assert out["registry_authority"] == "SOURCE_BOUND_OWNER_UNVERIFIED"
    assert [w["relpath"] for w in out["write_set"]] == [WS1, WS2]


def test_pos_instance_digest_is_stable():
    assert oi.instance_digest(contract(), INSTANCE) == oi.instance_digest(contract(), INSTANCE)


# ------------------------------------------------------------------ NEG

def test_neg_unknown_instance_is_refused():
    assert refusal(lambda: oi.evaluate(contract(), "OP-WP06-NOT-A-REAL-INSTANCE", repo_state())) == \
        "INSTANCE_UNKNOWN"


def test_neg_other_repository_is_refused():
    st = repo_state()
    st["repo_id"] = 1457756752
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_REPO_IDENTITY_MISMATCH"


def test_neg_other_repository_name_is_refused():
    st = repo_state()
    st["full_name"] = "shw097-team/HG-KSEOS"
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_REPO_IDENTITY_MISMATCH"


def test_neg_head_drift_is_refused_not_rebound_silently():
    st = repo_state()
    st["head"] = "0" * 40
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_HEAD_DRIFT"


def test_neg_extra_scope_is_refused():
    st = repo_state()
    st["write_scope"] = [WS1, WS2, "src/demo/billing.py"]
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_SCOPE_NOT_EXACT"


def test_neg_subset_scope_is_refused():
    st = repo_state()
    st["write_scope"] = [WS1]
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_SCOPE_NOT_EXACT"


def test_neg_existing_file_is_not_overwritten():
    st = repo_state()
    st["preimages"] = {WS1: "0" * 64, WS2: "ABSENT"}
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_PREIMAGE_NOT_ABSENT"


def test_neg_dirty_worktree_is_refused():
    st = repo_state()
    st["dirty"] = True
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_WORKTREE_NOT_CLEAN"


def test_neg_untracked_file_outside_scope_is_refused():
    st = repo_state()
    st["untracked_files"] = ["notes.txt"]
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, st)) == "INSTANCE_WORKTREE_NOT_CLEAN"


def test_neg_postimage_that_is_not_the_declared_bytes_is_refused():
    bad = {WS1: "0" * 64, WS2: WS2_SHA}
    assert refusal(lambda: oi.evaluate(contract(), INSTANCE, repo_state(), observed=bad)) == \
        "INSTANCE_CONTRACT_INCOMPLETE"


def test_neg_instance_inside_the_demo_scope_is_refused():
    body = copy.deepcopy(contract())
    body["operation_instances"][0]["write_set"][0]["relpath"] = "src/demo/billing.py"
    st = repo_state()
    st["write_scope"] = ["src/demo/billing.py", WS2]
    st["preimages"] = {"src/demo/billing.py": "ABSENT", WS2: "ABSENT"}
    assert refusal(lambda: oi.evaluate(body, INSTANCE, st)) == "INSTANCE_DEMO_SCOPE_OVERLAP"


def test_neg_incomplete_instance_row_is_refused():
    body = copy.deepcopy(contract())
    del body["operation_instances"][0]["repo"]["head_at_bind"]
    assert refusal(lambda: oi.evaluate(body, INSTANCE, repo_state())) == "INSTANCE_CONTRACT_INCOMPLETE"


# ------------------------------------------------------------------ scope parity

def test_neg_the_historical_r3_signature_does_not_cover_these_paths():
    """The decisive negative for the previous state: the r3 signed scope named the demo paths."""
    ok, missing = oi.ratified_scope_covers(contract(), INSTANCE, R3_SIGNED_SCOPE)
    assert ok is False
    assert missing == [WS1, WS2]


def test_pos_parity_passes_only_when_the_signed_scope_names_both_paths():
    ok, missing = oi.ratified_scope_covers(contract(), INSTANCE, [WS1, WS2])
    assert ok is True and missing == []


def test_current_sidecar_payload_scope_matches_the_instance_when_it_is_the_r4_signature():
    sidecar = json.loads(SIDECAR.read_text(encoding="utf-8"))
    payload = json.loads(sidecar["payload_json"])
    contract_sha = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if sidecar.get("contract_sha256") != contract_sha:
        return "SKIP sidecar belongs to another contract revision"
    ok, missing = oi.ratified_scope_covers(contract(), INSTANCE, payload["scope"])
    assert ok is True and missing == []
    assert payload["claim_ceiling"] == "DESIGN_ONLY"


# ------------------------------------------------------------------ live repository observation

def test_pos_against_the_real_clean_worktree_when_present():
    if not CLEAN.is_dir():
        return "SKIP no staging worktree"
    binding = pva.probe_repo(str(CLEAN), [WS1, WS2])
    pva.require_current(binding)
    st = dict(binding["repo"])
    st.update({"repo_id": 1457756751, "full_name": "shw097-team/FHS_vNEXT"})
    out = oi.evaluate(contract(), INSTANCE, st, observed={WS1: WS1_SHA, WS2: WS2_SHA})
    assert out["admitted"] is False
    assert st["preimages"] == {WS1: "ABSENT", WS2: "ABSENT"}
    assert st["head"] == "27abc69b21f66cbf345fc799263d7ed83e34b7cf"


def _run_standalone() -> int:
    tests = [(n, o) for n, o in sorted(globals().items()) if n.startswith("test_")]
    failures = []
    for name, fn in tests:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            failures.append((name, "%s: %s" % (type(exc).__name__, exc)))
        else:
            print("PASS %s" % name)
    print("\n%d/%d passed" % (len(tests) - len(failures), len(tests)))
    for name, why in failures:
        print("FAIL %s -> %s" % (name, why))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run_standalone())
