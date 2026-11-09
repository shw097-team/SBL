#!/usr/bin/env python3
"""GSTACK v5 — v4 plus the two gaps v4 could not see: identity claims outside the handover,
and an extra that "installs" without installing anything.

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

v4 closes three ways a future run could have gone green without proving anything:
  * `G18` passed `0/0` when a manifest carried `files: []` or omitted the key. Now the key must
    exist, the entry set must be non-empty, and it must equal the `expected_entry_set` the payload
    declares — so a manifest that silently narrows cannot pass.
  * `G16b` passed when a subject's scan was incomplete (`scan_complete: false`) because an absent
    module cannot appear in a set that was never scanned. Now incompleteness is its own verdict.
  * Coverage counted optional extras as if they were installed by `pip install .`. Now the required
    runtime set and the extras set are computed and judged separately, and an optional module must
    carry a measured `feature_when_absent`.

Also: the `yaml` claim is restated. The earlier round called it fail-open; what the code does is
return None from the YAML parser, fall back to strict JSON parsing (duplicate keys rejected), and
raise on YAML-only syntax. That is a bounded degradation, not a silent accept, and the artifact must
say which.

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


PAYLOAD_ALIASES = {
    # the round layout -> the payload layout, so CI can run this file from inside the payload
    "lanes/A/SOURCE_LOCK_V3.json": "evidence/SOURCE_LOCK_V3.json",
    "lanes/A/AUTHORITY_LEDGER_V3.json": "evidence/AUTHORITY_LEDGER_V3.json",
    "lanes/A/GATE_FORENSICS.json": "evidence/GATE_FORENSICS.json",
    "lanes/B/U0_PARTITION_V3.json": "evidence/U0_PARTITION_V3.json",
    "lanes/B/TREE_IDENTITY.json": "evidence/TREE_IDENTITY.json",
    "lanes/C/METHOD_DEPENDENCE.json": "evidence/METHOD_DEPENDENCE.json",
    "lanes/D/COPY_REGISTER_ALL.json": "evidence/COPY_REGISTER_ALL.json",
    "lanes/D/WP19_V3.json": "evidence/WP19_V3.json",
    "lanes/E/WP21_ENUM_V3.json": "evidence/WP21_ENUM_V3.json",
    "lanes/E/TRACE_AUDIT.json": "evidence/TRACE_AUDIT.json",
    "out/DEPENDENCY_SUBJECTS.json": "evidence/DEPENDENCY_SUBJECTS.json",
    "writeback/W0/FHS_PIPD-LS-PKG_W0_r10.md": "doc/FHS_PIPD-LS-PKG_W0_r10.md",
    "writeback/W0/FHS_PIPD-LS-PKG_W0_r11.md": "doc/FHS_PIPD-LS-PKG_W0_r11.md",
    "writeback/W0/W0_REVISION_MANIFEST.json": "evidence/W0_REVISION_MANIFEST.json",
    "writeback/W0/W0_CLOSEOUT_DECISION.json": "evidence/W0_CLOSEOUT_DECISION.json",
    "HANDOVER_R11_2026-11-08.md": "report/HANDOVER_R11_2026-11-08.md",
    "HANDOVER_R10_2026-11-08.md": "report/HANDOVER_R10_2026-11-08.md",
}


class Ctx:
    def __init__(self, round_dir: str, prior_dir: str | None = None, profile: str = "round", sdir: str | None = None):
        self.round_dir = os.path.abspath(round_dir)
        self.prior_dir = os.path.abspath(prior_dir) if prior_dir else None
        self.profile = profile
        self.sources_dir = sdir
        self.scope = "full"

    def doc_version(self) -> str:
        """The newest revision present, in the round layout or in the payload layout."""
        best = None
        d = os.path.join(self.round_dir, "writeback", "W0")
        if not os.path.isdir(d):
            d = os.path.join(self.round_dir, "doc")
        for fn in os.listdir(d) if os.path.isdir(d) else []:
            m = re.match(r"FHS_PIPD-LS-PKG_W0_r(\d+)\.md$", fn)
            if m and (best is None or int(m.group(1)) > best[0]):
                best = (int(m.group(1)), f"r{m.group(1)}")
        return best[1] if best else "r10"

    def inside(self, path: str) -> bool:
        if is_abs(path) and not os.path.exists(path):
            return False
        try:
            return os.path.commonpath([self.round_dir, os.path.realpath(path)]) == self.round_dir
        except ValueError:
            return False

    def doc_rel(self) -> str:
        return f"writeback/W0/FHS_PIPD-LS-PKG_W0_{self.doc_version()}.md"

    def handover_abs(self) -> str:
        v = self.doc_version().lstrip("r")
        for name in (f"HANDOVER_R{v}_2026-11-08.md",):
            direct = os.path.join(self.round_dir, name)
            if os.path.isfile(direct):
                return direct
            alias = PAYLOAD_ALIASES.get(name)
            if alias and self.profile == "payload":
                alt = os.path.join(self.round_dir, alias.replace("/", os.sep))
                if os.path.isfile(alt):
                    return alt
            if self.profile == "payload" and name.startswith("HANDOVER_R"):
                alt = os.path.join(self.round_dir, "report", name)
                if os.path.isfile(alt):
                    return alt
        cands = sorted(f for f in os.listdir(self.round_dir) if f.startswith("HANDOVER_R")) if os.path.isdir(self.round_dir) else []
        return os.path.join(self.round_dir, cands[-1]) if cands else os.path.join(self.round_dir, f"HANDOVER_R{v}_2026-11-08.md")

    def path(self, rel: str) -> str:
        direct = os.path.join(self.round_dir, rel.replace("/", os.sep))
        if os.path.exists(direct) or self.profile != "payload":
            return direct
        alt = PAYLOAD_ALIASES.get(rel)
        if alt:
            return os.path.join(self.round_dir, alt.replace("/", os.sep))
        m = re.match(r"^writeback/W0/(FHS_PIPD-LS-PKG_W0_r\d+\.md)$", rel)
        if m:
            return os.path.join(self.round_dir, "doc", m.group(1))
        return direct

    def load(self, rel: str) -> dict:
        p = self.path(rel)
        if not os.path.isfile(p):
            raise FileNotFoundError(p)
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)


# ------------------------------------------------------------------------------------------------
# dependency re-derivation (used by G16a/G16b)

WIN_ABS = re.compile(r"^[A-Za-z]:[\\/]")


def is_abs(p: str) -> bool:
    """Absolute on this host OR a Windows-style path seen from a POSIX runner.

    `os.path.isabs("C:/x")` is False on Linux, so a descriptor written on Windows silently became a
    relative path and got joined onto the payload directory. The CI log showed exactly that:
    `/home/runner/work/.../evidence/<round>/C:/Projects/...`.
    """
    return os.path.isabs(p) or p.startswith("/") or bool(WIN_ABS.match(p))


DIST_TO_IMPORT = {"pyyaml": "yaml", "pillow": "PIL", "beautifulsoup4": "bs4", "python-dateutil": "dateutil"}
IMPORT_RE = re.compile(r"^(\s*)(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)")


def _declared(pyproject_paths: list[str]) -> tuple[set[str], set[str], dict]:
    """Return (required runtime modules, optional-extra modules, detail).

    The two sets are kept apart on purpose: `pip install .` installs the first and not the second,
    so unioning them lets a package look covered while its default install lacks the module."""
    required: set[str] = set()
    optional: set[str] = set()
    detail = {}
    for p in pyproject_paths:
        with open(p, "rb") as fh:
            d = tomllib.loads(fh.read().decode("utf-8"))
        proj = d.get("project", {})
        run = [re.split(r"[<>=!~\[; ]", s.strip(), maxsplit=1)[0].lower() for s in proj.get("dependencies", []) or []]
        opt = {}
        for extra, specs in (proj.get("optional-dependencies") or {}).items():
            opt[extra] = [re.split(r"[<>=!~\[; ]", s.strip(), maxsplit=1)[0].lower() for s in specs]
        required |= set(run)
        optional |= {n for v in opt.values() for n in v}
        detail[os.path.basename(os.path.dirname(p)) or p] = {"runtime": run, "optional": opt}
    required |= {DIST_TO_IMPORT[d] for d in list(required) if d in DIST_TO_IMPORT}
    optional |= {DIST_TO_IMPORT[d] for d in list(optional) if d in DIST_TO_IMPORT}
    optional -= required
    return required, optional, detail


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


def _resolve(ctx: "Ctx", s: dict) -> dict:
    """Make a descriptor's paths absolute against the round dir, so the same descriptor works in a
    payload where the tree sits beside it rather than at a host absolute path."""
    out = dict(s)
    for k in ("metadata_files", "source_files"):
        if s.get(k):
            out[k] = [x if os.path.isabs(x) else ctx.path(x) for x in s[k]]
    if s.get("source_root"):
        out["source_root"] = s["source_root"] if os.path.isabs(s["source_root"]) else ctx.path(s["source_root"])
    out["path"] = s.get("path") if not s.get("path") or os.path.isabs(s.get("path")) else ctx.path(s["path"])
    return out


def derive_subject(s: dict) -> dict:
    required, optional, detail = _declared(s["metadata_files"])
    imports, complete = _imports(s)
    undeclared_required = {m: v for m, v in imports.items() if m.lower() not in required and m.lower() not in optional}
    via_extra_only = {m: v for m, v in imports.items() if m.lower() in optional and m.lower() not in required}
    behavioural = sorted({m for m, sites in undeclared_required.items() if any(not x["inside_function"] for x in sites)})
    return {
        "name": s["name"],
        "head": s.get("head"),
        "metadata_sha256": s.get("metadata_sha256"),
        "profile": "pip install . (default; no extras selected)",
        "declared_required": sorted(required),
        "declared_optional_extras": sorted(optional),
        "declared_detail": detail,
        "third_party_imported": sorted(imports),
        "scan_complete": complete,
        "undeclared_required": sorted(undeclared_required),
        "undeclared_sites": {k: v[:6] for k, v in undeclared_required.items()},
        "undeclared_used_at_module_level": behavioural,
        "provided_only_by_extra": sorted(via_extra_only),
        # coverage is judged against the default install, not the union of every extra
        "declared_covers_imports": not undeclared_required and not via_extra_only,
        "declared_covers_with_extras": not undeclared_required,
    }


# ------------------------------------------------------------------------------------------------
# checks


SOURCES_DEFAULT = r"C:/Projects/Agent_Workspace/FHS_W1_Work_Final/FHS_W1_Work_Final/sources"


def _remeasure_sources(directory: str, files: list[str]) -> dict:
    """Hash and count the source documents here, in this process, from their bytes."""
    out = {}
    for fn in files:
        p = os.path.join(directory, fn)
        if not os.path.isfile(p):
            return {"error": f"ABSENT:{fn}"}
        raw = open(p, "rb").read()
        out[fn] = {"bytes": len(raw), "lines": raw.count(b"\n"), "sha256": hashlib.sha256(raw).hexdigest()}
    return {"files": out}


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
    # a record must carry the numbers, not only booleans: "all true" with no figures behind it is a
    # claim about nothing (the red team passed G11 with 31 stub records)
    missing = []
    for r in recs:
        try:
            if (require(r, "declared").get("bytes") is None
                    or require(r, "declared").get("lines") is None
                    or require(r, "observed").get("bytes") is None
                    or require(r, "observed").get("lines_newline_count") is None):
                missing.append(r.get("source_id"))
        except FieldAbsent:
            missing.append(r.get("source_id"))
    if missing:
        return False, "LINE_RECORD_WITHOUT_NUMBERS", f"{len(missing)} records carry no figures, first={missing[0]}"
    bad = [r["source_id"] for r in recs if not (r["bytes_match"] and r["lines_match"] and r["sha_match"])]
    if bad:
        return False, "LINE_FIELD_FALSE", f"{len(bad)} records false, first={bad[0]}"
    # the totals must be the sums this run computes from the records, not two constants that agree
    calc_declared = sum(r["declared"]["lines"] for r in recs)
    calc_observed = sum(r["observed"]["lines_newline_count"] for r in recs)
    calc_bytes = sum(r["observed"]["bytes"] for r in recs)
    if not (calc_declared == d == calc_observed == o):
        return False, "LINE_TOTAL_NOT_DERIVED_FROM_RECORDS", f"artefact {d}/{o} vs records {calc_declared}/{calc_observed}"
    if calc_bytes <= 0 or require(a, "convention") in ("", None, {}):
        return False, "LINE_CONVENTION_UNSTATED", "the convention is empty or the byte total is zero"
    # the strongest form: re-hash the sources in this process. An artefact that says 31/31 without
    # anyone reopening the 31 files is a claim about a previous run.
    src = ctx.sources_dir or SOURCES_DEFAULT
    files = [r["file"] for r in recs]
    if os.path.isdir(src):
        m = _remeasure_sources(src, files)
        if "error" in m:
            return False, "SOURCE_REMEASURE_FAILED", m["error"]
        mism = []
        for r in recs:
            got = m["files"][r["file"]]
            if got["sha256"] != r["declared"].get("sha256") or got["bytes"] != r["declared"].get("bytes"):
                mism.append(r["source_id"])
        if mism:
            return False, "SOURCE_DISAGREES_WITH_DECLARATION", f"{len(mism)} of {len(recs)}: {mism[:3]}"
        return True, "OK", (f"{len(recs)}/{len(recs)} re-hashed from {os.path.basename(src)}: "
                            f"lines {sum(v['lines'] for v in m['files'].values()):,}, "
                            f"bytes {sum(v['bytes'] for v in m['files'].values()):,}")
    if ctx.profile == "payload":
        return False, "UNQUALIFIED_NO_SOURCES", "the 31 source documents are not in this payload, so nothing can be re-hashed here"
    return True, "OK", f"{len(recs)} records, sums derived here: lines {calc_observed}, bytes {calc_bytes:,} (sources not reachable, not re-hashed)"


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
    """In-set collisions re-derived from the 31 documents themselves.

    A ledger recording zero duplicates is indistinguishable from a ledger that never counted. The
    numbers below are grouped here, from the files, and then compared with the declared ones; a
    disagreement fails in either direction."""
    a = ctx.load("lanes/A/AUTHORITY_LEDGER_V3.json")
    inb = require(a, "in_set")
    declared_sha = require(inb, "duplicate_sha256_groups")
    declared_name = require(inb, "duplicate_basename_groups")

    src = ctx.sources_dir or SOURCES_DEFAULT
    if not os.path.isdir(src):
        return False, "UNQUALIFIED_NO_SOURCES", "the 31 source documents are not reachable, so the zeros cannot be re-derived"
    files = sorted(f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f)))
    if len(files) != 31:
        return False, "SOURCE_DENOMINATOR", f"{len(files)} files at the corpus, expected 31"
    by_sha, by_name = {}, {}
    for f in files:
        b = open(os.path.join(src, f), "rb").read()
        by_sha.setdefault(hashlib.sha256(b).hexdigest(), []).append(f)
        by_name.setdefault(f.lower(), []).append(f)
    measured_sha = sum(1 for v in by_sha.values() if len(v) > 1)
    measured_name = sum(1 for v in by_name.values() if len(v) > 1)
    if measured_sha != declared_sha or measured_name != declared_name:
        return False, "IN_SET_DISAGREES_WITH_DISK", (f"declared sha={declared_sha}/name={declared_name}, "
                                                     f"measured sha={measured_sha}/name={measured_name} over {len(files)} files")

    exts = [(k, a[k]) for k in ("kb_external_exact", "kb_external_normalised") if isinstance(a.get(k), dict)]
    if not exts:
        return False, "SCOPE_BLOCK_ABSENT", "no external-scope block"
    for label, blk in exts:
        require(blk, "scope"); require(blk, "match_rule")
        require(blk, "source_files_with_at_least_one_divergent_copy")
        den = require(blk, "denominator"); cov = require(blk, "denominator_covered")
        if den != len(files):
            return False, "SCOPE_DENOMINATOR", f"{label}: denominator={den}, but the corpus holds {len(files)} files"
        if cov != den:
            return False, "SCOPE_COVERAGE_GAP", f"{label}: only {cov}/{den}"
        if require(blk, "copies_counted") < den:
            return False, "SCOPE_VACUOUS", f"{label}: fewer copies than names"

    cr = require(a, "canonical_resolution")
    state = require(cr, "state")
    if state == "OWNER_UNRESOLVED":
        return False, "CANONICAL_STATE_UNRESOLVED", "the owner has decided; an unresolved ledger is now the defect"
    if state != "DECIDED_BY_OWNER":
        return False, "CANONICAL_STATE", state
    for k in ("decided_by", "choice", "rejected"):
        require(cr, k)
    return True, "OK", (f"re-derived over {len(files)} files: sha={measured_sha} name={measured_name} (declared {declared_sha}/{declared_name}); "
                        f"canonical {cr['choice'][:12]} decided by {cr['decided_by']}, {len(cr['rejected'])} rejection(s) recorded")

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
    identity_only = []
    for s in desc["subjects"]:
        s = _resolve(ctx, s)
        theirs = by_head.get(str(s.get("head") or "")[:12])
        if not isinstance(theirs, dict):
            mismatches.append((s["name"], "HEAD_NOT_IN_ARTIFACT"))
            continue
        metafiles = s.get("metadata_files") or []
        if ctx.profile == "payload" and not all(ctx.inside(m) for m in metafiles):
            # The tree is not in this payload. Verify the identity the artifact claims (HEAD and the
            # metadata digest) against the descriptor, and label the result as identity-only rather
            # than pretending a re-derivation happened here.
            want = s.get("metadata_sha256") or {}
            have = require(theirs, "pyproject")
            got = {os.path.basename(m): (have.get("sha256") if isinstance(have, dict) else None) for m in metafiles}
            pairs = [(k, want.get(k), got.get(k)) for k in want if want.get(k) and got.get(k)]
            if not pairs:
                # nothing to compare: reporting agreement here would be quantifying over an empty set
                mismatches.append((s["name"], "IDENTITY_CLAIM_WITHOUT_A_COMPARABLE_DIGEST"))
                continue
            if any(w != g for _, w, g in pairs):
                mismatches.append((s["name"], "METADATA_DIGEST_DISAGREES_WITH_DESCRIPTOR"))
                continue
            identity_only.append(s["name"])
            continue
        mine = derive_subject(s)
        claimed = require(theirs, "declared_covers_imports")
        if bool(claimed) != bool(mine["declared_covers_imports"]):
            mismatches.append((s["name"], f"claimed={claimed} derived={mine['declared_covers_imports']} (default profile)"))
            continue
        art_und = sorted(str(u.get("module") if isinstance(u, dict) else u) for u in (require(theirs, "undeclared") or []))
        derived_und = sorted(set(mine["undeclared_required"]) | set(mine["provided_only_by_extra"]))
        if art_und != derived_und:
            mismatches.append((s["name"], f"undeclared claimed={art_und} derived={derived_und}"))
    if mismatches:
        return False, "DEPENDENCY_ARTIFACT_DISAGREES_WITH_TREE", str(mismatches)
    tail = f"; identity-only (tree not in payload): {identity_only}" if identity_only else ""
    return True, "OK", f"{len(desc['subjects'])} subjects agree with what can be verified here{tail}"


def g16b_dependency_closed(ctx: Ctx):
    """REPORTING: is the default install actually covered, and was the tree fully scanned?

    v3 returned PASS when a subject's scan was incomplete, because a module that was never looked at
    cannot appear in the missing set. Incompleteness is now its own verdict, not a silent pass."""
    desc = ctx.load("out/DEPENDENCY_SUBJECTS.json")
    incomplete, gaps = {}, {}
    not_here = []
    for s in desc["subjects"]:
        s = _resolve(ctx, s)
        metafiles = s.get("metadata_files") or []
        if ctx.profile == "payload" and not all(ctx.inside(m) for m in metafiles):
            not_here.append(s["name"])
            continue
        d = derive_subject(s)
        if not d["scan_complete"]:
            incomplete[s["name"]] = {"scan_complete": False, "note": s.get("scan_note") or "the descriptor says the scan is partial"}
        if d["undeclared_required"] or d["provided_only_by_extra"]:
            gaps[s["name"]] = {
                "undeclared_required": d["undeclared_required"],
                "provided_only_by_extra": d["provided_only_by_extra"],
                "module_level": d["undeclared_used_at_module_level"],
            }
    if not_here and len(not_here) == len(desc["subjects"]):
        return False, "UNQUALIFIED_NO_SUBJECT_IN_PAYLOAD", json.dumps({"not_here": not_here}, ensure_ascii=False)[:300]
    tail = f"; not verifiable in this payload: {not_here}" if not_here else ""
    if incomplete:
        return False, "UNQUALIFIED_INCOMPLETE_SCAN", json.dumps({"incomplete": incomplete, "gaps": gaps}, ensure_ascii=False)[:400]
    if gaps:
        return False, "UNDECLARED_DEPENDENCY_OPEN", json.dumps(gaps, ensure_ascii=False)[:400]
    return True, "OK", f"every fully-scanned subject's default install covers its imports{tail}"


def g16c_optional_semantics(ctx: Ctx):
    """REPORTING: a module provided only by an extra must say what actually happens without it.

    Counting `[project.optional-dependencies]` as if `pip install .` installed it is how a package
    looks covered while its default host lacks the parser. Every non-required module must carry a
    classification measured by running the code with the module blocked, and that classification may
    not be `PROVIDED` when the default install does not provide it."""
    sem = None
    for rel in ("evidence/DEPENDENCY_SEMANTICS.json", "lanes/B/DEPENDENCY_SEMANTICS.json"):
        try:
            sem = ctx.load(rel)
            break
        except FileNotFoundError:
            continue
    if sem is None:
        raise FileNotFoundError("evidence/DEPENDENCY_SEMANTICS.json")

    coverage = sem.get("coverage") or {}
    verdicts = sem.get("verdicts") or {}
    if not coverage:
        raise FieldAbsent("coverage")
    allowed = {"SILENT_ACCEPT", "LOUD_REJECT", "DEGRADED_BUT_BOUNDED", "NOT_QUALIFIED", "PROVIDED", "SUBSTITUTED"}
    bad, states = [], {}
    for name, cov in coverage.items():
        if not isinstance(cov, dict):
            bad.append((name, "COVERAGE_NOT_AN_OBJECT"))
            continue
        provides = require(cov, "default_install_provides")
        fwa = require(cov, "feature_when_absent")
        if not (isinstance(fwa, str) and fwa.strip()) and not isinstance(fwa, dict):
            bad.append((name, "FEATURE_WHEN_ABSENT_EMPTY"))
            continue
        v = verdicts.get(name) or {}
        state = v.get("classification") or (fwa.get("state") if isinstance(fwa, dict) else None)
        if state is None:
            bad.append((name, "NO_MEASURED_CLASSIFICATION"))
            continue
        if state not in allowed:
            bad.append((name, f"UNKNOWN_CLASSIFICATION:{state}"))
            continue
        if provides is False and state == "PROVIDED":
            bad.append((name, "CLAIMS_PROVIDED_BUT_NOT_INSTALLED_BY_DEFAULT"))
            continue
        if provides is False and state.startswith("DEGRADED") and not v.get("why_not_silent_accept"):
            bad.append((name, "DEGRADED_WITHOUT_A_REASON"))
            continue
        states[name] = state
    if bad:
        return False, "OPTIONAL_SEMANTICS_UNQUALIFIED", json.dumps(bad, ensure_ascii=False)[:320]
    return True, "OK", f"{len(states)} non-required modules carry a measured absent-state: {states}"


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
    base = os.path.join(ctx.round_dir, "out", "stage") if ctx.profile != "payload" else ctx.round_dir
    manifests = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for fn in filenames:
            if fn in {"MANIFEST.json", "PROVENANCE.json"}:
                manifests.append(os.path.join(dirpath, fn))
    if not manifests:
        return False, "NO_PAYLOAD", "no manifest at all — a locality check with nothing to check is not a pass"
    problems = []
    resolved = declared = 0
    for m in manifests:
        mdir = os.path.realpath(os.path.dirname(m))
        doc = json.load(open(m, "r", encoding="utf-8"))
        # 1. the key must exist (v3 used .get(files, []) and passed 0/0 when it was absent)
        if "files" not in doc:
            return False, "FIELD_ABSENT", f"{os.path.basename(mdir)}/{os.path.basename(m)}: no 'files' key"
        entries = doc["files"]
        # 2. an empty entry list proves nothing (v3 passed 0/0)
        if not entries:
            return False, "EXPECTED_ENTRY_SET_EMPTY", f"{os.path.basename(mdir)}: files=[] — an empty manifest cannot vouch for anything"
        # 3. the manifest must state the set it intended to cover, and cover exactly that
        declared_expected = doc.get("expected_entry_set")
        if not isinstance(declared_expected, list) or not declared_expected:
            return False, "EXPECTED_ENTRY_SET_ABSENT", f"{os.path.basename(mdir)}: the payload does not declare expected_entry_set"
        # the set that counts is what is on disk, not what the manifest says it intended to cover:
        # deriving both sides from one list lets a narrowed payload pass against its own expectation
        on_disk = set()
        for dp, dns, fns in os.walk(mdir):
            dns[:] = [x for x in dns if x not in {".git", "__pycache__"}]
            for fn in fns:
                if fn in {"MANIFEST.json", "PROVENANCE.json", "SHA256SUMS"}:
                    continue
                on_disk.add(os.path.relpath(os.path.join(dp, fn), mdir).replace("\\", "/"))
        expected = sorted(on_disk)
        if sorted(declared_expected) != expected:
            return False, "EXPECTED_SET_DISAGREES_WITH_DISK", f"{os.path.basename(mdir)}: declared {len(declared_expected)} vs on disk {len(expected)}"
        if not expected:
            return False, "EXPECTED_ENTRY_SET_EMPTY", f"{os.path.basename(mdir)}: nothing on disk to vouch for"
        seen = {e.get("path") for e in entries}
        missing = sorted(set(expected) - seen)
        extra = sorted(seen - set(expected))
        if missing:
            return False, "EXPECTED_ENTRY_SET_NOT_COVERED", f"{os.path.basename(mdir)}: missing {missing[:5]}"
        if extra:
            return False, "ENTRY_OUTSIDE_EXPECTED_SET", f"{os.path.basename(mdir)}: undeclared {extra[:5]}"
        for e in entries:
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
    return True, "OK", f"{resolved}/{declared} resolve inside their own payload (realpath), {len(manifests)} manifests, entry sets match"



def read_long(path: str) -> bytes:
    r"""Read a file that may be under the Windows 260-character limit.

    The copy register declares `longpath_prefix_used: true`, so its own members were reached with the
    \\?\ prefix. A checker that opens the bare path raises FileNotFoundError on a file that exists and
    would then report 51 copies as absent - a false absence, which is the same class of error as a
    false pass."""
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except (FileNotFoundError, OSError):
        if re.match(r"^[A-Za-z]:[\\/]", path):
            pref = "\\\\?\\" + path.replace("/", "\\")
            with open(pref, "rb") as fh:
                return fh.read()
        raise




def _plain_path(x: str) -> str:
    """Normalise for comparison: strip the extended-length prefix the long-path walk introduces."""
    if x.startswith("\\\\?\\"):
        x = x[4:]
    return os.path.normcase(os.path.abspath(x))



def classify_walk_errors(errors: list, declared_paths: set):
    """Split traversal failures into fixture-excludable, other, and over-declared-copy.

    Pulled out as a pure function so the branch can be tested without creating an unreadable directory,
    a declared member under a fixture, and the privileges to prove it - three things a read-only verifier
    cannot arrange but can still reason about."""
    denied, other, covering = [], [], []
    for e in errors:
        path = e.get("path") or ""
        if not path:
            other.append(e)
            continue
        if "acl_probe" not in path and "protected_" not in path:
            other.append(e)
            continue
        located = _plain_path(path)
        covers = [d for d in declared_paths if d.startswith(located)]
        if covers:
            covering.append((e, covers))
            continue
        denied.append(e)
    return denied, other, covering


def longpath_walk(root: str, on_file, skip_dirs: set, fixture_dirs: set, budget_s: float, t0: float):
    r"""Walk a root, preferring the \\?\ form when the plain form cannot descend.

    Windows refuses paths past ~260 characters with WinError 3; os.walk reports that per directory and
    silently continues, which is why the first version of this check reported "no undeclared copies"
    while 24 subtrees were never entered. Try the plain form, then the extended-length form, and return
    whatever errors remain - the caller must not claim absence while any are left."""
    import time
    errors, undeclared, walked, hit = [], [], 0, False
    forms = [root]
    if re.match(r"^[A-Za-z]:[\\/]", root) and not root.startswith("\\\\?\\"):
        forms.append("\\\\?\\" + os.path.abspath(root).replace("/", "\\"))
    for form in forms:
        errors, undeclared, walked, hit = [], [], 0, False

        def _onerr(e):
            # the filename attribute is the path itself; parsing str(e) means parsing Python's repr
            # escaping, which is what made the ancestor test miss and let an exclusion through
            errors.append({"path": getattr(e, "filename", "") or "", "msg": str(e)[:140]})

        for dirpath, dirnames, filenames in os.walk(form, followlinks=False, onerror=_onerr):
            keep = []
            for d in dirnames:
                full = os.path.join(dirpath, d)
                if d in skip_dirs or os.path.islink(full):
                    continue
                if d in fixture_dirs:
                    on_file("fixture", full)
                    continue
                keep.append(d)
            dirnames[:] = keep
            for f in filenames:
                walked += 1
                on_file("file", os.path.join(dirpath, f))
            if time.time() - t0 > budget_s:
                hit = True
                break
        if not errors or hit:
            break
    return undeclared, walked, errors, hit

def g19_copy_register(ctx: Ctx):
    """Every declared copy is re-read, every declared root is walked, every group is recounted.

    Round-1 officer NACK: the check covered only the r6-focus subset. Round-2 officer NACK: it then
    reported "25 roots" while visiting 24, and claimed no root walk at all. Both were true, and both
    are the same defect - the sentence said more than the code did. The counts below are computed from
    what this run actually visited, never written from the artifact's own numbers."""
    import time
    a = ctx.load("lanes/D/COPY_REGISTER_ALL.json")
    groups = require(a, "names_exact")
    gn = require(a, "names_normalised")
    roots = require(a, "roots_scanned")
    bounds = require(a, "scan_bounds")
    if not isinstance(groups, list) or not groups:
        return False, "REGISTER_EMPTY", "names_exact is empty; nothing was ever counted"
    if len(groups) != 45 or len(gn) != 45:
        return False, "REGISTER_DENOMINATOR", f"names_exact={len(groups)} names_normalised={len(gn)}, expected 45/45"

    # 1. every root that the register says exists must still exist; count only what is visited
    declared_present = [r for r in roots if r.get("exists")]
    visited_roots = [r for r in declared_present if os.path.isdir(r.get("path") or "")]
    gone = [r.get("label") for r in declared_present if r not in visited_roots]
    if gone:
        return False, "ROOT_ABSENT", f"{len(gone)} of {len(declared_present)} roots declared present are gone: {gone[:3]}"

    # 2. every member of every group is re-hashed at its declared path
    checked, absent, drift, bad_counts, bad_digests = 0, [], [], [], []
    declared_paths = set()
    for group in groups + gn:
        members = group.get("members") or []
        if group.get("copies") != len(members):
            bad_counts.append((group.get("name"), group.get("copies"), len(members)))
        hashes = []
        for m in members:
            path, sha = m.get("path"), m.get("sha256")
            if not path or not sha:
                return False, "MEMBER_INCOMPLETE", json.dumps(m, ensure_ascii=False)[:160]
            declared_paths.add(_plain_path(path))
            cand = path if re.match(r"^[A-Za-z]:[\\/]", path) else os.path.join(ctx.round_dir, path)
            try:
                raw = read_long(cand)
            except (FileNotFoundError, OSError):
                absent.append(path)
                continue
            got = hashlib.sha256(raw).hexdigest()
            checked += 1
            hashes.append(got)
            if got != sha or len(raw) != m.get("bytes"):
                drift.append({"path": path, "declared": sha[:12], "measured": got[:12]})
        if hashes and group.get("distinct_digests") != len(set(hashes)):
            bad_digests.append((group.get("name"), group.get("distinct_digests"), len(set(hashes))))

    if absent:
        return False, "MEMBER_ABSENT", f"{len(absent)} of {checked + len(absent)} declared copies are not on disk: {absent[:3]}"
    if bad_counts:
        return False, "GROUP_COUNT_DISAGREES", json.dumps(bad_counts[:3], ensure_ascii=False)
    if bad_digests:
        return False, "GROUP_DIGESTS_DISAGREE", json.dumps(bad_digests[:3], ensure_ascii=False)
    if drift:
        # collected during the loop and judged here; the rewrite that fixed the coverage made this list
        # and forgot to read it, which the round-3 officer caught with the negative control
        return False, "MEMBER_DIGEST_DRIFT", json.dumps(drift[:3], ensure_ascii=False)

    # 3. walk every visited root for a same-named file the register never declared
    names = set()
    for group in groups + gn:
        for m in group.get("members") or []:
            if m.get("name"):
                names.add(m["name"].lower())
    skip_dirs = set((bounds.get("skip_dirs") or []) + [".git", "node_modules", "__pycache__", ".venv"])
    # Directories the round itself declares as disposable fixtures. Excluded by name, and the number of
    # files excluded is printed in the result: an exclusion a reader cannot see is a weakened check.
    fixture_dirs = {"_sandbox", "_g18_demo", "_redteam_fixtures", "_verify", "scratch"}
    undeclared, excluded_fixtures = [], []
    t0 = time.time()
    walk_errors, walked, budget_hit = [], 0, False

    def _visit(kind, full):
        global _UNDECL, _FIX
        if kind == "fixture":
            excluded_fixtures.append(full)
            return
        f = os.path.basename(full)
        if f.lower() in names:
            norm = _plain_path(full)
            if norm not in declared_paths:
                undeclared.append(full)

    for r in visited_roots:
        _u, w, errs, hit = longpath_walk(r["path"], _visit, skip_dirs, fixture_dirs, 240, t0)
        walked += w
        if errs:
            # no truncation: this list decides whether absence may be claimed, so dropping its tail
            # would be the same defect the list exists to prevent
            walk_errors.extend({"root": r.get("label"), **e} for e in errs)
        if hit:
            budget_hit = True
            break
    if budget_hit:
        return False, "ROOT_WALK_INCOMPLETE", f"walk stopped after 240s at {walked} files; an incomplete walk cannot report absence"
    if walk_errors:
        # A subtree that is unreadable because it was *built* unreadable is a known fixture, not an
        # unknown region - but only if nothing the register declares lives under it. That is checked
        # here rather than assumed, so an exclusion can never hide a declared copy.
        denied, other, covering = classify_walk_errors(walk_errors, declared_paths)
        if covering:
            e, covers = covering[0]
            return False, "ROOT_WALK_ERRORS_OVER_DECLARED_COPY", (
                f"an unreadable subtree covers {len(covers)} declared cop(y/ies): {covers[:2]}")
        if other:
            return False, "ROOT_WALK_ERRORS", (f"{len(other)} subtree(s) could not be traversed, so absence cannot be claimed: "
                                               f"{json.dumps([{k: v for k, v in e.items() if k != 'root'} for e in other[:2]], ensure_ascii=False)}")
        # every refusal left is an intentionally locked fixture directory with no declared member
        excluded_fixtures.extend((e.get("path") or e.get("msg", ""))[:80] for e in denied)
    if undeclared:
        return False, "UNDECLARED_COPY_ON_DISK", f"{len(undeclared)} same-named file(s) under visited roots were never registered: {undeclared[:3]}"

    declared_hashed = bounds.get("files_hashed")
    if isinstance(declared_hashed, int) and checked < declared_hashed:
        return False, "HASH_COVERAGE_GAP", f"re-hashed {checked} files but the register claims {declared_hashed} were hashed"

    cr = require(a, "canonical_resolution")
    state = require(cr, "state")
    if state == "OWNER_UNRESOLVED":
        return False, "CANONICAL_STATE_UNRESOLVED", "the owner has decided; an unresolved register is now the defect"
    if state != "DECIDED_BY_OWNER":
        return False, "CANONICAL_STATE", state
    return True, "OK", (f"{len(groups)}+{len(gn)} groups; {checked} copies re-hashed at their declared paths with counts and "
                        f"distinct digests recomputed per group; {len(visited_roots)} of {len(declared_present)} declared-present "
                        f"roots walked ({walked:,} files) with no undeclared same-named copy; "
                        f"{len(excluded_fixtures)} fixture director(ies) excluded by name; canonical decided by {cr.get('decided_by')}")

