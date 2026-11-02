"""G3: the sbl-tpm-sp skills bundle is derived from the single PIPD skill source.

No compiler copy, no second hand-maintained skill set: the builder copies the eight packs out of
``integrations/pipd/skills`` and binds each file to a sha256 in its manifest. These assertions run
without the compiler installed, because the builder only reads Markdown/JSON.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "products" / "sbl-tpm-sp" / "build_bundle.py"
SOURCE = ROOT / "integrations" / "pipd" / "skills"


class SkillsBundle(unittest.TestCase):
    def test_bundle_is_derived_with_eight_named_skills(self) -> None:
        self.assertTrue(BUILDER.is_file(), "the bundle builder is missing")
        self.assertTrue(SOURCE.is_dir(), "the skill source is missing")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "bundle"
            proc = subprocess.run(
                [sys.executable, str(BUILDER), "--source", str(SOURCE), "--out", str(out)],
                capture_output=True, text=True, timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            manifest = json.loads((out / "MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["skill_count"], 8)
            self.assertEqual(len(set(manifest["skills"])), 8)
            dirs = sorted(p.name for p in (out / "skills").iterdir() if p.is_dir())
            self.assertEqual(dirs, sorted(manifest["skills"]))
            for entry in manifest["files"]:
                self.assertTrue((out / entry["path"]).is_file(), entry["path"])
            self.assertFalse((out / "skills" / "pipd_ls_sp").exists())

    def test_a_ninth_pack_is_refused_rather_than_silently_shipped(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "skills"
            src.mkdir()
            for i in range(9):
                pack = src / f"skill-{i}"
                pack.mkdir()
                (pack / "SKILL.md").write_text(f"---\nname: skill-{i}\n---\n", encoding="utf-8")
            out = Path(td) / "bundle"
            proc = subprocess.run(
                [sys.executable, str(BUILDER), "--source", str(src), "--out", str(out)],
                capture_output=True, text=True, timeout=120)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("SKILL_COUNT_MISMATCH", proc.stderr)


if __name__ == "__main__":
    unittest.main()
