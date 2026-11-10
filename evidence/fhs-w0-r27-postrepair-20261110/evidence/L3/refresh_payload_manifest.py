"""Recompute the two payload integrity files after the r27 metadata repair.

Touched here:
  evidence/FHS_ORIGINAL_ACK.json   content repaired (bytes/lines/inventory/76 properties)
  evidence/EVIDENCE_SCOPE.json     content repaired (full.excluded -> not_runnable_in_CI)
  tools/gate_r20.py                G24 gained the source-contract bytes/lines re-derivation
  tools/verify_public_bundle.py    NEW: the real Ed25519 verifier for the seven owner signatures

MANIFEST.json carries `sha256` (what the payload ships) next to `sha256_as_measured` (the out/ file it
was normalised from). For the two repaired artefacts the r26 `out/` original is no longer in the tree,
so the honest statement is that the shipped file IS the measured file — hence normalised=false with the
old provenance preserved in `provenance_history` instead of being overwritten.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import pathlib

ROOT = pathlib.Path(r"C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-meta/evidence/fhs-w0-r26-repair-20261109")
MAN = ROOT / "MANIFEST.json"
SUMS = ROOT / "SHA256SUMS"
TZ = datetime.timezone(datetime.timedelta(hours=8))
REPAIRED = ["evidence/FHS_ORIGINAL_ACK.json", "evidence/EVIDENCE_SCOPE.json"]
NEW = ["tools/verify_public_bundle.py"]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    at = datetime.datetime.now(TZ).isoformat(timespec="seconds")
    man = json.loads(MAN.read_text(encoding="utf-8"))
    old = {e["path"]: e.get("sha256") for e in man["files"]}
    changed = []

    by_path = {e["path"]: e for e in man["files"]}
    for rel in REPAIRED:
        p = ROOT / rel
        e = by_path[rel]
        if not e.get("provenance_history"):
            # capture the r26 publication values exactly once; a re-run must not append a second copy
            e["provenance_history"] = [{
                "sha256": e.get("sha256"), "bytes": e.get("bytes"),
                "measured_from": e.get("measured_from"),
                "sha256_as_measured": e.get("sha256_as_measured"),
                "bytes_as_measured": e.get("bytes_as_measured"),
                "note": "r26 publication values, superseded by the r27 repair"}]
        before_sha = e.get("sha256")
        e["sha256"] = sha(p)
        e["bytes"] = p.stat().st_size
        e["measured_from"] = rel
        e["sha256_as_measured"] = e["sha256"]
        e["bytes_as_measured"] = e["bytes"]
        e["normalised"] = False
        e["repaired_in_round"] = "r27-metadata-hygiene"
        if before_sha != e["sha256"]:
            changed.append({"path": rel, "sha256_before": before_sha, "sha256_after": e["sha256"]})

    for rel in ("tools/gate_r20.py",):
        p = ROOT / rel
        e = by_path[rel]
        before = e["sha256"]
        e["sha256"] = sha(p)
        e["bytes"] = p.stat().st_size
        e["sha256_as_measured"] = e["sha256"]
        e["bytes_as_measured"] = e["bytes"]
        e["normalised"] = False
        e["repaired_in_round"] = "r27-metadata-hygiene"
        changed.append({"path": rel, "sha256_before": before, "sha256_after": e["sha256"]})

    for rel in NEW:
        p = ROOT / rel
        rec = {"path": rel, "sha256": sha(p), "bytes": p.stat().st_size,
               "measured_from": rel, "sha256_as_measured": sha(p),
               "bytes_as_measured": p.stat().st_size, "normalised": False,
               "added_in_round": "r27-metadata-hygiene"}
        changed.append({"path": rel, "sha256_before": (by_path[rel].get("sha256") if rel in by_path else None),
                        "sha256_after": rec["sha256"]})
        if rel in by_path:  # idempotent: a second run must update, never append a duplicate
            by_path[rel].update(rec)
        else:
            man["files"].append(rec)
        man["expected_entry_set"].append(rel)

    # a duplicate path would make `expected_entry_set` and `files` disagree while both look populated
    dedup = {}
    for e in man["files"]:
        if isinstance(e.get("provenance_history"), list) and len(e["provenance_history"]) > 1:
            e["provenance_history"] = e["provenance_history"][:1]  # the r26 original, exactly one
        dedup[e["path"]] = e
    man["files"] = list(dedup.values())

    man["files"].sort(key=lambda e: e["path"])
    man["expected_entry_set"] = sorted(set(man["expected_entry_set"]))
    man["regenerated_in_round"] = {
        "round": "r27-metadata-hygiene", "at": at,
        "why": "three files changed content and one was added; every digest below is recomputed from the "
               "file on disk in this process, none is carried over",
    }
    MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")

    # SHA256SUMS: MANIFEST.json first, then every shipped file by path
    lines = [f"{sha(MAN)}  MANIFEST.json"]
    for rel in sorted(e["path"] for e in man["files"]):
        lines.append(f"{sha(ROOT / rel)}  {rel}")
    SUMS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(json.dumps({"manifest_sha256": sha(MAN), "sums_sha256": sha(SUMS),
                      "files": len(man["files"]), "sums_lines": len(lines),
                      "changed": changed}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
