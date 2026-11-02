"""Deterministic unit tests for tools/preflight_check.py.

The tool shells out to git/docker/codex and opens sockets when it runs for real.
These tests never do: every check under test is a small function over injected
inputs (a git-status string, a TOML string, a free-byte count, a check list), so
the suite stays hermetic and fast. The one negative test assembles its credential
shapes from fragments -- writing a token-shaped literal into this file would make
the tree's own export step fail, which is the very defect it guards against.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import preflight_check as P  # noqa: E402

GIB = 1024 ** 3
FIVE_GIB = 5 * GIB
REQUIRED_KEYS = {"schema", "as_of", "repo", "head", "dirty", "checks",
                 "verdict", "verdict_reason"}


def _check(cid: str, status: str) -> dict:
    return {"id": cid, "status": status, "detail": "", "elapsed_ms": 0}


class ExitCodeMapping(unittest.TestCase):
    def test_fail_present_is_non_zero(self) -> None:
        checks = [_check("python", "PASS"), _check("disk", "FAIL"), _check("docker", "WARN")]
        self.assertNotEqual(P.exit_code_for(checks), 0)
        self.assertEqual(P.compute_verdict(checks)[0], "FAIL")

    def test_only_warn_and_skip_is_zero(self) -> None:
        checks = [_check("python", "PASS"), _check("docker", "WARN"),
                  _check("suite_baseline", "SKIP")]
        self.assertEqual(P.exit_code_for(checks), 0)
        verdict, reason = P.compute_verdict(checks)
        self.assertEqual(verdict, "PASS")
        self.assertIn("docker", reason)

    def test_all_pass_is_zero(self) -> None:
        checks = [_check(cid, "PASS") for cid in P.CHECK_IDS]
        self.assertEqual(P.exit_code_for(checks), 0)
        self.assertEqual(P.compute_verdict(checks), ("PASS", "all checks passed"))


class DiskThreshold(unittest.TestCase):
    def test_just_below_five_gib_fails(self) -> None:
        self.assertEqual(P.check_disk(FIVE_GIB - 1)["status"], "FAIL")

    def test_just_above_five_gib_passes(self) -> None:
        self.assertEqual(P.check_disk(FIVE_GIB + 1)["status"], "PASS")

    def test_exactly_five_gib_passes(self) -> None:
        # The threshold is inclusive: the check reads "free >= 5 GiB".
        self.assertEqual(P.check_disk(FIVE_GIB)["status"], "PASS")
        self.assertEqual(P.DISK_MIN_FREE_BYTES, FIVE_GIB)


class GitHeadComparison(unittest.TestCase):
    HEAD = "a" * 40
    PORCELAIN_TWO = " M src/x.py\n?? notes.txt\n"

    def test_match_passes_and_counts_dirty(self) -> None:
        res = P.check_git_head(is_git=True, head=self.HEAD, porcelain=self.PORCELAIN_TWO,
                               expect_head=self.HEAD, expect_dirty=2)
        self.assertEqual(res["status"], "PASS")
        self.assertIn("dirty=2", res["detail"])

    def test_not_a_work_tree_fails(self) -> None:
        res = P.check_git_head(is_git=False, expect_head=self.HEAD)
        self.assertEqual(res["status"], "FAIL")

    def test_head_mismatch_fails(self) -> None:
        res = P.check_git_head(is_git=True, head=self.HEAD, porcelain="",
                               expect_head="b" * 40)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("HEAD", res["detail"])

    def test_dirty_mismatch_fails(self) -> None:
        res = P.check_git_head(is_git=True, head=self.HEAD, porcelain=self.PORCELAIN_TWO,
                               expect_dirty=0)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("dirty 2 != expected 0", res["detail"])

    def test_absent_expectations_pass(self) -> None:
        res = P.check_git_head(is_git=True, head=self.HEAD, porcelain=self.PORCELAIN_TWO)
        self.assertEqual(res["status"], "PASS")

    def test_porcelain_blank_lines_are_not_dirty_files(self) -> None:
        self.assertEqual(P.count_porcelain("\n \n M a.py\n\n"), 1)


class ModelPinning(unittest.TestCase):
    def test_drift_named_config_drift(self) -> None:
        toml = 'model = "gpt-5-codex"\napproval_policy = "never"\n'
        res = P.check_model_pinning(toml, "gpt-4.1")
        self.assertEqual(res["status"], "WARN")
        self.assertIn("CONFIG_DRIFT", res["detail"])
        self.assertIn("pass --model explicitly", res["detail"])

    def test_match_passes(self) -> None:
        toml = "model = 'gpt-5-codex'\n"
        res = P.check_model_pinning(toml, "gpt-5-codex")
        self.assertEqual(res["status"], "PASS")

    def test_no_config_pin_is_warn(self) -> None:
        res = P.check_model_pinning("# empty config\n", "gpt-5-codex")
        self.assertEqual(res["status"], "WARN")
        self.assertIn("CONFIG_DRIFT", res["detail"])

    def test_no_model_given_is_skip(self) -> None:
        res = P.check_model_pinning('model = "gpt-5-codex"\n', None)
        self.assertEqual(res["status"], "SKIP")

    def test_extract_ignores_model_provider_like_lines(self) -> None:
        self.assertIsNone(P.extract_config_model('model_provider = "openai"\n'))
        self.assertEqual(P.extract_config_model("  model = \"m\"\n"), "m")


class SandboxAndBinary(unittest.TestCase):
    def test_helper_broken_is_warn_not_fail(self) -> None:
        res = P.check_codex_sandbox("... helper_unknown_error ...")
        self.assertEqual(res["status"], "WARN")
        self.assertEqual(res["detail"], "SANDBOX_HELPER_BROKEN")

    def test_setup_refresh_errors_is_warn(self) -> None:
        res = P.check_codex_sandbox("setup refresh had errors")
        self.assertEqual(res["status"], "WARN")
        self.assertEqual(res["detail"], "SANDBOX_HELPER_BROKEN")

    def test_probe_marker_is_pass(self) -> None:
        res = P.check_codex_sandbox(f"tool ran ok PREFLIGHT_PROBE_OK")
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["detail"], "SANDBOX_READY")

    def test_no_binary_is_fail(self) -> None:
        self.assertEqual(P.check_codex_binary([])["status"], "FAIL")

    def test_binary_listed_with_version(self) -> None:
        res = P.check_codex_binary(["C:/x/codex.exe", "C:/y/codex.exe"], version="codex 1.2.3")
        self.assertEqual(res["status"], "PASS")
        self.assertIn("2 hit(s)", res["detail"])
        self.assertIn("codex 1.2.3", res["detail"])


class OtherChecks(unittest.TestCase):
    def test_loopback_unreachable_is_warn(self) -> None:
        res = P.check_loopback({10102: True, 10100: False})
        self.assertEqual(res["status"], "WARN")
        self.assertIn("10100", res["detail"])

    def test_loopback_all_up_is_pass(self) -> None:
        res = P.check_loopback({10102: True, 10100: True})
        self.assertEqual(res["status"], "PASS")

    def test_python_below_minimum_fails(self) -> None:
        self.assertEqual(P.check_python(version_info=(3, 10, 6), unittest_importable=True)["status"],
                         "FAIL")

    def test_python_unittest_missing_fails(self) -> None:
        self.assertEqual(P.check_python(version_info=(3, 11, 17), unittest_importable=False)["status"],
                         "FAIL")

    def test_python_ok_passes(self) -> None:
        self.assertEqual(P.check_python(version_info=(3, 11, 17), unittest_importable=True)["status"],
                         "PASS")

    def test_suite_baseline_fail_exit_is_fail(self) -> None:
        res = P.check_suite_baseline(ran=True, exit_code=1, test_count=42, duration_s=3.5)
        self.assertEqual(res["status"], "FAIL")
        self.assertIn("tests=42", res["detail"])

    def test_suite_baseline_not_requested_is_skip(self) -> None:
        self.assertEqual(P.check_suite_baseline(ran=False)["status"], "SKIP")


class PayloadAndTable(unittest.TestCase):
    def test_payload_has_every_required_key(self) -> None:
        checks = [P._result(cid, "PASS", "ok") for cid in P.CHECK_IDS]
        payload = P.build_payload(repo=Path("C:/tmp/repo"), head="c" * 40, dirty=3,
                                  checks=checks)
        self.assertEqual(REQUIRED_KEYS <= set(payload), True,
                         f"missing keys: {sorted(REQUIRED_KEYS - set(payload))}")
        self.assertEqual(payload["schema"], "PIPD-PREFLIGHT/1")
        self.assertEqual(payload["head"], "c" * 40)
        self.assertEqual(payload["dirty"], 3)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertIsInstance(payload["as_of"], str)
        for check in payload["checks"]:
            self.assertEqual(set(check), {"id", "status", "detail", "elapsed_ms"})

    def test_payload_verdict_fail_when_a_check_fails(self) -> None:
        checks = [P._result(cid, "PASS", "ok") for cid in P.CHECK_IDS]
        checks[2] = P._result("disk", "FAIL", "too full")
        payload = P.build_payload(repo=Path("x"), head="", dirty=0, checks=checks)
        self.assertEqual(payload["verdict"], "FAIL")

    def test_rendered_table_contains_every_check_id(self) -> None:
        checks = [P._result(cid, "PASS", "detail " + cid) for cid in P.CHECK_IDS]
        table = P.render_table(checks)
        for cid in P.CHECK_IDS:
            self.assertIn(cid, table)

    def test_emitted_json_round_trips(self) -> None:
        checks = [P._result(cid, "PASS", "ok") for cid in P.CHECK_IDS]
        payload = P.build_payload(repo=Path("r"), head="h", dirty=1, checks=checks)
        blob = json.dumps(payload, ensure_ascii=False, indent=1)
        self.assertEqual(json.loads(blob)["schema"], "PIPD-PREFLIGHT/1")


class NoCredentialShapeInToolSource(unittest.TestCase):
    """Negative guard: the tool must not carry a literal credential shape.

    A token-shaped string anywhere in this tree makes the product's export step
    fail, so the tool is scanned with the same classes the repo's own secret
    patterns use. Patterns are assembled from fragments on purpose.
    """

    def _patterns(self) -> list[re.Pattern[str]]:
        gh = "git" + "hub_pat_"
        classic = "gh" + "[pousr]_"
        openai = "sk" + "-"
        aws = "AK" + "IA"
        body = "[A-Za-z0-9_]{20,}"
        return [
            re.compile(gh + body),
            re.compile(classic + body),
            re.compile(openai + body),
            re.compile(aws + "[0-9A-Z]{16}"),
            re.compile("-----BEGIN " + "[A-Z ]*PRIVATE KEY" + "-----"),
        ]

    def test_tool_source_is_clean(self) -> None:
        source = (ROOT / "tools" / "preflight_check.py").read_text(encoding="utf-8")
        for rx in self._patterns():
            self.assertIsNone(rx.search(source),
                              f"tool source matches a credential shape: {rx.pattern!r}")

    def test_pattern_actually_matches_an_assembled_sample(self) -> None:
        # Proves the guard above is not vacuously true.
        sample = "sk" + "-" + "A" * 24
        self.assertIsNotNone(self._patterns()[2].search(sample))


if __name__ == "__main__":
    unittest.main(verbosity=2)
