#!/usr/bin/env python3
"""S2 NRTV + NEG + SEC + oracle/judge calibration.

NRTV = Negative Request / Trigger Veto: a request that MUST NOT produce a positive artefact.
NEG  = negative fixture set: each capability is asked to fail, and must fail with a TYPED error.
SEC  = security set: secret shapes, path escape, self-acceptance, stale-candidate reuse.
JUDGE= oracle calibration: the oracle is DETERMINISTIC here. No LLM judge lane ran in this round, so
       `judge_kind` says so plainly rather than implying a model adjudicated anything. A calibration
       table records, for each oracle, a case the oracle must accept and a near-miss it must reject.

MAKER self-run: evidence, not acceptance.
"""
from __future__ import annotations
import json, subprocess, sys, tempfile, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pipd_ls_sp import pipeline as P, validate as V, workspace as W          # noqa: E402
from pipd_ls_sp.errors import PipdError, ExportSecretFound                   # noqa: E402

OUT = ROOT / ".hgk" / "artifacts" / "s2"; OUT.mkdir(parents=True, exist_ok=True)
SCHEMAS = ROOT / "schemas"
GOAL = ("Implement the pre-implementation lifecycle compiler and verify it against the source spec, "
        "then deliver the governed package.")
RECEIPT = ".hgk/ao/verdict_clean_G1-G5.log"


def typed(fn):
    """Return (refused_with_typed_error, error_type, detail). An untyped crash is NOT a pass."""
    try:
        fn()
    except PipdError as exc:
        return True, type(exc).__name__, str(exc)[:140]
    except Exception as exc:
        return False, f"UNTYPED::{type(exc).__name__}", str(exc)[:140]
    return False, "NO_REFUSAL", ""


