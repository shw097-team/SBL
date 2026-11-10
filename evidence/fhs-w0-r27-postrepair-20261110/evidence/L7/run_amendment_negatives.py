#!/usr/bin/env python3
"""run_amendment_negatives.py — executes the append-only amendment harness.

For each of the seven blueprints named in out/BLUEPRINT_AFFECTED_SCOPE_DELTA.md this
runs one accepted case and four refusals against a mutated COPY of the real file.
The knowledge-base originals are opened read-only and never written.

Expectations
  POS           exit 0  AMENDMENT_APPLIED        (prefix intact, anchor intact, marker once)
  NEG_PREFIX    exit 1  AMENDMENT_PREFIX_MISMATCH (one byte flipped inside the original)
  NEG_ANCHOR    exit 3  AMENDMENT_ANCHOR_MISSING  (anchor line rewritten in place)
  NEG_MARKER    exit 5  MARKER_MISSING            (append without the declared marker)
  NEG_DESIGNID  exit 4  DESIGNID_COUNT_DRIFT      (L1 only: proposal that would add a DesignID)

Exit 0 only if every observed (exit, code) equals the expectation.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, "neg")
KB = "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖"
SK = KB + "/各W藍圖&skeleton"
PY = sys.executable
CHECKER = os.path.join(HERE, "check_blueprint_amendment.py")

DOCS = [
    ("L0", KB + "/FHS_總藍圖_r4.md", 68, "- **唯一 Human Owner ≠ 單一技術 Principal**", 0),
    ("L1", KB + "/FHS_PIPD-LS-PKG_藍圖_r4.md", 1828, "**Hermes v0.22.5 pinned baseline**", 84),
    ("L2", KB + "/FHS_PIPD-LS-PKG_全波次藍圖_r4.md", 590, "| `ENGINEERING_PHASE_W0-A`", 0),
    ("W1", SK + "/FHS_PIPD-LS-PKG_W1_藍圖_skeleton_2026-11-04_r5.md", 110,
     "## W1-r5｜角色、產品規格與三庫工程入口", 0),
    ("W2", SK + "/FHS_PIPD-LS-PKG_W2_藍圖_skeleton_2026-11-04_r5.md", 87,
     "### 必要但未執行的原 PIPD 編譯順序", 0),
    ("W3", SK + "/FHS_PIPD-LS-PKG_W3_藍圖_skeleton_2026-11-04_r5.md", 123,
     "## 0.4｜跨波接口、效果分級與權限斷點", 0),
    ("W4", SK + "/FHS_PIPD-LS-PKG_W4_藍圖_skeleton_2026-11-04_r5.md", 242,
     "### 2.1A｜三相 Original Publisher 狀態機", 0),
]

TAIL = ("\n\n<!-- R27-APPEND:{doc} -->\n"
        "## r27 追加（提案，未生效）\n\n"
        "- harness stub: this is a PROPOSED_FOR_RATIFICATION span, not an applied amendment\n")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(doc, before_path, after_path, anchor_json, designids):
    cmd = [PY, CHECKER, "--doc-id", doc, "--before", before_path, "--after", after_path,
           "--marker", "R27-APPEND", "--anchor-json", anchor_json]
    if designids:
        cmd += ["--require-designids", str(designids)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    code = ""
    try:
        code = json.loads(p.stdout).get("code", "")
    except Exception:
        code = "UNPARSEABLE:" + (p.stdout or p.stderr)[:120]
    return p.returncode, code


def main():
    os.makedirs(NEG, exist_ok=True)
    rows, ok = [], True
    for doc, path, line, anchor, designids in DOCS:
        before = open(path, "rb").read()
        aj = os.path.join(NEG, "anchor_%s.json" % doc)
        json.dump({"line": line, "startswith": anchor}, open(aj, "w", encoding="utf-8"), ensure_ascii=False)

        tail = TAIL.format(doc=doc).encode("utf-8")
        cases = []

        pos = os.path.join(NEG, "%s_pos.md" % doc)
        open(pos, "wb").write(before + tail)
        cases.append(("POS", pos, 0, "AMENDMENT_APPLIED"))

        off = min(1000, len(before) - 1)
        flip = bytearray(before)
        while flip[off:off + 1] == b"\n":
            off += 1
        flip[off:off + 1] = b"X" if flip[off:off + 1] != b"X" else b"Y"
        negp = os.path.join(NEG, "%s_neg_prefix.md" % doc)
        open(negp, "wb").write(bytes(flip) + tail)
        cases.append(("NEG_PREFIX@%d" % off, negp, 1, "AMENDMENT_PREFIX_MISMATCH"))

        lines = before.split(b"\n")
        lines[line - 1] = b"Z" + lines[line - 1][1:]
        # an upstream re-publication that moved the anchor line: the pinned original
        # itself no longer carries the anchor, so the anchor check must refuse even
        # though the amendment is appended cleanly to the rewritten original.
        nega = os.path.join(NEG, "%s_neg_anchor.md" % doc)
        base = b"\n".join(lines)
        open(nega, "wb").write(base + tail)
        cases.append(("NEG_ANCHOR", nega, 3, "AMENDMENT_ANCHOR_MISSING", nega + ".base"))
        open(nega + ".base", "wb").write(base)

        negm = os.path.join(NEG, "%s_neg_marker.md" % doc)
        open(negm, "wb").write(before + b"\n\n## r27 append without the marker\n")
        cases.append(("NEG_MARKER", negm, 5, "MARKER_MISSING"))

        if designids:
            negd = os.path.join(NEG, "%s_neg_designid.md" % doc)
            open(negd, "wb").write(before + tail + b"\n- adds `FHS-DR-099` as a new DesignID\n")
            cases.append(("NEG_DESIGNID", negd, 4, "DESIGNID_COUNT_DRIFT"))

        print("## %s  (%s, %d bytes, sha256 %s)" % (doc, os.path.basename(path), len(before), sha(before)))
        for case in cases:
            name, fp, want_rc, want_code = case[:4]
            before_for_case = case[4] if len(case) > 4 else path
            rc, code = run(doc, before_for_case, fp, aj, designids)
            good = (rc == want_rc and code == want_code)
            ok = ok and good
            print("   %-18s exit=%d want=%d  code=%-26s want=%-26s %s"
                  % (name, rc, want_rc, code, want_code, "OK" if good else "MISMATCH"))
            rows.append({"doc": doc, "case": name, "input": fp, "input_sha256": sha(open(fp, "rb").read()),
                         "exit": rc, "code": code, "expected_exit": want_rc,
                         "expected_code": want_code, "ok": good})
        print()

    json.dump({"cases": rows, "all_ok": ok}, open(os.path.join(HERE, "amendment_negatives.json"), "w",
               encoding="utf-8"), ensure_ascii=False, indent=1)
    print("RESULT all_ok =", ok, " cases =", len(rows))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
