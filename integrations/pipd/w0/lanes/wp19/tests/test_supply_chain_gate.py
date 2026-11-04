#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-19 gate tests: one positive tree, four negative trees, redaction proof.

Run from the lane root:

    python -m unittest discover -s tests -p "test_*.py" -v

Every assertion is made against the gate's real process exit code and its
on-disk JSON artifact -- the same artifact an operator would read.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(LANE, "supply_chain_gate.py")
FIXTURES = os.path.join(LANE, "fixtures")
TMP_ROOT = os.path.join(LANE, "out", "_unittest_tmp")

CLAIM = "AUTHOR_SUPPLY_CHAIN_LOCAL"
VERDICTS = {"PASS", "FAIL", "HOLD", "NOT_APPLICABLE"}


def run_gate(tree: str, out_name: str):
    """Run the gate as a subprocess. Returns (exit_code, payload, raw_text)."""
    os.makedirs(TMP_ROOT, exist_ok=True)
    out_path = os.path.join(TMP_ROOT, out_name)
    proc = subprocess.run(
        [sys.executable, GATE, "--tree", tree, "--out", out_path, "--mode", "author", "--quiet"],
        cwd=LANE, capture_output=True, text=True, timeout=300,
    )
    raw = ""
    payload = None
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as fh:
            raw = fh.read()
        payload = json.loads(raw)
    return proc.returncode, payload, raw, proc


def check_by_id(payload: dict, check_id: str) -> dict:
    for chk in payload["checks"]:
        if chk["check_id"] == check_id:
            return chk
    raise AssertionError(f"check {check_id} absent from payload")


class GateContractTests(unittest.TestCase):
    """Shape / ceiling contract that must hold for every run."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.payload, cls.raw, cls.proc = run_gate(
            os.path.join(FIXTURES, "pos"), "contract_pos.json")

    def test_exit_code_matches_fail_presence(self):
        has_fail = any(c["verdict"] == "FAIL" for c in self.payload["checks"])
        self.assertEqual(self.code, 1 if has_fail else 0)
        self.assertEqual(self.payload["exit_code"], self.code)

    def test_claim_ceiling_and_negative_claims(self):
        self.assertEqual(self.payload["claim_ceiling"], CLAIM)
        self.assertIs(self.payload["wp19_done"], False)
        self.assertIs(self.payload["trace_closure"], False)

    def test_top_level_schema_fields(self):
        for key in ("schema", "gate_id", "gate_version", "mode", "generated_at_taipei",
                    "tree", "scanned", "checks", "summary", "exit_code", "limits"):
            self.assertIn(key, self.payload)
        self.assertEqual(self.payload["gate_id"], "WP-FHS-19")
        self.assertEqual(self.payload["mode"], "author")
        self.assertEqual(len(self.payload["checks"]), 7)

    def test_every_check_is_typed(self):
        for chk in self.payload["checks"]:
            self.assertIn(chk["verdict"], VERDICTS, chk["check_id"])
            self.assertTrue(chk["code"], chk["check_id"])
            self.assertIsInstance(chk["counts"], dict)
            self.assertIsInstance(chk["samples"], list)

    def test_scan_denominator_non_zero(self):
        self.assertGreater(self.payload["scanned"]["files_total"], 0)
        self.assertGreater(self.payload["scanned"]["bytes_total"], 0)

    def test_summary_adds_up(self):
        s = self.payload["summary"]
        self.assertEqual(s["checks_total"], len(self.payload["checks"]))
        self.assertEqual(s["PASS"] + s["FAIL"] + s["HOLD"] + s["NOT_APPLICABLE"], s["checks_total"])
        self.assertEqual(s["fail_codes"],
                         [c["code"] for c in self.payload["checks"] if c["verdict"] == "FAIL"])


class PositiveTreeTests(unittest.TestCase):
    """fixtures/pos must go all green, exit 0."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.payload, cls.raw, cls.proc = run_gate(
            os.path.join(FIXTURES, "pos"), "pos.json")

    def test_exit_zero(self):
        self.assertEqual(self.code, 0, self.proc.stderr)
        self.assertEqual(self.payload["summary"]["FAIL"], 0)
        self.assertEqual(self.payload["summary"]["fail_codes"], [])

    def test_all_seven_checks_pass(self):
        verdicts = {c["check_id"]: c["verdict"] for c in self.payload["checks"]}
        self.assertEqual(set(verdicts), {
            "LICENSE_PRESENT", "NOTICE_PRESENT", "SBOM_PRESENT_AND_PARSABLE",
            "SBOM_COMPONENT_RECONCILE", "DEPENDENCY_DECLARED",
            "SECRET_PATTERN_SCAN", "CI_ENTRY_PRESENT"})
        for check_id, verdict in verdicts.items():
            self.assertEqual(verdict, "PASS", check_id)

    def test_pos_specific_codes(self):
        self.assertEqual(check_by_id(self.payload, "LICENSE_PRESENT")["code"], "LICENSE_SPDX_RESOLVED")
        self.assertEqual(check_by_id(self.payload, "SBOM_PRESENT_AND_PARSABLE")["code"], "SBOM_PARSED")
        self.assertEqual(check_by_id(self.payload, "SBOM_COMPONENT_RECONCILE")["code"],
                         "SBOM_COMPONENTS_RECONCILED")
        self.assertEqual(check_by_id(self.payload, "DEPENDENCY_DECLARED")["code"], "DEPENDENCIES_DECLARED")
        self.assertEqual(check_by_id(self.payload, "SECRET_PATTERN_SCAN")["code"], "NO_SECRET_PATTERN")
        self.assertEqual(check_by_id(self.payload, "CI_ENTRY_PRESENT")["code"], "CI_ENTRY_WORKFLOW_PRESENT")

    def test_pos_spdx_is_parsed(self):
        self.assertEqual(check_by_id(self.payload, "LICENSE_PRESENT")["counts"]["spdx_resolved"], 1)


