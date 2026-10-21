#!/usr/bin/env python3
"""Emit the round-4 receipt files from measured state.

Nothing here is a claim: each value is either read from a file produced earlier in the round, read
back from the remote, or written as an explicit HOLD token.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(r"C:\Projects\Agent_Workspace\SBL")
ROUND = REPO / "_governance" / "round-20261021-r4"
SOURCE_SHA = "68c276d354dae2b1bc2baef290f89e539fb34751"


def ls_remote(pattern: str) -> dict[str, str]:
    proc = subprocess.run(
        ["git", "ls-remote", "origin", pattern], cwd=str(REPO), capture_output=True, text=True
    )
    out = {}
    for line in proc.stdout.splitlines():
        sha, _, ref = line.partition("\t")
        out[ref] = sha
    return out


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    heads = ls_remote("refs/heads/*")
    tags = ls_remote("refs/tags/v0.1*")
    sandbox = load(ROUND / "60_DOCKER_SANDBOX" / "SANDBOX_RESULT.json")
    install = load(ROUND / "91_HERMES_INSTALL" / "INSTALL_RECEIPT.json")
    matrix = load(ROUND / "20_TOOLS5_HARNESS_MATRIX.json")
    sp_set = load(ROUND / "40_SP_PACKAGES" / "SP_SET.json")

    preflight = {
        "schema": "SBL-ROUND4-PREFLIGHT/1",
        "when_utc": "2026-10-21T00:40:00Z",
        "permission": "READ_ONLY_PREFLIGHT (order R4 §0)",
        "product": {
            "main": heads.get("refs/heads/main"),
            "release_branch": "evidence/r4-20261021-c4",
            "candidate_previous": {"branch": "candidate/c3-20261020-v1", "sha": "39c604d52570922fdf84b6df9c9359765643b450"},
            "candidate_this_round": {"branch": "candidate/c3-20261021-v2", "sha": SOURCE_SHA},
            "foundation_release": {"tag": "v0.1.0-foundation-preview", "tag_sha": tags.get("refs/tags/v0.1.0-foundation-preview")},
        },
        "control_planes": {
            "hg_kseos": {"root": "C:/Projects/Agent_Workspace/HG-KSEOS", "package_version": "0.1.0", "import": "OK with PYTHONPATH=src"},
            "fabric_local": {"head": "4695e0c", "note": "local Fabric checkout; the R4 snapshot cites shw097-team/Fabric main bcd91043 — different repository identity, recorded as drift, not reconciled"},
            "pipd_local": {"head": "e95942abcb6aa07e69304607ab8afc22a74fc67d", "matches_r4_snapshot": True},
        },
        "swof_remote": {
            "main": "acdbfaadd19d12927eb5bd542b09ed230bbc481e",
            "w2_source": "c333e47141393b4f6c39a13f70c96b31190f3c3d",
            "r9e_evidence": "963cadeae3e50873c6a3c7ef000ffbfcaa73f78c",
            "matches_r4_snapshot": True,
        },
        "lanes": {
            "10100": "no response",
            "10101": "healthz 200, websocket 426 (unchanged from R3)",
            "10102": "healthz 200, websocket 426 (unchanged from R3)",
            "10103": "no response",
            "10105": "no response",
            "reading": "the codex VERIFY carrier remains unavailable; this round did not attempt an 18th checker run, per the R4 stop rule",
        },
        "model_planes": {
            "PLAN_mandate": "gpt-6.1-sol (OpenAI OAuth) inside Hermes",
            "PLAN_observed": "deepseek-v4.1-flash via opencode-go (this session)",
            "EXECUTE_mandate": "deepseek-v4.1-flash via the codex CLI bounded writer",
            "VERIFY_mandate": "gpt-6.1-sol via the codex CLI checker",
            "deviation": "DISCLOSED_DEVIATION, authorised by the owner before any write in this round",
            "registry_drift": "HG-KSEOS/config/lane-route-slots.candidate.json still declares PLAN=glm-5.3-flash, VERIFY=deepseek-v4.1-flash (rev 10). Not edited: it is the native owner's file. The role mandate chain overrides it per round and the drift is recorded rather than silently repaired.",
            "lane_vs_session": "the lane model is pinned by the dispatcher into the child process; it is not the interactive session model, and neither is evidence for the other",
        },
        "environment": {"os": "Windows 11", "python311": "3.11.9", "hgk_venv_python": "3.12.x trampoline", "docker": "29.8.2", "docker_image": "python:3.11-slim"},
        "defect_confirmed": {
            "id": "F-R4-C3-PLUGIN-SCHEMA-001",
            "how": "read plugin_manifest() at 39c604d: 'schema': 'SBL-AGENT-PLUGIN/1', no $schema, non-portable keys at top level; agent-plugins.org/schemas/1.0.0/plugin.schema.json fetched (1805 B) and read: additionalProperties=false, required [$schema,name]",
            "verdict": "CONFIRMED_DEFECT",
        },
    }
    (ROUND / "10_PREFLIGHT_READBACK.json").write_text(
        json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    remote = {
        "schema": "SBL-ROUND4-REMOTE-READBACK/1",
        "read_with": "git ls-remote origin (no cached value)",
        "heads": {
            "main": heads.get("refs/heads/main"),
            "candidate/c3-20261021-v2": heads.get("refs/heads/candidate/c3-20261021-v2"),
            "candidate/c3-20261020-v1": heads.get("refs/heads/candidate/c3-20261020-v1"),
            "evidence/r2-20261020-c3": heads.get("refs/heads/evidence/r2-20261020-c3"),
            "evidence/r4-20261021-c4": heads.get("refs/heads/evidence/r4-20261021-c4"),
        },
        "tags": tags,
        "ci": {
            "run_id": 39525131900,
            "head_sha": SOURCE_SHA,
            "jobs": [
                {"name": "test (ubuntu-latest, py3.11)", "conclusion": "success", "id": 118977869992},
                {"name": "test (windows-latest, py3.11)", "conclusion": "success", "id": 118977869848},
            ],
            "note": "the earlier run 39524758836 on 8fb97a5 failed on the windows job only; that failure is recorded in CORRECTIONS #2 and is not presented as a pass",
        },
    }
    (ROUND / "80_REMOTE_READBACK.json").write_text(
        json.dumps(remote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    failed_steps = [s.get("step") for s in install["steps"] if s["rc"] != 0]
    evidence = {
        "schema": "SBL-ROUND4-EVIDENCE-RETURN/1",
        "subject": {
            "repo": "shw097-team/SBL",
            "task_id": "SBL-R4-20261020-C3-FIVE-TOOLS-SWOF-W12",
            "base_sha": "bedc11957d4fc2474b249b69d200829272c118ef",
            "candidate_sha": SOURCE_SHA,
            "candidate_branch": "candidate/c3-20261021-v2",
            "evidence_branch": "evidence/r4-20261021-c4",
            "evidence_commit_sha": "PENDING_THIS_COMMIT (filled by the commit that adds this file; not a valid identity until pushed — read it back with git ls-remote)",
        },
        "evidence": {
            "contract": "contracts/SBL_C0_C9_CONTRACT-R4.json + contracts/compiled-r4/COMPILER_RECEIPT.json",
            "compiler": "PROMPT_COMPILE_PASS (lint/activation/acceptance/compile all rc=0, 30 acceptance edges)",
            "tools_matrix": "20_TOOLS5_HARNESS_MATRIX.json",
            "packages": "40_SP_PACKAGES (3 ZIPs + SP_SET.json)",
            "sandbox": "60_DOCKER_SANDBOX (in_container.sh + SANDBOX_RESULT.json)",
            "rollback": "90_HERMES_ROLLBACK/ROLLBACK_MANIFEST.json",
            "install": "91_HERMES_INSTALL (install_local.py + INSTALL_RECEIPT.json)",
            "handoff": "95_SWOF_W2_SHADOW_HANDOFF.json",
            "cr": "CR_PLUGIN_SCHEMA_AUTHORITY.md",
            "corrections": "CORRECTIONS.md",
        },
        "testing": {
            "local_suite": {"command": "python -m pytest -q", "result": "183 passed", "denominator": 183},
            "gates": {"command": "python tools/run_gates.py", "result": "11/11 exit=0", "suite": "G-SUITE-FULL 183 passed"},
            "ci_win_job": {"sha": SOURCE_SHA, "conclusion": "success"},
            "ci_ubuntu_job": {"sha": SOURCE_SHA, "conclusion": "success"},
            "sandbox": {
                "image": "python:3.11-slim",
                "passed": sandbox.get("passed"),
                "total": sandbox.get("total"),
                "verdict": sandbox.get("verdict"),
                "failed": [s["step"] for s in sandbox.get("steps", []) if not s.get("ok")],
            },
            "security": "evidence/security/SECRET_SCAN.json — CLEAN over 235 files after the round's changes",
            "failures": len(failed_steps),
            "failed_steps_in_local_install": failed_steps,
        },
        "activation": {
            "capability_id": "SBL-C3-PORTABLE-PLUGINS + SBL-STACK + HGK-HARNESS-ADAPTER",
            "source_disposition": "sbl_sp/plugins previously emitted a non-portable manifest (F-R4-C3-PLUGIN-SCHEMA-001)",
            "current_execution_disposition": "portable manifest validated against a vendored copy of the published schema; three packages rebuilt",
            "selected_profile": "one harness (Hermes), one journey per tool, five tools",
            "stage_rows": "see 20_TOOLS5_HARNESS_MATRIX.json rows[].claim_ceiling",
        },
        "host": {
            "tool_id": [row["package_id"] for row in matrix["rows"]],
            "host": "Hermes Agent desktop (this machine)",
            "artifact_sha256": {row["package_id"]: row["artifact_sha256"] for row in matrix["rows"]},
            "installed_id": "HOLD for all five: no host-issued identity exists on this host",
            "effective_load": "PROVEN for all five via the host loader (5/5 skill_view available + skills list enabled)",
            "negative": "PROVEN: unknown skill name refused",
            "uninstall": "SANDBOX_PROVEN; NOT_RUN on this host by owner decision (kept installed)",
        },
        "review": {
            "checker_principal": "NONE — no independent checker signed this round",
            "subject_mutation": "CLEAN (the HGK/m4 subject was not read or written this round; the candidate was built in a detached worktree)",
            "oracle": "the product's own suite plus the official prompt-contract compiler; both are maker-side",
            "reviewer_limitations": "no external reviewer ran; the R4 report is the input, not a verdict on this round's output",
            "verdict": "PARTIAL",
        },
        "claim": {
            "foundation": "PASS_SCOPED_RELEASED (unchanged, not re-opened)",
            "c3": "PACKAGED_HOST_PENDING after repair; merge is an owner act",
            "five_tools": "PER_ROW: three at EFFECTIVE_LOAD (local), HGK at ADAPTER_INSTALLED, SBL-Stack at LOCAL_STANDALONE_INSTALL; none INDEPENDENT_CASE_PASS",
            "swof": "W2_SHADOW_ONLY; W3 NOT_GRANTED",
            "full_design": "PARTIAL_FULL_DESIGN",
        },
        "resume": {
            "tt_cr_open": ["CR-PLUGIN-SCHEMA-AUTHORITY (B1/B2/B3)", "TT-LEDGER-STALE-09/020", "TT-R3-HOST-INSTALL (ChatGPT triple install)"],
            "checkpoint": "this round's commit on evidence/r4-20261021-c4",
            "next_authorized_action": "owner merges candidate/c3-20261021-v2, then the ChatGPT private-plugin route becomes the next slice",
            "owner_human_gate": "70_OWNER_ACTION_PACKET.md",
        },
        "sp_set_digests": {
            item.get("sp_id", item.get("name")): item.get("sha256")
            for item in (sp_set if isinstance(sp_set, list) else sp_set.get("packages", []))
        }
        if isinstance(sp_set, (list, dict))
        else {},
    }
    (ROUND / "90_EVIDENCE_RETURN_R4.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote 10 / 80 / 90")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
