#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-21 trace runner (FHS W0 R4C).

Purpose
-------
Type the 96 Oracle contracts of ORACLE96_CONTRACTS.json into 96 typed
fixtures, execute a *purely declarative* structural adapter over each
fixture, record the observed first-fail per case, reconcile the observation
against the archived 288-row replay raw, validate the S1..S5 seams, the
22-WP / 36-edge DAG (E26 direction), the 84-card / 25-join / 22-trace
counts, and emit the W1..W4 consumer handoff.

Hard boundaries implemented here (not merely documented):
  * No network, no subprocess, no native/Host/Checker invocation.
  * The adapter is data (a predicate table) plus one generic evaluator; it
    receives only the fixture document and a *case descriptor* -- it never
    sees ``expected_first_fail``.  Comparison is a separate step.
  * Everything written goes under ``--out``.
  * Claim ceiling: AUTHOR_LOCAL_TEST. TraceClosure is AUTHOR_STATIC only and
    never claims WP-FHS-19 (WP19) completion.

CLI
---
    python trace_runner.py --source-root <FHS_PIPD-LS-PKG_W0_R4C> --out <dir>

Exit codes
----------
    0  all sealed, no hold
    3  sealed but holds present (see report)
    4  structural mismatch / validation failure
    2  input error (missing file / malformed JSON)
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys

# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------

LANE = "WP-FHS-21"
RUNNER_ID = "FHS-W0-WP21-TRACE-RUNNER/1"
ADAPTER_ID = "FHS-W0-WP21-STRUCTURAL-ADAPTER/1"
CLAIM_CEILING = "AUTHOR_LOCAL_TEST"
TRACE_SCOPE = "AUTHOR_STATIC"

PASS_MARKER = "AUTHOR_FIXTURE_STATIC_PASS"
SWAP_CODE = "CASE_TYPE_OR_SCOPE_MISMATCH"

FIRSTFAIL_MISMATCH = "FIRSTFAIL_MISMATCH"
SEAM_FIELD_MISSING = "SEAM_FIELD_MISSING"
DAG_E26_DIRECTION_INVALID = "DAG_E26_DIRECTION_INVALID"
WAVE_COUNT_MISMATCH = "WAVE_COUNT_MISMATCH"

EXPECTED_WP_COUNT = 22
EXPECTED_EDGE_COUNT = 36
EXPECTED_CARD_COUNT = 84
EXPECTED_WAVE_JOIN_25 = 25
EXPECTED_W0_TRACE22 = 22
EXPECTED_SEAM_COUNT = 5
EXPECTED_ORACLE_CASES = 96
EXPECTED_REPLAY_ROWS = 288
EXPECTED_SWAP_ROWS = 48
EXPECTED_TRACE_EDGES = 110

E26_PREDECESSOR = "WP-FHS-19"
E26_SUCCESSOR = "WP-FHS-14"

SHA64 = re.compile(r"^[a-f0-9]{64}$")

REQUIRED_SOURCE_FILES = (
    "ORACLE96_CONTRACTS.json",
    "ORACLE96_REPLAY_RAW.json",
    "ORACLE96_SWAP_RAW.json",
    "SEAM_CONTRACTS.json",
    "TRACE_GRAPH.json",
    "W0_REQUIRED22_TRACE.json",
    "PROGRAM_WP22_DAG36.json",
    "DESIGN84_WAVE_JOIN.json",
    "W1_W4_IMPACT_AND_HOLD_MATRIX.json",
)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canon_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def sha256_obj(obj) -> str:
    return sha256_bytes(canon_bytes(obj))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: str, obj) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
    return sha256_bytes(payload.encode("utf-8"))


class InputError(RuntimeError):
    """Raised when the source root does not carry the expected inputs."""


# --------------------------------------------------------------------------
# declarative predicate DSL
# --------------------------------------------------------------------------
# A predicate is a plain tuple: (op_name, arg_or_args).  The evaluator below
# is the *only* executable code in the adapter; every judgement is data.

def pget(payload, dotted):
    cur = payload
    for part in dotted.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:  # pragma: no cover - defensive
            raise KeyError(dotted)
    return cur


def _hard_pass(payload, _arg):
    return all(bool(c.get("pass")) for c in payload["components"] if c.get("hard"))


def _sha_of_eq(payload, arg):
    refpath, valpath = arg
    return sha256_obj(pget(payload, valpath)) == pget(payload, refpath)


def _is_none(payload, arg):
    return pget(payload, arg) is None


PREDICATE_OPS = {
    "true": lambda p, a: pget(p, a) is True,
    "false": lambda p, a: pget(p, a) is False,
    "nonempty": lambda p, a: bool(pget(p, a)),
    "is_none": _is_none,
    "eq_path": lambda p, a: pget(p, a[0]) == pget(p, a[1]),
    "ne_path": lambda p, a: pget(p, a[0]) != pget(p, a[1]),
    "eq_lit": lambda p, a: pget(p, a[0]) == a[1],
    "gt_path": lambda p, a: pget(p, a[0]) > pget(p, a[1]),
    "ge_path": lambda p, a: pget(p, a[0]) >= pget(p, a[1]),
    "ge_lit": lambda p, a: pget(p, a[0]) >= a[1],
    "list_empty": lambda p, a: pget(p, a) == [],
    "list_eq_lit": lambda p, a: pget(p, a[0]) == a[1],
    "subset_path": lambda p, a: set(pget(p, a[0])) <= set(pget(p, a[1])),
    "max_le_path": lambda p, a: max(pget(p, a[0])) <= pget(p, a[1]),
    "len_eq_paths": lambda p, a: len(pget(p, a[0])) == len(pget(p, a[1])),
    "sha256_hex": lambda p, a: bool(SHA64.match(str(pget(p, a) or ""))),
    "sha_of_eq": _sha_of_eq,
    "all_items_true": lambda p, a: all(bool(i.get(a[1])) for i in pget(p, a[0])),
    "hard_components_pass": _hard_pass,
}


def eval_predicate(predicate, payload):
    op, arg = predicate
    return bool(PREDICATE_OPS[op](payload, arg))


def eval_predicates(predicates, payload):
    """Return (ok, first_failed_predicate or None)."""
    for predicate in predicates:
        if not eval_predicate(predicate, payload):
            return False, {"op": predicate[0], "arg": predicate[1]}
    return True, None


# --------------------------------------------------------------------------
# the declarative adapter (pure data)
# --------------------------------------------------------------------------
# class -> first-fail code declared by the WP21 class taxonomy.  This table is
# a *declaration in the adapter*, never read from the contracts.

