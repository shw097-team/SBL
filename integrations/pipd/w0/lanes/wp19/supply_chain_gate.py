#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FHS W0 / WP-FHS-19 -- author-local supply-chain & compliance gate.

Runs seven typed checks over an ARBITRARY tree supplied by the operator:

  1. LICENSE_PRESENT                SPDX resolution from LICENSE / OWNER_LICENSE_DECISION.yaml / pyproject
  2. NOTICE_PRESENT                 NOTICE file adjacent to the licence basis
  3. SBOM_PRESENT_AND_PARSABLE      CycloneDX JSON structural validation (no third-party lib)
  4. SBOM_COMPONENT_RECONCILE       SBOM component names vs. RUNTIME dependency names
                                    ([project].dependencies / requirements / setup.py / package.json).
                                    Optional-dependencies (test extras) are reported in
                                    counts["optional_not_listed"] for visibility and never drive
                                    the verdict: a test extra is not an installed component.
  5. DEPENDENCY_DECLARED            ast import scan vs. pyproject / requirements / package.json
  6. SECRET_PATTERN_SCAN            github_pat_ / ghp_ / AKIA / PRIVATE KEY ... masked output only
  7. CI_ENTRY_PRESENT               .github/workflows or a documented re-runnable command

Every check yields verdict in {PASS, FAIL, HOLD, NOT_APPLICABLE} plus a stable
`code`.  Exit status: 1 if any FAIL, else 0.  Usage / IO problems exit 2 (they
are not compliance verdicts).

Claim ceiling of every artifact this gate writes is AUTHOR_SUPPLY_CHAIN_LOCAL.
It is NOT an independent / protected checker, does NOT produce TraceClosure and
must never be used to declare WP19 DONE.

Stdlib only (ast, json, re, tomllib, hashlib, argparse ...). No network.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

GATE_ID = "WP-FHS-19"
GATE_VERSION = "1.0.0"
SCHEMA = "FHS_W0/SUPPLY_CHAIN_GATE/v1"
CLAIM_CEILING = "AUTHOR_SUPPLY_CHAIN_LOCAL"

PASS = "PASS"
FAIL = "FAIL"
HOLD = "HOLD"
NA = "NOT_APPLICABLE"
VERDICTS = (PASS, FAIL, HOLD, NA)

SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules"}

TAIPEI = timezone(timedelta(hours=8))

MAX_SCAN_BYTES = 4 * 1024 * 1024  # per-file cap for text decoding


# --------------------------------------------------------------------------- #
# result model
# --------------------------------------------------------------------------- #
@dataclass
class CheckResult:
    check_id: str
    title: str
    verdict: str
    code: str
    detail: str = ""
    counts: dict = field(default_factory=dict)
    samples: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "verdict": self.verdict,
            "code": self.code,
            "detail": self.detail,
            "counts": self.counts,
            "samples": self.samples,
        }


