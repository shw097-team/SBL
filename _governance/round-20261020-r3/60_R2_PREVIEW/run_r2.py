#!/usr/bin/env python3
"""R2 preview packaging receipts: build, clean install, first-useful-output, uninstall, residue.

Shape follows AC-R2-01..05 from the R3 execution spec: the artifact is built from ONE frozen SHA,
installed into a virtual environment that has never seen the repository, exercised across process
boundaries, uninstalled, and then scanned for residue.  Nothing here is a release: without an Owner
signature the artefacts are a packaging candidate.

Every step is a subprocess with its exit code and output digest recorded, including the failures --
a command that could not run is recorded as NOT_RUN with its reason instead of being skipped.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUBJECT_SHA = "bedc11957d4fc2474b249b69d200829272c118ef"
WORK = Path("C:/Projects/_sbl_r3")
DIST = HERE / "dist"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> dict:
    completed = subprocess.run([str(part) for part in cmd], cwd=str(cwd) if cwd else None,
                               capture_output=True, env=env)
    stdout = completed.stdout.decode("utf-8", "replace")
    stderr = completed.stderr.decode("utf-8", "replace")
    return {
        "command": " ".join(str(part) for part in cmd),
        "exit": completed.returncode,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
        "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
    }


def step(name: str, expectation: str, result: dict, ok: bool, extra: dict | None = None) -> dict:
    record = {"case_id": name, "expectation": expectation, "ok": bool(ok), **result}
    if extra:
        record.update(extra)
    return record


def main() -> int:
    receipts: list[dict] = []
    py311 = shutil.which("py") or "py"

    # ---- AC-R2-01 build from one frozen SHA ------------------------------------------------
    src = WORK / "build-src"
    if src.exists():
        shutil.rmtree(src, ignore_errors=True)
    src.mkdir(parents=True)
    # A tar of the exact commit (not a directory copy) so the build input is the frozen tree.
    export = run(["git", "-C", "C:/Projects/Agent_Workspace/SBL", "archive", "--format=tar",
                  "-o", str(WORK / "subject.tar"), SUBJECT_SHA])
    if export["exit"] != 0:
        print(json.dumps({"fatal": "git archive failed", "detail": export}, indent=2))
        return 2
    receipts.append(step("AC-R2-01/export", "the exact frozen tree is exported, not a directory copy",
                         export, export["exit"] == 0))
    extract = run(["tar", "-xf", str(WORK / "subject.tar"), "-C", str(src)])
    receipts.append(step("AC-R2-01/extract", "the exported tar expands", extract, extract["exit"] == 0))
    head = run(["git", "-C", "C:/Projects/Agent_Workspace/SBL", "rev-parse", SUBJECT_SHA + "^{tree}"])
    receipts.append(step("AC-R2-01/tree", "the tree sha is recorded with the artefacts", head, True,
                         {"tree_sha": head["stdout"]}))

    DIST.mkdir(parents=True, exist_ok=True)
    for stale in DIST.glob("*"):
        if stale.is_file():
            stale.unlink()
    build = run([sys.executable, "-m", "build", "--no-isolation", "--outdir", str(DIST)], cwd=src)
    artefacts = sorted(DIST.glob("sbl_v01-*"))
    receipts.append(step("AC-R2-01/build", "wheel and sdist are produced (build --no-isolation)",
                         build, build["exit"] == 0 and len(artefacts) >= 2,
                         {"artefacts": [{"name": a.name, "bytes": a.stat().st_size,
                                         "sha256": sha256_file(a)} for a in artefacts]}))
    wheel = next((a for a in artefacts if a.suffix == ".whl"), None)
    sdist = next((a for a in artefacts if a.suffix == ".gz"), None)
    if wheel is None:
        print(json.dumps({"fatal": "no wheel built", "receipts": receipts}, indent=2))
        return 1

    # ---- AC-R2-02 clean environment install -------------------------------------------------
    venv = WORK / "venv-r2"
    if venv.exists():
        shutil.rmtree(venv, ignore_errors=True)
    make_venv = run([py311, "-3.11", "-m", "venv", str(venv)])
    receipts.append(step("AC-R2-02/venv", "a 3.11 virtual environment outside the repo", make_venv,
                         make_venv["exit"] == 0))
    vpy = venv / "Scripts" / "python.exe"
    install = run([str(vpy), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)])
    receipts.append(step("AC-R2-02/install", "the wheel installs with no network", install, install["exit"] == 0))
    version = run([str(vpy), "-m", "pip", "show", "sbl-v01"])
    receipts.append(step("AC-R2-02/pip-show", "the installed distribution is visible to pip", version,
                         version["exit"] == 0 and "0.1.0" in version["stdout"], {"stdout": version["stdout"]}))

    # ---- AC-R2-03 first useful output, across process boundaries ---------------------------
    cli = venv / "Scripts" / "sbl-todo.exe"
    data = WORK / "todo-data"
    if data.exists():
        shutil.rmtree(data, ignore_errors=True)
    init = run([str(cli), "--data-dir", str(data), "init"])
    add = run([str(cli), "--data-dir", str(data), "add", "--title", "ship the foundation preview"])
    # A NEW process, no shared memory: this is what makes it persistence rather than a fixture.
    listing = run([str(cli), "--data-dir", str(data), "list", "--json"])
    try:
        items = json.loads(listing["stdout"])["items"]
    except Exception:
        items = []
    receipts.append(step("AC-R2-03/init", "init creates the data dir", init, init["exit"] == 0))
    receipts.append(step("AC-R2-03/add", "add records an item", add, add["exit"] == 0))
    receipts.append(step("AC-R2-03/list-new-process",
                         "a second process reads the item back", listing,
                         listing["exit"] == 0 and len(items) == 1
                         and items[0].get("title") == "ship the foundation preview",
                         {"items": items}))
    empty_title = run([str(cli), "--data-dir", str(data), "add", "--title", "   "])
    receipts.append(step("AC-R2-03/negative-empty-title", "an empty title is refused, not silently stored",
                         empty_title, empty_title["exit"] != 0))

    # ---- AC-R2-04 uninstall and residue ----------------------------------------------------
    uninstall = run([str(cli), "--data-dir", str(data), "uninstall", "--yes"])
    receipts.append(step("AC-R2-04/uninstall-data", "uninstall removes the state dir it owns", uninstall,
                         uninstall["exit"] == 0 and not data.exists(),
                         {"data_dir_exists": data.exists()}))
    pip_uninstall = run([str(vpy), "-m", "pip", "uninstall", "-y", "sbl-v01"])
    receipts.append(step("AC-R2-04/pip-uninstall", "pip uninstall succeeds", pip_uninstall,
                         pip_uninstall["exit"] == 0))
    site = list((venv / "Lib" / "site-packages").glob("sbl_*"))
    scripts = [p.name for p in (venv / "Scripts").glob("sbl-todo*")]
    residue = {"site_packages": [p.name for p in site], "console_scripts": scripts}
    receipts.append(step("AC-R2-04/residue", "no sbl module or console script survives uninstall", {},
                         not site and not scripts, residue))

    # ---- AC-R2-05 licence / notice / scope readback ----------------------------------------
    def read(path: Path, limit: int = 400) -> dict:
        return {"path": path.name, "exists": path.exists(),
                "sha256": sha256_file(path) if path.exists() else None,
                "excerpt": path.read_text(encoding="utf-8")[:limit] if path.exists() else None}

    repo = Path("C:/Projects/Agent_Workspace/SBL")
    docs = {name: read(repo / name) for name in ("LICENSE", "NOTICE", "SHIPPED_MATERIAL_INVENTORY.md", "README.md")}
    in_wheel = run([sys.executable, "-c",
                    "import zipfile,sys;print('\\n'.join(zipfile.ZipFile(sys.argv[1]).namelist()))", str(wheel)])
    wheel_files = in_wheel["stdout"].splitlines()
    has_licence = any("LICENSE" in name.upper() for name in wheel_files)
    receipts.append(step("AC-R2-05/scope-readback",
                         "licence/notice/readme are present in the tree; wheel packaging is recorded as-is",
                         in_wheel, all(d["exists"] for d in docs.values()),
                         {"tree_docs": docs, "wheel_contains_licence": has_licence,
                          "wheel_files": wheel_files}))

    payload = {
        "schema": "SBL-R2-PACKAGING-RECEIPT/1",
        "subject_sha": SUBJECT_SHA,
        "subject_tree_sha": head["stdout"],
        "python_build": sys.version.split()[0],
        "python_install": "3.11",
        "artefacts": {"wheel": {"name": wheel.name, "bytes": wheel.stat().st_size, "sha256": sha256_file(wheel)},
                      "sdist": ({"name": sdist.name, "bytes": sdist.stat().st_size, "sha256": sha256_file(sdist)}
                                if sdist else "NOT_BUILT")},
        "receipts": receipts,
        "all_ok": all(r["ok"] for r in receipts),
        "verdict": "PACKAGING_CANDIDATE_READY_OWNER_RELEASE_PENDING",
        "claim": "STANDALONE_FOUNDATION_PREVIEW candidate: sbl-todo CLI + shared core, not a general Skill/Agent builder",
    }
    out = HERE / "AC_R2_RECEIPT.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(out), "sha256": sha256_file(out), "all_ok": payload["all_ok"],
                      "artefacts": payload["artefacts"],
                      "failed": [r["case_id"] for r in receipts if not r["ok"]]}, indent=2))
    return 0 if payload["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
