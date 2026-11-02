#!/usr/bin/env python3
"""S2 verifier envelope: three-way delta classification, allow-rules, refusals, emitted schema.

Every test uses a tempfile tree only. Deterministic units: the classification and refusal cases are
pure; the init/snapshot round-trips use a throwaway ``git init`` repo in the temp dir and skip if
git is absent. No test touches the product tree.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import round_envelope as E  # noqa: E402


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def run_verify(before: dict, after: dict, allow: list[str] | None = None) -> tuple[int, dict, str]:
    """Drive the verify CLI through temp files; return (exit_code, parsed_summary, stderr)."""
    allow = allow or []
    out, err = io.StringIO(), io.StringIO()
    with tempfile.TemporaryDirectory() as td:
        b, a = Path(td) / "before.json", Path(td) / "after.json"
        write_json(b, before)
        write_json(a, after)
        argv = ["verify", "--before", str(b), "--after", str(a)]
        for rx in allow:
            argv += ["--allow-added", rx]
        with redirect_stdout(out), redirect_stderr(err):
            code = E.main(argv)
    lines = out.getvalue().splitlines()
    start = lines.index("{")
    summary = json.loads("\n".join(lines[start:]))
    return code, summary, err.getvalue()


def git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


def make_repo(root: Path) -> Path:
    """A minimal committed git repo with one tracked file."""
    root.mkdir(parents=True, exist_ok=True)
    git(["-c", "init.defaultBranch=main", "init", "-q"], root)
    (root / "a.txt").write_text("hello\n", encoding="utf-8")
    git(["add", "a.txt"], root)
    git(["-c", "user.email=t@example.invalid", "-c", "user.name=tester", "commit", "-q", "-m", "init"], root)
    return root


GIT = shutil.which("git") is not None


def _to_msys(p: Path) -> str:
    """Render an absolute Windows path in MSYS/POSIX form, e.g. ``C:\\a\\b`` -> ``/c/a/b``."""
    abs_path = os.path.abspath(str(p))
    drive, rest = os.path.splitdrive(abs_path)
    return "/" + drive[0].lower() + rest.replace("\\", "/")


def make_plain_src(root: Path) -> Path:
    """A minimal non-git source tree (one file). Init works on it; HEAD is simply unbound."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.txt").write_text("hello\n", encoding="utf-8")
    return root


class Classification(unittest.TestCase):
    def test_modified_path_is_detected_and_fails(self):
        before = {"files": {"a.py": "h1", "b.py": "h2"}}
        after = {"files": {"a.py": "CHANGED", "b.py": "h2"}}
        code, summary, _ = run_verify(before, after)
        self.assertIn("a.py", summary["modified"])
        self.assertEqual(summary["verdict"], "DRIFT")
        self.assertNotEqual(code, 0)

    def test_removed_path_is_detected_and_fails(self):
        before = {"files": {"a.py": "h1", "gone.py": "h2"}}
        after = {"files": {"a.py": "h1"}}
        code, summary, _ = run_verify(before, after)
        self.assertIn("gone.py", summary["removed"])
        self.assertEqual(summary["verdict"], "DRIFT")
        self.assertNotEqual(code, 0)

    def test_added_path_is_detected(self):
        before = {"files": {"a.py": "h1"}}
        after = {"files": {"a.py": "h1", "new.py": "h9"}}
        code, summary, _ = run_verify(before, after)
        self.assertIn("new.py", summary["added"])
        # No allow-rule -> the addition is unexpected, so it is drift (non-zero).
        self.assertIn("new.py", summary["unexpected_added"])
        self.assertNotEqual(code, 0)

    def test_allow_rule_makes_mandated_addition_not_drift(self):
        # The brief mandates the writer create this very file; the guard must not call it drift.
        before = {"files": {"a.py": "h1"}}
        after = {"files": {"a.py": "h1", "tests/test_round_envelope.py": "h9"}}
        code, summary, _ = run_verify(before, after, allow=[r"tests/test_round_envelope\.py"])
        self.assertIn("tests/test_round_envelope.py", summary["allowed_added"])
        self.assertEqual(summary["unexpected_added"], [])
        self.assertEqual(summary["modified"], [])
        self.assertEqual(summary["removed"], [])
        self.assertEqual(summary["verdict"], "CLEAN")
        self.assertEqual(code, 0)

    def test_added_without_matching_rule_is_unexpected_and_nonzero(self):
        before = {"files": {"a.py": "h1"}}
        after = {"files": {"a.py": "h1", "rogue.py": "h9"}}
        # An allow-rule that does NOT cover rogue.py must not launder it.
        code, summary, _ = run_verify(before, after, allow=[r"^tools/allowed\.py$"])
        self.assertEqual(summary["allowed_added"], [])
        self.assertIn("rogue.py", summary["unexpected_added"])
        self.assertEqual(summary["verdict"], "DRIFT")
        self.assertNotEqual(code, 0)

    def test_emitted_json_carries_schema_and_three_set_keys(self):
        before = {"files": {"a.py": "h1", "gone.py": "h2"}}
        after = {"files": {"a.py": "h2", "new.py": "h3"}}
        _, summary, _ = run_verify(before, after)
        self.assertEqual(summary["schema"], "PIPD-ROUND-BOUNDARY-CHECK/1")
        for key in ("modified", "removed", "added"):
            self.assertIn(key, summary)
            self.assertIsInstance(summary[key], list)


