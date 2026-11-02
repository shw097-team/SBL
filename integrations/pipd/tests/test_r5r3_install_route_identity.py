"""R5R3: the install route must name the bytes the release actually serves.

The defect this guards: the front page's private-plugin route named an in-repo, superseded
evidence-branch ZIP (68,355 bytes / ``2f9ae0...``) as the download, while the released asset is a
different byte string (68,357 bytes / ``545e359a...``) that the release's own ``SHA256SUMS`` carries -
and ``docs/install/README.md`` pointed at a ``RELEASE_TUPLE_*.json`` asset the release does not ship.
Nothing in the published tree recorded the served identity at all.

Derived, not hand-written: the tuple entry's tag facts are re-derived from git here, exactly as
``test_s4ext_release_provenance`` does for the earlier releases.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:  # every test file bootstraps src/ (tests/test_tooling_executes.py)
    sys.path.insert(0, str(SRC))
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
SERVED_ZIP = "545e359a5ca6abc7bcbbaa2316f8e062244ad4a132ae1ae839bc9a8e17d95d75"
SUPERSEDED_ZIP = "2f9ae010a6eba90787037a93a17e77f50bbc29dea5628f6fbe3e0f278fd2d199"
TAG = "v0.1.1-preview.4"
SERVED_RECORD_REL = "docs/install/ASSET_READBACK_v0.1.1-preview.4.json"
DISCLOSURE = ("superseded", "historical", "history", "do not install")


def git(*args: str) -> str:
    out = subprocess.run(["git", "-C", str(ROOT).replace("\\", "/"), *args],
                         check=True, capture_output=True, text=True)
    return out.stdout.strip()


class InstallRouteNamesTheServedAssetTests(unittest.TestCase):
    def test_readme_route_names_the_release_asset_and_its_served_digest(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"releases/download/{TAG}/pipd-ls-sp-public-skills.zip", text)
        self.assertIn(SERVED_ZIP, text)

    def _paragraphs(self) -> list[str]:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        return [p for p in re.split(r"\n\s*\n", text) if p.strip()]

    def test_the_download_route_paragraph_carries_the_served_digest_itself(self) -> None:
        """The digest must be bound to the download it belongs to, not merely present in the file.

        An earlier revision of this guard only asserted that the served digest appeared somewhere in
        README.md. A mutation that changed the digest inside the download paragraph still passed,
        because the correct digest survived elsewhere in the file. The binding is what matters.
        """
        for index, para in enumerate(self._paragraphs()):
            if f"releases/download/{TAG}/pipd-ls-sp-public-skills.zip" in para:
                self.assertIn(SERVED_ZIP, para,
                              f"README.md paragraph {index} names the download but not its served digest")
                return
        self.fail("README.md names no download route for the plugin ZIP")

    def test_superseded_digest_is_only_disclosed_as_superseded(self) -> None:
        """A paragraph that names the superseded ZIP must say it is superseded.

        The check is per PARAGRAPH rather than per line: a sentence naming the digest legitimately
        wraps across lines, so a per-line rule fails on a correctly worded disclosure. What must
        never happen is a paragraph presenting the superseded digest as the thing to download.
        """
        for index, para in enumerate(self._paragraphs()):
            if SUPERSEDED_ZIP in para:
                low = para.lower()
                self.assertTrue(any(m in low for m in DISCLOSURE),
                                f"README.md paragraph {index} names the superseded ZIP without saying so")

    def test_the_download_route_paragraph_never_names_the_superseded_digest(self) -> None:
        for index, para in enumerate(self._paragraphs()):
            if f"releases/download/{TAG}/pipd-ls-sp-public-skills.zip" in para:
                self.assertNotIn(SUPERSEDED_ZIP, para,
                                 f"README.md paragraph {index} names the superseded digest as the download")

    def test_install_readme_does_not_point_at_a_missing_release_asset(self) -> None:
        text = (ROOT / "docs/install/README.md").read_text(encoding="utf-8")
        self.assertNotIn("RELEASE_TUPLE_v0.1.1-preview.4.json", text)
        self.assertIn("RELEASE_TUPLE.json", text)


class TupleRecordsThePreview4IdentityTests(unittest.TestCase):
    def entry(self) -> dict:
        data = json.loads((ROOT / "docs" / "RELEASE_TUPLE.json").read_text(encoding="utf-8"))
        return next(r for r in data["releases"] if r["release_id"] == TAG)

    def test_tag_facts_re_derived_from_git(self) -> None:
        entry = self.entry()
        self.assertEqual(git("rev-parse", TAG), entry["tag_object"])
        self.assertEqual(git("rev-parse", f"{TAG}^{{commit}}"), entry["release_tag_target"])
        self.assertEqual(git("rev-parse", f"{TAG}^{{tree}}"), entry["tree"])
        self.assertNotEqual(entry["build_source_commit"], entry["release_tag_target"],
                            "the build source and the tag target are separate facts")

    def test_build_source_commit_exists_and_its_scope_is_stated(self) -> None:
        """A build-source claim must name a commit that is really in this repository, and say which
        artifact it is about. An earlier revision only checked presence and inequality, so a value
        like ``not-a-commit`` passed; and an unscoped claim silently turned wheel provenance into
        plugin-ZIP provenance."""
        entry = self.entry()
        sha = entry["build_source_commit"]
        self.assertRegex(sha, r"^[0-9a-f]{40}$", "build_source_commit must be a full commit sha")
        out = subprocess.run(["git", "-C", str(ROOT).replace("\\", "/"), "rev-parse",
                              "--verify", "--quiet", f"{sha}^{{commit}}"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, f"build_source_commit {sha} is not a commit in this repo")
        self.assertIn("build_source_scope", entry,
                      "a release that builds more than one artifact must scope its build-source claim")

    def test_every_tuple_digest_matches_the_retained_served_bytes(self) -> None:
        """Cross-check the recorded identities against the served-byte readback that ships beside
        them, and require the tuple to be COMPLETE against the release's own checksum list."""
        record = json.loads((ROOT / SERVED_RECORD_REL).read_text(encoding="utf-8"))
        served = record["assets"]
        entry = self.entry()
        self.assertEqual(set(entry["served_assets"]), set(served),
                         "the tuple must list every served asset of this release, and no other name")
        for name, meta in entry["served_assets"].items():
            self.assertEqual(meta, served[name], name)
        listed_in_sums = set(record["sha256sums_entries"])
        self.assertEqual(sorted(listed_in_sums - set(entry["served_assets"])), [],
                         "an entry of the release's SHA256SUMS is missing from the tuple")

    def test_served_asset_digests_are_recorded(self) -> None:
        entry = self.entry()
        self.assertEqual(entry["served_assets"]["pipd-ls-sp-public-skills.zip"]["sha256"], SERVED_ZIP)
        self.assertEqual(entry["published_asset_sha256"], SERVED_ZIP)
        for name, meta in entry["served_assets"].items():
            self.assertRegex(meta["sha256"], r"^[0-9a-f]{64}$", name)
            self.assertGreater(meta["bytes"], 0, name)

    def test_the_superseded_digest_is_not_presented_as_served(self) -> None:
        entry = self.entry()
        digests = {m["sha256"] for m in entry["served_assets"].values()}
        self.assertNotIn(SUPERSEDED_ZIP, digests)


if __name__ == "__main__":
    unittest.main(verbosity=2)
