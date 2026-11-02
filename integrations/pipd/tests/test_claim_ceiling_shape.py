"""TYPE5 (R5 §4.1): the five schema-admissible ClaimCeiling shapes must produce NAMED findings.

Before the repair ``schemas/ClaimCeiling.schema.json`` declared both claim lists as bare ``{}`` and
``validate.semantic_invariants`` read them with ``set(...)`` and ``CLAIM_LADDER.index(c)``, so
``allowed_claims: null``, a mapping entry and an undeclared claim name escaped the library as native
``TypeError``/``ValueError`` instead of a typed refusal. These tests pin both halves of the repair:
the schema now types both lists, and the library reports every shape by name while the legal shapes
keep their previous behaviour.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import validate  # noqa: E402

SCHEMAS = ROOT / "schemas"
HASH = "a" * 64


def claim_record(**overrides) -> dict:
    base = {
        "allowed_claims": ["LOCAL_QUALIFIED"],
        "forbidden_escalation": ["RELEASED"],
        "close_conditions": [],
        "subject_id": "PIPD-LS-SP",
        "version": "1.0.0",
        "content_hash": HASH,
        "schema_version": "1.1.0",
    }
    base.update(overrides)
    return base


class ClaimCeilingShapeSemantics(unittest.TestCase):
    """The library half: every shape is a finding, never a native exception."""

    def findings(self, record: dict) -> list[str]:
        return validate.semantic_invariants("ClaimCeiling", record)

    def test_null_allowed_claims_is_a_named_finding(self):
        found = self.findings(claim_record(allowed_claims=None))
        self.assertTrue(any("allowed_claims must be a list" in f for f in found), found)

    def test_null_forbidden_escalation_is_a_named_finding(self):
        found = self.findings(claim_record(forbidden_escalation=None))
        self.assertTrue(any("forbidden_escalation must be a list" in f for f in found), found)

    def test_mapping_entry_is_a_named_finding(self):
        for field in ("allowed_claims", "forbidden_escalation"):
            with self.subTest(field=field):
                found = self.findings(claim_record(**{field: [{"claim": "RELEASED"}]}))
                self.assertTrue(
                    any(f"{field} entries must be declared claim names" in f for f in found), found)

    def test_undeclared_claim_is_a_named_finding(self):
        found = self.findings(claim_record(allowed_claims=["NOT_A_DECLARED_CLAIM"]))
        self.assertTrue(
            any("names the undeclared claim" in f and "NOT_A_DECLARED_CLAIM" in f for f in found),
            found)

    def test_legal_lists_keep_their_previous_behaviour(self):
        self.assertEqual(self.findings(claim_record()), [])
        self.assertEqual(
            self.findings(claim_record(allowed_claims=["HGK_ADMITTED", "LOCAL_QUALIFIED"])), [])

    def test_escalation_still_needs_its_receipts_and_authority(self):
        found = self.findings(claim_record(allowed_claims=["RELEASED"]))
        self.assertTrue(any("receipt" in f.lower() or "authority" in f.lower() for f in found),
                        found)
        self.assertEqual(
            self.findings(claim_record(allowed_claims=["RELEASED"], forbidden_escalation=[],
                                       receipts=["r-1"], authority="independent-checker")), [])

    def test_overlapping_lists_are_still_refused(self):
        found = self.findings(claim_record(allowed_claims=["LOCAL_QUALIFIED"],
                                           forbidden_escalation=["LOCAL_QUALIFIED"]))
        self.assertTrue(any("both allowed and forbidden" in f for f in found), found)


class ClaimCeilingSchemaAdmission(unittest.TestCase):
    """The schema half: the same five shapes are no longer admitted as schema-valid records."""

    def schema_findings(self, record: dict) -> list[str]:
        return validate.validate_record("ClaimCeiling", record, SCHEMAS)

    def test_legal_record_is_schema_valid(self):
        self.assertEqual(self.schema_findings(claim_record()), [])

    def test_null_lists_are_refused_by_the_schema(self):
        for field in ("allowed_claims", "forbidden_escalation"):
            with self.subTest(field=field):
                found = self.schema_findings(claim_record(**{field: None}))
                self.assertTrue(any(field in f for f in found), found)

    def test_mapping_entries_are_refused_by_the_schema(self):
        found = self.schema_findings(claim_record(allowed_claims=[{"claim": "RELEASED"}]))
        self.assertTrue(found, "a mapping entry must not be schema-admissible")

    def test_undeclared_claim_is_refused_by_the_schema(self):
        found = self.schema_findings(claim_record(allowed_claims=["NOT_A_DECLARED_CLAIM"]))
        self.assertTrue(found, "an undeclared claim must not be schema-admissible")


if __name__ == "__main__":
    unittest.main(verbosity=2)
