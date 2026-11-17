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

H-01 -- WHAT THE HOLD ACTUALLY WAITS ON
    H-01 is the hold on the wave's undisposed Source IDs. The only thing that releases it is the
    ORIGINAL Reader's own per-Source-ID disposition -- one ACCEPT / NOT_APPLICABLE / NACK per
    Source ID of the declared denominator, bound to the pinned subject and signed by the key the
    owner enrolled for that reader. It is NOT released by a signature as such, not by a bundle
    verdict, not by an exit code, and never by a TEST_FIXTURE key: a fixture signature proves the
    verifier works and carries no disposition of its own, so it is structurally incapable of
    releasing H-01 (see ``H01_FIXTURE_KEY_CANNOT_RELEASE`` and the ``hold_h01`` block below).
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
SEVERITY_CAPPED = "CAPPED"
#: Verdicts that can only ever be produced by a capped / incomplete run. A consumer that reads a
#: verdict off this list as "the reader decided the wave" has read a name, not a completion.
INCOMPLETE_VERDICTS = ("INCOMPLETE", "INCOMPLETE_DENOMINATOR_UNDECLARED",
                       "INCOMPLETE_SUBJECT_UNBOUND", "INCOMPLETE_PARTIAL_COVERAGE",
                       "UNVERIFIED", "REFUSED", "COMPLETE_FIXTURE_KEY_ONLY")

#: The four completion gates. Each one is a REASON a run may not claim completion; none of them is
#: a new verb, a new contract family or a new reader key.
#: G1 - a run without --source-index or --subject has no declared denominator and cannot be complete
#: G2 - a signed subset is not the denominator; partial signatures never set a completion flag
#: G3 - original_reader_signature_verified is per-row, and the aggregate is true only when EVERY
#:      row of the DECLARED denominator is verified
#: G4 - consumer_gate() is the only accepted consumer check: adjudication.verdict + per-row
#:      decisions + coverage. Exit 0 and a PASS bundle are explicitly insufficient, by name
#:      (CONSUMER_* refusals), and `--require-consumer-gate` turns a refused gate into a non-zero
#:      exit so that "the command succeeded" cannot be read as "the wave was decided".
GATE_NO_DENOMINATOR = "ADJUDICATION_DENOMINATOR_UNDECLARED"
GATE_NO_SUBJECT = "ADJUDICATION_SUBJECT_UNBOUND"
GATE_PARTIAL_COVERAGE = "ADJUDICATION_PARTIAL_COVERAGE"
GATE_PARTIAL_SIGNATURE = "ADJUDICATION_PARTIAL_SIGNATURE_SET"
GATE_AGGREGATE_NOT_EVERY_ROW = "ADJUDICATION_ORIGINAL_READER_UNVERIFIED"

CONSUMER_NO_BLOCK = "CONSUMER_NO_ADJUDICATION_BLOCK"
CONSUMER_NOT_A_READ_CHECK = "CONSUMER_BLOCK_IS_NOT_A_READ_CHECK"
CONSUMER_VERDICT_NOT_COMPLETE = "CONSUMER_VERDICT_NOT_COMPLETE"
CONSUMER_DENOMINATOR_UNDECLARED = "CONSUMER_DENOMINATOR_UNDECLARED"
CONSUMER_PARTIAL_COVERAGE = "CONSUMER_PARTIAL_COVERAGE"
CONSUMER_ROW_NOT_VERIFIED = "CONSUMER_ROW_NOT_VERIFIED"
CONSUMER_ROW_DECISION_UNKNOWN = "CONSUMER_ROW_DECISION_UNKNOWN"
CONSUMER_ORIGINAL_READER_UNVERIFIED = "CONSUMER_ORIGINAL_READER_UNVERIFIED"
CONSUMER_BUNDLE_NOT_PASS = "CONSUMER_BUNDLE_NOT_PASS"
#: The single passage itself, named so a pipeline can act on a refused gate without re-deriving why.
CONSUMER_GATE_NOT_ACCEPTED = "CONSUMER_GATE_NOT_ACCEPTED"

