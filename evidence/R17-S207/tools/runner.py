"""Bounded continuous ready-drain for the R17 queue.

Fourth-round defects this file fixed (order section 6A):
  * the old runner returned 0 for a non-zero child AND for a timeout, so a broken runner looked exactly like a
    healthy idle tick. Every outcome now has a typed status, its own exit code, and the raw stderr kept.
  * the lease was 900s while the children could run 800s + 1500s, so a hung card outlived its own lease and a
    second tick could dispatch the same card. The execution bound is now strictly inside the lease TTL and that
    ordering is asserted at start-up, not trusted.
  * there was no fencing token. Each lease now carries a monotonically increasing fence, journaled with the cycle,
    so a takeover is visible and an expired holder cannot pretend it still owns the queue.

REC05 P0 adds a bounded continuous drain inside one invocation:

  DISCOVER -> ADMIT -> CLAIM -> DISPATCH -> FAN_IN -> VERIFY -> CHECKPOINT -> NEXT_READY

  * at most ``max_cards`` cards and at most ``total_budget`` seconds per invocation (720s by default, strictly
    inside the 900s lease);
  * after every card the queue is recomputed, so the next card is chosen from fresh evidence, never from the old
    snapshot;
  * every child timeout is clamped to the remaining lease/budget, so no child can outlive the lease that
    authorises it;
  * full child stdout/stderr is persisted to unique files under ``runner/raw`` (the old record kept only a tail);
  * a non-zero child or timeout keeps the cycle exit non-zero, parks the named card, and is never retried in the
    same invocation (the next recompute may still offer a DIFFERENT legal card);
  * a malformed recompute is ``RECOMPUTE_MALFORMED``, never ``IDLE_HEALTHY``;
  * ``BUSY_WAIT`` is reported as ``BUSY``, distinct from "no ready work";
  * a claim is written to disk BEFORE the child starts. If a claim is still pending after a crash/timeout, the
    card returns ``BLOCKED_READBACK`` and is never replayed automatically;
  * the dispatcher admits only read-only / isolated-candidate cards. An effect card without an explicitly
    verified Native admission is refused; this file never mints a permissive grant.

Exclusion is per writeset, not per worktree. The queue lease is a single-writer mutex for this queue; claiming a
writeset here is not a claim of worktree parallelism. Parallel worktrees need their own independent claims.

Statuses / exit codes
  IDLE_HEALTHY           0   recomputed, no ready work and no active worker
  DISPATCH_OK            0   one or more cards drained, every dispatch verified at the subprocess level
  BUSY                   0   recompute saw an active worker (not "no ready work")
  SKIPPED_LEASE_HELD     0   another tick holds a live lease (no child run)
  SKIPPED_WRITESET_HELD  0   another live claim owns the same writeset
  BUDGET_EXHAUSTED       0   the bounded budget ended before any card could start
  RUNNER_FAILED         10   a child exited non-zero
  TIMEOUT               11   a child exceeded its bounded timeout
  MISSING_RUNNER        12   advance.py is absent, so not even a recompute is possible
  INTERNAL_ERROR        13   the runner itself raised or its bounds were invalid
  RECOMPUTE_MALFORMED   20   recompute stdout was not a well-formed dispatch decision (fail closed)
  BLOCKED_READBACK      21   a previous dispatch outcome is unknown; replay is refused
  ADMISSION_REFUSED     22   the named card is not an admitted read-only/candidate card
  PARKED_CARD_NOT_RETRIED 23 the recompute named a card parked after an earlier failure
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid

DEFAULT_HOME = r"C:\Projects\Agent_Workspace\var\R17-20261023"
DEFAULT_WORKDIR = r"C:\Projects\Agent_Workspace"

LEASE_TTL = 900
RECOMPUTE_TIMEOUT = 120
RUN_TIMEOUT = 600  # 120 + 600 < 900 on purpose: no child may outlive the lease that authorises it
MAX_CARDS = 5
TOTAL_BUDGET = 720  # strictly inside LEASE_TTL
SAFETY_MARGIN = 2  # seconds kept between the last child and the lease/budget deadline
MIN_CHILD_SECONDS = 2  # do not start a child with less headroom than this

EXIT = {"IDLE_HEALTHY": 0, "DISPATCH_OK": 0, "BUSY": 0, "SKIPPED_LEASE_HELD": 0,
        "SKIPPED_WRITESET_HELD": 0, "BUDGET_EXHAUSTED": 0,
        "RUNNER_FAILED": 10, "TIMEOUT": 11, "MISSING_RUNNER": 12, "INTERNAL_ERROR": 13,
        "RECOMPUTE_MALFORMED": 20, "BLOCKED_READBACK": 21, "ADMISSION_REFUSED": 22,
        "PARKED_CARD_NOT_RETRIED": 23, "NO_EFFECT_VIOLATION": 24}

# The four governed repos: a card that claims NO_EFFECT must leave every one of them byte-identical at
# HEAD and identical in its tracked-dirty count. This is the measurement, not the assurance.
REPOS = ("SBL", "HG-KSEOS", "Fabric", "PIPD")


def repo_envelope(workdir: str) -> dict:
    """HEAD + tracked-dirty count per governed repo. Read-only and cheap; -uno keeps PIPD's 6k
    untracked paths out of the hot path."""
    state = {}
    for name in REPOS:
        d = os.path.join(workdir, name)
        if not os.path.isdir(os.path.join(d, ".git")):
            state[name] = "ABSENT"
            continue
        try:
            head = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True,
                                  text=True, timeout=60).stdout.strip()
            st = subprocess.run(["git", "-C", d, "status", "--porcelain=v1", "-uno"],
                                capture_output=True, text=True, timeout=180).stdout
            state[name] = {"head": head, "dirty": len([ln for ln in st.splitlines() if ln.strip()])}
        except Exception as exc:
            state[name] = "ERR:" + type(exc).__name__
    return state


def envelope_changes(before: dict, after: dict) -> list:
    return [{"repo": n, "before": before.get(n), "after": after.get(n)}
            for n in REPOS if before.get(n) != after.get(n)]

# A claim in one of these states means an effect may or may not have happened. It is never replayed.
PENDING_CLAIM_STATES = frozenset(("CLAIMED", "DISPATCHED", "UNKNOWN"))
EFFECT_CLASSES = frozenset(("READY_ADMITTED_EFFECT", "ADMITTED_EFFECT", "EFFECT", "NATIVE_EFFECT"))
READONLY_CLASSES = frozenset(("READY_READONLY", "READONLY", "READY_ISOLATED_CANDIDATE",
                              "ISOLATED_CANDIDATE"))
DONE_CLASSES = frozenset(("DONE_VERIFIED", "DONE", "DONE_NOFIT", "DONE_DOC_RED"))
KNOWN_DECISIONS = frozenset(("DISPATCH_NEXT_READY", "BUSY_WAIT", "IDLE_NO_READY", "REFUSED_NO_GRANT"))


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def paths(home):
    return {"lease": os.path.join(home, "runner", "lease.json"),
            "fence": os.path.join(home, "runner", "fence.json"),
            "journal": os.path.join(home, "runner", "journal.jsonl"),
            "out": os.path.join(home, "runner", "last_cycle.json"),
            "raw": os.path.join(home, "runner", "raw"),
            "claims": os.path.join(home, "runner", "claims"),
            "checkpoints": os.path.join(home, "runner", "checkpoints"),
            "parked": os.path.join(home, "runner", "parked.json"),
            "advance": os.path.join(home, "tools", "advance.py")}


def read_json(p, default=None):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


def atomic_write_json(path, obj):
    """Write-then-rename: a reader sees the old document or the new one, never a torn record."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp-{uuid.uuid4().hex[:8]}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def append_journal(p, obj):
    os.makedirs(os.path.dirname(p["journal"]), exist_ok=True)
    with open(p["journal"], "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def next_fence(p) -> int:
    cur = read_json(p["fence"], {"fence": 0}) or {"fence": 0}
    n = int(cur.get("fence", 0)) + 1
    atomic_write_json(p["fence"], {"fence": n, "utc": now().isoformat()})
    return n


def acquire(p, ttl):
    """Return the lease we hold, or None when a live lease exists. A stale lease is taken over with a new fence."""
    os.makedirs(os.path.dirname(p["lease"]), exist_ok=True)
    cur = read_json(p["lease"])
    if cur:
        try:
            age = (now() - datetime.datetime.fromisoformat(cur["acquired_utc"])).total_seconds()
        except Exception:
            age = ttl + 1
        if age < ttl:
            return None
        try:
            os.remove(p["lease"])
        except OSError:
            return None
    lease = {"lease_id": uuid.uuid4().hex[:16], "fence": next_fence(p), "pid": os.getpid(),
             "acquired_utc": now().isoformat(), "ttl": ttl}
    try:
        fd = os.open(p["lease"], os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return None
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(lease, fh)
    return lease


def release(p, lease):
    cur = read_json(p["lease"]) or {}
    if cur.get("lease_id") == lease.get("lease_id"):  # never remove a lease we do not own
        try:
            os.remove(p["lease"])
        except OSError:
            pass


def run_child(cmd, workdir, timeout):
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=workdir, timeout=timeout,
                              encoding="utf-8", errors="replace")
        return {"exit": proc.returncode, "stdout": proc.stdout or "", "stderr": proc.stderr or "",
                "secs": round(time.time() - t0, 1), "timeout": False}
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else ""
        err = exc.stderr if isinstance(exc.stderr, str) else ""
        return {"exit": None, "stdout": out, "stderr": err,
                "secs": round(time.time() - t0, 1), "timeout": True}


def _safe(card) -> str:
    text = str(card or "recompute")
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in text)[:80] or "card"


