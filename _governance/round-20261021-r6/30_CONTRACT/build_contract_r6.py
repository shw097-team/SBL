#!/usr/bin/env python3
"""R6-TS02: derive the R6 contract from R5 (inherit shape, change only round identity + edges)."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO = Path(r"C:\Projects\Agent_Workspace\SBL")
SRC = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R5.json"
OUT = REPO / "contracts" / "SBL_C0_C9_CONTRACT-R6.json"
OUTDIR = REPO / "contracts" / "compiled-r6"
COMPILER = Path(r"C:\Projects\Agent_Workspace\知識庫\工程基座\construction-acceptance-prompt-compiler"
                r"\construction-acceptance-prompt-compiler\scripts\prompt_contract_compiler.py")
PY = sys.executable

contract = json.loads(SRC.read_text(encoding="utf-8"))
contract["task_id"] = "SBL-R6-DOC00-13-CONTINUATION"

# R6 intent: supersede the R5 narrative (secret-scanner repair) with the R6 continuation goal.
contract["intent"]["goal"] = (
    "R6 continuation per the R6 independent acceptance report: reuse the scoped verdicts on the "
    "frozen candidate a6bcdd0 (PR#2 RECOMMEND_MERGE_SCOPED_NOW; owner-only merge), build the "
    "50-parent/149-child trace skeleton without fabricating any PASS, reconcile the 38-surface "
    "and 441-identity ledgers with frozen-vs-current dispositions, run the PLAN/EXECUTE/VERIFY "
    "lanes under the R6 model mandate (PLAN+VERIFY openai-codex/gpt-6.1-sol medium; EXECUTE "
    "opencode-go/deepseek-v4.1-flash via the sealed Codex lane), publish the scrubbed candidate "
    "and evidence branches with distinct remote SHAs, and keep the full contract honestly "
    "FAIL_FULL_CONTRACT until every active predicate closes."
)

cs = contract["changeset"]
cs["class"] = "CONTINUATION"
cs["baseline_verified"] = True
cs["affected_domains"] = ["trace_ledger", "packaging", "governance_evidence", "contracts"]
cs["affected_files"] = [
    "contracts/SBL_C0_C9_CONTRACT-R6.json",
    "_governance/round-20261021-r6/",
    "evidence_ledger/child_outcome_ledger.json",
    "evidence_ledger/surface_c001_c038_ledger.json",
    "evidence_ledger/source_identity_441_ledger.json",
]
cs.setdefault("must_not_reopen", []).extend([
    "R6 verdicts: PR#2 RECOMMEND_MERGE_SCOPED_NOW stays; full contract stays FAIL",
])

existing = {row["acceptance_id"] for row in contract["acceptance"]}
NEW_EDGES = [
 {
  "acceptance_id": "ACC-R6_TRACE_SKELETON",
  "subject_id": "SBL_CHILD_OUTCOME_LEDGER",
  "subject_type": "CAPABILITY",
  "source_locators": ["SBL_PIPD-LS-PKG_DOC-01#C05.1", "SBL_PIPD-LS-PKG_DOC-01#C05.2",
                      "SBL_PIPD-LS-PKG_DOC-00#R03"],
  "runtime_required": False,
  "required_depth": "L1_SCHEMA_CONTRACT",
  "positive_fixture": ("SBL_CHILD_OUTCOME_LEDGER: 50 parents and 149 children each carry source "
                       "locator, owner, consumer, acceptance predicate, and honest OPEN status; "
                       "0 orphan ids vs the DOC-01 appendix; no row claims PASS without raw evidence"),
  "negative_fixture": ("SBL_CHILD_OUTCOME_LEDGER: a fabricated PASS row, a child id missing from "
                       "the ledger, or a duplicate id is detected by the coverage check and fails "
                       "the round"),
  "recovery_fixture": ("SBL_CHILD_OUTCOME_LEDGER: coverage failure lists the exact "
                       "missing/duplicate/orphan ids so the ledger can be corrected without "
                       "touching the product"),
  "raw_evidence_required": True,
  "independent_checker_required": True,
  "terminal_states": ["INDEPENDENT_CASE_PASS"],
 },
 {
  "acceptance_id": "ACC_R6_LEDGER_RECONCILE",
  "subject_id": "SBL_SURFACE_441_LEDGER",
  "subject_type": "CAPABILITY",
  "source_locators": ["SBL_PIPD-LS-PKG_DOC-12#D12-04.PATCH", "SBL_PIPD-LS-PKG_DOC-06#C32",
                      "SBL_PIPD-LS-PKG_DOC-06#C33.2"],
  "runtime_required": False,
  "required_depth": "L1_SCHEMA_CONTRACT",
  "positive_fixture": ("SBL_SURFACE_441_LEDGER: C-001..C-038 and 441 source identities carry "
                       "frozen_disposition plus current_execution as separate columns; METHOD-09 "
                       "GitHub Actions shows current executed with historic DEFERRED preserved"),
  "negative_fixture": ("SBL_SURFACE_441_LEDGER: treating the 441 ledger as an install count, or "
                       "marking NOT_ADMITTED hosts (C-007/011/015/032/036) as installed, is a "
                       "fabrication and fails the round"),
  "recovery_fixture": ("SBL_SURFACE_441_LEDGER: reconciliation diffs list stale rows by id so "
                       "they can be corrected without rewriting frozen history"),
  "raw_evidence_required": True,
  "independent_checker_required": True,
  "terminal_states": ["INDEPENDENT_CASE_PASS"],
 },
 {
  "acceptance_id": "ACC_R6_CANDIDATE_READBACK",
  "subject_id": "SBL_R6_CANDIDATE_EVIDENCE_BIND",
  "subject_type": "CAPABILITY",
  "source_locators": ["SBL_PIPD-LS-PKG_DOC-01#U26", "SBL_PIPD-LS-PKG_DOC-01#U27",
                      "SBL_PIPD-LS-PKG_DOC-12#C43"],
  "runtime_required": True,
  "required_depth": "L3_INTEGRATION_RUNTIME",
  "positive_fixture": ("SBL_R6_CANDIDATE_EVIDENCE_BIND: this round's candidate branch and evidence "
                       "branch have distinct SHAs on the remote, the exact base of PR#2 (a6bcdd0) "
                       "tests pass unchanged, and remote readback returns both SHAs"),
  "negative_fixture": ("SBL_R6_CANDIDATE_EVIDENCE_BIND: an evidence branch whose commits mix "
                       "candidate code, or a readback that cannot confirm the pushed SHAs, fails "
                       "the round; PR#2 merge is NOT performed by this round (owner-only)"),
  "recovery_fixture": ("SBL_R6_CANDIDATE_EVIDENCE_BIND: a failed push or readback leaves local "
                       "checkpoints intact and the resume pointer in the closeout"),
  "raw_evidence_required": True,
  "independent_checker_required": True,
  "terminal_states": ["INDEPENDENT_CASE_PASS"],
 },
]
for edge in NEW_EDGES:
    if edge["acceptance_id"] not in existing:
        contract["acceptance"].append(edge)

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
    receipts.append({"stage": name, "rc": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]})
    print(f"{name}: rc={proc.returncode}")
    if proc.returncode != 0:
        print(proc.stdout[-3000:], file=sys.stderr)
        print(proc.stderr[-2000:], file=sys.stderr)
        rc_total = proc.returncode
        break
(OUTDIR / "COMPILER_RECEIPT.json").write_text(
    json.dumps({"contract": str(OUT), "compiler": str(COMPILER), "stages": receipts}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8")
# read back the receipt verdict
rec = json.loads((OUTDIR / "COMPILER_RECEIPT.json").read_text(encoding="utf-8"))
compile_stage = receipts[-1]
print("last stage:", compile_stage["stage"], "rc:", compile_stage["rc"])
sys.exit(rc_total)
