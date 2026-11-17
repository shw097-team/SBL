"""POS/NEG for the WP06 pre-write gate (OWNER H-15 amend items 1 and 2).

The gate is the only place where the signed instance is *consumed*. These tests hold it to the
owner's fail-closed list: identity independently resolved and never defaulted, postimages
mandatory, signed scope equal (not merely containing), head/tree/preimage/TTL/MaxOps bound, and
no stray path anywhere. The positive case runs against a real repository and the real signature;
nothing here fabricates an identity in place of the original reader.

Run with ``python -m pytest tests/test_wp06_prewrite_gate.py`` or standalone. A test that returns
the string "SKIP" is treated as a failure by the standalone runner: a silently skipped negative is
indistinguishable from a passing one, which is how a fake green gets made.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve()
PIPD = HERE.parents[1]
SRC = PIPD / "src"
for extra in (SRC, PIPD / "tools"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from pipd_ls_sp import operation_registry as oreg  # noqa: E402

_spec = importlib.util.spec_from_file_location("wp06_oi", PIPD / "tools" / "operation_instance.py")
assert _spec is not None and _spec.loader is not None
oi = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = oi
_spec.loader.exec_module(oi)

_gate_spec = importlib.util.spec_from_file_location("wp06_gate", PIPD / "tools" / "wp06_prewrite_gate.py")
assert _gate_spec is not None and _gate_spec.loader is not None
gate = importlib.util.module_from_spec(_gate_spec)
sys.modules[_gate_spec.name] = gate
_gate_spec.loader.exec_module(gate)

CONTRACT_PATH = PIPD / "contracts" / "operation-registry.pre-v2-r3.json"
SIDECAR_PATH = PIPD / "contracts" / "operation-registry.pre-v2-r3.owner.sig.json"
INSTANCE = "OP-WP06-FHSVNEXT-ADD-01"
WS1 = "adapters/hgk_admission/admission_ref.py"
WS2 = "tests/affected/W1/test_hgk_admission_ref.py"
WS1_SHA = "21ee790faebc5cbe62b7033bfdf253bd17d26e2f1ddd5f00b10bc2d80079b52c"
WS2_SHA = "110f081659a14c12380cfe0252e5c0d2a2ecc316f81384640ed388bcb1e3e1a8"
REPO = pathlib.Path(r"C:/Projects/Agent_Workspace/FHS_NEXT_Workspace/"
                    r"FHS_W0W1_WP06_MIN_AUTH_v1_R4_20261117T2231/staging/fhs_vnext")
HEAD = "27abc69b21f66cbf345fc799263d7ed83e34b7cf"
TREE = "14bb6ef11a041a08f4665595999ca278f02fa5ac"


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_bytes())


def signed_scope() -> list:
    return json.loads(json.loads(SIDECAR_PATH.read_text(encoding="utf-8"))["payload_json"])["scope"]


def contract_sha() -> str:
    return hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()


def state(**over) -> dict:
    base = {
        "head": HEAD, "tree": TREE, "write_scope": [WS1, WS2],
        "preimages": {WS1: "ABSENT", WS2: "ABSENT"},
        "repo_id": 1457756751, "full_name": "shw097-team/FHS_vNEXT",
    }
    base.update(over)
    return base


def observed(**over) -> dict:
    base = {WS1: WS1_SHA, WS2: WS2_SHA}
    base.update(over)
    return base


def write_call(**over):
    kwargs = dict(signed_contract_sha256=contract_sha(), contract_sha256=contract_sha(),
                  repo_state=state(), observed=observed(), changed_paths=[WS1, WS2],
                  signed_scope=signed_scope(), ttl_remaining_s=1000.0, ops_requested=1)
    kwargs.update(over)
    return oi.evaluate_write(contract(), INSTANCE, **kwargs)


def code(fn) -> str:
    try:
        fn()
    except oi.InstanceRefused as exc:
        return exc.code
    return "NO_REFUSAL"


# ------------------------------------------------------------------ identity

def test_pos_remote_url_forms_resolve_to_one_full_name():
    for url in ("https://github.com/shw097-team/FHS_vNEXT.git",
                "https://github.com/shw097-team/FHS_vNEXT",
                "git@github.com:shw097-team/FHS_vNEXT.git",
                "ssh://git@github.com/shw097-team/FHS_vNEXT.git"):
        assert oi.full_name_from_remote_url(url) == "shw097-team/FHS_vNEXT"


def test_neg_unparseable_or_empty_remote_is_refused_not_empty_stringed():
    for url in ("", "   ", "/local/path/repo", "file:///c/Projects/repo"):
        assert code(lambda u=url: oi.full_name_from_remote_url(u)) == \
            "INSTANCE_REPO_IDENTITY_UNRESOLVED"


def test_neg_missing_repo_identity_in_the_write_state_is_refused():
    st = state()
    st.pop("repo_id")
    assert code(lambda: write_call(repo_state=st)) == "INSTANCE_REPO_IDENTITY_MISSING"


def test_neg_missing_full_name_is_refused():
    st = state(full_name="")
    assert code(lambda: write_call(repo_state=st)) == "INSTANCE_REPO_IDENTITY_MISSING"


def test_neg_wrong_numeric_id_is_refused():
    assert code(lambda: write_call(repo_state=state(repo_id=1457756752))) == \
        "INSTANCE_REPO_IDENTITY_MISMATCH"


def test_neg_other_repository_name_is_refused():
    assert code(lambda: write_call(repo_state=state(full_name="shw097-team/HG-KSEOS"))) == \
        "INSTANCE_REPO_IDENTITY_MISMATCH"


# ------------------------------------------------------------------ the signed object

def test_neg_contract_sha_that_differs_from_the_signed_one_is_refused():
    assert code(lambda: write_call(contract_sha256="0" * 64)) == "INSTANCE_CONTRACT_SHA_MISMATCH"


def test_neg_signed_scope_with_an_extra_path_is_refused():
    assert code(lambda: write_call(signed_scope=signed_scope() + ["src/demo/billing.py"])) == \
        "INSTANCE_SCOPE_NOT_SIGNED"


def test_neg_signed_scope_missing_a_path_is_refused():
    assert code(lambda: write_call(signed_scope=[WS1])) == "INSTANCE_SCOPE_NOT_SIGNED"


def test_pos_signed_scope_equal_in_a_different_order_is_accepted():
    assert write_call(signed_scope=[WS2, WS1])["gate"] == "WRITE_GATE_PASSED_NOT_A_PERMIT"


# ------------------------------------------------------------------ head / tree / preimage

def test_neg_head_drift_is_refused():
    assert code(lambda: write_call(repo_state=state(head="0" * 40))) == "INSTANCE_HEAD_DRIFT"


def test_neg_tree_drift_is_refused():
    assert code(lambda: write_call(repo_state=state(tree="0" * 40))) == "INSTANCE_TREE_DRIFT"


def test_neg_preimage_that_already_exists_is_refused():
    assert code(lambda: write_call(repo_state=state(preimages={WS1: "0" * 64, WS2: "ABSENT"}))) == \
        "INSTANCE_PREIMAGE_NOT_ABSENT"


def test_neg_stray_changed_path_is_refused():
    assert code(lambda: write_call(changed_paths=[WS1, WS2, "README.md"])) == \
        "INSTANCE_PATHS_OUTSIDE_WRITESET"


# ------------------------------------------------------------------ postimages

def test_neg_missing_postimage_is_refused():
    obs = {WS1: WS1_SHA}
    assert code(lambda: write_call(observed=obs)) == "INSTANCE_POSTIMAGE_MISSING"


def test_neg_crlf_bytes_are_a_different_postimage():
    """The measured Windows trap: same text, CRLF, different digest, refused."""
    lf = b"line one\nline two\n"
    crlf = lf.replace(b"\n", b"\r\n")
    assert hashlib.sha256(lf).hexdigest() != hashlib.sha256(crlf).hexdigest()
    bogus = hashlib.sha256(crlf).hexdigest()
    assert code(lambda: write_call(observed=observed(**{WS1: bogus}))) == "INSTANCE_POSTIMAGE_MISMATCH"


def test_neg_wrong_postimage_for_the_second_file_is_refused():
    assert code(lambda: write_call(observed=observed(**{WS2: "0" * 64}))) == "INSTANCE_POSTIMAGE_MISMATCH"


# ------------------------------------------------------------------ contract shape / budget

def test_neg_over_long_relpath_is_refused_at_load():
    body = copy.deepcopy(contract())
    body["operation_instances"][0]["write_set"][0]["relpath"] = "a/" * 100 + "x.py"
    assert code(lambda: oi.find_instance(body, INSTANCE)) == "INSTANCE_PATH_TOO_LONG"


def test_neg_expired_ttl_is_refused():
    assert code(lambda: write_call(ttl_remaining_s=0.0)) == "INSTANCE_TTL_EXPIRED"


def test_neg_ttl_beyond_the_signed_ttl_is_refused():
    assert code(lambda: write_call(ttl_remaining_s=999999.0)) == "INSTANCE_TTL_EXPIRED"


def test_neg_absent_ttl_measurement_is_refused():
    assert code(lambda: write_call(ttl_remaining_s=None)) == "INSTANCE_TTL_EXPIRED"


def test_neg_more_ops_than_the_signed_max_is_refused():
    assert code(lambda: write_call(ops_requested=2)) == "INSTANCE_OPS_EXCEEDED"


def test_neg_demo_scope_overlap_is_refused():
    body = copy.deepcopy(contract())
    body["operation_instances"][0]["write_set"][0]["relpath"] = "src/demo/billing.py"
    try:
        oi.evaluate_write(body, INSTANCE, signed_contract_sha256=contract_sha(),
                          contract_sha256=contract_sha(),
                          repo_state=state(write_scope=["src/demo/billing.py", WS2],
                                           preimages={"src/demo/billing.py": "ABSENT", WS2: "ABSENT"}),
                          observed=observed(), changed_paths=[],
                          signed_scope=["src/demo/billing.py", WS2],
                          ttl_remaining_s=1000.0, ops_requested=1)
        raise AssertionError("expected a refusal")
    except Exception as exc:  # noqa: BLE001 - code is the stable contract, class identity is not
        assert getattr(exc, "code", None) == "INSTANCE_DEMO_SCOPE_OVERLAP", exc


# ------------------------------------------------------------------ the real repository

def test_pos_gate_passes_on_the_real_staged_write():
    """No fabrication: real clone, real remote, real signed sidecar, real staged bytes."""
    assert REPO.is_dir(), "the staging clone is required; a missing clone is a failure, not a skip"
    record = gate.run(REPO, INSTANCE)
    assert record["gate"] == "WRITE_GATE_PASSED_NOT_A_PERMIT"
    assert record["admitted"] is False
    assert record["grant_state"] == "NOT_GRANTED"
    assert record["repo"]["full_name"] == "shw097-team/FHS_vNEXT"
    assert record["preimages_at_head"] == {WS1: "ABSENT", WS2: "ABSENT"}
    assert record["observed_postimages"] == {WS1: WS1_SHA, WS2: WS2_SHA}
    assert record["signature"]["owner_fingerprint"] == "412b351937be72a1"


def test_neg_gate_refuses_a_repository_whose_remote_says_something_else():
    """A clone with a different origin must not be able to borrow this instance."""
    other = REPO.parent / "fhs_vnext_identity_probe"
    if other.exists():
        subprocess.run(["git", "-C", str(other), "remote", "set-url", "origin",
                        "https://github.com/shw097-team/HG-KSEOS.git"], capture_output=True)
    else:
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(REPO), str(other)],
                       capture_output=True, timeout=600)
        subprocess.run(["git", "-C", str(other), "remote", "set-url", "origin",
                        "https://github.com/shw097-team/HG-KSEOS.git"], capture_output=True)
    try:
        gate.run(other, INSTANCE)
        raise AssertionError("expected a refusal")
    except Exception as exc:  # noqa: BLE001
        assert getattr(exc, "code", None) == "INSTANCE_REPO_IDENTITY_MISMATCH", exc


def _run_standalone() -> int:
    tests = [(n, o) for n, o in sorted(globals().items()) if n.startswith("test_")]
    failures = []
    for name, fn in tests:
        try:
            returned = fn()
        except Exception as exc:  # noqa: BLE001
            failures.append((name, "%s: %s" % (type(exc).__name__, exc)))
        else:
            if isinstance(returned, str) and returned.startswith("SKIP"):
                failures.append((name, "SKIP_IS_A_FAILURE: " + returned))
            else:
                print("PASS %s" % name)
    print("\n%d/%d passed" % (len(tests) - len(failures), len(tests)))
    for name, why in failures:
        print("FAIL %s -> %s" % (name, why))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run_standalone())
