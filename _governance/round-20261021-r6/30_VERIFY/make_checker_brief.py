#!/usr/bin/env python3
"""Build the R6-TS29 checker brief and status files; then dispatch via the bare-vocab probe pool."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

SBL = Path(r"C:\Projects\Agent_Workspace\SBL")
OUT = SBL / "_governance" / "round-20261021-r6" / "30_VERIFY"
OUT.mkdir(parents=True, exist_ok=True)

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

cand_commit = "a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2"
base_head = "bedc11957d4fc2474b249b69d200829272c118ef"
r6_paths = ["_governance/round-20261021-r6/", "contracts/SBL_C0_C9_CONTRACT-R6.json", "contracts/compiled-r6/"]
sc_flat = SBL / "_r6_status.json"

brief = f"""# R6 Independent Verify Brief (round SBL-R6-DOC00-13-CONTINUATION, CHK29)

## Your task
You are the separate model-axis independent checker for SBL round R6. Your mandate:
1. Read back the raw inputs listed below and independently recompute the checks — accept nothing on the maker's say-so.
2. For each finding, copy the exact cfg/args/exit code/case that proves it.
3. Output a SHORT verdict (English, markdown) with sections: STRENGTHS / WEAKNESSES / ITEMS-LIST / VERDICT.
4. Do not modify any file. You are read-only.

## Inputs (raw, machine-generated this round; all under C:/Projects/Agent_Workspace/SBL)
- _governance/round-20261021-r6/00_NORTH_STAR_AND_SPEC.md              (round spec, lane/session plane separation)
- _governance/round-20261021-r6/10_PREFLIGHT/SSOT_FACTS.json           (46-source intake hashes + git + HGK readback)
- _governance/round-20261021-r6/30_CONTRACT/…, contracts/SBL_C0_C9_CONTRACT-R6.json + compiled-r6/compiler-receipt.json   (PROMPT_COMPILE_PASS)
- _governance/round-20261021-r6/40_TS05/TS05_READBACK.json             (a6bcdd0 tests 192/2 vs CI 191+3/189+5; wheel manifest parity)
- evidence_ledger/child_outcome_ledger.json + surface_c001_c038_ledger.json + source_identity_441_ledger.json  (50/149/38/441 skeleton; every row OPEN, no fabricated PASS)
- _governance/round-20261021-r6/20_TS20/SP_SEPARATION_CHECK.json       (13 POS/NEG permission probes, 13/13)
- upstream frozen subject: https://github.com/shw097-team/SBL commit {cand_commit} (local worktree C:/Projects/_sbl_r4/c3v2 @ same SHA)

## Baseline R6 reference
- R6 external review report sha256 ac2db3cb…42cde; merge decision RECOMMEND_MERGE_SCOPED_NOW (Owner-only, NOT performed).
- Full-contract verdict stays FAIL_FULL_CONTRACT / PARTIAL_CHALLENGE; three ChatGPT plugins 0/3 host-issued IDs; DeepSeek surfaces NOT_ADMITTED.

## Model-axis deviation to disclose (do NOT re-derive)
Round identity: R6-TS19/CHK29 independent checker is openai-codex/gpt-6.1-sol (OAuth), role mandate openai-codex/gpt-6.1-sol.
Upstream R6 report was produced by two different lanes in rounds R5; its identity deviates by model axis. That is an upstream additive disclosure, NOT yours to re-derive: focus on whether the maker-side R6 facts hold under your independent re-checks.

## Output
Return exactly one artifact: an English markdown document with a VERDICT line of the form
VERDICT: PASS_WITH_DISCLOSURES | FAIL | PASS
and a numbered ITEMS-LIST (max 8 lines) — each item: id, severity(BLOCKER/MAJOR/MINOR), what you re-executed to prove it.
Be adversarial: actively try to find a fabricated PASS row, an orphan id, a hash mismatch, an SP-permission leak, or a proxy-evidence shortcut in the R6 round.
"""
brief_path = OUT / "CHECKER_BRIEF.md"
brief_path.write_text(brief, encoding="utf-8")
print("brief size:", brief_path.stat().st_size, "sha:", sha(brief_path.read_bytes()))
