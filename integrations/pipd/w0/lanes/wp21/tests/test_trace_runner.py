# -*- coding: utf-8 -*-
"""WP-FHS-21 unittest suite.

POS: 96/96 expected==observed, S1..S5 fields complete, E26 direction correct,
288 archived observations reconcile, 84/25/22 counts, W1..W4 handoff.
NEG: four concrete codes --
     FIRSTFAIL_MISMATCH         (expected_firstfail tampered)
     SEAM_FIELD_MISSING         (seam missing permission)
     DAG_E26_DIRECTION_INVALID  (E26 reversed)
     WAVE_COUNT_MISMATCH        (wave/card count off)

All source reads are read-only; the suite never writes outside the lane.
Self-claim is AUTHOR_LOCAL_TEST (not Native, not WP19).
"""

import copy
import inspect
import json
import os
import sys
import unittest

LANE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LANE_DIR not in sys.path:
    sys.path.insert(0, LANE_DIR)

import trace_runner as tr  # noqa: E402

SOURCE_ROOT = os.environ.get(
    "FHS_W0_SOURCE_ROOT",
    "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
    "Semantic World OS Fabric/FHS／FHS-MSC／SBL/FHS/PIPD-LS-PKG/定案/W0/"
    "FHS_PIPD-LS-PKG_W0_R4C",
)


def _load(name):
    return tr.load_json(os.path.join(SOURCE_ROOT, name))


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = _load("ORACLE96_CONTRACTS.json")
        cls.archived = _load("ORACLE96_REPLAY_RAW.json")
        cls.swap_raw = _load("ORACLE96_SWAP_RAW.json")
        cls.seams_in = _load("SEAM_CONTRACTS.json")
        cls.program = _load("PROGRAM_WP22_DAG36.json")
        cls.design84 = _load("DESIGN84_WAVE_JOIN.json")
        cls.trace22 = _load("W0_REQUIRED22_TRACE.json")
        cls.trace_graph = _load("TRACE_GRAPH.json")
        cls.matrix = _load("W1_W4_IMPACT_AND_HOLD_MATRIX.json")
        # one full in-memory run (write=False: nothing leaves the lane)
        cls.result = tr.run_all(SOURCE_ROOT, None, write=False)


# --------------------------------------------------------------------------
# POS
# --------------------------------------------------------------------------

class TestOracleFixtures(Base):
    def test_96_typed_fixtures(self):
        fixtures = self.result["fixtures"]["fixtures"]
        self.assertEqual(len(fixtures), 96)
        self.assertEqual(self.result["fixtures"]["contracts_typed"], 96)
        required = {"case_id", "case_type", "subject_ref",
                    "expected_firstfail", "oracle_ref"}
        for fx in fixtures:
            self.assertTrue(required.issubset(fx), fx["case_id"])
            self.assertTrue(fx["subject_ref"]["source_sha"])
            self.assertTrue(fx["oracle_ref"]["source_parent"])
            self.assertTrue(fx["pos_fixture"]["sha_match"], fx["case_id"])
        self.assertEqual(sum(1 for f in fixtures
                             if f["pos_fixture"]["sha_match"]), 96)

    def test_case_type_and_oracle_type_coverage(self):
        counts = self.result["fixtures"]["case_type_counts"]
        self.assertEqual(len(counts), 12)
        self.assertEqual(set(counts.values()), {8})
        ocounts = self.result["fixtures"]["oracle_type_counts"]
        self.assertEqual(len(ocounts), 8)
        self.assertEqual(set(ocounts.values()), {12})

    def test_96_expected_equals_observed(self):
        run_raw = self.result["run_raw"]
        self.assertEqual(run_raw["rows_total"], 96)
        self.assertEqual(len(run_raw["rows"]), 96)
        self.assertEqual(run_raw["rows_expected_equal_observed"], 96)
        self.assertEqual(run_raw["base_runs_static_pass"], 96)
        for row in run_raw["rows"]:
            self.assertEqual(row["verdict"], "MATCH", row["case_id"])
            self.assertEqual(row["observed_firstfail"],
                             row["expected_firstfail"], row["case_id"])
            self.assertNotEqual(row["observed_firstfail"],
                                "MUTATION_OBSERVATION_DIVERGENCE")
            self.assertEqual(row["base_run_state"], tr.PASS_MARKER)
            self.assertEqual(row["observed_source"],
                             "ADAPTER:" + tr.ADAPTER_ID)

    def test_observed_is_not_copied_from_expected(self):
        probe = self.result["run_raw"]["independence_probe"]
        self.assertTrue(probe["observed_vector_identical"])
        self.assertEqual(probe["poisoned_rows_now_mismatching"], 96)
        params = list(inspect.signature(tr.adapter_evaluate).parameters)
        self.assertEqual(params, ["fixture", "descriptor", "mutation"])
        self.assertNotIn("expected", " ".join(params))
        self.assertIn("ORACLE96_CONTRACTS.expected_first_fail",
                      tr.ADAPTER["excluded_inputs"])
        self.assertEqual(len(tr.ADAPTER["class_firstfail"]), 12)


