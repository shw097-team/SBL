"""Guard the S4 typed-error surface.

A defect class found while qualifying the CLI: an I/O or parse failure, and an argparse usage error,
escaped as a bare traceback (exit 1) or as usage text on stderr. A caller cannot branch on either, so
every non-zero exit must carry the same machine-readable envelope. These tests pin that.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}


def cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", *args],
                          capture_output=True, text=True, env=ENV, cwd=str(ROOT))


class TypedErrorSurface(unittest.TestCase):
    def _assert_typed(self, args: list[str], code: str) -> None:
        r = cli(args)
        self.assertEqual(r.returncode, 2, f"{args} exited {r.returncode}, stdout={r.stdout[:200]!r}")
        payload = json.loads(r.stdout)
        self.assertEqual(payload["verdict"], "FAIL")
        self.assertEqual(payload["code"], code, payload)

    def test_missing_input_file_is_typed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._assert_typed(["compile-pi", "--intent", str(Path(tmp) / "nope.json")], "IO_NOT_FOUND")

    def test_malformed_json_is_typed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            self._assert_typed(["compile-pi", "--intent", str(bad)], "PARSE_INVALID")

    def test_non_object_json_is_typed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arr = Path(tmp) / "arr.json"
            arr.write_text("[1,2,3]", encoding="utf-8")
            self._assert_typed(["compile-pi", "--intent", str(arr)], "INPUT_SHAPE_INVALID")

    def test_usage_error_is_typed(self) -> None:
        self._assert_typed(["doctor", "--bogus"], "USAGE_INVALID")

    def test_repair_without_authorized_root_does_not_crash(self) -> None:
        # This used to raise NameError: the CLI referenced an undefined ROOT.
        r = cli(["--root", str(ROOT), "repair", "--subject", "src/pipd_ls_sp/util.py",
                 "--scope", "src/**"])
        self.assertNotEqual(r.returncode, 1, f"untyped crash: {r.stderr[-300:]}")
        self.assertIn(r.returncode, (0, 2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
