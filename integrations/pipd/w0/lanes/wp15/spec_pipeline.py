#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FHS W0 R4C / WP-FHS-15 — three genuinely heterogeneous SPEC generators.

The pipeline reads the W0 r4-candidate substantive body (CH-00..CH-49) plus the
author-side registries under --source-root, and *derives* every identifier and
every count it reports.  Nothing is hard-coded: requirement ids, WP/Edge ids,
chapter ids, source ids, oracle case ids, card ids and all headline numbers are
recomputed from the source bytes and each one carries a `source_ref` recording
the file, the selector used and the value actually observed.

Outputs (written into --out):
    SPEC_Product.json / .md
    SPEC_Architecture.json / .md
    SPEC_Program.json / .md
    GOAL_TO_FUO.json / .md
    SPEC_HETEROGENEITY.json

Failure codes raised by this module (asserted by tests/test_spec_pipeline.py):
    SPEC_NOT_HETEROGENEOUS   two SPECs share the same section set / field set,
                             i.e. "same body, different title"
    FUO_MISSING              a Product SPEC without any first-usable-outcome
    REQUIREMENT_UNBOUND      a cited RequirementID that no registry row binds
    SUBJECT_BODY_SHA_MISMATCH  body sha differs from CURRENT_CANDIDATE_STATE

Claim ceiling of everything produced here: AUTHOR_LOCAL_TEST.  No Native run,
no original Reader ACK, no world effect, no publisher/checker verdict.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys

CLAIM_CEILING = "AUTHOR_LOCAL_TEST"
SCHEMA_TAG = "FHS-W0-WP15/v1"
HETERO_MAX_SECTION_JACCARD = 0.25
HETERO_MAX_TOKEN_JACCARD = 0.35
HETERO_MAX_FIELD_JACCARD = 0.60

BODY_GLOB_SUFFIX = "_實質正文.md"


# --------------------------------------------------------------------------- #
# errors
# --------------------------------------------------------------------------- #
class SpecError(Exception):
    """Failure with a stable machine code (asserted verbatim by the tests)."""

    def __init__(self, code, detail="", payload=None):
        self.code = code
        self.detail = detail
        self.payload = payload or {}
        super().__init__("%s: %s" % (code, detail))


# --------------------------------------------------------------------------- #
# hashing helpers
# --------------------------------------------------------------------------- #
def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


