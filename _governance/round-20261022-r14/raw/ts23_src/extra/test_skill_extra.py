"""Contract cases for ts23-headings that the generator does not build inline."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

TAB = chr(9)
NBSP = " "


def run(*args):
    return subprocess.run([sys.executable, "-m", os.environ["TS23_MODULE"], *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")


class Contract(unittest.TestCase):
    def setUp(self):
        self.dir = Path(os.environ["TS23_FIXTURE"]).parent

    def headings(self, path):
        return json.loads(run(path).stdout)["headings"]

    def test_internal_tab_is_preserved(self):
        path = self.dir / "contract-internal-tab.md"
        path.write_text("##  tab" + TAB + "inside\n", encoding="utf-8")
        self.assertIn(TAB, path.read_text(encoding="utf-8"), "fixture must contain an internal tab")
        self.assertEqual([h["text"] for h in self.headings(path)], ["tab" + TAB + "inside"])

    def test_tab_separated_closing_sequence_is_stripped(self):
        path = self.dir / "contract-closing-tab.md"
        path.write_text("## Gamma" + TAB + "##\n", encoding="utf-8")
        self.assertIn(TAB + "##", path.read_text(encoding="utf-8"))
        self.assertEqual([h["text"] for h in self.headings(path)], ["Gamma"])

    def test_bom_is_not_whitespace_so_the_first_line_is_not_a_heading(self):
        path = self.dir / "contract-bom-heading.md"
        path.write_bytes(b"\xef\xbb\xbf# BOMHeading\n## Real\n")
        self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"), "fixture must start with a BOM")
        texts = [h["text"] for h in self.headings(path)]
        self.assertNotIn("BOMHeading", texts)
        self.assertIn("Real", texts)

    def test_a_unicode_space_is_content_not_a_closing_sequence(self):
        path = self.dir / "contract-unicode-closing.md"
        path.write_text("## Gamma" + NBSP + "##\n", encoding="utf-8")
        self.assertIn(NBSP, path.read_text(encoding="utf-8"), "fixture must contain a non-breaking space")
        self.assertEqual([h["text"] for h in self.headings(path)], ["Gamma" + NBSP + "##"])

    def test_error_path_is_exit_two_with_empty_stdout_and_no_traceback(self):
        missing = run(self.dir / "contract-missing.md")
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, "")
        self.assertNotIn("Traceback", missing.stderr)
        undecodable = self.dir / "contract-undecodable.md"
        undecodable.write_bytes(b"\xff\xfe# x\n")
        bad = run(undecodable)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")
        self.assertNotIn("Traceback", bad.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
