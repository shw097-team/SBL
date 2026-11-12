#!/usr/bin/env python3
"""REC08 F4 — per-row resume queue + driver (the register must be able to RESUME).

REC08 §F4 / skill rule 14: every open obligation needs an executable next action that EXISTS,
an expectation, a timeout, and a driver that parks a failure and continues. A row with no legal
agent action gets a typed park naming the missing signature -- never a fabricated command.

Usage:
  python tools/row_resume.py --build                  # write the queue
  python tools/row_resume.py --drive --max 12         # run a bounded batch, park failures
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
WORKSPACE = Path("C:/Projects/Agent_Workspace")
AUDIT = VAR / "ROW_AUDIT_R17.json"
QUEUE = VAR / "RESUME_QUEUE_R17.json"
JOURNAL = VAR / "receipts" / "F4_ROW_RESUME.json"

TERMINAL = {"DONE", "DONE_DOC_RED", "DONE_NOFIT"}
PATH_RE = re.compile(r"([\w./\\-]+\.(?:py|json|ps1|cmd))")


def resolve(path_text: str) -> Path | None:
    p = Path(path_text.replace("\\", "/"))
    cand = p if p.is_absolute() else WORKSPACE / p
    return cand if cand.exists() else None


def build() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = audit["rows"]
    queue, parked = [], []
    for r in rows:
        rid = r["id"]
        if r.get("state") in TERMINAL:
            continue
        action = (r.get("next_executable_action") or "").strip()
        entry = {
            "id": rid, "state": r.get("state"), "family": r.get("family"),
            "owner_class": r.get("owner_class"),
            "owning_principal": r.get("owning_principal"),
            "missing_grant_kind": r.get("missing_grant_kind"),
            "dependency_ids": r.get("immediate_dependency_ids") or [],
            "declared_action": action,
        }
        m = PATH_RE.search(action) if action else None
        if m and resolve(m.group(1)):
            entry.update({"resume_cmd": action, "expect": "exit 0 and a typed verdict in stdout",
                          "timeout": 180, "source": "DECLARED_ACTION"})
            queue.append(entry)
            continue
        # No declared action with a real target: the only honest generic verb is the row probe,
        # which exists and returns a TYPED verdict (OK / PARTIAL / UNBOUND / UNKNOWN).
        entry.update({
            "resume_cmd": f'python var/R17-20261023/tools/probe_all.py --id {rid}',
            "expect": "PROBE_OK|PROBE_PARTIAL|PROBE_UNBOUND (typed)",
            "timeout": 120, "source": "ROW_PROBE_FALLBACK",
            "declared_action_unusable": action or None,
        })
        if r.get("owner_class") == "OWNER" or r.get("state", "").startswith("BLOCKED_"):
            entry["park_reason"] = r.get("missing_grant_kind") or "OWNER_SIGNATURE_REQUIRED"
            parked.append(entry)
        queue.append(entry)

    out = {
        "schema": "RESUME_QUEUE.v1", "order": "REC08_F4",
        "built": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "denominator": len(rows), "open_rows": sum(1 for r in rows if r.get("state") not in TERMINAL),
        "terminal_rows": sum(1 for r in rows if r.get("state") in TERMINAL),
        "queue": queue, "owner_parked": [p["id"] for p in parked],
        "split": {
            "AGENT_RESUMABLE": sum(1 for e in queue if e["id"] not in {p["id"] for p in parked}),
            "OWNER_ONLY": len(parked),
        },
        "note": "OWNER_ONLY rows keep an executable PROBE (read-only) so the row still produces "
                "fresh evidence each round; the probe cannot close the row without the signature.",
    }
    QUEUE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"queue": len(queue), **out["split"], "denominator": out["denominator"],
                      "open": out["open_rows"]}, ensure_ascii=False))
    return 0


def drive(max_rows: int) -> int:
    q = json.loads(QUEUE.read_text(encoding="utf-8")) if QUEUE.is_file() else build() or None
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    runs, parks = [], []
    for entry in q["queue"][:max_rows]:
        t0 = time.time()
        try:
            p = subprocess.run(entry["resume_cmd"], shell=True, cwd=str(WORKSPACE),
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=entry["timeout"])
            out, err, code = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired:
            out, err, code = "", "TIMEOUT", "TIMEOUT"
        verdict = next((v for v in ("PROBE_OK", "PROBE_PARTIAL", "PROBE_UNBOUND", "PROBE_UNKNOWN")
                        if f'"{v}"' in out), None)
        rec = {"id": entry["id"], "cmd": entry["resume_cmd"], "exit": code,
               "seconds": round(time.time() - t0, 2), "probe_verdict": verdict,
               "stdout_sha256": hashlib.sha256(out.encode("utf-8", "replace")).hexdigest(),
               "stdout_head": out[:400], "stderr_head": err[:200]}
        # A park is decided by the typed verdict the row's OWN verb promises, never by
        # "nothing printed". A DECLARED_ACTION succeeds on exit 0 + real output; only a probe
        # fallback must emit a PROBE_* verdict. (First draft required PROBE_* everywhere and
        # parked W00 even though it had just written a 21,629-byte freeze receipt.)
        if entry.get("source") == "DECLARED_ACTION":
            ok = code == 0 and out.strip() != ""
        else:
            ok = code == 0 and verdict in ("PROBE_OK", "PROBE_PARTIAL")
        if ok:
            rec["disposition"] = "ADVANCED"
        else:
            rec["disposition"] = "PARKED_TYPED"
            rec["park_code"] = verdict or (code if isinstance(code, str) else f"EXIT_{code}")
            parks.append(entry["id"])
        runs.append(rec)

    doc = {"schema": "ROW_RESUME_RUN.v1", "order": "REC08_F4",
           "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "attempted": len(runs), "advanced": len(runs) - len(parks), "parked": len(parks),
           "parked_ids": parks, "runs": runs,
           "policy": "PARK_AND_CONTINUE: a parked row never stops the batch",
           "claim_ceiling": "PER_ROW_EXECUTED_EVIDENCE (not closure)"}
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("attempted", "advanced", "parked", "parked_ids")},
                     ensure_ascii=False, indent=1))
    print(f"journal={JOURNAL}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--drive", action="store_true")
    ap.add_argument("--max", type=int, default=8)
    a = ap.parse_args()
    if a.build:
        return build()
    if a.drive:
        return drive(a.max)
    return build()


if __name__ == "__main__":
    sys.exit(main())
