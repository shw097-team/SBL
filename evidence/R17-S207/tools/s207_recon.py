"""S2-07 RG00 + OD-13 readback: read the host's own ledger for the 19:05 C14.8 fire.

Read-only. Writes exactly one JSON report. Never touches a governed repo.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
HERMES = Path(os.environ["LOCALAPPDATA"]) / "Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes"
OUT = VAR / "receipts/R17_S207_RECON.json"
JOB_ID = "3602bce285e8"
TPE = timezone(timedelta(hours=8))


def lp(p):
    s = str(p)
    return "\\\\?\\" + s.replace("/", "\\") if len(s) > 240 else s


def sha(p):
    p = Path(p)
    try:
        return hashlib.sha256(Path(lp(p)).read_bytes()).hexdigest()
    except OSError:
        return None


def now():
    n = datetime.now(timezone.utc)
    return {"utc": n.isoformat(), "taipei": n.astimezone(TPE).isoformat()}


def job():
    f = HERMES / "cron/jobs.json"
    if not f.exists():
        return {"found": False}
    raw = f.read_text(encoding="utf-8", errors="replace")
    data = json.loads(raw)
    rows = data.get("jobs", data if isinstance(data, list) else [])
    for j in rows:
        if str(j.get("id")) == JOB_ID:
            keep = {k: j.get(k) for k in (
                "id", "enabled", "state", "paused_at", "paused_reason", "schedule",
                "script", "no_agent", "workdir", "deliver", "repeat", "last_run_at",
                "next_run_at", "last_status", "failure_streak", "last_error")}
            keep["_job_row_sha256"] = hashlib.sha256(
                json.dumps(j, sort_keys=True, default=str).encode()).hexdigest()
            keep["_jobs_file_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
            return {"found": True, "job": keep}
    return {"found": False, "ids": [str(j.get("id")) for j in rows]}


def db():
    f = HERMES / "cron/executions.db"
    if not f.exists():
        return {"found": False}
    con = sqlite3.connect(f"file:{f}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    tables = [r[0] for r in cur.execute(
        "select name from sqlite_master where type='table'").fetchall()]
    out = {"found": True, "db_sha256": sha(f), "tables": tables}
    for t in tables:
        cols = [r[1] for r in cur.execute(f'pragma table_info("{t}")').fetchall()]
        if "started_at" in cols or "created_at" in cols:
            order = "started_at" if "started_at" in cols else "created_at"
            rows = cur.execute(
                f'select * from "{t}" order by {order} desc limit 25').fetchall()
            out[t] = {"columns": cols, "recent": [dict(r) for r in rows]}
    con.close()
    return out


def journal():
    f = VAR / "runner/journal.jsonl"
    if not f.exists():
        return {"found": False}
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"found": True, "lines": len(lines), "tail": lines[-24:],
            "sha256": sha(f)}


def rg04():
    d = VAR / "runner/rg04"
    if not d.exists():
        return {"found": False}
    files = {}
    for p in sorted(d.glob("*.json")):
        try:
            files[p.name] = {"sha256": sha(p),
                             "body": json.loads(Path(lp(p)).read_text(encoding="utf-8", errors="replace"))}
        except Exception as e:  # noqa: BLE001
            files[p.name] = {"sha256": sha(p), "error": repr(e)}
    return {"found": True, "count": len(files), "files": files}


def arm():
    f = VAR / "RG04_ARM.json"
    if not f.exists():
        return {"found": False}
    return {"found": True, "sha256": sha(f),
            "body": json.loads(f.read_text(encoding="utf-8", errors="replace"))}


def subtasks():
    f = VAR / "SUBTASKS_R17.json"
    if not f.exists():
        return {"found": False}
    d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    rows = d if isinstance(d, list) else d.get("subtasks", d)
    c14 = {}
    if isinstance(rows, dict):
        for k, v in rows.items():
            if str(k).startswith("C14"):
                c14[str(k)] = v.get("state") if isinstance(v, dict) else v
    else:
        for r in rows:
            if isinstance(r, dict) and str(r.get("id", "")).startswith("C14"):
                c14[str(r["id"])] = r.get("state")
    return {"found": True, "sha256": sha(f), "c14": c14,
            "top_keys": list(d)[:12] if isinstance(d, dict) else "list"}


def queue():
    for name in ("RESUME_QUEUE_R17.json", "WORK_QUEUE_R17.json"):
        f = VAR / name
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        rows = d if isinstance(d, list) else d.get("rows", d.get("queue", []))
        ids = [str(r.get("id")) for r in rows if isinstance(r, dict)]
        return {"file": name, "sha256": sha(f), "rows": len(ids),
                "unique_ids": len(set(ids)), "has_canary": "FABRIC-CANARY" in ids,
                "sample_states": sorted({str(r.get("state")) for r in rows if isinstance(r, dict)})}
    return {"found": False}


def repo(path):
    p = Path(path)
    if not p.exists():
        return {"path": path, "exists": False}
    def g(*a):
        r = subprocess.run(["git", "-C", str(p).replace("/", "\\"), *a],
                           capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()[:200]
    rc1, head, _ = g("rev-parse", "HEAD")
    rc2, br, _ = g("rev-parse", "--abbrev-ref", "HEAD")
    rc3, st, _ = g("status", "--porcelain", "-uno")
    rc4, unt, _ = g("status", "--porcelain")
    return {"path": path, "exists": True, "head": head, "branch": br,
            "tracked_dirty": len([x for x in st.splitlines() if x.strip()]),
            "untracked_total": len([x for x in unt.splitlines() if x.startswith("??")]),
            "rc": [rc1, rc2, rc3, rc4]}


def main():
    report = {
        "schema": "R17_S207_RECON/1",
        "generated": now(),
        "hermes_home": str(HERMES),
        "var": str(VAR),
        "job": job(),
        "executions_db": db(),
        "journal": journal(),
        "rg04": rg04(),
        "rg04_arm": arm(),
        "subtasks": subtasks(),
        "queue": queue(),
        "repos": {n: repo(p) for n, p in {
            "SBL": "C:/Projects/Agent_Workspace/SBL",
            "HG-KSEOS": "C:/Projects/Agent_Workspace/HG-KSEOS",
            "Fabric": "C:/Projects/Agent_Workspace/Fabric",
            "PIPD": "C:/Projects/Agent_Workspace/PIPD",
        }.items()},
        "hold": (lambda f: {"exists": f.exists(), "sha256": sha(f) if f.exists() else None})(
            VAR / "HOLD_EXECUTE_WRITER.json"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(report, ensure_ascii=False, indent=1, default=str)
    OUT.write_text(txt, encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(OUT), "bytes": len(txt.encode())}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