# --------------------------------------------------------------------------- #
# tree walking / text helpers
# --------------------------------------------------------------------------- #
def walk_tree(tree: str):
    """Deterministic recursive walk. Returns (dirs, files) as relative POSIX paths."""
    dirs_out, files_out = [], []
    for root, dirnames, filenames in os.walk(tree, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        rel_root = os.path.relpath(root, tree)
        if rel_root != ".":
            dirs_out.append(rel_root.replace(os.sep, "/"))
        for name in sorted(filenames):
            full = os.path.join(root, name)
            if os.path.islink(full):
                continue
            rel = name if rel_root == "." else os.path.join(rel_root, name)
            files_out.append(rel.replace(os.sep, "/"))
    return sorted(dirs_out), sorted(files_out)


def read_text(path: str, limit: int = MAX_SCAN_BYTES):
    """Decode a file as text or return None when it looks binary / is too large."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return None
    if size > limit:
        return None
    try:
        with open(path, "rb") as fh:
            head = fh.read(4096)
            if b"\x00" in head:
                return None
            blob = head + fh.read()
    except OSError:
        return None
    return blob.decode("utf-8", errors="replace")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_name(name: str) -> str:
    """PEP 503-ish normalisation used for dependency name comparison."""
    name = name.strip().lower()
    name = re.split(r"[\s\[<>=!~;,@]", name, maxsplit=1)[0]
    return re.sub(r"[-_.]+", "-", name)


DIST_TO_MODULE = {
    "pyyaml": "yaml",
    "pillow": "pil",
    "beautifulsoup4": "bs4",
    "python-dateutil": "dateutil",
    "msgpack-python": "msgpack",
    "pyjwt": "jwt",
    "python-dotenv": "dotenv",
    "opencv-python": "cv2",
    "protobuf": "google",
}


# --------------------------------------------------------------------------- #
# manifests (declared dependencies)
# --------------------------------------------------------------------------- #
def discover_manifests(tree: str, files: list):
    """Return [(rel_path, kind)] for dependency manifests found in the tree."""
    out = []
    for rel in files:
        base = os.path.basename(rel).lower()
        if base == "pyproject.toml":
            out.append((rel, "pyproject"))
        elif base == "setup.py":
            out.append((rel, "setup"))
        elif base == "setup.cfg":
            out.append((rel, "setup_cfg"))
        elif base == "package.json":
            out.append((rel, "package_json"))
        elif base.startswith("requirements") and base.endswith((".txt", ".in")):
            out.append((rel, "requirements"))
    return out


def declared_dependencies(tree: str, manifests) -> dict:
    """name -> [manifest rel paths] for every declared dependency.

    Returns three views:
      declared  every name from every manifest (runtime + optional) -- used by check 5
      runtime   names installed by a plain `pip install <pkg>` -- used by check 4
      optional  names that only appear under [project.optional-dependencies] -- check 4 reports
                them but does not judge them
    A name declared both ways counts as runtime.
    """
    declared, runtime, optional, errors = {}, {}, {}, []
    for rel, kind in manifests:
        path = os.path.join(tree, rel.replace("/", os.sep))
        names = []
        extra_names = []
        try:
            if kind == "pyproject":
                with open(path, "rb") as fh:
                    data = tomllib.load(fh)
                project = data.get("project", {})
                names += list(project.get("dependencies", []) or [])
                for extra in (project.get("optional-dependencies", {}) or {}).values():
                    extra_names += list(extra or [])
            elif kind == "requirements":
                text = read_text(path) or ""
                for line in text.splitlines():
                    line = line.split("#", 1)[0].strip()
                    if not line or line.startswith("-"):
                        continue
                    names.append(line)
            elif kind == "package_json":
                data = json.loads(read_text(path) or "{}")
                for key in ("dependencies", "devDependencies", "peerDependencies"):
                    names += list((data.get(key) or {}).keys())
            elif kind in ("setup", "setup_cfg"):
                text = read_text(path) or ""
                for m in re.finditer(r"(?:install_requires|dependencies)\s*=\s*\[(.*?)\]", text, re.S):
                    names += re.findall(r"[\"']([^\"']+)[\"']", m.group(1))
                for m in re.finditer(r"(?m)^\s*(?:install_requires|dependencies)\s*=\s*\n((?:\s+\S.*\n)+)", text):
                    names += [ln.strip().rstrip(",") for ln in m.group(1).splitlines() if ln.strip()]
        except Exception as exc:  # malformed manifest is recorded, never fatal
            errors.append({"manifest": rel, "error": type(exc).__name__})
            continue
        extra_keys = {norm_name(str(raw)) for raw in extra_names}
        for raw in names + extra_names:
            name = norm_name(str(raw))
            if not name:
                continue
            declared.setdefault(name, []).append(rel)
            if name in runtime:
                runtime[name].append(rel)
            elif name in extra_keys:
                optional.setdefault(name, []).append(rel)
            else:
                runtime.setdefault(name, []).append(rel)
    return {"declared": declared, "runtime": runtime, "optional": optional, "errors": errors}


# --------------------------------------------------------------------------- #
# check 1: LICENSE_PRESENT
# --------------------------------------------------------------------------- #
LICENSE_BASENAMES = {
    "license", "license.txt", "license.md", "licence", "licence.txt",
    "licence.md", "copying", "copying.txt", "license.rst",
}
SPDX_RE = re.compile(r"SPDX-License-Identifier:\s*([A-Za-z0-9.+\-]+)")

LICENSE_SIGNATURES = (
    ("Apache-2.0", ("apache license", "version 2.0")),
    ("MIT", ("permission is hereby granted, free of charge",)),
    ("BSD-3-Clause", ("redistribution and use in source and binary forms", "neither the name")),
    ("BSD-2-Clause", ("redistribution and use in source and binary forms",)),
    ("MPL-2.0", ("mozilla public license version 2.0",)),
    ("GPL-3.0-only", ("gnu general public license", "version 3")),
)


def _spdx_from_text(text: str):
    m = SPDX_RE.search(text or "")
    if m:
        return m.group(1)
    low = (text or "").lower()
    for spdx, needles in LICENSE_SIGNATURES:
        if all(n in low for n in needles):
            return spdx
    return None


def check_license(tree: str, dirs, files, manifests) -> tuple:
    root_license, vendored, other = [], [], []
    root_licences = {}
    for rel in files:
        base = os.path.basename(rel).lower()
        depth = rel.count("/")
        if base in LICENSE_BASENAMES:
            if depth == 0:
                root_license.append(rel)
                root_licences[rel] = read_text(os.path.join(tree, rel.replace("/", os.sep))) or ""
            elif base.endswith("_license") or "/licenses/" in ("/" + rel).lower():
                vendored.append(rel)
            else:
                other.append(rel)
        elif base.endswith("_license") or base.startswith("license_"):
            vendored.append(rel)

    spdx = None
    spdx_source = None
    for rel in root_license:
        found = _spdx_from_text(root_licences.get(rel, ""))
        if found:
            spdx, spdx_source = found, rel
            break

    if spdx is None:
        for rel, kind in manifests:
            if kind != "pyproject":
                continue
            try:
                with open(os.path.join(tree, rel.replace("/", os.sep)), "rb") as fh:
                    project = tomllib.load(fh).get("project", {})
            except Exception:
                continue
            lic = project.get("license")
            if isinstance(lic, str) and lic.strip():
                spdx, spdx_source = lic.strip(), rel
                break
            if isinstance(lic, dict) and lic.get("text"):
                spdx, spdx_source = str(lic["text"]).strip(), rel
                break

    if spdx is None:
        for rel in files:
            if os.path.basename(rel).lower() in ("owner_license_decision.yaml", "owner_license_decision.yml"):
                text = read_text(os.path.join(tree, rel.replace("/", os.sep))) or ""
                m = re.search(r"(?m)^\s*spdx\s*:\s*[\"']?([A-Za-z0-9.+\-]+)", text)
                if m:
                    spdx, spdx_source = m.group(1), rel
                    break

    counts = {
        "license_files_at_root": len(root_license),
        "license_files_other_depth": len(other),
        "license_files_vendored_or_third_party": len(vendored),
        "spdx_resolved": 1 if spdx else 0,
    }
    sample = (root_license + other)[:10] + vendored[:10]

    if root_license and spdx:
        return (CheckResult("LICENSE_PRESENT", "Licence file present and SPDX-resolvable",
                            PASS, "LICENSE_SPDX_RESOLVED",
                            f"SPDX {spdx} resolved from {spdx_source}",
                            counts, sample), spdx, root_license)
    if root_license and not spdx:
        return (CheckResult("LICENSE_PRESENT", "Licence file present and SPDX-resolvable",
                            HOLD, "LICENSE_SPDX_UNPARSED",
                            "licence file(s) at tree root but no SPDX identifier or recognisable licence text",
                            counts, sample), None, root_license)
    if vendored or other:
        return (CheckResult("LICENSE_PRESENT", "Licence file present and SPDX-resolvable",
                            HOLD, "LICENSE_ONLY_VENDORED_COPIES",
                            "only third-party / vendored licence copies found; no first-party LICENSE at tree root",
                            counts, sample), None, root_license)
    return (CheckResult("LICENSE_PRESENT", "Licence file present and SPDX-resolvable",
                        FAIL, "LICENSE_MISSING",
                        "no LICENSE / COPYING file anywhere in the scanned tree",
                        counts, []), None, root_license)


# --------------------------------------------------------------------------- #
# check 2: NOTICE_PRESENT
# --------------------------------------------------------------------------- #
NOTICE_REQUIRED_SPDX = {"Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "MPL-2.0"}


def check_notice(tree: str, files, spdx, root_license) -> CheckResult:
    notices = [f for f in files
               if os.path.basename(f).lower() in ("notice", "notice.txt", "notice.md")]
    counts = {"notice_files": len(notices), "licence_basis_spdx": spdx or "",
              "licence_files_at_root": len(root_license)}
    if notices:
        return CheckResult("NOTICE_PRESENT", "NOTICE file present where the licence basis requires one",
                           PASS, "NOTICE_PRESENT", f"{len(notices)} NOTICE file(s) found",
                           counts, notices[:10])
    if not root_license and not spdx:
        return CheckResult("NOTICE_PRESENT", "NOTICE file present where the licence basis requires one",
                           HOLD, "NOTICE_BASIS_ABSENT",
                           "no licence basis in tree: notice obligation cannot be judged",
                           counts, [])
    if spdx and spdx not in NOTICE_REQUIRED_SPDX:
        return CheckResult("NOTICE_PRESENT", "NOTICE file present where the licence basis requires one",
                           HOLD, "NOTICE_NOT_MANDATED_BY_SPDX",
                           f"SPDX {spdx} does not mandate a NOTICE file; none found",
                           counts, [])
    return CheckResult("NOTICE_PRESENT", "NOTICE file present where the licence basis requires one",
                       FAIL, "NOTICE_MISSING",
                       f"licence basis {spdx or 'present'} requires attribution but no NOTICE file exists",
                       counts, [])


# --------------------------------------------------------------------------- #
# check 3 + 4: CycloneDX SBOM
# --------------------------------------------------------------------------- #
def _looks_like_sbom(rel: str) -> bool:
    base = os.path.basename(rel).lower()
    return (base.endswith(".cdx.json") or base.startswith("sbom") and base.endswith(".json")
            or base in ("bom.json", "bom.xml"))


def _component_name(comp) -> str:
    if not isinstance(comp, dict):
        return ""
    return str(comp.get("name", "") or "")


def check_sbom(tree: str, files) -> tuple:
    candidates = [f for f in files if _looks_like_sbom(f)]
    parsed, errors, structure_problems = [], [], []
    component_names = []

    for rel in candidates:
        path = os.path.join(tree, rel.replace("/", os.sep))
        text = read_text(path)
        if text is None:
            errors.append({"file": rel, "error": "UNREADABLE_OR_BINARY"})
            continue
        try:
            doc = json.loads(text)
        except Exception as exc:
            errors.append({"file": rel, "error": "JSON_INVALID", "detail": type(exc).__name__})
            continue
        if not isinstance(doc, dict):
            structure_problems.append({"file": rel, "problem": "TOP_LEVEL_NOT_OBJECT"})
            continue
        problems = []
        if doc.get("bomFormat") != "CycloneDX":
            problems.append("BOMFORMAT_NOT_CYCLONEDX")
        spec = doc.get("specVersion")
        if not isinstance(spec, str) or not re.match(r"^\d+\.\d+$", spec):
            problems.append("SPECVERSION_MISSING_OR_INVALID")
        comps = doc.get("components")
        if not isinstance(comps, list):
            problems.append("COMPONENTS_NOT_ARRAY")
            comps = []
        for comp in comps:
            if not _component_name(comp):
                problems.append("COMPONENT_WITHOUT_NAME")
                break
        for comp in comps:
            if isinstance(comp, dict) and not (comp.get("version") or comp.get("purl")):
                problems.append("COMPONENT_WITHOUT_VERSION_OR_PURL")
                break
        if problems:
            structure_problems.append({"file": rel, "problems": sorted(set(problems))})
            continue
        parsed.append(rel)
        component_names += [_component_name(c) for c in comps]

    counts = {"sbom_candidates": len(candidates), "sbom_parsed": len(parsed),
              "components": len(component_names), "parse_errors": len(errors),
              "structure_problems": len(structure_problems)}
    samples = parsed[:5] + [e["file"] for e in errors][:5]

    if not candidates:
        return (CheckResult("SBOM_PRESENT_AND_PARSABLE", "CycloneDX SBOM present and structurally valid",
                            FAIL, "SBOM_MISSING",
                            "no SBOM file (*.cdx.json / sbom*.json) found in the tree",
                            counts, []), [], counts)
    if not parsed:
        code = "SBOM_UNPARSABLE" if errors else "SBOM_SCHEMA_INVALID"
        return (CheckResult("SBOM_PRESENT_AND_PARSABLE", "CycloneDX SBOM present and structurally valid",
                            FAIL, code,
                            "SBOM candidate(s) found but none valid: JSON or CycloneDX structure failed",
                            counts, samples), [], counts)
    detail = f"{len(parsed)} SBOM file(s) valid, {len(component_names)} component(s)"
    if errors or structure_problems:
        detail += "; some candidates were rejected (see counts)"
    return (CheckResult("SBOM_PRESENT_AND_PARSABLE", "CycloneDX SBOM present and structurally valid",
                        PASS, "SBOM_PARSED", detail, counts, samples), component_names, counts)


def check_sbom_reconcile(sbom_verdict: str, component_names, runtime: dict, optional: dict,
                         manifest_count: int) -> CheckResult:
    """Reconcile the SBOM against the RUNTIME dependency set only.

    SCOPE DECISION (F2, W0 closeout -- do not silently undo):
    An SBOM enumerates the components a consumer of the package actually installs.
    A test/optional extra is, by definition, not part of that set unless installed,
    and its declared form is a constraint (">=1.2"), not a resolved version. Comparing
    extras against the SBOM therefore made every tree whose test harness needs
    pytest/build/wheel/setuptools/cryptography permanently red for a reason no
    packaging change could fix -- a checker defect, not a supply-chain defect.
    Extras are now reported in counts["optional_not_listed"] and never drive the
    verdict. The runtime comparison is NOT relaxed: a runtime dependency missing from
    the SBOM still fails, with its own code SBOM_COMPONENT_MISSING_RUNTIME, and a
    component the SBOM claims but no runtime manifest declares still fails with
    SBOM_COMPONENT_MISMATCH.
    """
    names = sorted({norm_name(n) for n in component_names if n})
    runtime_names = sorted({norm_name(n) for n in runtime})
    optional_names = sorted({norm_name(n) for n in optional} - set(runtime_names))
    counts = {
        "sbom_components": len(names),
        "runtime_dependencies": len(runtime_names),
        "declared_dependencies": len(runtime_names),
        "declared_optional_dependencies": len(optional_names),
        "sbom_only": 0,
        "missing_runtime_components": 0,
        "declared_only": 0,  # retained: always 0 now, extras are not "missing" by definition
        "optional_not_listed": len([n for n in optional_names if n not in names]),
        "optional_not_listed_names": [n for n in optional_names if n not in names],
    }

    if sbom_verdict != PASS:
        return CheckResult("SBOM_COMPONENT_RECONCILE", "SBOM components reconcile with declared manifests",
                           NA, "SBOM_NOT_AVAILABLE",
                           "no parsable SBOM: reconciliation cannot be evaluated", counts, [])
    if manifest_count == 0:
        return CheckResult("SBOM_COMPONENT_RECONCILE", "SBOM components reconcile with declared manifests",
                           HOLD, "DEPENDENCY_MANIFEST_MISSING",
                           "SBOM present but the tree declares no dependency manifest to reconcile against",
                           counts, names[:20])

    sbom_only = sorted(set(names) - set(runtime_names))
    missing_runtime = sorted(set(runtime_names) - set(names))
    counts["sbom_only"] = len(sbom_only)
    counts["missing_runtime_components"] = len(missing_runtime)
    extras_note = (f"; {counts['optional_not_listed']} optional/test extra(s) not listed in the SBOM "
                   f"(informational, not judged)")

    if sbom_only:
        samples = [f"sbom_only:{n}" for n in sbom_only[:15]]
        samples += [f"missing_runtime:{n}" for n in missing_runtime[:15]]
        return CheckResult("SBOM_COMPONENT_RECONCILE", "SBOM components reconcile with declared manifests",
                           FAIL, "SBOM_COMPONENT_MISMATCH",
                           f"{len(sbom_only)} component(s) in SBOM only, "
                           f"{len(missing_runtime)} runtime dependency(ies) missing from SBOM"
                           + extras_note,
                           counts, samples)
    if missing_runtime:
        samples = [f"missing_runtime:{n}" for n in missing_runtime[:15]]
        return CheckResult("SBOM_COMPONENT_RECONCILE", "SBOM components reconcile with declared manifests",
                           FAIL, "SBOM_COMPONENT_MISSING_RUNTIME",
                           f"{len(missing_runtime)} declared runtime dependency(ies) absent from the SBOM"
                           + extras_note,
                           counts, samples)
    return CheckResult("SBOM_COMPONENT_RECONCILE", "SBOM components reconcile with declared manifests",
                       PASS, "SBOM_COMPONENTS_RECONCILED",
                       f"{len(runtime_names)} runtime dependency(ies) all declared and vice versa"
                       + extras_note,
                       counts, names[:20] + [f"optional_not_listed:{n}"
                                             for n in counts["optional_not_listed_names"][:10]])


# --------------------------------------------------------------------------- #
# check 5: DEPENDENCY_DECLARED
# --------------------------------------------------------------------------- #
def python_imports(tree: str, files):
    """[(rel, lineno, top_level_module)] plus parse failures."""
    found, parse_errors = [], []
    for rel in files:
        if not rel.lower().endswith(".py"):
            continue
        path = os.path.join(tree, rel.replace("/", os.sep))
        text = read_text(path)
        if text is None:
            parse_errors.append({"file": rel, "error": "UNREADABLE"})
            continue
        try:
            tree_node = ast.parse(text, filename=rel)
        except SyntaxError as exc:
            parse_errors.append({"file": rel, "error": "SYNTAX_ERROR", "line": exc.lineno})
            continue
        for node in ast.walk(tree_node):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.append((rel, node.lineno, alias.name.split(".")[0]))
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    found.append((rel, node.lineno, node.module.split(".")[0]))
    return found, parse_errors


def local_module_names(tree: str, files) -> set:
    local = set()
    for rel in files:
        if not rel.lower().endswith(".py"):
            continue
        parts = rel.split("/")
        stem = parts[-1][:-3]
        local.add(stem)
        if parts[0] in ("src", "lib") and len(parts) > 2:
            local.add(parts[1])
        elif len(parts) > 1:
            local.add(parts[0])
    return local


def vendored_source_packages(tree: str, files) -> set:
    """Directory names that hold .py sources inside the tree.

    A vendored mirror (e.g. repo_sources/<repo>/src/<pkg>/) is first-party to the
    tree that ships it, so its package name must not be reported as an
    undeclared third-party distribution.
    """
    names = set()
    for rel in files:
        if not rel.lower().endswith(".py"):
            continue
        parts = rel.split("/")[:-1]
        for part in parts:
            if part in ("src", "lib", "tests", "test", "scripts", "tools", ".github"):
                continue
            names.add(part)
    return names


def check_dependency_declared(tree: str, files, declared: dict, manifest_count: int) -> CheckResult:
    imports, parse_errors = python_imports(tree, files)
    py_files = [f for f in files if f.lower().endswith(".py")]
    local = local_module_names(tree, files)
    stdlib = set(getattr(sys, "stdlib_module_names", set()))
    builtins = set(sys.builtin_module_names)
    allowed = set(stdlib) | builtins | local | {"__future__"}

    declared_modules = set(declared.keys())
    for dist in declared.keys():
        if dist in DIST_TO_MODULE:
            declared_modules.add(DIST_TO_MODULE[dist].replace("_", "-"))
    declared_modules = {m.replace("_", "-") for m in declared_modules}

    third_party, audit, vendored = set(), {}, set()
    vendored_dirs = vendored_source_packages(tree, files)
    for rel, lineno, mod in imports:
        key = mod.replace("_", "-")
        if mod in allowed or key in allowed:
            continue
        if mod in vendored_dirs:
            vendored.add(mod)
            continue
        third_party.add(mod)
        audit.setdefault(mod, []).append(f"{rel}:{lineno}")

    # "undeclared" is only a decidable question once a manifest exists.
    undeclared = {m: locs for m, locs in audit.items() if m.replace("_", "-") not in declared_modules}

    counts = {
        "python_files": len(py_files),
        "import_statements_scanned": len(imports),
        "distinct_third_party_modules": len(third_party),
        "vendored_in_tree_modules": len(vendored),
        "undeclared_modules": len(undeclared) if manifest_count else 0,
        "declared_dependencies": len(declared),
        "parse_errors": len(parse_errors),
    }

    if not py_files:
        return CheckResult("DEPENDENCY_DECLARED", "Every third-party import is declared in a manifest",
                           NA, "NO_PYTHON_SOURCES", "no .py file in the scanned tree", counts, [])
    if manifest_count == 0:
        return CheckResult("DEPENDENCY_DECLARED", "Every third-party import is declared in a manifest",
                           HOLD, "DEPENDENCY_MANIFEST_MISSING",
                           f"{len(third_party)} third-party module(s) imported but the tree ships no dependency manifest",
                           counts, sorted(third_party)[:20])
    if undeclared:
        samples = []
        for mod in sorted(undeclared):
            for loc in undeclared[mod][:3]:
                samples.append(f"{mod} @ {loc}")
        samples = samples[:20]
        return CheckResult("DEPENDENCY_DECLARED", "Every third-party import is declared in a manifest",
                           FAIL, "UNDECLARED_DEPENDENCY",
                           f"{len(undeclared)} module(s) imported but absent from every manifest",
                           counts, samples)
    return CheckResult("DEPENDENCY_DECLARED", "Every third-party import is declared in a manifest",
                       PASS, "DEPENDENCIES_DECLARED",
                       f"{len(third_party)} third-party module(s), all declared", counts,
                       sorted(third_party)[:20])


# --------------------------------------------------------------------------- #
# check 6: SECRET_PATTERN_SCAN
# --------------------------------------------------------------------------- #
SECRET_PATTERNS = (
    ("github_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("openai_style_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
)


def mask_secret(value: str, kind: str) -> str:
    """Return a masked rendering: at most 4 leading characters, never the secret body."""
    if kind == "private_key_block":
        return "----***PRIVATE_KEY_HEADER"
    head = value[:4]
    return f"{head}***MASKED(len={len(value)})"


def check_secret_scan(tree: str, files) -> CheckResult:
    hits, per_pattern, files_scanned, bytes_scanned = [], {}, 0, 0
    for rel in files:
        path = os.path.join(tree, rel.replace("/", os.sep))
        text = read_text(path)
        if text is None:
            continue
        files_scanned += 1
        bytes_scanned += len(text.encode("utf-8", errors="replace"))
        for kind, rx in SECRET_PATTERNS:
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                hits.append({
                    "kind": kind,
                    "location": f"{rel}:{line}",
                    "masked": mask_secret(m.group(0), kind),
                })
                per_pattern[kind] = per_pattern.get(kind, 0) + 1

    counts = {"files_scanned": files_scanned, "bytes_scanned": bytes_scanned,
              "matches": len(hits), "patterns_evaluated": len(SECRET_PATTERNS),
              "per_pattern": per_pattern}
    samples = [f"{h['location']} {h['kind']} {h['masked']}" for h in hits[:20]]

    if hits:
        return CheckResult("SECRET_PATTERN_SCAN", "No credential-shaped token in tree text files",
                           FAIL, "SECRET_PATTERN_FOUND",
                           f"{len(hits)} match(es) across {files_scanned} scanned text file(s); values masked",
                           counts, samples)
    if files_scanned == 0:
        return CheckResult("SECRET_PATTERN_SCAN", "No credential-shaped token in tree text files",
                           NA, "NO_READABLE_TEXT_FILES", "no decodable text file in tree", counts, [])
    return CheckResult("SECRET_PATTERN_SCAN", "No credential-shaped token in tree text files",
                       PASS, "NO_SECRET_PATTERN",
                       f"{len(SECRET_PATTERNS)} patterns over {files_scanned} text file(s), 0 matches",
                       counts, [])


# --------------------------------------------------------------------------- #
# check 7: CI_ENTRY_PRESENT
# --------------------------------------------------------------------------- #
WORKFLOW_RE = re.compile(r"^\.github/workflows/[^/]+\.ya?ml$", re.I)
OTHER_CI = {".gitlab-ci.yml", "azure-pipelines.yml", "jenkinsfile", ".circleci/config.yml",
            ".buildkite/pipeline.yml", "bitbucket-pipelines.yml"}
RERUN_CMD_RE = re.compile(
    r"^\s*(?:\$ |>\s*)?(?:python[0-9.]*|py)\s+(?:-m\s+)?"
    r"(?:unittest|pytest|supply_chain_gate\.py|AUTHOR_[A-Z_]+\.py)\b",
    re.MULTILINE,
)


def check_ci_entry(tree: str, files) -> CheckResult:
    workflows = [f for f in files if WORKFLOW_RE.match(f)]
    others = [f for f in files if f.lower() in OTHER_CI]
    documented = []
    for rel in files:
        if not rel.lower().endswith((".md", ".rst", ".txt")):
            continue
        text = read_text(os.path.join(tree, rel.replace("/", os.sep))) or ""
        m = RERUN_CMD_RE.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            cmd = m.group(0).strip().lstrip("$ ").strip()
            documented.append({"file": rel, "line": line, "command": cmd[:120]})

    counts = {"workflow_files": len(workflows), "other_ci_files": len(others),
              "documented_commands": len(documented)}
    samples = (workflows + others)[:10] + [f"doc:{d['file']}:{d['line']} `{d['command']}`" for d in documented[:5]]

    if workflows or others:
        return CheckResult("CI_ENTRY_PRESENT", "CI entry point exists (workflow file or documented command)",
                           PASS, "CI_ENTRY_WORKFLOW_PRESENT",
                           f"{len(workflows)} workflow file(s), {len(others)} other CI config(s)",
                           counts, samples)
    if documented:
        return CheckResult("CI_ENTRY_PRESENT", "CI entry point exists (workflow file or documented command)",
                           PASS, "CI_ENTRY_DOCUMENTED_COMMAND",
                           f"no CI config; {len(documented)} documented re-runnable command(s) found",
                           counts, samples)
    return CheckResult("CI_ENTRY_PRESENT", "CI entry point exists (workflow file or documented command)",
                       FAIL, "CI_ENTRY_MISSING",
                       "no .github/workflows config and no documented re-runnable command",
                       counts, [])


# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #
def run_gate(tree: str, mode: str = "author") -> dict:
    tree = os.path.abspath(tree)
    if not os.path.isdir(tree):
        raise FileNotFoundError(f"tree is not a directory: {tree}")
    if mode != "author":
        raise ValueError(f"unsupported mode {mode!r}; this build supports 'author' only")

    dirs, files = walk_tree(tree)
    manifests = discover_manifests(tree, files)
    decl_info = declared_dependencies(tree, manifests)
    declared = decl_info["declared"]

    results = []
    lic, spdx, root_license = check_license(tree, dirs, files, manifests)
    results.append(lic)
    results.append(check_notice(tree, files, spdx, root_license))

    sbom, components, sbom_counts = check_sbom(tree, files)
    results.append(sbom)
    results.append(check_sbom_reconcile(sbom.verdict, components, decl_info["runtime"],
                                        decl_info["optional"], len(manifests)))
    results.append(check_dependency_declared(tree, files, declared, len(manifests)))
    results.append(check_secret_scan(tree, files))
    results.append(check_ci_entry(tree, files))

    summary = {v: 0 for v in VERDICTS}
    for r in results:
        summary[r.verdict] += 1
    fail_codes = [r.code for r in results if r.verdict == FAIL]

    total_bytes = 0
    digest = hashlib.sha256()
    for rel in files:
        full = os.path.join(tree, rel.replace("/", os.sep))
        try:
            size = os.path.getsize(full)
            total_bytes += size
            digest.update(rel.encode("utf-8"))
            digest.update(b"\x00")
            digest.update(str(size).encode("ascii"))
            digest.update(b"\x00")
            digest.update(sha256_file(full).encode("ascii"))
            digest.update(b"\n")
        except OSError:
            continue

    exit_code = 1 if fail_codes else 0

    return {
        "schema": SCHEMA,
        "gate_id": GATE_ID,
        "gate_version": GATE_VERSION,
        "mode": mode,
        "generated_at_taipei": datetime.now(TAIPEI).isoformat(timespec="seconds"),
        "tree": tree,
        "claim_ceiling": CLAIM_CEILING,
        "wp19_done": False,
        "trace_closure": False,
        "scanned": {
            "files_total": len(files),
            "dirs_total": len(dirs),
            "bytes_total": total_bytes,
            "tree_digest_sha256": digest.hexdigest(),
            "tree_digest_scope": "sha256 over sorted lines 'rel_path\\\\0size\\\\0sha256(file)'",
            "python_files": len([f for f in files if f.lower().endswith(".py")]),
            "dependency_manifests": [m[0] for m in manifests],
            "manifest_parse_errors": decl_info["errors"],
            "declared_dependency_count": len(declared),
        },
        "checks": [r.as_dict() for r in results],
        "summary": {
            "PASS": summary[PASS],
            "FAIL": summary[FAIL],
            "HOLD": summary[HOLD],
            "NOT_APPLICABLE": summary[NA],
            "fail_codes": fail_codes,
            "checks_total": len(results),
        },
        "exit_code": exit_code,
        "limits": [
            "author-local static gate; not an independent or protected checker",
            "no network, no package install, no SBOM signature or vulnerability database",
            "SBOM check validates CycloneDX structure only, not provenance or attestation",
            "secret scan is regex-based over decodable text files; absence of a match is not proof of absence",
        ],
    }


def write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def render_summary(payload: dict) -> str:
    lines = [
        f"{GATE_ID} supply-chain gate  mode={payload['mode']}  ceiling={payload['claim_ceiling']}",
        f"tree: {payload['tree']}",
        f"scanned: {payload['scanned']['files_total']} file(s), {payload['scanned']['bytes_total']} bytes",
        "-" * 78,
    ]
    for chk in payload["checks"]:
        lines.append(f"{chk['verdict']:<15} {chk['check_id']:<28} {chk['code']}")
        if chk["detail"]:
            lines.append(f"{'':<15} {chk['detail']}")
        for s in chk["samples"][:5]:
            lines.append(f"{'':<17}- {s}")
    s = payload["summary"]
    lines.append("-" * 78)
    lines.append(f"PASS={s['PASS']} FAIL={s['FAIL']} HOLD={s['HOLD']} NOT_APPLICABLE={s['NOT_APPLICABLE']}"
                 f"  exit={payload['exit_code']}")
    if s["fail_codes"]:
        lines.append("fail codes: " + ", ".join(s["fail_codes"]))
    lines.append(f"claim_ceiling={payload['claim_ceiling']} wp19_done=false trace_closure=false")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="supply_chain_gate.py",
        description="WP-FHS-19 author-local supply-chain & compliance gate (stdlib only).")
    ap.add_argument("--tree", required=True, help="directory to scan (read-only)")
    ap.add_argument("--out", required=True, help="path of the typed JSON result to write")
    ap.add_argument("--mode", default="author", choices=["author"],
                    help="gate mode; only 'author' exists in this build")
    ap.add_argument("--quiet", action="store_true", help="suppress the human-readable summary")
    args = ap.parse_args(argv)

    try:
        payload = run_gate(args.tree, args.mode)
    except FileNotFoundError as exc:
        print(f"supply_chain_gate: ERROR {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"supply_chain_gate: ERROR {exc}", file=sys.stderr)
        return 2

    write_json(args.out, payload)
    if not args.quiet:
        print(render_summary(payload))
    return payload["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