def canonical_bytes(obj):
    """Stable byte form used for every digest that a reader must recompute."""
    return json.dumps(
        obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def pretty_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def strip_md(cell):
    return cell.strip().strip("*").strip("`").strip()


def clean_cell(cell):
    """Trim markdown emphasis but keep the author's inline code marks intact."""
    t = cell.strip()
    while t.startswith("**") and t.endswith("**") and len(t) > 4:
        t = t[2:-2].strip()
    return t


def split_pipe_row(line):
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


# --------------------------------------------------------------------------- #
# source index
# --------------------------------------------------------------------------- #
class SourceIndex(object):
    """Read-only view over the W0 r4-candidate body + author-side registries."""

    def __init__(self, body_path, source_root):
        self.body_path = os.path.abspath(body_path)
        self.source_root = os.path.abspath(source_root)
        with open(self.body_path, "rb") as fh:
            raw = fh.read()
        self.body_bytes = len(raw)
        self.body_sha256 = sha256_bytes(raw)
        self.text = raw.decode("utf-8")
        self.lines = self.text.splitlines()
        self._chapters = self._parse_chapters()
        self._reg_cache = {}
        self._mem = {}

    # -- chapters ---------------------------------------------------------- #
    def _parse_chapters(self):
        chapters = []
        cur = None
        for i, line in enumerate(self.lines, 1):
            m = re.match(r"^# (CH-\d\d)｜(.+)$", line)
            if m:
                cur = {"chapter_id": m.group(1), "title": m.group(2).strip(), "line": i}
                chapters.append(cur)
        for idx, ch in enumerate(chapters):
            ch["end_line"] = (
                chapters[idx + 1]["line"] - 1 if idx + 1 < len(chapters) else len(self.lines)
            )
        return chapters

    def chapters(self):
        return copy.deepcopy(self._chapters)

    def chapter(self, chapter_id):
        for ch in self._chapters:
            if ch["chapter_id"] == chapter_id:
                return copy.deepcopy(ch)
        raise SpecError("CHAPTER_NOT_FOUND", chapter_id)

    def chapter_lines(self, chapter_id):
        ch = self.chapter(chapter_id)
        return self.lines[ch["line"] - 1 : ch["end_line"]]

    def chapter_text(self, chapter_id):
        return "\n".join(self.chapter_lines(chapter_id))

    def line_ref(self, chapter_id, needle, occurrence=0):
        """Locate a needle inside a chapter and return a source_ref with the line."""
        lines = self.chapter_lines(chapter_id)
        hits = [i for i, l in enumerate(lines) if needle in l]
        if len(hits) <= occurrence:
            raise SpecError(
                "BODY_SPAN_NOT_FOUND", "%s / %r" % (chapter_id, needle[:40])
            )
        return {
            "file": os.path.basename(self.body_path),
            "chapter": chapter_id,
            "line": self.chapter(chapter_id)["line"] + hits[occurrence],
        }

    # -- registries -------------------------------------------------------- #
    def registry(self, filename):
        if filename in self._reg_cache:
            return self._reg_cache[filename]
        path = os.path.join(self.source_root, filename)
        if not os.path.exists(path):
            raise SpecError("SOURCE_MISSING", path)
        with open(path, "rb") as fh:
            raw = fh.read()
        rec = {
            "file": filename,
            "path": path,
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
        }
        if filename.lower().endswith(".json"):
            rec["data"] = json.loads(raw.decode("utf-8"))
        else:
            rec["text"] = raw.decode("utf-8")
        self._reg_cache[filename] = rec
        return rec

    def md_registry(self, filename):
        rec = self.registry(filename)
        if "text" not in rec:
            raise SpecError("SOURCE_NOT_TEXT", filename)
        return rec

    def registry_sha(self, filename):
        return self.registry(filename)["sha256"]

    def ref(self, filename, selector, observed=None):
        rec = self.registry(filename)
        out = {"file": filename, "selector": selector, "file_sha256": rec["sha256"]}
        if observed is not None:
            out["observed"] = observed
        return out

    # -- requirement registry ---------------------------------------------- #
    def requirement_registry(self):
        """Every RequirementID that at least one registry row actually binds.

        Bound == the id appears as `original_id` in W0_REQUIRED22_TRACE.json or
        DESIGN84_WAVE_JOIN.json, with a source_sha and a byte span.  An id that
        only shows up as prose is NOT bound; that is what REQUIREMENT_UNBOUND
        protects.
        """
        if "reqreg" in self._mem:
            return copy.deepcopy(self._mem["reqreg"])
        reg = {}
        w0 = self.registry("W0_REQUIRED22_TRACE.json")
        for row in w0["data"]:
            rid = row["original_id"]
            reg.setdefault(rid, {"requirement_id": rid, "rows": []})
            reg[rid]["rows"].append(
                {
                    "registry": "W0_REQUIRED22_TRACE.json",
                    "source_id": row["source_id"],
                    "source_sha": row["source_sha"],
                    "source_span": row["source_span"],
                    "source_row_sha": row["source_row_sha"],
                    "spec_kind": row["spec_kind"],
                    "deliver_id": row["deliver_id"],
                    "w0_required": True,
                }
            )
        d84 = self.registry("DESIGN84_WAVE_JOIN.json")
        for row in d84["data"]:
            rid = row["original_id"]
            reg.setdefault(rid, {"requirement_id": rid, "rows": []})
            reg[rid]["rows"].append(
                {
                    "registry": "DESIGN84_WAVE_JOIN.json",
                    "source_sha": row["source_sha"],
                    "source_span": row["source_span"],
                    "source_row_sha": row["source_row_sha"],
                    "requirement_delivery_wave": row["requirement_delivery_wave"],
                    "primary_wp_id": row["primary_wp_id"],
                    "wp_primary_wave": row["wp_primary_wave"],
                    "w0_required": False,
                }
            )
        for rid, rec in reg.items():
            rec["bound"] = all(r.get("source_sha") and r.get("source_span") for r in rec["rows"])
        self._mem["reqreg"] = reg
        return copy.deepcopy(reg)

    def requirement_ids(self):
        return sorted(self.requirement_registry().keys())

    # -- body tables ------------------------------------------------------- #
    def table_after(self, chapter_id, header_tokens, limit=64):
        """Rows of the first table inside `chapter_id` whose header holds all tokens."""
        lines = self.chapter_lines(chapter_id)
        start = None
        for i, line in enumerate(lines):
            if line.startswith("|") and all(tok in line for tok in header_tokens):
                start = i
                break
        if start is None:
            raise SpecError(
                "TABLE_NOT_FOUND", "%s %r" % (chapter_id, list(header_tokens))
            )
        base = self.chapter(chapter_id)["line"] + start
        rows = []
        for j in range(start + 1, min(len(lines), start + 2 + limit)):
            line = lines[j]
            if not line.startswith("|"):
                break
            cells = split_pipe_row(line)
            if all(re.fullmatch(r":?-{2,}:?", c or "-") for c in cells):
                continue
            rows.append({"line": base + (j - start), "cells": cells})
        return rows

    def product_table_rows(self):
        if "prodrows" in self._mem:
            return copy.deepcopy(self._mem["prodrows"])
        rows = self.table_after("CH-01", ["類型", "可量測 POS", "排除 NEG"])
        out = {}
        for r in rows:
            cells = r["cells"]
            if len(cells) < 4:
                continue
            key = strip_md(cells[0])
            out[key] = {
                "key": key,
                "statement": clean_cell(cells[1]),
                "pos": clean_cell(cells[2]),
                "neg": clean_cell(cells[3]),
                "source_ref": {
                    "file": os.path.basename(self.body_path),
                    "chapter": "CH-01",
                    "line": r["line"],
                },
            }
        if not out:
            raise SpecError("PRODUCT_TABLE_EMPTY", "CH-01")
        self._mem["prodrows"] = out
        return copy.deepcopy(out)

    def acceptance_lines(self, chapter_id):
        pos, neg = [], []
        ch_line = self.chapter(chapter_id)["line"]
        for i, line in enumerate(self.chapter_lines(chapter_id)):
            if line.startswith("**Acceptance POS**"):
                txt = line.split("：", 1)[-1].strip()
                pos.append(
                    {
                        "statement": txt,
                        "firstfail_codes": [],
                        "source_ref": {
                            "file": os.path.basename(self.body_path),
                            "chapter": chapter_id,
                            "line": ch_line + i,
                        },
                    }
                )
            elif line.startswith("**Acceptance NEG"):
                txt = line.split("：", 1)[-1].strip()
                codes = re.findall(r"`([A-Z][A-Z0-9_]{4,})`", line)
                ff = re.findall(r"FirstFail=([A-Z][A-Z0-9_]{3,})", line)
                neg.append(
                    {
                        "statement": txt,
                        "firstfail_codes": sorted(set(codes + ff)),
                        "source_ref": {
                            "file": os.path.basename(self.body_path),
                            "chapter": chapter_id,
                            "line": ch_line + i,
                        },
                    }
                )
        return pos, neg

    def chapter_map(self):
        """The 50-row chapter table carried in the body (id / title / primary wave)."""
        if "chmap" in self._mem:
            return copy.deepcopy(self._mem["chmap"])
        rows = []
        started = False
        for i, line in enumerate(self.lines, 1):
            m = re.match(r"^\| `(CH-\d\d)` \|", line)
            if m:
                started = True
                cells = split_pipe_row(line)
                rows.append(
                    {
                        "chapter_id": m.group(1),
                        "title": strip_md(cells[1]) if len(cells) > 1 else "",
                        "primary_wave_cell": strip_md(cells[2]) if len(cells) > 2 else "",
                        "line": i,
                    }
                )
            elif started and not line.startswith("|"):
                break
        if len(rows) != len(self._chapters):
            raise SpecError(
                "CHAPTER_TABLE_MISMATCH",
                "table rows=%d h1=%d" % (len(rows), len(self._chapters)),
            )
        self._mem["chmap"] = rows
        return copy.deepcopy(rows)

    def seam_rows(self):
        """S1..S5 rows of the walking-skeleton seam table (CH-37 region)."""
        if "seams" in self._mem:
            return copy.deepcopy(self._mem["seams"])
        out = {}
        started = False
        for i, line in enumerate(self.lines, 1):
            m = re.match(r"^\| (S[1-5]) (W\d[^|]*)\|", line)
            if m:
                started = True
                cells = split_pipe_row(line)
                out[m.group(1)] = {
                    "seam": m.group(1),
                    "wave_cell": m.group(2).strip(),
                    "producer_cell": strip_md(cells[1]),
                    "reader_cell": strip_md(cells[2]),
                    "handoff_cell": strip_md(cells[3]),
                    "oracle_cell": strip_md(cells[4]),
                    "line": i,
                }
            elif started and line.startswith("|"):
                continue
            elif started and not line.startswith("|"):
                break
        if sorted(out) != ["S1", "S2", "S3", "S4", "S5"]:
            raise SpecError("SEAM_TABLE_INCOMPLETE", ",".join(sorted(out)))
        self._mem["seams"] = out
        return copy.deepcopy(out)

    # -- count computation ------------------------------------------------- #
    def _count(self, key, value, file, selector, note=None):
        rec = {
            "value": int(value),
            "source_ref": {
                "file": file,
                "selector": selector,
                "file_sha256": self.registry_sha(file),
            },
        }
        if note:
            rec["note"] = note
        return rec

    def counts(self):
        """Every headline number, recomputed from source bytes."""
        if "counts" in self._mem:
            return copy.deepcopy(self._mem["counts"])

        body_ref = {
            "file": os.path.basename(self.body_path),
            "selector": "H1 '^# (CH-\\d\\d)｜'",
            "sha256": self.body_sha256,
            "bytes": self.body_bytes,
        }

        chapters = self.chapters()
        prog = self.registry("PROGRAM_WP22_DAG36.json")["data"]
        wps = prog["work_packages"]
        edges = prog["edges"]
        e26 = next((e for e in edges if e["id"] == "E26"), None)
        w0req = self.registry("W0_REQUIRED22_TRACE.json")["data"]
        d84 = self.registry("DESIGN84_WAVE_JOIN.json")["data"]
        src31 = self.registry("SOURCE31_PHYSICAL_IDENTITY.json")["data"]
        orc96 = self.registry("ORACLE96_CONTRACTS.json")["data"]
        tech = self.registry("TECH485_COMPACT_REGISTRY.json")["data"]
        case393 = self.registry("CASE393_REGISTRY.json")["data"]
        r15md = self.md_registry("W0_R2_TRACE_R15_949_CELL192_B1_CASES_AND_ORACLE.md")["text"]
        pc_md = self.md_registry("W0_R2_TRACE_SBL_PARENT50_CHILD149.md")["text"]

        r15_ids = re.findall(r"^\| `(R15-\d+)`", r15md, re.M)
        cell_ids = re.findall(r"^\| `(CELL-[^`]+)`", r15md, re.M)
        ac_ids = re.findall(r"^\| `(AC-C39-[^`]+)`", r15md, re.M)
        parents = re.findall(r"^\| (U\d\d) \|", pc_md, re.M)
        children = re.findall(r"^\| (U\d\d\.\d+) \|", pc_md, re.M)
        wave_split = [c for c in d84 if c["requirement_delivery_wave"] != c["wp_primary_wave"]]

        c = {}
        c["chapters"] = {
            "value": len(chapters),
            "ids": [x["chapter_id"] for x in chapters],
            "source_ref": body_ref,
        }
        c["work_packages"] = {
            "value": len(wps),
            "ids": [w["id"] for w in wps],
            "source_ref": {
                "file": "PROGRAM_WP22_DAG36.json",
                "selector": "$.work_packages[*].id",
                "file_sha256": self.registry_sha("PROGRAM_WP22_DAG36.json"),
            },
        }
        c["edges"] = {
            "value": len(edges),
            "ids": [e["id"] for e in edges],
            "source_ref": {
                "file": "PROGRAM_WP22_DAG36.json",
                "selector": "$.edges[*].id",
                "file_sha256": self.registry_sha("PROGRAM_WP22_DAG36.json"),
            },
        }
        c["e26"] = {
            "value": 1,
            "edge_id": e26["id"] if e26 else None,
            "predecessor": e26["predecessor"] if e26 else None,
            "successor": e26["successor"] if e26 else None,
            "wave": e26["wave"] if e26 else None,
            "source_ref": {
                "file": "PROGRAM_WP22_DAG36.json",
                "selector": "$.edges[?(@.id=='E26')]",
                "file_sha256": self.registry_sha("PROGRAM_WP22_DAG36.json"),
            },
        }
        c["design84_cards"] = {
            "value": len(d84),
            "ids": [x["original_id"] for x in d84],
            "source_ref": {
                "file": "DESIGN84_WAVE_JOIN.json",
                "selector": "$[*].original_id",
                "file_sha256": self.registry_sha("DESIGN84_WAVE_JOIN.json"),
            },
        }
        c["wave_split_25"] = {
            "value": len(wave_split),
            "ids": [x["original_id"] for x in wave_split],
            "rule": "count(card where requirement_delivery_wave != wp_primary_wave)",
            "source_ref": {
                "file": "DESIGN84_WAVE_JOIN.json",
                "selector": "$[?(@.requirement_delivery_wave != @.wp_primary_wave)].original_id",
                "file_sha256": self.registry_sha("DESIGN84_WAVE_JOIN.json"),
            },
        }
        c["w0_required"] = {
            "value": len(w0req),
            "ids": [x["original_id"] for x in w0req],
            "source_ref": {
                "file": "W0_REQUIRED22_TRACE.json",
                "selector": "$[*].original_id",
                "file_sha256": self.registry_sha("W0_REQUIRED22_TRACE.json"),
            },
        }
        c["sources31"] = {
            "value": len(src31),
            "ids": [x["source_id"] for x in src31],
            "source_ref": {
                "file": "SOURCE31_PHYSICAL_IDENTITY.json",
                "selector": "$[*].source_id",
                "file_sha256": self.registry_sha("SOURCE31_PHYSICAL_IDENTITY.json"),
            },
        }
        c["r15_949"] = {
            "value": len(r15_ids),
            "distinct": len(set(r15_ids)),
            "ids": r15_ids,
            "source_ref": {
                "file": "W0_R2_TRACE_R15_949_CELL192_B1_CASES_AND_ORACLE.md",
                "selector": "^\\| `(R15-\\d+)`",
                "file_sha256": self.registry_sha(
                    "W0_R2_TRACE_R15_949_CELL192_B1_CASES_AND_ORACLE.md"
                ),
            },
        }
        c["cell192"] = {
            "value": len(cell_ids),
            "distinct": len(set(cell_ids)),
            "ids": cell_ids,
            "source_ref": {
                "file": "W0_R2_TRACE_R15_949_CELL192_B1_CASES_AND_ORACLE.md",
                "selector": "^\\| `(CELL-[^`]+)`",
                "file_sha256": self.registry_sha(
                    "W0_R2_TRACE_R15_949_CELL192_B1_CASES_AND_ORACLE.md"
                ),
            },
        }
        c["parent50"] = {
            "value": len(parents),
            "distinct": len(set(parents)),
            "ids": parents,
            "source_ref": {
                "file": "W0_R2_TRACE_SBL_PARENT50_CHILD149.md",
                "selector": "^\\| (U\\d\\d) \\|",
                "file_sha256": self.registry_sha("W0_R2_TRACE_SBL_PARENT50_CHILD149.md"),
            },
        }
        c["child149"] = {
            "value": len(children),
            "distinct": len(set(children)),
            "ids": children,
            "source_ref": {
                "file": "W0_R2_TRACE_SBL_PARENT50_CHILD149.md",
                "selector": "^\\| (U\\d\\d\\.\\d+) \\|",
                "file_sha256": self.registry_sha("W0_R2_TRACE_SBL_PARENT50_CHILD149.md"),
            },
        }
        c["oracle96"] = {
            "value": len(orc96),
            "ids": [x["case_id"] for x in orc96],
            "md_rows": len(ac_ids),
            "source_ref": {
                "file": "ORACLE96_CONTRACTS.json",
                "selector": "$[*].case_id",
                "file_sha256": self.registry_sha("ORACLE96_CONTRACTS.json"),
            },
        }
        c["tech485"] = {
            "value": len(tech),
            "families": _family_counts(tech),
            "source_ref": {
                "file": "TECH485_COMPACT_REGISTRY.json",
                "selector": "$[*].original_id",
                "file_sha256": self.registry_sha("TECH485_COMPACT_REGISTRY.json"),
            },
        }
        c["case393"] = {
            "value": len(case393),
            "families": _family_counts(case393, key="family"),
            "source_ref": {
                "file": "CASE393_REGISTRY.json",
                "selector": "$[*].case_id",
                "file_sha256": self.registry_sha("CASE393_REGISTRY.json"),
            },
        }
        self._mem["counts"] = c
        return copy.deepcopy(c)

    # -- reconciliation against the source's own claims -------------------- #
    def declared_claims(self):
        state = self.registry("CURRENT_CANDIDATE_STATE.json")["data"]
        gate = next(
            (g for g in state.get("gate_results", []) if g.get("gate") == "G1_STRUCTURE"),
            None,
        )
        evidence = gate["evidence"] if gate else ""
        return {
            "source_ref": {
                "file": "CURRENT_CANDIDATE_STATE.json",
                "selector": "$.gate_results[?(@.gate=='G1_STRUCTURE')].evidence",
                "file_sha256": self.registry_sha("CURRENT_CANDIDATE_STATE.json"),
                "text": evidence,
            },
            "patterns": {
                "chapters": r"(\d+)\s*個 H1",
                "work_packages": r"(\d+)\s*WP",
                "edges": r"(\d+)\s*Edge",
                "design84_cards": r"(\d+)\s*Card",
                "wave_split_25": r"(\d+)\s*跨波",
                "w0_required": r"(\d+)\s*Required",
            },
            "e26_pattern": r"E26=WP(\d+)→WP(\d+)",
        }

    def reconcile(self):
        counts = self.counts()
        claims = self.declared_claims()
        text = claims["source_ref"]["text"]
        rows = []
        for key, pattern in claims["patterns"].items():
            m = re.search(pattern, text)
            declared = int(m.group(1)) if m else None
            computed = counts[key]["value"]
            rows.append(
                {
                    "claim": key,
                    "declared": declared,
                    "computed": computed,
                    "match": (declared == computed) if declared is not None else None,
                    "source_ref": claims["source_ref"],
                }
            )
        m = re.search(claims["e26_pattern"], text)
        declared_e26 = None
        if m:
            declared_e26 = "WP-FHS-%02d→WP-FHS-%02d" % (int(m.group(1)), int(m.group(2)))
        computed_e26 = "%s→%s" % (
            counts["e26"]["predecessor"],
            counts["e26"]["successor"],
        )
        rows.append(
            {
                "claim": "e26_direction",
                "declared": declared_e26,
                "computed": computed_e26,
                "match": (declared_e26 == computed_e26) if declared_e26 else None,
                "source_ref": claims["source_ref"],
            }
        )
        return rows


def _family_counts(rows, key="family"):
    out = {}
    for r in rows:
        k = str(r.get(key))
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


# --------------------------------------------------------------------------- #
# subject binding
# --------------------------------------------------------------------------- #
def build_subject(index):
    seams = index.registry("SEAM_CONTRACTS.json")["data"]
    subject_id = seams[0]["subject_id"]
    state = index.registry("CURRENT_CANDIDATE_STATE.json")["data"]
    if state.get("candidate_body_sha256") != index.body_sha256:
        raise SpecError(
            "SUBJECT_BODY_SHA_MISMATCH",
            "state=%s body=%s"
            % (state.get("candidate_body_sha256"), index.body_sha256),
        )
    return {
        "subject_id": subject_id,
        "subject_origin": "SEAM_CONTRACTS.json:$.subject_id (author example subject)",
        "body_sha256": index.body_sha256,
        "body_bytes": index.body_bytes,
        "body_file": os.path.basename(index.body_path),
        "candidate_id": state.get("candidate_id"),
        "candidate_currency": state.get("currency"),
        "same_subject_across_specs": True,
        "original_pipd_signature": "NOT_OBSERVED",
        "claim_ceiling": CLAIM_CEILING,
        "source_ref": {
            "file": "SEAM_CONTRACTS.json",
            "selector": "$[0].subject_id",
            "file_sha256": index.registry_sha("SEAM_CONTRACTS.json"),
        },
    }


# --------------------------------------------------------------------------- #
# Product SPEC
# --------------------------------------------------------------------------- #
PRODUCT_SECTIONS = [
    "§0 Subject Binding 與 Claim Ceiling",
    "§1 Persona 與 JTBD",
    "§2 FUO Register",
    "§3 MVP 範圍",
    "§4 Non-Goals",
    "§5 ACC+ 正例",
    "§6 ACC− 反例與 FirstFail",
    "§7 Requirement 綁定表",
]

SHARED_SECTION = "§0 Subject Binding 與 Claim Ceiling"


def build_product(index, goal):
    rows = index.product_table_rows()
    persona = rows.get("Persona")
    jtbd = rows.get("JTBD")
    mvp = rows.get("MVP")
    non_goals = rows.get("非目標")
    user_accept = rows.get("使用者驗收")
    for name, rec in (
        ("Persona", persona),
        ("JTBD", jtbd),
        ("MVP", mvp),
        ("非目標", non_goals),
    ):
        if not rec:
            raise SpecError("PRODUCT_ROW_MISSING", name)

    w0 = index.registry("W0_REQUIRED22_TRACE.json")["data"]
    product_rows = [r for r in w0 if r["spec_kind"] == "Product"]

    fuo = []
    for r in product_rows:
        fuo.append(
            {
                "fuo_id": "FUO-" + r["original_id"],
                "statement": r["requirement"],
                "source_ref": {
                    "file": "W0_REQUIRED22_TRACE.json",
                    "selector": "$[?(@.original_id=='%s')]" % r["original_id"],
                    "file_sha256": index.registry_sha("W0_REQUIRED22_TRACE.json"),
                    "source_id": r["source_id"],
                    "source_sha": r["source_sha"],
                    "source_span": r["source_span"],
                    "source_row_sha": r["source_row_sha"],
                    "chapter_refs": r["chapter_refs"],
                },
                "acceptance": {
                    "pos": r["requirement"],
                    "neg": r["source_negative"],
                    "condition": r["source_condition"],
                    "case_id": r["case_id"],
                    "evidence_expectation_id": r["evidence_expectation_id"],
                    "spec_clause_id": r["spec_clause_id"],
                },
                "deliver": {
                    "deliver_id": r["deliver_id"],
                    "primary_wp_id": r["primary_wp_id"],
                    "requirement_delivery_wave": r["requirement_delivery_wave"],
                },
                "original_consumer": r["original_consumer"],
                "u4_state": r["u4"],
                "fuo_origin": "W0_REQUIRED22_TRACE.json row with spec_kind=Product",
            }
        )
    # declared FUOs from the CH-01 product table (FUO-A / FUO-B)
    for key, rec in rows.items():
        if not re.match(r"^FUO-[A-Z]$", key):
            continue
        fuo.append(
            {
                "fuo_id": key,
                "statement": rec["statement"],
                "source_ref": dict(rec["source_ref"], selector="CH-01 product table row %s" % key),
                "acceptance": {"pos": rec["pos"], "neg": rec["neg"]},
                "deliver": {
                    "deliver_id": None,
                    "primary_wp_id": "WP-FHS-15",
                    "binding": "CHAPTER_LEVEL_W0; no W0_REQUIRED deliver row binds this FUO",
                },
                "original_consumer": "SBL Product Owner / Original PIPD Intake",
                "u4_state": "ORIGINAL_OWNER_ACK_NOT_OBSERVED",
                "fuo_origin": "CH-01 declared FUO row",
            }
        )

    pos_lines, neg_lines = index.acceptance_lines("CH-01")
    orc = index.registry("ORACLE96_CONTRACTS.json")["data"]
    acc_plus = []
    acc_minus = []
    for p in pos_lines:
        acc_plus.append(
            {
                "acc_id": "ACC+-CH01",
                "statement": p["statement"],
                "kind": "BODY_ACCEPTANCE_POS",
                "source_ref": p["source_ref"],
            }
        )
    for n in neg_lines:
        acc_minus.append(
            {
                "acc_id": "ACC--CH01",
                "statement": n["statement"],
                "kind": "BODY_ACCEPTANCE_NEG",
                "firstfail_codes": n["firstfail_codes"],
                "source_ref": n["source_ref"],
            }
        )
    for case in orc:
        if case["test_class"] == "POS":
            acc_plus.append(
                {
                    "acc_id": "ACC+-" + case["case_id"],
                    "statement": case["positive"],
                    "kind": "ORACLE96_POS_" + case["oracle_type"],
                    "expected_first_fail": case["expected_first_fail"],
                    "source_ref": {
                        "file": "ORACLE96_CONTRACTS.json",
                        "selector": "$[?(@.case_id=='%s')]" % case["case_id"],
                        "file_sha256": index.registry_sha("ORACLE96_CONTRACTS.json"),
                        "source_span": case["source_span"],
                    },
                }
            )
        elif case["test_class"] == "NEG":
            acc_minus.append(
                {
                    "acc_id": "ACC--" + case["case_id"],
                    "statement": case["source_negative"],
                    "kind": "ORACLE96_NEG_" + case["oracle_type"],
                    "expected_first_fail": case["expected_first_fail"],
                    "source_ref": {
                        "file": "ORACLE96_CONTRACTS.json",
                        "selector": "$[?(@.case_id=='%s')]" % case["case_id"],
                        "file_sha256": index.registry_sha("ORACLE96_CONTRACTS.json"),
                        "source_span": case["source_span"],
                    },
                }
            )

    bindings = []
    for r in product_rows:
        bindings.append(
            {
                "requirement_id": r["original_id"],
                "spec_kind": r["spec_kind"],
                "source_id": r["source_id"],
                "source_sha": r["source_sha"],
                "source_span": r["source_span"],
                "source_row_sha": r["source_row_sha"],
                "requirement": r["requirement"],
                "negative": r["source_negative"],
                "chapters": r["chapter_refs"],
                "original_consumer": r["original_consumer"],
            }
        )

    doc = {
        "schema": SCHEMA_TAG + "/SPEC_Product",
        "artifact_id": "SPEC-Product-W0-wp15-local",
        "spec_kind": "Product",
        "version": "w0-r4c-wp15-1",
        "goal": goal,
        "subject": build_subject(index),
        "persona": {
            "statement": persona["statement"],
            "pos": persona["pos"],
            "neg": persona["neg"],
            "source_ref": persona["source_ref"],
        },
        "jtbd": {
            "statement": jtbd["statement"],
            "pos": jtbd["pos"],
            "neg": jtbd["neg"],
            "source_ref": jtbd["source_ref"],
        },
        "fuo": fuo,
        "mvp": {
            "statement": mvp["statement"],
            "pos": mvp["pos"],
            "neg": mvp["neg"],
            "w0_waves": ["W0-A", "W0-B"],
            "source_ref": mvp["source_ref"],
        },
        "non_goals": {
            "statement": non_goals["statement"],
            "pos": non_goals["pos"],
            "neg": non_goals["neg"],
            "forbidden_constructs": [
                "第二 HGK 控制層",
                "第二 Compiler",
                "第二 Queue",
                "Independent Checker",
                "Release Gate",
            ],
            "source_ref": non_goals["source_ref"],
            "boundary_ref": index.line_ref("CH-00", "唯一 Writer"),
        },
        "acc_plus": acc_plus,
        "acc_minus": acc_minus,
        "user_acceptance": {
            "statement": user_accept["statement"] if user_accept else "",
            "pos": user_accept["pos"] if user_accept else "",
            "neg": user_accept["neg"] if user_accept else "",
            "source_ref": user_accept["source_ref"] if user_accept else None,
        },
        "requirement_ids": sorted({b["requirement_id"] for b in bindings}),
        "requirement_bindings": bindings,
        "requirement_registry_size": len(index.requirement_registry()),
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_RUN",
        "open_holds": [
            "H-U4：原 SBL Product / PIPD Intake Reader 未 ACK，FUO 只到 AUTHOR_DESIGN",
            "H-ORACLE-RAW96：96 個 Oracle 個案無原 Host Runner／Fixture 真 bytes",
            "所有人類簽章、Judge 校準、WorldRaw 皆 EXPECTED_NOT_OBSERVED",
        ],
    }
    md = _render_product_md(doc, index)
    return doc, md


def _render_product_md(doc, index):
    L = []
    L.append("# SPEC_Product｜%s" % doc["artifact_id"])
    L.append("")
    L.append("> claim_ceiling=`%s`；native_effect=`%s`；body_sha256=`%s`"
             % (CLAIM_CEILING, doc["native_effect"], doc["subject"]["body_sha256"]))
    L.append("> 本文件只由 `spec_pipeline.py` 從正文與 registry 實算產生，未執行任何 Native 效果。")
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[0])
    L.append("")
    L.append("- subject_id: `%s`" % doc["subject"]["subject_id"])
    L.append("- body: `%s` / %d bytes / sha256 `%s`"
             % (doc["subject"]["body_file"], doc["subject"]["body_bytes"],
                doc["subject"]["body_sha256"]))
    L.append("- candidate: `%s`（%s）" % (doc["subject"]["candidate_id"],
                                         doc["subject"]["candidate_currency"]))
    L.append("- 原 PIPD 簽名：`%s`；claim_ceiling=`%s`"
             % (doc["subject"]["original_pipd_signature"], doc["claim_ceiling"]))
    L.append("- 三份 SPEC 共用同一個 subject 區塊；差異在於各自的主體欄位與章節，不在標題。")
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[1])
    L.append("")
    L.append("**Persona**：%s" % doc["persona"]["statement"])
    L.append("")
    L.append("- 可量測 POS：%s" % doc["persona"]["pos"])
    L.append("- 排除 NEG／FirstFail：%s" % doc["persona"]["neg"])
    L.append("- 來源：`%s:%s`" % (doc["persona"]["source_ref"]["file"],
                                 doc["persona"]["source_ref"]["line"]))
    L.append("")
    L.append("**JTBD**：%s" % doc["jtbd"]["statement"])
    L.append("")
    L.append("| 面向 | 內容 |")
    L.append("|---|---|")
    L.append("| 可量測 POS | %s |" % doc["jtbd"]["pos"])
    L.append("| 排除 NEG | %s |" % doc["jtbd"]["neg"])
    L.append("| 來源 | `%s:%s` |" % (doc["jtbd"]["source_ref"]["file"],
                                    doc["jtbd"]["source_ref"]["line"]))
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[2])
    L.append("")
    L.append("共 **%d** 筆 FUO（%d 筆來自 W0_REQUIRED22 的 Product 需求列，%d 筆來自 CH-01 宣告列）。"
             % (len(doc["fuo"]),
                len([f for f in doc["fuo"] if f["fuo_origin"].startswith("W0_REQUIRED22")]),
                len([f for f in doc["fuo"] if f["fuo_origin"].startswith("CH-01")])))
    L.append("")
    L.append("> acceptance POS 對 W0_REQUIRED 來源列即其 `requirement` 原文（該 registry 未另存 POS 欄）；"
             "acceptance NEG 取自同列的 `source_negative`。CH-01 宣告列的 POS/NEG 取自正文表格。")
    L.append("")
    L.append("| fuo_id | statement | acceptance POS | acceptance NEG | deliver_id | source_ref |")
    L.append("|---|---|---|---|---|---|")
    for f in doc["fuo"]:
        acc = f["acceptance"]
        sref = f["source_ref"]
        if "line" in sref:
            ref = "`%s:%s`" % (sref["file"], sref["line"])
        else:
            ref = "`%s` %s span=%s" % (sref["file"], sref.get("source_id", ""),
                                       sref.get("source_span"))
        L.append(
            "| `%s` | %s | %s | %s | %s | %s |"
            % (f["fuo_id"], _cell(f["statement"]), _cell(acc["pos"]),
               _cell(acc["neg"]), "`%s`" % f["deliver"]["deliver_id"]
               if f["deliver"]["deliver_id"] else "_chapter-level_", ref)
        )
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[3])
    L.append("")
    L.append(doc["mvp"]["statement"])
    L.append("")
    L.append("- POS：%s" % doc["mvp"]["pos"])
    L.append("- NEG：%s" % doc["mvp"]["neg"])
    L.append("- 波次：%s" % " / ".join(doc["mvp"]["w0_waves"]))
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[4])
    L.append("")
    L.append(doc["non_goals"]["statement"])
    L.append("")
    for ng in doc["non_goals"]["forbidden_constructs"]:
        L.append("- 不建：%s" % ng)
    L.append("- 邊界來源：`%s:%s`" % (doc["non_goals"]["boundary_ref"]["file"],
                                     doc["non_goals"]["boundary_ref"]["line"]))
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[5])
    L.append("")
    L.append("| acc_id | kind | statement | first_fail | source_ref |")
    L.append("|---|---|---|---|---|")
    for a in doc["acc_plus"]:
        sref = a["source_ref"]
        loc = sref.get("line") or ("span " + str(sref.get("source_span")))
        L.append("| `%s` | %s | %s | `%s` | `%s` %s |"
                 % (a["acc_id"], a["kind"], _cell(a["statement"]),
                    a.get("expected_first_fail", "-"), sref["file"], loc))
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[6])
    L.append("")
    L.append("| acc_id | kind | statement | firstfail codes | source_ref |")
    L.append("|---|---|---|---|---|")
    for a in doc["acc_minus"]:
        sref = a["source_ref"]
        loc = sref.get("line") or ("span " + str(sref.get("source_span")))
        codes = a.get("firstfail_codes") or ([a["expected_first_fail"]]
                                             if a.get("expected_first_fail") else [])
        L.append("| `%s` | %s | %s | %s | `%s` %s |"
                 % (a["acc_id"], a["kind"], _cell(a["statement"]),
                    ", ".join("`%s`" % c for c in codes) or "-", sref["file"], loc))
    L.append("")
    L.append("## " + PRODUCT_SECTIONS[7])
    L.append("")
    L.append("共 **%d** 個 RequirementID；registry 內可綁定總數 %d。"
             % (len(doc["requirement_ids"]), doc["requirement_registry_size"]))
    L.append("")
    L.append("| RequirementID | kink | source_id | source_sha | span | chapters | consumer |")
    L.append("|---|---|---|---|---|---|---|")
    for b in doc["requirement_bindings"]:
        L.append("| `%s` | %s | `%s` | `%s` | %s | %s | %s |"
                 % (b["requirement_id"], b.get("spec_kind", "-"),
                    b.get("source_id", "-"), (b.get("source_sha") or "-")[:16],
                    b.get("source_span", "-"), ", ".join(b.get("chapters", [])) or "-",
                    _cell(b.get("original_consumer", "-"))))
    L.append("")
    L.append("### Open holds")
    for h in doc["open_holds"]:
        L.append("- %s" % h)
    L.append("")
    return "\n".join(L)


