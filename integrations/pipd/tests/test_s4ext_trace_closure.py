"""S4EXT-R1 (TT-S4EXT-002 / F002): typed trace endpoints + bundle graph closure.

F002 of the external challenge was a CONFIRMED_DEFECT at schema level:

* ``schemas/TraceLink.schema.json`` declared the seven endpoint/relation fields as the empty
  schema ``{}``, so ``from_id: 12345``, ``from_hash: {"a": 1}``, ``to_type: null`` and ``""`` were
  all schema-valid;
* ``schemas/PI-PKG.schema.json`` inlined only the ``required`` list for nested ``trace`` items, so
  the nested form was weaker than the standalone family it claims equivalence to;
* ``validate.validate_bundle`` never consulted ``pipeline.trace_closure``, so ``pipd validate
  --bundle`` could return PASS while an endpoint hash was fabricated or an endpoint did not exist
  at all -- the closure capability existed but was not on the CLI's acceptance path;
* ``validate._body_hash`` deliberately excludes ``trace`` (to avoid a parent-hash cycle), so a
  tampered trace does NOT change the PI's ``content_hash``: the body hash cannot catch this class.

This module pins the repair in BOTH directions and keeps the legal cases legal:

* positive -- the real compiler chain (PI/PD/ECP/TQAEP) validates, its closure reaches ``FULL``,
  a single PI-PKG closes against its own atoms, legacy ``version="1"`` records still pass;
* positive -- a bundle with no trace edge is labelled ``SCHEMA_ONLY`` (never passed off as closed);
* negative -- wrong-type endpoints are the SCHEMA first-fail, and orphan / hash-mismatch edges are
  CLOSURE failures that make the bundle verdict FAIL;
* drift -- the inlined PI constraint set and the standalone TraceLink family cannot diverge, and
  the ``from_type``/``to_type`` enum cannot drift from ``schemas/registry.json``.

Deterministic only; no LLM, no network. Runnable standalone.
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

from pipd_ls_sp import pipeline, registry, validate  # noqa: E402

GOAL = "以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 規格包編譯系統，完成測試驗收與公開交付。"
MAKER, CHECKER = "HERMES-MAKER", "GPT-6.1-SOL-AO-LANE"
RECEIPT = "deleg_s4ext/lane-trace-closure"
SCHEMAS_DIR = ROOT / "schemas"


# --------------------------------------------------------------------------- helpers
def _init_git_repo(path: Path) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}

    def g(*a: str) -> None:
        subprocess.run(["git", "-C", str(path).replace("\\", "/"), *a],
                       check=True, capture_output=True, text=True, env=env)

    path.mkdir(parents=True, exist_ok=True)
    g("init", "-q")
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    g("add", ".")
    g("commit", "-q", "-m", "seed")


def _bundle(repo: Path) -> dict:
    card = pipeline.intake(GOAL, sources=[str(repo)], constraints=["c1"], non_goals=["n1"])
    pi = pipeline.compile_pi(card, "LITE")
    pd = pipeline.bind_pd(pi, {"root": str(repo), "writable_scope": "src/**"})
    ecp = pipeline.compile_ecp(pd, pi)
    tqaep = pipeline.compile_tqaep(pi, ecp, maker=MAKER, checker=CHECKER,
                                   checker_execution_receipt=RECEIPT)
    return {"PI-PKG": pi, "PD-PKG": pd, "ECP": ecp, "TQAEP": tqaep}


def _findings(contract: str, record: dict) -> list[dict]:
    return validate.validate_bundle({contract: record}, SCHEMAS_DIR)["findings"]


class LegalTraceStillPassesTests(unittest.TestCase):
    """The repair must not narrow a legal chain (the report's 'no over-narrowing' rule)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls._tmp.name) / "repo"
        _init_git_repo(cls.repo)
        cls.bundle = _bundle(cls.repo)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_full_chain_validates_and_closes(self) -> None:
        res = validate.validate_bundle(self.bundle, SCHEMAS_DIR)
        self.assertEqual(res["findings"], [], str(res["findings"])[:600])
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["checked"], 4)
        self.assertEqual(res["closure"], "FULL", "the real chain must reach full graph closure")
        self.assertEqual(len(self.bundle["PI-PKG"]["trace"]),
                         len(self.bundle["PI-PKG"]["stable_semantic_contract"]["atoms"]))

    def test_single_pi_closes_against_its_own_atoms(self) -> None:
        res = validate.validate_bundle({"PI-PKG": self.bundle["PI-PKG"]}, SCHEMAS_DIR)
        self.assertEqual(res["verdict"], "PASS", str(res["findings"])[:400])
        self.assertEqual(res["closure"], "FULL")

    def test_real_trace_link_is_legal_beside_its_endpoints(self) -> None:
        """A TraceLink bundled WITH the PI it points at resolves on both sides."""
        link = self.bundle["PI-PKG"]["trace"][0]
        res = validate.validate_bundle({"PI-PKG": self.bundle["PI-PKG"], "TraceLink": link},
                                       SCHEMAS_DIR)
        self.assertEqual(res["verdict"], "PASS", str(res["findings"])[:400])
        self.assertEqual(res["closure"], "FULL")
        self.assertEqual(validate.validate_record("TraceLink", link, SCHEMAS_DIR), [])
        self.assertEqual(link["version"], "1", "the legacy version grammar must survive")

    def test_a_lone_edge_without_its_endpoints_is_fail_closed(self) -> None:
        """A TraceLink alone in a bundle cannot be closed -- and must not be reported as PASS."""
        link = self.bundle["PI-PKG"]["trace"][0]
        res = validate.validate_bundle({"TraceLink": link}, SCHEMAS_DIR)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["closure"], "FAILED")

    def test_legacy_version_and_nested_trace_survive_a_round_trip(self) -> None:
        pi = json.loads(json.dumps(self.bundle["PI-PKG"]))
        self.assertEqual(pi["trace"][0]["version"], "1")
        self.assertEqual(validate.validate_bundle({"PI-PKG": pi}, SCHEMAS_DIR)["findings"], [])


