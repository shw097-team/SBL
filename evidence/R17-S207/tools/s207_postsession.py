"""S2-07 OD-13: prove or refuse the post-session autonomous dispatch claim.

Reads (all read-only): runner/journal.jsonl, runner/rg04/RG04_*.json, hermes cron
executions.db, hermes state.db (session/message timestamps), job row.
Emits receipts/R17_S207_POSTSESSION.json and prints a compact verdict.

The claim under test is narrow:
  a scheduled FIRE happened while NO agent turn was executing, and that fire
  dispatched a work card which completed with its own raw artefact.
Nothing here can prove the desktop process died; that is reported separately.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
HERMES = Path(os.environ["LOCALAPPDATA"]) / "Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes"
OUT = VAR / "receipts/R17_S207_POSTSESSION.json"
JOB_ID = "3602bce285e8"
TPE = timezone(timedelta(hours=8))


def loc(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, TPE).isoformat(timespec="seconds")


def parse_journal():
    f = VAR / "runner/journal.jsonl"
    raw = f.read_text(encoding="utf-8", errors="replace").splitlines()
    cycles, cards, cur = [], [], None
    for line in raw:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "cycle":
            cur = ev.get("ts")
            cycles.append({"ts": ev.get("ts"), "cards": [c.get("card") for c in ev.get("cards", [])],
                           "stages": [s.get("stage") for s in ev.get("stages", [])],
                           "n_cards": len(ev.get("cards", []))})
        elif ev.get("type") == "card":
            cards.append({"cycle_ts": cur, "card": ev.get("card"), "child_exit": ev.get("child_exit"),
                          "command": ev.get("command"), "class": ev.get("class"),
                          "stdout_sha256": (ev.get("raw") or {}).get("stdout_sha256")})
    return cycles, cards


def journal_digest():
    f = VAR / "runner/journal.jsonl"
    return hashlib.sha256(f.read_bytes()).hexdigest()


def fire_rows():
    f = HERMES / "cron/executions.db"
    con = sqlite3.connect(f"file:{f}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "select id, job_id, source, pid, status, started_at, finished_at, error "
        "from executions where job_id=? order by started_at", (JOB_ID,)).fetchall()]
    con.close()
    return rows


def message_bounds():
    """Timestamps of the last message before, and first after, each candidate window."""
    f = HERMES / "state.db"
    con = sqlite3.connect(f"file:{f}?mode=ro", uri=True)
    cur = con.cursor()
    rows = cur.execute(
        "select session_id, role, timestamp, substr(content,1,60) from messages "
        "where timestamp > ? order by timestamp", (1792830000.0,)).fetchall()
    con.close()
    return [{"session_id": r[0], "role": r[1], "ts": r[2], "local": loc(r[2]),
             "head": (r[3] or "")[:60]} for r in rows]


def rg04():
    out = {}
    for p in sorted((VAR / "runner/rg04").glob("RG04_*.json")):
        try:
            out[p.name] = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:  # noqa: BLE001
            out[p.name] = {"_error": repr(e)}
    return out


def main():
    cycles, cards = parse_journal()
    fires = fire_rows()
    msgs = message_bounds()
    g = rg04()

    # cycles that actually dispatched a card
    dispatching = [c for c in cycles if c["n_cards"] > 0]
    for c in dispatching:
        ts = c["ts"].replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        c["local"] = dt.astimezone(TPE).isoformat(timespec="seconds")
        c["epoch"] = dt.timestamp()

    # agent-turn windows from the message log: a turn is "open" from a user message
    # until the last assistant/tool message that follows it before the next user msg.
    turns = []
    for i, m in enumerate(msgs):
        if m["role"] == "user":
            end = None
            for n in msgs[i + 1:]:
                if n["role"] == "user":
                    break
                end = n["ts"]
            turns.append({"start": m["ts"], "end": end or m["ts"],
                          "start_local": m["local"], "end_local": loc(end or m["ts"]),
                          "head": m["head"]})

    verdicts = []
    for c in dispatching:
        e = c["epoch"]
        # a fire is "turn-free" if it lies strictly after every completed turn's end
        # and strictly before the next turn's start
        after = [t for t in turns if t["end"] < e]
        before = [t for t in turns if t["start"] > e]
        open_now = [t for t in turns if t["start"] <= e <= t["end"]]
        turn_free = bool(after) and bool(before) and not open_now
        verdicts.append({
            "cycle_local": c["local"],
            "cards": c["cards"],
            "turn_free": turn_free,
            "inside_agent_turn": bool(open_now),
            "prev_turn_end_local": max((t["end"] for t in after), default=None) and loc(max(t["end"] for t in after)),
            "next_turn_start_local": loc(min(t["start"] for t in before)) if before else None,
        })

    g_file = g.get("RG04_G.json", {})
    proof = {
        "schema": "R17_S207_POSTSESSION/1",
        "generated_local": datetime.now(TPE).isoformat(timespec="seconds"),
        "job_id": JOB_ID,
        "journal_sha256": journal_digest(),
        "journal_cycles": len(cycles),
        "journal_card_events": len(cards),
        "dispatching_cycles": [c for c in dispatching],
        "idle_cycles_after": [
            {"local": datetime.fromisoformat(c["ts"].replace("Z", "+00:00"))
             .astimezone(TPE).isoformat(timespec="seconds")}
            for c in cycles if c["n_cards"] == 0],
        "turns_observed": [{"start_local": t["start_local"], "end_local": t["end_local"],
                            "head": t["head"]} for t in turns],
        "fire_turn_analysis": verdicts,
        "rg04_g": g_file,
        "rg04_files": sorted(g),
        "fire_rows": [{"started_at": r["started_at"], "status": r["status"],
                       "pid": r["pid"], "source": r["source"], "error": r["error"]} for r in fires],
        "card_events_tail": cards[-8:],
    }

    # verdict
    post = [v for v in verdicts if v["turn_free"]]
    if post and g_file.get("tag", "").upper() == "G":
        verdict = "POST_TURN_AUTONOMOUS_DISPATCH_MEASURED"
        note = ("a scheduled fire dispatched a card while no agent turn was open; "
                "see fire_turn_analysis for the bracketing turn timestamps")
    elif post:
        verdict = "POST_TURN_FIRE_MEASURED_CARD_ARTEFACT_UNCLEAR"
        note = "turn-free fire dispatched cards but RG04_G.json does not confirm tag G"
    else:
        verdict = "POST_SESSION_DISPATCH_UNVERIFIED"
        note = "no dispatching fire found outside an agent turn"
    proof["verdict"] = verdict
    proof["verdict_note"] = note
    proof["claim_ceiling"] = ("measurement shows the host fired and dispatched with no "
                             "agent turn open; it does NOT show the desktop process ended")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "out": str(OUT),
                      "dispatching": [v["cycle_local"] for v in verdicts],
                      "turn_free": [v["cycle_local"] for v in post]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
