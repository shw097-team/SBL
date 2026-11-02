"""WO-S4-CONTRACT-03 (post-release narrow repair): pin the three confirmed contract defects.

D1 -- the universal identity fields were declared as the empty schema ``{}`` in every family and
      ``PI-PKG.trace`` was ``{}`` too, so ANY JSON value (an integer id, ``null``, a string hash)
      was schema-valid and only a semantic ``str()`` coercion stood in the way. The pins below
      assert a wrongly-typed identity / trace is now the SCHEMA first-fail, whose detail names the
      contract and the JSON pointer.

D2 -- ``compute_profile`` counted the RAW ``axes`` (so ``["intent","intent","intent","intent"]``
      escalated LITE to ASSURED) while ``profile_record`` emitted ``sorted(set(axes))`` - the
      emitted record disagreed with the escalation basis. It now fails closed on a malformed axis
      set and returns ONE normalised list the record consumes verbatim.

D3 -- there was no risk input and ``vetoes`` was hardcoded ``[]``. The computation now states
      ``risk_assessment = "NOT_ASSESSED"`` when no evidence was supplied, and never emits
      ``LOW_RISK_VERIFIED``. ``ProfileBinding.schema.json`` does not declare ``risk_assessment``,
      so it rides in the ``_profile_meta`` sidecar rather than mutating the record contract.

Self-bootstrap (same rule as every test file here): runnable standalone.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, profiles, registry, validate  # noqa: E402
from pipd_ls_sp.errors import ProfileVeto, UnsupportedSurface  # noqa: E402

GOAL = "以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 規格包編譯系統，完成測試驗收與公開交付。"
MAKER, CHECKER = "HERMES-MAKER", "GLM-5.3-FLASH-AO-LANE"
RECEIPT = "deleg_s4post/lane-contract03"

# The canonical identity typing the repair pins across every family (brief step 1).
IDENTITY_TYPES = {
    "subject_id": {"type": "string", "minLength": 8, "maxLength": 200},
    "version": {"type": "string", "minLength": 1, "maxLength": 64},
    "content_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "schema_version": {"type": "string", "minLength": 1, "maxLength": 64},
}
SCHEMAS_DIR = ROOT / "schemas"


def _artifact_identity(**over: object) -> dict:
    rec = {"subject_id": "AI-0123456789abcdef", "version": "1", "content_hash": "a" * 64,
           "schema_version": "ArtifactIdentity@1", "supersedes": [], "invalidates": []}
    rec.update(over)
    return rec


def _bundle(contract: str, record: dict) -> list[dict]:
    """Findings for a single-record bundle (order preserved: SCHEMA findings before SEMANTIC)."""
    return validate.validate_bundle({contract: record}, SCHEMAS_DIR)["findings"]


class IdentityTypeTests(unittest.TestCase):
    """D1: a wrongly-typed universal identity field is the schema first-fail."""

    def test_every_family_identity_is_typed_to_the_canonical_spec(self) -> None:
        reg = registry.load_registry(SCHEMAS_DIR)
        self.assertEqual(len(reg["families"]), 19)
        for row in reg["families"]:
            schema = json.loads((SCHEMAS_DIR / f"{row['contract']}.schema.json")
                                .read_text(encoding="utf-8"))
            props = schema["properties"]
            for field, spec in IDENTITY_TYPES.items():
                self.assertIn(field, props, f"{row['contract']} must declare {field}")
                self.assertEqual(props[field], spec,
                                 f"{row['contract']}.{field} must be typed {spec}")

    def test_artifact_identity_legal_record_passes(self) -> None:
        self.assertEqual(_bundle("ArtifactIdentity", _artifact_identity()), [])

    def test_subject_id_integer_is_schema_first_fail(self) -> None:
        f = _bundle("ArtifactIdentity", _artifact_identity(subject_id=12345678))
        self.assertTrue(f, "an integer subject_id must be refused")
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertEqual(f[0]["contract"], "ArtifactIdentity")
        self.assertIn("ArtifactIdentity/subject_id", f[0]["detail"])
        self.assertIn("is not of type 'string'", f[0]["detail"])

    def test_subject_id_null_is_schema_first_fail(self) -> None:
        f = _bundle("ArtifactIdentity", _artifact_identity(subject_id=None))
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("ArtifactIdentity/subject_id", f[0]["detail"])
        self.assertIn("is not of type 'string'", f[0]["detail"])

    def test_version_integer_is_schema_first_fail(self) -> None:
        f = _bundle("ArtifactIdentity", _artifact_identity(version=1))
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("ArtifactIdentity/version", f[0]["detail"])
        self.assertIn("is not of type 'string'", f[0]["detail"])

    def test_version_null_is_schema_first_fail(self) -> None:
        f = _bundle("ArtifactIdentity", _artifact_identity(version=None))
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("ArtifactIdentity/version", f[0]["detail"])
        self.assertIn("is not of type 'string'", f[0]["detail"])

    def test_content_hash_non_hex_is_schema_first_fail(self) -> None:
        f = _bundle("ArtifactIdentity", _artifact_identity(content_hash="XYZ"))
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("ArtifactIdentity/content_hash", f[0]["detail"])
        self.assertIn("does not match", f[0]["detail"])

    def test_content_hash_integer_is_schema_first_fail(self) -> None:
        f = _bundle("ArtifactIdentity", _artifact_identity(content_hash=123))
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("ArtifactIdentity/content_hash", f[0]["detail"])
        self.assertIn("is not of type 'string'", f[0]["detail"])

    def test_schema_version_integer_is_schema_first_fail(self) -> None:
        f = _bundle("ArtifactIdentity", _artifact_identity(schema_version=1))
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("ArtifactIdentity/schema_version", f[0]["detail"])
        self.assertIn("is not of type 'string'", f[0]["detail"])


class PiTraceTypeTests(unittest.TestCase):
    """D1 (PI): ``trace`` is an array of trace links and nothing else."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        repo = Path(cls._tmp.name) / "repo"
        _init_git_repo(repo)
        cls.repo = repo
        cls.pi = pipeline.compile_pi(
            pipeline.intake(GOAL, sources=[str(repo)], constraints=["c1"], non_goals=["n1"]),
            "LITE")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_legal_pi_with_trace_array_passes(self) -> None:
        self.assertTrue(self.pi["trace"], "the compiler must emit trace links")
        self.assertEqual(_bundle("PI-PKG", self.pi), [])

    def _trace_case(self, value: object) -> None:
        rec = dict(self.pi)
        rec["trace"] = value
        f = _bundle("PI-PKG", rec)
        self.assertTrue(f, f"trace={value!r} must be refused")
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("PI-PKG/trace", f[0]["detail"])
        self.assertIn("is not of type 'array'", f[0]["detail"])

    def test_trace_string_is_refused(self) -> None:
        self._trace_case("not-an-array")

    def test_trace_null_is_refused(self) -> None:
        self._trace_case(None)

    def test_trace_object_is_refused(self) -> None:
        self._trace_case({})

    def test_trace_integer_is_refused(self) -> None:
        self._trace_case(123)

    def test_trace_missing_is_still_required(self) -> None:
        rec = dict(self.pi)
        rec.pop("trace")
        f = _bundle("PI-PKG", rec)
        self.assertTrue(any("trace" in x["detail"] for x in f), f)