class TestReplayReconcile(Base):
    def test_288_archived_rows_consistent(self):
        rec = self.result["reconcile"]
        self.assertEqual(rec["summary"]["archived_rows"], 288)
        self.assertEqual(len(rec["rows"]), 288)
        self.assertEqual(rec["summary"]["consistent_rows"], 288)
        self.assertEqual(rec["summary"]["inconsistent_rows"], 0)
        self.assertEqual(rec["summary"]["fixture_sha_matches"], 288)
        self.assertEqual(rec["summary"]["cases"], 96)
        self.assertEqual(rec["summary"]["cases_fully_consistent"], 96)
        self.assertEqual(rec["holds"], [])
        types = {r["archived_type"] for r in rec["rows"]}
        self.assertEqual(types, {"POS", "DOMAIN_NEG", "ORACLE_NEG"})
        for case in rec["per_case"]:
            self.assertEqual(case["rows"], 3, case["case_id"])
            self.assertEqual(case["status"], "CONSISTENT", case["case_id"])


class TestSeams(Base):
    def test_s1_s5_fields_complete(self):
        seams = self.result["seams"]
        self.assertEqual(seams["seams_total"], 5)
        self.assertEqual(seams["seams_sealed"], 5)
        self.assertEqual([s["seam"] for s in seams["seams"]],
                         ["S1", "S2", "S3", "S4", "S5"])
        for row in seams["seams"]:
            self.assertEqual(row["verdict"], "SEAM_SEALED", row["seam"])
            self.assertEqual(row["missing_contract_fields"], [], row["seam"])
            self.assertEqual(row["missing_fixture_fields"], [], row["seam"])
            self.assertTrue(row["abi"]["original_abi"], row["seam"])
            self.assertFalse(row["abi"]["runtime_bound"])
            self.assertTrue(row["reader"]["original_reader"], row["seam"])
            self.assertTrue(row["reader"]["reader_source_pin"], row["seam"])
            self.assertTrue(row["effect_permission"]["typed_input"],
                            row["seam"])
            self.assertTrue(row["effect_permission"]["typed_output"],
                            row["seam"])
            self.assertTrue(row["effect_permission"]["stop"], row["seam"])
            self.assertTrue(row["effect_permission"]["rollback"], row["seam"])
            self.assertTrue(row["firstfail"]["expected_first_fail"], row["seam"])
            self.assertTrue(row["resume"]["resume"], row["seam"])
            self.assertTrue(row["pos_neg"]["negative_fixture_present"])
            self.assertTrue(row["pos_neg"]["expected_raw_present"])
            self.assertFalse(row["effect_permission"]["permit_issued"])
            self.assertTrue(row["firstfail"]["consistent"])

    def test_s4_permission_declared_and_s5_principal_separated(self):
        by_seam = {s["seam"]: s for s in self.result["seams"]["seams"]}
        self.assertEqual(by_seam["S4"]["effect_permission"]["permission_value"],
                         "NONE_GRANTED")
        self.assertTrue(by_seam["S4"]["effect_permission"]["permission_declared"])
        self.assertTrue(by_seam["S5"]["effect_permission"]["principal_separated"])


