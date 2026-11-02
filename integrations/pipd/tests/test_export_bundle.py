"""R5-WO3 (REQ-PIPD-R5-EXPORT-003): `pipd export --out` delivers a portable bundle.

`pipd export` previously ignored `--out`: it declared a target in `--dry-run` and
then wrote nothing at all.  These tests drive the CLI as a subprocess (like
``test_project_destination_safety`` / ``test_cli_typed_errors``) over disposable
scratch trees, each in its own tree, and assert that `export --out` really writes a
deterministic archive + manifest + checksums that independently verify; that a
secret or an unsafe member path writes nothing anywhere; that a dangerous
destination is the same typed ``UNSAFE_DESTINATION`` envelope as `project --out`;
that dry-run writes nothing; and that a pre-existing target is kept as a backup.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

# Scrubbed so the tests never inherit an ambient authorization.
ENV = {k: v for k, v in os.environ.items() if k not in ("PIPD_PROJECT_ALLOWED_ROOTS",)}
ENV.update({"PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"})


def build_repo(dst: Path) -> Path:
    """A small, clean source root the export walks (schemas/src/tests/docs/pyproject)."""
    (dst / "src").mkdir(parents=True)
    (dst / "docs").mkdir(parents=True)
    (dst / "schemas").mkdir(parents=True)
    (dst / "src" / "a.py").write_text("x = 1\n", encoding="utf-8", newline="")
    (dst / "src" / "b.py").write_text("y = 2\n", encoding="utf-8", newline="")
    (dst / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8", newline="")
    (dst / "schemas" / "registry.json").write_text("{}\n", encoding="utf-8", newline="")
    (dst / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8", newline="")
    return dst


def tree_hash(root: Path) -> str:
    rows = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            rows.append((str(p.relative_to(root)),
                         hashlib.sha256(p.read_bytes()).hexdigest()))
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest()


class ExportBundleTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.scratch = Path(self._td.name)
        self.repo = build_repo(self.scratch / "repo")
        self.work = self.scratch / "work"
        self.work.mkdir()

    def tearDown(self):
        self._td.cleanup()

    def cli(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli",
                               "--root", str(self.repo), *args],
                              capture_output=True, text=True, env=ENV, cwd=str(self.work))

    def _export_ok(self, out: Path) -> dict:
        r = self.cli(["export", "--out", str(out), "--allow-root", str(self.scratch)])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["verdict"], "PASS")
        return payload

    def _unpack(self, archive: Path) -> dict:
        members = {}
        with tarfile.open(archive, mode="r:gz") as tar:
            for m in tar.getmembers():
                if m.isfile():
                    members[m.name] = tar.extractfile(m).read()
        return members

    # ------------------------------------------------------------ positive

    def test_export_writes_verifiable_bundle(self):
        out = self.scratch / "out"
        payload = self._export_ok(out)

        archive = out / "out.tar.gz"
        manifest_p = out / "export_manifest.json"
        sums_p = out / "SHA256SUMS"
        self.assertTrue(archive.is_file(), "archive missing")
        self.assertTrue(manifest_p.is_file(), "manifest missing")
        self.assertTrue(sums_p.is_file(), "SHA256SUMS missing")

        manifest = json.loads(manifest_p.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "PIPD-EXPORT-BUNDLE/1")
        for key in ("generated_at", "source_root", "file_count", "archive", "files"):
            self.assertIn(key, manifest)
        self.assertEqual(manifest["file_count"], len(manifest["files"]))
        self.assertEqual(manifest["archive"]["name"], "out.tar.gz")
        self.assertEqual(manifest["archive"]["sha256"],
                         hashlib.sha256(archive.read_bytes()).hexdigest())
        self.assertEqual(manifest["archive"]["size"], archive.stat().st_size)
        self.assertEqual(payload["file_count"], manifest["file_count"])

        rels = [f["rel"] for f in manifest["files"]]
        self.assertEqual(rels, sorted(rels))

        unpacked = self._unpack(archive)
        self.assertEqual(sorted(unpacked), sorted(rels),
                         "archive members must equal the manifest rel set")
        for row in manifest["files"]:
            data = unpacked[row["rel"]]
            self.assertEqual(len(data), row["size"], row["rel"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"], row["rel"])

        lines = [ln for ln in sums_p.read_text(encoding="utf-8").splitlines() if ln.strip()]
        parsed = {}
        for ln in lines:
            sha, rel = ln.split("  ", 1)
            parsed[rel] = sha
        self.assertEqual(set(parsed), set(rels) | {"out.tar.gz"})
        self.assertEqual(parsed["out.tar.gz"], manifest["archive"]["sha256"])
        for row in manifest["files"]:
            self.assertEqual(parsed[row["rel"]], row["sha256"], row["rel"])

    def test_byte_replay_is_deterministic(self):
        p1 = self._export_ok(self.scratch / "o1")
        p2 = self._export_ok(self.scratch / "o2")
        self.assertEqual(p1["manifest_sha256"], p2["manifest_sha256"],
                         "two exports of one frozen source must share a manifest digest")
        self.assertEqual(p1["archive"]["sha256"], p2["archive"]["sha256"],
                         "the deterministic archive must be byte-identical across runs")
        m1 = json.loads((self.scratch / "o1" / "export_manifest.json").read_text("utf-8"))
        m2 = json.loads((self.scratch / "o2" / "export_manifest.json").read_text("utf-8"))
        self.assertEqual(m1["files"], m2["files"])

    # --------------------------------------------------------------- dry run

    def test_dry_run_writes_nothing(self):
        before = tree_hash(self.scratch)
        out = self.scratch / "dry"
        r = self.cli(["export", "--out", str(out), "--allow-root", str(self.scratch),
                      "--dry-run"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        payload = json.loads(r.stdout)
        self.assertTrue(payload["wrote_nothing"])
        self.assertIn("manifest_sha256", payload)
        self.assertGreater(payload["file_count"], 0)
        self.assertFalse(out.exists(), "dry-run must not create the destination")
        self.assertEqual(tree_hash(self.scratch), before, "dry-run changed the tree")

    # --------------------------------------------------------------- secrets

    def test_secret_in_export_set_writes_nothing(self):
        (self.repo / "src" / "leak.py").write_text(
            'TOKEN = "ghp_' + "A" * 30 + '"\n', encoding="utf-8", newline="")
        out = self.scratch / "out"
        r = self.cli(["export", "--out", str(out), "--allow-root", str(self.scratch)])
        self.assertNotEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["verdict"], "FAIL")
        self.assertEqual(payload["code"], "EXPORT_SECRET_SCAN")
        self.assertFalse(out.exists() and any(out.iterdir()),
                         "a secret-bearing export must write zero files")

    # --------------------------------------------------- unsafe destinations

    def _assert_refused(self, args: list[str], *, label: str) -> None:
        before = tree_hash(self.scratch)
        r = self.cli(args)
        self.assertNotEqual(r.returncode, 0, f"{label}: expected non-zero\n{r.stdout}")
        payload = json.loads(r.stdout)
        self.assertEqual(payload.get("verdict"), "FAIL", f"{label}: {payload}")
        self.assertEqual(payload.get("code"), "UNSAFE_DESTINATION", f"{label}: {payload}")
        self.assertEqual(tree_hash(self.scratch), before, f"{label}: tree changed")

    def test_unsafe_destinations_refused(self):
        cases = {
            "out dot": ["export", "--out", ".", "--allow-root", str(self.scratch)],
            "repo root": ["export", "--out", str(self.repo), "--allow-root", str(self.scratch)],
            "cwd": ["export", "--out", str(self.work), "--allow-root", str(self.scratch)],
            "msys": ["export", "--out", "/c/anything", "--allow-root", str(self.scratch)],
            "empty": ["export", "--out", "", "--allow-root", str(self.scratch)],
        }
        for label, args in cases.items():
            with self.subTest(label=label):
                self._assert_refused(args, label=label)

    # ------------------------------------------------- replacement + backup

    def test_existing_target_refuse_then_replace_keeps_backup(self):
        out = self.scratch / "out"
        out.mkdir()
        (out / "keep.txt").write_text("do not lose me\n", encoding="utf-8", newline="")
        keep_bytes = (out / "keep.txt").read_bytes()

        refused = self.cli(["export", "--out", str(out), "--allow-root", str(self.scratch)])
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(json.loads(refused.stdout)["code"], "UNSAFE_DESTINATION")
        self.assertEqual((out / "keep.txt").read_bytes(), keep_bytes,
                         "a refused export must not touch the target")

        r = self.cli(["export", "--out", str(out), "--allow-root", str(self.scratch),
                      "--allow-replace"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        payload = json.loads(r.stdout)
        self.assertTrue(payload["destination"]["replaced"])
        rollback = payload["destination"]["rollback_pointer"]
        self.assertIsNotNone(rollback)
        backup = Path(rollback)
        self.assertTrue(backup.is_dir(), f"rollback pointer {rollback} is not a dir")
        self.assertIn(".pipd-backup-", backup.name)
        self.assertEqual((backup / "keep.txt").read_bytes(), keep_bytes,
                         "the previous bytes must be retrievable from the backup path")
        self.assertTrue((out / "out.tar.gz").is_file())
        self.assertTrue((out / "export_manifest.json").is_file())
        self.assertTrue((out / "SHA256SUMS").is_file())


    # ------------------------------------------------- member-path traversal

    def test_traversing_member_path_is_refused_typed(self):
        """Any absolute / `..` / escaping member rel is a typed refusal (req 3)."""
        from pipd_ls_sp import export_bundle
        from pipd_ls_sp.errors import ExportMemberUnsafe, PipdError
        (self.scratch / "evil.py").write_text("e = 1\n", encoding="utf-8", newline="")
        (self.repo / "inside.py").write_text("i = 1\n", encoding="utf-8", newline="")
        self.assertTrue(issubclass(ExportMemberUnsafe, PipdError))
        for bad_include in ("../evil.py", str(self.scratch / "evil.py"), "src/../../evil.py"):
            with self.subTest(include=bad_include):
                with self.assertRaises(ExportMemberUnsafe):
                    export_bundle.collect_source_files(self.repo, include=[bad_include])


if __name__ == "__main__":
    unittest.main(verbosity=2)