class Refusals(unittest.TestCase):
    def test_refuses_dst_inside_src(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_repo(tmp / "src")
            dst = src / "copy"  # inside src -> refused
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(dst)])
            self.assertNotEqual(code, 0)
            self.assertIn("REFUSED", err.getvalue())
            self.assertFalse(dst.exists(), "refusal must happen before any bytes are written")

    def test_refuses_scratch_inside_tree(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_repo(tmp / "src")
            dst = tmp / "dst"          # outside src -> admissible
            scratch = src / "scratch"  # inside src -> refused
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(dst), "--scratch", str(scratch)])
            self.assertNotEqual(code, 0)
            self.assertIn("REFUSED", err.getvalue())
            self.assertFalse(dst.exists(), "refusal must happen before any bytes are written")
            self.assertFalse(scratch.exists(), "refusal must happen before scratch is created")

    def test_guard_paths_reports_both_directions(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src, nested = tmp / "src", tmp / "src" / "inner"
            self.assertTrue(E.guard_paths(src, nested, tmp / "scratch"))
            self.assertTrue(E.guard_paths(nested, src, tmp / "scratch"))

    def test_refuses_src_inside_dst(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dst = tmp / "copy"
            src = dst / "src"  # src lives inside dst -> refused
            src.mkdir(parents=True)
            scratch = tmp / "scratch"
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(dst), "--scratch", str(scratch)])
            self.assertNotEqual(code, 0)
            self.assertIn("REFUSED", err.getvalue())
            # The boundary is checked before a single byte is written: no envelope, no scratch.
            self.assertFalse(scratch.exists(), "refusal must happen before scratch is created")


class PathNormalisation(unittest.TestCase):
    """H2-DEFECT-01: an MSYS-style path argument must become a real drive path, not ``\\c\\...``."""

    @unittest.skipUnless(os.name == "nt", "MSYS drive-letter normalisation is Windows-specific")
    def test_norm_path_converts_msys_style_to_drive_absolute(self):
        resolved = E._norm_path("/c/Users/x/copy")
        self.assertRegex(resolved, r"^[A-Za-z]:[\\/]")
        self.assertFalse(resolved.startswith("\\c\\"))

    @unittest.skipUnless(os.name == "nt", "MSYS drive-letter normalisation is Windows-specific")
    def test_native_drive_path_survives_unchanged(self):
        self.assertEqual(E._norm_path("C:/Users/x"), os.path.abspath("C:/Users/x"))

    @unittest.skipUnless(os.name == "nt", "MSYS drive-letter normalisation is Windows-specific")
    def test_init_with_msys_style_dst_lands_at_drive_path(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_plain_src(tmp / "src")
            dst = tmp / "copy"
            scratch = tmp / "scratch"
            msys_dst = _to_msys(dst)
            self.assertTrue(msys_dst.startswith("/"), msys_dst)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                E.main(["init", "--src", str(src), "--dst", msys_dst, "--scratch", str(scratch)])
            envelope = json.loads((scratch / "envelope.json").read_text(encoding="utf-8"))
            self.assertRegex(envelope["dst"], r"^[A-Za-z]:[\\/]")
            self.assertFalse(envelope["dst"].startswith("\\c\\"))
            self.assertTrue(dst.is_dir(), "the copy must materialise at the drive-resolved location")
            self.assertTrue((dst / "a.txt").is_file())


class DestinationFailClosed(unittest.TestCase):
    """H2-DEFECT-01: an uncreatable destination is a named refusal, never an os-level traceback."""

    def test_uncreatable_destination_is_a_clear_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_plain_src(tmp / "src")
            blocker = tmp / "blocker"
            blocker.write_text("not a directory", encoding="utf-8")  # a FILE where a dir is required
            dst = blocker / "copy"  # mkdir cannot succeed: a parent component is a file
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(dst), "--scratch", str(tmp / "scratch")])
            self.assertNotEqual(code, 0)
            self.assertIn("REFUSED", err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())