class PartialBundleIsLabelledSchemaOnlyTests(unittest.TestCase):
    """A bundle with no trace edge must NOT be presented as trace-closed."""

    def test_trace_free_bundle_is_schema_only(self) -> None:
        rec = {
            "subject_id": "WP-0123456789abcdef", "version": "1", "content_hash": "b" * 64,
            "schema_version": "WorkOrderCandidate@1", "candidate_only": True,
        }
        res = validate.validate_bundle({"WorkOrderCandidate": rec}, SCHEMAS_DIR)
        self.assertEqual(res["verdict"], "PASS", str(res["findings"])[:400])
        self.assertEqual(res["closure"], "SCHEMA_ONLY")

    def test_empty_bundle_reports_no_closure(self) -> None:
        res = validate.validate_bundle({}, SCHEMAS_DIR)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["closure"], "SCHEMA_ONLY")


class TypedEndpointTests(unittest.TestCase):
    """The seven endpoint/relation fields are typed: the exact probe from the report must fail."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        repo = Path(cls._tmp.name) / "repo"
        _init_git_repo(repo)
        cls.pi = _bundle(repo)["PI-PKG"]
        cls.link = cls.pi["trace"][0]

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _mutated_link(self, **over: object) -> dict:
        rec = json.loads(json.dumps(self.link))
        rec.update(over)
        return rec

    def test_integer_from_id_is_schema_first_fail(self) -> None:
        f = _findings("TraceLink", self._mutated_link(from_id=12345))
        self.assertTrue(f, "an integer endpoint id must be refused")
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("TraceLink/from_id", f[0]["detail"])

    def test_object_from_hash_is_schema_first_fail(self) -> None:
        f = _findings("TraceLink", self._mutated_link(from_hash={"a": 1}))
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("TraceLink/from_hash", f[0]["detail"])

    def test_null_and_blank_endpoint_strings_are_refused(self) -> None:
        for field in ("from_type", "from_id", "to_type", "to_id", "rationale"):
            for bad in (None, "", 7):
                f = _findings("TraceLink", self._mutated_link(**{field: bad}))
                self.assertTrue(f, f"{field}={bad!r} must be refused")
                self.assertEqual(f[0]["kind"], "SCHEMA", f"{field}={bad!r}")

    def test_short_or_uppercase_hash_is_refused(self) -> None:
        for bad in ("abc", "A" * 64, "g" * 64):
            f = _findings("TraceLink", self._mutated_link(to_hash=bad))
            self.assertTrue(f, f"to_hash={bad!r} must be refused")
            self.assertEqual(f[0]["kind"], "SCHEMA")

    def test_unknown_endpoint_type_is_refused(self) -> None:
        f = _findings("TraceLink", self._mutated_link(to_type="NotAFamily"))
        self.assertTrue(f)
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("TraceLink/to_type", f[0]["detail"])

    def test_nested_pi_trace_endpoint_is_typed_too(self) -> None:
        """The report's probe: nested trace, required keys present, wrong types must be refused."""
        pi = json.loads(json.dumps(self.pi))
        pi["trace"][0]["from_hash"] = 12345
        pi["trace"][0]["to_id"] = 999
        f = _findings("PI-PKG", pi)
        self.assertTrue(f, "the nested trace form must be typed like the standalone family")
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("PI-PKG/trace/0", f[0]["detail"])

    def test_extra_key_in_an_endpoint_is_refused(self) -> None:
        link = self._mutated_link()
        link["sneaky"] = "extra"
        f = _findings("TraceLink", link)
        self.assertTrue(f)
        self.assertEqual(f[0]["kind"], "SCHEMA")
        self.assertIn("additional properties", f[0]["detail"].lower())

    def test_trace_hash_edit_does_not_move_the_pi_content_hash(self) -> None:
        """Documents WHY the schema/closure layers are the only defence for this field."""
        pi = json.loads(json.dumps(self.pi))
        before = pi["content_hash"]
        pi["trace"][0]["to_hash"] = "c" * 64
        self.assertEqual(pi["content_hash"], before)


