"""S4R3-F006 (P0): the STANDARD build must ship the contract registry with the package.

The finding
-----------
A backend-driven build (``python -m build --wheel``) produced a wheel with NO
``pipd_ls_sp/schemas/`` at all: the canonical ``schemas/`` tree lives at the repository root while
``[tool.setuptools.package-data]`` can only reach data already inside a package directory. Installed
into a clean venv, ``pipd doctor`` reported ``mode=NONE`` / ``verdict=FAIL`` and exited 1. The
hand-built wheel from ``tools/build_dist.py`` never had this defect, which is why the earlier
``tests/test_wheel_distribution.py`` suite could not see it: it exercises the hand-built artefact,
not the backend-driven one.

What this module proves
-----------------------
* the mirror helper that ``setup.py`` actually uses reproduces ``registry.json`` + every schema the
  registry declares, byte for byte, and refuses on registry/file disagreement;
* the full ``python -m build --wheel`` path ships those files (skipped with an explicit reason when
  the build toolchain is not installed -- never silently passed);
* the installed package resolves its own registry (``mode=INSTALLED``) with no source tree on the
  path;
* NEGATIVE CONTROL: the same build with the hook removed produces a wheel that does NOT resolve the
  packaged surface, so this module would actually fail if F006 were reintroduced.

The build runs in a temporary copy of the packaging inputs so the worktree stays clean; the copy is
checked for the presence of every input it needs, so a renamed or added input fails loudly here
rather than silently weakening the test.
"""
from __future__ import annotations

import hashlib
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
# Standalone bootstrap: the repository convention (asserted by
# tests/test_tooling_executes.py::test_every_test_file_bootstraps_sys_path) is that no test file may
# rely on a sibling having put the package or the repo root on the path first.
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

# The packaging inputs a backend-driven build of this project reads. Kept explicit (rather than a
# whole-tree copy, which would drag ~62 MB of round evidence) and asserted below.
BUILD_INPUTS = ("pyproject.toml", "setup.py", "MANIFEST.in", "LICENSE", "NOTICE", "src", "schemas")
PACKAGE = "pipd_ls_sp"


def _load_mirror():
    """Load ``setup.py`` as a module (never as ``__main__``, so ``setup()`` is not invoked) and return
    it: the test then exercises the VERY SAME functions the build backend runs, rather than a copy."""
    path = ROOT / "setup.py"
    spec = importlib.util.spec_from_file_location("pipd_setup_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mirror = _load_mirror()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _toolchain_available() -> tuple[bool, str]:
    try:
        import build  # noqa: F401
    except Exception as exc:  # pragma: no cover - environment dependent
        return False, f"the `build` module is not importable in this interpreter ({exc})"
    try:
        import setuptools  # noqa: F401
    except Exception as exc:  # pragma: no cover - environment dependent
        return False, f"setuptools is not importable in this interpreter ({exc})"
    return True, ""


def _stage_inputs(destination: Path) -> None:
    missing = [name for name in BUILD_INPUTS if not (ROOT / name).exists()]
    if missing:
        raise AssertionError(
            "this test copies an explicit list of packaging inputs; it is stale: " + ", ".join(missing))
    for name in BUILD_INPUTS:
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def _build_wheel(tree: Path, outdir: Path) -> subprocess.CompletedProcess:
    """Backend-driven wheel build, isolated from the network (``--no-isolation``)."""
    outdir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.pop("PIPD_SCHEMAS_DIR", None)
    return subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(outdir)],
        cwd=str(tree), capture_output=True, text=True, env=env, timeout=600)


def _wheel_members(wheel: Path) -> list[str]:
    with zipfile.ZipFile(wheel) as archive:
        return archive.namelist()


def _probe_installed_surface(wheel: Path) -> dict:
    """Install the wheel into a throwaway dir (no deps, no network) and ask the resolver where the
    schemas came from. ``pipd_ls_sp.registry`` is imported from THAT directory, so the source-tree
    fallback cannot satisfy the answer. ``describe_schemas_source`` never raises, so this reports the
    surface even when the registry cannot be loaded -- which is exactly the regression it must catch."""
    script = (
        "import json, pipd_ls_sp.registry as r\n"
        "out = {'source': r.describe_schemas_source(), 'families': None, 'registry_error': None}\n"
        "try:\n"
        "    out['families'] = len(r.load_registry()['families'])\n"
        "except Exception as exc:\n"
        "    out['registry_error'] = f'{type(exc).__name__}: {exc}'\n"
        "print(json.dumps(out))\n")
    with tempfile.TemporaryDirectory() as raw:
        target = Path(raw) / "site"
        install = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--no-deps", "--no-index",
             "--target", str(target), str(wheel)],
            capture_output=True, text=True, timeout=300)
        if install.returncode != 0:
            raise AssertionError(f"installing the built wheel failed: {install.stdout[-2000:]}"
                                 f"{install.stderr[-2000:]}")
        probe = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, cwd=str(target), timeout=120,
            env={**os.environ, "PYTHONPATH": str(target), "PIPD_SCHEMAS_DIR": ""})
        if probe.returncode != 0:
            raise AssertionError(f"resolver probe failed: {probe.stdout}{probe.stderr}")
        return json.loads(probe.stdout.splitlines()[-1])