def g10_chain_integrity(ctx: Ctx):
    """The document's OWN parent, and a chain that contains every version including r8."""
    doc = ctx.path(ctx.doc_rel())
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
    latest = ctx.doc_version()
    _ship = by_v[latest].get("shipment") or {}
    if by_v[latest].get("sha256") != sha_file(doc) and _ship.get("sha256") != sha_file(doc):
        return False, "CHAIN_LATEST_DIGEST", f"manifest {latest} digest != file"
    latest = ctx.doc_version()
    pred = chain[-2]["version"] if chain[-1]["version"] == latest else latest
    if getattr(ctx, "profile", "round") == "payload":
        # In the payload profile the historical revisions are not shipped, so no prefix can be proven
        # from bytes that are not there. The chain property is checked where all revisions exist: the
        # round profile. What the payload can still assert is that the chain is present and that its
        # latest entry is the document actually shipped.
        # The payload carries the document twice on purpose: the author bytes that the owner signed, and an
        # LF-normalised copy for the repository's blob rule. The chain names the author bytes, so any shipped
        # copy may satisfy it - but at least one must, byte for byte.
        import base64 as _b64
        _want = by_v[latest].get("sha256")
        _name = os.path.basename(ctx.doc_rel())
        _seen = {}
        for _root, _dirs, _files in os.walk(ctx.round_dir):
            for _f in _files:
                if _f == _name:
                    _p = os.path.join(_root, _f)
                    try:
                        _seen[_p] = hashlib.sha256(open(_p, "rb").read()).hexdigest()
                    except Exception:
                        continue
        if len(chain) < 2:
            return False, "CHAIN_TRUNCATED_IN_PAYLOAD", "the shipped chain is too short"
        if _want not in _seen.values():
            # the payload ships the LF-normalised copy because the repository forbids CRLF blobs, so the
            # author bytes may legitimately be absent; a normalisation record that names both digests and
            # the transformation closes the gap, and it must point at a copy that is actually shipped.
            _n = None
            for _root, _dirs, _files in os.walk(ctx.round_dir):
                for _f in _files:
                    if _f == "NORMALISATION.json":
                        try:
                            _n = json.load(open(os.path.join(_root, _f), encoding="utf-8"))
                        except Exception:
                            _n = None
            if not _n or (_n.get("author_bytes") or {}).get("sha256") != _want:
                return False, "CHAIN_TRUNCATED_IN_PAYLOAD", f"no shipped copy hashes to the chain's latest entry ({len(_seen)} copies seen) and no normalisation record reconciles it"
            _shipped_sha = (_n.get("shipped_bytes") or {}).get("sha256")
            if _shipped_sha not in _seen.values():
                return False, "NORMALISATION_UNMATCHED", "the normalisation record names shipped bytes that are not present"
            return True, "", (f"payload: shipped copy is the LF form ({_shipped_sha[:16]}); the normalisation record "
                              f"reconciles it to the author bytes the chain and the signatures bind ({_want[:16]})")
        return True, "", (f"payload: {len(_seen)} shipped copy/copies of the document, one of which is the "
                          f"chain's latest entry; parent-prefix proof belongs to the round profile")
    if by_v[pred].get("sha256") != declared:
        # In an append-only chain the document's last declared parent can be an ancestor rather than the
        # immediate predecessor, because a record-only chapter need not restate one. That is acceptable
        # only if the declared parent is itself in the chain AND its bytes are a byte-exact prefix of
        # this document - a stronger statement than naming the predecessor, since it can be recomputed.
        ancestor = next((c for c in chain if c.get("sha256") == declared), None)
        prefix_ok = False
        if ancestor and isinstance(ancestor.get("bytes"), int):
            try:
                head = open(ctx.path(ctx.doc_rel()), "rb").read(ancestor["bytes"])
                prefix_ok = hashlib.sha256(head).hexdigest() == declared
            except Exception:
                prefix_ok = False
        if not prefix_ok:
            return False, "PARENT_IS_NOT_ITS_OWN_PARENT", f"doc declares {declared[:16]} but manifest {pred} is {str(by_v[pred].get('sha256'))[:16]} and it is not a proven ancestor prefix"
    external = []
    resolved = {}
    _order = [c["version"] for c in chain]
    for v in _order:
        ent = by_v[v]
        p = ent.get("path") or f"FHS_PIPD-LS-PKG_W0_{v}.md"
        # the last version is the document under test: resolve it where it actually is, not by the
        # absolute path the manifest recorded on the machine that built it
        shipped = ctx.path(f"doc/FHS_PIPD-LS-PKG_W0_{v}.md") if ctx.profile == "payload" else None
        if shipped and os.path.isfile(shipped):
            cand = shipped
        elif ctx.profile == "payload" and v != _order[-1]:
            # not shipped here: mixing this payload's LF copy with a CRLF file from the round would
            # compare two different transformations and call the result a broken prefix
            external.append({"version": v, "path": p, "why": "NOT_SHIPPED_IN_THIS_PAYLOAD"})
            continue
        else:
            cand = doc if v == _order[-1] else (p if is_abs(p) else ctx.path(p))
        if not os.path.isfile(cand):
            if v == _order[-1]:
                return False, "CHAIN_FILE_ABSENT", f"{v}: {cand}"
            external.append({"version": v, "path": p, "why": "NOT_IN_PAYLOAD"})
            continue
        measured = sha_file(cand)
        ship = ent.get("shipment") or {}
        if measured != ent.get("sha256") and measured != ship.get("sha256"):
            return False, "CHAIN_DIGEST_MISMATCH", v
        resolved[v] = cand
    prev = None
    for v in _order:
        ent = by_v[v]
        if v not in resolved:
            prev = v
            continue
        if prev is not None and prev in resolved:
            if ent.get("parent_sha256") not in (None, by_v[prev].get("sha256")):
                return False, "CHAIN_LINK_MISMATCH", f"{v} parent {str(ent.get('parent_sha256'))[:12]} != {prev} {str(by_v[prev].get('sha256'))[:12]}"
            if ent.get("prefix_of_parent") is not True:
                return False, "CHAIN_PREFIX_NOT_VERIFIED", f"{v} does not record that the parent's bytes are its own prefix"
            prev_bytes = open(resolved[prev], "rb").read()
            if open(resolved[v], "rb").read()[:len(prev_bytes)] != prev_bytes:
                return False, "CHAIN_PREFIX_BROKEN", f"{v} is not a byte-prefix extension of {prev}"
        elif prev is not None:
            # the parent was not shipped here, so only the link's recorded digest can be checked
            if ent.get("parent_sha256") not in (None, by_v[prev].get("sha256")):
                return False, "CHAIN_LINK_MISMATCH", f"{v} parent digest disagrees with the manifest's {prev}"
        prev = v
    tail = f"; {len(external)} earlier link(s) recorded by digest only (not shipped here)" if external else ""
    return True, "OK", f"chain {'→'.join(order[-7:])}; own parent {declared[:12]} == {pred}; {len(decls)} declarations, the last one counts{tail}"