class GraphClosureRefusalTests(unittest.TestCase):
    """Orphan endpoints and hash mismatches must make the bundle verdict FAIL."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        repo = Path(cls._tmp.name) / "repo"
        _init_git_repo(repo)
        cls.pi = _bundle(repo)["PI-PKG"]

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _pi_with(self, **over: object) -> dict:
        pi = json.loads(json.dumps(self.pi))
        pi["trace"][0].update(over)
        return pi

    def _expect_closure_refusal(self, pi: dict) -> str:
        res = validate.validate_bundle({"PI-PKG": pi}, SCHEMAS_DIR)
        self.assertEqual(res["verdict"], "FAIL", "a broken trace graph must not pass")
        self.assertEqual(res["closure"], "FAILED")
        closures = [f for f in res["findings"] if f["kind"] == "CLOSURE"]
        self.assertTrue(closures, res["findings"])
        return " | ".join(c["detail"] for c in closures)

    def test_fabricated_endpoint_hash_is_refused(self) -> None:
        detail = self._expect_closure_refusal(self._pi_with(to_hash="d" * 64))
        self.assertIn("hash mismatch", detail)

    def test_orphan_endpoint_is_refused(self) -> None:
        detail = self._expect_closure_refusal(self._pi_with(to_id="ATOM-ffffffffffffffff"))
        self.assertIn("orphan", detail)

    def test_missing_source_endpoint_is_refused(self) -> None:
        detail = self._expect_closure_refusal(self._pi_with(from_id="PI-0000000000000000"))
        self.assertIn("not present in the bundle", detail)

    def test_duplicated_edge_with_one_bad_hash_is_refused(self) -> None:
        pi = self._pi_with()
        dup = json.loads(json.dumps(pi["trace"][0]))
        dup["to_hash"] = "e" * 64
        pi["trace"].append(dup)
        self.assertIn("hash mismatch", self._expect_closure_refusal(pi))

    def test_stale_source_hash_is_refused(self) -> None:
        """A stale (previous revision's) source hash is a mismatch, not a legal edge."""
        pi = json.loads(json.dumps(self.pi))
        pi["trace"][0]["from_hash"] = "f" * 64
        self.assertIn("hash mismatch", self._expect_closure_refusal(pi))

    def test_closure_findings_are_named_not_aggregated(self) -> None:
        pi = self._pi_with(to_hash="d" * 64, from_hash="f" * 64)
        res = validate.validate_bundle({"PI-PKG": pi}, SCHEMAS_DIR)
        details = [f["detail"] for f in res["findings"] if f["kind"] == "CLOSURE"]
        self.assertGreaterEqual(len(details), 2, details)

    def test_closure_never_consults_the_network(self) -> None:
        """The closure is derived from the bundle in memory (no resolver, no $ref fetch)."""
        src = (ROOT / "src" / "pipd_ls_sp" / "validate.py").read_text(encoding="utf-8")
        body = src.split("def closure_findings", 1)[1].split("def validate_bundle", 1)[0]
        for forbidden in ("urlopen", "requests.", "http://", "https://", "subprocess"):
            self.assertNotIn(forbidden, body, f"closure must not reach out via {forbidden}")


class SchemaDriftTests(unittest.TestCase):
    """One constraint set, two places: they must not diverge."""

    def test_inlined_pi_trace_items_equal_the_standalone_family(self) -> None:
        tl = json.loads((SCHEMAS_DIR / "TraceLink.schema.json").read_text(encoding="utf-8"))
        pi = json.loads((SCHEMAS_DIR / "PI-PKG.schema.json").read_text(encoding="utf-8"))
        items = pi["properties"]["trace"]["items"]
        self.assertEqual(items["properties"], tl["properties"])
        self.assertEqual(items["required"], tl["required"])
        self.assertEqual(items["additionalProperties"], tl.get("additionalProperties"))

    def test_endpoint_type_enum_matches_the_registry_families(self) -> None:
        tl = json.loads((SCHEMAS_DIR / "TraceLink.schema.json").read_text(encoding="utf-8"))
        reg = registry.load_registry(SCHEMAS_DIR)
        families = sorted(row["contract"] for row in reg["families"])
        self.assertEqual(sorted(tl["properties"]["from_type"]["enum"]), families)
        self.assertEqual(sorted(tl["properties"]["to_type"]["enum"]), families)
        self.assertEqual(len(families), 19)

    def test_no_remote_ref_anywhere_in_the_two_schemas(self) -> None:
        for name in ("TraceLink.schema.json", "PI-PKG.schema.json"):
            text = (SCHEMAS_DIR / name).read_text(encoding="utf-8")
            self.assertNotIn('"$ref"', text, f"{name} must inline its constraints, not $ref them")


class CliBundleClosureRouteTests(unittest.TestCase):
    """`pipd validate --bundle` is the surface a consumer actually trusts (cli.py route)."""

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", *args],
                              capture_output=True, text=True, env=env, cwd=str(ROOT))

    def test_cli_reports_closure_state_on_a_legal_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            bundle = _bundle(repo)
            path = Path(td) / "bundle.json"
            path.write_text(json.dumps(bundle), encoding="utf-8")
            out = self._cli("--root", str(ROOT), "validate", "--bundle", str(path))
            self.assertEqual(out.returncode, 0, out.stderr)
            payload = json.loads(out.stdout)
            self.assertEqual(payload["verdict"], "PASS", payload)
            self.assertEqual(payload["closure"], "FULL")

    def test_cli_refuses_a_fabricated_endpoint_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            bundle = _bundle(repo)
            bundle["PI-PKG"]["trace"][0]["to_hash"] = "d" * 64
            path = Path(td) / "bundle.json"
            path.write_text(json.dumps(bundle), encoding="utf-8")
            out = self._cli("--root", str(ROOT), "validate", "--bundle", str(path))
            payload = json.loads(out.stdout)
            self.assertEqual(payload["verdict"], "FAIL", payload)
            self.assertEqual(payload["closure"], "FAILED")
            self.assertNotEqual(out.returncode, 0,
                                "a refused bundle must not exit 0 on the CLI surface")


