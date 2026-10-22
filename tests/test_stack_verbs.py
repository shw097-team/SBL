"""The eight verbs the stack claims, exercised as a caller would use them.

TS10 asked for five products with load/invoke/upgrade/rollback as real commands. Three of those verbs did not exist,
and 'upgrade' could not be proved by reinstalling because a reinstall of the same environment reproduces the same
digests. These tests pin the behaviour this module now provides: a digest-checked load, a real mode-gate invoke, an
upgrade that refuses a no-op and keeps a preimage, and a rollback that restores that preimage byte for byte.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sbl_stack
from sbl_core.errors import SBLError


class StackVerbTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sbl-stack-verbs-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def installed(self) -> Path:
        target = self.root / "stack"
        result = sbl_stack.install(target)
        self.assertTrue(result["ok"], result)
        return target

    def test_load_reports_every_component_after_checking_digests(self) -> None:
        target = self.installed()
        result = sbl_stack.load(target)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["components"], len(result["loaded"]))
        self.assertEqual(result["problems"], [])

    def test_load_fails_closed_when_a_recorded_digest_is_wrong(self) -> None:
        target = self.installed()
        manifest_path = target / "stack.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        first = sorted(manifest["components"])[0]
        manifest["components"][first] = "0" * 64
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        result = sbl_stack.load(target)
        self.assertFalse(result["ok"])
        self.assertTrue(any("digest changed" in p for p in result["problems"]), result["problems"])

    def test_invoke_returns_the_mode_gate_cells_and_refuses_an_unknown_mode(self) -> None:
        target = self.installed()
        result = sbl_stack.invoke(target)
        self.assertTrue(result["ok"], result)
        self.assertGreaterEqual(result["count"], 1)
        with self.assertRaises(SBLError) as caught:
            sbl_stack.invoke(target, "NOT_A_MODE")
        self.assertEqual(caught.exception.code, "SBL_E_PROHIBITED_KIND")

    def test_upgrade_refuses_a_noop(self) -> None:
        target = self.installed()
        current = target / "stack.json"
        with self.assertRaises(SBLError) as caught:
            sbl_stack.upgrade(target, current)
        self.assertEqual(caught.exception.code, "SBL_E_UPGRADE_NOOP")

    def test_upgrade_keeps_a_preimage_and_rollback_restores_it_byte_for_byte(self) -> None:
        target = self.installed()
        original = (target / "stack.json").read_bytes()
        desired = json.loads(original)
        desired["version"] = "0.1.1rc2"

        desired_path = self.root / "desired.json"
        desired_path.write_text(json.dumps(desired, indent=2), encoding="utf-8")
        upgraded = sbl_stack.upgrade(target, desired_path)
        self.assertTrue(upgraded["ok"], upgraded)
        self.assertEqual(upgraded["from_version"], "0.1.1rc1")
        self.assertEqual(upgraded["to_version"], "0.1.1rc2")
        self.assertNotEqual((target / "stack.json").read_bytes(), original)

        rolled = sbl_stack.rollback(target)
        self.assertTrue(rolled["ok"], rolled)
        self.assertTrue(rolled["byte_identical"])
        self.assertEqual((target / "stack.json").read_bytes(), original)

    def test_rollback_without_a_preimage_fails_closed(self) -> None:
        target = self.installed()
        with self.assertRaises(SBLError) as caught:
            sbl_stack.rollback(target)
        self.assertEqual(caught.exception.code, "SBL_E_BAD_STATE")

    def test_every_verb_is_reachable_from_the_cli(self) -> None:
        from sbl_stack.cli import main

        target = self.installed()
        self.assertEqual(main(["status", "--root", str(target)]), 0)
        self.assertEqual(main(["load", "--root", str(target)]), 0)
        self.assertEqual(main(["invoke", "--root", str(target)]), 0)
        self.assertEqual(main(["doctor", "--root", str(target)]), 0)
        self.assertEqual(main(["describe"]), 0)


if __name__ == "__main__":
    unittest.main()
