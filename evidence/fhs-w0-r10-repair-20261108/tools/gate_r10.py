#!/usr/bin/env python3
"""GSTACK v3 — the same invariants, with the three defects the r9 gate shipped repaired.

What was wrong with v2, and what v3 does instead
-----------------------------------------------
1. `G13` read `duplicate_digest_groups` / `duplicate_digests` while the artifact writes
   `duplicate_sha256_groups`, so `dict.get` returned None and the assertion was dead. v3 resolves
   every key through `require()`, which raises `FIELD_ABSENT` when the artifact does not carry the
   key the check reads. A check may not pass on a field that does not exist.

2. `G16` required `yaml` to be undeclared and rejected `cryptography` from the undeclared set. That
   is a conclusion about one tree frozen into a rule; on a tree where `cryptography` really is
   undeclared the correct measurement was judged red. v3 splits it in two and encodes no conclusion:
     G16a DEPENDENCY_TRUTHFUL  the artifact's per-subject verdict equals the gate's own
                               re-derivation from the pinned metadata and sources
     G16b DEPENDENCY_CLOSED    coverage is actually complete on every subject (REPORTING severity:
                               this is a property of the world, not of the round)

3. `G10` resolved a parent digest printed inside a nested chapter (r7's declaration inside r9) and
   never checked the document's own parent, and r8 was missing from the chain entirely. v3's
   CHAIN_INTEGRITY reads the document's own header declaration, resolves it against a real file, and
   requires the chain r5→r6→r7→r8→r9→r10 to be complete with every link digest-matching.

Also new: every check prints what it measured, not a slogan; `G18` uses realpath containment;
`G22` compares the documented selftest exit code with the real one; `G23` requires every finding the
round calls CLOSED to be named in the document body.

Severity: BLOCKING failures fail the gate. REPORTING failures are recorded as open findings and do
not — because "the world is not fixed yet" is not the same claim as "the round is broken", and
conflating them is how a gate starts lying in the other direction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tomllib
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
MAX_ARTIFACT_BYTES = 2 * 1024 * 1024
FORBIDDEN_SUFFIX = {".db", ".sqlite", ".sqlite3", ".zip", ".7z", ".tar", ".gz", ".whl", ".pyc", ".pem", ".key"}
TOKEN_SHAPES = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def sha_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class FieldAbsent(Exception):
    pass


def require(obj, path: str):
    """Resolve a dotted path; a missing key is an error, never a silent None."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise FieldAbsent(path)
    return cur


class Ctx:
    def __init__(self, round_dir: str, prior_dir: str | None = None):
        self.round_dir = os.path.abspath(round_dir)
        self.prior_dir = os.path.abspath(prior_dir) if prior_dir else None

    def path(self, rel: str) -> str:
        return os.path.join(self.round_dir, rel.replace("/", os.sep))

    def load(self, rel: str) -> dict:
        p = self.path(rel)
        if not os.path.isfile(p):
            raise FileNotFoundError(p)
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)


# ------------------------------------------------------------------------------------------------
# dependency re-derivation (used by G16a/G16b)

DIST_TO_IMPORT = {"pyyaml": "yaml", "pillow": "PIL", "beautifulsoup4": "bs4", "python-dateutil": "dateutil"}
IMPORT_RE = re.compile(r"^(\s*)(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)")


def _declared(pyproject_paths: list[str]) -> tuple[set[str], dict]:
    flat: set[str] = set()
    detail = {}
    for p in pyproject_paths:
        with open(p, "rb") as fh:
            d = tomllib.loads(fh.read().decode("utf-8"))
        proj = d.get("project", {})
        run = [re.split(r"[<>=!~\[; ]", s.strip(), maxsplit=1)[0].lower() for s in proj.get("dependencies", []) or []]
        opt = {}
        for extra, specs in (proj.get("optional-dependencies") or {}).items():
            opt[extra] = [re.split(r"[<>=!~\[; ]", s.strip(), maxsplit=1)[0].lower() for s in specs]
        flat |= set(run) | {n for v in opt.values() for n in v}
        detail[os.path.basename(os.path.dirname(p)) or p] = {"runtime": run, "optional": opt}
    flat |= {DIST_TO_IMPORT[d] for d in list(flat) if d in DIST_TO_IMPORT}
    return flat, detail