def _shipped_identity(ctx: Ctx):
    """(bytes, sha256) of the LF copy if this round staged one, else None."""
    try:
        man = ctx.load("writeback/W0/W0_REVISION_MANIFEST.json")
    except FileNotFoundError:
        try:
            man = ctx.load("evidence/W0_REVISION_MANIFEST.json")
        except FileNotFoundError:
            return None
    for e in (man.get("chain") or []):
        ship = e.get("shipment")
        if ship and ship.get("sha256"):
            return (ship["bytes"], ship["sha256"])
    return None


def g21_number_consistency(ctx: Ctx):
    """A number the round publishes about a file must equal the file."""
    doc = ctx.path(ctx.doc_rel())
    size = os.path.getsize(doc)
    handover = ctx.handover_abs()
    if not os.path.isfile(handover):
        return False, "HANDOVER_ABSENT", handover
    txt = open(handover, "r", encoding="utf-8", errors="replace").read()
    ver = ctx.doc_version()
    m = re.search(rf"FHS_PIPD-LS-PKG_W0_{ver}\.md[^\n]{{0,200}}?([\d][\d,]{{3,}})\s*(?:bytes|B)", txt)
    if not m:
        return False, "CLAIM_NOT_FOUND", "the handover does not state the document's byte count"
    # EVERY claim about this version must hold, not just the first one: a stale size sitting beside a
    # correct one is how the previous round's consolidated document stayed wrong for a whole review.
    ok_bytes = {size}
    for cand in (ctx.path(f"out/stage/sbl/evidence/fhs-w0-{ctx.doc_version()}-repair-20261108/doc/FHS_PIPD-LS-PKG_W0_{ctx.doc_version()}.md"),):
        if os.path.isfile(cand):
            ok_bytes.add(os.path.getsize(cand))
    # a payload carries the normalised copy, so the number a reader here measures is the shipment's.
    # Accept it only when the shipment digest is the digest of the file this run just hashed: a
    # recorded number that is not tied to bytes would let the manifest vouch for itself.
    try:
        rm = None
        for cand in ("writeback/W0/W0_REVISION_MANIFEST.json", "evidence/W0_REVISION_MANIFEST.json"):
            try:
                rm = ctx.load(cand)
                break
            except FileNotFoundError:
                continue
        for e in (rm or {}).get("chain", []):
            if e.get("version") == ctx.doc_version() and isinstance(e.get("shipment"), dict):
                sh = e["shipment"]
                if sh.get("sha256") == sha_file(doc):
                    # the same document in two transformations: the shipment digest ties the pair, so
                    # both recorded sizes name bytes that exist rather than a number on its own
                    ok_bytes.add(int(sh["bytes"]))
                    if isinstance(e.get("bytes"), int):
                        ok_bytes.add(int(e["bytes"]))
    except (FileNotFoundError, KeyError, TypeError):
        pass
    claims = [int(x.replace(",", "")) for x in re.findall(rf"FHS_PIPD-LS-PKG_W0_{ver}\.md[^\n]{{0,200}}?([\d][\d,]{{3,}})\s*(?:bytes|B)", txt)]
    stale = sorted({c for c in claims if c not in ok_bytes})
    if not claims:
        return False, "CLAIM_NOT_FOUND", "the handover states no byte count for this version"
    if stale:
        return False, "HANDOVER_BYTES_DISAGREE", f"stale={stale} measured={sorted(ok_bytes)}"
    sm = re.search(rf"FHS_PIPD-LS-PKG_W0_{ver}\.md[^\n]{{0,240}}?`([0-9a-f]{{64}})`", txt)
    if not sm:
        return False, "CLAIM_NOT_FOUND", "the handover does not state the document digest"
    here = sha_file(doc)
    ok_sha = {here}
    # the LF copy counts only if this run can hash it right now; taking the digest from the manifest
    # let the red team pass G21 with a handover and a shipment that agreed on a wrong value
    for cand in (ctx.path(f"out/stage/sbl/evidence/fhs-w0-{ctx.doc_version()}-repair-20261108/doc/FHS_PIPD-LS-PKG_W0_{ctx.doc_version()}.md"),):
        if os.path.isfile(cand):
            ok_sha.add(sha_file(cand))
    # in a payload only the normalised copy exists, so the round's own digest is also a true identity
    # of this document - but only when the manifest ties the two through the shipment digest we just
    # recomputed. Without that tie the claim would be the manifest vouching for itself.
    try:
        rm2 = None
        for cand in ("writeback/W0/W0_REVISION_MANIFEST.json", "evidence/W0_REVISION_MANIFEST.json"):
            try:
                rm2 = ctx.load(cand)
                break
            except FileNotFoundError:
                continue
        for e in (rm2 or {}).get("chain", []):
            if e.get("version") == ctx.doc_version() and isinstance(e.get("shipment"), dict) \
                    and e["shipment"].get("sha256") == here and e.get("sha256"):
                ok_sha.add(e["sha256"])
    except (KeyError, TypeError):
        pass
    if sm.group(1) not in ok_sha:
        return False, "HANDOVER_SHA_DISAGREE", f"claimed={sm.group(1)[:12]} measured={[x[:12] for x in sorted(ok_sha)]}"
    return True, "OK", f"handover states {sorted(ok_bytes)[-1]:,} B (and no stale size) with a matching digest"


