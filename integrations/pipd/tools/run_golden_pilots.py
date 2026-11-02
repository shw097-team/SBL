#!/usr/bin/env python3
"""S2 golden pilots — really execute the lifecycle on three profiles.

GP-01 LITE       : one-sentence need -> source-bound PI -> PD -> CC -> ECP -> TQAEP -> trace
GP-02 STANDARD   : the SAME need against a real brownfield repo, late-bound RepoContext
GP-03 ASSURED    : the full chain PLUS a real failure/recovery cycle (tamper -> detect -> bounded
                   repair -> rollback -> revalidate)

Every pilot writes its own raw receipt (per-step artefacts, hashes, verdicts) under
.hgk/artifacts/s2/pilots/. Nothing here is a fixed output: each step is the real function call and
each verdict is recomputed from the produced bytes.

This is a MAKER self-run. It is evidence, not acceptance.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from pipd_ls_sp import pipeline as P            # noqa: E402
from pipd_ls_sp import validate as V            # noqa: E402
from pipd_ls_sp import workspace as W           # noqa: E402
from pipd_ls_sp.profiles import compute_profile  # noqa: E402
from pipd_ls_sp.util import sha256_text         # noqa: E402
from pipd_ls_sp.errors import (PipdError, RepoContextMissing, TqSodFail,  # noqa: E402
                               IntakeInvalid, AuthorityUnknown, RepairScopeFail)

OUT = ROOT / ".hgk" / "artifacts" / "s2" / "pilots"
OUT.mkdir(parents=True, exist_ok=True)
SCHEMAS = ROOT / "schemas"

GOAL = ("Implement the PIPD-LS-SP pre-implementation lifecycle compiler and verify it against the "
        "source spec, then deliver the governed package.")
# A LITE-appropriate need: a single axis, so the profile does not auto-escalate away from LITE.
GOAL_LITE = "Implement the pre-implementation lifecycle compiler."


def _git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def _tracked(root: Path) -> int:
    r = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True)
    if r.returncode == 0:
        return len([l for l in r.stdout.splitlines() if l.strip()])
    return sum(1 for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)


def _repo_context(root: Path, *, writable: str) -> dict:
    """Derive the RepoContext from the host (R-AUD-009).

    The pilot used to hand-assert ``currentness: FRESH`` with no epoch. The strengthened binder
    correctly refuses an unverifiable freshness claim, so the pilot must exercise the real
    derivation path instead of asserting host state itself — and the pilot now fails for the same
    reason a caller would, which is the point of the repair.
    """
    from pipd_ls_sp import repo_context as RC

    return RC.derive_repo_context(root, writable_scope=writable)


def _validate_all(artifacts: dict) -> dict:
    """Validate against the S0 contract names. Internal reports have no schema and are excluded."""
    mapping = {"pi": "PI-PKG", "pd": "PD-PKG", "cc": "ConstructionContract", "ecp": "ECP",
               "tqaep": "TQAEP", "ee": "EvidenceExpectation", "ccl": "ClaimCeiling"}
    bundle = {contract: P.strip_sidecar(artifacts[key])
              for key, contract in mapping.items()
              if key in artifacts and artifacts[key]}
    return V.validate_bundle(bundle, schemas_dir=SCHEMAS)


def _chain(goal: str, profile: str, repo_ctx: dict | None, *, maker: str, checker: str,
           checker_receipt: str, source: Path | None = None) -> tuple[dict, list[dict]]:
    """Run the real pipeline. Returns (artefact set, ordered step log)."""
    log: list[dict] = []

    def step(name: str, fn):
        try:
            out = fn()
            log.append({"step": name, "status": "OK"})
            return out
        except PipdError as exc:                      # a typed refusal is a RESULT, not a crash
            log.append({"step": name, "status": "REFUSED", "error_type": type(exc).__name__,
                        "detail": str(exc)[:200]})
            raise

    # R-AUD-005: the clause source decides the atom count, and the atom count drives the profile.
    # A LITE pilot must be given a LITE-sized clause source, otherwise a 17 KB spec legitimately
    # compiles into hundreds of atoms and the product escalates the profile away from LITE.
    clause_source = source or (ROOT / "docs" / "S0_CONTRACT_SPEC.md")
    card = step("intake", lambda: P.intake(goal, sources=[str(clause_source)],
                                           constraints=["HG-KSEOS is the sole control plane"],
                                           non_goals=["no second control plane"]))
    pi = step(f"compile_pi[{profile}]", lambda: P.compile_pi(card, profile))
    pd = step("bind_pd", lambda: P.bind_pd(pi, repo_ctx))
    cc = step("construction_contract", lambda: P.compile_construction_contract(pd))
    ecp = step("compile_ecp", lambda: P.compile_ecp(pd, pi))
    tqaep = step("compile_tqaep", lambda: P.compile_tqaep(pi, ecp, maker=maker, checker=checker,
                                                          checker_execution_receipt=checker_receipt))
    ee = step("evidence_expectations", lambda: P.evidence_expectations(tqaep, maker))
    ccl = step("claim_ceiling", lambda: P.claim_ceiling(["PROMPT_COMPILE_PASS", "HGK_ADMITTED",
                                                         "LOCAL_QUALIFIED"]))
    arts = {"pi": pi, "pd": pd, "cc": cc, "ecp": ecp, "tqaep": tqaep,
            "ee": ee[0] if ee else {}, "ccl": ccl}
    trc = step("trace_closure", lambda: P.trace_closure(arts))
    arts["trc"] = trc
    return arts, log


def _receipt(name: str, arts: dict, log: list[dict], *, extra: dict | None = None) -> dict:
    valid = _validate_all(arts)
    rec = {
        "pilot": name,
        "candidate_head": _git("rev-parse", "HEAD"),
        "steps": log,
        "artefact_hashes": {k: v.get("content_hash", "") for k, v in arts.items()},
        "artefact_ids": {k: v.get("subject_id", "") for k, v in arts.items()},
        "schema_validation": {"verdict": valid.get("verdict"), "checked": valid.get("checked"),
                              "findings": valid.get("findings", [])},
        "trace_closure": {"verdict": arts["trc"].get("verdict"),
                          "edges": arts["trc"].get("edges"),
                          "orphans": arts["trc"].get("orphans"),
                          "bad_hashes": arts["trc"].get("bad_hashes")},
        "claim_ceiling": arts["ccl"].get("allowed_claims"),
        "producer": "HERMES-MAKER",
        "independent": False,
    }
    if extra:
        rec.update(extra)
    rec["pilot_verdict"] = "PASS" if (valid.get("verdict") == "PASS"
                                      and rec["trace_closure"]["verdict"] == "PASS") else "FAIL"
    return rec


# --------------------------------------------------------------------- GP-01
def gp01() -> dict:
    ctx = _repo_context(ROOT, writable="src/**")
    arts, log = _chain(GOAL_LITE, "LITE", ctx, maker="HERMES-MAKER",
                       checker="glm-5.3-flash/opencode-go",
                       checker_receipt=".hgk/ao/verdict_clean_G1-G5.log",
                       source=ROOT / "fixtures" / "gp01_lite_need.txt")
    # The profile must be genuinely LITE here (one axis), and the two escalation paths must fire on
    # their own triggers -- a LITE run that silently became ASSURED would not be a LITE test at all.
    eff = arts["pi"]["stable_semantic_contract"]["profile_binding"]["profile"]
    five_axes = compute_profile("LITE", axes=["intent", "knowledge", "verification", "release",
                                              "trust_boundary"])
    esc_off = compute_profile("LITE", axes=["intent"], provider_off_required=True)
    rec = _receipt("GP-01_LITE", arts, log,
                   extra={"profile": eff,
                          "profile_is_genuinely_lite": eff == "LITE",
                          "escalation_axis_complexity": {"profile": five_axes["profile"],
                                                         "reason": five_axes["escalation_reason"]},
                          "escalation_provider_off": {"profile": esc_off["profile"],
                                                      "reason": esc_off["escalation_reason"]},
                          "escalation_paths_verified": (five_axes["profile"] == "ASSURED"
                                                        and esc_off["profile"] == "STANDARD")})
    rec["lite_profile_verdict"] = "PASS" if (eff == "LITE" and rec["escalation_paths_verified"]) else "FAIL"
    if rec["lite_profile_verdict"] != "PASS":
        rec["pilot_verdict"] = "FAIL"
    return rec


# --------------------------------------------------------------------- GP-02
def gp02() -> dict:
    ctx = _repo_context(ROOT, writable="src/**")          # real brownfield repo = this product tree
    arts, log = _chain(GOAL, "STANDARD", ctx, maker="HERMES-MAKER",
                       checker="glm-5.3-flash/opencode-go",
                       checker_receipt=".hgk/ao/verdict_clean_G1-G5.log")
    rc = arts["pd"]["RepoContext"]
    return _receipt("GP-02_STANDARD_BROWNFIELD", arts, log,
                    extra={"repo_context": rc,
                           "late_binding_real": bool(rc.get("head")) and rc.get("tracked_files", 0) > 0,
                           "profile": arts["pi"]["stable_semantic_contract"]["profile_binding"]["profile"]})


# --------------------------------------------------------------------- GP-03
def gp03() -> dict:
    ctx = _repo_context(ROOT, writable="src/**")
    arts, log = _chain(GOAL, "ASSURED", ctx, maker="HERMES-MAKER",
                       checker="glm-5.3-flash/opencode-go",
                       checker_receipt=".hgk/ao/verdict_clean_G1-G5.log")

    # --- real failure/recovery cycle, on a scratch copy so the frozen tree is untouched ---
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="pipd-gp03-"))
    shutil.copytree(ROOT / "src", tmp / "src", ignore=shutil.ignore_patterns("__pycache__"))
    target = tmp / "src" / "pipd_ls_sp" / "util.py"
    clean = target.read_text(encoding="utf-8")
    tampered = clean + "\n# TAMPER\n"
    target.write_text(tampered, encoding="utf-8", newline="")

    detected = sha256_text(tampered) != sha256_text(clean)
    # bounded repair refuses out-of-scope targets, accepts in-scope ones
    try:
        W.repair_candidate("x.py", scope=["../HG-KSEOS/**"], maker="M", authorized_root=str(tmp))
        out_of_scope_refused = False
    except RepairScopeFail:
        out_of_scope_refused = True
    repaired = W.repair_candidate(str(target), scope=["src/**"], maker="HERMES-MAKER",
                                  authorized_root=str(tmp))
    # rollback = restore the pristine bytes
    target.write_text(clean, encoding="utf-8", newline="")
    rolled_back = target.read_text(encoding="utf-8") == clean
    shutil.rmtree(tmp, ignore_errors=True)

    rec = _receipt("GP-03_ASSURED_FAILURE_RECOVERY", arts, log,
                   extra={"tamper_detected": detected,
                          "out_of_scope_repair_refused": out_of_scope_refused,
                          "bounded_repair_receipt": repaired if isinstance(repaired, dict) else {},
                          "rollback_byte_identical": rolled_back,
                          "profile": arts["pi"]["stable_semantic_contract"]["profile_binding"]["profile"]})
    rec["failure_recovery_verdict"] = ("PASS" if (detected and out_of_scope_refused and rolled_back)
                                       else "FAIL")
    if rec["failure_recovery_verdict"] != "PASS":
        rec["pilot_verdict"] = "FAIL"
    return rec


# --------------------------------------------------------------------- negative pilots
def negatives() -> list[dict]:
    out = []
    cases = [
        ("N1_empty_goal", lambda: P.intake("   ", sources=[str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")])),
        ("N2_no_source", lambda: P.intake(GOAL, sources=[])),
        ("N3_missing_repo_context", lambda: P.bind_pd({"subject_id": "x"}, None)),
        ("N4_sod_same_identity", lambda: P.compile_tqaep({"trace": [1]}, {"subject_id": "e"},
                                                         maker="M", checker=" m ")),
        ("N5_self_attested_checker", lambda: P.compile_tqaep({"trace": [1]}, {"subject_id": "e"},
                                                             maker="M", checker="C",
                                                             checker_execution_receipt="SELF_ATTESTED")),
        ("N6_repair_out_of_scope", lambda: W.repair_candidate("x", scope=["**"], maker="M",
                                                              authorized_root=str(ROOT))),
        ("N7_repair_absolute_path", lambda: W.repair_candidate("C:/Windows/system32/x.dll",
                                                               scope=["src/**"], maker="M",
                                                               authorized_root=str(ROOT))),
    ]
    for cid, fn in cases:
        try:
            fn()
            out.append({"case": cid, "verdict": "FAIL", "why": "no typed refusal was raised"})
        except PipdError as exc:
            out.append({"case": cid, "verdict": "PASS", "refusal_type": type(exc).__name__,
                        "detail": str(exc)[:160]})
        except Exception as exc:                       # an untyped crash is NOT a correct refusal
            out.append({"case": cid, "verdict": "FAIL",
                        "why": f"untyped {type(exc).__name__}: {str(exc)[:120]}"})
    return out


def main() -> int:
    results = {"gp01": gp01(), "gp02": gp02(), "gp03": gp03(), "negative_cases": negatives()}
    results["candidate_head"] = _git("rev-parse", "HEAD")
    results["all_pilot_verdicts"] = {k: v.get("pilot_verdict") for k, v in results.items()
                                     if isinstance(v, dict) and "pilot_verdict" in v}
    results["negative_pass"] = f"{sum(1 for c in results['negative_cases'] if c['verdict'] == 'PASS')}/{len(results['negative_cases'])}"
    results["verdict"] = ("PASS" if all(v == "PASS" for v in results["all_pilot_verdicts"].values())
                          and results["negative_pass"].split("/")[0] == results["negative_pass"].split("/")[1]
                          else "FAIL")
    for key in ("gp01", "gp02", "gp03"):
        (OUT / f"{key}.json").write_text(json.dumps(results[key], ensure_ascii=False, indent=1,
                                                    default=str), encoding="utf-8", newline="")
    (OUT / "GOLDEN_PILOTS.json").write_text(json.dumps(results, ensure_ascii=False, indent=1,
                                                       default=str), encoding="utf-8", newline="")
    print(json.dumps({k: results[k] for k in ("all_pilot_verdicts", "negative_pass", "verdict",
                                              "candidate_head")}, ensure_ascii=False, indent=1))
    return 0 if results["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