@unittest.skipUnless(GIT, "git not available")
class RoundTrip(unittest.TestCase):
    def test_init_copies_git_head_and_writes_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_repo(tmp / "src")
            # A cache that must NOT be copied.
            (src / "__pycache__").mkdir()
            (src / "__pycache__" / "a.cpython-311.pyc").write_bytes(b"\x00\x01")
            dst = tmp / "copy"
            scratch = tmp / "scratch"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = E.main(["init", "--src", str(src), "--dst", str(dst), "--scratch", str(scratch)])
            self.assertEqual(code, 0)
            envelope = json.loads((scratch / "envelope.json").read_text(encoding="utf-8"))
            self.assertEqual(envelope["schema"], "PIPD-ROUND-ENVELOPE/1")
            self.assertEqual(envelope["head"], E.git_head(src))
            self.assertEqual(E.git_head(dst), E.git_head(src))
            self.assertFalse((dst / "__pycache__").exists(), "__pycache__ must be excluded from the copy")
            self.assertTrue((dst / ".git").exists(), ".git must be copied so dst is a real checkout")
            self.assertTrue(all(a["status"] == "PASS" for a in envelope["assertions"]))

    def test_snapshot_records_missing_listed_file(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            repo = make_repo(tmp / "repo")
            (repo / "a.txt").unlink()  # tracked but now absent on disk
            rec = E.snapshot_repo(repo)
            self.assertEqual(rec["schema"], "PIPD-ROUND-SNAPSHOT/1")
            self.assertEqual(rec["files"]["a.txt"], E.MISSING)


class DestinationDestructionGuards(unittest.TestCase):
    """H2-DEFECT-02: a blank or misdirected ``--dst`` must refuse before any deletion.

    Every probe uses a disposable tempfile tree (never the product tree); the destructive-path cases
    pass a destination the guards must refuse *before* any removal, and assert on the refusal text
    and exit code.
    """

    def test_blank_or_whitespace_dst_refuses_before_normalisation(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_plain_src(tmp / "src")
            old = os.getcwd()
            # Chdir into the disposable temp dir: if STOP-1 ever regressed, "" would normalise to
            # THIS dir, never the repo, so the probe can never destroy a real tree.
            os.chdir(td)
            try:
                for blank in ("", "   ", "\t"):
                    err = io.StringIO()
                    with redirect_stdout(io.StringIO()), redirect_stderr(err):
                        code = E.main(["init", "--src", str(src), "--dst", blank,
                                       "--scratch", str(tmp / "scratch")])
                    self.assertEqual(code, 2, err.getvalue())
                    self.assertIn("REFUSED", err.getvalue())
                    self.assertIn("blank", err.getvalue())
                    self.assertIn("--dst", err.getvalue())
                    self.assertNotIn("Traceback", err.getvalue())
                # nothing was written or removed
                self.assertTrue((src / "a.txt").is_file())
                self.assertFalse((tmp / "scratch").exists())
            finally:
                os.chdir(old)

    def test_refuses_destination_equal_to_cwd(self):
        with tempfile.TemporaryDirectory() as td_src, tempfile.TemporaryDirectory() as td_cwd:
            src = make_plain_src(Path(td_src) / "src")
            old = os.getcwd()
            os.chdir(td_cwd)  # dst == cwd, but both are disposable: the guard must refuse first
            try:
                err = io.StringIO()
                with redirect_stdout(io.StringIO()), redirect_stderr(err):
                    code = E.main(["init", "--src", str(src), "--dst", td_cwd,
                                   "--scratch", str(Path(td_src) / "scratch")])
                self.assertEqual(code, 2, err.getvalue())
                self.assertIn("REFUSED", err.getvalue())
                self.assertIn("current working directory", err.getvalue())
                self.assertNotIn("Traceback", err.getvalue())
                self.assertTrue(Path(td_cwd).is_dir(), "a refused cwd must not have been removed")
            finally:
                os.chdir(old)

    def test_refuses_destination_equal_to_source(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_plain_src(tmp / "src")
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(src),
                               "--scratch", str(tmp / "scratch")])
            self.assertEqual(code, 2, err.getvalue())
            self.assertIn("REFUSED", err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())
            self.assertTrue((src / "a.txt").is_file(), "the source must be untouched after a refusal")

    def test_refuses_destination_ancestor_of_source(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dst = tmp / "parent"
            src = dst / "src"
            make_plain_src(src)  # dst is a strict ancestor of src -> refused
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(dst),
                               "--scratch", str(tmp / "scratch")])
            self.assertEqual(code, 2, err.getvalue())
            self.assertIn("REFUSED", err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())
            self.assertTrue((src / "a.txt").is_file(), "the source must be untouched after a refusal")

    def test_allow_destroy_does_not_bypass_stop_guards(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_plain_src(tmp / "src")
            # STOP-1 still refuses a blank --dst even with --allow-destroy.
            old = os.getcwd()
            os.chdir(td)  # keep a regressed "" away from the real tree
            try:
                err = io.StringIO()
                with redirect_stdout(io.StringIO()), redirect_stderr(err):
                    code = E.main(["init", "--src", str(src), "--dst", "", "--allow-destroy",
                                   "--scratch", str(tmp / "scratch")])
                self.assertEqual(code, 2, err.getvalue())
                self.assertIn("REFUSED", err.getvalue())
                self.assertIn("blank", err.getvalue())
                self.assertNotIn("Traceback", err.getvalue())
            finally:
                os.chdir(old)
            # STOP-3 still refuses an ancestor-of-source --dst even with --allow-destroy.
            err2 = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err2):
                code2 = E.main(["init", "--src", str(src), "--dst", str(src.parent), "--allow-destroy",
                                "--scratch", str(tmp / "scratch2")])
            self.assertEqual(code2, 2, err2.getvalue())
            self.assertIn("REFUSED", err2.getvalue())
            self.assertIn("REFUSED", err2.getvalue())
            self.assertNotIn("Traceback", err2.getvalue())
            self.assertTrue((src / "a.txt").is_file(), "the source must be untouched after a refusal")

    @unittest.skipUnless(GIT, "git not available")
    def test_legitimate_temp_destination_still_succeeds(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_repo(tmp / "src")
            dst = tmp / "copy"
            scratch = tmp / "scratch"
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(dst), "--scratch", str(scratch)])
            self.assertEqual(code, 0, err.getvalue())
            self.assertTrue((dst / "a.txt").is_file(), "the happy path must still copy the tree")
            self.assertTrue((scratch / "envelope.json").is_file())

    @unittest.skipUnless(GIT, "git not available")
    def test_nonempty_existing_destination_needs_allow_destroy(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = make_repo(tmp / "src")
            dst = tmp / "copy"
            dst.mkdir()
            (dst / "stale.txt").write_text("old", encoding="utf-8")
            scratch = tmp / "scratch"
            # Without --allow-destroy a non-empty destination is refused before any removal.
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                code = E.main(["init", "--src", str(src), "--dst", str(dst), "--scratch", str(scratch)])
            self.assertEqual(code, 2, err.getvalue())
            self.assertIn("REFUSED", err.getvalue())
            self.assertIn("allow-destroy", err.getvalue())
            self.assertTrue((dst / "stale.txt").is_file(), "refusal must precede any removal")
            # With --allow-destroy it proceeds, and STOP-4 prints the path it destroys.
            err2 = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err2):
                code2 = E.main(["init", "--src", str(src), "--dst", str(dst), "--allow-destroy",
                                "--scratch", str(scratch)])
            self.assertEqual(code2, 0, err2.getvalue())
            self.assertIn(str(dst.resolve()), err2.getvalue(), "STOP-4 must name the path being removed")
            self.assertFalse((dst / "stale.txt").exists(), "the stale file must have been removed")
            self.assertTrue((dst / "a.txt").is_file())


if __name__ == "__main__":
    unittest.main()
