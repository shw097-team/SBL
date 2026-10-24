"""S2-07 RG00 freeze + S207-HOTPATH-DIFF-QUALIFY binding receipt.

Read-only over the governed tree. Emits two receipts:
  receipts/R17_S207_SOURCE_FREEZE.json
  receipts/R17_S207_ENTRYPOINT_BIND.json

The binding receipt answers one narrow question: which code object actually
implements card selection / cursor / ACK on the host hot path, and what is its
sha256 right now. Nothing here claims the fix is correct, only where it lives.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
WS = Path("C:/Projects/Agent_Workspace")
HERMES = Path(os.environ["LOCALAPPDATA"]) / "Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes"
SBL = WS / "知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL"
TPE = timezone(timedelta(hours=8))


def lp(p) -> str:
    s = str(p)
    if s.startswith("\\\\?\\"):
        return s
    n = s.replace("/", "\\")
    return "\\\\?\\" + n if len(n) > 220 else n


def sha(p) -> str | None:
    try:
        return hashlib.sha256(Path(lp(p)).read_bytes()).hexdigest()
    except OSError:
        return None


def size(p) -> int | None:
    try:
        return Path(lp(p)).stat().st_size
    except OSError:
        return None


def freeze_docs():
    out = {"sbl_docs": [], "pipd_docs": [], "kp": [], "r151": None, "counts": {}}
    pkg = SBL / "SBL_PIPD-LS-PKG"
    if pkg.exists():
        for p in sorted(pkg.glob("SBL_PIPD-LS-PKG_DOC-*.md")):
            out["sbl_docs"].append({"name": p.name, "bytes": size(p), "sha256": sha(p)})
    pdir = SBL / "參考工程資料庫/PIPD-LS/PIPD_LS"
    if pdir.exists():
        for p in sorted(pdir.glob("PIPD_LS_DOC-*.md")):
            out["pipd_docs"].append({"name": p.name, "bytes": size(p), "sha256": sha(p)})
    else:
        for p in sorted(SBL.rglob("PIPD_LS_DOC-*.md")):
            out["pipd_docs"].append({"name": p.name, "rel": str(p.relative_to(SBL)),
                                     "bytes": size(p), "sha256": sha(p)})
    kp_root = None
    for cand in SBL.rglob("KnowledgePack"):
        if cand.is_dir():
            kp_root = cand
            break
    if kp_root:
        for p in sorted(Path(lp(kp_root)).glob("*.md")):
            out["kp"].append({"name": p.name, "bytes": size(p), "sha256": sha(p)})
        out["kp_root"] = str(kp_root)
    r = SBL / "SBL_HGK_FABRIC_PIPD_LS_PKG_R15_1_FULL_SUBSTANTIVE_INTEGRATED_REPAIR_REPLACEMENT_2026-10-22.md"
    if r.exists():
        out["r151"] = {"bytes": size(r), "sha256": sha(r), "path": r.name}
    out["counts"] = {"sbl_docs": len(out["sbl_docs"]), "pipd_docs": len(out["pipd_docs"]),
                     "kp": len(out["kp"]), "sbl_docs_missing_sha": sum(1 for d in out["sbl_docs"] if not d["sha256"]),
                     "kp_missing_sha": sum(1 for d in out["kp"] if not d["sha256"])}
    return out


def repos():
    out = {}
    for n, p in {"SBL": WS / "SBL", "HG-KSEOS": WS / "HG-KSEOS",
                 "Fabric": WS / "Fabric", "PIPD": WS / "PIPD"}.items():
        def g(*a):
            r = subprocess.run(["git", "-C", str(p).replace("/", "\\"), *a],
                               capture_output=True, text=True, timeout=90)
            return (r.stdout or "").strip()
        out[n] = {"head": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
                  "tracked_dirty": len([x for x in g("status", "--porcelain", "-uno").splitlines() if x.strip()]),
                  "untracked": len([x for x in g("status", "--porcelain").splitlines() if x.startswith("??")])}
    return out


def bind():
    """Resolve the real chain: job row -> wrapper -> runner -> advance -> code objects."""
    jobs = json.loads((HERMES / "cron/jobs.json").read_text(encoding="utf-8", errors="replace"))
    rows = jobs.get("jobs", jobs if isinstance(jobs, list) else [])
    job = next((j for j in rows if str(j.get("id")) == "3602bce285e8"), {})
    wrapper = HERMES / "scripts" / str(job.get("script"))
    chain = {"job_id": job.get("id"), "job_script": job.get("script"),
             "wrapper_path": str(wrapper), "wrapper_sha256": sha(wrapper) if wrapper.exists() else None}
    # which modules does the wrapper reference?
    refs = []
    if wrapper.exists():
        txt = wrapper.read_text(encoding="utf-8", errors="replace")
        for line in txt.splitlines():
            s = line.strip()
            if ("runner" in s or "advance" in s or "import " in s or "subprocess" in s) and not s.startswith("#"):
                refs.append(s[:160])
    chain["wrapper_references"] = refs[:40]
    chain["files"] = {}
    for rel in ("tools/runner.py", "tools/advance.py", "tools/mission_runner.py"):
        p = VAR / rel
        chain["files"][rel] = {"exists": p.exists(), "sha256": sha(p) if p.exists() else None,
                               "bytes": size(p)}
    # runtime import resolution inside the runner's own import path
    code = r'''
import json, sys, hashlib, inspect
sys.path.insert(0, r"%s")
sys.path.insert(0, r"%s")
res = {}
for mod in ("advance", "runner"):
    try:
        spec = __import__("importlib").util.find_spec(mod)
        m = __import__(mod)
        res[mod] = {"file": getattr(m, "__file__", None),
                    "sha256": hashlib.sha256(open(getattr(m, "__file__"), "rb").read()).hexdigest(),
                    "names": [n for n in dir(m) if not n.startswith("_")][:40]}
    except Exception as e:
        res[mod] = {"error": repr(e)}
info = {}
for mod in ("advance", "runner"):
    if "error" in res.get(mod, {}):
        continue
    m = sys.modules[mod]
    hits = {}
    for name, obj in vars(m).items():
        if callable(obj) and getattr(obj, "__module__", None) == mod:
            try:
                src = inspect.getsource(obj)
            except (OSError, TypeError):
                continue
            if "cursor" in src or "ready[0]" in src or "select" in name.lower():
                hits[name] = {"sha_of_source": hashlib.sha256(src.encode()).hexdigest(),
                              "mentions_ready0": "ready[0]" in src,
                              "mentions_cursor": "cursor" in src,
                              "lines": len(src.splitlines())}
    info[mod] = hits
print(json.dumps({"modules": res, "code_objects": info}))
''' % (str(VAR / "tools"), str(VAR / "tools"))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=180,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    try:
        chain["runtime"] = json.loads(r.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        chain["runtime"] = {"error": "unparsable", "stdout": r.stdout[-1500:], "stderr": r.stderr[-1500:]}
    return chain


def main():
    stamp = datetime.now(TPE).isoformat(timespec="seconds")
    src = {"schema": "R17_S207_SOURCE_FREEZE/1", "generated_local": stamp,
           "sbl_root": str(SBL), "docs": freeze_docs(), "repos": repos(),
           "hold": {"exists": (VAR / "HOLD_EXECUTE_WRITER.json").exists(),
                    "sha256": sha(VAR / "HOLD_EXECUTE_WRITER.json")},
           "arm": {"exists": (VAR / "RG04_ARM.json").exists(),
                   "sha256": sha(VAR / "RG04_ARM.json")}}
    (VAR / "receipts").mkdir(parents=True, exist_ok=True)
    (VAR / "receipts/R17_S207_SOURCE_FREEZE.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b = {"schema": "R17_S207_ENTRYPOINT_BIND/1", "generated_local": stamp, **bind()}
    (VAR / "receipts/R17_S207_ENTRYPOINT_BIND.json").write_text(
        json.dumps(b, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"freeze_counts": src["docs"]["counts"], "repos": {k: v["head"][:8] for k, v in src["repos"].items()},
                      "bind_files": {k: (v["sha256"] or "")[:12] for k, v in b["files"].items()}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
