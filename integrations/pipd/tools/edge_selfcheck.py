#!/usr/bin/env python3
"""Local pre-check of the E1..E12 edge probes.

This is NOT independent acceptance -- the maker may not accept its own work. It exists only to
prove the probes the independent checker will run are executable and to catch a broken probe
before it wastes a checker round.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(r"C:\Projects\Agent_Workspace\PIPD")
res: list[dict] = []


def add(edge: str, ok: bool | None, command: str, observed: str) -> None:
    import re as _re
    observed = _re.sub(r"in \d+\.\d+s", "in <elapsed>", observed)
    res.append({"edge": edge, "verdict": "PASS" if ok else ("FAIL" if ok is False else "NOT_REPRODUCED"),
                "command": command, "observed": observed[:400]})


def run(cmd: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


# E1
r = run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-t", "."])
add("E1", r.returncode == 0 and r.stderr.strip().endswith("OK"),
    "python -m unittest discover -s tests -t .", r.stderr.strip()[-160:])

# E2
scratch = Path(tempfile.mkdtemp(prefix="pipd-edge-self-"))
dst = scratch / "PIPD"
shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.db"))
r2 = run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-t", "."], cwd=dst)
add("E2", r2.returncode == 0 and "OK" in r2.stderr and "skipped=1" in r2.stderr.replace(" ", ""),
    "fresh copy w/o .git: python -m unittest discover -s tests -t .", r2.stderr.strip()[-200:])

sys.path.insert(0, str(ROOT / "src"))
from pipd_ls_sp import pipeline, validate, workspace  # noqa: E402

# E3
vb = validate.validate_bundle({})
add("E3", vb["verdict"] == "FAIL" and vb["findings"][0]["kind"] == "DENOMINATOR",
    "validate.validate_bundle({})", json.dumps(vb))

# E4
f4 = validate.semantic_invariants("PI-PKG", {"subject_id": "", "version": "",
                                             "content_hash": "not-a-hash", "schema_version": "Anything@1"})
add("E4", bool(f4), 'semantic_invariants("PI-PKG", forged)', json.dumps(f4)[:300])

# E5
pi = json.loads((ROOT / ".hgk" / "artifacts" / "s1" / "pi_pkg.json").read_text(encoding="utf-8"))
tampered = json.loads(json.dumps(pi))
tampered["stable_semantic_contract"]["goal"] = "TAMPERED"
f5 = validate.semantic_invariants("PI-PKG", tampered)
add("E5", any("body" in x for x in f5), "tamper stable_semantic_contract then semantic_invariants",
    json.dumps(f5)[:300])

# E6
PI = {"subject_id": "PI-deadbeefdeadbeef",
      "trace": [{"from_id": "PI-deadbeefdeadbeef", "to_id": "ATOM-y", "from_hash": "a" * 64, "to_hash": "b" * 64}],
      "stable_semantic_contract": {"atoms": [{"req_id": "R", "subject_id": "ATOM-y"}]}}
def raises(fn):
    try:
        fn(); return False, "NO RAISE"
    except Exception as e:
        return True, type(e).__name__
a6a, m6a = raises(lambda: pipeline.compile_tqaep(PI, {"subject_id": "E"}, maker="M", checker="m ",
                                                 checker_execution_receipt="x"))
a6b, m6b = raises(lambda: pipeline.compile_tqaep(PI, {"subject_id": "E"}, maker="M", checker="C",
                                                 checker_execution_receipt="SELF_ATTESTED"))
tq = pipeline.compile_tqaep(PI, {"subject_id": "E"}, maker="M", checker="C", checker_execution_receipt="lane-X")
need = {"case", "maker_identity", "checker_identity", "distinct", "checker_execution_receipt"}
add("E6", a6a and a6b and need <= set(tq["acceptance"][0]),
    "compile_tqaep alias / SELF_ATTESTED / proper", f"alias={m6a} self={m6b} fields={sorted(tq['acceptance'][0])}")

# E7
b7 = []
for scope, root in (([ "**" ], str(ROOT)), (["C:/Projects/Agent_Workspace/HG-KSEOS/**"], str(ROOT)),
                    (["../HG-KSEOS/**"], str(ROOT)), (["src/**"], None)):
    try:
        if root is None:
            workspace.repair_candidate("PI-PKG", scope=scope, maker="M")
        else:
            workspace.repair_candidate("PI-PKG", scope=scope, maker="M", authorized_root=root)
        b7.append("NO RAISE")
    except Exception as e:
        b7.append(type(e).__name__)
ok7 = b7[0] != "NO RAISE" and b7[1] != "NO RAISE" and b7[2] != "NO RAISE" and b7[3] != "NO RAISE"
ok7 = b7[:3].count("NO RAISE") == 0 and b7[3] in ("RepairScopeFail",)
add("E7", ok7, "repair_candidate scope probes", json.dumps(b7))
ok7b = True
try:
    workspace.repair_candidate("PI-PKG", scope=["src/**"], maker="M", authorized_root=str(ROOT))
except Exception:
    ok7b = False
add("E7b", ok7b, "repair_candidate scope ['src/**'] with authorized_root", "accepted" if ok7b else "raised")

# E8
f8 = validate.semantic_invariants("ClaimCeiling", {
    "subject_id": "CCL-0000000000000000", "version": "1", "content_hash": "a" * 64,
    "schema_version": "ClaimCeiling@1", "allowed_claims": ["INDEPENDENT_PASS"], "forbidden_escalation": []})
add("E8", bool(f8), "semantic_invariants ClaimCeiling INDEPENDENT_PASS", json.dumps(f8)[:200])

# E9 - every pattern, not just the first one (a pattern table nobody pins rots silently)
PROBES = {
    "github_pat_fine_grained": "git" + "hub_pat_" + "A" * 30,
    "github_classic": "gh" + "p_" + "A" * 30,
    "openai_sk": "sk" + "-" + "A" * 30,
    "aws_access_key": "AK" + "IA" + "B" * 16,
    "private_key_block": "-----BEGIN " + "RSA " + "PRIVATE KEY" + "-----",
    "bearer_literal": ("Author" + "ization: " + "Bea" + "rer " + "AbC+/" * 6),
}
miss = [n for n, rx in workspace.SECRET_PATTERNS if not rx.search(PROBES.get(n, "\u0000"))]
add("E9", not miss, "all six SECRET_PATTERNS vs synthetic samples",
    f"patterns={len(workspace.SECRET_PATTERNS)} unmatched={miss}")

# E10
blob_receipt = subprocess.run(["git", "-C", str(ROOT), "show",
                               "HEAD:.hgk/preflight/compile_out/compiler-receipt.json"],
                              capture_output=True, text=True).stdout
blob_contract = subprocess.run(["git", "-C", str(ROOT), "show",
                                "HEAD:.hgk/preflight/PIPD-LS-SP.CONTRACT.json"],
                               capture_output=True, text=True).stdout
import hashlib  # noqa: E402
rec = json.loads(blob_receipt)
contract_bytes = subprocess.run(["git", "-C", str(ROOT), "show",
                                 "HEAD:.hgk/preflight/PIPD-LS-SP.CONTRACT.json"],
                                capture_output=True).stdout
csha = hashlib.sha256(contract_bytes).hexdigest()
add("E10", rec["contract_sha256"] == csha, "git show HEAD:<receipt>.contract_sha256 vs sha256(blob)",
    f"receipt={rec['contract_sha256'][:16]} blob={csha[:16]}")

# E11
s1dir = ROOT / ".hgk" / "artifacts" / "s1"
bundle = {k: json.loads((s1dir / f"{v}.json").read_text(encoding="utf-8"))
          for k, v in (("PI-PKG", "pi_pkg"), ("PD-PKG", "pd_pkg"), ("ECP", "ecp"),
                       ("TQAEP", "tqaep"), ("ConstructionContract", "construction_contract"))}
tc = pipeline.trace_closure(bundle)
add("E11", tc["verdict"] == "PASS" and not tc["orphans"] and not tc["bad_hashes"],
    "pipeline.trace_closure(bundle)", json.dumps({k: tc[k] for k in ("verdict", "orphans", "bad_hashes")}))

# E12
pats = [b"github_pat_[A-Za-z0-9_]{20,}", b"gh[pousr]_[A-Za-z0-9]{20,}", b"sk-[A-Za-z0-9]{20,}",
        b"AKIA[0-9A-Z]{16}", b"-----BEGIN [A-Z ]*PRIVATE KEY-----"]
import re  # noqa: E402
hits = 0
for p in ROOT.rglob("*"):
    if ".git" in p.parts or "__pycache__" in p.parts:
        continue
    if p.is_file():
        try:
            b = p.read_bytes()
        except Exception:
            continue
        for pat in pats:
            hits += len(re.findall(pat, b))
stray = [str(q.relative_to(ROOT)) for q in ROOT.rglob("__pycache__") if ".git" not in q.parts]
objs = subprocess.run(["git", "-C", str(ROOT), "rev-list", "--objects", "--all"],
                      capture_output=True, text=True).stdout.splitlines()
shas = [l.split()[0] for l in objs if len(l.split()) > 1]
batch = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch"], input="\n".join(shas).encode(),
                       capture_output=True).stdout
gh = sum(len(re.findall(pat, batch)) for pat in pats)
add("E12", hits == 0 and gh == 0 and not stray, "tracked-file + git object sweep (excludes __pycache__)",
    f"source_hits={hits} object_hits={gh} stray_bytecode_dirs={len(stray)}")

shutil.rmtree(scratch, ignore_errors=True)
out = {"schema": "PIPD-EDGE-SELFCHECK/1", "note": "MAKER SELF-CHECK - not independent acceptance",
       # no `head` field on purpose: a commit cannot contain its own SHA without self-reference.
       "candidate_of_record": "frozen-SHA file outside the repo + the external acceptance evidence file",
       "edges_cover": ("unittest / fresh-copy skip / empty-bundle / forged identity / body tamper / SoD / "
                       "repair scope / claim ceiling / PAT pattern / LF+receipt digest / trace closure / secret sweep"),
       "edges": res, "verdict": "PASS" if all(e["verdict"] == "PASS" for e in res) else "FAIL"}
(ROOT / ".hgk" / "artifacts" / "edge_selfcheck.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="")
print(json.dumps({"verdict": out["verdict"],
                  "failed": [e["edge"] for e in res if e["verdict"] != "PASS"],
                  "edges": {e["edge"]: e["observed"][:90] for e in res}}, ensure_ascii=False, indent=1))