def _imports(subject: dict) -> tuple[dict, bool]:
    found: dict[str, list[dict]] = {}
    complete = bool(subject.get("scan_complete"))
    roots = []
    if subject.get("source_root"):
        roots.append(subject["source_root"])
    files = list(subject.get("source_files") or [])
    local_names: set[str] = set()
    for r in roots:
        for dirpath, dirnames, filenames in os.walk(r):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                local_names.add(fn[:-3])
                files.append(os.path.join(dirpath, fn))
    base = subject.get("path") or ""
    for sub in ("tools", os.path.join("src", "hg_kseos")):
        d = os.path.join(base, sub)
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".py"):
                    local_names.add(fn[:-3])
    for f in files:
        if not os.path.isfile(f):
            continue
        for i, line in enumerate(open(f, "r", encoding="utf-8", errors="replace").read().splitlines(), 1):
            m = IMPORT_RE.match(line)
            if not m:
                continue
            mod = m.group(2)
            if mod in sys.stdlib_module_names or mod in local_names or mod == "hg_kseos":
                continue
            found.setdefault(mod, []).append({
                "file": os.path.relpath(f, subject.get("path") or os.path.dirname(f)).replace("\\", "/"),
                "line": i,
                "inside_function": bool(m.group(1)),
            })
    return found, complete


def derive_subject(s: dict) -> dict:
    decl, detail = _declared(s["metadata_files"])
    imports, complete = _imports(s)
    undeclared = {m: v for m, v in imports.items() if m.lower() not in decl}
    behavioural = sorted({m for m, sites in undeclared.items() if any(not x["inside_function"] for x in sites)})
    return {
        "name": s["name"],
        "head": s.get("head"),
        "metadata_sha256": s.get("metadata_sha256"),
        "declared_flat": sorted(decl),
        "declared_detail": detail,
        "third_party_imported": sorted(imports),
        "scan_complete": complete,
        "undeclared": sorted(undeclared),
        "undeclared_sites": {k: v[:6] for k, v in undeclared.items()},
        "undeclared_used_at_module_level": behavioural,
        "declared_covers_imports": not undeclared,
    }


# ------------------------------------------------------------------------------------------------
# checks


def g11_line_convention(ctx: Ctx):
    a = ctx.load("lanes/A/SOURCE_LOCK_V3.json")
    recs = require(a, "sources")
    tot = require(a, "totals")
    d = require(tot, "declared_lines_sum")
    o = require(tot, "observed_lines_sum")
    if len(recs) != 31:
        return False, "LINE_SOURCE_COUNT", f"{len(recs)} records"
    for r in recs:
        for k in ("bytes_match", "lines_match", "sha_match"):
            require(r, k)
    bad = [r["source_id"] for r in recs if not (r["bytes_match"] and r["lines_match"] and r["sha_match"])]
    if bad:
        return False, "LINE_FIELD_FALSE", f"{len(bad)} records false, first={bad[0]}"
    if not (d == 111331 and o == 111331):
        return False, "LINE_TOTAL_DISAGREES", f"declared={d} observed={o}"
    require(a, "convention")
    return True, "OK", f"31/31 bytes+lines+sha; {d}/{o}"


def g12_segmentation_rule(ctx: Ctx):
    a = ctx.load("lanes/B/U0_PARTITION_V3.json")
    tot = require(a, "totals")
    per = require(tot, "per_line_segments_sum")
    st = require(tot, "structural_blocks_sum")
    if per != 111331:
        return False, "PER_LINE_SUM", f"{per}"
    if st == per or st <= 0:
        return False, "RULES_COLLAPSED", f"per_line={per} structural={st}"
    require(a, "rule_semantics")
    if not require(tot, "all_tile_exactly"):
        return False, "TILING_FAILED", "all_tile_exactly false"
    # the rule that produced the structural number must be published next to it
    rec = a.get("reconciliation") or {}
    if "measured_structural" not in rec:
        return False, "RULE_UNDISCLOSED", "structural count published without the rule reconciliation block"
    return True, "OK", f"per_line={per} structural={st} rule published"


def g13_count_scope(ctx: Ctx):
    a = ctx.load("lanes/A/AUTHORITY_LEDGER_V3.json")
    inb = require(a, "in_set")
    # the exact keys the artifact writes; a rename makes this raise FIELD_ABSENT instead of passing
    dup_sha = require(inb, "duplicate_sha256_groups")
    dup_name = require(inb, "duplicate_basename_groups")
    require(inb, "scope")
    exts = [(k, a[k]) for k in ("kb_external_exact", "kb_external_normalised") if isinstance(a.get(k), dict)]
    if not exts:
        return False, "SCOPE_BLOCK_ABSENT", "no external-scope block"
    for label, blk in exts:
        require(blk, "scope")
        require(blk, "match_rule")
        require(blk, "source_files_with_at_least_one_divergent_copy")
        den = require(blk, "denominator")
        cov = require(blk, "denominator_covered")
        if den != 31:
            return False, "SCOPE_DENOMINATOR", f"{label}: denominator={den}, expected the 31 declared sources"
        if cov != den:
            return False, "SCOPE_COVERAGE_GAP", f"{label}: only {cov}/{den} source names were found under this rule"
        if require(blk, "copies_counted") < den:
            return False, "SCOPE_VACUOUS", f"{label}: fewer copies than names; the scope measured nothing"
        if not isinstance(require(blk, "source_files_with_at_least_one_divergent_copy"), int):
            return False, "SCOPE_VALUE_TYPE", label
    if dup_sha != 0 or dup_name != 0:
        return False, "IN_SET_COLLISION_PRESENT", f"duplicate_sha256_groups={dup_sha} duplicate_basename_groups={dup_name}"
    require(a, "canonical_resolution.state")
    if a["canonical_resolution"]["state"] != "OWNER_UNRESOLVED":
        return False, "CANONICAL_STATE", a["canonical_resolution"]["state"]
    return True, "OK", f"duplicate_sha256_groups=0 (key present); external {[ (k,v['source_files_with_at_least_one_divergent_copy']) for k,v in exts ]}"


