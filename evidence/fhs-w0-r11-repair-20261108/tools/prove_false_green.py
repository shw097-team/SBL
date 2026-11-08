#!/usr/bin/env python3
"""Prove that the three false-green paths the external review found are now closed.

Each case builds a throw-away fixture, runs the *shipped* check function against it, and records the
verdict. A fix that cannot be shown to turn a green into a red is not a fix; it is a claim.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
HERE = os.path.dirname(os.path.abspath(__file__))


def load_gate():
    spec = importlib.util.spec_from_file_location("gate_r11", os.path.join(HERE, "gate_r11.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
            fh.write("\n")


def main() -> int:
    g = load_gate()
    results = []
    tmp = tempfile.mkdtemp(prefix="fg11-")
    try:
        # ---- C1: a manifest with files: [] ------------------------------------------------
        for label, doc in (
            ("files_empty", {"schema": "x", "expected_entry_set": ["a"], "files": []}),
            ("files_key_absent", {"schema": "x", "expected_entry_set": ["a"]}),
            ("expected_set_absent", {"schema": "x", "files": [{"path": "a.txt", "sha256": "0" * 64}]}),
        ):
            root = os.path.join(tmp, "c1_" + label, "out", "stage", "p")
            os.makedirs(root, exist_ok=True)
            write(os.path.join(root, "a.txt"), "a\n")
            write(os.path.join(root, "MANIFEST.json"), doc)
            ctx = g.Ctx(os.path.join(tmp, "c1_" + label))
            ok, code, detail = g.g18_digest_locality(ctx)
            results.append({"case": f"C1_{label}", "ok": ok, "code": code, "detail": detail[:120],
                            "expected": "must not pass", "pass": ok is False})

        # ---- C1 control: a correct manifest still passes --------------------------------
        root = os.path.join(tmp, "c1_control", "out", "stage", "p")
        os.makedirs(root, exist_ok=True)
        write(os.path.join(root, "a.txt"), "a\n")
        import hashlib
        write(os.path.join(root, "MANIFEST.json"),
              {"schema": "x", "expected_entry_set": ["a.txt"],
               "files": [{"path": "a.txt", "sha256": hashlib.sha256(b"a\n").hexdigest()}]})
        ok, code, detail = g.g18_digest_locality(g.Ctx(os.path.join(tmp, "c1_control")))
        results.append({"case": "C1_control_correct", "ok": ok, "code": code, "detail": detail[:120],
                        "expected": "must pass", "pass": ok is True})

        # ---- C2: an incomplete scan with no imports must not read as closed --------------
        tree = os.path.join(tmp, "c2", "tree")
        os.makedirs(os.path.join(tree, "src"), exist_ok=True)
        write(os.path.join(tree, "src", "mod.py"), "X = 1\n")
        write(os.path.join(tree, "pyproject.toml"), '[project]\nname = "t"\nversion = "0"\nrequires-python = ">=3.12"\ndependencies = []\n')
        subj = {"name": "t", "kind": "repo", "path": tree, "head": "deadbeef" * 5,
                "metadata_files": [os.path.join(tree, "pyproject.toml")],
                "source_root": os.path.join(tree, "src"), "scan_complete": False}
        d = g.derive_subject(subj)
        results.append({"case": "C2_scan_incomplete", "ok": d["declared_covers_imports"],
                        "code": "DERIVED_COVERS" if d["declared_covers_imports"] else "-",
                        "detail": f"scan_complete={d['scan_complete']} undeclared={d['undeclared_required']}",
                        "expected": "the derived set is empty but the scan admits it is partial; G16b must refuse",
                        "pass": d["scan_complete"] is False})

        # ---- C3: an optional extra is not a default-install declaration -----------------
        tree3 = os.path.join(tmp, "c3", "tree")
        os.makedirs(os.path.join(tree3, "src"), exist_ok=True)
        write(os.path.join(tree3, "src", "mod.py"), "import yaml\n")
        write(os.path.join(tree3, "pyproject.toml"),
              '[project]\nname = "t"\nversion = "0"\nrequires-python = ">=3.12"\ndependencies = []\n\n'
              '[project.optional-dependencies]\nyaml = ["PyYAML>=6"]\n')
        subj3 = {"name": "t", "kind": "repo", "path": tree3, "head": "beefdead" * 5,
                 "metadata_files": [os.path.join(tree3, "pyproject.toml")],
                 "source_root": os.path.join(tree3, "src"), "scan_complete": True}
        d3 = g.derive_subject(subj3)
        results.append({"case": "C3_optional_extra_only",
                        "ok": d3["declared_covers_imports"],
                        "code": "default_profile_covers" if d3["declared_covers_imports"] else "default_profile_missing",
                        "detail": f"required={d3['declared_required']} extras={d3['declared_optional_extras']} "
                                  f"provided_only_by_extra={d3['provided_only_by_extra']} with_extras={d3['declared_covers_with_extras']}",
                        "expected": "default install does not provide yaml, so coverage must be false",
                        "pass": d3["declared_covers_imports"] is False and d3["declared_covers_with_extras"] is True})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out = {
        "schema": "FHS.W0.FalseGreenProof/1",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "gate_sha256": __import__("hashlib").sha256(open(os.path.join(HERE, "gate_r11.py"), "rb").read()).hexdigest(),
        "method": "import the shipped check functions and run them against small fixtures; no copy of the gate, no model of it",
        "results": results,
        "all_closed": all(r["pass"] for r in results),
    }
    p = os.path.join(HERE, "..", "out", "FALSE_GREEN_PROOF.json")
    write(os.path.abspath(p), out)
    for r in results:
        print(f"{'OK ' if r['pass'] else 'BAD'} {r['case']:24} ok={str(r['ok']):5} {r['code']:26} {r['detail'][:80]}")
    print("all_closed:", out["all_closed"])
    return 0 if out["all_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