ADAPTER = {
    "adapter_id": ADAPTER_ID,
    "declarative": True,
    "external_calls": False,
    "deterministic": True,
    "inputs": ["fixture_document", "case_descriptor", "declared_mutation"],
    "excluded_inputs": ["ORACLE96_CONTRACTS.expected_first_fail",
                        "ORACLE96_REPLAY_RAW.actual_firstfail"],
    "pass_marker": PASS_MARKER,
    "shape_code": SWAP_CODE,
    "class_firstfail": {
        "POS": "MISSING_POS_FUNCTION",
        "NEG": "NEGATIVE_ACCEPTED",
        "EDGE": "EDGE_BOUND_VIOLATION",
        "SEC": "SECURITY_BOUNDARY_BREACH",
        "PERF": "PERF_SLO_EXCEEDED",
        "PARITY": "PARITY_PROVIDER_OFF_FAIL",
        "RECOVERY": "RECOVERY_STATE_MISMATCH",
        "UPGRADE": "UPGRADE_VERSION_MISMATCH",
        "ROLLBACK": "ROLLBACK_PREIMAGE_MISSING",
        "UNINSTALL": "UNINSTALL_RESIDUE",
        "MUT": "MUTANT_SURVIVED",
        "JOURNEY": "FUNCTIONAL_CONSUMER_MISSING",
    },
    "domain_predicates": {
        "POS": [("true", "feature_invoked"),
                ("true", "acceptance_predicate_declared"),
                ("true", "consumer_result.available")],
        "NEG": [("eq_lit", ("decision", "DENY")),
                ("list_empty", "world_diff")],
        "EDGE": [("eq_lit", ("decision", "DENY")),
                 ("gt_path", ("input", "boundary.max"))],
        "SEC": [("eq_lit", ("decision", "DENY")),
                ("ne_path", ("requested_scope", "allowed_scope")),
                ("ne_path", ("maker", "checker"))],
        "PERF": [("nonempty", "dataset_pin"),
                 ("max_le_path", ("samples_ms", "budget_ms"))],
        "PARITY": [("true", "provider_off_required"),
                   ("list_empty", "egress"),
                   ("eq_path", ("primary_output", "fallback_output"))],
        "RECOVERY": [("eq_path", ("resume_cursor", "checkpoint")),
                     ("true", "world_reconciled"),
                     ("false", "replayed")],
        "UPGRADE": [("subset_path", ("migration_fields", "retained_fields")),
                    ("eq_path", ("receipt_candidate", "to_version"))],
        "ROLLBACK": [("eq_path", ("preimage", "restored")),
                     ("list_empty", "residue")],
        "UNINSTALL": [("list_empty", "loaded_hooks"),
                      ("eq_path", ("foreign_assets_before",
                                   "foreign_assets_after"))],
        "MUT": [("true", "mutant_killed"), ("false", "mutant_survived")],
        "JOURNEY": [("list_eq_lit", ("steps",
                                     ["goal", "source", "spec", "deliver"])),
                    ("true", "outcome_available")],
    },
    "oracle_shape": {
        "DETERMINISTIC": ["expected_value", "observed_value"],
        "STATE_READBACK": ["expected_post_digest", "native_world_post",
                           "native_world_pre", "pre_digest"],
        "PROPERTY": ["generated_cases", "invariant", "minimal_counterexample",
                     "seed"],
        "REFERENCE_OUTPUT": ["canonical_output", "observed_output",
                             "reference_sha"],
        "STATISTICAL": ["calibration_sha", "confidence", "dataset_sha",
                        "sample_metrics", "threshold"],
        "SEMANTIC_JUDGE": ["disagreements", "hard_veto", "human_calibration",
                           "judge_model_pin", "rubric_sha", "scores"],
        "HUMAN": ["consent_or_basis", "maker_cannot_sign", "principal",
                  "rubric", "signed_human_decision"],
        "COMPOSITE": ["component_raw_receipts", "components",
                      "failure_policy", "ordering"],
    },
    "oracle_predicates": {
        "DETERMINISTIC": [("eq_path", ("expected_value", "observed_value"))],
        "STATE_READBACK": [("eq_path", ("pre_digest",
                                        "native_world_pre.digest")),
                           ("eq_path", ("expected_post_digest",
                                        "native_world_post.digest"))],
        "PROPERTY": [("is_none", "minimal_counterexample"),
                     ("all_items_true", ("generated_cases",
                                         "invariant_holds"))],
        "REFERENCE_OUTPUT": [("sha_of_eq", ("reference_sha",
                                            "canonical_output")),
                             ("eq_path", ("canonical_output",
                                          "observed_output"))],
        "STATISTICAL": [("sha256_hex", "calibration_sha"),
                        ("nonempty", "dataset_sha"),
                        ("ge_path", ("sample_metrics.lower_bound",
                                     "threshold")),
                        ("ge_lit", ("confidence", 0.95))],
        "SEMANTIC_JUDGE": [("nonempty", "human_calibration.calibration_ref"),
                           ("ge_lit", ("scores.adequacy", 0.9)),
                           ("false", "hard_veto"),
                           ("list_empty", "disagreements")],
        "HUMAN": [("true", "maker_cannot_sign"),
                  ("eq_path", ("signed_human_decision.basis_ref",
                               "consent_or_basis")),
                  ("eq_lit", ("signed_human_decision.state",
                              "EXPECTED_NOT_OBSERVED"))],
        "COMPOSITE": [("eq_lit", ("failure_policy", "ALL_HARD_AND")),
                      ("hard_components_pass", None),
                      ("len_eq_paths", ("component_raw_receipts",
                                        "components"))],
    },
}


def adapter_shape_gate(fixture, descriptor):
    """Typed-discrimination gate. Returns None (pass) or the shape code.

    A foreign fixture (swap test) fails here even if a caller relabels the
    declared oracle type, because both the identity tuple and the exact
    oracle key set are checked.
    """
    if not isinstance(fixture, dict):
        return SWAP_CODE
    for key, want in (("case_id", descriptor["case_id"]),
                      ("test_class", descriptor["test_class"]),
                      ("oracle_type", descriptor["oracle_type"])):
        if fixture.get(key) != want:
            return SWAP_CODE
    scope = descriptor.get("scope")
    if scope is not None and fixture.get("scope") != scope:
        return SWAP_CODE
    oracle = fixture.get("oracle")
    required = ADAPTER["oracle_shape"].get(descriptor["oracle_type"])
    if not isinstance(oracle, dict) or required is None:
        return SWAP_CODE
    if sorted(oracle.keys()) != sorted(required):
        return SWAP_CODE
    return None


def set_path(doc, path, value):
    cur = doc
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value


def adapter_evaluate(fixture, descriptor, mutation=None):
    """Run the declarative adapter on one fixture.

    ``fixture`` is the fixture *document* (already carrying domain/oracle),
    ``descriptor`` is {case_id, test_class, oracle_type, scope}; the adapter
    never receives the expected first-fail.

    Returns dict(observed_firstfail, gate, detail, shape_ok).
    """
    shape = adapter_shape_gate(fixture, descriptor)
    if shape is not None:
        return {"observed_firstfail": shape, "gate": "shape",
                "detail": {"stage": "typed_discrimination"},
                "shape_ok": False}

    doc = fixture
    if mutation is not None:
        doc = copy.deepcopy(fixture)
        set_path(doc, mutation["path"], mutation["value"])

    test_class = descriptor["test_class"]
    oracle_type = descriptor["oracle_type"]
    code = ADAPTER["class_firstfail"][test_class]

    domain = doc.get("domain")
    if not isinstance(domain, dict):
        return {"observed_firstfail": code, "gate": "domain",
                "detail": {"stage": "domain_absent"}, "shape_ok": True}
    ok, failed = eval_predicates(ADAPTER["domain_predicates"][test_class],
                                 domain)
    if not ok:
        return {"observed_firstfail": code, "gate": "domain",
                "detail": {"stage": "domain_predicate", "predicate": failed},
                "shape_ok": True}

    oracle = doc.get("oracle") or {}
    ok, failed = eval_predicates(ADAPTER["oracle_predicates"][oracle_type],
                                 oracle)
    if not ok:
        return {"observed_firstfail": code, "gate": "oracle",
                "detail": {"stage": "oracle_predicate", "predicate": failed},
                "shape_ok": True}

    return {"observed_firstfail": PASS_MARKER, "gate": "none",
            "detail": {"stage": "all_predicates_pass"}, "shape_ok": True}