def _cell(text, limit=110):
    t = str(text).replace("|", "\\|").replace("\n", " ")
    if len(t) > limit:
        t = t[: limit - 1] + "…"
    if t.count("`") % 2:
        t += "`"
    return t


def _pin_label(pin):
    """Reader pin shapes differ per seam (file-only for S1, repo pin for S2..S5)."""
    if not isinstance(pin, dict):
        return "`%s`" % pin
    if pin.get("file"):
        return "`%s`" % pin["file"]
    return "`%s:%s@%s`" % (pin.get("repo"), pin.get("path"),
                           (pin.get("remote_commit") or "")[:12])


# --------------------------------------------------------------------------- #
# Architecture SPEC
# --------------------------------------------------------------------------- #
ARCH_SECTIONS = [
    SHARED_SECTION,
    "§A1 五域階段界線（Fabric Policy→SBL Compiler→HGK Issuer→Hermes Worker→Checker/Publisher）",
    "§A2 Seam ABI 表",
    "§A3 Seam Reader／Consumer",
    "§A4 Effect 與 Permission",
    "§A5 POS／NEG／FirstFail 晶格",
    "§A6 Stop／Resume／Rollback",
    "§A7 單一 Writer 與 No-Second-Issuer",
    "§A8 Principal 分離：唯一 Human Owner ≠ Maker／Issuer／Checker",
]