class TestProgramDag(Base):
    def test_22_wp_36_edges(self):
        dag = self.result["dag"]
        self.assertEqual(dag["work_packages"], 22)
        self.assertEqual(dag["edges"], 36)
        self.assertEqual(dag["verdict"], "DAG_SEALED")
        self.assertEqual(dag["codes"], [])
        self.assertTrue(dag["acyclic"])
        self.assertEqual(sum(dag["edge_wave_counts"].values()), 36)

    def test_e26_direction(self):
        dag = self.result["dag"]
        self.assertEqual(dag["e26"]["predecessor"], "WP-FHS-19")
        self.assertEqual(dag["e26"]["successor"], "WP-FHS-14")
        self.assertTrue(dag["e26"]["direction_valid"])
        self.assertEqual(dag["e26"]["wave"], "W0→W4")
        self.assertTrue(dag["e26"]["operation_binding_present"])
        self.assertEqual(dag["e26"]["firstfail"], "WP19_ORIGINAL_OUTPUT_MISSING")


class TestDesign84(Base):
    def test_84_cards_25_join_22_trace(self):
        waves = self.result["waves"]
        self.assertEqual(waves["cards_total"], 84)
        self.assertEqual(waves["join_affected_25"], 25)
        self.assertEqual(waves["not_blocked_59"], 59)
        self.assertEqual(waves["w0_trace22"], 22)
        self.assertEqual(len(self.trace22), 22)
        self.assertTrue(waves["w0_idset_equal"])
        self.assertEqual(waves["verdict"], "WAVE_JOIN_SEALED")
        self.assertEqual(waves["codes"], [])
        self.assertEqual(sum(waves["wave_counts"].values()), 84)
        self.assertEqual(set(waves["wave_counts"]), {"W0", "W1", "W2", "W3", "W4"})
        self.assertEqual(waves["consumer_verification_wave_unbound"], 84)
        self.assertIn("H-WAVE-25", waves["hold_ids"])


class TestTraceClosure(Base):
    def test_author_static_only(self):
        closure = self.result["closure"]
        self.assertEqual(closure["scope"], "AUTHOR_STATIC")
        self.assertEqual(closure["trace_closure"], "AUTHOR_STATIC")
        self.assertFalse(closure["wp19_done"])
        self.assertFalse(closure["wp19_claimed"])
        self.assertEqual(closure["native"], "NOT_RUN")
        self.assertEqual(closure["closure_state"],
                         "AUTHOR_STATIC_TRACE_CLOSED")
        self.assertEqual(closure["trace_graph"]["edges"], 110)
        self.assertEqual(closure["trace_graph"]["reverse_edges"], 110)
        self.assertEqual(closure["trace_graph"]["requirements"], 22)
        self.assertEqual(closure["trace_graph"]["edges_per_requirement"], 4)
        self.assertTrue(closure["trace_graph"]["closure_complete"])
        self.assertEqual(closure["e26"]["status"],
                         "UNSATISFIED_WP19_RAW_MISSING")

    def test_counts_block(self):
        counts = self.result["closure"]["counts"]
        self.assertEqual(counts["oracle96"], 96)
        self.assertEqual(counts["replay288"], 288)
        self.assertEqual(counts["wp22"], 22)
        self.assertEqual(counts["edge36"], 36)
        self.assertEqual(counts["card84"], 84)
        self.assertEqual(counts["wave_join25"], 25)
        self.assertEqual(counts["seam5"], 5)
        self.assertEqual(counts["trace22"], 22)


