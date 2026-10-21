#!/usr/bin/env python3
"""Derive the R5 contract from the R4 contract and compile it with the canonical compiler.

R4 already passed lint/activation/acceptance/compile. R5 does not re-author the contract: it
inherits that shape and changes only what round 5 changes — the task identity, a narrower write
set (the uninstall-boundary repair plus round evidence), and one new acceptance edge whose
negative fixtures are exactly the R5 finding's escape shapes.

Nothing is relaxed to obtain a pass. If the compiler rejects the result, the contract is fixed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Projects\Agent_Workspace\SBL")
COMPILER = Path(
    r"C:\Projects\Agent_Workspace\知識庫\工程基座\construction-acceptance-prompt-compiler"
    r"\construction-acceptance-prompt-compiler\scripts\prompt_contract_compiler.py"
)
SRC = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R4.json"
OUT = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R5.json"
OUTDIR = REPO / "contracts" / "compiled-r5"
PY = sys.executable

NEW_EDGES = (
    {
        "acceptance_id": "ACC-R5_UNINSTALL_BOUNDARY",
        "subject_id": "SBL_HARNESS_UNINSTALL_BOUNDARY",
        "subject_type": "CAPABILITY",
        "source_locators": [
            "SBL_PIPD-LS-PKG_DOC-05#C28",
            "SBL_PIPD-LS-PKG_DOC-07#C27",
            "SBL_PIPD-LS-PKG_DOC-12#C43",
        ],
        "runtime_required": True,
        "required_depth": "L3_INTEGRATION_RUNTIME",
        "positive_fixture": (
            "SBL_HARNESS_UNINSTALL_BOUNDARY: a genuine install can be doctor'd and uninstalled, "
            "leaving no residue, and every file whose digest the manifest declares is unchanged "
            "before removal"
        ),
        "negative_fixture": (
            "SBL_HARNESS_UNINSTALL_BOUNDARY: a tampered MANIFEST.json whose files key contains "
            "'../outside.txt', an absolute path, a symlink escaping the install root, or a key "
            "outside the installer's fixed file allowlist is REFUSED with a typed error and the "
            "external sentinel bytes are byte-identical afterwards"
        ),
        "recovery_fixture": (
            "SBL_HARNESS_UNINSTALL_BOUNDARY: after a refused uninstall the adapter directory, the "
            "manifest and the external sentinel are all still present, so the operator can inspect "
            "and re-run; no partial deletion is left behind"
        ),
        "raw_evidence_required": True,
        "independent_checker_required": True,
        "terminal_states": ["INDEPENDENT_CASE_PASS"],
    },
)


def main() -> int:
    contract = json.loads(SRC.read_text(encoding="utf-8"))
    contract["task_id"] = "SBL-FULL-DOC00-13-R5-20261021"

    changeset = contract["changeset"]
    changeset["class"] = "CONTINUATION"
    changeset["baseline_verified"] = True
    changeset["affected_domains"] = ["sbl_harness", "tests", "governance_evidence", "contracts"]
    changeset["affected_files"] = [
        "sbl_harness/__init__.py",
        "tests/test_sbl_harness.py",
        "sbl_core/errors.py",
        "contracts/SBL_C0_C9_CONTRACT-R5.json",
        "openspec/changes/sbl-v01-candidate-build/R5_DELTA.md",
    ]
    changeset["must_not_reopen"] = [
        "foundation main merge",
        "foundation prerelease v0.1.0-foundation-preview",
        "M4-LITE owner procedural receipt",
        "441/149/38 frozen ledgers",
        "c3-v2 plugin schema / package-data / stack / wheel work",
        "sbl_core m01..m06 module logic",
    ]

    existing = {row["acceptance_id"] for row in contract["acceptance"]}
    for edge in NEW_EDGES:
        if edge["acceptance_id"] in existing:
            continue
        row = json.loads(json.dumps(edge))
        row["raw_evidence_required"] = True
        row["independent_checker_required"] = True
        contract["acceptance"].append(row)

    OUT.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name} ({len(contract['acceptance'])} acceptance edges)")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    steps = [
        ("lint", [PY, str(COMPILER), "lint", str(OUT)]),
        ("activation", [PY, str(COMPILER), "activation", str(OUT)]),
        ("acceptance", [PY, str(COMPILER), "acceptance", str(OUT)]),
        ("compile", [PY, str(COMPILER), "compile", str(OUT), "--out-dir", str(OUTDIR)]),
    ]
    receipts = []
    rc_total = 0
    for name, argv in steps:
        proc = subprocess.run(argv, capture_output=True, text=True)
        receipts.append(
            {"stage": name, "rc": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]}
        )
        print(f"{name}: rc={proc.returncode}")
        if proc.returncode != 0:
            print(proc.stdout[-3000:], file=sys.stderr)
            print(proc.stderr[-2000:], file=sys.stderr)
            rc_total = proc.returncode
            break
    (OUTDIR / "COMPILER_RECEIPT.json").write_text(
        json.dumps({"contract": str(OUT), "compiler": str(COMPILER), "stages": receipts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return rc_total


if __name__ == "__main__":
    raise SystemExit(main())
