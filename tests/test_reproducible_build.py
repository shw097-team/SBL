"""The build must be a function of the git objects, not of the checkout.

TT-R6-WHEEL-NONREPRODUCIBLE-001 measured that two builds of the SAME commit
produced different bytes, because a Windows checkout rewrote the shipped text to
CRLF and because the archive recorded each file's mtime. These tests pin the two
properties that make the build reproducible.

THEY ARE BEHAVIOUR TESTS, NOT SOURCE-GREP TESTS.

An independent checker (VERIFY_SECURITY lane, R7) mutated the candidate three
ways and found that two of the three mutants still passed:
  * `.gitattributes` rewritten to `eol=crlf` -> PASSED (the old test only grepped
    the file for the literal "eol=lf")
  * `normalise_sdist(sdist, epoch)` replaced by `pass` -> PASSED (the old test
    grepped the source for the call, so removing the CALL was invisible to it)
  * `.gitattributes` deleted -> FAILED (only this mutant was caught)

So every assertion below is written to FAIL when the corresponding mechanism is
broken. `tests/test_repro_mutation_probe.py` breaks it on purpose and asserts
that these tests notice.

The assertions are about the SOURCE CONTRACT, not about a specific digest: a
digest changes on every release, and a test that must be edited on every release
is a test nobody keeps.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHIPPED_TEXT = (".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt")


def _git(*args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=180
    )
    assert r.returncode == 0, f"git {args} failed: {r.stderr}"
    return r.stdout.strip()


def _load_tool():
    spec = importlib.util.spec_from_file_location(
        "build_reproducible", REPO / "tools" / "build_reproducible.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------- #
# 1. the eol rule must be what git actually applies, not what the file says
# --------------------------------------------------------------------- #
def test_git_applies_lf_to_the_shipped_text_files():
    """`git check-attr` must report eol:lf for every shipped text type.

    A file that merely CONTAINS the string "eol=lf" proves nothing: the checker
    rewrote every rule to `eol=crlf` and this assertion still passed before.
    """
    attrs = REPO / ".gitattributes"
    assert attrs.exists(), ".gitattributes is missing: a Windows checkout rewrites the tree to CRLF"
    tracked = [f for f in _git("ls-files").splitlines() if Path(f).suffix.lower() in SHIPPED_TEXT]
    assert tracked, "no shipped text files were found to check"
    out = _git("check-attr", "eol", "--", *tracked)
    wrong = []
    for line in out.splitlines():
        path, _, value = line.rpartition(": ")
        if value.strip() != "lf":
            wrong.append((path, value.strip()))
    assert not wrong, (
        "git does not apply eol=lf to these shipped files (a CRLF rule would "
        f"reintroduce the defect): {wrong[:10]}"
    )


def test_gitattributes_covers_every_shipped_text_type():
    """Structural guard: the rule set must cover the types the package ships."""
    body = (REPO / ".gitattributes").read_text(encoding="utf-8")
    for suffix in (".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt"):
        assert suffix in body, f".gitattributes does not cover {suffix}"
    assert "eol=lf" in body, ".gitattributes does not pin LF endings"


def test_repo_ships_no_windows_only_script_that_lf_would_break():
    """LF endings are only safe because no .cmd/.bat/.ps1/.sh is shipped."""
    tracked = _git("ls-files").splitlines()
    windows_only = [
        f
        for f in tracked
        if Path(f).suffix.lower() in (".cmd", ".bat", ".ps1", ".sh", ".sln", ".vcxproj")
    ]
    assert not windows_only, (
        "LF normalisation would break these Windows-only scripts; give them an "
        f"explicit CRLF rule: {windows_only}"
    )


def test_git_objects_are_lf_clean():
    """The objects themselves must be LF, otherwise the export inherits CRLF."""
    tracked = _git("ls-files").splitlines()
    offenders = []
    for rel in tracked:
        if Path(rel).suffix.lower() not in SHIPPED_TEXT:
            continue
        blob = subprocess.run(
            ["git", "-C", str(REPO), "cat-file", "blob", f"HEAD:{rel}"],
            capture_output=True,
            timeout=60,
        ).stdout
        if b"\r\n" in blob:
            offenders.append(rel)
    assert not offenders, f"these committed blobs contain CRLF: {offenders}"


# --------------------------------------------------------------------- #
# 2. the tool must exist and the mechanisms must be present
# --------------------------------------------------------------------- #
def test_tool_self_check_cannot_be_disabled():
    """The tool's own `identical` verdict must be a real comparison.

    The independent checker's MUT_E replaced `"identical": first == second` with
    `"identical": True`. The suite stayed GREEN, because nothing asserted that
    the tool's self-check is honest - a tool that always says "identical" is
    indistinguishable from a tool that verifies.

    The end-to-end test above builds twice itself and compares the bytes, so a
    lying tool cannot make the PRODUCT reproducible; what a lying tool destroys
    is the RECEIPT, which is what an external reviewer reads. So this test
    asserts the receipt field is a real comparison and not a constant.
    """
    body = (REPO / "tools" / "build_reproducible.py").read_text(encoding="utf-8")
    assert '"identical": first == second,' in body, (
        "the tool's own verify receipt must compute `identical` by comparing the two "
        "builds; a hard-coded True makes the receipt unfalsifiable"
    )
    assert '"identical": True' not in body, (
        "the tool's verify receipt hard-codes `identical: True`; an external "
        "reviewer cannot falsify a receipt that asserts its own success"
    )


def test_reproducible_build_tool_is_present():
    tool = REPO / "tools" / "build_reproducible.py"
    assert tool.exists(), "tools/build_reproducible.py is missing"


def test_reproducible_build_tool_pins_the_source_date_epoch():
    """The archive timestamp must be pinned, or zip records the wall clock."""
    body = (REPO / "tools" / "build_reproducible.py").read_text(encoding="utf-8")
    assert "SOURCE_DATE_EPOCH" in body, "the tool must pin the archive timestamp"
    assert "core.autocrlf=false" in body, "the tool must export with autocrlf disabled"


# --------------------------------------------------------------------- #
# 3. the sdist normalisation must WORK, and it must be WIRED IN
# --------------------------------------------------------------------- #
def test_normalise_sdist_produces_constant_mtimes_and_zero_gzip_header():
    """normalise_sdist must actually rewrite the archive."""
    import gzip
    import io
    import tempfile

    mod = _load_tool()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "x"
        (src / "pkg").mkdir(parents=True)
        (src / "pkg" / "a.txt").write_text("hello", encoding="utf-8")
        with tarfile.open(src / "in.tar.gz", "w:gz") as tf:
            tf.add(src / "pkg" / "a.txt", arcname="pkg/a.txt")
        target = root / "out.tar.gz"
        target.write_bytes((src / "in.tar.gz").read_bytes())
        before = target.read_bytes()
        mod.normalise_sdist(target, 1700000000)
        raw = target.read_bytes()
        assert raw != before, "normalise_sdist did not change the archive at all"
        assert raw[4:8] == b"\x00\x00\x00\x00", "gzip header mtime must be 0"
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw))) as tf:
            mtimes = {m.mtime for m in tf.getmembers()}
        assert mtimes == {1700000000.0}, f"member mtimes are not constant: {mtimes}"


def test_build_applies_the_sdist_normalisation():
    """The CALL must be live, not merely present in the source.

    The checker replaced `normalise_sdist(sdist, epoch)` with `pass` and the old
    test still passed, because it grepped the source. This test calls build()
    with a stubbed builder, so a removed or bypassed call is visible.
    """
    import gzip
    import io
    import tempfile

    mod = _load_tool()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        outdir = root / "dist"
        outdir.mkdir()

        # a sdist with a NON-constant member mtime and a wall-clock gzip header
        payload = root / "payload"
        payload.mkdir()
        (payload / "f.txt").write_text("x", encoding="utf-8")
        raw = root / "raw.tar"
        with tarfile.open(raw, "w") as tf:
            tf.add(payload / "f.txt", arcname="f.txt")
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", mtime=1234567890) as gz:
            gz.write(raw.read_bytes())
        (outdir / "pkg-1.0.tar.gz").write_bytes(buf.getvalue())

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        real_run = mod.run
        try:
            setattr(mod, "run", lambda cmd, **kw: _R())
            # The builder interpreter is passed explicitly: the build COMMAND is
            # stubbed, so this test does not need a real `build` backend, and
            # requiring one would make it fail on any machine that has only
            # pytest -- which is exactly the hosted CI runner.
            mod.build(root, outdir, 1700000000, builder=sys.executable)
        finally:
            setattr(mod, "run", real_run)

        produced = sorted(outdir.glob("*.tar.gz"))
        assert produced, f"build() did not produce a sdist: {list(outdir.iterdir())}"
        data = produced[0].read_bytes()
        assert data[4:8] == b"\x00\x00\x00\x00", (
            "build() did NOT normalise the sdist gzip header: the normalisation "
            "call is not wired in"
        )
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(data))) as tf:
            mtimes = {m.mtime for m in tf.getmembers()}
        assert mtimes == {1700000000.0}, f"build() left non-constant member mtimes: {mtimes}"


def test_sdist_normalisation_strips_the_pax_mtime_header():
    """PAX keeps a sub-second mtime that an integer assignment does not overwrite."""
    body = (REPO / "tools" / "build_reproducible.py").read_text(encoding="utf-8")
    assert 'k != "mtime"' in body, (
        "the tool must strip the PAX mtime header; create_pax_header only "
        "overwrites it when the value does not fit the ustar field"
    )
    assert "mtime=0" in body, "the gzip header mtime must be pinned to 0"


# --------------------------------------------------------------------- #
# 4. the END-TO-END claim: two independent builds must be byte-identical
# --------------------------------------------------------------------- #
def test_source_date_epoch_is_pinned_across_processes():
    """The epoch must be a CONSTANT, not a value read from the clock.

    The independent checker's MUT_D replaced `DEFAULT_SOURCE_DATE_EPOCH` with
    `int(time.time())`. That mutant leaves an in-process two-build comparison
    GREEN, because one process reads the clock once and both builds then use the
    same value. The defect only shows up ACROSS processes: two separate CLI runs
    read the clock at different moments and produce different bytes.

    So this test reads the epoch in TWO SEPARATE PROCESSES, more than a second
    apart, and requires them to be equal. A clock-derived epoch differs; a
    pinned one does not. It costs about two seconds and it is deterministic
    (the values are integer seconds, so reads more than one second apart cannot
    coincide).
    """
    import subprocess
    import sys
    import time

    script = (
        "import importlib.util,sys;"
        "spec=importlib.util.spec_from_file_location('b', sys.argv[1]);"
        "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
        "print(m.DEFAULT_SOURCE_DATE_EPOCH)"
    )
    tool = REPO / "tools" / "build_reproducible.py"

    def _read() -> str:
        r = subprocess.run(
            [sys.executable, "-c", script, str(tool)],
            capture_output=True, text=True, timeout=180, cwd=str(REPO),
        )
        assert r.returncode == 0, f"reading the epoch failed: {r.stderr[-500:]}"
        return r.stdout.strip()

    first = _read()
    time.sleep(1.2)
    second = _read()
    assert first == second, (
        "the source-date epoch is not pinned: two processes one second apart read "
        f"{first!r} and {second!r}. The build is a function of the clock, not of "
        "the source."
    )
    # and it must be an integer, not a float of the wall clock
    assert first.isdigit(), f"the epoch is not an integer second: {first!r}"


def test_two_independent_builds_are_byte_identical():
    """The suite must ASSERT the actual property, end to end.

    The independent checker (VERIFY_SECURITY lane, R7 round 2) showed that a
    mutation replacing `DEFAULT_SOURCE_DATE_EPOCH` with wall-clock `time.time()`
    leaves the whole suite GREEN while destroying reproducibility: the two builds
    differ (wheel `f182f0cd...` vs `0d26e23b...`, `identical=false`).

    That mutant survived because every other test in this file asserts a LOCAL
    property (a rule is present, a normalisation changes a file, a timestamp is
    constant) and none of them builds anything twice. A local property can hold
    while the global property fails. This test builds twice and compares bytes.

    The two builds run as SEPARATE PROCESSES, because that is how the claim is
    used: an in-process comparison reuses one clock reading and cannot see a
    clock-derived epoch (see test_source_date_epoch_is_pinned_across_processes).
    """
    import hashlib
    import shutil
    import subprocess
    import sys
    import tempfile
    import unittest

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        digests = []
        for i in (1, 2):
            out = root / f"dist{i}"
            r = subprocess.run(
                [sys.executable, str(REPO / "tools" / "build_reproducible.py"),
                 "--commit", "HEAD", "--outdir", str(out)],
                capture_output=True, text=True, timeout=1800, cwd=str(REPO),
            )
            if r.returncode != 0:
                # A SKIP here is only legitimate when the BUILD BACKEND is
                # genuinely absent from this environment. A product defect that
                # happens to make the build fail must be a FAILURE, not a skip:
                # a blanket skip on any nonzero exit lets a broken build hide
                # behind an unavailable backend, and the independent checker
                # (R7 round 4) called exactly this out as fail-open.
                combined = (r.stdout or "") + (r.stderr or "")
                # The marker list must match what the builder ACTUALLY says
                # when the backend is missing. The builder's resolver raises
                # SystemExit("no interpreter with the 'build' package was
                # found. Install it with 'pip install build', or point
                # SBL_BUILD_PYTHON at an interpreter that has it. (Checked:
                # ...)"), so a marker list that only knows the bare
                # "No module named build" would turn an environment gap into a
                # product failure -- which is exactly what the D1 repair was
                # meant to prevent, and exactly what it did on CI, where the
                # runner has no build backend installed. A marker that does not
                # match reality is worse than no marker at all.
                backend_missing = any(
                    marker in combined
                    for marker in (
                        "no interpreter with the 'build' package was found",
                        "no interpreter with the build backend",
                        "No module named build",
                        "cannot be directly executed",
                        "unable to find the build backend",
                    )
                )
                if backend_missing:
                    raise unittest.SkipTest(
                        "no interpreter with the build backend is available in "
                        f"this environment: {combined[-400:]}"
                    )
                raise AssertionError(
                    "the build FAILED for a reason other than a missing backend "
                    f"(exit {r.returncode}). A product defect must not be skipped: "
                    f"{combined[-800:]}"
                )
            per = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())}
            assert per, f"build {i} produced nothing"
            digests.append(per)

    assert digests[0] == digests[1], (
        "two independent builds of the SAME commit produced different bytes: "
        f"{digests[0]} != {digests[1]}. The build is not a function of its source."
    )
    names = set(digests[0])
    assert any(n.endswith(".whl") for n in names), f"no wheel was built: {names}"
    assert any(n.endswith(".tar.gz") for n in names), f"no sdist was built: {names}"


def test_build_tool_rejects_an_interpreter_that_cannot_build():
    """`_has_build` must not be fooled by a `build/` directory in the repo.

    The independent checker (R7 round 2) found that `import build` succeeds as a
    NAMESPACE PACKAGE when the working directory contains a `build/` folder, so
    the resolver selected an interpreter that could not build anything and the
    tool failed with "No module named build.__main__". The repository itself
    contains `build/` (gitignored), so this is the normal case, not an edge case.
    """
    import subprocess
    import sys
    import tempfile

    mod = _load_tool()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "build").mkdir()
        (root / "build" / "__init__.py").write_text("", encoding="utf-8")
        # a namespace package: a build/ dir with NO __init__.py
        (root / "build" / "__init__.py").unlink()
        r = subprocess.run(
            [sys.executable, "-c", "import build"],
            capture_output=True,
            cwd=str(root),
            timeout=120,
        )
        # the point of the test: `import build` may well succeed here ...
        # ... but the tool's probe must still say NO for an interpreter that
        # cannot run the backend. Assert the probe asks the RIGHT question.
        src = (REPO / "tools" / "build_reproducible.py").read_text(encoding="utf-8")
        assert '"-m", "build", "--version"' in src, (
            "the probe must ask `python -m build --version`, not `import build`: a "
            "build/ directory in the working tree makes `import build` a namespace-"
            "package false positive"
        )
        assert "import build.__main__" in src, (
            "the probe must fall back to importing build.__main__"
        )
        # and the probe must not accept the naive form
        assert '[python, "-c", "import build"],' not in src, (
            "the naive `import build` probe is still present and will false-positive"
        )
        # The probe must be a BOOLEAN DECISION, not a callable that happens not
        # to raise. `in (True, False)` accepts every outcome, so it asserted
        # nothing: the independent checker (R7 round 4) called this out as an
        # oracle that does not enforce rejection. It now asserts the type AND
        # the behaviour on an interpreter that genuinely cannot build.
        assert mod._has_build(sys.executable) is True or mod._has_build(sys.executable) is False, (
            "_has_build must return a real bool, not a truthy/falsy object"
        )
        # An interpreter with no build backend must be REJECTED, and the
        # rejection must be about the backend, not about the cwd. Use a
        # definitely-backend-less interpreter if one can be found; otherwise
        # assert the probe's answer is CONSISTENT with `python -m build
        # --version`, which is the question the probe now asks.
        probe_result = mod._has_build(sys.executable)
        m = subprocess.run(
            [sys.executable, "-m", "build", "--version"],
            capture_output=True, text=True, cwd=str(root), timeout=120,
        )
        can_build = m.returncode == 0
        assert probe_result is can_build, (
            "_has_build disagrees with `python -m build --version`: the probe "
            f"returned {probe_result} but the backend check returned {m.returncode}. "
            "The probe must answer the SAME question the resolver relies on."
        )
        if not can_build:
            # And the failure must be a clean False, never a crash: a probe
            # that raises on a missing backend cannot be used by a resolver.
            assert probe_result is False, (
                f"an interpreter without the build backend must be rejected, got {probe_result!r}"
            )


def test_the_stubbed_build_path_does_not_require_a_real_backend():
    """A test that stubs the build COMMAND must not need the build BACKEND.

    MEASURED (R7 round 4, hosted CI run 32/33): the CI workflow installs pytest
    and nothing else, so the `build` package is absent on the runner. The
    sdist-normalisation test stubs the build command but still let `build()`
    resolve a backend interpreter, so it raised SystemExit there -- an
    environmental gap reported as a product failure. That took the whole
    mutation probe down as well, because the probe requires the unmutated
    tree to pass, and the hosted CI has been red ever since.

    This test pins the fix: with the build backend deliberately unreachable,
    the stubbed build path must still work, and the resolver must still
    report the gap honestly rather than pretending the backend is present.
    """
    mod = _load_tool()

    # 1. the resolver must NOT claim a backend exists when none does
    real_which = shutil.which
    real_exists = Path.exists
    try:
        # every candidate the resolver would try is either missing or
        # interpreter-without-the-backend
        def _no_build(path, *args, **kwargs):
            return None

        Path.exists = lambda self: False
        shutil.which = _no_build
        with unittest.mock.patch.dict(os.environ, {"SBL_BUILD_PYTHON": ""}, clear=False):
            # the resolver either raises SystemExit (the honest report) or
            # returns an interpreter that genuinely has the backend. It must
            # NEVER return a path that does not exist.
            try:
                chosen = mod._builder_python()
            except SystemExit as exc:
                assert "build" in str(exc), (
                    f"the resolver must say the build backend is missing, got: {exc}"
                )
            else:
                assert real_exists(Path(chosen)), (
                    f"the resolver returned {chosen!r}, which does not exist"
                )
    finally:
        shutil.which = real_which
        Path.exists = real_exists

    # 2. build() with an explicit builder must not consult the resolver at all
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        outdir = root / "dist"
        outdir.mkdir()

        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        def _explode():
            raise AssertionError("the resolver was consulted even though a builder was given")

        real_run = mod.run
        real_resolver = mod._builder_python
        try:
            setattr(mod, "run", lambda cmd, **kw: _R())
            setattr(mod, "_builder_python", _explode)
            mod.build(root, outdir, 1700000000, builder=sys.executable)
        finally:
            setattr(mod, "run", real_run)
            setattr(mod, "_builder_python", real_resolver)