class UndeclaredTraceStillRefusedTests(unittest.TestCase):
    """CE-2 guard restated: an undeclared ``trace`` on PD/ECP/TQAEP is still refused."""

    def test_undeclared_trace_on_pd_ecp_tqaep_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            bundle = _compilers_bundle(repo)
            for contract in ("PD-PKG", "ECP", "TQAEP"):
                self.assertNotIn("trace", bundle[contract])
                widened = dict(bundle[contract])
                widened["trace"] = [{"undeclared": True}]
                findings = _bundle(contract, widened)
                self.assertTrue(
                    any("trace" in x["detail"] and "was unexpected" in x["detail"]
                        for x in findings),
                    f"undeclared trace must be refused on {contract}: {findings}")


class BodyEditWithoutRehashTests(unittest.TestCase):
    """A release-bound body edited without re-issuing content_hash is still refused."""

    def test_pd_body_edit_without_rehash_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            pd = _compilers_bundle(repo)["PD-PKG"]
            edited = json.loads(json.dumps(pd))
            edited["currentness"]["state"] = "STALE"  # body change, identity untouched
            f = _bundle("PD-PKG", edited)
            self.assertTrue(f, "an edited body must not pass")
            self.assertTrue(any("content_hash does not match the record body" in x["detail"]
                                for x in f), f)