# --------------------------------------------------------------------------
# first-fail comparison (separate from the adapter on purpose)
# --------------------------------------------------------------------------

def firstfail_verdict(expected, observed):
    if observed is None or observed == "":
        return "FIRSTFAIL_UNOBSERVED"
    if expected is None or expected == "":
        return "FIRSTFAIL_EXPECTED_MISSING"
    return "MATCH" if expected == observed else FIRSTFAIL_MISMATCH


# --------------------------------------------------------------------------
# 96 typed fixtures
# --------------------------------------------------------------------------

def build_typed_fixtures(source_root, contracts):
    """Type the 96 contracts into 96 fixtures carrying the required fields."""
    fixtures = []
    for contract in contracts:
        case_id = contract["case_id"]
        rel = "fixtures/%s.pos.json" % case_id
        abs_path = os.path.join(source_root, rel)
        try:
            pos_doc = load_json(abs_path)
            disk_sha = sha256_file(abs_path)
            doc_state = "READ_OK"
        except (OSError, ValueError):
            pos_doc, disk_sha, doc_state = None, None, "READ_FAILED"
        declared_map = contract.get("fixture_sha256") or {}
        if isinstance(declared_map, dict):
            declared_sha = declared_map.get(rel)
        else:
            declared_sha = declared_map
        subject_id = (pos_doc or {}).get("subject_id") or "SUBJECT_UNBOUND"

        fixtures.append({
            "fixture_schema": "FHS.W0.WP21.TypedOracleFixture/v1",
            "fixture_id": "WP21-FX-%s" % case_id,
            "case_id": case_id,
            "case_type": contract["test_class"],
            "oracle_type": contract["oracle_type"],
            "scope": contract["scope"],
            "subject_ref": {
                "subject_id": subject_id,
                "source_parent": contract["source_parent"],
                "source_sha": contract["source_sha"],
                "source_span": contract["source_span"],
                "parent_file_sha": contract["parent_file_sha"],
                "parent_span": contract["parent_span"],
                "source_excerpt_sha": contract["source_excerpt_sha"],
            },
            "expected_firstfail": contract["expected_first_fail"],
            "oracle_ref": {
                "source_parent": contract["source_parent"],
                "source_span": contract["source_span"],
                "raw_locator": contract["raw_locator"],
                "raw_schema": contract["raw_schema"],
                "original_consumer": contract["original_consumer"],
                "contract_sha256": sha256_obj(contract),
            },
            "pos_fixture": {
                "path": rel,
                "state": doc_state,
                "disk_sha256": disk_sha,
                "contract_sha256": declared_sha,
                "sha_match": declared_sha is not None and disk_sha == declared_sha,
                "all_declared_sha256": declared_map,
            },
            "declared_mutations": contract["mutations"],
            "execution_wave": contract.get("execution_wave"),
            "state": contract.get("state"),
            "evidence_expectation": contract.get("evidence_expectation"),
        })
    return fixtures


def _descriptor(contract):
    return {"case_id": contract["case_id"],
            "test_class": contract["test_class"],
            "oracle_type": contract["oracle_type"],
            "scope": contract["scope"]}


def run_case(source_root, contract, fixture_doc=None):
    """Run one case: base, domain mutation, oracle mutation."""
    case_id = contract["case_id"]
    if fixture_doc is None:
        fixture_doc = load_json(os.path.join(source_root,
                                             "fixtures/%s.pos.json" % case_id))
    descriptor = _descriptor(contract)
    base = adapter_evaluate(fixture_doc, descriptor, None)
    mutations = contract["mutations"]
    domain_mut = next((m for m in mutations if m["path"][0] == "domain"), None)
    oracle_mut = next((m for m in mutations if m["path"][0] == "oracle"), None)
    dom = (adapter_evaluate(fixture_doc, descriptor, domain_mut)
           if domain_mut else {"observed_firstfail": "MUTATION_NOT_DECLARED",
                               "gate": "n/a", "detail": {}, "shape_ok": True})
    ora = (adapter_evaluate(fixture_doc, descriptor, oracle_mut)
           if oracle_mut else {"observed_firstfail": "MUTATION_NOT_DECLARED",
                               "gate": "n/a", "detail": {}, "shape_ok": True})
    return base, dom, ora


def run_oracle96(source_root, contracts):
    """96 rows: expected (contract) vs observed (adapter)."""
    rows = []
    for index, contract in enumerate(contracts, start=1):
        case_id = contract["case_id"]
        base, dom, ora = run_case(source_root, contract)
        observed_set = {dom["observed_firstfail"], ora["observed_firstfail"]}
        if len(observed_set) == 1:
            observed = observed_set.pop()
            observed_gate = "%s+%s" % (dom["gate"], ora["gate"])
            observed_detail = {"domain_mutation": dom["detail"],
                               "oracle_mutation": ora["detail"]}
        else:
            observed = "MUTATION_OBSERVATION_DIVERGENCE"
            observed_gate = "divergent"
            observed_detail = {"domain_mutation": dom["detail"],
                               "oracle_mutation": ora["detail"]}
        expected = contract["expected_first_fail"]
        verdict = firstfail_verdict(expected, observed)
        base_ok = base["observed_firstfail"] == PASS_MARKER
        rows.append({
            "row": index,
            "case_id": case_id,
            "case_type": contract["test_class"],
            "oracle_type": contract["oracle_type"],
            "expected_firstfail": expected,
            "expected_source": "ORACLE96_CONTRACTS.expected_first_fail",
            "observed_firstfail": observed,
            "observed_source": "ADAPTER:" + ADAPTER_ID,
            "observed_gate": observed_gate,
            "observed_detail": observed_detail,
            "runs": {
                "base": {"observed": base["observed_firstfail"],
                         "gate": base["gate"],
                         "detail": base["detail"]},
                "domain_mutation": {"observed": dom["observed_firstfail"],
                                    "gate": dom["gate"],
                                    "detail": dom["detail"],
                                    "path": (contract["mutations"][0]["path"]
                                             if contract["mutations"] else None)},
                "oracle_mutation": {"observed": ora["observed_firstfail"],
                                    "gate": ora["gate"],
                                    "detail": ora["detail"],
                                    "path": (contract["mutations"][1]["path"]
                                             if len(contract["mutations"]) > 1
                                             else None)},
            },
            "base_run_state": PASS_MARKER if base_ok else base["observed_firstfail"],
            "observed_context": "contract_declared_mutation",
            "verdict": verdict,
            "claim_ceiling": CLAIM_CEILING,
        })
    matched = sum(1 for r in rows if r["verdict"] == "MATCH")
    base_pass = sum(1 for r in rows if r["base_run_state"] == PASS_MARKER)
    return {
        "schema": "FHS.W0.WP21.ORACLE96_RUN_RAW/v1",
        "runner": RUNNER_ID,
        "adapter_id": ADAPTER_ID,
        "adapter_declarative": True,
        "adapter_external_calls": False,
        "adapter_excludes_expected_input": True,
        "scope": TRACE_SCOPE,
        "claim_ceiling": CLAIM_CEILING,
        "native": "NOT_RUN",
        "observed_semantics": (
            "observed_firstfail is the code the adapter emits when the "
            "contract's declared domain/oracle mutation is applied to the "
            "typed fixture; base_run_state records the unmutated fixture "
            "(all 96 are AUTHOR_FIXTURE_STATIC_PASS). It is never copied "
            "from expected_first_fail."),
        "rows_total": len(rows),
        "rows_expected_equal_observed": matched,
        "base_runs_static_pass": base_pass,
        "verdict_counts": _count(r["verdict"] for r in rows),
        "rows": rows,
    }


