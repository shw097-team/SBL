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


def _isolated_git_env(dst: Path) -> dict[str, str]:
    """Build a git environment that CANNOT reach the protected repository.

    WHY: setting GIT_DIR / GIT_WORK_TREE / GIT_INDEX_FILE is not enough. git
    honours several OTHER environment variables that redirect where objects,
    refs and the common dir live. If any of them is inherited and points into
    the protected repository, the copy's own `git init` / `git add` / `git
    commit` would write into the protected git store -- the same class of
    write-through the W3 fix was meant to end. An independent audit of this
    probe (R7 SWARM worker) flagged exactly this: the environment was copied
    wholesale and only three paths were overridden.

    So: STRIP every git-location variable from the inherited environment
    before setting the ones the copy needs. The list is not exhaustive by
    hand -- it is derived from `git` s own documentation of the variables
    that relocate the repository -- and the copy is given a private
    GIT_COMMON_DIR as well, so even a stray GIT_COMMON_DIR cannot point
    back at the protected repository.
    """
    env = dict(os.environ)
    # every variable that can relocate parts of a git repository
    for var in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_COMMON_DIR",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
        "GIT_CEILING_DIRECTORIES",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    ):
        env.pop(var, None)
    env["GIT_DIR"] = str(dst / ".git")
    env["GIT_WORK_TREE"] = str(dst)
    env["GIT_INDEX_FILE"] = str(dst / ".git" / "index")
    env["GIT_COMMON_DIR"] = str(dst / ".git")
    env["GIT_AUTHOR_NAME"] = "probe"
    env["GIT_AUTHOR_EMAIL"] = "probe@invalid"
    env["GIT_COMMITTER_NAME"] = "probe"
    env["GIT_COMMITTER_EMAIL"] = "probe@invalid"
    return env


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
        # symlinks=False: a symlink is COPIED AS A REGULAR FILE containing the
        # link target path. With symlinks=True the copy would keep the link, and
        # a mutation writing to a linked file would follow it back into the
        # protected tree -- a write-through the git-level isolation does not
        # cover. An independent audit of this probe (R7 SWARM worker) flagged
        # this: the copy preserved symlinks, so the isolation was only
        # complete at the git layer.
        symlinks=False,
    )
    # A fresh, PRIVATE git dir. `git init` + a single commit of the copied
    # content gives the tests a real `ls-files` / `check-attr` / `cat-file` to
    # read, and nothing shared with the protected repository.
    env = _isolated_git_env(dst)
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


def _pytest_counts(out: str) -> tuple[int, int, int]:
    """Parse pytest's summary line into (collected, failed, errored).

    WHY: the probe must distinguish "a test FAILED because the mutation broke
    the contract" from "pytest could not even collect the tests". Both give a
    nonzero exit, but only the first is evidence that the oracle works. The
    independent checker (R7 round 4) called the un-discriminated version out as
    a weak oracle that lets an infrastructure error masquerade as a kill.

    pytest's short summary line looks like:
        3 failed, 1 passed, 12 skipped in 4.2s
    and a collection error produces:
        ERRORS: 2 errors during collection
    or simply "no tests ran".
    """
    import re

    collected = failed = errored = 0
    m = re.search(r"(\d+)\s+(?:failed|passed|skipped|error|xfailed|xpassed)\b", out)
    # take the counts from the FINAL summary line, not the first match
    summary_lines = [l for l in out.splitlines() if re.search(r"\bin [\d.]+s\b", l)]
    if summary_lines:
        tail = summary_lines[-1]
        for key, pat in (("collected", r"(\d+)\s+collected"),
                         ("failed", r"(\d+)\s+failed"),
                         ("errored", r"(\d+)\s+error")):
            mm = re.search(pat, tail)
            if mm:
                v = int(mm.group(1))
                if key == "collected":
                    collected = v
                elif key == "failed":
                    failed = v
                else:
                    errored = v
        # "N failed" without "N collected" still implies N collected
        if not collected:
            collected = failed + errored
    if not collected and re.search(r"no tests ran", out, re.I):
        collected = 0
    # a collection error section
    if re.search(r"ERRORS?[:\s].*during collection|errors? during collection", out, re.I):
        err = re.search(r"(\d+)\s+error", out, re.I)
        if err:
            errored = max(errored, int(err.group(1)))
    if failed or errored:
        collected = max(collected, failed + errored)
    return collected, failed, errored


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
            # A mutant is only "caught" if the suite FAILED. A nonzero exit
            # that is a COLLECTION or INFRASTRUCTURE error is not a kill: the
            # test file itself broke, so nothing was proven about the product.
            # The independent checker (R7 round 4) called this out: treating
            # any nonzero exit as a catch lets a broken harness masquerade as
            # a working oracle.
            if rc != 0:
                collected, failed, errored = _pytest_counts(out)
                assert collected > 0, (
                    f"the mutation {name} ({rel}) produced a nonzero exit with ZERO "
                    f"collected tests -- that is a collection/infrastructure error, not "
                    f"a caught mutation. The probe would claim a kill it did not "
                    f"measure.\n{out[-2000:]}"
                )
                assert failed + errored > 0, (
                    f"the mutation {name} ({rel}) exited {rc} but no test FAILED "
                    f"(collected={collected}, failed={failed}, errors={errored}); "
                    f"the exit did not come from a test failure.\n{out[-2000:]}"
                )
            else:
                raise AssertionError(
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

    # The invariant can only be measured with git present. Without it the
    # test must SKIP, not fail: "git is not installed" is an environment gap,
    # and reporting it as a product defect would be the same fail-open mistake
    # the D1 repair was about. Measured on a machine whose PATH had no git:
    # the helper raised FileNotFoundError and the test FAILED.
    if shutil.which("git") is None:
        import pytest

        pytest.skip("git is not on PATH; the write-through invariant cannot be measured")
    if not (REPO / ".git").exists():
        import pytest

        pytest.skip("the candidate is not a git repository; the invariant cannot be measured")

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