#: The three signals that LOOK like a decision and are each individually insufficient. They are
#: published inside every gate result so no consumer has to be told twice, and each one has a NEG
#: in tests/test_clause_set_adjudication.py that fails if it ever becomes sufficient.
INSUFFICIENT_SIGNALS = (
    "exit_code_0",                                   # the command succeeded
    "bundle_verdict_PASS",                          # the four-object bundle is schema-and-trace valid
    "adjudication_verdict_COMPLETE_FIXTURE_KEY_ONLY",  # every signature verified -- under a fixture key
)
#: signal -> the refusal codes consumer_gate() returns when that signal is the ONLY thing a caller
#: has. Published with the gate result so a pipeline can pin the mapping instead of re-deriving it.
SIGNAL_REFUSALS = {
    "exit_code_0": [CONSUMER_VERDICT_NOT_COMPLETE],
    "bundle_verdict_PASS": [CONSUMER_NO_BLOCK, CONSUMER_VERDICT_NOT_COMPLETE],
    "adjudication_verdict_COMPLETE_FIXTURE_KEY_ONLY": [CONSUMER_VERDICT_NOT_COMPLETE,
                                                       CONSUMER_ORIGINAL_READER_UNVERIFIED],
}

#: H-01 is the hold on the wave's undisposed Source IDs. Its release condition is the ORIGINAL
#: Reader's own per-Source-ID disposition, not a signature: a TEST_FIXTURE key proves the verifier
#: runs and carries no ACCEPT / NOT_APPLICABLE / NACK of the reader's, so no fixture-signed record
#: set can release it, however many rows it covers.
H01_HOLD = "H-01"
H01_RELEASE_REQUIRES = "ORIGINAL_READER_PER_SOURCE_ID_DISPOSITION"
H01_DISPOSITIONS = DECISIONS
H01_FIXTURE_KEY_CANNOT_RELEASE = True


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
            # G3 (per row): this row, and only this row, carries a verified original-reader
            # signature. It is never inherited from the aggregate and never promoted to it.
            "original_reader_signature_verified": bool(state == "VERIFIED"
                                                       and not key.get("fixture_key")),
            # None = no denominator was declared, so membership is unknown, not false.
            "in_denominator": (source_id in index) if index else None,
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

    # --- G1: no declared denominator, no completion claim -------------------------------
    # Without --source-index the "expected" count is just the number of records the file happens
    # to carry, so a three-record file would read as a three-of-three complete wave. Without
    # --subject no binding field is recomputed from bytes, so a signature proves the signer
    # signed something, not this wave's clause. Both are named caps, not silent defaults.
    denominator_declared = bool(index) and bool(subject_sha)
    caps: list[dict[str, str]] = []
    if not index:
        caps.append({"code": GATE_NO_DENOMINATOR,
                     "detail": "no --source-index: the denominator is whatever the records file "
                               "names, so this run cannot declare a complete Original "
                               "Adjudication over the wave"})
    if not subject_sha:
        caps.append({"code": GATE_NO_SUBJECT,
                     "detail": "no --subject: subject_sha256, clause_id, span and clause_sha256 "
                               "are not recomputed from the pinned bytes, so a verified "
                               "signature is not a verified binding"})
    for cap in caps:
        findings.append({"kind": SEVERITY_CAPPED, "code": cap["code"], "source_id": "",
                         "detail": cap["detail"]})

    # --- G2/G3: coverage is computed against the DECLARED denominator only --------------
    coverage = coverage_summary(out_records, expected,
                                denominator_declared=denominator_declared,
                                fixture_key=bool(key.get("fixture_key")))
    for code in coverage["refusals"]:
        if code == GATE_PARTIAL_SIGNATURE:
            findings.append({"kind": SEVERITY_CAPPED, "code": code, "source_id": "",
                             "detail": f"{coverage['verified_in_denominator']} of "
                                       f"{coverage['expected']} declared Source IDs carry a "
                                       "verified signature; a signed subset is not the "
                                       "denominator and may not set a completion flag"})
        elif code == GATE_AGGREGATE_NOT_EVERY_ROW:
            findings.append({"kind": SEVERITY_CAPPED, "code": code, "source_id": "",
                             "detail": "original_reader_signature_verified stays false: the "
                                       "aggregate is true only when every row of the declared "
                                       "denominator is verified"})

    # H-01 counts the reader's OWN dispositions only. A row verified under a TEST_FIXTURE key is
    # state VERIFIED but its per-row original_reader_signature_verified is false, so it contributes
    # nothing here: that is what "a fixture key cannot release H-01" means at the data level.
    hold_dispositions = {d: 0 for d in H01_DISPOSITIONS}
    for row in out_records:
        if (row.get("original_reader_signature_verified") is True
                and row.get("decision") in hold_dispositions):
            hold_dispositions[row["decision"]] += 1

    states = {r["state"] for r in out_records}
    if SEVERITY_REFUSED in states:
        verdict = SEVERITY_REFUSED
    elif SEVERITY_UNVERIFIED in states or missing:
        verdict = SEVERITY_UNVERIFIED
    elif not index:
        verdict = "INCOMPLETE_DENOMINATOR_UNDECLARED"
    elif not subject_sha:
        verdict = "INCOMPLETE_SUBJECT_UNBOUND"
    elif coverage["verified_in_denominator"] != coverage["expected"] or coverage["expected"] == 0:
        verdict = "INCOMPLETE_PARTIAL_COVERAGE"
    elif key.get("fixture_key"):
        # a fixture key proves the verifier works; it is not the original reader's authority
        verdict = "COMPLETE_FIXTURE_KEY_ONLY"
    elif coverage["original_reader_signature_verified"]:
        verdict = "COMPLETE"
    else:
        verdict = "INCOMPLETE"

    return {
        "schema": SCHEMA,
        "read_only": True,
        "wrote_nothing": True,
        "records_file": str(records_path),
        "expected": coverage["expected"],
        "denominator_source": "SOURCE_INDEX" if index else "ADJUDICATIONS_ONLY",
        # G1: named denominators, so "complete" can never be reached by omission.
        "denominator_declared": denominator_declared,
        "denominator_caps": caps,
        "decided": coverage["verified"],
        "undecided": coverage["expected"] - coverage["verified_in_denominator"],
        "by_decision": by_decision,
        "states": {s: sum(1 for r in out_records if r["state"] == s)
                   for s in ("VERIFIED", SEVERITY_UNVERIFIED, SEVERITY_REFUSED)},
        # G2/G3: `complete` is the ONLY full-completion flag, it is per-run and it is false
        # unless every row of the declared denominator is verified. `completion_refusals`
        # names why, so a false is never mistaken for "not checked".
        "complete": coverage["complete"],
        "completion_refusals": coverage["refusals"],
        "coverage": coverage,
        "original_reader_signature_verified": coverage["original_reader_signature_verified"],
        "reader_key": key,
        "verdict": verdict,
        "findings": findings,
        "schema_check": schema_findings,
        "records": out_records,
        "claim_ceiling": (CLAIM_CEILING if not key.get("fixture_key")
                          else "FIXTURE_KEY_NOT_ORIGINAL_READER"),
        # H-01's own state, derived from the same coverage the verdict is derived from: a hold is
        # released only by the original reader's per-Source-ID disposition, so it can be RELEASED
        # only on a verdict that requires exactly that. A fixture key cannot appear here as a
        # release: it never reaches "COMPLETE", `released_by` names the disposition, not a
        # signature, and `dispositions` counts ONLY rows whose per-row original-reader flag is true
        # -- a fixture-verified ACCEPT is not a disposition of the reader's and counts as zero.
        "hold_h01": {
            "hold_id": H01_HOLD,
            "state": "RELEASED" if verdict == "COMPLETE" else "HELD",
            "released_by": H01_RELEASE_REQUIRES,
            "dispositions": hold_dispositions,
            "disposition_vocabulary": list(H01_DISPOSITIONS),
            "fixture_key_cannot_release": H01_FIXTURE_KEY_CANNOT_RELEASE,
            "why": ("H-01 waits on the original Reader's own ACCEPT / NOT_APPLICABLE / NACK for each "
                    "Source ID of the declared denominator. A TEST_FIXTURE signature verifies the "
                    "checker, carries no disposition and therefore cannot release the hold, even "
                    "when every row of the wave is fixture-signed."),
        },
        "note": ("this block is a check of the reader's records, not a compiler decision; it does "
                 "not change the bundle verdict and grants no acceptance"),
    }