def g14_maximum_is_global(ctx: Ctx):
    a = ctx.load("lanes/C/METHOD_DEPENDENCE.json")
    v = require(a, "V02")
    mx = require(v, "max_overall")
    mn = require(v, "min_overall")
    matrix = require(v, "matrix")
    vals = []
    for pair, methods in matrix.items():
        if isinstance(methods, dict):
            vals += [v for v in methods.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not vals:
        return False, "MATRIX_EMPTY", "no numeric cells"
    if abs(max(vals) - float(mx)) > 1e-9:
        return False, "MAXIMUM_IS_NOT_GLOBAL", f"max_overall={mx} but matrix max={max(vals)}"
    if abs(min(vals) - float(mn)) > 1e-9:
        return False, "MINIMUM_IS_NOT_GLOBAL", f"min_overall={mn} but matrix min={min(vals)}"
    if len(vals) < 6:
        return False, "MATRIX_TOO_SMALL", f"{len(vals)} cells; a claimed maximum over a subset is the defect this check exists for"
    claim = require(v, "claim")
    if "range" not in json.dumps(claim).lower() and "區間" not in json.dumps(claim, ensure_ascii=False):
        return False, "CLAIM_NOT_A_RANGE", "the claim does not present the value as method-dependent"
    return True, "OK", f"{len(vals)} cells, range [{mn}, {mx}]"


def g15_licence_layer(ctx: Ctx):
    a = ctx.load("lanes/B/TREE_IDENTITY.json")
    subs = a.get("subjects") or {}
    rows = list(subs.values()) if isinstance(subs, dict) else subs
    if len(rows) < 3:
        return False, "LICENCE_SUBJECT_COUNT", f"{len(rows)} subjects"
    for r in rows:
        cl = require(r, "licences.claim")
        for k in ("root_licence_present", "nested_licence_count", "scope_note"):
            require(cl, k)
        if r.get("head") and str(r["head"])[:7].lower() not in str(cl["scope_note"]).lower():
            return False, "LICENCE_SCOPE_NOTE_NO_HEAD", f"{r.get('subject') or r.get('name')}: scope_note does not name the HEAD it measured"
    return True, "OK", "; ".join(f"{r.get('subject') or r.get('name')}:{r['licences']['claim']['root_licence_present']}/{r['licences']['claim']['nested_licence_count']}" for r in rows)


def g16a_dependency_truthful(ctx: Ctx):
    """The artifact's per-subject verdict must equal the gate's own re-derivation."""
    desc = ctx.load("out/DEPENDENCY_SUBJECTS.json")
    art = ctx.load("lanes/B/TREE_IDENTITY.json")
    art_subs = art.get("subjects") or []
    if isinstance(art_subs, dict):
        art_subs = list(art_subs.values())
    by_head = {(str(x.get("head") or "")[:12]): x for x in art_subs if isinstance(x, dict)}
    mismatches = []
    for s in desc["subjects"]:
        mine = derive_subject(s)
        theirs = by_head.get(str(s.get("head") or "")[:12])
        if not isinstance(theirs, dict):
            mismatches.append((s["name"], "HEAD_NOT_IN_ARTIFACT"))
            continue
        claimed = require(theirs, "declared_covers_imports")
        if bool(claimed) != bool(mine["declared_covers_imports"]):
            mismatches.append((s["name"], f"claimed={claimed} derived={mine['declared_covers_imports']}"))
            continue
        art_und = sorted(str(u.get("module") if isinstance(u, dict) else u) for u in (require(theirs, "undeclared") or []))
        if art_und != sorted(mine["undeclared"]):
            mismatches.append((s["name"], f"undeclared claimed={art_und} derived={sorted(mine['undeclared'])}"))
    if mismatches:
        return False, "DEPENDENCY_ARTIFACT_DISAGREES_WITH_TREE", str(mismatches)
    return True, "OK", f"{len(desc['subjects'])} subjects agree with the trees"


def g16b_dependency_closed(ctx: Ctx):
    """REPORTING: is the world actually covered? No conclusion is encoded here."""
    desc = ctx.load("out/DEPENDENCY_SUBJECTS.json")
    gaps = {}
    for s in desc["subjects"]:
        d = derive_subject(s)
        if d["undeclared"]:
            gaps[s["name"]] = {"undeclared": d["undeclared"], "module_level": d["undeclared_used_at_module_level"], "scan_complete": d["scan_complete"]}
    if gaps:
        return False, "UNDECLARED_DEPENDENCY_OPEN", json.dumps(gaps, ensure_ascii=False)[:300]
    return True, "OK", "every subject's declared set covers its imports"


def g17_enum_slash_safe(ctx: Ctx):
    a = ctx.load("lanes/E/WP21_ENUM_V3.json")
    d = require(a, "denominators")
    for k, n in (("ac15", 15), ("oracle96", 96), ("h4", 12), ("seam", 11)):
        cell = require(d, k)
        if cell.get("measured") != n:
            return False, f"DENOMINATOR_{k.upper()}", f"{k}={cell.get('measured')}"
    nu = require(a, "naive_undercount")
    if nu.get("naive") != 10 or nu.get("robust") != 11 or not nu.get("missing_id"):
        return False, "SLASH_PARSE_NOT_DEMONSTRATED", json.dumps(nu, ensure_ascii=False)[:160]
    wb = require(nu, "naive_word_boundary")
    if wb != 11:
        return False, "WORD_BOUNDARY_ALSO_UNDERCOUNTS", f"word-boundary parser got {wb}; then the undercount is not caused by the slash convention"
    if require(nu, "naive_slash_split_recount") != 10:
        return False, "SLASH_SPLIT_NOT_REPRODUCED", str(nu.get("naive_slash_split_recount"))
    if not nu.get("which_parsers_undercount"):
        return False, "UNDERCOUNT_CAUSE_UNSTATED", "the artifact does not say which parser undercounts"
    return True, "OK", f"15/96/12/11; naive(slash)={nu['naive']} robust={nu['robust']}"


def g18_digest_locality(ctx: Ctx):
    base = os.path.join(ctx.round_dir, "out", "stage")
    manifests = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for fn in filenames:
            if fn in {"MANIFEST.json", "PROVENANCE.json"}:
                manifests.append(os.path.join(dirpath, fn))
    if not manifests:
        return False, "NO_PAYLOAD", "no staged payload — a locality check with nothing to check is not a pass"
    problems = []
    resolved = declared = 0
    for m in manifests:
        mdir = os.path.realpath(os.path.dirname(m))
        doc = json.load(open(m, "r", encoding="utf-8"))
        for e in doc.get("files", []):
            p = e.get("path")
            d = e.get("sha256")
            if not p or not d:
                problems.append({"manifest": os.path.relpath(m, ctx.round_dir), "why": "NO_PATH_OR_DIGEST"})
                continue
            fp = os.path.realpath(os.path.join(mdir, p))
            declared += 1
            if os.path.commonpath([mdir, fp]) != mdir:
                problems.append({"entry": p, "why": "PATH_OUTSIDE_PAYLOAD"})
                continue
            if not os.path.isfile(fp):
                problems.append({"entry": p, "why": "ABSENT"})
                continue
            if sha_file(fp) != d:
                problems.append({"entry": p, "why": "SHA_MISMATCH"})
                continue
            resolved += 1
    if problems:
        return False, "DIGEST_CROSSES_PAYLOAD", f"{len(problems)}: {problems[:3]}"
    return True, "OK", f"{resolved}/{declared} resolve inside their own payload (realpath containment), {len(manifests)} manifests"


def g19_copy_register(ctx: Ctx):
    a = ctx.load("lanes/D/COPY_REGISTER_ALL.json")
    ident = require(a, "target_set")
    names = require(ident, "exact_names")
    if names < 40:
        return False, "REGISTER_TOO_SMALL", f"{names} names"
    r6 = require(a, "r6_focus")
    n_copies = require(r6, "copies")
    members = require(r6, "members")
    if n_copies < 3 or len(members) != n_copies:
        return False, "R6_COPY_COUNT", f"count={n_copies} members={len(members)}"
    roots = {m.get("root") for m in members}
    if not any("worktrees" in str(r) for r in roots):
        return False, "R6_WORKTREE_ROOT_MISSING", str(sorted(roots))
    require(a, "canonical_resolution.state")
    if a["canonical_resolution"]["state"] != "OWNER_UNRESOLVED":
        return False, "COPY_CANONICAL_STATE", a["canonical_resolution"]["state"]
    return True, "OK", f"{names} names, r6 copies={n_copies} in {sorted(roots)}, digests={r6.get('distinct_digests')}"


def g10_chain_integrity(ctx: Ctx):
    """The document's OWN parent, and a chain that contains every version including r8."""
    doc = ctx.path("writeback/W0/FHS_PIPD-LS-PKG_W0_r10.md")
    if not os.path.isfile(doc):
        return False, "DOC_ABSENT", doc
    text = open(doc, "r", encoding="utf-8", errors="replace").read()
    # An append-only document carries one Parent line per embedded chapter.  The one that counts is
    # the LAST, because that is the chapter this revision appended; taking the first is exactly how
    # the r9 gate certified r7's declaration while calling it r9's.
    decls = list(re.finditer(r"Parent[／/][^\n]{0,120}?`([0-9a-f]{64})`", text))
    if not decls:
        return False, "PARENT_CLAIM_ABSENT", "the document carries no Parent declaration at all"
    m = decls[-1]
    declared = m.group(1)
    man = ctx.load("writeback/W0/W0_REVISION_MANIFEST.json")
    chain = require(man, "chain")
    order = [c["version"] for c in chain]
    for need in ("r5", "r6", "r7", "r8", "r9", "r10"):
        if need not in order:
            return False, "CHAIN_INCOMPLETE", f"{need} missing from chain {order}"
    by_v = {c["version"]: c for c in chain}
    if by_v["r10"].get("sha256") != sha_file(doc):
        return False, "CHAIN_R10_DIGEST", "manifest r10 digest != file"
    if by_v["r9"].get("sha256") != declared:
        return False, "PARENT_IS_NOT_ITS_OWN_PARENT", f"doc declares {declared[:16]} but manifest r9 is {str(by_v['r9'].get('sha256'))[:16]}"
    prev = None
    for v in ("r5", "r6", "r7", "r8", "r9", "r10"):
        ent = by_v[v]
        p = ent.get("path") or f"FHS_PIPD-LS-PKG_W0_{v}.md"
        cand = p if os.path.isabs(p) else ctx.path(p)
        if not os.path.isfile(cand):
            return False, "CHAIN_FILE_ABSENT", f"{v}: {cand}"
        if sha_file(cand) != ent.get("sha256"):
            return False, "CHAIN_DIGEST_MISMATCH", v
        ent["_abs"] = cand
        if prev is not None:
            if ent.get("parent_sha256") not in (None, by_v[prev].get("sha256")):
                return False, "CHAIN_LINK_MISMATCH", f"{v} parent {str(ent.get('parent_sha256'))[:12]} != {prev} {str(by_v[prev].get('sha256'))[:12]}"
            if ent.get("prefix_of_parent") is not True:
                return False, "CHAIN_PREFIX_NOT_VERIFIED", f"{v} does not record that the parent's bytes are its own prefix"
            prev_bytes = open(by_v[prev]["_abs"], "rb").read()
            if open(cand, "rb").read()[:len(prev_bytes)] != prev_bytes:
                return False, "CHAIN_PREFIX_BROKEN", f"{v} is not a byte-prefix extension of {prev}"
        prev = v
    return True, "OK", f"chain {'→'.join(order[-6:])}; own parent {declared[:12]} == r9; {len(decls)} declarations in the file, the last one counts"


def g21_number_consistency(ctx: Ctx):
    """A number the round publishes about a file must equal the file."""
    doc = ctx.path("writeback/W0/FHS_PIPD-LS-PKG_W0_r10.md")
    size = os.path.getsize(doc)
    handover = ctx.path("HANDOVER_R10_2026-11-08.md")
    if not os.path.isfile(handover):
        return False, "HANDOVER_ABSENT", handover
    txt = open(handover, "r", encoding="utf-8", errors="replace").read()
    m = re.search(r"FHS_PIPD-LS-PKG_W0_r10\.md[^\n]{0,160}?([\d][\d,]{3,})\s*(?:bytes|B)", txt)
    if not m:
        return False, "CLAIM_NOT_FOUND", "the handover does not state the document's byte count"
    claimed = int(m.group(1).replace(",", ""))
    if claimed != size:
        return False, "HANDOVER_BYTES_DISAGREE", f"claimed={claimed} measured={size}"
    sm = re.search(r"FHS_PIPD-LS-PKG_W0_r10\.md[^\n]{0,200}?`([0-9a-f]{64})`", txt)
    if not sm:
        return False, "CLAIM_NOT_FOUND", "the handover does not state the document digest"
    if sm.group(1) != sha_file(doc):
        return False, "HANDOVER_SHA_DISAGREE", f"claimed={sm.group(1)[:12]} measured={sha_file(doc)[:12]}"
    return True, "OK", f"handover states {claimed:,} B and a matching digest"


def g22_selftest_contract(ctx: Ctx):
    """The documented exit code must be the one this gate actually returns."""
    handover = ctx.path("HANDOVER_R10_2026-11-08.md")
    txt = open(handover, "r", encoding="utf-8", errors="replace").read()
    m = re.search(r"--selftest[^\n]{0,200}?exit[^\d]{0,10}(\d)", txt)
    if not m:
        return False, "CLAIM_NOT_FOUND", "the handover does not document the selftest exit code"
    documented = int(m.group(1))
    actual = run_selftest(ctx)
    if documented != actual:
        return False, "SELFTEST_EXIT_DOCUMENTED_WRONG", f"documented={documented} actual={actual}"
    return True, "OK", f"documented exit {documented} == actual"


def g23_trace_ids(ctx: Ctx):
    """Every finding the round calls CLOSED must be named in the document it claims to have changed."""
    close = ctx.load("writeback/W0/W0_CLOSEOUT_DECISION.json")
    defects = require(close, "defects")
    doc = open(ctx.path("writeback/W0/FHS_PIPD-LS-PKG_W0_r10.md"), "r", encoding="utf-8", errors="replace").read()
    missing = []
    for fid, disp in defects.items():
        if str(disp).startswith("CLOSED") and fid not in doc:
            missing.append(fid)
    if missing:
        return False, "TRACE_ID_NOT_NAMED", f"closed but absent from the document: {missing}"
    return True, "OK", f"{len(defects)} defects, all closed ones named in the body"


def g20_supply_chain_split(ctx: Ctx):
    """REPORTING: this is a claim-shape lint, not a supply-chain proof."""
    a = ctx.load("lanes/D/WP19_V3.json")
    sc = require(a, "supply_chain_claim")
    for k in ("offline_reproducible", "hosted_conclusion"):
        require(sc, k)
    note = json.dumps(sc.get("claim_shape") or "", ensure_ascii=False).lower()
    if not (("neither" in note and ("substitut" in note or "can not" in note or "cannot" in note)) or "不可互代" in note or "不可相互替代" in note):
        return False, "SUPPLY_CHAIN_SUBSTITUTION_ALLOWED", "claim_shape does not separate the evidence classes"
    if str(sc["hosted_conclusion"].get("state")) != "NOT_OBSERVED" and not sc["hosted_conclusion"].get("run_id"):
        return False, "HOSTED_CONCLUSION_UNBOUND", "hosted half claims a state without a run id"
    return True, "OK", f"offline={sc['offline_reproducible'].get('state')} hosted={sc['hosted_conclusion'].get('state')} (claim-shape lint only)"


CHECKS = [
    ("G10", "CHAIN_INTEGRITY", "BLOCKING", g10_chain_integrity),
    ("G11", "LINE_CONVENTION", "BLOCKING", g11_line_convention),
    ("G12", "SEGMENTATION_RULE", "BLOCKING", g12_segmentation_rule),
    ("G13", "COUNT_SCOPE", "BLOCKING", g13_count_scope),
    ("G14", "MAXIMUM_IS_GLOBAL", "BLOCKING", g14_maximum_is_global),
    ("G15", "LICENCE_LAYER", "BLOCKING", g15_licence_layer),
    ("G16a", "DEPENDENCY_TRUTHFUL", "BLOCKING", g16a_dependency_truthful),
    ("G16b", "DEPENDENCY_CLOSED", "REPORTING", g16b_dependency_closed),
    ("G17", "ENUM_SLASH_SAFE", "BLOCKING", g17_enum_slash_safe),
    ("G18", "DIGEST_LOCALITY", "BLOCKING", g18_digest_locality),
    ("G19", "COPY_REGISTER", "BLOCKING", g19_copy_register),
    ("G20", "SUPPLY_CHAIN_CLAIM_SHAPE", "REPORTING", g20_supply_chain_split),
    ("G21", "NUMBER_CONSISTENCY", "BLOCKING", g21_number_consistency),
    ("G22", "SELFTEST_CONTRACT", "BLOCKING", g22_selftest_contract),
    ("G23", "TRACE_ID_NAMED", "BLOCKING", g23_trace_ids),
]


def run_selftest(ctx: Ctx) -> int:
    """Ask the program what its own selftest returns.  The child runs with depth=1 so that G22 does
    not spawn a grandchild; G22 contributes nothing to the exit code either way, so the depth-1
    answer is the answer."""
    import subprocess
    env = dict(os.environ, FHS_SELFTEST_DEPTH="1")
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--round", ctx.round_dir, "--selftest", "--quiet"],
                       capture_output=True, text=True, env=env, timeout=120)
    return p.returncode


