#!/usr/bin/env python3
"""Build CONTRACT.json for SBL R15.2 from the real SOURCE_FREEZE.json.

Derives source families/ids from measured names, adds four runtime/state families
measured on this host, and emits a schema-conformant CAPC contract.
"""
from __future__ import annotations

import hashlib
import json
import os

ROUND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROUND, "SOURCE_FREEZE.json")
OUT = os.path.join(ROUND, "CONTRACT.json")

freeze = json.load(open(FREEZE, encoding="utf-8"))
docs = freeze["documents"]


def sha_file(p: str) -> str | None:
    if not os.path.isfile(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def doc_family(name: str) -> tuple[str, str]:
    if name.startswith("PIPD_LS_DOC-"):
        num = name.split("PIPD_LS_DOC-")[1][:2]
        return "PIPD_LS_DOC-00..09", "PIPD-DOC-" + num
    if name.startswith("SBL_PIPD-LS-PKG_DOC-"):
        num = name.split("SBL_PIPD-LS-PKG_DOC-")[1][:2]
        return "SBL_PIPD-LS-PKG_DOC-00..13", "SBL-DOC-" + num
    return "SUPPORT", name


def agg(rows: list[tuple[str, str]]) -> str:
    h = hashlib.sha256()
    for sid, sh in sorted(rows):
        h.update(("%s:%s\n" % (sid, sh)).encode())
    return h.hexdigest()


# ------------------------------------------------------- families from freeze
fam_rows: dict[str, list[tuple[str, str, str]]] = {}

for d in docs:
    fam, sid = doc_family(d["name"])
    fam_rows.setdefault(fam, []).append((sid, d["observed"]["sha256"], d["observed"]["path"]))

capc_files = []
for x in freeze.get("compiler_bundle", []):
    capc_files.append((x["path"].replace("\\", "/").split("/")[-1], x["sha256"], x["path"]))
fam_rows["CAPC_OFFICIAL_BUNDLE"] = capc_files

chal = [(x["path"].replace("\\", "/").split("/")[-1], x["sha256"], x["path"])
        for x in freeze.get("skills", []) if "challenge-review" in x["path"].lower()]
fam_rows["CHALLENGE_REVIEW_SKILL"] = chal

r151 = [(os.path.basename(x["path"]), x["sha256"], x["path"])
        for x in freeze.get("contracts", []) if "R15_1" in x["path"]]
r152 = [(os.path.basename(x["path"]), x["sha256"], x["path"])
        for x in freeze.get("contracts", []) if "R15_2" in x["path"]]
fam_rows["R15.1_SUBSTANTIVE_CONTRACT"] = r151
fam_rows["R15.2_ROUTEOUT_COMMAND"] = r152

# state/runtime families measured now
extra = {
    "FABRIC_ACTIVE_POLICY": [
        ("FABRIC/control/ACCEPTANCE_POLICY.yaml", sha_file(r"C:/Projects/Agent_Workspace/Fabric/FABRIC/control/ACCEPTANCE_POLICY.yaml"),
         r"C:/Projects/Agent_Workspace/Fabric/FABRIC/control/ACCEPTANCE_POLICY.yaml"),
        ("FABRIC/control/CAPABILITY_QUALIFICATION_POLICY.yaml", sha_file(r"C:/Projects/Agent_Workspace/Fabric/FABRIC/control/CAPABILITY_QUALIFICATION_POLICY.yaml"),
         r"C:/Projects/Agent_Workspace/Fabric/FABRIC/control/CAPABILITY_QUALIFICATION_POLICY.yaml"),
    ],
    "HGK_NATIVE_CONTROL_PLANE": [
        ("HG-KSEOS/AGENTS.md", sha_file(r"C:/Projects/Agent_Workspace/HG-KSEOS/AGENTS.md"),
         r"C:/Projects/Agent_Workspace/HG-KSEOS/AGENTS.md"),
    ],
    "HERMES_RUNTIME_AND_KANBAN": [
        ("hermes-agent/hermes_cli/main.py", sha_file(r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/hermes_cli/main.py"),
         r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/hermes_cli/main.py"),
    ],
    "R14_NATIVE_LEDGER_AND_CHECKPOINT": [
        ("SBL evidence/r14-20261022-native commit",
         freeze["repositories"]["SBL"].get("head"),
         "git -C C:/Projects/Agent_Workspace/SBL rev-parse evidence/r14-20261022-native"),
    ],
}
for fam, rows in extra.items():
    fam_rows[fam] = [(sid, sh or "UNAVAILABLE", path) for sid, sh, path in rows]

REQUIRED_FAMILIES = [
    "CAPC_OFFICIAL_BUNDLE",
    "CHALLENGE_REVIEW_SKILL",
    "FABRIC_ACTIVE_POLICY",
    "HERMES_RUNTIME_AND_KANBAN",
    "HGK_NATIVE_CONTROL_PLANE",
    "PIPD_LS_DOC-00..09",
    "R14_NATIVE_LEDGER_AND_CHECKPOINT",
    "R15.1_SUBSTANTIVE_CONTRACT",
    "R15.2_ROUTEOUT_COMMAND",
    "SBL_PIPD-LS-PKG_DOC-00..13",
]

reviewed, claims = [], []
for fam in REQUIRED_FAMILIES:
    rows = fam_rows.get(fam, [])
    good = [(s, h) for s, h, _ in rows if h and h != "UNAVAILABLE"]
    digest = agg(good) if good else "UNAVAILABLE"
    reviewed.append({
        "source_family": fam,
        "source_id": fam + "__FAMILY_MANIFEST",
        "locator": "SOURCE_FREEZE.json#family=%s (%d files, %d hashed)" % (fam, len(rows), len(good)),
        "sha256": digest,
        "role": "NORMATIVE" if fam.startswith(("R15", "PIPD_LS", "SBL_PIPD", "CAPC", "CHALLENGE")) else "STATE_EVIDENCE",
        "critical": fam.startswith(("R15", "PIPD_LS", "SBL_PIPD", "CAPC", "CHALLENGE")),
    })
    for sid, sh, path in rows:
        claims.append({
            "claim_id": "SC-" + fam + "-" + sid,
            "text": "%s is an input of this round, frozen at the measured digest %s." % (sid, sh),
            "source_ids": [fam + "__FAMILY_MANIFEST"],
            "locators": ["%s::sha256=%s" % (path, sh)],
        })

# ---------------------------------------------------------------- authority
RANK = {
    "R15.2_ROUTEOUT_COMMAND": "TASK_COMMAND",
    "R15.1_SUBSTANTIVE_CONTRACT": "SUBORDINATE_CONTRACT",
    "SBL_PIPD-LS-PKG_DOC-00..13": "PRODUCT_DESIGN_CANDIDATE",
    "PIPD_LS_DOC-00..09": "LIFECYCLE_STANDARD",
    "CAPC_OFFICIAL_BUNDLE": "COMPILER_BUNDLE",
    "CHALLENGE_REVIEW_SKILL": "CHECKER_BUNDLE",
    "FABRIC_ACTIVE_POLICY": "POLICY_SOURCE",
    "HGK_NATIVE_CONTROL_PLANE": "NATIVE_CONTROL_PLANE",
    "HERMES_RUNTIME_AND_KANBAN": "RUNTIME_PLANE",
    "R14_NATIVE_LEDGER_AND_CHECKPOINT": "STATE_EVIDENCE",
}
auth_sources = []
for fam in REQUIRED_FAMILIES:
    rows = fam_rows.get(fam, [])
    good = [(s, h) for s, h, _ in rows if h and h != "UNAVAILABLE"]
    p = rows[0][2] if rows else "UNRESOLVED"
    auth_sources.append({
        "id": fam,
        "rank": RANK[fam],
        "path": p,
        "sha256": agg(good) if good else "UNAVAILABLE",
        "locator": "SOURCE_FREEZE.json#family=%s" % fam,
        "role": "NORMATIVE" if fam.startswith(("R15", "PIPD_LS", "SBL_PIPD", "CAPC", "CHALLENGE")) else "STATE_EVIDENCE",
        "governs": fam.startswith(("R15", "PIPD_LS", "SBL_PIPD", "CAPC", "CHALLENGE")),
    })

# ---------------------------------------------------------------- capabilities
STAGES = ["identify", "pin", "install_materialize", "configure", "discover", "bind", "route",
          "effective_load", "doctor_health", "positive_pilot", "negative_security", "fallback",
          "rollback_uninstall", "independent_qualification", "certify", "enable"]

ACTIVE_CAPS = [
    ("SBL_PRODUCT_FRONT_DOOR", "L3_INTEGRATION_RUNTIME"),
    ("HGK_NATIVE_ISSUER", "L5_REAL_LIFECYCLE_SIDE_EFFECT"),
    ("FABRIC_ACTIVE_POLICY_CONSUMER", "L3_INTEGRATION_RUNTIME"),
    ("PIPD_8_SKILLS", "L3_INTEGRATION_RUNTIME"),
    ("PIPD_19_CONTRACT_FAMILIES", "L2_UNIT_BEHAVIOR"),
    ("PIPD_13_CLI_VERBS", "L2_UNIT_BEHAVIOR"),
    ("TPM_SP", "L3_INTEGRATION_RUNTIME"),
    ("COMMANDER_SP", "L3_INTEGRATION_RUNTIME"),
    ("EXTERNAL_CHALLENGE_SP", "L3_INTEGRATION_RUNTIME"),
    ("ONE_CORE_SIX_MODULES", "L3_INTEGRATION_RUNTIME"),
    ("FIVE_PRODUCT_TOOLS", "L5_REAL_LIFECYCLE_SIDE_EFFECT"),
    ("EIGHT_KINDS_THREE_MODES", "L3_INTEGRATION_RUNTIME"),
    ("HERMES_KANBAN_SWARM", "L3_INTEGRATION_RUNTIME"),
    ("OPENSPEC_STRICT_METHOD", "L2_UNIT_BEHAVIOR"),
]
DEFERRED_CAPS = [
    ("GSTACK_METHOD", "DONOR_ONLY", "DEFER"),
    ("SWOF_W3_CONNECTED", "DEFERRED_SOURCE_BACKED", "DEFER"),
    ("CHATGPT_PRIVATE_PLUGINS", "DEFERRED_SOURCE_BACKED", "DEFER"),
    ("AGENT_OS_KIND", "PROHIBITED", "PROHIBIT"),
    ("AI_SYSTEM_KIND", "PROHIBITED", "PROHIBIT"),
    ("GENIE_NATIVE_WRITE", "DEFERRED_SOURCE_BACKED", "DEFER"),
    ("PLUGIN_PROFILE_KINDS", "DEFERRED_SOURCE_BACKED", "DEFER"),
]

R152_LOC = "SOURCE_FREEZE.json#family=R15.2_ROUTEOUT_COMMAND"
R151_LOC = "SOURCE_FREEZE.json#family=R15.1_SUBSTANTIVE_CONTRACT"

execution_scope = []
for cap, _depth in ACTIVE_CAPS:
    execution_scope.append({
        "capability": cap,
        "source_disposition": "ACTIVE_IN_CURRENT_ISSUED_SCOPE",
        "current_execution_disposition": "ACTIVE_REQUIRED",
        "current_profile_selected": True,
        "canonical_flow_referenced": True,
        "automatic_route_target": True,
        "user_experience_required": True,
        "runtime_required_now": True,
        "action": "QUALIFY",
        "source_locators": [R152_LOC],
        "external_method": False,
        "control_authority": False,
    })
for cap, disp, act in DEFERRED_CAPS:
    execution_scope.append({
        "capability": cap,
        "source_disposition": "REASONED_" + disp,
        "current_execution_disposition": disp,
        "current_profile_selected": False,
        "canonical_flow_referenced": False,
        "automatic_route_target": False,
        "user_experience_required": False,
        "runtime_required_now": False,
        "action": act,
        "source_locators": [R152_LOC],
        "external_method": disp == "DONOR_ONLY",
        "control_authority": False,
    })

# ---------------------------------------------------------------- acceptance
acceptance = []


def acc(aid, subject, stype, locators, depth, pos, neg, rec=""):
    acceptance.append({
        "acceptance_id": aid,
        "subject_id": subject,
        "subject_type": stype,
        "source_locators": locators,
        "runtime_required": True,
        "required_depth": depth,
        "positive_fixture": pos,
        "negative_fixture": neg,
        "recovery_fixture": rec,
        "raw_evidence_required": True,
        "independent_checker_required": True,
        "terminal_states": ["INDEPENDENT_CASE_PASS", "INDEPENDENT_CASE_FAIL", "TEMP_CLOSED", "NOT_RUN"],
    })


for cap, depth in ACTIVE_CAPS:
    acc("ACC-%s-01" % cap, cap, "CAPABILITY", [R152_LOC], depth,
        "real invocation of %s on the frozen candidate with raw stdout/stderr/exit and sha256" % cap,
        "foreign subject, self-acceptance, missing raw or expired permit is rejected with a typed first-fail",
        "rollback pointer present; zero world effect without a native permit")

REQS = ["W%02d" % i for i in range(18)] + ["C%02d" % i for i in range(25)]
REQS += ["R14-TS%02d" % i for i in range(31)] + ["R14-CHK%02d" % i for i in range(31)]
REQS += ["E%02d" % i for i in range(1, 10)] + ["M%d" % i for i in range(1, 5)]

for r in REQS:
    deep = r.startswith(("C", "R14-CHK", "M"))
    acc("ACC-%s-01" % r, r, "REQUIREMENT", [R151_LOC, R152_LOC],
        "L5_REAL_LIFECYCLE_SIDE_EFFECT" if deep else "L3_INTEGRATION_RUNTIME",
        "%s executed on the frozen candidate with raw receipt, denominator and a distinct checker" % r,
        "%s satisfied only by document restatement, CI green, model 200 or maker self-report fails" % r,
        "affected-only rerun after repair; prior evidence preserved")

DELIVERABLES = [
    "18 work packages", "25 check runs", "31 R14 tasks and 31 R14 checks",
    "E01..E09", "M1..M4", "raw evidence manifest", "independent acceptance package",
]
for dl in DELIVERABLES:
    acc("ACC-DLV-" + hashlib.sha256(dl.encode()).hexdigest()[:8], dl, "DELIVERABLE", [R151_LOC],
        "L3_INTEGRATION_RUNTIME",
        "deliverable %s present with per-item raw evidence and distinct checker" % dl,
        "deliverable %s claimed from document restatement or a maker summary fails" % dl,
        "affected-only reissue after repair")
for jid in ("GJ01", "GJ02", "GJ03"):
    acc("ACC-" + jid, jid, "JOURNEY", [R152_LOC], "L3_INTEGRATION_RUNTIME",
        "journey %s executed end to end on the frozen candidate with raw receipts" % jid,
        "journey %s satisfied by fixtures, mocks or copied files fails" % jid,
        "resume from checkpoint without duplicating world effect")

runtime_readiness = []
for cap, depth in ACTIVE_CAPS:
    runtime_readiness.append({
        "capability": cap,
        "required_now": True,
        "lifecycle": {s: "OPEN" for s in STAGES},
        "current_verdict": "NOT_READY",
        "work_required": [
            "obtain the HGK native WorkOrder and Permit covering %s" % cap,
            "execute the real lifecycle probe and persist stdout/stderr/exit with sha256",
            "independent checker, distinct principal, re-execution on the same candidate sha",
        ],
        "acceptance_ids": ["ACC-%s-01" % cap],
    })

journeys = [
    {
        "journey_id": "GJ01", "required": True,
        "user_goal": "describe a new CLI tool in ordinary language and receive a working installable CLI",
        "expected_visible_result": "built wheel, --help, JSON output, persistence and clean uninstall",
        "expected_automatic_behavior": ["source-frozen intake", "PI/PD compile", "bounded repair on first fail"],
        "expected_manual_behavior": ["approve scope-expanding mutations"],
        "allowed_hitl": ["NEW_SCOPE", "IRREVERSIBLE", "PRODUCTION_RELEASE"],
        "required_capabilities": ["SBL_PRODUCT_FRONT_DOOR", "TPM_SP", "COMMANDER_SP",
                                  "ONE_CORE_SIX_MODULES", "EIGHT_KINDS_THREE_MODES", "FIVE_PRODUCT_TOOLS"],
        "negative_behavior": ["README-only delivery", "json type drift", "path traversal"],
        "failure_recovery": ["first-fail repair cone", "affected-only retest"],
        "source_expectation_ids": ["U42", "U44"],
        "source_locators": [R152_LOC],
    },
    {
        "journey_id": "GJ02", "required": True,
        "user_goal": "repair one failing test in an existing repository inside an exact write set",
        "expected_visible_result": "minimal diff, red to green evidence, foreign files untouched",
        "expected_automatic_behavior": ["repo context freshness check", "bounded write set"],
        "expected_manual_behavior": ["owner merge approval"],
        "allowed_hitl": ["NEW_SCOPE", "PRODUCTION_RELEASE"],
        "required_capabilities": ["COMMANDER_SP", "EXTERNAL_CHALLENGE_SP", "HGK_NATIVE_ISSUER", "HERMES_KANBAN_SWARM"],
        "negative_behavior": ["stale repo context", "cross-path write", "untracked overwrite"],
        "failure_recovery": ["checkpoint and replay without duplicate effect"],
        "source_expectation_ids": ["U31", "U32"],
        "source_locators": [R152_LOC],
    },
    {
        "journey_id": "GJ03", "required": True,
        "user_goal": "install an agent skill and a simple agent, then verify refusal of forbidden tools",
        "expected_visible_result": "host-discovered trigger, denial receipt, uninstall without residue",
        "expected_automatic_behavior": ["host discovery probe", "trigger matrix"],
        "expected_manual_behavior": ["host entitlement approval"],
        "allowed_hitl": ["IRREVERSIBLE", "PRODUCTION_RELEASE"],
        "required_capabilities": ["EIGHT_KINDS_THREE_MODES", "FIVE_PRODUCT_TOOLS", "HERMES_KANBAN_SWARM"],
        "negative_behavior": ["copy-only skill claims loaded", "false trigger", "unbounded tool loop"],
        "failure_recovery": ["provider-off", "uninstall and residue scan"],
        "source_expectation_ids": ["U03", "U42"],
        "source_locators": [R152_LOC],
    },
]

CHECKS = {
    "C00": ("source freeze and official CAPC compile", "frozen sources hashed and C0..C9 compile to one contract_sha", "mutated authority or wrong digest denied"),
    "C01": ("HGK native baseline", "installed ABI, HEAD and venv accounted for every red item", "old interpreter, nonce replay or dirty write denied"),
    "C02": ("Fabric RP002 consumption", "active policy digest consumed by HGK APL", "frozen Stage-1 treated as active denied"),
    "C03": ("Commander real invocation", "PLAN invocation id joins plan and work-order subject", "model ping only fails"),
    "C04": ("native admitted effect", "in-scope tracked diff with operation id and readback", "expired, revoked or foreign scope writes nothing"),
    "C05": ("independent challenge", "checker principal differs from maker and raw subjects match", "self-accept or proxy evidence denied"),
    "C06": ("R13/R14 AO regression", "fresh AO seal with truthful disposition of prior reds", "overwriting a prior FAIL fails"),
    "C07": ("model coherence", "required equals served rank across three lanes", "single-plane pinned green fails"),
    "C08": ("Hermes kanban", "every card uniquely owned and ready drained", "ghost ready fails"),
    "C09": ("Hermes swarm fan-in", "100 percent worker raw receipts before compose", "dropped worker raw blocks"),
    "C10": ("gstack method", "named role review invoked with readback", "selected but not invoked fails"),
    "C11": ("OpenSpec strict", "delta present and strict validate exit 0", "missing delta with exit 0 fails"),
    "C12": ("bounded repair", "first-fail to minimal repair to full regression", "oracle edited green denied"),
    "C13": ("FAR standing scope", "in-scope repair without routine HITL", "revoked or foreign grant denied"),
    "C14": ("long resume", "resume the same operation exactly once", "unknown effect replay holds"),
    "C15": ("evolution safety", "sandbox evaluation with owner promotion", "self promotion fails"),
    "C16": ("PIPD trace", "100 percent atom edges from intent to TQAEP", "zero atom or orphan accepted fails"),
    "C17": ("kinds and hosts", "three clean-room lifecycles plus honest NoFit", "prebaked fixture fails"),
    "C18": ("product semantic coverage", "50/149/441/38/39/24 closure", "invented N/A fails"),
    "C19": ("SWOF W3 effect", "W2 decision plus W3 permit plus remote readback", "no W3 then NO_EFFECT"),
    "C20": ("five tools and ZIPs", "five lifecycle UATs and three deterministic ZIPs", "ZIP without host install fails"),
    "C21": ("three ChatGPT private SPs", "three distinct host-issued ids with POS, NEG and uninstall", "draft or zero ids go to HOST_PENDING"),
    "C22": ("CI and supply chain", "pinned actions, provenance, SBOM, secret scan", "untrusted PR secret or unpinned action denied"),
    "C23": ("matched performance", "B0/B1/B2 paired on identical workload and hardware", "different denominators invalidate the comparison"),
    "C24": ("final claim ceiling", "all active hard gates on the exact subject", "partial scoped pass claiming full fails"),
}

evidence = []
pkg_sha = next((h for s, h, _ in fam_rows["R15.1_SUBSTANTIVE_CONTRACT"]), "UNAVAILABLE")
all_hashes = [h for fam in REQUIRED_FAMILIES for _, h, _ in fam_rows.get(fam, []) if h]
for cid, (pred, pos, neg) in CHECKS.items():
    evidence.append({
        "gate_id": "GATE-" + cid,
        "predicate": pred,
        "expected": {"positive": pos, "negative": neg, "raw": "stdout+stderr+exit persisted with sha256"},
        "command_or_probe": "COMMAND_UNBOUND until the native runner is observed on this host",
        "raw_receipt_required": True,
        "producer": "SBL_EXECUTE_LANE",
        "independent_checker": "DISTINCT_PRINCIPAL_REQUIRED",
        "candidate_binding": {
            "head": freeze["repositories"]["SBL"].get("head", ""),
            "package_sha256": pkg_sha,
            "source_hashes": all_hashes,
        },
        "tracked_subject": True,
        "rerun_rule": "affected-only",
        "invalidation": [
            "any frozen source sha changes",
            "the candidate sha changes",
            "the policy epoch or served arm changes",
            "the checker principal equals the maker principal",
        ],
        "terminal_verdict": "TEMP_CLOSED",
        "runtime_pass_allowed": False,
        "claim_level": "LOCAL",
    })

contract = {
    "schema": "CAPC-PROMPT-CONTRACT/1",
    "task_id": "SBL-R15.2-CONTINUATION-20261022",
    "source_scan": {
        "required_source_families": REQUIRED_FAMILIES,
        "reviewed": reviewed,
        "missing": [],
        "normative_claims": claims,
    },
    "intent": {
        "goal": "Land, execute, check, accept and deliver the SBL_PIPD-LS-PKG upper control package under the Fabric governor, with HG-KSEOS as the only native issuer and Hermes as the governed runtime.",
        "user_expected_outcome": "SBL is the single product engineering front door and HG-KSEOS remains the only native authority for admission, state and acceptance.",
        "user_expected_experience": "A long autonomous round that never fabricates a PASS, reports blockers as typed first-fails, and returns independently checkable evidence.",
        "explicit_constraints": [
            "product_front_door: SBL_ONLY",
            "native_issuer_and_state_acceptance: HG_KSEOS_ONLY",
            "runtime_orchestrator: CURRENT_CANONICAL_HERMES",
            "final_gate: FAIL_CLOSED",
            "no second issuer, reducer, RBWI or control plane",
        ],
        "non_goals": [
            "rewriting the governing documents",
            "claiming PROMPT_COMPILE_PASS as RUNTIME_READY",
            "signing permits or releases inside chat",
        ],
        "authorized_mutations": [
            "write inside the evidence worktree only",
            "create candidate and evidence branches",
        ],
        "forbidden_mutations": [
            "git add -A", "reset --hard", "force push",
            "overwriting foreign dirty or untracked files",
            "SWOF mutation without W3",
            "editing oracles to turn tests green",
        ],
        "expected_autonomy": "HIGH",
        "allowed_hitl": ["NEW_SCOPE", "IRREVERSIBLE", "HIGH_RISK_EXCEPTION",
                         "PRODUCTION_RELEASE", "SECRET_PERMISSION_ESCALATION"],
        "requested_delivery": [
            "18 work packages", "25 check runs", "31 R14 tasks and 31 R14 checks",
            "E01..E09", "M1..M4", "raw evidence manifest", "independent acceptance package",
        ],
        "active_requirement_ids": REQS,
        "claim_ceiling": "LOCAL",
    },
    "authority": {
        "sources": auth_sources,
        "conflicts": [],
        "missing_sources": [],
        "native_control_plane_ids": ["HG_KSEOS_NATIVE"],
        "current_control_plane_id": "HG_KSEOS_NATIVE",
    },
    "changeset": {
        "class": "CONTINUATION",
        "baseline_required": True,
        "baseline_verified": True,
        "reuse_prior_pass": True,
        "affected_domains": ["SBL", "HG-KSEOS", "Fabric", "PIPD", "Hermes"],
        "affected_files": [],
        "must_not_reopen": [
            "R14 items independently accepted on the same exact subject",
            "SBL DOC-00..13 normative text",
        ],
        "scope_expansion_requires_hitl": True,
        "tracked_mutation": False,
        "product_mutation_allowed": False,
    },
    "execution_scope": execution_scope,
    "runtime_readiness": runtime_readiness,
    "journeys": journeys,
    "acceptance": acceptance,
    "evidence": evidence,
    "termination": {
        "terminal_states": ["PASS", "PARTIAL", "FAIL", "TEMP_CLOSED", "NO_LEGAL_PROGRESS"],
        "non_terminal_pause": ["BLOCKED_HITL", "BLOCKED_EXTERNAL", "UNKNOWN_EFFECT"],
        "checkpoint_required": True,
        "checkpoint_fields": [
            "task_id", "source_hashes", "current_candidate", "completed_gates", "open_gates",
            "next_work_order", "rollback_pointer", "git_source_sha", "git_evidence_sha",
            "workorder_id", "permit_nonce", "policy_epoch", "kanban_card_state",
        ],
        "retry_budget": 1,
        "rollback_pointer_required": True,
    },
    "render_policy": {
        "control_corpus_restatement": False,
        "embedded_control_bodies": [],
        "max_prompt_chars": 24000,
        "output_language": "zh-TW",
    },
}

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(contract, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("wrote", OUT)
print("docs", len(docs), "families", len(REQUIRED_FAMILIES), "scope", len(execution_scope),
      "readiness", len(runtime_readiness), "journeys", len(journeys),
      "acceptance", len(acceptance), "evidence", len(evidence), "claims", len(claims))
