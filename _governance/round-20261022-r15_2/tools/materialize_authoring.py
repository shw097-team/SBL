"""Turn command-less authoring obligations into executable AUTHOR actions.

FAR ruling (PLAN__FAR_WHY_STOP_4): the round keeps stopping because unfinished authoring is stored as
NEEDS_RECIPE - counted, visible, and unexecutable. The driver can only run a command, so a state without a
command is indistinguishable from "nothing to do". This module gives every such item exactly one bounded
authoring brief and the mandated EXECUTE dispatch as its command; it never invents a pass and never touches DONE.

Idempotent: an item that already carries author_brief is left alone, so a second run changes nothing.
"""
from __future__ import annotations

import hashlib
import json
import os

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
WORKTREE = r"C:/Projects/Agent_Workspace/_r152_ev"
Q = os.path.join(R, "QUEUE_R15_2.json")
# run_lane resolves --brief relative to the round dir (its cwd), so briefs live there, not in the worktree
BRIEF_DIR = os.path.join(R, "workers", "codex_exec")

BRIEF = """# EXECUTE brief — {title}

You are the bounded writer on the EXECUTE lane. One artefact, one run, no sub-agents.

## Obligation
{item_id} ({den_id}). recipe_hint: {hint}

## Write exactly this
`{artefact}`

- A pytest module. No fixture may write outside the repo; no `tmp_path` under a system temp root; no network.
- One behaviour per test, at most 8 tests. Each test asserts a real product rule, not that a function exists.
- Keep the module under ~200 lines so the run finishes inside the lane's 330 s cap.
- Do not edit any other file. Do not edit the queue, the mandate or the receipts.

## Acceptance commands (run them yourself before you finish)
```
cd C:/Projects/Agent_Workspace/_r152_ev
python -m pytest {artefact} -q
```
If a test cannot pass because the product lacks the rule, write the test to assert what the governing document
actually requires and mark it `xfail(strict=True, reason="<the missing rule>")` - never weaken an assertion to make
it green.

## Refuse
Claiming the check is done, writing a placeholder test, touching DONE items, or reporting acceptance.
"""


def _hint(item: dict, recipes: dict) -> str:
    rec = (recipes.get("recipes") or {}).get(item.get("den_id") or "") or {}
    return (item.get("recipe_hint") or rec.get("recipe_hint") or rec.get("why") or "author the missing test").strip()


def materialise(queue: dict, recipes: dict, brief_dir: str = BRIEF_DIR) -> list[dict]:
    """Give every command-less authoring item one brief and one dispatch command. Returns what changed."""
    os.makedirs(brief_dir, exist_ok=True)
    changed = []
    for i in queue["items"]:
        # any unfinished item that carries an authoring obligation - by status, by needs_test, or by a recorded brief -
        # is reconsidered; the on-disk check below decides whether it still needs materialising
        needs = (i["status"] == "NEEDS_RECIPE" or bool(i.get("needs_test")) or bool(i.get("author_brief")))
        if not (needs and i.get("owner_class") == "AGENT"):
            continue
        # a brief recorded on the item but absent on disk is a broken obligation, not a done one
        if i.get("author_brief") and os.path.exists(os.path.join(R, i["author_brief"])):
            continue
        art = i.get("expect_artefact") or (i.get("artefact") or "")
        if not art:
            art = "tests/test_%s.py" % i["id"].split(".")[0].lower().replace("-", "_")
        bp = os.path.join(brief_dir, i["id"].replace(".", "_") + ".md")
        text = BRIEF.format(title=i.get("title") or i["id"], item_id=i["id"], den_id=i.get("den_id", "?"),
                            hint=_hint(i, recipes), artefact=art)
        open(bp, "w", encoding="utf-8", newline="\n").write(text)
        rel_brief = os.path.relpath(bp, R).replace("\\", "/")
        i.update({
            "status": "READY",
            "phase": "AUTHOR",
            "needs_test": True,
            "author_brief": rel_brief,
            "expect_artefact": art,
            "accept_cmd": "python -m pytest %s -q" % art,
            "resume_cmd": ("python _governance/round-20261022-r15_2/tools/run_lane.py --role EXECUTE "
                           "--brief %s --nonce %s-AUTHOR-%s --timeout 300" % (
                               rel_brief, i["id"].replace(".", "_"), hashlib.sha256(rel_brief.encode()).hexdigest()[:8])),
            "expect": r'"nonce":\s*true',
            "timeout_s": 340,
            "next_action": "AUTHOR %s via EXECUTE lane (brief %s)" % (art, rel_brief),
            "attempts": 0,
        })
        i.pop("parked_reason", None)
        i.pop("retry_hint", None)
        changed.append({"id": i["id"], "brief": rel_brief, "artefact": art})
    return changed


def main() -> int:
    q = json.load(open(Q, encoding="utf-8"))
    rp = os.path.join(R, "DENOMINATOR_RECIPES.json")
    recipes = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {}
    changed = materialise(q, recipes)
    json.dump(q, open(Q, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(json.dumps({"materialised": len(changed), "items": changed}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
