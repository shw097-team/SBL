#!/usr/bin/env python3
"""R6-TS20: SP separation probes at candidate a6bcdd0 — persisted receipt."""
from __future__ import annotations
import json, subprocess, hashlib, os
from pathlib import Path
from datetime import datetime, timezone

SBL = Path(r"C:\Projects\Agent_Workspace\SBL")
CAND = Path(r"C:/Projects/_sbl_r4/c3v2")
PY = r"C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe"
OUT = SBL / "_governance" / "round-20261021-r6" / "20_TS20"
OUT.mkdir(parents=True, exist_ok=True)

probe = f'''
import sys, os, json; sys.path.insert(0, r"{str(CAND)}")
import sbl_sp.sp as S
results = []
def probe(name, expect_refuse, fn):
    try:
        r = fn()
        got_refuse = False; detail = str(r)[:90]
    except Exception as e:
        got_refuse = True; detail = str(e)[:90]
    results.append({{"id": name, "expect_refuse": expect_refuse, "refused": got_refuse,
                     "match": got_refuse == expect_refuse, "detail": detail}})

def f1():
    S.assert_permission("commander_sp", "challenge.sign")
def f2():
    S.assert_permission("commander_sp", "verdict.sign")
def f3():
    S.assert_permission("external_challenge_sp", "product.write")
def f4():
    S.assert_permission("external_challenge_sp", "goal.write")
def f5():
    S.assert_permission("tpm_sp", "challenge.sign")
def f6():
    S.assert_permission("tpm_sp", "product.write")
def f7():
    S.assert_permission("tpm_sp", "spec.write"); return "PERMITTED"
def f8():
    S.assert_permission("commander_sp", "product.write"); return "PERMITTED"
def f9():
    S.load_manifest("../outside")
def f10():
    os.environ["SBL_SP_KEY_EXTERNAL_CHALLENGE_SP"] = "K"*40
    v = {{"case_id": "X7", "status": "PASS"}}
    cred = S.expected_signature("external_challenge_sp", v)
    r = S.sign_verdict("external_challenge_sp", "tpm_sp", v, credential=cred)
    return r["schema"] + " maker=" + r["maker"]
def f11():
    os.environ["SBL_SP_KEY_EXTERNAL_CHALLENGE_SP"] = "K"*40
    v = {{"case_id": "X8", "status": "PASS"}}
    return S.sign_verdict("external_challenge_sp", "tpm_sp", v, credential=("B"*64))
def f12():
    os.environ["SBL_SP_KEY_EXTERNAL_CHALLENGE_SP"] = "K"*40
    v = {{"case_id": "X9", "status": "SUMMARY_ONLY"}}
    cred = S.expected_signature("external_challenge_sp", v)
    return S.sign_verdict("external_challenge_sp", "tpm_sp", v, credential=cred)
def f13():
    os.environ["SBL_SP_KEY_EXTERNAL_CHALLENGE_SP"] = "K"*40
    v = {{"case_id": "XA", "status": "PASS"}}
    cred = S.expected_signature("external_challenge_sp", v)
    return S.sign_verdict("external_challenge_sp", "external_challenge_sp", v, credential=cred)

probe("NEG-COMMANDER-CHALLENGE-SIGN", True, f1)
probe("NEG-COMMANDER-VERDICT-SIGN", True, f2)
probe("NEG-CHALLENGE-PRODUCT-WRITE", True, f3)
probe("NEG-CHALLENGE-GOAL-WRITE", True, f4)
probe("NEG-TPM-CHALLENGE-SIGN", True, f5)
probe("NEG-TPM-PRODUCT-WRITE", True, f6)
probe("POS-TPM-SPEC-WRITE", False, f7)
probe("POS-COMMANDER-PRODUCT-WRITE", False, f8)
probe("NEG-UNKNOWN-SP-PATH", True, f9)
probe("POS-CHECKER-SIGNED-VERDICT", False, f10)
probe("NEG-TAMPERED-CREDENTIAL", True, f11)
probe("NEG-PROXY-STATUS-SIGN", True, f12)
probe("NEG-SELF-SIGN", True, f13)
print(json.dumps(results))
'''
p = subprocess.run([PY, "-c", probe], capture_output=True, text=True, timeout=120)
rows = json.loads(p.stdout) if p.returncode == 0 else []
cand_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(CAND), capture_output=True, text=True).stdout.strip()

receipt = {
    "schema": "SBL_R6_TS20_SP_SEPARATION/1",
    "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    "subject": {"candidate_branch": "candidate/c3-20261021-v2", "candidate_commit": cand_sha,
                "manifests": ["sbl_sp/manifests/tpm_sp.json", "sbl_sp/manifests/commander_sp.json",
                              "sbl_sp/manifests/external_challenge_sp.json"]},
    "raw_exit_code": p.returncode,
    "raw_stdout_sha256": hashlib.sha256(p.stdout.encode()).hexdigest(),
    "raw_stderr": p.stderr[-500:],
    "cases": rows,
    "summary": {"total": len(rows),
                "pass": sum(1 for r in rows if r["match"]),
                "fail": sum(1 for r in rows if not r["match"])},
}
p_out = OUT / "SP_SEPARATION_PROBE_R6.txt"
p_out.write_text(p.stdout + "\n[exit " + str(p.returncode) + "]\n", encoding="utf-8")
(OUT / "SP_SEPARATION_CHECK.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
# raw stdout saved, not printed wholesale
print(json.dumps(receipt["summary"]))
for r in rows:
    print(("OK " if r["match"] else "XX "), r["id"], "->", r["detail"][:60])