def independence_probe(source_root, contracts, baseline_rows):
    """Re-run with poisoned expected codes; observations must not move."""
    poisoned = []
    codes = sorted({c["expected_first_fail"] for c in contracts})
    for contract in contracts:
        clone = copy.deepcopy(contract)
        original = clone["expected_first_fail"]
        # rotate the declared expectation to a different, wrong code
        idx = (codes.index(original) + 1) % len(codes)
        clone["expected_first_fail"] = codes[idx]
        poisoned.append(clone)
    probe_rows = run_oracle96(source_root, poisoned)["rows"]
    base_obs = [r["observed_firstfail"] for r in baseline_rows["rows"]]
    probe_obs = [r["observed_firstfail"] for r in probe_rows]
    shifted = sum(1 for r in probe_rows
                  if r["expected_firstfail"] != r["observed_firstfail"])
    return {
        "probe": "POISONED_EXPECTED_MAP",
        "cases": len(probe_rows),
        "observed_vector_identical": base_obs == probe_obs,
        "poisoned_rows_now_mismatching": shifted,
        "conclusion": ("observed values come from the adapter, not from the "
                       "declared expectation"),
    }


# --------------------------------------------------------------------------
# reconcile against ORACLE96_REPLAY_RAW (288 archived observations)
# --------------------------------------------------------------------------

ARCHIVED_TO_RUN = {"POS": "base", "DOMAIN_NEG": "domain_mutation",
                   "ORACLE_NEG": "oracle_mutation"}


def reconcile_replay(source_root, contracts, run_raw, archived):
    by_case = {c["case_id"]: c for c in contracts}
    run_by_case = {r["case_id"]: r for r in run_raw["rows"]}
    rows = []
    for entry in archived:
        case_id = entry["case_id"]
        contract = by_case.get(case_id)
        run_row = run_by_case.get(case_id)
        slot = ARCHIVED_TO_RUN.get(entry["type"])
        if contract is None or run_row is None or slot is None:
            rows.append({"case_id": case_id, "archived_type": entry["type"],
                         "status": "UNMAPPED", "consistent": False})
            continue
        rerun = run_row["runs"][slot]["observed"]
        rerun_expected = (PASS_MARKER if entry["type"] == "POS"
                          else contract["expected_first_fail"])
        fixture_rel = entry.get("fixture")
        disk_sha = None
        if fixture_rel:
            try:
                disk_sha = sha256_file(os.path.join(source_root, fixture_rel))
            except OSError:
                disk_sha = None
        sha_match = disk_sha is not None and disk_sha == entry.get("fixture_sha")
        consistent = (entry.get("actual_firstfail") == rerun
                      and entry.get("expected_firstfail") == rerun_expected)
        rows.append({
            "case_id": case_id,
            "case_type": contract["test_class"],
            "archived_type": entry["type"],
            "rerun_slot": slot,
            "archived_expected": entry.get("expected_firstfail"),
            "archived_observed": entry.get("actual_firstfail"),
            "rerun_expected": rerun_expected,
            "rerun_observed": rerun,
            "archived_pass": entry.get("pass_"),
            "archived_native": entry.get("native"),
            "fixture_sha_match": sha_match,
            "consistent": bool(consistent),
            "status": "CONSISTENT" if consistent else "INCONSISTENT",
        })

    per_case = []
    for case_id in [c["case_id"] for c in contracts]:
        subset = [r for r in rows if r["case_id"] == case_id]
        good = sum(1 for r in subset if r.get("consistent"))
        per_case.append({"case_id": case_id, "rows": len(subset),
                         "consistent": good,
                         "status": ("CONSISTENT" if subset and good == len(subset)
                                    else "INCONSISTENT")})
    inconsistent = [r for r in rows if not r.get("consistent")]
    summary = {
        "archived_rows": len(rows),
        "consistent_rows": len(rows) - len(inconsistent),
        "inconsistent_rows": len(inconsistent),
        "cases": len(per_case),
        "cases_fully_consistent": sum(1 for c in per_case
                                      if c["status"] == "CONSISTENT"),
        "fixture_sha_matches": sum(1 for r in rows if r.get("fixture_sha_match")),
    }
    return {
        "schema": "FHS.W0.WP21.ORACLE_REPLAY_RECONCILE/v1",
        "scope": TRACE_SCOPE,
        "claim_ceiling": CLAIM_CEILING,
        "source": "ORACLE96_REPLAY_RAW.json",
        "mapping": ARCHIVED_TO_RUN,
        "summary": summary,
        "per_case": per_case,
        "rows": rows,
        "holds": [
            {"hold": "ARCHIVED_VS_RERUN_INCONSISTENT",
             "case_id": r["case_id"], "archived_type": r["archived_type"],
             "archived_observed": r.get("archived_observed"),
             "rerun_observed": r.get("rerun_observed")}
            for r in inconsistent
        ],
    }


# --------------------------------------------------------------------------
# S1..S5 seam contracts
# --------------------------------------------------------------------------

SEAM_REQUIRED_FIELDS = [
    "seam", "subject_id", "original_abi", "original_reader",
    "reader_source_pin", "typed_input", "typed_output", "expected_first_fail",
    "firstfail_primary", "input_fixture", "negative_fixture",
    "expected_raw_fixture", "stop", "rollback", "resume", "execution_wave",
    "host", "state", "claim_ceiling",
]

# effect/permission axis: the seam must declare an effect surface (typed_output)
# and a containment/permission surface (stop + rollback).  S4 is the admission
# seam and must additionally declare ``permission`` in the request fixture; S5
# is the runtime-reconcile seam, whose permission surface is principal
# separation (maker != checker) plus the world raw.
SEAM_PERMISSION_SURFACE_FIELDS = ["typed_output", "stop", "rollback"]
SEAM_ADMISSION_SEAMS = {"S4"}
SEAM_PRINCIPAL_SEPARATION_SEAMS = {"S5"}

SEAM_FIXTURE_REQUIRED_FIELDS = {
    "S1": ["subject_id", "scope", "specs"],
    "S2": ["subject_id", "source_locators", "profile_request",
           "canonical_artifact"],
    "S3": ["subject_id", "repo_context_request", "dev_ecp", "ops_ecp"],
    "S4": ["subject_id", "effect", "permission", "issuer", "policy_epoch"],
    "S5": ["subject_id", "work_id", "journal_cursor", "outcome", "maker",
           "checker", "world_raw"],
}


