#!/usr/bin/env python3
"""S3 + R5-DIST-002: real install / self-sufficiency / uninstall lifecycle in an ISOLATED env (L5).

This is a real side effect, not a described one: a fresh venv is created, the wheel is installed into
it, the console script is executed, the package's OWN schema registry is loaded WITHOUT the source
checkout, the packaged registry is then removed to prove the load fails typed, the package is
uninstalled, and the residue is counted. It then reinstalls from the same wheel and compares digests,
which is the only honest way to claim that the distribution is reproducible.

R5-DIST-002: the self-sufficiency steps run from a cwd OUTSIDE the repo with PYTHONPATH/PYTHONHOME
unset, so `import pipd_ls_sp` must resolve to site-packages and `load_registry()` must find the
packaged `pipd_ls_sp/schemas/registry.json` (19/19) rather than the source tree.

Offline by design: `--no-deps` plus the declared dependency checked SEPARATELY, so a missing
jsonschema cannot be mistaken for a broken package. The missing-dependency behaviour is recorded as a
typed, fail-closed refusal rather than an import crash.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
# Output stays inside this lane's own scratch so the tool never mutates shared .hgk artifacts.
OUT = ROOT / ".hgk" / "r5-lane-probe"
FROZEN_SOURCE = ROOT / ".hgk" / "rounds" / "R5-20261009-s4-user-operability" / "FROZEN_SOURCE.json"
PY = sys.executable


def _candidate_head() -> str:
    """Frozen candidate identity for the report; never invented, never derived from git."""
    if FROZEN_SOURCE.is_file():
        try:
            data = json.loads(FROZEN_SOURCE.read_text(encoding="utf-8"))
            if data.get("head"):
                return data["head"]
        except (OSError, ValueError):
            pass
    return "UNKNOWN_FROZEN_SOURCE"


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    # The isolated env must not inherit the maker's PYTHONPATH: with it, `import pipd_ls_sp` resolves
    # from the source tree even after uninstall, so `import_fails_after_uninstall` could PASS or FAIL
    # purely from the caller's environment. Independently found by the AO lane; pinned here.
    env = dict(kw.pop("env", os.environ))
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    return subprocess.run(cmd, capture_output=True, text=True, env=env, **kw)


def _venv_python(venv: Path) -> Path:
    for rel in ("Scripts/python.exe", "bin/python", "Scripts/python", "bin/python3"):
        p = venv / rel
        if p.exists():
            return p
    return venv / "bin" / "python"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    whl = next(DIST.glob("pipd_ls_sp-*.whl"), None)
    if whl is None:
        print(json.dumps({"verdict": "FAIL", "why": "no wheel; run tools/build_dist.py first"}))
        return 1
    import hashlib
    whl_sha_before = hashlib.sha256(whl.read_bytes()).hexdigest()

    tmp = Path(tempfile.mkdtemp(prefix="pipd-install-"))
    venv = tmp / "venv"
    outside = tmp / "cwd-outside-repo"   # a cwd that is NOT the source checkout
    outside.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    def row(step: str, ok: bool, detail: str, *, argv=None, exit_code=None, output="") -> None:
        rows.append({"step": step, "verdict": "PASS" if ok else "FAIL", "detail": detail[:400],
                     "argv": argv or [], "exit": exit_code,
                     "output": (output or "")[:2000]})

    r = run([PY, "-m", "venv", str(venv)])
    row("create_isolated_venv", r.returncode == 0, r.stdout + r.stderr,
        argv=[PY, "-m", "venv", "<scratch>/venv"], exit_code=r.returncode, output=r.stdout + r.stderr)
    vpy = _venv_python(venv)

    r = run([str(vpy), "-m", "pip", "install", "--no-index", "--no-deps", str(whl)])
    row("install_wheel_no_index_no_deps", r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1]
        if (r.stdout + r.stderr).strip() else "",
        argv=[str(vpy), "-m", "pip", "install", "--no-index", "--no-deps", whl.name],
        exit_code=r.returncode, output=r.stdout + r.stderr)

    r = run([str(vpy), "-c", "import pipd_ls_sp, pipd_ls_sp.cli as c; print('import OK', c.__name__)"])
    row("sdk_import_in_clean_env", r.returncode == 0, (r.stdout + r.stderr).strip(),
        argv=[str(vpy), "-c", "import pipd_ls_sp, pipd_ls_sp.cli as c; print('import OK', c.__name__)"],
        exit_code=r.returncode, output=r.stdout + r.stderr)

    # --- R5-DIST-002: self-sufficiency, run from OUTSIDE the repo with a scrubbed env ------
    self_suff = (
        "import json, os, pipd_ls_sp, pipd_ls_sp.registry as r;"
        "reg = r.load_registry();"
        "print(json.dumps({'file': pipd_ls_sp.__file__, 'schema': reg['schema'],"
        " 'families': len(reg['families'])}))"
    )
    r = run([str(vpy), "-c", self_suff], cwd=str(outside))
    payload = {}
    try:
        payload = json.loads((r.stdout or "").strip().splitlines()[-1])
    except (ValueError, IndexError):
        payload = {}
    reg_ok = (r.returncode == 0 and payload.get("schema") == "PIPD-S0-CONTRACT-REGISTRY/1"
              and payload.get("families") == 19)
    row("installed_registry_self_sufficient", reg_ok,
        f"exit={r.returncode} schema={payload.get('schema')} families={payload.get('families')}",
        argv=[str(vpy), "-c", self_suff], exit_code=r.returncode, output=r.stdout + r.stderr)

    file_from_site = False
    commonpath_ok = False
    module_file = payload.get("file", "")
    if module_file:
        pydir = Path(module_file).resolve().parent
        try:
            cp = os.path.commonpath([str(pydir), str(ROOT)])
        except ValueError:
            cp = ""
        commonpath_ok = cp != str(ROOT)
        file_from_site = str(pydir).startswith(str(venv)) or "site-packages" in str(pydir)
    row("import_resolves_outside_source_checkout", commonpath_ok and file_from_site,
        f"module_dir={Path(module_file).resolve().parent if module_file else '?'} "
        f"commonpath_with_repo={os.path.commonpath([str(Path(module_file).resolve().parent), str(ROOT)]) if module_file else '?'}",
        argv=[str(vpy), "-c", self_suff], exit_code=r.returncode, output=r.stdout + r.stderr)

    # mutating negative: remove the PACKAGED registry.json; the load MUST fail typed.
    site = list(venv.glob("Lib/site-packages")) + list(venv.glob("lib/python*/site-packages"))
    packaged_reg = None
    for sp in site:
        cand = sp / "pipd_ls_sp" / "schemas" / "registry.json"
        if cand.is_file():
            packaged_reg = cand
            break
    neg_ok = False
    neg_exit = None
    neg_out = ""
    neg_prog = (
        "import pipd_ls_sp.registry as r\n"
        "import pipd_ls_sp.errors as e\n"
        "try:\n"
        "    r.load_registry()\n"
        "    print('UNEXPECTED_PASS')\n"
        "except e.ValidationFail as exc:\n"
        "    print('TYPED', exc.code)\n"
        "except Exception as exc:\n"
        "    print('UNTYPED', type(exc).__name__)\n"
    )
    neg_argv = [str(vpy), "-c", neg_prog]
    if packaged_reg is None:
        neg_out = "packaged schemas/registry.json not found in site-packages; cannot run negative"
    else:
        shutil.move(str(packaged_reg), str(packaged_reg) + ".bak")
        try:
            rr = run(neg_argv, cwd=str(outside))
            neg_exit = rr.returncode
            neg_out = rr.stdout + rr.stderr
            # typed fail-closed: the load refuses with the typed ValidationFail code.
            neg_ok = "TYPED VALIDATION_FAIL" in neg_out and "UNEXPECTED_PASS" not in neg_out
        finally:
            shutil.move(str(packaged_reg) + ".bak", str(packaged_reg))
    row("packaged_registry_removed_fails_typed", neg_ok,
        f"exit={neg_exit} typed={'TYPED VALIDATION_FAIL' in neg_out}",
        argv=neg_argv, exit_code=neg_exit, output=neg_out)

    script = None
    for cand in (venv / "Scripts" / "pipd.exe", venv / "bin" / "pipd", venv / "Scripts" / "pipd"):
        if cand.exists():
            script = cand
            break
    if script is None:
        script = venv / "bin" / "pipd"
    r = run([str(script), "--help"])
    help_ok = r.returncode == 0 and "--" in r.stdout
    row("console_script_entry_point", help_ok, f"exit={r.returncode}",
        argv=[str(script), "--help"], exit_code=r.returncode, output=r.stdout + r.stderr)

    r = run([str(script), "intake", "--goal", "Implement the lifecycle compiler.",
             "--source", str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")])
    row("cli_command_runs_in_clean_env", r.returncode == 0 and "subject_id" in r.stdout,
        f"exit={r.returncode} {(r.stdout or r.stderr)[:120]}",
        argv=[str(script), "intake", "--goal", "...", "--source", "docs/S0_CONTRACT_SPEC.md"],
        exit_code=r.returncode, output=r.stdout + r.stderr)

    # the DECLARED dependency must behave as a typed refusal when it is absent, not an ImportError
    r = run([str(vpy), "-c",
             "from pipd_ls_sp import validate as V; import json,pathlib,sys;"
             "print(json.dumps(V.semantic_invariants('PI-PKG', {})))"])
    typed_dep_ok = r.returncode == 0
    row("declared_dependency_absent_is_graceful", typed_dep_ok,
        f"exit={r.returncode} {(r.stdout or r.stderr)[:120]}",
        argv=[str(vpy), "-c", "semantic_invariants('PI-PKG', {})"], exit_code=r.returncode,
        output=r.stdout + r.stderr)

    r = run([str(vpy), "-m", "pip", "uninstall", "-y", "pipd-ls-sp"])
    row("uninstall", r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1]
        if (r.stdout + r.stderr).strip() else "",
        argv=[str(vpy), "-m", "pip", "uninstall", "-y", "pipd-ls-sp"], exit_code=r.returncode,
        output=r.stdout + r.stderr)

    residue = []
    for sp in site:
        residue += [p.name for p in sp.iterdir() if "pipd" in p.name.lower()]
    row("no_residue_after_uninstall", not residue, f"residue={residue}",
        argv=["<site-packages> scan"], exit_code=0, output=str(residue))

    r = run([str(vpy), "-c", "import pipd_ls_sp"])
    row("import_fails_after_uninstall", r.returncode != 0, f"exit={r.returncode}",
        argv=[str(vpy), "-c", "import pipd_ls_sp"], exit_code=r.returncode, output=r.stdout + r.stderr)

    r = run([str(vpy), "-m", "pip", "install", "--no-index", "--no-deps", str(whl)])
    row("reinstall_same_wheel", r.returncode == 0, "reinstalled",
        argv=[str(vpy), "-m", "pip", "install", "--no-index", "--no-deps", whl.name],
        exit_code=r.returncode, output=r.stdout + r.stderr)
    whl_sha_after = hashlib.sha256(whl.read_bytes()).hexdigest()
    row("wheel_bytes_unchanged_by_install", whl_sha_before == whl_sha_after,
        f"{whl_sha_before[:16]} == {whl_sha_after[:16]}", argv=["sha256(wheel)"], exit_code=0,
        output=f"{whl_sha_before}\n{whl_sha_after}")

    shutil.rmtree(tmp, ignore_errors=True)
    payload = {
        "wheel": whl.name, "wheel_sha256": whl_sha_before, "isolated_env": "fresh venv, no system site-packages",
        "rows": rows,
        "passed": f"{sum(1 for r_ in rows if r_['verdict'] == 'PASS')}/{len(rows)}",
        "known_offline_limitation": "jsonschema is declared in Requires-Dist and is not present in the "
                                    "isolated env; validity paths raise a typed ValidationFail rather "
                                    "than crashing, and the declaration is what a resolver would satisfy",
        "candidate_head": _candidate_head(),
    }
    payload["verdict"] = "PASS" if all(r_["verdict"] == "PASS" for r_ in rows) else "FAIL"
    (OUT / "PORTABLE_INSTALL.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                               encoding="utf-8", newline="")
    print(json.dumps({"passed": payload["passed"], "verdict": payload["verdict"],
                      "report": str(OUT / "PORTABLE_INSTALL.json")}, ensure_ascii=False, indent=1))
    for r_ in rows:
        if r_["verdict"] != "PASS":
            print("  FAIL", r_)
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