def persist_raw(p, stage, card, res) -> dict:
    """Full stdout/stderr, not a tail. One unique pair of files per child invocation."""
    os.makedirs(p["raw"], exist_ok=True)
    base = f"{now().strftime('%Y%m%dT%H%M%S')}_{_safe(card)}_{stage}_{uuid.uuid4().hex[:8]}"
    outp = os.path.join(p["raw"], base + ".stdout.txt")
    errp = os.path.join(p["raw"], base + ".stderr.txt")
    out_b = (res.get("stdout") or "").encode("utf-8", "replace")
    err_b = (res.get("stderr") or "").encode("utf-8", "replace")
    with open(outp, "wb") as fh:
        fh.write(out_b)
    with open(errp, "wb") as fh:
        fh.write(err_b)
    return {"stdout": outp, "stderr": errp,
            "stdout_sha256": hashlib.sha256(out_b).hexdigest(),
            "stderr_sha256": hashlib.sha256(err_b).hexdigest(),
            "stdout_bytes": len(out_b), "stderr_bytes": len(err_b)}


def parse_snapshot(stdout: str):
    """Strict parse: exactly one JSON object and a known decision string. Anything else fails closed."""
    text = (stdout or "").strip()
    if not text:
        return None, "empty stdout"
    start = text.find("{")
    if start < 0:
        return None, "no JSON object in stdout"
    try:
        obj, end = json.JSONDecoder().raw_decode(text[start:])
    except Exception as exc:
        return None, f"invalid JSON: {type(exc).__name__}"
    if not isinstance(obj, dict):
        return None, "snapshot is not an object"
    trailing = text[start + end:].strip()
    if trailing:
        return None, f"trailing bytes after JSON: {trailing[:80]}"
    decision = obj.get("decision")
    if not isinstance(decision, str) or decision not in KNOWN_DECISIONS:
        return None, f"unknown decision: {decision!r}"
    return obj, None


