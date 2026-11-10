#!/usr/bin/env python3
"""review_lock — the maker may not move the subject while a checker is reading it.


try:  # keep every console child off the owner's desktop (see scripts/winproc.py)
    import winproc as _winproc  # noqa: E402  (same directory)
    _winproc.install()
except Exception:  # a missing helper must not stop a lane
    pass
Why this exists: on 2026-10-30 two independent checker sittings ended with
`ERR_CHECKER_MUTATED_SUBJECT` / `verdict_void_reason: the guarded subject changed during the turn`
because the maker committed into the guarded tree while the checker was running. The guard did its job
(it voided the verdict); the maker simply should not have been able to commit. Three rounds in a row
lost a checker verdict this way.

Mechanism (small on purpose):
  acquire --subject <path> --nonce <N>   record the subject and a live lock
  check --path <p> ...                   exit 1 if a live lock covers any path  (used by pre-commit)
  check --staged                         same, over `git diff --cached --name-only`
  release --nonce <N>                    drop the lock
  list                                   show live locks

A lock is a file under `var/review-locks/`. It dies with its TTL, so a crashed checker cannot wedge the
repository forever -- but a live lock refuses the commit, which is the point.
"""

from __future__ import annotations


try:  # every child of this process must be consoleless; see scripts/winproc.py and console_guard_gate.py
    import winproc as _winproc  # noqa: E402  (same directory)
    _winproc.install()
except Exception:  # a missing helper must not stop the tool
    pass


import argparse
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCKS = ROOT / "var" / "review-locks"


def now() -> datetime:
    return datetime.now(timezone.utc)


def _expiry(value) -> datetime | None:
    """Accept every shape an expiry can arrive in.

    Measured 2026-10-30: a lock restored by hand carried `expires_at` as an epoch integer, `fromisoformat`
    raised TypeError inside the pre-commit hook, and every commit died with a traceback instead of a refusal.
    A gate may refuse; it may not crash. Unreadable expiry is treated as "still live" -- the safe direction.
    """
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def live() -> list[dict]:
    out = []
    if not LOCKS.is_dir():
        return out
    for p in sorted(LOCKS.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - a corrupt lock must not block silently
            continue
        if not {"subject", "nonce"} <= set(d):
            continue
        expires = _expiry(d.get("expires_at"))
        if expires is None or expires > now():
            d["_path"] = str(p)
            out.append(d)
    return out


def covers(lock: dict, path: pathlib.Path) -> bool:
    subject = pathlib.Path(lock["subject"]).resolve()
    target = path.resolve()
    return target == subject or subject in target.parents


def cmd_acquire(args) -> int:
    subject = pathlib.Path(args.subject)
    if not subject.is_absolute():
        subject = (pathlib.Path.cwd() / subject).resolve()
    if not subject.exists():
        print(json.dumps({"ok": False, "code": "SUBJECT_MISSING", "subject": str(subject)}))
        return 2
    LOCKS.mkdir(parents=True, exist_ok=True)
    record = {
        "nonce": args.nonce,
        "pid": os.getpid(),
        "subject": str(subject),
        "reason": args.reason,
        "created_at": now().isoformat(timespec="seconds"),
        "expires_at": (now() + timedelta(minutes=args.ttl_min)).isoformat(timespec="seconds"),
    }
    (LOCKS / f"{args.nonce}.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(json.dumps({"ok": True, "lock": record}))
    return 0


def cmd_release(args) -> int:
    p = LOCKS / f"{args.nonce}.json"
    if p.exists():
        p.unlink()
        print(json.dumps({"ok": True, "released": args.nonce}))
        return 0
    print(json.dumps({"ok": True, "released": None, "note": "no such lock"}))
    return 0


def staged_paths() -> list[pathlib.Path]:
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--name-only"],
                       capture_output=True, text=True)
    return [ROOT / line.strip() for line in r.stdout.splitlines() if line.strip()]


def cmd_check(args) -> int:
    paths = staged_paths() if args.staged else [pathlib.Path(p) for p in (args.path or [])]
    if not paths:
        return 0
    blocking = []
    for lock in live():
        hit = [str(p) for p in paths if covers(lock, p)]
        if hit:
            blocking.append({"nonce": lock["nonce"], "subject": lock["subject"],
                             "expires_at": lock["expires_at"], "paths": hit[:5]})
    if blocking:
        print(json.dumps({"ok": False, "code": "SUBJECT_UNDER_REVIEW", "locks": blocking},
                         ensure_ascii=False))
        for b in blocking:
            print(f"review_lock: {b['subject']} is being checked under {b['nonce']} until "
                  f"{b['expires_at']}; committing into it would void that checker's verdict", file=sys.stderr)
        return 1
    return 0


def _holder_alive(lock: dict) -> bool | None:
    """Is the PID that took this lock still running?

    Measured failure, 2026-10-30: this answered "dead" for a LIVE dispatch, `reap` removed its lock, and the
    pre-commit hook then let two commits land during a review -- the exact defect review_lock exists to prevent,
    reintroduced by the reaper. `tasklist` output is not reliably decodable on this host, so the check asks
    PowerShell (already proven reliable for the driver) and treats any failure as ALIVE. Refusing to reap is the
    safe direction: a stale lock costs a manual release, a wrongly reaped one costs a voided verdict.
    """
    # The nonce is the decisive evidence, not the pid: Windows recycles pids within minutes, so a dead holder's pid
    # is routinely worn by an unrelated live process and the lock looked alive for ever (measured 2026-10-31: 40 locks,
    # every holder dead, every pid "ALIVE"). A dispatch that is really reading the subject carries its nonce in its
    # command line; nothing else does.
    nonce = lock.get("nonce")
    if nonce:
        if _nonce_running(nonce):
            return True
        pid = lock.get("pid")
        if isinstance(pid, int):
            cmd = "if (Get-Process -Id %d -ErrorAction SilentlyContinue) { 'ALIVE' } else { 'DEAD' }" % pid
            try:
                done = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, timeout=45)
                text = done.stdout.decode("utf-8", errors="replace") if isinstance(done.stdout, bytes) else str(done.stdout)
                return "ALIVE" in text and _nonce_running(nonce)
            except Exception:  # noqa: BLE001
                return True
        return False
    pid = lock.get("pid")
    if not isinstance(pid, int):
        return False
    cmd = "if (Get-Process -Id %d -ErrorAction SilentlyContinue) { 'ALIVE' } else { 'DEAD' }" % pid
    try:
        done = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, timeout=45)
        text = done.stdout.decode("utf-8", errors="replace") if isinstance(done.stdout, bytes) else str(done.stdout)
        return "ALIVE" in text
    except Exception:  # noqa: BLE001
        return True