class TestSwapAndHandoff(Base):
    def test_48_swap_rows_mismatch(self):
        swap = self.result["swap"]
        self.assertEqual(swap["rows"], 48)
        self.assertEqual(swap["matched"], 48)
        self.assertEqual(swap["code"], "CASE_TYPE_OR_SCOPE_MISMATCH")
        for row in swap["detail"]:
            self.assertEqual(row["rerun_observed"],
                             "CASE_TYPE_OR_SCOPE_MISMATCH", row["case"])

    def test_w1_w4_handoff_fields(self):
        handoff = self.result["handoff"]
        self.assertEqual(handoff["waves_total"], 4)
        self.assertEqual([w["wave"] for w in handoff["waves"]],
                         ["W1", "W2", "W3", "W4"])
        card_total = 0
        for wave in handoff["waves"]:
            for key in ("next_reader", "required_raw", "resume_predicate",
                        "affected_artifacts"):
                self.assertTrue(wave[key], "%s %s" % (wave["wave"], key))
            self.assertEqual(wave["original_reader_ack"], "NOT_OBSERVED")
            self.assertEqual(wave["native"], "NOT_RUN")
            self.assertTrue(wave["affected_artifacts"]["design84_card_ids"])
            card_total += wave["affected_artifacts"]["design84_card_count"]
        self.assertEqual(card_total, 62)
        self.assertEqual(handoff["cards_in_scope"], 62)
        self.assertEqual(handoff["w0_cards_not_in_scope"], 22)
        self.assertEqual(handoff["cards_in_scope"] +
                         handoff["w0_cards_not_in_scope"], 84)


# --------------------------------------------------------------------------
# NEG
# --------------------------------------------------------------------------

class TestNegFirstFail(Base):
    def test_tampered_expected_yields_firstfail_mismatch(self):
        row = copy.deepcopy(self.result["run_raw"]["rows"][0])
        self.assertEqual(row["verdict"], "MATCH")
        codes = sorted(tr.ADAPTER["class_firstfail"].values())
        wrong = next(c for c in codes if c != row["expected_firstfail"])
        row["expected_firstfail"] = wrong
        verdict = tr.firstfail_verdict(row["expected_firstfail"],
                                       row["observed_firstfail"])
        self.assertEqual(verdict, "FIRSTFAIL_MISMATCH")
        self.assertEqual(verdict, tr.FIRSTFAIL_MISMATCH)

    def test_positive_fixture_against_violation_expectation(self):
        contract = self.contracts[0]
        fixture = tr.load_json(os.path.join(
            SOURCE_ROOT, "fixtures/%s.pos.json" % contract["case_id"]))
        observation = tr.adapter_evaluate(fixture, tr._descriptor(contract))
        # the sound fixture passes, so demanding the violation code must mismatch
        self.assertEqual(observation["observed_firstfail"], tr.PASS_MARKER)
        self.assertEqual(
            tr.firstfail_verdict(contract["expected_first_fail"],
                                 observation["observed_firstfail"]),
            "FIRSTFAIL_MISMATCH")

    def test_unobserved_and_missing_paths(self):
        self.assertEqual(tr.firstfail_verdict("X", None),
                         "FIRSTFAIL_UNOBSERVED")
        self.assertEqual(tr.firstfail_verdict("X", ""),
                         "FIRSTFAIL_UNOBSERVED")
        self.assertEqual(tr.firstfail_verdict(None, "X"),
                         "FIRSTFAIL_EXPECTED_MISSING")


class TestNegSeam(Base):
    def _s4(self):
        contract = next(c for c in self.seams_in if c["seam"] == "S4")
        req = tr.load_json(os.path.join(SOURCE_ROOT, contract["input_fixture"]))
        neg = tr.load_json(os.path.join(SOURCE_ROOT,
                                        contract["negative_fixture"]))
        raw = tr.load_json(os.path.join(SOURCE_ROOT,
                                        contract["expected_raw_fixture"]))
        return contract, req, neg, raw

    def test_missing_permission_yields_seam_field_missing(self):
        contract, req, neg, raw = self._s4()
        self.assertEqual(
            tr.validate_seam_contract(contract, req, neg, raw)["verdict"],
            "SEAM_SEALED")
        broken = copy.deepcopy(req)
        del broken["permission"]
        result = tr.validate_seam_contract(contract, broken, neg, raw)
        self.assertEqual(result["verdict"], "SEAM_FIELD_MISSING")
        self.assertEqual(result["verdict"], tr.SEAM_FIELD_MISSING)
        self.assertIn("permission", result["missing_fixture_fields"])
        self.assertFalse(result["effect_permission"]["permission_declared"])

    def test_missing_contract_effect_surface(self):
        contract, req, neg, raw = self._s4()
        broken = copy.deepcopy(contract)
        del broken["typed_output"]
        result = tr.validate_seam_contract(broken, req, neg, raw)
        self.assertEqual(result["verdict"], "SEAM_FIELD_MISSING")
        self.assertIn("typed_output", result["missing_contract_fields"])

    def test_s5_principal_collapse_is_named(self):
        contract = next(c for c in self.seams_in if c["seam"] == "S5")
        req = tr.load_json(os.path.join(SOURCE_ROOT, contract["input_fixture"]))
        neg = tr.load_json(os.path.join(SOURCE_ROOT,
                                        contract["negative_fixture"]))
        raw = tr.load_json(os.path.join(SOURCE_ROOT,
                                        contract["expected_raw_fixture"]))
        collapsed = copy.deepcopy(req)
        collapsed["checker"] = collapsed["maker"]
        result = tr.validate_seam_contract(contract, collapsed, neg, raw)
        self.assertEqual(result["verdict"], "SEAM_PRINCIPAL_SEPARATION_BROKEN")


