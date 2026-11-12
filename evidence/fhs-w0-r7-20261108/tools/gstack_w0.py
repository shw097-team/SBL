#!/usr/bin/env python3
"""GSTACK invariant gate for the FHS W0 r6 completion round.

The gate does not trust any lane's own verifier. It re-reads every artifact the
lanes declare, recomputes every digest, re-slices every cited source span from
the original bytes, and re-checks the counts against the tables themselves.

Exit codes
  0  every check PASS (or PASS_EMPTY for a check whose input is legitimately empty)
  1  at least one FAIL
  2  fail closed: a precondition is absent (no lane reports, or the source tree
     is missing). The gate must be runnable while it can only fail, otherwise the
     first green run proves only that it tolerates missing input.

Usage
  python gstack_w0.py --round <round dir> --json <out.json> [--expect-wp WP01 ...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

SOURCES = r"C:\Projects\Agent_Workspace\FHS_W1_Work_Final\FHS_W1_Work_Final\sources"
REPOS = {
    "Fabric": r"C:\Projects\Agent_Workspace\worktrees\r4-fabric",
    "SBL": r"C:\Projects\Agent_Workspace\worktrees\r4-sbl",
    "HG-KSEOS": r"C:\Projects\Agent_Workspace\worktrees\r4-hgk",
}
ALLOWED_CEILINGS = {
    "AUTHOR_SIDE_SNAPSHOT_VERIFIED",
    "AUTHOR_SIDE_SOURCE_BOUND",
    "AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND",
    "AUTHOR_SIDE_PROJECTION_CANDIDATE",
    "SOURCE_READ_INVENTORY_ONLY",
    "AUTHOR_SIDE_ORACLE_PLAN_SOURCE_BOUND",
    "DOCUMENT_RECONCILIATION_COMPLETE_WITH_SCOPED_HOLDS",
}
FORBIDDEN_SUFFIX = {".db", ".sqlite", ".sqlite3", ".zip", ".enc", ".key", ".p12", ".pfx"}
SECRET_PAT = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
# A bare claim of a ceiling the round does not hold. Exempt lines that negate it or
# define it with an iff/definitional marker.
BARE_CLAIM = re.compile(r"(?<![\"'])\b(ORIGINAL_ACK|NATIVE_WORLDRAW|RELEASE_GRANTED|INDEPENDENT_PASS)\b")
CLAIM_EXEMPT = ("不主張", "不宣稱", "不聲明", "不是", "未達", "NOT_OBSERVED", "not_claimed",
                "claim_ceiling", "iff", "=false", "≠", "非", "禁止", "denied", "NOT_RUN",
                "無任何", "cannot", "不得")

results: list[dict] = []


def check(cid: str, status: str, detail, **extra):
    results.append({"id": cid, "status": status, "detail": detail, **extra})


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root: str):
    """Walk without following junctions or symlinks; a junction fixture must not
    make the gate scan a target outside the round."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        keep = []
        for d in dirnames:
            full = os.path.join(dirpath, d)
            if os.path.islink(full) or (hasattr(os.path, "isjunction") and os.path.isjunction(full)):
                continue
            if d == "__pycache__":
                continue
            keep.append(d)
        dirnames[:] = keep
        for f in filenames:
            full = os.path.join(dirpath, f)
            if os.path.islink(full):
                continue
            yield full