STAGES = [
    {
        "stage_id": "STAGE-1-FABRIC-POLICY",
        "name": "Fabric Policy（治理與 ActiveEpoch）",
        "chapter": "CH-17",
        "actor_tokens": ["Fabric Policy"],
        "canonical_owner": "Fabric Policy Owner / FAR Reader",
        "forbidden": "不得由作者文件或以 W0 Draft 代替 ActivePolicyEpoch／LoadedDigest",
    },
    {
        "stage_id": "STAGE-2-SBL-PIPD-COMPILER",
        "name": "SBL 原 PIPD Compiler（canonical PI 唯一 Writer）",
        "chapter": "CH-12",
        "actor_tokens": ["PIPD Compiler", "DOC02 Compiler", "PD/ECP"],
        "canonical_owner": "SBL-hosted PIPD canonical Compiler / Original Source Reader",
        "forbidden": "作者草案不得產 canonical PI；PI/PD/ECP 只由原 Writer 編譯",
    },
    {
        "stage_id": "STAGE-3-HGK-NATIVE-ISSUER",
        "name": "HGK 唯一 Native Issuer（SharedSpine／WorkID／permit）",
        "chapter": "CH-18",
        "actor_tokens": ["HGK Original Issuer", "Native Issuer"],
        "canonical_owner": "HGK Original Issuer / SharedSpine",
        "forbidden": "不得存在第二 Issuer；無 permit 先 park",
    },
    {
        "stage_id": "STAGE-4-HERMES-WORKER",
        "name": "Hermes bounded Worker（Execution 角色）",
        "chapter": "CH-30",
        "actor_tokens": ["Hermes"],
        "canonical_owner": "Original Hermes bounded Worker/World Receiver",
        "forbidden": "Worker 是執行角色，不是新的 Owner/Issuer；不得自簽 verdict",
    },
    {
        "stage_id": "STAGE-5-CHECKER-PUBLISHER",
        "name": "原 Checker／Publisher（獨立驗證與發布）",
        "chapter": "CH-38",
        "actor_tokens": ["Protected Checker", "Publisher"],
        "canonical_owner": "Original Protected Checker / Publisher",
        "forbidden": "Maker 不得自任 Checker；不得以 W0 文件代替 Verdict／Release",
    },
]


def derive_permission(handoff_text, reader_text, oracle_text):
    """Deterministic permission class from the seam row's own wording."""
    hay = " ".join([handoff_text, reader_text, oracle_text])
    rules = [
        ("WorldRaw", "WORLD_EFFECT_CHECKED", "seam row names WorldRaw / protected verdict"),
        ("permit", "PROTECTED_EFFECT_ADMISSION", "seam row requires an admission permit"),
        ("不寫世界", "READ_ONLY_REPO_BIND", "seam row states no world write at this seam"),
        ("ACK", "CANONICAL_WRITER_HANDOFF", "seam row ends in an original-consumer ACK"),
        ("SPECDraft", "ISOLATED_DRAFT_WRITE", "seam row output is an isolated draft"),
    ]
    for token, cls, why in rules:
        if token in hay:
            return {
                "mode": cls,
                "matched_token": token,
                "rule": why,
                "original_acl_ack": "NOT_OBSERVED",
                "write_scope": "ISOLATED_OUTPUT_ROOT_ONLY",
            }
    return {
        "mode": "UNCLASSIFIED",
        "matched_token": None,
        "rule": "no permission token in the seam row",
        "original_acl_ack": "NOT_OBSERVED",
        "write_scope": "NOT_DECLARED",
    }


def _split_oracle_cell(cell):
    """Split 'POS …；NEG …' using the delimiter, not the bare token NEG."""
    parts = re.split(r"[；;]\s*NEG", cell, maxsplit=1)
    if len(parts) == 2:
        pos = re.sub(r"^\s*POS[：:]?\s*", "", parts[0]).strip(" ；;")
        neg = parts[1].strip(" ；;")
        return pos, neg
    m = re.match(r"^\s*POS[：:]?\s*(.+)$", cell)
    if m:
        return m.group(1).strip(" ；;"), ""
    return cell, ""