def g22_selftest_contract(ctx: Ctx):
    """Documented exit code versus the one this gate returns.

    This is the one check that cannot be re-derived from anything outside the gate: the subject is the
    gate. It is kept because a handover that documents an exit code the program never returns is a real
    and common defect, but its result is labelled SELF_REPORTED and it does not gate."""
    handover = ctx.handover_abs()
    txt = open(handover, "r", encoding="utf-8", errors="replace").read()
    m = re.search(r"--selftest[^\n]{0,200}?exit[^\d]{0,10}(\d)", txt)
    if not m:
        return False, "CLAIM_NOT_FOUND", "the handover does not document the selftest exit code"
    documented = int(m.group(1))
    actual, bad = selftest_diagnose(ctx)
    if documented != actual:
        return False, "SELFTEST_EXIT_DOCUMENTED_WRONG", f"SELF_REPORTED_BY_THE_SUBJECT documented={documented} actual={actual}; rows not fired: {bad[:6]}"
    return True, "OK", f"SELF_REPORTED_BY_THE_SUBJECT documented exit {documented} == actual"

def g23_trace_ids(ctx: Ctx):
    """Every finding the round calls CLOSED must be named in the document it claims to have changed."""
    close = ctx.load("writeback/W0/W0_CLOSEOUT_DECISION.json")
    defects = require(close, "defects")
    doc = open(ctx.path(ctx.doc_rel()), "r", encoding="utf-8", errors="replace").read()
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





