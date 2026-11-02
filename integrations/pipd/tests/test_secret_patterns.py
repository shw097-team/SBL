"""Pin every entry of workspace.SECRET_PATTERNS against a synthetic sample.

Why this test exists: a bearer pattern was reported as matching nothing on a real sample. The
pattern itself turned out to be intact, but the token class omitted + and /, so a standard-base64
bearer token went unmatched and nothing in the suite noticed. A pattern table that no test pins
can rot silently, and a secret sweep is exactly the wrong place for that.

Samples are assembled from fragments on purpose: a credential-shaped literal written into this
file gets rewritten by the environment's secret redactor, which is the same failure mode.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Self-bootstrap: this file must be runnable standalone (`python -m unittest tests.test_secret_patterns`
# or `python tests/test_secret_patterns.py`). Relying on a sibling test file to mutate sys.path as an
# import side effect makes the file fail with ModuleNotFoundError outside discovery.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp.workspace import SECRET_PATTERNS  # noqa: E402

A = "A"


def sample(pattern_name: str) -> str:
    if pattern_name == "github_pat_fine_grained":
        return "git" + "hub_pat_" + A * 30
    if pattern_name == "github_classic":
        return "gh" + "p_" + A * 30
    if pattern_name == "openai_sk":
        return "sk" + "-" + A * 30
    if pattern_name == "aws_access_key":
        return "AK" + "IA" + "B" * 16
    if pattern_name == "private_key_block":
        return "-----BEGIN " + "RSA " + "PRIVATE KEY" + "-----"
    if pattern_name == "bearer_literal":
        return "Author" + "ization: " + "Bea" + "rer " + A * 30
    raise AssertionError(f"no sample defined for {pattern_name}")


class TestSecretPatterns(unittest.TestCase):
    def test_every_pattern_matches_its_sample(self) -> None:
        self.assertEqual(len(SECRET_PATTERNS), 6, "the pattern table changed size")
        for name, rx in SECRET_PATTERNS:
            with self.subTest(pattern=name):
                self.assertIsNotNone(rx.search(sample(name)),
                                     f"pattern {name!r} does not match its own sample")

    def test_bearer_class_covers_standard_base64(self) -> None:
        """The gap that motivated this test: + and / are legal bearer-token characters."""
        rx = dict(SECRET_PATTERNS)["bearer_literal"]
        for tok in ("AbC+/" * 6, A * 40 + "==", "x" * 20 + ".~-_"):
            with self.subTest(token=repr(tok[:12] + "...")):
                self.assertIsNotNone(
                    rx.search("Author" + "ization: " + "Bea" + "rer " + tok),
                    "standard-base64 / base64url bearer token went unmatched")

    def test_bearer_still_requires_a_real_token(self) -> None:
        """Widening must not turn the pattern into a blanket header match."""
        rx = dict(SECRET_PATTERNS)["bearer_literal"]
        for weak in ("Author" + "ization: " + "Bea" + "rer " + A * 19,
                     "Author" + "ization: " + A * 40):
            with self.subTest(weak=weak[:24]):
                self.assertIsNone(rx.search(weak),
                                  "pattern matched without a token of >=20 characters")

    def test_no_pattern_matches_ordinary_prose(self) -> None:
        for name, rx in SECRET_PATTERNS:
            with self.subTest(pattern=name):
                self.assertIsNone(rx.search("the quick brown fox jumps over the lazy dog"))


if __name__ == "__main__":
    unittest.main()
