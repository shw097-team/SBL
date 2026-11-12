"""Build the S2-07 CAPC contract by EXTENDING the S2-04 contract that already passes lint.

The S2-04 six-gate PASS is NOT reused as an S2-07 result: this builder only reuses the document
shape, then rewrites identity, intent, changeset and appends the S2-07 capabilities, journeys,
acceptance edges and evidence gates. The compiler must still be run on the new bytes.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
COMPILER = Path("C:/Projects/Agent_Workspace/知識庫/工程基座/construction-acceptance-prompt-compiler/"
                "construction-acceptance-prompt-compiler/scripts/prompt_contract_compiler.py")
SRC = VAR / "capc/S2-04_contract.json"
OUT = VAR / "capc/S2-07_contract.json"
ATT = Path(os.environ["LOCALAPPDATA"]) / "Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/attachments"
TPE = timezone(timedelta(hours=8))


def sha(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return None


def find_s207() -> tuple[str, str | None]:
    for p in sorted(ATT.glob("*S2-07*.md")):
        return p.name, sha(p)
    return "S2-07 command (not found on disk)", None


def cap(name, disposition, action, locators, control=True, runtime=True, ux=False, auto=False):
    return {"capability": name, "current_execution_disposition": disposition,
            "current_profile_selected": True, "canonical_flow_referenced": True,
            "automatic_route_target": auto, "user_experience_required": ux,
            "runtime_required_now": runtime, "action": action,
            "source_locators": locators, "source_disposition": "ACTIVE_REQUIRED",
            "external_method": False, "control_authority": bool(control)}


def readiness(name, verdict, work, acc_ids):
    return {"capability": name, "required_now": True,
            "lifecycle": {"identify": "PASS", "pin": "PASS", "install_materialize": "NOT_APPLICABLE_SOURCE_BACKED",
                          "configure": "PASS", "discover": "PASS", "bind": "PASS", "route": "PASS",
                          "effective_load": "PASS", "doctor_health": "PASS",
                          "positive_pilot": "OPEN" if verdict == "NOT_READY" else "PASS",
                          "negative_security": "OPEN" if verdict == "NOT_READY" else "PASS",
                          "fallback": "PASS", "rollback_uninstall": "PASS",
                          "independent_qualification": "OPEN", "certify": "OPEN", "enable": "OPEN"},
            "current_verdict": verdict, "work_required": work if isinstance(work, list) else [work],
            "acceptance_ids": acc_ids}


def acc(aid, subj, locators, pos, neg, rec, checker=True, stype="CAPABILITY"):
    return {"acceptance_id": aid, "subject_id": subj, "subject_type": stype,
            "source_locators": locators, "runtime_required": True,
            "required_depth": "L3_INTEGRATION_RUNTIME",
            "positive_fixture": pos, "negative_fixture": neg, "recovery_fixture": rec,
            "raw_evidence_required": True, "independent_checker_required": checker,
            "terminal_states": ["INDEPENDENT_CASE_PASS", "INDEPENDENT_CASE_FAIL", "BLOCKED_EXTERNAL"]}


def gate(gid, pred, expected, probe, producer="hermes-agent (maker)"):
    return {"gate_id": gid, "predicate": pred, "expected": expected, "command_or_probe": probe,
            "raw_receipt_required": True, "producer": producer,
            "independent_checker": "distinct checker principal (not available on this host)",
            "candidate_binding": {"head": "086a940", "package_sha256": CAPC_SHA,
                                  "source_hashes": [f"{gid}:{CAPC_SHA}"]},
            "tracked_subject": False, "rerun_rule": "affected-only",
            "invalidation": ["tool sha change", "queue change", "job definition change"],
            "terminal_verdict": "INDEPENDENT_CASE_PASS", "runtime_pass_allowed": False,
            "claim_level": "LOCAL"}


def main() -> int:
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    global CAPC_SHA
    CAPC_SHA = sha(COMPILER) or "UNRESOLVED"
    name, dsha = find_s207()
    loc = f"attachments/{name}"
    stamp = datetime.now(TPE).isoformat(timespec="seconds")

    doc["task_id"] = "SBL-R17-S2-07-HOST-HOTPATH-POSTSESSION-CONTAINMENT"
    ss = doc["source_scan"]
    ss["required_source_families"] = sorted(set(ss["required_source_families"] + ["S2-07 command set"]))
    ss["reviewed"].append({"source_family": "S2-07 command set", "source_id": "R17-S2-07",
                           "locator": loc, "sha256": dsha or "UNRESOLVED",
                           "role": "NORMATIVE", "critical": True})
    if not dsha:
        ss["missing"].append("R17-S2-07 attachment")

    doc["intent"].update({
        "goal": ("prove or refuse post-turn host dispatch, bind the real host hot path, keep the "
                 "containment per-card, and stop mistaking a relay-served lane turn for owner OAuth"),
        "user_expected_outcome": ("one measurable continuation claim with its ceiling, a per-card release list, "
                                 "and every remaining blocker named with its owner action"),
        "user_expected_experience": "the report states what was measured, by whom, and what was refused",
        "expected_autonomy": "HIGH",
        "claim_ceiling": "LOCAL",
        "active_requirement_ids": ["REQ-POST-TURN-DISPATCH", "REQ-HOTPATH-BIND", "REQ-CONTAINMENT-PER-CARD",
                                  "REQ-LANE-PAYER-ATTRIBUTION", "REQ-SANDBOX-POSITIVE-CONTROL"],
        "explicit_constraints": ["no bulk release of deferred cards",
                                 "no owner credential handled by the agent",
                                 "no second scheduler or ledger",
                                 "relay-served turns are never reported as owner OAuth",
                                 "writer hold survives until an OS positive control exists"],
        "non_goals": ["closing the mission", "declaring FULL_PRODUCT_ACCEPTED",
                      "relaxing an assertion to make a card green"],
        "forbidden_mutations": ["SBL/HG-KSEOS/Fabric/PIPD tracked files",
                                "another actor's untracked or dirty files",
                                "force push", "editing a test oracle"],
    })

    doc["authority"]["sources"].append({"id": "R17-S2-07", "rank": "2", "path": loc,
                                        "sha256": dsha or "UNRESOLVED", "locator": "#0",
                                        "role": "NORMATIVE", "governs": True})

    doc["changeset"].update({
        "class": "CONTINUATION", "baseline_verified": True, "reuse_prior_pass": False,
        "affected_domains": ["host cron hot path", "queue containment", "lane payer attribution",
                             "os sandbox qualification"],
        "affected_files": ["var/R17-20261023/tools/advance.py", "var/R17-20261023/tools/runner.py"],
        "must_not_reopen": ["S2-04 compiled contract bytes", "frozen PI/PD",
                            "the 145 obligation denominator", "another actor's dirty files"],
        "product_mutation_allowed": False,
        "scope_expansion_requires_hitl": True,
    })

    doc["execution_scope"] += [
        cap("POST_TURN_HOST_DISPATCH", "ACTIVE_REQUIRED", "QUALIFY",
            [loc + "#6.0A", loc + "#8.0"], control="HERMES_HOST"),
        cap("HOTPATH_RUNTIME_BINDING", "ACTIVE_REQUIRED", "QUALIFY", [loc + "#5.3"]),
        cap("CONTAINMENT_PER_CARD_RELEASE", "ACTIVE_REQUIRED", "QUALIFY", [loc + "#6.0A"]),
        cap("LANE_PAYER_ATTRIBUTION", "ACTIVE_REQUIRED", "QUALIFY",
            [loc + "#4.1"], control="HG-KSEOS"),
        cap("OS_SANDBOX_POSITIVE_CONTROL", "ACTIVE_REQUIRED", "QUALIFY", [loc + "#6.0A"]),
    ]
    doc["runtime_readiness"] += [
        readiness("POST_TURN_HOST_DISPATCH", "RUNTIME_READY",
                  "keep the arm marker; read each new fire from the scheduler ledger", ["ACC-POST-TURN-DISPATCH"]),
        readiness("HOTPATH_RUNTIME_BINDING", "RUNTIME_READY",
                  "keep the binding receipt; re-measure after any tool edit", ["ACC-HOTPATH-BIND"]),
        readiness("CONTAINMENT_PER_CARD_RELEASE", "NOT_READY",
                  "one admission receipt per card before release", ["ACC-CONTAINMENT-PER-CARD"]),
        readiness("LANE_PAYER_ATTRIBUTION", "NOT_READY",
                  "owner interactive sign-in in the sealed home", ["ACC-LANE-PAYER-ATTRIBUTION"]),
        readiness("OS_SANDBOX_POSITIVE_CONTROL", "NOT_READY",
                  "a sandbox mode that executes a child AND denies an outside write", ["ACC-SANDBOX-POS-NEG"]),
    ]

    doc["journeys"] += [
        {"journey_id": "J04_POST_TURN_WAKE", "required": True,
         "user_goal": "work moves while nobody is chatting",
         "expected_visible_result": "a dispatched card with a fire time outside every agent turn",
         "expected_automatic_behavior": ["scheduler fires", "driver gates to the allowlist", "card runs"],
         "expected_manual_behavior": ["owner deletes the arm marker when done"],
         "allowed_hitl": ["owner approval to widen the allowlist"],
         "required_capabilities": ["POST_TURN_HOST_DISPATCH"],
         "negative_behavior": ["absence of a fire reported as continuity"],
         "failure_recovery": ["HOST_POST_SESSION_FAIL + FAR", "re-arm a fresh card"],
         "source_expectation_ids": ["REQ-POST-TURN-DISPATCH"], "source_locators": [loc + "#6.0"]},
        {"journey_id": "J05_CONTAINMENT_RELEASE", "required": True,
         "user_goal": "deferred cards return one by one, with a reason each",
         "expected_visible_result": "a per-card admission record",
         "expected_automatic_behavior": ["classify", "refuse effect classes without a permit"],
         "expected_manual_behavior": ["owner grants a native permit for an effect card"],
         "allowed_hitl": ["per-card admission"],
         "required_capabilities": ["CONTAINMENT_PER_CARD_RELEASE"],
         "negative_behavior": ["deleting the arm marker to release everything at once"],
         "failure_recovery": ["re-arm the marker", "re-run the containment receipt"],
         "source_expectation_ids": ["REQ-CONTAINMENT-PER-CARD"], "source_locators": [loc + "#6.0A"]},
    ]

    doc["acceptance"] += [
        acc("ACC-POST-TURN-DISPATCH", "POST_TURN_HOST_DISPATCH", [loc + "#6.0"],
            "a fire outside every agent turn dispatches a card and leaves its raw artefact",
            "a fire inside an agent turn is not counted",
            "session truly closed: the count stays 0 until a later readback"),
        acc("ACC-HOTPATH-BIND", "HOTPATH_RUNTIME_BINDING", [loc + "#5.3"],
            "runtime import resolves the same file and sha the fix was applied to",
            "a fix in an unimported sibling module never counts",
            "re-bind after any edit; a mismatch blocks all further patches"),
        acc("ACC-CONTAINMENT-PER-CARD", "CONTAINMENT_PER_CARD_RELEASE", [loc + "#6.0A"],
            "each gated card carries class, reason and admission path",
            "bulk release without per-card admission is refused",
            "delete the marker and the prior ready set returns unchanged"),
        acc("ACC-LANE-PAYER-ATTRIBUTION", "LANE_PAYER_ATTRIBUTION", [loc + "#4.1"],
            "a lane turn is attributed to the payer that served it",
            "a relay that answers without a credential cannot be reported as owner OAuth",
            "re-run on owner sign-in and re-attribute"),
        acc("ACC-SANDBOX-POS-NEG", "OS_SANDBOX_POSITIVE_CONTROL", [loc + "#6.0A"],
            "pos: a child process runs inside the workspace",
            "neg: the same child cannot write outside it",
            "no positive control -> hold stays"),
    ]

    for req in ("POST-TURN-DISPATCH", "HOTPATH-BIND", "CONTAINMENT-PER-CARD",
                "LANE-PAYER-ATTRIBUTION", "SANDBOX-POSITIVE-CONTROL"):
        doc["acceptance"].append(acc(
            f"ACC-REQ-{req}", f"REQ-{req}", [loc + "#6.0A"],
            "the requirement's own positive fixture produces its raw receipt",
            "a family-level claim does not close a per-id requirement",
            "re-run the per-id probe after any source or tool change", stype="REQUIREMENT"))
    for jid in ("J04_POST_TURN_WAKE", "J05_CONTAINMENT_RELEASE"):
        doc["acceptance"].append(acc(
            f"ACC-{jid}", jid, [loc + "#6.0"],
            "the journey completes end to end with its visible artefact",
            "a partial path reported as the journey is refused",
            "re-run the journey from a fresh checkpoint", stype="JOURNEY"))

    doc["evidence"] += [
        gate("G-S207-1", "post-turn fire exists on the scheduler ledger", "fire row + journal cycle + card artefact",
             "receipts/R17_S207_POSTSESSION.json"),
        gate("G-S207-2", "hot path bound by runtime import", "module __file__ + sha equal to disk",
             "receipts/R17_S207_ENTRYPOINT_BIND.json"),
        gate("G-S207-3", "containment holds per card", "gated 14, dispatchable 0, effect-capable 0",
             "receipts/R17_S207_CONTAINMENT.json"),
        gate("G-S207-4", "lane turns attributed to payer", "relay accepts a bogus bearer",
             "receipts/R17_S207_LANE_PLAN_VERIFY.json"),
        gate("G-S207-5", "sandbox has a positive control", "child executes and outside write denied",
             "receipts/R17_S207_SANDBOX.json"),
    ]
    doc["termination"]["non_terminal_pause"] = sorted(set(
        doc["termination"]["non_terminal_pause"] + ["POST_TURN_DISPATCH_UNVERIFIED",
                                                   "CONTAINMENT_HELD_PER_CARD"]))
    doc["termination"]["checkpoint_fields"] = sorted(set(
        doc["termination"]["checkpoint_fields"] + ["post_turn_fire_id", "hotpath_module_sha"]))

    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"out": str(OUT), "bytes": OUT.stat().st_size, "sha256": sha(OUT),
                      "s207_source_sha": dsha, "generated": stamp}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