def class_of(snapshot: dict, card: str, home: str) -> str:
    """Card class from the snapshot, else from its Ready Set artefact, else unclassified (advance.py only hands
    out read-only/candidate work, so that legacy shape is admitted as candidate)."""
    for key in ("class", "card_class", "classification", "kind"):
        val = snapshot.get(key)
        if isinstance(val, str) and val:
            return val
    out_path = snapshot.get("out")
    if isinstance(out_path, str) and os.path.exists(out_path):
        try:
            if os.path.getsize(out_path) <= 4 * 1024 * 1024:
                doc = read_json(out_path, {}) or {}
                for bucket, items in (doc.get("buckets") or {}).items():
                    for item in items or []:
                        if isinstance(item, dict) and item.get("id") == card:
                            return bucket
        except Exception:
            pass
    return "UNCLASSIFIED"


def native_admission_verified(snapshot: dict) -> bool:
    """Only an explicit admission id plus a positive flag counts. There is no fallback grant in this file."""
    if snapshot.get("native_admission_verified") is not True:
        return False
    return bool(snapshot.get("native_admission_id") or snapshot.get("permit_id")
                or snapshot.get("work_order_id"))


def admit(snapshot: dict, card: str, home: str):
    cls = class_of(snapshot, card, home)
    if cls in EFFECT_CLASSES:
        if native_admission_verified(snapshot):
            return True, "NATIVE_ADMISSION_VERIFIED", cls
        return False, "EFFECT_REQUIRES_VERIFIED_NATIVE_ADMISSION", cls
    if cls in DONE_CLASSES:
        return False, "DONE_CARD_NOT_DISPATCHABLE", cls
    if cls in READONLY_CLASSES or cls == "UNCLASSIFIED":
        return True, "READONLY_OR_CANDIDATE", cls
    return False, "CLASS_NOT_ADMITTED:" + cls, cls


