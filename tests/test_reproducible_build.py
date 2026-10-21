"""The build must be a function of the git objects, not of the checkout.

TT-R6-WHEEL-NONREPRODUCIBLE-001 measured that two builds of the SAME commit
produced different bytes, because a Windows checkout rewrote the text files to
CRLF and because zip recorded each file's mtime. These tests pin the two
properties that make the build reproducible, so a regression is caught by CI
rather than by an external acceptance round.

The assertions here are about the SOURCE CONTRACT, not about a specific digest:
a digest would change every time the product changes, and a test that must be
edited on every release is a test nobody keeps.
"""
from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _git(*args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=120
    )
    assert r.returncode == 0, f"git {args} failed: {r.stderr}"
    return r.stdout.strip()


def test_gitattributes_forces_lf_for_every_shipped_text_type():
    """A checkout must not rewrite the shipped text to CRLF."""
    attrs = REPO / ".gitattributes"
    assert attrs.exists(), ".gitattributes is missing: a Windows checkout rewrites the tree to CRLF"
    body = attrs.read_text(encoding="utf-8")
    assert "eol=lf" in body, ".gitattributes does not pin LF endings"
    # the rule must cover the text types the package actually ships
    for suffix in (".py", ".md", ".json", ".toml", ".yml", ".yaml"):
        assert suffix in body, f".gitattributes does not cover {suffix}"


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
        if Path(rel).suffix.lower() not in (".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt"):
            continue
        blob = subprocess.run(
            ["git", "-C", str(REPO), "cat-file", "blob", f"HEAD:{rel}"],
            capture_output=True,
            timeout=60,
        ).stdout
        if b"\r\n" in blob:
            offenders.append(rel)
    assert not offenders, f"these committed blobs contain CRLF: {offenders}"


def test_reproducible_build_tool_is_present_and_importable():
    """The tool is the mechanism; it must exist and expose its contract."""
    tool = REPO / "tools" / "build_reproducible.py"
    assert tool.exists(), "tools/build_reproducible.py is missing"
    body = tool.read_text(encoding="utf-8")
    # the two mechanisms that make the build reproducible must both be present
    assert "core.autocrlf=false" in body, "the tool must export with autocrlf disabled"
    assert "SOURCE_DATE_EPOCH" in body, "the tool must pin the archive timestamp"
    assert "normalise_sdist" in body, "the tool must normalise the sdist"


def test_reproducible_build_tool_pins_the_sdist_mtime_and_gzip_header():
    """A PAX mtime header survives an int mtime assignment; the tool must clear it."""
    body = (REPO / "tools" / "build_reproducible.py").read_text(encoding="utf-8")
    assert 'k != "mtime"' in body, "the tool must strip the PAX mtime header"
    assert "mtime=0" in body, "the gzip header mtime must be pinned to 0"


def test_sdist_normalisation_round_trips():
    """normalise_sdist must produce a constant member mtime and gzip header."""
    sys.path.insert(0, str(REPO / "tools"))
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_reproducible", REPO / "tools" / "build_reproducible.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    import gzip
    import io
    import tarfile
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "x"
        (src / "pkg").mkdir(parents=True)
        (src / "pkg" / "a.txt").write_text("hello", encoding="utf-8")
        with tarfile.open(src / "in.tar.gz", "w:gz") as tf:
            tf.add(src / "pkg" / "a.txt", arcname="pkg/a.txt")
        target = Path(td) / "out.tar.gz"
        target.write_bytes((src / "in.tar.gz").read_bytes())
        mod.normalise_sdist(target, 1700000000)

        raw = target.read_bytes()
        assert raw[4:8] == b"\x00\x00\x00\x00", "gzip header mtime must be 0"
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw))) as tf:
            mtimes = {m.mtime for m in tf.getmembers()}
        assert mtimes == {1700000000.0}, f"member mtimes are not constant: {mtimes}"
