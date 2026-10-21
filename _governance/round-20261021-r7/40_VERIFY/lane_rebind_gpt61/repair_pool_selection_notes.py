#!/usr/bin/env python
"""Repair the per-lane `selection_note` in the canonical pool.

DEFECT (found by reading the pool, not by the conformance suite):
after the owner order of 2026-10-21 that promoted GPT 6.1 SOL to rank 1 on
PLAN and VERIFY_SECURITY, every lane's `selection_note` still read:

    "Owner order 2026-10-21: minimax-m3.1-flash-free (opencode-go) is rank 1
     and the automatic selection for <LANE>."

which is FALSE for two of the three lanes and contradicts the same file's
`declared_by`, its `change_log`, and the actual `ordered_pool[0]`. A
human reading the note would conclude MiniMax is the PLAN binding, and that
is precisely the confusion the owner asked to be avoided (lane binding vs
session pin).

The note is regenerated FROM the pool's own rank-1 entry, so it cannot drift
from the pool again: a future re-bind changes ordered_pool[0], and the next
run of this script rewrites the note to match. The note also records the
transport id convention, which differs per arm -- the OpenAI transport needs
the BARE id (`gpt-6.1-sol`), while the OpenCode Go transport takes the
provider-qualified slug (`opencode-go/deepseek-v4.1-flash`).

The claim_ceiling of the note is preserved in substance: a rank-1 arm is the
lane's default selection, the arms below it stay reachable as fallbacks, and
no note claims an acceptance.

Pre-image digest guard: the file is only written if its sha256 matches what
was read, so a concurrent writer cannot be silently overwritten.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
POOL = HGK / "config" / "lane-route-slots.candidate.json"
BACKUP = HGK / "var" / "R7-LANES" / f"pool-pre-note-repair-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"

OWNER_ORDER = (
    "Owner order 2026-10-21 (GPT quota restored): the PLAN execution model and the "
    "Independent Acceptance Officer / VERIFY / SECURITY checker model are BOTH "
    "openai-codex/gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OpenAI OAuth). This SUPERSEDES the "
    "earlier 2026-10-21 order that put minimax-m3.1-flash-free on PLAN and "
    "VERIFY_SECURITY. The EXECUTE lane is not named by the order and stays on "
    "opencode-go/deepseek-v4.1-flash, per the owner's standing clarification."
)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def transport_note(tm: str) -> str:
    """Explain the transport id convention for this arm."""
    if tm == "gpt-6.1-sol":
        return (
            "The transport id is the BARE 'gpt-6.1-sol': the OpenAI transport rejects the "
            "provider-qualified form 'openai-codex/gpt-6.1-sol' with HTTP 400 'Model is "
            "unavailable'."
        )
    return f"The transport id is the provider-qualified slug '{tm}'."


def build_note(lane: str, arm: dict, pool: dict) -> str:
    provider = arm.get("provider")
    model = arm.get("model")
    tm = arm.get("transport_model") or f"{provider}/{model}"
    effort = arm.get("reasoning_effort")
    qualifier = f" with reasoning effort {effort}" if effort else ""
    fb = [f"{a.get('provider')}/{a.get('model')}" for a in (arm.get("fallbacks") or [])]
    fb_txt = (
        "The arms below it stay reachable as fallbacks (first fallback: "
        + fb[0]
        + ")."
        if fb
        else "The arms below it stay reachable as fallbacks."
    )
    return (
        f"{OWNER_ORDER} For THIS lane ({lane}) the rank-1 arm is {provider}/{model}"
        f"{qualifier}, and it is the lane's automatic selection. "
        f"{transport_note(tm)} {fb_txt} "
        "A rank-1 arm is a SELECTION, not an acceptance: it says which model the lane "
        "dispatches to, not that anything has been accepted."
    )


def main() -> int:
    pre = sha256(POOL)
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(POOL, BACKUP)
    print("backup  :", BACKUP.name)
    print("pre     :", pre)

    changed = []
    for lane in pool["lanes"]:
        arm = lane["ordered_pool"][0]
        new = build_note(lane["lane"], arm, pool)
        if lane.get("selection_note") != new:
            changed.append((lane["lane"], arm.get("provider"), arm.get("model")))
            lane["selection_note"] = new

    if not changed:
        print("no change needed")
        return 0

    # bump the revision and append to the change_log -- the pool records its
    # own history, and a silent edit would leave the history lying.
    try:
        rev = int(pool.get("revision"))
        pool["revision"] = rev + 1
    except (TypeError, ValueError):
        pool["revision"] = str(pool.get("revision")) + "+note-repair"
    pool.setdefault("change_log", []).append({
        "rev": f"note-repair -> {pool['revision']}",
        "utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "round": "OWNER-ORDER-20261021-GPT-QUOTA-RESTORED",
        "what": (
            "Repaired each lane's selection_note so it states THAT lane's actual rank-1 arm. "
            "The notes still read 'minimax-m3.1-flash-free ... is rank 1' on all three lanes, "
            "contradicting the same file's declared_by, change_log and ordered_pool[0]. A "
            "reviewer reading the note would have concluded MiniMax was the PLAN binding -- "
            "exactly the lane-vs-session confusion the order was meant to end. The note is now "
            "generated from ordered_pool[0] so it cannot drift again."
        ),
        "lanes_changed": [{"lane": l, "rank1": f"{p}/{m}"} for l, p, m in changed],
    })

    # pre-image guard: refuse to write if the file changed under us
    if sha256(POOL) != pre:
        print("REFUSING TO WRITE: the pool changed under this script (concurrent writer)")
        return 2

    POOL.write_text(json.dumps(pool, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("post    :", sha256(POOL))
    print("changed :", changed)
    print("revision:", pool["revision"])

    # read back and verify each note names its own lane's real rank-1
    check = json.loads(POOL.read_text(encoding="utf-8"))
    for lane in check["lanes"]:
        arm = lane["ordered_pool"][0]
        note = lane["selection_note"]
        assert f"{arm.get('provider')}/{arm.get('model')}" in note, lane["lane"]
        assert "minimax-m3.1-flash-free (opencode-go) is rank 1" not in note, lane["lane"]
        print(f"  OK {lane['lane']:16s} note names {arm.get('provider')}/{arm.get('model')}")
    print("\nread-back: every note names its own lane's actual rank-1 arm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