def _nonce_running(nonce: str | None) -> bool:
    """True only if some live process still carries this nonce. A killed attempt leaves nothing to find."""
    if not nonce:
        return False
    # The query's own command line contains the nonce, so a naive `-like` filter matches the PowerShell process that
    # is doing the asking: every dead holder then looked alive for ever. Exclude the asker, and every shell, because a
    # shell's command line is the query itself.
    cmd = ("$n='%s'; if ((Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and "
           "$_.Name -notmatch '^(powershell|pwsh|WmiPrvSE|conhost|WindowsTerminal)\\.exe$' -and "
           "$_.CommandLine -like ('*' + $n + '*') } | Measure-Object).Count -gt 0) { 'ALIVE' } else { 'DEAD' }"
           % nonce.replace("'", "''"))
    try:
        done = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, timeout=60)
        text = done.stdout.decode("utf-8", errors="replace") if isinstance(done.stdout, bytes) else str(done.stdout)
        return "ALIVE" in text
    except Exception:  # noqa: BLE001
        return True


def cmd_reap(_args) -> int:
    """Remove locks whose holder is gone. A killed dispatcher used to leave a lock behind, and the
    pre-commit hook then refused legitimate commits -- the cure must not become the next outage."""
    reaped, kept = [], []
    for lock in live():
        alive = _holder_alive(lock)
        if alive is False:
            pathlib.Path(lock["_path"]).unlink(missing_ok=True)
            reaped.append(lock["nonce"])
        else:
            kept.append({"nonce": lock["nonce"], "holder_alive": alive})
    print(json.dumps({"reaped": reaped, "kept": kept}, ensure_ascii=False))
    return 0


def cmd_list(_args) -> int:
    print(json.dumps({"locks": live()}, ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="refuse maker commits into a subject under review")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("acquire"); a.add_argument("--subject", required=True)
    a.add_argument("--nonce", required=True); a.add_argument("--reason", default="checker reading the subject")
    a.add_argument("--ttl-min", type=int, default=120); a.set_defaults(fn=cmd_acquire)
    r = sub.add_parser("release"); r.add_argument("--nonce", required=True); r.set_defaults(fn=cmd_release)
    c = sub.add_parser("check"); c.add_argument("--path", action="append")
    c.add_argument("--staged", action="store_true"); c.set_defaults(fn=cmd_check)
    rp = sub.add_parser("reap"); rp.set_defaults(fn=cmd_reap)
    l = sub.add_parser("list"); l.set_defaults(fn=cmd_list)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