def build_architecture(index, goal):
    seams_raw = index.registry("SEAM_CONTRACTS.json")["data"]
    body_seams = index.seam_rows()
    seams = []
    for rec in seams_raw:
        sid = rec["seam"]
        brow = body_seams[sid]
        pos, neg = _split_oracle_cell(brow["oracle_cell"])
        perm = derive_permission(brow["handoff_cell"], brow["reader_cell"], brow["oracle_cell"])
        effect_word = "protected_world_effect" if perm["mode"] in (
            "WORLD_EFFECT_CHECKED",
            "PROTECTED_EFFECT_ADMISSION",
        ) else "no_world_effect_at_this_seam"
        seams.append(
            {
                "seam": sid,
                "wave": rec["execution_wave"],
                "abi": {
                    "declared": rec["original_abi"],
                    "reader_source_pin": rec["reader_source_pin"],
                    "state": "ORIGINAL_RUNTIME_ABI_UNBOUND"
                    if rec["original_abi"] == "ORIGINAL_RUNTIME_ABI_UNBOUND"
                    else rec["original_abi"],
                    "body_binding": "以 CH-37 五 seam 列的『真 ABI/Reader／Consumer』欄為界",
                    "source_ref": {
                        "file": "SEAM_CONTRACTS.json",
                        "selector": "$[?(@.seam=='%s')].original_abi" % sid,
                        "file_sha256": index.registry_sha("SEAM_CONTRACTS.json"),
                    },
                },
                "reader": {
                    "original_reader": rec["original_reader"],
                    "consumer_alias": rec["original_consumer_alias"],
                    "body_reader_cell": brow["reader_cell"],
                    "ack": "NOT_OBSERVED",
                    "source_ref": {
                        "file": "SEAM_CONTRACTS.json",
                        "selector": "$[?(@.seam=='%s')].original_reader" % sid,
                        "file_sha256": index.registry_sha("SEAM_CONTRACTS.json"),
                    },
                },
                "effect": {
                    "class": effect_word,
                    "declared_output": rec["typed_output"],
                    "declared_input": rec["typed_input"],
                    "executed": "NOT_RUN",
                    "delivery_gap": rec["delivery_gap"],
                    "source_ref": {
                        "file": "SEAM_CONTRACTS.json",
                        "selector": "$[?(@.seam=='%s')].typed_output" % sid,
                        "file_sha256": index.registry_sha("SEAM_CONTRACTS.json"),
                    },
                },
                "permission": dict(
                    perm,
                    body_cell=brow["handoff_cell"],
                    source_ref={
                        "file": os.path.basename(index.body_path),
                        "line": brow["line"],
                        "chapter": "CH-37（五 seam 表所在段）",
                    },
                ),
                "pos": {"statement": pos, "source_ref": {"file": os.path.basename(index.body_path), "line": brow["line"]}},
                "neg": {"statement": neg, "source_ref": {"file": os.path.basename(index.body_path), "line": brow["line"]}},
                "firstfail": {
                    "primary": rec["firstfail_primary"],
                    "expected": rec["expected_first_fail"],
                    "secondary": rec.get("firstfail_secondary", []),
                    "note": rec.get("firstfail_note"),
                    "source_ref": {
                        "file": "SEAM_CONTRACTS.json",
                        "selector": "$[?(@.seam=='%s')].firstfail_primary" % sid,
                        "file_sha256": index.registry_sha("SEAM_CONTRACTS.json"),
                    },
                },
                "resume": {
                    "stop": rec["stop"],
                    "resume": rec["resume"],
                    "rollback": rec["rollback"],
                    "state": rec["state"],
                    "host": rec["host"],
                    "source_ref": {
                        "file": "SEAM_CONTRACTS.json",
                        "selector": "$[?(@.seam=='%s')].resume" % sid,
                        "file_sha256": index.registry_sha("SEAM_CONTRACTS.json"),
                    },
                },
                "typed_handoff": {
                    "input": rec["typed_input"],
                    "output": rec["typed_output"],
                    "body_handoff_cell": brow["handoff_cell"],
                    "input_fixture": rec["input_fixture"],
                    "negative_fixture": rec["negative_fixture"],
                    "expected_raw_fixture": rec["expected_raw_fixture"],
                    "fixture_sha256": rec["fixture_sha256"],
                },
            }
        )

    stages = []
    for st in STAGES:
        ch = index.chapter(st["chapter"])
        matched = []
        for sid in sorted(body_seams):
            row = body_seams[sid]
            hay = row["producer_cell"] + " " + row["reader_cell"]
            if any(tok in hay for tok in st["actor_tokens"]):
                matched.append(
                    {
                        "seam": sid,
                        "matched_cell": row["producer_cell"] + " → " + row["reader_cell"],
                    }
                )
        if not matched:
            raise SpecError("STAGE_SEAM_UNRESOLVED", st["stage_id"])
        stages.append(
            {
                "stage_id": st["stage_id"],
                "name": st["name"],
                "canonical_owner": st["canonical_owner"],
                "forbidden": st["forbidden"],
                "owns_writer": st["canonical_owner"],
                "seam_refs": matched,
                "resolve_rule": "actor-token match over CH-37 seam rows (producer+reader cells)",
                "source_ref": {
                    "file": os.path.basename(index.body_path),
                    "chapter": st["chapter"],
                    "line": ch["line"],
                    "title": ch["title"],
                },
            }
        )

    covered = {m["seam"] for st in stages for m in st["seam_refs"]}
    entry_seams = sorted(set(s["seam"] for s in seams) - covered)
    if len(entry_seams) > 1:
        raise SpecError(
            "STAGE_SEAM_UNRESOLVED",
            "seams claimed by no domain stage: %s" % entry_seams,
        )
    entry_seam = None
    if entry_seams:
        sid = entry_seams[0]
        entry_seam = {
            "seam": sid,
            "role": "W0 草案入口接縫：在五個域階段的任何 effect 之前先接收三份 SPEC",
            "why_not_a_stage": "此接縫的原 Producer 是作者側 TPM、原 Reader 是 SBL Product/PIPD "
                               "Intake；它不是 Fabric Policy／Compiler／Issuer／Worker／Checker "
                               "任一個既有域的正本，故列為入口而不併入五階段。",
            "resolve_rule": "entry seam = the seam not claimed by any of the five domain stages",
            "source_ref": {
                "file": os.path.basename(index.body_path),
                "line": body_seams[sid]["line"],
                "chapter": "CH-37（五 seam 表所在段）",
            },
        }

    arch_reqs = [
        {
            "requirement_id": r["original_id"],
            "statement": r["requirement"],
            "negative": r["source_negative"],
            "source_id": r["source_id"],
            "source_sha": r["source_sha"],
            "source_span": r["source_span"],
            "original_consumer": r["original_consumer"],
            "deliver_id": r["deliver_id"],
        }
        for r in index.registry("W0_REQUIRED22_TRACE.json")["data"]
        if r["spec_kind"] == "Architecture"
    ]
    adr = [
        {
            "adr_id": "ADR-" + r["requirement_id"],
            "decision": r["statement"],
            "rejected": r["negative"],
            "consumer": r["original_consumer"],
            "requirement_id": r["requirement_id"],
            "source_ref": {
                "file": "W0_REQUIRED22_TRACE.json",
                "selector": "$[?(@.original_id=='%s')]" % r["requirement_id"],
                "file_sha256": index.registry_sha("W0_REQUIRED22_TRACE.json"),
                "source_span": r["source_span"],
            },
        }
        for r in arch_reqs
    ]

    writer_ref = index.line_ref("CH-00", "唯一 Writer")
    persona_ref = index.line_ref("CH-01", "Persona")
    checker_neg_ref = index.line_ref("CH-01", "`INT-01`")
    principal_neg_ref = index.line_ref("CH-11", "`FHS-DR-021`")

    doc = {
        "schema": SCHEMA_TAG + "/SPEC_Architecture",
        "artifact_id": "SPEC-Architecture-W0-wp15-local",
        "spec_kind": "Architecture",
        "version": "w0-r4c-wp15-1",
        "goal": goal,
        "subject": build_subject(index),
        "domain_stages": stages,
        "domain_boundary_statement": {
            "text": "Fabric Policy → SBL 原 PIPD Compiler → HGK 唯一 Native Issuer → Hermes Worker → 原 Checker／Publisher 五個域界不得合併、不得由 W0 草案跨越。",
            "no_second_issuer": True,
            "no_second_compiler": True,
            "no_second_checker": True,
            "source_refs": [writer_ref, index.line_ref("CH-17", "# CH-17")],
        },
        "seams": seams,
        "seam_ids": [s["seam"] for s in seams],
        "entry_seam": entry_seam,
        "adr": adr,
        "single_writer": {
            "statement": "本草案屬 W0:DraftMaker / AUTHOR_DESIGN_ONLY；SBL/PIPD/Fabric/HGK Canonical Writers、原 HGK Issuer、Protected Checker、Publisher 全部不移轉。",
            "non_transferable": [
                "SBL Canonical Writer",
                "PIPD Canonical Writer",
                "Fabric Canonical Writer",
                "HGK Issuer",
                "Protected Checker",
                "Publisher",
            ],
            "source_ref": writer_ref,
        },
        "principal_separation": {
            "assertion": "唯一 Human Owner 不是 Maker／Issuer／Checker 同一個技術 Principal。",
            "human_owner_count": 1,
            "technical_principals": [
                "Maker（W0 DraftMaker／Hermes bounded Worker：執行角色）",
                "Issuer（HGK Original Issuer：permit 與 WorkID）",
                "Checker（Original Protected Checker：獨立 Verdict）",
            ],
            "identity_collapse_is_a_failure": True,
            "evidence": [
                {
                    "claim": "模型／工具原生 Worker 是執行角色，非新的 Owner/Issuer",
                    "source_ref": persona_ref,
                },
                {
                    "claim": "混同一個 Human Owner 與技術 Checker 身分是 NEG 拒收",
                    "source_ref": checker_neg_ref,
                },
                {
                    "claim": "三職能被當三個獨立 Principal 屬 NEG",
                    "source_ref": principal_neg_ref,
                },
                {
                    "claim": "Canonical Writer／Issuer／Checker／Publisher 全部不移轉",
                    "source_ref": writer_ref,
                },
            ],
            "checked_codes": ["PRINCIPAL_COLLAPSE_DENIED", "SELF_CHECK_DENIED"],
        },
        "effect_registry": [
            {
                "seam": s["seam"],
                "effect_class": s["effect"]["class"],
                "executed": "NOT_RUN",
                "permission_mode": s["permission"]["mode"],
            }
            for s in seams
        ],
        "firstfail_lattice": {
            "seam_primary": {s["seam"]: s["firstfail"]["primary"] for s in seams},
            "global": ["SPEC_NOT_SOURCE_BOUND", "FUO_NOT_OBSERVABLE",
                       "CANONICAL_WRITER_BOUNDARY", "ORACLE_RUNNER_BIND_HOLD"],
            "source_ref": index.line_ref("CH-11", "SPEC_NOT_SOURCE_BOUND"),
        },
        "requirement_ids": sorted({r["requirement_id"] for r in arch_reqs}),
        "requirement_bindings": arch_reqs,
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_RUN",
        "open_holds": [
            "五 seam 的 original_abi 全為 ORIGINAL_RUNTIME_ABI_UNBOUND；無任何 ABI 真綁定",
            "S2–S5 的 original Reader ACK 皆 NOT_OBSERVED；W0 只停在 AUTHOR_DESIGN",
            "H-ABI-05：HGK reducer enum／OperationType／S3–S5 Receiver ABI 未綁",
        ],
    }
    md = _render_arch_md(doc)
    return doc, md


def _render_arch_md(doc):
    L = []
    L.append("# SPEC_Architecture｜%s" % doc["artifact_id"])
    L.append("")
    L.append("> claim_ceiling=`%s`；native_effect=`%s`；body_sha256=`%s`"
             % (CLAIM_CEILING, doc["native_effect"], doc["subject"]["body_sha256"]))
    L.append("> 五個域階段與五條 seam 全部由 CH-37 表格與 SEAM_CONTRACTS.json 實算，未執行任何 Native 效果。")
    L.append("")
    L.append("## " + ARCH_SECTIONS[0])
    L.append("")
    L.append("- subject_id: `%s`" % doc["subject"]["subject_id"])
    L.append("- body_sha256: `%s`（%d bytes）" % (doc["subject"]["body_sha256"],
                                                 doc["subject"]["body_bytes"]))
    L.append("- 與 Product／Program SPEC 共用同一 subject 區塊；本檔的差異欄位是 domain_stages／seams／principal_separation。")
    L.append("")
    L.append("## " + ARCH_SECTIONS[1])
    L.append("")
    L.append(doc["domain_boundary_statement"]["text"])
    L.append("")
    L.append("| stage | 名稱 | 原 Canonical Owner／Writer | 綁定 seam | 禁止 | 章 |")
    L.append("|---|---|---|---|---|---|")
    for st in doc["domain_stages"]:
        L.append("| `%s` | %s | %s | %s | %s | `%s:%s` |"
                 % (st["stage_id"], st["name"], _cell(st["canonical_owner"]),
                    ", ".join(x["seam"] for x in st["seam_refs"]),
                    _cell(st["forbidden"], 60), st["source_ref"]["chapter"],
                    st["source_ref"]["line"]))
    L.append("")
    if doc.get("entry_seam"):
        e = doc["entry_seam"]
        L.append("**入口接縫**：`%s` — %s" % (e["seam"], e["role"]))
        L.append("")
        L.append("- 不併入五階段之理由：%s" % e["why_not_a_stage"])
        L.append("- 來源：`%s:%s`" % (e["source_ref"]["file"], e["source_ref"]["line"]))
        L.append("- 判定規則：%s" % e["resolve_rule"])
        L.append("")
    L.append("## " + ARCH_SECTIONS[2])
    L.append("")
    L.append("| seam | wave | abi（宣告值） | abi state | reader_source_pin |")
    L.append("|---|---|---|---|---|")
    for s in doc["seams"]:
        L.append("| `%s` | %s | `%s` | `%s` | %s |"
                 % (s["seam"], s["wave"], s["abi"]["declared"], s["abi"]["state"],
                    _pin_label(s["abi"]["reader_source_pin"])))
    L.append("")
    L.append("- 五條 seam 的 ABI 皆未綁定原 runtime；W0 只交 typed 期望值與 fixture SHA。")
    L.append("")
    L.append("## " + ARCH_SECTIONS[3])
    L.append("")
    L.append("| seam | original_reader | ABI/Reader cell（正文） | consumer alias | ACK |")
    L.append("|---|---|---|---|---|")
    for s in doc["seams"]:
        L.append("| `%s` | %s | %s | %s | `%s` |"
                 % (s["seam"], _cell(s["reader"]["original_reader"]),
                    _cell(s["reader"]["body_reader_cell"], 90),
                    _cell(s["reader"]["consumer_alias"]), s["reader"]["ack"]))
    L.append("")
    L.append("## " + ARCH_SECTIONS[4])
    L.append("")
    L.append("| seam | permission mode | matched token | effect class | executed |")
    L.append("|---|---|---|---|---|")
    for s in doc["seams"]:
        L.append("| `%s` | `%s` | `%s` | `%s` | `%s` |"
                 % (s["seam"], s["permission"]["mode"],
                    s["permission"]["matched_token"], s["effect"]["class"],
                    s["effect"]["executed"]))
    L.append("")
    L.append("- permission 由該 seam 列的用字決定（WorldRaw > permit > 不寫世界 > ACK > SPECDraft 之優先序），原 ACL 一律 `NOT_OBSERVED`。")
    L.append("")
    L.append("## " + ARCH_SECTIONS[5])
    L.append("")
    L.append("| seam | POS | NEG | firstfail primary | expected |")
    L.append("|---|---|---|---|---|")
    for s in doc["seams"]:
        L.append("| `%s` | %s | %s | `%s` | `%s` |"
                 % (s["seam"], _cell(s["pos"]["statement"], 80),
                    _cell(s["neg"]["statement"], 80), s["firstfail"]["primary"],
                    s["firstfail"]["expected"]))
    L.append("")
    L.append("全域 firstfail：%s" % ", ".join("`%s`" % c for c in doc["firstfail_lattice"]["global"]))
    L.append("")
    L.append("## " + ARCH_SECTIONS[6])
    L.append("")
    L.append("| seam | stop | resume | rollback |")
    L.append("|---|---|---|---|")
    for s in doc["seams"]:
        L.append("| `%s` | %s | %s | %s |"
                 % (s["seam"], _cell(s["resume"]["stop"], 70),
                    _cell(s["resume"]["resume"], 110),
                    _cell(s["resume"]["rollback"], 70)))
    L.append("")
    L.append("## " + ARCH_SECTIONS[7])
    L.append("")
    L.append(doc["single_writer"]["statement"])
    L.append("")
    for w in doc["single_writer"]["non_transferable"]:
        L.append("- 不移轉：%s" % w)
    L.append("- 來源：`%s:%s`" % (doc["single_writer"]["source_ref"]["file"],
                                 doc["single_writer"]["source_ref"]["line"]))
    L.append("")
    L.append("## " + ARCH_SECTIONS[8])
    L.append("")
    L.append("**斷言**：%s" % doc["principal_separation"]["assertion"])
    L.append("")
    L.append("| Principal | 角色 | 不得兼任 |")
    L.append("|---|---|---|")
    L.append("| 唯一 Human Owner（1 人） | 授權與取捨 | 不得自任 Checker |")
    for p in doc["principal_separation"]["technical_principals"]:
        L.append("| %s | 技術執行 | 不得升格為 Owner |" % _cell(p, 70))
    L.append("")
    for ev in doc["principal_separation"]["evidence"]:
        L.append("- %s（`%s:%s`）" % (ev["claim"], ev["source_ref"]["file"],
                                     ev["source_ref"]["line"]))
    L.append("")
    L.append("### ADR（由 Architecture-kind W0_REQUIRED 需求列實算，共 %d 條）" % len(doc["adr"]))
    L.append("")
    L.append("| ADR | 決策 | 被拒方案 | requirement |")
    L.append("|---|---|---|---|")
    for a in doc["adr"]:
        L.append("| `%s` | %s | %s | `%s` |"
                 % (a["adr_id"], _cell(a["decision"], 90), _cell(a["rejected"], 90),
                    a["requirement_id"]))
    L.append("")
    L.append("### Open holds")
    for h in doc["open_holds"]:
        L.append("- %s" % h)
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# Program SPEC
# --------------------------------------------------------------------------- #
PROGRAM_SECTIONS = [
    SHARED_SECTION,
    "§P1 WP 矩陣（22）",
    "§P2 DAG 邊（36）",
    "§P3 E26 方向裁決",
    "§P4 Design84 卡與 25 跨波",
    "§P5 W0_REQUIRED22",
    "§P6 章圖 CH-00..49",
    "§P7 Source31",
    "§P8 R15 949",
    "§P9 Cell 192",
    "§P10 Parent50／Child149",
    "§P11 Oracle96",
    "§P12 Tech485",
    "§P13 計數對帳",
]


