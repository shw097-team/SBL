"""Deterministic PI -> PD -> ConstructionContract -> ECP/TQAEP pipeline.

Every artifact conforms EXACTLY to its S0 canonical schema (blueprint 7.3) and carries
ArtifactIdentity so the same input lock reproduces the same ids (G-S4-REPLAY).
No LLM is consulted on this path (5.9.1 responsibility split).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import (AuthorityUnknown, EffectUnknown, IntakeInvalid, PiSemanticFail,
                     RepoContextMissing, StaleProvider, TqOracleFail, TqSodFail, TqTraceFail)  # noqa: F401
from .profiles import compute_profile
from . import repo_context as repo_probe
from . import requirements as req_compile
from .util import canonical_json, content_id, sha256_text  # noqa: F401
# CE-2: the field lists are defined ONCE in validate and referenced here, so the hash body and
# the "stripped before validation" contract cannot diverge from the validator again.
#   HASH_EXCLUDED_FIELDS - the fields `_seal` does not hash (identity + derived `trace` + sidecar).
#   NON_RECORD_SIDECARS  - re-exported (validate defines it); the fields the schema check strips.
from .validate import HASH_EXCLUDED_FIELDS, NON_RECORD_SIDECARS  # noqa: F401

CLAIM_LADDER = ["PROMPT_COMPILE_PASS", "HGK_ADMITTED", "RUNTIME_READY", "LOCAL_QUALIFIED",
                "INDEPENDENT_PASS", "PUBLICATION_APPROVED", "RELEASED", "PRODUCTION_VERIFIED"]

# WO-S4-TQAEP-004: design-time TQAEP is a DESIGN ceiling, not independent acceptance. A checker
# *receipt string* supplied at design time is recorded, but it is NOT independent verification --
# that requires a live S5 runtime checker. The record's key set must stay schema-conformant
# (schemas/TQAEP.schema.json declares additionalProperties:false), so this ceiling and the
# not-granted flags are carried INSIDE the declared `acceptance` field, never as a new top-level
# key and never by editing the schema.
TQAEP_DESIGN_CEILING = "TQAEP_DESIGNED"
TQAEP_INDEPENDENT_PROOF_REQUIRES = "S5_LIVE_RUNTIME_CHECKER"


def _rec(kind: str, prefix: str, payload: Any, **fields: Any) -> dict[str, Any]:
    """Build a schema-conformant record whose identity is derived from its own body.

    The hash covers every declared field (not just the caller's `payload`), so a body edited
    without re-issuing identity is detectable by validate.semantic_invariants.
    """
    digest = sha256_text(canonical_json(fields))
    rec = {"subject_id": f"{prefix}-{digest[:16]}",
           "version": "1",
           "content_hash": digest,
           "schema_version": f"{kind}@1"}
    rec.update(fields)
    return rec


# ---------------------------------------------------------------- authority
def freeze_authority(manifest: dict[str, Any]) -> dict[str, Any]:
    families = manifest.get("families") if "families" in manifest else manifest
    if not families:
        raise AuthorityUnknown("no source families in manifest")
    bindings = []
    for fam, spec in sorted(families.items()):
        if not isinstance(spec, dict) or "manifest_sha256" not in spec:
            raise AuthorityUnknown(f"family {fam} lacks a manifest digest")
        if not spec.get("files"):
            raise AuthorityUnknown(f"family {fam} is empty")
        loc = spec["files"][0]["rel"]
        if not (Path(spec.get("root", "")) / loc).exists() and not Path(loc).exists():
            raise AuthorityUnknown(f"authority locator does not resolve on disk: {loc}")
        digest = spec["manifest_sha256"]
        if not re.match(r"^[0-9a-f]{64}$", str(digest)):
            raise AuthorityUnknown(f"family {fam} manifest digest is not a sha256: {digest!r}")
        rank = "R1" if fam.startswith(("F1", "F2", "F3", "F5", "F6")) else "R2"
        bindings.append(_rec("AuthorityBinding", "AUTH",
                             {"fam": fam, "digest": spec["manifest_sha256"]},
                             source_id=fam, authority_rank=rank,
                             locator=spec["files"][0]["rel"], supersession="CURRENT",
                             conflict_state="NONE"))
    payload = {"families": sorted(families), "digests": [b["content_hash"] for b in bindings]}
    freeze = _rec("SourceFreezeManifest", "SFM", payload,
                  families=len(bindings), bindings=bindings)
    return {"freeze": freeze, "bindings": bindings}


# ---------------------------------------------------------------- intake
def intake(goal: str, *, sources: list[str] | None = None,
           constraints: list[str] | None = None, non_goals: list[str] | None = None) -> dict[str, Any]:
    """Intake compiles clause-bound atomic requirements (R-AUD-005).

    The old five-keyword axis route is NO LONGER an authoritative path: atoms come from source
    clauses via req_compile.compile_requirements, so compound / negated / no-keyword requirements
    survive as distinct atoms instead of collapsing into keyword buckets.
    """
    if not goal or not goal.strip():
        raise IntakeInvalid("empty goal")
    sources = list(sources or [])
    if not sources:
        raise AuthorityUnknown("intake requires at least one source locator")
    for s in sources:
        if not Path(s).exists():
            raise AuthorityUnknown(f"source locator does not exist: {s}")
    payload = {"goal": goal.strip(), "sources": sources,
               "constraints": list(constraints or []), "non_goals": list(non_goals or [])}
    card = dict(payload)
    card["subject_id"] = content_id("INTENT", payload)
    card["content_hash"] = sha256_text(canonical_json(payload))
    card["schema_version"] = "IntentCard@1"
    card["atoms"] = req_compile.compile_requirements(goal.strip(), sources)
    return card


# ---------------------------------------------------------------- profile binding
def profile_record(profile_name: str, axes: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (ProfileBinding record, full profile computation); the record is schema-exact.

    D2: the record's ``axes`` is the NORMALISED list ``compute_profile`` returns - not a
    ``sorted(set(axes))`` re-derivation - so the escalation basis (the axis count the veto
    ran on) and the emitted record cannot disagree.

    D3: ``ProfileBinding.schema.json`` does NOT declare ``risk_assessment`` (adding it would
    break the published record contract), so the honest ``NOT_ASSESSED`` marker rides in the
    existing non-record ``_profile_meta`` sidecar instead of the record.
    """
    full = compute_profile(profile_name, axes=axes)
    bound_axes = list(full["axes"])
    rec = _rec("ProfileBinding", "PB", {"p": full["profile"], "a": bound_axes},
               profile=full["profile"], axes=bound_axes,
               vetoes=full["vetoes"], artifact_depth=full["artifact_depth"],
               assurance=full["assurance"])
    return rec, full


# ---------------------------------------------------------------- PI
def compile_pi(card: dict[str, Any], profile_name: str = "LITE") -> dict[str, Any]:
    """Compile the clause-bound atoms of an IntentCard into a PI package.

    The card's `atoms` field is a CLAIM, not an authority: the atom set is re-derived from the
    card's source clauses. A clause-bound claim must match the re-derivation exactly (tamper /
    collapse detection, refused otherwise); a legacy five-axis keyword claim is ignored outright -
    that shape is no longer an authoritative route into a RequirementAtom record.
    """
    compiled = req_compile.compile_requirements(str(card.get("goal") or "").strip(),
                                                list(card.get("sources") or []))
    claimed = list(card.get("atoms") or [])
    if claimed:
        try:
            req_compile.validate_atoms(claimed)
        except PiSemanticFail:
            claimed = []  # legacy keyword shape: an unverified claim, never an authority
        if claimed and claimed != compiled:
            raise PiSemanticFail("semantic collapse: claimed atoms diverge from their source clauses")
    src_atoms = compiled
    axes = sorted({a.get("axis") or "intent" for a in src_atoms})
    pb, profile_meta = profile_record(profile_name, axes)
    atoms = []
    for a in src_atoms:
        atoms.append(_rec("RequirementAtom", "ATOM",
                          {"req": a["req_id"], "goal": card["content_hash"]},
                          req_id=a["req_id"],
                          source_clause=req_compile.normalized_locator(a["source_clause"]),
                          owner=a.get("owner", "PIPD-EC"),
                          acceptance_cue=a["acceptance_cue"],
                          risk_guard=a["risk_guard"]))
    if not atoms:
        raise PiSemanticFail("PI compiled zero atoms")
    payload = {"intent": card["subject_id"], "atoms": [a["req_id"] for a in atoms],
               "profile": pb["profile"]}
    pi = _rec("PI-PKG", "PI", payload)
    pi["stable_semantic_contract"] = {"contract": "stable", "profile_binding": pb,
                                      "atoms": atoms, "goal": card["goal"],
                                      # normalized source table: one entry per source clause, so no
                                      # atom has to embed a full copy of its clause (payload economy)
                                      "sources": req_compile.source_table(src_atoms)}
    pi["acceptance"] = {"mode": "bound", "oracle_source": "DOC-03 DOMAIN_ORACLES"}
    _seal(pi, "PI")
    pi["trace"] = [_rec("TraceLink", "TL", {"f": pi["subject_id"], "t": a["subject_id"]},
                        from_type="PI-PKG", from_id=pi["subject_id"], from_hash=pi["content_hash"],
                        to_type="RequirementAtom", to_id=a["subject_id"],
                        to_hash=a["content_hash"],
                        rationale="PI derives this atom from the frozen intent")
                   for a in atoms]
    pi["_profile_meta"] = profile_meta  # non-record sidecar, stripped before validation
    return pi


def _seal(rec: dict[str, Any], prefix: str) -> dict[str, Any]:
    """Recompute identity over the FINAL body.

    Builders that add declared fields after _rec() must seal at the end, otherwise the hash does
    not cover the body and validate.semantic_invariants correctly rejects the record.
    """
    # `trace` is a derived relation, not body content: it carries the parent hash, so it cannot be
    # inside the hash it references. The validator excludes exactly the same key set
    # (validate.HASH_EXCLUDED_FIELDS) - one definition, referenced in both places.
    body = {k: v for k, v in rec.items() if k not in HASH_EXCLUDED_FIELDS}
    digest = sha256_text(canonical_json(body))
    rec["subject_id"] = f"{prefix}-{digest[:16]}"
    rec["content_hash"] = digest
    return rec


def atoms_of(pi: dict[str, Any]) -> list[dict[str, Any]]:
    return pi["stable_semantic_contract"]["atoms"]


def strip_sidecar(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if not k.startswith("_")}


# ---------------------------------------------------------------- PD
def bind_pd(pi: dict[str, Any], repo_context: dict[str, Any] | None) -> dict[str, Any]:
    """Late-bind PD against a REAL repository context (R-AUD-009).

    head / branch / dirty / tracked_files / manifest / currentness are DERIVED from the host by
    git/filesystem probes at bind time. Caller-supplied values are unverified claims: recorded,
    never trusted. A stale or spoofed freshness claim is REFUSED (StaleProvider); a missing
    RepoContext is REFUSED (RepoContextMissing) so no PREDEV_READY is ever emitted without one.
    """
    if not repo_context:
        raise RepoContextMissing("PD late-binding requires a RepoContext (no PREDEV_READY without one)")
    if not str(repo_context.get("root") or "").strip():
        raise RepoContextMissing("RepoContext has no root to probe (no PREDEV_READY without one)")
    root = Path(repo_context["root"])
    if not root.exists():
        raise RepoContextMissing(f"RepoContext root missing: {root}")
    derived = repo_probe.derive_repo_context(root)
    claims, evidence = repo_probe.claims_of(repo_context)
    verified = repo_probe.verify_freshness_claims(claims, derived, evidence)
    scope_check = repo_probe.resolve_writable_scope(
        repo_context.get("writable_scope") or "src/**")
    caller_claims = {k: {"value": v, "verified": bool(verified.get(k)),
                         "matches_host": v == derived.get(k)}
                     for k, v in claims.items()}
    ctx = {"root": derived["root"], "probe": derived["probe"],
           "degraded": derived["degraded"], "degraded_reason": derived["degraded_reason"],
           "head": derived["head"], "branch": derived["branch"],
           "dirty": derived["dirty"], "dirty_tracked": derived["dirty_tracked"],
           "tracked_files": derived["tracked_files"],
           "manifest_sha256": derived["manifest_sha256"],
           "currentness_epoch": derived["currentness_epoch"],
           "readiness": "PREDEV_READY",
           "caller_claims": caller_claims}
    payload = {"pi": pi["subject_id"], "repo": ctx}
    pd = _rec("PD-PKG", "PD", payload)
    pd["RepoContext"] = ctx
    pd["currentness"] = {"state": "FRESH", "epoch": derived["currentness_epoch"],
                         "derived_from": f"{derived['probe']}-probes at bind time",
                         "claims_verified": sorted(verified)}
    pd["late_bound_construction_binding"] = {
        "bound_at": "PD", "binding_scope": "affected_only",
        "writable_scope": repo_context.get("writable_scope") or "src/**",
        "writable_scope_check": scope_check}
    return _seal(pd, "PD")


# ---------------------------------------------------------------- ECP / TQAEP
def compile_construction_contract(pd: dict[str, Any]) -> dict[str, Any]:
    scope = pd["late_bound_construction_binding"]["writable_scope"]
    if not scope:
        raise EffectUnknown("ConstructionContract requires an explicit writable scope")
    payload = {"pd": pd["subject_id"], "scope": scope}
    return _seal(_rec("ConstructionContract", "CC", payload,
                subject=pd["subject_id"], writable_scope=[scope],
                expected_changes=["bounded edits inside writable scope"],
                tests=["tests/test_s1_lite_slice.py"],
                rollback="git revert to baseline commit",
                evidence_expectations=["EVD-POS", "EVD-NEG"]), "CC")


def compile_ecp(pd: dict[str, Any], pi: dict[str, Any]) -> dict[str, Any]:
    scope = pd["late_bound_construction_binding"]["writable_scope"]
    if not scope:
        raise EffectUnknown("ECP requires an explicit writable scope")
    payload = {"pd": pd["subject_id"], "scope": scope, "pi": pi["subject_id"]}
    return _seal(_rec("ECP", "ECP", payload,
                effect_intent="apply bounded edits inside the writable scope",
                permission={"scope": scope, "token_required": True},
                retries={"max": 1, "backoff": "none"},
                idempotency={"key": content_id("IDEM", payload), "guarantee": "at_most_once"},
                readback={"required": True, "kind": "residue_scan"},
                rollback={"pointer": "baseline_commit", "required": True}), "ECP")


def compile_effect_ecp(pd: dict[str, Any], pi: dict[str, Any], intent: dict[str, Any],
                       operation_registry: dict[str, Any]) -> dict[str, Any]:
    """PRE-V2 additive projection through the ORIGINAL ECP writer.

    Modified 2026-11-02: author intent remains unadmitted; canonical $id/fields
    and the legacy compile_ecp entry point are unchanged. Registry authority is
    explicitly unverified; this cannot create a Grant or executable readiness.
    """
    from .pre_v2_adapter import ecp_intent, Refusal
    try:
        from . import validate as original_validate
        if original_validate.validate_bundle({'PI-PKG':pi,'PD-PKG':pd}).get('verdict')!='PASS':
            raise Refusal('ECP_CANONICAL_INPUT_INVALID')
        source_atoms=req_compile.compile_requirements(pi['stable_semantic_contract'].get('goal',''),
            list(dict.fromkeys(x['source_clause']['file'] for x in atoms_of(pi))))
        derived={x['req_id']:x for x in source_atoms}
        given={x['req_id']:x for x in atoms_of(pi)}
        if set(derived)!=set(given) or any(given[k]['risk_guard']!=derived[k]['risk_guard'] or
            given[k]['source_clause']!=req_compile.normalized_locator(derived[k]['source_clause']) for k in given):
            raise Refusal('ECP_PI_SOURCE_REPLAY')
        context={k:intent[k] for k in ('subject_id','candidate_sha256','scope','host','policy_epoch')}
        if context['subject_id'] != pi.get('subject_id'):
            raise Refusal('ECP_PI_SUBJECT')
        checked=ecp_intent(context,intent['operation']['operation_type'],operation_registry,intent['details'])
        if checked != intent:
            raise Refusal('ECP_INTENT_REPLAY_MISMATCH')
        if not pd.get('RepoContext') or not pd.get('late_bound_construction_binding'):
            raise Refusal('ECP_PD_UNBOUND')
        effect=intent['operation']['effect_class']; details=intent['details']
        if effect=='REPOSITORY_WRITE':
            permitted=pd['late_bound_construction_binding']['writable_scope']
            if not repo_probe.writable_scope_subset_check(context['scope'],[permitted])['subset']:
                raise Refusal('ECP_PD_SCOPE_MISMATCH')
            observed=repo_probe.probe_repository(pd['RepoContext']['root'])
            if observed['probe']!='git' or observed['head']!=pd['RepoContext'].get('head') or observed['currentness_epoch']!=pd.get('currentness',{}).get('epoch'):
                raise Refusal('ECP_PD_STALE_OR_FAKE_HEAD')
        token_required=effect not in ('SOURCE_READ','LOCAL_DRAFT_WRITE')
        # This candidate's canonical record carries design intent only. Exact
        # authority/permission still belongs to the original effect receiver.
        return _seal(_rec('ECP','ECP',{},
            effect_intent={'operation_type':intent['operation']['operation_type'],'effect_class':effect,
                           'pi':pi['subject_id'],'pd':pd['subject_id'],'intent':intent,
                           'state':'EFFECT_UNBOUND','claim_ceiling':'AUTHOR_DESIGN_ONLY'},
            permission={'scope':context['scope'],'basis':details['permission_basis'],
                        'token_required':token_required,'grant_state':'NOT_GRANTED'},
            retries={'policy':intent['retry_policy'],'on_unknown':details['on_unknown'],
                     'reconcile_reader':details['reconcile_reader']},
            idempotency={'key':details['idempotency_key'],'guarantee':'DESIGN_ONLY'},
            readback={'required':True,'kind':details['readback_kind'],'expected':details['expected_postcondition']},
            rollback={'required':token_required,'recovery':{k:details[k] for k in
                ('cleanup','rollback_commit','host_recovery','compensation','recovery') if k in details},
                      'state':'RECOVERY_DESIGN_ONLY'}),'ECP')
    except (Refusal,KeyError,TypeError,ValueError) as exc:
        raise EffectUnknown(str(exc)) from exc


def read_planned_tqaep(pi: dict[str, Any], pd: dict[str, Any], ecp: dict[str, Any],
                      plan: dict[str, Any], fixture_root: Path) -> dict[str, Any]:
    """PRE-V2 receipt-free author Sidecar Reader; never canonical TQAEP@1.

    No live acceptance field is relaxed. This reads a versioned plan whose
    writer is the author adapter, binding original atom/oracle identities and
    the canonical candidate. It does not ratify the original Case registry.
    """
    from .pre_v2_adapter import deny_authority, encoded, sha, read, Refusal, validate_design
    try:
        deny_authority(plan)
        validate_design('PlannedTQAEP.schema.json',plan)
        if plan.get('schema')!='SBL.PlannedTQAEP@2' or plan.get('claim_ceiling')!='AUTHOR_DESIGN_ONLY':
            raise Refusal('PLANNED_SCHEMA_OR_CLAIM')
        bundle={'PI-PKG':pi,'PD-PKG':pd,'ECP':ecp}
        from . import validate as original_validate
        if original_validate.validate_bundle(bundle).get('verdict')!='PASS':
            raise Refusal('PLANNED_CANONICAL_INPUT_INVALID')
        if plan.get('subject_id')!=pi.get('subject_id') or plan.get('candidate_sha256')!=sha(encoded(bundle)):
            raise Refusal('PLANNED_CANONICAL_CANDIDATE')
        if plan.get('canonical_pi_sha256')!=sha(encoded(pi)):
            raise Refusal('PLANNED_PI_SHA')
        allowed=pd['late_bound_construction_binding']['writable_scope']
        scope=plan.get('scope',[])
        # Source-only plans bind a source locator; write plans must remain
        # inside the original admitted PD scope. No path determines the effect.
        effect=ecp.get('effect_intent',{})
        if isinstance(effect,dict) and effect.get('effect_class')=='REPOSITORY_WRITE':
            if not repo_probe.writable_scope_subset_check(scope,[allowed])['subset']:
                raise Refusal('PLANNED_PD_SCOPE')
        atoms={x['req_id']:x for x in atoms_of(pi)}; cases=plan.get('cases')
        contract=pi['stable_semantic_contract']
        original=req_compile.compile_requirements(contract.get('goal',''),list(dict.fromkeys(
            x['source_clause']['file'] for x in atoms.values())))
        originals={x['req_id']:x for x in original}
        if set(originals)!=set(atoms) or any(atoms[k]['risk_guard']!=originals[k]['risk_guard'] or
                atoms[k]['source_clause']!=req_compile.normalized_locator(originals[k]['source_clause']) for k in atoms):
            raise Refusal('PLANNED_PI_SOURCE_REPLAY')
        if not atoms or not isinstance(cases,list) or not cases:
            raise Refusal('PLANNED_EMPTY')
        seen=set(); reqs=set(); fuos=set()
        for case in cases:
            rid=case.get('original_requirement_id'); atom=atoms.get(rid)
            if not atom or case.get('original_oracle_id')!=atom.get('risk_guard',{}).get('oracle',{}).get('id'):
                raise Refusal('PLANNED_ORACLE_OR_REQUIREMENT')
            source=req_compile.resolve_source_clause(atom,pi['stable_semantic_contract']['sources'])
            if case.get('source_sha256')!=source.get('source_sha256') or case.get('clause_id')!=source.get('clause_id'):
                raise Refusal('PLANNED_SOURCE_CLAUSE')
            if not all(case.get(k) for k in ('case_id','fuo_id','positive_fixture','negative_fixture','raw_schema',
                'positive_fixture_sha256','negative_fixture_sha256','raw_schema_sha256','expected_world_raw',
                'evidence_expectation','checker_role','requalify_selector','runner_owner')):
                raise Refusal('PLANNED_CASE_FIELDS')
            if case['case_id'] in seen or case.get('runner_binding')!='RUNNER_UNBOUND':
                raise Refusal('PLANNED_DUPLICATE_OR_RUNNER_CLAIM')
            if case.get('applicability',{}).get('host')!=plan.get('host'):
                raise Refusal('PLANNED_HOST_MISMATCH')
            for key in ('positive_fixture','negative_fixture','raw_schema'):
                if sha(read(fixture_root,case[key]))!=case[key+'_sha256']:
                    raise Refusal('PLANNED_FIXTURE_DRIFT')
            seen.add(case['case_id']); reqs.add(rid); fuos.add(case['fuo_id'])
        if reqs!=set(atoms) or fuos!=set(plan.get('required_fuo',[])):
            raise Refusal('PLANNED_COVERAGE')
        if plan.get('live_acceptance')!='NOT_RUN' or plan.get('independent_acceptance')!='NOT_GRANTED':
            raise Refusal('PLANNED_LIVE_CLAIM')
        return plan
    except (Refusal,KeyError,TypeError,ValueError,OSError) as exc:
        raise TqTraceFail(str(exc)) from exc


def compile_tqaep(pi: dict[str, Any], ecp: dict[str, Any], *, maker: str, checker: str,
                  checker_execution_receipt: str = "") -> dict[str, Any]:
    # C-3 repair: reject aliasing tricks, not just exact string equality.
    if maker.strip().lower() == checker.strip().lower():
        raise TqSodFail("maker must not be the independent checker (case/whitespace-insensitive)")
    if not checker_execution_receipt or checker_execution_receipt.upper() == "SELF_ATTESTED":
        raise TqSodFail("an independent checker must supply a checker_execution_receipt; a maker "
                        "cannot self-attest independence")
    if not pi.get("trace"):
        raise TqTraceFail("TQAEP requires trace links")
    tests, oracles, fixtures = [], [], []
    for atom in atoms_of(pi):
        tests.append({"test_id": f"TEST-{atom['req_id']}", "requirement": atom["req_id"],
                      "oracle": "deterministic assertion on the bound artifact",
                      "positive_fixture": f"fixtures/{atom['req_id']}/positive",
                      "negative_fixture": f"fixtures/{atom['req_id']}/negative",
                      "evidence_expectation": "EVD-" + atom["req_id"]})
        oracles.append(f"TEST-{atom['req_id']}: deterministic assertion on the bound artifact")
        fixtures.append(f"fixtures/{atom['req_id']}/positive")
    if any(not t["oracle"] for t in tests):
        raise TqOracleFail("every TQAEP test needs an oracle")
    payload = {"pi": pi["subject_id"], "ecp": ecp["subject_id"],
               "tests": [t["test_id"] for t in tests]}
    # WO-S4-TQAEP-004: a design-time record establishes ONLY that a distinct checker identity was
    # supplied and recorded. A receipt string is not independent verification, so the entry must
    # NOT present it as an independently passed case; the design-time ceiling and the explicit
    # NOT_GRANTED flags say exactly what was established and what a live checker would have to do.
    acceptance = [{"case": "TQAEP_DESIGN_CANDIDATE",
                   "design_time_status": "DISTINCT_CHECKER_IDENTITY_RECORDED",
                   "maker_identity": maker, "checker_identity": checker, "distinct": True,
                   "checker_execution_receipt": checker_execution_receipt,
                   "claim_ceiling": TQAEP_DESIGN_CEILING,
                   "independent_acceptance": "NOT_GRANTED",
                   "independent_proof_requires": TQAEP_INDEPENDENT_PROOF_REQUIRES,
                   "note": "design-time candidate only: the checker receipt is a recorded string, "
                           "not independent verification; a live runtime checker must re-run it "
                           "before any independent acceptance can be claimed"}]
    return _seal(_rec("TQAEP", "TQAEP", payload,
                tests=tests, oracles=oracles, fixtures=fixtures,
                acceptance=acceptance, requalification="affected-only"), "TQAEP")


# ---------------------------------------------------------------- evidence / claim
def evidence_expectations(tqaep: dict[str, Any], producer: str) -> list[dict[str, Any]]:
    out = []
    for t in tqaep["tests"]:
        out.append(_rec("EvidenceExpectation", "EE", t,
                        expected_evidence_type="RAW_RECEIPT", producer=producer,
                        postcondition=f"{t['test_id']} returned its oracle verdict",
                        freshness="same_candidate_hash", claim_effect="LOCAL"))
    return out


def claim_ceiling(allowed: list[str]) -> dict[str, Any]:
    for c in allowed:
        if c not in CLAIM_LADDER:
            raise PiSemanticFail(f"unknown claim {c}")
    idx = max(CLAIM_LADDER.index(c) for c in allowed)
    payload = {"allowed": sorted(allowed), "idx": idx}
    return _rec("ClaimCeiling", "CCL", payload,
                allowed_claims=sorted(allowed),
                forbidden_escalation=CLAIM_LADDER[idx + 1:],
                close_conditions=["raw receipt bound to candidate hash",
                                  "independent checker verdict"])


# ---------------------------------------------------------------- trace closure
def trace_closure(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    edges = []
    known: set[str] = set()
    for name, arte in artifacts.items():
        if "subject_id" in arte:
            known.add(arte["subject_id"])
        for atom in (arte.get("stable_semantic_contract", {}) or {}).get("atoms", []) or []:
            known.add(atom["subject_id"])
        for tl in arte.get("trace", []) or []:
            edges.append((name, tl["to_id"]))
    orphans = sorted(t for _, t in edges if t not in known)
    # C-10 repair: a fabricated endpoint hash used to sail through. Recompute both sides.
    by_id = {}
    for name, arte in artifacts.items():
        if "subject_id" in arte:
            by_id[arte["subject_id"]] = arte.get("content_hash", "")
        for atom in (arte.get("stable_semantic_contract", {}) or {}).get("atoms", []) or []:
            by_id[atom["subject_id"]] = atom.get("content_hash", "")
    bad_hash = []
    for name, arte in artifacts.items():
        for tl in arte.get("trace", []) or []:
            for side in ("from", "to"):
                got = str(tl.get(f"{side}_hash") or "")
                want = by_id.get(tl.get(f"{side}_id"))
                if want is None:
                    bad_hash.append(f"{tl.get(f'{side}_id')}: endpoint not present in the bundle")
                elif got != want:
                    bad_hash.append(f"{tl.get(f'{side}_id')}: {side}_hash mismatch "
                                    f"(recorded {got[:12]} real {want[:12]})")
    payload = {"artifacts": sorted(artifacts), "edges": len(edges)}
    return _rec("TraceClosureReport", "TRC", payload,
                edges=len(edges), orphans=orphans, bad_hashes=bad_hash,
                verdict="PASS" if (not orphans and edges and not bad_hash) else "FAIL")
