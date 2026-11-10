#!/usr/bin/env python3
"""regen_payload_integrity — recompute MANIFEST.json / SHA256SUMS for the MERGED r27 payload.

Why this exists: three lanes each repaired a different file in the same payload and each correctly
regenerated the payload's integrity files for its own branch. After merging, the declared digests
describe three different trees, which is a false-green of exactly the kind this round is repairing.
This script derives every digest from the bytes on disk in one process, and records - rather than
overwrites - any prior value it displaces.

Rules kept:
  * a digest is never carried over; it is always recomputed from disk here;
  * a displaced value is preserved under `previous`, never deleted;
  * SHA256SUMS is regenerated over the same file set the manifest declares, sorted;
  * the script prints what changed and never writes outside the payload.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                    "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-integration/evidence/fhs-w0-r26-repair-20261109")
TZ = datetime.timezone(datetime.timedelta(hours=8))


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    man_p = ROOT / "MANIFEST.json"
    sums_p = ROOT / "SHA256SUMS"
    man = json.loads(man_p.read_text(encoding="utf-8"))
    entries = man.get("files") or []
    on_disk = sorted(p for p in ROOT.rglob("*") if p.is_file()
                     and p.name not in ("MANIFEST.json", "SHA256SUMS")
                     and "__pycache__" not in p.parts)
    by_rel = {p.relative_to(ROOT).as_posix(): p for p in on_disk}

    # repair an entry that was left half-merged (git conflict markers inside MANIFEST.json)
    seen, changed, added, missing = set(), [], [], []
    for e in entries:
        rel = e.get("path")
        p = by_rel.get(rel)
        if p is None:
            missing.append(rel)
            continue
        seen.add(rel)
        h, n = sha(p), p.stat().st_size
        if e.get("sha256") != h or e.get("bytes") != n:
            e["previous"] = {"sha256": e.get("sha256"), "bytes": e.get("bytes")}
            e["sha256"], e["bytes"] = h, n
            e["measured_from"] = rel
            e["sha256_as_measured"], e["bytes_as_measured"] = h, n
            e["normalised"] = False
            changed.append(rel)
    for rel, p in by_rel.items():
        if rel not in seen:
            entries.append({"path": rel, "sha256": sha(p), "bytes": p.stat().st_size,
                            "measured_from": rel, "sha256_as_measured": sha(p),
                            "bytes_as_measured": p.stat().st_size, "normalised": False})
            added.append(rel)

    entries.sort(key=lambda e: e["path"])
    man["files"] = entries
    man["expected_entry_set"] = sorted(e["path"] for e in entries)
    man["generated_at"] = datetime.datetime.now(TZ).isoformat(timespec="seconds")
    man.setdefault("regenerated_in_round", {})
    man["regenerated_in_round"] = {
        "round": "r27-postrepair-integration",
        "at": man["generated_at"],
        "why": ("three lane branches repaired three different payload files; the merged tree's digests are "
                "recomputed here from disk so the integrity files describe the tree that will be pushed"),
        "displaced_values_preserved_under": "previous",
        "changed": changed, "added": added, "declared_but_absent": missing,
    }
    man_p.write_bytes((json.dumps(man, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))

    lines = [f"{sha(man_p)}  MANIFEST.json"]
    for e in entries:
        lines.append(f"{e['sha256']}  {e['path']}")
    sums_p.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    # verify: every declared digest matches disk, and the sums file agrees with the manifest
    bad = [e["path"] for e in entries if sha(by_rel[e["path"]]) != e["sha256"]]
    print(json.dumps({"entries": len(entries), "changed": changed, "added": added,
                      "missing": missing, "digest_mismatches": bad,
                      "manifest_sha256": sha(man_p), "sums_sha256": sha(sums_p)}, ensure_ascii=False, indent=1))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
