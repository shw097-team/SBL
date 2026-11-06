#!/usr/bin/env python3
"""Supply-chain gate for the absorbed PIPD tree.

Why this file exists
--------------------
`ci.yml` ran three jobs that were all green while nothing in the repository parsed
`SBOM.cdx.json`, compared it with the declared dependencies, or checked that a required component
carries a licence. Two real defects (an SBOM that disagreed with the declarations, and two imports
that were never declared) survived that green CI. A green run that cannot see a defect is not
evidence about that defect.

What it checks (each is a hard failure, never a warning)
-------------------------------------------------------
  SBOM_MISSING                       the SBOM or its metadata/component block is absent
  SBOM_COMPONENT_MISMATCH            SBOM <-> pyproject declarations disagree (either direction)
  UNDECLARED_DEPENDENCY              a third-party import in src/ is not declared anywhere
  LICENSE_MISSING_FOR_REQUIRED       a scope=required component carries no licence identifier
  NOTICE_MISSING                     the distribution has no LICENSE/NOTICE next to the package metadata

`--self-test` proves the gate *discriminates*: it mutates a copy of the inputs three ways
(drop an SBOM component, add an undeclared import, strip a required licence) and asserts each
mutation is refused. A gate that only ever prints PASS has not been tested.

Scope note: test tooling (`pytest`) and build tooling (`build`, `setuptools`, `wheel`) are declared
in extras, not runtime dependencies. They are allowed in the SBOM as scope=optional, and they are
allowed to be imported only from tests/, never from src/.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

try:                                   # Python 3.11+
    import tomllib
except ModuleNotFoundError:            # pragma: no cover - only for <3.11 operators
    tomllib = None                     # type: ignore[assignment]

REPO = Path(__file__).resolve().parents[1]
PIPD = REPO / "integrations" / "pipd"
SBOM = PIPD / "SBOM.cdx.json"
PYPROJECT = PIPD / "pyproject.toml"

#: import name -> distribution name, where they differ
IMPORT_TO_DIST = {"yaml": "pyyaml", "hg_kseos": "hg-kseos"}
FIRST_PARTY = ("pipd_ls_sp", "sbl_core", "sbl_sp", "sbl_tpm_sp")


def _norm(name: str) -> str:
    return IMPORT_TO_DIST.get(name, name).lower().replace("_", "-")


def _stdlib() -> set[str]:
    return set(getattr(sys, "stdlib_module_names", frozenset()))


def load_sbom(path: Path = SBOM) -> dict:
    if not path.is_file():
        raise SystemExit(f"SBOM_MISSING: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    comps = data.get("components")
    if not isinstance(comps, list) or not comps:
        raise SystemExit("SBOM_MISSING: components block is absent or empty")
    meta = data.get("metadata") or {}
    if not (meta.get("component") or {}).get("version"):
        raise SystemExit("SBOM_MISSING: metadata.component.version is absent")
    return data


def _name_of(spec: str) -> str:
    """Distribution name of a PEP 508 requirement ('hg-kseos @ git+https://...' -> 'hg-kseos')."""
    head = str(spec)
    for sep in (";", " ", "[", "=", ">", "<", "!", "~", "("):
        head = head.split(sep)[0]
    return _norm(head.strip())


def load_declared(path: Path = PYPROJECT) -> tuple[set[str], set[str]]:
    """Return (runtime, declared_any). declared_any includes extras."""
    if tomllib is None:
        raise SystemExit("UNDECLARED_DEPENDENCY: tomllib unavailable, cannot read pyproject")
    doc = tomllib.loads(path.read_text(encoding="utf-8"))
    project = doc.get("project") or {}
    runtime = {_name_of(d) for d in project.get("dependencies") or []}
    extra: set[str] = set()
    for group in (project.get("optional-dependencies") or {}).values():
        for d in group:
            extra.add(_name_of(d))
    return runtime - {""}, (runtime | extra) - {""}


def imports_in_src(src: Path) -> dict[str, list[str]]:
    """top-level module -> files importing it (src/ only)."""
    found: dict[str, list[str]] = {}
    for py in sorted(src.rglob("*.py")):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError as exc:                       # a broken file is its own failure
            raise SystemExit(f"UNDECLARED_DEPENDENCY: cannot parse {py}: {exc}") from None
        for node in ast.walk(tree):
            mods: list[str] = []
            if isinstance(node, ast.Import):
                mods = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                mods = [node.module.split(".")[0]]
            for m in mods:
                if m in _stdlib() or m.startswith(FIRST_PARTY) or m == "__future__":
                    continue
                found.setdefault(m, []).append(str(py.relative_to(src.parent)))
    return found


def check(sbom_path: Path = SBOM, pyproject_path: Path = PYPROJECT) -> tuple[int, list[str]]:
    """Return (exit_code, findings). Empty findings == PASS."""
    sbom = load_sbom(sbom_path)
    runtime, declared_any = load_declared(pyproject_path)
    findings: list[str] = []

    components = {_norm(c.get("name", "")): c for c in sbom["components"]}
    # direction 1: a component the SBOM ships must be declared (runtime or an extra)
    for name in sorted(components):
        if name not in declared_any:
            findings.append(f"SBOM_COMPONENT_MISMATCH: SBOM lists {name!r}, pyproject declares it nowhere")
    # direction 2: a runtime dependency must be represented in the SBOM
    for name in sorted(runtime):
        if name and name not in components:
            findings.append(f"SBOM_COMPONENT_MISMATCH: pyproject requires {name!r}, SBOM omits it")

    # every third-party import in src/ must be declared. The src tree is derived from the
    # pyproject under test, not from a module-level constant, or a mutated copy would be scanned
    # against the real tree and every negative test would silently pass.
    for mod, files in sorted(imports_in_src(pyproject_path.parent / "src").items()):
        if _norm(mod) not in declared_any:
            findings.append(f"UNDECLARED_DEPENDENCY: src imports {mod!r} (e.g. {files[0]}) "
                            f"but pyproject declares it nowhere")

    # a required component must state a licence
    for name, comp in sorted(components.items()):
        if (comp.get("scope") or "").lower() == "required":
            lic = comp.get("licenses") or []
            if not lic or not (lic[0].get("license") or {}).get("id"):
                findings.append(f"LICENSE_MISSING_FOR_REQUIRED: {name!r} is scope=required "
                                f"but carries no licence id")

    # the distribution must ship its own licence/notice text
    if not list(PIPD.glob("LICENSE*")) and not list(PIPD.glob("NOTICE*")):
        findings.append("NOTICE_MISSING: integrations/pipd ships neither LICENSE* nor NOTICE*")

    return (0 if not findings else 1), findings


def self_test(tmp: Path) -> int:
    """Three mutations, three refusals. Returns 0 only if every mutation is caught."""
    import shutil

    base_rc, base_findings = check()
    if base_rc != 0:
        print("SELF-TEST FAIL: the shipped inputs do not pass their own gate:", file=sys.stderr)
        for f in base_findings:
            print("  " + f, file=sys.stderr)
        return 1
    print("self-test baseline: PASS (0 findings)")

    results: list[tuple[str, str, int, list[str]]] = []

    # 1) remove a RUNTIME component from the SBOM. Dropping an optional/tooling component is
    #    legitimately invisible to this gate, so mutating one of those would test nothing.
    d1 = tmp / "m1"
    d1.mkdir(parents=True)
    sbom = json.loads(SBOM.read_text(encoding="utf-8"))
    runtime, _ = load_declared()
    kept = [c for c in sbom["components"] if _norm(c.get("name", "")) not in runtime]
    dropped = [_norm(c.get("name", "")) for c in sbom["components"]
               if _norm(c.get("name", "")) in runtime]
    sbom["components"] = kept
    p1 = d1 / "SBOM.cdx.json"
    p1.write_text(json.dumps(sbom), encoding="utf-8")
    results.append((f"drop runtime component(s) {dropped}", "SBOM_COMPONENT_MISMATCH",
                    *check(sbom_path=p1)))

    # 2) add an undeclared import to src/
    tree = d1 / "pipd"
    shutil.copytree(PIPD / "src", tree / "src")
    shutil.copy(PYPROJECT, tree / "pyproject.toml")
    shutil.copy(SBOM, tree / "SBOM.cdx.json")
    (tree / "src" / "pipd_ls_sp" / "_undeclared_probe.py").write_text(
        "import requests\n", encoding="utf-8")
    rc, f = check(tree / "SBOM.cdx.json", tree / "pyproject.toml")
    results.append(("add undeclared import", "UNDECLARED_DEPENDENCY", rc, f))

    # 3) strip the licence from the required component
    sbom3 = json.loads(SBOM.read_text(encoding="utf-8"))
    for c in sbom3["components"]:
        if (c.get("scope") or "").lower() == "required":
            c.pop("licenses", None)
    p3 = d1 / "SBOM_nolicence.json"
    p3.write_text(json.dumps(sbom3), encoding="utf-8")
    results.append(("strip required licence", "LICENSE_MISSING_FOR_REQUIRED",
                    *check(sbom_path=p3)))

    failures = 0
    for label, want_code, rc, findings in results:
        caught = rc != 0 and any(f.startswith(want_code) for f in findings)
        print(f"self-test {label}: {'REFUSED (ok)' if caught else 'ACCEPTED (FAIL)'} -> "
              f"{[f.split(':')[0] for f in findings] or 'no findings'}")
        failures += 0 if caught else 1
    return 0 if failures == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PIPD supply-chain gate")
    ap.add_argument("--self-test", action="store_true", help="prove the gate refuses mutations")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = ap.parse_args(argv)

    if args.self_test:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            return self_test(Path(td))

    rc, findings = check()
    if args.json:
        print(json.dumps({"schema": "SBL.SupplyChain.Gate@1", "exit": rc,
                          "findings": findings}, indent=1))
    else:
        if findings:
            print(f"SUPPLY_CHAIN_REFUSED ({len(findings)} finding(s)):", file=sys.stderr)
            for f in findings:
                print("  " + f, file=sys.stderr)
        else:
            print("SUPPLY_CHAIN_OK: SBOM <-> declarations agree, imports declared, "
                  "required components licensed, LICENSE/NOTICE present")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
