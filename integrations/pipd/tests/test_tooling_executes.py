"""Guard the tooling surface that the artefact suites do not exercise.

Why this test exists: a repo-wide line-ending repair accidentally added `newline=""` to
`Path.read_text` calls in tools/cli_smoke.py. `Path.read_text` does not accept that keyword, so the
CLI smoke runner crashed with TypeError. Nothing caught it: the unit suite does not execute
tools/*.py, and the independent checker was (correctly) told not to run tools that write into the
repo. A whole directory of executable tooling was therefore unverified.

These tests are cheap and execute the tooling for real.
"""
from __future__ import annotations

import py_compile
import subprocess
import sys
import unittest
from pathlib import Path

# Self-bootstrap, same rule as every other test file here: a test file must be runnable standalone.
# An independent checker had to run this one with PYTHONPATH=src, which is exactly the defect the
# previous round flagged in another test file. Relying on a sibling's import side effects is not ok.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _is_git_internal_path(p: str) -> bool:
    """True when a repo-relative path is version-control machinery, NOT a project file.

    This is the exact intent behind the `tracked_files` guard: `tracked_files` must never count
    `.git`-internals. It flags an exact `.git` entry, anything under a `.git/` directory, the
    bare-repo internals (top-level `objects/`, `refs/`, `pack/` - no ref, object or pack path),
    and the top-level index/lock files. Ordinary project files that merely begin with the same
    four characters (`.gitignore`, `.gitattributes`) are NOT internals.
    """
    if p == ".git" or p.startswith(".git/") or "/.git/" in p:
        return True
    parts = p.split("/")
    if parts[0] in {"objects", "refs", "pack"}:
        return True
    if len(parts) == 1 and parts[0] in {"index", "index.lock", "ORIG_HEAD",
                                        "packed-refs", "COMMIT_EDITMSG"}:
        return True
    return False


