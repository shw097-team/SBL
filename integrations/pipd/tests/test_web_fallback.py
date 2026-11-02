"""Stage B lane B2: the Web fallback single-document projection.

Exercises ``tools/build_web_fallback.py`` end to end against temp-directory mount packs. Nothing
here touches the network or the real repository tree: every fixture is authored under a
``tempfile.TemporaryDirectory`` and every pack is a small ``MANIFEST.sha256`` plus its members.

The tool reproduces one frozen mount pack into ONE bounded markdown document
(``DOC_MOUNT_ONLY``) and is fail-closed. The cases below pin the positive exact projection and the
refusals:

 1. exact projection: verbatim member bytes, member inventory table, ``DOC_MOUNT_ONLY`` stamp
 2. stale release stamp (only the release id, or only the pinned commit, is REFUSED)
 3. over-cap composition REFUSED, and the destination is never created (no truncation)
 4. member digest disagreeing with ``MANIFEST.sha256`` REFUSED
 5. an unexpected extra file REFUSED; a manifest entry with no file REFUSED
 6. an existing destination REFUSED with its bytes unchanged (``O_EXCL``)
 7. a symlinked destination REFUSED, with the file behind it byte-identical
 8. a symlinked manifest / symlinked member REFUSED; a member path escaping the root REFUSED
 9. a non-UTF-8 / non-text member REFUSED
10. the CLI ``main()`` refusal path exits non-zero and refuses above-cap output instead of trimming

The fixtures are authored as LF-only UTF-8, which is exactly the canonical byte sequence the pack
builder ``tools/build_mount_pack.py`` hashes (EOL-normalised text members), so a member's manifest
digest is simply ``sha256`` of the bytes written here.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _entry in (str(ROOT), str(ROOT / "src")):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from tools import build_web_fallback as WFB  # noqa: E402

# Call the module's real entry point exactly once, resolved by name. The brief names it ``build()``;
# the tool currently exposes ``build_fallback()``. Never a re-implementation.
build = getattr(WFB, "build", None) or WFB.build_fallback

RELEASE_ID = "v0.1.1-preview.3"
RELEASE_COMMIT = "9f1c0b3d5e7a2468ac5df1b9c3e70d4f6a8b0c2e"


# --------------------------------------------------------------------------- fixture helpers

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_text(entries: list[tuple[str, bytes]]) -> str:
    return "".join(f"{_sha256(data)}  {rel}\n" for rel, data in entries)


def _write_pack(root: Path, members: dict[str, bytes], *, manifest: str | None = None) -> Path:
    """Author a mount pack: member files (LF bytes verbatim) plus a derived ``MANIFEST.sha256``."""
    root.mkdir(parents=True, exist_ok=True)
    for rel, data in members.items():
        member = root / rel
        member.parent.mkdir(parents=True, exist_ok=True)
        member.write_bytes(data)
    text = manifest if manifest is not None else _manifest_text(list(members.items()))
    (root / WFB.MANIFEST_NAME).write_bytes(text.encode("utf-8"))
    return root


def _stamp(name: str, extra: str = "") -> bytes:
    """A member document carrying BOTH the pinned release id and the pinned commit."""
    text = (f"# {name}\n\n"
            f"- release_id: {RELEASE_ID}\n"
            f"- release_commit: {RELEASE_COMMIT}\n\n"
            f"Verbatim body for {name}.\n{extra}")
    return text.encode("utf-8")


_SYMLINK_PROBE: list = [None]


def _symlinks_supported() -> bool:
    """Whether this host can actually create a symlink (Windows often cannot without privilege)."""
    if _SYMLINK_PROBE[0] is None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.write_bytes(b"x")
            link = Path(tmp) / "link"
            try:
                os.symlink(target, link)
                _SYMLINK_PROBE[0] = os.path.islink(link)
            except (OSError, NotImplementedError, AttributeError):
                _SYMLINK_PROBE[0] = False
    return bool(_SYMLINK_PROBE[0])


@contextlib.contextmanager
def _seam_symlink(path: Path):
    """Report exactly ``path`` as a symlink through the tool's documented ``_path_is_symlink`` seam.

    Used only when the host cannot create a real symlink; the refusal gate itself is unchanged.
    """
    seam_path = os.path.abspath(str(path))
    real = WFB._path_is_symlink

    def fake(candidate):
        return os.path.abspath(str(candidate)) == seam_path or real(candidate)

    WFB._path_is_symlink = fake
    try:
        yield
    finally:
        WFB._path_is_symlink = real


class WebFallbackTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.td = Path(self._td.name)

    # ---------------------------------------------------------------- fixtures

    def members(self) -> dict[str, bytes]:
        return {
            "PIPD_A.md": _stamp("PIPD_A.md", "Alpha payload line.\n"),
            "references/PIPD_B.md": _stamp("PIPD_B.md", "Beta payload line.\n"),
        }

    def pack(self, members: dict[str, bytes] | None = None, *, manifest: str | None = None,
             name: str = "pack") -> Path:
        return _write_pack(self.td / name, members if members is not None else self.members(),
                           manifest=manifest)

    def build_pack(self, pack: Path, out: Path, *, size_cap: int = WFB.DEFAULT_SIZE_CAP) -> dict:
        return build(mount_pack=pack, release_id=RELEASE_ID, release_commit=RELEASE_COMMIT,
                     out_path=out, size_cap=size_cap)

    def assert_refused(self, pack: Path, out: Path, code: str, *,
                       size_cap: int = WFB.DEFAULT_SIZE_CAP, pre_existing_destination: bool = False):
        with self.assertRaises(WFB.Refusal) as caught:
            self.build_pack(pack, out, size_cap=size_cap)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        # A refused build must never CREATE a destination. A destination that was ALREADY there —
        # in particular an existing symlink the gate refused to follow — is not the tool's artefact:
        # the tool must leave it exactly as it found it, and deleting a user's symlink would itself
        # be a mutation. The caller asserts the byte-identity of whatever the link points at.
        # Measured: on a host that can create symlinks (hosted Linux) `.exists()` follows the link,
        # so the previous blanket `assertFalse(out.exists())` failed the very test that proves the
        # gate worked, while the Windows seam path passed.
        if pre_existing_destination:
            self.assertTrue(os.path.islink(out) or out.is_file(),
                            "a refused build must leave a pre-existing destination in place")
        else:
            self.assertFalse(out.exists(), "a refused build must not leave a destination behind")
        return caught.exception

    # ------------------------------------------------------------- 1. positive

    def test_exact_projection_verbatim_inventory_and_ceiling_stamp(self):
        members = self.members()
        pack = self.pack(members)
        out = self.td / "fallback.md"

        report = self.build_pack(pack, out)

        self.assertEqual(report["verdict"], "BUILT")
        self.assertTrue(report["doc_mount_only"])
        self.assertEqual(report["member_count"], len(members))
        self.assertEqual(report["out"], str(out))
        document = out.read_bytes()
        self.assertEqual(len(document), report["bytes"])
        self.assertEqual(_sha256(document), report["sha256"])

        # ONE markdown document, and nothing else beside it.
        self.assertEqual([p.name for p in self.td.iterdir() if p.is_file()], ["fallback.md"])

        text = document.decode("utf-8")
        self.assertIn(WFB.FALLBACK_SCHEMA, text)
        self.assertIn("DOC_MOUNT_ONLY", text)
        self.assertIn(f"- release_id: {RELEASE_ID}", text)
        self.assertIn(f"- release_commit: {RELEASE_COMMIT}", text)
        self.assertIn("## Member inventory", text)

        for rel, data in members.items():
            # inventory table row, keyed by the manifest digest
            self.assertIn(f"| {rel} | {_sha256(data)} |", text)
            # embedded section carries the source bytes verbatim
            self.assertIn(data, document)
            begin = f"<!-- BEGIN MEMBER {rel} -->\n"
            end = f"\n<!-- END MEMBER {rel} -->"
            start = text.index(begin) + len(begin)
            stop = text.index(end, start)
            self.assertEqual(text[start:stop].encode("utf-8"), data,
                             f"{rel} was not embedded verbatim")

        # Deterministic: the same inputs produce byte-identical documents (no timestamp anywhere).
        again = self.td / "fallback-again.md"
        self.build_pack(pack, again)
        self.assertEqual(out.read_bytes(), again.read_bytes())

    # ------------------------------------------------------- 2. stale release stamp

    def test_stale_stamp_release_without_pinned_commit_refused(self):
        doc = (f"# Doc\n\n- release_id: {RELEASE_ID}\n\nno pinned commit here\n").encode("utf-8")
        pack = self.pack({"PIPD_A.md": doc}, name="pack-stale-a")
        self.assert_refused(pack, self.td / "stale-a.md", "RELEASE_STAMP_MISSING")

    def test_stale_stamp_pinned_commit_without_release_refused(self):
        doc = (f"# Doc\n\n- release_commit: {RELEASE_COMMIT}\n\nno release id here\n").encode("utf-8")
        pack = self.pack({"PIPD_A.md": doc}, name="pack-stale-b")
        self.assert_refused(pack, self.td / "stale-b.md", "RELEASE_STAMP_MISSING")

    # ----------------------------------------------------------------- 3. over cap

    def test_over_cap_refused_with_no_destination_and_no_truncation(self):
        pack = self.pack()
        out = self.td / "overflow.md"
        exc = self.assert_refused(pack, out, "SIZE_CAP_EXCEEDED", size_cap=64)
        self.assertIn("refusing to truncate", exc.detail)
        self.assertFalse(out.exists(), "an over-cap build must not truncate a prefix to disk")

    # -------------------------------------------------------------- 4. digest mismatch

    def test_member_digest_mismatch_refused(self):
        members = self.members()
        manifest = (f"{_sha256(members['PIPD_A.md'])}  PIPD_A.md\n"
                    f"{'0' * 64}  references/PIPD_B.md\n")
        pack = self.pack(members, manifest=manifest, name="pack-digest")
        self.assert_refused(pack, self.td / "digest.md", "MANIFEST_DIGEST_MISMATCH")

    # ---------------------------------------------- 5. extra file / manifest entry missing

    def test_unexpected_extra_file_refused(self):
        pack = self.pack()
        (pack / "EXTRA.md").write_bytes(b"# a file the manifest never listed\n")
        self.assert_refused(pack, self.td / "extra.md", "UNEXPECTED_EXTRA_FILE")

    def test_manifest_entry_without_file_refused(self):
        members = self.members()
        manifest = _manifest_text(list(members.items()))
        pack = _write_pack(self.td / "pack-missing",
                           {"PIPD_A.md": members["PIPD_A.md"]}, manifest=manifest)
        self.assert_refused(pack, self.td / "missing.md", "MANIFEST_MEMBER_MISSING")

    # -------------------------------------------------------- 6. destination exists

    def test_existing_destination_refused_and_bytes_unchanged(self):
        pack = self.pack()
        out = self.td / "exists.md"
        before = b"# pre-existing document\nkeep every byte\n"
        out.write_bytes(before)
        with self.assertRaises(WFB.Refusal) as caught:
            self.build_pack(pack, out)
        self.assertEqual(caught.exception.code, "DESTINATION_EXISTS")
        self.assertEqual(out.read_bytes(), before, "O_EXCL must never overwrite the destination")

    # ------------------------------------------------------- 7. symlinked destination

    def test_symlinked_destination_refused_and_target_byte_identical(self):
        pack = self.pack()
        sentinel = self.td / "sentinel.md"
        sentinel_bytes = b"# sentinel behind the symlink\nmust stay byte-identical\n"
        sentinel.write_bytes(sentinel_bytes)
        dest = self.td / "link.md"

        real_symlink = _symlinks_supported()
        if real_symlink:
            os.symlink(sentinel, dest)
            ctx = contextlib.nullcontext()
        else:
            ctx = _seam_symlink(dest)  # the tool's own test seam; the gate code is unchanged
        with ctx:
            exc = self.assert_refused(pack, dest, "DESTINATION_SYMLINK",
                                      pre_existing_destination=real_symlink)
        self.assertIn("symlink", exc.detail)
        self.assertEqual(sentinel.read_bytes(), sentinel_bytes,
                         "the file behind the symlink must be untouched")
        if real_symlink:
            self.assertTrue(os.path.islink(dest))
            self.assertEqual(os.readlink(dest), str(sentinel),
                             "the pre-existing symlink must still point at the sentinel")
        else:
            self.assertFalse(dest.exists())

    # ---------------------------- 8. symlinked manifest / symlinked member / path escape

    def test_symlinked_manifest_refused(self):
        pack = self.pack()
        manifest = pack / WFB.MANIFEST_NAME
        out = self.td / "manifest-link.md"
        if _symlinks_supported():
            target = self.td / "manifest-target.txt"
            target.write_bytes(manifest.read_bytes())
            manifest.unlink()
            os.symlink(target, manifest)
            ctx = contextlib.nullcontext()
        else:
            ctx = _seam_symlink(manifest)
        with ctx:
            self.assert_refused(pack, out, "MEMBER_SYMLINK")

    def test_symlinked_member_refused(self):
        members = self.members()
        pack = self.pack(members)
        member = pack / "references/PIPD_B.md"
        out = self.td / "member-link.md"
        if _symlinks_supported():
            target = self.td / "member-target.md"
            target.write_bytes(members["references/PIPD_B.md"])
            member.unlink()
            os.symlink(target, member)
            ctx = contextlib.nullcontext()
        else:
            ctx = _seam_symlink(member)
        with ctx:
            self.assert_refused(pack, out, "MEMBER_SYMLINK")

    def test_member_path_escaping_root_refused(self):
        members = self.members()
        escape_digest = _sha256(b"# outside\n")
        manifest = _manifest_text(list(members.items())) + f"{escape_digest}  ../outside.md\n"
        pack = self.pack(members, manifest=manifest, name="pack-escape")
        self.assert_refused(pack, self.td / "escape.md", "PATH_ESCAPE")

    # --------------------------------------------------------------- 9. non-text member

    def test_non_utf8_member_refused(self):
        members = self.members()
        members["blob.bin"] = b"\xff\xfe\x00\x01\x80not utf-8 \xc3\x28\n"
        pack = self.pack(members, name="pack-binary")
        self.assert_refused(pack, self.td / "binary.md", "MEMBER_NOT_TEXT")

    # --------------------------------------------------------- 10. CLI refusal path

    def test_cli_refusal_is_nonzero_and_above_cap_is_refused_not_trimmed(self):
        pack = self.pack()
        out = self.td / "cli-overflow.md"
        argv = ["--mount-pack", str(pack), "--release-id", RELEASE_ID,
                "--release-commit", RELEASE_COMMIT, "--size-cap", "64", "--out", str(out)]
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = WFB.main(argv)
        self.assertNotEqual(rc, 0, "a refusal must exit non-zero through main()")
        self.assertIn("SIZE_CAP_EXCEEDED", stdout.getvalue())
        self.assertFalse(out.exists(), "above-cap output must be refused, never trimmed")

    def test_cli_refusal_is_nonzero_for_a_stale_stamp(self):
        doc = (f"# Doc\n\n- release_id: {RELEASE_ID}\n\nstale, no commit\n").encode("utf-8")
        pack = self.pack({"PIPD_A.md": doc}, name="pack-cli-stale")
        out = self.td / "cli-stale.md"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = WFB.main(["--mount-pack", str(pack), "--release-id", RELEASE_ID,
                           "--release-commit", RELEASE_COMMIT, "--out", str(out)])
        self.assertNotEqual(rc, 0)
        self.assertIn("RELEASE_STAMP_MISSING", stdout.getvalue())
        self.assertFalse(out.exists())

    def test_cli_builds_when_the_pack_is_clean(self):
        pack = self.pack()
        out = self.td / "cli-ok.md"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = WFB.main(["--mount-pack", str(pack), "--release-id", RELEASE_ID,
                           "--release-commit", RELEASE_COMMIT, "--out", str(out)])
        self.assertEqual(rc, 0, stdout.getvalue())
        self.assertIn("DOC_MOUNT_ONLY", stdout.getvalue())
        self.assertTrue(out.is_file())


if __name__ == "__main__":
    unittest.main()
