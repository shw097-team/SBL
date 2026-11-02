#!/usr/bin/env python3
"""Preflight check for the PIPD governed lane.

One command gathers the environment facts that must hold before a governed
round starts, and that otherwise keep being checked by hand (and checked
wrongly). Every check reports one dict ``{id,status,detail,elapsed_ms}`` with a
status in PASS|FAIL|WARN|SKIP; the process exits non-zero only when some check
is FAIL -- WARN and SKIP alone still exit 0.

Two checks exist because of measured pain, not theory:

  * model_pinning -- a run that omitted ``--model`` silently used whatever
    ``~/.codex/config.toml`` pinned, and exactly that drift silently invalidated
    two verification runs. A mismatch is therefore reported as ``CONFIG_DRIFT``.
  * codex_sandbox -- a broken codex sandbox helper prints ``helper_unknown_error``
    / ``setup refresh had errors`` instead of running the probe. That is a WARN
    named ``SANDBOX_HELPER_BROKEN``, never a silent pass.

The checks are small functions over injected inputs (a git-status string, a TOML
string, a check list, a free-space count) so the unit tests exercise them
without docker, codex, or the network.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "PIPD-PREFLIGHT/1"
DISK_MIN_FREE_BYTES = 5 * 1024 ** 3  # 5 GiB
GIB = 1024 ** 3
PROBE_MARKER = "PREFLIGHT_PROBE_OK"
PROBE_COMMAND = "Run the shell command: echo " + PROBE_MARKER
SANDBOX_BROKEN_MARKERS = ("helper_unknown_error", "setup refresh had errors")
LOOPBACK_PORTS = (10102, 10100)
CODEX_GLOB = "OpenAI/Codex/bin/*/codex.exe"
CONFIG_RELPATH = (".codex", "config.toml")
CHECK_IDS = ("python", "git_head", "disk", "docker", "codex_binary",
             "codex_sandbox", "model_pinning", "loopback", "suite_baseline")


# --------------------------------------------------------------------------- #
# primitives
# --------------------------------------------------------------------------- #

def _result(cid: str, status: str, detail: str, elapsed_ms: int = 0) -> dict:
    return {"id": cid, "status": status, "detail": detail, "elapsed_ms": elapsed_ms}


def _timed(fn) -> dict:
    t0 = time.perf_counter()
    res = fn()
    res["elapsed_ms"] = int((time.perf_counter() - t0) * 1000)
    return res


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# check 1: python
# --------------------------------------------------------------------------- #

def check_python(*, version_info, unittest_importable: bool) -> dict:
    """>= 3.11 on the interpreter and a working stdlib ``unittest``."""
    shown = ".".join(str(x) for x in version_info)
    if tuple(version_info)[:2] < (3, 11):
        return _result("python", "FAIL", f"interpreter {shown} < 3.11")
    if not unittest_importable:
        return _result("python", "FAIL", f"interpreter {shown}; unittest NOT importable")
    return _result("python", "PASS", f"interpreter {shown}; unittest importable")


# --------------------------------------------------------------------------- #
# check 2: git_head
# --------------------------------------------------------------------------- #

def count_porcelain(porcelain: str) -> int:
    """Dirty-file count = non-empty lines of ``git status --porcelain``."""
    return sum(1 for line in porcelain.splitlines() if line.strip())


def check_git_head(*, is_git: bool, head: str = "", porcelain: str = "",
                   expect_head: str | None = None,
                   expect_dirty: int | None = None) -> dict:
    if not is_git:
        return _result("git_head", "FAIL", "not a git work tree")
    dirty = count_porcelain(porcelain)
    label = head[:12] if head else "<no HEAD>"
    detail = f"HEAD {label} dirty={dirty}"
    problems: list[str] = []
    if expect_head is not None and head != expect_head:
        problems.append(f"HEAD {label} != expected {expect_head[:12]}")
    if expect_dirty is not None and dirty != expect_dirty:
        problems.append(f"dirty {dirty} != expected {expect_dirty}")
    if problems:
        return _result("git_head", "FAIL", detail + "; " + "; ".join(problems))
    return _result("git_head", "PASS", detail)


# --------------------------------------------------------------------------- #
# check 3: disk
# --------------------------------------------------------------------------- #

def check_disk(free_bytes: int) -> dict:
    free_gib = free_bytes / GIB
    if free_bytes >= DISK_MIN_FREE_BYTES:
        return _result("disk", "PASS", f"{free_gib:.2f} GiB free (>= 5 GiB)")
    return _result("disk", "FAIL", f"{free_gib:.2f} GiB free (< 5 GiB)")


# --------------------------------------------------------------------------- #
# check 4: docker
# --------------------------------------------------------------------------- #

def check_docker(*, reachable: bool, reason: str = "") -> dict:
    if reachable:
        return _result("docker", "PASS", "docker reachable")
    return _result("docker", "WARN",
                   f"container lane unavailable: {reason.strip() or 'docker unreachable'}")


# --------------------------------------------------------------------------- #
# check 5: codex_binary
# --------------------------------------------------------------------------- #

def find_codex_binaries(localappdata: str | None) -> list[Path]:
    if not localappdata:
        return []
    base = Path(localappdata)
    if not base.is_dir():
        return []
    return sorted(base.glob(CODEX_GLOB))


def newest_by_mtime(paths: list[Path]) -> Path | None:
    return max(paths, key=lambda p: p.stat().st_mtime) if paths else None


def check_codex_binary(paths: list[str], version: str = "") -> dict:
    if not paths:
        return _result("codex_binary", "FAIL",
                       "no codex.exe found under %LOCALAPPDATA%/OpenAI/Codex/bin/*/")
    detail = f"{len(paths)} hit(s): " + "; ".join(str(p) for p in paths)
    if version:
        detail += f" | newest --version: {version}"
    return _result("codex_binary", "PASS", detail)


# --------------------------------------------------------------------------- #
# check 6: codex_sandbox
# --------------------------------------------------------------------------- #

def check_codex_sandbox(output: str) -> dict:
    for marker in SANDBOX_BROKEN_MARKERS:
        if marker in output:
            return _result("codex_sandbox", "WARN", "SANDBOX_HELPER_BROKEN")
    if PROBE_MARKER in output:
        return _result("codex_sandbox", "PASS", "SANDBOX_READY")
    return _result("codex_sandbox", "WARN",
                   f"probe produced no {PROBE_MARKER} marker")


# --------------------------------------------------------------------------- #
# check 7: model_pinning
# --------------------------------------------------------------------------- #

def extract_config_model(config_toml: str) -> str | None:
    m = re.search(r'(?m)^\s*model\s*=\s*["\']([^"\']+)["\']', config_toml or "")
    return m.group(1) if m else None


def check_model_pinning(config_toml: str, model: str | None) -> dict:
    if model is None:
        return _result("model_pinning", "SKIP", "no --model provided")
    config_model = extract_config_model(config_toml)
    if config_model is None:
        return _result("model_pinning", "WARN",
                       "CONFIG_DRIFT: config.toml carries no model pin; "
                       "the run must pass --model explicitly")
    if config_model != model:
        return _result("model_pinning", "WARN",
                       f"CONFIG_DRIFT: config.toml model={config_model!r} != "
                       f"--model {model!r}; the run must pass --model explicitly")
    return _result("model_pinning", "PASS",
                   f"config.toml model matches --model ({model!r})")


# --------------------------------------------------------------------------- #
# check 8: loopback
# --------------------------------------------------------------------------- #

def check_loopback(probes: dict[int, bool]) -> dict:
    up = sorted(p for p, ok in probes.items() if ok)
    down = sorted(p for p, ok in probes.items() if not ok)
    detail = ("up=[" + ",".join(map(str, up)) + "] down=[" + ",".join(map(str, down)) + "]")
    if down:
        return _result("loopback", "WARN", f"unreachable loopback port(s) {down}; {detail}")
    return _result("loopback", "PASS", detail)


# --------------------------------------------------------------------------- #
# check 9: suite_baseline
# --------------------------------------------------------------------------- #

def check_suite_baseline(*, ran: bool, exit_code: int | None = None,
                         test_count: int | None = None,
                         duration_s: float | None = None) -> dict:
    if not ran:
        return _result("suite_baseline", "SKIP", "not requested (pass --with-suite)")
    parts = [f"exit={exit_code}"]
    if test_count is not None:
        parts.append(f"tests={test_count}")
    if duration_s is not None:
        parts.append(f"duration={duration_s:.1f}s")
    detail = " ".join(parts)
    if exit_code == 0:
        return _result("suite_baseline", "PASS", detail)
    return _result("suite_baseline", "FAIL", detail)


# --------------------------------------------------------------------------- #
# verdict / payload / table
# --------------------------------------------------------------------------- #

def compute_verdict(checks: list[dict]) -> tuple[str, str]:
    fails = [c["id"] for c in checks if c["status"] == "FAIL"]
    warns = [c["id"] for c in checks if c["status"] == "WARN"]
    if fails:
        return "FAIL", f"{len(fails)} check(s) FAILED: {', '.join(fails)}"
    if warns:
        return "PASS", f"no FAIL; {len(warns)} warning(s): {', '.join(warns)}"
    return "PASS", "all checks passed"


def exit_code_for(checks: list[dict]) -> int:
    return 1 if any(c["status"] == "FAIL" for c in checks) else 0


def build_payload(*, repo, head: str, dirty: int, checks: list[dict],
                  as_of: str | None = None) -> dict:
    verdict, reason = compute_verdict(checks)
    return {
        "schema": SCHEMA,
        "as_of": as_of or _now_iso(),
        "repo": str(repo),
        "head": head,
        "dirty": dirty,
        "checks": checks,
        "verdict": verdict,
        "verdict_reason": reason,
    }


def render_table(checks: list[dict]) -> str:
    header = ("CHECK", "STATUS", "MS", "DETAIL")
    rows = [header] + [(c["id"], c["status"], str(c["elapsed_ms"]), c["detail"])
                       for c in checks]
    widths = [max(len(str(r[i])) for r in rows) for i in range(len(header))]
    lines: list[str] = []
    for idx, row in enumerate(rows):
        lines.append("  ".join(str(row[i]).ljust(widths[i]) for i in range(len(header))).rstrip())
        if idx == 0:
            lines.append("  ".join("-" * widths[i] for i in range(len(header))))
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# live drivers (real IO; the pure checks above stay injectable)
# --------------------------------------------------------------------------- #

def _git(repo, *args: str, timeout: float = 30.0):
    try:
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None


def git_state(repo) -> tuple[bool, str, str]:
    r = _git(repo, "rev-parse", "--is-inside-work-tree")
    is_git = bool(r and r.returncode == 0 and r.stdout.strip() == "true")
    if not is_git:
        return False, "", ""
    rh = _git(repo, "rev-parse", "HEAD")
    head = rh.stdout.strip() if rh and rh.returncode == 0 else ""
    rp = _git(repo, "status", "--porcelain")
    porcelain = rp.stdout if rp and rp.returncode == 0 else ""
    return True, head, porcelain


def check_python_live() -> dict:
    try:
        import unittest  # noqa: F401
        importable = True
    except Exception:
        importable = False
    return check_python(version_info=tuple(sys.version_info[:3]), unittest_importable=importable)


def check_disk_live(repo) -> dict:
    try:
        usage = shutil.disk_usage(str(repo))
    except OSError as exc:
        return _result("disk", "FAIL", f"disk_usage failed: {exc}")
    return check_disk(usage.free)


def check_docker_live(timeout: float) -> dict:
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return check_docker(reachable=False, reason="docker not found on PATH")
    except subprocess.TimeoutExpired:
        return check_docker(reachable=False, reason=f"docker info timed out after {timeout:.0f}s")
    except Exception as exc:
        return check_docker(reachable=False, reason=f"{type(exc).__name__}: {exc}")
    if r.returncode == 0:
        return check_docker(reachable=True)
    return check_docker(reachable=False, reason=(r.stderr or r.stdout).strip()[:160])


def check_codex_binary_live(hits: list[Path], timeout: float) -> dict:
    if not hits:
        return check_codex_binary([])
    newest = newest_by_mtime(hits)
    version = ""
    try:
        r = subprocess.run([str(newest), "--version"], capture_output=True, text=True,
                           timeout=min(timeout, 30.0))
        shown = (r.stdout or r.stderr).strip()
        version = shown.splitlines()[0] if shown else ""
    except Exception as exc:
        version = f"<version probe failed: {type(exc).__name__}>"
    return check_codex_binary([str(p) for p in hits], version)


def check_codex_sandbox_live(newest: Path | None, model: str | None, timeout: float) -> dict:
    if newest is None:
        return _result("codex_sandbox", "SKIP", "no codex binary found")
    if model is None:
        return _result("codex_sandbox", "SKIP", "no --model provided")
    cmd = [str(newest), "exec", "-s", "read-only", "--model", model,
           "--skip-git-repo-check", "-"]
    try:
        r = subprocess.run(cmd, input=PROBE_COMMAND, capture_output=True, text=True,
                           timeout=timeout)
        output = (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return _result("codex_sandbox", "WARN", f"probe timed out after {timeout:.0f}s")
    except Exception as exc:
        return _result("codex_sandbox", "WARN", f"probe could not run: {type(exc).__name__}: {exc}")
    return check_codex_sandbox(output)


def _userprofile() -> Path:
    env = os.environ.get("USERPROFILE")
    return Path(env) if env else Path.home()


def check_model_pinning_live(model: str | None) -> dict:
    config_path = _userprofile().joinpath(*CONFIG_RELPATH)
    try:
        config_toml = config_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        config_toml = ""
    return check_model_pinning(config_toml, model)


def tcp_probe(port: int, host: str = "127.0.0.1", timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_loopback_live() -> dict:
    return check_loopback({port: tcp_probe(port) for port in LOOPBACK_PORTS})


def check_suite_baseline_live(repo, timeout: float) -> dict:
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"]
    t0 = time.perf_counter()
    try:
        r = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return _result("suite_baseline", "FAIL", f"baseline suite timed out after {timeout:.0f}s")
    except Exception as exc:
        return _result("suite_baseline", "FAIL", f"baseline suite could not run: {type(exc).__name__}")
    duration = time.perf_counter() - t0
    stderr = r.stderr or ""
    m = re.search(r"Ran (\d+) tests?", stderr)
    count = int(m.group(1)) if m else None
    return check_suite_baseline(ran=True, exit_code=r.returncode, test_count=count,
                                duration_s=duration)


def run_checks(args) -> tuple[list[dict], dict]:
    is_git, head, porcelain = git_state(args.repo)
    dirty = count_porcelain(porcelain)
    hits = find_codex_binaries(os.environ.get("LOCALAPPDATA"))
    newest = newest_by_mtime(hits)

    checks: list[dict] = [
        _timed(check_python_live),
        _timed(lambda: check_git_head(is_git=is_git, head=head, porcelain=porcelain,
                                      expect_head=args.expect_head,
                                      expect_dirty=args.expect_dirty)),
        _timed(lambda: check_disk_live(args.repo)),
        _timed(lambda: check_docker_live(min(args.timeout, 15.0))),
        _timed(lambda: check_codex_binary_live(hits, args.timeout)),
        _timed(lambda: check_codex_sandbox_live(newest, args.model, args.timeout)),
        _timed(lambda: check_model_pinning_live(args.model)),
        _timed(check_loopback_live),
        _timed(lambda: check_suite_baseline_live(args.repo, args.timeout))
        if args.with_suite else check_suite_baseline(ran=False),
    ]
    facts = {"head": head, "dirty": dirty}
    return checks, facts


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="preflight_check.py",
        description="Gather the pre-round environment checks for the PIPD governed lane.")
    ap.add_argument("--repo", type=Path, default=Path("."),
                    help="repository / work tree to inspect (default: current directory)")
    ap.add_argument("--model", default=None,
                    help="model the run will use; checked against ~/.codex/config.toml")
    ap.add_argument("--provider", default=None, help="provider the run will use")
    ap.add_argument("--expect-head", default=None, help="expected HEAD sha; mismatch is FAIL")
    ap.add_argument("--expect-dirty", type=int, default=None,
                    help="expected git status --porcelain line count; mismatch is FAIL")
    ap.add_argument("--json-out", type=Path, default=None,
                    help="where to write the JSON payload (default: ./PREFLIGHT.json)")
    ap.add_argument("--with-suite", action="store_true",
                    help="also run python -m unittest discover -s tests -q")
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="per-check subprocess timeout in seconds (default: 120)")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.repo = args.repo.resolve()
    checks, facts = run_checks(args)

    payload = build_payload(repo=args.repo, head=facts["head"], dirty=facts["dirty"],
                            checks=checks)
    payload["provider"] = args.provider

    out_path = args.json_out if args.json_out is not None else Path("PREFLIGHT.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                        encoding="utf-8", newline="")

    print(render_table(checks))
    print()
    print(f"verdict: {payload['verdict']} -- {payload['verdict_reason']}")
    print(f"json:    {out_path}")
    return exit_code_for(checks)


if __name__ == "__main__":
    raise SystemExit(main())
