"""Issue the principal requests: one file per owner/host-gated item, each with a literal satisfying action."""
from __future__ import annotations

import json
import os
import time

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
OUT = os.path.join(R, "PRINCIPAL_REQUESTS")

REQUESTS = [
    {
        "id": "W02.policy", "item": "W02 / C02", "principal": "Fabric Policy Owner",
        "predicate": ("exactly one active policy version must be named, and the front door must read it instead of "
                      "hard-coding a model"),
        "why_agent_cannot": ("naming the active version is an owner determination; the agent can read any config but "
                             "cannot decide which one governs"),
        "artifact_ready": ["receipts/admission/hgk_doctor_py312.json",
                           "FAR_DECISIONS_R15_2.md#W02"],
        "satisfying_action": ("write config/active-policy.json with {\"policy_digest\": \"<sha256>\", \"declared_by\": "
                              "\"<owner>\", \"declared_at\": \"<iso8601>\"} — or reply 'hermes-codex-lane.json is "
                              "active' and the agent will write it with declared_by=<owner>"),
        "unblocks": ["W02 DONE", "C02 DONE", "TT-R15.2-FRONTDOOR-SANCTIONED-DRIFT can be closed by binding"],
        "expires": "2026-11-05", "fallback_if_denied": "round stays PARTIAL; front-door drift remains a filed TT",
    },
    {
        "id": "W12.swof", "item": "W12 / C19 / M3", "principal": "SWOF Domain Owner",
        "predicate": "a Native Admission for W3 must be issued by the domain owner",
        "why_agent_cannot": ("MODES declares SWOF_CONNECTED disposition BLOCKED_EXTERNAL; an agent-issued admission "
                             "would be indistinguishable from a real one downstream"),
        "artifact_ready": ["sbl_core/modes.py (3 modes, 13 gate ids)",
                           "workers/candidate_proposals/w11_continuation/continuation.py"],
        "satisfying_action": ("issue the W3 Domain Owner Native Admission (subject = the frozen candidate sha, "
                              "env = this host, ABI = current HGK) — or authorise a shadow-only connected dry run, "
                              "which unblocks E08 without claiming W3"),
        "unblocks": ["E08", "E09", "M3"], "expires": "2026-11-05",
        "fallback_if_denied": "E08/E09 remain NOT_RUN; the blocked disposition is the honest state",
    },
    {
        "id": "W13.hosts", "item": "W13 / C20 / C21 / E06", "principal": "ChatGPT Host Owner",
        "predicate": "three private hosts must each return a host-issued ID and a load receipt",
        "why_agent_cannot": "host IDs and the private-plugin schema are issued by the host, not derivable locally",
        "artifact_ready": ["BENCH_AND_TOOLS_R15_2.json (3 of 5 tool bundles, 0 of 8 lifecycle verbs)",
                           "PRINCIPAL_REQUESTS/W13.hosts.md"],
        "satisfying_action": ("supply three host IDs plus the private-plugin schema, or accept the local "
                              "double-digest build evidence as the interim ceiling for C20 while C21 stays open"),
        "unblocks": ["C20 to DONE", "C21 only with real host IDs"], "expires": "2026-11-12",
        "fallback_if_denied": "E06 stays NOT_RUN; local build evidence is published anyway",
    },
    {
        "id": "W15.release", "item": "W15 / C22 / C24", "principal": "Release Owner + HGK Control-Plane Owner",
        "predicate": "a release seal and a host-load receipt must exist; and the control plane must refuse a delivery state while work orders are open",
        "why_agent_cannot": "a self-issued seal is a forgery; and the gate change is a control-plane decision",
        "artifact_ready": ["workers/candidate_proposals/w15_gate/proposal.diff",
                           "workers/candidate_proposals/w15_gate/test_gate_candidate.py (4 tests green)"],
        "satisfying_action": ("(a) apply the DELIVERY_READY guard diff and approve it; (b) issue the release seal for "
                              "subject sha <to be named at seal time>"),
        "unblocks": ["C22", "W15", "the DELIVERED transition becomes trustworthy"], "expires": "2026-11-12",
        "fallback_if_denied": "release stays BLOCKED and DELIVERED is never claimed",
    },
    {
        "id": "W16.perf", "item": "W16 / C23", "principal": "SBL Performance Owner + HGK Benchmark",
        "predicate": "a reference workload and acceptance thresholds must be owner-defined before any B0/B1/B2 claim",
        "why_agent_cannot": ("an agent that defines both the exam and the grade has measured nothing; and B0 needs a "
                             "matched HGK-only workload that does not exist"),
        "artifact_ready": ["BENCH_AND_TOOLS_R15_2.json (two paired runs, sign flipped: -0.082s / +0.007s)"],
        "satisfying_action": ("name the reference workload, the attempt count and the acceptance threshold; or accept "
                              "the observation that no benefit is currently demonstrable"),
        "unblocks": ["C23 to DONE", "B0 comparability"], "expires": "2026-11-12",
        "fallback_if_denied": "C23 stays PARTIAL with both runs published",
    },
]


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    index = {"schema": "SBL_PRINCIPAL_REQUESTS/1", "round_id": "round-20261022-r15_2",
             "issued_at_utc": time.strftime("%FT%TZ", time.gmtime()),
             "why": ("An item parked on another principal is not finished and not abandoned: it is a request. These "
                     "files are the requests, each with the literal action that satisfies it."),
             "requests": []}
    for r in REQUESTS:
        body = [f"# Principal request: {r['item']}", "",
                f"**Principal:** {r['principal']}", f"**Expires:** {r['expires']}", "",
                "## The predicate", "", r["predicate"], "",
                "## Why an agent cannot satisfy it", "", r["why_agent_cannot"], "",
                "## Artefact already built and waiting", ""]
        body += [f"- `{a}`" for a in r["artifact_ready"]]
        body += ["", "## The literal action that satisfies it", "", "```text", r["satisfying_action"], "```", "",
                 "## What it unblocks", ""]
        body += [f"- {u}" for u in r["unblocks"]]
        body += ["", "## If it is denied", "", r["fallback_if_denied"], "",
                 "## Claim ceiling", "",
                 "Nothing in this round is externally accepted. This file is a request, not an acceptance.", ""]
        path = os.path.join(OUT, f"{r['id']}.md")
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(body))
        index["requests"].append({k: r[k] for k in ("id", "item", "principal", "expires", "unblocks",
                                                    "satisfying_action")} | {"file": os.path.basename(path)})
    json.dump(index, open(os.path.join(OUT, "INDEX.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=2)
    open(os.path.join(OUT, "INDEX.json"), "a", encoding="utf-8", newline="\n").write("\n")
    print(json.dumps({"issued": len(REQUESTS), "dir": OUT}, ensure_ascii=False))
    print("PRINCIPAL_REQUESTS_OK")


if __name__ == "__main__":
    main()
