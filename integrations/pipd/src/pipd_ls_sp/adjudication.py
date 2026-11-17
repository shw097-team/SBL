"""Read-only checker for `SBL.SourceAdjudication@1` (the reader's per-Source-ID decision).

THE SEPARATION THIS MODULE EXISTS TO ENFORCE
    The compiler may emit atoms and FirstFail. It may NOT emit Accept / N-A / NACK: it has no
    applicability input, no reader identity and no authority. The decision is the original SBL
    PIPD Reader's act, recorded as one signed record per Source ID. This module only CHECKS that
    such a record exists, resolves against the right clause, and was signed by a key the owner
    enrolled for the original reader. It never writes, never re-decides, never edits a bundle
    verdict.

WHY `UNVERIFIED` IS THE DEFAULT
    A record that carries only a `reader_identity` string, or an `authority_ref` path, is a NAME,
    not proof: anyone can type a reader's name into a JSON file. Unless an Ed25519 signature over
    the canonical payload verifies against a key that comes from the committed enrollment - never
    from the record itself - the record is `UNVERIFIED` and does not count as a decision. With no
    key enrolled, EVERY record is `UNVERIFIED`; that is the state of the tree today and it is the
    correct one.

READ-ONLY
    `validate --adjudications` attaches an `adjudication` block beside the existing verdict. The
    bundle's `verdict`, `checked`, `closure`, `scope`, `missing`, `complete` and `findings` are
    untouched: "is this four-object bundle schema-and-trace valid" and "did the reader decide the
    wave" are different questions, and a bundle PASS must not become FAIL because decisions are
    still pending.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import InputShapeInvalid, IoNotFound, ParseInvalid
from .util import canonical_json, sha256_text

SCHEMA = "SBL.SourceAdjudication@1"
ENROLLMENT_SCHEMA = "SBL.READER_ENROLLMENT@1"
DECISIONS = ("ACCEPT", "NOT_APPLICABLE", "NACK")
CLAIM_CEILING = "READER_ADJUDICATION_NOT_PRODUCT_ACCEPTANCE"
#: Signed payload fields. A signature only proves something if it covers the BINDING, not just the
#: decision word: the source, the subject, the span and the clause digest are all inside it.
PAYLOAD_FIELDS = ("schema", "source_id", "subject_sha256", "clause_id", "span", "clause_sha256",
                  "decision", "basis", "reader_id", "decided_at", "claim_ceiling")
#: The compiler's refusal vocabulary. A record whose basis is one of these is the compiler's
#: refusal laundered into a reader decision, which is the exact substitution the ruling forbids.
COMPILER_REFUSAL_CODES = ("INTAKE_INVALID", "AUTHORITY_UNKNOWN", "PI_SCHEMA", "PI_SEMANTIC",
                          "TRACE_FAIL", "TQ_TRACE", "TQ_ORACLE", "TQ_SOD", "VALIDATION_FAIL",
                          "REPO_CONTEXT_MISSING", "STALE_PROVIDER", "ECP_PERMISSION",
                          "EFFECT_UNKNOWN", "PROJECTION_LOSS", "EXPORT_HASH", "ZERO_OBLIGATION")
SEVERITY_REFUSED = "REFUSED"
SEVERITY_UNVERIFIED = "UNVERIFIED"


def canonical_enrollment() -> Path:
    """<integrations/pipd>/contracts/reader-enrollment.json, derived from this module's location."""
    return Path(__file__).resolve().parents[2] / "contracts" / "reader-enrollment.json"


def schema_path() -> Path:
    """The family schema, kept in ``contracts/`` - NOT in ``schemas/``.

    ``schemas/`` is the S0 exact-19 surface and ``tools/registry_reconcile.py`` refuses a 20th
    file there, which is the correct guard: SBL.SourceAdjudication@1 is a pre-V2 reader-side
    family, not a member of the ratified 19. Resolving it from the package's own ``contracts/``
    directory keeps that count at 19 and stops a workspace-local ``schemas/`` copy from shadowing
    the checker's idea of the record shape.
    """
    return Path(__file__).resolve().parents[2] / "contracts" / "SourceAdjudication.schema.json"