def g24_identity_claims(ctx: Ctx):
    """Every claim a shipped document makes about a revision's bytes must be true.

    `G21` only watched the handover, so a consolidated document could keep quoting a superseded size
    while the handover was correct — which is exactly what the previous round shipped. This walks all
    documents and checks each claim against the revision manifest, which is the only place the set of
    true identities is recorded.
    """
    try:
        man = ctx.load("writeback/W0/W0_REVISION_MANIFEST.json")
    except FileNotFoundError:
        man = ctx.load("evidence/W0_REVISION_MANIFEST.json")
    truth = {}
    for e in man.get("chain") or []:
        v = e.get("version")
        truth.setdefault(v, set())
        if e.get("sha256"):
            truth[v].add((e["sha256"], e.get("bytes")))
        ship = e.get("shipment") or {}
        if ship.get("sha256"):
            truth[v].add((ship["sha256"], ship.get("bytes")))
        # a revision can legitimately exist as more than one copy (r6 does, and the ambiguity is an
        # owner item). Those copies are true identities of that version and must not be flagged.
        for c in e.get("known_copies") or []:
            if c.get("sha256"):
                truth[v].add((c["sha256"], c.get("bytes")))
    if not truth:
        raise FieldAbsent("chain")

    pat = re.compile(r"FHS_PIPD-LS-PKG_W0_(r\d+)\.md([^\n]{0,240})")
    hexpat = re.compile(r"\b([0-9a-f]{64})\b")
    numpat = re.compile(r"([\d][\d,]{3,})\s*(?:bytes|B)\b")
    claims = 0
    stale = []
    skipped = []
    composition = 0
    roots = [ctx.round_dir]
    disposable = ("_sandbox", "_g18_demo", "_redteam_fixtures", "_verify", "scratch")
    for dirpath, dirnames, filenames in os.walk(ctx.round_dir):
        # fixture directories exist precisely to contain wrong documents; scanning them would turn a
        # deliberately false claim into a finding about the round
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "stage"} and d not in disposable]
        for fn in filenames:
            if not fn.lower().endswith((".md", ".json")):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(fp) > 4 * 1024 * 1024:
                    continue
                text = open(fp, "r", encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if fp.lower().endswith(".json"):
                try:
                    head = json.loads(text)
                except ValueError:
                    head = None
                if isinstance(head, dict) and head.get("claims_are_quoted_data") is True:
                    skipped.append(os.path.relpath(fp, ctx.round_dir).replace("\\", "/"))
                    continue
            for m in pat.finditer(text):
                ver, tail = m.group(1), m.group(2)
                if ver not in truth:
                    continue
                # "`r19.md` = r11 full text (… N bytes) + this chapter" states the PARENT's size, not
                # the named file's. Counting it would flag a true sentence.
                if ("全文" in tail) or ("＋本章" in tail):
                    composition += 1
                    continue
                for h in hexpat.findall(tail):
                    claims += 1
                    if not any(h == t[0] for t in truth[ver]):
                        stale.append({"file": os.path.relpath(fp, ctx.round_dir).replace("\\", "/"),
                                      "version": ver, "claimed_sha256": h[:16], "kind": "digest"})
                for n in numpat.findall(tail):
                    claims += 1
                    if not any(int(n.replace(",", "")) == t[1] for t in truth[ver] if t[1]):
                        stale.append({"file": os.path.relpath(fp, ctx.round_dir).replace("\\", "/"),
                                      "version": ver, "claimed_bytes": n, "kind": "bytes"})
    if claims < 4:
        return False, "TOO_FEW_CLAIMS_SEEN", f"{claims} claims found; a sweep that sees nothing cannot vouch for anything"
    if stale:
        return False, "STALE_IDENTITY_CLAIM", f"{len(stale)} stale of {claims}: {stale[:4]}"
    tail = f"; {composition} composition sentence(s) state a parent's size and were not counted as identity claims"
    tail += f"; {len(skipped)} file(s) declared themselves defect reports quoting wrong values: {skipped}" if skipped else ""
    return True, "OK", f"{claims} claims consistent with the revision manifest{tail}"


def g25_extra_qualified(ctx: Ctx):
    """An extra name that does not exist installs nothing and still exits 0.

    So "install with .[extra]" is not by itself a qualification step. The artifact must record, per
    subject, which extras exist in the metadata, which actually add distributions, and which attempts
    were no-ops — and a no-op must not be reported as if it had provided the module."""
    qual = None
    for rel in ("evidence/EXTRA_QUALIFICATION.json", "lanes/B/EXTRA_QUALIFICATION.json"):
        try:
            qual = ctx.load(rel)
            break
        except FileNotFoundError:
            continue
    if qual is None:
        raise FileNotFoundError("evidence/EXTRA_QUALIFICATION.json")
    subjects = require(qual, "subjects")
    if not isinstance(subjects, list) or not subjects:
        raise FieldAbsent("subjects")
    bad, declared_total, noop_total = [], 0, 0
    for t in subjects:
        sid = t.get("subject_id")
        declared = require(t, "extras_declared")
        provided = require(t, "extras_metadata_provided")
        if sorted(declared) != sorted(provided):
            bad.append((sid, "DECLARED_EXTRA_MISSING_FROM_METADATA", declared, provided))
        noops = t.get("extras_noop_attempted") or []
        noop_total += len(noops)
        declared_total += len(declared)
        for at in noops:
            if at in provided:
                bad.append((sid, "NOOP_CLAIMED_AS_PROVIDED", at))
    if bad:
        return False, "EXTRA_QUALIFICATION_FAILED", json.dumps(bad, ensure_ascii=False)[:320]
    # the fixture is what proves the method discriminates: an extra that exists must really install
    fx = qual.get("fixture") or {}
    proof = (fx.get("present_extra_adds") or fx.get("extras_installable") or [])
    if not proof:
        return False, "METHOD_NOT_PROVEN", "no fixture shows that a declared extra actually adds a distribution"
    return True, "OK", (f"{len(subjects)} subjects, {declared_total} declared extras; {noop_total} no-op attempt(s) "
                        f"record a warning and add nothing; fixture proves a real extra adds {proof}")


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



def selftest_diagnose(ctx: Ctx):
    """Run the selftest in a child and say which rows did not fire — a bare exit code is not a
    diagnosis, and CI is exactly where the difference between the two matters."""
    import subprocess
    env = dict(os.environ, FHS_SELFTEST_DEPTH="1")
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--round", ctx.round_dir,
                        "--profile", ctx.profile, "--scope", getattr(ctx, "scope", "full"),
                        "--selftest", "--quiet"],
                       capture_output=True, text=True, env=env, timeout=240)
    bad = []
    for line in p.stdout.splitlines():
        if line.startswith("{"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            for r in d.get("results", []):
                if r.get("mutated") not in ("FIRED", "EXEMPT"):
                    bad.append(f"{r['check']}:{r.get('mutated')}:{r.get('baseline')}")
    return p.returncode, bad


def run_selftest(ctx: Ctx) -> int:
    """Ask the program what its own selftest returns. The child runs with depth=1 so G22 does not
    spawn a grandchild; G22 contributes nothing to the exit code either way, so the depth-1 answer is
    the answer."""
    import subprocess
    env = dict(os.environ, FHS_SELFTEST_DEPTH="1")
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--round", ctx.round_dir,
                        "--profile", ctx.profile, "--selftest", "--quiet"],
                       capture_output=True, text=True, env=env, timeout=240)
    return p.returncode


