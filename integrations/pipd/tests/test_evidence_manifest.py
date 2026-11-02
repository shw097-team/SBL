"""Guard the R-AUD-014 / FW-11 evidence-manifest and secret-scan repairs.

Two audited defects are pinned here:

* the evidence manifest used to list and hash its OWN file (a self-hash cycle) and a bare path list
  was treated as independent evidence. The manifest must exclude itself and its seal, and a manifest
  that references either must be refused with a typed reason; a seal bound to a foreign or stale
  candidate head must be refused too; and the byte-level sha256 must be reproducible by readback.
* the working tree AND the git history must both be scanned for token-like strings, while the tool
  prints ONLY counts and status codes -- never a matched value and never a token prefix.

Dummy credentials are assembled from fragments on purpose (like `workspace.py` does): writing a
credential-shaped literal into a source file makes the environment's secret redactor rewrite it.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import build_evidence_manifest as M  # noqa: E402
import history_secret_scan as H  # noqa: E402


def _dummy_tokens() -> dict[str, str]:
    """Build obviously-fake token-shaped strings from fragments (redactor-safe)."""
    return {
        # github classic: gh[pousr]_ + >=20 [A-Za-z0-9_] chars
        "github_classic": "gh" + "p_" + "A" * 36,
        # openai: sk- + >=20 token chars
        "openai_sk": "sk" + "-" + "B" * 30,
        # aws: AKIA + 16 [0-9A-Z]
        "aws_access_key": "AKI" + "A" + "0" * 16,
        # bearer header: authorization: bearer <>=20 token chars
        "bearer_literal": "author" + "ization: bea" + "rer " + "C" * 30,
        "private_key_block": "-----BEGIN " + "RSA " + "PRIVATE KEY-----",
    }


class EvidenceManifestSelfExclusion(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = ROOT / ".hgk" / "artifacts" / "evidence_manifest.json"
        self.seal = ROOT / ".hgk" / "artifacts" / "evidence_manifest.seal.json"

    def test_manifest_never_lists_itself_or_its_seal(self) -> None:
        entries = json.loads(self.manifest.read_text(encoding="utf-8"))
        forbidden = {".hgk/artifacts/evidence_manifest.json",
                     ".hgk/artifacts/evidence_manifest.seal.json"}
        leaked = sorted(p for p in entries if p in forbidden)
        self.assertEqual(leaked, [], "the manifest lists its own file or seal (self-hash cycle)")

    def test_self_referential_manifest_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            man = tmp / "manifest.json"
            seal = tmp / "seal.json"
            # The manifest lists its OWN basename: the canonical self-reference defect.
            man.write_bytes(json.dumps({"manifest.json": "0" * 64}).encode("utf-8"))
            seal.write_text(json.dumps({"manifest": {"sha256": "0" * 64}}), encoding="utf-8")
            res = M.verify(manifest_path=man, seal_path=seal)
            self.assertEqual(res["status"], "FAIL")
            self.assertEqual(res["reason_code"], "SELF_REFERENTIAL_MANIFEST", res)

    def test_foreign_or_stale_manifest_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            man = tmp / "manifest.json"
            seal = tmp / "seal.json"
            body = json.dumps({"src/x.py": "a" * 64}).encode("utf-8")
            man.write_bytes(body)
            sha = M._sha256_bytes(body)
            seal.write_text(json.dumps({
                "schema": "PIPD-EVIDENCE-MANIFEST-SEAL/1",
                "seal_algorithm": "sha256",
                "manifest": {"sha256": sha, "bytes": len(body), "entries": 1},
                "candidate": {"repo_commit_sha": "aaaa"},
            }), encoding="utf-8")
            # Matching head: the same manifest verifies.
            ok = M.verify(manifest_path=man, seal_path=seal, head="aaaa")
            self.assertEqual(ok["status"], "PASS", ok)
            # A different current candidate head is a foreign/stale manifest: typed refusal.
            bad = M.verify(manifest_path=man, seal_path=seal, head="bbbb")
            self.assertEqual(bad["status"], "FAIL")
            self.assertEqual(bad["reason_code"], "REFUSED_STALE_OR_FOREIGN_MANIFEST", bad)

    def test_byte_level_hash_readback_matches(self) -> None:
        self.assertTrue(self.manifest.exists(), "run tools/build_evidence_manifest.py --seal")
        self.assertTrue(self.seal.exists(), "run tools/build_evidence_manifest.py --seal")
        data = self.manifest.read_bytes()
        seal_doc = json.loads(self.seal.read_text(encoding="utf-8"))
        # Recomputed byte-level sha256 must equal the value recorded in the outer seal.
        self.assertEqual(M._sha256_bytes(data), seal_doc["manifest"]["sha256"])
        self.assertEqual(seal_doc["seal_algorithm"], "sha256")
        # verify() reads the seal against the CURRENT head, so its verdict is only meaningful where
        # head still is the commit the seal was made at. In a clone it is not: the seal pins the
        # candidate commit and later publication commits moved the tip. That is the tool working
        # (typed REFUSED_STALE_OR_FOREIGN_MANIFEST), not the tool failing - so do not assert PASS
        # here; the refusal mechanism is covered hermetically by the neighbouring test. The
        # byte-level assertions above hold everywhere and are kept.
        sealed_head = (seal_doc.get("candidate") or {}).get("repo_commit_sha")
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
        ).stdout.strip()
        if sealed_head and head and sealed_head != head:
            self.skipTest(
                f"seal was made at {sealed_head[:12]} but HEAD is {head[:12]}; "
                "re-run tools/build_evidence_manifest.py --seal at this commit to assert the read-back"
            )
        res = M.verify()
        self.assertEqual(res["status"], "PASS", res)
        self.assertEqual(res["manifest_sha256"], seal_doc["manifest"]["sha256"])


class HistorySecretScanProjection(unittest.TestCase):
    def test_scan_finds_planted_dummy_patterns(self) -> None:
        tokens = _dummy_tokens()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "planted.py").write_text(
                "a = '{}'\nb = '{}'\nc = '{}'\nd = {}\ne = '''{}'''\n".format(
                    tokens["github_classic"], tokens["openai_sk"], tokens["aws_access_key"],
                    repr(tokens["bearer_literal"]), tokens["private_key_block"]),
                encoding="utf-8")
            totals, file_hits, files = H.scan_worktree(root=root)
        self.assertGreaterEqual(files, 1)
        for name in tokens:
            self.assertGreaterEqual(totals.get(name, 0), 1, f"scan missed planted {name}")

    def test_scan_prints_only_counts_and_status_codes(self) -> None:
        tokens = _dummy_tokens()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "planted.py").write_text(
                "x = '{0}' y = {1!r}\n".format(tokens["github_classic"], tokens["bearer_literal"]),
                encoding="utf-8")
            totals, file_hits, files = H.scan_worktree(root=root)

        out = {
            "source_revision_scanned": "0" * 40,
            "source_sha256": "0" * 64,
            "pattern_names": sorted(totals),
            "objects_listed": 0,
            "worktree_files_scanned": files,
            "history_hits_total": 0,
            "worktree_hits_total": sum(totals.values()),
            "status_codes": {"history": "CLEAN", "worktree": "HITS"},
            "verdict": "FAIL",
        }
        printed = json.dumps(H.printable_summary(out), ensure_ascii=False)
        artifact_projection = json.dumps(
            {"worktree_hits": file_hits, "totals": totals}, ensure_ascii=False)
        for label, text in (("printed summary", printed),
                            ("scanned projection", artifact_projection)):
            for token in tokens.values():
                self.assertNotIn(token, text, f"{label} leaked a matched value")
            for prefix in ("ghp_", "gho_", "ghs_", "sk-", "AKIA", "authorization", "bearer ",
                           "BEGIN RSA", "PRIVATE KEY"):
                self.assertNotIn(prefix, text, f"{label} leaked a token prefix {prefix!r}")
        # The per-file keys carry only the pattern NAME plus the path, never a matched value.
        for key in file_hits:
            self.assertRegex(key, r"^[a-z_]+::")
            for token in tokens.values():
                self.assertNotIn(token, key)


if __name__ == "__main__":
    unittest.main(verbosity=2)
