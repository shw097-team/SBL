#!/usr/bin/env python3
"""Build the single CAPC CONTRACT.json for SBL R15.2 (C0..C9 coverage).

Reads SOURCE_FREEZE.json (real measured hashes) and emits CONTRACT.json.
No fabricated evidence: every sha comes from the freeze file; every gate row
states the probe that a Native/AO checker must run.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

ROUND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROUND, "SOURCE_FREEZE.json")
WT = r"C:/Projects/Agent_Workspace/_r152_ev"

TASK_ID = "SBL-R15.2-CONTINUATION-20261022"


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def head() -> str:
    return subprocess.run(
        ["git", "-C", WT, "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()


freeze = json.load(open(FREEZE, encoding="utf-8"))
docs = freeze["documents"]
by_id: dict[str, dict] = {}


def _family(name: str) -> tuple[str, str]:
    """(family, source_id) for a normative document file name."""
    if name.startswith("SBL_PIPD-LS-PKG_DOC-"):
        return "SBL_DOC", "SBL-" + name.split("DOC-")[1][:2]
    if name.startswith("PIPD_LS_DOC-"):
        return "PIPD_DOC", "PIPD-" + name.split("DOC-")[1][:2]
    return "OTHER", name


reviewed = []
for d in docs:
    fam, sid = _family(d["name"])
    by_id[sid] = d
    reviewed.append(
        {
            "source_family": fam,
            "source_id": sid,
            "locator": d["observed"]["path"],
            "sha256": d["observed"]["sha256"],
            "role": "NORMATIVE",
            "critical": True,
        }
    )

for extra in freeze.get("contracts", []):
    reviewed.append(
        {
            "source_family": "R15_CONTRACT",
            "source_id": extra["name"],
            "locator": extra["path"],
            "sha256": extra["sha256"],
            "role": "NORMATIVE",
            "critical": True,
        }
    )
    by_id[extra["name"]] = {
        "name": extra["name"],
        "status": extra["status"],
        "observed": {"path": extra["path"], "sha256": extra["sha256"]},
    }

for extra in freeze.get("compiler_bundle", []):
    reviewed.append(
        {
            "source_family": "CAPC_BUNDLE",
            "source_id": "CAPC:" + os.path.basename(extra["path"]),
            "locator": extra["path"],
            "sha256": extra["sha256"],
            "role": "NORMATIVE",
            "critical": True,
        }
    )

for extra in freeze.get("skills", []):
    reviewed.append(
        {
            "source_family": "SKILL_BUNDLE",
            "source_id": "SKILL:" + extra["name"],
            "locator": extra["path"],
            "sha256": extra["sha256"],
            "role": "SUPPORT",
            "critical": True,
        }
    )

pkg_sha = by_id["R15.1_attachment"]["observed"]["sha256"]

# alias keys used by the tables below
_aliases = {}
for sid in list(by_id):
    if sid.startswith("SBL-"):
        _aliases["SBL_DOC-" + sid[4:]] = by_id[sid]
    elif sid.startswith("PIPD-"):
        _aliases["PIPD_DOC-" + sid[5:]] = by_id[sid]
for src, dst in (("R15.1_attachment", "R15.1"), ("R15.2_attachment", "R15.2"), ("R15.2_command", "R15.2")):
    if src in by_id:
        _aliases[dst] = by_id[src]
by_id.update(_aliases)

doc_loc = lambda sid: "%s::%s" % (by_id[sid]["observed"]["path"], sid)

WPS = [
    ("W00", "SourceFreeze + CAPC C0-C9 admission of the 24 normative documents", "C00"),
    ("W01", "HGK native conformance, issuer/lease/nonce/replay/expiry negatives", "C01"),
    ("W02", "Fabric ACTIVE policy consumed by HGK; policy digest six-edge readback", "C02"),
    ("W03", "PLAN lane真 Commander-SP invocation joined to TaskSpec/WorkOrder subject", "C03"),
    ("W04", "VERIFY_SECURITY真 Challenge-SP invocation by a distinct principal", "C05"),
    ("W05", "PIPD 8 skills / 19 contract families / 13 CLI verbs trace closure", "C16"),
    ("W06", "One Core 8 kinds x 3 modes; three kinds built, installed, used, removed", "C17"),
    ("W07", "FirstFail -> bounded repair cone -> new SHA -> regression -> checkpoint", "C12"),
    ("W08", "Cross-lane required/served rank, epoch and profile coherence", "C07"),
    ("W09", "Kanban claim/lease/heartbeat and swarm raw fan-in with recovery", "C08"),
    ("W10", "OpenSpec propose/strict validate on an admitted target; gstack route readback", "C11"),
    ("W11", "Bounded standing mandate -> typed recommendation -> native admissible repair", "C13"),
    ("W12", "SWOF W2 external acceptance -> W3 native admission -> first governed patch", "C19"),
    ("W13", "Five tools lifecycles; three deterministic ZIPs; three private plugin hosts", "C20"),
    ("W14", "50/149, 441=6+24+25+386, 38 surfaces, 39 mode gates denominator closure", "C18"),
    ("W15", "CI/supply-chain/security plus independent AO and lawful release control", "C22"),
    ("W16", "Matched B0/B1/B2 engineering-effectiveness measurement", "C23"),
    ("W17", "R14 31 TS / 31 CHK preserved and re-adjudicated on this candidate", "C06"),
]

CHECKS = {
    "C00": ("frozen source manifest matches the 24 pinned shas and the official C0-C9 compiler bundle is the one executed", "python3 scripts/prompt_contract_compiler.py lint|activation|acceptance|compile CONTRACT.json; sha256sum over the 24 documents", "a mutated authority digest or a foreign document must be rejected"),
    "C01": ("HGK native conformance on the installed ABI at this HEAD", "HGK owner conformance runner (COMMAND_UNBOUND until native readback)", "stale venv, replayed nonce and dirty-scope writes must be denied"),
    "C02": ("Fabric ACTIVE policy digest is consumed by HGK and not the frozen Stage-1 file", "Fabric active policy status + HGK APL consumer readback", "a tampered or inactive policy digest must be refused"),
    "C03": ("Commander-SP is really invoked in the PLAN lane and its subject joins the WorkOrder candidate", "registered PLAN invocation ABI; invocation_id in the receipt", "a bare model ping without an SP invocation must fail"),
    "C04": ("every effect carries a native WorkOrder/lease/permit with readback inside scope", "native issue/execute/readback ABI", "expired, revoked or foreign-scope writes must not land"),
    "C05": ("independent Challenge-SP/AO runs read-only on the frozen candidate with a distinct principal", "Codex CLI checker session pinned to the candidate sha", "self-acceptance or proxy raw evidence must be refused"),
    "C06": ("R14/R13 acceptance-officer results are reproduced or truthfully re-dispositioned", "existing R14 checker suite + fresh AO seal", "overwriting an earlier FAIL seal must fail"),
    "C07": ("required rank equals served rank for all three lanes with matching epoch digests", "lane registry/assignment/served-arm query", "pinning one rank while the others drift must fail"),
    "C08": ("kanban claims are unique, leases expire, ghost Ready cards are drained", "Hermes kanban board API: claim/heartbeat/cancel/ready", "a ghost Ready card or orphan claim must fail"),
    "C09": ("swarm fan-in consumes 100 percent of worker raw receipts", "worker spawn + fan-in manifest with per-worker sha", "dropping any worker raw receipt blocks synthesis"),
    "C10": ("named methods are truly selected and produce source-bound output", "installed gstack/OpenSpec --help then a real invocation", "selected-but-never-invoked must fail"),
    "C11": ("OpenSpec delta exists and strict validate really exits 0", "openspec list/validate --strict on the admitted change", "a missing delta with exit 0 must fail"),
    "C12": ("a real first-fail is repaired inside the bounded cone and regressed", "red/green run pair with pre/post candidate shas", "editing the oracle to green must be refused"),
    "C13": ("a bounded standing mandate lets ordinary repair proceed without routine HITL and cannot expand scope", "HGK grant verify + typed recommendation routing", "revoked or foreign grant auto-approval must fail"),
    "C14": ("checkpoint resume repeats no world effect", "kill/restart plus native effect readback", "unknown-effect replay must hold"),
    "C15": ("evolution candidates are qualified in a sandbox with an independent holdout", "held-out evaluation + owner promotion session", "self-promotion or oracle rewrite must fail"),
    "C16": ("PI/PD/ECP/TQAEP trace reaches every atom with no orphan", "pipd validate + independent trace orphan verifier", "zero-atom or orphan traces reported as pass must fail"),
    "C17": ("three non-prebaked kinds are installed, invoked and removed on a real host", "clean-room install/load/invoke/deny/uninstall per kind", "prebaked fixtures or fake host ids must fail"),
    "C18": ("product denominators close with source-bound identity: 50/149, 441, 38, 39, 8x3", "denominator registry + case runner", "invented N/A or aliased ids must fail"),
    "C19": ("SWOF W2/W3 admission is real and the first governed patch is read back", "SWOF owner decision + native permits + remote readback", "writing without W3 must be a critical invalid effect"),
    "C20": ("five tools ship with deterministic double-built ZIPs and real lifecycles", "build script double build + installer/doctor/uninstall", "a ZIP presented as a host install must fail"),
    "C21": ("three ChatGPT private plugins carry three distinct host-issued ids", "official host UI/API UAT records", "draft or zero ids must stay HOST_PENDING"),
    "C22": ("CI, provenance, SBOM, license and secret gates are pinned and enforced", "read existing workflows; pinned action shas; PR/merge_group status", "untrusted PR secrets or unpinned actions must fail"),
    "C23": ("B0/B1/B2 are compared on matched workload, hardware and budgets", "paired benchmark harness", "different denominators or hardware must invalidate the comparison"),
    "C24": ("the final claim ceiling matches exactly what the raw evidence supports", "independent full gate report + owner seal", "a scoped pass claimed as full must fail"),
}

E_MAP = {
    "E01": ("HGK baseline and native conformance", "C01"),
    "E02": ("PIPD/TPM/SPEC compilation", "C16"),
    "E03": ("Commander and Challenge SP lanes", "C03"),
    "E04": ("Native Fabric/Hermes wiring and effect", "C04"),
    "E05": ("real build and bounded repair", "C12"),
    "E06": ("five tools, host packaging and ZIPs", "C20"),
    "E07": ("independent security acceptance", "C05"),
    "E08": ("isolated SWOF-shaped dogfood", "C09"),
    "E09": ("W2/W3 first governed SWOF change", "C19"),
}

M_MAP = {
    "M1": ("Native chain ready: one subject flows PIPD -> Commander -> HGK -> Hermes/Codex -> Challenge", ["C01", "C02", "C03", "C04", "C05", "C06", "C07"]),
    "M2": ("Real standalone dogfood: three non-prebaked kinds built, repaired, independently checked", ["C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18"]),
    "M3": ("SWOF governed first mutation under owner W2/W3 plus HGK permits", ["C19"]),
    "M4": ("Full product release gate across every applicable kind, moment, host and denominator", ["C20", "C21", "C22", "C23", "C24"]),
}

reviewed_ids = [r["source_id"] for r in reviewed]

contract = {
    "schema": "PROMPT_CONTRACT/1",
    "task_id": TASK_ID,
    "source_scan": {
        "required_source_families": [
            "SBL_PIPD-LS-PKG_DOC-00..13",
            "PIPD_LS_DOC-00..09",
            "R15.1_SUBSTANTIVE_CONTRACT",
            "R15.2_ROUTEOUT_COMMAND",
            "CAPC_OFFICIAL_BUNDLE",
            "CHALLENGE_REVIEW_SKILL",
            "FABRIC_ACTIVE_POLICY",
            "HGK_NATIVE_CONTROL_PLANE",
            "R14_NATIVE_LEDGER_AND_CHECKPOINT",
            "HERMES_RUNTIME_AND_KANBAN",
        ],
        "reviewed": reviewed,
        "missing": [],
        "normative_claims": [
            {
                "claim_id": "NC-01-FRONT-DOOR",
                "text": "SBL is the single product front door; HG-KSEOS remains the only native admission, issuer, state and acceptance control plane.",
                "source_ids": ["R15.1", "R15.2", "SBL_DOC-00"],
                "locators": [doc_loc("R15.2"), doc_loc("SBL_DOC-00") + "::Mission"],
            },
            {
                "claim_id": "NC-02-NO-SECOND-ISSUER",
                "text": "No second issuer, reducer, RBWI, canonical plan IR or scheduler may be created; PIPD ECP constrains but never issues a token.",
                "source_ids": ["R15.1", "PIPD_DOC-05"],
                "locators": [doc_loc("R15.1") + "::12.1", doc_loc("PIPD_DOC-05")],
            },
            {
                "claim_id": "NC-03-CLAIM-CEILING",
                "text": "This round may only claim ROUTEOUT_CANDIDATE / consumer-side local verification; PROMPT_COMPILE_PASS is not RUNTIME_READY, INDEPENDENT_PASS, HOST_INSTALLED or RELEASED.",
                "source_ids": ["R15.1", "R15.2"],
                "locators": [doc_loc("R15.1") + "::3", doc_loc("R15.2") + "::16.5"],
            },
            {
                "claim_id": "NC-04-MODEL-SCHEME",
                "text": "PLAN uses gpt-6.1-sol (OpenAI OAuth served arm), EXECUTE uses opencode-go/minimax-m3.1-flash-free through Codex CLI, VERIFY_SECURITY uses gpt-6.1-sol through a distinct Codex CLI checker principal.",
                "source_ids": ["R15.2"],
                "locators": [doc_loc("R15.2") + "::model_scheme"],
            },
            {
                "claim_id": "NC-05-DENOMINATORS",
                "text": "Denominators stay 14 SBL DOC / 10 PIPD DOC / 50 parents / 149 children / 441 = 6 donors + 24 slots + 25 methods + 386 identities / 38 surfaces / 39 mode gates / 8 kinds x 3 modes / 16 moments / 3 journeys / 18 W / 25 C / 31 TS / 31 CHK.",
                "source_ids": ["R15.1", "SBL_DOC-01", "SBL_DOC-06", "SBL_DOC-12"],
                "locators": [doc_loc("R15.1") + "::4", doc_loc("SBL_DOC-01"), doc_loc("SBL_DOC-12")],
            },
            {
                "claim_id": "NC-06-FAIL-CLOSED",
                "text": "Missing native permission, host identity or raw evidence yields NO_EFFECT with a typed decision pack, never a fabricated pass.",
                "source_ids": ["R15.1", "R15.2"],
                "locators": [doc_loc("R15.1") + "::16.5", doc_loc("R15.2") + "::7"],
            },
        ],
    },
    "intent": {
        "goal": "Continue R14 in place and deliver the applicable SBL product capability for E01-E09 and M1-M4 under R15.1, with SBL as the single product front door and HG-KSEOS as the only native control plane.",
        "user_expected_outcome": "A natural-language need travels TPM/PIPD/PLAN/EXECUTE/Challenge and yields a new buildable CLI tool, agent skill and simple agent, with failures repaired in scope and independently re-verified.",
        "user_expected_experience": "One command surface, no routine HITL inside the standing mandate, honest NoFit receipts instead of silent holds, and every claim backed by reproducible raw evidence.",
        "explicit_constraints": [
            "product_front_door SBL_ONLY; native_issuer_and_state_acceptance HG_KSEOS_ONLY; runtime_orchestrator CURRENT_CANONICAL_HERMES; final_gate FAIL_CLOSED",
            "no force push, no git add -A, no reset --hard, no overwriting foreign dirty or untracked files",
            "no SWOF write before a real W3 admission; no Permit, PASS or Release signed in chat",
            "lane model bindings are carried by registry/assignment/pool, never by the session pin",
        ],
        "non_goals": [
            "rebuilding the foundation or re-running R14 work that is already sealed at the same sha",
            "installing donors that the source disposition marks deferred, rejected or quarantined",
            "claiming host installation, independent acceptance or release from local compile receipts",
            "creating a second orchestrator, scheduler, checkpoint store or oracle",
        ],
        "authorized_mutations": [
            "candidate and evidence branches inside github.com/shw097-team/SBL",
            "round artifacts under _governance/round-20261022-r15_2",
            "bounded product repairs inside the observed SBL working tree, on a new candidate sha",
        ],
        "forbidden_mutations": [
            "pushing to SBL main or any protected branch",
            "modifying the 24 frozen normative documents or the compiler bundle",
            "editing oracles, ledger history or prior FAIL seals to obtain green",
            "writing to SWOF, Fabric policy, HGK native store or another profile's governance data",
        ],
        "expected_autonomy": "Bounded standing mandate: ordinary, reversible, in-scope repair proceeds without asking; only scope expansion, irreversible effect, credential use, host identity or release requires a human decision.",
        "allowed_hitl": [
            "new scope or repo outside the standing grant",
            "irreversible or production world effect",
            "SWOF W3 domain acknowledgement and ChatGPT private host identity",
            "credential use and release approval",
        ],
        "requested_delivery": "Round artifacts, raw receipts, checkpoint and an honest per-gate verdict pushed to the SBL evidence branch for external acceptance.",
        "active_requirement_ids": [w[0] for w in WPS]
        + list(CHECKS.keys())
        + ["R14-TS%02d" % i for i in range(31)]
        + ["R14-CHK%02d" % i for i in range(31)]
        + list(E_MAP.keys())
        + list(M_MAP.keys())
        + ["GJ01", "GJ02", "GJ03"],
        "claim_ceiling": "ROUTEOUT_CANDIDATE_WITH_LOCAL_RAW_ONLY",
    },
    "authority": {
        "sources": [
            {
                "source_id": "R15.2",
                "locator": by_id["R15.2"]["observed"]["path"],
                "sha256": by_id["R15.2"]["observed"]["sha256"],
                "rank": 1,
                "current": True,
            },
            {
                "source_id": "R15.1",
                "locator": by_id["R15.1"]["observed"]["path"],
                "sha256": by_id["R15.1"]["observed"]["sha256"],
                "rank": 2,
                "current": True,
            },
            {
                "source_id": "SBL_DOC-00..13",
                "locator": by_id["SBL_DOC-00"]["observed"]["path"],
                "sha256": by_id["SBL_DOC-00"]["observed"]["sha256"],
                "rank": 3,
                "current": True,
            },
            {
                "source_id": "PIPD_LS_DOC-00..09",
                "locator": by_id["PIPD_DOC-00"]["observed"]["path"],
                "sha256": by_id["PIPD_DOC-00"]["observed"]["sha256"],
                "rank": 4,
                "current": True,
            },
            {
                "source_id": "HGK_NATIVE",
                "locator": "C:/Projects/Agent_Workspace/HG-KSEOS",
                "sha256": freeze["repositories"]["HG-KSEOS"]["head"],
                "rank": 1,
                "current": True,
            },
            {
                "source_id": "FABRIC_ACTIVE",
                "locator": "C:/Projects/Agent_Workspace/Fabric",
                "sha256": freeze["repositories"]["Fabric"]["head"],
                "rank": 1,
                "current": True,
            },
        ],
        "conflicts": [],
        "missing_sources": [],
        "native_control_plane_ids": ["HG-KSEOS", "FABRIC_ACTIVE_POLICY", "PIPD_CANONICAL_WRITER"],
        "current_control_plane_id": "HG-KSEOS",
    },
    "changeset": {
        "class": "CONTINUATION",
        "baseline_required": True,
        "baseline_verified": True,
        "reuse_prior_pass": True,
        "affected_domains": [
            "sbl_product_surface",
            "pipd_lifecycle_adapter",
            "hgk_native_admission",
            "fabric_policy_consumer",
            "hermes_runtime_orchestration",
            "evidence_and_acceptance",
        ],
        "affected_files": [
            "_governance/round-20261022-r15_2/",
            "sbl_core/",
            "sbl_cli/",
            "tests/",
        ],
        "must_not_reopen": [
            "R14 items already sealed DONE at the same subject and environment (21 DONE)",
            "the 24 frozen normative documents and the CAPC bundle",
            "R14 ledger history, prior FAIL seals and superseded candidate branches",
        ],
        "scope_expansion_requires_hitl": True,
        "tracked_mutation": True,
        "product_mutation_allowed": True,
    },
    "execution_scope": [],
    "runtime_readiness": [],
    "journeys": [],
    "acceptance": [],
    "evidence": [],
    "termination": {
        "terminal_states": ["PASS", "PARTIAL", "FAIL", "TEMP_CLOSED"],
        "non_terminal_pause": ["NO_LEGAL_PROGRESS", "HOST_PENDING", "AWAITING_OWNER_ACK"],
        "checkpoint_required": True,
        "checkpoint_fields": [
            "source_manifest_sha",
            "candidate_sha",
            "workorder_and_permit_state",
            "policy_epoch",
            "kanban_and_worker_state",
            "denominator_state",
            "open_tt_cr",
            "unknown_effects",
            "next_legal_cards",
        ],
        "retry_budget": 1,
        "rollback_pointer_required": True,
    },
    "render_policy": {
        "control_corpus_restatement": False,
        "embedded_control_bodies": [],
        "max_prompt_chars": 24000,
        "output_language": "zh-Hant-TW",
    },
}

# ---- execution_scope: one row per active capability edge -------------------
CAPS = [
    ("SBL_PRODUCT_FRONT_DOOR", "ACTIVE_REQUIRED", "R15.1 s3/s2", True, "USE_NATIVE", ["R15.1", "SBL_DOC-00"]),
    ("HGK_NATIVE_ISSUER", "ACTIVE_REQUIRED", "R15.1 s12.1", True, "USE_NATIVE", ["R15.1", "PIPD_DOC-05"]),
    ("FABRIC_ACTIVE_POLICY_CONSUMER", "ACTIVE_REQUIRED", "R15.1 s12.2", True, "QUALIFY", ["R15.1", "R15.2"]),
    ("PIPD_8_SKILLS", "ACTIVE_REQUIRED", "R15.1 s4.1", True, "QUALIFY", ["R15.1", "PIPD_DOC-03"]),
    ("PIPD_19_CONTRACT_FAMILIES", "ACTIVE_REQUIRED", "R15.1 s4.2", True, "QUALIFY", ["R15.1", "PIPD_DOC-03"]),
    ("PIPD_13_CLI_VERBS", "ACTIVE_REQUIRED", "R15.1 s4.3", True, "QUALIFY", ["R15.1", "PIPD_DOC-04"]),
    ("TPM_SP", "ACTIVE_REQUIRED", "R15.1 s3.2", True, "DESIGN", ["R15.1", "SBL_DOC-01"]),
    ("COMMANDER_SP", "ACTIVE_REQUIRED", "R15.1 s3.2", True, "DESIGN", ["R15.1", "SBL_DOC-04"]),
    ("EXTERNAL_CHALLENGE_SP", "ACTIVE_REQUIRED", "R15.1 s3.2", True, "DESIGN", ["R15.1", "SBL_DOC-11"]),
    ("ONE_CORE_SIX_MODULES", "ACTIVE_REQUIRED", "R15.1 s3.1", True, "DESIGN", ["R15.1", "SBL_DOC-01"]),
    ("FIVE_PRODUCT_TOOLS", "ACTIVE_REQUIRED", "R15.1 s3.3", True, "QUALIFY", ["R15.1", "SBL_DOC-12"]),
    ("EIGHT_KINDS_THREE_MODES", "ACTIVE_REQUIRED", "R15.1 s2.1/s2.2", True, "QUALIFY", ["R15.1", "SBL_DOC-01"]),
    ("HERMES_KANBAN_SWARM", "ACTIVE_REQUIRED", "R15.1 s12.5", True, "QUALIFY", ["R15.1", "R15.2"]),
    ("OPENSPEC_STRICT_METHOD", "ACTIVE_SELECTED", "R15.1 s8 METHOD-06", True, "QUALIFY", ["R15.1", "SBL_DOC-06"]),
    ("GSTACK_METHOD", "STANDBY", "R15.1 s7 SLOT-GT-01..04", False, "DEFER", ["R15.1", "SBL_DOC-06"], "gstack executable not installed on this host; source-bound projection only"),
    ("SWOF_W3_CONNECTED", "DEFERRED_SOURCE_BACKED", "R15.1 s13", False, "DEFER", ["R15.1", "SBL_DOC-13"], "requires SWOF owner W2 acceptance and a native W3 permit"),
    ("CHATGPT_PRIVATE_PLUGINS", "DEFERRED_SOURCE_BACKED", "R15.1 s14.2", False, "DEFER", ["R15.1", "SBL_DOC-12"], "requires three distinct host-issued plugin identities"),
    ("AGENT_OS_KIND", "PROHIBITED", "R15.1 s2.1", False, "PROHIBIT", ["R15.1", "SBL_DOC-01"]),
    ("AI_SYSTEM_KIND", "PROHIBITED", "R15.1 s2.1", False, "PROHIBIT", ["R15.1", "SBL_DOC-01"]),
    ("GENIE_NATIVE_WRITE", "PROHIBITED", "R15.1 s2.1", False, "PROHIBIT", ["R15.1", "SBL_DOC-01"]),
    ("PLUGIN_PROFILE_KINDS", "DEFERRED_SOURCE_BACKED", "R15.1 s2.1", False, "DEFER", ["R15.1", "SBL_DOC-06"]),
]

for row in CAPS:
    name, disp, loc, selected, action, srcs = row[:6]
    note = row[6] if len(row) > 6 else ""
    contract["execution_scope"].append(
        {
            "capability": name,
            "source_disposition": note or disp,
            "current_execution_disposition": disp,
            "current_profile_selected": selected,
            "canonical_flow_referenced": True,
            "automatic_route_target": action in ("USE_NATIVE", "QUALIFY", "INSTALL", "ENABLE"),
            "user_experience_required": action in ("USE_NATIVE", "QUALIFY", "INSTALL", "ENABLE"),
            "runtime_required_now": action in ("USE_NATIVE", "QUALIFY"),
            "action": action,
            "source_locators": [doc_loc(s) + "::" + loc for s in srcs],
            "external_method": name in ("OPENSPEC_STRICT_METHOD", "GSTACK_METHOD"),
            "control_authority": name in ("HGK_NATIVE_ISSUER", "FABRIC_ACTIVE_POLICY_CONSUMER"),
        }
    )

# ---- runtime_readiness -----------------------------------------------------
for name, disp, loc, selected, action, srcs in [c[:6] for c in CAPS]:
    if action in ("PROHIBIT", "DEFER"):
        continue
    acc = {
        "SBL_PRODUCT_FRONT_DOOR": ["C18"],
        "HGK_NATIVE_ISSUER": ["C01", "C04"],
        "FABRIC_ACTIVE_POLICY_CONSUMER": ["C02"],
        "PIPD_8_SKILLS": ["C16"],
        "PIPD_19_CONTRACT_FAMILIES": ["C16"],
        "PIPD_13_CLI_VERBS": ["C16"],
        "TPM_SP": ["C03"],
        "COMMANDER_SP": ["C03"],
        "EXTERNAL_CHALLENGE_SP": ["C05"],
        "ONE_CORE_SIX_MODULES": ["C17"],
        "FIVE_PRODUCT_TOOLS": ["C20"],
        "EIGHT_KINDS_THREE_MODES": ["C17", "C18"],
        "HERMES_KANBAN_SWARM": ["C08", "C09", "C14"],
        "OPENSPEC_STRICT_METHOD": ["C10", "C11"],
    }.get(name, ["C24"])
    contract["runtime_readiness"].append(
        {
            "capability": name,
            "required_now": action in ("USE_NATIVE", "QUALIFY"),
            "lifecycle": {
                "discover": "REQUIRED",
                "bind": "REQUIRED",
                "route": "REQUIRED",
                "effective_load": "REQUIRED_WHERE_HOST",
                "positive": "REQUIRED",
                "negative": "REQUIRED",
                "fallback": "REQUIRED",
                "rollback": "REQUIRED",
                "independent_qualification": "REQUIRED",
            },
            "current_verdict": "NOT_READY",
            "work_required": [
                "produce raw positive/negative receipts on this candidate",
                "record served arm and principal separation",
                "attach an independent checker receipt",
            ],
            "acceptance_ids": acc,
        }
    )

# ---- journeys --------------------------------------------------------------
JOURNEYS = [
    (
        "GJ01",
        "A developer describes a new CLI tool in plain language and gets a working tool",
        "A wheel/console script installs into a clean venv, --help and --json behave, data persists and uninstall leaves no residue.",
        ["M00", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13"],
        ["C12", "C17", "C18"],
        "A README-only artefact, a wrong JSON type or an untracked write must be rejected",
    ),
    (
        "GJ02",
        "A maintainer asks for one failing test to be fixed in an existing repository",
        "Fresh repo context, bounded diff, red then green on the same subject, original files untouched, rollback proven.",
        ["M00", "M03", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13"],
        ["C12", "C14", "C16"],
        "A stale repo context or a wide unrequested rewrite must block",
    ),
    (
        "GJ03",
        "A host user installs a skill and a bounded agent and tries to make them misbehave",
        "Host discovers and loads the skill, triggers it, refuses the non-trigger path and unloads; the agent calls an allowed tool and is denied a forbidden one, then stops.",
        ["M00", "M01", "M02", "M03", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13", "M14", "M15"],
        ["C17", "C20", "C21"],
        "Copy-only SKILL.md, a false trigger or an unbounded tool loop must fail",
    ),
]

for jid, goal, result, moments, caps, neg in JOURNEYS:
    contract["journeys"].append(
        {
            "journey_id": jid,
            "required": True,
            "user_goal": goal,
            "expected_visible_result": result,
            "expected_automatic_behavior": "The chain selects a lawful kind and mode, compiles PI/PD, plans, executes and challenges without routine questions.",
            "expected_manual_behavior": "Only scope expansion, irreversible effect or release asks the human.",
            "allowed_hitl": ["scope expansion", "irreversible effect", "release approval"],
            "required_capabilities": caps,
            "negative_behavior": neg,
            "failure_recovery": "FirstFail -> bounded repair cone -> new candidate sha -> affected and full regression -> fresh independent checker -> resume.",
            "source_expectation_ids": moments,
            "source_locators": [doc_loc("R15.1") + "::11.2 " + jid, doc_loc("R15.2") + "::" + jid],
        }
    )

# ---- acceptance rows: C00-C24 ---------------------------------------------
for cid, (pred, cmd, neg) in CHECKS.items():
    depth = "L5_REAL_LIFECYCLE_SIDE_EFFECT" if cid in ("C17", "C19", "C20", "C21", "C22") else "L3_INTEGRATION_RUNTIME"
    if cid in ("C00", "C18", "C24"):
        depth = "L1_SCHEMA_CONTRACT"
    contract["acceptance"].append(
        {
            "acceptance_id": "ACC-" + cid,
            "subject_id": cid,
            "subject_type": "REQUIREMENT",
            "source_locators": [doc_loc("R15.1") + "::6 " + cid, doc_loc("R15.2") + "::8.1 " + cid],
            "runtime_required": cid not in ("C00", "C18", "C24"),
            "required_depth": depth,
            "positive_fixture": pred,
            "negative_fixture": neg,
            "recovery_fixture": "restore the pre-round checkpoint and re-run the affected cone only",
            "raw_evidence_required": True,
            "independent_checker_required": True,
            "terminal_states": ["PASS", "PARTIAL", "FAIL", "TEMP_CLOSED"],
        }
    )

# ---- acceptance rows: E and M and journeys ---------------------------------
for eid, (text, cid) in E_MAP.items():
    contract["acceptance"].append(
        {
            "acceptance_id": "ACC-" + eid,
            "subject_id": eid,
            "subject_type": "DELIVERABLE",
            "source_locators": [doc_loc("R15.1") + "::6.3 " + eid, doc_loc("R15.2") + "::6.3 " + eid],
            "runtime_required": True,
            "required_depth": "L4_FAILURE_RECOVERY",
            "positive_fixture": text,
            "negative_fixture": "an engineering summary substituted for a workorder, raw receipt or gate must fail",
            "recovery_fixture": "keep the E item open with a checkpoint and the next legal step",
            "raw_evidence_required": True,
            "independent_checker_required": True,
            "terminal_states": ["PASS", "PARTIAL", "FAIL", "TEMP_CLOSED"],
        }
    )

for mid, (text, cids) in M_MAP.items():
    contract["acceptance"].append(
        {
            "acceptance_id": "ACC-" + mid,
            "subject_id": mid,
            "subject_type": "DELIVERABLE",
            "source_locators": [doc_loc("R15.1") + "::16.1 " + mid, doc_loc("R15.2") + "::6.3 " + mid],
            "runtime_required": True,
            "required_depth": "L5_REAL_LIFECYCLE_SIDE_EFFECT",
            "positive_fixture": text,
            "negative_fixture": "model 200, CI green, shadow-only or a stale seal presented as this milestone must fail",
            "recovery_fixture": "milestone stays open; affected workpackages hold while independent ones continue",
            "raw_evidence_required": True,
            "independent_checker_required": True,
            "terminal_states": ["PASS", "PARTIAL", "FAIL", "TEMP_CLOSED"],
        }
    )

for jid, _goal, _res, _moments, caps, _neg in JOURNEYS:
    contract["acceptance"].append(
        {
            "acceptance_id": "ACC-" + jid,
            "subject_id": jid,
            "subject_type": "JOURNEY",
            "source_locators": [doc_loc("R15.1") + "::11.2 " + jid],
            "runtime_required": True,
            "required_depth": "L4_FAILURE_RECOVERY",
            "positive_fixture": "end to end run of the named journey on this candidate",
            "negative_fixture": "a shortcut that skips an owner, a host load or an independent checker",
            "recovery_fixture": "resume from the last checkpoint without repeating a world effect",
            "raw_evidence_required": True,
            "independent_checker_required": True,
            "terminal_states": ["PASS", "PARTIAL", "FAIL", "TEMP_CLOSED"],
        }
    )

# ---- evidence gate rows ----------------------------------------------------
for cid, (pred, cmd, neg) in CHECKS.items():
    contract["evidence"].append(
        {
            "gate_id": "GATE-" + cid,
            "predicate": pred,
            "expected": {"positive": pred, "negative": neg, "raw": "stdout+stderr+exit persisted with sha256"},
            "command_or_probe": cmd,
            "raw_receipt_required": True,
            "producer": "SBL_EXECUTE_LANE",
            "independent_checker": "DISTINCT_PRINCIPAL_REQUIRED",
            "candidate_binding": {
                "head": head(),
                "package_sha256": pkg_sha,
                "source_hashes": [d["observed"]["sha256"] for d in docs],
            },
            "tracked_subject": True,
            "rerun_rule": "affected-only",
            "invalidation": [
                "any of the 24 source shas changes",
                "the candidate sha changes",
                "the policy epoch or served arm changes",
                "the checker principal equals the maker principal",
            ],
            "terminal_verdict": "TEMP_CLOSED",
            "runtime_pass_allowed": False,
            "claim_level": "LOCAL",
        }
    )

out = os.path.join(ROUND, "CONTRACT.json")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(contract, fh, ensure_ascii=False, indent=2, sort_keys=False)
    fh.write("\n")

print("wrote", out)
print("reviewed", len(reviewed), "exec_scope", len(contract["execution_scope"]),
      "readiness", len(contract["runtime_readiness"]), "acceptance", len(contract["acceptance"]),
      "evidence", len(contract["evidence"]))
print("candidate head", head())
print("sha256", sha256_file(out))