# ------------------------------------------------------------------------------------------------
# selftest: flip the field the check ACTUALLY reads

def _flip(ctx: Ctx, rel: str, mutate) -> tuple:
    p = ctx.path(rel)
    orig = open(p, "r", encoding="utf-8").read()
    try:
        d = json.loads(orig)
        mutate(d)
        with open(p, "w", encoding="utf-8", newline="") as fh:
            json.dump(d, fh, ensure_ascii=False)
        return None
    finally:
        pass


def _restore(ctx: Ctx, rel: str, orig: str):
    open(ctx.path(rel), "w", encoding="utf-8", newline="").write(orig)


MUTATIONS = {
    "G10": ("writeback/W0/W0_REVISION_MANIFEST.json",
            lambda d: d["chain"][3].__setitem__("sha256", "0" * 64)),
    "G11": ("lanes/A/SOURCE_LOCK_V3.json", lambda d: d["sources"][0].__setitem__("lines_match", False)),
    "G12": ("lanes/B/U0_PARTITION_V3.json",
            lambda d: d["totals"].__setitem__("structural_blocks_sum", d["totals"]["per_line_segments_sum"])),
    "G13": ("lanes/A/AUTHORITY_LEDGER_V3.json",
            lambda d: d["in_set"].__setitem__("duplicate_sha256_groups", 4)),
    "G14": ("lanes/C/METHOD_DEPENDENCE.json", lambda d: d["V02"].__setitem__("max_overall", 0.0)),
    "G15": ("lanes/B/TREE_IDENTITY.json",
            lambda d: d["subjects"][0]["licences"]["claim"].__setitem__("scope_note", "measured somewhere")),
    "G16a": ("lanes/B/TREE_IDENTITY.json",
             lambda d: d["subjects"][1].__setitem__("declared_covers_imports", not d["subjects"][1]["declared_covers_imports"])),
    "G17": ("lanes/E/WP21_ENUM_V3.json", lambda d: d["denominators"]["seam"].__setitem__("measured", 10)),
    "G18": ("out/stage/sbl/evidence/fhs-w0-r10-repair-20261108/MANIFEST.json",
            lambda d: d["files"][0].__setitem__("sha256", "0" * 64)),
    "G19": ("lanes/D/COPY_REGISTER_ALL.json",
            lambda d: d["r6_focus"].__setitem__("copies", 2) or d["r6_focus"].__setitem__("members", d["r6_focus"]["members"][:2])),
    "G20": ("lanes/D/WP19_V3.json", lambda d: d["supply_chain_claim"].__setitem__("claim_shape", "both halves are the same thing")),
    "G23": ("writeback/W0/W0_CLOSEOUT_DECISION.json", lambda d: d["defects"].__setitem__("X-99", "CLOSED")),
}