def _report_target(ctx: Ctx) -> str:
    """The consolidated report this round ships, whichever profile and revision is running.

    Globbed, not enumerated: the previous two rounds each failed the payload selftest with
    MUTATION_TARGET_ABSENT because a version-specific name was missing from a hand-written list.
    """
    import glob as _g
    for pat in ("report/FHS_W0_R*_CONSOLIDATED.md", "out/FHS_W0_R*_CONSOLIDATED_FOR_EXTERNAL_ACCEPTOR.md"):
        hits = sorted(_g.glob(os.path.join(ctx.round_dir, pat.replace("/", os.sep))))
        if hits:
            return os.path.relpath(hits[-1], ctx.round_dir).replace(os.sep, "/")
    return "report/FHS_W0_R23_CONSOLIDATED.md"


MUTATIONS = {   # G27/G28 have their own in-memory branches below; everything here lands in the copy
    # mutate the link that is actually verifiable here: in a payload the older links are recorded by
    # digest only, so flipping one of those proves nothing about the check
    "G10": ("writeback/W0/W0_REVISION_MANIFEST.json",
            lambda d: (d["chain"][-1].__setitem__("sha256", "0" * 64),
                       (d["chain"][-1].get("shipment") or {}).__setitem__("sha256", "0" * 64))),
    "G11": ("lanes/A/SOURCE_LOCK_V3.json", lambda d: d["sources"][0].__setitem__("lines_match", False)),
    "G12": ("lanes/B/U0_PARTITION_V3.json",
            lambda d: d["totals"].__setitem__("structural_blocks_sum", d["totals"]["per_line_segments_sum"])),
    "G13": ("lanes/A/AUTHORITY_LEDGER_V3.json",
            lambda d: d["in_set"].__setitem__("duplicate_sha256_groups", 4)),
    "G14": ("lanes/C/METHOD_DEPENDENCE.json", lambda d: d["V02"].__setitem__("max_overall", 0.0)),
    "G15": ("lanes/B/TREE_IDENTITY.json",
            lambda d: d["subjects"][0]["licences"]["claim"].__setitem__("scope_note", "measured somewhere")),
    "G16a": ("lanes/B/TREE_IDENTITY.json",
             lambda d: [x.__setitem__("declared_covers_imports", not x["declared_covers_imports"]) for x in d["subjects"]]),
    "G17": ("lanes/E/WP21_ENUM_V3.json", lambda d: d["denominators"]["seam"].__setitem__("measured", 10)),
    "G18": (lambda ctx: _first_manifest(ctx), lambda d: d["files"][0].__setitem__("sha256", "0" * 64)),
    "G19": ("lanes/D/COPY_REGISTER_ALL.json",
            lambda d: d["names_exact"][0]["members"][0].__setitem__("sha256", "0" * 64)),
    "G20": ("lanes/D/WP19_V3.json", lambda d: d["supply_chain_claim"].__setitem__("claim_shape", "both halves are the same thing")),
    "G16b": ("out/DEPENDENCY_SUBJECTS.json",
             lambda d: next(x for x in d["subjects"] if x.get("metadata_files")).__setitem__("scan_complete", False)),
    "G26": ("receipts/W0-RCPT-WP-FHS-00.json",
            lambda d: d["evidence_refs"][0].__setitem__("sha256", "0" * 64)),
    "G24": (_report_target, "text"),
    "G25": ("evidence/EXTRA_QUALIFICATION.json",
            lambda d: d["subjects"][0]["extras_declared"].append("yaml")),
    "G16c": ("evidence/DEPENDENCY_SEMANTICS.json",
             lambda d: next(iter(d["verdicts"].values())).__setitem__("classification", "PROVIDED")),
    "G21": (lambda ctx: os.path.relpath(ctx.handover_abs(), ctx.round_dir).replace(os.sep, "/"), "text"),
    "G23": ("writeback/W0/W0_CLOSEOUT_DECISION.json", lambda d: d["defects"].__setitem__("X-99", "CLOSED")),
}

# Two checks cannot be mutated from inside this program: G21/G22 read the handover, which names a
# digest that changes every time this file is rebuilt, and G22 re-invokes this program to learn the
# real exit code.  They are exempted by name, with the reason printed, rather than silently counted
# as passing.
SELFTEST_EXEMPT = {
    # G21 used to be exempt "because mutating the handover would invalidate the run"; with an in-process
    # overlay nothing is written, so the excuse evaporated (an independent lane counted it: 15/16 BLOCKING
    # FIRED). It now mutates the handover's byte claim in memory and must FIRED like every other check.
    "G22": "learns the exit code by invoking this program; a mutation inside it would recurse",
}
# G16b/G16c are REPORTING and their baseline depends on the world (three checkouts), so a mutation
# that makes them fire is not always available.  They are mutated when possible and counted as
# BASELINE_RED otherwise — never described as "exempt", which is what the previous round's handover
# did while the code was actually taking a different branch.


def _first_manifest(ctx: Ctx) -> str:
    """Locate the manifest to mutate without hard-coding a round name or a layout."""
    roots = [os.path.join(ctx.round_dir, "out", "stage")]
    if ctx.profile == "payload":
        roots.insert(0, ctx.round_dir)
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
            if "MANIFEST.json" in filenames:
                return os.path.relpath(os.path.join(dirpath, "MANIFEST.json"), ctx.round_dir).replace(os.sep, "/")
    return "out/stage/MANIFEST.json"


def _fingerprint_rows(root: str, exclude: tuple = ()) -> dict:
    """rel path -> "size|mtime_ns", the rows behind tree_fingerprint (kept so a diff can name the paths)."""
    rows = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in {"__pycache__", ".git"})
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            try:
                st = os.stat(full)
            except OSError:
                continue
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if rel in exclude:
                continue
            rows[rel] = str(st.st_size) + "|" + str(st.st_mtime_ns)
    return rows


def tree_fingerprint(root: str, exclude: tuple = ()) -> str:
    """A digest over every path, size and mtime_ns under `root` (no file contents read).

    This is what lets the selftest say "the round tree is unchanged" as a measurement rather than a
    promise: the checker asked whether the mutation had been restored, and the honest answer for a
    read-only-safe selftest is that nothing was ever written.
    """
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in {"__pycache__", ".git"})
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            try:
                st = os.stat(full)
            except OSError:
                continue
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if rel in exclude:
                continue   # the run's own report: a file whose content depends on the run cannot be an input to it
            rows.append(rel + "|" + str(st.st_size) + "|" + str(st.st_mtime_ns))
    return hashlib.sha256(chr(10).join(rows).encode("utf-8")).hexdigest()


