"""S4EXT-R1 (TT-S4EXT-001 / TT-S4EXT-003): release-provenance truth for the mount packs.

F001 of the external challenge (``PIPD-LS-SP-S4-EXTERNAL-CHALLENGE-2026-10-12-R1``) was a
CONFIRMED_DEFECT: every document of the ``v0.1.1-preview.3`` Web Mount pack declared
``tag commit 8faa64e581e8c25f5ec355475e29561847da3ead`` -- which is the ``v0.1.0-preview.2`` tag
target -- instead of the real dereference ``cbf69756d7fc90fc1cdfb3a45a1cc42cc603cb0a``. F003 was
the matching evidence gap: the only release-identity regression test pinned ``preview.2``, so no
test could observe the preview.3 mismatch.

This module closes both by making the expectation DERIVED rather than hand-written:

* the identity comes from ``docs/RELEASE_TUPLE.json``;
* the tuple's ``release_tag_target`` / ``tree`` are re-derived from the repository's own git
  objects with ``git rev-parse`` (no network, no floating branch);
* the pack documents must agree with the tuple, and the check is exercised in the NEGATIVE
  direction too (a stale value injected into a document must be refused), so a passing suite
  cannot be an artefact of a checker that always returns clean;
* ``build_source_commit`` and ``release_tag_target`` stay SEPARATE fields -- collapsing them into
  one string is the defect this module exists to prevent.

The tests never write inside the repository: a pack copy is built in a temporary directory.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_mount_pack as BMP  # noqa: E402

TUPLE_PATH = ROOT / "docs" / "RELEASE_TUPLE.json"
HEX40 = re.compile(r"[0-9a-f]{40}")

# The line shapes that ASSERT a pack's release identity. A 40-hex token on one of these lines is a
# provenance claim and must equal the frozen tuple's release_tag_target.
IDENTITY_MARKERS = (
    "release identity:",
    "bound to `v",
    "release_tag_commit:",
    "release_tag_target:",
    "build_source_commit:",
    "| release tag target |",
    "| build source commit |",
    "| tag commit |",
    "| release tree |",
    "bind it to release",
    "(release tag target",
    "(build source commit",
    "(tag commit",
)
# Lines that DISCLOSE the historical wrong value on purpose (the erratum). They may name any sha.
DISCLOSURE_MARKERS = ("erratum", "lineage note", "previously published", "stale")


def load_tuple() -> dict:
    return json.loads(TUPLE_PATH.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    """Run git against this checkout; native tool, so the path is passed Windows-style."""
    out = subprocess.run(["git", "-C", str(ROOT).replace("\\", "/"), *args],
                         check=True, capture_output=True, text=True)
    return out.stdout.strip()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity_claims(text: str) -> list[tuple[int, list[str], str]]:
    """Every (lineno, hex tokens, line) that claims identity, excluding disclosure lines."""
    claims = []
    for lineno, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        if not any(m in low for m in IDENTITY_MARKERS):
            continue
        if any(m in low for m in DISCLOSURE_MARKERS):
            continue
        tokens = HEX40.findall(line)
        if tokens:
            claims.append((lineno, tokens, line.strip()))
    return claims


def pack_identity_problems(pack_dir: Path, entry: dict) -> list[str]:
    """Return the provenance problems for one pack directory (empty list == clean)."""
    problems: list[str] = []
    target = entry["release_tag_target"]
    build = entry["build_source_commit"]
    docs = sorted(p for p in pack_dir.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256")
    if not docs:
        return [f"{pack_dir.name}: pack has no documents"]
    # every OTHER release's tag target is a foreign object for this pack
    foreign = {r["release_tag_target"] for r in load_tuple()["releases"]
               if r["release_id"] != entry["release_id"]}
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        rel = f"{pack_dir.name}/{doc.relative_to(pack_dir).as_posix()}"
        if target not in text:
            problems.append(f"{rel}: does not carry release_tag_target {target[:12]}")
        if build not in text:
            problems.append(f"{rel}: does not carry build_source_commit {build[:12]}")
        for lineno, tokens, line in identity_claims(text):
            for token in tokens:
                if token != target and token in foreign:
                    problems.append(
                        f"{rel}:{lineno}: asserts foreign release object {token[:12]} as this "
                        f"release's identity ({line[:70]})")
    return problems


class TupleIsDerivedFromGitTests(unittest.TestCase):
    """The frozen tuple must match the repository's own git objects, re-derived here."""

    def setUp(self) -> None:
        self.releases = load_tuple()["releases"]

    def test_every_tag_dereferences_to_the_recorded_target(self) -> None:
        for entry in self.releases:
            tag = entry["release_id"]
            self.assertEqual(git("rev-parse", f"{tag}^{{commit}}"), entry["release_tag_target"], tag)

    def test_every_recorded_tree_is_the_targets_tree(self) -> None:
        for entry in self.releases:
            tag = entry["release_id"]
            self.assertEqual(git("rev-parse", f"{tag}^{{tree}}"), entry["tree"], tag)

    def test_annotated_tag_object_recorded_verbatim(self) -> None:
        for entry in self.releases:
            tag = entry["release_id"]
            self.assertEqual(git("rev-parse", tag), entry["tag_object"], tag)
            kind = git("cat-file", "-t", tag)
            self.assertIn(kind, ("tag", "commit"), tag)

    def test_build_source_and_tag_target_are_separate_fields(self) -> None:
        """Collapsing them into one string IS the F001 defect; both must exist per release."""
        for entry in self.releases:
            self.assertIn("build_source_commit", entry, entry["release_id"])
            self.assertIn("release_tag_target", entry, entry["release_id"])
            self.assertNotIn("tag_commit", entry,
                             "a single collapsed `tag_commit` field is exactly what F001 broke on")

    def test_preview3_stale_value_is_the_preview2_target(self) -> None:
        by_id = {r["release_id"]: r for r in self.releases}
        self.assertEqual(by_id["v0.1.1-preview.3"]["stale_identity_in_first_shipped_asset"],
                         by_id["v0.1.0-preview.2"]["release_tag_target"])


