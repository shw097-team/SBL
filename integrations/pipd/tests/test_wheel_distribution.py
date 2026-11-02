"""R5-DIST-002: the installed wheel carries a current, self-sufficient package.

Proves, against the real hand-built artefact:
  * the wheel contains every ``src/pipd_ls_sp/**/*.py`` module plus the whole ``schemas/`` tree
    (``registry.json`` + 19 ``*.schema.json``) mapped INTO the package;
  * every sha the manifest records equals the sha of the bytes actually inside the zip;
  * the packaged schema copy is complete and self-consistent (``load_registry`` -> 19 families);
  * two builds of the same tree are byte-identical (determinism).
A real-venv self-sufficiency probe is SKIPPED with an explicit reason when ``venv``/``pip`` are
unavailable in the test interpreter - it is never silently passed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import registry  # noqa: E402

EXPECTED_MODULES = {
    "pipd_ls_sp/cli.py",
    "pipd_ls_sp/requirements.py",
    "pipd_ls_sp/repo_context.py",
    "pipd_ls_sp/projection.py",
}


def _load_build_dist():
    spec = importlib.util.spec_from_file_location("pipd_build_dist", ROOT / "tools" / "build_dist.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class WheelDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build_dist = _load_build_dist()
        cls._orig_dist = cls.build_dist.DIST

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build_dist.DIST = cls._orig_dist

    def _build_into(self, dst: Path) -> tuple[Path, dict]:
        self.build_dist.DIST = dst
        manifest = self.build_dist.build_wheel()
        return dst / manifest["artefact"], manifest

    # --------------------------------------------------------------- structure
    def test_required_members_present_and_hashes_match_zip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            whl, manifest = self._build_into(Path(td) / "dist")
            with zipfile.ZipFile(whl) as z:
                names = set(z.namelist())
                for member in manifest["members"]:
                    self.assertIn(member, names, f"{member} recorded but absent from zip")
                    self.assertEqual(manifest["members"][member], _sha256(z.read(member)),
                                     f"{member} manifest sha != zip bytes sha")
            for module in EXPECTED_MODULES:
                self.assertIn(module, names, f"required module {module} missing from wheel")
            self.assertIn("pipd_ls_sp/schemas/registry.json", names)
            schema_files = [n for n in names if n.startswith("pipd_ls_sp/schemas/")
                            and n.endswith(".schema.json")]
            self.assertEqual(len(schema_files), 19, "wheel must carry all 19 schema files")

    def test_manifest_records_frozen_identity_and_digests(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            dist = Path(td) / "dist"
            whl, manifest = self._build_into(dist)
            on_disk = json.loads((dist / "WHEEL_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(on_disk["candidate_head"], manifest["candidate_head"])
            self.assertNotEqual(manifest["candidate_head"], "", "candidate_head must be recorded")
            self.assertEqual(manifest["member_count"], len(manifest["members"]))
            canonical = json.dumps(
                [[k, manifest["members"][k]] for k in sorted(manifest["members"])],
                ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            self.assertEqual(manifest["product_digest"], _sha256(canonical.encode()))
            self.assertEqual(manifest["sha256"], _sha256(whl.read_bytes()))

    # --------------------------------------------------------------- self-consistency
    def test_packaged_schema_copy_is_complete_and_self_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            whl, _ = self._build_into(Path(td) / "dist")
            extract = Path(td) / "x"
            with zipfile.ZipFile(whl) as z:
                z.extractall(extract)
            packaged = extract / "pipd_ls_sp" / "schemas"
            reg = registry.load_registry(packaged)   # exact-set + order + required_fields checks
            self.assertEqual(len(reg["families"]), 19)
            names = [f["contract"] for f in reg["families"]]
            self.assertEqual(names, registry.SOURCE_ORDER)
            for family in names:
                self.assertTrue((packaged / f"{family}.schema.json").is_file(),
                                f"packaged copy missing {family}.schema.json")

    # --------------------------------------------------------------- determinism
    def test_two_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            whl_a, man_a = self._build_into(Path(td) / "a")
            whl_b, man_b = self._build_into(Path(td) / "b")
            self.assertEqual(_sha256(whl_a.read_bytes()), _sha256(whl_b.read_bytes()),
                             "two builds of the same tree must be byte-identical")
            self.assertEqual(man_a["sha256"], man_b["sha256"])
            self.assertEqual(man_a["product_digest"], man_b["product_digest"])

    # --------------------------------------------------------------- real venv (optional)
    def test_installed_package_is_self_sufficient(self) -> None:
        reason = self._venv_unavailable_reason()
        if reason:
            print(f"SKIP test_installed_package_is_self_sufficient: {reason}")
            self.skipTest(reason)
        with tempfile.TemporaryDirectory() as td:
            whl, _ = self._build_into(Path(td) / "dist")
            venv = Path(td) / "venv"
            r = subprocess.run([sys.executable, "-m", "venv", str(venv)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                self.skipTest(f"python -m venv failed: {r.stderr.strip()[:200]}")
            vpy = self._venv_python(venv)
            outside = Path(td) / "cwd"
            outside.mkdir()
            env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
            r = subprocess.run([str(vpy), "-m", "pip", "install", "--no-index", "--no-deps", str(whl)],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, f"pip install failed: {r.stdout + r.stderr}")
            prog = ("import json, pipd_ls_sp, pipd_ls_sp.registry as r;"
                    "reg = r.load_registry();"
                    "print(json.dumps({'file': pipd_ls_sp.__file__, 'families': len(reg['families'])}))")
            r = subprocess.run([str(vpy), "-c", prog], capture_output=True, text=True,
                               cwd=str(outside), env=env)
            self.assertEqual(r.returncode, 0, f"registry load failed: {r.stdout + r.stderr}")
            payload = json.loads(r.stdout.strip().splitlines()[-1])
            self.assertEqual(payload["families"], 19)
            pydir = Path(payload["file"]).resolve().parent
            self.assertNotEqual(os.path.commonpath([str(pydir), str(ROOT)]), str(ROOT),
                                "imported module resolved back to the source checkout")

    # --------------------------------------------------------------- doctor schema truth (F-R5-01)
    def test_installed_doctor_diagnoses_installed_schema_surface(self) -> None:
        """`pipd doctor` run from a scratch cwd must PASS and name the INSTALLED surface.

        WO-S4-DIAG-001: the healthy wheel's packaged ``schemas/`` is the surface the CLI
        actually resolves, so ``doctor`` must report ``schema_source.mode == "INSTALLED"``
        and 19 families - not silently pass by reading an unrelated workspace copy.
        """
        reason = self._venv_unavailable_reason()
        if reason:
            print(f"SKIP test_installed_doctor_diagnoses_installed_schema_surface: {reason}")
            self.skipTest(reason)
        with tempfile.TemporaryDirectory() as td:
            whl, _ = self._build_into(Path(td) / "dist")
            venv = Path(td) / "venv"
            r = subprocess.run([sys.executable, "-m", "venv", str(venv)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                self.skipTest(f"python -m venv failed: {r.stderr.strip()[:200]}")
            vpy = self._venv_python(venv)
            outside = Path(td) / "cwd"
            outside.mkdir()
            env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
            r = subprocess.run([str(vpy), "-m", "pip", "install", "--no-index", "--no-deps", str(whl)],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, f"pip install failed: {r.stdout + r.stderr}")
            r = subprocess.run([str(vpy), "-m", "pipd_ls_sp.cli", "doctor"],
                               capture_output=True, text=True, cwd=str(outside), env=env)
            self.assertEqual(r.returncode, 0, f"doctor must exit 0 on a healthy wheel: {r.stdout + r.stderr}")
            payload = json.loads(r.stdout)
            self.assertEqual(payload["verdict"], "PASS")
            self.assertEqual(payload["families"], 19)
            self.assertEqual(payload["schema_source"]["mode"], "INSTALLED")
            self.assertNotEqual(os.path.commonpath([payload["schema_source"]["path"], str(ROOT)]), str(ROOT),
                                "doctor resolved the schemas surface back to the source checkout")

    # --------------------------------------------------------------- helpers
    def _venv_unavailable_reason(self) -> str:
        try:
            import venv as _venv  # noqa: F401
        except Exception as exc:  # pragma: no cover
            return f"venv module unavailable: {exc}"
        r = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
        if r.returncode != 0:
            return f"pip unavailable in test interpreter: {(r.stderr or r.stdout).strip()[:120]}"
        return ""

    def _venv_python(self, venv: Path) -> Path:
        for rel in ("bin/python", "Scripts/python.exe", "bin/python3", "Scripts/python"):
            p = venv / rel
            if p.exists():
                return p
        return venv / "bin" / "python"


if __name__ == "__main__":
    unittest.main()
