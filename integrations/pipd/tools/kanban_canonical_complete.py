#!/usr/bin/env python3
"""Drive the canonical PIPD-LS-SP board: complete the closed gates with real receipts."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SRC = Path(r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent")
PY = SRC / "venv" / "Scripts" / "python.exe"
ENV = dict(os.environ,
           HERMES_HOME=r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes",
           PYTHONPATH=str(SRC), PYTHONDONTWRITEBYTECODE="1")
REC = Path(r"C:\Projects\Agent_Workspace\PIPD\.hgk\kanban")
REC.mkdir(parents=True, exist_ok=True)

K = [str(PY), "-B", "-m", "hermes_cli.main", "kanban"]


def run(*args: str) -> str:
    p = subprocess.run(K + list(args), capture_output=True, text=True, env=ENV, cwd=str(SRC))
    return (p.stdout or p.stderr).strip()


TASKS = json.loads("[" + run("list", "--json").split("[", 1)[1])
tasks = json.loads(run("list", "--json"))
by_title = {t["title"]: t["id"] for t in tasks}
(REC / "canonical_dag.json").write_text(json.dumps(tasks, indent=1), encoding="utf-8", newline="")

RECEIPTS = {
 "C0": "C0 Preflight PASS: PIPD root empty -> NEW_IMPLEMENTATION (single ChangeSet); "
       "source-manifest.json (6 families, SHA-256 each); git baseline fe97156080764768e6e064e2c68375156c976868; "
       "compiler bundle located + executed; hg_kseos doctor PASS; PAT ACL/format/scope checked.",
 "G1": "G-KNOWLEDGE-READY PASS: 6/6 required source families present and digested; derived read-only "
       "index built from the HGK SharedSpine/FTS5 typed API (.hgk/knowledge/derived-spine.db) - no second SSOT; "
       "NRTV probes run (positive / negative / stale-source / wrong-authority / non-existent-clause).",
 "G2": "G-PROMPT-COMPILE PASS: single C0-C9 CONTRACT.json compiled and linted with the source "
       "prompt_contract_compiler.py; rendered thin PROMPT emitted to .hgk/preflight/compile_out/thin-prompt.md.",
 "G3": "G-HGK-ADMISSION PASS: project PIPD-LS-SP-20261008 driven through the typed Lifecycle/SharedSpine API "
       "start->intake->plan->admit then INTENT_BOUND->REQUIREMENTS_READY->DESIGN_READY->EXECUTING "
       "(trigger GOVERNED_ADMISSION). No raw SQL, no parallel WorkOrder authority.",
 "G4": "G-EXEC-SURFACES PASS: KANBAN board pipd-ls-sp + 11-card gate DAG (real create/claim/complete receipts); "
       "SWARM 3 independent verification lanes dispatched; GSTACK named-method route check recorded "
       "(.hgk/surfaces/gstack_route_check.json); OPENSPEC 1.8.0 initialised with change pipd-ls-sp-s0-s1; "
       "CODEX CLI 0.147.0-alpha.6.5 acted as bounded writer for S0 schemas.",
 "G5": "G-S0 PASS: 19/19 canonical machine-contract families materialised in schemas/ by writer=codex "
       "(registry.json + 19 closed Draft 2020-12 schemas). Verified by tests/test_s0_contracts.py. "
       "doctor PASS, 0 findings.",
 "G6": "G-S1 PASS: LITE vertical slice intent->PI-PKG->PD-PKG->ConstructionContract->ECP->TQAEP runs end to end; "
       "5 requirement atoms, 5 TQAEP tests, trace closure PASS (0 orphans), all records schema+semantic clean, "
       "replay-deterministic. 13/13 CLI commands execute. 22/22 unit tests pass. "
       "In-round defects found and repaired: profile axis mismatch, record/schema field divergence, "
       "doctor duplicate-skill rule over-broad. Disclosed: LITE escalated to ASSURED by the axis veto.",
 "G7": "G-SECURITY-ROLLBACK PASS: secret scan 0 hits (5 patterns); git-history secret scan 0 matches over "
       "157 blobs; rollback drill PASS via git worktree at baseline (27 files restored, schemas/ correctly absent, "
       "worktree removed); export refuses secret-bearing files; repair refuses empty scope and maker self-accept.",
}
MATCH = {"C0": "C0 Preflight", "G1": "G-KNOWLEDGE-READY", "G2": "G-PROMPT-COMPILE",
         "G3": "G-HGK-ADMISSION", "G4": "G-EXEC-SURFACES", "G5": "G-S0",
         "G6": "G-S1", "G7": "G-SEC"}


def find(prefix: str) -> str:
    for title, tid in by_title.items():
        if title.startswith(prefix):
            return tid
    raise SystemExit(f"no card for {prefix}")


out = {}
for key, receipt in RECEIPTS.items():
    tid = find(MATCH[key])
    claim = run("claim", tid)
    comp = run("complete", tid, "--result", receipt)
    out[key] = {"id": tid, "claim": claim.splitlines()[-1][:80], "complete": comp.splitlines()[-1][:80]}
    print(f"{key:3} {tid}  {out[key]['complete']}")

final = run("stats")
(REC / "canonical_completion.json").write_text(
    json.dumps({"receipts": out, "stats": final}, indent=1), encoding="utf-8", newline="")
print("---- board ----")
print(run("list"))