class NegativeTreeTests(unittest.TestCase):
    """Each negative tree must go red with exactly one specific code."""

    def _assert_red_for(self, tree: str, check_id: str, code: str, out_name: str):
        exit_code, payload, raw, proc = run_gate(os.path.join(FIXTURES, tree), out_name)
        self.assertEqual(exit_code, 1, f"{tree} must exit 1 (stderr={proc.stderr})")
        self.assertEqual(payload["exit_code"], 1)
        self.assertEqual(payload["summary"]["fail_codes"], [code],
                         f"{tree} fail codes were {payload['summary']['fail_codes']}")
        chk = check_by_id(payload, check_id)
        self.assertEqual(chk["verdict"], "FAIL")
        self.assertEqual(chk["code"], code)
        self.assertEqual(payload["claim_ceiling"], CLAIM)
        self.assertIs(payload["wp19_done"], False)
        self.assertIs(payload["trace_closure"], False)
        return payload, raw

    def test_neg_notice_missing(self):
        payload, _ = self._assert_red_for(
            "neg_notice_missing", "NOTICE_PRESENT", "NOTICE_MISSING", "neg_notice.json")
        self.assertEqual(check_by_id(payload, "NOTICE_PRESENT")["counts"]["notice_files"], 0)

    def test_neg_sbom_component_mismatch(self):
        payload, _ = self._assert_red_for(
            "neg_sbom_mismatch", "SBOM_COMPONENT_RECONCILE", "SBOM_COMPONENT_MISMATCH",
            "neg_sbom.json")
        counts = check_by_id(payload, "SBOM_COMPONENT_RECONCILE")["counts"]
        self.assertGreater(counts["sbom_only"], 0)
        samples = check_by_id(payload, "SBOM_COMPONENT_RECONCILE")["samples"]
        self.assertTrue(any(s.startswith("sbom_only:requests") for s in samples), samples)

    def test_neg_undeclared_dependency(self):
        payload, _ = self._assert_red_for(
            "neg_undeclared_dep", "DEPENDENCY_DECLARED", "UNDECLARED_DEPENDENCY", "neg_dep.json")
        counts = check_by_id(payload, "DEPENDENCY_DECLARED")["counts"]
        self.assertEqual(counts["undeclared_modules"], 1)
        samples = check_by_id(payload, "DEPENDENCY_DECLARED")["samples"]
        self.assertTrue(any("yaml @" in s for s in samples), samples)

    def test_neg_secret_pattern_found(self):
        payload, _ = self._assert_red_for(
            "neg_secret", "SECRET_PATTERN_SCAN", "SECRET_PATTERN_FOUND", "neg_secret.json")
        counts = check_by_id(payload, "SECRET_PATTERN_SCAN")["counts"]
        self.assertGreaterEqual(counts["matches"], 4)
        self.assertGreaterEqual(len(counts["per_pattern"]), 4)


