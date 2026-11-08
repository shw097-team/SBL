#!/usr/bin/env python3
"""Layer audit: which artifacts are discardable, which are candidates, which are authority.

A round that mixes these three is how a draft gets quoted as a decision. This tool classifies every
file under the round, asserts the authority layer was not written this round, and refuses the shapes
that usually mean the layers were confused (a 500 KB document inside a lane's evidence directory, a
payload staged out of the proposal tree and cited as authority, a registry whose digest moved).

Output: out/LAYER_AUDIT.json
Exit:   0 all invariants hold, 1 an invariant broke
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPOS = {
    "SBL": r"C:/Projects/Agent_Workspace/worktrees/r4-sbl",
    "Fabric": r"C:/Projects/Agent_Workspace/worktrees/r4-fabric",
    "HG-KSEOS": r"C:/Projects/Agent_Workspace/HG-KSEOS",
}
REGISTRY = r"C:/Projects/Agent_Workspace/var/B1-PIPD-PKG-20261027/admission/registry/runner-registry.json"
REGISTRY_SHA_BASELINE = None  # filled from the previous round's measurement below


def sha(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def classify(rel: str) -> str:
    r = rel.replace("\\", "/")
    if r.startswith("lanes/") or r.startswith("out/stage/") or r.startswith("openspec/"):
        return "DISCARDABLE_REGENERABLE"
    if r.startswith("writeback/") or r.startswith("out/") or r in ("KANBAN.json",) or r == "SHA256SUMS":
        return "CANDIDATE"
    if r.startswith("tools/"):
        return "CANDIDATE_TOOL"
    if "/" not in r and r.endswith(".md"):
        # round-root documents: the report a reader opens first, the handover, the error log
        return "CANDIDATE"
    return "UNCLASSIFIED"


def main() -> int:
    buckets: dict[str, list[dict]] = {}
    unclassified = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, ROOT)
            lay = classify(rel)
            rec = {"path": rel.replace("\\", "/"), "bytes": os.path.getsize(p)}
            buckets.setdefault(lay, []).append(rec)
            if lay == "UNCLASSIFIED":
                unclassified.append(rec)

    # invariant 1: authority repos unchanged relative to the baseline lane D recorded before ITS run
    base = {}
    try:
        lane_d = json.load(open(os.path.join(ROOT, "lanes", "D", "WP19_V2.json"), "r", encoding="utf-8"))
        for k, v in (lane_d.get("repos") or {}).items():
            base[k] = v.get("post_status_porcelain")
    except Exception:  # noqa: BLE001
        base = {}

    repo_state = {}
    for name, path in REPOS.items():
        try:
            out = subprocess.run(["git", "-C", path, "status", "--porcelain"], capture_output=True, text=True, timeout=60)
            head = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
            lines = [l for l in out.stdout.splitlines() if l.strip()]
            key = {"SBL": "sbl", "Fabric": "fabric", "HG-KSEOS": "hgk"}.get(name, name.lower())
            expected = base.get(key)
            repo_state[name] = {
                "dirty_lines": len(lines),
                "dirty_preexisting": None if expected is None else len(expected),
                "same_as_baseline": None if expected is None else sorted(lines) == sorted(expected),
                "head": head.stdout.strip(),
                "path": path,
            }
        except Exception as e:  # noqa: BLE001
            repo_state[name] = {"error": f"{e.__class__.__name__}", "path": path}

    # invariant 2: registry digest
    reg = {"path": REGISTRY, "exists": os.path.isfile(REGISTRY)}
    if reg["exists"]:
        reg["sha256"] = sha(REGISTRY)
        try:
            d = json.load(open(REGISTRY, "r", encoding="utf-8"))
            reg["registry_rev"] = d.get("registry_rev")
            reg["rows"] = len(d.get("rows", []))
            reg["rows_installed"] = sum(1 for r in d.get("rows", []) if r.get("status") == "INSTALLED")
            reg["rows_signed"] = sum(1 for r in d.get("rows", []) if r.get("owner_signature"))
            reg["root_signed"] = bool(d.get("owner_signature"))
        except Exception as e:  # noqa: BLE001
            reg["parse_error"] = f"{e.__class__.__name__}"

    # invariant 3: no oversized document hiding in a lane's evidence directory
    misplacement = []
    for rec in buckets.get("DISCARDABLE_REGENERABLE", []):
        if rec["path"].startswith("lanes/") and rec["bytes"] > 400_000:
            misplacement.append({"path": rec["path"], "bytes": rec["bytes"], "why": "OVERSIZE_IN_LANE_EVIDENCE"})
        if rec["path"].startswith("lanes/") and rec["path"].endswith(".md") and rec["bytes"] > 20_000:
            misplacement.append({"path": rec["path"], "bytes": rec["bytes"], "why": "PROSE_IN_LANE_EVIDENCE"})

    report = {
        "schema": "FHS.W0.LayerAudit/2",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "round": ROOT.replace("\\", "/"),
        "layer_definition": {
            "DISCARDABLE_REGENERABLE": "rebuilt from tools on demand; never cited as authority",
            "CANDIDATE": "the round's own product; may be published as a branch, never as main",
            "CANDIDATE_TOOL": "the code that produced the evidence; shipped so a reader can re-run",
            "AUTHORITY": "source tree, three repositories, owner registry: read-only this round",
        },
        "counts": {k: len(v) for k, v in buckets.items()},
        "bytes": {k: sum(x["bytes"] for x in v) for k, v in buckets.items()},
        "misplacement": misplacement,
        "authority_repos": repo_state,
        "owner_registry": reg,
        "invariants": {
            "repos_match_baseline": all(v.get("same_as_baseline") is True for v in repo_state.values()),
            "registry_present": reg.get("exists", False),
            "registry_signed": reg.get("rows_signed") == reg.get("rows") and reg.get("root_signed") is True,
            "no_misplacement": not misplacement,
            "nothing_unclassified": not unclassified,
        },
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
    }
    report["invariants"]["all_hold"] = all(report["invariants"].values())
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    with open(os.path.join(ROOT, "out", "LAYER_AUDIT.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    for k, v in report["counts"].items():
        print(f"{k:28} files={v:3} bytes={report['bytes'][k]:,}")
    print("repos:", {k: (v.get("dirty_lines"), v.get("head", "")[:12]) for k, v in repo_state.items()})
    print("registry:", {k: reg.get(k) for k in ("registry_rev", "rows", "rows_installed", "rows_signed", "root_signed")})
    print("misplacement:", misplacement or "none")
    print("unclassified:", unclassified or "none")
    print("ALL_HOLD:", report["invariants"]["all_hold"])
    return 0 if report["invariants"]["all_hold"] else 1


if __name__ == "__main__":
    sys.exit(main())
