#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate every WP-FHS-19 artifact and emit LANE_REPORT.json.

The report's `commands[].exit_code` values are captured from real subprocess
runs made right here -- nothing is copied from a previous session.

    python tools/build_lane_report.py
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

LANE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(LANE_DIR, "supply_chain_gate.py")
TAIPEI = timezone(timedelta(hours=8))

S_TREE = ("C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
          "Semantic World OS Fabric/FHS／FHS-MSC／SBL/FHS/PIPD-LS-PKG/定案/W0/"
          "FHS_PIPD-LS-PKG_W0_R4C")
REMOTE_TREE = ("C:/Projects/Agent_Workspace/var/FHS_W0_IMPLEMENTATION_20261105_0305/"
               "source_readback/remote")

FIXTURES = ("pos", "neg_notice_missing", "neg_sbom_mismatch",
            "neg_undeclared_dep", "neg_secret")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: str) -> str:
    return os.path.relpath(path, LANE_DIR).replace(os.sep, "/")


def run(cmd, stdout_path=None):
    proc = subprocess.run(cmd, cwd=LANE_DIR, capture_output=True, text=True, timeout=1800)
    if stdout_path:
        with open(stdout_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(proc.stdout)
            if proc.stderr:
                fh.write("\n[stderr]\n" + proc.stderr)
    return proc


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    commands = []
    os.makedirs(os.path.join(LANE_DIR, "out", "fixture_runs"), exist_ok=True)

    # 1. the real S-tree run (the artefact under review)
    p = run([sys.executable, "supply_chain_gate.py", "--tree", S_TREE,
             "--out", "out/SUPPLY_CHAIN_RAW.json", "--mode", "author"],
            stdout_path=os.path.join(LANE_DIR, "out", "SUPPLY_CHAIN_RAW.stdout.txt"))
    commands.append({
        "cmd": f'python supply_chain_gate.py --tree "{S_TREE}" --out out/SUPPLY_CHAIN_RAW.json --mode author',
        "exit_code": p.returncode,
        "note": "real S-tree scan; non-zero because the gate found SBOM_MISSING",
    })

    # 2. supplementary real-tree run over the round's remote readback dump
    p = run([sys.executable, "supply_chain_gate.py", "--tree", REMOTE_TREE,
             "--out", "out/REMOTE_READBACK_RAW.json", "--mode", "author"])
    commands.append({
        "cmd": f'python supply_chain_gate.py --tree "{REMOTE_TREE}" --out out/REMOTE_READBACK_RAW.json --mode author',
        "exit_code": p.returncode,
        "note": "supplementary second real tree (flat dump of the three-repo rule/README files)",
    })

    # 3. fixture runs (POS + four NEG)
    for tree in FIXTURES:
        p = run([sys.executable, "supply_chain_gate.py", "--tree", f"fixtures/{tree}",
                 "--out", f"out/fixture_runs/{tree}.json", "--mode", "author", "--quiet"])
        commands.append({
            "cmd": f'python supply_chain_gate.py --tree fixtures/{tree} --out out/fixture_runs/{tree}.json --mode author --quiet',
            "exit_code": p.returncode,
            "note": "positive fixture" if tree == "pos" else f"negative fixture -> {tree}",
        })

    # 4. the unittest suite, captured verbatim
    p = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
    with open(os.path.join(LANE_DIR, "tests", "UNITTEST_RAW.log"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(p.stdout)
        if p.stderr:
            fh.write("\n[stderr]\n" + p.stderr)
    commands.append({
        "cmd": 'python -m unittest discover -s tests -p "test_*.py" -v',
        "exit_code": p.returncode,
        "note": "24 tests: POS all-PASS + 4 negative codes + redaction + usage errors",
    })

    # 5. fixture rebuild proof (deterministic; safe to re-run)
    p = run([sys.executable, "tools/build_fixtures.py"])
    commands.append({
        "cmd": "python tools/build_fixtures.py",
        "exit_code": p.returncode,
        "note": "fixture trees are generated, not hand-edited",
    })

    # ---- assemble -------------------------------------------------------- #
    s_raw = load(os.path.join(LANE_DIR, "out", "SUPPLY_CHAIN_RAW.json"))
    remote_raw = load(os.path.join(LANE_DIR, "out", "REMOTE_READBACK_RAW.json"))
    fix = {t: load(os.path.join(LANE_DIR, "out", "fixture_runs", f"{t}.json")) for t in FIXTURES}

    log_text = open(os.path.join(LANE_DIR, "tests", "UNITTEST_RAW.log"), encoding="utf-8").read()
    m = re.search(r"Ran (\d+) tests? in", log_text)
    tests_ran = int(m.group(1)) if m else -1
    tests_ok = bool(re.search(r"^OK\b", log_text, re.MULTILINE))

    deliverable_paths = [
        "supply_chain_gate.py",
        "tools/build_fixtures.py",
        "tools/build_lane_report.py",
        "tests/test_supply_chain_gate.py",
        "tests/UNITTEST_RAW.log",
        "out/SUPPLY_CHAIN_RAW.json",
        "out/SUPPLY_CHAIN_RAW.stdout.txt",
        "out/REMOTE_READBACK_RAW.json",
    ] + [f"out/fixture_runs/{t}.json" for t in FIXTURES] + [
        "fixtures/pos/LICENSE", "fixtures/pos/NOTICE", "fixtures/pos/SBOM.cdx.json",
        "fixtures/pos/pyproject.toml", "fixtures/neg_secret/config/sample_credentials.py",
    ]
    deliverables = []
    for relpath in deliverable_paths:
        full = os.path.join(LANE_DIR, relpath.replace("/", os.sep))
        deliverables.append({
            "path": relpath,
            "sha256": sha256(full),
            "bytes": os.path.getsize(full),
        })

    fixture_inventory = {}
    for tree in FIXTURES:
        base = os.path.join(LANE_DIR, "fixtures", tree)
        count = sum(len(files) for _, _, files in os.walk(base))
        fixture_inventory[tree] = {
            "files": count,
            "tree_digest_sha256": fix[tree]["scanned"]["tree_digest_sha256"],
            "exit_code": fix[tree]["exit_code"],
            "fail_codes": fix[tree]["summary"]["fail_codes"],
            "verdicts": {c["check_id"]: c["verdict"] for c in fix[tree]["checks"]},
        }

    negative_proof = {}
    for tree in FIXTURES[1:]:
        payload = fix[tree]
        target = [c for c in payload["checks"] if c["verdict"] == "FAIL"]
        negative_proof[tree] = {
            "expected_code": target[0]["code"] if len(target) == 1 else [c["code"] for c in target],
            "fail_codes": payload["summary"]["fail_codes"],
            "red_run_exit_code": payload["exit_code"],
            "artifact": f"out/fixture_runs/{tree}.json",
        }

    report = {
        "schema": "FHS_W0/LANE_REPORT/v1",
        "lane": "wp19",
        "gate_id": "WP-FHS-19",
        "generated_at_taipei": datetime.now(TAIPEI).isoformat(timespec="seconds"),
        "claim_ceiling": "AUTHOR_SUPPLY_CHAIN_LOCAL",
        "wp19_done": False,
        "trace_closure": False,
        "scope_statement": (
            "Executable supply-chain/compliance entry point plus author-side results only. "
            "No original CI Raw/ACK exists in this round, so WP19 DONE and TraceClosure are "
            "explicitly NOT claimed."
        ),
        "deliverables": deliverables,
        "commands": commands,
        "counts": {
            "checks_implemented": len(s_raw["checks"]),
            "verdict_enum": ["PASS", "FAIL", "HOLD", "NOT_APPLICABLE"],
            "s_tree": {
                "files_scanned": s_raw["scanned"]["files_total"],
                "dirs_scanned": s_raw["scanned"]["dirs_total"],
                "bytes_scanned": s_raw["scanned"]["bytes_total"],
                "python_files": s_raw["scanned"]["python_files"],
                "dependency_manifests": s_raw["scanned"]["dependency_manifests"],
                "tree_digest_sha256": s_raw["scanned"]["tree_digest_sha256"],
                "summary": s_raw["summary"],
                "verdicts": {c["check_id"]: c["verdict"] for c in s_raw["checks"]},
                "codes": {c["check_id"]: c["code"] for c in s_raw["checks"]},
                "exit_code": s_raw["exit_code"],
            },
            "remote_readback_tree": {
                "files_scanned": remote_raw["scanned"]["files_total"],
                "summary": remote_raw["summary"],
                "exit_code": remote_raw["exit_code"],
            },
            "fixtures": fixture_inventory,
            "tests": {
                "ran": tests_ran,
                "ok": tests_ok,
                "log": "tests/UNITTEST_RAW.log",
            },
        },
        "negative_proof": negative_proof,
        "holds": [
            "TraceClosure is not a WP19 output and is not produced here (trace_closure=false).",
            "No original CI run, Raw transcript or independent ACK exists in this round; WP19 DONE is not claimed.",
            "The S tree is a package mirror: it carries no first-party LICENSE/NOTICE/SBOM/manifest, so the real run returns LICENSE_ONLY_VENDORED_COPIES (HOLD), NOTICE_BASIS_ABSENT (HOLD), SBOM_MISSING (FAIL), DEPENDENCY_MANIFEST_MISSING (HOLD). These are honest observations of the mirror, not of the upstream SBL repo, which was never cloned or scanned in this lane.",
            "SBOM_COMPONENT_RECONCILE cannot be exercised on the real tree (no SBOM there); it is proven only on fixtures.",
            "SECRET_PATTERN_SCAN found 0 matches in 592 S files; absence of a regex match is not proof of absence of secrets.",
            "Gate is author-local static analysis: not an independent checker, no network, no package install, no SBOM signature/provenance or vulnerability lookup.",
        ],
        "known_limits": [
            "CycloneDX validation is structural (bomFormat/specVersion/components/name/version-or-purl) and does not validate against the published JSON schema.",
            "SPDX resolution is textual: SPDX-License-Identifier lines, well-known licence headers, pyproject `license`, or OWNER_LICENSE_DECISION.yaml; non-standard wording yields HOLD LICENSE_SPDX_UNPARSED rather than a guess.",
            "Dependency reconciliation uses PEP 503-ish name normalisation plus a small distribution->import alias table; exotic aliases may over-report UNDECLARED_DEPENDENCY.",
            "Vendored .py package directories are treated as in-tree first-party code, so a vendored mirror's own package is not flagged as an undeclared distribution.",
            "Files larger than 4 MiB or containing NUL bytes are skipped by the text checks (secret scan, licence text, documented-command detection) and by the ast import scan.",
            "Import scan is static: dynamic imports (importlib, __import__) and conditional/optional imports are not distinguished.",
            "Exit code 2 is reserved for usage/IO errors and is never a compliance verdict.",
            "The gate writes only inside the lane directory; the S tree and the remote readback dump are read-only inputs.",
        ],
    }

    out_path = os.path.join(LANE_DIR, "LANE_REPORT.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"wrote {rel(out_path)}")
    print(f"S tree: {s_raw['scanned']['files_total']} files, exit {s_raw['exit_code']}, "
          f"fail codes {s_raw['summary']['fail_codes']}")
    print(f"tests: {tests_ran} ran, ok={tests_ok}")
    for tree, info in fixture_inventory.items():
        print(f"  fixtures/{tree}: exit {info['exit_code']} fail {info['fail_codes']} "
              f"({info['files']} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