def load(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# Documents a lane may legitimately cite that are not one of the 31 sources: the
# control document itself and its retained parent. They are resolved by exact
# name so a span into the control text is checkable rather than unresolvable.
CONTROL_DOCS = {
    "FHS_PIPD-LS-PKG_W0_r6.md": r"C:\Projects\Agent_Workspace\FHS_W0W2_R4_20261107\writeback\W0\FHS_PIPD-LS-PKG_W0_r6.md",
    "FHS_PIPD-LS-PKG_W0_r5.md": r"C:\Projects\Agent_Workspace\FHS_W0W2_R4_20261107\evidence\E_docs\FHS_PIPD-LS-PKG_W0_r5.md",
}


def resolve_source(name: str, idmap: dict | None = None):
    base = os.path.basename(str(name))
    if base in CONTROL_DOCS and os.path.isfile(CONTROL_DOCS[base]):
        return CONTROL_DOCS[base]
    cand = os.path.join(SOURCES, base)
    if os.path.isfile(cand):
        return cand
    if idmap and str(name) in idmap:
        cand = os.path.join(SOURCES, os.path.basename(idmap[str(name)]))
        if os.path.isfile(cand):
            return cand
    return None


def iter_source_refs(obj, path="$"):
    """Yield (json_path, ref) for every dict that looks like a source reference."""
    if isinstance(obj, dict):
        if "byte_start" in obj and "byte_end" in obj and ("file" in obj or "source_id" in obj):
            yield path, obj
        for k, v in obj.items():
            yield from iter_source_refs(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_source_refs(v, f"{path}[{i}]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--expect-wp", nargs="*", default=["WP01", "WP15", "WP16", "WP19", "WP21"])
    args = ap.parse_args()
    R = args.round

    # ---- G0 preconditions (fail closed) -------------------------------------
    if not os.path.isdir(SOURCES):
        check("G0-SOURCES", "FAIL", f"source tree absent: {SOURCES}")
        return emit(args, 2)
    n_src = len([f for f in os.listdir(SOURCES) if f.lower().endswith(".md")])
    check("G0-SOURCES", "PASS" if n_src == 31 else "FAIL",
          f"{n_src} source files present (expected 31)")

    reports = {}
    for wp in args.expect_wp:
        p = os.path.join(R, "evidence", wp, "REPORT.json")
        if os.path.isfile(p):
            try:
                reports[wp] = load(p)
            except Exception as e:  # noqa: BLE001
                check(f"G1-{wp}", "FAIL", f"REPORT.json unparsable: {e}")
                continue
            check(f"G1-{wp}", "PASS", f"report present, schema={reports[wp].get('schema')}")
        else:
            check(f"G1-{wp}", "FAIL", f"missing {p}")
    if not reports:
        return emit(args, 2)

    # ---- G2 declared artifacts exist with the declared digest ---------------
    # A report may not hash itself; every other row must carry a real digest.
    HEX = re.compile(r"^[0-9a-f]{64}$")
    bad = []
    checked = 0
    self_rows = 0
    for wp, rep in reports.items():
        for art in rep.get("artifacts", []):
            rel = art.get("path", "")
            base = os.path.basename(rel)
            if base == "REPORT.json":
                self_rows += 1
                continue
            cands = [rel if os.path.isabs(rel) else os.path.join(R, rel)]
            if not os.path.isabs(rel):
                cands.append(os.path.join(R, "evidence", wp, rel))
            cand = next((c for c in cands if os.path.isfile(c)), None)
            if cand is None:
                bad.append(f"{wp}: absent {rel}")
                continue
            checked += 1
            digest = str(art.get("sha256") or "")
            if not HEX.match(digest):
                bad.append(f"{wp}: {rel} carries a placeholder digest, not a sha256")
            elif sha256(cand) != digest:
                bad.append(f"{wp}: digest drift {rel}")
            if art.get("bytes") not in (None, 0) and os.path.getsize(cand) != art["bytes"]:
                bad.append(f"{wp}: size drift {rel}")
    check("G2-ARTIFACT-DIGEST", "PASS" if not bad else "FAIL",
          f"{checked} declared artifacts re-hashed ({self_rows} self rows skipped, "
          f"a report cannot hash itself); {len(bad)} problem(s)", problems=bad[:20])

    # ---- G3 deliverable hygiene --------------------------------------------
    hygiene = []
    for full in walk(R):
        size = os.path.getsize(full)
        ext = os.path.splitext(full)[1].lower()
        if ext in FORBIDDEN_SUFFIX:
            hygiene.append(f"forbidden artifact type: {full}")
        if size > 2 * 1024 * 1024:
            rel = os.path.relpath(full, R).replace("\\", "/")
            if "/raw/" not in rel:
                hygiene.append(f"oversize outside raw/: {rel} {size}")
    check("G3-HYGIENE", "PASS" if not hygiene else "FAIL",
          f"no forbidden types, no oversize outside raw/; {len(hygiene)} problem(s)",
          problems=hygiene[:20])

    # ---- G4 secret material -------------------------------------------------
    secrets = []
    for full in walk(R):
        if os.path.getsize(full) > 3 * 1024 * 1024:
            continue
        try:
            txt = open(full, "r", encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if SECRET_PAT.search(txt):
            secrets.append(os.path.relpath(full, R))
    check("G4-NO-SECRETS", "PASS" if not secrets else "FAIL",
          f"{len(secrets)} file(s) carry token or private-key shapes", problems=secrets)

    # ---- G5 claim ceiling vocabulary ---------------------------------------
    ceil_bad, bare = [], []
    for wp, rep in reports.items():
        c = rep.get("claim_ceiling")
        if c not in ALLOWED_CEILINGS:
            ceil_bad.append(f"{wp}: claim_ceiling={c!r} not in the allowed vocabulary")
        declared = set(rep.get("not_claimed", []) or [])
        for md in [p for p in walk(os.path.join(R, "evidence", wp)) if p.endswith(".md")]:
            for i, line in enumerate(open(md, encoding="utf-8", errors="ignore"), 1):
                if BARE_CLAIM.search(line) and not any(x in line for x in CLAIM_EXEMPT):
                    bare.append(f"{os.path.relpath(md, R)}:{i}: {line.strip()[:110]}")
    check("G5-CLAIM-CEILING", "PASS" if not ceil_bad else "FAIL",
          f"ceilings declared by {len(reports)} lane(s); {len(ceil_bad)} outside the vocabulary",
          problems=ceil_bad)
    check("G5b-NO-BARE-CLAIM", "PASS" if not bare else "FAIL",
          f"{len(bare)} bare ceiling claim(s) in prose", problems=bare[:20])

    # ---- G6 independent source-span resolution -----------------------------
    # SourceIDs (FHS-BODY-02) and filenames (02_PIPD_LIFECYCLE_AND_TPM(4).md) are
    # both legitimate references; the WP-00 lock carries the mapping, so the gate
    # resolves which is which instead of accepting only one shape.
    idmap = {}
    lock_p = os.path.join(R, "evidence/WP00/raw/SOURCE_LOCK.json")
    if os.path.isfile(lock_p):
        for row in load(lock_p)["sources"]:
            idmap[row["source_id"]] = row["file"]

    refs, span_bad, ref_files = 0, [], 0
    for wp in reports:
        for p in walk(os.path.join(R, "evidence", wp)):
            if not p.endswith(".json"):
                continue
            try:
                doc = load(p)
            except Exception:  # noqa: BLE001
                continue
            ref_files += 1
            for jpath, ref in iter_source_refs(doc):
                name = ref.get("file") or ref.get("source_id") or ""
                src = resolve_source(str(name), idmap)
                refs += 1
                if src is None:
                    span_bad.append(f"{os.path.basename(p)}{jpath}: unresolved file {name!r}")
                    continue
                try:
                    a, b = int(ref["byte_start"]), int(ref["byte_end"])
                except Exception:  # noqa: BLE001
                    span_bad.append(f"{os.path.basename(p)}{jpath}: non-integer span")
                    continue
                raw = open(src, "rb").read()
                if not (0 <= a < b <= len(raw)):
                    span_bad.append(f"{os.path.basename(p)}{jpath}: span {a}:{b} outside {len(raw)}")
                    continue
                q = ref.get("quoted_text")
                if q is None:
                    continue
                if raw[a:b].decode("utf-8", "replace") != q:
                    span_bad.append(f"{os.path.basename(p)}{jpath}: quote != bytes")
    check("G6-SPAN-RESOLUTION", "PASS" if not span_bad else "FAIL",
          f"{refs} source refs re-sliced from original bytes across {ref_files} json files; "
          f"{len(span_bad)} mismatch(es)", problems=span_bad[:20])

    # ---- G7 count reconciliation against the tables themselves -------------
    # Reports name the same quantity differently (counts.ac15 vs ac15_count vs a
    # nested measured block). Resolve by alias over the flattened document rather
    # than demanding one spelling.
    rec = []
    def count(path):
        d = load(path)
        if isinstance(d, list):
            return len(d)
        for k in ("records", "rows", "cells", "items", "entries"):
            if isinstance(d.get(k), list):
                return len(d[k])
        return None

    def flat(o, prefix=""):
        out = {}
        if isinstance(o, dict):
            for k, v in o.items():
                out.update(flat(v, f"{prefix}{k}."))
        elif isinstance(o, list):
            out[prefix.rstrip(".")] = len(o)
        else:
            out[prefix.rstrip(".")] = o
        return out

    ALIASES = {
        "donor_slots_found": ("donor_slots_found", "donor_slots", "donor24", "donor"),
        "method_slots_found": ("method_slots_found", "method_slots", "method25", "method"),
        "ac15_count": ("ac15_count", "ac15"),
        "oracle96_count": ("oracle96_count", "oracle96", "oracle_96"),
    }

    def lookup(rep, metric):
        f = flat(rep)
        for key in ALIASES[metric]:
            for k, v in f.items():
                if k.split(".")[-1] == key and isinstance(v, (int, float)):
                    return int(v), k
        return None, None

    expect = {
        "WP16": [("evidence/WP16/tables/DONOR24.json", "donor_slots_found"),
                 ("evidence/WP16/tables/METHOD25.json", "method_slots_found")],
        "WP21": [("evidence/WP21/tables/AC15.json", "ac15_count"),
                 ("evidence/WP21/tables/ORACLE96.json", "oracle96_count")],
    }
    for wp, pairs in expect.items():
        rep = reports.get(wp)
        if not rep:
            continue
        for rel, key in pairs:
            full = os.path.join(R, rel)
            if not os.path.isfile(full):
                rec.append(f"{wp}: table absent {rel}")
                continue
            n = count(full)
            claimed, where = lookup(rep, key)
            if claimed is None:
                rec.append(f"{wp}: {key} not declared in report")
            elif n != claimed:
                rec.append(f"{wp}: {rel} holds {n} records, report declares {claimed} ({where})")
    check("G7-COUNT-RECONCILIATION", "PASS" if not rec else "FAIL",
          f"{len(rec)} reconciliation problem(s)", problems=rec)

    # ---- G8 the repos are untouched ---------------------------------------
    base_p = os.path.join(R, "evidence/WP00/raw/SOURCE_LOCK.json")
    repo_bad = []
    if os.path.isfile(base_p):
        base = {r["repo"]: r for r in load(base_p)["repositories"]}
        import subprocess
        for name, path in REPOS.items():
            head = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
            dirty = len([p for p in subprocess.run(["git", "-C", path, "status", "--porcelain"],
                                                   capture_output=True, text=True).stdout.splitlines() if p.strip()])
            b = base.get(name, {})
            if head != b.get("head"):
                repo_bad.append(f"{name}: HEAD moved {b.get('head','?')[:10]} -> {head[:10]}")
            if dirty > b.get("dirty_paths", 0):
                repo_bad.append(f"{name}: dirty paths {b.get('dirty_paths')} -> {dirty}")
        check("G8-REPOS-UNTOUCHED", "PASS" if not repo_bad else "FAIL",
              f"3 repos compared against the WP-00 baseline; {len(repo_bad)} drift(s)",
              problems=repo_bad)
    else:
        check("G8-REPOS-UNTOUCHED", "FAIL", "WP-00 baseline absent, cannot compare")

    # ---- G9 WP-00 source lock itself --------------------------------------
    if os.path.isfile(base_p):
        lock = load(base_p)
        ok = lock["counts"]["match"] == 31 and all(u["verdict"] == "MATCH" for u in lock["upper_documents"])
        check("G9-WP00-SOURCELOCK", "PASS" if ok else "FAIL",
              f"sources {lock['counts']['match']}/31, upper docs "
              f"{sum(1 for u in lock['upper_documents'] if u['verdict']=='MATCH')}/{len(lock['upper_documents'])}")
    else:
        check("G9-WP00-SOURCELOCK", "FAIL", "SOURCE_LOCK.json absent")

    failed = [r for r in results if r["status"] == "FAIL"]
    return emit(args, 1 if failed else 0)


def emit(args, code: int) -> int:
    doc = {
        "schema": "FHS.GSTACK.W0/1",
        "round": os.path.basename(os.path.abspath(args.round)),
        "verdict": {0: "PASS", 1: "FAIL", 2: "FAIL_CLOSED_PRECONDITION"}[code],
        "exit_code": code,
        "checks_total": len(results),
        "checks_pass": sum(1 for r in results if r["status"] == "PASS"),
        "checks_fail": sum(1 for r in results if r["status"] == "FAIL"),
        "checks": results,
        "note": ("the gate re-derives every digest and every source span from the original "
                 "bytes; it does not read a lane's own verdict as evidence"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
    with open(args.json, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    for r in results:
        print(f"[{r['status']:4}] {r['id']:24} {r['detail']}")
        for p in (r.get("problems") or [])[:5]:
            print(f"        - {p}")
    print(f"\nVERDICT {doc['verdict']}  pass={doc['checks_pass']} fail={doc['checks_fail']} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
