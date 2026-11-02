"""WO-S4-CONTRACT-HARDEN-03 (S4-R2): type the residual ProfileBinding contract fields.

Finding ``F-S4R2-NEW-01``: in ``schemas/ProfileBinding.schema.json`` the five decision-carrying
properties ``profile``, ``axes``, ``vetoes``, ``artifact_depth`` and ``assurance`` were still the
empty schema ``{}``, so ``validate_record`` accepted ANY JSON value for them. The pins below prove
each measured counterexample is now a typed SCHEMA refusal that names the offending field, that a
legal record the compiler actually emits still passes, and that the exact 19/19 set and the earlier
profile-contract tests did not regress.

Decision recorded here (brief step 1): the real axis vocabulary is ``profiles.AXES``; ``axes`` is
typed as an array whose items are drawn from that vocabulary with ``uniqueItems: true`` and
``minItems: 1``. The runtime duplicate/non-string/empty refusals in ``compute_profile()`` -
``ProfileVeto`` - are KEPT (never removed); the schema additionally refuses a double-counted axis at
the record boundary so the two layers agree instead of one silently accepting what the other vetoes.

Self-bootstrap (same rule as every test file here): runnable standalone.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, profiles, registry, validate  # noqa: E402

SCHEMAS_DIR = ROOT / "schemas"
CONTRACT = "ProfileBinding"

# The real axis vocabulary, read from the code (never invented).
AXES = list(profiles.AXES)
PROFILE_NAMES = sorted(profiles.PROFILES)
ARTIFACT_DEPTHS = sorted({cfg["artifact_depth"] for cfg in profiles.PROFILES.values()})
ASSURANCE = sorted({a for cfg in profiles.PROFILES.values() for a in cfg["assurance"]})


def _legal_record(name: str = "LITE", axes: list | None = None) -> dict:
    """A ProfileBinding record the COMPILER actually emits (never hand-written)."""
    rec, _full = pipeline.profile_record(name, axes if axes is not None else ["intent"])
    return json.loads(json.dumps(rec))


def _findings(record: dict) -> list[str]:
    return validate.validate_record(CONTRACT, record, SCHEMAS_DIR)


class NegativeCounterexampleTests(unittest.TestCase):
    """Each measured counterexample must become a typed refusal naming the offending field."""

    def _refused(self, field: str, value: object, pointer_token: str | None = None) -> None:
        rec = _legal_record()
        rec[field] = value
        findings = _findings(rec)
        self.assertTrue(findings, f"{field}={value!r} must be refused")
        needle = pointer_token or f"{CONTRACT}/{field}"
        self.assertTrue(any(needle in f for f in findings),
                        f"the refusal must name {needle}: {findings}")

    def test_axes_as_string_is_refused(self) -> None:
        self._refused("axes", "intent")

    def test_axes_with_non_string_member_is_refused(self) -> None:
        self._refused("axes", ["intent", 7], pointer_token=f"{CONTRACT}/axes/1")

    def test_profile_as_integer_is_refused(self) -> None:
        self._refused("profile", 7)

    def test_vetoes_as_string_is_refused(self) -> None:
        self._refused("vetoes", "none")

    def test_unknown_axis_is_refused(self) -> None:
        # An axis outside the real vocabulary is a schema refusal, not a silent acceptance.
        self._refused("axes", ["not_a_real_axis"], pointer_token=f"{CONTRACT}/axes/0")

    def test_duplicate_axis_is_refused_at_the_record_boundary(self) -> None:
        # Decision: duplicates are ALSO a schema-level refusal (uniqueItems), while the runtime
        # ProfileVeto in compute_profile() stays in place. Prove both layers.
        self._refused("axes", ["intent", "intent"])
        with self.assertRaises(profiles.ProfileVeto):
            profiles.compute_profile("LITE", axes=["intent", "intent"])

    def test_bad_artifact_depth_is_refused(self) -> None:
        self._refused("artifact_depth", "L2_MADE_UP")

    def test_assurance_as_string_is_refused(self) -> None:
        self._refused("assurance", "deterministic_validator")

    def test_unknown_assurance_value_is_refused(self) -> None:
        self._refused("assurance", ["not_a_real_assurance"], pointer_token=f"{CONTRACT}/assurance/0")


class PositiveLegalRecordTests(unittest.TestCase):
    """Every legal record the compiler emits still validates (no over-narrowing)."""

    def test_legal_lite_record_passes(self) -> None:
        self.assertEqual(_findings(_legal_record("LITE", ["intent"])), [])

    def test_legal_records_for_all_three_profiles_pass(self) -> None:
        cases = {
            "LITE": ["intent"],
            "STANDARD": ["intent", "verification", "knowledge"],
            "ASSURED": list(AXES),
        }
        for name, axes in cases.items():
            with self.subTest(profile=name):
                self.assertEqual(_findings(_legal_record(name, axes)), [])

    def test_vetoes_empty_list_is_legal(self) -> None:
        rec = _legal_record()
        rec["vetoes"] = []
        self.assertEqual(_findings(rec), [])


class DerivedVocabularyTests(unittest.TestCase):
    """The typed enums equal the values the code actually defines (no invented names)."""

    def test_schema_enums_match_the_code(self) -> None:
        schema = json.loads((SCHEMAS_DIR / f"{CONTRACT}.schema.json").read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(sorted(props["axes"]["items"]["enum"]), sorted(AXES))
        self.assertEqual(sorted(props["profile"]["enum"]), PROFILE_NAMES)
        self.assertEqual(sorted(props["artifact_depth"]["enum"]), ARTIFACT_DEPTHS)
        self.assertEqual(sorted(props["assurance"]["items"]["enum"]), ASSURANCE)
        self.assertTrue(props["axes"].get("uniqueItems"))
        self.assertEqual(props["vetoes"]["type"], "array")

    def test_risk_assessment_is_not_widened_into_the_contract(self) -> None:
        schema = json.loads((SCHEMAS_DIR / f"{CONTRACT}.schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("risk_assessment", schema["properties"])
        # The schema's additionalProperties must stay false exactly as before this round.
        self.assertIs(schema.get("additionalProperties"), False)


class ExactSetRegressionTests(unittest.TestCase):
    """The 19-schema exact set is still exactly 19 and unchanged in count."""

    def test_exact_set_is_still_nineteen(self) -> None:
        reg = registry.load_registry(SCHEMAS_DIR)
        names = [f["contract"] for f in reg["families"]]
        self.assertEqual(len(names), 19)
        self.assertEqual(len(set(names)), 19)
        self.assertEqual(names, registry.SOURCE_ORDER)

    def test_profile_binding_is_still_index_04_and_field_exact(self) -> None:
        schema = json.loads((SCHEMAS_DIR / f"{CONTRACT}.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:pipd:s0:ProfileBinding:1")
        self.assertEqual(schema["x-s0"]["index"], "04")
        row = next(f for f in registry.load_registry(SCHEMAS_DIR)["families"]
                   if f["contract"] == CONTRACT)
        self.assertEqual(set(row["required_fields"]), set(schema["required"]))

    def test_no_twentieth_schema_file_appeared(self) -> None:
        files = sorted(p.name for p in SCHEMAS_DIR.glob("*.schema.json"))
        self.assertEqual(len(files), 19, files)


class ExistingProfileTestsRegressionTests(unittest.TestCase):
    """The existing profile-contract tests still pass on the pinned interpreter."""

    MODULES = ("tests.test_s0_contracts", "tests.test_postrelease_contract_hardening")

    def test_existing_profile_contract_tests_still_pass(self) -> None:
        import os
        present = [m for m in self.MODULES
                   if (ROOT / (m.replace(".", "/") + ".py")).is_file()]
        self.assertTrue(present, "expected the profile-contract test modules to exist")
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src"),
               "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run([sys.executable, "-m", "unittest", *present, "-v"],
                                cwd=str(ROOT), capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
