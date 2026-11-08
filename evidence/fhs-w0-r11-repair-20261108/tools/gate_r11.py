#!/usr/bin/env python3
"""GSTACK v4 — v3 plus the three false-green paths the external review found in v3 itself.

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
    def __init__(self, round_dir: str, prior_dir: str | None = None, profile: str = "round"):
        self.round_dir = os.path.abspath(round_dir)
        self.prior_dir = os.path.abspath(prior_dir) if prior_dir else None
        self.profile = profile

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
        cands = sorted(f for f in os.listdir(self.round_dir) if f.startswith("HANDOVER_R")) if os.path.isdir(self.round_dir) else []
        return os.path.join(self.round_dir, cands[-1]) if cands else os.path.join(self.round_dir, f"HANDOVER_R{v}_2026-11-08.md")

    def path(self, rel: str) -> str:
        direct = os.path.join(self.round_dir, rel.replace("/", os.sep))
        if os.path.exists(direct) or self.profile != "payload":
            return direct
        alt = PAYLOAD_ALIASES.get(rel)
        return os.path.join(self.round_dir, alt.replace("/", os.sep)) if alt else direct

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
            if any(want.get(k) and got.get(k) and want[k] != got[k] for k in want):
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
        expected = doc.get("expected_entry_set")
        if not isinstance(expected, list) or not expected:
            return False, "EXPECTED_ENTRY_SET_ABSENT", f"{os.path.basename(mdir)}: the payload does not declare expected_entry_set"
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
    if by_v[pred].get("sha256") != declared:
        return False, "PARENT_IS_NOT_ITS_OWN_PARENT", f"doc declares {declared[:16]} but manifest {pred} is {str(by_v[pred].get('sha256'))[:16]}"
    external = []
    resolved = {}
    _order = [c["version"] for c in chain]
    for v in _order:
        ent = by_v[v]
        p = ent.get("path") or f"FHS_PIPD-LS-PKG_W0_{v}.md"
        # the last version is the document under test: resolve it where it actually is, not by the
        # absolute path the manifest recorded on the machine that built it
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
    if _shipped_identity(ctx):
        ok_bytes.add(_shipped_identity(ctx)[0])
    claims = [int(x.replace(",", "")) for x in re.findall(rf"FHS_PIPD-LS-PKG_W0_{ver}\.md[^\n]{{0,200}}?([\d][\d,]{{3,}})\s*(?:bytes|B)", txt)]
    stale = sorted({c for c in claims if c not in ok_bytes})
    if not claims:
        return False, "CLAIM_NOT_FOUND", "the handover states no byte count for this version"
    if stale:
        return False, "HANDOVER_BYTES_DISAGREE", f"stale={stale} measured={sorted(ok_bytes)}"
    sm = re.search(rf"FHS_PIPD-LS-PKG_W0_{ver}\.md[^\n]{{0,240}}?`([0-9a-f]{{64}})`", txt)
    if not sm:
        return False, "CLAIM_NOT_FOUND", "the handover does not state the document digest"
    ok_sha = {sha_file(doc)}
    if _shipped_identity(ctx):
        ok_sha.add(_shipped_identity(ctx)[1])
    if sm.group(1) not in ok_sha:
        return False, "HANDOVER_SHA_DISAGREE", f"claimed={sm.group(1)[:12]} measured={[x[:12] for x in sorted(ok_sha)]}"
    return True, "OK", f"handover states {sorted(ok_bytes)[-1]:,} B (and no stale size) with a matching digest"


def g22_selftest_contract(ctx: Ctx):
    """The documented exit code must be the one this gate actually returns."""
    handover = ctx.handover_abs()
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
    ("G22", "SELFTEST_CONTRACT", "BLOCKING", g22_selftest_contract),
    ("G23", "TRACE_ID_NAMED", "BLOCKING", g23_trace_ids),
]


def run_selftest(ctx: Ctx) -> int:
    """Ask the program what its own selftest returns.  The child runs with depth=1 so that G22 does
    not spawn a grandchild; G22 contributes nothing to the exit code either way, so the depth-1
    answer is the answer."""
    import subprocess
    env = dict(os.environ, FHS_SELFTEST_DEPTH="1")
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--round", ctx.round_dir,
                        "--profile", ctx.profile, "--selftest", "--quiet"],
                       capture_output=True, text=True, env=env, timeout=180)
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
            lambda d: d["r6_focus"].__setitem__("copies", 2) or d["r6_focus"].__setitem__("members", d["r6_focus"]["members"][:2])),
    "G20": ("lanes/D/WP19_V3.json", lambda d: d["supply_chain_claim"].__setitem__("claim_shape", "both halves are the same thing")),
    "G16b": ("out/DEPENDENCY_SUBJECTS.json",
             lambda d: next(x for x in d["subjects"] if x.get("metadata_files")).__setitem__("scan_complete", False)),
    "G16c": ("evidence/DEPENDENCY_SEMANTICS.json",
             lambda d: next(iter(d["verdicts"].values())).__setitem__("classification", "PROVIDED")),
    "G23": ("writeback/W0/W0_CLOSEOUT_DECISION.json", lambda d: d["defects"].__setitem__("X-99", "CLOSED")),
}

# Two checks cannot be mutated from inside this program: G21/G22 read the handover, which names a
# digest that changes every time this file is rebuilt, and G22 re-invokes this program to learn the
# real exit code.  They are exempted by name, with the reason printed, rather than silently counted
# as passing.
SELFTEST_EXEMPT = {
    "G21": "reads the handover that documents this run; mutating it would invalidate the run it is part of",
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
            if callable(rel):
                rel = rel(ctx)
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
    ap.add_argument("--prior", default=None, help="accepted for symmetry; v4 has no prior mode because every check reads artifacts that did not exist before r10")
    ap.add_argument("--profile", choices=("round", "payload"), default="round",
                    help="'payload' resolves artifacts by the names the published payload uses, so CI can run this file from inside it")
    ap.add_argument("--skip-hygiene", action="store_true")
    a = ap.parse_args()
    ctx = Ctx(a.round, a.prior, a.profile)

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
        "schema": "FHS.W0.Gate/4",
        "gate": "GSTACK v4",
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
