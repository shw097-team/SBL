"""Per-Source-ID atoms and FirstFail for a whole clause set, in ONE `intake` call.

This module backs the additive ``intake --clause-set <path>`` flag. It exists because the only
per-source channel the 13-verb CLI has ever had was "run the whole command once per clause and
read the exit code" - a loop every prior lane had to hand-write. That loop moved inside the verb;
the ANSWER did not move.

WHAT THIS EMITS
    One ``sources[]`` row per requested span, each carrying the compiler-native ``source_id``
    (``requirements.source_id_for``), the span and its ``clause_sha256``, the atoms that clause
    compiled to (with their polarity), and the FIRST FAIL of that clause (verb/stage/code/message).

WHAT THIS NEVER EMITS
    An ``Accept``, an ``N-A`` or a ``NACK``. The compiler has no applicability input, no reader
    identity and no authority to decide; ``INTAKE_INVALID`` is a refusal by the compiler and is
    NOT a reader disposition. ``reader_disposition`` is a constant in the payload precisely so a
    consumer cannot mistake the absence for a verdict.

DEFAULT BEHAVIOUR
    Nothing here runs unless ``--clause-set`` is given. The card is NOT an ``IntentCard@1``; it
    carries ``schema_version: ClauseSetIntake@1`` so it can never be read as a single-goal intake.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from . import requirements as req_compile
from .errors import InputShapeInvalid, IoNotFound, ParseInvalid
from .util import canonical_json, sha256_bytes, sha256_text

SCHEMA = "ClauseSetIntake@1"
CLAIM_CEILING = "PER_SOURCE_FIRST_FAIL_ONLY"
#: Constant, by design. The compiler does not produce a disposition and never will.
READER_DISPOSITION = "NOT_PRODUCED_BY_COMPILER"

ROW_KEYS = ("clause_id", "span", "source_id", "clause_sha256", "subject_sha256", "file", "text")


def _read_rows(path: Path) -> tuple[list[dict[str, Any]], str]:
    """Rows from a .tsv (header row) or .jsonl / .json (one object per line, or an array)."""
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise IoNotFound(f"cannot read clause set at {path}: {exc.strerror or type(exc).__name__}") from exc
    suffix = path.suffix.lower()
    if suffix in (".tsv", ".tab"):
        reader = csv.DictReader(raw.splitlines(), delimiter="\t")
        rows = [dict(r) for r in reader]
        return rows, f"tsv:{','.join(reader.fieldnames or [])}"
    if suffix in (".jsonl", ".ndjson"):
        rows = []
        for number, line in enumerate(raw.splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ParseInvalid(f"clause set line {number} of {path} is not JSON: {exc.msg}") from exc
        return rows, "jsonl"
    if suffix == ".json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ParseInvalid(f"clause set at {path} is not valid JSON: {exc.msg}") from exc
        rows = data.get("rows") if isinstance(data, dict) else data
        if not isinstance(rows, list):
            raise InputShapeInvalid(f"clause set at {path} must be a JSON array or {{'rows': [...]}}")
        return rows, "json"
    raise InputShapeInvalid(f"clause set at {path} must be .tsv, .jsonl or .json "
                            f"(got {path.suffix or 'no suffix'})")


def _span_of(row: dict[str, Any], index: int) -> tuple[int, int]:
    span = row.get("span")
    if isinstance(span, (list, tuple)) and len(span) == 2:
        values = span
    else:
        start, end = row.get("span_start"), row.get("span_end")
        if start in (None, "") or end in (None, ""):
            raise InputShapeInvalid(
                f"clause set row {index} has no span: give `span: [start, end]`, or the "
                "`span_start` / `span_end` columns of the wave Source Span table")
        values = (start, end)
    try:
        start, end = int(values[0]), int(values[1])
    except (TypeError, ValueError) as exc:
        raise InputShapeInvalid(f"clause set row {index} span is not two integers: {values!r}") from exc
    if start < 0 or end <= start:
        raise InputShapeInvalid(f"clause set row {index} span is not a forward half-open range: "
                                f"[{start}, {end})")
    return start, end


def _opt(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    return "" if value is None else str(value).strip()


def run(clause_set: Path | str, subject: Path | str, *,
        constraints: list[str] | None = None, non_goals: list[str] | None = None) -> dict[str, Any]:
    """Compile one clause set against one pinned subject. Raises a typed refusal if unusable."""
    clause_set_path = Path(clause_set)
    subject_path = Path(subject)
    rows, fmt = _read_rows(clause_set_path)
    if not rows:
        raise InputShapeInvalid(f"clause set at {clause_set_path} has zero rows")
    try:
        text = subject_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise IoNotFound(f"cannot read the pinned subject at {subject_path}: "
                         f"{exc.strerror or type(exc).__name__}") from exc
    except UnicodeError as exc:
        raise InputShapeInvalid(f"the pinned subject at {subject_path} is not UTF-8: {exc}") from exc
    subject_sha = sha256_text(text)
    # `str(Path(...))` is the same file string `source_id_for` was given when the wave bound its
    # Source IDs, so the ids reconcile to the index instead of being re-invented here.
    file_id = str(subject_path)

    spans: list[tuple[int, int]] = []
    declared: list[dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise InputShapeInvalid(f"clause set row {index} is not an object")
        spans.append(_span_of(row, index))
        declared.append({k: _opt(row, k) for k in ("source_id", "clause_id", "clause_sha256",
                                                   "subject_sha256", "file")})

    compiled = req_compile.compile_pinned_clauses(text, file_id, spans)

    sources: list[dict[str, Any]] = []
    atoms_all: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    for index, (span, row, want) in enumerate(zip(spans, compiled, declared), 1):
        start, end = span
        derived_id = req_compile.source_id_for(file_id, f"clause-{start}-{end}", subject_sha)
        code, message, state = row["code"], row["message"], row["state"]

        # Identity is checked, never trusted: a clause set that names an id this compiler does not
        # derive is a set for a different subject, and must not be reported as if it reconciled.
        if want["file"] and want["file"] != file_id:
            code, message = "SOURCE_LOCATOR_MISMATCH", (
                f"row names file {want['file']!r} but the pinned subject is {file_id!r}")
        elif want["subject_sha256"] and want["subject_sha256"] != subject_sha:
            code, message = "SUBJECT_SHA_MISMATCH", (
                f"row names subject_sha256 {want['subject_sha256'][:16]}... but the pinned "
                f"subject digests to {subject_sha[:16]}...")
        elif want["clause_id"] and want["clause_id"] != f"clause-{start}-{end}":
            code, message = "CLAUSE_ID_MISMATCH", (
                f"row names clause_id {want['clause_id']!r} for span [{start}, {end}); the "
                f"compiler's clause id for that span is 'clause-{start}-{end}'")
        elif want["clause_sha256"] and want["clause_sha256"] != row["clause_sha256"]:
            code, message = "CLAUSE_SHA_MISMATCH", (
                f"row names clause_sha256 {want['clause_sha256'][:16]}... but span [{start}, "
                f"{end}) digests to {row['clause_sha256'][:16]}...")
        elif want["source_id"] and want["source_id"] != derived_id:
            code, message = "SOURCE_ID_MISMATCH", (
                f"row names source_id {want['source_id']!r}; this compiler derives {derived_id!r}")

        if code:
            state = "REFUSED"
        entry: dict[str, Any] = {
            "row_no": index,
            "source_id": derived_id,
            "clause_id": f"clause-{start}-{end}",
            "span": [start, end],
            "file": file_id,
            "subject_sha256": subject_sha,
            "clause_sha256": row["clause_sha256"],
            "state": state,
            "stage": "intake",
            "code": code,
            "message": message,
            "atoms": [{"req_id": a["req_id"],
                       "polarity": a["risk_guard"]["polarity"],
                       "axis": a["axis"],
                       "acceptance_cue": a["acceptance_cue"]} for a in row["atoms"]],
            "polarity": sorted({a["risk_guard"]["polarity"] for a in row["atoms"]}),
            "atom_count": len(row["atoms"]),
            "first_fail": ({'verb': 'intake', 'stage': 'intake', 'code': code, 'message': message}
                           if state == "REFUSED" else None),
        }
        if entry["source_id"] in seen:
            findings.append({"kind": "CLAUSE_SET_DUPLICATE_SOURCE",
                             "source_id": entry["source_id"],
                             "detail": f"rows {seen[entry['source_id']]} and {index} resolve to the "
                                       "same Source ID; one Source ID is one record"})
        seen.setdefault(entry["source_id"], index)
        sources.append(entry)
        atoms_all.extend(row["atoms"])

    refused = [s for s in sources if s["state"] == "REFUSED"]
    histogram: dict[str, int] = {}
    for s in refused:
        histogram[str(s["code"])] = histogram.get(str(s["code"]), 0) + 1
    payload = {
        "goal": None,
        "subject": str(subject_path),
        "subject_sha256": subject_sha,
        "clause_set": {"path": str(clause_set_path),
                       "sha256": sha256_bytes(clause_set_path.read_bytes()),
                       "rows": len(sources), "format": fmt},
        "constraints": list(constraints or []),
        "non_goals": list(non_goals or []),
        "spans": [s["span"] for s in sources],
    }
    card: dict[str, Any] = {
        "schema_version": SCHEMA,
        "subject_id": "CLAUSESET-" + sha256_text(canonical_json(payload))[:16],
        "content_hash": sha256_text(canonical_json(payload)),
        **payload,
        "sources": sources,
        "atoms": atoms_all,
        "counts": {"sources": len(sources), "distinct_source_ids": len(seen),
                   "atoms_rows": len(sources) - len(refused),
                   "refused_rows": len(refused), "atoms": len(atoms_all)},
        "first_fail_histogram": dict(sorted(histogram.items())),
        "verdict": "PASS" if not refused else "FAIL",
        "claim_ceiling": CLAIM_CEILING,
        "reader_disposition": READER_DISPOSITION,
        "disposition_note": ("the compiler emits atoms and FirstFail only; Accept / N-A / NACK "
                             "require the original reader's signed SBL.SourceAdjudication@1 and "
                             "are checked read-only by `validate --adjudications`"),
        "findings": findings,
    }
    return card
