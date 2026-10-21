#!/usr/bin/env python3
"""Derive the R4 C0–C9 contract from the R3C contract and compile it with the official compiler.

The contract is not authored freehand: it inherits the R3C structure (which already passed lint,
activation, acceptance and compile) and changes only what round 4 changes — the task identity, the
changeset scope, and five new acceptance edges, one per tool that must be independently installable.
Anything the compiler rejects is left rejected; this script never relaxes a rule to get a pass.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Projects\Agent_Workspace\SBL")
COMPILER = Path(
    r"C:\Projects\Agent_Workspace\HG-KSEOS\var\a3\final-closure\wt-hgk\knowledge-base-compiler"
    r"\construction-acceptance-prompt-compiler\scripts\prompt_contract_compiler.py"
)
SRC = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R3C.json"
OUT = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R4.json"
OUTDIR = REPO / "contracts" / "compiled-r4"
PY = sys.executable

TOOLS = (
    ("ACC-TOOL_TPM_SP", "TOOL_TPM_SP", "SBL_PIPD-LS-PKG_DOC-12#C016", True),
    ("ACC-TOOL_COMMANDER_SP", "TOOL_COMMANDER_SP", "SBL_PIPD-LS-PKG_DOC-12#C017", True),
    ("ACC-TOOL_CHALLENGE_SP", "TOOL_CHALLENGE_SP", "SBL_PIPD-LS-PKG_DOC-12#C018", True),
    ("ACC-TOOL_HGK_UPGRADE", "TOOL_HGK_UPGRADE", "SBL_PIPD-LS-PKG_DOC-12#C029", True),
    ("ACC-TOOL_SBL_STACK", "TOOL_SBL_STACK", "SBL_PIPD-LS-PKG_DOC-12#C033", True),
)


def main() -> int:
    contract = json.loads(SRC.read_text(encoding="utf-8"))
    contract["task_id"] = "SBL-PIPDLS-20261021-R4-C3"

    changeset = contract["changeset"]
    changeset["class"] = "CONTINUATION"
    changeset["baseline_verified"] = True
    changeset["affected_domains"] = [
        "sbl_sp.plugins",
        "sbl_stack",
        "sbl_harness",
        "tools",
        "tests",
        "ci",
        "governance_evidence",
    ]
    changeset["affected_files"] = [
        "sbl_sp/plugins/__init__.py",
        "sbl_sp/plugins/portable.py",
        "sbl_sp/plugins/schema/plugin.schema.json",
        "sbl_stack/__init__.py",
        "sbl_stack/cli.py",
        "sbl_stack/SKILL.md",
        "sbl_harness/__init__.py",
        "sbl_harness/cli.py",
        "tools/build_sp_plugins.py",
        "tools/check_wheel_contents.py",
        "tests/test_sp_plugins.py",
        "tests/test_sbl_stack.py",
        "tests/test_sbl_harness.py",
        "sbl_core/errors.py",
        "pyproject.toml",
        ".github/workflows/ci.yml",
    ]
    changeset["must_not_reopen"] = [
        "foundation main merge",
        "foundation prerelease v0.1.0-foundation-preview",
        "M4-LITE owner procedural receipt",
        "441/149/38 frozen ledgers",
    ]

    existing = {row["acceptance_id"] for row in contract["acceptance"]}
    template = next(
        row for row in contract["acceptance"] if row["acceptance_id"] == "ACC-SBL_SHARED_CORE"
    )
    for acceptance_id, subject_id, locator, runtime in TOOLS:
        if acceptance_id in existing:
            continue
        row = json.loads(json.dumps(template))
        row.update(
            {
                "acceptance_id": acceptance_id,
                "subject_id": subject_id,
                "subject_type": "DELIVERABLE",
                "source_locators": [locator],
                "runtime_required": runtime,
                "required_depth": "L3_INTEGRATION_RUNTIME",
                "positive_fixture": (
                    f"{subject_id}: installs on its own into the selected harness, loads, answers its "
                    "declared question, and uninstalls without residue"
                ),
                "negative_fixture": (
                    f"{subject_id}: a request outside its declared authority is refused with a typed "
                    "error, and an uninstalled or unauthorised harness never reports loaded"
                ),
                "recovery_fixture": (
                    f"{subject_id}: rollback point restores the pre-install host state after a failed "
                    "install"
                ),
                "raw_evidence_required": True,
                "independent_checker_required": True,
            }
        )
        contract["acceptance"].append(row)

    OUT.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(contract['acceptance'])} acceptance edges)")

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
            {"stage": name, "rc": proc.returncode, "stdout": proc.stdout[-4000:],
             "stderr": proc.stderr[-2000:]}
        )
        print(f"{name}: rc={proc.returncode}")
        if proc.returncode != 0:
            print(proc.stdout[-3000:], file=sys.stderr)
            rc_total = proc.returncode
            break
    (OUTDIR / "COMPILER_RECEIPT.json").write_text(
        json.dumps({"contract": str(OUT), "stages": receipts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return rc_total


if __name__ == "__main__":
    raise SystemExit(main())
