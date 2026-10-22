"""Rewrite the canonical source ledger as a complete projection of the project's native intake.

The ledger previously covered only the 24 frozen documents while the intake bound 30 markdown files (it walks
recursively, so PIPD_LS/藍圖 contributes 6 more). A projection that silently drops admitted sources is not canonical,
so this rebuilds it from the intake itself and classifies each entry.
"""
import json
import os

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
admit = json.load(open(os.path.join(R, "receipts", "admission", "native_admit_close.json"), encoding="utf-8"))
freeze = json.load(open(os.path.join(R, "SOURCE_FREEZE.json"), encoding="utf-8"))

frozen_hashes = {(d.get("observed") or {}).get("sha256") for d in freeze["documents"]}
frozen_hashes.discard(None)

inv = admit["intake"]["inventory"]
rows = []
for s in inv:
    name = os.path.basename(s["path"])
    rel = s["path"].replace("\\", "/")
    blue = "/藍圖/" in rel or "\\藍圖\\" in s["path"]
    rows.append({
        "source_id": name,
        "path": rel,
        "sha256": s["sha256"],
        "bytes": s.get("bytes"),
        "frozen": s["sha256"] in frozen_hashes,
        "ledger_class": "NORMATIVE" if s["sha256"] in frozen_hashes else "SUPPLEMENTARY_BLUEPRINT",
        "outcome": "NATIVE_INTAKE_ADMITTED",
        "family": "PIPD_LS_BLUEPRINT" if blue else "SBL_PIPD-LS-PKG",
    })
rows.sort(key=lambda r: (r["ledger_class"] != "NORMATIVE", r["source_id"]))

obj = {
    "workorder": "WO-TS-20261022-02",
    "objective": "canonical source ledger covering every admitted source",
    "project_id": "sbl-r152-close-20261022c",
    "native_intake_source_count": admit["intake"]["source_count"],
    "ledger_entries": len(rows),
    "distinct_sha256": len({r["sha256"] for r in rows}),
    "entries_that_are_frozen_documents": sum(1 for r in rows if r["frozen"]),
    "entries_that_are_supplementary": sum(1 for r in rows if not r["frozen"]),
    "coverage_statement": ("every hash the native intake bound appears here exactly once; the 24 frozen documents are "
                           "classified NORMATIVE and the remaining admitted sources are classified SUPPLEMENTARY_BLUEPRINT "
                           "rather than dropped"),
    "why_this_changed": ("the first version projected SOURCE_FREEZE only, so 6 admitted sources were absent and a checker "
                         "correctly failed it — an incomplete projection is not a canonical ledger"),
    "rows": rows,
}
p = os.path.join(R, "evidence", "WO-TS-20261022-02", "source_ledger.json")
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: obj[k] for k in ("ledger_entries", "distinct_sha256", "entries_that_are_frozen_documents",
                                      "entries_that_are_supplementary", "native_intake_source_count")}, ensure_ascii=False))
