#!/usr/bin/env python3
"""WO-S4-TQAEP-004 / F-R5-05: design-time TQAEP is a DESIGN ceiling, never independent acceptance.

Before this repair `compile_tqaep()` emitted `acceptance = [{"case": "INDEPENDENT_CASE_PASS", ...}]`
- a *receipt string* presented as if it were independent verification, so the UAT only ever exercised
the refusal path. These tests pin the honest behaviour: a legal design-time call exits 0, carries the
`TQAEP_DESIGNED` ceiling, and never lets a receipt string become an independence token; the three
typed refusals are unchanged.

The CLI is driven in-process via `cli.main()` (the same dispatcher, exit code and stdout envelope the
`python3 -B -m pipd_ls_sp.cli compile-tqaep ...` command produces); spawning a fresh interpreter per
case is avoided only because this container's fresh-interpreter startup is pathologically slow.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import cli, pipeline  # noqa: E402

GOAL = "Implement the lifecycle compiler and verify it against the source spec."


def _run_cli(*args: str):
    """Invoke the real CLI dispatcher in-process; return (exit_code, parsed_stdout)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(list(args))
    text = buf.getvalue().strip()
    body = json.loads(text) if text else {}
    return rc, body


class TqaepDesignTime(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # The PI->PD->ECP fixture chain is built once: `bind_pd` runs a live repo probe
        # (52s on this bind mount), so per-test setup would dominate the module.
        card = pipeline.intake(GOAL, sources=[str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")])
        cls.pi = pipeline.compile_pi(card, "STANDARD")
        pd = pipeline.bind_pd(cls.pi, {"root": str(ROOT), "writable_scope": "src/**"})
        cls.ecp = pipeline.compile_ecp(pd, cls.pi)
        cls.tmp = ROOT / ".hgk" / "artifacts" / "tqaep_design_tmp"
        cls.tmp.mkdir(parents=True, exist_ok=True)
        cls.pi_p = cls.tmp / "pi.json"
        cls.ecp_p = cls.tmp / "ecp.json"
        # S4EXT-R1 AO finding: these fixtures live inside the tracked tree, so regenerating them
        # read as a transient candidate mutation during independent verification. Capture the bytes
        # that are on disk BEFORE this module writes anything, and put them back afterwards, so the
        # worktree is byte-identical when the module finishes.
        cls._pre_existing = {p: p.read_bytes() for p in (cls.pi_p, cls.ecp_p) if p.is_file()}
        cls.pi_p.write_text(json.dumps(cls.pi, ensure_ascii=False), encoding="utf-8")
        cls.ecp_p.write_text(json.dumps(cls.ecp, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        for path, original in getattr(cls, "_pre_existing", {}).items():
            if not path.is_file() or path.read_bytes() != original:
                path.write_bytes(original)

    # (a) a legal design-time call exits 0 and is honest about what it established.
    def test_legal_design_time_call_exits_zero_and_declares_design_ceiling(self) -> None:
        rc, art = _run_cli("compile-tqaep", "--pi", str(self.pi_p), "--ecp", str(self.ecp_p),
                           "--maker", "A", "--checker", "B",
                           "--checker-receipt", "lane-B/live.log")
        self.assertEqual(rc, 0)
        acc = art["acceptance"]
        self.assertEqual(art["subject_id"].split("-")[0], "TQAEP")
        # The design-time ceiling is carried, and it is not an independence claim.
        self.assertEqual(acc[0]["claim_ceiling"], pipeline.TQAEP_DESIGN_CEILING)
        self.assertEqual(pipeline.TQAEP_DESIGN_CEILING, "TQAEP_DESIGNED")
        self.assertEqual(acc[0]["independent_acceptance"], "NOT_GRANTED")
        self.assertEqual(acc[0]["independent_proof_requires"], "S5_LIVE_RUNTIME_CHECKER")
        # A receipt string may be recorded, but no INDEPENDENT_CASE_PASS token may appear anywhere.
        self.assertNotIn("INDEPENDENT_CASE_PASS", json.dumps(art))
        self.assertNotEqual(acc[0].get("case"), "INDEPENDENT_CASE_PASS")
        # The schema key set is unchanged (additionalProperties:false at the top level).
        self.assertEqual(sorted(art.keys()),
                         ["acceptance", "content_hash", "fixtures", "oracles",
                          "requalification", "schema_version", "subject_id", "tests", "version"])
        # The record still validates against the frozen 19-contract schema set.
        from pipd_ls_sp import validate
        self.assertEqual(validate.validate_bundle({"TQAEP": art}, ROOT / "schemas")["findings"], [])

    # (c) no code path can turn a receipt string into an INDEPENDENT_PASS token.
    def test_acceptance_entry_never_becomes_independent_pass(self) -> None:
        tq = pipeline.compile_tqaep(self.pi, self.ecp, maker="A", checker="B",
                                    checker_execution_receipt="independently-passed")
        blob = json.dumps(tq)
        self.assertNotIn("INDEPENDENT_CASE_PASS", blob)
        self.assertNotIn("INDEPENDENT_PASS", blob)
        # Even a receipt string that *claims* independence is only ever recorded verbatim.
        self.assertEqual(tq["acceptance"][0]["checker_execution_receipt"], "independently-passed")
        self.assertEqual(tq["acceptance"][0]["independent_acceptance"], "NOT_GRANTED")

    def test_case_and_design_status_are_not_the_old_independent_claim(self) -> None:
        tq = pipeline.compile_tqaep(self.pi, self.ecp, maker="A", checker="B",
                                    checker_execution_receipt="r")
        e = tq["acceptance"][0]
        self.assertEqual(e["case"], "TQAEP_DESIGN_CANDIDATE")
        self.assertEqual(e["design_time_status"], "DISTINCT_CHECKER_IDENTITY_RECORDED")

    # (b) the three typed refusals still exit non-zero with their typed codes (via the CLI).
    def test_maker_eq_checker_is_typed_sod_refusal(self) -> None:
        rc, body = _run_cli("compile-tqaep", "--pi", str(self.pi_p), "--ecp", str(self.ecp_p),
                            "--maker", "A", "--checker", " a ", "--checker-receipt", "r")
        self.assertNotEqual(rc, 0)
        self.assertEqual(body["code"], "TQ_SOD")

    def test_self_attested_receipt_is_typed_sod_refusal(self) -> None:
        rc, body = _run_cli("compile-tqaep", "--pi", str(self.pi_p), "--ecp", str(self.ecp_p),
                            "--maker", "A", "--checker", "B", "--checker-receipt", "SELF_ATTESTED")
        self.assertNotEqual(rc, 0)
        self.assertEqual(body["code"], "TQ_SOD")

    def test_missing_receipt_is_typed_sod_refusal(self) -> None:
        rc, body = _run_cli("compile-tqaep", "--pi", str(self.pi_p), "--ecp", str(self.ecp_p),
                            "--maker", "A", "--checker", "B")
        self.assertNotEqual(rc, 0)
        self.assertEqual(body["code"], "TQ_SOD")

    def test_missing_trace_is_typed_trace_refusal(self) -> None:
        empty_pi = self.tmp / "pi_empty_trace.json"
        empty_pi.write_text(json.dumps({"subject_id": "PI-x",
                                        "stable_semantic_contract": {"atoms": []}}),
                            encoding="utf-8")
        rc, body = _run_cli("compile-tqaep", "--pi", str(empty_pi), "--ecp", str(self.ecp_p),
                            "--maker", "A", "--checker", "B", "--checker-receipt", "r")
        self.assertNotEqual(rc, 0)
        self.assertEqual(body["code"], "TQ_TRACE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
