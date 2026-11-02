"""R5R CE-1/CE-2 repair regression: pin the two verification defects.

CE-1 -- ``validate`` resolved schemas ONLY from ``--root/schemas``, so a cwd without a
``schemas/`` tree (e.g. an installed wheel) hit ``FileNotFoundError`` even though ``doctor``
resolved the wheel's own packaged copy. ``validate`` must resolve through the same registry
chain, with a workspace-local ``<root>/schemas`` winning when it actually contains
``registry.json``.

CE-2 -- a bundle built from the compilers' OWN stdout (PI carries the ``_profile_meta``
sidecar) was rejected because the sidecar was schema-checked unstripped against a schema that
declares ``additionalProperties: false``. The non-record sidecar must be stripped from a
single definition shared by ``validate`` and ``pipeline``.

These tests are written to FAIL on the pre-repair tree (see the round's ``red_state.txt``).
"""
from __future__ import annotations

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

from pipd_ls_sp import pipeline, validate, workspace  # noqa: E402

GOAL = "以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 規格包編譯系統，完成測試驗收與公開交付。"
MAKER, CHECKER = "HERMES-MAKER", "GLM-5.3-FLASH-AO-LANE"
RECEIPT = "deleg_r5r/lane-verify"


def _clean_env() -> dict:
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
    env["PYTHONPATH"] = str(ROOT / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PIPD_SCHEMAS_DIR", None)
    return env


def _run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", *args],
                          capture_output=True, text=True, env=_clean_env(), cwd=str(cwd))


def _init_git_repo(path: Path) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}

    def g(*a: str) -> None:
        subprocess.run(["git", "-C", str(path), *a], check=True,
                       capture_output=True, text=True, env=env)

    path.mkdir(parents=True, exist_ok=True)
    g("init", "-q")
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    g("add", ".")
    g("commit", "-q", "-m", "seed")


def _compilers_stdout_bundle(repo: Path) -> dict:
    """The four compilers' OWN unmodified outputs - PI keeps its ``_profile_meta`` sidecar."""
    card = pipeline.intake(GOAL, sources=[str(repo)], constraints=["c1"], non_goals=["n1"])
    pi = pipeline.compile_pi(card, "LITE")
    pd = pipeline.bind_pd(pi, {"root": str(repo), "writable_scope": "src/**"})
    ecp = pipeline.compile_ecp(pd, pi)
    tqaep = pipeline.compile_tqaep(pi, ecp, maker=MAKER, checker=CHECKER,
                                   checker_execution_receipt=RECEIPT)
    return {"PI-PKG": pi, "PD-PKG": pd, "ECP": ecp, "TQAEP": tqaep}


class CE2CompilerStdoutTests(unittest.TestCase):
    """CE-2: the compilers' own stdout must be accepted (real functions, temp git repo)."""

    def test_compilers_own_stdout_bundle_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            bundle = _compilers_stdout_bundle(repo)
            self.assertIn("_profile_meta", bundle["PI-PKG"],
                          "the PI compiler must emit its non-record sidecar (no hand-edited fixture)")
            res = validate.validate_bundle(bundle)
            self.assertEqual(res["findings"], [], str(res["findings"])[:800])
            self.assertEqual(res["verdict"], "PASS")
            self.assertEqual(res["checked"], 4)

    def test_sidecar_list_has_one_definition(self) -> None:
        """A future copy-paste must not be able to split the field lists again.

        CE-2 refinement split ONE conflated list into TWO honest concepts, each defined once:

        * ``validate.NON_RECORD_SIDECARS`` - the fields the SCHEMA CHECK strips. NO schema
          declares these; today that is exactly ``_profile_meta``.
        * ``validate.HASH_EXCLUDED_FIELDS`` - the fields the body HASH does not cover
          (identity fields + derived ``trace`` + ``_profile_meta``); ``pipeline._seal`` must
          reference exactly this object so the hash cannot diverge from its recomputation.

        The test asserts the NEW single definition honestly: the two lists are distinct, and
        neither can be re-copied into ``pipeline`` without tripping this assertion.
        """
        self.assertTrue(hasattr(validate, "NON_RECORD_SIDECARS"),
                        "validate must expose the single non-record sidecar definition")
        self.assertTrue(hasattr(validate, "HASH_EXCLUDED_FIELDS"),
                        "validate must expose the single hash-exclusion definition")
        # pipeline references BOTH by identity (imported, never re-typed).
        self.assertIs(pipeline.NON_RECORD_SIDECARS, validate.NON_RECORD_SIDECARS)
        self.assertIs(pipeline.HASH_EXCLUDED_FIELDS, validate.HASH_EXCLUDED_FIELDS)
        # The two concepts are distinct: the hash-exclusion set is the strict superset. The
        # conflation bug was exactly `trace` living in the schema-check list.
        self.assertEqual(validate.NON_RECORD_SIDECARS, ("_profile_meta",))
        self.assertIn("trace", validate.HASH_EXCLUDED_FIELDS)
        self.assertNotIn("trace", validate.NON_RECORD_SIDECARS)
        for field in ("subject_id", "version", "content_hash", "schema_version", "_profile_meta"):
            self.assertIn(field, validate.HASH_EXCLUDED_FIELDS)


