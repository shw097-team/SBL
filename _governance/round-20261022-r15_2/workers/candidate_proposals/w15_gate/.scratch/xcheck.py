"""Independent cross-check: let `git diff --no-index` describe the same edit, then compare changed lines.

The real file is copied read-only into a scratch pair; git (not difflib, not my parser) produces the diff. Only the
+/- lines are compared, because hunk offsets legitimately differ between generators.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess

SRC = r"C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lifecycle.py"
X = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/candidate_proposals/w15_gate/.scratch/xcheck"
PROP = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/candidate_proposals/w15_gate/proposal.diff"

COND_OLD = '        if to_state == "DELIVERED":'
COND_NEW = '        if to_state in ("DELIVERY_READY", "DELIVERED"):'
ERR_OLD = '{open_rows} required workorders open")'
ERR_NEW = '{open_rows} required workorders open (refused at {to_state})")'


def main() -> int:
    a = os.path.join(X, "a", "src", "hg_kseos", "lifecycle.py")
    b = os.path.join(X, "b", "src", "hg_kseos", "lifecycle.py")
    os.makedirs(os.path.dirname(a), exist_ok=True)
    os.makedirs(os.path.dirname(b), exist_ok=True)
    shutil.copyfile(SRC, a)
    text = open(a, "rb").read().decode("utf-8")
    counts = {"cond_old": text.count(COND_OLD), "err_old": text.count(ERR_OLD)}
    edited = text.replace(COND_OLD, COND_NEW).replace(ERR_OLD, ERR_NEW)
    open(b, "wb").write(edited.encode("utf-8"))

    out = subprocess.run(["git", "-C", X, "diff", "--no-index", "--no-color", "-U6",
                          "a/src/hg_kseos/lifecycle.py", "b/src/hg_kseos/lifecycle.py"],
                         capture_output=True, text=True, encoding="utf-8")
    git_diff = out.stdout.replace("\r\n", "\n")
    git_changed = [ln for ln in git_diff.split("\n")
                   if (ln.startswith("+") or ln.startswith("-"))
                   and not ln.startswith("+++") and not ln.startswith("---")]
    prop_text = open(PROP, "rb").read().decode("utf-8").replace("\r\n", "\n")
    prop_changed = [ln for ln in prop_text.split("\n")
                    if (ln.startswith("+") or ln.startswith("-"))
                    and not ln.startswith("+++") and not ln.startswith("---")]

    result = {
        "anchor_occurrences_in_file": counts,
        "git_hunks": git_diff.count("\n@@") + (1 if git_diff.startswith("@@") else 0),
        "git_changed_lines": len(git_changed),
        "proposal_changed_lines": len(prop_changed),
        "changed_lines_identical": git_changed == prop_changed,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["changed_lines_identical"]:
        print("GIT:", json.dumps(git_changed, ensure_ascii=False, indent=1))
        print("PROP:", json.dumps(prop_changed, ensure_ascii=False, indent=1))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