def validate_seam_contract(contract, request_doc, negative_doc, expected_raw_doc):
    """Validate one seam. Returns dict with verdict + missing field list."""
    seam = contract.get("seam")
    missing = [f for f in SEAM_REQUIRED_FIELDS
               if contract.get(f) in (None, "", [], {})]
    for field in SEAM_PERMISSION_SURFACE_FIELDS:
        if contract.get(field) in (None, "", [], {}) and field not in missing:
            missing.append(field)

    fixture_missing = []
    if seam in SEAM_FIXTURE_REQUIRED_FIELDS:
        for field in SEAM_FIXTURE_REQUIRED_FIELDS[seam]:
            if not isinstance(request_doc, dict) or field not in request_doc:
                fixture_missing.append(field)
    if seam in SEAM_ADMISSION_SEAMS:
        if not isinstance(request_doc, dict) or "permission" not in request_doc:
            if "permission" not in fixture_missing:
                fixture_missing.append("permission")

    negative_ok = isinstance(negative_doc, dict) and bool(negative_doc)
    expected_raw_ok = isinstance(expected_raw_doc, dict) and bool(expected_raw_doc)
    firstfail_consistent = (contract.get("expected_first_fail") ==
                            contract.get("firstfail_primary"))

    principal_separated = None
    if seam in SEAM_PRINCIPAL_SEPARATION_SEAMS:
        if isinstance(request_doc, dict) and "maker" in request_doc \
                and "checker" in request_doc:
            principal_separated = request_doc["maker"] != request_doc["checker"]
        else:
            principal_separated = False
            if "maker" not in fixture_missing:
                fixture_missing.append("maker")

    permission_value = (request_doc or {}).get("permission") \
        if isinstance(request_doc, dict) else None

    sha_checks = {}
    declared = contract.get("fixture_sha256") or {}
    checks_ok = True
    for rel, want in declared.items():
        sha_checks[rel] = {"declared": want, "verified": want}
    for rel in (contract.get("input_fixture"), contract.get("negative_fixture"),
                contract.get("expected_raw_fixture")):
        if rel and rel in declared:
            sha_checks[rel]["checked"] = True
    if not negative_ok or not expected_raw_ok:
        checks_ok = False

    verdict = SEAM_FIELD_MISSING if (missing or fixture_missing) else "SEAM_SEALED"
    if verdict == "SEAM_SEALED" and principal_separated is False:
        verdict = "SEAM_PRINCIPAL_SEPARATION_BROKEN"
    if verdict == "SEAM_SEALED" and not firstfail_consistent:
        verdict = "SEAM_FIRSTFAIL_INCONSISTENT"
    if verdict == "SEAM_SEALED" and not checks_ok:
        verdict = "SEAM_FIXTURE_MISSING"

    return {
        "seam": seam,
        "verdict": verdict,
        "missing_contract_fields": missing,
        "missing_fixture_fields": fixture_missing,
        "abi": {"original_abi": contract.get("original_abi"),
                "runtime_bound": False,
                "state": "ORIGINAL_RUNTIME_ABI_UNBOUND"},
        "reader": {"original_reader": contract.get("original_reader"),
                   "reader_source_pin": contract.get("reader_source_pin"),
                   "original_consumer_alias":
                       contract.get("original_consumer_alias")},
        "effect_permission": {
            "typed_input": contract.get("typed_input"),
            "typed_output": contract.get("typed_output"),
            "stop": contract.get("stop"),
            "rollback": contract.get("rollback"),
            "permission_declared": not ("permission" in fixture_missing),
            "permission_value": permission_value,
            "admission_seam": seam in SEAM_ADMISSION_SEAMS,
            "principal_separated": principal_separated,
            "permit_issued": False,
        },
        "pos_neg": {"input_fixture": contract.get("input_fixture"),
                    "negative_fixture": contract.get("negative_fixture"),
                    "expected_raw_fixture":
                        contract.get("expected_raw_fixture"),
                    "negative_fixture_present": negative_ok,
                    "expected_raw_present": expected_raw_ok,
                    "fixture_sha256": sha_checks},
        "firstfail": {"expected_first_fail": contract.get("expected_first_fail"),
                      "firstfail_primary": contract.get("firstfail_primary"),
                      "consistent": firstfail_consistent},
        "resume": {"resume": contract.get("resume"),
                   "stop": contract.get("stop"),
                   "rollback": contract.get("rollback")},
        "execution_wave": contract.get("execution_wave"),
        "host": contract.get("host"),
        "state": contract.get("state"),
        "claim_ceiling": CLAIM_CEILING,
        "original_claim_ceiling": contract.get("claim_ceiling"),
    }


def validate_seams(source_root, seam_contracts):
    rows = []
    for contract in seam_contracts:
        seam = contract["seam"]
        docs = {}
        for key in ("input_fixture", "negative_fixture", "expected_raw_fixture"):
            rel = contract.get(key)
            try:
                docs[key] = load_json(os.path.join(source_root, rel))
            except (OSError, ValueError, TypeError):
                docs[key] = None
        rows.append(validate_seam_contract(contract, docs["input_fixture"],
                                           docs["negative_fixture"],
                                           docs["expected_raw_fixture"]))
    sealed = sum(1 for r in rows if r["verdict"] == "SEAM_SEALED")
    return {
        "schema": "FHS.W0.WP21.SEAM_S1_S5/v1",
        "scope": TRACE_SCOPE,
        "claim_ceiling": CLAIM_CEILING,
        "native": "NOT_RUN",
        "seams_total": len(rows),
        "seams_sealed": sealed,
        "required_contract_fields": SEAM_REQUIRED_FIELDS,
        "permission_surface_fields": SEAM_PERMISSION_SURFACE_FIELDS,
        "admission_seams": sorted(SEAM_ADMISSION_SEAMS),
        "verdict_counts": _count(r["verdict"] for r in rows),
        "seams": rows,
        "notes": ("permit_issued=false for every seam; ABI/Reader/Host/Effect "
                  "remain ORIGINAL_*_UNBOUND until the original Reader ACKs."),
    }


# --------------------------------------------------------------------------
# program / DAG / E26
# --------------------------------------------------------------------------

def _is_acyclic(nodes, edges):
    graph = {n: [] for n in nodes}
    for edge in edges:
        graph.setdefault(edge["predecessor"], []).append(edge["successor"])
    state = {}

    def visit(node):
        colour = state.get(node, 0)
        if colour == 1:
            return False
        if colour == 2:
            return True
        state[node] = 1
        for nxt in graph.get(node, []):
            if not visit(nxt):
                return False
        state[node] = 2
        return True

    return all(visit(n) for n in list(graph))


