#!/usr/bin/env python3
"""W9: `danger-full-access` is classified as a policy mention or a writer usage, and only an
in-round usage is fatal."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import deny_list_scan as D  # noqa: E402


class DenyListClassification(unittest.TestCase):
    def test_mention_vs_usage_both_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # A policy/contract line that FORBIDS the flag: a mention.
            (root / "contract").mkdir()
            (root / "contract" / "R4.CONTRACT.json").write_text(
                '   "禁止 danger-full-access 或其他僅憑 PROMPT 聲明限制的無隔離 writer。",\n',
                encoding="utf-8")
            # An actual codex sandbox setting that ENABLES it: a usage.
            (root / "logs").mkdir()
            (root / "logs" / "run.log").write_text(
                "approval: never\nsandbox: danger-full-access\n", encoding="utf-8")
            # A usage *inside the R4 round scope*: fatal.
            (root / ".hgk" / "codex").mkdir(parents=True)
            (root / ".hgk" / "codex" / "writer.log").write_text(
                "sandbox: danger-full-access\n", encoding="utf-8")

            report = D.evaluate(D.scan(root), r4_scope=".hgk/")
            self.assertTrue(report["policy_mention_count"] >= 1)
            self.assertTrue(report["writer_usage_count"] >= 2)
            self.assertIn("contract/R4.CONTRACT.json", report["policy_mention_files"])
            self.assertIn("logs/run.log", report["writer_usage_files"])
            self.assertTrue(report["r4_writer_usage"], "expected the in-round usage to be fatal")
            self.assertEqual(report["verdict"], "FAIL")
            self.assertEqual(D.main(["--root", str(root), "--r4-scope", ".hgk/"]), 1)

    def test_mention_only_tree_is_not_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "prompt.md").write_text(
                "- 禁止 danger-full-access 或其他無隔離 writer。\n", encoding="utf-8")
            report = D.evaluate(D.scan(root), r4_scope=".hgk/")
            self.assertEqual(report["writer_usage_count"], 0)
            self.assertEqual(report["verdict"], "PASS")
            self.assertEqual(D.main(["--root", str(root), "--r4-scope", ".hgk/"]), 0)

    def test_config_invocation_and_toml_setting_are_writer_usage(self) -> None:
        # C9': two real writer-usage forms the previous classifier missed.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # A codex invocation passing the setting through --config / -c, quoted either way.
            (root / "logs").mkdir()
            (root / "logs" / "exec.log").write_text(
                "codex exec --config 'sandbox_mode=\"danger-full-access\"'\n"
                'codex exec -c "sandbox_mode=\'danger-full-access\'"\n',
                encoding="utf-8")
            # A TOML setting, with and without a trailing comment.
            (root / "codex.toml").write_text(
                'sandbox_mode = "danger-full-access"\n'
                'sandbox_mode = "danger-full-access"   # explicitly enabled\n',
                encoding="utf-8")
            report = D.evaluate(D.scan(root), r4_scope=".hgk/")
            self.assertGreaterEqual(report["writer_usage_count"], 4)
            self.assertIn("logs/exec.log", report["writer_usage_files"])
            self.assertIn("codex.toml", report["writer_usage_files"])

    def test_forbidden_prose_stays_a_mention(self) -> None:
        # A contract that FORBIDS the flag is a mention, not a usage.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "contract").mkdir()
            (root / "contract" / "R4.CONTRACT.json").write_text(
                '   "禁止 danger-full-access，不得用 --config sandbox_mode=danger-full-access。",\n',
                encoding="utf-8")
            report = D.evaluate(D.scan(root), r4_scope=".hgk/")
            self.assertEqual(report["writer_usage_count"], 0)
            self.assertIn("contract/R4.CONTRACT.json", report["policy_mention_files"])
            self.assertEqual(report["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
