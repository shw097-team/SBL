"""S2-07 S207-GITHUB-DELIVER (bundle step): assemble a sanitized, self-describing evidence bundle.

Writes only under var/R17-20261023/deliver_s207/. Refuses to emit if a secret-shaped string is
found in any file it is about to publish. No repo is touched here; the git step is separate.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
BUNDLE = VAR / "deliver_s207"
TPE = timezone(timedelta(hours=8))

SECRET_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{12,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"eyJhbGciOi[A-Za-z0-9_\-\.]{40,}"),  # JWT
]

RECEIPTS = [
    "R17_S207_RECON.json", "R17_S207_POSTSESSION.json", "R17_S207_SOURCE_FREEZE.json",
    "R17_S207_ENTRYPOINT_BIND.json", "R17_S207_CONTAINMENT.json", "S207_READY_ARMED.json",
    "S207_READY_NOARM.json", "R17_S207_CRASHWINDOW.json", "R17_S207_LANE_PLAN_VERIFY.json",
    "R17_S207_SANDBOX.json", "R17_S207_CAPC_COMPILE.json",
    "S207_CAPC_SURVEY.json", "S207_PIPD_PROBES.json", "S207_FABRIC_CANARY.json",
]
EXTRA = ["capc/S2-07_contract.json", "capc/s207/thin-prompt.md"]
TOOLS = ["s207_bundle.py", "build_capc_s207.py", "s207_recon.py", "s207_postsession.py", "s207_bind.py", "s207_containment.py",
         "s207_crashwin.py", "s207_lanes.py", "s207_sandbox.py",
         "advance.py", "runner.py", "rg04_probe.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    (BUNDLE / "receipts").mkdir(parents=True)
    (BUNDLE / "tools").mkdir(parents=True)
    index = {"schema": "R17_S207_EVIDENCE_BUNDLE/1",
             "generated_local": datetime.now(TPE).isoformat(timespec="seconds"),
             "mission_id": "SBL-R17-FULL-INTEGRATED-NATIVE-20261023",
             "files": {}, "missing": [], "excluded": [
                 "hermes cron/executions.db and state.db (account/telemetry rows)",
                 "codex auth.json and any lane home (credentials)",
                 "OS-keyed secrets under API KEY/",
                 "the whole product working trees (only change metadata is included)",
             ]}
    for name in RECEIPTS:
        src = VAR / "receipts" / name
        if not src.exists():
            index["missing"].append(name)
            continue
        dst = BUNDLE / "receipts" / name
        shutil.copy2(src, dst)
        index["files"][f"receipts/{name}"] = {"sha256": sha(dst), "bytes": dst.stat().st_size}
    for name in TOOLS:
        src = VAR / "tools" / name
        if not src.exists():
            index["missing"].append(name)
            continue
        dst = BUNDLE / "tools" / name
        shutil.copy2(src, dst)
        index["files"][f"tools/{name}"] = {"sha256": sha(dst), "bytes": dst.stat().st_size}

    for rel in EXTRA:
        src = VAR / rel
        if not src.exists():
            index["missing"].append(rel)
            continue
        dst = BUNDLE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        index["files"][rel] = {"sha256": sha(dst), "bytes": dst.stat().st_size}

    # secret scan before anything leaves the host
    hits = {}
    for p in BUNDLE.rglob("*"):
        if not p.is_file():
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in SECRET_PATTERNS:
            m = pat.search(txt)
            if m:
                hits.setdefault(str(p.relative_to(BUNDLE)), []).append(pat.pattern[:24])
    index["secret_scan"] = {"clean": not hits, "hits": hits}
    if hits:
        (BUNDLE / "EVIDENCE_INDEX.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({"aborted": "SECRET_SHAPED_STRING_FOUND", "hits": hits}))
        return 2
    (BUNDLE / "EVIDENCE_INDEX.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"files": len(index["files"]), "missing": index["missing"],
                      "clean": True, "bundle": str(BUNDLE)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
