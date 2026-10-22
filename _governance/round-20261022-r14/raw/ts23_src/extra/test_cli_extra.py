"""Contract cases for ts23-newline that the generator does not build inline.

Written as a plain file rather than assembled through nested string literals: four earlier rounds of fixture defects came
from escaping inside the generator, and the cure is to stop generating these.
"""
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


def run(*args):
    return subprocess.run([sys.executable, "-m", os.environ["TS23_MODULE"], *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")


class Contract(unittest.TestCase):
    def setUp(self):
        self.fixture = Path(os.environ["TS23_FIXTURE"])
        self.dir = self.fixture.parent

    def test_read_only_even_when_the_rewrite_would_be_identical(self):
        binary = self.dir / "contract-binary.bin"
        binary.write_bytes(b"\xff\xfe a\n")
        before_digest = hashlib.sha256(binary.read_bytes()).hexdigest()
        before_mtime = binary.stat().st_mtime_ns
        self.assertEqual(run(binary).returncode, 0)
        self.assertEqual(hashlib.sha256(binary.read_bytes()).hexdigest(), before_digest)
        self.assertEqual(binary.stat().st_mtime_ns, before_mtime,
                         "a rewrite of identical bytes still moves the mtime, so this proves read-only")

    def test_input_error_writes_nothing_and_prints_no_traceback(self):
        result = run(self.dir / "contract-does-not-exist")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("ERR_INPUT", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_bom_and_terminators_are_counted_as_bytes(self):
        bom = self.dir / "contract-bom.md"
        bom.write_bytes(b"\xef\xbb\xbf# Title\n")
        data = bom.read_bytes()
        result = json.loads(run(bom).stdout)
        self.assertEqual(result["bytes"], len(data))
        self.assertEqual(result["newlines"], 1)
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
