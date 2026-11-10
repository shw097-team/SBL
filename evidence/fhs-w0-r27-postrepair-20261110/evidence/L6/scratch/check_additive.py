# -*- coding: utf-8 -*-
"""Compare the admission manifest against its pre-change baseline, key by key.

Proves the "preserve every existing entry byte-for-byte; only add" rule as a
measurement instead of a promise: every baseline key must be present and equal, and
the only new top-level key may be `subject_admissions`.
"""
import json
import sys
from pathlib import Path

new = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
old = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

added = [k for k in new if k not in old]
removed = [k for k in old if k not in new]
changed = [k for k in old if k in new and new[k] != old[k]]

print(f"baseline keys: {len(old)}   new keys: {len(new)}")
print(f"added:   {added}")
print(f"removed: {removed}")
print(f"changed: {changed}")
for key in old:
    same = key in new and new[key] == old[key]
    print(f"  {'SAME   ' if same else 'DIFFER '} {key}")
ok = not removed and not changed and added == ["subject_admissions"]
print("ADDITIVE_ONLY:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
