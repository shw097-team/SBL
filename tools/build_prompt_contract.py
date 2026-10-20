"""Generate the SBL v0.1 C0..C9 prompt contract (CAPC-PROMPT-CONTRACT/1).

Author-side generator. It validates nothing itself: the canonical
prompt_contract_compiler.py is the only validator (lint/activation/acceptance/compile).
Structure is derived from references/prompt-contract.schema.json (additionalProperties:false),
so role enums, lifecycle enums and digest patterns are schema-legal.

Every digest is recomputed from bytes on disk at build time, so the contract's package
binding is reproducible from the corpus and the control plane.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:/Projects/Agent_Workspace/SBL")
OUT = ROOT / "contracts" / "SBL_C0_C9_CONTRACT.json"
LOG = ROOT / "evidence" / "compiler"
COMPILED = ROOT / "contracts" / "compiled"
VERIFY = ROOT / "evidence" / "source" / "SOURCE_VERIFY.json"

CORPUS = Path(r"C:/Projects/Agent_Workspace/_sbl_src_mirror")
DOCDIR = CORPUS / "SBL_PIPD-LS-PKG"
HGK_AGENTS = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS/AGENTS.md")
HGK_REGISTRY = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS/config/lane-routing-registry.yaml")
FABRIC_AGENTS = Path(r"C:/Projects/Agent_Workspace/Fabric/FABRIC/AGENTS.md")
COMMANDER = Path(
    r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/"
    r"attachments/SBL／HERMES／HG-KSEOS／Fabric 完整指揮薄 PROMPT v2-3.md"
)
COMPILER = Path(
    r"C:/Projects/Agent_Workspace/知識庫/實作相關DOC/HG-KSEOS/construction-acceptance-prompt-compiler/"
    r"construction-acceptance-prompt-compiler/scripts/prompt_contract_compiler.py"
)

DOC = "SBL_PIPD-LS-PKG"

ACTIVE = [
    ("SBL_SHARED_CORE", f"{DOC}_DOC-04#one-core"),
    ("SBLM01_GOAL_INTAKE", f"{DOC}_DOC-04#modules"),
    ("SBLM02_GUIDED_SPECIFICATION", f"{DOC}_DOC-04#modules"),
    ("SBLM03_GOVERNED_ROUTING", f"{DOC}_DOC-04#modules"),
    ("SBLM04_GOVERNED_BUILD_BRIDGE", f"{DOC}_DOC-05#ecp"),
    ("SBLM05_EVIDENCE_VERIFICATION", f"{DOC}_DOC-08#tqaep"),
    ("SBLM06_BOUNDED_REPAIR", f"{DOC}_DOC-08#repair"),
    ("TPM_SP", f"{DOC}_DOC-04#three-sp"),
    ("COMMANDER_SP", f"{DOC}_DOC-04#three-sp"),
    ("EXTERNAL_CHALLENGE_SP", f"{DOC}_DOC-04#three-sp"),
    ("MODE_STANDALONE", f"{DOC}_DOC-04#modes"),
    ("MODE_PREW3_SHADOW", f"{DOC}_DOC-04#modes"),
    ("GJ01_CLI_TOOL", f"{DOC}_DOC-01#journeys"),
    ("GJ02_BROWNFIELD_PATCH", f"{DOC}_DOC-05#repocontext"),
    ("GJ03_SKILL_AGENT_BRIDGE", f"{DOC}_DOC-10#hosts"),
    ("GKNOW_RETRIEVAL", f"{DOC}_DOC-10#gknow"),
    ("PUBLIC_CANDIDATE_PUBLICATION", f"{DOC}_DOC-08#independent"),
]

DEFERRED = [("MODE_SWOFCON", f"{DOC}_DOC-04#modes")]

DELIVERABLES = ["DELIV_PRODUCT_TREE", "DELIV_PUBLIC_CANDIDATE", "DELIV_HANDOVER_BUNDLE"]

LIFECYCLE_KEYS = ["identify", "pin", "install_materialize", "configure", "discover", "bind", "route",
                  "effective_load", "doctor_health", "positive_pilot", "negative_security", "fallback",
                  "rollback_uninstall", "independent_qualification", "certify", "enable"]

GATES = [
    ("G-COMPILER", "canonical CAPC compiler returns PROMPT_COMPILE_PASS for these exact contract bytes",
     "prompt_contract_compiler.py lint|activation|acceptance|compile exit 0", "HERMES", True, "full", "PASS"),
    ("G-SOURCE-FREEZE", "306 corpus files byte-hashed, 14 normative DOC digests recomputed, originals untouched",
     "python tools/verify_source.py --verify", "HERMES", False, "full", "PASS"),
    ("G-KNOW", "G-KNOW local index answers a source-bound query with an exact locator and refuses an unanswerable one",
     "python -m sbl_core.gknow --query <q> --json", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
    ("G-CORE-MODULES", "Shared Core plus SBLM01..06 import and execute with typed refusals",
     "python -m pytest tests/test_core_modules.py -q", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
    ("G-SP-ISOLATION", "three SP manifests are permission-separated and a maker cannot self-sign the challenge verdict",
     "python -m pytest tests/test_sp_isolation.py -q", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
    ("G-GJ01-CLI", "install -> add -> list --json -> restart -> uninstall with exact id readback and no residue",
     "python -m pytest tests/e2e/test_gj01_cli.py -q", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
    ("G-GJ02-PATCH", "brownfield patch limited to the write-set, red then green, rollback to the baseline digest",
     "python -m pytest tests/e2e/test_gj02_patch.py -q", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
    ("G-GJ03-BRIDGE", "skill manifest discovered, effective-load trace, trigger and non-trigger verdicts",
     "python -m pytest tests/test_gj03_bridge.py -q", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
    ("G-MODES-NOEFFECT", "PREW3_SHADOW reports NO_EFFECT; SWOF_CONNECTED refuses without a native ACK",
     "python -m pytest tests/test_modes.py -q", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
    ("G-SEC-SCAN", "secret/PII/path-traversal scan CLEAN over the published tree",
     "python tools/secret_scan.py --root .", "HERMES", True, "full", "CLEAN"),
    ("G-PUBLIC-READBACK", "the public repo exists and the remote ref equals the published candidate SHA",
     "git ls-remote origin refs/heads/<candidate-branch>", "HERMES-OPS", False, "full", "PASS"),
    ("G-INDEPENDENT-CHECKER", "checker lane served by gpt-6.1-sol read-only with require_arm == served_arm and a raw verdict",
     "hgk-lane-dispatch.py --lane VERIFY_SECURITY --require-arm openai-codex/gpt-6.1-sol --force-rank <rank>",
     "HERMES-OPS", True, "full", "PASS"),
    ("G-ROLLBACK", "uninstall/rollback restores the pre-round state and leaves no residue",
     "python -m pytest tests/e2e/test_rollback.py -q", "CODEX-EXECUTE-DS41", True, "affected-only", "PASS"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def doc_digests() -> list[dict]:
    rows = []
    for i in range(14):
        p = DOCDIR / f"{DOC}_DOC-{i:02d}.md"
        rows.append({"doc": f"DOC-{i:02d}", "path": p.as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)})
    return rows


def aggregate(rows: list[dict]) -> str:
    payload = "\n".join(sorted(r["sha256"] for r in rows)) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def lifecycle() -> dict:
    return {k: "OPEN" for k in LIFECYCLE_KEYS}


def build() -> tuple[dict, dict]:
    docs = doc_digests()
    pkg = aggregate(docs)
    hgk_agents_sha = sha(HGK_AGENTS)
    hgk_registry_sha = sha(HGK_REGISTRY)
    fabric_sha = sha(FABRIC_AGENTS)
    commander_sha = sha(COMMANDER)
    compiler_sha = sha(COMPILER)

    families = [
        "SBL_PIPD_LS_PKG_DOCS",
        "HGK_CONTROL_PLANE",
        "FABRIC_CONTRACT_SURFACE",
        "COMMANDER_PROMPT_V2",
        "CAPC_COMPILER_BUNDLE",
    ]

    reviewed = [
        {"source_family": "SBL_PIPD_LS_PKG_DOCS", "source_id": "SRC-SBL-DOC00-13",
         "locator": f"{DOCDIR.as_posix()}/{DOC}_DOC-00.md .. DOC-13.md (14 files, byte hashed)",
         "sha256": pkg, "role": "NORMATIVE", "critical": True},
        {"source_family": "HGK_CONTROL_PLANE", "source_id": "SRC-HGK-AGENTS",
         "locator": f"{HGK_AGENTS.as_posix()} + config/lane-routing-registry.yaml",
         "sha256": hgk_agents_sha, "role": "NORMATIVE", "critical": True},
        {"source_family": "FABRIC_CONTRACT_SURFACE", "source_id": "SRC-FABRIC-AGENTS",
         "locator": FABRIC_AGENTS.as_posix(),
         "sha256": fabric_sha, "role": "SUPPORT", "critical": False},
        {"source_family": "COMMANDER_PROMPT_V2", "source_id": "SRC-COMMANDER-V2",
         "locator": "attachments/SBL／HERMES／HG-KSEOS／Fabric 完整指揮薄 PROMPT v2-3.md",
         "sha256": commander_sha, "role": "NORMATIVE", "critical": True},
        {"source_family": "CAPC_COMPILER_BUNDLE", "source_id": "SRC-CAPC-COMPILER",
         "locator": COMPILER.as_posix(),
         "sha256": compiler_sha, "role": "NORMATIVE", "critical": True},
    ]

    normative_claims = [
        {"claim_id": "NC-01",
         "text": "DOC-00..DOC-13 are the product authority surface for SBL v0.1; scope outside them is not invented by this round.",
         "source_ids": ["SRC-SBL-DOC00-13"], "locators": [f"{DOC}_DOC-00..DOC-13"]},
        {"claim_id": "NC-02",
         "text": "HG-KSEOS is the sole normative control plane for task admission, effects and evidence; no second control plane is created.",
         "source_ids": ["SRC-HGK-AGENTS"], "locators": [HGK_AGENTS.as_posix()]},
        {"claim_id": "NC-03",
         "text": "The round is admitted only if the canonical CAPC compiler returns PROMPT_COMPILE_PASS on exactly these contract bytes.",
         "source_ids": ["SRC-CAPC-COMPILER"], "locators": [COMPILER.as_posix()]},
    ]

    execution_scope, readiness, acceptance = [], [], []
    for cap, loc in ACTIVE:
        execution_scope.append({
            "capability": cap,
            "source_disposition": "SOURCE_REQUIRED",
            "current_execution_disposition": "ACTIVE_REQUIRED",
            "current_profile_selected": True,
            "canonical_flow_referenced": True,
            "automatic_route_target": True,
            "user_experience_required": True,
            "runtime_required_now": True,
            "action": "INSTALL",
            "source_locators": [loc],
            "external_method": False,
            "control_authority": False,
        })
        readiness.append({
            "capability": cap,
            "required_now": True,
            "lifecycle": lifecycle(),
            "current_verdict": "NOT_READY",
            "work_required": [
                f"materialize {cap} runtime closure with typed errors",
                "positive + negative + security fixtures executed for real",
                "raw receipt plus a distinct-model independent checker verdict",
            ],
            "acceptance_ids": [f"ACC-{cap}"],
        })
        acceptance.append({
            "acceptance_id": f"ACC-{cap}",
            "subject_id": cap,
            "subject_type": "CAPABILITY",
            "source_locators": [loc],
            "runtime_required": True,
            "required_depth": "L3_INTEGRATION_RUNTIME",
            "positive_fixture": f"{cap}: real invocation produces the declared observable result",
            "negative_fixture": f"{cap}: wrong or unauthorised input is refused with a typed error, never silently accepted",
            "recovery_fixture": f"{cap}: bounded repair plus checkpoint resume after a confirmed defect",
            "raw_evidence_required": True,
            "independent_checker_required": True,
            "terminal_states": ["INDEPENDENT_CASE_PASS"],
        })

    for cap, loc in DEFERRED:
        execution_scope.append({
            "capability": cap,
            "source_disposition": "SOURCE_REQUIRED",
            "current_execution_disposition": "DEFERRED_SOURCE_BACKED",
            "current_profile_selected": False,
            "canonical_flow_referenced": False,
            "automatic_route_target": False,
            "user_experience_required": False,
            "runtime_required_now": False,
            "action": "DEFER",
            "source_locators": [loc],
            "external_method": False,
            "control_authority": False,
        })
        acceptance.append({
            "acceptance_id": f"ACC-{cap}",
            "subject_id": cap,
            "subject_type": "CAPABILITY",
            "source_locators": [loc],
            "runtime_required": False,
            "required_depth": "L1_SCHEMA_CONTRACT",
            "positive_fixture": f"{cap}: gate reports BLOCKED_EXTERNAL without a native ACK/Permit",
            "negative_fixture": f"{cap}: a claimed world effect without a native ACK is a refusal, never a pass",
            "recovery_fixture": f"{cap}: stays blocked and resumable; no synthetic ACK is fabricated",
            "raw_evidence_required": True,
            "independent_checker_required": True,
            "terminal_states": ["BLOCKED_EXTERNAL"],
        })

    for deliv in DELIVERABLES:
        acceptance.append({
            "acceptance_id": f"ACC-{deliv}",
            "subject_id": deliv,
            "subject_type": "DELIVERABLE",
            "source_locators": [f"{DOC}_DOC-08#independent"],
            "runtime_required": False,
            "required_depth": "L3_INTEGRATION_RUNTIME",
            "positive_fixture": f"{deliv}: produced by the round and read back from disk/remote",
            "negative_fixture": f"{deliv}: absent or partially written artefact is reported absent, never assumed",
            "recovery_fixture": f"{deliv}: regenerated from source plus checkpoint with a digest comparison",
            "raw_evidence_required": True,
            "independent_checker_required": True,
            "terminal_states": ["INDEPENDENT_CASE_PASS"],
        })

    journeys = [
        {"journey_id": "GJ01_CLI_TOOL", "required": True,
         "user_goal": "Install a small CLI tool, add one item, and read it back after restarting",
         "expected_visible_result": "add prints an id; list --json shows the same id/title/status after restart; uninstall leaves nothing behind",
         "expected_automatic_behavior": ["install into an isolated user data dir", "persist state across restart",
                                         "report typed errors on duplicate/invalid input", "clean uninstall"],
         "expected_manual_behavior": [], "allowed_hitl": ["confirm data directory when ambiguous"],
         "required_capabilities": ["GJ01_CLI_TOOL", "SBLM01_GOAL_INTAKE", "SBLM05_EVIDENCE_VERIFICATION"],
         "negative_behavior": ["reject empty title", "reject duplicate title with typed error",
                               "refuse uninstall when foreign files are present"],
         "failure_recovery": ["reinstall over a broken install", "restore data dir from backup"],
         "source_expectation_ids": ["EXP-GJ01"], "source_locators": [f"{DOC}_DOC-01#journeys"]},
        {"journey_id": "GJ02_BROWNFIELD_PATCH", "required": True,
         "user_goal": "Have a scoped defect patched inside an existing repository without touching unrelated code",
         "expected_visible_result": "diff limited to the declared write-set; failing test turns green; affected regression clean; rollback restores the exact baseline",
         "expected_automatic_behavior": ["bind RepoContext + HEAD", "produce red then green",
                                         "run affected regression", "emit rollback pointer"],
         "expected_manual_behavior": ["user approves scope expansion when the write-set must grow"],
         "allowed_hitl": ["scope expansion approval"],
         "required_capabilities": ["GJ02_BROWNFIELD_PATCH", "SBLM04_GOVERNED_BUILD_BRIDGE", "SBLM06_BOUNDED_REPAIR"],
         "negative_behavior": ["refuse writes outside the write-set", "refuse stale HEAD binding"],
         "failure_recovery": ["rollback by pointer", "resume from checkpoint"],
         "source_expectation_ids": ["EXP-GJ02"], "source_locators": [f"{DOC}_DOC-05#repocontext"]},
        {"journey_id": "GJ03_SKILL_AGENT_BRIDGE", "required": True,
         "user_goal": "Use an agent skill that is discoverable, effectively loaded and refuses out-of-scope effects",
         "expected_visible_result": "skill is discovered and triggers on its intent, does not trigger on unrelated intents, and refuses unauthorised effects",
         "expected_automatic_behavior": ["register skill manifest", "effective load in host", "trigger/non-trigger routing"],
         "expected_manual_behavior": [], "allowed_hitl": ["provider-off confirmation"],
         "required_capabilities": ["GJ03_SKILL_AGENT_BRIDGE", "SBLM03_GOVERNED_ROUTING", "MODE_PREW3_SHADOW"],
         "negative_behavior": ["no trigger on unrelated intent", "refuse effect when provider is off"],
         "failure_recovery": ["unload skill with no residue"],
         "source_expectation_ids": ["EXP-GJ03"], "source_locators": [f"{DOC}_DOC-10#hosts"]},
    ]

    evidence = []
    for gid, predicate, probe, producer, tracked, rerun, terminal in GATES:
        evidence.append({
            "gate_id": gid,
            "predicate": predicate,
            "expected": terminal,
            "command_or_probe": probe,
            "raw_receipt_required": True,
            "producer": producer,
            "independent_checker": "CODEX-VERIFY-GPT61",
            "candidate_binding": {
                "head": "CANDIDATE_SHA" if tracked else "WORKTREE_OR_REMOTE_SHA",
                "package_sha256": pkg,
                "source_hashes": [r["sha256"] for r in docs] if gid == "G-SOURCE-FREEZE" else [pkg],
            },
            "tracked_subject": tracked,
            "rerun_rule": rerun,
            "invalidation": ["candidate drift", "raw receipt missing", "self-signed verdict"],
            "terminal_verdict": terminal,
            "runtime_pass_allowed": True,
            "claim_level": "LOCAL",
        })

    contract = {
        "schema": "CAPC-PROMPT-CONTRACT/1",
        "task_id": "SBL-PIPDLS-20261020-R2-NEW_IMPLEMENTATION",
        "source_scan": {
            "required_source_families": families,
            "reviewed": reviewed,
            "missing": [],
            "normative_claims": normative_claims,
        },
        "intent": {
            "goal": ("Build SBL / SpecBuild Loop v0.1 in the authorized target root as a real installable, "
                     "operable, testable, restartable, uninstallable and rollbackable product: one Shared Core, "
                     "six modules SBLM01..SBLM06, three permission-separated SPs, three modes, three golden "
                     "journeys, a source-bound G-KNOW layer, and a public candidate plus scrubbed evidence for "
                     "independent external acceptance."),
            "user_expected_outcome": "A working product tree with reproducible raw evidence and a public candidate an external checker can re-verify from bytes.",
            "user_expected_experience": "Run each golden journey end to end from the CLI without reading internal design documents; every failure is typed and recoverable.",
            "explicit_constraints": [
                "HG-KSEOS remains the only control plane; no second orchestrator, task DB or evidence authority",
                "maker != checker and the checker lane is read-only",
                "PLAN/VERIFY = openai-codex/gpt-6.1-sol medium; EXECUTE = opencode-go/deepseek-v4.1-flash through the Codex CLI lane",
                "candidate-only; no self-acceptance, no RELEASED, no PRODUCTION claim",
                "PREW3_SHADOW must produce NoEffect; SWOF_CONNECTED stays blocked without a native ACK/Permit",
                "no private corpus text and no credential value may enter the public repository",
                "SBL_MASTER_v2.0r1 and the PIPD native P4 package are absent from the mounted corpus; the absence is carried as TT and is not substituted by same-named material from another subject",
                "claim ceiling is LOCAL: only raw receipts from this host lift it, and only an external checker can grant acceptance",
            ],
            "non_goals": [
                "install all 386 donor technologies",
                "modify sealed HG-KSEOS or Fabric policy",
                "claim a SWOF world connection",
                "claim independent acceptance from the maker side",
                "publish private corpus content or credential material",
            ],
            "authorized_mutations": [
                "C:/Projects/Agent_Workspace/SBL (full tree)",
                "github.com/shw097-team/SBL candidate branches and scrubbed evidence",
                "HG-KSEOS Shared Spine records scoped to this project",
            ],
            "forbidden_mutations": [
                "HG-KSEOS and Fabric sealed policy",
                "the read-only source corpus root",
                "other repositories",
                "credential stores",
                "Oracles, RBWI and reducers",
            ],
            "expected_autonomy": "HIGH",
            "allowed_hitl": ["scope expansion", "credential or permission change", "release promotion",
                             "owner ruling on a TT/CR"],
            "requested_delivery": DELIVERABLES,
            "active_requirement_ids": [cap for cap, _ in ACTIVE],
            "claim_ceiling": "LOCAL",
        },
        "authority": {
            "sources": [
                {"id": "SRC-SBL-DOC00-13", "rank": "R1", "path": DOCDIR.as_posix(), "sha256": pkg,
                 "locator": f"{DOC}_DOC-00.md .. {DOC}_DOC-13.md", "role": "NORMATIVE", "governs": True},
                {"id": "SRC-HGK-AGENTS", "rank": "R1", "path": HGK_AGENTS.as_posix(), "sha256": hgk_agents_sha,
                 "locator": "AGENTS.md control-plane rules", "role": "NORMATIVE", "governs": True},
                {"id": "SRC-HGK-REGISTRY", "rank": "R2", "path": HGK_REGISTRY.as_posix(), "sha256": hgk_registry_sha,
                 "locator": "config/lane-routing-registry.yaml", "role": "STATE_EVIDENCE", "governs": False},
                {"id": "SRC-COMMANDER-V2", "rank": "R1",
                 "path": "attachments/SBL／HERMES／HG-KSEOS／Fabric 完整指揮薄 PROMPT v2-3.md",
                 "sha256": commander_sha, "locator": "commander prompt v2-3 machine header + TS00..TS19",
                 "role": "NORMATIVE", "governs": True},
                {"id": "SRC-FABRIC-AGENTS", "rank": "R3", "path": FABRIC_AGENTS.as_posix(), "sha256": fabric_sha,
                 "locator": "Fabric governance and assurance contract surface", "role": "SUPPORT", "governs": False},
                {"id": "SRC-CAPC-COMPILER", "rank": "R1", "path": COMPILER.as_posix(), "sha256": compiler_sha,
                 "locator": "scripts/prompt_contract_compiler.py + references/prompt-contract.schema.json",
                 "role": "NORMATIVE", "governs": True},
            ],
            "conflicts": [],
            "missing_sources": [],
            "native_control_plane_ids": ["HG-KSEOS"],
            "current_control_plane_id": "HG-KSEOS",
        },
        "changeset": {
            "class": "NEW_IMPLEMENTATION",
            "baseline_required": True,
            "baseline_verified": True,
            "reuse_prior_pass": False,
            "affected_domains": ["product-code", "tests", "evidence", "publication"],
            "affected_files": ["sbl_core/", "sbl_sp/", "sbl_cli/", "skills/", "tests/", "tools/",
                               "evidence/", "openspec/", ".github/"],
            "must_not_reopen": ["HG-KSEOS sealed policy", "Fabric sealed contracts", "the read-only source corpus",
                                "other repositories", "Oracles, RBWI and reducers"],
            "scope_expansion_requires_hitl": True,
            "tracked_mutation": True,
            "product_mutation_allowed": True,
        },
        "execution_scope": execution_scope,
        "runtime_readiness": readiness,
        "journeys": journeys,
        "acceptance": acceptance,
        "evidence": evidence,
        "termination": {
            "terminal_states": ["COMPLETED_ACCEPTED"],
            "non_terminal_pause": ["PAUSED_REMEDIABLE", "BLOCKED", "STOP_ESCALATE", "TEMP_CLOSED",
                                   "BLOCKED_EXTERNAL", "BLOCKED_HITL"],
            "checkpoint_required": True,
            "checkpoint_fields": ["task_id", "source_hashes", "current_candidate", "completed_gates",
                                  "open_gates", "next_work_order", "rollback_pointer"],
            "retry_budget": 3,
            "rollback_pointer_required": True,
        },
        "render_policy": {
            "control_corpus_restatement": False,
            "embedded_control_bodies": [],
            "max_prompt_chars": 20000,
            "output_language": "zh-TW",
        },
    }
    verify = {
        "schema": "SBL-SOURCE-VERIFY/1",
        "doc_count": len(docs),
        "aggregate_sha256": pkg,
        "aggregate_method": "sha256 of newline-joined SORTED per-document sha256 over the 14 DOC files",
        "docs": docs,
    }
    return contract, verify


def main() -> int:
    contract, verify = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(contract, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    VERIFY.parent.mkdir(parents=True, exist_ok=True)
    VERIFY.write_text(json.dumps(verify, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"contract written: {OUT} ({OUT.stat().st_size} bytes); package_sha256={verify['aggregate_sha256']}")

    steps = [["lint", str(OUT)], ["activation", str(OUT)], ["acceptance", str(OUT)],
             ["compile", str(OUT), "--out-dir", str(COMPILED)]]
    results = {}
    for step in steps:
        name = step[0]
        proc = subprocess.run([sys.executable, str(COMPILER), *step], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        (LOG / f"{name}.stdout.txt").write_text(proc.stdout, encoding="utf-8", newline="\n")
        (LOG / f"{name}.stderr.txt").write_text(proc.stderr, encoding="utf-8", newline="\n")
        results[name] = {"exit": proc.returncode}
    print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
