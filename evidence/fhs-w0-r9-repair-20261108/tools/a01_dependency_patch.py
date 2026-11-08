#!/usr/bin/env python3
"""A-01 repair: the one dependency that is genuinely undeclared, with a patch that applies.

What the previous round said, and what is true
----------------------------------------------
The r7 addendum (A-01) asserted that HG-KSEOS "imports the third-party module cryptography in three
source modules while pyproject declares dependencies = []". Measured on this machine:

  pyproject.toml:6   dependencies = ["cryptography>=42"]        -> cryptography IS declared
  src/hg_kseos/fhs/issuer_binding.py                            -> does not exist
  grep -rn 'import yaml' src                                     -> lane_policy.py:71 only

So the named module and the named file are both wrong. The real, narrower defect is `yaml`: imported
inside `_yaml_load_unique`, guarded by a try/except that returns None, and declared nowhere. A fresh
install therefore loses duplicate-key rejection silently instead of failing loudly.

The repair is to declare it as an optional extra, which is what the code already assumes, and to add
a check that refuses a future import with no declaration.

This script does not modify HG-KSEOS. It writes a candidate file, a patch, and the before/after
verdicts into the round directory.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
REPO = r"C:/Projects/Agent_Workspace/HG-KSEOS"
OUT = r"C:/Projects/Agent_Workspace/FHS_W0_R9_REPAIR_20261108/out/A01_DEPENDENCY_PATCH"

BLOCK = (
    "[project.optional-dependencies]\n"
    'yaml = ["PyYAML>=6"]  # imported lazily by hg_kseos.lane_policy._yaml_load_unique; absence degrades to None\n'
)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


DIST_TO_IMPORT = {"pyyaml": "yaml", "pillow": "PIL", "beautifulsoup4": "bs4", "python-dateutil": "dateutil"}


def local_module_names(repo: str) -> set[str]:
    """First-party modules importable because the repo puts its own directories on sys.path."""
    names: set[str] = set()
    for sub in ("tools", os.path.join("src", "hg_kseos")):
        d = os.path.join(repo, sub)
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".py"):
                    names.add(fn[:-3])
    return names


def declared_names(pyproject_bytes: bytes) -> dict:
    d = tomllib.loads(pyproject_bytes.decode("utf-8"))
    proj = d.get("project", {})
    run = []
    for spec in proj.get("dependencies", []) or []:
        run.append(re.split(r"[<>=!~\[; ]", spec.strip(), maxsplit=1)[0].lower())
    opt = {}
    for extra, specs in (proj.get("optional-dependencies") or {}).items():
        opt[extra] = [re.split(r"[<>=!~\[; ]", s.strip(), maxsplit=1)[0].lower() for s in specs]
    flat = set(run) | {n for v in opt.values() for n in v}
    # a declared distribution whose import name differs still covers that import
    flat |= {DIST_TO_IMPORT[d] for d in list(flat) if d in DIST_TO_IMPORT}
    return {"runtime": run, "optional": opt, "flat": sorted(flat)}


def imported_modules(repo: str) -> dict:
    """Top-level modules imported from the package source, with the guarded-ness of each site."""
    root = os.path.join(repo, "src")
    found: dict[str, list[dict]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, repo).replace("\\", "/")
            lines = open(p, "r", encoding="utf-8", errors="replace").read().splitlines()
            indent_stack = []
            for i, line in enumerate(lines, 1):
                m = re.match(r"^(\s*)(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)", line)
                if not m:
                    continue
                mod = m.group(2)
                if mod in sys.stdlib_module_names or mod == "hg_kseos":
                    continue
                found.setdefault(mod, []).append({
                    "path_rel": rel, "line": i,
                    "inside_function": bool(m.group(1)),
                    "text": line.strip()[:90],
                })
    return found


def coverage(repo: str, pyproject_bytes: bytes) -> dict:
    decl = declared_names(pyproject_bytes)
    imports = imported_modules(repo)
    local = local_module_names(repo)
    imports = {m: v for m, v in imports.items() if m not in local}
    undeclared = {m: v for m, v in imports.items() if m.lower() not in decl["flat"]}
    return {
        "declared_runtime": decl["runtime"],
        "declared_optional": decl["optional"],
        "third_party_imported": sorted(imports),
        "local_modules_excluded": sorted(local),
        "undeclared": sorted(undeclared),
        "sites": undeclared,
        "verdict": "DECLARED_COVERS_IMPORTS" if not undeclared else "UNDECLARED_DEPENDENCY",
    }


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    pp = os.path.join(REPO, "pyproject.toml")
    raw = open(pp, "rb").read()
    crlf = b"\r\n" in raw
    nl = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")

    # insert the extra after the runtime dependencies line inside [project]
    lines = text.split(nl)
    idx = next(i for i, ln in enumerate(lines) if ln.startswith("dependencies"))
    block_lines = BLOCK.rstrip("\n").split("\n")
    candidate_lines = lines[: idx + 1] + [""] + block_lines + lines[idx + 1:]
    candidate = nl.join(candidate_lines)
    cand_bytes = candidate.encode("utf-8")

    before = coverage(REPO, raw)
    cand_path = os.path.join(OUT, "pyproject.toml.candidate")
    open(cand_path, "wb").write(cand_bytes)
    after = coverage(REPO, cand_bytes)

    # unified diff with the file's own terminator on every line
    a = [ln + nl for ln in lines]
    b = [ln + nl for ln in candidate_lines]
    diff = "".join(difflib.unified_diff(a, b, fromfile="a/pyproject.toml", tofile="b/pyproject.toml", n=3))
    patch_path = os.path.join(OUT, "pyproject.toml.patch")
    open(patch_path, "w", encoding="utf-8", newline="").write(diff)

    # prove it applies, in a throwaway copy, with --binary
    applied_ok = None
    applied_sha = None
    apply_note = ""
    tmp = tempfile.mkdtemp(prefix="a01-")
    try:
        dst = os.path.join(tmp, "pyproject.toml")
        shutil.copy2(pp, dst)
        proc = subprocess.run(["patch", "--binary", "-p1", "--dry-run", "-i", patch_path],
                              cwd=tmp, capture_output=True, text=True)
        if proc.returncode != 0:
            apply_note = f"dry-run rc={proc.returncode} {proc.stdout.strip()} {proc.stderr.strip()}"
        else:
            proc2 = subprocess.run(["patch", "--binary", "-p1", "-i", patch_path],
                                   cwd=tmp, capture_output=True, text=True)
            applied = open(dst, "rb").read()
            applied_ok = applied == cand_bytes
            applied_sha = sha(applied)
            apply_note = f"apply rc={proc2.returncode}; applied_equals_candidate={applied_ok}"
    except FileNotFoundError:
        apply_note = "patch binary not on PATH; diff written but not exercised"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    result = {
        "schema": "FHS.W0.A01DependencyPatch/1",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "tool_sha256": sha(open(__file__, "rb").read()),
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "repo": REPO,
        "pyproject_sha256_before": sha(raw),
        "pyproject_bytes_before": len(raw),
        "eol": "CRLF" if crlf else "LF",
        "corrections_of_prior_round": [
            {
                "prior_claim": "HG-KSEOS imports cryptography in three source modules while pyproject declares dependencies = []",
                "measured": {
                    "pyproject_dependencies_line": "dependencies = [\"cryptography>=42\"]",
                    "issuer_binding_exists": os.path.isfile(os.path.join(REPO, "src/hg_kseos/fhs/issuer_binding.py")),
                    "cryptography_declared": "cryptography" in coverage(REPO, raw)["declared_runtime"],
                },
                "verdict": "PRIOR_CLAIM_FALSE_IN_BOTH_PARTS",
                "consequence": "the supply-chain finding survives, but against a different module and a narrower shape",
            }
        ],
        "before": before,
        "after": after,
        "patch": {
            "path": patch_path.replace("\\", "/"),
            "inserted_lines": block_lines,
            "dry_run_and_apply": apply_note,
            "applied_equals_candidate": applied_ok,
            "applied_sha256": applied_sha,
            "candidate_path": cand_path.replace("\\", "/"),
            "candidate_sha256": sha(cand_bytes),
        },
        "not_applied_to_repo": True,
        "why_not_applied": "HG-KSEOS is the native control source export; a packaging change there is the owner's write, and the repo has no CI to verify it. The patch is delivered validated and unapplied.",
        "not_claimed": ["UNDECLARED_DEPENDENCY_CLOSED_IN_REPO", "OWNER_ACCEPTANCE"],
    }
    with open(os.path.join(OUT, "RESULT.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print(f"before={before['verdict']} undeclared={before['undeclared']} runtime={before['declared_runtime']}")
    print(f"after ={after['verdict']} undeclared={after['undeclared']} optional={after['declared_optional']}")
    print(f"patch: {apply_note}")
    for mod, sites in before["sites"].items():
        for s in sites[:4]:
            print(f"  {mod}: {s['path_rel']}:{s['line']} inside_function={s['inside_function']}  {s['text']}")
    return 0 if (before["verdict"] == "UNDECLARED_DEPENDENCY" and after["verdict"] == "DECLARED_COVERS_IMPORTS") else 1


if __name__ == "__main__":
    sys.exit(main())