class TestToolingExecutes(unittest.TestCase):
    def test_every_module_compiles(self) -> None:
        bad: list[str] = []
        for d in (ROOT / "src", ROOT / "tools", ROOT / "tests"):
            for f in sorted(d.rglob("*.py")):
                try:
                    py_compile.compile(str(f), doraise=True, cfile=str(f.with_suffix(".pyc.tmp")))
                except py_compile.PyCompileError as exc:
                    bad.append(f"{f.relative_to(ROOT)}: {exc}")
                finally:
                    f.with_suffix(".pyc.tmp").unlink(missing_ok=True)
        self.assertEqual(bad, [], "modules failed to compile")

    def test_cli_smoke_runs(self) -> None:
        """The 13-command CLI surface must actually execute, not just import.

        Run inside a throwaway copy of the repo: the runner writes .hgk/artifacts/cli/CLI_SMOKE.json
        by design, and a test that rewrites tracked evidence makes "tree clean after a test run"
        impossible. The copy has every artifact the runner reads, so nothing is skipped.
        """
        import os as _os
        import shutil as _sh
        import tempfile as _tf
        with _tf.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "repo"
            _sh.copytree(ROOT, dst, ignore=_sh.ignore_patterns(".git", "__pycache__", "*.db", "*.pyc"))
            r = subprocess.run([sys.executable, "-B", "tools/cli_smoke.py"], cwd=str(dst),
                               capture_output=True, text=True,
                               env={**_os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(r.returncode, 0,
                         f"cli_smoke.py exited {r.returncode}\n{(r.stderr or r.stdout)[-800:]}")

    def test_no_read_text_receives_newline(self) -> None:
        """Pin the specific defect: Path.read_text takes no `newline` keyword."""
        offenders = []
        for d in (ROOT / "src", ROOT / "tools", ROOT / "tests"):
            for f in sorted(d.rglob("*.py")):
                text = f.read_text(encoding="utf-8")
                i = 0
                while True:
                    j = text.find(".read_text(", i)
                    if j < 0:
                        break
                    k = j + len(".read_text(")
                    depth, c = 1, k
                    while depth > 0 and c < len(text):
                        depth += (text[c] == "(") - (text[c] == ")")
                        c += 1
                    if "newline=" in text[k:c]:
                        offenders.append(str(f.relative_to(ROOT)))
                        break
                    i = c
        self.assertEqual(offenders, [], "read_text() was given a `newline` argument")


    def test_tracked_file_metric_excludes_vcs_internals(self) -> None:
        """Pin the oracle for `_tracked_file_count` in BOTH subjects it must serve (R2-E2).

        The shipped probe in `src/pipd_ls_sp/cli.py::_tracked_file_count` is the authoritative
        definition: it returns `git ls-files` when the subject IS a git checkout, and otherwise the
        count of files in the tree EXCLUDING `.git/` and `__pycache__/`. The old test asserted only
        the first branch against an unconditional `git ls-files` literal. That made the oracle
        subject-incorrect: in a non-git fresh copy the walk branch runs, git prints 0, and the test
        FAILED (R2-E2). The oracle is rebound to the probe's own defined behavior for the subject at
        hand, so it holds in both environments. It is not relaxed: each branch is pinned EXACTLY to
        the authoritative count (equality, not inequality), the walk branch is additionally pinned
        to exclude `.git/` internals and `__pycache__/` on a synthetic tree, and no magic constant
        is used.
        """
        import os as _os
        import shutil as _sh
        import subprocess as sp
        import tempfile as _tf
        from pipd_ls_sp.cli import _tracked_file_count

        def _walk_count(root: Path) -> int:
            # The probe's non-git branch, stated independently of the implementation.
            return sum(1 for p in root.rglob("*") if p.is_file()
                       and ".git" not in p.parts and "__pycache__" not in p.parts)

        def _git_tracked(root: Path, *, ceiling: str | None = None) -> tuple[int, int]:
            env = dict(_os.environ)
            if ceiling is not None:
                env["GIT_CEILING_DIRECTORIES"] = ceiling
            r = sp.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, env=env)
            return r.returncode, len([l for l in r.stdout.splitlines() if l.strip()])

        def _git_tracked_paths(root: Path) -> list[str]:
            # The raw subject the `.git`-internals guard inspects: the exact tracked path list.
            r = sp.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True)
            if r.returncode != 0:
                return []
            return [l for l in r.stdout.splitlines() if l.strip()]

        # (a) On a real git checkout the probe must report EXACTLY the git-tracked count, never
        #     rglob (which would also sweep .git). This is the branch the old test covered.
        rc, tracked = _git_tracked(ROOT)
        if rc == 0:
            n = _tracked_file_count(ROOT)
            self.assertEqual(n, tracked,
                             "on a git checkout tracked_files must equal `git ls-files` exactly")
            # (a.1) The guard's STATED intent, asserted directly: no tracked path may be a
            #       `.git`-internals path. This is the real "counting .git internals again"
            #       detector and it holds no matter how large the repo legitimately grows. Unlike
            #       an absolute size cap, it does not punish a repo for committing governance
            #       evidence under `.hgk/rounds/`.
            internals = [p for p in _git_tracked_paths(ROOT) if _is_git_internal_path(p)]
            self.assertEqual(
                internals, [],
                "tracked_files looks like it is counting .git internals again: "
                f"these tracked paths are version-control machinery: {internals[:10]}")
            # (a.2) Keep a sanity upper bound so a future miscount cannot slip through unnoticed.
            #       The bound is deliberately generous against real growth: the honest count here
            #       is ~1k and rises a few dozen files per round as receipts land under `.hgk/`.
            #       A genuine `.git`-internals miscount is a MANY-THOUSANDS jump (packed objects,
            #       refs, logs), not a few dozen - so 25_000 separates the two regimes with a wide
            #       margin while still failing loudly if the metric ever walks the whole `.git/`.
            self.assertLess(
                n, 25_000,
                "tracked_files is implausibly large (>= 25,000): a count this high is a "
                ".git-internals miscount, not real repo growth")

        # (b) A non-git copy (no .git at all) is the exact condition that broke the old oracle.
        #     GIT_CEILING_DIRECTORIES stops git from climbing to an enclosing repo, so the subject is
        #     genuinely non-git even when the temp dir sits inside a checkout; the ignore list drops
        #     any nested scratch so the copy cannot recurse into itself.
        with _tf.TemporaryDirectory() as td:
            dst = Path(td) / "PIPD"
            _sh.copytree(ROOT, dst,
                         ignore=_sh.ignore_patterns(".git", "__pycache__", "*.db"))
            self.assertFalse((dst / ".git").exists(), "the fresh copy must exclude .git")
            rc2, tracked2 = _git_tracked(dst, ceiling=str(Path(td).resolve()))
            self.assertNotEqual(rc2, 0, "the fresh copy must not resolve to a git checkout")
            self.assertEqual(tracked2, 0, "git must report no tracked files in the fresh copy")
            probe2 = _tracked_file_count(dst)
            self.assertEqual(probe2, _walk_count(dst),
                             "in a non-git copy tracked_files must equal the filesystem walk "
                             "excluding .git/ and __pycache__/")

        # (c) Pin that exclusion on a SYNTHETIC tree that actually carries `.git/` internals and a
        #     `__pycache__/`, proving the walk branch is non-trivial and really excludes them. The
        #     authoritative source is the probe's own defined behavior above; we only read it here.
        with _tf.TemporaryDirectory() as td:
            syn = Path(td) / "syn"
            (syn / "src").mkdir(parents=True)
            (syn / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            (syn / "README.md").write_text("# syn\n", encoding="utf-8")
            (syn / ".git" / "objects" / "aa").mkdir(parents=True)
            (syn / ".git" / "objects" / "aa" / "blob").write_text("pack\n", encoding="utf-8")
            (syn / "__pycache__").mkdir()
            (syn / "__pycache__" / "m.pyc").write_text("bytecode\n", encoding="utf-8")
            rc3, _ = _git_tracked(syn, ceiling=str(Path(td).resolve()))
            self.assertNotEqual(rc3, 0, "the synthetic tree must not resolve to a git checkout")
            self.assertEqual(_walk_count(syn), 2, "walk must see exactly the 2 real project files")
            self.assertEqual(_tracked_file_count(syn), 2,
                             "tracked_files must exclude .git/ internals and __pycache__/")

    def test_git_internals_guard_rejects_a_git_objects_entry(self) -> None:
        """The guard must actually FIRE: prove it flags a `.git/objects/...` path (third site).

        A guard that only ever sees a clean list proves nothing. This feeds the predicate a list
        containing a `.git/objects/...` entry and pins that it is detected, while ordinary project
        files that merely start with `.git` (`.gitignore`) are left alone.
        """
        poisoned = ["src/a.py", "README.md", ".git/objects/aa/blob", ".git/config"]
        internals = [p for p in poisoned if _is_git_internal_path(p)]
        self.assertEqual(internals, [".git/objects/aa/blob", ".git/config"],
                         "the .git-internals guard failed to flag .git machinery")
        self.assertEqual([p for p in [".gitignore", ".gitattributes"] if _is_git_internal_path(p)],
                         [], "ordinary .git* project files must NOT be flagged as internals")
        self.assertEqual([p for p in ["objects/aa/blob", "refs/heads/main", "index", "index.lock"]
                          if _is_git_internal_path(p)],
                         ["objects/aa/blob", "refs/heads/main", "index", "index.lock"],
                         "bare-repo object/ref/pack and index/lock internals must be flagged")

    def test_export_manifest_has_no_vcs_paths(self) -> None:
        from pipd_ls_sp import workspace

        bundle = workspace.export_manifest(ROOT, include=["."])
        paths = [row["rel"] for row in bundle.get("files", [])]
        self.assertTrue(paths, "export bundle produced no rows")
        def _is_vcs_internal(p: str) -> bool:
            # `.git/...` is a version-control internal. `.gitattributes` / `.gitignore` are ordinary
            # project files that merely start with the same four characters - an earlier version of
            # this predicate flagged them and failed on a correct tree.
            return p == ".git" or p.startswith(".git/") or "/.git/" in p

        leaked = [p for p in paths if _is_vcs_internal(p)]
        self.assertEqual(leaked, [], "export manifest leaked version-control internals")
        self.assertGreater(len(paths), 50,
                           "include=['.'] must walk the tree; a tiny result means the walk was skipped")

    def test_every_test_file_bootstraps_sys_path(self) -> None:
        """No test file may depend on a sibling importing src/ first."""
        missing = []
        for f in sorted((ROOT / "tests").glob("test_*.py")):
            src = f.read_text(encoding="utf-8")
            if "sys.path.insert" not in src:
                missing.append(f.name)
        self.assertEqual(missing, [], "test files without a sys.path bootstrap")


if __name__ == "__main__":
    unittest.main()
