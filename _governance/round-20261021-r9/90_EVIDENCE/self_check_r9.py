"""R9 self-check. Every check is falsifiable and reads real artifacts.

It does NOT check that the round went well. It checks that the round's claims are
borne out by files on disk and by the spine -- and several checks exist purely to
catch the failure mode this round identified: a green signal standing in for a
property it does not measure.

Deliberate design notes:
  * The contract check recomputes the subject join itself instead of trusting the
    compiler receipt, because the compiler only ever checked presence.
  * The manifest check runs the real negative controls, because a verifier that
    has never been seen to fail has not been shown to work.
  * The acceptance check asserts NOT_RUN. A self-check that would pass with an
    acceptance verdict recorded here would be a self-acceptance channel.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SBL = Path(r"C:/Projects/Agent_Workspace/SBL")
HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
CAND = Path(r"C:/Projects/Agent_Workspace/_sbl_r9_candidate")
R9 = SBL / "_governance" / "round-20261021-r9"
SCRATCH = Path(
    r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0"
    r"/LocalCache/Local/hermes/cache/scratch/r9"
)

results: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        ok, detail = fn()
    except Exception as exc:  # a check that explodes is a failure, not a skip
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    results.append((label, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {label}\n       {detail}")


# ---------------------------------------------------------------- C1 mandate
def c1_mandate_gate() -> tuple[bool, str]:
    want = {
        "PLAN": "gpt-6.1-sol",
        "EXECUTE": "opencode-go/minimax-m3.1-flash-free",
        "VERIFY_SECURITY": "gpt-6.1-sol",
    }
    seen = {}
    for lane in want:
        p = HGK / "var" / "R9-GATE" / f"gate_{lane}.json"
        if not p.exists():
            return False, f"missing gate receipt {p}"
        j = json.loads(p.read_text(encoding="utf-8"))
        if not j.get("ok"):
            return False, f"{lane} gate probe not ok: {j.get('ok')}"
        seen[lane] = (j.get("used_rank"), j.get("used_transport_model"))
    bad = {k: v for k, v in seen.items() if v[0] != 1 or v[1] != want[k]}
    if bad:
        return False, f"lane/arm mismatch: {bad}"
    return True, f"all three lanes served at rank 1: {seen}"


# ------------------------------------------------------- C2 contract binding
def c2_contract_binding() -> tuple[bool, str]:
    path = CAND / "contracts" / "SBL_C0_C9_CONTRACT-R9.json"
    c = json.loads(path.read_text(encoding="utf-8"))
    subjects = {a["acceptance_id"]: a.get("subject_id") for a in c["acceptance"]}
    bad = []
    for row in c.get("runtime_readiness", []):
        for aid in row.get("acceptance_ids") or []:
            if subjects.get(aid) != row["capability"]:
                bad.append((row["capability"], aid, subjects.get(aid)))
    four = ["SP_PLUGIN_PACKAGE_TPM", "SP_PLUGIN_PACKAGE_COMMANDER",
            "SP_PLUGIN_PACKAGE_CHALLENGE", "SP_HOST_INSTALL_REQUEST"]
    by_cap = {r["capability"]: r for r in c["runtime_readiness"]}
    for cap in four:
        ids = by_cap[cap]["acceptance_ids"]
        if "ACC-SBL_SHARED_CORE" in ids or f"ACC-{cap}" not in ids:
            bad.append((cap, "wrong-id", ids))
    if bad:
        return False, f"{len(bad)} mis-bound readiness cell(s): {bad}"
    return True, f"0 mis-bound of {len(c['runtime_readiness'])} rows; {len(c['acceptance'])} acceptance edges"


# --------------------------------------------- C3 compiler really did pass
def c3_compiler_receipt() -> tuple[bool, str]:
    rec = json.loads(
        (CAND / "contracts" / "compiled-r9" / "COMPILER_RECEIPT.json").read_text(encoding="utf-8")
    )
    stages = {s["stage"]: s for s in rec["stages"]}
    need = {"lint", "activation", "acceptance", "compile"}
    if set(stages) != need:
        return False, f"stages present {sorted(stages)} != {sorted(need)}"
    for name, s in stages.items():
        if s["rc"] != 0:
            return False, f"stage {name} rc={s['rc']}"
        if "PROMPT_COMPILE_PASS" not in s["stdout"]:
            return False, f"stage {name} did not report PROMPT_COMPILE_PASS"
    if rec["mismatches_before"] != 4 or rec["mismatches_after"] != 0:
        return False, f"receipt claims {rec['mismatches_before']}->{rec['mismatches_after']}"
    return True, "4 stages PROMPT_COMPILE_PASS rc=0; mismatches 4->0"


# ------------------------------------------ C4 contract digest self-consistent
def c4_contract_digest() -> tuple[bool, str]:
    import hashlib

    contract = CAND / "contracts" / "SBL_C0_C9_CONTRACT-R9.json"
    rec = json.loads(
        (CAND / "contracts" / "compiled-r9" / "COMPILER_RECEIPT.json").read_text(encoding="utf-8")
    )
    reported = None
    for s in rec["stages"]:
        if s["stage"] == "compile":
            try:
                reported = json.loads(s["stdout"])["contract_sha256"]
            except Exception:
                pass
    actual = hashlib.sha256(contract.read_bytes()).hexdigest()
    if reported is None:
        return False, "compile stage did not report contract_sha256"
    if reported != actual:
        return False, f"receipt {reported[:16]} != file {actual[:16]}"
    return True, f"contract sha256 {actual[:16]} matches the compiler receipt"


# ------------------------------------------------- C5 control package pinned
def c5_control_package(tmp: Path) -> tuple[bool, str]:
    tool = CAND / "tools" / "check_control_package.py"
    py = sys.executable
    ok = subprocess.run([py, str(tool), "--verify"], capture_output=True, text=True, cwd=str(CAND), timeout=600)
    if ok.returncode != 0:
        return False, f"verify against the real package failed: {(ok.stdout + ok.stderr)[:200]}"

    manifest = json.loads((CAND / "contracts" / "CONTROL_PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["doc_count"] != 14 or len(manifest["documents"]) != 14:
        return False, f"manifest covers {manifest['doc_count']} docs, expected 14"

    # run the negative controls for real -- an unexercised verifier proves nothing
    import shutil

    pkg = tmp / "pkg"
    shutil.rmtree(pkg, ignore_errors=True)
    pkg.mkdir(parents=True)
    src = Path(manifest["canonical_root_at_capture"])
    for f in src.glob("SBL_PIPD-LS-PKG_DOC-*.md"):
        shutil.copy2(f, pkg / f.name)
    saved = (CAND / "contracts" / "CONTROL_PACKAGE_MANIFEST.json").read_text(encoding="utf-8")
    try:
        w = subprocess.run([py, str(tool), "--write", "--root", str(pkg), "--mirror", str(pkg)],
                           capture_output=True, text=True, cwd=str(CAND), timeout=600)
        if w.returncode != 0:
            return False, f"could not write a control manifest for the tamper test: {w.stderr[:200]}"

        target = pkg / "SBL_PIPD-LS-PKG_DOC-00.md"
        orig = target.read_bytes()
        mut = bytearray(orig)
        i = len(mut) // 2
        mut[i] = (mut[i] + 1) % 256 if mut[i] != 255 else mut[i] - 1
        target.write_bytes(bytes(mut))
        if len(mut) != len(orig):
            return False, "tamper changed the size; the sha256 path would not be exercised"
        r = subprocess.run([py, str(tool), "--verify", "--root", str(pkg)],
                           capture_output=True, text=True, cwd=str(CAND), timeout=600)
        if r.returncode != 1 or "ERR_SHA256_DRIFT" not in r.stderr:
            return False, f"same-length tamper not caught by sha256: rc={r.returncode} {r.stderr[:200]}"

        (pkg / "SBL_PIPD-LS-PKG_DOC-13.md").unlink()
        r2 = subprocess.run([py, str(tool), "--verify", "--root", str(pkg)],
                            capture_output=True, text=True, cwd=str(CAND), timeout=600)
        if r2.returncode != 1 or "ERR_DOC_ABSENT" not in r2.stderr:
            return False, f"absent document not caught: rc={r2.returncode} {r2.stderr[:200]}"
    finally:
        (CAND / "contracts" / "CONTROL_PACKAGE_MANIFEST.json").write_text(saved, encoding="utf-8", newline="\n")

    return True, (
        f"14 docs pinned, rollup {manifest['rollup_sha256'][:16]}, real package verifies; "
        "same-length tamper -> ERR_SHA256_DRIFT, absent doc -> ERR_DOC_ABSENT"
    )


# ------------------------------------------------------------- C6 HGK admission
def c6_hgk_admission() -> tuple[bool, str]:
    import sqlite3

    db = HGK / "var" / "shared-spine" / "hg-kseos.db"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    req = "REQ-HGK-PRJ-SBL-PIPDLS-R9-CTRLPKG"
    acc = "ACC-" + req
    r = con.execute("select state,acceptance_id from requirements where requirement_id=?", (req,)).fetchone()
    if r is None:
        return False, "requirement not admitted"
    t = con.execute("select state from taskspecs where requirement_id=?", (req,)).fetchone()
    w = con.execute(
        "select state,base_head from workorders where taskspec_id=(select taskspec_id from taskspecs where requirement_id=?)",
        (req,),
    ).fetchone()
    a = con.execute("select verdict,evidence_ref from acceptances where acceptance_id=?", (acc,)).fetchone()
    con.close()
    if r["state"] != "FROZEN":
        return False, f"requirement state {r['state']}"
    if t is None or t["state"] != "ADMITTED":
        return False, f"taskspec state {t['state'] if t else None}"
    if w is None or w["state"] != "CREATED":
        return False, f"workorder state {w['state'] if w else None}"
    # a self-check must never be able to record its own acceptance
    if a is None or a["verdict"] != "NOT_RUN" or a["evidence_ref"] is not None:
        return False, f"acceptance is not honestly NOT_RUN: {dict(a) if a else None}"
    return True, f"FROZEN -> ADMITTED -> CREATED (base {w['base_head'][:8]}); acceptance NOT_RUN, no result pre-recorded"


# -------------------------------------------------------- C7 ruling artifacts
def c7_ruling() -> tuple[bool, str]:
    md = R9 / "FAR-R9-RULING.md"
    js = R9 / "FAR-R9-RULING.json"
    for p in (md, js):
        if not p.exists():
            return False, f"missing {p.name}"
    r = json.loads(js.read_text(encoding="utf-8"))
    need = ["headline_finding", "denominator", "executed_this_round", "not_executed",
            "claim_ceiling", "pre_authorisation_boundary"]
    missing = [k for k in need if k not in r]
    if missing:
        return False, f"ruling missing sections {missing}"
    if r["denominator"]["semantic_denominator"] != "UNKNOWN":
        return False, "denominator must stay UNKNOWN; the control package declares it so"
    if not r.get("research", {}).get("raw_outputs_gap"):
        return False, "the missing 4th worker output must be disclosed, not omitted"
    return True, f"{md.stat().st_size}B md + {js.stat().st_size}B json; denominator UNKNOWN; raw-output gap disclosed"


# --------------------------------------------------- C8 claim ceiling sentinel
def c8_claim_ceiling() -> tuple[bool, str]:
    r = json.loads((R9 / "FAR-R9-RULING.json").read_text(encoding="utf-8"))
    cc = r["claim_ceiling"]
    if not cc.startswith("CANDIDATE_ONLY"):
        return False, f"ceiling does not start CANDIDATE_ONLY: {cc[:60]}"
    if "NOT ACCEPTED" not in cc:
        return False, "ceiling must carry the R7 non-acceptance forward"
    forbidden = ["ACCEPTED", "FULL_CONTRACT_PASS", "PRODUCTION_VERIFIED"]
    hits = [f for f in forbidden if f in cc.replace("NOT ACCEPTED", "")]
    if hits:
        return False, f"ceiling claims a status it does not hold: {hits}"
    return True, "CANDIDATE_ONLY, carries INCONCLUSIVE/NOT ACCEPTED, claims no closed rung"


# ------------------------------------------- C9 candidate pushed and read back
def c9_remote_readback() -> tuple[bool, str]:
    def g(*a):
        r = subprocess.run(["git", "-C", str(CAND), *a], capture_output=True, text=True, timeout=300)
        return (r.stdout + r.stderr).strip()

    branch = g("rev-parse", "--abbrev-ref", "HEAD")
    local = g("rev-parse", "HEAD")
    g("fetch", "origin", branch)
    remote = g(f"rev-parse", f"origin/{branch}")
    if local != remote:
        return False, f"local {local[:8]} != remote {remote[:8]}"
    return True, f"{branch} @ {local[:8]} matches origin"


# ------------------------------------------------------ C10 no fabricated pass
def c10_no_fabricated_pass() -> tuple[bool, str]:
    """The round must not have written an acceptance PASS anywhere."""
    import sqlite3

    db = HGK / "var" / "shared-spine" / "hg-kseos.db"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    rows = con.execute(
        "select acceptance_id,verdict from acceptances where acceptance_id like '%R9%'"
    ).fetchall()
    con.close()
    bad = [r for r in rows if r[1] not in ("NOT_RUN", "FAIL")]
    if bad:
        return False, f"R9 acceptance is not honestly unresolved: {bad}"
    return True, f"{len(rows)} R9 acceptance row(s), all NOT_RUN or FAIL"


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    tmp = SCRATCH / "selfcheck"
    tmp.mkdir(parents=True, exist_ok=True)
    check("C1  mandate gate: three lanes served at rank 1", c1_mandate_gate)
    check("C2  contract binding: every readiness cell cites its own subject", c2_contract_binding)
    check("C3  compiler receipt: four stages pass, mismatches 4 -> 0", c3_compiler_receipt)
    check("C4  contract digest matches the compiler receipt", c4_contract_digest)
    check("C5  control package pinned and the verifier demonstrably fails", lambda: c5_control_package(tmp))
    check("C6  HGK admission complete, acceptance honestly NOT_RUN", c6_hgk_admission)
    check("C7  FAR ruling present with the required sections", c7_ruling)
    check("C8  claim ceiling carries the non-acceptance forward", c8_claim_ceiling)
    check("C9  candidate branch pushed and read back", c9_remote_readback)
    check("C10 no acceptance pass was fabricated", c10_no_fabricated_pass)

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    verdict = "R9_SELF_CHECK_PASS" if passed == total else "R9_SELF_CHECK_FAIL"
    summary = {
        "schema": "SBL-R9-SELF-CHECK/1",
        "verdict": verdict,
        "passed": passed,
        "total": total,
        "checks": [{"label": l, "ok": ok, "detail": d} for l, ok, d in results],
    }
    out = R9 / "SELF_CHECK_R9.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"\n{verdict}: {passed}/{total}")
    print(f"written {out}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
