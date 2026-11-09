#!/usr/bin/env python3
"""Write the dependency-coverage subjects the gate will re-measure.

The previous gate encoded a conclusion ("cryptography is declared") as a rule, so a tree where that
conclusion is false could not pass no matter what it measured. This file encodes only *subjects*:
which tree, which HEAD, which metadata file. The verdict is computed by the gate from the bytes at
gate time.

Three subjects exist because three trees exist and they disagree on the same line:

  hgk-main      GitHub main acd9196f   dependencies = []          issuer_binding.py present
  hgk-local     HG-KSEOS 6c9fc73       dependencies=[cryptography] issuer_binding.py absent
  hgk-worktree  r4-hgk a7046a3         dependencies = []          issuer_binding.py present

Which of them is the W0 baseline is the owner's decision (owner item HGK-REF-CANONICAL). The gate
reports all three; none of them is privileged by being first.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WS = os.path.dirname(ROOT)


def sha(p: str) -> str | None:
    if not os.path.isfile(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def head(repo: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ev = os.path.join(ROOT, "evidence")
    main_sha = open(os.path.join(ev, "HGK_MAIN_SHA.txt"), encoding="utf-8").read().strip()

    subjects = [
        {
            "name": "hgk-main",
            "kind": "repo",
            "label": "GitHub main (pinned contents fetched to evidence/)",
            "path": os.path.join(WS, "HG-KSEOS"),
            "head": main_sha,
            "head_source": "GitHub API /repos/shw097-team/HG-KSEOS/commits/main, contents fetched at that ref",
            "metadata_files": [os.path.join(ev, "HGK_MAIN_pyproject.toml")],
            "source_files": [
                os.path.join(ev, "HGK_MAIN_src_hg_kseos_fhs_issuer_binding.py"),
                os.path.join(ev, "HGK_MAIN_src_hg_kseos_lane_policy.py"),
            ],
            "scan_complete": False,
            "scan_note": "only the three files fetched at the pinned commit are scanned; the rest of that tree was not materialised here",
        },
        {
            "name": "hgk-local",
            "kind": "repo",
            "label": "HG-KSEOS working copy used by r9",
            "path": os.path.join(WS, "HG-KSEOS"),
            "head": head(os.path.join(WS, "HG-KSEOS")),
            "head_source": "git rev-parse HEAD",
            "metadata_files": [os.path.join(WS, "HG-KSEOS", "pyproject.toml")],
            "source_root": os.path.join(WS, "HG-KSEOS", "src"),
            "scan_complete": True,
        },
        {
            "name": "hgk-worktree",
            "kind": "repo",
            "label": "worktrees/r4-hgk, the tree the round before r9 measured",
            "path": os.path.join(WS, "worktrees", "r4-hgk"),
            "head": head(os.path.join(WS, "worktrees", "r4-hgk")),
            "head_source": "git rev-parse HEAD",
            "metadata_files": [os.path.join(WS, "worktrees", "r4-hgk", "pyproject.toml")],
            "source_root": os.path.join(WS, "worktrees", "r4-hgk", "src"),
            "scan_complete": True,
        },
    ]

    # Paths are recorded relative to this round so the descriptor stays usable inside a payload,
    # where the same files live under evidence/ rather than at a host absolute path.
    def rel(pth: str) -> str:
        pth = os.path.abspath(pth)
        for root in (ROOT, os.path.join(ROOT, "evidence")):
            try:
                r = os.path.relpath(pth, root)
                if not r.startswith(".."):
                    return os.path.join(os.path.basename(root) if root != ROOT else "", r).replace("\\", "/").lstrip("/") if root != ROOT else r.replace("\\", "/")
            except ValueError:
                continue
        return pth.replace("\\", "/")

    for s in subjects:
        s["path_base"] = "round"
        s["metadata_files_abs"] = list(s.get("metadata_files") or [])
        s["metadata_files"] = [rel(m) for m in (s.get("metadata_files") or [])]
        if s.get("source_root"):
            s["source_root"] = rel(s["source_root"])
        if s.get("source_files"):
            s["source_files"] = [rel(f) for f in s["source_files"]]
        s["metadata_sha256"] = {os.path.basename(m): sha(m) for m in s.get("metadata_files_abs", [])}

    out = {
        "schema": "FHS.W0.DependencySubjects/1",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "why_three": "the same line (pyproject 'dependencies') has three different values in three trees that are not ancestors of each other; a single-subject gate cannot be true for all of them",
        "canonical": {"state": "OWNER_UNRESOLVED", "owner_item": "HGK-REF-CANONICAL", "predicate": "owner names one HEAD as the W0 baseline; the others become lineage only"},
        "subjects": subjects,
    }
    p = os.path.join(ROOT, "out", "DEPENDENCY_SUBJECTS.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    for s in subjects:
        print(f"{s['name']:14} head={str(s['head'])[:12]} meta={list(s['metadata_sha256'].values())[0][:12] if list(s['metadata_sha256'].values())[0] else None} scan_complete={s['scan_complete']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