def nrtv() -> list[dict]:
    """Requests that must NOT yield a positive artefact."""
    cases = [
        ("NRTV-01_pure_filler_goal", lambda: P.intake("ok thanks", sources=[str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")])),
        ("NRTV-02_zero_atoms", lambda: P.intake("do the thing", sources=[str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")])),
        ("NRTV-03_no_sources", lambda: P.intake(GOAL, sources=[])),
        ("NRTV-04_source_does_not_exist", lambda: P.intake(GOAL, sources=["C:/nope/missing.md"])),
        ("NRTV-05_pd_without_repo", lambda: P.bind_pd({"subject_id": "p"}, None)),
        ("NRTV-06_repo_root_missing", lambda: P.bind_pd({"subject_id": "p"}, {"root": "C:/nope"})),
        ("NRTV-07_unknown_profile", lambda: P.profile_record("TURBO", ["intent"])),
        ("NRTV-08_unknown_axis", lambda: P.profile_record("LITE", ["vibes"])),
        ("NRTV-09_empty_authority_family", lambda: P.freeze_authority({"F2": {"files": [], "manifest_sha256": "a" * 64, "root": "."}})),
        ("NRTV-10_unknown_claim", lambda: P.claim_ceiling(["TOTALLY_VERIFIED"])),
    ]
    out = []
    for cid, fn in cases:
        ok, kind, detail = typed(fn)
        out.append({"case": cid, "verdict": "PASS" if ok else "FAIL", "refusal_type": kind, "detail": detail})
    return out


def neg() -> list[dict]:
    cases = [
        ("NEG-01_sod_same", lambda: P.compile_tqaep({"trace": [1]}, {"subject_id": "e"}, maker="M", checker="m ")),
        ("NEG-02_sod_self_attested", lambda: P.compile_tqaep({"trace": [1]}, {"subject_id": "e"}, maker="M", checker="C", checker_execution_receipt="SELF_ATTESTED")),
        ("NEG-03_sod_no_receipt", lambda: P.compile_tqaep({"trace": [1]}, {"subject_id": "e"}, maker="M", checker="C")),
        ("NEG-04_no_trace", lambda: P.compile_tqaep({}, {"subject_id": "e"}, maker="M", checker="C", checker_execution_receipt="r")),
        ("NEG-05_cc_without_scope", lambda: P.compile_construction_contract({"subject_id": "p", "late_bound_construction_binding": {"writable_scope": ""}})),
        ("NEG-06_ecp_without_scope", lambda: P.compile_ecp({"subject_id": "p", "late_bound_construction_binding": {"writable_scope": ""}}, {"subject_id": "i"})),
        ("NEG-07_repair_glob_scope", lambda: W.repair_candidate("a.py", scope=["**"], maker="M", authorized_root=str(ROOT))),
        ("NEG-08_repair_escape_scope", lambda: W.repair_candidate("a.py", scope=["../HG-KSEOS/**"], maker="M", authorized_root=str(ROOT))),
        ("NEG-09_repair_absolute_subject", lambda: W.repair_candidate("C:/Windows/x.dll", scope=["src/**"], maker="M", authorized_root=str(ROOT))),
        ("NEG-10_repair_no_authorized_root", lambda: W.repair_candidate("a.py", scope=["src/**"], maker="M")),
        ("NEG-11_repair_self_accept", lambda: W.repair_candidate("a.py", scope=["src/**"], maker="M", authorized_root=str(ROOT), self_accept=True)),
        ("NEG-12_diff_schema_mismatch", lambda: W.semantic_diff({"schema_version": "PI-PKG@1"}, {"schema_version": "PI-PKG@2"})),
        ("NEG-13_authority_without_families", lambda: P.freeze_authority({})),
        ("NEG-14_authority_missing_digest", lambda: P.freeze_authority({"F2": {"files": [{"rel": "x"}], "root": "."}})),
    ]
    out = []
    for cid, fn in cases:
        ok, kind, detail = typed(fn)
        out.append({"case": cid, "verdict": "PASS" if ok else "FAIL", "refusal_type": kind, "detail": detail})
    return out


def sec() -> list[dict]:
    out = []
    tmp = Path(tempfile.mkdtemp(prefix="pipd-sec-"))
    # SEC-01: a planted secret shape must be FOUND by the scanner (fail-closed, not fail-open)
    planted = tmp / "leak.txt"
    planted.write_text("Authorization: Bearer " + "AbCdEf0123456789xyz+/" * 2 + "\n", encoding="utf-8")
    found = W.secret_scan(tmp)
    out.append({"case": "SEC-01_planted_bearer_is_found", "verdict": "PASS" if found.get("hits") else "FAIL",
                "detail": f"hits={len(found.get('hits', []))}"})
    # SEC-02: export refuses to ship a secret-bearing tree
    refused, kind, detail = typed(lambda: W.export_manifest(tmp))
    out.append({"case": "SEC-02_export_refuses_secret_tree",
                "verdict": "PASS" if (refused and kind == "ExportSecretFound") else "FAIL",
                "refusal_type": kind, "detail": detail})
    # SEC-03: a clean tree exports normally (proves SEC-02 is not a blanket refusal)
    clean = tmp / "clean"; clean.mkdir()
    (clean / "a.txt").write_text("nothing sensitive here\n", encoding="utf-8")
    refused3, kind3, d3 = typed(lambda: W.export_manifest(clean))
    # NOT refused is the pass here: without this row, SEC-02 could be a blanket refusal and look fine.
    out.append({"case": "SEC-03_clean_tree_still_exports",
                "verdict": "PASS" if (not refused3 and kind3 == "NO_REFUSAL") else "FAIL",
                "refusal_type": kind3, "detail": d3 or "exported"})
    # SEC-04: the frozen tree itself must carry no secret hit
    fresh = W.secret_scan(ROOT)
    out.append({"case": "SEC-04_product_tree_has_no_secret_hit",
                "verdict": "PASS" if not fresh.get("hits") else "FAIL",
                "detail": f"hits={len(fresh.get('hits', []))} scanned={fresh.get('scanned')}"})
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def judge_calibration() -> dict:
    """Calibrate the DETERMINISTIC oracle: it must accept the true case and reject a near-miss."""
    rows = []
    ctx = {"root": str(ROOT), "head": "deadbeef" * 5, "tracked_files": 171,
           "currentness": "FRESH", "writable_scope": "src/**"}
    pi = P.compile_pi(P.intake(GOAL, sources=[str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")]), "STANDARD")
    pd = P.bind_pd(pi, ctx)
    cc = P.compile_construction_contract(pd)
    # accept case
    acc = V.validate_bundle({"ConstructionContract": P.strip_sidecar(cc)}, schemas_dir=SCHEMAS)
    rows.append({"oracle": "ConstructionContract.schema", "expect": "ACCEPT",
                 "got": acc["verdict"], "verdict": "PASS" if acc["verdict"] == "PASS" else "FAIL"})
    # near-miss: drop the required rollback field
    bad = dict(P.strip_sidecar(cc)); bad.pop("rollback", None)
    rej = V.validate_bundle({"ConstructionContract": bad}, schemas_dir=SCHEMAS)
    rows.append({"oracle": "ConstructionContract.schema", "expect": "REJECT_MISSING_ROLLBACK",
                 "got": rej["verdict"], "verdict": "PASS" if rej["verdict"] == "FAIL" else "FAIL",
                 "counterexample": [f["detail"] for f in rej["findings"]][:2]})
    # near-miss: a stale identity (body edited, hash not resealed)
    stale = dict(P.strip_sidecar(cc)); stale["expected_changes"] = ["tampered"]
    st = V.validate_bundle({"ConstructionContract": stale}, schemas_dir=SCHEMAS)
    rows.append({"oracle": "ArtifactIdentity.content_hash", "expect": "REJECT_STALE_HASH",
                 "got": st["verdict"], "verdict": "PASS" if st["verdict"] == "FAIL" else "FAIL",
                 "counterexample": [f["detail"] for f in st["findings"]][:2]})
    # denominator oracle
    empty = V.validate_bundle({})
    rows.append({"oracle": "denominator", "expect": "REJECT_EMPTY",
                 "got": empty["verdict"], "verdict": "PASS" if empty["verdict"] == "FAIL" else "FAIL"})
    return {"judge_kind": "DETERMINISTIC_ORACLE",
            "llm_judge_run": False,
            "llm_judge_note": "no LLM judge lane executed in this round; the calibration below is a "
                              "deterministic oracle, and the absence of an LLM judge is recorded as a TT",
            "rows": rows,
            "verdict": "PASS" if all(r["verdict"] == "PASS" for r in rows) else "FAIL"}


def main() -> int:
    res = {"nrtv": nrtv(), "neg": neg(), "sec": sec(), "judge": judge_calibration(),
           "candidate_head": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                            capture_output=True, text=True).stdout.strip()}
    for k in ("nrtv", "neg", "sec"):
        n = sum(1 for c in res[k] if c["verdict"] == "PASS")
        res[f"{k}_pass"] = f"{n}/{len(res[k])}"
    res["verdict"] = ("PASS" if all(res[f"{k}_pass"].split("/")[0] == res[f"{k}_pass"].split("/")[1]
                                    for k in ("nrtv", "neg", "sec")) and res["judge"]["verdict"] == "PASS"
                      else "FAIL")
    (OUT / "NRTV_JUDGE.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    print(json.dumps({k: res[k] for k in ("nrtv_pass", "neg_pass", "sec_pass", "verdict")}, ensure_ascii=False, indent=1))
    print("judge:", res["judge"]["judge_kind"], res["judge"]["verdict"])
    for k in ("nrtv", "neg", "sec"):
        for c in res[k]:
            if c["verdict"] != "PASS":
                print("  FAIL", k, c)
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
