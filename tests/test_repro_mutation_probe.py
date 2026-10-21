"""The reproducibility tests must actually FAIL when the mechanism is broken.

THE INDEPENDENT CHECKER FOUND THIS GAP. On the first version of
`tests/test_reproducible_build.py` the checker mutated the candidate three ways
and two of the three mutants still passed:

  * `.gitattributes` rewritten to `eol=crlf`  -> PASSED (the test only grepped
    the file for the literal "eol=lf")
  * `normalise_sdist(sdist, epoch)` -> `pass` -> PASSED (the test grepped the
    source for the CALL, so removing the call was invisible)
  * `.gitattributes` deleted -> FAILED (the only mutant that was caught)

A test that cannot fail is not a test. This module runs the same mutants against
a THROWAWAY COPY of the tree and asserts that the reproducibility tests notice
each one. The protected candidate is never modified: every mutation happens in a
temporary directory.

The probe is skipped when the environment cannot run it (no git identity, no
writable copy, no pytest in the ambient interpreter). A skipped probe is not a
pass, so it is reported as skipped rather than silently green.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEST_FILE = "tests/test_reproducible_build.py"

MUTANTS = {
    "gitattributes_crlf": (
        ".gitattributes",
        lambda body: body.replace("eol=lf", "eol=crlf"),
    ),
    "sdist_normalisation_disabled": (
        "tools/build_reproducible.py",
        lambda body: body.replace(
            "        normalise_sdist(sdist, epoch)\n", "        pass  # MUTANT\n"
        ),
    ),
    "pax_header_not_stripped": (
        "tools/build_reproducible.py",
        lambda body: body.replace(
            'k != "mtime"', 'k != "not-a-real-header"'
        ),
    ),
}


def _git(*args: str, cwd: Path) -> str:
    r = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=300
    )
    return r.stdout


def _copy_tree(dst: Path) -> None:
    """Copy the WORKING tree (with its .git) into dst.

    The working tree is copied, not `git checkout`ed: the uncommitted new tests
    would otherwise be reverted and the probe would run the OLD tests, which
    makes every mutant look green. The .git directory travels with it, so
    `ls-files`, `check-attr` and `cat-file` all work in the copy.
    """
    shutil.copytree(
        REPO,
        dst,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", "build", "dist", "*.egg-info", ".pytest_cache"
        ),
        symlinks=True,
    )
    # index the copied working tree so `check-attr` reflects the mutations
    subprocess.run(
        ["git", "-C", str(dst), "add", "-A"],
        capture_output=True,
        timeout=300,
    )


def _pytest_on(tree: Path, python: str) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["TMPDIR"] = str(tree)
    env["TEMP"] = str(tree)
    env["TMP"] = str(tree)
    r = subprocess.run(
        [python, "-m", "pytest", "-q", "-o", "addopts=", "-p", "no:cacheprovider",
         TEST_FILE, "--basetemp", str(tree / ".bt")],
        capture_output=True,
        text=True,
        timeout=900,
        cwd=str(tree),
        env=env,
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _skip_reason() -> str | None:
    if shutil.which("git") is None:
        return "git is not on PATH"
    if not (REPO / ".git").exists():
        return "the candidate is not a git repository"
    return None


def test_each_contract_breaking_mutation_is_caught():
    """Every mutant must make the reproducibility tests FAIL."""
    reason = _skip_reason()
    if reason:
        import pytest

        pytest.skip(f"mutation probe cannot run: {reason}")

    python = sys.executable
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        # 1. the unmutated tree must PASS, otherwise the probe proves nothing
        clean = base / "clean"
        _copy_tree(clean)
        rc, out = _pytest_on(clean, python)
        assert rc == 0, f"the clean tree does not pass ({rc}); the probe is meaningless:\n{out[-2000:]}"

        for name, (rel, mutate) in MUTANTS.items():
            tree = base / name
            _copy_tree(tree)
            target = tree / rel
            original = target.read_text(encoding="utf-8")
            mutated = mutate(original)
            assert mutated != original, f"mutant {name} did not change {rel}; the probe is stale"
            target.write_text(mutated, encoding="utf-8", newline="\n")
            rc, out = _pytest_on(tree, python)
            assert rc != 0, (
                f"the mutation {name} ({rel}) left the reproducibility tests GREEN. "
                f"A test that cannot fail is not a test.\n{out[-2000:]}"
            )
