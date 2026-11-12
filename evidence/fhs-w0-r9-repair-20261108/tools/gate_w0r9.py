#!/usr/bin/env python3
"""GSTACK v2 — the W0 invariant gate after the implementation repair (round r9).

What is new here, and why
-------------------------
The verification round found seven defects that the previous gate could not see, because every
one of them is a *relation between a published number and the rule that produced it*. The old
gate recomputed digests and re-sliced spans; it never asked "which rule made this count", "which
set was this count taken over", "is this maximum the maximum of the whole set", or "does this
digest resolve inside the payload that declares it".

So this gate adds one check per repaired invariant:

  G11 LINE_CONVENTION          one line convention, and the verdict covers the line field
  G12 SEGMENTATION_RULE        two named rules, both tile the bytes, both counts published
  G13 COUNT_SCOPE              every count carries the set it was counted over
  G14 MAXIMUM_IS_GLOBAL        a published maximum is the maximum of the whole set
  G15 LICENCE_LAYER            a licence claim carries its layer (root vs nested)
  G16 DECLARED_COVERS_IMPORTS  declared dependencies cover the modules actually imported
  G17 ENUM_SLASH_SAFE          identifier parsing survives punctuation inside the row
  G18 DIGEST_LOCALITY          every manifest digest resolves inside its own payload
  G19 COPY_REGISTER            a name with several copies is resolved by digest, canonical = owner
  G20 SUPPLY_CHAIN_SPLIT       offline-reproducible and hosted-conclusion are separate claims

Three modes:
  --round <dir>            gate the repaired artifacts
  --prior <dir>            run the same checks against the pre-repair artifacts (must be red where
                           the defect was present, and the report says which are not applicable)
  --selftest               for every check: prove the pass on the real artifact, then mutate the
                           artifact in memory and require the named code to fire

Exit codes: 0 pass, 1 at least one check failed, 2 fail-closed (a required artifact is absent),
            3 hygiene refusal (oversize/binary/token-shaped artifact in the deliverable).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
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


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class Ctx:
    def __init__(self, mode: str, round_dir: str, prior_dir: str | None):
        self.mode = mode
        self.round_dir = os.path.abspath(round_dir)
        self.prior_dir = os.path.abspath(prior_dir) if prior_dir else None

    def path(self, rel_r9: str, rel_prior: str | None = None) -> str:
        base = self.round_dir if self.mode == "r9" else (self.prior_dir or self.round_dir)
        rel = rel_r9 if self.mode == "r9" else (rel_prior or rel_r9)
        return os.path.join(base, rel.replace("/", os.sep))

    def load(self, rel_r9: str, rel_prior: str | None = None):
        p = self.path(rel_r9, rel_prior)
        if not os.path.isfile(p):
            raise FileNotFoundError(p)
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)


# --------------------------------------------------------------------------------------------------
# helpers


def walk_numbers(obj, prefix=""):
    """Yield (path, value) for every number in a nested structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_numbers(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_numbers(v, f"{prefix}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield prefix, float(obj)


def find_manifest_files(root: str) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for fn in filenames:
            if fn in {"MANIFEST.json", "PROVENANCE.json"}:
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def verify_manifest_locality(manifest_path: str) -> tuple[int, int, list[dict]]:
    """Return (resolved, declared, problems). A digest must resolve against bytes in the same dir tree."""
    with open(manifest_path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    entries = doc.get("files") or doc.get("entries") or doc.get("artifacts") or []
    if isinstance(entries, dict):
        entries = [{"path": k, "sha256": v} for k, v in entries.items()]
    base = os.path.dirname(manifest_path)
    resolved = 0
    problems = []
    for e in entries:
        if not isinstance(e, dict):
            problems.append({"entry": str(e)[:80], "why": "NOT_AN_OBJECT"})
            continue
        p = e.get("path") or e.get("file") or e.get("artifact")
        declared = e.get("sha256") or e.get("digest")
        if not p or not declared:
            problems.append({"entry": json.dumps(e, ensure_ascii=False)[:120], "why": "NO_PATH_OR_DIGEST"})
            continue
        fp = os.path.normpath(os.path.join(base, p))
        if not fp.startswith(base):
            # resolves only by leaving this payload
            problems.append({"entry": p, "why": "PATH_OUTSIDE_PAYLOAD"})
            continue
        if not os.path.isfile(fp):
            problems.append({"entry": p, "why": "ABSENT_IN_PAYLOAD"})
            continue
        if str(declared).startswith("sha256:"):
            declared = str(declared).split(":", 1)[1]
        actual = sha256_file(fp)
        if actual != declared:
            problems.append({"entry": p, "why": "SHA_MISMATCH", "declared": str(declared)[:16], "actual": actual[:16]})
            continue
        resolved += 1
    return resolved, len(entries), problems


# --------------------------------------------------------------------------------------------------
# checks: each returns (ok: bool, code: str, detail: str)


def g11_line_convention(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/A/SOURCE_LOCK_V2.json")
        recs = a.get("sources") or a.get("records") or []

        def m(rec, key):
            inner = rec.get("match")
            if isinstance(inner, dict):
                return inner.get(key)
            if key == "sha256":
                return rec.get("sha256_match", rec.get("sha_match"))
            return rec.get(f"{key}_match")

        if len(recs) != 31:
            return False, "LINE_SOURCE_COUNT", f"expected 31 records, found {len(recs)}"
        bad = [r for r in recs if not (m(r, "lines") is True and m(r, "bytes") is True and m(r, "sha256") is True)]
        if bad:
            return False, "LINE_FIELD_FALSE", f"{len(bad)} records have a false match field; first={bad[0].get('source_id')}"
        tot = a.get("totals", {})
        d, o = tot.get("declared_lines_sum"), tot.get("observed_lines_sum")
        if not (d == 111331 and o == 111331):
            return False, "LINE_TOTAL_DISAGREES", f"declared={d} observed={o} expected 111331"
        conv = a.get("convention") or {}
        stated = bool(conv.get("chosen") or conv.get("lines_posix_definition") or conv.get("semantics_posix"))
        blob = json.dumps(conv, ensure_ascii=False).lower()
        if not stated or "newline" not in blob:
            return False, "LINE_CONVENTION_UNSTATED", "no convention block naming the newline-count semantics"
        mc = a.get("match_counts") or tot.get("match_counts") or {}
        lm = mc.get("lines", mc.get("lines_match"))
        if isinstance(lm, int) and lm != 31:
            return False, "LINE_MATCH_COUNT", f"lines match count {lm} != 31"
        return True, "OK", f"31/31 bytes+lines+sha; sums {d}/{o}; convention stated"
    # prior round
    a = ctx.load("evidence/WP00/raw/SOURCE_LOCK.json", "evidence/WP00/raw/SOURCE_LOCK.json")
    recs = a.get("sources") or []
    true_lines = sum(1 for r in recs if r.get("lines_match") is True or r.get("match", {}).get("lines") is True)
    verdict = str(a.get("counts", {}).get("match", "")) + "/" + str(a.get("counts", {}).get("declared", ""))
    if true_lines != len(recs):
        return False, "LINE_CONVENTION_INCONSISTENT", (
            f"{true_lines}/{len(recs)} line fields true while counts say {verdict}: a verdict that omits the field it prints")
    return True, "OK", f"{true_lines}/{len(recs)} line fields true"


def g12_segmentation_rule(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/B/U0_PARTITION_V2.json")
        tot = a.get("totals", {})
        per, st = tot.get("per_line_segments_sum"), tot.get("structural_blocks_sum")
        if per != 111331:
            return False, "PER_LINE_SUM", f"per_line total {per} != 111331"
        if not st or st <= 0:
            return False, "STRUCTURAL_COUNT_ABSENT", f"structural total {st!r}"
        if st == per:
            return False, "RULES_COLLAPSED", f"both rules report {st}: they are not two rules"
        if not tot.get("all_tile_exactly"):
            return False, "TILING_FAILED", "all_tile_exactly is not true"
        sem = a.get("rule_semantics", {})
        text = json.dumps(sem, ensure_ascii=False).lower()
        if "per_line" not in text or "structural" not in text:
            return False, "RULE_SEMANTICS_ABSENT", "rule_semantics does not name both rules"
        files = a.get("files") or []
        not_tiled = [f.get("source_id") for f in files if not (f.get("tiles_exactly", {}).get("per_line") and f.get("tiles_exactly", {}).get("structural"))]
        if not_tiled:
            return False, "FILE_NOT_TILED", f"{len(not_tiled)} files fail tiling: {not_tiled[:4]}"
        return True, "OK", f"per_line={per} structural={st} files={len(files)} both rules tile"
    a = ctx.load("evidence/WP01/raw/U0_PARTITION.json", "evidence/WP01/raw/U0_PARTITION.json")
    tot = a.get("totals", {})
    if "structural_blocks" not in tot and "structural_blocks_sum" not in tot:
        return False, "SEGMENTATION_RULE_ABSENT", (
            f"only one rule published (segments={tot.get('segments')}); no structural count exists, so the number cannot be attributed")
    return True, "OK", "both counts present"


def g13_count_scope(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json")
        inb = a.get("in_set") or a.get("in_set_31")
        if not isinstance(inb, dict):
            return False, "SCOPE_BLOCK_ABSENT", "no in-set block"
        exts = [(k, a[k]) for k in ("kb_external", "kb_external_exact", "kb_external_normalised")
                if isinstance(a.get(k), dict)]
        if not exts:
            return False, "SCOPE_BLOCK_ABSENT", "no external-scope block"
        for label, blk in [("in_set", inb)] + exts:
            if not blk.get("scope"):
                return False, "COUNT_WITHOUT_SCOPE", f"block {label} carries no scope string"
        for label, blk in exts:
            if not blk.get("match_rule"):
                return False, "COUNT_WITHOUT_MATCH_RULE", f"block {label} does not state how a copy was matched to a source"
        dup_name = inb.get("duplicate_basename_groups", inb.get("duplicate_names"))
        dup_sha = inb.get("duplicate_digest_groups", inb.get("duplicate_digests"))
        if dup_name not in (0, None) or dup_sha not in (0, None):
            return False, "IN_SET_COLLISION_PRESENT", json.dumps(inb, ensure_ascii=False)[:220]
        counts = {}
        for label, blk in exts:
            v = blk.get("source_files_with_at_least_one_divergent_copy")
            if not isinstance(v, int):
                return False, "EXTERNAL_COUNT_ABSENT", f"block {label} has no integer divergent-copy count"
            counts[label] = v
        if a.get("canonical_resolution", {}).get("state") != "OWNER_UNRESOLVED":
            return False, "CANONICAL_STATE", f"canonical state {a.get('canonical_resolution', {}).get('state')!r}"
        return True, "OK", f"in-set dup=0; divergent by scope {counts}; canonical OWNER_UNRESOLVED"
    import glob
    cands = glob.glob(os.path.join(ctx.prior_dir, "evidence/WP01/**/*AUTHORITY*CONFLICT*"), recursive=True)
    if not cands:
        return None, "NO_ANALOGUE", "prior round has no authority conflict ledger file"
    a = json.load(open(cands[0], encoding="utf-8"))
    blob = json.dumps(a, ensure_ascii=False)
    if "scope" not in blob.lower():
        return False, "COUNT_WITHOUT_SCOPE", f"{os.path.basename(cands[0])} states counts with no scope field"
    return True, "OK", "scope present"


def g14_maximum_is_global(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/C/DISTINCTNESS_V2.json")
        mo = a.get("max_overall")
        if mo is None:
            return False, "MAXIMUM_NOT_PUBLISHED", "no max_overall field"
        breakdown = {}
        for k in ("max_per_method", "max_by_pair"):
            for name, v in (a.get(k) or {}).items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    breakdown[f"{k}/{name}"] = float(v)
        if not breakdown:
            return False, "MAXIMUM_UNVERIFIABLE", "no per-method or per-pair maxima to compare against"
        top = max(breakdown.values())
        if abs(top - float(mo)) > 1e-9:
            return False, "MAXIMUM_IS_NOT_GLOBAL", f"max_overall={mo} but the largest breakdown value is {top}"
        pc = a.get("prior_claim", {})
        if pc.get("value") is not None and pc.get("reproduced_as_maximum") is not False:
            return False, "PRIOR_CLAIM_NOT_DEMOTED", json.dumps(pc, ensure_ascii=False)[:200]
        nc = a.get("negative_control", {})
        fired = a.get("negative_control_bites")
        if fired is None:
            fired = nc.get("bites")
        if fired is None:
            sims = [v for v in (nc.get("similarities") or {}).values() if isinstance(v, (int, float))]
            fired = bool(sims) and max(sims) > (a.get("thresholds", {}).get("sentence_threshold") or 0.85)
        if not fired:
            return False, "NEGATIVE_CONTROL_DID_NOT_FIRE", json.dumps(nc, ensure_ascii=False)[:200]
        return True, "OK", f"max_overall={mo} equals the largest of {len(breakdown)} breakdown values; negative control fired"
    a = ctx.load("evidence/WP15/REPORT.json", "evidence/WP15/REPORT.json")
    d = a.get("distinctness", {})
    if "max_overall" not in d:
        pair_max = [p.get("max") for p in d.get("pairs", []) if isinstance(p.get("max"), (int, float))]
        return False, "MAXIMUM_NOT_PUBLISHED", (
            f"no global maximum published; largest pair value is {max(pair_max) if pair_max else None}, "
            f"yet one sub-method field ({d.get('pairs', [{}])[0].get('sentence_shingle_jaccard')}) was quoted elsewhere as the maximum")
    return True, "OK", f"max_overall={d.get('max_overall')}"


def _repo_rows(a):
    raw = a.get("repos")
    if isinstance(raw, dict):
        return [(k, v) for k, v in raw.items() if isinstance(v, dict)]
    if isinstance(raw, list):
        return [(str(r.get("repo") or r.get("label") or i), r) for i, r in enumerate(raw) if isinstance(r, dict)]
    return []


def g15_licence_layer(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/D/WP19_V2.json")
        rows = _repo_rows(a)
        if len(rows) < 3:
            return False, "LICENCE_REPO_COUNT", f"{len(rows)} repos recorded, expected 3"
        for name, r in rows:
            cl = r.get("claim")
            if not isinstance(cl, dict):
                cl = (r.get("licence") or {}).get("claim")
            if not isinstance(cl, dict):
                return False, "LICENCE_CLAIM_ABSENT", f"{name}: no claim block"
            if not isinstance(cl.get("root_licence_present"), bool):
                return False, "LICENCE_ROOT_FIELD", f"{name}: root_licence_present is not a bool"
            if not isinstance(cl.get("nested_licence_count"), int):
                return False, "LICENCE_NESTED_FIELD", f"{name}: nested_licence_count is not an int"
            if not cl.get("scope_note"):
                return False, "LICENCE_SCOPE_NOTE", f"{name}: no scope_note"
        return True, "OK", "; ".join(
            f"{n}:root={(r.get('claim') or (r.get('licence') or {}).get('claim') or {}).get('root_licence_present')}"
            f",nested={(r.get('claim') or (r.get('licence') or {}).get('claim') or {}).get('nested_licence_count')}"
            for n, r in rows)
    a = ctx.load("evidence/WP19/REPORT.json", "evidence/WP19/REPORT.json")
    bad = []
    for r in a.get("repos", []):
        v = r.get("licence")
        if isinstance(v, str) and v.strip().upper() in {"ABSENT", "NONE", "MISSING"}:
            bad.append(r.get("repo"))
    if bad:
        return False, "LICENCE_UNLAYERED_CLAIM", f"{bad} carry a bare absence string with no layer"
    return True, "OK", "no unlayered licence claim"


def g16_declared_covers_imports(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/D/WP19_V2.json")
        rows = _repo_rows(a)
        hgk = next((t for t in rows if "KSEOS" in t[0].upper() or "HGK" in t[0].upper() or "HG" in t[0].upper()), None)
        if hgk is None:
            return False, "DEPENDENCY_REPO_ABSENT", "no HG-KSEOS row"
        for name, r in rows:
            deps = r.get("dependencies") or {}
            if "declared_covers_imports" not in deps:
                return False, "DEPENDENCY_VERDICT_ABSENT", f"{name}: no declared_covers_imports"
            und = [str(u.get("module", "")).lower() for u in (deps.get("undeclared_third_party") or [])]
            verdict = deps.get("declared_covers_imports")
            if bool(verdict) != (len(und) == 0):
                return False, "DEPENDENCY_VERDICT_INCOHERENT", f"{name}: verdict={verdict} but undeclared={und}"
        name, row = hgk
        deps = row.get("dependencies") or {}
        und = [str(u.get("module", "")).lower() for u in (deps.get("undeclared_third_party") or [])]
        if "yaml" not in und:
            return False, "YAML_NOT_LOCATED", f"undeclared modules found: {und[:8]}"
        # The addendum of the previous round asserted that cryptography is imported and undeclared.
        # It is declared (pyproject: cryptography>=42). An artifact that repeats the false claim is red.
        if "cryptography" in und:
            return False, "CRYPTOGRAPHY_FALSELY_MARKED_UNDECLARED", "the artifact repeats the previous round's claim that cryptography is undeclared; pyproject declares cryptography>=42"
        return True, "OK", f"{name}: undeclared={und}; declared_covers_imports={deps.get('declared_covers_imports')}"
    a = ctx.load("evidence/WP19/DEPENDENCY_INVENTORY.json", "evidence/WP19/DEPENDENCY_INVENTORY.json")
    if not any("declared_covers_imports" in r for r in a.get("repos", [])):
        return False, "DECLARED_VS_IMPORTED_ABSENT", "dependency inventory lists declared packages only; no import set is compared"
    return True, "OK", "import comparison present"


def g17_enum_slash_safe(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/E/WP21_ENUM_V2.json")
        d = a.get("denominators") or {}
        want = {"ac15": 15, "oracle96": 96, "h4": 12, "seam": 11}
        for k, n in want.items():
            cell = d.get(k)
            got = cell.get("measured") if isinstance(cell, dict) else cell
            if got != n:
                return False, f"DENOMINATOR_{k.upper()}", f"{k} measured {got} expected {n}"
        nu = a.get("naive_undercount") or {}
        if nu.get("robust") != 11 or nu.get("naive") != 10:
            return False, "SLASH_PARSE_NOT_DEMONSTRATED", json.dumps(nu, ensure_ascii=False)[:200]
        if not nu.get("missing_id"):
            return False, "SLASH_MISSING_ID_UNNAMED", "the undercount names no identifier"
        seam = a.get("seam") or {}
        ids = seam.get("expected_ids") or seam.get("ids") or a.get("seam_ids") or []
        ids = [i for i in ids if isinstance(i, str)]
        if len(set(ids)) != 11:
            return False, "SEAM_ID_SET", f"{len(set(ids))} distinct seam ids"
        naive_ids = seam.get("naive_ids") or []
        if naive_ids and set(naive_ids) == set(ids):
            return False, "SLASH_NAIVE_EQUALS_ROBUST", "the two parsers produced the same set, so the undercount is unevidenced"
        x = (a.get("oracle_cross_product") or seam.get("oracle_cross_product")
             or (a.get("groups") or {}).get("oracle96") or {})
        classes = x.get("class_count", len(x.get("classes") or []))
        types = x.get("type_count", len(x.get("types") or []))
        complete = x.get("complete_12x8", x.get("complete"))
        if not (classes == 12 and types == 8 and complete is True):
            return False, "ORACLE_CROSS_PRODUCT", json.dumps({k: x.get(k) for k in ("class_count", "type_count", "complete_12x8", "pair_count")}, ensure_ascii=False)
        return True, "OK", f"ac15=15 oracle96=96 h4=12 seam=11; naive={nu.get('naive')} robust={nu.get('robust')} missing={nu.get('missing_id')}"
    a = ctx.load("evidence/WP21/REPORT.json", "evidence/WP21/REPORT.json")
    c = a.get("counts") or a.get("checks") or {}
    seam = c.get("seam") if isinstance(c, dict) else None
    if seam not in (11, None):
        return False, "SEAM_DENOMINATOR", f"seam={seam}"
    if "naive" not in json.dumps(a, ensure_ascii=False).lower():
        return True, "OK_PARSER_NOT_EXERCISED", "denominators correct, but the artifact never shows a naive parse: fragility is untested here and is proven by injection instead"
    return True, "OK", "denominators present"


def g18_digest_locality(ctx: Ctx):
    if ctx.mode == "r9":
        base = os.path.join(ctx.round_dir, "out", "stage")
        mfs = find_manifest_files(base) if os.path.isdir(base) else []
        if not mfs:
            return None, "NO_PAYLOAD", "no staged payload under out/stage — run the publication stage first"
        total_res = total_dec = 0
        probs = []
        for m in mfs:
            r, n, p = verify_manifest_locality(m)
            total_res += r
            total_dec += n
            probs += [dict(x, manifest=os.path.relpath(m, ctx.round_dir)) for x in p]
        if probs:
            return False, "DIGEST_CROSSES_PAYLOAD", f"{len(probs)} unresolved: {probs[:3]}"
        return True, "OK", f"{total_res}/{total_dec} digests resolve inside their own payload across {len(mfs)} manifests"
    base = os.path.join(ctx.prior_dir, "out", "stage")
    mfs = find_manifest_files(base) if os.path.isdir(base) else []
    if not mfs:
        return None, "NO_ANALOGUE", "prior round staged no payload"
    probs = []
    for m in mfs:
        r, n, p = verify_manifest_locality(m)
        probs += p
    if probs:
        return False, "DIGEST_CROSSES_PAYLOAD", f"{len(probs)} unresolved in prior payload: {probs[:3]}"
    return True, "OK", f"prior payload already local across {len(mfs)} manifests"


def g19_copy_register(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("out/SOURCE_COPY_REGISTER.json")
        ident = a.get("identity_31") or {}
        if ident.get("files") != 31:
            return False, "REGISTER_SOURCE_COUNT", f"{ident.get('files')} sources registered"
        if ident.get("duplicate_names") not in (0, None) or ident.get("duplicate_digests") not in (0, None):
            return False, "REGISTER_IN_SET_COLLISION", json.dumps(ident, ensure_ascii=False)
        amb = a.get("ambiguous") or []
        for g in amb:
            if g.get("distinct_digests", 0) < 2:
                return False, "AMBIGUOUS_GROUP_NOT_AMBIGUOUS", g.get("name")
            if not g.get("differing_bytes"):
                return False, "AMBIGUOUS_GROUP_LOCATION_UNSTATED", g.get("name")
        if a.get("canonical_resolution", {}).get("state") != "OWNER_UNRESOLVED":
            return False, "COPY_CANONICAL_STATE", "canonical resolution is not OWNER_UNRESOLVED"
        return True, "OK", f"{a.get('names_registered')} names, {len(amb)} ambiguous group(s), canonical OWNER_UNRESOLVED"
    p = os.path.join(ctx.prior_dir, "out", "SOURCE_COPY_REGISTER.json")
    if not os.path.isfile(p):
        return None, "NO_ANALOGUE", "prior round kept no copy register"
    return True, "OK", "register present"


def g20_supply_chain_split(ctx: Ctx):
    if ctx.mode == "r9":
        a = ctx.load("lanes/D/WP19_V2.json")
        sc = a.get("supply_chain_claim")
        if not isinstance(sc, dict):
            sc = {}
            for name, r in _repo_rows(a):
                cand = r.get("supply_chain_claim")
                if isinstance(cand, dict):
                    sc = cand
                    break
        if not sc.get("offline_reproducible") or not sc.get("hosted_conclusion"):
            return False, "SUPPLY_CHAIN_HALVES_ABSENT", f"keys={list(sc)}"
        note = json.dumps(sc.get("claim_shape") or "", ensure_ascii=False).lower()
        substitutable = ("neither substitut" in note or "cannot" in note or "不可" in note
                         or "not substitut" in note or "do not substitut" in note)
        evidence_words = ("evidence" in note or "證據" in note)
        if not (substitutable and evidence_words):
            return False, "SUPPLY_CHAIN_SUBSTITUTION_ALLOWED", "claim_shape does not state that the halves are different evidence classes"
        return True, "OK", "offline and hosted halves recorded separately, non-substitution stated"
    a = ctx.load("evidence/WP19/REPORT.json", "evidence/WP19/REPORT.json")
    blob = json.dumps(a, ensure_ascii=False).lower()
    if "offline" not in blob or "hosted" not in blob:
        return False, "SUPPLY_CHAIN_NOT_SPLIT", "the prior report does not separate an offline result from a hosted conclusion"
    return True, "OK", "halves separate"


CHECKS = [
    ("G11", "LINE_CONVENTION", g11_line_convention),
    ("G12", "SEGMENTATION_RULE", g12_segmentation_rule),
    ("G13", "COUNT_SCOPE", g13_count_scope),
    ("G14", "MAXIMUM_IS_GLOBAL", g14_maximum_is_global),
    ("G15", "LICENCE_LAYER", g15_licence_layer),
    ("G16", "DECLARED_COVERS_IMPORTS", g16_declared_covers_imports),
    ("G17", "ENUM_SLASH_SAFE", g17_enum_slash_safe),
    ("G18", "DIGEST_LOCALITY", g18_digest_locality),
    ("G19", "COPY_REGISTER", g19_copy_register),
    ("G20", "SUPPLY_CHAIN_SPLIT", g20_supply_chain_split),
]


# --------------------------------------------------------------------------------------------------
# selftest: one targeted mutation per check


def selftest(ctx: Ctx) -> int:
    results = []
    for cid, name, fn in CHECKS:
        try:
            ok, code, detail = fn(ctx)
        except FileNotFoundError as e:
            results.append({"check": cid, "name": name, "baseline": "ABSENT", "artifact": str(e), "mutated": "SKIPPED"})
            continue
        if ok is None:
            results.append({"check": cid, "name": name, "baseline": "NOT_APPLICABLE", "detail": code, "mutated": "SKIPPED"})
            continue
        if not ok:
            results.append({"check": cid, "name": name, "baseline": "FAIL", "detail": f"{code}: {detail}", "mutated": "SKIPPED"})
            continue
        mut = MUTATIONS.get(cid)
        verdict = "NO_MUTATION_DEFINED"
        got = None
        if mut:
            got = mut(ctx)
            verdict = "FIRED" if got and got[0] is False else "DID_NOT_FIRE"
        results.append({"check": cid, "name": name, "baseline": "PASS", "mutated": verdict,
                        "mutated_code": (got[1] if got else None), "mutated_detail": (got[2] if got else None)})
    bad = [r for r in results if r["baseline"] != "PASS" or r["mutated"] not in ("FIRED", "SKIPPED")]
    print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0 if not bad else 1


def _mut_g11(ctx):
    a = ctx.load("lanes/A/SOURCE_LOCK_V2.json")
    rec = a["sources"][0]
    if isinstance(rec.get("match"), dict):
        rec["match"]["lines"] = False
    else:
        rec["lines_match"] = False
    p = ctx.path("lanes/A/SOURCE_LOCK_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g11_line_convention(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g12(ctx):
    a = ctx.load("lanes/B/U0_PARTITION_V2.json")
    a["totals"]["structural_blocks_sum"] = a["totals"]["per_line_segments_sum"]
    p = ctx.path("lanes/B/U0_PARTITION_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g12_segmentation_rule(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g13(ctx):
    a = ctx.load("lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json")
    keys = [k for k in a if k.startswith("kb_external") and isinstance(a[k], dict)]
    if not keys:
        return None
    a[keys[-1]]["scope"] = ""
    p = ctx.path("lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g13_count_scope(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g14(ctx):
    a = ctx.load("lanes/C/DISTINCTNESS_V2.json")
    a["max_overall"] = 0.0
    p = ctx.path("lanes/C/DISTINCTNESS_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g14_maximum_is_global(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g15(ctx):
    a = ctx.load("lanes/D/WP19_V2.json")
    name, row = _repo_rows(a)[0]
    cl = row.get("claim") or (row.get("licence") or {}).get("claim")
    if not isinstance(cl, dict):
        return None
    cl["scope_note"] = ""
    p = ctx.path("lanes/D/WP19_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g15_licence_layer(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g16(ctx):
    a = ctx.load("lanes/D/WP19_V2.json")
    for _name, r in _repo_rows(a):
        deps = r.get("dependencies")
        if isinstance(deps, dict):
            deps.pop("undeclared_third_party", None)
            deps["declared_covers_imports"] = True
    p = ctx.path("lanes/D/WP19_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g16_declared_covers_imports(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g17(ctx):
    a = ctx.load("lanes/E/WP21_ENUM_V2.json")
    a["naive_undercount"]["naive"] = 11
    p = ctx.path("lanes/E/WP21_ENUM_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g17_enum_slash_safe(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g18(ctx):
    base = os.path.join(ctx.round_dir, "out", "stage")
    mfs = find_manifest_files(base)
    if not mfs:
        return None
    m = mfs[0]
    orig = open(m, encoding="utf-8").read()
    try:
        d = json.loads(orig)
        ents = d.get("files") or d.get("entries") or []
        if not ents:
            return None
        ents.append({"path": "../other-payload/not-here.json", "sha256": "0" * 64})
        json.dump(d, open(m, "w", encoding="utf-8"), ensure_ascii=False)
        return g18_digest_locality(ctx)
    finally:
        open(m, "w", encoding="utf-8").write(orig)


def _mut_g19(ctx):
    a = ctx.load("out/SOURCE_COPY_REGISTER.json")
    a["canonical_resolution"]["state"] = "RESOLVED_BY_MAKER"
    p = ctx.path("out/SOURCE_COPY_REGISTER.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g19_copy_register(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


def _mut_g20(ctx):
    a = ctx.load("lanes/D/WP19_V2.json")
    target = a.get("supply_chain_claim")
    if not isinstance(target, dict):
        target = None
        for _name, r in _repo_rows(a):
            if isinstance(r.get("supply_chain_claim"), dict):
                target = r["supply_chain_claim"]
                break
    if target is None:
        return None
    target["claim_shape"] = "green CI proves the offline gate too"
    p = ctx.path("lanes/D/WP19_V2.json")
    orig = open(p, encoding="utf-8").read()
    try:
        json.dump(a, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return g20_supply_chain_split(ctx)
    finally:
        open(p, "w", encoding="utf-8").write(orig)


MUTATIONS = {
    "G11": _mut_g11, "G12": _mut_g12, "G13": _mut_g13, "G14": _mut_g14, "G15": _mut_g15,
    "G16": _mut_g16, "G17": _mut_g17, "G18": _mut_g18, "G19": _mut_g19, "G20": _mut_g20,
}


# --------------------------------------------------------------------------------------------------
# hygiene


def hygiene(root: str) -> list[dict]:
    findings = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            if size > MAX_ARTIFACT_BYTES:
                findings.append({"path": rel, "why": "OVERSIZE", "bytes": size})
                continue
            if os.path.splitext(fn)[1].lower() in FORBIDDEN_SUFFIX:
                findings.append({"path": rel, "why": "FORBIDDEN_TYPE", "bytes": size})
                continue
            if size > 512 * 1024 or not fn.lower().endswith((".md", ".json", ".txt", ".py", ".yaml", ".yml")):
                continue
            try:
                text = open(p, "r", encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for pat in TOKEN_SHAPES:
                if pat.search(text):
                    findings.append({"path": rel, "why": "TOKEN_SHAPED_STRING", "pattern": pat.pattern[:24]})
                    break
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=".", help="round directory (repaired artifacts)")
    ap.add_argument("--prior", default=None, help="pre-repair round directory")
    ap.add_argument("--mode", choices=["r9", "prior"], default=None,
                    help="which artifact generation the checks read; defaults to prior when --prior is given")
    ap.add_argument("--json", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--skip-hygiene", action="store_true")
    a = ap.parse_args()

    mode = a.mode or ("prior" if a.prior else "r9")
    ctx = Ctx(mode, a.round, a.prior)
    if a.selftest:
        return selftest(ctx)

    hy = [] if a.skip_hygiene else hygiene(ctx.round_dir)
    results = []
    for cid, name, fn in CHECKS:
        try:
            ok, code, detail = fn(ctx)
        except FileNotFoundError as e:
            results.append({"check": cid, "name": name, "verdict": "ABSENT", "code": "ARTIFACT_ABSENT", "detail": str(e)})
            continue
        except Exception as e:  # noqa: BLE001
            results.append({"check": cid, "name": name, "verdict": "ERROR", "code": "CHECK_RAISED", "detail": f"{e.__class__.__name__}: {e}"})
            continue
        verdict = "PASS" if ok is True else ("NOT_APPLICABLE" if ok is None else "FAIL")
        results.append({"check": cid, "name": name, "verdict": verdict, "code": code, "detail": detail})

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = [r for r in results if r["verdict"] in ("FAIL", "ERROR")]
    absent = [r for r in results if r["verdict"] == "ABSENT"]
    na = [r for r in results if r["verdict"] == "NOT_APPLICABLE"]

    report = {
        "schema": "FHS.W0.Gate/2",
        "gate": "GSTACK v2",
        "mode": ctx.mode,
        "round": ctx.round_dir.replace("\\", "/"),
        "prior": (ctx.prior_dir or "").replace("\\", "/") if ctx.prior_dir else None,
        "generated_at": now(),
        "checks": results,
        "summary": {"total": len(results), "pass": passed, "fail": len(failed), "absent": len(absent), "not_applicable": len(na)},
        "hygiene": {"findings": hy, "count": len(hy)},
        "claim_ceiling": "GATE_VERDICT_NOT_ACCEPTANCE",
        "not_claimed": ["ORIGINAL_ACK", "NATIVE_WORLDRAW", "RELEASE_GRANTED", "INDEPENDENT_PASS"],
    }
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
            fh.write("\n")

    for r in results:
        mark = {"PASS": "ok  ", "FAIL": "FAIL", "ABSENT": "ABS ", "NOT_APPLICABLE": "n/a ", "ERROR": "ERR "}[r["verdict"]]
        print(f"[{mark}] {r['check']:3} {r['name']:26} {r['code']:34} {r['detail'][:110]}")
    print(f"\nVERDICT {'PASS' if not failed and not absent and not hy else 'FAIL'} "
          f"pass={passed} fail={len(failed)} absent={len(absent)} n/a={len(na)} hygiene={len(hy)} total={len(results)}")

    if hy:
        print("\nhygiene findings:")
        for f in hy[:10]:
            print(" ", f)
        return 3
    if absent:
        return 2
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