def _load_json(path: Path, what: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise IoNotFound(f"cannot read {what} at {path}: {exc.strerror or type(exc).__name__}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseInvalid(f"{what} at {path} is not valid JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise InputShapeInvalid(f"{what} at {path} must be a JSON object")
    return data


def _read_records(path: Path) -> list[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise IoNotFound(f"cannot read adjudications at {path}: {exc.strerror or type(exc).__name__}") from exc
    suffix = path.suffix.lower()
    if suffix in (".jsonl", ".ndjson"):
        records = []
        for number, line in enumerate(raw.splitlines(), 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ParseInvalid(f"adjudication line {number} of {path} is not JSON: {exc.msg}") from exc
    elif suffix == ".json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ParseInvalid(f"adjudications at {path} are not valid JSON: {exc.msg}") from exc
        records = data.get("records") if isinstance(data, dict) else data
    else:
        raise InputShapeInvalid(f"adjudications at {path} must be .jsonl or .json "
                                f"(got {path.suffix or 'no suffix'})")
    if not isinstance(records, list):
        raise InputShapeInvalid(f"adjudications at {path} must be a list of records")
    return records


def read_subject_index(path: Path) -> dict[str, dict[str, Any]]:
    """The expected Source ID set, from a wave Source Span table (TSV with a header row).

    Only identity columns are read: `source_id`, `clause_id`, `span_start`, `span_end`,
    `clause_sha256`, `source_sha256`. A table without `source_id` cannot express expectations and
    is refused by name rather than silently treated as empty.
    """
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise IoNotFound(f"cannot read the source index at {path}: "
                         f"{exc.strerror or type(exc).__name__}") from exc
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if not lines:
        raise InputShapeInvalid(f"the source index at {path} is empty")
    header = lines[0].split("\t")
    if "source_id" not in header:
        raise InputShapeInvalid(f"the source index at {path} has no `source_id` column "
                                f"(columns: {header})")
    index: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(lines[1:], 2):
        cells = line.split("\t")
        row = {k: (cells[i] if i < len(cells) else "") for i, k in enumerate(header)}
        source_id = row.get("source_id", "").strip()
        if not source_id:
            continue
        if source_id in index:
            index[source_id]["_duplicate_rows"] = True
        row["_row_no"] = number
        index[source_id] = row
    return index


def _payload_of(record: dict[str, Any]) -> bytes:
    body = {k: record.get(k) for k in PAYLOAD_FIELDS}
    return canonical_json(body).encode("utf-8")


def _verify_ed25519(public_hex: str, signature_hex: str, payload: bytes) -> tuple[bool, str]:
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception:
        # a missing verifier is a refusal, never a pass
        return False, "READER_SIGNATURE_VERIFIER_UNAVAILABLE"
    try:
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex))
    except Exception as exc:
        return False, "READER_KEY_UNREADABLE:" + type(exc).__name__
    try:
        key.verify(bytes.fromhex(signature_hex), payload)
    except InvalidSignature:
        return False, "ADJUDICATION_SIGNATURE_INVALID"
    except Exception as exc:
        return False, "ADJUDICATION_SIGNATURE_UNREADABLE:" + type(exc).__name__
    return True, ""


def _enrollment(path: Path | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """(enrollment, reader_key report). A test-fixture key may never read as original authority."""
    report: dict[str, Any] = {"state": "READER_KEY_NOT_ENROLLED", "reader_id": "",
                              "fingerprint": None, "fixture_key": False,
                              "enrollment_path": "", "authority": ""}
    target = Path(path) if path else canonical_enrollment()
    report["enrollment_path"] = str(target)
    if not target.is_file():
        report["state"] = "READER_ENROLLMENT_MISSING"
        return {}, report
    body = _load_json(target, "reader enrollment")
    if body.get("schema") != ENROLLMENT_SCHEMA:
        report["state"] = "READER_ENROLLMENT_SCHEMA"
        return {}, report
    report["reader_id"] = str(body.get("reader_id") or "")
    report["authority"] = str(body.get("authority") or "")
    # The enrollment's OWN lifecycle string is reported, never trusted as a verdict: the checker's
    # state is derived from whether a KEY is present, so editing the file to say
    # "READER_KEY_ENROLLED" cannot enrol anything.
    report["enrollment_state"] = str(body.get("state") or "")
    key = str(body.get("reader_public_hex") or "").strip()
    if path is not None and report["authority"] != "TEST_FIXTURE_ONLY":
        # Substituting an enrollment is how a maker would sign its own adjudications.
        report["state"] = "READER_ENROLLMENT_NOT_TEST_FIXTURE"
        return {}, report
    if not key:
        report["state"] = "READER_KEY_NOT_ENROLLED"
        return {}, report
    report["state"] = "READER_KEY_ENROLLED"
    report["fingerprint"] = body.get("reader_fingerprint")
    report["fixture_key"] = report["authority"] == "TEST_FIXTURE_ONLY"
    report["reader_public_hex"] = key
    return body, report


def _basis_launders_refusal(record: dict[str, Any]) -> str:
    """Name the compiler refusal a record is dressing up as a reader decision, or ''."""
    if record.get("derived_from_compiler_refusal") is True:
        return str(record.get("basis_code") or "INTAKE_INVALID")
    text = " ".join(str(record.get(k) or "") for k in ("basis", "basis_code", "rationale")).upper()
    for code in COMPILER_REFUSAL_CODES:
        if code in text:
            return code
    return ""


def check(records_path: Path | str, *, source_index: Path | str | None = None,
          subject: Path | str | None = None,
          enrollment: Path | str | None = None, maker: str = "",
          reader_id: str = "ORIGINAL_SBL_PIPD_READER") -> dict[str, Any]:
    """Read-only verification of a set of adjudication records. Returns the `adjudication` block."""
    records = _read_records(Path(records_path))
    _enrollment_body, key = _enrollment(Path(enrollment) if enrollment else None)
    subject_sha = ""
    subject_text = ""
    if subject:
        subject_path = Path(subject)
        try:
            subject_text = subject_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise IoNotFound(f"cannot read the pinned subject at {subject_path}: "
                             f"{exc.strerror or type(exc).__name__}") from exc
        subject_sha = sha256_text(subject_text)
    index = read_subject_index(Path(source_index)) if source_index else {}

    schema_findings: list[str] = []
    schema = None
    record_schema_path = schema_path()
    if record_schema_path.is_file():
        schema = json.loads(record_schema_path.read_text(encoding="utf-8"))
    else:
        # fail closed: a shape check that cannot run is not a shape pass
        schema_findings.append(f"SourceAdjudication.schema.json not found at "
                               f"{record_schema_path}; the record shape was NOT checked")

    findings: list[dict[str, Any]] = []
    out_records: list[dict[str, Any]] = []
    by_decision = {d: 0 for d in DECISIONS}
    seen: dict[str, int] = {}
    decided_verified = 0

    for position, record in enumerate(records, 1):
        if not isinstance(record, dict):
            findings.append({"kind": SEVERITY_REFUSED, "code": "ADJUDICATION_RECORD_SHAPE",
                             "source_id": "", "detail": f"record {position} is not an object"})
            out_records.append({"index": position, "state": SEVERITY_REFUSED,
                                "code": "ADJUDICATION_RECORD_SHAPE", "decision": None})
            continue
        source_id = str(record.get("source_id") or "")
        codes: list[dict[str, str]] = []

        if schema is not None:
            try:
                from jsonschema import Draft202012Validator
            except ImportError:  # pragma: no cover
                raise InputShapeInvalid("jsonschema is unavailable; a schema check that cannot run "
                                        "is not a schema pass") from None
            for err in sorted(Draft202012Validator(schema).iter_errors(record),
                              key=lambda e: list(e.absolute_path)):
                pointer = "/" + "/".join(str(x) for x in err.absolute_path)
                codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_SCHEMA",
                              "detail": f"{source_id or '?'}{pointer}: {err.message}"})

        # --- identity binding ------------------------------------------------
        if source_id in seen:
            codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_DUPLICATE",
                          "detail": f"records {seen[source_id]} and {position} both decide {source_id}"})
        seen.setdefault(source_id, position)
        if index and source_id not in index:
            codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_SOURCE_UNKNOWN",
                          "detail": f"{source_id} is not a Source ID of the bound index"})
        if subject_sha:
            declared = str(record.get("subject_sha256") or "")
            if declared != subject_sha:
                codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_SUBJECT_MISMATCH",
                              "detail": f"{source_id}: record binds subject_sha256 "
                                        f"{declared[:16] or '(absent)'}... but the pinned subject "
                                        f"digests to {subject_sha[:16]}..."})
        row = index.get(source_id)
        if row is not None:
            if str(row.get("clause_id") or "") and str(record.get("clause_id") or "") != str(row["clause_id"]):
                codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_SOURCE_MISMATCH",
                              "detail": f"{source_id}: decision is bound to clause "
                                        f"{record.get('clause_id')!r} but the index binds "
                                        f"{row['clause_id']!r}"})
            if str(row.get("clause_sha256") or ""):
                declared = str(record.get("clause_sha256") or "")
                if declared != str(row["clause_sha256"]):
                    codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_SOURCE_MISMATCH",
                                  "detail": f"{source_id}: clause_sha256 {declared[:16]}... does "
                                            f"not match the index digest {row['clause_sha256'][:16]}..."})
            span = record.get("span")
            if isinstance(span, list) and len(span) == 2 and str(row.get("span_start") or ""):
                try:
                    want = (int(row["span_start"]), int(row["span_end"]))
                except (TypeError, ValueError):
                    want = None
                if want is not None and (int(span[0]), int(span[1])) != want:
                    codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_SOURCE_MISMATCH",
                                  "detail": f"{source_id}: record span {span} does not match the "
                                            f"index span {list(want)}"})
        # a tampered span is caught from first principles when the subject is pinned
        span = record.get("span")
        if isinstance(span, list) and len(span) == 2 and subject_text:
            try:
                start, end = int(span[0]), int(span[1])
            except (TypeError, ValueError):
                codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_SOURCE_MISMATCH",
                              "detail": f"{source_id}: span {span!r} is not two integers"})
                start = end = -1
            if start >= 0:
                if end > len(subject_text) or end <= start:
                    codes.append({"severity": SEVERITY_REFUSED,
                                  "code": "ADJUDICATION_SOURCE_MISMATCH",
                                  "detail": f"{source_id}: span [{start}, {end}) is outside the "
                                            f"pinned subject ({len(subject_text)} characters)"})
                else:
                    # the clause-id scheme is the compiler's own: clause-<start>-<end>. A record
                    # whose id and span disagree has been shifted onto different bytes.
                    want_id = f"clause-{start}-{end}"
                    if str(record.get("clause_id") or "") != want_id:
                        codes.append({"severity": SEVERITY_REFUSED,
                                      "code": "ADJUDICATION_SOURCE_MISMATCH",
                                      "detail": f"{source_id}: clause_id "
                                                f"{record.get('clause_id')!r} does not name its own "
                                                f"span [{start}, {end}) (expected {want_id!r})"})
                    measured = sha256_text(subject_text[start:end])
                    if str(record.get("clause_sha256") or "") != measured:
                        codes.append({"severity": SEVERITY_REFUSED,
                                      "code": "ADJUDICATION_SOURCE_MISMATCH",
                                      "detail": f"{source_id}: clause_sha256 "
                                                f"{str(record.get('clause_sha256'))[:16]}... is not "
                                                f"the digest of the pinned subject bytes at "
                                                f"[{start}, {end}) ({measured[:16]}...)"})

        # --- decision vocabulary ---------------------------------------------
        decision = record.get("decision")
        if decision not in DECISIONS:
            codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_UNKNOWN_DECISION",
                          "detail": f"{source_id}: decision {decision!r} is not one of {DECISIONS}"})
        # --- the refusal-to-decision substitution ----------------------------
        laundered = _basis_launders_refusal(record)
        if laundered:
            codes.append({"severity": SEVERITY_REFUSED,
                          "code": "INTAKE_INVALID_IS_NOT_A_DISPOSITION",
                          "detail": f"{source_id}: the basis is the compiler refusal {laundered}; "
                                    "a compiler refusal is not a reader decision and may not be "
                                    "recorded as one"})
        # --- self-acceptance --------------------------------------------------
        claimed_reader = str(record.get("reader_id") or record.get("reader_identity") or "")
        if maker and claimed_reader and claimed_reader == maker:
            codes.append({"severity": SEVERITY_REFUSED, "code": "SELF_ACCEPT",
                          "detail": f"{source_id}: reader_id {claimed_reader!r} is the maker; "
                                    "TQ_SOD forbids a maker accepting its own work"})
        if key.get("reader_id") and claimed_reader and claimed_reader != key["reader_id"]:
            codes.append({"severity": SEVERITY_REFUSED, "code": "ADJUDICATION_READER_MISMATCH",
                          "detail": f"{source_id}: record names reader {claimed_reader!r} but the "
                                    f"enrolled reader is {key['reader_id']!r}"})

        # --- the signature: the ONLY thing that can promote a record ---------
        signature = record.get("signature")
        unverified_code = ""
        if not codes:
            if not isinstance(signature, dict) or not str(signature.get("signature_hex") or "").strip():
                unverified_code = "ADJUDICATION_UNSIGNED"
            elif key.get("state") != "READER_KEY_ENROLLED":
                unverified_code = str(key.get("state") or "READER_KEY_NOT_ENROLLED")
            else:
                payload = _payload_of(record)
                if signature.get("payload_sha256") != sha256_text(payload.decode("utf-8")):
                    codes.append({"severity": SEVERITY_REFUSED,
                                  "code": "ADJUDICATION_PAYLOAD_MISMATCH",
                                  "detail": f"{source_id}: payload_sha256 does not cover this record's "
                                            "own binding fields (the record was edited after signing)"})
                else:
                    ok, why = _verify_ed25519(str(key.get("reader_public_hex") or ""),
                                              str(signature.get("signature_hex")), payload)
                    if not ok:
                        codes.append({"severity": SEVERITY_REFUSED, "code": why,
                                      "detail": f"{source_id}: the record's signature does not verify "
                                                "against the enrolled reader key"})

        refused = [c for c in codes if c["severity"] == SEVERITY_REFUSED]
        if refused:
            state = SEVERITY_REFUSED
        elif unverified_code:
            state = SEVERITY_UNVERIFIED
            refused = [{"severity": SEVERITY_UNVERIFIED, "code": unverified_code,
                        "detail": (f"{source_id}: no verifiable original-reader signature; a "
                                   "reader_identity string or an authority_ref path is a claim, "
                                   "not proof")}]
        else:
            state = "VERIFIED"
            decided_verified += 1
            if decision in by_decision:
                by_decision[decision] += 1
        for finding in refused:
            findings.append({"kind": finding["severity"], "code": finding["code"],
                             "source_id": source_id, "detail": finding["detail"]})
        out_records.append({
            "index": position,
            "source_id": source_id,
            "clause_id": record.get("clause_id"),
            "decision": decision if state == "VERIFIED" else None,
            "claimed_decision": decision,
            "state": state,
            "codes": [c["code"] for c in refused],
            "reader_id": claimed_reader,
            "signed": isinstance(signature, dict),
        })

    expected = len(index) if index else len({str(r.get("source_id") or "") for r in records
                                             if isinstance(r, dict)})
    decided_ids = {r["source_id"] for r in out_records if r["state"] == "VERIFIED"}
    missing = sorted(set(index) - decided_ids) if index else []
    for source_id in missing:
        findings.append({"kind": SEVERITY_UNVERIFIED, "code": "ADJUDICATION_MISSING",
                         "source_id": source_id,
                         "detail": "the bound index carries this Source ID and no verified "
                                   "adjudication decides it"})

    states = {r["state"] for r in out_records}
    if SEVERITY_REFUSED in states:
        verdict = SEVERITY_REFUSED
    elif SEVERITY_UNVERIFIED in states or missing:
        verdict = SEVERITY_UNVERIFIED
    elif decided_verified == expected and expected:
        verdict = "COMPLETE"
    else:
        verdict = "INCOMPLETE"
    if key.get("fixture_key") and verdict == "COMPLETE":
        # a fixture key proves the verifier works; it is not the original reader's authority
        verdict = "COMPLETE_FIXTURE_KEY_ONLY"

    return {
        "schema": SCHEMA,
        "read_only": True,
        "wrote_nothing": True,
        "records_file": str(records_path),
        "expected": expected,
        "denominator_source": "SOURCE_INDEX" if index else "ADJUDICATIONS_ONLY",
        "decided": decided_verified,
        "undecided": expected - decided_verified,
        "by_decision": by_decision,
        "states": {s: sum(1 for r in out_records if r["state"] == s)
                   for s in ("VERIFIED", SEVERITY_UNVERIFIED, SEVERITY_REFUSED)},
        "original_reader_signature_verified": bool(decided_verified) and not key.get("fixture_key"),
        "reader_key": key,
        "verdict": verdict,
        "findings": findings,
        "schema_check": schema_findings,
        "records": out_records,
        "claim_ceiling": (CLAIM_CEILING if not key.get("fixture_key")
                          else "FIXTURE_KEY_NOT_ORIGINAL_READER"),
        "note": ("this block is a check of the reader's records, not a compiler decision; it does "
                 "not change the bundle verdict and grants no acceptance"),
    }
