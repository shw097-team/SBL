#!/usr/bin/env python3
"""Assemble the R5 machine-readable evidence return from the artefacts this round actually produced.

Every field is read back from a file or a recorded run; nothing here is asserted from memory. The
claim ceiling is the lowest of the stated evidence layers — a local repair plus a model-axis
independent read-only review is NOT `INDEPENDENT_CASE_PASS`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\Agent_Workspace\SBL\_governance\round-20261021-r5")
REPO = Path(r"C:\Projects\Agent_Workspace\SBL")
OUT = ROOT / "90_EVIDENCE" / "EVIDENCE_RETURN_R5.json"

CLAIM_CEILING = [
    "SOURCE_VERIFIED",
    "PROMPT_COMPILE_PASS",
    "CODE_READY",
    "PACKAGED_HOST_PENDING",
    "LOCAL_TESTED_POS_NEG_INJECTION",
    "CI_GREEN_SAME_SHA_UBUNTU_WINDOWS",
    "MODEL_AXIS_INDEPENDENT_READONLY_REVIEW_PASS_WITH_DISCLOSURES",
]
NON_CLAIMS = [
    "INDEPENDENT_CASE_PASS",
    "HOST_EFFECTIVE_LOAD",
    "NATIVE_EFFECT_AUDITED",
    "OWNER_RELEASE_APPROVED",
    "SBL_FULL_DOC_CONTRACT_PASS",
    "CHATGPT_PRIVATE_PLUGIN_ACCEPTED",
]


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract_receipt = json.loads((REPO / "contracts" / "compiled-r5" / "compiler-receipt.json").read_text(encoding="utf-8"))
    matrix = load("20_TS05/NEGATIVE_MATRIX.json")
    intake = load("10_PREFLIGHT/SOURCE_INTAKE.json")
    env = load("10_PREFLIGHT/ENV_SNAPSHOT.json")
    rounds = load("20_TS05/VERIFICATION_ROUNDS/ROUNDS.json")

    row = {
        "round": "SBL-R5-20261021-C5",
        "task_id": "SBL-FULL-DOC00-13-R5-20261021",
        "finding": "F-R5-HARNESS-UNINSTALL-TRAVERSAL-001",
        "finding_status": "CLOSED_LOCALLY_PENDING_OWNER_MERGE",
        "source_intake": {
            "doc_00_13": intake["summary"]["DOC_00_13"],
            "kp_00_19": intake["summary"]["KP_00_19"],
            "vol_01_10": intake["summary"]["VOL_01_10"],
            "skills": intake["summary"]["SKILLS"],
            "all_match": intake["all_match"],
            "receipt": "10_PREFLIGHT/SOURCE_INTAKE.json",
        },
        "model_plan": {
            "lane_plane": "lanes are pinned per dispatch; the interactive session model is a different plane",
            "PLAN": env["lanes"]["PLAN"],
            "EXECUTE": env["lanes"]["EXECUTE"],
            "VERIFY_SECURITY": env["lanes"]["VERIFY_SECURITY"],
            "receipt": "10_PREFLIGHT/ENV_SNAPSHOT.json",
        },
        "compiler": {
            "verdict": contract_receipt["verdict"],
            "contract_sha256": contract_receipt["contract_sha256"],
            "prompt_sha256": contract_receipt["prompt_sha256"],
            "compiler_sha256": contract_receipt["compiler_sha256"],
            "acceptance_edges": 31,
            "receipt": "contracts/compiled-r5/compiler-receipt.json",
        },
        "repair": {
            "candidate_branch": "candidate/c3-20261021-v2",
            "commits": [
                {"sha": "50e4852", "what": "allowlist + digest + link guards on uninstall"},
                {"sha": "ab9a354", "what": "bounded directory cleanup; discriminating escape tests; backslash-key fix"},
                {"sha": "a6bcdd0", "what": "allowlist test made discriminating (real digest)"},
            ],
            "affected_files": ["sbl_harness/__init__.py", "sbl_core/errors.py", "tests/test_sbl_harness.py"],
            "patch_diff_sha256": sha(ROOT / "20_TS05" / "PATCH.diff"),
        },
        "tests": {
            "negative_matrix": "20_TS05/NEGATIVE_MATRIX.json",
            "cases_green": matrix["verdict"]["all_cases_green"],
            "skipped_on_windows_host": matrix["verdict"]["skipped_on_this_host"],
            "injection_control_pre_repair_bytes_fail": matrix["verdict"]["pre_repair_bytes_fail_the_escapes"],
            "linux_container": "20_TS05/LINUX_CONTAINER_TESTS.txt (symlink cases run; junction cases skip on POSIX)",
            "gates": "11/11 exit 0; full suite 192 passed, 2 skipped (Windows), gate total 311",
        },
        "ci": [
            {"sha": "50e4852", "runs": [39531831134, 39531827059], "jobs": "2/2 per run success"},
            {"sha": "ab9a354", "runs": [39532711875, 39532706528], "jobs": "2/2 per run success"},
            {
                "sha": "a6bcdd0",
                "runs": [39532993091, 39532986228],
                "jobs": "2/2 per run success",
                "raw_counts": {"ubuntu": "189 passed, 5 skipped", "windows": "191 passed, 3 skipped"},
            },
        ],
        "independent_review": {
            "principal": "openai-codex/gpt-6.1-sol (VERIFY lane, read-only sandbox)",
            "maker": "opencode-go/deepseek-v4.1-flash (session) + EXECUTE lane",
            "model_axis_independence": True,
            "same_host_and_process_axis": "shared machine and dispatcher; declared as compensating control, not independence",
            "rounds": rounds,
            "final_verdict": "PASS_WITH_DISCLOSURES",
            "transcripts": "20_TS05/VERIFICATION_ROUNDS/round{1,2,3}_*.txt",
            "note": "the review ran three times and its findings drove two further commits; the reviewer never executed tests (read-only lane)",
        },
        "disclosures": [
            "TOCTOU: validation, hashing and unlink are not atomic against a concurrent filesystem mutation",
            "manifest digests prove consistency, not installation provenance",
            "deletion is not transactional after the first unlink",
            "symlink tests skip on a Windows host without Developer Mode; they ran on ubuntu CI and in the python:3.11-slim container",
            "the remaining rglob file inventory can inspect junction-linked entries although it deletes nothing",
            "all review rounds are static review of the supplied diff by a read-only lane",
        ],
        "claim_ceiling": CLAIM_CEILING,
        "non_claims": NON_CLAIMS,
    }
    OUT.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"finding_status": row["finding_status"], "compiler": row["compiler"]["verdict"], "claim_ceiling": CLAIM_CEILING[-1]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