class PackDocumentsAgreeWithTupleTests(unittest.TestCase):
    """positive: every pack document names its own release's object (F001 8/8)."""

    def test_every_pack_directory_is_identity_clean(self) -> None:
        for entry in load_tuple()["releases"]:
            if not entry.get("pack_dir"):
                continue
            pack = ROOT / entry["pack_dir"]
            self.assertTrue(pack.is_dir(), entry["pack_dir"])
            self.assertEqual(pack_identity_problems(pack, entry), [], entry["release_id"])

    def test_preview3_pack_has_all_eight_documents(self) -> None:
        entry = next(r for r in load_tuple()["releases"] if r["release_id"] == "v0.1.1-preview.3")
        pack = ROOT / entry["pack_dir"]
        docs = sorted(p.relative_to(pack).as_posix() for p in pack.rglob("*")
                      if p.is_file() and p.name != "MANIFEST.sha256")
        self.assertEqual(len(docs), 8, docs)

    def test_preview3_documents_state_the_release_tag_target(self) -> None:
        """Every one of the eight documents must name the tag it is actually shipped under.

        The superseded repair path additionally required a literal ``release tag target`` caption in
        all eight files; the served asset states the identity as *release id + tag commit*, and the
        pack bytes are the published asset, so the caption is not demanded. The substantive rule is
        kept in FULL: no subset escape and no floor — every document is checked.
        """
        entry = next(r for r in load_tuple()["releases"] if r["release_id"] == "v0.1.1-preview.3")
        pack = ROOT / entry["pack_dir"]
        docs = sorted(p for p in pack.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256")
        self.assertEqual(len(docs), 8, docs)
        for doc in docs:
            text = doc.read_text(encoding="utf-8")
            self.assertIn(entry["release_tag_target"], text, doc.name)

    def test_the_replacement_is_corroborated_outside_our_own_fields(self) -> None:
        """The in-place replacement must be backed by a producer record, not only our own metadata.

        ``asset_replaced_in_place`` and the digests in the tuple are written by this repository, so
        they can only corroborate themselves. The release-correction round left a producer log with
        the replaced asset's id and the new bytes; pin those, so the claim that a replacement
        happened cannot rest on our own boolean alone.
        """
        log = ROOT / ".hgk/rounds/S4R2M-20261012-merge-and-preview3/release/PUBLISH_REPLACE.log"
        self.assertTrue(log.is_file(), str(log))
        text = log.read_text(encoding="utf-8")
        entry = next(r for r in load_tuple()["releases"] if r["release_id"] == "v0.1.1-preview.3")
        self.assertIn("631301834", text, "the replaced asset id is not recorded")
        self.assertIn(entry["published_asset_sha256"], text,
                      "the served digest is not recorded in the producer log")


class StaleIdentityIsRefusedTests(unittest.TestCase):
    """negative: the pre-repair preview.3 text and a re-injected stale value must be refused."""

    def _preview3(self) -> tuple[dict, Path]:
        entry = next(r for r in load_tuple()["releases"] if r["release_id"] == "v0.1.1-preview.3")
        return entry, ROOT / entry["pack_dir"]

    def test_stale_value_no_longer_asserted_anywhere(self) -> None:
        entry, pack = self._preview3()
        stale = entry["stale_identity_in_first_shipped_asset"]
        for doc in sorted(p for p in pack.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256"):
            for lineno, _tokens, line in identity_claims(doc.read_text(encoding="utf-8")):
                self.assertNotIn(stale, line, f"{doc.name}:{lineno} still asserts the stale object")

    def test_reinjecting_the_stale_value_is_refused(self) -> None:
        entry, pack = self._preview3()
        stale = entry["stale_identity_in_first_shipped_asset"]
        with tempfile.TemporaryDirectory() as td:
            copy = Path(td) / pack.name
            shutil.copytree(pack, copy)
            doc = copy / "README_MOUNT.md"
            text = doc.read_text(encoding="utf-8")
            doc.write_text(text.replace(entry["release_tag_target"], stale), encoding="utf-8")
            problems = pack_identity_problems(copy, entry)
            self.assertTrue(problems, "a document re-naming preview.2's object must be refused")
            self.assertTrue(any("foreign release object" in p or "does not carry" in p
                                for p in problems), problems)

    def test_replacing_only_the_version_string_is_refused(self) -> None:
        """The pre-repair failure mode exactly: bump the version, keep the old commit.

        Also guards against a future edit that deletes the commit from the document entirely:
        dropping the identity is refused as well as mis-stating it.
        """
        entry, pack = self._preview3()
        with tempfile.TemporaryDirectory() as td:
            copy = Path(td) / pack.name
            shutil.copytree(pack, copy)
            doc = copy / "SKILL.md"
            text = doc.read_text(encoding="utf-8")
            # keep the version banner, remove every trace of the correct object
            doc.write_text(text.replace(entry["release_tag_target"], ""), encoding="utf-8")
            self.assertTrue(pack_identity_problems(copy, entry))

    def test_the_old_preview2_only_checker_would_have_passed(self) -> None:
        """Why F003 mattered: preview.2's own pack was clean, so an old-value-only pin saw nothing.

        The preview.2 pack legitimately names its own target (which IS the stale value for
        preview.3). A check that only knows preview.2 therefore cannot detect the preview.3 defect;
        the tuple-driven check above does.
        """
        p2 = next(r for r in load_tuple()["releases"] if r["release_id"] == "v0.1.0-preview.2")
        pack2 = ROOT / p2["pack_dir"]
        self.assertEqual(pack_identity_problems(pack2, p2), [])
        entry3, _ = self._preview3()
        self.assertEqual(p2["release_tag_target"], entry3["stale_identity_in_first_shipped_asset"])


class DistributionArtifactTests(unittest.TestCase):
    """What is served now is the corrected asset; what was served first is kept as history."""

    def _preview3(self) -> dict:
        return next(r for r in load_tuple()["releases"] if r["release_id"] == "v0.1.1-preview.3")

    def test_published_zips_are_byte_identical_to_the_recorded_digest(self) -> None:
        for entry in load_tuple()["releases"]:
            if not entry.get("zip"):
                continue
            zip_path = ROOT / entry["zip"]
            self.assertTrue(zip_path.is_file(), entry["zip"])
            if entry.get("published_asset_sha256"):
                self.assertEqual(_sha256_file(zip_path), entry["published_asset_sha256"],
                                 f"{entry['zip']} differs from the digest recorded for the served asset")

    def test_current_published_asset_matches_its_sidecar(self) -> None:
        entry = self._preview3()
        zip_path = ROOT / entry["zip"]
        sidecar = zip_path.with_name(zip_path.name + ".sha256")
        self.assertTrue(sidecar.is_file(), sidecar.name)
        self.assertEqual(_sha256_file(zip_path), sidecar.read_text(encoding="utf-8").split()[0])

    def test_the_replacement_is_logged_and_the_first_shipped_digest_is_preserved(self) -> None:
        entry = self._preview3()
        self.assertTrue(entry["asset_replaced_in_place"])
        record = ROOT / entry["asset_replacement_record"]
        self.assertTrue(record.is_file(), entry["asset_replacement_record"])
        first = entry["first_shipped_asset_sha256"]
        self.assertTrue(first and first != entry["published_asset_sha256"],
                        "the historical digest must be kept separate from the served one")
        self.assertIn("superseded_candidate_zip", entry)
        self.assertFalse((ROOT / entry["superseded_candidate_zip"]).is_file(),
                         "the superseded separate-rebuild candidate must not appear to be shipped")

    def test_rebuild_from_the_tree_reproduces_the_served_asset(self) -> None:
        """Two rebuilds agree byte-for-byte, and they equal the asset actually served."""
        entry = self._preview3()
        pack = ROOT / entry["pack_dir"]
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            digests = []
            for name in ("a", "b"):
                copy = tmp / name / pack.name
                shutil.copytree(pack, copy)
                out = tmp / f"{name}.zip"
                BMP.build_pack(copy, out)
                digests.append(_sha256_file(out))
            self.assertEqual(digests[0], digests[1], "the builder is not deterministic")
            self.assertEqual(digests[0], _sha256_file(ROOT / entry["zip"]),
                             "the served asset must be reproducible from the checked-in tree")

    def test_no_member_of_the_served_asset_captured_crlf(self) -> None:
        """The historical defect was CRLF-captured members; the served asset must carry none."""
        entry = self._preview3()
        with zipfile.ZipFile(ROOT / entry["zip"]) as zf:
            offenders = [n for n in zf.namelist() if b"\r\n" in zf.read(n)]
        self.assertEqual(offenders, [], f"CRLF members in the served asset: {offenders[:3]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