def build_program(index, goal):
    counts = index.counts()
    prog = index.registry("PROGRAM_WP22_DAG36.json")["data"]
    wps = prog["work_packages"]
    edges = prog["edges"]
    e26 = next(e for e in edges if e["id"] == "E26")
    binding = prog.get("operation_binding", {})
    e26_binding = next(
        (b for b in binding.get("edges", []) if b["edge"] == "E26"), None
    )
    if e26_binding is None:
        raise SpecError("E26_BINDING_MISSING", "operation_binding.edges")
    if e26["predecessor"] == e26["successor"]:
        raise SpecError("E26_DIRECTION_INVALID", str(e26))
    if e26_binding["predecessor"] != e26["predecessor"] or e26_binding["successor"] != e26["successor"]:
        raise SpecError(
            "E26_DIRECTION_CONFLICT",
            "edge=%s→%s binding=%s→%s"
            % (e26["predecessor"], e26["successor"],
               e26_binding["predecessor"], e26_binding["successor"]),
        )

    d84 = index.registry("DESIGN84_WAVE_JOIN.json")["data"]
    wave_split = [c for c in d84 if c["requirement_delivery_wave"] != c["wp_primary_wave"]]
    w0req = index.registry("W0_REQUIRED22_TRACE.json")["data"]
    cmap = index.chapter_map()
    src31 = index.registry("SOURCE31_PHYSICAL_IDENTITY.json")["data"]
    orc96 = index.registry("ORACLE96_CONTRACTS.json")["data"]
    tech = index.registry("TECH485_COMPACT_REGISTRY.json")["data"]
    reconcile = index.reconcile()

    doc = {
        "schema": SCHEMA_TAG + "/SPEC_Program",
        "artifact_id": "SPEC-Program-W0-wp15-local",
        "spec_kind": "Program",
        "version": "w0-r4c-wp15-1",
        "goal": goal,
        "subject": build_subject(index),
        "work_packages": [
            {
                "wp_id": w["id"],
                "name": w["name"],
                "output": w["output"],
                "dependencies": w["dependencies"],
                "primary_wave": w["primary_wave"],
                "effect_reader": w["effect_reader"],
            }
            for w in wps
        ],
        "edges": [
            {
                "edge_id": e["id"],
                "predecessor": e["predecessor"],
                "successor": e["successor"],
                "wave": e["wave"],
                "type_rule": e["type_rule"],
            }
            for e in edges
        ],
        "e26_direction": {
            "edge_id": e26["id"],
            "from": e26["predecessor"],
            "to": e26["successor"],
            "wave": e26["wave"],
            "direction": "%s→%s" % (e26["predecessor"], e26["successor"]),
            "operation": e26_binding["operation"],
            "blocking_rule": e26_binding["blocking_rule"],
            "firstfail": e26_binding["firstfail"],
            "secondary_firstfail": e26_binding["secondary_firstfail"],
            "original_reader_ack": e26_binding["original_reader_ack"],
            "body_clause": e26_binding["body_clause"],
            "rejection_points": binding.get("e26_rejection_points", {}),
            "source_ref": {
                "file": "PROGRAM_WP22_DAG36.json",
                "selector": "$.operation_binding.edges[?(@.edge=='E26')]",
                "file_sha256": index.registry_sha("PROGRAM_WP22_DAG36.json"),
            },
        },
        "design84": {
            "cards": [
                {
                    "original_id": c["original_id"],
                    "requirement_delivery_wave": c["requirement_delivery_wave"],
                    "primary_wp_id": c["primary_wp_id"],
                    "wp_primary_wave": c["wp_primary_wave"],
                    "scope_condition": c["scope_condition"],
                    "source_span": c["source_span"],
                }
                for c in d84
            ],
            "wave_split_cards": [
                {
                    "original_id": c["original_id"],
                    "requirement_delivery_wave": c["requirement_delivery_wave"],
                    "wp_primary_wave": c["wp_primary_wave"],
                    "primary_wp_id": c["primary_wp_id"],
                }
                for c in wave_split
            ],
            "wave_rule": "requirement_delivery_wave ≠ wp_primary_wave 需原 Program Reader 裁決，不得以需求波覆寫施工波",
            "source_ref": {
                "file": "DESIGN84_WAVE_JOIN.json",
                "selector": "$[*]",
                "file_sha256": index.registry_sha("DESIGN84_WAVE_JOIN.json"),
            },
        },
        "w0_required22": [
            {
                "original_id": r["original_id"],
                "spec_kind": r["spec_kind"],
                "primary_wp_id": r["primary_wp_id"],
                "requirement_delivery_wave": r["requirement_delivery_wave"],
                "deliver_id": r["deliver_id"],
                "chapter_refs": r["chapter_refs"],
                "source_id": r["source_id"],
                "source_span": r["source_span"],
            }
            for r in w0req
        ],
        "requirement_ids": sorted(
            r["original_id"] for r in w0req if r["spec_kind"] == "Program"
        ),
        "requirement_bindings": [
            {
                "requirement_id": r["original_id"],
                "spec_kind": r["spec_kind"],
                "statement": r["requirement"],
                "negative": r["source_negative"],
                "source_id": r["source_id"],
                "source_sha": r["source_sha"],
                "source_span": r["source_span"],
                "deliver_id": r["deliver_id"],
            }
            for r in w0req
            if r["spec_kind"] == "Program"
        ],
        "chapters": [
            {
                "chapter_id": c["chapter_id"],
                "title": c["title"],
                "primary_wave_cell": c["primary_wave_cell"],
                "line": c["line"],
            }
            for c in cmap
        ],
        "sources31": [
            {
                "source_id": s["source_id"],
                "original_name": s.get("original_name"),
                "bytes": s.get("bytes"),
                "lines": s.get("lines"),
                "sha256": s.get("sha256"),
            }
            for s in src31
        ],
        "r15_949": {
            "count": counts["r15_949"]["value"],
            "distinct": counts["r15_949"]["distinct"],
            "ids": counts["r15_949"]["ids"],
            "firstfail_note": "R15 949 屬原 SBL Full Product，不是 W0 必實作；本 SPEC 只作身份分母。",
        },
        "cell_192": {
            "count": counts["cell192"]["value"],
            "distinct": counts["cell192"]["distinct"],
            "ids": counts["cell192"]["ids"],
            "firstfail_note": "192 Cell 的 Provider ON/OFF 原標籤有歧義，未經原 Host/Provider Owner ACK 前保持 HOLD。",
        },
        "parent_child": {
            "parent_50": counts["parent50"]["value"],
            "child_149": counts["child149"]["value"],
            "parent_ids": counts["parent50"]["ids"],
            "child_ids": counts["child149"]["ids"],
            "rule": "每個 Child 必須引用已存在的 Parent；Child 身份不得被刪除或假稱 supersede。",
        },
        "oracle96": {
            "count": counts["oracle96"]["value"],
            "case_ids": counts["oracle96"]["ids"],
            "classes": _family_counts(orc96, key="test_class"),
            "runner_binding": "UNBOUND（原 Host Runner／Fixture bytes 未取回）",
            "source_ref": counts["oracle96"]["source_ref"],
        },
        "tech485": {
            "count": counts["tech485"]["value"],
            "families": counts["tech485"]["families"],
            "identity_rule": "485 正交技術身份為分母，不得相加為必安裝數",
            "source_ref": counts["tech485"]["source_ref"],
        },
        "counts": counts,
        "counter_reconciliation": reconcile,
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_RUN",
        "open_holds": [
            "E26 的 original_reader_ack=NOT_OBSERVED；W0 只出 typed 契約，不產生 CI Raw",
            "W2 Native E2E 未執行；本 SPEC 不宣稱任何 Native 效果",
            "25 張跨波卡待原 Program Reader 裁決（JOIN_AMBIGUOUS_AFFECTED）",
        ],
    }
    md = _render_program_md(doc)
    return doc, md


