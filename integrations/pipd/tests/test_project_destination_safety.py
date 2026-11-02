"""R5-WO1 (REQ-PIPD-R5-DEST-001): `project --out` destination safety.

The product CLI previously did `shutil.rmtree(out)` on a caller-supplied `--out`
with no validation, so `pipd project --out <anything>` could recursively delete
the repo root, the cwd, $HOME, a source ancestor or a foreign directory.

These tests drive the CLI as a subprocess (like ``test_cli_typed_errors``) over
disposable scratch trees - never against the real checkout - and assert that
each dangerous destination is a *typed* refusal (exit != 0, ``UNSAFE_DESTINATION``)
that leaves a whole-tree canary hash byte-identical. The positive control proves
the safe path still publishes the 5 Web documents + 3 host projections + IR, and
that replacement keeps a ``.pipd-backup-<token>`` rollback pointer.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

# Deliberately scrub PIPD_PROJECT_ALLOWED_ROOTS: the tests must not inherit an
# ambient authorization, so the "foreign dir" cases really are foreign.
ENV = {k: v for k, v in os.environ.items()
       if k not in ("PIPD_PROJECT_ALLOWED_ROOTS",)}
ENV.update({"PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"})

DOCS = {"PIPD_BOOTSTRAP.md", "PIPD_CANONICAL_CORE.md", "PIPD_ROUTER_PROFILES.md",
        "PIPD_ARTIFACT_SCHEMAS.md", "PIPD_EVAL_HANDOFF.md"}
HOST_DIRS = {"host_generic-skills", "host_hgk-receiver", "host_genie-adapter"}


def build_repo(dst: Path) -> Path:
    """A minimal but valid canonical source root the projector can read."""
    (dst / "src" / "pipd_ls_sp").mkdir(parents=True)
    (dst / "fixtures" / "s5_s8").mkdir(parents=True)
    shutil.copytree(ROOT / "schemas", dst / "schemas")
    shutil.copy(ROOT / "src" / "pipd_ls_sp" / "profiles.py",
                dst / "src" / "pipd_ls_sp" / "profiles.py")
    for f in (ROOT / "fixtures" / "s5_s8").iterdir():
        shutil.copy(f, dst / "fixtures" / "s5_s8" / f.name)
    return dst


def tree_hash(root: Path) -> str:
    rows = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            rows.append((str(p.relative_to(root)),
                         hashlib.sha256(p.read_bytes()).hexdigest()))
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest()


def cli(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", *args],
                          capture_output=True, text=True, env=ENV, cwd=str(cwd))


class DestinationSafetyTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.scratch = Path(self._td.name)
        self.repo = build_repo(self.scratch / "repo")

    def tearDown(self):
        self._td.cleanup()

    # ------------------------------------------------------------- helpers

    def _assert_refused(self, args: list[str], *, cwd: Path, label: str) -> None:
        before = tree_hash(self.repo)
        r = cli(args, cwd=cwd)
        self.assertNotEqual(r.returncode, 0,
                            f"{label}: expected a non-zero exit, got 0\n{r.stdout}")
        try:
            payload = json.loads(r.stdout)
        except json.JSONDecodeError:
            self.fail(f"{label}: stdout was not a JSON envelope: {r.stdout[:200]!r}")
        self.assertEqual(payload.get("verdict"), "FAIL", f"{label}: {payload}")
        self.assertEqual(payload.get("code"), "UNSAFE_DESTINATION", f"{label}: {payload}")
        self.assertEqual(tree_hash(self.repo), before,
                         f"{label}: the source tree changed despite the refusal")

    # ------------------------------------------------------------ negatives

    def test_out_dot_is_refused(self):
        self._assert_refused(["project", "--root", str(self.repo), "--out", "."],
                             cwd=self.repo, label="--out .")

    def test_out_dotdot_is_refused(self):
        work = self.scratch / "work"
        work.mkdir()
        self._assert_refused(["project", "--root", str(self.repo), "--out", ".."],
                             cwd=self.scratch / "work", label="--out ..")

    def test_repo_root_is_refused(self):
        self._assert_refused(["project", "--root", str(self.repo), "--out", str(self.repo)],
                             cwd=self.scratch, label="repo root")

    def test_scratch_cwd_is_refused(self):
        work = self.scratch / "work"
        work.mkdir()
        self._assert_refused(["project", "--root", str(self.repo), "--out", str(work)],
                             cwd=work, label="cwd")

    def test_home_is_refused(self):
        self._assert_refused(["project", "--root", str(self.repo), "--out", str(Path.home())],
                             cwd=self.scratch, label="$HOME")

    def test_filesystem_root_is_refused(self):
        self._assert_refused(["project", "--root", str(self.repo), "--out", "/"],
                             cwd=self.scratch, label="filesystem root")

    def test_source_ancestor_is_refused(self):
        self._assert_refused(["project", "--root", str(self.repo), "--out", str(self.scratch)],
                             cwd=self.scratch, label="source ancestor")

    def test_source_descendant_containing_cwd_is_refused(self):
        sub = self.repo / "subdir" / "deep"
        sub.mkdir(parents=True)
        self._assert_refused(
            ["project", "--root", str(self.repo), "--out", str(self.repo / "subdir")],
            cwd=sub, label="source descendant containing the cwd")

    def test_existing_non_empty_authorized_dir_without_allow_replace_is_refused(self):
        foreign = self.scratch / "foreign"
        foreign.mkdir()
        (foreign / "keep.txt").write_text("do not lose me\n", encoding="utf-8")
        self._assert_refused(
            ["project", "--root", str(self.repo), "--out", str(foreign),
             "--allow-root", str(self.scratch)],
            cwd=self.scratch, label="non-empty dir without --allow-replace")
        self.assertEqual((foreign / "keep.txt").read_text(encoding="utf-8"),
                         "do not lose me\n")

    def test_foreign_dir_outside_authorized_roots_is_refused(self):
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        self._assert_refused(
            ["project", "--root", str(self.repo), "--out", str(Path(other.name) / "x"),
             "--allow-root", str(self.scratch)],
            cwd=self.scratch, label="foreign absolute dir")

    def test_symlink_escaping_authorized_root_is_refused(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        link = self.scratch / "link"
        try:
            os.symlink(outside.name, link)
        except (OSError, NotImplementedError):
            self.skipTest("this host cannot create symlinks")
        self._assert_refused(
            ["project", "--root", str(self.repo), "--out", str(link),
             "--allow-root", str(self.scratch)],
            cwd=self.scratch, label="symlink escaping the authorized root")

    def test_msys_posix_form_is_refused(self):
        self._assert_refused(
            ["project", "--root", str(self.repo), "--out", "/c/Users/someone/dist"],
            cwd=self.scratch, label="MSYS /c/... form")

    def test_empty_out_is_refused(self):
        self._assert_refused(["project", "--root", str(self.repo), "--out", ""],
                             cwd=self.scratch, label="empty --out")

    def test_whitespace_out_is_refused(self):
        self._assert_refused(["project", "--root", str(self.repo), "--out", "   "],
                             cwd=self.scratch, label="whitespace --out")

    def test_dry_run_on_dangerous_destination_refuses_and_writes_nothing(self):
        before = tree_hash(self.scratch)
        r = cli(["project", "--root", str(self.repo), "--dry-run", "--out", "."],
                cwd=self.repo)
        self.assertNotEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertEqual(payload.get("verdict"), "FAIL")
        self.assertEqual(payload.get("code"), "UNSAFE_DESTINATION")
        self.assertEqual(tree_hash(self.scratch), before,
                         "a dangerous dry-run must create nothing")

    # ------------------------------------------------------------ positive

    def test_positive_control_publish_refuse_then_replace(self):
        out = self.scratch / "out"
        args = ["project", "--root", str(self.repo), "--out", str(out),
                "--allow-root", str(self.scratch)]
        source_before = tree_hash(self.repo)

        first = cli(args, cwd=self.scratch)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        payload = json.loads(first.stdout)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["web_count"], "5/5")
        self.assertEqual(payload["web_check"], "PASS")
        self.assertEqual(payload["host_check"], "PASS")
        self.assertEqual(payload["destination"]["replaced"], False)
        self.assertIsNone(payload["destination"]["rollback_pointer"])

        present = {p.name for p in out.iterdir()}
        self.assertTrue(DOCS.issubset(present), present)
        self.assertTrue(HOST_DIRS.issubset(present), present)
        self.assertIn("PROJECTION_IR.json", present)
        self.assertTrue(all((out / d).is_dir() for d in HOST_DIRS))
        self.assertTrue((out / ".pipd-generated-surface.json").is_file())
        self.assertEqual(tree_hash(self.repo), source_before,
                         "the source tree must be untouched by a publish")

        # The marker is not counted as one of the 5 Web documents.
        self.assertEqual({p.name for p in out.glob("PIPD_*.md")}, DOCS)

        # Second run, same arguments: a non-empty target is refused.
        before_bytes = (out / "PIPD_BOOTSTRAP.md").read_bytes()
        second = cli(args, cwd=self.scratch)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(json.loads(second.stdout)["code"], "UNSAFE_DESTINATION")

        # --allow-replace publishes again and keeps the previous tree as a backup.
        third = cli(args + ["--allow-replace"], cwd=self.scratch)
        self.assertEqual(third.returncode, 0, third.stdout + third.stderr)
        payload3 = json.loads(third.stdout)
        self.assertTrue(payload3["destination"]["replaced"])
        rollback = payload3["destination"]["rollback_pointer"]
        self.assertIsNotNone(rollback)
        backup = Path(rollback)
        self.assertTrue(backup.is_dir(), f"rollback pointer {rollback} is not a dir")
        self.assertIn(".pipd-backup-", backup.name)
        self.assertEqual((backup / "PIPD_BOOTSTRAP.md").read_bytes(), before_bytes,
                         "the backup must contain the previous bytes")
        self.assertEqual({p.name for p in out.glob("PIPD_*.md")}, DOCS)

    def test_resolver_unit_blank_and_none(self):
        from pipd_ls_sp import projection as P
        from pipd_ls_sp.errors import PipdError
        for bad in (None, "", "   "):
            with self.assertRaises(P.UnsafeDestination):
                P.resolve_output_destination(self.repo, bad)
        # UnsafeDestination is a typed PipdError so the CLI renders it.
        self.assertTrue(issubclass(P.UnsafeDestination, PipdError))
        self.assertEqual(P.UnsafeDestination.code, "UNSAFE_DESTINATION")


if __name__ == "__main__":
    unittest.main(verbosity=2)
