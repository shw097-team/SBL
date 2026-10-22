"""Build the W15 guard proposal from the real file, then verify the diff by re-applying it in memory.

Nothing here touches src/hg_kseos/lifecycle.py (opened read-only, bytes hashed before and after) and no
`git apply` is run. The diff is verified by parsing it back and reconstructing the after-image.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os

SRC = r"C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lifecycle.py"
OUT = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/candidate_proposals/w15_gate"

ANCHOR_OLD = '        if to_state == "DELIVERED":'
ANCHOR_NEW = '        if to_state in ("DELIVERY_READY", "DELIVERED"):'
ERR_OLD = ('                    f"ERR_PENDING_WORK_CANNOT_DELIVER {project_id}: '
           '{open_rows} required workorders open")')
ERR_NEW = ('                    f"ERR_PENDING_WORK_CANNOT_DELIVER {project_id}: '
           '{open_rows} required workorders open (refused at {to_state})")')


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    raw = open(SRC, "rb").read()
    before_digest = sha(raw)
    text = raw.decode("utf-8")
    assert "\r\n" in text, "expected CRLF working tree"
    lines = text.split("\r\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    old_idx = [i for i, ln in enumerate(lines) if ln == ANCHOR_OLD]
    err_idx = [i for i, ln in enumerate(lines) if ln == ERR_OLD]
    anchor_found = len(old_idx) == 1 and len(err_idx) == 1
    if not anchor_found:
        json.dump({"anchor_found": False, "guard_line_before": None, "guard_line_after": None,
                   "diff_lines": 0, "applied": False,
                   "why_not_applied": "control-plane change requires a HGK owner"},
                  open(os.path.join(OUT, "VERDICT.json"), "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=2)
        print(json.dumps({"anchor_found": False, "guard_line_candidates": [i + 1 for i in old_idx],
                          "err_line_candidates": [i + 1 for i in err_idx]}))
        return 1

    cond_line = old_idx[0] + 1
    err_line = err_idx[0] + 1

    after = list(lines)
    after[cond_line - 1] = ANCHOR_NEW
    after[err_line - 1] = ERR_NEW

    # n=6 so both edits land in a single hunk (they are 9 unchanged lines apart; difflib merges when
    # the gap is <= 2n). LF-only diff body; the file itself stays CRLF and is untouched.
    diff = "".join(difflib.unified_diff(
        [ln + "\n" for ln in lines], [ln + "\n" for ln in after],
        fromfile="a/src/hg_kseos/lifecycle.py",
        tofile="b/src/hg_kseos/lifecycle.py", n=6, lineterm="\n"))
    diff_text = diff if diff.endswith("\n") else diff + "\n"
    open(os.path.join(OUT, "proposal.diff"), "w", encoding="utf-8", newline="\n").write(diff_text)

    # Verify: parse the diff back, rebuild the after-image, and compare with the intended candidate.
    rebuilt: list[str] = []
    hunks = 0
    plus = minus = 0
    body = diff_text.split("\n")
    pos = 0
    i = 0
    while i < len(body):
        ln = body[i]
        if ln.startswith("@@"):
            hunks += 1
            head = ln.split("@@")[1].strip()
            start = int(head.split(" ")[0].split(",")[0].lstrip("-"))
            nlen = int(head.split(" ")[0].split(",")[1]) if "," in head.split(" ")[0] else 1
            rebuilt.extend(lines[pos:start - 1])
            pos = start - 1
            consumed = 0
            i += 1
            while consumed < nlen and i < len(body):
                cur = body[i]
                if cur == "":
                    break
                tag, payload = cur[0], cur[1:]
                if tag == " ":
                    assert payload == lines[pos], f"context mismatch at file line {pos + 1}"
                    rebuilt.append(payload)
                    pos += 1
                    consumed += 1
                elif tag == "-":
                    assert payload == lines[pos], f"minus mismatch at file line {pos + 1}"
                    pos += 1
                    minus += 1
                elif tag == "+":
                    rebuilt.append(payload)
                    plus += 1
                else:
                    raise SystemExit(f"unexpected diff line: {cur!r}")
                i += 1
            continue
        i += 1
    rebuilt.extend(lines[pos:])

    ok_rebuild = rebuilt == after
    one_hunk = hunks == 1
    only_two = (plus, minus) == (2, 2)

    after_digest = sha(open(SRC, "rb").read())
    verdict = {
        "anchor_found": True,
        "guard_line_before": lines[cond_line - 1],
        "guard_line_after": after[cond_line - 1],
        "diff_lines": len(diff_text.splitlines()),
        "applied": False,
        "why_not_applied": "control-plane change requires a HGK owner",
    }
    open(os.path.join(OUT, "VERDICT.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(verdict, ensure_ascii=False, indent=2) + "\n")

    print(json.dumps({
        "anchor_found": True,
        "condition_file_line": cond_line,
        "error_file_line": err_line,
        "hunks": hunks,
        "plus_lines": plus,
        "minus_lines": minus,
        "diff_lines": verdict["diff_lines"],
        "rebuild_matches_target": ok_rebuild,
        "single_hunk": one_hunk,
        "only_guard_and_error_changed": only_two,
        "src_digest_before": before_digest,
        "src_digest_after": after_digest,
        "src_unchanged": before_digest == after_digest,
    }, ensure_ascii=False, indent=2))
    return 0 if (ok_rebuild and one_hunk and only_two and before_digest == after_digest) else 1


if __name__ == "__main__":
    raise SystemExit(main())
