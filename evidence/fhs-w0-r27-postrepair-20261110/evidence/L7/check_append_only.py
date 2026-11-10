#!/usr/bin/env python3
"""check_append_only.py — the r27 document's own append-only guard.

Refuses any r27 whose first N bytes are not identical to the whole r26 file.
Exit 0 / PREFIX_IDENTICAL ; exit 1 / PREFIX_NOT_IDENTICAL ; exit 2 / PREFIX_TRUNCATED.
Read-only.
"""
import argparse
import hashlib
import json
import sys


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r26", required=True)
    ap.add_argument("--r27", required=True)
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    r26 = open(a.r26, "rb").read()
    r27 = open(a.r27, "rb").read()
    rep = {
        "r26": {"path": a.r26, "bytes": len(r26), "sha256": sha(r26)},
        "r27": {"path": a.r27, "bytes": len(r27), "sha256": sha(r27)},
    }

    if len(r27) < len(r26):
        rep.update(prefix_identical=False, code="PREFIX_TRUNCATED",
                   detail="r27 (%d bytes) is shorter than r26 (%d bytes)" % (len(r27), len(r26)))
        rc = 2
    else:
        prefix = r27[:len(r26)]
        same = prefix == r26
        rep["prefix"] = {"bytes": len(prefix), "sha256": sha(prefix)}
        if same:
            rep.update(prefix_identical=True, prefix_bytes=len(prefix),
                       r27_bytes=len(r27), appended_bytes=len(r27) - len(r26),
                       code="PREFIX_IDENTICAL", status="ACCEPT")
            rc = 0
        else:
            n = next(i for i in range(len(prefix)) if prefix[i] != r26[i])
            rep.update(prefix_identical=False, prefix_bytes=len(prefix), r27_bytes=len(r27),
                       first_diff_offset=n, code="PREFIX_NOT_IDENTICAL",
                       detail="prefix diverges from r26 at byte %d" % n)
            rc = 1

    for k in ("prefix_identical", "prefix_bytes", "r27_bytes", "r26_bytes", "appended_bytes"):
        pass
    print("prefix_identical: %s   prefix_bytes: %d   r26_bytes: %d   r27_bytes: %d   appended_bytes: %d"
          % (rep.get("prefix_identical"), rep.get("prefix_bytes", 0), len(r26), len(r27),
             rep.get("appended_bytes", 0)))
    print("r26 sha256 = %s  (%d bytes)" % (sha(r26), len(r26)))
    print("r27 prefix sha256 = %s" % sha(r27[:len(r26)]))
    print("r27 sha256 = %s  (%d bytes)" % (sha(r27), len(r27)))
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if a.json:
        open(a.json, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