class MirrorHelperTests(unittest.TestCase):
    """The helper is the unit ``setup.py`` delegates to; test it directly and cheaply."""

    def test_mirror_reproduces_the_registry_byte_for_byte(self):
        expected = mirror.assert_schemas_are_consistent(ROOT / "schemas")
        declared = mirror.declared_schema_files(ROOT / "schemas")
        self.assertEqual(len(declared), 19, "the registry must declare 19 schema families here")
        with tempfile.TemporaryDirectory() as raw:
            result = mirror.mirror_schemas(ROOT / "schemas", Path(raw) / "pkg" / "schemas")
            target = Path(result["target"])
            self.assertEqual(sorted(result["written"]), sorted([f for f in expected["files"]]))
            for name in expected["files"]:
                self.assertEqual(_sha256((target / name).read_bytes()), expected["sha256"][name],
                                 f"{name} did not arrive byte-identical")
            self.assertTrue((target / "registry.json").is_file())

    def test_mirror_refuses_a_registry_naming_an_absent_schema(self):
        with tempfile.TemporaryDirectory() as raw:
            schemas = Path(raw) / "schemas"
            schemas.mkdir()
            (schemas / "registry.json").write_text(json.dumps(
                {"schema": "x", "families": [{"index": "01", "contract": "Gone",
                                              "schema_file": "schemas/Gone.schema.json"}]}),
                encoding="utf-8")
            with self.assertRaisesRegex(mirror.SchemaMirrorRefusal, "absent from"):
                mirror.mirror_schemas(schemas, Path(raw) / "out")

    def test_mirror_refuses_an_undeclared_schema_file(self):
        with tempfile.TemporaryDirectory() as raw:
            schemas = Path(raw) / "schemas"
            schemas.mkdir()
            (schemas / "registry.json").write_text(json.dumps(
                {"schema": "x", "families": [{"index": "01", "contract": "Kept",
                                              "schema_file": "schemas/Kept.schema.json"}]}),
                encoding="utf-8")
            (schemas / "Kept.schema.json").write_text("{}", encoding="utf-8")
            (schemas / "Sneaked.schema.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(mirror.SchemaMirrorRefusal, "undeclared"):
                mirror.mirror_schemas(schemas, Path(raw) / "out")

    def test_mirror_refuses_a_missing_registry(self):
        with tempfile.TemporaryDirectory() as raw:
            schemas = Path(raw) / "schemas"
            schemas.mkdir()
            with self.assertRaisesRegex(mirror.SchemaMirrorRefusal, "registry"):
                mirror.mirror_schemas(schemas, Path(raw) / "out")


class StandardBuildTests(unittest.TestCase):
    """The real backend-driven build; the actual subject of F006."""

    @classmethod
    def setUpClass(cls):
        available, reason = _toolchain_available()
        if not available:
            raise unittest.SkipTest(f"standard-wheel build not exercised here: {reason}")

    def test_wheel_ships_the_registry_and_resolves_it_when_installed(self):
        expected = mirror.assert_schemas_are_consistent(ROOT / "schemas")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tree = root / "tree"
            tree.mkdir()
            _stage_inputs(tree)
            completed = _build_wheel(tree, root / "dist")
            self.assertEqual(completed.returncode, 0,
                             f"python -m build --wheel failed:\n{completed.stdout}\n{completed.stderr}")
            wheels = sorted((root / "dist").glob("*.whl"))
            self.assertEqual(len(wheels), 1, f"expected exactly one wheel, got {wheels}")
            members = set(_wheel_members(wheels[0]))
            for name in expected["files"]:
                self.assertIn(f"{PACKAGE}/schemas/{name}", members,
                              f"{name} is missing from the backend-built wheel (F006 regression)")
            with zipfile.ZipFile(wheels[0]) as archive:
                for name, digest in expected["sha256"].items():
                    self.assertEqual(_sha256(archive.read(f"{PACKAGE}/schemas/{name}")), digest,
                                     f"{name} in the wheel differs from schemas/{name}")
            probe = _probe_installed_surface(wheels[0])
            self.assertEqual(probe["source"]["mode"], "INSTALLED",
                             f"the installed wheel did not resolve its packaged registry: {probe}")
            self.assertEqual(probe["families"], 19)

    def test_negative_control_without_the_hook_the_wheel_cannot_resolve_its_registry(self):
        """If the hook is dropped the surface must degrade -- otherwise this module proves nothing."""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tree = root / "tree"
            tree.mkdir()
            _stage_inputs(tree)
            (tree / "setup.py").unlink()
            (tree / "MANIFEST.in").unlink()
            completed = _build_wheel(tree, root / "dist")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            wheels = sorted((root / "dist").glob("*.whl"))
            self.assertEqual(len(wheels), 1)
            members = set(_wheel_members(wheels[0]))
            self.assertNotIn(f"{PACKAGE}/schemas/registry.json", members,
                             "the negative control expected a wheel WITHOUT the registry")
            probe = _probe_installed_surface(wheels[0])
            self.assertNotEqual(probe["source"]["mode"], "INSTALLED",
                                "without the build hook the packaged surface must not resolve")


class InstalledRegistryGateTests(unittest.TestCase):
    """The S4R3-F006 gate as CI actually runs it: tools/verify_installed_wheel_registry.py.

    These exist because the first version of that gate lived only inside `.github/workflows/ci.yml`
    and asserted that the doctor's `families` was a dict when `workspace.doctor` reports the family
    COUNT as an int. Nothing local executed it, so the type error was invisible until the hosted run
    went red. A gate is only worth its green if a workstation can turn it red on purpose.
    """

    @classmethod
    def setUpClass(cls):
        available, reason = _toolchain_available()
        if not available:
            raise unittest.SkipTest(f"standard-wheel build not exercised here: {reason}")
        cls._tmp = tempfile.TemporaryDirectory()
        root = Path(cls._tmp.name)
        tree = root / "tree"
        tree.mkdir()
        _stage_inputs(tree)
        completed = _build_wheel(tree, root / "dist")
        if completed.returncode != 0:
            cls._tmp.cleanup()
            raise AssertionError(f"python -m build --wheel failed:\n{completed.stdout}\n{completed.stderr}")
        wheels = sorted((root / "dist").glob("*.whl"))
        assert len(wheels) == 1, wheels
        probe = _probe_installed_surface(wheels[0])
        cls.doc = {"verdict": "PASS", "schema_source": probe["source"], "families": probe["families"]}
        cls.tmpdir = root

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _run_tool(self, doc, *extra: str):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "doctor.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(ROOT / "tools" / "verify_installed_wheel_registry.py"),
                 str(path), *extra],
                capture_output=True, text=True)

    def test_the_real_installed_probe_satisfies_the_gate(self):
        """The unmutated document the wheel really produces must pass, with the checkout denied."""
        completed = self._run_tool(self.doc, "--expect-families", "19", "--deny-prefix", str(ROOT))
        self.assertEqual(completed.returncode, 0, f"{completed.stdout}\n{completed.stderr}")
        self.assertIn("mode=INSTALLED", completed.stdout)
        self.assertIn("families=19", completed.stdout)

    def test_the_gate_refuses_a_families_mapping(self):
        """The exact mutation that made the first version of this gate fail for the wrong reason."""
        doc = dict(self.doc, families={"01": "PrimeItem"})
        completed = self._run_tool(doc, "--expect-families", "19")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("DOCTOR_FAMILIES_TYPE", completed.stderr)

    def test_the_gate_refuses_a_boolean_family_count(self):
        # `True == 1` in Python, so a bool must be rejected by type, not by value.
        completed = self._run_tool(dict(self.doc, families=True), "--expect-families", "1")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("DOCTOR_FAMILIES_TYPE", completed.stderr)

    def test_the_gate_refuses_a_wrong_family_count(self):
        completed = self._run_tool(dict(self.doc, families=18), "--expect-families", "19")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("DOCTOR_FAMILIES", completed.stderr)

    def test_the_gate_refuses_a_source_mode_resolution(self):
        doc = dict(self.doc, schema_source=dict(self.doc["schema_source"], mode="SOURCE"))
        completed = self._run_tool(doc, "--expect-families", "19")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("DOCTOR_SCHEMA_MODE", completed.stderr)

    def test_the_gate_refuses_a_non_pass_verdict(self):
        completed = self._run_tool(dict(self.doc, verdict="FAIL"), "--expect-families", "19")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("DOCTOR_VERDICT", completed.stderr)

    def test_the_gate_refuses_a_resolution_inside_the_checkout(self):
        """mode=INSTALLED is not proof on its own: say where the schemas actually came from."""
        doc = dict(self.doc, schema_source=dict(self.doc["schema_source"], path=str(ROOT / "schemas")))
        completed = self._run_tool(doc, "--expect-families", "19", "--deny-prefix", str(ROOT))
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("DOCTOR_SCHEMA_PATH_IN_CHECKOUT", completed.stderr)
        # ... and the same document passes when the checkout is not the denied prefix.
        ok = self._run_tool(doc, "--expect-families", "19", "--deny-prefix", str(self.tmpdir / "nowhere"))
        self.assertEqual(ok.returncode, 0, ok.stderr)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
