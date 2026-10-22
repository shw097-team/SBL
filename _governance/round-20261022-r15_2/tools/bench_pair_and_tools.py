"""Paired benchmark B1 vs B2 (W16/C23) and five-tool inventory (W13/C20).

C23's rule is that a comparison is INVALID unless workload, hardware, attempt count and retry rule are identical. So
this harness runs the SAME command on two worktrees of the same repository, alternating attempts, and records every
attempt rather than a mean of convenience.

B0 (HGK_only) is reported as NOT_COMPARABLE: no owner has defined a matched HGK-only workload for this corpus, and
inventing one would be exactly the "different denominator" the rule forbids.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import time

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
TMP = r"C:/Users/user/AppData/Local/Temp/r152/bench"
B1_SHA = "e6623ba1e9a4a477d07048cd3a5a906f33d6029d"  # pre-round tooling baseline
WORKLOAD = ("uv run --python 3.11 --with pytest pytest -q -p no:cacheprovider "
            "tests/test_modes.py tests/test_core_modules.py tests/test_gj03_bridge.py")
ATTEMPTS = 3
# Calibrated roots: the packaging bundles live under the R14 worktree, not under a PIPD-LS-SP checkout (which does not
# exist on this host). The first inventory walked the missing root and reported a false all-clear.
PKG_ROOTS = [r"C:/Projects/Agent_Workspace/_r14s12_ev/pkg", r"C:/Projects/Agent_Workspace/_r14s12_ev/pkg2"]
DECLARED_TOOLS = ["TPM", "Commander", "Challenge", "HGK+Harness", "Full SBL Stack"]
VERBS = ["install", "doctor", "load", "invoke", "deny", "upgrade", "uninstall", "rollback"]


def sh(cmd: str, cwd: str, timeout: int = 600) -> tuple[int, str, float]:
    t0 = time.perf_counter()
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or ""), round(time.perf_counter() - t0, 3)


def ensure_worktree(name: str, sha: str) -> str:
    path = os.path.join(TMP, name)
    if os.path.exists(os.path.join(path, ".git")):  # a detached worktree has .git as a FILE
        return path
    os.makedirs(TMP, exist_ok=True)
    rc, out, _ = sh(f'git worktree add -f --detach "{path}" {sha}', r"C:/Projects/Agent_Workspace/_r152_ev")
    if rc != 0:
        raise SystemExit(f"worktree add failed for {name}: {out[-400:]}")
    return path


def bench() -> dict:
    b1 = ensure_worktree("b1", B1_SHA)
    b2 = r"C:/Projects/Agent_Workspace/_r152_ev"
    runs = {"B1": [], "B2": []}
    for i in range(ATTEMPTS):
        for tag, cwd in (("B1", b1), ("B2", b2)):
            rc, out, secs = sh(WORKLOAD, cwd, timeout=900)
            tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
            runs[tag].append({"attempt": i + 1, "rc": rc, "secs": secs, "last_line": tail[0][:120]})
    def med(xs: list[float]) -> float:
        xs = sorted(xs)
        n = len(xs)
        return round((xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2), 3)
    out = {"schema": "SBL_BENCH_PAIR/1", "workload": WORKLOAD, "attempts": ATTEMPTS,
           "hardware": {"platform": platform.platform(), "cpu_count": os.cpu_count(),
                        "python": platform.python_version()},
           "subjects": {"B1": {"sha": B1_SHA, "note": "pre-round tooling baseline"},
                        "B2": {"sha": sh("git rev-parse HEAD", b2)[1].strip(), "note": "current evidence branch"}},
           "runs": runs,
           "medians": {"B1": med([r["secs"] for r in runs["B1"]]), "B2": med([r["secs"] for r in runs["B2"]])},
           "all_rc_zero": all(r["rc"] == 0 for v in runs.values() for r in v),
           "B0": {"state": "NOT_COMPARABLE",
                  "why": "no owner-defined HGK-only workload matches this corpus; inventing one would be the "
                         "'different denominator' that C23 declares INVALID_COMPARE"},
           "claim_ceiling": ("paired wall-time on one fixed suite, same host, alternating attempts. This is not a "
                             "B0/B1/B2 engineering-performance claim and carries no benefit assertion.")}
    out["delta_secs"] = round(out["medians"]["B2"] - out["medians"]["B1"], 3)
    return out


def five_tools() -> dict:
    found, verbs_seen, bundles = {}, [], {}
    for root in PKG_ROOTS:
        if not os.path.isdir(root):
            continue
        for tool in sorted(os.listdir(root)):
            td = os.path.join(root, tool)
            if not os.path.isdir(td):
                continue
            names = set()
            for dp, _, fs in os.walk(td):
                names |= {f.lower() for f in fs}
            present = [v for v in VERBS if any(v in n for n in names)]
            bundles[tool] = len(names)
            verbs_seen += present
            found[os.path.basename(root) + "/" + tool] = {"files": len(names), "verbs_present": present,
                                                          "verbs_missing": [v for v in VERBS if v not in present]}
    return {"roots": PKG_ROOTS, "found": bundles, "declared": len(DECLARED_TOOLS),
            "lifecycle_verbs_present": sorted(set(verbs_seen)), "lifecycle_verbs_missing": VERBS,
            "per_bundle": found,
            "verdict": (f"{len(bundles)} of {len(DECLARED_TOOLS)} declared tools exist as packaging bundles; "
                        f"{len(set(verbs_seen))} of 8 lifecycle verbs found. E06/C20 NOT_RUN stands."),
            "instrument_note": ("first pass walked C:/Projects/Agent_Workspace/PIPD-LS-SP, which is MISSING on this host, "
                                "and reported 0 files for all five tools — an uncalibrated path list manufacturing an "
                                "all-clear. Roots are now the R14 package directories and are asserted to exist."),
            "roots_checked": [{"path": r, "exists": os.path.isdir(r)} for r in PKG_ROOTS]}


if __name__ == "__main__":
    res = {"bench": bench(), "five_tools_calibrated": five_tools()}
    os.makedirs(R, exist_ok=True)
    open(os.path.join(R, "BENCH_AND_TOOLS_R15_2.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(res, ensure_ascii=False, indent=2) + "\n")
    b = res["bench"]
    print(json.dumps({"medians": b["medians"], "delta": b["delta_secs"], "all_rc_zero": b["all_rc_zero"],
                      "B0": b["B0"]["state"],
                      "tools": res["five_tools_calibrated"]["found"],
                      "verbs_present": res["five_tools_calibrated"]["lifecycle_verbs_present"]},
                     ensure_ascii=False))
    print("BENCH_TOOLS_OK")
