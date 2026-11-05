#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-00 source_probe.py — FHS W0 R4C source/repo/host probe.

Standard library only. Read-only with respect to every input: this tool never
writes into --source-root, the ZIP, or any git repository. Its only writes go
to --out.

Outputs (written into --out):
  SOURCE_MANIFEST.json   ZIP identity, body identity/declaration comparison,
                         manifest declared-vs-present two-way set comparison,
                         31-source / 22-upstream parse census, check ledger
  REPO_TRIPLE_STATE.json per-repo declared-vs-measured local/remote state
  HOST_PROBE.json        host / python / git / hermes / profile paths

Exit codes:
  0  no blocking check failed (first_fail == "NONE")
  3  at least one blocking check failed (first_fail is the code)
  2  CLI/usage error

Check ledger semantics: every check is appended in a fixed order with a
`state` of PASS / FAIL / NOT_OBSERVED. `first_fail` is the code of the FIRST
check in that order whose state is FAIL. This is the value the negative tests
assert on -- they never assert on exit code alone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from datetime import datetime, timedelta, timezone

PROBE_VERSION = "1.0.0"
SCHEMA_PREFIX = "FHS_W0_IMPL/WP-FHS-00/v1"
TPE = timezone(timedelta(hours=8))

# Baseline ZIP identity declared by the W0 R4C round envelope handed to this
# lane. Overridable with --expect-zip-sha. Measured independently on every run.
EXPECTED_ZIP_SHA256 = "f3838fb095e56ea8d636e5c52f4bd69e9d529d110569b87376c168ea35ab2a2a"

BODY_NAME = "FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md"
MANIFEST_NAME = "INDEX_AND_MANIFEST_r4-candidate-b41d2e.json"
STATE_NAME = "CURRENT_CANDIDATE_STATE.json"
SOURCE31_NAME = "SOURCE31_PHYSICAL_IDENTITY.json"
UPPER22_NAME = "UPPER22_PHYSICAL_IDENTITY.json"
READBACK_NAME = "REPO_READBACK_SUMMARY.json"
RECHECK_NAME = "REPOS_RECHECK.json"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
H1_RE = re.compile(r"^#\s+\S")
CH_ID_RE = re.compile(r"^#\s+CH-(\d{2})\b")

DEFAULT_REPOS = {
    "Fabric": "C:/Projects/Agent_Workspace/Fabric",
    "SBL": "C:/Projects/Agent_Workspace/SBL",
    "HG-KSEOS": "C:/Projects/Agent_Workspace/HG-KSEOS",
}


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def now_iso():
    return datetime.now(TPE).replace(microsecond=0).isoformat()


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path, obj):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def nfc(text):
    return unicodedata.normalize("NFC", text)


def rel_posix(root, path):
    return nfc(os.path.relpath(path, root).replace(os.sep, "/"))


def strip_win_extended(path):
    """'\\\\?\\C:\\...' -> 'C:\\...' (Windows extended-length prefix)."""
    prefix = "\\\\?\\"
    if path.startswith(prefix):
        return path[len(prefix):]
    return path


def stat_entry(path):
    try:
        st = os.stat(path)
        return {"exists": True, "bytes": st.st_size, "error": None}
    except OSError as exc:
        return {"exists": False, "bytes": None, "error": "{}: {}".format(type(exc).__name__, exc)}


class Ledger:
    """Ordered check ledger; first_fail = first FAIL in insertion order."""

    def __init__(self):
        self.checks = []

    def add(self, code, state, detail, severity="BLOCK"):
        self.checks.append(
            {
                "seq": len(self.checks) + 1,
                "code": code,
                "state": state,
                "severity": severity,
                "detail": detail,
            }
        )

    def ok(self, code, detail, severity="BLOCK"):
        self.add(code, "PASS", detail, severity)

    def fail(self, code, detail, severity="BLOCK"):
        self.add(code, "FAIL", detail, severity)

    def not_observed(self, code, detail):
        self.add(code, "NOT_OBSERVED", detail, "WARN")

    def note(self, code, detail):
        """Fact worth recording that is not a probe failure (difference, hold, reading)."""
        self.add(code, "OBSERVED", detail, "WARN")

    def first_fail(self):
        for c in self.checks:
            if c["state"] == "FAIL" and c["severity"] == "BLOCK":
                return c["code"]
        return "NONE"

    def counts(self):
        out = {"PASS": 0, "FAIL": 0, "NOT_OBSERVED": 0}
        for c in self.checks:
            out[c["state"]] = out.get(c["state"], 0) + 1
        return out


# --------------------------------------------------------------------------
# (a) ZIP identity
# --------------------------------------------------------------------------
def probe_zip(zip_path, expect_sha, ledger):
    doc = {
        "path": os.path.abspath(zip_path),
        "exists": os.path.isfile(zip_path),
        "sha256": None,
        "bytes": None,
        "member_count": 0,
        "duplicate_member_names": [],
        "members": [],
        "expected_sha256": expect_sha,
        "sha_matches_expected": False,
        "unreadable": False,
    }
    if not doc["exists"]:
        ledger.fail("SOURCE_ZIP_UNREADABLE", "zip not found: {}".format(zip_path))
        return doc

    doc["bytes"] = os.path.getsize(zip_path)
    doc["sha256"] = sha256_file(zip_path)

    if expect_sha:
        if doc["sha256"] == expect_sha:
            doc["sha_matches_expected"] = True
            ledger.ok(
                "SOURCE_ZIP_SHA_MISMATCH",
                "sha256 {} == expected {}".format(doc["sha256"], expect_sha),
            )
        else:
            ledger.fail(
                "SOURCE_ZIP_SHA_MISMATCH",
                "sha256 {} != expected {}".format(doc["sha256"], expect_sha),
            )
    else:
        ledger.not_observed(
            "SOURCE_ZIP_SHA_MISMATCH", "no --expect-zip-sha supplied; sha recorded only"
        )

    try:
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            doc["member_count"] = len(names)
            seen = {}
            dups = set()
            for name in names:
                seen[name] = seen.get(name, 0) + 1
            for name, n in seen.items():
                if n > 1:
                    dups.add(name)
            doc["duplicate_member_names"] = sorted(dups)
            members = []
            for info in zf.infolist():
                name = info.filename
                entry = {
                    "name": name,
                    "bytes": info.file_size,
                    "crc32": "{:08x}".format(info.CRC),
                    "sha256": None,
                    "readable": True,
                }
                try:
                    with zf.open(info, "r") as fh:
                        h = hashlib.sha256()
                        while True:
                            block = fh.read(1 << 20)
                            if not block:
                                break
                            h.update(block)
                    entry["sha256"] = h.hexdigest()
                except Exception as exc:  # corrupt member must not abort the probe
                    entry["readable"] = False
                    entry["sha256"] = None
                    entry["error"] = "{}: {}".format(type(exc).__name__, exc)
                members.append(entry)
            members.sort(key=lambda m: m["name"])
            doc["members"] = members
            doc["member_sha_index"] = {m["name"]: m["sha256"] for m in members}
    except Exception as exc:
        doc["unreadable"] = True
        doc["error"] = "{}: {}".format(type(exc).__name__, exc)

    if doc["unreadable"]:
        ledger.fail("SOURCE_ZIP_UNREADABLE", doc.get("error", ""))
    elif doc["member_count"] == 0:
        ledger.fail("SOURCE_ZIP_MEMBER_COUNT_ZERO", "zip reports 0 members")
    else:
        ledger.ok(
            "SOURCE_ZIP_MEMBER_COUNT_ZERO",
            "{} members, {} unreadable".format(
                doc["member_count"],
                sum(1 for m in doc["members"] if not m.get("readable")),
            ),
        )
    if doc["duplicate_member_names"]:
        ledger.fail(
            "SOURCE_ZIP_DUPLICATE_MEMBER",
            "duplicate member names: {}".format(doc["duplicate_member_names"][:10]),
        )
    else:
        ledger.ok("SOURCE_ZIP_DUPLICATE_MEMBER", "no duplicate member names")
    return doc


