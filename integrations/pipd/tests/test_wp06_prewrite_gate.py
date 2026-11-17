"""POS/NEG for the WP06 pre-write gate — after the owner's H-16 correction.

The corrections this file pins:
  * identity is an **attested read** (or a recorded attestation file), never back-filled from the
    instance, and ``remote.origin.url`` is corroboration only;
  * the repository must sit inside a **protected root** the original registry names, so on this
    host the real registry refuses the FHS clone and only an explicitly labelled fixture reaches
    the mechanical checks;
  * presence at HEAD is decided by ``ls-tree``, so a non-zero ``cat-file`` is unreadable, not absent;
  * ops are consumed **across calls** by an exclusive nonce file: replay is refused, zero/negative
    ops are refused, and the TTL is counted from the signature only;
  * TOCTOU: a tree/index change between read and verdict is refused.

A test that returns "SKIP" counts as a failure in the standalone runner.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve()
PIPD = HERE.parents[1]
SRC = PIPD / "src"
for extra in (SRC, PIPD / "tools"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from pipd_ls_sp import operation_registry as oreg  # noqa: E402


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, "cannot load %s" % path
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


oi = _load("wp06_oi", PIPD / "tools" / "operation_instance.py")
gate = _load("wp06_gate", PIPD / "tools" / "wp06_prewrite_gate.py")

RUN = PIPD.parents[3]
CONTRACT_PATH = PIPD / "contracts" / "operation-registry.pre-v2-r3.json"
SIDECAR_PATH = PIPD / "contracts" / "operation-registry.pre-v2-r3.owner.sig.json"
INSTANCE = "OP-WP06-FHSVNEXT-ADD-01"
WS1 = "adapters/hgk_admission/admission_ref.py"
WS2 = "tests/affected/W1/test_hgk_admission_ref.py"
WS1_SHA = "21ee790faebc5cbe62b7033bfdf253bd17d26e2f1ddd5f00b10bc2d80079b52c"
WS2_SHA = "110f081659a14c12380cfe0252e5c0d2a2ecc316f81384640ed388bcb1e3e1a8"
REPO = RUN / "staging" / "fhs_vnext"
FIXTURE_REGISTRY = RUN / "staging" / "wp06_binding" / "registry.fixture.json"
ATTESTATION = RUN / "staging" / "wp06_binding" / "repo_id_attestation.json"
HEAD = "27abc69b21f66cbf345fc799263d7ed83e34b7cf"
TREE = "14bb6ef11a041a08f4665595999ca278f02fa5ac"
REAL_REGISTRY = pathlib.Path(r"C:/ProgramData/HG-KSEOS/native-admission/registry.json")


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_bytes())


def signed_scope() -> list:
    return json.loads(json.loads(SIDECAR_PATH.read_text(encoding="utf-8"))["payload_json"])["scope"]


def contract_sha() -> str:
    return hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()


def state(**over) -> dict:
    base = {"head": HEAD, "tree": TREE, "write_scope": [WS1, WS2],
            "preimages": {WS1: "ABSENT", WS2: "ABSENT"},
            "repo_id": 1457756751, "full_name": "shw097-team/FHS_vNEXT"}
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
    except Exception as exc:  # noqa: BLE001 - the code is the contract, the class is not
        return getattr(exc, "code", type(exc).__name__)
    return "NO_REFUSAL"


def fresh_journal() -> pathlib.Path:
    return pathlib.Path(tempfile.mkdtemp(prefix="wp06-gate-journal-"))


# ------------------------------------------------------------------ identity

def test_pos_remote_url_forms_resolve_to_one_full_name():
    for url in ("https://github.com/shw097-team/FHS_vNEXT.git",
                "https://github.com/shw097-team/FHS_vNEXT",
                "git@github.com:shw097-team/FHS_vNEXT.git",
                "ssh://git@github.com/shw097-team/FHS_vNEXT.git"):
        assert oi.full_name_from_remote_url(url) == "shw097-team/FHS_vNEXT"


def test_neg_unparseable_or_empty_remote_is_refused_not_empty_stringed():
    for url in ("", "   ", "/local/path/repo", "file:///c/Projects/repo"):
        assert code(lambda u=url: oi.full_name_from_remote_url(u)) == "INSTANCE_REPO_IDENTITY_UNRESOLVED"


def test_pos_attestation_file_supplies_the_id_with_its_own_digest():
    doc = gate.attest_repo_id("shw097-team/FHS_vNEXT", attestation_file=ATTESTATION)
    assert doc["id"] == 1457756751
    assert doc["full_name"] == "shw097-team/FHS_vNEXT"
    assert len(doc["source_sha256"]) == 64
    assert doc["source"].startswith("GITHUB_REST_GET")


def test_neg_attestation_file_with_another_repo_is_refused():
    bad = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    bad["full_name"] = "shw097-team/HG-KSEOS"
    fd, path = tempfile.mkstemp(suffix=".json")
    with open(fd, "w", encoding="utf-8") as fh:
        json.dump(bad, fh)
    assert code(lambda: gate.attest_repo_id("shw097-team/FHS_vNEXT",
                                            attestation_file=pathlib.Path(path))) == \
        "INSTANCE_REPO_ID_UNATTESTED"


def test_neg_missing_repo_identity_in_the_write_state_is_refused():
    st = state()
    st.pop("repo_id")
    assert code(lambda: write_call(repo_state=st)) == "INSTANCE_REPO_IDENTITY_MISSING"


def test_neg_wrong_numeric_id_is_refused():
    assert code(lambda: write_call(repo_state=state(repo_id=1457756752))) == \
        "INSTANCE_REPO_IDENTITY_MISMATCH"


# ------------------------------------------------------------------ protected root

def test_neg_the_real_registry_does_not_protect_the_fhs_clone():
    """The honest verdict on this host: B1 rev15 protects a different root, so no lawful write."""
    assert code(lambda: gate.protected_root_binding(REPO.resolve(), REAL_REGISTRY)) == \
        "INSTANCE_PROTECTED_ROOT_UNBOUND"


def test_pos_a_fixture_registry_binds_the_staging_root_and_says_so():
    bound = gate.protected_root_binding(REPO.resolve(), FIXTURE_REGISTRY)
    assert bound["mission_id"] == "FIXTURE-WP06-GATE-EXERCISE"
    assert bound["root_identity"] == "FIXTURE_NOT_ORIGINAL"


def test_neg_absent_registry_is_not_a_binding():
    assert code(lambda: gate.protected_root_binding(REPO.resolve(),
                                                    pathlib.Path(tempfile.gettempdir()) / "nope.json")) == \
        "INSTANCE_PROTECTED_ROOT_UNBOUND"


# ------------------------------------------------------------------ ops journal / replay

def test_pos_first_use_claims_the_nonce():
    claim = gate.consume_op(fresh_journal(), "n" * 64, 1)
    assert claim["ops"] == 1 and claim["nonce"] == "n" * 64


def test_neg_replay_of_the_same_nonce_is_refused():
    journal = fresh_journal()
    gate.consume_op(journal, "r" * 64, 1)
    assert code(lambda: gate.consume_op(journal, "r" * 64, 1)) == "INSTANCE_REPLAY_REFUSED"


def test_neg_zero_and_negative_ops_are_refused():
    journal = fresh_journal()
    assert code(lambda: gate.consume_op(journal, "z" * 64, 0)) == "INSTANCE_OPS_INVALID"
    assert code(lambda: gate.consume_op(journal, "y" * 64, -3)) == "INSTANCE_OPS_INVALID"


def test_neg_ops_above_the_signed_maximum_are_refused():
    assert code(lambda: write_call(ops_requested=2)) == "INSTANCE_OPS_EXCEEDED"


def test_neg_expired_ttl_is_refused_and_ttl_never_restarts():
    assert code(lambda: write_call(ttl_remaining_s=0.0)) == "INSTANCE_TTL_EXPIRED"
    assert code(lambda: write_call(ttl_remaining_s=999999.0)) == "INSTANCE_TTL_EXPIRED"
    assert code(lambda: write_call(ttl_remaining_s=None)) == "INSTANCE_TTL_EXPIRED"


def test_neg_ttl_without_an_offset_is_refused_rather_than_assumed():
    assert gate.ttl_remaining({"ttl_seconds": 3600}, "2026-11-18T01:18:44") is None


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


# ------------------------------------------------------------------ repo state / git plumbing

def test_neg_head_and_tree_drift_are_refused():
    assert code(lambda: write_call(repo_state=state(head="0" * 40))) == "INSTANCE_HEAD_DRIFT"
    assert code(lambda: write_call(repo_state=state(tree="0" * 40))) == "INSTANCE_TREE_DRIFT"


def test_neg_preimage_that_already_exists_is_refused():
    assert code(lambda: write_call(repo_state=state(preimages={WS1: "0" * 64, WS2: "ABSENT"}))) == \
        "INSTANCE_PREIMAGE_NOT_ABSENT"


def test_neg_stray_changed_path_is_refused():
    assert code(lambda: write_call(changed_paths=[WS1, WS2, "README.md"])) == \
        "INSTANCE_PATHS_OUTSIDE_WRITESET"


def test_pos_ls_tree_decides_presence_and_cat_file_is_only_read_when_present():
    head_paths = gate.paths_at_head(REPO)
    assert WS1 not in head_paths
    digest, st = gate.blob_at_head(REPO, WS1, head_paths)
    assert st == "ABSENT" and digest == ""
    present = sorted(head_paths)[0]
    digest2, st2 = gate.blob_at_head(REPO, present, head_paths)
    assert st2 == "PRESENT" and len(digest2) == 64


def test_neg_a_cat_file_failure_on_a_present_path_is_corruption_not_absence():
    real_git = gate.git

    def broken(root, *args):
        if args and args[0] == "cat-file":
            return 1, b"", b"fatal: bad object"
        return real_git(root, *args)

    setattr(gate, "git", broken)
    try:
        head_paths = gate.paths_at_head(REPO)
        present = sorted(head_paths)[0]
        assert code(lambda: gate.blob_at_head(REPO, present, head_paths)) == "GIT_OBJECT_UNREADABLE"
    finally:
        setattr(gate, "git", real_git)


def test_neg_unreadable_ls_tree_is_refused():
    real_git = gate.git
    setattr(gate, "git", lambda root, *args: (1, b"", b"fatal: not a git repository"))
    try:
        assert code(lambda: gate.paths_at_head(REPO)) == "GIT_OBJECT_UNREADABLE"
    finally:
        setattr(gate, "git", real_git)


def test_neg_unreadable_status_is_refused_rather_than_read_as_clean():
    real_git = gate.git

    def broken(root, *args):
        if args and args[0] == "status":
            return 128, b"", b"fatal: index unreadable"
        return real_git(root, *args)

    setattr(gate, "git", broken)
    try:
        assert code(lambda: gate.changed_paths(REPO)) == "GIT_STATUS_UNREADABLE"
    finally:
        setattr(gate, "git", real_git)


def test_pos_status_parser_reports_both_sides_of_a_rename():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="wp06-rename-"))
    subprocess.run(["git", "init", "-q", str(tmp)], capture_output=True)
    subprocess.run(["git", "-C", str(tmp), "config", "user.email", "t@t"], capture_output=True)
    subprocess.run(["git", "-C", str(tmp), "config", "user.name", "t"], capture_output=True)
    (tmp / "old.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp), "add", "."], capture_output=True)
    subprocess.run(["git", "-C", str(tmp), "commit", "-qm", "base"], capture_output=True)
    subprocess.run(["git", "-C", str(tmp), "mv", "old.txt", "new.txt"], capture_output=True)
    rows = gate.changed_paths(tmp)
    assert "new.txt" in rows and "old.txt" in rows


def test_neg_toctou_drift_is_refused():
    real_snapshot = gate.snapshot
    calls = {"n": 0}

    def drifting(root):
        calls["n"] += 1
        snap = real_snapshot(root)
        if calls["n"] > 1:
            snap = dict(snap, index_sha256="DRIFTED")
        return snap

    setattr(gate, "snapshot", drifting)
    try:
        assert code(lambda: gate.run(REPO, INSTANCE, registry_path=FIXTURE_REGISTRY,
                                     journal_dir=fresh_journal(), attestation_file=ATTESTATION)) == \
            "INSTANCE_TOCTOU_DRIFT"
    finally:
        setattr(gate, "snapshot", real_snapshot)


# ------------------------------------------------------------------ the whole gate

def test_pos_gate_passes_on_the_fixture_protected_root():
    record = gate.run(REPO, INSTANCE, registry_path=FIXTURE_REGISTRY,
                      journal_dir=fresh_journal(), attestation_file=ATTESTATION)
    assert record["gate"] == "WRITE_GATE_PASSED_NOT_A_PERMIT"
    assert record["admitted"] is False
    assert record["grant_state"] == "NOT_GRANTED"
    assert record["protected_root"]["mission_id"] == "FIXTURE-WP06-GATE-EXERCISE"
    assert record["identity_attestation"]["id"] == 1457756751
    assert record["observed_postimages"] == {WS1: WS1_SHA, WS2: WS2_SHA}
    assert record["preimages_at_head"] == {WS1: "ABSENT", WS2: "ABSENT"}
    assert record["op_claim"]["nonce"]


def test_neg_gate_refuses_on_the_real_registry_before_any_write():
    assert code(lambda: gate.run(REPO, INSTANCE, registry_path=REAL_REGISTRY,
                                 journal_dir=fresh_journal(), attestation_file=ATTESTATION)) == \
        "INSTANCE_PROTECTED_ROOT_UNBOUND"


def test_neg_gate_refuses_a_second_call_on_the_same_journal():
    journal = fresh_journal()
    gate.run(REPO, INSTANCE, registry_path=FIXTURE_REGISTRY, journal_dir=journal,
             attestation_file=ATTESTATION)
    assert code(lambda: gate.run(REPO, INSTANCE, registry_path=FIXTURE_REGISTRY, journal_dir=journal,
                                 attestation_file=ATTESTATION)) == "INSTANCE_REPLAY_REFUSED"


def test_neg_gate_refuses_a_repository_whose_remote_says_something_else():
    other = REPO.parent / "fhs_vnext_identity_probe"
    if not other.exists():
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(REPO), str(other)],
                       capture_output=True, timeout=600)
    subprocess.run(["git", "-C", str(other), "remote", "set-url", "origin",
                    "https://github.com/shw097-team/HG-KSEOS.git"], capture_output=True)
    assert code(lambda: gate.run(other, INSTANCE, registry_path=FIXTURE_REGISTRY,
                                 journal_dir=fresh_journal(), attestation_file=ATTESTATION)) == \
        "INSTANCE_REPO_IDENTITY_MISMATCH"


def test_pos_no_consume_leaves_the_nonce_available():
    journal = fresh_journal()
    gate.run(REPO, INSTANCE, registry_path=FIXTURE_REGISTRY, journal_dir=journal,
             attestation_file=ATTESTATION, consume=False)
    assert list(journal.iterdir()) == []
    gate.run(REPO, INSTANCE, registry_path=FIXTURE_REGISTRY, journal_dir=journal,
             attestation_file=ATTESTATION)
    assert len(list(journal.iterdir())) == 1


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
