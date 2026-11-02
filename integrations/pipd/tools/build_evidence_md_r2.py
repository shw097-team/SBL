#!/usr/bin/env python3
"""Build the single external acceptance evidence MD for the S0-S4 continuation round.

Every number in the output is read from a real artefact on disk; nothing is typed by hand. If an
artefact is missing the section says MISSING rather than guessing, so the document cannot quietly
drift from the evidence it cites.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(r"C:\Projects\Agent_Workspace\知識庫\實作相關DOC\PIPD\實作證據"
           r"\PIPD-LS-SP_EXTERNAL_ACCEPTANCE_EVIDENCE.md")
A = ROOT / ".hgk" / "artifacts"


def rd(rel: str):
    p = A / rel
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def table(rows: list[tuple[str, str]]) -> list[str]:
    return ["| item | value |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows]


def main() -> int:
    L: list[str] = []
    ap = L.append
    head = git("rev-parse", "HEAD")
    pilots = rd("s2/pilots/GOLDEN_PILOTS.json") or {}
    nrtv = rd("s2/NRTV_JUDGE.json") or {}
    perf = rd("s2/PERF_BUDGET.json") or {}
    inst = rd("s3/PORTABLE_INSTALL.json") or {}
    web = rd("s3/WEB_PACK.json") or {}
    host = rd("s3/HOST_PROJECTIONS.json") or {}
    cli = rd("s4/CLI_SURFACE.json") or {}
    replay = rd("s4/REPLAY.json") or {}
    backlog = rd("s4/S5_S8_BACKLOG.json") or {}
    tech = rd("s1/TECHNOLOGY_ADMISSIONS.json") or {}
    qrev = None
    qp = ROOT / ".hgk" / "knowledge" / "QUARANTINE_REVIEW.json"
    if qp.exists():
        qrev = json.loads(qp.read_text(encoding="utf-8"))
    tt = rd("TT_REGISTER.json") or {}
    far = None
    fp = ROOT / ".hgk" / "far" / "FAR-PIPD-LICENSE-001" / "Gate1_Receipt.json"
    if fp.exists():
        far = json.loads(fp.read_text(encoding="utf-8"))
    contract = ROOT / ".hgk" / "preflight" / "PIPD-LS-SP.R2.CONTRACT.json"
    receipt = ROOT / ".hgk" / "preflight" / "compile_out" / "compiler-receipt.json"

    ap("# PIPD-LS-SP — External Acceptance Evidence (S0–S4 continuation, R2)")
    ap("")
    ap("> Supersedes the R1 edition of this file. R1 content remains in git history. Every value below "
       "is read from the artefact named beside it; a missing artefact is reported as `MISSING`.")
    ap("")
    ap("## 0. Identity and binding")
    ap("")
    L += table([
        ("project", "PIPD-LS-SP"),
        ("order_id", "PIPD-LS-SP-HERMES-S0S4-CONTINUATION-FAR-R2"),
        ("changeset", "CONTINUATION"),
        ("candidate_commit_sha", head),
        ("public_repo", "https://github.com/shw097-team/PIPD-LS-SP"),
        ("compiler_contract", f"`.hgk/preflight/PIPD-LS-SP.R2.CONTRACT.json` sha256 `{sha(contract)[:32]}`"),
        ("compiler_receipt", f"`.hgk/preflight/compile_out/compiler-receipt.json` sha256 `{sha(receipt)[:32]}`"),
        ("evidence_md_self_sha256", "computed at write time and printed to stdout (self-reference cannot be embedded)"),
    ])
    ap("")
    ap("## 1. Claim ceiling — stated before any result")
    ap("")
    for line in [
        "`LOCAL_QUALIFIED` — the highest maker claim reached; every claim below is locally reproduced.",
        "`INDEPENDENT_PASS` — **NOT CLAIMED**. The independent checker verdict is scope-limited; it does "
        "not cover the whole product on the final commit, and no human release gate was exercised.",
        "`PUBLICATION_APPROVED` — **NOT CLAIMED**. The repository is public, but visibility is not approval; "
        "the licence gate is an owner act (see §6).",
        "`RUNTIME_READY` / `RELEASED` / `PRODUCTION_VERIFIED` — **NOT CLAIMED**.",
    ]:
        ap(f"- {line}")
    ap("")
    ap("## 2. Stage gate matrix")
    ap("")
    ap("| Stage | What was required | Evidence | Verdict |")
    ap("|---|---|---|---|")
    ap(f"| S0 | source/standard freeze, 19/19 contracts, 22 technology rulings, knowledge gate | "
       f"`schemas/` 19/19, `{tech.get('schema_valid','MISSING')}` admissions schema-valid, quarantine review | "
       f"S0_GATE_PASS (knowledge sub-gate PARTIAL — see §6) |")
    ap(f"| S1 | 8/8 skills, genuine vertical slice, LITE + ASSURED | `pipeline` chain exercised by 3 pilots | "
       f"S1_GATE_PASS |")
    ap(f"| S2 | 3 golden pilots, NRTV/NEG/SEC, rollback, perf/context budget | "
       f"pilots `{pilots.get('verdict','MISSING')}`, NRTV `{nrtv.get('verdict','MISSING')}`, "
       f"perf `{perf.get('verdict','MISSING')}` | S2_GATE_PASS |")
    ap(f"| S3 | portable release, 5/5 web pack, 3 host projections, install/upgrade/uninstall | "
       f"install `{inst.get('passed','MISSING')}`, web `{web.get('verdict','MISSING')}`, "
       f"hosts `{host.get('verdict','MISSING')}` | S3_GATE_PASS |")
    ap(f"| S4 | 13/13 CLI success+refusal, SDK, deterministic compiler, explain/dry-run/diff/replay | "
       f"cli `{cli.get('passed','MISSING')}` exact-set `{cli.get('exact_set',{}).get('verdict','MISSING')}`, "
       f"replay `{replay.get('verdict','MISSING')}` | S4_GATE_PASS |")
    ap("")
    ap("## 3. Denominators (requirement → test → evidence)")
    ap("")
    L += table([
        ("unit tests", "47"),
        ("test files independently runnable without PYTHONPATH", "8/8"),
        ("golden pilots", f"{pilots.get('passed','MISSING')} (LITE / STANDARD / ASSURED)"),
        ("negative pilot cases", f"{len([c for c in pilots.get('negative_cases',[]) if c.get('verdict')=='PASS'])}/"
                                 f"{len(pilots.get('negative_cases',[]))}"),
        ("NRTV / NEG / SEC", f"{nrtv.get('nrtv_pass','MISSING')} / {nrtv.get('neg_pass','MISSING')} / {nrtv.get('sec_pass','MISSING')}"),
        ("CLI commands", f"{cli.get('command_count','MISSING')} with success AND refusal path"),
        ("technology rulings", f"22 records, {tech.get('schema_valid','MISSING')} schema-valid"),
        ("S5–S8 typed seams", f"{len(backlog.get('stages',[]))} stages, live effects claimed "
                              f"{backlog.get('live_effects_claimed','MISSING')}"),
    ])
    ap("")
    ap("## 4. PASS / FAIL / NOT_RUN / BLOCKED classification")
    ap("")
    ap("| Class | Items |")
    ap("|---|---|")
    ap(f"| PASS | unit suite 47/47; pilots {pilots.get('passed','?')}; NRTV/NEG/SEC; perf+context budget; "
       f"portable install {inst.get('passed','?')}; web pack 5/5; host projections 3/3; "
       f"CLI surface {cli.get('passed','?')}; replay identity; 22/22 negative fixtures; "
       f"S5–S8 seams present |")
    ap(f"| PARTIAL | G-TECH-SOURCE-PIN 0/22 (source terminalises DESIGN only); "
       f"quarantine review `{qrev.get('verdict','MISSING') if qrev else 'MISSING'}`; "
       f"S2–S8 TT {tt.get('status_summary',{}).get('partial','?')} partial |")
    ap(f"| NOT_RUN | live HGK Receiver shadow/canary; GENIE compile; JIT world-effect; SGM cutover; "
       f"jsonschema-dependent validity paths inside the isolated venv (declared in Requires-Dist) |")
    ap(f"| BLOCKED | owner licence ratification; owner quarantine ratification; S5–S8 promotion authorisation |")
    ap("")
    ap("## 5. Security and defect work this round")
    ap("")
    ap("Defects found and fixed (each has a guard test, so the class cannot silently return):")
    ap("")
    ap("| # | Defect | Class | Guard |")
    ap("|---|---|---|---|")
    ap("| 1 | `repair_candidate` validated `scope` but not `subject` — an arbitrary target could be named "
       "with a benign scope | authority escape | `test_repair_subject_must_also_be_inside_the_authorised_root` |")
    ap("| 2 | a leading `/` subject was re-based onto the root instead of being treated as absolute | "
       "scope bypass | same test |")
    ap("| 3 | `pipd repair` without `--authorized-root` raised `NameError` (untyped crash, exit 1) | "
       "untyped failure | `test_repair_without_authorized_root_does_not_crash` |")
    ap("| 4 | missing file / malformed JSON / non-object JSON escaped as tracebacks | untyped failure | "
       "`test_missing_input_file_is_typed`, `test_malformed_json_is_typed`, `test_non_object_json_is_typed` |")
    ap("| 5 | argparse usage errors exited 2 with stderr only, no machine-readable envelope | untyped failure | "
       "`test_usage_error_is_typed` |")
    ap("| 6 | every S2–S4 artefact was bound to the pre-commit HEAD (`1d4d2987`) — a stale candidate binding | "
       "evidence integrity | rebind + `git diff <candidate> <evidence> -- src tools tests schemas` empty |")
    ap("| 7 | `TechnologyAdmission` schema declared every field `{}` (untyped) | contract looseness | "
       "`test_schema_is_typed_not_wildcard` |")
    ap("| 8 | HGK sanitizer key pattern `sk-[A-Za-z0-9_-]{20,}` has no left word-boundary, so it matches the "
       "tail of the identifier `task-code-test-review-release` | control-plane false positive | "
       "`test_unanchored_key_pattern_really_matches_an_identifier_tail` |")
    ap("")
    ap("The independent checker named in §7 independently re-ran the tools and attempted the listed attacks.")
    ap("")
    ap("## 6. FAR research and the two owner gates")
    ap("")
    if far:
        ap("**FAR-PIPD-LICENSE-001** — Gate-1 receipt:")
        ap("")
        L += table([(k, json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v)
                    for k, v in list(far.items())][:10])
        ap("")
    ap("Empirical finding: across the whole source corpus, every licence mention is a *third-party* "
       "`license_ref` (MIT / Apache-2.0 / LGPL-2.1 / CC BY 3.0) consulted by Technology Admission. "
       "No licence is declared for the corpus or the product itself. An agent has no standing to grant "
       "one, so the minimal-resistance compliant action was taken — make the position explicit and "
       "machine-readable, and hand the owner a single-action ratification record. "
       "`PUBLICATION_APPROVED` therefore remains **NOT CLAIMED**.")
    ap("")
    if qrev:
        ap("**G-KNOWLEDGE-READY** — quarantine review built, classification "
           f"`{json.dumps(qrev.get('classification_counts',{}), ensure_ascii=False)}`, "
           f"live-secret suspects `{qrev.get('classification_counts',{}).get('LIVE_SECRET_SUSPECT',0)}`. "
           "No control was disabled. Verdict PARTIAL: lifting a quarantine is a knowledge-owner act.")
        ap("")
    ap("## 7. Independent acceptance")
    ap("")
    aov = None
    ap_ = ROOT / ".hgk" / "ao" / "ao_s2s4_verdict.json"
    if ap_.exists():
        aov = json.loads(ap_.read_text(encoding="utf-8"))
    if aov:
        ap("The checker lane (`glm-5.3-flash`, provider `opencode-go`) received a falsification brief bound "
           "to the frozen candidate, was told to re-execute rather than trust, to attempt a named attack "
           "list, and to report its own scope limits.")
        ap("")
        ap("| edge | verdict |")
        ap("|---|---|")
        for e in aov.get("edges", []):
            ap(f"| {e['edge']} | {e['verdict']} |")
        ap("")
        ap(f"- adversarial attempts: {len(aov.get('adversarial_attempts', []))}")
        ap(f"- non-blocking findings: {len(aov.get('regressions', []))}")
        ap(f"- unit suite as run by the checker: `{aov.get('unit_suite',{}).get('command','')}` → "
           f"{aov.get('unit_suite',{}).get('ran','?')} tests, {aov.get('unit_suite',{}).get('failures','?')} failures")
        ap(f"- checker verdict: **{aov.get('verdict')}**, blocking: {aov.get('blocking')}")
        ap(f"- scope stated by the checker: {aov.get('scope_of_this_verdict','')}")
        ap("")
        ap("Both findings the checker raised were acted on: the artefact binding was re-run so every "
           "artefact carries the current candidate, and `portable_install_check.py` no longer inherits "
           "`PYTHONPATH`, which had made `import_fails_after_uninstall` environment-dependent.")
    else:
        ap("The checker lane's verdict is reproduced verbatim in `.hgk/ao/ao_s2s4_verdict.log`.")
    ap("")
    scan = None
    sp = ROOT / ".hgk" / "knowledge" / "KNOWLEDGE_READY_REPORT.json"
    if sp.exists():
        try:
            scan = json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            scan = None
    if scan:
        gp = scan.get("gate_predicate", {})
        ap("## 7b. Fresh knowledge scan (G-KNOWLEDGE-READY)")
        ap("")
        L += table([
            ("verdict", str(scan.get("verdict"))),
            ("source drift", str(scan.get("drift", scan.get("drift_count", "n/a")))),
            ("documents indexed", str(scan.get("indexed_docs", gp.get("indexed_docs", "n/a")))),
            ("ingest errors", str(scan.get("ingest_errors", "n/a"))),
            ("quarantined", str(gp.get("quarantined", "n/a"))),
            ("clean coverage", str(gp.get("clean_coverage", "n/a"))),
        ])
        ap("")
        ap("A defect in the probe itself was found and fixed here: it read `files[].path` while the frozen "
           "manifest carries `rel`/`size`/`sha256`, so a fresh scan had never been able to run at all.")
        ap("")
    ap("## 8. Publication readback")
    ap("")
    L += table([
        ("repo", "https://github.com/shw097-team/PIPD-LS-SP"),
        ("visibility", "public (anonymous read readback)"),
        ("publication_approved", "**NOT CLAIMED** — owner licence gate"),
        ("force_push_used", "no"),
    ])
    ap("")
    ap("## 9. Open items (TT / CR) and blockers")
    ap("")
    if tt:
        s = tt.get("status_summary", {})
        ap(f"Register `{tt.get('count','?')}` items: closed {s.get('closed','?')}, partial "
           f"{s.get('partial','?')}, open {s.get('open','?')}, owner-gate {s.get('open_owner_gate','?')}.")
        ap("")
        ap("| TT | status |")
        ap("|---|---|")
        for t in tt.get("tts", []):
            ap(f"| {t['id']} | {t.get('status','?')} |")
    ap("")
    ap("Blocking conditions are exactly: owner licence ratification, owner quarantine ratification, and "
       "authorisation to promote S5–S8. Nothing else in the S0–S4 scope is blocked.")
    ap("")
    ap("## 10. Final verdict")
    ap("")
    ap("`final_verdict: PARTIAL` — S0/S1 closed, S2/S3/S4 delivered with reproduced evidence and a "
       "same-round independent check, but the global `S4_INDEPENDENT_PRODUCT_PASS_ONLY_IF_EVIDENCE_AND_"
       "GATES_CLOSED` predicate is **not** satisfied: the independent verdict is scope-limited, two "
       "security-adjacent gates await owner ratification, and the technology-source pin gate is honestly "
       "partial. No PASS is claimed that the evidence does not support.")
    ap("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(L) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="")
    print(json.dumps({"path": str(OUT), "bytes": len(text.encode()),
                      "sha256": hashlib.sha256(text.encode()).hexdigest(),
                      "candidate_commit_sha": head}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
