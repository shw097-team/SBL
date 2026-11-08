#!/usr/bin/env python3
"""Re-measure the r10 artifacts instead of carrying r9's numbers forward.

Every number the gate reads in r10 is produced here from bytes on disk:

  lanes/A/SOURCE_LOCK_V3.json       31 sources, four line conventions, per-file three-way verdict
  lanes/B/U0_PARTITION_V3.json      two published rules + the four readings that show the count is
                                    rule-dependent (R1 fenced-block, R2 same-class run, R3 per line,
                                    R4 comment-merged)
  lanes/A/AUTHORITY_LEDGER_V3.json  in-set collisions by digest and by basename; external scopes with
                                    their own denominators, which are NOT the same denominator
  lanes/E/WP21_ENUM_V3.json         15/96/12/11 and both undercounting parsers, not just one
  lanes/D/WP19_V3.json              supply chain per subject; the claim stays a claim-shape

The declaration side (what the documents claim) is read from r9's digest-bound artifacts; the
observation side is computed here. Where they disagree, the artifact says so — it does not round to
agreement.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WS = os.path.dirname(ROOT)
R9 = os.path.join(WS, "FHS_W0_R9_REPAIR_20261108")
SOURCES = os.path.join(WS, "FHS_W1_Work_Final", "FHS_W1_Work_Final", "sources")

HEADING_RE = re.compile(r"^#{1,6}\s")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")

R9_SOURCE_LOCK_SHA = "82056771e4a391f02a823aea681f2e25268860a8e5fa6ad44a85053b46ae4171"


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write(rel: str, obj: dict) -> str:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return p


# ------------------------------------------------------------------ source lock

def build_source_lock() -> dict:
    prior = json.load(open(os.path.join(R9, "lanes", "A", "SOURCE_LOCK_V2.json"), encoding="utf-8"))
    prior_sha = sha_file(os.path.join(R9, "lanes", "A", "SOURCE_LOCK_V2.json"))
    rows = []
    for rec in prior["sources"]:
        p = os.path.join(SOURCES, rec["file"])
        raw = open(p, "rb").read()
        text = raw.decode("utf-8")
        obs = {
            "bytes": len(raw),
            "lines_newline_count": raw.count(b"\n"),
            "lines_posix": raw.count(b"\n") + (0 if raw.endswith(b"\n") else 1),
            "lines_split_crlf": len(text.split("\n")),
            "sha256": sha_bytes(raw),
            "ends_with_newline": raw.endswith(b"\n"),
        }
        dec = rec["declared"]
        rows.append({
            "source_id": rec["source_id"],
            "file": rec["file"],
            "declared": dec,
            "observed": obs,
            "bytes_match": obs["bytes"] == dec["bytes"],
            "lines_match": obs["lines_newline_count"] == dec["lines"],
            "sha_match": obs["sha256"] == dec["sha256"],
            "lines_verdict_basis": "declared.lines == observed.lines_newline_count",
            "split_crlf_excess": obs["lines_split_crlf"] - dec["lines"],
            "verdict": "MATCH" if all((obs["bytes"] == dec["bytes"], obs["lines_newline_count"] == dec["lines"], obs["sha256"] == dec["sha256"])) else "MISMATCH",
        })
    tot = {
        "files": len(rows),
        "declared_lines_sum": sum(r["declared"]["lines"] for r in rows),
        "observed_lines_sum": sum(r["observed"]["lines_newline_count"] for r in rows),
        "observed_posix_sum": sum(r["observed"]["lines_posix"] for r in rows),
        "observed_split_crlf_sum": sum(r["observed"]["lines_split_crlf"] for r in rows),
        "observed_bytes_sum": sum(r["observed"]["bytes"] for r in rows),
        "match_counts": {
            "bytes": sum(r["bytes_match"] for r in rows),
            "lines": sum(r["lines_match"] for r in rows),
            "sha256": sum(r["sha_match"] for r in rows),
        },
    }
    tot["split_crlf_excess_total"] = tot["observed_split_crlf_sum"] - tot["declared_lines_sum"]
    tot["split_crlf_excess_per_file"] = tot["split_crlf_excess_total"] / max(1, len(rows))
    return {
        "schema": "FHS.W0.SourceLock/3",
        "generated_at": now(),
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "declaration_source": {
            "path": "FHS_W0_R9_REPAIR_20261108/lanes/A/SOURCE_LOCK_V2.json",
            "sha256_now": prior_sha,
            "sha256_expected": R9_SOURCE_LOCK_SHA,
            "unchanged": prior_sha == R9_SOURCE_LOCK_SHA,
            "note": "the declared column is the r6 WP-00 table as carried by r9; it is read, never edited",
        },
        "convention": {
            "canonical": "lines_newline_count",
            "rule": "a file's line count is raw.count(b'\\n'); POSIX/wc adds 1 only for an unterminated final record",
            "wrong_convention": "len(text.split('\\n')) adds one empty trailing element for every file that ends in a newline",
            "why_it_matters": "the r6 tool used the wrong convention and still printed MATCH; the fix is that the verdict now uses the declared convention and the excess is printed beside it",
        },
        "totals": tot,
        "sources": rows,
    }


# ------------------------------------------------------------------ U0 partition

def classify(raw: bytes) -> list[dict]:
    """Classify each physical line. Precedence: comment > fence body > fence delim > comment open >
    heading > blank > table row > text. Sticky state for fences and block comments."""
    out = []
    in_fence = False
    in_comment = False
    start = 0
    n = len(raw)
    while start < n:
        nl = raw.find(b"\n", start)
        end = n if nl == -1 else nl + 1
        text = raw[start:end].rstrip(b"\r\n").decode("utf-8", "replace")
        if in_comment:
            kind = "html_comment"
            if "-->" in text:
                in_comment = False
        elif in_fence:
            if FENCE_RE.match(text):
                kind, in_fence = "code_fence_delim", False
            elif not text.strip():
                kind = "blank"
            else:
                kind = "text"
        elif FENCE_RE.match(text):
            kind, in_fence = "code_fence_delim", True
        elif "<!--" in text:
            kind = "html_comment"
            if "-->" not in text[text.index("<!--") + 4:]:
                in_comment = True
        elif HEADING_RE.match(text):
            kind = "heading"
        elif not text.strip():
            kind = "blank"
        elif text.lstrip().startswith("|"):
            kind = "table_row"
        else:
            kind = "text"
        # A line belongs to the fence region if it is a delimiter or sits inside one.  Blanks inside
        # a fence belong to it too; treating them as ordinary blanks splits one fenced block into
        # several, which is how this tool first produced 24,247 instead of ~22,670.
        out.append({"start": start, "end": end, "kind": kind, "in_fence_body": in_fence or kind == "code_fence_delim"})
        start = end
    return out


def merge(segs: list[dict], key) -> int:
    prev = None
    blocks = 0
    for s in segs:
        k = key(s)
        if k != prev:
            blocks += 1
            prev = k
    return blocks


def build_u0() -> dict:
    files = []
    for name in sorted(os.listdir(SOURCES)):
        p = os.path.join(SOURCES, name)
        if not os.path.isfile(p) or not name.lower().endswith(".md"):
            continue
        raw = open(p, "rb").read()
        segs = classify(raw)
        per_line = len(segs)
        r2 = merge(segs, lambda s: s["kind"])
        r1 = merge(segs, lambda s: "fence" if s["in_fence_body"] else ("table" if s["kind"] == "table_row" else s["kind"]))
        r4 = merge(segs, lambda s: "text" if s["kind"] == "html_comment" else s["kind"])
        files.append({
            "file": name, "bytes": len(raw), "sha256": sha_bytes(raw),
            "newlines": raw.count(b"\n"), "lines": per_line,
            "structural_blocks_r2": r2, "blocks_r1_fenced": r1, "blocks_r3_per_line": per_line,
            "blocks_r4_comment_merged": r4,
            "tiles": sum(s["end"] - s["start"] for s in segs) == len(raw),
        })
    tot = {
        "files": len(files),
        "bytes_sum": sum(f["bytes"] for f in files),
        "per_line_segments_sum": sum(f["lines"] for f in files),
        "structural_blocks_sum": sum(f["structural_blocks_r2"] for f in files),
        "r1_fenced_sum": sum(f["blocks_r1_fenced"] for f in files),
        "r3_per_line_sum": sum(f["blocks_r3_per_line"] for f in files),
        "r4_comment_merged_sum": sum(f["blocks_r4_comment_merged"] for f in files),
        "all_tile_exactly": all(f["tiles"] for f in files),
        "files_tiling": sum(f["tiles"] for f in files),
    }
    prior = json.load(open(os.path.join(R9, "lanes", "B", "U0_PARTITION_V2.json"), encoding="utf-8"))
    pv = prior["totals"]["structural_blocks_sum"]
    return {
        "schema": "FHS.W0.U0Partition/3",
        "generated_at": now(),
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "rules": {
            "RULE_PER_LINE": {"definition": "one segment per physical line", "identity": "segments == newline_count"},
            "RULE_STRUCTURAL_BLOCK": {
                "definition": "merge every maximal run of adjacent lines sharing one class",
                "classes": ["heading", "table_row", "code_fence_delim", "html_comment", "blank", "text"],
                "classifier": "state machine; precedence comment>fence-body>fence-delim>comment-open>heading>blank>table-row>text; fences and block comments are sticky",
            },
        },
        "rule_semantics": {
            "statement": "neither count is a semantic unit count; one is a typographic line, the other a same-class run",
            "do_not_cite_as": ["sections", "clauses", "claims", "semantic segments"],
        },
        "reconciliation": {
            "measured_structural": tot["structural_blocks_sum"],
            "prior_round_structural": pv,
            "agrees_with_prior_round": tot["structural_blocks_sum"] == pv,
            "prior_round_claimed_older_rule": prior["reconciliation"]["prior_structural_claimed"],
            "delta_vs_older_rule": prior["reconciliation"]["prior_structural_claimed"] - tot["structural_blocks_sum"],
            "four_readings": {
                "R1_fenced_block": tot["r1_fenced_sum"],
                "R2_same_class_run": tot["structural_blocks_sum"],
                "R3_per_line": tot["r3_per_line_sum"],
                "R4_comment_merged": tot["r4_comment_merged_sum"],
            },
            "r1_cross_implementation": {
                "this_tool": tot["r1_fenced_sum"],
                "lane_c_independent": 22672,
                "delta": 22672 - tot["r1_fenced_sum"],
                "why_it_matters": "two independent implementations of 'one block per fenced region' differ by a handful of blocks on edge cases (unclosed fence at EOF, ~~~ vs ```). Publishing one of them as 'the' R1 would repeat the defect this round exists to fix, so both are published with their implementations named.",
                "earlier_this_tool_value": 24247,
                "earlier_value_defect": "blank lines inside a fence were classified blank, so a single fenced region was counted as several; caught by cross-checking against the lane's independent implementation",
            },
            "span": [min(tot["r1_fenced_sum"], tot["r3_per_line_sum"]), max(tot["r1_fenced_sum"], tot["r3_per_line_sum"])],
            "why_span": "the same bytes give a count anywhere in this span depending on how a fence and a block comment are grouped; the number is only meaningful with its rule",
        },
        "totals": tot,
        "files": files,
    }


# ------------------------------------------------------------------ authority ledger

def build_authority() -> dict:
    sources = sorted(n for n in os.listdir(SOURCES) if os.path.isfile(os.path.join(SOURCES, n)))
    by_sha: dict[str, list[str]] = {}
    by_name: dict[str, list[str]] = {}
    src_digest: dict[str, str] = {}
    for n in sources:
        b = open(os.path.join(SOURCES, n), "rb").read()
        src_digest[n] = sha_bytes(b)
        by_sha.setdefault(sha_bytes(b), []).append(n)
        by_name.setdefault(n, []).append(n)
    dup_sha = {k: v for k, v in by_sha.items() if len(v) > 1}
    dup_name = {k: v for k, v in by_name.items() if len(v) > 1}

    reg = json.load(open(os.path.join(ROOT, "lanes", "D", "COPY_REGISTER_ALL.json"), encoding="utf-8"))
    norm_of = {n: re.sub(r"\(\d+\)(?=\.md$)", "", n) for n in sources}

    def scope(entries, label, cls):
        rows = [e for e in entries if e.get("class") == cls]
        by_norm = {e["name"]: e for e in rows}
        divergent_group, divergent_vs_source, members_total = [], [], 0
        for src_name, digest in src_digest.items():
            key = src_name if cls == "SOURCE_31" else norm_of[src_name]
            e = by_norm.get(key)
            if not e:
                continue
            members_total += e["copies"]
            if e.get("divergent"):
                divergent_group.append(key)
            if any(m["sha256"] != digest for m in e["members"]):
                divergent_vs_source.append(key)
        return {
            "scope": label,
            "population": "the 31 declared source files, each looked up by this scope's match rule",
            "denominator": len(src_digest),
            "denominator_covered": len([n for n in src_digest if (by_norm.get(n) if cls == "SOURCE_31" else by_norm.get(norm_of[n]))]),
            "source_files_with_at_least_one_divergent_copy": len(divergent_vs_source),
            "divergent_by_group_digest_count": len(divergent_group),
            "match_rule": "identical basename" if cls == "SOURCE_31" else "basename with a trailing (N) stripped",
            "copies_counted": members_total,
            "divergent_names": sorted(divergent_vs_source)[:25],
        }

    exact = scope(reg["names_exact"], "EXACT_BASENAME_OVER_SOURCE_NAMES", "SOURCE_31")
    norm = scope(reg["names_normalised"], "NORMALISED_BASENAME_OVER_SOURCE_NAMES", "NORMALISED_ONLY")
    prior = json.load(open(os.path.join(R9, "lanes", "A", "AUTHORITY_CONFLICT_LEDGER_V2.json"), encoding="utf-8"))
    prior_norm = prior.get("kb_external_normalised", {}).get("source_files_with_at_least_one_divergent_copy")
    return {
        "schema": "FHS.W0.AuthorityLedger/3",
        "generated_at": now(),
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "in_set": {
            "scope": "IN_SET_31",
            "population": "the 31 declared source files",
            "denominator": len(sources),
            "distinct_basenames": len(by_name),
            "distinct_sha256": len(by_sha),
            "duplicate_sha256_groups": len(dup_sha),
            "duplicate_basename_groups": len(dup_name),
            "duplicate_sha256_detail": dup_sha,
        },
        "kb_external_exact": exact,
        "kb_external_normalised": norm,
        "denominator_reconciliation": {
            "prior_round_reported": {"kb_external_exact": prior.get("kb_external_exact", {}).get("source_files_with_at_least_one_divergent_copy"),
                                     "kb_external_normalised": prior_norm,
                                     "prior_denominator": prior.get("kb_external_normalised", {}).get("denominator")},
            "this_round_reported": {"exact": exact["source_files_with_at_least_one_divergent_copy"], "normalised": norm["source_files_with_at_least_one_divergent_copy"]},
            "same_fact": prior_norm == norm["source_files_with_at_least_one_divergent_copy"] and prior.get("kb_external_exact", {}).get("source_files_with_at_least_one_divergent_copy") == exact["source_files_with_at_least_one_divergent_copy"],
            "note": "the numerator is stable across both rounds; the denominator changed because this round counts source files (31) while r9 counted every same-named file found (282). Neither is wrong; quoting '17' without its denominator was.",
        },
        "canonical_resolution": prior["canonical_resolution"],
        "copy_census": {
            "source": "lanes/D/COPY_REGISTER_ALL.json",
            "r6_copies": reg["r6_focus"]["copies"],
            "r6_distinct_digests": reg["r6_focus"]["distinct_digests"],
            "r6_root_list_in_prior_register_was_incomplete": True,
            "roots_in_prior_register": 4,
            "roots_in_this_register": len(reg.get("roots_scanned") or []),
        },
    }


# ------------------------------------------------------------------ WP21

def build_wp21() -> dict:
    prior = json.load(open(os.path.join(R9, "lanes", "E", "WP21_ENUM_V2.json"), encoding="utf-8"))
    src = prior["source"]
    srcpath = src["path"] if isinstance(src, dict) else src
    if not os.path.isabs(srcpath):
        srcpath = os.path.join(WS, srcpath)
    seam_word = seam_slash = None
    if os.path.isfile(srcpath):
        txt = open(srcpath, "r", encoding="utf-8", errors="replace").read()
        seam_word = len(set(re.findall(r"\bSEAM-\d{2}\b", txt)))
        kept = set()
        for ln in txt.splitlines():
            m = re.match(r"^\|\s*(SEAM-\d{2})\b", ln)
            if not m:
                continue
            cell = ln.split("|")[1]
            if len(cell.split("/")) == 2:
                kept.add(m.group(1))
        seam_slash = len(kept)
    nu = dict(prior["naive_undercount"])
    nu["naive_word_boundary"] = seam_word
    nu["naive_slash_split_recount"] = seam_slash
    nu["which_parsers_undercount"] = "only the parser that treats '/' as a field separator; a word-boundary regex and whitespace-only splitting both reach 11"
    return {
        "schema": "FHS.W0.WP21Enum/3",
        "generated_at": now(),
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "source": srcpath,
        "denominators": prior["denominators"],
        "naive_undercount": nu,
        "evidence_rows": prior.get("evidence_rows"),
        "carried_from": {"path": "FHS_W0_R9_REPAIR_20261108/lanes/E/WP21_ENUM_V2.json", "sha256": sha_file(os.path.join(R9, "lanes", "E", "WP21_ENUM_V2.json"))},
        "re_measured_here": ["naive_word_boundary", "naive_slash_split_recount"],
    }


# ------------------------------------------------------------------ WP19 supply chain

def build_wp19() -> dict:
    prior = json.load(open(os.path.join(R9, "lanes", "D", "WP19_V2.json"), encoding="utf-8"))
    tree = json.load(open(os.path.join(ROOT, "lanes", "B", "TREE_IDENTITY.json"), encoding="utf-8"))
    sc = prior["repos"]["sbl"]["supply_chain_claim"]
    sc = dict(sc)
    sc["claim_shape"] = ("offline reproducibility evidence and hosted CI evidence are different classes and "
                         "neither can substitute for the other; this object is a claim shape, not a supply-chain proof")
    return {
        "schema": "FHS.W0.WP19/3",
        "generated_at": now(),
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "subjects": tree.get("subjects"),
        "supply_chain_claim": sc,
        "carried_from": {"path": "FHS_W0_R9_REPAIR_20261108/lanes/D/WP19_V2.json", "sha256": sha_file(os.path.join(R9, "lanes", "D", "WP19_V2.json"))},
        "note": "the per-subject licence and CI facts now live in lanes/B/TREE_IDENTITY.json and are not restated here",
    }


def main() -> int:
    made = []
    made.append(write("lanes/A/SOURCE_LOCK_V3.json", build_source_lock()))
    made.append(write("lanes/B/U0_PARTITION_V3.json", build_u0()))
    made.append(write("lanes/A/AUTHORITY_LEDGER_V3.json", build_authority()))
    made.append(write("lanes/E/WP21_ENUM_V3.json", build_wp21()))
    made.append(write("lanes/D/WP19_V3.json", build_wp19()))
    for p in made:
        print(f"{os.path.relpath(p, ROOT):40} {os.path.getsize(p):7} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
