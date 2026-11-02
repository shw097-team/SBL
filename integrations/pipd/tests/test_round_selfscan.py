#!/usr/bin/env python3
"""Round self-scan: credential-shape sweep, cap/binary/git handling, deny-scan fold-in.

Samples are assembled from fragments on purpose: a credential-shaped literal written into this
file gets rewritten by the environment's secret redactor -- the exact failure mode this tool
exists to catch -- so the tests never write one either.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import round_selfscan as S  # noqa: E402


def _dummy_sk(n: int = 30) -> str:
    """An sk-shaped dummy assembled at runtime (never a literal in this file)."""
    return "s" + "k" + "-" + ("A" * n)


class RoundSelfScan(unittest.TestCase):
    def test_detects_dummy_credential_from_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "creds.txt").write_text(
                "prefix " + _dummy_sk() + " suffix\n", encoding="utf-8")
            report = S.build_report([tmp])
            self.assertEqual(report["schema"], "PIPD-ROUND-SELFSCAN/1")
            self.assertGreaterEqual(report["counts"]["total"], 1)
            hit = report["hits"][0]
            self.assertEqual(hit["kind"], "sk")
            self.assertEqual(hit["line"], 1)
            self.assertTrue(hit["path"].endswith("creds.txt"))
            self.assertEqual(report["verdict"], "HIT")

    def test_clean_directory_yields_pass_zero_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "readme.md").write_text("nothing to see here\n", encoding="utf-8")
            report = S.build_report([tmp])
            self.assertEqual(report["counts"]["total"], 0)
            self.assertEqual(report["counts"]["by_kind"], {})
            self.assertEqual(report["verdict"], "PASS")

    def test_binary_file_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "blob.bin").write_bytes(
                b"\x00\x01\x02" + _dummy_sk().encode() + b"\xff\x00")
            report = S.build_report([tmp])
            self.assertEqual(report["counts"]["total"], 0)
            self.assertEqual(report["files_scanned"], 0)
            self.assertEqual(report["verdict"], "PASS")

    def test_file_beyond_cap_not_scanned_beyond_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # A credential placed after the 2 MiB cap is invisible.
            (Path(tmp) / "big.txt").write_bytes(
                b"A" * (S.CAP_BYTES + 32) + _dummy_sk().encode())
            report_big = S.build_report([tmp])
            self.assertEqual(report_big["counts"]["total"], 0)
            self.assertEqual(report_big["files_scanned"], 1)
            # The very same scan still finds one placed within the cap.
            (Path(tmp) / "small.txt").write_text("x " + _dummy_sk() + "\n", encoding="utf-8")
            report_both = S.build_report([tmp])
            self.assertGreaterEqual(report_both["counts"]["total"], 1)
            paths = {h["path"] for h in report_both["hits"]}
            self.assertTrue(any(p.endswith("small.txt") for p in paths))
            self.assertFalse(any(p.endswith("big.txt") for p in paths))

    def test_excerpt_is_redacted_never_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = _dummy_sk(24)
            (Path(tmp) / "c.txt").write_text("key=" + raw + "\n", encoding="utf-8")
            report = S.build_report([tmp])
            self.assertTrue(report["hits"])
            for hit in report["hits"]:
                self.assertNotIn(raw, hit["excerpt"])
                self.assertNotIn(raw[3:], hit["excerpt"])  # the random tail too
                self.assertIn(hit["kind"], hit["excerpt"])
                self.assertIn("chars)", hit["excerpt"])
            # Stronger: the raw value appears nowhere at all in the serialised report.
            self.assertNotIn(raw, json.dumps(report))

    def test_deny_scan_stub_nonzero_is_hit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "clean.txt").write_text("all good here\n", encoding="utf-8")
            stub = Path(tmp) / "stub_deny.py"
            stub.write_text("import sys\nprint('stub deny hit')\nsys.exit(1)\n", encoding="utf-8")

            report = S.build_report([tmp], deny_scan_path=str(stub))
            self.assertEqual(report["counts"]["total"], 0)
            self.assertTrue(report["deny_scan"]["ran"])
            self.assertEqual(report["deny_scan"]["exit_code"], 1)
            self.assertIn("stub deny hit", report["deny_scan"]["tail"])
            self.assertEqual(report["verdict"], "HIT")

            # CLI surfaces the same verdict as a non-zero exit.
            self.assertEqual(S.main(["--paths", tmp, "--deny-scan", str(stub)]), 1)

    def test_own_source_has_no_literal_credential_shape(self) -> None:
        src = (ROOT / "tools" / "round_selfscan.py").read_text(encoding="utf-8")
        an = "[A-Za-z0-9]"
        up = "[A-Z0-9]"
        shapes = [
            "s" + "k" + "-" + an + "{20,}",
            "g" + "h" + "p" + "_" + an + "{20,}",
            "AK" + "IA" + up + "{16}",
            "xox" + "[baprs]" + "-" + an + "{20,}",
        ]
        for shape in shapes:
            self.assertIsNone(re.search(shape, src),
                              f"tool source leaked a literal credential shape: {shape}")

    def test_cli_writes_json_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "note.txt").write_text("clean text\n", encoding="utf-8")
            ok = Path(tmp) / "ok_deny.py"
            ok.write_text("import sys\nprint('ok')\nsys.exit(0)\n", encoding="utf-8")
            out = Path(tmp) / "report.json"

            rc = S.main(["--paths", tmp, "--json-out", str(out), "--deny-scan", str(ok)])
            self.assertEqual(rc, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "PIPD-ROUND-SELFSCAN/1")
            self.assertEqual(data["verdict"], "PASS")
            self.assertEqual(data["deny_scan"]["exit_code"], 0)
            self.assertIn("by_kind", data["counts"])
            self.assertEqual(data["as_of"], str(data["as_of"]))  # serialisable string

    def test_git_directory_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gd = Path(tmp) / ".git"
            gd.mkdir()
            # A generic secret assignment that WOULD hit if .git were not skipped.
            (gd / "config").write_text(
                "token = " + '"' + "x" * 20 + '"\n', encoding="utf-8")
            (Path(tmp) / "normal.txt").write_text("hello\n", encoding="utf-8")
            report = S.build_report([tmp])
            self.assertEqual(report["counts"]["total"], 0)
            self.assertEqual(report["verdict"], "PASS")

    def test_detects_multiple_credential_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ghp = "g" + "h" + "p" + "_" + ("B" * 30)
            akia = "AK" + "IA" + ("C" * 16)
            xox = "xox" + "b" + "-" + ("D" * 30)
            generic = "pass" + "word" + " = " + '"' + "E" * 16 + '"'
            (Path(tmp) / "env.txt").write_text(
                f"{ghp}\n{akia}\n{xox}\n{generic}\n", encoding="utf-8")
            report = S.build_report([tmp])
            kinds = {h["kind"] for h in report["hits"]}
            self.assertTrue({"ghp", "akia", "xox", "generic"}.issubset(kinds),
                            f"missing kinds; got {sorted(kinds)}")
            self.assertEqual(report["counts"]["total"], 4)
            self.assertEqual(report["counts"]["by_kind"].get("generic"), 1)


if __name__ == "__main__":
    unittest.main()
