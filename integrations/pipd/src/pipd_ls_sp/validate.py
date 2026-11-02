"""Deterministic validation: schema + semantic invariants over the 19 families.

Deterministic only: no LLM judge is consulted here (總藍圖 §5.9.1 responsibility split).
"""
from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from . import registry
from .errors import ValidationFail

CLAIM_LADDER = ["PROMPT_COMPILE_PASS", "HGK_ADMITTED", "RUNTIME_READY", "LOCAL_QUALIFIED",
                "INDEPENDENT_PASS", "PUBLICATION_APPROVED", "RELEASED", "PRODUCTION_VERIFIED"]
RELEASE_BOUND = ("PI-PKG", "PD-PKG", "ECP", "TQAEP", "ConstructionContract")

# CE-2 refinement (checker counterexample CE-CODEX-TRACE-WIDENING). Two DISTINCT concepts that
# used to be conflated into one list: "fields excluded from the body hash" and "fields that are
# not part of the record at all". They overlap only on `_profile_meta`.
#
# HASH_EXCLUDED_FIELDS -- the fields the body hash does NOT cover: the universal identity fields
#   (recomputed after sealing), the derived `trace` relation (it carries the parent hash, so it
#   cannot sit inside the hash it references) and the `_profile_meta` sidecar. This is the
#   HASH-EXCLUSION set ONLY; it says nothing about which fields a schema declares. `_body_hash`
#   and `pipeline._seal` both reference THIS object, so the hash and its recomputation stay one
#   definition and cannot diverge.
HASH_EXCLUDED_FIELDS = ("subject_id", "version", "content_hash", "schema_version", "trace",
                        "_profile_meta")

# NON_RECORD_SIDECARS -- the fields the pipeline emits for the operator/registry that NO schema
#   declares at all. Today that is exactly `_profile_meta`. `validate_record` strips ONLY this
#   set before the schema check, so a field that is hash-excluded but IS declared by the schema
#   (the identity fields, or `trace` on PI-PKG) remains schema-enforced, and an undeclared
#   `trace` on PD-PKG/ECP/TQAEP is again rejected by `additionalProperties: false`, exactly as
#   the published validator behaves.
NON_RECORD_SIDECARS = ("_profile_meta",)


def _validator(schema: dict[str, Any]):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:  # pragma: no cover
        raise ValidationFail(f"jsonschema unavailable: {exc}") from exc
    return Draft202012Validator(schema)


def validate_record(contract: str, record: dict[str, Any], schemas_dir: Path | None = None) -> list[str]:
    """Return a list of deterministic findings; empty list == schema-valid.

    Schema validation runs on a COPY of the record with the genuine non-record sidecars
    (``NON_RECORD_SIDECARS`` - today only ``_profile_meta``) removed, so a bundle assembled from
    the compilers' own stdout (which carries ``_profile_meta``) is held to its declared field set
    instead of tripping ``additionalProperties: false``. This is exactly the "stripped before
    validation" behavior ``pipeline`` already declares.

    ``NON_RECORD_SIDECARS`` is deliberately NOT the same set as ``HASH_EXCLUDED_FIELDS``: a field
    can be excluded from the body hash (``trace``, the identity fields) yet still be part of the
    record's contract, so its presence must remain schema-enforced. Only the genuine non-record
    sidecar ``_profile_meta`` is stripped; the defensive "unless the schema declares it" guard
    keeps that safe even if a future schema chooses to declare a sidecar. This closes CE-2 without
    widening the accepted input.
    """
    schema = registry.load_schema(contract, schemas_dir)
    v = _validator(schema)
    declared = set(schema.get("properties") or {})
    body = {k: val for k, val in record.items()
            if k not in NON_RECORD_SIDECARS or k in declared}
    findings = []
    for err in sorted(v.iter_errors(body), key=lambda e: list(e.absolute_path)):
        pointer = "/" + "/".join(str(x) for x in err.absolute_path)
        findings.append(f"{contract}{pointer}: {err.message}")
    return findings


HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _claim_names(contract: str, field: str, value: Any, out: list[str]) -> list[str]:
    """TYPE5 (R5 §4.1): the two ClaimCeiling claim lists are arrays of DECLARED ladder claims.

    Before this guard the library read ``set(record.get(field, []))`` and indexed ``CLAIM_LADDER``
    directly, so five schema-admissible shapes (null, a mapping item, an undeclared claim name)
    escaped as native ``TypeError``/``ValueError`` and became an untyped crash instead of a named
    finding. Every one of them is now reported by name and the caller keeps only the claims that are
    genuinely declared, so no caller ever indexes the ladder with an unknown value.
    """
    if not isinstance(value, list):
        out.append(f"{contract}: {field} must be a list of declared claim names "
                   f"(got {type(value).__name__})")
        return []
    names: list[str] = []
    for item in value:
        if not isinstance(item, str):
            out.append(f"{contract}: {field} entries must be declared claim names "
                       f"(got {type(item).__name__})")
            continue
        if item not in CLAIM_LADDER:
            out.append(f"{contract}: {field} names the undeclared claim {item!r}")
            continue
        names.append(item)
    return names


def _body_hash(record: dict[str, Any]) -> str:
    """Recompute the record digest over everything EXCEPT the identity fields.

    Lets the validator catch a record whose body was edited without re-issuing its hash.
    """
    import hashlib
    import json
    body = {k: v for k, v in record.items() if k not in HASH_EXCLUDED_FIELDS}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def semantic_invariants(contract: str, record: dict[str, Any]) -> list[str]:
    """Semantic invariants that a JSON Schema cannot express."""
    out: list[str] = []
    ident = ("subject_id", "version", "content_hash", "schema_version")
    for field in ident:
        if field not in record:
            out.append(f"{contract}: missing universal identity field {field}")
    # C-5/C-6 repair: presence is not enough. An adversarial lane proved that null identities, a
    # non-hash content_hash and a tampered body all passed the previous presence-only check.
    for field in ident:
        if field in record and not str(record.get(field) or "").strip():
            out.append(f"{contract}: identity field {field} must be a non-empty string")
    ch = str(record.get("content_hash") or "")
    if ch and not HEX64.match(ch):
        out.append(f"{contract}: content_hash must be a 64-char lowercase sha256 hex digest")
    sid = str(record.get("subject_id") or "")
    if sid and len(sid) < 8:
        out.append(f"{contract}: subject_id is implausibly short to be a content id")
    if record.get("recomputed_body_hash_required") is True:
        pass  # explicit opt-out is itself rejected below for release-bound families
    if contract in RELEASE_BOUND and ch and len(record) > 4:
        if ch != _body_hash(record):
            out.append(f"{contract}: content_hash does not match the record body "
                       "(body edited without re-issuing identity)")
    sv = str(record.get("schema_version") or "")
    if sv and not (re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", sv) or re.match(r"^[A-Za-z0-9_.-]+@[0-9]+$", sv)):
        out.append(f"{contract}: schema_version must be semver or <Token>@<n>")
    if contract == "ClaimCeiling":
        allowed = set(_claim_names(contract, "allowed_claims",
                                   record.get("allowed_claims", []), out))
        forbidden = set(_claim_names(contract, "forbidden_escalation",
                                     record.get("forbidden_escalation", []), out))
        if allowed & forbidden:
            out.append("ClaimCeiling: a claim cannot be both allowed and forbidden")
        # C-8 repair: a maker could previously mint claim_ceiling(['INDEPENDENT_PASS']).
        receipts = record.get("receipts") or record.get("approval_receipt")
        authority = record.get("authority") or record.get("checker_identity")
        above = [c for c in allowed
                 if CLAIM_LADDER.index(c) > CLAIM_LADDER.index("LOCAL_QUALIFIED")]
        if above and not (receipts and authority):
            out.append("ClaimCeiling: claims above LOCAL_QUALIFIED require a bound approval "
                       "receipt AND a checker identity; a maker cannot mint them unilaterally")
    if contract == "TQAEP":
        # C-3 repair. The S0 TQAEP schema declares a fixed field set (additionalProperties=false),
        # so SoD evidence is carried INSIDE the declared `acceptance` field rather than by inventing
        # a 20th family or new top-level keys. An unsigned string comparison is not SoD.
        acc = record.get("acceptance")
        entries = [a for a in acc if isinstance(a, dict)] if isinstance(acc, list) else []
        if not entries:
            out.append("TQAEP: acceptance must carry a structured separation-of-duties entry "
                       "(maker/checker never compared or persisted = unproven independence)")
        for e in entries:
            maker, checker = e.get("maker_identity"), e.get("checker_identity")
            if not (maker and checker):
                out.append("TQAEP: acceptance entry missing maker_identity/checker_identity")
            elif maker == checker or e.get("distinct") is not True:
                out.append("TQAEP: maker and checker must be distinct with distinct=true")
            elif str(e.get("checker_execution_receipt") or "") in ("", "SELF_ATTESTED", "self", "same-process"):
                out.append("TQAEP: acceptance entry needs a checker_execution_receipt that is not "
                           "self-attested (maker cannot attest its own independence)")
    if contract == "WorkOrderCandidate":
        if record.get("candidate_only") is not True:
            out.append("WorkOrderCandidate: candidate_only must be fixed true (never runtime authority)")
    if contract == "GENIEProjectionRef":
        refs = record.get("target_refs")
        want = ("ProductGraph", "Profile", "Bundle", "GENIEArtifact")
        if not isinstance(refs, (list, dict)) or not all(
                any(w in str(x) for x in (refs if isinstance(refs, list) else refs.keys())) for w in want):
            out.append("GENIEProjectionRef: target_refs must cover ProductGraph/Profile/Bundle/GENIEArtifact")
    if contract == "ExecutionBindingRef" and str(record.get("state", "")).upper() == "ACKED":
        if not (record.get("receiver_binding_id") and record.get("receiver_binding_hash")):
            out.append("ExecutionBindingRef: ACK requires a real HGK receiver binding id+hash")
    if contract == "TraceLink":
        for side in ("from", "to"):
            if not (record.get(f"{side}_type") and record.get(f"{side}_id")):
                out.append(f"TraceLink: {side} endpoint incomplete")
    return out


def trace_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    """The trace edges a single record carries (PI-PKG nests them; TraceLink is one edge)."""
    if not isinstance(record, dict):
        return []
    trace = record.get("trace")
    if isinstance(trace, list):
        return [e for e in trace if isinstance(e, dict)]
    if record.get("from_id") and record.get("to_id"):
        return [record]
    return []


def closure_findings(bundle: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Atomic graph closure over the bundle's trace edges (S4EXT-R1 TT-S4EXT-002 / F002).

    ``state`` is one of:

    * ``SCHEMA_ONLY`` - the bundle carries NO trace edge, so no graph relation exists to close.
      This is a legal PARTIAL bundle (e.g. a scoped validate of LITE artifacts). It is labelled
      explicitly so a caller can never read a schema-only result as a trace-closed one.
    * ``FULL`` - every edge resolved: both endpoints exist inside the bundle and both recorded
      hashes equal the real endpoint hashes.
    * ``FAILED`` - at least one orphan endpoint or hash mismatch; a finding is emitted per problem.
      A bundle in this state can never return PASS.

    The closure REUSES ``pipeline.trace_closure`` (the C-10 repair that recomputes both sides of
    every edge) rather than introducing a second trace engine.
    """
    records = {k: v for k, v in bundle.items() if isinstance(v, dict)}
    edge_count = sum(len(trace_edges(r)) for r in records.values())
    if edge_count == 0:
        return {"state": "SCHEMA_ONLY", "edges": 0, "findings": []}
    from . import pipeline  # local import: pipeline imports this module for the shared field lists
    try:
        report = pipeline.trace_closure(records)
    except Exception as exc:  # fail closed: an unclosable graph is not a closed graph
        return {"state": "FAILED", "edges": edge_count,
                "findings": [{"contract": "*", "kind": "CLOSURE",
                              "detail": f"trace closure could not be computed: {exc!r}"}]}
    problems: list[str] = []
    # S4EXT-R1 external-AO finding C3: a syntactically valid endpoint whose declared TYPE
    # contradicts the family of the record its id actually resolves to must fail closed. Without
    # this, "PD-PKG/from" could point at a PI-PKG record and still be reported as a closed graph.
    family_of: dict[str, str] = {}
    for name, rec in records.items():
        fam = str(rec.get("schema_version") or "").split("@")[0] or name
        if rec.get("subject_id"):
            family_of[str(rec["subject_id"])] = fam
        for atom in (rec.get("stable_semantic_contract", {}) or {}).get("atoms", []) or []:
            if isinstance(atom, dict) and atom.get("subject_id"):
                # an atom declares its OWN family (RequirementAtom@1), not the parent's
                afam = str(atom.get("schema_version") or "").split("@")[0] or fam
                family_of[str(atom["subject_id"])] = afam
    for _name, rec in records.items():
        for edge in trace_edges(rec):
            for side in ("from", "to"):
                declared = edge.get(f"{side}_type")
                resolved = family_of.get(str(edge.get(f"{side}_id") or ""))
                if declared and resolved and str(declared) != resolved:
                    problems.append(
                        "endpoint type contradicts the resolved record family: "
                        f"{side}_type={declared} but {side}_id={edge.get(f'{side}_id')} "
                        f"resolves to {resolved}")
    for orphan in report.get("orphans") or []:
        problems.append(f"orphan trace endpoint: {orphan} is not present in the bundle")
    for bad in report.get("bad_hashes") or []:
        problems.append(f"trace endpoint hash mismatch: {bad}")
    if report.get("verdict") != "PASS" and not problems:
        problems.append("trace closure did not reach PASS over the bundle")
    return {"state": "FULL" if not problems else "FAILED", "edges": int(report.get("edges") or edge_count),
            "findings": [{"contract": "*", "kind": "CLOSURE", "detail": p} for p in problems]}


def validate_bundle(bundle: dict[str, dict[str, Any]], schemas_dir: Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    # C-4 repair: validate_bundle({}) used to return PASS with checked=0. An empty denominator is
    # not a verification result.
    if not bundle:
        return {"verdict": "FAIL", "checked": 0, "closure": "SCHEMA_ONLY",
                "findings": [{"contract": "*", "kind": "DENOMINATOR",
                              "detail": "empty bundle: zero records checked cannot be a PASS"}]}
    for contract, record in bundle.items():
        if not isinstance(record, dict):
            findings.append({"contract": contract, "kind": "SCHEMA",
                             "detail": "record must be an object"})
            continue
        for f in validate_record(contract, record, schemas_dir):
            findings.append({"contract": contract, "kind": "SCHEMA", "detail": f})
        for f in semantic_invariants(contract, record):
            findings.append({"contract": contract, "kind": "SEMANTIC", "detail": f})
    # TT-S4EXT-002: `pipd validate --bundle` used to stop at the per-record schema/semantic checks,
    # so a bad endpoint hash, an orphan edge or a missing endpoint could still return PASS even
    # though pipeline.trace_closure() already knew how to refuse it. The closure is now part of the
    # bundle verdict, and a bundle with no trace edge is labelled SCHEMA_ONLY rather than passed off
    # as trace-closed.
    closure = closure_findings(bundle)
    findings.extend(closure["findings"])
    return {"verdict": "PASS" if not findings else "FAIL",
            "checked": len(bundle), "closure": closure["state"], "findings": findings}