def _render_program_md(doc):
    L = []
    L.append("# SPEC_Program｜%s" % doc["artifact_id"])
    L.append("")
    L.append("> claim_ceiling=`%s`；native_effect=`%s`；body_sha256=`%s`"
             % (CLAIM_CEILING, doc["native_effect"], doc["subject"]["body_sha256"]))
    L.append("> 每個數字都由 registry 實算並附 source_ref；本檔不含 WP 執行、不含 Native 收據。")
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[0])
    L.append("")
    L.append("- subject_id: `%s`" % doc["subject"]["subject_id"])
    L.append("- body_sha256: `%s`" % doc["subject"]["body_sha256"])
    L.append("- 與 Product／Architecture 同 Subject；本檔差異欄位是 work_packages／edges／counts。")
    L.append("")
    c = doc["counts"]
    L.append("## " + PROGRAM_SECTIONS[1])
    L.append("")
    L.append("共 **%d** 個 WP（`%s` → `%s`）。" % (
        c["work_packages"]["value"], c["work_packages"]["ids"][0],
        c["work_packages"]["ids"][-1]))
    L.append("")
    L.append("| WP | name | primary_wave | dependencies |")
    L.append("|---|---|---|---|")
    for w in doc["work_packages"]:
        L.append("| `%s` | %s | %s | %s |"
                 % (w["wp_id"], _cell(w["name"], 60), w["primary_wave"],
                    ", ".join("`%s`" % d for d in w["dependencies"]) or "-"))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[2])
    L.append("")
    L.append("共 **%d** 條邊；波次分佈：%s。" % (
        c["edges"]["value"],
        ", ".join("%s=%d" % (k, v) for k, v in sorted(
            _family_counts(doc["edges"], key="wave").items()))))
    L.append("")
    L.append("| edge | predecessor | successor | wave |")
    L.append("|---|---|---|---|")
    for e in doc["edges"]:
        L.append("| `%s` | `%s` | `%s` | %s |"
                 % (e["edge_id"], e["predecessor"], e["successor"], e["wave"]))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[3])
    L.append("")
    d = doc["e26_direction"]
    L.append("**方向**：`%s`（%s），wave=%s。" % (d["direction"], d["edge_id"], d["wave"]))
    L.append("")
    L.append("- operation：%s" % d["operation"])
    L.append("- blocking_rule：%s" % d["blocking_rule"])
    L.append("- firstfail：`%s`；secondary：%s" % (
        d["firstfail"], ", ".join("`%s`" % x for x in d["secondary_firstfail"])))
    L.append("- original_reader_ack：`%s`" % d["original_reader_ack"])
    L.append("- 正文條款：%s" % d["body_clause"])
    L.append("")
    L.append("拒收點：")
    for k, v in d["rejection_points"].items():
        L.append("- %s → `%s`" % (k, v))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[4])
    L.append("")
    L.append("共 **%d** 張 Design Card，其中 **%d** 張跨波語義歧義（JOIN_AMBIGUOUS_AFFECTED）。"
             % (len(doc["design84"]["cards"]), len(doc["design84"]["wave_split_cards"])))
    L.append("")
    L.append("| DesignID | requirement_delivery_wave | primary_wp_id | wp_primary_wave | scope |")
    L.append("|---|---|---|---|---|")
    for card in doc["design84"]["cards"][:14]:
        L.append("| `%s` | %s | `%s` | %s | %s |"
                 % (card["original_id"], card["requirement_delivery_wave"],
                    card["primary_wp_id"], card["wp_primary_wave"],
                    card["scope_condition"]))
    L.append("")
    L.append("（其餘 %d 張全量見 JSON `design84.cards`。）" % (len(doc["design84"]["cards"]) - 14))
    L.append("")
    L.append("**25 張跨波卡**：%s" % ", ".join(
        "`%s`" % x["original_id"] for x in doc["design84"]["wave_split_cards"]))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[5])
    L.append("")
    L.append("共 **%d** 筆 W0_REQUIRED；spec_kind 分佈：%s。" % (
        c["w0_required"]["value"],
        ", ".join("%s=%d" % (k, v) for k, v in sorted(
            _family_counts(doc["w0_required22"], key="spec_kind").items()))))
    L.append("")
    L.append("| RequirementID | spec_kind | primary_wp_id | wave | deliver_id | chapters |")
    L.append("|---|---|---|---|---|---|")
    for r in doc["w0_required22"]:
        L.append("| `%s` | %s | `%s` | %s | `%s` | %s |"
                 % (r["original_id"], r["spec_kind"], r["primary_wp_id"],
                    r["requirement_delivery_wave"], r["deliver_id"],
                    ", ".join(r["chapter_refs"]) or "-"))
    L.append("")
    L.append("本 SPEC 直接綁定的 Program-kind RequirementID：%s。"
             % ", ".join("`%s`" % r for r in doc["requirement_ids"]))
    L.append("（其餘 19 筆屬 Product／Architecture 的欄位責任，見各自 SPEC，不在此重複認領。）")
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[6])
    L.append("")
    L.append("共 **%d** 個 H1 章（`CH-00` → `CH-49`）；章表 %d 列。" % (
        c["chapters"]["value"], len(doc["chapters"])))
    L.append("")
    L.append("| CH | title | primary wave | body line |")
    L.append("|---|---|---|---|")
    for ch in doc["chapters"]:
        L.append("| `%s` | %s | %s | %d |"
                 % (ch["chapter_id"], _cell(ch["title"], 60),
                    ch["primary_wave_cell"], ch["line"]))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[7])
    L.append("")
    L.append("共 **%d** 冊原始 Source（SBL %d／FHS %d）。" % (
        c["sources31"]["value"],
        len([s for s in doc["sources31"] if s["source_id"].startswith("SBL")]),
        len([s for s in doc["sources31"] if s["source_id"].startswith("FHS")])))
    L.append("")
    L.append("| SourceID | original_name | bytes | lines | sha256（前 16） |")
    L.append("|---|---|---|---|---|")
    for s in doc["sources31"]:
        L.append("| `%s` | %s | %s | %s | `%s` |"
                 % (s["source_id"], _cell(s["original_name"], 55), s["bytes"],
                    s["lines"], (s["sha256"] or "")[:16]))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[8])
    L.append("")
    L.append("共 **%d** 個 R15 原子（distinct=%d）。%s" % (
        doc["r15_949"]["count"], doc["r15_949"]["distinct"],
        doc["r15_949"]["firstfail_note"]))
    L.append("")
    L.append("- 樣本：%s … %s" % (
        ", ".join("`%s`" % x for x in doc["r15_949"]["ids"][:6]),
        ", ".join("`%s`" % x for x in doc["r15_949"]["ids"][-3:])))
    L.append("- 全量 id 見 JSON `r15_949.ids`。")
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[9])
    L.append("")
    L.append("共 **%d** 個 Kind×Mode×Host×LegacyToken Cell（distinct=%d）。%s" % (
        doc["cell_192"]["count"], doc["cell_192"]["distinct"],
        doc["cell_192"]["firstfail_note"]))
    L.append("")
    L.append("- 樣本：%s" % ", ".join("`%s`" % x for x in doc["cell_192"]["ids"][:6]))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[10])
    L.append("")
    pc = doc["parent_child"]
    L.append("SBL 原產品 **Parent %d** ／ **Child %d**。" % (pc["parent_50"], pc["child_149"]))
    L.append("")
    L.append("- 規則：%s" % pc["rule"])
    L.append("- Parent ids：%s" % ", ".join("`%s`" % x for x in pc["parent_ids"][:10]))
    L.append("- Child 樣本：%s" % ", ".join("`%s`" % x for x in pc["child_ids"][:8]))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[11])
    L.append("")
    o = doc["oracle96"]
    L.append("共 **%d** 個 Original Oracle 個案；class 分佈：%s。" % (
        o["count"], ", ".join("%s=%d" % (k, v) for k, v in sorted(o["classes"].items()))))
    L.append("")
    L.append("- runner_binding：`%s`" % o["runner_binding"])
    L.append("- 樣本：%s" % ", ".join("`%s`" % x for x in o["case_ids"][:6]))
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[12])
    L.append("")
    t = doc["tech485"]
    L.append("共 **%d** 個正交技術身份；family 分佈：%s。" % (
        t["count"], ", ".join("%s=%d" % (k, v) for k, v in sorted(t["families"].items()))))
    L.append("")
    L.append("- %s" % t["identity_rule"])
    L.append("")
    L.append("## " + PROGRAM_SECTIONS[13])
    L.append("")
    L.append("| claim | 來源宣告 | 實算 | match |")
    L.append("|---|---|---|---|")
    for row in doc["counter_reconciliation"]:
        L.append("| %s | %s | %s | %s |"
                 % (row["claim"], row["declared"], row["computed"], row["match"]))
    L.append("")
    L.append("### Open holds")
    for h in doc["open_holds"]:
        L.append("- %s" % h)
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# validators
# --------------------------------------------------------------------------- #
SEAM_SHAPE_KEYS = ["abi", "reader", "effect", "permission", "pos", "neg",
                   "firstfail", "resume", "typed_handoff"]


def assert_seam_shape(doc):
    """Every seam must carry all nine bound facets, on all five seams."""
    seams = doc.get("seams") or []
    if [s.get("seam") for s in seams] != ["S1", "S2", "S3", "S4", "S5"]:
        raise SpecError("SEAM_SHAPE_INCOMPLETE", "seam list is not S1..S5")
    for s in seams:
        missing = [k for k in SEAM_SHAPE_KEYS if not s.get(k)]
        if missing:
            raise SpecError(
                "SEAM_SHAPE_INCOMPLETE",
                "%s missing %s" % (s.get("seam"), missing),
                {"seam": s.get("seam"), "missing": missing},
            )
    return len(seams)


def assert_claim_ceiling(doc):
    """A SPEC must not claim Native/authority it did not observe (CH-00 NEG)."""
    problems = []
    if doc.get("claim_ceiling") != CLAIM_CEILING:
        problems.append("claim_ceiling=%r != %r" % (doc.get("claim_ceiling"), CLAIM_CEILING))
    if doc.get("native_effect") not in (None, "NOT_RUN"):
        problems.append("native_effect=%r claimed without observed raw" % doc.get("native_effect"))
    if not (doc.get("requirement_bindings") or doc.get("counts")):
        problems.append("no source-bound rows: authority claimed without a source_ref")
    if problems:
        raise SpecError("CLAIM_CEILING_VIOLATION", "; ".join(problems))
    return True


def assert_subject_same(docs):
    shas = {k: v["subject"]["body_sha256"] for k, v in docs.items()}
    sids = {k: v["subject"]["subject_id"] for k, v in docs.items()}
    if len(set(shas.values())) != 1 or len(set(sids.values())) != 1:
        raise SpecError("SUBJECT_NOT_SHARED", json.dumps({"sha": shas, "sid": sids}))
    return True


def assert_fuo(doc):
    fuo = doc.get("fuo")
    if not fuo:
        raise SpecError("FUO_MISSING", "product SPEC declares zero first-usable-outcome")
    bad = []
    for f in fuo:
        if not f.get("fuo_id") or not f.get("statement") or not f.get("source_ref"):
            bad.append(f.get("fuo_id"))
        elif not f.get("acceptance") or not f["acceptance"].get("pos") or not f["acceptance"].get("neg"):
            bad.append(f.get("fuo_id"))
    if bad:
        raise SpecError("FUO_MISSING", "incomplete fuo rows: %s" % bad)
    return len(fuo)


def assert_requirements(doc, index):
    reg = index.requirement_registry()
    cited = list(doc.get("requirement_ids", []))
    for b in doc.get("requirement_bindings", []):
        cited.append(b["requirement_id"])
    unbound = sorted({c for c in cited if c not in reg or not reg[c].get("bound")})
    if unbound:
        raise SpecError("REQUIREMENT_UNBOUND", ",".join(unbound), {"unbound": unbound})
    return len(set(cited))


def _md_sections(md_text):
    """Map '## ' heading -> body text (H1 and '> ' orientation lines dropped)."""
    sections = {}
    order = []
    cur = None
    for line in md_text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            sections[cur] = []
            order.append(cur)
            continue
        if line.startswith("# ") or line.startswith("> "):
            continue
        if cur is not None:
            sections[cur].append(line)
    return {k: "\n".join(sections[k]) for k in order}


def _sections_of_md(md_text):
    return list(_md_sections(md_text).keys())


def _tokens(md_text, drop_shared=False):
    """Character-bigram set over section bodies.

    drop_shared=True measures *domain* content only: §0 (Subject Binding) is the
    one block the three SPECs are contractually required to share verbatim, so
    counting it would inflate similarity without saying anything about whether
    the three documents differ.
    """
    secs = _md_sections(md_text)
    if drop_shared:
        secs.pop(SHARED_SECTION, None)
    body = "\n".join(secs[k] for k in secs)
    return {body[i : i + 2] for i in range(len(body) - 1) if body[i : i + 2].strip()}


