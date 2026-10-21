"""R9: give the four runtime_readiness capabilities their OWN acceptance edges.

The four capabilities

    SP_PLUGIN_PACKAGE_TPM
    SP_PLUGIN_PACKAGE_COMMANDER
    SP_PLUGIN_PACKAGE_CHALLENGE
    SP_HOST_INSTALL_REQUEST

were each listed as satisfied by ACC-SBL_SHARED_CORE, whose subject_id is
SBL_SHARED_CORE.  Every other row in the contract is self-consistent -- the
capability, its acceptance subject_id and its acceptance_id all agree -- so
these four are not a design choice, they are a mis-binding.  The consequence is
concrete: a cell of the runtime-readiness matrix for an SP plugin package can be
satisfied by an acceptance that belongs to an entirely different subject.

This script does not invent locators.  Each capability already carries its own
`source_locators` inside `/execution_scope`; those are reused verbatim, so the
new acceptance edge cites exactly what the contract already says governs that
capability.  Each locator was checked to resolve to a real heading/row in the
upstream control package before this script was written:

    DOC-04#C15          -> '# C15|External Challenge-SP ...'          in DOC-04
    DOC-12#C-001..C-003 -> real table rows                           in DOC-12
    DOC-12#C-016..C-018 -> real table rows (TPM/Commander/Challenge) in DOC-12

Nothing is relaxed to obtain a pass: the acceptance rows are built from the
ACC-COMMANDER_SP template shape (subject_type, fixtures, checker requirement,
terminal state) and the compile stages still decide whether the result is legal.

Run:  python _governance/round-20261021-r9/05_CONTRACT/build_contract_r9.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Projects\Agent_Workspace\SBL")
COMPILER = Path(
    r"C:\Projects\Agent_Workspace\HG-KSEOS\var\a3\final-closure\wt-hgk"
    r"\knowledge-base-compiler\construction-acceptance-prompt-compiler"
    r"\scripts\prompt_contract_compiler.py"
)
SRC = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R6.json"
OUT = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R9.json"
OUTDIR = REPO / "contracts" / "compiled-r9"
PY = sys.executable

REPAIRED = (
    "SP_PLUGIN_PACKAGE_TPM",
    "SP_PLUGIN_PACKAGE_COMMANDER",
    "SP_PLUGIN_PACKAGE_CHALLENGE",
    "SP_HOST_INSTALL_REQUEST",
)


def mismatches(contract: dict) -> list[tuple[str, str, str]]:
    """capability -> acceptance subject_id pairs that do not agree."""
    subjects = {a["acceptance_id"]: a.get("subject_id") for a in contract["acceptance"]}
    bad = []
    for row in contract.get("runtime_readiness", []):
        for aid in row.get("acceptance_ids") or []:
            subject = subjects.get(aid, "<missing acceptance>")
            if subject != row["capability"]:
                bad.append((row["capability"], aid, str(subject)))
    return bad


def main() -> int:
    contract = json.loads(SRC.read_text(encoding="utf-8"))
    contract["task_id"] = "SBL-PIPDLS-20261021-R9-C3"

    before = mismatches(contract)
    print(f"mismatches before: {len(before)}")
    for cap, aid, subject in before:
        print(f"  {cap} -> {aid} (subject_id={subject})")

    # The execution_scope entry is the contract's own statement of what governs
    # each capability; reuse it rather than inventing a locator.
    scope = {row["capability"]: row for row in contract.get("execution_scope", [])}
    existing = {row["acceptance_id"] for row in contract["acceptance"]}
    template = next(a for a in contract["acceptance"] if a["acceptance_id"] == "ACC-COMMANDER_SP")

    added = []
    for cap in REPAIRED:
        aid = f"ACC-{cap}"
        locs = scope.get(cap, {}).get("source_locators") or []
        if not locs:
            print(f"FATAL: {cap} has no source_locators in execution_scope; refusing to invent one")
            return 3
        if aid in existing:
            print(f"  {aid} already present; leaving it")
            continue
        row = json.loads(json.dumps(template))
        row.update(
            {
                "acceptance_id": aid,
                "subject_id": cap,
                "source_locators": list(locs),
                "positive_fixture": (
                    f"{cap}: real invocation produces the declared observable result, and the "
                    f"readiness cell for this capability is only satisfied by an acceptance whose "
                    f"subject_id is {cap}"
                ),
                "negative_fixture": (
                    f"{cap}: a request outside its declared authority is refused with a typed error; "
                    f"a foreign acceptance id may not satisfy this cell"
                ),
                "recovery_fixture": (
                    f"{cap}: bounded repair plus checkpoint resume after a confirmed defect"
                ),
            }
        )
        contract["acceptance"].append(row)
        added.append(aid)

    for row in contract.get("runtime_readiness", []):
        if row["capability"] in REPAIRED:
            row["acceptance_ids"] = [f"ACC-{row['capability']}"]

    after = mismatches(contract)
    print(f"\nmismatches after: {len(after)}  (added {len(added)} acceptance edges)")
    if after:
        for cap, aid, subject in after:
            print(f"  UNFIXED {cap} -> {aid} (subject_id={subject})")
        return 4

    print(f"acceptance edges: {len(contract['acceptance'])}")
    OUT.write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT}")

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
            {
                "stage": name,
                "rc": proc.returncode,
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-2000:],
            }
        )
        print(f"{name}: rc={proc.returncode}")
        if proc.returncode != 0:
            print(proc.stdout[-3000:], file=sys.stderr)
            print(proc.stderr[-2000:], file=sys.stderr)
            rc_total = proc.returncode
            break
    (OUTDIR / "COMPILER_RECEIPT.json").write_text(
        json.dumps(
            {
                "contract": str(OUT),
                "mismatches_before": len(before),
                "mismatches_after": len(after),
                "added_acceptance_edges": added,
                "acceptance_edge_count": len(contract["acceptance"]),
                "stages": receipts,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return rc_total


if __name__ == "__main__":
    raise SystemExit(main())