class TestNegDag(Base):
    def test_reversed_e26_yields_direction_invalid(self):
        self.assertEqual(tr.validate_program_dag(self.program)["verdict"],
                         "DAG_SEALED")
        broken = copy.deepcopy(self.program)
        edge = next(e for e in broken["edges"] if e["id"] == "E26")
        edge["predecessor"], edge["successor"] = (
            edge["successor"], edge["predecessor"])
        result = tr.validate_program_dag(broken)
        self.assertEqual(result["verdict"], tr.DAG_E26_DIRECTION_INVALID)
        self.assertEqual(result["verdict"], "DAG_E26_DIRECTION_INVALID")
        self.assertFalse(result["e26"]["direction_valid"])
        self.assertEqual(result["e26"]["predecessor"], "WP-FHS-14")

    def test_deleted_edge_and_wp_count(self):
        broken = copy.deepcopy(self.program)
        broken["edges"] = [e for e in broken["edges"] if e["id"] != "E26"]
        codes = [c["code"] for c in tr.validate_program_dag(broken)["codes"]]
        self.assertIn("DAG_EDGE_COUNT_MISMATCH", codes)
        self.assertIn(tr.DAG_E26_DIRECTION_INVALID, codes)


class TestNegWaves(Base):
    def test_dropped_card_yields_wave_count_mismatch(self):
        broken = copy.deepcopy(self.design84)[:-1]
        wp_ids = [w["id"] for w in self.program["work_packages"]]
        result = tr.validate_design_waves(broken, self.trace22, wp_ids)
        self.assertEqual(result["verdict"], tr.WAVE_COUNT_MISMATCH)
        self.assertEqual(result["verdict"], "WAVE_COUNT_MISMATCH")
        self.assertEqual(result["codes"][0]["detail"]["field"], "cards_total")
        self.assertEqual(result["codes"][0]["detail"]["found"], 83)

    def test_join_count_drift_yields_wave_count_mismatch(self):
        broken = copy.deepcopy(self.design84)
        victim = next(c for c in broken
                      if c["scope_condition"] == "JOIN_AMBIGUOUS_AFFECTED")
        victim["scope_condition"] = "NO_WP_WAVE_CONFLICT"
        wp_ids = [w["id"] for w in self.program["work_packages"]]
        result = tr.validate_design_waves(broken, self.trace22, wp_ids)
        self.assertEqual(result["verdict"], "WAVE_COUNT_MISMATCH")
        fields = [c["detail"]["field"] for c in result["codes"]]
        self.assertIn("join_affected_25", fields)

    def test_trace22_drift_yields_wave_count_mismatch(self):
        broken = copy.deepcopy(self.trace22)[:-1]
        wp_ids = [w["id"] for w in self.program["work_packages"]]
        result = tr.validate_design_waves(self.design84, broken, wp_ids)
        self.assertEqual(result["verdict"], "WAVE_COUNT_MISMATCH")
        fields = [c["detail"].get("field") for c in result["codes"]
                  if isinstance(c.get("detail"), dict)]
        self.assertIn("w0_required22", fields)


if __name__ == "__main__":
    unittest.main(verbosity=2)
