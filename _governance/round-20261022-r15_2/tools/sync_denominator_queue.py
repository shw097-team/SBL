"""Make every open denominator row visible in the queue, without inventing commands.

A row with no explicit recipe becomes an item in status NEEDS_RECIPE: visible, countable, and impossible to
mistake for work the driver can run. DONE rows are never touched, so a replay cannot resurrect finished work.
"""
import json, os, sys
R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
DEN = os.path.join(R, "DENOMINATOR_R15_2.json")
Q = os.path.join(R, "QUEUE_R15_2.json")
RECIPES = os.path.join(R, "DENOMINATOR_RECIPES.json")
OWNER = {"C19": "OWNER", "C21": "HOST", "C24": "OWNER", "M3": "OWNER", "W12": "OWNER"}

def rows(den):
    for coll in ("checkruns", "workpackages", "eseries", "milestones"):
        for it in den.get(coll) or []:
            yield coll, it

def main() -> int:
    den = json.load(open(DEN, encoding="utf-8"))
    q = json.load(open(Q, encoding="utf-8"))
    recipes = json.load(open(RECIPES, encoding="utf-8")) if os.path.exists(RECIPES) else {"recipes": {}}
    have = {i["id"] for i in q["items"]}
    by_ref = {}
    for i in q["items"]:
        ref = i.get("denominator_ref") or ""
        for tok in ref.replace("/", " ").replace(",", " ").split():
            by_ref.setdefault(tok, i["id"])
    added, covered, needs = [], [], []
    for coll, it in rows(den):
        rid, st = it.get("id"), it.get("status")
        if st == "DONE":
            continue
        if rid in by_ref or ("DEN-" + rid) in have:
            covered.append(rid)
            needs.append(rid)
            continue
        rid_key = "DEN-" + rid
        if rid_key in have:
            covered.append(rid)
            continue
        rec = ((recipes.get("recipes") or {}).get(rid)) or {}
        q["items"].append({"id": rid_key, "owner_class": "AGENT",
                           "status": "READY" if rec else "NEEDS_RECIPE",
                           "denominator_ref": rid, "satisfiable_by": OWNER.get(rid, "AGENT"),
                           "next_action": (rec or {}).get("next_action") or f"author a bounded recipe for {coll} row {rid}",
                           "resume_cmd": (rec or {}).get("resume_cmd", ""),
                           "expect": (rec or {}).get("expect", ""),
                           "coverage_only": True})
        added.append(rid_key)
    from collections import Counter
    q["counts"] = dict(Counter(i.get("status") for i in q["items"]))
    q["coverage"] = {"at": __import__("time").strftime("%FT%TZ", __import__("time").gmtime()),
                     "added": added, "already_covered": covered}
    json.dump(q, open(Q, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(json.dumps({"added": len(added), "covered": len(covered), "counts": q["counts"]}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
