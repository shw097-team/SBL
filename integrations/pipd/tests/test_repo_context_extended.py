"""W2 CH-15: the live RepoContext must carry real, machine-readable repository evidence.

Eight things are asserted against a REAL temporary git checkout (never a mock):
git_root, index (digest + staged), untracked (list + count), acl, per_file_preimage,
capabilities, backward-compatible legacy fields, and a fail-soft negative case.

stdlib `unittest` only: no pytest import anywhere.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Self-bootstrap, same rule as every other test file here: runnable standalone.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import repo_context  # noqa: E402

GIT = shutil.which("git") or ""
REQUIRED_KEYS = ("git_root", "git_root_resolved", "root", "root_input",
                 "index_digest", "staged_changes",
                 "untracked", "untracked_count",
                 "acl", "acl_state",
                 "per_file_preimage", "capabilities")


def _git(repo, *args):
    return subprocess.run([GIT, "-C", str(repo), *args],
                          capture_output=True, text=True, timeout=60)


def _same_path(a, b):
    return os.path.normcase(os.path.abspath(str(a))) == os.path.normcase(os.path.abspath(str(b)))


@unittest.skipUnless(GIT, "git is required for live RepoContext probes")
class RepoContextExtendedTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.repo = self.tmp / "repo"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "src" / "mod.py").write_text("x = 1\n", encoding="utf-8")
        (self.repo / "README.md").write_text("# live\n", encoding="utf-8")
        _git(self.repo, "init", "-q")
        _git(self.repo, "add", ".")
        _git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t",
             "commit", "-q", "-m", "base")
        # one STAGED modification + one untracked file
        (self.repo / "src" / "mod.py").write_text("x = 2\n", encoding="utf-8")
        _git(self.repo, "add", "src/mod.py")
        (self.repo / "NOTES.txt").write_text("untracked\n", encoding="utf-8")
        self.preimage_root = self.tmp / "preimage-root"

    def tearDown(self):
        self._td.cleanup()

    # ---------------------------------------------------------------- 1 git_root
    def test_git_root_resolves_real_toplevel(self):
        ctx = repo_context.derive_repo_context(self.repo)
        self.assertTrue(ctx["git_root_resolved"], ctx.get("errors"))
        self.assertTrue(_same_path(ctx["git_root"], self.repo),
                        f"git_root={ctx['git_root']!r} repo={self.repo!r}")
        # caller path is preserved under both the legacy `root` and the new `root_input`
        self.assertTrue(_same_path(ctx["root"], self.repo))
        self.assertEqual(ctx["root_input"], str(self.repo))
        self.assertEqual(ctx["capabilities"]["git_root"], "PRESENT")

    def test_git_root_resolves_from_subdirectory(self):
        sub = self.repo / "src"
        ctx = repo_context.derive_repo_context(sub)
        self.assertTrue(ctx["git_root_resolved"])
        self.assertTrue(_same_path(ctx["git_root"], self.repo),
                        "git_root must be the toplevel, not the caller path")

    # ---------------------------------------------------------------- 2 index
    def test_index_digest_and_staged_changes(self):
        expected = hashlib.sha256(_git(self.repo, "ls-files", "-s").stdout.encode("utf-8")).hexdigest()
        ctx = repo_context.derive_repo_context(self.repo)
        self.assertEqual(ctx["index_digest"], expected)
        self.assertEqual(len(ctx["index_digest"]), 64)
        self.assertEqual(ctx["staged_changes"], ["src/mod.py"])
        self.assertEqual(ctx["staged_count"], 1)
        self.assertEqual(ctx["capabilities"]["index"], "PRESENT")

    # ---------------------------------------------------------------- 3 untracked
    def test_untracked_list_and_count_without_polluting_dirty(self):
        ctx = repo_context.derive_repo_context(self.repo)
        self.assertEqual(ctx["untracked"], ["NOTES.txt"])
        self.assertEqual(ctx["untracked_count"], 1)
        self.assertEqual(ctx["capabilities"]["untracked"], "PRESENT")
        # legacy semantics: dirty / dirty_tracked stay TRACKED-ONLY
        self.assertTrue(ctx["dirty"])
        self.assertTrue(all("??" not in entry for entry in ctx["dirty_tracked"]))
        self.assertNotIn("NOTES.txt", ctx["dirty_tracked"])

    # ---------------------------------------------------------------- 4 acl
    def test_acl_is_observed_or_honestly_unverified(self):
        ctx = repo_context.derive_repo_context(self.repo)  # writable_scope defaults to src/**
        acl = ctx["acl"]
        for key in ("state", "principals", "raw_sha256"):
            self.assertIn(key, acl)
        self.assertIn(acl["state"], ("OBSERVED", "UNVERIFIED"))
        self.assertEqual(ctx["acl_state"], acl["state"])
        self.assertEqual(ctx["capabilities"]["acl"], acl["state"])
        self.assertEqual(acl["files"], ["src/mod.py"])
        if os.name == "nt" and shutil.which("icacls"):
            self.assertEqual(acl["state"], "OBSERVED", acl.get("reason"))
            self.assertTrue(acl["principals"], "OBSERVED ACL must name at least one principal")
            self.assertEqual(len(acl["raw_sha256"]), 64)
        else:
            self.assertEqual(acl["state"], "UNVERIFIED")
            self.assertTrue(acl["reason"], "UNVERIFIED ACL must disclose why")
            self.assertIsNone(acl["raw_sha256"])
        # an UNVERIFIED block is never reported as VERIFIED/OK
        self.assertNotIn(str(acl["state"]), ("VERIFIED", "OK"))

    def test_acl_outside_any_scope_is_unverified(self):
        ctx = repo_context.derive_repo_context(self.repo, writable_scope="fixtures/**")
        self.assertEqual(ctx["acl"]["state"], "UNVERIFIED")
        self.assertEqual(ctx["acl"]["principals"], [])
        self.assertTrue(ctx["acl"]["reason"])
        self.assertEqual(ctx["capabilities"]["acl"], "UNVERIFIED")

    # ---------------------------------------------------------------- 5 per_file_preimage
    def test_per_file_manifest_present_without_capture(self):
        ctx = repo_context.derive_repo_context(self.repo)
        pre = ctx["per_file_preimage"]
        self.assertFalse(pre["captured"], "capture_preimage defaults to False (compat)")
        self.assertEqual(pre["preimage_refs"], [])
        self.assertEqual(pre["manifest_sha256"], ctx["manifest_sha256"])
        rels = sorted(row["rel"] for row in pre["manifest"])
        self.assertEqual(rels, ["README.md", "src/mod.py"])
        for row in pre["manifest"]:
            self.assertEqual(set(row), {"rel", "size", "sha256"})
            self.assertEqual(len(row["sha256"]), 64)
        self.assertEqual(ctx["capabilities"]["preimage_bytes"], "OPTIONAL_CAPTURE")
        self.assertEqual(ctx["capabilities"]["preimage_capture"], "NOT_REQUESTED")

    def test_preimage_bytes_captured_outside_scope(self):
        ctx = repo_context.derive_repo_context(
            self.repo, capture_preimage=True, preimage_dir=self.preimage_root)
        pre = ctx["per_file_preimage"]
        self.assertTrue(pre["captured"], ctx["errors"])
        self.assertEqual(ctx["capabilities"]["preimage_capture"], "CAPTURED")
        self.assertEqual(len(pre["preimage_refs"]), len(pre["manifest"]))
        for ref in pre["preimage_refs"]:
            self.assertEqual(set(ref), {"rel", "path", "sha256", "bytes"})
            stored = Path(ref["path"])
            self.assertTrue(stored.is_file())
            data = stored.read_bytes()
            self.assertEqual(ref["bytes"], len(data))
            self.assertEqual(ref["sha256"], hashlib.sha256(data).hexdigest())
            self.assertTrue(str(stored).startswith(str(self.preimage_root)),
                            "pre-image bytes must land under the caller-supplied temp root")
            self.assertFalse(str(stored).startswith(str(self.repo)),
                             "pre-image must not be written inside the repository")

    def test_preimage_scope_deny_is_recorded_not_raised(self):
        try:
            ctx = repo_context.derive_repo_context(
                self.repo, capture_preimage=True,
                preimage_dir=self.repo / "src" / "preimage")
        except Exception as exc:  # noqa: BLE001 - a raise here is the defect
            self.fail(f"PREIMAGE_SCOPE_DENY must be recorded, not raised: {exc!r}")
        pre = ctx["per_file_preimage"]
        self.assertFalse(pre["captured"])
        self.assertEqual(pre["preimage_refs"], [])
        self.assertTrue(any("PREIMAGE_SCOPE_DENY" in e for e in ctx["errors"]), ctx["errors"])
        self.assertEqual(ctx["capabilities"]["preimage_capture"], "SCOPE_DENY")
        self.assertFalse((self.repo / "src" / "preimage").exists(),
                         "a denied pre-image root must not be created")

    def test_preimage_without_dir_is_refused(self):
        ctx = repo_context.derive_repo_context(self.repo, capture_preimage=True)
        self.assertFalse(ctx["per_file_preimage"]["captured"])
        self.assertTrue(any("PREIMAGE_SCOPE_DENY" in e for e in ctx["errors"]))

    # ---------------------------------------------------------------- 6 capabilities
    def test_capabilities_enumerate_every_probe(self):
        ctx = repo_context.derive_repo_context(self.repo)
        caps = ctx["capabilities"]
        self.assertEqual(caps["git_root"], "PRESENT")
        self.assertEqual(caps["index"], "PRESENT")
        self.assertEqual(caps["untracked"], "PRESENT")
        self.assertEqual(caps["acl"], ctx["acl"]["state"])
        self.assertEqual(caps["preimage_bytes"], "OPTIONAL_CAPTURE")
        self.assertEqual(caps["preimage_capture"], "NOT_REQUESTED")
        for key, value in caps.items():
            self.assertIsInstance(key, str)
            self.assertIn(value, ("PRESENT", "ABSENT", "OBSERVED", "UNVERIFIED",
                                  "OPTIONAL_CAPTURE", "NOT_REQUESTED", "CAPTURED",
                                  "SCOPE_DENY", "FAILED"), key)

    # ---------------------------------------------------------------- 7 legacy fields
    def test_legacy_contract_is_unchanged(self):
        ctx = repo_context.derive_repo_context(self.repo)
        for key in REQUIRED_KEYS:
            self.assertIn(key, ctx)
        self.assertEqual(ctx["probe"], "git")
        self.assertFalse(ctx["degraded"])
        self.assertIsNone(ctx["degraded_reason"])
        self.assertEqual(ctx["tracked_files"], 2)
        self.assertEqual(len(ctx["manifest_sha256"]), 64)
        self.assertEqual(ctx["readiness"], "PREDEV_READY")
        self.assertEqual(ctx["currentness"], "FRESH")
        self.assertEqual(len(ctx["currentness_epoch"]), 64)
        self.assertTrue(ctx["writable_scope_check"]["subset"])
        self.assertEqual(len(ctx["head"]), 40)

    # ---------------------------------------------------------------- 8 negative case
    def test_non_git_root_is_unresolved_and_soft(self):
        plain = self.tmp / "plain"
        (plain / "src").mkdir(parents=True)
        (plain / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        try:
            ctx = repo_context.derive_repo_context(plain)
        except Exception as exc:  # noqa: BLE001 - the defect is a raise
            self.fail(f"non-git root must not raise: {exc!r}")
        self.assertFalse(ctx["git_root_resolved"])
        self.assertIsNone(ctx["git_root"])
        self.assertEqual(ctx["capabilities"]["git_root"], "ABSENT")
        self.assertEqual(ctx["capabilities"]["index"], "ABSENT")
        self.assertEqual(ctx["capabilities"]["untracked"], "ABSENT")
        self.assertTrue(ctx["errors"], "a failed git_root resolution must be disclosed")
        self.assertTrue(any("git_root" in e for e in ctx["errors"]), ctx["errors"])
        self.assertEqual(ctx["probe"], "filesystem")
        self.assertTrue(ctx["degraded"])
        self.assertEqual(ctx["untracked_count"], 0)
        self.assertEqual(ctx["staged_changes"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