class RedactionTests(unittest.TestCase):
    """No complete credential shape may survive into the artifact."""

    FIXTURE_SECRETS = (
        "github_pat_11AAADUMMYDUMMYDUMMY_0000000000000000000000000000000000000000000",
        "ghp_000000000000000000000000000000000000",
        "AKIAIOSFODNN7EXAMPLE",
    )

    @classmethod
    def setUpClass(cls):
        cls.code, cls.payload, cls.raw, cls.proc = run_gate(
            os.path.join(FIXTURES, "neg_secret"), "redaction_neg_secret.json")

    def test_no_fixture_token_verbatim_in_artifact(self):
        for token in self.FIXTURE_SECRETS:
            self.assertNotIn(token, self.raw, "artifact leaked a full credential shape")

    def test_no_fixture_token_verbatim_in_stdout(self):
        proc = subprocess.run(
            [sys.executable, GATE, "--tree", os.path.join(FIXTURES, "neg_secret"),
             "--out", os.path.join(TMP_ROOT, "redaction_stdout.json"), "--mode", "author"],
            cwd=LANE, capture_output=True, text=True, timeout=300)
        for token in self.FIXTURE_SECRETS:
            self.assertNotIn(token, proc.stdout)
            self.assertNotIn(token, proc.stderr)

    def test_samples_are_masked_and_located(self):
        chk = check_by_id(self.payload, "SECRET_PATTERN_SCAN")
        self.assertTrue(chk["samples"])
        for sample in chk["samples"]:
            self.assertRegex(sample, r"^[^\s]+:\d+ \S+ \S+$")
            literal = sample.split(" ")[-1]
            self.assertIn("***", literal, f"sample not masked: {literal}")
            self.assertLessEqual(len(literal.split("***")[0]), 4,
                                 f"mask kept too much of the secret: {literal}")

    def test_only_prefix_and_location_recorded(self):
        for hit_sample in check_by_id(self.payload, "SECRET_PATTERN_SCAN")["samples"]:
            self.assertNotIn("-----BEGIN RSA PRIVATE KEY-----", hit_sample)

    def test_scan_counts_are_reported(self):
        counts = check_by_id(self.payload, "SECRET_PATTERN_SCAN")["counts"]
        self.assertGreater(counts["files_scanned"], 0)
        self.assertGreater(counts["bytes_scanned"], 0)


