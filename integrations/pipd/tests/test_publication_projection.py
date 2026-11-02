"""Guard the R4/W1 publication projection + subject attestation (R3-EXT-01, R-AUD-006/014).

These tests pin the *subject separation* defect: the local evidence manifest is sealed against the
frozen local candidate ``10cb3d31...`` (tree ``bba26ad0...``), while the published GitHub subject is
``3aebbbce...`` (tree ``1a7dc57f...``). Reading the local seal as a statement about the published
subject must FAIL. Concretely:

* the product paths of the two subjects are byte-identical;
* an attestation built for the local candidate fails verification against the published subject;
* marking a private ``.hgk/rounds/...`` path as public fails ``--check``;
* the projection's counts reconcile to the local manifest, and every entry has one disposition + reason.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import build_publication_manifest as B  # noqa: E402
import publication_attestation as A  # noqa: E402

PUB_COMMIT = "3aebbbce948871c07b875ab92acf263d298ecf38"
PUB_TREE = "1a7dc57f9403202c32d1bc01deb1925ac1f6412e"
# The R3 frozen candidate was a *local-only* commit: it is the pre-publication state of the authoring
# repository and was never pushed, so it does not exist in any clone. These tests assert properties of
# that tuple (the two subjects must be distinct yet product-equal), so they can only run where such a
# pair is actually present. Both are overridable so an operator can point them at a real equivalent.
FROZEN_COMMIT = os.environ.get("PIPD_FROZEN_COMMIT") or "10cb3d31fcbd54fffe64152f4b17085866d0d75e"
FROZEN_TREE = os.environ.get("PIPD_FROZEN_TREE") or "bba26ad0634e46169270e81109f9db22c967602a"

MANIFEST = ROOT / ".hgk" / "artifacts" / "evidence_manifest.json"
PROJECTION = ROOT / ".hgk" / "ao" / "pub" / "PUBLICATION_PROJECTION_MANIFEST.json"
ATTESTATION = ROOT / ".hgk" / "ao" / "pub" / "PUBLICATION_SUBJECT_ATTESTATION.json"


def setUpModule() -> None:
    """Skip -- with the offending object named -- when the tuple under test is not in this store.

    An error here would say "the tool is broken". The truth is narrower and worth stating exactly:
    the tool is fine, the *fixture* is absent, because the R3 frozen candidate was never published.
    """
    missing = [s for s in (PUB_COMMIT, PUB_TREE, FROZEN_COMMIT, FROZEN_TREE) if not B.object_exists(s)]
    if missing:
        raise unittest.SkipTest(
            "these tests assert properties of a two-subject publication tuple; "
            + ", ".join(missing)
            + " is not in this object store. The R3 frozen candidate was local-only and never "
            "published, so it is absent from every clone. Run them in the authoring repository, or "
            "set PIPD_FROZEN_COMMIT/PIPD_FROZEN_TREE to an equivalent pair that is present."
        )
    # S4EXT-R1 AO finding C5: the objects can exist while the *ref* the gate resolves does not.
    # The gate pins the local branch `r5-s4-candidate`, which was never pushed, so in a clean-room
    # clone the tool exits FAIL and these tests reported a red suite instead of an absent fixture.
    unresolvable = []
    for ref in ("r5-s4-candidate",):
        try:
            B.resolve_ref(ref)
        except Exception:
            unresolvable.append(ref)
    if unresolvable:
        raise unittest.SkipTest(
            "the publication gate resolves the local branch ref(s) "
            + ", ".join(unresolvable)
            + ", which were never pushed and therefore do not exist in any clone. The gate cannot "
            "pass here whatever the candidate contains, so these tests assert nothing in this "
            "environment: run them in the authoring repository, or create an equivalent ref."
        )


class ProductPathEquality(unittest.TestCase):
    """Brief constraint 1: product paths are byte-identical across the two subjects."""

    def test_published_and_frozen_product_paths_are_byte_identical(self) -> None:
        pub = B.walk_tree(PUB_TREE)
        frz = B.walk_tree(FROZEN_TREE)
        pub_product = {p: B.blob_content_sha256(oid) for p, oid in pub.items() if B.is_product_path(p)}
        frz_product = {p: B.blob_content_sha256(oid) for p, oid in frz.items() if B.is_product_path(p)}

        self.assertEqual(set(pub_product), set(frz_product), "product path sets differ")
        drift = {p for p in pub_product if pub_product[p] != frz_product[p]}
        self.assertEqual(drift, set(), f"product paths differ by content: {sorted(drift)[:5]}")
        self.assertEqual(B.product_digest(pub), B.product_digest(frz))

    def test_subjects_are_distinct_but_product_equal(self) -> None:
        # The two subjects really are different commits/trees ...
        self.assertNotEqual(PUB_COMMIT, FROZEN_COMMIT)
        self.assertNotEqual(PUB_TREE, FROZEN_TREE)
        # ... yet their full-tree manifest digests differ (proving the trees are not the same).
        self.assertNotEqual(B.manifest_digest(PUB_TREE), B.manifest_digest(FROZEN_TREE))


class AttestationSubjectSeparation(unittest.TestCase):
    """Brief constraint 2: a local-candidate attestation must fail against the published subject."""

    def test_local_candidate_attestation_fails_against_published_subject(self) -> None:
        doc = A.build_document(commit=FROZEN_COMMIT, tree=FROZEN_TREE)
        # The document is internally consistent (no tamper) ...
        self.assertEqual(doc["product_digest"], B.product_digest(FROZEN_TREE))
        # ... but it must NOT verify as the published subject.
        violations = A.verify_document(doc, expect_commit=PUB_COMMIT, expect_tree=PUB_TREE)
        self.assertTrue(violations, "a local-candidate attestation verified against the published subject")
        joined = " ".join(violations)
        self.assertIn("SUBJECT_COMMIT_MISMATCH", joined)
        self.assertIn("SUBJECT_TREE_MISMATCH", joined)

    def test_published_attestation_verifies_against_published_subject(self) -> None:
        doc = A.build_document(commit=PUB_COMMIT, tree=PUB_TREE)
        self.assertEqual(A.verify_document(doc, expect_commit=PUB_COMMIT, expect_tree=PUB_TREE), [])

    def test_cli_build_for_local_candidate_then_verify_against_published_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "att.json"
            build = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "publication_attestation.py"),
                 "--build", "--commit", FROZEN_COMMIT, "--tree", FROZEN_TREE, "--out", str(out)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            verify = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "publication_attestation.py"),
                 "--verify", "--out", str(out)],  # default --expect-* is the published subject
                capture_output=True, text=True,
            )
            self.assertNotEqual(verify.returncode, 0, "local-candidate attestation must not verify as published")
            self.assertIn("SUBJECT_", verify.stdout)


class PrivatePathMustNotBePublic(unittest.TestCase):
    """Brief constraint 3: marking a private R2 worktree path as public fails ``--check``."""

    def _private_rounds_path(self, projection: dict) -> str:
        for path, entry in projection["entries"].items():
            if path.startswith(".hgk/rounds/") and entry["disposition"] == "NOT_PUBLISHED":
                return path
        self.fail("no private .hgk/rounds NOT_PUBLISHED entry found to mutate")

    def test_promoting_a_private_rounds_path_to_public_fails_check(self) -> None:
        self.assertTrue(PROJECTION.exists(), "projection manifest missing; run --write first")
        projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
        victim = self._private_rounds_path(projection)

        projection["entries"][victim]["disposition"] = "PUBLIC_IN_PUBLISHED_TREE"
        projection["entries"][victim]["published_blob_sha256"] = "0" * 64

        violations = B.run_check(projection)
        self.assertTrue(violations, "promoting a private path to PUBLIC did not fail --check")
        self.assertTrue(any("PUBLIC_NOT_IN_TREE" in v and victim in v for v in violations), violations)

    def test_checker_flags_a_seal_named_as_the_published_subject(self) -> None:
        # Brief rule 4: a seal/manifest that names a *different* candidate must not assert the
        # published subject. The published subject is read from the projection itself, so this test
        # does not hard-code one round's tuple (the shipped projection moved from R3 to R5 and the
        # R3 constants would silently stop asserting anything).
        projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
        published = projection["published_subject"]
        manifest, _ = B.load_evidence_manifest()
        foreign_seal = {
            "candidate": {
                "repo_commit_sha": published["commit"],
                "candidate_tree_sha": published["tree"],
            }
        }
        violations = B.check_projection(
            projection,
            manifest=manifest,
            seal=foreign_seal,
            published_tree_map=B.walk_tree(published["tree"]),
            frozen_tree_map=B.walk_tree(published["tree"]),
        )
        self.assertTrue(any("SEAL_SUBJECT_CONFLATION" in v for v in violations), violations)

    def test_cli_check_on_a_mutated_projection_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
            victim = self._private_rounds_path(projection)
            projection["entries"][victim]["disposition"] = "PUBLIC_IN_PUBLISHED_TREE"
            projection["entries"][victim]["published_blob_sha256"] = "0" * 64
            mutated = Path(tmp) / "PUBLICATION_PROJECTION_MANIFEST.json"
            mutated.write_text(json.dumps(projection), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-c",
                 "import sys,json;sys.path.insert(0,%r);"
                 "import build_publication_manifest as B;"
                 "p=json.load(open(%r));v=B.run_check(p);"
                 "print(json.dumps(v));sys.exit(1 if v else 0)"
                 % (str(ROOT / "tools"), str(mutated))],
                capture_output=True, text=True,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout)


class ProjectionReconciliation(unittest.TestCase):
    """Brief constraint 4: counts reconcile; every entry has exactly one disposition and a reason."""

    def setUp(self) -> None:
        self.assertTrue(PROJECTION.exists(), "projection manifest missing; run --write first")
        self.projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
        self.manifest, _ = B.load_evidence_manifest()
        self.entries = self.projection["entries"]

    def test_counts_reconcile_to_local_manifest_total(self) -> None:
        counts = self.projection["counts"]
        self.assertEqual(counts["total"], len(self.manifest))
        self.assertEqual(counts["total"], len(self.entries))
        per_disposition = sum(counts[d] for d in B.DISPOSITIONS)
        self.assertEqual(counts["total"], per_disposition)
        self.assertEqual(counts["total"], sum(c for d, c in counts.items() if d != "total"))

    def test_every_entry_has_one_disposition_and_a_reason(self) -> None:
        for path, entry in self.entries.items():
            self.assertIn(entry["disposition"], B.DISPOSITIONS, path)
            self.assertTrue(entry.get("reason"), f"{path} has no reason")
            self.assertTrue(entry.get("reference"), f"{path} has no reference")
            if entry["disposition"] == "PUBLIC_IN_PUBLISHED_TREE":
                self.assertTrue(entry.get("published_blob_sha256"), f"{path} public but no digest")
            else:
                self.assertIsNone(entry.get("published_blob_sha256"), f"{path} non-public but has digest")

    def test_no_entry_silently_dropped(self) -> None:
        self.assertEqual(set(self.entries), set(self.manifest))

    def test_projection_check_passes_clean(self) -> None:
        self.assertEqual(B.run_check(self.projection), [])


class CliSmoke(unittest.TestCase):
    def test_write_then_check_exits_zero(self) -> None:
        # The gate has no --out option, so preserve the repository projection bytes and restore
        # them afterwards: running the suite must never leave PUBLICATION_PROJECTION_MANIFEST.json
        # rewritten (its digest is part of the frozen publication record).
        original = PROJECTION.read_bytes() if PROJECTION.exists() else None
        try:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "build_publication_manifest.py"), "--write", "--check"],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn('"verdict": "PASS"', proc.stdout)
        finally:
            if original is not None:
                PROJECTION.write_bytes(original)
            elif PROJECTION.exists():
                PROJECTION.unlink()


class CurrentTreeCoverage(unittest.TestCase):
    """W9: a passing published-subject check must not silently omit the current tree."""

    def test_check_always_prints_current_tree_coverage(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_publication_manifest.py"), "--check"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("current_tree_coverage", proc.stdout)
        report = json.loads(proc.stdout)
        self.assertIn("subject_scope", report)
        self.assertEqual(report["subject_scope"]["scope"], "PUBLISHED_SUBJECT")
        self.assertIn("uncovered_count", report["current_tree_coverage"])

    def test_current_check_fails_while_any_current_product_path_is_uncovered(self) -> None:
        block, violations = B.check_current_coverage()
        self.assertTrue(block["uncovered_count"] > 0,
                        "expected some current product path without a disposition")
        self.assertTrue(any("CURRENT_TREE_UNCOVERED" in v for v in violations), violations)
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_publication_manifest.py"),
             "--check", "--current"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(proc.returncode, 0, "an uncovered current path must fail --current")
        self.assertIn("CURRENT_TREE_UNCOVERED", proc.stdout)

    def test_an_injected_uncovered_path_fails_current(self) -> None:
        # A synthetic current product path with no disposition produces a non-zero --current result.
        entries = {p: {"disposition": "NOT_PUBLISHED"}
                   for p in B.current_product_paths()}
        entries.pop("tools/pi_dedup_check.py", None)  # simulate an omitted current product file
        block, violations = B.check_current_coverage(entries=entries)
        self.assertIn("tools/pi_dedup_check.py", block["uncovered"])
        self.assertTrue(any("tools/pi_dedup_check.py" in v for v in violations), violations)

    def test_attestation_build_then_verify_exits_zero(self) -> None:
        # The attestation CLI has an --out option; write the sidecar to a temp dir so the frozen
        # repository bytes are never touched.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "PUBLICATION_SUBJECT_ATTESTATION.json"
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "publication_attestation.py"),
                 "--build", "--verify", "--out", str(out)],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn('"verdict": "PASS"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
