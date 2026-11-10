"""Count `preservation` keys per clause per work package from the signed reader receipts. Read-only.

Answers EC-R26-004's denominator: 19 clauses x 4 properties = 76 for the four unaffected WPs.
"""
from __future__ import annotations

import glob
import json
import sys

PROPS = ("parent_preserved", "exceptions_preserved", "negations_preserved", "scope_preserved")
UNAFFECTED = ("WP-FHS-15", "WP-FHS-16", "WP-FHS-19", "WP-FHS-21")

d = sys.argv[1] if len(sys.argv) > 1 else "receipts/reader"
rows, tot_clauses, tot_props = [], 0, 0
for f in sorted(glob.glob(d + "/*.signed.json")):
    body = json.load(open(f, encoding="utf-8"))["body"]
    clauses = body.get("clauses") or []
    n_p = sum(len(c.get("preservation") or {}) for c in clauses)
    same_keyset = all(set((c.get("preservation") or {}).keys()) == set(PROPS) for c in clauses)
    rows.append((body.get("Subject"), len(clauses), n_p, same_keyset))
    tot_clauses += len(clauses)
    tot_props += n_p

print(f"{'WP':<12}{'clauses':>8}{'properties':>12}{'props/clause':>14}  keyset==4")
for wp, nc, np_, same in rows:
    print(f"{wp:<12}{nc:>8}{np_:>12}{np_ / nc:>14.2f}  {same}")
print(f"{'TOTAL':<12}{tot_clauses:>8}{tot_props:>12}")

uc = sum(nc for wp, nc, _, _ in rows if wp in UNAFFECTED)
up = sum(np_ for wp, nc, np_, _ in rows if wp in UNAFFECTED)
print(f"\nunaffected WPs: {list(UNAFFECTED)}")
print(f"unaffected clauses={uc} properties={up} expected {uc} x 4 = {uc * 4}")
print("ACK r26 claim '32-4=28' -> " + ("DISAGREE" if up != 28 else "agree"))
for wp, nc, np_, _ in rows:
    if wp in UNAFFECTED:
        print(f"   {wp}: clauses={nc} properties={np_}")