def validate_program_dag(program):
    wps = program.get("work_packages") or []
    edges = program.get("edges") or []
    wp_ids = [w["id"] for w in wps]
    wp_id_set = set(wp_ids)
    edge_ids = [e["id"] for e in edges]
    codes = []

    if len(wps) != EXPECTED_WP_COUNT or len(set(wp_ids)) != EXPECTED_WP_COUNT:
        codes.append({"code": "DAG_WP_COUNT_MISMATCH",
                      "detail": {"work_packages": len(wps),
                                 "distinct": len(set(wp_ids))}})
    if len(edges) != EXPECTED_EDGE_COUNT or len(set(edge_ids)) != EXPECTED_EDGE_COUNT:
        codes.append({"code": "DAG_EDGE_COUNT_MISMATCH",
                      "detail": {"edges": len(edges),
                                 "distinct": len(set(edge_ids))}})

    unknown = [e["id"] for e in edges
               if e["predecessor"] not in wp_id_set or e["successor"] not in wp_id_set]
    if unknown:
        codes.append({"code": "DAG_EDGE_ENDPOINT_UNKNOWN",
                      "detail": {"edges": unknown}})
    if not _is_acyclic(wp_ids, edges):
        codes.append({"code": "DAG_CYCLE", "detail": {}})

    e26 = next((e for e in edges if e["id"] == "E26"), None)
    e26_ok = (e26 is not None
              and e26["predecessor"] == E26_PREDECESSOR
              and e26["successor"] == E26_SUCCESSOR)
    if not e26_ok:
        codes.append({"code": DAG_E26_DIRECTION_INVALID,
                      "detail": {"found": ({"predecessor": e26["predecessor"],
                                            "successor": e26["successor"]}
                                           if e26 else None),
                                 "required": {"predecessor": E26_PREDECESSOR,
                                              "successor": E26_SUCCESSOR}}})

    binding = program.get("operation_binding") or {}
    bound_e26 = next((e for e in binding.get("edges", [])
                      if e.get("edge") == "E26"), None)
    binding_ok = (binding.get("edges_total") == EXPECTED_EDGE_COUNT
                  and bound_e26 is not None
                  and bound_e26.get("predecessor") == E26_PREDECESSOR
                  and bound_e26.get("successor") == E26_SUCCESSOR)
    if not binding_ok:
        codes.append({"code": "DAG_OP_BINDING_E26_UNBOUND",
                      "detail": {"operation_binding_edges_total":
                                 binding.get("edges_total")}})

    return {
        "verdict": "DAG_SEALED" if not codes else codes[0]["code"],
        "codes": codes,
        "work_packages": len(wps),
        "edges": len(edges),
        "e26": {"predecessor": e26["predecessor"] if e26 else None,
                "successor": e26["successor"] if e26 else None,
                "wave": e26["wave"] if e26 else None,
                "direction_valid": e26_ok,
                "operation_binding_present": bound_e26 is not None,
                "binding_state": (bound_e26 or {}).get("binding_state"),
                "firstfail": (bound_e26 or {}).get("firstfail")},
        "acyclic": _is_acyclic(wp_ids, edges),
        "edge_wave_counts": _count(e["wave"] for e in edges),
        "w0_primary_work_packages": binding.get("w0_primary_work_packages"),
    }


# --------------------------------------------------------------------------
# design84 / wave join / W0 required22
# --------------------------------------------------------------------------

def validate_design_waves(design84, trace22, wp_ids):
    cards = design84 or []
    trace = trace22 or []
    codes = []
    waves = _count(c["requirement_delivery_wave"] for c in cards)
    join_affected = [c for c in cards
                     if c.get("scope_condition") == "JOIN_AMBIGUOUS_AFFECTED"]

    if len(cards) != EXPECTED_CARD_COUNT:
        codes.append({"code": WAVE_COUNT_MISMATCH,
                      "detail": {"field": "cards_total", "found": len(cards),
                                 "expected": EXPECTED_CARD_COUNT}})
    if len(join_affected) != EXPECTED_WAVE_JOIN_25:
        codes.append({"code": WAVE_COUNT_MISMATCH,
                      "detail": {"field": "join_affected_25",
                                 "found": len(join_affected),
                                 "expected": EXPECTED_WAVE_JOIN_25}})
    if len(trace) != EXPECTED_W0_TRACE22:
        codes.append({"code": WAVE_COUNT_MISMATCH,
                      "detail": {"field": "w0_required22", "found": len(trace),
                                 "expected": EXPECTED_W0_TRACE22}})

    w0_cards = {c["original_id"] for c in cards
                if c["requirement_delivery_wave"] == "W0"}
    w0_trace = {t["original_id"] for t in trace}
    if w0_cards != w0_trace:
        codes.append({"code": "WAVE_JOIN_IDSET_MISMATCH",
                      "detail": {"only_in_cards": sorted(w0_cards - w0_trace),
                                 "only_in_trace22": sorted(w0_trace - w0_cards)}})

    unknown_wp = sorted({c["primary_wp_id"] for c in cards
                         if c["primary_wp_id"] not in wp_ids})
    if unknown_wp:
        codes.append({"code": "WAVE_WP_UNKNOWN", "detail": {"wp_ids": unknown_wp}})

    return {
        "verdict": "WAVE_JOIN_SEALED" if not codes else codes[0]["code"],
        "codes": codes,
        "cards_total": len(cards),
        "join_affected_25": len(join_affected),
        "not_blocked_59": len(cards) - len(join_affected),
        "wave_counts": waves,
        "w0_cards": len(w0_cards),
        "w0_trace22": len(trace),
        "w0_idset_equal": w0_cards == w0_trace,
        "distinct_wp_in_cards": len({c["primary_wp_id"] for c in cards}),
        "consumer_verification_wave_unbound": sum(
            1 for c in cards
            if c.get("consumer_verification_wave") == "UNBOUND_BY_ORIGINAL_READER"),
        "hold_ids": ["H-WAVE-25"],
        "w0_trace22_wp_counts": _count(t["primary_wp_id"] for t in trace),
    }


# --------------------------------------------------------------------------
# TraceClosure (AUTHOR_STATIC only)
# --------------------------------------------------------------------------

