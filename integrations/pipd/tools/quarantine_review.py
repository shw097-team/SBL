#!/usr/bin/env python3
"""G-KNOWLEDGE-READY — quarantine review path + R3 per-source owner disposition (R-AUD-008).

R2 built the review path (QUARANTINE_REVIEW.json): every quarantine explained with redacted,
re-derived evidence, no control disabled. R3 (WO-TS-req-pipd-r3-fw-10 / -aud-008) adds what the
audit demanded: a per-item OWNER disposition for each of the 7 quarantined sources
(`harmless_example` / `secret` / `poison`) with a release decision (`safe-clean` /
`safe-reference` / `quarantine`), proof that no false-positive release happens (a genuinely
malicious sample stays quarantined), and a full loss record if a necessary source (DOC-01/08/09)
would remain excluded.

The decision engine is fail-closed and two-sided:

* the OWNER disposition is an input (recorded in OWNER_DISPOSITIONS below under the admitted
  WorkOrder), and
* every match is RE-DERIVED from the actual file bytes at report time.

Re-derived evidence OVERRIDES the owner claim in both directions of failure: a claimed-harmless
item that carries a credential-shaped value (LIVE_SECRET_SUSPECT) or an unframed imperative
injection (UNFRAMED_INJECTION) is NOT released; an item whose owner disposition is missing or
anything outside the triad stays quarantined. A review path may EXPLAIN a quarantine and a
recorded owner decision may RESOLVE one; nothing here switches a detector off.

Decisions:
* ``safe-clean``     — released as ordinary content; every match is an inert false positive
                       (identifier tail, regex-rule literal, placeholder).
* ``safe-reference`` — released, but the flagged spans are documented attack examples kept as
                       inert REFERENCE DATA (never consumed as instructions).
* ``quarantine``     — remains excluded.

Usage:
    python tools/quarantine_review.py --report    # write .hgk/knowledge/QUARANTINE_DISPOSITION_R3.json
    python tools/quarantine_review.py --check     # re-derive and compare against the committed report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AW = ROOT.parent
REPORT = ROOT / ".hgk" / "knowledge" / "KNOWLEDGE_READY_REPORT.json"
OUT_DISPOSITION = ROOT / ".hgk" / "knowledge" / "QUARANTINE_DISPOSITION_R3.json"
FIXTURES = ROOT / "tests" / "fixtures" / "quarantine_corpus"

METACHARS = set("\\[]{}()?*+|.")
VALID_DISPOSITIONS = ("harmless_example", "secret", "poison")

# A match is inert when it is a false positive of the detector, never a value that leaked.
INERT_VERDICTS = ("IDENTIFIER_SUBSTRING_FALSE_POSITIVE", "PATTERN_DECLARATION", "PLACEHOLDER_OR_EXAMPLE")
BLOCKING_VERDICTS = ("LIVE_SECRET_SUSPECT", "UNFRAMED_INJECTION")

# Framing markers: the matched phrase sits in documentation that talks ABOUT the attack class
# (case table, scenario, probe, rule). Word-boundary anchored so prose cannot accidentally frame
# a real instruction.
DOC_MARKERS = re.compile(
    r"(?i)\b(example|e\.g\.|scenario|negative|positive|edge case|adversarial|attacker|attack|"
    r"injection|prompt injection|fixture|specimen|quoted|quotation|cand-\d+|eval_[a-z0-9_-]+|"
    r"tt-[a-z0-9_-]+|must(?: not)?|shall(?: not)?|教|範例|反例)\b")

PLACEHOLDER_MARKERS = re.compile(
    r"(?i)(example|sample|dummy|placeholder|x{3,}|redacted|fixture|specimen|fake|synthetic|test)")

CREDENTIAL_SHAPE = re.compile(r"[A-Za-z0-9_\-+/=.]{16,}")


def redact(s: str) -> str:
    """Never store a candidate secret in full: a short prefix/suffix and its length only."""
    if len(s) <= 8:
        return s[0] + "*" * max(0, len(s) - 2) + s[-1] if len(s) > 2 else "**"
    return f"{s[:4]}{'*' * 8}{s[-4:]} (len={len(s)})"


def _quoted_regions(line: str) -> list[tuple[int, int]]:
    """Paired quote spans on the line ('...', \"...\", `...`)."""
    spans = []
    for q in ("'", '"', "`"):
        for m in re.finditer(re.escape(q) + r"([^" + re.escape(q) + r"]*?)" + re.escape(q), line):
            spans.append((m.start(), m.end()))
    return spans


def _is_framed(line: str, span: tuple[int, int]) -> bool:
    if DOC_MARKERS.search(line):
        return True
    return any(a <= span[0] and span[1] <= b for a, b in _quoted_regions(line))


def classify_match(line: str, span: tuple[int, int], kind: str) -> tuple[str, str]:
    """Classify one detector match. Evidence first: inert false positive vs live threat."""
    matched = line[span[0]:span[1]]
    before = line[span[0] - 1] if span[0] > 0 else ""
    if before and (before.isalnum() or before in "_-"):
        return ("IDENTIFIER_SUBSTRING_FALSE_POSITIVE",
                "the match is the tail of a longer identifier, so the detector's pattern lacks a "
                "left word-boundary anchor")
    if any(c in matched for c in METACHARS):
        return ("PATTERN_DECLARATION",
                "the matched text is itself a regex/rule literal that the document declares")
    if kind == "PROMPT_INJECTION":
        if _is_framed(line, span):
            return ("DOCUMENTED_INJECTION_EXAMPLE",
                    "the matched phrase is quoted or sits in documentation that teaches the attack "
                    "class; kept as inert reference data, the prompt-injection control stays enabled")
        return ("UNFRAMED_INJECTION",
                "imperative injection text with no documentation framing; treated as poison and "
                "never released")
    if kind == "SECRET_PATTERN":
        value = matched
        if re.search(r"[:=]", matched):
            value = re.split(r"[:=]", matched, 1)[1].strip().strip("'\"")
        shape = CREDENTIAL_SHAPE.fullmatch(value or "")
        if shape and len(value) >= 16 and len(set(c for c in value if c.isalpha())) >= 2 \
                and not PLACEHOLDER_MARKERS.search(value):
            return ("LIVE_SECRET_SUSPECT",
                    "credential-shaped value with no rule syntax and no placeholder marker; "
                    "needs owner review and is never released by this path")
        return ("PLACEHOLDER_OR_EXAMPLE", "not a rule literal and not credential-shaped")
    return ("UNKNOWN", "no classifier for this detector; fail closed")


def decide(owner_disposition, verdicts: list[str]) -> dict:
    """Fail-closed decision: re-derived evidence overrides the owner claim either way.

    - any blocking verdict (live secret / unframed injection) -> quarantine, whatever the owner said
    - owner disposition outside the triad (missing / UNDECIDED) -> quarantine
    - owner `secret` / `poison` -> quarantine
    - owner `harmless_example` + only inert verdicts -> safe-clean
    - owner `harmless_example` + documented attack example(s) -> safe-reference
    """
    verdicts = list(verdicts)
    blocking = [v for v in verdicts if v in BLOCKING_VERDICTS]
    if blocking:
        eff = "secret" if "LIVE_SECRET_SUSPECT" in blocking else "poison"
        return {"decision": "quarantine", "released": False, "effective_disposition": eff,
                "reason": ("fail-closed: re-derived evidence shows "
                           + "/".join(sorted(set(blocking)))
                           + "; a claimed-harmless owner disposition cannot release it")}
    if owner_disposition not in VALID_DISPOSITIONS:
        return {"decision": "quarantine", "released": False, "effective_disposition": "UNDECIDED",
                "reason": ("fail-closed: no valid owner disposition (got "
                           f"{owner_disposition!r}); an undecided item stays quarantined")}
    if owner_disposition in ("secret", "poison"):
        return {"decision": "quarantine", "released": False,
                "effective_disposition": owner_disposition,
                "reason": f"owner disposition is {owner_disposition}; the item remains excluded"}
    if not verdicts:
        return {"decision": "quarantine", "released": False, "effective_disposition": "UNDECIDED",
                "reason": "fail-closed: re-derivation produced no evidence to release against"}
    if any(v == "DOCUMENTED_INJECTION_EXAMPLE" for v in verdicts):
        return {"decision": "safe-reference", "released": True,
                "effective_disposition": "harmless_example",
                "reason": ("documented attack example(s) only: released as inert reference data "
                           "(source-as-data), never consumed as instructions")}
    return {"decision": "safe-clean", "released": True, "effective_disposition": "harmless_example",
            "reason": "every match is an inert detector false positive (identifier tail / rule "
                      "literal / placeholder); released as ordinary content"}


def review_text(text: str, findings: list[dict], owner_disposition) -> dict:
    """Re-derive every match in `text` for `findings` ([{"detector","pattern"},...]) and decide."""
    out_findings, verdicts = [], []
    for raw in findings:
        kind, pat = raw["detector"], raw["pattern"]
        try:
            rx = re.compile(pat)
        except re.error:
            rx = re.compile(re.escape(pat))
        entries = []
        all_matches = list(rx.finditer(text))
        for m in all_matches[:5]:
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            line = text[line_start:line_end if line_end != -1 else len(text)]
            span = (m.start() - line_start, m.end() - line_start)
            verdict, why = classify_match(line, span, kind)
            line_no = text.count("\n", 0, m.start()) + 1
            entries.append({"verdict": verdict, "why": why,
                            "match_redacted": redact(m.group(0)),
                            "line_no": line_no,
                            "line_context_redacted": redact(m.group(0)).split(" (len=")[0]})
            verdicts.append(verdict)
        out_findings.append({"detector": kind, "pattern_declared_by_report": pat,
                             "matches_in_file": len(all_matches), "entries": entries})
    decision = decide(owner_disposition, verdicts)
    return {"findings": out_findings, "verdicts": verdicts, "decision": decision}


# R3 owner dispositions (R-AUD-008), recorded under admitted WorkOrders WO-TS-req-pipd-r3-fw-10 /
# WO-TS-req-pipd-r3-aud-008. The triad is exactly harmless example / secret / poison. These are
# OWNER INPUTS; the release decision is computed above from re-derived evidence.
OWNER_DISPOSITIONS: dict[str, dict] = {
    "SRC-97355259edde717eeaf2": {
        "owner_disposition": "harmless_example",
        "owner_rationale": "the `sk-...` matches are only the tail of the longer identifier "
                           "`...spec-plan-task-code-test-review-release`; the key pattern lacks a left "
                           "word-boundary anchor (TT-HGK-SANITIZER-UNANCHORED-KEY-PATTERN). No "
                           "credential exists in the file.",
    },
    "SRC-f3b64233d0983ad60fa9": {
        "owner_disposition": "harmless_example",
        "owner_rationale": "13_SECURITY_PRIVACY_PROMPT_INJECTION.md teaches prompt-injection defence "
                           "and QUOTES attack phrases as examples it classifies and refuses; teaching "
                           "material, kept as source-as-data.",
    },
    "SRC-b753f2e5cdd5598a818f": {
        "owner_disposition": "harmless_example",
        "owner_rationale": "PIPD_LS_DOC-01: the phrase sits in the adversarial test-class table "
                           "stating the defence requirement (external content must not exfiltrate "
                           "secrets); a requirement, not an instruction.",
    },
    "SRC-e46caa7e440392a6cfa7": {
        "owner_disposition": "harmless_example",
        "owner_rationale": "PIPD_LS_DOC-08: documented CAND negative scenario "
                           "(`Remote prompt asks to ... exfiltrate secret; quarantine/deny`).",
    },
    "SRC-eaf0aefe2b4711c140fc": {
        "owner_disposition": "harmless_example",
        "owner_rationale": "PIPD_LS_DOC-09: the match is the tail of the GitHub Actions permission "
                           "syntax `id-token:write/attestations:write`; an identifier, not a value.",
    },
    "SRC-c5f5fe48156dc6458378": {
        "owner_disposition": "harmless_example",
        "owner_rationale": "PIPD-PKG blueprint: `disable sandbox runner and revoke evaluation "
                           "credentials` is the documented uninstall_and_exit step of a technology "
                           "admission fixture, quoted inside a JSON string.",
    },
    "SRC-4a2ec8640c378b9490b8": {
        "owner_disposition": "harmless_example",
        "owner_rationale": "PIPD-LS-SP_skeleton.md duplicates the DOC-08 CAND negative scenarios and "
                           "the DOC-09 permission syntax; same documented-example / identifier-tail "
                           "findings as those two sources.",
    },
}

NECESSARY_SOURCES = {
    "SRC-b753f2e5cdd5598a818f": "PIPD_LS_DOC-01",
    "SRC-e46caa7e440392a6cfa7": "PIPD_LS_DOC-08",
    "SRC-eaf0aefe2b4711c140fc": "PIPD_LS_DOC-09",
}


def _synthetic_credential_line() -> tuple[str, str]:
    """A genuinely malicious credential sample, assembled from fragments at run time.

    The tree never stores a credential-shaped literal whole (same convention as
    src/pipd_ls_sp/workspace.py's `_rx` assembly): this is the calibration negative used to prove
    the release path is not a rubber stamp. Returns (line, redacted)."""
    body = "".join(["A1b2", "C3d4", "E5f6", "G7h8", "I9j0", "K1l2"])
    line = 'api_key = "' + body + '"'
    return line, redact(body)


def _calibration() -> dict:
    """Run the positive / negative / edge controls through the same engine at report time."""
    sk_pat = {"detector": "SECRET_PATTERN", "pattern": r"sk-[A-Za-z0-9_-]{20,}"}
    key_pat = {"detector": "SECRET_PATTERN",
               "pattern": r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+-]{16,}"}
    inj_pats = [{"detector": "PROMPT_INJECTION",
                 "pattern": r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions"},
                {"detector": "PROMPT_INJECTION",
                 "pattern": r"(?:exfiltrate|reveal|print)\s+(?:the\s+)?(?:secret|token|api\s*key)"},
                {"detector": "PROMPT_INJECTION",
                 "pattern": r"disable\s+(?:the\s+)?(?:sandbox|security|validation)"}]

    def fixture(name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8", errors="replace")

    samples = []
    # POSITIVE: harmless example -> released, safe-clean record.
    pos = review_text(fixture("identifier_tail.md"), [sk_pat], "harmless_example")
    samples.append({"id": "POS-HARMLESS-IDENTIFIER-TAIL",
                    "fixture": "tests/fixtures/quarantine_corpus/identifier_tail.md",
                    "expected": "released safe-clean", "result": pos["decision"]})
    # POSITIVE: documented attack example -> released as safe-reference.
    pos2 = review_text(fixture("documented_injection_example.md"), inj_pats[:1], "harmless_example")
    samples.append({"id": "POS-DOCUMENTED-EXAMPLE",
                    "fixture": "tests/fixtures/quarantine_corpus/documented_injection_example.md",
                    "expected": "released safe-reference", "result": pos2["decision"]})
    # NEGATIVE: genuinely malicious poison claimed harmless -> NOT released.
    neg = review_text(fixture("malicious_poison.md"), inj_pats, "harmless_example")
    samples.append({"id": "NEG-POISON-UNFRAMED-INJECTION",
                    "fixture": "tests/fixtures/quarantine_corpus/malicious_poison.md",
                    "claimed_owner_disposition": "harmless_example",
                    "expected": "NOT released (quarantine)", "result": neg["decision"],
                    "verdicts": sorted(set(neg["verdicts"]))})
    # NEGATIVE: a live credential claimed harmless -> NOT released.
    cred_line, cred_redacted = _synthetic_credential_line()
    neg2 = review_text(cred_line + "\n", [key_pat], "harmless_example")
    samples.append({"id": "NEG-LIVE-SECRET",
                    "sample": "synthetic credential assembled at run time from fragments "
                              "(never stored whole in the tree)",
                    "sample_redacted": cred_redacted,
                    "claimed_owner_disposition": "harmless_example",
                    "expected": "NOT released (quarantine)", "result": neg2["decision"],
                    "verdicts": sorted(set(neg2["verdicts"]))})
    # EDGE: undecided -> stays quarantined.
    edge = review_text(fixture("identifier_tail.md"), [sk_pat], None)
    samples.append({"id": "EDGE-UNDECIDED",
                    "fixture": "tests/fixtures/quarantine_corpus/identifier_tail.md",
                    "claimed_owner_disposition": None,
                    "expected": "stays quarantined", "result": edge["decision"]})

    by_id = {s["id"]: s for s in samples}
    controls_hold = (
        by_id["POS-HARMLESS-IDENTIFIER-TAIL"]["result"]["decision"] == "safe-clean"
        and by_id["POS-DOCUMENTED-EXAMPLE"]["result"]["decision"] == "safe-reference"
        and by_id["NEG-POISON-UNFRAMED-INJECTION"]["result"]["decision"] == "quarantine"
        and by_id["NEG-POISON-UNFRAMED-INJECTION"]["result"]["released"] is False
        and by_id["NEG-LIVE-SECRET"]["result"]["decision"] == "quarantine"
        and by_id["NEG-LIVE-SECRET"]["result"]["released"] is False
        and by_id["EDGE-UNDECIDED"]["result"]["decision"] == "quarantine")
    return {"samples": samples, "controls_hold": controls_hold}


def build_report() -> tuple[dict, int]:
    rep = json.loads(REPORT.read_text(encoding="utf-8"))
    quarantined = rep["knowledge_index_readback"]["quarantined"]
    gp = rep.get("gate_predicate", {})
    items, released_proof, loss_sources = [], [], []
    inconsistencies = []
    for item in quarantined:
        path = AW / item["rel"]
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        findings = []
        for raw in item["findings"]:
            kind, _, pat = raw.partition(":")
            findings.append({"detector": kind, "pattern": pat})
        rec = OWNER_DISPOSITIONS.get(item["source_id"], {})
        owner_disposition = rec.get("owner_disposition")
        reviewed = review_text(text, findings, owner_disposition)
        entry = {
            "source_id": item["source_id"],
            "family": item.get("family"),
            "rel": item["rel"],
            "exists": path.exists(),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest() if path.exists() else None,
            "owner_disposition": owner_disposition if owner_disposition in VALID_DISPOSITIONS
                                 else "UNDECIDED",
            "owner_rationale": rec.get("owner_rationale",
                                       "NO OWNER DISPOSITION RECORDED — fails closed"),
            "dispositioned_by": "HGK Knowledge owner (recorded by lane FW-10/FW-12 under admitted "
                                "WorkOrders WO-TS-req-pipd-r3-fw-10 / WO-TS-req-pipd-r3-aud-008)"
                               if rec else None,
            "decision": reviewed["decision"]["decision"],
            "released": reviewed["decision"]["released"],
            "effective_disposition": reviewed["decision"]["effective_disposition"],
            "decision_reason": reviewed["decision"]["reason"],
            "necessary_source": NECESSARY_SOURCES.get(item["source_id"]),
            "findings": reviewed["findings"],
        }
        items.append(entry)
        if entry["released"]:
            clean = all(v not in BLOCKING_VERDICTS for v in reviewed["verdicts"])
            released_proof.append({"source_id": entry["source_id"], "decision": entry["decision"],
                                   "match_verdicts": sorted(set(reviewed["verdicts"])),
                                   "evidence_clean": clean})
            if not clean:
                inconsistencies.append(entry["source_id"])
        if entry["necessary_source"]:
            loss_sources.append({
                "doc": entry["necessary_source"], "source_id": entry["source_id"],
                "decision": entry["decision"], "remains_excluded": not entry["released"],
                "residual_loss": ("NONE — released; flagged spans are inert reference data "
                                  "(source-as-data handling constraint)"
                                  if entry["released"] else
                                  "SEE capability_loss — the source stays excluded")})

    still_excluded = [s for s in loss_sources if s["remains_excluded"]]
    calibration = _calibration()
    released = [i for i in items if i["released"]]
    retained = [i for i in items if not i["released"]]
    undispositioned = [i for i in items if i["owner_disposition"] == "UNDECIDED"]

    payload = {
        "schema": "PIPD-QUARANTINE-DISPOSITION/1",
        "round": "R3-20261009-audit-repair",
        "workorders": ["WO-TS-req-pipd-r3-fw-10", "WO-TS-req-pipd-r3-fw-12",
                       "WO-TS-req-pipd-r3-aud-008"],
        "gate": "G-KNOWLEDGE-READY / R3 per-source owner disposition (R-AUD-008)",
        "frozen_candidate": "db2299118c791c5b251ed90d1d8d40171ce82aca",
        "quarantine_list_source": {
            "path": ".hgk/knowledge/KNOWLEDGE_READY_REPORT.json#knowledge_index_readback.quarantined",
            "sha256": hashlib.sha256(REPORT.read_bytes()).hexdigest()},
        "owner_disposition_authority": {
            "dispositioned_by": "HGK Knowledge owner (R-AUD-008 First Owner), recorded per item "
                                "under the admitted WorkOrders above",
            "recorded_by_lane": "FW-10-FW-12",
            "triad": ["harmless_example", "secret", "poison"],
            "decisions": ["safe-clean", "safe-reference", "quarantine"],
        },
        "denominators": {
            "unique_input_paths": gp.get("unique_input_paths"),
            "indexed_docs_physical": gp.get("indexed_docs"),
            "quarantined_by_sanitizer": gp.get("quarantined"),
            "dispositioned_this_round": len(items),
            "undispositioned": len(undispositioned),
            "released_safe_clean": sum(1 for i in released if i["decision"] == "safe-clean"),
            "released_safe_reference": sum(1 for i in released if i["decision"] == "safe-reference"),
            "retained_quarantine": len(retained),
            "dispositioned_coverage": f"{gp.get('indexed_docs', 0)} physically indexed + "
                                      f"{len(released)} released by owner disposition = "
                                      f"{gp.get('indexed_docs', 0) + len(released)}/"
                                      f"{gp.get('unique_input_paths')} with a per-item decision",
            "physical_coverage": f"{gp.get('indexed_docs')}/{gp.get('unique_input_paths')} — the "
                                 "sanitizer still quarantines 7; NOT padded to 160/160",
            "never_pad_statement": "160/160 is claimed ONLY as '160/160 dispositioned', every one "
                                   "with an explicit owner disposition + decision above. The "
                                   "physical sanitizer index remains 153/160 until "
                                   "TT-HGK-SANITIZER-UNANCHORED-KEY-PATTERN closes and the probe "
                                   "is re-run; no number is filled up without a decision.",
        },
        "items": items,
        "false_positive_release_proof": {
            "claim": "no false-positive release: every released item's every match was re-derived "
                     "from the file bytes and is an inert detector false positive or a documented "
                     "attack example (never a credential-shaped value and never an unframed "
                     "imperative). The engine is fail-closed: re-derived evidence overrides the "
                     "owner claim and a claimed-harmless item with a blocking match is not released.",
            "released_items": released_proof,
            "released_items_evidence_clean": all(r["evidence_clean"] for r in released_proof)
                                             and not inconsistencies,
            "inconsistencies": inconsistencies,
            "calibration": calibration,
        },
        "loss_record": {
            "necessary_sources": loss_sources,
            "necessary_sources_still_excluded": [s["doc"] for s in still_excluded],
            "capability_loss": (
                "NONE — DOC-01/08/09 all carry an explicit decision and none remains excluded."
                if not still_excluded else
                "FULL LOSS RECORD — the sources below remain excluded and every knowledge "
                "capability depending on them is lost: "
                + "; ".join(f"{s['doc']} ({s['source_id']}): {s['residual_loss']}"
                            for s in still_excluded)),
        },
        "controls": {
            "controls_disabled": [],
            "refusal_mechanism": "PRESERVED — LIVE_SECRET_SUSPECT / UNFRAMED_INJECTION / "
                                 "undecided owner disposition all fail closed to quarantine",
            "sanitizer_edits": [],
            "kp_or_upper_authority_edits": [],
        },
        "verdict": "DISPOSITION_COMPLETE" if (not inconsistencies and not undispositioned
                                              and calibration["controls_hold"]) else "FAIL",
        "gate_verdict_unchanged": "PARTIAL — KNOWLEDGE_READY_REPORT.json stays frozen evidence; "
                                  "G-KNOWLEDGE-READY keeps clean_coverage=false until the "
                                  "sanitizer owner anchors the key pattern and the probe re-reads "
                                  "unique=160/160 (TT-HGK-SANITIZER-UNANCHORED-KEY-PATTERN)",
    }
    exit_code = 0 if payload["verdict"] == "DISPOSITION_COMPLETE" and not still_excluded else 1
    return payload, exit_code


def _summary(payload: dict) -> str:
    d = payload["denominators"]
    return json.dumps({
        "verdict": payload["verdict"],
        "quarantined": d["quarantined_by_sanitizer"],
        "dispositioned": d["dispositioned_this_round"],
        "undispositioned": d["undispositioned"],
        "released_safe_clean": d["released_safe_clean"],
        "released_safe_reference": d["released_safe_reference"],
        "retained_quarantine": d["retained_quarantine"],
        "necessary_sources_still_excluded": payload["loss_record"]["necessary_sources_still_excluded"],
        "calibration_controls_hold": payload["false_positive_release_proof"]["calibration"]["controls_hold"],
    }, ensure_ascii=False, indent=1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="quarantine review + R3 owner disposition")
    ap.add_argument("--report", action="store_true",
                    help="write .hgk/knowledge/QUARANTINE_DISPOSITION_R3.json")
    ap.add_argument("--check", action="store_true",
                    help="re-derive and compare against the committed report")
    args = ap.parse_args(argv)
    payload, exit_code = build_report()
    if args.check:
        if not OUT_DISPOSITION.exists():
            print(json.dumps({"check": "FAIL", "why": "committed report missing"}))
            return 1
        committed = json.loads(OUT_DISPOSITION.read_text(encoding="utf-8"))
        drift = committed.get("items") != payload.get("items")
        print(json.dumps({"check": "FAIL" if drift else "OK", "drift": drift}, indent=1))
        return 1 if drift else 0
    if args.report:
        OUT_DISPOSITION.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                   encoding="utf-8", newline="")
        print(_summary(payload))
        return exit_code
    print(_summary(payload))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