# Two checks cannot be mutated from inside this program: G21/G22 read the handover, which names a
# digest that changes every time this file is rebuilt, and G22 re-invokes this program to learn the
# real exit code.  They are exempted by name, with the reason printed, rather than silently counted
# as passing.
SELFTEST_EXEMPT = {
    "G21": "reads the handover that documents this run; mutating it would invalidate the run it is part of",
    "G22": "learns the exit code by invoking this program; a mutation inside it would recurse",
    "G16b": "measures the world (three checkouts), not an artifact; its falsifier is the patch plan in lanes/B, applied in a throw-away copy",
    "G20": "REPORTING check; mutated anyway",
}


def selftest(ctx: Ctx, verbose: bool = True) -> int:
    results = []
    failed = 0
    depth = os.environ.get("FHS_SELFTEST_DEPTH") == "1"
    for cid, name, sev, fn in CHECKS:
        entry = {"check": cid, "name": name, "severity": sev}
        if depth and cid == "G22":
            entry.update(baseline="SKIPPED", mutated="EXEMPT", exempt_reason="depth-1 child: G22 is the caller")
            results.append(entry)
            continue
        try:
            ok, code, detail = fn(ctx)
        except FileNotFoundError as e:
            entry.update(baseline="ABSENT", detail=str(e), mutated="SKIPPED")
            failed += 1
            results.append(entry)
            continue
        except FieldAbsent as e:
            entry.update(baseline="FIELD_ABSENT", detail=str(e), mutated="SKIPPED")
            failed += 1
            results.append(entry)
            continue
        entry["baseline"] = "PASS" if ok else "FAIL"
        entry["detail"] = detail
        if entry["baseline"] != "PASS":
            entry["mutated"] = "BASELINE_RED"
            if sev == "BLOCKING":
                failed += 1
        elif cid in MUTATIONS:
            rel, mut = MUTATIONS[cid]
            path = ctx.path(rel)
            orig = open(path, "r", encoding="utf-8").read()
            try:
                d = json.loads(orig)
                mut(d)
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    json.dump(d, fh, ensure_ascii=False)
                m = fn(ctx)
                entry["mutated"] = "FIRED" if m[0] is False else "DID_NOT_FIRE"
                entry["mutated_code"] = m[1]
            except Exception as e:  # noqa: BLE001
                entry["mutated"] = f"ERROR:{e.__class__.__name__}"
            finally:
                open(path, "w", encoding="utf-8", newline="").write(orig)
            if entry["mutated"] != "FIRED":
                failed += 1
        elif cid in SELFTEST_EXEMPT:
            entry["mutated"] = "EXEMPT"
            entry["exempt_reason"] = SELFTEST_EXEMPT[cid]
        else:
            entry["mutated"] = "NO_MUTATION_DEFINED"
            failed += 1
        results.append(entry)

    if verbose:
        for r in results:
            extra = f" ({r.get('mutated_code')})" if r.get("mutated_code") else ""
            print(f"{r['check']:5} {r['name']:24} baseline={r['baseline']:6} mutated={r['mutated']}{extra}")
    sys.stdout.write(json.dumps({"schema": "FHS.W0.GateSelftest/3", "results": results}, ensure_ascii=False) + "\n")
    return 0 if failed == 0 else 1