class CE2TraceWideningTests(unittest.TestCase):
    """Checker counterexample CE-CODEX-TRACE-WIDENING.

    The independent checker (GPT 6.1 SOL, separate CODEX_HOME) loaded the PUBLISHED validator
    straight out of the downloaded wheel: adding an undeclared ``trace`` key to a ``PD-PKG``,
    ``ECP`` or ``TQAEP`` record is rejected there ("Additional properties are not allowed
    (trace was unexpected)"). The CE-2 repair had widened the accepted input because
    ``trace`` was in the conflated ``NON_RECORD_SIDECARS`` list, which ``validate_record``
    stripped. This test is the checker's own counterexample, pinned.
    """

    def test_undeclared_trace_is_rejected_on_pd_ecp_tqaep(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            bundle = _compilers_stdout_bundle(repo)
            # Every non-PI member carries an undeclared `trace`; every other field and the
            # ORIGINAL content_hash are left untouched (trace is hash-excluded, so the body
            # digest is unaffected and the only possible finding is the schema one).
            for contract in ("PD-PKG", "ECP", "TQAEP"):
                self.assertNotIn("trace", bundle[contract],
                                 "precondition: the compiler does not emit `trace` here")
                widened = dict(bundle[contract])
                widened["trace"] = [{"undeclared": True}]
                bundle[contract] = widened
            res = validate.validate_bundle(bundle)
            self.assertEqual(res["checked"], 4)
            self.assertEqual(res["verdict"], "FAIL", res)
            named = {f["contract"] for f in res["findings"]
                     if "trace" in f["detail"] and "was unexpected" in f["detail"]}
            self.assertEqual(named, {"PD-PKG", "ECP", "TQAEP"},
                             f"undeclared `trace` must be named for each contract: {res['findings']}")

    def test_declared_trace_on_pi_pkg_still_tolerated(self) -> None:
        # Guard the other direction: PI-PKG DECLARES `trace`, so it must stay accepted.
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _init_git_repo(repo)
            bundle = _compilers_stdout_bundle(repo)
            self.assertIn("trace", bundle["PI-PKG"])
            res = validate.validate_bundle(bundle)
            self.assertEqual(res["findings"], [], str(res["findings"])[:800])
            self.assertEqual(res["verdict"], "PASS")


class CE1ValidateSchemaResolutionTests(unittest.TestCase):
    """CE-1: validate resolves the shipped schemas and reports the source it used."""

    def _bundle_file(self, td: Path) -> Path:
        repo = Path(td) / "repo"
        _init_git_repo(repo)
        # Isolate CE-1 from CE-2: strip the sidecar so only schema RESOLUTION is under test.
        bundle = {k: (pipeline.strip_sidecar(v) if k == "PI-PKG" else v)
                  for k, v in _compilers_stdout_bundle(repo).items()}
        p = Path(td) / "bundle.json"
        p.write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
        return p

    def test_validate_resolves_shipped_schemas_without_workspace_schemas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cwd = td / "cwd"
            cwd.mkdir()
            bundle = self._bundle_file(td)
            self.assertFalse((cwd / "schemas").exists(),
                             "precondition: the cwd must have no schemas/ tree")
            r = _run_cli(["--root", str(cwd), "validate", "--bundle", str(bundle)], cwd)
            self.assertEqual(r.returncode, 0,
                             f"validate must reach a verdict; stdout={r.stdout[:400]} "
                             f"stderr={r.stderr[-400:]}")
            payload = json.loads(r.stdout)
            self.assertEqual(payload["verdict"], "PASS", payload)
            self.assertIn("schema_source", payload)
            self.assertEqual(payload["schema_source"]["mode"], "SOURCE")
            self.assertTrue(payload["schema_source"]["path"])

    def test_workspace_local_schemas_still_takes_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            ws = td / "ws"
            (ws / "schemas").mkdir(parents=True)
            for p in (ROOT / "schemas").rglob("*"):
                if p.is_file():
                    shutil.copy2(p, ws / "schemas" / p.name)
            bundle = self._bundle_file(td)
            r = _run_cli(["--root", str(ws), "validate", "--bundle", str(bundle)], ws)
            self.assertEqual(r.returncode, 0,
                             f"stdout={r.stdout[:400]} stderr={r.stderr[-400:]}")
            payload = json.loads(r.stdout)
            self.assertEqual(payload["verdict"], "PASS", payload)
            self.assertEqual(payload["schema_source"]["mode"], "WORKSPACE")
            self.assertEqual(Path(payload["schema_source"]["path"]).resolve(),
                             (ws / "schemas").resolve())

    def test_validate_reports_schema_source_mode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cwd = td / "cwd"
            cwd.mkdir()
            bundle = self._bundle_file(td)
            r = _run_cli(["--root", str(cwd), "validate", "--bundle", str(bundle)], cwd)
            payload = json.loads(r.stdout)
            src = payload["schema_source"]
            self.assertEqual(set(src), {"mode", "path", "tried"})
            self.assertIn(src["mode"], {"SOURCE", "INSTALLED", "OVERRIDE", "WORKSPACE"})


class CE1InitSecondSiteSchemaResolutionTests(unittest.TestCase):
    """CE-1, second site: ``init_workspace`` reports the family count from the resolved chain.

    ``init_workspace`` creates the skeleton (``schemas`` among it) and then read the registry from
    ``<root>/schemas`` - the empty directory it had just created - so ``init`` failed on any fresh
    or installed root. It must resolve through the SAME shared chain ``doctor``/``validate`` use,
    report which surface produced the count, and still let a workspace-local ``<root>/schemas``
    carrying a real ``registry.json`` win.
    """

    def test_init_succeeds_on_fresh_root_without_schemas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "fresh"
            root.mkdir()
            self.assertFalse((root / "schemas").exists(),
                             "precondition: the root must have no schemas/ tree")
            out = workspace.init_workspace(root)
            self.assertEqual(out["verdict"], "PASS", out)
            self.assertEqual(out["contract_families"], 19,
                             "init must report the real family count from the resolved chain")
            # every pre-existing field survives
            for field in ("verdict", "root", "created", "contract_families"):
                self.assertIn(field, out)
            src = out["schema_source"]
            self.assertEqual(set(src), {"mode", "path", "tried"})
            self.assertIn(src["mode"], {"SOURCE", "INSTALLED", "OVERRIDE"})
            self.assertTrue(src["path"], "the resolved surface must be named")
            self.assertTrue(Path(src["path"]).is_dir())

    def test_init_reports_workspace_local_schemas_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "ws"
            (root / "schemas").mkdir(parents=True)
            for p in (ROOT / "schemas").rglob("*"):
                if p.is_file():
                    shutil.copy2(p, root / "schemas" / p.name)
            out = workspace.init_workspace(root)
            self.assertEqual(out["verdict"], "PASS", out)
            self.assertEqual(out["contract_families"], 19)
            self.assertEqual(out["schema_source"]["mode"], "WORKSPACE")
            self.assertEqual(Path(out["schema_source"]["path"]).resolve(),
                             (root / "schemas").resolve())


if __name__ == "__main__":
    unittest.main(verbosity=2)
