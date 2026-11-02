"""Oracle for the DEL-015 and PIPD-SP-SPEC-030 crosswalk rows (round R10).

A crosswalk row may only be EVIDENCED when its object AND an oracle exist. This module is that oracle:
it RE-DERIVES both artefacts from their sources and asserts the specific claims the rows rest on,
rather than asserting that a file is present.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class AdapterRegistryOracle(unittest.TestCase):
    """DEL-015 / ADAPTER_REGISTRY@1."""

    def test_registry_matches_its_canonical_source(self):
        sys.path.insert(0, str(ROOT / "src"))
        from pipd_ls_sp.projection import ADAPTER_MAPPING
        from pipd_ls_sp.util import canonical_json, sha256_text

        reg = json.loads((ROOT / ".hgk/artifacts/s3/ADAPTER_REGISTRY.json").read_text(encoding="utf-8"))
        self.assertEqual(reg["source"]["sha256"], sha256_text(canonical_json(ADAPTER_MAPPING)))
        self.assertEqual(reg["counts"]["materialised"], 3)
        self.assertEqual(reg["counts"]["live"], 0)
        # the declared-but-not-installed surface must be STATED, not omitted
        self.assertEqual(reg["counts"]["declared_not_installed"], 22)
        self.assertTrue(all(r["source_hash"] is None for r in reg["adapters_declared_not_installed"]))

    def test_artefacts_are_reproducible(self):
        p = subprocess.run([sys.executable, "-B", str(ROOT / "tools/build_bclass_artifacts.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


class McpStateOracle(unittest.TestCase):
    """PIPD-SP-SPEC-030 / MCP materialization state."""

    def test_record_states_an_absence_and_claims_no_schema(self):
        rec = json.loads((ROOT / ".hgk/artifacts/s2/MCP_MATERIALIZATION_DECISION.json").read_text(encoding="utf-8"))
        self.assertIsNone(rec["schema"])
        self.assertFalse(rec["claims_schema_authority"])
        self.assertFalse(rec["canonical"])
        self.assertFalse(rec["materialized"])
        self.assertEqual(rec["materialized_count"], 0)

    def test_absence_is_corroborated_by_the_canonical_admissions_record(self):
        adm = json.loads((ROOT / ".hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json").read_text(encoding="utf-8"))
        cands = adm.get("candidates", adm.get("admissions", []))
        mcp = [c for c in cands if "MCP" in str(c.get("external_name") or "").upper()]
        self.assertEqual(len(mcp), 1, "expected exactly one MCP admission record")
        self.assertEqual(mcp[0]["adapter_materialization_state"], "DESIGN_CONTRACT_SPECIFIED_NOT_INSTALLED")
        self.assertEqual(mcp[0]["current_runtime_state"], "NOT_EXECUTED")
        self.assertFalse(mcp[0].get("reported_active", False))


if __name__ == "__main__":
    unittest.main()
