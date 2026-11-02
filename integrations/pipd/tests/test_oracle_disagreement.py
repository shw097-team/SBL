"""Guard the ORACLE_DISAGREEMENT disposition (R-AUD-013 / FW-10): record, do not rewrite.

The rule this pins: when a lower-authority normalized rule table contradicts the upper
raw-evidence requirement, the disagreement is RAISED with both positions and locators, decided by
the authorised source (upper effective contract prevails), and the KP / upper-authority files are
NEVER silently edited. A genuine prohibition (calibration negative) must keep its MUST NOT
polarity — the mechanism may not become a blanket polarity flipper.
"""
from __future__ import annotations
import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

OD = json.loads((ROOT / ".hgk" / "knowledge" / "ORACLE_DISAGREEMENT_R3.json").read_text(encoding="utf-8"))
TT = json.loads((ROOT / ".hgk" / "artifacts" / "TT_REGISTER.json").read_text(encoding="utf-8"))

DISPUTED = {"GPTB-KP02-R04", "GPTB-KP11-R04", "GPTB-KP12-R04"}


class OracleDisagreementR3(unittest.TestCase):
    def setUp(self) -> None:
        self.entry = next(e for e in OD["entries"] if e["id"] == "OD-R3-001")

    def test_entry_records_both_positions_with_locators(self) -> None:
        inst = self.entry["position_a_lower_authority_normalized_kp_rows"]["clause_instances"]
        self.assertEqual({i["kp_rule_id"] for i in inst}, DISPUTED)
        for i in inst:
            self.assertTrue(i["locator"]["file"].endswith(".md"))
            self.assertGreater(i["locator"]["line"], 0)
            self.assertIn("MUST NOT", i["row_verbatim"], "the disputed polarity must be quoted verbatim")
            self.assertTrue(i["source_locator_cited_by_row"])
        upper = self.entry["position_b_upper_effective_contract"]
        self.assertGreaterEqual(len(upper["locators"]), 4)
        for loc in upper["locators"]:
            self.assertTrue(loc["locator"] and loc["verbatim"])
        self.assertTrue(upper["raw_upstream_anchors"])

    def test_resolved_by_the_authorised_source_without_rewriting(self) -> None:
        res = self.entry["resolution"]
        dec = self.entry["deciding_authority"]
        self.assertTrue(res["upper_effective_contract_prevails"])
        self.assertEqual(res["kp_files_edited"], [], "the KP must NOT be silently edited")
        self.assertEqual(res["upper_authority_files_edited"], [])
        self.assertIn("REJECTED", res["lower_authority_override"])
        self.assertIn("GPTB-DOC10#evidence-requirement-matrix", dec["decided_by"])
        self.assertTrue(dec["ratification_owner"])
        self.assertEqual(OD["controls"]["kp_files_edited"], [])
        self.assertEqual(OD["controls"]["upper_authority_files_edited"], [])
        # the raw-evidence requirement is operative for all three rows
        for row in res["disposition_per_row"]:
            self.assertEqual(row["disposition"], "POLARITY_DISPUTED_NORMALIZATION_DEFECT")
            self.assertTrue(row["operative_polarity"].startswith("MUST "))

    def test_calibration_negative_keeps_a_genuine_prohibition(self) -> None:
        cal = self.entry["calibration_negative_case"]
        self.assertIn("MUST NOT", cal["claimed_polarity"])
        self.assertIn("MUST NOT preserved", cal["expected"])
        self.assertTrue(cal["locator"])
        # the disputed set is exactly the three R04 rows: nothing else is flipped
        disputed = {r["kp_rule_id"] for r in self.entry["resolution"]["disposition_per_row"]}
        self.assertEqual(disputed, DISPUTED)

    def test_tt_row_registered_with_owner_state_and_close_criterion(self) -> None:
        rows = [t for t in TT["tts"] if t["id"] == "TT-ORACLE-DISAGREEMENT-KP-R04"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["class"], "ORACLE_DISAGREEMENT")
        self.assertTrue(row["owner"])
        self.assertEqual(row["state"], "OPEN", "final ratification belongs to the authorised source")
        self.assertTrue(row["raw_evidence"])
        self.assertTrue(row["close_criterion"])
        # and the PRE-W3 subject stays TEMP_CLOSED with its own owner (this round's other new row)
        pre = [t for t in TT["tts"] if t["id"] == "TT-PRE-W3-CROSS-PROJECT"]
        self.assertEqual(len(pre), 1)
        self.assertEqual(pre[0]["state"], "TEMP_CLOSED")
        self.assertTrue(pre[0]["owner"])
        self.assertTrue(pre[0]["close_criterion"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
