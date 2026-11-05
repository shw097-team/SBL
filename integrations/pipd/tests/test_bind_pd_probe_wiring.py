"""W2 CH-15 wiring: `bind_pd` must CONSUME the extended RepoContext probe, not drop it.

The probe (`repo_context.derive_repo_context`) already computes git_root / index_digest /
staged_changes / untracked / acl / capabilities. Before this wiring those keys were discarded when
`bind_pd` rebuilt its own narrower `ctx`, so PD and ECP consumers could not see what upstream had
actually observed. Three things are pinned here against a REAL temporary git checkout (never a
mock):

a. positive - the PD carries all eight new keys plus a machine-readable `evidence_completeness`
   block, and the legacy keys are still present and unchanged;
b. negative - a root that is NOT a git toplevel is REFUSED with `RepoContextMissing` (fail closed,
   never a silent degraded PD);
c. negative - a missing RepoContext is still refused (no regression of the prior contract).

stdlib `unittest` only: no pytest import anywhere.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Self-bootstrap, same rule as every other test file here: runnable standalone.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline  # noqa: E402
from pipd_ls_sp.errors import RepoContextMissing  # noqa: E402

GIT = shutil.which("git") or ""
GOAL = "實作受治理的編譯系統。"
CLAUSE = "系統 MUST 保留原始需求識別。\n"

# The eight probe fields that used to be dropped on the floor between probe and PD.
NEW_KEYS = ("git_root", "git_root_resolved", "index_digest", "staged_changes",
            "untracked", "untracked_count", "acl", "capabilities")
# The legacy keys: additive-only change, nothing renamed and nothing removed.
LEGACY_KEYS = ("root", "probe", "degraded", "degraded_reason", "head", "branch", "dirty",
               "dirty_tracked", "tracked_files", "manifest_sha256", "currentness_epoch",
               "readiness", "caller_claims")


def _git(repo, *args):
    return subprocess.run([GIT, "-C", str(repo), *args],
                          capture_output=True, text=True, timeout=60)


@unittest.skipUnless(GIT, "git is required for live RepoContext probes")
class BindPdProbeWiringTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.repo = self.tmp / "repo"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "src" / "mod.py").write_text("x = 1\n", encoding="utf-8")
        _git(self.repo, "init", "-q")
        _git(self.repo, "add", ".")
        _git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t",
             "commit", "-q", "-m", "base")
        # one STAGED modification and one untracked file: real evidence, not empty lists by luck
        (self.repo / "src" / "mod.py").write_text("x = 2\n", encoding="utf-8")
        _git(self.repo, "add", "src/mod.py")
        (self.repo / "NOTES.txt").write_text("untracked\n", encoding="utf-8")
        self.source = self.tmp / "source.txt"   # outside the repo: the probe set stays exact
        self.source.write_text(CLAUSE, encoding="utf-8")
        # Real PI through the shipped compilers; bind_pd only needs it to be a valid PI record.
        self.pi = pipeline.compile_pi(
            pipeline.intake(GOAL, sources=[str(self.source)]), "LITE")

    def tearDown(self):
        self._td.cleanup()

    # ---------------------------------------------------------------- a. positive
    def test_pd_carries_the_extended_probe_fields(self):
        pd = pipeline.bind_pd(self.pi, {"root": str(self.repo), "writable_scope": "src/**"})
        ctx = pd["RepoContext"]
        for key in NEW_KEYS:
            self.assertIn(key, ctx, f"bind_pd dropped probe field {key!r}")
        for key in LEGACY_KEYS:
            self.assertIn(key, ctx, f"legacy RepoContext key {key!r} must not disappear")

        # values are the PROBE's values, not re-invented ones
        self.assertTrue(ctx["git_root_resolved"], ctx.get("capabilities"))
        self.assertTrue(str(ctx["git_root"]).replace("\\", "/").lower()
                        .endswith("repo"), ctx["git_root"])
        self.assertRegex(ctx["index_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(ctx["staged_changes"], ["src/mod.py"])
        self.assertEqual(ctx["untracked"], ["NOTES.txt"])
        self.assertEqual(ctx["untracked_count"], 1)
        self.assertEqual(ctx["acl"]["state"], ctx["capabilities"]["acl"])
        self.assertIn("preimage_capture", ctx["capabilities"])

        # machine-readable completeness: no consumer has to guess what was probed
        ev = pd["evidence_completeness"]
        self.assertEqual(set(ev), {"probe_version", "git_root_resolved", "index_digest_present",
                                   "untracked_observed", "acl_state", "capability_keys"})
        self.assertIs(ev["git_root_resolved"], True)
        self.assertIs(ev["index_digest_present"], True)
        self.assertIs(ev["untracked_observed"], True)
        self.assertIn(ev["acl_state"], ("OBSERVED", "UNVERIFIED"))
        self.assertEqual(ev["capability_keys"], sorted(ctx["capabilities"]))
        self.assertIsInstance(ev["probe_version"], str)
        self.assertTrue(ev["probe_version"])

        # currentness names the repository identity and the ACL ceiling
        self.assertIs(pd["currentness"]["repo_identity_verified"], True)
        self.assertEqual(pd["currentness"]["acl_state"], ev["acl_state"])

        # the record is still a sealed PD record
        self.assertEqual(pd["subject_id"][:3], "PD-")
        self.assertRegex(pd["content_hash"], r"^[0-9a-f]{64}$")

    def test_bind_pd_is_replay_stable_on_the_same_root(self):
        a = pipeline.bind_pd(self.pi, {"root": str(self.repo), "writable_scope": "src/**"})
        b = pipeline.bind_pd(self.pi, {"root": str(self.repo), "writable_scope": "src/**"})
        self.assertEqual(a["content_hash"], b["content_hash"])
        self.assertEqual(a["evidence_completeness"], b["evidence_completeness"])

    # ---------------------------------------------------------------- b. non-git root
    def test_non_git_root_is_refused_not_degraded(self):
        plain = self.tmp / "plain"
        (plain / "src").mkdir(parents=True)
        (plain / "src" / "mod.py").write_text("x = 1\n", encoding="utf-8")
        with self.assertRaises(RepoContextMissing) as caught:
            pipeline.bind_pd(self.pi, {"root": str(plain), "writable_scope": "src/**"})
        message = str(caught.exception)
        self.assertIn("not a resolved git toplevel", message)
        self.assertIn(str(plain), message)
        self.assertEqual(caught.exception.code, "REPO_CONTEXT_MISSING")

    # ---------------------------------------------------------------- c. no context
    def test_missing_repo_context_is_still_refused(self):
        with self.assertRaises(RepoContextMissing):
            pipeline.bind_pd(self.pi, None)
        with self.assertRaises(RepoContextMissing):
            pipeline.bind_pd(self.pi, {})
        with self.assertRaises(RepoContextMissing):
            pipeline.bind_pd(self.pi, {"root": "   "})
        with self.assertRaises(RepoContextMissing):
            pipeline.bind_pd(self.pi, {"root": str(self.tmp / "does_not_exist_xyz")})


if __name__ == "__main__":
    unittest.main(verbosity=2)
