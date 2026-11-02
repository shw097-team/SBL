"""WO-S4-DIAG-001 / F-R5-01: `doctor` must diagnose the RESOLVED schemas surface.

The challenge defect: `workspace.doctor` only ever read `<root>/schemas`, while the CLI's real
resource resolver is `registry._resolve_schemas_dir()` (``$PIPD_SCHEMAS_DIR`` -> packaged wheel
copy -> ``<repo>/schemas``). Installing a wheel whose packaged ``schemas/`` is missing
``ArtifactIdentity.schema.json`` and running ``pipd doctor`` from a healthy workspace printed
``verdict=PASS``.

These tests prove the repair against REAL mutated wheels installed into disposable venvs:
  * in-process: ``describe_schemas_source`` reports the mode, and ``doctor`` FAILs (naming the
    missing family) when a resolved ``$PIPD_SCHEMAS_DIR`` surface is torn, even though the
    workspace-local ``schemas/`` tree is healthy;
  * B4a: wheel zip rewritten with ``ArtifactIdentity.schema.json`` removed, RECORD left as-is;
  * B4b: same removal, RECORD line dropped so the member list stays consistent.
A variant that cannot even be installed is recorded as a typed refusal (with an explicit printed
reason) rather than silently counted as a pass; a whole-suite skip only happens when the test
interpreter itself lacks ``venv``/``pip``.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import registry, workspace  # noqa: E402

MISSING_FAMILY = "ArtifactIdentity"
MISSING_MEMBER = f"pipd_ls_sp/schemas/{MISSING_FAMILY}.schema.json"
WHEEL_NAME = "pipd_ls_sp-0.1.1a4-py3-none-any.whl"


def _load_build_dist():
    spec = importlib.util.spec_from_file_location("pipd_build_dist_doctor", ROOT / "tools" / "build_dist.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rewrite_zip_without_member(src: Path, dst: Path, *, adjust_record: bool) -> None:
    """Copy ``src`` to ``dst``, dropping the missing-family schema member.

    ``adjust_record`` False -> the ``RECORD`` member is left byte-identical (B4a).
    ``adjust_record`` True  -> the dropped member's ``RECORD`` line is removed too (B4b).
    """
    with zipfile.ZipFile(src) as z:
        items = [(info.filename, z.read(info.filename)) for info in z.infolist()]
    out = []
    for name, data in items:
        if name == MISSING_MEMBER:
            continue
        if adjust_record and name.endswith(".dist-info/RECORD"):
            data = b"".join(
                line for line in data.splitlines(keepends=True)
                if not line.startswith(MISSING_MEMBER.encode() + b","))
        out.append((name, data))
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in out:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            z.writestr(info, data)


class DoctorSchemaTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build_dist = _load_build_dist()
        cls._orig_dist = cls.build_dist.DIST

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build_dist.DIST = cls._orig_dist

    def _build_into(self, dst: Path) -> Path:
        self.build_dist.DIST = dst
        manifest = self.build_dist.build_wheel()
        return dst / manifest["artefact"]

    def _healthy_workspace(self, parent: Path) -> Path:
        """A scratch cwd with a healthy workspace-local ``schemas/`` tree."""
        ws = parent / "ws"
        (ws / "schemas").mkdir(parents=True)
        for p in (ROOT / "schemas").rglob("*"):
            if p.is_file():
                shutil.copy2(p, ws / "schemas" / p.name)
        return ws

    # -------------------------------------------------------- describe_schemas_source
    def test_describe_schemas_source_reports_override_mode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            override = Path(td) / "override"
            override.mkdir()
            for p in (ROOT / "schemas").rglob("*"):
                if p.is_file():
                    shutil.copy2(p, override / p.name)
            old = os.environ.get("PIPD_SCHEMAS_DIR")
            os.environ["PIPD_SCHEMAS_DIR"] = str(override)
            try:
                source = registry.describe_schemas_source()
            finally:
                if old is None:
                    os.environ.pop("PIPD_SCHEMAS_DIR", None)
                else:
                    os.environ["PIPD_SCHEMAS_DIR"] = old
            self.assertEqual(source["mode"], "OVERRIDE")
            self.assertEqual(Path(source["path"]), override)
            self.assertIn(str(override), source["tried"])
            self.assertEqual(list(source.keys()), ["mode", "path", "tried"])

    def test_describe_schemas_source_reports_source_mode_from_checkout(self) -> None:
        old = os.environ.get("PIPD_SCHEMAS_DIR")
        os.environ.pop("PIPD_SCHEMAS_DIR", None)
        try:
            source = registry.describe_schemas_source()
        finally:
            if old is not None:
                os.environ["PIPD_SCHEMAS_DIR"] = old
        # No packaged copy exists in a source checkout, so the source fallback resolves.
        self.assertEqual(source["mode"], "SOURCE")
        self.assertEqual(Path(source["path"]), (ROOT / "schemas").resolve())

    # -------------------------------------------------------- doctor on a torn resolved surface
    def test_doctor_fails_when_resolved_surface_missing_member_even_if_workspace_healthy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            torn = td / "torn"
            torn.mkdir()
            for p in (ROOT / "schemas").rglob("*"):
                if p.is_file() and p.name != f"{MISSING_FAMILY}.schema.json":
                    shutil.copy2(p, torn / p.name)
            ws = self._healthy_workspace(td)
            old = os.environ.get("PIPD_SCHEMAS_DIR")
            os.environ["PIPD_SCHEMAS_DIR"] = str(torn)
            try:
                result = workspace.doctor(ws)
            finally:
                if old is None:
                    os.environ.pop("PIPD_SCHEMAS_DIR", None)
                else:
                    os.environ["PIPD_SCHEMAS_DIR"] = old
            self.assertEqual(result["verdict"], "FAIL")
            self.assertEqual(result["schema_source"]["mode"], "OVERRIDE")
            self.assertTrue(
                any(MISSING_FAMILY in f and str(torn) in f for f in result["findings"]),
                f"a finding must name {MISSING_FAMILY} and the resolved path: {result['findings']}")

    # -------------------------------------------------------- B4: real installed wheels
    def test_b4_wheel_mutation_installed_doctor_fails(self) -> None:
        reason = self._venv_unavailable_reason()
        if reason:
            print(f"SKIP test_b4_wheel_mutation_installed_doctor_fails: {reason}")
            self.skipTest(reason)
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            healthy_wheel = self._build_into(td / "dist")
            (td / "b4a").mkdir()
            (td / "b4b").mkdir()
            b4a = td / "b4a" / WHEEL_NAME
            b4b = td / "b4b" / WHEEL_NAME
            _rewrite_zip_without_member(healthy_wheel, b4a, adjust_record=False)
            _rewrite_zip_without_member(healthy_wheel, b4b, adjust_record=True)
            ws = self._healthy_workspace(td)

            refusals: dict[str, str] = {}
            healthy = self._install_and_doctor(healthy_wheel, td / "venv_healthy", "healthy", ws, refusals)
            self.assertIsNotNone(healthy, "healthy control wheel must install")
            self.assertEqual(healthy["exit"], 0, f"healthy control must exit 0: {healthy}")
            self.assertEqual(healthy["payload"]["verdict"], "PASS")
            self.assertEqual(healthy["payload"]["families"], 19)
            self.assertEqual(healthy["payload"]["schema_source"]["mode"], "INSTALLED")

            for label, wheel in (("B4a", b4a), ("B4b", b4b)):
                got = self._install_and_doctor(wheel, td / f"venv_{label}", label, ws, refusals)
                self.assertIsNotNone(got, f"{label} must install; refusals={refusals}")
                self.assertNotEqual(got["exit"], 0, f"{label} must exit non-zero: {got}")
                self.assertEqual(got["payload"]["verdict"], "FAIL", f"{label} must FAIL: {got}")
                self.assertTrue(
                    any(MISSING_FAMILY in f for f in got["payload"]["findings"]),
                    f"{label} finding must name {MISSING_FAMILY}: {got['payload']['findings']}")

            if refusals:
                print(f"typed install refusals recorded: {refusals}")

    # -------------------------------------------------------- helpers
    def _install_and_doctor(self, wheel, venv, label, ws, refusals):
        """Install ``wheel`` into a fresh venv and run ``doctor`` from ``ws``.

        A non-zero install is recorded as a TYPED refusal in ``refusals`` (and returned as
        ``None``); it is never silently skipped and never counted as a pass.
        """
        r = subprocess.run([sys.executable, "-m", "venv", str(venv)], capture_output=True, text=True)
        if r.returncode != 0:
            refusals[label] = f"VENV_FAILED rc={r.returncode}: {r.stderr.strip()[:200]}"
            return None
        py = self._venv_python(venv)
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
        r = subprocess.run([str(py), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            refusals[label] = f"INSTALL_REFUSED rc={r.returncode}: {(r.stdout + r.stderr).strip()[-300:]}"
            return None
        r = subprocess.run([str(py), "-m", "pipd_ls_sp.cli", "doctor"],
                           capture_output=True, text=True, cwd=str(ws), env=env)
        try:
            payload = json.loads(r.stdout)
        except json.JSONDecodeError:
            return {"exit": r.returncode, "payload": {"verdict": None, "findings": [r.stdout[:300]],
                                                      "families": None, "schema_source": {}}}
        return {"exit": r.returncode, "payload": payload}

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
