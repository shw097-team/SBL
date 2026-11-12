#!/usr/bin/env python3
"""Stage the r9 payloads and write a manifest that resolves entirely inside each payload.

The defect this is built against (V-05): a manifest whose entry points at bytes that live in a
*different* payload. A reader that verifies the manifest from where it sits gets a false "absent"
or, worse, verifies a digest it cannot see. So each payload carries its own manifest, its paths are
relative to that manifest, and `verify_payload_manifest.py` refuses any entry that leaves the tree.

SBL is normalised to LF because that repository asserts LF-clean blobs; the manifest then records the
*published* digest and, when it differs, the round digest beside it. Fabric keeps byte identity
because it has no such invariant and its mirror must agree with the digests its neighbours cite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SBL_FILES = [
    ("writeback/W0/FHS_PIPD-LS-PKG_W0_r9.md", "FHS_PIPD-LS-PKG_W0_r9.md"),
    ("KANBAN.json", "KANBAN.json"),
    ("out/SOURCE_COPY_REGISTER.json", "SOURCE_COPY_REGISTER.json"),
    ("out/GATE_R9.json", "gate/GATE_R9.json"),
    ("out/GATE_R9_ON_PRIOR.json", "gate/GATE_R9_ON_PRIOR.json"),
    ("out/GATE_R9_SELFTEST.json", "gate/GATE_R9_SELFTEST.json"),
    ("out/GATE_R9_INHERITED.json", "gate/GATE_R9_INHERITED.json"),
    ("lanes/A/SOURCE_LOCK_V2.json", "lanes/A_SOURCE_LOCK_V2.json"),
    ("lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json", "lanes/A_AUTHORITY_CONFLICT_LEDGER_V2.json"),
    ("lanes/B/U0_PARTITION_V2.json", "lanes/B_U0_PARTITION_V2.json"),
    ("lanes/B/TILE_PROOF.txt", "lanes/B_TILE_PROOF.txt"),
    ("lanes/C/DISTINCTNESS_V2.json", "lanes/C_DISTINCTNESS_V2.json"),
    ("lanes/D/WP19_V2.json", "lanes/D_WP19_V2.json"),
    ("lanes/E/WP21_ENUM_V2.json", "lanes/E_WP21_ENUM_V2.json"),
    ("out/A01_DEPENDENCY_PATCH/RESULT.json", "a01/RESULT.json"),
    ("out/A01_DEPENDENCY_PATCH/pyproject.toml.patch", "a01/pyproject.toml.patch"),
    ("tools/gate_w0r9.py", "tools/gate_w0r9.py"),
    ("tools/build_copy_register.py", "tools/build_copy_register.py"),
    ("tools/a01_dependency_patch.py", "tools/a01_dependency_patch.py"),
    ("tools/stage_r9.py", "tools/stage_r9.py"),
    ("tools/verify_payload_manifest.py", "tools/verify_payload_manifest.py"),
    ("writeback/W0/W0_REVISION_MANIFEST.json", "sidecars/W0_REVISION_MANIFEST.json"),
    ("writeback/W0/W0_CLOSEOUT_DECISION.json", "sidecars/W0_CLOSEOUT_DECISION.json"),
    ("writeback/W0/W0_HOLD_RESUME.json", "sidecars/W0_HOLD_RESUME.json"),
    ("writeback/W0/W0_EVIDENCE_INDEX.json", "sidecars/W0_EVIDENCE_INDEX.json"),
    ("writeback/W0/W0_WP_MATRIX.json", "sidecars/W0_WP_MATRIX.json"),
    ("out/FHS_W0_R9_IMPLEMENTATION_REPAIR_REPORT_2026-11-08.md", "FHS_W0_R9_IMPLEMENTATION_REPAIR_REPORT_2026-11-08.md"),
    ("out/SELF_ERRORS.md", "SELF_ERRORS.md"),
    ("out/LAYER_AUDIT.json", "LAYER_AUDIT.json"),
    ("tools/build_r9.py", "tools/build_r9.py"),
    ("tools/build_report.py", "tools/build_report.py"),
    ("tools/layer_audit.py", "tools/layer_audit.py"),
]

FABRIC_FILES = [
    ("writeback/W0/FHS_PIPD-LS-PKG_W0_r9.md", "FHS_PIPD-LS-PKG_W0_r9.md"),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def put(src: str, dst: str, normalise_lf: bool) -> dict:
    raw = open(src, "rb").read()
    out = raw
    if normalise_lf:
        out = raw.replace(b"\r\n", b"\n")
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    with open(dst, "wb") as fh:
        fh.write(out)
    rec = {"path": os.path.relpath(dst, os.path.dirname(os.path.dirname(dst))).split(os.sep)[-1],
           "bytes": len(out), "sha256": sha(out)}
    if out != raw:
        rec["normalised_from_crlf"] = True
        rec["sha256_round"] = sha(raw)
        rec["bytes_round"] = len(raw)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=ROOT)
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "stage"))
    a = ap.parse_args()
    ts = os.environ.get("FHS_ROUND_TS") or datetime.now(TZ).isoformat(timespec="seconds")

    missing = [s for s, _ in SBL_FILES + FABRIC_FILES if not os.path.isfile(os.path.join(a.round, s))]
    if missing:
        print("MISSING_SOURCE_FILES:")
        for m in missing:
            print("  ", m)
        return 2

    for p in (os.path.join(a.out, "sbl"), os.path.join(a.out, "fabric")):
        shutil.rmtree(p, ignore_errors=True)

    sbl_root = os.path.join(a.out, "sbl", "evidence", "fhs-w0-r9-repair-20261108")
    fabric_root = os.path.join(a.out, "fabric", "INTEGRATION", "FHS", "docs", "as-built", "W0", "r9")

    entries = []
    for src, rel in SBL_FILES:
        dst = os.path.join(sbl_root, rel.replace("/", os.sep))
        rec = put(os.path.join(a.round, src), dst, normalise_lf=True)
        rec["path"] = rel
        entries.append(rec)
    sbl_manifest = {
        "schema": "FHS.W0.PayloadManifest/2",
        "payload": "sbl",
        "round": "FHS_W0_R9_REPAIR_20261108",
        "generated_at": ts,
        "eol_policy": "LF (this repository asserts LF-clean blobs); sha256_round records the round bytes when they differed",
        "document_location": "FHS_PIPD-LS-PKG_W0_r9.md",
        "digest_scope": "every entry below resolves inside this directory; no entry refers to another payload",
        "files": entries,
        "non_claims": ["ORIGINAL_ACK", "NATIVE_WORLDRAW", "RELEASE_GRANTED", "INDEPENDENT_PASS"],
    }
    with open(os.path.join(sbl_root, "MANIFEST.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sbl_manifest, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    fentries = []
    for src, rel in FABRIC_FILES:
        dst = os.path.join(fabric_root, rel.replace("/", os.sep))
        rec = put(os.path.join(a.round, src), dst, normalise_lf=False)
        rec["path"] = rel
        fentries.append(rec)

    # The Fabric entry README says INTEGRATION/MANIFEST.json governs the mirror and "must not be
    # silently expanded". This path is therefore announced, not registered: the file below says so
    # in the payload, and registering it stays the Fabric Policy Owner's act.
    status_rel = "MIRROR_STATUS.md"
    status_text = (
        "# Mirror status — W0 r9\n\n"
        "This directory is a **non-authoritative candidate mirror** of the W0 r9 write-back.\n\n"
        "- `INTEGRATION/MANIFEST.json` is **not** modified by this change and does not list this path.\n"
        "- Registering it in the manifest is the Fabric Policy Owner's act, not the author's.\n"
        "- Until that happens this path is a candidate document under review, not a mirror entry, and\n"
        "  citing it grants no permission and no acceptance.\n"
        "- The authoritative W0 substance is the SBL payload at\n"
        "  `evidence/fhs-w0-r9-repair-20261108/` on the SBL candidate branch.\n\n"
        "Claim ceiling: `W0_SEVEN_DEFECTS_REPAIRED_WITH_SCOPED_OWNER_HOLDS`. Not an original-domain ACK,\n"
        "not a native world effect, not a release.\n"
    )
    status_path = os.path.join(fabric_root, status_rel)
    os.makedirs(fabric_root, exist_ok=True)
    with open(status_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(status_text)
    raw = status_text.encode("utf-8")
    fentries.append({"path": status_rel, "bytes": len(raw), "sha256": sha(raw)})
    fabric_manifest = {
        "schema": "FHS.W0.PayloadManifest/2",
        "payload": "fabric",
        "round": "FHS_W0_R9_REPAIR_20261108",
        "generated_at": ts,
        "eol_policy": "byte-identical (this repository has no LF invariant and the mirror must match the cited digest)",
        "document_location": "FHS_PIPD-LS-PKG_W0_r9.md",
        "digest_scope": "every entry below resolves inside this directory",
        "files": fentries,
        "non_claims": ["ORIGINAL_ACK", "NATIVE_WORLDRAW", "RELEASE_GRANTED", "INDEPENDENT_PASS"],
    }
    with open(os.path.join(fabric_root, "PROVENANCE.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fabric_manifest, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print(f"sbl   {len(entries)} files -> {sbl_root}")
    print(f"fabric {len(fentries)} files -> {fabric_root}")
    for e in entries:
        flag = " (LF)" if e.get("normalised_from_crlf") else ""
        print(f"  {e['bytes']:>8}  {e['sha256'][:16]}  {e['path']}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