class ProfileAxisRefusalTests(unittest.TestCase):
    """D2: malformed profile axes fail closed, typed, before any escalation math."""

    def test_duplicate_axis_is_typed_profile_veto(self) -> None:
        with self.assertRaises(ProfileVeto) as cm:
            profiles.compute_profile("LITE", axes=["intent", "intent"])
        self.assertIn("intent", str(cm.exception))

    def test_non_string_axis_is_typed_profile_veto(self) -> None:
        with self.assertRaises(ProfileVeto):
            profiles.compute_profile("LITE", axes=[1, 2])

    def test_empty_axis_list_is_typed_profile_veto(self) -> None:
        with self.assertRaises(ProfileVeto):
            profiles.compute_profile("LITE", axes=[])

    def test_non_list_axes_is_typed_profile_veto(self) -> None:
        with self.assertRaises(ProfileVeto):
            profiles.compute_profile("LITE", axes="intent")  # type: ignore[arg-type]

    def test_unknown_axis_is_typed_unsupported_surface(self) -> None:
        with self.assertRaises(UnsupportedSurface):
            profiles.compute_profile("LITE", axes=["nope"])

    def test_escalation_basis_and_emitted_record_cannot_disagree(self) -> None:
        # The exact D2 bug: raw duplicates escalated LITE while the record showed one axis.
        # It is now impossible - duplicates are refused outright.
        with self.assertRaises(ProfileVeto):
            pipeline.profile_record("LITE", ["intent", "intent", "intent", "intent"])
        # For a legal set, the record consumes EXACTLY the normalised list compute_profile returns.
        rec, full = pipeline.profile_record("LITE", ["verification", "intent", "knowledge"])
        self.assertEqual(rec["axes"], full["axes"])
        self.assertEqual(rec["axes"], ["intent", "knowledge", "verification"])
        self.assertEqual(sorted(full["axes"]), full["axes"], "normalised list is sorted+unique")


class RiskAssessmentHonestyTests(unittest.TestCase):
    """D3: state the absent risk assessment; never emit LOW_RISK_VERIFIED."""

    def test_compute_profile_states_not_assessed_without_evidence(self) -> None:
        full = profiles.compute_profile("LITE", axes=["intent"])
        self.assertEqual(full["risk_assessment"], "NOT_ASSESSED")
        self.assertNotIn("LOW_RISK_VERIFIED", json.dumps(full))

    def test_profile_binding_contract_does_not_declare_risk_assessment(self) -> None:
        schema = json.loads((SCHEMAS_DIR / "ProfileBinding.schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("risk_assessment", schema["properties"],
                         "adding it to the record contract would be a breaking change")

    def test_risk_assessment_rides_in_the_sidecar_not_the_record(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            pi = _compilers_bundle(repo)["PI-PKG"]
            pb = pi["stable_semantic_contract"]["profile_binding"]
            self.assertNotIn("risk_assessment", pb, "must not widen the ProfileBinding record")
            self.assertEqual(pi["_profile_meta"]["risk_assessment"], "NOT_ASSESSED")
            # and the PI still validates (the sidecar is stripped before the schema check)
            self.assertEqual(_bundle("PI-PKG", pi), [])

    def test_no_low_risk_verified_anywhere_in_a_compiled_pi(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            blob = json.dumps(_compilers_bundle(repo))
            self.assertNotIn("LOW_RISK_VERIFIED", blob)


class PositiveBundleTests(unittest.TestCase):
    """A legal PI/PD/ECP/TQAEP bundle still validates (no over-narrowing)."""

    def test_legal_bundle_still_validates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            bundle = _compilers_bundle(repo)
            res = validate.validate_bundle(bundle, SCHEMAS_DIR)
            self.assertEqual(res["findings"], [], str(res["findings"])[:800])
            self.assertEqual(res["verdict"], "PASS")
            self.assertEqual(res["checked"], 4)


# ---------------------------------------------------------------- helpers
def _init_git_repo(path: Path) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}

    def g(*a: str) -> None:
        subprocess.run(["git", "-C", str(path), *a], check=True, capture_output=True, text=True, env=env)

    path.mkdir(parents=True, exist_ok=True)
    g("init", "-q")
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    g("add", ".")
    g("commit", "-q", "-m", "seed")


def _compilers_bundle(repo: Path) -> dict:
    card = pipeline.intake(GOAL, sources=[str(repo)], constraints=["c1"], non_goals=["n1"])
    pi = pipeline.compile_pi(card, "LITE")
    pd = pipeline.bind_pd(pi, {"root": str(repo), "writable_scope": "src/**"})
    ecp = pipeline.compile_ecp(pd, pi)
    tqaep = pipeline.compile_tqaep(pi, ecp, maker=MAKER, checker=CHECKER,
                                   checker_execution_receipt=RECEIPT)
    return {"PI-PKG": pi, "PD-PKG": pd, "ECP": ecp, "TQAEP": tqaep}


if __name__ == "__main__":
    unittest.main(verbosity=2)
