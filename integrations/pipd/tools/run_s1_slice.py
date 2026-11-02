#!/usr/bin/env python3
"""Run the S1 LITE vertical slice and freeze its artifacts as raw evidence."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pipd_ls_sp import pipeline, validate  # noqa: E402
from pipd_ls_sp.cli import COMMANDS  # noqa: E402

OUT = ROOT / ".hgk" / "artifacts" / "s1"
GOAL = ("以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 規格包編譯系統，"
        "完成知識來源編譯、測試驗收與公開交付。")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    card = pipeline.intake(GOAL, sources=[str(ROOT)], constraints=["HGK-only control plane"],
                           non_goals=["no second control plane"])
    pi = pipeline.compile_pi(card, "LITE")
    pd = pipeline.bind_pd(pi, {"root": str(ROOT), "head": head,
                               "tracked_files": len(list((ROOT / "src").rglob("*.py"))),
                               "writable_scope": "src/**"})
    ecp = pipeline.compile_ecp(pd, pi)
    cc = pipeline.compile_construction_contract(pd)
    MAKER, CHECKER = "HERMES-MAKER", "glm-5.3-flash/opencode-go"
    # The receipt must name the lane whose ACTUAL execution produced the verdict, and must agree with
    # CHECKER. An earlier value pointed at a gpt-6.1-sol audit lane while CHECKER claimed a GLM lane:
    # a checker identity and its execution receipt that disagree are not evidence of independence.
    CHECKER_RECEIPT = ".hgk/ao/verdict_edge_12of12.log (lane edge-reverify-glm, glm-5.3-flash/opencode-go)"
    tqaep = pipeline.compile_tqaep(pi, ecp, maker=MAKER, checker=CHECKER,
                                   checker_execution_receipt=CHECKER_RECEIPT)
    trace = pipeline.trace_closure({"pi": pi, "pd": pd, "ecp": ecp, "tqaep": tqaep})
    ev = pipeline.evidence_expectations(tqaep, "HERMES-MAKER")
    ccl = pipeline.claim_ceiling(["PROMPT_COMPILE_PASS", "HGK_ADMITTED", "LOCAL_QUALIFIED"])

    bundle = {"PI-PKG": pipeline.strip_sidecar(pi), "PD-PKG": pd, "ECP": ecp,
              "TQAEP": tqaep, "ConstructionContract": cc}
    validation = validate.validate_bundle(bundle, ROOT / "schemas")
    for name, obj in (("intent_card", card), ("pi_pkg", pipeline.strip_sidecar(pi)), ("pd_pkg", pd),
                      ("ecp", ecp), ("construction_contract", cc), ("tqaep", tqaep),
                      ("trace_closure", trace),
                      ("evidence_expectations", {"items": ev}), ("claim_ceiling", ccl),
                      ("artifact_validation", validation)):
        (OUT / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8", newline="")

    summary = {
        "schema": "PIPD-S1-SLICE-EVIDENCE/1",
        "baseline_head": head,
        "cli_command_count": len(COMMANDS),
        "commands": list(COMMANDS),
        "artifacts": {
            "intent_card": card["subject_id"],
            "pi_pkg": pi["subject_id"],
            "pd_pkg": pd["subject_id"],
            "ecp": ecp["subject_id"],
            "tqaep": tqaep["subject_id"],
            "trace_closure": trace["subject_id"],
        },
        "atom_count": len(pipeline.atoms_of(pi)),
        "trace_verdict": trace["verdict"],
        "trace_orphans": trace["orphans"],
        "tqaep_tests": len(tqaep["tests"]),
        "evidence_expectations": len(ev),
        "profile": pi["_profile_meta"]["profile"],
        "profile_escalated_from": pi["_profile_meta"]["requested_profile"],
        "sod": {"maker": MAKER, "checker": CHECKER, "distinct": True,
                "checker_execution_receipt": tqaep["acceptance"][0]["checker_execution_receipt"]},
        "artifact_validation": validation["verdict"],
        "artifact_validation_findings": validation["findings"],
        "claim_ceiling_allowed": ccl["allowed_claims"],
        "claim_ceiling_forbidden": ccl["forbidden_escalation"],
    }
    (OUT / "SLICE_EVIDENCE.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if trace["verdict"] == "PASS" and validation["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