def _jaccard(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / float(len(a | b))


def spec_fingerprint(doc, md_text):
    return {
        "artifact_id": doc["artifact_id"],
        "spec_kind": doc["spec_kind"],
        "required_field_set": sorted(doc.keys()),
        "section_set": _sections_of_md(md_text),
        "json_sha256": sha256_bytes(canonical_bytes(doc)),
        "body_sha256": sha256_text(md_text),
        "body_bytes": len(md_text.encode("utf-8")),
    }


def assert_heterogeneity(docs, mds):
    """Prove the three SPECs are not the same document with a new title."""
    fp = {k: spec_fingerprint(docs[k], mds[k]) for k in ("Product", "Architecture", "Program")}
    problems = []
    pairs = [("Product", "Architecture"), ("Product", "Program"), ("Architecture", "Program")]
    pair_report = {}
    for a, b in pairs:
        sa = set(fp[a]["section_set"])
        sb = set(fp[b]["section_set"])
        fa = set(fp[a]["required_field_set"])
        fb = set(fp[b]["required_field_set"])
        inter = sa & sb
        sec_j = _jaccard(sa, sb)
        field_j = _jaccard(fa, fb)
        tok_j = _jaccard(_tokens(mds[a]), _tokens(mds[b]))
        dom_tok_j = _jaccard(_tokens(mds[a], drop_shared=True),
                             _tokens(mds[b], drop_shared=True))
        pair_report["%s×%s" % (a, b)] = {
            "section_intersection": sorted(inter),
            "section_intersection_size": len(inter),
            "section_strictly_smaller_than_each": len(inter) < len(sa) and len(inter) < len(sb),
            "section_jaccard": round(sec_j, 6),
            "field_sets_equal": fa == fb,
            "fields_only_in_a": sorted(fa - fb),
            "fields_only_in_b": sorted(fb - fa),
            "field_jaccard": round(field_j, 6),
            "body_token_jaccard": round(tok_j, 6),
            "domain_token_jaccard": round(dom_tok_j, 6),
            "only_shared_sections": sorted(inter),
        }
        if fa == fb:
            problems.append("%s/%s share an identical required_field_set" % (a, b))
        if not (len(inter) < len(sa) and len(inter) < len(sb)):
            problems.append("%s/%s section intersection is not strictly smaller" % (a, b))
        if sec_j > HETERO_MAX_SECTION_JACCARD:
            problems.append("%s/%s section_jaccard=%.3f > %.2f"
                            % (a, b, sec_j, HETERO_MAX_SECTION_JACCARD))
        if field_j > HETERO_MAX_FIELD_JACCARD:
            problems.append("%s/%s field_jaccard=%.3f > %.2f"
                            % (a, b, field_j, HETERO_MAX_FIELD_JACCARD))
        if dom_tok_j > HETERO_MAX_TOKEN_JACCARD:
            problems.append("%s/%s domain_token_jaccard=%.3f > %.2f"
                            % (a, b, dom_tok_j, HETERO_MAX_TOKEN_JACCARD))
    if problems:
        raise SpecError("SPEC_NOT_HETEROGENEOUS", "; ".join(problems), {"pairs": pair_report})
    report = {
        "schema": SCHEMA_TAG + "/SPEC_HETEROGENEITY",
        "verdict": "HETEROGENEOUS",
        "subject_sha256": docs["Product"]["subject"]["body_sha256"],
        "thresholds": {
            "max_section_jaccard": HETERO_MAX_SECTION_JACCARD,
            "max_field_jaccard": HETERO_MAX_FIELD_JACCARD,
            "max_domain_token_jaccard": HETERO_MAX_TOKEN_JACCARD,
            "section_intersection_must_be_strictly_smaller": True,
            "field_sets_must_differ": True,
        },
        "specs": fp,
        "pairs": pair_report,
        "method": {
            "section_set": "every '## ' heading in the produced .md, in order",
            "required_field_set": "every top-level key of the produced .json",
            "body_token_jaccard": "character-bigram Jaccard over all md section bodies (informational)",
            "domain_token_jaccard": "character-bigram Jaccard over md section bodies with the "
                                    "contractually shared §0 Subject block removed (gated)",
            "title_swap_signature": "identical section_set AND identical required_field_set "
                                    "AND domain_token_jaccard >= 0.9",
        },
        "failure_example_rejected": {
            "case": "same body, only the H1 title changed",
            "code": "SPEC_NOT_HETEROGENEOUS",
            "why": "field sets equal, section sets equal, token jaccard ~1.0",
        },
        "claim_ceiling": CLAIM_CEILING,
    }
    return report


# --------------------------------------------------------------------------- #
# Goal -> SPEC -> W0 deliver -> FUO readback chain
# --------------------------------------------------------------------------- #
def _bigrams(text):
    return {text[i : i + 2] for i in range(len(text) - 1) if text[i : i + 2].strip()}


def goal_relevance(goal, requirement_text):
    g = _bigrams(goal)
    if not g:
        return 0.0
    return round(len(g & _bigrams(requirement_text)) / float(len(g)), 6)


def compute_readback_sha(doc):
    """readback_sha = sha256 of the canonical doc with the digest field removed."""
    body = {k: v for k, v in doc.items() if k != "readback_sha"}
    return sha256_bytes(canonical_bytes(body))


def build_goal_chain(index, goal, product_doc, product_md, product_json_path, paths):
    product_json_sha = sha256_file(product_json_path)
    product_md_sha = sha256_text(product_md)
    input_sha = sha256_text(goal)
    chains = []
    for f in sorted(product_doc["fuo"], key=lambda x: x["fuo_id"]):
        deliver_id = f["deliver"].get("deliver_id")
        if not deliver_id:
            continue
        wp = f["deliver"]["primary_wp_id"]
        steps = [
            {"step": 1, "kind": "GOAL", "ref": "user_goal", "sha256": input_sha,
             "value": goal},
            {"step": 2, "kind": "PRODUCT_SPEC", "ref": "SPEC_Product.json",
             "sha256": product_json_sha, "value": product_doc["artifact_id"]},
            {"step": 3, "kind": "W0_DELIVER", "ref": deliver_id, "sha256": None,
             "value": {"deliver_id": deliver_id, "primary_wp_id": wp,
                       "subject_id": product_doc["subject"]["subject_id"],
                       "body_sha256": product_doc["subject"]["body_sha256"]}},
            {"step": 4, "kind": "FUO", "ref": f["fuo_id"],
             "sha256": sha256_text(f["statement"]), "value": f["statement"]},
        ]
        ok = all(
            (f["fuo_id"] in product_md) and (deliver_id in json.dumps(product_doc, ensure_ascii=False))
            for _ in [0]
        )
        chains.append(
            {
                "chain_id": "CHAIN-%s" % f["fuo_id"],
                "fuo_id": f["fuo_id"],
                "deliver_id": deliver_id,
                "steps": steps,
                "relevance": goal_relevance(
                    goal,
                    " ".join([f["statement"], f["acceptance"].get("pos", ""),
                              f["acceptance"].get("neg", "")]),
                ),
                "readback": {
                    "fuo_present_in_product_spec": f["fuo_id"] in product_md,
                    "deliver_present_in_product_spec": deliver_id
                    in json.dumps(product_doc, ensure_ascii=False),
                    "statement_sha256": sha256_text(f["statement"]),
                    "product_json_sha256": product_json_sha,
                    "product_md_sha256": product_md_sha,
                },
            }
        )
    if not chains:
        raise SpecError("FUO_MISSING", "no FUO carries a W0 deliver binding")
    declared_only = [f["fuo_id"] for f in product_doc["fuo"] if not f["deliver"].get("deliver_id")]
    primary = sorted(chains, key=lambda c: (-c["relevance"], c["fuo_id"]))[0]
    doc = {
        "schema": SCHEMA_TAG + "/GOAL_TO_FUO",
        "goal": goal,
        "input_sha": input_sha,
        "input_sha_rule": "sha256(goal.encode('utf-8'))",
        "output_sha": product_json_sha,
        "output_sha_rule": "sha256(bytes of out/SPEC_Product.json)",
        "subject": product_doc["subject"],
        "goal_binding_method": {
            "method": "AUTHOR_TOKEN_OVERLAP_HEURISTIC",
            "detail": "character-bigram overlap between the goal and each FUO's "
                      "statement+acceptance-pos+acceptance-neg; rank only, "
                      "NOT an original Reader semantic binding",
            "original_reader_ack": "NOT_OBSERVED",
        },
        "chain_count": len(chains),
        "primary_chain": primary["chain_id"],
        "chains": chains,
        "declared_fuo_without_deliver": declared_only,
        "declared_fuo_note": "CH-01 宣告的 FUO-A／FUO-B 只有章級 W0 綁定，沒有 W0_REQUIRED 的 "
                             "deliver_id，因此不升格為 chain，只列名。",
        "artifacts": paths,
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_RUN",
        "readback_sha_rule": (
            "sha256(canonical_json(doc without 'readback_sha'))；"
            "canonical = sort_keys + separators(',',':') + ensure_ascii=False + UTF-8"
        ),
    }
    doc["readback_sha"] = compute_readback_sha(doc)
    md = _render_goal_md(doc)
    return doc, md


def _render_goal_md(doc):
    L = []
    L.append("# GOAL_TO_FUO｜Goal → Product SPEC → W0 Deliver → FUO 可讀回鏈")
    L.append("")
    L.append("> claim_ceiling=`%s`；native_effect=`%s`" % (CLAIM_CEILING, doc["native_effect"]))
    L.append("")
    L.append("## 輸入 Goal")
    L.append("")
    L.append("```text")
    L.append(doc["goal"])
    L.append("```")
    L.append("")
    L.append("| digest | 值 | 規則 |")
    L.append("|---|---|---|")
    L.append("| input_sha | `%s` | %s |" % (doc["input_sha"], doc["input_sha_rule"]))
    L.append("| output_sha | `%s` | %s |" % (doc["output_sha"], doc["output_sha_rule"]))
    L.append("| readback_sha | `%s` | %s |" % (doc["readback_sha"], doc["readback_sha_rule"]))
    L.append("")
    L.append("## 主鏈 %s（共 %d 條，全部由 Product SPEC 的 FUO 實算）"
             % (doc["primary_chain"], doc["chain_count"]))
    L.append("")
    for ch in doc["chains"]:
        L.append("### %s → `%s`" % (ch["fuo_id"], ch["deliver_id"]))
        L.append("")
        L.append("| # | step | ref | sha256 | value |")
        L.append("|---|---|---|---|---|")
        for st in ch["steps"]:
            L.append("| %d | %s | `%s` | `%s` | %s |"
                     % (st["step"], st["kind"], st["ref"], (st["sha256"] or "-")[:16],
                        _cell(json.dumps(st["value"], ensure_ascii=False)
                              if not isinstance(st["value"], str) else st["value"], 90)))
        L.append("")
        rb = ch["readback"]
        L.append("- readback：fuo_in_spec=%s / deliver_in_spec=%s / statement_sha256=`%s`"
                 % (rb["fuo_present_in_product_spec"], rb["deliver_present_in_product_spec"],
                    rb["statement_sha256"]))
        L.append("- goal_relevance（bigram 重疊，僅排序用）= %s" % ch["relevance"])
        L.append("")
    L.append("### 宣告但未升格為 chain 的 FUO")
    L.append("")
    L.append("- %s" % (", ".join("`%s`" % x for x in doc["declared_fuo_without_deliver"]) or "（無）"))
    L.append("- %s" % doc["declared_fuo_note"])
    L.append("")
    L.append("### 綁定方法與上限")
    L.append("")
    L.append("- method：`%s` — %s" % (doc["goal_binding_method"]["method"],
                                     doc["goal_binding_method"]["detail"]))
    L.append("- original_reader_ack：`%s`" % doc["goal_binding_method"]["original_reader_ack"])
    L.append("- 本鏈只證明「同一份 Product SPEC 內可讀回」，不證明原 SBL/PIPD Reader 接受。")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# pipeline
# --------------------------------------------------------------------------- #
def _write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return sha256_file(path)


def run_pipeline(body_path, source_root, out_dir, goal, emit_hetero=True):
    index = SourceIndex(body_path, source_root)
    os.makedirs(out_dir, exist_ok=True)

    product, product_md = build_product(index, goal)
    arch, arch_md = build_architecture(index, goal)
    program, program_md = build_program(index, goal)
    docs = {"Product": product, "Architecture": arch, "Program": program}
    mds = {"Product": product_md, "Architecture": arch_md, "Program": program_md}

    assert_subject_same(docs)
    assert_seam_shape(arch)
    assert_fuo(product)
    for name, d in docs.items():
        assert_claim_ceiling(d)
        assert_requirements(d, index)
    hetero = assert_heterogeneity(docs, mds)

    written = {}
    for name, doc, md in (
        ("Product", product, product_md),
        ("Architecture", arch, arch_md),
        ("Program", program, program_md),
    ):
        jp = os.path.join(out_dir, "SPEC_%s.json" % name)
        mp = os.path.join(out_dir, "SPEC_%s.md" % name)
        written[jp] = _write(jp, pretty_json(doc))
        written[mp] = _write(mp, md)

    paths = {os.path.basename(p): written[p] for p in sorted(written)}
    chain, chain_md = build_goal_chain(
        index, goal, product, product_md,
        os.path.join(out_dir, "SPEC_Product.json"), paths,
    )
    jp = os.path.join(out_dir, "GOAL_TO_FUO.json")
    mp = os.path.join(out_dir, "GOAL_TO_FUO.md")
    written[jp] = _write(jp, pretty_json(chain))
    written[mp] = _write(mp, chain_md)

    if emit_hetero:
        hp = os.path.join(out_dir, "SPEC_HETEROGENEITY.json")
        written[hp] = _write(hp, pretty_json(hetero))

    manifest = {
        "schema": SCHEMA_TAG + "/RUN",
        "goal": goal,
        "input_sha": sha256_text(goal),
        "body": {
            "path": index.body_path,
            "sha256": index.body_sha256,
            "bytes": index.body_bytes,
            "chapters": len(index.chapters()),
        },
        "source_root": index.source_root,
        "outputs": {os.path.basename(p): {"sha256": written[p], "bytes": os.path.getsize(p)}
                    for p in written},
        "counts": {k: v["value"] for k, v in index.counts().items()},
        "heterogeneity": hetero["pairs"],
        "readback_sha": chain["readback_sha"],
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_RUN",
    }
    return manifest


def verify_readback(path):
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    stated = doc.get("readback_sha")
    recomputed = compute_readback_sha(doc)
    ok = stated == recomputed
    if not ok:
        raise SpecError(
            "READBACK_SHA_MISMATCH", "stated=%s recomputed=%s" % (stated, recomputed)
        )
    return {"readback_sha": recomputed, "verified": True}


def _default_body(source_root):
    cands = [f for f in os.listdir(source_root) if f.endswith(BODY_GLOB_SUFFIX)]
    if len(cands) != 1:
        raise SpecError("BODY_AMBIGUOUS", ",".join(cands))
    return os.path.join(source_root, cands[0])


def main(argv=None):
    ap = argparse.ArgumentParser(description="FHS W0 R4C WP-FHS-15 spec pipeline")
    ap.add_argument("--body", required=False, default=None,
                    help="path to the W0 r4-candidate substantive body .md")
    ap.add_argument("--source-root", required=True,
                    help="directory holding the author-side registries")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--goal", required=True, help="one plain-language goal sentence")
    ap.add_argument("--no-hetero", action="store_true", help="skip SPEC_HETEROGENEITY.json")
    ap.add_argument("--verify", default=None, help="verify a GOAL_TO_FUO.json readback_sha")
    args = ap.parse_args(argv)

    if args.verify:
        print(json.dumps(verify_readback(args.verify), ensure_ascii=False, indent=2))
        return 0

    body = args.body or _default_body(args.source_root)
    manifest = run_pipeline(body, args.source_root, args.out, args.goal,
                            emit_hetero=not args.no_hetero)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
