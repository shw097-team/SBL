"""N0: the ready-set driver that removes the "no worker running => stop the round" failure.

The rule this enforces (from the second interruption order, section 5):

    READY_COUNT > 0 AND ACTIVE_WORKERS = 0  =>  DISPATCH_NEXT_READY

It reads the queue, classifies every row into the seven classes, recomputes the legal ready set from the
measured evidence on disk, and names the next card WITH the exact command. `--run` executes exactly one card
and then recomputes; it never loops without re-reading the queue.

Classes
  DONE_VERIFIED            evidence on disk and the claim ceiling is recorded
  READY_READONLY           needs no write grant
  READY_ISOLATED_CANDIDATE candidate/patch work inside var/R17-20261023 only
  READY_ADMITTED_EFFECT    needs a native WorkOrder/Permit that we do not have yet -> never auto-run
  BLOCKED_SECURITY         credential/security refusal
  BLOCKED_OWNER            an owner signature is the only missing thing
  BLOCKED_DEPENDENCY       waits on another card
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import datetime

R17 = r"C:\Projects\Agent_Workspace\var\R17-20261023"
QUEUE = os.path.join(R17, "WORK_QUEUE_R17.json")

# card id -> (class, command, why). Only cards this round actually measured are listed; anything absent is
# BLOCKED_DEPENDENCY and must be classified by hand rather than guessed.
CARDS = {
    "W00": ("DONE_VERIFIED", None, "44/44 source freeze + F10 rebind"),
    "C00": ("BLOCKED_DEPENDENCY", None, "official C0..C9 compile rerun writes into SBL/contracts -> needs an SBL write grant (no such script exists in-round)"),
    "C01": ("READY_READONLY", "cd HG-KSEOS && PYTHONPATH=src /c/Users/user/.local/bin/uv.exe run --python 3.12 python -m hg_kseos doctor", "HGK doctor rerun"),
    "C02": ("BLOCKED_OWNER", None, "Fabric active designation"),
    "C07": ("READY_READONLY", "python var/R17-20261023/tools/join_lanes.py", "three-lane join refresh"),
    "C10": ("BLOCKED_OWNER", None, "gstack not admitted -> NoFit recorded"),
    "C11": ("READY_READONLY", "python var/R17-20261023/tools/hgk_native_abi_readback.py", "native ABI readback"),
    "C16": ("READY_READONLY", "cd PIPD && PYTHONPATH=src python -m pipd_ls_sp.cli doctor", "PIPD doctor + verb surface"),
    "W01": ("BLOCKED_DEPENDENCY", None, "conformance 6 PASS / 2 PARTIAL; the two PARTIAL skills need a PIPD fix (PR-009 class)"),
    "W05": ("BLOCKED_DEPENDENCY", None, "13 verbs probed; live doctor needs the PIPD symlink fix and validate needs the field/family fix"),
    "R16-F10": ("DONE_VERIFIED", None, "static oracle rebind"),
    "R16-F08": ("DONE_VERIFIED", None, "NoFit declaration"),
    "R16-F12": ("DONE_VERIFIED", "python var/R17-20261023/tools/join_lanes.py", "lane join artefact"),
    "R16-F13": ("BLOCKED_OWNER", None, "Fabric designation + path fix grant"),
    "R16-F06": ("READY_READONLY", "python var/R17-20261023/tools/hgk_native_abi_readback.py --selftest", "swarm fan-in evidence is the ABI selftest"),
    "DEL-01": ("DONE_VERIFIED", None, "freeze artefact"),
    "FABRIC-CANARY": ("READY_READONLY", "python var/R17-20261023/tools/fabric_consumer_canary.py",
                      "re-runnable Fabric consumer readback: 8/9 route, PROVIDER_CHANGE fail-closed"),
}


# ids that have a real read-only probe in tools/probe_all.py (the rest were phantom resume commands)
PROBE_IDS = {'W01', 'W02', 'W03', 'W04', 'W05', 'W06', 'W07', 'W08', 'W09', 'W10', 'W11', 'W12', 'W13', 'W14', 'W15', 'W16', 'W17', 'C00', 'C10', 'C18', 'C24'}


LEDGER = os.path.join(R17, "DISPATCH_LEDGER_R17.json")

# the outside world: a card must be able to wake up when a grant, a policy epoch or a source head changes
sys.path.insert(0, os.path.join(R17, "tools"))
try:
    import external_state as _ext
except Exception:
    _ext = None


def external_facts() -> dict:
    """Read the collected state if it is fresh, else collect it. Never raises: a runner tick must not die here."""
    if _ext is None:
        return {"digest": "NO_COLLECTOR", "per_source": {}, "grants": []}
    path = os.path.join(R17, "EXTERNAL_STATE_R17.json")
    try:
        if os.path.exists(path) and (datetime.datetime.now().timestamp() - os.path.getmtime(path)) < 900:
            facts = json.load(open(path, encoding="utf-8"))
            facts["_scope_patterns"] = _ext.SCOPE
            return facts
    except Exception:
        pass
    try:
        facts = _ext.collect()
        facts.pop("_scope_patterns", None)
        json.dump(facts, open(path, "w", encoding="utf-8", newline=chr(10)), ensure_ascii=False, indent=1)
        facts["_scope_patterns"] = _ext.SCOPE
        return facts
    except Exception as exc:
        return {"digest": f"COLLECT_FAILED:{type(exc).__name__}", "per_source": {}, "grants": []}


def load_ledger() -> dict:
    try:
        return json.load(open(LEDGER, encoding="utf-8"))
    except Exception:
        return {"schema": "SBL_R17_DISPATCH_LEDGER/1", "attempts": {}}


def input_digest(rid: str, rows: dict, audit_rows: dict, ext: dict | None = None) -> str:
    """A card may be re-dispatched only when its inputs changed. Probing the same unchanged row twice is
    spinning, not progress (the order calls it out as 'repeat the same signature with no new evidence')."""
    # only stable inputs may count: the dispatch itself appends evidence/repairs to the queue row, and hashing
    # those made every dispatch look like a new input, so the same card was handed out forever.
    q = rows.get(rid, {})
    a = audit_rows.get(rid, {})
    stable = {"state": q.get("state"), "deps": q.get("deps"), "title": q.get("title"),
              "family": q.get("family"), "owner_class": q.get("owner_class"),
              "requirement": a.get("requirement"), "oracle": a.get("oracle"),
              "deps_tree": a.get("immediate_dependency_ids"), "ready_without_effect": a.get("ready_without_effect"),
              "missing_grant_kind": a.get("missing_grant_kind")}
    if ext and _ext is not None and ext.get("per_source"):
        try:
            stable["external"] = _ext.digest_for(rid, ext)
        except Exception:
            stable["external"] = ext.get("digest")
    payload = json.dumps(stable, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def decide(ready: list, workers: list) -> str:
    """The scheduling invariant, as a function so a negative control can assert on it.

    The third premature stop happened because "no worker is running" was treated as "the round is over".
    A READY card plus zero workers is a DISPATCH, never an IDLE.
    """
    if ready and not workers:
        return "DISPATCH_NEXT_READY"
    if workers:
        return "BUSY_WAIT"
    return "IDLE_NO_READY"


def dispatch_allowed(cls: str, grant_present: bool) -> bool:
    """Effect classes may not be dispatched without a live grant. Read-only and isolated classes may."""
    if cls in ("READY_READONLY", "READY_ISOLATED_CANDIDATE", "DONE_VERIFIED"):
        return True
    if cls == "READY_ADMITTED_EFFECT":
        return bool(grant_present)
    return False


def load():
    q = json.load(open(QUEUE, encoding="utf-8"))
    return q, {r["id"]: r for r in q["rows"]}


def classify(rows: dict) -> dict:
    buckets: dict[str, list[dict]] = {k: [] for k in
                                      ("DONE_VERIFIED", "READY_READONLY", "READY_ISOLATED_CANDIDATE",
                                       "READY_ADMITTED_EFFECT", "BLOCKED_SECURITY", "BLOCKED_OWNER",
                                       "BLOCKED_DEPENDENCY", "STALLED_NO_NEW_EVIDENCE")}
    DONE_STATES = ("DONE", "DONE_NOFIT", "DONE_DOC_RED", "DONE_VERIFIED")
    for rid, (cls, cmd, why) in CARDS.items():
        row = rows.get(rid, {})
        # the queue is authoritative: a card recorded DONE is not re-dispatched because the table still
        # remembers it as READY (that mistake made the driver hand out the same finished card forever)
        if row.get("state") in DONE_STATES:
            cls = "DONE_VERIFIED"
        buckets[cls].append({"id": rid, "command": cmd, "why": why,
                             "queue_state": row.get("state"), "ceiling": (row.get("ceiling") or "")[:200]})
    for rid, row in rows.items():
        if rid in CARDS:
            continue
        cls = "DONE_VERIFIED" if row.get("state") in ("DONE", "DONE_NOFIT", "DONE_DOC_RED") else "BLOCKED_DEPENDENCY"
        buckets[cls].append({"id": rid, "command": None, "why": "not classified by the driver",
                             "queue_state": row.get("state")})

    # The queue table above is hand-written, so it under-reports: the row audit found five ids with a legal
    # read-only subtask that the table had parked as blocked. The audit is the authority for readiness, because
    # it is the only artefact that reasons per id. Without this, "no ready work" is a statement about the table,
    # not about R17 - which is precisely the defect this round is repairing.
    audit_path = os.path.join(R17, "ROW_AUDIT_R17.json")
    if os.path.exists(audit_path):
        audit = json.load(open(audit_path, encoding="utf-8"))
        closed = {b["id"] for b in buckets["DONE_VERIFIED"]}
        ready_now = {b["id"] for b in buckets["READY_READONLY"] + buckets["READY_ISOLATED_CANDIDATE"]}
        blocked_ids = {b["id"] for b in buckets["BLOCKED_DEPENDENCY"] + buckets["BLOCKED_OWNER"]
                       + buckets["BLOCKED_SECURITY"]}
        for rec in audit.get("rows", []):
            rid = rec.get("id")
            if rec.get("ready_without_effect") is not True or rid in closed or rid in ready_now:
                continue
            if rid in blocked_ids:
                # the audit proves a legal read-only subtask exists, so the family-level park is withdrawn
                for k in ("BLOCKED_DEPENDENCY", "BLOCKED_OWNER", "BLOCKED_SECURITY"):
                    buckets[k] = [b for b in buckets[k] if b["id"] != rid]
                blocked_ids.discard(rid)
            cmd = (f"python var/R17-20261023/tools/probe_all.py --id {rid}" if rid in PROBE_IDS
                   else f"python var/R17-20261023/tools/row_audit.py")
            buckets["READY_READONLY"].append({
                "id": rid, "command": cmd, "why": rec.get("readonly_subtask") or "row audit: read-only subtask",
                "queue_state": (rows.get(rid) or {}).get("state"),
                "ceiling": ((rows.get(rid) or {}).get("ceiling") or "")[:200], "source": "ROW_AUDIT_R17.json"})

    # operation-level subtasks under existing ids (SUBTASKS_R17.json): they add no denominator row, but they are
    # legal work and must be dispatchable, otherwise "no ready card" keeps hiding real product work
    sub_path = os.path.join(R17, "SUBTASKS_R17.json")
    if os.path.exists(sub_path):
        subs = json.load(open(sub_path, encoding="utf-8")).get("subtasks", [])
        done_ids = {b["id"] for b in buckets["DONE_VERIFIED"]}
        present = {b["id"] for k in buckets for b in buckets[k]}
        for st in subs:
            if st["id"] in present or st.get("parent") in done_ids:
                continue
            if not st.get("command_exists"):
                continue
            buckets["READY_ISOLATED_CANDIDATE"].append({
                "id": st["id"], "command": st["command"], "why": st["operation"][:120],
                "parent": st.get("parent"), "queue_state": (rows.get(st.get("parent")) or {}).get("state"),
                "source": "SUBTASKS_R17.json"})

    # a card whose inputs are unchanged since its last successful dispatch is not ready, it is stalled:
    # re-running it would produce the same receipt and no new evidence
    ext = external_facts()
    ledger = load_ledger().get("attempts", {})
    audit_by_id = {r["id"]: r for r in (json.load(open(audit_path, encoding="utf-8")).get("rows", [])
                                        if os.path.exists(audit_path) else [])}
    keep = []
    for card in buckets["READY_READONLY"] + buckets["READY_ISOLATED_CANDIDATE"]:
        prev = ledger.get(card["id"]) or {}
        dig = input_digest(card["id"], rows, audit_by_id, ext)
        if prev.get("digest") == dig and prev.get("exit") == 0:
            buckets["STALLED_NO_NEW_EVIDENCE"].append({**card, "why": "same inputs as the last successful run",
                                                       "digest": dig, "last_utc": prev.get("utc")})
        else:
            keep.append(card)
    ro_ids = {c["id"] for c in buckets["READY_READONLY"]}
    buckets["READY_READONLY"] = [c for c in keep if c["id"] in ro_ids]
    buckets["READY_ISOLATED_CANDIDATE"] = [c for c in keep if c["id"] not in ro_ids]
    return buckets


def active_workers() -> list[str]:
    """A worker is one of OUR processes: a run_lane dispatch, or a brief-stamped codex child."""
    out = []
    try:
        ps = subprocess.run(["powershell", "-NoProfile", "-Command",
                             "Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='codex.exe'\" |"
                             " Select-Object -ExpandProperty CommandLine"],
                            capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return out
    for line in ps.splitlines():
        if "run_lane.py" in line or "hgk-lane-dispatch" in line:
            out.append(line.strip()[:160])
    return out


def _atomic_json(path: str, obj) -> None:
    """Write-then-rename: a reader sees the old document or the new one, never a torn record."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def rg04_arm():
    """RG02/RG04 containment. While this marker exists the driver may dispatch ONLY the fixture
    allowlist; every other ready card is DEFERRED (not blocked, not parked). Deleting the marker
    restores the untouched ready set, so the containment is one reversible file."""
    try:
        return json.load(open(os.path.join(R17, "RG04_ARM.json"), encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="execute exactly one READY card, then stop")
    ap.add_argument("--out", default=os.path.join(R17, "READY_SET_R17.json"))
    a = ap.parse_args()
    q, rows = load()
    ext = external_facts()
    buckets = classify(rows)
    ready = buckets["READY_READONLY"] + buckets["READY_ISOLATED_CANDIDATE"]
    workers = active_workers()
    # an effect card without a grant must never be handed out, even if a table says it is ready
    dispatchable = [c for c in ready if dispatch_allowed("READY_ADMITTED_EFFECT" if c.get("grant_required") else "READY_READONLY", bool(c.get("grant_present")))]
    refused = dispatchable != ready
    ready = dispatchable

    # RG04 containment: only the fixture allowlist may move while the arm marker exists.
    arm = rg04_arm()
    gated = 0
    if arm:
        allowed = {str(x) for x in (arm.get("allowlist") or [])}
        before_gate = len(ready)
        ready = [c for c in ready if c.get("id") in allowed]
        gated = before_gate - len(ready)

    # Fair rotation over the legal ready list. `ready[0]` every tick is not fairness: the head card
    # wins every time the world changes, and a card behind it is unreachable while any head card wakes.
    led = load_ledger()
    cursor = led.get("cursor") or {}
    cursor_before = int(cursor.get("index") or 0)
    n = len(ready)
    start = cursor_before % n if n else 0
    last_k = 0
    nxt = ready[start] if n else None
    cursor_after = (start + last_k + 1) % n if n else cursor_before

    decision = decide(ready, workers)
    if refused and ready:
        decision = "REFUSED_NO_GRANT"
    # absolute tool paths: a non-interactive bash does not inherit the interactive PATH, and "uv: command not
    # found" from a dispatch is a launcher defect, not a card result.
    doc = {"schema": "SBL_R17_READY_SET/1",
           "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "invariant": "READY_COUNT > 0 AND ACTIVE_WORKERS = 0 => DISPATCH_NEXT_READY",
           "ready_count": len(ready), "active_workers": workers, "decision": decision,
           "rg04_armed": bool(arm), "rg04_allowlist": (arm or {}).get("allowlist"),
           "rg04_gated": gated,
           "cursor": {"before": cursor_before, "start": start, "after": cursor_after, "ready_n": n},
           "next": nxt, "buckets": {k: v for k, v in buckets.items()},
           "counts": {k: len(v) for k, v in buckets.items()}}
    _atomic_json(a.out, doc)
    print(json.dumps({"decision": decision, "ready": len(ready), "workers": len(workers),
                      "next": (nxt or {}).get("id"), "next_cmd": (nxt or {}).get("command"),
                      "rg04_armed": bool(arm), "rg04_gated": gated,
                      "cursor_before": cursor_before, "cursor_after": cursor_after,
                      "counts": doc["counts"], "out": a.out}, ensure_ascii=False, indent=1))
    if a.run and decision == "DISPATCH_NEXT_READY" and nxt and nxt.get("command"):
        print("RUN>", nxt["command"], flush=True)
        # The card commands are POSIX-shell strings (env prefixes, && chains). Running them through
        # cmd.exe mangles "PYTHONPATH=src cmd" into a not-a-command error, so dispatch through bash.
        # `bash` on PATH for a subprocess can be WSL's C:/Windows/System32/bash.exe, which cannot see /c/...
        # and reports "No such file or directory" for a file that exists. Pin git-bash explicitly, and use
        # forward slashes so no backslash escape can corrupt the literal (an earlier heredoc wrote \b as BS).
        gitbash = "C:/Program Files/Git/bin/bash.exe"
        env = dict(os.environ)
        # A read-only card must not leave .pyc behind inside a governed repo: that is a write effect.
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        rc = subprocess.call([gitbash, "-lc", nxt["command"]], cwd=r"C:\Projects\Agent_Workspace", env=env)
        print("EXIT>", rc)
        # ACK + cursor advance in ONE atomic commit: a crash can leave neither or both, never a cursor
        # that names a card whose result was never recorded (that is the duplicate-dispatch path).
        audit_by_id = {}
        ap_audit = os.path.join(R17, "ROW_AUDIT_R17.json")
        if os.path.exists(ap_audit):
            audit_by_id = {r["id"]: r for r in json.load(open(ap_audit, encoding="utf-8")).get("rows", [])}
        led.setdefault("attempts", {})[nxt["id"]] = {
            "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "command": nxt["command"], "exit": rc,
            "digest": input_digest(nxt["id"], rows, audit_by_id, ext)}
        led["cursor"] = {"index": cursor_after, "last_card": nxt["id"],
                         "last_k": last_k, "ready_n": n,
                         "passes": int(cursor.get("passes") or 0) + 1,
                         "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        _atomic_json(LEDGER, led)
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
