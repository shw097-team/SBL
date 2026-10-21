#!/usr/bin/env python3
"""R6-TS00/TS01: fresh machine facts + 46-source intake (hashes parsed from the R6 report, not hand-copied)."""
from __future__ import annotations
import hashlib, json, re, socket, sqlite3, subprocess
from pathlib import Path
from datetime import datetime, timezone

WS = Path(r"C:\Projects\Agent_Workspace")
SBL = WS / "SBL"
OUT = SBL / "_governance" / "round-20261021-r6" / "10_PREFLIGHT"
OUT.mkdir(parents=True, exist_ok=True)

R6_REPORT = Path(r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\attachments\SBL_DOC00_13_FULL_CONTRACT_INDEPENDENT_ACCEPTANCE_R6_2026-10-21.md")
R6_CMD = Path(r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\attachments\SBL_FULL_DOC00-13_HERMES_HGK_FABRIC_COMMAND_PROMPT_R6_2026-10-21.md")

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# ---------- parse section 7 ledger tables from the R6 report ----------
text = R6_REPORT.read_text(encoding="utf-8")
ledger: dict[str, str] = {}
# R6 report section 7 rows: | <kind> | `name` | <bytes> | `sha256` |
for m in re.finditer(r"^\|[^|]+\|\s*`([^`]+)`\s*\|\s*[\d,]+\s*\|\s*`([0-9a-f]{64})`\s*\|", text, re.M):
    ledger[m.group(1)] = m.group(2)
# report attachment self-hash (appears in command prompt header table)
cmd_text = R6_CMD.read_text(encoding="utf-8")
m = re.search(r"R6_report_sha256:\s*([0-9a-f]{64})", cmd_text)
r6_report_sha_expected = m.group(1) if m else None
r6_report_sha_actual = sha256(R6_REPORT)

DOC_DIR = WS / "知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG"
KP_DIR = WS / "知識庫/工程基座/GPTs_GENIEMAKER_開發實作+驗收指揮官_KP_Builder_ReleasePack_v2026.06.03-r2/KnowledgePack"
SKILL_DIR = WS / "知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/參考工程資料庫/SKILLS_PLUGIN"
VOL_DIR = WS / "知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/參考工程資料庫/GPTs_GENIEMAKER_設計實作/_10"

def role_of(name: str) -> str:
    if name.startswith("SBL_PIPD-LS-PKG_DOC-"): return "NORMATIVE:SBL_PRODUCT"
    if name.startswith("GPTs_GENIEMAKER_設計實作"): return "SUPPORT:DESIGN"
    if name.endswith("SKILL.md"): return "METHOD:SKILL"
    return "METHOD:KP"

def candidate_paths(name: str):
    base = name.replace("(1)", "")
    return [
        DOC_DIR / name, DOC_DIR / base,
        KP_DIR / name, KP_DIR / base,
        SKILL_DIR / name, SKILL_DIR / base,
        VOL_DIR / name, VOL_DIR / base,
    ]

intake = []
for name, expected in ledger.items():
    found = None
    for p in candidate_paths(name):
        if p.exists():
            found = p
            break
    actual = sha256(found) if found else None
    intake.append({
        "ledger_name": name, "role": role_of(name),
        "local_path": str(found) if found else None, "exists": found is not None,
        "sha256": actual, "expected_sha256": expected,
        "match": actual == expected,
        "bytes": found.stat().st_size if found else None,
    })

n_match = sum(1 for r in intake if r["match"])
n_exist = sum(1 for r in intake if r["exists"])

# ---------- git facts ----------
def git(*a):
    p = subprocess.run(["git", *a], cwd=str(SBL), capture_output=True, text=True)
    return (p.stdout + p.stderr).strip()

def ls_remote(ref: str) -> str:
    p = subprocess.run(["git", "ls-remote", "https://github.com/shw097-team/SBL.git", ref],
                       cwd=str(SBL), capture_output=True, text=True)
    s = p.stdout.strip()
    return s.split()[0] if s else "ERR:" + (p.stderr or "empty")[:200]

git_facts = {
    "local_head": git("rev-parse", "HEAD"),
    "local_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
    "local_dirty_files": len([l for l in git("status", "--porcelain").splitlines() if l.strip()]),
    "origin_main": git("rev-parse", "origin/main"),
    "origin_pr2_head": git("rev-parse", "origin/candidate/c3-20261021-v2"),
    "remote_main": ls_remote("refs/heads/main"),
    "remote_pr2_head": ls_remote("refs/heads/candidate/c3-20261021-v2"),
    "remote_evidence_r5": ls_remote("refs/heads/evidence/r5-20261021-c5"),
}

# ---------- HGK facts ----------
spine_counts = {}
try:
    c = sqlite3.connect(str(WS / "HG-KSEOS/var/shared-spine/hg-kseos.db"))
    for t in ["workorders", "acceptances", "tt_records", "checkpoints", "canonical_events", "candidates"]:
        spine_counts[t] = c.execute(f"select count(*) from {t}").fetchone()[0]
except Exception as e:
    spine_counts = {"error": str(e)}

s = socket.socket(); relay_ok = s.connect_ex(("127.0.0.1", 10101)) == 0; s.close()
codex_exe = Path(r"C:/Users/user/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe")

facts = {
    "schema": "SBL_R6_SSOT_FACTS/1",
    "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    "r6_report": {
        "path": str(R6_REPORT),
        "sha256_actual": r6_report_sha_actual,
        "sha256_expected_from_command": r6_report_sha_expected,
        "match": (r6_report_sha_actual == r6_report_sha_expected) if r6_report_sha_expected else None,
    },
    "source_intake": {"ledger_rows": len(intake), "exists": n_exist, "match": n_match, "rows": intake},
    "git": git_facts,
    "hgk": {
        "spine_counts": spine_counts,
        "codex_executable": str(codex_exe),
        "codex_sha256": sha256(codex_exe) if codex_exe.exists() else None,
        "relay_10101_listening": relay_ok,
    },
}
out = OUT / "SSOT_FACTS.json"
out.write_text(json.dumps(facts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"ledger rows parsed: {len(ledger)}; exists {n_exist}; match {n_match}")
for r in intake:
    if not r["match"]:
        print("  NOT-MATCH:", r["ledger_name"], "expected", r["expected_sha256"][:16], "actual", (r["sha256"] or "ABSENT"))
print("report self-hash:", r6_report_sha_actual, "expected:", r6_report_sha_expected,
      "match:", facts["r6_report"]["match"])
print("git:", json.dumps(git_facts, indent=1))
print("hgk:", json.dumps({"spine": spine_counts, "relay_10101": relay_ok}, indent=1))
