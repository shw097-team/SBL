"""FW-06 (R-AUD-004) + R-AUD-015: host projection regressions.

Positive path: the three hosts each carry a field-level contract, source
references, compatibility + capability-loss and an effective-load result a
marker-only stub cannot satisfy — generic-skills a genuinely loadable skill
projection, hgk-receiver a real typed receiver map, genie-adapter a real object
crosswalk. S5/S6 are NOT authorised: checks use fixture/mock contracts and must
never report a live HGK/GENIE integration PASS.

Refusal mutations: MUT-HOST-STUB, MUT-HOST-PROVIDER-OFF, MUT-HOST-UNSUPPORTED,
MUT-HOST-PERMISSION-WIDENING, MUT-HOST-MISSING-MAPPING, plus MUT-MISSING-FIELD,
MUT-EMPTY-PAYLOAD, MUT-SCOPE-WIDENING, MUT-STALE-SOURCE.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pipd_ls_sp import projection as P

RECORD_RE = re.compile(r"<!--PIPD-HOST-RECORD\s*\n(.*?)\n-->", re.S)
HOST_ENTRY = {"host_generic-skills": "SKILL.md",
              "host_hgk-receiver": "receiver-map.json",
              "host_genie-adapter": "object-crosswalk.json"}


class HostProjectionTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = Path(self._td.name)
        self.out = self.td / "web"
        P.project_surfaces(ROOT, self.out)

    def tearDown(self):
        self._td.cleanup()

    # ------------------------------------------------------------- positive

    def test_three_host_projections_effective_load(self):
        result = P.check_host_surfaces(ROOT, self.out)
        self.assertEqual(result["verdict"], "PASS", result["first_failing_invariant"])
        self.assertEqual(result["host_count"], "3/3")
        loaders = {}
        for row in result["rows"]:
            self.assertTrue(row["effective_load"], row["host"])
            self.assertTrue(row["resolved"], "effective load must resolve, not just read")
            loaders[row["host"]] = row["loader"]
        self.assertEqual(loaders, {"host:generic-skills": "skill_projection_v1",
                                   "host:hgk-receiver": "receiver_map_v1",
                                   "host:genie-adapter": "object_crosswalk_v1"})

    def test_hosts_carry_field_contract_source_refs_compat_loss_nack(self):
        for dir_name, entry in HOST_ENTRY.items():
            record = self._read_record(dir_name)
            self.assertEqual(record["schema"], P.SCHEMA_HOST_RECORD)
            self.assertTrue(record["field_contract"], f"{dir_name} has no field contract")
            for row in record["field_contract"]:
                for key in ("name", "type", "required", "source_object_id"):
                    self.assertIn(key, row, f"{dir_name} field contract missing {key}")
                self.assertIn(row["type"], P.TYPE_VOCAB)
            self.assertTrue(record["source_refs"], f"{dir_name} has no source references")
            for ref in record["source_refs"]:
                for key in ("object_id", "schema", "schema_version", "source_path", "source_hash"):
                    self.assertTrue(ref.get(key), f"{dir_name} source ref missing {key}")
            compat = record["compatibility"]
            self.assertEqual(compat["mode"], "FIXTURE_MOCK")
            self.assertEqual(compat["live_status"], "NOT_RUN")
            self.assertTrue(record["capability_loss"], f"{dir_name} has no capability loss")
            self.assertTrue(record["nack"], f"{dir_name} has no NACK record")
            self.assertEqual(record["capability_loss"][0]["record_type"], "CapabilityLoss")
            self.assertEqual(record["nack"][0]["record_type"], "NACK")
            self.assertFalse(record["provider"]["live_integration"])

    def test_semantic_parity_and_no_live_integration_claim(self):
        result = P.check_host_surfaces(ROOT, self.out)
        self.assertEqual(result["semantic_parity"], "PASS")
        self.assertEqual(result["claims"]["live_hgk_genie_integration"], "NOT_CLAIMED")
        self.assertEqual(result["claims"]["s5_s6"], "NOT_AUTHORISED")
        self.assertEqual(result["claims"]["live_status"], "NOT_RUN")
        for surface, compat in result["compatibility"].items():
            self.assertEqual(compat["live_status"], "NOT_RUN",
                             f"{surface} must not report a live integration status")
            self.assertEqual(compat["mode"], "FIXTURE_MOCK",
                             f"{surface} must load fixture/mock contracts only")
        for row in result["rows"]:
            self.assertIn(row["host"], result["compatibility"])

    def test_typed_receiver_map_and_object_crosswalk_payloads(self):
        receiver = self._read_record("host_hgk-receiver")["payload"]
        self.assertEqual(receiver["abi_version"], "PIPD-HGK-RECEIVER-ABI/1")
        self.assertGreaterEqual(len(receiver["receivers"]), 3)
        for entry in receiver["receivers"]:
            self.assertTrue(entry["fields"])
            for field in entry["fields"]:
                self.assertIn(field["type"], P.TYPE_VOCAB)
        crosswalk = self._read_record("host_genie-adapter")["payload"]
        targets = {m["target"] for m in crosswalk["mappings"]}
        self.assertEqual(targets, {"ProductGraph", "Profile", "Bundle", "GENIEArtifact"})
        for mapping in crosswalk["mappings"]:
            self.assertEqual(mapping["direction"], "REFERENCE_ONLY", "no truth writeback")

    # ------------------------------------------------------------ refusals

    def _read_record(self, dir_name):
        path = self.out / dir_name / HOST_ENTRY[dir_name]
        text = path.read_text(encoding="utf-8")
        if dir_name == "host_generic-skills":
            return json.loads(RECORD_RE.search(text).group(1))
        return json.loads(text)

    def _write_record(self, dir_name, record):
        path = self.out / dir_name / HOST_ENTRY[dir_name]
        if dir_name == "host_generic-skills":
            text = path.read_text(encoding="utf-8")
            match = RECORD_RE.search(text)
            path.write_text(text.replace(match.group(1), json.dumps(record, ensure_ascii=False,
                                                                    indent=1, sort_keys=True)),
                            encoding="utf-8")
        else:
            path.write_text(json.dumps(record, ensure_ascii=False, indent=1, sort_keys=True)
                            + "\n", encoding="utf-8")

    def _mutate(self, dir_name, edit):
        record = self._read_record(dir_name)
        edit(record)
        self._write_record(dir_name, record)

    def _codes(self, result):
        self.assertEqual(result["verdict"], "FAIL", "mutation was not refused")
        return [f["code"] for f in result["failures"]]

    def test_mut_host_stub_marker_only_refused(self):
        """MUT-HOST-STUB: a marker-only stub must never count as an effective load."""
        (self.out / "host_hgk-receiver" / "receiver-map.json").write_text(
            json.dumps({"surface": "host:hgk-receiver"}) + "\n", encoding="utf-8")
        result = P.check_host_surfaces(ROOT, self.out)
        codes = self._codes(result)
        self.assertIn("MARKER_ONLY_STUB", codes)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "MARKER_ONLY_STUB")
        row = {r["host"]: r for r in result["rows"]}["host:hgk-receiver"]
        self.assertFalse(row["effective_load"])
        self.assertIsNone(row["resolved"], "a stub must resolve nothing")
        # the same stub shape against the skill host
        (self.out / "host_generic-skills" / "SKILL.md").write_text(
            "# stub\n\n" + json.dumps({"surface": "host:generic-skills"}) + "\n",
            encoding="utf-8")
        result2 = P.check_host_surfaces(ROOT, self.out)
        self.assertIn("MARKER_ONLY_STUB", self._codes(result2))

    def test_mut_provider_off_refused(self):
        """Mutating the provider claim while the provider is off must FAIL."""
        self._mutate("host_hgk-receiver",
                     lambda r: r["provider"].update(admission_state="ACTIVE",
                                                    live_integration=True))
        result = P.check_host_surfaces(ROOT, self.out)
        codes = self._codes(result)
        self.assertIn("PROVIDER_OFF", codes)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "PROVIDER_OFF")

    def test_mut_live_status_claim_refused(self):
        self._mutate("host_genie-adapter",
                     lambda r: r["compatibility"].update(live_status="PASS"))
        result = P.check_host_surfaces(ROOT, self.out)
        self.assertIn("PROVIDER_OFF", self._codes(result))

    def test_mut_unsupported_host_refused(self):
        (self.out / "host_evil").mkdir()
        (self.out / "host_evil" / "x.json").write_text("{}", encoding="utf-8")
        result = P.check_host_surfaces(ROOT, self.out)
        codes = self._codes(result)
        self.assertIn("UNSUPPORTED_HOST", codes)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "UNSUPPORTED_HOST")
        self._mutate("host_hgk-receiver", lambda r: r.update(surface="host:not-a-host"))
        result2 = P.check_host_surfaces(ROOT, self.out)
        self.assertIn("UNSUPPORTED_HOST", self._codes(result2))

    def test_mut_permission_widening_refused(self):
        self._mutate("host_genie-adapter",
                     lambda r: r["permissions"].append("repo:write"))
        result = P.check_host_surfaces(ROOT, self.out)
        codes = self._codes(result)
        self.assertIn("PERMISSION_WIDENING", codes)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "PERMISSION_WIDENING")

    def test_mut_missing_required_mapping_refused(self):
        def drop_profile(record):
            record["payload"]["mappings"] = [
                m for m in record["payload"]["mappings"] if m["target"] != "Profile"]
        self._mutate("host_genie-adapter", drop_profile)
        result = P.check_host_surfaces(ROOT, self.out)
        codes = self._codes(result)
        self.assertIn("MISSING_REQUIRED_MAPPING", codes)
        self.assertEqual(result["first_failing_invariant"].split(":")[0],
                         "MISSING_REQUIRED_MAPPING")
        def drop_receiver(record):
            record["payload"]["receivers"] = record["payload"]["receivers"][:1]
        self._mutate("host_hgk-receiver", drop_receiver)
        result2 = P.check_host_surfaces(ROOT, self.out)
        self.assertIn("MISSING_REQUIRED_MAPPING", self._codes(result2))

    def test_mut_missing_field_refused(self):
        self._mutate("host_hgk-receiver", lambda r: r.pop("compatibility"))
        result = P.check_host_surfaces(ROOT, self.out)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "MISSING_FIELD")
        self._mutate("host_genie-adapter", lambda r: r["field_contract"].pop())
        result2 = P.check_host_surfaces(ROOT, self.out)
        self.assertIn("MISSING_FIELD", self._codes(result2))

    def test_mut_empty_payload_refused(self):
        (self.out / "host_genie-adapter" / "object-crosswalk.json").write_text(
            "", encoding="utf-8")
        result = P.check_host_surfaces(ROOT, self.out)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "EMPTY_PAYLOAD")
        self._mutate("host_hgk-receiver",
                     lambda r: r["payload"].update(receivers=[]))
        result2 = P.check_host_surfaces(ROOT, self.out)
        self.assertIn("EMPTY_PAYLOAD", self._codes(result2))

    def test_mut_scope_widening_refused(self):
        self._mutate("host_hgk-receiver", lambda r: r.update(scope=["**"]))
        result = P.check_host_surfaces(ROOT, self.out)
        self.assertEqual(result["first_failing_invariant"].split(":")[0], "SCOPE_WIDENING")

    def test_mut_stale_source_refused(self):
        def stale(record):
            record["source_refs"][0]["source_hash"] = "0" * 64
        self._mutate("host_hgk-receiver", stale)
        result = P.check_host_surfaces(ROOT, self.out)
        self.assertIn("STALE_SOURCE", self._codes(result))

    def test_cli_strict_refuses_stub(self):
        """The rewritten gate in --strict mode refuses MUT-HOST-STUB as delivered."""
        (self.out / "host_hgk-receiver" / "receiver-map.json").write_text(
            json.dumps({"surface": "host:hgk-receiver"}) + "\n", encoding="utf-8")
        receipt = self.td / "receipt.json"
        run = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "host_projection_check.py"), "--strict",
             "--out", str(self.out), "--receipt", str(receipt)],
            capture_output=True, text=True, cwd=str(ROOT),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertNotEqual(run.returncode, 0, "strict host gate accepted a marker-only stub")
        self.assertIn("MUT-HOST-STUB", run.stdout)
        self.assertTrue(receipt.is_file())


if __name__ == "__main__":
    unittest.main()
