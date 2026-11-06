"""WP-FHS-06/WP09 support: a runner entry can be BOUND and executed, and refusals are typed.

The contract this file defends is the one that blocked every earlier round: `planned_tqaep`
correctly refuses a bound runner while *planning*, and nothing existed to bind one afterwards.
These tests pin the binding side so a case can move from `RUNNER_UNBOUND` to a real execution —
and so a drifted oracle, a shared POS/NEG fixture or a self-edited entry cannot pass as bound.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import case_runner as cr  # noqa: E402

BILLING_DEFECTIVE = "\n".join([
    '"""Billing helper."""',
    "from decimal import Decimal, ROUND_HALF_UP",
    "",
    "",
    "def line_total(unit_price: str, quantity: int) -> Decimal:",
    '    return (Decimal(unit_price) * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)',
    "",
    "",
    "def total(lines) -> Decimal:",
    '    return sum((line_total(price, qty) for price, qty in lines), Decimal("0"))',
    "",
])

BILLING_FIXED = "\n".join([
    '"""Billing helper."""',
    "from decimal import Decimal, ROUND_HALF_UP",
    "",
    "",
    "def total(lines) -> Decimal:",
    '    exact = sum((Decimal(price) * qty for price, qty in lines), Decimal("0"))',
    '    return exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)',
    "",
])

ORACLE = "\n".join([
    "from decimal import Decimal",
    "from src.demo.billing import total",
    "",
    "",
    "def test_rounds_once():",
    '    assert total([("0.005", 1), ("0.005", 1), ("0.005", 1)]) == Decimal("0.02")',
    "",
])

RUNNER = "\n".join([
    "import json, subprocess, sys",
    "from pathlib import Path",
    "",
    "root = Path(sys.argv[1])",
    'proc = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", "tests/"],',
    "                      cwd=str(root), capture_output=True, text=True)",
    'value = "unknown"',
    "try:",
    "    sys.path.insert(0, str(root))",
    "    from src.demo.billing import total",
    '    value = str(total([("0.005", 1), ("0.005", 1), ("0.005", 1)]))',
    "except Exception as exc:",
    '    value = "error:" + type(exc).__name__',
    'verdict = "GREEN" if (proc.returncode == 0 and value == "0.02") else "RED"',
    'print(json.dumps({"verdict": verdict, "oracle_exit": proc.returncode, "observed": value}))',
    "",
])


class CaseRunnerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        files = {
            "src/demo/billing.py": BILLING_DEFECTIVE,
            "tests/test_billing.py": ORACLE,
            "tools/runner.py": RUNNER,
            "fixtures/pos.txt": "three 0.005 lines -> 0.02\n",
            "fixtures/neg.txt": "three 0.005 lines -> 0.03\n",
        }
        for rel, body in files.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def entry(self, **over):
        kwargs = dict(
            root=self.root, case_id="CASE-ROUND-ONCE",
            original_requirement_id="REQ-1", original_oracle_id="ORACLE-1",
            clause_id="C1", fuo_id="FUO-1", parent_neg="must not round per line",
            oracle="tests/test_billing.py", runner="tools/runner.py",
            positive_fixture="fixtures/pos.txt", negative_fixture="fixtures/neg.txt",
            raw_schema="SBL.CaseRunner.WorldRaw@1",
            evidence_expectation="three 0.005 lines produce 0.02",
            checker_role="protected_checker", runner_owner="sbl_caseregistry_runner",
            applicability={"host": "windows", "profile": "hgk-governed", "kind": "CLI_TOOL",
                           "mode": "STANDALONE"},
        )
        kwargs.update(over)
        return cr.build_entry(**kwargs)

    def test_bound_entry_pins_every_byte(self):
        e = self.entry()
        self.assertEqual(e["schema"], cr.SCHEMA)
        self.assertEqual(e["runner_binding"], "RUNNER_BOUND")
        self.assertRegex(e["runner_entry_sha256"], r"^[0-9a-f]{64}$")
        for block in ("oracle", "runner", "positive_fixture", "negative_fixture"):
            self.assertRegex(e[block]["sha256"], r"^[0-9a-f]{64}$")
        self.assertNotEqual(e["positive_fixture"]["sha256"], e["negative_fixture"]["sha256"])

    def test_shared_pos_and_neg_fixture_is_refused(self):
        (self.root / "fixtures" / "neg.txt").write_text(
            (self.root / "fixtures" / "pos.txt").read_text(encoding="utf-8"), encoding="utf-8")
        with self.assertRaises(cr.CaseRunnerRefusal) as ctx:
            self.entry()
        self.assertEqual(ctx.exception.code, "CASE_RUNNER_POS_NEG_COLLISION")

    def test_missing_runner_file_is_refused(self):
        with self.assertRaises(cr.CaseRunnerRefusal) as ctx:
            self.entry(runner="tools/absent.py")
        self.assertEqual(ctx.exception.code, "CASE_RUNNER_FILE_MISSING")

    def test_empty_applicability_axis_is_refused(self):
        with self.assertRaises(cr.CaseRunnerRefusal) as ctx:
            self.entry(applicability={"host": "windows", "profile": "", "kind": "k", "mode": "m"})
        self.assertEqual(ctx.exception.code, "CASE_RUNNER_APPLICABILITY")

    def test_drifted_oracle_is_refused(self):
        e = self.entry()
        (self.root / "tests" / "test_billing.py").write_text("# edited\n", encoding="utf-8")
        with self.assertRaises(cr.CaseRunnerRefusal) as ctx:
            cr.verify_entry(e, self.root)
        self.assertEqual(ctx.exception.code, "CASE_RUNNER_ENTRY_DRIFT")

    def test_self_edited_entry_is_refused(self):
        e = self.entry()
        e["oracle"]["sha256"] = "0" * 64
        with self.assertRaises(cr.CaseRunnerRefusal) as ctx:
            cr.verify_entry(e, self.root)
        self.assertEqual(ctx.exception.code, "CASE_RUNNER_ENTRY_DRIFT")

    def test_unbound_entry_cannot_run(self):
        e = self.entry()
        e["runner_binding"] = "RUNNER_UNBOUND"
        with self.assertRaises(cr.CaseRunnerRefusal) as ctx:
            cr.run_entry(e, subject_root=self.root)
        self.assertEqual(ctx.exception.code, "CASE_RUNNER_BINDING_STATE")

    def test_defective_subject_reports_red(self):
        e = self.entry()
        raw = cr.run_entry(e, subject_root=self.root)
        self.assertEqual(raw["world_state"], "RED", raw["runner"].get("stderr_tail"))
        self.assertEqual(raw["observed"]["observed"], "0.03")
        self.assertNotEqual(raw["observed"]["oracle_exit"], 0)

    def test_patched_subject_reports_green(self):
        e = self.entry()
        (self.root / "src" / "demo" / "billing.py").write_text(BILLING_FIXED, encoding="utf-8")
        raw = cr.run_entry(e, subject_root=self.root)
        self.assertEqual(raw["world_state"], "GREEN", raw["runner"].get("stderr_tail"))
        self.assertEqual(raw["observed"]["observed"], "0.02")
        self.assertEqual(raw["observed"]["oracle_exit"], 0)

    def test_preimage_and_restore_round_trip(self):
        scope = ["src/demo/billing.py"]
        before = cr.preimage(self.root, scope)
        backup = Path(self._tmp.name) / "_backup"
        (backup / "src" / "demo").mkdir(parents=True)
        (backup / "src" / "demo" / "billing.py").write_bytes(
            (self.root / "src" / "demo" / "billing.py").read_bytes())
        (self.root / "src" / "demo" / "billing.py").write_text("# changed\n", encoding="utf-8")
        out = cr.restore(self.root, before, backup)
        self.assertTrue(out["exact"])
        self.assertEqual(cr.preimage(self.root, scope), before)


if __name__ == "__main__":
    unittest.main()
