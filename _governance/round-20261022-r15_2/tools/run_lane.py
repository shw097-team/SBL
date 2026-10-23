"""Run a mandated lane in one command, so using the lane is cheaper than bypassing it.

    python tools/run_lane.py --role PLAN    --brief workers/plan_brief/ROOT_CAUSE.md
    python tools/run_lane.py --role EXECUTE --brief workers/codex_exec/BRIEF.md
    python tools/run_lane.py --role VERIFY  --brief workers/verify/CHECK.md

Lane, provider/model and rank come from MANDATE_R15_2.json. A receipt lands in receipts/dispatch/ regardless of outcome,
so the gate can audit it afterwards.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
MANDATE = os.path.join(R, "MANDATE_R15_2.json")


def stamp_header(nonce: str) -> str:
    """The instruction that makes a nonce mean something.

    Measured: with a plain "begin your reply with this token", two EXECUTE runs satisfied it by echoing the token in a
    shell command, which the strict detector refuses (a script echoing the brief could fake acknowledgement). Asking
    for the token AND a one-sentence statement of the change makes an echo insufficient, without loosening the detector.
    """
    nl = chr(10)
    return (nl.join([
        "NONCE: " + nonce,
        "",
        "Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words",
        "naming the exact file you will change and what behaviour you will pin down.",
        "Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be",
        "part of your reply text, because a script replaying the brief is not an acknowledgement.",
        "",
        "HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent",
        "(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that",
        "in your output and stop.",
        "", ""]))


def main() -> int:
    if "--role" not in sys.argv or "--brief" not in sys.argv:
        print("usage: run_lane.py --role PLAN|EXECUTE|VERIFY --brief <file> [--nonce N] [--timeout 560]")
        return 2
    role = sys.argv[sys.argv.index("--role") + 1]
    brief = sys.argv[sys.argv.index("--brief") + 1]
    if not os.path.isabs(brief):
        brief = os.path.join(R, brief)
    if not os.path.exists(brief):
        print(f"BRIEF_MISSING {brief}")
        return 2
    roles = json.load(open(MANDATE, encoding="utf-8"))["roles"]
    if role not in roles:
        # the role key is not the lane name (VERIFY -> lane VERIFY_SECURITY); a bare KeyError reads like a broken
        # lane when it is a typo, so say which keys exist
        print("UNKNOWN_ROLE %r; mandate role keys: %s (lane names: %s)"
              % (role, list(roles), [v.get("lane") for v in roles.values()]))
        return 2
    m = roles[role]
    nonce = (sys.argv[sys.argv.index("--nonce") + 1] if "--nonce" in sys.argv
             else f"{m['lane']}-R152-{time.strftime('%H%M%S')}-{abs(hash(brief)) % 9999:04d}")
    tmo = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 560
    # The lane's contract is that the model echoes the nonce. A brief that never asks for it fails the receipt for a
    # reason that has nothing to do with the work — measured: 358s of real analysis, 166KB stdout, ok=False purely
    # because no nonce was echoed. So the instruction is injected, not remembered.
    brief_text = open(brief, encoding="utf-8").read()
    stamped = os.path.join(os.path.dirname(brief), "_" + os.path.basename(brief))
    open(stamped, "w", encoding="utf-8", newline=chr(10)).write(
        stamp_header(nonce)
        + brief_text)
    brief = stamped
    # A receipt must not be erasable by a later run of the same brief. Measured 2026-10-23: the green relay receipt for
    # a PLAN brief was overwritten 98 seconds later by a red OAuth run of the SAME brief, because both derived the name
    # from the brief alone. The tag is what keeps a different transport on a different file.
    _tag = os.environ.get("HGK_LANE_RECEIPT_TAG", "").strip()
    _tag = ("__" + "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in _tag)) if _tag else ""
    out = os.path.join(R, "receipts", "dispatch",
                       f"{m['lane']}_{os.path.basename(brief).replace('.md', '')}{_tag}.json")
    def hgk_state() -> str:
        q = subprocess.run(["git", "-C", HGK, "status", "--porcelain"], capture_output=True, text=True)
        return (q.stdout or "").strip()

    hgk_before = hgk_state()
    cmd = [sys.executable, "scripts/hgk-lane-dispatch.py", "--lane", m["lane"], "--prompt", brief,
           "--nonce", nonce, "--require-arm", m["provider_model"], "--force-rank", str(m["required_rank"]),
           "--pool", "config/lane-route-slots.candidate.json", "--cwd", R, "--timeout", str(tmo),
           "--json-out", out]
    # The relay base is not always the shared 10101 relay: when the sealed front door is the sanctioned transport
    # (HGK_LANE_RELAY_BASE=http://127.0.0.1:10100) the lane must be told, otherwise it connects to 10101 and dies on
    # 426/401 as measured on 2026-10-23.
    relay_base = os.environ.get("HGK_LANE_RELAY_BASE") or "http://127.0.0.1:10101/v1"
    # The /v1 suffix is not cosmetic. With a bare http://127.0.0.1:10101 the codex client builds
    # ws://127.0.0.1:10101/responses and http://127.0.0.1:10101/responses, burns seven upgrade retries and dies
    # (measured 2026-10-23: eight dispatches, each ~12 s, all with the identical URL). The front door refuses the
    # path without /v1 for the same reason. Default it here so no call site can get it wrong again.
    if relay_base and not (os.environ.get("HGK_LANE_HUMAN_HOME") and "HGK_LANE_RELAY_BASE" not in os.environ):
        cmd += ["--relay-base", relay_base]
    # THE OAUTH LANE. The sealed home has no auth.json, so whatever a relay answers it pays for itself: measured
    # 2026-10-23, :10101 returned 200 for gpt-6.1-sol with a bogus bearer token AND with no auth header at all, which
    # is why the owner's OpenAI OAuth account showed no consumption while PLAN/VERIFY receipts were green. Pointing
    # the lane at the human home makes codex present the owner's own OAuth token to the ChatGPT backend.
    human_home = os.environ.get("HGK_LANE_HUMAN_HOME")
    if human_home:
        cmd += ["--codex-home", human_home, "--allow-human-home-transport"]
    # Identity source. On an OAuth-direct turn the relay writes no usage row, so 'relay-usage' (the default) can only
    # report model=null and ok=false: the lane that actually pays is the one that looks broken. 'codex-rollout' reads
    # the arm the codex client recorded for this run/cwd instead. Never silently the other way round.
    ident_src = os.environ.get("HGK_LANE_IDENTITY_SOURCE")
    if ident_src:
        cmd += ["--identity-source", ident_src]
    # codex 0.163-alpha.11 negotiates the responses transport over websocket first; the local relay answers
    # 426 Upgrade Required and the front door answers 403 on ws://. Measured 2026-10-23. One -c override removes it:
    #   HGK_LANE_CODEX_ARGS='-c|features.responses_websocket=false'
    extra = os.environ.get("HGK_LANE_CODEX_ARGS")
    if extra:
        for arg in extra.split("|"):
            if arg.strip():
                cmd += ["--codex-arg=%s" % arg.strip()]
    env = dict(os.environ, PYTHONPATH="src")
    p = subprocess.run(cmd, cwd=HGK, capture_output=True, text=True, timeout=tmo + 90, env=env)
    tail = ((p.stdout or "") + (p.stderr or "")).strip().splitlines()[-2:]
    hgk_after = hgk_state()
    if hgk_after != hgk_before:
        new = [ln for ln in hgk_after.splitlines() if ln not in hgk_before.splitlines()]
        side = out.replace(".json", ".control_plane_delta.json")
        json.dump({"before": hgk_before.splitlines(), "after": hgk_after.splitlines(), "new": new,
                   "verdict": "LANE_TOUCHED_CONTROL_PLANE"},
                  open(side, "w", encoding="utf-8", newline=chr(10)), ensure_ascii=False, indent=2)
        print(f"LANE_TOUCHED_CONTROL_PLANE ({len(new)} new entries) -> {side}")
    print("dispatch_exit=", p.returncode)
    print("\n".join(tail))
    try:
        d = json.load(open(out, encoding="utf-8"))
        a = (d.get("attempts") or [{}])[0]
        print(json.dumps({"lane": d.get("lane"), "ok": d.get("ok"), "secs": a.get("seconds"),
                          "nonce": a.get("nonce_present"), "model": d.get("used_transport_model"),
                          "rank": d.get("used_rank"), "receipt": out}, ensure_ascii=False))
        return 0 if d.get("ok") else 1
    except Exception as exc:
        print(f"RECEIPT_UNREADABLE {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
