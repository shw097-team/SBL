#!/usr/bin/env python3
"""build_r27.py — mechanical construction of the r27 append-only candidate.

  r27 = r26 bytes (verbatim) + "\n" + CH27 chapter bytes

No transformation is applied to the prefix: it is the exact byte string read from
the frozen r26 file, so `r27[:len(r26)] == r26` by construction (proved afterwards
by check_append_only.py, not assumed here).
"""
import hashlib
import sys

R26 = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs/evidence/fhs-w0-r26-repair-20261109/doc/FHS_PIPD-LS-PKG_W0_r26.md"
CH = "C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/L7/ch27_chapter.md"
OUT = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs/evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    r26 = open(R26, "rb").read()
    ch = open(CH, "rb").read()
    if b"\r" in ch:
        print("REFUSING: the chapter file contains CR; the repository normalises *.md to LF")
        return 3
    if not ch.startswith(b"## CH27"):
        print("REFUSING: the chapter does not start with the required heading '## CH27'")
        return 4
    out = r26 + b"\n" + ch
    if not out.endswith(b"\n"):
        out += b"\n"
    open(OUT, "wb").write(out)
    print("r26   bytes=%d sha256=%s" % (len(r26), sha(r26)))
    print("ch27  bytes=%d sha256=%s" % (len(ch), sha(ch)))
    print("r27   bytes=%d sha256=%s" % (len(out), sha(out)))
    print("prefix check (in-process, informational):", out[:len(r26)] == r26)
    print("written:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
