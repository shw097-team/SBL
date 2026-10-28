#!/usr/bin/env python3
"""REC08 F2 — build a checker work area that can actually run the suite.

Why this exists (measured, V04/V05/V06): the VERIFY lane's sandbox refused to create pytest's
tmp dir, so the "regression" item returned PermissionError before reaching any changed
behaviour. REC08 §F2 says the fix is a legitimate WORKER-SIDE writable checker area, not a
loosened verdict and not a retry of the same必败 guard.

So this tool:
  1. creates a detached git worktree of the exact subject HEAD (writable, real .git present,
     real var/ so repo-dependent tests are not run in a non-equivalent export tree);
  2. points TMPDIR/TEMP/TMP at a directory INSIDE that worktree;
  3. runs the requested pytest selection, records raw stdout/stderr/exit + counts + sha256;
  4. asserts the worktree HEAD equals the requested subject and that the tree was clean at
     creation, so a pass cannot be attributed to a different revision.

Claim ceiling: WORKER_SIDE_REGRESSION_EXECUTED. It is NOT an independent checker verdict --
that requires a different registered principal running the same subject (REC08 §8).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("C:/Projects/Agent_Workspace/HG-KSEOS")
VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")


def sh(cmd: list[str], cwd: Path | None = None, env: dict | None = None, timeout: int = 900):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout)
    return p, round(time.time() - t0, 2)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="HEAD", help="commit/tag the checker must test")
    ap.add_argument("--test", nargs="*", default=[], help="pytest paths (default: tests)")
    ap.add_argument("--workdir", default=str(VAR / "checker_area" / "repo"))
    ap.add_argument("--receipt", default=str(VAR / "receipts" / "F2_CHECKER_WORKAREA.json"))
    ap.add_argument("--timeout", type=int, default=1200)
    ap.add_argument("--env", action="append", default=[],
                    help="KEY=VALUE exported to the child (REQUIRED for external-repo anchors)")
    ap.add_argument("--mkdir", action="append", default=[],
                    help="untracked directory the subject needs to EXIST (empty is enough)")
    ap.add_argument("--seed", action="append", default=[],
                    help="untracked repo-relative path to copy in so the area is equivalent")
    ap.add_argument("--keep", action="store_true", help="keep the worktree for inspection")
    args = ap.parse_args()

    rec: dict = {"schema": "CHECKER_WORKAREA.v1", "order": "REC08_F2",
                 "repo": str(REPO), "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    ok = True

    # --- 0. resolve subject + require a clean tree so the pass belongs to that revision alone.
    p, _ = sh(["git", "rev-parse", args.subject], REPO)
    head = p.stdout.strip()
    p2, _ = sh(["git", "status", "--porcelain=v1", "-uall"], REPO)
    dirty = [ln for ln in p2.stdout.splitlines() if ln.strip()]
    rec["subject_arg"] = args.subject
    rec["subject_head"] = head
    rec["repo_dirty_lines"] = len(dirty)
    if not head:
        rec["verdict"] = "NO_SUBJECT"
        ok = False

    # --- 1. fresh detached worktree (writable, real .git, real var/).
    wt = Path(args.workdir)
    if wt.exists():
        sh(["git", "worktree", "remove", "--force", str(wt)], REPO)
        if wt.exists():
            shutil.rmtree(wt, ignore_errors=True)
    p, secs = sh(["git", "worktree", "add", "--detach", str(wt), head], REPO, timeout=300)
    rec["worktree"] = str(wt)
    rec["worktree_add"] = {"exit": p.returncode, "seconds": secs,
                           "stderr_tail": p.stderr[-600:]}
    if p.returncode != 0:
        rec["verdict"] = "WORKTREE_ADD_FAILED"
        ok = False
        args.keep = True
    else:
        p, _ = sh(["git", "rev-parse", "HEAD"], wt)
        rec["worktree_head"] = p.stdout.strip()
        if rec["worktree_head"] != head:
            rec["verdict"] = "WORKTREE_HEAD_MISMATCH"
            ok = False
        # Sibling-layout equivalence: the canonical tree keeps `TEST_RESULTS/` NEXT TO the repo root
        # and several suites scratch there via `ROOT.parent / "TEST_RESULTS"`. A worktree at another
        # depth therefore fails on `mkdtemp(dir=...)` for a reason that has nothing to do with the
        # change under test. Create the sibling scratch root so the area matches the canonical shape.
        sibling = wt.parent / "TEST_RESULTS"
        sibling.mkdir(parents=True, exist_ok=True)
        rec["sibling_test_results"] = {"path": str(sibling), "exists": sibling.is_dir()}

        # Untracked runtime state the SUBJECT needs (gitignored var/ and worktrees/) is absent from
        # any clean worktree by construction. Name each one explicitly instead of copying the tree
        # wholesale: an empty dir where only existence is asserted, a copy where content is read.
        seeded = []
        for rel in args.mkdir:
            (wt / rel).mkdir(parents=True, exist_ok=True)
            seeded.append({"path": rel, "mode": "mkdir"})
        for rel in args.seed:
            src, dst = REPO / rel, wt / rel
            if not src.exists():
                seeded.append({"path": rel, "mode": "copy", "error": "SOURCE_ABSENT"})
                continue
            shutil.copytree(src, dst, dirs_exist_ok=True)
            files = sum(1 for _ in dst.rglob("*") if _.is_file())
            seeded.append({"path": rel, "mode": "copy", "files": files})
        rec["seeded"] = seeded

    if ok:
        # --- 2. writable scratch NEXT TO the worktree, never inside it.
        # Measured trap: putting the scratch dir inside the worktree makes `git status` dirty, and a
        # hygiene test that reads the working tree then fails for a reason this harness invented.
        tmp = wt.parent / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        probe = tmp / "writable.probe"
        try:
            probe.write_text("ok", encoding="utf-8")
            writable = probe.read_text(encoding="utf-8") == "ok"
            probe.unlink()
        except OSError as exc:
            writable = False
            rec["scratch_error"] = repr(exc)
        rec["scratch"] = {"path": str(tmp), "writable": writable}
        if not writable:
            rec["verdict"] = "SCRATCH_NOT_WRITABLE"
            ok = False

    if ok:
        env = dict(os.environ)
        env.update({
            "PYTHONPATH": str(wt / "src"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "TMPDIR": str(tmp), "TEMP": str(tmp), "TMP": str(tmp),
            "PYTEST_DEBUG_TEMPROOT": str(tmp),
        })
        # Anchors resolved by tests as `parents[N]/X` are a property of the tree's DEPTH, so an
        # isolated worktree silently points them at the wrong place. Exporting them explicitly is
        # what makes the checker area EQUIVALENT to the canonical one instead of a different test.
        extra_env = {}
        for pair in args.env:
            k, _, v = pair.partition("=")
            extra_env[k.strip()] = v.strip()
        env.update(extra_env)
        rec["extra_env"] = extra_env
        targets = args.test or ["tests"]
        cmd = [sys.executable, "-B", "-m", "pytest", *targets, "-q", "--tb=short",
               "-p", "no:cacheprovider"]
        try:
            p, secs = sh(cmd, wt, env, timeout=args.timeout)
            out, err, code = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired:
            out, err, code, secs = "", "TIMEOUT", "TIMEOUT", args.timeout

        log = wt.parent / "F2_CHECKER_WORKAREA.log"
        log.write_text(f"$ {' '.join(cmd)}\ncwd={wt}\n--- STDOUT ---\n{out}\n--- STDERR ---\n{err}\n",
                       encoding="utf-8")
        tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
        rec["run"] = {
            "cmd": cmd, "seconds": secs, "exit": code,
            "stdout_sha256": sha256_text(out), "stderr_sha256": sha256_text(err),
            "log": str(log), "summary_line": tail[0],
            "permission_errors": out.count("PermissionError") + err.count("PermissionError"),
        }
        rec["verdict"] = {"OK": "SUITE_EXECUTED", "TIMEOUT": "SUITE_TIMEOUT"}.get(
            code if isinstance(code, str) else ("OK" if code == 0 else "FAILED"), "SUITE_FAILED")
        ok = code == 0

    if not args.keep:
        sh(["git", "worktree", "remove", "--force", str(wt)], REPO)
        rec["worktree_removed"] = not Path(wt).exists()
    else:
        rec["worktree_removed"] = False

    rec["claim_ceiling"] = "WORKER_SIDE_REGRESSION_EXECUTED"
    rec["not_claimed"] = ["INDEPENDENT_CHECKER_VERDICT", "NATIVE_EFFECT_VERIFIED"]
    rec["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    Path(args.receipt).parent.mkdir(parents=True, exist_ok=True)
    Path(args.receipt).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"verdict={rec['verdict']}")
    print(f"head={rec.get('head', head)} worktree_head={rec.get('worktree_head')}")
    if "run" in rec:
        print(f"run exit={rec['run']['exit']} seconds={rec['run']['seconds']} "
              f"permission_errors={rec['run']['permission_errors']}")
        print(f"summary: {rec['run']['summary_line']}")
    print(f"receipt={args.receipt}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
