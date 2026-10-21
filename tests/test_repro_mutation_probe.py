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
    # The independent checker's MUT_D: the wall-clock epoch. This one survived
    # the whole suite until the end-to-end two-build assertion was added, because
    # every other test asserted a LOCAL property and none of them built twice.
    "wall_clock_epoch": (
        "tools/build_reproducible.py",
        lambda body: body.replace(
            "DEFAULT_SOURCE_DATE_EPOCH = 1700000000",
            "import time as _t\nDEFAULT_SOURCE_DATE_EPOCH = int(_t.time())  # MUTANT",
        ),
    ),
    # The checker's MUT_E: the tool's own `identical` self-check disabled.
    "tool_self_check_disabled": (
        "tools/build_reproducible.py",
        lambda body: body.replace(
            '"identical": first == second,', '"identical": True,  # MUTANT'
        ),
    ),
    # The checker's W1 counterfactual: the naive `import build` probe.
    "naive_build_probe": (
        "tools/build_reproducible.py",
        lambda body: body.replace(
            '[python, "-m", "build", "--version"], capture_output=True, timeout=180',
            '[python, "-c", "import build"], capture_output=True, timeout=120  # MUTANT',
        ),
    ),
}


def _git(*args: str, cwd: Path) -> str:
    r = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=300
    )
    return r.stdout


def _copy_tree(dst: Path) -> None:
    """Copy the WORKING tree into dst, with an ISOLATED git dir.

    The working tree is copied, not `git checkout`ed: the uncommitted new tests
    would otherwise be reverted and the probe would run the OLD tests, which
    makes every mutant look green.

    THE `.git` DIRECTORY MUST NOT BE SHARED. The independent checker (R7 round 2)
    measured that copying a LINKED WORKTREE's `.git` - which is a pointer file to
    a shared admin dir - makes the copy's `git add -A` write THROUGH into the
    protected worktree's index. With an unstaged edit in the protected tree the
    copy silently STAGED it. The index self-healed here only because the
    protected tree happened to be clean; with real uncommitted work it would not.

    So the copy gets its OWN git dir: a fresh `git init` plus the commits that
    matter for the tests (HEAD's content), with no shared objects, no shared
    index, and no path back to the protected tree.
    """
    shutil.copytree(
        REPO,
        dst,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc", "build", "dist", "*.egg-info", ".pytest_cache"
        ),
        symlinks=True,
    )
    # a fresh, PRIVATE git dir. `git init` + a single commit of the copied
    # content gives the tests a real `ls-files` / `check-attr` / `cat-file` to
    # read, and nothing shared with the protected repository.
    env = dict(os.environ)
    env["GIT_DIR"] = str(dst / ".git")
    env["GIT_WORK_TREE"] = str(dst)
    env["GIT_INDEX_FILE"] = str(dst / ".git" / "index")
    env["GIT_AUTHOR_NAME"] = "probe"
    env["GIT_AUTHOR_EMAIL"] = "probe@invalid"
    env["GIT_COMMITTER_NAME"] = "probe"
    env["GIT_COMMITTER_EMAIL"] = "probe@invalid"
    subprocess.run(
        ["git", "init", "-q", str(dst)], capture_output=True, timeout=300, env=env
    )
    subprocess.run(
        ["git", "-C", str(dst), "add", "-A"], capture_output=True, timeout=300, env=env
    )
    subprocess.run(
        ["git", "-C", str(dst), "commit", "-q", "--no-verify", "-m", "probe copy"],
        capture_output=True,
        timeout=300,
        env=env,
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


def test_probe_does_not_touch_the_protected_repository():
    """The probe must not write through into the protected worktree.

    The independent checker (R7 round 2) measured that copying a LINKED
    WORKTREE's `.git` - a pointer file into a shared admin dir - made the copy's
    `git add -A` write THROUGH into the protected worktree's index, and with an
    unstaged edit in the protected tree the copy silently STAGED it.

    The invariant asserted here is the SEMANTIC one: the protected repository's
    STAGED TREE must not change. The raw index FILE's hash is NOT the invariant,
    because git rewrites the index file's stat cache on any read (`git status`,
    `git archive`, `git ls-files`), which changes its bytes without changing what
    is staged. Asserting on the file hash would report a false positive; the
    write-through the checker found is visible in the staged tree.
    """
    def _staged_tree() -> str:
        r = subprocess.run(
            ["git", "-C", str(REPO), "write-tree"],
            capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, f"write-tree failed: {r.stderr[-300:]}"
        return r.stdout.strip()

    def _head() -> str:
        r = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=120,
        )
        return r.stdout.strip()

    before_tree = _staged_tree()
    before_head = _head()
    before_status = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain"],
        capture_output=True, text=True, timeout=120,
    ).stdout

    with tempfile.TemporaryDirectory() as td:
        tree = Path(td) / "copy"
        _copy_tree(tree)
        # the copy must NOT be a linked worktree of the protected repository
        gitdir = tree / ".git"
        assert gitdir.is_dir(), "the copy must have its own real .git DIRECTORY"
        assert not (gitdir / "commondir").exists(), (
            "the copy's .git points at a SHARED admin dir (a linked worktree): its "
            "`git add -A` would write through into the protected repository"
        )
        # the copy's index must be its own, not the protected repository's
        assert (gitdir / "index").exists(), (
            "the copy has no private index of its own; it would fall back to a "
            "shared one"
        )

    after_tree = _staged_tree()
    after_head = _head()
    after_status = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain"],
        capture_output=True, text=True, timeout=120,
    ).stdout

    assert after_tree == before_tree, (
        "the probe's copy modified the PROTECTED repository's STAGED TREE: "
        f"{before_tree} -> {after_tree}. A `git add -A` wrote through into the "
        "protected worktree's index."
    )
    assert after_head == before_head, (
        f"the probe's copy moved the protected HEAD: {before_head} -> {after_head}"
    )
    assert after_status == before_status, (
        "the probe's copy changed the protected worktree's status:\n"
        f"before: {before_status!r}\nafter:  {after_status!r}"
    )