def coverage_summary(rows: list[dict[str, Any]], expected: int, *,
                     denominator_declared: bool, fixture_key: bool) -> dict[str, Any]:
    """G2/G3 in one place: what coverage this record set actually has, and what it may claim.

    ``verified`` counts rows whose signature verified (fixture or not). ``verified_in_denominator``
    counts only rows that are members of the DECLARED denominator, which is why a records-only run
    can never be reported as covered. ``original_reader_signature_verified`` is the aggregate the
    ruling cares about: it is true only when the denominator was declared AND every member of it
    has a row whose own per-row flag is true AND no row was refused.
    """
    refusals: list[str] = []
    verified = sum(1 for r in rows if r.get("state") == "VERIFIED")
    in_denominator = sum(1 for r in rows if r.get("state") == "VERIFIED"
                         and r.get("in_denominator") is not False)
    per_row_all = bool(rows) and all(r.get("original_reader_signature_verified") is True
                                     for r in rows)
    refused_rows = sum(1 for r in rows if r.get("state") == SEVERITY_REFUSED)

    if not denominator_declared:
        refusals.append(GATE_NO_DENOMINATOR)
    if expected and in_denominator < expected:
        refusals.append(GATE_PARTIAL_SIGNATURE)
    if not per_row_all or verified < expected or refused_rows:
        refusals.append(GATE_AGGREGATE_NOT_EVERY_ROW)
    if expected == 0:
        refusals.append(GATE_PARTIAL_COVERAGE)

    aggregate = bool(denominator_declared and per_row_all and expected > 0
                     and in_denominator == expected and verified == expected
                     and not fixture_key and not refused_rows)
    complete = bool(aggregate and not refusals)
    return {
        "expected": expected,
        "verified": verified,
        "verified_in_denominator": in_denominator,
        "not_in_denominator": verified - in_denominator,
        "refused_rows": refused_rows,
        "every_row_verified": per_row_all,
        "denominator_declared": denominator_declared,
        "fixture_key": fixture_key,
        "original_reader_signature_verified": aggregate,
        "complete": complete,
        "refusals": sorted(set(refusals)),
    }


