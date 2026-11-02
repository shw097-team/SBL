"""A normal `git clone` stores every object in a pack, not loose.

The publication tooling used to read only `.git/objects/xx/yyyy...` and refused to look inside a
pack, with the message "no pack index is consulted offline". The stated reason for the restriction
was that the writer image has no `git` binary - i.e. no subprocess - and that does NOT require loose
objects, because an `.idx` and its `.pack` can be parsed in pure Python. The practical consequence
was that the tool was unusable and its whole test surface failed on any clone.

These tests build a real repository, force its objects into a pack, and check the reader against
`git cat-file` as an oracle. They are hermetic (their own temporary repo) so they run everywhere,
including in a fresh clone - which is exactly where the defect showed up.
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import build_publication_manifest as B  # noqa: E402

GIT = shutil.which("git")

_GIT_ID = [
    "-c",
    "user.email=t@example.invalid",
    "-c",
    "user.name=packreader",
    "-c",
    "commit.gpgsign=false",
    "-c",
    "init.defaultBranch=main",
]


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        [GIT, *_GIT_ID, *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout


@unittest.skipUnless(GIT, "git is required to build the packed fixture")
class PackedObjectReader(unittest.TestCase):
    def setUp(self) -> None:
        self._saved_git_dir = B.GIT_DIR
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        _git(self.repo, "init", "-q")
        # A few commits so that delta chains and both delta encodings have something to work with,
        # and a file big and repetitive enough that git will actually delta it.
        for step in range(4):
            (self.repo / "src").mkdir(exist_ok=True)
            (self.repo / "src" / "big.py").write_text(
                "\n".join(f"line {i} value {i % 7}" for i in range(400)) + f"\n# rev {step}\n",
                encoding="utf-8",
            )
            (self.repo / "README.md").write_text(f"# fixture rev {step}\n", encoding="utf-8")
            _git(self.repo, "add", "-A")
            _git(self.repo, "commit", "-qm", f"rev {step}")
        # Force everything into a pack and drop the loose copies: this is the state a clone is in.
        _git(self.repo, "gc", "--quiet", "--prune=now", "--aggressive")
        B.GIT_DIR = self.repo / ".git"
        B.reset_object_caches()

    def tearDown(self) -> None:
        B.GIT_DIR = self._saved_git_dir
        B.reset_object_caches()
        self.tmp.cleanup()

    def _all_objects(self) -> list[tuple[str, str, int]]:
        out = _git(self.repo, "cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype) %(objectsize)")
        return [(s, t, int(n)) for s, t, n in (line.split() for line in out.splitlines() if line)]

    def test_the_fixture_really_is_packed(self) -> None:
        """Guard the guard: if this ever stops holding, the tests below prove nothing."""
        packs = list((self.repo / ".git" / "objects" / "pack").glob("*.pack"))
        self.assertTrue(packs, "expected at least one pack after gc")
        loose = [
            p
            for p in (self.repo / ".git" / "objects").iterdir()
            if p.is_dir() and len(p.name) == 2
        ]
        self.assertEqual(loose, [], "expected no loose object directories after gc")

    def test_every_packed_object_matches_git(self) -> None:
        objects = self._all_objects()
        self.assertGreater(len(objects), 10, "fixture too small to be meaningful")
        seen_types = set()
        for sha, want_type, want_size in objects:
            obj_type, body = B.read_object(sha)
            self.assertEqual(obj_type, want_type, f"{sha}: type")
            self.assertEqual(len(body), want_size, f"{sha}: size")
            # Byte-exact against the oracle for the types the manifest digests actually consume.
            if want_type in ("tree", "commit", "tag"):
                ref = subprocess.run(
                    [GIT, "cat-file", want_type, sha], cwd=self.repo, capture_output=True, check=True
                ).stdout
                self.assertEqual(body, ref, f"{sha}: bytes")
            seen_types.add(want_type)
        self.assertIn("tree", seen_types)
        self.assertIn("commit", seen_types)
        self.assertIn("blob", seen_types)

    def test_walk_tree_and_manifest_digest_work_from_a_pack(self) -> None:
        head = _git(self.repo, "rev-parse", "HEAD").strip()
        tree = _git(self.repo, "rev-parse", "HEAD^{tree}").strip()
        self.assertEqual(B.commit_tree(head), tree)
        walked = B.walk_tree(tree)
        self.assertIn("src/big.py", walked)
        # The digest must be a pure function of the tree contents, so resolving from a pack has to
        # give the same answer as resolving from loose objects.
        digest = B.manifest_digest(walked)
        B.reset_object_caches()
        self.assertEqual(B.manifest_digest(B.walk_tree(tree)), digest)

    def test_object_exists_sees_packed_objects(self) -> None:
        head = _git(self.repo, "rev-parse", "HEAD").strip()
        self.assertTrue(B.object_exists(head))
        self.assertFalse(B.object_exists("0" * 40))

    def test_missing_object_still_refuses_with_a_typed_error(self) -> None:
        with self.assertRaises(B.GitObjectUnavailable):
            B.read_object("f" * 40)

    def test_no_subprocess_is_spawned_by_the_read_path(self) -> None:
        """The original restriction was about not shelling out; packed support must not undo it."""
        head = _git(self.repo, "rev-parse", "HEAD").strip()
        real_popen = subprocess.Popen

        def explode(*a, **k):  # pragma: no cover - only reached on failure
            raise AssertionError("read_object must not spawn a process")

        subprocess.Popen = explode  # type: ignore[assignment]
        try:
            obj_type, body = B.read_object(head)
            self.assertEqual(obj_type, "commit")
            self.assertIn(b"rev 3", body)
        finally:
            subprocess.Popen = real_popen  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()
