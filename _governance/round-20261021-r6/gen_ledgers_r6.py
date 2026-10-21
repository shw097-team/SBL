#!/usr/bin/env python3
"""R6-TS07/24/25: build the trace-skeleton ledgers by parsing the R6 report appendices.

Every row is honest: status NOT_FULLY_TRACE_VERIFIED / OPEN unless a raw receipt exists.
No PASS is fabricated. Coverage self-check fails the run on orphan/duplicate ids.
"""
from __future__ import annotations
import json, re, hashlib
from pathlib import Path

WS = Path(r"C:\Projects\Agent_Workspace")
SBL = WS / "SBL"
R6 = Path(r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\attachments\SBL_DOC00_13_FULL_CONTRACT_INDEPENDENT_ACCEPTANCE_R6_2026-10-21.md")
OUT = SBL / "evidence_ledger"
OUT.mkdir(exist_ok=True)
text = R6.read_text(encoding="utf-8")
lines = text.splitlines()

def rows_between(start_pat, end_pat, include_start=False):
    """Yield pipe-table row cells between two markers."""
    on = False
    for ln in lines:
        if not on and re.search(start_pat, ln):
            on = True
            if not include_start:
                continue
        if on and re.search(end_pat, ln):
            break
        if on and ln.strip().startswith("|") and not re.match(r"^\|[\s\-|]+\|$", ln.strip()):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            yield cells

# ---------- B1: 50 parents ----------
parents = []
for cells in rows_between(r"^### B1", r"^### B2"):
    if not cells or not cells[0].startswith("`U"):
        continue
    uid = cells[0].strip("`")
    parents.append({
        "id": uid,
        "source_locator": cells[1].strip("`"),
        "upstream_state": cells[2].strip("`"),
        "r6_conservative_verdict": cells[3].strip("`"),
        "doc01_locator": cells[4].strip("`"),
        "owner": "SBL-Product-Owner",
        "consumer": "SBL_FULL_PRODUCT acceptance gate",
        "acceptance_id": "R6-CHK07",
        "status": "OPEN" if "NOT_ATOM" in cells[3] else "PARTIAL_EVIDENCE_ONLY",
        "raw_evidence": None,
    })

# ---------- B2: 149 children (5-column table) ----------
children = []
for cells in rows_between(r"^### B2", r"^---"):
    if len(cells) < 5 or not cells[0].startswith("`U"):
        continue
    cid = cells[0].strip("`")
    children.append({
        "id": cid,
        "parent_source_locator": cells[1].strip("`"),
        "section": cells[2].strip("`"),
        "doc01_locator": cells[3].strip("`"),
        "r6_status": cells[4].strip("`"),
        "owner": "SBL-Product-Owner",
        "consumer": "SBL_FULL_PRODUCT acceptance gate",
        "acceptance_id": "R6-CHK07",
        "status": "OPEN",
        "raw_evidence": None,
    })

# ---------- appendix C: 38 surfaces (starts at the C-001 table row) ----------
surfaces = []
for cells in rows_between(r"^\| `C-001`", r"^---", include_start=True):
    if len(cells) < 5 or not re.match(r"^`?C-\d{3}`?$", cells[0]):
        continue
    sid = cells[0].strip("`")
    surfaces.append({
        "id": sid,
        "consumer_surface": cells[1],
        "owner_status": cells[2],
        "r6_state": cells[3],
        "doc12_locator": cells[4].strip("`"),
        "status": "OPEN" if ("NO_NATIVE" in cells[3] or "HOLD" in cells[3]) else "PARTIAL_LOCAL_SCOPED",
        "raw_evidence": None,
    })

# ---------- appendix A: 441 identities ----------
donors, slots, methods, ids386 = [], [], [], []
for cells in rows_between(r"^### A1", r"^### A2"):
    if len(cells) >= 4 and cells[0].startswith("`DONOR"):
        donors.append({"id": cells[0].strip("`"), "name": cells[1], "frozen_disposition": cells[2].strip("`"),
                       "source": cells[3].strip("`"), "current_execution": "NOT_EXECUTED_THIS_ROUND"})
for cells in rows_between(r"^### A2", r"^### A3"):
    if len(cells) >= 4 and re.match(r"^`?[A-Z]{2}-\d{2}`?$", cells[0]):
        slots.append({"id": cells[0].strip("`"), "function": cells[1], "frozen_disposition": cells[2].strip("`"),
                      "source": cells[3].strip("`"), "current_execution": "NOT_EXECUTED_THIS_ROUND"})
for cells in rows_between(r"^### A3", r"^### A4"):
    if len(cells) >= 4 and cells[0].startswith("`METHOD"):
        methods.append({"id": cells[0].strip("`"), "name": cells[1], "frozen_disposition": cells[2].strip("`"),
                        "source": cells[3].strip("`"),
                        "current_execution": "EXECUTED_IN_R5_R6_CI" if cells[0].strip("`") == "METHOD-09" else "NOT_EXECUTED_THIS_ROUND"})
for cells in rows_between(r"^### A4", r"^\*\*A1–A4"):
    if len(cells) >= 4 and "/" in cells[0] and cells[0].startswith("`"):
        ids386.append({"id": cells[0].strip("`"), "name": cells[1], "frozen_disposition": cells[2].strip("`"),
                       "source": cells[3].strip("`"), "current_execution": "NOT_EXECUTED_THIS_ROUND"})

n386 = len(ids386)
total441 = len(donors) + len(slots) + len(methods) + n386
print(f"parsed: parents={len(parents)} children={len(children)} surfaces={len(surfaces)} "
      f"donors={len(donors)} slots={len(slots)} methods={len(methods)} ids386={n386} total441={total441}")

# ---------- coverage self-check (CHK07/CHK24/CHK25 anti-fabrication) ----------
errors = []
if len(parents) != 50: errors.append(f"parents {len(parents)} != 50")
if len(children) != 149: errors.append(f"children {len(children)} != 149")
if len(surfaces) != 38: errors.append(f"surfaces {len(surfaces)} != 38")
if total441 != 441: errors.append(f"441 total {total441} != 441")
# duplicates
for name, coll in [("parents", parents), ("children", children), ("surfaces", surfaces),
                   ("donors", donors), ("slots", slots), ("methods", methods), ("ids386", ids386)]:
    ids = [r["id"] for r in coll]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: errors.append(f"duplicate {name}: {sorted(dup)[:5]}")
# children parent linkage (U01.1 -> U01)
pids = {p["id"] for p in parents}
orphans = [c["id"] for c in children if c["id"].split(".")[0] not in pids]
if orphans: errors.append(f"orphan children: {orphans[:5]}")
# no fabricated PASS
for coll in (parents, children, surfaces):
    for r in coll:
        if r["status"] not in ("OPEN", "PARTIAL_EVIDENCE_ONLY", "PARTIAL_LOCAL_SCOPED"):
            errors.append(f"illegal status {r['id']}: {r['status']}")

if errors:
    print("COVERAGE CHECK FAIL:")
    for e in errors: print("  -", e)
    raise SystemExit(2)

meta = {
    "generated_by": "R6-TS07/24/25 gen script",
    "source_report_sha256": hashlib.sha256(R6.read_bytes()).hexdigest(),
    "honesty_rule": "OPEN rows require raw receipts before any PASS; frozen dispositions are history, not current execution",
}
files = {
    "child_outcome_ledger.json": {"schema": "SBL_R6_CHILD_OUTCOME_LEDGER/1", "meta": meta,
        "parents": parents, "children": children,
        "summary": {"parents": len(parents), "children": len(children),
                    "open": sum(1 for r in parents+children if r["status"]=="OPEN"),
                    "pass_claimed": 0}},
    "surface_c001_c038_ledger.json": {"schema": "SBL_R6_SURFACE_LEDGER/1", "meta": meta,
        "surfaces": surfaces, "summary": {"total": len(surfaces),
        "not_admitted": sum(1 for s in surfaces if "NOT_ADMITTED" in s["r6_state"])}},
    "source_identity_441_ledger.json": {"schema": "SBL_R6_SOURCE_IDENTITY_LEDGER/1", "meta": meta,
        "donors": donors, "slots": slots, "methods": methods, "named_identities": ids386,
        "summary": {"total": total441, "frozen": {"ACTIVE": 1, "NATIVE_SUBSTITUTED": 6, "STANDBY": 3,
        "PROHIBITED": 8, "DEFERRED": 423}, "current_executed_this_round": 0}},
}
for fname, payload in files.items():
    p = OUT / fname
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("wrote", p, p.stat().st_size, "bytes")
print("COVERAGE CHECK PASS (50/149/38/441, 0 dup, 0 orphan, 0 fabricated PASS)")