def consumer_gate(validate_output: dict[str, Any] | None,
                  adjudication_block: dict[str, Any] | None = None) -> dict[str, Any]:
    """G4 - the ONLY check an automated consumer may run. Exit code and bundle PASS are not it.

    Call it with the WHOLE `validate` payload (bundle verdict + `adjudication` beside it); a
    consumer that was handed only the four-object bundle file has no verdict to read and is
    refused with ``CONSUMER_NO_ADJUDICATION_BLOCK``.

    A `validate --adjudications` run can exit 0 with a `PASS` bundle and an `adjudication.verdict`
    of `UNVERIFIED`, `INCOMPLETE_*` or `COMPLETE_FIXTURE_KEY_ONLY`, because the two denominators are
    deliberately independent. A consumer that treats "exit 0", `bundle["verdict"] == "PASS"` or a
    `COMPLETE_FIXTURE_KEY_ONLY` verdict as "the wave was decided" has therefore accepted an
    undecided wave. This function refuses, by name, every shape of that mistake and returns
    ``{"accepted": bool, "refusals": [...]}``.

    ``accepted is True`` is the only lawful passage. Each of the three signals that look like one
    is individually insufficient -- ``INSUFFICIENT_SIGNALS`` names them and ``SIGNAL_REFUSALS``
    gives the refusal code each one earns when it is all a caller has. Bundle PASS is necessary and
    never sufficient; a non-PASS bundle is refused here too so a consumer cannot read decisions off
    an invalid bundle.
    """
    refusals: list[dict[str, str]] = []
    if adjudication_block is None and isinstance(validate_output, dict):
        adjudication_block = validate_output.get("adjudication")

    if not isinstance(adjudication_block, dict):
        refusals.append({"code": CONSUMER_NO_BLOCK,
                         "detail": "no adjudication block: a PASS bundle says nothing about "
                                   "whether the reader decided the wave; re-run validate with "
                                   "--adjudications and pass its whole output"})
        return {"accepted": False, "refusals": refusals, "verdict": None,
                "required_verdict": "COMPLETE", "exit_code_is_not_a_check": True,
                "bundle_pass_is_not_sufficient": True,
                "fixture_complete_is_not_sufficient": True,
                "insufficient_signals": list(INSUFFICIENT_SIGNALS),
                "signal_refusals": {k: list(v) for k, v in SIGNAL_REFUSALS.items()}}

    if adjudication_block.get("read_only") is not True:
        refusals.append({"code": CONSUMER_NOT_A_READ_CHECK,
                         "detail": "the block does not identify itself as a read-only check of "
                                   "the reader's records"})

    bundle_verdict = (validate_output or {}).get("verdict")
    if bundle_verdict != "PASS":
        refusals.append({"code": CONSUMER_BUNDLE_NOT_PASS,
                         "detail": f"bundle verdict is {bundle_verdict!r}; decisions may not be "
                                   "read off a bundle that is not PASS"})

    verdict = adjudication_block.get("verdict")
    if verdict != "COMPLETE":
        refusals.append({"code": CONSUMER_VERDICT_NOT_COMPLETE,
                         "detail": f"adjudication.verdict is {verdict!r}; only 'COMPLETE' is a "
                                   f"decided wave (capped/incomplete: "
                                   f"{', '.join(INCOMPLETE_VERDICTS)})"})

    if adjudication_block.get("denominator_declared") is not True:
        refusals.append({"code": CONSUMER_DENOMINATOR_UNDECLARED,
                         "detail": "no declared denominator (--source-index/--subject); coverage "
                                   "is unknowable, so no count in this block is a coverage claim"})

    expected = adjudication_block.get("expected")
    decided = adjudication_block.get("decided")
    rows = adjudication_block.get("records")
    rows = rows if isinstance(rows, list) else []
    coverage = adjudication_block.get("coverage") or {}
    if (not isinstance(expected, int) or expected <= 0 or decided != expected
            or len(rows) != expected
            or coverage.get("verified_in_denominator") != expected):
        refusals.append({"code": CONSUMER_PARTIAL_COVERAGE,
                         "detail": f"decided={decided!r} expected={expected!r} "
                                   f"rows={len(rows)} verified_in_denominator="
                                   f"{coverage.get('verified_in_denominator')!r}: a partial set "
                                   "is not the denominator"})

    # per-row refusals are grouped by code so a 428-row wave yields a few named refusals, not 428
    row_problems: dict[str, list[str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            row_problems.setdefault(CONSUMER_ROW_NOT_VERIFIED, []).append("<not an object>")
            continue
        source_id = str(row.get("source_id") or "?")
        if row.get("state") != "VERIFIED":
            row_problems.setdefault(CONSUMER_ROW_NOT_VERIFIED, []).append(source_id)
        if row.get("decision") not in DECISIONS:
            row_problems.setdefault(CONSUMER_ROW_DECISION_UNKNOWN, []).append(source_id)
        if row.get("original_reader_signature_verified") is not True:
            row_problems.setdefault(CONSUMER_ORIGINAL_READER_UNVERIFIED, []).append(source_id)
    for code, ids in row_problems.items():
        shown = ", ".join(ids[:3]) + (f", +{len(ids) - 3} more" if len(ids) > 3 else "")
        refusals.append({"code": code,
                         "detail": f"{len(ids)} of {len(rows)} row(s) fail this check: {shown}"})

    if adjudication_block.get("original_reader_signature_verified") is not True:
        refusals.append({"code": CONSUMER_ORIGINAL_READER_UNVERIFIED,
                         "detail": "the aggregate original_reader_signature_verified is not true"})

    if adjudication_block.get("complete") is not True:
        refusals.append({"code": CONSUMER_VERDICT_NOT_COMPLETE,
                         "detail": "the run does not set complete=true; refusals: "
                                   f"{adjudication_block.get('completion_refusals')}"})

    return {"accepted": not refusals,
            "refusals": refusals,
            "verdict": verdict,
            "required_verdict": "COMPLETE",
            "rows_checked": len(rows),
            "exit_code_is_not_a_check": True,
            "bundle_pass_is_not_sufficient": True,
            "fixture_complete_is_not_sufficient": True,
            "insufficient_signals": list(INSUFFICIENT_SIGNALS),
            "signal_refusals": {k: list(v) for k, v in SIGNAL_REFUSALS.items()},
            "only_lawful_passage": "consumer_gate().accepted is True"}


def enforce_consumer_gate(validate_output: dict[str, Any], *, required: bool = False) -> dict[str, Any]:
    """Stamp the single lawful passage into a `validate` payload and say what it decided.

    ``consumer_gate()`` is a function; a pipeline that never calls it has no gate at all. This
    helper exists so the assembled `validate` payload carries the gate's own result (nested in the
    read-only `adjudication` block, so the bundle half of the payload stays byte-identical), and so
    ``--require-consumer-gate`` has a single place to ask "must a refused gate stop this run".

    When ``required`` is true and the gate refuses, ``exit_code`` is 3 and the refusal list is
    prefixed with ``CONSUMER_GATE_NOT_ACCEPTED``: the run then cannot succeed on the bundle's exit
    code alone. When the gate accepts, ``exit_code`` is None and the CLI's normal exit code stands.

    Returns the same payload object it was given (mutated in place, `adjudication` only).
    """
    block = validate_output.get("adjudication") if isinstance(validate_output, dict) else None
    if not isinstance(block, dict):
        return validate_output
    gate = consumer_gate(validate_output)
    gate["required"] = bool(required)
    if required and not gate["accepted"]:
        gate["refusals"] = [{"code": CONSUMER_GATE_NOT_ACCEPTED,
                             "detail": "--require-consumer-gate was set and consumer_gate() "
                                       "refused: exit 0 + bundle PASS is not a decision"}] + gate["refusals"]
        gate["exit_code"] = 3
    else:
        gate["exit_code"] = None
    block["consumer_gate"] = gate
    return validate_output
