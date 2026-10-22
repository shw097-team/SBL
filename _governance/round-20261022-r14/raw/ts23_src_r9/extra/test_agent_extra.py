"""Contract cases for ts23-review that the generator does not build inline."""
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


def run(*args, cwd=None):
    return subprocess.run([sys.executable, "-m", os.environ["TS23_MODULE"], *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", cwd=cwd)


class Contract(unittest.TestCase):
    def setUp(self):
        self.queue = Path(os.environ["TS23_QUEUE"])
        self.entries = json.loads(self.queue.read_text(encoding="utf-8"))
        self.dir = self.queue.parent

    def test_full_queue_records_every_digest(self):
        result = json.loads(run(self.queue, "--max-steps", "20").stdout)
        self.assertEqual(result["steps"], len(self.entries))
        self.assertEqual([r["path"] for r in result["reviews"]], self.entries)
        self.assertEqual([r["sha256"] for r in result["reviews"]],
                         [hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in self.entries])
        self.assertEqual([r["bytes"] for r in result["reviews"]],
                         [len(Path(p).read_bytes()) for p in self.entries])
        self.assertEqual(result["halt_reason"], "QUEUE_EXHAUSTED")

    def test_zero_and_negative_budget_review_nothing_and_are_budget_limited(self):
        for value in ("0", "-4"):
            result = json.loads(run(self.queue, "--max-steps", value).stdout)
            self.assertEqual(result["steps"], 0, f"--max-steps {value} must review nothing")
            self.assertEqual(result["remaining"], len(self.entries))
            self.assertEqual(result["reviews"], [])
            self.assertEqual(result["halt_reason"], "BUDGET",
                             "a budget limit, not an exhausted queue")

    def test_a_non_array_queue_is_rejected_including_an_empty_object(self):
        for body in ('{"a": 1}', "{}", '"just a string"'):
            path = self.dir / "contract-bad-queue.json"
            path.write_text(body, encoding="utf-8")
            result = run(path)
            self.assertEqual(result.returncode, 2, f"{body} is not a JSON array")
            self.assertEqual(result.stdout, "")
            self.assertNotIn("Traceback", result.stderr)

    def test_an_unreadable_entry_is_an_error_not_a_skip(self):
        path = self.dir / "contract-missing-entry.json"
        path.write_text(json.dumps([str(self.dir / "contract-absent-file")]), encoding="utf-8")
        result = run(path)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_a_directory_entry_is_an_error_too(self):
        # A missing path alone would let `except FileNotFoundError` pass; a directory raises a different OSError.
        self.assertTrue(self.dir.is_dir(), "precondition: the fixture is a real directory")
        path = self.dir / "contract-dir-entry.json"
        path.write_text(json.dumps([str(self.dir)]), encoding="utf-8")
        result = run(path)
        self.assertEqual(result.returncode, 2, "a directory cannot be reviewed")
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)

    def test_every_recorded_path_is_resolved(self):
        # The reporting contract says path is the resolved absolute path, so a caller can compare it with Path.resolve().
        target = self.dir / "contract-resolved.md"
        target.write_text("## A\n", encoding="utf-8")
        self.assertTrue(target.is_file(), "precondition: the fixture exists")
        queue = self.dir / "contract-resolved-queue.json"
        queue.write_text(json.dumps(["contract-resolved.md"]), encoding="utf-8")
        result = run(queue, cwd=self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(result.stdout)["reviews"][0]
        self.assertEqual(entry["path"], str(target.resolve()),
                         "the record must identify the file it hashed, not echo the relative entry")

    def test_an_empty_queue_with_zero_budget_reports_budget(self):
        # Precedence in the contract: the budget decides first, the queue second.
        empty = self.dir / "contract-empty-queue.json"
        empty.write_text("[]", encoding="utf-8")
        self.assertEqual(json.loads(empty.read_text(encoding="utf-8")), [], "precondition: an empty array")
        result = json.loads(run(empty, "--max-steps", "0").stdout)
        self.assertEqual(result["halt_reason"], "BUDGET",
                         "a step limit of zero stopped the run before the queue could be exhausted")
        self.assertEqual(result["steps"], 0)
        self.assertEqual(result["remaining"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
