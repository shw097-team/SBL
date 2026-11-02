"""Tests for the 32 SPEC + 25 DEL crosswalk (tools/build_spec_del_crosswalk.py)."""
from __future__ import annotations

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import tools.build_spec_del_crosswalk as xwalk  # noqa: E402

OUT_PATH = os.path.join(ROOT, "docs", "SPEC_DEL_CROSSWALK.json")


class SpecDelCrosswalkTests(unittest.TestCase):
    def test_counts_are_exactly_32_and_25(self):
        rows = xwalk.build_rows()
        specs = [r for r in rows if r["kind"] == "SPEC"]
        dels = [r for r in rows if r["kind"] == "DEL"]
        self.assertEqual(len(specs), 32)
        self.assertEqual(len(dels), 25)
        self.assertEqual(
            [r["id"] for r in specs],
            [f"PIPD-SP-SPEC-{i:03d}" for i in range(1, 33)],
        )
        self.assertEqual([r["id"] for r in dels], [f"DEL-{i:03d}" for i in range(1, 26)])

    def test_every_evidence_ref_exists_and_evidenced_rows_have_oracle(self):
        for r in xwalk.build_rows():
            for ref in r["evidence_refs"]:
                self.assertTrue(
                    os.path.exists(os.path.join(ROOT, ref)),
                    f"{r['id']}: missing evidence_ref {ref}",
                )
            if r["status"] == "EVIDENCED":
                self.assertTrue(r["oracle"], f"{r['id']}: EVIDENCED row without oracle")

    def test_check_fails_when_evidenced_row_gets_nonexistent_evidence(self):
        # Baseline check is clean.
        self.assertEqual(xwalk.check_rows(xwalk.build_rows()), [])

        original_build = xwalk.build_rows

        def mutated_rows():
            rows = original_build()
            for r in rows:
                if r["id"] == "PIPD-SP-SPEC-001":
                    self.assertEqual(r["status"], "EVIDENCED")
                    r["evidence_refs"] = ["does/not/exist/mutation.json"]
            return rows

        xwalk.build_rows = mutated_rows
        try:
            rc = xwalk.main(["--check"])
        finally:
            xwalk.build_rows = original_build
        self.assertNotEqual(rc, 0)

    def test_check_fails_when_evidenced_row_oracle_is_nonexistent(self):
        # W9 / finding A3: replacing an EVIDENCED row's oracle with a non-existent path must be a
        # violation, not silently accepted.
        self.assertEqual(xwalk.check_rows(xwalk.build_rows()), [])

        original_build = xwalk.build_rows

        def mutated_rows():
            rows = original_build()
            for r in rows:
                if r["id"] == "PIPD-SP-SPEC-001":
                    self.assertEqual(r["status"], "EVIDENCED")
                    r["oracle"] = "tests/ORACLE_DOES_NOT_EXIST.py"
            return rows

        xwalk.build_rows = mutated_rows
        try:
            rc = xwalk.main(["--check"])
        finally:
            xwalk.build_rows = original_build
        self.assertNotEqual(rc, 0)

    def test_design_only_rows_are_never_reported_as_pass(self):
        design_only = [r for r in xwalk.build_rows() if r["status"] == "DESIGN_ONLY"]
        self.assertTrue(design_only, "expected S5/S6 seam rows to be DESIGN_ONLY")
        for r in design_only:
            self.assertNotEqual(r["status"], "PASS")
            self.assertNotEqual(r["oracle"], "PASS")
            self.assertTrue(r["first_fail"], f"{r['id']}: DESIGN_ONLY without reason")


if __name__ == "__main__":
    unittest.main()