def claim_path(p, card: str) -> str:
    return os.path.join(p["claims"], _safe(card) + ".json")


def load_claims(p) -> list:
    out = []
    try:
        names = sorted(os.listdir(p["claims"]))
    except OSError:
        return out
    for name in names:
        if not name.endswith(".json"):
            continue
        rec = read_json(os.path.join(p["claims"], name))
        if isinstance(rec, dict):
            rec["_path"] = os.path.join(p["claims"], name)
            out.append(rec)
    return out


def park_card(p, card: str, reason: str, detail: str, exit_code: int):
    doc = read_json(p["parked"], {"cards": {}}) or {"cards": {}}
    doc.setdefault("cards", {})[card] = {"reason": reason, "detail": str(detail)[:300],
                                         "exit": exit_code, "utc": now().isoformat()}
    atomic_write_json(p["parked"], doc)


def is_parked(p, card: str):
    doc = read_json(p["parked"], {}) or {}
    return (doc.get("cards") or {}).get(card)


def unpark(p, card: str) -> bool:
    doc = read_json(p["parked"], {}) or {}
    cards = doc.get("cards") or {}
    if card not in cards:
        return False
    cards.pop(card)
    atomic_write_json(p["parked"], {"cards": cards})
    return True


def writeset_for(snapshot: dict, card: str) -> str:
    ws = snapshot.get("writeset", snapshot.get("write_set"))
    if isinstance(ws, (list, tuple)):
        return json.dumps(sorted(str(x) for x in ws), ensure_ascii=False)
    if isinstance(ws, str) and ws:
        return ws
    return "card:" + card


def _deadline(lease: dict) -> datetime.datetime:
    return (datetime.datetime.fromisoformat(lease["acquired_utc"])
            + datetime.timedelta(seconds=int(lease["ttl"])))


def child_timeout(configured: int, lease_deadline, total_deadline):
    """Clamp a child timeout to the remaining lease and budget. None means: do not start a child."""
    rem = min((lease_deadline - now()).total_seconds(), (total_deadline - now()).total_seconds())
    budget = int(rem - SAFETY_MARGIN)
    if budget < MIN_CHILD_SECONDS:
        return None
    return max(1, min(int(configured), budget))


