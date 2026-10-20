"""SEC-04: the allowlist must apply to the matched span, not to the whole line.

The first independent challenge appended an allowlisted substring to a line and watched the
scanner go CLEAN while the token-shaped value stayed in place. These tests pin that shut.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

import secret_scan  # noqa: E402  (path-managed import on purpose)

# The fixture values are assembled at runtime so that this test file never contains a literal
# that the scanner (or a future reader) would treat as a real credential.
GH_TOKEN = "ghp_" + "0123456789abcdefghijABCDEFGHIJ0123"
PAT_TOKEN = "github_pat_" + "11ABCDEFG0123456789_" + "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH"
AWS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"
TOKEN_LINE = 'api_token = "' + GH_TOKEN + '"\n'


def _scan_text(tmp_path: Path, text: str) -> dict:
    (tmp_path / "sample.txt").write_text(text, encoding="utf-8")
    return secret_scan.scan(tmp_path)


def test_token_shaped_value_is_blocked(tmp_path):
    result = _scan_text(tmp_path, TOKEN_LINE)
    assert result["verdict"] == "BLOCKED"
    assert result["hard_findings"] >= 1


def test_appending_an_allowed_substring_does_not_hide_the_token(tmp_path):
    hidden = TOKEN_LINE.rstrip("\n") + "  # see example.com\n"
    result = _scan_text(tmp_path, hidden)
    assert result["verdict"] == "BLOCKED", "an allowlisted substring must not whitelist the line"
    rules = {f["rule"] for f in result["findings"]}
    assert "github_classic_token" in rules


def test_allowlisted_text_inside_the_value_does_not_hide_it(tmp_path):
    """NEW-03: putting "example.com" INSIDE the secret value must not suppress the finding."""

    secret = "example.com" + "supersecret123456"
    result = _scan_text(tmp_path, 'password = "' + secret + '"\n')
    assert result["verdict"] == "BLOCKED"
    assert {f["rule"] for f in result["findings"]} >= {"assigned_secret"}


def test_allowlisted_text_inside_a_token_line_still_blocks(tmp_path):
    result = _scan_text(tmp_path, 'api_token = "' + GH_TOKEN + '-example.com"\n')
    assert result["verdict"] == "BLOCKED"


def test_placeholder_value_stays_clean(tmp_path):
    result = _scan_text(tmp_path, 'password = "<token>"\n')
    assert result["verdict"] == "CLEAN"


def test_documentation_email_stays_clean(tmp_path):
    result = _scan_text(tmp_path, "write to you@example.com for access\n")
    assert result["verdict"] == "CLEAN"


@pytest.mark.parametrize(
    "line",
    [
        'secret = "' + "supersecretvalue123456" + '"\n',
        AWS_KEY + "\n",
        PAT_TOKEN + "\n",
    ],
)
def test_other_hard_rules_still_fire(tmp_path, line):
    result = _scan_text(tmp_path, line)
    assert result["verdict"] == "BLOCKED"


def test_excerpt_is_masked(tmp_path):
    result = _scan_text(tmp_path, TOKEN_LINE)
    excerpt = result["findings"][0]["excerpt"]
    assert "ghp_" not in excerpt
    assert excerpt.endswith("***")