class EndpointTypeCoherenceTests(unittest.TestCase):
    """S4EXT-R1 external-AO finding C3.

    The first candidate rejected mis-typed *values* but still PASSed an endpoint whose declared
    TYPE named a different family than the record its id resolves to. The graph must fail closed:
    a PI-PKG record referenced as if it were a PD-PKG is not a closed chain, it is a wrong claim.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        repo = Path(cls._tmp.name) / "repo"
        _init_git_repo(repo)
        cls.pi = _bundle(repo)["PI-PKG"]

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_declared_type_contradicting_the_resolved_family_is_refused(self) -> None:
        pi = json.loads(json.dumps(self.pi))
        edge = pi["trace"][0]
        edge["from_type"] = "PD-PKG"            # the id still resolves to the PI-PKG record
        res = validate.validate_bundle({"PI-PKG": pi}, SCHEMAS_DIR)
        self.assertEqual(res["verdict"], "FAIL", res)
        self.assertEqual(res["closure"], "FAILED", res)
        self.assertTrue(
            any("contradicts the resolved record family" in f["detail"] for f in res["findings"]),
            res["findings"])

    def test_a_wrong_type_on_either_side_is_refused(self) -> None:
        for side, bad in (("from_type", "PD-PKG"), ("to_type", "PI-PKG")):
            with self.subTest(side=side):
                pi = json.loads(json.dumps(self.pi))
                pi["trace"][0][side] = bad
                res = validate.validate_bundle({"PI-PKG": pi}, SCHEMAS_DIR)
                self.assertEqual(res["verdict"], "FAIL", res)
                self.assertEqual(res["closure"], "FAILED", res)

    def test_the_untouched_legal_edge_still_closes(self) -> None:
        res = validate.validate_bundle({"PI-PKG": json.loads(json.dumps(self.pi))}, SCHEMAS_DIR)
        self.assertEqual(res["closure"], "FULL", res)
        self.assertEqual(res["verdict"], "PASS", res)


if __name__ == "__main__":
    unittest.main(verbosity=2)