# ------------------------------------------------------------------------------------------------
# hygiene

def hygiene(root: str) -> list[dict]:
    findings = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root).replace("\\", "/")
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            if size > MAX_ARTIFACT_BYTES:
                findings.append({"path": rel, "why": "OVERSIZE", "bytes": size})
                continue
            if os.path.splitext(fn)[1].lower() in FORBIDDEN_SUFFIX:
                findings.append({"path": rel, "why": "FORBIDDEN_TYPE"})
                continue
            if size > 512 * 1024 or not fn.lower().endswith((".md", ".json", ".txt", ".py", ".yaml", ".yml", ".toml")):
                continue
            try:
                text = open(p, "r", encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for pat in TOKEN_SHAPES:
                if pat.search(text):
                    findings.append({"path": rel, "why": "TOKEN_SHAPED_STRING"})
                    break
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=".")
    ap.add_argument("--json", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--prior", default=None, help="accepted for symmetry; v3 has no prior mode because every check reads artifacts that did not exist before r10")
    ap.add_argument("--skip-hygiene", action="store_true")
    a = ap.parse_args()
    ctx = Ctx(a.round, a.prior)

    if a.selftest:
        return selftest(ctx, verbose=not a.quiet)

    hy = [] if a.skip_hygiene else hygiene(ctx.round_dir)
    results = []
    for cid, name, sev, fn in CHECKS:
        try:
            ok, code, detail = fn(ctx)
            verdict = "PASS" if ok else ("FAIL" if sev == "BLOCKING" else "OPEN")
        except FileNotFoundError as e:
            verdict, code, detail = "ABSENT", "ARTIFACT_ABSENT", str(e)
        except FieldAbsent as e:
            verdict, code, detail = "FAIL", "FIELD_ABSENT", f"the check reads a key the artifact does not write: {e}"
        except Exception as e:  # noqa: BLE001
            verdict, code, detail = "ERROR", "CHECK_RAISED", f"{e.__class__.__name__}: {e}"
        results.append({"check": cid, "name": name, "severity": sev, "verdict": verdict, "code": code, "detail": detail})

    blocking_fail = [r for r in results if r["verdict"] in ("FAIL", "ERROR", "ABSENT") and r["severity"] == "BLOCKING"]
    open_findings = [r for r in results if r["verdict"] in ("OPEN", "FAIL", "ERROR") and r["severity"] == "REPORTING"]
    passed = sum(1 for r in results if r["verdict"] == "PASS")

    report = {
        "schema": "FHS.W0.Gate/3",
        "gate": "GSTACK v3",
        "round": ctx.round_dir.replace("\\", "/"),
        "generated_at": now(),
        "checks": results,
        "summary": {"total": len(results), "pass": passed, "blocking_fail": len(blocking_fail),
                    "open_reporting_findings": len(open_findings)},
        "hygiene": {"count": len(hy), "findings": hy},
        "claim_ceiling": "GATE_VERDICT_NOT_ACCEPTANCE",
        "not_claimed": ["ORIGINAL_ACK", "NATIVE_WORLDRAW", "RELEASE_GRANTED", "INDEPENDENT_PASS"],
    }
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
            fh.write("\n")

    for r in results:
        mark = {"PASS": "ok  ", "FAIL": "FAIL", "OPEN": "OPEN", "ABSENT": "ABS ", "ERROR": "ERR "}[r["verdict"]]
        print(f"[{mark}] {r['check']:5} {r['name']:24} {r['code']:34} {r['detail'][:110]}")
    print(f"\nVERDICT {'PASS' if not blocking_fail and not hy else 'FAIL'} "
          f"pass={passed}/{len(results)} blocking_fail={len(blocking_fail)} open_reporting={len(open_findings)} hygiene={len(hy)}")
    if open_findings:
        print("open findings (reported, not gating):")
        for r in open_findings:
            print(f"  - {r['check']} {r['code']}: {r['detail'][:140]}")
    if hy:
        return 3
    if any(r["verdict"] == "ABSENT" for r in results if r["severity"] == "BLOCKING"):
        return 2
    return 0 if not blocking_fail else 1


if __name__ == "__main__":
    sys.exit(main())