class MaskFunctionTests(unittest.TestCase):
    """Unit-level proof of the masking primitive."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, LANE)
        import supply_chain_gate as gate  # noqa: E402  (import after path setup)
        cls.gate = gate

    def test_mask_keeps_four_chars_at_most(self):
        masked = self.gate.mask_secret("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "github_token")
        self.assertTrue(masked.startswith("ghp_"))
        self.assertIn("MASKED", masked)
        self.assertNotIn("ABCDEFGHIJ", masked)

    def test_mask_private_key_header_has_no_material(self):
        masked = self.gate.mask_secret("-----BEGIN RSA PRIVATE KEY-----", "private_key_block")
        self.assertNotIn("RSA", masked)

    def test_normalisation_is_pep503(self):
        self.assertEqual(self.gate.norm_name("PyYAML>=6.0"), "pyyaml")
        self.assertEqual(self.gate.norm_name("jsonschema[format]>=4.0"), "jsonschema")
        self.assertEqual(self.gate.norm_name("typing_extensions"), "typing-extensions")


class UsageErrorTests(unittest.TestCase):
    """Operational errors are exit 2, never conflated with a FAIL verdict."""

    def test_missing_tree_exits_two(self):
        out_path = os.path.join(TMP_ROOT, "missing.json")
        proc = subprocess.run(
            [sys.executable, GATE, "--tree", os.path.join(FIXTURES, "does_not_exist"),
             "--out", out_path, "--mode", "author"],
            cwd=LANE, capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("ERROR", proc.stderr)

    def test_unknown_mode_rejected_by_argparse(self):
        proc = subprocess.run(
            [sys.executable, GATE, "--tree", os.path.join(FIXTURES, "pos"),
             "--out", os.path.join(TMP_ROOT, "x.json"), "--mode", "protected"],
            cwd=LANE, capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 2)


class BranchTests(unittest.TestCase):
    """Degenerate trees exercise the FAIL/HOLD branches the fixtures do not reach."""

    def _tree(self, name: str, files: dict) -> str:
        root = os.path.join(TMP_ROOT, "branches", name)
        for rel, text in files.items():
            path = os.path.join(root, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        os.makedirs(root, exist_ok=True)
        return root

    def _run_tree(self, name: str, files: dict):
        root = self._tree(name, files)
        return run_gate(root, f"branch_{name}.json")

    def test_empty_tree_is_all_red_not_crash(self):
        code, payload, _, proc = self._run_tree("empty", {})
        self.assertEqual(code, 1, proc.stderr)
        codes = {c["check_id"]: c["code"] for c in payload["checks"]}
        self.assertEqual(codes["LICENSE_PRESENT"], "LICENSE_MISSING")
        self.assertEqual(codes["SBOM_PRESENT_AND_PARSABLE"], "SBOM_MISSING")
        self.assertEqual(codes["DEPENDENCY_DECLARED"], "NO_PYTHON_SOURCES")
        self.assertEqual(codes["SECRET_PATTERN_SCAN"], "NO_READABLE_TEXT_FILES")
        self.assertEqual(codes["CI_ENTRY_PRESENT"], "CI_ENTRY_MISSING")
        self.assertEqual(payload["scanned"]["files_total"], 0)

    def test_unparsable_sbom(self):
        code, payload, _, _ = self._run_tree("badjson", {
            "LICENSE": "SPDX-License-Identifier: MIT\n",
            "NOTICE": "x\n",
            "SBOM.cdx.json": "{not json at all",
        })
        self.assertEqual(code, 1)
        chk = check_by_id(payload, "SBOM_PRESENT_AND_PARSABLE")
        self.assertEqual((chk["verdict"], chk["code"]), ("FAIL", "SBOM_UNPARSABLE"))

    def test_sbom_with_wrong_bom_format(self):
        code, payload, _, _ = self._run_tree("wrongbom", {
            "LICENSE": "SPDX-License-Identifier: MIT\n",
            "NOTICE": "x\n",
            "SBOM.cdx.json": json.dumps({"bomFormat": "SPDX", "specVersion": "2.3",
                                         "components": [{"name": "a", "version": "1"}]}),
        })
        self.assertEqual(code, 1)
        chk = check_by_id(payload, "SBOM_PRESENT_AND_PARSABLE")
        self.assertEqual((chk["verdict"], chk["code"]), ("FAIL", "SBOM_SCHEMA_INVALID"))

    def test_licence_without_spdx_is_hold_not_guess(self):
        code, payload, _, _ = self._run_tree("nospdx", {
            "LICENSE": "You may use this software however you like.\n",
            "NOTICE": "x\n",
        })
        chk = check_by_id(payload, "LICENSE_PRESENT")
        self.assertEqual((chk["verdict"], chk["code"]), ("HOLD", "LICENSE_SPDX_UNPARSED"))
        self.assertEqual(check_by_id(payload, "NOTICE_PRESENT")["verdict"], "PASS")

    def test_documented_ci_entry_counts_as_pass(self):
        code, payload, _, _ = self._run_tree("docci", {
            "LICENSE": "SPDX-License-Identifier: MIT\n",
            "NOTICE": "x\n",
            "README.md": "Re-run:\n\n```\npython -m unittest discover -s tests -v\n```\n",
        })
        chk = check_by_id(payload, "CI_ENTRY_PRESENT")
        self.assertEqual((chk["verdict"], chk["code"]), ("PASS", "CI_ENTRY_DOCUMENTED_COMMAND"))


def tearDownModule():
    if os.path.isdir(TMP_ROOT):
        shutil.rmtree(TMP_ROOT, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