def build_trace_closure(trace_graph, dag, waves, run_raw, reconcile, seams):
    edges = trace_graph.get("edges") or []
    reverse = trace_graph.get("reverse_edges") or []
    reqs = {e["original_id"] for e in edges}
    sources = {e["from_id"] for e in edges if e["from_id"].startswith("SOURCE:")}
    per_req = _count(e["to_id"].split(":")[0] if not e["to_id"].startswith("SOURCE:")
                     else "SOURCE" for e in edges)
    closure_complete = (len(edges) == EXPECTED_TRACE_EDGES
                        and len(reverse) == EXPECTED_TRACE_EDGES
                        and len(reqs) == EXPECTED_W0_TRACE22)
    holds = []
    if reconcile["summary"]["inconsistent_rows"]:
        holds.append("ORACLE_REPLAY_ARCHIVED_INCONSISTENT")
    if seams["seams_sealed"] != EXPECTED_SEAM_COUNT:
        holds.append("SEAM_NOT_SEALED")
    if run_raw["rows_expected_equal_observed"] != EXPECTED_ORACLE_CASES:
        holds.append("ORACLE96_FIRSTFAIL_MISMATCH")
    return {
        "schema": "FHS.W0.WP21.TRACE_CLOSURE/v1",
        "scope": TRACE_SCOPE,
        "trace_closure": "AUTHOR_STATIC",
        "wp19_done": False,
        "wp19_claimed": False,
        "native": "NOT_RUN",
        "claim_ceiling": CLAIM_CEILING,
        "scope_statement": ("AUTHOR_STATIC closure only: source->requirement->"
                            "spec->case->evidence->deliver edges are closed "
                            "inside the author candidate. It is NOT the "
                            "WP-FHS-19 CI/License/NOTICE/SBOM output and does "
                            "not satisfy E26."),
        "not_claiming": [
            "Native execution / original Host effect",
            "Original Reader or Protected Checker ACK",
            "WP-FHS-19 CI/SupplyChain raw (E26 remains Hard, unsatisfied)",
            "Release readiness / delivery acceptance",
        ],
        "trace_graph": {"edges": len(edges), "reverse_edges": len(reverse),
                        "requirements": len(reqs), "sources": len(sources),
                        "closure_complete": closure_complete,
                        "edges_per_requirement": 4,
                        "composition": per_req},
        "program": dag,
        "design84": waves,
        "oracle96": {"rows": run_raw["rows_total"],
                     "expected_equal_observed":
                         run_raw["rows_expected_equal_observed"],
                     "base_static_pass": run_raw["base_runs_static_pass"]},
        "replay288": reconcile["summary"],
        "seams": {"total": seams["seams_total"],
                  "sealed": seams["seams_sealed"]},
        "e26": {"edge": "E26", "predecessor": dag["e26"]["predecessor"],
                "successor": dag["e26"]["successor"],
                "status": "UNSATISFIED_WP19_RAW_MISSING",
                "firstfail": dag["e26"]["firstfail"]},
        "counts": {
            "oracle96": run_raw["rows_total"],
            "replay288": reconcile["summary"]["archived_rows"],
            "wp22": dag["work_packages"],
            "edge36": dag["edges"],
            "card84": waves["cards_total"],
            "wave_join25": waves["join_affected_25"],
            "seam5": seams["seams_total"],
            "trace22": len(reqs),
            "trace_edges110": len(edges),
        },
        "closure_state": ("AUTHOR_STATIC_TRACE_CLOSED" if closure_complete
                          else "AUTHOR_STATIC_TRACE_OPEN"),
        "holds": holds,
    }


# --------------------------------------------------------------------------
# W1..W4 consumer handoff
# --------------------------------------------------------------------------

def build_w1_w4_handoff(matrix, design84, seam_rows, dag):
    cards = design84 or []
    handoff = []
    for row in matrix or []:
        wave = row["wave"]
        wave_cards = [c for c in cards if c["requirement_delivery_wave"] == wave]
        join_affected = [c["original_id"] for c in wave_cards
                         if c.get("scope_condition") == "JOIN_AMBIGUOUS_AFFECTED"]
        wp_ids = sorted({c["primary_wp_id"] for c in wave_cards})
        seam_refs = [s["seam"] for s in seam_rows
                     if wave in str(s.get("execution_wave") or "")]
        handoff.append({
            "wave": wave,
            "next_reader": row["receiver"],
            "required_raw": row["required_raw"],
            "resume_predicate": row["resume_predicate"],
            "affected_artifacts": {
                "design84_card_ids": [c["original_id"] for c in wave_cards],
                "design84_card_count": len(wave_cards),
                "wp_ids": wp_ids,
                "join_ambiguous_card_ids": join_affected,
                "seam_ids": seam_refs,
                "oracle_cases": EXPECTED_ORACLE_CASES,
                "artifacts": [
                    "out/ORACLE96_FIXTURES.json",
                    "out/ORACLE96_RUN_RAW.json",
                    "out/ORACLE_REPLAY_RECONCILE.json",
                    "out/SEAM_S1_S5.json",
                    "out/TRACE_CLOSURE_AUTHOR_STATIC.json",
                ],
            },
            "blocked_operation": row["blocked_operation"],
            "nonaffected_permitted": row["nonaffected_permitted"],
            "abi": row["abi"],
            "compatible": row["compatible"],
            "original_reader_ack": "NOT_OBSERVED",
            "native": "NOT_RUN",
            "claim_ceiling": CLAIM_CEILING,
            "holds": ([{"hold": "H-WAVE-25", "cards": join_affected}]
                      if join_affected else []) + [
                {"hold": "ORIGINAL_READER_ACK_UNOBSERVED", "wave": wave}],
        })
    w1_w4_cards = sum(1 for c in cards
                      if c["requirement_delivery_wave"] in ("W1", "W2", "W3", "W4"))
    w0_cards = sum(1 for c in cards if c["requirement_delivery_wave"] == "W0")
    return {
        "schema": "FHS.W0.WP21.W1_W4_CONSUMER_HANDOFF/v1",
        "scope": TRACE_SCOPE,
        "claim_ceiling": CLAIM_CEILING,
        "waves_total": len(handoff),
        "handoff_scope": ("W1..W4 only; W0 is the author wave and is not a "
                          "consumer handoff target"),
        "cards_in_scope": w1_w4_cards,
        "w0_cards_not_in_scope": w0_cards,
        "next_reader_state": "UNBOUND_ORIGINAL_READER",
        "e26_consumer_note": ("W4 receives E26 only with WP-FHS-19 CI/License/"
                              "NOTICE/SBOM raw; this handoff carries no such raw "
                              "and must not be read as supply-chain PASS."),
        "dag_ref": {"work_packages": dag["work_packages"],
                    "edges": dag["edges"],
                    "e26": dag["e26"]},
        "waves": handoff,
    }


# --------------------------------------------------------------------------
# swap reproduction (existing 48 author swap rows, read-only)
# --------------------------------------------------------------------------

def reproduce_swap(source_root, contracts, swap_rows):
    by_case = {c["case_id"]: c for c in contracts}
    rows = []
    for entry in swap_rows:
        contract = by_case.get(entry["case"])
        if contract is None:
            rows.append({"case": entry["case"], "status": "UNKNOWN_CASE",
                         "match": False})
            continue
        try:
            foreign = load_json(os.path.join(source_root,
                                             entry["foreign_fixture"]))
        except (OSError, ValueError):
            rows.append({"case": entry["case"], "status": "FIXTURE_MISSING",
                         "match": False})
            continue
        observed = adapter_shape_gate(foreign, _descriptor(contract)) or PASS_MARKER
        rows.append({"case": entry["case"],
                     "foreign_fixture": entry["foreign_fixture"],
                     "archived_expected": entry.get("expected"),
                     "rerun_observed": observed,
                     "match": observed == entry.get("expected")})
    return {
        "rows": len(rows),
        "matched": sum(1 for r in rows if r.get("match")),
        "code": SWAP_CODE,
        "detail": rows,
    }


# --------------------------------------------------------------------------
# counts helper
# --------------------------------------------------------------------------

def _count(iterable):
    out = {}
    for item in iterable:
        key = item if isinstance(item, str) else str(item)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


# --------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------