def mutated_bytes(path: str, data: bytes):
    """Serve `data` for reads of `path` for the duration of the block; write nothing anywhere.

    r20 first tried a copy of the round into %TEMP% and measured why that fails: under
    `codex exec --sandbox read-only` there is **no usable temporary directory at all** (tempfile raises
    FileNotFoundError for every candidate). A mutation only has to change the bytes a check reads, so an
    in-process read overlay is both sufficient and the only form that survives the sandbox the checker
    actually runs in. Nothing is written, so there is nothing to restore.
    """
    import builtins
    import contextlib
    import io
    target = os.path.normcase(os.path.abspath(path))
    real_open = builtins.open

    def fake_open(file, mode="r", *a, **k):
        try:
            same = os.path.normcase(os.path.abspath(str(file))) == target
        except Exception:  # noqa: BLE001  (a file object or an int fd: not our business)
            same = False
        if same and not any(c in mode for c in "wax+"):
            if "b" in mode:
                return io.BytesIO(data)
            return io.StringIO(data.decode("utf-8", "replace"))
        return real_open(file, mode, *a, **k)

    @contextlib.contextmanager
    def _ctx():
        builtins.open = fake_open
        try:
            yield
        finally:
            builtins.open = real_open

    return _ctx()


def g28_machine_readable_qualifier(ctx: Ctx):
    """BLOCKING: the qualifier rule must reach machine-readable metadata, not only the markdown.

    r19's rule read the document and three JSON keys. A JSON consumer never sees the document, and
    `body.kind = "original_reader_ack"` plus a prose `consequence` field were enough for a reader to
    conclude that the traditional per-domain acknowledgement had been obtained.
    """
    import importlib.util as _iu
    p = os.path.join(ctx.round_dir, "tools", "label_discipline.py")
    if not os.path.isfile(p):
        return False, "CHECKER_ABSENT", "label_discipline.py is not shipped with the round"
    spec = _iu.spec_from_file_location("label_discipline_g28", p)
    m = _iu.module_from_spec(spec)
    spec.loader.exec_module(m)
    bad, excluded = m.scan_json(ctx.round_dir)
    if bad:
        return False, "BARE_ORIGINAL_ACK_IN_MACHINE_READABLE", json.dumps(bad[:3], ensure_ascii=False)[:400]
    scope = m.scan_scope(ctx.round_dir) if hasattr(m, "scan_scope") else {}
    return True, "", ("0 bare sites across " + str(scope.get("scanned_files", "n/a"))
                      + " scanned json artefact(s); " + str(len(excluded)) + " exclusion(s) carry a reason")


def selftest(ctx: Ctx, verbose: bool = True, scope: str = "full") -> int:
    results = []
    failed = 0
    depth = os.environ.get("FHS_SELFTEST_DEPTH") == "1"
    skip = set()
    if scope == "payload":
        skip = {"G11", "G13", "G16a", "G16b", "G19", "G26"}
    # every mutation is applied to an in-process read overlay, never to the candidate: `--sandbox
    # read-only` must be able to run this, because the checker is the party it exists for.
    orig_root = ctx.round_dir
    global _BEFORE_ROWS
    _self_report = ("out/GATE_R20_SELFTEST.json",)
    _BEFORE_ROWS = _fingerprint_rows(orig_root, _self_report)
    before_fp = tree_fingerprint(orig_root, _self_report)
    for cid, name, sev, fn in CHECKS:
        if cid in skip:
            continue
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
            if callable(rel):
                rel = rel(ctx)
            path = ctx.path(rel)
            if not os.path.isfile(path):
                entry["mutated"] = "MUTATION_TARGET_ABSENT"
                failed += 1
                results.append(entry)
                continue
            orig_b = open(path, "rb").read()
            try:
                if mut == "text":
                    # documents are not JSON: corrupt the first plausible byte count in place
                    new_text, n = re.subn(r"([\d][\d,]{3,})(\s*(?:bytes|B)\b)",
                                          lambda mm: "9,999,999" + mm.group(2),
                                          orig_b.decode("utf-8", "replace"), count=1)
                    if n == 0:
                        entry["mutated"] = "MUTATION_TARGET_HAS_NO_NUMBER"
                        failed += 1
                        results.append(entry)
                        continue
                    new_b = new_text.encode("utf-8")
                else:
                    d = json.loads(orig_b.decode("utf-8"))
                    mut(d)
                    new_b = json.dumps(d, ensure_ascii=False).encode("utf-8")
                with mutated_bytes(path, new_b):
                    m = fn(ctx)
                entry["mutated"] = "FIRED" if m[0] is False else "DID_NOT_FIRE"
                entry["mutated_code"] = m[1]
            except Exception as e:  # noqa: BLE001
                entry["mutated"] = f"ERROR:{e.__class__.__name__}: {e}"
            if entry["mutated"] != "FIRED":
                failed += 1
        elif cid == "G29":
            # in-memory mutation: turn one of the two valid votes into an abstention, in the first receipt
            # that carries a repaired property. A quorum rule that cannot be made to fail by removing a vote
            # is not a quorum rule.
            import glob as _g
            victims = sorted(_g.glob(os.path.join(ctx.round_dir, "receipts", "reader", "*.signed.json")))
            target, mutated = None, None
            for v in victims:
                try:
                    env = json.loads(open(v, encoding="utf-8").read())
                except Exception:  # noqa: BLE001
                    continue
                body = env.get("body") or {}
                for c in body.get("clauses") or []:
                    for name, prop in (c.get("preservation") or {}).items():
                        if prop.get("votes_r25"):
                            prop["votes_r25"][0]["vote"] = "UNKNOWN"
                            target, mutated = v, json.dumps(env, ensure_ascii=False).encode("utf-8")
                            break
                    if target:
                        break
                if target:
                    break
            if target is None:
                entry["mutated"] = "MUTATION_TARGET_ABSENT"
                failed += 1
            else:
                try:
                    with mutated_bytes(target, mutated):
                        m = fn(ctx)
                    entry["mutated"] = "FIRED" if m[0] is False else "DID_NOT_FIRE"
                    entry["mutated_code"] = m[1]
                except Exception as e:  # noqa: BLE001
                    entry["mutated"] = "ERROR:" + e.__class__.__name__ + ": " + str(e)
                if entry["mutated"] != "FIRED":
                    failed += 1
        elif cid == "G28":
            # machine-readable mutation: put a bare claim back into an artefact the scan actually reads.
            # A new file under out/ would be out of scope (out/SCAN_SCOPE.json lists what is read), and a
            # mutation outside the scope proves nothing - the first r20 selftest reported DID_NOT_FIRE for
            # exactly that reason. The probe is written into the copy, never into the candidate.
            probe = None
            for rel in ("out/PRINCIPAL_DEFINITION.json", "evidence/PRINCIPAL_DEFINITION.json"):
                cand = ctx.path(rel)
                if os.path.isfile(cand):
                    probe = cand
                    break
            if probe is None:
                entry["mutated"] = "MUTATION_TARGET_ABSENT"
                failed += 1
                results.append(entry)
                continue
            try:
                d = json.loads(open(probe, "rb").read().decode("utf-8"))
                d["consequence"] = "ORIGINAL_ACK 6/6 may be issued by the reader role"
                with mutated_bytes(probe, json.dumps(d, ensure_ascii=False).encode("utf-8")):
                    m = fn(ctx)
                entry["mutated"] = "FIRED" if m[0] is False else "DID_NOT_FIRE"
                entry["mutated_code"] = m[1]
            except Exception as e:  # noqa: BLE001
                entry["mutated"] = "ERROR:" + e.__class__.__name__ + ": " + str(e)
            if entry["mutated"] != "FIRED":
                failed += 1
        elif cid == "G27":
            # text-level mutation on the document: append the exact sentence this rule exists to refuse.
            # No exemption: a label rule whose bite is only proven by a different tool is not enforcement.
            global _G27_TEXT_OVERRIDE
            docp = ctx.path(ctx.doc_rel())
            orig_doc = open(docp, "rb").read()
            try:
                # in-memory only: nothing is written, so --sandbox read-only can run this too
                _G27_TEXT_OVERRIDE = orig_doc.decode("utf-8", "replace") + "\r\n| 已取得 ORIGINAL_ACK 6/6 |\r\n"
                m = fn(ctx)
                entry["mutated"] = "FIRED" if m[0] is False else "DID_NOT_FIRE"
                entry["mutated_code"] = m[1]
            except Exception as e:  # noqa: BLE001
                entry["mutated"] = f"ERROR:{e.__class__.__name__}: {e}"
            finally:
                _G27_TEXT_OVERRIDE = None
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
    after_fp = tree_fingerprint(orig_root, _self_report)
    unchanged = after_fp == before_fp
    changed = []
    if not unchanged:
        after_rows = _fingerprint_rows(orig_root, _self_report)
        changed = sorted(set(_BEFORE_ROWS) ^ set(after_rows)) + [
            k for k in sorted(set(_BEFORE_ROWS) & set(after_rows)) if _BEFORE_ROWS[k] != after_rows[k]]
        failed += 1
    sys.stdout.write(json.dumps({"schema": "FHS.W0.GateSelftest/4", "results": results,
                                 "mutation_mechanism": "in_process_read_overlay (mutated_bytes)",
                                 "mutation_root": None, "wrote_inside_round": False,
                                 "round_tree_unchanged": unchanged,
                                 "changed_paths": changed[:20],
                                 "round_tree_fingerprint_before": before_fp,
                                 "round_tree_fingerprint_after": after_fp},
                                ensure_ascii=False) + "\n")
    return 0 if failed == 0 else 1



# ------------------------------------------------------------------------------------------------
# hygiene

HYGIENE_EXEMPT = {
    "lanes/A/evidence/fixtures/c3/dist/c3_optional_extra_demo-0.0.1-py3-none-any.whl":
        ("G25 optional-extra positive control: a genuine 1,648-byte wheel built by the fixture, shipped in r22 "
         "and re-hashed by G25; removing it would delete the control rather than clean the round"),
}


def hygiene(root: str) -> list[dict]:
    """Walk the round. A path in HYGIENE_EXEMPT is still printed, as its own finding kind, but it is not a
    hygiene failure: the report shows what was exempted and why instead of hiding it."""
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
                if rel in HYGIENE_EXEMPT:
                    findings.append({"path": rel, "why": "EXEMPT_WITH_REASON", "reason": HYGIENE_EXEMPT[rel],
                                     "counts_as_clean": True})
                else:
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


