"""S0: exact 19/19 machine-contract family tests (positive + negative)."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import registry, validate  # noqa: E402


class TestS0Contracts(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = registry.load_registry(ROOT / "schemas")

    def test_exact_19_identity_and_order(self) -> None:
        names = [f["contract"] for f in self.reg["families"]]
        self.assertEqual(len(names), 19, "exact-set must be 19/19")
        self.assertEqual(len(set(names)), 19, "no duplicates")
        self.assertEqual(names, registry.SOURCE_ORDER, "order must match §7.3")

    def test_every_schema_is_draft_2020_12_and_closed(self) -> None:
        for f in self.reg["families"]:
            schema = json.loads((ROOT / "schemas" / f"{f['contract']}.schema.json").read_text(encoding="utf-8"))
            self.assertIn("2020-12", schema.get("$schema", ""), f["contract"])
            self.assertFalse(schema.get("additionalProperties", True), f["contract"])
            self.assertEqual(schema.get("type"), "object")

    def test_registry_fields_are_enforced_by_schema(self) -> None:
        for f in self.reg["families"]:
            schema = json.loads((ROOT / "schemas" / f"{f['contract']}.schema.json").read_text(encoding="utf-8"))
            missing = set(f["required_fields"]) - set(schema.get("required", []))
            self.assertFalse(missing, f"{f['contract']} does not enforce {sorted(missing)}")

    def test_seam_only_materialization(self) -> None:
        mats = {f["contract"]: f["materialization"] for f in self.reg["families"]}
        self.assertEqual(mats["GENIEProjectionRef"], "SCHEMA_SEAM_ONLY_UNTIL_S6")
        self.assertEqual(mats["ExecutionBindingRef"], "SCHEMA_SEAM_ONLY_UNTIL_S5")
        self.assertEqual(mats["WorkOrderCandidate"], "REQUIRED_NOW_NONAUTHORITY")

    def test_a_twentieth_family_is_rejected(self) -> None:
        reg = json.loads(json.dumps(self.reg))
        reg["families"].append({"contract": "Invented", "required_fields": ["a"]})
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "registry.json").write_text(json.dumps(reg), encoding="utf-8", newline="")
            with self.assertRaises(registry.ValidationFail):
                registry.load_registry(Path(td))

    def test_negative_missing_schema_file_is_rejected(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            reg = json.loads(json.dumps(self.reg))
            for f in reg["families"]:
                (Path(td) / f"{f['contract']}.schema.json").write_text("{}", encoding="utf-8", newline="")
            reg["families"][0]["contract"] = "Renamed"
            (Path(td) / "registry.json").write_text(json.dumps(reg), encoding="utf-8", newline="")
            with self.assertRaises(registry.ValidationFail):
                registry.load_registry(Path(td))


class TestS0Reconciliation(unittest.TestCase):
    def run_check(self, mutate=None, flag="--check"):
        import os
        import shutil
        import subprocess
        import tempfile
        receipt = ROOT / ".hgk/rounds/R3-20261009-audit-repair/FW-02"
        receipt.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=receipt) as td:
            schemas = Path(td) / "schemas"
            shutil.copytree(ROOT / "schemas", schemas)
            if mutate:
                mutate(schemas)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            return subprocess.run(
                [sys.executable, str(ROOT / "tools/registry_reconcile.py"),
                 flag, "--schemas-dir", str(schemas)],
                capture_output=True, text=True, env=env)

    @staticmethod
    def edit(schemas, family, change):
        path = schemas / f"{family}.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        change(schema)
        path.write_text(json.dumps(schema), encoding="utf-8")

    def test_all_19_are_field_exact(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("19/19", result.stdout)
        for family in registry.SOURCE_ORDER:
            schema = registry.load_schema(family, ROOT / "schemas")
            row = next(f for f in registry.load_registry(ROOT / "schemas")["families"]
                       if f["contract"] == family)
            self.assertEqual(set(row["required_fields"]), set(schema["required"]), family)

    def test_required_field_removal_is_refused(self):
        for flag in ("--check", "--write"):
            result = self.run_check(lambda d: self.edit(d, "TechnologyAdmission",
                lambda s: s["required"].remove("immutable_pin")), flag)
            self.assertNotEqual(result.returncode, 0, "TechnologyAdmission immutable_pin accepted")
            self.assertIn("TechnologyAdmission", result.stderr)
            self.assertIn("immutable_pin", result.stderr)

    def test_version_id_mismatch_is_refused(self):
        result = self.run_check(lambda d: self.edit(d, "TechnologyAdmission",
            lambda s: s.update({"$id": "urn:pipd:s0:TechnologyAdmission:2"})))
        self.assertNotEqual(result.returncode, 0, "TechnologyAdmission $id accepted")
        self.assertIn("TechnologyAdmission", result.stderr)
        self.assertIn("$id", result.stderr)

    def test_wrong_owner_or_consumer_is_refused(self):
        for key in ("owner", "consumers"):
            result = self.run_check(lambda d: self.edit(d, "TechnologyAdmission",
                lambda s: s["x-s0"].update({key: "Wrong" if key == "owner" else ["Wrong"]})))
            self.assertNotEqual(result.returncode, 0, f"TechnologyAdmission {key} accepted")
            self.assertIn("TechnologyAdmission", result.stderr)
            self.assertIn(key, result.stderr)

    def test_extra_schema_family_is_refused(self):
        result = self.run_check(lambda d: (d / "Invented.schema.json").write_text("{}", encoding="utf-8"))
        self.assertNotEqual(result.returncode, 0, "Invented twentieth family accepted")
        self.assertIn("Invented", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