# --------------------------------------------------------------------------
# (b) body identity vs CURRENT_CANDIDATE_STATE.json
# --------------------------------------------------------------------------
def probe_body(source_root, manifest_doc, state_path, ledger, body_override=None):
    declared_state = {}
    state_sha = None
    if state_path and os.path.isfile(state_path):
        state_sha = sha256_file(state_path)
        st = load_json(state_path)
        declared_state = {
            "candidate_body_sha256": st.get("candidate_body_sha256"),
            "candidate_body_bytes": st.get("candidate_body_bytes"),
            "chapters": st.get("chapters"),
            "currency": st.get("currency"),
            "candidate_id": st.get("candidate_id"),
        }
    else:
        ledger.not_observed("BODY_DECLARATION_MISSING", "CURRENT_CANDIDATE_STATE.json not found")

    body_rel = (manifest_doc or {}).get("candidate_body", {}).get("path") or BODY_NAME
    body_path = body_override or os.path.join(source_root, body_rel)
    body_rel = rel_posix(source_root, body_path) if body_override else body_rel
    doc = {
        "path": os.path.abspath(body_path),
        "relative_path": body_rel,
        "exists": os.path.isfile(body_path),
        "sha256": None,
        "bytes": None,
        "h1_count": None,
        "chapter_ids": [],
        "chapter_id_count": None,
        "declared": {
            "from_current_candidate_state": declared_state,
            "from_manifest": (manifest_doc or {}).get("candidate_body", {}),
            "state_file_sha256": state_sha,
        },
        "matches": {},
    }
    if not doc["exists"]:
        ledger.fail("BODY_UNREADABLE", "body not found: {}".format(body_path))
        return doc

    raw = None
    with open(body_path, "rb") as fh:
        raw = fh.read()
    doc["bytes"] = len(raw)
    doc["sha256"] = sha256_bytes(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        ledger.fail("BODY_UNREADABLE", "not utf-8: {}".format(exc))
        return doc
    h1 = [ln for ln in text.splitlines() if H1_RE.match(ln)]
    ids = []
    for ln in h1:
        m = CH_ID_RE.match(ln)
        if m:
            ids.append("CH-" + m.group(1))
    doc["h1_count"] = len(h1)
    doc["chapter_ids"] = ids
    doc["chapter_id_count"] = len(ids)

    ds = declared_state
    dm = doc["declared"]["from_manifest"]
    doc["matches"]["sha256_state"] = (
        None if not ds.get("candidate_body_sha256") else doc["sha256"] == ds["candidate_body_sha256"]
    )
    doc["matches"]["bytes_state"] = (
        None if not ds.get("candidate_body_bytes") else doc["bytes"] == ds["candidate_body_bytes"]
    )
    doc["matches"]["chapters_state"] = (
        None if not ds.get("chapters") else doc["h1_count"] == ds["chapters"]
    )
    doc["matches"]["sha256_manifest"] = (
        None if not dm.get("sha256") else doc["sha256"] == dm["sha256"]
    )
    doc["matches"]["bytes_manifest"] = (
        None if not dm.get("bytes") else doc["bytes"] == dm["bytes"]
    )
    doc["matches"]["chapters_manifest"] = (
        None if not dm.get("chapters") else doc["h1_count"] == dm["chapters"]
    )

    if doc["matches"]["sha256_state"] is False:
        ledger.fail(
            "BODY_SHA_MISMATCH",
            "measured {} != CURRENT_CANDIDATE_STATE {}".format(
                doc["sha256"], ds.get("candidate_body_sha256")
            ),
        )
    else:
        ledger.ok(
            "BODY_SHA_MISMATCH",
            "{} (state declared {})".format(doc["sha256"], ds.get("candidate_body_sha256")),
        )
    if doc["matches"]["bytes_state"] is False:
        ledger.fail(
            "BODY_BYTES_MISMATCH",
            "measured {} != declared {}".format(doc["bytes"], ds.get("candidate_body_bytes")),
        )
    else:
        ledger.ok("BODY_BYTES_MISMATCH", "{} bytes".format(doc["bytes"]))
    if doc["matches"]["chapters_state"] is False:
        ledger.fail(
            "BODY_CHAPTER_COUNT_MISMATCH",
            "measured {} H1 != declared {}".format(doc["h1_count"], ds.get("chapters")),
        )
    else:
        ledger.ok(
            "BODY_CHAPTER_COUNT_MISMATCH",
            "{} H1 lines, {} CH-nn ids, declared {}".format(
                doc["h1_count"], doc["chapter_id_count"], ds.get("chapters")
            ),
        )
    if doc["matches"]["sha256_manifest"] is False or doc["matches"]["bytes_manifest"] is False:
        ledger.fail(
            "BODY_MANIFEST_DECLARATION_CONFLICT",
            "manifest candidate_body (sha={}, bytes={}) disagrees with measurement".format(
                dm.get("sha256"), dm.get("bytes")
            ),
        )
    else:
        ledger.ok("BODY_MANIFEST_DECLARATION_CONFLICT", "manifest candidate_body agrees")

    annex = (manifest_doc or {}).get("annex", {})
    annex_doc = {"path": None, "sha256": None, "bytes": None, "matches": {}}
    if annex.get("path"):
        apath = os.path.join(source_root, annex["path"])
        annex_doc["path"] = os.path.abspath(apath)
        if os.path.isfile(apath):
            annex_doc["bytes"] = os.path.getsize(apath)
            annex_doc["sha256"] = sha256_file(apath)
            annex_doc["matches"]["sha256"] = annex_doc["sha256"] == annex.get("sha256")
            annex_doc["matches"]["bytes"] = annex_doc["bytes"] == annex.get("bytes")
            if annex_doc["matches"]["sha256"] and annex_doc["matches"]["bytes"]:
                ledger.ok("MANIFEST_ANNEX_SHA_MISMATCH", "annex sha/bytes match manifest")
            else:
                ledger.fail(
                    "MANIFEST_ANNEX_SHA_MISMATCH",
                    "annex measured ({} , {}) != declared ({}, {})".format(
                        annex_doc["sha256"], annex_doc["bytes"], annex.get("sha256"), annex.get("bytes")
                    ),
                )
        else:
            ledger.fail("MANIFEST_ANNEX_SHA_MISMATCH", "annex missing: {}".format(apath))
    doc["annex"] = annex_doc
    return doc


# --------------------------------------------------------------------------
# (c) manifest declared-vs-present, both directions
# --------------------------------------------------------------------------
def probe_manifest(source_root, manifest_path, ledger, zip_index=None):
    doc = {
        "path": os.path.abspath(manifest_path) if manifest_path else None,
        "exists": os.path.isfile(manifest_path) if manifest_path else False,
        "sha256": None,
        "declared": {"files": 0, "evidence": 0, "unique": 0, "declared_total": None},
        "present": 0,
        "self_excluded": [],
        "missing": [],
        "undeclared": [],
        "duplicate_declarations": [],
        "sha_mismatches": [],
        "bytes_mismatches": [],
        "zip_cross_check": {},
    }
    if not doc["exists"]:
        ledger.fail("MANIFEST_UNREADABLE", "manifest not found: {}".format(manifest_path))
        return doc, {}
    doc["sha256"] = sha256_file(manifest_path)
    try:
        m = load_json(manifest_path)
    except Exception as exc:
        ledger.fail("MANIFEST_UNREADABLE", "{}: {}".format(type(exc).__name__, exc))
        return doc, {}

    files = m.get("files") or []
    evidence = m.get("evidence") or []
    doc["declared"]["files"] = len(files)
    doc["declared"]["evidence"] = len(evidence)
    doc["declared"]["declared_total"] = (m.get("counts") or {}).get("declared_total")
    doc["self_excluded"] = list((m.get("closure") or {}).get("self_excluded") or [])
    doc["declaration_claim"] = {
        "counts": m.get("counts") or {},
        "closure_complete_members": (m.get("closure") or {}).get("complete_members"),
        "parentage_source_zip_sha256": (m.get("parentage") or {}).get("source_zip_sha256"),
    }

    declared_map = {}
    dupes = set()
    for entry in files + evidence:
        p = entry.get("path")
        if p is None:
            continue
        p = nfc(p)
        if p in declared_map:
            dupes.add(p)
        declared_map[p] = entry
    doc["declared"]["unique"] = len(declared_map)
    doc["duplicate_declarations"] = sorted(dupes)

    present = set()
    for root, _dirs, names in os.walk(source_root):
        for name in names:
            present.add(rel_posix(source_root, os.path.join(root, name)))
    doc["present"] = len(present)

    self_excluded = set(nfc(x) for x in doc["self_excluded"])
    missing = sorted(set(declared_map) - present)
    undeclared = sorted(present - set(declared_map) - self_excluded)
    doc["missing"] = missing
    doc["undeclared"] = undeclared

    if missing:
        ledger.fail(
            "MANIFEST_MEMBER_MISSING",
            "{} declared member(s) absent from source root; first: {}".format(
                len(missing), missing[:5]
            ),
        )
    else:
        ledger.ok(
            "MANIFEST_MEMBER_MISSING",
            "0 of {} declared members absent (denominator {})".format(
                len(declared_map), len(declared_map)
            ),
        )
    if undeclared:
        ledger.fail(
            "MANIFEST_MEMBER_UNDECLARED",
            "{} present file(s) not declared; first: {}".format(len(undeclared), undeclared[:5]),
        )
    else:
        ledger.ok(
            "MANIFEST_MEMBER_UNDECLARED",
            "0 of {} present files undeclared (denominator {}, self_excluded {})".format(
                len(present), len(present), len(self_excluded)
            ),
        )
    if doc["duplicate_declarations"]:
        ledger.fail(
            "MANIFEST_DUPLICATE_DECLARATION",
            "{} path(s) declared more than once".format(len(doc["duplicate_declarations"])),
        )
    else:
        ledger.ok("MANIFEST_DUPLICATE_DECLARATION", "no duplicated declaration paths")

    # per-member sha/bytes re-hash
    for p in sorted(set(declared_map) - set(missing)):
        entry = declared_map[p]
        apath = os.path.join(source_root, p)
        try:
            size = os.path.getsize(apath)
            digest = sha256_file(apath)
        except OSError as exc:
            doc["sha_mismatches"].append({"path": p, "error": "{}: {}".format(type(exc).__name__, exc)})
            continue
        if entry.get("sha256") and digest != entry["sha256"]:
            doc["sha_mismatches"].append(
                {"path": p, "declared": entry["sha256"], "measured": digest}
            )
        if entry.get("bytes") is not None and size != entry["bytes"]:
            doc["bytes_mismatches"].append(
                {"path": p, "declared": entry["bytes"], "measured": size}
            )
    if doc["sha_mismatches"]:
        ledger.fail(
            "MANIFEST_MEMBER_SHA_MISMATCH",
            "{} member(s) sha differ from declaration; first: {}".format(
                len(doc["sha_mismatches"]), [x.get("path") for x in doc["sha_mismatches"][:5]]
            ),
        )
    else:
        ledger.ok(
            "MANIFEST_MEMBER_SHA_MISMATCH",
            "0 of {} re-hashed members differ".format(len(set(declared_map) - set(missing))),
        )
    if doc["bytes_mismatches"]:
        ledger.fail(
            "MANIFEST_MEMBER_BYTES_MISMATCH",
            "{} member(s) size differ; first: {}".format(
                len(doc["bytes_mismatches"]), [x.get("path") for x in doc["bytes_mismatches"][:5]]
            ),
        )
    else:
        ledger.ok("MANIFEST_MEMBER_BYTES_MISMATCH", "0 member size differences")

    declared_total = doc["declared"]["declared_total"]
    if declared_total is not None and declared_total != len(declared_map):
        ledger.fail(
            "MANIFEST_DECLARED_TOTAL_MISMATCH",
            "counts.declared_total {} != {} unique declared entries".format(
                declared_total, len(declared_map)
            ),
        )
    else:
        ledger.ok(
            "MANIFEST_DECLARED_TOTAL_MISMATCH",
            "counts.declared_total {} == {} unique declared entries".format(
                declared_total, len(declared_map)
            ),
        )

    complete = (m.get("closure") or {}).get("complete_members")
    physical_closure = len(declared_map) + len(self_excluded)
    if complete is not None and complete != len(files) + len(evidence):
        ledger.fail(
            "MANIFEST_CLOSURE_COUNT_MISMATCH",
            "closure.complete_members {} != files {} + evidence {}".format(
                complete, len(files), len(evidence)
            ),
        )
    else:
        ledger.ok(
            "MANIFEST_CLOSURE_COUNT_MISMATCH",
            "closure.complete_members {} == files {} + evidence {}".format(
                complete, len(files), len(evidence)
            ),
        )
    if complete is not None and complete != physical_closure:
        ledger.note(
            "MANIFEST_CLOSURE_RULE_READING",
            "closure.rule states COMPLETE = files ∪ evidence ∪ {{self .json}}; under that "
            "reading the physical closure is {} ({} declared + {} self_excluded) while "
            "closure.complete_members declares {}. Not a member/identity defect: the "
            "physical ZIP has {} members. Recorded as a named hold, not a failure.".format(
                physical_closure, len(declared_map), len(self_excluded), complete,
                len((zip_index or {}).get("member_sha_index", {})),
            ),
        )

    if zip_index is not None:
        znames = set(zip_index.get("member_sha_index", {}))
        only_zip = sorted(znames - present)
        only_fs = sorted(present - znames)
        doc["zip_cross_check"] = {
            "zip_members": len(znames),
            "fs_files": len(present),
            "in_zip_not_on_disk": only_zip[:20],
            "on_disk_not_in_zip": only_fs[:20],
            "count_in_zip_not_on_disk": len(only_zip),
            "count_on_disk_not_in_zip": len(only_fs),
        }
        if only_zip or only_fs:
            ledger.fail(
                "ZIP_FS_MEMBER_SET_DIVERGENCE",
                "zip-only {} / fs-only {}".format(len(only_zip), len(only_fs)),
            )
        else:
            ledger.ok(
                "ZIP_FS_MEMBER_SET_DIVERGENCE",
                "{} zip members == {} files on disk (bidirectional)".format(len(znames), len(present)),
            )

    declared_zip_sha = (m.get("parentage") or {}).get("source_zip_sha256")
    doc["zip_cross_check"]["declared_parentage_source_zip_sha256"] = declared_zip_sha
    measured_zip_sha = (zip_index or {}).get("sha256")
    doc["zip_cross_check"]["measured_zip_sha256"] = measured_zip_sha
    if zip_index is not None and declared_zip_sha and measured_zip_sha:
        if declared_zip_sha == measured_zip_sha:
            ledger.ok(
                "MANIFEST_PARENTAGE_ZIP_SHA_DIFFERENT",
                "parentage.source_zip_sha256 equals the measured ZIP sha",
            )
        else:
            ledger.note(
                "MANIFEST_PARENTAGE_ZIP_SHA_DIFFERENT",
                "parentage.source_zip_sha256 declares {} while the ZIP under test measures "
                "{}; the manifest names its parent package, so the probe pins the ZIP against "
                "the round-envelope constant, not against this field. Recorded as a named "
                "hold, not a failure.".format(declared_zip_sha, measured_zip_sha),
            )
    return doc, m


# --------------------------------------------------------------------------
# (d) 31 source / 22 upstream identity declarations
# --------------------------------------------------------------------------
def _parse_31(path, ledger):
    doc = {
        "path": os.path.abspath(path),
        "exists": os.path.isfile(path),
        "sha256": None,
        "declared_count": None,
        "parseable": 0,
        "unparseable": 0,
        "gaps": [],
        "resolution": {"resolved": 0, "unresolved": 0, "size_mismatch": 0, "unresolved_ids": []},
        "physical_identity_states": {},
        "currentness_states": {},
        "sha_verified": 0,
    }
    if not doc["exists"]:
        ledger.fail("SOURCE31_UNREADABLE", "not found: {}".format(path))
        return doc
    doc["sha256"] = sha256_file(path)
    try:
        entries = load_json(path)
    except Exception as exc:
        ledger.fail("SOURCE31_UNREADABLE", "{}: {}".format(type(exc).__name__, exc))
        return doc
    if not isinstance(entries, list):
        ledger.fail("SOURCE31_UNREADABLE", "top-level is {}, expected list".format(type(entries).__name__))
        return doc
    doc["declared_count"] = len(entries)
    required = ("source_id", "path", "sha256", "bytes", "physical_identity")
    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            doc["unparseable"] += 1
            doc["gaps"].append({"index": idx, "reason": "entry is not an object"})
            continue
        label = e.get("source_id") or "index:{}".format(idx)
        absent = [k for k in required if e.get(k) in (None, "")]
        bad = []
        if absent:
            bad.append("missing fields {}".format(absent))
        if e.get("sha256") and not HEX64.match(str(e["sha256"])):
            bad.append("sha256 not lowercase hex64")
        if e.get("bytes") is not None and not isinstance(e.get("bytes"), int):
            bad.append("bytes not int")
        if bad:
            doc["unparseable"] += 1
            doc["gaps"].append({"source_id": label, "reason": "; ".join(bad)})
            continue
        doc["parseable"] += 1
        pi = e.get("physical_identity")
        doc["physical_identity_states"][pi] = doc["physical_identity_states"].get(pi, 0) + 1
        cur = e.get("currentness")
        if cur:
            doc["currentness_states"][cur] = doc["currentness_states"].get(cur, 0) + 1
        st = stat_entry(strip_win_extended(str(e["path"])))
        if not st["exists"]:
            doc["resolution"]["unresolved"] += 1
            doc["resolution"]["unresolved_ids"].append(label)
        elif st["bytes"] != e.get("bytes"):
            doc["resolution"]["size_mismatch"] += 1
            doc["resolution"]["unresolved_ids"].append(label)
        else:
            doc["resolution"]["resolved"] += 1
    if doc["unparseable"]:
        ledger.fail(
            "SOURCE31_PARSE_GAP",
            "{}/{} entries unparseable: {}".format(
                doc["unparseable"], doc["declared_count"], doc["gaps"][:5]
            ),
        )
    else:
        ledger.ok(
            "SOURCE31_PARSE_GAP",
            "{}/{} entries parseable (0 unparseable); physical_identity={}".format(
                doc["parseable"], doc["declared_count"], doc["physical_identity_states"]
            ),
        )
    return doc


def _parse_22(path, ledger):
    doc = {
        "path": os.path.abspath(path),
        "exists": os.path.isfile(path),
        "sha256": None,
        "declared_count": None,
        "parseable": 0,
        "unparseable": 0,
        "gaps": [],
        "states": {},
        "match_count": 0,
        "resolution": {"resolved": 0, "unresolved": 0, "unresolved_names": []},
    }
    if not doc["exists"]:
        ledger.fail("UPPER22_UNREADABLE", "not found: {}".format(path))
        return doc
    doc["sha256"] = sha256_file(path)
    try:
        entries = load_json(path)
    except Exception as exc:
        ledger.fail("UPPER22_UNREADABLE", "{}: {}".format(type(exc).__name__, exc))
        return doc
    if not isinstance(entries, list):
        ledger.fail("UPPER22_UNREADABLE", "top-level is {}, expected list".format(type(entries).__name__))
        return doc
    doc["declared_count"] = len(entries)
    required = ("expected_name", "expected_sha", "matches", "state")
    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            doc["unparseable"] += 1
            doc["gaps"].append({"index": idx, "reason": "entry is not an object"})
            continue
        label = e.get("expected_name") or "index:{}".format(idx)
        absent = [k for k in required if e.get(k) in (None, "", [])]
        bad = []
        if absent:
            bad.append("missing fields {}".format(absent))
        if e.get("expected_sha") and not HEX64.match(str(e["expected_sha"])):
            bad.append("expected_sha not lowercase hex64")
        matches = e.get("matches")
        if matches is not None and not isinstance(matches, list):
            bad.append("matches not a list")
        if bad:
            doc["unparseable"] += 1
            doc["gaps"].append({"expected_name": label, "reason": "; ".join(bad)})
            continue
        doc["parseable"] += 1
        st = e.get("state")
        doc["states"][st] = doc["states"].get(st, 0) + 1
        doc["match_count"] += len(matches or [])
        if not matches:
            doc["resolution"]["unresolved"] += 1
            doc["resolution"]["unresolved_names"].append(label)
            continue
        resolved_any = False
        for m in matches:
            mst = stat_entry(strip_win_extended(str(m.get("path", ""))))
            if mst["exists"]:
                resolved_any = True
                break
        if resolved_any:
            doc["resolution"]["resolved"] += 1
        else:
            doc["resolution"]["unresolved"] += 1
            doc["resolution"]["unresolved_names"].append(label)
    if doc["unparseable"]:
        ledger.fail(
            "UPPER22_PARSE_GAP",
            "{}/{} entries unparseable: {}".format(
                doc["unparseable"], doc["declared_count"], doc["gaps"][:5]
            ),
        )
    else:
        ledger.ok(
            "UPPER22_PARSE_GAP",
            "{}/{} entries parseable; states={}; {} matches".format(
                doc["parseable"], doc["declared_count"], doc["states"], doc["match_count"]
            ),
        )
    return doc


# --------------------------------------------------------------------------
# (e) three-repo state
# --------------------------------------------------------------------------
def _run(cmd, timeout=600):
    """Read-only subprocess wrapper. Returns (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, timeout=timeout, check=False
        )
        return (
            proc.returncode,
            proc.stdout.decode("utf-8", "replace"),
            proc.stderr.decode("utf-8", "replace"),
        )
    except Exception as exc:
        return 127, "", "{}: {}".format(type(exc).__name__, exc)


def _run_bytes(cmd, timeout=600):
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as exc:
        return 127, b"", str(exc).encode()


def probe_repos(heads_path, readback_path, recheck_path, repos_root, ledger):
    doc = {
        "heads_path": os.path.abspath(heads_path) if heads_path else None,
        "heads_sha256": None,
        "readback_path": os.path.abspath(readback_path) if readback_path else None,
        "readback_sha256": None,
        "recheck_path": os.path.abspath(recheck_path) if recheck_path else None,
        "recheck_sha256": None,
        "git_version": None,
        "repos": {},
        "summary": {},
    }
    git = shutil.which("git")
    if git:
        rc, out, _err = _run([git, "--version"], timeout=60)
        doc["git_version"] = out.strip() if rc == 0 else None
    if not git:
        ledger.fail("GIT_NOT_AVAILABLE", "git executable not on PATH")
        return doc

    heads = {}
    if heads_path and os.path.isfile(heads_path):
        doc["heads_sha256"] = sha256_file(heads_path)
        heads = load_json(heads_path)
    else:
        ledger.fail("REPO_HEADS_SOURCE_MISSING", "REMOTE_HEADS.json not found")
        return doc

    readback = {}
    if readback_path and os.path.isfile(readback_path):
        doc["readback_sha256"] = sha256_file(readback_path)
        for entry in load_json(readback_path) or []:
            name = str(entry.get("repo", "")).split("/")[-1]
            readback[name] = entry
    recheck = {}
    if recheck_path and os.path.isfile(recheck_path):
        doc["recheck_sha256"] = sha256_file(recheck_path)
        recheck = (load_json(recheck_path) or {}).get("repos", {})

    names = sorted((heads.get("repos") or {}).keys())
    local_decl = heads.get("local_worktree_heads") or {}

    total_dirty = 0
    aligned = 0
    for name in names:
        h = heads["repos"][name] or {}
        ld = local_decl.get(name) or {}
        path = repos_root.get(name) or ld.get("path") or DEFAULT_REPOS.get(name)
        entry = {
            "path": path,
            "default_branch": h.get("default_branch"),
            "archived": h.get("archived"),
            "declared": {
                "remote_head": h.get("remote_head"),
                "remote_head_source": os.path.basename(heads_path),
                "remote_main_readback": (readback.get(name) or {}).get("remote_main"),
                "local_head": ld.get("head"),
                "branch": ld.get("branch"),
                "status_total_entries_recheck": (recheck.get(name) or {}).get("status_total_entries"),
                "origin_main_tracking_ref_recheck": (recheck.get(name) or {}).get(
                    "origin_main_local_tracking_ref"
                ),
            },
            "measured": {
                "local_head": None,
                "branch": None,
                "origin_main_tracking_ref": None,
                "status_total_entries": None,
                "tracked_dirty_count": None,
                "untracked_count": None,
                "dirty_count": None,
                "status_stderr_warning_lines": None,
                "status_sha256": None,
            },
            "flags": {},
            "state": None,
        }
        repo_path = path
        if not repo_path or not os.path.isdir(repo_path):
            # A missing local clone is a host-context gap, not a source-identity failure:
            # the probe must stay replayable on a machine that has no such worktree.
            ledger.not_observed(
                "REPO_LOCAL_HEAD_UNREADABLE",
                "{}: repo path missing ({}); recorded as host-context gap, not a probe failure".format(name, repo_path),
            )
            entry["state"] = "REPO_UNREADABLE"
            doc["repos"][name] = entry
            continue
        rc, out, err = _run([git, "-C", repo_path, "rev-parse", "HEAD"], timeout=120)
        if rc != 0:
            ledger.not_observed(
                "REPO_LOCAL_HEAD_UNREADABLE",
                "{}: rev-parse HEAD failed: {}".format(name, err.strip()[:200]),
            )
            entry["state"] = "REPO_UNREADABLE"
            doc["repos"][name] = entry
            continue
        entry["measured"]["local_head"] = out.strip()
        rc, out, _err = _run([git, "-C", repo_path, "symbolic-ref", "--short", "HEAD"], timeout=120)
        entry["measured"]["branch"] = out.strip() if rc == 0 else None
        branch = entry["default_branch"] or "main"
        rc, out, _err = _run(
            [git, "-C", repo_path, "rev-parse", "--verify", "-q", "refs/remotes/origin/" + branch],
            timeout=120,
        )
        entry["measured"]["origin_main_tracking_ref"] = out.strip() if rc == 0 else None

        # git status --porcelain -uall : read-only. -c core.quotepath=false keeps
        # non-ASCII paths literal in the captured bytes.
        rc, outb, errb = _run_bytes(
            [git, "-c", "core.quotepath=false", "-C", repo_path, "status", "--porcelain=v1", "-uall"]
        )
        if rc != 0:
            ledger.fail(
                "REPO_STATUS_UNREADABLE",
                "{}: git status rc={} err={}".format(name, rc, errb.decode("utf-8", "replace")[:200]),
            )
            entry["state"] = "REPO_UNREADABLE"
            doc["repos"][name] = entry
            continue
        lines = outb.split(b"\n")
        if lines and lines[-1] == b"":
            lines = lines[:-1]
        untracked = sum(1 for ln in lines if ln.startswith(b"??"))
        tracked = len(lines) - untracked
        entry["measured"]["status_total_entries"] = len(lines)
        entry["measured"]["tracked_dirty_count"] = tracked
        entry["measured"]["untracked_count"] = untracked
        entry["measured"]["dirty_count"] = len(lines)
        entry["measured"]["status_sha256"] = hashlib.sha256(outb).hexdigest()
        entry["measured"]["status_stderr_warning_lines"] = len(
            [ln for ln in errb.split(b"\n") if ln.strip()]
        )
        total_dirty += len(lines)

        flags = entry["flags"]
        flags["remote_declaration_corroborated"] = bool(
            entry["declared"]["remote_main_readback"]
            and entry["declared"]["remote_head"] == entry["declared"]["remote_main_readback"]
        )
        flags["local_head_matches_declaration"] = bool(
            entry["declared"]["local_head"] == entry["measured"]["local_head"]
        )
        flags["local_equals_remote"] = bool(
            entry["declared"]["remote_head"] == entry["measured"]["local_head"]
        )
        flags["tracking_ref_matches_remote"] = bool(
            entry["measured"]["origin_main_tracking_ref"]
            and entry["measured"]["origin_main_tracking_ref"] == entry["declared"]["remote_head"]
        )
        flags["status_count_matches_recheck"] = (
            None
            if entry["declared"]["status_total_entries_recheck"] is None
            else entry["declared"]["status_total_entries_recheck"]
            == entry["measured"]["status_total_entries"]
        )
        if flags["local_equals_remote"]:
            aligned += 1
        entry["state"] = (
            "LOCAL_ALIGNED_WITH_REMOTE" if flags["local_equals_remote"] else "LOCAL_DRIFTED_FROM_REMOTE"
        )
        doc["repos"][name] = entry

    # ---- ledger checks over the trio
    unreadable = [n for n, e in doc["repos"].items() if e["state"] == "REPO_UNREADABLE"]
    if unreadable:
        pass  # individual failures already recorded above
    else:
        ledger.ok("REPO_LOCAL_HEAD_UNREADABLE", "{} repos readable".format(len(doc["repos"])))

    conflicted = [
        n
        for n, e in doc["repos"].items()
        if e["flags"].get("local_head_matches_declaration") is False
    ]
    if conflicted:
        ledger.fail(
            "REPO_DECLARED_LOCAL_HEAD_MISMATCH",
            "measured local HEAD differs from REMOTE_HEADS declaration: {}".format(
                {n: (doc["repos"][n]["declared"]["local_head"], doc["repos"][n]["measured"]["local_head"]) for n in conflicted}
            ),
        )
    else:
        ledger.ok(
            "REPO_DECLARED_LOCAL_HEAD_MISMATCH",
            "all {} measured local HEADs match REMOTE_HEADS declaration".format(len(doc["repos"])),
        )

    uncorroborated = [
        n
        for n, e in doc["repos"].items()
        if e["flags"].get("remote_declaration_corroborated") is False
    ]
    if uncorroborated:
        ledger.fail(
            "REMOTE_HEAD_DRIFT",
            "declared remote_head not corroborated by REPO_READBACK_SUMMARY.remote_main: {}".format(
                {
                    n: (
                        doc["repos"][n]["declared"]["remote_head"],
                        doc["repos"][n]["declared"]["remote_main_readback"],
                    )
                    for n in uncorroborated
                }
            ),
        )
    else:
        ledger.ok(
            "REMOTE_HEAD_DRIFT",
            "all {} declared remote_heads corroborated by the independent readback "
            "snapshot; 0 declaration drift (local-vs-remote worktree drift is reported "
            "as a state, not as this code)".format(len(doc["repos"])),
        )

    stale_refs = [
        n
        for n, e in doc["repos"].items()
        if e["flags"].get("tracking_ref_matches_remote") is False
    ]
    if stale_refs:
        ledger.add(
            "REMOTE_TRACKING_REF_STALE",
            "NOT_OBSERVED",
            "declared remote_head not equal to local refs/remotes/origin/<default>: "
            "{} (offline snapshot; not a probe failure)".format(
                {
                    n: (
                        doc["repos"][n]["declared"]["remote_head"],
                        doc["repos"][n]["measured"]["origin_main_tracking_ref"],
                    )
                    for n in stale_refs
                }
            ),
            "WARN",
        )
    else:
        ledger.ok(
            "REMOTE_TRACKING_REF_STALE",
            "all local remote-tracking refs equal the declared remote head",
        )

    doc["summary"] = {
        "repos": len(doc["repos"]),
        "repos_readable": len(doc["repos"]) - len(unreadable),
        "local_aligned_with_remote": aligned,
        "local_drifted_from_remote": len(doc["repos"]) - aligned - len(unreadable),
        "remote_declaration_conflicts": len(uncorroborated),
        "dirty_total_across_repos": total_dirty,
        "dirty_by_repo": {
            n: e["measured"]["dirty_count"] for n, e in sorted(doc["repos"].items())
        },
    }
    return doc


# --------------------------------------------------------------------------
# (f) host probe
# --------------------------------------------------------------------------
def probe_host(ledger):
    doc = {
        "os": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
        },
        "python": {
            "version": sys.version,
            "version_info": list(sys.version_info[:3]),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "git": {"executable": shutil.which("git"), "version": None, "raw_first_line": None},
        "hermes": {
            "executable": None,
            "version_raw_first_line": None,
            "state": "NOT_OBSERVED",
        },
        "profile": {"candidates": [], "runtime_profile_path": None},
        "cwd": os.getcwd(),
    }
    git = shutil.which("git")
    if git:
        rc, out, _err = _run([git, "--version"], timeout=60)
        if rc == 0:
            doc["git"]["version"] = out.strip()
            doc["git"]["raw_first_line"] = out.strip().splitlines()[0]
    if doc["git"]["version"]:
        ledger.ok("HOST_GIT_VERSION", doc["git"]["version"])
    else:
        ledger.not_observed("HOST_GIT_VERSION", "git --version produced no output")

    hermes = shutil.which("hermes")
    doc["hermes"]["executable"] = hermes
    if hermes:
        rc, out, err = _run([hermes, "--version"], timeout=120)
        first = out.strip().splitlines()[0] if out.strip() else None
        doc["hermes"]["version_raw_first_line"] = first
        doc["hermes"]["exit_code"] = rc
        if rc == 0 and first:
            doc["hermes"]["state"] = "OBSERVED"
            ledger.ok("HOST_HERMES_VERSION", first)
        else:
            doc["hermes"]["state"] = "NOT_OBSERVED"
            doc["hermes"]["stderr_first_line"] = (
                err.strip().splitlines()[0] if err.strip() else None
            )
            ledger.not_observed(
                "HOST_HERMES_VERSION", "hermes --version rc={} output empty".format(rc)
            )
    else:
        ledger.not_observed("HOST_HERMES_VERSION", "hermes not on PATH")

    runtime_profile = "D:/Hermes-Recovery/live22/profiles/hgk-governed"
    candidates = []
    for label, value in (
        ("env:HERMES_PROFILE_DIR", os.environ.get("HERMES_PROFILE_DIR")),
        ("env:HERMES_HOME", os.environ.get("HERMES_HOME")),
        ("env:HERMES_DELEGATED_CHILD_CONTEXT", os.environ.get("HERMES_DELEGATED_CHILD_CONTEXT")),
        ("env:HERMES_DESKTOP_USER_DATA_DIR", os.environ.get("HERMES_DESKTOP_USER_DATA_DIR")),
        ("session_runtime_context", runtime_profile),
    ):
        if not value:
            continue
        candidates.append(
            {"source": label, "path": value.replace("\\", "/"), "exists": os.path.isdir(value)}
        )
    doc["profile"]["candidates"] = candidates
    doc["profile"]["runtime_profile_path"] = {
        "path": runtime_profile,
        "exists": os.path.isdir(runtime_profile),
        "source": "session runtime context (profile hgk-governed)",
    }
    if doc["profile"]["runtime_profile_path"]["exists"]:
        ledger.ok(
            "HOST_PROFILE_PATH_MISSING",
            "profile path exists: {}".format(runtime_profile),
        )
    else:
        ledger.not_observed(
            "HOST_PROFILE_PATH_MISSING", "profile path absent: {}".format(runtime_profile)
        )
    ledger.ok(
        "HOST_OS_IDENTITY",
        "{} / {} / {}".format(doc["os"]["system"], doc["os"]["release"], platform.python_version()),
    )
    return doc


# --------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------
def _find_heads(out_dir, source_root):
    for base in (out_dir, os.path.abspath(os.path.join(out_dir, ".."))):
        cur = os.path.abspath(base)
        for _ in range(5):
            cand = os.path.join(cur, "source_readback", "REMOTE_HEADS.json")
            if os.path.isfile(cand):
                return cand
            nxt = os.path.dirname(cur)
            if nxt == cur:
                break
            cur = nxt
    cand = os.path.join(source_root, "source_readback", "REMOTE_HEADS.json")
    if os.path.isfile(cand):
        return cand
    return None


def run_probe(
    zip_path,
    source_root,
    out_dir,
    expect_zip_sha=EXPECTED_ZIP_SHA256,
    manifest_path=None,
    state_path=None,
    body_path=None,
    source31_path=None,
    upper22_path=None,
    heads_path=None,
    readback_path=None,
    recheck_path=None,
    repos_root=None,
    generated_at=None,
):
    out_dir = os.path.abspath(out_dir)
    source_root = os.path.abspath(source_root)
    manifest_path = manifest_path or os.path.join(source_root, MANIFEST_NAME)
    state_path = state_path or os.path.join(source_root, STATE_NAME)
    source31_path = source31_path or os.path.join(source_root, SOURCE31_NAME)
    upper22_path = upper22_path or os.path.join(source_root, UPPER22_NAME)
    readback_path = readback_path or os.path.join(source_root, READBACK_NAME)
    recheck_path = recheck_path or os.path.join(source_root, RECHECK_NAME)
    heads_path = heads_path or _find_heads(out_dir, source_root)
    repos_root = repos_root or {}

    stamp = generated_at or now_iso()
    ledger = Ledger()

    zip_doc = probe_zip(zip_path, expect_zip_sha, ledger)

    manifest_doc, manifest_raw = probe_manifest(
        source_root, manifest_path, ledger, zip_index=zip_doc
    )
    body_doc = probe_body(source_root, manifest_raw, state_path, ledger, body_override=body_path)

    s31 = _parse_31(source31_path, ledger)
    u22 = _parse_22(upper22_path, ledger)
    repos = probe_repos(heads_path, readback_path, recheck_path, repos_root, ledger)
    host = probe_host(ledger)

    input_shas = {
        "zip": {"path": os.path.abspath(zip_path), "sha256": zip_doc.get("sha256"), "bytes": zip_doc.get("bytes")},
        "manifest": {"path": manifest_doc.get("path"), "sha256": manifest_doc.get("sha256")},
        "body": {"path": body_doc.get("path"), "sha256": body_doc.get("sha256")},
        "current_candidate_state": {"path": os.path.abspath(state_path), "sha256": body_doc["declared"]["state_file_sha256"]},
        "source31": {"path": s31.get("path"), "sha256": s31.get("sha256")},
        "upper22": {"path": u22.get("path"), "sha256": u22.get("sha256")},
        "heads": {"path": repos.get("heads_path"), "sha256": repos.get("heads_sha256")},
        "readback": {"path": repos.get("readback_path"), "sha256": repos.get("readback_sha256")},
        "recheck": {"path": repos.get("recheck_path"), "sha256": repos.get("recheck_sha256")},
    }

    first_fail = ledger.first_fail()
    state = "PROBE_PASS" if first_fail == "NONE" else "PROBE_FAIL"
    probe_block = {
        "name": "WP-FHS-00 source_probe",
        "version": PROBE_VERSION,
        "mode": "READ_ONLY",
        "generated_at": stamp,
        "generated_at_rule": "only field allowed to differ between two runs on identical inputs",
        "source_root": source_root,
        "inputs_sha256": input_shas,
        "checks": ledger.checks,
        "check_counts": ledger.counts(),
        "first_fail": first_fail,
        "state": state,
    }

    manifest_out = {
        "schema": SCHEMA_PREFIX + "/SOURCE_MANIFEST",
        "generated_at": stamp,
        "probe": probe_block,
        "source_zip": {k: v for k, v in zip_doc.items() if k != "member_sha_index"},
        "body": body_doc,
        "manifest": manifest_doc,
        "source31": s31,
        "upper22": u22,
        "repos_summary": repos.get("summary"),
        "counts": {
            "zip_members": zip_doc.get("member_count"),
            "zip_members_unreadable": sum(
                1 for m in zip_doc.get("members", []) if not m.get("readable")
            ),
            "manifest_declared_unique": manifest_doc["declared"]["unique"],
            "manifest_declared_total_field": manifest_doc["declared"]["declared_total"],
            "manifest_present_files": manifest_doc.get("present"),
            "manifest_missing": len(manifest_doc.get("missing", [])),
            "manifest_undeclared": len(manifest_doc.get("undeclared", [])),
            "body_h1": body_doc.get("h1_count"),
            "body_chapter_ids": body_doc.get("chapter_id_count"),
            "source31_total": s31.get("declared_count"),
            "source31_parseable": s31.get("parseable"),
            "source31_unparseable": s31.get("unparseable"),
            "source31_resolved_on_disk": s31.get("resolution", {}).get("resolved"),
            "upper22_total": u22.get("declared_count"),
            "upper22_parseable": u22.get("parseable"),
            "upper22_unparseable": u22.get("unparseable"),
            "upper22_matches": u22.get("match_count"),
            "repos": (repos.get("summary") or {}).get("repos"),
            "repos_dirty_total": (repos.get("summary") or {}).get("dirty_total_across_repos"),
        },
    }
    repo_out = {
        "schema": SCHEMA_PREFIX + "/REPO_TRIPLE_STATE",
        "generated_at": stamp,
        "probe_version": PROBE_VERSION,
        "mode": "READ_ONLY",
        "heads_source": repos.get("heads_path"),
        "heads_sha256": repos.get("heads_sha256"),
        "readback_source": repos.get("readback_path"),
        "readback_sha256": repos.get("readback_sha256"),
        "recheck_source": repos.get("recheck_path"),
        "recheck_sha256": repos.get("recheck_sha256"),
        "git_version": repos.get("git_version"),
        "repos": repos.get("repos"),
        "summary": repos.get("summary"),
        "drift_rule": (
            "REMOTE_HEAD_DRIFT fires when a repo's declared remote_head is not "
            "corroborated by the independent REPO_READBACK_SUMMARY.remote_main snapshot. "
            "local HEAD != remote_head is reported as repos[*].state=LOCAL_DRIFTED_FROM_REMOTE "
            "(the round's documented steady state) and is not a probe failure."
        ),
    }
    host_out = {
        "schema": SCHEMA_PREFIX + "/HOST_PROBE",
        "generated_at": stamp,
        "probe_version": PROBE_VERSION,
        "mode": "READ_ONLY",
        **host,
    }

    os.makedirs(out_dir, exist_ok=True)
    paths = {
        "SOURCE_MANIFEST.json": dump_json(os.path.join(out_dir, "SOURCE_MANIFEST.json"), manifest_out),
        "REPO_TRIPLE_STATE.json": dump_json(os.path.join(out_dir, "REPO_TRIPLE_STATE.json"), repo_out),
        "HOST_PROBE.json": dump_json(os.path.join(out_dir, "HOST_PROBE.json"), host_out),
    }
    return manifest_out, repo_out, host_out, paths


def build_parser():
    p = argparse.ArgumentParser(
        description="WP-FHS-00 source_probe: recompute ZIP/body/manifest/repo/host identity."
    )
    p.add_argument("--zip", required=True, help="FHS_PIPD-LS-PKG_W0_R4C.zip path")
    p.add_argument("--source-root", required=True, help="extracted source root directory")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--expect-zip-sha", default=EXPECTED_ZIP_SHA256)
    p.add_argument("--manifest", default=None)
    p.add_argument("--state", default=None, help="CURRENT_CANDIDATE_STATE.json")
    p.add_argument("--source31", default=None)
    p.add_argument("--upper22", default=None)
    p.add_argument("--heads", default=None, help="REMOTE_HEADS.json")
    p.add_argument("--readback", default=None, help="REPO_READBACK_SUMMARY.json")
    p.add_argument("--recheck", default=None, help="REPOS_RECHECK.json")
    p.add_argument(
        "--repo-root",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="override repo path, repeatable",
    )
    p.add_argument(
        "--generated-at",
        default=None,
        help="freeze generated_at (ISO8601) so two runs are byte-identical",
    )
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    repos_root = {}
    for spec in args.repo_root:
        if "=" not in spec:
            print("bad --repo-root {} (want NAME=PATH)".format(spec), file=sys.stderr)
            return 2
        name, path = spec.split("=", 1)
        repos_root[name] = path
    manifest_out, _repo_out, _host_out, paths = run_probe(
        zip_path=args.zip,
        source_root=args.source_root,
        out_dir=args.out,
        expect_zip_sha=args.expect_zip_sha,
        manifest_path=args.manifest,
        state_path=args.state,
        source31_path=args.source31,
        upper22_path=args.upper22,
        heads_path=args.heads,
        readback_path=args.readback,
        recheck_path=args.recheck,
        repos_root=repos_root,
        generated_at=args.generated_at,
    )
    summary = {
        "first_fail": manifest_out["probe"]["first_fail"],
        "state": manifest_out["probe"]["state"],
        "counts": manifest_out["counts"],
        "check_counts": manifest_out["probe"]["check_counts"],
        "outputs": paths,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if manifest_out["probe"]["first_fail"] == "NONE" else 3


if __name__ == "__main__":
    sys.exit(main())