def cycle(home=DEFAULT_HOME, workdir=DEFAULT_WORKDIR, lease_ttl=LEASE_TTL,
          recompute_timeout=RECOMPUTE_TIMEOUT, run_timeout=RUN_TIMEOUT,
          max_cards=MAX_CARDS, total_budget=TOTAL_BUDGET) -> dict:
    p = paths(home)
    for key in ("raw", "claims", "checkpoints"):
        os.makedirs(p[key], exist_ok=True)
    os.makedirs(os.path.dirname(p["journal"]), exist_ok=True)
    # Children inherit this: a read-only card must not leave .pyc inside a governed repo.
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    started = now()
    rec = {"schema": "SBL_R17_READY_DRAIN/1", "ts": started.isoformat(), "max_cards": max_cards,
           "total_budget": total_budget, "lease_ttl": lease_ttl, "cards": [], "stages": [],
           "claim_ceiling": "CANDIDATE_TESTED", "acceptance_checked": False}

    def stop(status, reason, **extra):
        rec["status"] = status
        rec["exit"] = EXIT[status]
        if reason:
            rec["stop_reason"] = reason
        rec.update(extra)

    def finish_early():
        rec["finished_utc"] = now().isoformat()
        rec["elapsed_secs"] = round((now() - started).total_seconds(), 2)
        atomic_write_json(p["out"], rec)
        return rec

    if not isinstance(max_cards, int) or max_cards < 1:
        stop("INTERNAL_ERROR", "INVALID_MAX_CARDS", detail=f"max_cards={max_cards!r}")
        return finish_early()
    if not isinstance(total_budget, int) or total_budget < MIN_CHILD_SECONDS:
        stop("INTERNAL_ERROR", "INVALID_TOTAL_BUDGET", detail=f"total_budget={total_budget!r}")
        return finish_early()
    if total_budget > lease_ttl - SAFETY_MARGIN:
        stop("INTERNAL_ERROR", "BUDGET_NOT_INSIDE_LEASE",
             detail=f"total budget {total_budget}s is not strictly inside lease TTL {lease_ttl}s")
        return finish_early()
    if recompute_timeout + run_timeout >= lease_ttl:
        stop("INTERNAL_ERROR", "BOUND_NOT_INSIDE_LEASE",
             detail=f"execution bound {recompute_timeout + run_timeout}s is not inside lease TTL {lease_ttl}s")
        return finish_early()

    if not os.path.exists(p["advance"]):
        stop("MISSING_RUNNER", "NO_ADVANCE", detail=f"advance.py not found at {p['advance']}")
        return finish_early()

    lease = acquire(p, lease_ttl)
    if lease is None:
        stop("SKIPPED_LEASE_HELD", "LIVE_LEASE", lease=read_json(p["lease"]))
        return finish_early()

    rec.update(lease_id=lease["lease_id"], fence=lease["fence"], pid=os.getpid())
    lease_deadline = _deadline(lease)
    total_deadline = started + datetime.timedelta(seconds=total_budget)
    dispatched_ids: list[str] = []
    step = 0

    try:
        while True:
            if len(rec["cards"]) >= max_cards:
                stop("DISPATCH_OK", "MAX_CARDS", capped=True)
                break

            # DISCOVER: recompute is a child too, so it is bounded by the same remaining lease/budget.
            tmo = child_timeout(recompute_timeout, lease_deadline, total_deadline)
            if tmo is None:
                stop("DISPATCH_OK" if rec["cards"] else "BUDGET_EXHAUSTED",
                     "BUDGET_EXHAUSTED", capped=True)
                break
            step += 1
            snap_run = run_child([sys.executable, p["advance"]], workdir, tmo)
            raw = persist_raw(p, "discover", "recompute", snap_run)
            discover_sha = raw["stdout_sha256"]
            rec["last_recompute_secs"] = snap_run["secs"]
            rec["stages"].append({"stage": "DISCOVER", "seq": step, "exit": snap_run["exit"],
                                  "timeout": snap_run["timeout"], "secs": snap_run["secs"],
                                  "stdout_sha256": discover_sha,
                                  "packet": "runner/raw/" + os.path.basename(raw["stdout"])})
            if snap_run["timeout"]:
                stop("TIMEOUT", "RECOMPUTE_TIMEOUT", stage="recompute",
                     stderr_tail=snap_run["stderr"][-400:], secs=snap_run["secs"],
                     stdout_sha256=discover_sha)
                break
            if snap_run["exit"] != 0:
                stop("RUNNER_FAILED", "RECOMPUTE_NONZERO", stage="recompute",
                     child_exit=snap_run["exit"], stderr_tail=snap_run["stderr"][-400:],
                     secs=snap_run["secs"], stdout_sha256=discover_sha)
                break

            snapshot, parse_err = parse_snapshot(snap_run["stdout"])
            if parse_err:
                stop("RECOMPUTE_MALFORMED", "BAD_RECOMPUTE_STDOUT", detail=parse_err,
                     stdout_sha256=discover_sha,
                     stdout_path="runner/raw/" + os.path.basename(raw["stdout"]))
                break

            decision = snapshot["decision"]
            rec.update(decision=decision, ready=snapshot.get("ready"),
                       workers=snapshot.get("workers"), next=snapshot.get("next"))

            if decision == "BUSY_WAIT":
                stop("BUSY", "WORKERS_ACTIVE", decision=decision, workers=snapshot.get("workers"))
                break
            if decision == "IDLE_NO_READY":
                if snapshot.get("next") is not None:
                    stop("RECOMPUTE_MALFORMED", "IDLE_WITH_NEXT_CARD",
                         detail="IDLE_NO_READY carried a next card")
                    break
                stop("DISPATCH_OK" if rec["cards"] else "IDLE_HEALTHY", "NO_READY")
                break
            if decision == "REFUSED_NO_GRANT":
                stop("ADMISSION_REFUSED", "RECOMPUTE_REFUSED_NO_GRANT")
                break

            card = snapshot.get("next")
            cmd = snapshot.get("next_cmd")
            if not isinstance(card, str) or not card or not isinstance(cmd, str) or not cmd.strip():
                stop("RECOMPUTE_MALFORMED", "DISPATCH_WITHOUT_CARD_OR_COMMAND",
                     detail=f"next={card!r} next_cmd={cmd!r}")
                break

            # NEXT_READY guard: the same card twice in one invocation is an unchanged-input spin, not progress.
            if card in dispatched_ids:
                stop("DISPATCH_OK" if rec["cards"] else "RECOMPUTE_MALFORMED",
                     "SAME_CARD_UNCHANGED", next=card)
                break

            pending = [c for c in load_claims(p)
                       if c.get("card") == card and c.get("state") in PENDING_CLAIM_STATES]
            if pending:
                claim = pending[0]
                stop("BLOCKED_READBACK", "UNKNOWN_EFFECT_PENDING_CLAIM", next=card, card=card,
                     claim=claim.get("_path"), claim_state=claim.get("state"),
                     detail="a previous dispatch has no verified result; read back before any replay")
                park_card(p, card, "UNKNOWN_EFFECT", "pending claim requires readback",
                          EXIT["BLOCKED_READBACK"])
                break

            parked = is_parked(p, card)
            if parked:
                stop("PARKED_CARD_NOT_RETRIED", "PARKED_AFTER_FAILURE", next=card,
                     detail=parked.get("detail"), parked=parked)
                break

            # ADMIT
            ok, why, cls = admit(snapshot, card, home)
            rec["stages"].append({"stage": "ADMIT", "seq": step, "card": card, "class": cls,
                                  "admitted": ok, "why": why})
            if not ok:
                stop("ADMISSION_REFUSED", why, next=card, card=card, card_class=cls)
                break

            ws = writeset_for(snapshot, card)
            live_other = []
            expired_other = []
            for claim in load_claims(p):
                if claim.get("state") not in PENDING_CLAIM_STATES or claim.get("card") == card:
                    continue
                if claim.get("writeset") != ws:
                    continue
                try:
                    live = datetime.datetime.fromisoformat(claim["lease_expires_utc"]) > now()
                except Exception:
                    live = False
                (live_other if live else expired_other).append(claim)
            if live_other:
                stop("SKIPPED_WRITESET_HELD", "LIVE_WRITESET_CLAIM", next=card,
                     claim=live_other[0].get("_path"))
                break
            if expired_other:
                stop("BLOCKED_READBACK", "EXPIRED_UNKNOWN_CLAIM_ON_WRITESET", next=card, card=card,
                     claim=expired_other[0].get("_path"),
                     detail="an expired claim on this writeset has an unknown outcome; read back first")
                break

            # CLAIM: durable before the child starts. This is what makes a crash visible instead of replayable.
            claim = {"card": card, "writeset": ws, "lease_id": lease["lease_id"],
                     "fence": lease["fence"], "pid": os.getpid(), "state": "CLAIMED",
                     "claimed_utc": now().isoformat(), "lease_expires_utc": lease_deadline.isoformat(),
                     "class": cls, "command": cmd}
            atomic_write_json(claim_path(p, card), claim)
            rec["stages"].append({"stage": "CLAIM", "seq": step, "card": card,
                                  "writeset": ws, "state": "CLAIMED"})

            tmo = child_timeout(run_timeout, lease_deadline, total_deadline)
            if tmo is None:
                claim.update(state="ABANDONED_BEFORE_CHILD", abandoned_utc=now().isoformat())
                atomic_write_json(claim_path(p, card), claim)
                stop("DISPATCH_OK" if rec["cards"] else "BUDGET_EXHAUSTED",
                     "BUDGET_EXHAUSTED_BEFORE_CHILD", next=card, card=card, capped=True)
                break

            claim.update(state="DISPATCHED", dispatched_utc=now().isoformat(), child_timeout_secs=tmo)
            atomic_write_json(claim_path(p, card), claim)
            rec["card"] = card
            dispatched_ids.append(card)

            # DISPATCH
            env_before = repo_envelope(workdir)
            ran = run_child([sys.executable, p["advance"], "--run"], workdir, tmo)
            env_after = repo_envelope(workdir)
            changed = envelope_changes(env_before, env_after)
            raw = persist_raw(p, "dispatch", card, ran)
            entry = {"card": card, "seq": step, "class": cls, "writeset": ws, "command": cmd,
                     "child_exit": ran["exit"], "timeout": ran["timeout"], "secs": ran["secs"],
                     "raw": raw, "stdout_sha256": raw["stdout_sha256"],
                     "stderr_sha256": raw["stderr_sha256"], "acceptance_checked": False,
                     "no_effect": {"before": env_before, "after": env_after, "changed": changed},
                     "stages": {"DISCOVER": {"decision": decision, "stdout_sha256": discover_sha},
                                "ADMIT": {"class": cls, "admitted": True, "why": why},
                                "CLAIM": {"writeset": ws, "state": "DISPATCHED",
                                          "path": claim_path(p, card)},
                                "DISPATCH": {"exit": ran["exit"], "timeout": ran["timeout"],
                                             "secs": ran["secs"], "child_timeout_secs": tmo}}}
            rec["stages"].append({"stage": "DISPATCH", "seq": step, "card": card,
                                  "exit": ran["exit"], "timeout": ran["timeout"],
                                  "secs": ran["secs"], "child_timeout_secs": tmo})

            # FAN_IN: collect what the child produced. Reading only; the runner never writes the card's receipt.
            ledger = read_json(os.path.join(home, "DISPATCH_LEDGER_R17.json"))
            entry["fan_in"] = {"ledger_present": isinstance(ledger, dict),
                               "attempt": ((ledger or {}).get("attempts") or {}).get(card)}
            rec["stages"].append({"stage": "FAN_IN", "seq": step, "card": card,
                                  "stdout_sha256": raw["stdout_sha256"],
                                  "stderr_sha256": raw["stderr_sha256"]})

            # VERIFY: subprocess outcome only. No acceptance, no claim of product correctness.
            if changed:
                result = "NO_EFFECT_VIOLATION"
                claim.update(state="NO_EFFECT_VIOLATION", violation_utc=now().isoformat(),
                             detail="a governed repo changed during a card claiming NO_EFFECT")
            elif ran["timeout"]:
                result = "UNKNOWN_EFFECT_TIMEOUT"
                claim.update(state="UNKNOWN", unknown_utc=now().isoformat(),
                             detail="child killed at its bounded timeout")
            elif ran["exit"] != 0:
                result = "FAILED_NONZERO"
                claim.update(state="FAILED_NONZERO", failed_utc=now().isoformat(),
                             detail=f"child exit {ran['exit']}")
            else:
                result = "VERIFIED_EXEC"
                claim.update(state="VERIFIED_EXEC", verified_utc=now().isoformat())
            atomic_write_json(claim_path(p, card), claim)
            entry["result"] = result
            entry["claim_state"] = claim["state"]
            entry["stages"]["VERIFY"] = {"result": result, "child_exit": ran["exit"],
                                         "timeout": ran["timeout"], "acceptance_checked": False}
            rec["stages"].append({"stage": "VERIFY", "seq": step, "card": card,
                                  "result": result, "child_exit": ran["exit"]})

            # CHECKPOINT (atomic) + journal, then NEXT_READY.
            ckpt = os.path.join(p["checkpoints"], f"{step:03d}_{_safe(card)}.json")
            entry["stages"]["CHECKPOINT"] = {"path": ckpt, "utc": now().isoformat()}
            atomic_write_json(ckpt, entry)
            append_journal(p, {"type": "card", **entry})
            rec["cards"].append(entry)
            rec["stages"].append({"stage": "CHECKPOINT", "seq": step, "card": card,
                                  "path": "runner/checkpoints/" + os.path.basename(ckpt)})
            rec["stages"].append({"stage": "NEXT_READY", "seq": step, "card": card,
                                  "result": result})
            rec["stderr_tail"] = ran["stderr"][-400:]

            if result == "UNKNOWN_EFFECT_TIMEOUT":
                rec["status"] = "TIMEOUT"
                rec["exit"] = EXIT["TIMEOUT"]
                rec["stop_reason"] = "DISPATCH_TIMEOUT_UNKNOWN_EFFECT"
                rec["stage"] = "dispatch"
                park_card(p, card, "UNKNOWN_EFFECT", "dispatch timed out", EXIT["TIMEOUT"])
                break
            if result == "FAILED_NONZERO":
                rec["status"] = "RUNNER_FAILED"
                rec["exit"] = EXIT["RUNNER_FAILED"]
                rec["stop_reason"] = "DISPATCH_NONZERO"
                rec["stage"] = "dispatch"
                rec["child_exit"] = ran["exit"]
                park_card(p, card, "DISPATCH_NONZERO", f"child exit {ran['exit']}",
                          EXIT["RUNNER_FAILED"])
                break
            if result == "NO_EFFECT_VIOLATION":
                rec["status"] = "NO_EFFECT_VIOLATION"
                rec["exit"] = EXIT["NO_EFFECT_VIOLATION"]
                rec["stop_reason"] = "GOVERNED_REPO_CHANGED"
                rec["stage"] = "dispatch"
                rec["no_effect_changed"] = changed
                park_card(p, card, "NO_EFFECT_VIOLATION",
                          json.dumps(changed, ensure_ascii=False), EXIT["NO_EFFECT_VIOLATION"])
                break
            # verified: loop and recompute for the NEXT_READY card
    except Exception as exc:
        rec["status"] = "INTERNAL_ERROR"
        rec["exit"] = EXIT["INTERNAL_ERROR"]
        rec["stop_reason"] = "EXCEPTION"
        rec["detail"] = f"{type(exc).__name__}: {exc}"[:300]
    finally:
        release(p, lease)
        rec.setdefault("status", "INTERNAL_ERROR")
        rec["exit"] = EXIT.get(rec["status"], EXIT["INTERNAL_ERROR"])
        rec["finished_utc"] = now().isoformat()
        rec["elapsed_secs"] = round((now() - started).total_seconds(), 2)
        atomic_write_json(p["out"], rec)
        append_journal(p, {"type": "cycle", **rec})
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=DEFAULT_HOME)
    ap.add_argument("--workdir", default=DEFAULT_WORKDIR)
    ap.add_argument("--lease-ttl", type=int, default=LEASE_TTL)
    ap.add_argument("--recompute-timeout", type=int, default=RECOMPUTE_TIMEOUT)
    ap.add_argument("--run-timeout", type=int, default=RUN_TIMEOUT)
    ap.add_argument("--max-cards", type=int, default=MAX_CARDS)
    ap.add_argument("--total-budget", type=int, default=TOTAL_BUDGET)
    ap.add_argument("--unpark", metavar="CARD", help="remove a park marker and exit")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if a.unpark:
        removed = unpark(paths(a.home), a.unpark)
        print(json.dumps({"unparked": a.unpark, "removed": removed}, ensure_ascii=False))
        return 0
    rec = cycle(a.home, a.workdir, a.lease_ttl, a.recompute_timeout, a.run_timeout,
                a.max_cards, a.total_budget)
    if not a.quiet or rec["status"] != "IDLE_HEALTHY":
        print(json.dumps(rec, ensure_ascii=False, indent=1))
    return int(rec.get("exit", EXIT["INTERNAL_ERROR"]))


if __name__ == "__main__":
    raise SystemExit(main())
