"""FW-05 (R-AUD-003) + R-AUD-015: semantic Web projection regressions.

Positive path: the exact five PIPD documents, source-derived from the canonical
objects/profiles, each carrying source objects (id/schema/version), a source
hash, a CapabilityLoss record and a NACK record. OPTIONAL_SITE_UI is excluded
from the Web denominator.

Refusal mutations: MUT-WEB-WRONGSET (including the audit's falsification — the
site UI five files as the Web pack), MUT-EMPTY-PAYLOAD, MUT-MISSING-FIELD,
MUT-SCOPE-WIDENING, MUT-STALE-SOURCE, MUT-NOT-DERIVED.
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pipd_ls_sp import projection as P

DOCS = {"PIPD_BOOTSTRAP.md", "PIPD_CANONICAL_CORE.md", "PIPD_ROUTER_PROFILES.md",
        "PIPD_ARTIFACT_SCHEMAS.md", "PIPD_EVAL_HANDOFF.md"}
META_RE = re.compile(r"<!--PIPD-DOC-META\s*\n(.*?)\n-->", re.S)


def make_source_root(td: Path) -> Path:
    """A minimal source root: the canonical objects the projector reads."""
    troot = td / "repo"
    (troot / "src" / "pipd_ls_sp").mkdir(parents=True)
    (troot / "fixtures" / "s5_s8").mkdir(parents=True)
    shutil.copytree(ROOT / "schemas", troot / "schemas")
    shutil.copy(ROOT / "src" / "pipd_ls_sp" / "profiles.py",
                troot / "src" / "pipd_ls_sp" / "profiles.py")
    for f in (ROOT / "fixtures" / "s5_s8").iterdir():
        shutil.copy(f, troot / "fixtures" / "s5_s8" / f.name)
    return troot


class WebProjectionTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = Path(self._td.name)
        self.out = self.td / "web"
        P.project_surfaces(ROOT, self.out)

    def tearDown(self):
        self._td.cleanup()

    # ------------------------------------------------------------- positive

    def test_exact_semantic_documents_not_site_ui(self):
        present = {p.name for p in self.out.glob("PIPD_*.md")}
        self.assertEqual(present, DOCS)
        result = P.check_web_surface(ROOT, self.out)
        self.assertEqual(result["verdict"], "PASS", result["first_failing_invariant"])
        self.assertEqual(result["denominator"]["ratio"], "5/5")

    def test_docs_carry_source_objects_schema_version_hash_loss_nack(self):
        for name in sorted(DOCS):
            text = (self.out / name).read_text(encoding="utf-8")
            match = META_RE.search(text)
            self.assertIsNotNone(match, f"{name} has no PIPD-DOC-META block")
            meta = json.loads(match.group(1))
            self.assertEqual(meta["schema"], P.SCHEMA_DOC_META)
            self.assertEqual(meta["schema_version"], P.SCHEMA_VERSION)
            self.assertTrue(meta["source_objects"], f"{name} declares no source objects")
            for ref in meta["source_objects"]:
                for key in ("object_id", "schema", "schema_version", "source_path", "source_hash"):
                    self.assertTrue(ref.get(key), f"{name} source ref missing {key}")
            self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", meta["source_hash"]),
                            f"{name} source hash is not a sha256")
            self.assertTrue(meta["capability_loss"], f"{name} has no CapabilityLoss record")
            self.assertTrue(meta["nack"], f"{name} has no NACK record")
            self.assertEqual(meta["capability_loss"][0]["record_type"], "CapabilityLoss")
            self.assertEqual(meta["nack"][0]["record_type"], "NACK")
            self.assertTrue(meta["denominator"])

    def test_content_derived_from_canonical_objects_not_free_text(self):
        """Cross-check derivation with independent parsing, not via the projector."""
        registry = json.loads((ROOT / "schemas" / "registry.json").read_text(encoding="utf-8"))
        core = (self.out / "PIPD_CANONICAL_CORE.md").read_text(encoding="utf-8")
        schemas_doc = (self.out / "PIPD_ARTIFACT_SCHEMAS.md").read_text(encoding="utf-8")
        for fam in registry["families"]:
            self.assertIn(fam["contract"], core, "canonical core misses a contract family")
            self.assertIn(fam["contract"], schemas_doc)
            schema = json.loads(
                (ROOT / fam["schema_file"]).read_text(encoding="utf-8"))
            self.assertIn(schema["$id"], schemas_doc, "schema doc misses a $id")
            for field in schema.get("required", []):
                self.assertIn(field, schemas_doc)
        prof_text = (ROOT / "src" / "pipd_ls_sp" / "profiles.py").read_text(encoding="utf-8")
        for name in re.findall(r'"(LITE|STANDARD|ASSURED)"', prof_text):
            self.assertIn(name, (self.out / "PIPD_ROUTER_PROFILES.md").read_text(encoding="utf-8"))
        handoff = (self.out / "PIPD_EVAL_HANDOFF.md").read_text(encoding="utf-8")
        for stage in ("S5", "S6", "S7", "S8"):
            self.assertIn(stage, handoff)
        bootstrap = (self.out / "PIPD_BOOTSTRAP.md").read_text(encoding="utf-8")
        self.assertIn("schemas/registry.json", bootstrap)

    def test_optional_site_ui_excluded_from_web_denominator(self):
        ui_dir = self.out / P.UI_DIR
        self.assertEqual(sorted(p.name for p in ui_dir.iterdir() if p.is_file()),
                         sorted(P.UI_FILES))
        result = P.check_web_surface(ROOT, self.out)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["denominator"]["optional_site_ui_excluded"], 5)
        ir = json.loads((self.out / P.IR_FILE).read_text(encoding="utf-8"))
        for art in ir["artifacts"]:
            if art["kind"] == P.UI_KIND:
                self.assertFalse(art["denominator"], "UI pack leaked into the denominator")
        self.assertEqual({a["path"] for a in ir["artifacts"] if a["denominator"]}, DOCS)

    def test_projection_ir_traceable_to_object_schema_version_hash(self):
        ir = json.loads((self.out / P.IR_FILE).read_text(encoding="utf-8"))
        P.validate_projection_ir(ir)
        self.assertEqual(len(ir["artifacts"]), 9)
        index = {r["object_id"]: r for r in ir["source_index"]}
        for art in ir["artifacts"]:
            self.assertTrue(art["source_objects"], art["artifact_id"])
            self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", art["source_hash"]))
            for ref in art["source_objects"]:
                self.assertIn(ref["object_id"], index)
                self.assertEqual(index[ref["object_id"]]["schema"], ref["schema"])
                self.assertEqual(index[ref["object_id"]]["schema_version"], ref["schema_version"])
                self.assertEqual(index[ref["object_id"]]["source_hash"], ref["source_hash"])
            self.assertEqual(art["scope"], ["dist/web/**"])

    def test_stale_source_is_regenerated(self):
        troot = make_source_root(self.td)
        out = self.td / "web2"
        P.project_surfaces(troot, out)
        self.assertEqual(P.check_web_surface(troot, out)["verdict"], "PASS")
        before = (out / "PIPD_ARTIFACT_SCHEMAS.md").read_bytes()
        schema_path = troot / "schemas" / "ArtifactIdentity.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["description"] = "Owner: PIPD. STALE-SOURCE TEST MUTATION."
        schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        stale = P.check_web_surface(troot, out)
        self.assertEqual(stale["verdict"], "FAIL")
        self.assertEqual(stale["first_failing_invariant"].split(":")[0], "STALE_SOURCE")
        P.project_surfaces(troot, out)
        self.assertEqual(P.check_web_surface(troot, out)["verdict"], "PASS")
        self.assertNotEqual(before, (out / "PIPD_ARTIFACT_SCHEMAS.md").read_bytes(),
                            "stale source must be regenerated into the artifact")

    def test_regeneration_is_byte_deterministic(self):
        snap = {p.name: p.read_bytes() for p in sorted(self.out.rglob("*")) if p.is_file()}
        P.project_surfaces(ROOT, self.out)
        again = {p.name: p.read_bytes() for p in sorted(self.out.rglob("*")) if p.is_file()}
        self.assertEqual(snap, again)

    # ------------------------------------------------------------ refusals

    def _codes(self, result):
        self.assertEqual(result["verdict"], "FAIL", "mutation was not refused")
        return [f["code"] for f in result["failures"]]

    def _mutate_meta(self, name, edit):
        path = self.out / name
        text = path.read_text(encoding="utf-8")
        match = META_RE.search(text)
        meta = json.loads(match.group(1))
        edit(meta)
        path.write_text(text.replace(match.group(1), json.dumps(meta, ensure_ascii=False,
                                                                indent=1, sort_keys=True)),
                        encoding="utf-8")

    def test_mut_web_wrongset_ui_files_cannot_pass(self):
        """MUT-WEB-WRONGSET: the site UI five files can never be the Web pack (R-AUD-003)."""
        for name in P.UI_FILES:
            shutil.copy(self.out / P.UI_DIR / name, self.out / name)
        for name in DOCS:
            (self.out / name).unlink()
        result = P.check_web_surface(ROOT, self.out)
        codes = self._codes(result)
        self.assertIn("WRONG_WEB_SET", codes)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "WRONG_WEB_SET")

    def test_mut_web_wrongset_missing_document_refused(self):
        (self.out / "PIPD_CANONICAL_CORE.md").unlink()
        result = P.check_web_surface(ROOT, self.out)
        self.assertIn("WRONG_WEB_SET", self._codes(result))

    def test_mut_web_wrongset_extra_file_is_projection_leak(self):
        (self.out / "EXTRA.md").write_text("leak\n", encoding="utf-8")
        result = P.check_web_surface(ROOT, self.out)
        self.assertIn("WRONG_WEB_SET", self._codes(result))

    def test_mut_empty_payload_refused(self):
        (self.out / "PIPD_BOOTSTRAP.md").write_text("", encoding="utf-8")
        result = P.check_web_surface(ROOT, self.out)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "EMPTY_PAYLOAD")
        ir = json.loads((self.out / P.IR_FILE).read_text(encoding="utf-8"))
        bad = copy.deepcopy(ir)
        bad["artifacts"][0]["payload"] = {}
        with self.assertRaises(P.EmptyPayload):
            P.validate_projection_ir(bad)

    def test_mut_missing_field_refused(self):
        self._mutate_meta("PIPD_CANONICAL_CORE.md", lambda meta: meta.pop("nack"))
        result = P.check_web_surface(ROOT, self.out)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "MISSING_FIELD")
        ir = json.loads((self.out / P.IR_FILE).read_text(encoding="utf-8"))
        bad = copy.deepcopy(ir)
        bad["artifacts"][0].pop("source_hash")
        with self.assertRaises(P.MissingField):
            P.validate_projection_ir(bad)
        bad = copy.deepcopy(ir)
        bad["artifacts"][0]["source_objects"][0].pop("schema_version")
        with self.assertRaises(P.MissingField):
            P.validate_projection_ir(bad)

    def test_mut_scope_widening_refused(self):
        self._mutate_meta("PIPD_CANONICAL_CORE.md", lambda meta: meta.update(scope=["**"]))
        result = P.check_web_surface(ROOT, self.out)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "SCOPE_WIDENING")
        ir = json.loads((self.out / P.IR_FILE).read_text(encoding="utf-8"))
        bad = copy.deepcopy(ir)
        bad["artifacts"][0]["scope"] = ["src/**"]
        with self.assertRaises(P.ScopeWidening):
            P.validate_projection_ir(bad)

    def test_mut_free_text_content_refused(self):
        """Keep the meta block, replace the derived body: content must not be free text."""
        name = "PIPD_EVAL_HANDOFF.md"
        path = self.out / name
        text = path.read_text(encoding="utf-8")
        match = META_RE.search(text)
        path.write_text(text[:match.end()] + "\n\n## Handoff\n\nfree text only\n",
                        encoding="utf-8")
        result = P.check_web_surface(ROOT, self.out)
        codes = self._codes(result)
        self.assertIn("NOT_DERIVED", codes)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "NOT_DERIVED")

    def test_mut_denominator_leak_refused(self):
        self._mutate_meta("PIPD_BOOTSTRAP.md", lambda meta: meta.update(denominator=False))
        result = P.check_web_surface(ROOT, self.out)
        self.assertIn("DENOMINATOR_LEAK", self._codes(result))

    def test_cli_strict_refuses_wrongset(self):
        """The rewritten gate in --strict mode refuses MUT-WEB-WRONGSET as delivered."""
        for name in P.UI_FILES:
            shutil.copy(self.out / P.UI_DIR / name, self.out / name)
        for name in DOCS:
            (self.out / name).unlink()
        receipt = self.td / "receipt.json"
        run = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "web_pack_check.py"), "--strict",
             "--out", str(self.out), "--receipt", str(receipt)],
            capture_output=True, text=True, cwd=str(ROOT),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertNotEqual(run.returncode, 0, "strict web gate accepted the UI five as the pack")
        self.assertIn("MUT-WEB-WRONGSET", run.stdout)
        self.assertTrue(receipt.is_file())


if __name__ == "__main__":
    unittest.main()