def g26_receipt_binding(ctx: Ctx):
    """Every receipt's evidence binding must name bytes that exist now.

    Round-5 officer finding: the six receipts bound out/GATE_R19.json by a digest captured before the
    gate was re-run, so they authenticated a report that was no longer the shipped one. A binding that
    is never re-checked is a comment."""
    rdir = os.path.join(ctx.round_dir, "receipts")
    if not os.path.isdir(rdir):
        return False, "RECEIPTS_ABSENT", "no receipts directory"
    files = sorted(f for f in os.listdir(rdir) if f.startswith("W0-RCPT-") and f.endswith(".json"))
    if len(files) != 6:
        return False, "RECEIPT_COUNT", f"{len(files)} receipts, expected 6"
    doc_sha = sha_file(ctx.path(ctx.doc_rel()))
    checked, bad = 0, []
    for f in files:
        r = json.load(open(os.path.join(rdir, f), encoding="utf-8"))
        for key in ("subject", "source_sha", "candidate_sha", "scope", "host", "policy_epoch", "original_consumer"):
            if key not in r:
                bad.append((f, "FIELD_ABSENT", key))
        cs = (r.get("candidate_sha") or {}).get("value")
        if cs != doc_sha:
            # The owner-signed candidate may be a byte-exact prefix of a record-only revision. Accept it
            # only when a manifest entry proves the prefix: same digest and the delivered file starts with
            # exactly that many bytes hashing to it.
            accepted = False
            try:
                rm = ctx.load("writeback/W0/W0_REVISION_MANIFEST.json")
                for e in rm.get("chain", []):
                    if e.get("sha256") == cs and isinstance(e.get("bytes"), int):
                        head = open(ctx.path(ctx.doc_rel()), "rb").read(e["bytes"])
                        if hashlib.sha256(head).hexdigest() == cs:
                            accepted = True
                            break
            except Exception:
                accepted = False
            if not accepted:
                bad.append((f, "CANDIDATE_DIGEST_STALE", f"{str(cs)[:12]} != {doc_sha[:12]} and is not a proven prefix"))
        if r.get("status") not in ("OWNER_READER_ACK_PENDING", "OWNER_SEMANTIC_ACK"):
            bad.append((f, "STATUS_NOT_A_PENDING_OR_SIGNED_STATE", r.get("status")))
        for ev in r.get("evidence_refs") or []:
            rel = ev.get("path")
            want = ev.get("sha256")
            cand = ctx.path(rel) if not os.path.isabs(rel) else rel
            if not os.path.isfile(cand):
                bad.append((f, "EVIDENCE_ABSENT", rel))
                continue
            got = sha_file(cand)
            checked += 1
            if got != want:
                bad.append((f, "EVIDENCE_DIGEST_STALE", f"{rel}: {str(want)[:12]} != {got[:12]}"))
    if bad:
        return False, "RECEIPT_BINDING_BROKEN", json.dumps(bad[:4], ensure_ascii=False)
    return True, "OK", f"{len(files)} receipts; 7 fields present; candidate digest matches; {checked} evidence binding(s) re-hashed"


_G27_TEXT_OVERRIDE = None


def g27_label_discipline(ctx: Ctx):
    """A positive ORIGINAL_ACK claim must carry the FHS_ qualifier, or be explicitly not claimed.

    The whole value of the qualified label is that it is not the traditional one. If the qualifier can be
    dropped without anything failing, the claim decays into a false statement within one retelling.
    """
    import importlib.util as _iu
    p = os.path.join(ctx.round_dir, "tools", "label_discipline.py")
    if not os.path.isfile(p):
        return False, "CHECKER_ABSENT", "label_discipline.py is not shipped with the round"
    spec = _iu.spec_from_file_location("label_discipline", p)
    m = _iu.module_from_spec(spec)
    spec.loader.exec_module(m)
    # a read-only officer cannot write the document, so the mutation arrives as text. It is carried in a
    # module global, not in an environment variable: the document is ~621 KB and Windows truncates an env
    # value at 32767 characters, which surfaced as `ERROR:ValueError` in the r20 selftest run.
    text = _G27_TEXT_OVERRIDE or os.environ.get("FHS_G27_TEXT")
    if text is None:
        text = open(ctx.path(ctx.doc_rel()), encoding="utf-8", errors="replace").read()
    bad = m.scan(text)
    if bad:
        return False, "BARE_ORIGINAL_ACK_CLAIM", f"{len(bad)} bare claim(s), first at line {bad[0]['line']}: {bad[0]['text'][:90]}"
    return True, "", "no bare ORIGINAL_ACK claim; the qualified label holds"



def g29_signed_vote_quorum(ctx: Ctx):
    """BLOCKING: a signed preservation decision needs two valid, distinct, same-candidate votes.

    The r24 external challenge found two signed `DECIDED=true` decisions backed by one agreeing vote, and the
    verifier never asked. `tools/verify_quorum.py` is that predicate; this check makes it bite inside the gate.
    """
    import importlib.util as _iu
    p = os.path.join(ctx.round_dir, "tools", "verify_quorum.py")
    if not os.path.isfile(p):
        return False, "CHECKER_ABSENT", "verify_quorum.py is not shipped with the round"
    spec = _iu.spec_from_file_location("verify_quorum_g29", p)
    m = _iu.module_from_spec(spec)
    spec.loader.exec_module(m)
    rep = m.scan_receipts(ctx.round_dir)
    if not rep["ok"]:
        return False, rep["findings"][0].get("first_fail") or "SIGNED_VOTE_QUORUM_FAIL", \
            json.dumps(rep["findings"][:3], ensure_ascii=False)[:400]
    return True, "", (str(rep["properties_checked"]) + " preservation properties across "
                      + str(rep["receipts"]) + " signed envelope(s); every DECIDED one has >=2 agreeing valid votes")


CHECKS = [
    ("G10", "CHAIN_INTEGRITY", "BLOCKING", g10_chain_integrity),
    ("G11", "LINE_CONVENTION", "BLOCKING", g11_line_convention),
    ("G12", "SEGMENTATION_RULE", "BLOCKING", g12_segmentation_rule),
    ("G13", "COUNT_SCOPE", "BLOCKING", g13_count_scope),
    ("G14", "MAXIMUM_IS_GLOBAL", "BLOCKING", g14_maximum_is_global),
    ("G15", "LICENCE_LAYER", "BLOCKING", g15_licence_layer),
    ("G16a", "DEPENDENCY_TRUTHFUL", "BLOCKING", g16a_dependency_truthful),
    ("G16b", "DEPENDENCY_CLOSED", "REPORTING", g16b_dependency_closed),
    ("G16c", "OPTIONAL_SEMANTICS", "REPORTING", g16c_optional_semantics),
    ("G17", "ENUM_SLASH_SAFE", "BLOCKING", g17_enum_slash_safe),
    ("G18", "DIGEST_LOCALITY", "BLOCKING", g18_digest_locality),
    ("G19", "COPY_REGISTER", "BLOCKING", g19_copy_register),
    ("G20", "SUPPLY_CHAIN_CLAIM_SHAPE", "REPORTING", g20_supply_chain_split),
    ("G21", "NUMBER_CONSISTENCY", "BLOCKING", g21_number_consistency),
    ("G22", "SELFTEST_CONTRACT", "REPORTING", g22_selftest_contract),
    ("G23", "TRACE_ID_NAMED", "BLOCKING", g23_trace_ids),
    ("G24", "IDENTITY_CLAIMS", "BLOCKING", g24_identity_claims),
    ("G25", "EXTRA_QUALIFIED", "REPORTING", g25_extra_qualified),
    ("G26", "RECEIPT_BINDING", "BLOCKING", g26_receipt_binding),
    ("G27", "LABEL_DISCIPLINE", "BLOCKING", g27_label_discipline),
    ("G28", "MACHINE_READABLE_QUALIFIER", "BLOCKING", g28_machine_readable_qualifier),
    ("G29", "SIGNED_VOTE_QUORUM", "BLOCKING", g29_signed_vote_quorum),
]




def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=".")
    ap.add_argument("--json", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--prior", default=None, help="accepted for symmetry; v4 has no prior mode because every check reads artifacts that did not exist before r10")
    ap.add_argument("--sources", default=None, help="the 31 source documents, so G11 can re-hash them instead of trusting the artefact")
    ap.add_argument("--scope", choices=("full", "payload"), default="full",
                    help="payload scope runs only the checks a payload can verify from its own bytes, and lists the exclusions")
    ap.add_argument("--profile", choices=("round", "payload"), default="round",
                    help="'payload' resolves artifacts by the names the published payload uses, so CI can run this file from inside it")
    ap.add_argument("--skip-hygiene", action="store_true")
    a = ap.parse_args()
    ctx = Ctx(a.round, a.prior, a.profile, a.sources)
    ctx.scope = a.scope

    if a.selftest:
        return selftest(ctx, verbose=not a.quiet, scope=a.scope)

    # A payload cannot verify what it does not carry. Rather than let those checks pass by default,
    # payload scope removes them from the run and names them in the output.
    payload_scope_excluded = {
        "G11": "the 31 source documents are not shipped; re-hashing them needs the corpus",
        "G13": "same corpus as G11: the in-set zeros are re-derived from the files",
        "G16a": "two of three dependency subjects are checkouts outside the payload; only identity is checkable",
        "G16b": "same reason as G16a; coverage of external trees cannot be recomputed here",
        "G19": "the copy register describes four roots outside the payload",
        "G26": "receipts bind the round layout; the payload ships them but not the gate report they cite",
    }
    run_checks = CHECKS
    excluded = []
    if a.scope == "payload":
        run_checks = [c for c in CHECKS if c[0] not in payload_scope_excluded]
        excluded = [{"check": k, "why": v} for k, v in payload_scope_excluded.items()]

    hy = [] if a.skip_hygiene else hygiene(ctx.round_dir)
    results = []
    for cid, name, sev, fn in run_checks:
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
        "schema": "FHS.W0.Gate/6",
        "gate": "GSTACK v6",
        "round": ctx.round_dir.replace("\\", "/"),
        "generated_at": now(),
        "checks": results,
        "summary": {"total": len(results), "pass": passed, "blocking_fail": len(blocking_fail),
                    "open_reporting_findings": len(open_findings)},
        "hygiene": {"count": len([x for x in hy if not x.get("counts_as_clean")]),
                    "exempted": len([x for x in hy if x.get("counts_as_clean")]), "findings": hy},
        "scope": a.scope,
        "excluded_in_this_scope": excluded,
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
    print(f"\nVERDICT {'PASS' if not blocking_fail and not [x for x in hy if not x.get('counts_as_clean')] else 'FAIL'} "
          f"pass={passed}/{len(results)} blocking_fail={len(blocking_fail)} open_reporting={len(open_findings)} hygiene={len([x for x in hy if not x.get('counts_as_clean')])}")
    if open_findings:
        print("open findings (reported, not gating):")
        for r in open_findings:
            print(f"  - {r['check']} {r['code']}: {r['detail'][:140]}")
    if [x for x in hy if not x.get('counts_as_clean')]:
        return 3
    if any(r["verdict"] == "ABSENT" for r in results if r["severity"] == "BLOCKING"):
        return 2
    return 0 if not blocking_fail else 1


if __name__ == "__main__":
    sys.exit(main())
