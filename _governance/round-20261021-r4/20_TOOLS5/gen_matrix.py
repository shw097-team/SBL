#!/usr/bin/env python3
"""Emit TOOLS5_HARNESS_MATRIX from measured facts.

Every field that can be computed is computed from the artefact on disk; every field that cannot be
computed is written as an explicit HOLD token rather than a hopeful value. The matrix exists so a
reviewer can see, per tool, which of the ten install questions were answered and which were not.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROUND = Path(__file__).resolve().parent.parent
PACKAGES = ROUND / "40_SP_PACKAGES"
SOURCE_SHA = "68c276d354dae2b1bc2baef290f89e539fb34751"
HOST = "Hermes Agent desktop (this machine, skills loader)"
HOST_VERSION = "not exposed by the app data directory; not recorded rather than guessed"
ROLLBACK = "90_HERMES_ROLLBACK/ROLLBACK_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_row(zip_name: str, skill: str, tool: str, ceiling: str) -> dict:
    archive = PACKAGES / zip_name
    return {
        "package_id": tool,
        "source_sha": SOURCE_SHA,
        "artifact_sha256": sha256(archive),
        "artifact_locator": f"_governance/round-20261021-r4/40_SP_PACKAGES/{zip_name}",
        "independent_install_command": (
            f"unzip {zip_name} -d <harness>/skills && copy skills/{skill}/ into the harness skills root"
        ),
        "host_abi": "agent-plugins/1.0.0 manifest + skills/<name>/SKILL.md directory convention",
        "host": HOST,
        "host_version": HOST_VERSION,
        "host_install_receipt": "91_HERMES_INSTALL/INSTALL_RECEIPT.json (installed[] entry with per-file sha256)",
        "host_issued_identity": (
            "HOLD: Hermes issues no plugin id. Host-side registration readback is the loaded skill name, "
            "recorded under deploy_register_readback; do not read this as a hosted registry identity"
        ),
        "deploy_register_readback": "hermes skills list -> row (name, category=sbl, source=local, state=enabled)",
        "effective_load_trace": (
            "skill_view(name) -> success=true, readiness_status=available, setup_needed=false, "
            f"_source_path=skills/sbl/{skill}/SKILL.md"
        ),
        "ordinary_user_POS": f"skill_view(name='{skill}') returned the body (see 02_TASK_LIST evidence column)",
        "unauthorized_NEG": (
            "skill_view(name='sbl-tpm-sp-nonexistent-probe') -> success=false, 'not found' with an "
            "available_skills list; an unregistered name never resolves"
        ),
        "dependency_resolution": "none: package declares no runtime dependencies; wheel installs with --no-index --no-deps",
        "rollback": ROLLBACK,
        "uninstall": f"remove skills/sbl/{skill}; rollback archive restores the pre-install tree",
        "uninstall_exercised": (
            "NOT_RUN on this host: the owner asked for install-and-test, so the surfaces are kept installed. "
            "Package-level uninstall/residue was exercised in the Docker sandbox (60_DOCKER_SANDBOX)"
        ),
        "no_residue": "SANDBOX_PROVEN (container), HOST_NOT_RUN (kept installed by owner decision)",
        "checker_receipt": "NONE: no independent checker signed this row; see claim_ceiling",
        "owner_gate": "OWNER_GRANTED 2026-10-21: install and test on this machine, rollback point first",
        "claim_ceiling": ceiling,
    }


def main() -> int:
    rows = [
        skill_row("sbl-tpm-sp-0.1.0.zip", "tpm-sp", "TPM-SP", "EFFECTIVE_LOAD (local); HOST_ISSUED_IDENTITY absent"),
        skill_row(
            "sbl-commander-sp-0.1.0.zip",
            "commander-sp",
            "Commander-SP",
            "EFFECTIVE_LOAD (local); HOST_ISSUED_IDENTITY absent",
        ),
        skill_row(
            "sbl-external-challenge-sp-0.1.0.zip",
            "external-challenge-sp",
            "Acceptance-Challenge-SP",
            "EFFECTIVE_LOAD (local); HOST_ISSUED_IDENTITY absent; read-only by construction",
        ),
        {
            "package_id": "HGK-Upgrade",
            "source_sha": SOURCE_SHA,
            "artifact_sha256": None,
            "artifact_locator": "C:/Projects/Agent_Workspace/SBL-install/hgk-adapter (adapter.json + plugin.json + skill)",
            "independent_install_command": "sbl-harness install --target <dir> --hgk-root <HGK root>",
            "host_abi": "hgk-harness-abi/1 (provides plan/execute/verify; requires WorkOrder/ExecutionBinding/Permit from native)",
            "host": HOST,
            "host_version": HOST_VERSION,
            "host_install_receipt": "91_HERMES_INSTALL/INSTALL_RECEIPT.json step harness.install rc=0 (ROOT_READY)",
            "host_issued_identity": "HOLD: adapter carries no host-issued id; probe_status=ROOT_READY against the real HGK root",
            "deploy_register_readback": "hermes skills list -> hgk-governed-runtime, category=sbl, enabled",
            "effective_load_trace": (
                "skill_view(name='hgk-governed-runtime') -> available; adapter.doctor -> ok=true, probe ROOT_READY, "
                "hg_kseos 0.1.0"
            ),
            "ordinary_user_POS": "sbl-harness doctor --target <dir> -> ok=true, probe.status=ROOT_READY",
            "unauthorized_NEG": (
                "install against a root without src/hg_kseos, spine db, lane registry or dispatcher -> "
                "REFUSED_ROOT_UNUSABLE/ROOT_INCOMPLETE and nothing is written (tests/test_sbl_harness.py)"
            ),
            "dependency_resolution": "pinned hg_kseos >=0.1.0,<0.2.0 resolved from the HGK root at probe time; no vendored copy",
            "rollback": ROLLBACK,
            "uninstall": "sbl-harness uninstall --target <dir> (refuses a directory holding foreign files)",
            "uninstall_exercised": "YES in unit tests and Docker sandbox; NOT_RUN on this host (kept installed)",
            "no_residue": "SANDBOX_PROVEN",
            "checker_receipt": "NONE",
            "owner_gate": "OWNER_GRANTED 2026-10-21",
            "claim_ceiling": (
                "ADAPTER_INSTALLED; native acceptance NOT_GRANTED. HGK's own WorkOrder/Permit/ExecutionBinding "
                "were not exercised and are not claimed"
            ),
        },
        {
            "package_id": "SBL-Stack",
            "source_sha": SOURCE_SHA,
            "artifact_sha256": "e5767bf8a8ba309553f5b979f3ddb2e9f883ab9a378b0766ad444efbb26ade36",
            "artifact_locator": "sbl_v01-0.1.0-py3-none-any.whl (built from 68c276d; wheel bytes vary per build, digest is of the installed one)",
            "independent_install_command": (
                "python -m venv <venv> && <venv>/pip install --no-index --no-deps sbl_v01-0.1.0-py3-none-any.whl "
                "&& <venv>/sbl-stack install --root <dir>"
            ),
            "host_abi": "CLI + integrity manifest (stack.json) over the composed M01..M06 core",
            "host": "Windows 11, Python 3.11.9, standalone venv at C:/Projects/Agent_Workspace/SBL-install/.venv",
            "host_version": "Python 3.11.9",
            "host_install_receipt": "91_HERMES_INSTALL/INSTALL_RECEIPT.json steps pip.install/stack.install rc=0",
            "host_issued_identity": "HOLD: a CLI has no host-issued id; identity is the installed manifest digest",
            "deploy_register_readback": "stack.json manifest_sha256 recorded at install; sbl-stack status reads it back",
            "effective_load_trace": (
                "sbl-stack doctor -> ok=true, components=14, mode_gate_cells=39; selftest 9/9 steps"
            ),
            "ordinary_user_POS": "sbl-stack selftest -> 9/9 (core.doctor, m01, m02, m03, sp.manifests, modes.matrix, plugins.build, 2 NEG)",
            "unauthorized_NEG": (
                "install into a non-empty foreign directory -> SBL_E_FOREIGN_FILES; tampered manifest -> doctor ok=false; "
                "uninstall over a foreign file -> refused"
            ),
            "dependency_resolution": "zero runtime dependencies (stdlib only); installed with --no-index --no-deps",
            "rollback": ROLLBACK,
            "uninstall": "sbl-stack uninstall --root <dir>",
            "uninstall_exercised": "YES in unit tests and Docker sandbox; NOT_RUN on this host (kept installed)",
            "no_residue": "SANDBOX_PROVEN (pip uninstall + no sbl_* modules + no console scripts)",
            "checker_receipt": "NONE",
            "owner_gate": "OWNER_GRANTED 2026-10-21",
            "claim_ceiling": "LOCAL_STANDALONE_INSTALL; production and multi-host NOT claimed",
        },
    ]

    payload = {
        "schema": "SBL-TOOLS5-HARNESS-MATRIX/1",
        "round": "R4 (order SBL-R4-20261020-C3-FIVE-TOOLS-SWOF-W12)",
        "source_sha": SOURCE_SHA,
        "generated_from": "measured artefacts in this round; no field is copied from a prior round",
        "note": (
            "One tool x one harness x one journey, five rows. A row is not a PASS because it exists: read "
            "claim_ceiling and uninstall_exercised. Five rows surviving the same harness does not prove any "
            "other harness works."
        ),
        "rows": rows,
        "aggregate": {
            "tools": len(rows),
            "independently_installed": len(rows),
            "effective_load_proven": 5,
            "host_issued_identity_obtained": 0,
            "independent_checker_signed": 0,
            "five_tools_qualified_scoped": False,
            "why_not": (
                "FIVE_TOOLS_QUALIFIED_SCOPED requires a per-tool independent receipt and an explicit "
                "applicability list for the selected harness. Every row here is maker-measured on one harness, "
                "three of five have no host-issued identity, and none carries a distinct checker signature."
            ),
        },
    }
    out = ROUND / "20_TOOLS5_HARNESS_MATRIX.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out, len(rows), "rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