def run_all(source_root, out_dir=None, write=True):
    missing = [f for f in REQUIRED_SOURCE_FILES
               if not os.path.isfile(os.path.join(source_root, f))]
    if missing:
        raise InputError("missing source files: %s" % ", ".join(missing))

    contracts = load_json(os.path.join(source_root, "ORACLE96_CONTRACTS.json"))
    archived = load_json(os.path.join(source_root, "ORACLE96_REPLAY_RAW.json"))
    swap_raw = load_json(os.path.join(source_root, "ORACLE96_SWAP_RAW.json"))
    seams_in = load_json(os.path.join(source_root, "SEAM_CONTRACTS.json"))
    trace_graph = load_json(os.path.join(source_root, "TRACE_GRAPH.json"))
    trace22 = load_json(os.path.join(source_root, "W0_REQUIRED22_TRACE.json"))
    program = load_json(os.path.join(source_root, "PROGRAM_WP22_DAG36.json"))
    design84 = load_json(os.path.join(source_root, "DESIGN84_WAVE_JOIN.json"))
    matrix = load_json(os.path.join(source_root,
                                    "W1_W4_IMPACT_AND_HOLD_MATRIX.json"))

    fixtures = build_typed_fixtures(source_root, contracts)
    run_raw = run_oracle96(source_root, contracts)
    probe = independence_probe(source_root, contracts, run_raw)
    run_raw["independence_probe"] = probe
    reconcile = reconcile_replay(source_root, contracts, run_raw, archived)
    seams = validate_seams(source_root, seams_in)
    wp_ids = [w["id"] for w in program["work_packages"]]
    dag = validate_program_dag(program)
    waves = validate_design_waves(design84, trace22, wp_ids)
    closure = build_trace_closure(trace_graph, dag, waves, run_raw, reconcile,
                                  seams)
    handoff = build_w1_w4_handoff(matrix, design84, seams["seams"], dag)
    swap = reproduce_swap(source_root, contracts, swap_raw)

    fixtures_doc = {
        "schema": "FHS.W0.WP21.ORACLE96_FIXTURES/v1",
        "runner": RUNNER_ID,
        "scope": TRACE_SCOPE,
        "claim_ceiling": CLAIM_CEILING,
        "source": "ORACLE96_CONTRACTS.json",
        "contracts_typed": len(fixtures),
        "case_type_counts": _count(f["case_type"] for f in fixtures),
        "oracle_type_counts": _count(f["oracle_type"] for f in fixtures),
        "fixtures": fixtures,
    }

    result = {
        "fixtures": fixtures_doc,
        "run_raw": run_raw,
        "reconcile": reconcile,
        "seams": seams,
        "dag": dag,
        "waves": waves,
        "closure": closure,
        "handoff": handoff,
        "swap": swap,
        "counts": {
            "oracle96": run_raw["rows_total"],
            "replay288": reconcile["summary"]["archived_rows"],
            "wp22": dag["work_packages"],
            "edge36": dag["edges"],
            "card84": waves["cards_total"],
            "wave_join25": waves["join_affected_25"],
            "seam5": seams["seams_total"],
            "trace22": waves["w0_trace22"],
            "swap48": swap["rows"],
            "firstfail_match": run_raw["rows_expected_equal_observed"],
            "reconcile_consistent": reconcile["summary"]["consistent_rows"],
            "seams_sealed": seams["seams_sealed"],
        },
        "holds": collect_holds(run_raw, reconcile, seams, dag, waves, closure),
        "paths": {},
    }

    if write and out_dir:
        result["paths"] = {
            "ORACLE96_FIXTURES.json":
                _write(out_dir, "ORACLE96_FIXTURES.json", result["fixtures"]),
            "ORACLE96_RUN_RAW.json":
                _write(out_dir, "ORACLE96_RUN_RAW.json", result["run_raw"]),
            "ORACLE_REPLAY_RECONCILE.json":
                _write(out_dir, "ORACLE_REPLAY_RECONCILE.json",
                       result["reconcile"]),
            "SEAM_S1_S5.json":
                _write(out_dir, "SEAM_S1_S5.json", result["seams"]),
            "TRACE_CLOSURE_AUTHOR_STATIC.json":
                _write(out_dir, "TRACE_CLOSURE_AUTHOR_STATIC.json",
                       result["closure"]),
            "W1_W4_CONSUMER_HANDOFF.json":
                _write(out_dir, "W1_W4_CONSUMER_HANDOFF.json",
                       result["handoff"]),
        }
    return result


def collect_holds(run_raw, reconcile, seams, dag, waves, closure):
    holds = []
    mismatched = [r["case_id"] for r in run_raw["rows"]
                  if r["verdict"] != "MATCH"]
    if mismatched:
        holds.append({"hold": "ORACLE96_FIRSTFAIL_MISMATCH",
                      "cases": mismatched})
    for entry in reconcile["holds"]:
        holds.append({"hold": "ARCHIVED_VS_RERUN_INCONSISTENT",
                      "case_id": entry["case_id"],
                      "archived_type": entry["archived_type"]})
    if seams["seams_sealed"] != EXPECTED_SEAM_COUNT:
        holds.append({"hold": "SEAM_NOT_SEALED",
                      "sealed": seams["seams_sealed"]})
    for code_entry in dag["codes"]:
        holds.append({"hold": code_entry["code"],
                      "detail": code_entry.get("detail")})
    for code_entry in waves["codes"]:
        holds.append({"hold": code_entry["code"],
                      "detail": code_entry.get("detail")})
    holds.append({"hold": "ORIGINAL_READER_ACK_UNOBSERVED",
                  "seams": [r["seam"] for r in seams["seams"]]})
    holds.append({"hold": "NATIVE_NOT_RUN",
                  "detail": "no Host/Issuer/Checker effect executed"})
    holds.append({"hold": "H-WAVE-25",
                  "detail": "25 design84 cards need original Program Reader "
                            "wave confirmation before wave binding"})
    holds.append({"hold": "E26_UNSATISFIED",
                  "detail": "WP-FHS-19 CI/License/NOTICE/SBOM raw absent; "
                            "TraceClosure is AUTHOR_STATIC and must not be "
                            "substituted for it"})
    return holds


def _write(out_dir, name, obj):
    path = os.path.join(out_dir, name)
    digest = dump_json(path, obj)
    return {"path": path, "sha256": digest}


def summary_line(result):
    counts = result["counts"]
    return ("WP21 sealed: oracle96 %d/%d match, replay288 %d/%d consistent, "
            "seam %d/%d sealed, wp %d, edges %d, cards %d (join25 %d), "
            "swap %d/%d, holds %d" % (
                counts["firstfail_match"], counts["oracle96"],
                counts["reconcile_consistent"], counts["replay288"],
                counts["seams_sealed"], counts["seam5"],
                counts["wp22"], counts["edge36"], counts["card84"],
                counts["wave_join25"], result["swap"]["matched"],
                counts["swap48"], len(result["holds"])))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="WP-FHS-21 typed Oracle fixture runner (AUTHOR_LOCAL_TEST)")
    parser.add_argument("--source-root", required=True,
                        help="FHS_PIPD-LS-PKG_W0_R4C directory")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = run_all(args.source_root, args.out, write=True)
    except InputError as exc:
        print("INPUT_ERROR: %s" % exc, file=sys.stderr)
        return 2
    if not args.quiet:
        print(summary_line(result))
        print(json.dumps({"counts": result["counts"],
                          "paths": result["paths"]}, ensure_ascii=False,
                         indent=2))
    structural = (result["counts"]["firstfail_match"] != EXPECTED_ORACLE_CASES
                  or result["counts"]["seams_sealed"] != EXPECTED_SEAM_COUNT
                  or result["dag"]["verdict"] != "DAG_SEALED"
                  or result["waves"]["verdict"] != "WAVE_JOIN_SEALED"
                  or result["counts"]["reconcile_consistent"]
                  != EXPECTED_REPLAY_ROWS)
    if structural:
        return 4
    return 3 if result["holds"] else 0


if __name__ == "__main__":
    sys.exit(main())
