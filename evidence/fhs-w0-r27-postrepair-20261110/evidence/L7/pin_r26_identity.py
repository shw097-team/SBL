#!/usr/bin/env python3
"""pin_r26_identity.py — establish the two r26 identities and prove they are the
same document differing only in line endings.

  LF  form : evidence/fhs-w0-r26-repair-20261109/doc/FHS_PIPD-LS-PKG_W0_r26.md
             (667,205 bytes, the bytes git stores — .gitattributes eol=lf)
  raw form : the published/writeback copy (668,540 bytes) whose last chapters were
             written by a Windows tool, i.e. 1,335 CRLF lines

Read-only.
"""
import hashlib
import os

LF = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs/evidence/fhs-w0-r26-repair-20261109/doc/FHS_PIPD-LS-PKG_W0_r26.md"
RAW = ("C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/實作/W0/"
       "FHS_PIPD-LS-PKG_W0_r26.md")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    lf = open(LF, "rb").read()
    raw = open(RAW, "rb").read()
    print("LF  form : %s" % LF)
    print("             bytes=%d sha256=%s crlf_lines=%d lines=%d"
          % (len(lf), sha(lf), lf.count(b"\r\n"), lf.split(b"\n").__len__()))
    print("raw form : %s" % RAW)
    print("             bytes=%d sha256=%s crlf_lines=%d lines=%d"
          % (len(raw), sha(raw), raw.count(b"\r\n"), raw.split(b"\n").__len__()))

    print("\nbyte delta = %d ; both files have %d LF-split lines"
          % (len(raw) - len(lf), raw.split(b"\n").__len__()))
    print('raw.replace(b"\\r\\n", b"\\n") == lf  ->  %s' % (raw.replace(b"\r\n", b"\n") == lf))

    # where do they differ, line by line, and is every difference a line ending?
    la, lb = lf.split(b"\n"), raw.split(b"\n")
    diff = [i + 1 for i in range(min(len(la), len(lb))) if la[i] != lb[i]]
    only_cr = all(la[i - 1] == lb[i - 1].replace(b"\r", b"") for i in diff)
    print("differing lines = %d (first %s, last %s) ; every difference is a trailing CR -> %s"
          % (len(diff), diff[:2], diff[-2:], only_cr))
    print("first differing byte offset = %d" % next(
        i for i in range(min(len(lf), len(raw))) if lf[i] != raw[i]))
    print("G10 line in evidence/L3/gate_baseline.log already records: "
          "\"shipped copy is the LF form (09c666dad4f31099)\"")
    return 0 if raw.replace(b"\r\n", b"\n") == lf else 1


if __name__ == "__main__":
    raise SystemExit(main())
