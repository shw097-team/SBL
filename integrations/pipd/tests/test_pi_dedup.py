#!/usr/bin/env python3
"""W5: the PI source-clause de-duplication is proven (payload economy without semantic loss)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import pi_dedup_check as D  # noqa: E402
from pipd_ls_sp import requirements as R  # noqa: E402


class PiDedup(unittest.TestCase):
    def test_one_sources_entry_per_distinct_clause(self):
        pi = D.compile_after_pi()
        sources = pi["stable_semantic_contract"]["sources"]
        raw = D._raw_atoms()
        distinct = {(a["source_clause"]["file"], a["source_clause"]["clause_id"]) for a in raw}
        self.assertEqual(len(sources), len(distinct))
        self.assertEqual(len({s["source_id"] for s in sources}), len(sources), "one entry per clause")

    def test_no_atom_carries_source_text(self):
        pi = D.compile_after_pi()
        for a in pi["stable_semantic_contract"]["atoms"]:
            self.assertNotIn("source_text", a["source_clause"])
            self.assertTrue(a["source_clause"]["source_ref"], "every atom carries a source_ref")

    def test_resolve_source_clause_round_trips_pre_dedupe_locator(self):
        pi = D.compile_after_pi()
        sources = pi["stable_semantic_contract"]["sources"]
        raw_by_req = {a["req_id"]: a for a in D._raw_atoms()}
        checked = 0
        for atom in pi["stable_semantic_contract"]["atoms"]:
            want = raw_by_req[atom["req_id"]]["source_clause"]
            got = R.resolve_source_clause(atom, sources)
            self.assertEqual(got["source_text"], want["source_text"])
            self.assertEqual(got["source_sha256"], want["source_sha256"])
            self.assertEqual(got["span"], want["span"])
            checked += 1
        self.assertGreater(checked, 0)

    def test_check_fails_when_a_duplicated_source_text_is_reintroduced(self):
        self.assertEqual(D.evaluate(D.compile_after_pi())["first_fail"], "")
        mutated = D.compile_after_pi()
        atom = mutated["stable_semantic_contract"]["atoms"][0]
        atom["source_clause"]["source_text"] = atom["source_clause"]["text"]  # re-introduce the copy
        res = D.evaluate(mutated)
        self.assertNotEqual(res["first_fail"], "")
        original = D.compile_after_pi
        D.compile_after_pi = lambda: mutated
        try:
            self.assertEqual(D.main(["--check"]), 1)
        finally:
            D.compile_after_pi = original

    def test_atom_text_duplicating_its_table_entry_is_reported_as_residual(self):
        # W9: the resolved view still duplicates clause bytes whenever an atom's stored `text`
        # equals the source-table entry it points at. That is residual duplication and must be
        # reported as such (and never counted as eliminated).
        pi = D.compile_after_pi()
        ssc = pi["stable_semantic_contract"]
        table = {s["source_id"]: s for s in ssc["sources"]}
        duplicate = [a["req_id"] for a in ssc["atoms"]
                     if table.get(a["source_clause"].get("source_ref"))
                     and a["source_clause"].get("text")
                     == table[a["source_clause"]["source_ref"]].get("text")]
        self.assertTrue(duplicate, "expected some atom's text to equal its table entry")
        residual = D.residual_duplication(pi)
        self.assertEqual(residual["residual_duplicate_atoms"], len(duplicate))
        self.assertGreater(residual["residual_duplicated_bytes"], 0)
        after = D.measure_after(pi)
        self.assertEqual(after["residual_duplicate_atoms"], len(duplicate))
        self.assertGreater(after["residual_duplicated_bytes"], 0)
        # It is NOT counted as eliminated: the reported removal is scoped to `source_text`.
        self.assertEqual(after["duplicate_atoms"], 0)  # no atom carries source_text any more

    def test_pi_missing_a_baseline_atom_fails(self):
        # W9: de-duplication may re-key, never drop. A PI that lost an atom vs the pre-change
        # baseline must FAIL with first_fail set and a non-zero exit.
        baseline = D.baseline_req_ids()
        self.assertTrue(baseline)
        full = D.compile_after_pi()
        self.assertEqual(D.evaluate(full, baseline=baseline)["first_fail"], "")
        deleted = D.compile_after_pi()
        atoms = deleted["stable_semantic_contract"]["atoms"]
        dropped = atoms.pop(0)["req_id"]
        res = D.evaluate(deleted, baseline=baseline)
        self.assertNotEqual(res["first_fail"], "")
        self.assertTrue(any("lost" in f or dropped in f for f in res["fails"]), res["fails"])
        original = D.compile_after_pi
        D.compile_after_pi = lambda: deleted
        try:
            self.assertEqual(D.main(["--check"]), 1)
        finally:
            D.compile_after_pi = original

    def test_size_effect_is_reported_honestly_when_current_tree_is_larger(self):
        # W9: the current tree did not shrink the resolved PI. Atoms still carry a `text` locator,
        # so the resolved/materialized view is LARGER than the pre-change shape; that growth must
        # be reported as growth, not as payload economy.
        after = D.measure_after()
        before = D.measure_before()
        self.assertGreater(after["resolved_materialized_bytes"], before["pi_payload_bytes"])
        self.assertGreater(after["resolved_materialized_bytes"], after["pi_payload_bytes"])

    def test_synthetic_baseline_does_not_claim_shrinkage(self):
        # C6': when git / HEAD objects are unavailable the tool must NOT claim a shrinkage from a
        # current-code reconstruction. It declares the baseline synthetic and keeps the honest
        # current_tree_larger field.
        original = D.head_baseline
        D.head_baseline = lambda: None  # simulate "no git binary in this container"
        try:
            info = D.baseline_info()
        finally:
            D.head_baseline = original
        self.assertEqual(info["baseline_source"], "SYNTHETIC_FROM_CURRENT")
        self.assertFalse(info["shrinkage_claimed"])
        self.assertIn("current_tree_larger", info)
        # A real HEAD baseline (when available) names its source and the files it compiled.
        head = D.head_baseline()
        if head is not None:
            self.assertEqual(head["baseline_source"], "HEAD")
            self.assertEqual(set(head["head_sha256"]), set(D.HEAD_BASELINE_FILES))
            for digest in head["head_sha256"].values():
                self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
