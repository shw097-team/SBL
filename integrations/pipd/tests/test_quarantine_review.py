"""Guard the quarantine review path (TT-PIPD-KNOWLEDGE-QUARANTINE) and the R3 disposition engine.

Two rules are pinned here:

1. a review path may EXPLAIN a quarantine, it may never CLEAR one by disabling a control. A
   security control that an agent can switch off is not a control.
2. (R-AUD-008) the per-source owner disposition path is fail-closed in BOTH directions: a
   harmless documented example is released with a safe-clean / safe-reference record, a
   genuinely malicious sample is NOT released even when the owner claims it is harmless, and an
   undecided item stays quarantined. The concrete unanchored-key-pattern finding that motivated
   the whole path is reproduced rather than trusted.
"""
from __future__ import annotations
import importlib.util
import json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
AW = ROOT.parent
FIX = ROOT / "tests" / "fixtures" / "quarantine_corpus"


def _load_tool():
    spec = importlib.util.spec_from_file_location(
        "quarantine_review_tool", ROOT / "tools" / "quarantine_review.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


QR = _load_tool()

SK_PAT = {"detector": "SECRET_PATTERN", "pattern": r"sk-[A-Za-z0-9_-]{20,}"}
KEY_PAT = {"detector": "SECRET_PATTERN",
           "pattern": r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+-]{16,}"}
INJ_PATS = [{"detector": "PROMPT_INJECTION",
             "pattern": r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions"},
            {"detector": "PROMPT_INJECTION",
             "pattern": r"(?:exfiltrate|reveal|print)\s+(?:the\s+)?(?:secret|token|api\s*key)"},
            {"detector": "PROMPT_INJECTION",
             "pattern": r"disable\s+(?:the\s+)?(?:sandbox|security|validation)"}]


class QuarantineReview(unittest.TestCase):
    def setUp(self) -> None:
        self.rev = json.loads((ROOT / ".hgk" / "knowledge" / "QUARANTINE_REVIEW.json").read_text(encoding="utf-8"))

    def test_every_quarantined_source_is_covered(self) -> None:
        rep = json.loads((ROOT / ".hgk" / "knowledge" / "KNOWLEDGE_READY_REPORT.json").read_text(encoding="utf-8"))
        self.assertEqual(len(self.rev["review"]), len(rep["knowledge_index_readback"]["quarantined"]))

    def test_review_does_not_disable_any_control(self) -> None:
        self.assertEqual(self.rev["controls_disabled"], [])
        self.assertEqual(self.rev["verdict"], "PARTIAL")
        self.assertTrue(self.rev["owner_decision_required"])

    def test_no_live_secret_suspect_is_waved_through(self) -> None:
        self.assertEqual(self.rev["classification_counts"].get("LIVE_SECRET_SUSPECT", 0), 0)

    def test_unanchored_key_pattern_really_matches_an_identifier_tail(self) -> None:
        # reproduces the finding rather than trusting it
        # R2-E1: this used to read the TRUE quarantine source under the external 知識庫 corpus
        # (AW/知識庫/...), so it SKIPPED in any isolated copy where that corpus is absent - a skipped
        # security test is a non-result. It now runs against a minimal, present, in-repo fixture that
        # reproduces the same identifier tail (`spec-plan-task-code-test-review-release`), so the
        # path is genuinely EXERCISED everywhere. Assertions are unchanged and no credential exists
        # in the fixture: the naive match is a substring of a longer identifier, exactly the finding.
        f = FIX / "identifier_tail.md"
        self.assertTrue(f.is_file(), "quarantine fixture corpus must be present in-repo")
        text = f.read_text(encoding="utf-8", errors="replace")
        naive = re.compile(r"sk-[A-Za-z0-9_-]{20,}")
        anchored = re.compile(r"(?<![A-Za-z0-9_-])sk-[A-Za-z0-9]{20,}")
        self.assertGreater(len(list(naive.finditer(text))), 0)
        self.assertEqual(len(list(anchored.finditer(text))), 0,
                         "the anchored form must not match an identifier tail")


class QuarantineDispositionR3(unittest.TestCase):
    """R-AUD-008: per-item owner disposition, no false-positive release, loss record (FW-10)."""

    def test_positive_harmless_example_is_released_with_a_safe_clean_record(self) -> None:
        text = (FIX / "identifier_tail.md").read_text(encoding="utf-8", errors="replace")
        res = QR.review_text(text, [SK_PAT], "harmless_example")
        self.assertEqual(res["decision"]["decision"], "safe-clean",
                         "a harmless identifier-tail false positive must be released safe-clean")
        self.assertTrue(res["decision"]["released"])
        self.assertEqual(res["decision"]["effective_disposition"], "harmless_example")
        self.assertEqual(set(res["verdicts"]), {"IDENTIFIER_SUBSTRING_FALSE_POSITIVE"},
                         "the record must show WHY it is clean: every match re-derived as inert")
        # the documented-attack-example sibling is released too, but only as reference data
        text2 = (FIX / "documented_injection_example.md").read_text(encoding="utf-8", errors="replace")
        res2 = QR.review_text(text2, INJ_PATS[:1], "harmless_example")
        self.assertEqual(res2["decision"]["decision"], "safe-reference")
        self.assertTrue(res2["decision"]["released"])
        self.assertIn("DOCUMENTED_INJECTION_EXAMPLE", res2["verdicts"])

    def test_negative_malicious_sample_is_not_released(self) -> None:
        # poison: unframed imperative injection, even claimed harmless by the owner
        text = (FIX / "malicious_poison.md").read_text(encoding="utf-8", errors="replace")
        res = QR.review_text(text, INJ_PATS, "harmless_example")
        self.assertEqual(res["decision"]["decision"], "quarantine",
                         "a genuinely malicious sample must NOT be released")
        self.assertFalse(res["decision"]["released"])
        self.assertEqual(res["decision"]["effective_disposition"], "poison")
        self.assertIn("UNFRAMED_INJECTION", res["verdicts"])
        # secret: a live credential-shaped value, also claimed harmless (assembled, never stored)
        cred_line, _ = QR._synthetic_credential_line()
        res2 = QR.review_text(cred_line + "\n", [KEY_PAT], "harmless_example")
        self.assertEqual(res2["decision"]["decision"], "quarantine")
        self.assertFalse(res2["decision"]["released"])
        self.assertEqual(res2["decision"]["effective_disposition"], "secret")
        self.assertIn("LIVE_SECRET_SUSPECT", res2["verdicts"])
        # and an owner who calls it secret/poison never releases it either
        self.assertEqual(QR.decide("poison", ["PLACEHOLDER_OR_EXAMPLE"])["decision"], "quarantine")
        self.assertEqual(QR.decide("secret", [])["decision"], "quarantine")

    def test_edge_undecided_item_stays_quarantined(self) -> None:
        text = (FIX / "identifier_tail.md").read_text(encoding="utf-8", errors="replace")
        for undecided in (None, "", "UNDECIDED", "undecided", "harmless"):
            res = QR.review_text(text, [SK_PAT], undecided)
            self.assertEqual(res["decision"]["decision"], "quarantine",
                             f"owner_disposition={undecided!r} must stay quarantined")
            self.assertFalse(res["decision"]["released"])
            self.assertEqual(res["decision"]["effective_disposition"], "UNDECIDED")

    def test_committed_disposition_report_has_a_decision_for_every_source(self) -> None:
        disp = json.loads((ROOT / ".hgk" / "knowledge" / "QUARANTINE_DISPOSITION_R3.json")
                          .read_text(encoding="utf-8"))
        rep = json.loads((ROOT / ".hgk" / "knowledge" / "KNOWLEDGE_READY_REPORT.json")
                          .read_text(encoding="utf-8"))
        quarantined = rep["knowledge_index_readback"]["quarantined"]
        self.assertEqual(len(disp["items"]), len(quarantined), "every quarantined source dispositioned")
        for it in disp["items"]:
            self.assertIn(it["owner_disposition"],
                          ("harmless_example", "secret", "poison", "UNDECIDED"))
            self.assertNotEqual(it["owner_disposition"], "UNDECIDED",
                                f"{it['source_id']} has no owner disposition")
            self.assertIn(it["decision"], ("safe-clean", "safe-reference", "quarantine"))
            self.assertTrue(it["owner_rationale"])
        d = disp["denominators"]
        self.assertEqual(d["undispositioned"], 0)
        self.assertEqual(d["dispositioned_this_round"], len(quarantined))
        # never pad: the physical number is reported as-is
        self.assertEqual(d["indexed_docs_physical"],
                         rep["gate_predicate"]["indexed_docs"])
        self.assertEqual(d["quarantined_by_sanitizer"], rep["gate_predicate"]["quarantined"])

    def test_no_false_positive_release_proof_is_recorded(self) -> None:
        disp = json.loads((ROOT / ".hgk" / "knowledge" / "QUARANTINE_DISPOSITION_R3.json")
                          .read_text(encoding="utf-8"))
        proof = disp["false_positive_release_proof"]
        self.assertTrue(proof["released_items_evidence_clean"])
        self.assertEqual(proof["inconsistencies"], [])
        self.assertTrue(proof["calibration"]["controls_hold"],
                        "the calibration controls must hold: positive released, malicious not")
        by_id = {s["id"]: s for s in proof["calibration"]["samples"]}
        self.assertFalse(by_id["NEG-POISON-UNFRAMED-INJECTION"]["result"]["released"])
        self.assertFalse(by_id["NEG-LIVE-SECRET"]["result"]["released"])
        self.assertEqual(by_id["EDGE-UNDECIDED"]["result"]["decision"], "quarantine")
        self.assertEqual(disp["controls"]["controls_disabled"], [])

    def test_loss_record_covers_the_necessary_sources(self) -> None:
        disp = json.loads((ROOT / ".hgk" / "knowledge" / "QUARANTINE_DISPOSITION_R3.json")
                          .read_text(encoding="utf-8"))
        loss = disp["loss_record"]
        docs = {s["doc"] for s in loss["necessary_sources"]}
        self.assertEqual(docs, {"PIPD_LS_DOC-01", "PIPD_LS_DOC-08", "PIPD_LS_DOC-09"})
        for s in loss["necessary_sources"]:
            self.assertIn(s["decision"], ("safe-clean", "safe-reference", "quarantine"))
            self.assertIn("residual_loss", s)
        if loss["necessary_sources_still_excluded"]:
            self.assertNotIn("NONE", loss["capability_loss"],
                             "an excluded necessary source requires a full loss record")
        else:
            self.assertEqual(loss["capability_loss"],
                             "NONE — DOC-01/08/09 all carry an explicit decision and none "
                             "remains excluded.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
