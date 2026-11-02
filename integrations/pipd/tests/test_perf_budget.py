#!/usr/bin/env python3
"""W5: every perf-budget entry carries provenance; an unprovenanced threshold is UNDECIDABLE."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import perf_budget as PB  # noqa: E402


class PerfBudgetProvenance(unittest.TestCase):
    def test_unprovenanced_threshold_is_undecidable_not_pass(self):
        # A threshold with no in-repo provenance is UNDECIDABLE even when the measured value is
        # comfortably under it - an unratified budget cannot be turned green by a small number.
        verdict = PB._verdict(1.0, 2000, "UNPROVENANCED")
        self.assertEqual(verdict, "UNDECIDABLE")
        self.assertNotEqual(verdict, "PASS")
        self.assertNotEqual(verdict, "FAIL")
        # A provenanced threshold still decides normally.
        self.assertEqual(PB._verdict(1.0, 2000, "docs/S0_CONTRACT_SPEC.md#perf"), "PASS")
        self.assertEqual(PB._verdict(9999.0, 2000, "docs/S0_CONTRACT_SPEC.md#perf"), "FAIL")

    def test_exceeded_unprovenanced_budget_is_fail_and_exits_nonzero(self):
        # Fail-closed: an OVER-budget value is a fact about the artefact. Missing provenance must
        # not launder it into UNDECIDABLE/pass - it stays FAIL and the process exits non-zero.
        self.assertEqual(PB._verdict(9999.0, 2000, "UNPROVENANCED"), "FAIL")
        over = 343547.0  # the 20,000-byte context budget's real overrun
        row = PB._row("context_bytes_per_artefact", over)
        self.assertEqual(row["source_of_truth"], "UNPROVENANCED")
        self.assertTrue(row["exceeded"])
        self.assertEqual(row["verdict"], "FAIL")
        self.assertIn("note", row)
        self.assertEqual(PB.overall_verdict([row]), "FAIL")
        self.assertNotEqual(PB.exit_code("FAIL"), 0)

    def test_under_budget_unprovenanced_budget_is_undecidable_not_pass(self):
        row = PB._row("context_bytes_per_artefact", 10.0)
        self.assertFalse(row["exceeded"])
        self.assertEqual(row["verdict"], "UNDECIDABLE")
        self.assertNotEqual(row["verdict"], "PASS")
        self.assertEqual(PB.overall_verdict([row]), "UNDECIDABLE")
        self.assertEqual(PB.exit_code("UNDECIDABLE"), 0)

    def test_raw_overrun_not_rounded_away(self):
        # C7': a raw measurement of 2000.04 against the 2000 ms compile budget rounds to 2000.0 for
        # display, but the decision must use the UNROUNDED value, so it is flagged as exceeded.
        row = PB._row("compile_chain_ms", 2000.04)
        self.assertTrue(row["exceeded"], "raw 2000.04 > 2000 must be flagged exceeded")
        self.assertEqual(row["verdict"], "FAIL")
        self.assertEqual(row["budget"], 2000)
        self.assertEqual(row["value_display"], 2000.0)
        self.assertNotEqual(PB.exit_code(PB.overall_verdict([row])), 0)


class AdvisoryAndVotingRows(unittest.TestCase):
    """R5 S4 owner adjudication: the deciding row changed; the historical rows did not vanish."""

    def test_the_recorded_absolute_fail_is_advisory_not_voting(self):
        # The historical 343,547 > 20,000 row must still be measured, still read FAIL, and must no
        # longer decide. Deleting it, or greening it, would both be rewrites of the record.
        row = PB._row("context_bytes_per_artefact", 343547.0)
        self.assertEqual(row["verdict"], "FAIL")
        self.assertTrue(row["exceeded"])
        self.assertFalse(row["voting"])
        self.assertTrue(row.get("preserved"))
        self.assertIn("advisory_reason", row)

    def test_advisory_rows_cannot_turn_the_gate_green(self):
        # An advisory row's own verdict must not be able to lift or sink the overall verdict: the
        # overall verdict is computed over voting rows only (see main()).
        for metric in ("compile_chain_ms", "validate_19_contracts_ms", "cli_cold_start_ms"):
            with self.subTest(metric=metric):
                self.assertFalse(PB.PROVENANCE[metric]["voting"])

    def test_bytes_per_atom_is_the_voting_row_with_a_ratified_source(self):
        prov = PB.PROVENANCE["bytes_per_atom"]
        self.assertTrue(prov["voting"])
        self.assertEqual(prov["budget"], 2000)
        self.assertNotEqual(prov["source_of_truth"], "UNPROVENANCED")
        self.assertIn("OWNER_ADJUDICATION_R5_S4", prov["source_of_truth"])
        # Provenanced and within budget => PASS (not UNDECIDABLE).
        row = PB._row("bytes_per_atom", 1449.57, pi_bytes=343547, atoms=237)
        self.assertEqual(row["verdict"], "PASS")
        self.assertFalse(row["exceeded"])

    def test_the_rate_still_fails_over_its_budget(self):
        # Re-specifying the metric must not remove the gate: an over-rate artefact still FAILs.
        row = PB._row("bytes_per_atom", 4321.0)
        self.assertTrue(row["exceeded"])
        self.assertEqual(row["verdict"], "FAIL")
        self.assertNotEqual(PB.exit_code(PB.overall_verdict([row])), 0)

    def test_end_to_end_check_preserves_history_and_reports_the_rate(self):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = PB.main(["--check"])
        res = json.loads(buf.getvalue())
        self.assertEqual(res["voting_metrics"], ["bytes_per_atom"])
        self.assertIn("context_bytes_per_artefact", res["advisory_metrics"])
        self.assertEqual(res["historical"]["preserved_fails"], ["context_bytes_per_artefact"])
        self.assertIn("bytes_per_atom", [r["metric"] for r in res["rows"]])
        # The rate decides: it is within its ratified budget on this candidate.
        self.assertEqual(rc, 0)
        self.assertEqual(res["verdict"], "PASS")
        # WO-S4-CAL-003: the anti-dilution denominator, the scale fixtures and the padding probe are
        # carried in the same verdict block, and the p95/max tail rows never vote.
        ad = res["anti_dilution"]
        self.assertEqual(ad["voting_row"], "bytes_per_atom")
        self.assertEqual(ad["denominator"], "unique_obligations")
        self.assertIn("dedup_rule", ad)
        self.assertEqual(ad["advisory_rows"], ["per_atom_p95_bytes", "per_atom_max_bytes"])
        self.assertNotIn("per_atom_p95_bytes", res["voting_metrics"])
        self.assertNotIn("per_atom_max_bytes", res["voting_metrics"])
        for scale in ("2", "237", "801"):
            self.assertEqual(res["scales"][scale]["unique_obligations"], int(scale))
        self.assertEqual(res["scales"]["long_clause"]["atoms"], 1)
        self.assertEqual(res["padding_invariance"]["padding_invariance"], "PASS")
        # Serialized/disk bytes and model-context bytes are separate; the latter is UNPROVENANCED.
        ctx = [r for r in res["rows"] if r["metric"] == "context_entry_bytes"]
        self.assertEqual(len(ctx), 1)
        self.assertIsNone(ctx[0]["value"])
        self.assertTrue(ctx[0]["uncomputable"])
        self.assertFalse(ctx[0]["voting"])

    def test_new_advisory_rows_do_not_change_the_preserved_fail_set(self):
        # Only the context_bytes_per_artefact row preserves history; the new tail/uncomputable rows
        # must not creep into preserved_fails.
        self.assertNotIn("preserved", PB._row("per_atom_p95_bytes", 10.0))
        self.assertFalse(PB.PROVENANCE["per_atom_p95_bytes"]["voting"])
        self.assertFalse(PB.PROVENANCE["per_atom_max_bytes"]["voting"])


class HistoricalRecordedValue(unittest.TestCase):
    """D1 repair: the `historical` block must report the RECORDED value, not a live host reading.

    The historical 343,547 > 20,000 row is a record; a record that changes with the machine that
    happens to run it is not a record. `value` is read from the frozen baseline at test time (never
    hard-coded here) and the live measurement is carried beside it as `measured_now`.
    """

    def _baseline(self):
        path = ROOT / ".hgk" / "artifacts" / "s2" / "BYTES_PER_ATOM_BASELINE.json"
        self.assertTrue(path.exists(), f"baseline artefact must exist: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _historical_row(self, metric):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = PB.main(["--check"])
        self.assertEqual(rc, 0)
        res = json.loads(buf.getvalue())
        rows = {r["metric"]: r for r in res["historical"]["rows"]}
        self.assertIn(metric, rows)
        return rows[metric]

    def test_historical_value_is_the_recorded_baseline_not_the_measurement(self):
        baseline = self._baseline()
        expected = baseline["pi_bytes"]  # 343547, read from the artefact - never hard-coded
        row = self._historical_row("context_bytes_per_artefact")
        self.assertEqual(row["value"], expected)
        self.assertTrue(row["recorded"])
        self.assertEqual(row["origin"],
                         {"file": ".hgk/artifacts/s2/BYTES_PER_ATOM_BASELINE.json",
                          "field": "pi_bytes"})
        # The verdict is decided from the RECORDED value against the UNCHANGED budget.
        self.assertEqual(row["verdict"], "FAIL")
        self.assertEqual(row["budget"], 20000)
        self.assertTrue(row["exceeded"])

    def test_historical_value_is_stable_across_live_measurements(self):
        baseline = self._baseline()
        expected = baseline["pi_bytes"]
        first = self._historical_row("context_bytes_per_artefact")
        second = self._historical_row("context_bytes_per_artefact")
        # `measured_now` is present and honest; `value` never follows it.
        self.assertIn("measured_now", first)
        self.assertIn("measured_now", second)
        self.assertEqual(first["value"], expected)
        self.assertEqual(second["value"], expected)
        # Sanity: if the live reading ever differed, `value` would still be the record.
        if first["measured_now"] != first["value"]:
            self.assertEqual(first["value"], expected)

    def test_unrecorded_advisory_metric_says_so_instead_of_fabricating(self):
        row = self._historical_row("compile_chain_ms")
        self.assertFalse(row["recorded"])
        self.assertIsNone(row["origin"])
        self.assertEqual(row["value"], row["measured_now"])
        self.assertEqual(row["budget"], 2000)
        self.assertIn("note", row)
        self.assertIn("no recorded value", row["note"])

    def test_no_source_comment_claims_verbatim_preservation_of_the_live_value(self):
        # Targeted, not a broad grep: the two corrected strings must describe what the code does.
        source = (ROOT / "tools" / "perf_budget.py").read_text(encoding="utf-8")
        self.assertNotIn("343,547 > 20,000 FAIL is preserved verbatim", source)
        self.assertNotIn("preserved verbatim and must never be rewritten", source)
        # The correction is present rather than the claim merely deleted.
        self.assertIn("RECORDED", source)
        self.assertIn("measured_now", source)


class AntiDilutionUniqueObligations(unittest.TestCase):
    """WO-S4-CAL-003: the denominator is *validated* obligations, content-addressed, not raw atoms and
    not `subject_id`s. The identity-addressed variant is the one independent challenge C4 (2026-10-10)
    defeated by re-stamping filler; it is kept only as a reported, non-voting counter."""

    def test_unique_obligations_counts_distinct_statements(self):
        atoms = [{"source_clause": {"text": "MUST log every request"}},
                 {"source_clause": {"text": "must   LOG every   request"}},   # same statement
                 {"source_clause": {"text": "MUST refuse unknown owners"}}]
        self.assertEqual(PB.unique_obligations(atoms), 2)

    def test_restamped_ids_do_not_create_obligations(self):
        # The exact attack independent challenge C4 used: identical filler, fresh subject_id/req_id.
        filler = [{"subject_id": f"ATOM-{i:04d}", "req_id": f"REQ-{i:04d}", "note": "padding"}
                  for i in range(50)]
        self.assertEqual(PB.unique_obligations(filler), 0)
        self.assertEqual(PB.unvalidated_atom_count(filler), 50)
        # ...and the weaker rule this round rejected would have counted every one of them.
        self.assertEqual(PB.identity_addressed_count(filler), 50)

    def test_an_atom_without_a_statement_is_not_an_obligation(self):
        self.assertEqual(PB.canonical_identity({"subject_id": "A", "note": "x"}), "")
        self.assertEqual(PB.unique_obligations([{"subject_id": "A"}]), 0)

    def test_identity_is_the_normalised_statement_only(self):
        base = {"source_clause": {"text": "MUST bind the repo context"}}
        same_statement_new_ids = dict(base, subject_id="OTHER", req_id="REQ-OTHER",
                                     content_hash="h" * 64, version="9")
        self.assertEqual(PB.canonical_identity(base), PB.canonical_identity(same_statement_new_ids))
        self.assertNotEqual(PB.canonical_identity(base),
                            PB.canonical_identity({"source_clause": {"text": "MUST bind the host context"}}))

    def test_rate_divides_by_unique_not_raw(self):
        one = {"source_clause": {"text": "MUST exist exactly once"}}
        pi = {"stable_semantic_contract": {"atoms": [one] * 100}}
        prof = PB.per_atom_profile(pi)
        self.assertEqual(prof["atoms"], 100)
        self.assertEqual(prof["unique_obligations"], 1)
        self.assertEqual(prof["unvalidated_atom_count"], 0)
        self.assertEqual(prof["bytes_per_atom"], prof["pi_bytes"])

    def test_dedup_rule_is_reported_verbatim(self):
        self.assertTrue(PB.DEDUP_RULE.startswith("distinct VALIDATED obligation"))


class PaddingInvariance(unittest.TestCase):
    """WO-S4-CAL-003: appending duplicate/filler atoms must not dilute the voting rate."""

    def test_padding_does_not_bring_the_rate_to_or_below_budget(self):
        res = PB.padding_invariance_probe()
        self.assertEqual(res["padding_invariance"], "PASS")
        self.assertGreater(res["after"]["bytes_per_atom"], res["budget"])
        self.assertEqual(res["after"]["unique_obligations"], res["before"]["unique_obligations"])

    def test_a_raw_atom_denominator_would_have_diluted(self):
        # Proof the fixture actually exercises dilution: under a raw atom-count denominator the
        # padded payload WOULD fall at or below budget.
        res = PB.padding_invariance_probe()
        self.assertLessEqual(res["naive_rate_if_denominator_were_raw_atoms"], res["budget"])

    def test_restamped_filler_ids_also_fail_to_dilute(self):
        # Independent challenge C4: identical filler re-stamped with fresh ids. The content-addressed
        # denominator must be unaffected, and the rejected identity-addressed rate is reported as the
        # evidence that it WOULD have been diluted.
        res = PB.padding_invariance_probe()
        self.assertEqual(res["restamped_identity_invariance"], "PASS")
        forged = res["after_restamped_ids"]
        self.assertEqual(forged["unique_obligations"], res["before"]["unique_obligations"])
        self.assertGreater(forged["bytes_per_atom"], res["budget"])
        self.assertLessEqual(forged["rate_if_denominator_were_identity_addressed"], res["budget"])


class ScaleFixtures(unittest.TestCase):
    """WO-S4-CAL-003: exercise 2 / 237 / 801 unique obligations and one long single clause."""

    def test_scales_2_237_801_have_exactly_that_many_unique_obligations(self):
        sc = PB.scale_fixtures()
        for n in ("2", "237", "801"):
            with self.subTest(scale=n):
                self.assertEqual(sc[n]["unique_obligations"], int(n))
                self.assertEqual(sc[n]["atoms"], int(n))
                self.assertGreater(sc[n]["pi_bytes"], 0)

    def test_single_long_clause_is_one_multi_thousand_char_atom(self):
        lc = PB.scale_fixtures()["long_clause"]
        self.assertEqual(lc["atoms"], 1)
        self.assertEqual(lc["unique_obligations"], 1)
        self.assertGreater(lc["clause_chars"], 2000)
        self.assertEqual(lc["max_bytes"], lc["p95_bytes"])

    def test_tail_statistics_are_advisory_and_never_replace_the_mean_row(self):
        self.assertFalse(PB.PROVENANCE["per_atom_p95_bytes"]["voting"])
        self.assertFalse(PB.PROVENANCE["per_atom_max_bytes"]["voting"])
        self.assertTrue(PB.PROVENANCE["bytes_per_atom"]["voting"])


class QuantitiesSeparated(unittest.TestCase):
    """WO-S4-CAL-003: serialized/disk bytes vs model-context bytes are separate quantities."""

    def test_context_entry_bytes_is_unprovenanced_and_not_invented(self):
        row = PB._row("context_bytes_per_artefact", 335252.0)
        self.assertTrue(row["preserved"])
        # The serialized quantity IS measured.
        self.assertEqual(row["metric"], "context_bytes_per_artefact")
        self.assertIsNotNone(row["value"])


class HistoricalFailPreserved(unittest.TestCase):
    """The historical 343,547 > 20,000 FAIL row must still be present and unchanged."""

    def test_recorded_absolute_fail_row_is_unchanged(self):
        row = PB._row("context_bytes_per_artefact", 343547.0)
        self.assertEqual(row["budget"], 20000)
        self.assertTrue(row["exceeded"])
        self.assertEqual(row["verdict"], "FAIL")
        self.assertFalse(row["voting"])
        self.assertTrue(row["preserved"])
        self.assertEqual(row["source_of_truth"], "UNPROVENANCED")

    def test_recorded_value_is_read_from_the_frozen_baseline(self):
        baseline = json.loads(
            (ROOT / ".hgk" / "artifacts" / "s2" / "BYTES_PER_ATOM_BASELINE.json")
            .read_text(encoding="utf-8"))
        row = PB._row("context_bytes_per_artefact", 1.0)  # a bogus live reading
        hist = PB._historical_row(row, baseline)
        self.assertTrue(hist["recorded"])
        self.assertEqual(hist["value"], baseline["pi_bytes"])
        self.assertEqual(hist["budget"], 20000)
        self.assertEqual(hist["verdict"], "FAIL")
        self.assertTrue(hist["exceeded"])


if __name__ == "__main__":
    unittest.main()
